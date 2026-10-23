---
name: cloudflare-flux-image-generation
description: "使用 Cloudflare Workers AI 的 FLUX.1 schnell 免费额度按文字生成 JPEG 图片时使用；覆盖账号注册、Workers AI API Token、Python 标准库脚本调用、额度核算和故障排查。"
---

# Cloudflare FLUX 图片生成

## 适用范围

- 使用 Cloudflare Workers AI REST API 的 `@cf/black-forest-labs/flux-1-schnell` 文生图模型，运行 [完整脚本](scripts/generate_image.py)，把 API 返回的 base64 JPEG 保存到本地。Python 3.10+ 标准库即可，不依赖源项目或第三方 Python 包。
- 首次使用先读[注册与配置](references/01_account_and_setup.md)；要执行生图、改参数或排错时读[调用与排错](references/02_usage_and_troubleshooting.md)。
- 仅支持文本生成单张 JPEG。图片输入、局部编辑、批量并发、尺寸指定和 PNG 输出不在这个脚本的能力内；需要这些能力时先核对当前模型文档。

## 执行要点

1. 检查 Python 版本、Cloudflare 账号和 Workers AI 权限。只通过当前进程环境变量传 `CLOUDFLARE_ACCOUNT_ID`、`CLOUDFLARE_API_TOKEN`；不得把真实 token 写入仓库、prompt、命令行参数或日志。
2. 查看当前 [模型参数](https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/)与[定价](https://developers.cloudflare.com/workers-ai/platform/pricing/)。免费额度和权限可能变化；付费计划的超额请求可能收费。
3. 先生成一张测试图，指定新文件名；检查退出码、JPEG 类型与画面内容，再按需继续。输出已有文件时，只有用户明确要替换才加 `--overwrite`。
4. 失败时按 HTTP 状态、Cloudflare 错误码和本地输出核对；429/暂时性 5xx 有界重试，401/403、配额或内容策略错误先处理原因，避免无界重试。

## 最短调用

```bash
python3 --version
export CLOUDFLARE_ACCOUNT_ID='[ACCOUNT_ID]'
read -r -s -p 'Cloudflare Workers AI token: ' CLOUDFLARE_API_TOKEN; printf '\n'
export CLOUDFLARE_API_TOKEN
python3 /path/to/cloudflare-flux-image-generation/scripts/generate_image.py \
  'a red fox reading a book, watercolor illustration, soft light' \
  --output ./fox.jpg
```

`[ACCOUNT_ID]` 是占位符；示例中的 `read -s` 让 token 不进入 shell history。脚本不会自动读取 `.env`。使用后可在当前 shell 执行 `unset CLOUDFLARE_API_TOKEN`。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 说明 Cloudflare 免费账号注册、Workers AI 仪表盘获取 Account ID 与 API Token 的逐步操作，以及 Python 检查、临时环境变量设置和 token 管理边界；列出官方注册与权限页面。 | Cloudflare, signup, Workers AI, Account ID, API Token, Read, Edit, Python, 环境变量, 凭据, 账号, 注册 | 首次注册账号前必须读取；创建或轮换 API Token 前必须读取；部署到新机器或遇到 401/403 时必须读取 | [references/01_account_and_setup.md](references/01_account_and_setup.md) |
| 02 | 给出 `generate_image.py` 命令行与 Python 导入示例、prompt/steps/输出规则、JPEG 验证、每日 Neurons 额度估算与付费边界，并按 HTTP/响应/网络/内容过滤错误列出恢复动作。 | generate_image.py, FLUX.1 schnell, REST API, base64, JPEG, --steps, --output, --overwrite, Neurons, 429, 401, 403, NSFW | 首次调用或调整 prompt/steps 前必须读取；判断免费额度与付费风险前必须读取；图片为空、格式异常或 API 失败时必须读取 | [references/02_usage_and_troubleshooting.md](references/02_usage_and_troubleshooting.md) |
