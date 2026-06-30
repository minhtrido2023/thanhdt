"""Fair-value multiples-reversion PROTOTYPE + edge backtest.
Fair value = revert each valuation multiple to the name's OWN trailing 5Y average (PIT-clean, causal).
  disc_pe = PE_MA5Y/PE - 1 ; disc_pb = PB_MA5Y/PB - 1 ; disc_eveb = EVEB_MA5Y/EVEB - 1
  fair_discount = mean of available anchors (require PE + >=1 other).  >0 = cheap vs own history.
  fair_price(VND) = Price * (1 + fair_discount).
Quality gate (golden-floor proxy; CF_OA_3Y absent in this cache): ROE_Min3Y>=0 AND FSCORE>=5, liquidity>=5B, PE>0.
EDGE TEST: does fair_discount predict forward return (profit_1M/2M/3M, TARGET only)? Rank-IC per date + quintiles,
IS 2014-19 / OOS 2020+. profit_* used ONLY as the label, never as a filter. v1 = pure reversion (NO moat/liquidity
adjustment yet) — prove the core edge first, then layer adjustments only if they ADD.
"""
import duckdb, numpy as np, pandas as pd
pd.set_option("display.width", 220)
PARQ = "data/bq_cache/ticker_prune.parquet"
q = f"""
SELECT time, ticker, Price, PE, PB, EVEB, PE_MA5Y, PB_MA5Y, EVEB_MA5Y,
       ROE_Min3Y, FSCORE, ROIC5Y, Trading_Value_1M_P50 AS liq,
       profit_1M, profit_2M, profit_3M
FROM read_parquet('{PARQ}')
WHERE time>=DATE '2014-01-01' AND Price>0 AND PE>0 AND PE_MA5Y>0
      AND ROE_Min3Y>=0 AND FSCORE>=5 AND Trading_Value_1M_P50>=5e9
      AND profit_1M IS NOT NULL
"""
df = duckdb.connect().execute(q).df()
df["disc_pe"] = df["PE_MA5Y"]/df["PE"] - 1
df["disc_pb"] = np.where((df["PB"]>0)&(df["PB_MA5Y"]>0), df["PB_MA5Y"]/df["PB"]-1, np.nan)
df["disc_eveb"] = np.where((df["EVEB"]>0)&(df["EVEB_MA5Y"]>0), df["EVEB_MA5Y"]/df["EVEB"]-1, np.nan)
df["n_anchor"] = df[["disc_pe","disc_pb","disc_eveb"]].notna().sum(axis=1)
df["fair_discount"] = df[["disc_pe","disc_pb","disc_eveb"]].mean(axis=1, skipna=True)
df = df[df["n_anchor"]>=2].copy()                                  # require PE + >=1 other anchor
df["fair_discount"] = df["fair_discount"].clip(-0.8, 3.0)          # winsorize
df["fair_price"] = df["Price"]*(1+df["fair_discount"])
df["yr"] = pd.to_datetime(df["time"]).dt.year
print(f"Loaded {len(df):,} name-days, {df['ticker'].nunique()} names, {df['yr'].min()}-{df['yr'].max()} (quality-gated, >=2 anchors)")

def rank_ic(d, fwd):
    g = d.groupby("time")
    ic = g.apply(lambda x: x["fair_discount"].corr(x[fwd], method="spearman") if len(x)>=20 else np.nan,
                 include_groups=False).dropna()
    return ic.mean(), ic.mean()/(ic.std()/np.sqrt(len(ic))), len(ic)

print("\n=== Rank-IC: fair_discount vs forward return (per-date Spearman, then averaged) ===")
print(f"{'window':>10} {'horizon':>8} {'mean_IC':>8} {'t':>6} {'n_dates':>8}")
for wlab, dd in [("ALL", df), ("IS 14-19", df[df.yr<=2019]), ("OOS 20+", df[df.yr>=2020])]:
    for fwd in ["profit_1M","profit_2M","profit_3M"]:
        ic, t, n = rank_ic(dd, fwd)
        print(f"{wlab:>10} {fwd:>8} {ic:>8.3f} {t:>6.1f} {n:>8}")

print("\n=== Quintiles of fair_discount -> mean forward return (%), pooled ===")
df["Q"] = df.groupby("time")["fair_discount"].transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=[1,2,3,4,5]) if s.nunique()>=5 else np.nan)
qt = df.dropna(subset=["Q"]).groupby("Q", observed=True).agg(N=("Q","size"),
        disc=("fair_discount","mean"), p1M=("profit_1M","mean"), p2M=("profit_2M","mean"), p3M=("profit_3M","mean")).round(2)
print(qt.to_string())
q5,q1 = qt.loc[5],qt.loc[1]
print(f"\nLong-short Q5-Q1 (most-cheap minus most-rich): 1M {q5.p1M-q1.p1M:+.2f}pp | 2M {q5.p2M-q1.p2M:+.2f}pp | 3M {q5.p3M-q1.p3M:+.2f}pp")

# OOS-only quintile (the honest test)
oos = df[df.yr>=2020].dropna(subset=["Q"])
qto = oos.groupby("Q", observed=True).agg(p1M=("profit_1M","mean"),p2M=("profit_2M","mean"),p3M=("profit_3M","mean")).round(2)
print(f"OOS-only  Q5-Q1: 1M {qto.loc[5].p1M-qto.loc[1].p1M:+.2f}pp | 2M {qto.loc[5].p2M-qto.loc[1].p2M:+.2f}pp | 3M {qto.loc[5].p3M-qto.loc[1].p3M:+.2f}pp")

print("\n=== DISPLAY BASKET: latest date, top 25 by fair_discount (proxy rating-1/2 = quality-gated) ===")
last = df[df.time==df.time.max()].copy().sort_values("fair_discount", ascending=False).head(25)
disp = last[["ticker","Price","fair_price","fair_discount","PE","PE_MA5Y","ROIC5Y","FSCORE"]].copy()
disp["fair_discount"] = (disp["fair_discount"]*100).round(1)
disp["fair_price"] = disp["fair_price"].round(0); disp["Price"]=disp["Price"].round(0)
disp.columns = ["ticker","price","fair_VND","disc%","PE","PE_MA5Y","ROIC5Y","FSCORE"]
print(f"(as of {pd.to_datetime(df.time.max()).date()})")
print(disp.to_string(index=False))
print("\nNOTE: v1 = pure own-history multiple reversion, quality-gated. CF_OA_3Y absent in cache -> golden-floor proxy = ROE_Min3Y>=0 & FSCORE>=5.")
print("profit_* = forward LABEL only. If edge holds OOS -> layer moat(fade)/liquidity(haircut) and test if they ADD.")
