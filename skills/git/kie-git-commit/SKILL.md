---
name: kie-git-commit
description: |
  只在生成提交信息与执行 git commit 这一步时加载：按 Conventional Commits 从工作区改动与工单号推导 type、scope 与中文 description，写说明为什么改的 body 与 `Resolve` footer，破坏性变更在 footer 前标 `BREAKING CHANGE`，信息草稿交用户确认后才执行提交。当用户说「提交」「commit 一下」「把这些改动提交上去」「写个提交信息」「提交信息里带上单号」「分两次提交」「这几个文件提交掉」「这次改动该写什么 type」时使用，即使没有说出 commit 这个词。本技能唯一的产出是提交信息加一次本地提交；为把分支交到远端、跨分支同步、打 tag、发版或建 PR 准备命令与步骤时不要加载它，那些走 kie-agent-rules 与 kie-pr-start；新建分支与工作区用 kie-git-worktree；交付前的本地验收测试与测试报告用 kie-dev-test；Rust 的 fmt、clippy 与最小测试集用 kie-rust-gates；只查看提交历史、解释某条提交、rebase 与 amend 也不适用，直接回答。
license: MIT
compatibility: 需要 git。
metadata:
  author: Kielas
  version: "0.1.0"
---

# 提交

按规范的提交信息格式提交本次改动，description 与 body 用中文。提交信息先给用户看，确认后才执行提交动作。

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
| footer | Story `Resolve m-{ID}`，Bug `Resolve f-{ID}`；一次提交解决多个单写 `Resolve m-123, f-456`；没有工单的 `chore` / `docs` / `ci` 省略 footer |

不加 AI 署名 trailer。

## 判定 type 与 scope

1. 读工作区状态与改动内容（`git status --short`、`git diff`、`git diff --cached`），按改动性质选 type：改行为用 `feat` 或 `fix`，只调整实现不动行为用 `refactor`，只改测试用 `test`，只改文档用 `docs`。
2. scope 取改动集中的模块、crate 或命令名，跨多个模块时按主要改动写。
3. description 用中文一句话写改动后的结果，写清改了什么、范围在哪，不写过程描述与工单号。
4. body 写为什么改：原先的状况与问题、这次改动解决什么；含配套改动（新增加载入口、交给 CI 校验这类）一并写明。
5. 单号取用户给出的，或从分支名里读（分支名格式见 `kie-git-worktree`：`feat/m-{ID}/{梗概}`、`fix/f-{ID}/{梗概}`）；单号缺失时向用户询问，不编造。

## 拆分与提交

1. 改动跨多个主题时按主题拆成多次提交，一次提交一个主题，每次单独写信息。
2. 把每次提交的信息草稿与要提交的文件清单给用户看。
3. 用户确认后执行 `git add <文件>` 与 `git commit`，只提交本次任务涉及的文件，不把无关的工作区改动一起带上。
4. 推送不在本技能范围，用户要求推送时按 `kie-agent-rules` 的提交推送约定执行。

## 交付

```text
━━━ 提交完成 ━━━
提交: {short sha} {首行}
文件: {n} 个
footer: {Resolve m-{ID} / 无}
下一步: {需要推送时按用户要求执行 / 无}
```

## 硬性约束

- 不擅自执行 `git add`、`git commit`、`git push`：信息草稿先给用户确认。
- 不用 `--amend` 改写已经推送的提交，不用 rebase 改写历史。
- 提交信息里的工单号不编造，取不到就问用户。

## Gotchas

- 工单号写进 `description` 是超出规范最常见的一处，单号只出现在 footer。
- description 与 body 用中文，identifier、文件路径、命令与工单号保留原名。
- 多行 `body` 与 `BREAKING CHANGE` 要跟在首行的空行之后，用 `-m` 拼接时注意空行位置，否则会被并进首行。
- 用户只说「提交一下」时按当前工作区改动提交，把无关改动一起带上之前先问用户。
- 仓库有语言专属门禁时先过门禁再提交，Rust 项目走 `kie-rust-gates` 的 fmt 与 clippy。
- `chore` 与 `release` 的 scope 可以省，其余 type 尽量写清 scope，便于按模块回溯。
