# 日志、对话与文字

## 规范化日志

- `prepare_trace.py` 读取 JSONL 的 `direction=output`（或无 direction 的 assistant 消息），以及同一 `step` 的 execution 时间。默认只输出公开消息正文和时间；截图与工具卡片需显式启用，不复制完整 API response 或隐藏推理。
- 配置的 `anchor.log_timestamp` 与 `anchor.source_seconds` 指向同一个已确认动作；可引用剪辑计划扣除 cuts。不要混用 UTC、当地时间和没有时区的字符串。
- 时间压缩会把剪掉区间内的消息映射到同一个剪口，播放时以该时刻最后的状态为准。片尾之外的消息留在清单中，不强行提前显示。
- `task_summary` 由 agent 根据任务要求简写，保留目标和关键行为，不堆全部操作细节。
- 鼠标坐标优先读取实际 x/y。需要 G/L 网格时必须明确全局间距、局部间距、局部当前鼠标 label 和初始位置；未校准时只输出消息，报告 unmapped pointer calls，不猜连续坐标。
- 有些 harness 会因边缘裁切、DPI 或窗口布局改变局部网格原点。只有确认其规则稳定才用固定 origin；否则逐步使用真实观察中的坐标/label，或手工导出规范化 `moves`。

```bash
python3 scripts/prepare_trace.py --config ./trace.json --output ./events.json
```

规范化后的 `events` 包含 `time`、`step`、`role`、`text`，有反馈时包含 `executed_at`；`moves` 使用 `time/x/y`，坐标属于完整录屏像素。

## 连续对话播放器

- 设置显示名、说明、logo 与任务摘要；原始日志的 recorded model 信息保留，不通过改写原始记录制造测试来源。
- 以真实输出时间追加气泡，内容超出卡片时自动上滚，固定标题区。不要默认将整个 API 响应或内部 reasoning 展给观众。
- 消息播放与面板退场分开控制。即使第二轮结束开始退场，第三条及之后仍在自己的时刻追加；测试独立对话素材在退场后是否仍推进。
- 绘制完整消息文档，再按当前最后一条裁取 viewport。遮住未来内容，避免预先绘好的后续消息从空白区漏出。
- 用户请求只展示部分消息时才过滤；“两轮后退出”本身不等于截断消息列表。
- 若在录屏和品牌展示间使用用户指定的模型显示名，界面可按要求展示，但原始来源记录不篡改，也不声称另一模型实际执行了原日志。

```bash
python3 scripts/render_overlays.py chat --config ./chat.json
```

输出 FFV1 无损视频和状态 PNG。它是渲染素材，交付 MP4 仍由合成工具生成。

## 面向观众写字幕

- 解释“当前做什么、为什么做”，不用每句都说“点击某按钮、按某组合键”。字幕与观察结果对齐，不把尝试中的操作写成已成功。
- 把长操作拆成阶段；阶段标题可在左上角，正文放底部留白。一行放不下先简写，不机械缩到难读。
- 科研展示不夸大：强度阈值筛选高密度区域不等于精确识别器官；局部预览不等于完整的科学验证。
- 名称用用户要求的品牌和模型名；不要用含糊的“智能助手”替代已经指定的名称。
- 拍摄/操作中的长停顿不必逐帧变字幕。阶段连续时保留文字，必要时小幅淡入；不要因每轮工具调用都切一条字幕。

## 字体与排版

- 中文字体需覆盖字形；优先项目已有、可合法使用的 Noto Sans SC、Noto Serif SC 或其他用户指定字体。不要把本机字体文件直接提交到公共项目。
- 正文适合清楚的中等字重 sans，阶段标题可配 serif 形成层次。字号按输出分辨率、实际播放尺寸和留白选择，不照搬 3200 像素画布的数值到 720p。
- 可变字体可能默认 Thin/ExtraLight。检查 variation axes，显式给 Weight；不支持该轴的普通字体保持原样。
- 单行正文的实际 `textlength` 必须小于可用宽度；阶段标签的 `textbbox` 必须在预留 header 内。宽度够还要检查字高、上下空隙与真实缩放后的可读性。
- 只要纯文字时保持 RGBA 背景透明，不添加色块。深色文字适合明亮背景；复杂背景若需要描边/底衬应与用户样式要求一致，不能擅自加大底板。
- 标题和底部正文可以打包成一个较矮的透明 strip，再在合成时裁成两层放到各自位置，避免逐帧编码整个透明画布。

