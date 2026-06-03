# 仓库维护指南

本仓库存放可复用的 agent skills。维护目标是：易读、可复用、可公开分享、改动克制。

## 隐私与安全

- 不要在仓库级说明中写入私人姓名、账号、私有路径、内部主机名、凭据、访问值或私有服务地址。
- 如果某个 skill 必须记录环境细节，只在用户明确要求时写入对应 skill。
- 示例中不要出现真实凭据，统一使用 `[API_KEY]`、`[PROJECT_ROOT]`、`[HOST]`、`[DATASET_ID]` 等占位符。
- 除非 skill 本身确实需要且内容可公开，否则不要记录本地机器状态。

## Git 工作流

- 编辑前先查看 `git status --short`。
- 保留无关的用户改动，不要回滚任务外文件。
- 改动保持最小、聚焦、可解释。
- 提交或推送前运行 `git diff --check`。
- 用户没有明确要求时，不要 commit 或 push。
- 拆分、移动或重命名文件后，必须检查旧路径引用是否已更新、内容是否丢失。

## Skill 结构

- 每个 skill 目录必须包含 `SKILL.md`。
- `SKILL.md` 负责触发范围、核心规则、引用哪些 reference。
- `references/` 放详细模板、示例和较长流程说明。
- `assets/` 放会被输出复用的静态资源。
- 不要随意增加额外说明文件；只有直接服务 skill 功能时才新增。

## 新增或更新 Skill 的同步清单

- 新增 skill 时，必须新建独立文件夹，并至少包含 `SKILL.md`。
- `SKILL.md` 的 frontmatter 必须包含清晰的 `name` 和 `description`；`name` 要与文件夹名一致。
- 如有详细模板、长示例、图片、脚本，分别放入 `references/`、`assets/`、`scripts/`，不要把所有内容塞进主文件。
- 必须同步更新 `README.md` 的 Skill 列表，包含 skill 名称、入口链接和一句用途说明。
- 必须同步更新 `docs/index.html` 中的网页展示数据，包含 `name`、`path`、`tags`、`desc` 和预览 `content`。
- 新增网页 tag 时，优先复用已有 tag；确实需要新增时，保持中英文粒度一致，专有名词不要硬翻译。
- 如仓库采用 UI metadata，例如 `agents/openai.yaml`，新增或大改 skill 后也要同步生成或更新。
- 通常不需要修改 `download_skill.py`；只有下载逻辑、仓库结构或默认行为变化时才改。
- 通常不需要修改 `docs/.nojekyll`、favicon 或网页资源；只有页面资源或路径变化时才改。
- 新增 skill 后，用 `find . -maxdepth 2 -name SKILL.md`、`README.md` 和 `docs/index.html` 互相对照，确认没有漏展示、漏链接或路径写错。
- 提交前运行 `git diff --check`；若改了 `docs/index.html` 内联脚本，提取脚本或用现有方式做 JS 语法检查。

## Skill 书写风格

- 优先使用踩点式规则，不写大段多点描述。
- 多个要求放成短 bullet，并给出清晰标签。
- 避免过深层级；正常 skill 文件标题最多到三级。
- 可复制的代码块、命令模板和表格保持完整，不为了拆点破坏可用性。
- 未知值使用占位符，不要编造。
- 可复用的大段模板放入 reference，不要塞进主 `SKILL.md`。

## Skill 内容质量

- frontmatter description 要清楚说明触发范围，但不要写成超长清单。
- 明确写出 agent 必须做什么、避免什么、验证什么。
- 稳定规则和环境专属说明分开。
- 优先沿用仓库已有组织方式，不轻易发明新结构。
- 避免跨文件重复规则；需要发现性提示时，用短指针即可。
- 高风险工作流要包含验证步骤和失败处理。

## Reference 文件

- Reference 可以更详细，但仍要便于按需阅读。
- 合并文件变得难导航时，按使用场景拆分。
- Markdown 技巧、LaTeX 技巧、代码模板应按上下文分开。
- 示例优先写成可复制骨架，并使用占位符。
- 除非用户明确要求且确认可公开，否则不要加入私人示例。

## 网页与 GitHub Pages

- 网页相关文件统一放在 `docs/`，不要把 `index.html`、`assets/`、`.nojekyll` 散在仓库根目录。
- 静态展示页优先使用原生 HTML/CSS/JS；没有明确收益时不要引入构建工具或前端框架。
- GitHub Pages 需要保留 `docs/.nojekyll`，资源路径使用相对路径，例如 `assets/[name].svg`。
- 浏览器标签页标题、favicon、meta description 都要同步检查；正文装饰图标和 favicon 是两件事，用户只要求去掉正文图标时不要误删 favicon。
- 页面可见文案优先中文；`GitHub`、`PDF`、`LaTeX`、`Python`、`LLM`、`Canvas`、skill 名称等专有名词不要硬翻译。

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
- 安装 Prompt 应先要求使用仓库下载工具下载整个 skill 文件夹，再检查 `SKILL.md`、frontmatter、相对路径、`references/`、`assets/`、`scripts/`，最后再安装。
- 安装 Prompt 不要预设安装给某个具体 agent；如果不能确定 skills 安装目录，应要求先询问用户。
- 安装 Prompt 必须强调：任何潜在危险操作都要先征得用户同意，包括覆盖、删除、移动、改全局配置、安装软件、改 shell 配置、改权限或不可逆操作。
- 安装 Prompt 若使用本地下载检查目录，安装完成后应询问用户是否删除，未经确认不要删除。
- 动态生成外链时，URL 统一由 base URL 和 path 拼接，路径要 `encodeURI`。
- 详情里的“查看完整文件”和“打开文件夹”是不同动作，文案要明确。
- 页面主说明要跟功能同步；新增复制安装 Prompt、复制链接、跳转 GitHub 等操作后，首页说明文案也要更新。
- 搜索输入应覆盖 skill 名称、路径、简介、预览内容和 tag。
- 空状态要在筛选无结果时显示，并放在滚动区内，避免顶部布局跳动。

## 网页验证

- 修改 HTML 内联 JS 后，提取 `<script>` 内容运行 `node --check`。
- 每次网页改动后运行 `git diff --check`。
- 改 UI 文案后用搜索确认旧文案没有残留。
- 改筛选控件后搜索确认旧实现没有残留，例如 `<select>`、旧 id、旧 class 或旧单选逻辑。
- 改布局后检查桌面和移动端 media query，不要只看桌面 CSS。
- 改渐隐、mask、固定表头后，检查默认第一条内容是否被切掉，滚动时是否自然消失，表头文字是否始终清晰。
- 如果能启动或打开页面，应实际检查：弹层是否超出视口、滚动区域是否正确、按钮字体是否一致、主题/背景颜色切换是否仍有效。
- 删除正文图标、移动资源或重命名文件后，检查资源引用仍然有效，特别是 favicon、图片、CSS、脚本路径。

## Review 检查

- 请求的改动已经完成，且范围受控。
- 没有新增私人内容。
- 长自然语言规则已拆成清晰踩点。
- 没有引入不必要的深层标题。
- 已有 reference 路径仍然有效。
- `git diff --check` 通过。
- 最终回复前确认工作区状态。
