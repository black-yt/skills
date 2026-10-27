# 安装、实际渲染和验收

## 实测版本与官方入口

- 2026-10-27 实际渲染器：draw.io 在线编辑器 **32.6.4**。每次运行将实际版号写入 `outputs/figure-N.render.json`。
- 同日对照的 [jgraph/drawio HEAD](https://github.com/jgraph/drawio/tree/84487b4891cbc0f32d7e30f34cf878c87cb1f414)：`84487b4891cbc0f32d7e30f34cf878c87cb1f414`。这是上游源码锚点，不断言在线服务恰好由该 commit 构建。
- 本例导出器依赖 Playwright `1.64.1`，由 `package-lock.json` 锁定；Python XML 生成器不依赖 draw.io 安装。
- 已访问的完整官方文档：[原生样式与 XML](https://www.drawio.com/docs/reference/diagram-generation/style-reference/)、[embed JSON 协议](https://www.drawio.com/docs/reference/embed-mode/)、[自定义 XML 形状](https://www.drawio.com/docs/manual/shapes/shape-complex-create-edit/)、[导出格式](https://www.drawio.com/docs/manual/export/export-diagram/)。官网文档滚动更新；本地 Desktop 的参数以 `drawio --version`、`drawio --help` 为准。
- 更新此 skill 的渲染器或样式前，重新核对实际版号、上游 HEAD、官方文档和当前 CLI 帮助；不要只改版本记录。

## 安装与生成

在 skill 目录运行：

```bash
# 生成 native XML 不需要第三方 Python 包
python3 scripts/build_examples.py
python3 scripts/validate_drawio.py outputs/figure-*.drawio

# 使用本目录的 Node 依赖；不修改全局 Node 或 shell 配置
npm ci
npx playwright install chromium --only-shell

# 可选：图标转换、PDF 检查与预览图集
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
```

仅打开已有 `.drawio` 可以直接使用 draw.io Desktop 或 diagrams.net，选择本地设备文件。无需运行 Python 或配置任何模型 API。

## 真实 draw.io 自动导出

```bash
node scripts/export_drawio.cjs assets/examples/figure-1.drawio assets/examples/figure-2.drawio assets/examples/figure-3.drawio assets/examples/figure-4.drawio
python3 scripts/validate_drawio.py assets/examples/figure-*.drawio --roundtrip-dir outputs
.venv/bin/python scripts/verify_exports.py
.venv/bin/python scripts/build_previews.py
```

- **执行过程**：Playwright 打开 draw.io 官方 embed 编辑器，等待 `init`，发送 native XML，等待 `load`，再请求 `xmlsvg`、`xmlpng` 和结构 JSON。PDF 从同一份 draw.io SVG 通过 Chromium 导出。
- **文件**：每图产生 `.svg`、`.png`、`.pdf`、原生结构 `.json` 和 `.render.json`。SVG/PNG 含源图 XML，可以重新导入 draw.io；`.drawio` 主文件单独保留。
- **输出目录**：可加 `--output-dir [OUTPUT_DIR]`。单次处理多个文件会复用编辑器，避免反复初始化。
- **既有浏览器**：需要显式使用已安装的 Chromium 时，仅对当前命令设置 `DRAWIO_CHROMIUM_EXECUTABLE='[CHROMIUM_PATH]'`。默认使用 Playwright 自带浏览器。
- **联网范围**：在线编辑器会收到图的 XML。私有图使用本地 Desktop 或组织自己的受控渲染环境；不在公共在线案例中放密钥、内部主机或私人数据。
- **文字**：默认使用 DejaVu Serif / DejaVu Sans；系统缺少该字体时可能回退，导出后必须实际查看。下载图标不依赖字体图标库。

## Desktop 导出

当本机已安装 draw.io Desktop，先核对该版本帮助：

```bash
drawio --version
drawio --help
drawio -x -f svg -e -b 8 -o outputs/figure-1.svg assets/examples/figure-1.drawio
drawio -x -f png -e -b 8 -o outputs/figure-1.png assets/examples/figure-1.drawio
drawio -x -f pdf -b 8 -o outputs/figure-1.pdf assets/examples/figure-1.drawio
```

`-e` 在支持的格式中嵌入图源；实际支持以该版本帮助为准。没有 CLI 时在编辑器中使用 File → Export as 手动导出，并保留 `.drawio`。不能把未执行的导出写成已验证。

## 四种检查

| 检查 | 代码与证据 | 能证明什么 |
| --- | --- | --- |
| XML 与 native 结构 | `validate_drawio.py`、`outputs/validation.json` | root/layer、唯一 ID、几何、父级、端点引用、stencil 解码与必备文字有效；四张主图没有图片/远端资产。 |
| 实际引擎回读 | `validate_drawio.py --roundtrip-dir outputs` | draw.io 真正加载后的 cell IDs 与源文件一致；核对 `.render.json` 中的源 SHA256，拒绝缺失或过期证据。 |
| 导出载体 | `verify_exports.py`、`outputs/exports-validation.json` | SVG/PNG 带源 XML；主 SVG 保留真实文字；PDF 能提取文字且没有位图层。 |
| 科学与视觉 | 逐项对照 brief、源图及最终预览 | 箭头含义、分区、数值、标注、文字拥挤、图标可辨认和最终论文版心可读性；这些不能由 XML 检查替代。 |

## 已遇到的问题与处理

- **空白/未加载**：先看编辑器网络响应与 `init/load` 事件；导出器使用普通浏览器 User-Agent，实际测试后可正常加载。网络失败就停止该次导出，不循环堆叠浏览器。
- **导出超时**：每个消息等待上限 120 秒。先确认网站可达和实际浏览器启动成功，再重试一次或切换本地 Desktop。
- **圆筒越界**：原生 `cylinder` 的尺寸样式在当前渲染中曾导致异常圆弧。本例 `buffer` 用筒身与两个椭圆明确构造，尺寸可控。
- **字体、重叠**：以实际 PNG/PDF 为准，先调整模块大小、文字框和边距，再调字号；旋转文字前使用适合的未旋转宽高，避免先被窄框折行。
- **图标破图**：原生 stencil 优先。PNG 图片单元的 data URI 必须符合 draw.io 样式语法，见 [图标获取与导入](04_tested_icon_sources.md)。
- **多页集合**：`all-figures.drawio` 方便切换四页；自动预览脚本按独立 `figure-N.drawio` 导出，以免把第一页面导出结果误记作全部页面。
