# SIRB K 系列验证集没过线：归因方法与领域文献

2026-10-07，Claude Code 子 agent 写。只查文献、只读本机已有的分析结果，没有连服务器，没有碰测试集。

这份调研要帮我们回答四件事：K1、K2 比 v1 不涨，是哪一项部件拖的，几次 20 GPU 小时的训练怎么查清；加笔为什么变保守、删笔却变好；离笔远的漏标怎么补；第一阶段的概率图该不该喂回网络。最要紧的五条结论：

- 只罚负例、没有对应正例的难例项，会把正例一起压下去，别的领域有直接测量（EQL v2、ASL、Xuan 2020、Wu 2017）。K 的难负样本只从 O、P 里挑，梯度是 target Dice 项的 2.4 倍，训练单元上的 T 召回从 0.82 降到 0.60（训练日志），机制对得上，还要 D2 核。
- 先分清"排序坏了"还是"门槛偏了"。按我们自己的 Dice 账，K 把加删两个方向都收严，删笔收对了、加笔收反了；温度缩放和按先验调 logit（概率之前的原始分数）都不改排序（Guo 2017、Menon 2021），D1 若显示排序没坏，按符号在 TRAIN 回放上学一个偏置，不用重训。
- 归因只需再训 2 次。v1（六项全关）和 K1（全开）两个角已有，对头号嫌疑做 2×2 析因就能得到主效应、交互和两人沙普利值（HyperSHAP、Covert 2021）；逐项去掉要 6 次且看不到交互（Rainbow、Revisiting Rainbow），6 部件部分析因 8 次起步、主效应和二阶交互混在一起（NIST 手册）。
- 概率图输入有直接证据：MFP 喂调制过的上一轮概率图，离点击远的部分也分得对；2S-ICR 喂上一轮概率并随机丢弃，Dice 从 0.815 升到 0.846。但项目 09-19 的决定为了不依赖基座把概率图拿出了网络，改不改要导演定。
- 远端排第二。测地距离编码在 autoPET 上不比欧氏距离好（Marinov 2023），学出的传播和按错误块大小抽训练样本证据更好（NLSPN、CDNet、nnInteractive）；而我们第 1 轮把 30 mm 外漏标全补齐，理想收益也只有约 +0.015（验证集，用了真值）。

本轮核了 75 个来源：71 篇论文，加 autoPET 三届官方评测页和 NIST 统计手册各一处。每篇至少读到摘要和要引用的那段结果，深写约 35 篇，其余一两句。和已有的十二领域文献深挖（`protocols/petct-sirb-v2-referent-scope-plan-20261003/literature-domains-review.md`）重复的，只补和这次失败相关的部分，注明"见领域几"。项目自己的数字都标来源：验证集（VAL，99 个扫描、57 位患者，Dice 分母 85 个阳性扫描）、训练日志，或测试集（只作背景）。下文 D1 到 D5 沿用 Codex 第二轮简报里设计好的五项不训练诊断（D1 看 pT 分布和门槛，D2 看各项梯度，D3 按符号换模型，D4 置换 B3 输入，D5 比特征），D6、D7、T1 到 T3、N1、N2 是本文新加的，汇总在第三部分。

## 第一部分 归因和诊断的方法

### A1 消融设计、交互作用、种子方差

这一类能回答：哪一项部件对第五轮 Dice 的差距负责，几项之间有没有互相抵消。答不了两件事：为什么（机制要靠 A2 到 A6），以及比一次重训的波动还小的差别。

《Rainbow: Combining Improvements in Deep Reinforcement Learning》，Hessel 等，AAAI 2018。核查：本轮读了消融一节。

- 思想和方法：把 DQN（深度 Q 网络，一种强化学习算法）的六项独立改进合成一个智能体，再从完整版里每次去掉一项（ablation，消融：去掉一项看效果变多少），在 57 个 Atari 游戏上比。
- 原文结论和条件：去掉优先回放或多步回报，中位成绩掉得最多；分布式回报次之；去掉 dueling 和 double Q（两项估值方式上的改进），中位数差别小，且随游戏变。
- 我们怎么用：它和 K 同构，都是一次加六项。"从全开里逐项关"回答的是"其余五项都开着时这一项值多少"，对 K 就是 K 去 B1、K 去 B2，共 6 次从零 40k，约 120 GPU 小时。
- 限制：一次只动一项，看不到交互作用（interaction，两项同时开时多出来的效应）。Rainbow 的六项各自单独被证明过有用，我们的六项没有。

《Revisiting Rainbow: Promoting more Insightful and Inclusive Deep Reinforcement Learning Research》，Obando-Ceron 与 Castro，ICML 2021。核查：本轮读了结果和算力段。

- 思想和方法：在经典控制和 MinAtar 小环境上重做 Rainbow 的消融，每个设置重复 100 次。
- 原文数字和条件：原版 Rainbow 的 Atari 实验约 34,200 GPU 小时（P100），MinAtar 每个游戏约 12 到 14 小时。分布式回报单独加给 DQN 有时反而变差（Acrobot、Freeway），从 Rainbow 里去掉它有时反而变好；多步回报一直有用；六项全加整体仍最好。
- 我们怎么用：同一个部件，"单独加到基线上"和"从全开里去掉"可以给出相反的结论。只做 K 去 B1 不够，还要做 v1 加 B1，两个合起来才看得出 B1 的作用依不依赖其他部件。
- 限制：小环境的结论不一定搬得回大环境。导演规矩是归因也要从零训满 40k，"缩短训练先筛一轮"只能讨论，不能当证据。

《What Matters for On-Policy Deep Actor-Critic Methods? A Large-Scale Study》，Andrychowicz 等，ICLR 2021（arXiv 版题名 What Matters In On-Policy Reinforcement Learning?）。核查：本轮读了实验设计段。

- 思想和方法：50 多个设计选择，训了 25 万个以上智能体。把可能互相影响的选择分成主题组，组内随机抽组合，组外固定在一个强基线上；每个取值看抽到它的配置成绩的第 95 百分位，以及它在前 5% 配置里出现的比例。
- 我们怎么用：规模学不了，分组的思路能借：按机制把六项并成两三组，组内看交互，组间先当没有交互。
- 限制：要成百上千次训练。

《Implementation Matters in Deep RL: A Case Study on PPO and TRPO》，Engstrom 等，ICLR 2020。核查：本轮读了消融设计和结论。

- 思想和方法：PPO 和 TRPO 是两种强化学习算法。PPO 的实现里有 9 项论文没强调的代码层优化（code-level optimization，只在实现里出现的细节），对其中 4 项做了 2^4＝16 种组合的全因子实验（factorial design，析因设计：各开关的组合都跑）。
- 原文结论：这些代码层优化对最终回报的影响，比 PPO 和 TRPO 两个算法本身的差别还大。
- 我们怎么用：按我们一次 20 GPU 小时算，全因子只在两三项时做得起（2 项 4 次，3 项 8 次），4 项的 16 次就要 320 GPU 小时。另一点更有用："主打的部件"和"顺手的细节"要分开登记。B6 只标定了一项的倍率、远端块的放置规则、难负样本只取 pT 最高的 |T| 个，都属于后一类，最可能藏着问题。
- 限制：强化学习的回报方差大。

《An Efficient Approach for Assessing Hyperparameter Importance》，Hutter、Hoos、Leyton-Brown，ICML 2014。核查：本轮读了摘要页。

- 思想和方法：fANOVA（函数方差分解：算每个超参、每对超参各解释了多少成绩差异）。先在已有调参记录上训一个随机森林当代理模型（surrogate，用便宜模型近似昂贵实验），再对代理模型做分解。
- 原文结论：即使超参维度很高，大部分成绩差异也只来自少数几个超参。
- 我们怎么用：训练部件做不起，要几十上百个配置。推理端的开关做得起：执行门槛、按符号换模型、翻转平均、B3 输入置换，组合起来在第 1 轮单步上跑全因子（T3），看主效应和两两交互。
- 限制：配置少时代理模型不可靠。

《Analysing differences between algorithm configurations through ablation》，Fawcett 与 Hoos，Journal of Heuristics 22(4):431–458，2016。核查：本轮读了作者项目页和书目信息，期刊正文没打开。

- 思想和方法：ablation path（消融路径）：从源配置出发，每次改一个参数朝目标配置走，记下沿途每一步的成绩。按作者工具的说明，下一步挑当前收益最大的那个改动（贪心的细节出自项目页，期刊正文未核）。
- 我们怎么用：v1 是源、K 是目标。固定顺序走完 6 步要 6 次训练，贪心挑选要 6＋5＋4＋3＋2＋1＝21 次，都做不起。它提醒一点：路径上的中间配置可以比两端都差，"v1 加 B1 变差"推不出"B1 在 K 里也有害"。
- 限制：结果依赖贪心顺序。

《Explaining by Removing: A Unified Framework for Model Explanation》，Covert、Lundberg、Lee，JMLR 22(209):1–90，2021；《HyperSHAP: Shapley Values and Interactions for Explaining Hyperparameter Optimization》，Wever、Muschalik、Fumagalli、Lindauer，AAAI 2026。核查：本轮读了两篇的定义段。

- 思想和方法：Covert 等把"去掉一部分看变化"的解释法拆成三个选择：怎么去掉、看什么量、怎么汇总。作者写明，只看单项边际贡献会漏掉交互，一组相关特征逐个去掉都接近 0，合起来却重要。HyperSHAP 定义了消融博弈：从参考配置出发，把一个子集换成目标配置的取值、看成绩，再算 Shapley value（沙普利值：把总差距按所有组合里的边际贡献平均分给各项）和交互值。
- 原文数字和例子：精确沙普利值要评 2^n 个子集。PD1 基准里训练 transformer（一种注意力网络结构）的例子里，消融博弈把收益几乎全给了学习率；可调性博弈显示学习率和动量各占一半，并且是负交互，两者互相替代。
- 我们怎么用：v1 当参考、K 当目标，部件子集就是"玩家组合"。6 项要 64 次训练，做不起；并成 2 个玩家只要 4 次，其中 v1、K1 已有。两人时，B1 的沙普利值＝[(v1+B1)−v1＋K−(K−B1)]/2，交互＝K−(K−B1)−(v1+B1)＋v1。
- 限制：沙普利值把交互平分给参与者，交互大时要另报交互值。

《NIST/SEMATECH e-Handbook of Statistical Methods》第 5.3.3.4.4 节。核查：本轮读了定义原文。

