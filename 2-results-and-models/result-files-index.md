# 原始结果文件在哪

本文件夹里的分数都从下面这些原件算出或抄出。原件不复制到这里，路径都相对于代码树 `projects/petct_textual_intent/`。每个文件夹里有 `TRANSFER_VERIFICATION.json` 或 `SHA256SUMS`，记着收回本机时两边核过的 sha256（文件指纹）。

## 验证集结果和训练记录：`records/development_results_transfer/`

| 文件夹 | 是什么 |
|---|---|
| `eval-sirb-batch1-val-20260925/` | v1 两个 40k 模型的三画法完整 VAL、理想修复参照、不改对照和机制原件（第 01 阶段） |
| `eval-sirb-batch1-val-teaching-trajectories-20261003/` | 从上面那份挑出来、网站协议示例用的几条轨迹（含掩膜） |
| `eval-segbase-fivefold-val-repair-upper-20260930/` | 学习池 506 例起点上的理想修复参照 |
| `eval-sirb-v2-quickval-{N4_STATIC,N1_STATE_STATIC,N1_STATE_INDUCED,N3_ES,N1_STATE_SPATIAL}-R1-*/` | 五个 8k 续训的快速 VAL（第 02 阶段） |
| `eval-sirb-v2-list-N1_STATE_SPATIAL-R1-20261004/` | 空间支路的 101 片段机制清单 |
| `eval-sirb-v2-trainrollout-N1_STATE-20261003/` | v1 flat 在 TRAIN 上的五轮回放表（10-07 从分析文件夹的副本挪来当原件） |
| `eval-sirb-v3-intent-quickval-N1_STATE_INDUCED-R1-20261005/` | 起点模型加组 A 的快速 VAL（第 04 阶段） |
| `eval-sirb-v3-quickval-flip-N1_STATE_INDUCED-R1-20261005/` | 起点模型加左右翻转平均的快速 VAL |
| `eval-sirb-v3-quickval-weightavg-N1_STATE-STATIC-INDUCED-R1-20261005/` | 同父权重平均的快速 VAL |
| `eval-sirb-v3-quickval-{INTENT_FULL,INTENT_REFRESH,INTENT_WIDE}-R1-20261006/` | K1、K2、K3 网络单独的 VAL 和判定文件（`extra/` 里） |
| `eval-sirb-v3-quickval-flip-{INTENT_FULL,INTENT_REFRESH,INTENT_WIDE}-R1-20261006/` | K1、K2、K3 网络加翻转的 VAL 和判定文件 |
| `train-sirb-formal-20260930/` | v1 两个 40k 正式训练的清单和每 20 步日志 |
| `train-sirb-v2-continuations-20261005/` | 五个 8k 续训的训练记录 |
| `train-sirb-k-20261006/` | K1、K2、K3 的训练记录 |
| `baseline-2sicr-fold{0,1,2,3}-val-*/` | 2S-ICR 第 0 到 3 折各自的 VAL，逐例六状态和折回执 |
| `baseline-uam-fold{0,1}-val-20261005/` | UAM 第 0、1 折的 VAL |
| `train-2sicr-epochs-20261005/`、`train-uam-logs-20261005/`、`train-scribble-nnunet-*-fivefold-20261005/`、`train-segbase-nnunet-fivefold-20261005/` | 基线和分割基座的训练记录，网站训练曲线用 |

K4 的两次 VAL 出来后放 `eval-sirb-v3-quickval-INTENT_HARDNEG_REMOVE_PRESERVE-R1-*` 和对应的 `-flip-` 文件夹。

## 测试集结果：`records/eval_results_transfer/`

正本登记在 vault 的 petct-eval-results-register。

| 文件夹 | 是什么 |
|---|---|
| `eval-sirb-lockedtest-20260928-R1/` | v1 flat 和 N3 的锁定 TEST |
| `baseline-2sicr-fold0-test-R1/` | 2S-ICR 第 0 折单折 TEST |
| `PETCT-W21-OFFICIAL-TEST-FIVEFOLD-20260826-R2/` | 二值通道、距离图通道两个涂鸦基线的五折 TEST |
| `eval-editor3d-lockedtest-20260916-R2/` | 旧三维执行器的 TEST |
| `eval-segbase-perfold-lockedtest-20260907-R1/`、`segbase-m0v6-fivefold-test-20260816/` | 分割基座各折和五折的 TEST |
| `eval-lockedtest-repair-ceiling-20260904-R1/` | 旧协议真值参考（不是现行协议的上限） |

## 服务器上的运行目录

| 运行 | 机器和位置 |
|---|---|
| K1 `INTENT_FULL` | z390 `/mnt/HDD4/honor_petct/sirb/runs/PETCT-EDITOR-SIRB-INTENT_FULL-S3407-TRAIN-20261006-R1/` |
| K2 `INTENT_REFRESH` | 5090 `/share/rlia4081/honor_degree/sirb/runs/PETCT-EDITOR-SIRB-INTENT_REFRESH-S3407-TRAIN-20261006-R1/` |
| K3 `INTENT_WIDE` | A6000 `/mnt/HDD4/zlei0805/honor_degree/sirb/runs/PETCT-EDITOR-SIRB-INTENT_WIDE-S3407-TRAIN-20261006-R1/` |
| K4 `INTENT_HARDNEG_REMOVE_PRESERVE` | z390 `/mnt/HDD4/honor_petct/sirb/runs/PETCT-EDITOR-SIRB-INTENT_HARDNEG_REMOVE_PRESERVE-S3407-TRAIN-20261007-R1/` |
| K 系列 VAL 和判定文件 | 各自机器的 `<存储根>/sirb/eval/` |
| v1 和续训 | z390 `/mnt/HDD4/honor_petct/runs/editor-sirb-v2-mainline-20261001-R1/` 等，见 vault T083 |

每次运行的代码版本、配置、种子、机器、启动命令和运行目录，记在 vault T083 的运行登记里。

## 本文件夹里各阶段自带的证据

第 03 阶段的 `discussions/`、`scripts/`，第 05 阶段的 `discussions/`，第 06 阶段的 `analysis-scripts/`、`figures/`、`server-diagnostics/`、`discussions/`，第 07 阶段的 `server-diagnostics/`。服务器诊断拷回本机的结果在这里是唯一一份，没有别的原件。
