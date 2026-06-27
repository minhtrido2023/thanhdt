"""#18 PROXY (cheap, no harness): at deep-cheap deploy bottoms, does a 1/PB-heavy 'pbcombo' basket
deploy BETTER than the production 'yieldcombo' (rank 1/PE + 1/PCF)? Per discipline: proxy before the
dual-vehicle harness wiring (base parking = yieldcombo, bottom-deploy = pbcombo).

At each deep-cheap deploy day (pbz_med<=-0.5 & market PE_pctile5y<=0.20), form two equal-weight top-15
baskets from the SAME liquid(>=5bn/day)+quality universe and compare forward profit_2M (T+40):
  A yieldcombo : rank(1/PE) + rank(1/PCF)                       (production selector)
  B pbcombo    : 0.67*rank(1/PB) + 0.23*rank(1/PCF) + 0.10*rank(1/PE)   (crisis-IC weights)
Quality floor = ROIC5Y>0.08 & ROE_Min5Y>0 & FSCORE>=5 (in-table proxy for the production rating<=3 gate;
avoids the fa_ratings as-of join; 1/PB without quality = distress trap). Direct-parquet read."""
import os, sys
os.chdir("/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import numpy as np, pandas as pd, duckdb
c = duckdb.connect()
tp = "data/bq_cache/ticker_prune/*.parquet"
st = "data/bq_cache/vnindex_5state_dt5g_live.parquet"

# market PE 5y-pctile (VNINDEX_PE mirror on ticker_prune rows)
mkt = c.execute(f"SELECT time, MAX(VNINDEX_PE) pe FROM read_parquet('{tp}') WHERE VNINDEX_PE>0 AND time>=DATE '2014-01-01' GROUP BY time ORDER BY time").fetchdf()
mkt["pe_pct5y"] = mkt["pe"].rolling(1250, min_periods=250).apply(lambda s:(s.iloc[-1]>=s).mean())

# per-name liquid+quality rows with lenses + per-date pbz_med
df = c.execute(f"""
WITH base AS (
  SELECT time, ticker, PE, PB, PCF, profit_2M f, Volume_3M_P50*Close adv,
         (PB - PB_MA5Y)/NULLIF(PB_SD5Y,0) pbz
  FROM read_parquet('{tp}')
  WHERE time>=DATE '2014-01-01' AND profit_2M IS NOT NULL
    AND ROIC5Y>0.08 AND ROE_Min5Y>0 AND FSCORE>=5 AND PE>0 AND PB>0 AND PCF>0 AND Volume_3M_P50*Close>=5e9)
SELECT b.*, MEDIAN(b.pbz) OVER (PARTITION BY b.time) pbz_med FROM base b
""").fetchdf()
df["time"] = pd.to_datetime(df["time"]); mkt["time"] = pd.to_datetime(mkt["time"])
df = df.merge(mkt[["time","pe_pct5y"]], on="time", how="left")
# liquid pbz_med here is over the QUALITY universe (not full prune) — fine as a relative deep-cheap flag,
# but recompute the deploy flag with the SAME full-universe pbz_med used elsewhere for consistency:
full_med = c.execute(f"SELECT time, MEDIAN((PB-PB_MA5Y)/NULLIF(PB_SD5Y,0)) pbz_full FROM read_parquet('{tp}') WHERE PB_SD5Y>0 AND time>=DATE '2014-01-01' GROUP BY time").fetchdf()
full_med["time"] = pd.to_datetime(full_med["time"]); df = df.merge(full_med, on="time", how="left")

deploy = df[(df["pbz_full"]<=-0.5) & (df["pe_pct5y"]<=0.20)].copy()
print(f"=== #18 bottom-basket proxy: {deploy['time'].nunique()} deep-cheap deploy days, {len(deploy)} name-rows ===")

N = 15
def basket_fwd(g, scorer):
    s = scorer(g)
    top = s.sort_values(ascending=False).head(N).index
    return g.loc[top, "f"].mean()
def yieldcombo(g): return g["PE"].rdiv(1).rank(pct=True) + g["PCF"].rdiv(1).rank(pct=True)
def pbcombo(g):   return 0.67*g["PB"].rdiv(1).rank(pct=True) + 0.23*g["PCF"].rdiv(1).rank(pct=True) + 0.10*g["PE"].rdiv(1).rank(pct=True)

rows = []
for d, g in deploy.groupby("time"):
    if len(g) < N: continue
    rows.append({"time": d, "yieldcombo": basket_fwd(g, yieldcombo), "pbcombo": basket_fwd(g, pbcombo), "n": len(g)})
R = pd.DataFrame(rows)
print(f"\n{'selector':>12} {'mean_fwd2M%':>12} {'median%':>9} {'win%':>6} {'days':>5}")
for col in ["yieldcombo","pbcombo"]:
    print(f"{col:>12} {R[col].mean():>11.2f}% {R[col].median():>8.2f}% {(R[col]>0).mean()*100:>5.0f}% {len(R):>5}")
print(f"\nΔ pbcombo − yieldcombo (per deploy-day, mean): {(R['pbcombo']-R['yieldcombo']).mean():+.2f}%  "
      f"| pbcombo wins {(R['pbcombo']>R['yieldcombo']).mean()*100:.0f}% of deploy-days")
# split by era (does the bottom-edge hold IS & OOS?)
for lbl, m in [("IS<2020", R['time']<'2020-01-01'), ("OOS>=2020", R['time']>='2020-01-01')]:
    s = R[m]
    if len(s): print(f"  {lbl}: Δ {(s['pbcombo']-s['yieldcombo']).mean():+.2f}% over {len(s)} days")
print("\nREAD: if pbcombo > yieldcombo at deploy-days (esp. both eras), the 1/PB-heavy bottom basket is worth")
print("the dual-vehicle harness wiring (base=yieldcombo parking, deploy=pbcombo). If ~flat, skip the complexity.")
