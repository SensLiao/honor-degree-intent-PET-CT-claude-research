"""E_ one-off (read-only): pair-manifest facts for the code-feasibility review.

* pair npz file sizes (what a training unit reads and decompresses per step);
* how often one STATE (same state hash) appears with several different strokes / targets in the TRAIN bank, i.e.
  whether counterfactual strokes for the same state already exist;
* (sign, target size) shares of the pair rows (target_before voxels x native voxel volume of the case).
Reads the local JSONL copies and case meta.json files only.
"""
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

BANK = Path(r"C:/Users/廖神/Desktop/Honor degree/.tmp/z390-pull/train-bank")
CASES = Path(r"D:/honor-petct-data-hub/z390/cache-inputs/dataset-sirb-cases-gen-20260919-R2/cache/inputs")


def voxel_ml(case_id: str, cache: dict) -> float:
    if case_id not in cache:
        meta = json.loads((CASES / case_id / "meta.json").read_text(encoding="utf-8"))
        a = meta["affine_dhw"]
        spacing = [math.sqrt(sum(a[r][c] ** 2 for r in range(3))) for c in range(3)]
        cache[case_id] = spacing[0] * spacing[1] * spacing[2] / 1000.0
    return cache[case_id]


def main() -> None:
    pairs = [json.loads(line) for line in (BANK / "pairs.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    episodes = [json.loads(line) for line in (BANK / "episodes.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()]
    print("pair rows", len(pairs), "episode rows", len(episodes))
    sizes = sorted(p["file_bytes"] for p in pairs)
    print("pair npz bytes p50/p90/max", sizes[len(sizes) // 2], sizes[int(0.9 * len(sizes))], sizes[-1],
          "total GB", round(sum(sizes) / 1e9, 2))
    # same state, several strokes
    by_state = defaultdict(set)
    by_state_sign = defaultdict(set)
    for e in episodes:
        by_state[(e["case_id"], e["state_hash"])].add(e["stroke_hash"])
        by_state_sign[(e["case_id"], e["state_hash"], e["sign"])].add(e["stroke_hash"])
    multi = Counter(len(v) for v in by_state.values())
    print("states", len(by_state), "strokes per state histogram", sorted(multi.items()))
    multi_sign = Counter(len(v) for v in by_state_sign.values())
    print("(state,sign) groups", len(by_state_sign), "strokes per (state,sign)", sorted(multi_sign.items()))
    print("episode rounds", Counter(e["round"] for e in episodes).most_common(),
          "styles", Counter(e["style"] for e in episodes).most_common(),
          "policies", Counter(e["selection_policy"] for e in episodes).most_common())
    # sign x size of the TARGET of the pair rows (before side)
    cache: dict = {}
    classes = Counter()
    for p in pairs:
        ml = p["transition_counts"]["target_before"] * voxel_ml(p["case_id"], cache)
        size = "<0.5" if ml < 0.5 else ("0.5-10" if ml < 10 else ">=10")
        classes[(p["sign"], size)] += 1
    total = sum(classes.values())
    print("pair rows by (sign, target mL):", {k: round(v / total, 3) for k, v in sorted(classes.items())})
    print("pair types", Counter(p["pair_type"] for p in pairs).most_common())
    print("rows per episode", statistics.mean(Counter(p["episode_id"] for p in pairs).values()))


if __name__ == "__main__":
    sys.exit(main())
