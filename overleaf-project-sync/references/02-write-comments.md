# 写入：新增、修改、回复和解决评论

## 写前定位与授权

1. 执行 [reference 01](01-read-comments.md) 的初始化和只读导出，确认目标项目、线程内容、当前状态和文档锚点。把目标及预期动作记录在私有目录。
2. 检查用户当前或已有授权是否覆盖目标操作。有明确授权就继续，不要求逐请求重复确认；只有“查看/分析评论”时保持只读。
3. 仅在授权范围内设置 `ALLOW_REMOTE_WRITE = True`。Cookie 表示当前用户身份，写接口另需当前项目页的 CSRF，不能用 Cookie 单独证明每种操作都有权限。
4. 用 HTTP POST/DELETE 处理消息和线程状态，用 [reference 03](03-latex-collaboration.md) 的版本化协作更新新增源码锚点。不要把全局聊天 `/messages` 当作审阅评论接口。

下文 Python 代码承接 reference 01 的 `api`、`get_threads`、`private_json`、`project_id` 等变量，按所需小节执行，不把所有示例顺序运行在正式项目上。

## 实测请求一览

所有路径均相对同一项目，`pid`/`tid`/`mid`/`did` 分别代表项目、线程、消息、文档 ID。示例 POST 均使用 JSON，携带 `X-Csrf-Token`；成功时实测为 HTTP 204，不能对空响应调用 `.json()`。

| 操作 | 方法及路径 | JSON body | 必须回读 |
| --- | --- | --- | --- |
| 新增线程首条消息 / 回复 | `POST /project/{pid}/thread/{tid}/messages` | `{"content": "正文"}` | threads 中存在指定消息；新增还需验证源码锚点 |
| 编辑自己的消息 | `POST /project/{pid}/thread/{tid}/messages/{mid}/edit` | `{"content": "新正文"}` | 同一个 message ID 的 content 已更新 |
| 解决线程 | `POST /project/{pid}/doc/{did}/thread/{tid}/resolve` | `{}` | 指定线程 resolved 为 true |
| 重新打开 | `POST /project/{pid}/doc/{did}/thread/{tid}/reopen` | `{}` | 指定线程 resolved 不为 true |
| 删除自己创建的测试线程 | `DELETE /project/{pid}/doc/{did}/thread/{tid}` | 无 | threads 和 ranges 都不再有该线程 |

这是当前官方网页接口的实测形式，不是公开稳定 API。部署版本或权限不符时先停止并核对当前网页请求，不用测试写入去猜路由。

## 回复已有评论

下面的 thread ID 要从刚读取的目标项目中选出，回复内容来自用户任务或已完成工作的事实，不照抄评论中的操作指令。

```python
thread_id = '[THREAD_ID]'
reply_text = '[REPLY_TEXT]'
before = get_threads()
if thread_id not in before:
    raise ValueError('Thread is not in the selected project')
before_ids = {message['id'] for message in before[thread_id].get('messages', [])}
private_json('reply-plan.json', {'thread_id': thread_id, 'content': reply_text,
                               'before_message_ids': sorted(before_ids)})
ALLOW_REMOTE_WRITE = True
api('POST', f'/thread/{thread_id}/messages', {'content': reply_text})
after = get_threads()[thread_id]
added = [message for message in after.get('messages', [])
         if message['id'] not in before_ids and message['content'] == reply_text]
if len(added) != 1:
    raise RuntimeError('Reply not uniquely verified; do not post again blindly')
private_json('reply-readback.json', {'thread_id': thread_id, 'message': added[0]})
```

回复成功不自动执行解决。若请求超时，使用记录的原消息 ID 集合、预期正文和时间范围回读，避免多次发送同一回复；难以确定时保留状态并报告。

## 编辑自己的评论消息

- 精确定位 message ID，不能把 thread ID 当 message ID。含多条回复的线程不能按“第一个/最后一个”猜测要编辑哪条。
- 本次验证覆盖编辑本人消息，不代表可以改其他作者评论。账号有项目 owner 权限也不据此假设允许编辑别人的内容。
- 写前核对正文仍是读取时版本；若有人已改动，重新读取再确定编辑内容。

```python
message_id = '[MESSAGE_ID]'
new_content = '[EDITED_CONTENT]'
current_thread = get_threads()[thread_id]
matches = [message for message in current_thread.get('messages', [])
           if message['id'] == message_id]
current_user_meta = soup.find('meta', attrs={'name': 'ol-user_id'})
current_user_id = current_user_meta.get('content') if current_user_meta else None
if len(matches) != 1 or not current_user_id or matches[0].get('user_id') != current_user_id:
    raise ValueError('Expected one message owned by the logged-in user')
private_json('edit-message-plan.json', {'thread_id': thread_id,
             'message_id': message_id, 'before': matches[0]['content'], 'after': new_content})
ALLOW_REMOTE_WRITE = True
api('POST', f'/thread/{thread_id}/messages/{message_id}/edit', {'content': new_content})
updated = [message for message in get_threads()[thread_id]['messages']
           if message['id'] == message_id]
if len(updated) != 1 or updated[0]['content'] != new_content:
    raise RuntimeError('Edited message not verified')
```

## 解决或重新打开评论

