"""Forward-return validation of the 8L composite-value zones + two user requests (2026-06-16):
  P1: do composite zones forward-predict (BUY-NOW > ACCUMULATE > WATCH-RICH; TRAP underperforms)?
      and does composite BUY-NOW beat the old pb_z-only BUY-NOW?
  P2: ROE_Min5Y<0 blanket exclusion is WRONG (one-off COVID scars vs chronic destroyers). Which
      THROUGH-CYCLE rule best separates "recovers / forward-OK" from "real trap"?
  P3: should a proven long (5Y) positive-cashflow record ADD points (tenure/stability/credibility)?
Forward target = profit_3M (T+60, matches multi-month zone holding). Equal-weight, per-month then averaged.
"""
import numpy as np, pandas as pd

WD = "/home/trido/thanhdt/WorkingClaude"
df = pd.read_csv(f"{WD}/data/zone_bt_panel.csv", parse_dates=["time"])
df["ym"] = df.time.values.astype("datetime64[M]"); df["year"] = df.time.dt.year
df["pb_z"] = (df.PB - df.PB_MA5Y) / df.PB_SD5Y.replace(0, np.nan)
df["earn_yield"] = np.where(df.PE > 0, 1.0/df.PE, np.nan)
df["sec"] = (df.ICB_Code // 1000).fillna(-1)
# merge 3Y CFO
fin = pd.read_csv(f"{WD}/data/cfoa3y_fin.csv", parse_dates=["fin_time"]).sort_values("fin_time")
df = pd.merge_asof(df.sort_values("time"), fin, by="ticker", left_on="time", right_on="fin_time", direction="backward")

d = df[df.turnover >= 5e9].copy()
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
_adj = np.where(_cfp.notna()&(_cfp>=0.5), 0.05, np.where(_cfp.notna()&(_cfp<0.2), -0.08, 0.0))
d["vscore"] = (0.35*d["rel"] + 0.65*d["abs_sn"].fillna(0.5) + _adj).clip(0,1)

FWD = "profit_3M"
def avgfwd(mask):
    s = d[mask]
    per = s.groupby("ym")[FWD].mean()
    return per.mean(), len(s)

# ---------- P2 FIRST (the trap rule feeds the zones) ----------
print("="*80)
print("P2: ROE_Min5Y<0 names — forward return by THROUGH-CYCLE recovery split (profit_3M)")
neg = d[d.ROE_Min5Y < 0]
print(f"  ALL ROE_Min5Y<0 (n={len(neg)}): fwd {avgfwd(d.ROE_Min5Y<0)[0]:+.2f}%   | universe fwd {d[FWD].mean():+.2f}%")
splits = {
    "chronic: ROE_Min3Y<0 (still -ve recent 3Y)": (d.ROE_Min5Y<0)&(d.ROE_Min3Y<0),
    "one-off: ROE_Min3Y>=0 (no -ve last 3Y)":     (d.ROE_Min5Y<0)&(d.ROE_Min3Y>=0),
    "chronic: ROE5Y<=0 (5Y avg -ve)":             (d.ROE_Min5Y<0)&(d.ROE5Y<=0),
    "recovered: ROE5Y>0.05 & ROIC_Trail>0":       (d.ROE_Min5Y<0)&(d.ROE5Y>0.05)&(d.ROIC_Trailing>0),
}
for lbl, m in splits.items():
    f, n = avgfwd(m)
    print(f"    {lbl:48} n={n:>5}  fwd {f:+.2f}%")

# NEW trap = chronic (ROE_Min5Y<0 AND (ROE_Min3Y<0 OR ROE5Y<=0.05)); one-off scars spared
d["trap_old"] = (d.ROE_Min5Y < 0)
d["trap_new"] = (d.ROE_Min5Y < 0) & ((d.ROE_Min3Y < 0) | (d.ROE5Y <= 0.05))
spared = d[d.trap_old & ~d.trap_new]
print(f"  --> NEW guard spares {spared.ticker.nunique()} names old-guard trapped; their fwd "
      f"{avgfwd(d.trap_old & ~d.trap_new)[0]:+.2f}% vs still-trapped {avgfwd(d.trap_new)[0]:+.2f}% "
      f"(if spared >> trapped, old blanket exclusion was wrong)")

# ---------- P1: zone forward returns (using NEW trap guard) ----------
T_BUY, T_ACC = 0.66, 0.48
def zone(r):
    if r["trap_new"] and r["vscore"] >= T_ACC: return "4_TRAP"
    if r["vscore"] >= T_BUY: return "1_BUY"
    if r["vscore"] >= T_ACC: return "2_ACC"
    return "3_WATCH"
d["zone"] = d.apply(zone, axis=1)
print("\n" + "="*80)
print("P1: forward return (profit_3M) by COMPOSITE zone — expect BUY > ACC > WATCH, TRAP worst")
for z in ["1_BUY","2_ACC","3_WATCH","4_TRAP"]:
    f, n = avgfwd(d.zone == z)
    print(f"    {z:8} n={n:>6}  fwd {f:+.2f}%")
# composite BUY vs old pb_z-only BUY
comp_buy = (d.zone == "1_BUY")
pbz_buy = (d.pb_z <= -0.3) & ~(d.ROE_Min5Y < 0)        # old BUY-NOW rule
print(f"\n  composite BUY-NOW : fwd {avgfwd(comp_buy)[0]:+.2f}%  (n={comp_buy.sum()})")
print(f"  old pb_z-only BUY : fwd {avgfwd(pbz_buy)[0]:+.2f}%  (n={pbz_buy.sum()})")
print(f"  pure w=1 abs top-30%%: fwd {avgfwd(d.abs_sn>=0.7)[0]:+.2f}%")

# ---------- P3: 5Y-CFO tenure/stability bonus ----------
print("\n" + "="*80)
print("P3: proven 5Y positive cashflow (CF_OA_5Y>0) — forward return + downside (tenure/credibility)")
has5 = d.CF_OA_5Y > 0
for lbl, m in [("CF_OA_5Y>0 (proven 5Y cash)", has5), ("no valid 5Y (new/weak)", ~has5)]:
    s = d[m]; per = s.groupby("ym")[FWD]
    dn = s[s[FWD] < -20][FWD].count()/max(len(s),1)*100   # tail/crash freq
    print(f"    {lbl:30} n={len(s):>6}  fwd {per.mean().mean():+.2f}%  P(fwd<-20%)={dn:.1f}%")
