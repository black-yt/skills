# Windows 更新未完成、旧界面与运行环境下载

用于“更新中断后像旧版”“重开后界面恢复”“后台组件一直下载”及失败下载占用磁盘。先区分下面三层，再选择修复对象。

| 层次 | 证据 | 不能替代的验收 |
| --- | --- | --- |
| 桌面程序包 | 当前窗口的进程路径、Appx 注册版本、包状态、部署事件 | 开始菜单的名字或界面风格不能证明二进制版本 |
| 配套主运行环境 | `runtime.json`、`primary-runtime-installer` / `install-primary-runtime` 日志、下载目录 | `download_archive` 失败不等于桌面程序包部署失败 |
| 当前界面与配置加载 | 用户实际看到的界面、重开时间、相同进程/包版本下的变化 | 同版重开后恢复，不能单独证明刚完成程序升级，也不能证明是运行环境下载导致 |

## 先核实程序与安装状态

在 Windows PowerShell 执行；没有 Windows 工具权限时说明限制，不拿 WSL CLI 版本替代。

```powershell
$package = Get-AppxPackage -Name 'OpenAI.Codex'
$package | Select-Object Name, Version, PackageFullName, InstallLocation,
    Status, IsPartiallyStaged

Get-Process -Name 'ChatGPT', 'Codex' -ErrorAction SilentlyContinue |
    Select-Object ProcessName, Id, StartTime, Path

Get-StartApps | Where-Object { $_.Name -match 'Codex|ChatGPT' } |
    Select-Object Name, AppID
```

- **对照四种版本**：App 关于页面/`package.json`、Windows MSIX 四段版本、实际后端 CLI 版本、主运行环境 `bundleVersion` 各自记录，不按字符串直接混比。可执行文件属性中的 `ProductVersion` 也可能对应内嵌 Chromium，不自动当作 App 发布版本。
- **确认入口**：当前样本的包身份仍为 `OpenAI.Codex`，开始菜单可显示 ChatGPT，入口可为 `app/ChatGPT.exe`。名称变化本身不是启动了另一份旧安装；以当前包 manifest 和实际路径为准。
- **对照前后状态**：重开后再次记录 PID、开始时间、路径和包版本。`Status = Ok`（某些输出显示枚举数值 `0`）、`IsPartiallyStaged = False` 说明当前注册包没有报告相应异常，不证明远端没有更高版本。
- **查真正部署失败**：怀疑 MSIX 中断或回退时，检查 `Microsoft-Windows-AppXDeploymentServer/Operational` 的相关时间窗，提取目标包版本、事件时间和 HRESULT；也核对安装渠道及更新策略。不要默认用 `Get-AppxPackage -AllUsers`，不要公开完整事件或私有账号路径。
- **及时采纳用户观察**：用户说重开后恢复，就核对恢复后的状态；不要为了复现旧界面反复重启、切换账号或卸载。无法确认界面变化的触发点时直接写未确定。

## 确认运行环境失败在哪一步

历史 Windows 路径如下，先验证当前版本是否仍使用它们：

| 位置或字段 | 用途 |
| --- | --- |
| `%LOCALAPPDATA%\Codex\Logs\YYYY\MM\DD` | App、更新器及主运行环境安装日志 |
| `%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\runtime.json` | 当前归档方式安装的主运行环境元数据 |
| 同级 `codex-runtime-install-*` | 单次安装的下载/解包临时目录；不是已安装环境 |
| 临时目录中的 `node-runtime.tar.gz`、`payload` | 下载归档与解包内容；文件名不代表只包含 Node |
| 同级 `codex-primary-runtime.previous-*` | 替换时保留的旧运行环境，可能仍有进程使用，不能按下载垃圾处理 |

Windows 原生包/框架方式安装的运行环境可能使用其他位置。找不到上述文件时先确认安装方式，不创建空 `runtime.json` 或手工拼装目录。

读取已安装版本，只输出必要字段：

```powershell
$runtimeRoot = Join-Path $env:USERPROFILE '.cache\codex-runtimes'
$metadata = Join-Path $runtimeRoot 'codex-primary-runtime\runtime.json'
if (Test-Path -LiteralPath $metadata) {
    Get-Content -LiteralPath $metadata -Raw | ConvertFrom-Json |
        Select-Object bundleVersion, bundleFormatVersion, targetPlatform, targetArch
}
```

