# PET/CT 交互分割公开水平与 autoPET V 协议核查（SOTA-CONTEXT，2026-10-07）

结论：本项目 TEST 第五轮 Dice 到 0.80 只能说“达到公开报告的交互 PET/CT 五轮涂鸦水平、与已完成的最强基线持平”，不能说刷新 SOTA（state of the art，领域最好成绩）；到 0.85 可以说“在同一锁定测试集、同一模拟器下超过已完成的全部基线，并高于我们能打开的全部五轮涂鸦公开数字（五折交叉验证 0.751 和 0.810，FDG+PSMA 混合）”，但因为数据集、起点、平均方式都不同，仍不能写“领域 SOTA”；唯一能让 SOTA 成立的地方是 autoPET V 官方 200 例四中心测试集榜单，本项目没有参加，榜单到今天也没有可打开的文字版。

写作约定：数字后面标集合（TRAIN/VAL/TEST、CV 即交叉验证、官方测试集）和协议（点击还是涂鸦、几轮、按例还是按患者平均）。来源标“来源 n”，对应第七节清单；每条来源的核实记录在 `5-ultimate-plan-20261007/04-cross-domain/registers/medical-cv/sota-and-protocol.json`。项目数字的出处是 `2-results-and-models/results-all-systems.md` 第四节和 `2-results-and-models/data-models-and-protocol.md` 1.1 到 1.6 节。

## 零、核实了什么、什么没打开

打开并读过的来源：

- autoPET V 官方网站四个子页（描述、数据、评测、时间线）和 www.autopet.org 的 autopetv、autopetiv 两页。
- 官方仓库 lab-midas/autoPETV 的本地只读克隆（提交 4a20268，2026-07-01）：`interactive/simulate_scribbles.py`、`interactive/interactive_loop.py`、`metrics.py`、`interactive/README.md`、两份教程笔记本、组织者的《Summary of the autoPET challenge series (I–IV)》PDF。
- autoPET I 结果论文（Nature Machine Intelligence 2024 网页版）、autoPET II 结果论文（Journal of Nuclear Medicine，PubMed 记录和期刊页）、autoPET III 结果预印本（arXiv 2605.05775 全文）。
- autoPET IV 官方任务页、评测页、数据页和 lab-midas/autoPETCTIV README；参赛论文 7 篇（arXiv 全文或摘要）。
- PSMA 全自动分割论文 7 篇；2S-ICR 的 arXiv 版和 Scientific Reports 版（PMC 全文）；nnInteractive、SAM-Med3D、SegVol、VISTA3D、Marinov 2024 的 arXiv 页。

没打开、只能记“未找到可打开的来源”的：

- autoPET IV 总结预印本（SSRN 6841479，两种 URL 都返回 403）。它的数字只在检索摘录里，放进 `sota-and-protocol.unverified.json`。
- autoPET V 初赛和决赛榜单页：JavaScript 渲染，静态页只有“Loading Results...”。
- autoPET I 冠军数字在 Nature 论文正文里只出现在图中，文字版没有；改用组织者 PDF 的表 1。
- 一条检索摘录提到“412 例三中心 68Ga-PSMA-11 nnU-Net，内部 Dice 0.70、外部 0.65 和 0.68”，没能定位到论文页。
- WebSearch 配额在第三轮用尽，之后只用已知 URL 直接打开，没有再做新检索。

## 一、autoPET 五届：任务、数据、指标、冠军数字

### 1.1 全自动四届的冠军成绩（官方最终测试集，按例平均，Dice 只算有病灶的例）

| 届 | 年 | 任务 | 训练数据 | 测试集 | 冠军：Dice / FNV / FPV | nnU-Net 基线 | 来源 |
|---|---|---|---|---|---|---|---|
| autoPET I | 2022 | 全身 FDG PET/CT 病灶全自动分割 | 1014 FDG 研究/900 患者（UKT 单中心） | 150 例 FDG：UKT 100 + LMU 50 | Blackbean 0.6226 / 0.5445 mL / 2.8372 mL；第二名 BDAV 0.6208 / 0.7518 / 3.6111 | 0.662 / 1.2423 / 9.3157 | 1、2 |
| autoPET II | 2023 | 同上，强调跨域泛化 | 1014 FDG（UKT） | 200 例、5 个域：UKT 50、UKT-Patho 25、LMU 25、LMU-PSMA 50、UKE 儿科 50 | BAMF Health 0.5038 / 8.4154 / 87.839；第二名 Blackbean 0.5198 / 9.7205 / 161.392 | 0.5024 / 18.9489 / 176.43 | 1、3 |
| autoPET III | 2024 | 多示踪剂多中心（FDG + PSMA） | 1014 FDG（UKT）+ 597 PSMA（LMU） | 200 例：FDG-UKT 50、PSMA-LMU 50、FDG-LMU 50、PSMA-UKT 50；156 阳性、44 阴性 | LesionTracer 0.6616 / 3.1842 / 2.7849；第二名 IKIM 0.6496 / 3.2451 / 3.0438 | 0.4523 / 7.3355 / 31.5028 | 1、4 |
| autoPET IV（任务 1） | 2025 | 预模拟点击的人机交互分割 | 1014 FDG + 597 PSMA + 预模拟点击 | 200 例，同 III 的四个子集 | BIRTH 0.7412 / 2.1665 / 1.2898（Dice@last，10 + 10 点击后）；第二名 LesionLocator 0.7236 / 1.7511 / 2.4750 | 0.6349 / 3.0666 / 10.8394 | 1、6、7 |

