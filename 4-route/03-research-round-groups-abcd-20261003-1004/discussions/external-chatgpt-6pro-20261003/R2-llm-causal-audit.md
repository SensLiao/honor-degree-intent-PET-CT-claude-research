# R2：LLM 编辑、因果配对与涂鸦传播的独立审计

审计日期：2026-10-03。对应现有计划第五稿，以及主审提供的第六稿合成草案。目标保持最终 TEST D5 > 0.80，三画法 VAL 到 0.79 即报告；本文件只补强研究与实施逻辑，不声称进行了新训练、服务器修改或新模型评测。

## 1. 结论先行

这条 intent 主线值得继续，最可靠的落点是“**给定当前分割状态和这一笔，预测本轮应修的错误范围，并学会在多轮中保留其他区域**”。跨领域研究能提供具体的结构、监督和失败模式；不能给出医学分割到 0.80 的保证，也不能把潜在心理意图的可识别性定理直接移植过来。

最需要补强的不是再加一个大型模块，而是三个接口：

1. **候选是否有益与是否越界，要有各自的训练标签。** 全例 Dice 上升可能来自修好没有被指到的 O；原方案只学全例增益，却把“不改 O”写成已经满足。
2. **成对监督必须保持问题等价。** 同一目标的不同画法可以共享目标；不同裁剪丢掉了不同证据时，不能无条件强制相同输出。
3. **模型自己的执行结果必须进入回放。** 选出来的候选、实际写回以及 NOOP 都会影响下一笔，旧固定门槛轨迹不能永远代表新系统。

建议以主审当前更新为准：A 用小型回归器分别预测真实增益和范围外修改量，在相对原 0.5 候选的预测保持条件内选最好候选；B 保留 T/O/P 监督、加入 O 屏蔽的软增益、空间笔迹与自身状态；C 的图结构是后续候选能力。**不把特殊指代效用 U_T 强行变成统一主损失；不默认上 DPO、RL、复杂约束优化或多套自动课程。**

本轮登记 31 篇可追溯研究记录，其中 30 篇正常论文/预印本，另 1 篇为已撤回论文的状态核查。深度包括原文重点章节、原文摘要及作者项目说明，逐篇明确记在 `R2-llm-causal-papers.json`；不是宣称 31 篇全部逐页精读。尤其 SmartBrush、Shu 及部分大 PDF 的访问不完整，不把附件数字直接冒充本轮核实结果。

附件覆盖：PLAN 全文；L5、L9、L10 全文；Codex 第四轮 brief/answer；D、G 的相关创新与推导部分；S1、S2 对应三领域的条目与汇总；第六稿合成草案全文。

## 2. 关键纠错：原始论文到底支持什么

