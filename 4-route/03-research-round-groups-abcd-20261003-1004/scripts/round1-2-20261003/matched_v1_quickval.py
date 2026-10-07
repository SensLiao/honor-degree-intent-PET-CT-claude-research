"""Matched v1 baseline on the quick-VAL roster: pick from the v1 three-style full VAL the same (scan, style) the
quick VAL used, then compare patient-mean D0..D5 and nAUC with the +8k static controls.  VAL only."""
import csv, collections, random, sys
from pathlib import Path

ROOT = Path(".")
def load(path):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    return rows

def table(rows, keyset=None):
    # (scan, style) -> {round: dice}, patient map, positivity
    d = collections.defaultdict(dict); pat = {}; pos = {}
    for r in rows:
        k = (r["scan_id"], r["style"])
        if keyset is not None and k not in keyset:
            continue
        if r["status"] != "ok":
            print("non-ok row", r["scan_id"], r["style"], r["round"], r["status"], file=sys.stderr)
        d[k][int(r["round"])] = float(r["dice"]) if r["dice"] not in ("", "nan", "None") else None
        pat[k] = r["patient_id"]; pos[k] = r["gt_positive"] == "True"
    return d, pat, pos

def patient_curves(d, pat, pos):
    per_pat = collections.defaultdict(list)
    for k, rounds in d.items():
        if not pos[k]:
            continue
        per_pat[pat[k]].append([rounds[i] for i in range(6)])
    out = {}
    for p, scans in per_pat.items():
        out[p] = [sum(s[i] for s in scans) / len(scans) for i in range(6)]
    return out

def nauc(c):  # trapezoid over 6 states, normalised to [0,1]
    return sum((c[i] + c[i + 1]) / 2 for i in range(5)) / 5

def summary(curves):
    n = len(curves)
    mean = [sum(c[i] for c in curves.values()) / n for i in range(6)]
    return n, mean, sum(nauc(c) for c in curves.values()) / n

quick = {
    "N1_STATE_STATIC": "eval-sirb-v2-quickval-N1_STATE_STATIC-R1-20261003/six_state.csv",
    "N4_STATIC": "eval-sirb-v2-quickval-N4_STATIC-R1-20261003/six_state.csv",
}
v1 = {"N1_STATE_STATIC": "eval-sirb-batch1-val-20260925/rollout/N1_STATE-s3407/six_state.csv",
      "N4_STATIC": "eval-sirb-batch1-val-20260925/rollout/N3-s3407/six_state.csv"}
for arm in quick:
    q_rows = load(quick[arm])
    keys = {(r["scan_id"], r["style"]) for r in q_rows}
    qd, qp, qpos = table(q_rows)
    vd, vp, vpos = table(load(v1[arm]), keys)
    assert set(qd) == set(vd), (len(qd), len(vd))
    qc, vc = patient_curves(qd, qp, qpos), patient_curves(vd, vp, vpos)
    assert set(qc) == set(vc)
    # D0 must match exactly (same start)
    d0diff = max(abs(qc[p][0] - vc[p][0]) for p in qc)
    nq, mq, aq = summary(qc); nv, mv, av = summary(vc)
    diffs5 = [qc[p][5] - vc[p][5] for p in qc]; diffsA = [nauc(qc[p]) - nauc(vc[p]) for p in qc]
    rng = random.Random(3407); pats = list(qc); boot5 = []; bootA = []
    for _ in range(10000):
        s = [rng.choice(pats) for _ in pats]
        boot5.append(sum(qc[p][5] - vc[p][5] for p in s) / len(s))
        bootA.append(sum(nauc(qc[p]) - nauc(vc[p]) for p in s) / len(s))
    boot5.sort(); bootA.sort()
    print(f"== {arm} (+8k static) vs v1 parent on the SAME quick-VAL roster; patients={nq}; max D0 diff={d0diff:.2e}")
    print("  v1   D0..D5:", " ".join(f"{x:.4f}" for x in mv), f"nAUC {av:.4f}")
    print("  +8k  D0..D5:", " ".join(f"{x:.4f}" for x in mq), f"nAUC {aq:.4f}")
    print(f"  D5 diff {sum(diffs5)/len(diffs5):+.4f}  95%CI [{boot5[250]:+.4f}, {boot5[9749]:+.4f}]  better/worse/tie "
          f"{sum(x>1e-9 for x in diffs5)}/{sum(x<-1e-9 for x in diffs5)}/{sum(abs(x)<=1e-9 for x in diffs5)}")
    print(f"  nAUC diff {sum(diffsA)/len(diffsA):+.4f}  95%CI [{bootA[250]:+.4f}, {bootA[9749]:+.4f}]")
