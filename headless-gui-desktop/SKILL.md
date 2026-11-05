---
name: headless-gui-desktop
description: "为 CUA（Computer Use Agent）和桌面自动化部署可截图、可用 PyAutoGUI 操控的无头 GUI 桌面；覆盖 Linux 容器、CPU rjob、低存储缓存、文件隔离、干净基线重建、产物导出，以及按用户要求接入现有 agent。"
---

# 面向 CUA 的无头 GUI 桌面

## 默认方案与边界

- **适用范围：** 为 CUA / Computer Use Agent 提供通用软件桌面、截图和键鼠操作。目标应用可以是浏览器、编辑器、办公工具或其他 GUI 软件；按应用的系统、显示协议和渲染需求选择承载方式。
- **Linux 起点：** Ubuntu 22.04 + Xvfb + Openbox + Mesa llvmpipe + PyAutoGUI。优先使用官方二进制包；基础 GUI 可使用 CPU，应用明确要求 GPU 时另行评估。
- **隔离：** 这是容器内虚拟桌面，共享宿主机内核。用户确实需要独立内核、其他操作系统或更强隔离时，再选择具备 KVM 的 VM；不能把容器称为硬件虚拟机。Linux rjob 不适合运行 macOS。
- **文件边界：** 共享目录可用于部署和导出；独立 HOME、普通 UID 或新容器本身不保证 agent 无法写入可写挂载。按用户要求确认 agent 可访问的路径、挂载和权限，复原/导出验收见 [05](references/05_isolation_reset_and_export.md)。
- **执行位置：** 开发机只做编辑、轻量检查、提交和监控。apt、应用解压、GUI 和录屏放在获准的独立容器/worker/job；不修改开发机、共享 conda、shell 启动文件或公共软件目录。
- **资源起点：** 按目标应用实测 CPU、内存、分辨率和交互延迟。现有参考样例在 2 CPU / 8000 MiB / 0 GPU、1440×900 下通过测试，不将单个应用的结果外推为所有软件的资源保证。
- **存储：** 软件包缓存一份、会话临时解压、退出清理；录屏默认关闭。设置运行时间和视频体积上限，保留必要证据，避免每次任务永久复制应用和缓存。
- **控制范围：** 默认只提供截图、键鼠和可选录屏。用户要求接入已有 agent 时，按 [06](references/06_existing_agent_integration.md) 复用其模型循环；模型服务、凭据和执行任务由用户指定，不能因“computer use”自动加入自主任务或另写 agent loop。

## 工作流

1. **判断环境：** 检查 CPU 配额、内存、架构、共享存储、容器权限及实际显示设备。没有 `/dev/kvm`、`/dev/dri` 或 NVIDIA 设备不妨碍 Xvfb + CPU OpenGL。
2. **准备软件：** 核对用户指定应用的官方版本、安装方式、运行依赖和校验值；缓存应用安装包及固定 Python 依赖。慢下载先确认真实文件接口和 Range 行为，不能只增加连接数。
3. **部署桌面：** 将 `assets/runtime/` 复制到用户项目，按 [02](references/02_runtime_and_control.md) 安装桌面组件并接入目标应用。通用控制接口可直接复用，应用启动和验收脚本按目标软件适配；不要把缓存、视频和 token 写入 skill 安装目录。
4. **验证应用：** 检查 PyAutoGUI、目标窗口就绪、真实键盘执行结果、鼠标交互、PNG 和可选视频；使用 3D 的应用还需核对实际渲染器。占位窗口、Xvfb 存活或 `glxinfo` 成功均不能单独证明目标软件可用。
5. **按需接入 agent：** 先验证不调用模型的桌面能力，再用用户指定的既有 agent 做有步数/时间上限的真实任务；检查原生工具调用、应用文件回读和完成信号，不能用手动输入替代模型验收。
6. **验证文件生命周期：** 需要限制会话外写入、复原或导出时，核对有效挂载/权限，比较 A 会话修改与全新 B 会话的基线，并在删除 job 前导出、校验产物。干净重建不等于运行中快照。
7. **交付：** 给出启动/停止方法、实际截图、日志位置、资源与磁盘统计、已测和未测范围；删除一次性测试 job。密钥、代理配置和本地运行证据不放入 skill。

