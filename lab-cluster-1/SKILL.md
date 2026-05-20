---
name: lab-cluster-1
description: "当需要在 lab cluster 1 / PJLAB 开发机上通过原始 rlaunch 或 rjob 命令使用 CPU/GPU worker、提交训练或部署任务、检查资源申请命令、处理 ai4sdata/scieval 分区、挂载共享存储、设置 worker 网络代理，或从开发机访问 worker 上的 OpenAI-compatible 服务时使用；不要依赖 .bashrc 中的 gpu/cpu/pred 快捷函数。"
---

# Lab Cluster 1

## 核心原则

- 把开发机只当作登录、编辑、提交、监控和轻量检查入口。不要在开发机上跑训练、评测、部署、压力测试或依赖 GPU/大内存的任务；开发机联网但资源很少，高负载可能导致死机。
- 主路径必须使用原始 `rlaunch` 和 `rjob submit` 命令。不要依赖远端 `.bashrc` 中的 `gpu`、`cpu`、`pred`、`proxy_on`、`openai_on` 等函数或 alias；这些只能作为用户本人交互时的便利项。
- `rlaunch` 申请到的 CPU/GPU 交互节点称为 worker，适合临时调试、短测试和临时服务部署。worker 可能因长时间无操作或长时间占用被释放，不适合正式长期任务。
- 正式训练、正式评测、稳定部署和长时间批处理用 `rjob submit`。
- GPU worker 和 GPU rjob 节点不可联网。需要下载、安装、访问外部 API、联网评测或做网络中转时，使用 CPU worker/rjob，并显式设置代理。
- 使用开发机和集群时务必格外小心。默认只做任务局部、临时、可回滚的操作；严禁擅自修改长期环境、系统配置、共享配置或他人依赖的目录。
- 不要把真实 token、代理密码、API key、KAPI AK/SK 写入仓库、脚本、提交信息或最终回复。需要鉴权时从远端环境变量读取，并在输出中打码。

## 环境安全边界

- 不要自行修改开发机、worker、共享 `.bashrc`、`/etc/profile`、conda 全局配置、系统 PATH、CUDA 软链接、代理脚本、集群 CLI 配置或其他长期生效的环境设置。
- 不要自行安装系统软件、升级驱动、升级 CUDA、升级 Python/conda 基础环境、修改全局 pip/conda 源，或在共享环境中执行会影响他人的安装命令。
- 不要在 `/root`、系统目录、公共共享目录或他人项目目录中写入持久配置，除非用户明确要求并说明影响范围。
- 需要依赖时，优先使用项目内已有环境；其次在用户指定的项目目录、个人 conda env 或临时 worker 环境中处理。确需新建环境或安装包时，先向用户说明安装位置、命令和可能影响，再执行。
- 需要改配置时，优先写到任务脚本、当前 shell 环境变量或当前 job 的局部配置中。不要把临时代理、API key、CUDA 路径、conda 设置写入长期启动文件。
- 不要清理、重命名、移动或删除共享存储中的数据、模型、环境、缓存和日志，除非用户明确指定目标路径和清理策略。
- 如果发现现有环境缺依赖、版本不匹配或配置损坏，先报告现状和建议命令；不要直接修全局环境。

## 固定信息

开发机 SSH：

```bash
ssh -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn
```

批处理检查 SSH：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=1 \
  -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn \
  'hostname; command -v rlaunch; command -v rjob'
```

非交互 SSH 下不要假设 kubebrain 环境已初始化。运行 `rjob` 前先 source 系统初始化脚本；这不是用户 `.bashrc`，而是平台环境初始化：

```bash
source /etc/profile.d/ssh-init.sh 2>/dev/null || true
```

远端一行命令示例：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn \
  'source /etc/profile.d/ssh-init.sh 2>/dev/null || true; rjob submit --help | sed -n "1,120p"'
```

公共挂载。所有 `rlaunch` 和 `rjob submit` 命令通常都带上这些挂载：

```bash
--mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan
--mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax
--mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public
--mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2
```

常用镜像：

```bash
registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab
```

常用 CUDA：

```bash
/mnt/shared-storage-gpfs2/gpfs2-shared-public/soft/cuda/12.8
```

常用 conda env 目录：

```bash
/mnt/shared-storage-user/xuwanghan/conda_env
```

常用 no_proxy：

```bash
10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147
```

## 资源公式

GPU 任务按这个公式配资源：

```text
num_gpus = G
cpu      = 22 * G
memory   = 230000 * G
```

