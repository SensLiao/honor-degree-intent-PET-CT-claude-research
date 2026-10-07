#!/bin/bash
# Sign-threshold diagnostic T1 on the 5090 (K shortfall analysis, Director 2026-10-07 "开始执行", Claude Code):
# K1 final -> round-1 score histograms on TRAIN -> one add and one remove threshold learned on half of the TRAIN
# patients (the other half checks them; fit_petct_sirb_sign_thresholds.py) -> five-round quick VAL with the thresholds
# frozen (eval_petct_editor_sirb_sign_threshold_rollout.py) -> VAL gate.  No training, no TEST.  Shares the card with
# the 2S-ICR fold-4 training (3.8 of 32.6 GB in use at start).  Stops at the first failure; progress in $D/state.
set -u
R=/share/rlia4081/honor_degree
D=$R/sirb/diag/signthr-K1-1007
C=$R/sirb/diag/checkpoints
CODE=$R/sirb/code-1006c/code
PY=$R/envs/editor-sirb-rtx5090-py310/bin/python
IN=$R/runs/dataset-sirb-cases-gen-20260919-R2/cache/inputs
LB=$R/runs/dataset-sirb-cases-gen-20260919-R2/cache/labels
TR=$R/runs/editor-sirb-v2-mainline-20261001-R1/train-style-roster.json
VR=$R/runs/editor-sirb-v2-mainline-20261001-R1/val-style-roster.json
MIN_FREE_MIB=9000
mkdir -p "$D" "$R/.t/signthr"
cd "$CODE" || exit 2
export CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMPY_MADVISE_HUGEPAGE=0 TMPDIR=$R/.t/signthr \
  TMP=$R/.t/signthr TEMP=$R/.t/signthr PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True PYTHONDONTWRITEBYTECODE=1 \
  PYTHONNOUSERSITE=1
step() { echo "$(date -Is) $1" >> "$D/state"; }
need_gpu() {
  local free
  free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
  if [ "$free" -lt "$MIN_FREE_MIB" ]; then step "stop: GPU free ${free} MiB < ${MIN_FREE_MIB} before $1"; exit 3; fi
}
step "start"
need_gpu histograms
"$PY" -B -u scripts/evaluation/gen_petct_eval_sirb_round1_score_histograms.py \
  --network=K1=INTENT_FULL:3407:$C/k1-final.pt --inputs-root=$IN --labels-root=$LB --partition=train \
  --style-roster=$TR --output=$D/train-round1-hist.jsonl --numerics=fp32_tf32 --tile-batch=2 --device=cuda:0 \
  >> "$D/log.txt" 2>&1 || { step "stop: histograms rc=$?"; exit 1; }
step "histograms done"
"$PY" -B scripts/evaluation/fit_petct_sirb_sign_thresholds.py --input=$D/train-round1-hist.jsonl \
  --output=$D/train-sign-thresholds.json >> "$D/log.txt" 2>&1 || { step "stop: fit rc=$?"; exit 1; }
step "fit done"
need_gpu rollout
"$PY" -B -u scripts/evaluation/eval_petct_editor_sirb_sign_threshold_rollout.py --model=checkpoint \
  --checkpoint=$C/k1-final.pt --arm=INTENT_FULL --seed=3407 --inputs-root=$IN --labels-root=$LB --partition=val \
  --output-dir=$D/quickval-signthr --style-policy=frozen_case_style --style-roster=$VR --numerics=fp32_tf32 \
  --tile-batch=2 --device=cuda:0 --thresholds-file=$D/train-sign-thresholds.json --thresholds-network=K1 \
  >> "$D/log.txt" 2>&1 || { step "stop: rollout rc=$?"; exit 1; }
step "rollout done"
"$PY" -B scripts/evaluation/gen_petct_eval_sirb_val_gate.py --rollout-dir=$D/quickval-signthr --inputs-root=$IN \
  --labels-root=$LB --style-roster=$VR --output=$D/quickval-signthr-valgate.json >> "$D/log.txt" 2>&1 \
  || { step "stop: val gate rc=$?"; exit 1; }
step "complete"
