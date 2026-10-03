# WSL agent 重连、过期登录态与 sandbox 依赖

## 历史现象与完整因果链

- WSL 终端 `codex` 正常，桌面 App 的 WSL agent 却停在 `Reconnecting... waiting for network`。
- App 启动的是 `codex app-server`，不是用户的交互式 shell，也不是手工测试的 `codex exec`。
- 案例里的 app-server 最初没有 `HTTP_PROXY`、`HTTPS_PROXY`，而直连 OpenAI/ChatGPT 超时；通过 Windows 主机代理才可达。
- Windows 用户代理变量修正后，App 的启动链通过 `WSLENV` 把变量传给 WSL；这是该版本观察到的行为，必须在当前版本真实进程中确认，不能一律假定自动传递。

修复后进程环境的结构是：

```text
CODEX_HOME=/mnt/c/Users/[WINDOWS_USER]/.codex
HTTP_PROXY=http://[WINDOWS_HOST]:[PROXY_PORT]
HTTPS_PROXY=http://[WINDOWS_HOST]:[PROXY_PORT]
NO_PROXY=localhost,127.0.0.1,::1
```

这同时说明：App agent 可能使用 Windows 映射的 Codex home，而 WSL 手动 CLI 默认仍使用 Linux home。两者的登录态和 provider 不能混为一谈。

- 原案例代理端口是 7890；后来的 Clash 重装案例是 7897。保留用户当前有效端口，按 [02_proxy_and_launch.md](02_proxy_and_launch.md) 验证。
- 原案例的 loopback-only `NO_PROXY` 不是所有机器的推荐覆盖值；已有内网域、网段和 API 中转 bypass 必须保留。
- 单独设置 `WSLENV` 时须先核对当前值和 flags；不能清空已有条目。已证实 App 能传递变量时不新增多余全局配置。

## 独立分支：`refresh_token_reused` 与 HTTP 401

原记录中 WSL 自身 `~/.codex/auth.json` 也曾失效，出现：

```text
refresh_token_reused
Please log out and sign in again
HTTP 401
```

- 这是认证状态分支，不能把它全部解释成代理失败；代理通路恢复后仍要检查真实登录状态。
- 先定位报错进程实际的 Codex home，再修复该客户端的认证。退出或覆盖共享凭据可能影响别的会话，应先核对使用者。
- 优先重新走该客户端支持的登录流程。确需迁移认证时，遵循 [08_auth_network_and_remote_proxy.md](08_auth_network_and_remote_proxy.md) 的同账号、私有传输、目标备份和刷新竞争边界。
- 原记录以 `codex exec --skip-git-repo-check "只回复 OK"` 验证 WSL CLI。此命令会发出模型请求、产生会话和潜在费用，只有在用户授权的真实运行验证范围内执行；它不能替代 App 的连接验证。

## bubblewrap 与 WSL 版本

- 原案例保留了 `/usr/bin/bwrap`，包版本为 `bubblewrap 0.9.0-1ubuntu0.1`；WSL 用户 CLI 为 `codex-cli 0.150.1`，位于 nvm Node `v22.22.2` 下。这些是历史复现值，不是必须安装的固定版本。
- 当前官方 Windows 说明指出 Codex 0.115 起 Linux sandbox 使用 bubblewrap，WSL1 不再适用；先检查 `wsl -l -v`、目标发行版和实际后端版本。

```bash
command -v bwrap
bwrap --version
command -v codex
codex --version
```

- 缺少依赖时用该发行版支持的包管理方式在已授权范围内安装；不能用关闭 sandbox 代替修好依赖。
- 安装 bwrap 与修复代理、修复登录态是三个不同动作；不能声称其中任意一个可以解决所有重连问题。

## 做过但最终撤回的尝试

| 尝试 | 当时作用或问题 | 最终处理与复用边界 |
| --- | --- | --- |
| `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` | 测试 PowerShell 执行链 | WSL agent 不依赖该改变，原案例恢复为 `CurrentUser Undefined`；回滚必须恢复用户自己的备份，不能强制所有人都改 Undefined |
| `Start-Codex-WSL-Proxy.cmd` | 验证“带代理启动 App”是否有效 | 正常桌面图标启动通过后移除本次临时脚本，不让日常使用依赖它 |
| `/usr/local/bin/codex` wrapper | 测试非交互 shell 的路径和环境 | 原案例只删除本次创建的 wrapper，保留真实 Linux CLI；不能按同名路径删除用户原本的程序 |
| 包装 `.codex/bin/wsl/[MANAGED_ID]/codex` | 想给 App managed CLI 注入环境 | App 自动恢复官方二进制，方法不可维护；还原原件，核对无临时 `codex.real` 残留 |

原记录还清理了本次 `auth.json.bak-[TIMESTAMP]`、`codex-wrapper.tmp`、`config.toml.bak-before-wsl-agent-fix` 等实验产物。可复用规则是**只清理本次确认无用且不承担回退用途的文件**，不按通配符删除用户认证备份或历史。

## 验收与复发检查

1. 保留有效 Windows 用户代理变量、目标 CLI 的有效认证、所需 sandbox 依赖以及可用 Linux CLI。
2. 通过正常桌面图标启动，检查新 app-server 的代理；保留原有活动 CLI 与远端任务。
3. 在实际请求环境用无凭据探针访问目标端点。原记录测试过 `https://chatgpt.com/backend-api/codex/models`；其状态码只用于分层诊断，不等于模型权限或登录成功。
4. 原记录用 `reg query HKCU\Environment`、`ps -eo pid,args`、`tr '\0' '\n' < /proc/[PID]/environ` 排查；现在只查询具体变量，使用脱敏代理脚本，不打印整份注册表、环境或命令参数。
5. 代理软件端口或 WSL 主机地址变化后，重新验证当前监听、用户环境和新后端继承，不能反复安装 CLI 碰运气。
