# L8 调研：从纠正中学、纠正怎样帮倒忙，以及“练什么、练多少”怎样由模型当前的错误来定

2026-10-03 夜，Claude Code 子 agent（L8 路），只读调研，没连服务器，没改别的文件；只写了本文件，并把 34 篇公开 PDF 存进 `Thesis/sirb-research-20261003/`。

标注：[全文] 读了 PDF 正文；[网页] 读了 PMC 或期刊网页上的正文，PDF 没存；[摘要] 只读到摘要或别人的转述，不当证据用。VAL＝验证集，TEST＝锁定测试集，本文没碰 TEST。出现的 VAL 数字都引自 `A-internal-evidence.md`，只作方向演示，不用来选系数。“预期提分”是规划估计，不是实验结果，不能相加。借来的机制只是设计动机，不是证据。

## 0 结论

新读 44 篇：34 篇读了已存的 PDF（短文读全文，长文读相关章节），6 篇读了网页正文，4 篇只读到摘要或转述。教育学和运动学习没有给出新的网络结构，给出的是三条“别手定，让学习者当前的表现来定”的规则，正对着导演 10-03 晚的要求。

- 训练配额：40/30/30、近远 75/25、诱导 0.5 这一串比例，可以换成一条规则，每组按“自然频率 × exp(β × 缺口)”抽，缺口＝1 − 实际增益/理想增益。理想修复在任意状态上都能现算，所以不需要手定目标。医学分割里已有先例（Fidon 2021/2022，nnU-Net 上只换采样器，默认参数没调）；2026 年的 DRATS 在对比的五种采样规则里最差任务表现最好。
- 成对监督：教育学里“比较”起作用有三个条件：两例只差一个关键因素；学习者被迫一起比，光并排放不够；比完要接着讲原理。H1 文件量到 v1 的成对项梯度只有主损失的 1/500 到 1/800，这一项基本没起作用，很可能没做到第二条。设计见 1.2。
- 改过头：教育里反馈帮倒忙的机制是注意力上移，运动学习里是误差记错了来源、增益不跟着误差的一致性走。后者能直接变成规则：上一轮改过头（残差符号反转）就收，没改够（符号不变）就放，增益由网络从“上一轮改动足迹”算出，不靠 0.5/0.7/0.9 这类门槛。

最有希望的改法在第 3 节排序。运动学习几篇的机制是类比；误差灵敏度这一支在运动学习内部也有争议（PubMed 30271906 提了另一种解释，只见标题，未读）。

## 1 四个问题的回答

### 1.1 配额怎样由模型当前的错误自动定

做法对比：

| 做法 | 用什么信号 | 稳定性与效果证据 | 剩下的手定量 |
|---|---|---|---|
| Group DRO（对分组取最坏情形的优化，Sagawa 2020） | 每组当前损失，q←q·exp(η·损失) | 比“每步取最差组”稳，凸情形 O(1/√T) 收敛；最差组准确率比固定加权再高 3.4、5.6、12.9 点；训练损失到 0 时失效，要配强正则或早停 | η、小组修正量 |
| hardness weighted sampler（Fidon 2021/2022，nnU-Net） | 病例上次的损失（陈旧值），softmax(β·损失)（把分数变成概率），权重截断 | 只多一个 softmax；BraTS 增强肿瘤平均 Dice +1.0 到 +1.5 点；胎儿脑小脑 p10 +26.5 点，对照组平均差 <0.1 点 | β=100、截断 [0.1, 10]，没调 |
| DRATS（Corrado 2026） | 归一化缺口，KL 信任域（限制抽样分布偏离自然频率的幅度），q∝p0·exp(β·缺口) | 对比均匀、学习进展、学习潜力、先难后易、先易后难，最差任务最好；“学会就扔”会崩 | KL 预算 ε |
| DoReMi（Xie 2023） | 相对参考模型的超额损失 | 所有域困惑度都降；只用最难或只用最易没用 | η=1、平滑 1e-3 |
| RHO-LOSS（Mindermann 2022） | 训练损失 − 留出集不可约损失 | 步数少 18 倍、准确率高 2%；按损失选会选中噪声样本 | 每批选 10% |
| OHEM（Shrivastava 2016） | 当前损失最大的 B 个，NMS（去掉重叠框）去重 | 去掉 1:3 前景配额“无副作用”；VOC07 67.2→69.9 | B、NMS 阈值 |
| 重要性采样（Katharopoulos 2018） | 梯度范数上界，权重保持目标不变 | 同墙钟时间训练损失最多降一个数量级 | 方差下降阈值 |
| Exp3.S 老虎机（边试边选的在线选择算法）、师生课程（Graves 2017；Matiisen 2017） | 学习进展 | 均匀采样是“出奇强”的基线 | η、探索率 |

有效又稳定的做法有五个共同点：
- 软分配，不取最大。贪心选最高分的组，在 DUMP（大模型后训练里按优势大小调数据分布的方法）里更差（13、14 个角色的谜题，奖励 −0.91、−1.38，软采样 −0.66、−1.16）；DRATS 里“学会就换”的硬切换让已学会的任务崩掉。
- 信号对着“还能降多少”，不是“现在多大”。DoReMi、RHO-LOSS、DRATS 都以参考为基线，扣掉不可约的部分，避免追噪声；我们有现成的参考，就是同一状态上的理想修复。
- 锚在自然频率上。DRATS 用 KL 预算并加最小概率，Fidon 截断权重；等价做法是要求有效样本数不低于一半（惯例值）。
- 分数会过期，要刷新。PLR（按学习潜力重放训练场景的强化学习方法）里陈旧系数必须在 0 到 1 之间才有收益。
- 改配额等于改先验，要补回。用重要性权重，或把 logit（概率之前的原始分数）平移 log(自然频率/配额)，否则 0.5 门槛的含义就变了（H1 的 a09、a23 已指出）。

套到我们这里：
- 分组：符号（加/删）× 目标体积分位箱（按 TRAIN 回放的体积分布切，不用 0.5 mL、10 mL 这类看过结果才定的切点）× 块类型（含 T、含 O、只有 P）× 状态来源（生成器、诱导第几轮）；成对类型（1.2）也当一组。
- 缺口：在留出的 TRAIN 病例（约 10%，惯例值，只用来量缺口）的新状态上，一步编辑的实际 Dice 增益比理想修复的增益，g＝1−实际/理想。不能用训练批内的成绩，它会高估学会的程度（Bjork 的“提取强度≠存储强度”；RHO-LOSS 也用留出集）。
- 规则两种，各跑一次：甲＝自然频率 × 梯度大小（方差最小、目标不变，经典的分层抽样 Neyman 分配，Katharopoulos 的分组版，由 Cauchy–Schwarz 不等式推出）；乙＝DRATS 式缺口规则加 logit 平移。都不需要手定配额。
- 更新：每 N 步更新一次配额表，N 取“最稀少的组预计被抽到 30 次”所需的步数（惯例值），表里的值做指数滑动平均；数据顺序改成（种子、序号、配额表版本）的函数，配额表存进检查点，续训可复现。8k 步里只有 10 到 20 次更新，所以用直接公式，不用要很多轮才收敛的老虎机。
- 对应 H1 的手定量：a12（40/30/30）、a13（预算 4096）、a15（难样本 0.5）、a16（状态对 60/25/15）、a17（诱导 0.5）、a18（笔划来源）。“诱导 0.5”变成“状态来源”这一维上的自动配额：生成器状态缺口小，自动淡出，这就是自适应撤脚手架（教育里的 fading；Salden 2010 报告自适应撤除优于固定撤除，只见检索摘要），不用另写日程。

方向演示（VAL，flat，数据来自 A 文件表 3，不是选择依据）：

