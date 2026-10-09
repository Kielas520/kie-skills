# PR 与 CI 命令

## 定位 PR

```bash
gh pr view --json number,url,headRefName,baseRefName,state
gh pr view <pr> --json body --jq .body
```

## CI 状态

```bash
gh pr checks <pr>                              # 全部检查项与状态，纯文本
gh pr checks <pr> --watch --interval 30        # 等检查跑完
gh pr view <pr> --json statusCheckRollup \
  --jq '.statusCheckRollup[] | {name, status, conclusion, detailsUrl}'
```

## 远端运行与产物

```bash
gh run list --branch <分支名> --json databaseId,name,status,conclusion,url -L 10
gh run view <run-id> --json jobs --jq '.jobs[] | {name, conclusion, url}'
gh run download <run-id> -n <artifact 名称> -D <下载目录>
gh run download <run-id> -p '<glob>'           # 按名称模式取多个产物
```

产物名称从 `gh run view <run-id> --json jobs` 或运行页面的 Artifacts 段读取。

## 发布评论与更新 PR body

```bash
gh pr comment <pr> --body-file <评论文件>
gh pr view <pr> --json body --jq .body > <body 文件>
gh pr edit <pr> --body-file <改好的 body 文件>
```

`gh pr edit` 只改传入的字段，用 `--body-file` 更新正文不会动标题与 reviewer。

## 版本差异

本机 `gh` 为 2.46.0，`gh pr checks` 不支持 `--json`，结构化状态用 `gh pr view --json statusCheckRollup` 取。
