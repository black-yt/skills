# Network Storage Resources

## 网络代理

不要依赖 `.bashrc` 里的 alias/function，但需要理解其语义并用原始命令复现。远端 `.bashrc` 中和代理相关的常用项：

- `proxy_on`：`source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh)`。
- `proxy_off`：清理 `http_proxy`、`https_proxy`、`HTTP_PROXY`、`HTTPS_PROXY`、`ftp_proxy`、`all_proxy`。
- `proxy_no`：设置 `no_proxy`，避免私网和 PJLAB 内网流量走代理。
- `proxy_test`：用 `curl -v https://www.google.com` 和 `wget --spider https://www.google.com` 测外网。
- `proxy_echo`：`env | grep -i proxy` 查看当前代理。

不要使用或恢复 `.bashrc` 中已经注释的旧代理；不要把旧代理认证串复制到脚本、skill、提交信息或回复中。`proxy_r`、`openai_on`、`rtest` 属于用户个人便利项，不作为本 skill 的默认执行路径；如果任务确实需要这类代理，先向用户确认用途，再用一次性环境变量和测试命令验证。

网络边界：

- 开发机联网，但只能做轻量下载、编辑、提交和监控，不要在开发机跑高负载任务。
- CPU `rlaunch` worker 可以按本节命令设置代理并测试外网。
- CPU `rjob` 外网任务使用 `--host-network=false`，job 启动后先 `sleep 5`，再执行 `setup_proxy.sh` 并测试外网。`--host-network=true` 更适合服务/内网访问场景，外网代理可能返回 407。
- GPU worker 和 GPU rjob 节点不可联网；GPU 任务脚本应显式 `unset` 代理，依赖和模型提前放到共享存储。
- 访问私网服务时，私网地址必须进入 `no_proxy`；不要让 GPU/CPU 内网调用走外部代理。

原始代理命令：

```bash
source /jobutils/scripts/worker_init.sh 2>/dev/null || true
source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh)
```

常用 `no_proxy`：

```bash
10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147
```

完整设置和测试：

```bash
export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147
env | grep -i proxy
curl -I --max-time 20 https://www.google.com
wget --spider https://www.google.com
```

关闭代理：

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ftp_proxy all_proxy ALL_PROXY
```

开发机执行需要外网的轻量命令前，先显式打开代理并验证连通性。典型场景包括 `git fetch`、`git pull`、`git push`、`gh`、访问 GitHub、下载小依赖、`curl` 外部 API。不要在网络未通时误判为 git 凭据、GitHub 权限或仓库配置问题：

```bash
source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh)
export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147
env | grep -i '^http_proxy\|^https_proxy\|^no_proxy'
curl -I --max-time 20 https://github.com

# 只有 curl 成功后再执行需要外网的命令。
git fetch
git push
```

scieval 4 CPU worker 内代理和外网访问检查。2026-06-05 已实测通过，命令会自动退出，不留下空闲 worker：

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
  -- bash -lc 'set -eo pipefail; echo worker_host=$(hostname); echo nproc=$(nproc); source /jobutils/scripts/worker_init.sh 2>/dev/null || true; source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh); export no_proxy=10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,10.140.213.96,10.140.213.145,.pjlab.org.cn,10.140.14.204,10.140.2.204,10.140.31.254,10.140.14.254,p-ceph-norm-outside.pjlab.org.cn,p-ceph-norm-inside.pjlab.org.cn,10.140.97.32,10.140.96.147; export NO_PROXY=$no_proxy; env | grep -i "^http_proxy\|^https_proxy\|^no_proxy"; curl -I -L --max-time 30 https://www.google.com | sed -n "1,12p"; wget --spider --timeout=30 --tries=1 https://www.google.com; echo scieval_cpu_network_ok'
```

ai4sdata 4 CPU worker 内代理和外网访问检查，历史模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要直接提交：

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

CPU rjob 外网代理要求：

