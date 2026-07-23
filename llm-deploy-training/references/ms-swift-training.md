# Ms Swift Training

## 训练：ms-swift SFT / DPO / GRPO

### 版本锚点

- 当前记录对照官方 `latest` 文档版本：`swift 4.5.0.dev0`。
- message 级 `loss_scale` 需要 `ms-swift>=4.2.0`；数据集级 `chat_template_kwargs` 需要 `ms-swift>=4.3.0`。
- 使用前先运行 `python -c 'import swift; print(swift.__version__)'` 和 `swift sft --help` / `swift rlhf --help`；如果本地版本低于上述门槛，不要直接照搬相关字段。
- 已知兼容性提醒：当前 `swift==4.3.1` 配置里不要写 `save_safetensors`；该字段会被参数解析拒绝。需要控制 checkpoint 体积时继续使用已验证的 `--save_only_model true`，不要把 `save_safetensors` 加进 YAML、JSON 配置或命令行。
- 官方文档入口：`https://swift.readthedocs.io/zh-cn/latest/`；loss/loss_scale 细节见 `https://swift.readthedocs.io/zh-cn/latest/Customization/Architecture.html#loss` 和自定义数据集文档。

### 训练核心原则

- 9B 级 full training 默认使用 `bf16 + DeepSpeed zero3 + save_only_model`。
- 不要把 LoRA 参数混进 full training；full training 不写 LoRA rank/alpha/target modules。
- 版本参数以当前环境的 `swift sft --help`、`swift rlhf --help` 和项目已跑通脚本为准。旧版本不支持 `--train_type full` 时再确认是否应使用 `--tuner_type full`，不要盲目同时写两个；当前环境若是 `swift==4.3.1`，也不要加入 `save_safetensors`。

### 训练类型选择

- **SFT**：普通 chat messages 训练，例如 solver trace、judge trace、direct LLM stage trace。
- **DPO**：preference pairs 训练，例如 chosen/rejected challenger behavior。DPO 显存压力大于 SFT。
- **GRPO**：带 reward/rollout 的强化学习式训练，资源压力来自 rollout、生成长度、reward 计算和并发采样。先 smoke test。

SFT 和 DPO 不要共用完全相同超参。默认参考：

| 训练 | learning rate | grad acc | max length | 备注 |
| --- | ---: | ---: | ---: | --- |
| SFT | `1e-5` | `16` | `8192-10240` | 9B full 也用 zero3 |
| DPO | `5e-7` | `8` | `4096` 起步 | 9B full DPO 必须 zero3 |
| GRPO | `5e-7` 起步 | `8` 起步 | 先短 | 重点控 generation 和 reward 成本 |

### 通用环境模板

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

### SFT 模板

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

### DPO 模板

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

### GRPO 模板

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

### 数据格式

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

### Messages Loss 与工具返回 Loss Mask

ms-swift 对 messages 的 loss 控制分两层：

- `loss`：控制某段模型回复是否参与损失计算。官方自定义数据集文档说明，该字段主要作用于 `role="assistant"` 的模型回复部分；默认值为 `None`，`true` 表示该 assistant content 计算损失，`false` 表示不计算损失。
- `loss_scale`：控制某段模型回复或 token 片段的权重。SFT/pretrain 可用它控制 token 是否参与训练以及权重大小；RLHF 场景通常只用于控制是否参与训练。若数据里出现大于 `1` 的 loss scale，训练参数需要确认是否设置 `--is_binary_loss_scale false`。
- 命令行 `--loss_scale`：控制 template 层面的整体策略，例如 `default`、`last_round`、`all` 或额外的 ignore/regex 策略。数据中的 `loss` / `loss_scale` 优先级高，但仍会受到 template 和其他 loss_scale 策略的影响。

常见 SFT 训练目标：

