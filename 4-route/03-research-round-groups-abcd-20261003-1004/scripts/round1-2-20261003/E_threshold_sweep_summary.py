"""E_ one-off (read-only): executor-threshold sweep of the v1 models on VAL same-state sets.

Reads the E07 ``sweep.jsonl`` tables that the 2026-09-25 batch-1 VAL evaluation already wrote (local copy under
records/development_results_transfer/eval-sirb-batch1-val-20260925/).  Single-step numbers only (one stroke on a
frozen state), patient-weighted: per patient the mean over its events, then the mean over patients.  VAL only.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/"
            r"eval-sirb-batch1-val-20260925")
SETS = ("samestate-list", "samestate-trajectory")
MODELS = ("N1_STATE-s3407", "N3-s3407")


def patient_mean(rows, key):
    by_patient = defaultdict(list)
    for row in rows:
        value = row.get(key)
        if value is not None:
            by_patient[row["patient_id"]].append(float(value))
    means = [sum(v) / len(v) for v in by_patient.values() if v]
    return sum(means) / len(means) if means else None, len(means)


def main() -> None:
    for subset in SETS:
        for model in MODELS:
            path = ROOT / subset / model / "sweep.jsonl"
            if not path.is_file():
                print("missing", path)
                continue
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            by_threshold = defaultdict(list)
            for row in rows:
                by_threshold[round(float(row["threshold"]), 4)].append(row)
            print(f"== {subset} {model}: events per threshold {len(next(iter(by_threshold.values())))}")
            print("thr   intentDice  recall   newErr_mL  otherRep_mL  (patient-weighted; patients)")
            for threshold in sorted(by_threshold):
                group = by_threshold[threshold]
                dice, n = patient_mean(group, "intent_dice")
                recall, _ = patient_mean(group, "target_recall")
                harm, _ = patient_mean(group, "new_error_ml")
                other, _ = patient_mean(group, "other_repaired_ml")
                print(f"{threshold:<5} {dice:.4f}      {recall:.4f}   {harm:.3f}      {other:.3f}       {n}")


if __name__ == "__main__":
    sys.exit(main())
