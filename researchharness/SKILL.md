---
name: researchharness
description: Use when installing, configuring, running, embedding, deploying, or debugging InternScience ResearchHarness as a lightweight tool-using LLM agent runtime, including CLI runs, local frontend UI, OpenAI-compatible API server, Python API, tool selection, workspaces, traces, compaction, tests, and read-only source inspection.
---

# ResearchHarness

## 使用边界

- ResearchHarness 是轻量、可审计的 tool-using LLM agent harness。
- 适合本地 agent 工作、benchmark 公平执行底座、OpenAI-compatible agent API 后端、代码/文件/PDF/图片/网页任务。
- 它是 base harness，不是大型 workflow platform、多租户服务或完整产品平台。
- 不要擅自安装依赖、升级共享环境、修改长期配置或暴露公网服务；需要时先征得用户同意。
- API server 默认没有用户认证；公开暴露前必须加外层认证、访问控制或只绑定可信内网。
- trace/session state 不要放进 agent 可见 workspace，避免 agent 读取自己的执行记录。
- 推荐通过源码阅读确认复杂行为、参数默认值、工具 schema 和 API contract，不要只凭经验猜测。
- 源码只读：只用于阅读和定位问题，不要改源码，不要直接修改 `site-packages`、editable checkout 或共享环境。

## 安装与源码

- PyPI 安装：`pip install researchharness`
- GitHub 源码：https://github.com/InternScience/ResearchHarness
- 在线体验：https://huggingface.co/spaces/InternScience/ResearchHarness
- Python 版本：Python 3.10+

PyPI 安装模板：

```bash
conda create -n rh-env python=3.11
conda activate rh-env
pip install researchharness
```

源码开发模板：

```bash
conda create -n rh-env python=3.11
conda activate rh-env
git clone https://github.com/InternScience/ResearchHarness.git
cd ResearchHarness
pip install -r requirements.txt
pip install -e . --no-deps
```

PyPI 安装后可用 console entrypoints：

```bash
rh-agent
rh-server
rh-frontend
```

源码 checkout 中也可用：

```bash
python3 run_agent.py
python3 run_server.py
python3 run_frontend.py
```

## 项目结构

第一次读源码时，按下面路径定位：

- `run_agent.py`：直接运行 agent 的薄 CLI 入口。
- `run_frontend.py`：本地浏览器 UI 启动入口。
- `run_server.py`：OpenAI-compatible API server 入口。
- `api/openai_server.py`：`/v1/chat/completions`、wrapper、per-request run 目录、health check。
- `frontend/`：WebSocket UI、静态资源、浏览器侧 AskUser bridge。
- `agent_base/react_agent.py`：主 ReAct loop、模型调用、tool-call 处理、trace/session state。
- `agent_base/base.py`：可扩展 base agent hooks 和 benchmark adapter 基础。
- `agent_base/prompt.py`：base system prompt 组合。
- `agent_base/trace_utils.py`：flat JSONL trace writer。
- `agent_base/console_utils.py`：CLI event 输出。
- `agent_base/tools/tool_file.py`：`Glob`、`Grep`、`Read`、`ReadPDF`、`ReadImage`、`Write`、`Edit`。
- `agent_base/tools/tool_runtime.py`：`Bash` 和 persistent terminal tools。
- `agent_base/tools/tool_web.py`：`WebSearch`、`ScholarSearch`、`WebFetch`。
- `agent_base/tools/tool_user.py`：`AskUser`。
- `agent_base/tools/tool_extra.py`：optional compatibility tools，例如 `str_replace_editor`。
- `agent_base/tools/custom.py`：Python function tools 适配。
- `benchmarks/`：benchmark-specific role prompts、README 和 adapter，不能塞进 `agent_base/`。
- `workspace/`：默认 CLI workspace root。
- `api_runs/`：默认 API server run root。
- `traces/`：默认 CLI trace 输出 root。

运行产物目录通常只追踪 `.gitkeep`；运行生成的文件应被 git 忽略。

## 运行模式速查

