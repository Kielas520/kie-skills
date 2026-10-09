---
name: kie-python-style
description: |
  涉及 Python 代码的开发约定，用户提到任何一项都先加载本技能：环境与依赖用 uv（版本基线 3.13 及以上、最低 3.10），类型注解用 `|` 联合与内置小写容器、抽象容器取 collections.abc，路径操作走 pathlib，进度条走 rich，结构化输出走 rich.print，日志走 loguru。写、改、评审、重构 Python 代码，或建环境、装依赖、挑库、补类型注解、替换旧写法（logging、os.path、typing.Union）、写脚本与调试代码时都适用；哪怕只是一句「换成 loguru」「加个进度条」「用 pathlib」，或没有给出文件与上下文、也没有提到「规范」「约定」，同样先加载本技能。不适用：Rust 项目与 Rust 的提交推送门禁（用 kie-rust-gates）；推送前的验收测试与测试报告（用 kie-dev-test）；与语言无关的协作规则（见 kie-agent-rules）；纯知识问答（解释 GIL、语法速查）。
license: MIT
compatibility: 需要 uv 与 Python 3.10 及以上，推荐 3.13 及以上。
metadata:
  author: Kielas
  version: "0.1.0"
---

# Python 开发约定

写、改 Python 代码时按本技能执行，不用与本文冲突的通用写法。

## 环境与版本

- 用 uv 管理环境与依赖：建环境、加依赖、跑脚本都用 uv。
- 版本基线：偏好 3.13 及以上，最低 3.10，不考虑 3.10 之前的兼容性。
- 新项目初始化直接按 3.13 基线走，不为了兼容性降要求，用户明确指定目标版本时按用户说的来。

## 类型注解

- 对外暴露的函数必须写类型注解，内部函数看情况。
- 3.10 及以上基线不需要 `from __future__ import annotations`。
- 联合类型用 `|`，不用 `typing.Union`：`def f(x: str | None) -> str | int`。
- 容器注解用内置小写 `dict`、`list`，不用 `typing.Dict`、`typing.List`。
- 抽象容器从 `collections.abc` 取，不从 `typing` 取。
- dict 注解不必写全内部结构，一般场景写 `dict[str, Any]`；要写细就至少写明 key 类型 `dict[str, object]`。
- 元素意义明确的元组，用继承方式创建 namedtuple 类来明确语义。

## 文件操作

- 一律用 pathlib，不用 `os.path` 系列。
- 函数签名含路径参数时类型写 `str | Path`，函数体第一行转成 `Path` 对象再操作。
- 返回路径时按调用方需求明确二选一：返回 `str` 或返回 `Path`，不含糊。

## 打印、进度与日志

- 进度条：简单场景用 `rich.progress.track`，多任务、嵌套、动态刷新的场景用 `rich.progress.Progress`。
- 打印 json、字典、dataclass 等结构化数据用：

```python
from rich import print as rprint
```

- 需要日志库时用 loguru，不用标准库 `logging` 手搭。

## Gotchas

- 改老代码遇到旧式写法（`os.path`、`Union[...]`、`logging`）时顺手改成上述风格，大范围重构前先问用户。
- 提交推送前的门禁与测试范围选择不在本技能范围，Rust 项目走 `kie-rust-gates`，工单驱动的验收测试走 `kie-dev-test`。
