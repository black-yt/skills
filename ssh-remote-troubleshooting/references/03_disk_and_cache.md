# 系统盘、缓存与活动任务保护

## 按文件系统解释空间

在远端 Linux 执行，替换实际数据盘和共享模型路径：

```bash
df -hT / "$HOME" '[DATA_MOUNT]' '[SHARED_MODEL_DIR]'
df -i / "$HOME"
findmnt -T "$HOME/.vscode-server"
findmnt -T '[SHARED_MODEL_DIR]'
du -xhd1 "$HOME" 2>/dev/null
```

- 系统盘、数据盘、共享盘的剩余空间不能相互抵消。Remote SSH 写入 home 时，另一块盘空闲也无法解决失败。
- `df` 查文件系统总占用；`du` 查当前可见路径。两者不一致还可能来自权限、文件系统元数据、快照、稀疏文件、打开但已删除的文件或挂载遮蔽。
- `df -i` 用于确认 inode 是否耗尽；不要只看字节空间。
- `lsof +L1` 或 `/proc/[PID]/fd` 可调查打开但已删除的文件；只输出必要元数据。不为释放空间强杀正在工作的进程。
- 挂载遮住的文件按 [04_mount_shadow.md](04_mount_shadow.md) 单独调查；不要用正常共享路径的 `du` 结果替代底层检查。

## 缓存分类

| 内容 | 建议 | 原因 |
| --- | --- | --- |
| pip、npm 的包下载缓存 | 确认用户允许未来重新下载后，用包管理器清理 | 不卸载已安装包，但离线重装会受影响 |
| npm `_npx` | 先保留，检查使用者 | 可能是正在使用的执行环境 |
| uv cache | 优先使用当前版本支持的保守 prune | 已安装环境、运行工具和构建资产可能依赖缓存 |
| Hugging Face、ModelScope 模型缓存 | 按模型资产管理 | 可能是唯一权重副本，删除会导致模型失效 |
| vLLM、Torch 编译缓存 | 默认保留，明确重编译影响后另行处理 | 重建可能很慢、需要空间或干扰运行任务 |
| Playwright 浏览器、conda/venv | 默认保留 | 是运行组件，不是普通下载垃圾 |
| `.codex` 会话、索引、SQLite、认证与配置 | 不作为缓存清理 | 可能承载活动对话与唯一历史 |

确认授权范围后，可从以下命令选择实际需要的一项；不要把它们当作无条件清理套餐：

```bash
python3 -m pip cache info
python3 -m pip cache purge
npm cache clean --force
uv cache prune --help
```

- 先核对 cache 目录、当前用户和工具版本。npm 命令中的 `--force` 是该命令的要求，不代表可对 uv 或文件删除使用强制选项。
- 若当前 uv 帮助支持，可以选择 `uv cache prune --offline --no-config --no-python-downloads`；不要追加绕过占用检查的 `--force`，也不要默认使用面向 CI 的激进清理选项。
- 包管理器对 `_npx` 等目录的处理会随版本变化；清理前后列出实际目录，不能仅凭命令名称承诺保留范围。
- 如果用户要求完全不影响离线使用或重新安装，包下载缓存也要保留。

## Codex 与活动进程保护

- 识别本地、WSL、SSH 远端各自的实际 Codex home，考虑 `CODEX_HOME` 和版本差异，不把多个目录合并或改指向。
- 只统计目录大小和文件元数据，不读取对话正文、`auth.json` 内容或完整进程环境。
- 清理前保存本机私有基线：受保护 PID、Linux `/proc/[PID]/stat` 的启动时间，`sessions/`、`archived_sessions/` 的文件清单，实际存在的 history/index、`state_*.sqlite`、`thread_history_*.sqlite`、配置与认证文件身份。
- SQLite 主文件、`-wal`、`-shm` 是相关状态；不能将 WAL 当缓存删除。在线数据库需要备份时使用 SQLite 在线备份机制或应用支持的快照，不能把普通文件复制当成一致性保证。
- 基线只供本次维护验收；不把真实文件名、路径、token 或会话信息写入公开仓库。
- 清理后确认原有进程启动时间未变且非 zombie，所有原文件仍存在、核心文件未被替换。活跃会话增长是正常现象，不能要求文件内容完全静止。
- 报告保护检查的实际范围；未验证的服务不能笼统声称未受影响。
