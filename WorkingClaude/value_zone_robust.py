"""Friendlier, overfit-resistant zoning of the composite value_score (user 2026-06-16):
  - DON'T grid-search a hard threshold (overfit). Show the DECILE shape (is the signal even monotone
    enough to hard-group?), then test PERCENTILE-based zones (self-calibrating, no fixed magic number)
    via WALK-FORWARD (IS 2014-19 / OOS 2020-26) to confirm separation holds out-of-sample.
Forward = profit_3M, equal-weight per-month then averaged.
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
d = df[df.turnover >= 5e9].copy()

# rebuild value_score exactly as the screener (w_abs=0.65, sector-neutral abs, 3Y confirm, track bonus)
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
nt = d[~d.trap].copy()    # zoning on non-trapped names

FWD = "profit_3M"
def perfwd(s): return s.groupby("ym")[FWD].mean().mean()

# ---- (1) DECILE SHAPE (is the signal monotone enough to hard-group?) ----
print("="*70)
print("(1) forward profit_3M by value_score DECILE (D1=cheapest ... D10=richest):")
nt["dec"] = nt.groupby("ym")["vscore"].transform(lambda s: pd.qcut(s.rank(method="first"), 10, labels=False))
for k in range(9, -1, -1):
    s = nt[nt.dec == k]
    f = perfwd(s); bar = "#"*int(max(f,0)*8)
    print(f"  D{k+1:<2} (vscore rank {'cheap' if k>=7 else 'rich' if k<=2 else 'mid'}): fwd {f:>+5.2f}%  {bar}")
print("  -> if smooth/noisy rather than cleanly monotone: hard 3-zone cutoffs are crude; soft score better")

# ---- (2) WALK-FORWARD: percentile zones vs hard threshold (IS 2014-19 / OOS 2020-26) ----
def zones_pct(g, buy=0.30, acc=0.40):   # top 30% BUY, next 40% ACC, bottom 30% WATCH — STRUCTURAL, not fitted
    r = g["vscore"].rank(pct=True)
    return np.where(r >= 1-buy, "BUY", np.where(r >= 1-buy-acc, "ACC", "WATCH"))
nt["z_pct"] = nt.groupby("ym", group_keys=False).apply(lambda g: pd.Series(zones_pct(g), index=g.index))
nt["z_hard"] = np.where(nt.vscore>=0.66, "BUY", np.where(nt.vscore>=0.48, "ACC", "WATCH"))

for tag, lo, hi in [("IS 2014-19", 2014, 2019), ("OOS 2020-26", 2020, 2026)]:
    sub = nt[(nt.year>=lo)&(nt.year<=hi)]
    print(f"\n(2) {tag}:")
    for scheme in ["z_pct","z_hard"]:
        row = []
        for z in ["BUY","ACC","WATCH"]:
            s = sub[sub[scheme]==z]; row.append(f"{z} {perfwd(s):+5.2f}% (n={len(s)})")
        sep = perfwd(sub[sub[scheme]=="BUY"]) - perfwd(sub[sub[scheme]=="WATCH"])
        nm = "PERCENTILE(top30/40/30)" if scheme=="z_pct" else "HARD(0.66/0.48)    "
        print(f"   {nm}: " + " | ".join(row) + f"   BUY-WATCH spread {sep:+.2f}pp")
print("\n  -> robust if BUY>WATCH spread holds POSITIVE in OOS for BOTH; percentile is friendlier")
print("     (self-calibrates per period, no fitted cutoff to overfit).")
