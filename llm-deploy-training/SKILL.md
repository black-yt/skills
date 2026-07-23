---
name: llm-deploy-training
description: "当需要部署或训练 LLM/VLM 时使用；覆盖 vLLM OpenAI-compatible 服务、多模态输入限制、Qwen3.5 工具调用、thinking/reasoning 控制、CUDA Graph 策略，以及 ms-swift SFT/DPO/GRPO full training、Megatron 长序列训练、messages loss/loss_scale、数据校验、显存排错和训练检查。"
---

# LLM Deploy And Training

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 规定 LLM/VLM 部署和训练的共通安全边界，说明不要改共享环境、如何匹配 vLLM/ms-swift/transformers/torch 版本、何时读官方文档、何时只读追溯源码，并记录 ms-swift 官方文档入口。 | LLM deploy、VLM deploy、training、shared env、conda、version match、official docs、CLI help、source tracing、site-packages、vLLM、ms-swift、loss、loss_scale、transformers、torch | 触发本 skill 后默认读取；部署或训练前；准备安装/升级依赖前；参数不确定要查文档或源码前；涉及共享 conda、CUDA、torch/vLLM/ms-swift 环境时读取 | `SKILL.md` |
| 2 | 记录 vLLM OpenAI-compatible 服务的完整部署和验证经验，覆盖 `vllm serve` 参数、多模态 `limit-mm-per-prompt`、Qwen3.5 工具调用、thinking/reasoning、35B 2 卡、CUDA Graph、`extra_body`、内网访问和 SSH local port forwarding。 | vLLM、OpenAI-compatible server、`vllm serve`、multimodal、`limit-mm-per-prompt`、auto tool choice、`qwen3_coder`、Qwen thinking、reasoning parser、35B、tensor parallel、CUDA Graph、`extra_body`、SSH forwarding、`/v1/models` | 写或审查 vLLM 部署脚本前；验证 `/v1/models`/短文本/工具调用/图片输入前；配置 Qwen thinking 开关或 35B 服务前；排查 CUDA Graph、OOM、多模态报错、工具调用失败或本地访问内网服务时必须读取 | [references/vllm-deployment.md](references/vllm-deployment.md) |
| 3 | 记录 ms-swift SFT/DPO/GRPO full training 的完整训练经验，覆盖默认超参、bf16/zero3/save_only_model、messages 的 `loss`/`loss_scale`、工具调用与工具返回的 loss mask、Megatron TP/CP/SP/TE fused CE 长序列训练、JSONL validator、max length 过滤、显存排错、dry-run、训练后检查和 rjob 资源模板。 | ms-swift、SFT、DPO、GRPO、full training、Megatron、TP、CP、PP、EP、sequence_parallel、fused attention、TE fused CE、cross_entropy_loss_fusion、optimizer_cpu_offload、bf16、DeepSpeed zero3、save_only_model、save_safetensors、messages、loss、loss_scale、loss mask、tool_call、tool_response、agent template、JSONL、validator、max_length、OOM、dry-run、rjob、checkpoint、consumed data | 编写/审查 SFT、DPO 或 GRPO 脚本前；普通 HF Trainer/ms-swift + DeepSpeed ZeRO 在长样本 forward/loss/activation/logits OOM 时；准备 full training 超参前；设计 messages 训练目标前；给不同 assistant 回复段设置 loss/loss_scale 前；处理 tool_call/tool_response 数据前；训练数据格式校验前；排查 OOM、LoRA/full 混用、checkpoint 膨胀、`save_safetensors` 参数解析失败、训练失败或 consumed 标记问题时必须读取 | [references/ms-swift-training.md](references/ms-swift-training.md) |

## 核心原则

- 部署和训练都优先复用已有环境；不要擅自升级 `torch`、`vllm`、`transformers`、`ms-swift` 或共享 conda 环境。
- 部署脚本使用环境变量配置模型路径、端口、上下文长度、工具调用、多模态限制和 CUDA Graph 策略。
- 多模态服务必须显式设置 `--limit-mm-per-prompt`，不要依赖 vLLM 默认值或旧脚本默认值。
- Qwen3.5 工具调用优先使用官方推荐的 auto tool choice 与 parser 参数。
- Qwen thinking/reasoning 不要写死在部署脚本里；部署端只启用必要 parser，请求侧用 `extra_body.chat_template_kwargs.enable_thinking` 控制开关。
- 对 vLLM 这类成熟第三方库，优先读官方教程、recipe、serving 文档和 API 文档；官方文档不能解释当前版本行为时，再做只读源码追溯。
- 训练输出目录不要放在代码仓库里；放到 base checkpoint 同级或专用的大容量模型目录。
- 训练数据先做 JSONL 格式校验、字段校验和 max length 过滤，再启动训练。
- 设计 ms-swift messages 训练数据时，必须明确哪些 assistant/tool_call/tool_response 片段参与 loss；训练前用当前 template 解码 `labels` 和 `loss_scale` 验证，不凭 JSON 外观看。
- 普通 ZeRO 只能切 optimizer、grad 和参数状态；当单个样本本身太长、监督 token 太多、vocab 太大，导致 attention/activation/logits/loss OOM 时，按 `ms-swift` Megatron 路线评估 TP/CP/SP/fused CE，而不是只增加 data parallel 卡。
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

ms-swift 官方阅读入口：

1. 文档根目录：`https://swift.readthedocs.io/zh-cn/latest/`。
2. 训练、数据集、模板、loss 或 loss mask 相关问题，先确认当前安装版本：`python -c 'import swift; print(swift.__version__)'`。
3. 当前记录对照的官方 `latest` 文档版本是 `swift 4.5.0.dev0`；如果本地版本不同，必须以当前环境 `swift sft --help`、`swift rlhf --help` 和已跑通脚本为准。
4. 版本门槛要单独核对：message 级 `loss_scale` 需要 `ms-swift>=4.2.0`，数据集级 `chat_template_kwargs` 需要 `ms-swift>=4.3.0`。
5. messages 的 `loss`、`loss_scale`、agent template 和工具消息格式，优先读官方自定义数据集文档与架构文档的 Loss/Loss Scale 章节。
6. 仍不确定时，只读追溯当前安装版本源码中的 `template`、`dataset`、`loss`、`loss_scale` 相关实现；不修改源码或共享环境。

```text
MS_SWIFT_DOCS_ROOT="https://swift.readthedocs.io/zh-cn/latest/"
MS_SWIFT_ARCH_LOSS_DOC="https://swift.readthedocs.io/zh-cn/latest/Customization/Architecture.html#loss"
MS_SWIFT_CUSTOM_DATASET_DOC="https://swift.readthedocs.io/zh-cn/latest/Customization/Custom-dataset.html"
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