| 组 | 轮次占比 | 缺口 1−实际/理想 | 占总缺口 | 现行训练曝光 |
|---|---|---|---|---|
| 加笔 <0.5 mL | 12.3% | 0.88 | 6.0% | 未核实 |
| 加笔 0.5–10 mL | 28.2% | 0.51 | 27.8% | 未核实 |
| 加笔 ≥10 mL | 20.5% | 0.74 | 23.5% | 7.8% |
| 删笔 <0.5 mL | 8.3% | 1.80（实际为负） | 8.2% | 未核实 |
| 删笔 0.5–10 mL | 20.4% | 0.91 | 27.1% | 未核实 |
| 删笔 ≥10 mL | 10.3% | 0.90 | 7.5% | 未核实 |

“占总缺口”＝轮次占比 ×（理想增益−实际增益）的归一化。加笔 ≥10 mL 约占 23.5%，训练里只抽 7.8%，与事实单“少练约 2.5 倍”一致。缺口本身差别不大，拉开差距的是“占比 × 缺口”，所以基线要用自然频率，不能用均匀底。

最快验证（只用 TRAIN/VAL）：先在 CPU 上用已有的 407/407 回放量各组自然频率和缺口，与现行曝光并排；若规则给的配额与现行配额每组之比都在 1.3 倍以内，就不值得跑。否则在 3090 上做两次 8k 续训（甲、乙），对照现成的 N1_STATE_STATIC；看最大组缺口、≥10 mL 加笔修回、删笔新错体积。单 seed，1 到 2 点的差可能是波动，判据要先写好。风险：分位箱只减少人为，组仍由我们定义；以缺口为目标会拉低平均（Group DRO 的老问题），而 D5 是病例平均，所以要用 KL 或有效样本数锚住；3 mm 网格往返丢掉的小目标连理想修复也做不到，以理想修复为参考就自动扣掉。

### 1.2 成对比较起作用的条件，以及成对监督怎么设计

教育里的证据（L8-06 到 L8-08）：
- 两例只差一个关键因素：Chen 与 Klahr 的变量控制训练在高度相似的情境里并排对比，7 个月后仍保持（经 Gentner 2003 转述）；Schwartz 与 Bransford 提醒，学习者经验少时要用更干净的对比；机器教学里，夹住边界的最近一对就是最小教学集（L8-25、L8-26）。
- 必须被迫一起比：比较两例 48%，分开学 19%（N=128）；实验 3 里引导 90%、只被要求比较 70%、分开学 55%、不学 37%；两例紧挨着放，学习者也不会自发去比（Gentner 2003）。
- 比完要讲：分析对比案例再听讲 43.8%，分析两遍 16.7%，总结后再听讲 14.6%，联合远大于两个对照之和（Schwartz 与 Bransford 1998）。
- 收益只落在被比的那条关系上（Gentner）。Alfieri 2013 元分析 d=0.50，[摘要]。

对我们的成对监督（设计推断，不是论文做过的）：
- 配对分四类，各自只差一个因素：换笔（同状态、两笔指两处同号错，目标互换）；换画法（同目标、范围不变）；换状态（同一笔、状态差一座桥，目标跟着变）；近邻到远对（第二笔离第一笔由近到远，对应逐步对齐）。
- 损失用“差异匹配”：只在两个目标不一致的体素上，要求两张 pT 之差的符号和大小对上；在两个目标一致的体素上，要求输出相等。这是“并排比较”的数学化，取代现在间隔 0.2、η 0.1 的状态约束。
- 配对项和主监督放进同一批样本一起训（“比较加讲”）；权重由实测的梯度范数自动均衡到与主损失同量级，不再用固定 0.25。
- 各类配对和距离箱的占比由缺口定（1.1）。断桥类断开后方向正确率只有 0.084，训练里只占 10.2%（H1 a16）。
- 对照：相同样本、没有成对关系（PLAN 3-1 已有）。风险：四类配对若都由 centerline 画法生成，会学到捷径；Gentner 的“原则特定性”说明没配到的关系不会涨。

### 1.3 反馈帮倒忙的条件，对应“改过头”的机制和防法

| 帮倒忙的条件（出处） | 我们这里的对应 | 防法与系数来源 |
|---|---|---|
| 注意力从任务上移到自我层，效果随之下降；表扬、威胁自尊降低效果（Kluger 与 DeNisi，经 Shute 转述） | 一笔被读成“这一类都错”而不是“这一处错”：10-01 实测顺手修所有同向错误，误改是多修的 2 到 19 倍 | 保持 T/O/P 三层标签，加同号同外观的难 O 和换笔成对（1.2）；不用系数 |
| 复杂任务上反馈效果更弱（同上） | 多处错误、大目标：≥10 mL 加笔修回比例 0.167（体积加权，VAL） | 先限定到笔碰到的对象再处理；不用系数 |
| 提示总以答案收尾，学习者滥用，形成依赖；频繁反馈让人忽视自身固有反馈（Shute 准则 16；引导假说，经 Wulf 2010 转述） | P6：换选笔习惯，D5 掉 0.09 到 0.10（TEST，描述） | 训练笔混入非最大错、局部笔、空笔，宽度随回放失败率自适应（H1 a18） |
| 频繁反馈引起“适应不良的短期纠正”，追着每次误差的噪声走（Wulf 2010 转述） | P1：90.6% 的加笔带出新假阳性（VAL） | 增益由符号一致性控制（Herzfeld 2014）；大改动按相关概率压低（Wei 与 Körding 2009）；系数由网络输出 |
| 误差记在错的来源上，泛化就错（Wolpert 2011；Berniker 与 Körding 2008） | 后几轮约 29% 的笔符合“落在模型自己上一轮新错上”的启发式条件（没做空间核对）；第 2 轮缺口 58% 是新错（VAL） | 输入上一轮改动足迹；训练里造“自己造的错”和“原来的错”两类；前者限制在足迹内撤销 |
| 纠正的形式决定吸收与修好（Lyster 与 Ranta 1997） | 笔只给位置，相当于提示类；可分三态：没动、动了没修对、动过头 | 诊断用，不加系数；没动对应 e<0.5 挡住 |
| 信息量：纠正性 d=0.46，高信息量 d=0.99（Wisniewski 2020） | 笔是纠正性；缺过程层信息 | 加“上一轮自己改了哪里、当时认定指哪块”（F 的 B） |

“改过头”可拆成三件事：增益太大、范围边界估不准、归因错。运动学习给了三件对应的工具：误差灵敏度随一致性调（Herzfeld）、泛化函数从逐试次数据里估计而不是假定（Donchin 2003；Thoroughman 与 Shadmehr 2000）、按来源归因（Berniker 与 Körding）。我们的泛化核两头都不对：近处太宽（中等加笔目标每修回 1 mL 带出约 0.75 mL 新假阳性），远处窄到 0（60 mm 外修回 0 和 0.084）。

### 1.4 查新：交互分割里有没有人用过这些

在通用网页检索（含 arXiv）里查了 8 组关键词，归并成下列 6 条，2026-10-03；没有直接用 Google Scholar、PubMed、Semantic Scholar，所以“未检索到”不等于首创。

1. “interactive segmentation training curriculum hard example mining adaptive click sampling model errors 3D medical”与“…curriculum learning user interaction simulation…”：只见按模型错误放点的在线模拟（2510.03189、ENSAM、ScribblePrompt、AGILE3D）、autoPET V 三阶段课程（2608.22096，已在 D、G 文件）和非交互的块尺寸课程（Fischer 2025，手定日程）。
2. “interactive segmentation distributionally robust / group DRO / bandit / prioritized replay / learning progress…”：没有交互分割的结果，只有 RL 和 LLM（DUMP、DRATS）。
3. “interactive segmentation hard click / difficulty-aware sampling…”：只见按最大错误区放点和难度加权的损失（AdaptiveClick）；没有按过去失败重抽样的。
4. “medical image segmentation group DRO lesion size…”：非交互的 DRO，nnU-Net-DRO（L8-32、L8-33）；DuetFair（2605.10521）与 KL 正则化 Group DRO 做 CT 分类（2603.15941）只见检索摘要。
5. “interactive segmentation paired same image different prompts targets swap contrastive…”：PVPUFormer 的提示—像素对比损失、Critic Feedback Signals（2510.09945，修正当反事实信号，只读摘要）、CPC-SAM；没有“同状态换笔、目标互换”的配对。
6. “interactive segmentation over-correction … learned threshold”与“… error sensitivity / sign flip / previous round edit reversal …”：TIA（BMVC 2024，受 PID 控制启发，整合过去几轮和掩膜变化，读了摘要和引言）、RITM 的上一轮掩膜、Kontogianni 2020、三维肿瘤“可修订提示”（Springer 2026，只见检索摘要）；没有用符号一致性调增益、也没有区分“自己造的错/原有的错”的。

