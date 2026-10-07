# R2 认知、意图与学习机制的独立原文审计

## 结论与范围

**intent 主线可以继续，但应定义为：在明确交互协议下，结合当前分割、当前笔和可观察交互历史，推断本轮被授权修改的残差范围。** 当前数据能监督这种可操作的指代范围，不能直接证明模型理解了医生真实心理意图。跨领域最值得带走的是三件可实现的事：目标与画法的条件式配对、模型实际编辑历史、应改区域与易误改保留区域的联合训练。物体注意为种子到范围的结构计算提供动机，但不能把解剖物体、残差连通块和用户所指三者等同。

本轮独立核查 **34 篇去重文献：32 篇原始研究，2 篇元分析**。32 篇原始研究中，**26 篇打开并检查了与本项目有关的方法、结果或模型定义正文；6 篇只有原始摘要或受限页面中的部分结果**。2 篇元分析中，2020 年论文全文可读；1996 年论文仅原摘要与同作者后续总结可核。这里的“正文核查”不表示逐字读完所有正文和补充材料，也不把此前已读论文重新记成新增发现。

本审计对照了 `PLAN.md`、`F-cognitive-analogies.md`、`L6-visual-cognition.md`、`L7-intent-inference.md`、`L8-education-motor.md`、`V1-citation-check.md`、`S1-literature-digest.md` 和第三轮 Codex brief/answer，并对 `R2-synthesis-draft.md` 做了第二轮概念复审。没有修改 PLAN、生产代码、服务器或队列。逐篇机器可读记录见同目录 `R2-cognition-papers.json`；所有条目区分原文结论、迁移建议与限制。

## 1. 必须纠正的论证

| 原有推演 | 审计判断 | 可保留的更强表述 |
|---|---|---|
| 人的注意沿物体传播，所以一笔至少指完整错误物体 | 前半有实验证据，后半不是该证据的结论 | 任务先定义 T；模型可利用种子到 T 的状态条件连通作为归纳偏置 |
| flat 是低维逐体素头，所以数学上算不了连通 | 论证越界 | 若输入特征丢失关键连通信息，任何读出都不能恢复；但全局或大感受野编码可能已保留信息，不能套局部感知机定理宣布整个网络不可能 |
| 一笔只指一个对象，应在对象间 softmax | 与“触及多个残差分量取并集”的当前标签可能冲突 | 候选可以竞争，但候选本身允许合法并集；不要默认互斥的单一解剖对象 |
| 同病灶重复笔意味着上一轮没修够 | 不是唯一解释 | 重复笔可表示剩余错误、强调、重新指认、撤销错误或目标切换，须结合模型实际响应 |
| 同一状态换笔就必须换目标 | 与同目标画法一致性矛盾 | 换到不同目标时输出应变；同一目标的合法画法变化才可作为不变性对 |
| 更多笔像素是更多独立例子，可据大小原则缩小范围 | 取样假设不成立 | 笔像素高度相关，且常由中心线/边界策略主动选取；训练应覆盖这些取样机制 |
| 教育学的 48% 对 19% 证明单因素成对损失有效 | 将人的学习结果直接推成机器学习结构 | 论文支持显式比较关系的价值；具体配对标签和损失必须由 SIRB 的任务变换推导 |
| 反馈元分析中许多负效应解释了模型改过头 | 只是一种宽泛类比 | 改过头的直接证据来自本地 T/O/P 与真实编辑记录；元分析不能证明其病因 |

F 文件中“两个远端体素 F 相同则得分相同”这个条件命题成立，但不能进一步推出当前全局编码器永远无法产生不同 F。原文自己记载约 405 mm 理论感受野与 global 特征，已不符合把整个系统当作局部感知机的前提。有效感受野衰减和细桥贡献很小可以提出可测的困难案例，不能自动推出不可表达。该问题属于项目架构与输入信息的推理边界，不是认知论文能替代的性能证据。

## 2. 四组关键数字与访问深度

### 2.1 注意传播的 r=0.51 对 r=0.13：部分核实，不能再写成完整核验

