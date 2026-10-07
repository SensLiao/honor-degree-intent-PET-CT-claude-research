# 第二轮独立复核：交互/提示分割、指代范围与创新边界

审计对象：现有 `PLAN.md`、`research/B-lit-interactive.md`、`D-innovation.md`、`L4-interactive-sota.md`、事实单、`S1-literature-digest.md` 的交互领域、Codex 第 1 轮 brief/answer 与第 6 轮反馈、旧 red-team review 的相关部分。

审计日期：2026-10-03（项目记录跨 UTC 日期）。这里新增独立证据与建议，不改主计划、不改服务器或评测，不把旧报告的“已读”数量当成本轮阅读量。

## 结论

主线值得保留，但准确的主张应当是：

> 给定当前分割状态和一笔带符号的修正，学习该笔在当前残差中的操作性指代范围，同时区分其他错误和需要保留的体素；在真实五轮交互中用更少的有害编辑提高最终 Dice。

“intent”“学出范围”“同一状态换一笔”“候选加质量头”“图上扩散”“模型自己出错再训练”中的任何一个，单独都不能稳妥地作为首创。真正还值得争取的组合区别，是**状态依赖的有符号残差指代标签、目标/其他错误/保留区域的显式区分、以及对这些标签关系的受控训练**。本轮没有证明这个具体组合已经被完全覆盖，也没有完成足以支持“全领域首创”的穷尽检索。

效果开发继续优先：保留 N1_STATE_SPATIAL，优先用模型自有状态、有效密集笔迹融合、与授权范围一致的编辑目标组成强配方；低成本候选评分可同时开展，但必须先堵住“靠修 O 涨全局 Dice”的目标漏洞。图结构可以接在赢家上，不应变成整个效果路线必须等它实现完的前置工程。最终目标仍为 TEST D5 > 0.8，完整三画法 VAL 达到 0.79 即汇报；这两条不改写成文献承诺或收益估计。

## 本轮实际阅读范围与证据强度

核验 **32 篇唯一论文**，年份为 2019–2026。按保守口径：

- **23 篇**直接读到论文方法、任务定义或相关实验章节。
- **3 篇**成功取得原始 PDF/作者稿的方法索引摘录及作者摘要，但全文网页未成功打开：MultiSeg、DIG、PseudoClick。
- **6 篇**主要读取原作者或正式会议/出版社摘要与架构说明：PiClick、FocalClick 原版、FocusCut、DynaMITe、ScribbleSeg、iSegFormer。FocalClick 的执行细节另由同作者 FocalClick-XL 正文核验；iSegFormer 后续还检索到导言与方法概述，但仍不计入本轮方法通读档。
- 没有把 **ClickSEG** 另算一篇论文。它是相关代码库名称，不能和 FocalClick 当成两个独立研究结果。
- 不称“32 篇全部精读全文”。PDF 打不开、仅有索引片段的记录均明确降级。涉及本轮没重核的内部公式和性能数字，不沿用旧稿口径。

逐篇结构化记录在 `R2-interactive-papers.json`；本文末尾逐篇列出实际结论、应用联系和不成立边界。

## 一、需要修改的关键结论

### 1. 52.1 / 68.2 数字真实，原叙述缺了决定性条件

