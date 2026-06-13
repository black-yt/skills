# 风险、验证与 Git 规则

## 隐私泄漏

- 不要在仓库级说明中写入私人姓名、账号、私有路径、内部主机名、凭据、访问值或私有服务地址。
- 示例中不要出现真实凭据。
- 除非用户明确要求且确认可公开，否则不要加入私人示例。

## 内容缺失

- 将用户给的大段经验写入 skill 时，不要只靠关键词抽查或肉眼判断。
- 重写、合并或整理已有章节时，要检查被删除的有效规则、示例和命令是否已保留、合并或明确移除。
- 同一经验写入多个 skill 时，不要让一个位置缺少关键示例、验证步骤或失败处理。

## 源码误改

- 记录第三方库经验时，优先推荐官方教程、官方文档、recipe、API reference 和当前环境 CLI help；源码阅读应放在官方文档之后。
- 文档链接必须与当前安装版本匹配。不要把 `stable`、`latest` 或某个历史版本链接写成固定答案；如果只能给模板，使用 `<matched-version>` 这类占位符。
- 源码追溯用于确认当前安装版本的真实行为、参数名、默认值、兼容分支、错误路径和边界条件，不用于替代官方教程学习推荐用法。
- 源码必须只读。不要修改 `site-packages`、pip 安装目录、共享 checkout、editable checkout 或共享环境。
- 如果确实需要改第三方库，必须先向用户说明风险、改动范围和安装方式；只有用户明确同意后，才 clone 独立副本并 editable install。
- 追源码示例应使用 `module.__file__`、`module.__version__`、`inspect.getsource(...)`、`command --help` 等只读方法。

## Reference 与路径失效

- 拆分 reference 后必须检查旧路径引用。
- 删除或重命名 reference 后，`SKILL.md`、`AGENTS.md`、README、docs 里的旧路径都要检查。
- 新增文件必须能从主 `SKILL.md`、`AGENTS.md` 或其他入口追溯，不要留下幽灵文件。

## Canonical Copy 同步检查

- 如果某个项目的 `AGENTS.md` 或 `AGENTS.local/` 被主仓库 ignore，只能在用户明确授权后同步 canonical copy、commit 或 push。
- 同步前必须确认目标仓库、目标目录和将写入的文件列表。
- `rsync` 源路径末尾斜杠含义不同：`AGENTS.local` 复制目录本身，`AGENTS.local/` 复制目录内容。
- 使用 `--delete` 前必须先执行 `--dry-run`，确认不会误删或误写上级目录。

```bash
# 同步单个入口文件，先预演再执行
rsync -a --dry-run AGENTS.md [CANONICAL_ROOT]/[REPO_NAME]/AGENTS.md
rsync -a AGENTS.md [CANONICAL_ROOT]/[REPO_NAME]/AGENTS.md

# 同步 AGENTS.local 目录内容，目标应是该仓库自己的 AGENTS.local/
rsync -a --delete --dry-run AGENTS.local/ [CANONICAL_ROOT]/[REPO_NAME]/AGENTS.local/
rsync -a --delete AGENTS.local/ [CANONICAL_ROOT]/[REPO_NAME]/AGENTS.local/
```

## 公式渲染失败

- GitHub Markdown 公式优先使用 `math` 围栏。
- 不要在 Markdown 表格中塞复杂公式。
- 避免 `x_{<t}`、高风险宏和未转义 HTML 标签。
- 改公式相关内容后，要检查 GitHub 页面是否能渲染，而不是只看本地 Markdown。

## 基础状态命令

```bash
git status --short
git diff --check
```

## Skill 列表对照

```bash
find . -maxdepth 2 -name SKILL.md
```

新增 skill 后，用实际 `SKILL.md` 列表、`README.md` 和 `docs/index.html` 互相对照，确认没有漏展示、漏链接或路径写错。
重命名 skill 后还要确认两处展示顺序已重排；不要只检查名称和链接是否存在。

## Reference 导航检查

确认有 `references/` 的 skill 主文件包含导航表，并能追溯到每个 reference：

