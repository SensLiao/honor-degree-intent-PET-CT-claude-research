from datetime import datetime, timedelta
var=(4+3+2+1.5, 5+5+3+1.5)            # one training variant: 8k + relabel + quick sel + quick 0.5
groups=(7*var[0]+5, 7*var[1]+8)        # 7 training variants + STATIC refit
execu=(1.5+2+2+4.7, 1.5+3+3+4.7)       # 0.5 / range-only / full quick + 0.5 three-style
cspec=(2+2+var[0], 3+3+var[1])         # zero channel + no fifth family + same-budget control
seedB=(4+3+6, 5+5+9); seedC=(4+5+3+6, 5+8+5+9)
mech=(8,14); test=(8,16)
def tot(*xs): return (sum(x[0] for x in xs), sum(x[1] for x in xs))
B=tot(groups,execu,seedB,mech,test); C=tot(groups,execu,cspec,seedC,mech,test)
end=datetime(2026,10,30,23,59)
for n,v in [("B",B),("C",C)]:
    lo,hi=v; print(n,"raw",round(lo,1),round(hi,1),"x1.25",round(lo*1.25),round(hi*1.25),"days",round(lo*1.25/24,1),round(hi*1.25/24,1),"latest",(end-timedelta(hours=hi*1.25)).strftime("%m-%d %H:%M"))
print("groups",groups,"execu",execu,"cspec",cspec)
