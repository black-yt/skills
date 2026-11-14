# 从旧版 WSL 智能体环境切换到远程 WSL 连接

已验证案例：Windows 桌面版 `26.1111.2228.0`、Ubuntu WSL 2、通过 nvm 安装的 Codex CLI `0.169.0`。桌面设置提示旧版 WSL 智能体环境已弃用，且尚未发现远程 WSL 连接。迁移前分别验证 CLI 安装、桌面启动时的路径和 app-server 初始化。

## Linux x64 可选依赖缺失

在目标发行版的交互式 Bash 中运行 `command -v node npm codex`、`npm prefix -g` 和 `codex --version`，确认 npm 指向 WSL 内的 Node 安装。遇到 `Missing optional dependency @openai/codex-linux-x64` 时，检查当前 Codex 包的版本和 npm 安装日志。平台包属于可选依赖，下载失败时 npm 仍可能返回成功。

```bash
# 使用现有 CLI 主包的实际版本
version=0.169.0
npm install --global "@openai/codex@$version" --include=optional
codex --version
```

如果官方源的二进制下载反复中断，可从可信镜像下载同版本平台压缩包，再与 npm 官方源的完整性值核对。对于上述版本，Linux x64 平台包对应 `@openai/codex@0.169.0-linux-x64`，确切版本和平台映射以主包的 `optionalDependencies` 为准。

```bash
expected="$(npm view "@openai/codex@${version}-linux-x64" dist.integrity \
  --registry=https://registry.npmjs.org)"
actual="sha512-$(openssl dgst -sha512 -binary "$tarball" | openssl base64 -A)"
if [ "$expected" = "$actual" ]; then
  npm cache add "$tarball" --offline &&
    npm install --global "@openai/codex@$version" --include=optional --offline &&
    codex --version
fi
```

先将 `tarball` 设为已下载文件的路径。仅在校验一致时使用该文件。若中断的安装留下 `ENOTEMPTY`，确认相关 npm 进程已退出，再把报错指向的 Codex 临时目录移到备份位置后重试。

## 桌面能找到 CLI 并启动 app-server

从 Windows PowerShell 检查目标发行版及桌面版使用的非交互式启动路径。将 `Ubuntu` 换成 `wsl.exe -l -v` 中的实际发行版名。

```powershell
wsl.exe -l -v
wsl.exe -d Ubuntu -- bash -lc 'export PATH="${CODEX_INSTALL_DIR:-$HOME/.local/bin}:$PATH"; command -v codex && codex --version'
```

- 交互式 Bash 能找到 nvm 的 Codex 而上面的检查失败时，把发行版内的独立 CLI 安装到桌面端搜索的目录，或在该目录增加用户级启动脚本。先检查是否已有同名入口。对 nvm 安装，脚本应把实际 Node 版本的 `bin` 放到 `PATH` 前面，再用 `exec "$nvm_bin/codex" "$@"` 调用 npm 入口。用 `command -v node` 确定 `nvm_bin`，给脚本执行权限。nvm 切换版本后重新核对路径。
- 如果版本检查通过，但 app-server 打开 Windows 挂载盘上的 `state_5.sqlite` 时出现 `migration 1 was previously applied but has been modified`，检查 Windows 经 `WSLENV` 传入的 `CODEX_HOME`。本案例在上述启动脚本内，仅对桌面端的 app-server 调用且 `CODEX_HOME` 指向 Windows 挂载目录时执行 `unset CODEX_HOME`。Linux 服务随后使用默认的 `~/.codex`。保留现有数据库和会话文件，避免原地修改迁移记录。
- 验收时从 Windows 使用相同的 Bash 启动路径运行 `codex app-server`，通过 stdio 发送 JSON-RPC `initialize` 请求并确认收到对应的成功响应。在本案例中桌面启动命令为 `codex -c features.code_mode_host=true app-server --analytics-default-enabled`。具体参数取决于已安装的桌面版。
- 完全退出并重新打开桌面端，在「设置 → 连接 → WSL」确认目标发行版出现并连接成功，再从该连接打开项目。该案例由用户确认重启后的连接可用。

官方文档提供 WSL 2 和 CLI 安装说明。桌面启动路径和迁移报错的处理来自上述版本的实测。[OpenAI WSL 指南](https://learn.chatgpt.com/docs/windows/wsl)
