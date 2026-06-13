# Login OIDC Session

## 目录

- [访问位置](#访问位置)
- [凭据与文件权限](#凭据与文件权限)
- [OIDC Authorization Code Flow](#oidc-authorization-code-flow)
- [Token 刷新与失败处理](#token-刷新与失败处理)
- [安全边界](#安全边界)

## 访问位置

lab-cluster-1 的集群管理网站入口是：

```text
https://h.pjlab.org.cn/
```

该网站通常只在特定网络内可达。先判断执行位置，不要把网络不可达误判为登录脚本错误：

```bash
curl -I --max-time 10 "https://h.pjlab.org.cn/"
```

通用判断：

- 本地电脑/WSL 访问超时：可能是 VPN、内网路由或 DNS 问题。
- 开发机可访问：把网页登录、API 探索和 token 刷新放在开发机或 CPU worker。
- CPU rjob 可访问：适合周期性只读巡检和生成报告。
- GPU job 通常不适合做网页登录、外部通知或 API 探索；GPU job 应专注训练/部署，把监控和通知交给 CPU 侧。

自动化前先在浏览器手动登录一次，确认：

- 登录入口 URL。
- 是否跳转到统一身份认证页面。
- 是否使用 OIDC/OAuth2。
- 登录成功后的回调路径。
- 浏览器 Network 面板中真正调用的 API 路径和请求头。

## 凭据与文件权限

不要把账号密码、token、cookie 写入仓库、`.bashrc`、命令行参数、日志或最终回复。推荐放在当前项目自己的 gitignored `.secrets/` 目录，并收紧权限：

```bash
mkdir -p ".secrets"
chmod 700 ".secrets"
chmod 600 ".secrets/hpjlab_login.json"
```

示例格式：

```json
{
  "username": "[USERNAME]",
  "password": "[PASSWORD]"
}
```

token 文件示例：

```text
.secrets/hpjlab_oidc_token.json
.secrets/hpjlab_cookiejar.txt
```

规则：

- 打印日志时只输出 token 是否存在、过期时间、刷新是否成功，不打印 token 值。
- 报错时清洗 URL query、Authorization header、Cookie header 和 form password。
- secret 文件不随项目提交；如果必须说明路径，用 `[SECRET_DIR]` 占位。

## OIDC Authorization Code Flow

如果 password grant 返回 `unauthorized_client` 或平台没有启用密码授权，不要硬试。浏览器网页登录常见可行方式是 OIDC authorization code flow。

`h.pjlab.org.cn` 的关键 OIDC 配置：

```text
discovery:
https://h.pjlab.org.cn/kapi/auth/.well-known/openid-configuration?tenant=ailab

authorization_endpoint:
https://h.pjlab.org.cn/kapi/auth/auth

token_endpoint:
https://h.pjlab.org.cn/kapi/auth/token

client_id:
kubebrain

client_secret:
ooxx

redirect_uri:
https://h.pjlab.org.cn/oidc-callback

scope:
openid profile email
```

流程：

1. 创建 cookie jar，保持同一个 HTTP session。
2. 请求 discovery URL，读取 `authorization_endpoint` 和 `token_endpoint`。
3. 构造授权 URL，参数包含 `client_id`、`redirect_uri`、`response_type=code`、`scope`、`state`、`nonce`。
4. 访问授权 URL，跟随跳转到登录表单。
5. 提交用户名和密码。字段名以实际登录表单为准，不要猜。
6. 跟随跳转，最终从 redirect URL 中解析 `code`。
7. 调 token endpoint，用 `code` 换 `access_token`、`refresh_token` 和过期时间。
8. 保存 token 文件，权限设置为 `600`。

伪代码结构：

```python
from http.cookiejar import MozillaCookieJar
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import build_opener, HTTPCookieProcessor

cookiejar = MozillaCookieJar(".secrets/hpjlab_cookiejar.txt")
opener = build_opener(HTTPCookieProcessor(cookiejar))

# 1. discovery
# 2. build authorization URL
# 3. open login page with same opener
# 4. submit login form
# 5. follow redirects and extract code
# 6. exchange code at token endpoint
# 7. save token and cookiejar
```

如果页面依赖复杂 JavaScript、验证码或多因子认证，用 Playwright 打开真实浏览器更稳。仍然要遵守同样安全边界：不要截图或打印密码、token 和 cookie。

## Token 刷新与失败处理

后续任务优先 refresh token：

```text
grant_type=refresh_token
refresh_token=[REFRESH_TOKEN]
client_id=[CLIENT_ID]
client_secret=[CLIENT_SECRET]
```

处理顺序：

1. token 文件存在且 access token 未过期：直接使用。
2. access token 过期但 refresh token 存在：刷新 token。
3. refresh 失败：清理旧 token 或标记失效，再重新走网页登录。
4. 重新登录仍失败：停止自动化，报告登录失败原因，不要反复提交密码。

常见失败：

| 现象 | 含义 | 处理 |
| --- | --- | --- |
| `unauthorized_client` | 当前 client 不允许该授权方式，常见于 password grant | 改走 authorization code flow，或核对平台支持的 grant type |
| redirect URL 没有 `code` | 登录没成功或被多因子/验证码/权限页拦截 | 用真实浏览器检查跳转链和页面提示 |
| refresh token 失效 | token 被撤销、过期或 client 信息变化 | 删除旧 token，重新网页登录 |
| 401/403 | access token 缺失、过期或权限不足 | 刷新 token；仍失败则核对用户权限和 API scope |

## 安全边界

- 只访问自己有权限查看的页面和 API。
- 不要绕过 SSO、OIDC、验证码、多因子认证或权限检查。
- 本 skill 可以记录 `h.pjlab.org.cn` 的固定入口、OIDC endpoint 和只读监控 API，因为这些是技能本身的操作对象；不要记录带 `code`、`state`、token、cookie、账号或临时查询参数的敏感 URL。
- 不要把 token、cookie、用户名、密码、真实节点名或个人运行状态写入公开 skill、README 或 issue。
- 自动化脚本默认只读；如果页面 API 支持写操作，除非用户明确要求，否则不要调用。
- 对 API 探索设置短超时和小范围请求，避免对管理网站造成压力。
