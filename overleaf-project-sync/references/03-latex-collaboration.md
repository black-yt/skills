# 写入：版本化修改 LaTeX 与评论锚点

先执行 reference 01 的会话初始化。读取文档仍属于只读操作，只有明确授权修改指定项目、文件或新增评论后才启用 `ALLOW_REMOTE_WRITE`。

## 选择正确的写入通道

- ZIP 下载脚本只支持远端到本地，不能把修改后的 LaTeX 上传回去。
- 这里记录的是实际网页编辑器的 Socket.IO 0.9 协作通道：HTTP 握手 → WebSocket → `joinProjectResponse` → `joinDoc` → `applyOtUpdate`。
- Socket.IO 0.9 线协议与现代 Socket.IO 3/4 不兼容，不能直接把新客户端库指向相同路径后假定可用。
- 本教程在 `protocolVersion=2`、旧 text OT 文档上实测。协作层版本与 Socket.IO 线协议版本是不同概念。
- 如果当前 `ol-otMigrationStage`、文档返回结构或 OT 类型与示例不符，停止套用旧操作，重新核对当前编辑器请求；不能对新 snapshot/history OT 格式强行发送旧 text OT。
- 不用普通 `/upload` 覆盖已有 `.tex`，不把删除文档再重建当作保存，不在协作编辑时全量覆盖文件绕过版本检查。

## 可复制的协作客户端

在独立环境中准备 `websocket-client`。下面代码承接 reference 01 的 `session`、`origin`、`project_id`、`ALLOW_REMOTE_WRITE`，放在同一个私有 Python 执行文件中。

该客户端只处理一次短操作所需的协议，不实现离线队列、自动重连、自动重发或完整并发 OT 变换。不要让它长时间无人值守运行。

```python
import time
from http.cookies import SimpleCookie
from urllib.parse import urlsplit

import websocket

class OverleafSocket:
    def __init__(self):
        self.ws = None
        self.next_ack = 0
        self.doc_ids = set()

    def recv(self, deadline):
        while time.monotonic() < deadline:
            self.ws.settimeout(min(10, deadline - time.monotonic()))
            try:
                frame = self.ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            if not frame:
                raise RuntimeError('Collaboration socket closed')
            if isinstance(frame, bytes):
                frame = frame.decode('utf-8')
            if frame.startswith('2:'):
                self.ws.send('2::')
                continue
            match = re.match(r'^(\d+):([^:]*):([^:]*):?(.*)$', frame, re.S)
            if not match:
                continue
            kind, _, _, payload = match.groups()
            if kind in {'0', '7'}:
                raise RuntimeError('Collaboration connection rejected or closed')
            if kind == '5':
                return ('event', json.loads(payload))
            if kind == '6':
                number, _, raw = payload.partition('+')
                return ('ack', int(number), json.loads(raw) if raw else [])
        raise TimeoutError('No collaboration response; re-read before any retry')

    def connect(self):
        handshake = require_success(session.get(
            origin + '/socket.io/1/',
            params={'projectId': project_id, 't': int(time.time() * 1000)},
            timeout=40, allow_redirects=False))
        sid, _, _, transports = handshake.text.split(':', 3)
        if not re.fullmatch(r'[A-Za-z0-9_-]+', sid) or 'websocket' not in transports:
            raise RuntimeError('Unsupported Socket.IO handshake')
        # The same load-balancer backend must receive the WebSocket upgrade.
        # A raw Cookie header would otherwise hide requests.Session's cookie jar.
        jar = SimpleCookie()
        jar.load(session.headers['Cookie'])
        for cookie in session.cookies:
            jar[cookie.name] = cookie.value
        upgrade_cookie = '; '.join(f'{key}={value.value}' for key, value in jar.items())
        options = {'cookie': upgrade_cookie, 'origin': origin, 'timeout': 30}
        proxy_url = os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY')
        if proxy_url:
            proxy = urlsplit(proxy_url)
            options.update(http_proxy_host=proxy.hostname, http_proxy_port=proxy.port)
            if proxy.username or proxy.password:
                raise RuntimeError('Configure authenticated proxy separately; do not log credentials')
        self.ws = websocket.create_connection(
            origin.replace('https://', 'wss://') + '/socket.io/1/websocket/' + sid,
            **options)
        deadline = time.monotonic() + 30
        while True:
            packet = self.recv(deadline)
            if packet[0] != 'event' or packet[1].get('name') != 'joinProjectResponse':
                continue
            info = packet[1]['args'][0]
            project = info['project']
            if project['_id'] != project_id or info.get('protocolVersion') != 2:
                raise RuntimeError('Unexpected project or collaboration protocol')
            def visit(folder):
                for doc in folder.get('docs', []):
                    self.doc_ids.add(doc['_id'])
                for child in folder.get('folders', []):
                    visit(child)
            for folder in project.get('rootFolder', []):
                visit(folder)
            return info

    def call(self, name, args):
        # Keep the example's callable surface narrow. No unknown write events.
        if name not in {'joinDoc', 'applyOtUpdate'}:
            raise ValueError('Unsupported collaboration event')
        if not args or args[0] not in self.doc_ids:
            raise ValueError('Document not found in the selected project')
        if name == 'applyOtUpdate' and not ALLOW_REMOTE_WRITE:
            raise PermissionError('Remote writes are disabled')
        self.next_ack += 1
        ack = self.next_ack
        self.ws.send(f'5:{ack}+::' + json.dumps({'name': name, 'args': args}))
        deadline = time.monotonic() + 35
        while True:
            packet = self.recv(deadline)
            if packet[0] != 'ack' or packet[1] != ack:
                continue
            data = packet[2]
            if data and data[0]:
                raise RuntimeError('Collaboration operation rejected; re-read state')
            return data[1:]

    def join_doc(self, doc_id):
        result = self.call('joinDoc', [doc_id, {'encodeRanges': True}])
        lines, version = result[:2]
        if not isinstance(lines, list) or not isinstance(version, int):
            raise RuntimeError('Unsupported document response')
        # This endpoint returns UTF-8 bytes packed into Latin-1 strings.
        # Fail on unexpected encoding rather than replacing/corrupting text.
        text = '\n'.join(line.encode('latin-1').decode('utf-8') for line in lines)
        return text, version

    def apply(self, doc_id, version, ops):
        return self.call('applyOtUpdate', [doc_id,
                         {'doc': doc_id, 'v': version, 'op': ops}])

    def close(self):
        if self.ws is not None:
            self.ws.close()
```

