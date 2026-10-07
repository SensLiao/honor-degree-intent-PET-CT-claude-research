# 第二轮调研文献摘要

> 核对与复审更正（2026-10-03 夜，Claude Code 主会话补，正文未改）：
> 1. 总述“发现一”里“加笔看概率是否高过当前 Dice 的一半、删笔看是否低于一半”只对已知内容的编辑块精确成立；在 flat 自己的 200 个后几轮状态上，每笔的最优门槛和当时 Dice 的排序相关加笔 −0.05、删笔 0.02（VAL，`scripts/S_oracle_threshold_per_state.*`），所以计划第五稿改为打分头在候选范围加“不改”里学着挑，不直接用这条规则。
> 2. SegNext 的 65.34→85.71 是在共享图像编码之后加稠密空间融合，不是把笔作为最前层通道的直接证据（Codex 第 5 轮核原文）。
> 3. 核对 agent（`V1-citation-check.md`）：L2-03 RankSEG“掉 2.0 到 8.2 点”说的是 Focal 损失，软 Dice 三行是 +0.1、+0.2、无结果；L6-22 FFN 的流水线合并错误是 1.0% 到 5.4%，不是 1.7% 到 10.6%。
> 4. 去重篇数：本文按自己的口径数出 388 篇；核对 agent 按“路号小的一路保留”数出 385 篇（去掉边界项 380 篇）。计划采用 385。


2026-10-03，由 L1 到 L11 十一路调研记录和 H0 路项目历史合成。只读，没有新增事实。

## 总述

这一轮读了 11 个文献领域：交互分割最新进展、经典传播数学、决策理论与门槛、控制论、涂鸦和弱监督、视觉认知、意图推断、教育学和运动学习、大模型和图像编辑、因果与成对监督、通用医学模型与尺度；另有项目自己的历史一节，没有新文献。新读文献按各路末尾清单逐条累加，合计 403 篇；再用第一作者、年份、题目和 PDF 文件名对出同一篇，发现 14 篇被两三个领域各读了一次，多算的 15 次扣掉，去重后 388 篇（各路自己注明“不计新读”的不算，只读摘要的算）。PDF 文件夹现有 401 个文件，合计 2,069,657,667 字节（约 2.07 GB，du 显示 2.0G）。其中 47 个是第一轮留下的，354 个来自这一轮，对应 349 篇论文（5 篇被两路各存了一份）；另有 39 篇没存，原因是付费墙、来源不在允许名单、要人机验证或没有公开全文，只记了链接。最重要的三个跨领域发现是：执行点不该手定 0.5，决策理论、控制论等六处推出同一条规则，加笔看概率是否高过当前 Dice 的一半，删笔看是否低于一半，Dice 与概率由模型自己估。范围不该靠 60 mm 截断和固定步数，传播数学等七个领域都指向“从笔出发的最弱一环连通，算到不动点，再加每例学出的尺度”。指代要靠成对干预监督来学（同状态换一笔、目标跟着换；同目标换画法、结果不变），因果、教育、意图推断等六处各给了独立的理由，交互分割里本次检索未见有人这样训练。

痛点编号（数字均为 VAL）：P1 改过头（删笔连同真病灶一起删、加笔溢到背景，合计约 8 点）；P2 笔附近没修全（约 6 到 7 点）；P3 远端修不到（约 2 到 3 点）；P4 多轮（差距在第 1、2 轮成形）；P5 训练状态太干净；P6 换选笔习惯就掉分；P7 指代弱（同一状态换一笔，输出不跟着换）；P8 多训无效（原配方多训 8k 步，D5 只多 0.004）。T 是这一笔指的那处错，O 是别处同向的错，P 是本该不动的正确区；pT 是体素属于 T 的概率，D5 是第五轮 Dice。表里“对我们有什么用”一栏写的是对应哪个痛点、搬过来变成什么；写着“推测”“推断”的是调研记录自己的估计，不是文献结论。

## 分领域

### 1. 交互分割最新进展（L4 路，读 34 篇）

本次检索没找到一篇把“这一笔指的那处错有多大”当成带标签的输出去监督的交互分割文献：范围要么是规则（FocalClick 只取新旧预测之差里含新点击的最大连通块），要么是相似度的副产品，系数几乎全手定。最像通用规则的有两条：MFP 的“窗口半径不超过到最近异类点击距离的一半”，AdaptiveClick 的“难度指数由模型自己预测的前景质量与答案之比算出”，可借形式，不借常数。多候选加质量头最接近“网络自己评分选范围”，但挑选是瓶颈：SAM（Meta 的通用提示分割模型）按置信度选，单击 IoU（预测与答案的重叠比例）52.1，按 oracle（事后拿答案挑，只是上限）选 68.2。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Chen 2022 | FocalClick | 只把“新旧预测之差里含新点击的最大连通块”并回旧掩码；已有掩码上 NoC@90（点几下让 IoU 到 90%）从 6.23 降到 3.08 | P1：只能作用在 pT 编辑区；同规则用在误差图上，新错从 2.4 涨到 58.6 mL（VAL） |
| Lee 2024 | MFP | 窗口半径取“到最近异类点击距离的一半”，上限 100；DAVIS（自然图像交互分割基准）上 NoC@90 从 5.60 降到 5.32 | P1 P4：同向修改不越过到最近异向历史笔距离的一半，取代 60 mm 截断 |
| Yan 2023 | PiClick | 7 个候选，按“预测 IoU 乘置信度”挑，少 23% 到 54% 的额外人工挑选；下一轮状态随机取自己的候选，NoC@90 为 4.60，取最优候选为 5.01 | P1 P2 P5：候选加质量头；随机取自己的候选当下一轮状态 |
| Li 2024 | PRISM | 三维 CT 肿瘤；去掉修正学习后 100 点 Dice 从 90.26 掉到 81.20；训练只用 1 点则测试 1 到 100 点从 76.40 掉到 69.60 | P4 P5：训练轮数必须覆盖推理轮数 |
| Liu 2024 | SegNext | 去掉稠密融合，5 次点击平均 IoU 从 85.71 掉到 65.34；SAM 读涂鸦只有 30.42，SimpleClick 76.63 | P2 P3 P7：当前笔只经 128 维向量属较差的一类，应画成稠密通道进局部主干 |
| Ping 2026 | SCISSR | 累计笔作稠密提示、最新笔经零初始化门控注入；手术图平均 IoU 第 0、2、4 轮 79.42、90.03、91.60；点提示的 SAM3 第 2 到 4 轮从 62.52 掉到 40.38 | P2 P3 P4：计划里“稠密笔进主干、最新笔走门控”的现成对照；2D |
| Chen 2023 | ScribbleSeg | 上一轮掩码取“预测对扰动真值 1:0.4”最好（所需交互次数 7.98，纯预测 8.61，无上一轮 8.95） | P5 P7：训练状态混合有最优比例，纯自己的状态不是最好 |
| Marinov 2024 | Rethinking Annotator Simulation | 全身 FDG PET 上，真人点击 25% 落在标注之外；机器人用户与真人的 Dice 差 7.0 到 11.6，混入点击扰动后降到 3.6 和 3.7 | P6：训练与 VAL 评估里加入扰动笔位和落在标注外的笔 |

### 2. 经典传播数学（图割、随机游走、测地、最大最小连通、可学传播；L1 路，读 37 篇）

这类方法回答“从一笔种子出发，范围该停在哪”，答案只取决于每条边的权重和一条判定规则，固定步数和半径只在迭代求解时才出现。不靠固定步数有四条路：一次精确求解、解到不动点、学出停止、候选队列排空。本路在随机边权的三维格点上实算：迭代取最大最小要 86 到 249 步才到最终值，跑 32 步时仍有 44% 到 90% 的体素没到位，固定 K 步（K 是扩散的固定步数）等于偷偷设了半径。项目里“取笔碰到的连通块”规则会漏出（新错 2.39 涨到 58.65 mL，VAL），文献指向问题出在“绝对阈值加逐体素训练”，不在连通性本身；最看好的是“笔到体素的最大最小连通度加点对损失”，对 D5 的帮助是推断的 0 到 +2 点，检索中没见有人在三维医学交互纠错里测过。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Boykov 2001 | Interactive Graph Cuts | 笔当硬约束，求边界与区域代价之和最小的全局最优割；区域权重 λ 取 0 时目标缩成小块，取 60 时碎成孤立块 | P1：对三类打分做一次图割收拢零碎；种子少时偏小割，P3 不对口 |
| Couprie 2011 | Power Watershed | 图割、随机游走、最短路、分水岭是同一能量公式的不同取值；power watershed 只用边权排序，不必选 β | P1 P3：最接近“零手定系数”的经典求解器 |
| Cerrone 2019 | Learned Random Walker | 网络出边权，求解器不动、梯度隐式微分回传；电镜数据 VOI（分割差异指标，越低越好）：边界图单独训 0.177，端到端训 0.062 | P1 P2 P3：同一求解器训法不同差 3 倍，对应“取连通块”漏出；损失接在求解器之后 |
| Turaga 2009, Funke 2018 | Maximin Affinity, Constrained MALIS | 阈值化后两点连通，当且仅当两点间最强路径的最弱一环高于阈值，所以“该连的连、该断的断”可直接当损失；三个电镜数据集比此前最好相对改进 27%、15%、250% | P1 P2 P3 P7：点对取（笔体素，可改区域体素），标签是“属不属于笔指的错”，梯度只落在瓶颈边 |
| Wolf 2017 | Learned Watershed | 分水岭高度由网络现算，输入含“归我、归别人、无人”三态图；合成数据误差动态版 5.8，静态版 6.4 | P4 P5 P7：传播权重读上一轮的修改，状态变了范围跟着变 |
| Januszewski 2016 | Flood-Filling Networks | 递归 3D 网络从种子往外长，候选队列排空即停；电镜 5234 条骨架边准确率 98.5%，合并错误 0.0% | P1 P2 P3：以笔为种子循环生长；PET 病灶没人这样做过 |
| Bertrand 2023 | Fast Marching Energy CNN | 网络输出“通行难度”度量，掩膜取半径固定为 1 的单位球，尺度放进度量；脑 MRI Dice 0.863（对照 0.873） | P1 P2 P3：不设半径，让网络预测各处尺度；只验证过二维单病灶 |
| Wang 2019 | DeepIGeoS | 笔的测地距离图（沿图像内部走的最短距离）当输入，一轮纠错：胎盘 Dice 85.86 到 89.31，脑肿瘤 87.55 到 89.93 | P1 P2：“在自动结果上纠错”的先例，但起点已过 85（我们 0.61），增益不能外推 |

### 3. 决策理论与门槛（信号检测论、Dice 最优判据、校准、风险控制；L2 路，读 35 篇）

