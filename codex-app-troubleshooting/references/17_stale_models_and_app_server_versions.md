# CLI 已更新，但模型列表或远程后台仍是旧版

适用症状：`codex update` 或包管理器报告成功，终端顶部也显示新版，但 `/model` 没有新增模型；退出并重开桌面 App 后仍无变化。先核对实际运行的后台，再区分版本、模型目录和账号可用性，不把所有缺失模型都归因于缓存或套餐。

## 先做只读核对

在**实际承载 app-server 的主机、用户和 `CODEX_HOME`** 下执行；SSH 远端、WSL 和本机终端分别取证。查询前不要为了套用示例切换数据目录或认证模式。

```bash
command -v codex
codex --version
codex app-server daemon version
codex app-server daemon --help
```

- **PATH CLI**：`codex --version` 和终端顶部版本只证明当前 CLI 程序已更新，不证明已运行的后台换了二进制，也不能代表桌面 App 版本。
- **运行中后台**：`appServerVersion` 来自目标 socket 上服务的实际响应。显式连接其他 `--remote` 地址时，还要核对那个端点；本机默认 socket 的查询不能替代远端取证。
- **后台选包**：`managedCodexVersion` / `managedCodexPath` 描述 daemon 管理入口选中的安装包，不能直接当成当前运行进程的版本。但它也不是无关字段：daemon 生命周期命令会使用这个包，因此托管包落后时是一个潜在回退点，见下方“托管包落后时是否刷新”。
- **管理归属**：`status: running` 只说明发现可响应的服务。即使输出中有 `managedCodexPath`，服务也可能是桌面端、SSH 启动器或用户直接启动的；结合 `/daemon` 的管理状态、启动来源及错误判断。
- **旧进程**：更新磁盘上的 npm 包不会替换已加载的进程。退出桌面客户端或重开终端也可能只断开连接；用后台 PID 和 starttime 的前后变化验证是否真的重启，不反复要求用户“再退出一次”。

2026-11-20 的脱敏实测样本：

| 字段 / 现象 | 重启前 | 正确后台重启后 |
| --- | --- | --- |
| `cliVersion` | `0.171.0` | `0.171.0` |
| `appServerVersion` | `0.164.0` | `0.171.0` |
| `managedCodexVersion` | `0.162.1` | `0.162.1` |
| 目标后台 | 直接启动，未受 daemon 管理 | 使用新 CLI 包重新启动 |
| 新模型目录 | 用户列表缺少新模型 | 新版独立服务的 `model/list` 返回新模型；用户确认重启后恢复 |

该样本说明版本不一致的排查方法，不表示任意旧版都缺相同模型，也不要求读者安装这些历史版本。

## 分支一：受 daemon 管理的后台

只对已确认受管理的服务使用本节。先在当前版本的 `restart --help`、`update --help` 中确认参数；沿用用户已给的中断授权，未授权中断时先完成只读检查并说明哪些活动或排队任务会受影响。

| 证据 | 处理 | 验证重点 |
| --- | --- | --- |
| 管理入口已选中目标版本，运行中的服务仍旧 | 重启受管理后台 | 运行版本是否变为选中的版本 |
| CLI 已更新，管理入口选中的包仍旧，用户要采用该 CLI 包 | `update --from-cli` 复制并固定当前完整 CLI 包，然后重启 | 选包版本、运行版本与目标版本 |
| 用户要采用正式发行渠道，而非固定本机 CLI 包 | 按当前 `update --help` 和官方说明选择正式更新方式 | 实际选中的渠道、包和运行版本；不能只重启旧包 |

已选中正确包时，官方的一行重启命令是：

```bash
codex app-server daemon restart
```

需要把当前 CLI 包提供给受管理后台时，使用官方更新命令，再独立检查结果：

```bash
codex app-server daemon update --from-cli
codex app-server daemon version
```