CPU 任务按这个公式配资源：

```text
num_cpu = C
memory  = 4000 * C
```

常用换算：

| 资源 | GPU | CPU | memory |
| --- | ---: | ---: | ---: |
| 1 GPU | 1 | 22 | 230000 |
| 2 GPU | 2 | 44 | 460000 |
| 4 GPU | 4 | 88 | 920000 |
| 4 CPU | 0 | 4 | 16000 |
| 8 CPU | 0 | 8 | 32000 |
| 16 CPU | 0 | 16 | 64000 |

## 分区矩阵

| 场景 | 分区 | charged group | namespace | private machine |
| --- | --- | --- | --- | --- |
| GPU 常规 | ai4sdata | `ai4sdata_gpu` | 不加 | `group` |
| GPU 常规 | scieval | `scieval_gpu` | `ailab-scieval` | `group` |
| CPU 常规 | ai4sdata | `ai4sdata_cpu_task` | 不加 | 不加 |
| CPU 常规 | scieval | `scieval_cpu_task` | `ailab-scieval` | 不加 |

ai4sdata 闲时 GPU `rjob` 使用 `--task-type=idle --backoff_limit 16 --restart-policy=restartjobonfailure`。用户给出的闲时模板不带 `--charged-group` 和 `--private-machine`，优先保持该模板。

## rlaunch 只检查资源

在没有用户明确要求真实申请资源时，只做轻量检查或预测，不启动 worker。

检查命令是否存在：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn \
  'command -v rlaunch && command -v rjob'
```

用原始 `rlaunch` 做 CPU 资源预测：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn \
  'rlaunch --cpu 1 --memory 4000 --predict-only'
```

检查 `rlaunch` 参数：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn \
  'rlaunch --help | sed -n "1,160p"'
```

检查 `rjob submit` 参数时必须先初始化 kubebrain 环境：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn \
  'source /etc/profile.d/ssh-init.sh 2>/dev/null || true; rjob submit --help | sed -n "1,160p"'
```

## rlaunch GPU worker

### ai4sdata 1 GPU

```bash
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
  -- bash
```

### ai4sdata 2 GPU

```bash
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
  -- bash
```

### scieval 1 GPU

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
  -- bash
```

### rlaunch GPU 启动后检查

进入 worker 后先做最小检查：

```bash
hostname
nvidia-smi
python3 - <<'PY'
import os
print("CUDA_VISIBLE_DEVICES=", os.environ.get("CUDA_VISIBLE_DEVICES"))
PY
```

GPU worker 不可联网。不要在 GPU worker 中运行 `pip install`、`git clone`、外部 API 调用或联网评测。需要依赖时，提前在 CPU worker 或开发机准备到共享存储。

## rlaunch CPU worker

### ai4sdata 4 CPU

```bash
rlaunch \
  --cpu=4 \
  --memory=16000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  -- bash
```

### ai4sdata 8 CPU

```bash
rlaunch \
  --cpu=8 \
  --memory=32000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  -- bash
```

### scieval 8 CPU

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
  -- bash
```

### rlaunch CPU 启动后设置联网代理

CPU worker 可联网。进入 worker 后需要联网时：

```bash
source /jobutils/scripts/worker_init.sh 2>/dev/null || true
source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh)
export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147
env | grep -i proxy
curl -I https://www.google.com
```

访问私网服务前，确认私网地址在 `no_proxy` 中，避免私网调用被代理干扰。

## rjob 工作流

1. 在共享存储中准备 `command.sh`，例如 `/mnt/shared-storage-user/xuwanghan/projects/<project>/jobs/<name>.sh`。
2. 脚本内不要写真实 secret。用环境变量、secret 文件或运行时注入。
3. 提交前检查 `--name`、GPU/CPU/memory、分区、namespace、挂载、镜像、端口和工作目录。
4. 非交互 SSH 提交时，在同一个远端 shell 中先执行 `source /etc/profile.d/ssh-init.sh 2>/dev/null || true`。
5. 先用 `rjob submit --dry-run true ...` 做语法和资源字段检查；确认无误后去掉 `--dry-run true` 正式提交。
6. 用 `rjob submit ... -- bash command.sh` 提交。
7. 提交后记录 job name、job id、worker id 或服务 IP；只摘录必要日志，不复制 secret。

`rjob` dry-run 最小例子，不会实际申请资源：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn \
  'source /etc/profile.d/ssh-init.sh 2>/dev/null || true; rjob submit --dry-run true \
    --name codex-skill-dryrun \
    -P 1 \
    --cpu=1 \
    --memory=4000 \
    --charged-group=ai4sdata_cpu_task \
    --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
    --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
    --host-network=true \
    -- bash -lc "echo dryrun"'
