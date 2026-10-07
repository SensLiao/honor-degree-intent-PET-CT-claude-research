# -*- coding: utf-8 -*-
"""Quick-VAL 'damage monitor' with the A_q5 definition: per sign and round group, per patient the mean of that
patient's per-stroke Dice gains, then the mean over patients that have such strokes.  Sign inferred from the
six-state FP/FN volume change (validated 415/415 on v1).  VAL only."""
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from a4_common import QUICK, ROLL, ARMS, six_state, dump  # noqa: E402

roster = set(six_state(QUICK["STATIC"])[0])
tabs = {name: six_state(path) for name, path in QUICK.items()}
tabs["v1_flat"] = six_state(ROLL / ARMS["flat"] / "six_state.csv", keys=roster)
tabs["v1_N3"] = six_state(ROLL / ARMS["N3"] / "six_state.csv", keys=roster)
out = {}
for name, (d, pat, pos) in tabs.items():
    byp = collections.defaultdict(lambda: collections.defaultdict(list))
    for k, r in d.items():
        if not pos[k]:
            continue
        for t in range(5):
            a, b = r[t], r[t + 1]
            dfp, dfn = b["fp_ml"] - a["fp_ml"], b["fn_ml"] - a["fn_ml"]
            s = "+" if (dfp > 1e-9 or dfn < -1e-9) else ("-" if (dfp < -1e-9 or dfn > 1e-9) else None)
            if s is None:
                continue
            grp = "round1" if t == 0 else "rounds2to5"
            byp[f"{s} {grp}"][pat[k]].append(b["dice"] - a["dice"])
    out[name] = {g: {"strokes": sum(len(v) for v in pp.values()), "patients": len(pp),
                     "patient_mean_gain": sum(sum(v) / len(v) for v in pp.values()) / len(pp)}
                 for g, pp in byp.items()}
dump(out, HERE / "a4_r2_monitor.json")
for name, m in out.items():
    print(name, {g: round(v["patient_mean_gain"], 4) for g, v in sorted(m.items())},
          {g: v["strokes"] for g, v in sorted(m.items())})