- 内容：fractional factorial（部分析因：只跑一部分组合）按 resolution（分辨度）分级。III 级主效应和二阶交互混在一起；IV 级主效应不和二阶交互混，但二阶交互彼此混；V 级都分得开。
- 我们怎么用：6 个两水平部件，2^(6−3)＝8 次只到 III 级，主效应和二阶交互分不开；16 次才到 IV 级，约 320 GPU 小时。B1 和别的部件很可能有交互（加删两向相反），本月不做部件级部分析因。

种子方差四篇：《Accounting for Variance in Machine Learning Benchmarks》，Bouthillier 等，MLSys 2021；《Deep Reinforcement Learning That Matters》，Henderson 等，AAAI 2018；《How Many Random Seeds? Statistical Power Analysis in Deep Reinforcement Learning Experiments》，Colas、Sigaud、Oudeyer，arXiv 2018；《Torch.manual_seed(3407) is all you need》，Picard，arXiv 2021。核查：本轮读了各自结果段。

- 原文数字和条件：Bouthillier 把训练结果的波动拆成数据抽样、增强、初始化、dropout（训练时随机丢弃一部分神经元）、数据顺序、调参，数据抽样最大，初始化通常不到它的一半，和数据顺序相当；建议按"A 胜 B 的概率"判断，门槛 0.75。Henderson 用 TRPO 的同一配置跑 10 个种子，分两组各 5 个，HalfCheetah 上两组学习曲线显著不同（t＝−9.09，p＝0.0016）。Colas 的例子里 5 个种子漏掉真实差别的概率是 0.51，要 10 个才降到 0.2，样本少于 10 时不宜用 bootstrap（有放回重抽样）区间。Picard 在 CIFAR-10 上扫了 1 万个种子（短训练），准确率从 89.01% 到 90.83%，差 1.82 个点；ImageNet 上 50 个种子的 ResNet50 差 0.44 个点。项目一直用的种子 3407 就出自这篇的题名。
- 我们怎么用：现有区间都是按患者重抽，量的是 VAL 病人抽样的不确定，没量"同一配方再训一次差多少"。K1 减 v1 是 −0.0022，K2 减 K1 是 −0.0011（验证集），都可能小于一次重训的波动，结论只能是"没涨"，排不出先后。要量训练波动，至少同配置换种子再训一次（T2，20 GPU 小时）。导演 09-18 定过三种子不强制，这一次做不做请导演定。
- 限制：这些数来自分类和强化学习，分割模型的波动要自己量。

在我们的预算里怎么做。v1 和 K1 两个角已有，K2 在 K1 上多了刷新、B6 倍率也不同，只能当半个重复。不训练的 D1 到 D6 和推理端全因子 T3 先做，合计几个到十几个 GPU 小时。随后训两次：对 B1 难负样本做 2×2 析因 T1（K1 去掉它、v1 加上它），约 40 GPU 小时，两张卡一天出结果，得到主效应、交互和两人沙普利值。B1 若能解释加笔损失的大头，就直接改 B1 训下一版；解释不了，再把 B2 和 B3 到 B6 当第二个玩家组补 2 次。要解读 0.01 以内的差，先做 T2。

### A2 损失项之间的干扰

这一类能回答：哪一项的梯度在和"把 T 修回来"对着干，哪一项量级太大。答不了：VAL 成绩会怎么变，梯度诊断只看局部一步。

《Gradient Surgery for Multi-Task Learning》（PCGrad），Yu 等，NeurIPS 2020。核查：本轮读了定义和 NYUv2 表。领域十二写过方法，这里补两点。

- 思想：两项梯度余弦（gradient cosine，两项更新方向的夹角）为负叫冲突。作者认为多任务难训是三件事同时出现：方向冲突，某一项梯度大得多、压住别项，损失面曲率高。
- 原文数字和条件：NYUv2 三任务、MTAN 结构，分割 mIoU（各类平均交并比）等权 17.72，不确定性加权 17.67，再加 PCGrad 20.17。
- 我们怎么用：K 满足"量级差很多"这一条。第 10k 到 40k 步，难负样本的梯度范数均值 14.79，target Dice 项 6.17（训练日志）。D2 里分加笔、删笔单元，把各项对参数的梯度两两求余弦；难负样本和 target Dice 在加笔单元上若长期负余弦，就坐实"互相顶"。
- 限制：PCGrad 只改方向不改量级；Xin 2022、Kurin 2022 的复查里，它没稳定赢过调好的加权求和。

另外几种自动调权：GradNorm（Chen 等，ICML 2018）、不确定性加权（Kendall 等，CVPR 2018）、MGDA（Sener 与 Koltun，NeurIPS 2018），方法和数字见领域十二，本轮只核了摘要页。CAGrad（Liu 等，NeurIPS 2021）在平均梯度附近找让最差那项改善最多的方向，NYUv2 上平均相对掉分 CAGrad 0.20%、MGDA 1.38%、PCGrad 3.97%、等权 MTAN 5.59%。

《Do Current Multi-Task Optimization Methods in Deep Learning Even Help?》，Xin 等，NeurIPS 2022；《In Defense of the Unitary Scalarization for Deep Multi-Task Learning》，Kurin 等，NeurIPS 2022。核查：本轮读了摘要，正文在领域十二核过。两篇的结论一致：专门的多任务优化器没有超出调好权重的加权求和（scalarization，各项损失乘权重相加）。对我们：先把各项量级对齐到同一尺度，比换优化器优先。

《Efficiently Identifying Task Groupings for Multi-Task Learning》（TAG），Fifty 等，NeurIPS 2021。核查：本轮读了方法和结果段。

- 思想和方法：lookahead（前瞻：先只沿一项损失走一步，看另一项损失变多少）。定义 Z(i→j)＝1−L_j(沿 i 走一步之后)/L_j(之前)，为正是 i 帮 j，为负是拖累；每 10 步算一次，随训练顺带得到。
- 原文数字和条件：CelebA 上和穷举得到的最佳分组相关 0.93；Taskonomy 上测试损失比所有任务一起训低 10.0%，比 HOA 方法快 11.6 倍。
- 我们怎么用：这是 D2 最直接的做法。在 K1 的 最终权重上取一批 TRAIN 加笔单元，只沿难负样本项走一小步，看 target Dice 项、T 召回、error 那一路在 T 上的过线比例怎么变；边界排序、软 Dice 收益、同目标一致性各做一次。哪一项的前瞻值最负，哪一项就最像保守的来源。几百次前向反传，不到 1 GPU 小时。
- 限制：只看一步，累积效应要靠 T1。

按正负号拆梯度（EQL v2 的累计正负梯度比、ASL 的概率差）是这次最该加的诊断。它们同时是"负例把正例压下去"的直接证据，放在 B4 写。

在我们的预算里怎么做。D2 一次出三张表：各项对 T 内圈、T 外圈、O、P 体素 logit（概率之前的原始分数）的梯度方向和大小，分加删；各项参数梯度的两两余弦；TAG 式前瞻矩阵。都在已有 最终权重上做。下一次训练时，新增各项一律按同一规则把梯度量级标定到 target Dice 项。B6 当初只标定了软 Dice 收益一项，其余新项权重固定为 1，难负样本于是长到 2.4 倍。这条规则是通用的，不看 VAL。

### A3 表示比较

这一类能回答：v1 和 K 的分歧在主干特征还是在输出头。答不了：分歧是不是掉分的原因。

《Similarity of Neural Network Representations Revisited》，Kornblith 等，ICML 2019。核查：本轮读了定义和表 2。

- 思想和方法：CKA（中心核对齐：比较两个网络在同一批输入上某一层的表示有多像），线性版只要两组特征矩阵。
- 原文数字和条件：同结构、不同初始化的网络，按"哪层最像哪层"找对应层，线性 CKA 准确率 99.3%，CCA 1.4%、SVCCA 9.9%、PWCCA 11.1%、线性回归 45.4%。网络变宽时浅层先变得相似，深层在不同种子之间更不像。
- 我们怎么用：D5 算 v1 对 K1、K1 对 K2 两组逐层 CKA。K1、K2 配方几乎一样，可以当"重训一次大约多不像"的参照。v1 对 K1 在主干上和 K1 对 K2 一样像、只在头部分开，就说明 K 改的是决策，门槛和头部的便宜改法更可能有效。
- 限制：见下面 Ding 2021。

SVCCA（Raghu 等，NIPS 2017）是更早的表示相似度方法，发现网络自下而上收敛，浅层先稳定。它最适合比较训练中途的 checkpoint；项目按规矩只留最后一个 checkpoint，这一用法本轮做不了。

《Grounding Representation Similarity Through Statistical Testing》，Ding、Denain、Steinhardt，NeurIPS 2021。核查：本轮读了 CKA 敏感度段。

- 原文数字和条件：BERT 最后一层要删掉 97% 的主成分，CKA 才认出和"换种子"一样大的差别，而此时线性探针准确率已从 80% 掉到 63%。CKA 主要看最大的几个方向；作者推荐正交普氏距离（Orthogonal Procrustes，旋转对齐后两组特征差多少）当稳健的基线。
- 我们怎么用：CKA 说"像"，证明不了功能一样。D5 要配功能探针：在冻结的 v1、K1 特征上各训一个线性分类器（linear probe，线性探针），分"加笔时 T 对 P"，比两者的 AUC（区分能力，0.5 等于瞎猜，1 是满分）。
- 限制：语言模型上的结论。

在我们的预算里怎么做。D5 从 TRAIN 抽几百个单元提特征，算 CKA 和正交普氏，训线性探针，不到 1 GPU 小时。

### A4 按样本看训练动态

这一类能回答：保守从哪一步开始，哪类训练单元学会了又忘掉。答不了：已经训完的 K1、K2，中途 checkpoint 没留。

《Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics》，Swayamdipta 等，EMNLP 2020。核查：本轮读了定义和结果段。

- 思想和方法：dataset cartography（数据地图：按训练中的置信度和波动给样本分区）。每个样本在各 epoch 上对真标签的平均概率、波动、判对比例，分成好学、难学、摇摆三区。
- 原文数字和条件：只用最摇摆的 33% 训练，域内成绩离全量只差 0.2%，域外更好；在人工翻转标签的 WinoGrande 上，被分到"疑似错标"的样本 67% 确实错标或有歧义，"正常"一类只有 13%；用提前停下的模型算出的动态，和完整训练的相关在 0.75 以上。
- 我们怎么用：我们的训练单元每步现抽，没有同一样本看多次。下一次训练加一个固定探针集（D7）：约 200 到 300 个 TRAIN 单元，按加删、T 大小、离笔距离分层，每 1000 步记一次 T 内平均 pT 和过 0.5 的比例。这样能看到加笔单元的置信度从哪一步开始往下走，比如是不是第 1000 步 B6 标定之后。
- 限制：要改训练记录。

《An Empirical Study of Example Forgetting during Deep Neural Network Learning》，Toneva 等，ICLR 2019。核查：本轮读了结果段。

