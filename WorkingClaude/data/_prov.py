import pandas as pd, numpy as np, os
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
def ld(f):
    d=pd.read_csv(f); d["time"]=pd.to_datetime(d["time"]); return d[["time","state"]].rename(columns={"state":f})
canon=ld("data/vnindex_5state.csv")
files={"dt4_macro":"data/vnindex_5state_dt4_macro.csv","dt5g_live":"data/vnindex_5state_dt5g_live.csv","tinhte_hist":"data/vnindex_5state_history.csv"}
for nm,f in files.items():
    if not os.path.exists(f): print(f"{nm}: MISSING {f}"); continue
    o=ld(f); m=canon.merge(o,on="time",how="inner"); c1=m.columns[1]; c2=m.columns[2]
    diff=(m[c1]!=m[c2]).sum()
    print(f"canon(vnindex_5state) vs {nm:12s}: overlap={len(m)}  diffs={diff} ({diff/len(m)*100:.0f}%)  range {m['time'].min().date()}->{m['time'].max().date()}")
# also: what does canonical look like 2014-05 (easing window)?
print("\ncanon 2014-05-27:", canon[canon["time"]=="2014-05-27"]["data/vnindex_5state.csv"].values)
