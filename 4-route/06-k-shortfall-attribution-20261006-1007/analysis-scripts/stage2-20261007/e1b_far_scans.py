"""Which scans carry K1's far T repair in rounds 2-5 (add strokes beyond 30/60 mm), and what v1/K2 did there. VAL."""
from b0_load import load

data = {n: load(n) for n in ("v1flat", "K1", "K2")}
six, tr, rem = data["K1"]
rows = []
for (s, st, k), by_r in rem.items():
    r0 = tr.get((s, st, k))
    if k >= 1 and r0 and r0.get("sign") == "+" and 30.0 in by_r:
        rows.append((by_r[30.0].get("remote_target_repair_ml") or 0.0, by_r.get(60.0, {}).get("remote_target_repair_ml") or 0.0,
                     by_r[30.0].get("remote_new_error_ml") or 0.0, s, st, k, r0.get("target_volume_ml"), r0.get("target_recovery_ml")))
rows.sort(reverse=True)
print("K1 add strokes, rounds 2-5, largest T repair beyond 30 mm: T>30 T>60 new>30 scan round |T| T-fixed ; Dice of K1/v1/K2 at that scan D0->D5")
for t30, t60, e30, s, st, k, tv, trec in rows[:10]:
    d = {n: data[n][0][(s, st)]["dice"] for n in data}
    print(f"{t30:7.1f} {t60:7.1f} {e30:7.1f} {s} r{k+1} |T|={tv:.1f} fixed={trec:.1f}  "
          + "  ".join(f"{n}:{d[n][0]:.3f}->{d[n][5]:.3f}" for n in d))
print("share of the K1 total from the top 3 scans:", round(sum(r[0] for r in rows[:3]) / max(1e-9, sum(r[0] for r in rows)), 3))
