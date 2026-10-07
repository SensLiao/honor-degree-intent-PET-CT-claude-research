"""E_ one-off (read-only): GPU-side (non-waiting) seconds per step = seconds_per_step x (1 - data_wait_fraction),
from every local training log (v1 formal 40k, 12k prototypes)."""
import json, statistics, sys
from pathlib import Path
LOGS = list(Path(r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/train-sirb-formal-20260930").glob("*/metrics.jsonl"))
LOGS += list(Path(r"C:/Users/廖神/Desktop/Honor degree/.tmp/z390-pull/protos").glob("*/metrics.jsonl"))
for path in LOGS:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    pairs = [(r["seconds_per_step"], r["data_wait_fraction"]) for r in rows
             if r.get("seconds_per_step") and r.get("data_wait_fraction") is not None]
    nonwait = [s * (1 - f) for s, f in pairs]
    workers = None
    manifest = path.parent / "run_manifest.json"
    if manifest.is_file():
        m = json.loads(manifest.read_text(encoding="utf-8"))
        workers = [a.get("loader", {}).get("num_workers") for a in m.get("attempts", [])]
    print(f"{path.parent.name[:44]:44s} s/step med={statistics.median(s for s, _ in pairs):.2f} "
          f"wait med={statistics.median(f for _, f in pairs):.2f} nonwait med={statistics.median(nonwait):.2f} "
          f"p10={sorted(nonwait)[len(nonwait)//10]:.2f} workers={workers}")
