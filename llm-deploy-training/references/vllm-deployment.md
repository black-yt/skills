# Vllm Deployment

## 部署：vLLM OpenAI-compatible 服务

### 核心经验

多模态输入必须显式设置：

```bash
LIMIT_MM_PER_PROMPT='{"image": 4, "video": 0}'
```

否则 vLLM 可能默认或旧脚本限制为 `image: 0`，图片任务会报：

```text
At most 0 image(s) may be provided in one prompt.
```

Qwen3.5 工具调用使用官方推荐参数：

```bash
--enable-auto-tool-choice --tool-call-parser qwen3_coder
```

CUDA / CUDA Graph 先试两种稳定配置：

```bash
# 保守 fallback：关闭 CUDA Graph
ENFORCE_EAGER=1
```

```bash
# 推荐先试：保留 CUDA Graph，但关闭 torch.compile
ENFORCE_EAGER=0
SERVE_COMPILATION_CONFIG='{"mode": 0, "cudagraph_mode": "FULL"}'
```

实用判断：

- **先试 1 GPU。** 对 9B 级或更小模型，在可行时先验证 1 GPU + 目标上下文长度 + 多模态配置，不要一开始就降低上下文或改成多 GPU。对已知 35B 级模型，应按推荐 GPU 数启动，不要强行先试 1 GPU。
- **观察日志。** vLLM 可能把 `FULL` 自动降为 `FULL_DECODE_ONLY`，只要 graph capture 完成且服务正常，可以接受。
- **失败顺序。** 先切 `ENFORCE_EAGER=1` 或降低 batch/sequence 相关参数，再考虑降低上下文长度或增加 GPU。
- **上下文长度。** `MAX_MODEL_LEN` 和 `MAX_NUM_BATCHED_TOKENS` 通常保持一致；smoke test 可先设 `MAX_NUM_SEQS=1`。

官方参考：

- 使用前先按当前 `vllm.__version__` 选择匹配的 vLLM 文档版本。
- 查 OpenAI-compatible server、Qwen/Qwen3.5 recipe 和 compilation config 时，使用上文的版本匹配链接模板，不要写死 `stable` 或 `latest`。

### Qwen3.5 35B-A3B 部署要点

35B 级模型优先只保留一份共享权重，部署脚本通过 `MODEL_PATH` 指向这份目录，不要在不同项目或临时目录复制多份大模型权重。示例占位：

```bash
MODEL_PATH="${MODEL_ROOT}/Qwen--Qwen3.5-35B-A3B"
SERVED_MODEL_NAME="Qwen3.5-35B-A3B"
```

资源建议：

- **GPU 数。** 建议 `2` GPU 起步，并设置 `--tensor-parallel-size 2`；`1` GPU 容易 OOM。
- **上下文。** 128k 上下文对应 `--max-model-len 131072`，并让 `--max-num-batched-tokens 131072` 与其一致。
- **多模态。** 显式设置 `--limit-mm-per-prompt '{"image": 4, "video": 0}'`，避免图片输入被旧默认值禁用。
- **工具调用。** 使用 `--enable-auto-tool-choice --tool-call-parser qwen3_coder`。
- **reasoning 解析。** 使用 `--reasoning-parser qwen3` 解析 Qwen thinking/reasoning 输出。
- **CUDA Graph。** 优先试 `--compilation-config '{"mode": 0, "cudagraph_mode": "FULL"}'`；日志中如果因为 attention backend 把 `FULL` 降到 `FULL_DECODE_ONLY`，只要服务正常和 graph capture 完成，一般不需要立刻改成 eager。

35B 级 vLLM 命令骨架：

```bash
vllm serve "${MODEL_PATH}" \
  --host 0.0.0.0 \
  --port "${PORT:-8010}" \
  --served-model-name "${SERVED_MODEL_NAME:-Qwen3.5-35B-A3B}" \
  --trust-remote-code \
  --dtype auto \
  --max-model-len 131072 \
  --max-num-batched-tokens 131072 \
  --max-num-seqs 1 \
  --limit-mm-per-prompt '{"image": 4, "video": 0}' \
  --gpu-memory-utilization 0.90 \
  --tensor-parallel-size 2 \
  --reasoning-parser qwen3 \
  --compilation-config '{"mode": 0, "cudagraph_mode": "FULL"}' \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder
```

