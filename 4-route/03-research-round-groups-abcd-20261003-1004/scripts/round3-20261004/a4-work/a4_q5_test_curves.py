"""TEST (locked, 91 scans / 57 patients; Dice on 82 positive scans / 56 patients): per-round patient-mean curves of
every method with stored per-state files, and a paired SIRB flat vs 2S-ICR fold0 per-round comparison.
DESCRIPTIVE ONLY: reads already-archived result files; no model, no new TEST use, nothing here selects anything."""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import TST, six_state, mean, nauc, summary_stats, paired_bootstrap, read_jsonl, dump, short

SIRB = TST / "eval-sirb-lockedtest-20260928-R1" / "server-originals"
curves = {}     # method -> patient -> [D0..D5]
meta = {}

def from_six(path):
    d, pat, pos = six_state(path)
    by_pat = collections.defaultdict(list)
    styles = {}
    for k, r in d.items():
        styles[k[0]] = k[1]
        if pos[k]:
            by_pat[pat[k]].append([r[i]["dice"] for i in range(6)])
    return {p: [mean(c[i] for c in cs) for i in range(6)] for p, cs in by_pat.items()}, styles, len(d)

for name, arm, sub in (("SIRB flat", "N1_STATE-s3407", "rollout"), ("SIRB N3", "N3-s3407", "rollout"),
                       ("flat E08 second-largest", "N1_STATE-s3407", "unseen_policy-unseen_second_largest_3d_component"),
                       ("N3 E08 second-largest", "N3-s3407", "unseen_policy-unseen_second_largest_3d_component"),
                       ("flat E08 short-dot", "N1_STATE-s3407", "unseen_policy-unseen_short_dot_stroke"),
                       ("N3 E08 short-dot", "N3-s3407", "unseen_policy-unseen_short_dot_stroke")):
    c, styles, n = from_six(SIRB / arm / "segbase-fivefold-mean" / sub / "six_state.csv")
    curves[name] = c
    meta[name] = {"rows_scan_style": n}
    if name == "SIRB flat":
        sirb_styles = styles

def from_rows(rows, getter):
    by_pat = collections.defaultdict(list)
    for r in rows:
        st = getter(r)
        if st is None:
            continue
        by_pat[r["patient_id"]].append(st)
    return {p: [mean(c[i] for c in cs) for i in range(6)] for p, cs in by_pat.items()}

ev = json.load(open(TST / "baseline-2sicr-fold0-test-R1" / "evaluation.json", encoding="utf-8"))
def get2s(r):
    sts = sorted(r["states"], key=lambda s: s["state_index"])
    if not sts[0]["metric_eligible"]:
        return None
    return [s["dice"] for s in sts]
curves["2S-ICR fold0"] = from_rows(ev["rows"], get2s)
case_2s = {r["case_id"]: get2s(r) for r in ev["rows"]}

ed = json.load(open(TST / "eval-editor3d-lockedtest-20260916-R2" / "evaluation.json", encoding="utf-8"))
curves["old 3D editor (T019)"] = from_rows(ed["rows"], get2s)

w21 = json.load(open(TST / "PETCT-W21-OFFICIAL-TEST-FIVEFOLD-20260826-R2" / "server-originals" / "TWOARM_PERSTATE_TRAJECTORY.json", encoding="utf-8"))
for arm, label in (("binary", "scribble baseline binary"), ("edt", "scribble baseline EDT")):
    curves[label] = from_rows(w21[arm], lambda r: r["dice"] if r["metric_eligible"] else None)

rc = json.load(open(TST / "eval-lockedtest-repair-ceiling-20260904-R1" / "evaluation" / "repair-ceiling.json", encoding="utf-8"))
curves["repair ceiling (T052, majority-vote start)"] = from_rows(rc["cases"], lambda r: r["dice_states"] if r["metric_eligible"] else None)

out = {"curves": {}, "nauc": {}, "patients": {}}
for name, c in curves.items():
    out["curves"][name] = [mean(v[i] for v in c.values()) for i in range(6)]
    out["nauc"][name] = mean(nauc(v) for v in c.values())
    out["patients"][name] = len(c)

# paired SIRB flat vs 2S-ICR fold0 per round
a, b = curves["SIRB flat"], curves["2S-ICR fold0"]
pats = sorted(set(a) & set(b))
pair = {"patients": len(pats)}
for i in range(6):
    dd = {p: a[p][i] - b[p][i] for p in pats}
    m, lo, hi = paired_bootstrap(dd)
    vals = list(dd.values())
    pair[f"D{i}"] = {"mean": m, "ci": [lo, hi], "sirb_higher": sum(v > 1e-9 for v in vals),
                     "2sicr_higher": sum(v < -1e-9 for v in vals)}
