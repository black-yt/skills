---
name: llm-deploy-training
description: "当需要部署或训练 LLM/VLM 时使用；覆盖 vLLM OpenAI-compatible 服务、多模态输入限制、Qwen3.5 工具调用、CUDA Graph 策略，以及 ms-swift SFT/DPO/GRPO full training、数据校验、显存排错和训练检查。"
---

# LLM Deploy And Training

## 核心原则

- 部署和训练都优先复用已有环境；不要擅自升级 `torch`、`vllm`、`transformers`、`ms-swift` 或共享 conda 环境。
- 部署脚本使用环境变量配置模型路径、端口、上下文长度、工具调用、多模态限制和 CUDA Graph 策略。
- 多模态服务必须显式设置 `--limit-mm-per-prompt`，不要依赖 vLLM 默认值或旧脚本默认值。
- Qwen3.5 工具调用优先使用官方推荐的 auto tool choice 与 parser 参数。
- 训练输出目录不要放在代码仓库里；放到 base checkpoint 同级或专用的大容量模型目录。
- 训练数据先做 JSONL 格式校验、字段校验和 max length 过滤，再启动训练。
- 失败、skip、OOM 或 dry-run 不应标记数据已消费；只有训练成功后才归档或标记 consumed。
- 如必须补包，先询问；确需安装单包时优先 `pip install --no-deps <pkg>`。

## vLLM 部署核心经验

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

- **先试 1 GPU。** 在可行时先验证 1 GPU + 目标上下文长度 + 多模态配置，不要一开始就降低上下文或改成多 GPU。
- **观察日志。** vLLM 可能把 `FULL` 自动降为 `FULL_DECODE_ONLY`，只要 graph capture 完成且服务正常，可以接受。
- **失败顺序。** 先切 `ENFORCE_EAGER=1` 或降低 batch/sequence 相关参数，再考虑降低上下文长度或增加 GPU。
- **上下文长度。** `MAX_MODEL_LEN` 和 `MAX_NUM_BATCHED_TOKENS` 通常保持一致；smoke test 可先设 `MAX_NUM_SEQS=1`。

官方参考：

- https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3.5.html
- https://docs.vllm.ai/en/stable/api/vllm/config/compilation.html

## vLLM 服务脚本模板

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
[[ "${ENFORCE_EAGER}" == "1" ]] && args+=(--enforce-eager)
[[ "${ENABLE_AUTO_TOOL_CHOICE}" == "1" ]] && args+=(--enable-auto-tool-choice --tool-call-parser "${TOOL_CALL_PARSER}")

echo "[INFO] Starting vLLM on ${HOST}:${PORT}"
printf '[INFO] Command:'
printf ' %q' "${args[@]}"
printf '\n'

exec "${args[@]}"
```

## vLLM 部署验证

最少验证：

- `curl http://<host>:<port>/v1/models` 能返回模型。
- 文本 chat completion 正常。
- 工具调用能产出可解析 tool call。
- 多模态图片请求不会报 `At most 0 image(s)`。

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

128k、多模态和 CUDA Graph capture 的首轮启动可能需要几分钟。先看日志是否还在加载权重、profile 或 capture，不要只因为 `/v1/models` 尚未返回就立刻判断失败。

常见问题：

- **图片输入被拒绝。** 检查 `--limit-mm-per-prompt` 是否为 JSON 字符串，且 `image` 数量大于 0。
- **工具调用不解析。** 检查是否启用 `--enable-auto-tool-choice --tool-call-parser qwen3_coder`。
- **CUDA Graph 失败。** 先试 `ENFORCE_EAGER=1`；若想保留 graph，试 `SERVE_COMPILATION_CONFIG='{"mode": 0, "cudagraph_mode": "FULL"}'`。
- **OOM。** 先降 `MAX_NUM_SEQS`、`MAX_NUM_BATCHED_TOKENS` 或 `GPU_MEMORY_UTILIZATION`，再考虑降低 `MAX_MODEL_LEN` 或增加 GPU。

