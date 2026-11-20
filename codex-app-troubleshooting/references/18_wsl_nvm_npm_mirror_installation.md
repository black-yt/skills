# WSL2 + nvm + npm 的镜像安装与更新

用户反馈在 WSL2 + nvm + npm 中反复安装失败，使用临时移除 HTTP/HTTPS 代理变量、国内 npm 镜像和可选依赖参数后安装成功。对已确认采用此环境、允许使用该镜像的用户，后续首次安装和更新优先沿用下面的命令。此经验不改变 Windows npm、standalone 或 App 管理入口的安装渠道，也不证明所有下载失败都由代理引起。

## 安装前确认与日常命令

- **执行位置**：在目标 WSL2 发行版的 Bash 中加载现有 nvm 环境；确认 `node`、`npm` 来自同一 Linux Node 安装。nvm 按 Node 版本隔离全局包，切换版本后需重新检查路径。
- **只读检查**：运行 `command -v node npm`、`node --version`、`npm --version`、`npm root -g`；已有 Codex 时记录 `type -a codex`、`codex --version`。若路径指向 Windows npm shim，先修正执行环境；`EACCES` 转到 [04](04_managed_cli_and_installation.md)，不要默认使用 sudo 或给 nvm 另设 prefix。
- **进程边界**：安装或清理前，保存工作并正常退出使用目标安装的 Codex，以及操作同一全局目录的 npm 安装进程；不要并发安装。若有受保护活动任务，先做独立检查，待任务结束再改包，不批量杀 Codex/node 或关闭整个 WSL。

首次安装和以后更新使用同一条命令：

```bash
env -u HTTP_PROXY -u HTTPS_PROXY \
    -u http_proxy -u https_proxy \
    npm install -g @openai/codex@latest \
    --registry=https://registry.npmmirror.com \
    --include=optional
```

- **`env -u ...`**：只为本次 npm 进程及其子进程移除列出的四个环境变量，不修改 shell 启动文件。它不清除 `.npmrc` 的代理、`npm_config_proxy` / `npm_config_https_proxy` 或其他代理层；仍有代理错误时按日志核对实际来源，不宣称已经完全直连。
- **`--registry`**：只对此命令选择用户接受的第三方镜像，不执行全局 `npm config set registry`。网络仍需代理的环境按实际连通性处理，不把这次成功的绕过方式扩展成永久关闭代理。
- **`--include=optional`**：要求包含与当前平台匹配的可选依赖；WSL Linux x64 的启动器查找 `@openai/codex-linux-x64`，arm64 对应自己的平台包。该参数不能保证下载成功，npm 返回成功也不能代替启动验证。
- **`@latest`**：安装所选 registry 的 `latest` tag，镜像可能稍晚同步；需要刚发布的版本时先核对同步状态，而不是反复重装。

安装退出码成功后，在当前 shell 验证：

```bash
hash -r
command -v codex
codex --version
```