在最近且相关的日志中，只提取组件、事件时间和这些字段，不输出整份日志或运行时配置：

- `bundleVersion`、`release`、`trigger`（例如 `startup_missing`、`manual_install`）。
- `failureStage`、`failureReason`、`networkErrorCode`、`outcome`。
- 必要时记录归档主机、版本及大小；移除 URL 的凭据、query、安装 ID 和原始调用 ID。
- 区分 `download_archive`、解包/验证、安装后 `sync_plugins`。归档已安装后插件同步失败，不能重新归类为下载失败。

| 观察 | 后续处理 |
| --- | --- |
| `failureStage=download_archive`，`networkErrorCode=ERR_CONNECTION_CLOSED` | 下载连接中断；在实际请求环境核对网络、代理与下载源，不清认证、不认定包注册坏了 |
| 归档长度/哈希或解包验证失败 | 保留错误与目标版本，使用应用支持的重试重新取得包；不解包覆盖已安装目录 |
| `failureStage=sync_plugins` | 检查对应插件同步错误、目录访问与版本兼容性；下载完成不代表整个安装完成 |
| 只有开始/下载来源记录，没有成功或失败结果 | 继续看活动文件增长和进程，不凭一段未结束日志宣称完成或卡死 |
| `outcome=installed` 或 `already-current` | 再核对已安装元数据与后续配置阶段；二者都通过后才报告运行环境更新完成 |

**版本样本（2026-11-04，UTC 日志日期）**：桌面注册包为 `26.1029.7803.0`，App 的 `package.json` 为 `26.1029.61003`，已安装主运行环境为 `26.1026.10807`。当时应用选取的目标为 `26.1103.20233`，存在下载连接中断记录；重开后用户确认界面恢复，但前后桌面程序包版本相同。因此只能分别确认界面恢复与运行环境下载故障，不能把后者写成前者的已证实根因。这些数字是样本，不是升级目标。

后续一次下载曾持续增长到数十 MB，但约 13 分钟后仍以 `ERR_CONNECTION_CLOSED` 结束，其临时目录随后消失，已安装版本未变。这说明短探针成功、下载持续增长、临时目录消失都不能替代最终安装结果；目录消失也可能是安装器失败后的清理。该样本只定位到长时间下载连接中断，没有足够证据把断开归因于某个代理实现、CDN 节点或界面问题。

## 恢复与以后遇到时的处理

1. **先恢复可达链路**：OAuth 的代理端口失效按 [01](01_oauth_diagnosis.md) / [02](02_proxy_and_launch.md) 核验，修正已证实错误的配置。OAuth endpoint 可达，不代表更新 CDN 的大文件下载稳定；反过来也一样。
2. **比较实际下载路径**：Windows 系统代理、用户环境代理、WSL 代理分别记录。Electron 下载不保证使用 `HTTP_PROXY` / `HTTPS_PROXY`；终端测试成功不能替代应用下载。必要时对日志中已核实的 HTTPS 归档做有超时、限量的小段请求，比较系统默认路径与显式代理，记录状态和耗时。
3. **解释探针边界**：HTTP `206` 只证明这一小段下载成功，不能证明完整归档能下载完。两种路径都成功时，不把“系统代理关闭”单独判为根因，也不为了试验开启全局代理。HTTP `403` 要确认响应来源、授权/策略与发布通道，不泛化为全部网络不可用。
4. **判断下载是否推进**：间隔一段时间重新取得活动归档的大小与写入时间；每次重新查询文件，避免复用缓存的 `FileInfo`。大小持续增长时保留当前安装进程，说明速度偏慢，不反复重开让下载从头开始。单次零字节、短暂不增长或没有末尾日志都不足以判死。
5. **下载中断后有限重试**：先完成独立检查、修正有证据的问题，再用该版本应用支持的更新/重试入口发起一次新尝试，观察最终安装与插件配置结果。同一阶段再次失败就保留错误并重新定位，不循环重试、不切换 stable/alpha 通道、不直接改 CDN 地址。
6. **程序包更新失败另走安装渠道**：检查应用的 Check for Updates、Microsoft Store 或组织部署策略。需要重新打开时先识别受保护任务，按正常退出方式处理所需窗口/后端；关闭窗口可能仍驻留托盘，不用批量杀进程代替退出。
7. **恢复后核对**：从日常开始菜单/快捷方式启动，确认实际包路径、登录和目标界面；运行环境单独确认目标版本、安装后配置与应用使用结果。对“界面已恢复、后台运行环境仍在下载”分别报告，不强求重装。

