# 经过实测的图标来源

这里只收录完成实际获取、文件检查和 draw.io 渲染的路线。测试日期为 **2026-10-27**，后续使用仍检查具体素材的许可和端点响应。

## 已走通的来源

| 网站 | 实测方式与素材 | 已验证能力和范围 |
| --- | --- | --- |
| [Yesicon](https://yesicon.app/) | 获取 `tabler:brain`、`snowflake`、`file-code`、`chart-bar`、`yarn` 的详情元数据，下载 Iconify SVG，转成原生 stencil，并在图 1/2 中实际加载导出。 | 作者、许可、viewBox 和集合版本可查询；本轮 Tabler 为 `3.49.0`、Paweł Kuna、MIT。验证的是下述 API 获取链，不保证每次网页按钮界面都相同。 |
| [Flaticon](https://www.flaticon.com/free-icon/yarn_11000244) | 详情页确认作者 Pop Vectors 和需要署名的免费许可；下载该页链接的 512×512 PNG，再以独立图片单元放入本地获取案例，已由 draw.io 成功导出。 | 只验证了此图标的 PNG 获取与显示；未验证 SVG、EPS、批量下载或免登录获取所有素材。原始 PNG 不放入公开 skill 包。 |

## Yesicon → 原生 draw.io 图标

实际使用的详情页：[brain](https://yesicon.app/tabler/brain)、[snowflake](https://yesicon.app/tabler/snowflake)、[file-code](https://yesicon.app/tabler/file-code)、[chart-bar](https://yesicon.app/tabler/chart-bar)、[yarn](https://yesicon.app/tabler/yarn)。

先查看网站元数据，保留作者和许可，然后下载其 Iconify 数据源 SVG：

```bash
curl -fL 'https://yesicon.app/api/icon/tabler:brain?locale=en' -o brain.metadata.json
curl -fL 'https://api.iconify.design/tabler/brain.svg' -o brain.svg
```

本 skill 已把这条流程做成完整脚本：

```bash
.venv/bin/python scripts/fetch_icons.py
```

- **输入**：可用 `--icons tabler:brain tabler:yarn` 显式选择；`--output [ICON_DIR]` 改保存目录。新增集合前先核对该集合及单个图标的作者、许可和再分发条件。
- **输出**：`assets/icons/*.svg` 为真实下载；`*.shape.xml` 为转换后的原生 stencil；`sources.json` 保存详情页、元数据/下载 URL、作者、许可、集合版本和文件 SHA256；`TABLER-LICENSE.txt` 保留上游 MIT 声明。
- **转换**：`fetch_icons.py` 使用 `svgpathtools` 将 SVG path 的直线、贝塞尔与圆弧转成 draw.io 原生 path 命令。运行时使用已转换快照，不需要再次联网或安装 SVG 解析依赖。
- **支持边界**：当前脚本支持无 transform、无内联 CSS 的单色 `path`、`circle`、`line`、`polyline`、`polygon`、`rect`；transform、CSS、mask、gradient、text、image 等明确报错。不要删除无法理解的 SVG 元素后冒称转换成功。
- **编辑**：`components.native_icon` 把 `.shape.xml` 直接嵌入 `.drawio`，图中没有 SVG 图片单元。可用格式面板改线色/填色；需要改轮廓时选择图标再打开 Edit Shape。
- **实际案例**：图 1 的脑、文档/图表、冻结雪花和纱线，以及图 2 的脑、冻结雪花、纱线都走过这条获取链。每个 `.drawio` 是自包含文件，离线打开不依赖网站。

## 双来源获取与导入案例

以下命令会真实获取 Yesicon/Tabler brain 和 Flaticon 的指定 yarn PNG，并生成本地 `.drawio` 对照页。Flaticon 作者署名已经放在该页中：

```bash
.venv/bin/python scripts/probe_icon_sources.py
node scripts/export_drawio.cjs outputs/icon-acquisition/icon-acquisition.drawio
python3 scripts/validate_drawio.py outputs/icon-acquisition/icon-acquisition.drawio --allow-icon-images --roundtrip-dir outputs --report outputs/icon-acquisition-validation.json
```

`outputs/icon-acquisition/` 保存实际 SVG、PNG、shape XML、来源清单和 `.drawio`。导出后的对照页在 `outputs/icon-acquisition.png` / `.svg` / `.pdf`。左侧是原生 stencil；右侧是独立 PNG 图片单元。文字和布局均保持原生对象。

Flaticon 的已验证素材信息：

- 详情页：<https://www.flaticon.com/free-icon/yarn_11000244>。
- 该页链接的 PNG：<https://cdn-icons-png.flaticon.com/512/11000/11000244.png>。
- 署名：**Yarn icon by Pop Vectors from Flaticon**，链接回该素材页；免费使用需要署名，重新下载时核对当时条款。
- 许可入口：<https://www.flaticon.com/legal>（本轮 `terms-of-use` 重定向至此）。论文、演示文稿等实际成品按适用条款保留署名；不要将原始素材单独打包成供他人下载的图标库。
- 公共 skill 只包含获取代码和来源；下载的 Flaticon PNG 与本地对照图保存在 ignored `outputs/`。

## PNG 的 data URI 语法

本轮实际修复并验证了以下写法：

```python
import base64
image_style_value = 'data:image/png,' + base64.b64encode(png_bytes).decode()
d.shape('downloaded-icon', 100, 80, 64, 64,
        kind='image', image=image_style_value, imageAspect=1,
        fill='none', stroke='none', sketch=False)
```

draw.io 的 `style` 用分号分隔属性；直接把 `data:image/png;base64,...` 塞进 `image=` 会被拆开并显示破图。这里使用 draw.io 支持的 `data:image/png,BASE64` 形式。只有实际图标单元允许使用这种图片路径，整张论文图仍需重建为可编辑的标签、形状和连接线。
