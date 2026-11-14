# AGENTS.md

demo 仓库：日志解析与格式化的小工具。`crates/logfmt` 是库，`crates/cli` 是命令行入口。

## Build Commands

```bash
cargo build --workspace                              # 全部 crate
cargo test --all-features --workspace                # 全部测试
cargo test -p logfmt                                 # 单个 crate
cargo run -q -p cli -- sample.log                    # 跑命令行入口
```

## Pre-Push Verification (Required)

推送前依次执行，任何一步失败都要修完再推：

```bash
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features --workspace
RUSTDOCFLAGS="-Dwarnings" cargo doc --no-deps --all-features
```

## 约定

- 库的新增对外接口要在 `README.md` 的用法示例里补一行，并在 `CHANGELOG.md` 记一条。
- 单元测试写在各 crate 的 `tests/` 下，用例名以 `parse_`、`render_`、`export_` 开头。
