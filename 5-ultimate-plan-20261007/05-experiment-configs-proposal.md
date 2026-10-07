# 05 实验配置草案：每个候选的配置字段含义与取值范围（第一版，10-07）

结论：本计划里的每个实验都应是一个新的配置文件（`configs/sirb/experiments/editor-sirb-<对象>-<动作>.json`），只加字段、不改代码；需要的新模块一律带开关，开关默认值等于 K4 的行为，这样旧配置逐位不变。下面只写字段的含义和允许的取值范围，不写具体数值的“推荐值”，凡是数值要么由网络学出（给初值和是否可学），要么按每例数据或模型自估量推出（写规则），要么是算力预算（写进配置并在论文的系数来源表里标明）。字段名用现有代码的风格（下划线小写，如 `hard_negative_signs`、`hard_negative_roles`，见 `4-route/07-*/k4-recipe-and-early-training.md`）。

> 现有的 K 系列配置字段（363 个，`4-route/06-*/analysis-scripts/stage2-20261007/c3_out.txt`）不动；本文件只列新增或要改的段。每段标注它属于“训练指纹”（改了就不能和旧 checkpoint 混）还是“科学指纹”（只影响推理）。

## 一、符号分治损失（S1 起全部配方都含）

| 字段 | 含义 | 取值范围 | 来源类型 |
|---|---|---|---|
| `hard_negative_signs` | 难负样本用在哪个方向 | `both` / `remove_only` / `none` | 结构开关；K4 为 `remove_only` |
| `hard_negative_roles` | 难负样本挑哪些角色 | `other_and_preserve` / `preserve_only` | 结构开关；K4 为 `preserve_only` |
| `hard_negative_onset_rule` | 何时开始计难负样本 | `always` / `after_gate_recall_quantile` | 规则：`after_gate_recall_quantile` 表示训练块上错误门召回的滑动均值超过同一次训练里自身历史分位数后才开始，分位数字段 `hard_negative_onset_quantile` 取 0.5 到 0.9（算力预算类，登记） |
| `dice_gain_loss_scale_mode` | 软 Dice 收益项（B1c）的倍率怎么定 | `calibrate_once_step1000`（K1 做法） / `learned_uncertainty` / `gradnorm_multipoint` | `learned_uncertainty` 为可学参数；`gradnorm_multipoint` 的量测步点与单元数见第三节 |
| `add_overshoot_penalty_mode` | 加笔误加背景的罚项 | `none` / `dice_account_weighted` | `dice_account_weighted` 的权重由当前状态的 D/S 与 (2−D)/S 之比给，无手定数 |
| `boundary_ranking_enabled` | 边界排序 B1a | `true` / `false` | 结构开关 |

训练指纹。

## 二、分数校正、D̂ 自估与门槛规则（S1 起）

| 字段 | 含义 | 取值范围 | 来源类型 |
|---|---|---|---|
| `logit_adjustment_mode` | 分数校正 | `none` / `prior_ratio_from_train_log` | 偏移 = log(自然占比 / 采样占比)，两个占比从训练日志的 `diag_*_voxels` 与 `sampled_*` 计数算，不手定 |
| `dice_estimate_head` | D̂ 自估头 | `none` / `soft_dice_self` / `regression_head` | `regression_head` 的标签是 TRAIN 回放状态上当前掩膜对真值的 Dice；只在 TRAIN 用真值 |
| `dice_estimate_head_width` | 回归头隐层宽度 | 16 到 64 | 容量类（不随数据集变） |
| `executor_threshold_mode` | 执行门槛怎么来 | `fixed_0.5`（K 系列） / `sign_rule_dhat`（加笔 D̂/2、删笔 1−D̂/2，对校准后的病灶概率） / `sign_two_level_train_median`（两档，由 TRAIN 上 D̂ 分布中位数给） / `gain_head`（见第四节） | 规则或学出；`fixed_0.5` 保留为对照 |
| `executor_probability_space` | 门槛作用在哪个概率上 | `pT` / `lesion_probability`（加笔：pT 作下界；删笔：1−pT 作上界） | 结构开关 |

`executor_*` 属科学指纹（只影响推理，评估入口可用 `--override-file` 换），其余属训练指纹。

## 三、损失权重可学与多点标定（S1 起）

