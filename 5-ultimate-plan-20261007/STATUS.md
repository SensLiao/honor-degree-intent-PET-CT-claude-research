# STATUS：究极 plan 进度表

最后更新：2026-10-07 07:14 UTC

结论一句话：网络通道已打通并写进规则（arXiv、doi.org、eutils/PMC、Europe PMC、OpenReview、CVF、PMLR、ACL、Cambridge Core 可用；PubMed 文章页、Nature、Springer 经 WebFetch 只给 cookie 页，已给出替代通道），七个领域合计已核实 227 篇（去重，脚本统计）；01 复盘已写完（325 行），02 核心想法、ULTIMATE-PLAN、05 配置草案、06 风险与判伪均有第一版，等模块候选、新意核查和两轮对抗审查后修订。并发上限 20 个子 agent，目前 20 个在跑，27 个排队（见 `work/AGENT-QUEUE.md`）。

## 各领域已核实篇数（`04-cross-domain/count_verified.py` 统计，去重后）

| 领域 | 已核实 | 未核实（不计数） | 目标 | 状态 |
|---|---|---|---|---|
| 心理学 psychology | 77 | 2 | 100 | 6 个检索 agent 在跑 |
| 脑神经科学 neuroscience | 81 | 1 | 100 | 6 个检索 agent 在跑 |
| 大语言模型 llm | 64 | 0 | 100 | 2 个完成（各 32 篇），3 个在跑，1 个排队 |
| 医学计算机视觉 medical-cv | 1 | 0 | 100 | 7 个排队；另有新意核查和 SOTA 背景两个 agent 在写入 |
| 物理 physics | 0 | 0 | 100 | 6 个排队 |
| 数学 mathematics | 4 | 0 | 100 | 7 个排队 |
| 教育学 education | 0 | 0 | 100 | 6 个排队 |

合计：227 / 700。

## 已完成

- `01-review-of-current-results.md`（复盘，325 行，带证据强度与统计功效推算）。
- 第一版：`02-core-idea-and-novelty.md`、`ULTIMATE-PLAN.md`、`05-experiment-configs-proposal.md`、`06-risks-and-falsification.md`。
- `work/PROJECT-BRIEF-for-agents.md`、`work/LIT-AGENT-INSTRUCTIONS.md`（含两节网络实测补充）、`work/LIT-SUBTOPICS.md`（44 个子主题）、`work/AGENT-QUEUE.md`。
- 主 agent 自己核实并登记 6 篇原理论文（Lipton 2014 F1 最优阈值、Grady 2006 随机游走者、Ross 2011 DAgger、Kendall 2018 不确定性加权、Clark 2013 预测加工、nnInteractive 2025）。

## 正在做

- 20 个子 agent：14 个文献检索（心理学 6、神经科学 6、LLM 2 在跑）、模块候选两部分、新意核查（直接近邻逐篇开原文）、已有调研摘要、SOTA 与协议背景。
- 等空位依次启动 27 个排队的检索 agent（LLM 1、医学 CV 7、物理 6、数学 7、教育学 6）。

## 还差什么

- 03 模块候选（两部分在写）、`work/NOVELTY-CHECK.md`、七个领域综述 `04-cross-domain/review-<领域>.md`、07 对抗审查两轮及修订、README。
- 五个领域尚未开始检索（排队中），要到 100 篇还差：医学 CV、物理、数学、教育学全部，心理学与神经科学看第一批结果再补。

## 已知问题

- WebSearch 配额会中途耗尽；已给子 agent 替代搜索 API（arXiv API、Crossref、Europe PMC、eutils、dblp）。
- 翻转平均在 K1/K2/K3 上是 −0.004 到 +0.004（验证集），计划里已把它从预期收益里拿掉。
