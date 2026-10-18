---
name: kie-commit-pr
description: |
  为一次改动生成提交信息与 PR 文案，并在用户确认后执行提交与建 PR：提交信息按 Conventional Commits 推导 type、scope 与中文 description，写说明为什么改的 body 与 `Resolve` footer，破坏性变更标 `BREAKING CHANGE`；PR body 按分支类型套模板（需求单写背景、改动、验证、影响，缺陷单写问题、原因、改动、验证、影响），标题按 commit 首行格式写。当用户说「提交」「commit 一下」「把这些改动提交上去」「写个提交信息」「提交信息里带上单号」「分两次提交」「这几个文件提交掉」「发 PR」「提个 PR」「建 PR」「写一下 PR 描述」「PR body 起草一份」「分支做完了，交评审」「这条分支可以交出去了，先把 PR 描述写出来」时使用，即使没有说出 commit 或 PR 这几个词。不适用：新建分支与工作区（用 kie-git-worktree）；推送、合入、打 tag 与发布；PR 建好后的远端 CI 产物验收与测试报告评论（用 kie-pr-ci-test）；处理 PR 评审意见与回复（用 kie-pr-review-fix）；交付前的本地验收测试与测试报告（用 kie-dev-test）；Rust 的 fmt、clippy 与最小受影响测试集（用 kie-rust-gates）；只查看提交历史、解释某条提交、rebase 与 amend 的请求。
license: MIT
compatibility: 需要 git 与已登录的 gh CLI（建 PR 时用）。
metadata:
  author: Kielas
  version: "0.3.0"
---

# 提交与 PR 文案

一次改动的信息在两处落地：提交信息进历史，PR 标题与 body 进评审。两处都从同一份输入推导，先定改动范围再写，避免两处说法不一致。`<项目名称>` 与 `<任务>` 的取值见 `kie-agent-rules` 技能目录下的 `references/workspace.md`。

## 子能力

| 子能力 | 产出 | 何时做 |
| --- | --- | --- |
| 写提交信息 | 每次提交的信息草稿与要提交的文件清单 | 用户要求提交或写提交信息时 |
| 执行提交 | 提交记录 | 用户确认草稿与文件清单后 |
| 写 PR 文案 | PR 标题与 body 草稿 | 用户要求起草 PR 描述或建 PR 时 |
| 建 PR | PR 链接 | 用户确认标题与 body 后；是否建成 draft 由用户定，没说就先问 |

提交前要跑的格式化、lint 等流程按项目规则执行。

## 输入

| 输入 | 从哪取 |
| --- | --- |
| 改动范围 | `git status --short`、`git diff`、`git diff --cached`，或用户给的改动清单 |
| 分支类型与单号 | 分支名：`feat/m-{ID}/{梗概}`、`fix/f-{ID}/{梗概}`、`chore/{梗概}`、`hotfix/{梗概}`；或用户给出的单号 |
| 工单内容与链接 | 由用户给出，或从工单链接读取 |
| 测试结果 | 同一任务目录下的 `.idea/<任务>/test-report.md` |

单号、链接、测试结果都不编造，也不拿相近编号顶替：取不到就问用户。分支名与用户都没有给出单号时，先问用户是这次没有工单，还是漏给了单号；用户确认没有工单后，PR body 才写「无关联工单」，footer 才省略。找不到测试报告、或报告早于最近的代码改动时，告诉用户，问用户以什么为验证依据。

## 提交信息

```text
<type>(<scope>): <中文描述>

[body]

Resolve m-{ID}
```

示例：

```text
fix(parser): 空白行不再被解析成空记录

原先逐行解析时只跳过了完全为空的行，只含空格或制表符的行
被当作一条字段全空的记录写进输出。现在先去掉首尾空白再判空。

Resolve f-6925239029
```

| 部分 | 规则 |
| --- | --- |
| `type` | `feat`、`fix`、`perf`、`refactor`、`docs`、`test`、`ci`、`build`、`chore`、`style`、`revert`、`release` 之一。改行为用 `feat` 或 `fix`，只调整实现不动行为用 `refactor`，只改测试用 `test`，只改文档用 `docs` |
| `scope` | 写改动集中的模块、crate 或命令，跨多个模块时按主要改动写；`chore` 与 `release` 可省 |
| `description` | 用中文写改动后的结果，写清改了什么、范围在哪；首行不超过 72 列（一个汉字按 2 列计），不写工单号，不写「修改了…」这类过程描述 |
| `body` | 可选，说明为什么改：原先是什么状况、这次怎么解决、有无配套改动，每行不超过 80 列。问题描述与验证证据写在 PR 里，不写进 commit |
| `BREAKING CHANGE` | 破坏性变更在 `Resolve` 前加一行 `BREAKING CHANGE: <不兼容点，迁移方式>` |
| footer | 需求单 `Resolve m-{ID}`，缺陷单 `Resolve f-{ID}`；一次提交解决多个单写 `Resolve m-123, f-456`；没有工单的 `chore` / `docs` / `ci` 省略 footer |

description 与 body 用中文，identifier、文件路径、命令与工单号保留原名。不加 AI 署名 trailer。

## 拆分与提交

1. 改动跨多个主题时按主题拆成多次提交，一次提交一个主题，每次单独写信息。
2. 把每次提交的信息草稿与要提交的文件清单给用户看。只提交本次任务涉及的文件；工作区里有无关改动时先问用户，不一起带上。
3. 用户确认后执行 `git add <文件>` 与 `git commit`。多行信息写进文件再用 `git commit -F <文件>`；用 `-m` 拼接时 body 与 `BREAKING CHANGE` 要跟在首行后的空行之后，否则会被并进首行。

## PR 文案

按分支类型套模板，各段写法见模板末尾的「填写要求」：

| 分支 | 模板 | 段 |
| --- | --- | --- |
| `feat/`（需求单） | [assets/pr-body-feat-模板.md](assets/pr-body-feat-模板.md) | 背景、改动、验证、影响 |
| `fix/`（缺陷单） | [assets/pr-body-fix-模板.md](assets/pr-body-fix-模板.md) | 问题、原因、改动、验证、影响 |

PR 标题按 commit 首行格式写（`<type>(<scope>): <描述>`）；仓库用 squash 合并时，它就是 main 上的 commit 标题。标题与 commit 首行不一致时以用户确认的为准，不自行改写。

把标题与 body 草稿贴给用户确认，说明哪些内容来自工单、哪些来自测试报告。

## 交付

```text
━━━ 提交完成 ━━━
提交: {short sha} {首行}
文件: {n} 个
footer: {Resolve m-{ID} / 无}
```

```text
━━━ PR 已建立 ━━━
PR: {链接}
标题: {标题}
关联工单: {单号，无则写无}
验证段: {来自哪一份本地测试报告}
```

## 硬性约束

- 不用 `--amend` 改写已经推送的提交。

## Gotchas

- 单号最常见的越界是写进 `description`，单号只出现在 footer。
