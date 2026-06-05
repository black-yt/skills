---
name: structai
description: Use when building, testing, or debugging LLM applications with the StructAI Python toolkit, including LLMAgent calls, structured outputs, LLM judging, batch concurrency, file/PDF utilities, text parsing, private-IP no_proxy handling, and timeout wrappers.
---

# StructAI

## 使用边界

- 用于基于 `structai` 快速搭建 LLM workflow、批量推理、结构化输出、评测、PDF 解析和常用 I/O。
- 不要把 API key、token、私有 base URL 写进代码或日志；优先读取环境变量。
- 不要擅自安装、升级或修改共享 Python/conda 环境；需要安装 `structai` 或依赖时，先征得用户同意。
- 如果本地 `structai` 版本和示例不一致，先用 `python -c "from structai import structai_skill; print(structai_skill())"` 查看当前版本文档。

## 环境变量

```bash
export LLM_API_KEY="[API_KEY]"
export LLM_BASE_URL="[OPENAI_COMPATIBLE_BASE_URL]"
export MINERU_TOKEN="[MINERU_TOKEN]"  # 仅 PDF 解析需要
```

- PyPI 安装：`pip install structai`
- GitHub 源码：https://github.com/black-yt/structai

安装模板：

```bash
pip install structai
```

开发版本模板：

```bash
git clone https://github.com/black-yt/structai.git
cd structai
pip install -e .
```

## 源码追溯

- 如果示例和当前行为不一致，优先追溯已安装包源码，而不是猜测 API。
- `inspect.getsource(...)` 适合快速查看函数、类、方法的真实实现。
- `module.__file__` 可定位包安装路径，再按需打开源码文件。
- 源码只用于阅读和定位问题，不要改源码，不要修改 `site-packages` 或共享环境；需要改库时，先 clone 仓库并使用 editable install，且必须征得用户同意。

```python
import inspect
import structai
from structai import LLMAgent, Judge, read_pdf, multi_thread

print(structai.__file__)
print(inspect.getsource(LLMAgent))
print(inspect.getsource(Judge))
print(inspect.getsource(read_pdf))
print(inspect.getsource(multi_thread))
```

命令行快速定位：

```bash
python - <<'PY'
import structai
print(structai.__file__)
PY
```

## 内置文档与 Prompt

- `structai_skill()` 会返回当前安装版本的 Markdown 文档；版本不确定时优先查看它。
- `prompts` 保存内置 judge / arena 等 prompt 模板；做评测时优先复用已有模板，再按任务小幅调整。
- 不要把 `structai_skill()` 的长输出无条件塞进上下文；只在 API 不确定或需要核对当前版本时读取。

```python
from structai import structai_skill, prompts

print(structai_skill())
print(prompts.keys())
```

## LLM 调用

- `LLMAgent()` 默认读取 `LLM_API_KEY` 和 `LLM_BASE_URL`。
- 初始化常用参数：`api_key`、`api_base`、`model_version`、`system_prompt`、`max_tokens`、`temperature`、`http_client`、`headers`、`time_limit`、`max_try`、`use_responses_api`。
- `__call__` 常用参数：`query`、`system_prompt`、`return_example`、`max_try`、`wait_time`、`n`、`max_tokens`、`temperature`、`image_paths`、`history`、`use_responses_api`、`list_len`、`list_min`、`list_max`、`check_keys`。
- 用 `return_example` 约束输出结构：`str`、`list`、`dict`。
- 用 `history` 传多轮上下文。
- 用 `image_paths` 传图片输入。
- 用 `n` 获取多个候选。
- 用 `max_try`、`time_limit`、`wait_time` 控制重试和超时。
- 需要 Responses API 时设置 `use_responses_api=True`，并配合 `messages_to_responses_input` / `extract_text_outputs`。

