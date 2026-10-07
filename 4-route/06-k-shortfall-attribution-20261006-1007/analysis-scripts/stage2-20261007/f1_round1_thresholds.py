"""Diagnostic D1 read-out: round-1 score distributions and what any execution threshold would give (VAL).

Input: server-diagnostics/z390-queue-diag-1007/round1-score-histograms.jsonl (from
gen_petct_eval_sirb_round1_score_histograms.py: per scan and network, histograms of the native pT over 40 equal bins in
T / O / P by distance band to the stroke, plus T boundary / interior / P ring and the error map e on T and O).

Round 1 starts from the same mask with the same stroke for every network, so the networks are compared voxel by voxel.
For a threshold tau (a multiple of 0.025, so bin sums are exact) the edit is every editable voxel with pT >= tau:
  add:    Dice' = 2 (I + t + o) / (M + G + t + o + p)
  remove: Dice' = 2 (I - p) / (M + G - t - o - p)
with t, o, p the T, O, P voxels at or above tau and I = |M and G|, M = |M|, G = |G| on the native grid.  At tau = 0.5
the patient mean must reproduce the rollout's D1 (v1 flat 0.6948, K1 0.6916, K2 0.6793): checked first.
Sections: 1 check; 2 Dice at tau, add and remove strokes read separately (the other sign kept at 0.5); 2b both
thresholds at once (round 1 starts from the same mask, so the joint optimum is exact); 3 the decision-theory rule (add
at D/2, remove at 1 - D/2 with the scan's own start Dice: a reference that uses the truth, not an upper bound, D is not
known at inference); 4 T recovered by distance band at 0.5 and 0.3; 4b volumes at 0.5 and at the joint VAL-best
thresholds; 5 where T voxels fail: e < 0.5 (total error score below 0.5) or e >= 0.5 but pT < 0.5 (total error score
over 0.5 while T's own score is below it; T may still score above O, so this is not "bound to O"); 5b threshold-free
ranking with the exact bounds that the 40 bins leave open; 6 T boundary / interior / P ring.  VAL; thresholds read off
VAL are diagnostics, never method values.  10-07: 2b, 4b, 5b bounds added and the 5b median made the standard median
(it was the upper median) after the Codex round-3 check.
"""
import collections
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from b0_load import patient_mean  # noqa: E402

SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE.parent / "server-diagnostics" / "z390-queue-diag-1007"
                                                     / "round1-score-histograms.jsonl")
TAUS = [round(0.025 * k, 3) for k in range(1, 40)]

rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
header = rows[0]
edges = header["bin_edges"]
nbins = len(edges) - 1
cases = [r for r in rows[1:] if r.get("kind") == "case" and r.get("status") == "ok" and r.get("prediction_status") == "ok"]
networks = [n["name"] for n in header["networks"]]
band_edges = header["band_edges_mm"]
band_names = [f"{band_edges[i]:g}-{band_edges[i + 1]:g}" if band_edges[i + 1] is not None else f">{band_edges[i]:g}"
              for i in range(len(band_edges) - 1)]


def at_or_above(hist_role, tau, bands=None):
    first = int(round(tau / (1.0 / nbins)))
    total = 0
    for band, counts in hist_role.items():
        if bands is not None and int(band) not in bands:
            continue
        total += sum(counts[first:])
    return total


def role_total(hist_role, bands=None):
    return sum(sum(c) for b, c in hist_role.items() if bands is None or int(b) in bands)


def dice_after(row, tau):
    h = row["hist"]
    t, o, p = at_or_above(h["T"], tau), at_or_above(h["O"], tau), at_or_above(h["P"], tau)
    i, m, g = row["intersection"], row["mask"], row["reference"]
    if row["sign"] == "+":
        return 2 * (i + t + o) / (m + g + t + o + p)
    return 2 * (i - p) / (m + g - t - o - p)


def start_dice(row):
    return 2 * row["intersection"] / (row["mask"] + row["reference"])


by_net = collections.defaultdict(list)
for r in cases:
    by_net[r["network"]].append(r)

print("== 1. Check: patient-mean round-1 Dice at tau 0.5 (positive scans with a stroke)")
for net in networks:
    values = {r["case_id"]: dice_after(r, 0.5) for r in by_net[net]}
    exact = {r["case_id"]: r["at_half"] for r in by_net[net]}
    agree = all(exact[c]["T"] == at_or_above(r["hist"]["T"], 0.5) for c, r in ((r["case_id"], r) for r in by_net[net]))
    print(f"  {net:8s} scans {len(values)}  D1 {patient_mean(values)[0]:.4f}  histogram = exact count at 0.5: {agree}")

