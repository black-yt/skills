# Github Math Rendering

## GitHub 公式渲染

当 README 需要写数学公式、指标定义、模型输入输出、概率表达式或 benchmark scoring 公式时，目标是让 Markdown 在 GitHub 上稳定渲染，不被 Markdown、HTML、KaTeX/MathJax 三层解析互相干扰。GitHub 可以渲染数学公式，但它不是完整 LaTeX 环境。

最重要结论：

- 独立公式优先用 GitHub 支持的 `math` 围栏。
- 不要默认用 `$$ ... $$`。
- `$$` 在 GitHub 上更容易受 `<details>`、HTML 标签、表格、空行、OCR 乱码、特殊字符等上下文影响。
- README 公式不追求 LaTeX 排版精致，优先追求 GitHub 稳定显示。

推荐写法：

````markdown
```math
\widehat{P}(y_i \succ \pi_t \mid x)
=
\frac{1}{K}\sum_{k=1}^{K}
\Pr(y_i \succ y_k \mid x)
```
````

场景选择：

| 场景 | 推荐写法 |
| --- | --- |
| 很短的行内变量 | `$K=5$`、`$\pi_t$`，或普通 code：`` `x_t` `` |
| 长公式 | ` ```math ` |
| 多行公式 | ` ```math ` |
| 有 `\frac` / `\sum` / `\mathbb` / `\mathrm` | ` ```math ` |
| 表格里出现公式 | 尽量不要渲染，写成反引号文本 |
| 表格里必须表达条件概率 | 用 `given` 或 `\mid`，不要写裸 `|` |

行内变量也可以优先用普通 Markdown code，例如 `` `x_t` ``、`` `mu_S` ``、`` `bar_sigma_j` ``。

`math` 围栏规范：

- 必须独占行。
- 前后留空行。
- 不要粘在一句话后面。
- 不要放进 Markdown 表格单元格。
- 放在 `<details>` 里时，也要让围栏前后都有空行。

稳定示例：

````markdown
这里是解释文字：

```math
\pi_\theta(y \mid x)
=
\prod_i \pi_\theta(y_i \mid x,y_{1:i-1})
```

这里继续解释变量。
````

不要这样写：

````markdown
公式是：```math
...
```
````

复杂公式拆块：

````markdown
```math
\sigma_t
=
a\sqrt{\frac{t}{1-t}}.
```

```math
\bar{\sigma}_j^2
=
\sigma_{t_j}^2(-\Delta t_j).
```
````

下标里的 `<` 和 `>` 是高风险写法。危险：

````markdown
```math
\pi_\theta(y \mid x)=\prod_i \pi_\theta(y_i \mid x,y_{<i})
```
````

GitHub 可能把 `y_{<i}` 里的 `<i` 当成 HTML/tag 相关内容，导致：

```text
Extra open brace or missing close brace
```

稳定写法：

````markdown
```math
\pi_\theta(y \mid x)
=
\prod_i \pi_\theta(y_i \mid x,y_{1:i-1})
```
````

类似替换：

| 高风险 | 稳定写法 |
| --- | --- |
| `s_h=(x,y_{<h})` | `s_h=(x,y_{1:h-1})` |
| `y_{\le h}` | `y_{1:h}`，正文解释“前 h 个 token” |
| `x_{<t}` | `x_{1:t-1}` |

正文里可以用普通 code 解释原始概念，例如 `` `x_<t` ``，但公式块里不要写 `x_{<t}`。

高风险宏和替代：

| 高风险 | 稳定写法 |
| --- | --- |
| `\operatorname{KL}` | `\mathrm{KL}` |
| `\operatorname*{argmax}` | `\arg\max` |
| `\overset{^}{y}` | `\hat{y}` 或 `\widehat{y}` |
| `\mathcal { M }` | `\mathcal{M}` |
| `\begin{array}` | 拆成多个 `math` 块或普通 Markdown 列表 |
| `\begin{align}` | 拆成多个 `math` 块 |
| `\substack` | 拆成多行文字说明或多个公式块 |
| `\newcommand` | 直接写展开后的公式 |
| `\DeclareMathOperator` | 直接用 `\mathrm{...}` |
| `\Vert` | KL 分隔符写 `\,\|\,` |
| `\| ... \|` | norm 写 `\left\lVert ... \right\rVert_2^2` |

其中 `\operatorname{KL}` 在 GitHub 可能报 `The following macros are not allowed: operatorname`，直接写 `\mathrm{KL}` 更稳。

KL 示例：

````markdown
```math
\mathrm{KL}\left(
p_S(\cdot \mid x)
\,\|\,
p_T(\cdot \mid x)
\right)
```
````

Loss/KL 块级示例：

````markdown
```math
\mathcal{L}(\theta)
=
\mathbb{E}_{x\sim p_\theta}
\left[
\mathrm{KL}\left(
p_\theta(\cdot \mid x)
\,\|\,
p_T(\cdot \mid x)
\right)
\right].
```
````

Norm 示例：

````markdown
```math
\left\lVert
\mu_S-\mu_T
\right\rVert_2^2
```
````

少用纯排版宏：

```latex
\bigl
\bigr
\Bigl
\Bigr
\!
```

改成普通括号，或使用：

```latex
\left( ... \right)
\left[ ... \right]
```

稳定示例：

````markdown
```math
\Pr(y \succ y' \mid x)
=
\sigma\left(r(y;x)-r(y';x)\right)
```
````

比下面更稳：

````markdown
```math
\Pr(y \succ y' \mid x)=\sigma\bigl(r(y;x)-r(y';x)\bigr)
```
````

README 表格里的公式：

- Markdown 表格用 `|` 分列，所以公式里不要出现裸竖线。
- 表格里只写变量名、shape、含义。
- 条件概率、KL、norm 等复杂公式移出表格。

危险：

```markdown
| `P(y|x)` | 条件概率 |
```

推荐：

```markdown
| `P(y given x)` | 条件概率 |
```

或者移出表格：

````markdown
条件概率写作：

```math
P(y \mid x)
```
````

OCR/PDF 解析公式必须手工清理。PDF 解析出来的公式经常会有异常空格、错括号、断裂命令。

| OCR 风险写法 | 稳定写法 |
| --- | --- |
| `\hat { \mathcal { M } } ( x , t , m )` | `\widehat{\mathcal{M}}(x,t,m)` |
| `${\overset{^}{y}_{j,k}}$` | `\hat{y}_{j,k}` |

推荐稳定符号：

```latex
\mathcal
\mathrm
\mathbb
\theta
\pi
\mu
\sigma
\epsilon
\Delta
\sum
\frac
\sqrt
\left
\right
\mid
\cdot
\sim
\nabla
\top
\mathbb{E}
\mathbb{R}
\mathcal{N}
\mathcal{L}
\mathrm{KL}
\mathrm{ref}
\mathrm{PairRM}
\frac{...}{...}
\sum_{k=1}^{K}
\left\lVert x \right\rVert_2^2
\Pr(y \succ y' \mid x)
\pi_\theta(y\mid x)
```

公式旁边必须解释变量：

- 每个变量是什么。
- 是标量、token 序列、分布还是张量。
- 形状是什么，例如 `[B,T,D]`、`[B,N_v,D]`。
- 这个公式实际在做什么。

示例：

```text
这里的 `y_{1:i-1}` 表示 response 中第 1 到第 i-1 个 token，也就是生成第 i 个 token 时已经看到的前缀。
```

修完公式后检查：

```bash
grep -nE '\\$\\$|\\operatorname|\\operatorname\\*|\\bigl|\\bigr|\\Bigl|\\Bigr|\\!|y_\\{<|<think>|<answer>' README.md
git diff --check
```

还要检查：

- ` ```math ` 数量和关闭围栏配对。
- 没有公式围栏嵌在表格里。
- 没有 `<think>`、`<answer>` 这类未转义标签。
- GitHub 页面上没有 `Unable to render rich display`。

公式不显示时按顺序修：

1. 把 `$$ ... $$` 改成 fenced math block。
2. 把 `\operatorname{...}` 改成 `\mathrm{...}`。
3. 把 `x_{<t}` 改成 `x_{1:t-1}`。
4. 把 KL 分隔符改成 `\,\|\,`。
5. 把 norm 改成 `\left\lVert ... \right\rVert`。
6. 删除自定义宏，写成完整展开公式。
7. 将超长公式拆成多个短块。

一句话总结：GitHub 上写公式，不追求 LaTeX 排版精致，追求 KaTeX + Markdown + HTML 三层都稳定。长公式用 `math` 围栏，复杂符号简化，prefix 下标别写 `<`，表格里别塞公式。
