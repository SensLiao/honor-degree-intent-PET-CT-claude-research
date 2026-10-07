# L3 路：控制论、优化和迭代修正的数学（第二轮跨领域调研）

2026-10-03 晚。读者是导演和主线 agent。只读了公开文献和本目录已有记录，没连服务器，没改代码、vault 和别的文件，没跑任何实验。数据集一律标明：VAL 是验证集，TEST 是锁定测试集，本文没有用任何 TEST 数。

标记：[read] 打开读过原文相关章节；[摘要] 只读到摘要或引言；【项目数】来自本目录 A、G 路或 PLAN；【推导】是本路自己的推导，前提写在旁边；【推测】没有实验支持，几项预计收益之间不能相加。GT＝标准答案。

## 0 先给结论

1. 最小介入和邻近步可以直接写成执行规则，也能写成训练目标。对二值掩膜，“满足指代＋λ·改动量”按体素可分，解就是对概率设门槛。设体素是真病灶的校准概率为 q，模型估计的当前 Dice 为 D̂：加笔要 q＞(D̂+κ)/(2+κ)，删笔要 q＜D̂/(2+κ_R)。κ 是一个假体素在后续轮里多占的代价，κ=0 就是单步 Dice 最优，和 PLAN 附一、G 路 §4 同一结论【推导】。所以现在试的 0.5、0.7、0.9 只是 λ 的几个取值，没有理由手定。门槛只截断排序，不增加区分度，管不了 P1 里“同一块分割里分不开真病灶和假阳性”那一半。
2. 超调。把加笔溢出比 hA、删笔误伤比 hR 写成线性回路，加删交替时稳定当且仅当 hA·hR＜1【推导】。用 A 路的中位数估出乘积约 0.03 到 0.13：常态是“稳定但低效”，不是处处在振荡；麻烦在长尾（最重的 10% 轮次占新错体积 73.2%）。所以增益要按状态调，不能整体压低。2D 分割里已有人把这件事叫 overshoot（超调：一步改过头）：TIA（点击分割，BMVC 2024）和 MedSAM-Agent（智能体，2026）。
3. 固定步数 K。单调的最弱一环扩散不需要 K，迭代到无变化为止（零容差）；学出来的非单调传播用监督式停止头，标签取“下一次迭代不再提高 T-Dice（被指的错那一块上的 Dice）”。不建议用 ACT（让网络自己决定迭代几步的老方法）的 ponder cost（思考成本），作者自己写“结果对 τ 很敏感，不知道怎么选”。
4. 五轮当整体优化。强化学习做过（IteR-MRL、BS-IRIS、MedSAM-Agent），多步序列损失做过（CFR-ICL、RAFT），MPC（模型预测控制：往前规划多步、只执行第一步）在交互分割里没查到。建议逐体素标签仍由 GT 教师给，只有标量控制（门槛偏移、停止）用滚动展开挑最优再蒸馏，不上完整强化学习。
5. 最有希望的改法在 §4.1：第一个只改执行器，不用训练；其余续训 8k，新增部分零初始化。

## 1 把五轮纠错写成反馈回路

| 控制论里的量 | 在 SIRB 里是什么 | 现有数据里怎么测 |
|---|---|---|
| 被控对象 | 当前分割 M(t) | D0 到 D5 六个状态的 Dice |
| 传感器 | 医生的一笔：对最大错误的一次带噪测量 | 笔落在哪、指哪块错 |
| 增益 g | 被指的错这一轮修回的比例 | flat 第 1 轮体积加权：15 mm 内 0.84，15–30 mm 0.47，30–60 mm 0.07（VAL，PLAN P2、P3） |
| 乘性噪声 h | 每修回一单位带出的新错 | ADD 0.5–10 mL 约 0.75（n=28，快速 VAL，G 路）；新错/目标体积中位数 ADD 0.49–0.73，REMOVE 0.07–0.18（VAL，A 路） |
| 超调 | 一轮之后 Dice 反而变差 | 变差 242 轮中 160 轮是 REMOVE、82 轮是 ADD，72.3% 新错多于修回（VAL 三画法，A 路） |
| 稳态误差 | 第五轮仍留的新错 | 患者平均 13.48 mL（VAL，A 路） |
| 状态估计 | 模型对“当前掩膜有多差”的估计 D̂ | 现在没有；Robinson 2018 在心脏 MR 上预测 Dice，MAE 0.03 [摘要] |
| efference copy（运动指令副本：控制器把自己发出的指令也当输入） | 上一轮自己的改动图 | 现在没有，PLAN 3-2 的“修补记录”就是它 |

单步账【推导】。设当前 Dice 为 D，B 是预测与标准答案体素数之和。加笔带进 a 个真体素、b 个假体素，ΔD＝[a(2−D)−D·b]/(B+a+b)。记溢出比 h＝b/a，则 ΔD＝a·[2−D(1+h)]/(B+a+b)，相对无溢出（h=0）的效率 η＝[2−D(1+h)]/(2−D)。D=0.75、h=0.75 时 η=0.55：同样修回量，只拿到无溢出时 55% 的收益。加笔不亏的条件是 hA＜(2−D)/D；删笔同理，误伤比 hR＜D/(2−D)。D=0.75 时前者上限 1.67，后者只有 0.6：删笔比加笔脆弱得多，和 A 路“后几轮 REMOVE 平均 −0.0204、ADD 平均 +0.0341”一致。

回路稳定条件【推导】。把一例的错误写成漏分体积 x 和多分体积 y。ADD 修回比例 a，同时产生体积为 hA·a·x 的新假阳性；REMOVE 去掉比例 r，同时误伤体积 hR·r·y 的真病灶。两轮 ADD、REMOVE 交替的更新矩阵特征值全在单位圆内，当且仅当 hA·hR＜1（Jury 判据，二阶离散系统稳定的代数条件；与 a、r 无关，a、r 只决定收敛快慢）。上面两个单步上限相乘正好是 1：每一步都守住单步不亏，回路增益就守住了 ＜1。假设是溢出与修回成正比、加删严格交替；真实协议每轮取最大的错，是交替的混合，所以这是稳定性的参照，不是预测。

和项目数对照。hA、hR 的中位数乘积只有 0.03–0.13，但新错多于修回的轮次占 10%–37%（按目标类型，A 路）。两类 h 在同一位置接连超标的比例没有数过；ADD→REMOVE→ADD 同位往返的次数是判断“是不是振荡”的直接指标，先数它（§4.1 的 E）。

## 2 四个问题

### 2.1 最小介入和邻近步，能不能写成训练目标或执行规则

事实。Todorov & Jordan 2002 的最小介入原理：偏差只在妨碍任务目标时才纠正，理由有两条，纠正任务无关的偏差得不到好处，产生纠正信号本身有害，因为噪声和力气代价都随控制量增大 [read]。Parikh & Boyd 2014：邻近算子 prox(v)＝argmin f(x)＋(1/2λ)‖x−v‖²，它与信赖域问题等价（每个邻近解都是某个半径的信赖域解，λ=半径/乘子，§3.4），不动点正是极小点 [read]。Gorelick 2013 在二值分割里实做了信赖域（trust region：只在当前点附近一圈内相信局部近似），并观察到半径与拉格朗日乘子近似成反比 [read]。

【推导】取 f＝−期望 Dice 收益，距离取汉明距离（翻转的体素个数）。翻转一个体素的一阶期望收益正比于 2q−D̂（加笔）或 D̂−2q（删笔），目标按体素可分，邻近步的闭式解就是逐体素门槛。再对“翻错的体素”收后续轮代价 κ，门槛就是 §0 的两个式子。有一点要注意：0.9 相当于赔率门槛 9；Dice 账里假体素对真体素的代价比是 (D̂+κ)/(2−D̂)，κ=0、D̂=0.75 时只有 0.6，要到 9 需要 κ≈10.5。后续轮代价解释不了 0.9，更像是概率本身偏高（平衡抽样造成的先验偏移，G 路 §13、Menon 2021 的 logit adjustment，按类别先验给对数几率加偏移）。所以公式的前提是 q 已校准，没校准的门槛是错的。

训练目标版有两种写法。一是把门槛放进软执行器，损失取“执行后软 Dice 减执行前软 Dice”，它自带改动代价，不需要再加 λ‖Δ‖（G 路的进步损失）。二是 Todorov 原版：保护项按误改的下游代价（cost-to-go）加权，而不是一个全局常数。