```

## rjob GPU 提交模板

### ai4sdata 常规 GPU

```bash
rjob submit \
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

### ai4sdata 闲时 GPU

```bash
rjob submit \
  --name=xxxxx \
  -P 1 \
  --gpu=2 \
  --memory=460000 \
  --cpu=44 \
  --task-type=idle \
  --backoff_limit 16 \
  --restart-policy=restartjobonfailure \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -e DISTRIBUTED_JOB=true \
  -- bash command.sh
```

### scieval GPU

```bash
rjob submit \
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

## rjob CPU 提交模板

CPU rjob 适合联网评测、下载、数据预处理、API 调用和 CPU 中转部署。

ai4sdata CPU：

```bash
rjob submit \
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

scieval CPU：

```bash
rjob submit \
  --name=xxxxx \
  -P 1 \
  --cpu=8 \
  --memory=32000 \
  --charged-group=scieval_cpu_task \
  --namespace=ailab-scieval \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax \
  --mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public \
  --mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2 \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -- bash command.sh
```

如果 CPU rjob 提交被集群拒绝，先运行 `rjob submit --help` 或查看最近成功 CPU 作业的提交命令，再调整队列参数。

## GPU 作业脚本骨架

GPU 脚本不要依赖外网。不要用 `set -u` 后再 source 用户 `.bashrc`，因为部分 bashrc 可能引用未定义变量。

```bash
#!/usr/bin/env bash
set -eo pipefail

echo "[INFO] Start."

source /jobutils/scripts/worker_init.sh
export PATH="/root/miniconda3/bin:$PATH"
export CUDA_HOME="/mnt/shared-storage-gpfs2/gpfs2-shared-public/soft/cuda/12.8"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
echo "[INFO] Proxy disabled."

conda config --append envs_dirs /mnt/shared-storage-user/xuwanghan/conda_env
source /root/miniconda3/bin/activate <conda_env>
cd /mnt/shared-storage-user/xuwanghan/projects/<project>

export NPROC_PER_NODE=<num_gpus>
export CUDA_VISIBLE_DEVICES=0,1
export MASTER_PORT=29504

hostname
nvidia-smi

# Start training or deployment command here.
```

如果确实需要用户自定义环境，再显式 source 已知文件，并保证文件不会写 secret 到日志：

```bash
source /mnt/shared-storage-user/xuwanghan/projects/SuperSFE/SuperSFE/back_up/.bashrc
```

## CPU 联网作业脚本骨架

CPU 脚本可以设置代理。不要把代理认证串硬编码到脚本；优先使用集群代理脚本或环境变量。

```bash
#!/usr/bin/env bash
set -eo pipefail

echo "[INFO] Start."
sleep 5

source /jobutils/scripts/worker_init.sh
export PATH="/root/miniconda3/bin:$PATH"
export CUDA_HOME="/mnt/shared-storage-gpfs2/gpfs2-shared-public/soft/cuda/12.8"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
echo "[INFO] Proxy disabled."

echo "[INFO] ------------------------ Set Proxy Start ------------------------"
source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh)
export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147
curl -I https://www.google.com
echo "[INFO] ------------------------ Set Proxy End ------------------------"

conda config --append envs_dirs /mnt/shared-storage-user/xuwanghan/conda_env
source /root/miniconda3/bin/activate <conda_env>
cd /mnt/shared-storage-user/xuwanghan/projects/<project>

export LLM_API_KEY="${LLM_API_KEY:?set LLM_API_KEY}"
export LLM_BASE_URL="${LLM_BASE_URL:?set LLM_BASE_URL}"

# Start network-dependent command here.
```

## 服务部署模式

### rlaunch GPU 服务

适合短期交互测试。启动 worker 后在 worker 内运行服务，监听 `0.0.0.0`：

```bash
export CUDA_VISIBLE_DEVICES=0
python -m vllm.entrypoints.openai.api_server \
  --model /mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/models/<model> \
  --host 0.0.0.0 \
  --port 8000
```

开发机访问 rlaunch worker 的 KAPI URL：

