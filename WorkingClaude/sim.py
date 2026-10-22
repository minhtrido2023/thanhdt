import csv,sys,collections
sys.path.insert(0,"/home/trido/thanhdt/WorkingClaude/wt-livermore-live-20261022/bin")
import livermore_trigger_check as T
rows=list(csv.DictReader(open(sys.argv[1])))
dates=[r["time"] for r in rows]; closes=[float(r["Close"]) for r in rows]
last={}; runs=collections.Counter(); rawdays=collections.Counter(); nd=collections.Counter()
for i in range(400,len(closes)):
    ks=T.price_kinds(closes[:i+1]); y=dates[i][:4]; nd[y]+=1
    if ks: rawdays[y]+=1
    ok=[k for k in ks if k not in last or i-last[k]>=T.COOLDOWN]
    if ok:
        runs[y]+=1
        for k in ok: last[k]=i
for y in sorted(nd): print(y, "days",nd[y],"raw_trigger_days",rawdays[y],"runs",runs[y])
print("total runs",sum(runs.values()),"over years",len(nd))
