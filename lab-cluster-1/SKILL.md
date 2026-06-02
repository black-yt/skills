---
name: lab-cluster-1
description: "当需要在 lab cluster 1 / PJLAB 上使用开发机、rlaunch worker 或 rjob 任务时使用；覆盖交互 SSH、安全边界、路径规范、代理、CPU/GPU 分区、训练/部署、服务访问和排错，并要求使用原始 rlaunch/rjob 命令。"
---

# Lab Cluster 1

## 覆盖范围

- 安全边界：开发机、worker、共享环境、conda、包管理、密钥和长期配置。
- 固定信息、登录与路径：后台持久交互 SSH、单次 SSH 适用边界、公共挂载、镜像、CUDA、conda、项目根目录、大文件目录。
- 远端文件编辑：本地编辑工具边界、后台持久 SSH、git patch、远端编辑器、`sed`、`scp` 传输替换和清理。
- 网络代理：开发机、CPU worker、CPU rjob、GPU 节点、私网服务和 OpenAI 相关代理边界。
- 模型权重：公共 HuggingFace 目录、大模型保存目录、查找和迁移前检查。
- 资源任务：CPU/GPU 资源公式、ai4sdata/scieval 分区、CPU rjob 只用 ai4sdata、GPU rjob 可用两个分区、`rlaunch`、`rjob`、日志和清理。
- 服务协作：host-network、KAPI、GPU 服务 + CPU 评测、多 worker 协作和排错。

## 核心原则

- 默认打开一个后台持久交互 SSH 终端登录开发机，并在同一个远端 shell 中连续操作。单次 `ssh 'command'` 只用于健康检查、只读查询、dry-run 这类简单一次性任务。
- 复杂任务必须走交互模式，包括远端文件编辑、项目内多步操作、调试、提交/监控 `rjob`、持续查看日志、启动/管理 `rlaunch` worker 或服务。不要为这类任务反复发送独立 `ssh` 命令。
- 主路径必须使用原始 `rlaunch` 和 `rjob submit` 命令。不要依赖远端 `.bashrc` 中的 `gpu`、`cpu`、`pred`、`proxy_on`、`openai_on` 等函数或 alias。
- 把开发机只当作登录、编辑、提交、监控和轻量检查入口。不要在开发机上跑训练、评测、部署、压力测试或依赖 GPU/大内存的任务；开发机联网但资源很少，高负载可能导致死机。
- `rlaunch` 申请到的 CPU/GPU 交互节点称为 worker，适合临时调试、短测试和临时服务部署。worker 可能因长时间无操作或长时间占用被释放，不适合正式长期任务。
- 正式训练、正式评测、稳定部署和长时间批处理用 `rjob submit`。
- GPU worker 和 GPU rjob 节点不可联网。需要下载、访问外部 API、联网评测或做网络中转时，使用 CPU worker/rjob，并在命令或脚本里直接写出 `setup_proxy.sh`、`no_proxy`、`env | grep -i proxy` 和联网测试。
- 使用开发机和集群时务必格外小心。默认只做任务局部、临时、可回滚的操作；严禁擅自修改长期环境、系统配置、共享配置或他人依赖的目录。
- 不要把真实 token、代理密码、API key、KAPI AK/SK 写入仓库、脚本、提交信息或最终回复。需要鉴权时从远端环境变量读取，并在输出中打码。

## 环境安全边界

