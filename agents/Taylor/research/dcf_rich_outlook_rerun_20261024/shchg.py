"""sh_chg_minmax.csv: max/min OShares PIT (fiinprox) trong [d0-30, d0+30] kể cả mức ngay trước cửa sổ; >2% = 465/7510."""
import pandas as pd, numpy as np
d=pd.read_csv("panel_aug.csv",parse_dates=["d0"]); d=d[d.ok & d.mos.notna()]
sh=pd.read_csv("/home/trido/thanhdt/WorkingClaude/mike/data/fiinprox_oshares_pit_20260926.csv",parse_dates=["date"]).sort_values(["ticker","date"])
g={k:v for k,v in sh.groupby("ticker")}
mm=[]
for r in d.itertuples():
    s=g[r.ticker]; w=s[(s.date>=r.d0-pd.Timedelta(days=30))&(s.date<=r.d0+pd.Timedelta(days=30))]
    b=s[s.date<=r.d0-pd.Timedelta(days=30)]
    v=pd.concat([b.shares.tail(1),w.shares])
    mm.append(v.max()/v.min()-1 if len(v) else np.nan)
d["mm"]=mm; d[["ticker","quarter","mm"]].to_csv("sh_chg_minmax.csv",index=False); print((d.mm>0.02).sum())