- **复制与固定**：`--from-cli` 是“复制并固定这个 CLI 包”，不是单纯重启，也不是修改模型。后续更新渠道的恢复见当前 help 和 [16 的受管理 WSL 案例](16_legacy_wsl_remote_connection.md)。
- **交互与影响**：命令可能显示确认提示并中断活动或排队任务。只有已有授权且需非交互执行时才加 `--yes`，不为了绕过提示默认添加。
- **入口位置**：支持的本地 TUI 可从 `/daemon` 查看管理状态并选择重启；显式远程连接应在服务所在主机管理，不能在客户端误重启另一个后台。

## 分支二：后台直接启动，不受 daemon 管理

遇到以下原文时，停止套用 daemon 更新/重启流程：

```text
app server is running but is not managed by codex app-server daemon
```

这说明目标 socket 有服务响应，但 daemon 未认领它。不是 npm 安装失败，也不能靠重复 `update --from-cli`、`restart` 或 `bootstrap` 把当前进程自动接管。

### 确认原有启动方式

- **定位进程**：核对监听端点对应的 app-server PID、父进程和 starttime，区分真正的服务、Node 包装器及 `app-server proxy`。Linux 可用 `ps -eo pid,ppid,lstart,comm` 做初筛；`readlink /proc/[PID]/exe` 可确认实际二进制，`(deleted)` 是运行进程仍引用已替换文件的线索。不要执行 `/proc/[PID]/exe --version` 来探测旧程序；那会启动另一个进程。
- **核对启动参数**：只在本机检查必要的可执行文件、工作目录、`CODEX_HOME`、监听地址和相关启动参数；不要转储完整环境、认证文件或带凭据的 argv。PID/starttime 的身份复核见 [03](03_backend_and_history.md)。
- **回收原启动器**：由桌面端 SSH 连接拉起的远程后台，`/proc/[PID]/environ` 中的 `CODEX_REMOTE_PAYLOAD`（名称随版本变化）就是客户端下发的启动脚本，内含原 `nohup ... app-server --listen ...` 命令、日志路径 `[CODEX_HOME]/app-server-control/app-server.log` 和 PATH 组装方式。只读这一个变量，分享前脱敏，不转储完整环境。
- **npm 管理标记**：同一进程环境里的 `CODEX_MANAGED_BY_NPM=1` 与 `CODEX_MANAGED_PACKAGE_ROOT` 表示它由 npm 全局包启动，而不是 daemon 选包；这与 `daemon version` 仍打印 `managedCodexPath` / `managedCodexVersion` 并不矛盾，不能单凭该输出判断服务受管理。
- **调用入口**：该启动脚本通常调用 PATH 上的 `codex`，因此 npm 全局包更新后，由客户端重连触发的重启会自动采用新版；不需要为此改写 PATH 或固定绝对路径。
- **找到所有者**：有 supervisor、服务单元或桌面连接专用重启入口时，通过原启动器正常停止并重启。仅知道进程名或父 PID 为 1，不足以选择 `systemctl restart` 的单元，更不能停止整个登录 session 或进程组。
- **明确中断范围**：共用后台的其他聊天、终端工具、任务控制器都可能中断。优先在独立 SSH 终端操作；从当前 agent 内停止承载自身的服务后，后续工具调用未必还能执行，不能假定“杀掉后再运行下一条”必然成功。

### 没有管理入口时的手动步骤

这条分支没有适用于所有机器的官方一行重启子命令。只在已核实目标进程、原启动方式及中断授权后操作；下面是**系统命令模板**，方括号须替换为本次实际值，不是可原样运行的固定命令。

1. 在独立终端再次核对目标 PID/starttime，然后请求这个服务正常终止：

   ```bash
   kill -TERM [APP_SERVER_PID]
   ```

