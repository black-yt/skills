# Monitoring API And Reporting

## 目录

- [数据源分层](#数据源分层)
- [Prometheus/DCGM 查询](#prometheusdcgm-查询)
- [Pod 与 RJob 映射](#pod-与-rjob-映射)
- [报告组织](#报告组织)
- [排错与验证](#排错与验证)

## 数据源分层

不要把网页监控、rjob 和通知混成一个系统。推荐分三层：

| 层级 | 数据来源 | 适合获取 | 不适合获取 |
| --- | --- | --- | --- |
| 任务层 | `rjob` CLI、rjob SDK、Kubernetes/RJob CRD | job 状态、提交者、申请资源、replica、pod、节点、排队原因、运行/等待时长 | GPU 真实计算利用率、显存、功率、温度 |
| 监控层 | 集群管理网页后端、Prometheus、DCGM exporter | GPU 利用率、显存 used/free、功率、温度、GPU 卡号、监控 label | 业务语义、用户归因、任务命令 |
| 通知层 | 飞书/Lark、邮件、Slack、Webhook | 发送整理后的脱敏报告和提醒 | 登录网页、查询 rjob、查询 Prometheus |

通用架构：

```text
rjob/SDK 读取任务层信息
        +
网页后端/Prometheus 读取监控层信息
        +
pod / replica / namespace 映射
        +
生成报告
        +
通知层发送
```

## Prometheus/DCGM 查询

`h.pjlab.org.cn` 登录后可访问的有效监控信息主要来自 Prometheus-compatible query endpoint。真正有用的通常不是 HTML 页面本身，而是这个后端 API：

```text
https://h.pjlab.org.cn/kapi/prom.monitoring.kubebrain.io/api/v1/query
```

请求头：

```text
Authorization: Bearer [ACCESS_TOKEN]
Accept: application/json
```

常见 DCGM 指标：

| 指标 | 含义 |
| --- | --- |
| `DCGM_FI_DEV_GPU_UTIL` | GPU 计算利用率 |
| `DCGM_FI_DEV_FB_USED` | 显存已用 |
| `DCGM_FI_DEV_FB_FREE` | 显存空闲 |
| `DCGM_FI_DEV_POWER_USAGE` | 功率 |
| `DCGM_FI_DEV_GPU_TEMP` | 温度 |

常见 label：

```text
Hostname
gpu
device
UUID
modelName
exported_namespace
exported_pod
exported_container
```

查询经验：

- 按节点或节点组查全部卡，不要只过滤某个 namespace，否则会漏掉其他 namespace/pod 的占用。
- 用 5 分钟窗口平滑瞬时波动，例如 `avg_over_time(...[5m])`。
- 查询范围先小后大；先查一个节点或少量 GPU，确认 label 和数值单位。
- 节点名、pod 名放进 PromQL regex 时要做 PromQL 友好的转义；不要直接把 Python `re.escape` 的结果当作 PromQL 字符串。

示例：

```promql
avg_over_time(DCGM_FI_DEV_GPU_UTIL{Hostname=~"[HOST_REGEX]"}[5m])
```

```promql
avg_over_time(DCGM_FI_DEV_FB_USED{Hostname=~"[HOST_REGEX]"}[5m])
```

Python 请求骨架：

```python
import requests

response = requests.get(
    "https://h.pjlab.org.cn/kapi/prom.monitoring.kubebrain.io/api/v1/query",
    params={"query": 'avg_over_time(DCGM_FI_DEV_GPU_UTIL{Hostname=~"[HOST_REGEX]"}[5m])'},
    headers={
        "Authorization": "Bearer [ACCESS_TOKEN]",
        "Accept": "application/json",
    },
    timeout=30,
)
response.raise_for_status()
data = response.json()
```

## Pod 与 RJob 映射

监控层通常只知道 namespace/pod/container/GPU 卡号。要归因到 rjob 和提交者，需要从任务层拿 rjob/replica 信息，再做映射。

可用映射键：

```text
monitoring.exported_namespace == replica namespace
monitoring.exported_pod == replica name 或 pod name
replica.labels["rjob name"] == rjob.metadata.name
rjob.labels["creator"] == 提交者
```

合并规则：

- 能匹配到 rjob replica：把监控指标归属到该 rjob 和提交者。
- 只能匹配 namespace/pod，不能匹配 rjob：显示为“其他占用”，不要硬归因。
- 其他占用默认放在摘要或单独小节；只有其利用率、显存、功率、温度等指标触发异常阈值时，才进入提醒项。
- 无 pod 的空卡：归为空闲卡。
- 同一 pod 多张卡：按 GPU 卡号逐条保留，再在报告层做均值、最大值或低效提醒。
- 低利用率提醒要看连续多轮或平滑窗口，不要只凭单个采样点。
- 如果要做周期性报告，保存上一轮脱敏状态，展示利用率升降、空卡变化、排队 GPU 变化和低效任务是否持续。
- 对无法从 rjob 自动归因的长期 pod，可以维护一个显式 owner 映射表；映射表必须可审计，不要靠 pod 名猜用户。

推荐内部数据结构：

```python
gpu_sample = {
    "node": "[NODE_NAME]",
    "gpu": "[GPU_INDEX]",
    "namespace": "[NAMESPACE]",
    "pod": "[POD_NAME]",
    "util": 0.0,
    "mem_used_mb": 0.0,
    "mem_free_mb": 0.0,
    "power_w": 0.0,
    "temp_c": 0.0,
}

rjob_replica = {
    "job": "[JOB_NAME]",
    "replica": "[REPLICA_NAME]",
    "creator": "[USER]",
    "node": "[NODE_NAME]",
    "requested_gpu": 1,
    "phase": "Running",
}
```

## 报告组织

报告应让读者一眼看懂“谁在排队、谁占卡、哪些卡空闲、哪些运行任务低效”。推荐结构：

1. 总览：总 GPU、占用 GPU、空闲 GPU、排队 GPU、空卡率和卡位占用率。
2. 成员汇总：提交者、运行任务数、运行占用 GPU、排队任务数、排队申请 GPU。
3. 运行任务：job、提交者、phase、申请 GPU、运行 GPU、节点、运行时长、平均 GPU 利用率、显存占用。
4. 节点卡位：节点、GPU 型号、总卡、占用卡、空卡、低利用率卡数。
5. 其他占用：无法映射到 rjob 的 namespace/pod/GPU 指标。
6. 提醒项：连续低利用率、排队过久、空卡率异常、监控数据缺失。
7. 阈值说明：低利用率阈值、低显存阈值、低功率阈值、平滑窗口和连续轮数。
8. 趋势变化：如果保存了上一轮状态，展示空卡、排队 GPU、低效任务数和核心任务利用率的变化方向。

注意用词：

- `卡位占用率` 表示 replica 占用了多少 GPU 卡。
- `GPU 利用率` 表示监控系统里的计算利用率。
- `显存占用率` 应用 `used / (used + free)` 计算，并说明单位。
- `其他占用` 不是异常，只表示无法从当前任务层信息归因到 rjob。

## 排错与验证

| 问题 | 常见原因 | 处理 |
| --- | --- | --- |
| 401/403 | access token 过期、scope 不足、用户无权限 | refresh token；仍失败则回到网页登录和权限检查 |
| PromQL 422 | regex 转义不兼容、label 名写错、query 语法错误 | 先查最小 query；逐步加 label；检查 Prometheus 返回的 error |
| 监控没有目标 pod | label 名不同、pod 已结束、监控延迟、namespace 过滤过窄 | 放宽过滤；查全部节点；对比 rjob replica 的 pod 和 namespace |
| rjob 能看到占卡但监控无利用率 | GPU 指标延迟、节点未采集、查询窗口太短 | 改 5 分钟窗口；检查 DCGM 指标是否存在 |
| 报告归因错 | pod/replica 映射键不唯一或 namespace 丢失 | 映射时同时使用 namespace + pod/replica；无法唯一匹配就归为其他占用 |

验证清单：

- API 请求是只读 GET 或等价只读 query。
- 查询带超时，不无限重试。
- 输出不包含 access token、refresh token、cookie、真实账号或登录 URL query。
- rjob 任务层与监控层口径在报告里明确区分。
- 未映射的 pod 没有被强行归因给某个用户。
- 外部通知前先本地打印脱敏报告或 dry-run。
