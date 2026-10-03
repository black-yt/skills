---
name: ssh-remote-troubleshooting
description: "排查 SSH 与 VS Code Remote SSH 连接故障，尤其是终端能登录但编辑器失败、Windows 临时目录拒绝访问、配置档未生效、远端服务安装失败或系统盘被缓存和隐藏文件占满；支持保留运行任务的安装迁移与验证。"
---

# SSH 与 VS Code Remote SSH 排障

把故障定位到本地启动、SSH 认证、远端安装或编辑器连接中的具体阶段，修复后从用户实际使用的客户端重新连接。

## 核心规则

- **先分层**：普通 SSH 成功只证明该次 SSH 路径可用；Remote SSH 还依赖本地脚本、非交互 shell、转发、下载、解压和远端写入。
- **看首个错误**：`Failed to parse remote port` 常是后续症状。先检查它之前的拒绝访问、下载失败、磁盘满或启动错误。
- **同一客户端**：比较终端和编辑器实际使用的 SSH 可执行文件、配置文件、Host 别名、用户、密钥和跳板；不要因 PATH 探测出现几个 `ENOENT` 就重装 SSH。
- **最小修改**：先备份目标配置，再只改生效配置档中的相关键；JSONC 的注释和其他字段必须保留。不把旧版兼容开关写成所有版本的默认值。
- **保护任务**：迁移或删除服务目录前检查 PID、父子关系、工作目录、打开文件和内存映射；不能用 `pkill node`、全局杀进程或重启整台机器代替定位。
- **保护数据**：模型、环境、浏览器二进制、编译缓存与会话数据库不等于可随意删除的下载缓存。已有授权只覆盖明确的任务和路径。
- **停止条件**：无法证明文件归属、共享副本完整或进程不受影响时，保留该项并继续其他修复；不要循环重装、清空所有服务器目录或放宽全局权限。
- **日志安全**：只输出所需错误和阶段信息；SSH 配置、完整环境、启动命令和 VS Code 日志可能含内部地址、token 或密码，分享前必须脱敏。

## 排查顺序

1. 记录客户端、Remote SSH 扩展和远端 OS 版本，确认实际主机别名与当前 VS Code Profile。
2. 从首个失败阶段选择下表 reference；已经正常的层不反复修改。
3. 若根因是存储，先区分文件系统、inode、缓存、打开但已删除的文件和被挂载遮住的文件。
4. 在已授权范围内做最小修复；临时改到数据盘时，记录实际安装路径与回迁条件。
5. 验证客户端的管理连接、扩展宿主连接和远端目录访问；若仍有断连，不能只凭监听端口宣告成功。
6. 比较受保护进程启动时间和文件清单，清理本次临时产物，报告最终目录、验证证据与尚未验证的项目。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 定位终端与 Remote SSH 的客户端差异，复现 Windows `cmd type` 临时脚本权限和非交互 SSH。给出用户 TEMP/TMP 修复、环境继承及回滚方法。 | ssh.exe, ENOENT, Permission denied, 拒绝访问, TEMP, TMP, cmd, OpenSSH, ssh -T, ProxyJump | 终端可登录但编辑器失败时读取；本地脚本位于系统 Temp 时读取；修改 SSH 路径或用户临时目录前读取 | [references/01_client_and_temp.md](references/01_client_and_temp.md) |
| 2 | 区分 VS Code Profile、服务器下载和执行模式，说明 `serverInstallPath` 的版本差异。覆盖临时数据盘安装、迁回默认目录、历史保留及删除旧安装的验收条件。 | Remote SSH, Profile, settings.json, JSONC, useExecServer, localServerDownload, serverInstallPath, vscode-server, 迁移 | 配置看似无效时读取；远端下载或启动失败时读取；修改安装位置、迁回默认目录或清理旧安装前读取 | [references/02_server_and_migration.md](references/02_server_and_migration.md) |
| 3 | 按文件系统和 inode 解释“其他盘有空间但系统盘满”，区分下载缓存与运行资产。提供保守的 pip/npm/uv 清理入口及活动进程、会话文件的保护验收。 | df, du, inode, cache, pip, npm, uv, lsof, Codex, sessions, SQLite | 出现 No space left on device 时读取；清理缓存或检查 Codex 占用前读取；空间统计不一致时读取 | [references/03_disk_and_cache.md](references/03_disk_and_cache.md) |
| 4 | 用独立挂载命名空间查看系统盘被遮住的目录，比较共享盘模型并规划无损迁移。包含写入保护的作用范围、失败处理与取消方法，不提供自动删除脚本。 | findmnt, virtiofs, xfs, unshare, bind mount, SHA-256, 模型, chattr, immutable, mountpoint | 发现挂载遮住的文件时读取；清理底层模型副本前读取；防止挂载失效后落盘或取消保护前读取 | [references/04_mount_shadow.md](references/04_mount_shadow.md) |

## 辅助脚本

- [scripts/compare_trees.py](scripts/compare_trees.py)：只读比较两棵目录的普通文件、空目录和 SHA-256；拒绝符号链接、特殊文件及跨设备子目录，检测扫描期间的变化。返回 0 表示一致，1 表示差异，2 表示无法完成核验。**脚本不会删除文件，也不授予删除权限。**
- 相等只表示本次读取时的目录结构与文件内容相同，不比较权限、ACL 或扩展属性，也不证明进程无占用、目录确属共享盘或之后没有变化。
- 使用方式：`python3 scripts/compare_trees.py '[SOURCE_DIR]' '[DESTINATION_DIR]'`。在待检文件所在机器运行，目录较大时预留读取两份数据的时间。

## 版本与官方入口

- 已验证故障样本：VS Code **1.95.0**、Remote SSH **0.115.1**、Windows OpenSSH **8.6p1**；这是适用性样本，不要求降级或固定版本。
- 上游漂移锚点（2026-10-03 GitHub API/源码读取）：`microsoft/vscode` HEAD `253b7648aa69de1a651a327370098f3814b8922f`，该提交的 `package.json` version 为 `1.141.0`；`microsoft/vscode-remote-release` HEAD `53c123ff18bb11fc9d01b86063347d84ecf8295c`。这些当前 HEAD 不代表上面旧版案例的源码；扩展实际版本仍以客户端安装结果为准。
- 先执行 `code --version`、`code --list-extensions --show-versions`、`ssh -V`，再核对已安装扩展的配置说明和日志。扩展与服务路径行为可能变化。
- 更新此 skill 时重新核对上游版本与 HEAD；变化后复查官方说明、当前 CLI help、设置注册和必要的只读源码，不能只刷新版本号。
- 官方排障入口：[VS Code Remote Development troubleshooting](https://code.visualstudio.com/docs/remote/troubleshooting)。此滚动文档不与上述历史版本一一绑定，2026-10-03 实际 GET 核对；版本有差异时以当前扩展设置和生成命令为准。
