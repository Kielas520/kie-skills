---
name: my-eval
description: 用无头会话跑技能评估。用户说「跑一下评估」「重跑这些用例」「换一组查询试试」时使用。
metadata:
  author: me
  version: "0.1.0"
---

# 我的评估

评估会话固定用 omp CLI 起，提示词从 stdin 读入：

```bash
omp -p --mode json --no-session --max-time 300
```

结果写到当前目录的 `results.json`。
