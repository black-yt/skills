# Codex CLI 的 npm 安装慢、卡住与下载失败

适用于通过 npm 全局安装或更新 `@openai/codex` 的 Windows、macOS、Linux 和 WSL 环境。先区分 registry 元数据、平台包下载和本地安装三个阶段，再按日志选择镜像、代理或残留清理方案。桌面 App 配套运行环境下载慢时读 [15](15_windows_updates_and_runtime_downloads.md)，standalone 安装按 [04](04_managed_cli_and_installation.md) 核对原渠道。

## 先定位卡在哪一步

- 用 `node --version`、`npm --version`、`node -p "process.platform + ' ' + process.arch"` 和 `npm root -g` 确认当前终端的 Node 平台及全局目录。使用 nvm 时确认当前 Node 版本和 npm 属于同一环境。检查 `npm config get registry` 与 `npm config get "@openai:registry"`。如果设置了 `@openai` 专用 registry，它可优先于通用 `--registry`，以请求日志中的实际主机为准。
- 对比官方源和可用的可信镜像。以下命令只查询元数据，适合在安装前检查响应速度和 `latest` 是否同步。请求超时以毫秒为单位。

```sh
npm view @openai/codex dist-tags.latest --registry=https://registry.npmjs.org --prefer-online --fetch-retries=0 --fetch-timeout=60000
npm view @openai/codex dist-tags.latest --registry=https://registry.npmmirror.com --prefer-online --fetch-retries=0 --fetch-timeout=60000
```

- 元数据查得快时，仍需从安装日志定位平台包 tarball 的实际下载主机和错误。用 `npm view @openai/codex@latest optionalDependencies --json` 加上选定 registry 查询平台包映射。需要刚发布的版本时，先对照两个源的 tag，并确认镜像也已同步对应平台包。
- 安装一直转圈或请求阶段不明时，等上一次 npm 退出，再对当前要验证的 registry 执行一次详细日志安装。以下用官方源示范，比较镜像时替换 `--registry` 的地址。看最后请求的是元数据还是 tarball，或已进入解包和写目录阶段。零重试和 60 秒超时用于单次请求诊断。

```sh
npm install -g @openai/codex@latest --registry=https://registry.npmjs.org --include=optional --fetch-retries=0 --fetch-timeout=60000 --loglevel=verbose
```

如果要排除缓存因素，再用 `--cache` 指向本次创建的空目录。保存实际路径以便事后清理，保留日常 npm 缓存。分享日志前移除凭据、账号、私人路径、内部主机及带认证的 URL。

## 按证据加快下载

- 官方源慢而镜像响应正常时，可用可信镜像完成首次安装或更新。下面以 npm mirror 为例，命令可用于 Windows PowerShell、macOS、Linux 和 WSL。命令行参数只针对本次调用。
- 遇到 TLS 错误、连接重置或超时时，核对目标主机、代理环境变量和 npm 配置的 `proxy` / `https-proxy`。需要代理的网络应使用可用的代理。确认可直连后，可仅对本次命令临时绕过有问题的代理，保留 TLS 校验。
- `--include=optional` 让 npm 安装匹配平台的可选依赖。npm 可能在平台包下载失败后仍报告安装成功，因此需要执行 `codex --version` 验收。命令找不到时检查当前 npm 全局 bin 和 PATH，Bash 中先运行 `hash -r`。若打开的是旧版本，用 `type -a codex` 或 PowerShell 的 `Get-Command codex -All` 查找实际入口。

```sh
npm install -g @openai/codex@latest --registry=https://registry.npmmirror.com --include=optional
codex --version
```

镜像尚未同步时可以等待，或从可达的官方源安装。WSL 中需要校验同版本平台包并离线恢复时见 [16](16_legacy_wsl_remote_connection.md)。若终端 CLI 已更新但实际 App 后台版本仍旧，见 [17](17_stale_models_and_app_server_versions.md)。

## 常见报错与重装条件

