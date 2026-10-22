import pandas as pd, numpy as np, random, json
SEED=20261022
px=pd.read_csv("vnindex_ohlcv.csv",parse_dates=["time"]).sort_values("time").reset_index(drop=True)
tr=pd.read_csv("dt5g_transitions.csv",parse_dates=["time"])
tr["d"]=(tr.state-tr.prev).abs()
big=tr[tr.d>=2].reset_index(drop=True)
rng=random.Random(SEED)
idx_of={t:i for i,t in enumerate(px.time)}
def pos(t): return int(px.time.searchsorted(t))
sel=sorted(rng.sample(range(len(big)),8))
trans=big.iloc[sel]
tpos=[pos(t) for t in tr.time]
cases=[]
for _,r in trans.iterrows():
    cases.append(dict(kind="transition",date=r.time,state=int(r.state),prev=int(r.prev)))
lo,hi=pos(pd.Timestamp("2014-06-01")),pos(pd.Timestamp("2026-09-15"))
chosen=[pos(c["date"]) for c in cases]
cand=[i for i in range(lo,hi) if min(abs(i-p) for p in tpos)>=40]
rng.shuffle(cand)
ctrl=[]
for i in cand:
    if all(abs(i-p)>=40 for p in chosen+ctrl):
        ctrl.append(i)
    if len(ctrl)==8: break
for i in ctrl: cases.append(dict(kind="control",date=px.time[i],state=None,prev=None))
order=list(range(16)); rng.shuffle(order)
truth=[]
import os; os.makedirs("cases",exist_ok=True)
for n,k in enumerate(order,1):
    c=cases[k]; D=pos(c["date"]); lab=f"C{n:02d}"
    w=px.iloc[D-399:D+1].copy()
    base=w.Close.iloc[0]; vm=w.Volume.median()
    out=pd.DataFrame({"session":range(400),"open":(w.Open.values/base*100).round(2),"high":(w.High.values/base*100).round(2),
      "low":(w.Low.values/base*100).round(2),"close":(w.Close.values/base*100).round(2),"vol_rel":(w.Volume.values/vm).round(2)})
    out.to_csv(f"cases/{lab}.csv",index=False)
    fwd=px.Close[D+20]/px.Close[D]-1; trail=px.Close[D]/px.Close[D-20]-1
    truth.append(dict(label=lab,kind=c["kind"],date=str(c["date"].date()),state=c["state"],prev=c["prev"],
      fwd20=float(fwd),up=int(fwd>0),trail20=float(trail),b1_up=int(trail>0),
      b2_up=(None if c["state"] is None else int(c["state"]>c["prev"]))))
json.dump(truth,open("SEALED_truth.json","w"),indent=1,default=str)
print("built",len(truth),"cases; labels:",[t["label"] for t in truth])
