---
name: feishu-bot
description: "当需要创建、配置、调用或排查飞书/Lark 机器人时使用；覆盖自定义机器人 webhook 单向群通知、签名校验、消息格式、错误码，以及应用机器人收发消息、tenant_access_token、权限、事件订阅、卡片交互和资源上传。"
---

# Feishu Bot

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 说明飞书自定义机器人 webhook 的创建、发送、签名、安全设置、消息类型、Markdown 表格渲染、报告型卡片排版/长度/表格数量限制、官方文档入口和常见错误码；它只适合往某个群里单向推送告警、日报、CI/CD 通知或临时消息。 | 飞书、Lark、custom bot、webhook、群机器人、text、post、interactive card、schema 2.0、CardKit、tag markdown、Markdown 表格、card table number over limit、ErrCode 11310、报告卡片、长度截断、lark_md、sign、HMAC、关键词、IP 白名单、错误码、单向通知 | 只需要给群推送通知前；已有 webhook 需要发文本/富文本/卡片/Markdown 表格前；需要查官方文档或 CardKit 验证卡片 JSON 前；报告卡片出现表格不渲染、内容拥挤、表格数量超限或正文过长时；排查 `9499`、`19021`、`19022`、`19024`、`11310` 前；配置签名校验或安全策略前必须读取 | [references/custom-webhook.md](references/custom-webhook.md) |
| 2 | 说明飞书应用机器人的正式开发链路，覆盖自建应用、机器人能力、权限、`tenant_access_token`、消息 API、事件订阅、回复/编辑/撤回、资源上传、群管理和卡片回调边界。 | 飞书开放平台、应用机器人、自建应用、tenant_access_token、im:message、send_as_bot、chat_id、open_id、事件订阅、reply、update、delete、upload image、upload file、card callback | 需要收消息、自动回复、查用户 ID、发单聊、撤回/编辑消息、上传图片/文件、群管理、按钮点击回调或 AI Bot 前；自定义机器人能力不够时必须读取 | [references/app-bot.md](references/app-bot.md) |

## 路线选择

- 只做“往某个群里推送告警、日报、CI/CD 结果、临时通知”：优先用自定义机器人 webhook。
- 需要“收用户消息、自动回复、查 open_id/user_id、发单聊、撤回/编辑消息、上传文件、管理群、处理卡片按钮回调”：用应用机器人。
- 需要“AI 对话、工单流转、审批通知后可交互处理”：用应用机器人 + 事件订阅 + 飞书卡片。

## 安全规则

- 不要把 webhook、签名密钥、`app_secret`、`tenant_access_token` 写入仓库、日志、截图或最终回复。
- 示例统一使用 `[HOOK_URL]`、`[BOT_SECRET]`、`[TENANT_ACCESS_TOKEN]`、`[CHAT_ID]`、`[OPEN_ID]`、`[IMAGE_KEY]`、`[MESSAGE_ID]` 等占位符。
- webhook 等同于“发消息密钥”。正式使用时至少开启一种安全策略，推荐签名校验；如果 webhook 曾公开暴露，重置 webhook 或重新配置签名密钥。
- 自定义机器人不能查用户 ID、不能响应用户消息、不能撤回消息；不要把它包装成正式交互机器人。
- 应用机器人需要权限申请、版本发布和管理员审核；不要在没确认权限的情况下盲目排查代码。

## 快速判断

- `curl "[HOOK_URL]"` 这种请求是自定义机器人 webhook。
- `Authorization: Bearer [TENANT_ACCESS_TOKEN]` + `/open-apis/im/v1/messages` 是应用机器人消息 API。
- 自定义机器人发卡片通常是顶层 `card`。
- 应用机器人发卡片时，`content` 通常是 JSON 字符串，需要转义。
- `@` 单人需要 `open_id` 或 `user_id`，并且目标用户必须在群里；外部群通常只支持 Open ID。

## 验证清单

- 发送前确认机器人类型，不要把自定义 webhook 和应用机器人 API 的请求体混用。
- 先发最小 text 消息，再尝试富文本、图片或卡片。
- 如果开启签名，确认 `timestamp` 是秒级时间戳，且请求在 1 小时有效期内。
- 如果开启关键词安全策略，确认消息文本或 title 包含配置关键词。
- 如果开启 IP 白名单，确认调用出口 IP 在白名单里。
- 对应用机器人，先确认权限、`tenant_access_token`、`receive_id_type`、`receive_id` 和 `content` 转义格式。
