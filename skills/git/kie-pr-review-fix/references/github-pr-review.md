# PR 评审相关的 GitHub 命令

## 拉取未解决的 review threads

只有 GraphQL 能拿到 `isResolved` 状态。首轮 `after` 传 `null`，`hasNextPage` 为 true 时用 `endCursor` 继续拉，直到取完全部 threads。

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

## 回复行内评论

```bash
gh api repos/OWNER/REPO/pulls/0/comments \
  -f body='<回复内容>' -F in_reply_to=<评论的 databaseId>
```

`databaseId` 来自 threads 查询里 `comments.nodes` 的 `databaseId` 字段。

## 回复会话区意见

```bash
gh pr comment 0 --body-file <回复文件>
```

## 解决 thread

```bash
gh api graphql -f query='
mutation { resolveReviewThread(input: {threadId: "THREAD_ID"}) { thread { isResolved } } }'
```

## 评审状态、CI 与 body

```bash
gh pr view 0 --json reviewDecision,mergeable,mergeStateStatus
gh pr view 0 --json statusCheckRollup \
  --jq '.statusCheckRollup[] | {name, status, conclusion, detailsUrl}'
gh pr view 0 --json body --jq .body
gh pr edit 0 --body-file <改好的 body 文件>
```

本机 `gh` 为 2.46.0，`gh pr checks` 不支持 `--json`，结构化状态用 `gh pr view --json statusCheckRollup` 取。