λ（连同 κ）不手定的三条路：

- 由数据和模型自己的预测算：D̂ 来自一个质量估计头（训练标签是 TRAIN 状态的真实 Dice），q 来自先验偏移校准；零新超参。
- 学出来：Kendall 2018 的不确定度加权，把每一项损失的权重写成可学的 σ，对 log σ² 的初值（−2 到 5）稳健 [read]；或者用小控制头在多轮进步损失下训出门槛偏移（§2.2）。
- 反馈整定：PPO 把惩罚系数 β 绑到“目标改动量”上，实际改动超过目标的 1.5 倍就把 β 翻倍，低于 1/1.5 就把 β 减半 [read]；目标改动量可以取模型自己估计的被指区域大小 Σp_T【推测】。

TRPO 的作者写明理论给出的惩罚系数让步子太小、难稳健地选，改用硬约束 δ [read]（L3-05）：由理论直接算出的 λ 偏保守，要么学，要么按预算整定。

限制。门槛只平移排序，不增加区分度；“任务无关方向”要定义对：O 里的真病灶改了 Dice 也涨，只是协议要求不动。交互分割里靠规则保护已有掩膜的有 FocalClick 的渐进合并和 FCFI 的局部修正（D 路已记）；带显式改动量惩罚的没查到（§4.2）。

### 2.2 多轮超调：理论上怎么避免，增益怎么学

对应关系。执行器里的“增益”是门槛的位置，门槛越低增益越大，修回和溢出一起涨。训练里的“增益”是平衡抽样烤进 logit 的先验赔率：评价块按 T、O、P 各 40%、30%、30% 抽，含 T 的块比部署时滑窗扫过的块多得多，等于把 T 的赔率抬高了一个常数（G 路 §13 的先验偏移，偏移量可用 TRAIN 回放实测）。

理论给的条件，各自来自：

- 单调性是设计目标，稳健要用步长换。Liao-McPherson 2022 的优化型 ILC（迭代学习控制）用过程测量代替模型，设计目标是误差范数单调下降、不动点对准控制目标，为在噪声和模型误差下稳定而给步长设上限，代价是收敛更慢 [read]。
- 信赖域用比值管步长。Gorelick 2013：实际下降/预测下降高于 η2=0.25 就允许放大半径，候选不降能量则缩小半径，η2 取 0 到 0.75 都稳健 [read]。
- 重复套用同一个算子要有可验证的收缩条件。Ryu 2019：去噪器的残差满足 Lipschitz 常数 ε 时，PnP 迭代无需递减步长就收敛，并用真谱归一化训练到满足条件；普通谱归一化没压住（实测各层谱范数 3.01、2.96、2.82、1.31）[read]。这只适合轮内重复调用或生长模块，跨轮笔会变，算子不是同一个。
- DEQ（深度平衡模型）图 2：深 transformer 可能绕着不动点振荡，直接求平衡点的模型稳定 [read]。

增益怎么学。建议一个小控制头，输入全是无量纲量：轮次序号、符号、D̂、当前笔与上一轮改动区的符号化重叠比例（笔落在上一轮新增区里且方向相反，等于上一轮溢出的证据）、候选集的期望溢出比 ĥ＝Σ(1−q)/Σq。输出对门槛的偏移，最后一层零初始化，初始行为不变。训练用两步展开的软执行和进步损失（§2.4）。Gorelick 的比值在测试时没有 GT，可用“下一笔落在刚加的区域里”当代理：落在里面说明上一步 ρ＜0，该缩【推测】。

先例与差别。TIA 把点击间的精度波动叫 overshoot，用 NoDC（加点击后 IoU 下降的案例数）和 mDIoU（平均降幅）度量，三个特征分支对应 PID（比例、积分、微分三项控制）的三项 [read]；MedSAM-Agent 的超调惩罚 R_over＝IoU_max−IoU_final 罚峰值之后的下降 [read]。它们都在 2D，是特征融合或奖励项，不是执行规则，也没有“学出增益”。大模型自我纠错有同形结论：继续迭代有益当且仅当 ECR/EIR＞Acc/(1−Acc)（ECR 错误纠正率，EIR 错误引入率，L3-30）。

### 2.3 固定步数 K 换成学出来的停止

按模块性质分两类。

单调的最弱一环扩散（PLAN 附二的指代生长）不需要 K。它必然停在不动点，迭代到相邻两次无任何体素变化即停，最坏迭代次数是最长最优路径的跳数，每次迭代只是邻域最大值再逐点取小，很便宜。反传可以不展开：每个目标体素的值等于最优路径上最弱那个体素的通行度，梯度只落在这个瓶颈体素上，沿记录的瓶颈指针回溯即可，这是 DEQ 的隐函数定理在“取大、取小”两种运算上的特例【推导，有并列最优时要平滑】。精确不动点也可由 widest path 算法（求最弱一环最强的路径）一次得到（zong-2026 在上一轮 47 篇里）。

学出来的非单调传播（GRU 一类）没有不动点保证，要用学出的停止。现成做法的系数问题：ACT 的 τ 手定且自述敏感（L3-15）；PonderNet 的先验 λ_p 过短会失败、偏长则自己收敛（L3-16）；DEQ 的容差 ε 取大了精度发散（L3-14）；CFR-ICL 的停止阈值是绝对的 20 像素（L3-22）；基于状态变化量的启发式停止在 PathFinder-21、-24 上完全不泛化，学出的停止泛化（Veerabadran 2023，见 L3-16）。学出停止的还有 DURR（Q 学习，L3-17）、HRM（Q 学习）与 TRM（监督式二元交叉熵，L3-18）、Pace 2022（监督式伯努利停止指示，L3-19）。

我们有 GT，不必用 Q 学习。推荐：标签＝训练时路径上的最佳停点（迭代序列里 T-Dice 最大的那一步），交叉熵训练停止头，无 ponder cost、无先验。同时训练时随机 K、每步都算损失（RAFT 序列损失权重 γ=0.8、IEF 的课程训练），推理时 K 可大于训练 K：RAFT 训练展开 12 次，推理试到 200 次也不发散 [read]。通用性上，步数交给停止头按病灶尺度自己定；Codex 第二轮把 32 步折成约 96 mm，换了体素间距就不成立。

### 2.4 五轮当整体优化：做过吗，效果和代价

| 工作 | 做法 | 效果 | 代价和局限 |
|---|---|---|---|
| IteR-MRL 2020 | 每个体素一个共享策略的 agent，动作是对概率的小幅加减 {±0.1,±0.2,±0.4}，奖励＝相邻步交叉熵下降，A3C（一种强化学习算法），T=5 | BraTS2015：5 步 88.53，InterCNN 85.56，DeepIGeoS 85.80；对手第 2 步起几乎不涨 | 图 55×55×30、MRI，训练几小时到 2 天（Titan X），每步 894 ms |
| BS-IRIS 2021 | 加边界奖励、超体素点击 | 全肿瘤 90.81±3.42，IteR-MRL 89.45；相对奖励比绝对奖励高约 1.1 点 | 计算时间更高；连续动作难收敛 |
| CFR-ICL 2024 | 每步点击都算损失 L＝Σλ_i·L_i | SimpleClick→ICL：Berkeley NoC@95 6.71→6.48，DAVIS 12.23→11.86 | 2D 自然图像，改进小 |
| MedSAM-Agent 2026 | 多模态大模型当智能体，GRPO，进步奖励＋超调惩罚，最多 5 轮 | 6 种模态 21 个 2D 数据集上最好（原文） | Qwen3-VL-8B，8 张 H20 |

共同点：IteR-MRL、BS-IRIS、MedSAM-Agent 的奖励都是相邻步的进步量，BS-IRIS 的消融里相对奖励优于绝对奖励；IteR-MRL 训练和测试用同一种交互策略。MPC 本身没查到（§4.2）。G 路已记 SegAgent（2025）：回放自己的点击轨迹，把让分数下降的动作换成模拟器的动作。Differentiable MPC（Amos 2018）说明代价参数可端到端学，但要一个动力学模型。我们的“动力学”是已知的执行器加模拟器，训练时模拟器能用 GT，测试时没有 GT，做不了推理时规划。

