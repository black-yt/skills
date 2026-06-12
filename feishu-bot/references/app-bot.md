# 应用机器人

## 适用范围

应用机器人适合正式业务系统、AI Bot、审批/工单/群管理、可交互机器人。它可以发消息、收消息、回复、撤回/编辑、上传资源、做群管理和处理卡片交互。配置入口是[飞书开放平台开发者后台](https://open.feishu.cn/app)。

当需求超过“往某个群里单向推送通知”时，通常需要应用机器人。

## 开发链路

1. 在开发者后台创建自建应用。官方：[自建应用开发流程](https://open.feishu.cn/document/home/introduction-to-custom-app-development/self-built-application-development-process)。
2. 开启机器人能力。官方：[如何启用机器人能力](https://open.feishu.cn/document/uAjLw4CM/ugTN1YjL4UTN24CO1UjN/trouble-shooting/how-to-enable-bot-ability)。
3. 申请权限，例如 `im:message:send_as_bot`、`im:message`、`im:resource`。
4. 发布应用版本，等待管理员审核。
5. 获取 `tenant_access_token`。官方：[获取 tenant_access_token](https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal)。
6. 调用消息 API。官方：[发送消息](https://open.feishu.cn/document/server-docs/im-v1/message/create)。

## 获取 tenant_access_token

内部应用通常用 `app_id` 和 `app_secret` 换取租户访问令牌。不要把真实 `app_secret` 写进仓库。

```bash
curl -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d '{
    "app_id": "[APP_ID]",
    "app_secret": "[APP_SECRET]"
  }'
```

响应中取 `tenant_access_token`，后续消息 API 使用：

```http
Authorization: Bearer [TENANT_ACCESS_TOKEN]
```

排查顺序：

- `app_id` 和 `app_secret` 是否属于同一个应用。
- 应用是否已发布到当前租户。
- 机器人能力和消息权限是否已经启用并通过审核。
- token 是否过期；不要把旧 token 当作长期密钥写死。

## 发送消息

```bash
curl --location --request POST \
  'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id' \
  --header 'Authorization: Bearer [TENANT_ACCESS_TOKEN]' \
  --header 'Content-Type: application/json; charset=utf-8' \
  --data-raw '{
    "receive_id": "[CHAT_ID]",
    "msg_type": "text",
    "content": "{\"text\":\"test content\"}",
    "uuid": "[OPTIONAL_DEDUPLICATE_ID]"
  }'
```

关键点：

- `Authorization` 使用 `Bearer [TENANT_ACCESS_TOKEN]`。
- `receive_id_type` 要和 `receive_id` 匹配，例如 `chat_id`、`open_id`、`user_id`。
- `content` 通常是 JSON 字符串，不是 JSON object；需要正确转义。
- `uuid` 可用于去重，按业务需要设置。

发送内容结构参考：[发送消息内容结构](https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json)。

应用机器人可发送：

- `text`
- `post`
- `image`
- `file`
- `audio`
- `media`
- `sticker`
- `interactive`
- `share_chat`
- `share_user`
- `system`

常见 `content` 写法如下。注意这些示例里的 `content` 都是字符串，在真实 JSON 请求体中需要转义。

文本：

```json
{"text":"test content"}
```

富文本：

```json
{"post":{"zh_cn":{"title":"项目更新","content":[[{"tag":"text","text":"请查看更新"},{"tag":"a","text":"链接","href":"https://example.com"}]]}}}
```

图片：

```json
{"image_key":"[IMAGE_KEY]"}
```

卡片：

```json
{"type":"template","data":{"template_id":"[CARD_TEMPLATE_ID]","template_variable":{"title":"通知标题"}}}
```

如果直接发送卡片 JSON，而不是模板卡片，仍然要按当前飞书卡片文档生成合法卡片结构，再整体作为 `content` 字符串传入。

## 接收消息

订阅 `im.message.receive_v1` 事件。官方：[接收消息](https://open.feishu.cn/document/server-docs/im-v1/message/events/receive)，事件订阅总览：[事件订阅概述](https://open.feishu.cn/document/ukTMukTMukTM/uUTNz4SN1MjL1UzM)。

使用场景：

- AI 对话机器人。
- 用户向机器人发指令。
- 群内 @ 机器人触发自动回复。
- 工单、审批或通知状态回流。

排查顺序：

1. 确认应用已开启机器人能力。
2. 确认事件订阅已配置并发布。
3. 确认回调 URL 可公网访问，或已配置正确的事件接收方式。
4. 确认权限包含消息读取或事件订阅所需权限。
5. 确认应用版本已发布并通过管理员审核。

事件处理边界：

- 第一次接入时先处理飞书平台的 URL 校验或 challenge 事件。
- 正式消息事件里需要读取 `message_id`、`chat_id`、`sender`、`message_type` 和 `content`。
- 机器人回复前要避免重复处理同一事件，建议按事件 ID 或消息 ID 做幂等。
- 如果机器人会调用 LLM，先在服务端做权限、群聊范围和输入长度限制。

## 回复、编辑和撤回

回复消息：

```http
POST /open-apis/im/v1/messages/:message_id/reply
```

官方：[回复消息](https://open.feishu.cn/document/server-docs/im-v1/message/reply)。

编辑消息：

```http
PUT /open-apis/im/v1/messages/:message_id
```

官方：[编辑消息](https://open.feishu.cn/document/server-docs/im-v1/message/update)。

注意：

- 通常只支持编辑机器人自己发出的文本、富文本消息。
- 一条消息最多编辑约 20 次。

撤回消息：

```http
DELETE /open-apis/im/v1/messages/:message_id
```

官方：[撤回消息](https://open.feishu.cn/document/server-docs/im-v1/message/delete)。

注意：

- 机器人通常可撤回自己发的消息。
- 群主/管理员身份可能具备撤回群消息能力，按实际权限判断。

## 上传资源

图片走上传图片接口：[上传图片](https://open.feishu.cn/document/server-docs/im-v1/image/create)。

文件、音频、视频走上传文件接口：[上传文件](https://open.feishu.cn/document/server-docs/im-v1/file/create)。

常见限制：

- 图片不超过 `10 MB`。
- 文件不超过 `30 MB`。
- 上传后拿到 `image_key`、`file_key` 等资源 key，再用于消息发送。

## 群管理

应用机器人可以创建群、拉人、获取群信息、维护群公告、配置群菜单等。入口可从机器人概述里的群组开放能力继续查：[机器人概述](https://open.feishu.cn/document/client-docs/bot-v3/bot-overview)。

群管理通常需要额外权限和管理员审核，不要只看消息发送权限。

## 卡片交互

应用机器人适合处理按钮点击、表单提交、审批流转、AI 对话中的快捷操作等交互。卡片官方入口：[飞书卡片概述](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/feishu-card-overview)。

和自定义 webhook 区别：

- 自定义 webhook 只负责把卡片推到群里，无法处理用户点击后的业务回调。
- 应用机器人可以配合事件订阅或卡片回调处理交互。
- 应用机器人发 `interactive` 时，`content` 通常是转义后的 JSON 字符串。

## 选择建议

- 只做“某个群的告警/日报推送”：用自定义机器人，开启签名校验。
- 要“能收消息、自动回复、@ 用户、查 open_id、发单聊、撤回/编辑、上传文件、管理群”：用应用机器人。
- 要“按钮点击后通知服务端、AI 对话、工单流转”：用应用机器人 + 事件订阅 + 飞书卡片交互。
