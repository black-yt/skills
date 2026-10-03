# Claude Code 代理链与凭据迁移包

## 原始目标与完整组件职责

目标是复现另一个环境中 `cc_on && claude` 的工作方式，并使代理只在用户主动启用的终端中生效。原迁移包包含如下组件：

| 原组件 | 保留的职责 | 本 skill 中的组织 |
| --- | --- | --- |
| `install.sh` | 安装代理文件、保留已有配置、按需迁移认证与身份 | [scripts/claude_proxy/install.py](../scripts/claude_proxy/install.py)，默认只安装工具，凭据迁移须显式参数 |
| `proxy/cc_proxy.conf` | direct/chain、上游、目标、本地端口、bypass | [scripts/claude_proxy/cc_proxy.conf.example](../scripts/claude_proxy/cc_proxy.conf.example)，只有占位值 |
| `proxy/cc_env.sh` | `cc_on`、`cc_off`、`cc_status` 与环境快照恢复 | [scripts/claude_proxy/cc_env.sh](../scripts/claude_proxy/cc_env.sh) |
| `proxy/cc_proxy.sh` | start/stop/status、PID 文件、日志与端口诊断 | [scripts/claude_proxy/cc_proxy.py](../scripts/claude_proxy/cc_proxy.py)，精确 PID/starttime/argv 校验 |
| `proxy/cc_proxy_chain.py` | 本地 socket 经上游 CONNECT 透明中继 | [scripts/claude_proxy/cc_proxy_chain.py](../scripts/claude_proxy/cc_proxy_chain.py) |
| `claude/credentials.json` | 私有 OAuth access/refresh token | 不随 skill 分发，用户可在私有通道提供 |
| `claude/claude.json.seed` | 私有账号身份与 onboarding 字段 | 不分发值，下面保留字段 schema 与合并策略 |
| `claude/settings.json` | 偏好如 stable 更新通道和 dark 主题 | 作为可选 `--settings` 输入，目标已有则跳过 |

原安装会写 `~/.cc/`、`~/.claude/.credentials.json`、`~/.claude/settings.json`、`~/.claude.json`，不改 `.bashrc`。通用实现保留位置与行为边界，所有路径基于用户 home，支持非 root；不会在导入 skill 时自动运行。

## 网络链路与模式选择

```text
Claude
  → 127.0.0.1:[LOCAL_PORT]（本地 Python relay）
  → [UPSTREAM_CONNECT_HOST]:[UPSTREAM_PORT]（上游 HTTP CONNECT）
  → [EGRESS_PROXY_HOST]:[EGRESS_PORT]（真正出网的 HTTP 代理）
  → api.anthropic.com
```

- 原上游是某集群的 `.svc` 内部 DNS，带临时 Pod 标识；出集群后不能解析，Pod 重建后也可能失效。必须替换为当前可达的服务，不能把旧私人地址写入配置。
- 原端口样本：本地/目标 26751，上游 10805；这里只保留作为历史排查线索，配置使用用户选定且未占用的端口。

| 当前网络 | 选择 |
| --- | --- |
| 能直接访问 Anthropic | 不启用这套代理 |
| 能直接连接出网 HTTP 代理 | `CC_PROXY_MODE=direct`，不启动本地 relay |
| 只能访问允许 CONNECT 到出网代理的跳板 | `CC_PROXY_MODE=chain`，配置上游和目标 |
| 没有任一已验证路径 | 先修复网络，不安装凭据碰运气 |

无凭据连通性探针：

```bash
curl --proxy 'http://[EGRESS_PROXY_HOST]:[EGRESS_PORT]' --noproxy '' \
  --connect-timeout 5 --max-time 15 -sS -o /dev/null \
  -w 'http=%{http_code}\n' https://api.anthropic.com/v1/models
```

- 原记录把 401 解释为“代理通”、000 为“连不上”。保留这个快速信号，但需确认 401 来自目标服务而非网关；它不证明账号有效。000 还可能是 DNS、TLS、连接超时等原因，不自动意味着必须加跳板。
- 原始 relay 发出 `CONNECT [TARGET_HOST]:[TARGET_PORT] HTTP/1.1` 与 Host、Proxy-Connection headers，等上游 200 后双向传输；不是 TLS MITM，也不读取 OAuth token。
- 保留 30 秒上游连接/握手超时、64 KiB 数据块、剩余 header 后数据透传和并发连接处理。新版严格解析 HTTP 状态、限制 header 大小、正确处理半关闭，不记录客户端请求首行，避免 URL 泄漏。
- 仅绑定 `127.0.0.1`，不会创建公网开放代理。此实现接受 DNS/IPv4 主机，不支持 IPv6 字面地址；上游 CONNECT 认证和 TLS-to-proxy 也不在此小工具支持范围，必要时使用成熟代理软件，不随意添加凭据日志。

## 安装与启用

所有操作都是明确维护动作。默认安装不迁移账号、不写 shell 启动文件，也不会自动联网或启动代理：

```bash
python3 '[SKILL_DIR]/scripts/claude_proxy/install.py'
# 编辑安装生成的占位配置，填入已经验证的主机和端口。
source "$HOME/.cc/cc_env.sh"
cc_on
cc_status
claude
cc_off
```

- 原 `cc_proxy.sh start|stop|status` 对应 `python3 "$HOME/.cc/cc_proxy.py" start|stop|status`；无需创建额外 shell wrapper。
- 工具脚本更新前保留已有副本；已有 `cc_proxy.conf` 原样保留，新模板保存为 `.new`。本机旧配置必须先审查，不能盲 source 不可信文件。
- 如需每个新终端都有函数，可在用户授权后加入 `[ -f "$HOME/.cc/cc_env.sh" ] && . "$HOME/.cc/cc_env.sh"`；它只定义函数，不自动开代理。
- 安装器与 start/stop 共用文件锁，检测到该工具自己的存活 daemon 时拒绝覆盖运行脚本；先确认无人依赖并正常停服务，再升级。启动失败或 PID 元数据写入失败时回收本次子进程，避免留下无记录的 daemon。

