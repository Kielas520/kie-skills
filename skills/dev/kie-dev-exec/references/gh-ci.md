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
gh api repos/{owner}/{repo}/actions/runs/<run-id>/artifacts --jq '.artifacts[] | {name, archive_download_url}'
gh run download <run-id> -n <artifact 名称> -D <下载目录>
gh run download <run-id> -p '<glob>'           # 按名称模式取多个产物
```

从运行页面的 Artifacts 段或上述 API 查询结果读取产物名称与下载链接。

## 发布验收评论与更新正文

```bash
gh pr comment <pr> --body-file <评论文件>
gh pr view <pr> --json body --jq .body > <body 文件>
gh pr edit <pr> --body-file <改好的 body 文件>
```