2. 等待并确认原服务退出、监听端点释放；若仍未退出，检查关闭阶段和超时原因。不要马上并行启动第二个实例，不删除正在使用的 socket、pidfile、数据库或 WAL。不能正常退出时，说明强制终止的具体影响，仅在授权覆盖时对同一目标升级处理。
3. 用**已验证的新 CLI 路径**，按原工作目录、环境和参数启动 app-server。例如原来就是前台 Unix-socket 服务时，可在独立终端运行以下模板并保持终端连接：

   ```bash
   [VERIFIED_CODEX] [ORIGINAL_GLOBAL_OPTIONS] app-server --listen '[ORIGINAL_LISTEN_URL]'
   ```

   原参数为空则省略对应占位符。原服务若含 `-c features.code_mode_host=true` 等参数，应按实际版本保留，不能将该案例参数设成所有环境的默认值。需要后台常驻时沿用已确认的启动器、脱离终端方式及日志位置；不要把前台启动误称为 SSH 断开后仍可用的服务。
4. 从原客户端重新连接，检查新后台版本、PID/starttime 和模型列表。重启后 CLI 与运行版本已一致时，先按下一节判断托管包是否需要刷新，再决定是否处理 `managedCodexVersion`。
5. 用整条链路的进程取证收尾：客户端重连后通常会再拉起一个新的 `app-server proxy`（父进程为 sshd 或同类连接进程）。确认新后台与 proxy 的 starttime 已更新，且 `readlink /proc/[PID]/exe` 都不再带 `(deleted)`；只更新了其中一个进程时，客户端仍可能复用旧链路。

### 托管包落后时是否刷新

- **为什么不能忽略**：daemon 生命周期命令使用选中的托管包，与调用它们的 CLI 版本无关。托管包停在旧版时，之后任何一次 `codex app-server daemon start` / `restart`、TUI `/daemon` 或桌面端“重启后台”都会让运行版本静默回退到该旧版。
- **先判断是否会被使用**：这台机器若始终由 PATH 上的 CLI 或桌面端 SSH 启动器拉起服务、从不调用 daemon 生命周期命令，旧托管包不影响当前链路；但要在排查记录里注明，避免后续有人执行 `daemon restart` 时无意回退。
- **刷新被拒绝的原因**：非托管服务正在运行时，`daemon update --from-cli` 会直接报 `app server is running but is not managed by codex app-server daemon`。这不是权限或网络问题，需要先按本分支正常终止后台再执行。
- **刷新命令**：刷新只替换托管包，不改变当前启动归属；命令会把当前 CLI 包复制并固定成 `releases/local-[hash]-[平台]`，旧版本目录保留可回退。

  ```bash
  kill -TERM [APP_SERVER_PID]
  codex app-server daemon update --from-cli --yes
  ```

  刷新成功后 `daemon version` 中 `managedCodexVersion` 应与 `cliVersion` 一致。随后仍用原启动器重启服务，`cliVersion`、`appServerVersion`、`managedCodexVersion` 三者一致才算闭环。
- **不要用固定包替代正式渠道**：`--from-cli` 会标记为固定包（pinned）。需要回到正式发行渠道时按当前 `daemon update` 的 help 与官方说明处理，不要长期把旧渠道状态留在机器上。

### 避免引入新的全局改动

- **不默认强杀**：不把 `pkill -KILL -f ...`、`kill -9`、宽泛的 Codex/node 批量终止或“先杀进程，再无条件启动”的一行命令作为日常修复。匹配表达式仍可能命中包装器或其他会话；`;` 不保证前一步成功。
- **不藏启动失败**：不要默认把 stdout/stderr 全部送到 `/dev/null` 后只凭 shell 返回成功就宣布后台已启动。
- **不安装自制助手**：一次排障不需要默认生成 Python 重启器、wrapper、守护进程或 shell alias，更不能未经请求把它们写入 `.codex`、shell rc、系统目录或其他项目。若用户确需可复用工具，说明它是自定义实现、确认存放范围后再交付。
- **不改变模型选择**：更新后台不需要固定 `-m [MODEL]`、改 `model`、更换 provider 或重新登录。用户要恢复完整模型列表时，不用“绑定某个新模型”代替修复。
- **不清空状态**：不删除整个模型缓存、`auth.json`、config、sessions 或数据库来碰运气。回滚也只撤销本次明确新增或修改的对象，不能清理不认识的全局文件。

## 模型目录与完成条件