- 不要自行修改开发机、worker、共享 `.bashrc`、`/etc/profile`、conda 全局配置、系统 PATH、CUDA 软链接、代理脚本、集群 CLI 配置或其他长期生效的环境设置。
- 不要自行安装系统软件、升级驱动、升级 CUDA、升级 Python/conda 基础环境、修改全局 pip/conda 源，或在共享环境中执行会影响他人的安装命令。
- 不要在 `/root`、系统目录、公共共享目录或他人项目目录中写入持久配置，除非用户明确要求并说明影响范围。
- 用户个人工作根目录是 `/mnt/shared-storage-user/xuwanghan/projects`。代码、脚本、普通数据、日志和项目局部产物默认都放在该目录下的具体项目目录中，不要放到其他位置。
- 大于 5G 的数据或模型权重放到 `/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/` 下的合适子目录，避免占满项目目录、开发机本地盘、worker 本地盘或临时目录。
- 不要把代码、数据、权重、日志或缓存长期放入 `/tmp`、`/var/tmp`、worker 本地盘或默认 `~/.cache`。临时文件必须用后清理，避免 `tmp`、`.cache` 等目录无限增长。
- 所有会产生大量缓存的工具都要显式指定缓存目录；小缓存放项目目录，大于 5G 的缓存或中间产物放 `/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/` 下的合适子目录。
- 开发机已经有 conda，不要重新安装 conda。默认开发环境是 `conda activate agent`。
- LLM 训练或部署优先使用已有环境 `llmv2`；`llm` 也用于 LLM 训练/部署但较旧，默认推荐 `llmv2`。
- 其他 conda 环境用途不清楚时先问用户；不要擅自创建 conda 环境、修改环境、安装/升级/卸载环境中的包。
- 需要依赖时，优先使用项目内已有环境和已有 conda 环境。确需新建环境或安装包时，先向用户说明安装位置、命令和可能影响，并取得明确许可。
- 需要改配置时，优先写到任务脚本、当前 shell 环境变量或当前 job 的局部配置中。不要把临时代理、API key、CUDA 路径、conda 设置写入长期启动文件。
- 不要清理、重命名、移动或删除共享存储中的数据、模型、环境、缓存和日志，除非用户明确指定目标路径和清理策略。
- 如果发现现有环境缺依赖、版本不匹配或配置损坏，先报告现状和建议命令；不要直接修全局环境。

## 实测状态

以下结果包含 2026-05-20 实测和 2026-05-22 更新。不要把“已提交但未调度运行”的 GPU 功能描述成已完整跑通。

已完整跑通：

- 交互式 SSH 登录开发机，开发机上 `rlaunch` 位于 `/kubebrain/rlaunch`，`rjob` 位于 `/usr/local/bin/rjob`。
- 后台持久 SSH 远端编辑流程：在 `/mnt/shared-storage-user/xuwanghan/projects` 创建测试文件、备份、用 `sed -i` 编辑、`diff -u` 校验、内容验证、删除测试文件和备份，清理检查通过。
- 远端 git patch 流程：在项目根目录下创建临时 git repo，生成 `.tmp/change.patch`，执行 `git apply --check` 和 `git apply`，内容验证通过，随后删除 patch、`.tmp` 和整个临时测试目录，清理检查通过。
- `scp` 传输流程：本地创建小测试文件，`scp` 到远端个人项目根目录，远端 `grep` 验证后删除远端测试文件，本地测试文件也已删除，清理检查通过。
- `rlaunch --help`、`rjob submit --help`。`rjob` 在非交互 shell 中需要先执行 `source /etc/profile.d/ssh-init.sh 2>/dev/null || true`。
- `rlaunch` CPU worker：ai4sdata 4 CPU、ai4sdata 8 CPU、scieval 8 CPU；worker 自动退出，挂载检查通过。
- `rlaunch` CPU worker 外网代理：`source /jobutils/scripts/worker_init.sh`、`source <(curl ...setup_proxy.sh)`、`curl -I https://www.google.com` 返回 HTTP 200。
- `rjob` CPU 短任务：ai4sdata CPU 提交成功、任务 `Succeeded`、日志可读、job 可删除。CPU rjob 固定使用 ai4sdata，不提交 scieval CPU rjob。
- `rjob` CPU 外网代理：`--host-network=false`，job 启动后 `sleep 5`，再执行 `setup_proxy.sh`，`curl -I https://www.google.com` 返回 `HTTP/1.0 200 OK` 和 `HTTP/2 200`，`wget --spider` 返回 `200 OK`。测试 job `codex-skill-cpu-net-nohost-1779424506` 保留给运维排查。
- `rjob` GPU 短任务：ai4sdata/scieval 均已真实提交并运行到 `nvidia-smi`，日志可读，测试后 job 已删除。
- `rjob submit --dry-run true`：ai4sdata CPU 模板、ai4sdata/scieval GPU 常规模板均可生成 YAML；1 GPU 模板也已 dry-run 通过，资源为 `--gpu=1 --cpu=22 --memory=230000`。
- `rjob` host-network 服务访问：ai4sdata CPU rjob 内启动 `python3 -m http.server`，开发机通过内网 IP 访问成功，返回 `codex_service_ok`，job 已删除。
- GPU 模型服务和 GPU+CPU 协作部署：GPU 服务、CPU 侧调用 GPU 内网 URL、host-network/no_proxy 协作链路已跑通。
- 模型与软件公共路径只读检查：`huggingface/hub`、`huggingface/zskj-hub`、`soft`、`soft-pkg`、大模型目标目录和 `rclone v1.68.2` 均存在；`find ... "*Qwen3-VL-4B*"` 可找到公共模型目录。