结论：缺口驱动的采样在非交互医学分割里已有（Fidon），交互分割里未见；差异匹配的成对监督、误差灵敏度记忆、自己改动与原有错误的归因，本次未检索到。

## 2 文献记录

### A 教育学：反馈

### [L8-01] Kluger 与 DeNisi 1996《The effects of feedback interventions on performance》Psychological Bulletin 119(2)
- 链接：https://doi.org/10.1037/0033-2909.119.2.254；PDF：未存（付费墙）。领域：工业与组织心理，反馈元分析。[摘要]（Hebrew University 记录页的摘要，加 Shute 对调节变量的转述；131 篇论文、38% 效应为负这两个数取自第三方镜像网页的检索片段）
- 说的是什么：607 个效应量、23,663 次观察，平均效应量 d＝0.41，但超过三分之一的反馈让表现变差，抽样误差、反馈正负号和已有理论都解释不了。反馈干预理论（FIT）：反馈把注意力在三层间移动，任务学习、任务动机、元任务（含自我）；越往自我层、离任务越远，效果越差。Shute 转述的调节变量：泄气的反馈降效果，给正确答案的升效果；排除有偏研究后，表扬和威胁自尊的降效果，复杂任务上效果更弱。
- 痛点与搬法：P1、P6。设计量取的是“这一笔被模型读到哪一层”，不看“反馈多不多”。落在这一处错误对象上是任务层；被读成“这一类外观都错”是上移。对应做法是同号同外观的难 O 加换笔成对比较（1.2）。
- 系数：全是定性调节变量，没有可搬的数。
- 证据与风险：样本大，但多是心理实验，离我们很远；“层级”是理论解释，不是可测机制。交互分割里没人把反馈层级当设计量（1.4）。

### [L8-02] Shute 2008《Focus on formative feedback》Review of Educational Research 78(1)
- 链接：https://journals.sagepub.com/doi/10.3102/0034654307313795；作者页 ETS 报告版 https://myweb.fsu.edu/vshute/pdf/shute%202007_f.pdf；PDF：已存 `shute-2008-formative-feedback.pdf`（ETS RR-07-11 版）。领域：教育测量，综述。[全文]
- 说的是什么：二十多条准则。和我们有关的：反馈对着任务不对着学习者；解释性反馈优于只说对错，但要分小块；别用总以正确答案收尾的渐进提示（会被滥用，改用提示和线索）；少做耗时的错误诊断（代价高、不总准）；难任务用即时反馈，简单任务可延迟；新手要即时显式的支持，高水平者延迟更好。
- 痛点与搬法：P6、P5。“提示总以答案收尾会被滥用”对应训练笔总画在最大的错上；新手与高水平者的差别，对应前期多用生成器状态、后期多用诱导状态，由缺口决定（1.1）。
- 系数：无。
- 证据与风险：综述，没有定量；结论多来自人类课堂。

### [L8-03] Hattie 与 Timperley 2007《The power of feedback》Review of Educational Research 77(1)
- 链接：https://doi.org/10.3102/003465430298487；PDF：未存（付费墙）。[摘要]（摘要，加 Wisniewski 2020 的转述）
- 说的是什么：反馈回答三个问题（去哪、进展如何、下一步），分四层（任务、过程、自我调节、自我）。类型和给法决定它帮忙还是帮倒忙；纠正性反馈对学新技能很有效；反馈要对准合适的问题和层次，否则容易被忽略或误解。元综合平均效应 0.79。
- 痛点与搬法：P1、P4。笔是任务层的纠正性反馈，只回答“哪里错”；P4 缺的是“下一步”，即上一轮自己改了什么。
- 系数：无。
- 证据与风险：元综合把各元分析等权相加，Wisniewski 指出会高估（L8-04）。

### [L8-04] Wisniewski、Zierer 与 Hattie 2020《The power of feedback revisited》Frontiers in Psychology 10:3087
- 链接：https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.03087/full；PDF：已存 `wisniewski-2020-power-of-feedback-revisited.pdf`。领域：元分析。[全文]
- 说的是什么：435 项研究、994 个效应量、6.1 万以上受试者，总体 d＝0.48，异质性很大，17% 的效应为负（Kluger 与 DeNisi 是 38%）。按信息量分：奖惩 d＝0.24（k＝39），纠正性 d＝0.46（k＝238），高信息量（纠正加过程与自我调节信息）d＝0.99（k＝42）。认知和运动技能的效果高于动机和行为；与 H&T 的 0.79 的差别主要来自方法。
- 痛点与搬法：P4。笔在“纠正性”这一档；信息量差一倍，对应加过程层信息：上一轮自己改了哪里、当时认定指哪块（F 的 B）。
- 系数：无。
- 证据与风险：高信息量组只有 42 个效应量；人的“过程信息”是策略提示，网络里只能是输入通道，类比要打折。

### [L8-05] Lyster 与 Ranta 1997《Corrective feedback and learner uptake》Studies in Second Language Acquisition 19(1)
- 链接：https://doi.org/10.1017/S0272263197001034；PDF：未存（付费墙）。领域：二语习得。[摘要]（Cambridge 摘要，加第三方网页摘录，数字未对照排版原文）
- 说的是什么：4 个沉浸式小学课堂、18.3 小时转录。六种纠正占比：重述 55%、引出 14%、澄清请求 11%、元语言提示 8%、明确纠正 7%、重复错误 5%。学生有回应（uptake）的比例：重述只有 31%，明确纠正 50%，澄清请求 88%、元语言提示 86%、重复 78%。学生自己修好（repair）的比例：引出、元语言提示约 45% 到 46%，重复 31%，澄清请求 27% 到 28%；重述与明确纠正已给出正确形式，不产生学生自己的修正。
- 痛点与搬法：笔只给位置不给答案，相当于提示类，设计上应有较高吸收。每一笔可分三态来诊断：没动（e<0.5 挡住；10-01 诊断里 N3 有 79/1263、flat 有 12/1262 次完全没改）、动了没修对、动过头。
- 系数：无，是诊断框架。
- 证据与风险：二语课堂，4 个班；文中两处百分比略有出入。

### B 教育学：对比、失败、困难

### [L8-06] Schwartz 与 Bransford 1998《A time for telling》Cognition and Instruction 16(4)
- 链接：https://aaalab.stanford.edu/papers/time_for_telling.pdf；PDF：已存 `schwartz-1998-time-for-telling.pdf`。领域：学习科学。[全文]
- 说的是什么：三项课堂实验，大学生先分析对比案例（简化的心理学实验与数据），再听讲座或读文，约一周后预测一个新实验的结果。实验 3：分析案例加讲座做出 43.8% 的可能预测，分析两遍无讲座 16.7%，总结文本加讲座 14.6%，后两者之和仍远低于联合组（作者称协同）。分析案例带来分辨力，讲座带来解释框架，缺一不可。设计提示：对比要对齐学习目标；经验少的学习者用更干净的对比。
- 痛点与搬法：P7。成对比较项只教“看出差异”，必须和 T/O/P 主监督放在同一批样本里一起训。
- 系数：无。
- 证据与风险：被试是大学生，任务是概念预测；“先比后讲”与梯度同时更新的对应是类比。

