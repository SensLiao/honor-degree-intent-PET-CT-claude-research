1. **[D] “生成器每步修掉 89.8%，模型每轮只修回 15–25%” → 两个数字各有出处，但混用了平均方式，必须改。**

   我从原始记录独立计算：

   | 来源与算法 | 修回比例 |
   |---|---:|
   | TRAIN 生成器，7414 步的 `realised_fraction` 逐步平均 | **89.761%** |
   | flat 三画法 VAL，1262 个有效交互的“该笔修回量÷该笔目标量”逐笔平均 | **62.373%** |
   | N3 三画法 VAL，1263 个有效交互，采用相同逐笔平均 | **49.527%** |
   | flat：所有笔的修回体积之和÷目标体积之和 | **23.049%** |
   | N3：采用相同总体积汇总 | **16.315%** |

   **证据：**生成器原件 `D:/honor-petct-data-hub/z390/banks/editor-sirb-mainline-20260920-R1/episodes/generation_log.jsonl`；模型原件 `records/development_results_transfer/eval-sirb-batch1-val-20260925/rollout/{N1_STATE-s3407,N3-s3407}/transitions.jsonl`。这里及下文的 `records/` 均相对 `projects/petct_textual_intent/`。原说法见 [local-data-models-results.md](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:375>)。

   **建议改法：**保留“生成器推进得比实际模型快、训练与部署状态存在差异”，删去这组混合口径的直接对比。即使改成 89.8% 对 62.4%，仍是 TRAIN 生成器与 VAL 模型轨迹的不同样本，不能据此量化因果贡献。英文可写：

   > The synthetic state generator typically repairs a larger fraction of the target than the model, suggesting a mismatch in training states; whether this explains the performance gap remains unproven.

2. **[D] “第 1 轮加笔占差距 46%，后几轮删笔占 38%” → 数字正确；作为丢分记账证据强，作为可回收收益或因果归因证据弱。**

   独立复算三画法 VAL：

   - flat D5＝0.7523582394；理想参照 D5＝0.9171768336；差距＝**0.1648185942**。
   - 第 1 轮 ADD 的贡献差＝**0.0760643421**，占 **46.1503%**。
   - 第 2–5 轮 REMOVE 的贡献差＝**0.0629163879**，占 **38.1731%**。
   - 第 1 轮 REMOVE 占 **15.7626%**；后几轮 ADD 为 **−0.0861%**，四项合计 100%。

   **证据：**上述 VAL 目录中 flat、oracle 的 `six_state.csv` 与 `transitions.jsonl`；先按画法、扫描、患者逐层平均。与 [本地分析第 4.4 节](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:231>)一致。

   **建议改法：**邮件第 34–35 行的 “comes from” 改成 “accounts for … in a descriptive decomposition”。第 1 轮两边起点相同，解释相对直接；之后两条轨迹的状态、目标、方向都可能不同，不能说“修好删笔就能拿回 38%”。

3. **[D] “纠错笔兑现 6.8%，贡献误删体积的 73.1%／78%” → 复算成立，但必须限定分类规则和分母。**

   按原分析的体积启发式重新分类，后四轮得到 NEW 420、CONTINUE 212、REPAIR 293、OTHER 82 笔，与文档一致。REPAIR 的逐笔平均实际增益为 **0.0102939003**，同状态理想增益为 **0.1519618222**，两者相除是 **6.7740%**。

   全部 **414 次**后四轮删笔中，REPAIR 类有 **163 次**，误删真病灶 **1578.0159 mL**；全部删笔误删 **2159.2841 mL**，相除为 **73.0805%**。因此它不是“73% 的删笔有问题”，也不是“73% 的患者受到这类影响”。**78%** 来自另外挑出的 **97 个状态**：483.7／621.4 mL，不能替代全量 73.1%。

   **证据：**同一组 VAL 原始记录；分类规则见归档包内 `round3-discussion-20261004/a4-work/a4_r3_codex.py` 第 26–45 行；正文见 [第 4.6 节](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:277>)。

   **建议改法：**始终写“**按体积规则标为 REPAIR 的笔**”。该规则会利用前一轮方向和新错量，本身没有证明当前笔在空间上确实落在前一轮新错上。邮件已经写了 “volume-based classification”，这一限定应保留；T083 的概述仍把 78% 写成宽泛结论，需修正。

4. **[D] “15 次小病灶删笔崩塌” → 正确，是明确的失败现象，但不是 15 个独立病例。**

   原始记录复算为 **15 个事件、7 个扫描、6 位患者**，全部是 REMOVE，全部扫描病灶总量小于 5 mL；实际上这 15 个事件对应的最大病灶总量只有 **1.6588 mL**，中位 **1.1280 mL**。其中 **9 次**到 D5 已恢复至崩塌前 0.05 以内，**2 次**发生在第 5 轮。

   **证据：**flat 的 `six_state.csv`、`transitions.jsonl`、`trajectories.jsonl` 中已存的病灶体积；与 [第 4.5 节](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:250>)一致。

   **建议改法：**邮件可保留一句，但写成 “15 deletion events across seven scans from six patients”。不能把 15 次直接当成总体发生率的独立样本，也不能把每次单步跌幅都算作最终 D5 损失。

5. **[D] “加笔外溢接在病灶上，下一轮删外溢时切进病灶” → 合理假说，现有证据尚未证明这条完整空间过程。**

   支持它的事实包括：第 1 轮加笔确实制造新多分；后几轮删笔确实伤到真病灶；REPAIR 类集中承担误删体积；挑出的 97 个删笔状态里，大部分误删发生在笔所碰、且含真病灶的预测连通块中。

   证据的缺口是：尚未把**上一轮新加的真阳性、上一轮新加的假阳性、此前已有的真阳性、当前笔、当前误删位置**逐体素对应起来。标量体积相符不能替代这个对应。

   已有结果还限制了过于简单的解释：

   - 97 个状态中，误删体积约 **80%** 来自“一笔伤到两个以上病灶”，不是只切坏一个局部小病灶。
   - STATIC／INDUCED 的后几轮删笔平均增益已经转正，但 D5 增益仍很小，因为加笔收益同时下降。
   - 撤回上轮新增体素，仍可能撤掉上轮**正确补出的病灶**，所以撤回并不天然安全。

   **证据：**[本地分析第 4.5–4.6 节](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:266>)、[第 4.10 节](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:363>)、[PLAN 的撤回定义](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/PLAN.md:57>)。

   **建议改法：**邮件目前的 “One explanation we have not yet checked spatially” 是合适措辞，应保留。不要升级成已确认机制。

