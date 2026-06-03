---
name: frontend-markdown-rendering
description: "当需要在前端把最终 assistant 文本渲染为 Markdown，同时保留工具过程为纯文本/JSON，并支持表格、代码块、图片、KaTeX 公式、Mermaid 图和 workspace 本地图片安全访问时使用。"
---

# Frontend Markdown Rendering

## 核心原则

- 只把最终 assistant 文本当 Markdown 渲染。
- 工具调用、工具输出、中间 trace、错误日志、JSON payload 和流式过程仍按纯文本或 JSON 展示。
- 不要自己手写完整 Markdown parser；组合成熟库。
- Markdown HTML 插入前必须清洗，避免直接插入不可信 HTML。
- 本地 workspace 图片必须通过受 token 保护的后端路由读取，不能直接暴露任意文件路径。
- 图片、表格、Mermaid SVG 都必须限制宽度，避免撑爆右侧或移动端布局。

推荐库：

- Markdown：`marked`
- HTML 安全：`DOMPurify`
- 数学公式：`KaTeX`
- 流程图：`Mermaid`
- 本地图片：后端自建 `/api/workspace-file` 路由

## CDN 依赖

前端可以直接使用 CDN：

```html
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.2.6/dist/purify.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked@15.0.12/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.12.0/dist/mermaid.min.js"></script>
```

如果页面需要 KaTeX 样式，同时引入 CSS：

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
```

如果使用 Mermaid，初始化一次：

```js
mermaid.initialize({
  startOnLoad: false,
  securityLevel: 'strict',
  theme: 'default'
});
```

## 渲染触发条件

只在最终结果消息上启用 Markdown：

```js
function shouldRenderMarkdown(message) {
  return (
    message.role === 'assistant' &&
    message.termination === 'result' &&
    !message.tool_calls &&
    !message.tool_call_id
  );
}
```

不要对这些内容做 Markdown 渲染：

- tool call arguments
- tool outputs
- runtime logs
- trace events
- JSON chunks
- error stack
- streaming delta before final result

## 渲染流程

推荐流程：

```text
text
-> 如果整个输出被 ```markdown ... ``` 包住，则去掉最外层 fence
-> 保护公式片段
-> marked.parse(..., { gfm: true })
-> 重写本地 workspace 图片路径
-> DOMPurify.sanitize(...)
-> 恢复公式片段
-> 插入 .markdown-body
-> KaTeX 渲染公式
-> Mermaid 渲染图
```

核心函数骨架：

```js
function stripOuterMarkdownFence(text) {
  const trimmed = text.trim();
  const match = trimmed.match(/^```(?:markdown|md)?\s*\n([\s\S]*?)\n```$/i);
  return match ? match[1] : text;
}

function renderAssistantMarkdown(text, options) {
  const source = stripOuterMarkdownFence(text);
  const protectedMath = protectMathSegments(source);

  let html = marked.parse(protectedMath.text, {
    gfm: true,
    breaks: false
  });

  html = rewriteWorkspaceImageSrc(html, options);
  html = DOMPurify.sanitize(html, {
    ADD_TAGS: ['math'],
    ADD_ATTR: ['target', 'rel']
  });
  html = restoreMathSegments(html, protectedMath.segments);

  const body = document.createElement('div');
  body.className = 'markdown-body';
  body.innerHTML = html;

  renderMath(body);
  renderMermaidBlocks(body);
  return body;
}
```

## 公式处理

支持这些公式分隔符：

```md
\(...\)
\[...\]
$$...$$
```

不主动支持单 `$...$`，因为它容易和普通文本、金额、shell 变量冲突。

公式要先从 Markdown 文本中临时替换成 token，等 `marked + DOMPurify` 后再恢复。否则 `marked` 可能改坏反斜杠或公式结构。

公式保护骨架：

```js
function protectMathSegments(text) {
  const segments = [];
  const pattern = /(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\))/g;
  const replaced = text.replace(pattern, (match) => {
    const token = `@@MATH_${segments.length}@@`;
    segments.push(match);
    return token;
  });
  return { text: replaced, segments };
}

function restoreMathSegments(html, segments) {
  return html.replace(/@@MATH_(\d+)@@/g, (_, index) => segments[Number(index)] || '');
}
```

KaTeX 渲染：

```js
function renderMath(body) {
  renderMathInElement(body, {
    delimiters: [
      { left: '$$', right: '$$', display: true },
      { left: '\\[', right: '\\]', display: true },
      { left: '\\(', right: '\\)', display: false }
    ],
    ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
    throwOnError: false
  });
}
```

## Mermaid 处理

Markdown 中写：

````md
```mermaid
graph TD
  A --> B
```
````

`marked` 会生成 `pre code.language-mermaid`。前端找到这些 block 后调用 `mermaid.render`，再把原 code block 替换成 SVG 容器。

```js
let mermaidCounter = 0;

