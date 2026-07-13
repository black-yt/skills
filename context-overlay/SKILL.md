---
name: context-overlay
description: Use when configuring or debugging the context-overlay OpenAI-compatible proxy for deterministic prompt/context injection, prompt patching, rule matching, request routing, rejection rules, skill_dir retrieval, streaming forwarding, and local or tunneled proxy validation.
---

# Context Overlay

## 使用边界

- `context-overlay` 是 OpenAI-compatible request proxy，位于 SDK client 和上游模型服务之间。
- 用于按规则注入 context、skill、policy、memory、profile、prompt patch，或把特定请求 route 到另一个上游。
- 它不运行 agent loop、不执行 tools、不解释模型输出。
- 它应保留 OpenAI-compatible 字段，例如 `tools`、`image_url`、`response_format`、`stream`。
- 不要把 secrets 写进 overlay 文本、skill JSON 或公开配置；优先用环境变量展开。
- 暴露到公网前必须配置 `auth.api_key`，不要公开无认证 proxy。
- 需要安装、开公网 tunnel、改服务端口或改长期配置时，先征得用户同意。

## 安装与最小配置

- PyPI 安装：`pip install context-overlay`
- GitHub 源码：https://github.com/black-yt/context-overlay

## 上游版本锚点

- 当前 skill 对照 context-overlay GitHub `VERSION`：`0.0.5`。
- 当前 skill 对照 GitHub HEAD：`e7a7c83924a225c443c454c80aab0735ca1bbe6c`。
- 维护本 skill 前，先重新检查上游 `VERSION` 和 HEAD；如果任一变化，必须阅读 README、`pyproject.toml`、CLI help 和相关源码后再更新。

安装模板：

```bash
pip install context-overlay
```

开发版本模板：

```bash
git clone https://github.com/black-yt/context-overlay.git
cd context-overlay
pip install -e ".[dev]"
pytest -q
```

## 源码追溯

- 如果配置字段、transform 行为或转发逻辑不确定，优先追溯已安装包源码。
- `inspect.getsource(...)` 适合查看 `apply_rules`、`load_config`、`SkillStore`、FastAPI app 创建逻辑。
- `module.__file__` 可定位包安装路径，再按需打开源码文件。
- 源码只用于阅读和定位问题，不要改源码，不要直接改 `site-packages` 或长期环境；需要改库时，先 clone 仓库并使用 editable install，且必须征得用户同意。

```python
import inspect
import context_overlay
from context_overlay import apply_rules, load_config, SkillStore
from context_overlay.server import create_app

print(context_overlay.__file__)
print(inspect.getsource(load_config))
print(inspect.getsource(apply_rules))
print(inspect.getsource(SkillStore))
print(inspect.getsource(create_app))
```

命令行快速定位：

```bash
python - <<'PY'
import context_overlay
print(context_overlay.__file__)
PY
```

最小 `config.yaml`：

```yaml
upstream:
  base_url: "${UPSTREAM_BASE_URL}"
  api_key: "${UPSTREAM_API_KEY}"
  timeout_seconds: 600

auth:
  api_key: "${CONTEXT_OVERLAY_API_KEY}"

rules:
  - name: add_short_system_overlay
    match:
      path: "/v1/chat/completions"
      messages_regex:
        - "scientific"
    transforms:
      - type: append_system
        content: "When relevant, produce a concrete, evidence-grounded plan before solving."
```

- `upstream.base_url` 必填，且应包含 `/v1`。
- `upstream.api_key` 会作为 Bearer token 发给上游；本地无认证上游可用 `unused`。
- `upstream.timeout_seconds` 控制请求上游的 HTTP timeout。
- `auth.api_key` 用来保护 proxy；设置后 client 必须带 `Authorization: Bearer ...`。
- YAML 字符串会通过 `os.path.expandvars` 展开，因此可写 `${UPSTREAM_BASE_URL}`、`${UPSTREAM_API_KEY}`、`${CONTEXT_OVERLAY_API_KEY}`。

