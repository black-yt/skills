---
name: wsl-bash-windows
description: "当在 Windows + WSL 项目中运行 shell 命令、排查 bash/沙箱启动失败、处理 /mnt/c 或 /mnt/d 路径、读取用户贴来的 Windows 图片/临时截图路径、执行 curl/git/npm/python 等 Linux 命令、排查 GitHub/Hugging Face push、DNS、代理或 token 环境差异、避免误切到 PowerShell/cmd/Windows Node/browser fetch 时使用。"
---

# WSL Bash on Windows

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 记录 WSL bash 中执行 GitHub 与 Hugging Face push 的安全流程，覆盖非交互/交互 shell token 差异、一次性 HTTP Basic header、DNS 解析失败、坏代理、沙箱网络、`.git/index.lock` 提权、LFS/Xet 边界和 push 后状态验证。 | WSL push、GitHub、Hugging Face、HF、git push、DNS、getent hosts、proxy、HTTP_PROXY、bash -ic、token env、http.extraheader、credential.helper、LFS、Xet、index.lock、Read-only file system、ahead 1 | 在 WSL 项目中 push GitHub 或 Hugging Face 前必须读取；排查 `Could not resolve host`、代理端口不可达、`You are not authorized to push to this repo` 前必须读取；发现 token 只在交互 shell 中存在、普通 shell 网络失败、`.git/index.lock` 写入失败、HF LFS/Xet 或大文件边界不清时必须读取 | [references/push-dns.md](references/push-dns.md) |

## 核心判断

- 看到 `cwd` 或项目路径是 `/mnt/c/...`、`/mnt/d/...`，默认这是 WSL 项目。
- 在 WSL 项目里优先使用 WSL 的 `bash` 和 Linux 命令链，不要绕到 PowerShell、cmd、Windows 侧 `node.exe`、浏览器 `fetch`。
- 如果普通执行失败，先判断是不是沙箱启动失败，而不是误判为“系统没有 bash”。
- Codex 桌面端可能出现“UI 显示 WSL workspace，但实际执行器在 Windows 侧直接找 `/bin/bash`”的混合坏状态；这时不能继续改文件。
- 有些失败只是普通沙箱权限不足或没有提权，不代表 WSL bash 坏了；例如写 `.git/index.lock`、访问受限路径、联网命令或安装依赖时失败，应优先申请提权/原生 WSL 执行。
- 典型沙箱失败包括：

```text
Unable to spawn ... codex-linux-sandbox because it doesn't exist
```

或一开始表现成：

```text
CreateProcess ... No such file or directory
```

- 这些错误通常说明受限沙箱或运行包装器启动失败；正确处理是申请脱离沙箱，用原生 WSL bash 执行，而不是切换到 Windows 工具链。
- 如果错误形态是 `CreateProcess` + `/bin/bash` + `No such file or directory`，通常表示 Windows 执行器误拿了 WSL shell；应先让用户重启/修复 Codex 桌面端的 WSL 绑定。

## 标准流程

1. 先用 WSL bash 确认当前目录：

```bash
pwd
```

期望输出形如：

```text
/mnt/d/[workspace]/[project]
```

2. 如果 `pwd` 能在 WSL bash 中返回正确路径，后续命令都继续走 WSL bash。
3. 如果普通执行报沙箱启动失败，直接申请用原生 WSL bash 执行当前命令。
4. 如果普通执行报 `Read-only file system`、`Permission denied`、无法创建 `.git/index.lock`、网络受限或依赖下载失败，先判断是否只是没有提权；需要时申请提权执行，不要切到 Windows 工具链。
5. 网络命令如 `curl`、`git fetch`、`git push`、`npm install`、`pip install` 如果受网络或沙箱限制，也应使用 WSL bash 的提权执行。
6. 正式改文件前确认三件事：`pwd` 返回 `/mnt/...`，交互 `PS1` 显示 WSL prompt，`apply_patch` 探针闭环成功。
7. 执行完后用项目内检查命令验证结果，例如 `git status --short`、`git diff --check`、`pwd`、`command -v <tool>`。

## 交互 Shell 与 PS1

默认工具命令可能是非交互 WSL bash，`PS1` 为空是正常现象；需要确认交互初始化时，用：

```bash
bash -i -c 'printf "%s\n" "$PS1"'
```

这里检查的是 bash 是否按交互 shell 初始化，不是检查是否有完整 TTY：

- `bash -i` 强制进入 interactive mode。
- `-c '...'` 执行一条命令后退出。
- `"$PS1"` 读取交互 shell 的提示词模板。
- `printf` 把变量原样打印出来。

正常交互 prompt 可能包含：

```text
(base) [user]@[host]:/mnt/d/[workspace]/[project]$
```

原始 `PS1` 可能包含颜色和窗口标题控制码，形如：

```text
(base) \[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$
```

读取要点：

