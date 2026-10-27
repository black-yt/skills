---
name: h3-video-api
description: "调用内网部署的 MiniMax-H3 视频 Generation API（SSH 隧道 + curl，无 SDK）：隧道保活、素材上传、文本/首帧/参考模式提交、轮询下载的完整流程与提示词结构。服务下线时接口不可用属正常。"
---

# H3 视频生成 API 调用

内网部署的 MiniMax-H3「文生视频 + 同步声音」服务（一张 H200，`BASE_URL` 文档示例为 `http://127.0.0.1:18083`，实际地址以提供者给的为准）。**该接口由个人部署，不保证长期开放；连不上就是关了，属正常情况，别反复硬连。**

## 什么时候用

- 用户想让 H3 生成一段视频（文本描述 → 视频，或用照片/视频/音频做参考、首尾帧）
- 服务可用性检查：`curl --noproxy '*' $BASE_URL/healthz` 返回 `{"ready":true,...}` 才能用；连不上即服务未开放

## 完整流程

### 1. 建 SSH 隧道（本机 → 开发机 → 内网）

先读「连通性：分层诊断」一节——隧道连不上时，问题多数在本机这一层，不在跳板机或服务。

#### 1a. 常规直连（本机能直出内网时）

```bash
ssh -N -T -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:18083:<内网服务IP（会变，以服务提供者最新通知为准）>:18083 \
  <跳板机用户名>@<跳板机地址>
```

- **必须**用 `run_in_background` 且显式给 `timeout: 7200000`（2 小时）——不写 timeout 时默认 10 分钟就被超时机制杀掉， tunnel 断了轮询会跟着 JSON 解析报错
- 隧道断开**不影响**服务端已提交的生成任务，重连后用原任务 ID 继续查询/下载
- 所有 curl 加 `--noproxy '*'`（本机走了外网代理，不加会连 127.0.0.1 失败）

#### 1b. 本机连不上跳板机时：从宿主侧建隧道（2026-10-26 实测可行）

本机（WSL）出站被中间层劫持时，直连和经代理的 SSH 都会超时，但**宿主侧网络是通的**。此时不要怀疑跳板机或服务，改从宿主侧绕：

```bash
# 先确认宿主侧能到跳板机（TcpTestSucceeded : True 即通）
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe \
  -Command "Test-NetConnection -ComputerName <跳板机域名> -Port 22 -InformationLevel Detailed"

# 用 Windows 自带 ssh 复用宿主的 ~/.ssh/config（里有现成跳板机别名），隧道绑到 WSL 可达的宿主网关地址上
nohup /mnt/c/Windows/System32/OpenSSH/ssh.exe -F 'C:\Users\<用户名>\.ssh\config' \
  -N -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
  -L <宿主网关IP>:18083:<内网服务IP>:18083 <宿主config里的别名> \
  > 隧道日志路径 2>&1 &
```

- **宿主网关 IP** = `ip route` 里 `default via` 后面那个（WSL 里不能绑 127.0.0.1——那是 WSL 自己）
- 隧道起来后：`curl --noproxy '*' http://<宿主网关IP>:18083/healthz` 即可访问
- 这条隧道由自己 nohup 管理（不受后台任务 timeout 影响），断了重建一条就行；宿主网络设置一律不动
- 宿主 `~/.ssh/config` 里的别名（如 `H-IP-llmagent`）通常已经配好跳板机和用户名，直接用最省事


### 2. 读文档（首次必读）

```bash
curl --noproxy '*' "$BASE_URL/guide" -o H3_API文档.md   # 完整中文指南
curl --noproxy '*' "$BASE_URL/v1/prompt-guide?mode=base"      # 文本/关键帧提示词规范
curl --noproxy '*' "$BASE_URL/v1/prompt-guide?mode=reference" # 参考模式六段提示词
```

### 3. 有素材先上传

```bash
curl --noproxy '*' "$BASE_URL/v1/assets" -F type=image -F file=@照片.jpg
# 返回 {"id":"asset_...","width":...,...}，保留 id
```

type 取 `image` / `video` / `audio`。限制：图片≤9、视频≤3、独立音频≤3、总文件≤12；视频/音频各 2–15 秒。

### 4. 提交任务（`POST /v1/videos`）

立即返回 `202` + 任务 ID，**提交后 HTTP 连接即可断开**，任务在服务端跑。服务一次只跑一个任务，占用期间其他生成请求返回 `429`（`429` = 没提交上，不是排队）。

参数要点：
- `prompt`：完整提示词，结构见下
- `mode`：`text_to_video` / `first_frame` / `last_frame` / `first_last_frame` / `reference`（可省略自动推断）
- `first_frame` / `last_frame`：素材 ID；与 `references` **不能混用**（混用返回 422）
- `references`：有序数组 `[{"type":"image","asset_id":"..."}]`，顺序决定 `<Picture 1>`/`<Video 1>`/`<Audio 1>` 标签编号
- `num_frames`：必须是 `17*n+5`（124/141/158/.../345 共 14 档），24fps；`duration_seconds` 与 `num_frames` 二选一
- 画幅：默认 1344×768；关键帧模式跟随首张图比例
- 无 `negative_prompt` / `guidance_scale`（guidance-distilled 模型不支持）

