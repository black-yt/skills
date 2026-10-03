# MCP `invalid transport` 与被插件重新生成的配置

## 原始错误与版本边界

```text
failed to load configuration: invalid transport
in `mcp_servers.codex_app`
```

- 历史案例在创建新聊天或重新打开会话时失败，发生于 Windows App 配合 WSL CLI。
- 当时 `mcp_servers.codex_app` 来自内置插件 `codex-app-tools@openai-bundled` 的自动合成，不是用户直接创建的服务器。
- 该版本的配置解析仍要求顶层 MCP 项具有合法 transport：stdio 的 `command`，或 HTTP 的 `url`。只有 `enabled = false` 的残缺表也会在启动前解析失败。
- 当前官方仍区分 stdio `command` 与 Streamable HTTP `url`，但“禁用项是否仍验证 transport”必须在实际版本验证，不把历史解析行为扩大为永久接口契约。

## 为什么删掉又回来

- App 或插件同步可能重新生成 MCP 表，因此只删除 `config.toml` 中一段并不能消除生成源。
- 先检查配置层次：用户 home、受信任项目配置、插件合成和管理策略。不要反复手改 managed/generated 文件。
- 如果用户仍需要插件能力，优先修复或更新兼容配置，不能为了创建聊天把所有 MCP 一并关闭。

## 历史兼容方案

在用户确认不需要该插件、备份相关配置且当前版本确实复现同一错误时，原记录同时做了两项修改：

```toml
[plugins."codex-app-tools@openai-bundled"]
enabled = false

[mcp_servers.codex_app]
command = "cmd.exe"
args = []
enabled = false
```

- 第一项禁用生成来源；第二项使残留/再次合成的表具有可解析的 stdio 字段，同时保持禁用。
- `cmd.exe` 是历史案例里的**禁用占位**，不是一个可用 MCP server，不能将其改成 enabled=true，也不能当作 Linux MCP 的标准启动命令。
- 没有插件残留时不要无缘无故新增占位项。若当前版本支持清理生成源后移除残留，应选择更小的修复。
- 保留用户的 agent 模式。原案例同时保持了 `runCodexInWindowsSubsystemForLinux=true` 和 `integratedTerminalShell="wsl"`，不是靠切回原生 Windows解决。

## 相关但独立的 CLI 路径修正

原记录还发现 `CODEX_CLI_PATH` 指向已不存在的旧 `.codex/bin/wsl/[OLD_MANAGED_ID]/codex`，于是改到当前存在且已核验的 `[NEW_MANAGED_ID]`。

- 这是环境变量，不应因为原文代码块标为 TOML 就把它随意写成 `config.toml` 键。
- 路径核验、备份和回滚按 [04_managed_cli_and_installation.md](04_managed_cli_and_installation.md) 执行，不复制原机器的 managed ID。

## 验证与恢复

1. 修改前记录所选插件与 MCP 项原值；只读检查 `codex mcp --help`、`codex mcp list` 和日志，避免执行服务器内未知工具。
2. 确认 TOML 可解析以及当前 CLI 不再报告 invalid transport；这只能证明配置加载阶段通过。
3. 在不影响受保护活动任务的前提下重新启动目标客户端，实际创建聊天、打开旧会话并检查所需 MCP 能力。
4. 如果插件再次生成残缺项，检查真正的配置源和版本兼容，不循环删文件。
5. 回滚恢复本次变更的插件/MCP 键与 CLI path 原值；认证、对话数据库与真实项目不参与此修复。

官方入口：[MCP 配置](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)、[基础配置](https://learn.chatgpt.com/docs/config-file/config-basic)，2026-10-03 实际 GET 核对；滚动文档不等同于案例版本源码。
