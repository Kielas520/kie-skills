---
name: kie-skill-dev
description: 当任务要产出或改动技能目录里的文件时使用：新建技能、把已经跑通的流程沉淀成技能、改技能正文或 description、排查技能不触发或误触发、判断字段命名与目录该怎么写。用户说「写个 skill」「把这套流程固化成技能」「这个技能老是不触发，明明问的就是它管的范围」时适用，即使没提到 skill 这个词。讲解 Agent Skills 的设计动机与原理、介绍格式生态、安装升级移除别人已发布的技能、编写 AGENTS.md 与 README 等普通文档都不适用。
license: MIT
compatibility: 需要 uvx（skills-ref 校验器）与 omp CLI（触发评估）
metadata:
  author: Kielas
  version: "0.2.0"
---

# 技能开发

个人技能仓库里 Agent Skill 的创建、修改与验证。

Agent Skills 的格式约束不写死在本文件里：字段、目录约定、评估 schema、校验工具一律实时从 `https://agentskills.io/llms.txt` 及其页面拉取。本文件是工作流。规则优先级：以下仓库约定 > 官方文档 > 本文件其余内容。

用户反馈技能不触发、误触发或效果不好时先定位类型：触发问题走第 6 步，输出质量问题走第 7 步。

## 调查边界

技能内容的来源只有用户给的输入，以及本仓库与 `~/project/AGENTS.md` 引用范围内的约定。

- 允许读取：本仓库内的文件、用户显式提供的文件与链接、`~/project/AGENTS.md` 及其明确引用的开发约定。
- 不作为技能内容依据：`~/.agents/skills/` 等用户层技能目录、`~/.omp/` 等运行时配置、其他仓库的技能与参考文件。
- 需要隔离环境时，沙箱只建在本仓库范围内，不改动本仓库之外的任何路径。
- 用户给的输入明确指向某个外部技能时，才读取该技能，并在产出里说明来源。

## 仓库约定

| 约定 | 内容 |
| --- | --- |
| 位置 | `skills/<分类>/<技能名>/SKILL.md` |
| 命名 | 目录名等于 frontmatter `name`，统一 `kie-` 前缀，只用小写字母、数字、连字符 |
| 分类 | 只用于组织源文件，按领域划分（`base/` 元技能与协作规则，其他按实际需要新增） |
| 版本 | `metadata.version` 用 semver，新技能从 `0.1.0` 起。影响 agent 行为的改动（description、规则、compatibility）bump minor，纯文字与格式修正 bump patch |
| 评估 | 每个技能带 `evals/trigger-queries.json`。评估依据只来自用户输入与本仓库，用户层技能与其他仓库的参考文件不作为依据 |
| Gotchas | 正文保留 `## Gotchas` 段，用户每次纠正技能行为后把结论写回该段或对应步骤 |

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

页面名以第 1 步索引里的当前列表为准。新建技能至少拉取 `specification.md` 与 `skill-creation/best-practices.md`，改动已有技能至少拉取 `specification.md`。不凭记忆写字段与约束。

### 2. 写 frontmatter

- `name` 与父目录名一致，1 至 64 字符，只能包含小写字母、数字、连字符，首尾不能是连字符，不能出现连续连字符。
- `description` 覆盖四块内容：做什么、何时用（含用户不会明说的场景）、边界、反例排除。不复述执行步骤，复述会让 agent 按 description 行事而不读正文。上限 1024 字符。
- 有明确环境依赖时写 `compatibility`，1 至 500 字符。
- `metadata` 用字符串键值对，写 `author` 与 `version`。

### 3. 写正文

正文补 agent 不知道的东西：仓库约定、真实命令、踩过的坑、决策条件。前置条件、步骤、输出要求、验证方法按任务组织。正文控制在 500 行内，超出的细节移进 `references/`，正文写清何时读取。

技能内容来自真实执行过程：做过的任务顺序、用户的纠正、实际命令与输出格式。通用建议不进技能。

### 4. 校验

```bash
uvx --from skills-ref agentskills validate skills/<分类>/<技能名>
```

输出 `Valid skill: <目录>` 即通过。校验器只检查 frontmatter 与命名约束，内容质量由第 6 步的评估和第 7 步的真实使用判定。

### 5. 本地接入

技能位于分类目录下，`skill://<技能名>` 只在技能根目录下一层查找，分类层不参与扫描。建立链接后仓库内的会话才能读到：