每届的补充说明：

- autoPET I：排名不只看 Dice。nnU-Net 基线 Dice 0.662 高于冠军 0.6226，但 FNV 和 FPV 差很多，所以不是冠军（来源 1）。结果论文（来源 2）正文给的是定性结论：150 例私有测试集来自两家机构；最高名次算法的集成模型与第二位阅片者表现相近（Extended Data Fig. 9）；Dice 与平均病灶体积正相关（p = 0.0002），小病灶更常被漏。一篇参赛论文在初赛测试集上报 Dice 0.7574、FPV 0.0299、FNV 0.2538（来源 31），初赛集与最终集不是一回事，只作水平参考。
- autoPET II：17 队；训练只有 FDG，测试含 50 例 PSMA（LMU-PSMA 域），冠军 Dice 掉到 0.5038，FPV 87.8 mL；结论是“单源域泛化仍是难题，算法还不能直接用于多样的临床环境”（来源 3）。
- autoPET III：17 队 27 个算法；排名权重 Dice 0.5、FPV 0.25、FNV 0.25，先按四个子集算再合名次；Dice 只在有病灶的例上算（原文：“The DSC is computed exclusively on lesion-positive samples”）。冠军 LesionTracer A 分子集 Dice：FDG-UKT 0.7702、PSMA-LMU 0.6433、FDG-LMU 0.6619、PSMA-UKT 0.5711；基线分别 0.6822、0.4741、0.5017、0.1512。PSMA-LMU 子集有一位初级阅片者的 25 例二次标注，冠军在三项指标上与之相当或更好；FDG-LMU 子集冠军仍低于二次阅片一致性（来源 4）。
- autoPET IV：见 1.2。

### 1.2 autoPET IV（2025）交互任务的协议

- 11 个交互步：第 1 步 0 个点击，之后每步加一个肿瘤（前景）点击和一个背景点击，到第 11 步满 10 + 10 个。点击是预先模拟好的三维坐标（JSON），训练和测试都预模拟，不依赖模型自己的错误（来源 6、7、8）。
- 指标六项：DSC@last、FPV@last、FNV@last 各算最后一步；AUC-DSC、AUC-FPV、AUC-FNV（AUC 即曲线下面积）按梯形法则对步 0 到 10 积分。权重 0.25/0.125/0.125/0.25/0.125/0.125；没有病灶的例只用 FPV；四个子集分别算再合名次（来源 7）。
- 冠军 BIRTH 分子集 Dice@last：LMU-FDG 0.7010、LMU-PSMA 0.7437、UKT-FDG 0.8242、UKT-PSMA 0.6959（来源 6）。
- 参赛队公开的验证数字（各自划分，不是测试集）：Huang 等（来源 9）PSMA 验证模型 Dice 0.619（0 点）→ 0.855（5 点）→ 0.871（10 点），FDG 0.788 → 0.870 → 0.877；LesionLocator（来源 8）五折 CV 按官方评测：autoPET III 原模型 68.33 → 最佳配置最后一步 76.35，AUC 只用 0、3、7、10 点算得 2.22，并指出 EDT（欧氏距离变换）编码点击稳定好于高斯核。

### 1.3 autoPET V（2026）交互赛道的协议（官方来源）