```python
from structai import LLMAgent

agent = LLMAgent(
    model_version="[MODEL_ID]",
    system_prompt="You are a helpful assistant.",
    max_try=2,
    time_limit=300,
)

answer = agent("Summarize the task in three bullets.")

items = agent(
    "Return exactly three risks as a JSON-like list.",
    return_example=["risk"],
    list_len=3,
)

variable_items = agent(
    "Return two to five concrete risks.",
    return_example=["risk"],
    list_min=2,
    list_max=5,
)

profile = agent(
    "Create a compact user profile.",
    return_example={"name": "str", "age": 1, "city": "str"},
    check_keys=True,
)

caption = agent(
    "Describe these images.",
    image_paths=["[IMAGE_1].png", "[IMAGE_2].jpg"],
)
```

## Messages 与 Responses API

- `messages_to_responses_input(messages)` 可把 Chat Completions `messages` 转成 Responses API 输入结构。
- `extract_text_outputs(response)` 可从 Chat Completions 或 Responses API 返回对象中提取文本输出。
- `print_messages(messages)` 用彩色标签打印多轮消息，适合调试 prompt，但不要在日志里打印 secrets。

```python
from structai import messages_to_responses_input, extract_text_outputs, print_messages

messages = [
    {"role": "system", "content": "You are concise."},
    {"role": "user", "content": "Hello."},
]

system_prompt, input_blocks = messages_to_responses_input(messages)
print_messages(messages)

# response = client.responses.create(...)
# texts = extract_text_outputs(response)
```

## LLM Judge 与 Arena

- `Judge()` 可组合 exact match、`math_verify` 和 LLM-as-a-judge。
- 初始化常用参数：`model_version`、`system_prompt`、`max_tokens`、`temperature`、`time_limit`、`max_try`、`prompt_tmp`、`use_tqdm`、`use_math_verify`、`use_llm_judge`、`llm_tags`、`workers`。
- 输入字典至少包含 `question`、`answer`、`model_answer`。
- 多个候选答案用 `<answer_split>` 分隔，可得到 pass@k / passall@k。
- 做 A/B 比较时使用 `prompts["llm_judge_arena"]`，并关闭不适用的 `math_verify`。
- Judge 结果仍需人工抽查；不要把 LLM judge 当成唯一真值。

```python
from structai import Judge, prompts

judge = Judge(model_version="[JUDGE_MODEL]")

sample = {
    "question": "1 + 1 = ?",
    "answer": "2",
    "model_answer": "2<answer_split>two",
}
result = judge(sample)
print(result["exact_match_pass@k"], result["llm_judge_pass@k"])

arena_judge = Judge(
    prompt_tmp=prompts["llm_judge_arena"]["prompt_tmp"],
    llm_tags=prompts["llm_judge_arena"]["llm_tags"],
    use_math_verify=False,
)
```

## 批量并发

- API 调用、网络请求、轻量 I/O 优先用 `multi_thread`。
- CPU-bound 函数优先用 `multi_process`。
- `inp_list` 是 `list[dict]`，每个 dict 会作为函数关键字参数传入。
- 控制 `max_workers`，避免触发 API 限流、机器负载过高或共享资源拥堵。

```python
from structai import multi_thread, multi_process

def call_one(prompt):
    return agent(prompt)

prompts = [{"prompt": p} for p in ["a", "b", "c"]]
responses = multi_thread(prompts, call_one, max_workers=8)

def heavy_computation(n):
    return sum(range(n))

jobs = [{"n": 1000000} for _ in range(4)]
results = multi_process(jobs, heavy_computation, max_workers=4)
```

## 文件、图片与 PDF