## 版本锚点

- **桌面控制基线（2026-11-05）：** Ubuntu 22.04、PyAutoGUI 0.9.54、PyScreeze 1.0.1；其余 Python 依赖固定在 `assets/runtime/requirements.txt`。Slicer 5.12.4 是已验证的应用示例，其版本、下载和测量保留在 [03](references/03_download_and_dependencies.md) 与 [04](references/04_rjob_and_acceptance.md)。
- **PyAutoGUI：** 核对时上游 master HEAD 为 `b4255d0be42c377154c7d92337d7f8515fc63234`。HEAD 仅为漂移检查锚点，实际运行使用固定发布版。
- 更新版本前重新核对官方要求、包元数据、CLI help 和相关配置；HEAD 或版本变化不意味着自动升级。完整文档与元数据入口见 [03](references/03_download_and_dependencies.md)。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 为 CUA 选择容器虚拟桌面、KVM 或原生系统，说明不同应用的 CPU 渲染边界、显示要求和共享缓存/临时解压/视频预算。 | CUA, Computer Use Agent, GUI, Ubuntu, Xvfb, Openbox, llvmpipe, KVM, OpenGL, CPU, 存储 | 选择部署方案前读取；承诺无需 GPU 前读取；估算磁盘或多会话开销前读取 | [references/01_architecture_and_budget.md](references/01_architecture_and_budget.md) |
| 02 | 说明通用 PyAutoGUI 控制接口和目标应用适配方式，提供 session.json、HTTP 操作、进程清理以及 Slicer 参考启动样例。 | CUA, GUI automation, desktop_server.py, PyAutoGUI, screenshot, session.json, Xauthority, token, FFmpeg, 焦点 | 首次接入目标应用前读取；截图或控制桌面前读取；调整会话生命周期或处理输入失效时读取 | [references/02_runtime_and_control.md](references/02_runtime_and_control.md) |
| 03 | 说明官方安装包、独立 Python venv、wheel 缓存与容量统计；保留 Slicer 的 SHA512、Girder Range 差异及有界 curl 分段续传。 | GUI, 安装包, Range, curl, SHA512, resume, pip, venv, wheel, bdist_wheel, PyAutoGUI, 离线缓存, Slicer | 首次下载或切换应用版本前读取；下载过慢或分段占盘异常时读取；安装依赖、修复打包错误或配置离线启动前读取 | [references/03_download_and_dependencies.md](references/03_download_and_dependencies.md) |
| 04 | 给出共享挂载与独立代码包两种 rjob 模式、CPU 队列回退和内网转发，以及应用输入、录屏验收与 Slicer 测量样例。 | CUA, computer use, rjob, --folder, .rjobignore, dry-run, predict-only, gpu=0, SSH, ffprobe, 输入验证, Succeeded | 提交集群任务、上传代码包或改分区前读取；判断排队和无日志错误前读取；最终验收、清理和汇报性能前读取 | [references/04_rjob_and_acceptance.md](references/04_rjob_and_acceptance.md) |
| 05 | 区分共享挂载与 agent 可写权限、容器与硬件 VM、干净重建与内存快照；说明 A/B 基线验收、认证导出、凭据排除和接收端文件校验。 | 隔离, mount, UID, ACL, canary, baseline, reset, snapshot, export, SHA256, tar, 凭据 | 承诺会话外文件不受影响前读取；实现恢复或销毁重建前读取；打包/下载日志截图与删除 job 前读取 | [references/05_isolation_reset_and_export.md](references/05_isolation_reset_and_export.md) |
| 06 | 说明在独立 Python 环境接入现有 CUA agent，保存私有 .env 并运行有界真实模型任务；记录 IrisGUI 的中英文保存验收、权限排错及测量边界。 | CUA, IrisGUI, venv, wheel, .env, API key, native tools, scrot, xclip, Tk, pynput, timeout | 用户要求安装或测试已有 agent 时读取；配置远端模型与持久凭据前读取；排查普通用户截图、中文输入或模型超时时读取 | [references/06_existing_agent_integration.md](references/06_existing_agent_integration.md) |