不要通过删除 `.codex`、认证缓存、数据库或当前运行环境来促成更新。暂存/注册新 MSIX、框架包安装和手工替换运行环境目录是不同操作；没有对应版本的安装失败证据时，不选其中任意一种作为通用修复。

## 失败下载的磁盘清理

仅在用户要求清理，或现有授权已经包含该清理时执行。诊断/提 PR 不自动授权删除本机数据；已明确授权时无需重复询问。

**先预览**：只枚举已确认的运行环境根目录下的临时安装子目录，不把 `.cache` 或整个运行环境根目录当清理目标。

```powershell
$runtimeRoot = Join-Path $env:USERPROFILE '.cache\codex-runtimes'
Get-ChildItem -LiteralPath $runtimeRoot -Directory -Filter 'codex-runtime-install-*' |
    ForEach-Object {
        $archive = Join-Path $_.FullName 'node-runtime.tar.gz'
        if (Test-Path -LiteralPath $archive -PathType Leaf) {
            Get-Item -LiteralPath $archive |
                Select-Object DirectoryName, Length, LastWriteTimeUtc
        }
    }
```

- **判定闲置**：对候选记录大小、最后写入时间、对应安装日志和活动进程。近期仍增长的归档、仍持有文件句柄的目录、正在解包或配置的安装都保留；归档大小不增长也可能正在解包，不能只看归档判断。
- **检查占用**：在 Windows 可用短暂的 `[IO.File]::Open($archive, 'Open', 'Read', 'None')` 检查独占读取是否可取得，立即 `Dispose()`。被拒绝说明要保留或继续核实，不提权、解锁或停止任务。该检查只覆盖此文件与此刻，不代表子目录无人使用，也不是无竞争的删除保证；还需确认没有进程/安装使用候选目录。
- **控制检查开销**：先从归档和实际进程路径筛选；部分 `payload` 含上万依赖文件，不默认逐文件打开或输出完整目录树。对确有需要的候选，再确认整个目录的近期写入、重解析点和占用情况。
- **列明边界**：`codex-primary-runtime` 是已安装环境；`codex-primary-runtime.previous-*` 是旧环境保留目录；二者都不属于这次下载临时目录清理。`previous-*` 即便清理时报文件占用，也不能因此杀 Node 或删除当前环境。
- **按明确目录删除**：先把候选固定为具体清单，复核它们是根目录的直接子目录、名称为 `codex-runtime-install-*`、没有指向范围外的重解析点。删除前再次检查写入/占用；只删除已确认闲置的精确路径，遇到锁、权限问题或状态变化就跳过。不要用通配符递归删除，不自动改 ACL、清只读属性或接管权限。
- **区分大小**：归档合计不包含已展开的 `payload`，不等于整个临时目录总量；最终报告实际删除目录数、预先统计的文件总字节数与核验结果，注明它不等于精确磁盘可用空间增量。
- **清理后验收**：确认目标已消失，已安装元数据及其路径保持有效；活动下载如果仍存在，复查它的增长/安装结果；如果目录自行消失，按对应安装日志区分成功、失败后清理和中止。不能把“临时文件已删”写成更新已完成，也不为验证清理反复重启应用。

## 官方依据与适用边界

- 2026-11-04 实际 GET 核对：[Windows 桌面应用](https://learn.chatgpt.com/docs/windows/windows-app)、[Windows 部署](https://learn.chatgpt.com/docs/enterprise/windows-deployment)、[更新管理](https://learn.chatgpt.com/docs/enterprise/manage-app-updates)。部署文档说明更新需要访问 `persistent.oaistatic.com`，应用内更新与 Store/组织部署是不同来源；这些滚动文档不保证某个旧版本的内部目录结构。
- 上述运行环境日志字段、归档临时目录与历史版本值来自已安装 App 的只读检查。没有可核实的桌面 App 上游 commit，不拿开源 CLI 的 HEAD 冒充 App 源码版本。
- 下载文件大小、文件锁和短请求探针只是分层证据；公开分享时仅保留必要错误、通用路径和软件版本，移除账号、私有主机、OAuth 内容及原始日志。