6. **[D] “怎样最便宜地验证上述机制” → 用已存原生状态做空间交集，零模型前向即可；仅靠当前标量表做不到。**

   设上一轮 ADD 为 \(M_{t-1}\rightarrow M_t\)，当前 REMOVE 为 \(M_t\rightarrow M_{t+1}\)，标准答案为 \(G\)。只需已有 TRAIN／VAL 的这些掩码和当前笔：

   - 上轮新增：\(A=M_t\setminus M_{t-1}\)。
   - 上轮新造假阳性：\(E=A\setminus G\)。
   - 本轮误删：\(L=G\cap M_t\setminus M_{t+1}\)。
   - 把误删拆成此前已有的病灶 \(L\cap M_{t-1}\)，以及上轮刚补对的病灶 \(L\cap A\)。

   再检查当前笔所指假阳性连通块与 \(E\) 的重叠，以及它和被误删真病灶的接触位置。这样才能区分“删外溢伤到旧病灶”“撤掉上轮正确新增”“删除远处其他病灶”。

   **证据：**[本地分析第 505 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:505>)已经指出同一证据缺口。

   **建议改法：**先查看这 7 个崩塌扫描，并加正常 ADD→REMOVE 的患者对照；若空间过程确实存在，再对已存轨迹全量汇总。不要只检查那 97 个经过筛选的状态，也不要只挑伤害最大的正例。本次没有读取这些掩码或执行新的空间分析，因此该假说仍未验证。

7. **[D/B] “我们的撤回只限系统上一轮写过的体素，LIM-Net 的整层回退不限这些体素” → 后半句作为实质区别不成立，新意必须再收窄。**

   这是一个无需联网即可检查的集合关系。若在切片区域 \(C\) 内把当前二值掩码退回上一轮，真正改变的体素必然是：

   \[
   C\cap(M_t\triangle M_{t-1})
   \]

   即该切片内前后不一致的体素。整步回退同理。因此，**“实际变化仅发生于前后差分”本身不是与整层／整步回退的充分区别**。

   **证据：**文献页对 LIM-Net 的描述是逐切片把结果退回上一轮，[literature-domains-review.md 第 156–161 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/literature-domains-review.md:156>)；上述公式直接由这种操作推出。

   **建议改法：**可以争取的区别是：**由当前这笔定位，在上一轮反向改动中生成多个局部、不同范围的撤回候选，再与范围、续修、不改一起学习选择**。不要把“差分体素限制”单独列为首创。表 3 的 LIM-Net 行、表 6、文献页该条的“限制”都要改。

8. **[D/B] 两条“本次检索未见”的新意 → 可以作为待检验的窄主张，不能作为已确立贡献。**

   - **执行端：**EFPNet 已有点击所指连通错误目标；PRISM 等已有候选质量预测；LIM-Net、IBISAgent 已有回退；Correction-aware 已有历史、修订通道和候选质量分。剩下的是上一条所述的**当前笔条件下的局部撤回候选构造与联合选择方式**。
   - **训练端：**CPC-SAM 已有同目标提示一致性，VTMR 已有不同起点条件下的一致性，Prompt-RIS 已有同／异目标的对比关系。广义“换提示就换目标”也不是新能力。可以研究的是：**同一纠错状态中的多处残差，通过配对监督交换 T，同时明确要求未被指的错误保持不动**，以及这个配对项是否优于使用相同样本的独立监督。
   - “当前状态变了便重算 T”是目标定义的自然结果，EFPNet 的当前错误目标也已有这一成分，不宜另算独立创新。

   **证据：**[PLAN 第 40–45 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/PLAN.md:40>)及文献页对应条目。这里核的是本机记录的一致性，没有重新联网验证文献，也没有证明检索覆盖完备。

   **建议给导师的一句话：**

   > Our literature review suggests two potentially distinctive combinations: stroke-conditioned local rollback candidates selected jointly with scope, continuation and no-change actions, and paired correction supervision that switches the target while preserving unreferenced errors; their benefit and novelty remain to be established.

9. **[D] “组 A、组 B 大概能涨多少” → 有可修空间，但目前没有足够数据给出统计意义上的收益预测。**

   第 4.7 节的单步上限来自 **19 个首轮样本**和 **200 个挑出的后续状态**，使用真值选候选，且主要取自旧 v1。它既不是新起点模型的空间，也不是五轮收益，不能把首轮 +0.064、后续删笔 +0.050 相加或乘轮数。

   第 4.9 节更适合做有限的情景计算：

   - 均匀把首轮 ADD 修回率提高至 40%：D1 约 +0.0104；乘历史保留比例 0.48–0.91，D5 约 **+0.0050～+0.0095**。
   - 提高至 60%：D1 约 +0.0211；同样折算，D5 约 **+0.0101～+0.0192**。
   - 这些仍假定新增错误不增加，不能当成实际模型预测。

   **证据：**[单步上限](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:294>)、[保留比例推算](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:330>)。

   **用于资源规划的主观范围，非置信区间：**

   | 改法 | 相对其同口径对照，可合理争取的正增益 | 主要限制 |
   |---|---:|---|
   | 组 A | 三画法 VAL D5 **0～+0.015**；+0.02 属乐观情形 | 新起点的删笔均值已转正；能否挑对候选、避免反复不改尚无结果 |
   | 组 B | **0～+0.025**；+0.03 以上需要明显的多轮协同收益 | 目前自身状态续训只给 +0.00035，新增边界、范围、配对项尚未证明有效 |
   | A+B | 有效时可把 **+0.01～+0.03** 作为规划情景 | 两组解决的错误重叠，不能把各自上限相加；也存在零收益或退步 |

   组 A 的 INDUCED 起点尚缺同口径三画法成绩，不能拿快速 VAL 的 0.7606 当作其三画法起点。组 B 的科学增益应优先对同父、同预算 STATIC 比较。

   我仍认为 **B1 的误删／误加约束、组 A 对坏编辑的识别、B2 对近处漏修的改善**比先增加组 C 更值得优先兑现。漏修体积 83% 在远处，不代表患者平均 Dice 的收益也主要在远处：真值只补近 30 mm 的 D1 增益为 +0.026，高于只补远处的 +0.0152。

