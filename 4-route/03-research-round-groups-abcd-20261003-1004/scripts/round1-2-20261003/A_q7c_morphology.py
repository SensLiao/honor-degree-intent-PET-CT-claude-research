"""Q7 add-on: error-component morphology at D0 and D5 (VAL, positive scans, three styles) from morphology.jsonl.

sign '-' = FP components, '+' = FN components.  Reports component counts, the largest component's share of the
error volume and the volume held by components < 0.5 mL / >= 10 mL (from largest_component_fraction only the largest
one is known exactly, so the >=10 mL statement is limited to the largest component).
"""
import collections
import json
from pathlib import Path

from A_common import ROLL, ARMS, read_jsonl

OUT = Path(__file__).with_suffix(".json")
res = {}
for arm in ("flat", "oracle"):
    rows = [r for r in read_jsonl(ROLL / ARMS[arm] / "morphology.jsonl") if r.get("gt_positive")]
    by = collections.defaultdict(list)
    for r in rows:
        by[(int(r["round"]), r["sign"])].append(r)
    out = {}
    for (rnd, sign), rs in sorted(by.items()):
        if rnd not in (0, 5):
            continue
        vol = [float(r["error_volume_ml"] or 0) for r in rs]
        largest = [float(r["error_volume_ml"] or 0) * float(r["largest_component_fraction"] or 0) for r in rs]
        comps = sorted(int(r["component_count"] or 0) for r in rs)
        out[f"round{rnd} {'FP' if sign == '-' else 'FN'}"] = {
            "trajectories": len(rs), "total_error_ml": sum(vol),
            "share_in_largest_component": sum(largest) / sum(vol) if sum(vol) else None,
            "trajectories_with_largest_ge10ml": sum(1 for x in largest if x >= 10),
            "volume_in_largest_ge10ml_share": sum(x for x in largest if x >= 10) / sum(vol) if sum(vol) else None,
            "median_component_count": comps[len(comps) // 2], "p90_component_count": comps[int(len(comps) * 0.9)]}
    res[arm] = out
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
for a, o in res.items():
    for k, v in o.items():
        print(a, k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()})
