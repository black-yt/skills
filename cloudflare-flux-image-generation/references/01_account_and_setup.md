# 注册与配置

核对日期：2026-10-23。Cloudflare 控制台布局和价格会变化，以[官方 REST API 入门](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)和[价格页](https://developers.cloudflare.com/workers-ai/platform/pricing/)的当前内容为准。

## 1. 注册账号

1. 打开 [Cloudflare 注册页](https://dash.cloudflare.com/sign-up)，按页面指引用邮箱创建账号并完成验证；已有账号则直接登录。
2. 进入 [Workers AI 控制台](https://dash.cloudflare.com/?to=/:account/ai/workers-ai)。如果直达链接随界面变化，从控制台菜单进入 **Workers AI**。
3. 选择 **Use REST API**。这个页面同时提供创建 token 和复制 Account ID 的入口。无需先部署 Worker。

## 2. 取得 Account ID 和 API Token

1. 在 **Use REST API** 页选择 **Create a Workers AI API Token**，检查模板预填的账号和权限，再选 **Create API Token**。
2. 复制 API Token；回到 **Get Account ID** 复制 Account ID。Account ID 是账号标识，不是 Zone ID、域名或 token。
3. 如需自己创建自定义 token，当前官方入门文档要求同时具备 **Workers AI - Read** 和 **Workers AI - Edit** 权限，并将资源限制在目标账号。不要照搬旧项目只设 Read 的步骤。
4. 把 token 保存在密码管理器或受控的私有配置中。不要提交到 Git、贴入聊天、写入脚本或 `~/.bashrc`。Token 遗失或泄露时到 Cloudflare 仪表盘撤销并重建。

## 3. 安装与临时注入

脚本只用 Python 3.10+ 标准库。WSL/Linux/macOS 检查 `python3 --version`；Windows 可用 `py -3 --version`，调用时把 `python3` 换成 `py -3`。缺 Python 时从操作系统包管理器或 [Python 官方下载页](https://www.python.org/downloads/)安装；不需要 `pip install`。

```bash
python3 --version
export CLOUDFLARE_ACCOUNT_ID='[ACCOUNT_ID]'
read -r -s -p 'Cloudflare Workers AI token: ' CLOUDFLARE_API_TOKEN; printf '\n'
export CLOUDFLARE_API_TOKEN
python3 /path/to/cloudflare-flux-image-generation/scripts/generate_image.py --help
```

以上命令只作用于当前 shell 和它启动的子进程；`[ACCOUNT_ID]` 请替换为自己的值。为自动化任务注入凭据时使用密钥管理器或受限环境文件，确保文件不在 Git 仓库内且仅本人可读。脚本不加载 `.env`，也不要求修改 shell 启动文件。运行结束后可 `unset CLOUDFLARE_API_TOKEN`。

## 4. 权限与费用检查

- 在 Workers AI 控制台确认已选择正确账号，并观察 Neurons 用量。
- 免费分配量当前为每天 10,000 Neurons，UTC 00:00 重置；Workers Free 用尽后请求报错。Workers Paid 超出免费分配量的用量按当前价格计费。升级或批量生成前重新看[官方价格页](https://developers.cloudflare.com/workers-ai/platform/pricing/)。
- 注册是否要求额外验证、具体可用模型和配额由 Cloudflare 当前页面与账号状态决定，不以历史经验保证。