- 只训练最后一轮答案：使用 `--loss_scale last_round`，或只给最后一个 assistant 设置 `loss: true`，其他 assistant 设置 `loss: false`。
- 训练多轮 assistant：使用默认 assistant-only 策略，或按每个 assistant turn 显式设置 `loss`。
- 提高关键段权重：对某个 assistant message 设置 `loss_scale`，例如 reasoning 设 `1.0`、final answer 设 `2.0`；同时确认 `--is_binary_loss_scale false`。
- 忽略空 thinking 或特定模板片段：优先使用当前版本内置的 `--loss_scale` 策略；内置策略不满足时，再考虑自定义 `LossScale`。

SFT 示例。第一轮 assistant 不训练，第二轮 assistant 训练；第二个样本把 reasoning 和最终回答拆成两个 assistant 片段，并给最终回答更高权重：

```json
{"messages":[{"role":"user","content":"你好"},{"role":"assistant","content":"你好，有什么可以帮助你的吗？","loss":false},{"role":"user","content":"1+1等于几？"},{"role":"assistant","content":"等于2","loss":true}]}
{"messages":[{"role":"user","content":"请解题"},{"role":"assistant","content":"<think>\n...\n</think>\n","loss_scale":1.0},{"role":"assistant","content":"最终答案是 A。","loss_scale":2.0}]}
```

工具调用数据要先区分三类文本：

- `user` / `system`：输入条件，不应训练为模型输出。
- `tool_call`：通常是模型要学会生成的工具调用内容；如果训练目标包含函数名和参数生成，需要监督它。
- `tool` / `tool_response`：工具或环境返回的观察结果，不是模型自己生成的文本，默认应被 mask，不应训练模型复述工具返回。
- `assistant`：模型读完工具返回后的自然语言最终回答，通常需要训练。

官方 agent template 支持 `tool_call` 和 `tool`/`tool_response` 格式化。当前文档还提醒：如果对连续的 `tool_call` 设置 `loss` / `loss_scale`，只有最前面的 `tool_call` 配置生效。因此，连续工具调用要么拆清楚样本结构，要么用当前 template debug 后再决定是否需要自定义 template/loss_scale。

工具返回 mask 的推荐策略：

- 保持工具返回使用 `role="tool"` 或 `role="tool_response"`，不要把工具返回伪装成 assistant 回复。
- 不要使用会把非 assistant 文本也纳入训练的全局策略，除非已经确认 tool_response 仍然被 mask。
- 如果数据转换器把工具返回写进了 assistant content，必须拆回 `tool_response`，或对对应 assistant 段设置 `"loss": false`。
- 如果某个模型模板会把 tool_response 序列化到 assistant label 中，使用内置/自定义 `loss_scale` 或自定义 template，把工具返回 span 的 loss scale 置为 `0`。
- 训练前抽样检查 `labels` 解码内容；如果工具返回中的 JSON、日志、检索结果或 observation 文本出现在 `labels` 里，说明 mask 没有生效，不能启动训练。

Agent SFT 示例。这里训练模型生成工具调用和最终回答，但工具返回本身应由 template/loss mask 排除；实际是否排除必须用后面的 debug 脚本确认：

```json
{"tools":"[{\"type\":\"function\",\"function\":{\"name\":\"get_weather\",\"description\":\"Get weather by city\",\"parameters\":{\"type\":\"object\",\"properties\":{\"city\":{\"type\":\"string\"}},\"required\":[\"city\"]}}}]","messages":[{"role":"user","content":"北京和上海今天的天气情况"},{"role":"tool_call","content":"{\"name\":\"get_weather\",\"arguments\":{\"city\":\"北京\"}}","loss":true},{"role":"tool_call","content":"{\"name\":\"get_weather\",\"arguments\":{\"city\":\"上海\"}}"},{"role":"tool_response","content":"{\"city\":\"北京\",\"weather\":\"sunny\"}"},{"role":"tool_response","content":"{\"city\":\"上海\",\"weather\":\"rainy\"}"},{"role":"assistant","content":"北京今天晴，上海今天有雨。","loss":true}]}
```