| 模式 | 入口 | 适合场景 | 关键目录 |
| --- | --- | --- | --- |
| CLI one-shot / chat | `rh-agent` 或 `python3 run_agent.py` | 本地一次性任务、交互式 follow-up、benchmark CLI adapter | `--workspace-root`，可选 `--trace-dir` |
| 本地前端 | `rh-frontend` 或 `python3 run_frontend.py` | 浏览器交互、图片附件、AskUser、实时查看工具步骤 | 浏览器选择 workspace，可选 `--trace-dir` |
| API server | `rh-server` 或 `python3 run_server.py` | OpenAI SDK 客户端、benchmark batch、自动化服务 | `--api-runs-dir/run_.../{agent_workspace,agent_trace}` |
| Python API | `create_agent` / `run_agent` | 嵌入其他 Python 程序、自定义工具、程序化参数 | `workspace_root`，可选 trace/runtime 参数 |
| Benchmark adapter | `benchmarks/*` | ResearchClawBench、QA/VQA、SGI 系列 benchmark | benchmark 目录下 role prompt / adapter |

## 执行生命周期

一次标准 run 的顺序：

1. 读取 `.env`、进程环境变量和显式参数。
2. 校验 `API_KEY`、`API_BASE`、`MODEL_NAME` 等必需变量。
3. 解析 workspace，必要时创建目录。
4. 组合 system prompt：base prompt + role prompt files + role prompt string。
5. 解析工具 surface：默认工具、`--tool` 完整工具集或 `--extra-tool` 追加工具。
6. 如果有初始图片，将图片复制/保存到 `inputs/images/`，并在 prompt 中加入本地相对路径提示。
7. 调用 OpenAI-compatible chat-completions，并带 native tool schemas。
8. 如果 assistant 返回 tool calls，按并发规则执行工具，把结果写回 messages 和 trace。
9. 如果 `ReadImage` 产生图像上下文，在下一轮把压缩图片作为 `image_url` content part 传给模型。
10. 如果 assistant 返回可接受的普通文本，作为 final result 结束。
11. 如果达到 round、LLM call、runtime、timeout 或 protocol error 边界，写入 termination/error。
12. 如果启用了 trace/session state，落盘 `trace_*.jsonl` 和 `session_state_*.json`。

执行边界：

- CLI interactive 模式会保留 `prior_messages`，final answer 后可继续 follow-up。
- API server 模式每个 HTTP request 是隔离 run，不自动继承上一请求的上下文。
- benchmark adapter 可以通过 subclass 增加 stop condition、禁用工具或改 final 接受条件。
- older image bytes 会在后续请求中被文本引用替代，避免每轮重复发送大图片；需要细节时让 agent 对保存路径调用 `ReadImage`。
- assistant tool-call turn 如果因输出长度被截断，runtime 会提示模型用更小的 tool call 重新发出，未执行被截断的 tool call。

## 运行目录布局

CLI / frontend 推荐布局：

```text
[PROJECT_ROOT]/
├── workspace/                 # agent 可见，本地文件工具和 shell 工作目录
│   └── inputs/
│       └── images/            # 初始图片或前端上传图片
└── traces/                    # agent 不可见，显式传 --trace-dir 后生成
    ├── trace_*.jsonl
    └── session_state_*.json
```

API server 默认每个请求一个独立 run：

```text
api_runs/
└── run_YYYYMMDD_HHMMSS_<random>/
    ├── agent_workspace/       # 未传 workspace-root 时的 agent workspace
    │   └── inputs/
    │       └── images/        # API data:image 输入保存位置
    ├── agent_trace/           # agent trace 和 session state
    │   ├── trace_*.jsonl
    │   └── session_state_*.json
    └── api_trace.jsonl        # API 请求/响应和 wrapper 事件
```

自定义 API workspace 时：

- `agent_workspace/` 可被 `extra_body={"workspace-root": "/abs/existing/workspace"}` 替代。
- 自定义 workspace 必须是已经存在的绝对目录。
- trace 仍写在 `api_runs/run_.../agent_trace/`，不要写进自定义 workspace。
- API 输入图片会写入该 workspace 的 `inputs/images/`。

## 源码追溯

- 行为不确定时，推荐优先定位当前安装版本源码，而不是猜测。
- `researchharness.__file__` 可定位 public import surface。
- `inspect.getsource(...)` 可查看 `create_agent`、`run_agent`、工具类和 server app 入口。
- 源码阅读必须保持只读；不要修改 `site-packages`、pip 安装目录、共享 checkout 或长期环境。
- 如果确实需要改库，先向用户说明风险和改动范围；只有用户确认后，才 clone 独立副本并使用 editable install。

