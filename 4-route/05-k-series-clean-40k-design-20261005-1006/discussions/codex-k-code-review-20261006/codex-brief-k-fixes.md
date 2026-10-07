# 第二轮（同一会话）：请核对你上一轮四条意见的修法（只读）

你上一轮列的四条问题已由两个 agent 修好、本机测过；导演要求只读复核。K1、K3 已用含第 2 条修法的代码开训，K2 用含全部四条修法的代码 01:54 开训（第一次刷新在第 10,000 步，约 6 到 10 小时后，所以刷新路径若还有问题，来得及在那之前改）。

请直接读现在的文件（代码树 `projects/petct_textual_intent/`），逐条判断修法是否到位、有没有引入新问题，结论先行，问题写清文件行号、触发条件、后果和最小改法：

1. 第 1 条（刷新回放有失败轨迹仍写完成记录）：`scripts/common/petct_sirb_refresh.py`（write_record 拒绝失败轨迹）、`scripts/evaluation/eval_petct_editor_sirb_rollout.py`（--refresh-request 模式有失败轨迹时退出码 3 并列出失败病例）、`scripts/orchestration/queue_editor_sirb_v3_intent.sh`（刷新步骤失败停队列）。测试 `tests/test_petct_sirb_refresh.py` 里新加的 7 个。
2. 第 2 条（B6 标定保留上一单元计算图）：`scripts/common/petct_sirb_training.py` 的 `unit_term_norms` / `representative_term_norms`；测试 `tests/test_petct_sirb_k_experiments.py::test_each_calibration_unit_is_freed_before_the_next_units_forward`。
3. 第 3 条（刷新时点之后续训缺记录静默退回旧池）：同一文件的 `check_refresh_states`；测试同文件里续训拒绝和接受的各组。
4. 第 4 条（全 TRAIN 名单完整性）：回放入口在挑半区之前要求名单和缓存里的 TRAIN 扫描完全一致；5090 上实测名单 407、缓存 407、两边差集为空。

说明文档：`docs/sirb-k-experiments-notes-20261006.md`、`docs/sirb-k2-refresh-notes-20261006.md`；测试记录：`records/verification/sirb-k-core-tests-20261006.txt`（第 6、7 节）、`records/verification/sirb-k2-refresh-tests-20261006.txt`（E、F 节）。