对本项目的判断。逐体素标签由教师给，信息比任何奖励都多（G 路对 DPO 的同一结论）；试错式的优化只该用在没有标签的标量控制上。做法如下，前两条要做，第三条不做：

- 两步展开，第一步截断梯度，笔仍由冻结模拟器按 GT 生成，不求导；损失＝每步逐体素损失＋软 Dice 进步项；逐步权重用不确定度加权学出。Metz 2019 说长展开梯度爆炸、短截断有偏，所以只展开两步 [摘要]。
- 对 κ、停止这类标量，在诱导状态上给 4 到 5 个候选值，各向前滚动 2 轮，取 D5 最好的，蒸馏给控制头（滚动展开标签，MPC 式）。成本估计：120 例×第 1–3 轮，每状态 1 次共用前向加 4 候选×2 轮，约 3200 次前向；按 PLAN 的 TRAIN 回放（约 6 小时跑 407 例×5 轮）折算每次约 10 秒，约 9 小时，未测。
- 不上完整强化学习：逐体素动作空间太大，IteR-MRL 靠体素共享策略和小图才可行。

## 3 逐篇记录

编号 L3-01 到 L3-31，都是新读；上一轮 47 篇不重复。主要条目按规定的七项写，次要条目并成四项（链接和领域；说的是什么；对得上与能搬；系数与风险）。PDF 在项目根 `Thesis/sirb-research-20261003/`。

### A 最优控制、邻近点、信赖域

### [L3-01] Todorov 2002《Optimal feedback control as a theory of motor coordination》Nature Neuroscience 5(11):1226
- 链接：https://doi.org/10.1038/nn963；PDF：已存 todorov-2002-optimal-feedback-control.pdf（作者主页公开版）。
- 领域：运动控制，随机最优反馈控制。
- 说的是什么：多关节动作的目标每次都达到，细节却每次不同。作者用随机最优反馈控制解释：最优控制器不跟踪固定轨迹，只纠正妨碍任务目标的偏差，对任务无关的冗余方向（uncontrolled manifold，不受控流形）任其变化，称 minimal intervention（最小介入）。理由写了两条：纠正无关偏差得不到好处；纠正信号本身可能有害，因为噪声和力气代价都随控制量增大。模型是带乘性噪声的离散线性系统 x(t+1)=Ax+Bu+ΣCᵢuεᵢ，二次任务代价，最优律 u=−L·x̂，x̂ 由卡尔曼滤波（用前向模型从带噪观测估计状态）给出。
- 和哪处痛点对得上：P1、P7。T 是任务相关方向，O 和 P 是该放着不动的方向；“纠正有害”对应实测溢出，ADD 0.5–10 mL 每修回 1 mL 约带出 0.75 mL 新 FP（G 路引）。
- 能搬过来变成什么：保护项（L_preserve）按“误改的下游代价”加权；执行规则用 §2.1 的门槛，κ 即后续轮代价；诊断上用“改动落在 T 内外的体积比”当不受控流形的方差比。
- 系数怎么来：原文代价矩阵按任务定义，噪声强度由数据拟合，没有全局常数。搬过来：噪声强度对应溢出比 h，按类按轮从回放轨迹测；代价对应 Dice 一阶式 (2−D)/D。
- 证据强度和风险：神经科学行为实验加仿真，线性高斯；掩膜是离散的。“任务无关”若定义错（O 里的真病灶改了 Dice 也涨）会放过该修的。交互分割里没人这样写。Scholz & Schöner 1999 的 UCM 原文是 Springer 付费墙，未读，只用本文对它的转述。

### [L3-02] Todorov & Jordan 2003《A Minimal Intervention Principle for Coordinated Movement》NIPS 15
- 链接、说的是什么、风险：https://papers.neurips.cc/paper/2195-a-minimal-intervention-principle-for-coordinated-movement.pdf；PDF：已存 todorov-2003-minimal-intervention-nips.pdf。L3-01 的技术版，用最优代价函数的梯度和 Hessian 做局部分析，定义“冗余”和“纠正”。只读摘要和引言，数学段的文本抽取是乱码，未核；对得上、能搬、系数同 L3-01。

### [L3-03] Parikh & Boyd 2014《Proximal Algorithms》Foundations and Trends in Optimization 1(3):127
- 链接：https://web.stanford.edu/~boyd/papers/prox_algs.html；PDF：已存 parikh-2014-proximal-algorithms.pdf（作者主页，113 页）。
- 领域：凸优化。
- 说的是什么：proximal operator（邻近算子）把“最小化 f”和“离上一点 v 不要太远”合成一个问题：prox(v)＝argmin f(x)＋(1/2λ)‖x−v‖²，λ 起步长作用（§1）。三条有关：不动点正是 f 的极小点（§2.3）；邻近问题与信赖域问题等价，每个邻近解都是某个半径的信赖域解，反之亦然，λ＝半径/乘子（§3.4）；proximal point 迭代 x(k+1)＝prox(x(k)) 只要极小点存在就收敛，变步长时 λ_k＞0 且 Σλ_k＝∞ 即可，求解允许有误差但误差要可求和（§4.1）。
- 和哪处痛点对得上：P1、P4。“满足指代＋离上一轮不要太远”就是邻近步，五轮是邻近点迭代。
- 能搬过来变成什么：单轮编辑写成 argmin[ℓ_ref(x)＋λ·d_H(x,M)]，d_H 是汉明距离，目标按体素可分，解是逐体素门槛，λ 与门槛一一对应（§2.1）。
- 系数怎么来：理论只要求 Σλ_k＝∞，没有给取值。搬过来 λ_t 由 D̂_t 和校准概率算。
- 证据强度和风险：凸函数理论。我们的 ℓ_ref 来自神经网络，非凸且有误差，单调性只在邻近步被精确求出时成立；“误差可求和”是条件，不是结论。

### [L3-04] Gorelick 2013《Fast Trust Region for Segmentation》CVPR
- 链接：https://openaccess.thecvf.com/content_cvpr_2013/html/Gorelick_Fast_Trust_Region_2013_CVPR_paper.html；PDF：已存 gorelick-2013-fast-trust-region-segmentation.pdf。
- 领域：分割的能量最小化，信赖域。
- 说的是什么：对带非线性区域项（KL 散度、Bhattacharyya 距离、体积约束、形状矩）的二值分割能量，每步在当前分割 S0 附近半径 d 的球内最小化一个近似模型，再算“实际能量下降/预测下降”的比值，高于 η2＝0.25 就放大半径。他们用拉格朗日形式 E~(S)＋(λ/2)dist(S0,S)²，经验上发现 d 与 λ 近似成反比，于是半径的自适应规则直接变成 λ 的自适应规则。η2 取 0 到 0.75 都稳健（图 10）。摘要称比现有最好方法快 1–2 个数量级；图 8、9 的例子里精确线搜索约慢 100 倍，“模拟梯度下降”降不动能量。
- 和哪处痛点对得上：P1、P4。分割里“在当前分割附近、惩罚形状距离”的邻近项早有二值标签版本。
- 能搬过来变成什么：每轮候选编辑按门槛阶梯排列，门槛越低半径越大；用 ρ＝实际下降/预测下降决定放大或缩小。测试时没有 GT，实际下降用代理：医生下一笔落在刚加的区域里，等于 ρ＜0【推测】。
- 系数怎么来：η1＝0、η2＝0.25 取自信赖域教科书的推荐（原文引 Yuan 1999），不是对本任务调出来的；λ 随半径自适应。
- 证据强度和风险：2013 年的自然图像和少量医学图像，能量能直接算；我们的“能量”是与 GT 的 Dice，测试时拿不到。交互分割里没查到。Conn–Gould–Toint 的专著未取得，用本文和 L3-03 §3.4 代替。

