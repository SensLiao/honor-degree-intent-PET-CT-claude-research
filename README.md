# PET/CT SIRB-Net 研究文档

这里放 SIRB-Net 第二版这条线的全部研究文字：现行计划、所有成绩、数据和模型的说明、文献，以及从 v1 一路走到 K4 每个阶段做了什么、发现了什么。以后的新发现、新分析和下一步计划都写在这个文件夹里。

## 先读哪几份

1. `1-plan/PLAN.md`：现在走到哪、目标和成绩、为什么没过线、下一步、要导演定的事。
2. `4-route/README.md`：七个阶段的目录，每个阶段一句话。想知道某一步是怎么走过来的，进对应阶段的文件夹看它的 README。
3. `2-results-and-models/results-all-systems.md`：所有系统的成绩，验证集和测试集分开写。

查口径、网络、部件和损失，看 `2-results-and-models/data-models-and-protocol.md`。查文献，看 `3-literature/`。

## 每个子文件夹放什么

| 文件夹 | 放什么 | 怎么改 |
|---|---|---|
| `1-plan/` | `PLAN.md` 总计划；`experiment-schedule.md` 实验安排（判定、候选改法、显卡、过线后的归因、公平对比、论文表图、投稿去处） | 只留最新一版，直接改 |
| `2-results-and-models/` | 成绩总表；数据、模型和评测口径；原始结果文件在本机哪里 | 出新成绩、改了口径或部件就改 |
| `3-literature/` | 13 个领域的文献深挖；10-07 为 K 没过线查的归因方法和文献（75 个来源）。论文 PDF 在 `Thesis/sirb-research-20261003/` | 新读的文献补进对应领域 |
| `4-route/` | 研究路线，一个阶段一个文件夹，按时间排 | 写完的阶段只补更正；进入新阶段就开新文件夹 |

每个阶段文件夹的 README（文件夹首页说明）都写七段：为什么做、做了什么、结果、发现、当时的决定、留下了什么、证据在哪。同一个文件夹里还放这一步的原文记录、图、分析脚本和输出、服务器诊断，以及 Codex 和外部调研的原文。

## 以后怎么写

- 新发现、新分析写进当前阶段的文件夹。换配方或进入新阶段，就在 `4-route/` 开一个新文件夹。
- 计划变了，改 `1-plan/` 里的两份。
- 新成绩补进 `results-all-systems.md`，写明验证集还是测试集。测试集成绩照旧同时登记在 vault 的 TEST 登记表。
- 原始结果文件不复制到这里。验证集结果和训练记录照旧收回代码树 `records/development_results_transfer/`，测试集结果收回 `records/eval_results_transfer/`，这里只写它们在哪。
- vault 管决定（决策正本）、测试集登记、任务进度和最新情况（hot），并链接到这里；长篇的方案和分析只写在这里。
- 改完一轮，在本文件夹提交一次版本记录（git）。旧版从版本记录里调，不再另存 zip。

## 旧位置对照

10-07 整理以前，这些内容分散在别处。原文里提到旧位置的，按这张表找。

| 旧位置 | 现在在哪 |
|---|---|
| 代码树 `protocols/petct-sirb-v2-referent-scope-plan-20261003/PLAN.md` | 第二部分和“系数从哪来”在 `1-plan/PLAN.md`；第零部分在 `4-route/route-overview-20261005.md`；第一、三、五部分在第 03 阶段，其中讲续训的一段在第 02 阶段；第四、六部分和第三部分的“训练方式和第一批完整组合”在第 05 阶段；第七、八部分是当时的目录和摘要，内容已在本页和第 06 阶段 |
| 同目录 `experiment-schedule-gpus.md` | 第七、九、十部分在 `1-plan/experiment-schedule.md`；第十三部分的内容已在那份的第二节；其余各部分在第 05 阶段 `k-series-design-20261005.md` |
| 同目录 `local-data-models-results.md` | 第一、二、六、七部分和出处缩写在 `2-results-and-models/data-models-and-protocol.md`；5.1 在 `results-all-systems.md`；结论、第三、四部分和 5.2、5.3 在第 03 阶段 `v1-local-analysis-20261004.md`；第八部分的内容已在第 06 阶段 |
| 同目录 `literature-domains-review.md` | `3-literature/literature-review.md` |
| 代码树 `records/verification/analysis-sirb-k-val-shortfall-20261006/` | 报告 1 拆进 `1-plan/PLAN.md` 和第 06 阶段 README；报告 2 是第 06 阶段 `k-analysis-report-20261007.md`；报告 3 在 `3-literature/`；报告 4 在 `1-plan/experiment-schedule.md` 和第 07 阶段；图、脚本、输出、服务器诊断、Codex 原文在第 06 阶段，K4 的排队文件在第 07 阶段。数据副本没有搬，原件位置见 `2-results-and-models/result-files-index.md` |
| `Thesis/sirb-research-20261003/` 里的三个 zip | 10-03、10-04 的调研原文、外部报告和讨论稿解压在第 03 阶段；10-05、10-07 两版旧计划在版本记录里 |
| 代码树 `records/verification/` 里三份 Codex 复核 | 第 03 阶段和第 05 阶段的 `discussions/` |
| vault 的 T083 主线任务页、主计划页、实验总表、09-30 完整 VAL 分析页 | 长篇内容在第 01 到 07 阶段；vault 只留进度、复现信息和链接 |
