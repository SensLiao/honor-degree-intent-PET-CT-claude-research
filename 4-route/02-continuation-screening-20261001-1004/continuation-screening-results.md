# 续训筛选：五个 8k 续训的结果、机制读数和运行记录（10-01 到 10-04）

> 原样搬自 vault T083 的批次登记、各续训快速 VAL 小节和证据小节，加 10-05 计划第一部分里关于续训的一段，以及 T083 里 10-03、10-04 早上的运行记录。文中提到的 PLAN.md、experiment-schedule-gpus.md、local-data-models-results.md 第几部分，指 10-07 整理前的旧文件；那些部分现在在哪，见文件夹首页 README.md 的“旧位置对照”。

## 批次和结果（T083 原文）

### 批次登记

每个批次一行；逐项明细（命令、目录、指标）在代码树 `projects/petct_textual_intent/records/editor-sirb-v2-batches/registry.tsv`。

| 批次 | 内容 | 状态 | 结果 |
|---|---|---|---|
| N4_STATIC-R1 | N3续训对照，8k步 | 训练及快速VAL/机制完成 | 结果见下节；仅VAL筛选 |
| N1_STATE_STATIC-R1 | flat续训对照，8k步 | 训练、快速VAL和两机制完成 | VAL及机制结果见下文 |
| v2-trainrollout-N1_STATE / -N3 | 两模型TRAIN回放 | 两者407/407、0失败完成 | 原件均已核 |
| v2-induced-N3-N1_STATE | 共用诱导状态池 | 15:16:52完成 | 两模型TRAIN回放合成 |
| N1_STATE_INDUCED-R1 | flat＋诱导状态，8k步 | 训练、快速VAL和两机制完成 | 快速VAL D5 0.760569；10-04选为起点模型 |
| N3_ES-R1 | N3 error branch读笔划，8k步 | 训练、快速VAL和101机制完成 | 快速VAL D5 0.754361；N3线结束 |
| N1_STATE_SPATIAL-R1 | flat扩张卷积空间支路，8k步 | 训练、快速VAL和101机制完成 | 快速VAL D5 0.754808；未入选 |

10-03 17:3x按导演令（`D-2026-10-03-03`：flat一条线，N3只留N3_ES）删掉还没开始的N3_INDUCED（训练加三项评估）和N3_ES_SPATIAL（训练加两项评估）：z390排队清单34行→28行（删7行、加1行说明），只换清单文件，没碰正在跑的训练和队列进程；删前原件 `queue/jobs.txt.before-director-cut-20261003`（sha256 16391e51…），新清单sha256 aa8d5b7d…，本机 `records/editor-sirb-v2-batches/launch/jobs.txt` 同步为同一份，registry.tsv删两行。清单里现在没有END行，跑完N1_STATE_SPATIAL的评估后队列空等新任务。新计划（多agent加Codex调研）定下前不追加任务。

每个续训后接快速评估：99个VAL扫描、每例一种冻结画法五轮，加101片段单步机制清单；状态类候选加397个轨迹状态。

### N3续训对照快速VAL结果（10-02核验）

- 身份：N4_STATIC、seed3407、v1 N3 40k final续训8k；三份manifest均绑定同一final checkpoint（18aa9116…），partition=val。每扫描一种冻结画法、五轮交互，不是三画法最终VAL或TEST，不与不同画法结果直接比较。
- 99扫描/57患者，85阳性扫描/54患者进入Dice分母，99轨迹/594个六状态记录、0失败。先在患者内平均扫描，再对患者等权平均：D0–D5为0.609465、0.671966、0.694585、0.704837、0.721913、0.736012；D5−D0=0.126547，nAUC=0.693208。
- 101机制片段全部有目标区域Dice定义值，56患者，患者平均0.548943；397轨迹状态全部有定义值，53患者，患者平均0.455288。这两项是目标区域Dice，不是全卷D5。
- 原件：代码树 `records/server_status/heartbeat-3-20261002-0924/val-results/`（10-07 已清理），三运行目录的manifest和19份结果表，全部表SHA256与manifest一致。汇总 `metrics-summary.json`，核对 `transfer-checks.json`；远端原件在运行根 `eval/v2-quickval-N4_STATIC-R1`、`v2-list-N4_STATIC-R1`、`v2-traj-N4_STATIC-R1`。
- 可用于本轮VAL筛选描述；尚未对匹配同头参考执行完整判定，不能据此声称领先或通过候选条件。批次登记已更新，TEST结果表不登记此VAL。

### flat续训对照快速VAL结果（10-03核验）

