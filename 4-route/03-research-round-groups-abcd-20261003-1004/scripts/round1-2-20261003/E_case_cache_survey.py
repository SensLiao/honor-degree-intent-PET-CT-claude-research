"""E_ one-off (read-only): survey the local copy of the SIRB case cache meta files.

Reports native shapes, voxel counts, research-grid sizes, tile counts, p0 presence per split and file sizes.
Reads meta.json and file sizes only; opens no array and no label.
"""
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:/honor-petct-data-hub/z390/cache-inputs/dataset-sirb-cases-gen-20260919-R2/cache/inputs")
RESEARCH_MM = 3.0
TILE = 96
OVERLAP = None  # filled from the implementation config if found


def main() -> None:
    rows = []
    for meta_path in sorted(ROOT.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        shape = meta["native_shape_dhw"]
        affine = meta["affine_dhw"]
        spacing = [math.sqrt(sum(affine[r][c] ** 2 for r in range(3))) for c in range(3)]
        extent = [n * s for n, s in zip(shape, spacing)]
        research = [math.ceil(e / RESEARCH_MM) for e in extent]
        files = {p.name: p.stat().st_size for p in meta_path.parent.iterdir() if p.is_file()}
        rows.append({"case": meta["case_id"], "split": meta["split"], "shape": shape, "spacing": spacing,
                     "research": research, "p0_file": "p0.npy" in files, "p0_cached_flag": meta.get("p0_cached", True),
                     "bytes": sum(files.values()), "voxels": shape[0] * shape[1] * shape[2]})
    splits = Counter(r["split"] for r in rows)
    print("cases", len(rows), dict(splits))
    print("p0 file present by split", Counter((r["split"], r["p0_file"], r["p0_cached_flag"]) for r in rows))
    vox = sorted(r["voxels"] for r in rows)
    res = sorted(r["research"][0] * r["research"][1] * r["research"][2] for r in rows)
    q = lambda xs, f: xs[min(len(xs) - 1, int(f * len(xs)))]  # noqa: E731
    print("native voxels (M) p10/p50/p90/max", [round(q(vox, f) / 1e6, 1) for f in (0.1, 0.5, 0.9, 0.999)])
    print("research voxels (M) p10/p50/p90/max", [round(q(res, f) / 1e6, 1) for f in (0.1, 0.5, 0.9, 0.999)])
    print("case dir MB p50/max", round(q(sorted(r["bytes"] for r in rows), 0.5) / 1e6, 1),
          round(max(r["bytes"] for r in rows) / 1e6, 1))
    print("total cache GB", round(sum(r["bytes"] for r in rows) / 1e9, 2),
          "train-only GB", round(sum(r["bytes"] for r in rows if r["split"] == "train") / 1e9, 2))
    print("shape examples", Counter(tuple(r["shape"][1:]) for r in rows).most_common(5))
    print("z extents mm p10/p50/p90", [round(q(sorted(r["shape"][0] * r["spacing"][0] for r in rows), f))
                                        for f in (0.1, 0.5, 0.9)])
    print("research shape p50", sorted(rows, key=lambda r: r["research"][0] * r["research"][1] * r["research"][2])
          [len(rows) // 2]["research"])


if __name__ == "__main__":
    sys.exit(main())
