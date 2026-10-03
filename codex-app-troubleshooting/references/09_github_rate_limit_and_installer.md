# 安装器访问 GitHub 匿名 API 限流

## 证据先行

- 原记录已经确认 `x-ratelimit-remaining: 0`，失败的是 GitHub 匿名 API 查询，不是所有 GitHub 下载都不可用。
- 将认证限制在 `https://api.github.com/` 的必要请求；不要把 GitHub token 发给任意下载域名或永久塞进 URL。
- 先查看安装器是否直接支持 `GITHUB_TOKEN`、`GH_TOKEN`、CLI 已有认证或指定 release 版本；支持时优先用官方入口，不修改安装器源码。
- 只需查 API 时可以用已有认证的 `gh api repos/openai/codex/releases/latest --jq .tag_name`，避免打印整份账户或 token。

## 原 WSL 临时 curl wrapper 的完整机制

原流程创建 `/tmp/codex-curl-wrapper/curl`，遍历参数，遇到 `https://api.github.com/*` 时调用真实 curl 并追加：

```text
Authorization: Bearer <gh auth token 的输出>
Accept: application/vnd.github+json
```

其他 URL 仍走普通 curl。安装器通过仅对单条命令有效的 PATH 前缀找到 wrapper：

```bash
PATH="[WRAPPER_DIR]:$PATH" CODEX_NON_INTERACTIVE=1 sh '[REVIEWED_INSTALL_SCRIPT]'
```

- 不编辑原 `install.sh`，不永久修改 PATH，不在 shell rc 中保存 token。
- 原版 `-H "Authorization: Bearer $(gh auth token)"` 会让 token 短暂出现在 curl argv；重用时应改成 stdin 配置等不出现在 argv 的传递方式。
- 不能用“任意参数包含 api.github.com 就给整次 curl 授权”的简单规则允许同次请求多个不可信 URL。须核对安装器调用形态、禁止 `--next`/跨主机共享 header 等情况。
- 下载域跳转也要审查；不使用 `--location-trusted`，不能假定所有包装器和 curl 版本的重定向行为相同。

本 skill 提供 [scripts/github_api_curl.py](../scripts/github_api_curl.py) 的保守实现：只支持单个 URL；非 API 请求原样交给真实 curl；API 请求只接受 HTTPS 和有限下载参数，禁止额外 config/header、verbose/trace 与多请求选项，以 stdin 传入短期取得的 token。允许安装器常用的 `-L`，但以 `--max-redirs 0` 保证遇到 redirect 即失败、不带认证跳转。与安装器参数不兼容时明确失败，转用官方 token 支持，不继续放宽白名单。

示例在 WSL bash 执行；脚本路径应替换为该 skill 实际位置：

```bash
set -eu
wrapper_dir=$(mktemp -d /tmp/codex-curl-wrapper.XXXXXX)
trap 'rm -f "$wrapper_dir/curl"; rmdir "$wrapper_dir"' EXIT
real_curl=$(command -v curl)
cp '[SKILL_DIR]/scripts/github_api_curl.py' "$wrapper_dir/curl"
chmod 700 "$wrapper_dir/curl"
CODEX_REAL_CURL="$real_curl" \
PATH="$wrapper_dir:$PATH" CODEX_NON_INTERACTIVE=1 \
sh '[REVIEWED_INSTALL_SCRIPT]'
hash -r
command -v codex
codex --version
```

- 使用唯一目录，退出时只清理本次文件；原固定 `/tmp` 路径可能与另一安装进程冲突。
- `CODEX_NON_INTERACTIVE=1` 只是历史安装器支持的开关，当前脚本必须先核对。
- 不在输出中打印 `gh auth token`；先通过不显示 token 的 `gh auth status` 等方式确认已有授权。
- 下载完成、二进制版本正确仍不代表 App 指向该二进制；按 reference 4 验收。

## PowerShell 路径

原记录用当前进程的 `GITHUB_TOKEN`，向 GitHub API 发带 Bearer/Accept/API-Version 的 GET，再运行本地安装脚本。下面保留请求结构，token 从现有环境读取：

```powershell
if (-not $env:GITHUB_TOKEN) { throw 'No GitHub token in this process environment' }
$release = Invoke-RestMethod -Headers @{
    Authorization = "Bearer $env:GITHUB_TOKEN"
    Accept = 'application/vnd.github+json'
    'X-GitHub-Api-Version' = '2022-11-28'
} -Uri 'https://api.github.com/repos/openai/codex/releases/latest'
$release.tag_name
$env:CODEX_NON_INTERACTIVE = '1'
powershell -ExecutionPolicy Bypass -File '[REVIEWED_INSTALL_PS1]'
```

- 不把真实 token 写入命令历史或文档；如果只是这次操作临时注入，完成后恢复进入前的环境。
- 上面的 API 查询成功不保证安装器读取 `GITHUB_TOKEN`；必须审查当前安装器实现或帮助。
- `Bypass` 仅是原单次 PowerShell 执行方式，不自动修改 CurrentUser/LocalMachine 策略。已有组织策略或正在运行的应用不应被绕过、退出或重置。
- GitHub API 版本 header 是案例值；按当前 GitHub API 支持范围核对。
