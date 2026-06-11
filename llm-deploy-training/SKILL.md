---
name: llm-deploy-training
description: "当需要部署或训练 LLM/VLM 时使用；覆盖 vLLM OpenAI-compatible 服务、多模态输入限制、Qwen3.5 工具调用、thinking/reasoning 控制、CUDA Graph 策略，以及 ms-swift SFT/DPO/GRPO full training、数据校验、显存排错和训练检查。"
---

# LLM Deploy And Training

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 规定 LLM/VLM 部署和训练的共通安全原则、版本匹配方法、官方文档优先级和只读源码追溯方式。 | 核心原则、版本匹配、官方文档、源码追溯 | 默认读取 | `SKILL.md` |
| 2 | 记录 vLLM OpenAI-compatible 服务的部署脚本参数、多模态限制、工具调用、Qwen thinking、CUDA Graph 和本地端口转发验证。 | OpenAI-compatible 服务、多模态、工具调用、Qwen thinking、CUDA Graph、SSH local port forwarding | 需要部署、验证或排错 vLLM 服务，尤其是多模态、工具调用、thinking 或本地转发时必须读取 | [references/vllm-deployment.md](references/vllm-deployment.md) |
| 3 | 记录 ms-swift SFT/DPO/GRPO full training 的默认超参、JSONL 数据格式、显存排错顺序、训练前后检查和 rjob 资源模板。 | SFT、DPO、GRPO、full training、数据格式、显存排错、rjob 资源建议 | 需要编写、审查或排错 ms-swift SFT/DPO/GRPO 训练脚本时必须读取 | [references/ms-swift-training.md](references/ms-swift-training.md) |

## 核心原则

- 部署和训练都优先复用已有环境；不要擅自升级 `torch`、`vllm`、`transformers`、`ms-swift` 或共享 conda 环境。
- 部署脚本使用环境变量配置模型路径、端口、上下文长度、工具调用、多模态限制和 CUDA Graph 策略。
- 多模态服务必须显式设置 `--limit-mm-per-prompt`，不要依赖 vLLM 默认值或旧脚本默认值。
- Qwen3.5 工具调用优先使用官方推荐的 auto tool choice 与 parser 参数。
- Qwen thinking/reasoning 不要写死在部署脚本里；部署端只启用必要 parser，请求侧用 `extra_body.chat_template_kwargs.enable_thinking` 控制开关。
- 对 vLLM 这类成熟第三方库，优先读官方教程、recipe、serving 文档和 API 文档；官方文档不能解释当前版本行为时，再做只读源码追溯。
- 训练输出目录不要放在代码仓库里；放到 base checkpoint 同级或专用的大容量模型目录。
- 训练数据先做 JSONL 格式校验、字段校验和 max length 过滤，再启动训练。
- 失败、skip、OOM 或 dry-run 不应标记数据已消费；只有训练成功后才归档或标记 consumed。
- 如必须补包，先询问；确需安装单包时优先 `pip install --no-deps <pkg>`。

## 版本、官方文档与源码追溯

- `vllm`、`swift`、`transformers`、`torch` 行为随版本变化明显；参数不确定时先查当前环境版本和官方文档，再看 CLI help，最后才读源码。
- vLLM 这类知名库应优先使用官方教程、官方 recipe、serving 文档和 API 文档，不要把源码阅读作为第一反应。
- 源码适合确认当前安装版本的实际参数名、默认值、兼容分支和错误路径；不适合替代官方教程来学习推荐用法。
- 源码只用于阅读和定位问题，不要改源码，不要直接修改共享环境里的 `site-packages`；需要改库或补 patch 时，先征得用户同意，并优先 clone 源码到项目目录后 editable install。
- `inspect.getsource(...)` 适合追 Python API；CLI 参数优先看 `vllm serve --help`、`swift sft --help`、`swift rlhf --help`。

vLLM 官方阅读顺序：

1. 先确认当前安装版本：`python -c 'import vllm; print(vllm.__version__)'`。
2. 在 vLLM 官方文档站选择与当前安装版本匹配的文档版本；不要把 `stable`、`latest` 或某个历史版本链接当作固定答案。
3. 依次阅读该版本下的文档首页、OpenAI-compatible server、相关模型/场景 recipe 和 API 文档。
4. 再看当前环境 CLI help：`vllm serve --help`。
5. 最后只读追溯当前安装版本源码；不修改源码或环境。

版本匹配链接模板。把 `<matched-vllm-doc-version>` 替换为官方文档站里与当前 `vllm.__version__` 对应的版本路径；如果官方文档没有完全相同版本，选择最接近的同系列版本，并在任务记录中写明所选文档版本：

```text
VLLM_DOCS_BASE="https://docs.vllm.ai/en/<matched-vllm-doc-version>/"
VLLM_OPENAI_SERVER_DOC="${VLLM_DOCS_BASE}serving/openai_compatible_server/"
VLLM_COMPILATION_DOC="${VLLM_DOCS_BASE}api/vllm/config/compilation/"
VLLM_RECIPES_BASE="https://docs.vllm.ai/projects/recipes/en/<matched-vllm-doc-version>/"
VLLM_QWEN35_RECIPE="${VLLM_RECIPES_BASE}Qwen/Qwen3.5.html"
```

```bash
python - <<'PY'
import importlib

for name in ["vllm", "swift", "transformers", "torch"]:
    try:
        mod = importlib.import_module(name)
        print(name, getattr(mod, "__version__", "unknown"), getattr(mod, "__file__", "no __file__"))
    except Exception as exc:
        print(name, "not importable:", exc)
PY
```

```bash
vllm serve --help | sed -n '1,160p'
swift sft --help | sed -n '1,160p'
swift rlhf --help | sed -n '1,180p'
```

示例：追 vLLM serve 入口或配置类时，先定位模块路径，再按当前版本源码确认参数名：

```bash
python - <<'PY'
import inspect
import vllm

print("vllm:", vllm.__version__, vllm.__file__)

try:
    from vllm.config import CompilationConfig
    print(inspect.getsource(CompilationConfig))
except Exception as exc:
    print("CompilationConfig unavailable:", exc)
PY
```
