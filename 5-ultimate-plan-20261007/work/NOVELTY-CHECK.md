# 新意核查：SIRB-Net 直接近邻逐篇打开原文核实，六条候选主张的新意等级

结论先说：六条候选主张没有一条能写成第一次有人做。(d) 嵌套范围候选加收益头、(e) 按 Dice 账推出的加删门槛、(f) 读连续概率状态整片重预测而写回受限，这三条已有人做，只能当实现细节写；(a) 由这一笔定位、在上一轮反向改动里给出多个范围的局部撤回候选并与范围、续修、不改同台打分，(b) 纠错场景三类配对的联合学习，(c) 从笔出发沿学出的误差场做可微的 minimax（路径上最弱一环最强的那条路）传播，这三条有近邻但有可辩的差别，写法只能是“本次检索未见”。本次打开来源页核实 68 条（简报点名的 30 条直接近邻，加 38 条 2025 到 2026 年新工作或原理来源），4 条只找到检索摘录，记为未核实，不作结论依据。

## 一、核实方式、网络实况、分级口径

- 工具与路线：WebSearch 找候选，做到第 22 次时会话共享的检索额度用尽，之后靠 export.arxiv.org API 按题名查、已打开页面里的引用线索、PubMed eutils（NCBI 的检索与取记录接口）补；WebFetch 打开 arXiv abs/HTML 页、proceedings.mlr.press、icml.cc、cvpr.thecvf.com 虚拟会场页、autopet-v.grand-challenge.org；PubMed 文章页只给 cookie 页，改 eutils esearch 找 PMID 再 efetch XML 读记录；Springer 文章页跳 idp 登录页，Correction-aware 一篇改读 Crossref（出版社存录元数据的接口）里出版社存的完整摘要，再读作者代码库 README；openaccess.thecvf.com 的 HTML 页经 WebFetch 得 403，用 curl 直接取到（MultiSeg）；OpenReview 是人机验证页，打不开；autoPET V 官方仓库按会话规则申请只读后浅克隆读 README 和 simulate_scribbles.py。
- 分级口径：已有人做 = 打开的来源里有同一机制、用途相同；有近邻但有可辩的差别 = 机制的主要部件都有先例，但组合、作用对象或监督方式在打开的来源里没有；本次检索未见 = 打开的来源都没有这个机制，不等于没人做过。
- 登记：每条按 `work/LIT-AGENT-INSTRUCTIONS.md` 的 JSON 格式写进 `04-cross-domain/registers/medical-cv/direct-neighbours.json`（68 条）和 `direct-neighbours.unverified.json`（4 条）。
- 项目主张只引简报第六节和 `1-plan/PLAN.md` 第三节；项目数字只在第四节用到 T1 门槛试验一处（TRAIN，出处 `5-ultimate-plan-20261007/work/PROJECT-BRIEF-for-agents.md` 第五节第 7 条）。来源页没写的事（例如仓库记的会议名）标“来源页未显示”。

## 二、第一部分：简报点名的直接近邻，逐篇

每篇五项：标题（作者，年份，出处）；打开的 URL 与核实方式；它做了什么（来源里真有的）；和我们哪条主张重叠；剩下的差别。

### 1. FocalClick: Towards Practical Interactive Image Segmentation（Xi Chen, Zhiyan Zhao, Yilei Zhang 等，2022，CVPR 2022）
- https://arxiv.org/abs/2204.02574 ；读了摘要。
- 做了什么：Progressive Merge（渐进合并）“利用形态信息决定哪里保留、哪里更新”，让用户能修改任意已有掩码；另一半贡献是低算力设备上的效率。
- 重叠：(f) 的“写回受限”。差别：按形态规则定保留区，不读连续概率，二维点击。

### 2. VISTA3D: A Unified Segmentation Foundation Model For 3D Medical Imaging（Yufan He, Pengfei Guo, Yucheng Tang 等，2024，arXiv 2406.05285；仓库记 CVPR 2025，来源页未显示）
- https://arxiv.org/abs/2406.05285 与 https://arxiv.org/html/2406.05285 ；读了全文（HTML 方法节）。
- 做了什么：自动 127 类加三维点击交互；合并规则原话“只增删含点击的连通块（connected component，相邻体素连成的一片），以免意外改动”；交互分支用 SAM 生成的超体素在 11454 例 CT 上训练。
- 重叠：(f) 写回限定在含笔的块。差别：规则合并、不学范围、不做撤回。

### 3. Interactive Segmentation for Diverse Gesture Types Without Context（DIG；Josh Myers-Dean, Yifei Fan, Brian Price 等，2023，arXiv 2307.10518；仓库记 WACV 2024，来源页未显示）
- https://arxiv.org/abs/2307.10518 与 https://arxiv.org/html/2307.10518 ；读了全文（HTML）。
- 做了什么：用户只“在图上做标记”，不指定手势类型，也不指定包含还是排除；DIG 数据集；“局部”指标只看“手势所指的那一块连通错误被修得多好”，RICE 指标按 IoU 变化算。
- 重叠：T 的定义（笔所指的那块连通错误）和“只评所指那块”。差别：二维、自然图像；没有多候选、撤回和配对监督。

### 4. PRISM: A Promptable and Robust Interactive Segmentation Model with Visual Prompts（Hao Li, Han Liu, Dewei Hu 等，2024，MICCAI 2024，arXiv 2404.15028）
- https://arxiv.org/abs/2404.15028 ；读了摘要。
- 做了什么：点、框、涂鸦稀疏提示加掩码稠密提示；迭代学习用上一轮提示；“每幅图多个分割头，各出连续图和一个置信分”；浅层修正网络重标错标体素。
- 重叠：(d) 多候选加分数头；(f) 修正网络。差别：候选是整幅掩码，分数是置信不是收益；无撤回。

