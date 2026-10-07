"""Per-transition table with volume accounting and the same-state perfect-repair counterfactual (VAL only).

For each rollout transition t (state t -> state t+1) of one arm:
  state t volumes TP, FP, FN from six_state.csv (TP = GT - FN, GT from the round-0 Dice identity, checked constant);
  actual moves from transitions.jsonl: target repair R (target_recovery_ml), collateral repair C (same_sign_other +
  opposite_sign), damage H (fp_added for ADD, tp_lost for REMOVE; both fields are used as stored);
  identity check: the next state's FP/FN must equal state t plus the moves;
  perfect same-state repair: the whole target V fixed, nothing else changes (what the oracle arm does);
  shortfall S = Dice(perfect) - Dice(actual next state), Shapley-split over three moves from the actual next state to the
  perfect one: finish the target (R -> V), drop collateral (C -> 0), drop damage (H -> 0).
Run as a script for the self-checks.
"""
import itertools

from A_common import arm_six, arm_transitions, gt_ml, dice, size_bin, STYLES

TOL_ML = 1e-6


def _apply(tp, fp, fn, sign, rec, coll_same, coll_opp, fp_add, tp_lost):
    """State after moves.  ADD (+) repairs FN (target and same-sign other); opposite-sign repair would remove FP.
    REMOVE (-) repairs FP; opposite-sign repair would add FN back to TP.  Damage: fp_added adds FP, tp_lost moves TP
    to FN."""
    if sign == "+":
        tp2 = tp + rec + coll_same - tp_lost
        fn2 = fn - rec - coll_same + tp_lost
        fp2 = fp - coll_opp + fp_add
    else:
        fp2 = fp - rec - coll_same + fp_add
        tp2 = tp + coll_opp - tp_lost
        fn2 = fn - coll_opp + tp_lost
    return tp2, fp2, fn2


def build(arm):
    d, pat, pos = arm_six(arm)
    tr = arm_transitions(arm)
    gts, rows = {}, []
    worst_gt = 0.0
    for k in d:
        if not pos[k]:
            continue
        g = gt_ml(d[k][0])
        gts[k] = g
        for r in range(1, 6):
            g2 = gt_ml(d[k][r])
            if g2 is not None:
                worst_gt = max(worst_gt, abs(g2 - g) / max(g, 1e-9))
    worst_fp = worst_fn = 0.0
    for (scan, style, t), x in tr.items():
        k = (scan, style)
        a, b = d[k][t], d[k][t + 1]
        row = {"scan": scan, "style": style, "t": t, "patient": pat[k], "pos": pos[k], "sign": x["sign"],
               "no_stroke": bool(x.get("no_stroke")), "V": float(x["target_volume_ml"] or 0.0),
               "R": float(x["target_recovery_ml"] or 0.0), "C_same": float(x["same_sign_other_repair_ml"] or 0.0),
               "C_opp": float(x["opposite_sign_repair_ml"] or 0.0), "fp_add": float(x["fp_added_ml"] or 0.0),
               "tp_lost": float(x["tp_lost_ml"] or 0.0), "flip": float(x["flip_ml"] or 0.0),
               "fp0": a["fp_ml"], "fn0": a["fn_ml"], "fp1": b["fp_ml"], "fn1": b["fn_ml"],
               "d0": a["dice"], "d1": b["dice"]}
        # identity check (all scans, Dice-independent)
        if not row["no_stroke"]:
            if row["sign"] == "+":
                fn_pred = row["fn0"] - row["R"] - row["C_same"] + row["tp_lost"]
                fp_pred = row["fp0"] - row["C_opp"] + row["fp_add"]
            else:
                fp_pred = row["fp0"] - row["R"] - row["C_same"] + row["fp_add"]
                fn_pred = row["fn0"] - row["C_opp"] + row["tp_lost"]
            worst_fp = max(worst_fp, abs(fp_pred - row["fp1"]))
            worst_fn = max(worst_fn, abs(fn_pred - row["fn1"]))
        if pos[k] and not row["no_stroke"]:
            g = gts[k]
            tp = g - row["fn0"]
            moves = {"target": (row["R"], row["V"]), "collateral": (1.0, 0.0), "damage": (1.0, 0.0)}

            def dice_with(finish, drop_c, drop_h):
                rec = row["V"] if finish else row["R"]
                cs = 0.0 if drop_c else row["C_same"]
                co = 0.0 if drop_c else row["C_opp"]
                fa = 0.0 if drop_h else row["fp_add"]
                tl = 0.0 if drop_h else row["tp_lost"]
                return dice(*_apply(tp, row["fp0"], row["fn0"], row["sign"], rec, cs, co, fa, tl))

            d_act = dice_with(False, False, False)
            d_perf = dice_with(True, True, True)
            row["d_perfect"] = d_perf
            row["gain_actual"] = row["d1"] - row["d0"]
            row["gain_perfect"] = d_perf - row["d0"]
            row["shortfall"] = d_perf - row["d1"]
            row["recon_err"] = abs(d_act - row["d1"])
            players = ("target", "collateral", "damage")
            shap = {p: 0.0 for p in players}
            for perm in itertools.permutations(players):
                state = {"target": False, "collateral": False, "damage": False}
                prev = dice_with(False, False, False)
                for p in perm:
                    state[p] = True
                    cur = dice_with(state["target"], state["collateral"], state["damage"])
                    shap[p] += (cur - prev) / 6.0
                    prev = cur
            row["S_target"], row["S_collateral"], row["S_damage"] = shap["target"], shap["collateral"], shap["damage"]
            row["size"] = size_bin(row["V"])
            row["cat"] = f"{'ADD' if row['sign'] == '+' else 'REMOVE'} {row['size']} mL"
        rows.append(row)
    checks = {"gt_constancy_max_rel": worst_gt, "identity_max_abs_fp_ml": worst_fp, "identity_max_abs_fn_ml": worst_fn,
              "dice_reconstruction_max_abs": max((r["recon_err"] for r in rows if "recon_err" in r), default=0.0)}
    return rows, checks, gts


