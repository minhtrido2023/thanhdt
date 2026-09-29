# -*- coding: utf-8 -*-
"""Kiem tra DO PHU du lieu THAT truoc khi cam ket chan CF-quality (yeu cau tuong minh cua dispatch)."""
import os, sys, bisect
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike/agents/Taylor/research/custom30v_selector_20260909")
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
os.environ.setdefault("BQ_CACHE_THREADS", "1")
from simulate_holistic_nav import bq
LOG=[]
def rep(t): print(t); LOG.append(t)

mem = pd.read_csv(f"{OUT}/members.csv", parse_dates=["rebal_date"])
P = pd.read_csv(f"{OUT}/pool_diag.csv", parse_dates=["rebal"])
rebs = sorted(mem.rebal_date.unique())
_in = ",".join(f"DATE '{pd.Timestamp(x).date()}'" for x in rebs)

# CF_OA_3Y as-of Release_Date (PIT), + OShares + gia THO tai ngay rebal -> cfy3 = (CF_OA_3Y/3)/mcap
f = bq("""SELECT ticker, time, Release_Date, CF_OA_3Y, CF_OA_5Y, CF_OA_P0, OShares
FROM tav2_bq.ticker_financial WHERE time <= DATE '2026-06-19'""")
f["eff"] = pd.to_datetime(f["Release_Date"]).fillna(pd.to_datetime(f["time"]) + pd.Timedelta(days=45))
f = f.sort_values("eff")
hist = {tk: (list(g["eff"]), list(zip(g["CF_OA_3Y"], g["CF_OA_5Y"], g["OShares"])))
        for tk, g in f.groupby("ticker")}
px = bq(f"""SELECT ticker, time, COALESCE(Price, Close) AS pxw FROM tav2_bq.ticker
WHERE time IN ({_in}) AND COALESCE(Price, Close) IS NOT NULL""")
px["time"] = pd.to_datetime(px["time"])
pxm = {(r.ticker, r.time): float(r.pxw) for r in px.itertuples()}
def cf_asof(tk, d):
    e = hist.get(tk)
    if not e: return None
    i = bisect.bisect_right(e[0], pd.Timestamp(d)) - 1
    return e[1][i] if i >= 0 else None

vp = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"], usecols=["ticker","time","route"])
vp["qstart"] = vp["time"].dt.to_period("Q").dt.start_time
rt = vp.dropna(subset=["route"]).sort_values("time").groupby(["ticker","qstart"])["route"].last()
rh = {tk:(list(g.index.get_level_values(1)),list(g.values)) for tk,g in rt.groupby(level=0)}
def route_asof(tk,q):
    e=rh.get(tk)
    if not e: return "UNKNOWN"
    i=bisect.bisect_right(e[0],pd.Timestamp(q))-1
    return e[1][i] if i>=0 else e[1][0]
FIN={"BANK","INSURANCE","SECURITIES"}

rows=[]
for d, g in mem.groupby("rebal_date"):
    q = pd.Timestamp(d).to_period("Q").start_time
    for tk in g.ticker:
        c = cf_asof(tk, d); p = pxm.get((tk, pd.Timestamp(d)))
        cf3 = cf5 = osh = np.nan
        if c is not None: cf3, cf5, osh = c
        mc = p*osh if (p and pd.notna(osh)) else np.nan
        rows.append(dict(rebal=d, ticker=tk, route=route_asof(tk,q),
                         has_cf3=pd.notna(cf3), has_cf5=pd.notna(cf5), has_mc=pd.notna(mc),
                         cfy3=(cf3/3.0/mc) if (pd.notna(cf3) and pd.notna(mc) and mc>0) else np.nan))
C = pd.DataFrame(rows)
C["is_fin"] = C.route.isin(FIN)
rep("## DO PHU CF_OA_3Y (as-of Release_Date, PIT) tren 30 ten trong ro moi ky")
rep(f"  tong {len(C)} cap (ten,ky). CF_OA_3Y co gia tri: {100*C.has_cf3.mean():.1f}% | "
    f"CF_OA_5Y: {100*C.has_cf5.mean():.1f}% | mcap tinh duoc: {100*C.has_mc.mean():.1f}% | "
    f"cfy3 tinh duoc: {100*C.cfy3.notna().mean():.1f}%")
rep(f"  PHI TAI CHINH: cfy3 phu {100*C[~C.is_fin].cfy3.notna().mean():.1f}% ({(~C.is_fin).sum()} cap)")
rep(f"  TAI CHINH:     cfy3 phu {100*C[C.is_fin].cfy3.notna().mean():.1f}% ({C.is_fin.sum()} cap)")
per = C.groupby("rebal").apply(lambda g: pd.Series({
    "phu_%": 100*g.cfy3.notna().mean(),
    "phu_phi_tc_%": 100*g[~g.is_fin].cfy3.notna().mean() if (~g.is_fin).any() else np.nan}))
rep(f"\n  Theo ky: phu min {per['phu_%'].min():.0f}% / trung vi {per['phu_%'].median():.0f}% / max {per['phu_%'].max():.0f}%")
rep(f"  Ky phu < 80%: {(per['phu_%']<80).sum()}/{len(per)}  |  ky phu < 60%: {(per['phu_%']<60).sum()}/{len(per)}")
rep(f"  Chi tinh phi-tai-chinh: min {per['phu_phi_tc_%'].min():.0f}% / trung vi {per['phu_phi_tc_%'].median():.0f}%")
rep("\n## Phan phoi cfy3 (loi suat dong tien 3 nam / von hoa) tren ten PHI TAI CHINH")
x = C[~C.is_fin].cfy3.dropna()
rep(f"  n={len(x)} | am {100*(x<0).mean():.1f}% | P10 {x.quantile(.1):.3f} | trung vi {x.median():.3f} | P90 {x.quantile(.9):.3f}")
rep("\n## Doi chieu voi 1/PCF (chan hien tai) — co phai thuoc do KHAC khong?")
pcf = bq(f"""SELECT ticker, DATE_TRUNC(time, QUARTER) AS q, AVG(SAFE_DIVIDE(1,PCF)) AS y
FROM tav2_bq.ticker WHERE PCF > 0 AND time BETWEEN DATE '2013-01-01' AND DATE '2026-06-19'
GROUP BY ticker, q""")
pcf["q"] = pd.to_datetime(pcf["q"])
pm = {(r.ticker, r.q): float(r.y) for r in pcf.itertuples()}
C["srcq"] = C.rebal.dt.to_period("Q").dt.start_time - pd.offsets.QuarterBegin(startingMonth=1)
C["cfy1"] = [pm.get((t, q), np.nan) for t, q in zip(C.ticker, C.srcq)]
sub = C[~C.is_fin].dropna(subset=["cfy1","cfy3"])
rep(f"  n={len(sub)} cap co ca hai. Spearman(1/PCF, cfy3) = {sub.cfy1.corr(sub.cfy3, method='spearman'):.3f}")
rep(f"  Pearson = {sub.cfy1.corr(sub.cfy3):.3f}   => {'KHAC nhau du de dang gia' if abs(sub.cfy1.corr(sub.cfy3, method='spearman'))<0.8 else 'GAN TRUNG - chan moi khong them thong tin'}")
C.to_csv(f"{OUT}/cov_cf.csv", index=False)
open(f"{OUT}/cov_check_raw.txt","w").write("\n".join(LOG))
