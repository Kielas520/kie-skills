# 评审意见

- PR：https://github.com/example/demo/pull/42
- head SHA：0123456789abcdef0123456789abcdef01234567

## PR body

````
发现一处空行处理问题，请修复后补充测试。
````

## 内联评论

### 1 空行被当作记录

- 路径：src/parser.py
- 行号：12

````
只含空白的行仍会生成空记录，建议去掉首尾空白后再判断。
````