Loss mask debug 必须使用当前模型、当前 template 和当前 ms-swift 版本，不要只看 JSONL：

```python
from swift import get_processor, get_template

data = {
    "tools": "[{\"type\":\"function\",\"function\":{\"name\":\"get_weather\",\"description\":\"Get weather by city\",\"parameters\":{\"type\":\"object\",\"properties\":{\"city\":{\"type\":\"string\"}},\"required\":[\"city\"]}}}]",
    "messages": [
        {"role": "user", "content": "北京和上海今天的天气情况"},
        {"role": "tool_call", "content": "{\"name\":\"get_weather\",\"arguments\":{\"city\":\"北京\"}}", "loss": True},
        {"role": "tool_call", "content": "{\"name\":\"get_weather\",\"arguments\":{\"city\":\"上海\"}}"},
        {"role": "tool_response", "content": "{\"city\":\"北京\",\"weather\":\"sunny\"}"},
        {"role": "tool_response", "content": "{\"city\":\"上海\",\"weather\":\"rainy\"}"},
        {"role": "assistant", "content": "北京今天晴，上海今天有雨。", "loss": True},
    ],
}

processor = get_processor("/abs/path/to/model")
template = get_template(processor, loss_scale="default")
# 如果当前模型需要 agent_template，按官方文档和已跑通脚本指定：
# template = get_template(processor, agent_template="qwen3_5", loss_scale="default")
template.set_mode("train")
inputs = template.encode(data)

print("[INPUT_IDS]")
print(template.safe_decode(inputs["input_ids"]))
print("[LABELS]")
print(template.safe_decode(inputs["labels"]))
print("[LOSS_SCALE]")
print(inputs.get("loss_scale"))
```

检查标准：

- `LABELS` 中应出现需要学习的 assistant answer。
- 若要训练 tool call，`LABELS` 中应出现目标 tool call 的函数名和参数。
- `LABELS` 中不应出现 tool_response 的原始 JSON、日志、网页内容、检索结果或 observation。
- 如果 `LOSS_SCALE` 中有大于 `1` 的权重，训练脚本同步设置 `--is_binary_loss_scale false`。
- 切换 `--loss_scale default`、`last_round`、`all` 或自定义策略后，重新跑 debug；不要复用旧结论。

如果内置策略不够，需要自定义 loss scale：

- 自定义 `LossScale.get_loss_scale(context, **kwargs)`，返回切分后的字符串列表和每段权重。
- 简单关键词或正则匹配可参考官方 `ConfigLossScale` 的 JSON 配置思路。
- 对工具返回做 mask 时，应匹配 template 序列化后的工具返回边界，而不是原始 JSONL 中的字段名。
- 自定义后必须抽样打印 `labels` 与 `loss_scale`，确认 tool_response span 权重为 `0`。
- 不要直接修改 ms-swift 源码或共享环境；需要插件化扩展时，使用项目目录里的外置插件，并先征得用户同意。

### Megatron 长序列训练判断与配置

Megatron 不应该作为所有训练的默认选项。先判断 OOM 来源，再决定是否切到 Megatron。

什么时候需要 Megatron：

- 单个样本本身太大，序列很长、监督 token 很多、vocab 很大。
- 普通 HF Trainer / ms-swift + DeepSpeed ZeRO 即使用多卡，也在 forward、loss、activation、logits 计算处 OOM。
- OOM 出现在 `logits.float()`、cross entropy、attention 中间张量、activation 或长序列相关计算，而不是单纯 optimizer state。
- 最长样本达到 64k、100k、128k 级别，并且 label/supervised token 很多。
- 加普通 data parallel 卡没有本质帮助，因为每个 DP rank 仍要处理完整长样本。

什么时候不需要 Megatron：

- 4k、8k、16k 普通 SFT。
- 主要问题是 optimizer state 太大。
- 可以通过 LoRA、gradient checkpointing、bf16、DeepSpeed ZeRO2/3、降低 batch 或降低 `max_length` 解决。
- 训练规模小且调试复杂度不值得增加。

