# 桌面 runtime 与操控

## 接入目标应用

- **通用控制层：** `desktop_server.py` 和 `desktop_client.py` 面向整个 X11 桌面，截图、点击、键盘和拖动均不依赖应用类型，可用于 CUA / Computer Use Agent 操控不同软件。
- **准备应用：** 使用目标软件对应的系统镜像、官方安装方式和依赖。浏览器、编辑器、办公工具各自的安装包、启动命令、用户配置与就绪状态需要按应用设置。
- **启动适配：** `run_slicer.sh` 是已有 Slicer 参考实现。接入其他应用时，在项目副本中替换 Slicer 归档解压与启动部分，使用该软件的可执行文件和参数；保留 Xvfb/Openbox、PyAutoGUI 服务、会话信息、进程组清理、TTL 和录屏限制。
- **无需示例包：** 其他应用不需要下载 Slicer；`prepare_software.sh` 的固定包配置、`submit_rjob.sh` 的归档检查以及 Slicer 专用 smoke runner 都属于样例，需要随目标应用一起适配。
- **验证适配：** 选择目标应用的真实操作来确认输入，例如在编辑器输入并保存文档、在浏览器填写本地测试表单。Ctrl+3、Python 控制台和 VTK 球面只是 Slicer 示例，不能照搬到其他应用。

## 项目内布局

将 runtime 复制到用户自己的项目，参数由当前会话或项目私有配置提供。以下命令中的路径占位符需要替换，运行命令不写入 skill 安装目录。

```bash
SKILL_DIR="[SKILL_DIR]"
PROJECT_ROOT="[PROJECT_ROOT]"
mkdir -p "$PROJECT_ROOT/desktop"
cp -a "$SKILL_DIR/assets/runtime/." "$PROJECT_ROOT/desktop/"
```

| 文件 | 用途与执行位置 |
| --- | --- |
| `prepare_software.sh` | Slicer 应用样例：在联网准备容器中下载并校验，已有有效缓存直接退出 |
| `requirements.txt`、`install_runtime.sh` | 只在获准的临时 Ubuntu 容器中安装桌面组件、Qt 示例库和固定 Python 依赖；其他应用按需调整依赖 |
| `run_slicer.sh` | Slicer 启动样例，演示会话目录、进程组、时间和录屏上限，退出清理 |
| `desktop_server.py` | 在桌面容器中调用真实 PyAutoGUI；不调用模型 |
| `desktop_client.py` | 从开发机、其他容器或 SSH 转发端口发送手动请求；只依赖 Python 标准库 |
| `verify_desktop.py`、`rjob_run_smoke.sh` | 在目标容器中执行真实 Slicer 输入/渲染/视频验收；不在开发机运行 GUI |
| `submit_rjob.sh` | Slicer 参考 runner 的参数化 rjob 提交，支持 dry-run；其他应用适配 runner 和归档检查 |

## Slicer 参考实现：准备与启动

**执行位置：以下 apt、解压和 GUI 命令仅在获准的独立 Ubuntu 22.04 容器内运行。**

```bash
RUNTIME="[PROJECT_ROOT]/desktop"
export CUA_SOFTWARE_DIR="[PROJECT_ROOT]/software"

# 只在联网准备阶段需要；无集群代理时继承正常网络环境。
# export CUA_PROXY_SETUP_URL="[APPROVED_SETUP_PROXY_URL]"
bash "$RUNTIME/prepare_software.sh"
bash "$RUNTIME/install_runtime.sh"

# 后续桌面容器可离线使用已经准备好的 Python 包缓存。
export CUA_OFFLINE=1
export CUA_RUN_ID="desktop-$(date +%Y%m%d-%H%M%S)-$$"
bash "$RUNTIME/run_slicer.sh"
```

- **系统包：** `install_runtime.sh` 要在需要安装缺失 apt 包时以容器 root 运行。不要为了它取得宿主机特权或挂载 Docker socket。
- **默认路径：** 软件归档在 runtime 上一级的 `software/`，证据在同级 `artifacts/<run_id>/`；`CUA_SOFTWARE_DIR`、`CUA_ARTIFACT_DIR`、`SLICER_ARCHIVE` 可覆盖。
- **现成应用：** 已有 Slicer 安装可传 `SLICER_APP_DIR`，跳过解压；若所有运行库已经预装，可用 `CUA_INSTALL_RUNTIME=0` 和正确的 `CUA_PYTHON_LIB`。
- **路径与会话：** 使用新的 run ID，避免旧 `session.json` 被误当作本次就绪状态。一个 pod 默认一个桌面；同一容器并发会话需独立 DISPLAY、端口、Python target 和 run ID。
- **启动窗口：** 官方 `--python-code 'slicer.util.mainWindow().showMaximized()'` 直接最大化并避免首次启动提示框阻塞；这是应用初始化，不是 agent loop。

