---
name: llm-image-generation
description: "当需要通过 OpenAI-compatible LLM 网关生成图片时使用，尤其是使用 LLM_API_KEY 和 LLM_BASE_URL 调用 gpt-image-2、gpt-image-1、dall-e-3 等图像模型；覆盖环境变量检查、缺失配置提示、模型选择、/images/generations 请求、长等待时间处理、base64/URL 返回保存和排错。"
---

# LLM Image Generation

## 使用原则

- 优先从环境变量读取 `LLM_API_KEY` 和 `LLM_BASE_URL`，不要把 key 写进代码、日志、README 或命令输出。
- 如果环境变量缺失，先要求用户配置环境变量，不要猜测 key 或 base URL。
- 图像生成比普通 chat completion 慢很多。请求发出后 60-180 秒没有输出是常见情况；默认等待至少 180 秒，推荐超时设置为 300 秒。不要因为 30-60 秒无输出就判断失败。
- 输出图片保存到用户指定路径或当前项目的明确输出目录。仅测试时可以临时写入 `/tmp`，但验证后必须删除。
- 只在用户明确要求真实生成图片时调用接口；普通写作、提示词设计或代码生成不需要真的发图像请求。

## 环境变量

必需：

```bash
export LLM_API_KEY="sk-..."
export LLM_BASE_URL="http://host:port/v1"
```

可选：

```bash
export LLM_IMAGE_MODEL="gpt-image-2"
```

检查当前环境：

```bash
python3 - <<'PY'
import os
print("LLM_API_KEY:", "<set>" if os.environ.get("LLM_API_KEY") else "<unset>")
print("LLM_BASE_URL:", os.environ.get("LLM_BASE_URL", "<unset>"))
print("LLM_IMAGE_MODEL:", os.environ.get("LLM_IMAGE_MODEL", "<unset>"))
PY
```

如果 `LLM_API_KEY` 或 `LLM_BASE_URL` 是 `<unset>`，回复用户：

```text
当前环境缺少 LLM_API_KEY 或 LLM_BASE_URL。请先在 shell 中配置：

export LLM_API_KEY="sk-..."
export LLM_BASE_URL="http://host:port/v1"

如果有指定图像模型，也可以配置：

export LLM_IMAGE_MODEL="gpt-image-2"
```

## 模型选择

先查询模型列表，再选择模型：

```bash
python3 - <<'PY'
import os, json, urllib.request

base = os.environ["LLM_BASE_URL"].rstrip("/")
key = os.environ["LLM_API_KEY"]
req = urllib.request.Request(
    base + "/models",
    headers={"Authorization": f"Bearer {key}"},
)
with urllib.request.urlopen(req, timeout=60) as r:
    data = json.load(r)

models = [m.get("id", "") for m in data.get("data", [])]
for m in models:
    ml = m.lower()
    if "image" in ml or "dall" in ml:
        print(m)
PY
```

默认优先级：

1. `LLM_IMAGE_MODEL`，如果用户或环境已指定。
2. `gpt-image-2`，如果模型列表存在。
3. `gpt-image-1`。
4. `gpt-image-1-mini`。
5. `dall-e-3`。
6. `dall-e-2`。

如果这些都不存在，向用户报告模型列表中没有明确可用的图像生成模型，并询问要使用哪个模型。

## 生成图片

下面的脚本使用标准库，无需安装 OpenAI SDK。它会：

- 从环境变量读取 key/base/model。
- 请求 `/images/generations`。
- 等待最多 300 秒。
- 支持 `b64_json` 或 `url` 返回。
- 不打印 API key。

