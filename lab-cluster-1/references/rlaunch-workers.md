# Rlaunch Workers

## rlaunch 资源检查

先在开发机交互 shell 中检查。只做资源预测时不会启动 worker：

```bash
# 2026-06-05 当前默认 CPU worker 检查。
rlaunch --cpu=4 --memory=16000 --charged-group=scieval_cpu_task --namespace=ailab-scieval --predict-only
rlaunch --cpu=8 --memory=32000 --charged-group=scieval_cpu_task --namespace=ailab-scieval --predict-only

# 仅在 ai4sdata 资源恢复并得到用户确认后使用。
rlaunch --cpu=4 --memory=16000 --charged-group=ai4sdata_cpu_task --predict-only
rlaunch --gpu=1 --cpu=22 --memory=230000 --charged-group=ai4sdata_gpu --private-machine=group --predict-only

# scieval GPU 是否可用仍需单独检查。
rlaunch --gpu=1 --cpu=22 --memory=230000 --charged-group=scieval_gpu --private-machine=group --namespace=ailab-scieval --predict-only
```

先用预测命令看调度结果；如果 GPU 返回资源不足或不可调度，不要循环提交或长期占用开发机轮询。

## rlaunch CPU Worker

真实交互使用时把末尾命令写成 `-- bash`。需要做短检查时，可以把末尾命令改成 `-- bash -lc '...'`，让 worker 自动退出，避免留下空闲资源。

scieval 4 CPU，2026-06-05 当前默认模板，已实测启动、挂载和自动清理：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rlaunch \
  --cpu=4 \
  --memory=16000 \
  --charged-group=scieval_cpu_task \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --max-wait-duration=5m \
  -- bash -lc 'echo worker_host=$(hostname); echo nproc=$(nproc); test -d /mnt/shared-storage-user/xuwanghan && echo mount_xuwanghan_ok; test -d /mnt/shared-storage-user/sciprismax && echo mount_sciprismax_ok; test -d /mnt/shared-storage-gpfs2/gpfs2-shared-public && echo mount_public_ok; test -d /mnt/shared-storage-gpfs2/sciprismax2 && echo mount_sciprismax2_ok'
```

ai4sdata 4 CPU，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源，不作为默认命令：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rlaunch \
  --cpu=4 \
  --memory=16000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --max-wait-duration=2m \
  -- bash -lc 'echo worker_host=$(hostname); test -d /mnt/shared-storage-user/xuwanghan && echo mount_xuwanghan_ok; test -d /mnt/shared-storage-user/sciprismax && echo mount_sciprismax_ok; test -d /mnt/shared-storage-gpfs2/gpfs2-shared-public && echo mount_public_ok; test -d /mnt/shared-storage-gpfs2/sciprismax2 && echo mount_sciprismax2_ok'
```

ai4sdata 8 CPU，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源，不作为默认命令：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rlaunch \
  --cpu=8 \
  --memory=32000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --max-wait-duration=2m \
  -- bash -lc 'echo worker_host=$(hostname); nproc; test -d /mnt/shared-storage-user/xuwanghan && echo mount_xuwanghan_ok; test -d /mnt/shared-storage-gpfs2/gpfs2-shared-public && echo mount_public_ok'
```

scieval 8 CPU：

```bash
rlaunch \
  --cpu=8 \
  --memory=32000 \
  --charged-group=scieval_cpu_task \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --max-wait-duration=2m \
  -- bash -lc 'echo worker_host=$(hostname); nproc; test -d /mnt/shared-storage-user/xuwanghan && echo mount_xuwanghan_ok; test -d /mnt/shared-storage-user/sciprismax && echo mount_sciprismax_ok; test -d /mnt/shared-storage-gpfs2/gpfs2-shared-public && echo mount_public_ok; test -d /mnt/shared-storage-gpfs2/sciprismax2 && echo mount_sciprismax2_ok'
```

CPU Worker 联网：

CPU worker 可联网。下面命令按 2026-06-05 已实测的 scieval CPU worker 编写，可直接复制到开发机交互 shell 中运行，设置代理、测试外网并自动退出，不留下空闲 worker：

```bash
rlaunch \
  --cpu=4 \
  --memory=16000 \
  --charged-group=scieval_cpu_task \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --max-wait-duration=5m \
  -- bash -lc 'set -eo pipefail; echo worker_host=$(hostname); echo nproc=$(nproc); source /jobutils/scripts/worker_init.sh 2>/dev/null || true; source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh); export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147; export NO_PROXY=$no_proxy; env | grep -i "^http_proxy\|^https_proxy\|^no_proxy"; curl -I -L --max-time 30 https://www.google.com | sed -n "1,12p"; wget --spider --timeout=30 --tries=1 https://www.google.com; echo scieval_cpu_network_ok'
```

ai4sdata CPU worker 联网检查，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要直接提交：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rlaunch \
  --cpu=4 \
  --memory=16000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --max-wait-duration=2m \
  -- bash -lc 'source /jobutils/scripts/worker_init.sh 2>/dev/null || true; source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh); export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147; env | grep -i "^http_proxy\|^https_proxy\|^no_proxy"; curl -I --max-time 20 https://www.google.com | sed -n "1,5p"'
```

进入交互 CPU worker 后，需要联网时用这一组命令。不要依赖 `.bashrc` alias：

```bash
source /jobutils/scripts/worker_init.sh 2>/dev/null || true
source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh)
export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147
env | grep -i proxy
curl -I --max-time 20 https://www.google.com
wget --spider https://www.google.com
```

## rlaunch GPU Worker

以下命令用于申请 GPU worker。真实交互使用时把末尾命令写成 `-- bash`，进入 worker 后先运行 `hostname`、`nvidia-smi -L` 和挂载检查；如果调度器提示资源不足或 pending unschedulable，不要反复提交。

ai4sdata 1 GPU，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要直接提交：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rlaunch \
  --gpu=1 \
  --cpu=22 \
  --memory=230000 \
  --charged-group=ai4sdata_gpu \
  --private-machine=group \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --max-wait-duration=2m \
  -- bash -lc 'echo worker_host=$(hostname); nvidia-smi -L; test -d /mnt/shared-storage-user/xuwanghan && echo mount_xuwanghan_ok'
```

ai4sdata 2 GPU，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要直接提交：

```bash
# 2026-06-05: ai4sdata 当前无 CPU/GPU 可用资源；仅在资源恢复并短测后使用。
rlaunch \
  --gpu=2 \
  --cpu=44 \
  --memory=460000 \
  --charged-group=ai4sdata_gpu \
  --private-machine=group \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --max-wait-duration=30s \
  -- bash -lc 'echo worker_host=$(hostname); nvidia-smi -L'
```

scieval 1 GPU：

```bash
rlaunch \
  --gpu=1 \
  --cpu=22 \
  --memory=230000 \
  --charged-group=scieval_gpu \
  --private-machine=group \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --max-wait-duration=30s \
  -- bash -lc 'echo worker_host=$(hostname); nvidia-smi -L'
```

GPU worker 不可联网。不要在 GPU worker 中运行 `pip install`、`git clone`、外部 API 调用或联网评测。需要依赖时，提前在 CPU worker 或开发机准备到共享存储。
