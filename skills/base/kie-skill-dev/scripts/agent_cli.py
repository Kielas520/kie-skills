"""评估会话驱动的 agent CLI 适配：探测可用 CLI、装配沙箱、解析输出。

trigger_eval.py 与 quality_eval.py 共用本模块。新增 agent 时实现 Agent 子类并加进 AGENTS：
会话命令、技能投放位置、判定信号、输出解析四处都要落地。
"""

import json
import os
import pathlib
import re
import shutil
import signal
import subprocess

HOME = pathlib.Path.home()
USER_SKILLS = HOME / ".agents" / "skills"
SANDBOX_ROOT = HOME / "project" / "test"
WINDOWS_PATH = re.compile(r"([A-Za-z]):[\\/](.*)")
PATH_SEPARATORS = re.compile(r"[\\/]+")


class HarnessError(Exception):
    """无法开始评估：选不到 agent CLI、隔离条件不成立。"""


def find_repo():
    for parent in pathlib.Path(__file__).resolve().parents:
        if (parent / "skills" / "base" / "kie-skill-dev").is_dir():
            return parent
    raise SystemExit("错误：找不到仓库根目录，本脚本需要在 kie-skills 仓库内运行")


REPO = find_repo()


def iter_events(stream):
    for line in stream.splitlines():
        if not line.startswith("{"):
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def copy_skills(source, target):
    """整份技能集平铺复制到沙箱，去掉各技能的 evals。"""
    target.mkdir(parents=True, exist_ok=True)
    for src in sorted(source.glob("*/*")):
        if not src.is_dir():
            continue
        shutil.copytree(src, target / src.name)
        shutil.rmtree(target / src.name / "evals", ignore_errors=True)


def windows_to_wsl(path):
    match = WINDOWS_PATH.fullmatch(str(path))
    if not match:
        return None
    return pathlib.Path("/mnt") / match.group(1).lower() / match.group(2).replace("\\", "/")


def test_workspace_masks(work):
    """挡掉测试工作区里用不到的目录：其他运行的沙箱，以及同一轮里其他组、其他用例的沙箱，
    会话翻进去就能接着答。只留当前组自己的目录。"""
    current = None
    for path in work.parents:
        if path.parent == SANDBOX_ROOT:
            current = path
            break
    if current is None:
        return []
    masks = [path for path in sorted(SANDBOX_ROOT.iterdir()) if path != current and path.is_dir()]
    # 质量评估把两组放在同一轮目录下，逐层盖住兄弟目录，直到本轮沙箱根
    arm = work.parent
    while arm != current:
        masks += [path for path in sorted(arm.parent.iterdir()) if path != arm and path.is_dir()]
        arm = arm.parent
    return masks


def terminate(proc):
    """结束整条进程组：只结束直接子进程时，agent CLI 本体可能继续跑下去。"""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        proc.kill()


class Agent:
    """一个 agent CLI 的评估适配。

    会话命令由 command() 给出，技能投放由 prepare() 决定，判定信号由 marker() 与
    normalize() 决定，输出解析由 text()、timing()、loaded_skills()、has_events() 决定。
    """

    name = ""
    binary = ""
    session_tools = ""
    workspace_tools = ""

    def __init__(self):
        self._mounts = None

    @property
    def found(self):
        return shutil.which(self.binary) is not None

    def user_skill_dirs(self):
        """该 CLI 会读取的用户层技能目录。"""
        return []

    def mask_dirs(self):
        """需要用 tmpfs 遮蔽的用户层技能目录；遮蔽不到的目录有技能就直接报错。"""
        if self._mounts is None:
            self._mounts = self.compute_mask_dirs()
        return self._mounts

    def compute_mask_dirs(self):
        mounts = []
        for path in self.user_skill_dirs():
            if not path.is_dir():
                continue
            if path.is_relative_to("/mnt"):
                if any(path.iterdir()):
                    raise HarnessError(
                        f"错误：{self.name} 的用户层技能目录 {path} 在 Windows 侧，tmpfs 遮蔽不到，"
                        "评估会混入用户技能。先清空该目录再重跑。")
                continue
            mounts.append(path)
        return mounts

    def prepare(self, sandbox, skills_source, with_skills):
        """装配沙箱，返回技能投放根目录。"""
        raise NotImplementedError

    def command(self, work, cap, tools, auto_approve):
        """会话命令，工作目录已切到 work。"""
        raise NotImplementedError

    def normalize(self, line):
        """判定信号在输出里的实际写法与判据的差异在比较前抹平。"""
        return line

    def hit(self, line, skills_root, skill_name):
        """这一行输出是否说明会话加载了沙箱里的目标技能。"""
        raise NotImplementedError

    def text(self, stream):
        raise NotImplementedError

    def timing(self, stream, wall_ms):
        raise NotImplementedError

    def loaded_skills(self, stream):
        return []

    def has_events(self, stream):
        raise NotImplementedError

    def ask(self, prompt, cap):
        """单轮问答，返回助手回复文本。评分与接入验证用。"""
        raise NotImplementedError

    def run(self, prompt, work, cap, tools, auto_approve):
        masks = [REPO] + self.mask_dirs() + test_workspace_masks(work)
        inner = " && ".join([f"mount -t tmpfs none {path}" for path in masks]
                            + [f"cd {work}", "exec " + self.command(work, cap, tools, auto_approve)])
        return ["unshare", "-rm", "bash", "-c", inner, f"{self.name}-eval", prompt]


