---
name: codex-app-troubleshooting
description: "排查 Codex App 登录、WSL 后端、CLI 定位、项目迁移、MCP 和代理故障，保护 provider、活动对话与历史；也覆盖用户明确涉及的 CC Switch、Claude Code 代理迁移、Gemini CLI 环境及相关 IDE 扫描问题。"
---

# Codex App 故障修复

定位真正失败的桌面进程、认证请求或 agent 后端，在用户已有配置和授权范围内修复，并验证正常桌面启动方式。其他 agent 经验按产品分篇，只在当前问题涉及对应客户端时读取；不把一个产品的参数套到另一个产品。

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
2. 按日志选择 reference：OAuth/端口/继承看 1–2；执行器与历史保护看 3；CLI、WSL 重连、项目迁移和 MCP 分别看 4–7；远端认证/转发看 8；安装限流看 9；provider/CC Switch 看 10；Claude/Gemini 看 11–12；扫描高占用看 13。
3. 修复后检查新启动的实际后端环境，而不只检查当前 shell。
4. 用新的登录流程和正常桌面快捷方式验证；临时启动脚本成功不等于双击启动已经修复。
5. 核对受保护进程与历史，报告根因、最小变更、回滚入口和未验证项。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 区分浏览器授权、本地回调与后端 token exchange，解释网页登录正常但桌面失败的原因。覆盖代理、DNS、TLS 和 HTTP 响应的证据边界，不更换用户认证模式。 | OAuth, auth.openai.com, oauth/token, Token exchange failed, callback, DNS, TLS, provider, API key | 登录报 token exchange 失败时读取；浏览器成功但 App 失败时读取；准备重置登录或修改 provider 前读取 | [references/01_oauth_diagnosis.md](references/01_oauth_diagnosis.md) |
| 2 | 处理 Clash 重装端口变化、Windows 系统代理与 WSL 网络地址差异。提供进程/用户变量备份、持久化、环境广播和正常桌面启动验收方法。 | Clash Verge, 系统代理, TUN, HTTP_PROXY, HTTPS_PROXY, ALL_PROXY, WSL, NAT, mirrored, 环境继承 | VPN 或代理重装后失败时读取；Win32 浏览器和 WSL 行为不同时读取；修改代理变量或启动脚本前读取 | [references/02_proxy_and_launch.md](references/02_proxy_and_launch.md) |
| 3 | 验证 Windows/WSL 执行器和文件视图是否一致，分辨等待审批、终端卡住与后端问题。定义活动对话、认证文件和 SQLite 状态的保护、备份及复核边界。 | CreateProcess, /bin/bash, CODEX_HOME, app-server, sessions, archived_sessions, SQLite, WAL, PID, history | 工具找不到 shell 或写文件不可见时读取；准备重启、清缓存或重置 App 前读取；用户要求保留远端对话时读取 | [references/03_backend_and_history.md](references/03_backend_and_history.md) |
| 4 | 区分 Windows npm、WSL 用户 CLI 与 App 管理入口，处理更新后无法定位二进制及 CODEX_CLI_PATH 失效。保留 Store 网络恢复、安装渠道、升级与 PATH 核验。 | CLI binary, CODEX_CLI_PATH, managed CLI, wrapper, npm, standalone, Store, winsock, PATH | App 更新后找不到 CLI 时读取；准备修改路径 override 或 wrapper 前读取；安装升级或 Store 下载失败时读取 | [references/04_managed_cli_and_installation.md](references/04_managed_cli_and_installation.md) |
| 5 | 记录 WSL app-server 重连的代理继承证据、refresh_token_reused 和 bubblewrap 依赖。完整保留 ExecutionPolicy、启动脚本、临时 wrapper 等撤回尝试及清理边界。 | Reconnecting, app-server, WSLENV, CODEX_HOME, refresh_token_reused, bubblewrap, bwrap, ExecutionPolicy | WSL CLI 正常而 App 重连时读取；401 或刷新令牌复用时读取；检查 sandbox 依赖或撤回临时 wrapper 前读取 | [references/05_wsl_reconnect_auth_and_sandbox.md](references/05_wsl_reconnect_auth_and_sandbox.md) |
| 6 | 处理 AbsolutePathBuf 项目迁移失败和 Windows 设置未完成，给出旧 trust/local 索引的字段级清理。包含 ACL 排除、备份、UNC 导入、sandbox fallback 与远程状态保护。 | AbsolutePathBuf, project migration, Windows setup, trust_level, global-state, local-projects, UNC, ACL, sandbox | 创建项目失败时读取；出现迁移反序列化错误时读取；修改 trust 记录、本地项目缓存或 Windows sandbox 前读取 | [references/06_project_migration_and_windows_setup.md](references/06_project_migration_and_windows_setup.md) |
| 7 | 解释 bundled plugin 重建残缺 MCP 表及禁用项仍报 invalid transport 的历史行为。保留合法禁用占位方案、CLI 路径附带修正、版本限制和验收回滚。 | MCP, invalid transport, command, url, enabled, codex_app, bundled plugin, cmd.exe | 创建聊天配置加载失败时读取；删除 MCP 后又自动出现时读取；禁用插件或添加 transport 占位前读取 | [references/07_mcp_invalid_transport.md](references/07_mcp_invalid_transport.md) |
| 8 | 区分 token endpoint 403、回调和 socket 10013，规范可信认证迁移与 provider 判断。给出 Windows/WSL/SSH 反向代理和 HTTP/SOCKS 环境的完整执行位置。 | 403, OAuth, callback, 10013, WinNAT, auth.json, requires_openai_auth, ssh -R, RemoteForward, SOCKS | 远端官方登录失败时读取；迁移认证或处理 Windows socket 错误前读取；建立本地代理的远程转发前读取 | [references/08_auth_network_and_remote_proxy.md](references/08_auth_network_and_remote_proxy.md) |
| 9 | 处理 GitHub 匿名 API 限额耗尽导致的安装失败，保留 WSL 临时 curl wrapper 与 PowerShell 认证查询。明确 token 主机限制、argv 脱敏、安装器兼容与清理。 | GitHub, rate limit, x-ratelimit-remaining, gh, curl wrapper, GITHUB_TOKEN, PATH, installer | 安装器 API 403 时读取；加入临时认证 wrapper 前读取；运行带 GitHub token 的安装脚本前读取 | [references/09_github_rate_limit_and_installer.md](references/09_github_rate_limit_and_installer.md) |
| 10 | 建立 Windows、WSL、App 和 SSH 配置归属，说明 CC Switch 的目录选择及 provider 模板。覆盖 Responses、env_key、sandbox、项目 trust、shell 函数和 wget 配置层。 | CC Switch, config.toml, model_provider, env_key, Responses, service_tier, approval_policy, writable_roots, .wgetrc | 切换 provider 未生效时读取；复制配置或修改 CC Switch 目录前读取；排查 npm/conda/nvm 与 shell 代理差异时读取 | [references/10_provider_config_and_cc_switch.md](references/10_provider_config_and_cc_switch.md) |
| 11 | 收录 Claude Code 网关变量、beta 兼容、WebFetch、Windows profile 和 VS Code 扩展环境。区分 Gemini CLI 的 npm 作用域、Google 登录和历史性能观察。 | Claude Code, Gemini CLI, ANTHROPIC_BASE_URL, AUTH_TOKEN, beta, WebFetch, PowerShell, VS Code, npm | 问题涉及 Claude/Gemini 时读取；终端与 IDE 插件行为不同时读取；修改 beta、WebFetch 或模型映射配置前读取 | [references/11_claude_gemini_and_extension_env.md](references/11_claude_gemini_and_extension_env.md) |
| 12 | 完整拆解 Claude 迁移包的 direct/chain 代理、环境快照、共享 daemon、CONNECT 中继及凭据身份合并。提供可选安装脚本、参数模板、权限、刷新竞争与恢复策略。 | cc_on, cc_off, CONNECT, direct, chain, pidfile, starttime, credentials, oauthAccount, migration | 迁移 Claude 代理环境前读取；启动停止跨终端 relay 前读取；导入凭据或身份 seed 前读取 | [references/12_claude_proxy_chain_and_migration.md](references/12_claude_proxy_chain_and_migration.md) |
| 13 | 排查 node 扫描共享存储导致的 CPU 高占用，保留原 files/search exclude 配置并说明 watcher 和 Git 警告的差别。按实际进程、glob 命中及功能回归验收。 | node, CPU, shared storage, files.exclude, search.exclude, watcherExclude, Git, language server | 共享盘扫描拖慢开发机时读取；修改 VS Code 排除配置前读取；准备停止 node 或重载扩展宿主前读取 | [references/13_shared_storage_watchers.md](references/13_shared_storage_watchers.md) |
| 14 | 按来源文件、故障证据、命令与代码组件列出完整覆盖映射，记录合并案例和历史结论修正。明确凭据与无关私人配置的排除范围，便于检索和后续完整性检查。 | coverage, case index, source mapping, 原始记录, 信息守恒, 版本限制, 脱敏, 历史修正 | 按原故障文件查找处理方式时读取；合并或拆分本 skill 内容前读取；核对代码改写和经验遗漏时读取 | [references/14_case_coverage.md](references/14_case_coverage.md) |

