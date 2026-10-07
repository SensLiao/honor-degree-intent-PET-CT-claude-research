# STATUS：究极 plan 进度表

最后更新：2026-10-07 07:05 UTC

结论一句话：上一次运行卡在网络策略上（当时只放行 github.com），本次实测 arXiv、doi.org、PubMed/PMC、Crossref、OpenReview、NeurIPS、CVF、Springer、Nature、PLOS、eLife、Frontiers、ACL、dblp 全部可达，文献核实可以做；仓库已通读（README、1-plan 两份、2-results 三份、4-route 七个阶段 README、03/05/06/07 的核心分析、H1 人定系数清点），正在并行开约 50 个子 agent（44 个文献检索、6 个复盘/模块/新意核查/已有调研摘要）。

## 本次实测网络（2026-10-07 07:00 UTC）

能打开：arxiv.org、export.arxiv.org、doi.org、api.crossref.org、pubmed/pmc/eutils、openreview.net、proceedings.neurips.cc、openaccess.thecvf.com、link.springer.com、nature.com、aclanthology.org、journals.plos.org、elifesciences.org、frontiersin.org、dblp.org。
被拦：scholar.google.com、api.semanticscholar.org（429）、biorxiv（429）、ieeexplore、dl.acm.org、sciencedirect、wiley、pnas、science.org、psycnet、jneurosci、aps、tandfonline、mdpi。对策写在 `work/LIT-AGENT-INSTRUCTIONS.md`。

## 各领域已核实篇数（`04-cross-domain/count_verified.py` 统计，去重后）

| 领域 | 已核实 | 未核实（不计数） | 目标 | 状态 |
|---|---|---|---|---|
| 心理学 psychology | 0 | 0 | 100 | 6 个检索 agent 启动中 |
| 脑神经科学 neuroscience | 0 | 0 | 100 | 6 个检索 agent 启动中 |
| 大语言模型 llm | 0 | 0 | 100 | 6 个检索 agent 启动中 |
| 医学计算机视觉 medical-cv | 0 | 0 | 100 | 7 个检索 agent 启动中 |
| 物理 physics | 0 | 0 | 100 | 6 个检索 agent 启动中 |
| 数学 mathematics | 0 | 0 | 100 | 7 个检索 agent 启动中 |
| 教育学 education | 0 | 0 | 100 | 6 个检索 agent 启动中 |

## 已完成

- 建目录 `5-ultimate-plan-20261007/`，本文件，`work/PROJECT-BRIEF-for-agents.md`（项目简报，修正了仓库路径）、`work/LIT-AGENT-INSTRUCTIONS.md`（文献核实硬规则，补了网络实况）、`work/LIT-SUBTOPICS.md`（44 个子主题分配）、`04-cross-domain/count_verified.py`（统计脚本）。
- 通读仓库必读文件（见上）。

## 正在做

- 44 个文献检索子 agent 并行检索并逐篇打开来源页核实，写入 `04-cross-domain/registers/<领域>/<子主题>.json`。
- 复盘（01）、模块候选（03，两部分）、新意核查（直接近邻逐篇打开原文核）、已有调研摘要（3-literature 与 03 阶段讨论稿）。

## 还差什么

- 02 核心想法、ULTIMATE-PLAN、05 配置草案、06 风险与判伪、07 对抗审查两轮、README；七个领域综述；各领域达到 100 篇已核实。
