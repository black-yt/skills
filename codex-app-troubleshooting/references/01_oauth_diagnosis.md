# OAuth 登录失败的分层诊断

## 浏览器正常为什么仍会失败

```text
浏览器打开授权页面
  → 用户登录并同意
  → 本地回调交付授权结果
  → 发起登录的客户端/后端请求 token endpoint
  → 保存认证状态并显示登录成功
```

- 浏览器可能使用 Windows 系统代理，而 App、CLI、WSL 后端使用进程环境代理或另一套网络实现。
- `Login server error: Token exchange failed: error sending request for url (https://auth.openai.com/oauth/token)` 把调查重点指向发起 token 请求的进程及其网络；仅凭这句话无法断言具体是 DNS、连接、TLS 还是代理实现。
- 浏览器能访问官网，只验证了浏览器的网络链路；`curl` 成功也只验证该命令的网络栈和环境，不能替代实际 App 登录。
- WSL 终端存在不代表 token exchange 一定发生在 WSL；根据进程树、日志来源和目标后端环境确认。

## 证据与下一步

| 证据 | 下一步 | 不能据此断言 |
| --- | --- | --- |
| 代理端口 TCP 连接被拒绝 | 检查真实监听端口、监听地址与进程 | 账号失效 |
| 显式 HTTP 代理测试正常，App 仍失败 | 检查实际 App/后端环境、代理优先级和旧进程 | 必须换账号或重装 |
| `Could not resolve host` | 在发起请求的环境检查 DNS；区分本地解析和代理解析 | 一定是防火墙 |
| TLS 根证书/证书链错误 | 核实可信企业 CA 和当前版本的 CA 配置 | 可以使用 `-k` 或禁用验证 |
| HTTP 400/405 或其他响应 | 说明这次请求收到 HTTP 响应，继续确认来源及业务错误 | OAuth 已登录成功 |
| 代理网关 403 或站点策略拒绝 | 区分响应来源、企业策略和服务可达性 | 返回任意 HTTP 码就代表完整链路通过 |
| 授权码过期、重复使用或回调错误 | 修复回调后发起新的登录流程 | 重放旧 code 可以恢复 |

## 不携带凭据的网络探针

在已确认的 Linux/WSL 请求环境执行；先替换代理地址。Windows 原生测试可用 `curl.exe` 的同等参数。

```bash
curl --proxy 'http://[PROXY_HOST]:[PORT]' --noproxy '' \
  --connect-timeout 5 --max-time 20 \
  --output /dev/null --silent --show-error \
  --write-out 'http=%{http_code} connect=%{http_connect}\n' \
  'https://auth.openai.com/oauth/token'
```

- 使用无 token 的 GET，只测试通路；该端点通常不接受这种业务请求。不要提供用户授权码或 refresh token 作测试。
- `--noproxy ''` 只对该命令避免已有 bypass 设置绕开显式代理；不要因此清空用户全局 `NO_PROXY`。
- 不使用 `-v`、转储 headers 或 response body 收集不必要信息；需要深入诊断时先做针对性脱敏。
- 不用 `--fail` 把预期的端点方法错误混同为无法连接；但必须解释 HTTP 码含义，不能把它当认证成功。
- TLS 问题使用已验证的可信 CA。当前官方认证文档描述 `CODEX_CA_CERTIFICATE` 及 `SSL_CERT_FILE` fallback；先核对安装版本支持情况，不能无条件套到旧版 App。

## 保留 provider 与认证状态

- 自定义 OpenAI-compatible provider 可能用 `env_key`，也可能要求 OpenAI 认证；读取必要配置键而不是输出整个配置或 key。
- 不因为 OAuth 失败就清除 `model_provider`、`base_url`、环境 API key 或正在工作的中转配置。
- 不默认执行 `codex logout`：CLI 与其他客户端可能共享凭据，退出会影响其他会话。
- 只有用户要求更换认证模式且确认影响时才操作；`--device-auth` 也要先看当前 `codex login --help` 与官方适用条件，并不能修复不可达的 token endpoint。
- 完成标准是新的真实登录流程成功、目标账号/认证方式正确、用户正常启动能复现成功，以及原有任务保持运行。
