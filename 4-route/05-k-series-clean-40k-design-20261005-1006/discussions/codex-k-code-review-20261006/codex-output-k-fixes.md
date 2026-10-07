**本轮复核通过：上一轮四条意见的修法均已到位，未发现由这些修改引入的新阻断问题。** 按你说明的部署版本，K1、K3 可以继续训练；K2 也没有需要为了这四项在第 10,000 步前补改代码的问题。这个结论针对当前本地代码和四处修法，服务器实际运行状态没有另行核实。

1. **第 1 条：失败轨迹不能再被当作刷新完成，修法到位。**

   [回放入口第 563 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/evaluation/eval_petct_editor_sirb_rollout.py:563>)现在会在 `--refresh-request` 模式下检查回放结果：发现失败轨迹就返回 **3**，输出失败数量、病例、画法和失败轮次。[完成记录第 424 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_refresh.py:424>)再次检查，因此即使前面的进程错误地返回了 0，也不能写刷新完成记录。

   两层检查共用的函数同时看回执中的失败数量和 `failures.jsonl`：**计数大于 0、或失败明细非空，任一成立都会拒绝。** 本轮内存检查确认了这两个方向，正常的“计数 0、明细空”仍被接受。

   [队列第 637 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/orchestration/queue_editor_sirb_v3_intent.sh:637>)在步骤返回非零时先写失败记录并退出，执行不到后面的 `.done` 写入，也不会接着续训。正常的退出码 3 路径重启后会重跑未完成回放。

   新增的[失败轨迹测试第 746 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/tests/test_petct_sirb_refresh.py:746>)确实调用真实回放入口，只在某病例第二轮注入模拟显存不足，验证“回放函数正常返回，但入口退出 3、完成记录拒绝”的情况。它覆盖了上一轮遗漏的触发条件。

2. **第 2 条：B6 相邻单元计算图重复保留，已消除。**

   [unit_term_norms 第 1001 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:1001>)把单个单元的设备张量、损失和计算图限制在一个函数调用内，返回值只有数值字典和浮点数；外层循环不再持有上一单元的损失对象。没有有效监督时直接返回 `None`，也会释放这些局部引用。

   我用与上一轮相同方式的小张量检查，调用当前生产标定循环，进入四次前向时仍存活的旧激活数量已从 **`[0, 1, 1, 1]` 变成 `[0, 0, 0, 0]`**。独立计算的倍率与生产函数结果在 `1e-6` 相对容差内一致，参数的 `.grad` 没有被标定过程累积。

   代表单元选择、梯度比值公式、其他项权重和第 1000 步的标定时点没有改变。[新增测试第 560 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/tests/test_petct_sirb_k_experiments.py:560>)也包装并调用了真实 `unit_loss()`，覆盖新、旧两种 B6 模式，并非用假的损失函数代替生产行为。正式 GPU 峰值显存仍未核实，但上一轮指出的引用问题已修复。

3. **第 3 条：刷新时点之后恢复时缺记录，现已拒绝；正常待刷新状态没有被误拒绝。**

   [check_refresh_states 第 937 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_training.py:937>)现在明确要求：**所有严格小于 checkpoint 步数的刷新时点，必须有完成记录和可读取的池；等于当前步数的刷新可以仍待完成。**

   这个边界处理正确。例如，第 10,000 步没有完成记录，可以重新请求第一次刷新；第 25,000 步已有第一次记录、尚无第二次记录，可以请求第二次刷新。第 11,000 步缺第一次记录，或第 26,000 步缺任一次记录，则拒绝恢复。

   本轮对生产检查函数做了内存验证：**8 组合法恢复被接受，6 组缺历史记录被拒绝**，其中包括“第 25,000 步连第一次记录也没有”的情况。现有测试还验证了记录存在但池目录丢失，以及真实训练入口中“删除旧记录后退出 2、还原记录后重新退出 76 请求刷新”的路径，见[第 765 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/tests/test_petct_sirb_k_experiments.py:765>)。未发现步数边界的新问题。

4. **第 4 条：全 TRAIN 名单与缓存的检查位置和比较方式正确。**

   [回放入口第 351 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/evaluation/eval_petct_editor_sirb_rollout.py:351>)在挑选患者半区之前调用完整名单检查；[检查函数第 183 行](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/scripts/common/petct_sirb_refresh.py:183>)比较的是两边的病例集合，不只是数量，并报告两个方向的差集。

   本轮内存检查确认：完整名单换顺序仍通过；误传半区名单被拒绝；缓存少一个病例也被拒绝。画法仍由完整 roster 生成后再选取半区，患者分半规则没有改变。检查仅加在刷新路径，普通回放原有的子集评估行为没有因此被改动。

   你提供的 5090 结果“名单 407、缓存 407、两边差集为空”满足当前检查条件；该服务器实测结果本轮没有独立复验。

测试证据也与修法相符：

| 记录 | 核对结果 |
|---|---|
| [训练侧记录第 6 节](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/sirb-k-core-tests-20261006.txt:1861>) | 新的计算图释放测试在修前失败；修后相关两文件 **59 passed**。恢复旧图驻留、保留设备张量的变异检查均变红。 |
| [训练侧记录第 7 节](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/sirb-k-core-tests-20261006.txt:2202>) | K 实验测试文件 **57 passed**；相关五文件回归 **201 passed**。删除缺记录检查、错误要求当前刷新也必须完成，都会被测试抓到。 |
| [刷新侧记录 E、F 节](<C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/verification/sirb-k2-refresh-tests-20261006.txt:954>) | 我逐项统计了 E 节，刷新测试文件 **63 项全部通过**。F 节删除入口失败处理、完成记录拒绝、完整名单检查等四项变异均变红。 |

这些 pytest 数字来自已有完整日志，本轮没有重新运行会写临时文件的 pytest；我独立执行的是上述不写文件的内存检查。较大的回归批次仍有失败记录，因此本次通过的范围是**这四处修法及其相关路径**，不扩展为整个项目的全部测试通过。