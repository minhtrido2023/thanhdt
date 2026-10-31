# β HPG vs VNINDEX (BQ tav2_bq.ticker, Close điều chỉnh), tuần (thứ Sáu), 2y & 3y; Blume; ADV.
import pandas as pd, numpy as np
d=pd.read_csv('gaps_hpg_px.csv',parse_dates=['time'])
px=d.pivot(index='time',columns='ticker',values='Close').sort_index().dropna()
end=px.index.max()
out=[]
for yrs in (2,3):
    s=px[px.index> end-pd.DateOffset(years=yrs)]
    w=s.resample('W-FRI').last().pct_change().dropna()
    cov=np.cov(w.HPG,w.VNINDEX); b=cov[0,1]/cov[1,1]
    n=len(w); resid=w.HPG-b*w.VNINDEX; se=np.std(resid,ddof=2)/ (np.std(w.VNINDEX,ddof=1)*np.sqrt(n-1))
    r=np.corrcoef(w.HPG,w.VNINDEX)[0,1]
    out.append((yrs,n,b,se,0.67*b+0.33,r))
    print(f"{yrs}y weekly n={n} beta={b:.3f} se={se:.3f} 95%CI=[{b-1.96*se:.2f},{b+1.96*se:.2f}] blume={0.67*b+0.33:.3f} corr={r:.2f}")
# daily 2y for reference
s=px[px.index> end-pd.DateOffset(years=2)].pct_change().dropna()
c=np.cov(s.HPG,s.VNINDEX); print(f"2y daily beta={c[0,1]/c[1,1]:.3f} n={len(s)}")
h=d[d.ticker=='HPG'].sort_values('time').set_index('time')
tv=(h.Price*h.Volume)/1e9
for lab,st in [('3M',end-pd.DateOffset(months=3)),('10/2026','2026-10-01'),('6M',end-pd.DateOffset(months=6))]:
    x=tv[tv.index>pd.Timestamp(st)]; print(f"ADV {lab}: mean {x.mean():.0f} ty, median {x.median():.0f} ty, n={len(x)}")
# Ke ranges
for b in sorted({round(o[4],2) for o in out}|{1.1}):
    print(f"beta {b}: Ke = 6.75% + b*ERP -> ERP5.0: {6.75+b*5.0:.2f}%  ERP6.1: {6.75+b*6.1:.2f}%")