启动 proxy：

```bash
context-overlay serve --config config.yaml --host 127.0.0.1 --port 8011
```

- CLI 参数：
  - `--config`：YAML 配置路径，必填。
  - `--host`：绑定地址，默认 `127.0.0.1`。
  - `--port`：绑定端口，默认 `8011`。
  - `--reload`：启用 uvicorn reload，适合本地开发。

等价 module 形式：

```bash
python -m context_overlay.cli serve --config config.yaml --host 127.0.0.1 --port 8011
```

版本检查：

```python
import context_overlay

print(context_overlay.__version__)
```

核对上游版本：

```bash
curl -fsSL https://raw.githubusercontent.com/black-yt/context-overlay/main/VERSION
git ls-remote https://github.com/black-yt/context-overlay.git HEAD
```

OpenAI SDK 调用：

```python
from openai import OpenAI

client = OpenAI(
    api_key="[CONTEXT_OVERLAY_API_KEY]",
    base_url="http://127.0.0.1:8011/v1",
)

response = client.chat.completions.create(
    model="[MODEL_ID]",
    messages=[{"role": "user", "content": "Analyze this scientific task."}],
)
print(response.choices[0].message.content)
```

## Rule Matching

- 每条 rule 包含 `name`、`match`、`transforms`。
- 支持的 match 字段：
  - `path`：精确匹配请求路径，例如 `/v1/chat/completions`。
  - `model_regex`：匹配 `body["model"]`。
  - `messages_regex`：匹配 chat messages 拼接文本；列表中的正则都必须命中，大小写不敏感。
  - `extra_body`：请求 body 中必须出现的 key-value 子集。
- 多条 rule 同时匹配时，按 YAML 顺序依次应用。
- 未匹配 rule 会跳过，不应影响请求。

```yaml
rules:
  - name: inject_when_task_matches
    match:
      path: "/v1/chat/completions"
      model_regex: "Qwen|gpt"
      messages_regex:
        - "INSTRUCTIONS"
        - "report.md"
      extra_body:
        skill_role: "solver"
    transforms:
      - type: append_system
        content: "Use a checklist-aware scientific planning workflow."
```

## Transform Types

- `append_system`：追加到 system message；没有 system message 时创建。
- `prepend_system`：前置到 system message。
- `append_user`：追加到最后一条 user message。
- `prepend_user`：前置到最后一条 user message。
- `insert_before`：在 system message 中第一个正则命中前插入；省略 `pattern` 时等价 `prepend_system`。
- `insert_after`：在 system message 中第一个正则命中后插入；省略 `pattern` 时等价 `append_system`。
- `regex_replace`：替换 system 或最后一条 user message 中的文本。
- `route`：修改匹配请求的 `upstream_base_url` 和/或 `model`。
- `reject`：拒绝匹配请求，返回 HTTP 403。

`insert_before`、`insert_after`、`regex_replace` 支持 `target: system` 或 `target: user`；默认是 `system`。

注意：对多模态 user message 使用 user transform 时，只有 text block 会被转换成 patched text message。多模态请求优先用 system transform。

插入文本语义：

- `insert_before` / `insert_after` 的 overlay content 按字面文本插入。
- Markdown、LaTeX 反斜杠、Windows 路径反斜杠等不会被当作正则 replacement 语法解释。
- `regex_replace` 会走 Python `re.sub` 的 replacement 语义；需要字面插入复杂文本时，优先用 `insert_before` / `insert_after`，或显式检查 replacement 中的反斜杠。
- `regex_replace` 省略 `replacement` 时，会使用 resolved `content` 作为 replacement。

```yaml
transforms:
  - type: regex_replace
    target: system
    pattern: "Return a short answer\\."
    replacement: "Return a complete, self-contained answer."
```