### 5. ClickAttention: Click Region Similarity Guided Interactive Segmentation（Long Xu, Shanghong Li, Yongquan Chen 等，2024，arXiv 2408.06021）
- https://arxiv.org/abs/2408.06021 ；读了摘要。
- 做了什么：按“正点击区域与整幅输入的相似度扩大正点击的影响范围”；判别亲和损失减少正负点击区域的注意力耦合。
- 重叠：范围由学出的相似度决定，和 (c)(d) 的“学范围”同类。差别：相似度扩散，不是路径瓶颈；无候选与收益。

### 6. Structured Click Control in Transformer-based Interactive Segmentation（Long Xu, Yongquan Chen, Rui Huang 等，2024，arXiv 2405.04009，页面注“Submitted to NeurIPS 2024”）
- https://arxiv.org/abs/2405.04009 ；读了摘要。
- 做了什么：“基于图神经网络的结构化点击意图模型”，用被点 token 的全局相似度自适应取图节点，双交叉注意力注入；针对多次点击后结果不变或变差。
- 重叠：“intent”一词和多轮后不响应的问题。差别：没有范围候选、撤回、配对。

### 7. nnInteractive: Redefining 3D Promptable Segmentation（Fabian Isensee, Maximilian Rokuss, Lars Krämer 等，2025，arXiv 2503.08373）
- https://arxiv.org/abs/2503.08373 与 https://arxiv.org/html/2503.08373 ；读了全文（HTML）。
- 做了什么：点、涂鸦、框、套索，二维交互出三维结果，120 多个数据集；训练时“先从自己预测的假阳或假阴区域里选一个连通块”放提示，网络“把上一轮预测当额外输入”；“用户意图常有歧义”，靠随机标签组合训练来按交互消歧；骨干 nnU-Net ResEnc-L。
- 重叠：(b) 第三类（状态变了按定义重算目标）是它的常规训练；(f) 读上一轮状态。差别：读二值掩码不读概率；无候选、撤回、配对。

### 8. Interactive Segmentation with Elaborate Focus Prior（EFPNet；Kangpeng Hu, Yinghui Sun, Tao Wang, Weihao Zhang, Quansen Sun，2026，ICML 2026，PMLR 306:45689–45702）
- https://proceedings.mlr.press/v306/hu26au.html 、 https://icml.cc/virtual/2026/poster/65114 、PMLR PDF 本地抽文字；读了全文。
- 做了什么：一阶段预测“错误掩码”Êm = f(I, Mt−1, cnew)；训练目标 Em 是上一轮掩码对真值的假阳 Ep 或假阴 En 里“含新点击的最大连通区域，其余孤立区域舍弃”；新点击按 Ep、En 哪个像素更多决定取负还是正；焦点视野取 Em 的最紧外接框，推理用 BBox(Êm > τ)；三重亲和（像素、特征、掩码）在框内修正 Mt−1；摘要里的“historical feedback”指上一轮掩码。
- 重叠：训练目标几乎等于 T；(f) 的“所指区域内重算、框外不动”。差别：单输出、无候选族、无撤回、无 O/P 分开监督、二维点击。

### 9. Correction-aware interactive 3D tumor segmentation with sparse and revisable prompts（Hao Li, Haoxuan Li，2026，The Visual Computer 42(9):370，DOI 10.1007/s00371-026-04560-5）
- https://api.crossref.org/works/10.1007/s00371-026-04560-5 （出版社存录的完整摘要）与 https://github.com/HaoLi12345/interactive_segmentation （README）；读了摘要；Springer 文章页跳登录页未开，正文里的残差修正细节本次没能重核，仅凭摘要和 README。
- 做了什么：把提示“当作对演化中掩码的修订”；点击、三维框、涂鸦加掩码反馈精修；“从残差错误抽提示”；稀疏切片涂鸦；“修订感知提示记忆，把最新正负指令和提示标签翻转过的位置分开”；合成的跨轮修订分析；MSD-Colon、KiTS21。README：建在 PRISM 上；三态修订输入含“矛盾图”；`--multiple_outputs` 出多个候选并带置信量。
- 重叠：(a) 的历史跟踪、(d) 的多候选加分数、(f) 的掩码反馈。差别：跟踪的是用户改口的体素，不是系统自己写回的体素；候选是整幅；无撤回候选。

### 10. Lightweight Method for Interactive 3D Medical Image Segmentation with Multi-Round Result Fusion（LIM-Net；Bingzhi Shen, Lufan Chang, Siqi Chen 等，2024，arXiv 2412.08315，未见同行评审版）
- https://arxiv.org/abs/2412.08315 与 https://arxiv.org/html/2412.08315 ；读了全文（HTML）。
- 做了什么：MRF 模块逐层切片，质量网络读“原图切片加两版掩码”，预测“上一轮掩码比这一轮更好”的概率 P_i；P_i > τ 就保留上一轮，否则接受这一轮。
- 重叠：(a) 学着退回上一轮。差别：整层二选一，不看新的一笔落在哪，不和别的候选同台打分。

### 11. IBISAgent: Reinforcing Pixel-Level Visual Reasoning in MLLMs for Universal Biomedical Object Referring and Segmentation（Yankai Jiang, Qiaoru Li, Binlu Xu 等，2026，arXiv 2601.03054；仓库记 CVPR 2026，来源页未显示）
- https://arxiv.org/abs/2601.03054 与 https://arxiv.org/html/2601.03054 ；读了全文（HTML）。
- 做了什么：多模态大模型发点击（类名、正负、二维坐标）给 MedSAM2，带上一步掩码；点击模拟放在错误区中心；自反思轨迹两类：“自我纠正：发现动作错了，退回上一状态，重新推理”，以及用户不一致纠正；强化学习五项奖励含逐步改善。
- 重叠：(a) 退回。差别：整步退回，无用户在环，不是局部范围候选。

