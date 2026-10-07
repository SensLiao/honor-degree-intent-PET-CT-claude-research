C 组文献调研：autoPET V/IV、2S-ICR、UAM 与 PSMA（2026-10-03）

核查时间 2026-10-03 17:41（悉尼）。只读网页和 GitHub 文字页，没下载文件，没改项目文件。来源标注：[read]（这次读了原文页面）；[secondary]（转引别处，没回原文核对）。我们自己的数来自共同事实单 `.tmp/sirb-research-20261003/00-fact-sheet.md`，其中 TEST 数只描述现象，不拿来挑方法。

几个词先说明：autoPET（全身 PET/CT 病灶分割系列比赛，V 是 2026 年的涂抹线交互版）；PSMA（前列腺癌用的示踪剂，我们的数据）；flat v1（SIRB 输出三类平铺的版本，现行主线）；AUC-Dice（六个状态 Dice 曲线的梯形面积，满分 5）；DMM（病灶级检测 F1，每个病灶算一次对错）。

## 结论

- autoPET V 最终榜还没公开。10-03 07:41 UTC 按页面自带的取数方式匿名请求，返回 0 行（[最终榜](https://autopet-v.grand-challenge.org/evaluation/final-test-set/leaderboard/) [read]）。官方日程写 11 月初才邀请前几名合写总结论文（[日程](https://autopet-v.grand-challenge.org/timeline/) [read]）。现在能看的只有参赛者自报的交叉验证数，口径各不相同，排不出名次。
- 公开的 PSMA 单列第 5 轮 Dice 只有一个：UAM 挑出来的最好一折，0.581 到 0.788（[UAM](https://arxiv.org/html/2608.28461) [read]）。别的稿子要么 FDG 和 PSMA 混算，要么没说是第几轮。我们跑的 2S-ICR 第 0 折 TEST 0.8000 已在这一档上沿，五折集成出来可能更高。
- 和 2S-ICR 的差距全出在第 2 到 5 轮。TEST 第 1 轮 0.7221 对 0.7216，第 5 轮 0.7694 对 0.8000。后几轮还在涨的方法，训练时的笔都落在模型自己犯的错上：UAM 第 1 到 5 轮 +0.085，Libo Zhang（参赛者）+0.068（两种示踪剂混算），我们的 2S-ICR +0.078。只用标准答案画笔训练的 BS 只有 +0.029。
- 只改被指那一处，本身不封顶：每轮完美修好被指错误的理想参照，VAL 第 5 轮 0.9172。短的是单笔修复量。flat v1 第 1 笔只拿到理想参照第 1 轮增益的 44%（VAL：理想 +0.183，flat +0.081）。和我们思路最近的公开做法（Yoshimoto，只合并方向与笔一致的改动）在 24 例上从 0.806 涨到 0.828，幅度也小（[Zenodo](https://zenodo.org/records/22210955) [read]）。
- PSMA 难在漏和分小。autoPET III 总结说 PSMA LMU 测试集主要是 1 到 100 mL 病灶分小（[总结](https://arxiv.org/html/2605.05775) [read]）。器官辅助监督在 PSMA 上只多 +0.002 到 +0.017 Dice，单独训 PSMA 模型才是大头（+0.073 到 +0.076）。
- 能搬、又不变成整卷重画的做法排在第 3 节。前三名：训练状态改用当前模型自己五轮跑出来的，并按真实失败分布加权；让一笔把被指的错修完整；软记忆加 mask dropout（训练时随机去掉上一轮分割输入）。器官上下文、多模型平均、笔下一致性损失，预期都小。

## 五个问题的证据表

问题 1：autoPET V（2026，涂抹线）最终榜和已公开的方法。

| 项目 | 内容 | 来源 |
|---|---|---|
| 最终榜 | 0 行（10-03 07:41 UTC）。官网 leaderboard 段仍写比赛进行中 | [最终榜](https://autopet-v.grand-challenge.org/evaluation/final-test-set/leaderboard/)、[autopet.org](https://www.autopet.org/autopetv.html) [read] |
| 日程 | 9-01 截止。9-27 MICCAI（医学影像年会）现场报告。11 月初邀请前几名写期刊总结；每个最终提交必须挂一篇预印本 | [日程](https://autopet-v.grand-challenge.org/timeline/)、[发表要求](https://autopet-v.grand-challenge.org/challenge-publication/) [read] |
| 排名口径 | AUC-Dice 和 AUC-DMM 各占一半。200 例来自四个中心（UKT、LMU、Peter MacCallum、Essen），另有 20 例用医生画的笔 | [autopet.org](https://www.autopet.org/autopetv.html) [read] |
| 初赛榜 | 181 条提交，只考 5 例公开训练病例，前排 Dice 列挤在 0.853 到 0.855，不能当排名证据。前排有 ybwang、Marchmello01（算法名含 LesionLocator 集成）、BIRTH Lab、CYX、miscusi，都没找到方法稿 | [初赛榜](https://autopet-v.grand-challenge.org/evaluation/preliminary-test-set/leaderboard/) [read] |
| Libo Zhang（Stevens 理工） | 两条涂抹线通道，约 1.4 亿参数的 ResEnc U-Net（nnU-Net 的残差编码器网络），4000 轮分三段：先无提示，再用标准答案画笔，最后在模型自己第 0 轮的错误上连画 1 到 5 笔。训练加 DeepPSMA（另一套 PSMA 公开数据）200 例，10 个 checkpoint 取平均。五折阳性病例 0.657、0.742、0.810（第 0、1、5 轮，两种示踪剂混算）。PSMA 只给 AUC-Dice 3.46 到 3.74，除以 5 约 0.69 到 0.75。三种画法之间几乎没差 | [arXiv 2608.22096](https://arxiv.org/html/2608.22096) [read] |
| UAM（马德里自治大学） | 器官和病灶共用输出头，PSMA 专用模型，在线交互训练：上一轮软概率和前景、背景高斯热图注入各级跳连。PSMA 单折 σ=5：0.581、0.703、0.788；σ=10 只到 0.753 | [arXiv 2608.28461](https://arxiv.org/html/2608.28461)、[代码](https://github.com/BiometricsAI/AUTOPET_V_submission) [read] |
| BS（Brightskies） | ResEncL（ResEnc 的大号），从 autoPET III 冠军同折权重微调。涂抹线直接用官方预生成的标准答案笔，不读上一轮。五折混算 0.5539、0.7223、0.7512。69% 的笔是背景笔，几乎不起作用：误报个数从 6869 变成 6998 | [arXiv 2609.01554](https://arxiv.org/html/2609.01554) [read] |
| TRIAGE/MEDAI | MAE 预训练（遮住部分图像让网络补全）的 STU-Net 骨干，加器官上下文，两级。PSMA 第二级 0.6405（十折），没说对应第几轮 | [arXiv 2608.30844](https://arxiv.org/html/2608.30844) [read] |
| msdsn 仓库（初赛榜队名 UTK Bredesen，算法名和仓库描述一致；是否同一队 UNVERIFIED，下文简称 UTK） | 5 通道，含上一轮掩码；笔划用截断的欧氏距离图编码；上一轮掩码是改坏标准答案冒充的；另加笔划合规后处理。fold 0 的 100 例子集（37 例 PSMA，含无病灶例）上 PSMA AUC-Dice：官方四通道基线 3.639，交互模型不加后处理 3.301，最终系统 3.776 | [README](https://github.com/msdsn/autopet-v)、[结果表](https://github.com/msdsn/autopet-v/blob/main/results/RESULTS.md) [read] |
| Yoshimoto（慈惠医大，只发在 Zenodo） | LesionLocator 起点。冻结的 autoPET IV 交互模型只提修改建议，每笔只把方向和笔一致的差值并进外部维护的分割。24 例开发集 0.806 到 0.828。自己从头训的修正模型单笔反应更好，整条轨迹反而变差 | [Zenodo](https://zenodo.org/records/22210955) [read] |

问题 2：autoPET IV（2025，点击）冠亚军的消融。IV 的点击从标准答案预先生成，不跟着模型的错误走（[IV 任务页](https://autopet-iv.grand-challenge.org/tasks/) [read]）。所以 IV 只回答提示编码和点击数课程，回答不了后几轮的自我纠错。

| 因素 | 证据 | 来源 |
|---|---|---|
| 提示编码 | Rokuss（LesionLocator 队）：EDT size 2（按离点击远近编码的距离图）最后一次点击 Dice 76.09。最好的高斯核 74.59，无交互模型 68.33 | [arXiv 2508.21680](https://arxiv.org/html/2508.21680v1) [read] |
| 采样方式和加数据 | 混入 20% 自定义点 +0.10（76.09 到 76.19），再加外部数据 +0.16（到 76.35），只加数据 −0.09。没有在线和离线模拟的单项对照 | 同上 [read] |
| 点击数课程 | BIRTH（IV 第 1 名）：只用满 10 点训练的 V0，0 点时 Dice 0.000。预训练加平衡随机点数的 V2：0 点 0.619，5 点 0.855，10 点 0.871。这 100 例 PSMA 训练时见过，不是留出成绩 | [arXiv 2509.02402](https://arxiv.org/html/2509.02402) [read] |
| 上一轮掩码、自身状态训练 | 冠亚军都没用。两家都是四通道，每次从点击整卷重算 | 同上两篇 [read] |
| 器官监督、预训练 | BIRTH 两样都用，没有单项消融 | 同上 [read] |
| 网络大小（自动分割段） | LesionTracer（autoPET III 冠军的自动分割模型）：ResEncL 对默认 nnU-Net，PSMA Dice 51.69 到 58.25，是它表里最大的一步。autoPET III 总结也说骨干大小影响最大 | [arXiv 2409.09478](https://arxiv.org/html/2409.09478)、[总结](https://arxiv.org/html/2605.05775) [read] |
| 训练更久 | LesionTracer 改 batch 3、1500 轮：全体 +0.07，PSMA −0.83。IKIM（autoPET III 第 2 名）也写 PSMA 多训不涨 | 同上、[arXiv 2409.12155](https://arxiv.org/html/2409.12155) [read] |
| TTA 和集成 | BIRTH 用镜像 TTA（翻转后取平均），Rokuss 用两套配置各五折集成，都没给消融 | 同上 [read] |
| 官方成绩（参考） | 最后一次点击 Dice：BIRTH 0.7412，LesionLocator 0.7236，Zhack 0.7308 | 项目综述页 `petct-autopet-comparators-current` 转引 [secondary] |

问题 3：2S-ICR 和 UAM 后几轮强在哪里，哪些能搬。

| 要素 | 2S-ICR | UAM | 搬进只改被指那处的编辑器 |
|---|---|---|---|
| 输入 | CT、PET、上一轮 sigmoid 概率、正负点击的高斯球，共 5 通道 | 图像编码器只读 CT、PET。上一轮软概率加前景、背景高斯热图（σ=5 体素），经零初始化的 1×1×1 卷积加到每一级跳连 | 能。软记忆当状态输入；零初始化接入，续训起点和父模型一样 |
| 训练状态 | 每次交互后都更新一次参数，下一步的状态就是模型自己的输出。论文写每例交互数在 1 到 15 均匀抽；我们 09-17 的代码核查记为 16 个伯努利之和，期望 7.5 | 每个训练步先不带梯度跑 0 到 5 轮（5 轮的概率 0.25，最大）。每轮在模型自己错得多的那一类、最大的轴向连通块上画笔，然后在这个状态上训练 | 能。只换状态来源，T/O/P 标签仍按这一笔指的错来定 |
| 防止照抄上一轮 | mask dropout p=0.2，上一轮换成全 0.5。HECKTOR（头颈 PET/CT 数据集）上 DSC 0.827 到 0.845，每次交互改动的体素 731 到 941 | 0 笔状态占 24%，保住起点 | 能，纯训练技巧 |
| 损失 | Dice 加 BCE 等权 | 病灶 Dice+CE，加 0.5 器官项，加 0.5 笔下一致性项（前景笔处罚 −log p，背景笔处罚 −log(1−p)） | 能。flat 笔下体素已改对 0.98，空间小 |
| 增强 | 旋转到 45°、平移 ±32 体素、镜像等重增强 | 亮度、gamma、旋转 | 能 |
| 推理 | 整卷重算，五折集成放进循环里 | 整卷重算，软概率存盘当下一轮输入，不翻转 | 整卷重算不能搬 |
| 后几轮表现 | 我们 TEST：D1 0.7216 到 D5 0.8000；第 1 轮修回的体积有 28.66% 在离笔 30 mm 以外 | PSMA 单折第 1 轮 0.703 到第 5 轮 0.788。编码器学习率只给 0.1 倍，500 轮 | 离笔远的那部分修复，正是我们不做的 |

来源：[2S-ICR 正式版](https://www.nature.com/articles/s41598-025-13601-3) [read]；交互数分布的代码核查见 vault `exp-petct-three-new-baselines` [secondary]；[UAM 论文](https://arxiv.org/html/2608.28461) 和 [训练器代码](https://github.com/BiometricsAI/AUTOPET_V_submission/blob/main/custom_trainers/nnUNet_Interactive_sigma_5.py) [read]；我们的数来自事实单。

同类旁证有两个。nnInteractive（DKFZ 的通用三维交互分割模型）训练时把当前预测连同新提示一起再喂回网络，续接交互的概率从 0.3 线性升到 0.75（[arXiv 2503.08373](https://arxiv.org/html/2503.08373) [read]）。RITM（2021 年的点击式交互分割方法）在自然图像上，上一轮掩码加自身轨迹训练让 SBD 数据集的 NoC@90 从 6.49 降到 6.06；可自身轨迹超过 4 步训练会崩（[RITM](https://ar5iv.org/abs/2102.06583) [read]）。

反例也有两个。BS 用静态标准答案笔，第 1 到 5 轮只 +0.029。UTK 用改坏标准答案冒充上一轮，交互模型第 1 到 5 轮从 0.669 到 0.679，几乎是平的（含无病灶例的合并口径）。作者自己把"假状态不等于模型真错误"列为局限（[训练文档](https://github.com/msdsn/autopet-v/blob/main/docs/train_pipeline.md) [read]）。

问题 4：PSMA 特有的难点和对策。

| 难点或对策 | 证据 | 来源 |
|---|---|---|
| 生理摄取部位 | 泪腺、唾液腺、肝、肾、肠、输尿管、膀胱。18F 示踪剂肾实质高，68Ga 尿路高，骨髓摄取不一 | [总结](https://arxiv.org/html/2605.05775)、[PSMA 数据集论文](https://www.nature.com/articles/s41597-026-07821-z) [read] |
| 典型误报 | 神经节像淋巴结转移、放疗后改变、炎症。PSMA UKT 测试集的泪腺训练集里没有；每例裁掉头顶约 50 个体素后，LesionTracer Dice 涨近 5% | [总结](https://arxiv.org/html/2605.05775) [read] |
| 典型漏报 | 低表达、病灶小、贴着膀胱。总结里的一例示例中，胸廓骨骼和颈部淋巴结的低表达病灶所有算法都漏。只有一个小病灶的病例，各队 Dice 几乎都是 0 | 同上 [read] |
| 体积影响 | 参考病灶体积每翻一倍，Dice +0.039。PSMA LMU 1 到 100 mL 的病灶普遍分小；10 到 100 mL 的严重漏报多出在两个 LMU 测试子集 | 同上 [read] |
| 标注方式 | 在圆形范围里按每例自定的 SUV（标准化摄取值）阈值预分割，再逐层手修。第二读者一致性低，分歧多在本来就模糊的病灶 | 同上 [read] |
| 器官辅助监督 | UAM PSMA 0.522 到 0.539。IKIM PSMA 0.6014 到 0.6133，漏报体积 20.49 到 11.23 mL，误报体积 12.17 到 12.97 mL。LesionTracer PSMA 60.63 到 60.84。autoPET III 总结说各队看不出稳定好处 | [UAM](https://arxiv.org/html/2608.28461)、[IKIM](https://arxiv.org/html/2409.12155)、[LesionTracer](https://arxiv.org/html/2409.09478)、[总结](https://arxiv.org/html/2605.05775) [read] |
| PSMA 专用模型 | UAM 0.539 到 0.612；IKIM 合训 0.5258，单训 0.6014 | 同上 [read] |
| SUV 阈值后处理 | IKIM：去掉 SUV 低于 1 的 PSMA 预测，Dice −0.0001。推断：误报多半不在低摄取区 | [IKIM](https://arxiv.org/html/2409.12155) [read] |
| 去小连通块 | IKIM：去掉长度小于 10 的连通块，PSMA 漏报体积 +3.17 mL | 同上 [read] |
| PET 强度表示 | UTK 实测：按病灶前景统计量归一化后，一个 SUV 0.92 到 2.18 的低摄取 PSMA 病灶，对比度比按例 z-score（每例减均值再除标准差）低 26.6 倍。换上 LesionTracer 的大骨干，PSMA 反而 −0.094 AUC-Dice（39 例，在噪声内）。BS 用主动脉血池做参照再取 asinh（压缩高值的对数型变换），没做消融 | [训练文档](https://github.com/msdsn/autopet-v/blob/main/docs/train_pipeline.md)、[BS](https://arxiv.org/html/2609.01554) [read] |
| CT、PET 错位增强 | LesionTracer PSMA 58.25 到 58.89 | [LesionTracer](https://arxiv.org/html/2409.09478) [read] |
| 转移部位人群图谱 | 训练后再融合，Dice +0.002、+0.011、+0.013（验证、同分布测试、外部测试） | [medRxiv](https://www.medrxiv.org/content/10.64898/2026.08.26.26361439v1) [secondary，只读到检索摘录] |

数据集画像：PSMA 阳性例的病灶数中位 6（IQR 1 到 41，最多 318），全身肿瘤体积中位 44.08 mL。普通 nnU-Net 平均 Dice 0.59，中位 0.70（[PSMA 数据集论文](https://www.nature.com/articles/s41597-026-07821-z) [read]）。

问题 5：约 5 次交互后 PSMA 能到多少。各行的数据集、聚合单位、是否含无病灶例都不同，只能看量级和曲线形状，不能直接排高低。

| 方法 | 数据与口径 | D0、D1、D5 | 第 1 到 5 轮增量 | 来源 |
|---|---|---|---|---|
| UAM σ=5 | 官方数据四折里挑最好的一折，PSMA 专用 | 0.581、0.703、0.788 | +0.085 | [UAM](https://arxiv.org/html/2608.28461) [read] |
| UAM σ=10 | 同上 | 0.578、0.692、0.753 | +0.061 | 同上 [read] |
| Libo Zhang | 五折，FDG 加 PSMA 阳性例；PSMA 只有 AUC | 0.657、0.742、0.810 | +0.068 | [arXiv 2608.22096](https://arxiv.org/html/2608.22096) [read] |
| BS | 五折，两种示踪剂混算 | 0.5539、0.7223、0.7512 | +0.029 | [arXiv 2609.01554](https://arxiv.org/html/2609.01554) [read] |
| UTK 交互模型，不加后处理 | 100 例子集，含无病灶例（空预测记 1） | 0.607、0.669、0.679 | +0.010 | [结果表](https://github.com/msdsn/autopet-v/blob/main/results/RESULTS.md) [read] |
| UTK 最终系统 | 同上；PSMA AUC-Dice 除以 5 约 0.755 | 0.664、0.818、0.867 | +0.049 | 同上 [read] |
| Yoshimoto | 24 例开发集，示踪剂构成没报 | 0.806、未报、0.828 | 未报 | [Zenodo](https://zenodo.org/records/22210955) [read] |
| BIRTH（IV，点击） | 100 例 PSMA，训练时见过，五折集成 | 0 点 0.619，5 点 0.855 | 不适用 | [arXiv 2509.02402](https://arxiv.org/html/2509.02402) [read] |
| 2S-ICR 原文（头颈，不是 PSMA） | HECKTOR 交叉验证 | 0.752、0.789、0.851（5 点） | 不适用 | [arXiv 2409.06605](https://arxiv.org/html/2409.06605v1) [read] |
| SIRB flat v1 | 我们 TEST，按患者平均 | 0.6387、0.7221、0.7694 | +0.047 | 事实单 |
| 2S-ICR 第 0 折 | 我们 TEST | 0.5778、0.7216、0.8000 | +0.078 | 事实单 |
| 理想参照 | 我们 VAL | 0.6095、0.7925、0.9172 | +0.125 | 事实单 |

0.80 以上做不做得到：有可能，但没有文献直接证明。理想参照说明只改被指那处也能到 0.9 以上。整卷重画的方法在 PSMA 上 5 笔后落在 0.75 到 0.79，我们的 2S-ICR 已到 0.80。至今没有公开的只改被指那处的方法在 PSMA 上过 0.80；Yoshimoto 的合并方式只证明了能稳住。

按事实单的粗算，VAL 三画法第 5 轮要从 0.7524 提到约 0.78，差 +0.028。原配方多训 8k 只给了 +0.004（区间含 0）。这几个点只能从训练状态分布和单笔修复量里找。

## 可以引入的做法（按预期效果排序）

排序看文献证据和我们已知短板对得上多少。"预期"是定性判断：文献里的数来自别的模型、别的数据，不能直接换算成我们的提分。

| 排序 | 做法 | 文献依据 | 对上 SIRB 哪个短板 | 怎样保住只改被指那处 | 预期，不确定在哪 | 成本 |
|---|---|---|---|---|---|---|
| 1 | 训练状态改成当前最好候选模型自己在 TRAIN 上五轮跑出来的，定期重跑刷新。按真实轮次的失败分布加权，第 3 到 5 轮和 ≥10 mL 的加笔补到真实比例 | UAM、2S-ICR、nnInteractive、RITM 都在模型自己的输出上接着训。BS 和 UTK 两个反例后几轮几乎不涨 | 离线状态太干净：生成器每步修掉 89.8%，真实只修 15% 到 25%。≥10 mL 加笔训练里占 7.8%，真实轮次 19.7% 到 20.5%。和 2S-ICR 的差全在第 2 到 5 轮 | 只换状态来源和抽样权重，T/O/P 仍按这一笔指的错来标 | 预期最大。没有 PSMA 文献单独拿掉这一项做对照。RITM 发现自身轨迹训练超过 4 步会崩。10-04 出结果的 N1_STATE_INDUCED 是第一份内部证据 | TRAIN 回放约 6 小时，8k 续训 8 到 10 小时，快速 VAL 2 到 3 小时 |
| 2 | 在执行器上让一笔修完整，不重训就能在 VAL 上试。删笔：笔碰到的那块预测，没有高摄取核心就整块删，有就沿分水岭切开只删笔这侧。加笔：在笔所在的同一高摄取连通区里，按笔覆盖处标定的 SUV 阈值补全。推理时再补一次以笔为中心的局部块 | UTK 的背景笔规则（测地半径和删除比例都有上限）和前景笔按笔印标定阈值生长。UTK 以笔为中心的二次推理 +0.010 AUC-Dice，PSMA +0.013。FocalClick（2022 年自然图像点击分割）的 progressive merge 只更新含新点击的那块变化区，修已有掩码时 NoC90 从 8.52 降到 3.69 | 第 1 笔只拿到理想增益的 44%；≥10 mL 目标被 e 挡住 0.35 到 0.49；PSMA 标注本来就按 SUV 阈值画 | 只动笔所在的那个连通块，别处一个体素不改 | 中到大。但 UTK 整套合规规则在 PSMA 上 Dice 只 +0.015 AUC（每轮约 +0.003），手工规则对 Dice 帮助有限；连通补全可能带进粘连的生理摄取，要靠 P 类保护和体积上限挡住 | 不训练，VAL 上几小时 |
| 3 | binding（判断这一笔指哪处错的那一路）的距离特征，从 60 mm 截断的欧氏距离换成或加上候选区内的测地距离：删笔沿当前分割内部走，加笔沿高摄取连通区走 | UTK 用连通块内的测地半径限定删除范围；DeepIGeoS 一类方法用测地距离编码交互 [secondary，术语表] | 30 mm 外修回 0.195，60 mm 外 0.084；远处的块共用一个查询向量 | 测地距离只沿同一物体走，断开的远处错误仍然够不着 | 中。远处问题集中在少数患者（5 位占 30 mm 外目标体积的 77%），按患者平均的 D5 涨不了太多 | 要重训 8k |
| 4 | 状态里加软记忆（上一轮输出的概率，或把 p0 打开），训练时配 mask dropout | 2S-ICR：p_drop 0.2 让 DSC 0.827 到 0.845，每次改动体素多 29%。UAM 软概率零初始化注入各级 | 修不全，修改偏保守 | 软记忆只是状态输入，执行器规则不变 | 中偏小。UTK 去掉上一轮掩码后 Dice 几乎不变（−0.002 AUC），另一版去掉后反而更好（+0.183），说明软记忆要配真实状态训练才有用，应和第 1 项一起做 | 零初始化续训 8k |
| 5 | 当前笔用小半径距离图稠密编码，只进范围支路（排队中的 N1_STATE_SPATIAL 就是现成位置），判断有没有错的那一路仍不看笔 | UAM 窄高斯好于宽高斯（PSMA 第 5 轮 0.788 对 0.753）；Rokuss 距离图好于高斯；RITM 小圆盘好于全图距离变换 | 笔附近修不全（15 mm 内 flat 0.800） | 笔只影响改多大，不影响有没有错 | 中偏小，变数大。flat 笔下体素已改对 0.98；UTK 各尺度都喂笔的独立编辑支路在 39 例上没比原模型好（4.015 对 4.094 和 4.133，非配对） | 并进已排队任务，几乎不加成本 |
| 6 | 器官上下文（输入通道或辅助头），主要帮删笔判断这是生理摄取 | UAM、IKIM、LesionTracer 在 PSMA 上 +0.002 到 +0.017；autoPET III 总结看不出稳定好处 | PSMA 生理摄取误报 | 只是状态信息 | 小，第 5 轮多半不到 1 个点。IKIM 基线要用 TotalSegmentator（CT 器官自动分割工具）给 506 例出标签，若已出完成本就低，需先核对 | 生成标签加重训 |
| 7 | 多个编辑器或翻转后对 pT 取平均 | Libo 发现最好和最终 checkpoint 在 20% 病例上互补；UTK 两次两模型集成都没涨（−0.013、−0.035 AUC-Dice，各 30 例）；BIRTH 用 TTA 没给消融 | 单模型在 0.5 附近抖动 | 执行器规则不变 | 小，证据互相矛盾，留到最后打磨 | 推理时间成倍 |
| 8 | 核查 PET 归一化是否压掉低摄取 PSMA 病灶的对比度，必要时换按例 z-score 或主动脉参照的 asinh | UTK 实测 26.6 倍的对比度差 | 小病灶、低表达骨病灶漏修 | 和编辑范围无关 | 未知。先看 VAL 漏修目标的 SUV 分布再定 | 核查几小时；换归一化要重训 |
| 9 | 笔下一致性损失 | UAM 用了，没单独消融 | N3 笔下改对 0.79 | 只约束笔下体素 | flat 上小（已 0.98），只对 N3_ES 有意义 | 续训时顺手加 |

不建议搬的：整卷重算和执行 O 类（事实单已测，误改是多修的 2 到 19 倍）；无病灶例的整例清空规则（我们的 Dice 只算阳性患者，对 D5 没用）；加 DeepPSMA 等外部数据（各基线只用 506 例学习池，比较就不公平了）；换大骨干。UTK 换上约 1 亿参数的 LesionTracer 骨干是零结果，PSMA 还略差；LesionTracer 的大涨幅出在自动分割段，不在编辑段。

和正在跑的任务怎么接：第 1 项的第一步就是 N1_STATE_INDUCED。它的状态池来自 v1 两个模型、固定一半比例，下一步应改成从当前最好候选重跑，并按失败分布加权。第 5 项可直接并进 N1_STATE_SPATIAL。第 2 项不占训练显卡，可以在 10-04 那批结果出来前先在 VAL 上试执行器规则。

选版提醒：Yoshimoto 发现单笔反应变好、整条轨迹却不一定变好。单笔修复率不能当选版标准，继续用完整五轮轨迹的快速 VAL 选，和现行做法一致。
