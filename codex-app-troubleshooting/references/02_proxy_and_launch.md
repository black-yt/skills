# Clash、Windows/WSL 代理与桌面启动

## 核对实际端口和地址

- Clash/Clash Verge 重装可能恢复默认端口，旧进程或配置仍指向旧端口。以软件当前配置和监听结果为准，不把某个端口写成通用常量。
- Windows 系统代理、WinHTTP 代理、`HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY`、WSL shell 变量属于不同配置层；查看其中一项不能证明其他项一致。
- Windows 原生请求通常可使用 Windows 的 loopback 监听；WSL2 NAT 下的 `127.0.0.1` 指向 WSL 自身，需验证 Windows 主机地址。mirrored 模式可能支持 localhost，不能无条件改成网关地址。
- WSL NAT 中 `ip -4 route show default` 给出主机地址候选，但 VPN、自定义路由可能改变含义；必须实际连通性验证，不能直接把候选写入全局设置。
- 不从 `/etc/resolv.conf` 的 nameserver 武断推导代理主机；DNS tunneling 模式下该地址可能是合成地址。
- WSL 要访问 Windows 监听时，按需开启代理软件的 LAN 访问，并限制防火墙到所需 WSL 网络；不要向所有网络开放一个未认证代理。

Windows 检查指定端口，替换占位值后执行：

```powershell
$proxyPort = [int]'[PORT]'
Get-NetTCPConnection -State Listen -LocalPort $proxyPort |
    Select-Object LocalAddress, LocalPort, OwningProcess
```

Linux/WSL 检查候选地址后，使用 reference 1 的显式代理探针，再验证实际 App 进程。

## 进程环境与优先级

- 进程启动时继承父进程环境；修改用户变量不会改写已经运行的 App、Explorer、终端或 WSL 后端。
- 用 `scripts/inspect_proxy_env.py --pid [PID]` 只读检查已核实的 Linux/WSL 后端。当前 shell 的输出不能代表目标进程。
- Linux 中大写和小写代理变量可能并存，不同客户端优先级不同；先查实际值是否冲突，再精确修改产生冲突的来源。
- `HTTPS_PROXY` 指的是 HTTPS 目标使用的代理，并不要求代理 URL 是 `https://`。Clash 的 HTTP/mixed 代理通常使用 `http://[HOST]:[PORT]`；不要把 SOCKS 监听当 HTTP 代理。
- 检查残留 `ALL_PROXY`、已有 `NO_PROXY` 和绕过规则；不要删除整个 bypass 列表，避免让内网 API 或当前 agent 中转链路失效。
- 从 WSL 发起 Windows 程序时，Windows 子进程可能继承调用者的旧值。诊断启动器要显式使用本次已验证的变量，而不是假定当前工具进程环境正确。

## 端口变化案例与分层取证

完整保留一次已解决案例的三个阶段，主机地址以占位符表示：

| 阶段 | 系统代理/环境变量 | 观察结果 |
| --- | --- | --- |
| Clash 重装后 | Windows 系统代理已到 `127.0.0.1:7897`，用户 HTTP/HTTPS 环境变量仍到 `[WINDOWS_HOST]:7890` | 旧端口不可达，浏览器正常而 App 失败 |
| 首次修正 | 将环境变量改到 `127.0.0.1:7897` | Windows 探针正常；实际 WSL 登录后端连接自己的 loopback，仍失败 |
| 最终修正 | 环境变量改为两侧都实测可达的 `[WINDOWS_HOST]:7897`，系统代理仍是 loopback | 新 WSL 后端继承正确 URI，正常桌面启动与真实 OAuth 均通过 |

- 因此系统代理和环境变量不必显示相同字符串，关键是各自的消费者可达；保留有效的 7897，不要求退回 7890。
- 当时 Clash 对应配置为 `mixed-port: 7897`、`allow-lan: true`，监听和 Windows 防火墙允许所需 WSL 来源；此配置只作为案例，不能把代理端口向所有网络开放。
- `.bashrc` 在很多发行版开头有以下逻辑，写在后面的代理配置不会被非交互 shell 读取；直接执行后端更可能完全跳过 shell 配置：

```bash
case $- in
    *i*) ;;
      *) return ;;
esac
```

Windows 只查询必要的系统代理字段与环境变量，代理值显示时去除用户信息和 URL 附带内容：

```powershell
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' |
    Select-Object ProxyEnable, ProxyServer
foreach ($scope in 'Process', 'User', 'Machine') {
    foreach ($name in 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY') {
        $value = [Environment]::GetEnvironmentVariable($name, $scope)
        $summary = '[unset]'
        if ($value) {
            try {
                $u = [uri]$value
                if (-not $u.IsAbsoluteUri -or -not $u.Host) { throw 'Invalid URI' }
                $summary = '{0}://{1}:{2}' -f $u.Scheme, $u.DnsSafeHost, $u.Port
            } catch { $summary = '[set; unrecognized URI]' }
        }
        [pscustomobject]@{ Scope = $scope; Name = $name; Proxy = $summary }
    }
    [pscustomobject]@{
        Scope = $scope; Name = 'NO_PROXY'
        Configured = [bool][Environment]::GetEnvironmentVariable('NO_PROXY', $scope)
    }
}
```