```bash
python3 scripts/render_overlays.py captions --config ./captions.json
```

## 字幕异常排查

1. 直接从 MP4 解码一帧，对照播放器截图。若只有播放器里出现额外大字，先检查自动加载的同名 SRT/ASS 或内嵌字幕轨道，不先改正常的视频字体。
2. `validate_export.py --burned-only` 同时检查 subtitle stream 和同目录同 stem 的外部字幕文件。删除文件后播放器可能仍缓存内容，需关闭并重新打开视频或关闭该播放器字幕层。
3. 工具默认只把字幕写入画面，不导出 SRT。用户明确需要软字幕时才使用 `--srt-output ./separate_subtitles/captions.srt`，避免和已经带字的交付视频同目录同名自动叠加。
4. 内部 PNG、FFV1 strip 和 JSON 是工作素材，不是需要用户在播放器加载的字幕文件。

## 观察、工具与最终交付卡片

- **显式启用：** trace 配置设 `include_screenshots: true`、`include_tools: true`，并以 `tool_argument_fields` 列出可公开参数。截图读取输入轮次的 `images.screenshot`，路径相对于 `screenshot_dir`；没有文件报错，不悄悄用带网格或后期改过的截图替代。
- **来源校验：** 规范化事件保留截图 SHA-256，渲染前再次校验；显示路径相对于公共 `media_root`。移动事件 JSON 时应同时保持媒体根和相对路径关系。
- **选择公开内容：** 实际屏幕可能含敏感信息，检查后再授权发布。工具参数采用白名单；允许的路径、输入文本本身也要复查。不能因为截图与日志已在本地就默认可上传。
- **类别可辨：** `rich_cards: true` 允许 `user/model/observation/tool/result`。观察卡片显示原始截图缩略图；工具卡片用独立颜色、工具名和键值布局，避免看起来只是普通聊天文本。
- **双重白名单：** 规范化和渲染配置分别设 `tool_argument_fields`，渲染 manifest 只保留选中的字段，不把未公开参数藏进交付 JSON。
- **Emoji 可选：** 可给 `emoji_font` 指定合法字体以画相机/工具标记，示例默认用文字标签；缺彩色字形时不要让方框替代类别。
- **调用不是成功：** 工具卡片表示请求/执行，不证明按钮已生效。完成文案必须有新截图或真实状态支持。渲染器按时间排卡，不自动验证操作成功。
- **完整交付：** 最后一条可显式加 `role: "result"`、`image` 与短说明，截图应来自实际成片/原片对应的结果画面。为叙事添加的结果卡设 `editorial: true`，保留原日志身份与时间，不伪装为真实模型消息。
- **展示节奏：** 不要求把每个内部 token 展示出来；任务摘要、公开输出、观察和调用要保留可理解的因果关系。常驻侧栏不设置退场；需要退场时以包含所需时间字段的事件为锚，避免同轮截图抢占执行反馈锚点。

```bash
# trace.json 中启用截图/工具，并先审阅获准公开字段。
python3 "$SKILL_DIR/scripts/prepare_trace.py" --config ./trace.json --output ./rich-events.json
# 从 assets/rich-chat.example.json 和 rich-events.example.json 开始配置。
python3 "$SKILL_DIR/scripts/render_overlays.py" chat --config ./rich-chat.json
```

富卡片仍按时间追加、遮住未来消息并自动上滚。先看最后一张状态图是否完整显示图片和说明，再决定交付停留时点；精确帧预算见 [08](08_exact_timing_and_source_quality.md)。
