# Api Server And Protocol

## OpenAI-Compatible API Server

ResearchHarness 可部署为同步 `/v1/chat/completions` 服务。调用方只需把 OpenAI SDK 的 `base_url` 指向 ResearchHarness。

默认透明 agent 服务：

```bash
rh-server \
  --api-runs-dir ./api_runs \
  --host 127.0.0.1 \
  --port 8686
```

源码入口等价：

```bash
python3 run_server.py \
  --api-runs-dir ./api_runs \
  --host 127.0.0.1 \
  --port 8686
```

QA/VQA strict-format benchmark 模式：

```bash
python3 run_server.py \
  --api-runs-dir ./api_runs \
  --host 127.0.0.1 \
  --port 8686 \
  --role-prompt-file benchmarks/QA/role_prompt.md \
  --input-wrapper \
  --output-wrapper
```

API server 常用参数：

| 参数 | 必需 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `--api-runs-dir PATH` | 是 | 无 | 每个请求的 run 父目录。 |
| `--host HOST` | 否 | `127.0.0.1` | 服务监听 host。 |
| `--port PORT` | 否 | `8686` | 服务监听端口。 |
| `--role-prompt-file PATH` | 否，可重复 | 无 | 追加 role prompt。 |
| `--input-wrapper` / `--no-input-wrapper` | 否 | 关闭 | 输入 LLM wrapper。 |
| `--output-wrapper` / `--no-output-wrapper` | 否 | 关闭 | 输出 LLM wrapper。 |
| `--max-concurrent-runs N` | 否 | `32` | server 侧同时执行的 agent run 数。 |
| `--tool NAME` | 否，可重复 | 无 | 完整工具全集；不能和 `--extra-tool` 同用。 |
| `--extra-tool NAME` | 否，可重复 | 无 | 启用 optional compatibility tool。 |

并发注意：

- endpoint 对客户端仍是同步一问一答。
- 长 agent run 在 server-side thread pool 中执行，不阻塞 FastAPI event loop。
- 大 batch 可根据 CPU、内存、磁盘、网络和后端 API quota 调整 `--max-concurrent-runs`。

Wrapper 模式：

- 默认不启用 wrapper，server 作为透明 ResearchHarness agent 服务。
- `--input-wrapper` 会先把 OpenAI-compatible messages 整理成 agent instruction、output contract 和 wrapper notes。
- `--output-wrapper` 会把 agent result 格式化为用户要求的最终输出格式。
- QA/VQA 或严格 benchmark 格式可启用 input/output wrapper。
- 普通研究、代码、文件处理和报告任务通常先用无 wrapper 模式，避免多一层 LLM 改写。
- wrapper 不应该引入 agent result 中没有的事实；如果信息不足，应输出 contract-compliant failure answer。

## API 调用协议

文本请求：

```python
from openai import OpenAI

client = OpenAI(api_key="unused", base_url="http://127.0.0.1:8686/v1")

response = client.chat.completions.create(
    model="RH",
    messages=[{"role": "user", "content": "Answer in one sentence: what is 2 + 2?"}],
)

print(response.choices[0].message.content)
```

模型选择：

- `model="RH"` 或不传 `model`：使用 `.env` / env 中 `MODEL_NAME`。
- `model="RH--<llm-model-name>"`：单个请求覆盖底层模型，例如 `RH--gpt-5.5`。
- 裸模型名如 `gpt-5.5` 会被拒绝。
- 覆盖只影响当前请求，不修改环境变量，也不影响其他并发请求。

provider-specific model 选项：

```python
from openai import OpenAI

client = OpenAI(api_key="unused", base_url="http://127.0.0.1:8686/v1")

response = client.chat.completions.create(
    model="RH--Qwen/Qwen3.5-9B",
    messages=[{"role": "user", "content": "Answer briefly."}],
    extra_body={"llm-extra-body": {"enable_thinking": False}},
)
```

`llm-extra-body` 要求：

- 必须是 JSON object。
- 只影响当前 API 请求，不修改 server 默认值，也不影响其他并发请求。
- 会被原样转发为底层 OpenAI SDK request 的 `extra_body`。
- ResearchHarness 不解释 provider-specific key；字段是否有效由上游 provider 决定。
- thinking / reasoning 模式通常会占用更多 completion token，必要时同步调高 `MAX_OUTPUT_TOKENS` 或请求的 `max_completion_tokens`。

自定义 workspace：

```python
from pathlib import Path
from openai import OpenAI

workspace = Path("./workspace/api_custom_workspace").resolve()
workspace.mkdir(parents=True, exist_ok=True)

client = OpenAI(api_key="unused", base_url="http://127.0.0.1:8686/v1")

response = client.chat.completions.create(
    model="RH",
    messages=[{"role": "user", "content": "Inspect this workspace and write summary.md."}],
    extra_body={"workspace-root": str(workspace)},
)
```

`workspace-root` 要求：

- 必须是字段名 `workspace-root`，不是 `workspace_root`。
- 只有已存在的绝对目录会被使用。
- 缺失、相对路径或不存在目录会回退到 per-request `agent_workspace/`。
- 即使用自定义 workspace，trace 仍写到 `--api-runs-dir/run_.../agent_trace/`。

多模态请求：

- 支持 `data:image/...;base64,...` image URL。
- 不支持远程图片 URL 下载。
- 不支持请求中直接传本地图片路径。
- 每张图片保存到 workspace 的 `inputs/images/`，并把保存后的相对路径写进 agent 可见文本。

协议边界：

- 当前 API 是 conversation-level stateless；每个 HTTP request 是一次隔离 run。
- 需要多轮 API 对话时，客户端自己管理历史并传入 messages。
- `extra_body["workspace-root"]` 和 `extra_body["llm-extra-body"]` 都是 request-local 控制字段。
- `workspace-root` 用于选择 agent workspace；`llm-extra-body` 才会转发给底层模型。
- `stream` 必须不存在或为 `false`。
- `n` 必须不存在或为 `1`。
- 支持 `system`、`user`、`assistant` role；不支持 `tool` role。
- `response_format` 会作为输出格式提示传给 wrapper。

Health check：

```bash
curl http://127.0.0.1:8686/v1/health
```

health 返回包含：

```json
{
  "status": "ok",
  "api_runs_dir": "./api_runs",
  "input_wrapper": false,
  "output_wrapper": false,
  "max_concurrent_runs": 32,
  "extra_tools": []
}
```

标准返回结构：

```json
{
  "id": "chatcmpl_...",
  "object": "chat.completion",
  "created": 1770000000,
  "model": "RH",
  "choices": [
    {
      "index": 0,
      "message": {"role": "assistant", "content": "final answer"},
      "finish_reason": "stop"
    }
  ]
}
```

API 请求校验要点：

- request body 必须是 JSON object。
- `messages` 必须是非空 list。
- `role` 只支持 `system`、`user`、`assistant`。
- content 支持 string，或包含 `text` / `image_url` 的 content parts。
- image MIME 只支持常见 `image/png`、`image/jpeg`、`image/webp`、`image/gif`。
- 单张 API 输入图片大小上限通常是 25 MB。
- `stream=true` 会被拒绝。
- `n != 1` 会被拒绝。
- `model` 必须是 `RH`、`researchharness` 或 `RH--<backend-model>`。
- API response 是 OpenAI-compatible 形状，但目前不含 token usage 统计。
