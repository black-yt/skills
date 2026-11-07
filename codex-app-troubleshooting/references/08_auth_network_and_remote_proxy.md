# 官方登录、403、Windows socket 与 SSH 反向代理

## 保留历史解释，同时纠正推断边界

原记录在 WSL/远端 Linux 登录时遇到 `Token exchange failed: token endpoint returned status 403 Forbidden`，曾把原因归为“WSL localhost 与 Windows localhost 不同，回调无法接收”，并通过 Windows CLI 登录再迁移缓存恢复。

- **保留有效操作经验**：Windows 原生 CLI 的浏览器回调可与 WSL/远端不同；在同账号的可信环境中迁移有效认证缓存，确实可能绕开目标机器的交互登录困难。
- **修正因果判断**：收到 token endpoint 的 HTTP 403 不足以证明 callback 不可达。需要区分代理网关、服务策略、请求错误和授权阶段；回调未接收到授权码与 token endpoint 已响应是不同证据。
- 原始问题线索：[openai/codex issue 2414](https://github.com/openai/codex/issues/2414)。不要把 issue 中某个环境的结论当通用根因。
- 看到 `oops an error occurred operation timed out` 可在检查网络与服务状态后发起一次新的登录尝试；不能无限重试或复用已使用的授权码。

## Windows socket 错误 10013

```text
Error logging in: 以一种访问权限不允许的方式做了一个访问套接字的尝试。
(os error 10013)
```

先查日志中实际 bind 地址与端口、端口占用、保留端口、终端权限和安全软件策略：

```powershell
Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess
netsh interface ipv4 show excludedportrange protocol=tcp
netsh interface ipv6 show excludedportrange protocol=tcp
```

- 原记录用过管理员 PowerShell 的 `net stop winnat`、`net start winnat` 后重试登录；完整保留该恢复手段，但它会中断 NAT、容器和部分 WSL 网络，不是默认第一步。
- 只有确认 WinNAT/保留端口为原因、用户允许相应中断且有恢复计划时才执行；严格不中断对话时保留此选项不执行。
- 不关闭全局防火墙、不随意清除保留端口、不把所有 10013 都归因于 WinNAT。可优先调查当前 CLI 支持的 device login 或合适的回调方案。

### WSL 已监听，但 Windows 浏览器回调被拒绝

- **先确认登录仍在等待**：浏览器报 `127.0.0.1` / `ERR_CONNECTION_REFUSED` 时，检查发起登录的 CLI 与实际回调端口。没有监听也可能只是原流程已结束；不要先断言 WSL 转发故障。
- **以实际端口为准**：CLI `0.167.0` 的[匹配源码](https://github.com/openai/codex/blob/rust-v0.167.0/codex-rs/login/src/server.rs)使用默认 `1455`，并有已注册的备用 `1457`。两者可能同时落入一个保留范围；这些值是版本样本，不是任意改 OAuth redirect URI 的依据。
- **对照两侧通路**：以下以已确认的 `1455` 为例；只请求根路径，不携带授权码：

```bash
# 在实际运行 CLI 的 WSL 中执行。
ss -ltnp '( sport = :1455 )'
curl --noproxy '*' --connect-timeout 2 --max-time 3 \
  --silent --show-error --output /dev/null \
  --write-out 'http=%{http_code}\n' http://127.0.0.1:1455/
```

```powershell
# 在 Windows 中执行，与 WSL 结果对照。
curl.exe --noproxy '*' --connect-timeout 2 --max-time 3 `
  --silent --show-error --output NUL `
  --write-out 'http=%{http_code}' http://127.0.0.1:1455/
Get-NetTCPConnection -State Listen -LocalPort 1455 -ErrorAction SilentlyContinue |
    Select-Object LocalAddress, LocalPort, OwningProcess
```

- **解释探针**：WSL 根路径收到 `404` 说明该次连接到达 HTTP 服务，不代表登录成功。若 WSL 有监听且可达、Windows 连接失败，再结合本篇前面的 IPv4/IPv6 保留端口查询检查宿主机；不能只检查 Linux 权限。
- **必要时验证 Windows bind**：仅在已确认 Windows 无其他进程占用该端口后，临时创建本机监听并立即关闭；`10013` 与覆盖该端口的 exclusion 范围一起，才构成宿主机保留端口问题的证据：

```powershell
$callbackPort = 1455
$callbackListener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $callbackPort)
try {
    $callbackListener.Start()
    'Temporary bind succeeded'
} catch {
    $_.Exception.GetBaseException().Message
} finally {
    $callbackListener.Stop()
}
```

- **WinNAT 恢复条件**：两侧探针与保留端口证据吻合、用户已允许网络中断且有恢复计划时，才考虑在管理员 PowerShell 顺序执行 `net stop winnat`、`net start winnat`，随后复查保留范围与两侧通路。重启可能改变动态保留端口，但不保证释放目标端口；若停止后启动失败，先恢复服务，不继续登录试错。不要用重启整个 WSL、关闭防火墙或批量删除 exclusion 代替定位。
- **继续分层验收**：Windows 回调恢复后若变成 `token_exchange_failed`，转到 [01](01_oauth_diagnosis.md) 和 [02](02_proxy_and_launch.md) 检查发起 token 请求的 WSL 进程。修复其代理后生成新的登录流程，最终以 `codex login status` 显示 `Logged in using ChatGPT` 验收，不能重放旧回调中的 code。
- **撤回临时尝试**：原生回调恢复后，移除本次不再需要的临时转发与等待登录进程；只停止身份已核实的本次进程，不触碰用户原有任务。

## 可信机器间迁移认证

1. 在有浏览器的可信机器上用用户选定方式完成登录；Windows npm CLI 需要对应 Node/npm，缺少时从 [Node.js 官方](https://nodejs.org/en/download) 按环境安装。
2. 核对 `codex login status`、实际 Codex home 和凭据存储方式。缓存可能是 `auth.json`，也可能在 OS keyring 中，不能保证登录后一定生成可复制 JSON。
3. 只有确需迁移且已有授权时，将文件通过 SSH/scp 等私有通道传到同一用户控制的目标；先备份目标，收紧目录/文件权限，避免打印文件内容。
4. 别把一套 refresh token 同时复制给多台活跃客户端作为长期同步方式；刷新轮换可能使另一台出现 `refresh_token_reused`。优先独立登录，原文件备份也当凭据保护。
5. 验证目标客户端实际认证成功，再按用户授权清理本次临时传输副本；不删远端原有会话或认证备份。

原记录说“必须注释掉 `model_provider` 才能用 auth.json”。更准确的判断是当前 provider 的认证声明：

- `requires_openai_auth=true` 使用 OpenAI 认证；当前官方说明在此模式下忽略 `env_key`。
- `env_key` 指向 provider 所需的环境变量名称，值不是 key 本身；这条路径与 ChatGPT OAuth 缓存不同。
- 不设置 OpenAI 认证也不提供 `env_key` 的本地 provider，可能不需要认证。
- 因此不能为修复官方登录无条件删除 provider；先确认用户想使用的服务。需要切换时做局部、可回滚的配置选择。

## 本地 Windows 与 WSL 代理

Windows 原生 PowerShell 的进程级示例：

```powershell
$env:HTTP_PROXY = 'http://127.0.0.1:[PORT]'
$env:HTTPS_PROXY = 'http://127.0.0.1:[PORT]'
curl.exe --connect-timeout 5 --max-time 20 -sS -o NUL -w 'http=%{http_code}' https://api.openai.com
```

WSL2 NAT 的进程级示例：

```bash
ip -4 route show default
export HTTP_PROXY='http://[VERIFIED_WINDOWS_HOST]:[PORT]'
export HTTPS_PROXY="$HTTP_PROXY"
curl --connect-timeout 5 --max-time 20 -sS -o /dev/null -w 'http=%{http_code}\n' https://api.openai.com
```

- 原案例端口出现过 7890 和 7897，两者都不是固定要求。
- 原文要求同时开 Clash TUN 和允许 LAN；**显式 HTTP 代理不以 TUN 为必需条件**。是否需要 TUN 取决于走哪条网络链，WSL 到 Windows 监听则要核对 LAN、监听地址与防火墙。
- `api.openai.com` 探针与 `auth.openai.com/oauth/token` 不是同一服务路径；网络连通、HTTP 状态和真实登录分别验证。
- 注意 PowerShell 中 `curl` 在一些版本是别名，明确使用 `curl.exe` 避免参数语义不同。

## 让远端 Linux 经本地 Clash 出网

在**能够访问 Windows 本地代理的 SSH 客户端**上建立远程转发：

```bash
ssh -o ExitOnForwardFailure=yes \
  -R 127.0.0.1:[REMOTE_PROXY_PORT]:127.0.0.1:[LOCAL_PROXY_PORT] '[HOST]'
```

对应 SSH 配置示例：

```sshconfig
Host [HOST]
    HostName [SSH_ENDPOINT]
    User [SSH_USER]
    RemoteForward 127.0.0.1:[REMOTE_PROXY_PORT] 127.0.0.1:[LOCAL_PROXY_PORT]
    ExitOnForwardFailure yes
```

- 右侧地址由本地 SSH 客户端访问，左侧监听在远端。Windows SSH 可访问 Windows loopback；如果在 WSL 里运行 SSH 且代理在 Windows NAT 主机，需要把右侧换成已验证的主机地址。
- 原例用了 `ssh -CAXY`，配置里有 Compression、ForwardAgent、ForwardX11、ForwardX11Trusted；这些不是 HTTP 反向代理的必需项。尤其 agent/X11 forwarding 会扩大能力范围，不默认启用。
- 远端端口冲突或服务端拒绝 forwarding 时停止，不更改 GatewayPorts 来把代理暴露到所有网卡。
- SSH 连接关闭会使代理消失；依赖该通路的远端 agent 在重试/重连时可能失败，要保留隧道或改用用户批准的长期方案。

在该远端会话导出 HTTP/mixed 代理：

```bash
export HTTP_PROXY='http://127.0.0.1:[REMOTE_PROXY_PORT]'
export HTTPS_PROXY="$HTTP_PROXY"
export http_proxy="$HTTP_PROXY"
export https_proxy="$HTTPS_PROXY"
```

仅当代理实际支持 SOCKS 时，原记录还会设置：

```bash
export ALL_PROXY='socks5h://127.0.0.1:[REMOTE_PROXY_PORT]'
export all_proxy="$ALL_PROXY"
```

原值是 `socks5://`；`socks5h://` 让支持该 scheme 的客户端交给代理解析 DNS。不是所有客户端都支持 SOCKS/CIDR bypass，必须按实际工具验证；不要把 HTTP-only 监听当 SOCKS。

恢复时使用进入前的代理快照，不能一律 `unset` 覆盖用户原环境；内网 `NO_PROXY` 也应保留。
