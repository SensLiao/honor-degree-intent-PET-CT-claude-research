from datetime import datetime, timedelta
wd = "一二三四五六日"
for d in range(4, 32):
    t = datetime(2026, 10, d)
    print(t.strftime("%m-%d"), "周" + wd[t.weekday()], end="; ")
print()
def at(start, hours):
    return (start + timedelta(hours=hours)).strftime("%m-%d %H:%M")
# UAM, from 10-03 23:54 snapshot
s1 = datetime(2026,10,3,23,54); s0 = datetime(2026,10,3,23,53)
for label, s2, s1lo, s1hi, val in [("normal",315,154,193,3),("slow",1136,555,695,8)]:
    s2b = 1161 if label=="slow" else 315
    g1_f0 = 254*s2/3600 + val
    g0_f1 = 377*s2b/3600 + val
    fold_lo = (1000*s1lo + 500*s2)/3600 + val
    fold_hi = (1000*s1hi + 500*s2)/3600 + val
    print(label, "GPU1 fold0 done", at(s1, g1_f0), "| fold2", at(s1, g1_f0+fold_lo), "~", at(s1, g1_f0+fold_hi),
          "| fold4", at(s1, g1_f0+2*fold_lo), "~", at(s1, g1_f0+2*fold_hi))
    print(label, "GPU0 fold1 done", at(s0, g0_f1), "| fold3", at(s0, g0_f1+fold_lo), "~", at(s0, g0_f1+fold_hi))
    print(label, "per-fold hours", round(fold_lo,1), round(fold_hi,1), "days", round(fold_lo/24,2), round(fold_hi/24,2))
# 2S-ICR on 5090 from 10-03 23:48 (epoch 137 done)
s = datetime(2026,10,3,23,48)
f2 = 163*630/3600 + 1.5
fold = 9.2 + 300*630/3600 + 1.5
print("2S fold2 done", at(s,f2), "fold3", at(s,f2+fold), "fold4", at(s,f2+2*fold), "per fold h", round(fold,1))
# IKIM organ labels 459 cases at 1489-3527 s/case single worker
print("IKIM labels days", round(459*1489/86400,1), round(459*3527/86400,1))
# eval unit costs: inferences x 10.4-11.5 s
for name,n in [("quickVAL",99*5),("threestyle",99*15),("TRAIN rollout",407*5),("TEST pass",91*5)]:
    print(name, n, round(n*10.4/3600,2), round(n*11.5/3600,2))