print("\n== 2. Patient-mean round-1 Dice when only the ADD threshold (or only the REMOVE threshold) moves")
for net in networks:
    best = {}
    for sign in ("+", "-"):
        line = []
        for tau in TAUS:
            values = {r["case_id"]: (dice_after(r, tau) if r["sign"] == sign else dice_after(r, 0.5)) for r in by_net[net]}
            d = patient_mean(values)[0]
            line.append((tau, d))
        top = max(line, key=lambda x: x[1])
        best[sign] = top
        show = " ".join(f"{tau:.2f}:{d:.4f}" for tau, d in line if tau in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9))
        print(f"  {net:8s} {sign} {show}  | best on VAL {top[0]:.3f} -> {top[1]:.4f}")

def dice_joint(row, tau_add, tau_remove):
    return dice_after(row, tau_add if row["sign"] == "+" else tau_remove)


print("\n== 2b. Both thresholds at once (joint grid on VAL; diagnostic, not a method value)")
joint_best = {}
for net in networks:
    base = patient_mean({r["case_id"]: dice_after(r, 0.5) for r in by_net[net]})[0]
    best = max(((ta, tr, patient_mean({r["case_id"]: dice_joint(r, ta, tr) for r in by_net[net]})[0])
                for ta in TAUS for tr in TAUS), key=lambda x: x[2])
    joint_best[net] = best
    print(f"  {net:8s} D1 both 0.5 {base:.5f} -> add {best[0]:.3f} / remove {best[1]:.3f} {best[2]:.5f} "
          f"({best[2] - base:+.5f})")

print("\n== 3. Decision-theory thresholds per scan: add at D0/2, remove at 1 - D0/2 (D0 = scan's start Dice; reference)")
for net in networks:
    values = {}
    for r in by_net[net]:
        d0 = start_dice(r)
        raw = d0 / 2 if r["sign"] == "+" else 1 - d0 / 2
        tau = min(TAUS, key=lambda x: abs(x - raw))
        values[r["case_id"]] = dice_after(r, tau)
    base = {r["case_id"]: dice_after(r, 0.5) for r in by_net[net]}
    print(f"  {net:8s} D1 at 0.5 {patient_mean(base)[0]:.4f} -> decision rule {patient_mean(values)[0]:.4f}")

print("\n== 4. Add strokes: share of T recovered by distance band (sums over scans), at 0.5 and 0.3")
for net in networks:
    adds = [r for r in by_net[net] if r["sign"] == "+"]
    parts = []
    for band in range(len(band_names)):
        total = sum(role_total(r["hist"]["T"], {band}) for r in adds)
        if total == 0:
            continue
        fixed5 = sum(at_or_above(r["hist"]["T"], 0.5, {band}) for r in adds)
        fixed3 = sum(at_or_above(r["hist"]["T"], 0.3, {band}) for r in adds)
        parts.append(f"{band_names[band]}mm {fixed5 / total:.2f}/{fixed3 / total:.2f} (n={total})")
    print(f"  {net:8s} " + " | ".join(parts))
    p5 = sum(at_or_above(r["hist"]["P"], 0.5) for r in adds)
    p3 = sum(at_or_above(r["hist"]["P"], 0.3) for r in adds)
    print(f"  {'':8s} P voxels added: at 0.5 {p5}, at 0.3 {p3}")

print("\n== 4b. Round-1 volumes (ml, sums over scans): add T fixed / background added, remove T fixed / true lesion removed")
far_bands = {i for i, edge in enumerate(band_edges[:-1]) if edge >= 60}
for net in networks:
    ta, tr, _ = joint_best[net]
    for label, (tau_a, tau_r) in (("both 0.5", (0.5, 0.5)), (f"add {ta:.3f} / remove {tr:.3f}", (ta, tr))):
        adds = [r for r in by_net[net] if r["sign"] == "+"]
        rems = [r for r in by_net[net] if r["sign"] == "-"]
        vol = {
            "add T": sum(at_or_above(r["hist"]["T"], tau_a) * r["voxel_ml"] for r in adds),
            "add FP": sum(at_or_above(r["hist"]["P"], tau_a) * r["voxel_ml"] for r in adds),
            "remove T": sum(at_or_above(r["hist"]["T"], tau_r) * r["voxel_ml"] for r in rems),
            "remove TP": sum(at_or_above(r["hist"]["P"], tau_r) * r["voxel_ml"] for r in rems),
        }
        far_total = sum(role_total(r["hist"]["T"], far_bands) * r["voxel_ml"] for r in adds)
        far_hit = sum(at_or_above(r["hist"]["T"], tau_a, far_bands) * r["voxel_ml"] for r in adds)
        print(f"  {net:8s} {label:24s} " + "  ".join(f"{k} {v:8.2f}" for k, v in vol.items())
              + f"  | add T beyond 60 mm, volume share recovered {far_hit / far_total:.4f}")

