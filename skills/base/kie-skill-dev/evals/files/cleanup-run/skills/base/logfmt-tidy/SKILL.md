---
name: logfmt-tidy
description: 把 logfmt 日志按时间与级别整理，去掉完全重复的行并统计各级别条数。用户说「把这份 logfmt 日志整理一下」「日志去重并统计」时使用。不适用：JSON 结构日志的解析、日志采集配置的调整。
metadata:
  author: Kielas
  version: "0.2.0"
---

# logfmt 日志整理

## 步骤

1. 读入日志文件，按 `time=` 字段排序，再按 `level=` 分组。
2. 去掉完全重复的行，统计 `info`、`warn`、`error` 各级别条数。
3. 输出整理后的文件与一张统计表。
