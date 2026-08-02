"""Self-check: tinh lai doc lap tu CSV da luu, khong dung lai bien trong bo nho."""
import numpy as np, pandas as pd
from scipy import stats
ok=True
p=pd.read_csv("panel.csv.gz",parse_dates=["d"])
assert (p.rating<=3).all() and (p.liq>=3e9).all(), "cong rating/liq bi ho"
print(f"[1] cong rating<=3 & liq>=3ty: OK ({len(p)} dong, {p.d.nunique()} thang, {p.ticker.nunique()} ma)")
# 2. IC tong the tinh lai tu dau tren panel (khong qua fm_*.csv)
r=[]
for d,g in p.groupby("d"):
    g=g[["ey_pct","fwd20"]].dropna()
    if len(g)>=20: r.append(stats.spearmanr(g.ey_pct,g.fwd20).statistic)
fm=pd.read_csv("fm_ey_pct_fwd20.csv")
d=abs(np.mean(r)-fm.ic.mean()); print(f"[2] IC tong the tinh lai {np.mean(r):+.4f} vs fm CSV {fm.ic.mean():+.4f} (lech {d:.6f})"); ok&= d<1e-9
# 3. forward return: kiem tra 3 ma ngau nhien vs panel_raw
raw=pd.read_csv("panel_raw.csv",parse_dates=["d"])
m=p.merge(raw[["d","ticker","Close","c20"]],on=["d","ticker"],suffixes=("","_r"))
e=(m.fwd20.dropna()-(m.c20_r/m.Close_r-1).loc[m.fwd20.dropna().index]).abs().max()
print(f"[3] fwd20 khop lai tu panel_raw: sai so max {e:.2e}"); ok&= e<1e-9
# 4. he so hieu chinh gia phai >=1 va giam dan theo thoi gian
f=(raw.Price/raw.Close); share_lt=(f<0.99).mean()
print(f"[4] F=Price/Close: {share_lt:.2%} dong <0.99 (chap nhan <1%: Price tho le/stale o vai ma UPCOM), "
      f"median 2014 {f[raw.d.dt.year==2014].median():.2f} > 2026 {f[raw.d.dt.year==2026].median():.2f}")
ok &= share_lt<0.01 and f[raw.d.dt.year==2014].median()>f[raw.d.dt.year==2026].median()
# 5. so thang moi state khop DT5G goc
st=pd.read_csv("dt5g.csv",parse_dates=["time"])
chk=p.groupby("d").state.first().reset_index().merge(st,left_on="d",right_on="time")
bad=(chk.state_x!=chk.state_y).sum(); print(f"[5] state trong panel khop dt5g_live: {bad} ngay lech"); ok&= bad==0
print("SELF-CHECK:", "PASS" if ok else "FAIL")
