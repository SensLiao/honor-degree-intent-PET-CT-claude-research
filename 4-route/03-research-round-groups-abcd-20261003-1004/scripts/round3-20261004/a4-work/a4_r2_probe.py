# -*- coding: utf-8 -*-
"""Round-2 probe: what the same-state sweep/events rows are (state_source, round, style), and whether a round-0
list event uses the same stroke as the rollout's first transition.  Read-only, VAL."""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a4_common import VAL1, ROLL, ARMS, read_jsonl

for lst in ("samestate-list", "samestate-trajectory"):
    ev = read_jsonl(VAL1 / lst / "N1_STATE-s3407" / "events.jsonl")
    sw = read_jsonl(VAL1 / lst / "N1_STATE-s3407" / "sweep.jsonl")
    print("==", lst, "events", len(ev), "sweep rows", len(sw))
    print("  event keys:", sorted(ev[0].keys()))
    print("  events by (state_source, round):", dict(collections.Counter((e.get("state_source"), e.get("round")) for e in ev)))
    print("  events by sign:", dict(collections.Counter(e.get("sign") for e in ev)))
    print("  sweep by (state_source, round):", dict(collections.Counter((s.get("state_source"), s.get("round")) for s in sw)))
    print("  sweep thresholds per episode:", collections.Counter(collections.Counter(s["episode_id"] for s in sw).values()))
    ep = ev[0]
    print("  example event:", {k: ep[k] for k in ("episode_id", "round", "state_source", "style", "sign") if k in ep})

# does the list round-0 event equal the rollout's transition 0 for the same (scan, style)?
tr = {(r["scan_id"], r["style"], int(r["transition"])): r for r in read_jsonl(ROLL / ARMS["flat"] / "transitions.jsonl")}
ev = read_jsonl(VAL1 / "samestate-list" / "N1_STATE-s3407" / "events.jsonl")
same = diff = 0
rows = []
for e in ev:
    if int(e.get("round", -1)) != 0:
        continue
    key = (e["scan_id"], e["style"], 0)
    x = tr.get(key)
    if x is None:
        rows.append((e["episode_id"], "no rollout transition"))
        continue
    v_ev = float(e.get("target_voxels", 0))
    same_target = abs(float(x["target_volume_ml"] or 0) - float(e.get("target_recovery_ml", 0)) / max(float(e.get("target_recall") or 1e-9), 1e-9)) < 1e-6
    rows.append((e["episode_id"], e.get("sign"), x["sign"], round(float(x["target_volume_ml"] or 0), 4), e.get("target_voxels"),
                 round(float(e.get("target_recovery_ml") or 0), 4), round(float(x["target_recovery_ml"] or 0), 4)))
print("round-0 list events vs rollout transition 0 (episode, list sign, rollout sign, rollout V mL, list target voxels, list R, rollout R):")
for r in rows:
    print("  ", r)
