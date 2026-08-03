---
name: agents-md-maintenance
description: "当需要创建、整理、拆分或维护仓库中的 AGENTS.md、CLAUDE.md 或同类默认加载 agent 操作指南时使用；覆盖常驻上下文边界、*.local/ 按需拆分、公开/私有跟踪策略、同步校验和安全编辑。"
---

# AGENTS.md 维护

## 核心原则

- `AGENTS.md` 是 agent 每次进入仓库时都会读取的操作指南，不是历史记录仓库。
- 目标是提供足够共享上下文，让 agent 在不浪费上下文窗口的情况下，知道“动手前必须知道什么”。
- 长流程、历史经验、大命令块、环境细节和低频说明放入 `AGENTS.local/` 或其他 topic docs。
- 公开仓库中不要写入 secrets、真实凭据、私有路径、内部主机、私有服务地址或个人本地状态。
- 编辑时保留已有硬规则；如果规则过时，要明确迁移或替换，不要静默删除。
- 每个对话都应该默认知道的项目背景、总览、硬规则和安全边界必须直接写在 `AGENTS.md`，不要拆成 `AGENTS.local/` 中的单独 overview 文件。
- 主 `AGENTS.md` 必须提供整个项目或工作空间的全局描述，让 agent 能从整体角度理解这个仓库是做什么的、核心目标是什么、主要结构如何组织、关键产物和维护边界是什么。

## 适用范围

- 这个 skill 主要面向 Codex 这类会自动加载 `AGENTS.md` 的智能体操作指南。
- 其他智能体可能使用不同入口文件名，例如 Claude Code 常用 `CLAUDE.md`；文件名不同，但维护逻辑相同。
- 维护非 `AGENTS.md` 入口时，把规则中的 `AGENTS.md` / `AGENTS.local/` 等价替换为对应文件和目录，例如 `CLAUDE.md` / `CLAUDE.local/`。
- 核心目标不是固定文件名，而是在默认加载的入口文件中提供足够全局上下文和硬规则，同时把低频细节拆到 local 目录按需读取，避免默认加载文档浪费上下文窗口。
- 如果采用 `CLAUDE.md`、`CLAUDE.local/` 或其他同类命名，也要同步维护 `.gitignore`、canonical copy、导航表和文件路径引用。

## 推荐结构

优先采用两层结构，但 `AGENTS.local/` 下的文件不要写死。拆分应由项目实际内容决定，不要套固定模板。

```text
AGENTS.md
AGENTS.local/
  01_<detailed-topic>.md
  02_<detailed-topic>.md
  ...
```

如果入口文件不是 `AGENTS.md`，保持同样结构语义，只替换文件名：

```text
CLAUDE.md
CLAUDE.local/
  01_<detailed-topic>.md
  02_<detailed-topic>.md
  ...
```

- `AGENTS.md`：中等长度入口，放必须常驻的规则和索引。
- `AGENTS.local/`：详细规则、长工作流、历史教训、命令示例和项目维护笔记。
- `AGENTS.local/` 应该是一组平行的细节章节，不应该包含“总览”“项目概览”这类默认上下文文件。
- 示例中的 `...` 表示按项目实际内容增减文件；不要让模型误以为只能按示例数量或示例命名拆分。
- 复制示例到真实 `AGENTS.md` 时，必须把 `...` 替换成真实文件行或删除，不要把省略行当成实际导航项。
- `AGENTS.local/` 的拆分目标是把语义相同或相近的章节放在一起，并降低常驻上下文压力；不是为了追求固定文件数或固定命名。
- 不要拆得很碎。只有当内容明显属于不同任务场景、单文件过长、或会导致模型上下文压力时，才拆成多个文件。
- 同一项目可以只有 1-3 个 `AGENTS.local/` 文件；复杂项目可以更多，但每个文件都应有清晰语义边界。
- `AGENTS.local/` 的文件导航必须写在 `AGENTS.md` 里，不要依赖 `AGENTS.local/README.md`；因为 `AGENTS.md` 会被自动加载，agent 应该一开始就知道什么时候读哪个详细文件。
- `AGENTS.md` 中导航 `AGENTS.local/` 文件时必须使用表格，列为：`序号 / 文件内容概览 / 关键词 / 触发时机 / 文件路径`，其中 `文件路径` 放在最后一列。
- `文件内容概览`、`关键词` 和 `触发时机` 都必须非常具体。目标是让 agent 不打开文件也能判断“是否必须读这个文件”，避免靠猜测、反复 `ls` 或反复打开文件寻找。
- `文件内容概览` 必须写清实际覆盖的模块、文件名、命令、边界和排除项；不要只写“项目概览”“工作流”“命令示例”这类粗略标签。
- `关键词` 和 `触发时机` 要覆盖足够多的真实检索词和任务场景；过少会导致模型查阅低效。
- 如果仓库已经有等价目录命名，优先沿用现有约定，不强行重命名。

