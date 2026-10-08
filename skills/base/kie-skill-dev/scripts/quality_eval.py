import argparse
import concurrent.futures
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

USER_SKILLS = pathlib.Path.home() / ".agents" / "skills"
SANDBOX_ROOT = pathlib.Path.home() / "project" / "test"
FILE_LIMIT = 8000
TOTAL_LIMIT = 60000


def find_repo():
    for parent in pathlib.Path(__file__).resolve().parents:
        if (parent / "skills" / "base" / "kie-skill-dev").is_dir():
            return parent
    raise SystemExit("错误：找不到仓库根目录，本脚本需要在 kie-skills 仓库内运行")


REPO = find_repo()


def parse_args():
    ap = argparse.ArgumentParser(description="技能输出质量评估：同一提示词分别带技能与不带技能运行，按 assertions 评分并汇总。"
                                             "退出码 0=结果可用，1=有运行没有事件输出或有评分失败")
    ap.add_argument("skill", help="技能名，例如 kie-skill-dev")
    ap.add_argument("--iteration", type=int, default=1, help="迭代轮次，结果写入 iteration-<N>，默认 1")
    ap.add_argument("--cases", help="只跑指定 id，逗号分隔")
    ap.add_argument("--workers", type=int, default=4, help="并发会话数，默认 4")
    ap.add_argument("--cap", type=int, default=600, help="单次任务会话时长上限（秒），默认 600")
    ap.add_argument("--no-grade", action="store_true", help="只运行会话与收集产物，不调用评分")
    return ap.parse_args()


def find_skill(skill):
    hits = [p for p in (REPO / "skills").glob(f"*/{skill}") if (p / "SKILL.md").is_file()]
    if len(hits) != 1:
        raise SystemExit(f"错误：skills/*/{skill} 匹配到 {len(hits)} 个目录，需要恰好一个")
    return hits[0]


def load_cases(skill_dir, only):
    path = skill_dir / "evals" / "evals.json"
    if not path.is_file():
        raise SystemExit(f"错误：缺少 {path.relative_to(REPO)}，先按官方 schema 写用例")
    cases = json.loads(path.read_text())["evals"]
    if only:
        wanted = {c.strip() for c in only.split(",")}
        cases = [c for c in cases if str(c["id"]) in wanted]
        if not cases:
            raise SystemExit(f"错误：没有 id 落在 {only} 的用例")
    return cases


def slug(case):
    text = re.sub(r"[^a-z0-9]+", "-", str(case["id"]).lower()).strip("-")
    return f"eval-{text}" if text else f"eval-{abs(hash(str(case['id']))) % 100000}"


def input_path(rel):
    # evals/files/ 之后的路径直接落到工作目录，会话看到的就是任务里的相对路径
    parts = pathlib.Path(rel).parts
    if parts[:2] == ("evals", "files"):
        return pathlib.Path(*parts[2:])
    return pathlib.Path(parts[-1])


def prepare_arm(sandbox, skill_dir, case, with_skill):
    skills = sandbox / "skills"
    shutil.rmtree(sandbox, ignore_errors=True)
    skills.mkdir(parents=True)
    work = sandbox / "work"
    work.mkdir()
    if with_skill:
        for src in sorted((REPO / "skills").glob("*/*")):
            if src.is_dir():
                shutil.copytree(src, skills / src.name)
                shutil.rmtree(skills / src.name / "evals", ignore_errors=True)
    overlay = sandbox / "overlay.yml"
    overlay.write_text(
        "skills:\n"
        f"  customDirectories:\n    - {skills}\n"
        "  enableAgentsUser: false\n"
    )
    for rel in case.get("files", []):
        source = skill_dir / rel
        if not source.is_file():
            raise SystemExit(f"错误：用例输入文件不存在 {source.relative_to(REPO)}")
        target = work / input_path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    return work, overlay


def run_session(prompt, work, overlay, cap):
    inner = (
        f"mount -t tmpfs none {REPO} && "
        f"cd {work} && "
        "exec omp -p --mode json --no-session "
        f"--config {overlay} --tools read,write,edit,bash,grep,glob --auto-approve "
        f"--max-time {cap} \"$1\""
    )
    if USER_SKILLS.is_dir():
        inner = f"mount -t tmpfs none {USER_SKILLS} && " + inner
    cmd = ["unshare", "-rm", "bash", "-c", inner, "omp-eval", prompt]
    started = time.time()
    truncated = False
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=cap + 30)
        out = proc.stdout
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        truncated = True
    wall_ms = (time.time() - started) * 1000
    # --max-time 到点会由客户端自己退出，用时贴住上限说明这次运行被截断，产物可能不完整
    if wall_ms >= (cap - 2) * 1000:
        truncated = True
    return out, wall_ms, truncated


