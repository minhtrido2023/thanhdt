"""1b — backfill 13 phiên thưa vào BẢN SAO 2 pkl (KHÔNG ghi đè data/*.pkl). Dùng đúng lagged_cache_patch.raw_basis
(= logic variant A của build_fixed_pkls.py). Ra: backfill13/{earnings_px,lagged_pos_ov}_bf13.pkl + MD5.txt.
Mode --apply (CHỈ SAU arch-review + user duyệt): backup .pre_bf13 rồi os.replace vào data/; từ chối nếu md5 canonical đã đổi so với lúc build."""
import sys, os, pickle, hashlib, shutil
import pandas as pd, numpy as np
WC="/home/trido/thanhdt/WorkingClaude"; R=f"{WC}/mike/agents/Taylor/research/book_regime_fit_20261110"; O=f"{R}/backfill13"
sys.path.insert(0,"/home/trido/thanhdt/wt-lagcache-1110/WorkingClaude")
from lagged_cache_patch import raw_basis
md5=lambda p: hashlib.md5(open(p,"rb").read()).hexdigest()
PX,OV=f"{WC}/data/earnings_px.pkl",f"{WC}/data/lagged_pos_ov.pkl"
if "--apply" in sys.argv:
    sys.exit("SUPERSEDED 2026-11-10 (job Taylor_20261110_103537): raw_basis cũ ghi giá SAI (VHM 08-06/TRC 09-15/DRI) — dùng ../backfill13_v2/build_backfill13.py")
    exp=dict(l.split()[::-1] for l in open(f"{O}/MD5.txt") if l.startswith(("canonical_",)) ) if False else None
    m={l.split()[0]:l.split()[1] for l in open(f"{O}/MD5.txt")}
    assert md5(PX)==m["canonical_earnings_px"] and md5(OV)==m["canonical_lagged_pos_ov"], "canonical đã đổi từ lúc build — build lại"
    for src,dst in [(f"{O}/earnings_px_bf13.pkl",PX),(f"{O}/lagged_pos_ov_bf13.pkl",OV)]:
        shutil.copy2(dst,dst+".pre_bf13"); shutil.copy2(src,dst+".tmp"); os.replace(dst+".tmp",dst); print("applied",dst)
    sys.exit(0)
px=pickle.load(open(PX,"rb")); px["time"]=pd.to_datetime(px["time"])
ov=pickle.load(open(OV,"rb")); ov["time"]=pd.to_datetime(ov["time"])
bq=pd.read_csv(f"{R}/data/lag_px_bq_fixed_2026H2.csv",parse_dates=["time"])
cnt=px.groupby("time").ticker.nunique()
gap=sorted(d for d in cnt.index if d>=pd.Timestamp("2026-06-01") and cnt[d]<50 and d.weekday()<5)
gap=[d for d in gap if d in set(bq.time.unique())]
print("gap:",[str(d.date()) for d in gap]); assert len(gap)==13
a=raw_basis(bq,pd.Timestamp("2026-06-01")); a=a[a.time.isin(gap)]
newpx=a[["ticker","time"]].assign(Close=a.Close_raw)
newov=a[["ticker","time"]].assign(Open=a.Open_raw,Volume_3M_P50=a.Volume_3M_P50)
pxB=pd.concat([px[~px.time.isin(gap)],newpx],ignore_index=True).sort_values(["ticker","time"]).reset_index(drop=True)
ovB=pd.concat([ov[~ov.time.isin(gap)],newov],ignore_index=True).sort_values(["ticker","time"]).reset_index(drop=True)
for df in (pxB,ovB): df["time"]=df["time"].astype("datetime64[ns]")
pickle.dump(pxB,open(f"{O}/earnings_px_bf13.pkl","wb")); pickle.dump(ovB,open(f"{O}/lagged_pos_ov_bf13.pkl","wb"))
untouched=lambda o,n: o[~o.time.isin(gap)].reset_index(drop=True).equals(n[~n.time.isin(gap)].reset_index(drop=True))
print("rows px",len(px),"->",len(pxB),"| ov",len(ov),"->",len(ovB),"| non-gap rows unchanged: px",untouched(px,pxB),"ov",untouched(ov,ovB))
c=pxB.groupby("time").ticker.nunique(); print("min tickers/day weekdays since 06-01:",int(c["2026-06-01":][c["2026-06-01":].index.weekday<5].min()))
open(f"{O}/MD5.txt","w").write("\n".join(f"{k} {v}" for k,v in {"canonical_earnings_px":md5(PX),"canonical_lagged_pos_ov":md5(OV),
 "earnings_px_bf13":md5(f"{O}/earnings_px_bf13.pkl"),"lagged_pos_ov_bf13":md5(f"{O}/lagged_pos_ov_bf13.pkl")}.items())+"\n")
print(open(f"{O}/MD5.txt").read())