| 附件表述或推论 | 核查结果 | 可替换的准确表述 |
|---|---|---|
| IKE 去掉保留样本，89.6 降到 28.0，因此每笔取与 T 等量的难 O/P | 数字真实，证据迁移过头。GPT-J、CounterFact、32 个上下文示例，移除的是推理提示中的 retain 演示；不是稠密训练样本的数量消融 | IKE 支持“保留示例会影响编辑的语义局部性”。体素保留监督值得做；1:1 配比是本项目工程选择，不能由该数字推出 |
| 执行器只执行 pT 过阈值，已构造性保证局部性 | 把“支持集内执行”与“支持集是真实 T”混为一谈 | 已知方向/footprint 可由构造保证；未知真实指代边界依然要预测，仍会越界 |
| SERAC 与 e×b 相乘头同构 | 是功能分工的类比，不是代数同构 | SERAC 路由输入语义范围、再生成答案；SIRB 对体素编辑。可以借范围监督与难例，不能借结构保证 |
| ScopeEdit 把结果分为正确、不足、过大三类 | 漏了同时不足且过大的第四类，而且原统计只在已可靠编辑中进行 | 不足与外泄是两个轴，可同时发生。无需新增阈值，先保留连续 T 修回/O 修改/P 新错统计 |
| Shu、Brehmer 等证明本项目两类配对缺一不可，并且换笔满足完美干预 | 定理的生成模型、变量、监督方式与本项目不同 | 两类配对是互补设计原则。已知 T 的全监督学习不因这些定理而必需某个配对损失；程序化换笔也未自动识别潜在心理意图 |
| 任意同目标换画法都应严格一致 | 若画法跨错块、方向改变、裁剪丢掉证据，目标或可辨识性可能改变 | 先验证角色定义与共同可见信息；有效域内约束一致，其他位置用正常监督或未知标记 |
| BoxInst 说明只有正边会塌成全前景 | 原成功弱监督方法本来使用筛选后的同标签正边；失败来自错误正边污染等条件 | 稠密 GT 可直接监督正、负边；重点防跨边界假正边，不能引用为“正边必塌”的普遍结论 |
| APro 可原样替换成从笔出发的最大最小传播 | APro 是所有像素的归一化亲和度加权和；有全局、局部两项及软伪标签目标 | 借用瓶颈边权、排序并查集和实现思想。改成种子 maximin 是新的算子定义，重新核查前向、梯度、复杂度 |
| 有稠密 GT，所以弱监督论文里的结构正则都没用 | ScribbleBench 只比较所测涂鸦监督管线；LTF 本身就在全监督分割中使用结构模块 | 不优先搬缺标签专用伪标签流程；仍可借结构算子和边监督，收益由本项目实测 |
| Blended Diffusion 图 3 证明加局部性罚项没有好的系数 | 三组定性例子展示取舍，不能否定一切局部性损失；用户还直接给了 ROI | 已知 ROI 外可以直接复制保留。SIRB 未知 T，仍需范围学习和保留监督 |
| 所有损失用 GradNorm 就没有手定系数，也能维护硬条件 | GradNorm 有 α、更新、共享层等设置；量级平衡不处理所有方向冲突，能把某任务压得很小 | 明确主监督地位，仅对附加项做可追溯的归一化/调整；已知硬条件放在执行器 |
| 多领域共同“推出”同一机制，等于多份独立证据 | 多处是对同一项目现象的类比，且常复用同一上游假设 | 写成“多个领域提供兼容的设计启发”，区分原论文结论、数学演绎、本项目假设 |