### [L8-07] Gentner、Loewenstein 与 Thompson 2003《Learning and transfer: A general role for analogical encoding》Journal of Educational Psychology 95(2)
- 链接：https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewensteinThompson03.pdf；PDF：已存 `gentner-2003-analogical-encoding.pdf`。领域：认知心理，类比。[全文]
- 说的是什么：类比编码（analogical encoding）＝并排比较两个例子，抽出共同结构。新手学谈判策略，三个实验。实验 1：引导类比组 15/32（47%）把原则用到新案例，基线 6%。实验 2：比较两例 48%，分开学 19%（N＝128，χ²＝11.85）。实验 3（真实对谈）：引导 90%，只被要求比较 70%，分开学 55%，不学 37%。收益只落在被教的那条原则上；学习者不会自发做比较，即使两例紧挨着；比较投入越多，迁移越好。
- 痛点与搬法：P7。让模型被迫比较：损失直接作用在两个输出的差上，不是两个独立样本并排；配对要覆盖想教的每种关系。
- 系数：无。
- 证据与风险：人类实验，样本小；网络里怎样“被迫比较”是我们的设计，没验证过。

### [L8-08] Alfieri、Nokes-Malach 与 Schunn 2013《Learning through case comparisons》Educational Psychologist 48(2)
- 链接：https://doi.org/10.1080/00461520.2013.775712；PDF：未存（作者页链接已失效）。领域：教育心理，元分析。[摘要]
- 说的是什么：57 个实验、336 个检验，案例比较优于其他案例学习、传统教学和对照，d＝0.50，区间 [0.44, 0.56]；四个调节变量可靠：比较的目的、是否给出原理、内容、比较与测试的间隔。“同时呈现优于顺序呈现”之类是第三方转述，未核原文。
- 痛点与搬法：P7；与 L8-06、L8-07 互相印证“比较加讲”。
- 系数：无。证据与风险：只有摘要。

### [L8-09] Kapur 2008《Productive failure》Cognition and Instruction 26(3)
- 链接：https://doi.org/10.1080/07370000802212669；PDF：未存（付费墙；正文经 KU Leuven 课程页的公开副本以网页读到，未保存）。领域：学习科学。[网页]
- 说的是什么：309 名十一年级学生、103 个三人组、7 所学校。先在无支撑下解决劣构问题的组，当时解题质量差，随后个人测验的近迁移和远迁移都高于先做良构题的组。依据：延迟给结构（卡壳驱动学习）和 Marton 的可辨别性：被注意和被迁移的是差异，不是相同。
- 痛点与搬法：P5。“先让学习者在自己的状态上失败，再给标准答案”就是 DAgger 的教育版，已在做（诱导状态），没有新机制。
- 系数：无。证据与风险：小组合作解题，对网络只是类比。

### [L8-10] Bjork 与 Bjork 2011《Making things hard on yourself, but in a good way》Psychology and the Real World 章节
- 链接：https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/04/EBjork_RBjork_2011.pdf；PDF：已存 `bjork-2011-desirable-difficulties.pdf`。领域：记忆与学习。[全文]
- 说的是什么：训练时的表现反映“提取强度”，学得牢不牢取决于“存储强度”，让表现升得最快的条件往往学得最浅。合意困难包括变化练习、交错、间隔、用测试代替展示；前提是学习者有能力克服，否则成了不合意困难。例：儿童投豆袋，一半只在固定距离练，一半在多个距离练，最后都在固定距离测，多距离组反而更好。
- 痛点与搬法：P5、P8。F 已判间隔和交错为装饰，我同意。新增两点：训练批内的成绩不能当进度信号（生成器状态修回 89.8%，真实 15% 到 25%），缺口要在留出病例的新状态上量；“合意”的边界是可学，缺口里要扣掉理想修复本身也做不到的部分。
- 系数：无。证据与风险：综述，没有网络实验。

### C 运动学习

### [L8-11 / L8-12] Wolpert、Diedrichsen 与 Flanagan 2011《Principles of sensorimotor learning》Nature Reviews Neuroscience 12；Shadmehr、Smith 与 Krakauer 2010《Error correction, sensory prediction, and adaptation in motor control》Annual Review of Neuroscience 33
- 链接：https://doi.org/10.1038/nrn3112；https://doi.org/10.1146/annurev-neuro-060909-153135；PDF：已存 `wolpert-2011-sensorimotor-learning.pdf`、`shadmehr-2010-error-correction-adaptation.pdf`。领域：运动控制综述。[全文]
- 说的是什么：基于误差的学习用有符号的感觉预测误差，不只说没中，还说怎么偏的；误差对每个指令分量的梯度只能带噪估计，同一个误差可以引出差别很大的调整；它能把平均误差压到零，进一步降方差要靠强化学习（Wolpert）。泛化函数描述“一个方向上的误差怎样影响别的方向”，实测多为较窄的类高斯函数。信用分配分情境和时间两种：同一个误差该记在身体还是环境上，由先验和“哪个来源与扰动最一致”决定。Shadmehr：前向模型靠感觉预测误差保持校准；预测与观测按各自不确定度加权（卡尔曼滤波：按可靠度融合两路信息）；运动纠正本身可当下一次的教学信号。
- 痛点与搬法：P1、P4。“修多少”应按不确定度加权，不是固定 0.5；“这一笔该记在原来的错上，还是模型上一轮自己造的错上”是信用分配问题（P4 的约 29%）；泛化核应窄且随尺度变。
- 系数：卡尔曼增益由两路不确定度之比推出，没有手定。
- 证据与风险：综述，没有可直接用的网络实验；类比层级高。

### [L8-13 / L8-14] Herzfeld、Vaswani、Marko 与 Shadmehr 2014《A memory of errors in sensorimotor learning》Science 345；Albert 等 2021《An implicit memory of errors limits human sensorimotor adaptation》Nature Human Behaviour 5
- 链接：https://herzfeldlab.neuro.wisc.edu/publications/herzfeld_science_2014.pdf；PMC11910176；PDF：Herzfeld 已存 `herzfeld-2014-memory-of-errors.pdf` [全文]；Albert 未存（PMC 的 PDF 被验证页挡住，没有绕过），读网页正文 [网页]。
- 说的是什么：误差灵敏度（从误差里取多少）不是常数，由过去误差的历史控制。三组各 9 人在慢、中、快切换的力场里伸手：慢切换（误差同号持续）组灵敏度升高，快切换组降低，探测试次里的误差大小两组相同；变化主要出现在小误差上（实验 2，每组 10 人）。模型是同号则在该误差附近升高灵敏度、异号则降低，作者指出形式上类似调学习率的 RPROP。Albert 2021：隐性系统在误差同向持续时更敏感；扰动方差高时残差变大，原因是灵敏度改变，不是遗忘。
- 痛点与搬法：P1、P4。把“上一轮改了之后，这一轮残差的符号是否反转”当增益信号：反转＝改过头，该收；不变＝没改够，该放。做法见 3.1 第 2 条；评测加符号反转率、同号持续率；D1 不应变。
- 系数：原文的基元宽度和更新率由数据拟合。搬过来增益是网络输出，随机化范围取自回放里实测的“编辑体积/目标体积”分布；若用显式规则，RPROP 的 1.2/0.5 是通用默认值。
- 证据与风险：每组 9 到 10 人，任务是力场伸手；在运动学习内也有争议（PubMed 30271906，只见标题）。交互分割里未见（1.4）。

