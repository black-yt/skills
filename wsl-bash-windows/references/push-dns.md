# WSL GitHub / Hugging Face Push 与 DNS 排障

## 目录

- [总体原则](#总体原则)
- [Shell 与 Token 环境差异](#shell-与-token-环境差异)
- [GitHub Push](#github-push)
- [Hugging Face Push](#hugging-face-push)
- [DNS 与代理问题判断](#dns-与代理问题判断)
- [何时需要提权](#何时需要提权)
- [Push 后验证](#push-后验证)
- [GitHub 与 Hugging Face LFS 边界](#github-与-hugging-face-lfs-边界)
- [推荐完整顺序](#推荐完整顺序)

## 总体原则

GitHub 和 Hugging Face 的 push 逻辑要分开处理：

- GitHub 代码仓库：普通 `git push` 通常即可，但要严格避免 LFS、大文件、误提交 ignored clone/cache。
- Hugging Face dataset/model 仓库：可以按 HF 官方机制使用 LFS/Xet，但认证、代理、缓存路径更容易出问题，推荐在必要时用一次性认证 header 推送。
- 不要把 token 写进 remote URL、credential store、README、AGENTS、命令日志或 shell history。
- 不要打印 token，也不要打印完整 auth header。
- 优先使用 WSL bash，不要在 Windows PowerShell、CMD、浏览器 fetch、Node REPL 之间乱切。

## Shell 与 Token 环境差异

WSL 中可能存在两类 bash 环境：

- 普通非交互 shell。
- 交互式 shell，例如 `bash -ic '...'`。

有时 token 只在 `bash -ic` 里存在，因为用户的 shell startup 文件只在交互式 shell 加载。

只检查 token 是否存在，不打印值：

```bash
python3 -c 'import os; print("TOKEN_ENV", "present" if os.environ.get("TOKEN_ENV") else "missing")'
```

如果普通 shell 是 `missing`，再试交互式 shell：

```bash
bash -ic 'python3 -c '\''import os; print("TOKEN_ENV", "present" if os.environ.get("TOKEN_ENV") else "missing")'\'''
```

如果交互式 shell 是 `present`，后续需要 token 的 push 可以用 `bash -ic` 包起来。不要因为普通 shell 缺 token 就改全局配置、写入 shell rc 文件或把 token 放进命令文本。

## GitHub Push

一般流程：

```bash
git status --short --branch --untracked-files=all
git diff --check
git add <files>
git commit -m "..."
git push
git status --short --branch --untracked-files=all
git rev-parse --short HEAD
```

如果 `.git/index.lock` 或 `.git` 写入被沙箱拦截，可能出现：

```text
fatal: Unable to create '.git/index.lock': Read-only file system
```

这通常不是 Git 坏了，而是沙箱权限问题。此时应申请提权执行对应 `git add` / `git commit`，不要改文件系统权限、不要乱删 `.git` 文件。

## Hugging Face Push

HF 仓库普通 push 如果报：

```text
You are not authorized to push to this repo.
```

不要反复普通 push，也不要改 remote URL。优先检查 token 是否在当前 shell 中存在；如果 token 只在交互式 shell 中存在，用 `bash -ic` 包住一次性 HTTP Basic header 推送。

```bash
bash -ic '
auth=$(python3 -c '\''import os,base64
t=os.environ["TOKEN_ENV"]
print("Authorization: Basic "+base64.b64encode(("hf_user:"+t).encode()).decode())
'\'')
git -c credential.helper= -c "http.extraheader=$auth" push
'
```

注意：

- `TOKEN_ENV` 替换成实际 token 环境变量名。
- 不打印 `$auth`。
- 不把 token 写到 remote URL。
- 不写 credential store。
- `credential.helper=` 用于避免系统 credential helper 写入失败或污染本机凭据。
- 如果命令失败，不要把完整 `http.extraheader` 或 token 复制到日志里。

## DNS 与代理问题判断

常见现象有三类。

1. DNS 解析失败：

```text
Could not resolve host: huggingface.co
```

检查：

```bash
getent hosts huggingface.co || true
getent hosts github.com || true
```

如果普通 shell 没结果，但提权环境能解析，说明普通沙箱网络/DNS 不可靠，应申请提权执行同一命令，而不是切到 Windows 工具链。

2. 代理端口不可达：

```text
Failed to connect to 172.x.x.x port 7890
```

检查代理变量：

```bash
env | grep -i proxy || true
bash -ic 'env | grep -i proxy || true'
```

有时普通 shell 没代理，但交互式 shell 从 Windows 环境继承了坏代理：

```text
HTTP_PROXY=http://...
HTTPS_PROXY=http://...
```

如果代理指向不可达端口，应在确认上下文后关闭或修正当前命令环境里的代理变量。不要把临时代理写进长期 shell 配置。

3. token 只在交互式 shell 有，但交互式 shell 代理坏：

- token 来源需要 `bash -ic`。
- 网络需要可用环境，必要时提权。
- 不能因为 `bash -ic` 下代理坏，就说 token 不可用。
- 也不能因为普通 shell 能联网，就忽略它可能缺 token。

## 何时需要提权

需要提权的典型情况：

- `git add` / `git commit` 写 `.git/index.lock` 被沙箱拦截。
- 普通环境 DNS 解析不到远端，但提权环境可以解析。
- 普通/交互式 push 因沙箱网络或代理问题失败，而同一命令在提权网络环境下可行。
- 依赖下载、远程 fetch、LFS/Xet 相关网络请求被沙箱限制。

提权时仍保持同一套安全原则：

```bash
bash -ic '
auth=$(python3 -c '\''import os,base64
t=os.environ["TOKEN_ENV"]
print("Authorization: Basic "+base64.b64encode(("hf_user:"+t).encode()).decode())
'\'')
git -c credential.helper= -c "http.extraheader=$auth" push
'
```

提权解决的是网络/沙箱问题，不是让命令变得更随意。仍然不要打印 token、不要写 credential store、不要改 remote URL、不要改长期配置。

## Push 后验证

每个仓库都要分别检查：

```bash
git status --short --branch --untracked-files=all
git rev-parse --short HEAD
```

理想状态：

```text
## main...origin/main
```

如果是：

```text
## main...origin/main [ahead 1]
```

说明本地 commit 已完成，但远端还没更新。

如果是：

```text
 M README.md
```

说明文件还没 commit。

如果是：

```text
?? some_file
```

要判断是不是不该提交的缓存、大文件、clone、build artifact。

## GitHub 与 Hugging Face LFS 边界

不要混淆平台规则：

- GitHub 主仓库 / GitHub 代码仓库：
  - 不用 LFS，除非项目已有明确规则。
  - 不提交大文件。
  - 不提交 ignored clone、cache、build artifact。
  - 新增图片/PDF 前可检查：

```bash
git check-attr filter -- <file>
```

期待普通文件结果：

```text
<file>: filter: unspecified
```

- Hugging Face dataset/model 仓库：
  - 可以使用 HF 官方 LFS/Xet。
  - dataset parquet、图片、model weights 可以走 HF 机制。
  - README-only 更新一般不涉及 LFS，但仍要避免误 add 大文件/cache。

## 推荐完整顺序

1. 确认目标仓库：

```bash
git remote -v
git status --short --branch --untracked-files=all
```

2. 搜索和修改目标内容。

3. 检查 diff：

```bash
git diff --check
git diff --stat
git diff
```

4. 只 stage 目标文件：

```bash
git add <files>
git diff --cached --stat
```

5. commit：

```bash
git commit -m "..."
```

6. GitHub 仓库普通 push：

```bash
git push
```

7. HF 仓库必要时用一次性 header push：

```bash
bash -ic '
auth=$(python3 -c '\''import os,base64
t=os.environ["TOKEN_ENV"]
print("Authorization: Basic "+base64.b64encode(("hf_user:"+t).encode()).decode())
'\'')
git -c credential.helper= -c "http.extraheader=$auth" push
'
```

8. push 后再次检查：

```bash
git status --short --branch --untracked-files=all
git rev-parse --short HEAD
```