- 任务：先出初始分割，再按推理时给的稀疏涂鸦（scribble，一小段笔画）迭代修正；两种交互方式并行评测：标准化模拟交互（可复现）和医生真实涂鸦（来源 10）。
- 轮数：`interactive/README.md` 写“每个测试例 6 个交互步：1 次无涂鸦预测 + 5 次修正”；修正步按“模型最大错误区域”画笔，过分割画背景笔、欠分割画前景笔；三种画法 centerline、random、boundary 各分到三分之一测试例，对所有参赛者一致（来源 11）。官方材料内部有两处口径出入：教程笔记本写“第一笔按真值模拟，再按错误加最多 4 笔”；`interactive_loop.py` 的 `--max_iters` 默认 5（迭代 0 到 4）。两篇参赛论文都按“6 次推理：r0 无笔，r1 到 r5 每轮加一笔”描述（来源 12、13）。
- 选笔（`simulate_scribble_from_label`，第 389 到 455 行）：对错误掩码逐轴向切片做二维 8 邻接连通块（`cc3d.connected_components(slice_mask, connectivity=8)`），每层取最大块，再取所有层里面积最大的那层（`area > best_area` 严格大于才替换，所以平手留靠前的层），笔只画在这一层。centerline 取骨架最长路径并在路径超过 10 点时截掉两端各 10%；random 用种子 42 在块内随机两点连线；boundary 从随机起点沿内边缘走边界长度的 20%（来源 11）。
- 加删判定（`interactive_loop.py` 第 253 到 262 行）：`overseg = pred & ~gt`、`underseg = ~pred & gt` 各出一条候选笔，`if fp <= fn` 加前景笔，否则加背景笔；fp、fn 是两条候选笔的体素数，不是错误体积（来源 11）。
- 指标：AUC-Dice 50% + AUC-DMM 50%（DMM 即病灶检出匹配指标），AUC 按梯形法则对交互步积分，按测试子集算再平均；FPV、FNV 只作描述（来源 10、14）。`metrics.py` 的 `MetricEvaluator(overlap_threshold=0.1, connectivity=18)`：病灶实例按三维 18 邻接划分，IoU（交并比）不低于 0.1 算命中，多重匹配不罚；DMM 是把所有例的 TP/FP/FN 加总后算 F1；`calc_dice` 对空真值返回 NaN，即 Dice 只算有病灶的例（来源 11、15）。`interactive_loop.py` 用 `np.trapz(dice, iterations)` 按迭代序号积分，6 个状态时最大值 5，不归一化。
- 数据：训练 1014 FDG（900 患者）+ 597 PSMA（378 患者）+ DeepPSMA 100 例；最终测试 200 例四中心各 50（UKT、LMU、Peter MacCallum、Essen），另有 20 例（每中心 5 例）双医生标注做医生交互评测（来源 10、14）。
- 时间线：4 月 1 日开放，5 月 4 日初赛提交，7 月 15 日决赛提交，9 月 1 日关闭，9 月 27 日在 MICCAI 2026 现场报告，11 月初邀请写总结论文（来源 10）。到 2026-10-07 没有可打开的最终名次文字版。
- 参赛队公开数字（都是五折 CV，FDG+PSMA 混合，各自起点，不是测试集）：Sherif 等（来源 12）从 autoPET III 冠军权重微调，平均 Dice 0.554（r0）→ 0.722（r1）→ 0.751（r5），病灶 F1 0.528 → 0.704 → 0.733，约 85% 的增益来自第一笔；Zhang 和 Ning（来源 13）1.4 亿参数 ResEnc U-Net、三阶段课程、1811 例含 DeepPSMA，Dice 0.657 → 0.742（1 步）→ 0.810（5 步），AUC-Dice 3.836、AUC-DMM 3.869（最大 5，折成归一化约 0.767 和 0.774），第一笔约占 55% 增益；Liang 等（来源 16）只有方法，数字留空待赛后补。

### 1.4 autoPET IV 与 V 的差别

| 项 | autoPET IV（2025） | autoPET V（2026） |
|---|---|---|
| 交互形式 | 点击，三维坐标 | 涂鸦，单个轴向切片上的一串坐标 |
| 交互怎么来 | 预模拟，来自真值，与模型输出无关 | 按模型当前预测的最大错误块在线模拟（第一笔口径见 1.3） |
| 步数 | 11 步，0 到 10 + 10 个点击 | 6 步，0 到 5 笔 |
| 指标 | DSC/FPV/FNV@last 加三条 AUC，六项加权 | AUC-Dice 与 AUC-DMM 各一半，FPV/FNV 只描述 |
| 病灶级指标 | 无 | DMM：18 邻接实例、IoU ≥ 0.1、跨例加总 F1 |
| 测试集 | 200 例，UKT 与 LMU 两中心 | 200 例四中心，加 20 例医生交互 |

### 1.5 PSMA-PET-CT-Lesions 规模核对