可保存的一行命令：

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy npm install -g @openai/codex@latest --registry=https://registry.npmmirror.com --include=optional
```

## ENOTEMPTY 或可选依赖缺失时彻底重装

先用日常命令重试一次；仍报 `ENOTEMPTY` 或 `Missing optional dependency` 时，确认上面的目标目录、进程状态和用户已有的卸载/清理授权。清理只覆盖当前 `npm root -g` 下的 `@openai/codex` 和同级 `.codex-*` 临时目录，保留其他 `@openai` 包、`~/.codex`、认证、provider、数据库和会话。

```bash
# 子 shell 遇到失败即停止，避免 npm root 查询失败后拼出错误删除路径。
(
    set -e
    CODEX_NPM_ROOT="$(npm root -g)"
    case "$CODEX_NPM_ROOT" in
        /*/node_modules) ;;
        *) printf '%s\n' '无法确认 npm 全局目录，停止清理。' >&2; exit 1 ;;
    esac
    CODEX_PARENT="$CODEX_NPM_ROOT/@openai"

    # 卸载失败可能正是安装残留；已核实目录后继续定向清理。
    npm uninstall -g @openai/codex || true
    rm -rf -- "$CODEX_PARENT/codex"
    if [ -d "$CODEX_PARENT" ]; then
        find "$CODEX_PARENT" -maxdepth 1 \
            -name '.codex-*' -type d -exec rm -rf -- {} +
    fi

    env -u HTTP_PROXY -u HTTPS_PROXY \
        -u http_proxy -u https_proxy \
        npm install -g @openai/codex@latest \
        --registry=https://registry.npmmirror.com \
        --include=optional \
        --fetch-retries=2 \
        --fetch-timeout=120000
)
```

- **验收**：仅在重装成功后，在当前 shell 执行上面的 `hash -r`、`command -v codex` 和 `codex --version`；命令失败时先保留日志，不继续把旧入口当成新安装验收。
- **有限重试**：网络请求最多重试 2 次，单次请求超时为 120000 毫秒；不是整个安装的总时限。失败后记录具体错误并转到下载诊断，不循环执行卸载或清理。
- **恢复**：重装失败时保留错误日志，恢复同一 npm 渠道的可用版本；原版本已记录且仍可获取时，用该确切版本替换 `@latest`。包目录清理本身不可回滚，不能用删除用户配置代替恢复安装。

## 下载仍卡住：详细日志与全新缓存

先确认上一次 npm 已退出，再执行一次带新缓存的诊断安装：

```bash
env -u HTTP_PROXY -u HTTPS_PROXY \
    -u http_proxy -u https_proxy \
    npm install -g @openai/codex@latest \
    --registry=https://registry.npmmirror.com \
    --include=optional \
    --cache="$(mktemp -d)" \
    --fetch-retries=0 \
    --fetch-timeout=60000 \
    --loglevel=verbose
```

- **判读**：禁用请求重试、把单次请求超时设为 60000 毫秒，观察最后请求的 registry、元数据或 tarball，以及错误类别；npm 的旋转动画不能单独证明死锁。
- **缓存与日志**：新缓存隔离旧缓存影响，不清空原缓存；临时目录会保留，记下路径，排障完成后只清理本次目录。分享日志前移除凭据、账号、私人路径、内部主机和带认证的 URL，仅保留必要的错误及公共下载主机。
- **停止条件**：一次诊断仍失败就按日志检查镜像同步、代理配置、DNS 或 TLS，不盲目重试，不关闭 TLS 校验。成功后重复上面的 PATH 与版本验收。

## 常见报错速查与镜像同步

| 报错或现象 | 下一步 |
| --- | --- |
| `Missing optional dependency` | 使用 `--include=optional` 重装并实际运行 `codex --version`；检查对应平台包的下载日志，必要时执行定向清理重装 |
| `ENOTEMPTY` | 确认无并发安装，卸载后只清当前 npm 目录的 Codex 包与 `.codex-*` 残留 |
| `SSL_ERROR_SYSCALL` | 检查失败请求和代理链，在本场景临时绕过代理并切镜像验证；不凭错误名认定单一根因 |
| npm 一直显示 `⠸` | 用全新缓存和 `--loglevel=verbose` 检查具体下载阶段及请求超时 |
| `ETIMEDOUT` / `ECONNRESET` | 检查镜像连通性、同步状态和代理；按证据选择可达的 registry |
| `codex: command not found` | 检查 nvm 当前 Node 版本、`npm root -g`、全局 bin 与 PATH，执行 `hash -r`；App 入口另按 [04](04_managed_cli_and_installation.md) 验收 |

需要刚发布的版本时，分别查询镜像和官方源的 tag，并检查目标主包的 `optionalDependencies` 中对应平台包是否可获取：

```bash
npm view @openai/codex dist-tags.latest --registry=https://registry.npmmirror.com
npm view @openai/codex dist-tags.latest --registry=https://registry.npmjs.org
```

这两次查询按各自网络需要使用临时代理设置。若镜像尚未同步目标版本或平台包，可等待同步，或使用可达的官方源安装；需要同版本平台压缩包校验与离线恢复时见 [16](16_legacy_wsl_remote_connection.md)。终端 CLI 安装成功不证明 App 或正在运行的远程后台已升级，版本不一致转到 [17](17_stale_models_and_app_server_versions.md)。

## 官方依据与版本边界

- **2026-11-20 核对**：GitHub API 返回最新 CLI release `rust-v0.171.0`，HEAD 为 `bb5b9c6240136de8ff4d30215e2341c44559aa04`；本地 `codex --version` 为 `0.171.0`。复查官方 README、配置指引、当前 CLI help 和 npm 启动器；这些核对不代表本次重新执行了用户的全局安装。
- **Codex**：[官方 README](https://github.com/openai/codex/blob/rust-v0.171.0/README.md)确认 npm 安装渠道；[本次核对的启动器源码](https://github.com/openai/codex/blob/bb5b9c6240136de8ff4d30215e2341c44559aa04/codex-cli/bin/codex.js)确认平台映射和缺失依赖报错。已发布包的确切平台版本以其 `optionalDependencies` 和当前启动器为准，不把源码里的开发版本当作 npm 发布版本。
- **npm**：先运行 `npm --version`，再查匹配主版本的文档；本次 GET 验证可访问的完整入口为 [npm 11 install](https://docs.npmjs.com/cli/v11/commands/npm-install/) 和 [npm 11 config](https://docs.npmjs.com/cli/v11/using-npm/config/)，用于核对 `include`、代理、registry、缓存、重试和超时参数。镜像与绕过代理是用户实测方案，不是 OpenAI 对第三方镜像的推荐。
