"""Shared readers for the A4 local-evidence scripts.  Read-only, CPU, seconds.

Patient mean (project rule): per (scan, style) value -> scan = mean over its styles -> patient = mean over its
scans -> patients equally weighted.  Only gt_positive scans enter Dice.
"""
import collections
import csv
import json
import random
from pathlib import Path

ROOT = Path("C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent")
REC = ROOT / "records"
DEV = REC / "development_results_transfer"
TST = REC / "eval_results_transfer"
VAL1 = DEV / "eval-sirb-batch1-val-20260925"
ROLL = VAL1 / "rollout"
ARMS = {"flat": "N1_STATE-s3407", "N3": "N3-s3407", "oracle": "oracle", "noop": "noop"}
QUICK = {
    "STATIC": DEV / "eval-sirb-v2-quickval-N1_STATE_STATIC-R1-20261003" / "six_state.csv",
    "INDUCED": DEV / "eval-sirb-v2-quickval-N1_STATE_INDUCED-R1-20261003" / "six_state.csv",
    "N4_STATIC": DEV / "eval-sirb-v2-quickval-N4_STATIC-R1-20261003" / "six_state.csv",
}
STYLES = ("centerline", "random", "boundary")


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def fnum(v):
    return float(v) if v not in ("", "nan", "None", None) else None


def six_state(path, keys=None):
    """(scan, style) -> {round: row}; patient map; positivity map."""
    d = collections.defaultdict(dict)
    pat, pos = {}, {}
    for r in csv.DictReader(open(path, newline="", encoding="utf-8")):
        k = (r["scan_id"], r["style"])
        if keys is not None and k not in keys:
            continue
        if r["status"] != "ok":
            raise SystemExit(f"non-ok row {k} {r['round']} {r['status']}")
        rr = dict(r)
        for f in ("dice", "fp_ml", "fn_ml", "lesion_recall", "dmm"):
            rr[f] = fnum(r.get(f, ""))
        d[k][int(r["round"])] = rr
        pat[k] = r["patient_id"]
        pos[k] = r["gt_positive"] == "True"
    return d, pat, pos


def patient_curves(d, pat, pos, field="dice"):
    """patient -> [v0..v5] (style mean within scan, scan mean within patient)."""
    by_scan = collections.defaultdict(list)
    for k, rounds in d.items():
        if not pos[k]:
            continue
        by_scan[k[0]].append((pat[k], [rounds[i][field] for i in range(6)]))
    by_pat = collections.defaultdict(list)
    for scan, items in by_scan.items():
        curve = [sum(c[i] for _, c in items) / len(items) for i in range(6)]
        by_pat[items[0][0]].append(curve)
    return {p: [sum(c[i] for c in cs) / len(cs) for i in range(6)] for p, cs in by_pat.items()}


def nauc(c):
    return sum((c[i] + c[i + 1]) / 2.0 for i in range(5)) / 5.0


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def quantile(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    pos = (len(xs) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def summary_stats(xs):
    xs = list(xs)
    return {"n": len(xs), "mean": mean(xs), "median": quantile(xs, 0.5), "q1": quantile(xs, 0.25),
            "q3": quantile(xs, 0.75), "min": min(xs), "max": max(xs)}


def paired_bootstrap(diffs_by_patient, samples=10000, seed=3407):
    """Patient-resampling bootstrap of the mean paired difference; returns (mean, lo, hi)."""
    pats = sorted(diffs_by_patient)
    rng = random.Random(seed)
    vals = [diffs_by_patient[p] for p in pats]
    n = len(vals)
    boots = []
    for _ in range(samples):
        s = 0.0
        for _ in range(n):
            s += vals[rng.randrange(n)]
        boots.append(s / n)
    boots.sort()
    return sum(vals) / n, boots[int(0.025 * samples)], boots[int(0.975 * samples) - 1]


def gt_ml(row):
    """GT volume from one six-state row: D = 2TP/(2TP+FP+FN) -> TP = D(FP+FN)/(2(1-D)); GT = TP + FN."""
    d, fp, fn = row["dice"], row["fp_ml"], row["fn_ml"]
    if d is None or d >= 1.0 - 1e-12:
        return None
    return d * (fp + fn) / (2.0 * (1.0 - d)) + fn


def short(pid):
    return pid.replace("psma_", "")[:8]


def dump(obj, path):
    Path(path).write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
