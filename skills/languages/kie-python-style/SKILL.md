---
name: kie-python-style
description: |
  Python 代码的写法与环境约定：环境与依赖管理、Python 版本基线、类型注解写法、路径操作、进度条、结构化输出、日志库与 import 写法。写、改、评审、重构 Python 代码，或建环境、装依赖、挑库、补类型注解、替换旧写法、写脚本与调试代码时使用，即使用户没有提到「规范」「约定」，也没有给出文件与上下文。不适用：Rust 项目与 Rust 的提交推送门禁（用 kie-rust-gates）；推送前的验收测试与测试报告（用 kie-dev-test）；与语言无关的协作规则（见 kie-agent-rules）；纯知识问答（解释 GIL、语法速查）。
license: MIT
compatibility: 需要 uv 与 Python 3.10 及以上，推荐 3.13 及以上。
metadata:
  author: Kielas
  version: "0.2.0"
---

# Python 开发约定

写、改 Python 代码时按本技能执行，不用与本文冲突的通用写法。

## 适用范围

- 新写的代码与本次改动涉及的函数，按本技能的写法写；改动涉及的函数里有旧式写法（`os.path`、`typing.Union`、标准库 `logging` 这类），跟着这次改动一起改掉。
- 本次改动之外的旧式写法只指出，不改。
- 用户明确要求「按约定改一遍」某个文件或模块时，整份按本技能改写。

## 环境与版本

- 用 uv 管理环境与依赖，不用全局 pip：

  ```bash
  uv init                 # 新建项目
  uv add <包>             # 加依赖，写进 pyproject.toml
  uv run <脚本或命令>      # 在项目环境里运行
  ```

- 已有项目以 `pyproject.toml` 的 `requires-python` 为准。
- 新项目按 3.13 基线初始化，最低 3.10，不考虑 3.10 之前的兼容性；用户明确指定目标版本时按用户说的来。

## import 与文件开头

- 必需的库直接 import，不用 try-except 包住 import。
- 文件开头不加模块 docstring，也不加 shebang。

## 类型注解

- 对外暴露的函数必须写类型注解，内部函数看情况。
- 3.10 及以上不需要 `from __future__ import annotations`。
- 联合类型用 `|`，不用 `typing.Union` 与 `typing.Optional`：`def f(x: str | None) -> str | int`。
- 容器注解用内置小写 `dict`、`list`、`tuple`，不用 `typing.Dict`、`typing.List`。
- 抽象容器（`Iterable`、`Mapping`、`Sequence` 等）从 `collections.abc` 取，不从 `typing` 取。
- dict 不写裸的 `dict`，至少写成 `dict[str, Any]`；内部结构不必写全。
- 元素意义明确的元组，继承 `typing.NamedTuple` 定义成类，不返回裸 tuple：

  ```python
  from typing import NamedTuple

  class Point(NamedTuple):
      x: int
      y: int
  ```

## 文件操作

- 一律用 pathlib，不用 `os.path` 系列。
- 函数签名含路径参数时类型写 `str | Path`，函数体第一行转成 `Path` 对象再操作。
- 返回路径时按调用方需求明确二选一：返回 `str` 或返回 `Path`。

## 打印、进度与日志

- 进度条：简单场景用 `rich.progress.track`，多任务、嵌套、动态刷新的场景用 `rich.progress.Progress`。
- 打印 json、字典、dataclass 等结构化数据用 `from rich import print as rprint`。
- 需要日志库时用 loguru，不用标准库 `logging` 手搭。