执行门槛 0.5 在 Dice 评测下没有依据：加笔时，这块里真病灶的比例高过当前 Dice 的一半才让 Dice 上升；删笔时，低于一半才上升。换成“这些体素真是错的概率”，加笔门槛是 D/2，删笔门槛是 1-D/2（D 是当前 Dice，D=0.75 时是 0.375 和 0.625），公式只用 Dice 本身（本路推导，计划附一已有同一结论）。前提是概率已校准（让打分和真实概率对得上），而 pT 没校准，用已有的单步扫描粗估偏移约 2.4 到 2.7 个 logit（概率之前的原始分数）单位，没校准就套规则会变差。所以分两层：规则层管门槛随 D 和方向变，校准层用对数损失拟合两个数；交互分割里没查到有人这样做，收益都是推测。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Elkan 2001, Landy 2024 | Cost-Sensitive Learning, Signal Detection Theory | 最优判据只由代价（收益）矩阵定；理想观察者在似然比超过“先验赔率乘收益比”时答“有” | P1：门槛 0.5 暗含“加错与漏加代价相等”，Dice 下不成立；Dice 的边际代价（对的收益 2-D，错的损失 D）就是收益矩阵 |
| Dai & Li 2023 | RankSEG | 固定门槛对 Dice 不一致，最优是“按概率排序取前 τ* 个”、逐图自适应；平均 Dice 高 3.13%、3.87%，但对软 Dice 训练的网络反掉 2.0 到 8.2 点 | P1：每例每轮自适应门槛，须先校准 |
| Nordström 2023 | Marginal Thresholding | 标签带噪声时，软 Dice 的最优解等于交叉熵的概率按“最优期望 Dice 的一半”切开 | P1：自估的 D̂/2 是它的增量版，门槛由模型自己的概率算出 |
| Berman 2018 | Lovász-Softmax | Nowozin 的规则套在交叉熵网络上，mIoU（平均 IoU）从 68.7 掉到 65.1；直接以 Jaccard（即 IoU）为目标的 Lovász 损失升到 72.5 | P1：既是“让网络自己学判据”的先例，也是“没校准别套规则”的警告 |
| Wolfe 2005, 2010 | Prevalence effect | 目标出现率 50%、10%、1% 时漏检 7%、16%、30%；98% 时虚警从 0.18 升到 0.58（2010 篇数字取自网页摘录，未逐字核对） | P1：训练里错误占四成、用时占千分之几，等于高出现率观察者，倾向虚警，表现为新错 |
| Mehrtash 2020 | Calibration in Medical Segmentation | Dice 损失训练的 U-Net（编码器解码器加跳连的分割网络）过度自信：脑肿瘤 ECE（置信度与实际正确率的平均差）13.20%，交叉熵 8.11% | P1：pT 受软 Dice 项影响会偏尖；校准放在集成之后 |
| Zheng & Ray 2026 | Conformal Risk Control, PET/CT | 共形（给门槛配统计保证）方法在 autoPET 900 例（FDG 示踪剂，非 PSMA）上：“漏掉整个病灶”无法认证，“漏掉的肿瘤体素比例”可认证，上界 0.093 | P1 P3：全局门槛救不回网络没支持的病灶；它把按连通块的共形族列为下一步 |
| Robinson 2018 | Segmentation Quality Prediction | 3D 网络看图像加分割掩膜，直接输出 Dice，平均绝对误差 0.03 | P1：自估 D 的现成做法；我们每个训练状态都有真实 Dice，标签免费 |

### 4. 控制论与迭代修正（L3 路，读 33 篇）

控制论把五轮纠错写成反馈回路：当前分割是被控对象，一笔是带噪测量，修回比例是增益，顺带带出的新错是乘性噪声。三个实用结论：一，“最小介入”（只纠正妨碍目标的偏差）和“邻近步”（离上一轮别太远）写成数学后，对二值掩膜就是逐体素门槛，加笔要求概率高于 (D̂+κ)/(2+κ)（D̂ 是自估的当前 Dice，κ 是一个假体素在后续轮里多占的代价），0.5、0.7、0.9 只是同一公式的几个取值；二，加删交替的回路稳定，当且仅当加笔溢出比与删笔误伤比的乘积小于 1（本路推导，假设溢出与修回成正比、加删严格交替），已有数据估出乘积约 0.03 到 0.13，麻烦在长尾，最重的 10% 轮次占新错体积的 73.2%（VAL）；三，固定步数 K 可以去掉，单调的最弱一环扩散迭代到无变化即停。MPC（往前规划多步、只执行第一步）在交互分割里没查到。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Todorov 2002 | Optimal feedback control | 最优控制器只纠正妨碍任务目标的偏差，对任务无关的方向任其变化，因为纠正信号本身有害 | P1 P7：T 是任务相关方向，O 和 P 该放着不动；保护项按“误改的下游代价”加权 |
| Parikh & Boyd 2014 | Proximal Algorithms | “最小化 f”加“离上一点别太远”，与信赖域（只在当前点附近一圈内相信局部近似）等价 | P1 P4：单轮编辑写成“满足指代加汉明距离惩罚”，解就是逐体素门槛 |
| Gorelick 2013 | Fast Trust Region | “实际下降/预测下降”高于 0.25 就放大半径，该阈值取 0 到 0.75 都稳健 | P1 P4：门槛越低半径越大；测试时用“医生下一笔落在刚加的区域里”当代理（推测） |
| Schulman 2015, 2017 | TRPO, PPO | 理论给的惩罚系数让步子太小、难稳健地选；PPO 按“实际改动是否超过目标 1.5 倍”把系数翻倍或减半 | P1 P4：λ 难选正是我们的问题；目标改动量可取自估的被指区域大小（推测） |
| Pace 2022 | Learned iterative segmentation | RNN（循环神经网络）从一次点击把分割逐步长出来，每步输出停止指示，用完整标注即时造“部分完成”的样本；60 例心脏磁共振 | P3 P5：监督式停止头，标签取 T-Dice（被指那处错上的 Dice）最大的那一步 |
| Liao 2020 | IteR-MRL | 每个体素是共享策略的 agent，奖励是相邻两步交叉熵之差；脑肿瘤 BraTS2015 从 77.15 到 88.53，对手第 2 步起几乎不涨 | P4 P5：与我们“第 2 轮 flat（现行主线的三分类输出头）只涨 0.0012”同形 |
| Wei 2024 | TIA | 点击后精度反降叫“精度波动”（类比超调）；NoDC（下降案例数）1685 降到 1478，mDIoU（平均降幅）0.79% 降到 0.26%（按表格行序读出，未逐格核对） | P1 P4：两个指标可当机制指标，用已存轨迹就能算 |
| Revach 2022 | KalmanNet | 保留“先验加增益乘新息”的结构，只把增益用 RNN 学出，状态方程失配时比卡尔曼滤波好约 3 dB | P1 P7：新掩膜等于当前掩膜加增益乘这一笔的指代证据；交互分割里没查到 |

### 5. 涂鸦和弱监督分割（L5 路，读 37 篇）

弱监督分割解决的是“标签缺”，靠伪标签（模型自己猜出来当训练标签的结果）去猜范围。我们训练时有稠密的三类标签，缺的是推理时远端的信息通路，所以能借的主要是传播算子和亲和度（相邻两点属于同一处的打分）的参数化，损失侧能借的很少：BoxInst 在全监督下把逐像素 Dice 换成它的两项，COCO（常用自然图像数据集）上打平。值得做的监督有三种：边级“开/闭”交叉熵、成对“同标签”一致性（要保留负边）、传播之后 pT 的 Dice。APro 的最大边传播能精确替代固定步数扩散，但一条错开的边会带出一大片，所以生长只能当训练信号。三维医学涂鸦上，精致方法并不稳。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Ahn 2018 | AffinityNet | 学相邻两点“是否同类”的亲和度，再靠随机游走传开；VOC（自然图像分割数据集）伪标签 mIoU 从 48.0 升到 58.1 | P2 P3：边级开/闭交叉熵；我们的边标签由符号误差连通块精确导出，比它干净 |
| Ahn 2019 | IRNet | 只预测一张类别边界图，亲和度取“连线上最强的一道边界”；伪标签 mIoU 66.5，对 59.3 | P1 P3：怎么参数化亲和度比怎么传更重要（约 7 点） |
| Tian 2021 | BoxInst | 框的投影项加相邻像素“同标签”成对项；全监督下换掉 Dice 打平（35.4 对 35.6 AP，平均精度）；颜色阈值取 0 时塌到 9.4 AP | P1：成对同标签项加在 pT 上，正负边都要，只有正边会塌成全前景 |
| Li 2023 | APro | 最小生成树上的瓶颈传播，并查集一次算完；一次全局传播 0.8 ms，逐点广度优先 4.3×10³ ms | P3 最直接：精确替代固定步数扩散；要改：不按全图总权重归一、三维非平面图、泄漏 |
| Huang 2018 | DSRG | 训练时用网络概率图从种子往外长，前景阈值取 0.80 到 0.99，mIoU 只在 57.2 到 57.7 变化 | P1：取连通块规则的弱监督版，区别是生长只当训练信号、推理不用 |
| Wang 2018 | BIFSeg | “拿初始分割再用笔纠错”的先例，测试时微调；胎盘 Dice 84.57 到 91.93，脑肿瘤核 82.66 到 87.49 | P2 P5：可借“离笔近且与笔相反的旧标签权重置 0”；测试时微调与冻结执行冲突 |
| Gotkowski 2025 | ScribbleBench | 七个三维数据集平均 Dice：CycleMix 0.559、DMSPS 0.697、partial loss（只在有标注的体素上算损失）0.813、全监督 0.856 | 通用性：不引入伪标签、一致性、对抗这类专用模块 |
| Wang 2024 | MaCo | 手定的距离衰减函数换成线性或高斯，前列腺 Dice 从 80.5 掉到 71.8 和 77.8 | P3：手定距离衰减是 60 mm 截断距离特征的同类，对形状敏感 |

### 6. 视觉认知与神经科学（L6 路，读 28 篇）

视觉皮层里“注意从提示点铺满整个物体、碰到边界停下”，靠三道互相独立的刹车：边界信号压低扩散，标签只出现在前馈证据已亮起的地方，大感受野在歧义处让位给小感受野。扩散速度随局部宽度变，不随固定半径变：猴子 V1（初级视觉皮层）里增强延迟的拟合，欧氏距离的相关系数 r 只有 0.13，沿局部宽度走的“生长锥”（用尽量大又不碰到干扰物的感受野往前推）模型有 0.51。连不连要分两类缺口：模型自己上一轮改出来的“状态缺口”用硬规则关死，影像上证据偏弱的“证据缺口”用学出的两侧支持函数。这与导演的 intent 概念同向：视觉里“指一处”指的是一个物体，注意会自动铺满整个物体。现成的深度循环模块代价高（γ-Net 在二维上训练就慢 12 到 18 倍），借结构，不借常数。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Grossberg & Mingolla 1985 | BCS/FCS form perception | 视觉分两路：边界系统算“边在哪”，特征系统让亮度向四周扩散；边界信号压低扩散常数形成屏障，有缺口就漏出 | P1 P7：把“壁”和“填”拆成两条通道，壁通道不读笔；预言的失败正是取连通块规则的失败 |
| Roelfsema & Houtkamp 2011 | Incremental grouping | 基础分组（一次认出）与增量分组（一格一格传开）；V1 的 96 个位点中 56 个负责传标签 | P1 P2 P3：标签通道与特征通道分开，标签受特征门控；这也是不让笔进主干（计划 2-2，稠密笔划证据）的理由 |
| Pooresmaeili & Roelfsema 2014 | Growth-cone model | 猴子 V1 增强延迟的拟合相关系数：欧氏距离 0.13，沿曲线恒速 0.2，生长锥 0.51 | P2 P3：传播跳数按局部宽度折算，窄处慢，必须由细尺度接手；每跳 49 ms 是生物常数，不搬 |
| Ekman 2020 | Automatic spreading in V1 | 线索点在一个物体上，血氧信号铺满整个物体；欧氏距离相同的两位置，沿物体更远的峰晚 0.43 s（7 人，探索性） | P3：检验远端漏修随欧氏距离还是随沿错误区的距离变化 |
| Mollard 2026 | Multiscale incremental grouping | 前馈单元只在感受野“无歧义”时才亮；5 个网络平均 23,200 次试验到 100%，没训练过的 30 像素曲线上也是 100% | P1 P2 P3 P6：内切半径辅助头（预测每个错误体素到最近正确体素的距离），学“无歧义”尺度；36×36 的玩具 |
| Hochstein & Ahissar 2002 | Reverse hierarchy | 知觉从层级顶端开始，先“一瞥”要点，需要细节再回低层；只练难例子通常没有进步 | P3：粗层要点图（全局分支上带深监督的粗分辨率读出，零初始化接回细层）；课程由易到难 |
| Ren 2008 | Contour completion statistics | 自然图像里近似直线的轮廓段长度服从幂律（指数 2.40，r² 0.9917），指数分布只有 0.9391；一条边的证据取两端证据之积 | P7 P2：缺口通行等于两侧支持相乘再乘学出的函数，不用 90 度、指数衰减这类常数 |
| Veerabadran 2023 | Adaptive recurrent vision | 没见过的 PathFinder-24（判断两点是否被同一条虚线连起来的测试）：学出停止 85.81%，固定步数 58.35%，“状态变化小于阈值就停”50.0% | P3：反对固定 K；非单调循环要学出的停止，单调传播不需要 |

