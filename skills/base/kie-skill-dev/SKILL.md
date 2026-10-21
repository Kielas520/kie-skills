---
name: kie-skill-dev
description: 当任务要动本仓库 `skills/` 下技能目录里的文件时才用本技能：新建技能、把已经跑通的流程沉淀成技能，以及技能本身没有出现行为异常时的正文与 description 改写，包括判断字段该怎么命名、目录该怎么组织；改错别字、改一句话这类小修改也算，同样要按版本号与更新日志的约定处理。用户说「写个 skill」「把这套流程固化成技能」「帮我起个技能」「这个技能的 description 太笼统，改到能用」时适用，即使没提到 skill 这个词。不适用：不动任何文件、只要一段解释的问答，别人渠道装来的技能怎么装怎么卸怎么升级，编写 AGENTS.md 与 README 这类普通文档，直接回答即可；已装技能出现行为异常（越界、该做没做、做错事、输出走样、不触发或误触发）走 kie-skill-fix。
license: MIT
compatibility: 需要 python3 与 unshare（评估沙箱隔离）、uv（质量评估脚本用 uv run 运行）与 uvx（skills-ref 校验器），以及一个可无头驱动的 agent CLI（用 --list-agents 看本机有哪些）
metadata:
  author: Kielas
  version: "0.23.1"
---

# 技能开发

个人技能仓库里 Agent Skill 的创建、修改与验证。

Agent Skills 的格式约束不写死在本文件里：字段、目录约定、评估 schema 一律实时从 `https://agentskills.io/llms.txt` 及其页面拉取。规则优先级：以下仓库约定 > 官方文档 > 本文件其余内容。

## 子能力

| 子能力 | 产出 | 对应步骤 |
| --- | --- | --- |
| 写技能 | 技能目录下的 `SKILL.md`、`references/`、`scripts/`、`evals/` | 1 至 3 |
| 校验 | `skills-ref` 的校验结果 | 4 |
| 评估 | 触发评估与输出质量评估的结果，落在 `.scratch/` | 6、7 |
| 提交与部署 | 提交记录与用户层安装 | 8 |

每个子能力做不做由用户决定。有两处必须停下来等用户确认：写完到评估之前（第 5 步），评估到提交之前（第 8 步开头）。用户说先不跑评估时，写完与校验之后就停在第 5 步的总结。

## 调查边界

技能内容的来源只有用户给的输入，以及本仓库已固化的约定。

- 允许读取：本仓库内的文件，以及用户显式提供的文件与链接。
- 不作为技能内容的来源：`~/.agents/skills/` 等用户层技能目录、`~/.omp/` 与 `~/.claude/` 等 agent 运行时配置、其他仓库的技能与参考文件。项目 `AGENTS.md` 的规则只用来判断冲突，不从里面取材写进技能。
- 用户给的输入明确指向某个外部技能时，才读取该技能，并在产出里说明来源。
- 评估沙箱建在 `~/kie-ws/test/` 下，仓库内只保留 `.scratch/` 里的运行结果。一次评估或复现跑完、结果写进 `.scratch/`、结论汇报完之后，把本次用过的沙箱删掉（进回收站）；要留作物证时先在汇报里说明再留。

## 仓库约定