- `load_file(path)` 按后缀自动读取 JSON/JSONL/CSV/Parquet/XLSX/TXT/MD/Pickle/NumPy/PT/Image。
- `save_file(data, path)` 按后缀自动保存，并创建必要目录。
- 支持的常见读取后缀包括 `.json`、`.jsonl`、`.csv`、`.parquet`、`.xlsx`、`.txt`、`.md`、`.py`、`.pkl`、`.npy`、`.pt`、`.png`、`.jpg`、`.jpeg`。
- `get_all_file_paths(directory, suffix=..., filter_func=..., absolute=...)` 递归收集文件路径。
- `read_pdf(path)` 调用 MinerU 解析 PDF，需要 `MINERU_TOKEN`。
- `read_pdf` 返回 `text`、`img_paths`、`imgs`；解析后要检查 Markdown 是否完整、图片是否存在。
- `encode_image(img)` 把 PIL 图片转 base64，适合构造多模态请求。
- `print_once(msg)` / `make_print_once()` 用于循环中只打印一次提示，避免日志刷屏。

```python
from structai import load_file, save_file, read_pdf, encode_image, get_all_file_paths

data = load_file("[DATA].jsonl")
save_file(data[:10], "[OUTPUT_DIR]/sample.json")

py_files = get_all_file_paths("[PROJECT_ROOT]", suffix=".py", absolute=False)

parsed = read_pdf("[PAPER].pdf")
if parsed is not None:
    print(parsed["text"][:500])
    print(parsed["img_paths"])

b64 = encode_image(parsed["imgs"][0])
```

## 文本和标签解析

- `str2dict` / `str2list` 用于容错解析模型输出中的 dict/list。
- `parse_think_answer` 用于解析 `<think>...</think><answer>...</answer>`。
- `extract_within_tags` 用于抽取自定义标签之间的内容。
- `remove_tag` 用于去掉 `<think>`、`<answer>` 等标签。
- `sanitize_text` 用于清理控制字符和异常字符。
- `filter_excessive_repeats` 用于删除过度重复字符或短片段。
- `cutoff_text` 用于裁剪异常长文本，并清理重复字符和不可控内容。
- `extract_markdown_images` 用于从 Markdown 中抽取图片路径。

```python
from structai import (
    cutoff_text,
    extract_markdown_images,
    extract_within_tags,
    filter_excessive_repeats,
    sanitize_text,
    str2dict,
)

obj = str2dict("{'score': 1, 'reason': 'ok'}")
answer = extract_within_tags("<answer>42</answer>", "<answer>", "</answer>")
clean = sanitize_text(raw_text)
clean = filter_excessive_repeats(clean, threshold=5)
safe_text = cutoff_text(long_text, l=20000)
images = extract_markdown_images(markdown_text)
```

## 网络与服务

- 访问私网 OpenAI-compatible 服务前，先调用 `add_no_proxy_if_private(url)`，避免请求走外部代理。
- `run_server()` 可启动一个基于 `LLM_BASE_URL` / `LLM_API_KEY` 的 OpenAI-compatible proxy server。
- 对长期服务设置清晰端口、日志和停止方式；不要在共享机器上随意暴露无认证服务。

```python
from structai import add_no_proxy_if_private
from openai import OpenAI

url = "http://[PRIVATE_IP]:[PORT]/v1"
add_no_proxy_if_private(url)

client = OpenAI(api_key="[API_KEY]", base_url=url)
print(client.models.list().data[0].id)
```

## 超时控制

- 用 `timeout_limit(timeout=...)` 装饰可能卡住的函数。
- 用 `run_with_timeout(func, args=..., kwargs=..., timeout=...)` 包裹一次性调用。
- LLM/API 调用优先使用 `LLMAgent` 自带的 `time_limit`，普通函数再使用 timeout 工具。

```python
from structai import run_with_timeout

def task(x):
    return x * 2

result = run_with_timeout(task, args=(10,), timeout=1.0)
```

## 验证清单

- `python -c "import structai; print(structai.__version__ if hasattr(structai, '__version__') else 'structai imported')"` 可成功导入。
- `LLM_API_KEY`、`LLM_BASE_URL` 在需要 LLM 调用时已配置。
- PDF 解析前已配置 `MINERU_TOKEN`，并确认输出 Markdown 和图片路径。
- 批量任务限制 `max_workers`，失败样本不应被标记为成功消费。
- 私网服务调用前已处理 `no_proxy`。
