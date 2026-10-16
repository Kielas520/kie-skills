import argparse
import json
import os
import shutil
import socket
import subprocess
from pathlib import Path
from urllib import error, request

HOME = Path.home()
REPO_NAME = "kie-skills"
REPO_REMOTE_HINT = "Kielas520/kie-skills"

# 键、版本命令、期望。缺失判定只看真实可执行文件，不看 agent shell 的内置命令
TOOLS = (
    ("git", "--version", "任意版本，工作空间的一切操作的前提"),
    ("gh", "--version", "已登录 github.com，scopes 至少含 repo"),
    ("uv", "--version", "kie-python-style 与 kie-skill-dev 的校验依赖它"),
    ("uvx", "--version", "随 uv 提供，uv 的官方安装脚本会一并装出"),
    ("cargo", "--version", "与项目工具链一致"),
    ("rustup", "--version", "含 rustfmt 与 clippy 组件"),
    ("node", "--version", "v20 及以上"),
    ("npm", "--version", "随 node 提供"),
    ("npx", "--version", "随 node 提供，部署技能用 skills CLI"),
    ("python3", "--version", "3.10 及以上，探测脚本与评估脚本用"),
    ("rg", "--version", "kie-agent-rules 优先使用的命令行工具，缺失时用 grep"),
    ("fd", "--version", "kie-agent-rules 优先使用的命令行工具，缺失时用 find"),
    ("bat", "--version", "kie-agent-rules 优先使用的命令行工具，缺失时用 cat"),
    ("sd", "--version", "kie-agent-rules 优先使用的命令行工具，缺失时用 sed"),
    ("jq", "--version", "gh 的 --jq 用内置实现，独立 jq 只在脚本里需要"),
    ("gio", "--version", "回收站首选工具"),
    ("gomi", "--version", "回收站备选"),
    ("trash", "--version", "回收站备选"),
    ("unshare", "--version", "评估脚本的隔离依赖它，且 user namespace 要放开"),
    ("brew", "--version", "缺失工具安装顺序的首选"),
    ("paper-search", "--help", "kie-dev-solution 的学术检索入口"),
    ("context7", "--help", "kie-dev-solution 的库文档查询入口，包名未确认"),
    ("claude", "--version", "kie-skill-dev 的 claude 适配与判定信号"),
)

SYSTEM_KEYS = (
    ("kernel.apparmor_restrict_unprivileged_userns", "0", "0 表示不限制非特权 user namespace"),
    ("kernel.unprivileged_userns_clone", "1", "1 表示允许创建非特权 user namespace"),
)

PROXY_KEYS = ("https_proxy", "HTTPS_PROXY", "http_proxy", "HTTP_PROXY", "all_proxy", "ALL_PROXY", "no_proxy", "NO_PROXY")

NET_TARGETS = (
    "https://github.com",
    "https://api.github.com",
    "https://registry.npmjs.org",
    "https://pypi.org",
    "https://index.crates.io/config.json",
)

UA = "env-probe/0.1.0"


def run(cmd, timeout=20):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    text = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, text.strip()


def first_line(text):
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def entry(name, current, expected, action="", group="", todo=False):
    return {"group": group, "name": name, "current": current, "expected": expected,
            "action": action, "todo": bool(todo and action)}


def probe_workspace(root):
    rows = []
    exists = root.is_dir()
    rows.append(entry(str(root), "存在" if exists else "不存在", "存在",
                      "" if exists else f"mkdir -p {root}", "工作空间", todo=True))
    for sub in (".tmp", ".draft", "test"):
        path = root / sub
        exists = path.is_dir()
        rows.append(entry(str(path), "存在" if exists else "不存在", "存在",
                          "" if exists else f"mkdir -p {path}", "工作空间", todo=True))
    containers = []
    if root.is_dir():
        containers = sorted(d.name for d in root.iterdir() if d.is_dir() and d.name.endswith("-p"))
    rows.append(entry("项目容器", f"{len(containers)} 个（{'、'.join(containers) if containers else '无'}）",
                      "由其他技能按任务建出，本技能不预建", "", "工作空间"))
    return rows


def find_clones():
    found = set()
    for current, dirs, _ in os.walk(HOME):
        depth = len(Path(current).relative_to(HOME).parts)
        if depth >= 3:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        if Path(current).name == REPO_NAME and (Path(current) / ".git").exists():
            found.add(Path(current))
    return sorted(found)


def clone_remote(path):
    code, text = run(["git", "-C", str(path), "remote", "get-url", "origin"])
    return text if code == 0 else ""


