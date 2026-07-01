---
name: codex-history-sync
description: "当需要把一个 CODEX_HOME/.codex 中的 Codex 会话记录、history.jsonl、sessions 和 thread title 元数据单向同步到另一个用户或目录下的 .codex 时使用；强调 dry-run、敏感配置排除、filter、force 边界和同步后验证。"
---

# Codex History Sync

## 适用场景

- 把一个 `CODEX_HOME` 下的 `.codex` 历史记录同步给另一个用户、另一台机器、另一个 Windows/WSL 目录或备份目录。
- 只迁移会话记录、`history.jsonl`、`sessions/` 和 thread title/name 元数据，不迁移登录态和长期配置。
- 需要按项目关键词筛选历史记录时，用 `--filter` 做路径/文本内容正则过滤。
- 需要只同步会话标题、名称或 SQLite/JSON/JSONL 中的 title metadata 时，用 `--rename-only`。

## 核心边界

- 这是单向同步：`--source` 是可信来源，`--dest` 是接收方。
- 默认不会删除目标目录中的文件。
- 默认不会覆盖目标中已有但内容不同的文件；只有加 `--force` 才会覆盖。
- 默认排除 `auth.json`、`config.toml`、`credentials.json`、`settings.json`、`.env`，以及 `bin/`、`cache/`、`logs/`、`node_modules/`、`tmp/`。
- 不要默认使用 `--include-sensitive`。只有用户明确要求迁移配置/凭据类文件，并理解风险时才考虑。
- 同步前先运行 `--dry-run --verbose`，确认复制、覆盖、跳过和 title 更新范围。

## 脚本

使用 bundled script：

```bash
python3 codex-history-sync/scripts/sync_codex_history.py --help
```

脚本能力：

- 复制源 `.codex` 中选定目录和根文件，默认同步 `sessions/` 和 `history.jsonl`。
- 保留相对路径和文件时间戳。
- 对已有不同文件默认跳过，避免覆盖目标用户已有历史。
- 支持 `--force` 覆盖目标不同文件。
- 支持 `--filter '[REGEX]'`，只同步相对路径或文本内容匹配的记录。
- 支持 `--all-folders` 或 `--folders sessions [OTHER_FOLDER]` 控制顶层目录。
- 支持 `--root-files history.jsonl [OTHER_FILE]` 控制根文件。
- 支持从 JSON、JSONL 和 SQLite 文件中收集源 thread title/name，并更新目标中的同 ID title/name。

## 推荐流程

1. 确认源和目标目录。

```bash
SOURCE_CODEX_HOME="[SOURCE_CODEX_HOME]"
DEST_CODEX_HOME="[DEST_CODEX_HOME]"
```

`SOURCE_CODEX_HOME` 和 `DEST_CODEX_HOME` 应该是包含 `.codex` 的目录，或者直接用 `.codex` 目录作为参数。保持两个参数表达一致即可。

2. 先 dry-run。

```bash
python3 codex-history-sync/scripts/sync_codex_history.py \
  --source "[SOURCE_CODEX_HOME]/.codex" \
  --dest "[DEST_CODEX_HOME]/.codex" \
  --dry-run \
  --verbose
```

3. 如果只想同步某个项目相关记录，加 `--filter`。

```bash
python3 codex-history-sync/scripts/sync_codex_history.py \
  --source "[SOURCE_CODEX_HOME]/.codex" \
  --dest "[DEST_CODEX_HOME]/.codex" \
  --filter "[PROJECT_OR_PATH_REGEX]" \
  --dry-run \
  --verbose
```

4. dry-run 输出符合预期后，去掉 `--dry-run` 执行。

```bash
python3 codex-history-sync/scripts/sync_codex_history.py \
  --source "[SOURCE_CODEX_HOME]/.codex" \
  --dest "[DEST_CODEX_HOME]/.codex" \
  --filter "[PROJECT_OR_PATH_REGEX]"
```

5. 如果目标已有不同文件且确定要用源覆盖，再显式加 `--force`。

```bash
python3 codex-history-sync/scripts/sync_codex_history.py \
  --source "[SOURCE_CODEX_HOME]/.codex" \
  --dest "[DEST_CODEX_HOME]/.codex" \
  --filter "[PROJECT_OR_PATH_REGEX]" \
  --force
```

## 常用模式

### 默认同步历史

```bash
python3 codex-history-sync/scripts/sync_codex_history.py \
  --source "[SOURCE_CODEX_HOME]/.codex" \
  --dest "[DEST_CODEX_HOME]/.codex"
```

默认同步：

- `sessions/`
- `history.jsonl`
- JSON/JSONL/SQLite 中可匹配的 thread title/name 元数据

### 只同步标题

```bash
python3 codex-history-sync/scripts/sync_codex_history.py \
  --source "[SOURCE_CODEX_HOME]/.codex" \
  --dest "[DEST_CODEX_HOME]/.codex" \
  --rename-only \
  --dry-run \
  --verbose
```

确认后：

```bash
python3 codex-history-sync/scripts/sync_codex_history.py \
  --source "[SOURCE_CODEX_HOME]/.codex" \
  --dest "[DEST_CODEX_HOME]/.codex" \
  --rename-only
```

### 同步更多目录但仍排除敏感文件

```bash
python3 codex-history-sync/scripts/sync_codex_history.py \
  --source "[SOURCE_CODEX_HOME]/.codex" \
  --dest "[DEST_CODEX_HOME]/.codex" \
  --all-folders \
  --dry-run \
  --verbose
```

