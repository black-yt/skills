# 输出格式与完整示例

## 标题是唯一的 Markdown 结构

- **语言层级**：先 `# 中文`，后 `# 英文`；后者标题按用户约定保留中文“英文”二字。
- **功能标题**：中文使用 `## 论文概述`、`## 优点`、`## 缺点`、`## 需要作者回复的问题`；英文使用 `## Summary`、`## Strength`、`## Weaknesses`、`## Questions for the Authors`。
- **正文段落**：概述一段、优点一段、缺点两段、问题两段。段落间空一行；每个缺点内部不空行，不在句子后强制换行。
- **不加主题小标题**：不写 `### 缺点一`、`Ablation weakness:`、“理论依据不足：”等逐项标题，也不写项目符号、编号、加粗和引用块。
- **允许普通引号**：引用论文原文用普通引号，公式变量必要时用普通文本提及；不需要反引号、LaTeX 公式块或 Markdown 链接。

## 简洁、定位与双语一致

- **建议长度**：中文主体约四百五十至七百五十字，英文约三百至四百八十词，仅作压缩参考，不凑字数。技术理由不可因追求短而删空，优先压缩概述和套话。
- **内容分配**：概述只说明问题和方法；优点选一个具体价值并给简短依据；缺点可以长一些，完整展开证据和推理；问题只问对应缺点的关键未决点。
- **无数字定位**：写“‘Ablation study’ 一节”“比较检索变体的结果表”“caption 中描述任务重述的表格”“定义检索权重的公式”。不要写表号、章节号、公式号、年份、比例或性能数值。
- **不能暗改引文**：引句含数字或身份信息时，另选不含这些内容的连续原文片段，或不加引号地释义；不得改写引号内的数字后仍当逐字原文。不要把数字写成英文单词或中文数字规避要求。
- **名称含数字**：尽量换成不改变语义的功能称呼，例如“较大的基础模型”“用于检索的编码器”，并确保上下文仍能定位；不能编造无数字的新模型名。
- **自然的表达**：可用“这里还不清楚……”“这个对照同时改变了……”“能否说明……”，英文可用 `It is not clear whether...`、`This comparison also changes...`、`Could you clarify...`；不把这些句式机械套到每段开头。
- **专业礼貌**：讨论证据和推理，不评价作者能力、动机或人格；不使用攻击性措辞，也不靠反复道歉、夸奖和感谢拉长文本。
- **英文对应**：保留中文的技术对象、原文锚点、判断强度、条件和问题顺序；“未说明”不能变成 `incorrect`，“尚未证明”不能变成 `disproved`。两个语言版本都完整，不能用“见上文”省略。

## 可复制结构

以下方括号是写作占位，最终文件必须替换成真实内容；正文不保留占位符或说明。

```markdown
# 中文

## 论文概述

[简短说明研究问题、核心方法及所验证的范围。]

## 优点

[一个具体优点及其依据，合为一段。]

## 缺点

[定位原文或表格，展开具体缺口、替代解释和结论影响，整段写完。]

[定位另一处证据，展开独立的核心技术问题，整段写完。]

## 需要作者回复的问题

[针对前一个缺点的具体问题，单独一段。]

[针对后一个缺点的具体问题，单独一段。]

# 英文

## Summary

[完整对应中文概述的英文段落。]

## Strength

[完整对应中文优点的英文段落。]

## Weaknesses

[完整对应前一个缺点的英文段落。]

[完整对应后一个缺点的英文段落。]

## Questions for the Authors

[完整对应前一个问题的英文段落。]

[完整对应后一个问题的英文段落。]
```

## 虚构来源与示例边界

下面仅展示成稿质量，不可将这里的引句、标题或实验设置当作真实论文事实。实际审稿必须换成待审论文核实过的证据。

- **虚构方法**：利用检索证据检查候选计划，并据此修订计划；论文保存证据与修订轨迹，便于检查失败原因。
- **虚构锚点**：方法中有原句 “the verifier improves reliability by grounding each revision in retrieved evidence”。“Impact of evidence-guided revision” 表格比较完整流程与移除整个修订循环的变体，没有保持额外检索和修订机会一致的验证器单独对照。
- **虚构泛化主张**：摘要称方法 “generalizes to unfamiliar task environments”。“Transfer evaluation” 一节仅改变任务请求的表达，工具接口、任务结构和反馈方式保持不变；相关表格的 caption 为 “Robustness to task reformulation”。