10. **[D] “10-18 或 10-22 前到 0.79 的把握” → 目标有依据，但当前不能报高把握。**

    从已验证的 v1 三画法成绩算，需要 **0.79−0.7523582394＝0.0376417606**。这超过上述较保守的 A+B 规划情景上端，需要更强的协同、后续候选或工程增益。

    **判断：**10-18 目前只能给“偏低到中等”的主观把握；若磁盘问题及时解决，且 10-05／06 的真实五轮组 A、随后组 B 显示稳定的 1–2 点增益，10-22 可上调到“中等”。这不是经过校准的成功概率，现有数据不支持给百分比。若首批只有单步好、五轮不涨，多四天也不能自动解决问题。

    **证据：**第 9 项的计算、[PLAN 的申请条件与检查点](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/PLAN.md:122>)。

    **建议改法：**邮件只写目标和检查点，不写“预计届时达到”。更不能把 v1 曾经 TEST 高于 VAL 约 0.017，当成新模型从 0.79 到 TEST 0.80 的保证。

11. **[A] 邮件第 5、13–15、22–27、37 行的主要 TEST 数字 → 数值正确，但开头必须指明 0.7694 属于 flat 版本。**

    已从逐患者汇总、SIRB 原始六状态表及 P2T／2S-ICR 的 `evaluation.json` 交叉核对：

    | 模型／结果身份 | TEST D0 | TEST D5 | 核对结果 |
    |---|---:|---:|---|
    | nnU-Net 五折概率均值基座 | 0.6386864 | — | 0.6387 正确 |
    | 3D P2T，单次训练 | 0.6386864 | 0.7024271 | 增加 0.0637407，邮件 +0.064 正确 |
    | SIRB v1 factorised／N3 | 0.6386864 | 0.7619205 | 增加 0.1232341，+0.123 正确 |
    | SIRB v1 flat／N1_STATE | 0.6386864 | 0.7693647 | 增加 0.1306783，+0.131 正确 |
    | 二值涂鸦通道，五折合成 | 0.3782744 | 0.7657391 | 0.7657 正确 |
    | 距离图涂鸦通道，五折合成 | 0.0003269 | 0.7495106 | 0.7495 正确 |
    | 2S-ICR fold0，单折补充结果 | 0.5778337 | 0.7999744 | 0.5778→0.8000 正确 |

    flat 相对 P2T 高 **0.0669376**，邮件 +0.067 正确。TEST 共 91 扫描／57 患者；Dice 排除 9 个空标准答案扫描，按 82 扫描／56 患者计算。

    **证据：**[成绩登记第 45–54 行](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/sources/petct-eval-results-register.md:45>)；`records/eval_results_transfer/eval-sirb-lockedtest-20260928-R1/server-originals/statistics-e06-early/patient_summary.csv`。

    第 1 轮 flat＝**0.7221006**，2S-ICR＝**0.7216001**；最终差 **0.0306097**，邮件的描述正确，但只说明不同系统的曲线形状。

    **建议改法：**开头用 “The flat variant of SIRB-Net v1 reached 0.7694 …”。0.8000 应在开头就标为 2S-ICR **single-fold**，防止导师把它读成五折最终基线。

12. **[A] “主比较 inconclusive；flat passes 两个涂鸦基线” → 前半句正确，后半句应改成均值描述。**

    原统计文件给出 factorised−flat 的 nAUC 差 **−0.0118254103**，95% CI **[−0.0269817804, 0.0019663146]**，sign-flip p＝**0.1270872913**，56 位患者。邮件的 −0.012、[−0.027,+0.002]、p＝0.13 均正确；单种子区间只反映患者抽样的限定也正确。

    但 flat−二值基线 D5 差为 **+0.0036257**，95% CI **[−0.0287006,+0.0300261]**；flat−距离图为 **+0.0198541**，CI **[−0.0145449,+0.0483992]**。均跨零。N3 相对二值低 **0.0038185**，相对距离图高 **0.0124099**，其区间也跨零。

    **证据：**同目录 `registered_comparisons.json` 的 `comparisons` 和 `descriptive_contrasts`。

    **建议改法：**把 “passes” 改成 “has a higher mean D5 than …”。这些基线对比不是正式主比较，也不能据均值称已证明超过。

13. **[A] “each model was run on TEST once” → 字面不准确。**

    已有 SIRB 默认轨迹、E08 第二大错误、E08 短点等预定评测；P2T 登记明确记录第一次失败后修复、新授权重跑；涂鸦基线也有历史单折与后续五折结果。遵守授权、固定模型、不按 TEST 选点，不等于整个模型只接触 TEST 一次。

    **证据：**[成绩登记第 42–54 行](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/sources/petct-eval-results-register.md:42>)。

    **建议改法：**删掉这句绝对表述，改成：

    > These are fixed-model TEST results; version-2 development and model selection use TRAIN and VAL.

    后文未来的 “the single TEST run” 也应考虑最终是否有单模型、集成两臂：决策允许一次授权、事先列明两臂、每臂一次，并非必然只有一个运行。

14. **[A/D] “所有基线都按我们同一五折、作者配方重训，完全干净可比” → 邮件压缩掉了实质差异。**

    - 二值、距离图两臂的 **fold0 使用旧 407／99 单折**，其余折按五折方案；这是已批准保留的例外。
    - SIRB 是一个编辑器训练划分，基座另有五折；不能让读者以为 SIRB 编辑器也训练了五折。
    - 2S-ICR 原论文是头颈 PET/CT 点击修正；本项目是全身 PSMA 的涂鸦适配。基线按作者方法重训，不等于未经适配的原配方复现。
    - 基线的起点、模型数、预算不同，比较是系统级终点比较；正式同预算主比较是 N3 对 flat。
    - VAL 存在已记录的间接路径：**VAL 标签→基座折模型→TRAIN 起点→SIRB 训练状态**。不能把 VAL 称为整条系统完全未见。
    - TEST 患者虽未进入学习池训练，但基座实际使用的四个 CT 归一化常数来自包含全部 597 例的数据指纹。影响大小未测，因此“所有训练来源完全没有任何 TEST 信息”也过强。

    **证据：**[T013 第 140–141 行](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/tasks/petct-t013-baseline-scribble-fivefold-official-test.md:140>)；[本地分析第 469–494 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:469>)。

    **建议改法：**邮件用 “patient-level splits and a common five-round evaluation protocol, with differences in starting models, fold coverage and adaptations documented on the website”。细节放网站／论文，但不要用绝对一致、完全未见的概括替代披露。

