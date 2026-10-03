# 远端服务、Profile 与安装迁移

## 找到真正生效的配置

- 先看当前窗口的 Profile。默认用户设置和 `User/profiles/[PROFILE_ID]/settings.json` 可能不同；不要假定改默认文件就能影响当前窗口。
- Windows 稳定版通常使用 `%APPDATA%\Code\User`；Insiders、便携版和自定义 `--user-data-dir` 的位置不同。
- 使用 VS Code 的“打开用户设置(JSON)”定位当前 Profile，结合 Remote SSH Output 中的 `remote.SSH.*` 实际值验收。
- 工作区、远端设置和用户设置有不同作用范围；按设置注册的 scope 判断，不能把连接之前需要的本地参数写入远端配置。
- 修改前保存原文件；JSONC 不是严格 JSON，不要用会删除注释的整文件 JSON 重写方式。

## 有证据才启用的兼容选项

```json
{
  "remote.SSH.localServerDownload": "always",
  "remote.SSH.useExecServer": false
}
```

- `localServerDownload: always`：适用于远端访问下载源失败、而本地客户端可下载并传输的情况；本地网络也失败时不会自动解决问题。
- `useExecServer: false`：在已确认当前版本 Exec Server 启动链异常时，测试传统启动路径；不是磁盘满或 SSH 认证失败的修复。
- 两个设置应分别有诊断依据；只设置当前扩展支持的键，查看变更后的日志和最终启动目录。
- 服务 commit 应与客户端匹配；`code --version` 的 commit 比“系统里已有某个服务器目录”更可靠。

## 数据盘只作为有记录的临时方案

```json
{
  "remote.SSH.serverInstallPath": {
    "[HOST]": "[WRITABLE_DATA_DIRECTORY]"
  }
}
```

- `[HOST]` 必须与实际连接别名一致；确认数据盘可写、空间和 inode 足够、挂载允许执行。
- 某些旧版本会在配置的路径后再次追加 `.vscode-server`。日志中的 `vscodeAgentFolder`、启动命令、可执行文件路径才是实际结果。
- 不因为出现双层目录就立即移动正在运行的服务；先核对活动进程和依赖。
- 记录修改的 Profile、配置原值、实际安装目录和回迁条件。不要对整块数据盘执行递归清理。

## 迁回默认目录

默认服务目录通常是 **SSH 登录用户**的 `$HOME/.vscode-server`，不是固定 `/root`。自定义环境或当前版本若有其他覆盖，应先核实。

1. **容量与进程**：确认默认目录所在文件系统空间、inode、权限和执行挂载选项。检查旧目录的服务、extension host、PTY host 以及其终端子任务；迁移不得中断用户要求保留的任务。
2. **选择迁移内容**：可复用匹配当前客户端 commit 的完整 `bin/[COMMIT]`。目标有文件时先比较；不覆盖其他版本、原有扩展和用户数据。
3. **保留状态**：调查旧目录的 `extensions/`、`data/User/`、`data/Machine/`。历史文件先保留实体，再按 ID 合并索引；配置冲突保留双方备份并人工合并。不要盲拷运行锁、PID 和 token 文件。
4. **验证副本**：对计划复制的目录先 `rsync -a --dry-run`，完成后以 `rsync -anc --itemize-changes` 或文件清单/校验和验证。目标额外文件不会自动出现在普通 rsync 比较中，需另行清点；不使用 `--delete`。
5. **恢复默认**：仅删除 `serverInstallPath` 中该 Host 的覆盖；还有其他 Host 时保留其映射。保留仍有必要的下载和启动兼容选项。
6. **实际重连**：通过用户的 Windows VS Code、相同 Profile 和 Host 打开远端目录。日志应显示默认目录，管理连接与扩展宿主连接建立；进一步确认文件浏览和终端可用。
7. **再删旧安装**：确认旧路径无进程可执行文件、cwd、打开文件、内存映射和相关子任务占用，且独有历史/扩展/配置已保留后，才清理已授权的旧安装目录。

出现任一失败，保留旧目录和配置备份。可以恢复该 Host 的原安装覆盖回到旧服务；在新连接未验证前，不删除回退所需内容。

## 完成证据

- 本地日志：实际 `serverInstallPath` 和启动路径正确；没有后续循环重连。
- 远端日志：`ManagementConnection`、`ExtensionHostConnection` 建立，扩展宿主能够启动。
- 运行状态：服务的 `/proc/[PID]/exe` 指向预期目录；文件浏览和终端测试成功。
- 数据保护：原有受保护任务的 PID 与启动时间未变；历史文件清单无丢失。
- 报告区分“SSH 成功”“服务启动成功”“完整编辑器可用”，不把一个层面的成功泛化成全部正常。
