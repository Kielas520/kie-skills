# kie-skills

个人日常开发使用的一套 Agent Skills，面向注重代码质量与软件架构设计的人。全部技能遵守同一条主张：**人是决策者，Agent 是执行者**。

现在的 Agent 都很喜欢把一件事自己做完，从修改文件一路做到提交推送，业界也在强调这种自主能力。模型能力越强，「谁来决定、做到哪一步」越需要提前写下来。这套技能把这些约定固化成文本，让 Agent 在动手之前先把边界讲清楚。

## 为什么要约束 Agent

根源在 LLM 的指令遵循倾向：外部输入进来，倾向直接执行，跳过判断环节。问题集中在五个环节：

| 环节 | 表现 |
| --- | --- |
| 越权执行 | 没经要求就 `git commit`、`git push`，询问类的请求被当成改动指令执行 |
| 跳过决策 | 需求没调研就给出实现，方案还没定稿就开始写代码 |
| 质量门禁靠自觉 | 格式化、lint、测试、验收标准全凭 Agent 记得执行 |
| 产出物散乱 | 方案、设计、测试报告、临时脚本落在各处，事后找不到 |
| 经验不沉淀 | 纠正只留在单次会话里，换一个项目重新出现 |

## 设计原则

- **指令分型**：咨询类请求只分析、不改文件，改动类请求只改文件。授权以明确的改动要求为准，讨论与询问都不构成授权。
- **不可逆动作等授权**：提交、推送、合并、发布评论、删除文件都在用户授权后执行，技能只列出命令与执行顺序。
- **先方案再实现**：调研出全部候选方案交用户拍板，方案定稿后写设计文档，设计确认后生成计划，再逐条实现到可运行。
- **质量门禁前置**：提交前跑格式化与自动修复，推送前按影响范围选出最小测试集，验收标准写成测试报告。
- **落点固定**：源仓库、工作区、任务文档各有一处固定位置，文档与临时产物不会散在项目目录里。
- **技能可评估**：每个技能带正负例触发查询与输出质量用例，改动之后先跑评估，再提交与部署。

## 技能

| 分类 | 技能 | 用途 |
| --- | --- | --- |
| `base/` | [`kie-agent-rules`](skills/base/kie-agent-rules) | 协作准则：回答语言、咨询与改动的分型、提交与回退的边界、工作空间落点、文件删除方式 |
| | [`kie-doc-style`](skills/base/kie-doc-style) | 文档文风的检查与生成：中英文规范、去冗余、对外文档的读者边界 |
| | [`kie-env-setup`](skills/base/kie-env-setup) | 本机环境的体检与补齐：工作空间、仓库落位、工具链、系统与网络 |
| | [`kie-skill-dev`](skills/base/kie-skill-dev) | 技能全流程开发：新建、改写、字段与目录约定、触发评估与输出质量评估 |
| | [`kie-skill-fix`](skills/base/kie-skill-fix) | 已装技能行为异常的排查与修复：越界、该做没做、输出走样、不触发或误触发 |
| `dev/` | [`kie-dev-solution`](skills/dev/kie-dev-solution) | 开工前的调研与多方案选型，产出选型文档交用户拍板 |
| | [`kie-dev-design`](skills/dev/kie-dev-design) | 方案选定后写技术设计文档，含数据链路图与具体设计 |
| | [`kie-dev-execute`](skills/dev/kie-dev-execute) | 按设计文档生成计划，逐条实现到可运行，先写测试再实现 |
| | [`kie-dev-test`](skills/dev/kie-dev-test) | 推送前的本地验收测试与测试报告，缺陷单附对照实验 |
| `git/` | [`kie-git-worktree`](skills/git/kie-git-worktree) | 为单个任务新建独立工作区与分支，分支名、落位与基线先确认 |
| | [`kie-commit-pr`](skills/git/kie-commit-pr) | 生成提交信息与 PR 正文，用户确认后执行提交与建 PR |
| | [`kie-pr-review-fix`](skills/git/kie-pr-review-fix) | 处理 PR 评审意见到推送更新并逐条回复 |
| | [`kie-pr-review`](skills/git/kie-pr-review) | 作为 reviewer 评审别人的 PR：评审报告、评论草稿、逐条确认后一次发送 |
| | [`kie-pr-ci-test`](skills/git/kie-pr-ci-test) | PR 的 CI 跑完后验收远端产物，出测试报告并回写 PR |
| `languages/` | [`kie-python-style`](skills/languages/kie-python-style) | Python 约定：uv、类型注解、pathlib、rich、loguru |
| | [`kie-rust-gates`](skills/languages/kie-rust-gates) | Rust 门禁：提交前 fmt 与 clippy，推送前最小受影响测试集 |

## 安装

全局安装，所有项目可用：

```bash
npx -y skills add Kielas520/kie-skills -g -y
```

只装其中一个：

```bash
npx -y skills add Kielas520/kie-skills -s kie-agent-rules -g -y
```

只列出仓库里的技能，不安装：

```bash
npx -y skills add Kielas520/kie-skills -l
```

更新已安装的技能：

```bash
npx skills update -g
```

`-g` 安装到用户目录，`-y` 跳过全部确认。CLI 会探测本机已安装的 Agent，按各自的技能目录建立链接。

## 约定

- 技能格式遵循 [agentskills.io](https://agentskills.io) 规范，统一 `kie-` 前缀，按 `skills/<分类>/<技能名>/` 组织，分类只用于整理源文件，不参与技能发现。
- 触发靠 frontmatter 的 `description` 匹配，每个技能带 `evals/trigger-queries.json`（正负例触发查询）与 `evals/evals.json`（输出质量用例）。
- 新增或修改技能走 `kie-skill-dev` 的流程：字段与目录约定、校验、两道确认、触发评估与输出质量评估、提交与部署。评估脚本在 `skills/base/kie-skill-dev/scripts/`，运行记录落在 `.scratch/`。
- 评估时脚本把技能复制进沙箱，并按选定的 agent 放到它能读到的位置，仓库里不需要建技能软链。
