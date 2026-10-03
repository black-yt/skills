# 故障资料覆盖清单与适用性审计

本表帮助使用者按原始错误、组件或历史尝试找到完整处理过程，也用于后续维护检查信息是否被意外删减。来源文件名只作为案例标识；skill 不依赖原备份目录，所有执行代码和必要流程均已内置或给出完整官方入口。

## 内容保留原则

- 保留症状、错误原文、原因证据、修复参数、无效尝试、验证、恢复和风险边界；重复案例可合并，但不同证据与附带修复分别列出。
- 原记录的确定结论若缺证据或已受版本影响，保留“原说法/原操作”并补充限制，不把猜测升级为事实。
- 私人姓名、账号、机器路径、IP、内部域、token、credential JSON 值与具体订阅期限采用占位符或字段 schema；这些不是可公开复用的技术内容。
- 原来源文件全部保留，不在整理过程中修复、执行或删除其 live 配置；公开仓库只含脱敏后的独立内容。

## 来源与主题逐项映射

| 标识 | 原始主题或操作 | 保留位置与处理 |
| --- | --- | --- |
| A01 | `codex_app.md`：Store 下载失败、VPN 对照、winsock reset、重启 | [04](04_managed_cli_and_installation.md)：完整历史恢复链，补充中断范围 |
| A02 | App 更新后找不到 CLI，Windows npm、WSL CLI、App managed entry 三者区别 | [04](04_managed_cli_and_installation.md)：位置表、调用者与错误链 |
| A03 | managed ID 失效、CODEX_CLI_PATH、setx/echo、新进程 | [04](04_managed_cli_and_installation.md)：核验、备份、override 和回滚 |
| A04 | `.cmd` 语法错误、node not found、错误包装二进制 | [04](04_managed_cli_and_installation.md)：文件类型与 App 自恢复边界 |
| B01 | `codex_app_bug_1.md`：终端正常、App Reconnecting、app-server 非交互环境 | [05](05_wsl_reconnect_auth_and_sandbox.md)：完整因果链 |
| B02 | Windows 代理经 WSLENV 传入，App CODEX_HOME 指向 Windows 映射目录 | [05](05_wsl_reconnect_auth_and_sandbox.md)：观察值结构与版本限制 |
| B03 | refresh_token_reused、401、重新认证、codex exec OK 探针 | [05](05_wsl_reconnect_auth_and_sandbox.md)、[08](08_auth_network_and_remote_proxy.md)：区分认证与网络 |
| B04 | bwrap 依赖、WSL1/2、0.115+、历史 bubblewrap/CLI/Node 版本 | [05](05_wsl_reconnect_auth_and_sandbox.md)：完整版本样本与验证命令 |
| B05 | ExecutionPolicy、启动 cmd、/usr/local/bin wrapper、managed CLI wrapper 的失败尝试 | [05](05_wsl_reconnect_auth_and_sandbox.md)：逐项撤回原因、删除范围 |
| B06 | 认证/配置临时备份、codex.real、桌面图标验收、models 端点探针 | [05](05_wsl_reconnect_auth_and_sandbox.md)：保留清理清单类型与验收 |
| C01 | `codex_app_bug_2.md` 与 `_3.md`：创建项目/Windows setup 失败、AbsolutePathBuf | [06](06_project_migration_and_windows_setup.md)：合并重复机制，保留两个表象 |
| C02 | 坏中文编码、Windows/WSL/Linux 路径混杂 | [06](06_project_migration_and_windows_setup.md)：TOML 示例，不泛化为中文不支持 |
| C03 | WSL 写入、UNC 枚举、ACL Deny 与 FullControl 排除 | [06](06_project_migration_and_windows_setup.md)：实测证据与有效权限限制 |
| C04 | desktop WSL/terminal 设置、windows unelevated sandbox fallback | [06](06_project_migration_and_windows_setup.md)：完整键与官方当前边界 |
| C05 | 清旧 projects trust 记录、config/global-state 备份 | [06](06_project_migration_and_windows_setup.md)：保留全清历史，改为可选择范围 |
| C06 | local-projects、selected-project、thread-project-assignments | [06](06_project_migration_and_windows_setup.md)：local/remote 字段级处理表 |
| C07 | sidebar-project-thread-orders、electron-workspace-root-labels | [06](06_project_migration_and_windows_setup.md)：失效映射与实体对话分离 |
| C08 | remote-projects、codex-managed-remote-connections、认证保留 | [06](06_project_migration_and_windows_setup.md)：明确保护边界 |
| C09 | 关闭 codex_app/node_repl/cua_repl、移除临时 wrapper | [06](06_project_migration_and_windows_setup.md)、[07](07_mcp_invalid_transport.md)：仅限不用组件，合法 transport |
| C10 | 日志位置/关键词、完全退出、UNC 两种形式、统一项目路径 | [06](06_project_migration_and_windows_setup.md)：重启条件、导入与完整验收 |
| D01 | `codex_app_bug_4.md`：7890→7897、localhost 误修、最终宿主机地址 | [02](02_proxy_and_launch.md)：三阶段表和五项跨环境探针 |
| D02 | 浏览器授权/回调/token exchange 是不同请求进程 | [01](01_oauth_diagnosis.md)：阶段图、错误与证据边界 |
| D03 | 系统代理、User/Machine/Process、shell 环境、大小写、NO_PROXY/ALL_PROXY | [02](02_proxy_and_launch.md)：完整配置分层和脱敏查询 |
| D04 | spawnCommand/executablePath、目标 PID 环境、.bashrc 非交互 return | [02](02_proxy_and_launch.md)：命令与读取限制 |
| D05 | NAT/mirrored、默认网关、Clash LAN/mixed-port、必要防火墙范围 | [02](02_proxy_and_launch.md)：发现、验证与动态地址边界 |
| D06 | 200 CONNECT + 405 GET、HTTP/1.1/2、403/TLS 不同判断 | [01](01_oauth_diagnosis.md)、[02](02_proxy_and_launch.md)：无凭据探针与四层验收 |
| D07 | 用户变量备份/URI 校验/恢复、普通双击启动、保留中转 API 会话 | [02](02_proxy_and_launch.md)：完整 PowerShell 片段与进程保护 |
| E01 | `codex_mcp_bug.md`：invalid transport、禁用表仍解析、自动生成来源 | [07](07_mcp_invalid_transport.md)：错误、plugin 与 MCP 的关系 |
| E02 | 禁用 bundled plugin + 合法但禁用 cmd.exe 占位 | [07](07_mcp_invalid_transport.md)：完整 TOML、只限历史兼容分支 |
| E03 | CLI path 的旧/新 managed ID | [04](04_managed_cli_and_installation.md)、[07](07_mcp_invalid_transport.md)：不把环境变量误写成 TOML |
| F01 | `codex_setting.md`：WSL/远端 token endpoint 403、localhost 原解释 | [08](08_auth_network_and_remote_proxy.md)：保留操作，纠正单因果结论 |
| F02 | Node/npm 安装、mirror、codex update、npm/sh/PowerShell 三渠道 | [04](04_managed_cli_and_installation.md)：来源、help 检查和 PATH 验收 |
| F03 | 安装 403 换 VPN、GitHub 匿名限流、登录 timeout 重试 | [04](04_managed_cli_and_installation.md)、[08](08_auth_network_and_remote_proxy.md)、[09](09_github_rate_limit_and_installer.md)：按响应来源分支 |
| F04 | Windows socket 10013、net stop/start winnat | [08](08_auth_network_and_remote_proxy.md)：检查保留端口、仅显式中断窗口 |
| F05 | 复制 auth.json、原“注释 model_provider”说法 | [08](08_auth_network_and_remote_proxy.md)：保留可信迁移方法，解释真实认证声明 |
| F06 | Windows、WSL、Linux SSH 三种代理地址 | [08](08_auth_network_and_remote_proxy.md)：完整命令与 NAT/TUN 条件 |
| F07 | ssh -R/RemoteForward、-CAXY、大小写 HTTP/SOCKS 环境变量 | [08](08_auth_network_and_remote_proxy.md)：保留转发机制，移除默认不必要能力 |
| G01 | `codex_with_github.md`：ratelimit=0、临时 curl wrapper、限定 API host | [09](09_github_rate_limit_and_installer.md)：原机制、完整调用、内置脚本 |
| G02 | GH token、Accept/API-Version、CODEX_NON_INTERACTIVE、hash -r | [09](09_github_rate_limit_and_installer.md)：WSL/PowerShell 两种流程 |
| H01 | `cc_switch.md`：高级配置目录、WSL UNC、Windows home、远端另配 | [10](10_provider_config_and_cc_switch.md)：配置归属表与同步边界 |
| I01 | `AI.md`：Claude 安装、beta 兼容变量、WebFetch preflight、IDE env | [11](11_claude_gemini_and_extension_env.md)：完整键、片段、版本和策略限制 |
| I02 | Windows sysdm.cpl、User/Process 差异、$PROFILE/cla 函数 | [11](11_claude_gemini_and_extension_env.md)：参数透传、恢复、避免覆盖 profile |
| I03 | Gemini npm/conda 全局范围、Google 登录、慢/效果评价 | [11](11_claude_gemini_and_extension_env.md)：保留体验为观察，不作通用结论 |
| I04 | Codex 安装升级、model/provider/effort/tier、sandbox/approval 配置 | [04](04_managed_cli_and_installation.md)、[10](10_provider_config_and_cc_switch.md)：模板与历史键完整保留 |
| I05 | WSL/Ubuntu/nvm/Node22/npm/Miniconda 环境链 | [10](10_provider_config_and_cc_switch.md)：可选初始化用途与渠道区分 |
| I06 | Git 身份/credential store、其他 SDK token | [10](10_provider_config_and_cc_switch.md)、[11](11_claude_gemini_and_extension_env.md)：独立配置、禁止发布值 |
| J01 | `config.toml`：多个 provider、env_key、inline bearer、local switch | [10](10_provider_config_and_cc_switch.md)：保留三种结构及 Responses 语义 |
| J02 | writable_roots、project trust、feature fast_mode、TUI/notice/marketplace/plugin | [10](10_provider_config_and_cc_switch.md)：键级说明与本机状态界限 |
| K01 | `.bashrc`/`.bashrc.wsl`：proxy_on/off/no/test/echo、远程加载代理 | [10](10_provider_config_and_cc_switch.md)：作用、恢复快照与远端执行风险 |
| K02 | proxy_r、openai_on、mycodex、ag/cr/sw、nvm/conda PATH | [08](08_auth_network_and_remote_proxy.md)、[10](10_provider_config_and_cc_switch.md)：通用函数与参数保留 |
| K03 | Claude 模型映射与插件数组、独立 token、.wgetrc 代理层 | [10](10_provider_config_and_cc_switch.md)、[11](11_claude_gemini_and_extension_env.md)：不混淆客户端 |
| K04 | shell 只引用但未提供 `switch_proxy.py`、远端 `setup_proxy.sh` | [10](10_provider_config_and_cc_switch.md)、下方依赖表：明确外部来源缺失，不能声称本 skill 内置这些服务 |
| K05 | 历史 `ftp_proxy`、提示用 `PROXY_STATUS`、注释中的 `WS_PROXY`/`WSS_PROXY` | [10](10_provider_config_and_cc_switch.md)：保留变量职责与未确认支持的边界 |
| L01 | `README.md` 的 cmp/diff/cp 与 `settings.json` node CPU 排除 | [10](10_provider_config_and_cc_switch.md)、[13](13_shared_storage_watchers.md)：保留配置比较及 exclude 差异 |
| M01 | `cc-migrate/README.md`：组件清单、作用范围、private token | [12](12_claude_proxy_chain_and_migration.md)：完整组件表与输入边界 |
| M02 | 多跳 CONNECT、direct/chain/直连模式、401/000 信号 | [12](12_claude_proxy_chain_and_migration.md)：网络图、模式表、响应局限 |
| M03 | `install.sh`：HOME 路径、保留 conf/.new、备份 credentials、跳过 settings | [12](12_claude_proxy_chain_and_migration.md)、install.py：保留职责，凭据显式选择 |
| M04 | seed 顶层/账号 schema、cur.update、损坏 JSON、文件权限 | [12](12_claude_proxy_chain_and_migration.md)、install.py：字段完整，损坏时停止而不静默丢数据 |
| M05 | `cc_env.sh`：首次快照、unset/空值、on/off/status、daemon 跨终端 | [12](12_claude_proxy_chain_and_migration.md)、cc_env.sh：增补 export 状态、ALL_PROXY 与 keep-daemon |
| M06 | `cc_proxy.sh`：配置加载、pidfile、no pkill、start/stop/status、TERM/KILL、游离端口 | [12](12_claude_proxy_chain_and_migration.md)、cc_proxy.sh/cc_proxy.py：手动入口加载配置，加强 starttime/身份验证 |
| M07 | `cc_proxy_chain.py`：CONNECT/header/rest、30 秒、64 KiB、线程与关闭 | [12](12_claude_proxy_chain_and_migration.md)、cc_proxy_chain.py：保留中继逻辑，加强边界并关闭请求日志 |
| M08 | `.conf`：target/upstream/listen/bypass；seed 与 settings 文件 | [12](12_claude_proxy_chain_and_migration.md)、配置模板：去除私有值、保留所有参数职责 |
| M09 | OAuth 有效期、两机刷新互踢、传输/清理包、重新登录 | [12](12_claude_proxy_chain_and_migration.md)：保留机制，不发布旧账号期限 |

