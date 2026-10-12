# 系统与网络配置

判据、命令与影响。需要 sudo 的一律由用户执行，本技能只给命令。

## 非特权 user namespace

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

变量共八个：`HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`（socks 地址）、`NO_PROXY`，各自大小写一份。本机 2026-10-12 探测：这些变量只出现在 agent 运行时进程里，指向 `127.0.0.1` 上的本地端口；`/etc/environment`、`/etc/profile.d/*`、`~/.bashrc`、`~/.profile` 里都搜不到，因此用户自己的交互终端没有代理。

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

全局身份缺失时提交报 `Please tell me who you are`。本机 2026-10-12：全局配置里没有身份，`/etc/gitconfig` 不存在，而仓库历史里有提交，说明身份由 agent 运行时注入；在 agent 之外的终端提交会失败。

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

本机 2026-10-12：`gh` 2.102.0 已登录账号 `Kielas520`，令牌存在 keyring，scopes 为 `gist, read:org, repo`，git 操作用 https 协议；全局配置里的凭据助手是 `!gh auth git-credential`。

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

本机 2026-10-12 用的就是这一条（注释写着 22 端口在本网络不可达）。

验证：`ssh -T git@github.com` 输出含 `successfully authenticated`，且 `ssh -G github.com` 显示的 `hostname` 是 `ssh.github.com`、`port` 是 `443`。
