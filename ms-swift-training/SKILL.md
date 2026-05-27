---
name: ms-swift-training
description: "当需要用 ms-swift 进行 LLM 训练或编写/审阅训练脚本时使用，覆盖 SFT、DPO、GRPO，尤其是 9B 级 full training 的 bf16、DeepSpeed zero3、save_only_model、数据 JSONL 校验、max length 过滤、显存排错、训练前 dry-run、训练后 checkpoint 检查、rjob GPU 资源脚本和避免破坏共享 conda 环境。"
---

# ms-swift Training

## 核心原则

- 9B 级 full training 默认使用 `bf16 + DeepSpeed zero3 + save_only_model`。
- 不要把 LoRA 参数混进 full training；full training 不写 LoRA rank/alpha/target modules。
- 输出目录不要放在代码仓库里；放到 base checkpoint 同级或专用的大容量模型目录。
- 训练数据先做 JSONL 格式校验、字段校验和 max length 过滤，再启动训练。
- 失败、skip、OOM 或 dry-run 不应标记数据已消费；只有训练成功后才归档或标记 consumed。
- 不要修改共享 conda 环境，不要升级 `torch`、`vllm`、`transformers`、`ms-swift`。如必须补包，先询问；确需安装单包时优先 `pip install --no-deps <pkg>`。
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

9B full SFT/DPO 起步用 2 GPU、44 CPU、460000 memory。GPU 任务不联网，依赖、模型和数据提前放到共享存储。

```bash
rjob submit \
  --name train-full-example \
  -P 1 \
  --gpu=2 \
  --cpu=44 \
  --memory=460000 \
  --charged-group=scieval_gpu \
  --private-machine=group \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -e DISTRIBUTED_JOB=true \
  -- bash /abs/path/to/runner.sh
```

如果是 CPU evo loop，另走 CPU rjob，不要和 GPU training runner 混在一起。集群分区、挂载、CPU/GPU rjob 限制和代理细节使用 `lab-cluster-1` skill。

## 最终检查清单

- SFT 和 DPO 超参不同：SFT 参考 `1e-5 / grad_acc=16 / max_length 8k-10k`，DPO 参考 `5e-7 / grad_acc=8 / max_length 4k`。
- 9B full DPO 必须 zero3。
- `save_only_model true` 已启用。
- 没有 LoRA 参数混入 full training。
- 没有修改共享 conda 环境。
- 数据成功训练前未标记 consumed。
- 输出目录在大容量模型目录。
- 失败任务目录不会被下一次训练复用。