```python
import base64
import os
from openai import OpenAI

api_key = "EMPTY"
worker_id = "<worker-id>"
partition = "ai4sdata"  # or "scieval"
port = 8000
url = f"https://h.pjlab.org.cn/kapi/workspace.kubebrain.io/ailab-{partition}/{worker_id}.xuwanghan/{port}/v1"

ak = os.environ["PJLAB_KAPI_AK"]
sk = os.environ["PJLAB_KAPI_SK"]
headers = {
    "Authorization": f"Basic {base64.b64encode(f'{ak}:{sk}'.encode()).decode()}",
    "Content-Type": "application/json",
}

client = OpenAI(api_key=api_key, base_url=url, default_headers=headers)
model_id = client.models.list().data[0].id
print(model_id)
```

### rjob GPU 服务

适合较稳定部署。脚本中启动服务并保持前台运行；用 `--host-network=true` 后，通常从开发机访问内网 IP：

```bash
hostname -I
python -m vllm.entrypoints.openai.api_server \
  --model /mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/models/<model> \
  --host 0.0.0.0 \
  --port 8000
```

开发机测试：

```python
from openai import OpenAI

api_key = "EMPTY"
url = "http://<private-ip>:8000/v1"
client = OpenAI(api_key=api_key, base_url=url)
print(client.models.list().data[0].id)
```

### CPU 中转服务

当 GPU 服务不联网但需要外部调用、评测或 API 聚合时，申请 CPU worker/rjob 做中转。CPU 侧设置代理访问外网，同时把 GPU 私网服务加入 `no_proxy`。

```bash
export GPU_BASE_URL="http://<gpu-private-ip>:8000/v1"
export LLM_BASE_URL="$GPU_BASE_URL"
export LLM_API_KEY="EMPTY"
```

Python 客户端访问私网服务前，如果项目有 `structai.add_no_proxy_if_private`，先调用：

```python
from structai import add_no_proxy_if_private

add_no_proxy_if_private(url)
```

## 复杂协作模式

- 多 GPU 训练：用单个 `rjob` 申请多卡，设置 `NPROC_PER_NODE=<gpu数>`、`CUDA_VISIBLE_DEVICES=0,1,...`、固定 `MASTER_PORT`。
- GPU 服务 + CPU 评测：GPU rjob 部署模型服务；CPU rjob 设置代理并运行评测脚本；CPU 调 GPU 内网 URL，不让私网流量走代理。
- 多个 CPU/GPU worker 协作：先记录每个 worker id、内网 IP、端口、分区和任务角色；只在 CPU 节点做联网和调度，GPU 节点只跑模型计算或服务。
- 需要下载依赖：在 CPU worker 或开发机下载到共享存储；GPU 作业从共享存储读取，不在 GPU 节点联网安装。

## 提交前检查

- 任务是否真的需要 GPU；能用 CPU 解决的联网任务不要占 GPU。
- 是短测试还是正式任务；短测试用 `rlaunch`，正式任务用 `rjob submit`。
- GPU 数是否和 CPU/memory 匹配。
- 分区是否正确：ai4sdata 不加 namespace，scieval 加 `--namespace=ailab-scieval`。
- GPU 任务是否完全不依赖外网。
- `command.sh` 是否位于共享存储，且没有硬编码 secret。
- 服务是否监听 `0.0.0.0`，端口是否和客户端 URL 一致。
- 私网 URL 是否绕过代理。
- 日志输出是否会泄露 API key、代理认证、KAPI AK/SK。

## 排错

- `gpu: command not found` 或 `cpu: command not found`：不要修 `.bashrc`，直接使用本 skill 中的原始 `rlaunch` 命令。
- 非交互 SSH 没加载 alias/function：这是正常现象。`.bashrc` 常见写法会在非交互 shell 中提前 return。
- `rlaunch` 申请失败：先跑 `rlaunch --cpu 1 --memory 4000 --predict-only` 看可用资源，再降低 CPU/memory/GPU 或换分区。
- `unknown charged-group` 或 namespace 相关错误：核对分区矩阵；scieval 必须带 `--namespace=ailab-scieval`，ai4sdata 通常不带 namespace。
- GPU 节点下载失败：预期行为。改用 CPU worker 下载到共享存储，或提前准备镜像/环境。
- 外部 API 调用失败：确认任务是否在 CPU 节点；GPU 节点不可联网。
- 私网服务访问失败：检查服务是否监听 `0.0.0.0`、端口是否开放、URL 是否用了正确 worker id 或私网 IP、私网地址是否在 `no_proxy`。
- 训练 OOM：先降低 batch、sequence length、并发生成数或改用更多 GPU；再按资源公式调整 CPU/memory。
- worker 被释放：`rlaunch` 不适合长期运行；改用 `rjob submit`。