## ms-swift 训练核心原则

- 9B 级 full training 默认使用 `bf16 + DeepSpeed zero3 + save_only_model`。
- 不要把 LoRA 参数混进 full training；full training 不写 LoRA rank/alpha/target modules。
- 版本参数以当前环境的 `swift sft --help`、`swift rlhf --help` 和项目已跑通脚本为准。旧版本不支持 `--train_type full` 时再确认是否应使用 `--tuner_type full`，不要盲目同时写两个。

## 训练类型选择

- **SFT**：普通 chat messages 训练，例如 solver trace、judge trace、direct LLM stage trace。
- **DPO**：preference pairs 训练，例如 chosen/rejected challenger behavior。DPO 显存压力大于 SFT。
- **GRPO**：带 reward/rollout 的强化学习式训练，资源压力来自 rollout、生成长度、reward 计算和并发采样。先 smoke test。

SFT 和 DPO 不要共用完全相同超参。默认参考：

| 训练 | learning rate | grad acc | max length | 备注 |
| --- | ---: | ---: | ---: | --- |
| SFT | `1e-5` | `16` | `8192-10240` | 9B full 也用 zero3 |
| DPO | `5e-7` | `8` | `4096` 起步 | 9B full DPO 必须 zero3 |
| GRPO | `5e-7` 起步 | `8` 起步 | 先短 | 重点控 generation 和 reward 成本 |

## 通用环境模板

训练脚本开头：

```bash
#!/usr/bin/env bash
set -eo pipefail

export NPROC_PER_NODE="${NPROC_PER_NODE:-2}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

export CUDA_HOME="${CUDA_HOME:-/abs/path/to/cuda}"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY

MODEL_PATH="${MODEL_PATH:-/abs/path/to/base/Qwen3.5-9B}"
MODEL_TYPE="${MODEL_TYPE:-qwen3_5}"
OUTPUT_ROOT="${OUTPUT_ROOT:-/abs/path/to/models/Qwen3.5-9B-my-run}"
```

通用必备参数：

- `--model "$MODEL_PATH"`
- `--model_type "$MODEL_TYPE"`
- `--train_type full`
- `--torch_dtype bfloat16`
- `--per_device_train_batch_size 1`
- `--save_only_model true`
- `--save_total_limit 2`
- `--deepspeed zero3`
- `--dataloader_num_workers 4`
- `--dataset_num_proc 1`，数据大时可用 `4`
- `--split_dataset_ratio 0.0`，没有单独验证集时不从训练集切分

## SFT 模板

```bash
swift sft \
  --model "$MODEL_PATH" \
  --model_type "$MODEL_TYPE" \
  --train_type full \
  --dataset "/abs/path/to/model_messages_train.jsonl" \
  --split_dataset_ratio 0.0 \
  --torch_dtype bfloat16 \
  --num_train_epochs 1 \
  --per_device_train_batch_size 1 \
  --learning_rate 1e-5 \
  --gradient_accumulation_steps 16 \
  --save_strategy epoch \
  --save_total_limit 2 \
  --save_only_model true \
  --logging_steps 10 \
  --warmup_ratio 0.03 \
  --dataloader_num_workers 4 \
  --dataset_num_proc 1 \
  --max_length 8192 \
  --deepspeed zero3 \
  --output_dir "$OUTPUT_ROOT/messages" \
  --system "You are a helpful assistant."
```

SFT 默认 `learning_rate=1e-5`、`gradient_accumulation_steps=16`、`max_length=8192` 到 `10240`、`warmup_ratio=0.03` 到 `0.05`。

## DPO 模板

