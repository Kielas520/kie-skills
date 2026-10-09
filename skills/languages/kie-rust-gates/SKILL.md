---
name: kie-rust-gates
description: |
  Rust 项目里提交与推送前的质量门禁：先判定本次改动是否涉及 Rust（相对 origin/main 的分支累计 diff 加工作区改动），commit 前跑 `cargo fmt --all` 与 `cargo clippy --fix --all-targets --all-features --allow-dirty --allow-staged -- -D warnings`，push 前按影响范围选出最小受影响测试集并说明选择依据。当用户在含 Cargo.toml 的项目里执行 add、commit、push，或说「提交前检查一遍」「推送前要测什么」「这次改动涉及哪些测试要跑」「只测本分支相对 main 的改动」「最小化测试范围」「别跑全量」、提到修 CI 的 clippy 与 fmt 报错时使用，即使用户没有提到检查或测试。不适用：非 Rust 项目；改动不影响 Rust 构建与测试（纯文档、纯资源）；按工单验收标准做的交付测试与测试报告（用 kie-dev-test）；PR 上 CI 与远端产物的验收（用 kie-pr-ci-test）；Rust 代码写法风格以外的语言约定（Python 用 kie-python-style）；与门禁无关的版本控制与发布话题（Cargo.lock 是否入库、commit message 写法、发布到 crates.io、依赖树检查）。
license: MIT
compatibility: 需要 cargo 工具链（含 rustfmt、clippy 组件，缺时用 `rustup component add rustfmt clippy` 安装）与 git。
metadata:
  author: Kielas
  version: "0.1.0"
---

# Rust 提交与推送门禁

存在 `Cargo.toml` 的项目在提交与推送前的硬性检查顺序。fmt 与 clippy 命令原样执行；测试保留 `--all-features`，按影响范围选择包、target 与用例，不默认跑全量。

工单驱动的验收测试与测试报告归 `kie-dev-test`，本技能只管机械门禁命令与测试范围选择，两者都要过。

## 第 0 步：判定本次改动是否涉及 Rust

commit 前看工作区状态，包含已暂存、未暂存与未跟踪文件：

```bash
git status --porcelain --untracked-files=all
```

push 前无论工作区是否干净，都要先确定分支累计变更：

1. 优先用 `origin/main`，不存在时用本地 `main`，记录所用引用与 SHA。引用已知过期时先更新。两者都不存在或找不到共同祖先时停下问用户要基线，不用当前分支的 upstream 或 `HEAD^` 代替。
2. 用 `git merge-base <main 引用> HEAD` 得到 `base`，再用 `git diff --name-status --find-renames <base> HEAD` 与对应 diff 检查分支全部变更，不只看最后一次提交或尚未推送的提交。
3. 把工作区状态里的改动路径合并进来，重命名同时看新旧路径，删除也算变更。未提交改动不能作为待推送 HEAD 已通过测试的证据，push 前必须确认测试对应当前待推送的代码状态。

在范围内筛选：

- `*.rs`（任意路径：`src/`、`build.rs`、`examples/`、`tests/`、`benches/`）→ Rust 源码改动
- `Cargo.toml`、`Cargo.lock`（任意层级，workspace 子 crate 也算）→ 清单与依赖改动

测试夹具、快照、生成器输入、`.cargo/`、工具链与构建配置虽然不是 `.rs`，只要影响 Rust 构建或测试也要纳入。确认整个范围都不影响 Rust（纯文档等）时才跳过全部门禁。

## 门禁

### commit 前：fmt 与 clippy --fix

改动含 `*.rs` 源码时执行：

```bash
cargo fmt --all
cargo clippy --fix --all-targets --all-features --allow-dirty --allow-staged -- -D warnings
```

只改了 Cargo.toml、Cargo.lock 而没有源码改动时，fmt 与 clippy 没有检查对象，直接跳过。

### push 前：最小受影响测试集

以第 0 步的分支累计 diff 为输入，选出能覆盖行为变化的最小测试集。main 上已通过测试只说明基线通过，不代表未修改的调用方不会回归。