### 7. 心理学和语言学里的意图推断（L7 路，读 31 篇）

心理学把“读懂别人的一个动作”写成逆规划（inverse planning，从看到的动作反推对方想要的目标）：目标的后验，正比于“这个目标下会这样做的概率”乘“这个目标本来就合理的先验”。照这个框架，一笔该被读成“理性的医生为某个目标状态选的动作”，要读出指哪处、加还是删、范围多大、到哪停、和上一轮的关系，并消掉一个干扰量：这位医生习惯怎么选笔。现在的输出头把这些压成一个直接预测，选笔习惯可能成了学进权重里的先验，这是 P6 的可能来源（推断，未实测）。范围可用语言习得的两条原则夹住：整体对象假设给下限，尺寸原则给上限。交互分割里本次未检索到有人这样做。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Baker 2009 | Action understanding as inverse planning | 看别人动作猜目标写成逆规划；允许目标中途改变的模型与人的判断相关 0.97（实时）、0.95（回溯），固定单一目标的只有 0.82 和 0.57 | P4 P6 P7：一笔读成对“当前候选错误”的后验；多轮里要区分沿用、重说、换目标 |
| Tomasello 2007 | A new look at infant pointing | 指点本身定不死指代对象，要靠共同背景（双方都知道对方知道的东西）；对方没懂时婴儿重复指 | P4 P7：共同背景就是当前分割加历史笔；重复指等于上一轮没改到位的信号 |
| Kranstedt 2006 | Measuring and Reconstructing Pointing | 32 个积木零件、1472 次示范；指点落成围绕目标的“云”，离指点者越远越散，失败从 60.25 到 77.75 cm 起快速增加 | P2 P3：容忍度随离笔距离成比例，不是固定截断；示范的外延是一个集合，不是单点 |
| Xu & Tenenbaum 2007 | Word learning as Bayesian inference | 尺寸原则：似然正比于 (1/假设大小)^n；成人一个例子时推广渐变，三个例子时收紧 | P1 P2 P3：范围写成“水平集链”（按阈值由高到低排成一串嵌套的候选范围）上的后验，门槛变成后验分位，步数跑到收敛 |
| Xu & Tenenbaum 2007 | Sensitivity to sampling | 同样三个相似例子，老师挑则收窄（儿童 71% 推到下位层），学习者自己挑则相反（儿童 29%） | P6：推广宽窄取决于被假定的抽样过程；选笔习惯改变的是“选哪一处”，要和“笔落在目标内”分开 |
| Rabinowitz 2018 | Machine Theory of Mind | 按一种智能体训练、换另一种测试，预测误差变大；混合几种训练则隐式学会层级推断 | P6：总体训练（混合选笔类型）是前提 |
| Ziebart 2008 | Maximum Entropy IRL | 局部归一化的动作模型有标签偏置；路线匹配全局归一化 78.79%，局部归一化 77.30%；Gandhi 与 Lake 2019 另证普通网络不会自发出现“一物一名”的互斥偏置 | P7：现有头逐体素三选一，没有“一笔只指一处”的约束；改为在候选错误对象之间做归一化 |
| Fradlin 2024 | Interactive4D | 用对手 AGILE3D 的选点策略测它，10 次点击后 IoU 为 87.0%，反过来测对手从 86.6% 降到 81.2% | P6：“选哪处”与“点哪里”解耦、训练时混合选点策略的先例；激光雷达，非医学 |

### 8. 教育学、学习科学和运动学习（L8 路，读 44 篇）

教育学和运动学习没有给出新的网络结构，给出三条“别手定，让学习者当前的表现来定”的规则。训练配额（现在是 40/30/30、近远 75/25）可换成：每组按“自然频率乘 exp(β×缺口)”抽，缺口等于 1 减实际增益除以理想增益，理想修复现算；医学分割里已有先例，Fidon 在 nnU-Net 上只换采样器。成对比较在教育学里起作用要三个条件：两例只差一个关键因素、被迫一起比、比完要讲；项目手定系数的清点（H1 路）量到 v1 的成对项梯度只有主损失的 1/500 到 1/800。反馈帮倒忙时，运动学习的解释是增益不跟着误差的一致性走：上一轮改过头（残差符号反转）就收，没改够就放。这些多是类比，直接证据都不在交互分割里。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Sagawa 2020 | Group DRO | 对预先分好的组最小化最坏组损失，组权重按当前损失指数上调；最差组准确率：普通训练 63.7/47.8/66.4，固定上调权重 88.0/83.3/64.8，Group DRO 91.4/88.9/77.7 | P5 P2：自适应权重优于固定权重，固定权重就是我们现在的手定配额；以最差组为目标会拉低平均，要加锚 |
| Fidon 2021, 2022 | Hardness weighted sampling | 按每个病例上次的损失做 softmax（把分数变成概率）抽样，nnU-Net 上只换采样器；脑肿瘤增强区 Dice +1.0 到 +1.5，胎儿脑 MRI 小脑最差 10% 病例的 Dice +26.5 点 | P5 P8：医学分割里“按当前难度自动抽”的先例，交互分割里未检索到；要细到块与错误类型 |
| Corrado 2026 | DRATS | 缺口等于（参考-实际）/（参考-随机），抽样概率正比于自然频率乘 exp(β×缺口)；五种采样规则里最差任务表现最好，“学会就换”的硬切换会崩 | P5：参考换成“理想修复”、随机换成“不改”；我们的加笔 ≥10 mL 约占总缺口 23.5%，训练里只抽 7.8%（VAL，只作方向演示） |
| Xie 2023 | DoReMi | 优化“相对参考模型的超额损失”，扣掉不可约部分以免追噪声；用 2.6 分之一的步数达到基线准确率 | P5：信号要对着“还能降多少”；不必另训参考模型，理想修复就是参考 |
| Gentner 2003 | Analogical encoding | 并排比较两个例子并抽出共同结构，迁移比两例分开学好：48% 对 19%（共 128 人）；学习者不会自发去比 | P7：损失要直接作用在两个输出之差上，让模型被迫比较 |
| Schwartz & Bransford 1998 | A time for telling | 先分析对比案例再听讲，预测新实验 43.8%；分析两遍无讲座 16.7%，总结文本加讲座 14.6% | P7：成对项必须和主监督放在同一批样本里一起训（比较加讲） |
| Herzfeld 2014 | A memory of errors | 误差灵敏度由过去误差的历史控制：误差同号持续则升高，快速切换则降低（每组 9 人，力场伸手） | P1 P4：上一轮改了之后残差符号反转就收、不变就放，增益由网络从改动足迹算出；D1 不应变 |
| Wei & Körding 2009 | Relevance of error | 只对“与自己动作有关”的误差强适应；相关性模型解释 90.8% 的方差，线性模型 68.7%（7 人） | P1 P4：大改动按“与模型自身上一轮动作相关的概率”压低，归因决定该撤销上一轮还是在原错上补 |

### 9. 大模型和图像编辑里的“只改该改的地方”（L9 路，读 39 篇）

知识编辑（不重训模型，只改它对某条事实的回答）有三条要求：可靠性、泛化、局部性，对应我们的“笔下改对、整块修全、不越界”。我们的执行器加三分类头已是 SERAC 那种分工（先判范围，再只改范围内），所以不建议搬 ROME、MEMIT 这类直接改权重的方法；能搬的是编辑块级的验证与筛选、保留样本配对、显式的范围尺寸头，以及“新错与修回配对报”的评价。大模型自我纠错的文献说明，剩下的错少时最容易把对的改错，我们后几轮正处于这个区间。图像编辑给的反面证据是：往损失里加局部性惩罚系数没有好点。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Yao 2023 | Editing LLMs survey | 编辑写成“范围内改成目标、范围外保持原输出”，评可靠性、泛化、局部性三项；SERAC 99.78/99.41/98.89，但可移植性不到 20%；连续编辑时改参数的方法退化 | P1 P4 P7：三条做 VAL 机制指标；局部性要同“编辑前的输出”比，不同标准答案比，否则奖励越界 |
| Mitchell 2022 | SERAC | 不改基座模型，范围分类器判断输入是否落在某条编辑范围内，是则交给改写模型；分类器错误绝大多数落在难样例上 | P1 P7：“何时改”与“怎么改”拆开，与相乘头 N3（“有没有错”e 乘“是不是这笔指的”b）同构；范围判断要用难正例和难负例训 |
| Zheng 2023 | IKE | 把“复制、更新、保留”三类示例放进上下文；去掉保留示例，综合分从 89.6 掉到 28.0，改写分反升到 99.8，这就是过度编辑 | P1：每笔配一批数量与 T 相同、模型自己 pT 最高的 O 和 P 作保留样本，取近邻难例 |
| Avrahami 2022 | Blended Diffusion | 每个去噪步把前景与原图按蒙版混合，末步把蒙版外换回原图；对照“损失里加背景保持项”：系数 100 整图变，10000 前景改不动 | P1：局部性靠构造不靠惩罚，我们的执行器就是构造，力气放在范围判准上 |
| Huang 2023 | LLMs Cannot Self-Correct Reasoning Yet | 不用标准答案决定何时停时，自我纠错反而变差：GSM8K（小学数学题集）上 GPT-3.5 标准 75.9，不带答案 75.1 和 74.7 | P4：“防止改错才是关键”；笔是外部反馈，属于“能成”的一类 |
| Tyen 2024 | Find errors, correct given location | GPT-4 找推理错误的准确率只有 52.87，给出错误位置后修正很稳；定位准确率约 60% 到 70% 时回溯修正的净收益已转正 | P1 P4：笔就是给定的位置，剩下的错出在“改多大”；第 2 轮缺口里新错占 58% 与此同型 |
| Goto 2026 | Edit-level majority voting | 对一个模型采 8 个修改，只保留出现次数不低于 τ 的编辑；错误最少的数据集上 F0.5（精确率权重是召回率两倍的评分）比贪心解码高 14.0 | P1 P4：后几轮错少，执行应更严；票数门槛改取“经验精确率等于 D/2 的票数”，不在 VAL 上选 |
| Shahin 2023 | From Sparse to Precise | 超声心内导管分割的编辑框架：近处同标准答案比、远处同原分割比；连续 10 次编辑，交叉熵和 Dice 越改越差，编辑损失越改越好 | P1 P4：最近的交互分割先例；但范围由距离定义、不由指代对象定义，权重手定 |

### 10. 因果、不变性和成对监督（L10 路，读 49 篇）