def iter_events(stream):
    for line in stream.splitlines():
        if line.startswith("{"):
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def collect_timing(transcript, wall_ms):
    # message_end 是每个助手消息的唯一一次落账，turn_end 与 agent_end 会重复同一份 usage
    tokens = 0
    events = 0
    for event in iter_events(transcript):
        events += 1
        if event.get("type") != "message_end":
            continue
        message = event.get("message") or {}
        if message.get("role") != "assistant":
            continue
        tokens += ((message.get("usage") or {}).get("totalTokens") or 0)
    loaded = sorted({m for m in re.findall(r'"resolvedPath":"[^"]*/skills/([^/"]+)/SKILL\.md"', transcript)})
    return {"duration_ms": round(wall_ms), "total_tokens": tokens, "events": events,
            "loaded_skills": loaded}


def assistant_text(stream):
    texts = []
    for event in iter_events(stream):
        if event.get("type") != "message_end":
            continue
        message = event.get("message") or {}
        if message.get("role") != "assistant":
            continue
        for block in message.get("content", []):
            if block.get("type") == "text" and block.get("text"):
                texts.append(block["text"])
    return texts[-1] if texts else ""


def dump_outputs(directory):
    parts = []
    total = 0
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            parts.append(f'<file path="{path.relative_to(directory)}">二进制文件，{path.stat().st_size} 字节</file>')
            continue
        snippet = text[:FILE_LIMIT]
        if len(text) > FILE_LIMIT:
            snippet += f"\n...（截断，原文 {len(text)} 字符）"
        block = f'<file path="{path.relative_to(directory)}">\n{snippet}\n</file>'
        if total + len(block) > TOTAL_LIMIT:
            parts.append("（产物过多，其余文件未纳入评分）")
            break
        parts.append(block)
        total += len(block)
    return "\n".join(parts) if parts else "（没有产生任何文件）"


def grade(case, arm_dir, cap):
    outputs = dump_outputs(arm_dir / "outputs")
    reply = assistant_text((arm_dir / "transcript.jsonl").read_text(encoding="utf-8", errors="replace"))
    prompts = "\n".join(f"{i + 1}. {a}" for i, a in enumerate(case["assertions"]))
    prompt = (
        "你是输出质量评分器。只输出 JSON，不要输出其他文字。\n\n"
        f"任务提示词：{case['prompt']}\n"
        f"期望结果：{case['expected_output']}\n"
        f"断言列表：\n{prompts}\n\n"
        f"会话最后一条回复：\n{reply[:FILE_LIMIT]}\n\n"
        f"工作目录里的文件（含任务给的输入文件的最终状态）：\n{outputs}\n\n"
        "逐条判定断言是否成立，判定为通过必须给出产物中的具体证据，找不到证据记不通过。\n"
        '输出格式：{"assertion_results":[{"text":"断言原文","passed":true,"evidence":"证据"}],'
        '"summary":{"passed":0,"failed":0,"total":0,"pass_rate":0}}\n'
    )
    cmd = ["omp", "-p", "--mode", "json", "--no-session", "--tools", "read", f"--max-time={cap}"]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=cap + 30)
    text = assistant_text(proc.stdout)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        return {"error": "评分输出里没有 JSON", "raw": text[-2000:]}
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as exc:
        return {"error": f"评分输出不是合法 JSON：{exc}", "raw": text[start:start + 2000]}


def normalized_rate(result):
    """评分器可能把通过率写成百分数，统一按 passed/total 重算。"""
    summary = result.get("summary") or {}
    passed, total = summary.get("passed"), summary.get("total")
    if isinstance(passed, (int, float)) and isinstance(total, (int, float)) and total:
        return round(passed / total, 3)
    rate = summary.get("pass_rate")
    if isinstance(rate, (int, float)):
        return round(rate / 100 if rate > 1 else rate, 3)
    return None


