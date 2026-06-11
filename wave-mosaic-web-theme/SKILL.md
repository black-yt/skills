---
name: wave-mosaic-web-theme
description: "当需要为网页复刻 black-yt 风格的高级前端主题时使用；覆盖 canvas wave-mosaic 动态方块背景、Pure White/Warm Yellow/Cool Blue/Dark 四种背景颜色切换、Space Grotesk 字体、CSS 变量、floating background dots、卡片/表格/按钮主题化和性能细节。"
---

# Wave Mosaic Web Theme

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 说明 Wave Mosaic 背景的视觉目标、canvas 动态方块规则、四种背景颜色切换和组件透明质感。 | 主题原则、动态背景参数、4 种背景颜色系统、组件风格规则 | 默认读取 | `SKILL.md` |
| 2 | 提供可直接复刻的 HTML/CSS/JS，实现固定全屏 canvas、主题切换按钮、CSS 变量、favicon 和字体加载。 | HTML、CSS、JS、canvas wave-mosaic、theme switcher、favicon、字体 | 需要实际复刻页面背景、主题切换、CSS 变量或完整 HTML/CSS/JS 时必须读取 | [references/theme-implementation.md](references/theme-implementation.md) |

## 使用原则

- 用这个 skill 复刻一种低噪声、高级、学术/技术感的网页主题。
- 必须包含固定全屏 canvas 动态方块背景，背景位于内容下方且不拦截点击。
- 必须包含 4 种背景颜色：`white`、`yellow`、`blue`、`dark`。
- 背景颜色切换使用 `<html data-theme="...">`；默认白色背景不设置 `data-theme`。
- 颜色必须由 CSS custom properties 驱动，不要在组件里散落硬编码主题色。
- 字体优先使用 `Space Grotesk`，中文/系统 fallback 使用 `Noto Sans SC`、`Inter`、`ui-sans-serif`。
- 页面主体保持透明，让 canvas wave-mosaic 背景可见。
- 组件风格使用轻微边框、低饱和渐变、细腻 hover 和主题色 glow，不使用大面积高饱和渐变。

## 必读实现

完整可复制实现见 [references/theme-implementation.md](references/theme-implementation.md)。

需要写页面时：

1. 先复制参考文件中的 `head` 字体和 favicon 配置。
2. 复制 4 种背景颜色的 CSS 变量。
3. 复制 `#theme-switcher` 和 `.theme-dot` 样式。
4. 复制 canvas wave-mosaic 背景脚本。
5. 复制 background color switcher 脚本。
6. 再按页面需求添加卡片、表格、accordion 或导航。

## 动态方块背景

核心参数必须保持一致：

| 参数 | 值 | 作用 |
| --- | --- | --- |
| `TILE` | `26` | 每个方块的网格尺寸 |
| `GAP` | `1` | 方块间隔，形成 mosaic grid |
| `FRAME_MS` | `1000 / 24` | 约 24 fps，减少 CPU 占用 |
| `t +=` | `0.007` | 慢速平静波动 |
| `z-index` | `0` | 背景层 |
| `pointer-events` | `none` | 不拦截页面交互 |

每个 tile 的透明度来自两组交叉 sine wave：

- `0.6 * sin(c * 0.21 + t * 0.36) * sin(r * 0.17 + t * 0.28)`
- `0.4 * sin(c * 0.11 - r * 0.13 + t * 0.19)`
- 用 cubic bias：`v = norm * norm * norm`
- 透明度范围：`0.004 + v * 0.186`
- 低于 `0.02` 的 tile 跳过绘制，提高性能。

背景颜色对应 RGB：

| Theme | RGB |
| --- | --- |
| `white` | `10,10,10` |
| `yellow` | `120,85,20` |
| `blue` | `38,88,155` |
| `dark` | `220,210,175` |

## 4 种背景颜色系统

必须提供这些背景颜色：

- `white`：纯白、黑灰文字、低对比浅灰边框。
- `yellow`：暖黄纸感、棕色文字、低饱和米色组件。
- `blue`：冷蓝技术感、蓝灰背景、深蓝文字。
- `dark`：近黑背景、暖灰文字、暗色组件。

必须包含这些变量组：

- 页面：`--bg`、`--masthead-bg`、`--masthead-border`
- 卡片/表格：`--paper-border`、`--paper-hover`
- 组件：`--c-bg-start`、`--c-bg-end`、`--c-border`、`--c-text`
- hover：`--c-hover-start`、`--c-hover-end`、`--c-hover-border`、`--c-hover-text`
- segmented / active：`--seg-start`、`--seg-end`、`--seg-shadow`、`--seg-inactive`、`--seg-active-text`
- glow：`--glow-rgb`

## Background Color Switcher

- 位置：固定在右下角，`bottom: 1.5em; right: 1.5em`。
- 容器：pill 形，`border-radius: 9999px`。
- dot：`18px × 18px` 圆点。
- active dot：`scale(1.35)`，并用双层 `box-shadow` 表达当前背景颜色。
- hover dot：`scale(1.18)`。
- 本地存储 key 推荐用项目名，例如 `site-background` 或 `[project]-background`。

## 组件复刻规则

- 内容容器用 `position: relative; z-index: 1` 压在 canvas 上方。
- 表格/卡片背景用 `linear-gradient(135deg, var(--c-bg-start), var(--c-bg-end))`。
- 边框统一用 `1px` 或 `1.5px solid var(--c-border)`。
- hover 时只做轻微 `translateY(-1px/-2px)`、边框变深和低透明阴影。
- 深色背景要显式设置文本、链接、表格边框和代码块颜色。
- 移动端避免内容宽度溢出；固定控制器要给足 `z-index`。

## 验证清单

- 4 个 background dots 都可点击，刷新后保留背景颜色。
- `white` 背景时 `<html>` 不带 `data-theme`。
- canvas 背景可见，页面主体不是不透明白底。
- 背景在切换背景颜色后同步变化。
- 滚动和点击不受 canvas 影响。
- 切到后台时动画暂停，回到页面后恢复。
- mobile resize 不因为地址栏高度变化频繁重设 canvas。
- 深色模式下正文、链接、表格、代码块都可读。
