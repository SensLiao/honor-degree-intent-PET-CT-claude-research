"""Shared loaders for the A_* internal-evidence scripts (VAL only, CPU, read-only).

Patient mean (project rule): per (scan, style) Dice -> scan = mean over its styles -> patient = mean over its scans ->
patients equally weighted.  Only gt_positive scans enter Dice.
"""
import collections
import csv
import json
from pathlib import Path

REC = Path("C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/records")
DEV = REC / "development_results_transfer"
VAL1 = DEV / "eval-sirb-batch1-val-20260925"
ROLL = VAL1 / "rollout"
ARMS = {"flat": "N1_STATE-s3407", "N3": "N3-s3407", "oracle": "oracle", "noop": "noop"}
QUICK = {"flat8k": DEV / "eval-sirb-v2-quickval-N1_STATE_STATIC-R1-20261003" / "six_state.csv",
         "N3_8k": DEV / "eval-sirb-v2-quickval-N4_STATIC-R1-20261003" / "six_state.csv"}
STYLES = ("centerline", "random", "boundary")
SIZE_BINS = ((0.0, 0.5, "<0.5"), (0.5, 10.0, "0.5-10"), (10.0, float("inf"), ">=10"))


def size_bin(ml):
    for lo, hi, name in SIZE_BINS:
        if lo <= ml < hi:
            return name
    raise ValueError(ml)


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def six_state(path):
    """(scan, style) -> dict(round -> row with floats), plus patient and positivity maps."""
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    d = collections.defaultdict(dict)
    pat, pos = {}, {}
    for r in rows:
        k = (r["scan_id"], r["style"])
        if r["status"] != "ok":
            raise SystemExit(f"non-ok row {k} {r['round']} {r['status']}")
        rr = dict(r)
        for f in ("dice", "fp_ml", "fn_ml", "lesion_recall", "dmm"):
            v = r.get(f, "")
            rr[f] = float(v) if v not in ("", "nan", "None") else None
        d[k][int(r["round"])] = rr
        pat[k] = r["patient_id"]
        pos[k] = r["gt_positive"] == "True"
    return d, pat, pos


def arm_six(arm):
    return six_state(ROLL / ARMS[arm] / "six_state.csv")


def arm_transitions(arm):
    """(scan, style, transition) -> transition row."""
    return {(r["scan_id"], r["style"], int(r["transition"])): r
            for r in read_jsonl(ROLL / ARMS[arm] / "transitions.jsonl")}


def patient_mean(values_by_key, pat, keys=None):
    """values_by_key: (scan, style) -> float.  Mean over styles per scan, scans per patient, then patients equally.
    Returns (overall mean, {patient: value})."""
    by_scan = collections.defaultdict(list)
    for k, v in values_by_key.items():
        if keys is not None and k not in keys:
            continue
        by_scan[k[0]].append((pat[k], v))
    by_pat = collections.defaultdict(list)
    for scan, items in by_scan.items():
        by_pat[items[0][0]].append(sum(v for _, v in items) / len(items))
    pm = {p: sum(vs) / len(vs) for p, vs in by_pat.items()}
    return sum(pm.values()) / len(pm), pm


def gt_ml(row):
    """GT volume from one six-state row: D = 2TP/(2TP+FP+FN) -> TP = D(FP+FN)/(2(1-D)); GT = TP + FN."""
    d, fp, fn = row["dice"], row["fp_ml"], row["fn_ml"]
    if d is None:
        return None
    if d >= 1.0 - 1e-12:
        return None  # perfect state, TP not identifiable from D alone (no such state observed so far)
    return d * (fp + fn) / (2.0 * (1.0 - d)) + fn


def dice(tp, fp, fn):
    den = 2.0 * tp + fp + fn
    return 2.0 * tp / den if den > 0 else None


def nauc(c):
    return sum((c[i] + c[i + 1]) / 2.0 for i in range(5)) / 5.0
