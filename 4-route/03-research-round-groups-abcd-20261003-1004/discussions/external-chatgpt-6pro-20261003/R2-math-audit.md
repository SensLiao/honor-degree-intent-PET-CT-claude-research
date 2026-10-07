# R2 数学、候选决策与连通模块独立审查

日期：2026-10-03（UTC 调研开始于 2026-10-03）。本报告读过 PLAN.md、L1-propagation-math.md、L2-decision-thresholds.md、S2-causal-map.md、codex-round6-answer.md，并对 R2-synthesis-draft.md 做第二轮数学复审。未访问生产服务器，未改生产代码，未重跑 VAL/TEST。

本路核查 **28 篇原始来源**：26 篇读到原文中与本任务有关的方法、定理或结果段；FFN 与层次分割 UCM 只成功读到出版方／作者机构摘要及部分图注。不是声称 28 篇逐字通读，也不是把这 28 篇都算作此前文献库之外的新论文。逐篇 URL、访问深度和可迁移边界在 R2-math-papers.json；文末有便于阅读的索引。

## 1. 结论及本轮唯一主推

**继续做“候选执行器 + 直接空间和保持监督 + 当前联合策略状态”，但把真实效果与指代保持分成两本账。** 当前最小可靠设计是两个小回归器：一个预测原生实际写回后的整例 Dice 变化 g；另一个预测该候选在 O 和 P 上造成的未授权编辑量 b。在同一当前状态下，先要求预测 b 不超过该 checkpoint 原 0.5 执行候选的预测 b，再在剩余候选与 no-op 中选预测 g 最大的。原来的 T/O/P 监督继续是任务定义，不因全局 Dice 选择器而删除。

这是一条**相对原执行器保持范围、争取更高真实 Dice**的经验决策规则，不是零越界保证，也不是证明最优的策略。它只比原有的 Dice 回归树多一个同量级的树模型，不引入新半径、手扫风险容差或奖励惩罚系数。参考原执行器本身是明确的设计选择，不能包装成“数学唯一推出”。

不采用本轮讨论过的两个替代标量作为 A/B 的共同主目标：

- 不用 Dice(M_A,Y*) 替换原生 Dice，其中 Y* 是当前 M 只在 T 上理想修正得到的伪目标。它改变了前景基数和错删／漏修的相对价格，且可能产生空目标平台。
- 不把 U_T=g−2o/(B±k) 同时塞进选择器和软损失。它是人为规定“把 O 当错误编辑收费”的效用，不是 Dice 差；REMOVE 极端状态下可远小于 −1，数值尺度也不再受 Dice 的范围约束。

原有 B 的“在软收益项里固定 O、不奖励 O + 原 T/O/P 绑定”可以保留为便宜而诚实的折衷。固定 O 意味着该辅助项不给 O 收益，也不给 O 梯度；**压住 O 的责任仍在原来的绑定与保持监督。** 不能写成 O 已被硬性禁止。

