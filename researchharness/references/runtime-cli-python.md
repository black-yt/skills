# Runtime Cli Python

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
11. 如果达到 round、runtime、timeout 或 protocol error 边界，写入 termination/error。
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

## 环境变量

启动前要求：

- 运行 ResearchHarness 前必须先配置 `.env.example` 中对应的必需变量。
- 必需变量不只是 LLM 服务；联网和解析工具的 key 也必须配置。
- 没有填齐 `SERPER_KEY`、`JINA_KEY`、`MINERU_TOKEN` 时，不要开始真实任务，因为 `WebSearch`、`ScholarSearch`、`WebFetch`、`ReadPDF` 会不可用。
- 如果是源码 checkout，可以从 `.env.example` 复制为 `.env`，再替换占位符。
- 不要把缺少 key、依赖缺失、额度耗尽或外部服务不可用当成“可跳过”的问题；这类情况都应该先修好。

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
- `MAX_ROUNDS`
- `MAX_RUNTIME_SECONDS`
- `TIMEOUT_SECONDS`
- `WEBFETCH_TIMEOUT_SECONDS`
- `WEBFETCH_MAX_CHARS`
- `MAX_OUTPUT_TOKENS`
- `MAX_INPUT_TOKENS`
- `RECENT_HISTORY_BUDGET_TOKENS`
- `COMPACT_SUMMARY_MAX_TOKENS`
- `MAX_RETRIES`
- `TEMPERATURE`
- `TOP_P`
- `PRESENCE_PENALTY`
- `COMPACT_TRIGGER_TOKENS`
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
| `MAX_ROUNDS` | `500` | ReAct loop 最大轮次。 |
| `MAX_RUNTIME_SECONDS` | `10800` | 单次 run 最大秒数。 |
| `TIMEOUT_SECONDS` | `1200` | 单次 chat-completions 请求 timeout。 |
| `WEBFETCH_TIMEOUT_SECONDS` | `300` | 单次 WebFetch 总 timeout。 |
| `WEBFETCH_MAX_CHARS` | `16384` | 单次 WebFetch 返回字符上限。 |
| `MAX_OUTPUT_TOKENS` | `16384` | 请求模型输出 token 上限。 |
| `MAX_INPUT_TOKENS` | `131072` | runtime token accounting 输入预算。 |
| `RECENT_HISTORY_BUDGET_TOKENS` | `8192` | compaction 后保留的最近原始历史 token 预算。 |
| `COMPACT_SUMMARY_MAX_TOKENS` | `8192` | compaction summary 的最大输出 token 和默认 compaction reserve。 |
| `MAX_RETRIES` | `5` | LLM API 瞬时错误最大重试次数。 |
| `TEMPERATURE` | `0.6` | 主模型 temperature。 |
| `TOP_P` | `0.95` | 主模型 top-p。 |
| `PRESENCE_PENALTY` | `1.00` | provider 支持时使用。 |
| `COMPACT_TRIGGER_TOKENS` | `96k` | 自动上下文压缩触发阈值。 |
| `IMAGE_PART_TOKEN_ESTIMATE` | `2048` | 每个 image content part 的 token 估计。 |
| `LLM_IMAGE_MAX_EDGE` | `1568` | 发送给多模态模型的图片最大边长。 |
| `LLM_IMAGE_MAX_BYTES` | `524288` | 发送给多模态模型的压缩图片最大字节数。 |
| `LLM_IMAGE_JPEG_QUALITY` | `85` | 图片压缩初始 JPEG 质量。 |

配置优先级：

```text
explicit Python/API/CLI arguments > process environment variables > .env > code defaults
```

配置边界：

