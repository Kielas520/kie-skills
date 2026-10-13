---
name: kie-commit-pr
description: |
  为一次改动生成提交信息与 PR 文案，并在用户确认后执行提交与建 PR：提交信息按 Conventional Commits 推导 type、scope 与中文 description，写说明为什么改的 body 与 `Resolve` footer，破坏性变更标 `BREAKING CHANGE`；PR body 按分支类型套模板（需求单写背景、改动、验证、影响，缺陷单写问题、原因、改动、验证、影响），标题按 commit 首行格式写。当用户说「提交」「commit 一下」「把这些改动提交上去」「写个提交信息」「提交信息里带上单号」「分两次提交」「这几个文件提交掉」「发 PR」「提个 PR」「建 PR」「写一下 PR 描述」「PR body 起草一份」「分支做完了，交评审」「这条分支可以交出去了，先把 PR 描述写出来」时使用，即使没有说出 commit 或 PR 这几个词。不适用：新建分支与工作区（用 kie-git-worktree）；本技能只覆盖提交与建 PR 两个动作，其余 git、发布与合入动作按 kie-agent-rules 的约定执行；PR 建好后的远端 CI 产物验收与测试报告评论（用 kie-pr-ci-test）；处理 PR 评审意见与回复（用 kie-pr-review-fix）；交付前的本地验收测试与测试报告（用 kie-dev-test）；Rust 的 fmt、clippy 与最小受影响测试集（用 kie-rust-gates）；只查看提交历史、解释某条提交、rebase 与 amend 的请求。
license: MIT
compatibility: 需要 git 与已登录的 gh CLI（建 PR 时用）。
metadata:
  author: Kielas
  version: "0.1.0"
---

# 提交与 PR 文案

一次改动的信息在两处落地：提交信息进历史，PR body 与标题进评审。两处都从同一份输入推导，先出草稿，用户确认后才执行动作。推送与合并不在本技能范围，按 `kie-agent-rules` 的提交与回退约定执行。

## 输入

| 输入 | 从哪取 |
| --- | --- |
| 改动范围 | `git status --short`、`git diff`、`git diff --cached`，或用户给的改动清单 |
| 分支类型与单号 | 分支名（格式见 `kie-git-worktree`：`feat/m-{ID}/{梗概}`、`fix/f-{ID}/{梗概}`、`chore/{梗概}`），或用户给出的单号 |
| 工单内容与验收标准 | 由用户给出，或从工单链接读取；取不到就问用户要 |
| 本地测试报告 | `~/kie-ws/<项目名称>-p/.idea/<任务>/test-report.md`（由 `kie-dev-test` 产出），作为 PR 验证段的来源 |

单号缺失时向用户询问，不编造，也不拿相近编号顶替。

## 提交信息格式

```text
<type>(<scope>): <中文描述>

[body]

Resolve m-{ID}
```

示例：

```text
feat(skills): 内部 Skills 增加 Claude Code 加载入口与提交前自审清单

Claude Code 不读 .agents/skills/，此前只能靠 AGENTS.md 的路径指引手工
读取内部约定；补 .claude/skills/ 相对符号链接后可按 Skill 机制加载。
同时新增提交前自审清单，并把三处一致性交给 CI 校验。

Resolve m-7112014324
```

| 部分 | 规则 |
| --- | --- |
| `type` | `feat`、`fix`、`perf`、`refactor`、`docs`、`test`、`ci`、`build`、`chore`、`style`、`revert`、`release` 之一 |
| `scope` | 写模块 / crate / 命令；`chore` 与 `release` 可省 |
| `description` | 用中文写改动后的结果，首行不超过 72 列（一个汉字按 2 列计），不写工单号，不写「修改了…」这类过程描述 |
| `body` | 可选，说明为什么改：原先是什么状况、这次怎么解决、有无配套改动，每行不超过 80 列。问题描述与验证证据写在 PR 里，不写进 commit |
| `BREAKING CHANGE` | 破坏性变更在 `Resolve` 前加一行 `BREAKING CHANGE: <不兼容点，迁移方式>` |
| footer | 需求单 `Resolve m-{ID}`，缺陷单 `Resolve f-{ID}`；一次提交解决多个单写 `Resolve m-123, f-456`；没有工单的 `chore` / `docs` / `ci` 省略 footer |

不加 AI 署名 trailer。

## 判定 type 与 scope

1. 读改动范围，按改动性质选 type：改行为用 `feat` 或 `fix`，只调整实现不动行为用 `refactor`，只改测试用 `test`，只改文档用 `docs`。
2. scope 取改动集中的模块、crate 或命令名，跨多个模块时按主要改动写。
3. description 用中文一句话写改动后的结果，写清改了什么、范围在哪，不写过程描述与工单号。
4. body 写为什么改：原先的状况与问题、这次改动解决什么；含配套改动（新增加载入口、交给 CI 校验这类）一并写明。
5. 单号取用户给出的，或从输入里的分支名读出；单号缺失时询问用户。

## 拆分与提交

1. 改动跨多个主题时按主题拆成多次提交，一次提交一个主题，每次单独写信息。
2. 把每次提交的信息草稿与要提交的文件清单给用户看。
3. 用户确认后执行 `git add <文件>` 与 `git commit`，只提交本次任务涉及的文件，不把无关的工作区改动一起带上。
4. 提交完再进入 PR 文案，或按用户要求只做提交。