## 辅助脚本

- [scripts/inspect_proxy_env.py](scripts/inspect_proxy_env.py)：只显示允许列表中的代理变量，代理 URL 仅输出 scheme/host/port，移除用户信息、路径、查询和片段；不输出 API key、完整环境或 `NO_PROXY` 具体内容。
- `python3 scripts/inspect_proxy_env.py` 检查当前 Python 进程继承的环境；Linux/WSL 使用 `--pid [PID]` 检查已核实的后端进程。权限不足就报告限制，不自动提权或转储其他进程。
- 该脚本不修改变量、不发网络请求、不读取对话或认证文件；输出仍可能包含内部代理主机，公开分享前继续匿名化。
- [scripts/github_api_curl.py](scripts/github_api_curl.py)：仅供 reference 9 的临时安装器 wrapper，限定 GitHub API 请求并避免 token 出现在 argv；不是全局 curl 替代品。
- [scripts/claude_proxy/install.py](scripts/claude_proxy/install.py) 与同目录资源：按 reference 12 安装 Linux/WSL 代理助手，默认不导入凭据、不改 shell rc；只有显式命令才会安装、联网或停止共享 relay。
- [scripts/claude_proxy/cc_proxy.sh](scripts/claude_proxy/cc_proxy.sh)：供已安装助手手动管理 relay，启动前加载配置；原始文件与运行依赖的完整对应表见 reference 14。
- [scripts/tests/test_helpers.py](scripts/tests/test_helpers.py)：在临时目录和回环模拟服务上验证下载后的完整代码包，不依赖作者的认证或本地项目。