| 字段 | 含义 | 取值范围 | 来源类型 |
|---|---|---|---|
| `loss_weighting_mode` | 多项损失怎么平衡 | `fixed`（现行） / `learned_uncertainty` / `gradnorm_multipoint` | — |
| `learned_uncertainty_init_from_fixed` | 可学权重初值取现行固定值 | `true` | 规则 |
| `learned_uncertainty_terms` | 哪些项参与可学加权 | 子集：{B1a, B1c, hard_negative, B5a, B5b, state_loss, preserve} | 结构开关；v1 继承的三项基础损失（error、binding、target_dice）可选不参与 |
| `gradnorm_steps` | 多点标定的步点 | 列表，如 [1000, 5000, 10000, 20000]（算力预算，登记） | 算力预算 |
| `gradnorm_units` | 每次标定用的训练单元数 | 32 到 128（B6 只用 4 个，倍率因此偏小） | 算力预算 |
| `effective_weight_logging` | 记录各项有效权重与梯度份额 | `true` | 日志 |

训练指纹。

## 四、范围候选与收益头（S2 起）

| 字段 | 含义 | 取值范围 | 来源类型 |
|---|---|---|---|
| `scope_candidates_source` | 候选从哪个场生成 | `error_field_levelsets`（S2） / `propagation_field_levelsets`（S3） | 结构开关 |
| `scope_candidate_levels_rule` | 嵌套范围的水平怎么取 | `persistence_merge_events`：只取“和笔相连的块与别的块合并”的水平，纯增长阶段按持续度取代表水平，去重 | 规则（数据给出） |
| `scope_candidates_per_family` | 每族最多候选数 K | 4 到 12 | 算力预算 |
| `continuation_candidates_enabled` | 续修候选（上一轮提案里未执行且与本笔相连的部分） | `true` / `false` | 结构开关 |
| `undo_candidates_enabled` | 撤回候选（只在上一轮实际写回的体素里反向取） | `true` / `false` | 结构开关 |
| `noop_candidate_enabled` | “不改” | `true` | 结构开关 |
| `gain_head_target` | 收益头回归目标 | `g_T`（去掉 O 部分后在整例上重算的 Dice 变化；穷举核过的公式） / `delta_dice_true` | 标签只在 TRAIN 用真值 |
| `gain_head_features` | 收益头输入 | 推理时可见的量：候选体积、候选内外 e 与 R 的分位、与笔和上一轮改动的重叠、符号、轮次、当前分割体积、D̂ | 结构开关（列表） |
| `gain_head_tiebreak` | 预测并列时的取舍 | `smaller_volume_first` | 规则 |
| `gain_head_training_states` | 收益头的训练样本来源 | `offline_and_teacher_pool` / `plus_joint_replay`（训完做一次 TRAIN 联合回放再重训收益头） | 结构开关 |
| `user_stroke_protection` | 不做与用户笔迹符号相反的改动 | `true` | 硬规则 |

训练指纹（收益头和候选在训练中学）；`executor_threshold_mode=gain_head` 时推理按收益头挑。

## 五、传播场 R（S3）

| 字段 | 含义 | 取值范围 | 来源类型 |
|---|---|---|---|
| `propagation_field_enabled` | 是否启用 | `true` / `false` | 结构开关 |
| `propagation_edge_inputs` | 边权读什么 | 子集：{PET 差, CT 差, 当前分割差, e 的几何均值, 学出的特征} | 结构开关 |
| `propagation_operator` | 传播算子 | `soft_minimax`（log-sum-exp 软最大的最小最大路径） / `random_walker_iterative` | 结构开关 |
| `propagation_softness_learnable` | 软最大的温度是否可学 | `true`（初值 1） | 学出 |
| `propagation_max_steps` | 步数上限 | 24 到 96（块边长） | 算力预算 |
| `propagation_fixed_point_tol` | 不动点提前停的容差 | 1e-4 到 1e-2 | 算力预算 |
| `propagation_resolution` | 在哪个分辨率上传播 | `full` / `half_then_upsample` | 算力预算 |
| `bridge_supervision_enabled` | 用断桥状态对直接监督边权“该断” | `true` / `false` | 结构开关 |
| `bridge_sample_share_rule` | 断桥样本在训练单元里的占比 | `natural`（回放里的自然频率） / `inverse_frequency_capped` | 规则 |
| `pT_composition` | pT 怎么由 e 和 R 合成 | `e_times_gate(R)`（门为可学 sigmoid） / `e_only`（对照） | 结构开关 |

