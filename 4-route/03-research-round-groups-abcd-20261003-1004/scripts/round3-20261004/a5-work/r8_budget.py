from datetime import datetime, timedelta
var=(4+3+2+1.5, 5+5+3+1.5)
groups=(7*var[0]+5, 7*var[1]+8)
execu=(1.5+1.5+2+2+2+4.7, 1.5+2+3+3+6+4.7)   # 4 arms five-round + fixed-state single-step + 0.5 three-style
cspec=(2+2+var[0], 3+3+var[1])
seedB=(4+3+6,5+5+9); seedC=(4+5+3+6,5+8+5+9)
mech=(8,14); test=(8,16); ens=(12,26)
def tot(*xs): return (sum(x[0] for x in xs), sum(x[1] for x in xs))
end=datetime(2026,10,30,23,59)
rows={"B single":tot(groups,execu,seedB,mech,test),"C single":tot(groups,execu,cspec,seedC,mech,test),
      "B +ens":tot(groups,execu,seedB,mech,test,ens),"C +ens":tot(groups,execu,cspec,seedC,mech,test,ens)}
for k,(lo,hi) in rows.items():
    print(k,"raw",round(lo,1),round(hi,1),"x1.25",round(lo*1.25,1),round(hi*1.25,1),"days",round(lo*1.25/24,1),round(hi*1.25/24,1),"latest",(end-timedelta(hours=hi*1.25)).strftime("%m-%d %H:%M"))
print("execu",execu)