## session.json 与 HTTP

`session.json` 记录实际 IP、端口、DISPLAY、XAUTHORITY、Python 库目录和 token 文件路径。`control.token` 权限为 0600；脚本不把 token 打印到日志。

```bash
SESSION="[PROJECT_ROOT]/artifacts/[RUN_ID]/session.json"
python3 "$RUNTIME/desktop_client.py" "$SESSION"
python3 "$RUNTIME/desktop_client.py" "$SESSION" --screenshot ./desktop.png
python3 "$RUNTIME/desktop_client.py" "$SESSION" --action '{"type":"move","x":600,"y":400}'
python3 "$RUNTIME/desktop_client.py" "$SESSION" --action '{"type":"click","x":600,"y":400}'
python3 "$RUNTIME/desktop_client.py" "$SESSION" --action '{"type":"keypress","keys":["ctrl","3"]}'
python3 "$RUNTIME/desktop_client.py" "$SESSION" --action '{"type":"type","text":"print(123)"}'
python3 "$RUNTIME/desktop_client.py" "$SESSION" --action '{"type":"keypress","keys":["enter"]}'
```

| 接口或动作 | 语义 |
| --- | --- |
| GET `/healthz` | backend 应为 `pyautogui`，返回实际屏幕尺寸 |
| GET `/screenshot` | 由 `pyautogui.screenshot()` 返回 PNG |
| GET `/position` | 当前实际鼠标位置 |
| POST `/action` | 单个手动动作；不做策略规划或循环 |
| `click`、`double_click`、`move` | `x,y` 是原始桌面像素，需在屏幕范围内 |
| `drag` | `start` 和 `end` 各包含 `x,y`，当前使用鼠标左键 |
| `scroll` | `ticks` 向上为正，限制在 -20 到 20 |
| `keypress` | PyAutoGUI 键名列表，例如 `['ctrl','3']` |
| `type` | 对应 `pyautogui.write`，最多 10000 个 ASCII 字符；非 ASCII 明确拒绝 |
| `wait` | `seconds` 最多 10 秒 |

- **访问边界：** 默认绑定容器网卡并要求 Bearer token；HTTP 没有 TLS，适用于受控内网。集群外使用 SSH 转发，不直接暴露公网。客户端 URL 覆盖见 [04](04_rjob_and_acceptance.md)。
- **避免代理：** 内网控制请求使用不带外部代理的 urllib opener；不要把桌面 IP、127.0.0.1 流量转发给公共代理。
- **坐标：** 截图保持原始分辨率；缩放图像后若继续用旧坐标，输入位置会错。
- **输入诊断：** HTTP 200 只说明事件已发送；必须确认窗口焦点和应用结果。默认样例关闭 PyAutoGUI 的角落 FAILSAFE，由输入坐标校验、会话 TTL 和容器生命周期控制运行。

## 在桌面容器中直接调用 PyAutoGUI

```python
import json, os, sys
session = json.load(open('[PROJECT_ROOT]/artifacts/[RUN_ID]/session.json'))
os.environ['DISPLAY'] = session['display']
os.environ['XAUTHORITY'] = session['xauthority']
os.environ['XDG_SESSION_TYPE'] = 'x11'
sys.path.insert(0, session['python_lib'])
import pyautogui
pyautogui.moveTo(600, 400)
pyautogui.click()
pyautogui.screenshot().save('[PROJECT_ROOT]/desktop.png')
```

必须在导入 PyAutoGUI 之前设置 DISPLAY/XAUTHORITY。开发机的文件系统能读到 `session.json`，并不意味着它也能访问另一个容器的 X11 socket；跨容器使用 HTTP 接口。

## 录屏与停止

- **开启：** `CUA_RECORD_SCREEN=1`，可调 `CUA_RECORD_FPS` 和 `CUA_RECORD_MAX_BYTES`。默认关闭，5 FPS 是低开销示例，非所有任务的最佳帧率。
- **验证：** 不以文件存在或扩展名判断成功；用 ffprobe 检查 codec、分辨率、时长，必要时全片解码。停止时先向 FFmpeg 发送 SIGINT，让 MP4 完成封装。
- **停止：** 向 launcher 发 SIGTERM，或按集群规则删除专用 job。脚本停止进程组、删除会话临时目录、写出 `exit-code`；应用异常仍返回异常退出码。
- **状态区分：** 桌面 `exit-code=0` 只说明会话正常停止，不等于验收成功；还需 `verification.json`、录屏检查和 smoke runner 的退出状态。
