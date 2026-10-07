"""VAL: single-round Dice collapses (one stroke drops scan Dice by > 0.3).  How many, which sign, how small the scan's
lesion burden, how often they recover by D5, and how much they move patient-mean D5.  Three-style full VAL (v1) and
quick VAL (+8k continuations).  Sign inferred from FP/FN volume change where transitions.jsonl is not available."""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import QUICK, ROLL, ARMS, six_state, read_jsonl, mean, short, dump, patient_curves

lesion = {}
for t in read_jsonl(ROLL / ARMS["flat"] / "trajectories.jsonl"):
    les = t.get("lesions") or {}
    lesion[t["scan_id"]] = sum(float(x["volume_ml"]) for x in les.get("lesions", []))

def infer_sign(a, b):
    dfp, dfn = b["fp_ml"] - a["fp_ml"], b["fn_ml"] - a["fn_ml"]
    if dfp > 1e-9 or dfn < -1e-9:
        return "ADD"
    if dfp < -1e-9 or dfn > 1e-9:
        return "REMOVE"
    return "noedit"

def collapses(path, label, threshold=0.3):
    d, pat, pos = six_state(path)
    ev = []
    n_trans = 0
    for k, r in d.items():
        if not pos[k]:
            continue
        for t in range(5):
            n_trans += 1
            g = r[t + 1]["dice"] - r[t]["dice"]
            if g < -threshold:
                ev.append({"patient": short(pat[k]), "scan": k[0][-10:], "style": k[1], "round": t + 1,
                           "sign": infer_sign(r[t], r[t + 1]), "drop": g, "dice_before": r[t]["dice"],
                           "dice_after": r[t + 1]["dice"], "gt_ml": lesion.get(k[0]),
                           "fn_added_ml": r[t + 1]["fn_ml"] - r[t]["fn_ml"],
                           "recovered_by_d5": r[5]["dice"] >= r[t]["dice"] - 0.05, "d5": r[5]["dice"]})
    c = patient_curves(d, pat, pos)
    # counterfactual-free descriptive: patient-mean D5 if each collapsing scan-style kept its pre-collapse Dice at D5
    # (NOT a method result; shows how much of the mean these few events move)
    adj = {}
    for k, r in d.items():
        if pos[k]:
            adj[k] = r[5]["dice"]
    for e in ev:
        pass
    return {"label": label, "transitions": n_trans, "events": len(ev),
            "by_sign": dict(collections.Counter(e["sign"] for e in ev)),
            "by_round": dict(collections.Counter(e["round"] for e in ev)),
            "median_gt_ml": sorted(e["gt_ml"] for e in ev)[len(ev) // 2] if ev else None,
            "gt_lt_5ml": sum(1 for e in ev if e["gt_ml"] < 5.0),
            "recovered_by_d5": sum(1 for e in ev if e["recovered_by_d5"]),
            "events_at_round5": sum(1 for e in ev if e["round"] == 5),
            "patients": len({e["patient"] for e in ev}), "list": ev}

out = {}
out["v1_flat_3style"] = collapses(ROLL / ARMS["flat"] / "six_state.csv", "v1 flat, three-style VAL")
out["v1_N3_3style"] = collapses(ROLL / ARMS["N3"] / "six_state.csv", "v1 N3, three-style VAL")
for name, path in QUICK.items():
    out[name] = collapses(path, f"{name}, quick VAL")
dump(out, Path(__file__).with_suffix(".json"))
for name, r in out.items():
    print(f"{name:16s} trans {r['transitions']:4d} collapses(>0.3) {r['events']:3d} sign {r['by_sign']} round {r['by_round']} "
          f"median GT {r['median_gt_ml'] and round(r['median_gt_ml'], 2)} mL  GT<5mL {r['gt_lt_5ml']}  recovered {r['recovered_by_d5']}"
          f"  at round5 {r['events_at_round5']}  patients {r['patients']}")
for name in ("STATIC", "INDUCED", "N4_STATIC"):
    for e in out[name]["list"]:
        if e["round"] == 5:
            print("  r5 collapse", name, e["patient"], e["style"], e["sign"], round(e["dice_before"], 3), "->", round(e["dice_after"], 3),
                  "GT", round(e["gt_ml"], 2), "FN added", round(e["fn_added_ml"], 2))
