from datetime import datetime, timedelta
# hours (lo, hi) on z390, estimates
items = {
 "groups x5 (8k B-type 4-5h + quickVAL 1.5h)": (5*(4+1.5), 5*(5+1.5)),
 "reference quickVAL 0.5 on final": (1.5, 1.5),
 "C-specific (zero channel quickVAL + same-budget control)": (1.5+4+1.5, 3+5+1.5),
 "seed2 three-style VAL (seed2 trained in main phase)": (6, 9),
 "mechanism 101+397 + policy-shift quickVAL x4": (2+4*1.5, 2+4*3),
 "final TEST": (8, 16),
}
noC = {k:v for k,v in items.items() if not k.startswith("C-")}
def tot(d): return sum(v[0] for v in d.values()), sum(v[1] for v in d.values())
for name, d in [("with C", items), ("without C", noC)]:
    lo, hi = tot(d)
    print(name, "raw", lo, hi, "with 25%", round(lo*1.25,1), round(hi*1.25,1), "days", round(lo*1.25/24,2), round(hi*1.25/24,2))
end = datetime(2026,10,30,23,59)
for name, d in [("with C", items), ("without C", noC)]:
    lo, hi = tot(d)
    for extra_label, extra in [("seed2 pretrained",0),("seed2 not pretrained",(7.5+14.5)/2)]:
        need = (hi+extra)*1.25
        print(name, extra_label, "latest start", (end - timedelta(hours=need)).strftime("%m-%d %H:%M"), "need h", round(need,1))
# A6000 offload: seed2 three-style + policy/mechanism moved off z390
for name, d in [("with C", items), ("without C", noC)]:
    lo, hi = tot(d)
    off = 9 + 14
    need = (hi-off)*1.25
    print(name, "A6000 offload latest start", (end - timedelta(hours=need)).strftime("%m-%d %H:%M"), round(need,1))