| 约定 | 内容 |
| --- | --- |
| 位置 | `skills/<分类>/<技能名>/SKILL.md` |
| 命名 | 目录名等于 frontmatter `name`，统一 `kie-` 前缀，只用小写字母、数字、连字符 |
| 分类 | 只用于组织源文件，按领域划分（`base/` 元技能与协作规则，其他按实际需要新增） |
| 版本 | `metadata.version` 用 semver，新技能从 `0.1.0` 起。影响 agent 行为的改动（description、规则、compatibility）bump minor，纯文字与格式修正 bump patch |
| 更新日志 | 仓库根 `CHANGELOG.md` 按 [Keep a Changelog 1.1.0](https://keepachangelog.com/zh-CN/1.1.0/) 维护。改动技能内容时与版本号同批记一段，写在整个文件最前面：段头 `## [<技能名> <版本>] - <YYYY-MM-DD>`，版本取该技能 frontmatter 的 `metadata.version`，日期取写条目当天；段内按 `Added`、`Changed`、`Deprecated`、`Removed`、`Fixed`、`Security` 分组，条目写人能读的一句话，说清这次变动对使用者意味着什么，不抄提交标题，也不记与技能行为无关的仓库改动。版本与段一一对应：版本号动了就记一段，patch 级的纯文字修正也记一句；技能创建记 `Added`，改名或合并时在条目里注明原技能名 |
| 评估 | 每个技能带 `evals/trigger-queries.json`（触发，官方 schema）与 `evals/evals.json`（输出质量，官方 schema），评估依据只来自用户输入与本仓库。新技能只写基础用例：触发用例 3 条正例加 3 条负例；质量用例 3 条，分别测主路径（依据齐全时产出物的位置与结构）、停在确认点（做完一个子能力就停下等用户）、依据缺失（按约定命名查找，找不到就问用户），没有子能力先后顺序的技能换成它自己的 3 个基础场景。每次会话都要加载的技能（如 kie-agent-rules）只写正例，不写负例。之后的用例只通过 kie-skill-fix 留下的回归用例增加 |
| 用户纠正 | 用户纠正技能行为后，先把纠正提炼成一条判据，写进对应步骤；与已有规则说的是同一件事时合并成一条，不另加。只有提炼不出判据、不写下来就会再踩的坑才进 `## Gotchas`，写成场景加动作，不抄对话原话 |

## 流程

### 1. 拉取官方文档

先读 `https://agentskills.io/llms.txt` 取页面索引，再按任务拉取需要的页面：

| 任务 | 页面 |
| --- | --- |
| 字段、目录结构、渐进式披露 | `specification.md` |
| 第一次做、最小示例 | `skill-creation/quickstart.md` |
| 内容设计、控制力度、Gotchas、输出模板 | `skill-creation/best-practices.md` |
| 触发准确性 | `skill-creation/optimizing-descriptions.md` |
| 输出质量评估 | `skill-creation/evaluating-skills.md` |
| 打包可执行脚本 | `skill-creation/using-scripts.md` |

页面名以索引里的当前列表为准。新建技能至少拉取 `specification.md` 与 `skill-creation/best-practices.md`，改动已有技能至少拉取 `specification.md`。不凭记忆写字段与约束。

### 2. 写 frontmatter

- `name` 与父目录名一致，1 至 64 字符，只能包含小写字母、数字、连字符，首尾不能是连字符，不能出现连续连字符。
- `description` 覆盖四块内容：做什么、何时用（含用户不会明说的场景）、边界、反例排除。不复述执行步骤，复述会让 agent 按 description 行事而不读正文。上限 1024 字符。
- 有明确环境依赖时写 `compatibility`，1 至 500 字符。
- `metadata` 用字符串键值对，写 `author` 与 `version`。

### 3. 写正文

正文只写 agent 不知道的东西：仓库约定、真实命令、决策条件、踩过的坑。内容来自真实执行过程：做过的任务顺序、用户的纠正、实际命令与输出格式。通用建议不进技能。

写法：

- 用子能力表写清技能负责什么、有哪些子能力、每个子能力产出什么。不写「先执行另一个技能再来」：子能力需要的依据不在手上时，写明按什么命名与落点查找，找不到就问用户。
- 说话方式、开工授权、提交与合入、删除文件这些规则归 `kie-agent-rules`，单个技能不再重复写。
- 本机取值（路径、版本号、账号、开关状态）不写死，写成怎么探测。
- 写完从读者角度读一遍：没参与过这次对话的人能看懂每一句。第一次出现的名词、参数、文件名要说明是什么。
- 正文控制在 500 行内，超出的细节移进 `references/`，正文写清什么时候读。`references/` 只放正文没有的内容，正文已有结论的不再重复。
- 产出物的模板（文档模板、报告模板、PR body 模板）一律放 `assets/`，`references/` 只放规则说明、命令清单这类参考资料。模板的写法要求放在模板末尾的「填写要求」里，正文只写按哪份模板来。

### 4. 校验

```bash
uvx --from skills-ref agentskills validate skills/<分类>/<技能名>
```

输出 `Valid skill: <目录>` 即通过。校验器只检查 frontmatter 与命名约束，内容质量由评估判定。

### 5. 确认与总结

进入评估之前先向用户总结这次改动，等用户同意再往下走：改了哪些文件、frontmatter 动了哪些字段、正文加了或改了哪些规则、版本号怎么动、更新日志记了哪一条、接下来准备跑哪几步评估。

- 用户提出修改就改完重新总结，不进入评估。
- 用户明确同意开始下一步之后，才启动第 6 步与第 7 步。
- 不代替用户判断「改动很小不用看」。

### 6. 触发评估

改了 `description` 就跑。用哪个 agent CLI 跑由用户定，先探测本机有哪些，再问用户：

```bash
python3 scripts/trigger_eval.py --list-agents
python3 scripts/trigger_eval.py <技能名> --agent <名字> [--runs 1] [--workers 12] [--cap 60] [--only 3,7]
```

正例累计触发率高于 0.5、负例低于 0.5 算通过，负例用 `--runs 3`。结果在 `.scratch/trigger-eval/<技能名>/<时间戳>/results.json`。用例写法、判定方式、退出码与常见坑见 [references/evaluation.md](references/evaluation.md)，跑之前先读。

### 7. 输出质量评估

改了正文就跑：

```bash
uv run scripts/quality_eval.py <技能名> --agent <名字> [--iteration 1] [--workers 4] [--cap 600] [--no-grade]
```

同一提示词分带技能、不带技能两组跑，`benchmark.json` 汇总两组的断言通过率与差值。带技能组通过率高于不带技能组、且自己读完 `outputs/` 没有具体意见时收工；否则改 `SKILL.md`，按第 5 步总结等确认，再用 `--iteration <N+1>` 重跑。用例写法、产物结构与常见坑见 [references/evaluation.md](references/evaluation.md)。

### 8. 提交与部署

评估走完、用户确认后才进入本步。有未通过的用例、证据不足的运行或评分失败时，先回报结果与下一轮准备改什么，等用户决定。

提交前核对本次改动已经记进仓库根 `CHANGELOG.md`：段头的技能名与该技能 frontmatter 的 `metadata.version` 一致，条目落在新版本段里，多技能一起改时每个技能各一段。

提交并推送后，部署用 `npx -y skills add Kielas520/kie-skills -g -y`。

## 可用脚本

脚本从自身路径向上找仓库根，只在 kie-skills 仓库内可用。

- **`scripts/trigger_eval.py`**：触发评估，第 6 步用。
- **`scripts/quality_eval.py`**：输出质量评估，第 7 步用。
- **`scripts/agent_cli.py`**：两者共用的 agent CLI 适配层。加新 agent 时在 `AGENTS` 里加一个子类，会话命令、技能在沙箱里的投放位置、加载判定信号、输出解析四处都要实现。

## Gotchas

- 技能改名要同步目录名、frontmatter `name`、其他技能里的引用、`evals/` 下的用例。仓库全是文本文件，没有工具兜底，改完逐处核对。
- 触发评估只说明技能被加载过，看不出 agent 有没有照着做；照没照着做要看输出质量评估。