- CPU rjob 外网任务提交时使用 `--host-network=false`。
- job 内先 `sleep 5`，再 `source /jobutils/scripts/worker_init.sh` 和 `source <(curl -sSL http://deploy.i.h.pjlab.org.cn/infra/scripts/setup_proxy.sh)`。
- 正式联网任务前用短 job 测到 `HTTP/2 200`、`HTTP/1.1 200` 或 `network_test_done`。
- 不要在 job 命令、日志、仓库或最终回复中打印带认证信息的代理 URL。
- 如果测试返回 `407 Proxy Authentication Required`、`403 Forbidden` 或连接超时，先检查是否误用了 `--host-network=true`；仍失败时再让用户或运维确认代理策略。

私网服务代理处理：

```python
from structai import add_no_proxy_if_private

add_no_proxy_if_private(url)
```

## 模型权重与公共软件路径

优先复用集群已有模型，避免重复下载大模型。保存路径不能随便改，项目目录、开发机本地盘、worker 本地盘和临时目录经常容量不够。超过 5G 的数据或权重应放到 `/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/` 下。

公共路径结构：

```text
/mnt/shared-storage-gpfs2/gpfs2-shared-public/
├── huggingface
│   ├── hub        # 大模型评测团队提供的公共模型，会持续更新
│   └── zskj-hub   # 用户交流群反馈下载的模型
├── soft           # 集群内常用软件的 prefix 安装目录
└── soft-pkg       # 集群内常用软件包
```

更大的模型优先保存到：

```bash
/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/models
```

只读查找模型命令：

```bash
find /mnt/shared-storage-gpfs2/gpfs2-shared-public/huggingface -maxdepth 3 -type d -name "*Qwen3-VL-4B*"
```

需要找 Qwen3.5 系列时也先查公共目录：

```bash
find /mnt/shared-storage-gpfs2/gpfs2-shared-public/huggingface -maxdepth 3 -type d \( -name "*Qwen3.5-9B*" -o -name "*Qwen3.5-35B*" \)
```

有些公共模型路径是 Hugging Face hub cache 格式，不是可以直接作为 `MODEL_PATH` 的标准 ckpt/model 文件夹。典型 cache 目录长这样：

```text
models--Org--Model/
├── blobs/
├── refs/
│   └── main
└── snapshots/
    └── <commit>/
```

判断规则：

- 标准模型目录通常在根目录能看到 `config.json`、tokenizer 文件、`*.safetensors` 或模型分片，可直接作为 `MODEL_PATH`。
- cache 顶层通常只有 `blobs/`、`refs/`、`snapshots/`，不能直接当成标准 ckpt 目录传给 vLLM/Transformers。
- cache 里的 `snapshots/<commit>/` 经常是指向 `blobs/` 的 symlink；在 rjob/worker 或跨挂载场景下，最好先转换成标准目录。

转换脚本放在本 skill 的 `scripts/hf_cache_to_model_dir.py`。使用前先做 dry-run，确认输入 cache、输出目录和 revision 正确；输出目录应放在大模型目录下，不要放到项目目录、`/tmp` 或 worker 本地盘：

```bash
SCRIPT="/abs/path/to/skills/lab-cluster-1/scripts/hf_cache_to_model_dir.py"
CACHE_DIR="/mnt/shared-storage-gpfs2/gpfs2-shared-public/huggingface/hub/models--Org--Model"
OUT_DIR="/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/models/Org--Model"

python3 "$SCRIPT" \
  --cache-dir "$CACHE_DIR" \
  --out-dir "$OUT_DIR" \
  --revision main \
  --link-mode hardlink \
  --dry-run
```

dry-run 确认无误后再执行真实转换：

```bash
python3 "$SCRIPT" \
  --cache-dir "$CACHE_DIR" \
  --out-dir "$OUT_DIR" \
  --revision main \
  --link-mode hardlink

test -f "$OUT_DIR/config.json"
find "$OUT_DIR" -maxdepth 2 -type f \( -name "*.safetensors" -o -name "*.bin" -o -name "tokenizer*" \) | sed -n '1,20p'
```

转换边界：