```yaml
rules:
  - name: route_large_model
    match:
      model_regex: "large"
    transforms:
      - type: route
        upstream_base_url: "http://127.0.0.1:8020/v1"
        model: "[LARGE_MODEL_ID]"
```

```yaml
rules:
  - name: reject_unapproved_mode
    match:
      extra_body:
        unsafe_mode: true
    transforms:
      - type: reject
        reason: "unsafe_mode is not allowed through this proxy"
```

## Content Sources

- `content` 可以是直接字符串。
- `type: text`：内联文本。
- `type: file`：每次请求读取 UTF-8 文件。
- `type: skill_dir`：从目录读取 `*.json` skill，按 lexical token overlap 取 top-k 并渲染注入。

`skill_dir` JSON 推荐字段：

```json
{
  "name": "scientific_planning",
  "description": "Plan a scientific analysis with concrete validation artifacts.",
  "category": "scientific_analysis",
  "content": "Detailed planning guidance...",
  "score": 5
}
```

实际必备字段：

- `name`
- `description`
- `content`

完整 skill 注入示例：

```yaml
rules:
  - name: inject_solver_planning_skills
    match:
      path: "/v1/chat/completions"
      messages_regex:
        - "INSTRUCTIONS"
        - "report.md"
    transforms:
      - type: insert_before
        pattern: "Current date:"
        content:
          type: skill_dir
          path: "./skills/generated_skills"
          top_k: 5
          max_chars: 32000
          title: "Relevant Planning Skills"
```

## Python API

- `context_overlay.__version__`：当前安装包版本。
- `load_config(path)`：读取 YAML 并返回 `ContextOverlayConfig`。
- `ContextOverlayConfig.model_validate(...)`：直接验证配置对象。
- `apply_rules(body, config, path="/v1/chat/completions")`：对请求 body 应用匹配 rule 和 transforms，适合单元测试。
- `create_app(config)`：创建 FastAPI app，用于嵌入式服务。
- `Skill.from_json_file(path)`：读取单个 skill JSON。
- `SkillStore.from_dir(path).retrieve(query, top_k=...)`：从 skill 目录检索相关 skill。

```python
from context_overlay import ContextOverlayConfig, apply_rules

config = ContextOverlayConfig.model_validate(
    {
        "upstream": {"base_url": "http://127.0.0.1:8010/v1"},
        "rules": [
            {
                "name": "append_overlay",
                "match": {"messages_regex": ["hello"]},
                "transforms": [{"type": "append_system", "content": "Injected."}],
            }
        ],
    }
)

body = {"model": "m", "messages": [{"role": "user", "content": "hello"}]}
new_body = apply_rules(body, config)
print(new_body["messages"][0])
```

嵌入式 FastAPI 服务：

```python
import uvicorn
from context_overlay import load_config
from context_overlay.server import create_app

config = load_config("config.yaml")
app = create_app(config)

uvicorn.run(app, host="127.0.0.1", port=8011)
```

Skill JSON 与检索：

```python
from pathlib import Path
from context_overlay import Skill, SkillStore

skill = Skill.from_json_file(Path("skills/example.json"))
print(skill.name, skill.description)

store = SkillStore.from_dir("./skills/generated_skills")
matched = store.retrieve("glacier mass balance uncertainty", top_k=3)
```

## 转发与部署

- 所有 `/v1/*` 路径都会转发到 upstream。
- 只有 `POST /v1/chat/completions` 会应用 rule transforms。
- 其他 `/v1/*` endpoint 原样转发请求内容。
- streaming 请求通过转发 upstream streaming bytes 支持。
- 临时公网访问可用 `cloudflared tunnel --url http://127.0.0.1:8011`，但 quick tunnel URL 临时、随机、无 uptime 保证。
- 长期生产使用 named tunnel 和 access policy。

```bash
context-overlay serve --config config.yaml --host 127.0.0.1 --port 8011
cloudflared tunnel --url http://127.0.0.1:8011
```

## Runtime Logs