原始位置是 [Semantic-SAM，§4.1/Table 5](https://arxiv.org/html/2307.04767v1)，并非 SAM 原论文给出的通用能力总分：

| 项目 | 原文条件 |
|---|---|
| 被比较模型 | SAM-B |
| 数据 | COCO Val2017 |
| 任务与指标 | 单击分割，mean IoU |
| Max 52.1 | 由模型预测置信度选择候选 |
| Oracle 68.2 | 事后用真实 IoU 选出候选 |
| 同表训练条件 | 仅用 SA-1B 训练，直接评测 COCO |
| 可支持结论 | 这个候选集和这组数据上存在明显选择遗憾 |
| 不可支持结论 | 一个小评分头就能回收 16.1 点；医疗 Dice 可同幅增长；选择一定是本项目最大瓶颈 |

建议主文改为：“Semantic-SAM 的自然图像实验表明，多候选系统可能存在较大的选择遗憾；本项目是否能利用类似机会，应由 TRAIN 学习后的五轮 VAL 判断。”保留本地 oracle 作为机会诊断，不能和这组文献数字相加。

### 2. “没人把这一笔范围作为带标签预测目标”过宽

至少有三种直接反例或强近邻：

- [ClickAttention，§III](https://arxiv.org/html/2408.06021v1) 明确研究点击影响范围，并用分割标签监督点击区域与全图的相似性；所以“范围只靠手定相似度”不准确。
- [Structured Click Control，§III](https://arxiv.org/html/2405.04009v1) 明确使用 structured click intent，学习重要性分数并监督节点选择，再通过图和 cross-attention 影响分割。不能把 intent 或图结构本身写成新概念。
- [MultiSeg](https://openaccess.thecvf.com/content_ICCV_2019/papers/Liew_MultiSeg_Semantically_Meaningful_Scale-Diverse_Segmentations_From_Minimal_User_Input_ICCV_2019_paper.pdf)、[Semantic-SAM](https://arxiv.org/html/2307.04767v1)、[GraCo](https://arxiv.org/html/2405.00587v2) 都显式处理一处提示可能对应的不同语义范围、粒度或部件。

这些方法通常监督对象/部件前景，并未因此等同于项目的 signed residual T/O/P。可保留的表述是：“在本次检查的近邻中，尚未确认有与我们的操作性目标完全相同的三类有符号残差指代训练；需要逐项比较，不作全领域排他性断言。”

### 3. 局部纠错与保留并非本项目首次提出，VISTA3D 是必须加入的医学近邻

[FocalClick](https://openaccess.thecvf.com/content/CVPR2022/html/Chen_FocalClick_Towards_Practical_Interactive_Image_Segmentation_CVPR_2022_paper.html) 已针对已有掩膜修正。[原作者 FocalClick-XL §3](https://arxiv.org/html/2506.14686v1) 对 Progressive Merge 的说明十分直接：比较前后预测，只更新包含当前点击的差异连通区域，保留其他位置。

[VISTA3D Algorithm 1](https://arxiv.org/html/2406.05285v1) 把类似问题带到三维医学：正负差异区分别计算 CC，合并命中相应正负点击的分量。它不是学习出的 GT error referent，但已经在医学中限制交互引起的连带修改。

[DIG / Local RICE](https://openaccess.thecvf.com/content/WACV2024/papers/Myers-Dean_Interactive_Segmentation_for_Diverse_Gesture_Types_Without_Context_WACV_2024_paper.pdf) 也不应被缩成“只改评测指标”。可检索的原文方法还包含 gesture-region 训练增强及其他区域保留。它与项目有实质任务交集，尽管标签和三维协议不同。

因此主文应说明：我们要把既有的局部更新/形态学选择，推进为在当前状态中学出的残差指代；不能借漏引邻近方法扩大新意。

### 4. 候选加质量头已有自然图像与医学直接先例

[SAM](https://ar5iv.labs.arxiv.org/html/2304.02643)、[PiClick](https://www.sciencedirect.com/science/article/abs/pii/S0925231224008543) 已有多候选与自动选择。[PRISM 的 confidence learning](https://arxiv.org/html/2404.15028v1) 在医学中用 Dice 回归监督候选质量，选择最高分掩膜再进入浅层纠错网络。

本项目“预测编辑后整例 Dice 的变化”仍有具体工程价值：在同一状态下排序候选，原 Dice 是共同常数，预测最终 Dice 和预测 ΔDice 在排序意义上相同，但回归尺度、跨状态校准及 no-op 判定会不同。因此不能以“预测的是变化而非 Dice”独立建立强创新主张。区别应是所评价的编辑、授权范围、跨状态学习和实际五轮效果。

### 5. SegNext 不能支持“当前笔必须直接进主干”

[SegNext §3/Table 4](https://arxiv.org/html/2404.00741v1) 先缓存图像嵌入，再对密集提示进行卷积和融合，并使用自注意力融合块。其消融去除的是 dense fusion 相关处理，不能等同为“把笔从图像编码主干第一层拿掉”。

[InterFormer](https://ar5iv.labs.arxiv.org/html/2304.02942)、[DynaMITe](https://amitrana001.github.io/DynaMITe/)、[FocSAM](https://arxiv.org/html/2405.18706v1) 都为缓存后有效提示处理提供了近邻。既有 N1_STATE_SPATIAL 可以准确定位为“共享编码后的当前笔条件空间支路”，与这一类设计一致；它是否足够有效取决于本项目真实结果。

所以应保留当前队列，不因文献被误读而立即改成全主干早融合。另一方面，也不能为守住架构标签而把早融合列为原则性禁区：若效果证据表明后融合不足，早融合是工程备选，但创新要从任务定义和训练关系说明。

### 6. CPC-SAM 的原义需要纠正

[CPC-SAM §2.2](https://ar5iv.labs.arxiv.org/html/2407.05416) 是半监督双分支 cross prompting：一个分支由无提示输出给另一分支产生点提示；提示后的预测再交叉监督对方无提示预测。其推理可以使用默认无提示嵌入。

它不是简单的“同一目标换两个点，要求输出不变”。本项目可借对称训练关系的想法，但不能把这个简写当作准确论文摘要，也不能拿它证明跨目标反事实对已经做过或从未做过。

### 7. “同一状态换一笔，目标要跟着换”不能仅凭这句话声称首创

[SEEM](https://ar5iv.labs.arxiv.org/html/2304.06718) 的不同视觉/语言提示、DynaMITe 的多对象查询、MultiSeg/PiClick 的不同目标候选，都依赖提示改变目标的能力。普通训练也可以在同一图像中抽不同对象。因此“换提示换输出”这一关系本身属于交互分割的基础要求。

较窄且可检验的贡献是：固定影像和当前分割，构造只改变本次误差 referent 的两个合法笔迹，把 T 与 O 的身份互换作为显式监督关系；同一残差 referent 内改变笔迹风格时保持目标标签；当前 mask 变化后重新计算 referent，而不是强迫所有前后状态输出恒等。

这些关系可能以训练样本组织、目标定义和损失形成方法组合，但仍需给出准确训练方案及最近邻对照。效果前不必先大规模做逐项消融；先用组合训练跑起来，并完整保留训练版本以便后补。

### 8. “不改”不等于完成意图；单步正效用也不等于五轮收益

[GRES](https://ar5iv.labs.arxiv.org/html/2306.00968) 的 no-target 指输入没有匹配目标；SAM 2/3 的 presence 指对象或概念是否存在。这些都不同于“目标确实存在，但当前候选不值得执行”。

如果确定性 robot 在掩膜不变时重复同一笔，而评分器也确定性地输出 no-op，系统可能进入剩余轮数全不改的状态。历史输入或模型置信度更新可能打破这个条件，但不能默认会发生。主计划已有跳过后状态改变的提醒，应落实成真实五轮记录：连续 no-op 次数、重复笔、之后是否仍能恢复。同一轮 ΔDice 的 oracle 不可代替这个验证；不为规避死循环私自改变冻结 robot。

### 9. 泛化不能由“删掉 60 mm”自动获得

[nnInteractive §2.4–2.6](https://arxiv.org/html/2503.08373v1) 借混合交互策略、对象相对参数、标签变体与多领域训练适应用户及对象尺度；AutoZoom 也仍含计算上的步长和上限。[ScribblePrompt §3](https://arxiv.org/html/2312.07381v2) 通过多任务影像、真实/合成标签和不同提示学习未见任务。

可借的是**避免将固定物理距离当成语义范围**，保留 spacing 与未截断位置信息、对象相对尺度，以及任务多样性。不是所有参数都要学：候选数量、计算精度、邻接形式、显存预算、训练学习率必然还会存在。应区分“语义范围不由硬半径决定”和“算法完全无超参数”。

本阶段可把架构目标写成适应不同医学数据；单一 PET/CT 数据结果本身不足以证明 general medical 能力。等效球半径只是辅助尺度，无法完整表征细长、分支、穿插、多分量残差；它不应重新变成隐藏的硬裁剪半径。

## 二、intent 的可操作定义：不要让术语超过标签能证明的内容

根据本地协议与主审最新代码核验：

1. 对当前分割 M 和 GT Y，按 ADD/REMOVE 形成对应的有符号错误集合。
2. **T 是当前笔实际命中的原生网格 18 邻接错误分量的并集**；不必只有一个分量。
3. O 是同方向的其他错误；P 是该次操作不应改变的其他位置。
4. robot 并非简单选择“最大 3D 体积错误”：它在 FP/FN 的轴向切片中按最大 8 邻接区域生成笔迹，再按笔迹长度选择符号，平局取 ADD。具体以冻结实现为准。

这是一种**协议定义的残差 referent**。它与医生的真实语义意图有联系，但不是同一件事。举例：同一病灶的两块漏分因当前 mask 中的一条正确桥断开，协议会把它们当作两个错误分量；医生可能仍指整个病灶。反过来，两个语义上不同的病灶错误若通过误分桥连通，协议可能把它们归进同一 T。连接方式随采样网格变化，也不等于语义边界变化。

论文若说“模型理解意图”，必须限定为这个可操作任务。若以后要扩展为临床语义 intent，需引入目标实例、语言、医生指定范围或对应交互标注，而不应只换名词。

### 图结构的对应要求

假设图模块用 3 mm 网格 6 邻接，而任务 T 来自原生网格 18 邻接，二者连通性没有自动同构关系。一个只通过对角相邻连接的 T，可能在 6 邻接图上没有完全位于 T 内的路径；下采样也会丢失细桥。**不能把“所有 T 都应通过正边连到笔”设成无条件训练真理。**

实施时至少要明确：投影后可见且有合法路径的部分、由于网格/视域不可达的部分、边界与未知部分。可以改用一致邻接，也可以让图分数作为软特征保留非图路径，但不能偷偷穿过 O/P 建桥后仍称为不越界。并查集精确求解的是给定图的连通问题，不能证明输入边权正确或临床范围正确。

## 三、候选执行器的最低正确性要求

### 候选不是“仅 19 档”

原计划每个阈值有两类候选：全阈值集合和命中当前笔的连通分量并集。19 个阈值因此最多产生 **38 个原始掩膜**；再加旧执行器与 no-op，名义上最多 40 个条目，之后按实际写回掩膜去重。如果旧 0.5 执行器确实与全集合 0.5 候选完全一致，则该项重复，最多 39 个不同动作（含 no-op）。若旧写回逻辑还有其他过滤，不能假定重复。

同时，两条候选族各自可能随阈值嵌套；把不同族混在一起，并非一个单调的“从小到大”链。同体积也不代表同位置或同含义。评分器必须读到实际编辑位置、符号、模型分数分布、笔迹关系与当前状态，不能只看体积。

### 全局 Dice 评分和“只修 T”有真实冲突

设两个候选在 T、P 上的行为完全相同，第二个候选另修复了一部分 O。按真实 GT 计算整例 Dice，第二个候选会得到额外收益；但按本次授权定义，它多改了未被指的错误。因而“预测整例 ΔDice，选正的最大值”本身不会学到 O 该保留。

这不是需要等消融才处理的归因问题，而是执行目标相互矛盾。最低补强是：训练标签同时记录 T 的修复、P 新错、O 编辑与实际整例增益；训练/排序的主目标不能奖励 O。只在测试后检查 O 是否碰巧少改，不能替代目标一致性。

具体使用授权效用、约束排序还是多头风险预测，应由主审统一核算，避免这里随意拍一个惩罚 λ。必须明确预测的风险约束仍可能错判，并非 GT 级硬保证。对于分数相同或不确定的候选，简单动作/no-op 可以作为确定的决胜规则，但不可夸称保证提高 Dice。

### 学习与选择保持闭环

按患者交叉拟合评分器是正确方向，但如果基础编辑器本身已经见过所有 TRAIN 患者，评分器的折外不代表整条系统对这些患者完全折外。应如实记录这个条件，以最少额外工作检查训练回放分布与实际 VAL 五轮分布的一致性。网络继续训练后候选分布会变化；旧评分器不能未经验证就永久沿用。

快速 VAL 用于筛选，晋级组合再做完整三画法 VAL；最小检查是端到端真实五轮及 T/O/P 编辑记账，不是扩大门槛扫描或先补几十个消融。

## 四、近邻矩阵：到底还剩什么空间

| 拟主张 | 最近邻 | 已有的部分 | 本项目仍可能贡献的更窄部分 |
|---|---|---|---|
| 一笔对应可学习范围 | MultiSeg、Semantic-SAM、GraCo、ClickAttention | 粒度、候选、监督式点击影响范围 | 有符号残差中 T/O/P 区分，随当前 mask 重定义 |
| 局部修改、外部保留 | FocalClick、DIG、VISTA3D | 差异 CC 限制、局部评价与训练关系 | 学出的范围替代易错形态规则，并保持授权目标 |
| 候选+学质量 | SAM、PiClick、PRISM | IoU/Dice 评分、自动候选选择 | 授权残差效用、no-op 与真实五轮后果 |
| state-conditioned | RITM、InterFormer、ScribblePrompt、SAM 2 | 前次 mask、迭代自有状态、记忆 | 状态变化使 error referent 标签本身改变 |
| 提示换目标 | SEEM、DynaMITe、PiClick | 提示条件对象选择、多实例查询 | 固定 M 的 T/O 角色互换监督与对应反事实对 |
| prompt/style 不变性 | 多样交互训练、CPC-SAM 的相关但不同关系 | 提示多样性和跨分支学习 | 同一残差 referent 的等价笔迹配对；不能误述 CPC |
| graph/attention intent | Structured Click Control、ClickAttention | 图节点选择、相似度监督、注意范围 | 与任务网格一致的 seed-to-error reachability，明确不可达条件 |
| 通用医学 | ScribblePrompt、nnInteractive、VISTA3D | 多模态/多任务训练与未见目标验证 | 可移植残差操作接口与实际跨域证据 |

矩阵中的“仍可能”是待检验区别，不是授予优先权，也不意味着必须先把整张矩阵做成消融才能跑效果。

## 五、把方案做强而不过度拖慢的建议

### 组合 A：先把当前笔真正用起来，并练真实错误状态

以现有 flat 赢家为父模型，组合：

- 保留并接收 N1_STATE_SPATIAL 的真实结果；有效时直接采用缓存后的密集笔迹空间处理。
- current stroke 与 history 分别表示，保证最新修正对当前输出有可追踪影响。
- 使用模型自身五轮状态，而不是只训练干净的离线错误；最新模型分布与历史回放混合要记录。
- 编辑目标同时关心 T 修复及 P/O 保留，边界与易误改区域给出足够监督。
- 去掉把 60 mm 当不可见边界的截断，保留物理 spacing 与连续位置证据，尺度仅作软条件。

这套组合直接对应“后续轮出大坏编辑、笔迹空间证据不足、训练与实际状态不匹配”。它主要继承成熟设计，正适合效果优先阶段。无须把每项都先拆开证明净贡献。

### 组合 B：同一个基础模型上加真正针对编辑的候选排序

沿用现有候选计算，但完成上节的动作去重、O 不奖励和五轮 no-op 检查。对现成网络先训练小评分器确实可以省主网络训练，但训练评分器仍属于学习一个新模型，不应写成系统完全未训练。

优先比较同一基础模型的默认执行与学习执行的五轮结果；这是一项必要的系统正确性比较，不等于拖延效果的全面归因。它还可并行帮助判断强组合 A 之后，选择器是否仍有实际价值。

### 组合 C：在效果赢家上加明确的残差关系与可达结构

若 A/B 已改善效果，加入同状态换 referent、同 referent 换画法、状态变化后重定 referent 的配对训练。图模块只承担与网格匹配的关系建模，允许不可达/未知，不以“不限步数”包装成无限范围或完美修复。

若图实现与训练成本会占掉主要实验窗口，可以先使用相似度/关系监督作为轻量版本，再接精确图求解；此前保留的 checkpoint 与训练配置足够支撑效果后补归因。不要为“必须有一个图”延迟有效系统到达 VAL 0.79 的检验。

### 与论文论证的连接

效果出来后，最有信息的后补问题是：同预算下，显式残差 referent 标签及正确配对关系是否比只看相同独立样本更有效？学习范围是否优于简单 CC merge，且收益是否不依赖 O 的额外修复？这比逐个删除每一层、每一种 runtime 参数更能支撑 intent 主张。

## 六、逐篇证据卡

以下卡片与 JSON 一一对应。每篇的应用联系均是本项目推演，除“原文实际结论”外不冒充论文已验证的结果。

### IA01 · Segment Anything (2023)

- 领域：通用提示分割。
- 原始来源：[论文/作者来源](https://ar5iv.labs.arxiv.org/html/2304.02643)。
- 实际访问深度：方法相关章节：模型、歧义候选、质量预测；未逐页读全部附录。
- 原文实际结论：同一提示可输出多个歧义掩膜，按最小分割损失训练匹配候选，并学习每个候选的 IoU 质量分数；候选加质量预测并非新机制。
- 可联系本项目：可复用候选与质量分工，必须把候选质量改成项目所需的编辑效用。
- 不成立边界：质量是对象掩膜 IoU，不是既有医学分割的授权残差编辑收益；不会自动解决 T/O 区别或不改决策。

### IA02 · SAM 2: Segment Anything in Images and Videos (2024)

- 领域：视频与通用提示分割。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2408.00714v2)。
- 实际访问深度：方法相关章节与附录 D.2.1：多掩膜、IoU 监督和迭代训练。
- 原文实际结论：保留歧义多掩膜和预测 IoU 选择，视频记忆用于后续帧；所有候选的 IoU 头获得监督而分割损失选择最佳候选，迭代训练包含纠正点击。
- 可联系本项目：参考历史与当前提示的区分、缓存及纠错训练；不要把视频记忆直接当作医学 intent。
- 不成立边界：时序物体传播不同于同一影像的残差纠错；object presence 头判断对象是否出现，不能直接解释成编辑有益概率。

### IA03 · SAM 3: Segment Anything with Concepts (2025)

- 领域：概念提示与多实例分割。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2511.16719v1)。
- 实际访问深度：方法相关章节：presence head、候选与概念匹配；预印本。
- 原文实际结论：文本或示例概念提示驱动所有匹配实例的分割；全局概念存在判断与局部实例定位评分分开处理。
- 可联系本项目：帮助区分目标存在、指代匹配、编辑获益三种不应混成同一分数的判断。
- 不成立边界：概念是否匹配不等于某次修改是否能提高 Dice，也不等于只修本次选中错误。该论文确实存在，但不能从题名推断自由形式临床指令能力。

### IA04 · Semantic-SAM: Segment and Recognize Anything at Any Granularity (2024)

- 领域：多粒度提示分割。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2307.04767v1)。
- 实际访问深度：方法 §3、实验 §4.1–4.2 与 Table 5、7；2023 预印本/2024 ECCV。
- 原文实际结论：通过多粒度候选与 many-to-many 匹配学习同一点对应的不同范围。Table 5 的 SAM-B 在 COCO Val2017 单击 mIoU 为 Max 52.1、Oracle 68.2；Max 用预测置信度挑候选，Oracle 用 GT IoU 挑候选。
- 可联系本项目：支持检验候选质量与选择遗憾；不能据此证明候选评分是本项目唯一或最大瓶颈。
- 不成立边界：这些数字不是 SAM 原论文的总体结果，不是 PET/CT Dice，也不是可兑现的 16.1 点收益；同表模型仅用 SA-1B 训练。学出的粒度仍有候选数等设计参数。

### IA05 · MultiSeg: Semantically Meaningful Scale-Diverse Segmentations From Minimal User Input (2019)

- 领域：多尺度语义范围。
- 原始来源：[论文/作者来源](https://openaccess.thecvf.com/content_ICCV_2019/papers/Liew_MultiSeg_Semantically_Meaningful_Scale-Diverse_Segmentations_From_Minimal_User_Input_ICCV_2019_paper.pdf)。
- 实际访问深度：原始 PDF 方法检索摘录及作者机构摘要；PDF 全文打开失败。
- 原文实际结论：最少交互下输出具有语义意义的不同尺度掩膜，包含多分支范围和评分机制；范围歧义早于 SAM 已被显式处理。
- 可联系本项目：把“学出范围”查新收窄为 state-dependent signed residual referent，不能以范围或多尺度输出本身声称首创。
- 不成立边界：所见原文不能支持它学习当前 signed error CC 的指代范围；对象、部件、群体尺度与残差范围不是同一标签。

### IA06 · PiClick: Picking the Desired Mask from Multiple Candidates in Click-Based Interactive Segmentation (2024)

- 领域：候选掩膜选择与目标歧义。
- 原始来源：[论文/作者来源](https://www.sciencedirect.com/science/article/abs/pii/S0925231224008543)。
- 实际访问深度：原作者 arXiv 摘要和正式出版社摘要/方法概述；全文未读；2023 预印本/2024 Neurocomputing。
- 原文实际结论：输出多个候选并用 Target Reasoning Module 自动建议用户期望的掩膜，直接处理点击目标歧义。
- 可联系本项目：作为“候选加评分选择意图”的最近邻之一；评分器不是独立创新，目标标签与多轮授权行为才可能构成区别。
- 不成立边界：本次未能独立核全 TRM 每个内部头和融合细节，因此不重复旧稿关于内部乘积公式或具体收益数字；也未发现它定义本项目的 T/O/P。

### IA07 · GraCo: Granularity-Controllable Interactive Segmentation (2024)

- 领域：用户控制分割粒度。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2405.00587v2)。
- 实际访问深度：方法 §3.1–3.3、粒度定义及实验分析相关章节。
- 原文实际结论：自动产生 mask-granularity 对，再将粒度嵌入作为额外提示学习不同对象/部件范围；构造粒度同时依赖语义和大小。
- 可联系本项目：尺度与语义范围不等价；等效球半径最多是辅助尺度，不能独自定义 intent。
- 不成立边界：粒度由额外输入控制，并非只凭一笔自动发现医学残差范围；其粒度公式使用 0.5 权重和离散 bins，不能当作完全无人工参数的范例。

### IA08 · Reviving Iterative Training with Mask Guidance for Interactive Segmentation (2022)

- 领域：迭代交互与模型自有状态。
- 原始来源：[论文/作者来源](https://ar5iv.labs.arxiv.org/html/2102.06583)。
- 实际访问深度：方法与迭代训练相关实验；2021 预印本/2022 正式发表。
- 原文实际结论：利用前次掩膜作为输入，在训练中基于模型当前输出模拟纠正点击，可从外部初始掩膜开始修正。
- 可联系本项目：把 own-state training 定位为使交互训练分布匹配的必要工程，不将其包装成全新 intent 理论。
- 不成立边界：“练自己的错”和“上一轮掩膜输入”已经是既有路线；单篇的迭代数/训练稳定性经验不可升格为通用定律。

### IA09 · FocalClick: Towards Practical Interactive Image Segmentation (2022)

- 领域：交互局部纠错与保留。
- 原始来源：[论文/作者来源](https://openaccess.thecvf.com/content/CVPR2022/html/Chen_FocalClick_Towards_Practical_Interactive_Image_Segmentation_CVPR_2022_paper.html)。
- 实际访问深度：原始会议摘要；同作者 FocalClick-XL §3 对原方法的完整说明交叉核验；原版 PDF 打开失败。
- 原文实际结论：原论文明确同时处理局部 refinement 与已有掩膜修正。后续原作者详述其 Progressive Merge：新旧二值掩膜差异中取包含新点击的连通区域更新，其他区域保留。
- 可联系本项目：是必须承认的概念和执行近邻，比较维度应是推断出的残差范围能否优于形态学限定。
- 不成立边界：不能写“传统连通方法从未考虑指代/不越界”；但形态学更新区域不是直接监督学习出的 signed error referent。原版所有消融数字本次未重核。

### IA10 · FocusCut: Diving Into a Focus View in Interactive Segmentation (2022)

- 领域：自适应局部范围与意图。
- 原始来源：[论文/作者来源](https://openaccess.thecvf.com/content/CVPR2022/html/Lin_FocusCut_Diving_Into_a_Focus_View_in_Interactive_Segmentation_CVPR_2022_paper.html)。
- 实际访问深度：原始会议摘要及 PDF 可检索的方法概述；全文打开失败。
- 原文实际结论：从全局预测出发，裁剪以点击为中心且范围自适应的局部视图做渐进修正；作者明确以从点击视角理解用户意图来描述该机制。
- 可联系本项目：直接反驳“交互分割没有考虑意图/修改范围”的宽泛表述；保留 project-specific 标签区别。
- 不成立边界：摘要不足以核所有自适应公式；它没有因此证明心理意图被识别，也不能据此宣称当前项目 scope 相同。

### IA11 · SimpleClick: Interactive Image Segmentation with Simple Vision Transformers (2023)

- 领域：交互分割架构。
- 原始来源：[论文/作者来源](https://ar5iv.labs.arxiv.org/html/2210.11006)。
- 实际访问深度：方法 §3、补充架构和 prompt encoding；2022 预印本/2023 ICCV。
- 原文实际结论：正负点击图及前一轮掩膜通过独立 patch embedding 与图像特征融合，使用朴素 ViT 和轻量 MLP 头，采用迭代点击训练。
- 可联系本项目：为密集提示保留空间位置提供设计依据，但不构成当前笔必须进入第一层主干的定理。
- 不成立边界：其大规模预训练与 2D 对象任务不能证明向 6.65M 3D SIRB 主干直塞点击必然优于后融合；论文也提示输出概率可能未校准。

### IA12 · InterFormer: Real-time Interactive Image Segmentation (2023)

- 领域：缓存后交互特征融合。
- 原始来源：[论文/作者来源](https://ar5iv.labs.arxiv.org/html/2304.02942)。
- 实际访问深度：方法：五类参考图、图像缓存、I-MSA 交互模块。
- 原文实际结论：耗时图像编码可预处理，交互模块融合缓存特征与包含确定/可能前景背景及 unknown 的参考图；后续点击可重置冲突区域的不确定性。
- 可联系本项目：N1_STATE_SPATIAL 可合理定位为共享编码之后的提示条件空间处理；既有状态和 unknown 表示值得借鉴。
- 不成立边界：五类参考图和历史状态不等于 SIRB 的三类残差监督；不支持“只有主干早期融合才有效”。

### IA13 · DynaMITe: Dynamic Query Bootstrapping for Multi-object Interactive Segmentation Transformer (2023)

- 领域：多对象交互与时空查询。
- 原始来源：[论文/作者来源](https://amitrana001.github.io/DynaMITe/)。
- 实际访问深度：原作者项目页摘要与架构图说明、会议元数据；论文正文未成功打开。
- 原文实际结论：将点击位置特征编码为时空查询，缓存图像特征，在同一轮处理多个对象并按后续点击更新。
- 可联系本项目：当前图像换目标要变化这一总原则已存在；创新应落在受控残差配对及其具体监督关系。
- 不成立边界：本次访问不足以审计全部训练目标；显式对象查询不等于 signed residual CC，也不等于所有多目标模型都缺少 target-change 学习。

### IA14 · Rethinking Interactive Image Segmentation with Low Latency, High Quality, and Diverse Prompts (2024)

- 领域：SegNext 密集提示融合。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2404.00741v1)。
- 实际访问深度：方法 §3 与 Table 4 对应消融。
- 原文实际结论：SegNext 先缓存图像嵌入，密集提示图经卷积再与图像嵌入融合，并经过自注意力融合块。Table 4 的 65.34 到 85.71 对应去除/加入 dense fusion 的实验设置。
- 可联系本项目：优先评估现有 N1 空间支路及有效后融合，避免为追随误读立即重做大主干。
- 不成立边界：dense fusion 消融并不是“把当前笔从主干拿掉”的等价实验；旧稿据此断言当前笔必须进主干不成立。该差值是自然图像 HQSeg-44K 条件，不是项目预期收益。

### IA15 · FocSAM: Delving Deeply into Focused Objects in Segmenting Anything (2024)

- 领域：提示条件对象聚焦。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2405.18706v1)。
- 实际访问深度：引言与方法相关章节：Dwin-MSA、P-DyReLU、对象特征迭代。
- 原文实际结论：围绕被提示对象动态聚焦窗口与特征，利用点击条件处理改善 SAM 的交互细节，并以缓存设计减少重复计算。
- 可联系本项目：支持低成本提示条件空间支路与对象相关缓存；不必把所有信息注入图像编码第一层。
- 不成立边界：对象聚焦不是本项目 signed error 区域的监督标签；更强聚焦也可能带来较大范围覆盖，不能直接保证不越界。

### IA16 · FocalClick-XL: Towards Unified and High-quality Interactive Segmentation (2025)

- 领域：统一交互、局部与全局上下文。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2506.14686v1)。
- 实际访问深度：方法 §3 对 FocalClick 的复述及扩展设计；预印本。
- 原文实际结论：组合上下文网络、对象网络、细节网络和提示层，支持不同交互形式；原方法的 Progressive Merge 以差异连通区保留已有细节。
- 可联系本项目：将 image context、state、current prompt、writeback 分清；在编辑推断中保留足够全局证据。
- 不成立边界：仍含裁剪扩展率和二值化规则；不能用其成功证明固定几何参数被彻底消除，也不能忽略全局上下文对局部编辑的影响。

### IA17 · ScribbleSeg: Scribble-based Interactive Image Segmentation (2023)

- 领域：笔迹交互分割。
- 原始来源：[论文/作者来源](https://arxiv.org/abs/2303.11320)。
- 实际访问深度：原作者摘要与元数据；全文多次打开失败。
- 原文实际结论：提出多样化训练笔迹、确定性评测笔迹生成器，以及 Prototype Adaption Module 和 Corrective Refine Module。
- 可联系本项目：明确区分训练 prompt 模拟、评测 robot 规则与预测目标；这些因素不能在一篇引用中混为一谈。
- 不成立边界：摘要不能核实旧稿对其全部模块作用和公式的陈述；它不是弱监督只用 scribble 标签的方法。

### IA18 · Interactive Segmentation for Diverse Gesture Types Without Context (2024)

- 领域：DIG 局部意图与手势多样性。
- 原始来源：[论文/作者来源](https://openaccess.thecvf.com/content/WACV2024/papers/Myers-Dean_Interactive_Segmentation_for_Diverse_Gesture_Types_Without_Context_WACV_2024_paper.pdf)。
- 实际访问深度：原始 PDF 的方法与 Local RICE 可检索摘录，原作者项目页；PDF 全文打开失败。
- 原文实际结论：不仅提出只计手势目标错误区域的 Local RICE，也通过训练增强学习手势与区域的关系，并让其他区域保持已有分割；考察 diverse gestures 的局部修正。
- 可联系本项目：列为真正的 task-level 近邻；新方法需强调显式 T/O/P 残差标签和状态变化后的指代重定，而不是笼统的局部编辑。
- 不成立边界：本次读取为原文方法摘录，未核全数据与所有公式。它不完全等同 native 18 邻接残差标签，但旧稿将它说成仅换评价指标过窄。

### IA19 · ClickAttention: Click Region Similarity Guided Interactive Segmentation (2024)

- 领域：点击影响范围与亲和监督。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2408.06021v1)。
- 实际访问深度：方法 §III：点击相似度、监督式范围、正负点击 affinity loss；预印本。
- 原文实际结论：显式扩展点击影响范围，按点击区域和全图特征相似性学习 attention，并用分割标签监督相似度、用判别亲和损失减少正负点击耦合。
- 可联系本项目：“已有范围只靠手定相似度、无人监督学习范围”必须删除；可保留残差指代与普通前景监督的区别。
- 不成立边界：已经不是纯无监督相似度；但监督对象仍为语义前景/背景，不是本项目有符号残差中的 T/O/P。

### IA20 · Structured Click Control in Transformer-based Interactive Segmentation (2024)

- 领域：图结构意图与点击控制。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2405.04009v1)。
- 实际访问深度：方法 §III-A/B 及前言；预印本。
- 原文实际结论：作者明确提出 structured click intent，学习点击相似性分数、选择图节点、用 GNN 聚合和双 cross-attention 融合；节点重要性有监督损失。
- 可联系本项目：反驳“intent + 图传播”的宽泛首创；把新意限定为状态条件的 signed residual connectivity 和可操作的配对标签。
- 不成立边界：使用相似度阈值、top-k 等人工计算选择；其图是动态 token 关系，并非 seed-to-voxel 精确 maximin 残差可达图。

### IA21 · Segment Everything Everywhere All at Once (2023)

- 领域：SEEM 多模态 referring 与交互。
- 原始来源：[论文/作者来源](https://ar5iv.labs.arxiv.org/html/2304.06718)。
- 实际访问深度：方法：提示采样、语言/视觉组合、记忆提示和掩膜匹配。
- 原文实际结论：视觉提示、语言提示与记忆提示可组合，模型按提示生成对应分割，历史掩膜通过 memory prompting 参与后续互动。
- 可联系本项目：将 referent 定义写清楚；同状态不同提示对应不同目标是广泛已有能力。
- 不成立边界：语义指代表达和视觉对象选择不同于误差 CC 定义；没有语言或临床目标标签时不能借 SEEM 证明本项目已经理解医生完整意图。

### IA22 · GRES: Generalized Referring Expression Segmentation (2023)

- 领域：多目标与无目标指代。
- 原始来源：[论文/作者来源](https://ar5iv.labs.arxiv.org/html/2306.00968)。
- 实际访问深度：任务定义 §3.1 与 no-target 评价/分类器分析。
- 原文实际结论：扩展语言指代分割到多个目标和无目标输入，提供独立 no-target 标签及相关评价；只看掩膜空不空不能充分完成无目标识别。
- 可联系本项目：给评分器分清匹配、修正范围与停止原因；无益拒绝不可与无目标识别混同。
- 不成立边界：no target 是请求未匹配对象，no-op 是候选编辑预期无益；真实错误仍存在时 no-op 不能被宣称为已经完成意图。

### IA23 · Cross Prompting Consistency with Segment Anything Model for Semi-supervised Medical Image Segmentation (2024)

- 领域：CPC-SAM 半监督跨分支提示。
- 原始来源：[论文/作者来源](https://ar5iv.labs.arxiv.org/html/2407.05416)。
- 实际访问深度：方法 §2.1–2.2 的 cross prompting 与监督关系。
- 原文实际结论：两个分支从各自无提示输出产生对方的点提示，用提示后的更可靠输出交叉监督对方无提示输出，训练时利用未标注数据；推理可无显式提示。
- 可联系本项目：纠正旧稿对 CPC-SAM 的简化描述；仅借对称关系监督的思想并清楚标注改造。
- 不成立边界：不是简单的同一目标换两个点要求输出一致；不能直接称为已有同状态目标切换的反事实监督。全标注 SIRB 未必需要其半监督损失。

### IA24 · PRISM: A Promptable and Robust Interactive Segmentation Model with Visual Prompts (2024)

- 领域：医学交互候选评分与修正。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2404.15028v1)。
- 实际访问深度：方法：迭代、confidence learning、corrective learning，相关实验。
- 原文实际结论：多个候选掩膜的置信度通过 Dice 目标回归监督，选择最高分候选后进入浅层纠错网络，训练包含迭代错误提示。
- 可联系本项目：医学里“多候选+学质量+选择”已有直接先例；工程价值仍高，贡献应落在 T/O/P 一致的效用与五轮闭环行为。
- 不成立边界：监督是候选整掩膜的 Dice，不是某个已有多病灶掩膜的授权编辑增益；存在指标相同而任务不同的区别。

### IA25 · VISTA3D: Versatile Imaging Segmentation and Annotation Model for 3D Computed Tomography (2024)

- 领域：三维医学局部纠错与合并。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2406.05285v1)。
- 实际访问深度：方法、Algorithm 1 的 connected component merge。
- 原文实际结论：新预测与已有掩膜形成正负差异区，各自按连通分量，只合并包含相应点击的分量；还处理正点击落在已有掩膜内的情形。
- 可联系本项目：作为 SIRB 最直接的三维医学执行近邻；学习指代范围应证明超出规则式 CC merge 的具体能力。
- 不成立边界：不是学习本项目的 T/O/P，且连通更新仍是形态学规则；但已在 3D 医学任务明确限制点击引发的修改。

### IA26 · nnInteractive: Redefining 3D Promptable Segmentation (2025)

- 领域：通用三维医学交互。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2503.08373v1)。
- 实际访问深度：方法 §2 的 prompting、用户策略、AutoZoom、ambiguity 与训练数据章节。
- 原文实际结论：混合交互用户策略、按对象尺度调整笔迹形变、随机标签组合适应语义歧义；AutoZoom 根据边界预测扩展 ROI。训练覆盖 120 多个 3D 数据集和多模态。
- 可联系本项目：强烈支持对象相对尺度与混合用户策略；当前 PET/CT 模型只能先称 generalizable design，需跨数据证据才称 general medical model。
- 不成立边界：AutoZoom 仍有 1.5 倍步长和最多 4 倍等计算/范围设置，不能拿它证明无超参数。通用性来自任务数据与评测，不来自模型名称。

### IA27 · ScribblePrompt: Fast and Flexible Interactive Segmentation for Any Biomedical Image (2024)

- 领域：通用生物医学笔迹交互。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2312.07381v2)。
- 实际访问深度：方法 §3.1–3.4、引言与作者项目页；未逐页读全部补充。
- 原文实际结论：在多任务影像上以模型当前错误模拟后续提示，结合真实与合成标签提升未见任务适应；正负笔迹、点击和框均被表示，支持轻量 UNet。
- 可联系本项目：支持先做轻量有效的状态与提示训练，借多样化任务而非仅移除 mm 常数实现泛化。
- 不成立边界：多任务 2D 全对象分割不同于 native 3D 残差授权；专家研究的时间和 Dice 改善不能外推为本项目收益。

### IA28 · SCISSR: Scribble-Conditioned Interactive Surgical Segmentation and Refinement (2026)

- 领域：外科笔迹交互与历史记忆。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2603.18544v1)。
- 实际访问深度：方法 §2.1–2.7；2026-03-19 预印本。
- 原文实际结论：冻结 SAM 2 主体，加入密集笔迹编码、最新笔迹的空间门控融合、前轮预测记忆与 LoRA，展开多轮纠错训练。
- 可联系本项目：最新笔迹和历史信号分流已经有近邻；SIRB 可借简洁接口，但创新需来自残差指代目标。
- 不成立边界：自然视角手术图像不同于 PET/CT；所见摘要提及 SAM 3 可转移并不等于已经报告跨 backbone 完整验证。不能凭其高 Dice 判断 SIRB 可以达到相同分数。

### IA29 · iSegFormer: Interactive Segmentation via Transformers with Application to 3D Knee MR Images (2022)

- 领域：医学 Transformer 交互。
- 原始来源：[论文/作者来源](https://arxiv.org/abs/2112.11325)。
- 实际访问深度：原作者摘要、作者论文页与会议元数据；全文未读。
- 原文实际结论：Transformer 交互框架应用于膝 MR 分割，结合 2D 交互和视频式传播服务三维影像。
- 可联系本项目：避免按标题归类；可比较交互计算与体积范围，但不是直接 scope 标签先例。
- 不成立边界：不能把“应用到 3D”写成原生全体积 3D 卷积/Transformer 残差模型；本次未核全部传播参数和数字。

### IA30 · PseudoClick: Interactive Image Segmentation with Click Imitation (2022)

- 领域：错误预测与自动纠正点击。
- 原始来源：[论文/作者来源](https://pmc.ncbi.nlm.nih.gov/articles/PMC12685406/)。
- 实际访问深度：原始作者稿在 PMC 的方法检索摘录；网页打开遇到验证页，ECCV PDF 未成功打开。
- 原文实际结论：预测假阳性和假阴性错误区域，按这些预测产生伪点击，区分人类与伪点击的输入表示以模仿交互纠错。
- 可联系本项目：把 error localization 与 referent assignment 分成不同能力；不能认为有错误图就自然得到 T/O。
- 不成立边界：预测哪里可能有错并自动出下一笔，不等于推断当前真实一笔指向哪块错；本次未重新验证所有性能数字。

### IA31 · TETRIS: Towards Exploring the Robustness of Interactive Segmentation (2024)

- 领域：真实用户与交互鲁棒性。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2402.06132v1)。
- 实际访问深度：真实用户研究、极端点击优化、评价协议方法章节。
- 原文实际结论：真实用户点击分布偏离标准中心错误点击，模型对有效点击位置敏感；用受约束极端点击测试模型鲁棒性。
- 可联系本项目：支持训练端覆盖多样交互；评测协议保持冻结，不能为消除难例临时改 robot。
- 不成立边界：真实研究是 600 个第一轮和 1200 个第二轮答复，不能称 1800 名医生或完整多轮临床轨迹；自然图像结论不能量化 PET/CT 掉分。

### IA32 · RClicks: Realistic Click Simulation for Benchmarking Interactive Segmentation (2024)

- 领域：学习用户点击分布。
- 原始来源：[论文/作者来源](https://arxiv.org/html/2410.11722v1)。
- 实际访问深度：用户数据 §3 与 clickability 方法 §4 相关章节。
- 原文实际结论：收集约 47.5 万有效真实点击并学习 clickability 模型，使用更真实点击分布评测交互质量和鲁棒性。
- 可联系本项目：在 TRAIN 混合不同选笔习惯时留出未训练的策略作压力检验；将策略变化和理想可修空间变化区分。
- 不成立边界：是自然图像点击模型，不是医生 PET/CT 笔迹分布；学习出来的用户模型也有域依赖，不能直接替换冻结评测。

## 七、可直接替换进主文的短表述

**思想。** Intent 在这里被操作化为：当前笔在当前分割残差中命中了哪一组应修改体素，以及哪些体素应保留。我们不把 GT error CC 等同于完整临床心理意图。

**查新。** 既有交互分割已研究点击范围、粒度歧义、局部保留、候选评分、状态记忆及图结构控制。本次检索尚未确认与我们“状态依赖的有符号残差指代标签及受控关系监督”完全相同的方案，不能宣称概念首创。

**实施。** 先用有效的密集笔迹融合、模型自有状态、授权一致的编辑目标和低成本候选排序跑强组合，达到实际效果后补关键对照。图结构与配对训练围绕剩余失败加入，不把论文组件数量当作收益保证。

**目标。** TEST D5 > 0.8 是目标；完整三画法 VAL 达到 0.79 即报告。文献、单步 oracle、理想连通求解都不能提前保证这个结果。

## 八、对 R2-synthesis-draft 的第二轮独立交叉审核

审核了主审随后提供的第六稿草案。主审正在替换 U_T，按分工本节不评价该项代数。对创新边界、强组合 A/B/C、N1 保留和引用公平性，未发现新的实施阻断；提出以下五项重要补正：

1. `q(T | X,M,s,H)` 容易被理解为完整集合后验，而 flat 目前输出逐体素 T/O/P。建议改成“预测 T 掩膜/体素角色分布”，不暗示已经建模全部可能集合上的后验分布。
2. P 首先应严格按冻结角色构建器定义为 T/O 以外区域，再与合法方向域相交；不要在全域把它简写为只有正确体素。合法动作域中的计数与全卷标签定义应分开说明。
3. “复用 N1 空间支路”应明确依据实际完成结果决定具体采用。保留正在运行的候选，不等于该支路已被证明有效或必然成为最终模型。
4. 主文至少承认 FocalClick/DIG/VISTA3D 的局部保留、SAM/PiClick/PRISM 的候选评分、ClickAttention/Structured Click Control 的监督式范围或 intent。狭义残差标签与受控关系仍可作为待验证区别，不写概念首创。
5. A 的特征 `e` 应注明 flat 中 `e=pT+pO`，与 pT 来自同一个三类头；不把它解释为独立错误分支的第二份证据。

整体上，A 先试低成本执行选择，B 作为一次续训的强组合，C 不阻挡 A/B 的路线符合效果优先。真实五轮判定、图不强制进入最终模型、N1 不撤、模型历史允许被纠正、避免宣称当前笔必须进主干等处理合理。阅读深度和旧 TEST 使用历史保持如实披露。
