# Provider、CC Switch 与多环境配置

## 先画清配置归属

| 客户端或进程 | 常见配置位置 | 注意事项 |
| --- | --- | --- |
| Windows 原生 Codex/App | `%USERPROFILE%\.codex` | App 设置和 `CODEX_HOME` 可能改变实际来源 |
| WSL 用户 CLI | `$HOME/.codex` | Windows 工具可通过 `\\wsl.localhost\[DISTRO]\home\[USER]\.codex` 访问 |
| App 启动的 WSL agent | 由日志、启动参数和进程环境确认 | 历史案例指向 Windows home 的 `/mnt/c/Users/.../.codex`，不一定等于 WSL CLI home |
| SSH 远端 Codex | 远端登录用户的实际 Codex home | 本地 CC Switch 不会自动修改远端配置 |

- 原记录为了让 CC Switch 修改 WSL CLI，在高级设置指定 WSL 的 `.codex` 目录；`/home/[USER]/.local/bin/codex` 是二进制位置，不能填成配置目录。
- 原经验依次用默认 Windows 目录切一次，再换 WSL 目录切一次，覆盖两个独立客户端。只有实际确实存在两个独立 home 且用户要求同时修改时才做，不能全量同步或互相覆盖 auth/history。
- SSH 模式中实际请求若在远端执行，须在远端核对 `config.toml` 和环境；不能因本地工具显示 provider 已切换就宣告远端生效。
- CC Switch 是外部工具，先阅读其当前帮助与备份行为；不依赖固定界面字段或把该工具当作所有环境的唯一来源。

## 可复用的配置键清单

下例是**合并片段**，不是覆盖用户整个 `config.toml` 的命令。所有占位路径、模型和 provider 按当前服务替换。

```toml
model_provider = "example"
model = "[MODEL_ID]"
model_reasoning_effort = "[SUPPORTED_EFFORT]"
service_tier = "[SUPPORTED_TIER]"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
writable_roots = ["[AUTHORIZED_ENV_ROOT]", "[PROJECT_ROOT]", "/tmp"]

[model_providers.example]
name = "Example provider"
base_url = "https://[API_HOST]/v1"
wire_api = "responses"
env_key = "PROVIDER_API_KEY"

[model_providers.alternate]
name = "Alternate provider"
base_url = "https://[ALTERNATE_API_HOST]/v1"
wire_api = "responses"
env_key = "ALTERNATE_API_KEY"

[model_providers.local_switch]
name = "Local switch"
base_url = "http://127.0.0.1:14141/v1"
wire_api = "responses"
env_key = "LOCAL_SWITCH_API_KEY"

[projects."[PROJECT_ROOT]"]
trust_level = "trusted"
```

- `env_key` 填环境变量名，实际 secret 从该进程的私有环境读取；不把 API key 填进 name 字段。
- 原资料包含多个 provider：HTTP `/v1` 网关、另一个同类网关、`http://127.0.0.1:14141/v1` 本地 switch。名称和私有地址已泛化，三种配置结构与选择关系保留。
- 原文件还使用 `experimental_bearer_token` 内联保存 key。保留该历史键的信息，但不发布实际值；优先使用当前版本支持的环境或凭据存储，不能擅自移除用户正在使用的认证方式。
- `wire_api="responses"` 要求网关兼容 Responses 协议；`/v1` 是否应有，取决于服务契约，不能机械追加到所有 provider。
- 原本地 switch 用过固定占位 key `sk-local`。只有该本地服务确实约定此值时才适用，它不是远端 API 的通用认证。
- `model_reasoning_effort` 出现过 low/medium/high/xhigh，`service_tier` 出现过 default/fast，另有 `[features] fast_mode=true`；支持范围与模型、provider、客户端版本有关，不能靠设置值保证服务端支持或加速。

## 许可、sandbox 与信任不是同一个开关

- 原记录列出 approval policy：untrusted、on-request、on-failure、never。`on-failure` 是历史选项，当前支持与弃用状态应看 CLI/schema；不能把这些值一律当作最新推荐。
- 原 sandbox 模式为 read-only、workspace-write、danger-full-access；后者扩大能力，不是代理或登录错误的修复。
- `writable_roots` 只在对应 sandbox 模式下按版本生效；不用把所有 conda、项目、共享盘一律加入白名单。
- `[projects] trust_level="trusted"` 是本地信任记录，不代表绕过系统策略或所有命令都获准。失效历史项的清理按 reference 6。
- 原配置附有 `[tui.model_availability_nux]`、`[notice] hide_rate_limit_model_nudge`：这些属于版本相关 UI 状态，不是网络根因；保留用户状态，不当通用模板批量下发。
- `[marketplaces.openai-bundled] source_type="local"` 及 `source` 指向本机 bundled-marketplace 缓存；`visualize@openai-bundled`、`sites@openai-bundled` 等插件 enabled 状态应按实际安装维护，不能复制别的机器 `/root/.codex/.tmp/...` 路径。

## shell 函数和网络配置层

原资料包含以下便利入口，保留其作用但使用通用名称：

```bash
# 只对本次 CLI 调用选 provider，保留用户传入参数。
example_codex() { codex -c model_provider=example "$@"; }
# 已安装在指定 conda 环境时才定义/使用。
alias agent_env='conda activate [ENV_NAME]'
alias resume_codex='codex resume'
start_local_switch() {
    cd '[LOCAL_SWITCH_PROJECT]' || return
    python3 switch_proxy.py
}
```

