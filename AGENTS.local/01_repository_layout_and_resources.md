# 仓库结构与资源边界

这个文件只记录仓库结构、resource 目录和展示层的细节。项目总览、公开安全边界和每次对话都应默认知道的硬规则必须保留在 `AGENTS.md`。

## Skill 文件夹

- 每个 skill 目录必须包含 `SKILL.md`。
- `SKILL.md` 负责触发范围、核心规则、引用哪些 reference。
- `SKILL.md` 的 frontmatter 必须包含清晰的 `name` 和 `description`。
- `name` 要与文件夹名一致。

## Bundled Resources

- `references/` 放详细模板、示例和较长流程说明。
- `assets/` 放会被输出复用的静态资源。
- `scripts/` 放可执行辅助脚本。
- 不要随意增加额外说明文件；只有直接服务 skill 功能时才新增。
- Reference 可以更详细，但仍要便于按需阅读。
- 合并文件变得难导航时，按使用场景拆分。
- Markdown 技巧、LaTeX 技巧、代码模板应按上下文分开。
- 示例优先写成可复制骨架，并使用占位符。
- 除非用户明确要求且确认可公开，否则不要加入私人示例。

## 展示层

- `README.md` 是仓库主页中的 skill 列表和使用说明。
- `docs/index.html` 是 GitHub Pages 展示页的数据和前端实现。
- 网页相关文件统一放在 `docs/`，不要把 `index.html`、`assets/`、`.nojekyll` 散在仓库根目录。
- GitHub Pages 需要保留 `docs/.nojekyll`。
- 资源路径使用相对路径，例如 `assets/[name].svg`。
- 浏览器标签页标题、favicon、meta description 都要同步检查。
- 正文装饰图标和 favicon 是两件事，用户只要求去掉正文图标时不要误删 favicon。

## 目录边界

- 通常不需要修改 `download_skill.py`；只有下载逻辑、仓库结构或默认行为变化时才改。
- 通常不需要修改 `docs/.nojekyll`、favicon 或网页资源；只有页面资源或路径变化时才改。
- 如仓库采用 UI metadata，例如 `agents/openai.yaml`，新增或大改 skill 后也要同步生成或更新。