| 现象 | 下一步 |
| --- | --- |
| npm 一直显示 `⠸` | 用 `--loglevel=verbose` 和有限请求超时定位阶段，怀疑缓存时用临时空目录验证 |
| `ETIMEDOUT` / `ECONNRESET` | 对照实际请求主机、代理、镜像响应和同步状态 |
| `SSL_ERROR_SYSCALL` | 核对失败请求和 TLS 握手路径，只在直连可用时临时绕过故障代理 |
| `Missing optional dependency` | 检查平台包是否下载成功，用 `--include=optional` 和可达 registry 重装，再运行 `codex --version` |
| `ENOTEMPTY` | 先结束同一全局目录的并发安装，核对报错指向的残留路径后再清理 |
| `codex: command not found` | 检查当前 Node 环境、npm 全局目录及 PATH，再按原安装渠道处理 |

只有确认是本地安装残留，且普通重试仍失败时，才卸载并清理对应包。先记录旧版本、确认 `npm root -g` 和报错路径，并正常退出使用该安装的 Codex 及操作同一目录的 npm。运行 `npm uninstall -g @openai/codex` 后，只清理该全局目录下实际存在的 `@openai/codex` 和已确认的同级 `.codex-*` 残留，保留其他包和 Codex 用户数据。用可达的 registry 重装并验证版本。重装失败时保留日志，原版本仍可获取时可用确切版本恢复。权限错误见 [04](04_managed_cli_and_installation.md)。

## 实测案例：WSL2 + nvm

用户在 WSL2 的 nvm 环境中多次安装失败，使用国内镜像并对本次 npm 移除四个 HTTP/HTTPS 代理变量后安装成功。在同一环境和网络条件下，可将这条命令用于首次安装及后续更新。

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy npm install -g @openai/codex@latest --registry=https://registry.npmmirror.com --include=optional
```

`env -u` 只移除列出的变量。通过 `.npmrc` 或 `npm_config_proxy` / `npm_config_https_proxy` 等配置的代理仍需按日志检查。若这个 WSL 环境需要按上一节清理重装，可用下面的命令限制清理位置和下载重试次数。

```bash
(
    set -e
    CODEX_NPM_ROOT="$(npm root -g)"
    case "$CODEX_NPM_ROOT" in
        /*/node_modules) ;;
        *) printf '%s\n' '无法确认 npm 全局目录，停止清理。' >&2; exit 1 ;;
    esac
    CODEX_PARENT="$CODEX_NPM_ROOT/@openai"
    npm uninstall -g @openai/codex || true
    rm -rf -- "$CODEX_PARENT/codex"
    if [ -d "$CODEX_PARENT" ]; then
        find "$CODEX_PARENT" -maxdepth 1 \
            -name '.codex-*' -type d -exec rm -rf -- {} +
    fi
    env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy \
        npm install -g @openai/codex@latest \
        --registry=https://registry.npmmirror.com --include=optional \
        --fetch-retries=2 --fetch-timeout=120000
)
```

重装成功后在原终端运行 `hash -r`、`command -v codex` 和 `codex --version`。如果仍卡住，可用空缓存测试同一下载路径。

```bash
CODEX_NPM_DIAG_CACHE="$(mktemp -d)" &&
    env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy \
        npm install -g @openai/codex@latest \
        --registry=https://registry.npmmirror.com --include=optional \
        --cache="$CODEX_NPM_DIAG_CACHE" \
        --fetch-retries=0 --fetch-timeout=60000 --loglevel=verbose
```

## 官方依据与版本边界

- 2026-11-20 核对 CLI release `rust-v0.171.0` 及 HEAD `bb5b9c6240136de8ff4d30215e2341c44559aa04`。用 `codex --version` 确认本地版本，再查对应 release 的安装说明和启动器。已发布的主包所声明的 `optionalDependencies` 决定平台包版本。[Codex README](https://github.com/openai/codex/blob/rust-v0.171.0/README.md)、[npm 启动器](https://github.com/openai/codex/blob/bb5b9c6240136de8ff4d30215e2341c44559aa04/codex-cli/bin/codex.js)
- 用 `npm --version` 选择匹配主版本的文档。2026-11-20 核对的 npm 11 入口包括 [install](https://docs.npmjs.com/cli/v11/commands/npm-install/)、[view](https://docs.npmjs.com/cli/v11/commands/npm-view/)、[config](https://docs.npmjs.com/cli/v11/using-npm/config/) 和 [scope](https://docs.npmjs.com/cli/v11/using-npm/scope/)。