- 握手返回 `sid:heartbeat:timeout:transports`，sid 也属于私有连接信息，不打印。
- SaaS 可能通过 `GCLB` 等 Cookie 把连接固定到后端。WebSocket 升级要合并握手的 Set-Cookie，丢失它可能间歇性返回 502。
- 服务端发心跳时回复 `2::`。ACK `6:::id+[null,...result]` 的第一个元素是错误，不是返回值。
- 某些旧部署需要显式 `joinProject`，此示例不包含该分支。未收到 `joinProjectResponse` 时只报告尚未连接，不盲试写事件。
- 在 `try/finally` 中关闭连接，包括 connect 失败的情况；不记录含 Cookie 的网络调试日志。

## 读取文档树与源码基线

```python
ot = OverleafSocket()
try:
    info = ot.connect()
    paths_by_id = {}
    def visit(folder, prefix=''):
        for doc in folder.get('docs', []):
            paths_by_id[doc['_id']] = prefix + doc['name']
        for child in folder.get('folders', []):
            visit(child, prefix + child['name'] + '/')
    for root in info['project'].get('rootFolder', []):
        visit(root)
    # Exact file path selected by the user, not a guessed document ID.
    wanted_path = 'sections/experiments.tex'
    matches = [key for key, path in paths_by_id.items() if path == wanted_path]
    if len(matches) != 1:
        raise RuntimeError('Target document path is missing or ambiguous')
    doc_id = matches[0]
    text, version = ot.join_doc(doc_id)
    private_json('source-before.json', {'doc_id': doc_id, 'path': wanted_path,
                                      'version': version, 'text': text})
finally:
    ot.close()
```

写入时使用同样的连接流程，将下面的局部替换放在 `try` 内，并在完成前回读。`permissionsLevel` 应允许编辑；只读成员不要调用写操作。既有基线不能被后一次读取覆盖。

## UTF-16 偏移、局部替换与回读

