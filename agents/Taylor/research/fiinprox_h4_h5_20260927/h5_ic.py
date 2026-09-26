"""H5 part A -- IC of momentum / value CONDITIONED on retail_net_share tercile,
side by side with the default axis-2 (breadth-tercile PIT, convention 2026-08-22).
Direction is NOT tested (ecology-as-direction REFUTED 2026-07-13) -- conditioning only."""
import numpy as np, pandas as pd, duckdb
WC="/home/trido/thanhdt/WorkingClaude"
c=duckdb.connect()

# ---- panel: universe_pit members only (PIT membership, not a whole-history ticker list)
q=f"""
SELECT t.time AS date, t.ticker, t.Close, t.MA200, t.PE
FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet') t
JOIN read_parquet('{WC}/data/bq_cache/universe_pit_q/*.parquet') u
  ON u.time=t.time AND u.ticker=t.ticker AND u.in_universe
WHERE t.time>='2015-04-01' AND t.ticker<>'VNINDEX' AND t.Close>0
"""
p=c.execute(q).df(); p["date"]=pd.to_datetime(p["date"])
p=p.sort_values(["ticker","date"]).reset_index(drop=True)
print(f"panel rows={len(p):,}  tickers={p.ticker.nunique()}  {p.date.min().date()}->{p.date.max().date()}")

g=p.groupby("ticker",sort=False)["Close"]
p["mom_200"]=g.transform(lambda s: s/s.shift(200)-1)       # adjusted Close: correct for momentum (§9)
p["fwd_1m"]=g.transform(lambda s: s.shift(-21)/s-1)        # 21-session forward return
p["ey"]=np.where(p["PE"]>0, 1.0/p["PE"], np.nan)           # value = 1/PE (8L dominant axis)
p["above_ma200"]=(p["Close"]>p["MA200"]).astype(float)

# ---- breadth PIT (axis-2 default): %members above MA200, classified by breadth_{t-1},
#      tercile from the ROLLING 252-session percentile
br=p.groupby("date")["above_ma200"].mean().rename("breadth").to_frame()
br["breadth_lag"]=br["breadth"].shift(1)
br["breadth_pctile"]=br["breadth_lag"].rolling(252,min_periods=252).rank(pct=True)
br["breadth_ter"]=pd.cut(br["breadth_pctile"],[0,1/3,2/3,1.0],labels=["LOW","MID","HIGH"])

# ---- retail_net_share tercile, PIT: month M uses the PREVIOUS month's value
mon=pd.read_csv("h5_retail_monthly.csv",parse_dates=["date"]).set_index("date")
mon["lagged"]=mon["retail_net_share_m"].shift(1)
mon["pctile"]=mon["lagged"].rolling(24,min_periods=24).rank(pct=True)   # rolling 24m, PIT
mon["retail_ter"]=pd.cut(mon["pctile"],[0,1/3,2/3,1.0],labels=["LOW","MID","HIGH"])
ax=br.reset_index()[["date","breadth_ter"]].copy()
ax["ym"]=ax["date"].values.astype("datetime64[M]")
ax=ax.merge(mon.reset_index()[["date","retail_ter"]].rename(columns={"date":"ym"}),on="ym",how="left")

# ---- daily cross-sectional Spearman IC
def daily_ic(df,fac):
    s=df.dropna(subset=[fac,"fwd_1m"])
    if len(s)<30: return np.nan
    return s[fac].corr(s["fwd_1m"],method="spearman")
ics=p.groupby("date").apply(lambda df: pd.Series({"ic_mom":daily_ic(df,"mom_200"),
                                                  "ic_ey":daily_ic(df,"ey"),
                                                  "n":len(df)}),include_groups=False).reset_index()
ics=ics.merge(ax[["date","breadth_ter","retail_ter"]],on="date",how="left")
ics=ics[(ics.date>="2016-04-01")&(ics.date<="2026-08-31")]
ics.to_csv("h5_daily_ic.csv",index=False)

def block_boot(x, months, B=2000, seed=7):
    """cluster-robust by MONTH (quant-research skill §4): resample months with replacement,
    each drawn month carries ALL its days."""
    rng=np.random.default_rng(seed); um=months.unique(); idx={m:np.where(months==m)[0] for m in um}
    out=np.empty(B)
    for b in range(B):
        take=np.concatenate([idx[m] for m in rng.choice(um,len(um),replace=True)])
        out[b]=np.nanmean(x[take])
    return out

for split,col in [("RETAIL_SHARE","retail_ter"),("BREADTH (truc 2 mac dinh)","breadth_ter")]:
    print(f"\n{'='*78}\n=== IC theo tercile {split} ===")
    for period,a,b in [("IS  2016-04..2019-12","2016-04-01","2019-12-31"),
                       ("OOS 2020-01..2026-08","2020-01-01","2026-08-31")]:
        w=ics[(ics.date>=a)&(ics.date<=b)]
        print(f"\n  {period}   (n phien={len(w)})")
        print(f"  {'tercile':8s} {'n_day':>6s} {'n_mon':>6s} {'IC_mom':>8s} {'IC_ey':>8s}")
        for t in ["LOW","MID","HIGH"]:
            s=w[w[col]==t]
            if not len(s): continue
            nm=s.date.dt.to_period("M").nunique()
            print(f"  {t:8s} {len(s):6d} {nm:6d} {np.nanmean(s.ic_mom):8.4f} {np.nanmean(s.ic_ey):8.4f}")
        hi,lo=w[w[col]=="HIGH"],w[w[col]=="LOW"]
        for fac in ["ic_mom","ic_ey"]:
            if not len(hi) or not len(lo): continue
            diff=np.nanmean(hi[fac])-np.nanmean(lo[fac])
            bh=block_boot(hi[fac].to_numpy(),hi.date.dt.to_period("M"))
            bl=block_boot(lo[fac].to_numpy(),lo.date.dt.to_period("M"))
            bd=bh-bl; ci=np.percentile(bd,[2.5,97.5])
            print(f"    HIGH-LOW {fac}: {diff:+.4f}  block-boot(month,B=2000) 95%CI "
                  f"[{ci[0]:+.4f},{ci[1]:+.4f}]  {'CI KHONG chua 0' if ci[0]*ci[1]>0 else 'CI CHUA 0'}")
