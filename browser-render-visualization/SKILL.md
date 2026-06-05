---
name: browser-render-visualization
description: "当需要用 Playwright 渲染网页前端、GitHub Pages、本地静态页面、Canvas 或 Three.js 页面并保存桌面/移动端截图、检查空白渲染、布局溢出和浏览器报错时使用。"
---

# 浏览器渲染可视化

## 核心原则

- 用真实浏览器渲染页面，而不是只看源码或静态 HTML。
- 静态页面也优先通过本地 HTTP server 打开，不要直接用 `file://`。
- 桌面端和移动端都要截图检查。
- Canvas、Three.js、动画页面不能只检查页面打开，还要确认画面不是空白。
- 截图、临时脚本和缓存放在明确目录；如果临时放到 `/tmp`，用后清理。
- 如果缺 Node.js、Playwright 或浏览器依赖，安装前先确认当前环境允许安装。

## 适用场景

- GitHub Pages 或 docs 静态页面验收。
- React、Vue、Vite 或普通 HTML/CSS/JS 页面截图。
- Canvas、Three.js、WebGL、动态图形是否真实渲染。
- 移动端布局是否溢出、文字是否重叠、按钮是否可点击。
- 页面资源路径、字体、图片、CDN、import map、module import 是否正常。

## 环境准备

检查 Node.js：

```bash
node -v
npm -v
```

安装 Playwright：

```bash
npm install -D playwright
npx playwright install chromium
```

Linux 如果缺浏览器系统依赖：

```bash
npx playwright install-deps chromium
```

如果 npm 或 Playwright 缓存权限有问题，可以指定临时缓存；任务结束后清理：

```bash
env npm_config_cache=/tmp/.npm \
    PLAYWRIGHT_BROWSERS_PATH=/tmp/pw-browsers \
    npx playwright install chromium
```

## Playwright 源码追溯

- Playwright 行为以当前 npm 包和浏览器版本为准；截图、locator、等待条件或 console 捕获异常时，先确认版本和包路径。
- `require.resolve('playwright')` 可定位 Node 包入口。
- `npm view playwright version` 可查看 registry 最新版本；不要因此自动升级，升级前先确认。
- 源码只用于阅读和定位问题，不要改源码，不要直接改 `node_modules`；需要改测试脚本时改项目脚本，需要改依赖时先征得用户同意。

```bash
node - <<'JS'
const pw = require('playwright');
console.log('playwright package:', require.resolve('playwright'));
console.log('chromium executable:', pw.chromium.executablePath());
JS
```

```bash
npx playwright --version
npm ls playwright
```

常见 Linux 依赖包括：

```bash
sudo apt install -y \
  libnspr4 \
  libnss3 \
  libasound2t64 \
  libatk-bridge2.0-0 \
  libgtk-3-0 \
  libgbm1 \
  libxkbcommon0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libcups2 \
  libdrm2 \
  libpango-1.0-0 \
  libcairo2
```

## 本地启动页面

普通静态页面：

```bash
cd /path/to/project/docs
python3 -m http.server 8000
```

访问：

```text
http://127.0.0.1:8000/
```

不要直接打开 `file://.../index.html`，因为：

- ES modules 可能被 CORS 限制。
- Three.js 或 module import 可能加载失败。
- 相对资源路径和真实 GitHub Pages 行为不一致。

## Playwright CLI 截图

桌面端截图：

```bash
npx playwright screenshot \
  --browser=chromium \
  --viewport-size=1440,1000 \
  http://127.0.0.1:8000/ \
  preview_desktop.png
```

整页截图：

```bash
npx playwright screenshot \
  --browser=chromium \
  --viewport-size=1440,1000 \
  --full-page \
  http://127.0.0.1:8000/ \
  preview_fullpage.png
```

移动端截图：

```bash
npx playwright screenshot \
  --browser=chromium \
  --viewport-size=390,844 \
  --full-page \
  http://127.0.0.1:8000/ \
  preview_mobile.png
```

CLI 适合快速截图；如果页面加载慢、有动画、需要捕获 console，使用脚本。

## 推荐截图脚本

可以新建 `scripts/screenshot.js`：

```javascript
const { chromium } = require('playwright');

async function main() {
  const url = process.argv[2] || 'http://127.0.0.1:8000/';
  const out = process.argv[3] || 'screenshot.png';

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
    deviceScaleFactor: 1,
  });

  page.on('console', msg => {
    console.log('[browser]', msg.type(), msg.text());
  });

  page.on('pageerror', err => {
    console.error('[pageerror]', err);
  });

  await page.goto(url, {
    waitUntil: 'networkidle',
    timeout: 60000,
  });

  await page.waitForTimeout(2000);

  await page.screenshot({
    path: out,
    fullPage: true,
  });

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

运行：

```bash
node scripts/screenshot.js http://127.0.0.1:8000/ preview_desktop.png
```

移动端把 viewport 改成：

```javascript
viewport: { width: 390, height: 844 }
```

## Canvas 和 Three.js 检查

先截图：

```bash
node scripts/screenshot.js http://127.0.0.1:8000/ page.png
```

再检查截图是否几乎纯色：

```python
from PIL import Image, ImageStat

img = Image.open("page.png").convert("RGB")
stat = ImageStat.Stat(img)

print("mean:", stat.mean)
print("stddev:", stat.stddev)

if max(stat.stddev) < 2:
    print("image may be nearly blank")
```

只截第一个 canvas：

```javascript
const canvas = page.locator('canvas').first();
await canvas.screenshot({ path: 'canvas.png' });
```

检查重点：

- canvas 是否非空白。
- 动画或 3D 场景是否已经加载完成。
- 桌面和移动端视口下主体是否居中、未裁切。
- 文字、按钮、图层和 canvas 是否互相遮挡。

## 常见问题

页面空白时优先检查：

- 浏览器 console 是否有 JavaScript 报错。
- 是否用 HTTP server 打开，而不是 `file://`。
- 静态资源路径是否正确。
- Three.js import map、module import 或 CDN 是否可访问。
- 图片、字体或模型资源是否 404。

Playwright 找不到 Chromium：

```bash
npx playwright install chromium
```

Linux 缺系统库：

```bash
npx playwright install-deps chromium
```

定位缺失库：

```bash
ldd /path/to/chrome-headless-shell | grep "not found"
```

截图太糊：

```javascript
const page = await browser.newPage({
  viewport: { width: 1600, height: 1100 },
  deviceScaleFactor: 2,
});
```

动画或 3D 模型还没加载完：

```javascript
await page.waitForLoadState('networkidle');
await page.waitForTimeout(3000);
```

更稳的方式是等待页面自己的 ready 元素：

```javascript
await page.locator('.loaded').waitFor({ timeout: 30000 });
```

## 推荐验收流程

一个终端启动页面：

```bash
cd /path/to/project/docs
python3 -m http.server 8000
```

另一个终端截图：

```bash
npx playwright screenshot \
  --browser=chromium \
  --viewport-size=1440,1000 \
  --full-page \
  http://127.0.0.1:8000/ \
  preview_desktop.png

npx playwright screenshot \
  --browser=chromium \
  --viewport-size=390,844 \
  --full-page \
  http://127.0.0.1:8000/ \
  preview_mobile.png
```

最终确认：

- 页面不是空白。
- 桌面和移动端没有横向溢出。
- 文字没有重叠或被遮挡。
- 图片、字体、图标、Canvas、Three.js 资源都显示。
- console 没有影响渲染的错误。
- 截图文件保存在项目内明确目录；临时缓存按需清理。