### 12. Cross Prompting Consistency with Segment Anything Model for Semi-supervised Medical Image Segmentation（CPC-SAM；Juzheng Miao, Cheng Chen, Keli Zhang 等，2024，MICCAI 2024，arXiv 2407.05416）
- https://arxiv.org/abs/2407.05416 与 https://arxiv.org/html/2407.05416 ；读了全文（HTML 2.3 节）。
- 做了什么：双分支互出提示与监督；提示一致性正则：“从最大连通块取一个中心点和一个随机点”，随机点的预测要接近中心点的，Dice 加交叉熵。
- 重叠：(b) 第二类“同目标换画法输出一致”。差别：半监督、单目标；没有换笔换目标和“没被指的那处不动”。

### 13. Variance-insensitive and Target-preserving Mask Refinement for Interactive Image Segmentation（VTMR；Chaowei Fang, Ziyin Zhou, Junye Chen 等，2024，AAAI 2024，arXiv 2312.14387）
- https://arxiv.org/abs/2312.14387 与 https://arxiv.org/html/2312.14387 ；读了全文（HTML）。
- 做了什么：掩码匹配正则要求“第一步预测”和“把真值扰动到同样 IoU 的合成掩码”两种起点输出一致；局部精修区域是“M1 与 M0 差图里的最大连通区域”；目标感知缩放。
- 重叠：(b) 第二类（换起点输出一致）；(f) 所指连通块。差别：二维、单目标、无撤回。

### 14. Prompt-Driven Referring Image Segmentation with Instance Contrasting（Prompt-RIS；Chao Shang, Zichen Song, Heqian Qiu 等，2024，CVPR 2024）
- https://cvpr.thecvf.com/virtual/2024/poster/30670 ；读了摘要（CVF HTML 与 PDF 403）。
- 做了什么：CLIP 与 SAM 用提示学习接起来；“实例对比学习提高对不同实例的判别力，以及对描述同一实例的不同语言的鲁棒性”。
- 重叠：(b) 的“同目标拉近、不同目标推开”。差别：按一句话分割，不是纠错状态；无“没被指的错不动”。

### 15. Interactive 3D segmentation for primary gross tumor volume in oropharyngeal cancer（2S-ICR；Mikko Saukkoriipi, Jaakko Sahlsten, Joel Jaskari 等，2025，Scientific Reports 15，DOI 10.1038/s41598-025-13601-3，PMID 40764730）
- https://pubmed.ncbi.nlm.nih.gov/40764730/ （eutils XML）与 https://arxiv.org/html/2409.06605 ；读了全文（arXiv HTML 方法节）加读了摘要（eutils XML）。
- 做了什么：两阶段；精修网络读 PET-CT、“上一轮 sigmoid 后的概率图”和累计交互坐标；训练时“以 p=0.2 随机把上一轮掩码换成全 0.5 的卷”；模拟交互按到错误区边界的距离抽样、偏向大错；训练每次 1 到 15 次交互，验证 10 次；整卷重预测。期刊摘要：无交互 Dice 0.722，十次交互 0.858；arXiv 摘要：0.713 到五次 0.824（版本不同，数字不同）。
- 重叠：(f) 读连续概率状态、整卷重预测。差别：整卷写回不受限；点击不是涂鸦；头颈单病灶。

### 16. Anatomy-Aware Promptable Segmentation with Online Interactive Training for AUTOPET V（UAM；Pablo Lozano-Jimenez, Sergio Romero-Tapiador, Ruben Tolosana 等，2026，arXiv 2608.28461）
- https://arxiv.org/abs/2608.28461 ；读了摘要。
- 做了什么：nnU-Net 家族，预训练后“在线交互阶段学习利用涂鸦提示”；器官监督；示踪剂分类器；“Dice 随每次提示单调上升”。
- 重叠：同一赛道基线。差别：无 T/O/P 分解、候选、撤回。

### 17. ScribblePrompt: Fast and Flexible Interactive Segmentation for Any Biomedical Image（Hallee E. Wong, Marianne Rakic, John Guttag 等，2024，ECCV 2024，arXiv 2312.07381）
- https://arxiv.org/abs/2312.07381 与 https://arxiv.org/html/2312.07381 ；读了全文（HTML）。
- 做了什么：涂鸦、点击、框；“纠正涂鸦或点击从上一轮预测与真值的错误区抽，正的来自假阴、负的来自假阳”；上一轮预测作输入；二维任务（按轴取切片）。
- 重叠：状态相关的笔模拟。差别：二维；无候选、撤回、配对。

### 18. SAM-Med3D: Towards General-purpose Segmentation Models for Volumetric Medical Images（Haoyu Wang, Sizheng Guo, Jin Ye 等，2023，arXiv 2310.15161）
- https://arxiv.org/abs/2310.15161 ；读了摘要。做了什么：“完全可学的三维结构”，少量三维点提示。重叠与差别：通用三维提示模型，和六条主张都不重叠，只作基线类别。

### 19. Segment anything in medical images（MedSAM；Jun Ma, Yuting He, Feifei Li 等，2024，Nature Communications 15:654，arXiv 2304.12306）
- https://arxiv.org/abs/2304.12306 ；读了摘要（Nature 页跳登录页）。做了什么：1,570,263 对图像掩码、10 种模态、30 多种癌症的通用模型。重叠：无；基线类别。

### 20. SegVol: Universal and Interactive Volumetric Medical Image Segmentation（Yuxin Du, Fan Bai, Tiejun Huang 等，2024，NeurIPS 2024 Spotlight，arXiv 2311.13385）
- https://arxiv.org/abs/2311.13385 ；读了摘要。做了什么：语义加空间提示，200 多类，zoom-out-zoom-in，9 万无标注加 6 千有标注 CT。重叠：无；基线类别。