```bash
python3 - <<'PY'
import base64
import json
import os
import pathlib
import urllib.error
import urllib.request

base = os.environ.get("LLM_BASE_URL", "").rstrip("/")
key = os.environ.get("LLM_API_KEY")
model = os.environ.get("LLM_IMAGE_MODEL", "gpt-image-2")

prompt = "A clean scientific icon of a blue beaker with a small sparkle, white background."
out_path = pathlib.Path("generated_image.png")

if not key or not base:
    raise SystemExit(
        "Missing LLM_API_KEY or LLM_BASE_URL. Please export both before generating images."
    )

payload = {
    "model": model,
    "prompt": prompt,
    "size": "1024x1024",
    "n": 1,
}

req = urllib.request.Request(
    base + "/images/generations",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    },
    method="POST",
)

print(f"[INFO] Request sent to {base}/images/generations with model={model}.")
print("[INFO] Image generation may take 60-180 seconds; waiting up to 300 seconds.")

try:
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.load(r)
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    print(f"[ERROR] HTTP {e.code}")
    print(body[:2000])
    raise SystemExit(1)
except TimeoutError:
    print("[ERROR] Timed out after 300 seconds. The request may be slow or the model may be unavailable.")
    raise SystemExit(1)

items = data.get("data") or []
if not items:
    print("[ERROR] Response has no data field.")
    print(json.dumps(data, ensure_ascii=False)[:2000])
    raise SystemExit(1)

item = items[0]
if item.get("b64_json"):
    image_bytes = base64.b64decode(item["b64_json"])
    out_path.write_bytes(image_bytes)
    print(f"[INFO] Saved image to {out_path.resolve()} ({len(image_bytes)} bytes).")
elif item.get("url"):
    img_req = urllib.request.Request(item["url"])
    with urllib.request.urlopen(img_req, timeout=300) as r:
        image_bytes = r.read()
    out_path.write_bytes(image_bytes)
    print(f"[INFO] Downloaded image to {out_path.resolve()} ({len(image_bytes)} bytes).")
else:
    print("[ERROR] Response has neither b64_json nor url.")
    print(json.dumps(data, ensure_ascii=False)[:2000])
    raise SystemExit(1)
PY
```

如果只是验证接口是否可用，可以把 `out_path` 指向临时文件，验证 PNG 后立刻删除：

```python
path = pathlib.Path("/tmp/codex_gpt_image_test.png")
path.write_bytes(image_bytes)
print(path.stat().st_size)
path.unlink()
```

## 等待时间与状态判断

- 0-30 秒无输出：正常，不要中断。
- 30-90 秒无输出：仍然正常，图像模型经常需要较长生成时间。
- 90-180 秒无输出：继续等待，尤其是 `gpt-image-2` 这类较新模型。
- 超过 300 秒：按超时处理，记录模型名、endpoint、HTTP 状态或错误正文，再考虑换模型或重试。

发起请求后应给用户明确状态说明，例如：

```text
图像生成请求已发出。该接口可能需要 60-180 秒返回；我会等到 300 秒超时后再判断失败。
```

## 排错

- `LLM_API_KEY=<unset>` 或 `LLM_BASE_URL=<unset>`：要求用户先配置环境变量。
- HTTP 401/403：key 无效、权限不足或网关拒绝；不要打印 key。
- HTTP 404：`LLM_BASE_URL` 不对、网关不支持 `/images/generations`，或模型名不可用。
- HTTP 400：检查 `model`、`size`、`n`、`prompt` 参数。先把请求缩小到 `n=1` 和 `1024x1024`。
- 300 秒超时：不要立刻认为代码错。先换 `gpt-image-1` 或 `dall-e-3` 对照，再判断是模型慢还是接口不可用。
- 返回没有 `b64_json`：检查是否返回 `url`；两者都没有时打印不含 key 的响应摘要。
- 生成成功但文件打不开：检查是否正确 base64 decode，确认文件头是否为 PNG/JPEG。

## 当前环境实测记录

在本环境中，`LLM_BASE_URL=http://35.220.164.252:3888/v1` 的模型列表包含 `gpt-image-2`、`gpt-image-1`、`gpt-image-1-mini`、`dall-e-3` 等图像模型。`gpt-image-2` 调用 `/images/generations` 可返回 `b64_json`，解码后是有效 PNG。实际调用时等待时间超过 60 秒属于正常现象。