Megatron 的定位：

- ZeRO 主要切 optimizer、grad 和参数状态。
- ZeRO 不能自动把一条 100k token 样本的 attention、activation、logits/loss 计算切开。
- Megatron 解决的是模型计算和单样本长序列本身太大的问题。
- Megatron 会增加安装、并行组合、checkpoint 和调试复杂度，不该一上来就用。

先做 loss logits 显存估算：

```text
loss logits 内存 ≈ supervised_tokens × vocab_size × dtype_bytes
```

这次遇到的最长样本估算：

```text
82490 supervised tokens × 248320 vocab × 4 bytes ≈ 76.31 GiB
```

这个量级下，HF loss 在 `logits.float()` 处 OOM 是必然的。此时继续只加 ZeRO 或普通 DP 卡不是第一解法，应考虑 Megatron 的 TP/CP/SP/fused CE。

Megatron 的核心并行关系：

```text
总 GPU 数 ≈ TP × CP × PP × EP × DP
```

其中 `DP` 是数据并行副本数。这次 4 卡全部用于模型与长序列切分：

```text
TP=2 × CP=2 × PP=1 × EP=1 = 4
```

也就是没有额外 DP。

TP，tensor parallel：

- 把大矩阵、attention projection、MLP 和输出 vocab projection 切到多张卡上。
- 适合模型大、vocab 大、单卡 projection/loss 压力大的场景。
- 先从 `TP=2` 起步，稳定后再试 `TP=4`。
- TP 越大，单卡显存越低，但通信越多。
- TP 通常要能适配 hidden size、head 数、vocab projection 等结构。
- 对 MoE 或大 vocab 模型，TP 对 output layer 和 CE 前后压力很关键。

CP，context parallel：

- 把长 context/sequence 维度切开。
- 对 64k、128k、100k+ 长样本，CP 往往比继续加 DP 更有用。
- 如果 OOM 根源是单条长序列，优先考虑 CP。
- 4 卡可以试 `TP=2, CP=2`。
- 8 卡可以试 `TP=2, CP=4` 或 `TP=4, CP=2`，需要 profile 比较显存和速度。
- CP 增大会增加跨卡通信，但它解决的是普通 ZeRO 不解决的长上下文问题。

PP，pipeline parallel：

- 按层切模型。例如 40 层模型，`PP=4` 可以理解为每组卡放 10 层。
- 模型层数或参数太大，TP/CP 后仍放不下时再考虑 PP。
- GPU 数足够多，且 microbatch 足够多能填满流水线时，PP 才更有意义。
- `global_batch_size=1` 或 microbatch 很少时，不优先用 PP。
- 只有 4 卡且已经要给 TP/CP 时，不优先用 PP。
- 如果主要瓶颈是长序列 logits/loss，而不是模型层放不下，PP 不是第一选择。
- 这次用 `PP=1`，表示不启用 pipeline。

EP，expert parallel：

- MoE 模型按专家切分。
- 可以减少每卡 expert 负担，但会引入 MoE token dispatch、all-to-all 和路由通信。
- 4 卡先别急着开 EP，优先 TP/CP。
- 当 GPU 更多，且 MoE expert 成为显存或计算瓶颈时再试。
- 开 EP 前要做短 profile，看通信是不是拖垮速度。
- EP 不是长上下文 OOM 的第一解法。

`sequence_parallel=true`：

- SP 通常和 TP 搭配，把部分 sequence 相关 activation、LayerNorm、residual 等张量进一步切分。
- 长序列训练建议开启。
- SP 不是单独解决一切，但和 TP/CP 组合很关键。

`attention_backend` 选择：

