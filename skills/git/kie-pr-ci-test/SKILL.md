---
name: kie-pr-ci-test
description: |
  PR 建好、CI 跑完之后的远端产物验收：先看 PR 内 CI 的基础检查是否通过，再拉 CI 构建产物按工单验收标准测一遍（缺陷单同样做有问题版本与当前产物的对照实验），需求单给出 CI 产物链接，缺陷单给出 CI 产物链接与有问题版本的 tag，无工单只给 CI 产物链接；随后生成测试报告评论，用户确认后发布，并把远端结果追加进 PR body 的测试报告段。当用户说「PR 的 CI 跑完了，测一下」「CI 产物验一下」「远端产物测一遍」「给 PR 写测试报告评论」「CI 绿了，可以验收了吗」「这个 PR 的产物链接给我」，或 PR 已推送、CI 触发完成、准备交给评审者时使用，即使用户没有说出「CI」二字。不适用：本机分支的推送前测试与测试报告（用 kie-dev-test）；起草 PR body 或发起 PR（用 kie-pr-start）；处理 PR 评审意见并回复（用 kie-pr-review-fix）；CI 失败的日志分析与根因修复。
license: MIT
compatibility: 需要 git 与已登录的 gh CLI；拉取产物需要 GitHub Actions 的读取权限。
metadata:
  author: Kielas
  version: "0.1.0"
---

# PR 远端产物验收

PR 推送之后验收 CI 构建出来的远端产物，产出测试报告评论并更新 PR body。测试内容与 `kie-dev-test` 同源，差别在测试对象是本机产物还是 CI 产物。

## 前置条件

- PR 已经建立并推送，CI 已经跑完。还在跑就先等，或用 `gh pr checks <pr> --watch` 等结束。
- 本地测试已经做过，报告在 `~/project/<项目名称>/.idea/test-report.md`。
- 工单内容与缺陷单里的有问题版本信息可以取到。

## 步骤 1：检查 PR 内的 CI 基础

```bash
gh pr checks <pr>
gh pr view <pr> --json statusCheckRollup \
  --jq '.statusCheckRollup[] | {name, status, conclusion, detailsUrl}'
```

检查项有失败或取消的，把失败项与链接报给用户，由用户决定先修还是继续验。命令清单见 [references/gh-ci.md](references/gh-ci.md)。

## 步骤 2：取远端产物

```bash
gh run list --branch <分支名> --json databaseId,name,status,conclusion,url -L 10
gh run download <run-id> -n <artifact 名称> -D <下载目录>
```

按工单类型确定要给出的链接：

| 工单 | 给什么 |
| --- | --- |
| 需求单 | CI 产物链接 |
| 缺陷单 | CI 产物链接与有问题版本的 tag |
| 无工单 | 只有 CI 产物链接 |

## 步骤 3：按工单验收

验收标准与对照实验的做法与 `kie-dev-test` 一致，测试对象换成下载下来的 CI 产物：

1. 逐条过工单的验收标准，本机能跑的都在远端产物上跑一遍。
2. 缺陷单做对照实验：有问题版本与 CI 产物的结果并列，环境对不齐的部分写明差异。
3. 远端产物跑不起来（缺少依赖、平台不符、需要真实设备）时，把缺什么前提写清楚，不拿 CI 绿灯代替验收。

## 步骤 4：报告、评论与 PR body

报告结构读 [references/测试报告模板.md](references/测试报告模板.md)，与本地报告同一套结构，远端部分多出 CI 运行链接、产物链接与有问题版本 tag。

按顺序推进，每一步都等用户确认：

1. 先生成测试报告给用户看。
2. 用户看过没问题，起草 PR 评论（说明测了哪些验收标准、结论、产物链接）。
3. 用户确认评论内容后才发布：

```bash
gh pr comment <pr> --body-file <评论文件>
```

4. 更新 PR body 的测试报告段：先取出当前 body，在原本地测试结果下面追加远端结果，本地部分不动，改完的文件交用户确认后再写回：

```bash
gh pr view <pr> --json body --jq .body > <body 文件>
gh pr edit <pr> --body-file <改好的 body 文件>
```

同时把远端结果写进 `~/project/<项目名称>/.idea/test-report.md` 的「远端 CI 结果」段。

## 交付

```text
━━━ PR 远端验收完成 ━━━
PR: {链接}
CI: {通过数}/{总数}
产物: {CI 产物链接}
有问题版本: {tag，缺陷单才写}
报告: ~/project/<项目名称>/.idea/test-report.md
评论: {已发布 / 待用户确认}
PR body: {已追加远端结果 / 无需变更}
```

## 硬性约束

- 不擅自发布评论、不擅自改 PR body、不擅自推送提交。
- 远端产物要真下载下来跑，脚本与结果都来自实际执行。
- CI 检查失败时先报给用户，不自行修改代码绕过检查。

## Gotchas

- CI 通过只说明构建成功，验收标准仍要逐条过，绿灯不等于交付合格。
- PR body 的本地测试结果保留，远端结果追加在下面，两者不互相覆盖。
- 本地报告与远端报告同结构，远端多一段 CI 产物链接与有问题版本 tag。
- 本机 `gh` 为 2.46.0，`gh pr checks` 不支持 `--json`，结构化状态用 `gh pr view --json statusCheckRollup` 取。
- 评论与 body 都先起草给用户看，用户确认之前不发布。