### 21. Reviving Iterative Training with Mask Guidance for Interactive Segmentation（RITM；Konstantin Sofiiuk, Ilia A. Petrov, Anton Konushin，2022，ICIP 2022，arXiv 2102.06583）
- https://arxiv.org/abs/2102.06583 ；读了摘要。做了什么：前馈模型“使用前几步的分割掩码”，能“从外部掩码出发修正”。重叠：(f) 读上一轮状态。差别：二值掩码，整图重出。

### 22. SimpleClick: Interactive Image Segmentation with Simple Vision Transformers（Qin Liu, Zhenlin Xu, Gedas Bertasius 等，2023，ICCV 2023，arXiv 2210.11006）
- https://arxiv.org/abs/2210.11006 ；读了摘要。做了什么：平面 ViT（MAE 预训练），“对称补丁嵌入层把点击编进骨干”。重叠：笔的稠密编码最小做法；与六条主张不重叠。

### 23. InterFormer: Real-time Interactive Image Segmentation（You Huang, Hao Yang, Ke Sun 等，2023，ICCV 2023，arXiv 2304.02942）
- https://arxiv.org/abs/2304.02942 ；读了摘要。做了什么：I-MSA 轻量模块在预处理特征上实时响应点击，重算力预处理与轻交互分离。重叠：无。

### 24. Sliding Window FastEdit: A Framework for Lesion Annotation in Whole-body PET Images（Matthias Hadlich, Zdravko Marinov, Moon Kim 等，2023，arXiv 2311.14482；仓库记 ISBI 2024，来源页未显示）
- https://arxiv.org/abs/2311.14482 ；读了摘要。做了什么：滑窗交互方案处理整卷、不裁不缩，“10 次点击迭代”得高质量结果，AutoPET 与 HECKTOR。重叠：同数据领域的滑窗做法。差别：点击、无候选和撤回。

### 25. DeepIGeoS: A Deep Interactive Geodesic Framework for Medical Image Segmentation（Guotai Wang, Maria A. Zuluaga, Wenqi Li 等，2017，arXiv 1707.00652；期刊版 TPAMI 来源页未显示）
- https://arxiv.org/abs/1707.00652 ；读了摘要。做了什么：两个 CNN，第二个“读用户交互与初始分割给出精修”；交互经测地距离（沿影像走的最短路代价）变换输入；可反传的 CRF 把交互当硬约束。重叠：(c) 的“从笔出发沿场传播”。差别：测地距离是累加代价，不是最弱一环；不可学的场。

### 26. MIDeepSeg: Minimally Interactive Segmentation of Unseen Objects from Medical Images Using Deep Learning（Xiangde Luo, Guotai Wang, Tao Song 等，2021，arXiv 2104.12166）
- https://arxiv.org/abs/2104.12166 ；读了摘要。做了什么：内缘点经“指数化测地距离”编码；初始分割加少量点击精修；泛化到未见对象。重叠：同 25。

### 27. iSegFormer: Interactive Segmentation via Transformers with Application to 3D Knee MR Images（Qin Liu, Zhenlin Xu, Yining Jiao 等，2022，MICCAI 2022，arXiv 2112.11325）
- https://arxiv.org/abs/2112.11325 ；读了摘要。做了什么：Swin 加 MLP 解码器用于交互式三维膝关节 MR。重叠：无。

### 28. SAM 2: Segment Anything in Images and Videos（Nikhila Ravi, Valentin Gabeur, Yuan-Ting Hu 等，2024，arXiv 2408.00714）
- https://arxiv.org/abs/2408.00714 ；读了摘要。做了什么：图像与视频可提示分割，流式记忆，视频上交互少三倍。重叠：(a) 的“记忆历史状态”只是同类词；不做撤回候选。

### 29. Segment Anything in High Quality（HQ-SAM；Lei Ke, Mingqiao Ye, Martin Danelljan 等，2023，NeurIPS 2023，arXiv 2306.01567）
- https://arxiv.org/abs/2306.01567 ；读了摘要。做了什么：可学的高质量输出 token 注入 SAM 掩码解码器，SAM 冻结，4.4 万精细掩码训 4 小时。重叠：无。

### 30. autoPET V 交互赛道官方说明（autopet-v.grand-challenge.org 与 lab-midas/autoPETV 仓库，2026）
- https://autopet-v.grand-challenge.org/task/ 、/autopet-v/ 、/evaluation/ 、/datasets/ 、/timeline/ ，仓库 README 与 interactive/simulate_scribbles.py；读了全文。
- 写了什么：先出初始分割，再按“针对假阳和假阴区域的涂鸦”迭代改进；两类评测，第一类算法生成、可复现、每例固定步数，第二类临床医生涂鸦、步数不定；每例“6 步：1 次初始预测加 5 次纠正”，涂鸦落在“模型最大错误区”，多分给背景笔、漏分给前景笔；三种画法 centerline、random、boundary，画在最大面积的那一层；输出高斯热图或坐标；排名 AUC-Dice 50% 加 AUC-DMM 50%（梯形法则按步积分），另报终 Dice、DMM、FPV、FNV；数据 FDG 1014 例/501 患者加 513 阴性对照、PSMA 597 例、DeepPSMA 100 患者；最终测试 200 例，四中心各 50；2026-04-01 开赛，09-01 截止。
- 重叠：这就是我们冻结的模拟器与评测口径的来源。差别：不涉及六条主张。

## 三、第二部分：2025 到 2026 年新工作与原理来源，按六条主张归类

