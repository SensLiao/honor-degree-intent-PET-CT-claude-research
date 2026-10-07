**结论：这版不建议直接启动三条正式 40k。K2 有一处高优先级的结果可信度问题，以及两处恢复、名单检查缺口；三个实验共用的 B6 标定还有额外保留计算图的问题，建议一并修好再开训。** 从零初始化、40,000 步、state loss 预热和爬坡、K3 加宽的主要实现已核对正确。

本次全程只读本地文件，没有连服务器、读取凭据、修改文件或运行训练。下面列出的都是有具体触发条件的问题；实际服务器是否已满足触发条件，未核实。

1. **[P1，K2] 回放出现失败轨迹后，仍会把这次刷新标为完成并继续训练。**

   位置：[petct_sirb_refresh.py:397](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_refresh.py:397>)，第 397–407 行；对应回放分支在 [eval_petct_editor_sirb_rollout.py:403](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/evaluation/eval_petct_editor_sirb_rollout.py:403>)。

   **触发条件：** 半区回放中某例遇到显存不足、`RuntimeError`、`ValueError` 等，至少其他成功轨迹仍能生成配对。底层回放会记录 `failed_round`，后续状态缺失；开发集入口仍可正常退出。建池程序会利用成功前缀生成配对，完成记录只要求 `n_pairs > 0`，把 `failed_trajectories` 写入记录，却不据此拒绝完成。

   **后果：** 计划要求的“该半区每扫描完整五轮”没有完成，队列仍写完成文件、恢复训练。之后重启队列也会跳过这次刷新。失败病例偏多时，K2 实际学到的是偏向容易成功病例、较早轮次的状态分布。

   我用内存中的文件输入调用了真实 `write_record()`，只替换文件读写，确认 `failed_trajectories=1、n_pairs=1` 仍会请求发布 `refresh-10000.json`。这是完成判定的确认结果，未模拟服务器显存不足。

   **最小改法：** 刷新回放存在失败轨迹时返回非零，避免队列写 `rollout-<S>.done`；`write_record()` 同时拒绝失败轨迹，全部完成后才能生成刷新完成记录。测试需覆盖“回放函数返回了结果，但里面有失败轨迹”，现有仅模拟进程非零退出的队列测试抓不到这一种。

2. **[P2，K1/K2/K3] B6 标定开始下一个单元的前向计算时，上一单元的计算图仍被保留。**

   位置：[petct_sirb_training.py:1018](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:1018>)，以及同文件第 570 行的 `retain_graph=True`。

   **触发条件：** 第 1000 步进入标定，逐个处理代表单元。`term_gradient_norms()` 保留计算图，而循环中的 `_` 和 `loss` 没有释放；执行下一次 `_, loss = unit_loss(...)` 时，要先完成右边的前向计算，才能替换旧引用。

   **后果：** 相邻两个标定单元的计算图会短暂同时存在，提高这一阶段的显存峰值。在“一份计算图放得下、两份放不下”的状态下，普通训练步可以正常跑，第 1000 步却会失败。K1 的省显存开关并不消除这个引用问题。

   我用小型 CPU 张量替代前向损失，保持生产标定循环和梯度测量函数不变，观察到四次前向入口仍存活的旧激活数量为 **`[0, 1, 1, 1]`**。重复保留已确认；正式 96³ 输入下的峰值，以及 3090 是否必然显存不足，**未核实**。

   **最小改法：** 把单个单元的测量放进独立函数，只返回数值，让计算图在返回时释放；或者在每次循环末尾及跳过分支明确释放 `loss`、总损失和相关张量引用。无需改变标定公式或损失权重。

3. **[P2，K2] 从刷新时点之后的 checkpoint 恢复时，缺少刷新记录不会被拒绝，会静默退回旧池。**

   位置：[petct_sirb_training.py:934](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:934>)，第 934–942 行；重新请求刷新的判断在同文件第 882–884 行。

   **触发条件：** 例如恢复第 11,000 步的 checkpoint，但运行目录在恢复或迁移时漏了 `refresh-10000.json`，或整个 `refresh/` 目录没有带回来。`check_refresh_states()` 只比较“找到的记录”和“加载的池”是否一致；两边都是空列表也通过。重新请求刷新又只在步数**恰好等于** 10,000 或 25,000 时触发。

   **后果：** 已经使用过新池的 K2，会从第 11,000 步开始继续只抽旧池，优化步数和运行状态仍正常。第 26,000 步恢复时同样可能丢掉两次刷新，直到 40k 都不再请求。

   我直接调用生产检查函数确认：第 **11,000、26,000 步**在没有任何刷新记录时均被接受，且 `refresh_due=False`。

   **最小改法：** 根据计划检查所有**小于 checkpoint 步数**的刷新时点，要求其完成记录和池文件齐全；只允许“刷新时点等于当前 checkpoint 步数”处于待刷新状态。缺历史记录应明确拒绝，不能按空池继续。补第 11,000 步缺第一次记录、第 26,000 步缺任一次记录的恢复测试。