- `(base)`：当前交互 shell 启用了 Conda base 或类似环境。
- `[user]@[host]`：WSL 用户名与主机名。
- `/mnt/d/...`：当前目录是 WSL 挂载的 Windows 盘路径。
- `$`：普通用户 shell。
- `\[\033[01;32m\]`、`\[\033[01;34m\]` 等是颜色控制码，不影响命令执行。
- `\[\e]0;\u@\h: \w\a\]` 是终端窗口标题控制码，不影响命令执行。
- 如果启动 `bash -i` 后第一秒没有看到 prompt，不一定异常；交互 shell 可能先输出警告，需要继续读取直到看到类似 `[user]@[host]:/mnt/...$` 的 prompt。

如果 `bash -i` 输出：

```text
bash: cannot set terminal process group (...): Inappropriate ioctl for device
bash: no job control in this shell
```

通常只是 Codex 工具没有完整 TTY，影响 `Ctrl+Z`、`fg`、`bg` 等 job control，不影响 `pwd`、`git status`、`npm test`、`python script.py` 或 `apply_patch`。

也就是说，`tty` 检测的是有没有真实或伪终端；`PS1` 检测的是 bash 是否按交互 shell 初始化。两者相关，但不是一回事。

## 路径规则

Windows 路径：

```text
D:\[workspace]\[project]
```

WSL 路径：

```bash
/mnt/d/[workspace]/[project]
```

规则：

- `C:\...` 对应 `/mnt/c/...`。
- `D:\...` 对应 `/mnt/d/...`。
- 中文路径、空格路径或特殊字符路径要整体放在 `workdir` 中；如果命令里必须手写路径，使用引号。
- 按当前环境给出的 `cwd` 为准，不要凭记忆改大小写。
- 在大小写敏感或跨文件系统场景里，`Project`、`project`、`PROJECT` 可能不是同一个路径。

## 用户图片路径读取

用户贴来的 Windows 图片路径可能不能被 WSL 直接读取，例如：

```text
C:\Users\[USER]\AppData\Local\Temp\[IMAGE].png
```

先转换成 WSL 路径：

```text
/mnt/c/Users/[USER]/AppData/Local/Temp/[IMAGE].png
```

转换规则：

- `C:\Users\...\file.png` 对应 `/mnt/c/Users/.../file.png`。
- `D:\...\file.png` 对应 `/mnt/d/.../file.png`。
- 反斜杠 `\` 改成正斜杠 `/`。
- 不要把用户的真实临时路径写进仓库文档；skill 中使用 `[USER]`、`[IMAGE]` 等占位符。

读取前先确认文件仍存在：

```bash
ls -l "/mnt/c/Users/[USER]/AppData/Local/Temp/[IMAGE].png"
```

如果文件存在，用转换后的 WSL 路径交给图片查看工具；如果不存在，通常是临时截图文件已经被清理，需要请用户重新上传或重新截图。

## 命令执行规则

- 使用 Linux 命令：`bash`、`pwd`、`ls`、`rg`、`sed`、`python3`、`curl`、`git`、`npm`、`node`。
- 如果 `node` 不在当前 `PATH`，先检查是否是 `nvm` 没在非交互 shell 中加载；不要直接判断为没有 Node。

```bash
if [ -s "$HOME/.nvm/nvm.sh" ]; then
  . "$HOME/.nvm/nvm.sh"