- 优先使用当前环境真实可用的 fused/flash attention，不凭感觉写。
- 当前实测链路使用 `attention_backend=fused`。
- 原因是当前环境没有可用 `flash-attn`；如果写 `flash`，会触发 `flash_attention_2` 依赖并失败。
- `fused` 走 Megatron/Transformer Engine 可用路径，能减少 attention 中间张量物化。
- 有稳定 flash-attn wheel 且版本匹配时，可以 profile `flash`。
- 没有 flash-attn 或安装风险高时，用 `fused`。
- 不要为了“看起来更快”临时源码编译 flash-attn，避免破坏共享环境。

cross entropy / loss kernel：

- 长序列 + 大 vocab 时，cross entropy kernel 是硬门槛。
- 如果 HF loss OOM，先不要只加 ZeRO。
- 先计算 `label_tokens × vocab × bytes`。
- Megatron native CE 可以试，但大 vocab 长序列可能仍不够。
- TE fused CE 是优先 profile 的路线。

实测链路：

```text
HF loss: logits.float() 额外约 76.31 GiB，OOM
Megatron native fused CE: 仍额外约 26.45 GiB，4 卡 OOM
TE fused CE: 成功
```

关键配置：

```text
cross_entropy_loss_fusion=true
cross_entropy_fusion_impl=te
```

optimizer 选择：

```text
optimizer=adam
optimizer_cpu_offload=true
optimizer_offload_fraction=1.0
use_distributed_optimizer=true
```

选择原因：

- 降低 GPU optimizer state 压力。
- 避开 TE FusedAdam 在 LoRA + MoE 大量小 tensor 场景下的 `Maximum number of tensors reached` 问题。

代价：

- optimizer step 可能变慢。
- 小数据 SFT 可以接受。
- 大规模训练时要重新 profile CPU offload 的吞吐，不要默认认为它总是划算。

学习率经验：

- Megatron 把显存问题解决后，数值稳定性仍然要单独处理。
- 第一次正式跑 `LR=1e-4`，第 1 步后出现 NaN grad norm。
- 降到下面配置后正式 `39/39` 成功：

```text
LR=1e-5
MIN_LR=1e-6
CLIP_GRAD=0.5
```

教学建议：

- 长轨迹 SFT，尤其 MoE + LoRA，不要默认用过高 LR。
- 先做 1-step 最长样本 profile。
- 再做 2-step 或 5-step 正式数据 profile。
- 只要出现 NaN，先降 LR、加 clip、检查 loss mask，不要直接扩大 GPU。

配置骨架。字段名按当前已跑通经验记录；写入具体 ms-swift 脚本前，仍要用当前版本 `swift sft --help`、项目配置模板和日志确认真实参数名：

```text
tensor_model_parallel_size=2
context_parallel_size=2
pipeline_model_parallel_size=1
expert_model_parallel_size=1
sequence_parallel=true
attention_backend=fused
cross_entropy_loss_fusion=true
cross_entropy_fusion_impl=te
optimizer=adam
optimizer_cpu_offload=true
optimizer_offload_fraction=1.0
use_distributed_optimizer=true
learning_rate=1e-5
min_lr=1e-6
clip_grad=0.5
```

推荐调参流程：

1. 先确认数据 mask：decode labels，确保 tool response 是 `-100`。
2. 统计最长样本：`input_len`、`label_tokens`、vocab size。
3. 用公式估算 HF loss 显存。
4. 普通 HF/ZeRO 路线做 smoke，但不要硬跑正式长轨迹。
5. Megatron 先跑最长样本 1-step profile。
6. 如果 CE OOM，换 TE fused CE。
7. 如果 optimizer step 报错，开 CPU offload。
8. 如果第 1 步后 NaN，降 LR、加 grad clip、做 2-step profile。
9. profile 稳定后再提交正式 1 epoch。
10. 成功后检查 checkpoint 大小、曲线、无 optimizer/rng 文件。

一句话总结：

```text
ZeRO 解决“训练状态太大”；
Megatron 解决“模型计算和单样本长序列本身太大”。
```

当瓶颈是 100k token 轨迹、巨大 vocab loss、attention/activation/logits OOM 时，就该考虑 Megatron。

### 数据校验与过滤

至少校验：