## 文件导航表写法

`AGENTS.md` 中的 `AGENTS.local/` 导航表必须让 agent 一眼知道“该读哪个文件、为什么读、何时必须读”，不能让 agent 靠猜测、反复 `ls`、反复打开文件来定位信息。

表头固定为：

```md
| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
```

各列写法：

- **序号。** 使用稳定整数，按推荐阅读顺序排列；不要用字母、emoji 或会频繁变化的优先级标签。表格序号要和文件名前缀一致，例如表格写 `01`，文件名也用 `01_...`。
- **文件内容概览。** 写 1-2 个具体短句，说明这个文件实际包含什么、解决什么边界问题、涉及哪些关键文件/命令/系统，以及不覆盖什么；不要只写“项目概览”“工作流”“详细说明”。
- **关键词。** 写足够多的检索词，通常至少 6-12 项；包含同义词、命令名、文件名、目录名、库名、错误类型、任务阶段和风险词。关键词用逗号分隔，不要替代内容概览。
- **触发时机。** 写多个具体条件，通常至少 3 个；优先使用“修改 X 前必须读取”“运行 Y 前必须读取”“排查 Z 时必须读取”“同步 A 到 B 前必须读取”；用分号分隔，避免只写“需要时读取”“默认读取”或过宽泛的描述。
- **文件路径。** 使用相对路径，放最后一列，并用反引号包住；移动、重命名或拆分文件后必须同步更新路径。

最小示例。这个示例只展示表格写法，不要求所有项目都使用这些文件名：

```md
| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 解释仓库源码、生成物、配置、数据、文档和静态资源目录的职责边界，并标明哪些路径可以改、哪些路径只能读、哪些路径由工具生成不能手写。 | layout、ownership、generated files、do-not-edit、config、data、docs、assets、scripts、build output、resource path、path safety | 新增/移动/删除目录前；修改资源路径前；编辑生成物前；调整构建产物位置前；不确定某个路径是否可改时必须读取 | `AGENTS.local/01_repository_layout_and_boundaries.md` |
| 02 | 记录开发、测试、构建、发布、回滚和排错的项目级流程，包含常用命令、执行顺序、前置条件、失败处理和哪些命令不能直接运行。 | workflows、commands、test、lint、build、release、rollback、CI、debug、dry-run、pitfalls、failure handling | 执行多步维护前；运行复杂命令前；发布/回滚前；修 CI 或测试失败前；排查环境、依赖、权限或构建异常前必须读取 | `AGENTS.local/02_workflows_validation_and_release.md` |
| ... | 按项目实际语义继续增减，不要为了凑固定数量而拆分。 | ... | ... | `AGENTS.local/...` |
```

## AGENTS.md 应该包含

- 项目或工作空间的整体描述：这个仓库做什么、服务谁、核心目标是什么、主要产物是什么。
- 主要结构的全局说明：核心目录、关键文件、展示层、生成物、配置和外部资源各自承担什么职责。
- 主要目录、服务、子系统及职责边界。
- 高优先级安全规则和数据完整性规则。
- 不能误改的文件、目录、生成物或外部资源。
- Git、commit、push、release 规则。
- 测试、构建、lint、验证期望。
- 子系统边界和交互限制。
- 以表格写清楚什么时候读取 `AGENTS.local/` 中的每个详细文件。
- 指向详细文档的短链接，而不是复制完整内容。