```bash
ln -sfn ../../skills/<分类>/<技能名> .agents/skills/<技能名>
```

```bash
omp -p --mode json --no-session "读取 skill://<技能名> 的正文" | grep -o '"resolvedPath":"[^"]*"'
```

第二条命令输出技能目录内的路径说明接入成功；出现 `Unknown skill: <技能名>` 说明链接缺失或名字不一致。

### 6. 触发评估

改 `description` 必须重跑评估。

用例写在技能的 `evals/trigger-queries.json`，采用官方 schema `[{"query": "...", "should_trigger": true}]`，约 20 条。正例覆盖不同表述：明说与不明说、简短与带上下文、正式与口语。负例取关键词重合但任务不同的近似场景，无关查询测不出边界。

评估在仓库外的沙箱里运行。仓库内的会话会加载仓库所在目录树的 `AGENTS.md` 与仓库内容，带写权限的运行还能顺着 `resolvedPath` 改到技能源文件。

```bash
mkdir -p <沙箱>/skills <沙箱>/work
cp -r <仓库>/skills/<分类>/<技能名> <沙箱>/skills/
rm -rf <沙箱>/skills/<技能名>/evals
```

`evals/` 要删掉：它留在沙箱里，会话能读到用例清单，看出自己在被评估。沙箱目录名同样用中性名字，避免出现 `eval`、`测试` 之类的字样。

写 `<沙箱>/overlay.yml`：

```yaml
skills:
  customDirectories:
    - <沙箱>/skills
```

逐条查询无头运行：

```bash
cd <沙箱>/work
omp -p --mode json --no-session --config <沙箱>/overlay.yml --tools read,grep,glob "<查询>"
```

判定：输出里出现 `"resolvedPath":"<沙箱>/skills/<技能名>/SKILL.md"` 记为触发。没有出现该路径记为未触发，包括会话改用别的技能、或直接动手的情况。运行报错、超时、没有产生工具调用事件记为证据不足，不计为通过也不计为未触发。模型行为不确定，每条查询跑 3 次算触发率。正例触发率高于 0.5 通过，负例低于 0.5 通过。

不过关先改 `description` 再重跑。归纳失败查询代表的概念类别，不要堆查询里的原词。

### 7. 输出质量评估

技能触发正常但输出质量差时用。写 2 至 3 条真实测试提示词，带技能与不带技能各跑一遍做对比，用例 schema、评分方式与迭代循环按 `skill-creation/evaluating-skills.md` 执行。

基线运行复用第 6 步的沙箱：沙箱里不放技能副本，`overlay.yml` 的 `customDirectories` 指向空目录，`skill://<技能名>` 就会解析失败。两次运行各用独立的会话与工作目录，除技能有无之外的条件保持一致。`--tools` 按任务放开，需要产出文件时加上 `write`、`edit`。

### 8. 提交与部署

提交并推送后，部署用 `npx -y skills add Kielas520/kie-skills -g -y`。

## Gotchas

- 分类层不参与技能发现，全靠 `.agents/skills/` 符号链接接入。新增分类时同样要建链接。
- 技能改名要同步目录名、frontmatter `name`、`.agents/skills/` 链接、其他技能里的引用、`evals/trigger-queries.json`。仓库全是文本文件，没有工具兜底，改完逐处核对。
- 触发判定看会话有没有解析 `skill://<技能名>`。读取只说明查阅过，采纳与否看不出来。
- 负例是关键词重合的近似场景时，会话常会为了确认「这件事归不归它管」而加载本技能。description 要给明确的不适用清单，只写适用范围的正面描述拦不住这类加载。
- 触发评估的查询要写成沙箱里也成立的说法。依赖「这个仓库」这类上下文的查询，测到的是沙箱里缺内容。
- 沙箱运行必须限制工具，只留 `read`、`grep`、`glob`。技能一旦被读取，会话就看到技能的真实路径，带写权限时会顺着路径改技能源文件。
- 官方文档会演进。字段上限、目录约定以拉取到的 `specification.md` 为准，本文件的数字只是当前值。
- 评估材料只来自用户输入与本仓库。用户层技能目录与运行时配置不属于评估范围，也不作为改写目标。
- 触发评估的沙箱只负责放置被测技能的副本，不用来屏蔽或改动本仓库之外的技能。
- 用户提供的输入指向哪里就只看哪里，不带入其他仓库的设计习惯当作标准。
