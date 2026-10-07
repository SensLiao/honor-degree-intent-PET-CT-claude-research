# 七个领域的子主题分配（每个子主题一个检索 agent，目标每个 ≥25 篇已核实、最少 22 篇）

| 领域（目录名） | 子主题（文件名） | 范围 | 主要对应模块 |
|---|---|---|---|
| psychology | referring-and-pragmatics | 指代、指向、共同注意、语用推断（Grice、Rational Speech Acts、共同基础）、指称歧义消解 | 意图绑定、范围头 |
| psychology | perceptual-grouping-and-objecthood | 格式塔分组、图形背景、基于物体的注意、物体边界判断、分组尺度 | 范围/指代头、连通 |
| psychology | repair-and-correction-behaviour | 对话修补、纠错反馈的理解、撤销与重做、人如何解读他人的更正 | 多轮纠错、撤回候选 |
| psychology | decision-criteria-and-asymmetric-cost | 信号检测论、判据设定、不对称损失下的决策、损失厌恶、信心与校准 | 执行门槛、加删分治 |
| psychology | stroke-sketch-and-gesture-semantics | 手绘笔画、草图理解、手势语义、笔画形状与意图的关系、指点手势的精度 | 笔的编码、画法稳健性 |
| psychology | medical-image-perception-and-expertise | 放射科医生视觉搜索、满意式搜索、整体印象（gist）、专家与新手的差异 | 训练状态分布、评测 |
| neuroscience | predictive-coding-and-error-signals | 预测编码、预测误差、误差驱动更新、自由能 | 残差修正框架、误差场 |
| neuroscience | efference-copy-and-forward-models | 传出副本、前向模型、感觉运动学习、自身动作与外界变化的区分 | 上一轮实际改动作输入、撤回 |
| neuroscience | attention-and-biased-competition | 偏置竞争、空间与基于物体的注意、特征注意、胜者通吃、注意的归一化模型 | 笔查询的交叉注意力、绑定 |
| neuroscience | contour-integration-and-figure-ground | 边界归属细胞、轮廓整合、关联场、填充、表面补全、侧向连接传播 | 范围传播、远端补全、连通 |
| neuroscience | plasticity-gating-and-asymmetric-learning | 多巴胺奖励预测误差的正负不对称、抑制与兴奋平衡、门控、稳态可塑性 | 难负样本平衡、加删不对称损失 |
| neuroscience | binding-and-working-memory | 绑定问题、同步、序列工作记忆、情境依赖的记忆更新 | 意图绑定、历史作为证据 |
| llm | grounding-and-reference-resolution | 视觉定位、指代表达理解、多模态指代消解、指令中的指代 | 意图绑定 |
| llm | self-correction-verifiers-and-revision | 自我纠错、反思、验证器、过程奖励模型、先提议后核验、最佳 N 选 | 候选打分、撤回 |
| llm | preference-and-contrastive-pairs | RLHF/DPO 配对偏好、对比学习的难负例、假负例问题、奖励作弊 | 块内配对、难负样本 |
| llm | prompting-and-structured-decoding | 提示编码、软提示、提示微调、思维链式结构化中间步骤、受约束解码 | 笔的编码、类型化中间步骤 |
| llm | editing-and-locality | 模型编辑的局部性、文本编辑模型（插入删除）、带掩膜的图像编辑与修补、编辑不外溢 | 受约束的残差编辑 |
| llm | calibration-abstention-and-multiturn | 校准、选择性预测与拒答、不确定性、多轮对话状态跟踪 | 执行门槛、多轮纠错 |
| medical-cv | interactive-medical-segmentation | nnInteractive、SAM-Med3D、MedSAM、ScribblePrompt、SegVol、VISTA3D、PRISM、DeepIGeoS、MIDeepSeg、点击与涂鸦纠错 | 整体结构 |
| medical-cv | petct-lesion-segmentation | autoPET I 到 V、PSMA PET/CT、全身病灶分割、假阳性抑制、SUV 先验、小病灶 | 数据先验、输入 |
| medical-cv | losses-imbalance-and-dice-optimisation | Dice 优化理论、边界损失、难例挖掘、Focal/Tversky、分割校准、类别不平衡 | 损失设计、加删不对称 |
| medical-cv | uncertainty-tta-and-quality-control | 测试时增强、集成、翻转平均、分割质量控制、失败预测、不确定性估计 | 翻转增强、收益头 |
| medical-cv | training-on-own-states-and-click-simulation | RITM、FocalClick、SimpleClick 的迭代训练、点击模拟策略、DAgger 式状态收集、交互轨迹训练 | 训练状态池、模拟器 |
| medical-cv | evaluation-statistics-and-lesion-level-metrics | NoC/AUC 协议、患者级 bootstrap、小样本推断、多重比较、连通块后处理、病灶级指标 | 评测与统计 |
| medical-cv | natural-image-interactive-and-local-refinement | SAM/SAM2/HQ-SAM、RITM、FocalClick 的局部精修、涂鸦传播、InterFormer、GPCIS | 解码、局部精修 |
| physics | diffusion-levelsets-and-geodesics | 热方程、反应扩散、水平集、主动轮廓、测地距离、程函方程、快速行进 | 范围传播 |
| physics | statistical-physics-mrf-and-percolation | Ising/Potts、MRF/CRF、平均场、相变、渗流与连通、随机簇模型 | 连通、绑定、传播 |
| physics | energy-control-hysteresis-and-stability | 能量模型、变分原理、最优控制与最小作用量、迟滞、阻尼、多轮迭代的稳定性与过冲 | 受约束编辑、撤回、多轮稳定 |
| physics | pet-ct-imaging-physics | SUV、部分容积效应、分辨率与点扩散、噪声、重建、CT HU、多模态融合 | 输入归一化、小病灶 |
| physics | inverse-problems-and-regularisation | 正则化、Tikhonov、稀疏恢复、压缩感知、超分辨、先验与似然的权衡 | 远端补全、正则项 |
| physics | symmetry-equivariance-and-information | 对称与等变、翻转等变网络、信息瓶颈、率失真、学习的热力学 | 翻转增强、等变结构 |
| mathematics | graph-connectivity-and-topology | 最小割、随机游走者、最宽路径（最小最大路径）、生成树、持续同调、拓扑约束分割 | 范围、绑定、连通 |
| mathematics | set-metric-optimisation-and-bayes-decision | Dice/F 度量最优决策、贝叶斯最优阈值、校准与真分数规则、次模优化 | 执行门槛、加删不对称 |
| mathematics | statistics-paired-bootstrap-and-power | 配对与聚类 bootstrap、置换检验、多重比较、层次贝叶斯、序贯检验、功效分析 | 评测与统计 |
| mathematics | multiobjective-and-loss-balancing | 多目标优化、梯度冲突、损失平衡（GradNorm、PCGrad、不确定性加权）、课程学习 | 损失标定 |
| mathematics | metric-learning-ranking-and-hard-negatives | 度量学习、成对/三元组/排序损失、难负例挖掘理论、对比学习中的假负例、一致性正则 | 块内配对、难负样本 |
| mathematics | sequential-decision-and-fixed-points | MDP、模仿学习与 DAgger 理论、迭代算法收敛、压缩映射与不动点、最优停止 | 多轮、撤回、状态池 |
| mathematics | morphology-distance-and-shape | 数学形态学、距离变换、中轴、形状先验、测地主动轮廓、图像上的 PDE | 范围 |
| education | feedback-theory-and-formative-assessment | 反馈理论（Hattie 与 Timperley 等）、形成性评价、纠正性反馈的时机与具体性 | 训练信号设计 |
| education | scaffolding-zpd-and-curriculum | 支架、最近发展区、逐步撤除支架、样例学习、课程排序 | 课程学习、状态池难度 |
| education | error-based-learning-and-desirable-difficulties | 从错误中学习、建设性失败、合意困难、检索练习、间隔练习 | 难负样本设计、回放 |
| education | tutoring-systems-and-learner-modelling | 智能导学系统、知识追踪、学习者建模、从示范学习 | 多轮用户意图建模、历史 |
| education | motor-skill-and-handwriting-instruction | 运动技能习得、刻意练习、书写教学、基于草图的教学 | 笔的编码 |
| education | assessment-reliability-and-item-response | 评分量规、评分者一致性、项目反应理论（难度与区分度）、测评的信效度 | 按病例难度分层评测 |