已测试但当前未完整跑通：

- `rlaunch` GPU worker：ai4sdata 1 GPU、ai4sdata 2 GPU、scieval 1 GPU 都可执行调度命令，但当前资源不足或 pending unschedulable，未进入 GPU worker。

关键边界：

- CPU rjob 外网任务使用 `--host-network=false`。`--host-network=true` 下代理访问外网返回 `407 Proxy Authentication Required`，不要用于 CPU rjob 外网任务。
- CPU rjob 只能使用 ai4sdata；GPU rjob 可使用 ai4sdata 或 scieval。

## 固定信息、登录与路径

交互式登录开发机：

```bash
ssh -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn
```

推荐工作方式：先保持一个后台持久 SSH 终端，再在这个终端内连续执行 `cd`、编辑、提交、日志查看和清理。对于 Codex 或其他自动化 agent，这意味着优先维护一个长期 PTY/session，而不是每一步都新发一次 `ssh 'command'`。只有下面这种单次简单检查才适合一次性 SSH：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=1 \
  -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn \
  'hostname; command -v rlaunch; command -v rjob'
```

复杂远端操作，例如项目内多步修改、任务脚本编写、`rjob` 提交后跟日志、`rlaunch` worker 交互、服务启动和端口测试，都应在后台持久 SSH 终端中完成。

登录后最小检查：

```bash
hostname
command -v rlaunch
command -v rjob
source /etc/profile.d/ssh-init.sh 2>/dev/null || true
rlaunch --help | sed -n '1,20p'
rjob submit --help | sed -n '1,20p'
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

常用 conda 环境：

```bash
conda activate agent   # 开发机默认开发环境
conda activate llmv2   # LLM 训练/部署推荐环境
conda activate llm     # LLM 训练/部署旧环境
```

不要重新安装 conda，不要擅自创建环境或修改已有环境中的包。遇到不清楚的环境名，先问用户。

个人项目根目录。不同项目都在这里，代码和普通项目数据不要存放到其他地方：

```bash
/mnt/shared-storage-user/xuwanghan/projects
```

大文件根目录。大于 5G 的数据或权重放到这里的合适子目录：

```bash
/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan
```

临时文件与缓存控制：

```bash
PROJECT_DIR="/mnt/shared-storage-user/xuwanghan/projects/<project>"
BIG_DIR="/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/<project>"
mkdir -p "$PROJECT_DIR" "$BIG_DIR"

# 小型项目缓存。不要使用默认 ~/.cache。
export XDG_CACHE_HOME="$PROJECT_DIR/.cache"
export HF_HOME="$PROJECT_DIR/.cache/huggingface"
export TRANSFORMERS_CACHE="$HF_HOME/transformers"
export HF_DATASETS_CACHE="$HF_HOME/datasets"

# 大于 5G 的缓存、数据或权重改放 BIG_DIR，并在命令结束后检查容量。
# export HF_HOME="$BIG_DIR/huggingface"
# export TRANSFORMERS_CACHE="$HF_HOME/transformers"
# export HF_DATASETS_CACHE="$HF_HOME/datasets"

# 必须用临时目录时，只放任务内短生命周期文件，并确保退出时清理。
RUN_TMP="$PROJECT_DIR/.tmp/run-$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$RUN_TMP"
trap 'rm -rf "$RUN_TMP"' EXIT
```

## 远端文件编辑工作流

本地编辑工具只能修改当前本地 workspace，不能直接修改开发机或 worker 上的文件。需要修改远端集群文件时，不要假装本地 `apply_patch` 已经改到了远端；先建立后台持久 SSH 终端，再按下面三种方式处理。

远端目录不一定是 git repo。只有确认远端目录是 git repo 时，才使用 `git status`、`git diff`、`git apply --check`、`git apply`。非 git 目录不要套用 git 流程，改用远端编辑器或完整文件复制。

