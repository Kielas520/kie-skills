---
name: kie-git-worktree
description: |
  只在需要为一个任务新建独立的 git worktree 与分支时使用：按工作项 ID 与任务内容生成分支名（feat/m-<ID>/<英文梗概>、fix/f-<ID>/<英文梗概>、chore/<英文梗概>、hotfix/<英文梗概>），把工作区建到 ~/kie-ws/<项目名称>-p/worktrees/<分支名>，从项目容器的 source/<仓库名> 开出。用户说「开个分支做这个」「单独开个工作区」「另开个独立目录干活」「并行处理两件事」「为这个单开个分支」「别动我当前工作区」时使用，即使没有说出 worktree 这个词；用户给出飞书项目单号并要求开始这个单的工作时同样适用；个人项目开发同样适用；已交付版本的紧急修复要新建 hotfix 分支与工作区时同样适用。不适用：对已有分支与已有工作区的任何操作（查看、切换、合并、清理、删除）、在当前目录直接开发、把代码放到其他位置、提交与推送、合入规则与合并方式。
license: MIT
metadata:
  author: Kielas
  version: "0.4.0"
---

# 新建 worktree 工作区

为一个任务建立独立的开发工作区，多个任务并行时互不干扰。工作区统一放在 `~/kie-ws/<项目名称>-p/worktrees/` 下，由 `~/kie-ws/<项目名称>-p/source/<仓库名>/` 开出。`<项目名称>` 与 `<仓库名>` 的取值见 `kie-agent-rules` 技能目录下的 `references/workspace.md`。

## 子能力

| 子能力 | 产出 | 改不改仓库 |
| --- | --- | --- |
| 收集基线与占用情况 | 默认分支、基线 commit、拟用分支名是否被占用 | 只执行 `git fetch`，更新远端跟踪分支 |
| 提出方案 | 分支名、工作区路径、基线三项 | 不改 |
| 创建工作区 | 新分支与 worktree 目录 | 改，三项都得到用户确认后才做 |
| 验证与交付 | 验证结果与进入命令 | 不改 |

用户没有明确要求开分支或开工作区时，只收集情况、给出建议，不创建。分支名、工作区路径、基线三项都得到用户确认后才创建；用户在请求里明确说了「定好直接建」「不用等我确认」时视为已确认。用户改动其中任意一项时，把新的完整方案再贴一遍确认。

## 步骤 1：收集基线与占用情况

命令在源仓库 `~/kie-ws/<项目名称>-p/source/<仓库名>/` 内执行；不在仓库目录里时给每条命令加 `git -C <源仓库>`。

```bash
git fetch origin                                  # 个人项目的本地仓库没有远端时跳过
git symbolic-ref --short refs/remotes/origin/HEAD # 默认分支，输出形如 origin/main
git rev-parse --short origin/<默认分支>           # 基线 commit
git worktree list                                 # 这个仓库已有的全部 worktree
git branch -a --list '<分支名>' '*/<分支名>'       # 拟用分支名在本地与远端是否已存在
```

- 基线分支取 `origin/<默认分支>`。
- 个人项目的本地仓库没有远端时，基线取本地默认分支，commit 用 `git rev-parse --short <默认分支>` 取。
- 有远端但没有 `origin/HEAD`（第二条命令报错）时，基线分支由用户指定，不自己挑。
- 拟用分支名已存在时，对照 `git worktree list` 看它是否正被其他 worktree 检出，把情况写进方案，交给用户决定复用已有工作区还是换分支名。

## 步骤 2：提出方案

分支命名：

| 场景 | 格式 | 示例 |
| --- | --- | --- |
| 缺陷单 | `fix/f-{ID}/{梗概}` | `fix/f-6925239029/fix-crash` |
| 需求单 / Epic | `feat/m-{ID}/{梗概}` | `feat/m-6918761640/add-login` |
| 不影响功能的杂项（依赖升级、文档、配置整理） | `chore/{梗概}` | `chore/update-deps` |
| 已交付版本的紧急修复 | `hotfix/{梗概}` | `hotfix/fix-boot-loop` |

