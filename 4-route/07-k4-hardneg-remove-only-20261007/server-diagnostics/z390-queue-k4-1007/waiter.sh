#!/bin/bash
# SIRB K4 on z390 (Director 2026-10-07 "开始执行", Claude Code).  Waits until the K-shortfall diagnostics queue on this
# card is done (its queue.done), then runs jobs.txt of this folder with the production v3 queue from code-1007
# (settings z390-k4.env: z390.env with SIRB_CODE -> code-1007).  Stops without starting anything if the diagnostics
# queue failed.
set -u
R=/mnt/HDD4/honor_petct/sirb
Q=$R/queue-k4-1007
D=$R/queue-diag-1007
echo "$(date -Is) waiting for $D/queue.done" >> "$Q/waiter.state"
while true; do
  if [ -e "$D/queue.done" ]; then break; fi
  if [ -e "$D/queue.fail" ]; then echo "$(date -Is) STOP: diagnostics queue failed ($D/queue.fail); K4 not started" >> "$Q/waiter.state"; exit 1; fi
  sleep 120
done
echo "$(date -Is) diagnostics done; K4 queue starts" >> "$Q/waiter.state"
cd "$R"
SIRB_ENV_FILE=$R/z390-k4.env JOBS_FILE=$Q/jobs.txt QUEUE_DIR=$Q EVAL_ROOT=$R/eval BANK_ROOT=$R/banks QUEUE_MIN_FREE_DISK_GIB=5 \
  bash $R/code-1007/code/scripts/orchestration/queue_editor_sirb_v3_intent.sh >> "$Q/console.log" 2>&1
echo "$(date -Is) K4 queue exited rc=$?" >> "$Q/waiter.state"
