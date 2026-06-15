# 仓库维护指南

本仓库存放可复用的 agent skills。维护目标是：易读、可复用、可公开分享、改动克制。

## 项目概览

- 本仓库的核心产物是一个个独立 skill 文件夹；每个 skill 都以 `SKILL.md` 为入口，并可按需包含 `references/`、`assets/`、`scripts/`。
- `README.md` 和 `docs/index.html` 是对外展示层；新增、重命名或大改 skill 后必须保持它们与实际 skill 列表一致。
- 本仓库应保持可公开分享；不要写入 secrets、真实凭据、私有路径、内部主机、私有服务地址或个人本地状态。

## 深入指南

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 解释每个 skill 文件夹与仓库展示层的职责边界，说明 `SKILL.md`、`references/`、`assets/`、`scripts/`、`docs/`、`docs/.nojekyll`、favicon 和 `download_skill.py` 分别何时可改、何时不应顺手修改。 | layout、skill folder、`SKILL.md`、`references/`、`assets/`、`scripts/`、`docs/index.html`、`docs/.nojekyll`、favicon、`download_skill.py`、GitHub Pages、资源路径、生成物边界 | 新增/删除/移动 skill 文件夹前；拆分/合并 reference 前；移动 assets/scripts 前；修改 GitHub Pages 资源路径、favicon、下载脚本或展示层目录前必须读取 | `AGENTS.local/01_repository_layout_and_resources.md` |
| 02 | 记录新增和更新 skill 的完整维护流程，包括 frontmatter、reference 拆分、文件导航表、README 列表、`docs/index.html` 展示数据、安装 prompt、Markdown 公式和跨文件同步要求。 | skill workflow、frontmatter、name/description、file navigation、README.md、`docs/index.html`、tags、preview content、install prompt、GitHub Markdown math、reference split、coverage checklist | 新增 skill 前；大改 `SKILL.md` 前；修改导航表前；更新 README/docs 展示项前；写 GitHub Markdown 公式前；整理用户大段经验或拆分 reference 前必须读取 | `AGENTS.local/02_skill_workflows_and_formats.md` |
| 03 | 汇总维护过程中的风险和验证方法，覆盖隐私泄漏、路径失效、跨 skill 规则不一致、第三方源码误改、公式渲染失败、内容迁移丢失、canonical copy 同步、`rsync --dry-run`、Git 暂存提交和 push 前检查。 | pitfalls、privacy、validation、source tracing、site-packages、third-party docs、git diff、git status、commit、push、stale path、content loss、cross-skill consistency、formula rendering、canonical copy、rsync dry-run | 排查异常时；复制经验到多个 skill 前；追溯第三方库源码前；移动/删除文件后；同步 ignored 指南到 canonical copy 前；提交或 push 前；检查内容是否丢失、路径是否过期或规则是否冲突时必须读取 | `AGENTS.local/03_risks_validation_and_git.md` |
| 04 | 保留 `docs/` 静态网页的长期 UI 经验，覆盖固定头部和滚动列表、自定义多选标签、复制链接/安装 prompt、按钮字体一致性、渐隐 mask、4 种背景颜色切换和 GitHub Pages 视觉验证。 | web UI、`docs/index.html`、layout、fixed header、scroll list、tag filter、checkbox dropdown、copy prompt、copy link、button style、mask-image、theme switcher、GitHub Pages、responsive | 修改 `docs/` 前端前；调整搜索/筛选/展开交互前；改复制按钮或安装 prompt 前；改渐隐滚动、主题切换、移动端样式、favicon 或页面文案前必须读取 | `AGENTS.local/04_web_pages_and_ui_notes.md` |

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

## WSL Shell 规则

- 本仓库位于 `/mnt/d/...` WSL 工作区，运行 shell 命令时坚持使用 WSL bash，不要因为一次失败就切到 PowerShell、cmd、Windows Node 或浏览器 fetch。
- 需要 shell 初始化、`nvm`、conda、token、代理变量或联网环境的命令，优先使用交互式 WSL bash，例如 `bash -ic '...'`；只检查 prompt 时可用 `bash -i -c 'printf "%s\n" "$PS1"'`。
- 联网任务失败时，先检查是否需要提权/原生 WSL 执行，再检查代理变量是否污染；必要时只对当前命令临时关闭代理，不要修改长期 shell 配置。

## Skill 核心规则

- 每个 skill 目录必须包含 `SKILL.md`。
- `SKILL.md` 的 frontmatter 必须包含清晰的 `name` 和 `description`；`name` 要与文件夹名一致。
- `SKILL.md` 负责触发范围、核心规则、引用哪些 reference。
- `references/` 放详细模板、示例和较长流程说明；`assets/` 放会被输出复用的静态资源；`scripts/` 放可执行辅助脚本。
- 不要随意增加额外说明文件；只有直接服务 skill 功能时才新增。
- 新增或大改 skill 后，必须同步检查 `README.md` 和 `docs/index.html`。
- 新增、删除或重命名 skill 后，`README.md` 和 `docs/index.html` 不仅要同步名称、链接和数量，还要按当前仓库展示顺序重新排序；重命名后的条目不能停留在旧名称所在位置。
- 维护任何 `AGENTS.md`、`CLAUDE.md` 或同类默认加载的 agent 指南时，主入口文件必须包含项目或工作空间的整体描述，让 agent 默认理解项目目标、主要结构、关键产物和维护边界；这些总览信息不要拆到 local 文件。
- skill 默认面向“使用这个能力的用户”，不是面向“维护上游仓库的人”；除非 skill 明确是维护类，例如 `agents-md-maintenance`，否则不要记录上游 `.gitignore`、发布流程、内部维护习惯或与使用技能无关的仓库治理细节。
- `lab-cluster-1` 和 `lab-cluster-1-web-portal` 是面向相同集群使用者的具体 skill，不是通用模板；维护时可以保留技能本身必要的具体网站、分区、namespace、charged group、mount 目录、共享存储路径、CUDA/conda 路径和登录 endpoint。
- 上述集群 skill 仍需泛化不属于技能本身的一次性项目路径、脚本路径、临时 job 名、真实凭据、token、cookie、账号密码、个人运行状态和任务私有数据。

## 文件导航表规则

- 有 `references/` 的 `SKILL.md` 必须包含文件导航表，表头固定为 `序号 / 文件内容概览 / 关键词 / 触发时机 / 文件路径`。
- `序号` 使用稳定整数；如果导航对象文件名带数字前缀，序号必须和文件名前缀一致。
- `文件内容概览` 必须写成足够具体的 1-2 个短句，说明文件实际覆盖的模块、文件名、命令、边界和排除项；不要只写“模板”“工作流”“详细说明”。
- `关键词` 要写足够多的检索词，通常至少 6-12 项；包含同义词、命令名、文件名、目录名、库名、错误类型和场景词，用逗号分隔，但不要替代内容概览。
- `触发时机` 要列出多个具体可执行条件，通常至少 3 个，用分号分隔，例如“修改 X 前必须读取；运行 Y 前必须读取；排查 Z 时必须读取”；避免只写“需要时读取”或过宽泛的“默认读取”。
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
