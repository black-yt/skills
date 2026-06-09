# Skills

这是徐望瀚在日常工作中使用和维护的一组可复用 skills。每个 skill 使用独立子文件夹，并按 Anthropic/Claude Skills 风格提供 `SKILL.md`。

每个 skill 的基本结构：

```text
skill-name/
  SKILL.md
  scripts/      # 可选，放可执行脚本
  references/   # 可选，放按需读取的参考资料
  assets/       # 可选，放模板、图片、示例文件等素材
```

## Skill 列表

| Skill | 入口文档 | 用途 |
| --- | --- | --- |
| `ai-conference-paper-writing` | [`ai-conference-paper-writing/SKILL.md`](ai-conference-paper-writing/SKILL.md) | 撰写、重构和打磨 AI conference paper，覆盖 research story、核心包装关键词、Introduction、Related Work、Method、Experiments、图表布局、case study、citation 和 reviewer-risk 检查。 |
| `browser-render-visualization` | [`browser-render-visualization/SKILL.md`](browser-render-visualization/SKILL.md) | 使用 Playwright 渲染网页前端并保存桌面/移动端截图，检查 GitHub Pages、本地静态页面、Canvas/Three.js 空白渲染、布局溢出和浏览器报错。 |
| `context-overlay` | [`context-overlay/SKILL.md`](context-overlay/SKILL.md) | 配置和验证 OpenAI-compatible context overlay proxy，覆盖 rule matching、prompt/context 注入、prompt patch、routing、reject、skill_dir 检索和转发安全。 |
| `docx-splitting` | [`docx-splitting/SKILL.md`](docx-splitting/SKILL.md) | 在 Windows + Microsoft Word 环境中，通过 [`scripts/split_docx.py`](docx-splitting/scripts/split_docx.py) 按页无损拆分 `.docx` 文档。 |
| `frontend-markdown-rendering` | [`frontend-markdown-rendering/SKILL.md`](frontend-markdown-rendering/SKILL.md) | 在前端只渲染最终 assistant Markdown，保留工具过程为纯文本/JSON，并支持表格、代码块、图片、KaTeX 公式、Mermaid 和 workspace 图片安全访问。 |
| `github-readme-writing` | [`github-readme-writing/SKILL.md`](github-readme-writing/SKILL.md) | 创建或优化 GitHub 项目 README，包含居中标题、badge、teaser、highlights、news、Mermaid、GitHub 公式渲染、目录结构、quick start、联系方式、citation 和 star history。 |
| `huggingface-dataset-publishing` | [`huggingface-dataset-publishing/SKILL.md`](huggingface-dataset-publishing/SKILL.md) | 创建、上传、验证和维护 Hugging Face Dataset，尤其是图片/多图字段、JSON metadata、`push_to_hub`、回读验证和 dataset card。 |
| `wave-mosaic-web-theme` | [`wave-mosaic-web-theme/SKILL.md`](wave-mosaic-web-theme/SKILL.md) | 复刻 black-yt 风格前端主题，覆盖 canvas wave-mosaic 动态方块背景、4 种背景颜色切换、Space Grotesk 字体和高级卡片/表格视觉。 |
| `latex-compiling` | [`latex-compiling/SKILL.md`](latex-compiling/SKILL.md) | 使用系统级 `latexmk` + `pdflatex` 编译 LaTeX，并隔离 build 目录与 TeX 缓存。 |
| `llm-image-generation` | [`llm-image-generation/SKILL.md`](llm-image-generation/SKILL.md) | 通过 OpenAI-compatible LLM 网关生成图片，优先读取 `LLM_API_KEY`/`LLM_BASE_URL`，覆盖图像模型选择、长等待时间、base64/URL 保存和排错。 |
| `markdown-to-pdf` | [`markdown-to-pdf/SKILL.md`](markdown-to-pdf/SKILL.md) | 使用 [`scripts/md_to_pdf.py`](markdown-to-pdf/scripts/md_to_pdf.py) 将 Markdown 转为 PDF，支持表格、代码块、图片路径和基础 CSS。 |
| `markdown-to-docx` | [`markdown-to-docx/SKILL.md`](markdown-to-docx/SKILL.md) | 使用 [`scripts/build_docx.py`](markdown-to-docx/scripts/build_docx.py) 将 Markdown 文档转为 Word `.docx`，支持本地图片、caption、标题样式、列表、引用、图文块表格和可见字数估算。 |
| `llm-deploy-training` | [`llm-deploy-training/SKILL.md`](llm-deploy-training/SKILL.md) | 部署和训练 LLM/VLM，覆盖 vLLM OpenAI-compatible 服务、多模态限制、Qwen3.5 工具调用、CUDA Graph 策略，以及 ms-swift SFT/DPO/GRPO full training。 |
| `pdf-to-images` | [`pdf-to-images/SKILL.md`](pdf-to-images/SKILL.md) | 使用系统级 Ghostscript (`gs`) 或 Poppler `pdftoppm` 将 PDF 页面导出为 PNG/JPEG 图片，支持单页、页码范围、整篇导出和论文排版可视化检查。 |
| `pdf-parsing` | [`pdf-parsing/SKILL.md`](pdf-parsing/SKILL.md) | 使用 `structai.read_pdf` 将 PDF 解析为本地 Markdown，并处理图片抽取、代理重试和解析质量检查。 |
| `researchharness` | [`researchharness/SKILL.md`](researchharness/SKILL.md) | 使用 InternScience ResearchHarness 作为轻量 tool-using LLM agent runtime，覆盖安装配置、CLI、本地前端、OpenAI-compatible API、Python API、工具选择、workspace、trace 和测试。 |
| `structai` | [`structai/SKILL.md`](structai/SKILL.md) | 使用 StructAI Python 工具箱搭建 LLM workflow，覆盖 `LLMAgent`、结构化输出、Judge、并发、文件/PDF 工具、文本解析、私网 no_proxy 和 timeout。 |
| `lab-cluster-1` | [`lab-cluster-1/SKILL.md`](lab-cluster-1/SKILL.md) | 在 lab cluster 1 / PJLAB 上处理开发机登录、路径和环境、网络代理、模型权重、`rlaunch`/`rjob`、服务部署和排错等集群工作流。 |

## 下载 Skill 文件夹

GitHub 网页不支持直接下载指定文件夹。可以先下载本目录下的 `download_skill.py`，之后用它下载本仓库中的一个或多个 skill 文件夹。

### 下载脚本

```bash
curl -L -o download_skill.py https://raw.githubusercontent.com/black-yt/skills/main/download_skill.py
```

### 下载单个 Skill

```bash
python download_skill.py docx-splitting
```

下载后会生成同名目录：

```text
docx-splitting/
  SKILL.md
  scripts/
    split_docx.py
```

指定输出目录：

```bash
python download_skill.py docx-splitting -o my_skills/docx-splitting
```

### 一次下载多个 Skill

```bash
python download_skill.py docx-splitting pdf-parsing markdown-to-pdf -o skills
```

多个 skill 同时下载时，`-o` 表示父目录。上面的命令会生成：

```text
skills/
  docx-splitting/
  pdf-parsing/
  markdown-to-pdf/
```

默认不会覆盖已存在文件；需要覆盖时加 `--overwrite`。

如果 GitHub API 触发限流，可以设置 `GITHUB_TOKEN` 后重试：

```bash
export GITHUB_TOKEN=<your_github_token>
python download_skill.py docx-splitting
```
