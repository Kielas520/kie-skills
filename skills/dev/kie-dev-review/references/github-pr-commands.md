# 评审 PR 的只读命令

将 `OWNER/REPO` 和 `0` 换成目标仓库与 PR 编号。

```bash
gh pr view 0 --repo OWNER/REPO --json number,url,title,author,body,baseRefName,headRefName,headRefOid,commits,files,reviewDecision
gh pr diff 0 --repo OWNER/REPO
gh api --paginate repos/OWNER/REPO/pulls/0/reviews
```

未解决的 threads 使用 GraphQL 查询；按 `pageInfo.hasNextPage` 与 `endCursor` 分页取完，线程内评论也须分页取完：

```bash
gh api graphql -f query='
{
  repository(owner: "OWNER", name: "REPO") {
    pullRequest(number: 0) {
      reviewThreads(first: 50, after: null) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved isOutdated path line
          comments(first: 20) {
            pageInfo { hasNextPage endCursor }
            nodes { author { login } body }
          }
        }
      }
    }
  }
}'
```

PR 的 head 可通过 `git fetch origin pull/0/head` 获取。需要新工作区时先核对已有 worktree 及目标路径，在该工作的分支代码目录安全创建 detached worktree；不得覆盖已有工作区。`git diff` 的 `+++ b/<path>` 与 `@@ -a,b +c,d @@` 指示 head 的文件和行号；行内评论须落在有效改动行。