15. **[A] 基线名称、出处、名次、取舍原因 → 大部分与本机核查记录一致，以下限定应补。**

    本项只按已有本机来源核对，未重新联网核验外部发表和排名。

    | 原说法 | 判定及建议改法 | 证据 |
    |---|---|---|
    | nnU-Net 五折自动基座、不给提示 | 对；它是 SIRB 起点和自动参考 | 本地分析第 74 行；成绩登记第 49 行 |
    | 两个涂鸦通道 nnU-Net 源于官方 autoPET V 设计 | 对；写“based on the official baseline design”，不要暗示官方直接提供本项目两组成绩 | `petct-autopet-comparators-current.md`:78–80；T013:140 |
    | 2S-ICR 是 Scientific Reports 2025 | 对，文献页有明确条目；2024 是预印本年份 | 文献页:393–398 |
    | 2S-ICR 是最接近的已发表 PET/CT 方法 | 有依据，建议 “a directly relevant published PET/CT correction method”；“closest”不是可穷尽证明的排名 | 同上 |
    | 把 2S-ICR 称为 autoPET IV 方法 | 不对；本地分析第 14 行有这种旧写法，但其对应文献是 HECKTOR 头颈研究 | 文献页:393–398 |
    | UAM 有 previous-mask feedback、online error-driven scribbles、organ supervision | 三项都与正本一致；是 autoPET V 参赛方法，不能补一个未核实的最终名次 | 比较正本:67、219–223 |
    | IKIM 是 autoPET III 第二名且 PSMA 专用 | 要限定为 **2024 autoPET III Modelcentric 综合第二名，采用其 PSMA 分支**；不是 Dice 单项第二，也不是整个方法只适用于 PSMA | 比较正本:150、183–195 |
    | IKIM 从头训，排在 2S 后 | 对；不使用作者训练过 PSMA 病灶的模型权重 | 比较正本:150；21:48 现场后续等待记录 |
    | BIRTH 是 autoPET IV 冠军，7–13 小时／epoch | 基本对；精确记录为本机当时 **7.4–12.9 小时／epoch**，不是其固有耗时；只完成 6／1000 轮 | 比较正本:123、166、205 |
    | LesionTracer 是 autoPET III 冠军，被 IKIM 替换 | 对；本机每轮约 **1333–1404 秒，即 22.2–23.4 分钟**；只完成 9／300 轮，取舍来自成本和资源竞争 | 比较正本:135、141、167、189 |
    | autoPET-interactive 是 autoPET IV 第二名 | 对，但明确为 **Task 1 综合第二名**；Dice 单项第二是 Zhack | 比较正本:42–47 |
    | autoPET-interactive 需要超过 24 GB | 要限定为**所测试训练配置的本地合成检查为 25.51 GiB**；不能写成所有配置、所有推理都需要 >24 GB | 比较正本:131、168 |
    | 它有两配置集成 | 对，作者最终配置是 **2 配置×5 折** | 比较正本:56、60 |
    | 三个方法没有在本划分上产生结果 | 改为“没有完成可报告的最终评估”；它们有过部分训练、测速等记录 | 比较正本:166–168 |
    | 都能按作者配方在每折约 3–5 天完成 | 作为筛选目标可理解，但不是每种方法当前实测承诺 | 实验安排:124–149；比较正本中的各项估算 |

    比较正本实际路径是 [knowledge-vault/wiki/syntheses/petct-autopet-comparators-current.md](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/syntheses/petct-autopet-comparators-current.md>)。

16. **[A/B] 表 1 和邮件中的 SIRB VAL 数字 → 数值正确；“多训不能缩小差距”超出了证据。**

    我从原始六状态表复算了五个续训结果，并按相同画法分配抽取 v1 对照：

    | 模型 | 三画法 VAL D5 | 快速 VAL D5 | 核对／解释 |
    |---|---:|---:|---|
    | v1 flat | **0.7523582** | **0.7561546** | 表 1 的 0.7524／0.7562 正确 |
    | STATIC | 尚不能由快速值代替 | **0.7602166** | 对匹配 v1 **+0.0040620**，四舍五入 +0.0041 |
    | INDUCED | 同上 | **0.7605693** | 对 v1 **+0.0044147**；对 STATIC **+0.0003527** |
    | SPATIAL | 同上 | **0.7548081** | 对 INDUCED **−0.0057612** |
    | N3 原配方续训 | 同上 | **0.7360119** | 属于 N3 的续训对照 |
    | N3_ES | 同上 | **0.7543607** | 对 N3 续训对照 +0.0183489，但仍低于 flat INDUCED |

    **证据：**各 `eval-sirb-v2-quickval-.../six_state.csv`；区间与 [本地分析第 353–358 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/local-data-models-results.md:353>)一致。

    表 1 四行的继承关系也基本正确：A 用 INDUCED，B 从 v1 flat，STATIC 作同预算对照，SPATIAL 未入选。应提醒“现行主模型”与“当前执行端起点”不是同一个 checkpoint。

    **建议改法：**邮件第 38 行改为：

    > An 8k continuation did not show a reliable improvement in final Dice on quick VAL; training on model-generated states gave a further mean change of only +0.00035 over the matched continuation control.

    “这一次没有测到可靠提升”成立；“更长训练无法缩小差距”不成立。五个续训的范围 0.7360–0.7606 正确，但包含两种输出头、不同改法，不能拿这整个范围证明训练长度的作用。

17. **[A/C] 新收回的 2S-ICR fold2 VAL、三折均值 → 独立复算全部一致；旧 fold0／1 人数写法有混淆。**

    | 折 | 全部扫描／患者 | Dice 阳性扫描／患者 | 患者平均 D0 | D5 | nAUC |
    |---|---:|---:|---:|---:|---:|
    | fold0 | **104／64** | **96／62** | 0.5193061732 | 0.7857339556 | 0.7109992878 |
    | fold1 | **102／65** | **94／64** | 0.4747436225 | 0.7615007013 | 0.6862220060 |
    | fold2 | **100／63** | **88／62** | **0.4887913993** | **0.7439269043** | **0.6566650628** |
    | 三折等权暂定值 | **3／5 折** | 不补缺折 | **0.4942803983** | **0.7637205204** | **0.6846287855** |

    **计算：**只取 `gt_empty=false` 的病例；先平均同一患者的扫描，再平均患者；每条六状态曲线用梯形积分除以 5；最后各折等权。逐例 nAUC 与保存值最大差 **2.22×10⁻¹⁶**。fold2 清单列出的 **101 个文件**本机 sha256 全部匹配；本次没有重新连接远端验证。

    **证据：**三个 `baseline-2sicr-fold*-val-*/cases/*.json`；新折 [传输目录](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/baseline-2sicr-fold2-val-20261004>)；算法与 [builder 第 129–245 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/reporting/build_sirb_results_dataset.py:129>)一致。

    **建议改法：**邮件补第三折和 3／5 暂定均值。hot 的“104 扫描／62 患者”“102 扫描／64 患者”混合了全部扫描与阳性患者分母，应分别列清。三折均值既不是同一验证人群上的集成成绩，也不能与 SIRB 的 0.7524直接排名。

