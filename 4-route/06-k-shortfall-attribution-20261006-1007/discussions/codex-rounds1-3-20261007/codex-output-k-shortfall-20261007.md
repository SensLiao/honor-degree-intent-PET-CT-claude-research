我的判断是：**K1、K2 主要把“别改错”学强了，却没有同时学会“把所指漏标补全”。最值得先查的是 B1 新增难负样本造成的加笔抑制；B2 的远端训练设计则几乎没有触发，未能解决原有的远处补全问题。** B6 可能加重了这种失衡，但不是前 1000 步召回下降的起因。B3、B4、B5 各自贡献多少，目前不能从这两个完整组合中分离出来。

这次复算还发现两处明确错误：远端块触发率实际约 **0.13%–0.14%**，不是 4%–7%；第 1 轮加笔恢复率的标准中位数应为 **v1 53.7%、K1 17.5%、K2 18.4%**。这些修正不推翻“加笔变差、删笔变好”的现象，但会改变下一步的优先级。

下面所有模型成绩、收益和反事实数字均为 **VAL**。训练字段单独称为“训练日志诊断”，不能当作 VAL 成绩。

我从原始表重算出的主结果如下。增益仍按每条轨迹实际发生的加笔、删笔记账，先扫描、后患者等权：

| 系统 | 第五轮 Dice | 五轮加笔贡献 | 五轮删笔贡献 |
|---|---:|---:|---:|
| v1 flat 40k | 0.75615 | +0.13019 | +0.01650 |
| K1 | 0.75393 | +0.09693 | +0.04754 |
| K2 | 0.75287 | +0.08567 | +0.05773 |
| K2 加翻转 | 0.75705 | +0.09515 | +0.05243 |

这部分与你们的分析一致，患者配对重抽区间也复现了。证据为各运行的 `six_state.csv`、`transitions.jsonl`；聚合方式见已复核的 [a2_rounds.py:62](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/a2_rounds.py:62>) 和 [a6_boot.py:18](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/a6_boot.py:18>)。

1．加笔变保守的根因：我把 B1 的新增难负样本排第一，但“已核实的机制”与“尚未隔离的因果”需要分开。

T/O/P 的实际定义没有含糊之处：

| 角色 | 加笔时 | 删笔时 |
|---|---|---|
| T | 笔碰到的漏标错误连通块 | 笔碰到的多分错误连通块 |
| O | 其余漏标真病灶体素 | 其余多分体素 |
| P | 当前没分出来、真值也为背景的体素 | 当前已经分对的真病灶体素 |

这里的 O 不一定是另一处解剖病灶，也可以是同一病灶中、被当前正确分割部分隔开的另一块漏标。它按“同号错误连通块”划分。证据：[make_roles:100](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_roles.py:100>)。

加笔时，B1 新增难负样本确实会处罚这些 O。它在两个监督块去重后的 **全部 O∪P** 中，按当前 `pT` 从高到低选出最多 `|T|` 个体素，最小化其平均 `−log(1−pT)`。它不受原有分类采样配额或 30 mm 包络限制，是叠加在原损失之上的一项。与此同时，软 Dice 收益对修 O 完全中性，既不增加分子，也不增加预测体积。证据：[hard_negative_loss:338](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_losses.py:338>)、[soft_dice_gain:371](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_losses.py:371>)。

这说明训练目标更强调“只修所指那处”。但 **“O 是漏标真病灶”并不自动证明这是错误监督**：按当前指代任务，O 本来就不应被这笔修改。真正需要查的是，这项额外约束是否通过共享特征，同时压低了 T 内那些边界模糊、距离较远的体素。现有结果与这个解释相符，尚无单项消融证明它。

另一个需要纠正的理解是：**按 `|T|` 取样，不等于损失随 `|T|` 线性变重。** 代码最后除以实际选中数量，得到的是均值。直接把选取数量改少，可能只剩下最难的几个负样本，平均处罚反而更强。因此，我更倾向先拆分 O 与 P 的处罚、检查实际梯度，而不是只缩小 top-k 数量。