成对干预监督（同一状态换一笔、同一目标换画法）有三条互相独立的理论依据：两种配对缺一不可（Shu 2020）；“同目标换画法”约束的是给定目标后输出与画法无关，不是对选笔策略的边缘无关（Veitch 2021）；每个干扰因素都要有“单独变”的机会，干预要随机、标签要精确（Brehmer 2022 等）。这些定理按连续变量证明，我们的“哪一处错”是离散的，只能当设计准则。我们有别的领域没有的便利：贴标函数是已知程序，任何一笔都能精确重贴标签。P6 的掉分（“第二大错误”选笔下 D5 降约 0.09 到 0.10，TEST，只作描述）还不能直接当成“模型有选笔习惯”的证据：该策略下最大的错没人修，理想参照也会掉分，要先在 VAL 上做四个不训练的检查。成对排序损失不要 hinge margin（要求两个分数至少差一个固定间隔），它对 AUC（排序区分能力）不一致。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Veitch 2021 | Counterfactual Invariance | 把“换掉无关因素，预测不该变”写成反事实不变性；标签造成特征（反因果）时可检验的条件是“给定标签后输出与该因素无关”；正则过强则预测器对所有输入给同一答案 | P6 P7：“由笔推 T”是反因果方向，同目标换画法应写成“给定 T”；不做对选笔策略的边缘无关 |
| Shu 2020 | Weakly Supervised Disentanglement with Guarantees | 解耦拆成一致性（其余因素重采样，该因素读数不变）和限制性（改该因素，其余读数不变）；只做一种配对不保证另一种 | P7 P6：同目标换画法和同画法换目标缺一不可；换笔那一对里画法类型、长度、粗细要保持不变 |
| Brehmer 2022 | Weakly Supervised Causal Representation Learning | 给定干预前后的成对样本，因果变量可识别；条件是干预完美且随机、所有单变量干预都出现、噪声共享；离散变量学不好 | P6 P7：同一状态、同一噪声只换笔，正好满足；我们的变量离散，只当设计准则 |
| Geirhos 2020 | Shortcut Learning | 捷径是同分布测试集上好、分布外失效的决策规则，加数据很少能消掉；归纳偏置由结构、数据、损失、优化四部分决定 | P6 P8：去捷径的四个旋钮；也解释了“同分布多训 8k 步没用，换分布才有用” |
| Niu 2021 | Counterfactual VQA | 推理时从总分里扣掉“只看问题也给得出”的先验部分，参考值用 KL（两个分布的差异度量）匹配学出；视觉问答数据集上 38.46 升到 51.27 | P6 P7：零训练探针 u(q)-c·u(q̄)，q̄ 是训练集平均查询；一刀切扣先验会伤协议分 |
| Liu 2021 | Just Train Twice | 先训一个模型，再把它分错的样本上采样重训，不需要组标签；人脸属性数据集上平均 95.6 降到 88.0，最差组 47.2 升到 81.1 | P6：代价一贯是“平均掉一点，最差组涨很多”；可把父模型在换策略时分错的样本加权 |
| Kirichenko 2023 | Last Layer Re-Training | 只在均衡留出集上重训最后一层，多个基准上持平或超过更复杂的方法 | P6：主干不读笔，伪依赖只可能出在读笔的头；冻结主干，只在策略均衡数据上重训读笔的头 |
| Gardner 2020 | Contrast Sets | 对测试样本做小而有意义的扰动得到对照集，用“整组全对”一致率评价；10 个数据集上最多比原测试集低 25 点 | P7：VAL 上对每个状态的每块错各画一笔再换画法，整组全对才算对，用留出策略建对照集 |

### 11. 通用医学模型和尺度（L11 路，读 36 篇）

带毫米单位的常数换了数据集就不对，只能来自三处：数据指纹的规则（nnU-Net 的做法）、模型对每一例的预测、训练后在 VAL 上标定；无量纲的比例（倍频比 2，即相邻尺度差一倍；放大步 1.5 倍）跨数据集通用，可以保留。最该先做的是把 60 mm 截断换成“每例长度 ℓ̂ 加倍频距离特征”（距离按 ℓ̂ 的 1/2、1、2、4 倍分档折算）：现在 60 mm 外，距离和笔划占据两个通道都恒为 0，对局部头和空间支路（排队中的扩张卷积支路）等于没有笔，远端只能靠那一个共用的 128 维向量，这是 P3 的结构原因之一；ℓ̂ 由小头预测，监督是被指错误的等效半径，预期对 D5 帮助不大（粗估 0.3 到 1.0 点，是本路估计）。提示的空间尺度本身就是一阶超参：UAM（带器官辅助分支的交互基线）的高斯 σ 由 5 变 10，PSMA 单折第 5 笔 Dice 从 0.788 掉到 0.753。三维医学交互基础模型的尺度几乎全手定，也没有一个报告“按离提示距离”的修回。

| 作者 年份 | 题目简称 | 说的是什么 | 对我们有什么用 |
|---|---|---|---|
| Lindeberg 1998 | Automatic scale selection | 不预先挑尺度，沿尺度轴找“尺度归一化导数”的局部极值，极值所在尺度就是该结构的特征尺度 | P3 P2：笔处算尺度归一化 LoG（找斑点的滤波器）的最大响应尺度，作输入通道和 ℓ̂ 的先验；大而不均匀的病灶会选到热点的小尺度 |
| Isensee 2021 | nnU-Net | 数据指纹经启发式规则变成管线参数：目标间距取各轴中位数，块大小按显存缩，块覆盖不足 12.5% 中位形状就启用级联；19 个挑战赛、49 个任务 | 通用性：把 3 mm、96³、支路层数这些尺度常数并入一个规划器，由学习池指纹算出；规则只管自动分割，对提示几何只字未提 |
| Luo 2016 | Effective Receptive Field | 输出单元受输入影响的分布近似高斯，有效感受野只占理论的一小部分，按 √n 增长而理论按 n 线性增长 | P3：空间支路“视野约 93 mm”是理论值，按它粗算一个标准差只有约 22.6 mm（本路推算，非测量） |
| Chi 2022 | KERPLE | 位置偏置取对数型 -r1·log(1+r2·距离)，每头 2 个可学参数；训练 512 词、测到 16384，困惑度 23.9 降到 21.4，对照的线性偏置法 ALiBi 为 22.5 | P3：binding 打分（判断这一笔指哪处错的那一路）加毫米距离的对数型偏置（加笔、删笔各一组，r1 零初始化），对远处不绝望；仅语言 |
| Isensee 2025 | nnInteractive | 原生间距、192³ 块，缩放增广 0.5 到 2；预测碰块边就把视野放大 1.5 倍、最多 4 倍；放大使肝细胞癌数据的 AUC（交互曲线下面积）从 91.92 升到 95.40 | 通用性：缩放增广、毫米参数化、放大规则，常数无量纲、不依赖本数据 |
| Marinov 2023 | Guiding the Guidance | 3D PET（autoPET 501 例）上比五种提示编码：σ=5 最好，更大明显掉；距离截断按“每幅图自己的分位数”而非固定毫米；10 次点击后 Dice 自适应热图 79.89，实心球 78.15 | P3：60 mm 截断改成每例分位数或去掉；半径用边缘感知的局部尺度；点击而非涂鸦 |
| Lin 2021 | DCT-Net | 每个点击一个高斯，半径由用户拖拽长度给出或由轻量网络预测；DAVIS 上纯点击 NoC@90 为 7.00，拖拽给半径 5.92（正文与表数字略有出入） | P3 P2：“预测每个提示的影响半径”的唯一直接先例；用户给的半径明显好于预测的 |
| Liu 2026 | LAD | 逐例回归每个轴的尺度，末层零初始化；UNETR（三维 Transformer 分割网络）的平均 Dice 从 65.93 升到 71.58；学到的各轴尺度比与真实间距比相关 0.904 到 0.958（n=1039） | 通用性：ℓ̂ 头与它同类，零初始化的标量回归，输出在 1 附近；基于图像 Transformer、非交互 |

### 12. 项目自己走过的路子（H0 路，没有新文献）

这一节来自对项目自己文件的通读。intent（意图）的定义换过五次：导师 07-15 的“这一笔想修什么”，07-16 的文字意图，07-31 的六类，08-14 起的“合法程序”，09-17 起 SIRB-Net 的“操作化纠错意图”，也就是这一笔碰到的那块带符号错误；各版标签都由标准答案、当前分割和模拟笔划按规则算出，没有一版来自真实医生。最稳的结论有两条：意图标签本身给执行器的额外信息很少，导师 07-15 提的检验“意图是否比同样的空间提示更有用”在旧线上没有通过；差距一直出在“修多大、修到哪停”和“进入自己造的状态以后”。删笔连带删掉同一块里的真病灶，二维旧线和 SIRB 是同一个现象：二维 12 条金标准局部修剪里 11 条删光了所选块在当前切片的投影，SIRB 删笔新错 95.7% 落在笔碰到的那块里。H0 排出最值得重启的三个旧想法：范围改成终止条件（学出“到哪停”）、同状态成对监督、多笔意图（上一轮改了哪里、当时认定指哪块）。

| 时间 | 路子 | 做了什么、结果（除注明外为 VAL） | 留下的教训（对应痛点） |
|---|---|---|---|
| 07-31 到 08-13 | 六类意图本体加意图分类器 | 小分类器预测六类，macro-F1（各类 F1 的平均）0.7616，去掉当前分割 0.5795，切断加删泄漏后 0.4166；执行器“笔加意图”ΔDice（修改后减修改前的 Dice）0.0344，只给笔 0.0353 | 加删由“笔落不落在当前分割里”直接读出，满分是构造出来的；意图标签没比只给笔好（P7 P8） |
| 08-14 到 08-29 | 二维“合法程序”执行器 | 不看程序 0.3067，类型化程序 0.3192，差 +0.0125 [-0.0029, +0.0272]；换族 -0.0466，换指针 -0.0055 | 族名被用上，指针没被用上；指代信息只做成一个嵌入，网络会靠笔的落点（P7） |
| 08 月 | 二维伤害门 | 执行前回归 ΔDice，判坏就弃权；harm-AUC（把会改坏的修改排到低分处的概率）0.760（训练集内检），负例 12/95 降到 1/95，但删除侧放弃 94.8%，非劣没过 | 伤害能排序，但 28 名校准患者下只能接受零伤害，几乎关掉删除；完美门上限仅 +0.0248（P1） |
| 08 月 | 二维缺口分解与五轮轨迹 | 第 1 轮缺口：改坏 28.0%、放弃 26.7%、幅度不足 45.3%；兑现率 45.3% 降到 16.2%，再是 18.9%、18.4%、19.9% | 掉点出在第一次进入自己造的状态的第 2 轮；训练状态一直是 teacher forcing（训练时用标准答案推进状态）（P2 P4 P5） |
| 08-26 到 09-17 | 三维全局-局部残差执行器（旧主线，09-17 取消） | 起点 0.6387，终态 0.7024 [0.6459, 0.7530]（TEST，只作描述）；删侧可写区是整块所选分量 | 挡不住块内真病灶被删；后查出 315 个加笔回合里 124 个（39%）前景笔在进网络前整段丢失，修后为 100%（TRAIN）（P1） |
| 09-17 到 10-01 | SIRB v1：相乘头对三分类头 | TEST D5 相乘头 0.7619、三分类头 0.7694，nAUC（六个状态的 Dice 曲线下面积）差 -0.0118 [-0.0270, +0.0020]，判“不能下结论”；VAL 第一笔相乘头就少 2.84 点 | 排除笔的代价是真的，笔本身是错误证据；10-03 定只走三分类头一条线 |
| 10 月 | SIRB 笔划路径体检 | 当前笔只经一个 128 维向量和 2 张稠密图；101 片段体积加权：15 mm 内修回三分类头 0.800、相乘头 0.558，60 mm 外 0.084 和 0.000 | 笔进来以后没有任何带空间范围的计算；远端要靠新信息，靠采样和损失救不回（P2 P3） |
| 10 月 | 执行规则与多训探针 | 门槛 0.5 提到 0.9，删笔单步 -0.0175 变成 +0.0044；“同向体素全执行”误改是多修的 1.9 到 19.4 倍；原配方多训 8k 步，三分类头 D5 +0.0041 [-0.0152, +0.0208] | 规则扩大范围就漏，门槛是手定系数；堆训练步数不是出路（P1 P3 P8） |