### [L3-05] Schulman 2015《Trust Region Policy Optimization》ICML
- 链接：https://arxiv.org/abs/1502.05477；PDF：已存 schulman-2015-trpo.pdf。
- 领域：强化学习，策略优化。
- 说的是什么：新策略的真实回报不低于“以旧策略为中心的替代目标减 C×新旧策略最大 KL”，每步最大化右边就得到单调不下降的策略序列（Theorem 1、Algorithm 1）。理论给的惩罚系数 C 会让步子很小，作者写“经验上难以稳健地选惩罚系数”，改成 KL 的硬约束 δ，所有实验取 0.01。
- 和哪处痛点对得上：P4。“每轮只走可信的一步”；λ 难选正是我们的问题。
- 能搬过来变成什么：编辑前后输出分布的距离约束；我们有标签，单步 Dice 增益就是替代目标。
- 系数怎么来：C 和 δ 都手定；δ＝0.01 对所有任务通用，但仍是常数。
- 证据强度和风险：连续控制和 Atari 上有效。单调性只对近似之前的目标成立，做了近似就不再有保证；理论系数太保守是作者自己写的。

### [L3-06] Schulman 2017《Proximal Policy Optimization Algorithms》
- 链接和领域：https://arxiv.org/abs/1707.06347；PDF：已存 schulman-2017-ppo.pdf。强化学习。
- 说的是什么：KL 惩罚系数的反馈整定：设目标 KL（d_targ），更新后若 d＜d_targ/1.5 则 β 减半，若 d＞1.5·d_targ 则 β 翻倍；1.5 和 2 是启发式，算法对它们不敏感。作者报告这个版本比裁剪版差。
- 对得上、能搬、系数与风险：P1、P4。λ 随“实际改动量”自己调；目标改动量取模型估计的被指区域大小 Σp_T（【推测】，无出处），替代手定的 d_targ。我们的改动量是体素数，不是分布距离。

### [L3-07] Laroche 2019《Safe Policy Improvement with Baseline Bootstrapping》ICML
- 链接和领域：https://arxiv.org/abs/1712.06924；PDF：已存 laroche-2019-spibb.pdf。离线强化学习。
- 说的是什么：从固定数据训练一个以高概率不比基线差的策略。证据不足的（状态，动作）对（计数小于阈值 N∧，称 bootstrapped 集）原样照抄基线的概率，其余才优化，即“不确定时用基线补位”（knows-what-it-knows）。Theorem 2：以 1−δ 的概率，新策略最多比基线差 ζ，ζ 含 (4Vmax/(1−γ))·√((2/N∧)·log(2|X||A|2^|X|/δ))；安全性随时间长度线性变差。
- 对得上与能搬：P1、P7。指代不确定时，最安全的行为是不动。对每个候选区域算证据量（例如同一笔做几次小扰动，p_T 的一致程度），证据不足的地方保持当前分割。
- 系数与风险：N∧ 由置信水平 δ 和允许回退量 ζ 反解，δ 是通用约定。表格 MDP 的理论加小型导航实验；连续特征要用伪计数；交互分割里没人用。

### B 展开、学出的步长和门槛

### [L3-08] Gregor & LeCun 2010《Learning Fast Approximations of Sparse Coding》ICML
- 链接和领域：https://icml.cc/Conferences/2010/papers/449.pdf；PDF：已存 gregor-2010-lista.pdf。稀疏编码，展开。
- 说的是什么：ISTA 的迭代是 Z(k+1)＝h(We·X−S·Z(k))，h 是阈值为 θ 的收缩函数，标准 ISTA 把 θ 固定为 α/L。作者把迭代截成固定深度，We、S、θ 都变成可训练参数，即后来的 LISTA（学出来的迭代收缩阈值算法）。m=100 时 FISTA 要 18 次迭代才达到 LISTA 1 次迭代的误差，m=400 要 35 次；结论写低迭代区间约少 20 倍。
- 对得上与能搬：P3、P1。生长或修正模块每一步的门槛、步长做成逐步可学的标量，用解析值初始化。
- 系数与风险：We、S、θ 全部学出，初值取解析公式。线性逆问题；深度仍是固定的，只是 K 很小。

### [L3-09] Chen 2018《Theoretical Linear Convergence of Unfolded ISTA and its Practical Weights and Thresholds》NeurIPS
- 链接：https://arxiv.org/abs/1808.10038；PDF：已存 chen-2018-lista-linear-convergence.pdf。
- 领域：展开网络的收敛理论。
- 说的是什么：给出展开 ISTA 收敛的必要条件（两个权重矩阵必须渐近耦合，可去掉一个），耦合后线性收敛，优于 ISTA 与 FISTA 的次线性。提出 support selection（支撑选择）：每层把幅值最大的 p^k% 条目当作“可信支撑”，不经阈值直接传入下一层，理论和实验都加快收敛。他们的解释：LASSO 里 λ 大则收敛快但解不准，每步自适应的 λ 路径折中更好，LISTA 学出的阈值序列就是这条路径；实测阈值随层数趋于 0（图 2）。
- 和哪处痛点对得上：P1、P3。“高置信体素不受门槛惩罚”和“阈值逐步放松”。
- 能搬过来变成什么：每轮或每步的门槛序列由网络学出且允许递减；被笔直接覆盖且高分的体素放行，不过门槛。
- 系数怎么来：p^k＝min(p·k, p_max)，p 与 p_max 是作者手调的（原文写明）。搬来要用模型自身置信度的分位数或学出的门控替代。
- 证据强度和风险：合成稀疏恢复加压缩感知。稀疏编码到掩膜编辑只是结构上的类比。

### [L3-10] Monga 2021《Algorithm Unrolling: Interpretable, Efficient Deep Learning for Signal and Image Processing》IEEE SPM
- 链接和领域：https://arxiv.org/abs/1912.10557；PDF：已存 monga-2021-algorithm-unrolling.pdf。综述。
- 说的是什么：unrolling（展开）把迭代算法的一步映射成网络一层。层参数共享则像 RNN，省参数但训练面临梯度爆炸或消失；逐层不同则易训，但可能丢掉原算法的收敛保证。LISTA 的层数可比 ISTA 收敛所需的迭代数少一个数量级。文中举 DURR（L3-17）为“从最优控制看”的例子。
- 对得上与能搬：P3、P4。初值取原算法，步长和门槛可学；生长模块若共享参数就要随机 K 训练。
- 系数与风险：综述无系数。只读了引言、LISTA 一节、理论一节和训练讨论的片段。

### [L3-11] Teed & Deng 2020《RAFT: Recurrent All-Pairs Field Transforms for Optical Flow》ECCV
- 链接和领域：https://arxiv.org/abs/2003.12039；PDF：已存 teed-2020-raft.pdf。光流。
- 说的是什么：更新算子（GRU）模仿一阶优化，用共享权重和有界激活促使序列收敛到不动点；训练展开 12 次更新，序列损失权重按 γ^(N−i) 递增，γ＝0.8；推理可用任意次更新，试到 200 次也不发散，3 次更新就超过 PWC-Net。
- 对得上、能搬、系数与风险：P3、P4。多段监督加指数权重，推理 K 可大于训练 K；γ 手定，可改用 Kendall 式学出；光流任务。

### [L3-12] Carreira 2016《Human Pose Estimation with Iterative Error Feedback》CVPR
- 链接和领域：https://arxiv.org/abs/1507.06550；PDF：已存 carreira-2016-iterative-error-feedback.pdf。姿态估计。
- 说的是什么：不直接预测输出，而预测当前估计的“有界修正”（训练时 ‖ε‖＜L，L＝20 像素），加到当前估计后再喂回，共 4 步。PCKh-0.5 为 81.0，迭代地直接预测目标只有 73.4；不用 Fixed Path Consolidation（第 i 阶段只训练前 i 步修正的课程）掉近 10 点并出现多步漂移。
- 对得上与能搬：P4、P5。有界修正加课程训练稳住多步；生长模块每步只走一圈邻域并按步数做课程。
- 系数与风险：L 手定，要换成相对尺度。姿态估计。

### [L3-13] Ryu 2019《Plug-and-Play Methods Provably Converge with Properly Trained Denoisers》ICML
- 链接和领域：https://arxiv.org/abs/1905.05406；PDF：已存 ryu-2019-pnp-convergence.pdf。图像复原。
- 说的是什么：PnP-FBS 与 PnP-ADMM 在去噪器残差 (I−H) 满足 Lipschitz 条件时收敛，无需递减步长；real spectral normalization（真谱归一化）把卷积网络训到满足条件。普通谱归一化没压住：实测各层谱范数 3.01、2.96、2.82、1.31。
- 对得上与能搬：P4。重复套用同一个算子时“增益＜1”是可验证条件；只用于轮内重复调用或生长模块，跨轮笔会变，算子不是同一个。
- 系数与风险：约束常数是设计参数；压低整个网络的 Lipschitz 常数会损表达力。