不要为了启动失败立刻把 `131072` 改成 `96000` 或直接增加更多 GPU。先确认日志中的失败原因：权重加载、profile、CUDA Graph capture、OOM、端口占用和请求侧代理污染是不同问题。

### 服务脚本模板

`scripts/serve_model.sh` 的通用结构：

```bash
#!/usr/bin/env bash
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"

if [[ -f "${PROJECT_DIR}/.env" ]]; then
  set -a
  . "${PROJECT_DIR}/.env"
  set +a
fi

MODEL_PATH="${MODEL_PATH:-/abs/path/to/model}"
CONDA_ENV_NAME="${CONDA_ENV_NAME:-}"
CONDA_ENV_DIR="${CONDA_ENV_DIR:-}"
PORT="${PORT:-8010}"
HOST="${HOST:-0.0.0.0}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-local-model}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-131072}"
MAX_NUM_BATCHED_TOKENS="${MAX_NUM_BATCHED_TOKENS:-131072}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-1}"
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
ATTENTION_BACKEND="${ATTENTION_BACKEND:-}"
ENFORCE_EAGER="${ENFORCE_EAGER:-0}"
ENABLE_AUTO_TOOL_CHOICE="${ENABLE_AUTO_TOOL_CHOICE:-1}"
TOOL_CALL_PARSER="${TOOL_CALL_PARSER:-qwen3_coder}"
REASONING_PARSER="${REASONING_PARSER:-}"
LIMIT_MM_PER_PROMPT=${LIMIT_MM_PER_PROMPT:-'{"image": 4, "video": 0}'}
SERVE_COMPILATION_CONFIG="${SERVE_COMPILATION_CONFIG:-}"

if [[ -n "${CONDA_ENV_NAME}" || -n "${CONDA_ENV_DIR}" ]]; then
  if command -v conda >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    if [[ -n "${CONDA_ENV_DIR}" ]]; then
      conda activate "${CONDA_ENV_DIR}"
    else
      conda activate "${CONDA_ENV_NAME}"
    fi
  else
    echo "[ERROR] conda requested but not found." >&2
    exit 1
  fi
fi

args=(
  vllm serve "${MODEL_PATH}"
  --host "${HOST}"
  --port "${PORT}"
  --served-model-name "${SERVED_MODEL_NAME}"
  --trust-remote-code
  --dtype auto
  --max-model-len "${MAX_MODEL_LEN}"
  --max-num-batched-tokens "${MAX_NUM_BATCHED_TOKENS}"
  --max-num-seqs "${MAX_NUM_SEQS}"
  --limit-mm-per-prompt "${LIMIT_MM_PER_PROMPT}"
  --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}"
)

[[ -n "${TENSOR_PARALLEL_SIZE}" ]] && args+=(--tensor-parallel-size "${TENSOR_PARALLEL_SIZE}")
[[ -n "${ATTENTION_BACKEND}" ]] && args+=(--attention-backend "${ATTENTION_BACKEND}")
[[ -n "${SERVE_COMPILATION_CONFIG}" ]] && args+=(--compilation-config "${SERVE_COMPILATION_CONFIG}")
[[ -n "${REASONING_PARSER}" ]] && args+=(--reasoning-parser "${REASONING_PARSER}")
[[ "${ENFORCE_EAGER}" == "1" ]] && args+=(--enforce-eager)
[[ "${ENABLE_AUTO_TOOL_CHOICE}" == "1" ]] && args+=(--enable-auto-tool-choice --tool-call-parser "${TOOL_CALL_PARSER}")

echo "[INFO] Starting vLLM on ${HOST}:${PORT}"
printf '[INFO] Command:'
printf ' %q' "${args[@]}"
printf '\n'

exec "${args[@]}"
```

### 部署验证

建议验证顺序：