### (a) 局部撤回候选并与范围、续修、不改同台打分
- Queries Knew More Than We Thought: Uncovering Latent Knowledge in Segmentation Models（HYDRA；Ignacio M. De la Jara, Cristian Rodriguez-Opazo, Damith Ranasinghe，2026，arXiv 2609.20283）｜https://arxiv.org/abs/2609.20283 与 /html/ ；读了全文。小选择器“只在缓存的冻结输出上训练”，推理时“把候选和一个明确的保持基线选项一起打分”，只有“留出集标定的间隔”够大才动，训练标签是“按与真值 IoU 选出的最优动作”，用“收益加权交叉熵”。全自动、无用户、DETR 系与 SAM 3、自然图像。重叠 (a) 的“不改作为候选同台打分”和 (d) 的收益标签来自真实变化；差别是没有撤回候选，也不由一笔定位。
- SLIP: Segmentation with Low-latency Interactive Prompting for 3D Medical Images（Baptiste Podvin, Alexandre Ancel, Flavio Milana 等，2026，arXiv 2607.22332）｜https://arxiv.org/abs/2607.22332 ；读了摘要。“支持可逆提示而不用重算图像特征”，由用户触发；真人用户研究。差别：撤回是用户动作，不是模型判断。
- MAIS: Memory-Attention for Interactive Segmentation（Mauricio Orbes-Arteaga, Oeslle Lucena, Sabastien Ourselin 等，2025，MIDL 2025，arXiv 2505.07511）｜https://arxiv.org/abs/2505.07511 ；读了摘要。“存过去的用户输入和分割状态”，避免重复纠正。差别：记忆是输入，不生成撤回。
- 加上第二节的 LIM-Net（整层退回）、IBISAgent（整步退回）、Correction-aware（跟踪用户改口的位置）、SAM 2（记忆）。

### (b) 纠错场景三类配对联合学习
- 第二节的 CPC-SAM（中心点对随机点一致）、VTMR（两种起点一致）、Prompt-RIS（实例对比）、nnInteractive（随机标签组合消歧）、EFPNet（每轮按 Mt−1 与新点击重算目标）。
- Exploring Cycle Consistency Learning in Interactive Volume Segmentation（Qin Liu, Meng Zheng, Benjamin Planche 等，2023/2024，arXiv 2303.06493）｜https://arxiv.org/abs/2303.06493 ；读了摘要。“把中间分割沿反向传播回起始切片”的环一致性损失。差别：一致性在切片传播上，不在换笔换目标。
- Learning from Noisy Prompts: Saliency-Guided Prompt Distillation for Robust Segmentation with SAM（Jingxuan Kang, Ziqi Zhang, Shaoming Zheng 等，2026，CVPR 2026 Findings，arXiv 2604.23314）｜https://arxiv.org/abs/2604.23314 ；读了摘要。显著性头、“成对切片一致性”、从相邻切片蒸馏提示。差别：鲁棒性来自提示蒸馏，不是配对监督。
- 本次打开的来源里没有“同一纠错状态并存几处错，换一笔换一处当 T，没被指的那处必须不动”这种成对监督。

### (c) 从笔出发沿学出的误差场做可微 minimax 传播
- Iterative Relative Fuzzy Connectedness for Multiple Objects with Multiple Seeds（Krzysztof Chris Ciesielski, Jayaram K. Udupa, Punam K. Saha, Ying Zhuge，2007，CVIU，PMID 18769655）｜https://pubmed.ncbi.nlm.nih.gov/18769655/ （eutils XML）；读了摘要。“基于任意两个图像元素之间连通强度”的分割，多目标多种子。
- GPU-based relative fuzzy connectedness image segmentation（Ying Zhuge, Krzysztof C. Ciesielski, Jayaram K. Udupa, Robert W. Miller，2013，Medical Physics，PMID 23298094）｜https://pubmed.ncbi.nlm.nih.gov/23298094/ （eutils XML）；读了摘要。“最常见的 FC 分割优化一个 ℓ∞ 型能量”，即 RFC 与 IRFC，线性时间。ℓ∞ 能量就是路径最弱一环，这是从种子出发沿亲和场做 minimax 传播的经典先例。
- Joint graph cut and relative fuzzy connectedness image segmentation algorithm（Ciesielski 等，2013，Medical Image Analysis，PMID 23880374）｜https://pubmed.ncbi.nlm.nih.gov/23880374/ （eutils XML）；读了摘要。RFC 对种子选择鲁棒、免 GC 的收缩问题，GC 对“从边界薄弱处漏出”控制更强；这是 minimax 传播的已知短板。
- Widest-Path Reachability Fields for Connectivity-Preserving Slender Structure Segmentation（WPRF；Youcheng Zong, Runda Jia, Minxuan Hu 等，2026，arXiv 2607.07123）｜https://arxiv.org/abs/2607.07123 与 /html/ ；读了全文。“可微的 Max-Min 可达性目标”，在步长 4 的图上做动态规划（DP，逐步递推），边权来自亲和头的 sigmoid，源点从真值骨架抽样，递推 r_{t+1}(v)=max(r_t(v), max_p min(r_t(p), w_pv))；只做训练损失，推理只阈值化；血管、道路、裂缝。
- Online Learning of Network Bottlenecks via Minimax Paths（Niklas Åkerblom, Fazeleh Sadat Hoseini, Morteza Haghir Chehreghani，2023，Machine Learning 112:131–150，arXiv 2109.08467）｜https://arxiv.org/abs/2109.08467 ；读了摘要。网络瓶颈的 minimax 路径学习，组合半 bandit；只说明“学 minimax 路径”在别的领域已有。
- 第二节的 DeepIGeoS、MIDeepSeg 是累加代价的测地传播，ClickAttention 是相似度扩散。
- 本次打开的来源里，“从用户笔出发、沿网络学出的误差场、把可微 Max-Min 递推当前向绑定算子”这个组合没有；部件（种子 minimax、可微 Max-Min DP）都有。

