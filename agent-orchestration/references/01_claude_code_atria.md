# Claude Code 与 Atria-Dawn

## 使用边界

- 先确认目标环境已有 `claude`，读取 `claude --version`、`claude --help`。以下参数骨架在 Claude Code 2.1.296 的本机 help 中存在；升级后重新核对，不能假设永远兼容。
- Atria-Dawn 按用户提供的接入约束只处理文本、上下文上限 512k；不传图片、截图、PDF 图像或视觉工具结果。视觉任务由其他可读图工具处理，传给 Atria 的只应是必要文字观察。
- 申请入口：[InternAI Discovery Token Plan](https://discovery.intern-ai.org.cn/token-plan/home?tabIndex=0)。示例 endpoint 为 `https://discovery-api.intern-ai.org.cn`；模型名为 `Atria-Dawn`。服务可用性、价格和限制以申请页与实际响应为准。
- 外部调用是 Claude Code 工具与会话能力，不是单次问答。任务提示应说明目标、可见输入、可写输出、禁区、完成证据与何时交接。

## 临时凭据与文本探针

把 JSON 凭据保存在仓库外的 `[PRIVATE_CONFIG_JSON]`，限制为仅当前用户可读写；不要把真实 token 放进 prompt、命令行、Git、调试日志或最终回复。文件示意：

```json
{
  "ANTHROPIC_BASE_URL": "https://discovery-api.intern-ai.org.cn",
  "ANTHROPIC_AUTH_TOKEN": "[API_KEY]",
  "ANTHROPIC_MODEL": "Atria-Dawn"
}
```

下面的 Python 片段只把配置注入 Claude 子进程。探针禁用工具，返回内容只用于核实该后端确实工作；不要打印环境、原始错误响应或认证头。

```python
import json
import os
import stat
import subprocess
from pathlib import Path

raw_cfg = Path("[PRIVATE_CONFIG_JSON]").expanduser()
assert not raw_cfg.is_symlink()
cfg = raw_cfg.resolve(strict=True)
assert cfg.is_file()
assert stat.S_IMODE(cfg.stat().st_mode) & 0o077 == 0
settings = json.loads(cfg.read_text(encoding="utf-8"))
required = {"ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_MODEL"}
assert required <= settings.keys()
env = os.environ.copy()
for name in ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN",
             "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL"):
    env.pop(name, None)
env.update({name: settings[name] for name in required})
env["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = "1"
result = subprocess.run(
    ["claude", "-p", "--model", env["ANTHROPIC_MODEL"],
     "--setting-sources", "", "--strict-mcp-config",
     "--mcp-config", '{"mcpServers":{}}',
     "--settings", '{"disableAllHooks":true}',
     "--no-chrome", "--disable-slash-commands",
     "--tools", "", "--output-format", "json",
     "Return exactly EXTERNAL_AGENT_OK. Text only. Do not call tools."],
    env=env, text=True, capture_output=True, timeout=150,
)
if result.returncode != 0:
    raise RuntimeError(f"Claude text probe failed (exit {result.returncode})")
response = json.loads(result.stdout)
assert not response.get("is_error")
assert response["result"].strip() == "EXTERNAL_AGENT_OK"
print("Claude text probe passed")
```

避免继承其他 API key 或 OAuth token 抢占后端；只清理子进程环境，不删除父环境或旧凭据。`--bare` 在已查看的 help 中采用不同认证路径，不能机械替换上述调用。不改 `~/.bashrc`、`~/.profile`、个人 Claude 登录或全局设置。

## 从探针到实际任务

1. 先验证指定小文本的读取，再验证仅向自己的候选目录写入一个小文件。真实任务去掉 `--tools ""`，按需要用 `--tools` 指定 `Read,Write,Edit,Bash` 中的最小集合，并用 `--allowedTools` 限定具体操作；不要默认跳过全部权限校验。
2. 非交互任务使用 `-p`，交互任务可使用 `claude`。保存 CLI 返回的 session ID；续接时明确 `--resume <session-id>`，并保持 cwd、配置与任务范围一致，不用 `--continue` 猜最近会话。
3. 可用版本若支持 `--background`，按该版本 help 启动和管理。需要长期目标时，使用持久化监督循环与会话续接；不要杜撰 `--goal` 等未核实开关。
4. 记录启动/结束时间、退出码、允许的工具和输出路径。暂时故障有限退避；持续认证或网络故障先核实连接，不切换原管线的 provider 或已有 session。

工具验证必须真实发生；纯文本探针成功不能证明 Read/Write、持续会话、资源隔离或生产管线均已通过。
