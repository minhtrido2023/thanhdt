# -*- coding: utf-8 -*-
"""Phase 0b — pool co bi rang buoc khong? gate loai bao nhieu? BANK co phai hieu ung SELECTOR
hay hieu ung UNIVERSE? (pool=60 liquid gated -> top30 value)"""
import os, sys, bisect
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(WORKDIR, "mike/agents/Taylor/research/custom30v_selector_20260909")
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
os.environ.setdefault("BQ_CACHE_THREADS", "1")
from simulate_holistic_nav import bq
import custom_basket as cb
LOG=[]
def rep(t): print(t); LOG.append(t)

eff_start, end_date = "2013-01-02", "2026-06-19"
qliq = bq(f"""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q,
  AVG(t.Volume_3M_P50*{cb.pxw_sql()}) AS liq, COUNT(*) AS nd
FROM tav2_bq.ticker t WHERE {cb.universe_pred()} AND {cb.UNIVERSE_FILTER}
  AND t.time >= DATE '{eff_start}' AND t.time <= DATE '{end_date}'
GROUP BY t.ticker, q HAVING nd >= 20""")
qliq["q"] = pd.to_datetime(qliq["q"])
rat = bq(f"""SELECT r.ticker, r.time, r.rating FROM tav2_bq.fa_ratings_8l r
WHERE r.time <= DATE '{end_date}' ORDER BY r.ticker, r.time""")
rat["time"] = pd.to_datetime(rat["time"])
rby = {tk:(list(g["time"]),list(g["rating"])) for tk,g in rat.groupby("ticker")}
def rating_asof(tk,d):
    e=rby.get(tk)
    if not e: return np.nan
    i=bisect.bisect_right(e[0],d)-1
    return float(e[1][i]) if i>=0 else np.nan
vp = pd.read_csv(f"{WORKDIR}/data/value_panel_2014.csv", parse_dates=["time"], usecols=["ticker","time","route"])
vp["qstart"]=vp["time"].dt.to_period("Q").dt.start_time
rt = vp.dropna(subset=["route"]).sort_values("time").groupby(["ticker","qstart"])["route"].last()
rh = {tk:(list(g.index.get_level_values(1)),list(g.values)) for tk,g in rt.groupby(level=0)}
def route_asof(tk,q):
    e=rh.get(tk)
    if not e: return "UNKNOWN"
    i=bisect.bisect_right(e[0],pd.Timestamp(q))-1
    return e[1][i] if i>=0 else e[1][0]
FIN={"BANK","INSURANCE","SECURITIES"}
mem = pd.read_csv(f"{OUT}/members.csv", parse_dates=["rebal_date"])
liq_piv = qliq.pivot_table(index="q", columns="ticker", values="liq")
rows=[]
for d, g in mem.groupby("rebal_date"):
    qd = pd.Timestamp(d).to_period("Q").start_time
    pq = [q for q in liq_piv.index if q < qd]
    if not pq: continue
    src = max(pq)
    lr = liq_piv.loc[src].dropna().sort_values(ascending=False)
    gated=[t for t in lr.index if (lambda r: pd.notna(r) and r<=3)(rating_asof(t,d))]
    pool=gated[:60]
    rows.append(dict(rebal=d.date(), n_liquid=len(lr), n_gated=len(gated), pool_binds=len(gated)>60,
        fin_in_pool=sum(route_asof(t,src) in FIN for t in pool),
        bank_in_pool=sum(route_asof(t,src)=="BANK" for t in pool),
        bank_in_basket=sum(route_asof(t,src)=="BANK" for t in g.ticker),
        fin_in_basket=sum(route_asof(t,src) in FIN for t in g.ticker)))
P=pd.DataFrame(rows)
rep("## POOL co bi rang buoc khong (pool = 60 ten thanh khoan nhat da qua gate rating<=3)")
rep(f"So ten qua gate moi ky: TB {P.n_gated.mean():.0f} (min {P.n_gated.min()}, max {P.n_gated.max()}) "
    f"tren {P.n_liquid.mean():.0f} ten co thanh khoan => pool 60 RANG BUOC {P.pool_binds.mean()*100:.0f}% so ky")
rep("\n## BANK: hieu ung SELECTOR hay UNIVERSE? (so ten trong POOL 60 vs trong RO 30)")
P["bank_rate_pool"]=100*P.bank_in_pool/60; P["bank_rate_basket"]=100*P.bank_in_basket/30
P["fin_rate_pool"]=100*P.fin_in_pool/60;   P["fin_rate_basket"]=100*P.fin_in_basket/30
_is=P[P.rebal<pd.Timestamp("2020-01-01").date()]; _oos=P[P.rebal>=pd.Timestamp("2020-01-01").date()]
for nm,S in (("TOAN KY",P),("IS 2014-19",_is),("OOS 2020+",_oos)):
    rep(f"  {nm:<11} BANK trong pool {S.bank_rate_pool.mean():5.1f}% -> trong ro {S.bank_rate_basket.mean():5.1f}% "
        f"(khuech dai x{S.bank_rate_basket.mean()/max(S.bank_rate_pool.mean(),1e-9):.2f}) | "
        f"FIN pool {S.fin_rate_pool.mean():5.1f}% -> ro {S.fin_rate_basket.mean():5.1f}%")
rep(f"\nKy gan nhat: {P.iloc[-1].to_dict()}")
P.to_csv(f"{OUT}/pool_diag.csv", index=False)
open(f"{OUT}/phase0_pool_raw.txt","w").write("\n".join(LOG))