### [L8-15 / L8-16] Wei 与 Körding 2009《Relevance of error》Journal of Neurophysiology 101；Berniker 与 Körding 2008《Estimating the sources of motor errors》Nature Neuroscience 11
- 链接：PMC2657056、PMC2707921；PDF：未存（PMC 的 PDF 被验证页挡住，没有绕过），读网页正文。领域：运动学习的贝叶斯模型。[网页]
- 说的是什么：Wei：神经系统要估计“这个误差与自己的动作有关的概率”，只对相关的误差强适应。7 名受试者、900 次伸手，视觉反馈被随机扰动 0、±1、±2、±4、±8 cm；±2 cm 内影响近线性（相邻试次斜率 −0.049±0.006），全范围斜率 −0.030±0.005，大扰动下次线性；相关性估计模型解释 90.8±1.5% 的方差，线性模型 68.7±4.9%。Berniker：把误差归因于“身体”还是“世界”是贝叶斯推断（扩展卡尔曼滤波），归因决定泛化到哪里；模型只留一个自由参数 α（世界与身体不确定度之比），取 0.4。
- 痛点与搬法：P1、P4。大改动不应线性放大，应乘“与模型自身动作相关的概率”；归因决定该撤销上一轮的改动，还是在原错误上补。做法见 3.1 第 2 条；相关概率的真标签：笔落在自己造的错上＝相关。
- 系数：Wei 的 6 个参数由数据拟合；Berniker 的 α＝0.4 手定，搬过来改成网络自己学。
- 证据与风险：7 人；类比。

### [L8-17 / L8-18] Donchin、Francis 与 Shadmehr 2003《Quantifying generalization from trial-by-trial behavior》Journal of Neuroscience 23；Thoroughman 与 Shadmehr 2000《Learning of action through adaptive combination of motor primitives》Nature 407
- 链接：PMC6740843、PMC2556237；PDF：未存（PMC 的 PDF 被验证页挡住，没有绕过），读网页正文。领域：运动学习的泛化。[网页]
- 说的是什么：Thoroughman：前一次误差对后一次输出的影响＝两次输入的基元相似度 × 误差，所以“一个误差影响多远”由基元的调谐宽度决定，可从逐试次误差序列反推，得到宽调谐的类高斯函数。Donchin：用逐试次数据估计泛化函数；误差的度量本身（期望轨迹是否随适应变化）决定估出的形状，允许期望轨迹变化时，泛化函数多解释约两倍方差。
- 痛点与搬法：P1、P3。“一笔影响多远”是学习者的性质，可以从它自己逐轮的行为里估出来。做法是诊断，不是训练项：在 TRAIN 回放上拟合“笔到体素的距离、目标尺度 → 被修改的概率”这个泛化核，与理想核（连通错误块）并排，差别就是越界与漏修的来源。
- 系数：数据拟合。证据与风险：伸手任务，类比。

### [L8-19 / L8-20] Smith、Ghazizadeh 与 Shadmehr 2006《Interacting adaptive processes with different timescales》PLoS Biology 4；Wulf、Chiviacowsky、Schiller 与 Ávila 2010《Frequent external-focus feedback enhances motor learning》Frontiers in Psychology 1:190
- 链接：https://doi.org/10.1371/journal.pbio.0040179；https://doi.org/10.3389/fpsyg.2010.00190；PDF：均已存（`smith-2006-two-timescale-motor-learning.pdf`、`wulf-2010-external-focus-feedback.pdf`，开放获取）。[全文]
- 说的是什么：Smith：两个过程吃同一个误差，快的学得猛、忘得快，慢的学得弱、留得久。Wulf：48 名 10 至 12 岁儿童练足球界外球，反馈聚焦（内部/外部）× 频率（每次 100%/每三次 33%）；每次都给的外部聚焦反馈学得最好。引导假说认为频繁反馈让学习者依赖反馈、忽视自身固有反馈，并造成“适应不良的短期纠正”；依赖是否出现，取决于反馈把注意力放在哪。
- 痛点与搬法：Smith 无新机制，只支持“上一轮改动”要保留一段时间。Wulf 对应 P6、P1：我们的笔指向效果（外部聚焦），问题更可能来自规律性太强，不是频率；对策是训练笔的多样性（1.3 第三行）。
- 系数：Smith 的参数由数据拟合；Wulf 无。证据与风险：单一动作任务；儿童。

### D 课程、自定步调、机器教学

### [L8-21 / L8-22 / L8-23 / L8-24] Bengio 等 2009《Curriculum learning》ICML；Kumar、Packer 与 Koller 2010《Self-paced learning for latent variable models》NeurIPS；Jiang 等 2014《Self-paced learning with diversity》NeurIPS；Soviany 等 2022《Curriculum learning: A survey》IJCV
- 链接：https://ronan.collobert.com/pub/matos/2009_curriculum_icml.pdf；arXiv 2101.10382；PDF：均已存（`bengio-2009-curriculum-learning.pdf`、`kumar-2010-self-paced-learning.pdf`、`jiang-2014-self-paced-learning-diversity.pdf`、`soviany-2022-curriculum-learning-survey.pdf`）。[全文]
- 说的是什么：Bengio 把课程定义为一串训练分布，熵递增、支持集递增（先易后全）；容易的好处，一是噪声少，二是类似延拓法。Kumar 让学习者自己定“容易”：v_i＝1[损失 < 1/K]，K 以 μ＝1.3 退火。Jiang 加多样性：每组内按损失排名 i，损失 < λ + γ/(√i+√(i−1)) 才选。Soviany 综述提醒课程可能损害多样性而变差。
- 痛点与搬法：P5、P8。方向与“多练困难”相反（易先），只适合当预热；我们的难点是曝光缺口，不是局部极小。可借的是 SPLD 的“按组内排名取”，避免只从一两个组里挑。
- 系数：K0、μ、λ、γ 都是手定。证据与风险：与 OHEM 同样依赖损失，却取相反的一端；噪声多时易先更稳。

### [L8-25 / L8-26 / L8-27] Zhu 2015《Machine teaching: An inverse problem to machine learning》AAAI；Zhu、Singla、Zilles 与 Rafferty 2018《An overview of machine teaching》arXiv；Liu 等 2017《Iterative machine teaching》ICML
- 链接：https://ojs.aaai.org/index.php/AAAI/article/view/9761；arXiv 1801.05927、1705.10470；PDF：均已存（`zhu-2015-machine-teaching.pdf`、`zhu-2018-machine-teaching-overview.pdf`、`liu-2017-iterative-machine-teaching.pdf`）。[全文]
- 说的是什么：机器教学是机器学习的逆问题：教师知道目标模型和学习器的算法，求最优训练集。一维阈值分类器：被动学习要 O(1/ε) 个样本，主动学习 O(log 1/ε)，教学只要 2 个，一正一负、相距不超过 ε 并夹住阈值。迭代教学（Liu 2017）：教师按学习器当前状态逐个喂样本，在一定条件下可证明不慢于随机教师；选样本看“相对学习器当前参数的难度低、与离目标差距相关的有用性高”，学习率大时偏简单，接近最优时偏困难，课程自动出现。
- 痛点与搬法：P7。夹住边界的最近一对就是最小教学集，对应成对里（T 的边缘体素，紧挨着的真病灶体素）这类近邻对，不是随机远对。迭代教学说明样本选择要以“学习器当前状态与目标的差距”为准，与“配额由当前错误定”同构；“有用性”需要目标模型，我们只能用理想修复代替，这正是 DRATS 的参考。
- 系数：难度和有用性无手定系数，但依赖目标模型或其代理。证据与风险：理论针对线性或凸学习器，深度网络上只有启发意义。

### E 配额由当前错误决定

