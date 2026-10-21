# PR 317 评审报告

## PR 概况

| 项 | 内容 |
| --- | --- |
| 链接 | https://github.com/example/tailq/pull/317 |
| 作者 | dev-b |
| 分支 | feat/m-7301122334/upload-retry → main |
| head SHA | 4f1c9a2e7b3d5c6f8a9b0c1d2e3f4a5b6c7d8e9f |
| 工单 | m-7301122334 |
| 提交 | 2 个 |
| 改动文件 | 2 个，+23 / -3 |
| CI | 通过 |
| 已有评审 | 无 review 结论；1 个未解决 thread（reviewer-a，`uploader.py:27`，最后一轮失败后仍 sleep） |

## 改动与声称的一致性

| PR body 或工单声称的内容 | 改动里对应的位置 | 结论 |
| --- | --- | --- |
| 失败后按指数退避重试，默认 3 次 | `uploader.py` / `upload` | 做到 |
| 重试次数可通过 `--retry` 参数配置 | `uploader.py` / `RETRY_TIMES` 常量 | 没有做到 |
| 全部重试失败时命令以非零退出码结束 | `uploader.py` / `main` | 没有做到 |
| 新增 `tests/test_uploader.py`，`pytest` 通过 | `tests/test_uploader.py` | 做到 |

超出声称范围的改动：无

## 改动走读

### uploader.py

- 改了什么：新增 `import time` 与常量 `RETRY_TIMES = 3`；`upload()` 从单次请求改成 `while attempt < RETRY_TIMES` 的循环，捕获 `Exception` 后 `attempt += 1` 并 `time.sleep(2 ** attempt)`，循环结束返回 `False`。
- 为什么改：PR body 说网络抖动时直接失败会丢一批日志。
- 核对结论：重试循环本身成立；成功判定、异常处理、退出码与参数化四处与声称或项目约定不符，见问题清单。

### tests/test_uploader.py

- 改了什么：新增文件，一个用例 `test_upload_success`，mock `urlopen` 返回 `status == 200`，断言 `upload()` 返回 `True`。
- 为什么改：PR body 的验证段。
- 核对结论：只覆盖成功路径。

## 问题清单

| 序号 | 位置 | 类别 | 严重度 | 问题 | 依据 | 修改建议 | 定夺 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `uploader.py:36` / `main` | 正确性 | 必须修 | 上传全部失败时命令仍以 0 退出 | 第 34 行 `ok = upload(batch)`，第 36 行无条件 `return 0`；`AGENTS.md` 规定 `main()` 返回值就是退出码 | `return 0 if ok else 1` | 要提 |
| 2 | `uploader.py:25` / `upload` | 边界与错误处理 | 必须修 | `except Exception` 吞掉全部失败原因，重试耗尽后用户看不到为什么失败 | 第 25 至 27 行只计数与 sleep，不输出异常；`AGENTS.md` 禁止只计数不输出的 `except` | 只捕获 `urllib.error.URLError`，把 `attempt` 与异常信息输出到 stderr，其他异常继续抛出 | 要提 |
| 3 | `uploader.py:8` / `RETRY_TIMES` | 范围 | 必须修 | body 声称 `--retry` 参数可配，代码里是写死的模块常量，`main()` 也没有解析参数 | 第 8 行 `RETRY_TIMES = 3`，diff 里没有参数解析；`AGENTS.md` 要求运行参数由命令行参数给出 | `upload()` 加 `retry_times` 参数，`main()` 用 `argparse` 解析 `--retry` 传入 | 要提 |
| 4 | `uploader.py:24` / `upload` | 正确性 | 必须修 | 采集服务成功时返回 202，`resp.status == 200` 把成功当失败且直接返回，不重试 | 第 24 行 `return resp.status == 200`；`AGENTS.md` 写明服务返回 202 Accepted | 判定改为 `resp.status == 202` | 改成：判定改为 `200 <= resp.status < 300`，服务以后换状态码也不用再改 |
| 5 | `tests/test_uploader.py` | 测试 | 建议修 | 重试路径与重试耗尽路径没有测试 | 测试文件只有 `test_upload_success`，mock 从不抛异常 | 补两个用例：前两次抛 `URLError` 第三次成功；三次都抛异常时返回 `False`。mock `time.sleep` 避免真等 | 要提 |
| 6 | `uploader.py:27` / `upload` | 可选 | 可选 | 首轮失败后等 2 秒而不是 1 秒，`2 ** attempt` 在自增之后计算 | 第 26 行先 `attempt += 1`，第 27 行再 `2 ** attempt` | 改为 `2 ** (attempt - 1)` | 不提（reviewer-a 的 thread 已在讨论退避节奏，等那条有结论再说） |

## 测试覆盖

| 改动的行为 | 对应测试 | 结论 |
| --- | --- | --- |
| 上传成功返回 `True` | `tests/test_uploader.py::test_upload_success` | 已覆盖 |
| 失败后重试、第 n 次成功 | 无 | 未覆盖 |
| 重试耗尽返回 `False` | 无 | 未覆盖 |
| 失败时非零退出码 | 无 | 未覆盖 |

运行结果：未运行，评审依据用户导出的 diff 与 head 文件，没有检出仓库。

## 项目约定核对

| 约定 | 出处 | 结论 |
| --- | --- | --- |
| 错误不吞掉 | `AGENTS.md` | 不符合（`uploader.py:25`） |
| 命令失败时以非零退出码结束 | `AGENTS.md` | 不符合（`uploader.py:36`） |
| 运行参数由命令行参数给出 | `AGENTS.md` | 不符合（`uploader.py:8`） |
| 采集服务返回 202 | `AGENTS.md` | 不符合（`uploader.py:24`） |
| 新增行为要有对应测试 | `AGENTS.md` | 部分符合（只有成功路径） |

## 待确认的疑问

- 无