- provider 选择与用于评测/其他工作流的 provider 可以隔离，不为个人 CLI 更改全部项目。
- `proxy_r` 类函数设置 SSH 反向代理；`openai_on` 类函数切到专用 HTTP 代理；`proxy_no` 设置内网 bypass；`proxy_test` 用 curl/wget 验证；它们修改当前 shell 及子进程，不自动修改 App 已运行后端。
- 原 `.bashrc` 会 `source <(curl ...setup_proxy.sh)` 自动加载集群代理。该行为会执行远端代码，不应复制私有地址到公开 skill，也不默认在每个 shell 启动时联网执行；需要时先审查可信脚本。
- `.wgetrc` 的 `http_proxy`、`https_proxy`、`no_proxy`、`use_proxy=on` 是 wget 自己的配置层。curl 正常但 wget 异常时应单独核对；不要把旧私人 bypass 清单写成通用值。
- 原 `proxy_off` 是一组 unset，还遗漏了某些大小写变体。更可靠的恢复是快照后逐项恢复，防止中断已配置的中转 API。
- Linux 发行版 `.bashrc` 常有非交互提前 return；App 和 SSH 的非交互启动未必读取后面的 nvm、conda 或代理配置。重复 source nvm 与 conda 改 PATH 也可能改变实际 `node/npm/codex` 来源。
- 记录代理、provider 和配置来源时只输出必要键，不 `env | grep` 打印所有可能包含凭据的值。

## 比较与恢复配置

原备份目录用 `cmp`/`diff -u` 对比 `.bashrc`、`config.toml` 后 `cp` 恢复。复用时先保存目标现状，逐段合并并保留权限、注释和无关配置；不能把整份个人 dotfile 覆盖到新机器。

原 AI 环境搭建还包括 WSL 安装/选择默认发行版、Ubuntu 的 git/curl/build-essential、nvm Node 22、npm 升级、可选 Miniconda。这些是选择 WSL 开发链时的依赖，不是原生 Windows Codex 的硬性前提。Miniconda、nvm 与系统 npm 可以并存，先确定实际 PATH 再安装，不为排障重装全部环境。

原记录还配置 Git 身份并使用 `credential.helper store`。这是独立的 Git 认证配置，store 会将凭据落盘；更适合使用既有系统凭据管理器或 gh 认证，不为 agent 排障更改全局身份或把 token 写入命令历史。

## 原环境初始化命令的独立模板

为完整保留原安装链，下面列出其可复用命令。仅在用户选择**新建 WSL 开发环境**时使用，不在现有环境排障时整段执行；Node 22 是原记录的版本样本，先核对当前 CLI 的运行要求。

Windows PowerShell：

```powershell
wsl --install
wsl -l -v
# 只有目标发行版已存在且用户要切换默认环境时执行。
wsl --set-default Ubuntu
wsl -d Ubuntu
```

进入目标 Ubuntu 后：

```bash
sudo apt update
sudo apt install -y git curl build-essential
# 先从 nvm 官方 README 选择安装脚本版本，下载并审查后再执行。
# 原记录使用 master/install.sh 管道安装；不把会变化的脚本自动执行。
curl -fSL 'https://raw.githubusercontent.com/nvm-sh/nvm/[REVIEWED_TAG]/install.sh' \
  -o /tmp/nvm-install-reviewed.sh
bash /tmp/nvm-install-reviewed.sh
source "$HOME/.bashrc"
nvm --version
nvm install 22
nvm use 22
node --version
npm --version
npm install -g @openai/codex
```

- 原记录随后运行 `npm install -g npm@latest`、`npm -v`。保留该升级命令，但先确认最新 npm 支持当前 Node，且修改的是选定环境；无需为登录故障主动升级 npm。
- 可选 Miniconda 原流程为下载 `Miniconda3-latest-Linux-x86_64.sh`、运行 `bash Miniconda3-latest-Linux-x86_64.sh`、确认协议/初始化，再 `source "$HOME/.bashrc"`。从当前官方安装入口选择匹配架构并核验校验和；原文的两个 `yes` 是交互回答，不是要单独运行无限输出的 `yes` 命令。
- 不把原来的 `cat > ~/.codex/config.toml` 当作合并操作：它会截断原配置。已有文件逐段合并上面的 TOML，新文件才可在备份与路径确认后创建。
- 原比较方式可用 `cmp -- '[PRIVATE_SOURCE]' '[PRIVATE_TARGET]'`；需要详细差异时在可信本地终端用 `diff -u -- '[PRIVATE_SOURCE]' '[PRIVATE_TARGET]'`，输出可能含 key，不能原样发到公共日志。复制前先备份目标，优先只合并已核实的字段。
- 原通用 SDK 变量名为 `LLM_API_KEY`、`LLM_BASE_URL`，文档解析使用 `MINERU_TOKEN`；它们与 `ANTHROPIC_AUTH_TOKEN`、Codex provider 的 `env_key` 是不同输入，不能相互替换。只保留键名与职责，不内置凭据。
- nvm 官方 README fallback：2026-10-03 实际 GET 200 的完整入口为 [nvm README](https://raw.githubusercontent.com/nvm-sh/nvm/master/README.md)。它随主分支滚动，安装时仍需选定并审查版本。
