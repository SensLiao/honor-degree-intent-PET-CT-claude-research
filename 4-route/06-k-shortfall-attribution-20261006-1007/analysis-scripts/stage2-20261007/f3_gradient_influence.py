"""Diagnostic D2 read-out: which loss term pushes the target score of the pointed error T up or down (TRAIN units).

Input: server-diagnostics/rtx5090-d2-1007/d2-term-gradient-influence-train48.jsonl (gen_petct_eval_sirb_term_gradient_
influence.py; 48 fixed TRAIN units from the offline bank, each scored by v1 flat with the B1 terms switched on (v1c),
K1 final, K1 at step 5000 and K2 final).  Per unit and term: delta[R] = -w <a_R, g>, the first-order change of region
R's mean target logit when one plain gradient step descends the term (per unit learning rate); positive raises R's
target score.  Training-log-type diagnostic on TRAIN units, never a validation score; AdamW, clipping and momentum are
not modelled.

Sections: 1 per network and stroke sign, the median and mean influence of every term on T, T near / far, T boundary /
interior, P ring and O, and the share of units where the term lowers T; 2 the "positive / negative" balance in the
spirit of EQL v2: the summed influence on T of the terms that raise it against those that lower it; 3 cosines with the
target soft Dice gradient; 3b unit counts behind the medians (hard negative against target Dice, target Dice itself
on T, hard negative on the P ring of remove units); 4 which voxels the hard-negative choice took (O, P ring, other P),
as shares of the voxels actually chosen (10-07: the denominator was the requested k, which is larger when a unit has
fewer candidates; corrected after the Codex round-3 check).  The section-2 shares hold for these probes and the
measured terms' effect on the mean target logit of T, not for the full training update (the probes come from the
offline bank with the far block and B5 pairs off).
"""
import collections
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "server-diagnostics" / "rtx5090-d2-1007" / "d2-term-gradient-influence-train48.jsonl"
REGIONS = ("T", "T_near", "T_far", "T_boundary", "T_interior", "P_ring", "O")
TARGET_DICE = "base_target_dice"

rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
units = [r for r in rows if r.get("kind") == "unit"]
footer = [r for r in rows if r.get("kind") == "footer"]
networks = [n["name"] for n in rows[0]["networks"]]
print(f"units: {len(units)} rows; networks {networks}; footer {footer[0] if footer else None}")

groups = collections.defaultdict(list)
for r in units:
    groups[(r["network"], r["sign"])].append(r)


def med(values):
    return statistics.median(values) if values else float("nan")


print("\n== 1. Influence on region target logits (median over units; share of units where the term lowers T)")
for net in networks:
    for sign in ("+", "-"):
        sel = groups.get((net, sign), [])
        if not sel:
            continue
        print(f"-- {net} sign {sign} ({len(sel)} units)")
        names = sorted({n for r in sel for n in r["terms"]})
        for name in names:
            parts = []
            for region in REGIONS:
                vals = [r["terms"][name]["influence"][region] for r in sel
                        if name in r["terms"] and region in r["terms"][name]["influence"]]
                if vals:
                    parts.append(f"{region} {med(vals):+.3g}")
            low = [r["terms"][name]["influence"].get("T", 0) < 0 for r in sel if name in r["terms"]
                   and "T" in r["terms"][name]["influence"]]
            share = sum(low) / len(low) if low else float("nan")
            print(f"   {name:24s} " + " ".join(parts) + f" | lowers T in {share:.0%}")

print("\n== 2. Balance on T: sum of positive influences vs sum of negative influences (median over units)")
for net in networks:
    for sign in ("+", "-"):
        sel = [r for r in groups.get((net, sign), []) if r["region_voxels"].get("T", 0) > 0]
        if not sel:
            continue
        ups, downs, ratio = [], [], []
        hard_share = []
        for r in sel:
            vals = {n: e["influence"].get("T") for n, e in r["terms"].items() if e["influence"].get("T") is not None}
            up = sum(v for v in vals.values() if v > 0)
            down = -sum(v for v in vals.values() if v < 0)
            ups.append(up)
            downs.append(down)
            ratio.append(up / down if down > 0 else float("inf"))
            hn = vals.get("intent_hard_negative")
            if hn is not None and down > 0:
                hard_share.append(max(0.0, -hn) / down)
        print(f"  {net:6s} {sign}: up {med(ups):.3g}  down {med(downs):.3g}  up/down median {med(ratio):.2f}"
              + (f"  hard-negative share of the downward push {med(hard_share):.0%}" if hard_share else ""))

print("\n== 3. Cosine of each term's gradient with the target soft Dice gradient (median)")
for net in networks:
    for sign in ("+", "-"):
        sel = groups.get((net, sign), [])
        names = sorted({n for r in sel for n in r["terms"]})
        parts = []
        for name in names:
            vals = [r["terms"][name]["cos_target_dice"] for r in sel if name in r["terms"]
                    and r["terms"][name]["cos_target_dice"] is not None]
            if vals:
                parts.append(f"{name.replace('intent_', 'i.').replace('base_', 'b.')} {med(vals):+.2f}")
        if parts:
            print(f"  {net:6s} {sign}: " + " | ".join(parts))

print("\n== 3b. Unit counts behind the medians")
for net in networks:
    for sign in ("+", "-"):
        sel = groups.get((net, sign), [])
        if not sel:
            continue
        hn = [r["terms"]["intent_hard_negative"] for r in sel if "intent_hard_negative" in r["terms"]]
        neg_cos = sum(1 for e in hn if e["cos_target_dice"] is not None and e["cos_target_dice"] < 0)
        hn_t_down = sum(1 for e in hn if e["influence"].get("T") is not None and e["influence"]["T"] < 0)
        ring = [e["influence"]["P_ring"] for e in hn if e["influence"].get("P_ring") is not None]
        td = [r["terms"][TARGET_DICE]["influence"].get("T") for r in sel if TARGET_DICE in r["terms"]]
        td_down = sum(1 for v in td if v is not None and v < 0)
        print(f"  {net:6s} {sign} ({len(sel)} units): hard negative lowers T {hn_t_down}/{len(hn)}, cosine with target "
              f"Dice < 0 in {neg_cos}/{len(hn)}; P ring lowered {sum(1 for v in ring if v < 0)}/{len(ring)} "
              f"(median {med(ring):+.4g}); {TARGET_DICE} lowers T in {td_down}/{len(td)}")

print("\n== 4. Hard-negative choice on the before state: share of the chosen voxels that are O / P ring / other P")
for net in networks:
    for sign in ("+", "-"):
        sel = groups.get((net, sign), [])
        k = sum(r["hard_negative_choice"]["k"] for r in sel)
        if not k:
            continue
        o = sum(r["hard_negative_choice"]["chosen_O"] for r in sel)
        ring = sum(r["hard_negative_choice"]["chosen_P_ring"] for r in sel)
        far = sum(r["hard_negative_choice"]["chosen_P_far"] for r in sel)
        chosen = o + ring + far
        mean_p = [r["hard_negative_choice"]["chosen_mean_pT"] for r in sel if r["hard_negative_choice"]["chosen_mean_pT"] is not None]
        print(f"  {net:6s} {sign}: requested k={k}, chosen {chosen}: O {o / chosen:.3f} P-ring {ring / chosen:.3f} "
              f"other P {far / chosen:.3f}  mean pT of chosen {med(mean_p):.3f}")
