# GPU 分区代理启动

GPU worker 和普通 GPU rjob 默认不应依赖外网。`llmagent_gpu` 上的 0 GPU CPU fallback 是经过短探针验证的特例：任务启动后先加载获准的集群代理，再启动共享 checkout 中的 HTTP proxy，最后由 rjob 通过运行时注入的 `GPU_RJOB_PROXY_URL` 使用该代理。这个流程只适用于当前集群上已验证的 0 GPU CPU 任务，不能推广到有 GPU 的普通训练任务。

代理启动分成两层：

1. `CLUSTER_PROXY_SETUP_URL` 指向集群提供的、当前获准的 `setup_proxy.sh`。它负责建立节点到集群网络的基础代理和内部地址的 `no_proxy` 规则。
2. `META_BOT_DIR` 指向已获准的 metabot checkout。其 `tools/http_proxy/http_proxy.sh` 负责启动可被 rjob 使用的 HTTP proxy。checkout 路径、监听地址和认证信息都属于运行时配置，不写入 skill。

本仓库提供的 [`scripts/start_gpu_proxy.sh`](../scripts/start_gpu_proxy.sh) 是从实际 GPU 分区启动脚本整理出的可复用版本。它不包含个人路径、真实代理地址或凭据：

```bash
export CLUSTER_PROXY_SETUP_URL="[APPROVED_SETUP_PROXY_URL]"
export META_BOT_DIR="[APPROVED_METABOT_CHECKOUT]"

bash scripts/start_gpu_proxy.sh
```

脚本会先清除旧的大小写 HTTP 代理变量，再加载集群代理；它只报告代理是否已配置，不打印完整代理 URL，最后以 `exec` 启动 HTTP proxy。运行前应确认：

- `CLUSTER_PROXY_SETUP_URL` 来自当前集群运维或已验证的本地 ignored 配置，不从聊天内容、提交信息或公共文档复制未知 URL。
- `META_BOT_DIR/tools/http_proxy/http_proxy.sh` 存在且来自当前获准 checkout；不要在共享环境中为了补齐它而安装或升级依赖。
- 脚本通过 `bash -n scripts/start_gpu_proxy.sh`，并在短任务中验证代理和共享挂载后再提交长任务。
- 日志只能报告 `proxy=configured`、监听端口、连通性和退出状态；不要打印代理认证、完整 URL、token 或环境变量全集。

提交 GPU0 CPU rjob 时，把已经验证的代理地址从 ignored 本地配置注入所有常见大小写变量：

```bash
rjob submit \
  --charged-group=llmagent_gpu \
  --private-machine=group \
  --namespace=ailab-llmagent \
  --cpu=1 \
  --gpu=0 \
  --memory=1024 \
  --host-network=false \
  --env http_proxy="$GPU_RJOB_PROXY_URL" \
        https_proxy="$GPU_RJOB_PROXY_URL" \
        HTTP_PROXY="$GPU_RJOB_PROXY_URL" \
        HTTPS_PROXY="$GPU_RJOB_PROXY_URL" \
        all_proxy="$GPU_RJOB_PROXY_URL" \
        ALL_PROXY="$GPU_RJOB_PROXY_URL" \
  -- bash command.sh
```

私网服务地址应继续遵循集群代理脚本设置的 `no_proxy` 规则；外部 API host 如果被错误加入 `no_proxy`，会绕过 HTTP proxy 并在 GPU0 任务中超时。修复时只做目标 host 的最小移除，不要在 wrapper 中重写整份 `no_proxy`，也不要为普通 GPU 任务强行打开外网。