## 跨领域交叉印证

下面六个做法，各被三个以上互不相干的领域独立指向（括号里是领域）；最后一条是一处分歧。

- 执行点不手定 0.5、0.7、0.9，由 Dice 公式和模型自估的质量算。指向它的有：决策理论（加笔 D/2、删笔 1-D/2）、控制论（逐体素门槛）、交互分割（每笔取一串由小到大的嵌套候选范围，加“执行后 Dice 变化”打分头，大于 0 才改）、意图推断（门槛读成范围后验分布的分位数）、大模型编辑（预测每个编辑块执行后的净 Dice 变化）、项目旧路子（自估增益大于 0）。
- 范围用“从笔出发的最弱一环连通，算到不动点”加“每例学出的尺度”，替掉 60 mm 截断和固定步数 K。指向它的有：传播数学、控制论、涂鸦弱监督、视觉认知（生长锥跳数、内切半径头）、意图推断（范围后验）、大模型编辑（范围尺寸头）、通用尺度（每例长度加倍频距离特征）。
- 成对干预监督：同一状态换一笔、目标跟着换；同一目标换画法、结果不变。指向它的有：因果（三条理论依据）、教育学（差异匹配的成对比较）、意图推断（对象级归一化加成对项）、大模型编辑（等价集监督、保留样本配对）、传播数学（人造断桥反事实，本路推演）、项目旧路子（二维配对臂当年没开）；交互分割里本次检索未见有人这样训练。
- 训练配额和状态来源由模型当前的缺口或总体分布决定，不手定 40/30/30。指向它的有：教育学与运动学习（缺口驱动抽样）、因果（学出采样混合）、交互分割（随机取自己的候选状态、1:0.4 混合）、意图推断（混合选笔类型的总体训练）、通用尺度（抽样包络按离笔距离对数均匀）。
- 把上一轮自己改了哪里、当时认定指哪块，作为输入；残差符号反转就收、不变就放。指向它的有：控制论、教育学与运动学习、意图推断（意图记录）、传播数学（边权头读上一轮“归我、归别人、无人”三态图）、交互分割（累计笔与最新笔分路）、项目旧路子（后几轮约 29% 的笔落在自己上一轮造的新错上，启发式估计）。
- 动手训练前先做不训练的机制检验。各领域的“最快验证”几乎都从不训练主网络的探针或诊断开始：控制论的回路稳定度检查、视觉认知的神经科学式检验、因果的四个检查、大模型编辑的“新错与修回配对报”、教育学的“没动、动了没修对、动过头”三态诊断、意图推断的线性探针（看笔向量里有没有意图信息）、通用尺度的按离笔距离分桶看修回。
- 一处分歧：笔该不该进主干。交互分割的证据（SegNext、SCISSR 等）偏向把当前笔画成稠密图送进局部主干；视觉认知与涂鸦弱监督的设计让主干不读笔，笔只当传播的种子。要靠空间支路的对照实验分清（计划决策 5：笔进不进主干）。

## 附表：新读文献去重清单

共 388 篇，按领域分组（顺序同上），编号沿用各路原编号。同一篇被几路读到的，只列在靠前的领域，编号用“=”连起来，所以有的领域在本表里条数少于正文标的“读 N 篇”。第一作者、年份、题目取自各路记录里的写法，超过 48 个字符的题目截断；有的记录只写了简称（如 CycleMix、BPR），括号里是补的说明或出处。PDF 列是 Thesis/sirb-research-20261003/ 里的文件名，省略 .pdf，开头的“~”代替“第一作者小写-年份-”，“+”后是同一篇的另一份文件，“未存”表示没存。第一轮留下的 47 个 PDF 不在本表，文件名见 F-cognitive-analogies.md 第 6 节和 G-cross-domain-ai.md 第 17 节。

交互分割最新进展（L4，34 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L4-01|Li|2018|Interactive Image Segmentation with Latent…|~latent-diversity|
|L4-02|Liew|2019|MultiSeg: Semantically Meaningful…|~multiseg|
|L4-03|Li|2023|Semantic-SAM: Segment and Recognize Anything…|~semantic-sam|
|L4-04|Zhao|2024|GraCo: Granularity-Controllable Interactive…|~graco|
|L4-05|Yan|2023|PiClick: Picking the desired mask from…|~piclick|
|L4-06|Li|2024|PRISM: A Promptable and Robust Interactive…|~prism|
|L4-07|Zhu|2024|SPA: Efficient User-Preference Alignment…|~spa-preference-alignment|
|L4-08|Chen|2021|Conditional Diffusion for Interactive…|~cdnet|
|L4-09|Chen|2022|FocalClick: Towards Practical Interactive…|~focalclick|
|L4-10|Lin|2022|FocusCut: Diving into a Focus View in…|~focuscut|
|L4-11|Wei|2023|Focused and Collaborative Feedback Integration…|~fcfi|
|L4-12|Du|2023|Efficient Mask Correction for Click-Based…|~emc-click|
|L4-13|Lee|2024|MFP: Making Full Use of Probability Maps for…|~mfp|
|L4-14|Asad|2023|Adaptive Multi-scale Online Likelihood Network…|~monet-online-likelihood|
|L4-15|Chen|2025|FocalClick-XL: Towards Unified and…|~focalclick-xl|
|L4-16=L3-22|Sun|2024|CFR-ICL: Cascade-Forward Refinement with…|~cfr-icl|
|L4-17|Darko|2026|U-CFR: Uncertainty-Guided Cascade Forward…|~u-cfr|
|L4-18|Xu|2024|Structured Click Control in Transformer-based…|~structured-click-control|
|L4-19=L7-23=L10-11|Moskalenko|2024|TETRIS: Towards Exploring the Robustness of…|~tetris +moskalenko-2024-tetris-robustness-interactive-segmentation|
|L4-20|Marinov|2024|Rethinking Annotator Simulation: Realistic…|~annotator-simulation-pet|
|L4-21|Esmaeili|2025|A methodology for clinically driven…|~clinical-interactive-evaluation|
|L4-22|Gao|2025|SafeClick: Error-Tolerant Interactive…|~safeclick|
|L4-23|Liu|2022|PseudoClick: Interactive Image Segmentation…|~pseudoclick|
|L4-24|Lin|2023|AdaptiveClick: Clicks-aware Transformer with…|~adaptiveclick|
|L4-25|Hadlich|2023|Sliding Window FastEdit: A Framework for…|~sw-fastedit|
|L4-26|Liu|2023|SimpleClick: Interactive Image Segmentation…|~simpleclick|
|L4-27|Huang|2023|InterFormer: Real-time Interactive Image…|~interformer|
|L4-28|Liu|2024|Rethinking Interactive Image Segmentation with…|~segnext|
|L4-29=L5-19|Chen|2023|ScribbleSeg: Scribble-based Interactive Image…|~scribbleseg|
|L4-30|Ping|2026|SCISSR: Scribble-Conditioned Interactive…|~scissr-scribble-surgical|
|L4-31=L11-34|Marinov|2024|Deep Interactive Segmentation of Medical…|~medical-interactive-review +marinov-2024-deep-interactive-segmentation-review|
|L4-32|Mesbah|2025|QuantIF: Semi-automatic PET/CT segmentation…|未存|
|L4-33|Xing|2025|Med3D: Exploring the design space of nnUNet on…|未存|
|L4-34|Mazher|2025|Masked Autoencoder Pretraining and…|未存|

经典传播数学（L1，37 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L1-01|Boykov|2001|Interactive Graph Cuts for Optimal Boundary &…|~interactive-graph-cuts|
|L1-02|Grady|2006|Random Walks for Image Segmentation|未存|
|L1-03|Couprie|2011|Power Watershed: A Unifying Graph-Based…|~power-watershed|
|L1-04|Criminisi|2008|GeoS: Geodesic Image Segmentation|未存|
|L1-05a|Udupa|2002|Axiomatic path strength definition for fuzzy…|未存|
|L1-05b|Ciesielski|2013|Joint graph cut and relative fuzzy…|未存|
|L1-06|Sethian|1996|A fast marching level set method for…|未存|
|L1-07|Caselles|1997|Geodesic Active Contours|~geodesic-active-contours|
|L1-08|Perona|1990|Scale-Space and Edge Detection Using…|~anisotropic-diffusion|
|L1-09|Chen|2017|Trainable Nonlinear Reaction Diffusion: A…|~tnrd|
|L1-10|Liu|2017|Learning Affinity via Spatial Propagation…|~spn|
|L1-11|Bertasius|2017|Convolutional Random Walk Networks for…|~crwn|
|L1-12|Vernaza|2017|Learning random-walk label propagation for…|~random-walk-label-propagation|
|L1-13|Cerrone|2019|End-to-End Learned Random Walker for Seeded…|~learned-random-walker|
|L1-14=L5-11|Song|2019|Learnable Tree Filter for Structure-preserving…|~learnable-tree-filter|
|L1-15|Turaga|2009|Maximin affinity learning of image segmentation|~maximin-affinity-learning|
|L1-16|Funke|2018|Large Scale Image Segmentation with Structured…|~constrained-malis|
|L1-17|Wolf|2017|Learned Watershed: End-to-End Learning of…|~learned-watershed|
|L1-18|Wolf|2021|The Mutex Watershed and its Objective…|~mutex-watershed-objective|
|L1-19=L6-22|Januszewski|2016|Flood-Filling Networks|~flood-filling-networks|
|L1-20|Mensch|2018|Differentiable Dynamic Programming for…|~differentiable-dynamic-programming|
|L1-21|Vlastelica|2020|Differentiation of Blackbox Combinatorial…|~blackbox-combinatorial-solvers|
|L1-22a=L3-14|Bai|2019|Deep Equilibrium Models|~deep-equilibrium-models|
|L1-22b|Winston|2020|Monotone operator equilibrium networks|~monotone-operator-equilibrium|
|L1-23a|Veličković|2020|Neural Execution of Graph Algorithms|~neural-execution-graph-algorithms|
|L1-23b|Zhu|2021|Neural Bellman-Ford Networks|~neural-bellman-ford-networks|
|L1-24a|Cheng|2020|CSPN++|~cspn-plus-plus|
|L1-24b=L3-16|Banino|2021|PonderNet: Learning to Ponder|~pondernet|
|L1-25a|Bertrand|2023|Fast Marching Energy CNN|~fast-marching-energy-cnn|
|L1-25b|Makaroff|2025|Learning Anisotropic Metrics for Geodesic…|~learning-anisotropic-metrics-heat-equation|
|L1-25c|Lichtenstein|2019|Deep Eikonal Solvers|~deep-eikonal-solvers|
|L1-26|Wang|2019|DeepIGeoS: A Deep Interactive Geodesic…|~deepigeos|
|L1-27|Luo|2021|MIDeepSeg: Minimally Interactive Segmentation…|~mideepseg|
|L1-28=L3-21|Ma|2021|Boundary-aware Supervoxel-level Iteratively…|~bs-iris|
|L1-29a|Yonetani|2021|Path Planning using Neural A* Search|~neural-astar|
|L1-29b|Song|2026|SILSM: A Sustainable Interactive Level Set…|~silsm-sustainable-interactive-level-set|
|L1-29c|Sambaturu|2021|Efficient and Generic Interactive Segmentation…|~interactive-conditional-inference-correct-mispredictions|

