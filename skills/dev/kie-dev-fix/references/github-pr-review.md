# PR 评审相关的 GitHub 命令

## 拉取未解决的 review threads

只有 GraphQL 能拿到 `isResolved` 状态。首轮 `after` 传 `null`，按 `hasNextPage` 与 `endCursor` 分页取完全部 threads；线程内评论也要分页取完。

```bash
gh api graphql -f query='
{
  repository(owner: "OWNER", name: "REPO") {
    pullRequest(number: 0) {
      reviewThreads(first: 50, after: null) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          comments(first: 20) {
            pageInfo { hasNextPage endCursor }
            nodes { author { login } body createdAt databaseId }
          }
        }
      }
    }
  }
}'
```

## 拉取 review body

```bash
gh api --paginate repos/OWNER/REPO/pulls/0/reviews \
  --jq '.[] | select(.body != "") | {id, user: .user.login, state, body}'
```

返回历史全量。同一个评审者按最新一条 review 的 state 判定，`DISMISSED` 跳过。

## 拉取会话区 issue comments

```bash
gh api --paginate repos/OWNER/REPO/issues/0/comments \
  --jq '.[] | {user: .user.login, body}'
```

