# App 更新后找不到 CLI、安装失败与版本定位

## `Unable to locate the Codex CLI binary`

历史案例在 App 更新后、Agent Environment 已选择 WSL 时出现该错误。不能因为 WSL 终端里的 `codex` 能用，就认为桌面 App 的 CLI 路径正确。

| 组件 | 历史安装位置示例 | 调用者 |
| --- | --- | --- |
| Windows npm CLI | `%APPDATA%\npm\codex`、`codex.cmd` | Windows 终端 |
| WSL 用户安装的 Linux CLI | `$HOME/.nvm/versions/node/[NODE_VERSION]/bin/codex` 或 `$HOME/.local/bin/codex` | WSL 交互式终端 |
| App 管理的 WSL 启动入口 | `%USERPROFILE%\.codex\bin\wsl\[MANAGED_ID]\codex` | 桌面 App 的 WSL 启动链 |

- 原记录把第三项称为“WSL Wrapper”；另一次检查发现它实际是官方 ELF 二进制。**名称不证明文件类型**，需要查看真实文件、启动日志和当前版本实现。
- 更新可能使旧 managed ID 失效，或让 `CODEX_CLI_PATH` 继续指向已经不存在的目录。
- 将 App 的 Linux 入口误指向 Windows npm shim，可能产生 `.cmd` 语法错误；指向依赖未加载 nvm 的用户 CLI，则可能出现 `node not found`。
- 不改写 App 管理的二进制来注入代理。App 会自行恢复或替换它，手工包装可能留下 `codex.real`、失效 wrapper 或与版本不匹配的入口。

## 核验与精确修复

在 Windows PowerShell 查看 override 和实际入口，不输出其他环境：

```powershell
[Environment]::GetEnvironmentVariable('CODEX_CLI_PATH', 'User')
Get-ChildItem -LiteralPath "$env:USERPROFILE\.codex\bin\wsl" -Filter codex -Recurse |
    Select-Object FullName, Length, LastWriteTime
```

1. 根据 App 日志中的 `spawnCommand=wsl.exe`、`executablePath` 和当前 agent 模式确定应使用哪个入口；不要只按“最后修改时间最大”选一个。
2. 验证 Windows 路径存在，在对应 WSL 环境检查文件类型及该入口的 `--version`；记录 App 版本与终端 CLI 版本。
3. 备份原 `CODEX_CLI_PATH` 的用户值。优先让当前 App 自己恢复正确入口；若对应版本确实需要 override，再将其设为刚核实的 App 管理入口。

```powershell
$cliPath = '[VERIFIED_WINDOWS_PATH_TO_APP_MANAGED_WSL_CODEX]'
if (-not (Test-Path -LiteralPath $cliPath -PathType Leaf)) { throw 'CLI entry does not exist' }
[Environment]::SetEnvironmentVariable('CODEX_CLI_PATH', $cliPath, 'User')
```

原案例也使用过 CMD：`setx CODEX_CLI_PATH "[VERIFIED_PATH]"`。`setx` 影响后续进程；同一个旧 CMD 中 `echo %CODEX_CLI_PATH%` 不能证明新值已继承。检查注册表用户值、重新启动的目标 App 环境及实际启动日志。

- 只有目标 App 无受保护活动任务时才正常退出并重开；不杀独立 CLI、远端 app-server 或整个 WSL。
- 若失败，恢复本次备份的 override；原值不存在时移除用户覆盖。不能把旧 managed ID 写成所有机器的固定路径。
- 原始问题线索：[openai/codex issue 16408](https://github.com/openai/codex/issues/16408)。issue 是历史排障线索，不保证当前所有版本仍有同一缺陷。

## CLI 安装渠道、PATH 与升级

先看位置和版本，再按**原安装渠道**处理；不能从 App 故障推导必须升级系统里所有 CLI。

```bash
command -v codex
type -a codex
ls -l "$(command -v codex)"
codex --version
codex --help
npm root -g
```

Windows PowerShell 对照：

```powershell
(Get-Command codex).Source
Get-Command codex -All | Select-Object Source
codex --version
```

| 安装渠道 | 常见位置 | 原记录中的更新方法 |
| --- | --- | --- |
| npm | `.../lib/node_modules/@openai/codex/bin/codex.js` 或 Windows npm shim | `npm install -g @openai/codex`，指定最新 tag 时用 `@latest` |
| Linux standalone | `$HOME/.codex/packages/standalone/current/bin/codex` | 下载并审查官方 `https://chatgpt.com/codex/install.sh` 后执行 |
| Windows standalone | `%LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe` | 下载并审查官方 `https://chatgpt.com/codex/install.ps1` 后执行 |

- `codex update` 是原记录中的统一更新入口，必须先从**已安装版本**的 `--help` 确认存在；不支持时回到原渠道，不能反复运行不存在的子命令。
- 原记录使用 `curl -fsSL ... | sh`、`powershell -ExecutionPolicy Bypass -c "irm ... | iex"`；保留其安装来源，但推荐先下载、检查脚本再运行。Bypass 若确有必要只限该进程，不能顺手修改永久 ExecutionPolicy。
- npm 安装路径可能属于 conda 或 nvm 环境；切换环境后找不到命令，不等于包被删除。检查 `node`、`npm`、`codex` 是否属于同一运行环境。
- npm 403、安装脚本 403 和 GitHub 匿名 API 限额是不同分支。原记录尝试过换 VPN 节点；先检查响应来源和限额 headers，网络切换只是用户允许时的诊断，不是通用修复。
- 国内 npm mirror 是原记录中的可选下载路径，不要自动执行全局 `npm config set registry`。若需要，保留当前 registry，确认可信镜像和该次命令的作用范围。
- 安装成功后执行 `hash -r`、`command -v codex`、`codex --version`，并核对 App 实际入口；终端 CLI 更新不等于 App 内置版本更新。

## Microsoft Store 下载失败的历史分支

原记录顺序是：Microsoft Store 无法下载 → 关闭 VPN 测试 → 管理员 PowerShell 执行 `netsh winsock reset` → 重启设备 → 下载恢复。

- 这是历史上有效的网络修复链，不是 Codex 登录失败的默认操作。
- `netsh winsock reset` 与整机重启会影响网络和正在运行的会话。只有已经定位到 Windows 网络栈问题、用户授权该中断范围且已保存工作时才执行。
- 优先检查 Store 自身错误、系统时间、代理和实际网络；不中断任务的要求优先于这条历史方案。
- 原始参考：[Microsoft Store 社区问答](https://learn.microsoft.com/zh-cn/answers/questions/3838117/microsoft-store)。社区经验不等于产品修复承诺。
- 原记录安装后把 agent 和集成终端都设为 WSL；这是目标工作流，不是 Windows App 的安装前提。当前产品也支持原生 Windows，两个设置需要分别核实。