### (d) 嵌套范围候选加收益头
- MultiSeg: Semantically Meaningful, Scale-Diverse Segmentations From Minimal User Input（Jun Hao Liew, Scott Cohen, Brian Price 等，2019，ICCV 2019，pp. 662–670）｜https://openaccess.thecvf.com/content_ICCV_2019/html/Liew_MultiSeg_Semantically_Meaningful_Scale-Diverse_Segmentations_From_Minimal_User_Input_ICCV_2019_paper.html （curl）；读了摘要。“一组二维尺度先验生成一组随尺度变化、符合用户输入的提案”，合成多样训练样本，用户挑最近的。
- GraCo: Granularity-Controllable Interactive Segmentation（Yian Zhao, Kehan Li, Zesen Cheng 等，2024，CVPR 2024 Highlight，arXiv 2405.00587）｜https://arxiv.org/abs/2405.00587 ；读了摘要。“通过额外输入参数精确控制预测粒度”，自动生成掩码-粒度对。
- PiClick: Picking the desired mask from multiple candidates in click-based interactive segmentation（Cilin Yan, Haochen Wang, Jie Liu 等，2023，arXiv 2304.11609）｜https://arxiv.org/abs/2304.11609 ；读了摘要。出所有合理掩码，Target Reasoning 模块“自动建议用户想要的那个”。
- SegAgent: Exploring Pixel Understanding Capabilities in MLLMs by Imitating Human Annotator Trajectories（Muzhi Zhu, Yuzhuo Tian, Hao Chen 等，2025，CVPR 2025，arXiv 2503.08625）｜https://arxiv.org/abs/2503.08625 ；读了摘要。分割当多步马尔可夫决策过程，StaR 与 PRM 引导树搜索。
- User-preference alignment with uncertainty-aware interactive rectification for liver organ and tumor segmentation and analysis from CT images（UAIR；Guangyuan Zhao, Yang Wang, Chen Gong 等，2026，npj Digital Medicine，PMC13230871）｜https://pmc.ncbi.nlm.nih.gov/articles/PMC13230871/ ；读了摘要。按不确定性给“一小组多样候选”让医生选，迭代；肝肿瘤三轮 Dice 0.776 对手工提示 0.685。
- 加上 HYDRA（收益加权、真值最优动作标签）、PRISM、Correction-aware、SAM 系的多掩码加 IoU 头。
- 结论：多候选加分数头已有十余个先例，HYDRA 的标签来自冻结输出的真实收益与“保持基线”选项同台；同一状态内预测终 Dice 与预测 Dice 变化排序等价（PLAN 第三节已指出）。“嵌套范围”只是候选族的形状。

### (e) 按 Dice 账推出的不对称门槛
- Thresholding Classifiers to Maximize F1 Score（Zachary Chase Lipton, Charles Elkan, Balakrishnan Narayanaswamy，2014，arXiv 1402.1892）｜https://arxiv.org/abs/1402.1892 ；读了摘要。原话“若分类器输出是标定好的条件概率，最优门槛是最优 F1 的一半”。Dice 就是 F1，“加笔 p > D/2”是这条定理的直接应用；删笔 p < D/2 是同一门槛的另一侧，不是另一条规则。
- Marginal Thresholding in Noisy Image Segmentation（Marcus Nordström, Henrik Hult, Atsuto Maki，2023，arXiv 2304.04116）｜https://arxiv.org/abs/2304.04116 ；读了摘要。“soft-Dice 的最优解可由交叉熵解按一个事先未知但可算的门槛得到”。
- On Image Segmentation With Noisy Labels: Characterization and Volume Properties of the Optimal Solutions to Accuracy and Dice（Marcus Nordström, Henrik Hult, Jonas Söderberg 等，2022，arXiv 2206.06484）｜https://arxiv.org/abs/2206.06484 ；读了摘要。Dice 最优解的体积可明显偏离期望体积。
- RankSEG: A Consistent Ranking-based Framework for Segmentation（Ben Dai, Chunlin Li，2023，JMLR 24(224)，arXiv 2206.13086）｜https://arxiv.org/abs/2206.13086 ；读了摘要。“现有阈值化框架配多数损失对 Dice/IoU 不一致”，提出排序式插入规则 RankDice。
- 结论：门槛随 D 走且 D 由模型自估，是 Lipton 定理加一个 D 的估计器；项目自己的 T1 试验（TRAIN 学两个全局门槛，第五轮 −0.001、误删真病灶大增，见简报第五节第 7 条）也说明全局门槛不是贡献点。

### (f) 读连续概率状态、所指区域整片重预测、写回受限
- MFP: Making Full Use of Probability Maps for Interactive Image Segmentation（Chaewon Lee, Seon-Ho Lee, Chang-Su Kim，2024，CVPR 2024，arXiv 2404.18448）｜https://arxiv.org/abs/2404.18448 ；读了摘要。“先调制上一轮概率图以强化用户指定对象，再把调制后的概率图当额外输入”。
- Clore: Interactive Pathology Image Segmentation with Click-based Local Refinement（Tiantong Wang, Minfan Zhao, Jun Shi 等，2026，arXiv 2603.27625）｜https://arxiv.org/abs/2603.27625 与 /html/ ；读了全文。前 n 次（默认 5）全局预测，之后在“当前与上一轮掩码差异里靠近点击的最大连通域”外接框内精修，合并时“找精修与上一轮的分歧，选含最新点击的连通块，加上或减去”。
- Focused and Collaborative Feedback Integration for Interactive Image Segmentation（FCFI；Qiaoqiao Wei, Hui Zhang, Jun-Hai Yong，2023，CVPR 2023，arXiv 2303.11880）｜https://arxiv.org/abs/2303.11880 ；读了摘要。“聚焦新点击周围局部区域，按高层特征相似度修正反馈”，并交替更新反馈与特征。
- FocalClick-XL: Towards Unified and High-quality Interactive Segmentation（Xi Chen, Hengshuang Zhao 等，2025，arXiv 2506.14686）｜https://arxiv.org/abs/2506.14686 ；读了摘要。粗到细设计拆成 context、object、detail 三个子网，对象级提示层编码点击、涂鸦、框、粗掩码。
- U-CFR: Uncertainty-Guided Cascade Forward Refinement for Interactive Segmentation（Elijah Danquah Darko, Min Xian, Terence Soule 等，2026，ICPR 2026，arXiv 2607.20705）｜https://arxiv.org/abs/2607.20705 ；读了摘要。每次交互后用边界不确定性放内部伪点击自我修正。
- 加上第二节的 2S-ICR（概率输入、整卷重出）、FocalClick、VISTA3D、VTMR、EFPNet、PRISM。
- 结论：读概率状态（MFP、2S-ICR）和“所指连通块内改、块外不动”（FocalClick、VISTA3D、VTMR、Clore、EFPNet）各有多个先例，组合不构成贡献；三维 PET/CT 涂鸦上的实现是工程适配。