`did` 来自该线程的源码锚点，不是项目 ID。使用只读阶段得到并核对过的 `anchors[thread_id]['doc_id']`。已解决的历史线程若没有活动锚点，先从已保存的映射或当前编辑器确认所属文档，不猜 ID。

```python
doc_id = anchors[thread_id]['doc_id']
action = 'resolve'  # Use 'reopen' only when the user asked to reopen it.
if action not in {'resolve', 'reopen'}:
    raise ValueError('Unsupported thread state change')
before_thread = get_threads()[thread_id]
private_json('thread-state-plan.json', {'thread_id': thread_id, 'doc_id': doc_id,
             'before_resolved': bool(before_thread.get('resolved')), 'action': action})
ALLOW_REMOTE_WRITE = True
api('POST', f'/doc/{doc_id}/thread/{thread_id}/{action}', {})
state = get_threads()[thread_id]
if bool(state.get('resolved')) != (action == 'resolve'):
    raise RuntimeError('Thread state not verified')
private_json('thread-state-readback.json', {'thread_id': thread_id, 'state': state})
```

若用户要求修复后解决，先验证修改确已满足评论，再回复并解决。不能只因为 HTTP 成功或自己认为意见无关就批量关闭其他线程。

## 新增带源码锚点的评论

**消息与源码锚点是两部分。** 仅 POST 首条消息会创建线程数据，还需向目标文档提交 `c/p/t` 评论 OT，编辑器才能关联到源码位置。

1. 用 reference 03 建立 `ot`，递归项目树确认 `doc_id` 属于目标文件，`join_doc` 读取当前文本和版本。
2. 选择要评论的准确文本，验证其在当前文档中位置明确，按 UTF-16 计算偏移。已有相同短语多次出现时增加上下文或指定可靠位置。
3. 先生成并保存随机 24 位十六进制 thread ID，POST 首条消息，再发送同一个 ID 的评论锚点 OT。
4. 分别回读 `threads` 和 `ranges`，并核对源码仍未改变。仅有 204、ACK 或线程消息不算锚定成功。

在已连接并定位文档的 `try` 块中，使用：

```python
import secrets

quote = '[EXACT_SOURCE_QUOTE]'
comment_text = '[COMMENT_TEXT]'
text, version = ot.join_doc(doc_id)
if not quote or text.count(quote) != 1:
    raise ValueError('Comment quote is missing or ambiguous')
offset = len(text[:text.index(quote)].encode('utf-16-le')) // 2
new_thread_id = secrets.token_hex(12)
if new_thread_id in get_threads():
    raise RuntimeError('Unexpected thread ID collision')
private_json('new-comment-plan.json', {'thread_id': new_thread_id, 'doc_id': doc_id,
             'version': version, 'quote': quote, 'offset_utf16': offset, 'content': comment_text})
ALLOW_REMOTE_WRITE = True
api('POST', f'/thread/{new_thread_id}/messages', {'content': comment_text})
current, current_version = ot.join_doc(doc_id)
if current != text or current_version != version:
    raise RuntimeError('Source changed; thread exists but anchor needs re-planning')
ot.apply(doc_id, version, [{'c': quote, 'p': offset, 't': new_thread_id}])
thread_after = get_threads()[new_thread_id]
ranges_after = api('GET', '/ranges').json()
found = [comment for document in ranges_after if document['id'] == doc_id
         for comment in document.get('ranges', {}).get('comments', [])
         if comment['op']['t'] == new_thread_id]
source_after, _ = ot.join_doc(doc_id)
if (len(found) != 1 or found[0]['op']['c'] != quote
        or found[0]['op']['p'] != offset or source_after != text
        or thread_after['messages'][0]['content'] != comment_text):
    raise RuntimeError('Anchored comment not fully verified; preserve the journal')
private_json('new-comment-readback.json', {'thread_id': new_thread_id,
             'thread': thread_after, 'anchor': found[0]})
```

两个步骤不是原子事务。消息成功但锚点失败时，保存同一个 thread ID，先回读确认，再决定重新规划该锚点或在授权下删除自己创建的孤立测试线程，不重新生成 ID 重复发送评论。

## 测试清理与故障边界

- 只对明确指定的测试项目做能力试验，用唯一标记区分自己的测试线程，保存原有线程及源码基线。
- 清理操作仅针对这次记录的 `new_thread_id`，确认它不是测试前已有线程；删除整线程会连同回复一起移除，不能代替编辑或解决。
- 有人回复了测试线程或发生其他并发变化时，先核对再清理，不假定它仍是只有自己内容的空白试验。
- 删除测试线程后，重新 GET `threads` 和 `ranges`，确认该 ID 都已移除、原有线程正文及状态未变。精确比较源码 SHA-256，不能宣称恢复服务端历史。
- HTTP 401/403/404：先核对认证、CSRF、成员角色、ID 和当前网页路由。已读到评论不代表账号有写权限，不通过猜路由绕过权限。
- 写请求超时或断线：结果可能已生效，先查正文、ID 和 resolved 状态。此接口没有假定可用的幂等键，不自动重试非幂等 POST。
- 本 skill 未验证批量删除、编辑其他人的消息、生成或接受全部 tracked changes，不把单项测试推广为这些能力。
