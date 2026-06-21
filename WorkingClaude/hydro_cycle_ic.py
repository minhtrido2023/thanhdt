#!/usr/bin/env python3
"""hydro_cycle_ic.py — test the HYDROLOGY mean-reversion (user): drought year → output/profit down →
cheap → rain returns → recovery. Proxy drought by Revenue_YoY (hydro revenue ∝ generation ∝ rainfall).
Hypothesis: buy in DROUGHT (rev down sharply) → higher forward returns when output normalizes."""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
fin=pd.read_csv(os.path.join(W,"data","hydro_fin_panel.csv")); px=pd.read_csv(os.path.join(W,"data","power_price_panel.csv"))
fin["time"]=pd.to_datetime(fin["time"]); px["time"]=pd.to_datetime(px["time"]); px=px.sort_values("time")
def asof(tk,dt):
    s=px[(px.ticker==tk)&(px.time>=dt)]; return s.iloc[0]["Close"] if len(s) else np.nan
rows=[]
for _,r in fin.iterrows():
    tk=r["ticker"]; d0=r["time"]+pd.Timedelta(days=45)
    p0=asof(tk,d0)
    if not np.isfinite(p0): continue
    p1=asof(tk,d0+pd.Timedelta(days=365)); p2=asof(tk,d0+pd.Timedelta(days=730))
    ry=r["rev_yoy"]
    bucket=("1_drought(rev<-15%)" if ry<-0.15 else "2_dry(-15..-5%)" if ry<-0.05 else
            "3_normal(-5..+15%)" if ry<0.15 else "4_flood(rev>+15%)")
    rows.append(dict(ticker=tk,time=r["time"],rev_yoy=ry,pb=r["pb"],bucket=bucket,
        f1=(p1/p0-1) if np.isfinite(p1) else np.nan, f2=(p2/p0-1) if np.isfinite(p2) else np.nan))
d=pd.DataFrame(rows)
print(f"hydro panel: {len(d)} obs, {d.ticker.nunique()} hydro names {d.time.dt.year.min()}-{d.time.dt.year.max()}\n")
print("=== forward returns by hydrology bucket (rev_yoy = rainfall/output proxy) ===")
print(f"{'bucket':<22}{'n':>5}{'1Y med':>9}{'1Y mean':>9}{'2Y med':>9}{'2Y mean':>9}{'2Y win':>8}")
for b in sorted(d.bucket.unique()):
    g=d[d.bucket==b]; f1=g["f1"].dropna(); f2=g["f2"].dropna()
    print(f"{b:<22}{len(g):>5}{f1.median()*100:>8.1f}%{f1.mean()*100:>8.1f}%{f2.median()*100:>8.1f}%{f2.mean()*100:>8.1f}%{(f2>0).mean()*100:>7.0f}%")
print("  [hypothesis: drought (rev down) = depressed/cheap → HIGHER forward when rain returns]")
print()
# drought + cheap PB (the full contrarian)
dr=d[d.bucket.str.startswith(('1_','2_'))]
print("=== drought/dry × PB (contrarian: buy drought when also cheap) ===")
for lab,sub in [("PB<1.2",dr[dr.pb<1.2]),("PB>=1.2",dr[dr.pb>=1.2])]:
    f2=sub["f2"].dropna()
    if len(f2)>=5: print(f"  drought&dry {lab:<8} n={len(sub):>3}  2Y med {f2.median()*100:+.1f}% mean {f2.mean()*100:+.1f}% win {(f2>0).mean()*100:.0f}%")
