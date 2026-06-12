# 自定义机器人 Webhook

## 适用范围

自定义机器人适合监控告警、日报、临时通知、CI/CD 推送等单向群通知。配置入口是目标群的群设置：群机器人 -> 添加机器人 -> 自定义机器人。官方入口：[自定义机器人使用指南](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot)，总览：[机器人概述](https://open.feishu.cn/document/client-docs/bot-v3/bot-overview)。

能力边界：

- 只能向所在群推送消息。
- 没有数据读取权限。
- 不能响应用户消息。
- 不能自行撤回消息。
- 不能查用户 ID。

## 最小发送

```bash
curl -X POST "[HOOK_URL]" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"request example"}}'
```

成功响应通常类似：

```json
{"StatusCode":0,"StatusMessage":"success","code":0,"data":{},"msg":"success"}
```

## 文本消息

```json
{
  "msg_type": "text",
  "content": {
    "text": "新更新提醒"
  }
}
```

文本中 @ 单人：

```json
{
  "msg_type": "text",
  "content": {
    "text": "<at user_id=\"[OPEN_ID_OR_USER_ID]\">Tom</at> 新更新提醒"
  }
}
```

@ 所有人：

```html
<at user_id="all">所有人</at>
```

注意：

- @ 单人需要 `open_id` 或 `user_id`。
- 被 @ 用户必须是该群成员。
- 外部群通常只支持 Open ID。
- 自定义机器人不能查 ID；需要通过应用机器人或通讯录 API 获取。

## 富文本 post

```json
{
  "msg_type": "post",
  "content": {
    "post": {
      "zh_cn": {
        "title": "项目更新通知",
        "content": [
          [
            {"tag": "text", "text": "项目有更新："},
            {"tag": "a", "text": "请查看", "href": "https://example.com"},
            {"tag": "at", "user_id": "[OPEN_ID_OR_USER_ID]"}
          ]
        ]
      }
    }
  }
}
```

## 图片消息

```json
{
  "msg_type": "image",
  "content": {
    "image_key": "[IMAGE_KEY]"
  }
}
```

图片要先通过上传图片接口拿 `image_key`。官方：[上传图片](https://open.feishu.cn/document/server-docs/im-v1/image/create)。

## 群名片

```json
{
  "msg_type": "share_chat",
  "content": {
    "share_chat_id": "[CHAT_ID]"
  }
}
```

## 卡片消息

自定义机器人发卡片时通常使用顶层 `card`。卡片官方入口：[飞书卡片概述](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/feishu-card-overview)。

```json
{
  "msg_type": "interactive",
  "card": {
    "schema": "2.0",
    "header": {
      "title": {"tag": "plain_text", "content": "告警通知"},
      "template": "red"
    },
    "body": {
      "elements": [
        {
          "tag": "markdown",
          "content": "**服务异常**\n请立即查看。"
        }
      ]
    }
  }
}
```

和应用机器人区别：

- 自定义机器人 webhook：通常顶层是 `card`。
- 应用机器人消息 API：`content` 通常是转义后的 JSON 字符串。

## 安全设置

强烈建议至少开启一种安全策略。webhook 本身等同于“发消息密钥”。

| 策略 | 作用 | 注意 |
| --- | --- | --- |
| 关键词 | 消息必须包含配置关键词 | 最多 10 个；通常检查 text/title 等文本值 |
| IP 白名单 | 只允许指定 IP 调用 | 最多 10 个；可用 `123.1.1.*` 或 CIDR |
| 签名校验 | 请求必须带 `timestamp` 和 `sign` | 时间戳单位秒，通常要求 1 小时内 |

### 签名算法

把 `timestamp + "\n" + secret` 作为 HMAC-SHA256 的 key，对空字符串计算摘要，再 Base64。

```python
import base64
import hashlib
import hmac
import time

timestamp = str(int(time.time()))
secret = "[BOT_SECRET]"
string_to_sign = f"{timestamp}\n{secret}"
sign = base64.b64encode(
    hmac.new(string_to_sign.encode("utf-8"), b"", hashlib.sha256).digest()
).decode("utf-8")
```

签名请求体：

```json
{
  "timestamp": "1599360473",
  "sign": "[SIGN]",
  "msg_type": "text",
  "content": {
    "text": "request example"
  }
}
```

完整签名发送示例：

```python
import base64
import hashlib
import hmac
import time

import requests


def make_sign(timestamp: str, secret: str) -> str:
    string_to_sign = f"{timestamp}
{secret}"
    digest = hmac.new(string_to_sign.encode("utf-8"), b"", hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def send_text_with_sign(hook_url: str, secret: str, text: str) -> dict:
    timestamp = str(int(time.time()))
    payload = {
        "timestamp": timestamp,
        "sign": make_sign(timestamp, secret),
        "msg_type": "text",
        "content": {"text": text},
    }
    response = requests.post(hook_url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


result = send_text_with_sign("[HOOK_URL]", "[BOT_SECRET]", "飞书机器人测试消息")
print(result)
```

排查签名时先固定输入值，只验证 `timestamp`、`secret`、HMAC key 和请求体字段位置；确认签名正确后再接入业务逻辑。

## 常见错误

| 错误 | 常见原因 | 处理 |
| --- | --- | --- |
| `9499 Bad Request` | 请求体格式错、JSON 不合法、字段位置不对 | 先发最小 text；确认 `Content-Type` 和 JSON 结构 |
| `19024 Key Words Not Found` | 关键词安全策略未命中 | 消息正文或 title 加入配置关键词 |
| `19022 Ip Not Allowed` | 出口 IP 不在白名单 | 查调用机器出口 IP，更新白名单 |
| `19021 sign match fail` | 签名错误、secret 错、timestamp 过期或单位不对 | 用秒级 timestamp；按 HMAC 规则重算 |

## 限制

- 单租户单机器人约 `100 次/分钟`、`5 次/秒`。
- 请求体不超过 `20 KB`。
- 不能响应消息。
- 不能自行撤回消息。
- webhook 曾公开暴露时，正式使用前重置 webhook 或至少开启签名校验。