每个 `POST /v1/chat/completions` 请求都会在 uvicorn 日志中输出 overlay decision log。日志是 key-value 风格，便于排查“规则是否命中”和“命中了哪条规则”，但不会直接打印注入内容正文。

未命中任何 rule：

```text
context_overlay timestamp=2026-06-07T10:20:30+08:00 event=no_rule_matched path=/v1/chat/completions model=gpt-5.5 rules_checked=40
```

命中 rule：

```text
context_overlay timestamp=2026-06-07T10:20:30+08:00 event=rule_matched path=/v1/chat/completions model=gpt-5.5 rule=inject_planning_skill transform_count=1 transforms=type=insert_before;target=system;pattern=yes;content=file:/path/to/rendered_skill.md
```

日志字段：

- `timestamp`：本地时区 ISO-8601 时间，表示 overlay 决策日志生成时间，不是上游模型响应时间。
- `event`：`rule_matched` 或 `no_rule_matched`。
- `path`：请求路径。
- `model`：请求 body 中的 model 字段。
- `rule`：命中的 rule 名称，仅 `rule_matched` 有。
- `rules_checked`：配置中的 rule 总数，仅 `no_rule_matched` 有。
- `transform_count`：命中 rule 的 transform 数量。
- `transforms`：结构化摘要，包含 type、target、是否有 pattern、是否 route upstream、content 来源。

内容来源日志：

- 内联字符串记录为 `content=inline_text`。
- 文件记录为 `content=file:/path/to/file`。
- skill 目录记录为 `content=skill_dir:/path:top_k=N`。
- 缺失 content 记录为 `content=none`。

如果一个请求命中多条 rule，会为每条命中的 rule 输出一行 `rule_matched`。如果没有任何 rule 命中，只输出一行 `no_rule_matched`。

## Echo 验证模板

先用本地 echo upstream 验证 rule 是否真的改写了请求，再接真实模型。

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/v1/models")
async def models():
    return {"object": "list", "data": [{"id": "echo-model", "object": "model"}]}

@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    messages = body.get("messages") or []
    last_user = ""
    for message in reversed(messages):
        if message.get("role") == "user":
            last_user = str(message.get("content", ""))
            break
    return {
        "id": "chatcmpl-echo",
        "object": "chat.completion",
        "model": body.get("model", "echo-model"),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": last_user},
                "finish_reason": "stop",
            }
        ],
    }
```

```yaml
upstream:
  base_url: "http://127.0.0.1:19210/v1"
  api_key: "unused"
  timeout_seconds: 30

auth:
  api_key: "proxy-key"

rules:
  - name: insert_skill_after_test
    match:
      path: "/v1/chat/completions"
      messages_regex:
        - "test"
    transforms:
      - type: regex_replace
        target: user
        pattern: "test"
        replacement: "test[skill]"
```

```bash
uvicorn upstream:app --host 127.0.0.1 --port 19210
context-overlay serve --config config.yaml --host 127.0.0.1 --port 19211
```

```bash
curl -sS \
  -H "Authorization: Bearer proxy-key" \
  -H "Content-Type: application/json" \
  http://127.0.0.1:19211/v1/chat/completions \
  -d '{"model":"echo-model","messages":[{"role":"user","content":"hello test world"}]}'
```

期望 assistant content：

```text
hello test[skill] world
```

## 验证清单

- `context-overlay serve --config ...` 能正常启动。
- `/v1/models` 能通过 proxy 访问 upstream。
- 未命中的请求保持原样。
- 命中的请求按 rule 顺序应用 transform。
- 日志中能看到 `rule_matched` / `no_rule_matched`，且 transform 摘要和预期一致。
- `tools`、`image_url`、`response_format`、`stream` 等字段未被无意破坏。
- 多模态请求优先注入 system，不轻易 patch user message。
- 公网暴露前已设置 `auth.api_key`，且 upstream key 只保存在服务端。