你问 P 是否主要是 T 边界外一圈“像病灶”的体素：**未核实实际比例。** 两种采样不能混为一谈：

- 原有基础损失的加笔困难 P，在 T/笔周围包络内按基座概率 `p0` 加权抽样。
- B1 新项直接按网络当前 `pT` 排序，候选来自全部监督块；它可能集中在边界，也可能落在远处高摄取背景。

现有日志没有保存选中体素的 O/P 构成、距离或边界占比。证据：[sample_classification_mask:478](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_dataset.py:478>)。

比“损失值 0.20 大于 0.05”更有力的证据，是训练记录里已经保存的梯度。对第 10k–40k 步的 150 次梯度探针，我重新聚合如下；已乘实际训练倍率，没有该配对项的探针按零计：

| 损失项的梯度范数均值 | K1 | K2 |
|---|---:|---:|
| 原有 target Dice | 6.17 | 6.48 |
| 新增难负样本 | 14.79 | 14.99 |
| 边界排序 | 3.35 | 2.89 |
| 新增软 Dice 收益，乘 B6 倍率后 | 0.53 | 0.79 |
| 同目标、不同画法的一致性项 | 3.89 | 3.92 |

这些是训练日志诊断，来源为 [K1 metrics.jsonl](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-k-20261006/K1_INTENT_FULL/metrics.jsonl>)、[K2 metrics.jsonl](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-k-20261006/K2_INTENT_REFRESH/metrics.jsonl>)；代码明确这些梯度在记录时未乘损失权重：[term_gradient_norms:562](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:562>)。它们支持“额外约束有很强的优化影响”，但没有按加、删笔拆分，也没有梯度夹角，**不能直接证明难负样本正在反向抵消 target Dice**。

边界排序是次一级嫌疑。它最小化 `softplus(sP−sT)`，会同时抬高 T 内侧、压低 P 外侧，公式本身没有要求边界内缩。在图像特征无法清楚区分边界两侧时，它可能与其他处罚共同形成过度保守的边界；但本次没有打开影像，也没有边界不确定性统计，所以“PSMA 边界模糊导致内缩”仍是推测。证据：[ring_rank_loss:316](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_losses.py:316>)。

B6 的不对称确实存在，但要准确描述：它缩小的是**同时包含补对收益和改错代价的软 Dice 项**，并非一个纯奖励项。K1、K2 的倍率为 0.4629、0.5926，其余新增项保持 1。当时用四个单元将该项梯度对齐原 target Dice，因此倍率小于 1 本身不代表标定方向错误；后续日志说明，这次对齐没有维持整个训练期的相对量级。证据：[calibrate_dice_gain:1112](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:1112>)、[K1 标定记录](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-k-20261006/K1_INTENT_FULL/run_manifest.json:213>)。

我对根因的排序是：

| 候选原因 | 判断与证据强度 |
|---|---|
| **B1 新增难负样本** | **最可能的主因，证据中等偏强。** 从开训即生效；早期和后期梯度都很强；VAL 同起点首笔呈现“恢复少、误改也少”。缺少按符号消融与梯度方向证据。 |
| **B4 改变状态分布，加上 B5 改变监督组成** | **重要次因，证据中等。** K 的训练目标更大、状态更难；B5 还把第二笔作为额外独立监督加入基础损失，基础损失随之重新取平均，训练诊断也包括这笔。不能把召回差全部解释为网络退化。 |
| **B6 一次标定后的相对失衡** | **可能放大上述问题，证据中等。** 不能解释标定前已经出现的差距。 |
| **边界排序、B5 一致性约束** | **可能参与，尚未隔离。** 后期梯度不可忽略，但边界排序并非单向压低 T，一致性项也不直接奖励统一缩小两张概率图。 |
| **B3 历史输入** | **作为首轮保守的主因，证据较弱。** 首轮没有上一轮实际改动；轮次标志仍可能影响输出，所以不能完全排除。 |

B5 的额外监督及重新平均见 [group_b_terms:426](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:426>)、[unit_loss:492](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:492>)。