- 思想：forgetting event（遗忘事件：某个样本先判对、后又判错）。
- 原文数字和条件：从没被忘的样本，MNIST 91.7%、置换 MNIST 75.3%、CIFAR-10 31.3%；CIFAR-10 去掉 30% 训练集，成绩仍有竞争力；最常被忘的是错标样本，错标样本没有一个从没被忘过。
- 我们怎么用：在 D7 的探针集上数加笔单元"填回又缩回"的次数。远端 T 体素反复被忘，就说明有一项损失一直在把它压回去。
- 限制：定义要换成"体素过不过 0.5"。

在我们的预算里怎么做。D7 每 1000 步一次前向，40k 步共 40 次，开销可忽略，作为下一次训练的附加记录。

### A5 错误分解

这一类能回答：差距落在哪类错上，每类错补好值多少 Dice。答不了：为什么出这类错，补不补得到。

《TIDE: A General Toolbox for Identifying Object Detection Errors》，Bolya 等，ECCV 2020。核查：本轮读了方法段。

- 思想和方法：检测错误分六类，每类用 oracle（用真值把这一类错改掉的理想上限）单独修，看成绩涨多少；每类都从原始结果出发，不累加。
- 原文要点：作者演示了逐类累加着修时，换个顺序，背景误检的贡献会大变，累加法会误导。
- 我们怎么用：D6 把 K 与 v1 的差距分成加笔 T 没填满（离笔 15、30、60 mm 分段）、加笔误加、删笔误删、删笔没删干净、顺手修了 O 几类，每类从同一状态单独补齐，各算 Dice 变化，再报全部一起补的值。第一轮分析里"30 mm 内补齐 +0.062、30 mm 外 +0.015"（验证集）就是这种算法，要核一下两者是各自独立算的。
- 限制：只说值多少。

autoPET 比赛的病灶级指标（官方评测页）。核查：本轮读了评测页。FPV（假阳性体积）是和真值完全不重叠的预测连通块的体积，FNV（假阴性体积）是和预测完全不重叠的真值连通块的体积，有一点重叠就不算；排名按 Dice 50%、FPV 25%、FNV 25%。对我们：加笔失败分两种，整块没碰到（进 FNV）和碰到了没填满（只影响 Dice）。第 1 轮修回中位比例从 53.7% 降到 17.5%（验证集），看着是后一种，要用 FNV 式统计核一下。

《Metrics reloaded: recommendations for image analysis validation》，Maier-Hein、Reinke 等，Nature Methods 21:195–212，2024。核查：本轮读了摘要。一句话：按"问题指纹"挑指标，多病灶问题要配实例级指标，只报整体 Dice 不够。

在我们的预算里怎么做。D6 在已有轨迹文件上算，不用 GPU。

### A6 反事实输入消融和因果中介

这一类能回答：网络到底用没用某个输入，比如 B3 的上一轮实际改动、B2 的不截断距离。答不了：这个输入在训练中帮没帮忙，那要重训。

《A Benchmark for Interpretability Methods in Deep Neural Networks》（ROAR），Hooker 等，NeurIPS 2019。核查：本轮读了方法和结果段。

- 思想：测试时直接去掉输入看掉多少分，会混进"输入变成没见过的样子"的影响。ROAR（去掉再重训）把去掉后的数据重新训练再比。
- 原文数字和条件：ImageNet 随机替换 90% 像素再重训，ResNet-50 仍有 63.53%，干净数据是 76.68%；多数梯度类解释方法在 ROAR 下不比随机好。
- 我们怎么用：D4 把 B3 输入置零，测的是"推理时拿掉"，会混进分布外的影响。好在第 1 轮训练时这一通道本来就是零，置零接近训练时见过的样子；更干净的做法是换成同一扫描别的轮次的真实改动图。要回答"训练时用没用"，只能靠 T1 那样的重训。
- 限制：重训成本高。

《Towards Best Practices of Activation Patching in Language Models: Metrics and Methods》，Zhang 与 Nanda，ICLR 2024。核查：本轮读了结论段。

- 思想和方法：比较 activation patching（激活替换：把一层输出换成另一个输入下的输出，看结果怎么变）的几种做法：加高斯噪声破坏，或对称替换成一个合理的同类输入；看概率，或看 logit 差。
- 原文结论：高斯噪声把模型带出训练分布，会给出误导的定位；推荐对称替换和 logit 差。
- 我们怎么用：D4 换成别的真实改动图，不加噪声；看 pT 的 logit 差，不只看过没过 0.5。

《Investigating Gender Bias in Language Models Using Causal Mediation Analysis》，Vig 等，NeurIPS 2020。核查：本轮读了定义段。

- 思想：causal mediation（因果中介分析）把输入改动的总效应拆成直接效应和经由某些中间单元的间接效应。GPT-2 small 里，只要 10 个注意力头就能达到干预全部 144 个头的效果。
- 我们怎么用：B3 如果有用，再问它经由哪一路起作用：把某一路的中间特征换成"B3 置零后"的值，看第 2 到 5 轮加删笔的 Dice 变化。要改推理代码，排在 D4 之后。

遮挡法出自《Visualizing and Understanding Convolutional Networks》（Zeiler 与 Fergus，ECCV 2014）：用灰块遮住输入的一块，看输出掉多少。对我们可以测"离笔多远的影像还在影响 pT"。

在我们的预算里怎么做。D4 每种置换跑一次第 2 到 5 轮的 VAL 回放，小时级，本文没有实测时长。

### A7 校准和门槛

这一类能回答：K 的加笔保守是"分数整体偏低、排序没坏"，还是排序也坏了；前者不用重训。答不了：门槛一动，后几轮的状态会怎么变，要实跑五轮。

先算我们自己的账，推导见领域五。加笔每加对一个病灶体素赚 2−D 份、加错一个背景体素赔 D 份，所以边际体素是病灶的概率高于 D/2 就该加；删笔反过来，边际体素被误删的概率要低于 D/2。验证集起点 Dice 约 0.61，加笔的盈亏线约 0.30，删笔要"删对的概率"高于约 0.70。第 1 轮的实际情况（验证集，全部扫描合计体积）：

- 加笔加进去的体积里，真病灶（T 加 O）占比 v1 约 68%（708.4/1047.5 ml），K1 约 86%（375.0/437.7 ml），K2 约 79%（486.0/615.7 ml）。都远高于 0.30，边际上很可能还有该加没加的。
- 删笔删掉的体积里，删对的占比 v1 约 75%（193.6/257.8 ml），贴着 0.70；K1 约 93%（69.7/75.1 ml），K2 约 93%（74.0/79.7 ml）。
- 这是合计体积上的平均，不是边际，也没按每例的 D 算，要 D1 逐例逐门槛算才作数。方向上它和观察吻合：K 把两个方向都收严，删笔收对了，加笔收反了。

《On Calibration of Modern Neural Networks》，Guo 等，ICML 2017。核查：本轮读了定义和结果段，领域五也核过。

- 思想和方法：temperature scaling（温度缩放：用一个数整体缩放 logit）在留出集上拟合，不改哪类分数最高；二分类的 Platt scaling（普拉特缩放：斜率加偏置两个参数）属于同一族。
- 原文数字：CIFAR-100、ResNet-110 的 ECE（期望校准误差：置信度和实际正确率的平均差）从 16.53% 降到 1.26%。
- 我们怎么用：只用温度时 0.5 的分界不动，要移动执行门槛得有偏置项。D1 先比 v1、K1、K2 在"加笔的 T"与"可改正确区"之间的排序（AUC），排序相当就说明问题在偏置，每个符号学一个偏置就够。
- 限制：校准好不等于 Dice 高。

《Local Temperature Scaling for Probability Calibration》，Ding、Han、Liu、Niethammer，ICCV 2021。核查：本轮读了方法和结果段。

- 思想和方法：用一个小网络给每个体素预测自己的温度，因为物体内部和边界的失校准程度不同。
- 原文数字和条件：LPBA40 脑 MRI、U-Net，ECE 全局温度 1.43%，逐体素温度 0.90%；正温度不改各类排序，分割结果不变。
- 我们怎么用：我们的偏差可能随离笔距离变，远端 pT 被压得更低。可以按离笔距离分几档、每档一个偏置，只在 TRAIN 回放上拟合，比逐体素网络简单。
- 限制：只改校准，排序坏了它救不回。

《Long-tail learning via logit adjustment》，Menon 等，ICLR 2021。核查：本轮读了方法和表 3。

- 思想和方法：类别不均衡时，训练出的分数系统偏向多数类；推理时在 logit 上减去 τ·log(类先验)（logit adjustment，按先验在原始分数上加减一个常数）就能纠正，理论上 τ＝1，也可以把同样的调整写进损失。
- 原文数字和条件（balanced error，各类平均错误率，越低越好）：CIFAR-10-LT 普通训练 27.16%，事后调整 22.60%，写进损失 22.33%；ImageNet-LT 依次 53.11%、49.66%、48.89%。
- 我们怎么用：事后调整拿回了写进损失的大部分收益，偏置类问题可以先不重训。调整量原则上能由 Dice 账推出（加笔对应 logit(D/2)），前提是 pT 先在 TRAIN 回放上校准过。领域五测过每笔最优门槛和当时 D 的相关只有 −0.05（加笔）和 0.02（删笔）（验证集），所以更现实的做法是每个符号一个常数偏置，在 TRAIN 回放上学。
- 限制：τ 的理论值要求概率已校准。

在我们的预算里怎么做。D1 一次：三个模型，第 1 轮，整卷 pT 按符号、T/O/P、离笔距离分段做直方图，加门槛扫描，小时级。VAL 上的门槛扫描只作诊断；按导演 10-03 的规矩，门槛要在 TRAIN 回放上按固定规则学出来，再拿到 VAL 跑一次五轮。

### A8 交互分割的评测方法

这一类能回答：我们的 VAL 口径会不会总是高估或低估某一种笔。答不了：真人会怎么画。

《Deep Interactive Object Selection》，Xu 等，CVPR 2016。核查：本轮读了评测段。

- 内容：最早的深度交互分割之一。评测时自动把下一次点击放在"离当前选区边界和图像边界最远的错分像素"，也就是最大错误区的中间，后来的 NoC@85/90（到达目标 IoU 要点几次）都沿用这种模拟。训练时负点击用三种采样：背景随机、其他物体上、沿物体外缘。作者还写到，直接在 0.5 处切概率图得到的掩膜很粗，他们改用图割在概率图上细化。
- 我们怎么用：我们的机器人用户也画当前最大的错，K 在一块大漏标上修得少，下一轮还会画同一块。后几轮加笔几乎没起作用（修回不到 1%）的比例，v1 是 1/189，K1 是 57/232，K2 是 40/212（验证集）。这种"白画一轮"相当于交互分割里的失败率（failure rate，规定次数内到不了目标的比例），应该单列。
- 限制：二维点击。

