#!/usr/bin/env python3
"""
analyze_lagged_pos_why.py
==========================
Phân tích sâu vì sao LAGGED_POS hoạt động tốt trong bear/sideways.

Hypotheses test:
  H1: Information asymmetry — small/mid caps drift longer (sector/market-cap analysis)
  H2: Behavioral — bear/sideways markets are slower to price earnings → bigger drift
  H3: Mean reversion — depressed pre-prices → bigger positive bounce post
  H4: Defensive selection — universe biased toward stable/quality names
  H5: Liquidity — less crowding in bear means lag captured
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

# ─── Load data ───────────────────────────────────────────────────────────
trades = pd.read_csv("data/lagged_pos_trades.csv", parse_dates=["dt","entry_dt","release_dt"])
sells  = trades[trades["side"]=="SELL"].copy()
print(f"Total sells: {len(sells)}")

vni = pd.read_csv("data/VNINDEX.csv", parse_dates=["time"])
vni = vni[["time","Close"]].rename(columns={"Close":"vni_close"}).set_index("time").sort_index()
vni["vni_ma200"] = vni["vni_close"].rolling(200, min_periods=100).mean()
vni["vni_3m_ret"] = vni["vni_close"].pct_change(63) * 100
vni["vni_6m_ret"] = vni["vni_close"].pct_change(126) * 100

# Attach VNI state at entry date
sells["entry_dt"] = pd.to_datetime(sells["entry_dt"])
sells = sells.merge(vni[["vni_ma200","vni_close","vni_3m_ret","vni_6m_ret"]],
                     left_on="entry_dt", right_index=True, how="left")
sells["vni_above_ma200"] = sells["vni_close"] > sells["vni_ma200"]

# Define regime at entry
def classify_regime(r):
    if pd.isna(r["vni_3m_ret"]) or pd.isna(r["vni_ma200"]): return "UNK"
    if r["vni_3m_ret"] < -8 and not r["vni_above_ma200"]: return "BEAR"
    if r["vni_3m_ret"] > 10 and r["vni_above_ma200"]: return "BULL"
    return "SIDEWAYS"
sells["regime"] = sells.apply(classify_regime, axis=1)

print("\n" + "="*90)
print("  H2: Performance by VNI regime at entry")
print("="*90)
for reg, g in sells.groupby("regime"):
    print(f"  {reg:<10}: N={len(g):4d}  WR={(g['ret_pct']>0).mean()*100:>5.1f}%  avg_ret={g['ret_pct'].mean():>+6.2f}%  median={g['ret_pct'].median():>+6.2f}%")
print(f"  {'ALL':<10}: N={len(sells):4d}  WR={(sells['ret_pct']>0).mean()*100:>5.1f}%  avg_ret={sells['ret_pct'].mean():>+6.2f}%")

# ─── H3: pre-release dip vs post-release bounce ──────────────────────────
print("\n" + "="*90)
print("  H3: Pre-release pricing — were stocks already depressed?")
print("="*90)
# Need entry_dt prices vs release_dt prices and earlier
# We have entry_px (T+5 from release), release_dt
# Compute pre-release move: how much did stock move from -30d to -1d pre-release?
import pickle
with open("data/earnings_px.pkl","rb") as f: px = pickle.load(f)
px["time"] = pd.to_datetime(px["time"])
px_piv = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
all_dates = np.array(px_piv.index)

def get_offset(tk, ref_dt, offset):
    if tk not in px_piv.columns: return np.nan
    pos = np.searchsorted(all_dates, np.datetime64(ref_dt), side="right") - 1
    if pos < 0: return np.nan
    tgt = pos + offset
    if tgt < 0 or tgt >= len(all_dates): return np.nan
    return px_piv.iloc[tgt][tk]

sells["px_m30"] = sells.apply(lambda r: get_offset(r["ticker"], r["release_dt"], -30), axis=1)
sells["px_m1"]  = sells.apply(lambda r: get_offset(r["ticker"], r["release_dt"], -1),  axis=1)
sells["pre_release_ret"] = (sells["px_m1"] / sells["px_m30"] - 1) * 100

print("  Pre-release return distribution (T-30 → T-1):")
print(f"    Overall: mean={sells['pre_release_ret'].mean():+.2f}%  median={sells['pre_release_ret'].median():+.2f}%")
for reg, g in sells.groupby("regime"):
    if reg == "UNK": continue
    print(f"    {reg:<10}: mean={g['pre_release_ret'].mean():+6.2f}%  median={g['pre_release_ret'].median():+6.2f}%  ret_pct_mean={g['ret_pct'].mean():+6.2f}%")

# Correlation: pre_release_ret vs realized ret
corr_all = sells[["pre_release_ret","ret_pct"]].corr().iloc[0,1]
print(f"  Corr(pre_release_ret, realized_ret) overall: {corr_all:+.3f}")

# ─── H4: Defensive selection — sector/cap analysis ───────────────────────
print("\n" + "="*90)
print("  H4: Universe composition — what sectors/types are in LAGGED_POS?")
print("="*90)
# Read FA ratings for ticker info (ICB_Code, MktCap)
fa = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time"])
prof = pd.read_csv("data/ticker_reaction_profile.csv", index_col=0)
universe = prof[(prof["avg_post_good"] >= 5.0) & (prof["n_good"] >= 4)].index.tolist()
fa_uni = fa[fa["ticker"].isin(universe)].sort_values("quarter").drop_duplicates("ticker", keep="last")
print(f"  Universe size with FA data: {len(fa_uni)}/{len(universe)}")
print(f"  MktCap distribution (latest, B VND):")
print(f"    p10={fa_uni['MktCap'].quantile(0.1)/1e9:.0f}B  median={fa_uni['MktCap'].median()/1e9:.0f}B  p90={fa_uni['MktCap'].quantile(0.9)/1e9:.0f}B")
print(f"  ICB_Code groups (top 15):")
icb = fa_uni["ICB_Code"].value_counts()
for code, n in icb.head(15).items():
    print(f"    {code}: {n}")

# Compare to whole universe (all tickers with FA)
fa_all = fa.sort_values("quarter").drop_duplicates("ticker", keep="last")
print(f"\n  Compare median MktCap LAGGED_POS vs ALL: {fa_uni['MktCap'].median()/1e9:.0f}B vs {fa_all['MktCap'].median()/1e9:.0f}B")

# Ticker count by size bucket (for LAGGED_POS universe)
def cap_bucket(mc):
    if pd.isna(mc): return "UNK"
    if mc < 500e9:  return "MICRO (<500B)"
    if mc < 2000e9: return "SMALL (500B-2T)"
    if mc < 10000e9: return "MID (2T-10T)"
    return "LARGE (>10T)"
fa_uni["bucket"] = fa_uni["MktCap"].apply(cap_bucket)
fa_all["bucket"] = fa_all["MktCap"].apply(cap_bucket)
print(f"\n  Market cap bucket distribution:")
print(f"  {'Bucket':<20}{'LAGGED %':>12}{'ALL %':>12}")
for b in ["MICRO (<500B)","SMALL (500B-2T)","MID (2T-10T)","LARGE (>10T)","UNK"]:
    n_uni = (fa_uni["bucket"]==b).sum() / len(fa_uni) * 100
    n_all = (fa_all["bucket"]==b).sum() / len(fa_all) * 100
    print(f"  {b:<20}{n_uni:>11.1f}%{n_all:>11.1f}%")

# ─── H1: WR by sector (FA sub) ──────────────────────────────────────────
print("\n" + "="*90)
print("  H1: Performance breakdown by sector")
print("="*90)
sells_m = sells.merge(fa_uni[["ticker","ICB_Code","sub"]], on="ticker", how="left")
for sub, g in sells_m.groupby("sub"):
    if len(g) < 20: continue
    print(f"  {sub:<14}: N={len(g):4d}  WR={(g['ret_pct']>0).mean()*100:>5.1f}%  avg={g['ret_pct'].mean():>+6.2f}%")

# ─── H5: hold duration vs WR ────────────────────────────────────────────
print("\n" + "="*90)
print("  H5: Performance by VNI 6M momentum at entry (proxy for lag-window strength)")
print("="*90)
sells["vni_6m_bucket"] = pd.cut(sells["vni_6m_ret"], bins=[-100, -20, -5, 5, 20, 100],
                                  labels=["<-20%","-20to-5%","-5to+5%","+5to+20%",">+20%"])
for b, g in sells.groupby("vni_6m_bucket"):
    if len(g) < 20: continue
    print(f"  VNI_6M {str(b):<14}: N={len(g):4d}  WR={(g['ret_pct']>0).mean()*100:>5.1f}%  avg={g['ret_pct'].mean():>+6.2f}%")

# ─── H6: Average entry MktCap (proxy for size) ──────────────────────────
print("\n" + "="*90)
print("  H6: Performance by ticker market cap")
print("="*90)
sells_m["mktcap"] = sells_m["ticker"].map(fa_uni.set_index("ticker")["MktCap"])
sells_m["cap_bucket"] = sells_m["mktcap"].apply(cap_bucket)
for b, g in sells_m.groupby("cap_bucket"):
    if len(g) < 20: continue
    print(f"  {b:<20}: N={len(g):4d}  WR={(g['ret_pct']>0).mean()*100:>5.1f}%  avg={g['ret_pct'].mean():>+6.2f}%")

print("\nDone.")
