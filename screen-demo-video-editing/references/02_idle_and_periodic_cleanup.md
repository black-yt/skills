# 静止、周期与原始开场

## 删除静止片段

1. 用缩略灰度/低帧率分析，输出静止候选；正式导出仍读取全分辨率原片。`freezedetect` 的 noise/minimum 依素材调节，低噪声不等于语义无变化。
2. 为每段静止保留一部分停顿。可以从保留约 2%、至少 0.5 秒开始试，但用户要“保留思考过程”时不应把所有停顿删光。
3. 把保留时间分到等待段前后，避免按钮刚点下就切走、下一步刚出现便跳变。参数输入、选区形成、加载成功与操作反馈要有可读时间。
4. 头尾裁切独立列入 EDL。新增“去掉原片前一分钟”时与已存在 cuts 合并，不能从成片再凭时长重复切一分钟。
5. 小范围复看切口，再整片导出和解码。检测报告只是候选，不是无需检查的自动删除许可。

```bash
python3 scripts/edit_timeline.py detect-static ./source.mp4 --output ./freezes.json \
  --minimum 1.5 --noise=-60dB
python3 scripts/edit_timeline.py build-plan --freezes ./freezes.json --output ./edit.json \
  --keep-fraction 0.02 --minimum-pause 0.5 --head 0 --tail 0
python3 scripts/edit_timeline.py render --plan ./edit.json
```

如果片段中的轻微图像更新正是科研结果，不可因它只改变少量像素就删除。

## 去掉冗余周期

- **限定范围：** 先确认是哪段无意义等待，例如分割预览在同一幅图上反复闪烁。不要对整片自动套用，否则会删掉真实切层、数据周期、模型自动摇摆。
- **提取周期：** 在明确的内容 ROI 上取均值信号、阈值过零或自相关，估计周期并找完整相邻周期。片段首尾的不完整周期单独保留。
- **同相位比较：** 一个周期的亮相与下一周期的暗相不应直接比较。可比较周期中位图，再在信号 ROI 上做最近相位匹配，记录内容差异。
- **光标遮罩：** 鼠标指针或输入插入符会制造虚假差异。只遮掉实际复核过的小区域，不能遮掉整个参数框、选区边缘或 ROI。
- **保护真正变化：** 数字更新、菜单选择、面板标题、分割结果与切片内容都应触发保留。报告同时记录遮罩前、遮罩后的变化像素和内容相位差异。
- **删除单位：** 在内容稳定的 run 内删除完整周期，前后留少量呼吸；不要把所有闪烁都保留，也不要切任意半周期造成亮暗突跳。
- **接缝优化：** 在周期整数倍附近搜索几帧，比较 `start-1` 与 `end` 的实际画面；变化过大时保留该 run 供人工判断，而非强切。

```bash
python3 scripts/analyze_cycles.py --source ./source.mp4 \
  --regions ./cycles.json --output ./cycle_report.json
python3 scripts/edit_timeline.py build-plan --freezes ./freezes.json \
  --cycles ./cycle_report.json --output ./edit.json
```

`assets/cycles.example.json` 的 ROI 坐标属于示例分析尺寸，必须根据新素材重画。`signal_roi` 是反复变化的内容区，`static_regions` 是应该稳定但可能出现参数变化的区域，`cursor_ignore_regions` 是经过确认的指针区域。阈值依赖分析分辨率，样例的“10 个像素”不适用于所有素材。

## 恢复移动前的真实静止

- 用户要求动作前静止 3 秒，假设原片首次移动在 12 秒，应保留从 9 秒起的原片以及完整移动后的短段。
- 不能将已经移动后的保留首帧用 `tpad` 冻结 3 秒；时长虽然对，动作起点和鼠标位置却错了。
- `build-plan --first-motion 12 --still-before-motion 3 --protect-after-motion 1` 会保护 `[9,13)` 并裁去更早的片头。确认真实第一动作时间后再填写，不能从演示模板猜。
- 验收时检查移动区域的相邻帧：动作前应一致，动作起点应出现真实指针变化；还要确认原动作没有被此前静止 cuts 切掉。

## 质量与播放器

- 有损导出每次从原片/确认的时间轴重建，避免对上次有损导出反复压缩。只改音频例外：直接复制已确认成片视频包。
- `CRF 18 + medium + yuv420p + faststart` 是兼容性较好的起点，码率上限依分辨率和设备选择；不能把它称无损。
- 显示裁切、无损编码、视觉相似与有损高质量是不同承诺。说明用的是什么方法，以及如何核对。
- 末尾“卡一下”先检查时间戳、实际最后帧、解码和另一播放器。若文件正常，不要为了播放器性能一遍遍误切尾部。
