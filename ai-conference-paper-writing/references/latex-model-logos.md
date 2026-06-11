# Latex Model Logos

### 模型或系统图标

只有 logo 文件确实存在且图标能提升可读性时才用；否则保持纯文本模型名。复制到新论文时，请把示例宏名和 logo 路径改成当前项目自己的命名。

本 skill 已保存一组常用模型 logo，可从 `assets/logos/models/` 复制到论文工程，例如放到 `figures/logos/models/`：

- `anthropic.png`
- `deepseek.png`
- `gemini.png`
- `glm.png`
- `grok.png`
- `kimi.png`
- `mimo.png`
- `minimax.png`
- `openai.png`
- `qwen.png`

模型结果表、leaderboard 表、消融对比表中，模型名前建议加对应 provider logo，提升扫读性。不要在每个 cell 里重复 logo，只在第一列模型名处加；如果同一个系统由多个模型组成，只给主模型或系统入口加一个 logo。

推荐写法：

```latex
\newcommand{\ModelLogo}[1]{\raisebox{-1.5pt}{\includegraphics[height=1.05em]{figures/logos/models/#1.png}}\hspace{0.28em}}
\newcommand{\OpenAIModel}[1]{\ModelLogo{openai}#1}
\newcommand{\AnthropicModel}[1]{\ModelLogo{anthropic}#1}
\newcommand{\GeminiModel}[1]{\ModelLogo{gemini}#1}
\newcommand{\GrokModel}[1]{\ModelLogo{grok}#1}
\newcommand{\QwenModel}[1]{\ModelLogo{qwen}#1}
\newcommand{\GLMModel}[1]{\ModelLogo{glm}#1}
\newcommand{\KimiModel}[1]{\ModelLogo{kimi}#1}
\newcommand{\MiMoModel}[1]{\ModelLogo{mimo}#1}
\newcommand{\MiniMaxModel}[1]{\ModelLogo{minimax}#1}
\newcommand{\DeepSeekModel}[1]{\ModelLogo{deepseek}#1}
```

如果需要把引用紧跟模型名，可以额外定义 citation helper；这要求论文模板支持 `natbib` 的 `\citealp`，否则改成当前模板使用的 citation 命令。

```latex
\newcommand{\ModelRef}[1]{\textsuperscript{\citealp{#1}}}
```

表格示例：

```latex
\begin{table}[t]
\centering
\caption{\textbf{Main results on [Benchmark].} Higher is better.}
\label{tab:main-results-with-logos}
\begingroup
\scriptsize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.08}
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}lccc@{}}
\toprule
Model & Overall & Level 1 & Level 2 \\
\midrule
\GeminiModel{Gemini 3.1 Pro}\ModelRef{google_gemini_models} & \BestScore{82}{82.1} & \ScoreCell{78}{78.4} & \BestScore{84}{84.0} \\
\OpenAIModel{GPT-5.5}\ModelRef{openai_models} & \SecondScore{79}{78.6} & \BestScore{80}{80.2} & \ScoreCell{77}{76.9} \\
\QwenModel{Qwen3.6-35B-A3B}\ModelRef{qwen_models} & \ScoreCell{72}{72.3} & \SecondScore{79}{79.1} & \SecondScore{77}{77.2} \\
\DeepSeekModel{DeepSeek V4 Pro}\ModelRef{deepseek_models} & \ScoreCell{68}{67.8} & \ScoreCell{70}{70.0} & \ScoreCell{66}{66.4} \\
\bottomrule
\end{tabular}%
}
\endgroup
\end{table}
```

使用规则：

- 模型表第一列使用 `\OpenAIModel{...}`、`\QwenModel{...}` 这类宏，不要手动在每行写 `\includegraphics`。
- logo 高度通常用 `0.9em-1.1em`，以文字基线自然对齐为准；`raisebox` 可以按模板微调。
- 宏里的图片路径必须和论文工程实际路径一致，例如 `figures/logos/models/#1.png` 或 `imgs/logos/models/#1.png`。
- 如果 logo 在压缩后的表格中显得拥挤，优先略调 `\tabcolsep` 或 logo 高度，不要删除模型名或改实验数字。
- 这些 logo 只服务可读性，不替代 citation；模型名附近仍应有对应真实引用。

更通用的系统图标写法如下。适合 agent/system 表或自定义 logo 较多的表；只有对应 logo 文件真实存在时才定义宏。

```latex
\newcommand{\CustomIcon}[1]{\raisebox{-0.12em}{\includegraphics[height=0.9em]{imgs/logos/#1.png}}\hspace{0.25em}}
\newcommand{\ClaudeIcon}{\CustomIcon{anthropic}}
\newcommand{\OpenAIIcon}{\CustomIcon{openai}}
\newcommand{\ArisIcon}{\CustomIcon{asx}}
\newcommand{\OpenClawIcon}{\CustomIcon{openclaw}}
\newcommand{\NanobotIcon}{\CustomIcon{nanobot}}
\newcommand{\EvoIcon}{\CustomIcon{evo}}
\newcommand{\ResearchClawIcon}{\CustomIcon{researchclaw}}
\newcommand{\GlmIcon}{\CustomIcon{glm}}
\newcommand{\GeminiIcon}{\CustomIcon{gemini}}
\newcommand{\DeepSeekIcon}{\CustomIcon{deepseek}}
\newcommand{\GrokIcon}{\CustomIcon{grok}}
\newcommand{\KimiIcon}{\CustomIcon{kimi}}
\newcommand{\MimoIcon}{\CustomIcon{mimo}}
\newcommand{\QwenIcon}{\CustomIcon{qwen}}
```
