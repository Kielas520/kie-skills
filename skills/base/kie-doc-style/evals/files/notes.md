# release notes v0.3.0

## new features

- 对导出功能进行了优化，实现了对 Parquet 格式的支持；导出速度非常快。
- 新增 `demo-cli export --format` 参数,默认值为 `csv`。

## bug fixes

- 修复了空白行会被解析成空记录的问题。
