---
name: kie-env-setup
description: |
  建立与核对本机开发环境的前提条件：工作空间根是否建好、kie-skills 仓库是否就位、命令行工具链是否齐全、系统与网络是否可用（代理、git 身份、gh 登录、SSH 连通，以及技能评估要用的非特权 user namespace）。用户说「配一下环境」「新机器初始化」「环境体检」「工作空间还没建」「工具不全」「装一下 uv」「技能评估脚本因为 unshare 受限跑不起来」「kie-skills 仓库该放哪」时使用，包括只要求看现状、不要求执行的情况。本技能只做探测与补齐，不处置工作空间里已有的内容；单个项目的依赖安装走 kie-python-style 与 kie-rust-gates，技能的编写、修改、接入与部署走 kie-skill-dev，某个工具怎么用的知识性问题不加载本技能。
license: MIT
compatibility: 需要 Linux、python3 与 git；补齐系统层配置需要用户具备 sudo 权限；联网探测需要代理或直连可用
metadata:
  author: Kielas
  version: "0.5.0"
---

# 环境初始化技能

把本机调到技能集假定的状态：任务工作空间、技能仓库位置、命令行工具与系统网络配置。

## 子能力

| 子能力 | 产出 | 改不改本机 |
| --- | --- | --- |
| 探测 | `scripts/env_probe.py` 的输出 | 不改 |
| 报告差异 | 按四组列出的差异清单 | 不改 |
| 逐项补齐 | 每条差异执行后的验证结果 | 改，每条都等用户确认 |

用户只要求看现状时，做到报告差异为止。

## 纪律

- 补齐时确认一条执行一条，不批量执行，不做清单以外的动作。
- 系统层动作不代跑：`sudo sysctl`、`sudo apt`、安装 linuxbrew、写 shell 配置文件这类改系统状态或要密码的操作，只给命令、影响与回退方式，由用户自己执行。用户要求整批代办时，也先把命令逐条列出再动手。
- 本机取值只取本次探测输出：代理地址与端口、git 身份、已有克隆的路径、工具是否已装与版本、系统开关状态，都按本次 `scripts/env_probe.py` 的输出写，不写进 `SKILL.md` 与 `references/`，也不引用历史会话里的取值。参考文件只写判定方式与安装内容。
- 每条差异都附上探测命令与原始输出，不写「可能缺失」这类无依据结论。

## 步骤 1：探测

```bash
python3 scripts/env_probe.py            # 本机检查，不联网
python3 scripts/env_probe.py --net      # 追加联网检查，各域名取一次状态码
python3 scripts/env_probe.py --json     # 只输出 JSON，便于前后比对
python3 scripts/env_probe.py --eval     # 要跑技能评估时使用，user namespace 相关项计入待确认
python3 scripts/env_probe.py --task-root ~/kie-ws/技能维护  # 指定本次任务根，检查其下 kie-skills
```

脚本只读：不创建、不修改、不删除任何文件，也不执行安装。退出码 0 表示探测完成，不代表环境合格。

`--workspace` 指定工作空间根，默认 `~/kie-ws`。`--task-root` 指定本次任务根，省略时只检查工作空间根并探测已有仓库，不猜测任务名称。脚本在家目录下最多 3 层、指定工作空间下最多 2 层查找 Git 克隆，并核对远端。搜索范围以外的已知克隆需另行使用只读 Git 命令检查，不把“未发现”解释为全机不存在。

## 步骤 2：报告差异清单