597 研究/378 名男性患者，与 `data-models-and-protocol.md` 1.1 节一致；18F-PSMA-1007 369 例、68Ga-PSMA-11 228 例，与 1.2 节一致（来源 17、18）。阳性/阴性数两处官方来源不同：fdat 数据记录 v2 和 Scientific Data 论文写 539 有病灶/58 无病灶，autoPET V 数据页写 537/60。本项目三层划分里标准答案为空的扫描 9 + 35 + 14 = 58（1.1 节），对得上 539/58。三台扫描仪：GE Discovery 690 230 例、Siemens Biograph mCT Flow 20 251 例、Siemens Biograph 64-4R TruePoint 116 例（来源 18）。

## 二、PSMA PET/CT 全自动病灶分割的公开 Dice

| 论文 | 数据 | 模型 | Dice 与口径 | 备注 | 来源 |
|---|---|---|---|---|---|
| Jeblick 等，Sci Data 2026 | 本项目同一数据集 597 例，五折 CV | vanilla 3D fullres nnU-Net v2 | 按例中位 0.70（IQR 0.44 到 0.81），均值 0.59 ± 0.28，只算阳性例；病灶级召回 0.91、精确率 0.80、F1 0.81（重叠 1 体素即命中）；中位 FNV 1.64 mL、FPV 1.30 mL | 与本项目基座最接近的公开参照 | 18 |
| Rokuss 等（LesionTracer），arXiv 2024 | 1014 FDG + 597 PSMA，五折 CV，官方评测 | nnU-Net ResEncL + 器官监督 | PSMA 子集按例 60.01（ResEncL 基线 58.25）；FDG 77.28；总体 68.40 | autoPET III 冠军方法 | 19 |
| Dexl 等（autoPET III 总结），arXiv 2026 | 官方测试集 | 冠军 LesionTracer A | PSMA-LMU 0.6433、PSMA-UKT 0.5711（按例，只算阳性） | 唯一的 PSMA 官方测试集数字 | 4 |
| Abtahi 等（Fine-UNETR），arXiv 2026 | 373 例（299 训练/74 验证），外部 192 例 autoPET IV 数据 | Fine-UNETR | 验证集按例 66.63%，病灶检出 79.53%；外部 44.11% | 跨机构掉 22 点 | 20 |
| Yazdani 等，Cancer Imaging 2024 | 752 例 68Ga-PSMA-11 两中心，100 例有标注，20 例留出测试 | Swin UNETR 自监督预训练 | 病灶 Dice 0.68（20 例测试），比 nnU-Net 高 5% | 器官 + 病灶多类 | 21 |
| Kendrick 等，EJNMMI 2022 | 337 例 68Ga-PSMA-11（209 训练/128 测试，75 阳性 53 阴性） | nnU-Net | 体素级 Dice 均值 43.5% ± 21.5%、中位 50.7%（第二观察者 32%）；病灶级灵敏度 73.0%、PPV 88.2% | 生化复发人群，病灶小 | 22 |
| Perret 等，EJNMMI Research 2026 | 73 例 mCRPC（转移性去势抵抗前列腺癌）两中心 | nnU-Net | PET/CT 内部 0.83 ± 0.19、外部 0.76 ± 0.22 | 病灶负担重，Dice 自然高 | 23 |
| Tun 等，J Imaging Inform Med 2026 | 212 例/478 次观察，160 次扫描 | 多任务 UNETR | 死亡组 0.556、存活组 0.324 | 多任务模型，分割不是主目标 | 24 |

读法：PSMA 全自动 Dice 在 0.5 到 0.7 之间是常态，人群的病灶负担决定上下限（Kendrick 的生化复发人群 0.44，Perret 的 mCRPC 人群 0.83）。本项目基座 TEST 0.6387（五折均值）、VAL 0.6095（单折 OOF，即折外预测）在这个区间中段，和同一数据集的 vanilla nnU-Net（中位 0.70、均值 0.59）、LesionTracer 的 PSMA CV 0.60 在一个水平；起点不弱也不强。

## 三、2S-ICR 原文

论文：Mikko Saukkoriipi 等，“Interactive 3D segmentation for primary gross tumor volume in oropharyngeal cancer”，Scientific Reports 2025，DOI 10.1038/s41598-025-13601-3；arXiv 2409.06605 是 2024 年的早期版本（来源 25）。