```bash
python - <<'PY'
import inspect
import researchharness
from researchharness import Bash, Read, create_agent, run_agent

print("researchharness:", researchharness.__version__, researchharness.__file__)
print(inspect.getsource(create_agent))
print(inspect.getsource(run_agent))
print(inspect.getsource(Read))
print(inspect.getsource(Bash))
PY
```

定位 runtime / server 关键模块：

```bash
python - <<'PY'
import inspect
import researchharness.runtime as runtime
import agent_base.react_agent as react_agent
import api.openai_server as openai_server

print("runtime:", runtime.__file__)
print("react_agent:", react_agent.__file__)
print("openai_server:", openai_server.__file__)
print(inspect.getsource(runtime.create_agent))
PY
```

## 环境变量

必需变量：

```env
API_KEY="[OPENAI_COMPATIBLE_API_KEY]"
API_BASE="[OPENAI_COMPATIBLE_BASE_URL]/v1"
MODEL_NAME="[MODEL_ID]"
SERPER_KEY="[SERPER_KEY]"
JINA_KEY="[JINA_KEY]"
MINERU_TOKEN="[MINERU_TOKEN]"
```

变量用途：

- `API_KEY` / `API_BASE` / `MODEL_NAME`：OpenAI-compatible chat-completions 模型服务。
- `SERPER_KEY`：`WebSearch`、`ScholarSearch`。
- `JINA_KEY`：`WebFetch`。
- `MINERU_TOKEN`：`ReadPDF`，依赖 MinerU 和 `structai`。

常用可选变量：

- `WORKSPACE_ROOT`
- `MAX_LLM_CALL_PER_RUN`
- `MAX_AGENT_ROUNDS`
- `MAX_AGENT_RUNTIME_SECONDS`
- `LLM_TIMEOUT_SECONDS`
- `WEBFETCH_TIMEOUT_SECONDS`
- `WEBFETCH_MAX_CHARS`
- `LLM_MAX_OUTPUT_TOKENS`
- `MAX_INPUT_TOKENS`
- `LLM_MAX_RETRIES`
- `TEMPERATURE`
- `TOP_P`
- `PRESENCE_PENALTY`
- `AUTO_COMPACT_TRIGGER_TOKENS`
- `IMAGE_PART_TOKEN_ESTIMATE`
- `LLM_IMAGE_MAX_EDGE`
- `LLM_IMAGE_MAX_BYTES`
- `LLM_IMAGE_JPEG_QUALITY`
- `DEBUG_AGENT`
- `DEBUG_SEARCH`
- `DEBUG_SCHOLAR`
- `DEBUG_VISIT`

常用默认值：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `WORKSPACE_ROOT` | `./workspace` | 未显式传 workspace 时使用。 |
| `MAX_LLM_CALL_PER_RUN` | `100` | 单次 run 最大 LLM 调用数。 |
| `MAX_AGENT_ROUNDS` | `100` | ReAct loop 最大轮次。 |
| `MAX_AGENT_RUNTIME_SECONDS` | `9000` | 单次 run 最大秒数。 |
| `LLM_TIMEOUT_SECONDS` | `600` | 单次 LLM 请求 timeout。 |
| `WEBFETCH_TIMEOUT_SECONDS` | `180` | 单次 WebFetch 总 timeout。 |
| `WEBFETCH_MAX_CHARS` | `30000` | 单次 WebFetch 返回字符上限。 |
| `LLM_MAX_OUTPUT_TOKENS` | `10000` | 请求模型输出 token 上限。 |
| `MAX_INPUT_TOKENS` | `320000` | runtime token accounting 输入预算。 |
| `LLM_MAX_RETRIES` | `10` | LLM API 瞬时错误最大重试次数。 |
| `TEMPERATURE` | `0.6` | 主模型 temperature。 |
| `TOP_P` | `0.95` | 主模型 top-p。 |
| `PRESENCE_PENALTY` | `1.1` | provider 支持时使用。 |
| `AUTO_COMPACT_TRIGGER_TOKENS` | `128k` | 自动上下文压缩触发阈值。 |
| `IMAGE_PART_TOKEN_ESTIMATE` | `1536` | 每个 image content part 的 token 估计。 |
| `LLM_IMAGE_MAX_EDGE` | `1568` | 发送给多模态模型的图片最大边长。 |
| `LLM_IMAGE_MAX_BYTES` | `524288` | 发送给多模态模型的压缩图片最大字节数。 |
| `LLM_IMAGE_JPEG_QUALITY` | `85` | 图片压缩初始 JPEG 质量。 |