### [L8-28] Shrivastava、Gupta 与 Girshick 2016《Training region-based object detectors with online hard example mining》CVPR
- 链接：arXiv 1604.03540；PDF：已存 `shrivastava-2016-ohem.pdf`。领域：目标检测。[全文]
- 说的是什么：Fast R-CNN 用手定规则，前景:背景＝1:3（前景占 25%）；去掉或加大这个比例，mAP 降 3 点。OHEM 对一张图的全部候选框前向，按当前损失排序，取最难的 B 个，用 NMS（非极大值抑制，阈值 0.7）去掉高度重叠、损失相关的框；原文说“某一类被忽视，它的损失会升到被抽到的概率很高”，所以不需要前景背景比例。VOC07 mAP：VGGM 59.6→62.0，VGG16 67.2→69.9；比用全部候选框还高 1 点以上；每步多 0.09 到 0.43 秒。
- 痛点与搬法：这是 40/30/30 手定配额的最直接前例，用损失取代类别比例（P5）。做法见 3.1 第 4 条：候选块上前向一遍，取 pT 错误质量最大的 B 个，块间做“NMS”，保留均匀底。
- 系数：B/N 与 NMS 阈值手定；B/N 可改为“有效样本数下限”。证据与风险：会追噪声标签（RHO-LOSS 实测）；3 mm 网格往返丢失的小目标就是我们的噪声源。

### [L8-29] Katharopoulos 与 Fleuret 2018《Not all samples are created equal》ICML
- 链接：arXiv 1803.00942；PDF：已存 `katharopoulos-2018-importance-sampling.pdf`。领域：优化。[全文]
- 说的是什么：最优采样分布正比于每个样本的梯度范数；推导出只需一次前向的梯度范数上界（对最后一层预激活的梯度范数，闭式）；给出方差下降量的估计，降得够多（阈值 1.5 到 2）才打开重要性采样；采样后用权重 1/(B·g_i) 保持无偏。同墙钟时间训练损失最多降一个数量级，测试误差相对降 5% 到 17%；在 CIFAR100 上只有它相对按损失采样有收益。
- 痛点与搬法：配额的“目标保持不变”版本。块级评分用 logit 梯度范数（|p−y| 的范数），前向里免费得到；分组版见 1.1 的甲规则。
- 系数：无手定量，阈值由时间模型推出。证据与风险：只提速，不改目标，对“曝光不足造成的先验偏差”没有直接作用。

### [L8-30] Mindermann 等 2022《Prioritized training on points that are learnable, worth learning, and not yet learnt》ICML
- 链接：arXiv 2206.07137；PDF：已存 `mindermann-2022-rho-loss.pdf`。领域：数据选择。[全文]
- 说的是什么：选“可学、值得学、还没学会”的点：分数＝训练损失 − 在留出集上训练的小模型给出的不可约损失；每批 320 里选 32。Clothing-1M：步数少 18 倍、最终准确率高 2%；加 10% 标签噪声时对手变差、它的加速反而更大；不可约损失模型可小 21 倍，也可把训练集二分得到而不需额外留出数据。
- 痛点与搬法：3 mm 网格往返丢小目标，理想标签往返后目标 Dice 只有 0.47（<0.1 mL），这类块损失高但不可约。参考可用理想修复的结果（免训练），或 TRAIN 内交叉拟合的小模型。
- 系数：每批选 10% 手定，可改按有效样本数定。证据与风险：要多训或多跑一个参考模型。

### [L8-31] Sagawa、Koh、Hashimoto 与 Liang 2020《Distributionally robust neural networks for group shifts》ICLR
- 链接：arXiv 1911.08731；PDF：已存 `sagawa-2020-group-dro.pdf`。领域：鲁棒优化。[全文]
- 说的是什么：对预先定义的组，最小化最坏组的损失。对模型做 SGD，对组权重 q 做指数梯度上升（q_g←q_g·exp(η·损失)，再归一化）；比 Oren 2019“每步取最差组”稳，凸情形 O(1/√T) 收敛。过参数化网络能把训练损失降到 0，此时最坏组训练损失也是 0，朴素 Group DRO 与普通训练没差别；配强 L2 正则或早停，最差组准确率提高 10 到 40 个百分点。表 3 最差组准确率（三个数据集）：普通训练 63.7/47.8/66.4，固定上调权重 88.0/83.3/64.8，Group DRO 91.4/88.9/77.7。
- 痛点与搬法：1.1 的组权重更新；“自适应权重优于固定权重”的直接证据，固定权重就是我们现在的手定配额。
- 系数：η 与小组修正量需要设定；组由人定义。证据与风险：以最差组为目标会拉低平均；D5 是平均指标，要加锚（DRATS 的 KL 预算）。

### [L8-32 / L8-33] Fidon 等 2022《Distributionally robust deep learning using hardness weighted sampling》Journal of Machine Learning for Biomedical Imaging；Fidon 等 2021《Distributionally robust segmentation of abnormal fetal brain 3D MRI》PIPPI 研讨会
- 链接：arXiv 2001.02658、2108.04175；PDF：已存 `fidon-2022-hardness-weighted-sampling.pdf`、`fidon-2021-distributionally-robust-fetal-brain.pdf`。领域：医学分割。[全文]
- 说的是什么：hardness weighted sampling＝按每个病例上次的损失（陈旧值，用到才更新）做 softmax(β·损失) 抽样，重要性权重截断到 [w_min, w_max]；等价于带 KL 正则的 DRO，而它是“最小化损失分位数”的一个松弛；只多一个 softmax 和一个向量；证明了 ReLU 过参数化网络上（不含重要性采样）的收敛。nnU-Net 上只换采样器：胎儿脑 3D MRI（368 例，含 124 例开放性脊柱裂），默认 β＝100、截断 [0.1, 10]；平均 Dice 不低于对照，脊柱裂小脑 p10 +26.5 个百分点，对照组平均差 <0.1 点。BraTS 2019：增强肿瘤平均 Dice +1.0（普通 SGD）和 +1.5（Nesterov）。
- 痛点与搬法：医学分割里“按当前难度自动抽”的先例，不改网络。我们的粒度要更细：病例级（前 10 位患者占 D5 缺口的 43%）加块、错误类型级。
- 系数：β 与截断是原文默认值，没调；搬过来可用有效样本数下限代替。证据与风险：评价重在尾部分位数，我们的指标是病例平均，收益可能小；粒度是病例，不是错误类型。交互分割里未见。

### [L8-34 / L8-35] Xie 等 2023《DoReMi: Optimizing data mixtures speeds up language model pretraining》NeurIPS；Albalak 等 2023《Efficient online data mixing for LM pre-training》NeurIPS 研讨会
- 链接：arXiv 2305.10429、2312.02406；PDF：已存 `xie-2023-doremi.pdf`、`albalak-2023-online-data-mixing.pdf`。领域：大模型预训练。[全文]
- 说的是什么：DoReMi 先训参考模型，再在小代理模型上做 Group DRO，目标是最坏的“超额损失”（代理损失−参考损失），取全程域权重的平均，用于训练 30 倍大的模型。所有域的困惑度都降（包括被下调的域）；平均小样本准确率 +6.5 点，2.6 分之一的步数达到基线准确率。η＝1、平滑 1e-3，没仔细调。只用最难或只用最易（不减参考）都没有这些收益。ODM 用 Exp3 老虎机在线调域权重，奖励＝当前损失，比次优方法少 19% 迭代达到同样的最终困惑度。
- 痛点与搬法：1.1 的“信号要扣掉不可约部分”。我们不必训参考模型：理想修复就是参考。
- 系数：η、平滑项原文固定；ODM 的探索率衰减手定。证据与风险：语言模型预训练，数据量大；8k 步续训的更新次数少。