inc = {}
for i in range(1, 6):
    inc[f"round{i}"] = {"SIRB flat": mean(a[p][i] - a[p][i - 1] for p in pats),
                        "2S-ICR fold0": mean(b[p][i] - b[p][i - 1] for p in pats),
                        "SIRB N3": mean(curves["SIRB N3"][p][i] - curves["SIRB N3"][p][i - 1] for p in pats)}
pair["per_round_increment"] = inc
pair["gain_D5_minus_D0"] = {"SIRB flat": mean(a[p][5] - a[p][0] for p in pats),
                            "2S-ICR fold0": mean(b[p][5] - b[p][0] for p in pats)}
pair["gain_D5_minus_D1"] = {"SIRB flat": mean(a[p][5] - a[p][1] for p in pats),
                            "2S-ICR fold0": mean(b[p][5] - b[p][1] for p in pats)}
out["paired_flat_vs_2sicr"] = pair

# same comparison by the frozen per-scan style (both methods use the same assignment)
by_style = collections.defaultdict(lambda: collections.defaultdict(list))
d, pat, pos = six_state(SIRB / "N1_STATE-s3407" / "segbase-fivefold-mean" / "rollout" / "six_state.csv")
for k, r in d.items():
    if not pos[k]:
        continue
    s2 = case_2s.get(k[0])
    if s2 is None:
        continue
    by_style[k[1]]["sirb"].append([r[i]["dice"] for i in range(6)])
    by_style[k[1]]["2s"].append(s2)
out["by_style_scan_mean"] = {st: {"scans": len(v["sirb"]),
                                  "SIRB flat D1/D5": [mean(c[1] for c in v["sirb"]), mean(c[5] for c in v["sirb"])],
                                  "2S-ICR D1/D5": [mean(c[1] for c in v["2s"]), mean(c[5] for c in v["2s"])]}
                             for st, v in by_style.items()}

# lesion burden strata (GT volume from the SIRB TEST trajectories)
les = {}
for t in read_jsonl(SIRB / "N1_STATE-s3407" / "segbase-fivefold-mean" / "rollout" / "trajectories.jsonl"):
    L = t.get("lesions") or {}
    les[t["scan_id"]] = sum(float(x["volume_ml"]) for x in L.get("lesions", []))
pat_gt = collections.defaultdict(list)
for k in d:
    if pos[k]:
        pat_gt[pat[k]].append(les[k[0]])
gtm = {p: mean(v) for p, v in pat_gt.items()}
strata = {"<5 mL": [p for p in pats if gtm[p] < 5], "5-200 mL": [p for p in pats if 5 <= gtm[p] < 200],
          ">=200 mL": [p for p in pats if gtm[p] >= 200]}
out["by_burden"] = {s: {"patients": len(ps), "SIRB flat D0/D1/D5": [mean(a[p][i] for p in ps) for i in (0, 1, 5)],
                        "2S-ICR D0/D1/D5": [mean(b[p][i] for p in ps) for i in (0, 1, 5)]} for s, ps in strata.items()}

dump(out, Path(__file__).with_suffix(".json"))
for name in out["curves"]:
    print(f"{name:44s} n={out['patients'][name]:2d}", " ".join(f"{x:.4f}" for x in out["curves"][name]), f"nAUC {out['nauc'][name]:.4f}")
print("paired flat - 2S-ICR, patients", pair["patients"])
for i in range(6):
    p = pair[f"D{i}"]
    print(f"  D{i} diff {p['mean']:+.4f} CI [{p['ci'][0]:+.4f}, {p['ci'][1]:+.4f}]  SIRB higher {p['sirb_higher']}  2S higher {p['2sicr_higher']}")
for r, v in inc.items():
    print("  increment", r, {k: round(x, 4) for k, x in v.items()})
print("  gains", {k: round(v, 4) for k, v in pair["gain_D5_minus_D0"].items()}, "D5-D1", {k: round(v, 4) for k, v in pair["gain_D5_minus_D1"].items()})
for st, v in out["by_style_scan_mean"].items():
    print("  style", st, v["scans"], [round(x, 4) for x in v["SIRB flat D1/D5"]], [round(x, 4) for x in v["2S-ICR D1/D5"]])
for s, v in out["by_burden"].items():
    print("  burden", s, v["patients"], [round(x, 4) for x in v["SIRB flat D0/D1/D5"]], [round(x, 4) for x in v["2S-ICR D0/D1/D5"]])