## 文件级完整清单

本次对照的备份目录共 **33 个文件**：25 个文件的相关技术内容已归入下表；另有 6 份 Codex 认证快照、1 份 Claude credentials 和 1 份 rclone 私有配置，不公开其内容。这里的完整性按技术内容和运行依赖判断，不要求保持原来的文件名或重复段落。

| 来源文件 | 发布位置与处理 |
| --- | --- |
| `codex_app.md` | [04](04_managed_cli_and_installation.md)，Store、CLI 定位、路径覆盖与恢复 |
| `codex_app_bug_1.md` | [05](05_wsl_reconnect_auth_and_sandbox.md)，WSL 重连、认证、sandbox、撤回尝试 |
| `codex_app_bug_2.md` | [06](06_project_migration_and_windows_setup.md)，创建项目失败与迁移缓存 |
| `codex_app_bug_3.md` | [06](06_project_migration_and_windows_setup.md)、[07](07_mcp_invalid_transport.md)，Windows setup、MCP 与 wrapper 附带处理 |
| `codex_app_bug_4.md` | [01](01_oauth_diagnosis.md)、[02](02_proxy_and_launch.md)，OAuth/Clash 完整诊断与命令 |
| `codex_mcp_bug.md` | [07](07_mcp_invalid_transport.md)，合法 transport、生成来源、CLI path |
| `codex_setting.md` | [04](04_managed_cli_and_installation.md)、[08](08_auth_network_and_remote_proxy.md)，安装、403、10013、认证与三环境代理 |
| `codex_with_github.md` | [09](09_github_rate_limit_and_installer.md)、[github_api_curl.py](../scripts/github_api_curl.py)，WSL/PowerShell 与临时 wrapper |
| `cc_switch.md` | [10](10_provider_config_and_cc_switch.md)，Windows/WSL/远端配置归属 |
| `AI.md` | [04](04_managed_cli_and_installation.md)、[10](10_provider_config_and_cc_switch.md)、[11](11_claude_gemini_and_extension_env.md)，三种 agent、安装与环境 |
| `README.md` | [10](10_provider_config_and_cc_switch.md)、[13](13_shared_storage_watchers.md)，比较恢复与共享盘扫描 |
| `config.toml` | [10](10_provider_config_and_cc_switch.md)，provider、sandbox、trust、features、UI 和插件键 |
| `settings.json` | [13](13_shared_storage_watchers.md)，完整 JSON 模板及 watcher 区别 |
| `.bashrc` | [08](08_auth_network_and_remote_proxy.md)、[10](10_provider_config_and_cc_switch.md)、[11](11_claude_gemini_and_extension_env.md)，相关代理和 agent 函数；排除私人与非 agent 内容 |
| `.bashrc.wsl` | [02](02_proxy_and_launch.md)、[10](10_provider_config_and_cc_switch.md)、[11](11_claude_gemini_and_extension_env.md)，WSL 端口、provider 快捷函数和客户端环境 |
| `.ssh_config` | [08](08_auth_network_and_remote_proxy.md)，代理有关的 RemoteForward 与执行位置；不公开主机拓扑 |
| `.wgetrc` | [10](10_provider_config_and_cc_switch.md)，wget 独立代理配置层 |
| `cc-migrate/README.md` | [12](12_claude_proxy_chain_and_migration.md)，组件、安装、网络、凭据与影响范围 |
| `cc-migrate/install.sh` | [install.py](../scripts/claude_proxy/install.py)，功能迁移为 Python；文档明确新的调用方式 |
| `cc-migrate/proxy/cc_env.sh` | [cc_env.sh](../scripts/claude_proxy/cc_env.sh)，启用、关闭、状态与快照恢复 |
| `cc-migrate/proxy/cc_proxy.sh` | [cc_proxy.sh](../scripts/claude_proxy/cc_proxy.sh)、[cc_proxy.py](../scripts/claude_proxy/cc_proxy.py)，配置加载入口及进程管理 |
| `cc-migrate/proxy/cc_proxy_chain.py` | [cc_proxy_chain.py](../scripts/claude_proxy/cc_proxy_chain.py)，CONNECT 中继完整实现 |
| `cc-migrate/proxy/cc_proxy.conf` | [cc_proxy.conf.example](../scripts/claude_proxy/cc_proxy.conf.example)，全部参数职责、无私有服务地址 |
| `cc-migrate/claude/settings.json` | [12](12_claude_proxy_chain_and_migration.md) 中保留完整两字段 JSON；属于可选输入，不是默认安装所需文件 |
| `cc-migrate/claude/claude.json.seed` | [12](12_claude_proxy_chain_and_migration.md) 保留顶层与 oauthAccount schema；真实账号值仅作为私有迁移输入 |

