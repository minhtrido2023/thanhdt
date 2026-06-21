"""END-TO-END backtest on the CORRECT screener universe (rating<=3 AS-OF, not just liquid) — closes the
validation gap flagged before sync. Merges historical fa_ratings_8l (PIT), filters to the actual screener
gate (rating<=3 & liquid), rebuilds the EXACT production composite (w_abs=0.65, sector-neutral 1/PE, 3Y
CFO confirm, track-record bonus, ROE_Min3Y trap, PERCENTILE zones), and validates forward returns +
walk-forward IS/OOS on that universe.
"""
import numpy as np, pandas as pd
WD = "/home/trido/thanhdt/WorkingClaude"
df = pd.read_csv(f"{WD}/data/zone_bt_panel.csv", parse_dates=["time"])
df["ym"] = df.time.values.astype("datetime64[M]"); df["year"] = df.time.dt.year
df["pb_z"] = (df.PB - df.PB_MA5Y)/df.PB_SD5Y.replace(0, np.nan)
df["earn_yield"] = np.where(df.PE > 0, 1.0/df.PE, np.nan)
df["sec"] = (df.ICB_Code//1000).fillna(-1)
fin = pd.read_csv(f"{WD}/data/cfoa3y_fin.csv", parse_dates=["fin_time"]).sort_values("fin_time")
df = pd.merge_asof(df.sort_values("time"), fin, by="ticker", left_on="time", right_on="fin_time", direction="backward")
# PIT 8L rating
rat = pd.read_csv(f"{WD}/data/fa_ratings_8l_hist.csv", parse_dates=["rt_time"]).sort_values("rt_time")
df = pd.merge_asof(df.sort_values("time"), rat, by="ticker", left_on="time", right_on="rt_time", direction="backward")

# CORRECT screener universe = as-of rating<=3 AND liquid (LIQ_MIN ~ 3bn live; use turnover>=3e9 proxy)
d = df[(df.rating <= 3) & (df.turnover >= 3e9)].copy()
print(f"universe rating<=3 & liquid: {len(d)} rows, {d.ticker.nunique()} names, {d.ym.nunique()} months, "
      f"avg {d.groupby('ym').size().mean():.0f}/mo  (vs broad-liquid had ~hundreds)")

d["rel"] = (0.5 - d.pb_z/2.0).clip(0, 1)
def _sn(g):
    out = pd.Series(np.nan, index=g.index)
    for sec, idx in g.groupby("sec").groups.items():
        sub = g.loc[idx, "earn_yield"]
        out.loc[idx] = sub.rank(pct=True) if sub.notna().sum() >= 5 else np.nan
    return out.fillna(g["earn_yield"].rank(pct=True))
d["abs_sn"] = d.groupby("ym", group_keys=False).apply(_sn)
_ttm = d[["CF_OA_P0","CF_OA_P1","CF_OA_P2","CF_OA_P3"]].sum(axis=1, min_count=1)
_n3 = d.CF_OA_3Y/3.0
d["cfo_normy"] = np.where((d.PCF>0)&(_ttm>0)&(_n3>0), (1/d.PCF)*np.clip(_n3/_ttm,0.3,3), np.nan)
_cfp = d.groupby("ym")["cfo_normy"].transform(lambda s: s.rank(pct=True))
_adj = np.where(_cfp.notna()&(_cfp>=0.5),0.05, np.where(_cfp.notna()&(_cfp<0.2),-0.08,0.0))
_track = np.where(d.CF_OA_5Y>0,0.03,0.0) + np.where(d.ROE_Min5Y.fillna(-9)>0.10,0.03,0.0)
d["vscore"] = (0.35*d.rel + 0.65*d.abs_sn.fillna(0.5) + _adj + _track).clip(0,1)
d["trap"] = (d.ROE_Min3Y < 0)
nt = d[~d.trap].copy()

FWD = "profit_3M"
def perfwd(s): return s.groupby("ym")[FWD].mean().mean()
print(f"  universe fwd {FWD}: {perfwd(d):+.2f}%  (trapped names fwd {perfwd(d[d.trap]):+.2f}%, "
      f"n_trap={d.trap.sum()})")

# percentile zones (production logic)
def zpct(g, buy=0.30, acc=0.40):
    r = g["vscore"].rank(pct=True)
    return np.where(r>=1-buy,"1_BUY",np.where(r>=1-buy-acc,"2_ACC","3_WATCH"))
nt["zone"] = nt.groupby("ym", group_keys=False).apply(lambda g: pd.Series(zpct(g), index=g.index))

print("\n(A) forward profit_3M by zone (rating<=3 universe, percentile):")
for z in ["1_BUY","2_ACC","3_WATCH"]:
    print(f"    {z:8} fwd {perfwd(nt[nt.zone==z]):+.2f}%  (n={(nt.zone==z).sum()})")
print(f"    4_TRAP   fwd {perfwd(d[d.trap]):+.2f}%  (n={d.trap.sum()})")

# decile
nt["dec"] = nt.groupby("ym")["vscore"].transform(lambda s: pd.qcut(s.rank(method="first"),10,labels=False))
print("\n(B) decile (D10 cheap -> D1 rich):", " ".join(f"D{k+1}:{perfwd(nt[nt.dec==k]):+.1f}" for k in range(9,-1,-1)))

# composite BUY vs old pb_z-only BUY (BOTH on rating<=3 universe)
comp_buy = nt.zone=="1_BUY"
pbz_buy = (d.pb_z<=-0.3) & ~d.trap     # note: pb_z-only buy also on rating<=3 here
print(f"\n(C) composite BUY {perfwd(nt[comp_buy]):+.2f}% (n={comp_buy.sum()})  vs  "
      f"pb_z-only BUY {perfwd(d[pbz_buy]):+.2f}% (n={pbz_buy.sum()})")

# walk-forward IS/OOS
print("\n(D) walk-forward (percentile zones, rating<=3 universe):")
for tag, lo, hi in [("IS 2014-19",2014,2019),("OOS 2020-26",2020,2026)]:
    sub = nt[(nt.year>=lo)&(nt.year<=hi)]
    b,w = perfwd(sub[sub.zone=="1_BUY"]), perfwd(sub[sub.zone=="3_WATCH"])
    a = perfwd(sub[sub.zone=="2_ACC"])
    print(f"    {tag}: BUY {b:+.2f}% | ACC {a:+.2f}% | WATCH {w:+.2f}%   BUY-WATCH {b-w:+.2f}pp")
