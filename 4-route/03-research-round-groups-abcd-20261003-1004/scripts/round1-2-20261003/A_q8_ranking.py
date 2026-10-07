"""Ranking of failure modes for the flat model (VAL) from the JSON outputs of A_q1..A_q7 (run those first).

Estimates per failure mode, all in patient-mean D5 points (VAL three-style):
  first-order  = sum over the 5 rounds of the same-state shortfall share (upper side; A_q2/A_q3);
  central      = first-order x (actual D5 gap / total first-order), i.e. the actual gap shared out in proportion
                 (assumes the catch-up of later rounds is the same for every mode);
  cross-check  = independent D5-state estimates where available (persistent damage, A_q3/A_q7).
Distance rings at round 1 are differenced from the cumulative 15/30/60 mm values of A_q2.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent


def load(name):
    return json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))


q1, q2, q3, q7 = load("A_q1_gap_structure"), load("A_q2_categories"), load("A_q3_damage"), load("A_q7_other")
out = {}
for arm in ("flat", "N3"):
    gap = q1[f"gap_{arm}"]["per_round"][5]
    fo = q2[arm]["first_order_total"]
    f = gap / fo
    cats = q2[arm]["categories"]
    comp = q2[arm]["first_order_total_by_component"]
    dmg_add = sum(cats[c]["D5pts_damage"] for c in cats if c.startswith("ADD"))
    dmg_rem = sum(cats[c]["D5pts_damage"] for c in cats if c.startswith("REMOVE"))
    tgt = comp["target"]
    out[arm] = {"actual_gap": gap, "first_order_total": fo, "scale": f,
                "categories_central": {c: cats[c]["D5pts_first_order"] * f for c in cats if c != "ALL"},
                "categories_first_order": {c: cats[c]["D5pts_first_order"] for c in cats if c != "ALL"},
                "damage_first_order": comp["damage"], "damage_central": comp["damage"] * f,
                "damage_add_first_order": dmg_add, "damage_add_central": dmg_add * f,
                "damage_remove_first_order": dmg_rem, "damage_remove_central": dmg_rem * f,
                "target_first_order": tgt, "target_central": tgt * f,
                "collateral_central": comp["collateral"] * f}
    if arm == "flat":
        sh = q2["target_incompleteness_share_beyond_30mm"]
        lo, hi = min(sh.values()), max(sh.values())
        out[arm]["target_far30_central_range"] = [tgt * f * lo, tgt * f * hi]
        out[arm]["target_near30_central_range"] = [tgt * f * (1 - hi), tgt * f * (1 - lo)]
        out[arm]["target_far30_first_order_range"] = [tgt * lo, tgt * hi]
        out[arm]["target_near30_first_order_range"] = [tgt * (1 - hi), tgt * (1 - lo)]
    p = q3[arm]["persistent_d5"]
    bt = q3[arm]["persistent_by_type_event_ratio"]
    out[arm]["persistent_damage_D5_gain_range"] = [p["D5_without_persistent_damage_all_fp"] - p["D5"],
                                                   p["D5_without_persistent_damage_all_fn"] - p["D5"]]
    out[arm]["persistent_damage_D5_gain_event_ratio"] = p["D5_without_persistent_damage_event_ratio"] - p["D5"]
    out[arm]["persistent_fp_only_gain"] = [bt["D5_without_FP_damage_only"] - p["D5"], bt["D5_without_FP_damage_only_max_feasible"] - p["D5"]]
    out[arm]["persistent_fn_only_gain"] = [bt["D5_without_FN_damage_only"] - p["D5"], bt["D5_without_FN_damage_only_max_feasible"] - p["D5"]]
    b = q7[f"b_{arm}"]
    out[arm]["gap_shapley_damage_vs_unrepaired"] = {m: b[m] for m in ("max_fp", "max_fn", "event_ratio")}
# distance rings at round 1
rings = {}
for arm in ("flat", "N3"):
    t = q2["distance_t0"][arm]["table"]
    for key in ("all", "size >=10", "size 0.5-10"):
        a15, a30, a60 = t[f"{key} | 15 mm"], t[f"{key} | 30 mm"], t[f"{key} | 60 mm"]
        tot = a15["near_ml"] + a15["far_ml"]

        def rec(a):
            return a["near_recovered"] * a["near_ml"] if a["near_ml"] else 0.0

        def far_rec(a):
            return (a["far_recovered"] or 0.0) * a["far_ml"]
        r15, r30, r60 = rec(a15), rec(a30), rec(a60)
        rings[f"{arm} | {key}"] = {
            "<15mm": (r15 / a15["near_ml"]) if a15["near_ml"] else None,
            "15-30mm": ((r30 - r15) / (a30["near_ml"] - a15["near_ml"])) if a30["near_ml"] - a15["near_ml"] > 1e-9 else None,
            "30-60mm": ((r60 - r30) / (a60["near_ml"] - a30["near_ml"])) if a60["near_ml"] - a30["near_ml"] > 1e-9 else None,
            ">60mm": (far_rec(a60) / a60["far_ml"]) if a60["far_ml"] else None,
            "volume_share": {"<15mm": a15["near_ml"] / tot, "15-30mm": (a30["near_ml"] - a15["near_ml"]) / tot,
                             "30-60mm": (a60["near_ml"] - a30["near_ml"]) / tot, ">60mm": a60["far_ml"] / tot}}
out["round1_distance_rings"] = rings
(HERE / "A_q8_ranking.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for arm in ("flat", "N3"):
    o = out[arm]
    print(f"===== {arm}: gap {o['actual_gap']:.4f} first-order total {o['first_order_total']:.4f} scale {o['scale']:.4f}")
    print("  damage FO {:.4f} central {:.4f} | ADD-leak FO {:.4f} central {:.4f} | REMOVE-overcut FO {:.4f} central {:.4f}".format(
        o["damage_first_order"], o["damage_central"], o["damage_add_first_order"], o["damage_add_central"],
        o["damage_remove_first_order"], o["damage_remove_central"]))
    print("  target FO {:.4f} central {:.4f} collateral central {:+.4f}".format(o["target_first_order"], o["target_central"], o["collateral_central"]))
    if arm == "flat":
        print("  target near30 central {} far30 central {} | FO near {} far {}".format(
            [round(x, 4) for x in o["target_near30_central_range"]], [round(x, 4) for x in o["target_far30_central_range"]],
            [round(x, 4) for x in o["target_near30_first_order_range"]], [round(x, 4) for x in o["target_far30_first_order_range"]]))
    print("  persistent damage D5 gain range", [round(x, 4) for x in o["persistent_damage_D5_gain_range"]], "event ratio",
          round(o["persistent_damage_D5_gain_event_ratio"], 4), "| FP-only", [round(x, 4) for x in o["persistent_fp_only_gain"]],
          "FN-only", [round(x, 4) for x in o["persistent_fn_only_gain"]])
    print("  gap Shapley damage vs unrepaired", {m: {k: round(v, 4) for k, v in x.items()} for m, x in o["gap_shapley_damage_vs_unrepaired"].items()})
    for c in sorted(o["categories_central"], key=lambda c: -o["categories_central"][c]):
        print(f"    {c:18s} central {o['categories_central'][c]:.4f}  first-order {o['categories_first_order'][c]:.4f}")
for k, v in rings.items():
    print("ring", k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "volume_share"},
          "vol share", {kk: round(vv, 3) for kk, vv in v["volume_share"].items()})
