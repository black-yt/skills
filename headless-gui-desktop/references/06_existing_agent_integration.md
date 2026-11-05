# 接入已有 CUA agent 与真实模型验收

## 保留用户选择与上游实现

- **启用条件：** 用户要求安装/测试现有 agent 时再接入模型；仅请求桌面、截图或 PyAutoGUI 时不自动添加。使用用户指定的软件和模型服务，不另写循环替换上游 agent。
- **先读官方说明：** 核对当前仓库 README、requirements、配置示例和启动方式。先确认系统/Python/显示依赖，再为具体失败只读检查源码。
- **分两阶段：** 先做不调用模型的导入、窗口、输入、截图与依赖检查；随后才做用户要求的有界模型任务。成功安装/导入不等于模型已经操作过电脑。
- **独立环境：** 在获准的容器内创建 venv，固定依赖并缓存 wheel；联网和 Python 安装不要求物理 GPU。准备步骤见 [03](03_download_and_dependencies.md#独立-python-环境与-wheel-缓存)。

## 模型配置与凭据生命周期

- **持久保存：** 用户要求记住配置时，使用项目私有 `.env`，权限 `600`，加入 Git 忽略规则；已有文件先保留其内容，只更新本任务需要的字段。不写 shell profile、共享 conda 或 skill 安装目录。
- **上游字段：** 按应用实际要求填写 endpoint/key/model；例如 IrisGUI 使用 `LLM_API_ENDPOINT`、`LLM_API_KEY`、`LLM_MODEL_NAME`，不能无条件换成 SDK 的其他变量名。
- **注入：** `.env` 排除于上传包、模型输入、截图和导出归档。由用户选择的安全运行时配置机制传入会话；不要把真实 key 放进 `rjob --env` 命令、可见 job 注解或 PR。
- **接口：** 模型服务需支持图像与所用工具调用协议；给出兼容的 base URL 和模型名，确认当前代理/TLS 设置。联网测试只输出状态，不打印代理 URL、全量环境或 Authorization。
- **控制令牌：** 桌面/导出服务的 token 与模型 key 分开；内网控制流量绕过外部代理。共享目录不是模型 key 的默认公开交换区。

## 有界真实任务

以文本编辑器为例，选择一个容易独立验收的任务：让模型通过 GUI 输入指定中英文、保存当前文件、另存新文件，并保持结果可见。控制端准备初始文件和验收值，**不替模型执行目标输入或写入期望结果**。

1. **启动桌面与应用：** 设置 DISPLAY/XAUTHORITY 后再导入 PyAutoGUI；等待真实目标窗口和焦点就绪，处理首次运行提示。
2. **运行上游 agent：** 使用其正式入口或控制器，保留上游截图、工具执行和终止逻辑。为样例指定步数/请求/总时长上限及截图保留轮数；不要默认无限重试或保留全部图像历史。
3. **观察证据：** 保存真实模型响应、工具名/参数、执行反馈和截图；检查错误、超时、工具调用及最终完成信号。图像网格 ID 与绝对像素接口不同，按该 agent 的坐标协议使用。
4. **独立回读：** 在容器内从应用保存的文件读回内容，核对文件名和路径，打开实际截图，并在需要时验证录屏。模型说“完成”、输入事件成功或退出码为 0 均不能替代文件结果。
5. **停止与导出：** 区分任务完成和进程退出；部分 agent 完成后保留 GUI 主循环。保存证据后停止该会话的进程组，按 [05](05_isolation_reset_and_export.md) 导出并验证重建。

## 常见安装与输入问题

| 表现 | 排查与实测经验 |
| --- | --- |
| venv 构建旧包报 `invalid command 'bdist_wheel'` | 在该 venv 安装 wheel/setuptools 后再构建；不要为此改全局 Python，已测引导版本见 [03](03_download_and_dependencies.md#独立-python-环境与-wheel-缓存) |
| pynput 的 Linux 依赖需要编译 | evdev 可能需要 gcc、python3-dev、linux-libc-dev；这是小型 CPU 构建，准备后缓存匹配 Python/架构的 wheel，不是 CUDA 编译 |
| 切换普通用户后无法执行 Python | 检查 venv 及所有父目录的读/执行权限；root 安装时的 `umask 077` 可能使目录仅 root 可访问 |
| 鼠标能动，截图却报 scrot Permission denied/FileNotFoundError | scrot 后端会在 cwd 创建临时 PNG；切到该会话用户可写的 HOME/工作目录，核对 Xauthority 和 scrot，不靠开放整个共享目录写权限修复 |
| 中文输入失败 | `pyautogui.write` 主要处理 ASCII；核对上游的剪贴板粘贴实现、xclip/xsel 与目标应用的粘贴键。中文显示还需字体，不能只看输入事件返回成功 |
| 同进程 Tk 输入测试丢事件或粘贴错乱 | 保持目标 GUI 主线程处理事件，让注入动作在其他线程执行；否则会把测试阻塞误判成 agent/剪贴板故障 |
| 全选/键盘行为与预期不同 | Linux Tk Entry 的 Ctrl+A/Ctrl+E 常为行首/行尾；Mousepad 的 Ctrl+A 是全选。独立验证键盘与中英文回读，不套用浏览器快捷键 |
| 模型请求超时或未调用工具 | 记录失败，不计入成功响应；按上游错误处理和任务预算继续或停止，不能无限消耗请求。任务是否成功仍由实际结果与完成信号判断 |

## IrisGUI 实测示例

这是现有 agent 的一个示例，不把本 skill 绑定为某一 agent，也不要求其他 GUI 软件安装它。2026-11-05 测试版本：仓库提交 `67bd64ab9510ac4f7c886f2ef07411af6668e002`，上游源码未修改；Python 3.10.12、PyAutoGUI 0.9.54、Pillow 12.3.0、pynput 1.8.2、OpenAI SDK 3.42.0。无独立应用版本号，以提交作为本次实例锚点，更新时重新核对要求。

官方入口（同日 HTTP GET 核对的固定提交文件）：

- [README 与安装说明](https://github.com/black-yt/IrisGUI/blob/67bd64ab9510ac4f7c886f2ef07411af6668e002/README.md)
- [requirements.txt](https://github.com/black-yt/IrisGUI/blob/67bd64ab9510ac4f7c886f2ef07411af6668e002/requirements.txt)
- [.env.example](https://github.com/black-yt/IrisGUI/blob/67bd64ab9510ac4f7c886f2ef07411af6668e002/.env.example)

**启动：** `python main.py` 提供任务编辑器，用户提交任务后由上游控制器运行。需要程序化启动已指定任务时，可在容器内复用控制器，而不是编写另一套 `step()` 循环：

```python
# 在配置、DISPLAY/XAUTHORITY 和目标应用就绪后，从 IrisGUI checkout 运行。
from main import IrisController

controller = IrisController('[USER_SPECIFIED_TASK]')
controller.start()
```

**配置：** 已测使用 `DEBUG_MODE=True` 保存任务日志与原始/全局/局部截图，`LOG_WINDOW_MODE=hidden` 避免日志浮窗遮挡目标应用，`MAX_STEPS=35`、`MEMORY_IMAGE_ROUNDS=2`、请求超时 90 秒、SDK 重试 0，外部监督任务总时长 600 秒。它们是本次预算，不是所有应用的固定配置。全局三次 ESC 可触发上游退出，另保留会话进程组和 job TTL。

| 范围 | 观测与边界 |
| --- | --- |
| 基础桌面/Python | Ubuntu 22.04、Xvfb/Openbox、1440×900，2 CPU / 3000 MiB / 0 GPU；不调用模型的安装检查峰值内存约 482 MiB，不是模型任务或大型应用峰值 |
| 持久存储 | GPFS `du -sk` 统计：venv 约 376.6 MiB、wheel 缓存 16.7 MiB、源码 5.0 MiB，总计约 398.3 MiB；不包含容器镜像层或其他应用归档 |
| 独立代码包部署 | 上传包约 20 MiB；两次容器内准备约 23/22 秒，依赖内部 apt 源和离线 wheel，不包含排队/拉镜像；不是所有环境的启动 SLA |
| 真实模型操作 | Mousepad 中英文输入、保存并另存成功；8 轮中有一次 90 秒超时，7 个成功响应、9 个原生工具调用，最终文件回读匹配且调用 final_answer |
| 录屏与导出 | H.264 / 1440×900 / 181 秒 / 243,471 字节；产物导出与 A/B 重建结果见 [05](05_isolation_reset_and_export.md#已测实例的解释) |

只公开方法、版本、资源和结果量级；密钥、私有服务地址、本地路径、job/节点标识、运行日志和截图不随 skill 发布。长期稳定性、多会话吞吐及其他软件仍需各自验收。
