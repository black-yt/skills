---
name: cluster-web-portal
description: "当需要访问、登录、自动化查询或排查集群管理网站/集群 Web 控制台时使用；覆盖浏览器/OIDC 登录、凭据和 token 安全、会话刷新、网页后端 API 探索、Prometheus/DCGM 监控查询、pod/rjob 映射和报告数据分层。"
---

# Cluster Web Portal

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 说明访问集群管理网站时如何选择执行位置、如何用浏览器式 OIDC authorization code flow 登录、如何保存和刷新 token、如何保护账号密码和 cookie/token 文件，并明确不要绕过认证或把 secret 写入日志。 | cluster portal、web console、OIDC、authorization code、discovery endpoint、token endpoint、refresh token、cookie jar、session、credential file、chmod 600、secret safety、login form、headless browser、urllib、requests | 需要登录集群网页前；需要自动化获取 access token 或 refresh token 前；本地网络无法访问但开发机/CPU worker 可访问时；排查 `unauthorized_client`、登录跳转失败、token 过期、cookie 丢失或凭据泄漏风险时必须读取 | [references/login-oidc-session.md](references/login-oidc-session.md) |
| 2 | 说明网页登录后如何只读探索网页后端 API 和监控接口，如何查询 Prometheus/DCGM 指标，如何用 pod/replica/namespace 把监控数据映射到 rjob 任务，并如何把任务层信息、监控层信息和通知层信息分开合并成报告。 | monitoring API、Prometheus、PromQL、DCGM、GPU util、FB used、FB free、power、temperature、Hostname、gpu label、namespace、pod mapping、replica、rjob、other occupancy、report merge、rate limit、read-only API | 需要从集群网页或后端 API 获取 GPU 利用率/显存/功率/温度前；需要把网页监控数据和 rjob 信息合并前；排查 PromQL 422、label 不匹配、pod 无法归因、监控数据缺失或报告口径混乱时必须读取 | [references/monitoring-api-and-reporting.md](references/monitoring-api-and-reporting.md) |

## 核心边界

- 把集群 Web 控制台视为“需要授权的只读数据源”。不要尝试绕过登录、扫描无关接口、越权访问、批量抓取非任务相关数据或绕过组织安全策略。
- 本 skill 只记录通用网页登录、token 管理、监控 API 查询和数据合并方法。具体域名、账号文件、脚本路径、项目名称、namespace、quota group、API key 和 token 都必须用占位符。
- 网页登录和后端 API 探索通常应在能访问内网 Web 控制台的位置执行，例如开发机、CPU worker 或 CPU rjob。本地 WSL/个人电脑如果网络不可达，不要误判代码错误。
- 不要把账号密码写入 `.bashrc`、命令行历史、日志、仓库、最终回复或截图。需要自动化登录时，使用权限收紧的 secret 文件或安全凭据管理方式。
- token、cookie jar、抓包结果和 API 响应可能包含敏感信息。保存前先确定用途和生命周期，用后清理或放入明确的 gitignored 目录。
- 监控数据和任务数据必须分层：rjob/SDK/CLI 提供任务层；网页后端/Prometheus/DCGM 提供监控层；飞书或其他 webhook 只是通知层。

## 基本流程

1. 明确执行位置：先确认当前机器能访问 `[PORTAL_BASE_URL]`；不能访问时，转到开发机、CPU worker 或 CPU rjob。
2. 确认认证方式：优先按网页登录/OIDC flow 走完整授权，不要把 password grant 当成默认可用方式。
3. 安全保存凭据：账号密码文件、token 文件、cookie jar 使用 `chmod 600`，目录使用 `chmod 700`。
4. 只读获取 token：用 discovery endpoint 找 authorization/token endpoint，完成 authorization code flow 后保存 access/refresh token。
5. 优先 refresh：后续任务优先用 refresh token；refresh 失败再重新登录。
6. 探索 API：从浏览器 Network 面板、官方文档或只读请求中确认真实 API 路径、参数、返回字段和权限边界。
7. 查询监控：对 Prometheus/DCGM 这类指标使用小范围、短窗口、可解释的 PromQL；不要一次请求过大时间范围或无过滤全量数据。
8. 合并报告：用 rjob 的 pod/replica/namespace 与监控 label 做映射；无法映射的数据单独展示为其他占用。
9. 验证输出：检查报告中没有 token、cookie、账号、真实私有 URL 或不该公开的节点细节。

## 与其他 Skill 的分工

- `lab-cluster-1`：负责 SSH、rlaunch/rjob、CPU/GPU 作业、远端路径、代理、服务部署和任务层查询。
- `cluster-web-portal`：负责网页登录、token 会话、网页后端 API、Prometheus/DCGM 监控指标和任务/监控数据合并。
- `feishu-bot`：负责把已经整理好的报告推送到飞书/Lark，不负责登录集群网页或查询监控。

## 验证清单

- 登录脚本只读运行，没有写入仓库、命令历史或日志中的 secret。
- token 文件和 cookie 文件权限收紧，路径位于 gitignored 或临时目录。
- API 请求带超时、错误处理和最小必要查询范围。
- PromQL label 过滤不会漏掉目标 namespace/pod，也不会把无关 namespace 硬归因给某个 rjob。
- 报告里明确区分“任务申请/卡位”和“真实 GPU 利用率/显存/功率/温度”。
- 需要外部通知时，只把整理后的脱敏报告交给通知 skill。