推荐长度：约 `80-200` 行。太短容易漏规则，太长会挤占任务上下文。

如果维护过程中发现主 `AGENTS.md` 明显超过推荐长度、开始挤占上下文或难以扫描，应主动询问用户是否需要进一步拆分。不要因为入口变长就直接删减规则；优先把低频细节无损迁移到已有 `AGENTS.local/` topic 文件，或在确有必要时新增语义边界清晰的 topic 文件。

## AGENTS.md 不应该包含

- 长历史 incident log。
- 大段命令块和完整迁移流程。
- 一次性 debug 记录。
- 低频 API 细节。
- benchmark、模型、部署的完整配置。
- README 内容的重复副本。
- secrets、key、token、credential。
- 本机端口、私有 endpoint、真实运行 key 名称组合、临时模型服务状态等低频本地配置。
- 临时本地文件、个人机器状态或未确认可公开的信息。

这些内容应迁移到 `AGENTS.local/` 的 topic 文件，或放入私有 context 文档。

## AGENTS.local/ 应该包含

- 完整开发工作流。
- import/export、部署、release、CI 等细节流程。
- 大命令示例和可复制脚本片段。
- 数据格式文档。
- 常见坑、排错历史和长期维护笔记。
- 只在特定任务中需要读取的环境说明。

判断规则：如果一条说明不是每个会话都必须知道，就优先放到 `AGENTS.local/`。

反向判断：如果一条说明是 agent 每次进入仓库都应该默认知道的背景、硬规则、安全边界或总览，就必须留在 `AGENTS.md`，即使它会让 `AGENTS.md` 略微变长。

拆分规则：

- **主动询问。** 当主入口持续变长、明显超过推荐长度或开始影响阅读效率时，先询问用户是否需要拆分；未经用户明确同意，不要自动做大规模迁移。
- **信息无损。** 拆分是移动和重组，不是压缩或删减。迁移到 `AGENTS.local/` 的内容必须保留原有约束、命令、失败处理、示例和边界条件。
- **按语义合并。** 目录职责和生成物边界通常可以放一起；开发流程和验证命令通常可以放一起；风险、排错和历史教训通常可以放一起。
- **按触发场景拆分。** 如果两个章节总是被同一类任务同时读取，就不要拆成两个文件。
- **按上下文压力拆分。** 只有当文件过长、模板太多、命令块太大或任务场景明显不同，才拆出新文件。
- **避免碎片化。** 不要为了对应固定编号创建很多几十行的小文件；每个文件都应该值得被单独读取。
- **禁止二级总览。** 不要创建 `overview.md`、`project_overview.md`、`scope.md` 这类只是承载默认背景的 local 文件；这些内容应在 `AGENTS.md` 中默认加载。
- **导航表不缩水。** 主入口中的 `AGENTS.local/` 导航表一般不应减少内容或迁移到 local 文件，因为它决定 agent 的检索效率。拆分后仍要保留具体的文件内容概览、关键词、触发时机和路径；可以迁移正文细节，但不要把导航信息挪走导致 agent 找不到该读什么。

## Git 跟踪策略

- **公开仓库。** 通常建议 `.gitignore` 中忽略 `AGENTS.md` 和 `AGENTS.local/`，并在私有 context 仓库、内部文档或安全知识库中维护 canonical copy。
- **私有仓库。** 默认跟踪 `AGENTS.md` 和 `AGENTS.local/`，这样团队 agent 能共享同一套维护规则。
- **例外情况。** 如果用户明确要求忽略，或 `AGENTS.local/` 含私有机器路径、内部命令、部署细节、凭据、token、临时本地状态等不应入库内容，再把对应文件或目录加入 `.gitignore`。
- 如果项目仓库中的 agent 指南被忽略，必须有别处作为 source of truth，不能只存在某个开发者本地工作树。

## Canonical Copy 同步

- 如果 `AGENTS.md` 或 `AGENTS.local/` 被主仓库 ignore，修改完成后只能报告需要同步 canonical copy。
- 除非用户明确要求“同步 canonical copy / commit / push”，否则不要自动写入、提交或推送 canonical 仓库。
- 同步前必须先确认目标路径、列出将写入的文件，并用 `diff`、`rsync --dry-run` 或等价检查确认写入范围正确。
- 同步前必须确认不会把 `AGENTS.local/` 文件误写到上级目录、错误仓库或错误分支。

