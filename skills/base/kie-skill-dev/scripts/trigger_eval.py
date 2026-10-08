import argparse
import concurrent.futures
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import threading
import time

USER_SKILLS = pathlib.Path.home() / ".agents" / "skills"
SANDBOX_ROOT = pathlib.Path.home() / "project" / "test"


def find_repo():
    for parent in pathlib.Path(__file__).resolve().parents:
        if (parent / "skills" / "base" / "kie-skill-dev").is_dir():
            return parent
    raise SystemExit("错误：找不到仓库根目录，本脚本需要在 kie-skills 仓库内运行")


REPO = find_repo()


def parse_args():
    ap = argparse.ArgumentParser(
        description="技能触发评估：隔离沙箱里逐条查询运行无头会话，按 resolvedPath 判定触发率。"
                    "先用 --runs 1 粗筛，只对结果翻转的用例补 --runs 3。"
                    "退出码 0=全部通过，1=有未通过或有证据不足的运行，2=预检失败"
    )
    ap.add_argument("skill", help="技能名，例如 kie-skill-dev")
    ap.add_argument("--runs", type=int, default=1, help="每条查询重复次数，默认 1")
    ap.add_argument("--workers", type=int, default=12, help="并发进程数，默认 12")
    ap.add_argument("--cap", type=int, default=60, help="单次会话时长上限（秒），默认 60")
    ap.add_argument("--only", help="只跑指定用例：逗号分隔的序号（从 1 开始）或查询文本子串")
    ap.add_argument("--queries", help="用例文件路径，默认取技能的 evals/trigger-queries.json")
    ap.add_argument("--no-preflight", action="store_true",
                    help="跳过预检（默认先用第一条正例确认客户端能加载技能）")
    ap.add_argument("-v", "--verbose", action="store_true", help="每完成一次运行就打一行到 stderr")
    return ap.parse_args()


def sandbox_path(skill):
    # 目录名不带技能名：会话翻到沙箱路径时，不会顺着名字判定这是该技能的评测而去加载它
    return SANDBOX_ROOT / f"coop-{hashlib.sha256(skill.encode()).hexdigest()[:8]}"


def find_skill(skill):
    hits = [p for p in (REPO / "skills").glob(f"*/{skill}") if (p / "SKILL.md").is_file()]
    if len(hits) != 1:
        raise SystemExit(f"错误：skills/*/{skill} 匹配到 {len(hits)} 个目录，需要恰好一个")
    return hits[0]


def load_queries(skill_dir, override):
    cases = json.loads(pathlib.Path(override).read_text() if override
                       else (skill_dir / "evals" / "trigger-queries.json").read_text())
    for item in cases:
        if "query" not in item or "should_trigger" not in item:
            raise SystemExit("错误：用例条目需要 query 与 should_trigger 字段")
    return cases


def filter_cases(cases, spec):
    if not spec:
        return cases
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    if all(p.isdigit() for p in parts):
        picked = []
        for part in parts:
            number = int(part)
            if not 1 <= number <= len(cases):
                raise SystemExit(f"错误：序号 {number} 超出用例范围 1-{len(cases)}")
            picked.append(cases[number - 1])
        return picked
    picked = [case for case in cases if any(part in case["query"] for part in parts)]
    if not picked:
        raise SystemExit(f"错误：没有用例匹配 {spec}")
    return picked


def prepare(skill, sandbox):
    skills = sandbox / "skills"
    shutil.rmtree(sandbox, ignore_errors=True)
    skills.mkdir(parents=True)
    (sandbox / "work").mkdir()
    for src in sorted((REPO / "skills").glob("*/*")):
        if not src.is_dir():
            continue
        shutil.copytree(src, skills / src.name)
        shutil.rmtree(skills / src.name / "evals", ignore_errors=True)
    overlay = sandbox / "overlay.yml"
    overlay.write_text(
        "skills:\n"
        f"  customDirectories:\n    - {skills}\n"
        "  enableAgentsUser: false\n"
    )
    return overlay


def run_one(job):
    idx, run, query, target, sandbox, overlay, cap, log = job
    begun = time.monotonic()
    inner = (
        f"mount -t tmpfs none {REPO} && "
        f"cd {sandbox / 'work'} && "
        "exec omp -p --mode json --no-session "
        f"--config {overlay} --tools read,grep,glob --max-time {cap} \"$1\""
    )
    if USER_SKILLS.is_dir():
        inner = f"mount -t tmpfs none {USER_SKILLS} && " + inner
    cmd = ["unshare", "-rm", "bash", "-c", inner, "omp-eval", query]
    marker = f'"resolvedPath":"{target}"'
    deadline = time.time() + cap + 20
    verdict = "miss"
    with open(log, "w", encoding="utf-8") as fh:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, bufsize=1)
        try:
            for line in proc.stdout:
                fh.write(line)
                if marker in line:
                    # 判定信号已经出现，后面的工作不再产生新信息，直接结束会话
                    verdict = "hit"
                    proc.kill()
                    break
                if time.time() > deadline:
                    verdict = "timeout"
                    proc.kill()
                    break
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            verdict = "timeout"
    if verdict == "miss":
        text = log.read_text(encoding="utf-8", errors="replace")
        if '"type":"tool_execution_start"' not in text:
            verdict = "error"
    return idx, run, verdict, time.monotonic() - begun


def start_heartbeat(progress, lock, interval=5.0):
    stop = threading.Event()

    def loop():
        while not stop.wait(interval):
            now = time.monotonic()
            with lock:
                done, total = progress["done"], progress["total"]
                active = dict(progress["active"])
            running = "、".join(f"#{i}({now - t:.0f}s)" for i, t in sorted(active.items()))
            tail = f"，运行中 {running}" if running else ""
            print(f"[+{now - progress['start']:5.1f}s] 完成 {done}/{total}{tail}", file=sys.stderr)

    threading.Thread(target=loop, daemon=True).start()
    return stop


