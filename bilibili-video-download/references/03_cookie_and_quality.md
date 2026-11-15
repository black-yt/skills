# 登录态 Cookie：获取、保管与下载高清画质

本页补齐「高画质下载」这一环：什么时候必须带登录态、怎么拿到 Cookie、怎么安全保存、下载时怎么用，以及怎样判断 Cookie 失效。

## 1. 什么时候需要 Cookie

游客（未登录）访问 `x/player/playurl` 时，B站只返回 **480P** 一档实际可下载流，即使 `accept_quality` 里列出了 4K、1080P+ 等档位。

判断依据：`--list` 输出的「账号可选画质」与「实际可选画质」不一致时，差额就是登录态（以及账号权益）带来的。

| 画质 | 游客 | 登录 | 大会员 |
| --- | --- | --- | --- |
| 360P / 480P | ✅ | ✅ | ✅ |
| 720P | — | ✅ | ✅ |
| 1080P / 1080P+ | — | ✅ | ✅ |
| 4K（超清） | — | — | ✅ |

上表是常见情况，不同视频、不同时期策略可能不同；**以 `--list` 的实际输出为准**，不要凭档位名称承诺结果。

## 2. 获取 Cookie

Cookie 里真正决定登录态的是 `SESSDATA` 一项，其它字段可以不用。

### 方法一：开发者工具 → Application（推荐）

1. 用电脑浏览器打开 <https://www.bilibili.com> 并**先登录**（右上角能看到自己的头像才算登录成功）。
2. 按 `F12` 打开开发者工具。
3. 切到 **Application**（中文版为「应用」）标签。
4. 左侧 `Storage → Cookies → https://www.bilibili.com`。
5. 在右侧表格中找到 `Name` 为 `SESSDATA` 的行，双击 `Value` 单元格，复制整段值。
6. 得到形如 `xxxxxxxx%2C1807410741%2Cxxxxx%2Axxxx...IIEC` 的字符串（含 `%2C` 说明已被 URL 编码，原样保存即可，不要自行解码）。

### 方法二：复制整条 Cookie

1. 同样 `F12`，切到 **Network**（网络）标签。
2. 刷新页面，任选一条 `api.bilibili.com` 开头的请求。
3. 右侧 `Headers → Request Headers → Cookie`，复制整条值。

整条 Cookie 与单项 `SESSDATA` 脚本都能识别：文件里有 `SESSDATA=` 就用它，没有就把整条当 Cookie 头发送。

### 方法三：移动端（不方便时）

手机浏览器打开 m.bilibili.com 登录后，用「查看网页源码 / 开发者工具」类工具取 Cookie；多数移动端浏览器不支持，建议优先用电脑。

## 3. 安全保存

Cookie 等于账号登录凭证，拿到的人可以登录该账号。因此：

- **只存在本地私有文件里**，仓库外、权限 600；
- 不要写进命令行参数（会进 shell 历史与进程列表）、不要贴进聊天记录或提交信息；
- 不要提交进 Git，不要在日志里打印真实值。

推荐位置（任选其一，脚本通过 `--cookie-file` 读取）：

```bash
umask 077
mkdir -p "$HOME/.config/bilibili-video-download"
# 交互式输入，不回显、不进历史
read -r -s -p '粘贴 Cookie 或 SESSDATA: ' BILI_COOKIE; printf '\n'
printf '%s\n' "$BILI_COOKIE" > "$HOME/.config/bilibili-video-download/cookie"
unset BILI_COOKIE
chmod 600 "$HOME/.config/bilibili-video-download/cookie"
```

文件内容两种写法都可以：

```text
SESSDATA=xxxxxxxx%2C1807410741%2Cxxxxx%2A...
```

```text
# 或整条 Cookie
buvid3=...; b_nut=...; SESSDATA=...; bili_jct=...; DedeUserID=...
```

## 4. 下载时怎么用

先用 `--list` 确认登录态已生效、看到目标档位，再执行下载：

```bash
SKILL_DIR="/path/to/bilibili-video-download"
COOKIE_FILE="$HOME/.config/bilibili-video-download/cookie"
VIDEO_URL="https://www.bilibili.com/video/BVxxxxxxxxxx/"

# 1) 先看档位：账号可选 vs 实际可选
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" \
  --cookie-file "$COOKIE_FILE" --list

# 2) 下载 1080P（实际不足时自动降到不高于目标的最高可用档）
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" \
  --cookie-file "$COOKIE_FILE" --qn 1080P --dir "./downloads/BVxxxxxxxxxx"

# 3) 只要音频，同样带 Cookie
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" \
  --cookie-file "$COOKIE_FILE" --mp3-only --dir "./downloads_mp3/BVxxxxxxxxxx"
```

配合 `FFMPEG_BIN` 指向已有 ffmpeg 时，也可写成一行：

```bash
FFMPEG_BIN=/path/to/ffmpeg python3 "$SKILL_DIR/scripts/bilibili_download.py" \
  "$VIDEO_URL" --cookie-file "$COOKIE_FILE" --qn 1080P --dir ./out
```

注意：`--qn` 是「目标画质」，实际拿到的是**不高于它**的最高可用档。请求 4K 但账号无大会员时，会静默降到 1080P——核对输出文件的分辨率，不要只看命令参数。

## 5. 判断 Cookie 是否有效、何时过期

### 过期时间

`SESSDATA` 值里第二段是 Unix 时间戳，可直接换算：

```bash
python3 - <<'PY'
import datetime
ts = 1807410741          # 替换为你的 SESSDATA 中间那段数字
print(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M'))
PY
```

典型有效期约半年到一年。临期前重新获取一份并覆盖旧文件即可。

### 失效的表现

- `--list` 里「实际可选画质」又只剩 480P / 360P；
- 下载命令退出码非 0，错误里出现 `-101`（账号未登录）或返回流明显低于预期；
- 登录态正常但高码率档缺失：多半是**账号权益不足**（如无大会员），而不是 Cookie 失效。

### 确认方法

```bash
COOKIE_FILE="$HOME/.config/bilibili-video-download/cookie" python3 - <<'PY'
import json, os, urllib.request
cookie = open(os.path.expanduser(os.environ["COOKIE_FILE"])).read().strip()
req = urllib.request.Request(
    "https://api.bilibili.com/x/web-interface/nav",
    headers={"User-Agent": "Mozilla/5.0", "Cookie": cookie})
d = json.load(urllib.request.urlopen(req, timeout=20))
print("isLogin:", d["data"].get("isLogin"), "uname:", d["data"].get("uname"))
print("vip:", d["data"].get("vipStatus"), "level:", d["data"].get("level_info", {}).get("current_level"))
PY
```

`isLogin: True` 说明登录态有效；`vipStatus` 为 1 表示有大会员权益，可尝试 4K。

## 6. 收尾

- 用完后如需销毁：`shred -u "$COOKIE_FILE"`（或 `rm -f`）并确认没有副本留在日志、`~/.bash_history`、临时目录里。
- 把 Cookie 传给他人等同于交出账号；如需共享下载能力，优先让对方自行获取自己的 Cookie，而不是共用一份。
- 只下载用户有权保存的内容；需要账号权益时走正常获取途径，不尝试绕过平台访问控制。