### C 学出的停止、不动点

### [L3-14] Bai 2019《Deep Equilibrium Models》NeurIPS
- 链接和领域：https://arxiv.org/abs/1909.01377；PDF：另一路已存同内容文件 bai-2019-deep-equilibrium-models.pdf（大小一致，我未重复保存）。隐式深度网络。
- 说的是什么：权重共享的深网加深时会收敛到不动点。DEQ（deep equilibrium model，深度平衡模型）不逐层迭代，直接用拟牛顿法（Broyden）解 z*＝f(z*,x)，反传用隐函数定理。求根在残差小于容差 ε 或达最大迭代数时停。原文：f 要“稳定且受约束”才能可靠求平衡点；容差 ε 取大时精度发散（图 3）；深 transformer 可能绕着不动点振荡（图 2）。
- 对得上与能搬：P3、P4。指代生长取精确不动点（K＝∞），单调情形的反传见 §2.3。
- 系数与风险：ε 和最大迭代数是数值参数；单调最弱一环情形零容差。非单调的学出传播没有不动点保证；monDEQ（Winston & Kolter 2020，另一路已存 winston-2020-monotone-operator-equilibrium.pdf，只读摘要引言）给出保证唯一平衡点的单调参数化。

### [L3-15] Graves 2016《Adaptive Computation Time for Recurrent Neural Networks》
- 链接和领域：https://arxiv.org/abs/1603.08983；PDF：已存 graves-2016-adaptive-computation-time.pdf。循环网络。
- 说的是什么：RNN 每步输出一个停止概率，累积到 1−ε 就停；损失加 τ×ponder cost（思考成本，累积停止分数）。parity 任务无 ACT 时平均误差近 40%（随机为 50%），τ≤0.03 时误差低于 5%。作者写：结果对 τ 很敏感，不知道怎么选，“自动确定权衡”留作未来工作。
- 对得上与能搬：P3。不直接用，因为 τ 手定。
- 系数与风险：τ 手定且自述敏感。Figurnov 2017 SACT（另一路已存 figurnov-2017-sact.pdf，我只读摘要和引言）把 ACT 用到逐空间位置，可作逐体素停止的参考。

### [L3-16] Banino 2021《PonderNet: Learning to Ponder》ICML AutoML 研讨会
- 链接和领域：https://arxiv.org/abs/2107.05407；PDF：另一路已存 banino-2021-pondernet.pdf（大小一致）。自适应计算。
- 说的是什么：每步给“条件停止概率”，整体停止分布是几何型；损失＝按停止分布加权的预测损失＋停止分布对几何先验 p_G(λ_p) 的 KL，梯度无偏（ACT 有偏）。parity 外推（训练 1–48 个元素，测 49–96）：PonderNet 近乎满分，ACT 在随机水平，思考步数从约 3 增到 5。先验平均 1 步（λ_p＝0.9）时解不了；先验平均 10 步（λ_p＝0.1）时网络自己收敛到约 3 步。
- 对得上与能搬：P3 和通用性：换器官或体素间距，所需步数会变，停止头要能外推。学出的传播模块用这种停止头；λ_p 取 TRAIN 上量到的最短传播跳数中位数的倒数【推测】。
- 系数与风险：λ_p 是超参，但对偏长的先验不敏感。合成算法任务；视觉上的验证见 Veerabadran 2023（另一路已存 veerabadran-2023-adaptive-recurrent-vision.pdf，读了摘要、引言和 5.3 节）：基于状态变化量的启发式停止在 PathFinder-21、-24 上完全不泛化，学出的停止泛化。

### [L3-17] Zhang 2019《Dynamically Unfolding Recurrent Restorer: A Moving Endpoint Control Method for Image Restoration》ICLR
- 链接：https://arxiv.org/abs/1805.07709；PDF：已存 zhang-2019-durr-moving-endpoint.pdf。
- 领域：图像复原，最优控制。
- 说的是什么：复原当作控制问题，终点（迭代停在哪里）依赖输入的退化程度。模型＝卷积 RNN 复原单元（约 1.8×10⁵ 参数）加一个决定何时停的策略网络（约 1.0×10⁵ 参数）。奖励：继续则得 L(x(n−1),y)−L(x(n),y)，停止得 0，用 Deep Q-learning 训练。训练复原单元时对比固定循环 8 次与按噪声级手工指定步数，训练用的策略会影响复原单元的泛化。参数比 DnCNN（约 7.0×10⁵）少；在对两者都没见过的噪声级 σ＝65 的一张示例图上，22.84 dB 对 DnCNN 的 21.86 dB。
- 和哪处痛点对得上：P3。步数随输入难度自己定。
- 能搬过来变成什么：生长或迭代模块的终点由小策略头给，奖励＝本步让 T-Dice 涨多少。我们有 GT，直接用监督标签（最佳停点）代替 Q 学习。
- 系数怎么来：奖励无超参；但原文训练复原单元的“refined policy”步数表是手工指定的。
- 证据强度和风险：去噪和 JPEG 去块（PSNR），不是分割；强化学习训练常不稳。

### [L3-18] Jolicoeur-Martineau 2025《Less is More: Recursive Reasoning with Tiny Networks》（TRM）与 Wang 2025《Hierarchical Reasoning Model》（HRM）
- 链接和领域：https://arxiv.org/abs/2510.04871 ；https://arxiv.org/abs/2506.21734；PDF：已存 jolicoeur-martineau-2025-tiny-recursive-model.pdf、wang-2025-hierarchical-reasoning-model.pdf（HRM 只读摘要、停止和逐段监督两节）。递归推理。
- 说的是什么：deep supervision（逐段监督）＝每段迭代后都算一次损失，并把潜状态截断梯度（detach）后作为下一段起点，TRM 最多 16 段。TRM 引 ARC Prize 的分析：逐段监督使准确率从 19% 到 39%，递归本身只从 35.7% 到 39.0%。HRM 的停止用 Q 学习（halt 或 continue，要第二次前向）；TRM 只学一个停止概率，标签是“当前答案是否已对”的二元交叉熵，推理时 q＞0 就停。HRM 推理时加大最大段数 M_max 可继续提高，无需重训。
- 对得上与能搬：P4、P5、P3。逐段监督加截断梯度，就是不穿过全部轮次反传的展开；停止头标签改成“下一次迭代不再提高 T-Dice”，无系数。
- 系数与风险：HRM 的最小段数以概率 ε 随机取，是超参，TRM 去掉了 Q 学习。数独、迷宫、ARC 谜题，与分割差得远，只借训练和停止的做法。

### [L3-19] Pace 2022《Learned iterative segmentation of highly variable anatomy from limited data》Medical Image Analysis 80:102469
- 链接：https://doi.org/10.1016/j.media.2022.102469；PDF：已存 pace-2022-learned-iterative-segmentation.pdf（第一作者主页）。
- 领域：医学影像，迭代分割，学出的停止。
- 说的是什么：RNN 从用户的一次点击出发，把分割逐步长出来，直到自动判定的停止点。每步输出分割和一个伯努利停止指示，停止损失是类别加权的二元交叉熵，推理取后验＞0.5 为停（原文说也可按领域知识换阈值）。用 teacher forcing（教师强制）训练：由完整标注即时生成“部分完成的分割→下一步”的样本，损失按时间步拆开，不需要穿过时间反传。60 例心脏 MR。自动停止与最佳停止有差距，用户可前后翻看补救，补救后严重病例平均 Dice 超过 85。
- 和哪处痛点对得上：P3、P5、P2。“从种子长到被指的对象”，逐步状态由 GT 即时生成，同我们的状态库做法。
- 能搬过来变成什么：生长或迭代模块的监督式停止头；用 GT 造“部分完成”的训练状态。
- 系数怎么来：停止阈值默认 0.5；类别权重由停止点占比算，不手调。
- 证据强度和风险：60 例心脏 MR，不是 PET/CT；自动停止有误差；我们的生长受状态门限制，样本分布不同。

### D 交互分割里的多轮优化

