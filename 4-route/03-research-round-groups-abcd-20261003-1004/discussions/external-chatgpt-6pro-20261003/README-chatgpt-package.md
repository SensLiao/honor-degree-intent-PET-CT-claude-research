# SIRB计划与研究记录索引

## 当前入口：第六稿独立复核（2026-10-03）

当前执行依据是上一级 [PLAN.md](../PLAN.md)。目标为最终锁定TEST D5 >0.80；三画法VAL >=0.79即报告。先跑A/B强组合，C独立推进；效果后再做归因。

| 文件 | 内容 |
|---|---|
| [R2-review-and-recommendations.md](R2-review-and-recommendations.md) | 完整复核报告：发现、领域、论文、迁移思想、最精炼实施方案 |
| [R2-literature-register.md](R2-literature-register.md) | 168篇跨路去重登记；127篇相关原文正文核读、41篇访问有限 |
| [R2-literature-register.json](R2-literature-register.json) | 文献、原始URL、访问深度、各路重复映射的机器可读记录 |
| [R2-literature-register.bib](R2-literature-register.bib) | 最小书目导入索引；作者/卷期页码未补齐，不作为最终投稿书目 |
| [R2-local-audit.md](R2-local-audit.md) | 附件数字、口径、公式与可验证范围 |
| [R2-peer-review.md](R2-peer-review.md) | 六路交叉审查及最后限定阻断检查的采纳记录 |
| [PLAN-draft5-20261003.md](PLAN-draft5-20261003.md) | 本次修订前的原第五稿，逐字保留 |

### 六路原始核验

每一路均提供报告和对应JSON逐篇记录：

- [R2-interactive-audit.md](R2-interactive-audit.md)：交互分割与创新近邻，32条。
- [R2-math-audit.md](R2-math-audit.md)：图、Dice决策、校准与数学边界，28条。
- [R2-sequential-audit.md](R2-sequential-audit.md)：闭环状态、序贯决策与控制，27条。
- [R2-cognition-audit.md](R2-cognition-audit.md)：认知、意图、教育、运动学习，34条。
- [R2-llm-causal-audit.md](R2-llm-causal-audit.md)：LLM编辑、因果配对与弱监督，31条。
- [R2-medical-scale-audit.md](R2-medical-scale-audit.md)：通用医学、PET/CT、尺度与数据来源，27条。

179条分路记录去重为168篇，含165篇原始研究/方法论文、2篇元分析和1篇撤回状态核验。阅读深度按逐篇记录，不将摘要当全文，不将本轮全部计为新发现。

### 证据边界

本轮读取了上传ZIP的81个原始文件。附件没有此前401份PDF、生产模型/完整源码、完整原始逐例轨迹和现场日志；此处的旧实验数值不是本轮重跑结果。新增脚本结果只核对JSON算术与代数。没有修改Windows项目或服务器，没有启动新的训练/VAL/TEST。

S1、S2开头已加入明确更正。它们后面的旧摘要，以及下面列出的早期文献与Codex文字，作为历史过程保留；与第六稿及本轮审计冲突时，不再作当前决策依据。

## 历史目录说明

以下原索引保留供定位，其中日期、下载数量、服务器和历史完成状态均为旧记录的自述，本轮没有重新验证。旧的 .tmp/sirb-research-20261003 路径对应本目录。

本目录是 SIRB-Net 第二版计划（上一级 PLAN.md）的调研记录。第一轮在 2026-10-03 傍晚，原在项目根 `.tmp/sirb-research-20261003/`，计划定稿时挪到这里，文中引用的 `.tmp/sirb-research-20261003/...` 路径都对应本目录；第二轮在 10-03 夜，按导演令直接写在这里，没有建新文件夹。

第一轮
- `00-fact-sheet.md`：发给各路调研和 Codex 的共同事实单。
- `A-` 到 `G-`：本地失败拆解（VAL）、交互分割文献、PET/CT 与 autoPET、创新与查新、代码可行性、认知科学与教育学、LLM 与跨领域。
- `R-redteam-review.md`：对初稿的挑错复审。
- `codex-round1` 到 `round4`：给 Codex 的简报和它的回答（只读会话；会话日志没有保留）。
- `PLAN-draft4-20261003.md`：第四稿留底（第五稿取代前的版本，Codex 第 1 到 4 轮审的就是它的前身）。

第二轮（导演 10-03 晚令，决策 D-2026-10-03-05）
- `00-fact-sheet-round2.md`：第二轮共同说明，导演新要求、痛点 P1 到 P8、记录格式。
- `H0-internal-paths.md`：项目自己走过的路子和 intent 概念的演变（读了归档区）。
- `H1-hand-set-coefficients.md`：方法里手定系数的清点和改法。
- `L1-` 到 `L11-`：十一路外部文献（传播数学、决策与门槛、控制与迭代、交互分割、涂鸦弱监督、视觉认知、意图推断、教育与运动学习、LLM 与编辑、因果与成对、通用模型与尺度）。
- `S1-literature-digest.md`：逐领域文献摘要和去重清单；`S2-causal-map.md`：因果对照、交叉印证和组合方案。两份开头都补了核对与复审更正。
- `V1-citation-check.md`：抽查核对（101 处、130 篇论文），PDF 体检，去重篇数（385）。
- `codex-round5`、`codex-round6`：Codex 新会话（id 01a10188-37cb-79d2-b1fc-1c4348c0e417）的简报和回答。

`scripts/`：拆解和核对用的一次性脚本及其 JSON 输出，只读本机已回传的 VAL 结果和训练日志。A_ 开头为第一轮本地拆解，E_ 开头为代码可行性核对，S_ 开头为第二轮检查（`S_oracle_threshold_per_state`：每笔从 19 档门槛和“不改”里挑最优的单步上限）。

下载的论文 PDF 在项目根 `Thesis/sirb-research-20261003/`，401 个文件，约 1.93 GiB，全部核过文件头。
