"""Coordinator add-on: missed target voxels by distance from the stroke, split into error-blocked (derived e = pT+pO
< 0.5) and passed-but-not-executed (e >= 0.5, pT < 0.5), flat (N1_STATE) on the 101-episode list and the 397
trajectory states (VAL).

The stored events give, per event, only the TOTAL gate-passed share (error_gate_recall) and the total repaired voxels;
per distance they give the target geometry (coverage.jsonl: target voxels within 10..60 mm) and the repair beyond
15/30/60 mm (remote.jsonl).  No per-distance gate value is stored, so the ring split is only bounded by set arithmetic:
with B = blocked voxels, M = all missed voxels, missed_k = missed voxels in ring k,
    max(0, B - (M - missed_k)) <= B_k <= min(missed_k, B),   and P_k = missed_k - B_k.
Reported voxel-weighted (mL) and patient-weighted (event mean within patient, then patients equal), as [lower, upper].
"""
import collections
import json
from pathlib import Path

from A_common import VAL1, read_jsonl

OUT = Path(__file__).with_suffix(".json")
RINGS = ("<=15 mm", "15-30 mm", "30-60 mm", ">60 mm")
res = {}
for lst in ("samestate-list", "samestate-trajectory"):
    base = VAL1 / lst / "N1_STATE-s3407"
    ev = [e for e in read_jsonl(base / "events.jsonl") if e.get("status") == "ok" and e.get("target_voxels")]
    cov = {(c["episode_id"], float(c["radius_mm"])): c for c in read_jsonl(base / "coverage.jsonl")}
    rem = {(c["episode_id"], float(c["radius_mm"])): c for c in read_jsonl(base / "remote.jsonl")}
    orc = collections.defaultdict(dict)
    for o in read_jsonl(base / "oracle.jsonl"):
        orc[o["episode_id"]][o["oracle_mode"]] = o
    vox = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])  # ring -> missed, B_lo, B_hi, volume
    pat = collections.defaultdict(lambda: collections.defaultdict(list))  # ring -> patient -> (lo, hi)
    exact = collections.Counter()
    overall = [0.0, 0.0, 0.0, 0.0]  # T, repaired, blocked, passed-not-executed (voxels x ml)
    pat_overall = collections.defaultdict(list)
    checks = {"max_neg_missed_vox": 0.0, "max_gate_minus_oracle_binding_recall": 0.0, "events": 0}
    for e in ev:
        eid, T = e["episode_id"], int(e["target_voxels"])
        vml = float(e["target_volume_ml"]) / T
        Rv = int(e["target_recovered_voxels"])
        passed = int(round(float(e["error_gate_recall"]) * T))
        B, P = T - passed, passed - Rv
        c15, c30, c60 = (int(cov[(eid, r)]["covered_voxels"]) for r in (15.0, 30.0, 60.0))
        r15, r30, r60 = (float(rem[(eid, r)]["remote_target_repair_ml"]) / vml for r in (15.0, 30.0, 60.0))
        V = [c15, c30 - c15, c60 - c30, T - c60]
        R = [Rv - r15, r15 - r30, r30 - r60, r60]
        missed = [max(v - r, 0.0) for v, r in zip(V, R)]
        checks["max_neg_missed_vox"] = max(checks["max_neg_missed_vox"], max(r - v for v, r in zip(V, R)))
        M = sum(missed)
        ob = orc[eid].get("oracle_binding_keep_error")
        if ob is not None:
            checks["max_gate_minus_oracle_binding_recall"] = max(
                checks["max_gate_minus_oracle_binding_recall"], abs(float(ob["target_recall"]) - passed / T))
        checks["events"] += 1
        overall[0] += T * vml
        overall[1] += Rv * vml
        overall[2] += B * vml
        overall[3] += P * vml
        pat_overall[e["patient_id"]].append((Rv / T, B / T, P / T))
        for k, ring in enumerate(RINGS):
            if missed[k] <= 1e-9:
                continue
            lo = max(0.0, B - (M - missed[k]))
            hi = min(missed[k], float(B))
            vox[ring][0] += missed[k] * vml
            vox[ring][1] += lo * vml
            vox[ring][2] += hi * vml
            vox[ring][3] += V[k] * vml
            pat[ring][e["patient_id"]].append((lo / missed[k], hi / missed[k]))
            exact[(ring, "exact")] += (hi - lo) < 0.5
            exact[(ring, "events")] += 1
    out = {"checks": checks,
           "overall_voxel_weighted": {"repaired": overall[1] / overall[0], "error_blocked": overall[2] / overall[0],
                                      "passed_not_executed": overall[3] / overall[0]},
           "overall_patient_weighted": {name: sum(sum(x[i] for x in v) / len(v) for v in pat_overall.values()) / len(pat_overall)
                                        for i, name in enumerate(("repaired", "error_blocked", "passed_not_executed"))},
           "rings": {}}
    for ring in RINGS:
        m, lo, hi, vol = vox[ring]
        pp = pat[ring]
        out["rings"][ring] = {
            "events_with_missed": exact[(ring, "events")], "events_split_exact": exact[(ring, "exact")],
            "patients": len(pp), "target_ml": vol, "missed_ml": m,
            "missed_share_of_ring_target": m / vol if vol else None,
            "blocked_share_of_missed_voxel_weighted": [lo / m, hi / m] if m else None,
            "blocked_share_of_missed_patient_weighted": [sum(sum(a for a, _ in v) / len(v) for v in pp.values()) / len(pp),
                                                         sum(sum(b for _, b in v) / len(v) for v in pp.values()) / len(pp)] if pp else None}
    res[lst] = out
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
for lst, o in res.items():
    print("=====", lst, o["checks"])
    print("   overall voxel-weighted", {k: round(v, 3) for k, v in o["overall_voxel_weighted"].items()},
          "patient-weighted", {k: round(v, 3) for k, v in o["overall_patient_weighted"].items()})
    for ring, x in o["rings"].items():
        print(f"   {ring:9s} events {x['events_with_missed']:3d} exact {x['events_split_exact']:3d} patients {x['patients']:2d} "
              f"target {x['target_ml']:8.1f} mL missed {x['missed_ml']:8.1f} mL ({(x['missed_share_of_ring_target'] or 0):.3f}) "
              f"blocked share vox {[round(v, 3) for v in x['blocked_share_of_missed_voxel_weighted']]} "
              f"pat {[round(v, 3) for v in x['blocked_share_of_missed_patient_weighted']]}")
