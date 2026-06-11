# Latex Layout And Contribution

### 版面微调与图表浮动

这一节用于最终 `.tex` 排版检查。此时默认正文、caption、图大小和表格内容已经确定；排版调整应尽量不改变论文 claim、文字内容、图表数值或图像尺寸。

段落末行规则：

- 每个段落最后一行尽量超过半行，避免只剩几个词或一个短短的 dangling line。
- 如果末行不足半行，优先通过轻微压缩到上一行解决，例如检查是否有冗余短语、重复限定词或可合并的表达。
- 如果不能自然压缩到上一行，可以适度补足一句必要解释，让段落超过一行，而不是留下很短的末行。
- 不要为了版面美观删除重要 claim、弱化证据或改变 technical meaning。
- 这类微调只适合最终 polish；在结构和论证未稳定前不要过早逐段抠末行。

图表溢出规则：

- 图、表、case box 或 algorithm 一旦超出正文边框、页边距或双栏范围，必须修排版，不能保留溢出版面。
- 若溢出是由浮动位置导致的，优先只调整位置，不改正文文字、不改 caption 内容、不改图大小、不改表格数值。
- 允许图表不紧贴首次提到它的文字；可以放到上一小节末尾、下一小节开头、页顶、页底或 float page，只要整体阅读顺序仍然自然。
- 只要正文中已经明确引用对应 figure/table，图表在前后相邻区域浮动是可以接受的。
- 可调整的对象是位置和浮动策略，例如 `figure`/`table` 的 `[t]`、`[b]`、`[p]`、`[!t]`，或把图表移到相邻段落之间。
- 不要用改文字、缩小图、压缩表格、删 caption 或删内容来掩盖溢出问题。
- 如果仅靠移动位置无法解决真实宽度溢出，停止并说明需要用户确认是否允许改图大小、表格排版或内容。

最终检查项：

- 图表外边界没有超出正文区域、页边距、单栏或双栏边界。
- 图表 caption 和正文引用顺序可读，没有让读者先看到很远之后才解释的图。
- 段落末行没有大量只剩 1-3 个词的短行。
- 版面调整没有改变实验数字、claim、caption 含义、图大小或表格内容。

### 紧凑贡献列表

当会议页数非常紧，Introduction 最后一段贡献列表需要压缩时，可以使用 `paralist` 的 `compactitem`。贡献仍然保持 3-5 点、名词开头、语法并列；不要因为压缩版式而把多个贡献塞进一个过长 bullet。

Preamble:

```latex
\usepackage{paralist}       % compactitem
```

正文模板：

```latex
\begin{compactitem}
\item \textbf{[Contribution 1 Name]}: [one-sentence contribution, focusing on task/data/method/evaluation rather than implementation details].
\item \textbf{[Contribution 2 Name]}: [one-sentence contribution with parallel grammar].
\item \textbf{[Contribution 3 Name]}: [one-sentence contribution that states the empirical finding or released resource].
\end{compactitem}
```

示例：

```latex
\begin{compactitem}
\item \textbf{ResearchClawBench}: 40 real scientific discovery tasks with expert-annotated rubrics across 10 domains and diverse scenarios.
\item \textbf{ResearchHarness}: a unified lightweight tool-use evaluation harness for LLM baselines.
\item \textbf{Unified evaluation}: a systematic assessment of seven autonomous research agents and eleven native LLM baselines, quantifying the gap between current AI research systems and target-paper-level re-discovery.
\end{compactitem}
```