if __name__ == "__main__":
    import collections
    base = {}
    for arm in ("flat", "N3", "oracle", "noop"):
        rows, checks, _ = build(arm)
        base[arm] = {(r["scan"], r["style"], r["t"]): r for r in rows}
        print(arm, "transitions", len(rows), "checks", {k: f"{v:.2e}" for k, v in checks.items()})
        cnt = collections.Counter((r["C_opp"] > 0, r["sign"]) for r in rows)
        print("   opposite-sign repair > 0 by sign:", dict(cnt))
        dmg = collections.Counter((r["sign"], r["fp_add"] > 0, r["tp_lost"] > 0) for r in rows if not r["no_stroke"])
        print("   (sign, fp_added>0, tp_lost>0):", dict(dmg))
    # round-0 targets identical across arms?
    same = diff = 0
    for k, r in base["flat"].items():
        if k[2] != 0:
            continue
        o = base["oracle"][k]
        if r["sign"] == o["sign"] and abs(r["V"] - o["V"]) < TOL_ML and r["no_stroke"] == o["no_stroke"]:
            same += 1
        else:
            diff += 1
    print("transition-0 target identical flat vs oracle:", same, "different:", diff)
    # oracle repairs exactly the target and nothing else?
    o_rows = [r for r in base["oracle"].values() if not r["no_stroke"]]
    print("oracle: max |V-R|", max(abs(r["V"] - r["R"]) for r in o_rows), "max collateral",
          max(r["C_same"] + r["C_opp"] for r in o_rows), "max damage", max(r["fp_add"] + r["tp_lost"] for r in o_rows))
    print("oracle: max |shortfall| on positive scans", max(abs(r["shortfall"]) for r in o_rows if r["pos"]))
    # noop: does the robot re-stroke the same target every round?
    n_rows = base["noop"]
    same_target = sum(1 for (s, st, t), r in n_rows.items() if t > 0 and r["sign"] == n_rows[(s, st, 0)]["sign"]
                      and abs(r["V"] - n_rows[(s, st, 0)]["V"]) < TOL_ML)
    print("noop: transitions t>0 with the same target as t0:", same_target, "of", sum(1 for k in n_rows if k[2] > 0))