Pooresmaeili 与 Roelfsema（2014）的原始摘要确实报告：干扰曲线离目标近时注意传播慢，远时快，约每个感受野 50 ms。出版社索引结果可核到模型距离与延迟 **r=0.51、解释 26.6% 方差**。但本轮未取得可读的完整正文和补充材料，**r=0.13 及 49/118 ms 的统计条件没有完成独立原文核验**。这不是判定数字错误，而是证据状态仍不足。主计划可以直接改为定性结论：传播受沿目标的几何和周边干扰影响，不能用直线距离统一描述。[原始摘要](https://pubmed.ncbi.nlm.nih.gov/25456446/)；[出版社页面](https://www.sciencedirect.com/science/article/pii/S0960982214012834)。

### 2.2 可变目标 r=0.95 对固定目标 r=0.57：数字正确，漏了重要对照

Baker、Saxe、Tenenbaum（2009）Table 2 的 bootstrap 交叉验证相关：M2=0.95，固定单目标 M1=0.57；**简单近期行动启发式 H=0.91**。这是回溯目标判断中对人类评级的拟合，不是 95% 对 57% 的识别准确率。它说明目标可能变化、近期行动有用，不能证明必须引入复杂逆规划器。对本项目，先提供上一轮实际编辑与当前笔的关系更符合效率要求。[原文 Table 2](https://web.mit.edu/9.s915/www/classes/cognition2009.pdf)。

### 2.3 反馈 38% 为负：原始可访问证据支持“超过三分之一”

Kluger 与 DeNisi（1996）原摘要报告 607 个效应、23,663 次观察、平均 d=0.41，超过三分之一为负。同作者 1998 年总结也采用超过三分之一的表述。旧 L8 已承认精确 38% 来自二手检索片段。本轮没有把 38% 升级为原文完整核验，建议正文写“超过三分之一”，不靠这个数字支撑损失结构。[1996 DOI](https://doi.org/10.1037/0033-2909.119.2.254)；[同作者 1998 年总结](https://itgs.ict.usc.edu/papers/Kluger&DeNisiFeedbackCDPS98.pdf)。

还发现一个统计口径需要澄清：Wisniewski 等（2020）**994 个效应整体 d=0.55，17% 为负；删除 35 个极端效应后 d=0.48**。旧摘要把 d=0.48 和 17% 不加说明地并列，混合了清理前后口径。教育效应量不是 Dice，不能拿这些数给模型增益定量。[原文 General Impact 与 Outlier Analysis](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.03087/full)。

### 2.4 比较案例 48% 对分别学习 19%：数字正确，实验不是“只差一因素”

Gentner、Loewenstein、Thompson（2003）实验 2，N=128，学习谈判案例后应用所教原则到新情境的比例，比较条件为 48%，分别学习为 19%。操作是明确引导比较共同结构，**没有证明每对只改变一个因素最佳，也没有研究神经网络输出差分损失**。若本项目用目标交换和画法不变性配对，数学依据是任务标签随输入变换的关系；这篇论文提供启发，不提供该损失的正确性或效应量。[原文 Experiment 2](https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewensteinThompson03.pdf)。

## 3. intent 应怎样精确定义

### 3.1 三个对象必须区分

**解剖对象 A**：图像中的器官、病灶或其他可感知实体。

**当前带符号残差 E**：由当前分割 M 与参考 G 的差构造；ADD 为 G\M，REMOVE 为 M\G。

**本轮可操作所指 T**：在固定交互协议 π 下，这一笔所触及的原生残差连通分量的并集。π 包括当前角色构建器、连通方式、操作方向与未触及错误时的处理。

一个病灶内可能存在被正确分割组织隔开的多个漏分残差岛；两个残差岛属于同一解剖对象，却不因此都被同一笔授权。相反，一笔也可能合法地碰到多个残差分量，此时 T 是并集。视觉注意可以沿整个物体展开，但 SIRB 需要在当前已正确部分停止编辑。这正是“从物体传播借结构”与“直接照搬物体范围”的区别。[Ekman 等 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7687059/)；[Jeurissen 等 2016](https://elifesciences.org/articles/14320)。

### 3.2 建议的论文定义

> 本方法学习交互条件下的操作性指代范围：在声明的纠错协议下，由影像、当前分割、当前有符号笔迹及可观察历史，预测本轮应被修改的残差集合，并保留其余区域。训练真值用于构建范围监督，不作为推理输入。这里的 intent 指任务可观察变量所约束的纠错目标，不等同于对临床操作者内在心理状态的直接测量。

可用概念记号 qθ(T | X, M, s, a, H; π)。π 在当前实验中是固定协议，不要求新增协议网络。若实现只输出逐体素 pT，应称体素属于 T 的预测分数；未经相应概率建模与校准，不能把它直接叫作完整集合的后验概率。

在固定 π 与 G 时，T 的训练定义可唯一；这并不表示真实临床的同一幅图、同一 mask、同一笔能唯一揭示 LOCAL、COMPLETE、整病灶或任意其他心理目标。若两个被允许的真实目标在所有可见输入上相同，模型无法凭重新命名 hidden state 增加信息。此时需要固定操作约定，或以后引入显式范围模式/额外反馈。当前性能线用已有冻结协议即可，不需要先开展心理量表或新用户实验。RSA 与逆规划论文也都依赖明确的候选目标、说话人知识和行动生成假设。[Frank 与 Goodman 2012](https://web.stanford.edu/~ngoodman/papers/FrankGoodman-Science2012.pdf)；[Baker 等 2017](https://compdevlab.yale.edu/docs/2017/Bakeretal2017.pdf)。

### 3.3 没有额外输入，intent 仍然可以有价值

新增表示、结构和监督可以让模型更有效地使用已有笔与状态信息，所以“没有新增信息”不等于“不能提升”。应准确称为更好的归纳偏置或训练目标，不能声称模型凭一个新意图标签获得了原输入没有的语义。相同输入下的强组合可以先验证性能；效果出来后再以同父、同预算、同数据暴露对照分析贡献。

## 4. 从原文到可实现机制

### 4.1 物体注意：借空间关系，编辑边必须由当前残差任务学习

Egly（1994）的同物体优势、Roelfsema（1998）的目标曲线反应、Houtkamp（2003）的渐进追踪、Ekman（2020）的任务无关物体约束，共同说明仅有提示点的直线距离并不足以描述人如何选择一个对象。它们并未区分本项目的真病灶、同号非目标错误 O 与正确区 P。[Egly 原始摘要](https://pubmed.ncbi.nlm.nih.gov/8014611/)；[Roelfsema 原始摘要](https://pubmed.ncbi.nlm.nih.gov/9759726/)；[Houtkamp 出版社摘要](https://link.springer.com/article/10.3758/BF03194840)。

**本项目推演**：让当前笔直接影响空间特征；可选图边由影像、M、操作方向及物理邻接关系计算，学习“这条连接在当前错误定义下是否允许”，而不是只学图像强度相似性。正确区可能是禁止编辑的桥，外观相似也不应自动贯通。边界归属和关联场提供了局部与全局上下文共同作用的机制动机。[Zhou 等 2000](https://neuroscience.jhu.edu/files2/publications_Von_Der_Heydt_R_6594-6611.pdf)；[Field 等 1993](https://web.mit.edu/9.35/www/archives/2020/vision/papers/contour_integration.pdf)。

不要写成“认知证明 max-min 是唯一正确算子”。Jeurissen（2016）的模型使用局部宽度加权路径与 Dijkstra 计算；视觉研究可以启发不同路径统计，无法替代本任务算法选择。即使并查集精确解出某个给定图的可达性，也不会使错误的边亲和自动变正确。

最新直接相关论文 Mollard 等（2026）尤其需要准确介绍：它先按尺度用明确分组标签训练前馈门，再使用循环动态；作者报告直接联合训练没有稳定学会所有尺度，自然图像仍是后续方向。可借“分清边的监督与聚合”的训练设计，不能据此承诺一个端到端模块自动解决医学所有尺度。[完整原文](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014193)。

### 4.2 语用推断：候选和信息来源比复杂递归深度更重要

RSA 解释相同词在不同对象情境下为何有不同所指；知识操纵进一步表明同样话语的含义依赖说话人知道什么。教学性取样研究又表明随机例子与有意挑选的例子不可用同一似然处理。[Goodman 与 Stuhlmüller 2013](https://onlinelibrary.wiley.com/doi/10.1111/tops.12007)；[Shafto 等 2014](https://web.stanford.edu/~ngoodman/papers/shaftogg14.pdf)。

**本项目推演**：候选集合应能表达协议允许的替代范围，同时包含不改；至少不能把“所有阈值都是同一排序的水平集”误称为涵盖所有语义。若体素排序本来把 T 与 O 混在一起，仅重排阈值不一定出现正确范围。来自不同结构的候选可以增加覆盖，但要用真实五轮结果判断是否值得计算。

范围解释与执行价值是不同问题：q(T|可见量) 表达范围证据，候选的预期收益表达执行后果。候选评分头可以实际合并这些信息，不必新增两套复杂网络；论文和日志仍应区分“没给出好候选”和“选错已有候选”。Jeon 等（2020）强调反馈的选择集合与 grounding function，正好说明一条纠正必须相对于当前参考状态和实际可选后果解释。[原文](https://proceedings.neurips.cc/paper_files/paper/2020/file/2f10c1578a0706e06b6d7db6f0b4a6af-Paper.pdf)。

大小原则不可照搬成越长笔越小范围：Xu 与 Tenenbaum（2007）的强取样似然依赖概念内随机、独立取样等假设，相邻笔像素并非如此。更稳的实现是混合合法选笔策略与同目标的形态增强，使网络学到实际取样条件，而不是训练一个只辨认模拟器中心线形状的“speaker head”。[原文模型假设](https://sites.socsci.uci.edu/~lpearl/courses/readings/XuTenenbaum2007_WordLearningBayesianInference.pdf)。

### 4.3 重复纠正：保存系统做了什么，不把动作符号当成心理标签

Liszkowski 等（2007）把成人指错对象和态度不同分开操纵，重复指向的解释依赖成人响应。Baker（2009）允许目标变化的模型与近期行为启发式都能解释不少目标判断。机器人纠正文献则说明：人的纠正有目的但可能夹带其他变化，不能把所有随纠正变化的特征都更新为目标。[Liszkowski 原文](https://www.eva.mpg.de/documents/Cambridge/Liszkowski_Reference_JChildLang_2007_1554758.pdf)；[Losey 等 2022](https://journals.sagepub.com/doi/10.1177/02783649211050958)。

**本项目推演**：至少分开两个历史来源：

1. 用户可观察历史：此前的有符号笔迹、顺序，以及已知交互模式。
2. 系统可观察历史：实际执行后的 ΔM，按新增与删除分开；可加上一轮预测分数、选择的候选和当前笔与该编辑的重叠关系。

系统 ΔM 是可能有错的证据，不是永久正确区域。旧用户笔也不必永久有效：新笔可能修订旧目标或纠正旧操作，尤其反号重叠时应允许重新解释。**同号重复不硬扩张，反号重复不硬收缩**。首轮用明确缺失标记，所有轮次只输入可观察量；真实 T、真实新错分布或 Dice 可以生成 TRAIN 标签，不能伪装成历史特征。

Hawkins（2020）的机器交流适应使用可观察目标反馈做在线更新，不能无条件搬成测试时分割训练。ToMnet 或 CHAI 的计算思想可以借为轻量历史条件化及多策略训练；当前五轮性能线无须增加心理特质网络、完整 CIRL 或在线逆规划。[Hawkins 原文](https://aclanthology.org/2020.conll-1.33/)；[ToMnet](https://proceedings.mlr.press/v80/rabinowitz18a.html)；[CHAI 作者稿](https://cocosci.princeton.edu/papers/hawkinspartners.pdf)。

### 4.4 类比教育：配对的有效性先由任务关系保证

建议把配对定义写成以下合同，再选择实现损失：

| 配对类型 | 必须成立的条件 | 可要求的输出关系 |
|---|---|---|
| 同状态交换目标笔 | 相同 X、M、方向及兼容可见域；两笔触及不同目标集合 T1、T2 | 输出分别对应各自目标；不能只训练两输出“尽量不同” |
| 同目标换画法 | 按冻结角色构建器计算的原生 T 完全相同；可见域足以覆盖比较区域 | 在共同合法可见域上保持范围一致 |
| 同笔改变分割状态 | 固定笔与影像，按新 M 重算 T/O/P；被比较位置有可用标签 | 输出按新残差变化；不强求整卷都不同，也不因未知路径强判断开 |

“同病灶”“中心接近”或“都叫 boundary 画法”不保证 T 相同；更长的笔可能碰到另一残差分量。若训练裁剪不同且目标不在共同可见域，不能强制全体素一致。配对是可利用的监督设计，不因此等于识别了人类意图的因果机制。

Gentner（2003）与 Schwartz、Bransford（1998）支持显式对照和区分对学习有用，但不决定必须某种差分损失或某个系数。保留样本的选择应服从当前 T/O/P 任务：覆盖容易被误改的 P 以及容易混淆的 O，避免只给轻易可辨的背景。先组合训练，再在胜出系统中分析配对具体贡献。[Gentner 原文](https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewensteinThompson03.pdf)；[A Time for Telling](https://aaalab.stanford.edu/papers/time_for_telling.pdf)。

### 4.5 运动学习：相关历史有启发，不要制造硬门槛

Herzfeld 等（2014）的误差记忆、Wei 与 Körding（2009）的误差相关性、Smith 等（2006）的双时间尺度都描述特定运动适应现象。它们启发“当前纠正要看历史和任务”，但操作类型 ADD/REMOVE 不是同一目标下的有符号运动误差，五轮分割也不是长时间身体适应。[误差记忆](https://pmc.ncbi.nlm.nih.gov/articles/PMC4506639/)；[误差相关性](https://pmc.ncbi.nlm.nih.gov/articles/PMC2657056/)；[双过程学习](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.0040179)。

**本项目推演**：预测每次编辑的实际价值和保留风险，不把大编辑统一惩罚；用实际状态变化覆盖后几轮，不根据“人会快速慢速学习”新增双 RNN。局部错误归属、目标范围和执行价值可以区分，但性能线先用小模块共同表达，不先做庞大心理模型拆分。

## 5. 对性能优先方案的具体建议

**直接并入现有强组合**：当前笔的空间输入、真实闭环状态、任务定义下的目标/保留联合监督、实际 signed ΔM 历史，以及不额外增加大前向的合法配对。这些分别针对缺少空间证据、后几轮分布变化、块内过改和条件关系没有被学会，且不需要先验证一个完整心理理论。

**保留为可独立推进的结构组合**：状态条件边亲和与种子连通的软特征。让已有输出头可利用或忽略它，保留边界监督；不把图模块设成达到效果的前置条件，也不把它产生的图范围当成真实 T 的硬保证。最新认知模型的分阶段门训练可作为难训时的备选，不增加第一轮待实现清单。

**先不加入**：RSA 多层递归、完整逆规划/CIRL、医生心理量表、人格表征、测试时在线心理适应、由笔长推出来的体积先验、重复笔硬伸缩、单对象互斥 softmax。这些目前缺少额外可观察信息或明确的计算收益，会分散达到 D5 目标的资源。

**最低限度记录即可，不开新一轮消融**：每次真实五轮的 T 内修复、O 改动、P 新错、no-op、用户当前笔与上一轮实际编辑的关系。已有原生候选标签可分清候选覆盖失败与选择失败。0.79/0.80 的报告口径保持总方案定义。认知实验不预测本项目可实现多少 Dice；所有收益数必须来自当前联合策略的真实闭环评估。

## 6. 第二轮综合方案复审：四条必要文字修订

针对 `R2-synthesis-draft.md`，以下四处已回传主审；其余关于操作定义、可学习不等于硬保证、图解不等于真范围的边界基本正确。

1. 1.1 中“同一 M 换到另一笔，目标应变化”改为“换到不同目标的笔时应变化；同一目标的合法画法变化可保持”。开头“由这一笔确定”改为“结合可见状态、笔迹与历史推断协议定义的范围”。
2. q(T|…) 只作任务记号，不将现有逐体素 pT 宣称为校准的范围级后验，也不要求因此新增一个心理意图头。
3. 明确 H 包含用户笔历史与系统实际 signed ΔM 两种来源。系统动作可能错误；旧用户约束也可能被新笔修订或覆盖，不能把任何历史无条件永久锁定。
4. 同目标正对以原生 T 集合相同和可见域/方向/状态兼容为准；同一解剖病灶或相近中心不足以判为正对。延长一笔可能改变授权集合。

## 7. 逐篇核查登记

下表与 JSON 对应。正文表示已检查相关方法/结果，不表示全文逐字精读；原始摘要或受限页面明确另列。所有“用于本项目”都是待验证迁移推演，未声称原论文已在 SIRB 上验证。

| ID / 论文 | 访问深度 | 原文核验结论 | 项目迁移与限制 |
|---|---|---|---|
| R2-C01 · [Shifting Visual Attention Between Objects and Locations: Evidence From Normal and Parietal Lesion Subjects](https://pubmed.ncbi.nlm.nih.gov/8014611/)（1994） | 原始摘要 | 双矩形线索范式区分位置与物体对注意转移的作用；正常受试者有同物体优势，病灶组显示可分离的注意效应。 | 把同一笔与目标内、目标外相似区域的区分作为训练和诊断问题；不以此证明整病灶就是指代范围。 限制：等距同物体优势本身不唯一确定逐格传播机制，也没有定义医学残差的边界。 |
| R2-C02 · [Object-based attention in the primary visual cortex of the macaque monkey](https://pubmed.ncbi.nlm.nih.gov/9759726/)（1998） | 原始摘要 | 猕猴曲线追踪中，与目标曲线对应的 V1 神经元反应相对干扰曲线增强，支持物体选择对早期视觉表征的影响。 | 当前笔应能调制空间表征，适合作为空间支路的机制动机；不推导特定连通算法。 限制：这是训练过的曲线追踪任务，曲线身份由实验规定；不是从有限笔迹恢复任意医生意图的证据。 |
| R2-C03 · [A gradual spread of attention during mental curve tracing](https://link.springer.com/article/10.3758/BF03194840)（2003） | 原始摘要 | 心理曲线追踪中注意逐渐沿目标曲线展开；选中一条曲线需要时间，不能把物体选择一概视为瞬时完成。 | 保留种子到范围的结构候选，计算预算由实际图规模处理，不能照搬人脑毫秒数为迭代次数。 限制：动态行为证据支持渐进选择，不意味着离散 3D 残差图必须以固定轮数神经传播实现。 |
| R2-C04 · [A Growth-Cone Model for the Spread of Object-Based Attention during Contour Grouping](https://pubmed.ncbi.nlm.nih.gov/25456446/)（2014） | 原摘要＋索引结果 | 目标曲线附近干扰物较近时注意传播较慢、较远时较快；摘要给出约每个感受野 50 ms 的量级。出版社结果片段报告模型距离与延迟 r=0.51。 | 借相对几何与边界约束，不借固定 mm 或神经时间常数；精确数字对在主方案中降为定性表述。 限制：未完整核实旧摘要的 r=0.51 对 r=0.13 数字对及具体统计条件；感受野尺度是该视觉任务的机制量，不是医学空间半径。 |
| R2-C05 · [Object Selection by Automatic Spreading of Top-Down Attentional Signals in V1](https://pmc.ncbi.nlm.nih.gov/articles/PMC7687059/)（2020） | 相关正文 | 在物体结构与任务无关的条件下，空间注意仍沿物体扩展；结果支持物体结构对由上而下的注意信号产生约束。 | 显式学习任务定义的错误边界，避免直接把图像中的物体边界当作编辑边界。 限制：自动物体扩展可能正与残差纠错的保留要求冲突；正确分割的同一病灶部分仍须保持。 |
| R2-C06 · [Coding of Border Ownership in Monkey Visual Cortex](https://neuroscience.jhu.edu/files2/publications_Von_Der_Heydt_R_6594-6611.pdf)（2000） | 相关正文 | 相同局部边缘在不同全局图形上下文中可产生不同反应，V2/V4 神经元编码边界属于哪一侧的物体。 | 当前状态、笔迹两侧及较大上下文需共同决定编辑边界；优先空间编码，不额外硬设毫米采样距离。 限制：边界归属是物体—背景判断，不等于 ADD/REMOVE 操作下 T/O/P 三类；单一二维法线也不能覆盖任意 3D 笔迹。 |
| R2-C07 · [Contour Integration by the Human Visual System: Evidence for a Local Association Field](https://web.mit.edu/9.35/www/archives/2020/vision/papers/contour_integration.pdf)（1993） | 相关正文 | 局部定向元素能否被整合为轮廓取决于位置与方向关系；共线或平滑连接与正交排列的可检测性不同。 | 图亲和可联合学习图像、当前 mask 与操作方向，而不是只用欧氏邻近或强度相近。 限制：关联场是受具体刺激支持的感知描述；作者没有证明任意语义区域都由同一局部亲和规则决定。 |
| R2-C08 · [How the visual brain can learn to parse images using a multiscale, incremental grouping process](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014193)（2026） | 相关正文 | 模型先用各尺度的明确分组标签训练前馈门，再通过循环去抑制动态完成曲线和区域分组；作者报告直接联合训练未能稳定学会利用全部尺度。 | 若图分支难训，先监督状态条件下的边亲和再接聚合，比直接复制整套皮层循环更可行；不能把阶段训练的成果说成无先验全学习。 限制：自然图像适用性仍是后续工作；该论文不支持无需额外监督即可端到端自动学出所有尺度的保证。 |
| R2-C09 · [Serial grouping of 2D-image regions with object-based attention in humans](https://elifesciences.org/articles/14320)（2016） | 相关正文 | 二维区域分组时间受区域几何约束；模型用局部可容纳圆的尺度构造加权路径距离，再与反应时比较。 | 把连通距离与局部宽度作为可学习候选特征；算法选择按准确率和计算效率，不能由注意扩散类比直接指定。 限制：原文并非 max-min 路径唯一性的证明；神经行为拟合不能决定医学任务应采用加权最短路、随机游走还是最宽路径。 |
| R2-C10 · [Action understanding as inverse planning](https://web.mit.edu/9.s915/www/classes/cognition2009.pdf)（2009） | 相关正文 | 回溯目标判断中，可变目标模型 M2 的交叉验证 r=0.95，固定单目标 M1 为 0.57；同时简单启发式 H 为 0.91。论文明确把动作到目标视为欠定逆问题。 | 用实际近期编辑历史帮助判断当前目标，可先用小历史分支；没有理由因该比较立即增加复杂规划器。 限制：0.95/0.57 是特定移动主体任务下人类评级拟合，不是意图识别准确率，更不是医学性能增幅；不能省略强启发式对照。 |
| R2-C11 · [Predicting pragmatic reasoning in language games](https://web.stanford.edu/~ngoodman/papers/FrankGoodman-Science2012.pdf)（2012） | 相关正文 | 听者结合词义、情境显著性以及说话人选词的信息量来推断所指对象；模型使用可观测情境及测得的显著性。 | 候选范围应相对于实际可选替代项评分；先用当前图像、mask、笔迹和可观察历史，避免把额外心理信息凭空加入。 限制：所谓无自由参数的拟合依赖任务结构和显著性测量，不代表任何输入都能唯一读出意图。 |
| R2-C12 · [Knowledge and Implicature: Modeling Language Understanding as Social Cognition](https://onlinelibrary.wiley.com/doi/10.1111/tops.12007)（2013） | 相关正文 | 听者的含义推断依赖说话人知道什么；同样话语在不同知识条件下产生不同推断。 | 区分图像证据的不确定性与范围偏好不确定性；临床泛化时允许噪声笔和不确定目标。 限制：医生看见影像不等于掌握真实病变 mask；不能据可见图像就把用户当作完美规划者。 |
| R2-C13 · [Word Learning as Bayesian Inference](https://sites.socsci.uci.edu/~lpearl/courses/readings/XuTenenbaum2007_WordLearningBayesianInference.pdf)（2007） | 相关正文 | 大小原则在样本由概念范围内随机抽取等假设下，使更窄且能解释全部例子的假设获得较高似然；多例可改变词义泛化。 | 对笔迹采样机制建模或增强；不强加随笔长增加自动缩范围的体积先验。 限制：一条笔上的相邻像素高度相关且由用户主动选择，不能当作 n 个独立随机例子代入 \|H\|^-n；儿童词义的整体物体偏好不规定医学残差下限。 |
| R2-C14 · [A rational account of pedagogical reasoning: Teaching by, and learning from, examples](https://web.stanford.edu/~ngoodman/papers/shaftogg14.pdf)（2014） | 相关正文 | 学习者若知道例子是为教学而选择，会做出不同于随机取样假设的推断；教师选择与学习者解释相互依赖。 | 训练混合有效的选笔策略，保持每种策略的目标标签一致；不让模型只把最大错误中心的几何规律当作 intent。 限制：推断依赖双方对任务、目标空间及取样者的知识假设；不能直接给出医学模拟器的唯一正确分布。 |
| R2-C15 · [Reference and attitude in infant pointing](https://www.eva.mpg.de/documents/Cambridge/Liszkowski_Reference_JChildLang_2007_1554758.pdf)（2007） | 相关正文 | 成人对错误所指表现积极时，婴儿常在同一试次重复指向以修复所指；成人所指正确但不感兴趣时，行为模式不同。 | 把模型上一轮实际修改作为解释重复笔的上下文；同号重复和反号重复均不可直接触发扩张或收缩。 限制：重复动作的意义由成人具体响应条件界定；实验不支持重复笔迹必然表示范围不足。 |
| R2-C16 · [Rational quantitative attribution of beliefs, desires and percepts in human mentalizing](https://compdevlab.yale.edu/docs/2017/Bakeretal2017.pdf)（2017） | 相关正文 | 观察者结合主体能看见的环境及其行动，联合推断信念与目标；部分可观测性在解释行为时有作用。 | 训练用 G 构造标签但推理输入只能用可见量；不把真值残差或前轮真值目标作为用户历史输入。 限制：模型需要环境与行动生成假设；推断目标和推断主体对事实的认识是不同变量。 |
| R2-C17 · [Machine Theory of Mind](https://proceedings.mlr.press/v80/rabinowitz18a/rabinowitz18a.pdf)（2018） | 相关正文 | 通过跨主体经验、近期轨迹和当前情境学习预测主体行为，可以在受控环境中归纳主体差异与部分可观测状态。 | 轻量历史编码与混合选笔策略已经能借其计算思想，暂不新增人格或医生心理模块。 限制：行为预测嵌入不等于解释清楚的心理意图；短短五轮修复也未必足以估计稳定用户特质。 |
| R2-C18 · [Reward-rational (implicit) choice: A unifying formalism for reward learning](https://proceedings.neurips.cc/paper_files/paper/2020/file/2f10c1578a0706e06b6d7db6f0b4a6af-Paper.pdf)（2020） | 相关正文 | 不同人类反馈可描述为在特定可选集合内的带噪声选择；同一动作需要通过 grounding function 对应到它在该任务中比较的后果。 | 候选编辑应相对于当前 mask 解释，并含保留/不改；先定义哪些候选是任务允许的替代项，再训练评分。 限制：选择集合与映射本身是关键建模假设；不能只加一个 intent 标签就获得额外信息，也不能默认人类温度参数通用。 |
| R2-C19 · [Cooperative Inverse Reinforcement Learning](https://people.eecs.berkeley.edu/~russell/papers/russell-nips16-cirl.pdf)（2016） | 相关正文 | 人类知道而机器人不知道的奖励参数可作为隐藏状态；机器人在合作交互中通过人的行为更新目标信念。 | 概念上分开图像正确性、被授权范围与动作收益；本轮不把完整 CIRL 求解器加入性能主线。 限制：结论依赖指定奖励结构与合作策略；求解 POMDP 对本任务可能代价过高，而且 G 与意图并非同一个隐藏量。 |
| R2-C20 · [Learning Robot Objectives from Physical Human Interaction](https://collab.me.vt.edu/pdfs/bajcsy_corl2017.pdf)（2017） | 相关正文 | 物理纠正不仅可被当作外力抵消，也可用来更新机器人目标，以减少之后重复发生的同类偏差。 | 保存上一轮实际编辑及后续用户纠正的关系，比只累计笔位置更有信息；适合作为输入，不强制跨病灶推广纠正。 限制：学习建立在给定奖励特征与机器人动力学上，不能直接推出像素级完整指代范围。 |
| R2-C21 · [Physical interaction as communication: Learning robot objectives online from human corrections](https://journals.sagepub.com/doi/10.1177/02783649211050958)（2022） | 相关正文 | 人的纠正常是有意图但不完美的；沿纠正同时改变的所有特征更新目标，可能误把附带变化当成用户意图。 | 每笔联合训练应改与应保留的区域，避免给附带正确的别处编辑奖励；以实际操作约束抑制过度泛化。 限制：单次主要调整一个特征是该方法假设；不同任务比较结果混合，不能说所有交互指标都显著提升，也不等同一笔只能指一个空间连通块。 |
| R2-C22 · [Online Bayesian Goal Inference for Boundedly-Rational Planning Agents](https://proceedings.neurips.cc/paper/2020/file/df3aebc649f9e3b674eeb790a4da224e-Paper.pdf)（2020） | 相关正文 | 把行动者建模为有限计算、会重新规划的主体，可比完美最优假设更好解释部分回溯行为与在线目标判断。 | 选笔训练应覆盖合理但非最优行为；不把每笔都在最大错误中心写成真实用户的理性定律。 限制：结果来自可明确枚举规划状态与目标的受控任务；医学笔迹成本和医生知识无法自动从这些条件继承。 |
| R2-C23 · [Continual Adaptation for Efficient Machine Communication](https://aclanthology.org/anthology-files/pdf/conll/2020.conll-1.33.pdf)（2020） | 相关正文 | 人与模型重复协作指代时，利用互动反馈持续适应可提高交流成功率和效率；训练更新使用了游戏内可观察的目标反馈。 | 先采用训练时学好的历史编码；测试不在线改权重，也不隐式使用真实目标标签。 限制：不能把带真目标反馈的在线学习照搬成没有 G 的测试时分割训练；不同反馈条件的性能不应直接比较。 |
| R2-C24 · [Characterizing the Dynamics of Learning in Repeated Reference Games](https://onlinelibrary.wiley.com/doi/full/10.1111/cogs.12845)（2020） | 相关正文 | 重复共同指代可形成更简短的表达，表达如何收敛受互动历史与反馈影响。 | 允许历史影响当前笔的解释，但不给短笔、长笔或重复笔硬编码固定范围语义。 限制：重复语言的缩短是在伙伴共享同一已知对象集合的条件下发生；笔迹长短未必具有相同语用含义。 |
| R2-C25 · [From Partners to Populations: A Hierarchical Bayesian Account of Coordination and Convention](https://cocosci.princeton.edu/papers/hawkinspartners.pdf)（2023） | 相关正文 | CHAI 把快速伙伴特异的共同知识与较慢的群体约定区分，结合新行为数据与模拟解释重复交流和跨伙伴迁移。 | 通用训练覆盖多种选笔策略，单个病例仅保留短期可观察历史；避免把一种模拟器风格当成所有用户约定。 限制：模型使用具体词义空间、备选表达和自由参数；同一个五轮医学病例不足以验证群体约定形成。 |
| R2-C26 · [Learning and Transfer: A General Role for Analogical Encoding](https://groups.psych.northwestern.edu/gentner/papers/GentnerLoewensteinThompson03.pdf)（2003） | 相关正文 | 实验 2 的谈判案例学习中，明确比较两案例与分别学习的条件，应用所教谈判原则到新任务的比例分别为 48% 和 19%。 | 把关系显式作为训练信息有启发；配对约束应由任务标签变换推导，并在同一强组合中实现，收益由 SIRB 数据决定。 限制：不是深度网络实验；没有比较只差一个因素的样本对与其他差异数量，也没有推出预测差分损失或最佳损失权重。 |
| R2-C27 · [A Time for Telling](https://aaalab.stanford.edu/papers/time_for_telling.pdf)（1998） | 相关正文 | 先分析对照案例再接受讲解，可帮助学生形成后续理解和迁移所需的区分；不同教学顺序的优势依具体测试而定。 | 确保训练里存在需要区分的 T 与相似 O/P，而非仅给同质样本；不引入昂贵的课程阶段来复制课堂结构。 限制：实验中的新预测百分比是特定教育评价量，不能当成成对机器学习泛化增益的量级。 |
| R2-C28 · [A Memory of Errors in Sensorimotor Learning](https://pmc.ncbi.nlm.nih.gov/articles/PMC4506639/)（2014） | 相关正文 | 运动系统会根据过去误差的局部统计规律调节对误差的敏感度；重复相关误差与反复改变方向的误差可诱导不同学习。 | 历史输入保留模型实际编辑与当前区域关系；不根据 ADD/REMOVE 序列硬设学习率或范围伸缩。 限制：同号医学笔是操作类别，不等于在同一控制目标下经历的同符号运动误差；目标切换会改变解释。 |
| R2-C29 · [Relevance of Error: What Drives Motor Adaptation?](https://pmc.ncbi.nlm.nih.gov/articles/PMC2657056/)（2009） | 相关正文 | 运动适应不能简单正比于误差大小；把误差归因为与自身控制相关或无关，可解释部分非线性反应。 | 对每个候选预测具体收益和越界风险，而非统一提高门槛或按体积一律惩罚。 限制：不能推出大编辑默认有害；真实大病灶残差可能需要大范围修复。 |
| R2-C30 · [Interacting Adaptive Processes with Different Timescales Underlie Short-Term Motor Learning](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.0040179)（2006） | 相关正文 | 快而易忘、慢而持久的适应过程可以解释短期运动学习中的自发恢复等现象。 | 只保留长程权重学习与病例短历史的概念区分，当前实现用简单历史分支即可。 限制：行为时间尺度与五轮分割交互不一致；不能仅据此新增双记忆网络或预期特定 D2–D5 增益。 |
| R2-C31 · [Estimating the sources of motor errors for adaptation and generalization](https://www.nature.com/articles/nn.2229)（2008） | 原摘要＋索引结果 | 以误差可能来自身体还是外部环境的估计，解释适应及其跨动作条件泛化。 | 把笔意图歧义与模型图像判断错误分开讨论；不能把所有改过头都归于用户指代推断失败。 限制：本文具体动力学模型未在本轮完整复核；物理误差源不等于分割中的目标范围。 |
| R2-C32 · [Optimal feedback control as a theory of motor coordination](https://www.nature.com/articles/nn963)（2002） | 原始摘要 | 最优反馈控制强调对任务相关偏差的选择性纠正，而非强迫所有状态轨迹完全相同。 | 保留区和被授权范围必须写进任务目标；可借选择性纠错原则，不复制未经校准的闭式控制系数。 限制：任务效用的定义先于控制规则；不能从该理论直接推出当前 Dice 的某个固定门槛。 |
| R2-C33 · [The Effects of Feedback Interventions on Performance: A Historical Review, a Meta-Analysis, and a Preliminary Feedback Intervention Theory](https://doi.org/10.1037/0033-2909.119.2.254)（1996） | 原摘要＋同作者总结；元分析 | 原摘要报告 607 个效应、23,663 次观察、总体 d=0.41；超过三分之一的反馈干预效应为负。 | 只保留反馈可能伤害表现的背景警示；具体应保留区域由 SIRB 标签与本地改过头证据确定。 限制：精确 38% 在旧文献记录明确来自二手片段；不同反馈类型、任务和干预条件的异质性不能推导医学保留样本比例或损失结构。 |
| R2-C34 · [The Power of Feedback Revisited: A Meta-Analysis of Educational Feedback Research](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.03087/full)（2020） | 相关正文；元分析 | 435 项研究、994 个效应的整体加权 d=0.55，17% 效应为负；剔除 35 个极端效应后 d=0.48。不同反馈类型效果不同。 | 支持检查反馈是否给出有用区分信息；不据高信息量反馈的 d 值设 loss 权重或声称成对监督必然提升。 限制：旧摘要把 d=0.48 与原始样本的 17% 并列而未说明口径；效应量类型和临床 Dice 完全不同，不能据此预估收益。 |