所有远端临时文件都放到目标项目自己的 `.tmp` 子目录，文件名带任务名或时间戳；任务结束必须删除临时文件，避免 `.tmp` 被杂乱文件塞满。不要把临时编辑文件放到系统 `/tmp`、`/var/tmp` 或 worker 本地盘。

方式一：远端项目是 git repo 时，优先用 patch。先在本地生成 patch，再传到远端项目 `.tmp`，在后台持久 SSH 终端中检查并应用，最后删除临时 patch 和空 `.tmp` 目录：

```bash
# 本地终端
REMOTE='agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn'
PROJECT='/mnt/shared-storage-user/xuwanghan/projects/<project>'
PATCH_NAME="cluster-change-$(date +%Y%m%d-%H%M%S).patch"
PATCH_LOCAL="./$PATCH_NAME"

git diff -- <files> > "$PATCH_LOCAL"
ssh -CAXY "$REMOTE" "mkdir -p '$PROJECT/.tmp'"
scp "$PATCH_LOCAL" "$REMOTE:$PROJECT/.tmp/$PATCH_NAME"
rm -f "$PATCH_LOCAL"
```

```bash
# 远端后台持久 SSH 终端
PROJECT='/mnt/shared-storage-user/xuwanghan/projects/<project>'
PATCH_NAME='<patch-name-from-local-step>'
cd "$PROJECT"
test -d .git
git status --short
git apply --check ".tmp/$PATCH_NAME"
git apply ".tmp/$PATCH_NAME"
rm -f ".tmp/$PATCH_NAME"
rmdir .tmp 2>/dev/null || true
git status --short
```

方式二：少量手工改动，直接在后台持久 SSH 终端中用远端已有编辑器修改。不要安装新编辑器，不要改全局配置。git repo 用 `git diff` 检查；非 git 目录用 `diff -u` 前后备份检查，检查后删除备份：

```bash
cd /mnt/shared-storage-user/xuwanghan/projects/<project>
vim path/to/file
if [ -d .git ]; then
  git diff -- path/to/file
fi
```

```bash
cd /mnt/shared-storage-user/xuwanghan/projects/<project>
TARGET_FILE="path/to/file"
BACKUP_FILE="${TARGET_FILE}.bak.$(date +%Y%m%d-%H%M%S)"
cp "$TARGET_FILE" "$BACKUP_FILE"
vim "$TARGET_FILE"
diff -u "$BACKUP_FILE" "$TARGET_FILE" || true
rm -f "$BACKUP_FILE"
```

方式三：本地编辑复杂文件后上传替换。这是传输/替换流程，不是远端编辑；命令叫 `scp`，用于通过 SSH 复制文件。适合一个文件太复杂、不适合在远端用 `sed` 或编辑器逐步修改时使用。先在本地编辑好完整文件，再复制到远端项目 `.tmp`，在远端校验后移动到目标路径，并清理临时文件：

```bash
# 本地终端
REMOTE='agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn'
PROJECT='/mnt/shared-storage-user/xuwanghan/projects/<project>'
LOCAL_FILE='./file.new'
REMOTE_NAME="file.new.$(date +%Y%m%d-%H%M%S).$$"
REMOTE_TMP="$PROJECT/.tmp/$REMOTE_NAME"

ssh -CAXY "$REMOTE" "mkdir -p '$PROJECT/.tmp'"
scp "$LOCAL_FILE" "$REMOTE:$REMOTE_TMP"
```

```bash
# 远端后台持久 SSH 终端
PROJECT='/mnt/shared-storage-user/xuwanghan/projects/<project>'
REMOTE_NAME='<remote-name-from-local-step>'
TARGET_FILE='path/to/file'
BACKUP_NAME="$(basename "$TARGET_FILE").bak.$(date +%Y%m%d-%H%M%S)"
cd "$PROJECT"
test -s ".tmp/$REMOTE_NAME"
if [ -f "$TARGET_FILE" ]; then
  cp "$TARGET_FILE" ".tmp/$BACKUP_NAME"
fi
cp ".tmp/$REMOTE_NAME" "$TARGET_FILE"
rm -f ".tmp/$REMOTE_NAME"
if [ -d .git ]; then
  git diff -- "$TARGET_FILE"
else
  if [ -f ".tmp/$BACKUP_NAME" ]; then
    diff -u ".tmp/$BACKUP_NAME" "$TARGET_FILE" || true
  fi
fi
rm -f ".tmp/$BACKUP_NAME"
rmdir .tmp 2>/dev/null || true
```

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