class OmpAgent(Agent):
    name = "omp"
    binary = "omp"
    session_tools = "read,grep,glob"
    workspace_tools = "read,write,edit,bash,grep,glob"

    def user_skill_dirs(self):
        return [USER_SKILLS]

    def prepare(self, sandbox, skills_source, with_skills):
        root = sandbox / "skills"
        if with_skills:
            copy_skills(skills_source, root)
        else:
            root.mkdir(parents=True, exist_ok=True)
        (sandbox / "overlay.yml").write_text("skills:\n"
                                             f"  customDirectories:\n    - {root}\n"
                                             "  enableAgentsUser: false\n")
        return root

    def command(self, work, cap, tools, auto_approve):
        # 路径从沙箱推出来，不落实例字段：多个组并发跑同一个适配实例，字段会被别的组改写
        overlay = work.parent / "overlay.yml"
        approve = " --auto-approve" if auto_approve else ""
        return (f"omp -p --mode json --no-session --config {overlay} --tools {tools}"
                f"{approve} --max-time {cap} \"$1\"")

    def hit(self, line, skills_root, skill_name):
        return f'"resolvedPath":"{skills_root / skill_name / "SKILL.md"}"' in line

    def text(self, stream):
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

    def timing(self, stream, wall_ms):
        # message_end 是每个助手消息的唯一一次落账，turn_end 与 agent_end 会重复同一份 usage
        tokens = 0
        events = 0
        for event in iter_events(stream):
            events += 1
            if event.get("type") != "message_end":
                continue
            message = event.get("message") or {}
            if message.get("role") != "assistant":
                continue
            tokens += ((message.get("usage") or {}).get("totalTokens") or 0)
        return {"duration_ms": round(wall_ms), "total_tokens": tokens, "events": events,
                "loaded_skills": self.loaded_skills(stream)}

    def loaded_skills(self, stream):
        return sorted(set(re.findall(r'"resolvedPath":"[^"]*/skills/([^/"]+)/SKILL\.md"', stream)))

    def has_events(self, stream):
        return '"type":"tool_execution_start"' in stream

    def ask(self, prompt, cap):
        cmd = ["omp", "-p", "--mode", "json", "--no-session", "--tools", "read", f"--max-time={cap}"]
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=cap + 30)
        return self.text(proc.stdout)