## PR body 结构

按分支类型套模板：`feat/` 分支用 [assets/pr-body-feat-模板.md](assets/pr-body-feat-模板.md)，`fix/` 分支用 [assets/pr-body-fix-模板.md](assets/pr-body-fix-模板.md)。

| 分支 | 段 | footer |
| --- | --- | --- |
| feat（需求单） | 背景、改动、验证、影响 | `Resolve m-{ID}` |
| fix（缺陷单） | 问题、原因、改动、验证、影响 | `Resolve f-{ID}` |

- 背景 / 问题：先写关联工作项链接（无工单写「无关联工单」）；需求写需求背景与设计文档路径，缺陷写现象、触发条件、出错信息原文、设备与固件版本，截图、日志、dump 放这一段。
- 原因（只有 fix 有这一段）：写到根因与机制；没定位就写「根因未定位，本次规避：…」。
- 改动：行为上变了什么。需求单写新增的行为与接口，含资源名、命令、参数、默认值。
- 验证：同条件下改前结果与改后结果、测试名和数量、实机 SN 与固件版本、CI 链接；本地测试阶段引用最后一次本地测试报告的结果，没有远端结果就不写 CI 部分。
- 影响：需回退的临时缓解、兼容性、回滚方式；需求单再写配套升级的组件和版本、默认行为变化。没有内容就删掉这一段。
- 影响段的末行写是否修改云文档已有设计的判断；需求单另附方案文档链接，缺陷单只在涉及架构缺陷修复时附，复杂度不高时写「不适用」并说明原因。
- footer：需求单 `Resolve m-{ID}`，缺陷单 `Resolve f-{ID}`；一次解决多个单写 `Resolve m-123, f-456`；没有工单的 `chore` / `docs` / `ci` 省略 footer。

其余规则：

- PR 标题按 commit 首行格式写（`<type>(<scope>): <描述>`，scope 写模块或命令，只有 `chore` 与 `release` 可省），squash 后它就是 main 上的 commit 标题；项目另有约定时按项目约定。
- 一个 PR 一个工单一个主题。
- 评审修复的往来与回复留在评论里，不写进描述；代码变化导致改动、影响失实时同步更新，描述里只留改动本身。
- 涉及对外可见变更的 PR，在同一个 PR 里同步修改 `public/CHANGELOG.md`。
- 关联工单链接与方案文档链接由用户给出，或从工单与项目知识库读取；取不到就问用户要，不编造链接。
- 改动段按实际改动写，不复制工单原文当作变更内容。

## 起草与建 PR

1. 把 body 与标题草稿贴给用户确认，说明哪些内容来自工单、哪些来自测试报告。
2. 用户确认后建立 PR。是否建成 draft 由用户定，用户没说就先问一句。
3. 建 PR 之后把链接与后续步骤告诉用户：CI 跑完的远端验收走 `kie-pr-ci-test`，评审意见的处理走 `kie-pr-review-fix`。

## 交付

```text
━━━ 提交完成 ━━━
提交: {short sha} {首行}
文件: {n} 个
footer: {Resolve m-{ID} / 无}
下一步: {进入 PR 文案 / 需要推送时按用户要求执行 / 无}
```

```text
━━━ PR 已建立 ━━━
PR: {链接}
标题: {标题}
关联工单: {单号，无则写无}
验证段: {来自哪一份本地测试报告}
下一步: CI 跑完后走 kie-pr-ci-test 做远端产物验收
```

## 硬性约束

- 不擅自执行 `git add`、`git commit`、`git push`：提交信息草稿与文件清单先给用户看。
- 不擅自发起 PR：body 与标题先给用户看，用户确认之前不执行建 PR 的命令。
- 不用 `--amend` 改写已经推送的提交，不用 rebase 改写历史。
- 提交信息与 PR 里的工单号、链接、测试结论都不编造，取不到就问用户。

## Gotchas

- 推送、合并、打 tag 与发版都不擅自执行：用户没有明确要求时只把要跑的命令与顺序列出来，等用户来跑。
- 提交信息与 PR body 的输入是同一份，改动范围先定下来再写两处，避免两处说法不一致。
- 工单号写进 `description` 是超出规范最常见的一处，单号只出现在 footer。
- description 与 body 用中文，identifier、文件路径、命令与工单号保留原名。
- 多行 `body` 与 `BREAKING CHANGE` 要跟在首行的空行之后，用 `-m` 拼接时注意空行位置，否则会被并进首行。
- 用户只说「提交一下」时按当前工作区改动提交，把无关改动一起带上之前先问用户。
- 缺陷单只在涉及架构缺陷修复时附方案文档链接，复杂度不高时不硬凑。
- 验证段引用 `kie-dev-test` 的最新报告，报告失效或还没写时要提醒用户先补测试。
- 远端测试结果由 `kie-pr-ci-test` 之后追加进验证段，起草第一版时不预留空段。
- 标题与 commit 首行不一致时以用户确认为准，不自行改写标题。
- 仓库有语言专属门禁时先过门禁再提交，Rust 项目走 `kie-rust-gates` 的 fmt 与 clippy。
