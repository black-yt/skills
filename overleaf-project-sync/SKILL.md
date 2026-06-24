---
name: overleaf-project-sync
description: "当需要从 Overleaf 网页端项目下载 ZIP、用浏览器开发者工具获取 Overleaf Cookie 和 download/zip 链接、检查本地 LaTeX/论文目录是否与远端 Overleaf 一致、或把远端 Overleaf 文件覆盖同步到本地目录时使用。"
---

# Overleaf Project Sync

## 核心原则

- 只从浏览器当前登录会话中临时复制 Overleaf Cookie；不要把 Cookie、项目 ID、下载链接或个人账号信息写入仓库。
- 用 `scripts/overleaf_sync.py` 执行检查和同步，不要把一次性脚本复制到论文项目根目录。
- 默认不写入本地目录；不传子命令时等价于 `check`。
- 只有显式执行 `update --overwrite` 时才把 Overleaf ZIP 中的文件复制到本地；`update` 不带 `--overwrite` 也只做 dry-run。
- 脚本会在系统临时目录下载和解压 ZIP，并在结束后自动清理；不要在项目根目录留下 `overleaf_tmp.zip`、`overleaf_tmp/` 等临时文件。
- 同步前先 `check`，确认差异符合预期后再 `update`。
- 同步后检查 `git status --short` 和 `git diff --check`；不要直接提交未审阅的远端覆盖结果。

## 从 Overleaf 网页获取参数

1. 在浏览器打开 Overleaf 首页并保持登录。
2. 按 `Ctrl + Shift + C`，或用浏览器菜单打开开发者工具。
3. 切到 `Network` 面板。
4. 建议勾选 `Preserve log`，避免从首页跳转到项目页时请求记录被清掉。
5. 从 Overleaf 首页点击进入目标项目页，让浏览器产生项目相关请求。
6. 在 Network 请求列表中选择一个 Overleaf 请求。优先找这些请求：
   - 下载项目 ZIP 的请求；
   - URL 中包含 `/project/[PROJECT_ID]` 的项目页请求；
   - URL 中包含 `download/zip` 的请求；
   - 其他发往 `www.overleaf.com` 且状态码正常的请求。
7. 点开请求的 `Headers`。
8. 在 `Request Headers` 中找到 `Cookie`，复制 `Cookie:` 后面的值。
9. 通常只需要其中的 `overleaf_session2=...` 这一段；如果下载返回 `401`、`403` 或登录态异常，再复制完整 Cookie 串重试。
10. 在项目页找到下载项目 ZIP 的请求或链接，形如：

```text
https://www.overleaf.com/project/[PROJECT_ID]/download/zip
```

也可以根据项目 URL 手动拼出 ZIP 下载链接：

```text
项目页:   https://www.overleaf.com/project/[PROJECT_ID]
ZIP 链接: https://www.overleaf.com/project/[PROJECT_ID]/download/zip
```

11. 把 Cookie 和 ZIP URL 作为环境变量或命令行参数传给脚本。

推荐使用环境变量，避免命令历史里直接出现长 Cookie：

```bash
export OVERLEAF_ZIP_URL='https://www.overleaf.com/project/[PROJECT_ID]/download/zip'
export OVERLEAF_COOKIE='overleaf_session2=[SESSION_VALUE]'
```

如果 Cookie 很长，也可以写到一个本地临时文件，但不要提交：

```bash
printf '%s' 'overleaf_session2=[SESSION_VALUE]' > .overleaf-cookie.local
```

## 检查本地与远端是否一致

在本地论文目录或 LaTeX 项目目录中运行：

```bash
python /path/to/overleaf-project-sync/scripts/overleaf_sync.py --target .
```

也可以显式传参：

```bash
python /path/to/overleaf-project-sync/scripts/overleaf_sync.py check \
  --url 'https://www.overleaf.com/project/[PROJECT_ID]/download/zip' \
  --cookie-file .overleaf-cookie.local \
  --target .
```

输出含义：

- `Changed files`：两边都有，但内容不同。
- `Missing locally, present in Overleaf`：Overleaf 有，本地没有。
- `Extra locally, absent from Overleaf`：本地有，Overleaf 没有。
- 完全一致时返回 `0`；发现差异时返回 `2`，方便脚本化检查。

## 从 Overleaf 更新本地目录

先 dry-run：

```bash
python /path/to/overleaf-project-sync/scripts/overleaf_sync.py update \
  --target . \
  --dry-run
```

确认将复制的文件无误后再执行：

```bash
python /path/to/overleaf-project-sync/scripts/overleaf_sync.py update \
  --overwrite \
  --target .
```

更新行为：

- 只有带 `--overwrite` 时，远端 ZIP 中未被忽略的文件才会复制到本地同名路径。
- 已存在的本地文件会被覆盖。
- 本地额外文件不会被删除。
- 不会修改 `.git/`、`.codex/`、`.claude/` 等默认忽略路径。

更新后必须检查：

```bash
git status --short
git diff --check
git diff --stat
```

## 默认忽略规则

默认忽略适合“本地 repo 中有维护脚本和 agent 文档，Overleaf 只保存论文源文件”的场景：

- 目录：`.git/`、`.codex/`、`.claude/`、`__pycache__/`、`node_modules/`、`latex_cache/`、`backups/`、`raw/`、`context/` 等。
- 文件：`*.py`、`*.pyc`、`*.md`、`.gitignore`、`.gitmodules`、`AGENTS.md`、`CLAUDE.md`、常见 LaTeX 编译产物。

如果项目确实需要同步某些默认忽略内容，用：

```bash
python /path/to/overleaf-project-sync/scripts/overleaf_sync.py check \
  --target . \
  --no-default-ignores
```

如果只需要额外忽略某些文件：

```bash
python /path/to/overleaf-project-sync/scripts/overleaf_sync.py check \
  --target . \
  --ignore 'figures/generated/**' \
  --ignore '*.bak'
```

## 常见问题

- `HTTP 401` / `HTTP 403`：Cookie 过期、复制不完整、项目权限不足，重新从浏览器 Network 面板复制 Cookie。
- `HTTP 403` 且只复制了 `overleaf_session2`：检查 session 值是否少字符；如果仍失败，复制完整 `Cookie` 请求头重试。
- `Missing URL`：没有传 `--url`，也没有设置 `OVERLEAF_ZIP_URL`。
- `Missing Cookie`：没有传 `--cookie` / `--cookie-file`，也没有设置 `OVERLEAF_COOKIE`。
- 无法连接 Overleaf、DNS 失败、连接超时或代理端口不可达：检查当前 shell 的代理变量；如果代理污染或代理不可用，临时关闭代理后重试，不要修改长期 shell 配置。
- 差异里出现大量本地脚本或缓存：增加 `--ignore`，或确认默认忽略规则没有被 `--no-default-ignores` 关闭。
- 本地文件被覆盖后不符合预期：不要继续提交，先用 Git 查看 diff，并从版本控制恢复或重新运行 `check` 分析差异。

临时关闭代理示例：

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY \
  python /path/to/overleaf-project-sync/scripts/overleaf_sync.py --target .
```

## 验证脚本本身

修改脚本后至少运行：

```bash
python -m py_compile overleaf-project-sync/scripts/overleaf_sync.py
python overleaf-project-sync/scripts/overleaf_sync.py --help
```