剩余最有价值的补强是一次真实 TRAIN 联合策略回放：editor 和新 selector 共同执行五轮，下一笔继续调用冻结机器人，根据实际新状态重新生成监督。旧 0.5 轨迹不足以替代这个步骤。这是借鉴 DAgger 的状态覆盖思想，不需要实施完整强化学习系统。[DAgger 原文](https://proceedings.mlr.press/v15/ross11a/ross11a.pdf)

## 2. 必须修改的事实与因果表述

| 原有表述或隐含结论 | 原文／本轮核查 | 应改成 |
|---|---|---|
| “边权和最终结果一起训练，误差 0.177 降到 0.062” | Cerrone 2019 Table 1 的 CREMI A：RW VOI 0.177±0.015，LRW 0.062±0.021。是二维输出、三切片输入、每真段一个种子、半分辨率图、两像素边界容差。 | 指定指标、数据和条件。支持结构化监督可能有用，不支持可兑现的医疗 Dice 提升。 |
| 上述数字支持 LRW／传播整体优于简单算法 | 同表汇总 LRW 0.162、watershed 0.165；CREMI C 上 LRW 0.232，watershed 0.209，后者更好。 | 对比 RW 的改善是真实结果；不说所有数据上都胜出，也不把它当 max-min 比随机游走更优的证据。 |
| “24³ 随机格子需要 249 步”作为经典文献发现 | L1 开头注明，这是旧 agent 的 CPU 玩具实验，脚本在会话临时目录，未随项目保存；此附件无法逐位重现该数。 | 数字若保留，明确为旧本地示例、未本轮复现。一般结论只需“K 轮局部传播至多依赖 K 跳”的结构事实。 |
| “没有校准就用最优规则，68.7 降到 65.1” | Berman 2018 §4.3：20 个随机批次，每批 21 张且全类别出现；指标是 mIoU。CE+equibatch 为 68.7±1.2，Nowozin 决策为 65.1±1.4；作者将失校准写为他们相信的原因。 | 这是特定实验中规则失效与失校准风险的例子，不是只改变校准因素的因果证明，不是 Dice 或 PET/CT 数字。 |
| “连通规则漏出原因已证明在逐体素训练，不在连通本身” | MALIS 明确指出一条错误高亲和边就可造成大型合并；Funke 的完整方法也采用 watershed 与 agglomeration，而非只阈值取块。 | 旧 rule-CC 的原因尚未隔离。学习边和结构监督能针对问题，但 max-min 本身仍有单桥泄漏偏好。 |
| “半阈值来自 Dice 定义”跨论文统一成立 | Lipton 用最优总体 F1，不是当前 Dice；RankSEG 明确区别总体 F1 与逐图期望 Dice，并有条件独立等假设；Nordström 另有标签体积恒定条件。 | 已知实际候选内容的 Dice 增量可以精确计算；未知分数的执行阈值不能只由当前 Dice 代入推出。 |

原文：[Cerrone 2019](https://arxiv.org/html/1905.09045v1)、[Berman 2018](https://arxiv.org/pdf/1705.08790)、[MALIS](https://papers.nips.cc/paper_files/paper/2009/file/68d30a9594728bc39aa24be94b319d21-Paper.pdf)、[Funke](https://arxiv.org/pdf/1709.02974)、[RankSEG](https://jmlr.org/papers/volume24/22-0712/22-0712.pdf)、[Lipton](https://arxiv.org/pdf/1402.1892)、[Marginal Thresholding](https://arxiv.org/pdf/2304.04116)。

S2-causal-map.md 仍保留已被 PLAN 撤回的“Dice 半值规则 + 自估 D 头 + 校准”组合一，并将“再次指同一处”解释为范围估小的确定原因。其核心表与组合必须同步更新或明确标为旧提案；不能让新计划与其主要依据文件相互矛盾。重复笔可能是强调、纠正、残留错误或改目标，仅凭动作重复不能唯一归因。

## 3. 并查集究竟精确算什么

给定有限图 G=(V,E)、固定边亲和 a_e 和种子集合 S，定义：

\[
R(v)=\max_{s\in S}\max_{\pi:s\leadsto v}\min_{e\in\pi}a_e.
\]

R 是从种子到该点所有路径里“最弱边尽可能强”的数值。对任一阈值 τ，R(v)≥τ 当且仅当 v 在仅保留 a_e≥τ 的图上连到种子。按边权降序合并，或建立最大生成森林后读取瓶颈值，可以得到这一数学定义的精确值。[MALIS 原文](https://papers.nips.cc/paper_files/paper/2009/file/68d30a9594728bc39aa24be94b319d21-Paper.pdf)

这保证了：

- 不需要人为规定传播 K 步；长而弯的有效路径可以被完整计算。
- 对给定边权、图和种子，前向连通值有确定含义。
- 对同一图的多种阈值可复用层次连接结构。

这不保证：

- R 是“属于 T 的概率”。落在 [0,1] 的瓶颈值仍不是概率；对图边作单调变换能保排序，不代表保校准。
- 只沿真实错误区域传播。图和边头不知道 G；一条虚假高亲和桥便可接入大块 O/P。
- 多路径证据被综合。max-min 只需存在一条强路径，不奖励多条相互支持的通路，也不按通路宽度或长度收费。
- 输出必与真实意图范围、病灶解剖对象或最高 Dice 候选一致。

**单桥反例。** 两块各有高内部亲和，之间只要存在一条高于执行水平的假桥，远端整块都会有足够高的 R。并查集在这里算得完全正确，但边和任务定义错了。去掉固定 K 不会消除这个错误，可能让错误传播得更远。

因此 C 保持“软特征接入 + 直接边监督 + 少量结构配对”合理。高风险假桥和漏连桥应在训练中被看见；不必同时实现随机游走、MWS 和图割。MALIS 只说明对连通结果监督有方法依据，不能承诺该损失就是 SIRB 的最优选择。Funke 的约束正负两遍是有用的实现参考，但其原始 Rand 点对目标仍需与 T/O/P 任务区别。[Funke 原文](https://arxiv.org/pdf/1709.02974)

### 3.1 复杂度与可微性

常规实现排序约 O(E log E)，并查集约 O(E α(|V|))，存储 O(E+|V|)。三维局部邻接时，18 邻接的无向边量级约 9|V|，6 邻接约 3|V|；边界会减少一些。全卷代价还包括边特征产生、缓存、排序、CPU/GPU 传递和反向信息，不能用旧 96³、6 邻接玩具计时推断全卷耗时。此处只要求在正常训练／推理任务日志中记录实际代价，不另外发动测速。

前向 R 的 max/min 是分段线性的，非并列区间可将梯度传给被选中的瓶颈边；并列边可使梯度路线不唯一，需确定处理。若输出是硬连通分区／阈值掩膜，则对边权几乎处处是分段常数，直接梯度没有信息。Python/CPU 并查集不会自动变成可微网络层，必须实现相应反向或由独立边损失训练。两者不要混称。[Blackbox Solvers](https://arxiv.org/html/1912.02175v2)

“Mutex Watershed 精确全局最优”也要限缩：原文定理针对独异边权、dominant power 变换后的特定目标；不是任意多割能量的精确解。[Mutex Watershed §IV](https://arxiv.org/html/1904.12654v2)

### 3.2 通用医学的范围边界

当前 T 由冻结的“笔触及的同向残差分量”定义；多个触及分量可以取并集。这与“一个完整病灶”不同：同一病灶的漏分残差可能被已经正确分割的区域隔成多块。方向门控若只允许 ADD 在 M 外行进，就不能穿过那些已正确分割的 M 去连另一漏分岛。按当前 T 定义这未必是错误；如果以后任务允许一笔指整个解剖对象，则要重新定义监督，不能指望连通求解器自动扩大语义。

同理，移除 60 mm 截断只修复距离表示。局部训练块、global 分支分辨率、滑窗覆盖、可获得的边图和实际写回 footprint 都仍限制可用信息或可执行范围。不能把“无固定传播步数”写成“无任何空间上限”。

## 4. Dice 的精确账、概率规则与范围目标

以下是独立代数推导，不是新的实验结果。所有集合在同一网格、同一有效域和同一物理体积权重上计算。令 A=|M∩G|、B=|M|+|G|、D=2A/B。候选 K 是经过真实写回后实际被改变的体素，k=|K|。

### 4.1 已知候选的 ADD／REMOVE

ADD 候选中 a=|K∩G|：

\[
\Delta D_{\rm add}
=\frac{2(A+a)}{B+k}-\frac{2A}{B}
=\frac{2a-Dk}{B+k}.
\]

非空候选、B>0 时，严格变好等价于 a/k>D/2。

REMOVE 候选中 a=|K∩G| 为被误删的真前景：

\[
\Delta D_{\rm remove}
=\frac{2(A-a)}{B-k}-\frac{2A}{B}
=\frac{Dk-2a}{B-k}.
\]

B−k>0 时，严格变好等价于 a/k<D/2。这是**候选实际内容已知时的判据**。推理不知道 a、G 或 D；把 a/k 替成未经验证的 pT 均值，不会保持这条充要条件。

Dice 比值含随机分母，逐病例 E[Dice] 一般不等于把后验均值代入比值。RankSEG 的精确决策还有条件独立、后验估计和体积选择；Lipton 的总体 F1 结论不是这一个问题。校准风险需要被记录，但本项目不必为此先堆完整概率校准工程。

### 4.2 O 奖励冲突确实存在

在合法方向域内分解 k=c+o+h，其中 c=|K∩T|、o=|K∩O|，h=|K∩P|。则真实原生 Dice 变化为：

\[
g_{\rm add}=\frac{(2-D)(c+o)-Dh}{B+k},
\qquad
g_{\rm remove}=\frac{D(c+o)-(2-D)h}{B-k}.
\]

因此 g 对 T 与 O 的正确修改同等奖励。全局指标与“只修本笔范围”的任务目标不是完全同序的两个说法；保持范围必须由另一份监督／约束表达。任何学习器都不能单凭同一个 g 标签知道 O 不该改。

### 4.3 为什么不采用 Y* 或 U_T 为共同主目标

**Y* 方案。** 令 Y* 为当前 M 只在 T 理想编辑后的 mask，u*=Dice(M_K,Y*)−Dice(M,Y*)。该目标确实把 O 当应保留的区域，范围含义清楚。但它的基准前景由 M 决定，并非 G。ADD 若 |M|=m、|T|=t，初始 Dice(M,Y*)=2m/(2m+t)，常接近 1；相应误编辑价格便接近以 0.5 为分界，未保留当前原生 D 较低时的同一价格关系。REMOVE 同样改变错删和正确删的相对收益。不能声称这个变换既完整保留 native Dice 又自动满足 intent。

更明确的反例是 Y*=∅：当当前 M 恰是本次要删的整块 FP，删除一部分后只要 M_K 仍非空，常见空目标 Dice 约定下分数一直为 0，直至删空才跳变；若冻结协议跳过空目标则标签根本不适用。不能用任意 epsilon 制造本不存在的收益。

**U_T 方案。** 此前讨论的

\[
U_{\rm add}=\frac{(2-D)c-D(o+h)}{B+k},\quad
U_{\rm remove}=\frac{Dc-(2-D)(o+h)}{B-k}
=g-\frac{2o}{B\pm k}
\]

把 O 的正确编辑改按错误编辑收费。它可作为明确的研究效用，却不是有效目标 mask 的原生 Dice 差，而且 REMOVE 的范围可失控：若 |M|=1000、|G|=1、二者不交，当前 T 只有 1 个 FP、O 有 999 个，候选删光 M，则原生 g=0，而 U_T=−1998。这个负值来自规范性重记账，不是原指标恶化 1998 点。把它作为软损失可能让少数候选支配梯度。

所以本轮将两者降为**未采用的研究备选**。目前不要求另跑这两个标签的消融；它们的反例已足以撤回“直接共同替换 A/B 目标”的推荐。

## 5. 可直接替换第六稿 §4.3、§5.1–5.2 的定稿段

### A：两棵小树，真实收益和范围保持分别预测

对于同一当前状态 s 与当前 checkpoint θ，先让所有候选经过同一原生写回算子，得到实际编辑集合 K。标签保存 c/o/h、真实原生 Dice 变化 g，以及未授权编辑体积：

\[
b(K)=|K\cap(O\cup P)|.
\]

O 虽然是别处同向错误，修改它仍计入 b；P 是本方向的正确区域。b 不是“新增分割错误”的别名，必须把 O 与 P 分项保存。

建议用于小树的 b 标签除以**同一状态所有候选共享的合法可写区域体积** V(F_s)，形成 [0,1] 的无量纲量。F_s 由当前分割、方向、固定有效域和真实写回 footprint 得到，不用 G；若 F_s 为空，直接 no-op。不能除以各候选自己的 k，那会把总未授权量变成候选错误比例，改变所声明的约束。原始 mL 同时保留用于结果解释。

分别拟合 g_hat(s,K) 与 b_hat(s,K)。b_hat 的有限输出统一截到其已知值域 [0,1]；非有限预测按确定异常规则排除，不能用 NaN 参与排序。g_hat 必须保留真实零点，纯排序分数不能直接与 0 比较。

令 K_ref 是**同一当前 checkpoint、同一当前状态、同一次 pT 前向、同一合法域和写回算子**的原 0.5 执行候选；它不是旧父模型历史轨迹里的候选。可行集合为：

\[
\mathcal C_{\rm keep}(s)=
\{K:\widehat b(s,K)\leq \widehat b(s,K_{\rm ref})\}
\cup\{\varnothing\}.
\]

no-op 固定 g_hat=0、b_hat=0。从可行集合选择 g_hat 最大的候选；有限预测下 K_ref 自身可行，所以该约束不会凭空失去原候选。精确并列用确定规则，可优先落实当前 signed stroke。模型预测不精确并列时，该 tie 约定不提供额外保证。

这是对预测量施加的**相对范围保持约束**，不保证真实 b 不上升，更不保证 K⊆T。全套 T/O/P 训练和实际已选动作的 O/P 审计仍不可少。约束不引入新的手扫风险系数，但选择以 0.5 候选为参照仍是公开的工程决定。

对空 GT 扫描，g 标签严格沿用冻结指标的有效性掩码；若官方不定义／不计该扫描 Dice，不填一个虚假的 g=0。b、角色监督和 FP 记录照常。推理不得读取 G 来决定是否走某条分支。

### B：保留原角色监督与 O 不奖软收益

B 不使用 U_T。原有 T/O/P 指代损失、边界排序和保持样本保留。对两个训练块按实际坐标合并去重为 U，块外分割不变；在合法方向域用 pT 作软编辑量，并在这个辅助项中将 O 固定不动。令加笔 δ=(1−M)pT，删笔 δ=−MpT，再对 O 位置置零。损失使用：

\[
-\left[
\frac{2(A_0+\sum_{v\in U}w_vG_v\delta_v)}
{B_0+\sum_{v\in U}w_v\delta_v}
-\frac{2A_0}{B_0}
\right].
\]

A0、B0 来自同一训练网格整例的常量统计；w_v 为相应体素体积／有效权重。体积求和不能直接用 T/O/P 过采样点代替均匀有效域。空 GT 或无定义分母按已冻结约定掩码处理，不伪造收益。

该辅助项给出 3 mm 网格上的软收益近似；不是原生二值写回的精确梯度，也不等于选择器的完整决策。固定 O 只是不给这项奖励和梯度，O 的约束来自原角色绑定。网络、选择器、保持约束服务同一任务，但不必也不应强行宣称三个数学目标完全相同。

## 6. argmax、no-op 与五轮分布：最便宜但不能省的环节

### 6.1 同时防两个头被选择过程利用

若每个候选都有预测误差，从 20–40 个里取最大值会倾向挑中 g 的正误差；范围筛选同时会倾向放过 b 被低估的候选。即使两个头的全体候选 MSE 都不错，也可能在最终赢家上失真。这是极值选择偏差和选择性评估问题；不需要把系统改造成 Double Q-learning 才能承认并检查它。[Double Q §2](https://papers.nips.cc/paper/3964-double-q-learning.pdf)、[Cawley & Talbot](https://jmlr.org/papers/volume11/cawley10a/cawley10a.pdf)

一次按患者留出的 TRAIN 检查应直接回答：

1. 实际选中的 K 比同状态 K_ref 带来多少真实 g；其候选 regret 和负收益率如何。
2. 实际 b(K) 是否超过真实 b(K_ref)，超出多少、出现于哪些轮次；分别记录 O 与 P，不能只看二者合计。
3. 新选择器实际执行五轮后，D5/nAUC、P 新错、O 编辑和 no-op／目标重访如何。

不需要先新建多个风险控制器、置信区间头或大规模阈值扫描。若头部只能靠错误低估 b 通过约束，那是当前小模型不适用的可见结果，不能用“有约束”掩盖。

当前 checkpoint 的 0.5 参照与“已接受的完整系统”是两个层次。B/C 的自身 0.5 可能比旧系统更容易越界，故相对当前参照的规则不能保证跨模型全系统保持。最终仍与已接受系统在相同 roster 上各自完整走五轮，报告实际范围变化。

### 6.2 19 档、去重与候选质量

19 是既有阈值预算，两个候选族原始最多 38 个，再加入原候选、原生 stroke-only 和 no-op 后按实际 native 编辑去重。它不是 19 个独立候选，也不是数学上最优的档数。均匀概率阈值还依赖分数标度；可学习并未消除候选族的表达上限。

目前不用因为这个问题增加一轮候选数消融。保留原预算、去重、原 0.5 和 stroke-only 即可。真正的候选质量瓶颈应由“留出 TRAIN 上最优可执行候选相对参考”的事实来判断；上限大仍不保证选择器能拿到。

RankNet 的分差损失可用于边界两侧排序；它对共同分数平移不敏感，若未来用于候选排序仍需绝对收益或 no-op 锚。本轮直接回归 g 已是最小路径。[RankNet](https://icml.cc/2015/wp-content/uploads/2015/06/icml_ranking.pdf)、[Decision-Focused Learning](https://proceedings.mlr.press/v162/mandi22a/mandi22a.pdf)

### 6.3 零交集平台和 no-op

设 A=0、G 非空、当前 M 只含 FP。正确删除任意部分 FP，只要不同时加入 TP，Dice 在删除前后都是 0。即使选择器知道真值，严格“g>0 才执行”也会拒绝这些正确删除；而删除后下一笔可能转向漏分，有限五轮的最终效果可能更好。故严格正即时收益不是最佳五轮策略的定理。

stroke-only 只按**原生 signed stroke ∩ 合法方向域 ∩ 实际 writeback footprint**定义；若 3 mm 表示或原写回会扩展其范围，必须照原算子执行，不能把扩展体素称为用户已逐点保证正确。加入此候选和精确并列时优先落实笔迹很便宜，但预测误差通常使分数不精确为 0，所以不宣称已经解决平台。

新 TRAIN 联合回放顺手记录实际 no-op、笔迹是否落实和重复目标。no-op 消耗一轮，不重新抽笔；历史、轮次或随机数变化可能改变下一笔，所以也不要未经观察称它严格吸收态。

**只有真实回放发现停滞时**，再对这些状态比较一个当前提案与 no-op 两支，使用相同剩余 horizon、相同未来部署策略和冻结机器人继续到同一终点。训练另一个清楚命名的优势：

\[
Adv_H(s,K)=V_H(s,K)-V_H(s,\varnothing).
\]

这里 no-op 的相对值才是 0。不能给提案两步／多步收益，却给 no-op 即时 0；不能把少量 Adv_H 与 g 标签混在同一列。仅做两支，避免对所有 40 个候选展开。训练可用真值定位问题和生成标签，推理触发只能依赖可观察的 no-op／笔迹／状态历史，不读取真实 T 或真实 Dice。两支最终都为 0 时，原目标在该 horizon 内确实不可区分，应记录限制，不能造正收益。[AggreVaTe](https://arxiv.org/pdf/1406.5979)

### 6.4 状态回放与患者交叉拟合的不同责任

患者交叉拟合控制头部在相同患者标签上的拟合泄漏；它不能消除以下两种偏移：

- 主网络 v1 已看过所有 TRAIN 患者，头部患者留出不等于整个系统 OOF。
- 新 selector 改了本轮状态，机器人下一笔跟着变；旧 0.5 轨迹不是新策略的轨迹。

最小流程是先用旧轨迹初训，再真实回放一次当前 editor+selector 的 TRAIN 五轮，聚合新标签重拟合。交叉拟合评估时，留出患者的轨迹必须由未在该患者标签上训练的 selector 生成；不能用全 TRAIN 拟合的 selector 先生成留出轨迹，再称独立。每个 checkpoint 的配套 selector、候选生成器和回放策略版本要一起记录。该刷新只是减少明显偏移，不宣称一次刷新达到策略收敛。

## 7. 第六稿第二轮修改清单（限五条）

1. 将 §3.1、§4.3、§5.1–5.2、§10 的 U_T 共同目标全部撤回，替换成第 5 节的 g/b 两树和原 T/O/P + O 不奖软收益；Y*、U_T 降为未采用研究备选。
2. 固定 K_ref 的定义为同一当前 checkpoint／state／writeback 的 0.5 候选；区别当前参考与跨 checkpoint 的完整系统对照。
3. 写清 b 的含义、共享归一化分母、[0,1] 输出处理、空 footprint 和非有限值；预测约束不叫真实或零越界保证。
4. 头部验收改为选中后 g/b/O/P 的真实结果与真实五轮；患者留出评估的联合轨迹也不得由看过该患者标签的 selector 生成。
5. no-op 用即时 g=0；若触发短续演则统一 horizon 和 no-op baseline、另命名 Advantage。空 GT 依据冻结 metric 掩码，不伪造 Dice 标签。

第六稿 C 的 max-min、并列次梯度、原生／研究网格拓扑和 FOV 区分已基本准确；保留即可，无需为本次数学审核再增加一套传播算法。

## 8. 证据能支持的最强方案，以及不能承诺的事

对效应最直接的组合仍是：

- A：复用现有强 checkpoint 的一次前向，以真实 native 候选拟合 g/b 选择器，一次新联合策略 TRAIN 回放刷新，然后直接做真实五轮 VAL。
- B：一次既有 8k 预算把密集笔迹空间信息、T/O/P 边界与保持、O 不奖软收益、真实自身状态、可撤回的上一轮编辑足迹和正确物理几何一起训练；最终 checkpoint 配套重拟合选择器。
- C：并行准备边头与 max-min 软通道及少量结构配对，有完整可用 B 后作为增强候选，不挡 A/B 出效果。

这不是三套平行理论争论，而是同一执行器随网络变强继续使用。超参数政策是消除用答案拍出的语义半径／截止线，保留并公开计算预算和优化设置。可学习不会自动创造跨模态泛化；也没有任何上述原文能给出从 0.7524 必达 0.79 或 0.80 的可靠概率。新方法的证据必须来自实际五轮结果。达到目标后再补同预算归因是符合当前用户意图的顺序。

## 9. 逐篇阅读索引

“全文相关段”表示本次实际打开原文，读取与本任务有关的方法、定理或结果，不表示逐字通读所有补充材料。精确 URL 与限制以 JSON 为准。

| ID | 年份与原始论文 | 访问深度 | 可迁移的核心与边界 |
|---|---|---|---|
| M01 | 2009 · [Maximin Affinity Learning of Image Segmentation](https://papers.nips.cc/paper_files/paper/2009/file/68d30a9594728bc39aa24be94b319d21-Paper.pdf) | 全文相关段 | 借用 seed-to-target 连通监督和误接桥负监督；只把最大最小连通作为可学习特征，保留 T/O/P 语义目标。 监督目标是点对 Rand 分割误差，不是医疗交互中的 T/O/P 或整例 Dice；精确连通计算不保证边权正确，也不自动避免单桥泄漏。 |
| M02 | 2018 · [Large Scale Image Segmentation with Structured Loss Based Deep Learning for Connectome Reconstruction](https://arxiv.org/pdf/1709.02974) | 全文相关段 | 学习边时加入决定 T 内连通和 T 外误接的结构化监督；对 max-min 支路采用软接入，不立即硬裁剪。 不能把优化后的 MALIS 误写成原始朴素实现的平方复杂度；该工作不能证明 SIRB 的 rule-CC 失败完全由逐体素损失造成。 |
| M03 | 2001 · [Interactive Graph Cuts for Optimal Boundary & Region Segmentation of Objects in N-D Images](https://csd.uwo.ca/~yboykov/Papers/iccv01.pdf) | 全文相关段 | 把任务语义、图能量和求解器保证分开写；通用医学 residual scope 不应无理由等同于整个病灶的单个连通块。 全局最优是针对指定能量，并非语义真值或 Dice；区域与边界的权衡仍是建模选择。一般多标签能量也不能因此声称一次精确解。 |
| M04 | 2011 · [Power Watershed: A Unifying Graph-Based Optimization Framework](https://www.esiee.fr/~coupriec/power_watershed.pdf) | 全文相关段 | 精确陈述选用 max-min 的归纳偏好：保留长而弯的通路，但容易受单桥影响；不把它描述为所有传播问题的统一最佳算法。 随机游走是 Dirichlet／线性系统问题，不能一概说用并查集解决；排序不变性不使学出的亲和值成为概率。 |
| M05 | 2019 · [End-to-End Learned Random Walker for Seeded Image Segmentation](https://arxiv.org/html/1905.09045v1) | 全文相关段 | 支持求解器后的任务监督有用，不能据此兑现 SIRB 任何百分点；也提示多路径信息可比单条瓶颈路径更稳。 不是三维医疗 Dice 0.177→0.062，也不是只改一个因素的严格同配方对比。LRW 的结构化目标还含边辅助项；优于 RW 不等于优于所有传播。 |
| M06 | 2020 · [The Mutex Watershed and its Objective: Efficient, Parameter-Free Graph Partitioning](https://arxiv.org/html/1904.12654v2) | 全文相关段 | 负边提供不该合并的结构信息，但当前效果路线不必额外实现一套 MWS；用于约束创新与最优性表述。 有限精度相等边权须有确定 tie 约定；无可调阈值不等于网络、图邻接、排斥边和训练全部没有选择。 |
| M07 | 2018 · [High-precision automated reconstruction of neurons with flood-filling networks](https://www.nature.com/articles/s41592-018-0049-4) | 摘要／局部图注 | 借用当前掩膜状态影响下一次编辑的思想；不把 FFN 精度或停止规则作为整卷医疗纠错的保证。 上述指标不是病灶 Dice，也不能由摘要验证本项目需要的每一项移动／停止实现。迭代队列结束不意味着无计算预算、视野或移动参数。 |
| M08 | 2023 · [RankSEG: A Consistent Ranking-based Framework for Segmentation](https://jmlr.org/papers/volume24/22-0712/22-0712.pdf) | 全文相关段 | 借用每个状态选择候选体积，放弃把当前 Dice/2 当直接输出阈值；用实际执行标签训练轻量选择器。 训练中带 T/O/P 配额、Dice、难例采样的 pT 不自动是所需后验；固定阈值非普遍最优不表示任意学习选择器一定更好。 |
| M09 | 2014 · [Thresholding Classifiers to Maximize F1 Score](https://arxiv.org/pdf/1402.1892) | 全文相关段 | 保留已知候选实际内容的精确 Dice 算式，禁止把定理名称当作未校准 pT 执行阈值的来源。 总体 F1 的定义与逐病例 Dice 期望不相同；本项目 pT 表示指定错误而不是全病灶概率。 |
| M10 | 2023 · [Marginal Thresholding in Noisy Image Segmentation](https://arxiv.org/pdf/2304.04116) | 全文相关段 | 支持用候选真实执行结果直接监督决策，避免把所有概率理论简化成一个当前 Dice 标量。 期望 Dice 与把边缘概率直接代入分子分母通常不同；不能省略恒定标签体积条件，将其推广到多发病灶、残差和多轮状态。 |
| M11 | 2019 · [Optimizing the Dice Score and Jaccard Index for Medical Image Segmentation: Theory and Practice](https://arxiv.org/pdf/1911.01685) | 全文相关段 | 把执行后的 metric 信号加入原有 T/O/P 监督有依据；避免将更换损失与保证达到 0.80 等同。 不能推出任何加权交叉熵在任意数据上都无法学出好 Dice，也不能把该定理解释为边界负样本不该训练。 |
| M12 | 2018 · [The Lovász-Softmax Loss: A Tractable Surrogate for the Optimization of the Intersection-Over-Union Measure in Neural Networks](https://arxiv.org/pdf/1705.08790) | 全文相关段 | 改正计划中的条件和因果语气，保留实测 action score 的理由，避免额外发动大规模校准实验。 不是 Dice/PET 实验；没有通过只改变校准这一因素证明下降的唯一原因。凸扩展也不意味着深网优化全局凸。 |
| M13 | 2017 · [On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a/guo17a.pdf) | 全文相关段 | 不把校准当先决的庞大模块；直接检查选择器挑中候选的真实收益与误改。 概率可靠性与动作排序、分割 Dice、域外可靠性是不同目标；一维温度不能自动修复状态或候选依赖的偏差。 |
| M14 | 2010 · [On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation](https://jmlr.org/papers/volume11/cawley10a/cawley10a.pdf) | 全文相关段 | 留出患者上测已被 argmax 选中的候选，不能只报全部候选 MSE、排序相关或 oracle 上限。 原实验是模型选择，迁移到每状态 20–40 个候选属于数学机制类比，不是该论文直接验证 SIRB。 |
| M15 | 2022 · [Decision-Focused Learning: Through the Lens of Learning to Rank](https://proceedings.mlr.press/v162/mandi22a/mandi22a.pdf) | 全文相关段 | 用当前可执行候选的真实效用监督，并优先检查赢家相对原执行器的收益；首轮无需可微求解器或强化学习。 该方法仍有损失／温度／求解频率等选择，不能称零超参数；候选质量限制了选择器的上限。 |
| M16 | 2025 · [Efficient Connectivity-Preserving Instance Segmentation with Supervoxel-Based Loss Function](https://arxiv.org/html/2501.01022v1) | 全文相关段 | 论文主创新若改善 scope/连接仍需用真实五轮 Dice 选择效果路线，拓扑指标不替代主目标。 连接保持与区域重合不是同一优化目标；不能用其对朴素 MALIS 的描述代替 Funke 高效实现的复杂度。 |
| M17 | 2017 · [Selective Classification for Deep Neural Networks](https://proceedings.neurips.cc/paper/2017/file/4a8423d5e91fda00bb7e46540e2b0cf1-Paper.pdf) | 全文相关段 | 允许不改，但记录它占用的一次交互和重复目标，不把拒绝率越高解释为越安全或越好。 把 no-op 的当前增益定为 0 不是风险控制定理；医学五轮交互中的机会成本与分类拒答不同。 |
| M18 | 2019 · [SelectiveNet: A Deep Neural Network with an Integrated Reject Option](https://proceedings.mlr.press/v97/geifman19a/geifman19a.pdf) | 全文相关段 | 只借鉴可拒绝动作，当前首轮保留便宜的回归树与固定 no-op 参照，不扩为全套 SelectiveNet。 集成 reject 头不能消除效用定义和部署分布问题；多加一个头不自动使零阈值正确。 |
| M19 | 2011 · [A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning](https://proceedings.mlr.press/v15/ross11a/ross11a.pdf) | 全文相关段 | 质量头初训后用实际网络＋选择器做一次 TRAIN 五轮回放并补标签，这是最便宜的闭环补强。 一次回放补数据不继承原定理的多轮、无遗憾和样本条件保证；本项目不是必须完整实现 DAgger。 |
| M20 | 2014 · [Reinforcement and Imitation Learning via Interactive No-Regret Learning](https://arxiv.org/pdf/1406.5979) | 全文相关段 | 仅当 TRAIN 实际发现重复 no-op 或返工时，给 proposal/no-op 两支同剩余 horizon 续演，并预测相对 no-op 的 Advantage。 当前候选的单步 ΔDice 不是 Q 值；若候选用两步标签而 no-op 仍用单步 0，二者基准不相同。 |
| M21 | 2001 · [The Foundations of Cost-Sensitive Learning](https://cseweb.ucsd.edu/~elkan/rescale.pdf) | 全文相关段 | 不因等量保留样本或自适应采样就声称 pT 被校准，直接学执行结果能绕开部分概率解释要求。 距离依赖难负样本采样改变了类内输入分布，不能简单以一个先验修正恢复部署 pT；代价矩阵仍是任务约定。 |
| M22 | 2014 · [Optimal Decisions from Probabilistic Models: the Intersection-over-Union Case](https://www.nowozin.net/sebastian/papers/nowozin2014intersectionoverunion.pdf) | 全文相关段 | 不再套用体素标量规则，用原生执行后的监督标签检查真实候选价值。 期望的比值不是比值的期望；既非所有空间相关标签的精确解，也不是当前 Dice/2 的无条件定理。 |
| M23 | 2020 · [Confidence Calibration and Predictive Uncertainty Estimation for Deep Medical Image Segmentation](https://arxiv.org/pdf/1911.13273) | 全文相关段 | 保留预测值的非概率解释边界，首轮检验已选动作真实结果，不因校准文献启动多模型集成。 更好的校准不等于更高 Dice；该文不保证模型在 PET/CT 或交互状态迁移中可靠。集成计算成本也不符合本轮首要轻量要求。 |
| M24 | 2020 · [Differentiation of Blackbox Combinatorial Solvers](https://arxiv.org/html/1912.02175v2) | 全文相关段 | 明确连通模块应输出连续瓶颈值并有自定义梯度或独立边监督；不要把 Python/CPU 并查集写成自动端到端可微。 这不是求解器原始梯度，也不无超参数；max-min 连通数值是分段线性的另一种对象，不能把两种微分问题混同。 |
| M25 | 2005 · [Learning to Rank Using Gradient Descent](https://icml.cc/2015/wp-content/uploads/2015/06/icml_ranking.pdf) | 全文相关段 | 边界成对排序有直接作用；若给选择器加入排序损失仍应保留绝对收益/no-op 锚，首轮可先用简单回归。 成对排序只约束分差，对共同平移不敏感，不能单独赋予 0 分绝对的“不值得改”意义。 |
| M26 | 2010 · [Double Q-learning](https://papers.nips.cc/paper/3964-double-q-learning.pdf) | 全文相关段 | 20–40 候选后必须核查 argmax 赢家，而非只看平均预测误差；候选去重、保留 baseline/no-op、患者留出和真实五轮即可。 本项目候选高度相关，不能套独立高斯近似给出固定扣分系数；此处借用统计机制，不推荐将系统改为 Double Q/RL。 |
| M27 | 2024 · [Conformal Risk Control](https://arxiv.org/pdf/2208.02814) | 全文相关段 | 当前不把 CRC 加入效果主线；防止把 no-op 或候选置信界包装成现成的理论安全保证。 随编辑阈值变化的 Dice 或新错不一般单调；边际风险控制不是每一患者保证。必须给 α 风险预算，不能说无阈值无参数。 |
| M28 | 2010 · [Contour Detection and Hierarchical Image Segmentation](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2010/EECS-2010-17.html) | 摘要／局部图注 | 候选可按实际 merge/体积次序组织，19 个均匀概率档是计算预算选择而不是自然定律；暂不新增一套 UCM 实现。 仅凭摘要不声称某一种超度量构造具备本项目所需全部性质；层次候选仍受初始轮廓与树结构限制。 |