前 1000 步的错误门召回均值确实约为 K1 0.4346、K2 0.4351、v1 0.8508。但 **B2 没有改变 T 的定义**，三者仍调用同一个 `make_roles`；改变的是状态、监督块和额外笔的组成。K 在这段日志中的平均 T 体素数约 468，v1 约 201，因此这组训练召回不是同一批目标上的比较。它能说明问题早于 B6，不能单独在 B1、B4、B5 之间定案。

2．B2 没带来远处修补，最明确的问题是“远端”的触发条件没有对准实际缺口。

**已核实：新增远端块的真实触发率是 K1 103/80,000＝0.12875%，K2 114/80,000＝0.14250%。**

`far_block_placed` 在单元内记录 0/1，写日志时按窗口求和。每条日志是 20 个更新步，每步两个训练单元，所以一条日志对应 40 个单元。把日志中平均 0.04、0.07 直接当成 4%、7%，漏除了 40。证据：[训练事件记录:610](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:610>)、[窗口聚合:662](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:662>)，分母和总次数来自上述完整训练记录。

这里说的是 **B2 新增的远端替换块**，不是说只有这些单元看到了离笔较远的 T。原来的锚点块、第二块也可能包含远处目标。

触发为什么这么少，代码给出一个合理解释：配置是 3 mm 网格、`96³` 块，块边长约 **288 mm**；B2 判断的是“T 有没有跑到这个大块外面”，不是“离笔超过 30 mm 或 60 mm”。一个离笔 80 mm 的漏标仍很容易待在锚点块里面，完全不会触发新增远端块。锚点选择还优先让笔靠近块中心。证据：[实际几何配置:436](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-k-20261006/K1_INTENT_FULL/resolved_config.json:436>)、[far_block_origin:679](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_dataset.py:679>)、[select_anchor_tile:292](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_geometry.py:292>)。

距离进入网络的方式也比“未截断距离直接作用于输出”更有限：

- 原始毫米距离先变成 `max(1−d/R, 0)`；`R=60×exp(s)`，其中 `s` 是**全模型共享的一个可学标量**，不是每笔独立预测的半径。
- 对 `d>R` 的体素，这个距离变换关于 R 的直接梯度为零。远端体素不能通过自己这条通道直接要求半径长大。
- 另有 `log(1+d/体素边长)` 通道，通过零初始化的 `1×1×1` 层接入输出头，确实保留了远端距离信息。
- 实际训练结束时 R 是多少，日志没有记录；按本次限制未读取 checkpoint，因此 **未核实**，不能说它“学成了 30 mm”。

证据：[距离输入:186](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_inputs.py:186>)、[可学距离变换:436](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_network.py:436>)。

30 mm 包络和“近 75%、远 25%”**没有截断 T，也没有限制输出范围**。包络围绕的是 `T ∪ 笔`，因此一个离笔很远的 T 体素仍在包络内；全部可见 T 都参与分类监督，75/25 主要分配 O/P 负样本。不能把“30 mm 外修不好”直接归因于这条采样边界。证据：[包络构建:943](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_dataset.py:943>)、[分类采样:478](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_dataset.py:478>)。

推理确实遍历整卷，各块共用锚点生成的同一个查询。问题在于：当前笔在状态主干之后才进入，主要通过查询与体素特征匹配、距离和局部 `1×1×1` 输出头影响结果；B2 没有新建一条沿病灶空间连续传播提示的路径。**这可能形成强烈的局部偏好，但没有代码把 30/60 mm 外的高 pT 变成数学上的不可能。** 证据：[输出头:419](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_network.py:419>)、[整卷查询复用:357](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_inference.py:357>)。

3．删笔变好，我更倾向于 B1 的保留约束，其次才是 B4；B3 的独立贡献未核实。

首轮 31 笔删除中，v1、K1、K2 的误删真病灶体积分别为 **64.25、5.41、5.71 ml**。这时还没有上一轮实际改动可供 B3 使用，因此“记住自己上一轮改了什么”不能直接解释首轮的大幅改善。B3 的轮次标志仍在，不能把整个 B3 判为零作用。证据为三个运行的 `transitions.jsonl`，首轮输入定义见 [interaction_fields:116](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_rollout.py:116>)。