《Large-scale interactive object segmentation with human annotators》，Benenson、Popov、Ferrari，CVPR 2019。核查：本轮读了模拟噪声和真人两节。

- 原文数字和条件：模拟点击加 3 像素和 6 像素的高斯位置噪声，mIoU（平均交并比）分别掉 3% 和 7%；真人 60% 的点击大致按错误区从大到小的顺序（30% 完全按此顺序），平均每个实例 11.4 秒。
- 我们怎么用：真人也先修大错，和我们的机器人一致；但真人画不准，对笔的位置敏感的模型到了真人手里会掉分。
- 限制：自然图像。

《Rethinking Annotator Simulation: Realistic Evaluation of Whole-Body PET Lesion Interactive Segmentation Methods》，Marinov 等，arXiv 2024。领域一已写。补数：autoPET FDG 上 25% 的真人点击落在标注外；常规机器人和真人的 Dice 差 8.7 个点（研究 1）和 7.0 个点（研究 2），新机器人降到 3.6 和 3.7。

autoPET IV 任务 1 的评测（官方评测页和 GitHub 说明）。核查：本轮读了评测页和 README。

- 协议：11 步，从 0 次点击到 10 个病灶点加 10 个背景点，每步加一对。点击按真值事先模拟好：用连通块和欧氏距离变换取病灶中心或边界，带随机偏移，不随模型的预测变。指标是最后一步的 Dice、FPV、FNV，加上三者随步数的曲线下面积（梯形法），排名权重依次 0.25、0.125、0.125、0.25、0.125、0.125。
- 我们怎么用：它的点击不看模型错在哪，和我们、2S-ICR、UAM"画在当前最大错误上"不同，autoPET IV 的分数和我们的轨迹分数不能直接比。我们的主指标是六个状态 Dice 曲线的标准化面积，和它的 AUC-DSC 是同一类量。
- 限制：官方总结论文本轮打不开（SSRN 返回 403），前几名的数字未核实。

在我们的预算里怎么做。在已有轨迹上加两项统计：每个符号的"白画一轮"比例，同一块错被连续画中的次数，不用 GPU。

## 第二部分 领域文献

### B1 加笔和删笔不对称

这一类能回答：同样的训练改动，为什么在两种笔上效果相反。现状是专门研究正负笔不对称的论文很少，本轮找到的多是"正负点击用法不同"和"损失偏召回还是偏精确"的证据，最硬的解释仍是 A7 里我们自己的 Dice 账。

《DiffClick: Click-differentiated enhancement network for interactive segmentation》，Song 等，Pattern Recognition 171:112217，2026（2025 年在线）。核查：读了作者存档 PDF 的引言摘录和期刊书目信息。

- 思想和方法：正点击找前景、负点击修背景，目的不同，数量也差很多，分两个模块处理；没有负点击时补一个"非目标原型"。
- 原文数字和条件：Pascal 上负点击占全部点击不超过 35%；有负点击时，20 次内到不了 IoU 90% 的失败率低于 3%，没有负点击时失败率高出约 20%（原文没说明是绝对值还是相对值）。
- 我们怎么用：两种笔共用一个头、一套损失，一方就可能吃亏。这支持按符号分开监控、分开定门槛、分开设难负样本的规则。
- 限制：二维点击，数字来自引言的统计说明。

《Tversky loss function for image segmentation using 3D fully convolutional deep networks》，Salehi 等，MLMI 2017；《Asymmetric Loss Functions and Deep Densely Connected Networks for Highly Imbalanced Medical Image Segmentation》，Hashemi 等，IEEE Access 7，2019。核查：本轮读了结果段。

- 原文数字和条件：多发性硬化病灶。Tversky loss（能分别调漏检和误检权重的 Dice 类损失）把漏检权重调到 0.7，灵敏度从 49.85% 到 56.85%，Dice 从 53.42% 到 56.42%（Salehi）。F-beta 损失（β 大就偏召回）取 β＝1.5，灵敏度从 74.49% 到 78.58%，Dice 70.3% 对 69.9%（Hashemi）。
- 我们怎么用：正负两侧在损失里的相对分量，直接决定模型偏召回还是偏精确。K 新加的三项里，边界排序和难负样本都压在负例一侧，等于把加笔的天平往"罚误加"推。
- 限制：两篇的权重都是扫出来的，按导演规矩我们不能这样定。

项目内已有的：BS（Sherif 等 2026，见领域三）背景笔占 69%，误报个数却没降，说明删笔方向要在模型自己的误报上训练。

### B2 局部编辑还是整卷重算：离笔远的地方怎么处理

FocalClick、VISTA3D、RITM、SimpleClick、nnInteractive 在领域一、领域三都写过。这里只补一件事：每种方法怎么处理离点击远的错。

| 方法 | 每轮改哪里 | 离点击远的错 | 上一轮结果怎么进网络 |
|---|---|---|---|
| FocalClick，CVPR 2022 | 先在外扩 1.4 倍的目标框里粗分，再只把"新旧之差里含新点击的最大连通块"并回旧掩膜 | 框外和那一块以外一律保留旧值，修不到 | 上一轮掩膜作输入 |
| VISTA3D，CVPR 2025 | 只接受含正点击的新增连通块、含负点击的删除连通块 | 原文写明一个点击只影响含它的那个 128³ 块 | 自动结果作合并对象 |
| SAM，ICCV 2023 | 每轮整幅重出 | 全图都能改 | 上一轮未阈值化的掩膜 logit 以四分之一分辨率作稠密提示 |
| nnInteractive，arXiv 2025 | 块内重出；预测碰到视野边就放大 1.5 倍、最多 4 倍，再滑窗细化 | AutoZoom（自动缩放）让大目标能整块分出 | 网络接收自己最新一次的预测 |
| SimpleClick，ICCV 2023 | 每次点击整幅重出 | 全图 | 上一轮分割和正负点击盘图合成三通道，单独嵌入后与图像相加 |
| RITM，ICIP 2022 | 整幅重出 | 全图 | 上一轮掩膜作输入，训练时让模型自己跑几步 |
| 2S-ICR，Sci Rep 2025 | 整卷重出 | 全卷 | 上一轮的 sigmoid 概率（sigmoid 把分数压到 0 到 1） |

《Segment Anything》（SAM），Kirillov 等，ICCV 2023；《nnInteractive: Redefining 3D Promptable Segmentation》，Isensee 等，arXiv 2025。核查：本轮读了 SAM 的交互训练段，nnInteractive 的输入、模拟和 AutoZoom 段，下面的引文是原句的译文。

- SAM：每个掩膜训练时模拟 11 轮交互，后续点从"上一轮预测和真值之差"的区域里均匀抽；上一轮的掩膜 logit 喂回网络，每轮整幅重出。
- nnInteractive：原文写"网络还接收它最新一次的预测作为额外输入"；加新交互时，旧交互的强度乘 0.9 衰减；训练时"随机选一个错误连通块，概率和它的大小成正比"；预测碰到视野边缘时 AutoZoom 放大视野。
- 我们怎么用：整卷重算的方法不按离笔远近决定改不改，靠的是"上一轮预测加提示"重新判断；训练时错误块按大小抽，大块（远端体积多的块）天然得到更多训练。SIRB 每轮也算整卷 pT，但网络被 B1 训得"拿不准就别动"，执行端又只改 pT≥0.5、只许朝笔的符号改，两层保守叠在一起。
- 限制：nnInteractive 能接一份已有分割，但没有报"离提示多远修回多少"，这个量本次检索没见到任何三维方法报过。

### B3 把上一轮概率图喂回网络

《MFP: Making Full Use of Probability Maps for Interactive Image Segmentation》，Lee、Lee、Kim，CVPR 2024。核查：本轮读了全文。

- 思想：上一轮概率图里有物体形状的信息，比如自行车轮子的轮廓。常规做法把它当一个输入通道，进了主干就被稀释，没传到当前预测上。
- 方法：先用这一次点击调制上一轮概率图。在点击周围的窗口里做 gamma correction（伽马校正：用幂次把概率往 1 或 0 推），正点击往 1 推、负点击往 0 推；窗口半径默认 100 像素，有反向点击时取到最近反向点击距离的一半。前 7 次点击按"和点击处的概率相不相近"决定推多少，不看直线距离，之后改按直线距离。原概率图和调制后的概率图都送进网络，并在输出头前再接一次（late fusion，后融合）。训练按"每次点在最大错误区中心"递归跑到 24 次点击。
- 原文数字和条件：DAVIS 消融，ViT-B、SBD 训练，NoC@85/90/95：基线 4.10/5.60/11.58，去掉后融合 4.05/5.30/11.54，去掉递归训练 3.98/5.35/11.79，完整 3.92/5.32/11.27。定性图里其他方法在离点击远的地方（车轮）分错，MFP 分对。
- 我们怎么用：概率图起作用的地方正是"远处的形状"，对着我们 65% 在 30 mm 外的漏标体积（验证集）。"概率相近就一起推"是一种不受直线距离限制的传播。后融合说明，要让一个输入真正起作用，可以在头前再接一次。
- 限制：二维自然图像；窗口和"前 7 次"都是人定的数；增益不大，NoC@90 少 0.28 次。

《Interactive 3D segmentation for primary gross tumor volume in oropharyngeal cancer》（2S-ICR），Saukkoriipi 等，Scientific Reports 2025。核查：本轮读了 PMC 正式版。领域三引的是 arXiv 版，几个数字略有不同，以下按正式版。

- 方法：修正网络 5 个输入通道：PET、CT、上一轮的 sigmoid 概率（连续值，不二值化）、正负点击的三维高斯热图。每次交互整卷重出；点击按到错误区边界的距离加权抽，偏向大错误；每例训练时随机 1 到 15 次交互；mask dropout（掩膜丢弃：训练时以概率 p 把上一轮分割换成全 0.5）。
- 原文数字和条件：表 5，1 到 10 次点击的平均 Dice 和每次改动的体素数，p＝0 时 0.815、1847 个，p＝0.2 时 0.846、3108 个，p＝0.4 到 0.8 稳在 0.844 到 0.845。HECKTOR 五折交叉验证 0、1、5、10 次点击 Dice 依次 0.752、0.787、0.850、0.870；MDA 医院外部测试 0.722、0.773、0.835、0.858。
- 我们怎么用：表 5 是最直接的旁证。网络太依赖上一轮分割时改得少、Dice 低；随机拿掉这个输入，改得多了、Dice 高了。K 的 B3 读系统上一轮的实际改动，B4 用教师回放的状态，都可能加重"照着上一轮、少动"；给 B3 输入加随机丢弃几乎不花成本。它喂概率、不喂 0/1 掩膜，也支持概率图输入。
- 限制：头颈原发灶、点击协议，Dice 不能和全身 PSMA 比。

