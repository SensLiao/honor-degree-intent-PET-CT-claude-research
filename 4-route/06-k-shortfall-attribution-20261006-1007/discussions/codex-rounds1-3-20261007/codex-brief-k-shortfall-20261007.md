# Codex 只读交叉分析：SIRB 组合 K1、K2 为什么停在 v1 flat 的水平（2026-10-07）

你是只读分析方。不要连服务器，不要读 .env、私钥、凭据，不要改任何文件，不要打开任何影像、标注、掩膜文件（.nii、.nii.gz、.npz、.npy、.pt）。可以读代码、配置、计划文档、成绩表（csv、jsonl、json）和训练记录。路径相对 `C:\Users\廖神\Desktop\Honor degree\`，代码树根是 `projects/petct_textual_intent/`。

导演要的是科学上的原因和证据，以及往下挖能好多少；不要评流程严不严谨。输出用中文：先给结论，再分问题回答；每条说法写清证据（文件和行号，或数据文件和你算出的数），分清“已核实”和“推测”，不确定的写“未核实”。数字一律是验证集（VAL），不是测试集。

## 背景

- K 系列是按以前的分析拼出来的完整组合，从随机初始化训满 40,000 步（v1 配方：AdamW 2e-4、预热后余弦、种子 3407、flat 三分类头）。组 B 六个部件全开：B1 编辑合同（边界排序、难负样本、只奖励修所指那处的软 Dice 收益）、B2 到笔距离不截断加可学半径加远端训练块、B3 上一轮实际改动和交互标志作输入、B4 固定教师生成的状态池（按可挽回缺口抽样）、B5 块内配对（换笔换目标、同目标换画法）、B6 第 1000 步只给软 Dice 收益项标定倍率。K1 `INTENT_FULL`；K2 `INTENT_REFRESH` = K1 加第 10k、25k 步两次在线刷新状态池；K3 `INTENT_WIDE` = K1 加宽状态主干 ×1.5（还在训）。每个部件想解决的问题、来源和预期，见 `projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/PLAN.md` 第零部分、第三部分组 B，和 `experiment-schedule-gpus.md` 第二部分。实验配置 `configs/sirb/experiments/editor-sirb-intent{full,refresh,wide}-train.json`。
- 评测：VAL 99 扫描/57 患者，每扫描一种冻结画法，冻结机器人画五笔，每轮 0.5 阈值执行；Dice 分母 85 阳性扫描/54 患者，先扫描后患者等权。判定线是第五轮 Dice 0.79。

## 结果（验证集，第五轮 Dice，起点都是 0.6095）

- K1 网络单独 0.7539；K2 网络单独 0.7529；K2 加左右翻转平均 0.7571；K1 加翻转还在跑。
- 同口径参照：v1 flat 从零 40k 0.7562（09-30 完整 VAL 里每扫描取快速 VAL 分给它的画法）；v1 flat 续训 8k 的两个版本 0.7602、0.7606，续训版加翻转 0.7728。
- 理想修复参照（同一起点、同样的笔，把每笔所指的那块同号错误完全修好）0.9180。
- 已登记 TEST（测试集，只作背景）：v1 flat 0.7694，2S-ICR 第 0 折单折 0.8000。

## 我们已经算出的（请核对，有错直接指出）

材料：`projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/`（README.md、a1 到 a7 的脚本和输出）。原始成绩表在 `records/development_results_transfer/` 下：`eval-sirb-v3-quickval-INTENT_FULL-R1-20261006/`、`eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006/`、`eval-sirb-v3-quickval-flip-INTENT_REFRESH-R1-20261006/`（各有 six_state.csv、transitions.jsonl、remote.jsonl、trajectories.jsonl），v1 flat、理想修复、不改在 `eval-sirb-batch1-val-20260925/rollout/{N1_STATE-s3407,oracle,noop}/`（三种画法都有，比较时只取 K 那一种）。训练记录：K1、K2 在 `records/development_results_transfer/train-sirb-k-20261006/`（metrics.jsonl、run_manifest.json、resolved_config.json），v1 flat 在 `records/development_results_transfer/train-sirb-formal-20260930/N1_STATE/metrics.jsonl`。

1. 五轮增益按“这一轮是加笔还是删笔”拆开：v1 flat 加笔 +0.1302、删笔 +0.0165；K1 +0.0969、+0.0475；K2 +0.0857、+0.0577；理想修复 +0.2072、+0.1013。K 删笔变好、加笔变差，一正一负抵消。
2. 第 1 轮所有系统同一状态、同一笔（99/99 一致）：加笔修回所指漏标的中位数 v1 flat 57.9%、K1 19.7%、K2 18.7%；删笔误删真病灶 v1 flat 64.25 ml、K1 5.41 ml、K2 5.71 ml；加笔新增假阳性 v1 flat 339 ml、K1 63 ml、K2 130 ml。按所指漏标大小分档：小于 5 ml 的 26 笔，K 修回一半左右但第 1 轮 Dice 增益和 v1 flat 一样（约 +0.18）；5 ml 以上的 28 笔，K 只修回 4% 到 11%，v1 flat 18% 到 44%。
3. 第 1 轮加笔所指漏标体积 65.3% 在离笔 30 mm 外、42.0% 在 60 mm 外；三个模型在 30 mm 外只修回 2.3% 到 2.9%，60 mm 外 0.0% 到 0.3%。
4. 后几轮加笔修回不到 1% 的：v1 flat 1/189，K1 57/232，K2 40/212。
5. 训练记录：K 的错误门召回在头 1000 步（B6 标定之前）就只有 0.435，v1 flat 0.85；到 40k 时 K1 0.685、K2 0.665，v1 flat 0.884。所指错误召回 40k 时 K1 0.604、K2 0.576、v1 0.820，K 到 40k 还在慢慢涨。改到保留区的体素 K 约 35 到 43，v1 约 86。B6 标定结果：软 Dice 收益倍率 K1 0.463、K2 0.593，边界排序、难负样本、两项配对都保持 1.0。新增项 40k 时的大小：难负样本约 0.20、边界排序约 0.13、软 Dice 收益约 −0.05（乘倍率前）。远端训练块只在 4% 到 7% 的训练单元里放下。K 训练块里所指错误的体素数约是 v1 的 2 到 3 倍（目标更大更远，召回不完全同口径）。
6. 在线刷新（K2 减 K1）−0.0011；翻转只给 K2 加 0.0042。

## 请回答

1. 加笔变保守的根因。请读 `scripts/common/petct_sirb_losses.py`（ring_rank_loss、hard_negative_loss、soft_dice_gain）、`scripts/common/petct_sirb_training.py`（intent_parts、calibrate_dice_gain 和训练循环里新增项怎么加进总损失）、`scripts/common/petct_sirb_dataset.py`（角色 T/O/P 的定义、hard_preserve_region、采样配额、远端块）。重点：加笔时难负样本实际挑到的是哪些体素（O 里是否包括别处真病灶的漏标、P 里是否主要是 T 边界外一圈的“像病灶”的体素），数量按 |T| 取是不是过重；边界排序在 PSMA PET 边界模糊时会不会把填充往里推；B6 只缩小软收益、惩罚项保持 1.0，这个不对称会不会把平衡推向少改；头 1000 步错误门召回就只有 0.435，是 B1 惩罚、B2 改了目标定义（T 变大变远）、B3/B4/B5 里哪一个更可能。给出你认为的主因和次因，各自的证据强弱。
2. B2 为什么没有带来远处修补：远端块的放置概率（T 在锚点块外的体积占比）在训练中只有 4% 到 7% 生效；推理时整卷各块共用锚点块算出的同一个查询，未截断距离和可学半径怎样进入网络。有没有实现或设计上的原因让网络在离笔 30 mm、60 mm 外几乎不可能输出高 pT（例如距离编码、半径参数、采样里 30 mm 包络、近 75% 远 25% 的负样本配额、锚点块大小）。请给出具体代码位置。
3. 删笔变好更可能来自哪个部件（B1 的难负样本或边界排序、B3 的上一轮实际改动、B4 状态池），证据是什么。
4. 往下怎么改效果最大。至少比较这几类，每类写机制、证据、对 VAL 第五轮 Dice 增量的主观估计范围（标明主观）、最便宜的验证办法（不训练或只要几小时 GPU 的诊断优先；我们现在一次从零 40k 要 17 到 24 小时 GPU）：
   (a) 保住删笔、找回加笔：例如 B1 惩罚只对删笔生效，或难负样本排除同号漏标、按比例而不是按 |T| 取，或 B6 对惩罚项也标定；
   (b) 执行端的校准：加笔和删笔用不同阈值、或按 TRAIN 回放学出的规则定（导演要求系数要学出来或按通用规则推出，不按结果手定）；
   (c) 远处补全：例如加笔时沿网络或分割基座概率在所指连通区域内扩展、2S-ICR 式整卷重预测、训练里提高远端块比例；
   (d) 其他你认为证据更强的方向。
   另请估计：只做 (a) 能不能到 VAL 0.79；要到 0.85 至少需要哪几项。
5. 我们的分析里有没有算错、拿错参照或漏看的地方（比如“v1 flat 的加笔加 K 的删笔约 0.787 到 0.797”这种简单相加的粗算）。
