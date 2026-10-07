#!/bin/bash
# Diagnostic D2 on the 5090 (K shortfall analysis 2026-10-07, Claude Code): per-term gradient influence on the target
# logits, 48 fixed TRAIN units, measure only.  Shares the card with the 2S-ICR fold-4 training (GPU 3.8 of 32.6 GB in
# use when started); the z390 run of the same job could not fit beside the K4 training (out of memory).
R=/share/rlia4081/honor_degree
D=$R/sirb/diag
C=$D/checkpoints
cd $R/sirb/code-1006c/code
echo "$(date -Is) D2 starts" >> $D/d2-5090.state
env CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 NUMPY_MADVISE_HUGEPAGE=0 TMPDIR=$R/.t/d2tmp \
  PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  $R/envs/editor-sirb-rtx5090-py310/bin/python -B -u scripts/evaluation/gen_petct_eval_sirb_term_gradient_influence.py \
  --network=v1c=N1_STATE:3407:$C/v1flat-final.pt:contract \
  --network=K1=INTENT_FULL:3407:$C/k1-final.pt:mult=dice_gain=0.46292146252998073 \
  --network=K1s5k=INTENT_FULL:3407:$C/k1-step5000.pt:mult=dice_gain=0.46292146252998073 \
  --network=K2=INTENT_REFRESH:3407:$R/sirb/runs/PETCT-EDITOR-SIRB-INTENT_REFRESH-S3407-TRAIN-20261006-R1/checkpoints/final.pt:mult=dice_gain=0.5925754145773268 \
  --pair-manifest=$R/runs/editor-sirb-mainline-20260920-R1/episodes/pairs.jsonl \
  --manifest-root=$R/runs/editor-sirb-mainline-20260920-R1/episodes \
  --inputs-root=$R/runs/dataset-sirb-cases-gen-20260919-R2/cache/inputs \
  --labels-root=$R/runs/dataset-sirb-cases-gen-20260919-R2/cache/labels \
  --output=$D/d2-term-gradient-influence-train48.jsonl --units=48 --device=cuda:0 >> $D/d2-5090.log 2>&1
echo "$(date -Is) D2 exited rc=$?" >> $D/d2-5090.state