## 影响范围与开关语义

| 操作/对象 | 范围与恢复 |
| --- | --- |
| `cc_on` 的大小写 HTTP/HTTPS、ALL_PROXY、NO_PROXY | 仅当前 shell 及其子进程；首次调用保存原值、unset/空值和 export 状态，重复 on 不覆盖快照 |
| `cc_off` | 恢复当前 shell 的快照；保留原版语义，停止**由本次 shell 启用的 chain 配置所引用**的共享 daemon，因此仍可能影响其他终端 |
| `cc_off --keep-daemon` | 恢复当前 shell 环境但保留共享 daemon，适合其他终端仍在使用时 |
| chain relay | 同用户多个终端可共享，不属于某一个 shell 的隔离环境 |
| 凭据与身份文件 | 当前用户全局、长期；新会话可能切到迁入账号，不只是当前 shell |

- 原 cc_on 只快照六个 HTTP/HTTPS/NO_PROXY 变量；新版也保存/临时移除 ALL_PROXY 大小写，避免旧 SOCKS 设置抢占路由，关闭后恢复。
- `CC_NO_PROXY` 默认保留进入前的 bypass；用户显式指定时才替换。原个人配置含 loopback、私网 CIDR 和内部域，公开模板不携带私有清单，各客户端是否支持 CIDR 应单独验证。
- 原 `cc_off` 会重新读取当前配置，如果开关期间改为 direct 可能漏停旧链。新版记住本 shell 开启时的模式/目录，减少这种歧义。
- stop 只操作经过 PID + starttime + 精确脚本 argv 校验的本工具进程；无法读取身份时不发送信号。不用 `pkill -f`，防止误杀编辑器、grep 或其他会话。
- 原 stop 先 TERM、最多等约 5 秒再 KILL；保留为显式 stop 的实现边界，只有允许中断该共享 relay 时才调用。孤立端口占用报告诊断，不自动杀占用者。
- PID 元数据和日志在 `~/.cc/cc_proxy_chain.pid`、`~/.cc/cc_proxy_chain.log`；限制访问且不记录认证内容。只有 PID 文件而无匹配进程不等于可以杀同 PID 的新进程。

## 可选的凭据和身份迁移

优先在新机器独立登录。如果确需迁移，先确认目标没有必须保留账号状态的活动会话，私有传输输入文件，再显式执行：

```bash
python3 '[SKILL_DIR]/scripts/claude_proxy/install.py' \
  --credentials '[PRIVATE_CREDENTIALS_JSON]' \
  --identity-seed '[PRIVATE_IDENTITY_SEED_JSON]' \
  --settings '[OPTIONAL_PRIVATE_SETTINGS_JSON]'
```

- 已有 `.credentials.json` 先做唯一备份，落盘为 0600，目录为用户私有；不要通过 `cat`、工具输出或 Git 传输认证内容。
- 已有 settings 保留；原偏好内容为 `{"autoUpdatesChannel":"stable","theme":"dark"}`，是否迁移由用户决定，不强制改主题。
- 身份 seed 的原顶层字段包括 `oauthAccount`、`userID`、`hasCompletedOnboarding`、`hasIdeOnboardingBeenShown`、`installMethod`、`autoUpdates`、`firstStartVersion`、`claudeCodeFirstTokenDate`、`opusProMigrationComplete`。
- `oauthAccount` 的原 schema 包含 accountUuid、emailAddress、organizationUuid、hasExtraUsageEnabled、billingType、accountCreatedAt、subscriptionCreatedAt、ccOnboardingFlags、claudeCodeTrialEndsAt、claudeCodeTrialDurationDays、seatTier、displayName、fullName、profileFetchedAt、organizationRole、workspaceRole、organizationName、organizationType、organizationRateLimitTier、userRateLimitTier。保留字段信息，绝不分发真实身份或订阅值。
- 原 installer 对身份采用 `cur.update(seed)`，seed 覆盖对应顶层键、保留其他本机项；嵌套 oauthAccount 作为整体替换，不是深度合并。新版继续明确此语义，先备份目标，未知 seed 顶层键拒绝导入。
- 原 JSON 损坏时重命名 `.corrupt` 并继续空配置；新版失败即停，保留损坏原件供诊断，避免静默丢掉本机配置。文件级原子替换不等于整个多文件安装是事务，失败时按记录恢复本次备份。
- access token 短期有效，refresh token 也会失效或被轮换。原文中具体过期日期是当时账号状态，不能作为复用期限；以当前认证返回为准。
- 多机器共享同一 refresh token 可能互相失效。遇到冲突在各自机器按当前官方方式独立登录，代理工具无需一并重装。
- 安装后可以在确认不用回退且用户允许时清理本次私有传输包；不默认删除用户原备份目录。凭据副本和备份同样敏感。

## 验收与失败处理

- `cc_status` 分别报告模式、daemon/端口状态和无凭据目标 HTTP 码；不把“进程存在”当作整条代理链通过。
- 用实际 Claude 会话验证认证和模型请求，再确认其他终端/agent 的环境与任务未受影响。
- 若 relay 启动失败、上游 CONNECT 非 200 或目标不可达，保留脱敏错误，恢复该 shell 原环境；不更换账号来修网络。
- 安装/升级失败先恢复本次备份的脚本和配置；认证回滚需避开活动写入，不能将已轮换的旧 refresh token 强行同步回所有机器。