ai4sdata 4 CPU worker 内代理和外网访问检查：

```bash
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
RCLONE="/mnt/shared-storage-user/xuwanghan/projects/rclone/rclone-v1.68.2-linux-amd64/rclone"
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

CPU rjob 固定使用 ai4sdata。不要提交 scieval CPU rjob；需要 scieval 分区时只用于 GPU rjob 或 rlaunch worker。

## rlaunch 资源检查

先在开发机交互 shell 中检查。只做资源预测时不会启动 worker：

```bash
rlaunch --cpu=1 --memory=4000 --predict-only
rlaunch --cpu=4 --memory=16000 --charged-group=ai4sdata_cpu_task --predict-only
rlaunch --cpu=8 --memory=32000 --charged-group=scieval_cpu_task --namespace=ailab-scieval --predict-only
rlaunch --gpu=1 --cpu=22 --memory=230000 --charged-group=ai4sdata_gpu --private-machine=group --predict-only
rlaunch --gpu=1 --cpu=22 --memory=230000 --charged-group=scieval_gpu --private-machine=group --namespace=ailab-scieval --predict-only
```

先用预测命令看调度结果；如果 GPU 返回资源不足或不可调度，不要循环提交或长期占用开发机轮询。

## rlaunch CPU Worker

真实交互使用时把末尾命令写成 `-- bash`。需要做短检查时，可以把末尾命令改成 `-- bash -lc '...'`，让 worker 自动退出，避免留下空闲资源。

ai4sdata 4 CPU：

```bash
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

ai4sdata 8 CPU：

```bash
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

CPU worker 可联网。下面命令可直接复制到开发机交互 shell 中运行，设置代理、测试外网并自动退出，不留下空闲 worker：

```bash
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

ai4sdata 1 GPU：

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
  --max-wait-duration=2m \
  -- bash -lc 'echo worker_host=$(hostname); nvidia-smi -L; test -d /mnt/shared-storage-user/xuwanghan && echo mount_xuwanghan_ok'
```

ai4sdata 2 GPU：

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

## rjob 工作流

1. 在个人项目根目录下准备 `command.sh`，例如 `/mnt/shared-storage-user/xuwanghan/projects/<project>/jobs/<name>.sh`。
2. 脚本内不要写真实 secret。用环境变量、secret 文件或运行时注入。
3. 提交前检查 `--name`、GPU/CPU/memory、分区、namespace、挂载、镜像、端口和工作目录。
4. 非交互 SSH 提交时，在同一个远端 shell 中先执行 `source /etc/profile.d/ssh-init.sh 2>/dev/null || true`。
5. 先用 `rjob submit --dry-run true ...` 做语法和资源字段检查；确认无误后去掉 `--dry-run true` 正式提交。
6. 用 `rjob submit ... -- bash command.sh` 提交。
7. 提交后记录 job name、job id、worker id 或服务 IP；只摘录必要日志，不复制 secret。
8. CPU rjob 固定使用 ai4sdata。GPU rjob 可使用 ai4sdata 或 scieval；scieval GPU job 的查询、日志和删除使用临时前缀 `KUBEBRAIN_NAMESPACE=ailab-scieval`。

最小 dry-run，用于生成并检查 YAML：

```bash
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

CPU rjob 只能使用 ai4sdata。不要提交 scieval CPU rjob；如果任务需要 CPU 且要联网、下载、评测或做中转，统一按本节 ai4sdata 模板提交。

ai4sdata CPU rjob 最小任务：

```bash
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

ai4sdata 8 CPU rjob 常规模板。正式使用前替换 `--name` 和启动命令；需要检查语法时保留 `--dry-run true`。

```bash
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

CPU rjob 外网代理必须使用 `--host-network=false`，并先用短任务验证。本命令可完整复制用于测试默认代理；跑到 `HTTP/2 200`、`HTTP/1.1 200` 或 `network_test_done` 明确出现后，才能继续正式联网任务。

```bash
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

ai4sdata 1 GPU dry-run 模板：

```bash
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

ai4sdata GPU rjob：

```bash
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

ai4sdata GPU 模板：

```bash
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

## 服务部署模式

host-network 服务访问模式：job 内启动 HTTP 服务，开发机访问日志中的内网 IP 和端口。