1. 从变更的函数、类型、接口与数据入手，检查调用方与已有测试。用仓库已有的测试映射或可靠的影响分析工具，不能只按测试文件是否修改或名称是否相似来筛。
2. 列出「变更 → 受影响行为与调用方 → 测试」的对应关系，包含新增或修改的测试、覆盖变更行为的已有单元测试、集成测试与相关 doctest。共享测试工具、夹具与快照的变更覆盖全部使用者。
3. 按下表选择范围，每次扩大只到足以覆盖影响的层级，不因一个局部改动默认跑整个 workspace。
4. 执行前说明基线、选择依据与命令。用名称筛选时先用相同参数加 `-- --list` 核对匹配到的用例。执行后检查实际运行数量与结果，`0 tests`、全部 ignored、只有编译成功都不算测试通过。确实没有测试时报告覆盖缺口，不宣称门禁通过。

| 影响范围 | 测试选择 |
| --- | --- |
| 行为和调用方都能精确定位 | 对应 target 内的具体用例或模块筛选 |
| 无法可靠缩小到用例，但能定位 target | 该 target 全部测试 |
| crate 内共享逻辑，无法可靠缩小到 target | 该 crate 全部测试 |
| 公共 API、共享类型或跨 crate 行为变化 | 变更 crate 及受影响的直接与传递依赖方测试，不只测定义所在 crate |
| Cargo 清单、依赖、feature、构建脚本或配置变化 | 至少执行受影响包及依赖方的包级测试，不用用例名筛选；无法可靠界定包集合时执行 workspace 全量测试 |
| 影响遍及 workspace，或分析后仍无法界定边界 | workspace 全量测试，并说明回退原因 |

命令模板，替换占位符，只执行选中的命令。包级默认测试包含 doctest；指定 `--lib` 或 `--test` 时要单独补相关 doctest：

```bash
cargo test -p <package> --all-features --lib <full-test-name> -- --exact
cargo test -p <package> --all-features --lib <module-filter>
cargo test -p <package> --all-features --test <target>
cargo test -p <package> --all-features --doc
cargo test -p <package> --all-features
cargo test --workspace --all-features
```

二进制等 target 用对应的 `--bin`、`--example` 选项，多个包可以重复指定 `-p`。只有仓库明确要求全量测试、用户明确要求，或满足上表回退条件时才跑全量。

## 执行规则

1. 先做第 0 步判定。不影响 Rust 时跳过门禁；否则按 fmt → clippy --fix →（用户要求 commit）→ 受影响测试 →（用户要求 push）的顺序执行，被条件跳过的步骤直接略过。
2. `clippy --fix` 会自动改代码，改完重新过目 diff 再提交，确认它没有把语义改坏。
3. 任何一步失败就停下，修复后从头重跑该步，不带病提交；修不了就把报错原样汇报给用户。
4. 测试通过、用户明确要求之后才实际执行 commit 与 push。

## Gotchas

- `--allow-dirty --allow-staged` 是必需的：提交前工作区必然有未提交改动，不加会直接报错退出。
- `-D warnings` 让 warning 也当失败，这是有意的，不为了通过而去掉。
- 不把「main 已通过」当作排除调用方测试的依据，也不把 Cargo 的名称筛选当作自动的变更影响分析。
- push 范围始终包含相对 main 的分支累计变更。工作区只有文档改动或完全干净，不代表本分支没有 Rust 改动。
- `git status --porcelain --untracked-files=all` 用于补充未提交与未跟踪文件，不能代替分支 diff；不要只用 `git diff --cached`，它会漏掉未暂存与未跟踪文件。
- 全量测试不是默认策略。需要回退到更宽范围时说明具体影响或缺失的证据，不为了省时间取消已确定必需的测试。
- 多语言仓库里只覆盖 Cargo 部分，但其他语言或资源的改动若影响 Rust，也要选相关的 Rust 测试。不削弱仓库已有的强制 CI 门禁。