def main():
    args = parse_args()
    skill_dir = find_skill(args.skill)
    cases = filter_cases(load_queries(skill_dir, args.queries), args.only)

    sandbox = sandbox_path(args.skill)
    overlay = prepare(args.skill, sandbox)
    target = sandbox / "skills" / args.skill / "SKILL.md"
    out = REPO / ".scratch" / "trigger-eval" / args.skill / time.strftime("%Y%m%d-%H%M%S")
    logs = out / "logs"
    logs.mkdir(parents=True)
    print(f"技能 {args.skill}：{len(cases)} 条用例 × {args.runs} 次，并发 {args.workers}，"
          f"单次上限 {args.cap}s\n沙箱 {sandbox}\n结果 {out}", file=sys.stderr)

    positives = [i for i, case in enumerate(cases) if case["should_trigger"]]
    if positives and not args.no_preflight:
        first = positives[0]
        print(f"预检：{cases[first]['query']}", file=sys.stderr)
        _, _, verdict, seconds = run_one(
            (first, 0, cases[first]["query"], target, sandbox, overlay, args.cap,
             logs / "preflight.json"))
        if verdict != "hit":
            print(f"预检未命中（{verdict}，用时 {seconds:.1f}s）：客户端没有把技能喂给模型，"
                  "整批结果不可信，已中止。先确认 omp 本身能正常跑通再重跑，"
                  "确认无误时可以加 --no-preflight。", file=sys.stderr)
            return 2
        print(f"预检通过（{seconds:.1f}s）", file=sys.stderr)

    jobs = [(idx, run, case["query"], target, sandbox, overlay, args.cap, logs / f"q{idx:02d}-r{run}.json")
            for idx, case in enumerate(cases)
            for run in range(1, args.runs + 1)]
    started = time.monotonic()
    lock = threading.Lock()
    progress = {"start": started, "total": len(jobs), "done": 0, "active": {}}
    stop_heartbeat = start_heartbeat(progress, lock)

    def timed(index, job):
        began = time.monotonic()
        with lock:
            progress["active"][index] = began
        try:
            result = run_one(job)
        finally:
            with lock:
                progress["active"].pop(index, None)
                progress["done"] += 1
        if args.verbose:
            print(f"[+{time.monotonic() - started:5.1f}s] {job[7].stem} {result[3]:5.1f}s "
                  f"{result[2]:5}  {job[2]}", file=sys.stderr)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(timed, range(len(jobs)), jobs))
    stop_heartbeat.set()

    by_idx = {}
    for idx, run, verdict, seconds in results:
        by_idx.setdefault(idx, []).append((verdict, seconds))

    rows = []
    failed = 0
    unverified_cases = 0
    for idx, case in enumerate(cases):
        pairs = by_idx.get(idx, [])
        verdicts = [verdict for verdict, _ in pairs]
        hits = verdicts.count("hit")
        decided = hits + verdicts.count("miss")
        unverified = verdicts.count("error") + verdicts.count("timeout")
        rate = hits / decided if decided else None
        ok = None if rate is None else (rate > 0.5) == bool(case["should_trigger"])
        if ok is False:
            failed += 1
        if ok is None:
            unverified_cases += 1
        seconds = [s for _, s in pairs]
        rows.append({
            "query": case["query"],
            "should_trigger": case["should_trigger"],
            "hits": hits,
            "decided": decided,
            "rate": rate,
            "passed": ok,
            "error": verdicts.count("error"),
            "timeout": verdicts.count("timeout"),
            "seconds_mean": round(sum(seconds) / len(seconds), 1) if seconds else None,
            "seconds_max": round(max(seconds), 1) if seconds else None,
        })
        flag = "证据不足" if ok is None else ("通过" if ok else "不通过")
        rate_text = "n/a" if rate is None else f"{rate:.2f}"
        print(f"{'正例' if case['should_trigger'] else '负例'} {flag} {hits}/{decided} "
              f"rate={rate_text} 平均 {rows[-1]['seconds_mean']}s 证据不足 {unverified} "
              f"{case['query']}")

    wall = time.monotonic() - started
    unverified_runs = sum(row["error"] + row["timeout"] for row in rows)
    summary = {
        "skill": args.skill,
        "runs": args.runs,
        "workers": args.workers,
        "cap_seconds": args.cap,
        "wall_seconds": round(wall, 1),
        "positives_passed": sum(1 for row in rows if row["should_trigger"] and row["passed"]),
        "positives_total": sum(1 for row in rows if row["should_trigger"]),
        "negatives_passed": sum(1 for row in rows if not row["should_trigger"] and row["passed"]),
        "negatives_total": sum(1 for row in rows if not row["should_trigger"]),
        "failed": failed,
        "unverified_cases": unverified_cases,
        "unverified_runs": unverified_runs,
    }
    (out / "results.json").write_text(json.dumps({"summary": summary, "cases": rows},
                                                ensure_ascii=False, indent=2))
    print(f"正例 {summary['positives_passed']}/{summary['positives_total']} "
          f"负例 {summary['negatives_passed']}/{summary['negatives_total']} "
          f"墙钟 {wall:.1f}s 超时/错误运行 {unverified_runs} 结果 {out / 'results.json'}")
    if unverified_runs:
        print(f"有 {unverified_runs} 次运行没有产生工具调用事件，列为证据不足未计入分母。"
              "整批都这样通常是客户端或账号侧的问题，先单独复跑确认。")
    return 0 if not failed and not unverified_cases else 1


if __name__ == "__main__":
    sys.exit(main())