- **可选目录探针**：仅需区分独立 CLI 与共享后台时，可让用户运行 `codex --no-daemon` 并查看 `/model`，不传 `-m`。这是绕过共享后台的临时对照，不是共享后台已更新的证据；不能与 `--remote` 或 `codex agents` 混用。
- **缓存仅作线索**：当前 `CODEX_HOME` 下 `models_cache.json` 的 `client_version`、`fetched_at` 和模型名称可辅助核对；只读必要字段，不公布 identity、ETag 或整份用户状态。旧版本标记不证明缓存损坏，新旧服务也可能先后写入同一缓存。`0.171.0` 的实现会校验缓存版本与身份，不凭文件存在就断言服务采用了它。
- **实际端点**：有现成协议客户端时，按官方握手与当前 schema 查询目标后台的 `model/list`，而不是只检查另起服务的结果。列表受 provider、客户端、账号和工作区影响，升级不保证任意账号都能看到所有公开模型。
- **验收**：确认原连接使用新后台且 `appServerVersion` 为预期值，再检查 `/model`。目录返回某模型只证明可发现性，不等于已成功推理。真实请求只在任务授权范围内做；无授权时记录“目录已恢复，推理未测试”。
- **仍未恢复**：运行版本已正确但目录仍缺模型时，转查官方模型可用性、账号/工作区权限、provider 与目录请求错误，不继续反复重启或清空认证。

## 官方依据与版本边界

- **核对日期**：2026-11-20；案例 CLI / 新服务为 `0.171.0`，旧运行服务为 `0.164.0`。已只读检查 `daemon --help`、`restart --help`、`update --help`、`daemon version`；没有为编写本文再次重启用户服务。
- **二次核对（2026-11-25）**：CLI `0.172.0`，由桌面端 SSH 启动、未受 daemon 托管的远程后台仍运行 `0.171.0`；按“分支二”正常终止并按原参数重启后，`appServerVersion` 变为 `0.172.0`。`managedCodexVersion` 原为 `0.162.1`，核实上游 `app-server-daemon/README` 中“生命周期命令使用选中托管包”的说明后，用 `daemon update --from-cli` 刷新为 `0.172.0` 的 `local-[hash]` 固定包，旧 `0.162.1` 目录保留。客户端在重启后数秒内自动重连并拉起新的 `app-server proxy`。本次只复现本文流程，未重新核对 CLI 0.172.0 的其余官方文档与源码。
- **上游锚点**：GitHub API 返回最新 release 为 [`rust-v0.171.0`](https://github.com/openai/codex/releases/tag/rust-v0.171.0)，当时仓库 HEAD 为 `45ace810b3d394f177fb6b1c8a10db9c698e6e05`；release 和 HEAD 分开记录，源码核对使用固定 release，不冒充桌面 App 的源码版本。
- **官方文档**：已实际 GET 核对[命令与 `/daemon`](https://learn.chatgpt.com/docs/developer-commands)、[app-server 与 `model/list`](https://learn.chatgpt.com/docs/app-server)、[模型可用性](https://learn.chatgpt.com/docs/models)。这些完整 URL 是当前可访问的 fallback，属于滚动文档；后续先读目标版本 help，不能把本文版本冻结成永久要求。
- **固定版本源码**：已读取该 release 的 [README / 安装说明](https://github.com/openai/codex/blob/rust-v0.171.0/README.md)、[配置入口](https://github.com/openai/codex/blob/rust-v0.171.0/docs/config.md)、[daemon 生命周期说明](https://github.com/openai/codex/blob/rust-v0.171.0/codex-rs/app-server-daemon/README.md)、[管理归属与版本探针](https://github.com/openai/codex/blob/rust-v0.171.0/codex-rs/app-server-daemon/src/lib.rs)、[CLI 参数声明](https://github.com/openai/codex/blob/rust-v0.171.0/codex-rs/cli/src/main.rs)及[模型缓存版本校验](https://github.com/openai/codex/blob/rust-v0.171.0/codex-rs/models-manager/src/cache.rs)。daemon 属于实验性接口，后续版本须重新核对。