### [L3-20] Liao 2020《Iteratively-Refined Interactive 3D Medical Image Segmentation with Multi-Agent Reinforcement Learning》CVPR
- 链接：https://arxiv.org/abs/1911.10334；PDF：已存 liao-2020-iter-mrl.pdf。
- 领域：三维交互分割，多智能体强化学习。
- 说的是什么：多轮交互建成 MDP（马尔可夫决策过程），每个体素是共享策略的一个 agent。状态＝[体素值，上一轮分割概率，两张提示图]；动作＝对上一轮概率加一个小量，动作集 {±0.1,±0.2,±0.4}，加入 ±1.0 反而伤性能，连续动作难训；奖励＝相邻两步交叉熵的下降，累积折扣 γ＝0.95，用 A3C 训练，T＝5 步、每步 5 笔，模拟医生点最大 5 个错误区域的中心。BraTS2015，V-Net 起点 77.15：5 步后 IteR-MRL 88.53，InterCNN 85.56，DeepIGeoS 85.80；逐步增益 +7.20、+2.43、+0.83、+0.57、+0.35，对手从第 2 步起几乎不涨（DeepIGeoS 第 3 步 −0.01），与我们的“第 2 轮几乎不涨”同形。
- 和哪处痛点对得上：P1、P4、P5。有界步长防突变；相对进步奖励；训练与测试用同一种交互策略。
- 能搬过来变成什么：动作是对 logit 的小步长调整，而不是整块重预测；奖励是 Dice 进步量。
- 系数怎么来：动作集和 γ 手定。
- 证据强度和风险：图小（55×55×30）、MRI、训练几小时到 2 天（Titan X）；没有 CT 和 PET，没和 nnU-Net 一类强基线比。

### [L3-21] Ma 2021《Boundary-aware Supervoxel-level Iteratively Refined Interactive 3D Image Segmentation with Multi-agent Reinforcement Learning》IEEE TMI 40(10)
- 链接和领域：https://arxiv.org/abs/2303.10692；PDF：已存 ma-2021-bs-iris.pdf。三维交互分割。
- 说的是什么：IteR-MRL 的加强版：奖励＝全局相对交叉熵增益＋边界奖励（按到 GT 边界的距离加权），交互改为超体素点击。BraTS2015 全肿瘤，4 次交互×6 点：BS-IRIS 90.81±3.42，IteR-MRL 89.45±3.66，DeepIGeoS 87.19，InterCNN 86.75。奖励消融：绝对奖励 88.67，绝对加边界 89.59，相对 89.80，相对加边界 90.81；相对奖励比绝对高约 1.1–1.2 点。作者写连续动作空间难收敛，二值状态无法收敛。
- 对得上与能搬：P4。证据是“进步量奖励优于绝对奖励”；边界权重对应我们边界处的越界。
- 系数与风险：边界奖励权重 λ 手定。同 L3-20，计算时间更高。

### [L3-22] Sun 2024《CFR-ICL: Cascade-Forward Refinement with Iterative Click Loss for Interactive Image Segmentation》arXiv 2303.05620（v2）
- 链接和领域：https://arxiv.org/abs/2303.05620；PDF：另一路已存 sun-2024-cfr-icl.pdf（大小一致）。2D 交互分割。
- 说的是什么：Iterative Click Loss（迭代点击损失）L＝Σᵢλᵢ·L(Yᵢ,Y)，每个点击步都算一次损失，后面步的权重更大，鼓励用更少点击；训练用 3 个迭代生成的点击（λᵢ∈[1,2,3]），从训练好的 SimpleClick 微调 1 个 epoch。SimpleClick→ICL（NoC，越小越好）：Berkeley @95 6.71→6.48，DAVIS @95 12.23→11.86，GrabCut @95 2.16→2.00。推理的 Adaptive CFR：内循环里相邻两次输出改变的像素数低于阈值就停（20 像素），好于固定 4 步；作者写增加步数不保证更好。
- 对得上与能搬：P4、P3。序列损失的逐步权重可改成学出的；停止规则的阈值改成相对量并由数据决定。
- 系数与风险：λᵢ 手定；20 像素手定且是绝对像素数。2D 自然图像，改进小。

### [L3-23] Wei 2024《Interactive Image Segmentation with Temporal Information Augmented》BMVC
- 链接：https://papers.bmvc2024.org/0101.pdf；PDF：未存（BMVC 论文集不在允许的来源清单；全文已通过网页读取）。
- 领域：2D 点击交互分割，控制类比。
- 说的是什么：把交互分割看成带反馈的控制系统：新点击后精度反而大幅下降叫 accuracy fluctuation（精度波动），类比超调；点击用完仍留的误差叫 constrained minimal error，类比稳态误差。方法 TIA 的三个分支对应 PID 三项：Interaction Propagation（当前，P）、Memory Incorporation（过去各轮的前景背景信息，I）、Difference Awareness（感知上一轮与本轮分割的差异，D）。稳定性指标：NoDC（点击加入后 IoU 下降的案例数）、mDIoU（这些案例的平均降幅）。DAVIS、ViT-B 消融：基线 NoC@90 5.06、NoDC20 1685、mDIoU 0.79%；三支路全加 4.78、1478、0.26%（按表格行顺序读出，未逐格核对）。
- 和哪处痛点对得上：P1、P4，就是我们的“超调”在 2D 点击里的版本。
- 能搬过来变成什么：NoDC、mDIoU 当机制指标，用已存轨迹就能算；D 分支（感知上一轮与本轮分割的差异）近似于把上一轮改动图当输入（efference copy，§2.2）。
- 系数怎么来：三个分支都是学出的特征融合，没有手定增益。
- 证据强度和风险：自然图像加点击；只是特征融合，不是执行规则；“PID”是类比，没有稳定性证明。

### [L3-24] Liu 2026《MedSAM-Agent: Empowering Interactive Medical Image Segmentation with Multi-turn Agentic Reinforcement Learning》arXiv 2602.03320
- 链接：https://arxiv.org/abs/2602.03320；PDF：已存 liu-2026-medsam-agent.pdf。
- 领域：医学分割，智能体强化学习。
- 说的是什么：把交互医学分割当多步决策。多模态大模型（Qwen3-VL-8B）当智能体调用 SAM2.1、MedSAM2 等工具，每步把当前掩膜叠到图上再编码，最多 5 轮。先用专家轨迹监督微调，再用 GRPO（组相对策略优化，一种强化学习算法）训练。奖励含：进步奖励 R_imp＝Σmax(0, IoU_t−IoU_(t−1))；overshoot penalty（超调惩罚）R_over＝IoU_max−IoU_final，罚峰值之后的下降，作者称这让模型学到在收益递减处停止；另有与序列长度成正比的工具成本。6 种模态 21 个 2D 数据集，8 张 H20。
- 和哪处痛点对得上：P1、P4。“超调惩罚”和“进步奖励”是我们想要的训练项。
- 能搬过来变成什么：把软 Dice 版的 R_imp 和 R_over 加进两步展开的损失（§2.4）。
- 系数怎么来：权重 w 和 β₁、β₂、β₃ 全是手定。
- 证据强度和风险：智能体自己选提示，不是医生的笔；2D；大模型；2026 年预印本。

### E 增益、不确定度、规划、稳定性

### [L3-25] Kendall 2018《Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics》CVPR
- 链接和领域：https://arxiv.org/abs/1705.07115；PDF：已存 kendall-2018-uncertainty-weighting.pdf。多任务学习。
- 说的是什么：手调多任务损失权重“困难且昂贵”。把每个任务建成带同方差不确定度 σᵢ 的高斯似然，损失约为 Σ(1/2σᵢ²)Lᵢ＋log σᵢ，σᵢ 随网络一起学；对 log σ² 初值（−2 到 5）稳健。
- 对得上、能搬、系数与风险：每轮损失权重（5 个数）和 L_err、L_bind、L_DiceT 之间的权重都可以这样学。权重学出；可能压低难任务，逐轮之间并不独立。