## 运行依赖、未提供源码与包验证

| 对象 | 是否随 skill 提供 | 使用边界 |
| --- | --- | --- |
| Claude 代理运行文件 | 是 | 安装器所读的 `cc_env.sh`、`cc_proxy.sh`、`cc_proxy.py`、`cc_proxy_chain.py`、`cc_proxy.conf.example` 全部在同目录；需要 Linux/WSL、Bash、Python 3.9+ 标准库 |
| 代理状态探针 | 命令在代码内 | 需要本机 curl；真实目标连通性只在显式 `cc_status` 时探测 |
| GitHub API wrapper | 是 | 实际使用还需 curl 和已登录的 gh；安装器本身从当前官方入口取得并审查 |
| `switch_proxy.py` | 否，原备份未提供源码 | 原 `sw` 函数只跳转另一个本地项目；不把该函数当作已打包服务 |
| 集群 `setup_proxy.sh` | 否，原备份只有远程加载命令 | 私有集群配置需要从其可信维护方取得，不能复制旧地址或虚构实现 |
| 临时 Codex `.cmd`、managed CLI wrapper | 原备份仅记录其曾存在且已移除 | 最终修复不依赖这些撤回产物，不为凑齐文件重新创建 |
| 认证文件与身份值 | 否，有意排除 | 默认安装无需它们；只有私有迁移时显式传入，不能从公共包获得有效登录态 |
| 离线回归测试 | [test_helpers.py](../scripts/tests/test_helpers.py) | 临时 home、虚构凭据、回环模拟服务；不登录、不访问真实模型、不停止用户服务 |

