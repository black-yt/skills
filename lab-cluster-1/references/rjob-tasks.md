# Rjob Tasks

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