### [L3-26] Revach 2022《KalmanNet: Neural Network Aided Kalman Filtering for Partially Known Dynamics》IEEE TSP
- 链接和领域：https://arxiv.org/abs/2107.10043；PDF：已存 revach-2022-kalmannet.pdf。状态估计。
- 说的是什么：卡尔曼增益本来由噪声统计算出。KalmanNet 保持“先验＋增益×新息”的更新结构，只把增益用 RNN 学出，状态方程失配时比基于模型的卡尔曼滤波好约 3 dB；在 T＝20 训练、T＝200 测试时仍与滤波只差一小截，端到端 RNN 差 50 dB 以上。
- 对得上与能搬：P1、P7。增益应由“先验可靠度/测量可靠度”决定。更新写成“新掩膜＝当前掩膜＋增益⊙新息”，新息是这一笔的指代证据，增益由小网络给，输入含笔的歧义度和 D̂。
- 系数与风险：增益学出。线性动力学，掩膜离散，类比只在结构上；没查到把点击当卡尔曼测量的交互分割（§4.2）。

### [L3-27] Amos 2018《Differentiable MPC for End-to-end Planning and Control》NeurIPS
- 链接和领域：https://arxiv.org/abs/1810.13400；PDF：已存 amos-2018-differentiable-mpc.pdf。模型预测控制。
- 说的是什么：MPC 在滚动时域上求最优控制序列，通常只执行第一个动作再重解。文章在不动点处用 KKT 条件求导，端到端学代价和动力学；摆和倒立摆的模仿学习里比同规模通用网络省数据。
- 对得上、能搬、系数与风险：P4。代价参数（含 λ）可端到端学；推理时不做 MPC，训练时用滚动展开给标量控制造标签（§2.4）。低维连续控制，我们是高维离散掩膜。

### [L3-28] Metz 2019《Understanding and correcting pathologies in the training of learned optimizers》ICML
- 链接和领域：https://arxiv.org/abs/1810.10180；PDF：已存 metz-2019-learned-optimizer-pathologies.pdf（只读摘要、引言）。学出的优化器。
- 说的是什么：穿过展开的优化过程反传时，截断短则梯度有偏，截断长则范数爆炸；作者动态加权两个无偏梯度估计来克服。
- 对得上、能搬、系数与风险：P4、P5 的训练风险，所以五轮展开只做 2 步、第一步截断梯度。加权细节未读；任务不是分割。

### [L3-29] Liao-McPherson 2022《On Robustness in Optimization-Based Constrained Iterative Learning Control》
- 链接和领域：https://arxiv.org/abs/2203.05291；PDF：已存 liao-mcpherson-2022-robust-constrained-ilc.pdf。迭代学习控制。Bristow 2006 综述是 IEEE 付费，未读，用本文代替。
- 说的是什么：ILC（迭代学习控制：同一任务反复做，用上一次的测量误差改下一次的输入）。优化型 ILC 的设计目标是误差范数单调下降、不动点对准控制目标。作者用前向后向分裂，给出噪声和模型误差下的“迭代域输入到状态稳定”分析；无约束时等于 norm-optimal ILC（求“跟踪误差＋输入改变量”之和最小）加一个步长。仿真里它比 NO-ILC 收敛慢但渐近误差更低：为稳健稳定给步长设了上限。
- 对得上与能搬：P4。稳健性与速度的取舍；把“网络预测的编辑效果”看作不准的过程模型，它的误差大小决定允许的增益。
- 系数与风险：步长上限由模型误差界给出。线性过程；Amann–Owens–Rogers 1996 与 Bristow 综述未读，norm-optimal ILC 的说法转述自本文。

### [L3-30] Liu 2026《Self-Correction as Feedback Control: Error Dynamics, Stability Thresholds, and Prompt Interventions in LLMs》arXiv 2604.22273
- 链接：https://arxiv.org/abs/2604.22273；PDF：已存 liu-2026-self-correction-feedback-control.pdf。
- 领域：大模型自我纠错，反馈控制。
- 说的是什么：把反复自我纠错当反馈控制，建成 {对,错} 两状态马尔可夫链，错误引入率 EIR（对→错）、错误纠正率 ECR（错→对）。准确率递推 Acc(k+1)＝Acc(k)(1−EIR)＋(1−Acc(k))·ECR；继续迭代有益当且仅当 ECR/EIR＞Acc/(1−Acc)；收敛是几何的，速率 |1−EIR−ECR|^k。7 个模型、GSM8K、4 轮：只有 EIR 约低于 0.5% 的模型受益；GPT-4o-mini 从 91.2% 降到 85.0%（EIR 从 1.3% 升到 3.8%）。自适应停止规则 ASC 在 500 题上第 0 步就停，但置信度提示本身掉 3.8 点。
- 和哪处痛点对得上：P1、P4。EIR 对应溢出和误伤，ECR 对应修回；“稳定阈值”的形式同我们的 hA＜(2−D)/D。
- 能搬过来变成什么：用已存轨迹按目标类型算 EIR、ECR，作为机制指标（诊断，无系数）。
- 证据强度和风险：预印本，未同行评审；语言模型；作者承认 EIR 随轮次变大，非平稳。

### [L3-31] Wang-Lin 2026《If It's Not Buggy, Don't Fix It: On the Dynamics of Iterative Bug-fixing with LLMs》arXiv 2609.10123；附 Wu 2026《CyberCorrect》arXiv 2605.17305
- 链接和领域：https://arxiv.org/abs/2609.10123；https://arxiv.org/abs/2605.17305；PDF：已存 wang-lin-2026-iterative-bug-fixing-dynamics.pdf、wu-2026-cybercorrect.pdf（后者只读摘要引言）。大模型迭代修复。
- 说的是什么：把迭代修 bug 当离散动力系统 C(n+1)＝f(C(n))。大模型常在无 bug 的程序里“找出”bug，对有 bug 程序的修复率低于对正确程序的破坏率；用 search/replace 小改动时更常陷入同一改动反复加上又撤销的循环。CyberCorrect 把对正确内容的不必要改动称作 overshoot，并提出回滚。
- 对得上、能搬、系数与风险：P1、P4。最小介入的反面教材；循环就是 ADD 与 REMOVE 往返；回滚就是“撤销上一轮改动”的候选。大模型文本，CyberCorrect 是预印本，证据弱。

## 4 汇总

### 4.1 最有希望的改法（按预期对第五轮 Dice 的帮助、实现难度、新意排序）

#### A 校准过的 Dice 增益执行器（只改执行器，先做）

- 对应痛点：P1 中能由门槛处理的部分，P4。
- 做法：加笔的体素校准概率 q＞(D̂+κ)/(2+κ) 才加，删笔 q＜D̂/(2+κ_R) 才删，加删分开。D̂ 来自一个质量估计头（标签＝TRAIN 状态的真实 Dice，做法见 Robinson 2018）；q 由 p_T 经先验偏移校准得到（G 路 §13 的 logit adjustment，偏移量用 TRAIN 采样比例和 TRAIN 回放里 T 体素的真实占比算）。κ 从 0 起步。
- 系数：门槛全由 D̂ 和 q 决定，没有手定数；校准的偏移和斜率两个标量在 VAL 患者上二折交叉拟合，或在 TRAIN 回放上拟合后核对 VAL；κ=0 不够时才按轮次学，至多 5 个数。
- 最快验证（只用 TRAIN/VAL，不训练主网络）：先用已存的单步结果算事后最优门槛的上限（oracle：用 GT 逐状态挑最优门槛，只能当上限），即它的 Dice 与固定 0.5 的差，按患者平均的 D5 上限太小（比如不到 0.3 点，这是我定的停损线，不是统计规则）就停。再对 N1_STATE_INDUCED 与 N1_STATE_STATIC 里较好的 checkpoint 跑一次五轮快速 VAL（2–3 小时），并排报 0.5、PLAN 0-2 的手定门槛、本规则，判定沿用 PLAN 3.3 节。
- 预期【推测】：相对 0.5，D5 约 +0.3 到 +1.0，和手定的 0.7、0.9 可比；价值在不手定、可迁移。风险：校准做不好；门槛只平移排序。

#### B 上一轮改动图作输入，加增益控制头（PLAN 3-2 提前）

- 对应痛点：P4（后几轮约 29% 的笔落在自造的新错上，PLAN，未做空间核对）、P5。
- 做法：两个零初始化输入通道（上一轮改动的符号图、上一轮 p_T）；一个小控制头，输入轮次序号、符号、D̂、当前笔与上一轮改动区的符号化重叠比例，输出对门槛的偏移，末层零初始化。网络因此能学“撤销”：笔落在上一轮新增区且方向相反时，被指的对象就是那一次的多余部分。
- 系数：全部学出。
- 最快验证：在 N1_STATE_INDUCED 之后续训 8k，对照同样样本不加该通道；看第 2–5 轮增益、变差轮次比例（v1 为 22.4%，续训对照 N1_STATE_STATIC 为 16.5%，A 路）、笔落在自造错上那部分轮次的修回、NoDC 与 mDIoU。可证伪的预测：D1 不变，D2 到 D5 的增量变大。
- 预期【推测】：D5 0 到 +1.5，把握低到中。

