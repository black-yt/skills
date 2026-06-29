# Setup And Source

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

依赖版本经验：

- 新版本 `requirements.txt` 使用下限约束，不再假设每个依赖都是精确 pin。
- 典型形式是 `fastapi>=...`、`openai>=...`、`structai>=0.1.23`、`uvicorn>=...`。
- 排查依赖问题时，先看当前 checkout 的 `requirements.txt` 和当前环境安装版本，不要套用旧的固定版本经验。
- 不要在共享环境里随手升级依赖；需要升级时先创建独立环境或征得用户同意。

检查当前安装版本：

```bash
python - <<'PY'
import importlib.metadata as md

for name in ["researchharness", "openai", "structai", "fastapi", "uvicorn"]:
    try:
        print(name, md.version(name))
    except md.PackageNotFoundError:
        print(name, "not installed")
PY
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