def main():
    args = parse_args()
    skill_dir = find_skill(args.skill)
    cases = load_cases(skill_dir, args.cases)
    workspace = REPO / ".scratch" / "quality" / args.skill / f"iteration-{args.iteration}"
    if workspace.exists():
        print(f"提示：{workspace} 已存在，本次结果覆盖同名文件")
    workspace.mkdir(parents=True, exist_ok=True)
    print(f"技能 {args.skill}：{len(cases)} 条用例 × 2 组（带技能 / 不带技能），"
          f"并发 {args.workers}，单次上限 {args.cap}s\n结果 {workspace}")

    jobs = []
    for case in cases:
        for with_skill in (True, False):
            arm = "with_skill" if with_skill else "without_skill"
            sandbox = SANDBOX_ROOT / f"coop-{args.skill}-quality" / slug(case) / arm
            jobs.append((case, arm, sandbox))

    def run_arm(job):
        case, arm, sandbox = job
        work, overlay = prepare_arm(sandbox, skill_dir, case, arm == "with_skill")
        transcript, wall_ms, truncated = run_session(case["prompt"], work, overlay, args.cap)
        arm_dir = workspace / slug(case) / arm
        shutil.rmtree(arm_dir, ignore_errors=True)
        (arm_dir / "outputs").mkdir(parents=True)
        (arm_dir / "transcript.jsonl").write_text(transcript)
        for path in sorted(work.rglob("*")):
            if not path.is_file():
                continue
            # 任务给的输入文件按最终状态一并收进产物，改动就发生在这个文件上
            target = arm_dir / "outputs" / path.relative_to(work)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        timing = collect_timing(transcript, wall_ms)
        timing["truncated"] = truncated
        (arm_dir / "timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=2))
        kept = sum(1 for p in (arm_dir / "outputs").rglob("*") if p.is_file())
        if timing["events"] == 0:
            print(f"{slug(case)}/{arm} 本次运行没有任何事件输出，标记为不可信")
        else:
            print(f"{slug(case)}/{arm} 完成 {timing['duration_ms'] / 1000:.1f}s "
                  f"加载技能 {','.join(timing['loaded_skills']) or '无'} 产物 {kept} 个文件"
                  f"{'（用时贴住上限，已截断）' if truncated else ''}")
        return job, arm_dir, timing["events"], truncated

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        done = list(pool.map(run_arm, jobs))

    summary = {"with_skill": [], "without_skill": []}
    unverified = [f"{slug(case)}/{arm}" for (case, arm, _), _, events, _ in done if events == 0]
    truncated = [f"{slug(case)}/{arm}" for (case, arm, _), _, events, cut in done if cut and events]
    graded_errors = []
    if not args.no_grade:
        for (case, arm, _), arm_dir, _, _ in done:
            if not case.get("assertions"):
                print(f"{slug(case)}/{arm} 没有 assertions，跳过评分")
                continue
            result = grade(case, arm_dir, 180)
            (arm_dir / "grading.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
            rate = normalized_rate(result)
            summary[arm].append(rate)
            if result.get("error"):
                graded_errors.append(f"{slug(case)}/{arm}")
                print(f"{slug(case)}/{arm} 评分失败：{result['error']}")
            else:
                print(f"{slug(case)}/{arm} 通过率 {rate}")

    def mean(values):
        clean = [v for v in values if isinstance(v, (int, float))]
        return round(sum(clean) / len(clean), 3) if clean else None

    benchmark = {
        "skill": args.skill,
        "iteration": args.iteration,
        "cases": len(cases),
        "with_skill_pass_rate": mean(summary["with_skill"]),
        "without_skill_pass_rate": mean(summary["without_skill"]),
        "unverified_runs": unverified,
        "truncated_runs": truncated,
        "grading_errors": graded_errors,
    }
    if benchmark["with_skill_pass_rate"] is not None and benchmark["without_skill_pass_rate"] is not None:
        benchmark["delta"] = round(benchmark["with_skill_pass_rate"] - benchmark["without_skill_pass_rate"], 3)
    (workspace / "benchmark.json").write_text(json.dumps(benchmark, ensure_ascii=False, indent=2))
    print(f"带技能通过率 {benchmark['with_skill_pass_rate']} "
          f"不带技能通过率 {benchmark['without_skill_pass_rate']} "
          f"差值 {benchmark.get('delta')}")
    if unverified:
        print(f"有 {len(unverified)} 组运行没有事件输出，结果不可信：{'、'.join(unverified)}")
    if truncated:
        print(f"有 {len(truncated)} 组运行撞到 --cap 被截断，产物可能不完整，"
              f"这一组的通过率不能当结论：{'、'.join(truncated)}")
    if graded_errors:
        print(f"有 {len(graded_errors)} 组评分失败：{'、'.join(graded_errors)}")
    print(f"汇总 {workspace / 'benchmark.json'}")
    return 1 if unverified or truncated or graded_errors else 0


if __name__ == "__main__":
    sys.exit(main())
