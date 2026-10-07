"""E_ one-off (read-only): learned binding against the connected-component rule on the SAME N3 error map (VAL).

Reads events.jsonl of samestate-list/N3-s3407 and samestate-list/N3-s3407-rulecc (and the trajectory set) from the
local copy of the 2026-09-25 batch-1 VAL evaluation.  Patient-weighted means of the target-region Dice, recall,
new-error mL and other-error mL at the frozen operating point.  Single step, VAL only.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records/development_results_transfer/"
            r"eval-sirb-batch1-val-20260925")
KEYS = ("intent_dice", "target_recall", "target_precision", "new_error_ml", "other_repaired_ml", "zero_recovery")


def load(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def patient_mean(rows, key):
    groups = defaultdict(list)
    for row in rows:
        value = row.get(key)
        if value is not None:
            groups[row["patient_id"]].append(float(value))
    means = [sum(v) / len(v) for v in groups.values()]
    return sum(means) / len(means) if means else float("nan")


def main() -> None:
    for subset in ("samestate-list", "samestate-trajectory"):
        for model in ("N1_STATE-s3407", "N3-s3407", "N3-s3407-rulecc"):
            path = ROOT / subset / model / "events.jsonl"
            if not path.is_file():
                print("missing", path)
                continue
            rows = load(path)
            print(f"{subset:21s} {model:16s} n={len(rows):4d} " +
                  " ".join(f"{k}={patient_mean(rows, k):.4f}" for k in KEYS))
        print("keys of one event:", sorted(load(ROOT / subset / "N3-s3407" / "events.jsonl")[0])[:60])


if __name__ == "__main__":
    sys.exit(main())
