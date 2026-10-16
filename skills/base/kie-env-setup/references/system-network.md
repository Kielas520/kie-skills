# 系统与网络配置

判据、命令与影响。需要 sudo 的一律由用户执行，本技能只给命令。

## 非特权 user namespace

需要跑技能评估（kie-skill-dev 的 `trigger_eval.py` 与 `quality_eval.py`）时才检查这一项，日常环境体检只报现状，不列为待补齐的差异；探测时带 `--eval` 才计入待确认项。

判据：

```bash
cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns   # 1 表示受限
unshare -rm true                                            # 受限时报 write failed /proc/self/uid_map: Operation not permitted
```

影响：`kie-skill-dev` 的 `trigger_eval.py` 与 `quality_eval.py` 用 `unshare -rm bash -c 'mount -t tmpfs ...'` 遮蔽真实仓库、用户层技能目录与测试工作区里的其他沙箱，受限时两个脚本都以退出码 2 结束（隔离条件不成立），评估跑不起来。

修复（需 root 与交互密码，用户执行）：

```bash
sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
sudo tee /etc/sysctl.d/99-userns.conf <<'EOF'
kernel.apparmor_restrict_unprivileged_userns=0
EOF
sudo sysctl --system
```

第一条立即生效、重启后失效；第二与第三条让它持久化。回退方式是删除 `/etc/sysctl.d/99-userns.conf` 后重新加载，或把值改回 1。

代价要说清楚并交给用户决定：这个值置 0 之后任何进程都能创建 user namespace，隔离强度下降；只在需要跑评估的机器上临时放开的做法是只执行第一条。

验证：`unshare -rm true` 无输出且退出码 0。

## 代理

判据：`env | grep -i proxy` 看变量，再看端口能不能连上。

变量共八个：`HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`（socks 地址）、`NO_PROXY`，各自大小写一份。是否设置、指向哪个地址与端口，取本次探测输出，不套用参考文件与历史会话里的取值。

交互终端需要代理时，由用户把下面几行写进 `~/.bashrc`，取值换成本次探测到的地址：

```
export HTTP_PROXY=http://<地址>:<端口>
export HTTPS_PROXY=$HTTP_PROXY
export ALL_PROXY=socks://<地址>:<端口>
export NO_PROXY=<探测到的内网范围>
```

落点二选一：交互 shell 用 `~/.bashrc`；systemd 用户会话用 `~/.config/environment.d/proxy.conf`，写成 `HTTP_PROXY=http://<地址>:<端口>`（该文件里不带 `export`）。

验证：另开一个终端执行 `env | grep -i proxy`，或 `curl -s -o /dev/null -w '%{http_code}' https://api.github.com` 输出 200。

单域名返回 403 不能判定代理失效：`crates.io` 的 API 不带 User-Agent 就返回 403，带上 `-A 'cargo <版本>'` 后正常。

## git 身份

```bash
git var GIT_AUTHOR_IDENT           # 实际生效的身份，身份来自环境变量注入时也能显示
git config --global user.name
git config --global user.email
```

全局身份缺失时提交报 `Please tell me who you are`。全局配置里没有身份不代表提交一定失败：身份也可能由 agent 运行时注入，也可能完全没有，以 `git var GIT_AUTHOR_IDENT` 的本次输出为准，不预设注入存在。

写入的值由用户提供，不套用历史提交里的姓名与邮箱：

```bash
git config --global user.name "<用户给的姓名>"
git config --global user.email "<用户给的邮箱>"
```

验证：两条 `git config --global` 查询都有输出，且 `git var GIT_AUTHOR_IDENT` 给出的身份与用户给的一致。

## gh 登录与凭据助手

```bash
gh auth status
git config --global credential.https://github.com.helper
```

登录账号、令牌存放位置、scopes 与 git 协议取 `gh auth status` 的本次输出；凭据助手取 `git config --global credential.https://github.com.helper` 的本次输出，不在这里记本机取值。

未登录时 `gh auth login`；令牌缺权限时 `gh auth refresh -s <scope>`。两条都是交互式的，由用户执行。

验证：`gh auth status` 输出含 `Logged in to github.com`。

## SSH 连通

```bash
ssh -T git@github.com                              # 输出含 successfully authenticated 即通
ssh -G github.com | grep -E '^(hostname|port) '    # 实际使用的主机与端口
timeout 5 bash -c 'exec 3<>/dev/tcp/github.com/22' # 22 端口是否可达
```

22 端口不可达时改用 GitHub 的 443 端点，`~/.ssh/config` 段落为：

```
Host github.com
  HostName ssh.github.com
  Port 443
  User git
  IdentityFile ~/.ssh/<私钥文件>
```

本机用的是直连还是 443 端点，以 `ssh -G github.com` 的本次输出为准。

验证：`ssh -T git@github.com` 输出含 `successfully authenticated`；`ssh -G github.com` 显示的 hostname 与 port 与本次实际使用的链路一致（直连是 `github.com` + `22`，走 443 端点时是 `ssh.github.com` + `443`）。