### 5. 轮询 → 下载

```bash
TASK_ID=vid_xxx
curl --noproxy '*' "$BASE_URL/v1/videos/$TASK_ID"      # 每 5-10 秒一次
# status: running → succeeded/failed；result 里有 num_frames/duration_seconds/分辨率
curl --noproxy '*' --fail-with-body "$BASE_URL/v1/videos/$TASK_ID/content" -o video.mp4
# 也可下载音轨 /audio 和元数据 /metadata
```

轮询写成 bash 循环放 `run_in_background`（`timeout: 7200000`），状态 JSON 存文件；别前台 sleep（会被拦）。

## 提示词结构（关键，直接按官方规范写）

**文本 / 首帧 / 尾帧 / 首尾帧模式**（三段）：

```
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
（仅关键帧模式要这行；首帧写 0.00 秒，尾帧写实际终点秒数）

integrated_multimodal_description: [Shot 1] <风格 如 Live-action/3D CG>. <初始构图与主体外观> → <动作发展> → <结果>. 镜头/对白/沿时间轴的可见可听细节都写这里.

overall_soundscape: 环境声、动作声、人声/动物声.

non_diegetic_music: N/A 或 BGM 描述（风格、乐器、节奏配合）.
```

- 首帧模式结构：**首帧锚定（复述图片真实状态）→ 动作开始 → 连续发展 → 结尾状态**
- 开始处声明风格：`Cinematic` / `live-action` / `2D-animated` / `3D CG` / `claymation` / `watercolor` / `vintage film`
- 首尾帧模式的锚定行写法（FL2VA）：
  ```
  How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
  ```
  （S.SS = 124 帧对应的 5.17 秒，按实际帧网格算）
- 参考模式用六段：`summary` / `retention_analysis` / `subject_definitions` / `detailed_description` / `overall_soundscape` / `non_diegetic_music`，素材用 `<Picture 1>` 等标签引用，保留程度用 `fully_preserved` / `partially_preserved` 等词
- 首尾帧模式很适合做**两段视频之间的转场**：两段先各自合成到统一画幅（如白板卡片式），抽首段收尾帧 + 次段开头帧上传，`mode: first_last_frame`，提示词描述转场动效（如「光粒子溶解 → 玻璃流体 → 重组」），生成的转场可直接 concat 进整片（注意默认 1344×768，需要 scale 到目标画幅）

## 实测耗时（单卡 H200，50 步去噪）

| 配置 | 时长 | 耗时 |
|---|---|---|
| 纯文本 124 帧 | 5.17s | ~9 分钟 |
| 首帧 192 帧 | 8s | ~10-15 分钟 |
| 复杂参考 | — | 12-29 分钟 |

生成结果：原生 MP4 + 同步 AAC 音轨，`file_check.py` 校验后用 `feishu_send_file`（mp4 走视频消息，用户可直接播放）。

## 连通性：分层诊断（隧道连不上时先看这个）

隧道/healthz 连不上时，**先排除「本机到目标之间的路」的问题，别急着判定服务关了**：

1. 测不经代理的连接（`curl --noproxy '*' <地址>`），再测经代理的；**经代理通 + 直连断 = 本机网络的问题，不是目标的问题**
2. 看路由表（`ip route`）确认网关/宿主地址，测到它通不通
3. 换观测点复测——宿主侧 PowerShell：
   ```bash
   /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe \
     -Command "Test-NetConnection -ComputerName <目标> -Port <端口>"
   ```
   **宿主能连、本机不能 = 本机这层断了**，走 1b 宿主侧隧道；宿主也不通才是跳板机/服务真挂了

吃了大亏的教训（2026-10-26）：耗了 4 个多小时反复怀疑跳板机和服务，实际宿主侧一直能连、生成任务也早就跑完了，换个观测点 5 分钟就定位。

## 常见坑

- `429`：服务忙（有任务在跑），不是提交成功，稍后重试提交
- `422`：参数非法——首帧与 references 混用、只有音频没有视觉参考、帧数/时长超限（如直接要 15 秒会因向上对齐超过 345 帧上限而 422）
- 隧道默认 10 分钟被杀：后台任务一定写 `timeout: 7200000`
- 本机 curl 不加 `--noproxy '*'` 会走代理导致连不上 127.0.0.1
- 提交用 **JSON body**（`-H "Content-Type: application/json" --data-binary @body.json`，prompt/references/num_frames 都是 JSON 字段）；用 `curl -F` multipart 提交会报 `Input should be a valid dictionary or object to extract fields from`（references 字段解析失败）。上传素材才用 `-F` 表单
- 服务端 IP 可能重新部署后变化，以提供者最新地址为准；连不上先 `/healthz` 确认