```bash
swift rlhf \
  --rlhf_type dpo \
  --model "$MODEL_PATH" \
  --model_type "$MODEL_TYPE" \
  --train_type full \
  --dataset "/abs/path/to/model_preference_train.jsonl" \
  --split_dataset_ratio 0.0 \
  --torch_dtype bfloat16 \
  --num_train_epochs 1 \
  --per_device_train_batch_size 1 \
  --learning_rate 5e-7 \
  --gradient_accumulation_steps 8 \
  --save_strategy epoch \
  --save_total_limit 2 \
  --save_only_model true \
  --logging_steps 10 \
  --warmup_ratio 0.05 \
  --dataloader_num_workers 4 \
  --dataset_num_proc 4 \
  --max_length 4096 \
  --rpo_alpha 0.1 \
  --deepspeed zero3 \
  --output_dir "$OUTPUT_ROOT/preference"
```

DPO 比 SFT 更容易 OOM，因为 chosen/rejected/ref/logprob 路径更重。9B full DPO 不开 zero3 很容易爆显存。默认 `learning_rate=5e-7`、`gradient_accumulation_steps=8`、`max_length=4096` 起步、`warmup_ratio=0.05`。

## GRPO 模板

GRPO 参数随 ms-swift 版本和项目插件变化大，优先参考项目已有 GRPO 脚本。不要凭空添加 reward functions、vLLM server、temperature、top_p、loss_scale 或 `gradient_checkpointing_kwargs`。

```bash
swift rlhf \
  --rlhf_type grpo \
  --model "$MODEL_PATH" \
  --model_type "$MODEL_TYPE" \
  --train_type full \
  --dataset "/abs/path/to/grpo_train.jsonl" \
  --split_dataset_ratio 0.0 \
  --torch_dtype bfloat16 \
  --num_train_epochs 1 \
  --per_device_train_batch_size 1 \
  --learning_rate 5e-7 \
  --gradient_accumulation_steps 8 \
  --save_strategy epoch \
  --save_total_limit 2 \
  --save_only_model true \
  --logging_steps 10 \
  --warmup_ratio 0.05 \
  --dataloader_num_workers 4 \
  --dataset_num_proc 4 \
  --max_length 4096 \
  --max_completion_length 1024 \
  --num_generations 4 \
  --deepspeed zero3 \
  --output_dir "$OUTPUT_ROOT/grpo"
```

GRPO 先小 batch smoke test。`max_completion_length`、`num_generations`、rollout batch 会显著影响显存和速度。如果 reward model、judge 或 vLLM rollout 同节点运行，要单独预留显存。训练失败时先缩短 generation length 和样本数，再考虑改模型、环境或算法。

## 数据格式

SFT JSONL 通常每行：

```json
{"messages":[{"role":"system","content":"..."},{"role":"user","content":"..."},{"role":"assistant","content":"..."}]}
```

DPO JSONL 常见格式一：

```json
{"messages":[{"role":"user","content":"..."}],"response":"chosen answer","rejected_response":"rejected answer"}
```

DPO JSONL 常见格式二：

```json
{"messages":[{"role":"user","content":"..."}],"chosen_messages":[{"role":"assistant","content":"..."}],"rejected_messages":[{"role":"assistant","content":"..."}]}
```

实际字段以当前 ms-swift 文档和已跑通脚本为准。关键是训练前写 validator，不要等训练跑起来才发现格式错。

## 数据校验与过滤

至少校验：

- 每行是合法 JSON。
- SFT 有 `messages`，role 顺序和内容非空。
- DPO 有 prompt、chosen 和 rejected，chosen/rejected 不为空且不相同。
- GRPO 有 reward/plugin 所需字段。
- 文本长度不超过计划的 `max_length` 或可控过滤阈值。
- 数据文件路径存在，行数符合预期，没有空文件。

示例 validator 思路：

```python
import json
import sys

path = sys.argv[1]
bad = 0
with open(path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        try:
            obj = json.loads(line)
        except Exception as e:
            print(f"bad json line={i}: {e}")
            bad += 1
            continue
        if "messages" not in obj:
            print(f"missing messages line={i}")
            bad += 1
if bad:
    raise SystemExit(f"invalid lines: {bad}")
print("jsonl ok")
```