- 每行是合法 JSON。
- SFT 有 `messages`，role 顺序和内容非空。
- 如果使用 `loss` / `loss_scale`，确认它们只出现在当前 ms-swift 版本和 template 支持的位置。
- Agent 数据中 `tool_response` / `tool` 不应被转换成需要训练的 assistant 文本，除非明确就是要让模型复述工具结果。
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

Agent/tool 数据额外检查：

```python
import json
import sys

path = sys.argv[1]
bad = 0

for i, line in enumerate(open(path, "r", encoding="utf-8"), 1):
    obj = json.loads(line)
    messages = obj.get("messages", [])
    for j, message in enumerate(messages):
        role = message.get("role")
        content = message.get("content", "")
        if role in {"tool", "tool_response"} and message.get("loss") is True:
            print(f"line={i} msg={j}: tool response should not set loss=true")
            bad += 1
        if role in {"tool", "tool_response"} and not content:
            print(f"line={i} msg={j}: empty tool response")
            bad += 1
        if role == "assistant" and "TOOL_RESULT:" in content and message.get("loss") is not False:
            print(f"line={i} msg={j}: assistant contains tool result but is not masked")
            bad += 1

if bad:
    raise SystemExit(f"invalid agent/tool rows: {bad}")
print("agent/tool rows ok")
```

### 训练前检查

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
- 对含 `loss` / `loss_scale` / tool messages 的数据，至少抽样 3-5 条跑 template debug，确认 labels 和 loss_scale 符合预期。
- 对工具返回 mask，必须确认 tool_response 原文没有出现在 labels 中。
- 对长轨迹样本，统计 `input_len`、`label_tokens` 和 vocab size；如果 loss logits 估算已经达到几十 GiB，不要硬跑普通 HF/ZeRO 正式训练，先做 Megatron 1-step profile。

### 训练后检查

- 日志里 trainable params 应显示 full training 的大量参数，而不是 LoRA 的极低 trainable 百分比。
- 输出目录不应塞满 optimizer state；应使用 `save_only_model true`。
- 检查是否有 `logging.jsonl`、`args.json`、checkpoint 目录。
- checkpoint 位于大容量模型目录，不在代码 repo。
- 训练成功后再标记数据 consumed。
- 训练失败不要标记 consumed；失败输出目录清理或隔离。

### 显存排错顺序

1. 确认 `--torch_dtype bfloat16`。
2. 确认 full training：`--train_type full`。
3. 确认 `--deepspeed zero3`。
4. 确认真实双卡：`NPROC_PER_NODE=2`、`CUDA_VISIBLE_DEVICES=0,1`、rjob `--gpu=2`。
5. 确认 `--per_device_train_batch_size 1`。
6. 降低 `max_length`。
7. DPO/GRPO 降低 grad acc 不一定省单步显存；真正省显存通常是降低 max length、batch、generation 数或启用 zero3。
8. 设置 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`。
9. 如果 OOM 来自单条超长样本的 attention/activation/logits/loss，按 Megatron TP/CP/SP/TE fused CE 路线 profile，而不是只增加普通 DP 卡。
10. 仍 OOM 时再考虑更多 GPU、降低模型规模、缩短数据或换训练算法。

### rjob 资源建议

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

### 最终检查清单

- SFT 和 DPO 超参不同：SFT 参考 `1e-5 / grad_acc=16 / max_length 8k-10k`，DPO 参考 `5e-7 / grad_acc=8 / max_length 4k`。
- 9B full DPO 必须 zero3。
- `save_only_model true` 已启用。
- 没有 LoRA 参数混入 full training。
- 没有修改共享 conda 环境。
- 数据成功训练前未标记 consumed。
- 输出目录在大容量模型目录。
- 失败任务目录不会被下一次训练复用。
- 如果使用 Megatron 长序列路线，已记录 TP/CP/PP/EP/DP 组合、attention backend、CE fusion 实现、optimizer offload、LR/clip 和 profile 结果。
