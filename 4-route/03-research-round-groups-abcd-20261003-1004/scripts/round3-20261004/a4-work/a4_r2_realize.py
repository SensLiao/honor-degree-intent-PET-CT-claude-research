# -*- coding: utf-8 -*-
"""Verify A3's per-tag realisation (mean actual gain / mean same-state ideal gain) for flat rounds 2-5 (VAL)."""
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, "C:/Users/廖神/Desktop/Honor degree/projects/petct_textual_intent/protocols/"
                   "petct-sirb-v2-referent-scope-plan-20261003/research/scripts")
from A_transitions import build, TOL_ML  # noqa: E402

flat_rows, _, _ = build("flat")
o_rows, _, _ = build("oracle")
fk = {(r["scan"], r["style"], r["t"]): r for r in flat_rows}
o_by = collections.defaultdict(list)
for r in o_rows:
    if not r["no_stroke"]:
        o_by[(r["scan"], r["style"])].append((r["sign"], r["V"]))
acc = collections.defaultdict(lambda: [0, 0.0, 0.0])
for (scan, style, t), r in fk.items():
    if t == 0 or r["no_stroke"] or not r["pos"]:
        continue
    prev = fk[(scan, style, t - 1)]
    if any(s == r["sign"] and abs(v - r["V"]) < TOL_ML for s, v in o_by[(scan, style)]):
        tag = "original"
    elif (not prev["no_stroke"] and prev["sign"] == r["sign"] and prev["V"] - prev["R"] > TOL_ML
          and r["V"] <= prev["V"] - prev["R"] + TOL_ML):
        tag = "residue"
    elif not prev["no_stroke"] and prev["sign"] != r["sign"] and (prev["fp_add"] + prev["tp_lost"]) > TOL_ML:
        tag = "repair"
    else:
        tag = "other"
    a = acc[tag]
    a[0] += 1
    a[1] += r["gain_actual"]
    a[2] += r["gain_perfect"]
for tag, (n, g, p) in acc.items():
    print(f"{tag:9s} n={n:4d} mean actual {g / n:+.4f} mean ideal {p / n:+.4f} realisation {g / p:.3f}")