print("\n== 5. Add strokes: why T voxels stay below 0.5 (sums over scans; e = pT + pO)")
for net in networks:
    adds = [r for r in by_net[net] if r["sign"] == "+" and r.get("hist_error")]
    if not adds:
        print(f"  {net:8s} no error map recorded")
        continue
    t_total = sum(role_total(r["hist"]["T"]) for r in adds)
    t_hit = sum(at_or_above(r["hist"]["T"], 0.5) for r in adds)
    e_hit = sum(at_or_above(r["hist_error"]["T"], 0.5) for r in adds)
    print(f"  {net:8s} T voxels {t_total}: pT>=0.5 {t_hit / t_total:.3f} | e>=0.5 {e_hit / t_total:.3f} | "
          f"e<0.5 (total error score low) {(t_total - e_hit) / t_total:.3f} | e>=0.5 but pT<0.5 (error score over, "
          f"T's own score under) {(e_hit - t_hit) / t_total:.3f}")

def merged(hist_role, bands=None):
    total = [0] * nbins
    for band, counts in hist_role.items():
        if bands is None or int(band) in bands:
            total = [a + b for a, b in zip(total, counts)]
    return total


def auc(pos, neg, tie=0.5):
    """P(score of a T voxel > score of a P voxel) from two histograms on the same bins.  tie = the share of the
    within-bin pairs counted as T above P: 0.5 for the estimate, 0 and 1 for the exact lower and upper bounds (the order
    inside a bin is not recorded)."""
    n_pos, n_neg = sum(pos), sum(neg)
    if not n_pos or not n_neg:
        return None
    below, acc = 0, 0.0
    for b in range(nbins):
        acc += pos[b] * (below + tie * neg[b])
        below += neg[b]
    return acc / (n_pos * n_neg)


def pooled(sel, role, bands=None):
    return [sum(x) for x in zip(*[merged(r["hist"][role], bands) for r in sel])]


print("\n== 5b. Ranking quality, threshold-free: AUC of T against editable P, estimate [exact bounds from the bins]")
near_bands = {i for i, edge in enumerate(band_edges[:-1]) if band_edges[i + 1] is not None and band_edges[i + 1] <= 30}
per_scan_near = collections.defaultdict(dict)
for net in networks:
    for sign in ("+", "-"):
        sel = [r for r in by_net[net] if r["sign"] == sign]
        if not sel:
            continue
        whole = [auc(pooled(sel, "T"), pooled(sel, "P"), t) for t in (0.5, 0.0, 1.0)]
        near = [auc(pooled(sel, "T", near_bands), pooled(sel, "P", near_bands), t) for t in (0.5, 0.0, 1.0)]
        per_scan = [a for a in (auc(merged(r["hist"]["T"]), merged(r["hist"]["P"])) for r in sel) if a is not None]
        scan_near = {}
        for r in sel:
            est = [auc(merged(r["hist"]["T"], near_bands), merged(r["hist"]["P"], near_bands), t) for t in (0.5, 0.0, 1.0)]
            if est[0] is not None:
                scan_near[r["case_id"]] = est
        per_scan_near[(net, sign)] = scan_near
        print(f"  {net:8s} {sign} pooled {whole[0]:.4f} [{whole[1]:.4f}, {whole[2]:.4f}] | within 30 mm {near[0]:.4f} "
              f"[{near[1]:.4f}, {near[2]:.4f}] | per-scan median {statistics.median(per_scan):.5f} (n={len(per_scan)}) | "
              f"within 30 mm per scan, patient mean {patient_mean({c: v[0] for c, v in scan_near.items()})[0]:.4f}")
print("  Scans where the bounds do not overlap (within 30 mm): certainly worse / certainly better than v1 flat")
for net in networks:
    if net == "v1flat":
        continue
    for sign in ("+", "-"):
        mine, ref = per_scan_near[(net, sign)], per_scan_near[("v1flat", sign)]
        common = set(mine) & set(ref)
        worse = sum(1 for c in common if mine[c][2] < ref[c][1])
        better = sum(1 for c in common if mine[c][1] > ref[c][2])
        print(f"  {net:8s} {sign} scans {len(common)}: certainly worse {worse}, certainly better {better}")

print("\n== 6. Boundary and interior of T, and the P ring around T, share at or above 0.5 (add / remove)")
for net in networks:
    for sign in ("+", "-"):
        sel = [r for r in by_net[net] if r["sign"] == sign and r.get("hist_parts")]
        if not sel:
            continue
        out = []
        for part in ("T_boundary", "T_interior", "P_ring"):
            total = sum(role_total(r["hist_parts"][part]) for r in sel)
            hit = sum(at_or_above(r["hist_parts"][part], 0.5) for r in sel)
            out.append(f"{part} {hit / total:.3f} (n={total})" if total else f"{part} -")
        print(f"  {net:8s} {sign} " + " | ".join(out))
