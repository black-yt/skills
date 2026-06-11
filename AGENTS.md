# 仓库维护指南

本仓库存放可复用的 agent skills。维护目标是：易读、可复用、可公开分享、改动克制。

## 项目概览

- 本仓库的核心产物是一个个独立 skill 文件夹；每个 skill 都以 `SKILL.md` 为入口，并可按需包含 `references/`、`assets/`、`scripts/`。
- `README.md` 和 `docs/index.html` 是对外展示层；新增、重命名或大改 skill 后必须保持它们与实际 skill 列表一致。
- 本仓库应保持可公开分享；不要写入 secrets、真实凭据、私有路径、内部主机、私有服务地址或个人本地状态。

## 深入指南

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 解释 skill 目录、resource 目录、`docs/` 展示层和通常不应修改的资源路径各自承担什么职责。 | layout、SKILL.md、references、assets、docs、GitHub Pages | 新增目录、移动文件、拆分 reference 或修改展示资源路径前必须读取 | `AGENTS.local/01_repository_layout_and_resources.md` |
| 02 | 记录新增/更新 skill、拆分 reference、同步 README/docs、维护网页展示数据、安装 prompt 和结构化格式的完整规则。 | workflow、frontmatter、file navigation、README、docs/index.html、install prompt | 新增或大改 skill、修改导航表、修改 README/docs 展示项或写 Markdown 公式前必须读取 | `AGENTS.local/02_skill_workflows_and_formats.md` |
| 03 | 汇总隐私泄漏、路径失效、跨 skill 不一致、源码误改、公式渲染失败等风险，以及验证命令和 Git 交付规则。 | pitfalls、validation、source tracing、git、diff、release | 排查异常、复制经验到多个 skill、追溯第三方库、提交前检查或涉及 commit/push 前必须读取 | `AGENTS.local/03_risks_validation_and_git.md` |
| 04 | 保留网页布局、标签筛选、按钮样式、复制安装 prompt、渐隐滚动、主题切换和 GitHub Pages 验证等长期 UI 经验。 | web UI、layout、filter、copy prompt、mask、GitHub Pages | 修改 `docs/` 前端、网页交互、视觉样式、筛选逻辑或复制按钮行为前必须读取 | `AGENTS.local/04_web_pages_and_ui_notes.md` |

如果某个文件不存在，不要假设其内容；按当前任务需要创建或更新，并保持本表同步。

## 安全规则

- 不要在仓库级说明中写入私人姓名、账号、私有路径、内部主机名、凭据、访问值或私有服务地址。
- 如果某个 skill 必须记录环境细节，只在用户明确要求时写入对应 skill，并优先使用占位符。
- 示例中不要出现真实凭据，统一使用 `[API_KEY]`、`[PROJECT_ROOT]`、`[HOST]`、`[DATASET_ID]` 等占位符。
- 除非 skill 本身确实需要且内容可公开，否则不要记录本地机器状态。
- 不要修改 `site-packages`、pip 安装目录、共享 checkout、editable checkout 或共享环境；源码追溯只能只读。

## Git 规则

- 编辑前先查看 `git status --short`。
- 保留无关的用户改动，不要回滚任务外文件。
- 改动保持最小、聚焦、可解释。
- 提交或推送前运行 `git diff --check`。
- 用户没有明确要求时，不要 commit 或 push。
- 拆分、移动或重命名文件后，必须检查旧路径引用是否已更新、内容是否丢失。

## Skill 核心规则

- 每个 skill 目录必须包含 `SKILL.md`。
- `SKILL.md` 的 frontmatter 必须包含清晰的 `name` 和 `description`；`name` 要与文件夹名一致。
- `SKILL.md` 负责触发范围、核心规则、引用哪些 reference。
- `references/` 放详细模板、示例和较长流程说明；`assets/` 放会被输出复用的静态资源；`scripts/` 放可执行辅助脚本。
- 不要随意增加额外说明文件；只有直接服务 skill 功能时才新增。
- 新增或大改 skill 后，必须同步检查 `README.md` 和 `docs/index.html`。

## 文件导航表规则

- 有 `references/` 的 `SKILL.md` 必须包含文件导航表，表头固定为 `序号 / 文件内容概览 / 关键词 / 触发时机 / 文件路径`。
- `序号` 使用稳定整数；如果导航对象文件名带数字前缀，序号必须和文件名前缀一致。
- `文件内容概览` 必须写成能解释文件实际内容边界的具体短句，让模型不需要靠猜测或不断打开文件寻找；不要只写“模板”“工作流”“详细说明”。
- `关键词` 写检索词、命令名、子系统名、文件类型或风险词；用逗号分隔，不要替代内容概览。
- `触发时机` 写可执行条件，例如“修改 X 前必须读取”“运行 Y 前必须读取”“排查 Z 时必须读取”；避免“需要时读取”这种无法执行的描述。
- `文件路径` 使用相对路径，放最后一列；移动、重命名或拆分文件后必须同步更新。
- 示例里的 `...` 只表示省略；真实导航表中必须删除或替换成实际文件行。

## 写作与内容质量

- 优先使用踩点式规则，不写大段多点描述。
- 多个要求放成短 bullet，并给出清晰标签。
- 避免过深层级；正常 skill 文件标题最多到三级。
- 可复制的代码块、命令模板和表格保持完整，不为了拆点破坏可用性。
- 未知值使用占位符，不要编造。
- 可复用的大段模板放入 reference，不要塞进主 `SKILL.md`。
- 明确写出 agent 必须做什么、避免什么、验证什么。
- 稳定规则和环境专属说明分开，优先沿用仓库已有组织方式。
- 高风险工作流要包含验证步骤和失败处理。
- 将用户给的大段经验写入 skill 时，先拆成可检查的覆盖清单，再逐项确认新内容完整覆盖。
- 重写、合并或整理已有章节时，必须反查 `git diff --unified=0` 中被删除的有效规则、示例和命令。

## 文档与源码追溯

- 记录第三方库经验时，优先推荐官方教程、官方文档、recipe、API reference 和当前环境 CLI help；源码阅读应放在官方文档之后。
- 文档链接必须与当前安装版本匹配；不要把 `stable`、`latest` 或某个历史版本链接写成固定答案。
- 需要写具体文档链接时，先说明如何获取当前版本，例如 `python -c 'import vllm; print(vllm.__version__)'`。
- 源码追溯用于确认当前安装版本的真实行为、参数名、默认值、兼容分支、错误路径和边界条件。
- 追源码示例应使用 `module.__file__`、`module.__version__`、`inspect.getsource(...)`、`command --help` 等只读方法。

## 网页与 GitHub Pages

- 网页相关文件统一放在 `docs/`，不要把 `index.html`、`assets/`、`.nojekyll` 散在仓库根目录。
- 静态展示页优先使用原生 HTML/CSS/JS；没有明确收益时不要引入构建工具或前端框架。
- GitHub Pages 需要保留 `docs/.nojekyll`，资源路径使用相对路径。
- 页面可见文案优先中文；`GitHub`、`PDF`、`LaTeX`、`Python`、`LLM`、`Canvas`、skill 名称等专有名词不要硬翻译。
- 修改 `docs/index.html` 内联 JS 后，提取 `<script>` 内容运行 `node --check`。

## Review 检查

- 请求的改动已经完成，且范围受控。
- 没有新增私人内容。
- 长自然语言规则已拆成清晰踩点。
- 没有引入不必要的深层标题。
- 已有 reference 路径仍然有效。
- `README.md`、`docs/index.html` 和实际 skill 文件夹一致。
- `git diff --check` 通过。
- 最终回复前确认工作区状态。
