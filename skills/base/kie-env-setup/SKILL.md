---
name: kie-env-setup
description: |
  建立与核对本机开发环境的前提条件：工作空间根是否建好、kie-skills 仓库是否就位、命令行工具链是否齐全、系统与网络是否可用（非特权 user namespace、代理、git 身份、gh 登录、SSH 连通）。用户说「配一下环境」「新机器初始化」「环境体检」「工作空间还没建」「工具不全」「装一下 uv」「评估脚本报隔离条件不成立」「kie-skills 仓库该放哪」时使用，包括只要求看现状、不要求执行的情况。本技能只做探测与补齐，不处置工作空间里已有的内容；单个项目的依赖安装走 kie-python-style 与 kie-rust-gates，技能本身的编写与修改走 kie-skill-dev，某个工具怎么用的知识性问题不加载本技能。
license: MIT
compatibility: 需要 Linux、python3 与 git；补齐系统层配置需要用户具备 sudo 权限；联网探测需要代理或直连可用
metadata:
  author: Kielas
  version: "0.1.0"
---

# 环境初始化技能

把本机调到技能集假定的状态：工作空间目录骨架、技能仓库落位、命令行工具齐全、系统与网络配置可用。产出是一份分组差异清单，加上逐项执行后的验证结果。

## 前置条件

- 会话已加载 `kie-agent-rules`：工作空间路径约定、提交纪律、删除规则都取自它，正文不重复。
- uv 缺失时本技能照常可用：探测脚本只用 Python 标准库。

## 纪律

- 默认只探测与报告。差异清单逐项等用户确认，确认一条执行一条，不批量执行，不做清单以外的动作。
- 系统层动作不代跑：`sudo sysctl`、`sudo apt`、安装 linuxbrew、写 shell 配置文件这类改系统状态或要密码的操作，只给命令、影响与回退方式，由用户自己执行。用户要求整批代办时，也先把命令逐条列出再动手。
- 探测到的取值不作示例：代理地址与端口、git 身份、已有克隆的路径都按本次探测输出写，不套用正文与参考文件里的历史取值。
- 目录移动用 `mv`，不使用 `rm`。
- 每条差异都要有依据：附上探测到的命令与原始输出，不写「可能缺失」这类无依据结论。
- 报告现状时不评价工作量，不预告后续轮次要做的事。

## 步骤 1：探测

```bash
python3 scripts/env_probe.py            # 本机检查，不联网
python3 scripts/env_probe.py --net      # 追加联网检查，各域名取一次状态码
python3 scripts/env_probe.py --json     # 只输出 JSON，便于前后比对
```

脚本只读：不创建、不修改、不删除任何文件，也不执行安装。退出码 0 表示探测完成，不代表环境合格。

## 步骤 2：报告差异清单

按五组输出，每条给「现状 / 期望 / 建议动作」，标出该动作是否需要用户确认。

```markdown
探测: scripts/env_probe.py  <时间>

工作空间
| 项 | 现状 | 期望 | 建议动作 |
| --- | --- | --- | --- |

仓库落位
| 项 | 现状 | 期望 | 建议动作 |

工具链
| 工具 | 现状 | 期望 | 建议动作 |

系统与网络
| 项 | 现状 | 期望 | 建议动作 |

部署与接入
| 项 | 现状 | 期望 | 建议动作 |
```

清单末尾附一行总结：待确认项数、用户需要自己执行的命令数。缺失工具的命令按 `references/tools.md` 的安装顺序给，一次给一条可执行命令加一条验证命令。

## 步骤 3：逐项执行

### 3.1 工作空间骨架

只建工作空间根与三个固定用途目录：

```bash
mkdir -p ~/kie-ws/.tmp ~/kie-ws/.draft ~/kie-ws/test
```

`<项目名称>-p/` 项目容器、`.idea/<任务>/`、`worktrees/<分支名>/` 由对应技能按任务建出，本技能不预先创建。不创建 `~/kie-ws/AGENTS.md`。

验证：

```bash
ls -d ~/kie-ws/.tmp ~/kie-ws/.draft ~/kie-ws/test
```

### 3.2 技能仓库落位

目标路径固定 `~/kie-ws/kie-skills`：`kie-skill-fix` 等技能按这个路径引用脚本。按下面顺序判定，三条互斥：

1. 目标路径已是 `Kielas520/kie-skills` 的克隆：不动它，报告分支、commit 与工作区是否干净。
2. 家目录其他位置已有克隆：移动过去，不重新克隆。

```bash
git -C <已有克隆> status --short                 # 输出必须为空
git -C <已有克隆> worktree list                  # 只允许主仓库一行
git -C <已有克隆> remote -v                      # 确认远端是 Kielas520/kie-skills
mv <已有克隆> ~/kie-ws/kie-skills
```

3. 都没有：克隆。

```bash
git clone git@github.com:Kielas520/kie-skills.git ~/kie-ws/kie-skills
```

验证：

```bash
git -C ~/kie-ws/kie-skills rev-parse --abbrev-ref HEAD
git -C ~/kie-ws/kie-skills rev-parse --short HEAD
git -C ~/kie-ws/kie-skills remote -v
git -C ~/kie-ws/kie-skills status --short
```