## 官方依据与版本边界

- 先从 App 关于页面记录版本，并读取**实际后端二进制**的 `--version`；`codex --version` 只代表 PATH 上的 CLI，不能替代 App 版本。
- 开源 CLI 漂移锚点（2026-10-03 GitHub API 读取）：`openai/codex` 最新 release tag `rust-v0.160.0`，仓库 HEAD `b741e480e203f037ca726bc2a76d99a8e8668e66`。release 与 HEAD 分开记录，均不表示用户 App 内置版本；桌面 App 未取得可核实的源码版本时不得编造对应 commit。
- 更新此 skill 时重新核对版本与 HEAD；变化后复查官方文档、当前 CLI help 和相关只读源码，再调整参数与故障分支。
- 2026-10-03 实际 GET 核对：[认证](https://learn.chatgpt.com/docs/auth)、[Windows App](https://learn.chatgpt.com/docs/windows/windows-app)、[故障排查](https://learn.chatgpt.com/docs/reference/troubleshooting)。这些是滚动文档，不是与某个旧 App 版本绑定的固定实现说明。
- 旧入口 `https://developers.openai.com/codex/auth/`、`https://developers.openai.com/codex/app/windows/` 与 `https://developers.openai.com/codex/app/troubleshooting/` 在核对时跳转到上述完整 URL；页面当前使用 ChatGPT desktop app 名称，排查用户所称 Codex App 时仍需确认安装版本与产品界面。
- 官方文档确认原生 Windows 与可选 WSL agent、浏览器登录流程和敏感认证缓存；下文 Clash 端口、代理继承和临时修复是操作经验，不声称所有版本都使用相同网络实现。
- 新增历史案例包括 CLI 0.150.1、Node 22.22.2、bubblewrap 0.9.0-1ubuntu0.1；只作样本，不作为升级/降级要求。Claude/Gemini 是独立客户端，复现前分别读取其版本与官方帮助，不能用 Codex 版本替代。