class ClaudeAgent(Agent):
    name = "claude"
    binary = "claude"
    session_tools = "Read,Grep,Glob,Skill"
    workspace_tools = "Read,Write,Edit,Bash,Grep,Glob,Skill"

    def config_dir(self):
        proc = subprocess.run(["claude", "auth", "status"], capture_output=True, text=True, timeout=60)
        try:
            config = json.loads(proc.stdout)["configDirectory"]
        except (json.JSONDecodeError, KeyError, TypeError):
            raise HarnessError(f"错误：读不到 claude 的配置目录，`claude auth status` 输出为："
                               f"{proc.stdout[:200] or proc.stderr[:200]}")
        return windows_to_wsl(config) or pathlib.Path(config)

    def user_skill_dirs(self):
        config = self.config_dir()
        dirs = [HOME / ".claude" / "skills"]
        if config != HOME / ".claude":
            dirs.append(config / "skills")
        return dirs

    def prepare(self, sandbox, skills_source, with_skills):
        root = sandbox / "skills-root"
        root.mkdir(parents=True, exist_ok=True)
        if with_skills:
            copy_skills(skills_source, root / ".claude" / "skills")
        return root

    def command(self, work, cap, tools, auto_approve):
        # 路径从沙箱推出来，不落实例字段：多个组并发跑同一个适配实例，字段会被别的组改写
        # --restricted 会连沙箱技能一起停掉，隔离靠 --add-dir 投放的技能目录
        return (f"claude -p \"$1\" --output-format stream-json --verbose --no-session-persistence "
                f"--permission-mode bypassPermissions --tools \"{tools}\" "
                f"--add-dir {work.parent / 'skills-root'}")

    def normalize(self, line):
        # claude 在本机以 Windows 进程运行，路径在输出里是 \\wsl.localhost\... 形式
        return PATH_SEPARATORS.sub("/", line)

    def hit(self, line, skills_root, skill_name):
        # 目录列举里也会出现技能路径，只有加载动作才算命中
        for event in iter_events(line):
            if event.get("type") != "assistant":
                continue
            for block in (event.get("message") or {}).get("content", []):
                if (block.get("type") == "tool_use" and block.get("name") == "Skill"
                        and (block.get("input") or {}).get("skill") == skill_name):
                    return True
        return ("Base directory for this skill" in line
                and str(skills_root / ".claude" / "skills" / skill_name) in self.normalize(line))

    def text(self, stream):
        texts = []
        for event in iter_events(stream):
            if event.get("type") != "assistant":
                continue
            for block in (event.get("message") or {}).get("content", []):
                if block.get("type") == "text" and block.get("text"):
                    texts.append(block["text"])
        return texts[-1] if texts else ""

    def timing(self, stream, wall_ms):
        events = list(iter_events(stream))
        usage = {}
        cost = None
        for event in events:
            if event.get("type") == "result":
                usage = event.get("usage") or {}
                cost = event.get("total_cost_usd")
        tokens = sum(value for key, value in usage.items()
                     if key.endswith("_tokens") and isinstance(value, (int, float)))
        return {"duration_ms": round(wall_ms), "total_tokens": tokens, "events": len(events),
                "total_cost_usd": cost, "loaded_skills": self.loaded_skills(stream)}

    def loaded_skills(self, stream):
        names = set()
        for event in iter_events(stream):
            if event.get("type") != "assistant":
                continue
            for block in (event.get("message") or {}).get("content", []):
                if block.get("type") == "tool_use" and block.get("name") == "Skill":
                    names.add((block.get("input") or {}).get("skill"))
        return sorted(name for name in names if name)

    def has_events(self, stream):
        return any(event.get("type") in ("assistant", "result") for event in iter_events(stream))

    def ask(self, prompt, cap):
        cmd = ["claude", "-p", "--output-format", "json", "--no-session-persistence",
               "--permission-mode", "bypassPermissions", "--tools", ""]
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=cap + 30)
        try:
            return json.loads(proc.stdout).get("result") or ""
        except json.JSONDecodeError:
            return ""


AGENTS = [OmpAgent(), ClaudeAgent()]


def by_name(name):
    for agent in AGENTS:
        if agent.name == name:
            return agent
    raise HarnessError(f"错误：没有名为 {name} 的适配，当前支持：{'、'.join(a.name for a in AGENTS)}")


def available():
    return [agent for agent in AGENTS if agent.found]


def select(name):
    """选定本次评估使用的 agent CLI。"""
    if name:
        agent = by_name(name)
        if not agent.found:
            raise HarnessError(f"错误：{agent.binary} 不在 PATH 上，先安装或换一个 agent")
        return agent
    found = available()
    if not found:
        raise HarnessError(f"错误：本机没找到可驱动的 agent CLI，当前支持："
                           f"{'、'.join(a.binary for a in AGENTS)}")
    if len(found) > 1:
        raise HarnessError(f"错误：本机有多个可驱动的 agent CLI：{'、'.join(a.name for a in found)}。"
                           "先问用户这次用哪个，再用 --agent <名字> 指定")
    return found[0]


def add_arguments(parser):
    parser.add_argument("--agent", help="评估会话用哪个 agent CLI，先用 --list-agents 看本机有哪些")
    parser.add_argument("--list-agents", action="store_true", help="列出本机可驱动的 agent CLI 后退出")


def resolve(args):
    """处理 --list-agents 并选定 agent，两者的报错都按「无法开始」退出。"""
    if args.list_agents:
        found = available()
        for agent in AGENTS:
            state = "可用" if agent.found else "未安装"
            print(f"{agent.name}\t{agent.binary}\t{state}")
        raise SystemExit(0 if found else 2)
    return select(args.agent)