配置优先级：

```text
explicit Python/API/CLI arguments > process environment variables > .env > code defaults
```

正式使用前运行工具可用性检查：

```bash
python3 tests/test_tool_availability.py
```

如果 `WebSearch`、`ScholarSearch`、`WebFetch` 或 `ReadPDF` 出现 network、TLS、upload、download、PDF parsing 错误，优先尝试关闭 VPN/proxy 后重试。

## CLI 运行

基本运行：

```bash
rh-agent "Who proposed the transformer architecture, and in what year was the paper published?"
```

源码入口等价：

```bash
python3 run_agent.py "Who proposed the transformer architecture, and in what year was the paper published?"
```

指定 workspace：

```bash
rh-agent "Summarize this project." --workspace-root ./workspace
```

保存 trace：

```bash
rh-agent "Summarize this project." \
  --workspace-root ./workspace \
  --trace-dir ./traces
```

追加 role prompt：

```bash
rh-agent "Answer this QA task." \
  --workspace-root ./workspace \
  --role-prompt-file benchmarks/QA/role_prompt.md
```

附加本地图片：

```bash
rh-agent "Read the image and return JSON." \
  --workspace-root ./workspace \
  --images /path/to/image-1.png /path/to/image-2.png
```

常用 CLI 参数：

| 参数 | 必需 | 说明 |
| --- | --- | --- |
| `prompt` | 是，除非用 `--prompt-file` | prompt 文本，可由多个位置参数拼接。 |
| `--prompt-file PATH` | 否 | 从 UTF-8 文件读取 prompt。 |
| `--workspace-root PATH` | 否 | agent 可见 workspace；不存在会创建。 |
| `--trace-dir PATH` | 否 | 写 `trace_*.jsonl` 和 `session_state_*.json`；不要指向 workspace。 |
| `--role-prompt-file PATH` | 否，可重复 | 追加 role-specific prompt 到 base prompt。 |
| `--images PATH [PATH ...]` | 否 | 复制图片到 `workspace/inputs/images/` 并作为初始 `image_url` 输入。 |
| `--chat` | 否 | 强制开启 follow-up 模式。 |
| `--no-chat` | 否 | 强制一问一答，适合脚本或 benchmark。 |
| `--tool NAME` | 否，可重复 | 定义完整工具全集；不能和 `--extra-tool` 同用。 |
| `--extra-tool NAME` | 否，可重复 | 启用 optional compatibility tool，例如 `str_replace_editor`。 |

交互式终端中，CLI 默认在 final answer 后等待 follow-up，并保留消息、工具结果和图片路径提示。脚本或 benchmark 需要一问一答时使用 `--no-chat`。

## Python API

嵌入式使用：

```python
from researchharness import Bash, Read, Write, create_agent, tool

@tool
def add_numbers(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

agent = create_agent(
    workspace_root="./workspace",
    role_prompt="Answer carefully from evidence.",
    role_prompt_files=["./benchmarks/QA/role_prompt.md"],
    tools=[Read, Write, Bash, add_numbers],
    max_input_tokens=131072,
    max_output_tokens=4096,
    compact_trigger_tokens="96k",
)

answer = agent.run(
    "Inspect the workspace and write a short summary.",
    images=["/abs/path/to/image-1.png"],
)
```

一次性调用：

```python
from researchharness import run_agent

answer = run_agent(
    "Summarize this project.",
    workspace_root="./workspace",
    role_prompt="Be concise.",
    images=["/abs/path/to/image-1.png"],
)
```

工具边界：

