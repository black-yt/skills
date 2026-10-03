# 创建项目失败与“Windows 设置未完成”

## 两份历史记录中的共同证据

```text
Local app-server project migration failed
Invalid request: AbsolutePathBuf deserialized without a base path
```

- 案例表现同时包括“创建项目失败”和“Windows 设置未完成”；换成纯英文新目录仍然失败。
- App 运行于 Windows，agent 与集成终端使用 WSL。该模式本身受支持，不需要为了错误强制切回 Windows Native。
- 旧 `config.toml` 中 `[projects...]` 的 trust 记录和 Desktop 的本地项目缓存混入 Windows 路径、WSL `/mnt/...` 路径、Linux home 路径以及坏编码的中文路径。
- 当时的 Windows 侧项目迁移在路径反序列化时失败，使本地项目索引初始化不完整。**不能推广为所有 Linux 路径或中文路径天然不支持**；必须结合具体迁移错误。

示例结构：

```toml
[projects.'D:\[PROJECT_ROOT]\[GARBLED_NAME]']
trust_level = "trusted"

[projects."/mnt/d/[PROJECT_ROOT]/[GARBLED_NAME]"]
trust_level = "trusted"

[projects."/home/[USER]/[PROJECT]"]
trust_level = "trusted"
```

## 与权限或 WSL 可访问性区分

| 分支 | 应有证据 | 检查 |
| --- | --- | --- |
| WSL 目录权限 | `permission denied`、`EACCES`、`EPERM`，在 WSL 中实际写入也失败 | 只在目标目录创建唯一临时文件，验证后移除；不覆盖名为 test 的现有文件 |
| Windows 无法访问发行版 | 从 Windows 枚举 WSL UNC 路径失败 | `Get-ChildItem '\\wsl$\[DISTRO]\home\[USER]'`，再检查发行版状态 |
| 本地项目迁移失败 | 上面的 migration/AbsolutePathBuf 错误，目录实际可写、UNC 可枚举 | 检查旧项目记录、路径编码和缓存 schema |

历史案例中 WSL home 和临时测试目录均可写，Windows 能枚举 UNC 路径，因此没有通过递归改权限解决。

`.codex` ACL 的 Deny 项可能来自 sandbox 隔离，但不能仅凭存在 FullControl 就断言有效权限没有问题：显式 Deny 和用户组成员关系仍需核对。本案例用实际访问测试排除了 ACL 根因；不删除 sandbox ACL 或给 Everyone 全权限。

## 先备份并避免运行时竞争

- 在需要关闭 App 才能稳定修改状态时，先核对活动任务；要求不中断的任务仍在运行时暂不执行该修改，完成可独立的调查。
- 备份实际 App Codex home 中的 `config.toml` 与 `.codex-global-state.json`，使用唯一时间戳或 GUID，不覆盖已有 `.bak`。
- 备份可能含服务地址或配置凭据，只保存本机私有位置，不发布。

```powershell
$codexDir = '[ACTUAL_APP_CODEX_HOME]'
$stamp = [guid]::NewGuid().ToString()
foreach ($name in 'config.toml', '.codex-global-state.json') {
    $source = Join-Path $codexDir $name
    if (Test-Path -LiteralPath $source -PathType Leaf) {
        Copy-Item -LiteralPath $source -Destination ($source + '.bak-' + $stamp)
    }
}
```

## 精确清理配置与本地索引

1. **解析而非全量重置**：先确认 TOML/JSON 能解析并识别当前 schema。只清理已证实损坏或本次明确选定的旧本地项目项。
2. **保留项目实体**：`[projects.'...']` 中的 `trust_level` 是配置记录，不是工程目录。移除记录不应删除、移动或修改项目文件；重新导入时可能需要重新信任。
3. **完整保留历史经验**：原案例曾清掉全部旧 `[projects...]` trust 记录后恢复；这是一次性恢复范围，不是默认清理所有用户项目的授权。
4. **字段按版本辨识**：下表列出当时涉及的字段。字段不存在、类型不同或无法判定 local/remote 时停止编辑，不照抄清空整个字段。

| 字段 | 原案例处理范围 | 必须保留 |
| --- | --- | --- |
| `local-projects` | 已选定的损坏本地项目索引 | 未涉及的有效本地项目 |
| `selected-project` | 仅指向待清理 local 项的当前选择 | remote 选择与其他有效选择 |
| `thread-project-assignments` | `projectKind` 为 `local` 且关联目标项目的映射 | remote 映射、对话实体和无关关系 |
| `sidebar-project-thread-orders` | 对应目标的 `local-*` 排序项 | remote 排序及无关 sidebar 状态 |
| `electron-workspace-root-labels` | 已确认失效的本地 root 标签 | 无关 workspace label |
| `remote-projects` | 不处理 | 全部远程项目 |
| `codex-managed-remote-connections` | 不处理 | 全部远程连接 |
| auth、sessions、数据库 | 不处理 | 认证和完整对话历史 |

- 编辑前后对照键级 diff，保留未选中的对象，不把删 sidebar 映射写成删对话。
- 若改坏或结果无效，在无并发写入的安全窗口恢复本次备份，再针对日志继续定位。

## 两个设置与附带修复的适用边界

原案例保留：

```toml
[desktop]
runCodexInWindowsSubsystemForLinux = true
integratedTerminalShell = "wsl"

[windows]
sandbox = "unelevated"
```

- `[desktop]` 的具体键是历史 App 版本使用的设置；先核实当前版本支持与实际生效位置。
- `unelevated` 在当时绕过 elevated sandbox setup 失败。当前官方把 elevated 作为有管理员权限时的推荐，unelevated 是权限或 setup 不可用时的 fallback；它不是 AbsolutePathBuf 的普遍修复，也不能为了省事默认降级隔离方式。
- 原记录关闭了用户不使用的 `codex_app`、`node_repl`、`cua_repl` MCP。只有确定不需要的项目才禁用，且不能留下当前版本无法解析的“只有 enabled=false”的 transport；参见 [07_mcp_invalid_transport.md](07_mcp_invalid_transport.md)。
- 曾创建的 `.codex/bin/wsl/codex-wrapper/codex` 被移除以避免污染 `CODEX_CLI_PATH`。只删除本次临时文件，处理路径 override 按 reference 4。

## 重启、重新导入与验收

- 日志历史位置为 `%LOCALAPPDATA%\Codex\Logs`；可按日期继续定位，先验证该版本实际日志目录。
- 搜索关键词：`Local app-server project migration failed`、`AbsolutePathBuf`、`project`、`workspace`、`failed`、`permission`、`denied`、`EACCES`、`EPERM`、`ENOENT`、`wsl`。
- 在可安全重启目标 App 时正常完全退出；只关窗口可能留下 Electron 状态。原记录用过任务管理器结束进程，现在必须先确认具体进程归属和活动任务，禁止批量终止 Codex/ChatGPT。
- Windows 文件选择器使用 `\\wsl$\[DISTRO]\home\[USER]\[PROJECT]` 或 `\\wsl.localhost\[DISTRO]\home\[USER]\[PROJECT]`；不能期待 Windows 文件选择器把裸 `/home/...` 当作 WSL 路径。
- 同一项目避免反复混用 `D:\...`、`/mnt/d/...`、`\\wsl$\[DISTRO]\mnt\d\...` 创建多份历史项。若项目确实在 Windows 盘，按目标 agent 能力选择一种稳定表示，不强制搬迁到 Linux home。
- 验收应包括 App 初始化、创建/打开项目、信任提示和文件访问，且原远程项目、连接和对话仍在；不能只看错误提示消失。
