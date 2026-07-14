# -*- coding: utf-8 -*-
"""P2: forward drawdown depth + recovery per name-event, div-strength vs not. Cluster by event."""
import os, sys
import numpy as np, pandas as pd
WORKDIR="/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0,WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq
P="mike/agents/Taylor/probe_capit_div/"
a = pd.read_csv(P+"all_name_events.csv")
out=[]
for d, g in a.groupby("date"):
    tk = ",".join(f"'{t}'" for t in g["ticker"])
    px = bq(f"""SELECT t.ticker, t.time, t.Close FROM tav2_bq.ticker t
WHERE t.ticker IN ({tk}) AND t.time BETWEEN DATE '{d}' AND DATE_ADD(DATE '{d}', INTERVAL 200 DAY)
ORDER BY t.ticker, t.time""")
    px["time"]=pd.to_datetime(px["time"])
    for _, r in g.iterrows():
        s = px[px.ticker==r.ticker].sort_values("time")["Close"].reset_index(drop=True)
        if len(s) < 40: continue
        p0 = s.iloc[0]
        for hor, n in (("3M",60), ("6M",120)):
            w = s.iloc[:min(n,len(s))]
            if len(w) < n*0.6: continue
            out.append(dict(date=d, ticker=r.ticker, pbz=r.pbz, dy3=r.dy3, hor=hor,
                            mdd=(w.min()/p0-1)*100,          # worst drawdown from entry
                            ret=(w.iloc[-1]/p0-1)*100,        # terminal return
                            maxup=(w.max()/p0-1)*100))        # recovery upside reached
o=pd.DataFrame(out); o.to_csv(P+"forward.csv", index=False)
print("name-event-horizons:", len(o))

for hor in ("3M","6M"):
    x = o[o.hor==hor].copy()
    x["hi_dy"] = x.dy3 > x.groupby("date").dy3.transform("median")   # within-event split = kills event/regime confound
    print(f"\n===== {hor}  (N events={x.date.nunique()}, name-events={len(x)}) =====")
    print(x.groupby("hi_dy")[["mdd","ret","maxup","pbz"]].agg(["mean","count"]).round(2).to_string())
    # PAIRED by event: within each event, mean(hi) - mean(lo). N = n events -> honest inference
    for m in ("mdd","ret","maxup"):
        pr = x.groupby(["date","hi_dy"])[m].mean().unstack()
        pr = pr.dropna()
        dif = pr[True]-pr[False]
        n=len(dif); t = dif.mean()/(dif.std(ddof=1)/np.sqrt(n)) if n>2 and dif.std(ddof=1)>0 else np.nan
        print(f"  paired-by-event {m:6s}: hi-lo = {dif.mean():+6.2f}pp  t={t:5.2f}  N_events={n}  wins={int((dif>0).sum())}/{n}")
