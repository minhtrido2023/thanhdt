"""Spot-check độc lập (đường code khác build_events.py): tính lại CAR[-1,+1], fwdx_3m, mdd_3m, rating as-of cho 5 sự kiện ngẫu nhiên từ parquet năm thô."""
import numpy as np, pandas as pd
C="/home/trido/thanhdt/WorkingClaude/data/bq_cache"
ev=pd.read_csv("events_features.csv.gz",parse_dates=["rd","t_s"]); ev=ev[ev.in_universe & ev.mdd_3m.notna()].sample(5,random_state=7)
r8=pd.read_parquet(f"{C}/fa_ratings_8l.parquet"); r8["time"]=pd.to_datetime(r8.time)
bad=0
for e in ev.itertuples():
    yrs=[e.rd.year-1,e.rd.year,e.rd.year+1]
    d=pd.concat([pd.read_parquet(f"{C}/ticker/{y}.parquet",columns=["time","ticker","Close"],filters=[("ticker","in",[e.ticker,"VNINDEX"])]) for y in yrs if y<=2026])
    d["time"]=pd.to_datetime(d.time); p=d.pivot_table(index="time",columns="ticker",values="Close").sort_index()
    i0=p.index.searchsorted(e.rd); s=i0+1
    r=p.pct_change(); car=(r[e.ticker]-r["VNINDEX"]).iloc[i0-1:i0+2].sum()
    fx=p[e.ticker].iloc[s+63]/p[e.ticker].iloc[s]-1-(p["VNINDEX"].iloc[s+63]/p["VNINDEX"].iloc[s]-1)
    path=p[e.ticker].iloc[s:s+64].ffill(); mdd=(path/path.cummax()-1).min()
    rr=r8[(r8.ticker==e.ticker)&(r8.time<=p.index[s])].sort_values("time").rating.iloc[-1]
    ok=np.allclose([car,fx,mdd],[e.car_m1p1,e.fwdx_3m,e.mdd_3m],atol=1e-9) and rr==e.rating
    bad+=not ok
    print(e.ticker,e.quarter,f"car {car:.6f}/{e.car_m1p1:.6f} fwdx3m {fx:.6f}/{e.fwdx_3m:.6f} mdd {mdd:.6f}/{e.mdd_3m:.6f} rating {rr}/{e.rating}", "OK" if ok else "MISMATCH")
print("SELFCHECK", "PASS" if bad==0 else f"FAIL {bad}")
