# -*- coding: utf-8 -*-
"""
build_concentration_history.py
==============================
Build daily concentration time series for VNINDEX universe 2014→now.

Metrics:
  - Trading-value HHI (Σ w_i² where w_i = TV_i / total_TV) — "where money is flowing"
  - CR3, CR5, CR10 — top-k share of trading value
  - VIN_family share — VIC + VHM + VPL + VRE
  - rolling 60d cap-EW return divergence — |ret_VNI_60d − ret_VNINDEX_EW_60d|

Composite concentration_score(t) = mean of expanding pct-ranks of
{HHI_tv, CR3_tv, capEW_div_60d}, clipped [0,1].

Trading-value HHI chosen over cap HHI: doesn't require OShares (sparse pre-2014),
captures dynamic attention/flow, and is what actually drives daily index moves.

Output:
  concentration_history.csv: time, HHI_tv, N_eff, CR3, CR5, CR10, VIN_family,
                              capEW_div_60d, hhi_rank, cr3_rank, div_rank,
                              concentration_score
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
CACHE_TICKER = os.path.join(WORKDIR, "data/_cache_universe_2013_now.pkl")
CACHE_VNI    = os.path.join(WORKDIR, "data/_cache_vnindex_2000_now.pkl")
EW_FULL_CSV  = os.path.join(WORKDIR, "data/vnindex_5state_ew_full.csv")
VIN_FAMILY   = {"VIC", "VHM", "VPL", "VRE"}

print("="*70)
print("Build concentration history")
print("="*70)

# ─────────────────────────────────────────────────────────────────────
# Load cached data
# ─────────────────────────────────────────────────────────────────────
print("\n[1] Load cached data")
univ = pd.read_pickle(CACHE_TICKER)
vni  = pd.read_pickle(CACHE_VNI)
ew   = pd.read_csv(EW_FULL_CSV)
vni["time"] = pd.to_datetime(vni["time"])
ew["time"]  = pd.to_datetime(ew["time"])
print(f"  Universe: {len(univ):,} rows, {univ['ticker'].nunique()} tickers")
print(f"  VNI:      {len(vni)} rows")
print(f"  EW:       {len(ew)} rows")

# ─────────────────────────────────────────────────────────────────────
# Compute trading value
# ─────────────────────────────────────────────────────────────────────
print("\n[2] Compute daily trading values")
univ = univ.sort_values(["ticker", "time"]).reset_index(drop=True)
univ["tv"] = univ["Close"] * univ["Volume"]
# Mask: only include if trading value > 0 (drop halt/zero-volume days)
univ = univ[univ["tv"] > 0].copy()
print(f"  Non-zero TV rows: {len(univ):,}")

# ─────────────────────────────────────────────────────────────────────
# Per-date aggregates: HHI_tv, CR3/5/10, VIN_family
# ─────────────────────────────────────────────────────────────────────
print("\n[3] Aggregate per date (HHI, CR3/5/10, VIN family share)")
univ["is_vin"] = univ["ticker"].isin(VIN_FAMILY).astype(int)

def per_date_stats(group):
    tv = group["tv"].values
    total = tv.sum()
    if total <= 0: return None
    w = tv / total
    w_sorted = np.sort(w)[::-1]
    hhi = float(np.sum(w * w))
    cr3 = float(w_sorted[:3].sum())
    cr5 = float(w_sorted[:5].sum())
    cr10 = float(w_sorted[:10].sum())
    vin_share = float((group["tv"] * group["is_vin"]).sum() / total)
    n = len(group)
    return pd.Series({
        "HHI_tv": hhi, "N_eff": 1.0/hhi if hhi > 0 else np.nan,
        "CR3": cr3, "CR5": cr5, "CR10": cr10,
        "VIN_family": vin_share, "n_tickers": n,
    })

# Vectorized version (faster):
print("  Computing weights ...")
univ["tv_total"] = univ.groupby("time")["tv"].transform("sum")
univ["w"] = univ["tv"] / univ["tv_total"]
univ["w2"] = univ["w"]**2

# HHI = sum of w²
g = univ.groupby("time")
hhi_series = g["w2"].sum()
n_series = g["w"].count()
vin_share_series = univ[univ["is_vin"]==1].groupby("time")["w"].sum().reindex(hhi_series.index).fillna(0)

# Top-k CR via groupby + nlargest is expensive; use sort + take.
print("  Computing CR3/5/10 (sort + take per day) ...")
def top_k_sum(df, k):
    return df.sort_values("w", ascending=False).groupby("time")["w"].apply(lambda s: s.head(k).sum())
# faster: use groupby head
sub = univ[["time", "w"]].sort_values(["time", "w"], ascending=[True, False])
sub["rk"] = sub.groupby("time").cumcount() + 1
cr3 = sub[sub["rk"]<=3].groupby("time")["w"].sum().reindex(hhi_series.index).fillna(0)
cr5 = sub[sub["rk"]<=5].groupby("time")["w"].sum().reindex(hhi_series.index).fillna(0)
cr10 = sub[sub["rk"]<=10].groupby("time")["w"].sum().reindex(hhi_series.index).fillna(0)

conc = pd.DataFrame({
    "time": hhi_series.index,
    "HHI_tv": hhi_series.values,
    "N_eff": 1.0 / hhi_series.values,
    "CR3": cr3.values,
    "CR5": cr5.values,
    "CR10": cr10.values,
    "VIN_family": vin_share_series.values,
    "n_tickers": n_series.values,
})
conc = conc.sort_values("time").reset_index(drop=True)
print(f"  Concentration time series: {len(conc)} rows | {conc['time'].min().date()} → {conc['time'].max().date()}")

# ─────────────────────────────────────────────────────────────────────
# Cap-EW divergence: rolling 60d return diff
# ─────────────────────────────────────────────────────────────────────
print("\n[4] Cap-EW 60d return divergence")
vni_post = vni[vni["time"] >= "2014-01-01"][["time", "Close"]].rename(columns={"Close":"vni_close"})
ew_post  = ew[ew["time"] >= "2014-01-01"][["time", "Close"]].rename(columns={"Close":"ew_close"})
m = vni_post.merge(ew_post, on="time", how="inner").sort_values("time").reset_index(drop=True)
m["ret_vni_60d"] = np.log(m["vni_close"] / m["vni_close"].shift(60))
m["ret_ew_60d"]  = np.log(m["ew_close"]  / m["ew_close"].shift(60))
m["capEW_div_60d"] = (m["ret_vni_60d"] - m["ret_ew_60d"]).abs()
print(f"  Divergence series: {len(m)} rows; current value: {m['capEW_div_60d'].iloc[-1]:.4f}")

conc = conc.merge(m[["time", "capEW_div_60d"]], on="time", how="left")

# ─────────────────────────────────────────────────────────────────────
# Expanding pct-ranks (no look-ahead, min 252)
# ─────────────────────────────────────────────────────────────────────
print("\n[5] Expanding percentile ranks (min 252 sessions)")

def expanding_pct_rank(arr, min_lb=252):
    arr = np.asarray(arr, dtype=float)
    out = np.full(len(arr), np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        hist = arr[:t+1]; valid = hist[~np.isnan(hist)]
        if len(valid) < min_lb: continue
        out[t] = np.sum(valid <= arr[t]) / len(valid)
    return out

conc["hhi_rank"] = expanding_pct_rank(conc["HHI_tv"].values, 252)
conc["cr3_rank"] = expanding_pct_rank(conc["CR3"].values, 252)
conc["div_rank"] = expanding_pct_rank(conc["capEW_div_60d"].values, 252)

# Composite (require ≥2 of 3 ranks; if all NaN early period → NaN)
def composite(row):
    vals = [row["hhi_rank"], row["cr3_rank"], row["div_rank"]]
    valid = [v for v in vals if not np.isnan(v)]
    return np.mean(valid) if len(valid) >= 2 else np.nan

conc["concentration_score"] = conc.apply(composite, axis=1)

# ─────────────────────────────────────────────────────────────────────
# Save + summary
# ─────────────────────────────────────────────────────────────────────
out_path = os.path.join(WORKDIR, "data/concentration_history.csv")
conc.to_csv(out_path, index=False)
print(f"\n[6] Saved → {out_path}")
print(f"\nSUMMARY")
print("="*70)

# Current values
last = conc.iloc[-1]
print(f"\nLatest ({last['time']}):")
print(f"  HHI_tv = {last['HHI_tv']:.4f} ({last['HHI_tv']*10000:.0f} bps) | N_eff = {last['N_eff']:.1f}")
print(f"  CR3 = {last['CR3']*100:.1f}%  CR5 = {last['CR5']*100:.1f}%  CR10 = {last['CR10']*100:.1f}%")
print(f"  VIN_family = {last['VIN_family']*100:.1f}%")
print(f"  Cap-EW 60d divergence = {last['capEW_div_60d']*100:.2f}pp")
print(f"  Ranks: hhi={last['hhi_rank']:.2f} cr3={last['cr3_rank']:.2f} div={last['div_rank']:.2f}")
print(f"  → concentration_score = {last['concentration_score']:.2f}")

print(f"\nHistorical distribution of concentration_score (post-252-lookback):")
cs = conc["concentration_score"].dropna()
print(f"  count = {len(cs)}")
for p in [10, 25, 50, 75, 90, 95, 99]:
    print(f"  p{p:>2}  = {np.percentile(cs, p):.3f}")
print(f"  max  = {cs.max():.3f}")

# Distribution of score by regime
print(f"\nScore regime distribution:")
print(f"  score < 0.50:        {(cs < 0.50).mean()*100:>5.1f}% ({(cs < 0.50).sum()} days)")
print(f"  0.50 ≤ score < 0.70: {((cs >= 0.50) & (cs < 0.70)).mean()*100:>5.1f}% ({((cs >= 0.50) & (cs < 0.70)).sum()} days)")
print(f"  0.70 ≤ score < 0.85: {((cs >= 0.70) & (cs < 0.85)).mean()*100:>5.1f}% ({((cs >= 0.70) & (cs < 0.85)).sum()} days)")
print(f"  score ≥ 0.85:        {(cs >= 0.85).mean()*100:>5.1f}% ({(cs >= 0.85).sum()} days)")

# Worst concentration episodes
print(f"\nTop 10 days by concentration_score:")
top = conc.sort_values("concentration_score", ascending=False).head(10)
for _, r in top.iterrows():
    print(f"  {r['time'].strftime('%Y-%m-%d')}  score={r['concentration_score']:.3f}  "
          f"HHI={r['HHI_tv']*10000:.0f}bps  CR3={r['CR3']*100:.1f}%  VIN={r['VIN_family']*100:.1f}%  "
          f"div60d={r['capEW_div_60d']*100:.1f}pp")

# Annual mean
print(f"\nYearly mean concentration_score:")
conc["year"] = pd.to_datetime(conc["time"]).dt.year
yrs = conc.dropna(subset=["concentration_score"]).groupby("year")["concentration_score"].mean()
for y, v in yrs.items():
    bar = "█" * int(v * 50)
    print(f"  {y}  {v:.3f}  {bar}")