## 训练前检查

提交真实训练前运行：

```bash
python -m compileall -q src
bash -n scripts/train_messages.sh
bash -n scripts/train_preference.sh
pytest -q
DRY_RUN=1 BASE_MODEL_PATH="$MODEL_PATH" scripts/train_messages.sh <run_id>
DRY_RUN=1 BASE_MODEL_PATH="$MODEL_PATH" scripts/train_preference.sh <run_id>
```

dry-run 输出必须能看到：

- `--train_type full`
- `--torch_dtype bfloat16`
- `--deepspeed zero3`
- `--save_only_model true`
- SFT: `--learning_rate 1e-5`
- DPO: `--learning_rate 5e-7`

同时检查：

- `MODEL_PATH` 存在且不是输出目录。
- `OUTPUT_ROOT` 在大容量模型目录，不在代码 repo。
- output dir 不存在或为空；失败输出目录不要复用。
- `NPROC_PER_NODE`、`CUDA_VISIBLE_DEVICES`、rjob `--gpu` 数一致。
- 脚本不含代理、API key、LoRA 参数或环境修改命令。

## 训练后检查

- 日志里 trainable params 应显示 full training 的大量参数，而不是 LoRA 的极低 trainable 百分比。
- 输出目录不应塞满 optimizer state；应使用 `save_only_model true`。
- 检查是否有 `logging.jsonl`、`args.json`、checkpoint 目录。
- checkpoint 位于大容量模型目录，不在代码 repo。
- 训练成功后再标记数据 consumed。
- 训练失败不要标记 consumed；失败输出目录清理或隔离。

## 显存排错顺序

1. 确认 `--torch_dtype bfloat16`。
2. 确认 full training：`--train_type full`。
3. 确认 `--deepspeed zero3`。
4. 确认真实双卡：`NPROC_PER_NODE=2`、`CUDA_VISIBLE_DEVICES=0,1`、rjob `--gpu=2`。
5. 确认 `--per_device_train_batch_size 1`。
6. 降低 `max_length`。
7. DPO/GRPO 降低 grad acc 不一定省单步显存；真正省显存通常是降低 max length、batch、generation 数或启用 zero3。
8. 设置 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`。
9. 仍 OOM 时再考虑更多 GPU、降低模型规模、缩短数据或换训练算法。

## rjob 资源建议

9B full SFT/DPO 起步用 2 GPU、44 CPU、460000 memory。GPU 任务通常不联网，依赖、模型和数据提前放到共享存储。

```bash
rjob submit \
  --name train-full-example \
  -P 1 \
  --gpu=2 \
  --cpu=44 \
  --memory=460000 \
  --charged-group=<gpu_charged_group> \
  --private-machine=<private_machine_policy> \
  --namespace=<namespace_if_required> \
  --mount=<shared_storage_mount_1> \
  --mount=<shared_storage_mount_2> \
  --image=<container_image> \
  --host-network=<true_or_false> \
  -e DISTRIBUTED_JOB=true \
  -- bash /abs/path/to/runner.sh
```

如果对应集群不需要 namespace 或 private-machine 参数，删除相应行。训练任务和服务部署对 host-network 的要求不同，按集群规则和访问方式选择。CPU 辅助循环、数据处理或联网任务另走 CPU rjob，不要和 GPU training runner 混在一起。集群分区、挂载、CPU/GPU rjob 限制和代理细节使用 `lab-cluster-1` skill。

## 最终检查清单

- SFT 和 DPO 超参不同：SFT 参考 `1e-5 / grad_acc=16 / max_length 8k-10k`，DPO 参考 `5e-7 / grad_acc=8 / max_length 4k`。
- 9B full DPO 必须 zero3。
- `save_only_model true` 已启用。
- 没有 LoRA 参数混入 full training。
- 没有修改共享 conda 环境。
- 数据成功训练前未标记 consumed。
- 输出目录在大容量模型目录。
- 失败任务目录不会被下一次训练复用。
