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
| 1 | 概括 ResearchHarness 的定位、可用模式、必须先配置工具 key 的前提，以及不能修改源码/共享环境的边界。 | 总览、使用边界、安全限制、源码只读 | 默认读取 | `SKILL.md` |
| 2 | 说明如何从 PyPI 或 GitHub 获取 ResearchHarness、如何定位包内源码、以及只读追溯模块行为的方法。 | PyPI、GitHub、项目结构、源码追溯、只读源码 | 需要安装、定位源码、确认项目结构或阅读源码时必须读取 | [references/setup-and-source.md](references/setup-and-source.md) |
| 3 | 记录 CLI、本地前端和 Python API 的运行方式，并列出 `.env`、工具 key、模型参数和生命周期相关环境变量。 | 运行模式、生命周期、环境变量、CLI、Python API、本地前端 UI | 需要运行 CLI、本地前端、Python API 或配置环境变量时必须读取 | [references/runtime-cli-python.md](references/runtime-cli-python.md) |
| 4 | 说明如何启动和调用 OpenAI-compatible API server，重点覆盖 chat completions、`extra_body` object 约束和协议兼容边界。 | OpenAI-compatible server、chat completions、extra_body、请求协议 | 需要部署或调用 API server，或处理 OpenAI-compatible 请求参数时必须读取 | [references/api-server-and-protocol.md](references/api-server-and-protocol.md) |
| 5 | 记录工具可用性测试、workspace 路径约束、trace/compaction 产物、benchmark adapter 和联网工具代理排错。 | tools、workspace、trace、compaction、benchmark adapters、测试验证、常见边界 | 需要配置 tools、处理 workspace/trace/compaction、接 benchmark 或验证工具可用性时必须读取 | [references/tools-workspace-testing.md](references/tools-workspace-testing.md) |

## 使用边界

- ResearchHarness 是轻量、可审计的 tool-using LLM agent harness。
- 适合本地 agent 工作、benchmark 公平执行底座、OpenAI-compatible agent API 后端、代码/文件/PDF/图片/网页任务。
- 它是 base harness，不是大型 workflow platform、多租户服务或完整产品平台。
- 不要擅自安装依赖、升级共享环境、修改长期配置或暴露公网服务；需要时先征得用户同意。
- API server 默认没有用户认证；公开暴露前必须加外层认证、访问控制或只绑定可信内网。
- trace/session state 不要放进 agent 可见 workspace，避免 agent 读取自己的执行记录。
- 推荐通过源码阅读确认复杂行为、参数默认值、工具 schema 和 API contract，不要只凭经验猜测。
- 源码只读：只用于阅读和定位问题，不要改源码，不要直接修改 `site-packages`、editable checkout 或共享环境。
