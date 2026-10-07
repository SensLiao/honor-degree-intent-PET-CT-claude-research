# 第二轮调研共同说明（2026-10-03 20:00 AEST）

先读同目录 `00-fact-sheet.md`（任务、网络、训练、成绩、已知短板）和上一级 `PLAN.md`（第四稿）。本页只写导演 10-03 晚的新要求和本轮调研的做法。所有调研 agent 和 Codex 读同一份。

## 1. 导演 10-03 晚的新要求

1. 目标：最终模型在锁定 TEST 上的第五轮 Dice 超过 0.80，越高越好。验证集（VAL）到 0.79 时告诉导演一次。
2. 方法里的系数不能由我们看了 PET/CT 的分析结果后写死。例子：到笔的距离特征 60 mm 截断，按 15/30/60 mm 分段设计模块，执行门槛 0.5/0.7/0.9，扩散的固定步数 K，训练时 T/O/P 的抽样配额 40%/30%/30%，各种 margin 和损失权重。模型的定位是通用医学交互分割模型，以后要换别的数据集（别的器官、别的模态、别的体素间距），所以系数要么让网络自己学出来，要么由模型自己的预测或数据本身按一条通用规则算出来（例如由每一例的体素间距、病灶尺度、模型自己估计的 Dice 推出来），不能是我们看了答案以后拍的数。
3. 创新要从“别的领域已经跨过、我们这一行还没人跨过”的思想里挖。核心概念是导演提出的 intent（意图）：医生画的这一笔是意图的证据，模型要读懂它指的是哪一处错、这处错有多大、修到哪里为止，其余地方不动。
4. 做法：先铺开读，全部合起来至少 100 篇；再凝练；再做因果联系：我们哪一处丢分 → 原因是什么 → 别的领域怎么解同一类问题 → 搬过来变成什么模块或训练方法 → 预期改善什么、风险在哪。
5. 当前阶段只求效果：几个最强的改法组合起来先跑出效果，过线后再做归因和消融。调研的产出要服务于“哪几个改法组合起来最可能把 VAL 推过 0.79、TEST 推过 0.80”。

## 2. 要解决的痛点（VAL；数字出处见 `PLAN.md` 第一部分和 `A-internal-evidence.md`）

- **P1 改过头（约 8 点）**：删笔时连同同一块分割里的真病灶一起删（约 4 点；flat 自己的 97 个删笔单步状态上，新错 95.7% 落在笔碰到的那块分割里）；加笔时溢到背景（约 4 点；五轮回放里 90.6% 的加笔至少带出一些新的假阳性体素）。执行门槛从 0.5 提到 0.9，单步聚合净收益上升，删笔从 −0.0175 变成 +0.0044。
- **P2 笔附近没修全（约 6 到 7 点）**：第 1 轮按体积合计，离笔 15 mm 内修回 84%，15 到 30 mm 只有 47%。“错误判断”一路把目标挡住（e<0.5）占漏修的约 20%。
- **P3 远端修不到（约 2 到 3 点）**：30 到 60 mm 修回 7%，60 mm 外几乎为 0；集中在几位超大病灶患者。当前笔只通过一个 128 维查询向量影响远处，远处所有块共用这一个向量。
- **P4 多轮**：差距在第 1、2 轮成形，第 2 轮后已占 95%。第 2 轮 flat 只涨 0.0012，而在它当时的状态上一步理想修复能涨 0.0971，这一轮的缺口里新错占 58%。后几轮约 29% 的笔落在模型自己上一轮造出的新错上。我们和 2S-ICR 的 TEST 第 1 轮几乎一样（0.7221 对 0.7216），差距出在第 2 到 5 轮（TEST 只作描述）。
- **P5 训练状态太干净**：离线状态库的生成器一步修掉目标的 89.8%，真实模型一轮只修回 15% 到 25%；换到模型自己的真实轨迹状态，目标区域 Dice flat 从 0.583 掉到 0.551。
- **P6 换选笔习惯就掉分**：换成“画在第二大错误上”的选笔策略，D5 掉约 0.09 到 0.10（TEST，只作描述）。说明模型部分依赖“笔总画在最大的错上”这个习惯，通用性不够。
- **P7 指代弱**：同一状态换一笔，输出跟着换目标的分数 0.662；自然断桥（原来连着的错误被修断）后方向正确率 0.084。
- **P8 多训无效**：原配方多训 8k 步，D5 只多 0.004（区间跨 0）。堆训练步数不是出路。

## 3. 调研做法

