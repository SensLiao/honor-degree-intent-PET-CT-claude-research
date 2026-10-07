"""Q3 add-on: where REMOVE damage happens (VAL, same-state trajectory states and the 101-episode list).

Field definition (scripts/common/petct_sirb_metrics.py preserve_damage_by_touched_component): for a REMOVE stroke the
'touched component' is the predicted-mask component the stroke touches; new error inside it is erosion of the true
lesion core of the very object the user pointed at, outside it is collateral change elsewhere.  ADD strokes touch no
predicted component, so their damage has no inside/outside split.
"""
import collections
import json
from pathlib import Path

from A_common import VAL1, read_jsonl, size_bin

OUT = Path(__file__).with_suffix(".json")
res = {}
for lst in ("samestate-trajectory", "samestate-list"):
    for arm in ("N1_STATE-s3407", "N3-s3407"):
        ev = [e for e in read_jsonl(VAL1 / lst / arm / "events.jsonl") if e.get("status") == "ok"]
        for source in ("all", "own"):
            if source == "own":
                if lst != "samestate-trajectory":
                    continue
                tag = ".trajbank-" + arm.split("-s3407")[0] + "-"
                rows = [e for e in ev if tag in e["episode_id"]]
            else:
                rows = ev
            rem = [e for e in rows if e["sign"] == "-"]
            touched = [e for e in rem if e.get("touched_predicted_components")]
            with_core = [e for e in touched if e.get("touched_component_has_preserve")]
            dmg = sum(float(e["new_error_ml"] or 0) for e in rem)
            inside = sum(float(e["new_error_inside_touched_component_ml"] or 0) for e in rem)
            outside = sum(float(e["new_error_outside_touched_component_ml"] or 0) for e in rem)
            by_core = collections.defaultdict(lambda: [0, 0.0, 0.0, 0.0])
            for e in touched:
                key = "touched component contains true lesion" if e.get("touched_component_has_preserve") else "touched component is pure FP"
                b = by_core[key]
                b[0] += 1
                b[1] += float(e["new_error_ml"] or 0)
                b[2] += float(e["target_recovery_ml"] or 0)
                b[3] += float(e["target_volume_ml"] or 0)
            add = [e for e in rows if e["sign"] == "+"]
            res[f"{lst} | {arm} | {source}"] = {
                "remove_events": len(rem), "remove_touching_a_predicted_component": len(touched),
                "remove_touched_component_contains_true_lesion": len(with_core),
                "remove_new_error_ml": dmg, "remove_new_error_inside_touched_ml": inside,
                "remove_new_error_outside_touched_ml": outside,
                "remove_inside_share": inside / dmg if dmg else None,
                "remove_by_component_type": {k: {"n": v[0], "new_error_ml": v[1], "target_recovered": v[2] / v[3] if v[3] else None,
                                                 "new_error_per_ml_target": v[1] / v[3] if v[3] else None}
                                             for k, v in by_core.items()},
                "add_events": len(add),
                "add_new_error_per_ml_target": sum(float(e["new_error_ml"] or 0) for e in add) / max(1e-9, sum(float(e["target_volume_ml"]) for e in add)),
                "remove_new_error_per_ml_target": dmg / max(1e-9, sum(float(e["target_volume_ml"]) for e in rem)),
            }
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
for k, v in res.items():
    print("=====", k)
    for kk, vv in v.items():
        print("   ", kk, vv if not isinstance(vv, float) else round(vv, 4))
