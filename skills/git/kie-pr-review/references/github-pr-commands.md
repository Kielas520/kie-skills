# 评审 PR 用到的 git 与 GitHub 命令

命令里的 `OWNER/REPO` 与 `0` 换成目标仓库与 PR 编号。

## PR 概况

```bash
gh pr view 0 --repo OWNER/REPO \
  --json number,url,title,author,body,baseRefName,headRefName,headRefOid,commits,files,additions,deletions,reviewDecision
gh pr view 0 --repo OWNER/REPO --json statusCheckRollup \
  --jq '.statusCheckRollup[] | {name, status, conclusion, detailsUrl}'
gh pr diff 0 --repo OWNER/REPO
```

`files` 里是每个改动文件的路径与增删行数，`commits` 里是每个提交的 SHA 与标题。

## 已有的 review 与未解决 threads

```bash
gh api --paginate repos/OWNER/REPO/pulls/0/reviews \
  --jq '.[] | select(.body != "" or .state != "COMMENTED") | {user: .user.login, state, body}'
gh api graphql -f query='
{
  repository(owner: "OWNER", name: "REPO") {
    pullRequest(number: 0) {
      reviewThreads(first: 50, after: null) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved
          isOutdated
          path
          line
          comments(first: 20) { nodes { author { login } body } }
        }
      }
    }
  }
}'
```

`hasNextPage` 为 true 时用 `endCursor` 填 `after` 继续拉，直到取完。

## 检出 head 的最新代码

在 `~/kie-ws/<项目名称>-p/source/<仓库名>/` 里执行：

```bash
git fetch origin pull/0/head
git worktree list
git worktree add --detach ~/kie-ws/<项目名称>-p/worktrees/<head 分支名> <head SHA>
```

`git worktree list` 里已经有该路径时不再 add：进入该路径核对 `git rev-parse HEAD` 等于 head SHA，不等时 `git fetch origin pull/0/head` 后 `git checkout --detach <head SHA>`。fork 来的 PR 也用 `pull/0/head` 拉，不需要加 fork 的 remote。

## 核对行号在 diff hunk 内

```bash
gh pr diff 0 --repo OWNER/REPO | grep -n '^@@\|^+++ ' 
```

`+++ b/<path>` 之后的每个 `@@ -a,b +c,d @@` 表示 head 版本该文件第 `c` 行起的 `d` 行在 hunk 内，行内评论的 `line` 要落在这些区间里。

## 一次 review 提交全部评论

默认发送方式。`comments` 里每条是一条行内评论，`line` 是 head 版本的行号，`side` 固定 `RIGHT`；`body` 放全局评论，多条之间空一行，没有全局评论就留空字符串。JSON 先写进文件再传，避免 shell 转义改坏 Markdown：

```bash
gh api --method POST repos/OWNER/REPO/pulls/0/reviews --input <JSON 文件> --jq '.html_url'
```

JSON 文件结构：

```json
{
  "commit_id": "<head SHA>",
  "event": "COMMENT",
  "body": "<全局评论>",
  "comments": [
    {"path": "<path>", "line": 0, "side": "RIGHT", "body": "<正文>"}
  ]
}
```

输出是 review 链接。返回 422 时整个提交都没有发出，先按上一节逐条核对行号再重发。用户要求给结论时把 `event` 换成 `APPROVE` 或 `REQUEST_CHANGES`。

## 单独发一条评论

只在用户要求把某一条先单独发出去时用：

```bash
gh api --method POST repos/OWNER/REPO/pulls/0/comments \
  -f commit_id='<head SHA>' -f path='<path>' -F line=<line> -f side=RIGHT \
  -F body=@<正文文件> --jq '.html_url'
gh pr comment 0 --repo OWNER/REPO --body-file <正文文件>
```

第一条发行内评论，第二条发全局评论，输出都是评论链接。