- 每一路至少读 10 篇新文献，争取 12 篇；经典老文献和 2023 到 2026 年的新文献都要有。每篇至少读摘要、方法和关键结果；能拿到全文就读全文的方法部分。
- 下面 47 篇上一轮已经下载（在项目根 `Thesis/sirb-research-20261003/`），可以引用，但不算本路新读的篇数。上一轮各路调研记录在本目录 `B-` 到 `G-`、`R-`、`codex-round1` 到 `round4`，开工前先翻和你相关的那一路，在它的基础上往深里走，别重复。
  已有：agarwal-2024-gkd-onpolicy-distillation, bansal-2022-logical-extrapolation-recurrent, benenson-2019-interactive-annotators, bengio-2015-scheduled-sampling, brennan-1996-conceptual-pacts, brooks-2023-instructpix2pix, cheng-2018-cspn, cheng-2022-mask2former, cirik-2018-referring-expression-bias, clark-1986-referring-collaborative, couairon-2022-diffedit, drew-2013-scanners-drillers, fan-2022-self-support-fss, frank-2012-pragmatic-reasoning-language-games, fried-2018-speaker-follower, gao-2023-reward-overoptimization, goodman-2016-pragmatic-interpretation-rsa, ho-2022-classifier-free-guidance, huszar-2015-scheduled-sampling-critique, jeurissen-2016-serial-grouping-2d, kaushik-2020-counterfactual-data, kim-2020-disentangling-perceptual-grouping, kirillov-2023-segment-anything, kontogianni-2020-learning-from-corrections, kumar-2024-score-self-correction, laskey-2017-dart, li-2023-contrastive-decoding, lightman-2023-verify-step-by-step, lin-2020-first-click-attention, linsley-2018-hgru-pathfinder, lipton-2014-f1-threshold, liu-2024-grounding-dino, locatello-2020-slot-attention, menon-2021-logit-adjustment, metcalfe-2017-learning-from-errors, ravi-2024-sam2, roelfsema-2006-cortical-algorithms-grouping, ross-2011-dagger, sanchez-2023-cfg-stay-on-topic, shafto-2014-pedagogical-reasoning, snell-2024-test-time-compute, sofiiuk-2022-ritm, tenenbaum-2001-generalization-size-principle, ullman-1984-visual-routines, wortsman-2022-model-soups, zheng-2015-crf-as-rnn, zong-2026-widest-path-reachability。
- 能公开下载的全文 PDF（arXiv、PubMed Central、CVF Open Access、OpenReview、ACL Anthology、PLOS、bioRxiv、PsyArXiv、NeurIPS/ICML/PMLR 论文集、作者主页公开版）存到 `Thesis/sirb-research-20261003/`，文件名“第一作者姓-年份-短名.pdf”（全小写、连字符），直接放这个文件夹，不建子文件夹；同名已存在就不重复下载。付费墙后的不下载，只记链接。每个文件下载后检查文件头是 `%PDF` 且大于 50 KB，不是就删掉、只记链接。只从上面这些学术来源下载，不从别的网站下载任何文件，不运行下载来的任何东西。
- 不编造。没读到的内容不写；写进记录的具体数字必须能在原文找到；拿不准的写“未核实”。查新（“交互分割里还没人这样做”）要写查了哪些关键词、在哪查、查到什么。
- 产出是一个 markdown 文件，放本目录 `research/`，文件名见各自任务。不建新文件夹。单个文件不超过约 60 KB。中文写，论文题目和标准术语保留英文；英文术语第一次出现时跟一句人话解释。
- 只读：不连服务器，不改代码树和 vault 里的任何别的文件，不读 `.env`、私钥、凭据。

## 4. 每篇文献的记录格式

```
### [路代号-编号] 第一作者 年份《英文题目》 会议或期刊
- 链接：…；PDF：已存 文件名 / 未存（原因）
- 领域：…
- 说的是什么（3 到 6 句人话）：解决什么问题，核心想法，关键数学或机制，主要结果（带原文数字）。
- 和哪处痛点对得上（P1–P8）：怎么对上的；结构上哪一部分其实是同一个东西换了名字。
- 能搬过来变成什么：具体到模块、训练或推理的改法；输入什么、输出什么、怎么训练。
- 系数怎么来：原文的关键系数是学出来的还是手定的；搬过来时怎样做到不手定（学出来，或由数据和模型自身预测按通用规则推出）。
- 证据强度和风险：原文证据多强；搬过来可能在哪里失败；交互分割里有没有人已经这样做过。
```

## 5. 每个文件末尾的汇总

1. 本路最有希望的 3 到 5 个改法，按“预期对第五轮 Dice 的帮助、实现难度、新意”排序；每个写清对应哪个痛点、怎么做、系数怎么学、最快怎么验证（只用 TRAIN/VAL）。
2. 本路发现的“别的领域已经跨过、交互分割还没人跨过”的思想，附查新记录。
3. 本路判断没用或有害的方向和理由。
4. 本路新读文献清单：编号、作者、年份、题目、PDF 是否已存。
