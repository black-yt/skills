# 自定义机器人 Webhook

## 适用范围

自定义机器人适合监控告警、日报、临时通知、CI/CD 推送等单向群通知。配置入口是目标群的群设置：群机器人 -> 添加机器人 -> 自定义机器人。官方入口：[自定义机器人使用指南](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot)，总览：[机器人概述](https://open.feishu.cn/document/client-docs/bot-v3/bot-overview)。

能力边界：

- 只能向所在群推送消息。
- 没有数据读取权限。
- 不能响应用户消息。
- 不能自行撤回消息。
- 不能查用户 ID。

## 官方入口

优先看这些官方页面，不要只凭旧脚本猜字段结构：

| 入口 | 用途 |
| --- | --- |
| [自定义机器人使用指南](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot) | 查看 webhook 如何发消息、`msg_type` 如何填写、签名如何计算、安全策略和常见错误。 |
| [机器人概述](https://open.feishu.cn/document/client-docs/bot-v3/bot-overview) | 查看自定义机器人和应用机器人的能力边界，确认当前需求是否只能单向推送，还是需要正式应用机器人。 |
| [飞书卡片概述](https://open.feishu.cn/document/uAjLw4CM/ukzMukzMukzM/feishu-cards/feishu-card-overview) | 查看卡片消息整体结构、卡片 JSON 2.0 风格和可用元素。Markdown 表格渲染应按卡片 JSON 2.0 写。 |
| [飞书消息卡片 Markdown 文档](https://open.feishu.cn/document/common-capabilities/message-card/message-cards-content/using-markdown-tags) | 查看卡片 Markdown 元素支持的语法和限制，特别是表格、列表、链接、代码块等是否按当前卡片版本支持。 |
| [飞书卡片搭建工具 CardKit](https://open.feishu.cn/cardkit) | 需要登录；适合可视化搭建和验证卡片，尤其是 `schema: "2.0"`、`body.elements`、`tag: "markdown"` 等结构。 |
| [飞书卡片搭建工具 Card Builder](https://open.feishu.cn/tool/cardbuilder) | 需要登录；如果 CardKit 入口不可用或界面不同，用这个入口可视化验证卡片 JSON 和元素渲染。 |

当前已验证成功的 Markdown 表格最小模板：

```json
{
  "msg_type": "interactive",
  "card": {
    "schema": "2.0",
    "config": {
      "wide_screen_mode": true
    },
    "header": {
      "template": "blue",
      "title": {
        "tag": "plain_text",
        "content": "Feishu 表格渲染测试"
      }
    },
    "body": {
      "elements": [
        {
          "tag": "markdown",
          "content": "| A | B |\n| --- | --- |\n| 1 | 2 |"
        }
      ]
    }
  }
}
```

关键经验：`text` 不渲染表格，旧式 `div + lark_md` 也不渲染表格；要用 `interactive card + schema 2.0 + body.elements.markdown`。

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

### Markdown 表格渲染

自定义机器人要渲染 Markdown 表格，不能用普通 `text` 消息，也不要用旧式 `div + lark_md` 卡片。已验证可行的是 `schema: "2.0"` + `body.elements[].tag = "markdown"`。

失败方式 1：普通 `text` 消息会发送成功，但只显示管道符，不渲染表格。

```json
{
  "msg_type": "text",
  "content": {
    "text": "| A | B |\n| --- | --- |\n| 1 | 2 |"
  }
}
```

失败方式 2：旧式卡片 `div + lark_md` 会发送成功，但 Markdown 表格不渲染。

```json
{
  "msg_type": "interactive",
  "card": {
    "config": {"wide_screen_mode": true},
    "header": {"title": {"tag": "plain_text", "content": "标题"}},
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "| A | B |\n| --- | --- |\n| 1 | 2 |"
        }
      }
    ]
  }
}
```

成功方式：使用 `schema: "2.0"`，并把表格放进 `body.elements` 中的 `markdown` 元素。

```json
{
  "msg_type": "interactive",
  "card": {
    "schema": "2.0",
    "config": {
      "wide_screen_mode": true
    },
    "header": {
      "template": "blue",
      "title": {
        "tag": "plain_text",
        "content": "巡检报告"
      }
    },
    "body": {
      "elements": [
        {
          "tag": "markdown",
          "content": "| 提交者 | 运行任务 | 占用资源 |\n| --- | --- | --- |\n| [USER] | 4 | 28 |"
        }
      ]
    }
  }
}
```

发送函数建议保留为“标题 + Markdown 正文”的结构：

```python
def send_feishu_report(title: str, markdown: str) -> dict:
    card_payload = {
        "msg_type": "interactive",
        "card": {
            "schema": "2.0",
            "config": {"wide_screen_mode": True},
            "header": {
                "template": "blue",
                "title": {"tag": "plain_text", "content": title},
            },
            "body": {
                "elements": [
                    {"tag": "markdown", "content": trim_text(markdown, 18000)},
                ]
            },
        },
    }
    return post_feishu(card_payload, webhook_url, secret=secret)
```

表格生成函数使用标准 Markdown 表格：

```python
def table(headers, rows):
    if not rows:
        return "无"
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)
```

如果已有脚本以前用 `text` 或 `div + lark_md` 发送表格，把实现改成：

```text
interactive card
schema 2.0
body.elements markdown
标准 Markdown 表格
```

### 报告型卡片排版与限制

飞书卡片适合承载短报告，但不要把所有信息都塞成表格。经验上把一张卡里的 Markdown 表格控制在少量核心表格内，通常不超过 4 张；如果表格太多，可能返回类似 `card table number over limit` 或 `ErrCode: 11310`。通用处理方式：

- 重要数据用表格，例如成员汇总、运行任务、节点卡位、提醒项。
- 次要数据用分点，例如排队摘要、其他占用、阈值说明和补充备注。
- 每个章节之间保留显式空行，表格后不要紧贴下一个标题或代码 fence。
- 对外部通知正文设置保守长度上限，例如 18k 字符左右；接近限制时截断并在末尾说明。
- 卡片发送成功只说明 JSON 被飞书接收，不代表内容排版好看；重要模板要实际在群里看一次渲染效果。

推荐用 helper 拼接章节，统一处理空行和长度限制：

```python
MAX_CARD_MARKDOWN = 18000


def trim_text(text: str, limit: int = MAX_CARD_MARKDOWN) -> str:
    if len(text) <= limit:
        return text
    suffix = "\n\n> 内容过长，已截断。"
    return text[: max(0, limit - len(suffix))].rstrip() + suffix


def section(title: str, body: str) -> str:
    body = body.strip() if body else "无"
    return f"## {title}\n\n{body}"


markdown = "\n\n".join([
    section("成员汇总", table(["提交者", "运行任务", "占用资源"], rows)),
    section("提醒项", "- 暂无需要提醒的异常。"),
])
```

注意：下面这类配置不像飞书自定义 webhook 的原生请求体，更像某个上层通知库的配置；直接发给飞书 webhook 没用。

```json
"feishu": {
  "renderMode": "card",
  "markdown": {
    "tableMode": "native",
    "mode": "native"
  }
}
```

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
    string_to_sign = f"{timestamp}\n{secret}"
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
