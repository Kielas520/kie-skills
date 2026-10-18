# PR 482 修复实现

## 改动步骤

| 序号 | 关联问题 | 改哪里（文件 / 符号） | 怎么改 | 验收方式 |
| --- | --- | --- | --- | --- |
| 1 | 4 | `logfmt.py` / `parse` | `part.split("=")` 改成 `part.split("=", 1)` | `printf 'a= b=2\n' \| python3 logfmt.py /dev/stdin` 输出含 `"a": ""` |
| 2 | 1 | `logfmt.py` / `parse` | 空行判断合并成一行 | `python3 logfmt.py sample.log` 仍输出 4 条记录 |

## 测试范围

| 关联问题 | 测试内容 | 命令或观察方式 |
| --- | --- | --- |
| 4 | 没有值的字段不再抛异常 | 同上 |
| 1 | 空行仍被跳过，条数不变 | 同上 |