- `.env` 只补齐缺失变量，不覆盖 shell 中已经 export 的进程环境变量。
- Python 参数名对应大写环境变量，例如 `max_rounds` 对应 `MAX_ROUNDS`，`compact_trigger_tokens` 对应 `COMPACT_TRIGGER_TOKENS`。
- `recent_history_budget_tokens` 对应 `RECENT_HISTORY_BUDGET_TOKENS`，`compact_summary_max_tokens` 对应 `COMPACT_SUMMARY_MAX_TOKENS`。
- CLI 中 `--workspace-root` 优先于 `WORKSPACE_ROOT`。
- API server 中，request-local `model`、`extra_body["workspace-root"]`、`extra_body["llm-extra-body"]` 只覆盖当前请求。
- `--trace-dir` 没有环境变量等价项；只有显式传入时才写 trace/session state。
- token budget 会在 run 开始前校验；无效配置会直接报错，不会被静默 clamp。
- `MAX_OUTPUT_TOKENS + COMPACT_SUMMARY_MAX_TOKENS` 必须小于 `MAX_INPUT_TOKENS`。
- 显式 `COMPACT_TRIGGER_TOKENS` 必须小于 `MAX_INPUT_TOKENS - MAX_OUTPUT_TOKENS`，为最终回复保留空间。
- 如果未设置 `COMPACT_TRIGGER_TOKENS`，默认触发点按 `MAX_INPUT_TOKENS - MAX_OUTPUT_TOKENS - COMPACT_SUMMARY_MAX_TOKENS` 计算。

Provider-specific `extra_body`：

- 用于传递 OpenAI-compatible provider 的非标准字段，例如 provider-specific thinking / reasoning 开关。
- ResearchHarness 只校验它是 JSON object / Python dict，不解释字段含义，不写死 provider 名或字段名。
- Python API：`create_agent(..., extra_body={"enable_thinking": False})`。
- CLI：`--llm-extra-body-json '{"enable_thinking": false}'`。
- API server：OpenAI SDK 请求中写 `extra_body={"llm-extra-body": {"enable_thinking": false}}`。
- API server 的 `extra_body["workspace-root"]` 是 ResearchHarness 请求控制字段，不会转发给底层模型。
- API server 中 provider-specific 字段必须放进 `llm-extra-body`，不要直接放在顶层 `extra_body`。
- invalid list/string/null 等非 object 值会在 agent run 开始前被拒绝。
- 如果上游 provider 不支持某字段，可能由 provider 拒绝请求；开启 thinking / reasoning 时通常需要调高 `MAX_OUTPUT_TOKENS` 或 `max_output_tokens`。

2026-06-06 后的迁移提示：

| 旧变量 | 当前处理 |
| --- | --- |
| `MAX_AGENT_ROUNDS` | 改用 `MAX_ROUNDS`。 |
| `MAX_AGENT_RUNTIME_SECONDS` | 改用 `MAX_RUNTIME_SECONDS`。 |
| `LLM_TIMEOUT_SECONDS` | 改用 `TIMEOUT_SECONDS`。 |
| `LLM_MAX_OUTPUT_TOKENS` | 改用 `MAX_OUTPUT_TOKENS`。 |
| `LLM_MAX_RETRIES` | 改用 `MAX_RETRIES`。 |
| `AUTO_COMPACT_TRIGGER_TOKENS` | 改用 `COMPACT_TRIGGER_TOKENS`。 |
| `MAX_LLM_CALL_PER_RUN` | 已移除，没有等价的新环境变量；不要继续写入新脚本。 |

正式使用前运行工具可用性检查：

```bash
python3 tests/test_tool_availability.py
```

检查要求：

- 真实任务开始前必须跑完整工具可用性检查。
- 预期结果是所有工具通过；只要有工具失败，就不要把当前 ResearchHarness 环境视为可用。
- 如果失败来自 missing credentials、missing dependencies、exhausted service credits 或 unavailable external tools，应先修复，而不是跳过。
- 如果 `WebSearch`、`ScholarSearch`、`WebFetch` 或 `ReadPDF` 出现 network、TLS、upload、download、PDF parsing 错误，优先尝试关闭 VPN/proxy 后重试。
- 如果源码 checkout 里需要机器可读结果，可运行 `python3 tests/test_tool_availability.py --json`。

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

传 provider-specific `extra_body`：

```bash
rh-agent "Answer briefly." \
  --llm-extra-body-json '{"enable_thinking": false}'
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
| `--llm-extra-body-json JSON` | 否 | provider-specific OpenAI-compatible request `extra_body` object。 |

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
    extra_body={"enable_thinking": False},
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
    extra_body={"enable_thinking": False},
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
