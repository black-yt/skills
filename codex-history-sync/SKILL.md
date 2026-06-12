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
