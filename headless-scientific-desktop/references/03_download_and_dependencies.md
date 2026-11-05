# 下载、版本与依赖

## 官方入口与版本核对

先读目标软件的官方安装说明、系统要求和当前 CLI help，再为具体错误追源码。以下链接在 2026-11-05 用 HTTP HEAD/GET 核对：

- **固定发布版安装要求：** [Slicer v5.12.4 getting_started.md](https://raw.githubusercontent.com/Slicer/Slicer/v5.12.4/Docs/user_guide/getting_started.md)，对应 runtime 使用的版本。
- **发布页：** [Slicer v5.12.4](https://github.com/Slicer/Slicer/releases/tag/v5.12.4)。更换版本时从官方 [下载入口](https://download.slicer.org/) 重新取得包信息。
- **滚动文档入口：** [Slicer getting started](https://slicer.readthedocs.io/en/latest/user_guide/getting_started.html)。此处 latest 不与本地发布版绑定；具体参数以固定发布版文档和 CLI help 为准。不能假设 `/en/5.12/` 存在，本次该路径返回 404。
- **PyAutoGUI：** [quickstart](https://pyautogui.readthedocs.io/en/latest/quickstart.html) 为滚动文档；运行版本固定为 0.9.54。
- **启动提示实现：** [v5.12.4 qSlicerMainWindow.cxx](https://github.com/Slicer/Slicer/blob/v5.12.4/Base/QTApp/qSlicerMainWindow.cxx) 可只读核对 `disclaimer()` 对启动 Python code/script 的处理，不修改上游源码。

```bash
# 在准备/运行容器内核对实际版本及帮助。
"$SLICER_APP_DIR/Slicer" --help
PYTHONPATH="$CUA_PYTHON_LIB" /usr/bin/python3 -c \
  'from importlib.metadata import version; print(version("PyAutoGUI")); print(version("PyScreeze"))'

# 维护版本锚点时使用当前已授权的 GitHub 访问方式。
git ls-remote https://github.com/Slicer/Slicer.git refs/heads/main refs/tags/v5.12.4
git ls-remote https://github.com/asweigart/pyautogui.git refs/heads/master
```

## 归档与真实文件接口

固定样例为 `Slicer-5.12.4-linux-amd64.tar.gz`，在目标 CPU 架构为 amd64 时使用；其他架构应重新选包，不能直接套用。

- **官方文件元数据：** `https://slicer-packages.kitware.com/api/v1/file/6aa1bec1ce9de556d3010212`
- **支持 Range 的文件下载：** `https://slicer-packages.kitware.com/api/v1/file/6aa1bec1ce9de556d3010212/download`
- **总大小：** `498717156` 字节。
- **SHA512：** `ac76c5061a8fff20d4e59732855f74360930fd4891450085bcbc6a8eb1a1f4ade9a1ca4fc633142661b714dbe8c4604306079f9546e52053faa5e6f99410cf76`。

这些值与官方元数据一致，不是从第三方下载站复制。更新版本时同时更新 URL、大小、归档名和 SHA512；只改文件名会让续传和完整性判断失效。

## 慢下载的诊断与处理

- **先区分 item 与 file：** download.slicer.org 的 bitstream 跳转可能落到 Girder item 下载接口；本次 item 接口忽略 Range，真实 file 接口支持 Range。不能把它推广成所有服务都支持分段。
- **小范围探针：** 先请求几 KiB，检查 `206 Partial Content`、`Content-Range`、响应大小和重定向最终 URL。若收到完整 `200`，改用正确接口或正常串行下载。
- **成熟工具：** 单连接和 aria2 16 连接在本次网络中很慢；系统 curl 的有界并行 Range 请求最终完成下载。不因此要求每个环境都用 64 连接；先测吞吐，允许降低并发。
- **脚本机制：** `prepare_software.sh` 默认 512 KiB 分段、最多 64 并发、每段重试和超时、总调用 900 秒；已有长度正确的分段复用，合并后检验 SHA512，成功后删除分段。长度只用于续传判断，完整性以最终校验为准。
- **防膨胀：** 每段 curl `max-filesize` 等于该段字节数；下载子进程同时用 `ulimit -f` 限制每个输出文件。旧 curl 在没有 Content-Length 时未必执行 max-filesize，不能只靠该参数承诺磁盘上限。系统限制按 KiB 向上取整，默认段大小为 512 KiB；最后一段还需精确长度检查。部分分段即使大小正确，内容仍可能错误，必须保留最终 SHA512。
- **失败恢复：** 不发布未校验归档；检查 `download.log`，保留部分下载以续传。最终 SHA512 失败时先检查版本参数、接口和缓存；只清理本任务生成的 `.parts`、`.part`，不删除其他软件缓存。一个缓存目录只运行一个准备任务。

```bash
# 在联网准备容器内运行；正常网络可不提供代理 setup URL。
export CUA_SOFTWARE_DIR="[PROJECT_ROOT]/software"
export CUA_DOWNLOAD_PARALLEL=16
bash "[PROJECT_ROOT]/desktop/prepare_software.sh"
```

脚本还接受 `SLICER_DOWNLOAD_URL`、`SLICER_ARCHIVE_NAME`、`SLICER_SIZE_BYTES`、`SLICER_SHA512`、`CUA_DOWNLOAD_CHUNK_BYTES`；默认值组成一个不可混用的发布版配置。`CUA_PROXY_SETUP_URL` 只能来自当前已获准的环境配置，脚本完整下载、语法检查后加载，不记录真实代理值或凭据。已有有效归档时先校验并退出，不调用代理 setup。

## Ubuntu 与 Python 依赖

- **官方 Slicer 库：** 包括 `libglu1-mesa`、`libpulse-mainloop-glib0`、`libnss3`、`libasound2`、`qt5dxcb-plugin`、`libsm6`。不要只装 Xvfb 后就把 xcb/GL 错误归因于 GPU。
- **桌面与截图：** `xvfb`、`openbox`、`xauth`、`x11-utils`、`mesa-utils`、Mesa DRI、`scrot`、`python3-tk`、`python3-pil`；录屏用系统 FFmpeg/libx264。
- **PyAutoGUI 安装：** 本次 Ubuntu 仓库没有 `python3-pyautogui`。使用固定 PyPI 发布包，依赖由 `requirements.txt` 列全；不依赖 xdotool 悄悄替代 PyAutoGUI。
- **纯 Python：** pip 源码包会执行常规 Python 打包步骤，但不涉及 GPU、CUDA 或 Slicer 源码编译。Pillow/Tk 从 apt 取得，避免现场编译它们。
- **离线复用：** `install_runtime.sh` 首次缓存 Python 归档，然后通过 `--no-index --no-deps --no-build-isolation --target` 安装到独立目录；`CUA_OFFLINE=1` 时缺少缓存应明确失败，不偷偷联网。
- **准备顺序：** 一个联网容器运行 `prepare_software.sh` 和 `install_runtime.sh`；后续 job 复用缓存。apt 仍通过当前容器配置的软件源安装，离线 Python 不等于完全无需 apt 网络。
- **预构建镜像：** 高频启动可将这些系统依赖和 Python target 预装到派生镜像，Slicer 归档继续挂载共享缓存。该方式可省安装时间，但本次没有构建/验证派生镜像，不能写成已经可用的镜像地址。

## 下载器的低开销回归

```bash
python3 "[SKILL_DIR]/scripts/test_download.py"
```

使用本地 HTTP fixture 验证 Range 续传、有效缓存不联网、校验失败不发布，以及有/无 Content-Length 的服务忽略 Range 时限制占盘；只产生 KiB 级临时数据。它验证下载协议和磁盘约束，不替代真实 Slicer GUI 验收。
