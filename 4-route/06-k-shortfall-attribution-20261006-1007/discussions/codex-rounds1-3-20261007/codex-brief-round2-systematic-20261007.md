# Codex 第二轮（同一会话接着问）：K 系列体系化归因，每个部件、每个网络、训练过程、损失、评测，全挖一遍（2026-10-07）

你仍是只读分析方。规矩同上一轮：不连服务器，不读 .env、私钥、凭据，不改任何文件，不打开影像、标注、掩膜、权重文件（.nii、.nii.gz、.npz、.npy、.pt）。可以读代码、配置、计划文档、成绩表（csv、jsonl、json）和训练记录。可以上网查文献（只读）。路径相对 `C:\Users\廖神\Desktop\Honor degree\`，代码树根是 `projects/petct_textual_intent/`。输出用中文，先给结论；每条说法写清证据（代码文件和行号，或数据文件和你算出的数），分清“已核实”和“推测”，不确定写“未核实”。数字一律标明是验证集（VAL）、测试集（TEST）还是训练日志诊断。

导演这次的原话要点：把 K 为什么没过线做成体系化的归因，“每个组件都挖，每个神经网络、每个组件对比，还有过程中的训练 loss、dice；各种组件训练方式、组件大小、优化步数、训练的 loss function、test 的方式”，能怎么归因就怎么归因，网上查有什么分析和归因的方法，最后给计划。导演关心科学依据、证据和挖下去效果能好多少，不关心流程严不严谨。

## 一、这一轮的材料（已全部拷进一个文件夹）

文件夹：`projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/`

- `data/val-and-train-results/`：本机 `records/development_results_transfer/` 的完整副本。重点：
  - K1 网络单独 VAL `eval-sirb-v3-quickval-INTENT_FULL-R1-20261006/`，K2 网络单独 `eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006/`，K2 加翻转 `eval-sirb-v3-quickval-flip-INTENT_REFRESH-R1-20261006/`（各有 six_state.csv、transitions.jsonl、remote.jsonl、trajectories.jsonl、latency.jsonl）。K1 加翻转今天 02:20 左右出，K3 两次 VAL 约 08:00、10:00 出，到时我补进同一目录。
  - v1 flat、v1 N3、理想修复参照（oracle）、不改（noop）：`eval-sirb-batch1-val-20260925/rollout/{N1_STATE-s3407,N3-s3407,oracle,noop}/`（三种画法都跑了；和 K 比时每扫描只取 K2 那一次用的画法，见 `stage2-20261007/b0_load.py`）。另有 morphology.jsonl。
  - 续训版、组 A、翻转、权重平均、空间支路、N3_ES 的快速 VAL（多数只有 six_state.csv）：`eval-sirb-v2-quickval-*`、`eval-sirb-v3-*`。
  - 基线各折 VAL：`baseline-2sicr-fold{0,1,2}-val-*`、`baseline-uam-fold{0,1}-val-*`。
  - 训练记录：v1 flat `train-sirb-formal-20260930/N1_STATE/`（metrics.jsonl、run_manifest.json、resolved_config.json），v1 N3 同目录 `N3/`；K1 `train-sirb-k-20261006/K1_INTENT_FULL/`，K2 `.../K2_INTENT_REFRESH/`，K3 到第 32,140 步左右的部分记录 `.../K3_INTENT_WIDE_partial-20261007/`（00:5x 从 A6000 读回，核过是服务器文件的前缀）；续训版 `train-sirb-v2-continuations-20261005/`；2S-ICR、UAM 的训练日志 `train-2sicr-epochs-20261005/`、`train-uam-logs-20261005/`。
- `data/test-results/`：本机 `records/eval_results_transfer/` 的完整副本（v1 的 TEST 在 `eval-sirb-lockedtest-20260928-R1/`，2S-ICR 第 0 折 TEST 在 `baseline-2sicr-fold0-test-R1/`）。只作背景，不用 TEST 挑方法。
- `data/configs/`：K1、K2、K3 的实验配置。`data/previous-analyses/`：10-03 到 10-05 计划调研的归档包（zip，不用解开也行）。
- `stage1-20261006/`：我们第一轮的脚本和输出（a1 到 a12，README-stage1.md 写了每个脚本看什么），你上一轮指出的错已改正写在那个 README 末尾。
- `stage2-20261007/`：这一轮的新脚本，`b0_paths.py`、`b0_load.py` 是共用读取，`b1_other_repair.py` 及输出 `b1_out.txt` 是刚算的。
- 计划正本：`projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/` 四份文件（PLAN.md 第零部分讲每个部件为什么加，`experiment-schedule-gpus.md` 第二部分是你第 11 轮的估计，`local-data-models-results.md` 是 v1 的丢分账，`literature-domains-review.md` 是 12 个领域的文献）。
- 代码：`scripts/common/petct_sirb_losses.py`、`petct_sirb_training.py`、`petct_sirb_dataset.py`、`petct_sirb_network.py`、`petct_sirb_inputs.py`、`petct_sirb_inference.py`、`petct_sirb_rollout.py`、`petct_sirb_roles.py`、`petct_sirb_executor.py`、`petct_sirb_registry.py`、`petct_sirb_refresh.py`、`petct_sirb_trajectory_bank.py`；评测入口 `scripts/evaluation/eval_petct_editor_sirb_rollout.py`；基线 `scripts/baselines/`。

## 二、到现在的事实（VAL，99 扫描/57 患者，Dice 分母 85 阳性扫描/54 患者，第五轮 Dice，起点 0.6095）

- K1 0.7539，K2 0.7529，K2 加翻转 0.7571；同口径 v1 flat 从零 40k 0.7562；判定线 0.79；理想修复参照 0.9180。
- 参数量（run_manifest）：K1、K2 6,652,475（主干 6,607,096，输出头 45,379）；K3 14,117,459（主干加宽 1.5 倍）。B6 标定的软 Dice 收益倍率 K1 0.463、K2 0.593、K3 0.299，其余新增项倍率 1。三者 `use_p0=false`。
- 你上一轮的结论和更正（见 `codex/codex-output-k-shortfall-20261007.md`，我们逐条核过）：加笔变保守、删笔变好、一正一负抵消；B1 新难负样本最可能是主因；B2 远端块只在约 0.13% 训练单元放下，可学半径 60→61 mm 没动；第 1 轮补齐 30 mm 内漏标理想上 +0.062，30 mm 外只 +0.015。
- 刚算的（`stage2-20261007/b1_out.txt`）：第 1 轮 54 个加笔，所指漏标合计 3107.8 ml，修回 v1 700.8、K1 369.4、K2 483.0 ml；别处同号漏标（O）修回只有 v1 7.6、K1 5.6、K2 3.0 ml；新增假阳性 v1 339.1、K1 62.7、K2 129.7 ml。后几轮加笔修回 O 也只有 v1 61、K1 52、K2 31 ml。所以“难负样本罚了 O、而 Dice 其实奖励修 O”这一条在量上不是主要丢分来源，差距主要在 T 本身补得少。

## 三、请回答（每题写结论、证据、强弱；能算的直接从文件算）

1. **逐部件归因总表。** 部件：B1a 边界排序、B1b 难负样本、B1c 修 O 不奖励的软 Dice 收益、B2 距离不截断＋可学半径＋远端块、B3 上一轮实际改动和交互标志、B4 固定教师状态池（按可挽回缺口抽样）、B5a 换笔换目标、B5b 同目标换画法、B5 第二笔的独立基础监督（它会进基础损失的平均）、B6 第 1000 步标定、K2 的在线刷新、K3 的加宽。每一项写：机制（代码位置）、原本想解决的痛点、预期效果、VAL 行为和训练日志里的实际证据、判定（帮了、拖了、没作用、无法判断）、证据强弱、最便宜的检验。能从现有数据拆的尽量拆（例如按轮次、按画法、按笔的关系、按所指错误大小和到笔距离、按病灶负荷分层），拆不开的写清还缺什么实验。
2. **训练过程全程对比。** 读 v1 flat、K1、K2 的完整 metrics.jsonl 和 K3 的部分记录，逐项比：每个损失项、每项梯度范数（注意记录的是未乘权重的梯度，见 `term_gradient_norms`）、各项乘权重后对总梯度的占比随步数怎么变、目标 Dice、T 召回、错误门召回、保留区误改、学习率、训练块里 T 的大小和到笔距离、远端块、配对种类、刷新前后的变化。要回答：K 和 v1 在哪一步开始分开；K 是没训够（还在涨）还是训偏了（早就平了）；K3 加宽在同步数上和 K1 比有没有不同；K2 两次刷新前后有没有跳变。能画成分段表就画分段表。
3. **网络大小和计算。** 从代码算出 v1、K1/K2、K3 各模块（状态主干、全局分支、融合、提示编码、B2 距离层、B3 历史通道、输出头）的参数量和输入通道，哪些输入其实是零（例如 p0），每步实际看到的体素块大小和数量，训练 40k 步共见过多少个训练单元、多少位病人、每位病人平均见几次；和 2S-ICR、UAM 比（参数量、训练轮数或更新次数、损失、输入、推理方式、是否整卷重预测）。2S-ICR 第 1 轮在共有扫描上涨 0.169、v1 涨 0.107，用代码和日志说明差在哪里。
4. **评测口径审计。** 我们的 VAL 和基线 VAL 的同与不同（机器人、画法分配、Dice、轮数、病人集合、起点掩膜）；翻转平均和组 A 怎么进评测；有哪些地方会让我们的 VAL 偏低或偏高；VAL 到 TEST 的平移（三个模型都 +0.013 到 +0.018）说明什么。
5. **方法和文献（请上网查，给出处链接和原文数字、条件）。** (a) 多部件训练配方的归因方法：消融设计（逐项去掉、因子设计、Shapley 式分配）、损失项梯度冲突度量（例如 PCGrad 的余弦、GradNorm 的相对比例）、表示相似度（CKA）、训练动态按样本分析（dataset cartography）、错误类型分解（检测里的 TIDE 那类）、反事实输入消融；哪些在我们的预算里做得到（一次从零 40k 约 20 小时 3090）。(b) 交互分割里加点和减点（正负点击）不对称、只改含点击那块的局部编辑（FocalClick 的 progressive merge 一类）、难负样本挖掘让模型变保守的证据、整卷重新分割式修正（2S-ICR、SAM 一类）、把上一轮概率图当输入（MFP 一类）、PET 病灶的交互分割（autoPET 交互赛道）。每篇写：做了什么、原文数字和条件、和我们的问题怎么对应、能迁移什么。
6. **下一步计划。** 现在能用的卡：z390 一张 3090 今天约 02:20 起空闲（一次 40k 约 20 小时，训练峰值约 12 GB，可以同卡再放一个评估，评估峰值约 4.7 GB）；A6000 GPU0 约 10-07 中午 K3 的两次 VAL 做完后按导演令接 UAM fold3；5090 跑 2S-ICR 到约 10-10。请排序：(i) 只去掉加笔的难负样本；(ii) 难负样本只罚 P（加删都这样，和 Dice 的账一致）；(iii) 软 Dice 收益改成也算修 O 的真 Dice，或去掉；(iv) 加笔也去掉边界排序；(v) 打开 p0 输入；(vi) 远端块改成按 T 内到笔距离分档放；(vii) B6 也标定惩罚项；(viii) 第二笔独立监督不进基础平均；以及它们的组合。每项写机制、证据、对 VAL 第五轮 Dice 增量的主观范围（标明主观）、风险、成本。请直接回答：只有一张卡时，下一个 40k 最该训哪个配方；有两张卡时训哪两个。注意导演的两条硬规矩：系数要学出来或按通用规则推出，不按 VAL 结果手定；最终模型和归因都从零训满 40k，续训不当证据。
7. **我准备在服务器上跑的不训练诊断，请审设计、挑最有信息量的、指出要改的地方。** D1：用 v1、K1、K2 的 final 权重，在 VAL 第 1 轮（三者起点和首笔相同）每个扫描算一次整卷 pT，按笔的符号、T/O/P、到笔距离分段存 pT 的直方图，从直方图算“门槛从 0.05 到 0.95 时各能修回多少 T、多改多少 P”，看 K 的能力是不是被 0.5 门槛挡住；同样做 TRAIN 的一批状态，供以后按通用规则定门槛。D2：在 final 权重上取一批 TRAIN 训练单元，分加笔、删笔，算每个损失项对输出 logit 的梯度在 T 内部、T 边界、O、P 上的方向和大小，以及每项梯度和“T 内平均 logit 的梯度”的内积（这一步沿该项下降，T 的 logit 会升还是降），也算各项参数梯度两两余弦。D3：五轮实跑“加笔用 v1、删笔用 K1（或 K2）”的按符号换模型系统。D4：K1 在自己的轨迹上把 B3 的上一轮改动和交互标志置零，看第 2 到 5 轮掉多少。D5：v1 和 K1 在同一批输入上各层特征的 CKA，看分歧在主干还是输出头。

写长一点没关系，表格多用。最后单列“我们的分析里还有哪些算错、拿错参照或漏看的地方”。