- 任务与数据：口咽癌 GTVp（原发肿瘤大体靶区，单个靶区，二值分割），不是全身多病灶。开发用 HECKTOR 2021（224 例，加拿大、瑞士、法国五中心），外部测试用 MD Anderson 67 例 HPV 阳性患者。
- 交互：点击，不是涂鸦。模拟器找模型输出与真值不一致的区域，按每个错误体素到错误区边界的距离加权抽点，大错误区更容易被点到；正负点击编成两卷高斯球。评测 0、1、5、10 个点击，最多 20 个。每个模型最多训 300 轮，早停耐心 50。
- 数字（MD Anderson 外部集，Dice 均值 ± 标准差）：2S-ICR 0.722 ± 0.142（0 点）→ 0.773 ± 0.128（1 点）→ 0.835 ± 0.072（5 点）→ 0.858 ± 0.050（10 点），0 到 10 点平均 0.820 ± 0.097；DeepGrow 0.642 → 0.849（10 点）；DeepEdit-25 0.642 → 0.839；DeepEdit-50 0.721 → 0.822。arXiv 2024 版同一测试集是 0.713 → 0.824（5 点）→ 0.847（10 点），期刊版数字有更新。
- 是不是 autoPET 方法：不是。全文没有 autoPET、全身、多病灶的字样。本项目的“2S-ICR 基线”是按原文两阶段思路改到全身 PET/CT 涂鸦任务上的复现（简报第五节第 9 条），它在本项目 TEST 上的 0.8000 是项目自己的数字，原文没有可对照的全身数字。

## 四、三维医学交互分割“若干轮后 Dice”的背景（不可直接比）

| 方法 | 协议 | 数字 | 来源 |
|---|---|---|---|
| nnInteractive（Isensee 等 2025） | 1 个初始点 + 5 次按模型掩码采样的修正点击；训练数据 120 多个数据集含 PET | 五轮后所有数据集 Dice 都过 70；画法 AUC：lasso 83.42、点 71.76；涂鸦比 SAM2 高 23.8 点、框高 14.9 点；12 个 MR/CT 肿瘤的用户研究与专家无显著差异 | 26 |
| SAM-Med3D（Wang 等 2023） | 三维点提示 1/5/10 点 | 总体 76.27（1 点）→ 80.71（10 点）；病灶：见过的 58.06 → 62.94 → 64.80，没见过的 44.22 → 58.46 → 62.72 | 27 |
| VISTA3D（He 等 2024） | 单点交互；自动结果上编辑时只加减含点击的连通块 | MSD 肝肿瘤 0.701、肺 0.682、胰腺 0.603、结肠 0.609（单点）；自动 127 类平均 0.711，nnU-Net 0.718 | 28 |
| SegVol（Du 等 2023） | 语义 + 空间提示 | 22 项任务 19 项第一，最多领先 37.24%；摘要没有病灶 Dice | 29 |
| Marinov 等 2024（autoPET FDG PET 用户研究） | SW-FastEdit，10 轮，每轮 1 病灶点 + 1 背景点，1014 卷取 10% 测试 | 常规机器人用户比真人高估 Dice 8.7 和 7.0 点，改进机器人 3.6 和 3.7 点；真人约 25% 的点击落在真值外 | 30 |

为什么不能直接比：这些数字是单器官或单病灶靶区、按病灶算 Dice；本项目和 autoPET V 是整卷多病灶、按扫描算 Dice，一笔只指一处错，其余病灶要靠模型自己扛。点击与涂鸦不同；提示来源不同（按真值采点对按模型错误画笔）；模态不同（CT/MR 对 PET/CT）。Marinov 的结果提醒：模拟交互下的 Dice 比真人交互高几个点，本项目全部数字都是模拟交互。

与参赛队的增益结构对照：Sherif 等第一笔占总增益约 85%，Zhang 和 Ning 约 55%；本项目 SIRB flat v1 在 TEST 上 D0 0.6387 → D1 0.7221 → D5 0.7694，第一笔占 0.0834/0.1307 约 64%，处在两者之间。这只说明本项目的曲线形状和公开报告一样“前重后轻”，不说明水平高低。

## 五、判断：TEST 0.80 和 0.85 各能说什么

本项目 TEST 现状（`results-all-systems.md` 第四节；91 扫描/57 患者，Dice 分母 82 阳性扫描/56 患者，按患者平均，5 轮，官方模拟器，每例一种画法 31/30/30）：分割基座 D0 0.6387（0.5647 到 0.7068）；SIRB flat v1 D5 0.7694、nAUC 0.7371；SIRB N3 0.7619；2S-ICR 第 0 折单折 D5 0.8000（0.7640 到 0.8335，起点 0.5778）；涂鸦基线二值通道 0.7657（起点 0.3783）；旧三维执行器 0.7024；旧协议真值参考 0.8814 只作旧协议参考。VAL 理想修复参照 D5 0.9180 是上限。配对差 95% 区间约 ±0.02（简报第三节）。

### 5.1 什么时候能说“超过已完成的全部基线”