不要把 `--all-folders` 理解为“同步所有秘密”。脚本仍会默认排除敏感文件名和缓存/日志/tmp 类目录。

## 输出解读

脚本结束后会打印 `Summary`：

- `copied`：新增复制到目标的文件数。
- `overwritten`：使用 `--force` 覆盖的文件数。
- `unchanged`：源和目标完全一致的文件数。
- `skipped_existing`：目标已有不同文件且未加 `--force`，因此跳过。
- `skipped_filtered`：被 `--filter` 排除的文件数。
- `skipped_sensitive`：被敏感文件/目录规则排除的文件数。
- `titles_found`：从源 JSON/JSONL/SQLite 中找到的 title/name 数量。
- `json_files_renamed`、`jsonl_files_renamed`、`sqlite_rows_renamed`：目标中被更新 title/name 的位置。

## 验证

- 先看 dry-run 输出，确认没有复制 `auth.json`、`config.toml`、`credentials.json`、`settings.json`、`.env`。
- 检查 `Summary` 中 `skipped_sensitive` 是否合理。
- 没有加 `--force` 时，如果 `skipped_existing` 大于 0，说明目标已有不同历史；不要盲目覆盖，先确认是否真的要以源为准。
- 同步后打开目标 Codex，检查相关历史是否出现、标题是否正常。
- 如果只按项目同步，抽查目标 `sessions/` 或 `history.jsonl` 中是否只包含匹配项目的记录。

## 失败处理

- `source does not exist`：确认传入的是实际 `.codex` 目录，或先展开 `~`。
- `source and dest are the same directory`：源和目标不能相同，避免自同步。
- dry-run 中目标不存在：脚本会提示；真实运行时会创建目标目录。
- `skipped_existing` 很多：目标已有不同记录，默认保护目标；需要用户明确同意后才加 `--force`。
- title 没有更新：检查源和目标中是否存在同一 thread/session/conversation id；不同 ID 无法自动匹配。

## 安全提醒

- 不要把 `.codex` 整目录粗暴复制给别人；其中可能包含登录、配置、缓存或本地路径信息。
- 不要在公开文档里写真实用户名、真实本机路径、真实项目路径或凭据。
- 如果目标是另一个真实用户的 `.codex`，同步前让对方关闭正在运行的 Codex，避免同时写同一批历史文件。
- 如需共享给第三方，优先使用 `--filter` 限定项目，并先 dry-run 检查敏感文件是否被排除。

## 外部备选工具

本 skill 自带脚本适合保守的单向同步；如果需求变成 provider 切换、Desktop 可见性修复、会话导入导出或跨 provider 克隆，可以先了解下面两个外部项目，再决定是否使用。

### Dailin521/codex-provider-sync

- GitHub：https://github.com/Dailin521/codex-provider-sync
- 定位：同步 Codex session provider metadata，主要解决切换 `model_provider` 后旧会话在 Codex Desktop 或 `/resume` 中不可见的问题。
- 覆盖范围：`~/.codex/sessions`、`~/.codex/archived_sessions`、`~/.codex/state_5.sqlite`、`.codex-global-state.json` 中的项目根路径缓存。
- 常见能力：`status` 检查 provider/rollout/SQLite/项目可见性；`sync` 把历史会话 metadata 同步到当前 provider；`switch <provider-id>` 修改 `config.toml` 后同步；`restore <backup-dir>` 从工具备份恢复。
- 边界：它只修复历史会话可见性相关 metadata，不修改消息正文、会话标题、登录态、认证或 `auth.json`。
- 注意：含 `encrypted_content` 的旧会话跨 provider/account 后，通常只能恢复列表可见性，继续对话或 compact 仍可能失败。

### goodnightzsj/codex-session-cloner

- GitHub：https://github.com/goodnightzsj/codex-session-cloner
- 定位：`AI CLI Kit (aik)` 中的 Codex Session Toolkit，面向本地 Codex 会话浏览、迁移、导入导出、跨 provider 克隆和 Desktop 可见性修复。
- 常见能力：`aik codex list` 查看本机会话；`aik codex export <session_id>` 导出 bundle；`aik codex import <session_id>` 导入 bundle；`aik codex clone-provider` 在切换 provider 后克隆会话；`aik codex watch-provider` 持续监听 provider 变化并自动克隆；`aik codex repair-desktop` 修复 Desktop 可见性/索引。
- 运行方式：可在项目目录直接运行 `./aik`，也可按 upstream README 使用安装脚本或 `python -m ai_cli_kit`。
- 边界：这是外部工具箱，不是本 skill bundled script；实际使用前必须阅读 upstream README 和 `--help`，确认当前版本命令、备份策略和清理范围。
- 注意：涉及清理、覆盖、修复 SQLite 或归档会话时，先 dry-run 或选择预览命令；真实删除或覆盖必须征得用户确认。

选择建议：

- 只想把一个 `.codex` 的会话记录保守同步到另一个目录：优先用本 skill 自带脚本。
- 切换 provider 后历史会话不可见：优先了解 `codex-provider-sync`。
- 需要会话 bundle 导入导出、跨 provider 克隆、watch provider 或 Desktop 修复：优先了解 `codex-session-cloner` / `aik codex`。
- 使用任何外部工具前，都要先备份 `.codex`，关闭正在运行的 Codex Desktop，并确认不会同步或泄露 `auth.json`、凭据、token、私有路径和不该共享的会话内容。
