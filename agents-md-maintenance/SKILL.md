---
name: agents-md-maintenance
description: "当需要创建、整理、拆分或维护仓库中的 AGENTS.md 与 AGENTS.local/ agent 操作指南时使用；覆盖常驻上下文边界、公开/私有跟踪策略、拆分规则、同步校验和安全编辑。"
---

# AGENTS.md 维护

## 核心原则

- `AGENTS.md` 是 agent 每次进入仓库时都会读取的操作指南，不是历史记录仓库。
- 目标是让 agent 在不浪费上下文窗口的情况下，知道“动手前必须知道什么”。
- 长流程、历史经验、大命令块、环境细节和低频说明放入 `AGENTS.local/` 或其他 topic docs。
- 公开仓库中不要写入 secrets、真实凭据、私有路径、内部主机、私有服务地址或个人本地状态。
- 编辑时保留已有硬规则；如果规则过时，要明确迁移或替换，不要静默删除。

## 推荐结构

优先采用两层结构：

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

- `AGENTS.md`：中等长度入口，放必须常驻的规则和索引。
- `AGENTS.local/`：详细规则、长工作流、历史教训、命令示例和项目维护笔记。
- 如果仓库已经有等价目录命名，优先沿用现有约定，不强行重命名。

## AGENTS.md 应该包含

- 项目目的和一段式 overview。
- 主要目录、服务、子系统及职责边界。
- 高优先级安全规则和数据完整性规则。
- 不能误改的文件、目录、生成物或外部资源。
- Git、commit、push、release 规则。
- 测试、构建、lint、验证期望。
- 子系统边界和交互限制。
- 什么时候读取 `AGENTS.local/` 或其他更详细指南。
- 指向详细文档的短链接，而不是复制完整内容。

推荐长度：约 `80-200` 行。太短容易漏规则，太长会挤占任务上下文。

## AGENTS.md 不应该包含

- 长历史 incident log。
- 大段命令块和完整迁移流程。
- 一次性 debug 记录。
- 低频 API 细节。
- benchmark、模型、部署的完整配置。
- README 内容的重复副本。
- secrets、key、token、credential。
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

## Git 跟踪策略

- **公开仓库。** 通常建议 `.gitignore` 中忽略 `AGENTS.md` 和 `AGENTS.local/`，并在私有 context 仓库、内部文档或安全知识库中维护 canonical copy。
- **私有仓库。** 可以跟踪 `AGENTS.md`；如果 `AGENTS.local/` 含私有路径、内部命令、部署细节或本地状态，仍应保持 ignored。
- 如果项目仓库中的 agent 指南被忽略，必须有别处作为 source of truth，不能只存在某个开发者本地工作树。

## 编辑工作流

1. 先读现有 `AGENTS.md`、`.gitignore` 和相关 `AGENTS.local/README.md`。
2. 判断改动属于常驻规则还是低频细节。
3. 常驻规则写入 `AGENTS.md`，保持短句和稳定标题。
4. 长解释、命令、历史记录写入 `AGENTS.local/` 对应 topic。
5. 如果规则改名或迁移，更新所有旧引用。
6. 检查没有 secrets、真实凭据和不应公开的本地环境信息。
7. 运行 `git diff --check`，并按仓库规则做必要测试。
8. 如果指南是 ignored 文件，同步更新 canonical copy。

## 拆分过大的 AGENTS.md

当 `AGENTS.md` 过长、难导航或包含大量低频细节时：

1. 创建 `AGENTS.local/`。
2. 按主题拆出 Markdown 文件。
3. 用中等长度入口替换原 `AGENTS.md`。
4. 确保原有信息没有丢失，只是迁移。
5. 在 `AGENTS.md` 中添加索引和读取时机。
6. 按公开/私有策略更新 `.gitignore`。

完整模板和拆分校验脚本见 [references/agents-md-template.md](references/agents-md-template.md)。

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
- `AGENTS.local/` 回答了“做某类任务前还应读什么”。
- 没有把低频细节塞进常驻上下文。
- 没有丢失已有硬规则或历史教训。
- 没有 secrets、真实凭据、私有路径或未确认可公开的信息。
- 公开/私有仓库的 Git 跟踪策略明确。
- ignored 指南有 canonical copy 和同步说明。
- 标题稳定、层级不深、规则可扫描。
- `git diff --check` 通过。
