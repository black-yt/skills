# Rjob Tasks

## 目录

- [rjob 工作流](#rjob-工作流)
- [rjob 查询、事件与卡位巡检](#rjob-查询事件与卡位巡检)
- [rjob CPU 任务](#rjob-cpu-任务)
- [rjob GPU 任务](#rjob-gpu-任务)
- [作业脚本骨架](#作业脚本骨架)

## rjob 工作流

1. 在个人项目根目录下准备 `command.sh`，例如 `/mnt/shared-storage-user/xuwanghan/projects/<project>/jobs/<name>.sh`。
2. 脚本内不要写真实 secret。用环境变量、secret 文件或运行时注入。
3. 提交前检查 `--name`、GPU/CPU/memory、分区、namespace、挂载、镜像、端口和工作目录。
4. 非交互 SSH 提交时，在同一个远端 shell 中先执行 `source /etc/profile.d/ssh-init.sh 2>/dev/null || true`。
5. 先用 `rjob submit --dry-run true ...` 做语法和资源字段检查；确认无误后去掉 `--dry-run true` 正式提交。
6. 用 `rjob submit ... -- bash command.sh` 提交。
7. 提交后记录 job name、job id、worker id 或服务 IP；只摘录必要日志，不复制 secret。
8. 2026-06-05 当前 CPU rjob 优先使用 scieval `scieval_cpu_task` + `--namespace=ailab-scieval`；查询、日志和删除使用临时前缀 `KUBEBRAIN_NAMESPACE=ailab-scieval`。ai4sdata CPU rjob 模板是历史已验证模板，当前 ai4sdata 无 CPU/GPU 资源时不要直接提交。GPU rjob 可使用 ai4sdata 或 scieval；scieval GPU job 的查询、日志和删除同样使用临时前缀 `KUBEBRAIN_NAMESPACE=ailab-scieval`。

最小 dry-run，用于生成并检查 YAML。2026-06-05 当前 CPU rjob 默认使用 scieval：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rjob submit --dry-run true \
  --name codex-skill-dryrun \
  -P 1 \
  --cpu=1 \
  --memory=4000 \
  --charged-group=scieval_cpu_task \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=false \
  -- bash -lc "echo dryrun"
```

ai4sdata CPU 最小 dry-run，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要直接提交：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rjob submit --dry-run true \
  --name codex-skill-dryrun \
  -P 1 \
  --cpu=1 \
  --memory=4000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -- bash -lc "echo dryrun"
```

## rjob 查询、事件与卡位巡检

在开发机上做 rjob 查询时，先确保 `rjob` 环境已加载：

```bash
source /etc/profile.d/ssh-init.sh 2>/dev/null || true
```

常用只读查询命令：

```bash
# 列出指定 namespace 下的 rjob
KUBEBRAIN_NAMESPACE=<namespace> rjob list

# 查看某个 job 的状态、任务副本和调度信息
KUBEBRAIN_NAMESPACE=<namespace> rjob get <job-name>

# 查看排队、失败、quota、调度等事件原因
KUBEBRAIN_NAMESPACE=<namespace> rjob events <job-name>

# 查看已有日志；Pending/Inqueue 任务可能还没有日志
KUBEBRAIN_NAMESPACE=<namespace> rjob logs job <job-name> --tail-lines 100
```

scieval 的 namespace 通常是 `ailab-scieval`。ai4sdata 通常不需要 namespace 前缀；如果某个命令查不到任务，先核对任务实际提交的 namespace 和 charged group。

数据源要分层，不要把 `rjob` 信息和网页监控信息混成一个来源：

- `rjob` / rjob SDK 负责任务层信息：运行/排队状态、提交者、申请 GPU 数、运行时长、replica、节点、pod 名、任务命令和最近事件。
- 集群管理网页或监控后端负责监控层信息：GPU 计算利用率、显存 used/free、显存占用率、功率、温度、节点、卡号、namespace、pod。
- 两边通常通过 `pod`、`replica name`、`namespace` 或监控 label 映射。只有监控中的 pod 能匹配到 rjob replica 时，才能把卡级指标归属到具体 rjob 和提交者。
- 无法映射到 rjob 的 pod 不要硬归因给某个用户或任务；报告中应单独归为“其他占用”或只显示 namespace/pod。
- `rjob` 卡位占用率不是 GPU 计算利用率。不要用 running replica 的 GPU 数推断训练是否高效；真实利用率、显存、功率和温度必须来自监控系统或任务自上报。

`rjob get` 有时会把 `Inqueue` 显示成 `Unknown`。自动巡检时不要只解析 CLI 文本，应优先读底层对象的 `status.phase`、`status.conditions` 和 replica 状态。

结构化查询通常需要开发机系统 Python 中可用的 `brainpp.rjob`。不要默认使用 conda Python；先做只读 import 检查：

```bash
/usr/bin/python3 - <<'PY'
from brainpp.rjob import RJobClient
print("brainpp.rjob ok")
PY
```

通用结构化查询入口：

```python
from brainpp.rjob import RJobClient

client = RJobClient(
    cluster_entry="[CLUSTER_ENTRY]",
    namespace="[NAMESPACE]",
    verifyssl=False,
)
```

查询 GPU 节点时，按节点组 label 获取 node，并只读取调度和资源字段：

```python
nodes = client.corev1_api.list_node(
    label_selector="nodeGroup=[GPU_NODE_GROUP]",
    _request_timeout=30,
).items

for node in nodes:
    name = node.metadata.name
    gpu_type = node.metadata.labels.get("GPUType", "")
    total_gpu = int(node.status.allocatable.get("nvidia.com/gpu", 0))
    schedulable = not bool(node.spec.unschedulable)
```

可以得到：

```text
GPU 总卡数 = sum(node.status.allocatable["nvidia.com/gpu"])
节点型号 = node.metadata.labels["GPUType"]
节点是否可调度 = not node.spec.unschedulable
```

查询 GPU rjob 和 replica 时，用 rjob resource type 与 quota group label 做筛选：

```python
label_selector = (
    "kubebrain.brainpp.cn/resourcetype=rjob,"
    "quotagroup.brainpp.cn/quotagroup=[GPU_QUOTA_GROUP]"
)

rjobs = client.api.list_namespaced_custom_object(
    group="rjob.brainpp.cn",
    version="v1alpha1",
    namespace="[NAMESPACE]",
    plural="rjobs",
    label_selector=label_selector,
    resource_version="0",
    _request_timeout=30,
).get("items", [])

replicas = client.api.list_namespaced_custom_object(
    group="rjob.brainpp.cn",
    version="v1alpha1",
    namespace="[NAMESPACE]",
    plural="replicas",
    label_selector=label_selector,
    resource_version="0",
    _request_timeout=30,
).get("items", [])
```

rjob 常用字段：

```text
metadata.name
metadata.labels["kubebrain.brainpp.cn/creator"]
metadata.labels["quotagroup.brainpp.cn/quotagroup"]
metadata.annotations["kubebrain.brainpp.cn/showname"]
metadata.annotations["rjob.brainpp.cn/job-command"]
status.phase
status.conditions
spec.taskSpecs
```

replica 常用字段：

```text
metadata.name
metadata.labels["rjob.brainpp.cn/rjob-name"]
metadata.labels["kubebrain.brainpp.cn/creator"]
status.phase
status.nodeName
status.podIP
status.startTime
spec.containers[].resources.limits["nvidia.com/gpu"]
```

计算申请 GPU 数时，排队任务可能还没有 running replica，所以必须从 rjob spec 计算：

```text
requested_gpu = sum(taskSpec.replicas * container.resources.limits["nvidia.com/gpu"])
```

也就是遍历：

```text
rjob.spec.taskSpecs[*].replicas
rjob.spec.taskSpecs[*].template.spec.containers[*].resources.limits["nvidia.com/gpu"]
```

计算运行占用 GPU 时，用 running replica 计算：

```text
running_gpu = sum(replica_gpu for replica.status.phase == "Running")
```

计算节点卡位：

```text
node_occupied[nodeName] += replica_gpu
node_free = node_total - node_occupied
```

整体卡位：

```text
总卡 = sum(GPU node allocatable gpu)
占用卡 = sum(running replica gpu)
空卡 = 总卡 - 占用卡
卡位占用率 = 占用卡 / 总卡
空卡率 = 空卡 / 总卡
```

注意：这是“卡位占用率”，不是 GPU 计算利用率。rjob/replica/node 结构化查询通常拿不到真实 GPU 利用率、显存占用、功率和温度；这些需要监控系统、DCGM/Prometheus、管理员权限或训练任务自上报。

排队/启动中的 phase 建议按集合判断：

```python
QUEUE_PHASES = {
    "Inqueue",
    "Pending",
    "Starting",
    "Creating",
    "Created",
    "Queued",
    "Queueing",
}
```

排队任务数和排队 GPU 需求：

```text
queued_jobs = rjob.status.phase in QUEUE_PHASES
queued_gpu = sum(rjob_requested_gpu(job) for queued jobs)
```

等待时长可以从 `status.conditions` 中找 `Inqueue`、`Pending`、`Starting` 等 condition，优先使用对应 `lastTransitionTime` 作为开始时间。

成员维度汇总按 `kubebrain.brainpp.cn/creator` 聚合：

```text
提交者
运行任务数
运行占用 GPU
排队任务数
排队申请 GPU
```

排序建议：

```text
先按运行占用 GPU 降序
再按排队 GPU 降序
再按提交者名字
```

排队原因优先看：

```bash
KUBEBRAIN_NAMESPACE=<namespace> rjob events <job-name>
```

典型 quota 问题形如：

```text
insufficient group quota: cpu : <used>/<quota>
insufficient group quota: nvidia.com/gpu : <used>/<quota>
```

这说明任务卡在资源 quota 或调度约束，不代表任务脚本本身已经执行失败。

重要坑点：

- `rjob logs` 对 Pending/Inqueue replica 可能报 `TypeError: 'NoneType' object is not iterable`；这通常是 CLI 在无日志时处理不好，不代表任务脚本错了。
- 不要在 `set -u` 下直接 `source /jobutils/scripts/worker_init.sh`。部分环境初始化脚本可能读取未定义变量，导致 `unbound variable`；作业脚本默认用 `set -eo pipefail`，或在 source 前临时关闭 nounset。
- 0 GPU 的 GPU 分区任务可能调度到 GPU 节点，但容器里没有 `nvidia-smi`、没有 `/dev/nvidia*`，`CUDA_VISIBLE_DEVICES` 为空；不能用 0 GPU 任务绕过隔离去查 GPU 利用率。
- GPU 分区通常没有外网；外部 webhook/API 通知更适合放在开发机、CPU worker 或 CPU rjob。GPU 任务只写共享存储或提供内网数据，避免在 GPU 任务里依赖外网通知。
- 需要周期性巡检或发送外部通知时，优先放在 CPU rjob 或开发机轻量进程中。若放在 CPU rjob，使用 `PYTHONUNBUFFERED=1` 或等价方式保证日志及时刷新，避免 `rjob logs` 长时间看不到输出。
- 正式启用巡检前先跑 smoke rjob：只做 dry-run 或只生成报告，不发送外部通知；确认能读取 rjob、读取监控后端、生成报告并退出后，再开启循环和通知。

可稳定得到的巡检信息：

```text
GPU 总卡数
各节点总卡 / 占用卡 / 空卡
运行中 GPU 任务
排队或启动中 GPU 任务
每个任务申请 GPU 数
每个任务实际运行占用 GPU 数
提交者 creator
任务所在节点
运行时长 / 排队时长
排队原因 / 最近状态
成员维度汇总
```

合并成报告时，建议按以下顺序组织：

1. 任务层汇总：总卡数、占用卡、空卡、运行任务、排队任务、成员维度汇总。
2. rjob 明细：运行中任务、排队/启动中任务、申请 GPU、实际运行 GPU、节点、运行/等待时长、最近事件。
3. 监控明细：已映射到 rjob 的 GPU 利用率、显存、功率、温度；未映射的 namespace/pod 单独列为其他占用。
4. 提醒项：连续多轮低利用率、低显存占用、低功率、空卡率异常或排队时间过长。不要只凭单轮瞬时值下结论。

## rjob CPU 任务

2026-06-05 当前 CPU rjob 默认使用 scieval。scieval CPU rjob 已实测提交、运行、日志读取和删除链路；查询、日志和删除必须带 `KUBEBRAIN_NAMESPACE=ailab-scieval`。ai4sdata CPU rjob 模板保留为 2026-05 历史已验证模板，当前 ai4sdata 没有 CPU/GPU 可用资源时不要直接提交。

scieval CPU rjob 最小任务，当前默认模板：

```bash
JOB=codex-skill-cpu-scieval-real-$(date +%s)
rjob submit --name "$JOB" \
  -P 1 \
  --cpu=1 \
  --memory=4000 \
  --charged-group=scieval_cpu_task \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=false \
  -- bash -lc 'set -eo pipefail; echo scieval_cpu_rjob_start; hostname; echo nproc=$(nproc); test -d /mnt/shared-storage-user/xuwanghan && echo mount_xuwanghan_ok; sleep 10; echo scieval_cpu_rjob_done'

sleep 90
KUBEBRAIN_NAMESPACE=ailab-scieval rjob get "$JOB"
KUBEBRAIN_NAMESPACE=ailab-scieval rjob logs job "$JOB" --tail-lines 100
KUBEBRAIN_NAMESPACE=ailab-scieval rjob delete "$JOB"
```

ai4sdata CPU rjob 最小任务，历史模板，当前不默认：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
JOB=codex-skill-cpu-ai4sdata-real-$(date +%s)
rjob submit --name "$JOB" \
  -P 1 \
  --cpu=1 \
  --memory=4000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -- bash -lc 'echo real_rjob_start; hostname; test -d /mnt/shared-storage-user/xuwanghan && echo mount_xuwanghan_ok; echo real_rjob_done'
sleep 20
rjob get "$JOB"
rjob logs job "$JOB" --tail-lines 50
rjob delete "$JOB"
```

ai4sdata 8 CPU rjob 常规模板，历史模板，当前不默认。正式使用前替换 `--name` 和启动命令；需要检查语法时保留 `--dry-run true`。

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rjob submit --dry-run true \
  --name=xxxxx \
  -P 1 \
  --cpu=8 \
  --memory=32000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -- bash command.sh
```

CPU rjob 外网代理必须使用 `--host-network=false`，并先用短任务验证。下面是 2026-06-05 scieval CPU rjob 已跑通的模板；跑到 `HTTP/2 200`、`HTTP/1.1 200` 或 `scieval_cpu_network_rjob_done` 明确出现后，才能继续正式联网任务。

```bash
JOB=codex-skill-cpu-scieval-net-$(date +%s)
rjob submit --name "$JOB" \
  -P 1 \
  --cpu=1 \
  --memory=4000 \
  --charged-group=scieval_cpu_task \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=false \
  -- bash -lc 'set -eo pipefail; echo scieval_cpu_network_rjob_start; sleep 5; source /jobutils/scripts/worker_init.sh 2>/dev/null || true; unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ftp_proxy all_proxy ALL_PROXY; source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh); export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147; export NO_PROXY=$no_proxy; env | grep -i "^http_proxy\|^https_proxy\|^no_proxy"; curl -I -L --max-time 30 https://www.google.com | sed -n "1,12p"; wget --spider --timeout=30 --tries=1 https://www.google.com; echo scieval_cpu_network_rjob_done'
sleep 110
KUBEBRAIN_NAMESPACE=ailab-scieval rjob get "$JOB"
KUBEBRAIN_NAMESPACE=ailab-scieval rjob logs job "$JOB" --tail-lines 140
KUBEBRAIN_NAMESPACE=ailab-scieval rjob delete "$JOB"
```

ai4sdata CPU rjob 外网代理，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要直接提交：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
JOB=codex-skill-cpu-network-$(date +%s)
rjob submit --name "$JOB" \
  -P 1 \
  --cpu=1 \
  --memory=4000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=false \
  -- bash -lc 'set -eo pipefail; echo network_test_start; sleep 5; source /jobutils/scripts/worker_init.sh 2>/dev/null || true; unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ftp_proxy all_proxy ALL_PROXY; source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh); export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147; export NO_PROXY=$no_proxy; env | grep -i "^http_proxy\|^https_proxy\|^no_proxy"; curl -I -L --max-time 30 https://www.google.com | sed -n "1,12p"; wget --spider --timeout=30 --tries=1 https://www.google.com; echo network_test_done'
sleep 30
rjob get "$JOB"
rjob logs job "$JOB" --tail-lines 100
rjob delete "$JOB"
```

## rjob GPU 任务

以下命令用于提交 GPU 短任务，检查调度、`nvidia-smi`、日志和删除链路。

1 张 GPU 可以用。资源公式是 `--gpu=1 --cpu=22 --memory=230000`。

ai4sdata 1 GPU dry-run 模板，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要作为默认模板：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rjob submit --dry-run true \
  --name=xxxxx \
  -P 1 \
  --gpu=1 \
  --memory=230000 \
  --cpu=22 \
  --charged-group=ai4sdata_gpu \
  --private-machine=group \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -e DISTRIBUTED_JOB=true \
  -- bash command.sh
```

scieval 1 GPU dry-run 模板：

```bash
rjob submit --dry-run true \
  --name=xxxxx \
  -P 1 \
  --gpu=1 \
  --memory=230000 \
  --cpu=22 \
  --charged-group=scieval_gpu \
  --private-machine=group \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -e DISTRIBUTED_JOB=true \
  -- bash command.sh
```

ai4sdata GPU rjob，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要直接提交：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
JOB=codex-skill-gpu-ai4sdata-real-$(date +%s)
rjob submit --name "$JOB" \
  -P 1 \
  --gpu=2 \
  --memory=460000 \
  --cpu=44 \
  --charged-group=ai4sdata_gpu \
  --private-machine=group \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -e DISTRIBUTED_JOB=true \
  -- bash -lc 'echo gpu_rjob_start; hostname; nvidia-smi -L; echo gpu_rjob_done'
sleep 20
rjob get "$JOB"
rjob delete "$JOB"
```

scieval GPU rjob：

```bash
JOB=codex-skill-gpu-scieval-real-$(date +%s)
rjob submit --name "$JOB" \
  -P 1 \
  --gpu=2 \
  --memory=460000 \
  --cpu=44 \
  --charged-group=scieval_gpu \
  --private-machine=group \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -e DISTRIBUTED_JOB=true \
  -- bash -lc 'echo gpu_rjob_start; hostname; nvidia-smi -L; echo gpu_rjob_done'
sleep 20
KUBEBRAIN_NAMESPACE=ailab-scieval rjob get "$JOB"
KUBEBRAIN_NAMESPACE=ailab-scieval rjob delete "$JOB"
```

常规 GPU 模板。正式训练或部署时，把最后一行改为 `-- bash command.sh`，并确保 `command.sh` 已放在共享存储中；需要检查语法时保留 `--dry-run true`。

ai4sdata GPU 模板，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要作为默认模板：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rjob submit --dry-run true \
  --name=xxxxx \
  -P 1 \
  --gpu=2 \
  --memory=460000 \
  --cpu=44 \
  --charged-group=ai4sdata_gpu \
  --private-machine=group \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -e DISTRIBUTED_JOB=true \
  -- bash command.sh
```

scieval GPU 模板：

```bash
rjob submit --dry-run true \
  --name=xxxxx \
  -P 1 \
  --gpu=2 \
  --memory=460000 \
  --cpu=44 \
  --charged-group=scieval_gpu \
  --private-machine=group \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -e DISTRIBUTED_JOB=true \
  -- bash command.sh
```

## 作业脚本骨架

GPU 脚本不要依赖外网。下面是正式脚本应遵循的局部环境设置；LLM 训练/部署默认使用 `llmv2`，`<project>` 和启动命令必须由具体任务决定，不能盲目照抄执行。

GPU rjob runner 的 CUDA 规则：

- **不要继承 submit host 路径。** submit host 上 `/usr/local/cuda-12.8` 存在，不代表 rjob container 内也存在。
- **恢复时机。** 在 `source /jobutils/scripts/worker_init.sh` 之后显式恢复 wrapper 传入的 CUDA 和 conda 环境变量。
- **覆盖风险。** `worker_init.sh` 可能覆盖 `PATH`、`CUDA_HOME` 或相关环境。
- **变量完整性。** 除了 `CUDA_HOME`，还要同步设置 `CUDA_PATH=$CUDA_HOME` 和 `CUDACXX=$CUDA_HOME/bin/nvcc`。
- **原因。** `flashinfer`、`ninja` 或 CUDA extension build 可能直接读取这些变量。

```bash
#!/usr/bin/env bash
set -eo pipefail

echo "[INFO] Start."

JOB_CUDA_HOME="${JOB_CUDA_HOME:-/mnt/shared-storage-gpfs2/gpfs2-shared-public/soft/cuda/12.8}"
JOB_CONDA_ENV="${JOB_CONDA_ENV:-llmv2}"

source /jobutils/scripts/worker_init.sh
export PATH="/root/miniconda3/bin:$PATH"
export CUDA_HOME="/mnt/shared-storage-gpfs2/gpfs2-shared-public/soft/cuda/12.8"
# The line above records the known cluster CUDA path. The effective rjob CUDA path below
# follows JOB_CUDA_HOME, which defaults to the same shared-storage CUDA path.
export CUDA_HOME="$JOB_CUDA_HOME"
export CUDA_PATH="$CUDA_HOME"
export CUDACXX="$CUDA_HOME/bin/nvcc"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
echo "[INFO] Proxy disabled."

conda config --append envs_dirs /mnt/shared-storage-user/xuwanghan/conda_env
source /root/miniconda3/bin/activate llmv2
if [ "$JOB_CONDA_ENV" != "llmv2" ]; then
  source /root/miniconda3/bin/activate "$JOB_CONDA_ENV"
fi
cd /mnt/shared-storage-user/xuwanghan/projects/<project>

export NPROC_PER_NODE=<num_gpus>
export CUDA_VISIBLE_DEVICES=0,1
export MASTER_PORT=29504

hostname
nvidia-smi
echo "[INFO] CUDA_HOME=$CUDA_HOME"
echo "[INFO] CUDA_PATH=$CUDA_PATH"
echo "[INFO] CUDACXX=$CUDACXX"
test -x "$CUDACXX" || { echo "[ERROR] CUDACXX not executable: $CUDACXX"; exit 1; }
which nvcc
nvcc --version

# Start training or deployment command here. Do not install or upgrade packages unless the user explicitly permits it.
```

CPU 联网脚本骨架。把 `PROJECT_DIR`、`CONDA_ENV` 和最后的启动命令改成具体任务；不要安装或升级包。用 rjob 跑外网任务时，提交命令使用 `--host-network=false`，脚本内先 `sleep 5` 再配置代理。

```bash
#!/usr/bin/env bash
set -eo pipefail

echo "[INFO] Start CPU network job."
sleep 5

PROJECT_DIR="/mnt/shared-storage-user/xuwanghan/projects/<project>"
CONDA_ENV="agent"

source /jobutils/scripts/worker_init.sh 2>/dev/null || true
export PATH="/root/miniconda3/bin:$PATH"
export CUDA_HOME="/mnt/shared-storage-gpfs2/gpfs2-shared-public/soft/cuda/12.8"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ftp_proxy all_proxy ALL_PROXY
source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh)
export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147
env | grep -i proxy
curl -I --max-time 20 https://www.google.com

conda config --append envs_dirs /mnt/shared-storage-user/xuwanghan/conda_env
source /root/miniconda3/bin/activate "$CONDA_ENV"
cd "$PROJECT_DIR"

# Start CPU/network-dependent command here.
```
