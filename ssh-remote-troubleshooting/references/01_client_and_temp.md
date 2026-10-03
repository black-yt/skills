# 客户端差异与 Windows 临时目录

## 先确定失败在哪一侧

| 日志现象 | 优先判断 | 验证方式 |
| --- | --- | --- |
| 多次探测 `ssh.exe` 得到 `ENOENT`，最后打印 OpenSSH 版本 | PATH 中部分候选不存在，已经找到可用客户端 | 继续看后续连接命令，不把探测噪声当根因 |
| `cmd type` 管道启动后立即“拒绝访问” | 本地脚本读取或执行权限，也可能是 SSH 自身错误 | 分开测试脚本读取和同一客户端的 SSH，不直接修改远端权限 |
| `Permission denied (publickey)` | 用户、密钥、agent、配置或跳板差异 | 比较同一可执行文件的 `ssh -G [HOST]` 和必要的脱敏调试日志 |
| 能登录，但 `ssh -T [HOST] sh` 失败 | 非交互 shell、登录脚本、策略或 stdin 路径 | 用无副作用标记命令测试；检查 shell 启动输出 |
| 安装输出缺远端端口 | 上游安装或启动没有完成 | 查找最早的下载、磁盘、解压和进程启动错误 |

## Windows 只读检查

以下 PowerShell 命令在 **Windows** 执行。若维护的是 WSL 项目，项目编辑与 Git 仍在 WSL bash 中进行；不要混淆诊断目标和维护执行器。

```powershell
Get-Command ssh -All | Select-Object Source
& "$env:WINDIR\System32\OpenSSH\ssh.exe" -V
foreach ($scope in 'Process', 'User', 'Machine') {
    foreach ($name in 'TEMP', 'TMP') {
        [pscustomobject]@{
            Scope = $scope
            Name = $name
            Value = [Environment]::GetEnvironmentVariable($name, $scope)
        }
    }
}
```

- 读取 Remote SSH Output 中的实际 `ssh.exe`、配置路径和生成命令，再与成功的终端命令对照。
- `ssh -G [HOST]` 展开配置会含内部信息；只提取用于比较的字段，不发布完整内容或私钥。
- 不设置 `StrictHostKeyChecking=no` 绕过连接问题；主机指纹变化需要核实。
- 系统 `C:\Windows\Temp` 不是一概不可用；必须复现文件创建、读取或 ACL 问题后才归因。

测试当前进程的临时目录能否被 VS Code 所用的 `cmd.exe` 读取：

```powershell
$probe = New-TemporaryFile
try {
    Set-Content -LiteralPath $probe.FullName -Value 'temporary-file-readable' -Encoding ASCII
    & $env:ComSpec /d /c ('type "{0}"' -f $probe.FullName)
    if ($LASTEXITCODE -ne 0) { throw 'cmd could not read the temporary file' }
} finally {
    Remove-Item -LiteralPath $probe.FullName
}
```

## 修复已确认的用户 TEMP/TMP 问题

仅在已获授权的用户环境修复范围内执行。备份只包含这两个变量，不导出整个环境。

```powershell
$backupPath = Join-Path $env:USERPROFILE ('temp-env-backup-' + [guid]::NewGuid() + '.json')
$backup = @{}
foreach ($name in 'TEMP', 'TMP') {
    $backup[$name] = [Environment]::GetEnvironmentVariable($name, 'User')
}
$backup | ConvertTo-Json | Set-Content -LiteralPath $backupPath -Encoding UTF8

$tempDir = Join-Path $env:LOCALAPPDATA 'Temp'
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
foreach ($name in 'TEMP', 'TMP') {
    [Environment]::SetEnvironmentVariable($name, $tempDir, 'User')
    [Environment]::SetEnvironmentVariable($name, $tempDir, 'Process')
}
```

- 重跑临时文件探针；失败则停止，不对系统 Temp 执行递归改 ACL、取得所有权或清空目录。
- 注册表中的用户变量不会自动改写已运行 VS Code、Explorer 或终端的环境。让实际启动它的父进程获得新值，或在修正当前进程变量的 PowerShell 中启动客户端进行验证。
- 环境变更广播可让支持它的进程重新读取值，但不能保证所有现有进程更新。退出前保存编辑内容，只重启目标 VS Code 窗口/客户端；不要连带重启 WSL、SSH 服务或活动任务。
- 回滚时读取本次备份，将 `TEMP`、`TMP` 恢复到 `User` 范围；原值为 null 时移除该用户覆盖。新启动的进程也要重新检查。

## 验证非交互 SSH

用日志里的同一个 Windows SSH 可执行文件和 Host 别名测试：

```powershell
$sshExe = Join-Path $env:WINDIR 'System32\OpenSSH\ssh.exe'
$sshTarget = '[HOST]'
& $sshExe -T $sshTarget 'printf "remote-shell-ready\n"'
```

- 替换 `[HOST]`；对已有密钥登录可追加 `-o BatchMode=yes`，否则该选项会主动禁止密码和交互认证。
- Remote SSH 常使用 `-T -D [LOCAL_PORT] [HOST] sh` 或 `bash`，与交互登录不同。转发失败时检查端口占用和服务端转发策略。
- 远端 shell 配置若无条件打印菜单、启动交互程序或消费 stdin，可能破坏安装协议。只修正已证明有问题的非交互分支。
- 不复制日志里的 token、临时脚本文件名或本机端口作为长期配置。