### PET/CT 同赛道 2025 到 2026 年工作与模拟器（不对应单条主张）
- BS: Take the Hint - Interactive Multitracer PET/CT Lesion Segmentation with a Scribble-Conditioned ResEnc U-Net（Marven Sherif, Amgad Elmasry, Youssef Ghazal 等，2026，arXiv 2609.01554）｜读了摘要。四通道 CT、PET、前景笔、背景笔，笔通道零初始化；Dice 0.554 到五轮 0.751，约 85% 增益在第一笔。
- Pretrained, Curriculum-Tuned, and Ensembled: A Tracer-Aware Interactive Segmentation Pipeline for AutoPET V（TRIAGE；Xinglong Liang, Chunyao Lu, Tianyu Zhang 等，2026，arXiv 2608.30844）｜读了摘要。初始预测“与累计前景/背景涂鸦合并后由第二个交互网络精修”，课程式训练加集成。
- Three-Phase Scribble-Adaptive Curriculum Learning for autoPETV Grand Challenge（Libo Zhang, Yue Ning 等，2026，arXiv 2608.22096）｜读了摘要。三阶段：静默交互通道的全自动、真值涂鸦随机可见、“在线模拟至多五步错误驱动纠正来适应自己的错误”；约 1.4 亿参数 ResEnc U-Net，1811 例，五折 logit 平均。
- Towards Interactive Lesion Segmentation in Whole-Body PET/CT with Promptable Models（Maximilian Rokuss, Yannick Kirchhoff, Fabian Isensee 等，2025，arXiv 2508.21680）｜读了摘要。autoPET IV 任务 1，前景/背景点击作输入通道，在线模拟交互与自定义点采样。
- Rethinking Annotator Simulation: Realistic Evaluation of Whole-Body PET Lesion Interactive Segmentation Methods（Zdravko Marinov, Moon Kim, Jens Kleesiek 等，2024，arXiv 2404.01816）｜读了摘要。机器人用户和真人标注者的表现与行为明显不同，提出带点击变异和标注者分歧的机器人用户。
- Dynamic Prompt Generation for Interactive 3D Medical Image Segmentation Training（Tidiane Camaret Ndir, Alexander Pfefferle, Robin Tibor Schirrmeister，2025，arXiv 2510.03189）｜读了摘要。动态体提示生成加内容自适应裁剪，模拟真实交互模式与顺序精修反馈。
- SAMI3D-DW（Ping Gong 等，2026，arXiv 2609.25743）、BrainIAC（Wentian Xu 等，2026，arXiv 2609.23026）、LeCor（Yi Luo 等，2026，arXiv 2609.09477）、SCISSR（Haonan Ping 等，2026，arXiv 2603.18544）、MediRound（Qinyue Tong 等，2025，arXiv 2511.12110）、Refining 3D Medical Segmentation with Verbal Instruction（Kangxian Xie 等，2026，arXiv 2603.14496）、InsightSeg（Vanshika Vats 等，2026，arXiv 2609.02002）、IMPACT-Scribe（Qian Yin 等，2026，arXiv 2605.01668）｜都读了摘要；分别是通用三维交互、在线适应、元学习测试时训练、手术涂鸦编码、多轮语言推理分割、语言指令改形状、复用纠正经验、时序动作标注；都没有撤回候选、三类配对、minimax 绑定，列入登记只为说明 2025 到 2026 年的近邻面貌。

## 四、结论表与写法

