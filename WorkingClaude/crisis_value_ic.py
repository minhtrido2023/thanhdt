"""User req: at the lever-deploy bottom, buy from a LIQUIDITY-gated universe (>=5bn VND/day ADV) ranked by
3 value axes 1/PE, 1/PB, 1/PCF — choose the WEIGHTS by their IC measured IN the crisis-recovery period
(not full-period). This script measures the per-cross-section Spearman IC of each lens vs forward return,
in two deploy-relevant contexts, so we can set IC-proportional weights for the bottom-buy basket.

Contexts:
  (1) CRISIS/BEAR states (DT5G 1,2) — broad de-risk regime.
  (2) DEEP-CHEAP deploy windows (pbz_med<=-0.5 & market PE_pctile5y<=0.20) — the ACTUAL G2 lever context.
Universe = liquid (Volume_3M_P50*Close >= 5e9/day). Forward = profit_2M (T+40, already %). Negative
PE/PB/PCF = no-reward (excluded from that lens, like the 8L composite). Cache threads=1."""
import os, sys
os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache")
os.chdir("/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd
from bq_local_cache import get_cache
lc = get_cache()

# market PE 5y-pctile (causal-ish, for the deep-cheap window flag) + liquid universe rows in crisis context
mkt = lc.query("""SELECT t.time, MAX(t.VNINDEX_PE) pe FROM tav2_bq.ticker t
 WHERE t.time>=DATE '2014-01-01' AND t.VNINDEX_PE>0 GROUP BY t.time ORDER BY t.time""")
mkt["time"] = pd.to_datetime(mkt["time"])
mkt["pe_pct5y"] = mkt["pe"].rolling(1250, min_periods=250).apply(lambda s:(s.iloc[-1]>=s).mean())

# per-name liquid rows with the 3 value lenses + forward + state + liquid pbz_med
df = lc.query("""
WITH base AS (
  SELECT t.time, t.ticker, t.PE, t.PB, t.PCF, t.profit_2M f,
         t.Volume_3M_P50*t.Close AS adv,
         (t.PB - t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0) AS pbz
  FROM tav2_bq.ticker_prune t
  WHERE t.time>=DATE '2014-01-01' AND t.profit_2M IS NOT NULL)
SELECT b.*, s.state,
   PERCENTILE_CONT(b.pbz, 0.5) OVER (PARTITION BY b.time) AS pbz_med
FROM base b JOIN tav2_bq.vnindex_5state_dt5g_live s ON b.time=s.time
WHERE b.adv >= 5e9""")
df["time"] = pd.to_datetime(df["time"])
df = df.merge(mkt[["time","pe_pct5y"]], on="time", how="left")

# value lenses (no-reward when denominator<=0)
df["ey"]  = np.where(df["PE"]>0,  1.0/df["PE"],  np.nan)
df["by"]  = np.where(df["PB"]>0,  1.0/df["PB"],  np.nan)
df["cfy"] = np.where(df["PCF"]>0, 1.0/df["PCF"], np.nan)

def spearman_ic(g, col):
    s = g[[col,"f"]].dropna()
    if len(s) < 8: return np.nan
    return s[col].rank().corr(s["f"].rank())

def ic_report(mask, label):
    sub = df[mask]
    days = sub["time"].nunique()
    out = {}
    for c in ["ey","by","cfy"]:
        ics = sub.groupby("time").apply(lambda g: spearman_ic(g, c)).dropna()
        out[c] = (ics.mean(), ics.std()/np.sqrt(len(ics)) if len(ics)>1 else np.nan, len(ics))
    print(f"\n=== {label}  ({days} cross-sections, n_rows={len(sub)}) ===")
    print(f"{'lens':>5} {'mean_IC':>9} {'t-stat':>7} {'n_days':>7}")
    pos = {}
    for c,(m,se,n) in out.items():
        t = m/se if (se and se>0) else np.nan
        print(f"{c:>5} {m:>9.4f} {t:>7.2f} {n:>7}")
        pos[c] = max(m, 0.0)
    tot = sum(pos.values())
    if tot>0:
        w = {c: pos[c]/tot for c in pos}
        print(f"  IC-proportional weights: ey(1/PE)={w['ey']:.2f}  by(1/PB)={w['by']:.2f}  cfy(1/PCF)={w['cfy']:.2f}")
    return out

# Context 1: CRISIS/BEAR
ic_report(df["state"].isin([1,2]), "CRISIS/BEAR (states 1,2)")
# Context 2: deep-cheap deploy window (the actual G2 lever context)
ic_report((df["pbz_med"]<=-0.5) & (df["pe_pct5y"]<=0.20), "DEEP-CHEAP deploy window (pbz_med<=-0.5 & PE_pct<=0.20)")
# Reference: full-period (all states) for contrast
ic_report(df["time"].notna(), "FULL PERIOD (all states, reference)")
print("\nREAD: pick IC-proportional weights from the DEEP-CHEAP window (the actual buy context). Compare to")
print("custom30V's current rank(1/PE)+rank(1/PCF) equal blend (no 1/PB). If 1/PB carries crisis IC, add it.")