```bash
JOB=codex-skill-http-service-real-$(date +%s)
rjob submit --name "$JOB" \
  -P 1 \
  --cpu=1 \
  --memory=4000 \
  --charged-group=ai4sdata_cpu_task \
  --mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan \
  --image=registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab \
  --host-network=true \
  -- bash -lc 'IP=$(hostname -I | awk "{print \$1}"); echo SERVICE_IP=$IP; SERVE_DIR="/mnt/shared-storage-user/xuwanghan/projects/.tmp/$JOB-http"; mkdir -p "$SERVE_DIR"; echo codex_service_ok > "$SERVE_DIR/index.html"; cd "$SERVE_DIR"; python3 -m http.server 18081 --bind 0.0.0.0 & pid=$!; echo SERVICE_READY; sleep 180; kill $pid 2>/dev/null || true; cd /; rm -rf "$SERVE_DIR"'
sleep 20
rjob get "$JOB"
rjob logs job "$JOB" --tail-lines 40
curl --max-time 10 http://<SERVICE_IP_FROM_LOGS>:18081/
rjob delete "$JOB"
```

GPU 模型服务使用同一原则：服务监听 `0.0.0.0`，`rjob` 加 `--host-network=true`，开发机或 CPU 侧任务访问日志中的内网 IP 和端口。CPU 侧调用 GPU 内网 URL 时必须设置 `no_proxy`，不要让私网流量走外部代理。

rjob 部署服务后的访问 IP 必须从 job 日志获取，不要猜。部署脚本里打印 IP 和端口：

```bash
PORT=8010
IP=$(hostname -I | awk '{print $1}')
echo "SERVICE_IP=$IP"
echo "[INFO] ip=$IP"
echo "[INFO] port=$PORT"

# Start service with --host 0.0.0.0 and --port "$PORT".
```

rjob 启动日志里也可能出现 `SOCKET_IP=...`、`MASTER_ADDR=...`。优先使用服务脚本打印的 `SERVICE_IP` 或 `[INFO] ip=`；没有这些行时，再结合日志中的 `SOCKET_IP`、`MASTER_ADDR` 和实际监听端口判断。查看日志：

```bash
rjob logs job "$JOB" --tail-lines 200 | grep -E 'SERVICE_IP=|\[INFO\] ip=|\[INFO\] port=|SOCKET_IP=|MASTER_ADDR='
```

假设日志里出现：

```text
[INFO] ip=10.xxx.xxx.xxx
[INFO] port=8010
```

访问地址就是：

```bash
BASE_URL="http://10.xxx.xxx.xxx:8010/v1"
```

从开发机或 CPU worker 验证 OpenAI-compatible 服务：

```bash
SERVICE_IP="10.xxx.xxx.xxx"
PORT="8010"
export no_proxy="$SERVICE_IP,${no_proxy:-10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,.pjlab.org.cn}"
export NO_PROXY="$no_proxy"
curl --max-time 20 "http://$SERVICE_IP:$PORT/v1/models"
```

rlaunch worker 的 KAPI 访问需要 worker id、分区和端口，并从环境变量读取 KAPI AK/SK：

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
print(client.models.list().data[0].id)
```

访问私网服务前，把私网主机加入 `no_proxy`，避免内网流量走外部代理：

```bash
PRIVATE_HOST="<private-ip-or-hostname>"
export no_proxy="$PRIVATE_HOST,${no_proxy:-10.140.158.153,100.100.125.235,10.0.0.0/8,100.96.0.0/12,0.0.0.0,127.0.0.1,localhost,.pjlab.org.cn}"
export NO_PROXY="$no_proxy"
```

如果项目有 `structai.add_no_proxy_if_private`，Python 客户端里也直接调用：

```python
from structai import add_no_proxy_if_private