```bash
python3 - <<'PY'
from pathlib import Path
import re
for skill in sorted(p for p in Path('.').iterdir() if p.is_dir() and (p / 'SKILL.md').exists()):
    refs = sorted((skill / 'references').glob('*.md')) if (skill / 'references').exists() else []
    if not refs:
        continue
    text = (skill / 'SKILL.md').read_text(encoding='utf-8')
    header = '| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |'
    if header not in text:
        raise SystemExit(f'{skill}: missing navigation table')
    for ref in refs:
        rel = ref.relative_to(skill).as_posix()
        if rel not in text:
            raise SystemExit(f'{skill}: missing {rel}')
    for line in text.splitlines():
        if not line.startswith('| ') or line.startswith('| ---') or line.startswith('| 序号'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) != 5 or not cells[0].isdigit():
            continue
        keyword_count = len([x for x in re.split(r'[、,，/]+', cells[2]) if x.strip()])
        trigger_count = len([x for x in re.split(r'[；;]+', cells[3]) if x.strip()])
        if len(cells[1]) < 35:
            raise SystemExit(f'{skill}: navigation overview too short: {line}')
        if keyword_count < 6:
            raise SystemExit(f'{skill}: navigation keywords too few: {line}')
        if cells[3] == '默认读取':
            raise SystemExit(f'{skill}: navigation trigger too vague: {line}')
        if cells[0] != '1' and trigger_count < 2:
            raise SystemExit(f'{skill}: navigation triggers too few: {line}')
print('navigation ok')
PY
```

## README 与 docs 对照

```bash
python3 - <<'PY'
from pathlib import Path
import re

readme = Path('README.md').read_text(encoding='utf-8')
docs = Path('docs/index.html').read_text(encoding='utf-8')
skills = sorted(p.name for p in Path('.').iterdir() if p.is_dir() and (p / 'SKILL.md').exists())
readme_names = re.findall(r"^\| `([^`]+)` \|", readme, flags=re.M)
doc_names = re.findall(r"name:\s*['\"]([^'\"]+)['\"]", docs)

missing_readme = [s for s in skills if s not in readme_names]
missing_docs = [s for s in skills if s not in doc_names]
extra_readme = sorted(set(readme_names) - set(skills))
extra_docs = sorted(set(doc_names) - set(skills))
readme_order_ok = readme_names == skills
docs_order_ok = doc_names == skills

print('skill files:', len(skills))
print('README entries:', len(readme_names))
print('docs entries:', len(doc_names))
print('missing README:', missing_readme)
print('missing docs:', missing_docs)
print('extra README:', extra_readme)
print('extra docs:', extra_docs)
print('README order ok:', readme_order_ok)
print('docs order ok:', docs_order_ok)
if missing_readme or missing_docs or extra_readme or extra_docs or not readme_order_ok or not docs_order_ok:
    raise SystemExit(1)
PY
```

## docs/index.html JS 检查

修改 HTML 内联 JS 后，提取 `<script>` 内容运行 `node --check`。如果已有项目脚本能做同等检查，优先沿用现有方式。

## 网页 UI 回归检查

- 删除正文图标、移动资源或重命名文件后，检查资源引用仍然有效，特别是 favicon、图片、CSS、脚本路径。
- 改 UI 文案后用搜索确认旧文案没有残留。
- 改筛选控件后搜索确认旧实现没有残留，例如 `<select>`、旧 id、旧 class 或旧单选逻辑。
- 改布局后检查桌面和移动端 media query，不要只看桌面 CSS。
- 改渐隐、mask、固定表头后，检查默认第一条内容是否被切掉，滚动时是否自然消失，表头文字是否始终清晰。
- 如果能启动或打开页面，应实际检查：弹层是否超出视口、滚动区域是否正确、按钮字体是否一致、主题/背景颜色切换是否仍有效。

## Git 基础规则

- 编辑前先查看 `git status --short`。
- 保留无关的用户改动，不要回滚任务外文件。
- 改动保持最小、聚焦、可解释。
- 提交或推送前运行 `git diff --check`。
- 用户没有明确要求时，不要 commit 或 push。
- 最终回复前确认工作区状态。

## Dirty Worktree

- 可能存在用户未提交改动。
- 如果无关，忽略它们。
- 如果会影响当前任务，先读清楚并与这些改动共存。
- 不要用 destructive command 回滚用户改动。

## 拆分、移动和重命名

- 拆分、移动或重命名文件后，必须检查旧路径引用是否已更新、内容是否丢失。
- 删除旧文件前确认内容已迁移或确实不再需要。
- 新增文件后确认它能从主 `SKILL.md`、`AGENTS.md` 或其他入口追溯。

## Commit 和 Push

- 用户没有明确要求时，不要 commit 或 push。
- 用户要求 push 前，先运行必要检查。
- push 前说明关键检查结果。
- 如果检查失败，先修复；无法修复时说明阻塞点，不要带问题 push。