- `tools=None`：使用默认 ResearchHarness 工具集。
- `tools=[...]`：完整暴露工具全集；未列出的默认工具会被移除。
- Python 中优先传 `Read`、`Bash` 等内置工具类或 `@researchharness.tool` 函数，不要优先传字符串。
- `extra_tools=[...]`：在默认工具集上追加 optional compatibility tools。
- `tools` 和 `extra_tools` 不能同时传。
- 自定义 tool function 必须有唯一合法名称、docstring 或 description、JSON-compatible 参数类型，不能有 `*args`、`**kwargs` 或 positional-only 参数。

schema 检查：

```python
from researchharness import Bash, Read, available_tool_schemas, tool

@tool
def add_numbers(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

schemas = available_tool_schemas([Read, Bash, add_numbers])
print([schema["function"]["name"] for schema in schemas])
```

## 本地前端 UI

启动：

```bash
rh-frontend
```

源码入口：

```bash
python3 run_frontend.py
```

指定端口并不自动打开浏览器：

```bash
python3 run_frontend.py --port 8766 --no-browser
```

前端模式也支持常用 agent 选项：

```bash
python3 run_frontend.py \
  --trace-dir ./traces \
  --role-prompt-file benchmarks/QA/role_prompt.md
```

前端参数：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--host` | `127.0.0.1` | 绑定 host。 |
| `--port` | `8765` | 绑定端口。 |
| `--no-browser` | 关闭 | 不自动打开浏览器。 |
| `--trace-dir PATH` | 无 | 写 frontend agent traces；不要指向 workspace。 |
| `--role-prompt-file PATH` | 无，可重复 | 追加 role prompt。 |
| `--extra-tool NAME` | 无，可重复 | 启用 optional compatibility tool。 |

前端特性：

- 默认绑定 `127.0.0.1:8765`。
- 在浏览器中选择已有 workspace；支持 Unicode 路径和手动粘贴路径。
- WebSocket 实时展示 assistant rounds、tool calls、tool results。
- 支持图片附件：文件选择、拖拽、粘贴。
- 图片保存到 workspace 的 `inputs/images/`，并把相对路径写进 agent 可见文本。
- `AskUser` 可通过同一个 chat input 回复。
- final answer 后继续输入会延续当前对话；点击 `New chat` 才清空。
- 运行中 `Stop` 是 cooperative stop，保留上下文直到安全点。
- 模型下拉只影响当前/下一次 run，不修改 `.env`。

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

## 工具 Surface

默认工具：

- `Glob`
- `Grep`
- `Read`
- `ReadPDF`
- `ReadImage`
- `Write`
- `Edit`
- `Bash`
- `WebSearch`
- `ScholarSearch`
- `WebFetch`
- `AskUser`
- `TerminalStart`
- `TerminalWrite`
- `TerminalRead`
- `TerminalInterrupt`
- `TerminalKill`

Optional extra tool：

- `str_replace_editor`

工具参数矩阵：

| 工具 | 参数 | 返回 / 说明 |
| --- | --- | --- |
| `Glob` | `pattern`, `path?`, `include_dirs?`, `max_results?` | 返回 `root`、`match_count`、`truncated`、`results`；用于路径发现。 |
| `Grep` | `pattern`, `path?`, `glob?`, `case_sensitive?`, `max_results?`, `max_chars?` | 返回匹配文件、行号、行文本；跳过明显二进制、图片、PDF。 |
| `Read` | `path`, `start_line?`, `end_line?`, `max_chars?` | 读取文本文件；PDF/image 会提示转用 `ReadPDF` / `ReadImage`。 |
| `ReadPDF` | `path`, `max_chars?`, `max_image_paths?` | 依赖 `structai` 和 `MINERU_TOKEN`；返回文本、`image_paths`、图片计数和截断信息。 |
| `ReadImage` | `path` | 返回图片 metadata；运行时将压缩图像作为 `image_url` content part 发给模型。 |
| `Write` | `path`, `content`, `overwrite?` | 创建文本文件；`overwrite=false` 时拒绝覆盖已有文件。 |
| `Edit` | `path`, `patch` | 应用 unified-diff / hunk-style patch；基于上下文匹配，不是完整 `patch(1)`。 |
| `Bash` | `command`, `timeout?`, `workdir?` | 一次性 shell 命令；返回 `stdout` / `stderr`；适合确定性本地处理。 |
| `WebSearch` | `query` | Serper general search；单次一个 query。 |
| `ScholarSearch` | `query` | Serper Scholar；返回论文标题、年份、摘要、citation 等。 |
| `WebFetch` | `url`, `start_line?`, `end_line?`, `max_chars?` | Jina Reader；返回清洗后的网页文本和行/字符截断 metadata。 |
| `AskUser` | `question`, `context?` | 交互式向用户提问；无交互终端时返回 unavailable；benchmark 可禁用。 |
| `TerminalStart` | `cwd?`, `shell?`, `rows?`, `cols?` | 启动持久 terminal，返回 `session_id`、`pid`、`cwd`、`alive` 等。 |
| `TerminalWrite` | `session_id`, `input`, `append_newline?`, `yield_time_ms?`, `max_output_chars?` | 向 terminal 写入输入并读增量输出。 |
| `TerminalRead` | `session_id`, `yield_time_ms?`, `max_output_chars?` | 读取 terminal 未读输出。 |
| `TerminalInterrupt` | `session_id`, `max_output_chars?` | 发送 `Ctrl-C`，保留 session。 |
| `TerminalKill` | `session_id`, `force?` | 终止 session 并释放资源。 |
| `str_replace_editor` | `command`, `path`, `file_text?`, `old_str?`, `new_str?`, `insert_line?`, `view_range?` | optional compatibility editor；默认不加载。 |

执行语义：

- 每个 tool call 表示一个清晰请求；不要把多个 query、URL、file path 塞进一个参数。
- 多个独立搜索、网页读取、文件读取或图片读取应发多个 tool call。
- 相邻 read-only tools 会并发执行，默认每个 parallel block 最多 3 个，并保持 tool result 原顺序。
- 可并发 read-only tools：`Glob`、`Grep`、`Read`、`ReadImage`、`WebSearch`、`ScholarSearch`、`WebFetch`。
- mutation / shell / terminal / PDF parsing / human interaction 不并发：`Write`、`Edit`、`Bash`、`ReadPDF`、`AskUser`、`Terminal*`、`str_replace_editor`。

PDF 和图片：

- `ReadPDF` 用 MinerU / `structai` 解析 PDF，返回文本和 `image_paths`。
- 推荐 PDF figure workflow：先 `ReadPDF`，再挑选 `image_paths`，最后用 `ReadImage` 查看具体图片。
- `ReadImage` 读取本地图片 metadata，并在 agent run 中把压缩图片作为 OpenAI-compatible `image_url` 发给模型。

`str_replace_editor` 细节：

- 用 `--extra-tool str_replace_editor` 启用。
- 支持 `view`、`create`、`str_replace`、`insert`、`undo_edit`。
- 要求 workspace 内绝对路径。
- `str_replace` 的 `old_str` 必须精确且唯一。
- `create` 拒绝覆盖已有文件。
- `undo_edit` 只撤销该 tool instance 对该文件的最近一次成功编辑。

## Workspace、Trace 与 Compaction

CLI / frontend：

- `--workspace-root` 是 agent 可见目录。
- `--trace-dir` 只在显式传入时写 trace。
- `--trace-dir` 不要指向 workspace，避免 agent 读取自己的 trace/session state。

API server：

```text
./api_runs/
└── run_YYYYMMDD_HHMMSS_<random>/
    ├── agent_workspace/
    │   └── inputs/images/
    └── agent_trace/
        ├── api_trace.jsonl
        ├── trace_*.jsonl
        └── session_state_*.json