async function renderMermaidBlocks(body) {
  const blocks = Array.from(body.querySelectorAll('pre code.language-mermaid'));

  for (const code of blocks) {
    const source = code.textContent || '';
    const wrapper = document.createElement('div');
    wrapper.className = 'mermaid-chart';

    try {
      const id = `mermaid-${Date.now()}-${mermaidCounter++}`;
      const result = await mermaid.render(id, source);
      wrapper.innerHTML = result.svg;
      code.closest('pre').replaceWith(wrapper);
    } catch (error) {
      wrapper.textContent = source;
      wrapper.classList.add('mermaid-chart--error');
      code.closest('pre').replaceWith(wrapper);
    }
  }
}
```

## 图片处理

在线图片和 data URL 可以保留：

```md
![plot](https://example.com/a.png)
![inline](data:image/png;base64,...)
```

本地 workspace 图片应被前端改写：

```md
![plot](assets/result.png)
```

改写为：

```text
/api/workspace-file?token=<token>&path=assets/result.png
```

前端改写逻辑：

```js
function rewriteWorkspaceImageSrc(html, options) {
  const root = document.createElement('div');
  root.innerHTML = html;

  root.querySelectorAll('img').forEach((img) => {
    const src = img.getAttribute('src') || '';
    if (isExternalOrDataUrl(src)) return;
    if (!options.workspaceToken) return;

    const url = new URL('/api/workspace-file', window.location.origin);
    url.searchParams.set('token', options.workspaceToken);
    url.searchParams.set('path', src);
    img.setAttribute('src', url.toString());
  });

  return root.innerHTML;
}

function isExternalOrDataUrl(src) {
  return /^(https?:|data:image\/)/i.test(src);
}
```

后端 `/api/workspace-file` 必须做三件事：

- 根据 token 找到当前 chat 的 workspace。
- 解析并规范化请求 path，确认没有逃出 workspace。
- 只允许图片扩展名内联显示：`.png`、`.jpg`、`.jpeg`、`.gif`、`.webp`、`.bmp`、`.svg`。

后端伪代码：

```python
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}

def workspace_file(token: str, path: str):
    workspace = lookup_workspace_by_token(token)
    if workspace is None:
        raise NotFound()

    target = safe_join(workspace, path)
    if not target.is_file():
        raise NotFound()

    if target.suffix.lower() not in ALLOWED_IMAGE_EXTS:
        raise Forbidden()

    return send_file(target)
```

## CSS

Markdown 容器：

```css
.markdown-body {
  overflow-wrap: anywhere;
  line-height: 1.62;
}
```

图片：

```css
.markdown-body img {
  display: block;
  width: auto;
  max-width: 100%;
  height: auto;
  object-fit: contain;
}
```

表格：

```css
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
}

.markdown-body th,
.markdown-body td {
  padding: 8px 10px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  vertical-align: top;
}

.markdown-body table {
  display: block;
  overflow-x: auto;
}
```

Mermaid：

```css
.mermaid-chart {
  max-width: 100%;
  overflow-x: auto;
}

.mermaid-chart svg {
  max-width: 100%;
  height: auto;
}
```

代码块：

```css
.markdown-body pre {
  max-width: 100%;
  overflow-x: auto;
  white-space: pre;
}
```

## 验证清单

- 最终 assistant result 会渲染 Markdown。
- tool call、tool output、trace、error log 不会渲染 Markdown。
- GFM 表格能正常显示且横向不撑爆页面。
- `\(...\)`、`\[...\]`、`$$...$$` 能正常渲染，单 `$...$` 不作为默认支持。
- `pre code.language-mermaid` 能被替换成 SVG。
- 远程图片和 data URL 能显示。
- workspace 相对图片通过 `/api/workspace-file` 显示。
- workspace 图片不能通过 `../` 逃出工作目录。
- 非图片文件不能通过 workspace 图片路由读取。
- 大图、宽表、Mermaid SVG、代码块都不会撑破移动端。
- DOMPurify 清洗后，不可信 HTML 不会执行脚本。

## 常见错误

- 把所有 assistant streaming chunk 都 Markdown 渲染，导致半截代码块或半截公式闪烁。
- 把工具日志当 Markdown 渲染，导致 JSON、shell 输出或错误栈被错误格式化。
- 在 `marked` 前不保护公式，导致反斜杠和换行被改坏。
- 支持单 `$...$` 后把金额、shell 变量或普通美元符号误渲染成公式。
- 直接插入 `marked.parse` 结果，不经过 DOMPurify。
- 直接把本地路径放进 `<img src>`，导致浏览器无法访问或产生路径泄露。
- 后端文件路由只拼字符串，不做 path normalization 和 workspace 边界检查。
- Mermaid 渲染失败时没有 fallback，导致整条消息空白。
