# 更新日志

本文件记录本仓库每个技能的显著变动，按技能各自的版本倒序排列。

格式基于 [Keep a Changelog 1.1.0](https://keepachangelog.com/zh-CN/1.1.0/)，每个技能的版本号遵守[语义化版本规范](https://semver.org/lang/zh-CN/)。

## 本仓库的记法

本仓库是技能集合，没有仓库级版本，发布单位是每个技能自己的 `metadata.version`：

- 段头写作 `## [<技能名> <版本>] - <YYYY-MM-DD>`，版本取该技能 frontmatter 里的 `metadata.version`，日期用 ISO 8601，新版本在前。
- 段内按变动类型分组，只保留有内容的组：`Added`、`Changed`、`Deprecated`、`Removed`、`Fixed`、`Security`。
- 版本与段一一对应：只要 bump 了 `metadata.version` 就有一段，纯文字与格式修正这类 patch 也记一句话。
- 条目写人能读的一句话，说清这次变动对使用者意味着什么，不抄提交标题，也不记与技能行为无关的仓库改动。
- 技能创建记为 `Added`；技能改名或合并时，在条目里注明原技能名。

## [kie-skill-dev 0.20.0] - 2026-10-13

### Added

- 仓库约定增加更新日志一项：技能内容改动要在仓库根 `CHANGELOG.md` 里记一条，位置、段头格式与变动类型分组都写在那条约定里。
- 第 6 步的改动总结要列出本次的更新日志条目，第 9 步提交前要核对它已经记下。

## [kie-skill-fix 0.4.0] - 2026-10-13

### Changed

- 修复完成后同样要给被改技能记一条更新日志，时机与格式按 kie-skill-dev 的仓库约定，写法不在本文件重复。

## [kie-commit-pr 0.1.0] - 2026-10-13

### Added

- 新增技能：按 Conventional Commits 从工作区改动与工单号推导 type、scope 与中文 description，写说明为什么改的 body 与 `Resolve` footer，草稿经用户确认后执行本地提交。
- 由 `kie-pr-start` 与 `kie-git-commit` 合并而来，这两个技能在同一次改动里移除。

## [kie-agent-rules 0.13.0] - 2026-10-12

### Changed

- 提交与回退段重组：合入 main 前先征询用户、统一用 squash merge 并删除开发分支、团队仓库 main 只允许通过 PR 合并且门禁为 2 个 approval 加 CodeRabbit 加 CI 全绿；同步上游与集成分支统一用 merge，不用 rebase。
- 相关技能路由表补上生成提交信息与本地提交这一条。

## [kie-dev-test 0.3.0] - 2026-10-12

### Changed

- 版本号随仓库的提交与 PR 流程重构对齐，正文没有行为变化。

## [kie-git-commit 0.1.0] - 2026-10-12

### Added

- 新增技能：按 Conventional Commits 生成中文提交信息并执行本地提交，信息草稿先给用户确认。（0.1.0 之后在 2026-10-13 与 `kie-pr-start` 合并为 `kie-commit-pr`。）

## [kie-git-worktree 0.3.0] - 2026-10-12

### Changed

- 分支命名表把「多工作项」换成「杂项（无关联单）」的 `chore/{梗概}`；一次解决多个单改为用主单 ID 建分支，其余单号写进 commit footer。
- 补上 main 只允许通过 PR 合并、`hotfix/*` 紧急修复不带工单 ID 的说明。

## [kie-pr-ci-test 0.3.0] - 2026-10-12

### Changed

- 回写 PR body 的段名从「测试报告段」改为「验证段」，按当前 body 里已有的段名定位。

## [kie-pr-review-fix 0.3.0] - 2026-10-12

### Changed

- 核对 PR body 时按「验证段」判断；评审修复的往来与「按评审意见修改」这类说明只留在评论里，不写进描述。

## [kie-pr-start 0.3.0] - 2026-10-12

### Changed

- PR body 模板按分支类型拆成两份：`feat/` 写背景、改动、验证、影响，`fix/` 写问题、原因、改动、验证、影响，末尾带 `Resolve` footer。
- PR 标题按 commit 首行格式写，squash 后就是 main 上的 commit 标题。

## [kie-dev-design 0.4.0] - 2026-10-12

### Changed

- 文档模板改名为 `design.md`，删掉旧的技术方案模板，新增「篇幅与去重」章节，质量用例同步到新结构。

## [kie-env-setup 0.2.0] - 2026-10-12

### Changed

- 本机取值从正文与参考文件里清出去：取值一律以本次探测输出为准，参考文件只留判定方式与安装内容。
- 新增回归用例，断言 git 身份必须本次取证、不得引用带日期的历史结论。

## [kie-env-setup 0.1.1] - 2026-10-12

### Changed

- 「现状」与已知缺口改按实测收窄，代理段改为以当前进程与配置文件的实际探测为准。

## [kie-env-setup 0.1.0] - 2026-10-12

### Added

- 新增技能：只读探测工作空间骨架、仓库落位、命令行工具链、系统与网络、部署与接入，按五组出差异清单并逐项等用户确认。

## [kie-dev-solution 0.4.0] - 2026-10-10

### Changed

- 「项目现状」必须先讲清原有设计的技术原理：机制是什么、覆盖哪些范围、数据从哪来到哪去、每个环节做什么，不压成文件与符号清单。
- `solve.md` 新增「原有设计要点」一节，并补回归用例与素材。

## [kie-agent-rules 0.12.0] - 2026-10-10

### Changed

- 项目文档目录按工单类型分层：Bug 单落 `fix/f-{ID}`、Story 与 Epic 落 `feat/m-{ID}`、无工单用梗概单层目录，分类头与 worktrees 对齐。
- 新增分层落点回归用例与素材，其他技能里固定平铺落点的用例与 fixture 同步到新分层。

## [kie-agent-rules 0.11.0] - 2026-10-10

### Changed

- 补「技能被调用不构成开工指令」：技能正文里的产出物路径不作为落盘依据。

## [kie-dev-design 0.3.0] - 2026-10-10

### Changed

- 产出物随 `solution.md` 与 `solve.md` 的拆分同步。

## [kie-dev-solution 0.3.0] - 2026-10-10

### Changed

- 产出物拆成 `solution.md`（交用户拍板的选型文档）与 `solve.md`。

## [kie-agent-rules 0.10.0] - 2026-10-10

### Changed

- 工作空间根目录补 `~/kie-ws/.tmp/` 与 `~/kie-ws/.draft/` 两个落点，中间结果按工作区分支情形取落点，根目录不落单个文件。

## [kie-agent-rules 0.9.0] - 2026-10-10

### Changed

- 工作空间根目录迁到 `~/kie-ws`，项目容器加 `-p` 后缀。
- 补 `AGENTS.md` 的读取时机：已确定在哪个项目里干活就直接读取并报路径，还不知道动哪个项目先问一句，任务与该项目无关时不读取。

## [kie-dev-design 0.2.0] - 2026-10-10

### Changed

- 设计文档落点随工作空间迁移改成项目容器下的 `~/kie-ws/<项目名称>-p/.idea/...`。

## [kie-dev-execute 0.3.0] - 2026-10-10

### Changed

- 设计文档与计划文件的表述改为同目录下的 `design.md`、`plan.md`，路径随工作空间迁移更新。

## [kie-dev-solution 0.2.0] - 2026-10-10

### Changed

- 新增「准备源仓库」段：调研前确认源仓库已经克隆并与最新 main 同步，落后的 commit 数写进方案文档的「项目现状」；工作区有未提交改动时不动它，报给用户决定。

## [kie-dev-test 0.2.0] - 2026-10-10

### Changed

- 工作区与产物路径随工作空间迁移更新到 `~/kie-ws/<项目名称>-p/`。

## [kie-git-worktree 0.2.0] - 2026-10-10

### Changed

- 工作区落点随迁移改为 `~/kie-ws/<项目名称>-p/worktrees/<分支名>`；`git worktree list` 的说明改为确认源仓库落在哪个项目容器下。

## [kie-pr-ci-test 0.2.0] - 2026-10-10

### Changed

- CI 产物下载目录明确为 `.scratch/ci-<run-id>/`，其余路径随工作空间迁移更新。

## [kie-pr-review-fix 0.2.0] - 2026-10-10

### Changed

- 仓库路径与工作区落点随工作空间迁移更新到 `~/kie-ws/<项目名称>-p/`。

## [kie-pr-start 0.2.0] - 2026-10-10

### Changed

- 仓库路径与工作区落点随工作空间迁移更新到 `~/kie-ws/<项目名称>-p/`。

## [kie-skill-dev 0.19.0] - 2026-10-10

### Changed

- 沙箱、脚本与素材路径随工作空间迁移改成 `~/kie-ws` 与 `-p` 后缀。

## [kie-skill-fix 0.3.0] - 2026-10-10

### Changed

- 评估脚本与沙箱路径随工作空间迁移改成 `~/kie-ws/kie-skills/...`。

## [kie-skill-dev 0.17.0] - 2026-10-09

### Changed

- 调查边界收束为「用户给的输入加本仓库已固化的约定」，去掉外部约定文件这一取材来源。
- 评估边界加「用户没有明确允许时推送、提交、合并、打 tag、发通知都不能自己擅自执行」；触发用例的远端约束只收正例，正文示例换成推送分支、合并分支、跟进 CI，质量用例换成本地场景。
- 沙箱遮蔽逐层盖住同一轮的兄弟目录，适配层的配置路径改从 `work/` 推出，修掉并发时两组瞬间失败。

## [kie-agent-rules 0.7.0] - 2026-10-09

### Changed

- 详述层的来源改为正文的详述层，去掉写死的 `~/project/AGENTS.md` 阅读路径，优先级链回落为 SKILL.md 正文高于详述层。

## [kie-agent-rules 0.6.0] - 2026-10-09

### Changed

- 新增详述层 `references/user-rules-full.md`，收录正文没有的内容：用词的例子与反例、术语的允许范围、错误处理链路与批量命令退出码；正文已有结论的条目不在该文件重复。

## [kie-skill-dev 0.15.0] - 2026-10-09

### Changed

- 第 7 步与第 8 步的用例输入都不得要求会话碰远端，第 8 步补本地 fixture 替代与「写用例前先审一遍远端命令」。
- 新增发版流程固化的回归用例与素材。

## [kie-skill-dev 0.14.0] - 2026-10-09

### Changed

- `description` 收窄到新建技能与技能本身没有行为异常时的正文与 description 改写，手上的行为异常交给 kie-skill-fix，质量用例同步调整。

## [kie-skill-fix 0.2.0] - 2026-10-09

### Added

- 新增技能：把技能行为异常落成三行现象、在评估沙箱复现、归类根因、出修复方案等用户批准、改完验证并把现象固化成回归用例；字段写法、校验、接入、评估脚本与提交部署引用 kie-skill-dev。带 22 条触发用例与 2 条质量用例。

## [kie-dev-execute 0.2.0] - 2026-10-09

### Changed

- 交付段指向 `kie-dev-test`，推送前的本地测试与测试报告交给它。

## [kie-dev-test 0.1.0] - 2026-10-09

### Added

- 新增技能：按工单验收标准做推送前的本地测试与测试报告，缺陷单附有问题版本与当前产物的对照实验。

## [kie-pr-ci-test 0.1.0] - 2026-10-09

### Added

- 新增技能：PR 建好、CI 跑完后验收远端产物，产出测试报告评论并把远端结果追加进 PR body。

## [kie-pr-review-fix 0.1.0] - 2026-10-09

### Added

- 新增技能：按四个流程处理 PR 评审意见，先写审核文档与实现文档，用户确认后改代码、测试、逐条回复。

## [kie-pr-start 0.1.0] - 2026-10-09

### Added

- 新增技能：本地测试通过后起草 PR body 与标题，交用户确认之后才创建 PR。

## [kie-python-style 0.1.0] - 2026-10-09

### Added

- 新增技能：收录 Python 的开发约定（uv、类型注解、pathlib、rich、loguru）。

## [kie-rust-gates 0.1.0] - 2026-10-09

### Added

- 新增技能：Rust 的提交与推送门禁，fmt、clippy 与最小受影响测试集。

## [kie-agent-rules 0.5.0] - 2026-10-08

### Changed

- `compatibility` 去掉固定的一种 agent CLI，命令行依赖改为按技能评估脚本的适配层判定。

## [kie-skill-dev 0.12.0] - 2026-10-08

### Changed

- 评估改用 `--agent` 选定 agent CLI：新增 `scripts/agent_cli.py` 适配层，两个评估脚本不再写死 omp，结果与 benchmark 记下所用 CLI。
- 沙箱遮蔽扩到测试工作区里本次运行之外的目录；负例判定改为一律 `--runs 3`。

## [kie-agent-rules 0.4.0] - 2026-10-08

### Changed

- 补「讨论不等于授权」与开工指令的两种来源，越界最常见的「评价加祈使词」写进 Gotchas。

## [kie-skill-dev 0.8.0] - 2026-10-08

### Changed

- Gotchas 记下「用户对技能写法的评价与建议属于讨论」，改动要等开工指令。

## [kie-agent-rules 0.3.0] - 2026-10-08

### Changed

- 咨询类的识别信号扩充到「行不行」「能不能」「要不要」「可以吗」，询问语气的判据写成语气与句式。

## [kie-skill-dev 0.7.0] - 2026-10-08

### Changed

- 第 6 步补「提问与改动分开」，Gotchas 记下询问语气不构成改动授权。

## [kie-git-worktree 0.1.0] - 2026-10-08

### Added

- 新增技能：按工作项 ID 生成分支名并把工作区建到项目容器的 `worktrees/` 下，只负责新建，方案经用户确认后动手。

## [kie-skill-dev 0.6.0] - 2026-10-08

### Changed

- 触发评估与质量评估的沙箱目录名改为技能名哈希，会话不再顺着目录名认出被测技能。

## [kie-skill-dev 0.5.0] - 2026-10-08

### Changed

- 新增第 6 步确认与总结，触发评估改为 `scripts/trigger_eval.py`（预检、心跳、粗筛、退出码 0/1/2），输出质量评估改为 `scripts/quality_eval.py`（带技能与不带技能对比、截断标记、退出码）。

## [kie-dev-design 0.1.0] - 2026-10-01

### Added

- 新增技能：方案选定后写技术设计文档，含数据链路图与具体设计。

## [kie-dev-execute 0.1.0] - 2026-10-01

### Added

- 新增技能：按设计文档生成计划，逐条实现到可运行，先写测试再实现。

## [kie-dev-solution 0.1.0] - 2026-10-01

### Added

- 新增技能：开工前的调研与多方案选型，产出选型文档交用户拍板。

## [kie-skill-dev 0.3.0] - 2026-10-01

### Changed

- 沙箱改为放整份技能集：复制整个 `skills/` 并平铺进沙箱的 `skills/`，只删各技能的 `evals/`，只放被测技能会让负例被全部误判为触发。

## [kie-agent-rules 0.2.0] - 2026-09-30

### Added

- 新增技能：协作准则的通用规则层，含指令类型判定、提交与回退、命名与呈现、工作空间、文件删除与技能路由。

## [kie-doc-style 0.2.0] - 2026-09-30

### Added

- 新增技能：检查与生成中英文项目文档的文风，规则细节移到 `references/` 下。

## [kie-skill-dev 0.2.0] - 2026-09-30

### Added

- 新增技能：Agent Skill 的创建与修改流程，覆盖字段与目录约定、校验、本地接入、评估与提交部署。