- 所有基线在同一 TEST、同一模拟器、同一画法分配表、同一 5 轮下跑完，并且 2S-ICR 和 UAM 的五折集成已经出 TEST（简报：2S-ICR 约 10-10 起在 5090 跑）。单折 0.8000 的区间上沿是 0.8335，新结果落在 0.80 到 0.83 时与它分不出真假；0.85 在区间外，才算有把握“超过”。集成通常比单折高，autoPET 参赛队都做五折集成，所以单折 0.8000 不是 2S-ICR 的上限。
- 起点不同的基线要同时报 D0、D5 和 D5 − D0。2S-ICR 起点 0.5778、涂鸦基线起点 0.3783，和 SIRB 的 0.6387 不同；只报 D5 会把起点差异混进去。
- 单种子 3407、单次训练，差 1 到 2 点时按简报规则不下结论。

### 5.2 什么时候能说“达到或超过公开报告的水平”

- 能找到的五轮涂鸦公开数字只有 autoPET V 参赛队的五折 CV：0.751（Sherif 等）和 0.810（Zhang 和 Ning），都是 FDG+PSMA 混合、按例平均、各自起点（0.554、0.657）。0.80 落在这个区间里，可以写“与公开报告的五轮涂鸦交叉验证水平相当”；0.85 高于两者，可以写“高于我们检索到的公开五轮涂鸦数字”，但必须紧跟一句“数据与划分不同，不构成同榜比较”。
- autoPET IV 的 0.7412 是 10 + 10 个预模拟点击、四中心测试集的 Dice@last，PSMA-LMU 子集 0.7437。交互形式和测试集都不同，不能和本项目的五轮涂鸦并排。
- 2S-ICR 原文的 0.858 是头颈单靶区十点击，与本任务无关，不能当对照。
- 本项目的 2S-ICR 单折 0.8000 已经等于“0.80”，所以 0.80 对公开水平来说只是“到了”，不是“超了”。

### 5.3 什么时候不能说 SOTA

- 数据集不同：公开数字要么是官方 200 例四中心测试集，要么是 FDG+PSMA 混合 CV；本项目 TEST 是 PSMA 单中心训练集里按患者封存的 91 例。autoPET V 的 PSMA 训练集就是本项目的全部数据，参赛模型见过这些扫描，所以也不能把参赛模型拿到本项目 TEST 上比。
- 起点不同，平均方式不同（按患者对按例），Dice 分母规则相同（都只算阳性例）但本项目再按患者等权。
- 单折对集成：2S-ICR 单折；参赛队都用五折集成。
- 没有参加官方榜单；榜单到今天没有可打开的文字版。

### 5.4 论文里稳妥的表述

- 中文：“在按患者封存的 PSMA-PET-CT-Lesions 测试集（91 次扫描/57 名患者）上，使用 autoPET V 官方涂鸦模拟器、相同起点（nnU-Net 五折均值 Dice 0.6387）与五轮交互，SIRB-Net 第五轮 Dice 为 X（95% 区间 a 到 b），高于同一设置下的全部已完成基线（逐个列出 D0 与 D5）；该数字与 autoPET V 参赛方法公开报告的五轮交叉验证水平（0.75 到 0.81，FDG+PSMA 混合）处于同一区间（或：高于该区间），但数据、划分与起点不同，不构成同榜比较。”
- 英文：“On a patient-level held-out split of PSMA-PET-CT-Lesions (91 scans / 57 patients), with the official autoPET V scribble simulator, a shared starting segmentation (nnU-Net five-fold ensemble, Dice 0.6387) and five rounds, SIRB-Net reaches a fifth-round Dice of X, exceeding all completed baselines under identical conditions. Published five-round scribble results from autoPET V participants (0.75 to 0.81, five-fold cross-validation on mixed FDG/PSMA data) are reported on different data and splits and are not directly comparable.”
- 不写“刷新 SOTA”“首次”“通用”；不引用 2S-ICR 原文的 0.858 当对照；autoPET 各届冠军数字只作背景，不进比较表。

## 六、协议上的可比性陷阱：本项目与 autoPET V 官方评测的异同