- 身份：N1_STATE_STATIC、seed3407、v1 flat 40k final续训8k；manifest partition=val、99扫描、checkpoint_step 8000、0失败。每扫描一种冻结画法、五轮交互，与N3续训对照同一套口径，不是三画法最终VAL或TEST。
- 99扫描/57患者，85阳性扫描/54患者进入Dice分母。患者平均（先扫描后患者等权）D0–D5：0.6095、0.6985、0.7183、0.7414、0.7513、0.7602；D5−D0=0.1507，Dice nAUC 0.7189，病灶F1（第5轮）0.7781。扫描平均（85个阳性扫描等权）0.5974→0.7428，nAUC 0.7063，F1 0.7634。
- 与N3续训对照（N4_STATIC，上一节）同口径并排：患者平均D5 0.7360（N3）对0.7602（flat），nAUC 0.6932对0.7189，F1 0.7555对0.7781。两个续训对照各是自己那一头的参照，比较候选时只用同头的对照（PLAN.md第3.3节）；这个并排不是主线对照结论。快速VAL只有一种画法，也不与v1完整VAL（三种画法）直接比较。
- 原件：本机 `records/development_results_transfer/eval-sirb-v2-quickval-N1_STATE_STATIC-R1-20261003/`（`rollout_manifest.json`、`six_state.csv`，两个文件的sha256本机与服务器一致）；N3续训对照的同类副本在 `eval-sirb-v2-quickval-N4_STATIC-R1-20261003/`（与10-02那份逐字节相同）。收回工具 `scripts/reporting/collect_baseline_fold_val.py`。远端原件在运行根 `eval/v2-quickval-N1_STATE_STATIC-R1`。
- 网页：Results → Training & Validation → VAL里，两个续训对照是第二版模型两行（Continuation control · based on Main model / Flat 3-class control，v2-1、v2-2），状态由in progress改completed（训练和快速VAL完成），标“quick VAL · 一种冻结画法 · screening only”；10-03 01:00已随网页上线（见 [[petct-sirb-illustrated-course]]）。

flat续训对照新增机制结果（10-03 02:49核验）：101片段/56患者目标区域Dice0.610919，397轨迹状态/53患者0.552134，全部事件有定义值。两manifest同绑定b2c19b77…final checkpoint、partition=val；events SHA256与manifest一致。原件和汇总在代码树 `records/server_status/heartbeat-3-20261003-0247/val-results/`（10-07 已清理）。属于VAL机制诊断，不是全卷Dice或TEST。

### flat诱导状态候选首批VAL（10-03 23:56核验）

- 8000步21:38完成；快速VAL23:10:31完成99例/57患者，Dice85阳性例/54患者、0失败，594六状态行。一种冻结画法、患者等权D0..D5：0.609465、0.699238、0.727400、0.746023、0.759147、0.760569；nAUC0.723365。
- 对匹配flat续训对照D5 0.7602165885、nAUC0.7188665317：差+0.0003526817/+0.0044986699。按原10-01快速筛选整体条件未达到；只是该旧规则对照，不替新计划下结论，397机制仍63/397未齐。
- 101机制23:36完成，101定义值/56患者目标区域Dice0.608588（对照0.610919）。原件及events SHA与manifest一致，保存records/server_status/heartbeat-3-20261003-2353/val-results/；快速VAL按既有工具回传records/development_results_transfer/eval-sirb-v2-quickval-N1_STATE_INDUCED-R1-20261003，双端SHA核验通过，附metrics-summary及matched-control-summary。
- 本机Results已接sirb-v2-3新VAL，builder运行成功、无新推理/体素读取；线上本轮尚未更新。协作板注明本机Research map UI待导演审阅，不能把它随VAL整站发布；仅VAL数据发布待与当前批准线上版本合并，本轮不声称上线。

### flat诱导状态397机制收口（10-04 03:55 AEDT）

397状态评估03:02:48完成，397定义值/53患者，目标区域患者平均Dice0.5681492602；匹配flat续训对照0.5521337860，差+0.0160154742，小于原机制阈值+0.02。结合快速VAL D5差+0.0003526817、nAUC差+0.0044986699：原10-01整体和机制条件均未满足，不作为该旧规则下的合格组合项。新计划待定，不擅自改变既有队列。新manifest/events已回传，SHA与manifest一致，证据records/server_status/heartbeat-3-20261004-0354/val-results/v2-traj-N1_STATE_INDUCED-R1/。

队列03:02:48自动开始N3_ES训练，本轮2040/8000步，最近1.33秒/步，训练/队列活；3090 77°C、数据盘44GB、系统盘0。首候选全部完成，现队列14步完成/1运行/5排队（共20）。快速VAL网页状态仍按上一轮记录，本轮未发布网站。

### N3_ES快速VAL与机制结果（10-04 09:58 AEDT核验）

