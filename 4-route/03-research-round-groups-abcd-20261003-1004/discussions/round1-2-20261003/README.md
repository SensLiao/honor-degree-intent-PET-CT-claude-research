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
