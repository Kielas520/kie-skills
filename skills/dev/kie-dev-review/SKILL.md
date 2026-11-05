---
name: kie-dev-review
description: 评审自己的本地分支或他人的 PR，核对代码与需求并输出评审建议。当用户说「评审我的分支」「自查代码」「审一下这个 PR」「看看这个 PR 有什么问题」时使用。不负责发送评论，也不处理收到的评审意见（用 kie-dev-fix）。
license: MIT
compatibility: 需要 git；评审 GitHub PR 时需要已登录的 gh CLI 与仓库读取权限。
metadata:
  author: Kielas
  version: "0.2.0"
---

# 代码评审

评审自己的本地分支或他人的 PR，产出可供用户查看和处理的评审建议。发送 PR 评论由 `kie-commit-pr` 负责。

## 子能力

| 子能力 | 产出 |
| --- | --- |
| 评审本地分支 | `<工作目录>/.tmp/comment/comment-review-n.md`，只写评审建议 |
| 评审他人的 PR | 同一位置的 `comment-review-n.md`，含 PR body 和内联评论 |

`<工作目录>` 是 `~/kie-ws/<仓库名>/<name>/`，分支代码位于其下的 `branch_source/` 或工单编号目录。`n` 在该项工作的 `.tmp/comment/` 中递增：检查已有 `comment-review-n.md` 与 `comment-fix-n.md`，取其中最大编号加一；没有文件时从 1 开始。不得覆盖已有文件。

## 评审

1. 确定评审对象及基准。本地分支查看当前分支、工作区状态、与目标基准的差异以及未提交改动；基准无法从上下文或仓库确定时询问用户。PR 取得仓库、编号、标题、body、base、head SHA、diff、已有 review 和未解决 threads，避免重复提出已有意见；所需只读命令见 [references/github-pr-commands.md](references/github-pr-commands.md)。
2. 读取目标仓库根目录的 `AGENTS.md`（存在时），以及需求、设计和相关实现。PR 评审须核对与 head SHA 对应的代码；不要覆盖已有工作区或切换有未提交改动的工作区。无法安全获取对应代码时说明原因并询问用户。
3. 核对需求一致性、正确性、边界条件、错误处理、并发与资源、安全、性能、测试和文档。只报告有具体代码依据及实际影响的问题；需要澄清的问题单独列出。是否执行测试由本次用户授权决定。
4. 按 [assets/comment-review.md](assets/comment-review.md) 写文件：本地分支仅写建议；PR 写明确的 PR body 与可定位的内联评论。每条建议写清位置、依据、影响和修改建议。没有发现问题时明确写出，并说明检查范围和剩余风险。
5. 交付文件路径、评审对象和发现的问题；说明是否读取了 `AGENTS.md`。不发送评论。