项目已定的规矩。09-19 的决定（`D-2026-09-19-03` 第 3 项）把基座概率图从网络输入里拿掉，理由是去掉对基座的依赖、给换起点的迁移实验留路，训练时挑加笔难负例仍用基座的折外概率；当时约定，"加回概率图"的原型比较只在出现明显退化时才回来找导演。文献站在喂概率图一边，但这件事改的是方法设计，需要导演定：

- 甲：维持现状，不喂。
- 乙：喂基座概率图，训练时随机丢弃（2S-ICR 的做法，术语表里已有"p0 dropout"这个说法），推理时没有基座概率也能跑；代价是迁移实验的说法要收窄。
- 丙：只从第 2 轮起喂 SIRB 自己上一轮的 pT（MFP、nnInteractive 喂的都是模型自己的上一轮输出），不依赖基座；但损失最大的是第 1 轮，这条帮不到第 1 轮。

我的推荐是先甲，等 D1 和 T1 的结果。B1 改好之后，第 1 轮加笔若仍明显不如 2S-ICR，再开乙。参照数：45 个共有扫描（29 位患者）上，2S-ICR 第 1 轮从 0.4728 涨到 0.6420，约 +0.169；v1 用同一画法从 0.5428 涨到 0.6499，约 +0.107（验证集）。

### B4 难负例和保持类损失让模型变保守

这一类和这次失败最相关。能回答：B1 为什么会让加笔变保守，有哪些已知的改法。证据分七组。

挑难例的标准做法是"按损失挑，正负都有份"。《Training Region-based Object Detectors with Online Hard Example Mining》（OHEM），Shrivastava、Gupta、Girshick，CVPR 2016；《Focal Loss for Dense Object Detection》，Lin 等，ICCV 2017；《Bridging Category-level and Instance-level Semantic Image Segmentation》，Wu、Shen、van den Hengel，arXiv 2016。核查：本轮读了相关段落。

- 原文要点和数字：OHEM（在线难例挖掘）每张图按损失排序，只回传最难的区域；作者写明它不需要前景背景 1:3 的配比，因为哪一类被忽略，它的损失就会升高、就会被选上。VOC 2007 上 Fast R-CNN（VGG16）从 67.2 到 69.9 mAP（平均精度，检测的常用总分，AP 是同类指标）。focal loss（给易分样本降权的交叉熵）在 ResNet-101-FPN 上 36.0 AP，最好的 OHEM 设置 32.8 AP；γ＝0 时最佳正例权重 α＝0.75，γ＝2 时降到 0.25，作者的解释是大量易分负例主导了损失和梯度。分割里的自举损失（只留最难的 512 个像素）在 VOC 上从 73.41% 到 74.80%，Cityscapes 上从 71.51% 到 74.64% mIoU（表 7）。
- 我们怎么用：三种做法都在全部样本里按难度挑，正例被忽略时会自动被挑回来。K 的难负样本只在 O、P 里挑，T 一侧没有对应的难正例，缺了这个自动平衡。改法之一：在 T、O、P 全体里按损失挑难例，或给加笔补一个对称的难正例项（T 里 pT 最低的 |T| 个体素）。
- 限制：检测和自然图像分割。

只挑最难的负例，会推走挨着的正例，或者让训练塌缩。

《Sampling Matters in Deep Embedding Learning》，Wu、Manmatha、Smola、Krähenbühl，ICCV 2017。核查：本轮读了全文相关段。

- 思想：最难的负例离锚点最近，梯度方向被噪声主导，在三元组损失（triplet loss，拉近同类、推远异类）下常导致塌缩，所有样本嵌到一点；半难负例只在一条窄带里，训练会停滞。
- 原文数字和条件：Stanford Online Products 从零训练的 Recall@1（检索时排第一的结果就对的比例），对比损失随机采样 30.1、半难采样 49.4；作者的间隔损失随机 37.5、半难 61.0、按距离加权采样 61.7。
- 我们怎么用：难负样本取"pT 最高的 |T| 个 O、P 体素"，按定义集中在 T 外边一圈和长得像病灶的 O 上，正是"最难、离正例最近"的那一段。按 pT 加权抽并设上限，比只取最高的稳。
- 限制：度量学习。

《Hard negative examples are hard, but useful》，Xuan、Stylianou、Liu、Pless，ECCV 2020。核查：本轮读了方法和结果段。

- 思想：最难的负例和锚点几乎一样时，把锚点拉向正例的更新会把负例一起拉过来，作者叫它 entanglement（纠缠）；只用最难负例会在训练早期陷进坏的局部最优。
- 方法和数字：对"负例比正例还近"的三元组，只用推开负例的对比项，不同时拉近正例。Recall@1：Hotels-50K 半难 18.78、他们的方法 29.24；CUB 56.7 对 57.7；CAR 67.9 对 73.4；SOP 81.0 对 81.9。
- 我们怎么用：这是和 B1 最像的机制。T 内边一圈和外边一圈只隔一个体素，感受野几乎重叠，PET 上边界又常常模糊，网络很难给出相反的分数；边界排序和难负样本在外圈往下压，会把内圈一起压下去，表现就是笔附近都填不满。第 1 轮离笔 15 mm 以内的漏标，v1 修回 81.0%，K1 43.7%，K2 50.2%（验证集）。这是推测，D2 里看 T 内圈 logit 的梯度方向能核。
- 限制：跨领域类比。

最难的负例里混着"其实是同类"的样本。《Contrastive Learning with Hard Negative Samples》，Robinson、Chuang、Sra、Jegelka，ICLR 2021；《Debiased Contrastive Learning》，Chuang 等，NeurIPS 2020。核查：本轮读了方法和图 4 的说明。

- 要点：无监督对比学习里，离锚点最近的负例很可能是同类，也就是假负例。Robinson 等的实验里，负例越难（集中参数 β 越大）不一定越好；只有用真实同类信息去掉假负例时，成绩才随 β 单调上升；难例加去偏一起用最好。
- 我们怎么用：O 里的漏标病灶外观上和 T 同一类，只是"这一笔没指它"。把它们当最难的负例，等于逼网络用外观以外的线索（离笔多远）把它们分开，而远端信息正是 K 学不动的（可学半径从 60 mm 只走到 61 mm，远端块只放进约 0.13% 的训练单元，训练日志）。外观上一压，T 自己也被压。
- 和网络结构对上的推测机制：K 用三类平铺的头，T、O、P 三个概率相加为 1，error 那一路的分数是 pT＋pO。难负样本在 O 体素上罚 −log(1−pT)，按 softmax（把几项分数变成加起来等于 1 的概率）的梯度，它把 T 的概率按 pO 与 pP 的比例同时推给 O 和 P，推给 P 的那一份降低了"这里是错"的总分。O 和 T 长得一样，这份压力会连带压低 T 上的 error 分数。训练日志诊断（最后 2000 步均值）里，error 那一路在 T 上的过线比例从 v1 的 0.88 降到 K1 的 0.68、K2 的 0.67，T 召回从 0.82 降到 0.60、0.58，和这个推测一致。
- 对应的改法按 T/O/P 定义直接推出：O 体素只罚"T 相对 O 的比例"，写成 −log(pO/(pT＋pO))，不罚"它是错"；P 体素照旧。D2 里看难负样本项在 O 体素上把概率推给了 O 还是 P，就能核这条。
- 限制：对比学习的结论，搬到分割要打折扣。

按正负号量梯度，能直接看出"正例被淹没"。

《Equalization Loss v2: A New Gradient Balance Approach for Long-Tailed Object Detection》，Tan 等，CVPR 2021。核查：本轮读了引言和方法段。

- 思想和方法：对每个类别的分类器，分别累计正样本和负样本给输出 logit 的梯度，用两者之比判断训练是否平衡；比值低就加大正梯度、减小负梯度。
- 原文结论和条件：LVIS 上头部类的比值接近 1，尾部类接近 0，作者原话是正梯度被负梯度淹没（long-tailed，长尾：少数类别样本极少）；相对 Mask R-CNN 等基线，整体 AP 约多 6 个点，尾部类多 17 到 20 个点，比 EQL 多约 4 个点。
- 我们怎么用：D2 最该加这张表。在 K1、v1 的 最终权重上取加笔单元，分别累计各项损失对 T 体素 logit 的上推梯度和对 O、P 体素的下压梯度，算比值；删笔再做一遍。K1 加笔的比值若远低于 v1、删笔差不多，B1 就是加笔保守的直接原因。训练时也可以每 200 步记一次这个比值。
- 限制：检测的分类头；我们的正负体素数本来受 |T| 配额控制，比值要按体素数归一。

《Asymmetric Loss for Multi-Label Classification》，Ridnik 等，ICCV 2021。核查：本轮读了 2.6 节和表 4。

- 思想和方法：多标签分类里负标签远多于正标签，负例主导优化，正例的梯度被低估。对正负样本用不同的聚焦参数，负例降权更多，并把很容易的负例直接截掉。用 probability gap（概率差：正样本平均概率减负样本平均概率）监控不对称，负例的聚焦参数可以跟着概率差自动调。
- 原文数字和条件：MS-COCO 上用交叉熵和 focal loss 训完，概率差分别是 −0.23 和 −0.1，正样本的平均概率反而低于负样本；ASL 用 TResNet-L、448 输入，mAP 86.6%。
- 我们怎么用：概率差是现成的监控量：加笔单元里 T 体素的平均 pT，减去被选中的难负体素的平均 pT。训练日志里这个差若随步数缩小，就和加笔变保守对上了。
- 限制：多标签分类。

《Soft Sampling for Robust Object Detection》，Wu、Bodla、Singh、Najibi、Chellappa、Davis，BMVC 2019。核查：本轮读了结果段。

- 原文数字和条件：PASCAL VOC 随机去掉 30% 的标注，这些物体被当成背景，Faster R-CNN 从 81.28% 掉到 76.75%；按和已标正例的重叠给背景区域降权（soft sampling，软采样），回到 78.24%，上限 79.26%；OpenImages V3 的 50 类子集上从 42.57% 到 45.92%。另有检索摘录说，Niitani 等（CVPR 2019）在稀疏标注的 COCO 上调过参也没让软采样赢过基线，原因是降权太多、负例贡献不足；这篇原文本轮没读，未核实。
- 我们怎么用：O 就像"没标的物体"，它是真病灶，只是这一笔不负责。给 O 降权比完全不罚稳妥，降多少按通用规则定，例如按 O 体素到笔的距离，不按 VAL 调。
- 限制：检测。