`rsync` 适合把 ignored 的 `AGENTS.md` 和 `AGENTS.local/` 增量同步到 canonical copy，但必须先 dry-run。源路径末尾斜杠含义不同：

- `AGENTS.local`：复制整个目录本身，目标下会出现 `AGENTS.local/`。
- `AGENTS.local/`：复制目录里面的内容，适合同步到已存在的 `DEST/AGENTS.local/`。

推荐流程：

```bash
# 同步单个入口文件
rsync -a --dry-run AGENTS.md [CANONICAL_ROOT]/[REPO_NAME]/AGENTS.md
rsync -a AGENTS.md [CANONICAL_ROOT]/[REPO_NAME]/AGENTS.md

# 同步 AGENTS.local 目录内容，先预演再执行
rsync -a --delete --dry-run AGENTS.local/ [CANONICAL_ROOT]/[REPO_NAME]/AGENTS.local/
rsync -a --delete AGENTS.local/ [CANONICAL_ROOT]/[REPO_NAME]/AGENTS.local/
```

安全规则：

- 使用 `--delete` 前必须先跑 `--dry-run`。
- 先确认 `[CANONICAL_ROOT]`、`[REPO_NAME]` 和目标目录都正确，再去掉 `--dry-run`。
- 需要显示过程时加 `-v`；大目录可加 `-P`；需要排除缓存时用 `--exclude '__pycache__/' --exclude '*.pyc'`。
- 不要把 `AGENTS.local/` 同步到 canonical 根目录本身，除非目标就是专门为该仓库准备的目录。

## 编辑工作流

1. 先读现有 `AGENTS.md`、`.gitignore` 和已存在的 `AGENTS.local/` topic 文件。
2. 判断改动属于常驻规则还是低频细节。
3. 常驻规则写入 `AGENTS.md`，保持短句和稳定标题。
4. 长解释、命令、历史记录写入 `AGENTS.local/` 对应 topic。
5. 如果规则改名或迁移，更新所有旧引用。
6. 检查没有 secrets、真实凭据和不应公开的本地环境信息。
7. 运行 `git diff --check`，并按仓库规则做必要测试。
8. 如果指南是 ignored 文件，只报告 canonical copy 需要同步；同步、commit 或 push 必须等用户明确授权。

## 拆分过大的 AGENTS.md

当 `AGENTS.md` 过长、难导航或包含大量低频细节时：

0. 先询问用户是否需要拆分，并说明计划移动哪些低频内容、保留哪些常驻规则。
1. 创建 `AGENTS.local/`。
2. 按项目实际语义拆出少量 Markdown 文件，把相近章节放在一起。
3. 用中等长度入口替换原 `AGENTS.md`。
4. 确保原有信息没有丢失，只是迁移。
5. 在 `AGENTS.md` 中保留或添加完整索引和每个详细文件的读取时机；导航表列为 `序号 / 文件内容概览 / 关键词 / 触发时机 / 文件路径`，且后三列必须足够具体，不能让 agent 靠猜。一般不要为了缩短主入口而精简导航表，尤其不能删掉关键词和触发时机。
6. 按公开/私有策略更新 `.gitignore`。

拆分后必须做结构审计：

- `AGENTS.local/` 文件是否从 `01_` 开始编号，且表格序号与文件名前缀一致。
- 拆分是否经过用户确认；迁移是否信息无损，没有把规则、命令、示例或失败处理压缩丢失。
- 是否没有 `00_`、`overview`、`project_overview`、`scope`、`README.md` 这类二级总览文件。
- 导航表列是否为 `序号 / 文件内容概览 / 关键词 / 触发时机 / 文件路径`。
- `文件内容概览` 是否具体说明文件里的真实内容、关键文件/命令/边界和不覆盖项。
- `关键词` 是否包含足够多的同义词、命令名、目录名、错误类型和任务场景，而不是 2-3 个泛词。
- `触发时机` 是否写成多个“修改/运行/排查/同步 X 前必须读取”这类可执行条件。
- 导航表是否仍保留在主入口中，且没有因为拆分而减少内容、降低检索效率或迁移到 local 文件。
- `AGENTS.md` 行数是否大致在 `80-200` 行；超出时要判断是否仍然属于常驻上下文。
- `git diff --check` 是否通过。