- PAC/`AutoConfigURL` 也可能影响系统代理；需要时只读检查并隐藏其中私有地址或 query，不能原样发布。
- App 历史日志位置 `%LOCALAPPDATA%\Codex\Logs\YYYY\MM\DD`，证据包括 `spawnCommand=wsl.exe` 和 `.codex\bin\wsl\...\codex`。路径随版本变化，先验证当前实际位置。
- 在 Linux 只定位目标 app-server 的 PID、启动时间和可执行路径，再用脱敏脚本读取环境。`/proc/[PID]/environ` 反映可见的进程环境区，不保证捕获程序运行中所有内部改写；读取被拒绝不能当作“变量不存在”。
- 原探针从 Windows 与 WSL 分别测试旧端口、新 loopback 和新宿主机地址；完整比较这五种观察结果，才能解释“一边能用另一边不能用”。
- 收到 `200 Connection established` 及目标 `405 Method Not Allowed` 说明本次 CONNECT/HTTPS 请求到达了响应阶段；协议可能是 HTTP/1.1 或 HTTP/2。这是无凭据 GET，不代表账号/授权成功；403 或证书错误仍须继续调查。

## 备份与最小持久化

先以单次启动/进程范围验证目标 URI。只有明确需要让未来桌面启动继承时，才修改用户变量；用户变量会影响其他新启动程序，不是 App 专属设置。

下面是 **Windows PowerShell** 模板。替换占位 URI 为在实际请求环境验证可达的 HTTP 代理；不包含任何账号密码。

```powershell
$proxyUri = 'http://[REACHABLE_PROXY_HOST]:[PORT]'
$uri = [uri]$proxyUri
if ($uri.Scheme -ne 'http' -or -not $uri.Host -or $uri.UserInfo -or
    $uri.AbsolutePath -ne '/' -or $uri.Query -or $uri.Fragment) {
    throw 'Expected an HTTP proxy host and port without credentials or URL suffixes'
}
$backupPath = Join-Path $env:USERPROFILE ('codex-proxy-backup-' + [guid]::NewGuid() + '.json')
$backup = @{}
foreach ($name in 'HTTP_PROXY', 'HTTPS_PROXY') {
    $backup[$name] = [Environment]::GetEnvironmentVariable($name, 'User')
}
$backup | ConvertTo-Json | Set-Content -LiteralPath $backupPath -Encoding UTF8
foreach ($name in 'HTTP_PROXY', 'HTTPS_PROXY') {
    [Environment]::SetEnvironmentVariable($name, $proxyUri, 'User')
    [Environment]::SetEnvironmentVariable($name, $proxyUri, 'Process')
}
```

- 备份可能包含已有代理凭据，必须保存在用户私有位置，不提交或分享；无需把旧值打印出来。
- 上例不修改 WinINET 系统代理、WinHTTP、WSL shell 配置、`ALL_PROXY` 或 `NO_PROXY`，这些层只有被证据指向时才单独调整。
- 若 App 实际在 WSL 请求，但 Windows 用户变量未传到该后端，找出真实启动链和支持的传递方式；不要盲目追加 `.bashrc`，非交互启动不一定读取它。
- 若不同消费者需要不同 URI，优先局部启动配置；不要为了 App 让其他新进程的代理失效。

可对已修改的用户环境广播通知；它不能保证所有已运行程序刷新：

```powershell
if (-not ('CodexProxyEnvironmentNotify' -as [type])) {
    Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class CodexProxyEnvironmentNotify {
    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern IntPtr SendMessageTimeout(
        IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam,
        uint flags, uint timeout, out UIntPtr result);
}
'@
}
$result = [UIntPtr]::Zero
[void][CodexProxyEnvironmentNotify]::SendMessageTimeout(
    [IntPtr]0xffff, 0x001A, [UIntPtr]::Zero, 'Environment', 2, 3000, [ref]$result)
```

## 正常启动验收与回滚

1. 识别哪些 App/后端进程需要新环境，确认没有用户要求保护的活动任务依赖它们；不能一律重启所有 Codex 或 WSL。
2. 通过用户日常的桌面快捷方式启动，再定位实际新进程，确认代理地址和端口正确。CLI 或临时脚本成功不替代这一步。
3. 重新执行真实登录流程；浏览器授权成功之后，确认 App 完成 token exchange 并显示正确认证状态。
4. 核对原有 provider 和内网访问仍正常，受保护的对话进程与历史没有损失。
5. 如果用户要“直接双击启动”，最终方案不能依赖每次手动运行辅助脚本。可以保留诊断脚本，但必须解释其是否必需。
6. Windows 主机网关可能随 WSL 重建改变。若持久化了 NAT 地址，应记录重新发现和验证方法；不要承诺一个地址永久有效，也不要为此擅自切换 WSL 网络模式。

回滚只恢复本次备份中的变量；原来缺失的用户变量应移除覆盖。重新通知并检查新进程，不能用回滚覆盖用户后续修改。

以下回滚模板先验证两个字段都存在，再执行修改，避免只恢复一半才发现备份错误：

```powershell
$backupPath = '[THIS_OPERATION_BACKUP_JSON]'
$previous = Get-Content -LiteralPath $backupPath -Raw | ConvertFrom-Json
foreach ($name in 'HTTP_PROXY', 'HTTPS_PROXY') {
    if ($previous.PSObject.Properties.Name -notcontains $name) {
        throw "Missing backup field: $name; no settings restored"
    }
    if ($null -ne $previous.$name -and $previous.$name -isnot [string]) {
        throw "Invalid backup value: $name; no settings restored"
    }
}
foreach ($name in 'HTTP_PROXY', 'HTTPS_PROXY') {
    [Environment]::SetEnvironmentVariable($name, $previous.$name, 'User')
}
```

当前已正常时不执行回滚。最终分别验收配置写入、新进程继承、后端网络、真实 OAuth 四层；修复后也核对原先使用中转 API 的 CLI 仍正常，不能通过 killall、重启整机或 WSL 来替代。

官方网络依据：[WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking)，2026-10-03 实际 GET 核对。它说明 NAT、mirrored 与主机访问方式，具体代理软件仍需以当前监听配置为准。
