from datetime import datetime, timedelta
# gap plan from 10-04 13:00
t = datetime(2026,10,4,13,0)
plan = [("R0 parent rollout",6),("seed2 40k parent",14.5),("soup quickVAL",1.5),("flip quickVAL",2.75),("start-model threestyle",4.7)]
for n,h in plan:
    t2 = t+timedelta(hours=h); print(f"{n:28s} {t:%m-%d %H:%M} -> {t2:%m-%d %H:%M}"); t=t2
print("40k at 1.25-1.35 s/step:", round(40000*1.25/3600,1), round(40000*1.35/3600,1))
var = (4+3+2+1.5, 5+5+3+1.5)
groups = (6*var[0]+5, 6*var[1]+8)
execu = (1.5+2+2+4.7, 1.5+3+3+4.7)
cspec = (2+var[0], 3+var[1])
seedB = (4+3+6, 5+5+9); seedC=(4+5+3+6, 5+8+5+9)
mech=(8,14); test=(8,16)
def tot(*xs): return (sum(x[0] for x in xs), sum(x[1] for x in xs))
B = tot(groups,execu,seedB,mech,test); C = tot(groups,execu,cspec,seedC,mech,test)
for name,v in [("B-final",B),("C-final",C)]:
    lo,hi=v; print(name,"raw",round(lo,1),round(hi,1),"x1.25",round(lo*1.25,1),round(hi*1.25,1),"days",round(lo*1.25/24,1),round(hi*1.25/24,1))
end = datetime(2026,10,30,23,59)
for name,v in [("B-final",B),("C-final",C)]:
    print(name,"latest start",(end-timedelta(hours=v[1]*1.25)).strftime("%m-%d %H:%M"))
for d in [(10,15),(10,18),(10,25)]:
    s = datetime(2026,d[0],d[1],18,0); print(d, "hours to 10-30 24:00", round((end-s).total_seconds()/3600,1))