- `curl http://<host>:<port>/v1/models` 能返回模型。
- 短文本 chat completion 正常。
- 工具调用能产出可解析 tool call。
- 多模态图片请求不会报 `At most 0 image(s)`。

集群内网服务测试优先使用 `httpx.Client(trust_env=False)` 或临时关闭代理，避免代理污染导致 EOF、hang、407 或误判端口不可用。

基础连通性：

```bash
BASE_URL="${BASE_URL:-http://127.0.0.1:8010/v1}"
curl -fsS "${BASE_URL}/models"
```

文本请求：

```bash
BASE_URL="${BASE_URL:-http://127.0.0.1:8010/v1}" python - <<'PY'
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("API_KEY", "EMPTY"), base_url=os.environ["BASE_URL"])
model = client.models.list().data[0].id
resp = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Answer in one sentence: what is vLLM?"}],
    max_tokens=64,
)
print(resp.choices[0].message.content)
PY
```

工具调用请求：

```bash
BASE_URL="${BASE_URL:-http://127.0.0.1:8010/v1}" python - <<'PY'
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("API_KEY", "EMPTY"), base_url=os.environ["BASE_URL"])
model = client.models.list().data[0].id
resp = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Call the weather tool for Shanghai."}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    }],
    tool_choice="auto",
)
print(resp.choices[0].message.tool_calls)
PY
```

图片请求：

```bash
BASE_URL="${BASE_URL:-http://127.0.0.1:8010/v1}" IMAGE_PATH="${IMAGE_PATH:-/abs/path/to/image.png}" python - <<'PY'
import base64
import mimetypes
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("API_KEY", "EMPTY"), base_url=os.environ["BASE_URL"])
model = client.models.list().data[0].id
image_path = os.environ["IMAGE_PATH"]
mime = mimetypes.guess_type(image_path)[0] or "image/png"
with open(image_path, "rb") as f:
    data_url = f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"
resp = client.chat.completions.create(
    model=model,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image briefly."},
            {"type": "image_url", "image_url": {"url": data_url}},
        ],
    }],
    max_tokens=128,
)
print(resp.choices[0].message.content)
PY
```

### Qwen thinking 请求侧控制

thinking 不要写死在部署脚本里。对支持 `chat_template_kwargs` 的 vLLM/Qwen 组合，推荐在请求侧通过 `extra_body` 控制：

```python
extra_body={"chat_template_kwargs": {"enable_thinking": False}}
```

不要写成顶层参数：

```python
extra_body={"enable_thinking": False}
```

顶层 `enable_thinking` 可能被 vLLM 当作未知参数忽略，导致以为关闭 thinking 但实际没有生效。

关闭 thinking 的短文本验证：

```python
from openai import OpenAI
import httpx
import os

client = OpenAI(
    api_key=os.environ.get("API_KEY", "EMPTY"),
    base_url=os.environ["BASE_URL"],
    http_client=httpx.Client(trust_env=False, timeout=120),
)

response = client.chat.completions.create(
    model=os.environ.get("MODEL_NAME", "Qwen3.5-35B-A3B"),
    messages=[{"role": "user", "content": "Reply exactly: ok"}],
    max_tokens=128,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)

print(response.choices[0].message.content)
```

打开 thinking 时要给更大的输出预算，否则可能只生成 reasoning，正文为空，或返回 `finish_reason=length`：

```python
response = client.chat.completions.create(
    model=os.environ.get("MODEL_NAME", "Qwen3.5-35B-A3B"),
    messages=[{"role": "user", "content": "Reply exactly: ok"}],
    max_tokens=1024,
    extra_body={"chat_template_kwargs": {"enable_thinking": True}},
)
```

如果业务侧需要默认关闭 thinking，优先把该策略放在请求配置或 client wrapper 中；如果需要更底层 provider 参数，用可配置的 extra body 覆盖。显式传 `{}` 应表示不自动注入 thinking 配置。

### 本地访问集群内网服务