| 候选主张 | 新意等级 | 最近的先例（已核实） | 论文里怎么写才站得住 |
|---|---|---|---|
| (a) 由这一笔定位，在上一轮反向改动里给几个范围的局部撤回候选，和范围、续修、不改一起由同一打分器挑 | 有近邻但有可辩的差别 | LIM-Net 整层退回（门槛二选一）；IBISAgent 整步退回；SLIP 用户触发可逆；Correction-aware 跟踪用户改口位置；HYDRA 把“保持基线”当候选与其他候选同台打分 | 写“退回上一轮已有整层、整步两种粗粒度做法，保持不改作为候选同台打分在自动分割里已有；本次检索未见把撤回候选限定为系统上一轮写回的反向改动、由当前这一笔定位、给出多个范围并和沿笔范围、续修、不改一起打分的做法”。附四臂执行对照和患者配对 95% 区间，含零就写“证据不足”。 |
| (b) 纠错场景三类配对联合学习 | 有近邻但有可辩的差别 | CPC-SAM、VTMR（同目标换提示或起点要一致）；Prompt-RIS（同实例拉近、异实例推开）；nnInteractive、EFPNet、RITM（状态变了按定义重算是迭代训练常规） | 第二、三类明写有先例，只保留“同一纠错状态并存几处错、换一笔换一处当 T、没被指的那处必须不动”作为本次检索未见的成对监督；证伪对照是正确配对、独立监督、打乱配对，读数用换笔跟随、换画法一致、断桥方向正确率和五轮 Dice。 |
| (c) 从笔出发沿学出的误差场做可微 minimax 传播 | 有近邻但有可辩的差别 | fuzzy connectedness（RFC/IRFC 优化 ℓ∞ 能量，种子出发的最弱一环最强路径，1990 年代起）；WPRF（2026，可微 Max-Min 动态规划，但只作训练损失、源点取真值骨架）；DeepIGeoS/MIDeepSeg（累加测地代价） | 写“minimax 传播是 fuzzy connectedness 的经典算子，可微 Max-Min 递推在细长结构分割里已作训练损失；本次检索未见把它当交互修正网络的前向绑定算子、源点取用户笔、边权取学出的误差场”。要正面写已知短板：单条强路径漏出（GC 与 RFC 联合那篇所说的“从边界薄弱处漏”），并给对照（逐体素分类头）。 |
| (d) 嵌套范围候选加收益头，标签来自回放的真实 Dice 变化 | 已有人做 | MultiSeg、GraCo（尺度/粒度候选族）；SAM、HQ-SAM、PRISM、PiClick、Correction-aware（多候选加分数头）；HYDRA（收益加权、真值最优动作标签、保持基线选项） | 不列为贡献。写成“执行端用多候选加分数头的通行做法，分数头按候选的 Dice 变化监督”，引 HYDRA 说明同一状态内终 Dice 与 Dice 变化排序等价。 |
| (e) 加笔 p > D/2、删笔 p < D/2，D 由模型自估 | 已有人做 | Lipton 等 2014（F1 最优门槛 = 最优 F1 的一半）；Nordström 等 2022、2023（soft-Dice 最优解的门槛与体积性质）；RankSEG（阈值化对 Dice 不一致，排序式规则） | 写成“按 Lipton 等的 F1 最优门槛结果推出执行门槛，D 用模型自估量代替”，列为推导出的通用规则而非贡献；并写明项目 T1 全局门槛试验（TRAIN）为负结果。 |
| (f) 读连续前一轮概率、所指区域整片重预测、写回限定在所指块 | 已有人做 | MFP、2S-ICR（概率状态输入）；FocalClick、VISTA3D、VTMR、Clore、EFPNet（只改含笔的连通块或其外接框，其余不动） | 不列为贡献。写成“沿用概率状态输入与含笔连通块写回的既有做法，在三维 PET/CT 涂鸦上的实现细节见方法节”。 |

写法规则（全文适用）：

- 只写“本次检索未见”，并在相关工作里正面列出本表第三列的先例；不写首创、不写读懂医生意图、不写通用医学模型。
- “intent”一词已被 Structured Click Control（“结构化点击意图”）、EFPNet（“全局用户意图”）、nnInteractive（“用户意图常有歧义”）、DIG（隐式学意图）用过，论文里用它只能指操作定义（指哪处、多大、修到哪、和上一笔的关系、值不值），并说明监督来自冻结模拟器和连通错误定义。
- 近邻密度决定篇幅：相关工作要分五段写，局部合并（FocalClick、VISTA3D、VTMR、Clore、EFPNet）、退回与记忆（LIM-Net、IBISAgent、SLIP、MAIS、Correction-aware）、候选与选择（MultiSeg、GraCo、PiClick、PRISM、HYDRA、UAIR）、一致性与对比（CPC-SAM、VTMR、Prompt-RIS）、PET/CT 交互（2S-ICR、UAM、BS、TRIAGE、Libo Zhang、Rokuss、SW-FastEdit、Marinov）。
- 原本简报第六节只认两条待检验主张 (a)(b)，现在加核 (c) 到 (f) 后，(c) 同属“有近邻但有可辩的差别”，(d)(e)(f) 为已有人做；主张数从两条变三条，等级不升。

## 五、检索词与缺口

- 已做的 22 次 WebSearch：各篇题名核对 7 次；interactive segmentation undo revert previous edit learned rollback；correction intent interactive segmentation user intention click scribble；scribble-guided correction medical 3D segmentation refinement；iterative refinement propagate click connected component error region localized update preserve unclicked regions；state-dependent interactive segmentation conditioned on previous mask re-predicts only clicked region；learned scope interactive segmentation predict extent of click influence；referring correction segmentation language-guided mask correction；interactive segmentation candidate masks predict Dice gain selection training labels from replay；differentiable minimax path bottleneck path widest path segmentation learned cost map；asymmetric decision threshold add remove voxels Dice optimal threshold D/2；pairwise consistency training interactive segmentation two prompts same target different target swap contrastive；whole-body PET/CT interactive lesion segmentation scribble refinement autoPET 2026（两次）；autoPET V 官方说明。
- 因额度用尽没做成的 5 条：“interactive segmentation revert previous round mask fusion select better round”；“intent-aware interactive medical image segmentation 2026”；“expected improvement / predicted gain head candidate selection 2025 2026”；“one-stage regional refinement focus region latest click 2026”；“autoPET V github simulate_scribbles”（最后一条改走仓库浅克隆完成）。这些方向的覆盖靠 arXiv API 题名查和已开页面的引用补上，但 2026 年下半年的新预印本可能有漏，建议投稿前再查一次 (a) 与 (c)。
- 未核实（只见检索摘录，已放 unverified 文件）：Click-based interactive image segmentation with global hints and local corrections（Engineering Applications of Artificial Intelligence 2026，ScienceDirect 被拦、无 arXiv）；Semantic reweighting and attention field supervision for interactive image segmentation（Digital Signal Processing 2026，同上）；Udupa & Samarasekera 1996 的 fuzzy connectedness 原始论文（Elsevier 被拦，改用 2007、2013 两篇 PubMed 记录）；LORE（MICCAI 2026 卫星会，本次未开）。前两篇题名与 (f)(d) 有关，若能开到全文要补核。