## AGENTS.md 模板

```md
# [REPOSITORY_NAME] 的 AGENTS.md 指南

## 项目概览

- [用一段话说明这个项目或工作空间做什么、服务谁、核心目标是什么。]
- [说明主要产物、运行方式、部署目标、数据/模型/文档等关键对象。]
- [说明主要目录和子系统如何组织，以及 agent 最需要保护或避免破坏的东西。]

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

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 解释仓库源码、生成物、配置、数据、文档和静态资源目录的职责边界，并标明哪些路径可以改、哪些路径只能读、哪些路径由工具生成不能手写。 | layout、ownership、generated files、do-not-edit、config、data、docs、assets、scripts、build output、resource path、path safety | 新增/移动/删除目录前；修改资源路径前；编辑生成物前；调整构建产物位置前；不确定某个路径是否可改时必须读取 | `AGENTS.local/01_repository_layout_and_boundaries.md` |
| 02 | 记录开发、测试、构建、发布、回滚和排错的项目级流程，包含常用命令、执行顺序、前置条件、失败处理和哪些命令不能直接运行。 | workflows、commands、test、lint、build、release、rollback、CI、debug、dry-run、pitfalls、failure handling | 执行多步维护前；运行复杂命令前；发布/回滚前；修 CI 或测试失败前；排查环境、依赖、权限或构建异常前必须读取 | `AGENTS.local/02_workflows_validation_and_release.md` |
| ... | 按项目实际语义继续增减，不要为了凑固定数量而拆分。 | ... | ... | `AGENTS.local/...` |

如果某个文件不存在，不要假设其内容；按当前任务需要创建或更新，并保持 `AGENTS.md` 中的索引同步。

## 指令优先级

1. 安全和数据完整性规则。
2. 仓库特定约束。
3. 构建、测试和验证要求。
4. 工作流偏好。
5. 历史 notes。
```

## 拆分校验

拆分大文件时，先确认内容是迁移而不是删除。可用下面脚本检查拆分后的文件集合是否稳定。`files` 列表必须按当前项目实际拆分结果填写，不要照抄示例文件名：

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib

files = [
    "01_repository_layout_and_boundaries.md",
    "02_workflows_validation_and_release.md",
    # ...
]

text = "".join((Path("AGENTS.local") / f).read_text(encoding="utf-8") for f in files)
print("lines:", len(text.splitlines()))
print("sha256:", hashlib.sha256(text.encode("utf-8")).hexdigest())
PY
```

这个脚本不能替代人工检查语义、标题和引用，只用于确认拆分文件集合没有意外变化。

## 优先级规则

`AGENTS.md` 中应明确 instruction priority：

1. 安全和数据完整性。
2. 仓库特定约束。
3. 构建、测试、验证要求。
4. 工作流偏好。
5. 历史 notes。

agent 遇到冲突时，应优先遵守高优先级规则。

## Review 清单

- `AGENTS.md` 回答了“动手前必须知道什么”。
- `AGENTS.md` 提供了项目或工作空间的全局描述，能让 agent 理解项目目标、主要结构、关键产物和维护边界。
- `AGENTS.local/` 回答了“做某类任务前还应读什么”。
- 导航表的 `文件内容概览 / 关键词 / 触发时机` 足够具体，模型不需要靠猜测或反复打开文件定位信息。
- 没有把低频细节塞进常驻上下文。
- 没有丢失已有硬规则或历史教训。
- 没有 secrets、真实凭据、私有路径或未确认可公开的信息。
- 公开/私有仓库的 Git 跟踪策略明确。
- ignored 指南有 canonical copy 和同步说明。
- ignored 指南没有在用户授权前被自动同步、commit 或 push。
- 标题稳定、层级不深、规则可扫描。
- `git diff --check` 通过。
