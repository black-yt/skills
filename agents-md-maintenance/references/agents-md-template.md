# AGENTS.md 维护模板

## 目标

`AGENTS.md` 是 AI agent 在仓库中工作的常驻操作指南。它应该提供足够共享上下文，让 agent 能安全、正确地开始工作，同时不要消耗过多上下文窗口。

它不负责保存所有历史细节。它负责保存必要项目背景、硬规则、危险边界和更深本地指南的入口。

## 推荐目录

```text
AGENTS.md
AGENTS.local/
  README.md
  00_project_overview.md
  01_repository_layout.md
  02_core_workflows.md
  03_data_formats.md
  04_common_pitfalls.md
  05_development_commands.md
  06_git_and_release.md
  07_long_term_notes.md
```

`AGENTS.md` 是简洁入口。

`AGENTS.local/` 存放详细规则、长工作流、历史经验、命令示例和项目特定维护笔记。

## AGENTS.md 模板

```md
# [REPOSITORY_NAME] 的 AGENTS.md 指南

## 项目概览

- [用一段话说明这个仓库做什么。]
- [说明主要用户、运行方式、部署目标或产物类型。]
- [说明 agent 最需要保护或避免破坏的东西。]

## 仓库结构

- `[path]/`：[职责和所有权边界。]
- `[path]/`：[职责和所有权边界。]
- `[path]/`：[生成物、禁止编辑范围或安全编辑规则。]

## 安全规则

- 不要提交 secrets、tokens、credentials、私有服务 URL 或本地机器路径。
- 不要覆盖用户改动或生成产物，除非任务明确要求。
- 未经明确同意，不要修改共享环境、生产配置或长期运行服务。
- [项目特定硬规则。]

## 编辑规则

- 优先做小而聚焦的改动。
- 除非有明确理由，否则保留已有约定。
- 保持生成文件、源码和文档的边界清晰。
- 如果规则变化，更新所有引用旧规则的位置。

## 构建与测试

- [主要测试命令。]
- [lint、typecheck 或 build 命令。]
- [测试昂贵时的 smoke test。]
- [测试无法运行时的处理方式。]

## Git 规则

- 编辑前和最终回复前检查 `git status --short`。
- 不要回滚无关的用户改动。
- 只有用户明确要求时才 commit 或 push。
- commit 或 push 前运行 `git diff --check`。

## 深入指南

- 大型架构改动前读取 `AGENTS.local/00_project_overview.md`。
- 修改 [workflow] 前读取 `AGENTS.local/02_core_workflows.md`。
- 触碰 [risky subsystem] 前读取 `AGENTS.local/04_common_pitfalls.md`。
- 做 release 工作前读取 `AGENTS.local/06_git_and_release.md`。

## 指令优先级

1. 安全和数据完整性规则。
2. 仓库特定约束。
3. 构建、测试和验证要求。
4. 工作流偏好。
5. 历史 notes。
```

## AGENTS.local/README.md 模板

```md
# AGENTS.local

这个目录存放面向 agent 的详细仓库维护笔记。

按任务选择性阅读：

- `00_project_overview.md`：项目目的和架构。
- `01_repository_layout.md`：目录所有权和生成文件。
- `02_core_workflows.md`：常见开发和维护工作流。
- `03_data_formats.md`：输入/输出 schema 和校验期望。
- `04_common_pitfalls.md`：已知失败模式和排错历史。
- `05_development_commands.md`：完整命令示例。
- `06_git_and_release.md`：release、branch、commit 和 publish 流程。
- `07_long_term_notes.md`：不是每轮都需要的长期上下文。

除非这个目录明确是私有且 ignored，否则不要放 secrets 或 credentials。
```

## 拆分流程

当原 `AGENTS.md` 太长时，按下面流程拆分：

1. 备份当前内容。
2. 创建 `AGENTS.local/`。
3. 按主题移动内容，优先保持原句不变。
4. 用中等长度的新 `AGENTS.md` 替换原文件。
5. 在新 `AGENTS.md` 中写清楚每个 local 文件的读取时机。
6. 搜索旧标题和旧路径引用，确认没有断链。
7. 根据公开/私有策略更新 `.gitignore`。
8. 运行 diff 检查，确认信息是迁移不是删除。

可选完整性检查：

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib

files = [
    "00_project_overview.md",
    "01_repository_layout.md",
    "02_core_workflows.md",
    "03_data_formats.md",
    "04_common_pitfalls.md",
    "05_development_commands.md",
    "06_git_and_release.md",
    "07_long_term_notes.md",
]

text = "".join((Path("AGENTS.local") / f).read_text(encoding="utf-8") for f in files)
print("lines:", len(text.splitlines()))
print("sha256:", hashlib.sha256(text.encode("utf-8")).hexdigest())
PY
```

这个脚本只验证拆分后的文件集合是否稳定，不能替代人工检查语义和引用。

## `.gitignore` 策略模板

公开仓库通常忽略 agent 指南：

```gitignore
AGENTS.md
AGENTS.local/
```

私有仓库可跟踪 `AGENTS.md`。如果 `AGENTS.local/` 包含私有路径、内部命令、部署细节、机器状态或凭据，仍应忽略：

```gitignore
AGENTS.local/
```

## Size Guidance

- `AGENTS.md`：建议 `80-200` 行。
- 每个 `AGENTS.local/*.md`：按主题聚焦。
- 如果 local guide 继续变大，再拆分，不要形成一个新的超长文件。

## 最终判断

- `AGENTS.md` 应回答：“agent 在触碰仓库前必须知道什么？”
- `AGENTS.local/` 应回答：“agent 在做某类具体工作前应该读什么？”
