"""Shared loaders for the stage-2 scripts (VAL only; read-only on the canonical result stores, see b0_paths).

Quick-VAL protocol: each of the 99 VAL scans runs its one frozen drawing style (the style K2's run used); systems that
ran all three styles (v1 batch-1) are restricted to that style.  Dice: patient mean of scan means over the 85 positive
scans / 54 patients, as in the registered tables.
"""
import collections
import csv
import json
import random

from b0_paths import RUNS


def jl(path):
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def read_six(path):
    out, patient = collections.defaultdict(dict), {}
    with open(path, newline="", encoding="utf-8") as handle:
        for r in csv.DictReader(handle):
            key, k = (r["scan_id"], r["style"]), int(r["round"])
            patient[r["scan_id"]] = r["patient_id"]
            row = out[key]
            row.setdefault("dice", [None] * 6)
            row.setdefault("fp_ml", [None] * 6)
            row.setdefault("fn_ml", [None] * 6)
            d = r["dice"]
            row["dice"][k] = float(d) if d not in ("", "None") else None
            for f in ("fp_ml", "fn_ml"):
                v = r.get(f, "")
                row[f][k] = float(v) if v not in ("", "None", None) else None
            row["pos"] = r["gt_positive"] == "True"
    return out, patient


_REF, PATIENT = read_six(RUNS["K2"] / "six_state.csv")
KEYS = set(_REF)
ASSIGNED = {s: st for (s, st) in KEYS}
POS = {s for (s, st), v in _REF.items() if v["pos"]}


def load(name, transitions=True, remote=True):
    folder = RUNS[name]
    six, patient = read_six(folder / "six_state.csv")
    PATIENT.update(patient)
    six = {k: v for k, v in six.items() if k in KEYS}
    tr, rem = {}, collections.defaultdict(dict)
    if transitions and (folder / "transitions.jsonl").exists():
        for r in jl(folder / "transitions.jsonl"):
            if (r["scan_id"], r["style"]) in KEYS:
                tr[(r["scan_id"], r["style"], r["transition"])] = r
    if remote and (folder / "remote.jsonl").exists():
        for r in jl(folder / "remote.jsonl"):
            if (r["scan_id"], r["style"]) in KEYS:
                rem[(r["scan_id"], r["style"], r["transition"])][r["radius_mm"]] = r
    return six, tr, rem


def patient_mean(values):
    """values: scan -> number.  Patient mean of scan means; returns (mean, n_patients)."""
    by = collections.defaultdict(list)
    for s, v in values.items():
        if v is not None:
            by[PATIENT[s]].append(v)
    means = [sum(v) / len(v) for v in by.values()]
    return (sum(means) / len(means) if means else float("nan")), len(means)


def per_patient(values):
    by = collections.defaultdict(list)
    for s, v in values.items():
        if v is not None:
            by[PATIENT[s]].append(v)
    return {p: sum(v) / len(v) for p, v in by.items()}


def paired_bootstrap(a, b, reps=10000, seed=3407):
    """a, b: scan -> value on the same scans.  Patient-level paired bootstrap of mean(a - b): (diff, lo, hi)."""
    pa, pb = per_patient(a), per_patient(b)
    common = sorted(set(pa) & set(pb))
    diffs = [pa[p] - pb[p] for p in common]
    rng = random.Random(seed)
    n = len(diffs)
    boots = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return sum(diffs) / n, boots[int(0.025 * reps)], boots[int(0.975 * reps) - 1], n


def dice_at(six, rnd, positive_only=True):
    return {s: v["dice"][rnd] for (s, st), v in six.items() if (s in POS or not positive_only)}
