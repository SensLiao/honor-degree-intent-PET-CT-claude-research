"""Figures of the VAL behaviour analysis (saved into ../figures/): gain split by stroke sign, round-1 add-stroke fill by
distance to the stroke, D5 by patient group, lesion-level safety.  VAL only; colours as in the training-curve figures
(v1 flat grey-black, K1 blue, K2 orange, K2 + flip light orange, ideal repair purple)."""
import collections
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from b0_load import KEYS, POS, jl, load, patient_mean, per_patient  # noqa: E402
from b0_paths import RUNS  # noqa: E402

OUT = HERE.parent / "figures"
COLOR = {"v1flat": "#222222", "K1": "#1f5fbf", "K1flip": "#7fa7e0", "K2": "#e07b00", "K2flip": "#f5b041",
         "oracle": "#7b3fa0"}
LABEL = {"v1flat": "v1 flat", "K1": "K1", "K1flip": "K1 + flip", "K2": "K2", "K2flip": "K2 + flip",
         "oracle": "ideal repair"}
SYSTEMS = ["v1flat", "K1", "K1flip", "K2", "K2flip"]
data = {n: load(n) for n in SYSTEMS + ["oracle"]}

# 1. five-round gain split by stroke sign
fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=150)
names = SYSTEMS + ["oracle"]
adds, rems = [], []
for n in names:
    six, tr, _ = data[n]
    g = collections.Counter()
    for k in range(5):
        for sign in ("+", "-"):
            vals = {}
            for (s, st), v in six.items():
                if s not in POS or None in v["dice"]:
                    continue
                r = tr.get((s, st, k))
                hit = r is not None and not r.get("no_stroke") and r.get("sign") == sign
                vals[s] = (v["dice"][k + 1] - v["dice"][k]) if hit else 0.0
            g[sign] += patient_mean(vals)[0]
    adds.append(g["+"])
    rems.append(g["-"])
x = range(len(names))
ax.bar([i - 0.2 for i in x], adds, width=0.4, color=[COLOR[n] for n in names], label="add strokes")
ax.bar([i + 0.2 for i in x], rems, width=0.4, color=[COLOR[n] for n in names], alpha=0.45, hatch="//",
       edgecolor="white", label="remove strokes")
for i, (a, r) in enumerate(zip(adds, rems)):
    ax.text(i - 0.2, a + 0.003, f"{a:+.3f}", ha="center", fontsize=7)
    ax.text(i + 0.2, r + 0.003, f"{r:+.3f}", ha="center", fontsize=7)
ax.set_xticks(list(x))
ax.set_xticklabels([LABEL[n] for n in names])
ax.set_ylabel("five-round Dice gain (patient mean)")
ax.set_title("Where the gain comes from: add strokes (solid) vs remove strokes (hatched), VAL")
ax.legend(frameon=False, fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "val-gain-by-stroke-sign.png")
plt.close(fig)

# 2. round-1 add strokes: share of the pointed missed lesion recovered beyond each radius (remote.jsonl)
fig, ax = plt.subplots(figsize=(7.5, 4.0), dpi=150)
radii = [15.0, 30.0, 60.0]
for n in SYSTEMS + ["oracle"]:
    six, tr, rem = data[n]
    total = {}
    for (s, st, k), r in tr.items():
        if k == 0 and r.get("sign") == "+" and not r.get("no_stroke"):
            total[(s, st)] = r.get("target_recovery_ml") or 0.0
    t_all = sum(total.values())
    ys = [1.0]
    for radius in radii:
        far = sum((rem.get((s, st, 0), {}).get(radius, {}).get("remote_target_repair_ml") or 0.0) for (s, st) in total)
        ys.append(far / t_all if t_all else 0.0)
    ax.plot(["all", ">15 mm", ">30 mm", ">60 mm"], ys, marker="o", color=COLOR[n], label=f"{LABEL[n]} (total {t_all:.0f} ml)")
ax.set_ylabel("share of the round-1 add repair\nthat lies beyond the radius")
ax.set_title("Round-1 add strokes: share of the repair beyond each radius (VAL)")
ax.legend(frameon=False, fontsize=8)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "val-round1-add-repair-by-distance.png")
plt.close(fig)

# 3. D5 by patient group (start missed volume terciles)
six_v1 = data["v1flat"][0]
start_fn = per_patient({s: v["fn_ml"][0] for (s, st), v in six_v1.items() if s in POS})
order = sorted(start_fn, key=lambda p: start_fn[p])
groups = [order[:18], order[18:36], order[36:]]
fig, ax = plt.subplots(figsize=(7.5, 4.0), dpi=150)
width = 0.15
for j, n in enumerate(SYSTEMS):
    d5 = per_patient({s: v["dice"][5] for (s, st), v in data[n][0].items() if s in POS})
    ys = [sum(d5[p] for p in g) / len(g) for g in groups]
    ax.bar([i + (j - 2) * width for i in range(3)], ys, width=width, color=COLOR[n], label=LABEL[n])
ax.set_xticks(range(3))
med = [statistics.median(start_fn[p] for p in g) for g in groups]
ax.set_xticklabels([f"least missed\n(median {med[0]:.2f} ml)", f"middle\n(median {med[1]:.2f} ml)",
                    f"most missed\n(median {med[2]:.0f} ml)"])
ax.set_ylim(0.6, 0.88)
ax.set_ylabel("D5 (patient mean)")
ax.set_title("Round-5 Dice by how much lesion the start missed (18 patients per group, VAL)")
ax.legend(frameon=False, fontsize=8, ncol=5, loc="upper right")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "val-d5-by-start-missed-volume.png")
plt.close(fig)

# 4. lesion-level safety
fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.6), dpi=150)
erased, persist = [], []
for n in SYSTEMS:
    rows = [r for r in jl(RUNS[n] / "trajectories.jsonl") if (r.get("scan_id"), r.get("style")) in KEYS
            and r.get("lesions") and r.get("cumulative_damage")]
    erased.append(sum(len(r["lesions"]["initial_lesion_erasure_lesions"]) for r in rows))
    persist.append(sum(r["cumulative_damage"]["damage_persistent_d5_ml"] for r in rows))
for ax, ys, title in ((axes[0], erased, "lesions detected at the start\nand later erased (count)"),
                      (axes[1], persist, "wrong edits still present\nat round 5 (ml)")):
    ax.bar(range(len(SYSTEMS)), ys, color=[COLOR[n] for n in SYSTEMS])
    for i, y in enumerate(ys):
        ax.text(i, y, f"{y:.0f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(SYSTEMS)))
    ax.set_xticklabels([LABEL[n] for n in SYSTEMS], fontsize=8)
    ax.set_title(title, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
fig.suptitle("K is safer: far fewer lesions erased by remove strokes (VAL, 99 scans)", fontsize=10)
fig.tight_layout()
fig.savefig(OUT / "val-lesion-safety.png")
plt.close(fig)
print("figures written:", sorted(p.name for p in OUT.glob("val-*.png")))
