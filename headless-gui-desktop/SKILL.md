---
name: headless-gui-desktop
description: "为 CUA（Computer Use Agent）、computer use 和桌面自动化部署无头 GUI 桌面，让 agent 截图并通过 PyAutoGUI 操控浏览器、编辑器、办公工具及其他应用；覆盖 Linux 容器、CPU rjob、软件渲染、低存储缓存、可选录屏和真实应用验收。"
---

# 面向 CUA 的无头 GUI 桌面

## 默认方案与边界

- **适用范围：** 为 CUA / Computer Use Agent 提供通用软件桌面、截图和键鼠操作。目标应用可以是浏览器、编辑器、办公工具或其他 GUI 软件；按应用的系统、显示协议和渲染需求选择承载方式。
- **Linux 起点：** Ubuntu 22.04 + Xvfb + Openbox + Mesa llvmpipe + PyAutoGUI。优先使用官方二进制包；基础 GUI 可使用 CPU，应用明确要求 GPU 时另行评估。
- **隔离：** 这是容器内虚拟桌面，共享宿主机内核。用户确实需要独立内核、其他操作系统或更强隔离时，再选择具备 KVM 的 VM；不能把容器称为硬件虚拟机。Linux rjob 不适合运行 macOS。
- **执行位置：** 开发机只做编辑、轻量检查、提交和监控。apt、应用解压、GUI 和录屏放在获准的独立容器/worker/job；不修改开发机、共享 conda、shell 启动文件或公共软件目录。
- **资源起点：** 按目标应用实测 CPU、内存、分辨率和交互延迟。现有参考样例在 2 CPU / 8000 MiB / 0 GPU、1440×900 下通过测试，不将单个应用的结果外推为所有软件的资源保证。
- **存储：** 软件包缓存一份、会话临时解压、退出清理；录屏默认关闭。设置运行时间和视频体积上限，保留必要证据，避免每次任务永久复制应用和缓存。
- **控制范围：** 只提供截图、键鼠和可选录屏。模型、API key、自主策略和 agent loop 由用户另行指定，不能因“computer use”自动加入。

## 工作流

1. **判断环境：** 检查 CPU 配额、内存、架构、共享存储、容器权限及实际显示设备。没有 `/dev/kvm`、`/dev/dri` 或 NVIDIA 设备不妨碍 Xvfb + CPU OpenGL。
2. **准备软件：** 核对用户指定应用的官方版本、安装方式、运行依赖和校验值；缓存应用安装包及固定 Python 依赖。慢下载先确认真实文件接口和 Range 行为，不能只增加连接数。
3. **部署桌面：** 将 `assets/runtime/` 复制到用户项目，按 [02](references/02_runtime_and_control.md) 安装桌面组件并接入目标应用。通用控制接口可直接复用，应用启动和验收脚本按目标软件适配；不要把缓存、视频和 token 写入 skill 安装目录。
4. **验证应用：** 检查 PyAutoGUI、目标窗口就绪、真实键盘执行结果、鼠标交互、PNG 和可选视频；使用 3D 的应用还需核对实际渲染器。占位窗口、Xvfb 存活或 `glxinfo` 成功均不能单独证明目标软件可用。
5. **交付：** 给出启动/停止方法、实际截图、日志位置、资源与磁盘统计、已测和未测范围；删除一次性测试 job。

## 版本锚点

- **桌面控制基线（2026-11-05）：** Ubuntu 22.04、PyAutoGUI 0.9.54、PyScreeze 1.0.1；其余 Python 依赖固定在 `assets/runtime/requirements.txt`。Slicer 5.12.4 是已验证的应用示例，其版本、下载和测量保留在 [03](references/03_download_and_dependencies.md) 与 [04](references/04_rjob_and_acceptance.md)。
- **PyAutoGUI：** 核对时上游 master HEAD 为 `b4255d0be42c377154c7d92337d7f8515fc63234`。HEAD 仅为漂移检查锚点，实际运行使用固定发布版。
- 更新版本前重新核对官方要求、包元数据、CLI help 和相关配置；HEAD 或版本变化不意味着自动升级。完整文档与元数据入口见 [03](references/03_download_and_dependencies.md)。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 为 CUA 选择容器虚拟桌面、KVM 或原生系统，说明不同应用的 CPU 渲染边界、显示要求和共享缓存/临时解压/视频预算。 | CUA, Computer Use Agent, GUI, Ubuntu, Xvfb, Openbox, llvmpipe, KVM, OpenGL, CPU, 存储 | 选择部署方案前读取；承诺无需 GPU 前读取；估算磁盘或多会话开销前读取 | [references/01_architecture_and_budget.md](references/01_architecture_and_budget.md) |
| 02 | 说明通用 PyAutoGUI 控制接口和目标应用适配方式，提供 session.json、HTTP 操作、进程清理以及 Slicer 参考启动样例。 | CUA, GUI automation, desktop_server.py, PyAutoGUI, screenshot, session.json, Xauthority, token, FFmpeg, 焦点 | 首次接入目标应用前读取；截图或控制桌面前读取；调整会话生命周期或处理输入失效时读取 | [references/02_runtime_and_control.md](references/02_runtime_and_control.md) |
| 03 | 说明目标应用的官方安装包、依赖与离线缓存准备，用 Slicer 示例保留 SHA512、Girder Range 差异及有界 curl 分段续传。 | GUI, 安装包, Range, curl, SHA512, resume, pip, PyAutoGUI, 离线缓存, Slicer | 首次下载或切换应用版本前读取；下载过慢或分段占盘异常时读取；安装依赖或配置离线启动前读取 | [references/03_download_and_dependencies.md](references/03_download_and_dependencies.md) |
| 04 | 给出参数化 rjob、CPU 队列与 0 GPU 回退、内网服务转发，以及不同应用的 CUA 输入和录屏验收方法；保留 Slicer 测量样例。 | CUA, computer use, rjob, dry-run, predict-only, gpu=0, SSH, ffprobe, 输入验证, Succeeded | 提交集群任务或改分区前读取；判断排队和无日志错误前读取；最终验收、清理和汇报性能前读取 | [references/04_rjob_and_acceptance.md](references/04_rjob_and_acceptance.md) |
