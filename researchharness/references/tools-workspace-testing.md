# Tools Workspace Testing

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

- 默认触发阈值是 `96k`。
- CLI/env 可用 `COMPACT_TRIGGER_TOKENS=16k`。
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

- 真实任务前必须要求所有工具通过。
- 需要机器可读结果时使用 `python3 tests/test_tool_availability.py --json`。

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