B1 的机制很符合这个现象：删笔时 P 就是真病灶，新增难负样本专门压低“最容易误删”的 P；边界排序把要删的 T 与相邻正确 P 分开。不过，原有 `hard_preserve_region` 在 v1 已经存在，不能把它当作 K 新增的有效部件。K 新增的是其上的动态难负样本、排序和软收益。证据：[hard_preserve_region:594](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_dataset.py:594>)。

“删笔变好”也需要保留一个限制：**K 同时删少了该删的部分。** 首轮所指多分恢复体积从 v1 的 **182.42 ml** 降到 K1 **66.94 ml**、K2 **72.07 ml**。首轮删笔对全体患者 Dice 的贡献只从 **+0.02245** 提高到 **+0.02596、+0.02476**。这更像是精度提高、覆盖减少，不是删除能力全面增强；五轮较大的删笔收益差还包含后续状态与选笔变化。证据：[首轮与逐轮原始汇总](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/a2_out.txt:39>)，数值已独立复算。

B4 让模型见到教师实际产生的错误，因此可能帮助学习保护真病灶；B3 可能帮助后续纠错。这两种解释都有机制合理性，目前没有单独证据能排在 B1 前面。

4．往下改，我建议先恢复近处加笔，再决定远端补全需要多大改动。

这里有一项比漏标体积占比更直接的新计算。我用已存的病灶体积、FP/FN 计数及 `remote.jsonl`，计算了首轮的理想反事实：**保留模型本次所有编辑，只把指定距离内尚未修回的 T 完全补齐。**

| 理想操作，仅第 1 轮 | K1 的患者平均 Dice 增量 | K2 的患者平均 Dice 增量 |
|---|---:|---:|
| 补齐离笔 ≤30 mm 的剩余 T | **+0.06191** | **+0.06387** |
| 补齐离笔 >30 mm 的剩余 T | +0.01479 | +0.01493 |

计算前，我用这些体积计数重建了四个系统共 2040 条阳性状态的 Dice，最大绝对误差为 `4.44×10⁻¹⁶`。加笔反事实采用 `2(I+x)/(M+G+x)`，其中 x 是该距离范围内尚未补回的 T。来源为 [K1 结果目录](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/eval-sirb-v3-quickval-INTENT_FULL-R1-20261006>)、[K2 结果目录](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/eval-sirb-v3-quickval-INTENT_REFRESH-R1-20261006>) 与 [oracle 结果目录](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/eval-sirb-batch1-val-20260925/rollout/oracle>) 中的 `six_state.csv`、`trajectories.jsonl`、`transitions.jsonl`、`remote.jsonl`。

**这是用了真值计数的首轮理想空间，不是可实现成绩，也不能直接加到 D5。** 但它说明：65.3% 的漏标体积在远处，不代表远处占 65.3% 的患者 Dice 改善空间。当前最值得先救的是近处没有补好的 T。

下面的增量范围均为**主观估计**，以 K1/K2 网络单独约 0.753 为基点；不是置信区间，各方向存在重叠，不能相加。诊断成本也是估计，均指后续由执行方开展的工作，本次没有运行。