最关键数字出处为 [IKE Table 3](https://aclanthology.org/2023.emnlp-main.296.pdf)：完整方案 S=89.6、ES=100、PS=95.2、NS=77.0，删 retain 后 S=28.0、NS=11.5。S 是三项调和平均。这些是语义回答指标，不是 Dice。[SERAC Table 4](https://proceedings.mlr.press/v162/mitchell22a/mitchell22a.pdf) 则支持困难范围样本的辨别问题。两者都不能给出医学保留体素的最佳采样比例。

[ScopeEdit](https://arxiv.org/pdf/2607.01978) 的 Figure 2/§III-B 统计 M-ORE 在 LLaVA-v1.5 的可靠编辑：正确 62.20%、不足 28.60%、过大 7.20%、二者交织 2.00%。可靠性、泛化和局部性阈值为作者设置，不能直接照搬成 SIRB 范围评分标准。

### 2.1 数学定理的使用边界

[Brehmer 等](https://proceedings.neurips.cc/paper_files/paper/2022/file/fa567e2b2c870f8f09a87b6e73370869-Paper-Conference.pdf) 的可识别性涉及实值因果变量、光滑可逆映射、所有随机完美原子干预及共享未干预噪声。换一笔时位置、形状、长度、裁剪和目标身份可能同时变；离散错误组件身份也不满足该证明的变量假设。“同状态只换输入笔”是我们能控制的数据操作，不等于已经满足该定理。

[Veitch 等](https://arxiv.org/abs/2106.00545) 明确区分反事实不变性与可观察的必要独立条件。按目标分组做一致性可以合理，但不能凭输出一致性就宣称“识别了真实因果作用”。[Shu 等](https://arxiv.org/abs/1910.09772) 分析的也是特定分布匹配型弱监督学习；SIRB 直接拥有范围标签。成对项提供的价值是训练偏置、有效样本结构与泛化约束，不是凭空增加了新的标签信息。

## 3. 把 intent 的概念说强，说到可执行

定义当前合法方向的真实错误集合 E_a(G,M)。角色构建器由笔 s 触及的错误组件得到 T，其他同向错误为 O，原本正确而不该翻转的区域为 P。于是当前实验的意图是一个已定义的函数：

`T = Referent(G, M, s, action, topology_rule)`。

这个定义的优势是训练标签可复现、能随状态重算，而且确实比“改进整张分割”更严格：修好 O 仍可能违反当前这一笔的范围。它的限制是 T 由程序定义，不是医生自由意图的观测。如果两种心理意图对应完全相同的可见影像、状态、笔迹和历史，模型无法凭空分开它们。因此论文宜称“状态依赖的指代范围学习”，把 intent 作为概念主线，并如实界定当前的操作化实例。

这不削弱创新。真正可论证的问题是：**给定同一影像和状态，模型是否按不同笔选取不同剩余错误；给定同一笔，在模型已经修过的状态下，能否重新确定范围并避免重复误改。** 单加一个由已有输入可算出的 intent 类型标签，不能算新增信息；学出有边界的、状态相关的范围可能有实质价值。

### 3.1 成对关系应该怎样定义

| 配对 | 应当固定 | 可以改变 | 合法监督 |
|---|---|---|---|
| 同目标换画法 | 患者、当前 M、方向、目标组件身份、信息足够的可见域 | 不跨出目标且不改变语义的笔迹形态 | 对应物理体素的范围预测一致；每支仍有 GT 监督 |
| 同状态换目标 | 影像、M、方向、可复用状态特征 | 目标组件和匹配后的笔位置 | 每支匹配自己的 T；在对方目标上抑制错误选择 |
| 同笔换状态 | 影像、笔与方向 | 已合法改变的 M | 按新 M 重算 T/O/P，不强制与旧 T 相同 |
| 同病例换采样网格 | 同一物理影像与目标语义 | 合理的离散采样 | 坐标、笔迹、标签正确变换后的对应，而非数组索引直接相等 |

若两次裁剪分别看见目标的不同部分，最好复用同一状态编码和同一空间域，只改变查询笔。这能省算力，也减少把裁剪内容差异误当画法差异。必须裁剪不同时，只在共同真实坐标域、且相关证据/路径有效处比较；跨出视野的连通路径是“未知”，不是自动负例。

[MatchDG](https://proceedings.mlr.press/v139/mahajan21b.html) 的同对象匹配提示一个具体陷阱：同属“病灶”类别的两个区域不是同一个指代对象。[SupCon](https://arxiv.org/abs/2004.11362) 的同类正例规则不能原样复制到指代头。T/O/P 是相对当前笔的角色；同一个物理体素换一笔后角色会变，不能无条件把这些角色做成永久语义类别。

## 4. 候选选择：正确性优先，不能把不确定性当收益

[GRECO](https://aclanthology.org/2023.emnlp-main.785/) 说明质量估计器是否能分清好坏，会决定候选组合能否改善。直接迁移到本项目的做法是使用训练真值产生编辑后果标签，而不是把熵、不同画法预测一致度或上一轮置信度直接当作收益。它们可以是特征，但不是答案。

对实际 native 写回后的每个候选 C，保存：

- `g = Dice(M_after, G) - Dice(M_before, G)`；
- `c = |C ∩ T|`，`o = |C ∩ O|`，`h = |C ∩ P|`；
- `b = o + h`，即相对本笔的范围外修改量；
- 实际是否落实本笔、是否为空、所用 editor/selector/候选版本。

这里的 O 和 P 必须分开存：P 是新增分割错误，O 是分割上可能变好但指代上越界。最终展示可以同时回答“分割效果是否更高”和“有没有通过改任务偷分”。

### 4.1 第一版采用主审的轻量方案

用两个轻量预测器估计 g 与非负 b。保留原 0.5 候选作为固定参照；先留 `pred_b(C) ≤ pred_b(C_0.5)` 的候选，再在其中挑预测 g 最高者，包含 NOOP；NOOP 的两项均固定为 0。

这条规则只是**相对预测保持条件**，不是“真实 T 外零修改”的保证。预测错误时真实 b 仍会升高；它也允许和旧模型相当的越界。其研究意义是，在已知基线保持水平上追求更高效用，不声称解决了全部范围约束。A 的晋级必须看五轮实际 Dice 和 O/P 变化，而不是只看回归误差或秩相关。

同一个候选生成器/真实写回版本必须定义参考候选和待选候选。将 b 输出限制为非负，明确非有限值的回退；不要让“两个树模型”口头省略成“没有超参数”。树复杂度、样本权重、候选数量和拟合方式仍需登记。

### 4.2 为什么先不用 DPO 或纯排名

[RankNet](https://www.microsoft.com/en-us/research/wp-content/uploads/2005/08/icml_ranking.pdf) 用的是分数差。对同一状态把每个候选分数都加上 c(x)，排名完全不变，所以仅有排序学不到收益零点。`score > 0` 是否值得执行，需要绝对增益回归、与固定 NOOP 比较，或两者结合。[DPO](https://arxiv.org/abs/2305.18290) 还涉及参考策略概率和 KL 正则化；这里已有有限候选的精确数值监督，直接回归再选择更简单。

即使 NOOP 的即时收益为零，也不意味着它在五轮任务中总是合理。拒绝后机器人可能重复提出同一笔；NOOP必须消耗本轮，按新系统实际继续回放。只在真实 TRAIN 回放发现停滞时，再考虑有限的“当前提案 vs NOOP”共同未来策略短续演，不能先把每个候选都多步展开。

### 4.3 不采用 U_T 作为 B 主损失

主审/math 分路指出，`g - 2o/(B ± k)` 一类把 O 改记为坏编辑的量即使代数成立，在 REMOVE 的特定状态下可出现很大的负值和梯度。其值不是标准 Dice 变化，也不天然解决多目标取舍。本轮不把它作为统一训练损失。

B 使用 T/O/P 的作用域监督与 O 屏蔽的软全例增益：前者学习“不属于这笔”，后者不给顺带修 O 额外奖励。**O 屏蔽不等于禁止 O 修改**。A 和 B 可以使用不同的优化实现，只需一致披露共同的指代任务、各自的软/相对条件及真实指标。

## 5. B 组合里最值得保留的监督补强

### 5.1 保留监督比错误教师蒸馏更直接

[MEND](https://arxiv.org/abs/2110.11309) 与 [KnowledgeEditor](https://aclanthology.org/2021.emnlp-main.522/) 的局部性以无关输入的原输出作为参照。移植时不能把旧 editor 的错误也学回来。SIRB 训练已经知道当前 T/O/P，因此第一版直接对 O/P 的编辑概率使用保留监督最简；若改用输出 mask 监督，则在 O/P 对齐**当前 M**。

别在 T 里蒸馏原 M：那里本来就是该修的错。别用上一轮 pT 作无条件教师：pT 是一次提案，其执行可能被 selector 缩小或跳过。上一轮实际 signed ΔM 才是执行事实，但它仍可能错误，也不能被永久锁定。

保留样本不必只拿最难的一批。按最高 pT 选 O/P 会集中在边界与不确定标注处；应保证自然分布覆盖和 O/P 两类覆盖。若首轮沿用 `|T|` 个样本，记成有预算上限的 1:1 工程配比，而不是文献推导或无系数算法。

### 5.2 边界排序的目标来自有效标签

同方向 T 内边界与 P 外边界配对，直接针对“同一预测块内删到真病灶”。排序损失与区域监督互补。若标签经过 native→3 mm 重采样，部分体积、组件身份、研究网格和实际写回必须对应；不能仅因 pT 高就认定这个 P 是“假负例”。

[Debiased Contrastive Learning](https://arxiv.org/abs/2007.00224) 主要处理同语义类被当负例的问题，不是对任意边界软化的保证。若构造 `(n+0.5)/(N+1)` 之类比例，还引入了先验平滑选择；它不能被写成“全部由数据决定”。优先用已有可靠标签，别为了概念一致把复杂边界概率估计设成第一轮依赖。

### 5.3 自动权重保持克制

[GradNorm](https://proceedings.mlr.press/v80/chen18a.html) 调整任务梯度幅值与学习速率，有 α 等设置；[PCGrad](https://arxiv.org/abs/2001.06782) 则处理梯度方向冲突。两者不是同一个问题的两个名字，也不产生零越界保证。

首轮先按有效体素/有效配对数归一化，让原 T/O/P 和增益目标仍可见；只做一次 TRAIN 的梯度量级核查。若采用自动权重，明确主监督保持位置，定义没有有效配对或零梯度时的处理，不同时叠 GradNorm、DoReMi、Group DRO。用户要求更快得到效果，这种克制能减少新系统互相干扰。

[DoReMi](https://arxiv.org/abs/2305.10429) 的超额损失混合有启发，但代理语言域损失不等于每轮可兑现 Dice 缺口。现有真实回放覆盖优先，若之后启用自适应采样，参考和当前模型必须比较相同状态、相同目标和同一种损失；不混用不同状态下的“谁更难”。

## 6. L5 全文复审：真正可借的传播思想

[APro](https://arxiv.org/html/2310.10533v2) 的全局传播有归一化加权求和，使用树路径上的最大代价构造亲和力，再结合局部传播生成软伪标签。其并查集实现帮助加速这种计算。SIRB 要的是“从本笔种子到体素的最强路径的最弱边”，不是同一输出算子；删除归一化、改种子聚合、改 3D 图都属于新的工程设计。

固定图上 exact maximin 可以作为可靠的软件数学定义，但不等于可靠的医学对象范围。假桥、3 mm 拓扑丢失、全卷图内存和瓶颈边稀疏梯度仍在。最合适的低风险接法是主审 C：作为可忽略的软特征，保留直接边监督和有限结构对，不直接整块执行；若边头不读笔，在缓存里也必须真的保持该条件。

BoxInst 的颜色筛选实验提示“少量错误正边也可造成大范围错误连接”；不能改写成没有负边就一定塌陷。我们有稠密 GT，直接学习同一 signed-error 组件内部开边、跨边界闭边是合理迁移，依据是标签可用和失败机制，而不是颜色阈值。

[ScribbleBench 的正式论文](https://papers.miccai.org/miccai-2025/0782-Paper4424.html) 标题是 *Revisiting 3D Medical Scribble Supervision: Benchmarking Beyond Cardiac Segmentation*。Table 3 的 3D partial-loss 平均 0.813、全监督 0.856，支持优先强基线和跨任务检验。它不证明 full supervision 下结构约束没价值；[LTF](https://arxiv.org/abs/1909.12513) 就是全监督结构建模的例子。

[Gated CRF Loss](https://arxiv.org/abs/1906.04651) 已由作者撤回，说明部分数字/陈述有误；附件 L5 已提醒，继续保留，不把其数值纳入效果证据。

## 7. 最精炼的组合建议与待实施合同

| 顺序 | 保留的组合 | 本分路补强 | 不作为首轮依赖 |
|---|---|---|---|
| A 先出结果 | 冻结强 checkpoint、有限候选、g/b 小预测器、NOOP | 同时记录 c/o/h；相对保持而非硬保证；联合策略 TRAIN 刷新 | DPO、在线大模型、全候选多步树搜索 |
| B 主押注 | 空间笔迹、T/O/P+O屏蔽软增益、边界保持、自身状态、可观察历史、无距离截断 | 现有块内的有效目标交换/画法配对直接加入；避免错误蒸馏和无效裁剪一致性 | 全部消融、三个自动权重/采样控制器、额外心理意图标签 |
| C 后续候选 | 学出的边与种子连通软特征、状态/结构配对 | 明确 unknown 路径、native与研究图拓扑、假桥与缓存 | 声称生物机制证明、强制整块执行、保证通用所有尺度 |

实现前应一致替换合成稿旧 U_T 相关文字：§3.1、A 的标签与 NOOP、B 的配方和损失、实施清单。A/B 共同承担指代任务，但不要求同一标量损失。

第一版只需保留对结果正确性有直接影响的检查：候选实际写回一致、GT不进入特征、患者分折、NOOP正确消耗一轮、下一笔从真实新状态重算、五轮 Dice 与 c/o/h。新分支零接入时与父模型兼容、配对坐标/路径有效即可。效果达到后，再判断收益来自哪个模块；不让归因计划阻挡强组合。

## 8. 文献索引与访问限制

逐篇 JSON 是本分路的完整登记。只看到了摘要的条目提供检索背景与方法线索，不承担精确数值或定理条件的证明；撤回论文单独标记。所有本项目收益、最优组合、范围学习能否超过 0.80 都是待实验问题。

- **LC01，2023**：[Can We Edit Factual Knowledge by In-Context Learning?](https://aclanthology.org/2023.emnlp-main.296/)。LLM知识编辑；全文重点精读：方法、Table 3、相关实验。
- **LC02，2022**：[Memory-Based Model Editing at Scale](https://proceedings.mlr.press/v162/mitchell22a.html)。LLM知识编辑/范围路由；全文重点精读：范围分类器、损失、Table 4。
- **LC03，2022**：[Fast Model Editing at Scale](https://arxiv.org/abs/2110.11309)。LLM知识编辑/保留蒸馏；全文重点精读：目标定义与方法，未复核全部实验表。
- **LC04，2021**：[Editing Factual Knowledge in Language Models](https://aclanthology.org/2021.emnlp-main.522/)。知识编辑/等价集监督；全文重点精读：约束优化、等价集、指标定义。
- **LC05，2022**：[Locating and Editing Factual Associations in GPT](https://arxiv.org/abs/2202.05262)。知识定位/模型编辑；primary摘要、作者项目页与会议元数据；未独立复核Table 4数字。
- **LC06，2023**：[Mass-Editing Memory in a Transformer](https://arxiv.org/abs/2210.07229)。批量知识编辑；primary摘要、作者项目页与ICLR元数据。
- **LC07，2026**：[Multimodal Knowledge Edit-Scoped Generalization for Online Recursive MLLM Editing](https://arxiv.org/abs/2607.01978)。多模态知识编辑/范围；全文重点精读：Section III-B、Figure 2、脚注、方法。
- **LC08，2022**：[Blended Diffusion for Text-driven Editing of Natural Images](https://omriavrahami.com/blended-diffusion-page/)。局部图像编辑；作者项目页与primary摘要；Fig 3原论文重载摘录，官方PDF过大未完整读取。
- **LC09，2023**：[SmartBrush: Text and Shape Guided Object Inpainting With Diffusion Model](https://openaccess.thecvf.com/content/CVPR2023/html/Xie_SmartBrush_Text_and_Shape_Guided_Object_Inpainting_With_Diffusion_Model_CVPR_2023_paper.html)。图像局部编辑/粗提示细化；primary摘要与会议元数据；全文抓取失败。
- **LC10，2023**：[Prompt-to-Prompt Image Editing with Cross Attention Control](https://prompt-to-prompt.github.io/)。扩散编辑/条件控制；作者项目页和primary摘要；ICLR2023，预印本2022。
- **LC11，2023**：[MasaCtrl: Tuning-Free Mutual Self-Attention Control for Consistent Image Synthesis and Editing](https://openaccess.thecvf.com/content/ICCV2023/html/Cao_MasaCtrl_Tuning-Free_Mutual_Self-Attention_Control_for_Consistent_Image_Synthesis_and_ICCV_2023_paper.html)。图像编辑/特征复用；primary摘要和作者仓库。
- **LC12，2020**：[GECToR – Grammatical Error Correction: Tag, Not Rewrite](https://aclanthology.org/2020.bea-1.16/)。文本纠错/编辑式动作；primary摘要与作者仓库。
- **LC13，2023**：[System Combination via Quality Estimation for Grammatical Error Correction](https://aclanthology.org/2023.emnlp-main.785/)。纠错验证器/候选组合；ACL原文摘要、会议元数据与预印本记录；未复核全文表格。
- **LC14，2021**：[Training Verifiers to Solve Math Word Problems](https://arxiv.org/abs/2110.14168)。LLM验证器/正确性；primary摘要与作者论文链接。
- **LC15，2023**：[Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290)。偏好优化；HTML全文重点精读：KL约束目标、Bradley–Terry、奖励平移等价。
- **LC16，2005**：[Learning to Rank using Gradient Descent](https://www.microsoft.com/en-us/research/wp-content/uploads/2005/08/icml_ranking.pdf)。成对排序；全文重点精读：Section 3、式1–4。
- **LC17，2020**：[Weakly Supervised Disentanglement with Guarantees](https://arxiv.org/abs/1910.09772)。弱监督解耦理论；primary摘要、框架说明；PDF文本解析不可用，未独立逐行核验全部定理。
- **LC18，2021**：[Counterfactual Invariance to Spurious Correlations: Why and How to Pass Stress Tests](https://arxiv.org/abs/2106.00545)。反事实不变性；全文重点精读：Theorem 3.2、必要不充分说明。
- **LC19，2022**：[Weakly supervised causal representation learning](https://proceedings.neurips.cc/paper_files/paper/2022/hash/fa567e2b2c870f8f09a87b6e73370869-Abstract-Conference.html)。因果表示可识别性；全文重点精读：Definitions 1–3、Theorem 1、方法。
- **LC20，2021**：[Self-Supervised Learning with Data Augmentations Provably Isolates Content from Style](https://arxiv.org/abs/2106.04619)。增强/内容风格解耦；primary摘要和会议版本检索；全文体积过大。
- **LC21，2021**：[Domain Generalization using Causal Matching](https://proceedings.mlr.press/v139/mahajan21b.html)。域泛化/同对象配对；论文HTML相关方法段及PMLR摘要。
- **LC22，2020**：[Supervised Contrastive Learning](https://arxiv.org/abs/2004.11362)。监督对比学习；primary摘要与NeurIPS元数据。
- **LC23，2020**：[Debiased Contrastive Learning](https://arxiv.org/abs/2007.00224)。对比学习标签污染；primary摘要与NeurIPS元数据。
- **LC24，2023**：[DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining](https://arxiv.org/abs/2305.10429)。数据混合/超额损失；primary摘要、作者项目说明与仓库；不复核全部实验表。
- **LC25，2018**：[GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks](https://proceedings.mlr.press/v80/chen18a.html)。多任务损失平衡；全文重点精读：算法、α、目标梯度、权重归一化。
- **LC26，2020**：[Gradient Surgery for Multi-Task Learning](https://arxiv.org/abs/2001.06782)。多任务梯度冲突；primary摘要与NeurIPS论文元数据。
- **LC27，2021**：[BoxInst: High-Performance Instance Segmentation with Box Annotations](https://openaccess.thecvf.com/content/CVPR2021/html/Tian_BoxInst_High-Performance_Instance_Segmentation_With_Box_Annotations_CVPR_2021_paper.html)。弱监督分割/边界；primary摘要；原论文Table 1及段落的重载检索摘录；原站PDF读取受阻。
- **LC28，2023**：[Label-efficient Segmentation via Affinity Propagation](https://arxiv.org/abs/2310.10533)。弱监督分割/图传播；HTML全文重点精读：式2–8、Algorithm 1、讨论。
- **LC29，2019**：[Learnable Tree Filter for Structure-preserving Feature Transform](https://arxiv.org/abs/1909.12513)。全监督结构建模；primary摘要、NeurIPS元数据与作者仓库。
- **LC30，2025**：[Revisiting 3D Medical Scribble Supervision: Benchmarking Beyond Cardiac Segmentation](https://papers.miccai.org/miccai-2025/0782-Paper4424.html)。3D医学涂鸦监督基准；全文重点精读：实验设置、Table 3、比较限制。
- **LC31，2019**：[Gated CRF Loss for Weakly Supervised Semantic Image Segmentation](https://arxiv.org/abs/1906.04651)。弱监督正则/撤稿状态；arXiv摘要、版本历史与撤回说明。