| 项 | 本项目（`data-models-and-protocol.md` 1.1 到 1.6） | autoPET V 官方（来源 10、11、14、15） | 后果 |
|---|---|---|---|
| 起点 | TEST 用 nnU-Net 五折概率均值 D0 0.6387；TRAIN/VAL 用单折 OOF（VAL 0.6095） | 不规定起点，参赛队自己的自动阶段（CV 里 0.554、0.657） | D5 和增益都依赖起点；报结果必须带 D0 |
| 选笔 | 用官方 `simulate_scribbles.py` 原文件，sha256 核过；单个轴向切片面积最大的 8 邻接块，平手留靠前层 | `simulate_scribble_from_label` 第 389 到 455 行完全相同 | 一致 |
| 加删判定 | 两侧候选笔比笔长，多分侧不长于漏分侧就加笔 | `if fp <= fn` 加前景笔，fp、fn 是笔体素数（第 259 行） | 一致 |
| 画法与种子 | 三种，种子 42；快速 VAL 三种各 33 例，TEST 31/30/30；三画法 VAL 每例跑三种 | 三种各分到三分之一测试例，种子 42 | 快速 VAL 和 TEST 与官方同构；三画法 VAL 是项目扩展，数字不能和快速 VAL 相减 |
| 轮数 | 状态 0 + 5 轮 = 6 个评分状态 | README：6 步；教程：第一笔按真值、再加最多 4 笔；本地脚本默认 `max_iters=5` | 与 README 和参赛论文一致；写论文时注明按 README 口径 |
| 18 邻接 | T 是笔碰到的同向错误三维 18 邻接块的并（训练与分析用）；病灶级 F1 用 18 邻接、IoU ≥ 0.1 | 评测里没有 T；18 邻接只用于 DMM 的病灶实例划分，IoU ≥ 0.1，多重匹配不罚，F1 把所有例的 TP/FP/FN 加总后算 | T 是项目内部构造，不影响官方指标；项目 DMM 的聚合方式（逐例平均还是加总）需核对后再说“同官方” |
| Dice 分母与平均 | 只算阳性扫描；先扫描内平均画法，再患者内平均扫描，最后 54 位患者等权 | `calc_dice` 空真值 NaN，按例平均，按子集再平均 | 同一批数据两种平均会得出不同数字；与官方数字并排时要说明 |
| 空真值 | 不画笔，不进 Dice 分母，FPV 照报 | `metrics.py` 同上；但 `interactive_loop.py` 自带的 `dice_score` 对双空返回 1.0、预测非空返回 0 | 本地脚本与正式 `metrics.py` 不一致，正式榜单的处理没有可打开的来源 |
| AUC | nAUC = 梯形面积 ÷ 5，0 到 1 | `np.trapz` 按迭代序号积分，6 个状态最大 5，不归一化 | 换算：官方 AUC-Dice = nAUC × 5；参赛队的 3.836 对应 0.767 |
| 网格 | 3 mm 各向同性网格计算，插值回原生网格评测；小于 0.1 mL 的目标在往返里 Dice 只剩 0.47（SYN） | 输出掩码必须与输入同形状（`pred.shape != gt.shape` 报错），在原生网格评测 | 评测口径一致；3 mm 往返是模型侧损失，不是指标差异 |
| 测试数据 | 91 例 PSMA 单中心训练集内留出 | 200 例四中心 FDG+PSMA，加 20 例医生涂鸦 | 数据不同；本项目没有医生交互数字 |
| 模拟与真人 | 全部模拟 | 另设医生交互赛道 | Marinov 2024：模拟比真人高 7 到 8.7 点 Dice，模拟数字偏乐观 |

## 七、来源清单