- 一个分支对应一个工作项；一次解决多个单时用主单 ID 建分支，其余单号写进 commit footer。
- 梗概段写成动词开头的英文短语，全小写单词用连字符连接，一般 2 个词以内、最多 3 个词，不使用下划线、空格、中文与驼峰。
- 单号与梗概来自用户给出的工作项与对话内容，不自行编造，也不拿相近的编号顶替。
- 改动会影响功能、又没有单号时，问用户是先给单号，还是用 `chore/` 命名。紧急修复没有单号时直接用 `hotfix/{梗概}`，不阻塞。

把三项一起给用户：

```text
分支: fix/f-<ID>/<梗概>
工作区: ~/kie-ws/<项目名称>-p/worktrees/fix/f-<ID>/<梗概>
基线: origin/main (<commit>)
```

工作区路径固定是 `~/kie-ws/<项目名称>-p/worktrees/<分支名>`。分支名里的斜杠就是目录层级，不压成连字符；用户只给出根目录时补上 `<项目名称>-p` 与 `worktrees` 两层。项目容器不存在时说明会一并建出。

## 步骤 3：创建 worktree

```bash
git -C ~/kie-ws/<项目名称>-p/source/<仓库名> worktree add ~/kie-ws/<项目名称>-p/worktrees/<分支名> -b <分支名> <基线>
```

命令里显式写基线：不带基线时从当前 HEAD 分叉，源仓库停在旧提交或别的分支时会带进错误的基线。git 会自动创建多层父目录。

| 情况 | 处理 |
| --- | --- |
| 报 `fatal: '<路径>' already exists` | 目录已被占用（git 只接受不存在或空的目录）。不覆盖、不加 `--force`，用 `git branch --list <分支名>` 确认分支有没有被建出来，把冲突路径与分支状态报给用户，由用户决定换路径还是先处理已有目录 |
| 报 `fatal: a branch named '<分支名>' already exists` | 用 `git worktree list` 确认它是否正被别的 worktree 占用，报给用户，由用户决定复用已有工作区还是换分支名；同一分支不能同时检出到两个 worktree |
| 用户要检出已有分支 | 去掉 `-b` 与基线，写 `git worktree add <路径> <已有分支>` |

## 步骤 4：验证与交付

```bash
git worktree list
git -C ~/kie-ws/<项目名称>-p/worktrees/<分支名> status --short --branch
git -C ~/kie-ws/<项目名称>-p/worktrees/<分支名> log --oneline -1
```

第二条输出新分支名，第三条输出与基线一致的 commit，两条都对上才算建好；对不上时把实际输出报给用户。

```text
━━━ worktree 已创建 ━━━
分支: <分支名>
工作区: ~/kie-ws/<项目名称>-p/worktrees/<分支名>
基线: origin/<默认分支> (<commit>)
进入: cd ~/kie-ws/<项目名称>-p/worktrees/<分支名>
提醒: 新工作区不共享构建产物与未纳入版本控制的文件（Rust 的 target/、Node 的 node_modules/、.env 之类），需要先装依赖或构建；仓库没有这些时写明不需要重新准备
```

提醒一行每次都写，按仓库实际情况说明，不省略。

## 硬性约束

- 不在仓库内建 worktree（源仓库下的 `.worktrees/` 同样不允许），工作区一律建到 `~/kie-ws/<项目名称>-p/worktrees/` 下；用户明确给出其他路径时按用户给的建。
- 源仓库 `source/<仓库名>/` 只用来开工作区与同步默认分支，不在它的默认分支上做开发改动。
- 不使用 `--force`，不覆盖已有目录，不删除已有 worktree。

## Gotchas

- 已经在某个 worktree 内执行时，`git rev-parse --show-toplevel` 给出的是当前 worktree 的路径，项目名不能取它的目录名，要从源仓库路径取。