def probe_repo(root):
    rows = []
    target = root / REPO_NAME
    if target.is_dir():
        _, branch = run(["git", "-C", str(target), "rev-parse", "--abbrev-ref", "HEAD"])
        _, commit = run(["git", "-C", str(target), "rev-parse", "--short", "HEAD"])
        _, status = run(["git", "-C", str(target), "status", "--short"])
        remote = clone_remote(target)
        rows.append(entry(str(target), f"{branch or '分支未知'} {commit or ''}，远端 {remote or '未知'}",
                          f"{REPO_REMOTE_HINT} 的克隆", "", "仓库落位"))
        rows.append(entry("目标仓库工作区", "干净" if not status else f"有改动：{first_line(status)}", "干净",
                          "" if not status else "报给用户，等其处理后再继续", "仓库落位", todo=bool(status)))
    else:
        rows.append(entry(str(target), "不存在", f"{REPO_REMOTE_HINT} 的克隆", "下面两条二选一", "仓库落位"))
    others = [path for path in find_clones() if path != target]
    for path in others:
        rows.append(entry(str(path), f"已有克隆，远端 {clone_remote(path) or '未知'}", f"落位到 {target}",
                          f"确认 status 干净且 worktree 只有主仓库后 mv {path} {target}", "仓库落位", todo=True))
    if not target.is_dir() and not others:
        rows.append(entry("克隆来源", "本机无克隆", f"落位到 {target}",
                          f"git clone git@github.com:{REPO_REMOTE_HINT}.git {target}", "仓库落位", todo=True))
    return rows


def probe_tools():
    rows = []
    for name, args, expected in TOOLS:
        path = shutil.which(name)
        if not path:
            rows.append(entry(name, "缺失", expected, f"按 references/tools.md 的顺序安装 {name}", "工具链", todo=True))
            continue
        code, text = run([path, args], timeout=25)
        version = first_line(text) if code == 0 else f"探测失败：{first_line(text)}"
        rows.append(entry(name, version or f"存在（{path}）", expected, "", "工具链"))
    return rows


def to_host_port(value):
    if not value:
        return None
    text = value.split("://", 1)[-1]
    host, _, port = text.rpartition(":")
    if not host or not port.isdigit():
        return None
    return host, int(port)


