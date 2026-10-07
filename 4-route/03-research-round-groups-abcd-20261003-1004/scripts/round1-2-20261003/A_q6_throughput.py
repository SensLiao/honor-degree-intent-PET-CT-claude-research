"""Q6: v1 training throughput from the formal 40k runs' metrics.jsonl (one row per 20-step log block).

seconds_per_step and data_wait_fraction are per-block values as logged; summaries: median, IQR, mean, p90 per 5k-step
phase and overall; the time-weighted data-wait share = sum(data_wait_seconds) / sum(seconds_per_step * steps).
"""
import json
from pathlib import Path

import numpy as np

from A_common import DEV

OUT = Path(__file__).with_suffix(".json")
res = {}
for arm in ("N1_STATE", "N3"):
    base = DEV / "train-sirb-formal-20260930" / arm
    rows = [json.loads(l) for l in open(base / "metrics.jsonl", encoding="utf-8") if l.strip()]
    man = json.loads((base / "run_manifest.json").read_text(encoding="utf-8"))
    att = man.get("attempts") or []
    steps = np.array([r["step"] for r in rows], float)
    sps = np.array([r["seconds_per_step"] for r in rows], float)
    dwf = np.array([r["data_wait_fraction"] for r in rows], float)
    dws = np.array([r.get("data_wait_seconds", np.nan) for r in rows], float)
    nst = np.array([r.get("steps", 20.0) for r in rows], float)

    def summ(x):
        return {"median": float(np.median(x)), "q25": float(np.quantile(x, 0.25)), "q75": float(np.quantile(x, 0.75)),
                "mean": float(np.mean(x)), "p90": float(np.quantile(x, 0.9)), "max": float(np.max(x))}
    out = {"blocks": len(rows), "last_step": int(steps.max()), "attempts_seen": sorted({r.get("attempt") for r in rows}),
           "seconds_per_step": summ(sps), "data_wait_fraction": summ(dwf),
           "time_weighted_data_wait_share": float(np.nansum(dws) / np.sum(sps * nst)),
           "sum_step_seconds_hours": float(np.sum(sps * nst) / 3600.0),
           "share_blocks_data_wait_gt_0.3": float(np.mean(dwf > 0.3)),
           "share_blocks_data_wait_lt_0.01": float(np.mean(dwf < 0.01)),
           "peak_reserved_gb_max": float(max(r.get("peak_reserved_gb", 0) for r in rows)),
           "manifest_wall_hours": man.get("wall_hours_total"), "manifest_workers":
               [a.get("loader", {}).get("num_workers") for a in att] if att else None}
    phases = {}
    for lo in range(0, 40000, 5000):
        m = (steps > lo) & (steps <= lo + 5000)
        phases[f"({lo},{lo + 5000}]"] = {"sps": summ(sps[m]), "dwf": summ(dwf[m]),
                                         "time_weighted_dw": float(np.nansum(dws[m]) / np.sum(sps[m] * nst[m]))}
    out["phases"] = phases
    # correlation: how much of the step time variation is data wait
    out["corr_sps_dwf"] = float(np.corrcoef(sps, dwf)[0, 1])
    # step time with data wait removed (compute-only estimate)
    comp = sps * (1 - dwf)
    out["compute_only_seconds_per_step"] = summ(comp)
    res[arm] = out
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
for arm, o in res.items():
    print("=====", arm, {k: o[k] for k in ("blocks", "last_step", "attempts_seen", "manifest_wall_hours", "manifest_workers",
                                         "sum_step_seconds_hours", "peak_reserved_gb_max")})
    print("  sps", {k: round(v, 3) for k, v in o["seconds_per_step"].items()})
    print("  dwf", {k: round(v, 3) for k, v in o["data_wait_fraction"].items()}, "time-weighted", round(o["time_weighted_data_wait_share"], 3),
          ">0.3:", round(o["share_blocks_data_wait_gt_0.3"], 3), "<0.01:", round(o["share_blocks_data_wait_lt_0.01"], 3))
    print("  compute-only sps", {k: round(v, 3) for k, v in o["compute_only_seconds_per_step"].items()}, "corr", round(o["corr_sps_dwf"], 3))
    for ph, x in o["phases"].items():
        print(f"   {ph:14s} sps med {x['sps']['median']:.3f} IQR [{x['sps']['q25']:.3f},{x['sps']['q75']:.3f}] mean {x['sps']['mean']:.3f}"
              f" | dwf med {x['dwf']['median']:.3f} IQR [{x['dwf']['q25']:.3f},{x['dwf']['q75']:.3f}] tw {x['time_weighted_dw']:.3f}")
