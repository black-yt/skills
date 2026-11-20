# DeepSeek V4.1 Flash 的 SGLang 部署与缓存感知路由

适用于长历史、多轮工具调用以及多实例共享入口。先用单实例验收模型和协议，再接入 SMG，最后按真实负载增加副本。部署和路由常驻长期 RJob，开发机负责提交、查询与维护。

## 版本和资源

- 实测模型 ID 为 `deepseek-v4.1-flash-1017`。锁定已验收的 SGLang 镜像 digest、模型 snapshot、CUDA 和参数。例子使用支持 DSPARK、Marlin、Engram 的模型专用构建，部署前在候选镜像中执行 `python3 -m sglang.launch_server --help` 并核对构建来源。不得用未核对的通用镜像或浮动 tag 推断兼容性。
- 路由实测版本为 SMG 1.15.0，release commit `82c0f1fcd0ec44e29bb5dcb80ede1cd4c7a17eb3`，配合 HAProxy 2.4.24。公开依赖可在独立 CPU 镜像或环境中固定。记录镜像 digest 或 wheel SHA256，运行 `python3 -m smg launch --help` 核对脚本参数。2026-11-21 核验的公开入口见 [PyPI 1.15.0](https://pypi.org/project/smg/1.15.0/)、[健康探测](https://lightseek.org/smg/v1.15.0/concepts/reliability/health-checks)和[前缀策略源码](https://github.com/smg-project/smg/blob/v1.15.0/model_gateway/src/policies/cache_aware.rs)。
- TP4 初始资源为 4 张同型号 H200、32 CPU、768 GiB 主机内存。实测另有 12 CPU 的可用副本，未比较其等负载吞吐。短看 quota 或空卡会遗漏单节点拓扑、CPU 和主机内存。按整组资源做任务可调度性预检。用已获授权的资源组、namespace 和挂载参数，按集群说明设置长运行期限与恢复策略。
- 保持 524288 token 总上下文。如果客户端预留 96000 输出 token，输入压缩窗口为 428288。保持双方对预算的定义一致。按排队、KV 压力和内存调准入或实例数。权重挂载只读，各实例使用独立可写缓存和日志路径，并为日志设定轮转与保留策略。

## 启动一个模型副本

[deepseek_serving.py](../scripts/deepseek_serving.py) 可打印或启动完整参数。先在 rjob 容器里检查卡数、显存、模型快照的实际配置与镜像版本。仅对已审查且固定 revision 的本地模型启用 `--trust-remote-code`。由平台的专用作业网络或网络策略限制作业间访问权限。

提交命令共用如下骨架。配置和入口脚本放在作业已授权且重启后仍可读的挂载里。模型使用 4 GPU，路由、入口和监控使用 0 GPU。对应的 CPU 与内存使用上一节或下文的实测起点。

```bash
rjob submit --name="$JOB_NAME" --namespace="$JOB_NAMESPACE" \
  --charged-group="$RESOURCE_GROUP" --cpu="$JOB_CPU" --gpu="$JOB_GPU" \
  --memory="$JOB_MEMORY_MIB" --image="$IMAGE_WITH_DIGEST" \
  --auto-restart=true --host-network=false --mount="$JOB_MOUNT" \
  -- bash "$ENTRY_SCRIPT"
```

在每个 GPU RJob 的入口运行以下代码，变量由本地部署配置提供。例子中的 cache 目录按副本隔离，保留给同一副本重启复用。

```bash
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
export SGLANG_DEFAULT_THINKING=1 SGLANG_DSV41_REASONING_EFFORT=max
export SGLANG_ENABLE_DSV41_ENGRAM_HOST_TABLE=1
export SGLANG_DSV41_ENGRAM_HOST_TABLE_LAYOUT=shared
export XDG_CACHE_HOME="$INSTANCE_CACHE"
export HF_HOME="$INSTANCE_CACHE/huggingface"
export TRITON_CACHE_DIR="$INSTANCE_CACHE/triton"
export TORCHINDUCTOR_CACHE_DIR="$INSTANCE_CACHE/torchinductor"
mkdir -p "$INSTANCE_CACHE"
exec python3 "$SKILL_DIR/scripts/deepseek_serving.py" model "$WEIGHTS_DIR" --run
```

- 固定启动组是 TP4、EP1、DP1，Marlin 主后端与 speculative 后端，DSPARK block size 5。FP4 默认后端在此构建遇到 576 维与 128 对齐冲突时，先确认错误确实来自分片与 kernel 对齐，再用已验证的 Marlin 组合，保留原模型与权重格式。
- 权重就位后还要完成 Engram、kernel 编译与 CUDA Graph 预热。结合日志、`/health`、`/get_server_info` 与一次真实生成判断就绪。核对 `served_model_name`、`tp_size`、上下文、radix cache 和 `GET /v1/models`。冷启动的较长预热需要单独的启动期限。
- 直接测试实际客户端使用的协议。包括 OpenAI Chat Completions 和原生 Anthropic Messages 里的图文、工具往返、多轮、thinking 和 SSE 正常结束。若需训练轨迹，比较路由前后后端解析后的实际模型输入。代理可能规范化 JSON 或移除未知字段。工具轮里可见 thinking 允许为空，依照实际事件与终止原因验收。

## 接入缓存感知路由

```text
客户端 → 稳定 HAProxy 入口 → SMG cache_aware
       → 每副本的 HAProxy 推理准入 → 独立 SGLang TP4
```

把 SMG 和每副本准入代理放在同一个长期 0 GPU RJob。统一入口与监控也使用长期 0 GPU RJob。实测起点为 SMG 和统一入口各 4 CPU、8 GiB，监控 1 CPU、2 GiB。使用 RJob 资源声明核对实际分配。下例的 HTTP 端口仅用于受控服务网络。对外提供服务时另配置认证和 TLS，并按调用方权限保护数据面、引擎探测和监控端口。SMG 管理面绑定 loopback。

```bash
# 每次启动使用新目录，平台重启时也能重新生成配置。
umask 077
mkdir -p "$ROUTER_CONFIG_ROOT"
attempt_dir=$(mktemp -d "$ROUTER_CONFIG_ROOT/attempt.XXXXXXXX")
ROUTER_CONFIG="$attempt_dir/config"
python3 "$SKILL_DIR/scripts/deepseek_serving.py" router \
  --worker "$WORKER_A" --worker "$WORKER_B" --worker "$WORKER_C" \
  --total 12 --output "$ROUTER_CONFIG"
exec bash "$SKILL_DIR/scripts/run_deepseek_router.sh" "$ROUTER_CONFIG"
```

`WORKER_A/B/C` 是真实 SGLang HTTP origin，形如 `http://worker-a.example.invalid:31000`。在已验证的 SMG 与 HAProxy 环境中执行。[run_deepseek_router.sh](../scripts/run_deepseek_router.sh) 前台监督两个进程，收到终止信号时先让 SMG 收尾，再软停 HAProxy。RJob 的终止宽限及上游超时也要覆盖所需排空时间。

确认候选路由的独立 `/readiness`、实际 worker 类型与负载，再生成稳定入口配置。`SMG_ORIGIN` 使用候选路由的作业服务地址和数据端口 32100。

```bash
umask 077
python3 "$SKILL_DIR/scripts/deepseek_serving.py" ingress \
  --worker "$WORKER_A" --worker "$WORKER_B" --worker "$WORKER_C" \
  --router "$SMG_ORIGIN" --total 12 > "$CANDIDATE_CFG"
haproxy -c -f "$CANDIDATE_CFG"
# 全新入口用稳定配置路径启动，后续更新按下文热加载。
# CANDIDATE_CFG 与 INGRESS_CFG 位于同一文件系统。
mv -- "$CANDIDATE_CFG" "$INGRESS_CFG"
exec haproxy -W -db -f "$INGRESS_CFG"
```

| 项目 | 示例值和验收点 |
| --- | --- |
| 前缀和负载 | `cache_aware` 匹配阈值 0.3，负载差绝对阈值 4、相对阈值 1.5，前缀余量 1024 token，启用 uncached credit。HTTP 前缀树是历史近似索引，各副本 KV 本地存放，驱逐或路由重启会降低命中 |
| 拥塞保护 | 每 2 秒读取实际 engine load，示例过载参数为 KV 0.85、等待数 1。以相同前缀压向忙副本做隔离负控，确认选择健康且有余量的同模型副本。实际负载含其他入口的请求。当所有健康副本均过载时，示例按 SMG 默认策略尝试最轻的副本，仍受连接和队列上限控制。若要主动返回 503，单独评估 `--worker-overload-shed` 与调用方重试合同 |
| 并发和探测 | 每副本最多 4 个来自该路由的推理连接，三副本总准入 12。GET 观测有独立后端，SMG readiness 使用独立端口 32102。任务并发、引擎实际运行数、代理连接数分别验收 |
| 健康和重试 | 初始设置为 30 秒探测超时、10 秒间隔、连续失败 3 次摘除、成功 2 次恢复。确认过载时探测仍可用，故障后新请求避开故障副本。SMG 与 HAProxy 的推理自动重试均关闭 |
| 协议和长流 | 请求、队列、流停滞和关闭宽限的示例预算为 8 小时。稳定入口将 `GET /v1/models` 直接发往验证过的引擎，供需要 `max_model_len=524288` 的客户端预检。比较实际返回的模型目录和原生 SSE 结束事件 |

同一会话稳定复用 system prompt、工具声明顺序及可累加的消息历史。若前缀命中突然下降，先对比真实请求中的动态头、压缩后首轮与工具 schema 变动，再查路由历史和引擎 KV 驱逐。保留实际发送的请求用于排查，协议变更走独立验收。

部署后在受保护的路由容器内查看管理面 `GET http://127.0.0.1:32103/workers`。即使设了 `--backend sglang`，仍应核对每个 worker 的实际 runtime 与负载是否可用。压测替身复用实际 `/get_load` schema，未实现的探测路由返回 404。对所有 GET 返回 200 的替身可能被误识别成另一种引擎，导致过载测试结论无效。

## 增加实例、迁移与回退

1. **选资源。** 增加一个同构 TP4 副本相当于再申请一组 4 卡，扩展请求吞吐。跨节点增大单副本 TP 需要独立评估互联、单请求延迟和模型支持。先看排队、首 token 延迟、decode 吞吐、未缓存 prefill、KV、OOM 与 5xx，明确扩容解决的瓶颈。
2. **验副本。** 同 digest、权重版本及协议先直连验收，核 TP、上下文、实际负载和健康；记录冷启动。保持现有模型作业供旧流请求完成。
3. **起候选路由。** 用同一脚本重复追加 `--worker`，在新目录和独立 CPU RJob 启动候选配置。全局上限至多为健康副本数乘以每副本已验证准入。原路径仍有流量时先减去占用的容量，旧任务停止新认领并自然排空。此时独立候选网关的连接上限仍需和旧入口的实际占用合并评估。
4. **无损接流。** 用候选路由地址生成完整入口配置，`haproxy -c` 校验，保留上一版。由持有入口的监督器在同一文件系统原子替换配置，再向该 RJob 的原生 HAProxy master 发 `SIGUSR2`。核对 master 未变、worker 已换代、既有 SSE 完整收尾以及新调用已走候选池。可用候选配置的小范围探针测故障选路，避免主动让生产实例失效。
5. **逐步放量。** 观察真实长请求和负载分布，按新旧在途数逐档调整任务准入。新副本可能需要预热缓存。出现目录不符、错误率升高或长流异常时暂停新增准入，以同一方式校验并热加载上一份入口配置。保留旧路由直到其在途流退出，然后回收闲置作业。

长期监督至少记录实际 worker 数、与旧入口合计的 running／waiting、KV、队列、每副本 5xx、重载代号和最近一次成功探测。若平台重调度会改作业 IP，使用稳定服务地址或经就绪验证后由监督器更新上游。单个入口 RJob 的自动重启只提供进程恢复，应按服务可用性要求单独设计入口冗余。

## 实测前缀复用

在隔离窗口对授权的统一入口发起四轮短输出的累加 Messages 请求，并从每个物理引擎采集未缓存 prompt histogram。 [deepseek_cache_probe.py](../scripts/deepseek_cache_probe.py)

```bash
python3 "$SKILL_DIR/scripts/deepseek_cache_probe.py" --router "$INGRESS_ORIGIN" \
  --worker "$WORKER_A" --worker "$WORKER_B" --worker "$WORKER_C"
```

每轮只有一台引擎的 histogram count 增加 1，其他引擎的 count 和 sum 均无变化时，才可用该引擎的 sum 增量估计本轮未缓存 token。需要各引擎提供单个目标 histogram series。计数被并行业务污染或发生重置时，改用独立测量窗口，别从受污染结果推断缓存命中。探针退出码 2 表示至少一轮无法归因。成功归因后再比较命中的引擎与实际 token 复用率。

历史受控运行首轮约 30058 token 冷 prefill，后三轮仅 124、142、160 token 未缓存，约 99.5% 复用。短输出墙钟约 3.94 秒降到 0.57–0.61 秒。该结果仅针对这组重复前缀、短输出和隔离测量场景。完整 512K 总窗口、96K 输出、长请求并发及任务交付效率需要各自的负载验收。
