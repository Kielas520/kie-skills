# 工作空间落点

开发和测试放在 `~/kie-ws` 下。每个仓库使用 `~/kie-ws/<仓库名>/` 作为容器；容器本身不是仓库。Spike 调研单独放在 `~/kie-ws/spike/` 下，不归属任何仓库容器。

| 用途 | 路径 |
| --- | --- |
| 源仓库 | `~/kie-ws/<仓库名>/source/` |
| 工作项目录 | `~/kie-ws/<仓库名>/<name>/` |
| 分支工作区，有单号 | `~/kie-ws/<仓库名>/<name>/<单号>/` |
| 分支工作区，无单号 | `~/kie-ws/<仓库名>/<name>/branch_source/` |
| 方案、设计与设备信息 | 工作项目录下的 `solution.md`、`design.md`、`devices.md` |
| 工作项临时文件 | 工作项目录下的 `.tmp/` |
| 测试文件与验收报告 | `.tmp/test-n/`，报告为 `test-report-n.md` |
| 修复记录 | `.tmp/fix/fix-n.md` |
| 评审与修复评论 | `.tmp/comment/comment-review-n.md`、`comment-fix-n.md` |
| 其他临时文档 | `.tmp/docs/` |
| 跨仓库评估与调试沙箱 | `~/kie-ws/test/` |
| Spike 调研目录 | `~/kie-ws/spike/<name>/` |
| Spike 调研用到的源码仓库 | `~/kie-ws/spike/<name>/<仓库名>/`，每个仓库一个目录，直接用仓库名命名 |
| Spike 调研文档与资料 | Spike 调研目录下的 `.tmp/docs/` |

- `<name>` 是根据工作内容取的简短名称，同一仓库的不同工作各用一个目录；Spike 调研的 `<name>` 取调研主题，可带单号。分支名中的名称与工作项目录名一致。
- 仓库容器内克隆仓库时将克隆目录命名为 `source`；工作区从该源仓库创建。`kie-skills` 也使用相同结构。Spike 调研可能涉及多个仓库，调研目录内的克隆直接以仓库名命名，不套 `source/`。
- `test-n/`、`fix/`、`comment/` 的编号各自在当前工作项内计算，互不跨工作项。测试脚本和该次验收报告放在同一个 `test-n/` 下。
- 工作项目录内的文档与临时文件不放进分支工作区；没有工作项归属时的中间文件和草稿分别使用 `~/kie-ws/.tmp/` 与 `~/kie-ws/.draft/`。
- `~/kie-ws` 根目录不落单个文件。