边界类损失单独用会塌到空前景。《Boundary loss for highly unbalanced segmentation》，Kervadec 等，MIDL 2019（期刊版 MedIA 2021）。核查：本轮读了方法讨论段。原文写明，单用边界损失时网络很快塌到空前景，softmax 输出接近 0，所以要和区域损失（广义 Dice）一起用，并让边界损失的权重随训练逐步加大。对我们：B1 的边界排序只作用在 T 内外两圈，方向和边界损失相近；K 里它和 target Dice 同时开，不至于塌空，但"先让区域项立住、再逐步加边界项"是按训练进度定的现成做法。作者没给"两者同时开时偏多少"的数。

保持类损失让笔附近改得少、远处保得好。《From Sparse to Precise: A Practical Editing Approach for Intracardiac Echocardiography Segmentation》，Shahin、Zhuang、El-Zehiry，MICCAI 2023。核查：本轮读了损失定义和表 1。

- 方法：编辑损失＝笔附近（三维高斯权重 A，σ 经交叉验证取 20）对真值的交叉熵，加上远处（1−A）对原分割的交叉熵。
- 原文数字和条件：605 例五折交叉验证，95 分位距离误差（mm），近处 / 远处：交叉熵 0.577/0.849，Dice 损失 0.57/0.892，InterCNN 0.517/0.561，编辑损失 0.621/0.182；107 例测试集，编辑损失近处 0.662、远处 0.184。
- 我们怎么用：表里能直接看到代价，远处保得最好的编辑损失，在笔附近的误差反而最大。K 删笔误删少（保得好）、加笔在笔附近填不满，方向一致。作者没讨论这个代价，是我们从表里读出的。
- 限制：心腔超声，误差是距离不是 Dice。

一致性项的平凡解。《Exploring Simple Siamese Representation Learning》（SimSiam），Chen 与 He，CVPR 2021。核查：本轮读了塌缩实验段。两支互相对齐的一致性目标，如果两边都回传梯度，会塌到常数输出：ImageNet 线性评估 0.1%，一侧截断梯度（stop-gradient）后 67.7%。对我们：B5 里"同一目标换画法"的一致性项，梯度范数 3.89，和 target Dice 的 6.17 同量级（训练日志）；如果两边都回传，最省力的解是两种画法都只填它们都覆盖的那一小块，也会往保守推。这条是推测，排在 B1 之后，要看这一项是否只把一边当目标。

### B5 把一笔的影响传到远处

先摆位置：我们第 1 轮加笔所指的漏标体积 65.3% 在离笔 30 mm 外，三个模型在 30 mm 外只修回 2.3% 到 2.9%；但把 30 mm 外全补齐的理想收益只有约 +0.015，30 mm 内是 +0.062（验证集，用真值）。远端排第二。

《DeepIGeoS: A Deep Interactive Geodesic Framework for Medical Image Segmentation》，Wang 等，TPAMI 2019。领域四已写。补数：同一批笔、一轮纠错，二维胎盘 Dice 欧氏距离 88.26%、测地距离 88.76%，三维脑肿瘤 88.82%、89.30%；纠错网络的输入里有第一阶段网络的初始分割。

《MIDeepSeg: Minimally Interactive Segmentation of Unseen Objects from Medical Images Using Deep Learning》，Luo 等，Medical Image Analysis 72:102102，2021。核查：本轮读了表 2、表 6。

- 方法：用指数化测地距离编码用户点（落在目标内边缘附近的点），不带参数；再用测地距离做信息融合细化。
- 原文数字和条件：二维胎盘 / 脾脏 Dice，仅框 85.53/91.36，欧氏 87.56/93.58，高斯 87.91/93.22，测地 87.17/94.02，指数化测地 88.10/95.08；三维肿瘤 87.00，普通测地 86.42。
- 我们怎么用：普通测地距离并不总比欧氏好，胎盘上更差，差别都在 1 个点上下。

《Guiding the Guidance: A Comparative Analysis of User Guidance Signals for Interactive Segmentation of Volumetric Images》，Marinov 等，MICCAI 2023。领域三已写。补数：autoPET（只用 PET）10 次点击后 Dice，实心球 78.15，高斯 78.24，欧氏距离变换 75.22，测地距离变换 74.50，指数化测地 73.19，作者的自适应热图 79.89。PET 病灶上测地编码排在最后几名。

这三篇合起来：测地编码没有"远处填得更好"的直接证据，下一版不加。

《Conditional Diffusion for Interactive Segmentation》（CDNet），Chen 等，ICCV 2021。核查：本轮读了引言和方法段，消融表没取到。

- 问题：常规做法把点击编码成距离图或高斯图和图像拼在一起，点击的标签常常推不到离点击较远、外观几乎一样的目标部分；简单按特征相似度扩散又会溢到别的相似物体上。作者称之为"扩大扩散范围"和"避免过度推广"的两难。
- 方法：特征扩散模块在全图上按特征相似度从点击处往外扩，并用一个粗的前景背景预测约束扩散的目的地；像素扩散模块在 logit 上按颜色相似度在局部反复扩散，遇到边界就停，迭代越多到得越远。
- 我们怎么用：和我们的远端问题是同一件事。"用粗预测约束目的地"对应"用 error 那一路的输出约束 binding 往哪传"。
- 限制：二维；本轮没取到消融数字。

《Depth Estimation via Affinity Learned with Convolutional Spatial Propagation Network》（CSPN），Cheng、Wang、Yang，ECCV 2018；《Non-Local Spatial Propagation Network for Depth Completion》（NLSPN），Park 等，ECCV 2020。核查：本轮读了两篇的方法段和 NLSPN 的结果表。

- 思想：depth completion（深度补全：从稀疏的深度点补出整幅深度图）和"从一笔补出整个病灶"同构。CSPN 用网络学出每个像素和邻居的亲和度，在局部反复传播，每步把已知的稀疏点写回；NLSPN 指出固定的局部邻居会从无关邻居传错、也够不到远处，改由网络给每个像素预测非局部邻居。
- 原文数字和条件：NYUv2、500 个稀疏点，NLSPN 表里 RMSE（均方根误差，米）S2D 0.230、CSPN 0.117、NLSPN 0.092；KITTI 测试集 CSPN 1019.64 mm、NLSPN 741.68 mm。
- 我们怎么用：学出的传播在"稀疏输入补稠密"上收益很大，且非局部邻居比固定局部邻居好。它和领域四的"学出的边加连通"同类，那条已定本月不做，这里只登记证据。
- 限制：深度补全不是分割，类比要打折扣。

nnInteractive 训练时"错误块按大小成比例抽"（见 B2），大块、远端的错天然得到更多训练。K 的远端块只放进约 0.13% 的训练单元（K1 103/80000，K2 114/80000，训练日志），训练分布和部署分布对不上：部署时 65% 的漏标体积在 30 mm 外。按"训练单元里 T 体素到笔的距离分布，对齐 TRAIN 回放实测的部署分布"来放远端块，是通用规则，不看 VAL；可学半径也只有这样才拿得到梯度。

### B6 PET/CT 交互病灶分割

autoPET IV 任务 1（MICCAI 2025）：协议和指标见 A8。官方数据页写的是训练 1,014 例 FDG（900 位患者）、597 例 PSMA（378 位患者），最终测试 200 例，四个"中心加示踪剂"组合各 50 例。前几名的成绩在官方总结论文里，本轮打不开。检索摘要里有"第一名 DSC 0.74、FNV 2.17 ml、FPV 1.30 ml，加点击稳定减少漏报、对小或低对比病灶略增误报"的说法，全部未核实。

《Towards Interactive Lesion Segmentation in Whole-Body PET/CT with Promptable Models》，Rokuss 等，arXiv 2025。领域三已写。补：在 autoPET III 冠军的 nnU-Net 残差编码器版上加点击输入通道，欧氏距离变换编码比高斯核好；训练时 80% 用官方模拟的点击，20% 用自己的模拟，让点击可以落在目标内任意处、偏向核心。

《autoPET IV challenge: Incorporating organ supervision and human guidance for lesion segmentation in PET/CT》（BIRTH），Huang 等，arXiv 2025。核查：本轮读了摘要和作者 PDF 的方法摘录。作者写明，只用 10 个点击的密集引导训练的模型，在 0 个或少量点击时很差，不利于按曲线面积排名；改为每个训练样本按事先设的概率随机取前 k 个点击（k 从 0 到 10）。项目术语表记它为 autoPET 2025 交互赛道第一名，本轮未核实名次。

autoPET V（2026）换成涂鸦，排名一半看 AUC-Dice，一半看 AUC-DMM（检测匹配指标：预测病灶能否和真病灶一一对上），UAM 来自这一届（见领域三）。

纠正 nnU-Net 输出的 PET 工作，本轮没找到新的；已有的 2S-ICR（头颈 PET/CT）、BS 和 UAM（PSMA，autoPET V）、SW-FastEdit（全身 PET 滑窗）都在领域三。

对我们：BIRTH 的"只训密集引导、稀疏时就差"，和 K 的远端块、教师状态池是同一个教训：训练时的交互分布要盖住评测时的分布。

### B7 一次加很多辅助损失没涨分

《A Metric Learning Reality Check》，Musgrave、Belongie、Lim，ECCV 2020。核查：本轮读了摘要和问题清单。统一网络、嵌入维度、数据增强，并用交叉验证调参以后，2006 到 2019 年的度量学习方法表现接近一条平线，作者的话是"实际进步至多是微小的"；很多论文是在测试集上挑模型的。

《nnU-Net Revisited: A Call for Rigorous Validation in 3D Medical Image Segmentation》，Isensee 等，MICCAI 2024。核查：本轮读了摘要。许多新结构"更好"的说法，在补足基线、数据量和算力对齐之后站不住，配置好的 CNN U-Net 仍属最好的一类。

再加上 A1 的 Engstrom 2020、Revisiting Rainbow，A2 的 Xin 2022、Kurin 2022，这几篇查"是哪一项起作用"的办法各不相同：Engstrom 用 4 项全因子，Rainbow 用逐项去掉，Revisiting Rainbow 在小环境里多次重复，Andrychowicz 分主题组随机抽组合。共同点是先固定一个调好的强基线，每次只动可解释的一组。

对我们：K 一次加了六项，v1 本身已经不弱（0.7562，验证集），和上面几篇的处境一样。六项一起没涨，不能推出每项都没用，更可能是 B1 拖、别的帮，互相抵消：K2 减 v1，加笔增益 −0.0445，删笔 +0.0412（验证集）。2×2 析因就是用来拆这个的。

