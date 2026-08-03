# Service Deployment And Collaboration

## 服务部署模式

host-network 服务访问模式：job 内启动 HTTP 服务，开发机访问日志中的内网 IP 和端口。下面是 2026-05 ai4sdata CPU rjob 已跑通的历史模板；2026-06-05 当前 ai4sdata 无 CPU 资源时不要直接提交。scieval CPU rjob 基础任务和外网代理已实测，但 host-network 服务模式尚未在 scieval 上重测，需要另行短任务验证。

```bash
# 2026-06-05: ai4sdata 当前无 CPU 可用资源；这是 2026-05 已跑通的历史模板。
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

本地电脑访问集群内网服务时使用 SSH local port forwarding。这个方法不限于 vLLM；任何只在集群内网可达、但需要在本地访问的服务都可以用类似方式，例如 vLLM/OpenAI-compatible API、context-overlay、HTTP dashboard、Jupyter、Web UI、metric endpoint 或项目自定义 API。集群服务通常只暴露在 PJLAB 内网 `10.x.x.x` 或 `100.x.x.x`，本地电脑直连 `http://100.x.x.x:<port>` 超时是正常现象。把本地端口通过开发机转发到集群内网服务后，本地客户端只访问 `127.0.0.1:<local_port>`；如果服务是 OpenAI-compatible，再把 base URL 写成 `http://127.0.0.1:<local_port>/v1`：

```text
本地电脑 127.0.0.1:<local_port>
  -> SSH 登录开发机
  -> 转发到集群内网服务 <service_ip>:<service_port>
```

通用模板。在本地电脑终端执行，不是在开发机 shell 内执行：

```bash
ssh -N -T \
  -L <local_port>:<service_ip>:<service_port> \
  agent.xuwanghan+root.ailab-llmagent.ws@h.pjlab.org.cn
```

旧的 `ailab-ai4sdata.ws` workspace 保留为历史/备用入口；如果需要旧 workspace 或 `llmagent` 入口不可用，只替换 SSH 远端登录名，转发目标 `<service_ip>:<service_port>` 仍必须来自 job 日志或实际服务信息：

```bash
ssh -N -T \
  -L <local_port>:<service_ip>:<service_port> \
  agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn
```

如果同时有多个内网服务，可以转发多个端口：

```bash
ssh -N -T \
  -L <local_port_1>:<service_ip_1>:<service_port_1> \
  -L <local_port_2>:<service_ip_2>:<service_port_2> \
  agent.xuwanghan+root.ailab-llmagent.ws@h.pjlab.org.cn
```

参数含义：

- `-L <local_port>:<service_ip>:<service_port>`：把本地 `127.0.0.1:<local_port>` 转发到集群内网 `<service_ip>:<service_port>`。
- `-N`：只建立转发，不执行远端命令。
- `-T`：不分配 TTY，适合纯转发。
- 这个命令必须保持运行；终端关闭、网络断开或 `Ctrl-C` 后转发断开。
- 本地端口冲突时，换一个未占用端口，例如 `18010`、`18011`、`28010`。
- 不要把本地监听改成 `0.0.0.0`，除非用户明确要求并理解会暴露给本地网络。

双服务转发示例。下面 IP 只是某次部署示例；rjob 重启后内网 IP 可能变化，必须重新从 job 日志获取并更新 `ssh -L`：

```bash
ssh -N -T \
  -L 18010:100.96.167.106:8010 \
  -L 18011:100.101.195.51:8011 \
  agent.xuwanghan+root.ailab-llmagent.ws@h.pjlab.org.cn
```

示例含义：

- `18010 -> 100.96.167.106:8010`：某个内网服务，例如 raw vLLM/OpenAI-compatible API。
- `18011 -> 100.101.195.51:8011`：另一个内网服务，例如 context-overlay、Web UI 或自定义 API。
- 多个服务可以同时转发，只要本地端口不同。

本地测试。路径按服务类型决定；OpenAI-compatible 服务用 `/v1/models`，普通 HTTP 服务用它自己的健康检查路径、首页或 API path：

```bash
curl http://127.0.0.1:18010/v1/models \
  -H "Authorization: Bearer <API_KEY>"

curl http://127.0.0.1:18011/v1/models \
  -H "Authorization: Bearer <API_KEY>"

curl http://127.0.0.1:<local_port>/<health_or_service_path>
```

如果是 OpenAI-compatible 服务，本地 Python OpenAI SDK 写法如下：

```python
from openai import OpenAI

client = OpenAI(
    api_key="<API_KEY>",
    base_url="http://127.0.0.1:18011/v1",
)

model = client.models.list().data[0].id
response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "hello"}],
)

print(response.choices[0].message.content)
```

SSH 转发排错：

- 先在开发机或集群可访问节点上确认 `curl http://<service_ip>:<service_port>/<service_path>` 可访问；OpenAI-compatible 服务可测 `/v1/models`。
- 确认服务监听 `0.0.0.0`，不是只监听 `127.0.0.1`。
- 再在本地确认 SSH 转发终端仍在运行。
- 本地 `curl http://127.0.0.1:<local_port>/<service_path>` 超时，多数是转发断开、IP/端口过期、服务未监听 `0.0.0.0` 或 rjob 已重启。
- 返回 `401`、`403` 或其他业务鉴权错误时，检查服务自己的 API key、cookie、token 或认证头；OpenAI-compatible 服务通常需要使用对应服务 `.env` 里的 `API_KEY`，不要混用本地其他 key。
- rjob 重启后 `100.x.x.x` / `10.x.x.x` 可能变化，重新查 `SERVICE_IP`、`[INFO] ip=`、`SOCKET_IP` 或 `MASTER_ADDR`，再更新 `ssh -L`。

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