决策理论与门槛（L2，35 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L2-01|Elkan|2001|The Foundations of Cost-Sensitive Learning|~cost-sensitive-learning|
|L2-02|Nowozin|2014|Optimal Decisions from Probabilistic Models…|~iou-optimal-decisions|
|L2-03|Dai|2023|RankSEG: A Consistent Ranking-based Framework…|dai-2022-rankseg|
|L2-04|Nordström|2023|Marginal Thresholding in Noisy Image…|~marginal-thresholding|
|L2-05|Nordström|2022|On Image Segmentation With Noisy Labels…|~noisy-labels-dice-volume|
|L2-06|Bertels|2019|Optimizing the Dice Score and Jaccard Index…|~optimizing-dice-jaccard|
|L2-07|Berman|2018|The Lovász-Softmax Loss|~lovasz-softmax|
|L2-08|Salehi|2017|Tversky Loss Function for Image Segmentation…|~tversky-loss|
|L2-09|Landy|2024|Signal Detection Theory|未存|
|L2-10|Bogacz|2006|The Physics of Optimal Decision Making|~physics-optimal-decision-making|
|L2-11a|Wolfe|2005|Rare Items Often Missed in Visual Searches|~rare-items-often-missed|
|L2-11b|Wolfe|2010|Varying Target Prevalence Reveals Two…|未存|
|L2-12|Saerens|2002|Adjusting the Outputs of a Classifier to New A…|未存|
|L2-13|Alexandari|2020|Maximum Likelihood with Bias-Corrected…|~bias-corrected-calibration-label-shift|
|L2-14|Lipton|2018|Detecting and Correcting for Label Shift with…|~black-box-label-shift|
|L2-15|Tian|2020|Posterior Re-calibration for Imbalanced Datasets|~posterior-recalibration-imbalanced|
|L2-16|Guo|2017|On Calibration of Modern Neural Networks|~calibration-modern-networks|
|L2-17|Mehrtash|2020|Confidence Calibration and Predictive…|~calibration-medical-segmentation|
|L2-18|Mukhoti|2020|Calibrating Deep Neural Networks Using Focal…|~focal-loss-calibration|
|L2-19|Yeung|2021|Calibrating the Dice Loss to Handle Neural…|~calibrating-dice-loss|
|L2-20|Liao|2020|Real-time Scene Text Detection with…|~dbnet-differentiable-binarization|
|L2-21|Zhou|2021|Document-Level Relation Extraction with…|~atlop-adaptive-threshold|
|L2-22|Liu|2021|Supervised Adaptive Threshold Network for…|~supervised-adaptive-threshold-network|
|L2-23|Geifman|2017|Selective Classification for Deep Neural…|~selective-classification|
|L2-24|Bates|2021|Distribution-Free, Risk-Controlling Prediction…|~risk-controlling-prediction-sets|
|L2-25|Angelopoulos|2021|Learn then Test: Calibrating Predictive…|~learn-then-test|
|L2-26|Angelopoulos|2022|Conformal Risk Control|~conformal-risk-control|
|L2-27|Tan|2025|Conformal Lesion Segmentation for 3D Medical…|~conformal-lesion-segmentation|
|L2-28|Zheng|2026|What Can Conformal Risk Control Certify for…|未存|
|L2-29a|Mossina|2025|Controlling False Positives in Image…|~controlling-false-positives-conformal|
|L2-29b|Mossina|2024|Conformal Semantic Segmentation (CVPRW)|~conformal-semantic-segmentation|
|L2-29c|Mossina|2025|Morphological prediction sets (MICCAI)|~morphological-prediction-sets|
|L2-30|Robinson|2018|Real-time Prediction of Segmentation Quality|~segmentation-quality-prediction|
|L2-31|Huang|2019|Mask Scoring R-CNN|~mask-scoring-rcnn|
|L2-32|Li|2021|Interactive Medical Image Segmentation with…|~interactive-confidence-calibration|

控制论与迭代修正（L3，29 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L3-01|Todorov|2002|Optimal feedback control as a theory of motor…|~optimal-feedback-control|
|L3-02|Todorov|2003|A Minimal Intervention Principle for…|~minimal-intervention-nips|
|L3-03|Parikh|2014|Proximal Algorithms|~proximal-algorithms|
|L3-04|Gorelick|2013|Fast Trust Region for Segmentation|~fast-trust-region-segmentation|
|L3-05|Schulman|2015|Trust Region Policy Optimization|~trpo|
|L3-06|Schulman|2017|Proximal Policy Optimization Algorithms|~ppo|
|L3-07|Laroche|2019|Safe Policy Improvement with Baseline…|~spibb|
|L3-08|Gregor|2010|Learning Fast Approximations of Sparse Coding|~lista|
|L3-09|Chen|2018|Theoretical Linear Convergence of Unfolded…|~lista-linear-convergence|
|L3-10|Monga|2021|Algorithm Unrolling: Interpretable, Efficient…|~algorithm-unrolling|
|L3-11|Teed|2020|RAFT: Recurrent All-Pairs Field Transforms for…|~raft|
|L3-12|Carreira|2016|Human Pose Estimation with Iterative Error…|~iterative-error-feedback|
|L3-13|Ryu|2019|Plug-and-Play Methods Provably Converge with…|~pnp-convergence|
|L3-15|Graves|2016|Adaptive Computation Time for Recurrent Neural…|~adaptive-computation-time|
|L3-17|Zhang|2019|Dynamically Unfolding Recurrent Restorer: A…|~durr-moving-endpoint|
|L3-18a|Jolicoeur-Martineau|2025|Less is More: Recursive Reasoning with Tiny…|jolicoeur-martineau-2025-tiny-recursive-model|
|L3-18b|Wang|2025|Hierarchical Reasoning Model (HRM)|~hierarchical-reasoning-model|
|L3-19|Pace|2022|Learned iterative segmentation of highly…|~learned-iterative-segmentation|
|L3-20|Liao|2020|Iteratively-Refined Interactive 3D Medical…|~iter-mrl|
|L3-23|Wei|2024|Interactive Image Segmentation with Temporal…|未存|
|L3-24|Liu|2026|MedSAM-Agent: Empowering Interactive Medical…|~medsam-agent|
|L3-25=L10-48|Kendall|2018|Multi-Task Learning Using Uncertainty to Weigh…|~uncertainty-weighting +kendall-2018-uncertainty-weigh-losses|
|L3-26|Revach|2022|KalmanNet: Neural Network Aided Kalman…|~kalmannet|
|L3-27|Amos|2018|Differentiable MPC for End-to-end Planning and…|~differentiable-mpc|
|L3-28|Metz|2019|Understanding and correcting pathologies in…|~learned-optimizer-pathologies|
|L3-29|Liao-McPherson|2022|On Robustness in Optimization-Based…|liao-mcpherson-2022-robust-constrained-ilc|
|L3-30|Liu|2026|Self-Correction as Feedback Control: Error…|~self-correction-feedback-control|
|L3-31a|Wang-Lin|2026|If It's Not Buggy, Don't Fix It: On the…|wang-lin-2026-iterative-bug-fixing-dynamics|
|L3-31b|Wu|2026|CyberCorrect|~cybercorrect|

涂鸦和弱监督分割（L5，35 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L5-01|Tang|2018|On Regularized Losses for Weakly-supervised…|~regularized-losses|
|L5-02|Tang|2018|Normalized Cut Loss for Weakly-supervised CNN…|~normalized-cut-loss|
|L5-03|Obukhov|2019|Gated CRF Loss for Weakly Supervised Semantic…|~gated-crf-loss|
|L5-04|Liang|2022|Tree Energy Loss: Towards Sparsely Annotated…|~tree-energy-loss|
|L5-05|Tian|2021|BoxInst: High-Performance Instance…|~boxinst|
|L5-06|Li|2023|Label-efficient Segmentation via Affinity…|~apro-affinity-propagation|
|L5-07|Tian|2023|AttenScribble: Attentive Similarity Learning…|~attenscribble|
|L5-08|Ahn|2018|Learning Pixel-level Semantic Affinity with…|~affinitynet|
|L5-09|Ahn|2019|Weakly Supervised Learning of Instance…|~irnet|
|L5-10|Araslanov|2020|Single-Stage Semantic Segmentation from Image…|~pamr-single-stage|
|L5-12|Song|2020|Rethinking Learnable Tree Filter for Generic…|~rethinking-learnable-tree-filter|
|L5-13|Lin|2022|Dynamic Spatial Propagation Network for Depth…|~dyspn-dynamic-spatial-propagation|
|L5-14|Park|2020|Non-Local Spatial Propagation Network for…|~nlspn-non-local-spatial-propagation|
|L5-15|Huang|2018|Weakly-Supervised Semantic Segmentation…|~dsrg-seeded-region-growing|
|L5-16|Lin|2016|ScribbleSup: Scribble-Supervised Convolutional…|~scribblesup|
|L5-17|Wang|2018|Interactive Medical Image Segmentation using…|~bifseg-image-specific-fine-tuning|
|L5-18|Gotkowski|2025|Revisiting 3D Medical Scribble Supervision…|~scribblebench-revisiting-3d-scribble|
|L5-20|Lee|2020|Scribble2Label|~scribble2label|
|L5-21|Zhang|2022|CycleMix|~cyclemix|
|L5-22|Luo|2022|Scribble-Supervised Medical Image Segmentation…|~dual-branch-mixed-pseudo-labels|
|L5-23|Han|2024|DMSPS: Dynamically Mixed Soft Pseudo-label…|未存|
|L5-24|Valvano|2021|Learning to Segment from Scribbles using…|~multiscale-adversarial-attention-gates|
|L5-25|Cheng|2022|Pointly-Supervised Instance Segmentation|~pointly-supervised-instance-segmentation|
|L5-26a|Li|2024|ScribFormer|~scribformer|
|L5-26b|Li|2023|ScribbleVC|~scribblevc|
|L5-27|Wang|2025|ScribbleVS: Scribble-Supervised Medical Image…|wang-2024-scribblevs|
|L5-28|Wang|2024|From Few to More: Scribble-based Medical Image…|~maco-scribble|
|L5-29|Chen|2022|Scribble2D5|~scribble2d5|
|L5-30a|Han|2023|TDNet (triple-branch, 3D scribble)|~triple-branch-multi-dilated-scribble-3d|
|L5-30b|Qiu|2025|SparseMamba-PCL|~sparsemamba-pcl|
|L5-30c|Zhang|2025|MedCL (scribble)|~medcl-scribble|
|L5-30d|Yang|2022|PacingPseudo (scribble)|~pacingpseudo-scribble|
|L5-30e|Zhang|2025|Class-driven scribble promotion|~class-driven-scribble-promotion|
|L5-30f|Nguyen|2026|SDT-Net (scribble)|~sdt-net-scribble|
|L5-30g|Li|2024|SP3: superpixel-propagated pseudo-label|~sp3-superpixel-propagated-pseudo-label|

