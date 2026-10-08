# kie-skills

个人日常开发使用的 Agent Skills 集合。技能在仓库里统一维护，通过 skills CLI 安装到用户目录，在多个项目和多个 Agent 中复用同一份内容。

## 部署

```bash
npx -y skills add Kielas520/kie-skills -g -y
```

`-g` 安装到用户目录，`-y` 跳过全部确认。CLI 自动检测本机已安装的 Agent，按各自的技能目录建立链接，安装记录写入 `~/.agents/.skill-lock.json`。

只列出仓库里的技能，不安装：

```bash
npx -y skills add Kielas520/kie-skills --list
```

更新已安装的技能：

```bash
npx skills update -g
```

## 目录布局

| 路径 | 用途 |
| --- | --- |
| `skills/<分类>/<技能名>/SKILL.md` | 技能元数据与操作说明，唯一发布源 |
| `skills/<分类>/<技能名>/references/` | 按需读取的参考资料 |
| `skills/<分类>/<技能名>/scripts/` | 技能执行所需的脚本 |
| `skills/<分类>/<技能名>/assets/` | 模板与静态资源 |
| `skills/<分类>/<技能名>/evals/` | 评估用例：`trigger-queries.json` 用于触发评估，`evals.json` 与 `files/` 用于输出质量评估 |

skills CLI 从 `skills/` 开始向下扫描，深度上限三层，`skills/<技能名>/` 与 `skills/<分类>/<技能名>/` 都能被发现。分类目录只影响源文件组织，技能 `name` 在整个仓库内唯一。每个技能目录独立安装，只携带自身运行所需内容，引用自身目录内的相对路径。

## 新增技能

1. 新建目录 `skills/<分类>/<技能名>/`，在其中写 `SKILL.md`。
2. frontmatter 至少包含 `name` 与 `description`，`name` 与目录名一致。
3. 正文写清前置条件、步骤、决策条件、输出要求与验证方法。篇幅较长的细节放进 `references/`，正文说明何时读取。
4. 写 `evals/trigger-queries.json`，正负例查询各约十条；需要评估输出质量时再写 `evals/evals.json` 与 `evals/files/` 下的输入文件。
5. 校验：按下一节把技能接入本地会话，让 Agent 读取 `skill://<技能名>`，能取到内容即解析通过。

完整的编写流程与两个评估的操作见 `skills/base/kie-skill-dev`。

字段约束与格式细节以 [Agent Skills Specification](https://agentskills.io/specification) 为准。

## 评估

触发评估与输出质量评估都在仓库内跑，脚本随 `kie-skill-dev` 提供，沙箱建在 `~/project/test/` 下，结果写在仓库的 `.scratch/` 里：

```bash
python3 skills/base/kie-skill-dev/scripts/trigger_eval.py <技能名>
python3 skills/base/kie-skill-dev/scripts/quality_eval.py <技能名> --iteration 1
```

触发评估默认 `--runs 1` 粗筛，只对结果翻转的用例补 `--runs 3`。`kie-skill-dev` 规定两道确认：写完技能要总结改动并等用户同意才进入评估，评估走完才进入提交与部署。

## 本地维护

技能位于分类目录下，Agent 只发现技能根目录下一层的 `<根>/<技能名>/SKILL.md`，分类层不参与扫描。改了技能要让它立刻对仓库内的会话生效，把技能链接进 `.agents/skills/`：

```bash
mkdir -p .agents/skills
ln -s ../../skills/<分类>/<技能名> .agents/skills/<技能名>
```

`.agents/skills/` 只服务于本地维护，已加入忽略规则。