按脚本输出的四组列出，每条给「现状 / 期望 / 建议动作」，标出该动作是否需要用户自己执行。

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
```

清单末尾写一行计数：待确认几项、用户需要自己执行几条命令。缺失工具的命令按 `references/tools.md` 的安装顺序给，一次给一条可执行命令加一条验证命令。

## 步骤 3：逐项补齐

### 3.1 任务工作空间

初始化只创建工作空间根：

```bash
mkdir -p ~/kie-ws
```

有具体任务时，没有工单编号使用 `~/kie-ws/<任务简述>/`，上下文明确本任务的 `SWE-<编号>` 时使用 `~/kie-ws/swe-<编号>-<任务简述>/`。命名判定遵循 `kie-agent-rules` 的 `references/workspace.md`，不自动添加任务类型前缀。按需创建任务根，仓库直接位于 `<任务根>/<仓库名>/`，任务内的文档层级按对应技能保留。

临时文件都放在 `<任务根>/.tmp/`，按活动创建子目录：

- 测试使用 `.tmp/test/`，多轮测试使用 `.tmp/test/<n>/`，保留各轮 `test-report-n.md`。
- 调研使用 `.tmp/<调研简述>/`。
- 仅文档任务使用 `.tmp/docs-tmp/`，已有修复与评论活动分组继续保留。

不预建全局临时目录、仓库目录或 `~/kie-ws/AGENTS.md`。进入任务时记录任务根，命令优先使用工具的 `cwd` 参数或 `git -C`。进入仓库执行操作或测试后，恢复会话工作目录到记录的任务根，不用子 shell 的 `pwd` 结果代替恢复。

验证：

```bash
test -d ~/kie-ws
```

### 3.2 技能仓库位置

新增技能仓库默认放在 `<任务根>/kie-skills/`，与其他仓库遵循同一约定。按以下顺序判定：

1. 先探测已有克隆，确认远端为 `Kielas520/kie-skills`，报告实际路径、分支、commit 与工作区状态。已有克隆保持原位，不要求迁移。任务内已有调研克隆时直接复用，进入开发时在其中切换开发分支。
2. 有多个克隆时，优先使用本次任务根下的克隆，其他克隆按实际路径报告。已有改动只报告，不覆盖。
3. 未发现已有克隆时，确认搜索范围与已知路径，确定本次任务根。目标路径已存在但不是该仓库时停止并报告，不覆盖目标路径。仅在批准克隆后执行：

```bash
mkdir -p "<任务根>"
git clone git@github.com:Kielas520/kie-skills.git "<任务根>/kie-skills"
```

用本次选定的实际克隆路径验证：

```bash
git -C "<实际克隆路径>" rev-parse --abbrev-ref HEAD
git -C "<实际克隆路径>" rev-parse --short HEAD
git -C "<实际克隆路径>" remote -v
git -C "<实际克隆路径>" status --short
```

### 3.3 工具链

以探测输出为准逐个确认缺失项，再按 `references/tools.md` 的安装顺序与执行者给命令。装完一个验证一个，不把安装命令攒成一段脚本执行。

### 3.4 系统与网络

条目、判据、命令与影响见 `references/system-network.md`：代理环境变量、git 身份、gh 登录、SSH 连通，以及需要跑技能评估时才检查的非特权 user namespace。需要 sudo 的一律交给用户执行。

## 验证

| 动作 | 验证命令 | 通过判据 |
| --- | --- | --- |
| 建工作空间目录 | `test -d ~/kie-ws`，创建任务根时另用 `test -d "<任务根>"` | 退出码 0 |
| 克隆或复用仓库 | `git -C "<实际克隆路径>" status --short` | 命令成功，按实际输出报告改动 |
| 装补工具 | `bash -c 'command -v <工具>'` | 输出真实可执行文件路径 |
| 放开 user namespace | `unshare -rm true` | 无输出且退出码 0 |
| 代理可用 | `curl -s -o /dev/null -w '%{http_code}' https://api.github.com` | 输出 200 |
| gh 登录 | `gh auth status` | 输出含 `Logged in to github.com` |
| SSH 连通 | `ssh -T git@github.com` | 输出含 `successfully authenticated` |

## 交付

```
工作空间: ~/kie-ws（已建 / 已存在），任务根: <本次任务根 / 未指定>
仓库: <实际克隆路径> <分支> <commit>（新克隆 / 原位复用）
工具: 已补齐 <工具列表>；仍缺 <工具列表>
系统与网络: <改动的项与结果>
验证: <命令> -> <结果>
待用户执行: <需要密码或改系统状态的命令，逐条列出>
```

## Gotchas

- 判断工具是否装上要看真实可执行文件：有的 agent 在自己的 shell 里内置了 `rg`、`fd`、`jq` 这类命令，`command -v` 能命中，用户的终端里却没有。用 `bash -c 'command -v <工具>'` 或 `shutil.which` 判定。
- 代理变量可能只存在于 agent 运行时进程里，用户自己的终端拿不到。判断用户终端有没有代理，要单独看 `/etc/environment`、`/etc/profile.d/*`、`~/.bashrc` 与 `~/.profile`。
- uv 缺失时 kie-skill-dev 的校验命令 `uvx --from skills-ref agentskills validate` 跑不了；skills CLI（`npx -y skills`）没有 validate 子命令，不能拿它顶替。