- 优先用 `--link-mode hardlink` 节省空间；如果跨文件系统硬链接失败，脚本会自动 fallback 到 copy。
- 如果明确需要复制独立副本，用 `--link-mode copy`，但必须先确认目标盘容量。
- 目标目录非空时脚本默认拒绝写入；只有确认路径无误且允许清空时才加 `--overwrite`。
- 不要把 cache 转换结果写回公共 `huggingface/hub` 或 `zskj-hub` 目录；输出到个人大模型目录。
- 转换只是整理文件布局，不会下载模型；如果 cache 不完整或 `refs/main` 指向的 snapshot 缺文件，需要先在可联网 CPU 节点补齐 cache 或换已有完整模型目录。

迁移前检查：

- 不要假设用户给出的迁移源路径一定存在。先 `test -d` 或 `find` 确认源目录，再 `rclone copy`。
- 如果目标目录已经存在，先确认是否复用、增量同步或另存新目录；不要覆盖或移动现有权重。
- 大模型迁移前先确认目标盘容量，超过 5G 的权重放到 `/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/` 下。

使用模型前，先把 `MODEL_PATH` 指向已存在目录，不要重新下载：

```bash
MODEL_PATH="/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/models/Qwen--Qwen3.5-9B"
test -d "$MODEL_PATH" || { echo "missing model: $MODEL_PATH"; exit 1; }
```

只有用户明确要求迁移模型时，才考虑从公共目录复制到大模型目录。复制前必须检查源目录和目标父目录；如果目标已存在，不要重复复制：

```bash
RCLONE="${RCLONE:-/abs/path/to/rclone}"
SRC="/mnt/shared-storage-gpfs2/gpfs2-shared-public/huggingface/zskj-hub/models-Qwen-Qwen3.5-35B-A3B"
DST="/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/models/Qwen--Qwen3.5-35B-A3B"
test -x "$RCLONE"
test -d "$SRC"
test -d "$(dirname "$DST")"
test ! -e "$DST"
```

满足以上检查后，再向用户确认是否执行大文件复制。不要在没有用户明确许可时运行 `rclone copy --progress --transfers 200 --checkers 200 "$SRC" "$DST"`。

## 资源与分区

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

分区矩阵：

| 场景 | 分区 | charged group | namespace | private machine |
| --- | --- | --- | --- | --- |
| rlaunch GPU / rjob GPU | ai4sdata | `ai4sdata_gpu` | 不加 | `group` |
| rlaunch GPU / rjob GPU | scieval | `scieval_gpu` | `ailab-scieval` | `group` |
| rlaunch CPU worker | ai4sdata | `ai4sdata_cpu_task` | 不加 | 不加 |
| rlaunch CPU worker | scieval | `scieval_cpu_task` | `ailab-scieval` | 不加 |
| rjob CPU | ai4sdata | `ai4sdata_cpu_task` | 不加 | 不加 |
| rjob CPU | scieval | `scieval_cpu_task` | `ailab-scieval` | 不加 |

分区状态记录：

| 日期 | ai4sdata | scieval | 默认选择 |
| --- | --- | --- | --- |
| 2026-05 | CPU rjob、GPU rjob 和相关模板已验证 | GPU rjob 已验证；CPU worker 历史上可用 | 按任务选择 ai4sdata 或 scieval |
| 2026-06-05 | 当前没有 CPU/GPU 可用资源；模板保留为历史已验证配置 | `rlaunch` CPU worker、CPU rjob、CPU 外网代理已验证 | CPU 默认用 scieval；GPU 先按实际资源验证 |

当前使用边界：

- ai4sdata 分区当前没有 CPU/GPU 可用资源，不作为默认提交目标；下面保留的 ai4sdata 命令只在资源恢复且用户确认后使用。
- scieval 分区已增加 CPU task；`rlaunch` CPU worker 使用 `scieval_cpu_task` + `--namespace=ailab-scieval`，4 CPU 启动、挂载和外网代理均已实测通过。
- scieval CPU rjob 使用 `scieval_cpu_task` + `--namespace=ailab-scieval`，1 CPU 最小任务已实测 `Succeeded`；查询、日志和删除时带 `KUBEBRAIN_NAMESPACE=ailab-scieval`。
- GPU rjob 历史上 ai4sdata/scieval 都跑通过；当前是否可调度仍要以 predict-only、短任务和调度器状态为准。
- 保留 ai4sdata 模板是为了资源恢复时复用；恢复后仍必须先短测，不要直接按历史结果提交正式任务。