18. **[A] “约 480 篇、12 个领域、重读 118 篇” → 12 个领域可确认，其余属于已有调研记录的统计，不能写成已独立审计的去重阅读量。**

    文献页第 25 行明确说跨领域重复未完全剔除，合计约 470 条，补查后约 483 条；表中各领域近似数相加约为 486，因此“约 480”适合作为**条目量级**，不宜解释为 480 篇全局去重论文。

    “118 篇”在第 25 行有明确记载，但本次没有逐一重建“118 个唯一论文→原文段落→核查回执”的对应。当前文件有 119 个带核查信息的文献标题，其中 115 个标题标“原文核过”、4 个标摘要；另有重复条目和一条包含多篇的情况，不能直接拿标题数证明精读篇数。

    **证据：**[文献页第 23–42 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/literature-domains-review.md:23>)。

    **建议改法：**短邮件删两个篇数，写 “We reviewed work across 12 research areas and checked the most relevant methods against their original descriptions.” 详细调研量及来源留网站，并区分筛查、摘要、相关段落核读、全文阅读。

19. **[A] 邮件 3b 的五组思想及列举文献 → 都能在文献页找到，但不能把跨领域类比写成对本方法有效性的共同证明。**

    | 五组概括 | 对应情况 | 应补的限定 |
    |---|---|---|
    | 局部编辑＋执行前判断收益 | 所列 FocalClick、VISTA3D、DIG、SERAC、IKE、Todorov、Lipton、RankSEG 都在 | 各论文分别支持局部性、范围分类、决策结构；并非每篇都支持“整例 ΔDice 打分” |
    | 自身状态训练＋自身历史 | DAgger、SEARN、LOLS、RITM、PRISM、2S-ICR、UAM、运动指令副本、Losey 都在 | SEARN／LOLS 的后续代价不同于当前一步标签；Losey 是人机纠正类比 |
    | 学边与连通决定范围 | MALIS、Funke、AffinityNet、IRNet、BoxInst、Roelfsema 都在 | BoxInst 不是 max-min 连通；认知研究不证明该结构在 PET/CT 上有效 |
    | 成对干预与保持不变 | Kaushik、Gardner、Gentner、Frank & Goodman 都在 | Gardner 是评测；RSA 是指代推断启发，不是本项目配对损失或因果识别的证据 |
    | 语义尺度、物理量、损失量级 | nnU-Net、nnInteractive、Xin、Kurin 都在 | nnInteractive 自身也有手定系数；两篇优化研究没有证明“一次 TRAIN 标定必然足够” |

    **证据：**[文献页第 9–15 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/literature-domains-review.md:9>)及各篇条目。

    **建议改法：**“Five ideas … version 2 is built on them” 可以保留；把“可信度最高／多个领域独立证明”这类扩展说法留掉。邮件可压成两句，具体论文列表移网站。

20. **[A/C] 邮件时间线 → 应区分目标、检查点和已开始的步骤。**

    - “Version 2 is now running”：广义项目推进成立；21:48 运行的是起点模型 TRAIN 回放和候选采集，不能读成组 B 新模型已训练完成或已有效。
    - 5–6 日首批 VAL、11 日小结：属于计划，当前仍可能实现，但受磁盘和联合回放时长影响。
    - “18 Oct, latest 22 Oct”：**错误地保留了最晚锁定日含义**。D-2026-10-04-03 已改为两个检查点，未到 0.79 就继续，不申请 TEST。
    - 31 日全部实验结束：是目标；应补“10-30 24:00 后不开新任务”。UAM／IKIM 未完成时，结论只覆盖已完成基线。
    - 11 月中旬 Honours：本机时间表写 **11 月上中旬**。这是项目计划，不是本次已核学校正式截止日。

    **证据：**[决策正本第 65–73 行](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/sources/petct-decision-register.md:65>)；[PLAN 第 114–129 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/PLAN.md:114>)；时间表第 130 行。

    **建议改法：**“We will review progress on 18 and 22 October and request TEST evaluation only after three-style VAL reaches 0.79.”

21. **[A] “98 页论文初稿已准备好” → 页数正确，完成程度应限定。**

    本机直接读取 `honours-thesis-revised-20261001.pdf` 得到 **98 页**。T082 分解为前置 11、主文 59、参考 4、附录 24 页，合计一致。

    **证据：**[PDF](<C:/Users/廖神/Desktop/Honor degree/Honor thesis/Honor paper submission/drafts/honours-thesis-revised-20261001.pdf>)；[T082 第 40–46 行](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/tasks/petct-t082-honours-thesis-drafting.md:40>)。

    **建议改法：**写 “A 98-page working draft is in place, with the final results and version-2 revisions still to be incorporated.” 现稿日期早于当前 V2 定稿，不能暗示只差把几个结果数字填进去。

22. **[B] 表 2 的全部实验行 → 大体吻合 PLAN，但有几处摘要改变了方法或预算含义。**

    下表 `P` 指 [PLAN.md](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/PLAN.md>)，`E` 指 [experiment-schedule-gpus.md](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/experiment-schedule-gpus.md>)。

    | 表 2 行 | 判定及建议改法 | 证据 |
    |---|---|---|
    | A 执行端意图解码 | 基本对；挑的是**预测的** \(g_T\)，不是知道哪项真实 Dice 最好。“不重训”指主网络，仍需拟合树模型。“不奖励 O”不等于保证不改 O | P:57–63 |
    | B1 编辑合同 | 新增三项概括对；不要扩写成 v1 原来没有保留监督或难样本，v1 已有 P 保持项及 O／P 抽样 | P:70；本地分析:129–130 |
    | B2 第 1 轮范围 | 对；第二块按未覆盖 T 的比例决定，从未覆盖 T 内均匀抽中心，不固定取最远点 | P:71 |
    | B3 运动指令副本 | 对；新增的是实际改动与标志，原用户笔迹历史保留；首版不存上一轮整卷 pT | P:72 |
    | B4 自身状态池 | 对；应写明联合回放、旧诱导池与原离线库并用，首版不做中点刷新 | P:73、77；E:73 |
    | B5 块内配对 | 基本对；换目标须为另一处**同方向**错误，并控制大小和到笔距离；正对要求原生 T 完全一致 | P:74 |
    | B6 损失对齐 | 做法对；“1／500–1／800”指旧诊断中的**加权梯度影响量级**，不是简单损失值比 | P:75；本地分析:400 |
    | C 学出连通 | 新做法对；“原本用距离判断范围”过度简化，原网络也用影像、状态与笔特征；C 还含跨块配对和选笔混合，不能只归因于图 | P:81、47 |
    | D1 权重平均 | 对：STATIC 与 INDUCED 同父、同结构权重平均；零训练不等于零验证成本 | E:70；P:95 |
    | D2 翻转平均 | 对；两次预测先还原到同一空间再平均、执行 | P:96、99 |
    | D3 种子集成 | 推理描述对；“不训练”仅指合并动作，第二个成员仍需完整训练链 | P:85、97–99 |
    | TRAIN 回放＋三画法 VAL | 对；407 扫描是 TRAIN。4.7 小时是 **0.5 执行**三画法估时；组 A 三画法估 6–9 小时 | E:55、59、67–68 |
    | 第二种子 40k 父模型 | 对；必须再走最终续训链，才能算真正第二种子；当前队列写定为 3408 | P:85、89；T083:65 |
    | 第二段最多 3 个候选 | 常规候选从 v1 续训 8k 对；**加宽候选从头训 40k**、加长候选续训 16k 是另列的规模分支，不能共用该行“父模型＋8k”描述 | P:85–87、120–121 |

    “四组都建在 v1 flat 上”作为共同祖先概括成立，但 A／D 使用已完成续训版，C 使用 B 赢家，不能说四组直接从同一个 checkpoint 开始。

