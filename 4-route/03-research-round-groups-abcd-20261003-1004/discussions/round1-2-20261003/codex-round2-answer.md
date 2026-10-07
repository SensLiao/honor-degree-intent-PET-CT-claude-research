**我最看好的三个机制是：S1 的状态条件循环传播、S2 的保留初始指代参照的 query 迭代，以及 S7 与反事实过程监督结合的训练。** 它们分别解决“怎样沿对象找到完整范围”“怎样从局部提示形成更完整的对象表示”“怎样在真实失败状态上学会正确调整范围”。

但三者的执行顺序不必与科学价值排序相同：**训练侧先强化 a、l 和有效的状态干预监督；结构侧先试便宜的 S2，再决定是否投入全卷 S1。** 第一轮推荐的早融合 c 仍值得保留，作为强对照。S1、S2 必须证明自己比“让普通卷积更早看到笔划”多解决了什么。

这轮跨领域调研也让我更明确地反对三个直接迁移：

- **“连通性需要循环”不是对所有现代网络成立的定理。** 循环提供的是适合逐步传播的计算方式和参数复用，当前证据不足以宣布 SIRB 的前馈主干存在不可突破的连通性上限。
- **“第二笔意味着更大胆”不是普遍成立的决策规则。** 第二笔可能要求补全，也可能要求撤回上次误改，或指向另一处错误。
- **CFG 不能制造模型原本没有提取到的指代信息。** 远端的有笔／无笔预测如果相同，放大两者差值仍然没有作用。

以下用 **【文献事实】、【数学推演】、【项目事实】、【研究建议】** 区分证据身份。所有 D5 收益范围都是研究规划估计，**没有任何一项已经在 SIRB 上得到实验验证，也不能把各项上限相加**。全程没有连接服务器、修改文件或下载论文到本机。

---

**一、跨领域最值得借的，不是模块名字，而是五种可操作的关系。**

| 跨领域来源 | 核对到的内容 | 对 SIRB 有用的迁移 | 不能直接迁移的部分 |
|---|---|---|---|
| 指代沟通、联合注意 | 理解指代需要利用交流双方共享的场景与上下文；指代可以通过后续交流修正 | 将 image、当前 M、笔划和既往编辑共同作为指代上下文；在同场景的竞争对象之间判断“指谁” | “人有联合注意”不能证明一个 attention layer 已具备同类能力 |
| 语用学、RSA | 听话人可以依据“说话人为什么选择这个表达”反推目标 | 在训练中学习笔划与候选目标的相容性，尤其是相似错误之间的区分 | 模拟器不自动等于理性说话人；“最大错误”策略可能成为捷径 |
| 视觉神经科学 | 对象内注意、逐步成组、路径追踪支持按关系传播的计算思想 | 将局部指代种子扩展为状态条件的对象范围，并在状态改变后重新计算 | 人类反应时和神经活动不能直接换算为网络迭代次数或 Dice 收益 |
| 教育学、从错误中学习 | 有效练习需要针对能力缺口、反馈与可学习性；高置信错误在得到反馈后可能更容易被纠正 | 训练真实失败状态，区分错误类型，并选择仍有学习进展的样本组 | 不能把“最高置信的错误”一律当成最值得训练的样本 |
| LLM、模仿学习、对象中心学习 | 自身状态访问、迭代表示更新、偏好比较、过程反馈都有成熟机制 | 将其落实为 TRAIN 回放、竞争式对象表示、同状态换笔／同笔换状态监督 | 不必引入 LLM、RLHF 或 diffusion 全套训练，才能借用这些思想 |