url = "http://<private-ip>:8000/v1"
add_no_proxy_if_private(url)
```

## 复杂协作模式

- 多 GPU 训练：用单个 `rjob` 申请多卡，设置 `NPROC_PER_NODE=<gpu数>`、`CUDA_VISIBLE_DEVICES=0,1,...`、固定 `MASTER_PORT`。
- GPU 服务 + CPU 评测：GPU rjob 部署模型服务；CPU worker 或确认过代理认证方案的 CPU rjob 运行评测脚本；CPU 调 GPU 内网 URL，不让私网流量走代理。
- 多个 CPU/GPU worker 协作：先记录每个 worker id、内网 IP、端口、分区和任务角色；只在 CPU 节点做联网和调度，GPU 节点只跑模型计算或服务。
- 需要下载依赖：先征得用户同意，再在 CPU worker 或开发机下载到 `/mnt/shared-storage-user/xuwanghan/projects/<project>` 的项目局部路径；超过 5G 的数据或权重放到 `/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/`；GPU 作业从共享存储读取，不在 GPU 节点联网安装。

## 提交前检查

- 真实申请 `rlaunch` worker 或提交 `rjob` 前，先向用户说明会占用的 CPU/GPU/memory 和预计持续时间。
- 任务是否真的需要 GPU；能用 CPU 解决的联网任务不要占 GPU。
- 是短测试还是正式任务；短测试用 `rlaunch`，正式任务用 `rjob submit`。
- GPU 数是否和 CPU/memory 匹配。
- 分区是否正确：CPU rjob 只能用 ai4sdata 且不加 namespace；GPU rjob 可用 ai4sdata 或 scieval，scieval 加 `--namespace=ailab-scieval`。
- GPU 任务是否完全不依赖外网。
- `command.sh` 是否位于共享存储，且没有硬编码 secret。
- 代码、脚本和普通项目数据是否位于 `/mnt/shared-storage-user/xuwanghan/projects/<project>`。
- 大于 5G 的数据或权重是否位于 `/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/` 的合适子目录。
- 是否避免使用 `/tmp`、`/var/tmp`、worker 本地盘或默认 `~/.cache` 存放长期内容。
- 是否为临时目录设置了退出清理逻辑，例如 `trap 'rm -rf "$RUN_TMP"' EXIT`。
- 是否显式设置了缓存目录，避免工具把大缓存写进默认 home cache。
- 服务是否监听 `0.0.0.0`，端口是否和客户端 URL 一致。
- 私网 URL 是否绕过代理。
- 日志输出是否会泄露 API key、代理认证、KAPI AK/SK。
- `rlaunch` 测试命令必须自动退出，除非用户明确要求进入交互 worker。
- `rjob` 测试任务结束后必须用 `rjob delete` 清理。

## 排错

- `gpu: command not found` 或 `cpu: command not found`：不要修 `.bashrc`，直接使用本 skill 中的原始 `rlaunch` 命令。
- 非交互 SSH 没加载 alias/function：这是正常现象。`.bashrc` 常见写法会在非交互 shell 中提前 return。
- `rlaunch` 申请失败：先跑对应资源的 `rlaunch --predict-only`，再降低 CPU/memory/GPU 或换分区。
- `unknown charged-group` 或 namespace 相关错误：核对分区矩阵；CPU rjob 只用 ai4sdata，scieval 只用于 GPU rjob 或 rlaunch worker；scieval 必须带 `--namespace=ailab-scieval`，ai4sdata 通常不带 namespace。
- GPU 节点下载失败：预期行为。改用 CPU worker 下载到共享存储，或提前准备镜像/环境。
- GPU rjob 里 `flashinfer`、`ninja`、CUDA extension build、`nvcc not found`、`CUDA_HOME not set` 报错：不要只看开发机或 submit host 的 CUDA 路径。进入 rjob 日志或 worker 内检查 `echo "$CUDA_HOME"`、`echo "$CUDA_PATH"`、`echo "$CUDACXX"`、`test -x "$CUDACXX"`、`which nvcc`、`nvcc --version`。如果脚本 source 了 `/jobutils/scripts/worker_init.sh`，确认之后又恢复了 `CUDA_HOME`、`CUDA_PATH`、`CUDACXX`、`PATH` 和 conda env。
- 外部 API 调用失败：确认任务是否在 CPU 节点；GPU 节点不可联网。
- CPU rjob 外网返回 407：先检查提交命令是否误用了 `--host-network=true`；外网任务改用 `--host-network=false`，job 内 `sleep 5` 后再配置代理。
- 私网服务访问失败：检查服务是否监听 `0.0.0.0`、端口是否开放、URL 是否用了正确 worker id 或私网 IP、私网地址是否在 `no_proxy`。
- 训练 OOM：先降低 batch、sequence length、并发生成数或改用更多 GPU；再按资源公式调整 CPU/memory。
- worker 被释放：`rlaunch` 不适合长期运行；改用 `rjob submit`。