23. **[B] 表 3–5 的逐篇核对 → 下列判断区分“与文献页一致”和“已证实对本项目有效”。**

    下表 `L:行号` 均指 [literature-domains-review.md](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/petct-sirb-v2-referent-scope-plan-20261003/literature-domains-review.md>)。**“原文”仅表示该页已有“原文核过”标记，不表示本次又把全部论文原文重读了一遍。**

    | 论文／用途 | 思想与“我们怎么用”的判定、建议改法 | 文献页核查状态／证据 |
    |---|---|---|
    | FocalClick／A | 思想对；表中“执行时只改相连块”太像全局硬规则。改成相连候选的依据和规则合并对照；最终方案还保留整个水平集候选的条件评估 | 原文；L:72–77，P:57 |
    | VISTA3D／A | 思想及规则对照用途对；标为 CT 方法。2024 是预印本，正式会议信息为 CVPR 2025 | 原文；L:79–84 |
    | DIG／A | 思想对；“和我们只管 T 相同”须限定。它把其余块作 void，我们要求 O 不改，有实质区别 | 原文；L:86–91 |
    | PRISM／A、B4 | 多候选＋质量头、迭代训练迁移对；同状态下 Dice 与 ΔDice 排序等价，换名字不构成新意 | 原文；L:93–98，P:40 |
    | Semantic-SAM／A | 多粒度与选错候选的问题概括对；不能把 oracle 与自身选择差距当预期收益。正式版 ECCV 2024 | 原文；L:100–105 |
    | PiClick／A、B4 | 思想与迁移对；2023 预印本，Neurocomputing 2024 | 原文；L:107–112 |
    | SAM／A | 与短条目一致；“读涂鸦差”没有在本页展开条件，不宜作为已充分核实的一般缺陷结论 | 一行，“ChatGPT 核”；L:186 |
    | SEARN／A | 思想对；“组 A 就是一步 SEARN”改“受代价敏感动作选择启发”。原法用后续总损失、迭代与策略插值 | 原文；L:731–736 |
    | EFPNet／A | 含新点击连通错误作为训练目标的概括对；不能再将 T 定义或随当前错误重算单独列为新意 | 原文；L:149–154 |
    | Correction-aware／A | 概括和用户修订／系统改动的区别对；它不等于本项目局部撤回，但历史及候选质量分已有先例 | 原文；L:142–147 |
    | LIM-Net／A | 逐切片回退思想对；“不限系统改过体素”不是有效区别，见第 7 项 | 原文；L:156–161 |
    | IBISAgent／A | 与本机条目一致；限定为合成轨迹中包含回退，不能由此推断所有推理都按这种策略运行 | 一行、无逐条原文标记；L:198 |
    | SLIP／A | “用户触发撤回”与条目一致；其余实现细节本页没有依据 | 一行、未标；L:203 |
    | Todorov & Jordan／A | 最小介入思想对；只是任务效用类比，不能证明修 O 有害 | 原文 L:780–785；另有摘要重复条目 L:1107 |
    | MEND／B1 | 思想与难保留样本迁移对；不把本项目说成实现了参数编辑 | 原文；L:1182–1187 |
    | SERAC／B1 | 思想与难例迁移对；空间边界排序是我们的迁移，原文范围是语义集合 | 原文；L:1189–1194 |
    | IKE／B1 | 思想与迁移对；原文改的是推理提示示例，不能据此推出训练体素 1:1 配额 | 原文；L:1196–1201 |
    | BoxInst／B1 | 对；坏的是错误正边造成传播，不能再简化为“只用正边必塌” | 原文；L:246–251 |
    | IRNet／B1 | 与条目一致；“只能靠学出的边界”过强，宜改“需要能区分内部真假边界的证据，边界学习是一种方案” | 原文；L:267–272 |
    | DCT-Net／B2 | 思想与影响半径迁移对；原文未写清 Auto-Drag-Head 的损失，不能补成已知配方 | 原文；L:407–412 |
    | nnU-Net／B2、系数 | 三类参数思想及迁移对；它不是“所有参数都必须学习”的证据 | 原文；L:351–356 |
    | GECToR／B3 | 编辑标签、KEEP、迭代概括对；“上一轮实际改动作输入”是我们的推论，不是原文直接验证过的模块 | 原文；L:1231–1236 |
    | RITM／B3、B4 | 自身状态和上轮掩码思想对；表中“加上一轮概率作输入”不符合最终 B3 首版，需删或标后备 | 原文；L:121–126、766–771；P:72 |
    | TIA／B3 | PID／时间反馈思想对；“历史近邻”可保留，但本条明确迁移的是下降次数与幅度指标，不能说它证明实际差分输入有效 | 原文；L:787–792 |
    | DAgger／B4、A | 自身策略状态上标注、合并再训对；文献页还残留“8k 中点刷新”旧建议，最终计划明确不采用 | 原文；L:724–729；L:21、P:77 |
    | 2S-ICR／B4 | 在线自身状态思想对；我们的离线状态池不是完整复制作者每次交互更新参数的训练过程 | 原文；L:393–398 |
    | SCoRe／B4、A | 离线轨迹分布偏移及少改／不改塌陷对；是风险提示，不能证明本项目已经发生同一种塌陷 | 原文；L:759–764 |
    | Kaushik／B5 | 最小改变使标签翻转、用于换目标配对的迁移对；跨域效果不直接外推为医学 Dice 收益 | 原文；L:1329–1334 |
    | Gentner／B5 | 比较样例迁移思想对；“比较才学得会”太绝对，改“引导比较在其研究中提高迁移”；不能推出损失权重 | 原文；L:1079–1084 |
    | CPC-SAM／B5 | 双分支＋中心／随机提示一致性对；它是同目标一致性先例，没有目标交换 | 一行、未逐条标；L:190；P:45 |
    | VTMR／B5 | 两种同质量起点的一致性对；表中“同上”不可读成它研究的就是换提示，改变的是起点条件 | 一行、未逐条标；L:199 |
    | Prompt-RIS／B5 | 同目标拉近、异目标推开的概括对；恰好限制了泛化的“换目标配对首创”说法 | 一行、未逐条标；L:201 |
    | Gardner／B5 评测 | 思想与“只用于评测”均对 | 原文；L:1350–1355 |
    | Xin／B6 | 思想与固定加权和优先的选择对；不能推出不调权在本任务必然最优 | 原文；L:1489–1494 |
    | Kurin／B6 | 思想与迁移对；结论受实验、正则、量级条件限制 | 原文；L:1496–1501 |
    | MALIS／C | 瓶颈连通与边监督思想对；原目标是连通错误，不是 Dice | 原文；L:495–500 |
    | Funke／C | 正负两遍 MALIS 模板对；书目信息应写 2018 在线、2019 卷期 | 原文；L:502–507 |
    | APro／C | 并查集／瓶颈迁移对；“最大边”指最大**边代价**，别和最大亲和度混淆。新算子的梯度及三维成本仍需验证 | 原文；L:253–258 |
    | AffinityNet／C | 思想与边头迁移对；最终方案不照搬 256 步随机游走及伪标签 | 原文；L:260–265 |
    | Roelfsema & Houtkamp／C | 思想与软特征迁移对；属于认知类比，没有证明网络中同样的分工更好 | 原文；L:835–840 |
    | Jeurissen／表中 C | 思想对，组别不一致：文献页把宽度折算路径距离放 **B 的可选几何**，并强调与 C 的 max-min 是两种量；最终首版未明确纳入 | 原文；L:849–854 |
    | Wortsman／D1 | 权重平均思想及用途有实验安排依据；**不在文献页对应条目中**，0–1 点只是项目推测 | 文献页缺项；E:213 标“本轮没重核” |
    | Bouthillier／第二种子 | 随机性来源概括对；整条链重训是针对本项目问题的合理设计，不是该文直接规定的实验流程 | 一行、未逐条标；L:205 |

    表 4 另有“运动指令副本”一行：它是控制论概念，文献页 **L:720** 有对应说明，没有单篇论文身份；计数时不应算作第 44 篇论文。