def probe_system(check_eval):
    # user namespace 只在要跑技能评估时计入待确认项，日常体检只报现状
    rows = []
    restricted = None
    for key, want, hint in SYSTEM_KEYS:
        path = Path("/proc/sys") / key.replace(".", "/")
        if not path.exists():
            continue
        value = path.read_text().strip()
        if key == SYSTEM_KEYS[0][0]:
            restricted = value
        rows.append(entry(key, value, f"{want}（{hint}）",
                          "" if value == want else "按 references/system-network.md 的 sysctl 命令处理，需 root", "系统与网络",
                          todo=check_eval))
    code, text = run(["unshare", "-rm", "true"])
    if code is None:
        rows.append(entry("unshare -rm", f"无法执行：{text}", "退出码 0", "先补 unshare", "系统与网络", todo=check_eval))
    else:
        rows.append(entry("unshare -rm", f"退出码 {code}" + (f"，{first_line(text)}" if text else ""), "退出码 0",
                          "" if code == 0 else "评估脚本会退出码 2，先放开 user namespace", "系统与网络", todo=check_eval))
    usable = code == 0 and restricted in (None, "0")
    rows.append(entry("评估隔离可用性", "可用" if usable else "不可用", "可用（trigger_eval.py 与 quality_eval.py 才能跑）",
                      "" if usable else "放开 user namespace 后重跑探测", "系统与网络", todo=check_eval))
    present = {key: os.environ[key] for key in PROXY_KEYS if os.environ.get(key)}
    if not present:
        rows.append(entry("代理变量", "未设置", "按本机网络情况设置或不设", "", "系统与网络"))
    else:
        sample = present.get("https_proxy") or present.get("HTTPS_PROXY") or first_line(json.dumps(present))
        parts = to_host_port(sample)
        state = "未知"
        if parts:
            try:
                with socket.create_connection(parts, timeout=3):
                    state = f"{parts[0]}:{parts[1]} 可连"
            except OSError as exc:
                state = f"{parts[0]}:{parts[1]} 连不上（{type(exc).__name__}）"
        rows.append(entry("代理变量", f"{len(present)} 个，取样 {sample}，{state}", "端口可连",
                          "" if state.endswith("可连") else "核对代理进程是否启动", "系统与网络", todo=True))
        rows.append(entry("代理落点", "变量只出现在当前进程，需核对其余落点", "用户交互终端也能拿到代理",
                          "排查 /etc/environment、/etc/profile.d/*、~/.bashrc、~/.profile，缺失时由用户写入", "系统与网络"))
    code, name = run(["git", "config", "--global", "user.name"])
    _, mail = run(["git", "config", "--global", "user.email"])
    _, ident = run(["git", "var", "GIT_AUTHOR_IDENT"])
    if code == 0 and name and mail:
        rows.append(entry("git 全局身份", f"{name} <{mail}>", "已配置", "", "系统与网络"))
    else:
        rows.append(entry("git 全局身份", f"姓名 {'有' if name else '无'}、邮箱 {'有' if mail else '无'}，当前生效身份 {first_line(ident) or '取不到'}",
                          "已配置", "值由用户提供后写 git config --global", "系统与网络", todo=True))
    code, text = run(["gh", "auth", "status"])
    account = ""
    for line in text.splitlines():
        if "Logged in to" in line:
            account = line.strip().lstrip("✓ ")
    if code == 0:
        rows.append(entry("gh 登录", account or "已登录", "已登录且 scopes 够用", "", "系统与网络"))
    else:
        rows.append(entry("gh 登录", f"未登录或报错：{first_line(text)}", "已登录", "gh auth login（交互式，用户执行）", "系统与网络", todo=True))
    code, text = run(["git", "config", "--global", "credential.https://github.com.helper"])
    if code != 0 or "gh auth git-credential" not in text:
        rows.append(entry("git 凭据助手", text or "未配置", "指向 gh auth git-credential",
                          "gh auth login 会一并写回，或手动配置 credential.helper", "系统与网络", todo=True))
    else:
        rows.append(entry("git 凭据助手", text, "指向 gh auth git-credential", "", "系统与网络"))
    code, text = run(["ssh", "-G", "github.com"])
    if code != 0:
        rows.append(entry("SSH 配置", f"读不到：{first_line(text)}", "能读出 hostname 与 port", "确认 ~/.ssh/config 与 ssh 可用", "系统与网络", todo=True))
    else:
        hostname = port = ""
        for line in text.lower().splitlines():
            if line.startswith("hostname "):
                hostname = line.split(None, 1)[1].strip()
            elif line.startswith("port "):
                port = line.split(None, 1)[1].strip()
        direct = hostname == "github.com" and port == "22"
        rows.append(entry("SSH 端点", f"{hostname or '未知'}:{port or '未知'}", "22 可用则直连，否则走 ssh.github.com:443",
                          "22 不可达时按 references/system-network.md 改 ~/.ssh/config", "系统与网络", todo=direct))
    return rows


def probe_network():
    rows = []
    for url in NET_TARGETS:
        req = request.Request(url, headers={"User-Agent": UA}, method="GET")
        try:
            with request.urlopen(req, timeout=15) as resp:
                code = resp.status
        except error.HTTPError as exc:
            code = exc.code
        except Exception as exc:
            rows.append(entry(url, f"失败：{type(exc).__name__}: {exc}", "HTTP 200 或 3xx", "核对代理与 DNS", "联网", todo=True))
            continue
        rows.append(entry(url, f"HTTP {code}", "HTTP 200 或 3xx",
                          "" if code < 400 else "403 多为缺 User-Agent 或代理拦截", "联网", todo=True))
    return rows


def render(rows):
    lines = []
    current = None
    for row in rows:
        if row["group"] != current:
            current = row["group"]
            lines += ["", f"## {current}", "", "| 项 | 现状 | 期望 | 建议动作 |", "| --- | --- | --- | --- |"]
        lines.append(f"| {row['name']} | {row['current']} | {row['expected']} | {row['action'] or '—'} |")
    todo = [row for row in rows if row["todo"]]
    lines += ["", f"待确认项 {len(todo)} 条。"]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="探测本机环境与工作空间现状，只读，不创建与修改任何文件")
    parser.add_argument("--workspace", default=str(HOME / "kie-ws"), help="工作空间根目录，默认 ~/kie-ws")
    parser.add_argument("--net", action="store_true", help="追加联网检查，各域名取一次状态码")
    parser.add_argument("--json", action="store_true", help="只输出 JSON")
    parser.add_argument("--eval", action="store_true", help="要跑技能评估时使用，user namespace 相关项计入待确认")
    args = parser.parse_args()
    root = Path(args.workspace).expanduser()
    rows = probe_workspace(root) + probe_repo(root) + probe_tools() + probe_system(args.eval)
    if args.net:
        rows += probe_network()
    if args.json:
        print(json.dumps({"workspace": str(root), "rows": rows}, ensure_ascii=False, indent=2))
        return 0
    print(f"探测: env_probe.py，工作空间 {root}")
    print(render(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