### [L8-36 / L8-37] Graves 等 2017《Automated curriculum learning for neural networks》ICML；Matiisen 等 2017《Teacher-student curriculum learning》NIPS 2017 深度强化学习研讨会
- 链接：arXiv 1704.03003、1707.00183；PDF：已存 `graves-2017-automated-curriculum-learning.pdf`、`matiisen-2017-teacher-student-curriculum.pdf`。领域：自动课程。[全文]
- 说的是什么：Graves 把课程当 N 臂老虎机，用 Exp3.S，奖励是学习进展：预测增益（训练前后同一样本的损失差）、自预测增益（在同任务再抽一个样本上量，无偏）、梯度预测增益（有偏，偏向方差大的任务）等。奖励按历史的 20%/80% 分位缩放到 [−1, 1]，免调尺度；bAbI 上预测增益优于均匀，但“均匀采样是出奇强的基线”。Matiisen：在学习曲线斜率最大的子任务上多练，斜率取绝对值以对付遗忘。
- 痛点与搬法：1.1 的候选之一，但 DRATS 2026 复测发现学习进展与学习潜力不比均匀好：它们偏向已经快速进步的（多半是容易的）任务，斜率小就放弃困难任务。只借分位数缩放。
- 系数：η、探索率手定。证据与风险：合成序列和迷宫任务；进展信号噪声大，8k 步里估计不稳。

### [L8-38 / L8-39] Jiang、Grefenstette 与 Rocktäschel 2021《Prioritized level replay》ICML；Dennis 等 2020《Emergent complexity and zero-shot transfer via unsupervised environment design》NeurIPS
- 链接：arXiv 2010.03934、2012.02096；PDF：已存 `jiang-2021-prioritized-level-replay.pdf`、`dennis-2020-paired-environment-design.pdf`。领域：强化学习的自动课程。[全文]
- 说的是什么：PLR 用 L1 价值损失给训练场景（level）打分，按排名（1/rank，温度 0.1）加陈旧度（系数 0.1）混合抽样；只有陈旧系数在 0 与 1 之间才有收益；与此前最好的方法 UCB-DrAC 合用，测试回报比标准 RL 基线提高 76% 以上。PAIRED 让对手生成环境，奖励＝遗憾（对手 agent 回报−主角回报），最小化最大遗憾得到的环境可解，也有挑战；极小极大对抗会造出不可解的环境。
- 痛点与搬法：“遗憾”＝理想修复增益−实际增益，我们天然有理想修复这个对手，不用训练对抗者；PLR 说明分数要带陈旧度刷新。
- 系数：PLR 的温度、陈旧系数由网格搜索定。证据与风险：RL 环境；对抗训练不稳。

### [L8-40 / L8-41] Corrado、Huang 与 Hanna 2026《Distributionally robust multi-task RL via adaptive task sampling》arXiv 2605.14350；Wang 等 2025《DUMP: Automated distribution-level curriculum learning》arXiv 2504.09710
- 链接：同上编号；PDF：已存 `corrado-2026-drats-adaptive-task-sampling.pdf`、`wang-2025-dump-distribution-level-curriculum.pdf`。领域：多任务强化学习；大模型后训练。[全文]
- 说的是什么：DRATS 把多任务学习写成可行性问题：每个任务要达到参考回报；缺口 g＝(参考−实际)/(参考−随机)，归一化到 [0,1]；在 KL(q‖p0)≤ε 的信任域里最大化期望缺口，解析解 q∝p0·exp(β·g)，β 由 ε 定；镜像上升在线更新，设最小采样概率。MT10/MT50、MuJoCo 上，增益来自最差任务；Ant 任务上给它 40% 到 70% 的采样概率，其余规则约 30% 且做不出来；“学习进展”“学习潜力”不比均匀好，“先难后易、学会就换”的硬切换让已学会的任务崩掉。DUMP 用滑动窗口内平均绝对优势加探索项再 softmax（温度 0.1），贪心（温度 0）更差。
- 痛点与搬法：1.1 的乙规则。参考回报换成理想修复，随机回报换成“不改”（增益 0），则 g＝1−实际/理想，恰是 A 文件表 3 的“实际/理想”。
- 系数：ε 可由有效样本数下限推出；参考值和随机值由理想修复和“不改”给出。DUMP 的温度手定。证据与风险：2026 年新文，作者自己的基准；RL 的任务是离散的，我们的组是人定的分箱。

### [L8-42 / L8-43] Chen 等 2025《Self-evolving curriculum for LLM reasoning》arXiv 2505.14970；Bae 等 2025《Online difficulty filtering for reasoning oriented RL》arXiv 2504.03380
- 链接：同上编号；PDF：已存 `chen-2025-self-evolving-curriculum.pdf`、`bae-2025-online-difficulty-filtering.pdf`。领域：大模型后训练。[全文]
- 说的是什么：SEC 把每类问题当老虎机的一臂，奖励＝该类平均绝对优势，Boltzmann 采样（按分数指数加权抽）加 TD(0)（逐步修正估计的规则）更新；绝对优势期望＝2p(1−p)，在成功率 p＝0.5 最大；Countdown 3B 模型分布外准确率 0.48→0.54；作者自认多出温度、学习率要调。Bae 证明期望策略改进的下界正比于成功率的方差，中等难度最有用；保留通过率 0.3 到 0.7 的“平衡过滤”五个数学基准平均超过 30%，普通 GRPO（一种强化学习算法）26.3%，只留难题或只留易题（24.9% 到 25.9%）还不如不过滤。
- 痛点与搬法：给 F 的“最近发展区取样”（只练修回比例 0.1 到 0.9 的状态）补了形式化依据。但推导依赖二元奖励，逐体素 BCE 的梯度正比于 |p−y|，越错越大，没有“成功率 0.5 最大”这回事，只当启发。
- 系数：SEC 的温度、学习率手定；Bae 的阈值 (0.3, 0.7) 是网格比较的结果。证据与风险：可验证奖励的 RL；对我们是类比。

### [L8-44] Fischer 等 2025《Progressive growing of patch size》arXiv 2510.23241
- 链接：arXiv 2510.23241；PDF：已存 `fischer-2025-progressive-patch-size-curriculum.pdf`。领域：医学分割（nnU-Net 框架）。[全文]
- 说的是什么：训练中把块尺寸由小逐步增大（手定的分段线性日程）；15 个 3D 分割任务；效率模式同等 Dice 下只用 44% 训练时间，性能模式平均 Dice 相对 +1.28%、用 89% 时间。文中说明 nnU-Net 的前景块比例是手定的（批大小 2 时 50%，更大时 33%）；CASED（Jesson 2017，只见转述）先多后少地过采样前景。
- 痛点与搬法：确认“块抽样配额手定”是医学分割的通行做法；它的日程手定，不是自适应的。
- 系数：块尺寸日程手定。证据与风险：非交互分割。

## 3 汇总

### 3.1 最有希望的改法（按预期对第五轮 Dice 的帮助、实现难度、新意排序）

预期提分是规划估计，不能相加；前三项合起来大约 +1 到 +2.5 点，把握低。

1. 缺口驱动的自动配额。对 P5、P2、P8。预期 D5 +0.3 到 +1.2，难度中，新意中（医学分割有 Fidon 先例，交互分割未见）。
   - 做法：1.1 的分组、缺口、甲乙两条规则，配额表存进检查点；状态来源、成对类型、病例（Fidon 式）放进同一套规则。
   - 系数：缺口以理想修复为参考，目标不手定；偏离自然频率的幅度由“有效样本数不低于一半”定；更新间隔由“最稀少组被抽到 30 次”定；体积分位箱按 TRAIN 回放切。剩下的惯例值（一半、30 次、1.3 倍、约 10% 留出病例）写进配置并注明是惯例。
   - 最快验证：CPU 上量 407/407 回放的组频率与缺口，与现行曝光并排；GPU 上两次 8k 续训对 N1_STATE_STATIC；看最大组缺口、≥10 mL 加笔修回、删笔新错体积，再看 D5。