- Overleaf/JavaScript 的位置单位为 UTF-16。Python 的 `len()` 只在 BMP 文本中碰巧相同，不能把它当作通用偏移。
- 中文处于 BMP，通常每字一个 UTF-16 单元；emoji 等非 BMP 字符占两个单元。旧 text OT 通道对非 BMP 插入可能不兼容，示例遇到该类插入应停止并改用已验证的编辑器途径，不静默替换字符。
- 插入为 `{'p': offset, 'i': text}`，删除为 `{'p': offset, 'd': exact_text}`。同一批操作依次作用于当前文本，替换用先删后插，位置不变。
- 新增评论锚点为 `{'p': offset, 'c': exact_quote, 't': thread_id}`，不会修改正文，但属于远端写入，也要带当前版本。

```python
def utf16_length(value):
    return len(value.encode('utf-16-le')) // 2

def replacement_plan(text, old, new):
    if not old or text.count(old) != 1:
        raise ValueError('Expected one exact nonempty target')
    if any(ord(char) > 0xffff for char in new):
        raise ValueError('Non-BMP insertion is not validated for this legacy OT path')
    index = text.index(old)
    offset = utf16_length(text[:index])
    ops = [{'p': offset, 'd': old}]
    if new:
        ops.append({'p': offset, 'i': new})
    return ops, text[:index] + new + text[index + len(old):]
```

同一个 `ot` 连接中已完成目标文档定位后，执行。真实 LaTeX 段落从 UTF-8 文件读取或使用 raw 三引号字符串，避免把 `\begin`、`\ref` 等误解析为 Python 转义；多行内容保留实际换行：

```python
old = r'''[EXACT_OLD_LATEX]'''
new = r'''[NEW_LATEX]'''
ops, expected = replacement_plan(text, old, new)
private_json('latex-write-plan.json', {'doc_id': doc_id, 'version': version,
                                     'ops': ops, 'expected': expected})
current, current_version = ot.join_doc(doc_id)
if current != text or current_version != version:
    raise RuntimeError('Baseline changed; re-read and re-plan the local edit')
ALLOW_REMOTE_WRITE = True  # Only after the user's scoped authorization.
ot.apply(doc_id, version, ops)
actual, actual_version = ot.join_doc(doc_id)
private_json('latex-write-readback.json', {'doc_id': doc_id,
             'version': actual_version, 'matches_expected': actual == expected})
if actual != expected or actual_version <= version:
    raise RuntimeError('Write not fully verified; preserve evidence, do not overwrite')
```

- 这个示例是直接编辑，不指定 `meta.tc`，没有测试生成修订建议的路径。若项目强制修订，需核对当前 Review/ranges 状态，不能擅自关闭修订或声称所有变更已接受。
- 如需编译检查，先核对本地快照确实包含刚回读的内容，再在本地编译或使用用户已授权的编译方式。源码保存成功不等于 PDF 编译成功。
- 遇到并发写入，服务器可能做 OT 变换。回读不符时保留实际内容和操作记录，重新规划局部变更，不整文件覆盖其他人的工作。

## 临时验证与恢复

只在用户指定的测试项目中验证未知写操作。先保存源码与评论基线，插入可识别的 `%` 注释标记，确认回读后以其最新位置和版本精确删除，再核对源码 SHA-256 与原基线一致。

- 清理自己的测试锚点和线程后，核对原有线程正文与 resolved 状态、源码及其他锚点仍一致。
- 不删除原有评论，不把“未发现自己标记”当作整份内容已恢复的证明。
- 若其他人同时修改了文件，只撤销自己能唯一定位的变化，不拿旧基线整体覆盖新内容。
- 清理恢复当前内容，但文档版本会增长，服务端编辑/评论历史不会因此回到测试前。

## 故障处理

| 现象 | 核对与停止条件 |
| --- | --- |
| 握手 401/403 或跳转 | 核对 Cookie、项目权限、CSRF 和当前登录页，不打印认证值 |
| WebSocket 502 | 检查代理和握手 Set-Cookie 是否带到升级请求；未连接前可重新建立只读连接 |
| 只读连接成功但 OT 拒绝 | 核对项目编辑权限、协议、文档 ID 和版本，不猜字段绕过校验 |
| 中文乱码、返回格式不同 | 保留原始私有证据并停止写入，不用 `errors='replace'` 掩盖解码问题 |
| ACK 超时或断线 | 结果可能已经生效，先新建只读连接并回读文档/锚点，再决定是否需要重新规划 |
| 回读与 expected 不符 | 不自动重发或整份恢复，先判断并发、编码或操作未生效 |
