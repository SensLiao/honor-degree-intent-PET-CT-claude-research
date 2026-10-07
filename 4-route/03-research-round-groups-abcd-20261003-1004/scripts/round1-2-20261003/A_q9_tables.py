"""Print the markdown tables used in A-internal-evidence.md from the A_q*.json outputs (no new computation except
rounding and the proportional scaling already defined in A_q8_ranking.py).  VAL only."""
import json
from pathlib import Path

HERE = Path(__file__).parent


def load(name):
    return json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))


q1, q2, q3, q4, q5, q6, q7, q8 = (load(n) for n in ("A_q1_gap_structure", "A_q2_categories", "A_q3_damage", "A_q4_style",
                                                    "A_q5_continuation", "A_q6_throughput", "A_q7_other", "A_q8_ranking"))
f = q8["flat"]["scale"]
print("## T1 curves")
for a in ("flat", "N3", "oracle"):
    c = q1["curves_patient_mean"][a]
    print(f"| {a} | " + " | ".join(f"{x:.4f}" for x in c) + f" | {q1['nauc_patient_mean'][a]:.4f} |")
g = q1["gap_flat"]["per_round"]
print("| oracle − flat | " + " | ".join(f"{x:.4f}" for x in g) + " | |")
g = q1["gap_N3"]["per_round"]
print("| oracle − N3 | " + " | ".join(f"{x:.4f}" for x in g) + " | |")

print("## T2 worst patients")
cur = {w["patient"]: w for w in q1["worst_patients_flat"]}
split = {w["patient"]: w for w in q7["b_flat"]["worst12_patients"]}
for p in list(cur)[:10]:
    w, s = cur[p], split.get(p)
    print(f"| {p[5:13]} | {w['n_pos_scans']} | {s['mean_scan_gt_ml']:.1f} | " + " ".join(f"{x:.2f}" for x in w["arm_curve"])
          + f" | {w['oracle_curve'][5]:.2f} | {w['gap_d5']:.3f} | {s['damage_part']:.3f} | {s['unrepaired_part']:.3f} |")

print("## T3 categories flat")
cats = q2["flat"]["categories"]
for c in ["ADD <0.5 mL", "ADD 0.5-10 mL", "ADD >=10 mL", "REMOVE <0.5 mL", "REMOVE 0.5-10 mL", "REMOVE >=10 mL", "ALL"]:
    x = cats[c]
    print(f"| {c.replace('>=', '≥')} | {x['n']} ({x['share']*100:.1f}%) | {x['median_V_ml']:.2f} | {x['vol_weighted_recovery']:.3f} / {x['event_mean_recovery']:.3f}"
          f" | {x['mean_gain_actual']:+.4f} | {x['mean_gain_perfect']:+.4f} | {x['efficiency_sum_gain_over_sum_perfect']:.2f} | {x['dice_worse_rate']*100:.1f}%"
          f" | {x['damage_ml_per_ml_target']:.2f} |")
print("## T4 categories D5 points flat")
for c in ["ADD <0.5 mL", "ADD 0.5-10 mL", "ADD >=10 mL", "REMOVE <0.5 mL", "REMOVE 0.5-10 mL", "REMOVE >=10 mL", "ALL"]:
    x = cats[c]
    print(f"| {c.replace('>=', '≥')} | {x['D5pts_first_order']*100:.2f} | {x['D5pts_target_incomplete']*100:.2f} | {x['D5pts_damage']*100:.2f}"
          f" | {x['D5pts_collateral']*100:+.2f} | {x['D5pts_first_order_t0_exact']*100:.2f} | {x['D5pts_first_order']*f*100:.2f} |")
print("## T4b N3 categories D5 points")
for c in ["ADD <0.5 mL", "ADD 0.5-10 mL", "ADD >=10 mL", "REMOVE <0.5 mL", "REMOVE 0.5-10 mL", "REMOVE >=10 mL", "ALL"]:
    x = q2["N3"]["categories"][c]
    print(f"| {c.replace('>=', '≥')} | {x['event_mean_recovery']:.3f} | {x['zero_recovery_rate']*100:.1f}% | {x['D5pts_first_order']*100:.2f}"
          f" | {x['D5pts_target_incomplete']*100:.2f} | {x['D5pts_damage']*100:.2f} | {x['D5pts_first_order']*q8['N3']['scale']*100:.2f} |")
print("## T5 by round flat")
for t, x in q2["flat"]["by_round"].items():
    print(f"| {int(t)+1} | {x['gain_actual']:+.4f} | {x['gain_perfect']:+.4f} | {x['shortfall']:.4f} | {x['target']:.4f} | {x['damage']:.4f} | {x['collateral']:+.4f} |")
print("## T6 rings")
for k, v in q8["round1_distance_rings"].items():
    print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "volume_share"},
          {kk: round(vv, 3) for kk, vv in v["volume_share"].items()})
print("## T7 origin")
for arm in ("flat", "N3"):
    for tag, v in q2["target_origin_rounds1to4"][arm].items():
        print(arm, tag, v["n"], f"{v['share_of_rounds_1to4']*100:.1f}%", v["by_t"], f"{v['mean_gain_actual']:+.4f}")
print("## T8 damage by round flat")
for t, x in q3["flat"]["per_round"].items():
    print(f"| {int(t)+1} | {x['mean_fp_added_ml']:.2f} | {x['mean_tp_lost_ml']:.2f} | {x['share_with_damage']*100:.1f}% | {x['share_damage_exceeds_target_repair']*100:.1f}% | {x['D_pts_first_order_damage']*100:.2f} |")
print("## T9 style")
for arm in ("flat", "N3"):
    for st in ("centerline", "random", "boundary"):
        o = q4[arm][st]
        c = o["curve"]
        print(f"| {arm} {st} | {c[1]:.4f} | {c[2]:.4f} | {c[5]:.4f} | {o['first_order_target']*100:.2f} | {o['first_order_damage']*100:.2f} | {o['event_mean_recovery']:.3f}"
              f" | {o['damage_ml_per_ml_target']:.3f} | {o['patient_mean_new_error_ml']:.1f} | {o['dice_worse_rate']*100:.1f}% |")
for st in ("centerline", "random", "boundary"):
    print("oracle", st, [round(x, 4) for x in q4["oracle"][st]["curve"]])
print("## T10 continuation")
for lab in ("flat8k", "N3_8k"):
    o = q5[lab]
    for t, x in o["by_round"].items():
        print(f"| {lab} {int(t)+1} | {x['v1']['gain']:+.4f} | {x['8k']['gain']:+.4f} | {x['v1']['damage_cost_first_order']:.4f} | {x['8k']['damage_cost_first_order']:.4f}"
              f" | {x['v1']['worse_rate']*100:.1f}% | {x['8k']['worse_rate']*100:.1f}% |")
print("## T11 throughput")
for arm, o in q6.items():
    for ph, x in o["phases"].items():
        print(f"| {arm} {ph} | {x['sps']['median']:.2f} ({x['sps']['q25']:.2f}-{x['sps']['q75']:.2f}) | {x['dwf']['median']:.2f} ({x['dwf']['q25']:.2f}-{x['dwf']['q75']:.2f}) | {x['time_weighted_dw']:.2f} |")
