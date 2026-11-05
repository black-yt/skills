# rjob 部署、访问与真实验收

## 运行时注入集群配置

集群登录、分区权限和代理规则以当前环境为准。目标为 lab cluster 1 时，结合现有 [lab-cluster-1](https://github.com/black-yt/skills/blob/main/lab-cluster-1/SKILL.md) 使用；本 skill 不复制账号、个人目录、镜像凭据或长期配置。

```bash
# 在开发机设置获准的配置；只提交/监控，不在这里启动 GUI。
export CUA_NAMESPACE="[NAMESPACE]"
export CUA_CHARGED_GROUP="[CPU_CHARGED_GROUP]"
export CUA_IMAGE="[APPROVED_UBUNTU_22_04_IMAGE]"
export CUA_MOUNT="[GPFS_MOUNT_SPEC]"
export CUA_SOFTWARE_DIR="[PROJECT_ROOT]/software"
export CUA_ARTIFACT_DIR="[PROJECT_ROOT]/artifacts"
export CUA_RUN_ID="desktop-$(date +%Y%m%d-%H%M%S)-$$"

RUNTIME="[PROJECT_ROOT]/desktop"
CUA_DRY_RUN=1 bash "$RUNTIME/submit_rjob.sh" "$CUA_RUN_ID"
bash "$RUNTIME/submit_rjob.sh" "$CUA_RUN_ID"
```

- **前置准备：** 使用当前环境认可的 rjob 初始化方式；例如 CLI 需要初始化脚本时先加载，不修改共享 `.bashrc`。软件和 Python 缓存按 [03](03_download_and_dependencies.md) 在联网 CPU 准备任务中建立。
- **资源：** 提交脚本固定 `--gpu=0`，默认 2 CPU / 8000 MiB；`CUA_CPU`、`CUA_MEMORY` 可覆盖。名字含时间戳和 run 标识，重试使用新 run ID。
- **挂载：** 必须显式挂载包含代码、软件和证据目录的共享盘。能访问公网不证明 GPFS 已挂载；容器中的绝对路径必须与提交命令一致。
- **网络：** 样例使用 `--host-network=false`。私网服务绕过外部代理；不要把切换 host-network 当作修复外网认证的方法。
- **参数不泄漏：** 脚本不转发 API key、完整代理 URL 或任意环境变量列表。联网准备需另行按环境注入获准代理，桌面提交默认 `CUA_OFFLINE=1`。
- **dry-run 边界：** 只验证命令/YAML，不证明配额或节点足够；真实调度要看 job、replica 和 events。

## CPU 排不上时的 0 GPU 回退

1. **先判断原因：** 读取 events；`Insufficient cpu/memory`、标签不匹配和 group quota 不是应用安装失败。可先用当前集群 `rlaunch --predict-only` 检查目标资源。
2. **授权和范围：** 仅在用户授权且集群允许时，用 GPU 分区的少量 CPU 做短任务；始终 `--gpu=0`。不能擅自申请 GPU，也不能把短探针例外当作批量 CPU 调度政策。
3. **私有节点参数：** 在要求私有节点 admission 的环境设置 `CUA_PRIVATE_MACHINE=group`，对应 `--private-machine=group`。其他环境不要凭空照搬。
4. **联网边界：** 归档和 Python 包已缓存时可复用内部 apt 源，无需公网。确需外网时，先遵循该集群的获准代理与最小探针流程，不把普通 GPU 节点假设为可联网。
5. **清理：** 删除无效 pending 任务；测试完删除回退任务，不同时挂着多份重试。

```bash
export CUA_CHARGED_GROUP="[APPROVED_GPU_CHARGED_GROUP]"
export CUA_PRIVATE_MACHINE=group
export CUA_RUN_ID="desktop-fallback-$(date +%Y%m%d-%H%M%S)-$$"
CUA_DRY_RUN=1 bash "$RUNTIME/submit_rjob.sh" "$CUA_RUN_ID"
bash "$RUNTIME/submit_rjob.sh" "$CUA_RUN_ID"
```

## 内网与本地访问

- **同集群：** 从 `session.json` 或 `DESKTOP_URL` 获取实际容器 IP/端口，不假设宿主机 IP 等于 pod IP。先测 `/healthz`，再截图。
- **集群外：** 用 SSH local port forwarding 将本地端口转到该内网 IP；保留已有 SSH 登录方式，不把代理或认证写入仓库。

```bash
ssh -N -L 8765:[DESKTOP_IP]:8765 [APPROVED_DEV_HOST]
python3 "$RUNTIME/desktop_client.py" ./session.json \
  --url http://127.0.0.1:8765 --screenshot ./desktop.png
```

本地客户端还需读取 `session.json` 指向的 token 文件；安全复制所需 session/token 后，将本地 `token_file` 改为本地文件路径并保留 0600 权限。不要在终端、PR 或截图中展示 token 内容。转发只解决连通性，不替代接口鉴权。

## 真实验收

```bash
# 在开发机提交，验收本身在 rjob 容器中执行。
export CUA_RUN_ID="desktop-smoke-$(date +%Y%m%d-%H%M%S)-$$"
CUA_MODE=smoke CUA_DRY_RUN=1 bash "$RUNTIME/submit_rjob.sh" "$CUA_RUN_ID"
CUA_MODE=smoke bash "$RUNTIME/submit_rjob.sh" "$CUA_RUN_ID"

KUBEBRAIN_NAMESPACE="$CUA_NAMESPACE" rjob get "$CUA_RUN_ID"
KUBEBRAIN_NAMESPACE="$CUA_NAMESPACE" rjob logs job "$CUA_RUN_ID" -n 60
KUBEBRAIN_NAMESPACE="$CUA_NAMESPACE" rjob events "$CUA_RUN_ID"
# 核对并保留结果后删除这一个测试任务。
KUBEBRAIN_NAMESPACE="$CUA_NAMESPACE" rjob delete "$CUA_RUN_ID"
```

`rjob_run_smoke.sh` 启动真实 Slicer、开启短录屏并运行 `verify_desktop.py`，结束后停止会话并检查视频。通过条件：

- **鼠标：** PyAutoGUI 移动后读取到期望坐标；点击取得目标窗口焦点。
- **键盘：** Ctrl+3 打开 Slicer 控制台，输入并执行一条场景生成命令；由应用写出 `slicer-input-confirmed.json`，证明输入确实到达软件。
- **渲染：** 真实 VTK 球面超过 1000 顶点，应用内 `ReportCapabilities()` 包含 llvmpipe；拖动 3D 视图后保存 PNG。
- **证据：** `verification.json`、`slicer-pyautogui.png`、日志及 `screen.mp4`；必须实际打开 PNG，确认是目标软件和可见 3D 场景。
- **视频与退出：** ffprobe 检查 H.264 与有效时长；`exit-code=0` 且 runner 日志出现 `real_slicer_acceptance=ok`，最终 job Succeeded。单个条件不能替代其余条件。

## 已有测量与局限

2026-11-05，Ubuntu 22.04、Slicer 5.12.4、1440×900，2 CPU / 8000 MiB / 0 GPU 的 GPU 分区 CPU 回退任务已实测成功；当时 CPU 分区无可调度资源。

| 指标 | 观测 |
| --- | --- |
| 软件渲染 | 应用内 Mesa llvmpipe，OpenGL 4.5 |
| 场景与操作 | 2210 顶点球面，真实 PyAutoGUI 热键、输入、执行、拖动和截图 |
| cgroup 内存峰值 | 2,773,491,712 字节，约 2.58 GiB，包含录屏和文件缓存 |
| 录屏 | H.264、1440×900、5 FPS、34.2 秒、396,480 字节 |
| 远端控制 | 另一次真实任务从开发机经 pod IP 完成健康检查与截图 |
| 官方包下载 | 正确 file 接口 + curl 64 并发，在当时网络中约 462 秒；不能作为带宽 SLA |

- **可公开的经验：** 保留版本、资源、方法、数值和失败原因；不包含本地项目路径、临时 job 名、节点 IP、token、个人日志或软件二进制。
- **尚未覆盖：** 大型影像、分割/体渲染、长时间和多会话性能；派生 Docker 镜像没有构建测试。
- **复用复测：** 本 skill 参数化后的 runtime 同日再次通过相同 2 CPU / 8000 MiB / 0 GPU 真实验收，内存峰值约 2.62 GiB。脚本复用已有官方归档与 Python 包缓存，未重新下载软件；两次测量差异不作为性能回归结论。

## 常见失败判据

| 表现 | 排查与处理 |
| --- | --- |
| job Unknown/Starting，但没有应用日志 | 看真实 phase、replica 和 events；Inqueue 可能被 CLI 映射为 Unknown，不先改 GUI 代码 |
| pending 时 logs 报 `TypeError: 'NoneType' object is not iterable` | 可能是 CLI 处理“暂无日志”的问题；不等于容器已失败 |
| Xvfb 或 glxinfo 正常，Slicer 没画面 | 看目标应用 stderr、xcb/GL 依赖和应用内渲染器；占位 Qt 窗口不能替代验收 |
| 输入返回 200，但场景没变化 | 检查首次启动提示和窗口焦点；保留控制台截图，用应用写回标记验证输入 |
| PyAutoGUI import/Xauthority 错误 | 在 import 前设置会话 DISPLAY/XAUTHORITY；确认在桌面所在容器，而非开发机 |
| 截图失败但鼠标能动 | 检查 Pillow/Tk/scrot、X11 session 标识和截图后端；不得静默换成其他鼠标工具 |
| 视频存在但不能播放 | 确认 FFmpeg 读取正确 DISPLAY，正常 SIGINT 收尾并用 ffprobe/解码检查 |
| 退出码 0，但 smoke 未通过 | 区分桌面清理状态与验收状态；看 marker、verification、runner 和 job 的最终结果 |