2. 上一轮改动足迹加符号一致性增益。对 P1、P4。预期 D5 +0.5 到 +1.5，集中在第 2 到 5 轮，D1 不应变；难度中高，新意高。
   - 做法：L8-13 到 L8-16：两路零初始化输入（上一轮改动足迹、当前笔符号 × 足迹符号）；增益随机化的回放；范围头输出乘“与模型自身动作相关的概率”。
   - 系数：增益和相关概率都是网络输出；随机化范围取回放里实测的“编辑体积/目标体积”分布；若另加显式规则，RPROP 的 1.2/0.5 是通用默认值。
   - 最快验证：先在 CPU 上用现有轨迹量“反转笔”（笔与上一轮足迹重叠且符号相反）占后几轮笔的比例，以及这些轮的净新错；占比低于 10%（惯例值）就不值得做。PLAN 里的 29% 只是启发式条件，没做空间核对，这一步正好补上。
3. 差异匹配的成对监督。对 P7。预期 D5 0 到 +1.0，主要改善换笔分数 0.662 和断桥方向正确率 0.084；难度中，新意中高。做法见 1.2；权重由梯度范数自动均衡，配对类型和距离箱的占比由缺口定，差异匹配不需要间隔；验证用 PLAN 3-1 的对照（相同样本、没有成对关系），先量 E04 换笔分数和断桥方向。
4. 参考扣底的块级评分与去重。对 P2、P5。预期 D5 0 到 +0.5，难度低到中，新意低。评价块不再按 T/O/P 配额抽，而在候选块上取（pT 错误质量 − 参考）最大的前 B 个，块间去重（L8-28、L8-30）；可当第 1 项的块级实现，B 由有效样本数定。
5. 诊断，不提分：三态（没动、动了没修对、动过头）和泛化核拟合（L8-05、L8-17），用来判断上面几项是不是因为机制成立才变好。

### 3.2 别的领域已经跨过、交互分割还没跨过的思想

- 以理想修复为参考的缺口采样：RL（DRATS 2026）、LLM（DoReMi 2023）、非交互医学分割（Fidon）已有；1.4 第 2、3 条检索在交互分割里没见到。
- 类比编码式的成对比较（目标差异匹配）：教育学；1.4 第 5 条检索没见到。
- 误差灵敏度记忆（残差符号一致性调增益）：运动学习；1.4 第 6 条检索没见到，最近邻是 TIA 和 RITM 的上一轮掩膜输入。
- 信用分配（自己的改动还是原有的错）：运动学习；同上没见到。

### 3.3 判断没用或有害的方向

- 易先课程和自定步调（Bengio、Kumar、Jiang）当主机制：方向与“多练困难”相反，我们的难点是曝光缺口，不是局部极小；Soviany 还提醒会损害多样性。只作预热。
- 学习进展或斜率当主信号（Graves、Matiisen）：DRATS 复测不比均匀好，斜率小就放弃困难组；8k 步里估计也不稳。只借分位数缩放。
- 硬切换（学会就扔）和贪心取最大：DRATS 里崩，DUMP 里更差。
- 不扣参考的“损失最大的前 B 个”：追噪声标签（RHO-LOSS）；3 mm 网格往返丢掉的小目标就是现成的噪声源。
- 把 RL 里“成功率 0.5 时学习信号最大”直接搬到逐体素 BCE（SEC、Bae）：推导依赖二元奖励，BCE 的梯度越错越大；只当启发。
- 以最差组为唯一目标的 Group DRO：拉低平均；要加 KL 或有效样本数的锚。
- 机器教学的精确最优教学集（NP 难）和需要目标模型的“有用性”项（Liu）：做不了，只借“夹住边界的近邻对”。
- 快慢两过程（Smith）、表扬与自我层反馈、间隔与交错：没有新增机制，F 已判装饰。

### 3.4 本路新读文献清单

共 44 篇；已存 PDF 34 个。未存 10 篇：付费墙 4 篇（01、03、05、09），作者页链接失效 1 篇（08），PMC 的 PDF 被验证页挡住、没有绕过 5 篇（14 到 18）。

- L8-01 Kluger、DeNisi，1996，The effects of feedback interventions on performance，未存
- L8-02 Shute，2008，Focus on formative feedback，已存
- L8-03 Hattie、Timperley，2007，The power of feedback，未存
- L8-04 Wisniewski、Zierer、Hattie，2020，The power of feedback revisited，已存
- L8-05 Lyster、Ranta，1997，Corrective feedback and learner uptake，未存
- L8-06 Schwartz、Bransford，1998，A time for telling，已存
- L8-07 Gentner、Loewenstein、Thompson，2003，Learning and transfer: A general role for analogical encoding，已存
- L8-08 Alfieri、Nokes-Malach、Schunn，2013，Learning through case comparisons，未存
- L8-09 Kapur，2008，Productive failure，未存
- L8-10 Bjork、Bjork，2011，Making things hard on yourself, but in a good way，已存
- L8-11 Wolpert、Diedrichsen、Flanagan，2011，Principles of sensorimotor learning，已存
- L8-12 Shadmehr、Smith、Krakauer，2010，Error correction, sensory prediction, and adaptation in motor control，已存
- L8-13 Herzfeld 等，2014，A memory of errors in sensorimotor learning，已存
- L8-14 Albert 等，2021，An implicit memory of errors limits human sensorimotor adaptation，未存
- L8-15 Wei、Körding，2009，Relevance of error，未存
- L8-16 Berniker、Körding，2008，Estimating the sources of motor errors，未存
- L8-17 Donchin、Francis、Shadmehr，2003，Quantifying generalization from trial-by-trial behavior，未存
- L8-18 Thoroughman、Shadmehr，2000，Learning of action through adaptive combination of motor primitives，未存
- L8-19 Smith、Ghazizadeh、Shadmehr，2006，Interacting adaptive processes with different timescales，已存
- L8-20 Wulf 等，2010，Frequent external-focus feedback enhances motor learning，已存
- L8-21 Bengio 等，2009，Curriculum learning，已存
- L8-22 Kumar、Packer、Koller，2010，Self-paced learning for latent variable models，已存
- L8-23 Jiang 等，2014，Self-paced learning with diversity，已存
- L8-24 Soviany 等，2022，Curriculum learning: A survey，已存
- L8-25 Zhu，2015，Machine teaching: An inverse problem to machine learning，已存
- L8-26 Zhu、Singla、Zilles、Rafferty，2018，An overview of machine teaching，已存
- L8-27 Liu 等，2017，Iterative machine teaching，已存
- L8-28 Shrivastava、Gupta、Girshick，2016，Training region-based object detectors with online hard example mining，已存
- L8-29 Katharopoulos、Fleuret，2018，Not all samples are created equal，已存
- L8-30 Mindermann 等，2022，Prioritized training on points that are learnable, worth learning, and not yet learnt，已存
- L8-31 Sagawa 等，2020，Distributionally robust neural networks for group shifts，已存
- L8-32 Fidon 等，2022，Distributionally robust deep learning using hardness weighted sampling，已存
- L8-33 Fidon 等，2021，Distributionally robust segmentation of abnormal fetal brain 3D MRI，已存
- L8-34 Xie 等，2023，DoReMi: Optimizing data mixtures speeds up language model pretraining，已存
- L8-35 Albalak 等，2023，Efficient online data mixing for LM pre-training，已存
- L8-36 Graves 等，2017，Automated curriculum learning for neural networks，已存
- L8-37 Matiisen 等，2017，Teacher-student curriculum learning，已存
- L8-38 Jiang、Grefenstette、Rocktäschel，2021，Prioritized level replay，已存
- L8-39 Dennis 等，2020，Emergent complexity and zero-shot transfer via unsupervised environment design，已存
- L8-40 Corrado、Huang、Hanna，2026，Distributionally robust multi-task RL via adaptive task sampling，已存
- L8-41 Wang 等，2025，DUMP: Automated distribution-level curriculum learning，已存
- L8-42 Chen 等，2025，Self-evolving curriculum for LLM reasoning，已存
- L8-43 Bae 等，2025，Online difficulty filtering for reasoning oriented RL，已存
- L8-44 Fischer 等，2025，Progressive growing of patch size，已存