| 方向 | 我建议的具体改法及依据 | 对 VAL D5 的主观增量 | 最便宜的验证办法 |
|---|---|---:|---|
| **(a) 保住删笔、找回加笔** | 优先在 ADD 撤去新增难负样本，或让新增项只处罚 P；保留原 binding 对 O 的约束和软 Dice 收益。先别把整个 B1 一起关掉，也别先假定排序一定有害。依据是首轮 T 恢复下降、强难负梯度及近处理想空间。 | **+0.010～+0.035**；乐观情形可到 +0.04 左右 | 固定同一批 TRAIN 状态，按符号量各项对 T 内部、T 边界、O、P 的梯度方向，约几十分钟至 1 小时 GPU；再做两条从零前 2000 步的机制诊断，约 2～3 小时 GPU。 |
| **(b) 按加/删笔学习执行阈值** | 新增排序、困难采样后，pT 未必仍是适合统一 0.5 决策的概率。用 TRAIN 回放学两个阈值，或很小的校准模型；选择依据来自 TRAIN 的患者收益，不手定 ADD=某个数。 | **0～+0.020**；也可能无收益或变差 | 固定模型，在少量 TRAIN 状态导出按符号、距离划分的分数—恢复—误改曲线，约 1～3 小时 GPU；确定候选后才跑五轮，因为单笔最优不保证 D5 最优。 |
| **(c1) 让训练真正覆盖离笔远的 T** | 第二块按 T 内到笔距离的分位数分层覆盖，取消“必须出了 288 mm 锚点块才有机会补块”的触发依赖。保持总块数，仍给 O/P 监督。 | 单独 **0～+0.025** | 先统计现有训练单元中 T 的距离覆盖与对应召回；再以相同状态做短程对照。不能只看 `far_block_placed`。 |
| **(c2) 用分割提议补全，再约束所指范围** | 将“哪里像病灶”和“这笔指哪处”分开：由分割概率或提示条件化解码器给出完整提议，再选择与笔对应的部分。单纯扩张现有低 pT 区域不一定够。 | **−0.010～+0.060**，不确定性最大 | 先在相同 TRAIN 状态比较候选提议的真实可恢复空间；若候选本身没有空间，不训练选择器。初筛约数小时 GPU，完整训练另算。 |
| **(d) 加笔用 v1、删笔用 K 的固定路由** | 按笔符号选模型，是最直接检验“两边优势能否共存”的方法；规则来自已知动作语义，没有手调系数。 | **−0.010～+0.035** | 不训练，实际跑混合系统五轮。每轮只调用一个模型；不能用已有贡献表代替这次回放。 |
| **继续加宽、延长原配方或增加刷新** | 当前证据弱于上述方向。刷新系统差接近零；延长原配方的历史增益约 0.004；加宽也不会自动消除错误的优化偏好。 | 暂按 **−0.005～+0.010** 看待 | 先读 K3 的同口径结果，再决定是否投入下一次 40k。 |

对 (a)，我不建议简单“所有惩罚项都拉到同一梯度大小”。现有 B5 一致性项已经不弱，再放大可能引入新问题。更有信息量的是按加、删笔测梯度方向，再以 TRAIN 的收益选择相对权重。