从下载后的完整 skill 文件夹验证代码包，不要求原备份或作者目录存在：

```bash
python3 -B scripts/tests/test_helpers.py
```

测试覆盖安装依赖是否齐全、配置保留、可选迁移、环境精确恢复、手动入口配置加载、CONNECT 数据与半关闭、活动 relay 升级保护、无关 PID 保护和 GitHub token 不进 argv。Windows 原生 PowerShell 示例没有在此 Linux 离线测试中执行；真实账号登录和网络需要在实际环境按各篇验收。

## 明确不迁入的私人或无关内容

- 六份 Codex 认证快照及 Claude credentials 的实际 token、账号信息：仅记录认证存储/迁移机制，不读取发布其值。
- rclone 凭据、存储复制命令中的私有桶与一次性数据路径：属于存储同步，不属于本 skill 的 agent bug；保留在来源，不扩展成公开配置。
- SSH 配置中的个人 Host、用户、跳板拓扑：只抽取与反向代理相关的参数机制，不分发可连接的内部主机。
- shell 中终端美化、目录跳转、GPU/CPU 调度函数、CUDA/集群配额：与 agent 故障无关，未覆盖原配置或删掉这些功能。
- 私有 provider 名、API 节点、项目路径和原账号过期时间：替换为角色明确的占位符；保留端口变化、协议、配置层次和刷新行为等技术含义。

