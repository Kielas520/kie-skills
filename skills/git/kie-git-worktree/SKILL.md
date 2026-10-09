---
name: kie-git-worktree
description: |
  只在需要为一个任务新建独立的 git worktree 与分支时加载（新建之外的 git 操作都不归本技能，不要为了让别的操作确认边界而读取）：按工作项 ID 与任务内容生成分支名（feat/m-<ID>/<英文梗概>、fix/f-<ID>/<英文梗概>），把工作区建到 ~/kie-ws/<项目名称>-p/worktrees/<分支名>，从项目容器的 source/<仓库名> 开出。用户说「开个分支做这个」「单独开个工作区」「另开个独立目录干活」「并行处理两件事」「为这个单开个分支」「别动我当前工作区」时使用，即使没有说出 worktree 这个词；用户给出飞书项目单号并要求开始这个单的工作时同样适用；个人项目开发同样适用。对已有分支与已有工作区的任何操作（查看、切换、合并、清理、删除）、在当前目录直接开发、把代码放到其他位置、提交与推送都不适用。
license: MIT
metadata:
  author: Kielas
  version: "0.2.0"
---

# 新建 worktree 工作区

为一个任务建立独立的开发工作区，多个任务并行时互不干扰。分支命名锚定工作项 ID，工作区统一放在项目容器的 `~/kie-ws/<项目名称>-p/worktrees/` 下，由 `~/kie-ws/<项目名称>-p/source/<仓库名>/` 开出。`<项目名称>` 与 `<仓库名>` 的取值见 `kie-agent-rules` 的工作空间约定。

## 纪律

用户是决策者，agent 是执行者。用户没有明确要求开分支或开工作区时，只收集基线与分支占用情况、给出建议，不执行创建动作。分支名、工作区路径、基线分支三项都得到用户确认后才动手；用户改动其中任意一项时，把新的完整方案再贴一遍确认。

## 步骤 1：收集基线与占用情况

收集只服务两件事：确定基线（默认分支与基线 commit），判断拟用的分支名是否已被占用。

命令在源仓库 `~/kie-ws/<项目名称>-p/source/<仓库名>/` 或它的任一 worktree 内执行；不在仓库目录里时先进入源仓库，或给每条命令加 `git -C <源仓库>`。

```bash
git worktree list --porcelain | head -1
git branch -a --format='%(refname:short)' | head -30
git symbolic-ref --short refs/remotes/origin/HEAD
```

| 命令 | 说明 |
| --- | --- |
| `git worktree list --porcelain \| head -1` | 当前仓库的主工作区路径，用来确认源仓库落在哪个项目容器下，同时列出这个仓库已有的 worktree |
| `git branch -a --format='%(refname:short)' \| head -30` | 列出本地与远端分支，用于判断拟用分支名是否已存在 |
| `git symbolic-ref --short refs/remotes/origin/HEAD` | 默认分支，输出形如 `origin/main` |

基线分支取 `origin/<默认分支>`，基线 commit 用 `git rev-parse --short origin/main` 取。个人项目的本地仓库没有远端时，基线分支取本地默认分支 `main`，commit 用 `git rev-parse --short main` 取。有远端但没有 `origin/HEAD`（第三条命令报错）时，基线分支由用户指定，不自己挑。

拟用的分支名出现在分支列表里时，先确认它是否正被其他 worktree 检出，把情况写进方案交给用户决定复用已有工作区还是换分支名。

## 步骤 2：提出方案并等待确认

分支命名：

| 场景 | 格式 | 示例 |
| --- | --- | --- |
| Bug 修复 | `fix/f-{ID}/{梗概}` | `fix/f-6925239029/fix-crash` |
| 需求单 / Epic | `feat/m-{ID}/{梗概}` | `feat/m-6918761640/add-login` |
| 多个工作项 | `fix/f-{ID1},f-{ID2}/{梗概}` | `fix/f-1,f-2/fix-two` |
| 个人项目开发 | `{梗概}` | `update-deps` |

梗概段写成动词开头的英文短语（`add-login`、`fix-crash`、`update-deps`），全小写单词用连字符连接，一般 2 个词以内、最多 3 个词，不使用下划线、空格、中文与驼峰。

