"""Q7 add-on: per-trajectory FP / FN balance from D0 to D5 (VAL, positive scans, three styles)."""
import json
from pathlib import Path

from A_common import arm_six, patient_mean

OUT = Path(__file__).with_suffix(".json")
res = {}
for arm in ("flat", "N3", "oracle"):
    d, pat, pos = arm_six(arm)
    keys = [k for k in d if pos[k]]
    dfp = sorted(d[k][5]["fp_ml"] - d[k][0]["fp_ml"] for k in keys)
    dfn = sorted(d[k][5]["fn_ml"] - d[k][0]["fn_ml"] for k in keys)
    rel_fp = {k: (d[k][5]["fp_ml"] - d[k][0]["fp_ml"]) for k in keys}
    res[arm] = {"trajectories": len(keys),
                "fp_more_at_d5": sum(1 for x in dfp if x > 1e-9), "fp_less_at_d5": sum(1 for x in dfp if x < -1e-9),
                "fn_more_at_d5": sum(1 for x in dfn if x > 1e-9), "fn_less_at_d5": sum(1 for x in dfn if x < -1e-9),
                "median_dfp_ml": dfp[len(dfp) // 2], "median_dfn_ml": dfn[len(dfn) // 2],
                "patient_mean_dfp_ml": patient_mean(rel_fp, pat)[0],
                "patient_median_fp0_ml": sorted(patient_mean({k: d[k][0]["fp_ml"] for k in keys}, pat)[1].values())[27],
                "patient_median_fp5_ml": sorted(patient_mean({k: d[k][5]["fp_ml"] for k in keys}, pat)[1].values())[27],
                "patient_median_fn0_ml": sorted(patient_mean({k: d[k][0]["fn_ml"] for k in keys}, pat)[1].values())[27],
                "patient_median_fn5_ml": sorted(patient_mean({k: d[k][5]["fn_ml"] for k in keys}, pat)[1].values())[27]}
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
for a, o in res.items():
    print(a, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in o.items()})
