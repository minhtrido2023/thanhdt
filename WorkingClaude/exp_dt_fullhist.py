# -*- coding: utf-8 -*-
"""Research-only: does heavier DT-commitment smoothing worsen crash DD?
Apply DT asym-commit gate (light/prod/heavy) to the Co Dien base (state_dvg, reliable
2011+) and evaluate pure-index per crisis window. No deploy."""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_state_timing import simulate_timing

def dt_asym(states, default_min, target_min):
    out=states.copy(); committed=states[0]; ps=states[0]; pr=1; out[0]=committed
    for t in range(1,len(states)):
        s=states[t]
        if s==ps: pr+=1
        else: ps=s; pr=1
        if pr>=target_min.get(ps,default_min) and ps!=committed: committed=ps
        out[t]=committed
    return out
def ntrans(s): a=np.asarray(s); return int((a[1:]!=a[:-1]).sum())

m=pd.read_csv("data/vnindex_5state_intermediate.csv"); m["time"]=pd.to_datetime(m["time"])
m=m[m["time"]>="2011-01-01"].reset_index(drop=True)
dvg=m["state_dvg"].values.astype(int)

VARIANTS={
 "raw (no DT)":   None,
 "DT light 5/15": (5,{1:15,5:15}),
 "DT prod 10/25": (10,{1:25,5:25}),
 "DT heavy 15/30":(15,{1:30,5:25}),
}
WINDOWS={
 "FULL 2011-now": ("2011-01-01", None),
 "2011 inflation":("2011-01-01","2012-01-31"),
 "2018 selloff":  ("2018-04-01","2019-01-31"),
 "2020 COVID":    ("2020-01-01","2020-06-30"),
 "2022 rate/bond":("2022-04-01","2022-12-31"),
 "2025 tariff":   ("2025-03-01","2025-08-31"),
}
rows={}
for vname,p in VARIANTS.items():
    st = dvg.copy() if p is None else dt_asym(dvg, p[0], p[1])
    df=pd.DataFrame({"time":m["time"].dt.strftime("%Y-%m-%d"),"state":st})
    rows[vname]={"_trans":ntrans(st)}
    for wname,(ws,we) in WINDOWS.items():
        r=simulate_timing(df,start_date=ws,end_date=we)
        rows[vname][wname]=(r["cagr"],r["max_dd"])

print("="*100); print("DT-commitment smoothing vs CRASH DD — pure-index, Co Dien base, 2011+ (research only)"); print("="*100)
print(f"\n{'variant':16s}{'#trans':>7s}  " + "".join(f"{w:>17s}" for w in WINDOWS))
print(f"{'':16s}{'':>7s}  " + "".join(f"{'CAGR / MaxDD':>17s}" for _ in WINDOWS))
for vname in VARIANTS:
    line=f"{vname:16s}{rows[vname]['_trans']:>7d}  "
    for w in WINDOWS:
        c,d=rows[vname][w]; line+=f"{c*100:6.1f}%/{d*100:6.1f}% ".rjust(17)
    print(line)
print("\nNote: 2008 GFC NOT testable — all v3.4b-lineage & Co Dien bases warm up post-2009/2011.")