1. autoPET 组织者，Summary of the autoPET challenge series (I–IV)，官方仓库 lab-midas/autoPETV 的 `tutorials/autoPETI-IV-Summary.pdf`，提交 4a20268（2026-07-01），https://github.com/lab-midas/autoPETV
2. Gatidis S 等，Results from the autoPET challenge on fully automated lesion segmentation in oncologic PET/CT imaging，Nature Machine Intelligence 2024，https://www.nature.com/articles/s42256-024-00912-9
3. Dexl J 等，AutoPET Challenge on Fully Automated Lesion Segmentation in Oncologic PET/CT Imaging, Part 2: Domain Generalization，Journal of Nuclear Medicine，PMID 41469162，DOI 10.2967/jnumed.125.270260
4. Dexl J 等，The autoPET3 Challenge: Automated Lesion Segmentation in Whole-Body PET/CT – Multitracer Multicenter Generalization，arXiv 2605.05775
5. autoPET III 官方页 https://autopet-iii.grand-challenge.org/ （类别定义；榜单是图片，数字取自来源 1、4）
6. www.autopet.org/autopetiv.html（任务 1 最终榜单，分子集 Dice@last）
7. autoPET IV 官方页 https://autopet-iv.grand-challenge.org/tasks/ 、/eval/ 、/dataset/ ；GitHub lab-midas/autoPETCTIV README
8. Rokuss M 等，Towards Interactive Lesion Segmentation in Whole-Body PET/CT with Promptable Models，arXiv 2508.21680（PDF 自 autopet.org）
9. Huang J 等，autoPET IV challenge: Incorporating organ supervision and human guidance for lesion segmentation in PET/CT，arXiv 2509.02402
10. autoPET V 官方页 https://autopet-v.grand-challenge.org/ 、/datasets/ 、/evaluation/ 、/timeline/ ；www.autopet.org/autopetv.html
11. lab-midas/autoPETV 本地克隆：`interactive/simulate_scribbles.py`、`interactive/interactive_loop.py`、`interactive/README.md`、`tutorials/scribble-simulation-tutorial.ipynb`
12. Sherif M 等，BS: Take the Hint - Interactive Multitracer PET/CT Lesion Segmentation with a Scribble-Conditioned ResEnc U-Net，arXiv 2609.01554
13. Zhang L, Ning Y，Three-Phase Scribble-Adaptive Curriculum Learning for autoPETV Grand Challenge，arXiv 2608.22096
14. autoPET V 评测页 https://autopet-v.grand-challenge.org/evaluation/
15. lab-midas/autoPETV 的 `metrics.py` 与 `tutorials/metrics-tutorial.ipynb`
16. Liang X 等，Pretrained, Curriculum-Tuned, and Ensembled: A Tracer-Aware Interactive Segmentation Pipeline for AutoPET V，arXiv 2608.30844
17. PSMA-PET-CT-Lesions 数据记录 v2，https://fdat.uni-tuebingen.de/records/gpeq5-yxy63
18. Jeblick K 等，A Whole-Body PSMA-PET/CT dataset with manually annotated tumor lesions，Scientific Data 2026，PMID 42432027，DOI 10.1038/s41597-026-07821-z
19. Rokuss M 等，From FDG to PSMA: A Hitchhiker's Guide to Multitracer, Multicenter Lesion Segmentation in PET/CT Imaging，arXiv 2409.09478
20. Abtahi M 等，Fine-UNETR for PSMA PET/CT Lesion Segmentation: Automated Tumor Quantification and Overall Survival Stratification in Prostate Cancer，arXiv 2606.17570
21. Yazdani E 等，Automated segmentation of lesions and organs at risk on [68Ga]Ga-PSMA-11 PET/CT images using self-supervised learning with Swin UNETR，Cancer Imaging 2024，PMID 38424612
22. Kendrick J 等，Fully automatic prognostic biomarker extraction from metastatic prostate lesion segmentations in whole-body [68Ga]Ga-PSMA-11 PET/CT images，European Journal of Nuclear Medicine and Molecular Imaging 2022，PMC9668788
23. Perret S 等，Automatic lesion segmentation in 68Ga-PSMA PET/CT and 177Lu-PSMA SPECT/CT: added value of PET-guided SPECT in a bicentric study，EJNMMI Research 2026，PMID 42387196
24. Tun HM 等，Multi-task Deep Learning via UNETR for PSMA PET/CT Image for Prostate Cancer，Journal of Imaging Informatics in Medicine 2026，PMID 42675275
25. Saukkoriipi M 等，Interactive 3D segmentation for primary gross tumor volume in oropharyngeal cancer，Scientific Reports 2025，PMC12325674；arXiv 2409.06605
26. Isensee F 等，nnInteractive: Redefining 3D Promptable Segmentation，arXiv 2503.08373
27. Wang H 等，SAM-Med3D: Towards General-purpose Segmentation Models for Volumetric Medical Images，arXiv 2310.15161
28. He Y 等，VISTA3D: A Unified Segmentation Foundation Model For 3D Medical Imaging，arXiv 2406.05285
29. Du Y 等，SegVol: Universal and Interactive Volumetric Medical Image Segmentation，arXiv 2311.13385（NeurIPS 2024）
30. Marinov Z 等，Rethinking Annotator Simulation: Realistic Evaluation of Whole-Body PET Lesion Interactive Segmentation Methods，arXiv 2404.01816
31. Zhong S 等，AutoPET Challenge 2022: Automatic Segmentation of Whole-body Tumor Lesion Based on Deep Learning and FDG PET/CT，arXiv 2209.01212

未核实、只有检索摘录（在 `sota-and-protocol.unverified.json`）：autoPET IV 总结预印本 From Automation to Collaboration: The autoPET/CT-IV Challenge on Interactive Lesion Segmentation in Whole-Body PET/CT and Longitudinal CT（SSRN 6841479，2026-05-29，摘录称任务 1 约 3 万训练病灶/3 千测试病灶，最佳 DSC 0.74、FNV 2.17 mL、FPV 1.30 mL，与来源 1、6 的 0.7412/2.1665/1.2898 对得上）；“412 例三中心 68Ga-PSMA-11 nnU-Net”研究。