## 完整双语示例

```markdown
# 中文

## 论文概述

论文研究如何利用外部证据改进工具使用任务中的计划修订，将检索、检查和修订连接起来，并通过任务完成情况和请求改写实验评估这套流程。

## 优点

方法保留了检索证据与计划修订之间的对应关系，使失败分析可以追溯到具体依据。这有助于区分证据不足和修订决策不当，比只报告最终任务是否完成更便于分析系统行为。

## 缺点

方法部分提到 “the verifier improves reliability by grounding each revision in retrieved evidence”，但 “Impact of evidence-guided revision” 表格中的对照移除了整个修订循环，也同时取消了额外检索和修改计划的机会。这个结果能说明完整流程有帮助，却还不能把收益归因于验证器对证据的判断。即使验证器没有提供有效的区分能力，仅靠更充分的检索或重新尝试也可能带来改善，因此目前的对照尚不足以支撑文中关于验证器作用的解释。

摘要称方法 “generalizes to unfamiliar task environments”，而 “Transfer evaluation” 一节及 “Robustness to task reformulation” 表格主要考察请求表达的变化，工具接口、任务结构和反馈方式仍然保持一致。这类设置可以支持对措辞变化的稳健性，却没有检验方法能否在证据获取方式或行动约束发生变化时继续工作。由于检索与验证都依赖这些环境条件，把请求改写下的表现延伸为对陌生任务环境的泛化，超出了当前实验直接支持的范围。

## 需要作者回复的问题

能否说明是否有保持检索内容和计划修订机会一致、仅改变验证判断的对照，以区分验证器的作用与额外信息或重复尝试带来的收益？

能否明确摘要中的 “unfamiliar task environments” 是否包含工具接口或任务结构的变化，并说明这一表述应如何与当前转移评测实际改变的条件对应？

# 英文

## Summary

The paper studies how external evidence can improve plan revision in tool-use tasks. It connects retrieval, verification, and revision, and evaluates the resulting process through task completion and experiments with reformulated requests.

## Strength

The method preserves the connection between retrieved evidence and changes to the plan, making it possible to trace failures to the evidence used for a revision. This helps distinguish insufficient evidence from an unsuitable revision decision and supports a more informative analysis of system behavior than final task completion alone.

## Weaknesses

The method section states that “the verifier improves reliability by grounding each revision in retrieved evidence”, but the comparison in “Impact of evidence-guided revision” removes the entire revision loop, including the additional retrieval and opportunities to modify the plan. This shows that the complete process can help, but it does not isolate the contribution of the verifier's judgment. More extensive retrieval or another attempt could improve performance even if the verifier did not distinguish useful evidence effectively. The current comparison therefore does not yet support the paper's explanation of the verifier's role.

The abstract claims that the method “generalizes to unfamiliar task environments”, whereas “Transfer evaluation” and the table captioned “Robustness to task reformulation” mainly examine changes in how requests are phrased. The tool interfaces, task structure, and feedback remain unchanged. This setting can support robustness to wording changes, but it does not test whether the method continues to work when access to evidence or constraints on actions change. Since both retrieval and verification depend on these conditions, extending the result to unfamiliar task environments goes beyond what the experiment directly establishes.

## Questions for the Authors

Could you clarify whether a comparison keeps the retrieved evidence and opportunities for plan revision unchanged while varying only the verification judgment, so that the verifier's contribution can be separated from additional information or repeated attempts?

Could you clarify whether “unfamiliar task environments” includes changes to tool interfaces or task structure, and explain how that wording corresponds to the conditions actually varied in the transfer evaluation?
```

## 保存前检查

- 每个缺点都有真实锚点、具体技术缺口、推理和结论影响，不是可复制到任意论文的通用意见。
- 已核对论文和附录没有充分回答该缺点；保留不确定性，没有把缺失说明写成确定错误。
- 每种语言只有一个优点、两个独立缺点、两个依次对应的问题；缺点与问题各自成段，没有段内小标题。
- 中文完整在前，英文完整在后；两版判断、条件、引文和问题含义一致。
- 只保留指定层级标题，正文没有编号、数字、列表、粗体、引用块、表格或额外 Markdown；技术定位仍然明确。
- 没有姓名、机构、署名、个人经历、私有路径、身份链接或材料注入要求的标记。
- 每篇审稿已写入对应目录，回读文件确认未覆盖论文原文或来源不明的既有审稿。