把这三项一起给用户：

```text
分支: fix/f-7128574383/linux-commit-unknown
工作区: ~/kie-ws/wuji-cli-dev-p/worktrees/fix/f-7128574383/linux-commit-unknown
基线: origin/main (2f0f8a8)
```

工作区路径固定是 `~/kie-ws/<项目名称>-p/worktrees/<分支名>`；用户只给出根目录时补上 `<项目名称>` 与 `worktrees` 两层，不要把目录压平。项目容器不存在时说明会一并建出 `~/kie-ws/<项目名称>-p/worktrees/`。

单号与梗概来自用户给出的工作项与对话内容；单号缺失时向用户询问，不自行编造，也不拿相近的编号顶替。

## 步骤 3：创建 worktree

确认后执行：

```bash
cd ~/kie-ws/<项目名称>-p/source/<仓库名>
git fetch origin                     # 个人项目的本地仓库没有远端时跳过
git worktree add ~/kie-ws/<项目名称>-p/worktrees/<分支名> -b <分支名> <基线>
```

git 会自动创建多层父目录。冲突时的处理：

| 报错 | 含义与动作 |
| --- | --- |
| `fatal: '<路径>' already exists` | 目录已被占用（git 只接受不存在或者空目录的路径）。不覆盖、不加 `--force`，把冲突路径报给用户，由用户决定换路径还是先处理已有目录 |
| `fatal: a branch named '<分支名>' already exists` | 分支已存在。用 `git worktree list` 确认是否正被别的 worktree 占用，把结论报给用户，由用户决定复用已有工作区还是换分支名 |
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
分支: fix/f-7128574383/linux-commit-unknown
工作区: ~/kie-ws/wuji-cli-dev-p/worktrees/fix/f-7128574383/linux-commit-unknown
基线: origin/main (2f0f8a8)
进入: cd ~/kie-ws/wuji-cli-dev-p/worktrees/fix/f-7128574383/linux-commit-unknown
提醒: 新工作区不共享构建产物与未纳入版本控制的文件（Rust 的 target/、Node 的 node_modules/、.env 之类），需要先装依赖或构建；仓库没有这些时写明不需要重新准备
```

提醒一行每次都写，按仓库实际情况说明，不省略。

## 硬性约束

- worktree 与主仓库共享同一份 `.git`，在 worktree 内提交直接写进同一份历史；`git add`、`commit`、`push` 按 `kie-agent-rules` 只在用户明确要求时执行。
- 不在仓库内建 worktree（源仓库下的 `source/<仓库名>/.worktrees/` 同样不允许），工作区一律建到 `~/kie-ws/<项目名称>-p/worktrees/` 下；用户明确给出其他路径时按用户给的建。
- 源仓库 `source/<仓库名>/` 只用来开工作区与同步 main，不在它的默认分支上做开发改动。
- 不使用 `--force`，不覆盖已有目录，不删除已有 worktree（清理与删除不在本技能范围）。

## Gotchas

- 目标目录必须不存在或者是空目录，路径被占用时 `git worktree add` 以 `fatal: '<路径>' already exists` 失败。失败后用 `git branch --list <分支名>` 确认分支有没有被建出来：已经存在时直接重试会撞上 `branch already exists`，先把残留分支处理掉或者换分支名。
- 分支名里的斜杠会变成目录层级，`~/kie-ws/<项目名称>-p/worktrees/fix/f-7128574383/linux-commit-unknown` 是多层目录，这是预期布局，不要压成连字符。
- 多工作项分支名带逗号（`fix/f-1,f-2/fix-two`），目录名同样带逗号，引用路径时加引号。
- 已经在某个 worktree 内执行时，`git rev-parse --show-toplevel` 给出的是当前 worktree 的路径，项目名不能取自它的目录名，要从源仓库路径或 `git worktree list --porcelain` 的第一行取。
- 不带基线的 `git worktree add <路径> -b <分支名>` 从当前 HEAD 分叉，主仓库停在旧提交或停在别的分支时会把错误的基线带进新工作区，命令里显式写 `origin/<默认分支>`。
- 同一个分支不能同时检出到两个 worktree，遇到分支被占用时改分支名或复用已有工作区，不用 `--force` 绕过。
