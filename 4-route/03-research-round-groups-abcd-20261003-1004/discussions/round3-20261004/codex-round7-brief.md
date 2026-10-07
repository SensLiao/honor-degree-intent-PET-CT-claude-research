# Codex 第 7 轮：两份外部 deep research 的核对，以及 10-31 前的最终方案（同一会话接着问）

谢谢第 5、6 轮。第五稿在你第 6 轮意见后已改定（计划目录 PLAN.md）。导演没有直接拍板第五稿，而是又拿了两份外部 deep research 来，要我们“详细阅读检查，开多 agent 讨论，配合 Codex Astra 做分析和深度研究，给最终版本计划”，要求：效果越高越好；围绕 intent 发散和深挖创新；**10 月底前跑完所有实验**（主实验、最佳组合、导演满意后的消融和归因，供 Honours 论文 11 月上中旬交稿；之后再考虑顶会顶刊）。

## 新材料（都在本机，只读）

- 本轮共同说明（导演原话、约束、10-04 01:54 服务器现状、文件位置）：`C:\Users\廖神\AppData\Local\Temp\claude\C--Users----Desktop-Honor-degree\05dc1f8f-e2e5-4f75-95f9-1de19cf841e7\scratchpad\r3\00-brief-round3.raw`
- Gemini 报告原文：同目录 `input-gemini-deep-research.raw`
- ChatGPT 6 Pro 对话总结：同目录 `input-chatgpt-summary.raw`；它的修订包解压在 `...\scratchpad\chatgpt-pkg\petct-sirb-v2-referent-scope-plan-20261003\`：第六稿 `PLAN.md`，审计 `research/R2-review-and-recommendations.md`、`R2-local-audit.md`、`R2-peer-review.md`、`R2-math-audit.md`、`R2-sequential-audit.md`、`R2-interactive-audit.md`、`R2-medical-scale-audit.md`、`R2-cognition-audit.md`、`R2-llm-causal-audit.md`，文献登记 `R2-literature-register.md`（168 篇）。
- 我们的第五稿和调研：`C:\Users\廖神\Desktop\Honor degree\projects\petct_textual_intent\protocols\petct-sirb-v2-referent-scope-plan-20261003\`（PLAN.md、research/）。
- vault（只读 wiki/）、本机结果、代码、上游 2S-ICR 代码位置见共同说明第 4 节。

## 新出现的事实（10-03 夜到 10-04）

- flat 诱导状态 N1_STATE_INDUCED（v1 flat 40k 续训 8k，加模型自身失败状态）快速 VAL D5 0.760569、nAUC 0.723365；同 roster 的原配方续训对照 N1_STATE_STATIC 为 0.760217、0.718867，差 +0.0004/+0.0045。101 片段目标区域 Dice 0.6086（对照 0.6109）。397 状态评估还在跑。
- z390 还剩 N3_ES、N1_STATE_SPATIAL 两个已批准训练及评估，约 10-04 下午跑完。数据盘只剩 45 GB。
- A6000 两卡 UAM 基线变慢到约 1136–1161 秒/轮（此前约 315），GPU 利用率 36–56%，compact_stall 只有 6.3 万（不是 z390 那种透明大页问题），原因未定；5090 在跑 2S-ICR fold2–4，之后 IKIM。十月里 SIRB 实际上只有 z390 一张 3090 可靠可用。

## 请回答（结论先行，中文，尽量短；数字自己从文件核，拿不准就说）

1. **两份外部报告哪里错了、哪里有用。** Gemini 和 ChatGPT 各列最严重的问题（引原句，说错在哪），以及各自真正能改进我们第五稿的新内容。特别核：ChatGPT 说官方机器人的“最大错误”是“FP/FN 各在单个轴向切片里找面积最大的 8 邻接分量”，请对代码（`scripts/common/petct_sirb_robot.py` 等）确认；它提出的 g/b 两个小预测器加“预测越界不比同状态 0.5 编辑大”的选择规则、一次联合策略 TRAIN 回放刷新、no-op 零收益平台的两支续演、两阶段数据流（M0 五折在 506 扫描上、SIRB 407/99 独立二分）是否成立、值不值得做。
2. **10-31 前最有效率的组合。** 假设十月 SIRB 只有 z390 一张 3090（训练约 3 小时/8k，快速 VAL 约 1.5 小时，三画法 VAL 约 4.7 小时，回放 2–3 小时），全部实验（含导演满意后的消融、归因、第二种子）10-31 前完成。请按“每 GPU 天预期 D5 增益”给候选部件排序并给证据：执行端选择器、指代约束 Dice 收益损失、边界排序加保留样本、空间支路、无截断几何、上一轮足迹、自身状态刷新、学出连通、成对干预、选笔策略混合；以及工程增益：翻转 TTA（测试时左右翻转再平均）、同父续训权重平均、多种子或多 checkpoint 集成。工程增益和基线的五折 ensemble 怎么公平地并排报？
3. **只改 T 和 Dice 的关系。** TEST 修复上限 0.8814 和 VAL 理想五轮 0.9172 各是什么口径（查 vault T052、A_q1）？“只改这一笔所指的错”这个 intent 约束在 0.80 目标下会不会封顶？顺带修 O 的潜在收益有多少（有数据就给数据）？
4. **2S-ICR 为什么每轮涨得多。** 它 TEST 从 0.5778 到 0.8000（+0.222），我们 flat 从 0.6387 到 0.7694（+0.131）。读上游 2S-ICR 代码和我们的协议记录，说哪些设计差异最可能解释这个差距（例如每轮整卷重新分割、提示编码、在自己预测上训练、起点更低），哪些能在保持 intent 的前提下搬过来。
5. **intent 创新的可辩护部分。** 面对 ChatGPT 列出的直接近邻（VISTA3D、PRISM、ClickAttention、Structured Click Control、nnInteractive、FocalClick-XL），本项目哪两三个贡献对 Honours 论文站得住、对 MICCAI/MedIA 级别站得住？每个配一个能证伪的实验。
6. **消融和归因怎么排进剩下的显卡时间。** 最佳系统大约哪天必须定下，才能在 10-31 前做完同父同预算的逐项去除、执行端 0.5 对选择器、配对有无、第二种子、对比实验？给一个最小但够写论文的消融清单。
7. **一句话**：按你的判断，这个计划 10-31 前让 TEST D5 超过 0.80 的把握（高/中/低）和最大的单一杠杆是什么。

边界同前：只读，不连服务器，不读凭据，不改任何文件。
