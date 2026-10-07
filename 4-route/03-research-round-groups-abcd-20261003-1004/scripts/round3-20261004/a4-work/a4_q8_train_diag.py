"""TRAIN-side diagnostics that exist locally (all TRAIN, none is a score):
  1. the two formal 40k runs' monitoring logs (metrics.jsonl, every 20 steps): last-5k-window means of the tile-level
     diagnostics, pair-type mix, state-loss supervision counts, memory, speed;
  2. the 407 TRAIN scans' out-of-fold start Dice and the ideal-repair reference on them (oracle, uses GT), next to VAL.
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import DEV, ROLL, ARMS, six_state, patient_curves, mean, nauc, summary_stats, dump

out = {}
for arm in ("N1_STATE", "N3"):
    base = DEV / "train-sirb-formal-20260930" / arm
    rows = [json.loads(l) for l in open(base / "metrics.jsonl", encoding="utf-8") if l.strip()]
    man = json.load(open(base / "run_manifest.json", encoding="utf-8"))
    steps = [r["exposure"]["optimizer_steps"] for r in rows]
    def window(lo, hi, key):
        vals = [r[key] for r, s in zip(rows, steps) if lo < s <= hi and r.get(key) is not None]
        return mean(vals)
    keys = ["diag_hard_dice_target", "diag_target_recall", "diag_error_gate_recall", "diag_binding_accuracy_in_error",
            "base_total", "base_error", "base_binding", "base_target_dice", "base_preserve", "state_change", "state_stable",
            "state_down_count", "pair_type_bridge", "pair_type_other_error", "pair_type_peripheral", "pair_fallback",
            "data_wait_fraction", "seconds_per_step", "peak_reserved_gb"]
    res = {"log_rows": len(rows), "last_step": steps[-1], "plan": man.get("plan"), "parameters": man.get("parameters"),
           "wall_hours": man.get("wall_hours_total"), "pools": man.get("pools")}
    res["windows"] = {f"{lo // 1000}k-{hi // 1000}k": {k: window(lo, hi, k) for k in keys}
                      for lo, hi in ((0, 5000), (15000, 20000), (30000, 35000), (35000, 40000))}
    # preserve false-edit rate on training tiles: edited preserve voxels / preserve voxels
    pe = [(r["diag_preserve_edit_voxels"], r["diag_preserve_voxels"]) for r, s in zip(rows, steps) if s > 35000]
    res["late_preserve_edit_fraction"] = sum(a for a, _ in pe) / sum(b for _, b in pe)
    tv = [r["diag_target_voxels"] for r, s in zip(rows, steps) if s > 35000]
    ov = [r["diag_other_voxels"] for r, s in zip(rows, steps) if s > 35000]
    pev = [r["diag_preserve_edit_voxels"] for r, s in zip(rows, steps) if s > 35000]
    res["late_mean_target_voxels_per_log"] = mean(tv)
    res["late_mean_preserve_edit_voxels_per_log"] = mean(pev)
    res["late_mean_other_voxels_per_log"] = mean(ov)
    out[arm] = res

# TRAIN start states and the ideal-repair reference on TRAIN (oracle) vs VAL
d, pat, pos = six_state(DEV / "eval-segbase-fivefold-val-repair-upper-20260930" / "server-originals" / "rollout-train" / "six_state.csv")
ct = patient_curves(d, pat, pos)
dv, patv, posv = six_state(ROLL / ARMS["oracle"] / "six_state.csv")
cv = patient_curves(dv, patv, posv)
out["oof_start_and_oracle"] = {
    "TRAIN": {"patients": len(ct), "positive_scans": len({k[0] for k in d if pos[k]}), "scans": len({k[0] for k in d}),
              "curve": [mean(c[i] for c in ct.values()) for i in range(6)], "nauc": mean(nauc(c) for c in ct.values()),
              "D0_dist": summary_stats(c[0] for c in ct.values())},
    "VAL": {"patients": len(cv), "positive_scans": len({k[0] for k in dv if posv[k]}), "scans": len({k[0] for k in dv}),
            "curve": [mean(c[i] for c in cv.values()) for i in range(6)], "nauc": mean(nauc(c) for c in cv.values()),
            "D0_dist": summary_stats(c[0] for c in cv.values())}}
# empty-GT share
out["empty_gt_scans"] = {"TRAIN": sum(1 for s in {k[0] for k in d} if not any(pos[k] for k in d if k[0] == s)),
                         "VAL": sum(1 for s in {k[0] for k in dv} if not any(posv[k] for k in dv if k[0] == s))}

dump(out, Path(__file__).with_suffix(".json"))
for arm in ("N1_STATE", "N3"):
    r = out[arm]
    print("==", arm, "rows", r["log_rows"], "last step", r["last_step"], "wall h", round(r["wall_hours"], 2), "params", r["parameters"])
    print("   plan", r["plan"])
    for w, v in r["windows"].items():
        print("  ", w, {k: (round(x, 4) if isinstance(x, float) else x) for k, x in v.items()})
    print("   late preserve-edit fraction", r["late_preserve_edit_fraction"], "target vox/log", round(r["late_mean_target_voxels_per_log"], 1),
          "preserve-edit vox/log", round(r["late_mean_preserve_edit_voxels_per_log"], 1))
for s, v in out["oof_start_and_oracle"].items():
    print(s, v["patients"], v["positive_scans"], v["scans"], " ".join(f"{x:.4f}" for x in v["curve"]), "nAUC", round(v["nauc"], 4),
          "D0 median", round(v["D0_dist"]["median"], 4))
print("empty GT scans", out["empty_gt_scans"])