- 快速VAL08:49:39完成99例/57患者、0失败，Dice85阳性例/54患者，一种冻结画法。患者D0..D5：0.609465、0.684402、0.708991、0.719875、0.743620、0.754361；nAUC0.707760。
- 对同头N3续训对照：D5差+0.0183488595、nAUC差+0.0145523019。101机制09:33:37完成，101定义值/56患者，目标区域Dice0.5807686401（对照0.5489426568，差+0.0318259833）；原10-01整体及目标Dice机制条件均满足。但D5比flat诱导状态0.760569低0.0062085320，不能声称胜过flat，新计划待定。
- 快速VAL按既有工具回传 `records/development_results_transfer/eval-sirb-v2-quickval-N3_ES-R1-20261004/`，双端SHA一致；机制manifest/events和核验在 `records/server_status/heartbeat-3-20261004-0956/val-results/v2-list-N3_ES-R1/`（10-07 已清理）。本机Results已接sirb-v2-5，builder成功无新推理/体素读取；线上本轮尚未发布，待审UI不整站发布。
- 队列09:33:37自动接flat空间支路N1_STATE_SPATIAL，当前720/8000、1.52秒/步，训练/队列活；20步现17完成/1运行/2排队。3090 78°C、数据盘34GB、系统盘0；证据records/server_status/heartbeat-3-20261004-0956/。

### flat空间支路快速VAL与起点模型（10-04 15:28 AEDT核验）

- N1_STATE_SPATIAL（v1 flat 40k续训8k，加扩张卷积空间支路）8000步13:11:59训完，快速VAL 15:27:43完成，99例/57患者、Dice分母85阳性例/54患者、0失败，一种冻结画法。患者D0..D5：0.609465、0.696266、0.718980、0.737682、0.746302、0.754808；nAUC 0.716273。对同头静态对照N1_STATE_STATIC（D5 0.760217、nAUC 0.718867）：D5 −0.005409、nAUC −0.002593；比诱导状态版N1_STATE_INDUCED（0.760569、0.723365）低0.005761。验证集筛选，不是三画法VAL或TEST。
- 起点模型按D-2026-10-04-02的规则（D5最高且nAUC不低于当时最好者）由服务器空档链自动选定：N1_STATE_INDUCED。选定记录 `/mnt/HDD4/honor_petct/runs/ops-sirb-v3-slot-chain-r3-20261004/selection.json`，指标由six_state.csv重算并和已存汇总逐位核对。组B的N1_INTENT不加空间支路（登记表保持spatial_residual为none）。
- 原件已回传 `records/development_results_transfer/eval-sirb-v2-quickval-N1_STATE_SPATIAL-R1-20261004/`（manifest和六状态表，两端sha256一致）。101片段清单16:05:39完成：101定义值/56患者，目标区域Dice 0.610454，对静态对照0.610919差−0.000464（原件 `records/development_results_transfer/eval-sirb-v2-list-N1_STATE_SPATIAL-R1-20261004/`，三个文件两端sha256一致）。空间支路在快速VAL和机制清单上都没有收益。

## 续训在 TRAIN 和后几轮删笔上的读数（10-05 计划原文）

**已经试过、作用很小的（都是续训，10-05 晚起只作历史记录，不作证据）。** 10-05 晚新算的 TRAIN 回放（407 扫描，每扫描一种画法）：v1 flat 第五轮 Dice 0.5768→0.7758，诱导状态续训版 0.5768→0.7986；续训在 TRAIN 上涨 0.0228，在快速 VAL 上只涨 0.0044，多训的部分没有推广到 VAL。原配方多训 8k，快速 VAL D5 只多 +0.0041，区间跨 0。用模型自身失败状态续训，再多 +0.0004，nAUC 多 +0.0045。两个续训版都只改了第 2 到 4 轮，第 1 轮几乎没动（D1 差 +0.004）；后几轮删笔的平均收益从 v1 的 −0.0226 转成 +0.0015 和 +0.0103。所以组 A 用已完成的续训赢家作起点模型，删笔方向的空间要在它自己的状态上重测。均值转正不等于大的误删没了，新起点模型的回放里要另报负收益的笔数和总量，以及最坏的少数笔是不是仍落在纠错笔上。

## 当时的运行记录（T083 原文）

10-03 17:52–17:54 AEST实测：诱导状态池15:16完成，flat诱导状态候选N1_STATE_INDUCED续训到2180/8000步，最近约5.21秒/步，训练及队列存活；当前无候选VAL。D-2026-10-03-03已取代两头全跑计划，服务器清单从27删到20步，10步完成、1步运行、9步排队；N3_INDUCED和N3_ES_SPATIAL已从排队删除，N3仅保留N3_ES。原始证据records/server_status/heartbeat-3-20261003-1752/。