视觉认知与神经科学（L6，27 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L6-01|Grossberg|1985|Neural Dynamics of Form Perception: Boundary…|~bcs-fcs-form-perception|
|L6-02|Grossberg|1988|Neural dynamics of 1-D and 2-D brightness…|~brightness-filling-in|
|L6-03|Grossberg|2001|A neural model of how horizontal and…|~horizontal-connections-development|
|L6-04|Zhou|2000|Coding of Border Ownership in Monkey Visual…|~border-ownership|
|L6-05|Field|1993|Contour integration by the human visual…|未存|
|L6-06|Jolicoeur|1986|Curve tracing: A possible basic operation in…|未存|
|L6-07|Houtkamp|2003|A gradual spread of attention during mental…|未存|
|L6-08|Pooresmaeili|2014|A Growth-Cone Model for the Spread of…|未存|
|L6-09|Roelfsema|2011|Incremental grouping of image elements in vision|~incremental-grouping-theory|
|L6-10|Ekman|2020|Object selection by automatic spreading of…|~automatic-spreading-v1|
|L6-11|Mollard|2026|How the visual brain can learn to parse images…|~multiscale-incremental-grouping|
|L6-12|Brosch|2015|Reinforcement Learning of Linking and Tracing…|~rl-linking-tracing-contours|
|L6-13|Li|2008|Learning to link visual contours|未存|
|L6-14|Hochstein|2002|View from the Top: Hierarchies and Reverse…|~reverse-hierarchy|
|L6-15a|Kellman|1991|A theory of visual interpolation in object…|~visual-interpolation-relatability|
|L6-15b|Kellman|2005|Object interpolation in three dimensions|~object-interpolation-3d|
|L6-16|Ren|2008|Learning Probabilistic Models for Contour…|~contour-completion-statistics|
|L6-17|Linsley|2020|Stable and expressive recurrent vision models|~crbp-stable-expressive-recurrent|
|L6-18|Linsley|2020|Recurrent neural circuits for contour detection|~gamma-net-contour-detection|
|L6-19|Veerabadran|2023|Adaptive recurrent vision performs zero-shot…|~adaptive-recurrent-vision|
|L6-20|Figurnov|2017|Spatially Adaptive Computation Time for…|~sact|
|L6-21|Bai|2020|Multiscale Deep Equilibrium Models|~multiscale-deq|
|L6-23|Egly|1994|(记录未列题名；J Exp Psychol Gen 123:161)|未存|
|L6-24|Kahneman|1992|(记录未列题名；Cogn Psychol 24:175)|未存|
|L6-25|Richard|2008|(记录未列题名；J Exp Psychol HPP 34:842)|未存|
|L6-26|Lamme|2000|(记录未列题名；Trends Neurosci 23:571)|未存|
|L6-27|Schmid|2025|(记录未列英文题名；丘脑-皮层增量绑定)|~thalamocortical-incremental-binding|

心理学和语言学里的意图推断（L7，30 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L7-01|Baker|2009|Action understanding as inverse planning|~action-understanding-inverse-planning|
|L7-02|Baker|2017|Rational quantitative attribution of beliefs…|~rational-quantitative-attribution-mentalizing|
|L7-03|Gergely|2003|Teleological reasoning in infancy: the naive…|未存|
|L7-04|Csibra|2009|Natural pedagogy|未存|
|L7-05|Jara-Ettinger|2016|The naive utility calculus|jara-ettinger-2016-naive-utility-calculus|
|L7-06|Tomasello|2007|A new look at infant pointing|~new-look-infant-pointing|
|L7-07|Kranstedt|2006|Measuring and Reconstructing Pointing in…|~measuring-reconstructing-pointing|
|L7-09|Xu|2007|Word learning as Bayesian inference|~word-learning-bayesian-inference|
|L7-10|Xu|2007|Sensitivity to sampling in Bayesian word…|~sensitivity-to-sampling-bayesian-word-learning|
|L7-11|Hadfield-Menell|2016|Cooperative inverse reinforcement learning|hadfield-menell-2016-cooperative-irl|
|L7-12a|Dragan|2013|Legibility and predictability of robot motion|~legibility-predictability-robot-motion|
|L7-12b|Dragan|2013|Generating Legible Motion|~generating-legible-motion|
|L7-13|Hawkins|2020|Continual adaptation for efficient machine…|~continual-adaptation-machine-communication|
|L7-14|Hawkins|2021|From partners to populations|~partners-to-populations|
|L7-15|Ziebart|2008|Maximum entropy inverse reinforcement learning|~maximum-entropy-irl|
|L7-16|Rabinowitz|2018|Machine theory of mind|~machine-theory-of-mind|
|L7-17|Jeon|2020|Reward-rational (implicit) choice|~reward-rational-implicit-choice|
|L7-18|Fisac|2017|Pragmatic-pedagogic value alignment|~pragmatic-pedagogic-value-alignment|
|L7-19|Javdani|2015|Shared autonomy via hindsight optimization|~shared-autonomy-hindsight-optimization|
|L7-20|Zhi-Xuan|2020|Online Bayesian goal inference for…|zhi-xuan-2020-online-bayesian-goal-inference|
|L7-21|Bajcsy|2017|Learning robot objectives from physical human…|~learning-from-physical-human-interaction|
|L7-22=L10-37|Antonov|2024|RClicks: Realistic click simulation for…|~rclicks-realistic-click-simulation +antonov-2024-rclicks|
|L7-24|Yue|2023|AGILE3D: Attention guided interactive…|~agile3d-interactive-multi-object-3d|
|L7-25|Fradlin|2024|Interactive4D: Interactive 4D LiDAR segmentation|~interactive4d-lidar-segmentation|
|L7-26|Li|2023|Understanding embodied reference with…|~touch-line-transformer-embodied-reference|
|L7-27|Eyiokur|2025|CAPE: A CLIP-aware pointing ensemble of…|~cape-clip-aware-pointing-ensemble-heatmap-cues|
|L7-28|Yu|2025|UnSAMv2: Self-supervised learning enables…|~unsamv2-segment-anything-any-granularity|
|L7-29|Çelikok|2019|Interactive AI with a theory of mind|~interactive-ai-with-a-theory-of-mind|
|L7-30|Gandhi|2019|Mutual exclusivity as a challenge for deep…|~mutual-exclusivity-challenge-deep-networks|
|L7-31|Hawkins|2020|(据文件名) repeated reference games|~dynamics-repeated-reference-games|

教育学、学习科学和运动学习（L8，44 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L8-01|Kluger|1996|The effects of feedback interventions on…|未存|
|L8-02|Shute|2008|Focus on formative feedback|~formative-feedback|
|L8-03|Hattie|2007|The power of feedback|未存|
|L8-04|Wisniewski|2020|The power of feedback revisited|~power-of-feedback-revisited|
|L8-05|Lyster|1997|Corrective feedback and learner uptake|未存|
|L8-06|Schwartz|1998|A time for telling|~time-for-telling|
|L8-07|Gentner|2003|Learning and transfer: A general role for…|~analogical-encoding|
|L8-08|Alfieri|2013|Learning through case comparisons|未存|
|L8-09|Kapur|2008|Productive failure|未存|
|L8-10|Bjork|2011|Making things hard on yourself, but in a good…|~desirable-difficulties|
|L8-11|Wolpert|2011|Principles of sensorimotor learning|~sensorimotor-learning|
|L8-12|Shadmehr|2010|Error correction, sensory prediction, and…|~error-correction-adaptation|
|L8-13|Herzfeld|2014|A memory of errors in sensorimotor learning|~memory-of-errors|
|L8-14|Albert|2021|An implicit memory of errors limits human…|未存|
|L8-15|Wei|2009|Relevance of error|未存|
|L8-16|Berniker|2008|Estimating the sources of motor errors|未存|
|L8-17|Donchin|2003|Quantifying generalization from trial-by-trial…|未存|
|L8-18|Thoroughman|2000|Learning of action through adaptive…|未存|
|L8-19|Smith|2006|Interacting adaptive processes with different…|~two-timescale-motor-learning|
|L8-20|Wulf|2010|Frequent external-focus feedback enhances…|~external-focus-feedback|
|L8-21|Bengio|2009|Curriculum learning|~curriculum-learning|
|L8-22|Kumar|2010|Self-paced learning for latent variable models|~self-paced-learning|
|L8-23|Jiang|2014|Self-paced learning with diversity|~self-paced-learning-diversity|
|L8-24|Soviany|2022|Curriculum learning: A survey|~curriculum-learning-survey|
|L8-25|Zhu|2015|Machine teaching: An inverse problem to…|~machine-teaching|
|L8-26|Zhu|2018|An overview of machine teaching|~machine-teaching-overview|
|L8-27|Liu|2017|Iterative machine teaching|~iterative-machine-teaching|
|L8-28|Shrivastava|2016|Training region-based object detectors with…|~ohem|
|L8-29|Katharopoulos|2018|Not all samples are created equal|~importance-sampling|
|L8-30|Mindermann|2022|Prioritized training on points that are…|~rho-loss|
|L8-31=L10-08|Sagawa|2020|Distributionally robust neural networks for…|~group-dro|
|L8-32|Fidon|2022|Distributionally robust deep learning using…|~hardness-weighted-sampling|
|L8-33|Fidon|2021|Distributionally robust segmentation of…|~distributionally-robust-fetal-brain|
|L8-34=L10-32|Xie|2023|DoReMi: Optimizing data mixtures speeds up…|~doremi +xie-2023-doremi-data-mixtures|
|L8-35|Albalak|2023|Efficient online data mixing for LM pre-training|~online-data-mixing|
|L8-36|Graves|2017|Automated curriculum learning for neural…|~automated-curriculum-learning|
|L8-37|Matiisen|2017|Teacher-student curriculum learning|~teacher-student-curriculum|
|L8-38|Jiang|2021|Prioritized level replay|~prioritized-level-replay|
|L8-39=L10-33|Dennis|2020|Emergent complexity and zero-shot transfer via…|~paired-environment-design|
|L8-40|Corrado|2026|Distributionally robust multi-task RL via…|~drats-adaptive-task-sampling|
|L8-41|Wang|2025|DUMP: Automated distribution-level curriculum…|~dump-distribution-level-curriculum|
|L8-42|Chen|2025|Self-evolving curriculum for LLM reasoning|~self-evolving-curriculum|
|L8-43|Bae|2025|Online difficulty filtering for reasoning…|~online-difficulty-filtering|
|L8-44|Fischer|2025|Progressive growing of patch size|~progressive-patch-size-curriculum|

