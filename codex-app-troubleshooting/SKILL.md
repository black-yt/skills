---
name: codex-app-troubleshooting
description: "排查 Codex 桌面端登录、代理和 Windows/WSL 后端故障，包括浏览器能登录但 OAuth token exchange 失败、Clash 端口变化、环境变量未继承及执行器路径错配；修复时保护现有 provider、活动对话和历史记录。"
---

# Codex App 故障修复

定位真正失败的桌面进程、认证请求或 agent 后端，在用户已有配置和授权范围内修复，并验证正常桌面启动方式。

## 核心规则

- **先确定执行位置**：Windows 原生 agent、WSL agent、独立 CLI 和 SSH 远端 app-server 可能同时存在。桌面窗口或内置终端的类型不能证明认证请求来自哪里。
- **保留认证模式**：浏览器 ChatGPT OAuth 与自定义 API provider 的链路不同。修复 OAuth 不代表可以删除中转服务配置、改 `base_url`、清除 API key 或切换登录方式。
- **保留会话**：不把 `.codex`、数据库、WAL、history 或 sessions 当作重置按钮。用户要求保留活动对话时，不重启其后端、执行 `wsl --shutdown` 或批量杀 Codex/node 进程。
- **先读官方说明**：查询实际版本对应的认证和 Windows 环境文档；CLI 与 App 内置版本可能不同，页面名称或路径也可能迁移。
- **日志最小化**：不输出完整环境、`auth.json`、URL 中的凭据、OAuth code、cookie 或完整进程启动参数。只提取错误类别、请求主机、端口与必要 PID 信息。
- **最小修复**：先用目标进程范围的代理设置验证，再按用户的日常启动需求持久化；用户指定的有效端口要保留，不为了套用教程改成另一个端口。
- **失败边界**：连接失败、证书失败、HTTP 拒绝与授权码失效分开处理。不要关闭 TLS 校验、循环重放授权码或不断清空凭据。
- **权限与重启**：沿用当前会话已有授权，不重复索要已给的权限；若只有中断受保护活动任务才能继续，则先完成独立检查并说明剩余限制，不能自行终止任务。

## 问题路由

1. 记录 App 版本、实际后端版本、Windows/WSL 模式、代理软件与当前端口，以及故障前发生的变化。
2. 按日志分支定位：token exchange 网络错误看 reference 1；代理端口或继承问题看 reference 2；执行器错配、卡住或历史风险看 reference 3。
3. 修复后检查新启动的实际后端环境，而不只检查当前 shell。
4. 用新的登录流程和正常桌面快捷方式验证；临时启动脚本成功不等于双击启动已经修复。
5. 核对受保护进程与历史，报告根因、最小变更、回滚入口和未验证项。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 区分浏览器授权、本地回调与后端 token exchange，解释网页登录正常但桌面失败的原因。覆盖代理、DNS、TLS 和 HTTP 响应的证据边界，不更换用户认证模式。 | OAuth, auth.openai.com, oauth/token, Token exchange failed, callback, DNS, TLS, provider, API key | 登录报 token exchange 失败时读取；浏览器成功但 App 失败时读取；准备重置登录或修改 provider 前读取 | [references/01_oauth_diagnosis.md](references/01_oauth_diagnosis.md) |
| 2 | 处理 Clash 重装端口变化、Windows 系统代理与 WSL 网络地址差异。提供进程/用户变量备份、持久化、环境广播和正常桌面启动验收方法。 | Clash Verge, 系统代理, TUN, HTTP_PROXY, HTTPS_PROXY, ALL_PROXY, WSL, NAT, mirrored, 环境继承 | VPN 或代理重装后失败时读取；Win32 浏览器和 WSL 行为不同时读取；修改代理变量或启动脚本前读取 | [references/02_proxy_and_launch.md](references/02_proxy_and_launch.md) |
| 3 | 验证 Windows/WSL 执行器和文件视图是否一致，分辨等待审批、终端卡住与后端问题。定义活动对话、认证文件和 SQLite 状态的保护、备份及复核边界。 | CreateProcess, /bin/bash, CODEX_HOME, app-server, sessions, archived_sessions, SQLite, WAL, PID, history | 工具找不到 shell 或写文件不可见时读取；准备重启、清缓存或重置 App 前读取；用户要求保留远端对话时读取 | [references/03_backend_and_history.md](references/03_backend_and_history.md) |

## 辅助脚本

- [scripts/inspect_proxy_env.py](scripts/inspect_proxy_env.py)：只显示允许列表中的代理变量，代理 URL 仅输出 scheme/host/port，移除用户信息、路径、查询和片段；不输出 API key、完整环境或 `NO_PROXY` 具体内容。
- `python3 scripts/inspect_proxy_env.py` 检查当前 Python 进程继承的环境；Linux/WSL 使用 `--pid [PID]` 检查已核实的后端进程。权限不足就报告限制，不自动提权或转储其他进程。
- 该脚本不修改变量、不发网络请求、不读取对话或认证文件；输出仍可能包含内部代理主机，公开分享前继续匿名化。

## 官方依据与版本边界

- 先从 App 关于页面记录版本，并读取**实际后端二进制**的 `--version`；`codex --version` 只代表 PATH 上的 CLI，不能替代 App 版本。
- 开源 CLI 漂移锚点（2026-10-03 GitHub API 读取）：`openai/codex` 最新 release tag `rust-v0.160.0`，仓库 HEAD `b741e480e203f037ca726bc2a76d99a8e8668e66`。release 与 HEAD 分开记录，均不表示用户 App 内置版本；桌面 App 未取得可核实的源码版本时不得编造对应 commit。
- 更新此 skill 时重新核对版本与 HEAD；变化后复查官方文档、当前 CLI help 和相关只读源码，再调整参数与故障分支。
- 2026-10-03 实际 GET 核对：[认证](https://learn.chatgpt.com/docs/auth)、[Windows App](https://learn.chatgpt.com/docs/windows/windows-app)、[故障排查](https://learn.chatgpt.com/docs/reference/troubleshooting)。这些是滚动文档，不是与某个旧 App 版本绑定的固定实现说明。
- 旧入口 `https://developers.openai.com/codex/auth/`、`https://developers.openai.com/codex/app/windows/` 与 `https://developers.openai.com/codex/app/troubleshooting/` 在核对时跳转到上述完整 URL；页面当前使用 ChatGPT desktop app 名称，排查用户所称 Codex App 时仍需确认安装版本与产品界面。
- 官方文档确认原生 Windows 与可选 WSL agent、浏览器登录流程和敏感认证缓存；下文 Clash 端口、代理继承和临时修复是操作经验，不声称所有版本都使用相同网络实现。