10-03 19:47–19:55 AEST（导演10-03晚令“直接把 worker 少一点……不要去测速了”，`D-2026-10-03-05`）：查明变慢主因是内存整理卡顿，不是磁盘。numpy 1.26.4 默认对大数组向内核申请透明大页，这台机器内存碎片化后每次申请都进直接整理且几乎都失败（compact_stall 3.49亿次、compact_fail 3.46亿次），内存“全部卡住”约46%的时间。改运行设置文件 `sirb-v2-launch-r2.env`：读数据进程8→6，加 `export NUMPY_MADVISE_HUGEPAGE=0`（备份同目录 `.before-workers6-nothp-20261003T194730`）；停训练（队列随之停，queue.fail 改名 `.operator-restart-workers6-20261003T194730`），用原命令重开 tmux 队列，N1_STATE_INDUCED从3000步存档续训（丢约300步）。每个训练样本的随机数按序号定，换进程数不改变数据和结果。续训后正常训练日志：每步5.7–6.5秒→1.6–2.2秒，等数据占比0.27–0.46→0.24，内存全卡住46%→0，预计约22:10训完。证据 `records/server_status/z390-loader-memory-fix-20261003.txt`；本机设置副本已同步（sha256 88db4585…）。

10-03 20:53–20:54 AEST新连接实测：原N1_STATE_INDUCED续训5900/8000步，实际命令--workers 6 --resume；最近1.25–1.35秒/步，数据等待占比约0.00015，训练/队列存活。19:48的旧STOP和已改名queue.fail是有记录的操作恢复，不是当前失败。3090 78°C/约14.9GiB、GPU95–100%（5次采样），数据盘52GB、系统盘0。本轮无候选VAL，证据records/server_status/heartbeat-3-20261003-2053/。

10-03 21:38:31 N1_STATE_INDUCED 训完 8000/8000（run_manifest 总用时 6.28 小时，含 19:47 前的慢速段），队列 21:38 自动接快速 VAL，22:03 到第 28/99 例；之后是 101 片段和 397 轨迹两项机制评估。state 目录里的 train.fail 是 19:47 操作停训（attempt 0）留下的，不是这次训练失败。

10-04 06:54 AEDT新连接核验：N3_ES训练8000/8000于06:09:44完成，自动接快速VAL，27/99病例、135条transition刚更新；评测未齐，不给整体成绩。主线队列活，3090约3.5GiB/59°C，数据盘39GB、系统盘0；20步队列15完成/1运行/4排队。最终计划等待导演审批的状态保留。证据records/server_status/heartbeat-3-20261004-0654/。

## 证据（T083 原文）

### 证据

- 部署回执：代码树 `records/verification/editor-sirb-v2-code-deploy-20261001-R1.json`（10-07 已清理）、`-R2.json`。
- 新组别测试：本机Python 3.10，退役旧计划脚本后重跑新组别、配置登记、推理回放、启动队列四个测试文件，296项通过、5项跳过（4项要Linux的真flock、真符号链接、GNU stat，1项是登记表自身不查）；2项失败是此前就有的（完整VAL脚本直接写数值精度名、一个10-01新加的2S-ICR辅助模块不在分流表），与本次改动无关。完整输出在代码树 `records/verification/editor-sirb-v2-tests-after-retirement-20261001.txt`（10-07 已清理）。服务器Python核对：新组别参数量N3_ES 6,650,938（多20,672）、空间支路多36,642，训练配方哈希仍为20d6da7d…，v1 checkpoint可作父模型。
- 完整VAL队列停止记录 `runs/eval-sirb-full-val-20260930-R1/queue.stopped-by-director-20261001.json`；12k原型checkpoint删除前清单 `records/verification/editor-sirb-pilot-12k-checkpoints-before-delete-20261001.txt`。
- 快速评估判定程序：代码树 `scripts/evaluation/gen_petct_eval_sirb_v2_quickval_verdict.py`，按PLAN.md第3.3节判候选对同头续训对照（主条件、各模块机制条件、组合、排序；远端几何未实现会拒绝），打印登记表要填的四格，登记表人工填。本机107项测试通过（含故意改坏程序的检查），输出 `records/verification/editor-sirb-v2-quickval-verdict-tests-20261001.txt`（10-07 已清理）；用第一批VAL已存结果试跑，101清单目标区域Dice 0.5319 / 0.6051、397状态0.4537 / 0.5511与登记值逐位相同。10-01 23:3x作为新文件放进R2代码目录（sha256 5fa4cb2b…），服务器上 `--help` 正常。
