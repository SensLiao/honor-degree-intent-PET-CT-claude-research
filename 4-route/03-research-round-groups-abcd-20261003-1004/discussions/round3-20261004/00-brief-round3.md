# 第三轮共同说明（10-04 凌晨，Claude Code 写给本轮所有 agent 和 Codex）

## 1. 导演这次要什么（10-04 凌晨原话要点）

导演把两份外部 deep research 贴给我们：Gemini 一份（原文在 r3/input-gemini-deep-research.raw），ChatGPT 6 Pro 一份（对话总结在 r3/input-chatgpt-summary.raw，修订包解压在 scratchpad/chatgpt-pkg/petct-sirb-v2-referent-scope-plan-20261003/，含第六稿 PLAN.md 和 research/R2-* 审计、168 篇文献登记）。导演原话：

> “上面是Gemini的deep research和chatgpt的6 pro的deep research给出来的内容和分析，你去详细阅读检查，最后开启多agents去讨论（全opus，配合codex的Astra进行一个分析和深度研究），最后给出我最终版本计划（符合我们主旨要求：效果越高越好，围绕intent去发散和深度挖掘创新，10月底前跑完所有实验），直接改在原本的文件里面，在这个folder里面只保留最终的几个markdown：每个领域深度详细挖掘和分析的文章思想内容（领域，文章，思想，方法，我们怎么迁移），项目Overview计划，本地数据和模型已有分析（数据，模块，对比实验，train/val的cases的效果和情况，test分数），实验计划安排（模块制作和使用，训练的预算和模型的设置，显卡的安排，保证公平干净的对比，找出最佳组合方案，先跑主要的，得到了最佳让我满意了后，就开始跑消融和对比归因去方便写honor论文，最后在考虑相关的顶会顶刊）。”

所以最终交付是计划目录 `projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/` 里只剩四份 markdown：
1. 领域文献深挖（每个领域：文章、思想、方法、我们怎么迁移）
2. 项目 Overview 计划（PLAN.md）
3. 本地数据和模型已有分析（数据、模块、对比实验、TRAIN/VAL 病例效果、TEST 分数）
4. 实验计划安排（模块制作和使用、训练预算和模型设置、显卡安排、公平干净的对比、找最佳组合、先跑主要的、导演满意后跑消融和归因写 Honours 论文、最后考虑顶会顶刊）

这四份由 Claude Code 最后合成写入。你们各自只写自己的草稿或审计到 `scratchpad/r3/` 下指定的文件，**不改计划目录、不改 vault、不改代码树、不连服务器**。

## 2. 不变的约束（来自导演历次决定，必须遵守）

- 目标：最终模型 TEST 第五轮 Dice（D5）超过 0.80，越高越好；还要超过全部基线（现最高 2S-ICR 第 0 折单折 TEST D5 0.8000；五折 ensemble 出来后以更高者为线）。三画法 VAL D5 到 0.79 报导演一次。TEST 每个模型只用一次、另行授权，不用 TEST 选模型或参数。
- 10 月底（10-31）前跑完全部实验（主实验、最佳组合、消融、归因、对比）；Honours 论文 11 月上中旬交；之后再考虑顶会顶刊（IPMI 2027 截稿 12-07 已核实；MIDL 12 月上旬、CVPR 约 11-13、MICCAI 2027 约 2 月下旬都是推算）。
- 效果优先：先跑几个强组合出效果，导演满意后再做消融和归因（导演原话：“那个消融也没有意义”是指效果出来前不做）。
- 创新围绕 intent（意图）：模型在当前分割状态下读出这一笔指的是哪处错、多大、修到哪、和上一笔什么关系、值不值得改。intent 要定义成可检验的操作定义，不能说读懂了医生心理。
- 系数不能按 PET/CT 结果手定（30 mm、60 mm、门槛 0.5/0.7/0.9、配额 40/30/30、损失权重等）：要么网络学出，要么按每例数据或模型自估量的通用规则推出；冻结评测协议（模拟器、三种画法、3 mm 网格、5 轮、Dice、18 邻接）不动。计算预算类（候选档数、树深、步数）允许存在但要透明写明。
- flat 一条线（D-2026-10-03-03）；N3 只留 N3_ES 一次；续训版可作最终模型。
- 训练、评估只在服务器上跑；本机只写代码和跑秒级 CPU 计算（读本机已有 CSV/JSON 做统计可以）。不读、不打印 .env、私钥、凭据。
- 说“已完成/已核实”要附证据；没核实写 UNVERIFIED；推测写“推测”。VAL、TEST、TRAIN 数字必须标明。不写“首创/没人做过”，只能写“本次检索未见”。

