# 调用、验证与排错

## 基本命令

```bash
SKILL_DIR='/path/to/cloudflare-flux-image-generation'
python3 "$SKILL_DIR/scripts/generate_image.py" \
  'a small orange cat on a rainy street, cinematic photography, evening light' \
  --output ./cat.jpg
python3 "$SKILL_DIR/scripts/generate_image.py" \
  'a mountain lake at dawn, watercolor painting' --steps 6 --output ./lake.jpg
```

`prompt` 必填，官方模型限制 1–2048 字符。建议把中文需求准确转成英文提示词，并描述主体、动作、风格、背景和光线；“仅懂英文”不是官方硬限制。`--steps` 是 1–8 的整数，默认 4；更多步数会增加 Neurons 消耗。输出路径默认是当前目录下带 UTC 时间戳的 `.jpg`；只接受 `.jpg`/`.jpeg` 后缀，已存在文件默认拒绝覆盖。`--overwrite` 仅在明确需要替换成品时使用。

该脚本通过 `POST /client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell` 请求图片，JSON 请求体含 `prompt`、`steps`；解析响应 `result.image` 的 base64 JPEG。暂时性失败可能触发有界重试。模型 API 详情见[官方模型页](https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/)。

## Python 中复用

```python
import sys
sys.path.insert(0, '/path/to/cloudflare-flux-image-generation/scripts')
from generate_image import generate

result = generate('a blue bird on a branch, ink illustration', output='./bird.jpg', steps=4)
print(result['path'], result['duration_seconds'])
```

调用进程需要预先设置 `CLOUDFLARE_ACCOUNT_ID` 和 `CLOUDFLARE_API_TOKEN`。脚本不会把 token 写入返回值或图片。真实输出尺寸由模型返回决定；不要把 prompt 中的横图/竖图文字当作尺寸参数。

## 验收

```bash
test -s ./cat.jpg
file ./cat.jpg
python3 -c 'from pathlib import Path; p=Path("cat.jpg"); b=p.read_bytes(); assert b[:3]==bytes.fromhex("ffd8ff") and b[-2:]==bytes.fromhex("ffd9"); print(len(b), "JPEG bytes")'
```

还应实际打开图片检查内容；文件有效不等于画面满足需求。生图失败时，脚本不会把损坏字节当成成品保存。

## 免费额度怎样算

按[2026-10-23 官方价格页](https://developers.cloudflare.com/workers-ai/platform/pricing/)：免费分配 10,000 Neurons/天；此模型按每个 512×512 tile 4.80 Neurons、每步 9.60 Neurons 计。若一次输出是 1024×1024、4 步，估算为 `4 × 4.80 + 4 × 9.60 = 57.60 Neurons`，理论上单独使用此模型可约 173 张/天。输出尺寸、模型计量和账号其他 Workers AI 用量都会影响实际张数；不要把它当成固定“170 张/天”配额。UTC 00:00 重置。Workers Paid 可能对超出免费分配的使用收费；大批量任务先看控制台用量和当前价格。

## 常见失败

| 表现 | 检查与动作 |
| --- | --- |
| 缺环境变量 | 用当前 shell 的 `env` 检查变量是否存在；只输出是否设置，不打印 token。确认脚本和变量在同一进程环境。 |
| HTTP 401/403 | 核对 Account ID、token 所属账号、有效期和 Workers AI 权限；自定义 token 参考官方入门页的 Read 与 Edit 要求。不要连续重试同一个无效 token。 |
| HTTP 400/内容策略 | 阅读截断后的 Cloudflare 错误说明，检查 prompt 长度和 `steps`；内容过滤时调整提示词，不循环碰撞过滤器。 |
| HTTP 429/暂时性 5xx | 脚本最多重试两次并做短暂退避；持续失败时检查网络、服务状态和账户限制，稍后重试。不要堆积并发。 |
| 配额用尽 | 到 Workers AI 控制台确认 Neurons 用量和计划。Free 计划等次日 UTC 重置或按用户意愿调整计划；Paid 计划确认计费。 |
| 没有图片/格式不符 | 检查 API 响应结构是否变化及模型文档；脚本要求 base64 解码后有 JPEG 起止标记，不会误写 PNG 为 JPEG。 |
| 超时/代理/TLS | 检查本机连通性、时间和代理配置；不要通过关闭 TLS 校验绕过证书问题。 |

当前接口、权限与定价由 Cloudflare 官方文档和账号实际状态决定；本文中的额度与参数依据 2026-10-23 公开文档。