fi
node -v
npm -v
```

- 如果 `npm`/`npx` 指向 `/mnt/c/Program Files/nodejs/...`，但 `node` 不存在，说明当前 shell 混入了 Windows Node 路径；在 WSL 项目里应加载 WSL/Linux 侧 Node，而不是调用 Windows shim。
- 不要因为一次沙箱启动失败就尝试 `cmd.exe`、`powershell.exe`、Windows `node.exe` 或浏览器侧 `fetch`。
- 需要联网、访问受限路径、写 `.git`、运行安装命令、绕过坏掉的沙箱包装器时，申请原生 WSL bash 或提权执行。
- 对一次性简单命令可以直接跑；对多步调试先跑 `pwd` 和 `git status --short` 确认位置。
- 不要把临时文件散落在项目根目录或 `/tmp`；如果必须临时写入，用后清理。
- 文件修改必须优先用标准 `apply_patch`；如果 `apply_patch` 异常，应先汇报并修环境，不要用 `cat > file`、Python 写文件或 `sed -i` 绕过。

## apply_patch 探针

`apply_patch` 可用性必须做真实闭环，不只看工具返回 `Success`。

1. 用 `apply_patch` 新建临时探针文件：

```patch
*** Begin Patch
*** Add File: .codex_apply_patch_probe.tmp
+apply_patch probe ok
*** End Patch
```

2. 用 bash 读取：

```bash
cat .codex_apply_patch_probe.tmp
```

期望输出：

```text
apply_patch probe ok
```

3. 用 `apply_patch` 删除：

```patch
*** Begin Patch
*** Delete File: .codex_apply_patch_probe.tmp
*** End Patch
```

4. 用 bash 确认删除：

```bash
test ! -e .codex_apply_patch_probe.tmp && printf 'probe removed\n'
```

只有新建、读取、删除、确认删除都成功，才能认为 `apply_patch` 和当前 WSL 文件系统视图可信。

坏状态特征：

- `apply_patch` 新建文件返回 `Success`，但 bash 看不到文件。
- 同一个文件能重复 `Add File` 且每次都成功。
- 刚新建的文件用 `apply_patch` 删除时报 `No such file or directory`。
- `exec_command` 跑 `pwd` 报 `CreateProcess` 找不到 `/bin/bash`。
- Node 或其他工具出现 Windows 风格错误，例如“目录名称无效”。

遇到这些情况时，停止改项目，先告诉用户执行器没有真正进入 WSL 或文件系统视图不可信，再修复 Codex/WSL 环境。

## 异常处理顺序

遇到 WSL、沙箱或 `apply_patch` 异常时，按这个顺序处理：

1. 先测：

```bash
pwd
```

2. 如果出现 `CreateProcess` + `/bin/bash`，判断当前执行器不是正常 WSL bash。
3. 立即停止用替代方式写文件，并告知用户：

```text
当前执行器没有真正进入 WSL，apply_patch 结果不可信，需要先修复环境。
```

4. 让用户完全重启 Codex 桌面端；不要只关闭窗口，必要时退出托盘进程。
5. 重启后重新打开 WSL workspace。
6. 重新测试：

```bash
pwd
bash -i -c 'printf "%s\n" "$PS1"'
```

7. 最后执行 `apply_patch` 新建、读取、删除、确认删除的探针闭环。

## 桌面端配置边界

- 如果项目路径是 `/mnt/c/...` 或 `/mnt/d/...`，Codex 执行器也必须在 WSL 内运行，shell 使用 `/bin/bash`。
- 如果使用 Windows 后端，项目路径应该是 Windows 风格，例如 `C:\[workspace]\[project]` 或 `D:\[workspace]\[project]`，shell 应该是 PowerShell 或 CMD。
- 最危险的混合状态是：Windows 执行器 + `/mnt/d/...` 路径 + `/bin/bash` shell。这会让 Windows 的 `CreateProcess` 直接查找 Linux 路径 `/bin/bash`，并导致文件系统视图和工具结果不可信。
- UI 显示 WSL workspace 不足以证明执行器真的在 WSL 内；必须用 `pwd`、交互 `PS1` 和 `apply_patch` 探针闭环确认。

## 网络命令示例

用 WSL bash 直接执行 `curl`：

```bash
curl -sS -X POST '[URL]' \
  -H 'Content-Type: application/json' \
  -d '{"msg_type":"text","content":{"text":"这是一条来自 WSL bash 的测试消息。"}}'
```

成功响应可能形如：

```json
{"StatusCode":0,"StatusMessage":"success","code":0,"data":{},"msg":"success"}
```

注意：

- 示例里的 `[URL]` 必须替换为用户提供的真实地址，但不要把真实 webhook 写进仓库。
- 如果调用飞书/Lark 自定义机器人，优先配合 `feishu-bot` skill 检查签名、关键词、IP 白名单和错误码。
- 如果命令返回网络错误，先区分代理、DNS、证书、沙箱网络和服务端鉴权，不要立刻改代码。
- 如果网络命令是 `git push`、Hugging Face push 或认证相关操作，先读取 [references/push-dns.md](references/push-dns.md)，区分 GitHub/HF 平台规则、token 所在 shell、DNS/代理状态和是否需要提权。

## 排查清单

- `pwd` 是否显示 `/mnt/c/...` 或 `/mnt/d/...`。
- `git status --short` 是否能在同一个 WSL 目录执行。
- 报错是否包含 `codex-linux-sandbox` 或 `CreateProcess ... No such file or directory`。
- 报错是否只是权限/沙箱限制，例如 `Read-only file system`、`Permission denied`、无法创建 `.git/index.lock`、网络受限；这类情况优先提权，不要误判成 bash 坏了。
- 是否误用了 Windows 路径分隔符 `\` 作为 Linux 命令参数。
- 是否因为中文路径或空格路径没有加引号导致参数被拆开。
- 是否误切到 PowerShell、cmd、Windows Node 或浏览器 fetch。
- 网络命令是否需要代理、关闭代理或提权执行。
- 任务结束后是否清理了临时文件，并确认没有在仓库里留下无关生成物。

## 一句话原则

这是 WSL 项目，就使用 `/mnt/c/...` 或 `/mnt/d/...` 路径、WSL bash 和 Linux 命令；如果沙箱坏了，就申请原生 WSL bash，不要换 Windows 工具链。
