---
name: lab-cluster-1
description: "当需要在 lab cluster 1 / PJLAB 上使用开发机、rlaunch worker 或 rjob 任务时使用；覆盖交互 SSH、安全边界、路径规范、代理、CPU/GPU 分区、训练/部署、服务访问和排错，并要求使用原始 rlaunch/rjob 命令。"
---

# Lab Cluster 1

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 概括开发机、CPU/GPU worker 和 rjob 的安全边界，列出禁止修改共享环境/conda/配置、不要在开发机跑重任务、必须使用原始 rlaunch/rjob、当前实测状态和提交前检查。 | lab cluster、dev host、rlaunch worker、rjob、CPU/GPU、environment safety、conda、shared config、raw commands、tested status、storage limit、no secrets | 触发本 skill 后默认读取；接触开发机/worker/rjob 前；准备跑测试、训练、部署、联网或改环境前；不确定某个操作是否会影响共享环境时读取 | `SKILL.md` |
| 2 | 说明交互式 SSH 工作流和远端文件编辑边界，覆盖登录方式、后台持续终端、个人项目路径、代码/数据存放、标准 unified diff + `git apply`、`perl`/`sed` 小替换、`scp` 传输和临时文件清理。 | SSH、interactive shell、remote editing、project path、storage path、`git apply --check`、unified diff、`perl -0pi`、`sed -i`、`scp`、tmp cleanup、remote git repo | 登录开发机前；需要远端编辑文件前；本地工具无法直接改远端文件时；准备传输文件、应用 patch、小范围替换、清理临时文件或确认远端路径边界时必须读取 | [references/remote-access-and-editing.md](references/remote-access-and-editing.md) |
| 3 | 记录网络和存储资源规则，覆盖开发机/CPU/GPU 节点联网差异、代理启停、`no_proxy`、公共模型/软件目录、大文件放置、缓存控制、ai4sdata/scieval 当前资源状态和历史可用性。 | proxy、network、`setup_proxy.sh`、`no_proxy`、CPU internet、GPU no internet、shared storage、model weights、HuggingFace cache、large files、ai4sdata、scieval、partition status | 需要联网下载/访问 API 前；CPU/GPU 节点网络行为不确定时；选择分区前；查模型权重/公共软件路径前；放置大文件、缓存或排查代理/407/timeout 问题时必须读取 | [references/network-storage-resources.md](references/network-storage-resources.md) |
| 4 | 给出交互式 `rlaunch` CPU/GPU worker 的原始命令模板，包含资源配比、scieval/ai4sdata 分区差异、mount、启动后检查、联网测试、GPU 检查和 worker 释放边界。 | `rlaunch`、interactive worker、CPU worker、GPU worker、resource ratio、mount、namespace、charged group、`nvidia-smi`、proxy test、worker cleanup、scieval CPU | 需要启动临时 CPU/GPU worker 前；需要交互式测试、短任务、临时服务或资源预测时；排查 worker 资源、挂载、联网、GPU 可见性或分区参数时必须读取 | [references/rlaunch-workers.md](references/rlaunch-workers.md) |
| 5 | 提供正式 `rjob` CPU/GPU 作业模板和排错规则，覆盖 submit/query/logs/delete、CPU task/GPU job、脚本初始化、CUDA_HOME/CUDA_PATH/CUDACXX、conda 恢复、host-network、代理联网和 1/2 GPU 资源模板。 | `rjob submit`、CPU task、GPU job、logs、delete、CUDA_HOME、CUDA_PATH、CUDACXX、worker_init、conda env、host-network、proxy、namespace、resource template | 提交正式训练/部署/评测任务前；写 rjob runner 前；查询/删除/看日志前；配置 CUDA/conda/代理/host-network 前；排查 job Pending/Starting/OOM/联网失败时必须读取 | [references/rjob-tasks.md](references/rjob-tasks.md) |
| 6 | 说明集群内网服务部署和本地访问链路，覆盖从 job 日志读取服务 IP/端口、设置 `no_proxy`、CPU/GPU 协作、KAPI 访问、任意内网服务的 SSH local port forwarding 和本地 OpenAI SDK/curl 验证。 | service deployment、internal IP、job logs、`SERVICE_IP`、`no_proxy`、CPU/GPU collaboration、KAPI、SSH local port forwarding、`ssh -L`、OpenAI SDK、curl `/v1/models`、private service | 部署模型/API/HTTP 服务后；需要从开发机/CPU worker/本地访问内网服务时；rjob 重启导致 IP 变化时；做多节点协作、端口转发、OpenAI SDK 验证或排查本地直连超时时必须读取 | [references/service-deployment-and-collaboration.md](references/service-deployment-and-collaboration.md) |

## 覆盖范围