#### C 两步展开的进步损失，加滚动展开给标量控制造标签

- 对应痛点：P4、P5、P8。
- 做法：训练块从诱导状态出发做两步，第一步截断梯度，笔由冻结模拟器按 GT 生成、不求导。损失＝每步逐体素损失＋软 Dice 的进步项和超调项（R_imp、R_over 的软版本，L3-24）；逐步权重取 Kendall 式可学的 σ。κ 与停止偏移：给 4 到 5 个候选，各向前滚动 2 轮，取 D5 最好的，蒸馏给 B 的控制头。
- 系数：权重学出，κ 由滚动展开的最优给出。
- 最快验证：与 B 同一次续训里加，另设“样本相同、只差进步损失”的对照。成本：训练前向约 ×2（估）；滚动展开标签约 9 小时（估，未测）。
- 预期【推测】：在 INDUCED 之上再 +0.3 到 +1.0。风险：Metz 2019 的梯度问题；Kendall 权重可能压低难步。

#### D 指代生长不设 K（替 PLAN 2-3 的固定 K）

- 对应痛点：P3，并去掉手定的 K。
- 做法：单调最弱一环扩散迭代到无变化即停，反传沿瓶颈指针（§2.3）；若改用 GRU 式传播，则加监督式停止头，标签＝路径上 T-Dice 最大的一步。训练时随机 K、每步都算损失，推理时 K 可大于训练 K。
- 系数：无 K，无 ponder cost。
- 最快验证：固定状态上比较 K 与 2K 的结果应相同（不动点性质）；报 30、60 mm 外修回和漏出。
- 预期：本身不提分，价值在不手定、能跨体素间距。

#### E 回路稳定度四件套（CPU，一天内，先于 A–C）

各类 hA、hR 的分布（不只中位数），以及两者在同一位置接连超过 1 的比例；NoDC 与 mDIoU；ADD→REMOVE→ADD 同位往返次数；按目标类型的 EIR、ECR。数据只用已回收的 VAL 轨迹和 TRAIN 回放。它决定 A–C 的预期有多大。

A 不动网络；B 只在主干输入端加零初始化通道，C 只在训练目标上加项；三者都能叠在 PLAN 第一到第三轮任何候选的 checkpoint 上，收益互相重叠，不能相加。对 PLAN 的具体建议：0-2 改成“规则版与手定版并排”，3-2 提前到第二轮，2-3 去掉固定 K。

### 4.2 别的领域已跨过、交互分割还没人跨过的思想，与查新记录

查新方法：用 Claude Code 自带的网页搜索，2026-10-03，每条查询看前 10 个结果；没查到只表示前 10 条里没有，不能证明没有。

| 思想 | 来自 | 查询和结果 |
|---|---|---|
| 用“下一笔落在刚加的区域里”当信赖域比值的无 GT 代理 | Gorelick 2013＋ILC | “trust region interactive image segmentation adaptive step … overshoot oscillation clicks”：只有 Gorelick 2013（非学习），没有学出增益的 |
| 模型自己上一轮的改动图作输入（efference copy） | 运动控制 | “interactive segmentation correction history of previous edits … undo …”：只见用户历史修正图（COVID 纵向 CT 工具，2110.00948）和系统级撤销，没有模型自己的改动 |
| 用预测的 Dice 控制编辑门槛 | Kalman 增益、本文 §2.1 | “per-case adaptive decision threshold from predicted Dice …”：只见质量预测（Robinson 2018、SegQC 2411.07601）和逐例路由（2609.20700、2509.04687） |
| 先验/测量可靠度之比决定增益 | Kalman 滤波 | “Kalman filter interactive segmentation user clicks as measurements …”：无 |
| 显式邻近项 ‖m−m_prev‖ | 邻近算子 | “… regularize toward previous mask minimal change proximal term …”：只有规则式保护（FocalClick 渐进合并、FCFI 局部修正）和 RITM 的上一轮掩膜输入 |
| MPC 式滚动展开给标量控制造标签 | MPC | “receding horizon OR model predictive control segmentation refinement …”等两条：无；PseudoClick 只预测下一点，是单步 |
| 展开迭代并学步长、门槛 | LISTA | “algorithm unrolling interactive segmentation learned step size threshold …”：无（只有 CRF-as-RNN 类展开均场） |

已有人做过、不能当新意写的：overshoot 概念和稳定性指标（TIA 2024）、超调惩罚（MedSAM-Agent 2026）、进步量奖励（IteR-MRL 2020、BS-IRIS 2021）、多步序列损失（CFR-ICL 2024）、学出的停止（Pace 2022）、基于改动量的停止（CFR-ICL 的 A-CFR，阈值手定）。另查过三条（learned stopping criterion … ；interactive segmentation reinforcement learning multi-round … ；performance degrades with additional clicks …），结果分别是 Pace 2022 与 A-CFR、IteR-MRL 等三篇、RITM 与 TIA。

### 4.3 判断没用或有害的方向

- ACT、PonderNet 原样搬：ponder cost τ 与先验 λ_p 是手定数，而我们有 GT 能直接监督停止点。
- 把“每轮必须不退步”写成硬约束：会退化成什么都不改。L3-30 里的自适应停止在 GPT-4o-mini 的 500 道题上第 0 步就停，且置信度提示本身掉 3.8 点。MedSAM-Agent 只罚峰值之后的下降，不禁止探索。
- 推理时的 MPC 规划：测试时没有 GT，也没有医生的模型。
- 给整个编辑网络做谱归一化（Ryu 2019）：损表达力，跨轮笔变化使收缩前提不成立；只在轮内重复调用或生长模块考虑。
- 把 TIA 的三支路原样搬：只在 2D 点击上验证；我们已有 H+、H− 历史通道（积分项）和当前掩膜（比例项），缺的只是差分项，即 B 的改动图。
- 在损失里直接加固定权重的 λ‖Δ‖：TRPO 的作者写明理论系数让步子太小、难选。

### 4.4 本路新读文献清单

题目见 §3 各条目标题行。“存”＝本路存入 Thesis；“他路存”＝另一路已存同内容文件，未重复保存。L3-01 Todorov 2002 存；L3-02 Todorov 2003 存（数学段未核）；L3-03 Parikh 2014 存；L3-04 Gorelick 2013 存；L3-05 Schulman 2015 存；L3-06 Schulman 2017 存；L3-07 Laroche 2019 存；L3-08 Gregor 2010 存；L3-09 Chen 2018 存；L3-10 Monga 2021 存；L3-11 Teed 2020 存；L3-12 Carreira 2016 存；L3-13 Ryu 2019 存；L3-14 Bai 2019 他路存；L3-15 Graves 2016 存；L3-16 Banino 2021 他路存；L3-17 Zhang 2019 存；L3-18 Jolicoeur-Martineau 2025 与 Wang 2025 存；L3-19 Pace 2022 存；L3-20 Liao 2020 存；L3-21 Ma 2021 存；L3-22 Sun 2024 他路存；L3-23 Wei 2024 未存（BMVC 论文集不在允许的来源清单）；L3-24 Liu 2026 存；L3-25 Kendall 2018 存；L3-26 Revach 2022 存；L3-27 Amos 2018 存；L3-28 Metz 2019 存；L3-29 Liao-McPherson 2022 存；L3-30 Liu 2026 存；L3-31 Wang-Lin 2026 与 Wu 2026 存。

本路新存 29 个文件（27 条正条目，加 HRM、CyberCorrect 两个附带），另有 3 条他路已存，1 条未存，共 31 条。只读摘要或引言、不计入精读：HRM、CyberCorrect、Metz、Figurnov、Winston、Veerabadran（部分）、Robinson。未取得全文：Scholz & Schöner 1999（Springer 付费墙）、Bristow 2006（IEEE 付费墙）、Conn–Gould–Toint 专著、Amann–Owens–Rogers 1996。