24. **[B] 表 7“35 篇原文核过，8 篇标注不全” → 按这 43 篇的逐条标记计算，正确，但“8 篇”应拆开。**

    独立清点得到 **43 篇论文＋1 个概念**；43 篇中：

    - **35 篇**能找到明确“原文核过”的条目。
    - **7 篇**只有短条目：SAM、IBISAgent、SLIP、CPC-SAM、VTMR、Prompt-RIS、Bouthillier。
    - **1 篇 Wortsman**未列入文献页，只在实验安排中出现并标“本轮没重核”。

    **证据：**第 23 项逐篇定位。

    **建议改法：**不要把这 8 篇统称为“没核实过”。例如 SAM 写了“ChatGPT 核”，PLAN 又笼统说补查包括读原文；目前的问题是**当前文献页缺少一致、逐篇可定位的核查标记**。反过来也不能把泛指的“都读了原文”当成逐条回执已经完整。

25. **[B] 表 6“借来的和我们自己的” → 借鉴概括基本成立，“我们自己的”应改“拟检验的区别”。**

    执行端近邻清单漏掉了 **Correction-aware**，它与历史／修订通道的边界直接相关，应加入。训练端广义“换笔换目标”已有大量提示分割先例；真正要评的是特定纠错任务中的配对损失与未指错误保持约束。

    **证据：**L:17、142–161、186–201；P:44–45。

    **建议改法：**两条都用第 8 项的窄表述，删去“差分体素限制本身独有”的暗示。对于“同一状态预测 Dice 与预测 ΔDice”，P:40 已明确排序等价，不可在邮件里暗示换成收益头便是贡献。

26. **[B] 表 8 的七处更正 → 基本都对，但其中两项需要措辞限定。**

    | 更正 | 判定 | 证据／建议 |
    |---|---|---|
    | MEND、SERAC、IKE 属 B1 | 对 | L:1182–1201；P:70 |
    | SAM 只有一行，Semantic-SAM 有原文条目 | 对 | L:186 对 L:100–105 |
    | SCoRe 对应 A 防不改塌陷和 B4 | 对，B4 属分布偏移的迁移启发 | L:759–764、1275、1289 |
    | SEARN 对应 A 回归器 | 对，但不要写成实现了完整 SEARN | L:731–736 |
    | 运动指令副本在控制论章、无单篇 | 对 | L:720 |
    | Gardner 只用于评测 | 对 | L:1354 |
    | Wortsman 标“本轮没重核” | 对，标记在实验安排，不在文献页 | E:213 |

27. **[B/C] 表 9“未完事项” → 不完整，且第一项已经过时。**

    **证据与建议改法：**

    - TRAIN 回放改为 **21:48 的 268／407**，不是 18:09 的 83／407；旧完成时间只是当时估计。
    - 加入 **数据盘 7.6 GB，已低于 15 GB 开工要求**，这是当前明确阻塞风险。
    - 2S-ICR 应改为 **fold2 完成、fold3 已启动，3／5 折 VAL 已收回**。
    - “组 A、B 无新成绩”仍正确；真实病例上跑通不能改写成效果已成立。
    - 补充 **INDUCED 起点三画法 VAL 尚缺、选择器在自身轨迹上的收益尚缺、空间机制尚未验证**。
    - “8 篇标注不全”按第 24 项拆成 7 个短条目＋1 个缺项。
    - 还应交代五折 ensemble TEST 未出、第二种子未完成，以及 VAL 的两阶段数据来源限制。