对 (c2)，SIRB **已经是整卷分块推理**，所以需要借鉴的并非“把整卷算一遍”这件事。2S-ICR 的区别在于：把连续的上一轮分割概率和提示一起送入修正网络，重新预测分割；本项目代码也确实这样连接输入。证据：[2S-ICR 训练输入:687](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/baselines/train_psma_2sicr_refine.py:687>)、[原论文方法](https://pmc.ncbi.nlm.nih.gov/articles/PMC12325674/)。这支持尝试“完整分割提议＋指代选择”，不支持直接承诺它在本项目能带来多少分。

另一个容易漏掉的事实是：**K 的网络实际不读取 p0，输入通道被置零**，虽然基础困难采样仍使用 p0。让分割基座概率参与补全是一个真实的新信息来源，不是当前网络已经利用过的能力；其增益未核实。证据：[运行配置 use_p0=false](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-k-20261006/K1_INTENT_FULL/run_manifest.json:197>)、[输入置零:621](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_network.py:621>)。

只做 (a) 能不能到 0.79？**有可能，但我不会把它作为最可能的必达结果。** K1 需要 +0.03607、K2 需要 +0.03713；这已接近“完整追回 v1 的加笔优势，同时不丢 K 的删笔收益”的幅度。我的主观预期更接近先到 **0.77～0.79**，再由执行校准或补全改进决定能否稳定越过 0.79。

到 0.85，K1 需要 **+0.09607**，相当于追回它与 0.91796 理想参照差距的约 **58.6%**。目前没有证据支持仅靠损失倍率、翻转或多训实现这个量级。我认为至少要同时取得三种能力上的改善：近处加笔明显补全；大目标和后续续修不再反复停住；在提高覆盖时仍保住删除的低误伤。具体由哪些部件实现尚未核实，但仅恢复到 v1 的加笔水平，幅度明显不够。

5．你们的分析里，需要修正的主要是这些地方。

- **中位数确实算错了。** `a2_rounds.py` 用 `sorted(ratios)[len(ratios)//2]`，54 笔时取上中位数，没有平均中间两个值。标准结果为 v1 **53.70%**、K1 **17.46%**、K2 **18.43%**，而非 57.9%、19.7%、18.7%。证据：[a2_rounds.py:102](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/a2_rounds.py:102>)，由三个运行的首轮 `transitions.jsonl` 重新计算。

- **小于 5 ml 那档“和 v1 一样”只适用于 K1。** 26 笔的扫描平均首轮 Dice 增益是 v1 **+0.18010**、K1 **+0.17814**、K2 **+0.13827**。这段原脚本只打印了 v1 和 K1 的 Dice，没有打印 K2；而且该段用的是扫描均值。改成该子组内患者等权后，分别为 **+0.15390、+0.15171、+0.11929**。证据：[a3_patients.py:78](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/a3_patients.py:78>)。

- **“99/99 首笔一致”要写成“99 个起点一致，其中 85 个有首笔、14 个无笔”。** 我核对了 99 个起始预测哈希，全部相同；首笔符号、目标体积也相同。原 a2 只检查符号和体积，并没有逐体素比较笔迹。本次也没有打开笔迹数组；同笔判断还有冻结机器人和相同输入的代码支持。证据：[a2 的实际检查:109](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/a2_rounds.py:109>)、[冻结机器人调用:280](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_robot.py:280>)。

- **0.9180 不是沿 K 原五笔计算的理想结果。** 它从相同起点出发，每轮修好后，由机器人在自己的新状态上重新画下一笔。到了第二笔，K1 与 oracle 连“符号＋目标体积”都只剩 **45/99** 一致。因此它是同机器人协议下的理想修复参照，不能写成“同样五笔完全修好”的结果。证据来自各运行 `transitions.jsonl`，状态推进代码见 [run_trajectory:194](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_rollout.py:194>)。

- **0.7872、0.7974 的简单相加算术没错，解释不能越过数据。** 它们确实等于起点＋v1 加笔贡献＋K1/K2 删笔贡献，但来源是不同状态、不同后续笔的轨迹，既不是混合模型成绩，也不是严格上限。首轮可以直接拼，因为状态相同：v1 加笔＋K1 删笔的 D1 为 **0.69832**，比 K1 原 D1 **0.69164** 高 **0.00668**；后四轮必须重新运行才知道。

- **“在线刷新贡献 −0.0011”应改为“K2−K1 的观测系统差为 −0.0011”。** 我重算的患者配对 95% 区间为 **[−0.0121，+0.0095]**；而两者 B6 倍率在刷新前已经不同，不能把整个差值完全归给刷新。K2 翻转增量 **+0.00419** 的对应区间为 **[−0.0040，+0.0131]**，目前也不能证明稳定增益。原始数据为 K1、K2、K2 翻转各自的 `six_state.csv`。

- **末段训练数字有几处小偏差，且“还在涨”应收紧。** 按最后 2000 步统一重算，T 召回为 K1 **0.6021**、K2 **0.5772**；保留区误改体素为 K1 **42.10**、K2 **35.32**、v1 **78.93**。K1 的 T 召回在 30k–32k 为 **0.6015**，末 2k 为 **0.6021**，已相当平缓，不能据此预言再训会明显涨 VAL。证据：[完整末段训练汇总](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/analysis-sirb-k-val-shortfall-20261006/a4_out.txt>)及完整 `metrics.jsonl`。

我会优先让执行方做 **ADD 难负样本的梯度诊断、按符号的分数校准诊断，以及 v1-ADD/K-REMOVE 的真实五轮混合回放**。它们分别回答“是不是损失压住了 T”“是否已有能力被 0.5 阈值挡住”“两边优势到底能不能共存”，比再投入一个完整组合更快缩小原因范围。