4. **[P2，K2] 没有核对全 TRAIN 名单的完整性，半区名单误用和缓存漏例都可能被接受。**

   位置：[eval_petct_editor_sirb_rollout.py:332](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/evaluation/eval_petct_editor_sirb_rollout.py:332>)，第 332–342 行；名单检查在 [petct_sirb_metrics.py:1154](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_metrics.py:1154>)。

   **触发条件：** 把当前半区名单误填为 `SIRB_TRAIN_STYLE_ROSTER`，或当前 TRAIN 缓存缺少若干病例。入口先从现有缓存筛半区；画法函数只检查“要跑的病例是否都在传入名单中”，没有确认该名单确实是完整 TRAIN，也没有确认应跑的半区病例全部在缓存中。

   **后果：** 半区名单会重新参与排序、分配画法，同一扫描可能与全 TRAIN 分配不同；缓存漏例则会缩小刷新病例范围，仍能生成完成记录。

   我用虚构的 24 扫描名单调用生产分配函数：只传其中 16 扫描的半区名单仍被接受，其中 **10 个扫描的画法改变**。这个数字仅用于验证代码行为，不是项目数据结果。

   **最小改法：** 在筛半区之前，对照已登记的全 TRAIN 名单检查 roster 和缓存覆盖；缺失、多余病例逐项报出。画法始终从完整名单生成，再选取半区。补“传入半区 roster”和“缓存缺一个应跑病例”的拒绝测试。

其余重点检查的结果如下：

| 检查项 | 本次核对结果 |
|---|---|
| 从零配方 | 三个实验均为 `continuation=False`、序列偏移 0、40,000 步、每步 2 个配对单元；AdamW `2e-4 / 1e-5`、学习率预热 1000 步、梯度裁剪 5；state loss 前 2000 步为 0，随后 2000 步升至 0.25。生产配置解析输出与要求一致，传入父 checkpoint 会被拒绝。 |
| B6 时点和倍率 | 在完成第 1000 次优化更新后、保存该步 checkpoint 前标定；使用确定序列中最先满足监督条件的 4 个单元，最多查 64 个。只替换 `dice_gain` 倍率，其余保持 1。标定前恢复继续等待；标定后恢复读回记录；K2 刷新恢复不重新标定。这些正常路径未发现错误。 |
| K2 正常刷新与续训 | 第 S 步先保存，再保留该步 checkpoint、写请求、退出 76；回放加载请求指定文件。恢复读回优化器，学习率按已完成步数计算，样本从 `S × 2` 开始。新池路径保留自己的根目录；外层离线库/状态池各半，状态池内新旧各半。问题集中在上面列出的异常和缺文件路径。 |
| K3 加宽和评估 | 正式宽度为 `40/72/144/288`，query 所读层的维度随之调整；训练和评估共用按 arm 构造网络的函数，checkpoint 记录宽度并严格加载权重。未发现评估退回原宽度的路径。 |
| 旧组别兼容 | 从所给 diff 还原后，旧组别登记内容的结构一致。对旧、新抽样函数做了 **18,000 组内存输入比较**，覆盖单池、双池、gap-weighted 及三个种子，抽到的行和日志一致。未用真实旧 checkpoint 和完整 TRAIN 数据重新跑训练。 |
| 省显存开关 | 开关确实传到主干重算路径。现有测试比较了 K1/K3 的损失、各项梯度和参数梯度，并比较 K3 整段小规模训练的最终权重；CPU 容差检查有通过记录。正式 GPU 数值差异和峰值显存未核实。 |

测试并非只跑替身。当前的 [test_petct_sirb_k_experiments.py:817](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/tests/test_petct_sirb_k_experiments.py:817>) 已补上“真实刷新回放入口 → 真实建池 → 完成记录 → 恢复训练”的交接测试；最新[训练侧日志](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/sirb-k-core-tests-20261006.txt:1786>)记录 **41 passed**，[刷新侧日志](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/sirb-k2-refresh-tests-20261006.txt>)记录 **56 passed**。删除生产标定、刷新停止、读取新池等调用后测试变红，也有已有记录。

不过，队列故障恢复测试仍使用替身训练、回放和建池进程；它们覆盖了非零退出，未覆盖第 1 条的“进程成功退出、内容实际不完整”。第 2–4 条也没有对应测试。全回归日志另有 **12 failed、1219 passed、6 skipped**；notes 将失败归为既有问题，本次没有重新运行会写文件的 pytest 来独立确认该归因。服务器上的固定教师池是否齐全、正 gap 是否存在、实际显存和磁盘余量，均留在本次只读本地复核的未核实范围。