- 安全边界：开发机、worker、共享环境、conda、包管理、密钥和长期配置。
- 固定信息、登录与路径：后台持久交互 SSH、单次 SSH 适用边界、公共挂载、镜像、CUDA、conda、项目根目录、大文件目录。
- 远端文件编辑：本地编辑工具边界、后台持久 SSH、标准 unified diff + `git apply`、远端编辑器、`sed`/`perl` 小替换、`scp` 传输替换和清理。
- 网络代理：开发机、CPU worker、CPU rjob、GPU 节点、私网服务和 OpenAI 相关代理边界。
- 模型权重：公共 HuggingFace 目录、大模型保存目录、查找和迁移前检查。
- 资源任务：CPU/GPU 资源公式、ai4sdata/scieval 当前可用性、scieval CPU task、GPU/CPU `rlaunch`、`rjob`、日志和清理。
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

以下结果包含 2026-05-20 实测、2026-05-22 更新和 2026-06-05 scieval CPU task 更新。不要把“已提交但未调度运行”的 GPU 功能描述成已完整跑通。

已完整跑通：

- 交互式 SSH 登录开发机，开发机上 `rlaunch` 位于 `/kubebrain/rlaunch`，`rjob` 位于 `/usr/local/bin/rjob`。
- 后台持久 SSH 远端编辑流程：在 `/mnt/shared-storage-user/xuwanghan/projects` 创建测试文件、备份、用 `sed -i` 编辑、`diff -u` 校验、内容验证、删除测试文件和备份，清理检查通过。`perl` 与 `sed` 同属小范围机械替换工具，适用边界见下文。
- 远端 git patch 流程：在项目根目录下创建临时 git repo，生成 `.tmp/change.patch`，执行 `git apply --check` 和 `git apply`，内容验证通过，随后删除 patch、`.tmp` 和整个临时测试目录，清理检查通过。
- `scp` 传输流程：本地创建小测试文件，`scp` 到远端个人项目根目录，远端 `grep` 验证后删除远端测试文件，本地测试文件也已删除，清理检查通过。
- `rlaunch --help`、`rjob submit --help`。`rjob` 在非交互 shell 中需要先执行 `source /etc/profile.d/ssh-init.sh 2>/dev/null || true`。
- `rlaunch` CPU worker：2026-06-05 使用 `scieval_cpu_task` + `--namespace=ailab-scieval` 申请 4 CPU 成功，调度到 `lg-cmc-h-cpu-0084.host.h.pjlab.org.cn`，worker 内 `nproc=4`，四个共享挂载检查通过，worker 自动退出并删除 podGroup。历史上 ai4sdata 4 CPU、ai4sdata 8 CPU、scieval 8 CPU 也曾跑通；2026-06-05 当前不要把 ai4sdata 当默认可用分区。
- `rlaunch` CPU worker 外网代理：2026-06-05 在 scieval 4 CPU worker 内执行 `source /jobutils/scripts/worker_init.sh`、`source <(curl ...setup_proxy.sh)`，`curl -I -L https://www.google.com` 返回 `HTTP/1.0 200 OK` 和 `HTTP/2 200`，`wget --spider` 返回 `200 OK`。
- `rjob` CPU 短任务：2026-06-05 使用 `scieval_cpu_task` + `--namespace=ailab-scieval` 提交 1 CPU 最小任务成功，调度到 `lg-cmc-h-cpu-0065.host.h.pjlab.org.cn`，任务状态 `Succeeded`，日志包含 `nproc=1`、`mount_xuwanghan_ok` 和 `scieval_cpu_rjob_done`，测试 job 已删除。2026-05 ai4sdata CPU rjob 也曾跑通；2026-06-05 当前 ai4sdata 没有 CPU/GPU 可用资源，因此 ai4sdata CPU rjob 模板只作为历史已验证模板保留。
- `rjob` CPU 外网代理：2026-06-05 scieval CPU rjob 使用 `--host-network=false`，job 启动后 `sleep 5`，再执行 `setup_proxy.sh`，`curl -I -L https://www.google.com` 返回 `HTTP/1.0 200 OK` 和 `HTTP/2 200`，`wget --spider` 返回 `200 OK`，测试 job 已删除。2026-05 ai4sdata CPU rjob 外网代理也曾跑通，测试 job `codex-skill-cpu-net-nohost-1779424506` 保留给运维排查；2026-06-05 当前 ai4sdata 无 CPU 资源时只作为历史验证结果。
- `rjob` GPU 短任务：ai4sdata/scieval 均已真实提交并运行到 `nvidia-smi`，日志可读，测试后 job 已删除。
- `rjob submit --dry-run true`：历史上 ai4sdata CPU 模板、ai4sdata/scieval GPU 常规模板均可生成 YAML；1 GPU 模板也已 dry-run 通过，资源为 `--gpu=1 --cpu=22 --memory=230000`。dry-run 只证明语法和资源字段可生成，不证明当前分区有可用资源。
- `rjob` host-network 服务访问：2026-05 在 ai4sdata CPU rjob 内启动 `python3 -m http.server`，开发机通过内网 IP 访问成功，返回 `codex_service_ok`，job 已删除；2026-06-05 当前 ai4sdata 无 CPU 资源时只作为历史验证结果。
- GPU 模型服务和 GPU+CPU 协作部署：GPU 服务、CPU 侧调用 GPU 内网 URL、host-network/no_proxy 协作链路已跑通。
- 模型与软件公共路径只读检查：`huggingface/hub`、`huggingface/zskj-hub`、`soft`、`soft-pkg`、大模型目标目录和 `rclone v1.68.2` 均存在；`find ... "*Qwen3-VL-4B*"` 可找到公共模型目录。