### 对我们下一版配方的启示

文献和本机数字合起来，按证据从强到弱：

- 先改 B1 的难负样本，三种改法都由 T/O/P 定义或通用规则推出，不看 VAL。O 体素只罚"T 相对 O 的比例"，P 体素照旧（Robinson、Chuang、软采样，加上 B4 的结构推测）；不只取 pT 最高的 |T| 个，改按 pT 加权抽并设上限（Wu 2017、Xuan 2020）；给加笔补一个对称的难正例项，或在 T、O、P 全体里按损失挑（OHEM、自举损失）。
- 所有新增项按同一规则把梯度量级标定到 target Dice 项。依据是 PCGrad 的"量级差"和 Xin、Kurin 的"量级调好的加权求和就够"；B6 当初只标定了一项。
- 边界排序先让区域项立住，再随训练进度逐步加权（Kervadec 2019）。
- 训练日志加三样监控：按符号的正负梯度累计比（EQL v2），概率差（ASL），固定探针集上的 T 平均 pT 和遗忘次数（D7）。
- B3 输入训练时随机丢弃（2S-ICR 表 5）。
- 远端块按 TRAIN 回放实测的距离分布放置（nnInteractive 的同一思路），让可学半径拿到梯度；不加测地距离编码（Marinov 2023、MIDeepSeg）。远端收益上限小，这条是顺手做。
- 执行门槛：D1 若显示排序没坏，在 TRAIN 回放上按符号学偏置（Guo 2017、Menon 2021），先不重训，看能收回多少。
- 概率图：见 B3 的甲乙丙，等导演定。

哪些是推测要说清：B4 里三类头把概率推给 P 的机制、"内外圈纠缠"的类比、一致性项往保守推，都是推测，分别由 D2 的概率去向表、内圈梯度方向和 T1 的结果来核。实验顺序上，不训练的 D1 到 D6、T3 先做；T1 两次（B1 难负样本的 2×2）随后；T2 看导演定；N1 等 T1 出来再训。

## 第三部分 建议的诊断和改法一览

成本按一张 3090 估：一次从零 40k 约 20 GPU 小时（项目记录）；推理类只给量级，"小时级"指一次 VAL 回放上下，本文没有实测。

| 编号 | 做什么 | 依据 | 回答什么 | 成本（GPU 小时） | 要导演定 |
|---|---|---|---|---|---|
| D1 | v1、K1、K2 第 1 轮整卷 pT，按符号、T/O/P、离笔 15/30/60 mm 分段做直方图；门槛 0.05 到 0.95 扫描；加笔 T 对可改正确区的 AUC | Guo 2017、Ding 等 2021 的局部温度、Menon 2021、领域五的 Dice 账 | 加笔保守是偏置还是排序坏了；远端 pT 是差一点过线还是接近 0 | 小时级 | 否 |
| D2 | 最终权重上取一批 TRAIN 单元：各项对 T 内圈、外圈、O、P 的 logit 梯度；按符号的正负梯度累计比；概率差；难负样本在 O 上把概率推给 O 还是 P；参数梯度两两余弦；前瞻矩阵 | EQL v2、ASL、PCGrad、TAG、Xuan 2020 | 哪一项在压加笔的 T，压的是内圈、整体还是 error 分数 | 不到 1 | 否 |
| D3 | 加笔用 v1、删笔用 K1 或 K2 的按符号换模型系统，跑五轮 VAL | TIDE 的按类修思路；第 1 轮拼接已有 +0.0067 到 +0.0178（验证集） | 两边各取所长的上限，不训练 | 小时级 | 否 |
| D4 | K1 自己轨迹上，B3 输入置零或换成同扫描别轮的真实改动图，看第 2 到 5 轮 | ROAR、Zhang 与 Nanda、Vig | 网络用没用 B3，是否因此少改 | 小时级 | 否 |
| D5 | v1、K1、K2 逐层 CKA 和正交普氏，加冻结特征上的线性探针 | Kornblith 2019、Ding 等 2021 的表示相似度检验 | 分歧在主干还是头 | 不到 1 | 否 |
| D6 | 错误类型逐类独立补齐，加 FNV 式统计 | TIDE、autoPET 指标 | 差距落在哪类错 | 0，只用 CPU | 否 |
| D7 | 下一次训练加固定探针集，每 1000 步记 T 平均 pT、过线比例、遗忘次数 | Swayamdipta 2020、Toneva 2019 | 保守从哪一步开始，跟哪一项同步 | 接近 0，随训练附带 | 随下一次训练 |
| T1 | 2×2 析因：K1 去掉 B1 难负样本，v1 加上 B1 难负样本，各从零 40k | Rainbow、Revisiting Rainbow、HyperSHAP、Covert 2021、NIST | B1 的主效应、它和其余部件的交互、两人沙普利值 | 40 | 是，开训 |
| T2 | 同配置换种子重训一次（K1 或 v1） | Bouthillier、Henderson、Colas、Picard | 一次重训的波动有多大，±0.01 能不能解读 | 20 | 是，三种子不强制 |
| T3 | 推理端全因子：TRAIN 上学出的按符号偏置、按符号换模型、翻转、B3 置换，只在第 1 轮单步上跑 | Hutter 2014 的思路、Menon 2021 | 不训练能收回多少 | 小时级到十几 | 否 |
| N1 | 下一版配方：加笔难负样本只取 P 或 O 只罚相对比例、按 pT 加权抽并设上限、补难正例、新增项统一标定量级、边界排序逐步加权、B3 输入随机丢弃、远端块按部署距离分布放 | B4 各篇、2S-ICR、nnInteractive、PCGrad | 下一次 40k 训什么 | 20 | 是，等 T1 |
| N2 | 概率图输入加随机丢弃（B3 的选项乙） | MFP、2S-ICR、nnInteractive | 第 1 轮加笔能不能明显多修 | 20 | 是，改 09-19 的决定 |
| 不推荐 | 6 部件部分析因，8 次只到分辨度 III | NIST 手册 | 主效应和二阶交互分不开 | 160 | 不做 |

本轮没能核实的引用：autoPET IV 官方总结论文（SSRN 返回 403），以及其中的前几名成绩和"点击减漏报、增误报"的说法；BIRTH 的赛道名次；CDNet 的消融数字；Fawcett 与 Hoos 只读到项目页和书目信息，期刊正文没打开；DiffClick 的数字来自作者存档 PDF 的引言摘录。

## 参考文献

A1 消融设计与种子方差

- Hessel M, Modayil J, van Hasselt H, et al. Rainbow: Combining Improvements in Deep Reinforcement Learning. AAAI 2018. https://arxiv.org/abs/1710.02298
- Obando-Ceron JS, Castro PS. Revisiting Rainbow: Promoting more Insightful and Inclusive Deep Reinforcement Learning Research. ICML 2021. https://arxiv.org/abs/2011.14826
- Andrychowicz M, Raichuk A, Stańczyk P, et al. What Matters for On-Policy Deep Actor-Critic Methods? A Large-Scale Study. ICLR 2021. https://openreview.net/forum?id=nIAxjsniDzg
- Engstrom L, Ilyas A, Santurkar S, et al. Implementation Matters in Deep RL: A Case Study on PPO and TRPO. ICLR 2020. https://openreview.net/forum?id=r1etN1rtPB
- Hutter F, Hoos H, Leyton-Brown K. An Efficient Approach for Assessing Hyperparameter Importance. ICML 2014. https://proceedings.mlr.press/v32/hutter14.html
- Fawcett C, Hoos HH. Analysing differences between algorithm configurations through ablation. Journal of Heuristics 22(4):431–458, 2016. https://doi.org/10.1007/s10732-014-9275-9
- Covert I, Lundberg S, Lee SI. Explaining by Removing: A Unified Framework for Model Explanation. JMLR 22(209):1–90, 2021. https://jmlr.org/papers/v22/20-1316.html
- Wever M, Muschalik M, Fumagalli F, Lindauer M. HyperSHAP: Shapley Values and Interactions for Explaining Hyperparameter Optimization. AAAI 2026. https://arxiv.org/abs/2502.01276
- NIST/SEMATECH e-Handbook of Statistical Methods, 5.3.3.4.4 Fractional factorial design specifications and design resolution. https://www.itl.nist.gov/div898/handbook/pri/section3/pri3344.htm
- Bouthillier X, Delaunay P, Bronzi M, et al. Accounting for Variance in Machine Learning Benchmarks. MLSys 2021. https://proceedings.mlsys.org/paper_files/paper/2021/hash/0184b0cd3cfb185989f858a1d9f5c1eb-Abstract.html
- Henderson P, Islam R, Bachman P, et al. Deep Reinforcement Learning That Matters. AAAI 2018. https://ojs.aaai.org/index.php/AAAI/article/view/11694
- Colas C, Sigaud O, Oudeyer PY. How Many Random Seeds? Statistical Power Analysis in Deep Reinforcement Learning Experiments. arXiv 2018. https://arxiv.org/abs/1806.08295
- Picard D. Torch.manual_seed(3407) is all you need: On the influence of random seeds in deep learning architectures for computer vision. arXiv 2021. https://arxiv.org/abs/2109.08203

A2 损失项干扰

- Yu T, Kumar S, Gupta A, et al. Gradient Surgery for Multi-Task Learning. NeurIPS 2020. https://arxiv.org/abs/2001.06782
- Liu B, Liu X, Jin X, et al. Conflict-Averse Gradient Descent for Multi-task Learning. NeurIPS 2021. https://arxiv.org/abs/2110.14048
- Xin D, Ghorbani B, Garg A, Firat O, Gilmer J. Do Current Multi-Task Optimization Methods in Deep Learning Even Help? NeurIPS 2022. https://arxiv.org/abs/2209.11379
- Kurin V, De Palma A, Kostrikov I, Whiteson S, Kumar MP. In Defense of the Unitary Scalarization for Deep Multi-Task Learning. NeurIPS 2022. https://arxiv.org/abs/2201.04122
- Fifty C, Amid E, Zhao Z, et al. Efficiently Identifying Task Groupings for Multi-Task Learning. NeurIPS 2021. https://arxiv.org/abs/2109.04617
- Chen Z, Badrinarayanan V, Lee CY, Rabinovich A. GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks. ICML 2018. https://arxiv.org/abs/1711.02257
- Kendall A, Gal Y, Cipolla R. Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics. CVPR 2018. https://arxiv.org/abs/1705.07115
- Sener O, Koltun V. Multi-Task Learning as Multi-Objective Optimization. NeurIPS 2018. https://arxiv.org/abs/1810.04650

A3 表示比较