【文献事实】Clark 与 Wilkes-Gibbs 的指代沟通实验强调，双方会修正、扩展或替换表达，直到形成可接受的指代。Frank 与 Goodman 将简单指代游戏建模为信息性表达与 Bayesian 推断。更接近视觉任务的是 Fan 等人的绘图指代实验：人在相似干扰对象存在时，会改变画法以增加区分信息。[Clark & Wilkes-Gibbs，1986](https://web.stanford.edu/~clark/1980s/Clark,%20H.H.%20_%20Wilkes-Gibbs,%20D.%20_Referring%20as%20a%20collaborative%20process_%201986.pdf)、[Frank & Goodman，2012](https://web.stanford.edu/~ngoodman/papers/FrankGoodman-Science2012.pdf)、[Fan 等，2019](https://arxiv.org/pdf/1903.04448)

对我们最有用的启发是：**笔划应在“其他可能指代对象也在场”的情况下被理解。** 当前只强调 T 的覆盖，还不够检验这一点；需要给出外观、距离、体积相近的 O，要求模型随笔划正确交换选择。

在继续讨论之前，先回应导演说的“scribble 可能不起作用，就只用意图”。

【数学推演】可以把 scribble 转成更好的 latent intent（内部意图表示），但不能无条件删掉识别目标所需的信息。设当前可观察上下文为 \(C=(X,M,H,\text{sign})\)，有两个可能的目标 \(R_1,R_2\)。若两次任务的 \(C\) 完全相同，只是用户心里想改的对象不同，那么没有额外提示的确定性模型只能给出相同输出。

更一般地，如果

\[
I(R;I_{\mathrm{input}}\mid C)=0,
\]

即输入的“意图”没有提供区分目标的信息，模型就只能依赖先验猜测；在 \(K\) 个等概率候选的对称例子里，选对率最多是 \(1/K\)。

因此有三种不同研究：

- **保留 scribble 的信息，改进其表示和解释方式**：仍在当前任务内，最适合现在做。
- **让用户提供对象名称、解剖位置、候选编号或更明确的修改范围**：合理，但新增了交互信息，是另一个提示预算。
- **完全不给目标线索，让模型自己挑最该修的错误**：转成自动错误选择，不再单独检验用户指代理解。

我推荐第一种。把笔划当作**指代证据**，不必把它当作必须局限修复范围的几何模板。

---

**二、S1：值得优先研究，但应改成“循环传播提供合适的计算结构”，而非“前馈网络不可能计算连通性”。**

【文献事实】Minsky–Papert 的相关限制针对受约束的有限阶谓词／感知机模型及随输入规模增长的连通性问题，不是现代多层 U-Net、全局 attention 的普遍不可能性定理。Linsley 等人的 Pathfinder 实验显示 hGRU 在所测设置中具有很强的参数效率；原文也有表现接近的较大前馈网络，包括 U-Net。[Minsky–Papert 原始论述存档](https://dailypapert.com/linearly-unrecognizable-patterns/)、[hGRU 原论文](https://papers.nips.cc/paper/2018/file/ec8956637a99787bd197eacd77acce5e-Paper.pdf)

Egly 等的经典工作支持对象因素影响注意转移；Roelfsema 与 Houtkamp 的 incremental grouping 理论进一步提出，注意可沿已建立的联系逐步扩展。Ullman 的 visual routines 则提供从基础视觉表示出发执行任务相关操作的计算框架。它们是设计动机，不能直接证明病灶错误区域也服从同一机制。[Egly 等原文索引与 PDF](https://www2.psychology.uiowa.edu/faculty/hollingworth/prosem/Egly_etal_94_JEPG_ShiftingVisualAttention.pdf)、[Incremental grouping](https://pmc.ncbi.nlm.nih.gov/articles/PMC3222807/)、[Ullman 作者章节](https://courses.csail.mit.edu/6.803/pdf/ullman9.pdf)

**数学上真正成立的是局部传播的范围约束。**

设每个体素是图上的节点，\(A_{uv}\) 表示相邻节点是否属于可传播的同一对象，\(s_v\) 是笔划种子。对于二值正确邻接图，定义：

\[
h_v^{(0)}=s_v,
\]

\[
h_v^{(k+1)}
=
\max\left(
h_v^{(k)},
\max_{u\in\mathcal N(v)}A_{uv}h_u^{(k)}
\right).
\]

【数学推演】用归纳法可知：\(h_v^{(K)}=1\)，当且仅当 \(v\) 能在不超过 \(K\) 条有效边内从种子到达。

这说明：

- 一次只交换相邻信息的模块，传播距离受迭代次数约束。
- 固定次数的循环也不能处理任意长路径。
- 多尺度边、长距离边或全局操作可以缩短所需步数。
- 循环展开后也是一个深网络；主要优势是共享参数与允许增加计算步数，不是获得前馈计算绝对没有的能力。

**连续亲和度有一个很容易忽略的问题：越传播越弱。**

若把 \(A_{uv}\) 换成 \([0,1]\) 的预测值，上式会得到路径边权乘积的最大值。32 条边的简单数值例子为：

\[
0.9^{32}\approx0.034,\qquad
0.95^{32}\approx0.194,\qquad
0.99^{32}\approx0.725.
\]

这些数字已作纯 CPU 算术核对。即使每条正确边都有 0.95，远端值也会降得很低。**直接把扩散结果当 \(p_T\) 再用 0.5 截断，可能重新制造远端漏修。**

另一种带 restart 的线性传播：

\[
h^{(k+1)}=(1-\alpha)s+\alpha P_\theta h^{(k)},\quad 0<\alpha<1,
\]

若 \(P_\theta\) 为适当归一化的非负矩阵，可以有稳定的不动点：

\[
h^*=(1-\alpha)(I-\alpha P_\theta)^{-1}s.
\]

但它表示的是扩散访问强度，不是“属于目标”的校准概率；距离衰减、跨边界泄漏仍然存在。

【研究建议】在 flat 上，更合适的是：

\[
A_\theta=A_\theta(F,M,\text{sign},q),
\]

\[
h^{(k+1)}=\Phi_\theta(h^{(k)},A_\theta,s,F),
\]

\[
(u_T',u_O')
=
(u_T,u_O)+R_\psi(F,h^{(K)},q).
\]

把传播状态当作补充特征，由零初始化的残差输出接回两个 flat logits，保留原执行器。不要用当前 flat 的低 \(e\) 做硬传播门，否则当前漏检可能再次成为不可跨越的障碍。

它成立需要四个条件：

1. 亲和度学习的是**当前同向错误对象内部关系**，而不只是 PET 强度相似。
2. 状态断桥后，相关连接或传播结果确实改变。
3. 所需桥和细结构在输入网格上可见。
4. 推理时能跨 tile 交换传播状态；各块独立扩散不能支持全对象传播的主张。

【项目事实】远端恢复差是已记录短板，但此前患者等权分解没有支持“远端解释全部缺口”。因此我的单次 8k 工作预期仍是 **0–2 个 D5 点，低至中等把握**，不是循环一加就能补齐 4–5 点。

**最便宜验证：**先冻结父模型特征，在固定 TRAIN 片段上检验新增传播头能否拟合“相同欧氏距离、不同连通关系”的样本；这只是机制原型。通过后再做完整 8k 续训和 VAL。

**机制指标：**

- 固定欧氏距离，按目标内路径长度分层的召回。
- \(K=1,4,8,\ldots\) 增加时，正确远端恢复是否提高，同时 O/P 泄漏受控。
- 同一笔、断桥前后，远侧 T→O 区域是否退出当前目标。
- 相同计算预算的普通空间支路能否获得相同收益。

此外，**学习亲和度并传播早已有直接视觉先例**，如 Spatial Propagation Networks。潜在贡献必须落在状态干预引起的关系变化及指代限制上。[SPN 原论文](https://arxiv.org/pdf/1710.01020)

---

**三、S2：最值得先做的小型结构实验，但“预测加权平均”只有在特定模型下才是 EM。**

【文献事实】Slot Attention 使用 slots 之间的竞争分配、加权聚合和 GRU 更新；论文将它与 soft k-means 联系起来，但并未把任意神经更新都称为具有单调似然保证的 EM。Mask2Former 则用预测 mask 限制 cross-attention 的区域。这两者都比“把一个 query 做三次均值”更有结构。[Slot Attention](https://arxiv.org/pdf/2006.15055)、[Mask2Former](https://arxiv.org/pdf/2112.01527)

用户给出的式子：

\[
q^{(k+1)}
=
\frac{\sum_v p_T^{(k)}(v)F(v)}
{\sum_v p_T^{(k)}(v)}
\]

需要先补两个条件：

- 当前 \(F\) 是 32 维、\(q\) 是 128 维，必须先投影到共同空间。
- \(p_T\) 必须有明确的分配含义，否则它只是启发式权重。

设 \(z_v=W_FF(v)\)，并假设特征由若干球形 Gaussian 成分生成：

\[
p(z_v)=\sum_j\pi_j\,
\mathcal N(z_v;\mu_j,\sigma^2 I).
\]

E-step 为：

\[
r_{vj}
=
\frac{\pi_j\exp[-\|z_v-\mu_j\|^2/(2\sigma^2)]}
{\sum_l\pi_l\exp[-\|z_v-\mu_l\|^2/(2\sigma^2)]}.
\]

M-step 为：

\[
\mu_j'=\frac{\sum_vr_{vj}z_v}{\sum_vr_{vj}}.
\]

【数学推演】在固定特征、正确执行上述 E/M 两步的条件下，可以讨论相应似然的单调改进。但这仍不意味着 Dice 单调提高。若换成现有任意 \(p_T\)、GRU、残差网络，原 EM 保证不自动保留。

**对 SIRB 更重要的是保留笔划确定的初始对象身份。**

可以给目标原型一个以 \(q_0\) 为中心的先验，得到：

\[
q_T^{(k+1)}
=
\frac{\lambda q_0+\sum_vr_{vT}^{(k)}z_v}
{\lambda+\sum_vr_{vT}^{(k)}}.
\]

这里 \(q_0\) 来自当前笔划，不能被第一次不完整预测轻易覆盖。可以同时维护一个干扰表示，与 T 竞争；P 仍由 flat 原有表示保护。一个 O 原型只能是最小试验，因为“其他错误”可能有多种完全不同的外观。

为什么需要这个参照？假设更新权重中混入比例为 \(\epsilon\) 的其他对象特征：

\[
\mathbb E[\hat q]
=
(1-\epsilon)\mu_T+\epsilon\mu_O.
\]

则：

\[
\mathbb E[\hat q]-\mu_T
=
\epsilon(\mu_O-\mu_T).
\]

【数学推演】错误区域越多、与目标特征差越大，原型漂移越大；下一轮错误分配又可能加重漂移。这是自我强化，不是自动纠错。笔划参照、竞争对象、软范围限制和停止条件都是为控制这个问题。

还有一个陷阱：**若只在当前高置信 T mask 内聚合，完全漏掉的远端永远不能进入更新。** 需要允许少量低置信区域参与，或者使用较软的 mask attention，而不是把旧预测变成永久搜索边界。

【项目事实】当前 query 已经有两层 cross-attention，并非完全没有全局更新。S2 新增的应是**由预测对象范围反馈来更新 query**，而不是再堆两层普通 attention。[当前 query 实现](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_network.py:243>)

【研究建议】预期 **0–1.5 个 D5 点，低至中等把握**。它比 S1 更便宜，也更容易从 v1 续训；但对于“外观相同、连通关系不同”的目标，单一原型可能仍然不够。

**最便宜验证：**固定同一父模型，比较一次预测、三次保留参照的更新、三次不保留参照的更新。先在固定 TRAIN 状态验证，再将合格实现做 8k。

**机制指标：**

- 每次迭代的 T 覆盖、O 泄漏及净误改。
- 遮掉目标远端的初始预测后，是否能恢复它。
- 有相似干扰病灶时，query 是否漂向干扰对象。
- 同状态换笔后，最终区域能否换到对应对象。
- 增益是否在第 2、3 次更新发生，而不是仅来自新增参数。

缓存结论要限定：**同一状态、同一权重下**可以复用主干特征。M 改了、训练权重更新了，就不能继续用旧缓存。若采用早融合 c，换笔也需要重新编码；S2 的缓存优势会减少。

---

**四、S3：Bayesian 解释成立，完整 RSA 暂不优先；更值得先做“竞争对象下的笔划相容性”。**

【数学推演】给定上下文 \(C=(X,M,H,\text{sign})\)：

\[
P(R\mid S,C)
\propto P(S\mid R,C)P(R\mid C).
\]

这是普通 Bayes 公式。要成为 RSA，还需要一个说话人选择模型，例如：

\[
S_1(S\mid R,C)
\propto
\exp\{\alpha[\log L_0(R\mid S,C)-c(S)]\},
\]

\[
L_1(R\mid S,C)\propto S_1(S\mid R,C)P(R\mid C).
\]

其中 \(c(S)\) 是表达成本，\(L_0\) 是基础听话人，\(L_1\) 才是在推断说话人选择的听话人。

**当前模拟器是一个已定义策略，不必把它假设成理性说话人。** 更准确的形式是：

\[
P(S\mid R,C)
=
\sum_zP(S\mid R,C,z)P(z\mid C),
\]

\(z\) 表示不同画法或选目标策略。

成立的条件包括：

- 推理时的候选 \(R\) 由可观察输入预测，不能直接用真实错误连通块。
- 训练时可以用 GT 构造目标和笔划；推理时不能调用需要 GT 的模拟器算 likelihood。
- 对不同画法做边缘化或稳健训练，而不是猜到 roster 的具体画法就获得优势。

【项目事实】当前编码已经包含笔划采样特征、位置和范围，不能说它只知道“碰到哪里”。但 mean/max 聚合确实不保证保留全部形状结构。补充长度、主方向、几何覆盖可能有用，也可能只是学到模拟器的画法规律。

**最大风险是错误先验压过当前指代。** 如果 \(P(R\mid C)\) 太偏向最大错误，模型会在笔划指别处时仍选最大块。这样的分数提升不能支持“理解意图”。

【研究建议】先不做完整 RSA。用同状态下两个难区分的错误候选，训练：

\[
g_\theta(S,R_{\mathrm{true}},C)
>
g_\theta(S,R_{\mathrm{other}},C).
\]

再比较只用位置、位置加形状、再加候选竞争的区别。这个实验不必引入一个语言模型。

预期 **0–1 点 D5，把握低**；相较 D5，目标选择准确率可能更先改善。

**最便宜验证：**固定状态，匹配候选体积与离笔距离，观察笔划形状是否仍增加区分信息。若没有，就不为 RSA 增加复杂生成模型。

**机制指标：**同状态目标选择准确率、换画法稳定性、不同选择策略下的排序稳定性，以及“选择最大块”先验被当前笔划纠正的能力。

Fan 等的视觉沟通研究支持在干扰对象背景下理解绘图，但它研究的是人类绘图指代，不是当前三种模拟涂鸦的直接效果证据。[视觉语用研究](https://arxiv.org/pdf/1903.04448)

---

**五、S4：应改为“识别修复反馈类型”，不要预设第二笔就扩大修改。**

【文献事实】对话修复包括对表达的扩展、替换和澄清，不只有增加力度。Self-Refine 则把当前输出、具体反馈与后续修订结合起来；它并不保证重复运行同一个模型就单调改善。[指代修复](https://web.stanford.edu/~clark/1980s/Clark,%20H.H.%20_%20Wilkes-Gibbs,%20D.%20_Referring%20as%20a%20collaborative%20process_%201986.pdf)、[Self-Refine](https://arxiv.org/pdf/2303.17651)

【数学推演】历史是否值得加入，取决于它在当前状态和笔划之外是否提供额外信息：

\[
I(R_t;\mathcal H_t\mid X,M_t,S_t,\text{sign}_t)>0.
\]

如果任务目标完全由当前 \(M_t\)、GT 与当前笔划定义，历史并不改变目标定义；它可能帮助模型估计隐藏的错误结构和此前失败方式，但不能自动推出应修改更多。

建议明确区分：

\[
z_t\in\{\text{补全上次目标},\text{撤回误改},\text{转向新目标}\}.
\]

可观察输入包括：

\[
\Delta M_{t-1}^{+}=M_t\setminus M_{t-1},
\qquad
\Delta M_{t-1}^{-}=M_{t-1}\setminus M_t,
\]

以及上一笔、当前笔与这些变化的关系。

部署时这些都是已有操作记录，不需要 GT。但“确实是同一个错误”只在 TRAIN 监督／离线分析中能由标签确认；推理时必须估计，不能把真实目标 ID 当输入。

**更合理的升级方式是增加推理计算或改变关注区域，不是统一降低阈值。** 例如判断为补全时增加 S1/S2 的迭代次数；判断为撤回时重新检查上次变化区域；判断为新目标时重置对象表示。

【研究建议】预期 **0–1 点 D5，把握低至中**，主要取决于 flat 的重复残留事件占比及其可修空间。它不应仅靠 N3 的无编辑次数来排优先级。

**最便宜验证：**先用既有 TRAIN 轨迹，看“上一轮编辑关系”能否在当前状态特征之外预测下一轮失败类型，再决定是否加网络支路。

**机制指标：**

- 重复残留事件的下一步恢复量。
- 已经正确的区域被再次破坏的比例。
- 新目标被历史错误牵制的比例。
- 与“每次都多迭代同样次数”的等计算对照比较。

这项若有效，论文主张应是**利用交互反馈重新分配修复计算**，而不是“模型第二次更听话”。

---

**六、S5：整体对象偏向可以转成目标完整性约束；时间上的互斥不适合当前任务。**

【文献事实】Markman 与 Wachtel 研究的是儿童如何利用词义假设减少解释空间。互斥也会引导儿童把新词解释为部分或材料，而非绝对坚持“一物一词”。它不是禁止重复指代的通用规则。[Markman & Wachtel 原论文](https://www.sciencedirect.com/science/article/pii/0010028588900175)

**“整对象”在我们这里必须指完整错误对象，而非整块病灶。**

设一处病灶已有部分正确分割，剩下两片互不连通的漏分。当前任务若只指其中一片，那么把整个病灶的所有漏分都补上可能提高 Dice，却不一定符合本笔的 operational target（任务规定的修改对象）。

【数学推演】硬性的“新笔不许选择曾被选过的对象”会给重复残留的目标先验赋零：

\[
P(R_t=R_{t-1}\mid H_t)=0.
\]

如果上一次只修了一部分，这条约束直接排除了正确答案。因此不能用。

可保留的是：

- **空间竞争**：同一次交互中区分 T、O、P。
- **完整恢复偏向**：当某区域被判为当前目标时，不应只覆盖提示附近。
- **已正确部分保护**：依据当前状态与图像判断，而非仅因历史上改过就永久锁定。

【研究建议】S5 不应单开网络模块。并入 S1/S2 的对象完整性和竞争式表示，或并入第一轮的区域监督 i。独立增益预期 **0–0.5 点，低把握**。

**最便宜验证：**在同一监督预算下，加入对象级 coverage 目标，并同时检查非目标误改；不加入历史排斥。

**机制指标：**目标完成率、反复残留次数、同一病灶内不同错误块的混淆。若 D5 上升只是因为把更多未被指的错误也顺手改了，不能归为指代理解改善。

---

**七、S6：可做小型实验，优先级低于 S1/S2；它解决条件响应强度，不解决缺失的对象推理。**

【文献事实】原始 CFG 联合训练有条件与无条件模型，再组合其预测。LLM 中也已有将 CFG 用于条件／无条件 token 分布的工作，因此这个思想并不限于 diffusion。[Classifier-Free Diffusion Guidance](https://arxiv.org/pdf/2207.12598)、[Stay on Topic with Classifier-Free Guidance](https://arxiv.org/pdf/2306.17806)

为了避免 flat 两个 logits 的含义混乱，先考虑二分类目标 log-odds：

\[
\ell_S(v)=\log\frac{p_T(v\mid S,C)}{1-p_T(v\mid S,C)},
\quad
\ell_\varnothing(v)=
\log\frac{p_T(v\mid C)}{1-p_T(v\mid C)}.
\]

指导后：

\[
\ell_w=\ell_\varnothing+
w(\ell_S-\ell_\varnothing)
=
\ell_S+(w-1)\Delta\ell.
\]

这里 \(w=1\) 是原条件预测。

【数学推演】是否能救回一个漏修体素，直接由 \(\Delta\ell\) 决定：

| 情形 | 例子 | \(w=2\) 后 |
|---|---|---|
| 有笔已增加目标证据，但尚未过阈值 | \(\ell_S=-1,\ell_\varnothing=-2\) | \(\ell_w=0\)，可能刚好执行 |
| 远端根本没有笔划响应 | \(\ell_S=\ell_\varnothing=-2\) | 仍为 −2，没有改善 |
| 有笔错误增强了背景 | \(\ell_S=-0.2,\ell_\varnothing=-3\) | 变为 2.6，误改显著增强 |
| 目标处有笔反而抑制预测 | \(\Delta\ell<0\) | 放大指导会使漏修更严重 |

对三类 flat logits 同时组合时：

\[
\tilde p_w(y\mid S,C)
\propto
\frac{p(y\mid S,C)^w}
{p(y\mid C)^{w-1}}.
\]

这是条件信息相对先验的增强；不是简单把 T 全部抬高。

**最难的部分在“无笔”究竟学什么。**

目标 T 由笔划决定。丢掉笔划以后：

\[
p(y_v=T\mid C)
=
\sum_Rp(y_v=T\mid R,C)p(R\mid C).
\]

它应是对未知指代对象的边缘分布，而不是所有体素都不修改。若 null 分支被训练成全零 T，减去它会产生很大的数值提升，但失去上述概率解释。

实施还必须满足：

- 当前笔划的位置编码、采样点、距离图、occupancy 等都要一起隐藏，不能只擦一张图。
- “训练时隐藏条件”与“用户真的没有给提示”分开。真实空提示仍应按既有执行语义不修改。
- 当前 balanced losses 得到的概率不保证校准；即使形式正确，Bayesian 解释也只能近似成立。
- 需要同状态多目标的训练，避免 null 分支学成“默认选择最大错误”。

【研究建议】预期 **0–0.8 点 D5，把握低**；也可能显著增加误改。建议先在固定 TRAIN 状态检查 \(\Delta\ell\) 在 T、O、P 中的分布。如果远端 T 与 O/P 的差值不可分，直接停止，不进入大规模 guidance 搜索。

**最便宜验证：**训练一个最小 null 条件版本后，只比较预定的 \(w=1\) 与一个温和增强值；入选后必须重新跑五轮，而不是仅扫描旧轨迹的阈值。

**机制指标：**分距离的 T/O/P 条件差值分离、净修复／误改、各轮状态变化。必须证明它增强的是正确指代证据，而不是统一放大编辑量。

---

**八、S7：值得做，但应从“最高置信错误优先”改成“可靠、重要且可学的失败优先”。**

【文献事实】Hypercorrection effect 指人对部分高置信错误在获得正确反馈后有较高的纠正概率。后续研究讨论了注意和既有部分知识等解释。它不证明神经网络的最高置信错误都是最好学的样本。[作者团队的儿童实验](https://www.columbia.edu/cu/psychology/metcalfe/PDFs/MetcalfeFinn2012.pdf)

“最近发展区”与 Metcalfe 的 Region of Proximal Learning 也不应混为同一个精确定律。可迁移的共同思想是：在尚未掌握、但仍可取得进步的内容上分配时间。Graves 等的 automated curriculum 已把学习进展用于任务抽样。[Metcalfe，2002](https://columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%202002.pdf)、[Graves 等，2017](https://proceedings.mlr.press/v70/graves17a/graves17a.pdf)

**先看它与现有 loss 的区别。**

对于二分类 CE：

\[
\frac{\partial L_{\mathrm{CE}}}{\partial z}=p-y.
\]

高置信错误的梯度已经接近最大幅度。Focal loss：

\[
L_{\mathrm{focal}}=-(1-p_y)^\gamma\log p_y
\]

主要进一步降低容易正确样本的相对权重。OHEM 选择高损失样本；经典 self-paced learning 通常先纳入低损失样本，再逐渐扩大范围。[Focal Loss](https://arxiv.org/pdf/1708.02002)、[OHEM](https://openaccess.thecvf.com/content_cvpr_2016/html/Shrivastava_Training_Region-Based_Object_CVPR_2016_paper.html)、[Self-Paced Learning](https://ai.stanford.edu/~koller/Papers/Kumar%2Bal%3ANIPS10.pdf)

因此，“高置信错误加权”与 OHEM／focal 有较大重叠，单独创新有限。

【研究建议】更合适的训练组评分是：

\[
\text{priority}_g
\propto
\underbrace{\text{任务缺口}_g}_{需要改善}
\times
\underbrace{\text{标签及输入可辨识性}_g}_{确实可学}
\times
\underbrace{\text{近期学习进展}_g}_{继续练有用}
\div
\underbrace{\text{计算成本}_g}_{花多少资源}.
\]

这是建议的选样原则，不是已证最优公式。第一版不要训练一个复杂 teacher，先用少量固定组：

- 大 ADD 的不完整修复；
- 近距离同向 O 的错误绑定；
- 自然可见断桥后的范围改变；
- 模型新引入的错误；
- 已经稳定修好的常规样本。

所有组保留最低抽样概率，避免只练困难样本后遗忘正常情形。置信度由冻结父模型或滞后版本提供，样本权重停止梯度并设上限。

一个有用的数学条件是：若抽样分布

\[
Q=\alpha D+(1-\alpha)Q_{\mathrm{hard}},
\]

其中 \(D\) 是希望覆盖的基础分布，非负损失满足：

\[
\mathbb E_D[\ell]\le \frac{1}{\alpha}\mathbb E_Q[\ell].
\]

【数学推演】这说明保留基础分布质量可以避免完全放弃某些区域；但它不是 D5 保证。若进行 importance weighting 可恢复原风险目标，不做则是在有意改变训练目标，两者应说清。

**五轮复合误差如何推？**

令 \(\pi\) 是编辑策略，\(d_t^\pi\) 是它第 \(t\) 轮实际访问的状态分布。

DAgger 相关分析区分了：

\[
\epsilon_{\mathrm{expert}}
=
\mathbb E_{d^{\pi^*}}\ell(\pi,\pi^*),
\]

与：

\[
\epsilon_{\mathrm{own}}
=
\mathbb E_{d^\pi}\ell(\pi,\pi^*).
\]

在规定的 bounded cost、动作错误等条件下，仅在专家状态上学，累计成本差可出现 \(O(T^2\epsilon)\)；若能控制自身访问状态上的错误，并有单次错误的后续成本上界 \(u\)，则可得到类似：

\[
J(\pi)-J(\pi^*)\le uT\epsilon_{\mathrm{own}}.
\]

对五轮，分别出现 \(25\epsilon\) 与 \(5u\epsilon\) 的量级；**如果 \(u\) 本身随剩余轮数增长，就没有自动获得从平方到线性的实际优势。** [DAgger 定理与条件](https://proceedings.mlr.press/v15/ross11a/ross11a.pdf)

迁到 SIRB 还要加三项限制：

1. 一个编辑动作是高维 mask，“动作是否完全一致”的错误率可能几乎总为 1，使界非常松。
2. 目标区域 Dice loss 不天然上界最终 D5 损失。
3. 当前只用冻结父模型状态池，不是不断聚合当前策略状态的完整 DAgger。

对固定回放池，更直接的描述是：若 \(0\le\ell\le1\)，

\[
\mathbb E_{d^\pi}\ell
\le
\mathbb E_Q\ell+
\operatorname{TV}(d^\pi,Q).
\]

这给出了“何时刷新状态池”的理论理由：新模型访问的状态若明显偏离旧池，旧池上学得再好也未必覆盖新失败。但总变差距离在这里难以准确估计，不能把几个残余体积统计当成它的精确数值。

【研究建议】相对普通回放，S7 的增量预期 **0–1 点 D5，中等偏低把握**。它与 a、l 很重叠，不能把三项分别算成独立收益。

**最便宜验证：**同父、同 8k、同样本预算，比普通分层回放与固定困难组配额；先不做持续在线自适应 teacher。

**机制指标：**困难组与普通组的共同改善、早晚轮错误、父模型高置信错误的纠正率、训练曝光、遗忘，以及是否只是提高了少数大体积患者的表现。

---

**九、补充方向：比直接套 DPO/RLHF 更合适的是“成对干预的过程监督”。**

这是我认为最值得加入 S7 的部分，也最贴近第一轮主张 A。

【文献事实】DPO 从带参考策略的偏好优化推出特定损失；随便写一个两个分数的 logistic ranking loss，不自动成为 DPO。过程监督研究则强调定位中间步骤的错误，但《Let’s Verify Step by Step》具体训练的是数学解答的 reward model，并未直接证明任意分割网络加中间监督都会改善。[DPO](https://arxiv.org/pdf/2305.18290)、[Process Supervision](https://arxiv.org/pdf/2305.20050)

我们已经有 TRAIN GT，能直接知道错误角色，没有必要先把精确标签降成粗偏好，再训练一个 reward model。

建议使用三类训练关系：

\[
\text{同状态、换目标笔划}
\Rightarrow
\text{选择应该交换},
\]

\[
\text{同目标、换合法画法}
\Rightarrow
\text{范围应基本一致},
\]

\[
\text{同笔划、改变状态}
\Rightarrow
\text{范围按角色变化而改变}.
\]

例如定义区域分数：

\[
g_\theta(R;S,M)
=
\frac1{|R|}
\sum_{v\in R}(u_T(v)-u_O(v)).
\]

对同状态中的两个同向错误 \(R_a,R_b\)，笔划 \(S_a\) 指向 \(R_a\)：

\[
L_{\mathrm{select}}
=
\operatorname{softplus}
\left[m-g_\theta(R_a;S_a,M)+g_\theta(R_b;S_a,M)\right],
\]

再加交换笔划后的对应项。

GT 区域在这里仅用于 TRAIN loss 和机制评估，不进入推理。若采用 S1，还可以监督“传播在哪类边界应停止”；采用 S2，则监督迭代后目标选择是否改善，而不要求每个内部向量都像人工指定的原型。

**与 v1 的区别必须写清：**v1 已有共同可编辑域上的变化与稳定约束。新增贡献应是竞争对象下的换笔关系、有效变化覆盖，以及关系监督与迭代推理的对应证据；不能把已有 state loss 换名字。[现有 state loss](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_losses.py:168>)

最便宜且最有解释力的对照是：**两组看到相同的单个状态、笔划和基础标签，只在是否利用正确配对关系上不同。** 这可以区分关系学习与单纯多看困难样本。

另一个可借方向是 diffusion 的局部编辑：RePaint、Blended Diffusion 将修改区域与保留区域区分开。对 SIRB，可借的是明确保护未授权区域的设计思想；它们通常已有用户提供的 mask，**恰好把我们最难的“范围从哪里来”问题作为输入给定了**，所以暂不值得直接换 diffusion 主干。[RePaint](https://arxiv.org/html/2201.09865v1)、[Blended Diffusion](https://openaccess.thecvf.com/content/CVPR2022/papers/Avrahami_Blended_Diffusion_for_Text-Driven_Editing_of_Natural_Images_CVPR_2022_paper.pdf)

---

**十、重新排序及 flat 上的最小设计。**

按“贴近指代理解、潜在方法贡献、D5 机会”综合排序：

| 排名 | 机制 | 主要回答什么 | 我给它的定位 |
|---|---|---|---|
| **1** | **S1：状态条件循环传播＋干预监督** | 当前笔所指范围怎样沿对象扩展，又怎样因状态改变而停止或缩小 | 科学潜力最高，工程风险也最高 |
| **2** | **S2：保留笔划参照的竞争式 query 更新** | 从局部提示怎样形成完整对象表示，且不漂到相似错误 | 最值得先做的低成本结构实验 |
| **3** | **S7＋成对过程监督** | 模型是否在真实、可辨识的失败上学会正确换目标与换范围 | 训练主线；和 a、l 合并设计 |
| 4 | S4 历史反馈分类 | 重复交互需要补全、撤回还是换对象 | 由重复失败的实际贡献触发 |
| 5 | S3 竞争对象下的语用相容性 | 笔划形状能否提供位置之外的指代证据 | 小型判别实验，暂不完整 RSA |
| 6 | S6 CFG | 已存在的条件证据能否被温和增强 | 后期小试，不能承担主创新 |
| 7 | S5 整体／互斥偏向 | 是否完整修复、是否与其他对象竞争 | 并入其他机制，不独立开线 |

新增参数和计算只能针对具体最小设计估算，不能给“hGRU”“EM”一个通用成本。下面采用当前 **32 维 dense feature、128 维 query、96³ tile、每步 8 个 tile 前向**的规模；数值是静态算术，不是 GPU 实测。

| 机制 | 最小 flat 设计 | 新增参数估计 | 每步额外计算与实际风险 |
|---|---|---:|---|
| **S1** | \(F:32\to8\) 投影，query 小投影，轻量相邻亲和度；18 邻域传播；两 logit 残差输出零初始化 | 简单亲和度约 **1.5k–5k**；若换完整多通道 GRU，会明显更多 | 每 tile 投影约 **0.23 GMAC**；8 维邻边比较约 **0.13 GMAC**；32 次传播约 **5.1 亿次邻边更新／tile**，8 tiles 约 **41 亿次**。传播更新不是等价的稠密卷积 MAC，主要可能受显存带宽与反传存储限制 |
| **S2** | 将 q 投影到 32 维；目标与干扰两个表示竞争；约 3 次软分配／聚合；保留 q₀；残差 logit 读出零初始化 | 线性与均值版本约 **6k–8k**；加 32 维 GRU 约 **12k–15k** | 一个 32→32 特征投影，加两表示、三次相似度与聚合，约 **1.25 GMAC／tile**，8 tiles 约 **10 GMAC**；未计已有头、归一化、反传与全卷读取 |
| **S7＋关系监督** | 复用 flat 输出，不新增推理模块；替换部分训练单元为换笔／换状态配对 | **0**，除非额外加辅助头 | 区域 loss 本身便宜；能否不增加主干前向取决于配对组织。v1 同状态换笔可以共享特征；早融合 c 下不能如此。真实状态池刷新成本另计 |

两点不能省略：

- **S1 的 32 次局部传播不是无限远。** 在 3 mm 网格上沿轴向相邻边是约 96 mm 路径，曲折路径仍受跳数限制。用粗网格加速之前，要检查是否抹掉细桥或制造假连接。
- **S2 的全卷聚合不是“两个训练块做完就自动一致”。** 若训练只聚合两个标签引导块，推理却聚合全卷，会产生新的分布差异。需要固定可复现的聚合域、合理的抽样权重或训练／推理一致的 token 方案。重叠 tiles 的体素也不能重复计权。

S1 推理若需要跨块传播，应使用全卷标量状态或等价的边界交换。S2 若每轮重新读取全部特征，可能放大当前 I/O 瓶颈。**参数少只能说明模型文件小，不代表训练和推理时间小。**

三项的最小实验与否证条件：

| 机制 | 最小实验 | 能支持设想的结果 | 应停止或降级的结果 |
|---|---|---|---|
| S1 | 同父 flat：原空间支路与循环传播，各 8k；同参数循环模型再测几个预定 K | 随 K 增加，长路径 T 恢复提高；断桥后远侧退出；同距离 O 不随之上升 | 只增加编辑体积；收益与路径无关；跨块失败；普通空间支路同成本已做到 |
| S2 | 同父 flat：一次更新与三次保留参照的更新；去参照版本可先作冻结特征诊断 | 后续更新补回初次遗漏目标，同时保持对象身份 | query 漂移、两表示塌缩、只提高高置信近端、全卷聚合成本抵消优势 |
| S7＋关系监督 | 曝光和单样本标签匹配，比较有无新增配对关系 | 同状态换笔与同笔换状态均改善，并转化为恢复／误改改善 | 只有训练 loss 更好；自然变化不改善；依赖合成断桥；D5 改善完全由过采样解释 |

**与第一轮 a、l、c 的关系：**

- **a 继续，l 并入曝光设计。** 它们提供真实、足量的练习对象。
- **c 保留作强结构对照。** 不预设跨领域机制一定优于早融合。
- **h 不再只是“加一个对比 loss”**，落实成上述干预关系与机制指标。
- **f 从笼统的远端补全，收紧成 S1/S2 两种可区分机制。**
- 暂不加入完整 DPO、RLHF、diffusion 或大规模候选实例网络。

我推荐的实际顺序是：**先等当前 a、b 结果；同父比较 c 与 S2；训练侧做曝光匹配的关系监督；只有长路径与自然断桥仍是明确缺口时，再做 S1。** 若导演更重视尽快验证核心创新，可以把 S1 的冻结特征小原型提前，但不能据原型失败就宣布循环方向无效。

---

**十一、值得精读的 PDF 链接。**

下表前两组是本轮已打开全文并核对相关方法、理论或实验部分的文献。并非逐页通读所有附录。没有保存到 `Thesis/sirb-research-20261003/`。

**优先存这 12 篇，直接服务于三个推荐机制。**

| 文献 | PDF 链接 | 精读重点 |
|---|---|---|
| Linsley 等，2018，hGRU | [NeurIPS PDF](https://papers.nips.cc/paper/2018/file/ec8956637a99787bd197eacd77acce5e-Paper.pdf) | Pathfinder 的实际对照、迭代次数、参数效率；不要扩写成普遍不可能性定理 |
| Liu 等，2017，Spatial Propagation Networks | [arXiv PDF](https://arxiv.org/pdf/1710.01020) | 学习亲和度、空间传播与 diffusion 的关系；明确 S1 已有先例 |
| Locatello 等，2020，Slot Attention | [arXiv PDF](https://arxiv.org/pdf/2006.15055) | Algorithm 1、跨 slot 竞争、加权均值、GRU，以及与 soft clustering 的区别 |
| Cheng 等，2022，Mask2Former | [arXiv PDF](https://arxiv.org/pdf/2112.01527) | 预测 mask 如何限制 attention；搜索范围与漏检的关系 |
| Ross 等，2011，DAgger | [PMLR PDF](https://proceedings.mlr.press/v15/ross11a/ross11a.pdf) | Theorem 2.1、2.2、状态访问分布、\(u\) 的条件 |
| Graves 等，2017，Automated Curriculum Learning | [PMLR PDF](https://proceedings.mlr.press/v70/graves17a/graves17a.pdf) | 用学习进展选任务，而不只是按当前难度排序 |
| Kumar 等，2010，Self-Paced Learning | [作者 PDF](https://ai.stanford.edu/~koller/Papers/Kumar%2Bal%3ANIPS10.pdf) | 样本选择变量与从易到难的目标；和 OHEM 的差别 |
| Lightman 等，2023，Let’s Verify Step by Step | [arXiv PDF](https://arxiv.org/pdf/2305.20050) | 过程监督具体监督了什么；哪些结论只针对 reward model |
| Frank & Goodman，2012，RSA | [作者 PDF，含补充材料](https://web.stanford.edu/~ngoodman/papers/FrankGoodman-Science2012.pdf) | 听话人、说话人、先验和信息性如何组成模型 |
| Fan 等，2019，视觉语用沟通 | [arXiv PDF](https://arxiv.org/pdf/1903.04448) | 相似干扰对象如何改变绘图；最接近我们“指谁”的跨领域实验 |
| Metcalfe，2002，Region of Proximal Learning | [作者 PDF](https://columbia.edu/cu/psychology/metcalfe/PDFs/Metcalfe%202002.pdf) | 学习时间如何分配到尚未掌握但可学习的内容 |
| Metcalfe & Finn，2012，Hypercorrection | [作者 PDF](https://www.columbia.edu/cu/psychology/metcalfe/PDFs/MetcalfeFinn2012.pdf) | 高置信错误、部分知识和纠正反馈之间的区别 |

**第二组用于评估后备方向和避免错误类比。**

| 文献 | PDF 链接 | 阅读目的 |
|---|---|---|
| Ho & Salimans，2022，CFG | [arXiv PDF](https://arxiv.org/pdf/2207.12598) | 条件 dropout、无条件分支的定义、指导强度与代价 |
| Sanchez 等，2023，Stay on Topic with CFG | [arXiv PDF](https://arxiv.org/pdf/2306.17806) | CFG 如何作用于离散输出概率；理解 S6 的 logit 推演 |
| Rafailov 等，2023，DPO | [arXiv PDF](https://arxiv.org/pdf/2305.18290) | 参考策略、偏好模型及推导条件；普通 ranking loss 为什么不等于 DPO |
| Madaan 等，2023，Self-Refine | [arXiv PDF](https://arxiv.org/pdf/2303.17651) | 反馈内容与修订的关系；迭代并非自动可靠 |
| Lin 等，2017，Focal Loss | [arXiv PDF](https://arxiv.org/pdf/1708.02002) | S7 与已有困难样本加权机制的重叠 |
| Clark & Wilkes-Gibbs，1986 | [作者 PDF](https://web.stanford.edu/~clark/1980s/Clark,%20H.H.%20_%20Wilkes-Gibbs,%20D.%20_Referring%20as%20a%20collaborative%20process_%201986.pdf) | 指代的协作、修复、扩展和替换 |
| Wood、Bruner、Ross，1976，Scaffolding | [原文 PDF 镜像](https://sachafund.wordpress.com/wp-content/uploads/2018/10/wood_et_al-1976-journal_of_child_psychology_and_psychiatry.pdf) | 辅助如何减少暂时无法处理的自由度；不是永久给出答案 |
| Hattie & Timperley，2007，Feedback | [大学托管 PDF](https://educacion.udd.cl/files/2018/04/The-Power-of-Feedback.pdf) | 反馈的内容与层级；“反馈多”不等于“反馈有效” |
| Ullman，Visual Cognition and Visual Routines | [MIT 托管作者章节 PDF](https://courses.csail.mit.edu/6.803/pdf/ullman9.pdf) | 从基础表示执行任务相关视觉操作；这是后来的作者章节，不冒称 1984 原论文 |

**以下资料有访问限制，单独标明，避免把“找到链接”写成“已核对全文”。**

- **Egly、Driver、Rafal，1994**：[PDF 链接](https://www2.psychology.uiowa.edu/faculty/hollingworth/prosem/Egly_etal_94_JEPG_ShiftingVisualAttention.pdf)。搜索返回了原文内容，但本轮直接 PDF 获取失败；没有完成全文核对。
- **Roelfsema & Houtkamp，2011**：[PMC 正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC3222807/)、[出版社 PDF](https://link.springer.com/content/pdf/10.3758/s13414-011-0200-0.pdf)。可检索内容支持上述理论概述，直接全文获取遇到验证码／错误，PDF 本轮未验证成功。
- **Butterfield & Metcalfe，2001**：作者主页列有原文，但直达获取失败；本轮用上表可访问的 2012 作者论文核对相关实验机制，不把后续论文冒充 2001 原文。
- **RePaint**：[PDF](https://arxiv.org/pdf/2201.09865)、[已打开的 HTML 正文](https://arxiv.org/html/2201.09865v1)。HTML 已核对，直接 PDF 获取失败。
- **Blended Diffusion**：[CVPR 开放 PDF](https://openaccess.thecvf.com/content/CVPR2022/papers/Avrahami_Blended_Diffusion_for_Text-Driven_Editing_of_Natural_Images_CVPR_2022_paper.pdf)。已核对公开方法内容；精读时重点看其用户提供 ROI 的前提。
- **Minsky–Papert**：[原始 memo 论述存档](https://dailypapert.com/linearly-unrecognizable-patterns/)。本轮没有拿到可核对完整证明的原书 PDF，因此不将其列为已完成原证明复核。

这轮仍待实验回答的核心问题只有三个：**远端缺失主要是传播不足还是表征不足；query 更新能否扩展目标而不漂移；成对干预训练能否在自然状态变化上产生超出普通困难样本训练的收益。** 三个问题各对应一个可否证的小实验，足以决定是否值得继续投入。