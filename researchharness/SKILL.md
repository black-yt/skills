---
name: researchharness
description: Use when installing, configuring, running, embedding, deploying, or debugging InternScience ResearchHarness as a lightweight tool-using LLM agent runtime, including CLI runs, local frontend UI, OpenAI-compatible API server, Python API, tool selection, workspaces, traces, compaction, tests, and read-only source inspection.
---

# ResearchHarness

## 总览

- ResearchHarness 是轻量、可审计的 tool-using LLM agent runtime，支持 CLI、本地前端、Python API 和 OpenAI-compatible API server。
- 主文件保留使用边界和 reference 导航；涉及安装、环境变量、API 协议、tools、workspace、trace 或测试时，按下面导航读取对应 reference。
- 任何源码阅读都只用于确认行为和参数，不能修改第三方源码、`site-packages`、editable checkout 或共享环境。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 概括 ResearchHarness 的定位和边界，说明 CLI、本地 UI、Python API、OpenAI-compatible server 四种模式、必须先配置工具 key、workspace/trace 安全和禁止修改源码/共享环境。 | ResearchHarness、agent runtime、CLI、local UI、Python API、OpenAI-compatible API、tool keys、workspace、trace、source read-only、shared env、safety boundary | 触发本 skill 后默认读取；判断是否适合用 ResearchHarness 前；开始安装/运行/部署/调试前；涉及工具 key、workspace、trace 或源码阅读边界时读取 | `SKILL.md` |
| 2 | 说明如何通过 PyPI 或 GitHub 获取 ResearchHarness、如何确认版本和仓库结构、如何用 `module.__file__`/`inspect` 只读定位包内源码和关键模块。 | PyPI、pip install、GitHub repo、source tree、`module.__file__`、`__version__`、`inspect.getsource`、package path、read-only source、do not patch | 安装或升级前；需要确认当前版本行为前；需要从源码追溯工具 schema、参数默认值或模块路径前；遇到文档和实际行为不一致时必须读取 | [references/setup-and-source.md](references/setup-and-source.md) |
| 3 | 记录 CLI、本地浏览器前端和 Python API 的运行方法，列出 `.env`、模型、工具 key、生命周期、上下文压缩、LLM wrapper 和常用环境变量配置。 | CLI、local frontend、Python API、`.env`、env.example、tool API keys、model config、lifecycle、compaction、LLM wrapper、workspace root、interactive run | 运行 CLI 前；启动本地 UI 前；写 Python 调用前；配置 `.env`/工具 key/模型参数前；排查生命周期、上下文压缩、workspace root 或交互运行问题时必须读取 | [references/runtime-cli-python.md](references/runtime-cli-python.md) |
| 4 | 说明如何启动和调用 OpenAI-compatible API server，覆盖 `/v1/chat/completions`、请求/响应结构、`extra_body` object 约束、非 object 拒绝、multimodal 内容和协议兼容边界。 | API server、OpenAI-compatible、chat completions、`/v1/chat/completions`、`extra_body`、object only、request schema、multimodal、streaming、OpenAI SDK、protocol boundary | 部署 API server 前；用 OpenAI SDK 调 ResearchHarness 前；新增 provider 参数或 `extra_body` 前；排查 400/422、非 object 值被拒绝、协议兼容或多模态请求问题时必须读取 | [references/api-server-and-protocol.md](references/api-server-and-protocol.md) |
| 5 | 记录工具可用性测试和 workspace 约束，覆盖 env.example 必要工具 key、联网工具代理排错、trace/compaction 产物、benchmark adapter、路径边界和测试验证顺序。 | tools、tool tests、env.example、workspace path、path safety、trace、compaction、benchmark adapter、network tools、proxy off、validation、test tool availability | 配置或测试 tools 前；接 benchmark adapter 前；处理 workspace/trace/compaction 前；联网工具失败或代理污染时；验证工具 key 是否可用、路径是否越界或 trace 是否应暴露时必须读取 | [references/tools-workspace-testing.md](references/tools-workspace-testing.md) |

## 使用边界

- ResearchHarness 是轻量、可审计的 tool-using LLM agent harness。
- 适合本地 agent 工作、benchmark 公平执行底座、OpenAI-compatible agent API 后端、代码/文件/PDF/图片/网页任务。
- 它是 base harness，不是大型 workflow platform、多租户服务或完整产品平台。
- 不要擅自安装依赖、升级共享环境、修改长期配置或暴露公网服务；需要时先征得用户同意。
- API server 默认没有用户认证；公开暴露前必须加外层认证、访问控制或只绑定可信内网。
- trace/session state 不要放进 agent 可见 workspace，避免 agent 读取自己的执行记录。
- 推荐通过源码阅读确认复杂行为、参数默认值、工具 schema 和 API contract，不要只凭经验猜测。
- 源码只读：只用于阅读和定位问题，不要改源码，不要直接修改 `site-packages`、editable checkout 或共享环境。