如果 vLLM 服务部署在集群 GPU/CPU 节点上，服务可能只暴露在集群内网 `10.x.x.x`、`100.x.x.x` 或类似私网地址。本地电脑通常不能直接访问这个地址，直连 `http://<service_ip>:<port>/v1` 超时是正常现象。此时使用 SSH local port forwarding：

```text
本地电脑 127.0.0.1:<local_port>
  -> SSH 登录开发机 / 跳板机
  -> 转发到集群内网服务 <service_ip>:<service_port>
```

通用模板。在本地电脑终端执行，不是在远端开发机 shell 内执行：

```bash
ssh -N -T \
  -L <local_port>:<service_ip>:<service_port> \
  <cluster_login_user>@<cluster_login_host>
```

如果同时有 raw vLLM 和上层 OpenAI-compatible proxy / overlay 服务，可以转发多个端口：

```bash
ssh -N -T \
  -L 18010:<raw_vllm_service_ip>:8010 \
  -L 18011:<overlay_service_ip>:8011 \
  <cluster_login_user>@<cluster_login_host>
```

参数含义：

- `-L <local_port>:<service_ip>:<service_port>`：把本地 `127.0.0.1:<local_port>` 转发到集群内网服务。
- `-N`：只建立转发，不执行远端命令。
- `-T`：不分配 TTY，更适合纯转发。
- SSH 命令必须保持运行；终端关闭、网络断开或 `Ctrl-C` 后转发失效。
- 本地端口冲突时换端口，例如 `18010`、`18011`、`28010`。
- 不要把本地监听暴露成 `0.0.0.0`，除非用户明确要求并确认安全边界。

本地测试：

```bash
curl http://127.0.0.1:18010/v1/models \
  -H "Authorization: Bearer <API_KEY>"

curl http://127.0.0.1:18011/v1/models \
  -H "Authorization: Bearer <API_KEY>"
```

本地 OpenAI SDK：

```python
from openai import OpenAI

client = OpenAI(
    api_key="<API_KEY>",
    base_url="http://127.0.0.1:18010/v1",
)

model = client.models.list().data[0].id
response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "hello"}],
)
print(response.choices[0].message.content)
```

排错顺序：

1. 在开发机或集群可访问节点上先确认 `curl http://<service_ip>:<service_port>/v1/models` 可通。
2. 确认 vLLM 服务监听 `0.0.0.0`，不是只监听 `127.0.0.1`。
3. 确认 SSH 转发终端仍在运行。
4. 本地 `curl http://127.0.0.1:<local_port>/v1/models` 超时，优先检查转发是否断开、服务 IP/端口是否变化、job 是否重启。
5. 返回 `401` 时，检查是否使用了该服务 `.env` 或部署脚本中配置的 `API_KEY`。
6. rjob / worker 重启后，内网 IP 可能变化；重新从服务日志读取 `SERVICE_IP`、`[INFO] ip=`、`SOCKET_IP` 或 `MASTER_ADDR`，再更新 `ssh -L`。

128k、多模态和 CUDA Graph capture 的首轮启动可能需要几分钟。先看日志是否还在加载权重、profile 或 capture，不要只因为 `/v1/models` 尚未返回就立刻判断失败。

常见问题：

- **图片输入被拒绝。** 检查 `--limit-mm-per-prompt` 是否为 JSON 字符串，且 `image` 数量大于 0。
- **工具调用不解析。** 检查是否启用 `--enable-auto-tool-choice --tool-call-parser qwen3_coder`。
- **CUDA Graph 失败。** 先试 `ENFORCE_EAGER=1`；若想保留 graph，试 `SERVE_COMPILATION_CONFIG='{"mode": 0, "cudagraph_mode": "FULL"}'`。
- **OOM。** 先降 `MAX_NUM_SEQS`、`MAX_NUM_BATCHED_TOKENS` 或 `GPU_MEMORY_UTILIZATION`，再考虑降低 `MAX_MODEL_LEN` 或增加 GPU。
- **本地不能访问集群内网服务。** 使用 SSH local port forwarding，把本地 `127.0.0.1:<local_port>` 转发到集群内网 `<service_ip>:<service_port>`。