移动前先看 `worktree list`：仓库带 worktree 时，`.git/worktrees/*/gitdir` 记的是绝对路径，整体移动会让工作区失效。

### 3.3 工具链

以探测输出为准逐个确认缺失项，再按 `references/tools.md` 的安装顺序给命令。装完一个验证一个，不把安装命令攒成一段脚本执行。

缺失项里的 linuxbrew、uv / uvx、paper-search 三项有依赖顺序，且执行者不同：linuxbrew 由用户执行（官方脚本内部要用 sudo），uv / uvx 与 paper-search 由 agent 执行；命令、验证方式与 linuxbrew 装完后的 `brew shellenv` 落点见 `references/tools.md`。

### 3.4 系统与网络

条目、判据、命令与影响见 `references/system-network.md`：非特权 user namespace（评估脚本隔离的前提）、代理环境变量、git 身份、gh 登录、SSH 连通。需要 sudo 的一律交给用户执行。

### 3.5 部署与接入

用户明确要求时才做，命令见 `references/tools.md` 末节：仓库内建本地维护软链，或用 skills CLI 安装到用户层。

## 验证

| 动作 | 验证命令 | 通过判据 |
| --- | --- | --- |
| 建工作空间目录 | `ls -d ~/kie-ws/.tmp ~/kie-ws/.draft ~/kie-ws/test` | 三条路径都列出 |
| 移动或克隆仓库 | `git -C ~/kie-ws/kie-skills status --short` | 无报错，输出为空或只有未跟踪文件 |
| 装补工具 | `bash -c 'command -v <工具>'` | 输出真实可执行文件路径 |
| 放开 user namespace | `unshare -rm true` | 无输出且退出码 0 |
| 代理可用 | `curl -s -o /dev/null -w '%{http_code}' https://api.github.com` | 输出 200 |
| gh 登录 | `gh auth status` | 输出含 `Logged in to github.com` |
| SSH 连通 | `ssh -T git@github.com` | 输出含 `successfully authenticated` |

## 交付

```
工作空间: ~/kie-ws（.tmp/ .draft/ test/ 已建 / 已存在）
仓库: ~/kie-ws/kie-skills <分支> <commit>（新克隆 / 移动自 <旧路径> / 未动）
工具: 已补齐 <工具列表>；仍缺 <工具列表>
系统与网络: <改动的项与结果>
验证: <命令> -> <结果>
待用户执行: <需要密码或改系统状态的命令，逐条列出>
```

## Gotchas

- 判断工具是否装上要用真实可执行文件，不用 agent shell 的判断结果：agent 的 shell 内置了 `rg`、`fd`、`jq`，`command -v rg` 能命中但这个命令在其真实终端里不存在。用 `bash -c 'command -v <工具>'` 或直接看 `shutil.which` 的返回值。
- `crates.io` 的 API 不带 User-Agent 时返回 403，带上 `-A 'cargo <版本>'` 才 200。拿到 403 不代表断网，别据此下结论。
- 代理变量可能只存在于 agent 运行时进程里，用户自己的交互终端拿不到：本机 2026-10-12 探测时 `/etc/environment`、`/etc/profile.d/*`、`~/.bashrc` 与 `~/.profile` 都搜不到代理端口，而登录 shell 里有。判断「用户终端有没有代理」要单独看配置文件，不能只看当前进程的环境变量。
- 非特权 user namespace 受限时，`unshare -rm` 报 `write failed /proc/self/uid_map: Operation not permitted`，kie-skill-dev 的 `trigger_eval.py` 与 `quality_eval.py` 直接退出码 2（隔离条件不成立）。先查 `kernel.apparmor_restrict_unprivileged_userns`，不要在描述或用例上找原因。
- 全局 git 身份缺失时 `git config --global user.name` 输出为空，但仓库里仍可能有提交：agent 运行时会注入提交身份。判据用 `git var GIT_AUTHOR_IDENT`，它在两种情况下都能给出实际生效的身份来源。
- uv 缺失时 kie-skill-dev 的校验命令 `uvx --from skills-ref agentskills validate` 跑不了；skills CLI（`npx -y skills`）没有 validate 子命令，不要拿它顶替。
- 技能正文里记的本机工具版本会过期：kie-pr-ci-test 与 kie-pr-review-fix 的 Gotchas 记着「本机 gh 为 2.46.0」，2026-10-12 探测已是 2.102.0。以探测输出为准，并把过期的记录报给用户。
- `context7` 的包名未确认：npm 上 `context7`、`ctx7`、`@upstash/context7-mcp` 都存在，含义不同。缺失时报给用户，按用户给的命令安装，不自行挑一个。
- 移动仓库前先确认 `~/.agents/skills/` 里是实拷贝还是软链：skills CLI 装的是实拷贝时移动不影响已装技能，是软链时移动后会全部失效，需要重新安装；`--copy` 安装的一定是实拷贝。本机 2026-10-12 检查到的是实拷贝目录。