## 3. 现状要点（10-04 01:54 AEST 实测加 vault）

- 现有模型（都从 v1 40k 出发；VAL＝99 扫描/57 患者，85 阳性扫描/54 患者进 Dice）：
  - flat v1（N1_STATE 40k）：三画法 VAL D5 0.7524、nAUC 0.7040；TEST D5 0.7694（D0 0.6387，nAUC 0.7371；82 阳性扫描/56 患者）。
  - N3 v1 40k：TEST D5 0.7619、nAUC 0.7253。
  - flat 续训对照 N1_STATE_STATIC（+8k 原配方）：快速 VAL D5 0.7602、nAUC 0.7189（同 roster 的 v1 快速 VAL 0.7562）。
  - flat 诱导状态 N1_STATE_INDUCED（+8k，加模型自身失败状态）：快速 VAL D5 0.7606、nAUC 0.7234（对 STATIC +0.0004/+0.0045）。
  - 快速 VAL＝每扫描一种冻结画法；三画法 VAL＝每扫描三种画法；两者不直接相减。
- 基线 TEST（82 阳性扫描/56 患者，按患者平均）：2S-ICR 第 0 折单折 D5 0.8000（起点是它自己的自动阶段 0.5778，nAUC 0.7504）；涂鸦基线二值通道 0.7657、距离图通道 0.7495；旧三维执行器 0.7024；分割基座起点 0.6387；修复上限（协议上限，不是模型）0.8814。2S-ICR 两折 VAL：fold0 0.5193→0.7857，fold1 0.4747→0.7615。UAM、IKIM 还没有 TEST。
- z390（RTX 3090 24 GiB，SIRB 唯一主机）：已批准队列还剩 N1_STATE_INDUCED 的 397 状态评估（10-03 23:36 起在跑）、N3_ES 训练和两项评估、N1_STATE_SPATIAL 训练和两项评估；按现速约 10-04 下午跑完，之后 GPU 空等新任务。8k 续训约 3 小时（1.25–1.35 秒/步，读数据进程 6、关 numpy 透明大页后）；快速 VAL 约 1.5 小时；三画法 VAL 约 4.7 小时；TRAIN 回放此前 6.6 小时一次（修复前），现在估 2–3 小时。训练峰值显存约 14.4 GiB、评估约 4.7 GiB。数据盘 /mnt/HDD4 只剩 45 GB（100% 用），回放存储要省。
- A6000（2×48 GiB）：两卡在跑 UAM 基线（GPU1 fold0 第二阶段 246/500、GPU0 fold1 123/500，最近约 1136–1161 秒/轮，比此前约 315 秒慢 3.6 倍；GPU 利用率 36–56%；不是 z390 那种内存整理问题，compact_stall 只有 6.3 万；原因未定）。导演定：UAM 跑完后接 SIRB。
- RTX 5090（32 GiB）：2S-ICR fold2 修正阶段 137/300（约 625 秒/轮），之后 fold3、fold4，再 IKIM 五折。
- 我们自己的第五稿计划：计划目录 PLAN.md（三步：执行端学改不改、一次 8k 续训强组合、加结构）；调研记录在同目录 research/（L1–L11 十一路文献、H0 项目历史、H1 手定系数、S1 摘要、S2 因果对照、V1 核对、codex-round1–6）。ChatGPT 第六稿在修订包 PLAN.md，审计在 research/R2-*。

