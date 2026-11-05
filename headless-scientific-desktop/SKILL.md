---
name: headless-scientific-desktop
description: "在无头 Linux 容器或 CPU rjob 中部署可截图、可用 PyAutoGUI 操控的科学软件桌面；覆盖 Ubuntu、Slicer/Qt/VTK、CPU OpenGL、低存储缓存、可选录屏和真实 GUI 验收，不包含模型调用或 agent loop。"
---

# 无头科学软件桌面

## 默认方案与边界

- **栈：** Ubuntu 22.04 + Xvfb + Openbox + Mesa llvmpipe + PyAutoGUI；Slicer 是已实测的 Qt/VTK 应用样例。优先使用官方 Linux 二进制包，无需 GPU、CUDA 编译、完整桌面发行版或嵌套虚拟机。
- **隔离：** 这是容器内虚拟桌面，共享宿主机内核。用户确实需要独立内核、其他操作系统或更强隔离时，再选择具备 KVM 的 VM；不能把容器称为硬件虚拟机。Linux rjob 不适合运行 macOS。
- **执行位置：** 开发机只做编辑、轻量检查、提交和监控。apt、应用解压、GUI 和录屏放在获准的独立容器/worker/job；不修改开发机、共享 conda、shell 启动文件或公共软件目录。
- **资源起点：** 基础 Slicer GUI 已在 2 CPU / 8000 MiB / 0 GPU、1440×900 下通过测试。复杂影像和分割计算按实际负载另测；不能将基础球面测试当作大型医学任务的性能保证。
- **存储：** 软件包缓存一份、会话临时解压、退出清理；录屏默认关闭。设置运行时间和视频体积上限，保留必要证据，避免每次任务永久复制应用和缓存。
- **控制范围：** 只提供截图、键鼠和可选录屏。模型、API key、自主策略和 agent loop 由用户另行指定，不能因“computer use”自动加入。

## 工作流

1. **判断环境：** 检查 CPU 配额、内存、架构、共享存储、容器权限及实际显示设备。没有 `/dev/kvm`、`/dev/dri` 或 NVIDIA 设备不妨碍 Xvfb + CPU OpenGL。
2. **准备软件：** 在联网准备任务中核对官方版本、文件元数据和校验值；缓存 Slicer 及固定 Python 依赖，随后会话离线复用。慢下载先确认真实文件接口和 Range 行为，不能只增加连接数。
3. **部署桌面：** 将 `assets/runtime/` 复制到用户项目，按 [02](references/02_runtime_and_control.md) 在临时容器中安装运行依赖并启动；不要把缓存、视频和 token 写入 skill 安装目录。
4. **验证应用：** 检查 PyAutoGUI、应用级渲染器、真实键盘执行结果、鼠标交互、PNG 和实际视频。Qt 占位窗口、Xvfb 存活或 `glxinfo` 成功均不能单独证明目标软件可用。
5. **交付：** 给出启动/停止方法、实际截图、日志位置、资源与磁盘统计、已测和未测范围；删除一次性测试 job。

## 版本锚点

- **实测组合（2026-11-05）：** Ubuntu 22.04、Slicer 5.12.4 Stable、PyAutoGUI 0.9.54、PyScreeze 1.0.1；其余 Python 依赖固定在 `assets/runtime/requirements.txt`。
- **Slicer：** 发布标签 `v5.12.4` 对应 commit `4e21c19d8360242d88d6ca2490bf52400441b8e1`；核对时上游 main HEAD 为 `feb57a512b51d7eec11a1edb46e00897528e7aa9`。
- **PyAutoGUI：** 核对时上游 master HEAD 为 `b4255d0be42c377154c7d92337d7f8515fc63234`。HEAD 仅为漂移检查锚点，实际运行使用固定发布版。
- 更新版本前重新核对官方要求、包元数据、CLI help 和相关配置；HEAD 或版本变化不意味着自动升级。完整文档与元数据入口见 [03](references/03_download_and_dependencies.md)。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 选择容器虚拟桌面、KVM 或原生系统，说明 Xvfb/llvmpipe 的 CPU 渲染边界、显示要求和共享缓存/临时解压/视频预算。 | Ubuntu, Xvfb, Openbox, llvmpipe, KVM, macOS, OpenGL, CPU, 内存, 存储 | 选择部署方案前读取；承诺无需 GPU 前读取；估算磁盘或多会话开销前读取 | [references/01_architecture_and_budget.md](references/01_architecture_and_budget.md) |
| 02 | 提供项目内 runtime 的安装启动、session.json、真实 PyAutoGUI HTTP 操作及进程清理方式，说明 token、ASCII、Xauthority 与首次启动窗口焦点。 | run_slicer.sh, desktop_server.py, PyAutoGUI, screenshot, session.json, Xauthority, token, FFmpeg, 焦点, ASCII | 首次使用脚本前读取；截图或控制桌面前读取；调整会话生命周期或处理输入失效时读取 | [references/02_runtime_and_control.md](references/02_runtime_and_control.md) |
| 03 | 说明官方稳定包元数据与 SHA512、Girder item/file 的 Range 差异、有界 curl 分段续传，以及 Ubuntu 库和离线 PyAutoGUI 安装。 | Slicer, Girder, Range, curl, SHA512, resume, pip, python3-tk, scrot, qt5dxcb-plugin | 首次下载或切换版本前读取；下载过慢或分段占盘异常时读取；安装依赖或配置离线启动前读取 | [references/03_download_and_dependencies.md](references/03_download_and_dependencies.md) |
| 04 | 给出参数化 rjob 提交、CPU 队列与 0 GPU 回退边界、内网服务转发和真实 Slicer/VTK/录屏验收；保留测量条件与常见失败判据。 | rjob, dry-run, predict-only, gpu=0, private-machine, host-network, SSH, ffprobe, VTK, Succeeded | 提交集群任务或改分区前读取；判断排队和无日志错误前读取；最终验收、清理和汇报性能前读取 | [references/04_rjob_and_acceptance.md](references/04_rjob_and_acceptance.md) |
