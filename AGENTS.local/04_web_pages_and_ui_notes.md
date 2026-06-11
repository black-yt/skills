# 网页与 GitHub Pages 长期经验

## 网页布局经验

- 需要“头部固定、列表滚动”时，不要让 `body` 自然滚动；用 `body { height: 100vh; overflow: hidden; }` 和 `.page { height: 100vh; display: flex; flex-direction: column; min-height: 0; }`。
- 固定区域使用 `flex: 0 0 auto`，可滚动区域使用 `flex: 1 1 auto; min-height: 0; overflow-y: auto`。
- 真正固定的表头不要放在滚动容器里依赖 `position: sticky`；如果用户要求完全不动，应把表头移到滚动容器外。
- 表头移出表格后，要用相同列宽复刻布局，例如 `grid-template-columns: minmax(0, 28%) minmax(0, 1fr) 56px`。
- 表头背景不要无意设置成不透明白色；默认用 `transparent`，除非确实需要遮挡滚动内容。
- 如果只想让固定表头文字视觉上更靠近列表，不要用 `margin` 推动布局；用 `transform: translateY(...)` 和 `z-index` 调整视觉位置。
- 如果表格列名对理解帮助不大，可以直接删除表头；删除后要同步移除表头 CSS、移动端隐藏规则和旧文案残留。
- 搜索工具栏和列表之间的空隙应优先通过工具栏 `margin-bottom` 调整；如果使用负 margin，要确认没有遮挡点击区域和下拉面板。
- 负 margin 只适合微调，过大时滚动列表、渐隐 mask 和搜索框会产生重叠感；改完必须检查滚动状态下的视觉边界。
- 移动端卡片式表格通常不需要固定表头；在 media query 中隐藏独立表头。
- 控制器和弹层要考虑 `z-index`，但不要通过过高层级掩盖布局问题。

## 网页交互经验

- 多选标签筛选不要用原生 `<select>`；使用自定义下拉面板加 checkbox，视觉才容易和页面统一。
- “全部”不应是一个 checkbox；应放在下拉面板顶部做成 `全选 / 取消全选` 操作按钮。
- 标签默认全选时，顶部按钮应显示 `取消全选`；取消后再显示 `全选`。
- 多标签筛选默认使用 OR 逻辑，除非用户明确要求 AND。
- tag 很多时，下拉面板必须有 `max-height` 和 `overflow-y: auto`，并加 `overscroll-behavior: contain`，避免内容被截断。
- 下拉面板可以比触发按钮更宽，但右边缘不能超出网页；常用做法是 `right: 0; width: min([宽度], calc(100vw - [边距]))`。
- 桌面端标签面板可以用 4 列网格；移动端应降为 1 列，避免文字挤压。
- 展开/收起动画优先用 `opacity`、`transform` 和 `max-height`，不要只切换 `display`，否则没有过渡。
- 下拉面板如果比触发框更宽，要明确对齐方向。靠近页面右侧时用 `right: 0` 和 `transform-origin: top right`，避免右边溢出。
- 点击表格行展开详情时，行内按钮的 click 需要 `event.stopPropagation()`，避免点击按钮同时折叠详情。
- 支持键盘操作：表格行用 `Enter` / `Space` 展开，弹层用 `Escape` 关闭，点击外部关闭。

## 网页视觉经验

- 同类控件必须共享同一个 class，例如链接按钮和复制按钮都用 `.detail-link`，避免浏览器默认 button 样式导致字体不一致。
- 对 button 显式设置 `appearance: none`、`font-family: inherit`、`font-size`、`font-weight`、`line-height`。
- 搜索框、按钮、下拉触发器应使用统一高度、圆角、边框、渐变背景、hover/focus 光晕。
- 自定义 checkbox 时隐藏原生 input，并用 `span::before` 画方框和勾选态。
- 展开面板、卡片、表格行使用同一组 CSS 变量：背景、边框、hover、文字、glow 都从变量读取。
- 背景颜色切换和“网页主题”要区分表述；如果只是切换白/黄/蓝/深色背景，应写“4 种背景颜色切换”。
- 动态背景放在固定全屏 canvas 中，设置 `pointer-events: none`，并确保页面主体不是完全不透明背景。
- 列表上下边缘的渐隐不要用白色或纯色 overlay 覆盖内容；优先用 `mask-image` 让内容本身逐渐透明，露出真实背景。
- 使用 `mask-image` 时，给滚动内容增加顶部/底部 padding，避免默认状态下第一条或最后一条内容直接被渐隐切掉。
- 如果渐隐边缘需要短一些，调 mask 的透明区高度，例如 `transparent 0, #000 24px, #000 calc(100% - 24px), transparent 100%`。
- 深色背景下必须检查正文、链接、按钮、代码、表格、弹层、滚动条是否可读。

## 网页功能经验

- 复制链接按钮优先使用 `navigator.clipboard.writeText`，并提供 `textarea + document.execCommand('copy')` fallback。
- 复制成功要有短暂状态反馈，例如按钮文案变为 `已复制` 后恢复。
- 需要“一键复制安装 Prompt”时，Prompt 应写成可直接交给 agent 的操作清单，而不是只复制 URL。
- 动态生成外链时，URL 统一由 base URL 和 path 拼接，路径要 `encodeURI`。
- 详情里的“查看完整文件”和“打开文件夹”是不同动作，文案要明确。
- 页面主说明要跟功能同步；新增复制安装 Prompt、复制链接、跳转 GitHub 等操作后，首页说明文案也要更新。
- 搜索输入应覆盖 skill 名称、路径、简介、预览内容和 tag。
- 空状态要在筛选无结果时显示，并放在滚动区内，避免顶部布局跳动。

## 网页验证经验

- 修改 HTML 内联 JS 后，提取 `<script>` 内容运行 `node --check`。
- 每次网页改动后运行 `git diff --check`。
- 改 UI 文案后用搜索确认旧文案没有残留。
- 改筛选控件后搜索确认旧实现没有残留，例如 `<select>`、旧 id、旧 class 或旧单选逻辑。
- 改布局后检查桌面和移动端 media query，不要只看桌面 CSS。
- 改渐隐、mask、固定表头后，检查默认第一条内容是否被切掉，滚动时是否自然消失，表头文字是否始终清晰。
- 如果能启动或打开页面，应实际检查：弹层是否超出视口、滚动区域是否正确、按钮字体是否一致、主题/背景颜色切换是否仍有效。
- 删除正文图标、移动资源或重命名文件后，检查资源引用仍然有效，特别是 favicon、图片、CSS、脚本路径。