## 需持续关注的历史结论

| 原记录中的说法 | 本 skill 的规范化解释 |
| --- | --- |
| 403 一定是 WSL callback localhost 问题 | 按回调、token endpoint 与代理响应逐层验证 |
| auth.json 只在注释 model_provider 后有效 | 按 requires_openai_auth/env_key/实际 provider 判断 |
| WSL 使用 Clash 必须 TUN | 显式 HTTP proxy、NAT、mirrored、LAN 监听分别核实 |
| 所有旧 projects 可一律删 | 保留历史恢复范围，只清理已确认并授权的目标项 |
| sandbox unelevated 是普遍修复 | 只在 elevated setup/权限确有问题时作为版本支持的 fallback |
| 只要 enabled=false 就不会解析 transport | 某些版本仍校验，历史禁用占位只在证据吻合时使用 |
| HTTP 401/405 表示登录正常 | 仅说明相应 HTTP 通路响应，真实认证单独验证 |
| cc_off 只影响当前终端 | 环境恢复是局部，停共享 daemon 会影响其他使用者 |
| node CPU 高直接排除文件即可 | 分清 UI/search/watcher/Git/语言服务器，实测生效 |
| 固定 managed hash、端口、账号期限可直接复制 | 都是环境/版本状态，先发现再验证 |
