# Codex 第三轮（同一会话接着问）：三项诊断的结果、K4 改法，请审读数和下一步（2026-10-07 早上）

规矩同前两轮：只读；不连服务器；不读 .env、私钥、凭据；不改文件；不打开影像、标注、掩膜、权重（.nii、.nii.gz、.npz、.npy、.pt）。中文，先结论；每条写证据（文件和行号，或数据文件和你算出的数），分清已核实和推测；数字标 VAL / TRAIN / 训练日志诊断。

## 这一轮新出的东西（都在 `projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/`）

1. D3 按笔方向换模型的五轮 VAL 回放（加笔用 v1 flat、删笔用 K2，网络单独）：原始表在 `server-diagnostics/z390-queue-diag-1007/diag-routed-v1add-k2remove-val/`，读数脚本 `stage2-20261007/f2_routed_rollout.py`，输出 `f2_out.txt`。要点：D1 0.6971（各系统最高），D5 0.7472，比 v1 低 0.0090［−0.025, +0.006］；后几轮删笔只清掉 551 ml 多分（v1 自己 1016 ml），删笔 199 轮、加笔 220 轮。我的解读：v1 加笔留下的多分，K2 的谨慎删笔清不掉，机器人后几轮多在画删笔，两边长处不能直接叠加。
2. D1 第 1 轮整卷分数分布（v1、K1、K2、K1 第 1 万步、第 2 万步，VAL 第 1 轮，同起点同笔）：`server-diagnostics/z390-queue-diag-1007/round1-score-histograms.jsonl`，读数 `stage2-20261007/f1_round1_thresholds.py`，输出 `f1_out.txt`（门槛扫描、按距离分段的修回、e 和 pT 的分解、T 边界/内部和 P 外圈）。
3. D2 每项损失对 T 分数的推拉方向（48 个固定 TRAIN 单元，v1 加 B1 项打分、K1 最终和第 5000 步、K2）：如果已出，在 `server-diagnostics/z390-d2-1007/d2-term-gradient-influence-train48.jsonl`，读数 `stage2-20261007/f3_gradient_influence.py`、输出 `f3_out.txt`；没出就跳过这一项。代码在 `scripts/evaluation/gen_petct_eval_sirb_term_gradient_influence.py`。
4. K4 的改法（D-2026-10-07-01，`knowledge-vault/wiki/sources/petct-decision-register.md` 顶部）：原定“难负样本只用在删笔上”（`configs/sirb/experiments/editor-sirb-intent-hardneg-remove-train.json`），看到 D3 后改成“只用在删笔上、而且只罚掩膜里的真病灶 P，不罚别处同号的错 O”（`editor-sirb-intent-hardneg-remove-preserve-train.json`，开关实现在 `scripts/common/petct_sirb_registry.py`、`petct_sirb_losses.py`、`petct_sirb_training.py` 的 group_b_terms）。理由：按 Dice 的账，删笔删掉真病灶每体素约亏 (2−D)/S，误加背景约亏 D/S，改到别处同号的错反而加分；D3 显示 K 式删笔太谨慎。K4 10-07 早上在 z390 开训，40k 约 20 小时。
5. K4 前 800 步的训练日志（`server-diagnostics/z390-queue-k4-1007/train-early/metrics.jsonl`，读数 `stage2-20261007/g1_k4_early.py`、输出 `g1_out.txt`）：错误门召回第 400 步 v1 0.809、K1 0.135、K4 0.464，第 800 步 0.819、0.410、0.647；目标召回第 800 步 0.661、0.265、0.462。D2 在 z390 和 K4 同卡显存不够（OOM），改在 5090 跑，约 06:40 出，结果文件会出现在 `server-diagnostics/z390-d2-1007/`；你读的时候如果还没有就跳过。
6. 第一、二轮的全部结论和四份报告在 `reports/`（`1-overview-and-plan.md` 是总览）。

## 请回答

1. D3 的解读站不站得住？特别是“删笔太谨慎导致多分清不掉、机器人把轮次花在删笔上”这条因果链，用 transitions.jsonl 能不能再核实（例如按轮次看机器人画删笔的比例、删笔目标体积是不是一直在同一块多分上、每笔清掉的比例）。有没有别的解释（例如 K2 读 B3 输入时，上一轮改动来自 v1，分布外）。
2. D1：K 的加笔是“分数整体偏低、排序还在”还是“排序也坏了”？请从直方图算一个和门槛无关的量（例如加笔时 T 对可改正确区 P 的 AUC，或 T 和 P 分数分布的重叠），比较 v1、K1、K2 和 K1 第 1 万、2 万步。v1 在第 1 轮两个方向都偏“改多了”（VAL 上门槛往高挪有好处）、K 两个方向都偏“改少了”，这个读法对不对；门槛能收回多少（只在第 1 轮，标明是 VAL 上看的，不能当方法值）。
3. D2（如果已出）：难负样本对 T、T 边界、P 外圈的推拉方向和大小；它在 O 上把概率推给了谁（看 cos 和 influence 能推到哪一步）；这能不能支持或推翻“难负样本经共享参数压低 T”。
4. K4 改成“删笔只罚 P”是否合理？和原定 K4 比，你预计哪一个更可能涨；它有没有新的风险（例如删笔又开始误删真病灶，或加笔外溢变大、清不掉）。K4 出数后（约 10-08 早上）怎么读：给出两三条事先写下的判读标准（看哪几个数说明改法起作用）。
5. 下一步（K4 训练期间能做、不占 z390 的，和 K4 出数后的）：执行端按方向的门槛如果在 TRAIN 上学（我已写好 `scripts/evaluation/fit_petct_sirb_sign_thresholds.py` 和 `eval_petct_editor_sirb_sign_threshold_rollout.py`），值不值得做、该怎么学才不算按 VAL 手定；远端补全、基座概率图输入、2S-ICR 式整卷重预测，哪个对 0.79 以上最关键。
6. 我们这一轮的分析里有没有算错、读过头的地方。
