#!/bin/bash
# K shortfall diagnostics on z390 (Director 2026-10-07, Claude Code).  Waits until the K1 VAL chain queue on this card
# has finished (its last job's success record and queue.done), then runs jobs.txt of this folder one at a time with the
# production v3 queue (code-1006b, settings z390.env).  Stops without starting anything if the K1 queue failed.
set -u
R=/mnt/HDD4/honor_petct/sirb
Q=$R/queue-diag-1007
K1_LAST=$R/eval/v3-valgate-quickval-flip-INTENT_FULL-R1.done
echo "$(date -Is) waiting for $K1_LAST and $R/queue/queue.done" >> "$Q/waiter.state"
while true; do
  if [ -e "$K1_LAST" ] && [ -e "$R/queue/queue.done" ]; then break; fi
  if [ -e "$R/queue/queue.fail" ]; then echo "$(date -Is) STOP: K1 queue failed ($R/queue/queue.fail); diag not started" >> "$Q/waiter.state"; exit 1; fi
  sleep 120
done
echo "$(date -Is) K1 queue done; diag queue starts" >> "$Q/waiter.state"
cd "$R"
SIRB_ENV_FILE=$R/z390.env JOBS_FILE=$Q/jobs.txt QUEUE_DIR=$Q EVAL_ROOT=$R/eval BANK_ROOT=$R/banks QUEUE_MIN_FREE_DISK_GIB=5 \
  bash $R/code-1006b/code/scripts/orchestration/queue_editor_sirb_v3_intent.sh >> "$Q/console.log" 2>&1
echo "$(date -Is) diag queue exited rc=$?" >> "$Q/waiter.state"