## 4. 主要文件位置（只读）

- 计划目录：`C:\Users\廖神\Desktop\Honor degree\projects\petct_textual_intent\protocols\petct-sirb-v2-referent-scope-plan-20261003\`
- ChatGPT 修订包：`C:\Users\廖神\AppData\Local\Temp\claude\C--Users----Desktop-Honor-degree\05dc1f8f-e2e5-4f75-95f9-1de19cf841e7\scratchpad\chatgpt-pkg\petct-sirb-v2-referent-scope-plan-20261003\`
- 本轮输入和输出：`...\scratchpad\r3\`
- vault（只在 wiki/ 里读）：`C:\Users\廖神\Desktop\Honor degree\knowledge-vault\wiki\`：hot.md；tasks/petct-t083-sirb-v2-mainline.md；tasks/petct-t080-sirb-locked-test.md；tasks/petct-t081-sirb-statistics-and-release.md；tasks/petct-t070-three-new-baselines.md；sources/petct-decision-register.md（D-2026-10-03-05、-03、-01，D-2026-10-01-02/03 等）；sources/petct-eval-results-register.md（TEST 成绩）；sources/petct-experiment-timetable.md；sources/server-usage-guide.md；sources/petct-sirb-master-plan-20260917.md；sources/petct-sirb-experiment-matrix.md；sources/petct-protocols-metrics-and-gates.md；sources/petct-canonical-project-contract.md。其他页用 index.md 找。
- 本机结果：`C:\Users\廖神\Desktop\Honor degree\projects\petct_textual_intent\records\development_results_transfer\`（VAL：eval-sirb-v2-quickval-*/six_state.csv、eval-sirb-batch1-val-20260925 等）；`records\eval_results_transfer\`（TEST）；`records\server_status\`；`records\editor-sirb-v2-batches\registry.tsv`。
- 代码（只读）：`projects\petct_textual_intent\scripts\common\petct_sirb_*.py`（网络、损失、执行器、机器人、角色、训练、数据）；上游代码 `projects\petct_textual_intent\upstream\`（含 2S-ICR、PRISM）。
- 文献 PDF：`C:\Users\廖神\Desktop\Honor degree\Thesis\sirb-research-20261003\`（401 个）。

## 5. 写法要求（导演全局规则，违反会被打回）

- 简体中文。结论先行。讲功能和方法（原本 X，现在 Y），不讲文件名函数名行号，除非是证据路径。数字给变化量并标 TRAIN/VAL/TEST。
- 英文术语第一次出现后面跟 5 到 15 字的人话解释（Dice、TEST、VAL、TRAIN、checkpoint、baseline、agent、JSON、git 不用解释）。
- 禁用词：席位、写权、读权、承重、承重清单、落盘、决策包、不自决、机器不自决、闸门、派工单、互盲、真相源、扇出、写入者、验收卡、计划卡、开工卡、机器契约；以及 值得注意的是、综上所述、总的来说、不难看出、由此可见、赋能、抓手、闭环、颗粒度、底层逻辑、沉淀、打通、助力、加持、拥抱、洞察、范式、重塑、解锁、全方位、多维度、至关重要、不可或缺、里程碑、革命性、显著提升。
- 不用“首先、其次、最后”或“第一、第二、第三”搭骨架；不给每段配总结句；长短句混用；少用破折号。
- 引用论文写清作者、年份、出处（会议/期刊/arXiv 号），原文关键数字写清实验条件。读到原文的标“原文核过”，只读摘要的标“摘要”，没核的标 UNVERIFIED。
- 不编造。拿不准就写拿不准。