训练指纹。

## 六、配对 B5（主张 B 的三臂）

| 字段 | 含义 | 取值范围 | 来源类型 |
|---|---|---|---|
| `pairing_mode` | 配对方式 | `correct`（换笔换目标、同目标换画法） / `independent`（同样本、不配对、各自普通监督） / `shuffled`（只打乱关系，保持每样本自己的 T/O/P） | 结构开关 |
| `pairing_consistency_weight_mode` | 同目标换画法一致项的权重 | `fixed` / `learned_uncertainty` | 学出或固定 |
| `pairing_target_matching_rule` | 换笔换目标时两个目标按大小和到笔距离配对 | `size_and_distance_matched` | 规则 |

训练指纹。

## 七、读连续状态（需导演批，第二批）

| 字段 | 含义 | 取值范围 | 来源类型 |
|---|---|---|---|
| `p0_input_mode` | 基座概率 p0 通道 | `zero`（现行） / `read` | 结构开关 |
| `previous_round_pT_input` | 上一轮 pT 图作输入 | `none` / `read` | 结构开关 |
| `continuous_input_dropout_rule` | 训练时随机丢弃这些通道 | `per_case_bernoulli`，概率由“部署时第 0 轮占五轮的 1/5”这类规则给，或可学 | 规则 |
| `completion_head_enabled` | 强档：所指区域整片重预测 | `true` / `false` | 结构开关 |
| `completion_writeback_constraint` | 整片重预测的写回限制 | `within_propagation_support_and_sign` | 硬规则 |

训练指纹。

## 八、训练状态与抽样（沿用 K4，列出可能改的）

| 字段 | 含义 | 取值范围 | 来源类型 |
|---|---|---|---|
| `teacher_state_pool_enabled` | 固定教师状态池 B4 | `true` / `false` | 结构开关 |
| `online_refresh_steps` | 在线刷新步点 | `[]`（不刷新） / 列表 | 算力预算；K2 一次比较无差，默认不刷新 |
| `tile_class_quota_rule` | 评价块类别配额 | `fixed_40_30_30`（现行） / `replay_frequency`（按 TRAIN 回放里各类块的自然占比） | 规则 |
| `negative_budget_rule` | O、P 负样本预算 | `fixed_4096` / `multiple_of_T_voxels`（倍数为中性常数 1） | 规则 |
| `far_tile_placement_rule` | 远端第二块 | `T_outside_first_tile_fraction`（按 T 在第一块外的体积占比决定是否放、从未覆盖部分均匀抽中心） | 规则 |

训练指纹。

## 九、推理与评测（科学指纹）

| 字段 | 含义 | 取值范围 |
|---|---|---|
| `tta_flip_lr` | 左右翻转平均 | `true` / `false`；翻转在 e、R 和候选分数上做 |
| `tta_apply_to` | 翻转平均作用于 | `logits` / `fields_and_gain` |
| `report_modes` | 同一 checkpoint 并排报 | 子集：{`fixed_0.5`, `sign_rule_dhat`, `gain_head`} |
| `mechanism_metrics` | 机制读数 | {换笔跟随, 换画法一致性, 断桥方向正确率, 按符号拆的五轮贡献, 第 1 轮按距离修回, 误删真病灶, 被整块删没的病灶数, “不改”占比, 同一笔连续被拒次数} |
| `unseen_policies` | 稳健性选笔 | {second_largest_3d, smallest, farthest_from_previous, short_dot} |

## 十、运行身份（每个配置都要带）

数据和标签版本、患者划分、起点分割来源、初始化方式（随机）、配方哈希、各开关、状态池哈希、候选生成器与硬规则版本、写回和机器人版本、种子、步数、读数据进程数、机器与 PyTorch 版本、执行方式、画法分配表哈希（`1-plan/experiment-schedule.md` 第六节）。改了会影响输出的任何一项就是新身份。

> 修订记录：第一版 10-07；字段名以工程师核对现有代码后为准，这里只定含义和范围。
