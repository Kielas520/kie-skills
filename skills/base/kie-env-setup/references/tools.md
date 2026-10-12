# 工具链清单

探测方式、期望状态与安装命令。安装顺序按 `kie-agent-rules`：linuxbrew > cargo binstall > apt > 官方安装脚本 > cargo install，都不可行时改用传统命令。每装一个就跑一遍探测命令验证，再进入下一个。`sudo` 需要交互密码，apt 类安装只能由用户执行。

本文件只写判定方式与安装内容；某项是否已装、版本多少，一律取 `scripts/env_probe.py` 的本次输出，这里不记本机取值。

| 工具 | 探测命令 | 期望 | 安装命令（按顺序取第一个可用的） |
| --- | --- | --- | --- |
| git | `git --version` | 任意版本 | `sudo apt install git` |
| gh | `gh auth status` | 输出含 `Logged in to github.com`，scopes 至少 `repo` | 官方安装脚本或 `sudo apt install gh`；未登录走 `gh auth login` |
| uv / uvx | `uv --version`、`uvx --version` | 两者都可执行 | 有 linuxbrew：`brew install uv`；没有 linuxbrew：官方脚本 `curl -LsSf https://astral.sh/uv/install.sh \| sh`。两条都由 agent 执行，官方脚本落在 `~/.local/bin`；`uvx` 随 `uv` 一并装出，两条探测命令都要通过 |
| cargo / rustup | `cargo --version`、`rustup --version` | 可执行 | 官方脚本 `curl -LsSf https://sh.rustup.rs \| sh` |
| rustfmt / clippy | `rustup component list --installed` | 列表含 `rustfmt` 与 `clippy` | `rustup component add rustfmt clippy` |
| node / npm / npx | `node --version`、`npx --version` | 可执行 | 版本管理器或 NodeSource 官方脚本 |
| python3 | `python3 --version` | 3.10 及以上 | `sudo apt install python3` |
| ripgrep（`rg`） | `bash -c 'command -v rg'` | 输出可执行文件路径 | `brew install ripgrep`；`sudo apt install ripgrep`（候选 15.1.0-1ubuntu1）；`cargo install ripgrep` |
| fd（`fd`） | `bash -c 'command -v fd'` | 同上 | `brew install fd`；`sudo apt install fd-find`（候选 10.3.0-2ubuntu1，Ubuntu 上二进制名为 `fdfind`，需自建软链）；`cargo install fd-find` |
| bat | `bash -c 'command -v bat'` | 同上 | `brew install bat`；`sudo apt install bat`（候选 0.25.0-5ubuntu1，Ubuntu 上二进制名为 `batcat`，需自建软链）；`cargo install bat` |
| sd | `bash -c 'command -v sd'` | 同上 | `brew install sd`；`sudo apt install sd`（候选 1.0.0-4ubuntu1）；`cargo install sd` |
| jq | `bash -c 'command -v jq'` | 可执行 | `sudo apt install jq`。gh 的 `--jq` 用内置实现，不依赖它 |
| linuxbrew | `brew --version` | 可执行 | 官方脚本 `curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh \| bash`，**由用户执行**：Ubuntu 与 Debian 上脚本会先用 sudo 装 `build-essential procps curl file git`，需要交互密码。装完由用户把 `eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"` 追加到 `~/.bashrc`，新终端里 `brew` 才可用 |
| gio（回收站） | `gio --version` | 可执行 | `sudo apt install libglib2.0-bin`。删除规则依次尝试 gio trash > gomi > trash-cli，已有 gio 即可 |
| unshare | `unshare -rm true` | 无输出、退出码 0 | 见 `system-network.md` |
| paper-search（MCP） | `bash -c 'command -v paper-search'` | 可执行 | `uv tool install paper-search-mcp`（PyPI 上为 0.1.4），由 agent 执行，落在 `~/.local/bin`。依赖 uv，先补 uv 再装它 |
| context7 CLI | `bash -c 'command -v context7'` | 可执行 | 包名未确认：npm 上 `context7`、`ctx7`、`@upstash/context7-mcp` 都在，含义不同。报给用户后按用户给的命令安装 |

linuxbrew、uv / uvx、paper-search 三项按依赖顺序补：**linuxbrew → uv / uvx → paper-search**。前一项装完并验证通过再动后一项；linuxbrew 由用户执行，uv / uvx 与 paper-search 由 agent 执行。linuxbrew 装好后，其余缺失工具的安装命令优先取 `brew install` 一档。

## 部署与接入（用户要求时才做）

仓库内本地维护，让仓库内的会话能读到技能：

```bash
mkdir -p .agents/skills
ln -sfn ../../skills/<分类>/<技能名> .agents/skills/<技能名>   # omp
ln -sfn ../../skills/<分类>/<技能名> .claude/skills/<技能名>   # claude
```

用户层安装：

```bash
npx -y skills add Kielas520/kie-skills -g -y
npx -y skills add Kielas520/kie-skills --list        # 只列不装
npx skills update -g                                  # 更新已装技能
```

验证：`npx -y skills list -g` 列出技能，或在该 agent 的无头会话里读 `skill://<技能名>`；omp 报 `Unknown skill`、claude 无加载记录说明链接或安装缺失。