28. **[C] 21:48 现场 → 三台服务器状态如下；邮件与 hot 使用的晚间轮次都已过时。**

    | 机器 | 21:48 证据支持的状态 | 对旧说法的更正 |
    |---|---|---|
    | z390 | 起点 INDUCED 的 TRAIN 回放 **268／407**，1340 条 transition；进程与 v3 队列仍活着 | 不是 83／407，也不是组 B 已开训 |
    | z390 数据盘 | `/mnt/HDD4` 可用 **7.6G**，显示 100% 使用；系统盘可用 0 | 明确低于队列下一项开工要求的 15 GB |
    | RTX5090 | fold2 修正与 VAL 完成；**20:37:04** 出 100 例折回执；**20:37:07** 启动 fold3 automatic | 邮件“fold2 289／300”已过时 |
    | RTX5090 当前轮次 | epoch 28 已完成，21:48:32 开始 epoch 29 | 可写“fold3 automatic running, epoch 29 started” |
    | A6000 UAM fold0 | stage2 日志显示 **Epoch 485**，最近完整轮约 307.72 秒 | 不是 442 |
    | A6000 UAM fold1 | stage2 日志显示 **Epoch 355**，最近完整轮约 319.48 秒 | 不是 313 |

    **证据：**[21:48 原始现场文件](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/server_status/heartbeat-3-20261004-2148/latest.txt>)：UAM 第 77–83 行；磁盘第 288–291 行；v3 第 337–378 行；2S 第 494–523 行。

    **建议改法：**所有“现在”都附快照时间。训练器的 “Epoch 485” 不应擅自写成已经完成 485 轮；fold3 最严谨的写法也是“28 轮完成，29 轮开始”。

29. **[C] hot、T083、PLAN 中哪些过时 → 不只是进度数，T083 还保留了已撤销的决策表述。**

    - [hot:13–18](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/hot.md:13>)：三机轮次、z390 20 GB、83／407、2S 两折均值均应更新。
    - [hot:27](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/hot.md:27>)：仍写等待 SPATIAL 后定起点；起点已定为 INDUCED。
    - [T083:60](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/tasks/petct-t083-sirb-v2-mainline.md:60>)：“到 0.79 **或导演满意**”“最多再改到 10-22”与 D-2026-10-04-03 不一致，应以明确 0.79 条件和检查点规则替换。
    - [T083:66](<C:/Users/廖神/Desktop/Honor degree/knowledge-vault/wiki/tasks/petct-t083-sirb-v2-mainline.md:66>)：6／407、预计 05:00、CPU 负载 30–40 是更早快照；21:48 负载约 5.27，不能继续当当前状态。
    - T083:81 的 SPATIAL “101 机制在跑”、:83 的旧队列空等，已被 16:05 完成记录取代。
    - P:114–116 的“等待批准／5 日才部署 A”不是当前执行状态：R4 已部署，回放在跑。
    - E:146 的 fold2 137／300、E:156–158 的 45 GB 已过时。
    - 本地分析:126–127、159、509 的 N3_ES／SPATIAL“排队中、无结果”已过时。

    **建议改法：**更新现状时不要覆写历史事实，但现行段落应由新快照和最新决策取代，避免导师看到互相矛盾的“下一步”。

30. **[C/D] “PLAN 第四部分的日历还能否守住” → 主线首批结果日仍有可能，最大即时风险是磁盘；最大科学风险是单步空间兑现不了五轮增益。**

    回放进度从 18:09 的 83 到 21:48 的 268，219 分钟处理 185 例，约 **1.184 分钟／例**。剩余 139 例按该速度还需 **2.74 小时**；按自 16:16 开始的全程平均约 **2.87 小时**。不受阻时，结束约在 **10-05 00:33–00:40**，旧 01:40 并非最新推算。

    但这不等于组 A 马上出 VAL：后面仍有两折拟合、联合回放、重拟合、快速 VAL。E:55–59 给联合回放含候选约 6–9 小时、拟合约每次 1 小时、组 A 快速 VAL 2–3 小时。因此 5 日白天至夜间出首批结果在算力上仍可能，7–8 日组 B 的日历也未必失守。

    **磁盘已构成现实阻碍：**当前 7.6 GB 低于 15 GB；若执行检查保持原样，下一项任务开工时会停。当前运行仍活着，不能把它写成已经停机。若此前几个小时约 20→7.6 GB 的净占用速度持续，磁盘还可能在当前回放结束前耗尽；这只是风险外推，不是确定的填满时刻。

    **证据：**现场第 291、339、376–378 行；hot:16；E:55–59、162；P:127。

    **建议改法：**将日期写成受条件约束的计划。10-18／22 前是否到线，主要取决于首批真实五轮增益；10-22 后能否完成消融，则取决于实测候选成本、第二种子、集成臂和 A6000 何时可用。不能继续用旧的单步上限或理想 GPU 小时数支撑确定性交付承诺。

31. **[A] 邮件是否会被导师读成夸大 → 会，主要风险集中在几处措辞，并非主要成绩算错。**

    邮件按空白分词为 **1555 词**，与“约 1500 词”一致。建议下一版压到约 350–500 词，正文只留：两种 v1 结果及主比较、最强已完成基线的单折身份、已经确认的失败现象、下一轮检验及条件时间表。以下内容最容易误导，应优先改：

    - 将 flat 的最好均值直接冠名为 SIRB 主模型结果。
    - 用 “passes” 暗示已证明超过两个涂鸦基线。
    - 用“每模型只测一次”“完全相同五折”“作者原配方”掩盖已登记差异。
    - 把 89.8% 与 15–25% 混合口径比较。
    - 把“多训这一次没可靠提升”写成普遍否定。
    - 把跨领域启发、局部检索未见写成已经成立的新贡献。
    - 把 18／22 日检查点写成最晚锁定／测试日。

    网址已存在的本机部署记录可支持“有项目网站”，但本次未联网，**不能核实邮件发送时线上是否已经包含今晚 fold2 和最新任务进度**。发送前应由负责会话核对线上实际内容。

**最该改的几处**

- 先改“89.8% 对 15–25%”：逐步平均与体积汇总混用，不能直接支撑训练状态差距的大小。
- 保留 46%／38%、6.8%、73.1% 的数字，但写清记账、体积分类和分母，不升级为已证明的空间因果链。
- 撤回新意收窄为“当前笔定位的分级局部撤回＋联合选择”；整层回退本来也只改变前后不同的体素。
- 开头明确 **flat 0.7694、factorised 0.7619、2S-ICR 单折 0.8000**；“passes”改为均值更高。
- 更新现场为 **268／407、7.6 GB、2S fold3 已开始、UAM Epoch 485／355**，加入第三折 VAL 和正确患者分母。
- 把 10-18／22 改为检查点；当前没有足够证据承诺到 0.79，更不能由 VAL 推定 TEST 必过 0.80。
- 43 篇表格可留作网站附件；邮件删篇数宣传和长文献名单，保留“98 页 working draft”及尚待补充的内容。