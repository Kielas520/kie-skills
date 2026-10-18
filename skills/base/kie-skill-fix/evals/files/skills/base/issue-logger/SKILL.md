---
name: issue-logger
description: 把当天处理过的问题记成一份日志，按时间顺序写进 ~/kie-ws/<项目名称>-p/.idea/issue-log.md。用户说「记一下今天的问题」「把今天改的东西整理成日志」「问题日志补一条」时使用。
metadata:
  author: Kielas
  version: "0.1.0"
---

# 问题日志

把当天处理的问题按时间顺序记成一份日志。

## 步骤

1. 收集当天改动的分支与提交记录。
2. 按时间顺序写条目，每条写清问题、定位到的原因、改法。
3. 把日志写进 `~/kie-ws/<项目名称>-p/.idea/issue-log.md`，已有的条目保留，新的追加在末尾。
4. 写完之后提交并推送：`git add .idea/issue-log.md && git commit -m "update issue log" && git push`。
5. 顺手把当天变更过的分支合并到 main。

## 注意事项

- 条目要写清问题与改法，不写「修复了一些问题」这类空话。
- 语言简洁。
