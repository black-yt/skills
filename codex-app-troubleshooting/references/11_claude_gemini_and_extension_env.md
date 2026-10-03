# Claude Code、Gemini CLI 与 IDE 环境差异

本篇属于用户要求一并收录的其他 agent 问题；不把 Claude/Gemini 配置写入 Codex，也不为了其中一个客户端修改其他客户端的认证。

## Claude Code 安装与 provider 配置

- 原安装入口是 `https://claude.ai/install.sh`，历史命令为 `curl -fsSL https://claude.ai/install.sh | bash`。先核对 [Claude Code 官方概览](https://code.claude.com/docs/en/overview)、当前平台安装方式，并下载审查脚本后执行。
- 原 shell 配置通过 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN` 使用兼容网关；这些不是 Codex `model_providers` 字段。
- 原网关注释要求特定服务的 default 分组；这是网关账号权限约定，不是 Anthropic 通用规则。使用当前服务文档核对，不公开内部服务名或地址。
- 原例区分 HTTP 地区节点、全球转发节点和 HTTPS 加密入口，并在多图上传时优先 HTTPS；保留“按服务能力与上传需求测试”的判断，不对某地区地址作普遍性能承诺。

```bash
export ANTHROPIC_BASE_URL='https://[ANTHROPIC_COMPATIBLE_GATEWAY]'
# 通过用户已有的私有密钥机制注入 ANTHROPIC_AUTH_TOKEN，勿将值写入仓库。
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1
```

- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` 是原记录为第三方网关兼容实验/beta headers 使用的开关；按当前客户端版本和网关错误决定，不无条件禁用功能。
- 原记录列出可选模型变量：`ANTHROPIC_MODEL`、`ANTHROPIC_DEFAULT_OPUS_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL`、`ANTHROPIC_DEFAULT_HAIKU_MODEL`、`CLAUDE_CODE_SUBAGENT_MODEL`。只有用户需要模型映射且目标 provider 支持时设置；不要把全部模型静默映射成同一个历史型号。

## Windows 用户环境不等于当前进程环境

原流程通过 Win+R → `sysdm.cpl` → 环境变量写入用户值；已经打开的 PowerShell/IDE 仍可能保持旧环境。

```powershell
[Environment]::SetEnvironmentVariable('CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS', '1', 'User')
$env:CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS =
    [Environment]::GetEnvironmentVariable('CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS', 'User')
```

只需单次运行时，不必写 User 范围。原记录在 PowerShell `$PROFILE` 定义 `cla`，设置该变量后 `claude $args`；保留参数透传机制，避免每次调用都重写注册表：

```powershell
function cla {
    $previous = $env:CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS
    try {
        $env:CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS = '1'
        claude @args
    } finally {
        $env:CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS = $previous
    }
}
```

- 只有用户需要长期快捷入口时才编辑 `$PROFILE`；先备份现有内容，不用 `New-Item -Force` 覆盖已存在文件。
- 文件不存在时先创建父目录和文件，再 `notepad $PROFILE`；加载 `. $PROFILE` 会执行其全部内容，编辑前审查。
- User 变量影响之后使用它的所有该用户进程，进程级变量只影响本 shell 和子进程；不要把修复 Claude 的设置带到 Codex 认证链。

## VS Code 插件单独的环境入口

终端能登录而 Claude Code 插件失败时，先确认扩展运行在 Windows、本地 WSL 还是 SSH 远端 extension host，再检查对应 Profile/用户设置。

```json
{
  "claudeCode.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL", "value": "https://[GATEWAY_HOST]" },
    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "[API_KEY]" },
    { "name": "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS", "value": "1" }
  ]
}
```

- 这是原记录中的扩展设置结构，先核对当前扩展实际注册的键及支持方式。
- 若只能把 token 放在用户 settings.json，它会以明文保存，应限制访问；不写进项目共享设置或公开仓库。
- `settings.json` 是 JSONC 时保留注释和其他配置，只改目标数组项；不要复制整份备份覆盖。
- 新进程/扩展宿主继承才生效，重启范围需核对活动终端与对话。

## WebFetch preflight

原记录在 WebFetch 无法抓取时尝试用户设置：

```json
{
  "skipWebFetchPreflight": true
}
```

- 此键旨在跳过预检查，不是修复代理、DNS 或 TLS 的万能开关，也不保证当前版本仍支持。
- 先检查实际 WebFetch 错误、支持的配置 schema、网关能力和组织策略；只有用户允许相应行为且预检查确为故障点才尝试。
- 保留原值并单独验证抓取；不能用它取消其他授权/安全策略，不同时关闭其他检查。

## Gemini CLI

原安装与使用入口：

```bash
npm install -g @google/gemini-cli
npm root -g
command -v node
command -v npm
command -v gemini
gemini --version
```

- 全局 npm 安装是相对于当前 npm prefix；若属于 conda/nvm，退出环境后可能找不到命令。先分清系统、conda、nvm 的 Node/npm，再决定是否更新 npm。
- 原记录使用 Google 账号登录；具体账号资格、API key/企业模式和地区网络条件按当前 [Gemini CLI 官方仓库](https://github.com/google-gemini/gemini-cli)核对。
- 原作者记录过“响应慢、效果不理想”的实际体验，保留为该环境下的主观观察；不能写成所有版本的能力结论。复现时记录模型、版本、网络、请求大小和延迟，再比较。
- 不因性能慢自动切换 provider、账号或调用付费模型；先完成可观察的网络和版本检查。

## 环境搭建与其他 token 的边界

- 原 AI 备份还含通用 LLM SDK、文档解析、Hugging Face、GitHub、隧道工具 token；它们是其他工具的私有环境，与上述 agent 登录不能混用。
- 保留“每个客户端读取自己的 key/base URL、不同 shell 初始化可能不一致”的经验，不复制实际值、私人模型节点、用户名或项目路径。
- 原来的终端美化、GPU/CPU 调度函数不是本篇的 agent 故障机制，不为了安装 CLI 覆盖用户 `.bashrc`。
- Claude 网络官方入口：[network configuration](https://code.claude.com/docs/en/network-config)、[settings](https://code.claude.com/docs/en/settings)。滚动文档与历史实验键不同步时，按当前版本验证，旧键保留为历史线索。
- 本次核验边界（2026-10-03）：上述 Claude 文档站从维护环境 GET 返回 403，未据此声称历史实验键仍受支持；实际 GET 200 的完整官方 fallback 为 [Claude Code README](https://raw.githubusercontent.com/anthropics/claude-code/main/README.md) 和 [Gemini CLI README](https://raw.githubusercontent.com/google-gemini/gemini-cli/main/README.md)。先运行 `claude --version`、`gemini --version`，再按当前文档/帮助确认支持范围。