- Kornblith S, Norouzi M, Lee H, Hinton G. Similarity of Neural Network Representations Revisited. ICML 2019. https://arxiv.org/abs/1905.00414
- Raghu M, Gilmer J, Yosinski J, Sohl-Dickstein J. SVCCA: Singular Vector Canonical Correlation Analysis for Deep Learning Dynamics and Interpretability. NIPS 2017. https://arxiv.org/abs/1706.05806
- Ding F, Denain JS, Steinhardt J. Grounding Representation Similarity Through Statistical Testing. NeurIPS 2021. https://arxiv.org/abs/2108.01661

A4 训练动态

- Swayamdipta S, Schwartz R, Lourie N, et al. Dataset Cartography: Mapping and Diagnosing Datasets with Training Dynamics. EMNLP 2020. https://arxiv.org/abs/2009.10795
- Toneva M, Sordoni A, Tachet des Combes R, et al. An Empirical Study of Example Forgetting during Deep Neural Network Learning. ICLR 2019. https://arxiv.org/abs/1812.05159

A5 错误分解

- Bolya D, Foley S, Hays J, Hoffman J. TIDE: A General Toolbox for Identifying Object Detection Errors. ECCV 2020. https://arxiv.org/abs/2008.08115
- autoPET Challenge, Evaluation (Dice, false positive volume, false negative volume). https://autopet.grand-challenge.org/Evaluation/
- Maier-Hein L, Reinke A, Godau P, et al. Metrics reloaded: recommendations for image analysis validation. Nature Methods 21:195–212, 2024. https://www.nature.com/articles/s41592-023-02151-z ; https://arxiv.org/abs/2206.01653

A6 反事实输入与因果中介

- Hooker S, Erhan D, Kindermans PJ, Kim B. A Benchmark for Interpretability Methods in Deep Neural Networks. NeurIPS 2019. https://arxiv.org/abs/1806.10758
- Zhang F, Nanda N. Towards Best Practices of Activation Patching in Language Models: Metrics and Methods. ICLR 2024. https://arxiv.org/abs/2309.16042
- Vig J, Gehrmann S, Belinkov Y, et al. Investigating Gender Bias in Language Models Using Causal Mediation Analysis. NeurIPS 2020. https://arxiv.org/abs/2004.12265
- Zeiler MD, Fergus R. Visualizing and Understanding Convolutional Networks. ECCV 2014. https://arxiv.org/abs/1311.2901

A7 校准与门槛

- Guo C, Pleiss G, Sun Y, Weinberger KQ. On Calibration of Modern Neural Networks. ICML 2017. https://arxiv.org/abs/1706.04599
- Ding Z, Han X, Liu P, Niethammer M. Local Temperature Scaling for Probability Calibration. ICCV 2021. https://arxiv.org/abs/2008.05105
- Menon AK, Jayasumana S, Rawat AS, et al. Long-tail learning via logit adjustment. ICLR 2021. https://arxiv.org/abs/2007.07314

A8 交互分割评测

- Xu N, Price B, Cohen S, Yang J, Huang T. Deep Interactive Object Selection. CVPR 2016. https://arxiv.org/abs/1603.04042
- Benenson R, Popov S, Ferrari V. Large-scale interactive object segmentation with human annotators. CVPR 2019. https://arxiv.org/abs/1903.10830
- Marinov Z, Kim M, Kleesiek J, Stiefelhagen R. Rethinking Annotator Simulation: Realistic Evaluation of Whole-Body PET Lesion Interactive Segmentation Methods. arXiv 2024. https://arxiv.org/abs/2404.01816
- autoPET/CT IV Challenge, Task 1 Evaluation & Ranking; official repository. https://autopet-iv.grand-challenge.org/eval/ ; https://github.com/lab-midas/autoPETCTIV

B1 加删不对称

- Song S, Yu S, Zhou H, Huang X, Yu L, Xiao J. DiffClick: Click-differentiated enhancement network for interactive segmentation. Pattern Recognition 171:112217, 2026. https://doi.org/10.1016/j.patcog.2025.112217
- Salehi SSM, Erdogmus D, Gholipour A. Tversky loss function for image segmentation using 3D fully convolutional deep networks. MLMI 2017. https://arxiv.org/abs/1706.05721
- Hashemi SR, Salehi SSM, Erdogmus D, et al. Asymmetric Loss Functions and Deep Densely Connected Networks for Highly Imbalanced Medical Image Segmentation: Application to Multiple Sclerosis Lesion Detection. IEEE Access 7, 2019. https://arxiv.org/abs/1803.11078

B2 局部编辑与整卷重算

- Chen X, Zhao Z, Zhang Y, et al. FocalClick: Towards Practical Interactive Image Segmentation. CVPR 2022. https://arxiv.org/abs/2204.02574
- He Y, Guo P, Tang Y, et al. VISTA3D: A Unified Segmentation Foundation Model For 3D Medical Imaging. CVPR 2025. https://arxiv.org/abs/2406.05285
- Kirillov A, Mintun E, Ravi N, et al. Segment Anything. ICCV 2023. https://arxiv.org/abs/2304.02643
- Isensee F, Rokuss M, Krämer L, et al. nnInteractive: Redefining 3D Promptable Segmentation. arXiv 2025. https://arxiv.org/abs/2503.08373
- Liu Q, Xu Z, Bertasius G, Niethammer M. SimpleClick: Interactive Image Segmentation with Simple Vision Transformers. ICCV 2023. https://arxiv.org/abs/2210.11006
- Sofiiuk K, Petrov IA, Konushin A. Reviving Iterative Training with Mask Guidance for Interactive Segmentation. ICIP 2022. https://arxiv.org/abs/2102.06583

B3 概率图输入

- Lee C, Lee SH, Kim CS. MFP: Making Full Use of Probability Maps for Interactive Image Segmentation. CVPR 2024. https://arxiv.org/abs/2404.18448
- Saukkoriipi M, et al. Interactive 3D segmentation for primary gross tumor volume in oropharyngeal cancer. Scientific Reports 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12325674/

B4 难负例与保持类损失

- Shrivastava A, Gupta A, Girshick R. Training Region-based Object Detectors with Online Hard Example Mining. CVPR 2016. https://arxiv.org/abs/1604.03540
- Lin TY, Goyal P, Girshick R, He K, Dollár P. Focal Loss for Dense Object Detection. ICCV 2017. https://arxiv.org/abs/1708.02002
- Wu Z, Shen C, van den Hengel A. Bridging Category-level and Instance-level Semantic Image Segmentation. arXiv 2016. https://arxiv.org/abs/1605.06885
- Wu CY, Manmatha R, Smola AJ, Krähenbühl P. Sampling Matters in Deep Embedding Learning. ICCV 2017. https://arxiv.org/abs/1706.07567
- Xuan H, Stylianou A, Liu X, Pless R. Hard Negative Examples are Hard, but Useful. ECCV 2020. https://arxiv.org/abs/2007.12749
- Robinson J, Chuang CY, Sra S, Jegelka S. Contrastive Learning with Hard Negative Samples. ICLR 2021. https://arxiv.org/abs/2010.04592
- Chuang CY, Robinson J, Lin YC, Torralba A, Jegelka S. Debiased Contrastive Learning. NeurIPS 2020. https://arxiv.org/abs/2007.00224
- Tan J, Lu X, Zhang G, Yin C, Li Q. Equalization Loss v2: A New Gradient Balance Approach for Long-Tailed Object Detection. CVPR 2021. https://arxiv.org/abs/2012.08548
- Ridnik T, Ben-Baruch E, Zamir N, et al. Asymmetric Loss for Multi-Label Classification. ICCV 2021. https://arxiv.org/abs/2009.14119
- Wu Z, Bodla N, Singh B, Najibi M, Chellappa R, Davis LS. Soft Sampling for Robust Object Detection. BMVC 2019. https://arxiv.org/abs/1806.06986
- Kervadec H, Bouchtiba J, Desrosiers C, et al. Boundary loss for highly unbalanced segmentation. MIDL 2019. https://arxiv.org/abs/1812.07032
- Shahin AH, Zhuang Y, El-Zehiry N. From Sparse to Precise: A Practical Editing Approach for Intracardiac Echocardiography Segmentation. MICCAI 2023. https://arxiv.org/abs/2303.11041
- Chen X, He K. Exploring Simple Siamese Representation Learning. CVPR 2021. https://arxiv.org/abs/2011.10566

B5 远端传播

- Wang G, Zuluaga MA, Li W, et al. DeepIGeoS: A Deep Interactive Geodesic Framework for Medical Image Segmentation. IEEE TPAMI 2019. https://arxiv.org/abs/1707.00652
- Luo X, Wang G, Song T, et al. MIDeepSeg: Minimally Interactive Segmentation of Unseen Objects from Medical Images Using Deep Learning. Medical Image Analysis 72:102102, 2021. https://arxiv.org/abs/2104.12166
- Marinov Z, Stiefelhagen R, Kleesiek J. Guiding the Guidance: A Comparative Analysis of User Guidance Signals for Interactive Segmentation of Volumetric Images. MICCAI 2023. https://arxiv.org/abs/2303.06942
- Chen X, Zhao Z, Yu F, Zhang Y, Duan M. Conditional Diffusion for Interactive Segmentation. ICCV 2021. https://openaccess.thecvf.com/content/ICCV2021/html/Chen_Conditional_Diffusion_for_Interactive_Segmentation_ICCV_2021_paper.html
- Cheng X, Wang P, Yang R. Depth Estimation via Affinity Learned with Convolutional Spatial Propagation Network. ECCV 2018. https://arxiv.org/abs/1808.00150
- Park J, Joo K, Hu Z, Liu CK, Kweon IS. Non-Local Spatial Propagation Network for Depth Completion. ECCV 2020. https://arxiv.org/abs/2007.10042

B6 PET/CT 交互

- Rokuss M, Kirchhoff Y, Isensee F, Maier-Hein KH. Towards Interactive Lesion Segmentation in Whole-Body PET/CT with Promptable Models. arXiv 2025. https://arxiv.org/abs/2508.21680
- Huang J, Hao Y, Luo Y, et al. autoPET IV challenge: Incorporating organ supervision and human guidance for lesion segmentation in PET/CT. arXiv 2025. https://arxiv.org/abs/2509.02402
- autoPET V Challenge, Evaluation & Ranking. https://autopet-v.grand-challenge.org/evaluation/

B7 多辅助损失

- Musgrave K, Belongie S, Lim SN. A Metric Learning Reality Check. ECCV 2020. https://arxiv.org/abs/2003.08505
- Isensee F, Wald T, Ulrich C, et al. nnU-Net Revisited: A Call for Rigorous Validation in 3D Medical Image Segmentation. MICCAI 2024. https://arxiv.org/abs/2404.09556