当前不可用或未完整跑通：

- `rlaunch` GPU worker：ai4sdata 1 GPU、ai4sdata 2 GPU、scieval 1 GPU 都可执行调度命令，但当前资源不足或 pending unschedulable，未进入 GPU worker。
- 2026-06-05 当前 ai4sdata 分区没有 CPU/GPU 可用资源；不要把 ai4sdata 作为默认提交目标。需要 CPU worker 时优先使用已实测的 scieval CPU task；GPU 资源仍需按实际分区状态先 predict-only 或短任务验证。

关键边界：

- CPU rjob 外网任务使用 `--host-network=false`。`--host-network=true` 下代理访问外网返回 `407 Proxy Authentication Required`，不要用于 CPU rjob 外网任务。
- 2026-06-05 当前 `rlaunch` CPU worker 优先使用 `scieval_cpu_task` + `--namespace=ailab-scieval`。
- 2026-06-05 当前 CPU rjob 优先使用 `scieval_cpu_task` + `--namespace=ailab-scieval`；查询、日志和删除时使用 `KUBEBRAIN_NAMESPACE=ailab-scieval`。
- CPU rjob 的 ai4sdata 模板是历史已验证模板；2026-06-05 当前 ai4sdata 无 CPU/GPU 资源时不要直接提交。
- GPU rjob 历史上 ai4sdata/scieval 都跑通过；2026-06-05 当前 ai4sdata 无 GPU 资源时不要直接提交 ai4sdata GPU job，先按实际分区状态验证。
- ai4sdata 的 CPU/GPU 命令模板不要删除；它们是 2026-05 已验证模板。后续如果 ai4sdata 资源恢复，先做 predict-only、最小短任务和日志检查，再恢复为默认提交目标。

## 提交前检查

- 真实申请 `rlaunch` worker 或提交 `rjob` 前，先向用户说明会占用的 CPU/GPU/memory 和预计持续时间。
- 任务是否真的需要 GPU；能用 CPU 解决的联网任务不要占 GPU。
- 是短测试还是正式任务；短测试用 `rlaunch`，正式任务用 `rjob submit`。
- GPU 数是否和 CPU/memory 匹配。
- 分区是否正确：2026-06-05 当前 rlaunch CPU worker 和 CPU rjob 都可使用 scieval `scieval_cpu_task` + `--namespace=ailab-scieval`；查询、日志和删除 scieval rjob 时加 `KUBEBRAIN_NAMESPACE=ailab-scieval`；ai4sdata CPU/GPU 当前不作为默认提交目标；GPU rjob 可用 ai4sdata 或 scieval，scieval 加 `--namespace=ailab-scieval`。
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
- `unknown charged-group` 或 namespace 相关错误：核对分区矩阵；scieval 的 `rlaunch` CPU worker 和 CPU rjob 使用 `scieval_cpu_task` 且必须带 `--namespace=ailab-scieval`；scieval rjob 查询、日志和删除需要临时前缀 `KUBEBRAIN_NAMESPACE=ailab-scieval`；ai4sdata 通常不带 namespace，但 2026-06-05 当前无 CPU/GPU 可用资源。
- GPU 节点下载失败：预期行为。改用 CPU worker 下载到共享存储，或提前准备镜像/环境。
- GPU rjob 里 `flashinfer`、`ninja`、CUDA extension build、`nvcc not found`、`CUDA_HOME not set` 报错：不要只看开发机或 submit host 的 CUDA 路径。进入 rjob 日志或 worker 内检查 `echo "$CUDA_HOME"`、`echo "$CUDA_PATH"`、`echo "$CUDACXX"`、`test -x "$CUDACXX"`、`which nvcc`、`nvcc --version`。如果脚本 source 了 `/jobutils/scripts/worker_init.sh`，确认之后又恢复了 `CUDA_HOME`、`CUDA_PATH`、`CUDACXX`、`PATH` 和 conda env。
- 外部 API 调用失败：确认任务是否在 CPU 节点；GPU 节点不可联网。
- CPU rjob 外网返回 407：先检查提交命令是否误用了 `--host-network=true`；外网任务改用 `--host-network=false`，job 内 `sleep 5` 后再配置代理。
- 私网服务访问失败：检查服务是否监听 `0.0.0.0`、端口是否开放、URL 是否用了正确 worker id 或私网 IP、私网地址是否在 `no_proxy`。
- 训练 OOM：先降低 batch、sequence length、并发生成数或改用更多 GPU；再按资源公式调整 CPU/memory。
- worker 被释放：`rlaunch` 不适合长期运行；改用 `rjob submit`。