```

trace 特点：

- flat JSONL event stream。
- 包含 system prompt、user prompt、assistant tool-call turns、tool results、runtime messages、final text。
- 统一字段包括 `run_id`、`event_index`、`turn_index`、`timestamp`、`model_name`、`workspace_root`、`role`、`text`、`tool_call_ids`、`tool_names`、`tool_arguments`、`finish_reason`、`termination`、`error`、`image_paths`、`capture_type`、`payload`。
- `capture_type="llm_call"` 保存发送给模型的请求和结构化响应。
- `capture_type="compaction"` 保存压缩前消息、summary request/response、compact memory 和压缩后消息状态。

自动 compaction：

- 默认触发阈值是 `128k`。
- CLI/env 可用 `AUTO_COMPACT_TRIGGER_TOKENS=16k`。
- Python API 可用 `compact_trigger_tokens="32k"`。

## Benchmark Adapters

benchmark-specific 行为放在 `benchmarks/`，不要塞进 `agent_base/`。

| Benchmark | 目录 | tracked contract |
| --- | --- | --- |
| ResearchClawBench | `benchmarks/ResearchClawBench/` | `README.md`、`role_prompt.md`、`adapter.py` |
| QA / VQA | `benchmarks/QA/` | `README.md`、`role_prompt.md` |
| SGI-DeepResearch | `benchmarks/SGI-DeepResearch/` | `README.md`、`role_prompt.md` |
| SGI-IdeaGeneration | `benchmarks/SGI-IdeaGeneration/` | `README.md`、`role_prompt.md` |
| SGI-DryExperiment | `benchmarks/SGI-DryExperiment/` | `README.md`、`role_prompt.md` |
| SGI-Reasoning | `benchmarks/SGI-Reasoning/` | `README.md`、`role_prompt.md` |
| SGI-WetExperiment | `benchmarks/SGI-WetExperiment/` | `README.md`、`role_prompt.md` |

Adapter 使用规则：

- 每个 benchmark 目录至少应有 `README.md` 说明运行 contract。
- `role_prompt.md` 只追加 benchmark-specific 规则，不复制 base prompt。
- 需要特殊停止条件、禁用工具或结果接受逻辑时，用 adapter subclass，不要改通用 ReAct loop。
- ResearchClawBench adapter 会自动选择 `ResearchClawBenchAgent`，并禁用不适合 benchmark 的交互工具。
- QA/VQA server 模式常配合 `benchmarks/QA/role_prompt.md --input-wrapper --output-wrapper`。
- SGI 系列 benchmark 应优先复用各自 `benchmarks/SGI-*/README.md` 中的 server 命令和 response contract。
- 改 benchmark 行为后，至少运行对应 README 检查和 API smoke test。

Benchmark 运行前检查：

- role prompt 是否只包含任务约束，不包含私有路径或凭据。
- workspace 是否隔离，输入文件是否已放在 agent 可见目录。
- trace 是否写到 agent 不可见目录。
- tool surface 是否符合 benchmark 公平性要求。
- `AskUser` 是否应该禁用。
- 输出格式是否需要 `--output-wrapper`。
- 多模态任务是否使用支持 vision 的后端模型。

## 测试与验证

安装后检查：

```bash
python - <<'PY'
import researchharness
print(researchharness.__version__)
print(researchharness.__file__)
PY
```

工具可用性：

```bash
python3 tests/test_tool_availability.py
```

推荐测试：

```bash
python3 tests/test_openai_api_checks.py
python3 tests/test_sgi_benchmark_readmes.py
python3 tests/test_agent_extension_checks.py
python3 tests/test_edge_case_checks.py
python3 tests/test_extra_tools.py
python3 tests/test_python_api_tools.py
python3 tests/test_toolchain_validation.py
```

API smoke check：

- 启动 `rh-server --api-runs-dir ./api_runs --host 127.0.0.1 --port 8686`。
- 调用 `GET /v1/health`。
- 用 OpenAI SDK 发 `model="RH"` 的纯文本请求。
- 如果要测多模态，构造 `data:image/...;base64,...`，不要传远程图片 URL 或本地路径。

## 常见问题

- 缺 required env：补齐 `.env` 或环境变量。
- Web/PDF 工具失败：检查 key、额度、网络、VPN/proxy、TLS；关闭 VPN/proxy 后重试。
- 图片请求 400：确认图片是 `data:image/...;base64,...`。
- 底层模型拒绝图片：换支持 vision 的模型，或改纯文本任务。
- API streaming 报错：当前 API 不支持 `stream=true`。
- 输出格式不符合预期：明确输出格式，或在 benchmark 模式开启 `--output-wrapper`。
- 工具不该出现：用 `--tool NAME` 或 Python `tools=[...]` 显式限定完整工具集。

## 当前边界

- 第一版 API 暂不支持 streaming。
- 暂不支持 async run status。
- 暂不支持 cancellation。
- 暂不提供 artifact download endpoint。
- 暂不支持远程图片 URL 下载。
- 暂无内建用户认证或多租户访问控制。
- 这些能力应作为外层服务扩展，不要破坏核心 harness loop。
