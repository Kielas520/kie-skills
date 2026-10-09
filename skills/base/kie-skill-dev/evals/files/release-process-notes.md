# 集中式发版流程（素材）

本文件是写技能用的素材，里面的命令只作正文与用例的写法参考，不要在会话里执行。

内部 CLI 仓的发版走 org 仓库 `.github` 的集中式链路，动作都在远端：

1. 在 `wuji-technology/.github` 触发集中式发版，输入仓库与版本：

   ```bash
   gh workflow run centralized-release.yml --repo wuji-technology/.github \
     -f repositories='wuji-cli-dev=2026.10.8:CHANGELOG.md:public/CHANGELOG.md' \
     -f release_date=2026-10-08
   ```

   它创建 `release/v2026.10.8` 分支与发版 PR（带 `auto-release` 标签），并向飞书发通知卡片。

2. 审发版 PR 的两份 CHANGELOG 段落与版本号文件，合入 `main`：

   ```bash
   gh pr merge <编号> --repo wuji-technology/wuji-cli-dev --squash
   ```

3. 合入后 `auto-release-on-pr.yml` 推 tag，`release.yml` 构建产物并创建 GitHub Release。

4. 同步公开仓：

   ```bash
   gh workflow run sync-public.yml --repo wuji-technology/wuji-cli-dev
   gh workflow run sync-release.yml --repo wuji-technology/wuji-cli-dev
   ```

版本号统一带 `v` 前缀；`.release.yml` 列出的版本号文件与两份 CHANGELOG 一起更新，任一规则不命中就整链失败。