大模型和图像编辑（L9，39 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L9-01|Yao|2023|Editing Large Language Models: Problems…|~editing-llm-survey|
|L9-02|Meng|2022|Locating and Editing Factual Associations in GPT|~rome-locating-editing-factual|
|L9-03|Meng|2023|Mass-Editing Memory in a Transformer|~memit-mass-editing|
|L9-04|Mitchell|2022|Fast Model Editing at Scale|~mend-fast-model-editing|
|L9-05|Mitchell|2022|Memory-Based Model Editing at Scale|~serac-memory-based-editing|
|L9-06|De Cao|2021|Editing Factual Knowledge in Language Models|~knowledgeeditor|
|L9-07|Zheng|2023|Can We Edit Factual Knowledge by In-Context…|~ike-in-context-editing|
|L9-08|Fang|2025|AlphaEdit: Null-Space Constrained Knowledge…|~alphaedit-null-space|
|L9-09|Gupta|2024|Model Editing at Scale leads to Gradual and…|~model-editing-catastrophic-forgetting|
|L9-10|Cohen|2023|Evaluating the Ripple Effects of Knowledge…|~ripple-effects-editing|
|L9-11|Guo|2025|BalancEdit: Dynamically Balancing the…|~balancedit-generality-locality|
|L9-12|Li|2026|Multimodal Knowledge Edit-Scoped…|~edit-scoped-generalization-mllm-editing|
|L9-13|Zhu|2026|Evaluating and Understanding Model Editing for…|~m3bench-medical-vlm-model-editing|
|L9-14|Yang|2024|Learning Where to Edit Vision Transformers|~learning-where-to-edit-vit|
|L9-15|Malmi|2019|Encode, Tag, Realize: High-Precision Text…|~lasertagger|
|L9-16|Omelianchuk|2020|GECToR - Grammatical Error Correction: Tag…|~gector|
|L9-17|Stahlberg|2020|Seq2Edits: Sequence Transduction Using…|~seq2edits|
|L9-18|Mallinson|2022|EdiT5: Semi-Autoregressive Text Editing with…|~edit5|
|L9-19|Ng|2014|The CoNLL-2014 Shared Task on Grammatical…|~conll-shared-task-gec|
|L9-20|Dahlmeier|2012|Better Evaluation for Grammatical Error…|~better-evaluation-gec|
|L9-21|Qorib|2022|Frustratingly Easy System Combination for…|~esc-system-combination-gec|
|L9-22|Qorib|2023|System Combination via Quality Estimation for…|~greco-quality-estimation-gec|
|L9-23|Fang|2023|Is ChatGPT a Highly Fluent Grammatical Error…|~chatgpt-gec-overcorrection|
|L9-24|Goto|2026|Edit-level Majority Voting Mitigates…|~edit-level-majority-voting|
|L9-25|Huang|2023|Large Language Models Cannot Self-Correct…|~cannot-self-correct|
|L9-26|Kamoi|2024|When Can LLMs Actually Correct Their Own…|~self-correction-survey|
|L9-27|Tyen|2024|LLMs cannot find reasoning errors, but can…|~find-errors-correct-given-location|
|L9-28|Zhang|2024|Understanding the Dark Side of LLMs' Intrinsic…|~dark-side-self-correction|
|L9-29|Zhao|2023|Verify-and-Edit: A Knowledge-Enhanced…|~verify-and-edit|
|L9-30|Xia|2024|Agentless: Demystifying LLM-based Software…|~agentless|
|L9-31|Hertz|2022|Prompt-to-Prompt Image Editing with Cross…|~prompt-to-prompt|
|L9-32|Avrahami|2022|Blended Diffusion for Text-driven Editing of…|~blended-diffusion|
|L9-33|Shi|2024|DragDiffusion: Harnessing Diffusion Models for…|~dragdiffusion|
|L9-34|Xie|2023|SmartBrush: Text and Shape Guided Object…|~smartbrush|
|L9-35|Cai|2024|Making Large Multimodal Models Understand…|~vip-llava|
|L9-36|Yang|2023|Set-of-Mark Prompting Unleashes Extraordinary…|~set-of-mark|
|L9-37|Shahin|2023|From Sparse to Precise: A Practical Editing…|~sparse-to-precise-ice-editing|
|L9-38|Luo|2026|LeCor: Learning to Be Corrected by…|~lecor-meta-learned-test-time-correction|
|L9-39|Forte|2020|Getting to 99% Accuracy in Interactive…|~getting-to-99-accuracy-interactive|

因果、不变性和成对监督（L10，43 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L10-01|Veitch|2021|Counterfactual Invariance to Spurious…|~counterfactual-invariance|
|L10-02|Shu|2020|Weakly Supervised Disentanglement with…|~weakly-supervised-disentanglement-guarantees|
|L10-03|von Kügelgen|2021|Self-Supervised Learning with Data…|kugelgen-2021-content-style-augmentations|
|L10-04|Brehmer|2022|Weakly supervised causal representation learning|~weakly-supervised-causal-representation|
|L10-05|Mahajan|2021|Domain Generalization using Causal Matching|~matchdg-causal-matching|
|L10-06|Geirhos|2020|Shortcut Learning in Deep Neural Networks|~shortcut-learning|
|L10-07|Niu|2021|Counterfactual VQA: A Cause-Effect Look at…|~counterfactual-vqa|
|L10-09|Burges|2005|Learning to Rank using Gradient Descent|~ranknet-learning-to-rank|
|L10-10|Ouyang|2022|Causality-inspired Single-source Domain…|~causality-inspired-sdg-segmentation|
|L10-12|Miao|2024|Cross Prompting Consistency with Segment…|~cpc-sam-cross-prompting-consistency|
|L10-13|Locatello|2020|Weakly-Supervised Disentanglement Without…|~weakly-supervised-disentanglement|
|L10-14|Heinze-Deml|2021|Conditional Variance Penalties and Domain…|heinze-deml-2021-conditional-variance-penalties|
|L10-15|Arjovsky|2019|Invariant Risk Minimization|~invariant-risk-minimization|
|L10-16|Rosenfeld|2021|The Risks of Invariant Risk Minimization|~risks-of-irm|
|L10-17|Schölkopf|2021|Towards Causal Representation Learning|~causal-representation-learning|
|L10-18|Teney|2020|Learning What Makes a Difference from…|~counterfactual-gradient-supervision|
|L10-19|Gardner|2020|Evaluating Models' Local Decision Boundaries…|~contrast-sets|
|L10-20|Chen|2020|Counterfactual Samples Synthesizing for Robust…|~css-counterfactual-samples-vqa|
|L10-21|Zhang|2020|Causal Intervention for Weakly-Supervised…|~conta-causal-intervention-wsss|
|L10-22|Shah|2020|The Pitfalls of Simplicity Bias in Neural…|~simplicity-bias|
|L10-23|Nagarajan|2021|Understanding the Failure Modes of…|~failure-modes-ood|
|L10-24|Liu|2021|Just Train Twice|~just-train-twice|
|L10-25|Kirichenko|2023|Last Layer Re-Training is Sufficient for…|~last-layer-retraining|
|L10-26|Gao|2015|On the Consistency of AUC Pairwise Optimization|~auc-pairwise-consistency|
|L10-27|Khosla|2020|Supervised Contrastive Learning|~supervised-contrastive-learning|
|L10-28|Robinson|2021|Contrastive Learning with Hard Negative Samples|~hard-negative-contrastive|
|L10-29|Wang|2021|Understanding the Behaviour of Contrastive Loss|~contrastive-loss-behaviour|
|L10-30|Cao|2019|Learning Imbalanced Datasets with…|~ldam-margin-loss|
|L10-31|Sohn|2020|FixMatch|~fixmatch|
|L10-34|Zhang|2020|Generalizing Deep Learning for Medical Image…|未存|
|L10-35|Billot|2023|SynthSeg: Segmentation of brain MRI scans of…|~synthseg|
|L10-36|Gulrajani|2021|In Search of Lost Domain Generalization|~domainbed|
|L10-38|Wong|2024|ScribblePrompt: Fast and Flexible Interactive…|~scribbleprompt|
|L10-39|Ahuja|2023|Interventional Causal Representation Learning|~interventional-causal-representation|
|L10-40|Tang|2020|Unbiased Scene Graph Generation from Biased…|~unbiased-scene-graph-generation|
|L10-41|Pezeshki|2021|Gradient Starvation|~gradient-starvation|
|L10-42|Nam|2020|Learning from Failure|~learning-from-failure|
|L10-43|Mitrovic|2021|Representation Learning via Invariant Causal…|~relic-invariant-causal-mechanisms|
|L10-44|Yu|2024|Revisiting Counterfactual Problems in…|~counterfactual-problems-rec|
|L10-45|Rendle|2009|BPR|~bpr|
|L10-46|Soudry|2018|The Implicit Bias of Gradient Descent on…|~implicit-bias-separable-data|
|L10-47|Kim|2019|Deep Metric Learning Beyond Binary Supervision|~metric-learning-beyond-binary-supervision|
|L10-49|Chen|2018|GradNorm|~gradnorm|

通用医学模型和尺度（L11，35 篇）

|编号|第一作者|年份|题目|PDF|
|---|---|---|---|---|
|L11-01|Lindeberg|1998|Feature detection with automatic scale selection|~automatic-scale-selection|
|L11-02a|Isensee|2019|Automated Design of Deep Learning Methods for…|~nnunet-automated-design|
|L11-02b|Isensee|2018|nnU-Net 早期版（arXiv 1809.10486，题名记录未写全）|~nnunet-self-adapting|
|L11-03|Isensee|2024|nnU-Net Revisited: A Call for Rigorous…|~nnunet-revisited|
|L11-04|Worrall|2019|Deep Scale-spaces: Equivariance Over Scale|~deep-scale-spaces|
|L11-05|Sosnovik|2020|Scale-Equivariant Steerable Networks|~scale-equivariant-steerable|
|L11-06|Jansson|2022|Scale-invariant scale-channel networks: Deep…|~scale-channel-networks|
|L11-07|Pintea|2021|Resolution learning in deep convolutional…|~resolution-learning-scale-space|
|L11-08|Romero|2022|FlexConv: Continuous Kernel Convolutions with…|~flexconv|
|L11-09|Khalfaoui-Hassani|2023|Dilated convolution with learnable spacings|khalfaoui-hassani-2023-dcls|
|L11-10|Dai|2017|Deformable Convolutional Networks|~deformable-convnets|
|L11-11|Li|2019|Selective Kernel Networks|~selective-kernel-networks|
|L11-12|Gao|2022|RF-Next|~rf-next|
|L11-13|Luo|2016|Understanding the Effective Receptive Field in…|~effective-receptive-field|
|L11-14|Roy|2023|MedNeXt: Transformer-driven Scaling of…|~mednext|
|L11-15|Tancik|2020|Fourier Features Let Networks Learn High…|~fourier-features|
|L11-16|Press|2022|Train Short, Test Long: Attention with Linear…|~alibi|
|L11-17|Chi|2022|KERPLE: Kernelized Relative Positional…|~kerple|
|L11-18|Joutard|2024|HyperSpace: Hypernetworks for spacing-adaptive…|~hyperspace|
|L11-19|Liu|2026|LAD: Learnable Anisotropic Deformation for 3D…|未存|
|L11-20|Recasens|2018|Learning to Zoom: a Saliency-Based Sampling…|~learning-to-zoom|
|L11-21|Isensee|2025|nnInteractive: Redefining 3D Promptable…|~nninteractive|
|L11-22|He|2024|VISTA3D: A Unified Segmentation Foundation…|~vista3d|
|L11-23|Wang|2023|SAM-Med3D: Towards General-purpose…|~sam-med3d|
|L11-24|Du|2024|SegVol: Universal and Interactive Volumetric…|~segvol|
|L11-25|Ma|2025|MedSAM2: Segment Anything in 3D Medical Images…|~medsam2|
|L11-26|Liu|2023|CLIP-Driven Universal Model|~clip-driven-universal-model|
|L11-27|Marinov|2023|Guiding the Guidance: A Comparative Analysis…|~guiding-the-guidance|
|L11-28|Majumder|2019|Scale-aware multi-level guidance for…|~scale-aware-multi-level-guidance|
|L11-29|Lin|2021|Interactive Object Segmentation with Dynamic…|~dynamic-click-transform|
|L11-30|Zhou|2023|Interactive Segmentation as Gaussian Process…|~interactive-segmentation-gaussian-process|
|L11-31|Yang|2023|DRE-Net: A Dynamic Radius-Encoding Neural…|未存|
|L11-32|You|2026|Consispace（arXiv 2606.31839，题名记录未写全）|~voxel-spacing-consistency|
|L11-33|Brudfors|2022|(splat 层；arXiv 2206.06445；题名记录未写全)|~varying-resolutions-splatting|
|L11-35|Ndir|2025|(基于 nnInteractive 的方案；arXiv 2510.03189)|未存|
