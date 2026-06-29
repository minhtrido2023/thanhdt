"""Gap-adaptive fill study (proxy) — should Layer-3 fill timing adapt to an ABNORMAL open?

Setup: a name is on the buy-list (alpha already decided). At the open it gaps vs its recent
daily vol. Question = pure EXECUTION: buy at OPEN (chase) or wait to ATC (Close)? And is a gap
two-sided (up = don't-chase slippage problem; down = lean-in alpha-capture)?

Proxy (we lack intraday bars for the full universe — only 16 names in data/intraday_1m):
  gap   = Open/Close_T1 - 1                 (overnight jump)
  rvol  = stddev(daily ret) over trailing 20d, CAUSAL (excludes today)   [= "normal 1M pattern"]
  gap_z = gap / rvol                        (abnormality of the open)
  intraday = Close/Open - 1                 (within-day give-back/continuation = the Open-vs-ATC delta)
  fwd20 = profit_1M (T+20 drift from Close; research use, NOT a live filter)

Decision read (maps onto the existing Layer-3 Open-vs-ATC choice):
  intraday < 0  -> ATC is CHEAPER than Open -> for a BUY, WAITING saved |intraday|.  (don't chase)
  intraday > 0  -> Open was cheaper          -> buying at Open captured it.           (lean in)
So: big UP-gap with intraday<0 => confirm "don't chase up-gap";
    big DOWN-gap with intraday>0 => confirm "accelerate fill on down-gap" (alpha side).
Also check fwd20 by bucket: is the gap informative about the thesis, or pure noise?

Universe = ticker_prune (liquid, quality-gated), 2014+, liquidity floor 5B/day, |gap|<=0.15
(VN price band; beyond = corp-action/adjustment artifact). Walk-forward IS 2014-19 / OOS 2020+.
"""
import duckdb, numpy as np, pandas as pd
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)
PARQ = "data/bq_cache/ticker_prune.parquet"
LIQ_FLOOR = 5e9

q = f"""
WITH base AS (
  SELECT ticker, time, Open, Close, Close_T1, MA50, PC1M, profit_1M,
         ID_Current, ID_Release, Trading_Value_1M_P50,
         Close/Close_T1 - 1 AS ret
  FROM read_parquet('{PARQ}')
  WHERE time >= DATE '2014-01-01' AND Open IS NOT NULL AND Close_T1 IS NOT NULL
        AND Close_T1 > 0 AND Open > 0 AND profit_1M IS NOT NULL
),
z AS (
  SELECT *,
    Open/Close_T1 - 1 AS gap,
    Close/Open - 1    AS intraday,
    stddev_samp(ret) OVER (PARTITION BY ticker ORDER BY time
                           ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS rvol
  FROM base
)
SELECT ticker, time, gap, intraday, rvol, profit_1M AS fwd20, MA50, PC1M, Close,
       ID_Current - ID_Release AS fresh, Trading_Value_1M_P50 AS liq
FROM z
WHERE rvol > 0 AND Trading_Value_1M_P50 >= {LIQ_FLOOR} AND abs(Open/Close_T1 - 1) <= 0.15
"""
df = duckdb.connect().execute(q).df()
df["gap_z"] = df["gap"] / df["rvol"]
df["yr"] = pd.to_datetime(df["time"]).dt.year
df = df[df["gap_z"].abs() <= 8].copy()                 # drop pathological z (thin rvol tails)
BINS = [-99, -2, -1, 1, 2, 99]
LAB  = ["z<-2 (big DOWN)", "-2..-1", "-1..1 (normal)", "1..2", "z>2 (big UP)"]
df["bucket"] = pd.cut(df["gap_z"], BINS, labels=LAB)

def tbl(d, title):
    g = d.groupby("bucket", observed=True)
    out = pd.DataFrame({
        "N": g.size(),
        "intraday_bps": (g["intraday"].mean() * 1e4).round(1),     # Open->Close, bps. <0 = ATC cheaper for a BUY
        "intraday_t":  (g["intraday"].mean() / (g["intraday"].std() / np.sqrt(g.size()))).round(1),
        "fwd20_%":     (g["fwd20"].mean()).round(2),               # T+20 drift from Close (profit_1M already %)
        "fwd20_t":     (g["fwd20"].mean() / (g["fwd20"].std() / np.sqrt(g.size()))).round(1),
    })
    print(f"\n=== {title} (N={len(d):,}) ===")
    print(out.to_string())

print(f"Loaded {len(df):,} ticker-days, {df['ticker'].nunique()} names, {df['yr'].min()}-{df['yr'].max()}")
tbl(df, "ALL buy-able liquid universe")
tbl(df[df["yr"] <= 2019], "IS 2014-19")
tbl(df[df["yr"] >= 2020], "OOS 2020+")
# book split: momentum (BAL proxy = uptrend) vs earnings-fresh (LAG/PEAD proxy)
tbl(df[(df["Close"] > df["MA50"]) & (df["PC1M"] > 0)], "MOMENTUM proxy (Close>MA50 & PC1M>0)")
tbl(df[(df["fresh"] >= 0) & (df["fresh"] <= 40)], "EARNINGS-FRESH proxy (<=40 sessions since release)")

# headline decision numbers
up = df[df["gap_z"] > 2]; dn = df[df["gap_z"] < -2]
print(f"\n--- DECISION SUMMARY ---")
print(f"Big UP-gap (z>2):   N={len(up):,}  intraday {up['intraday'].mean()*1e4:+.1f} bps  fwd20 {up['fwd20'].mean():+.2f}%")
print(f"Big DOWN-gap (z<-2):N={len(dn):,}  intraday {dn['intraday'].mean()*1e4:+.1f} bps  fwd20 {dn['fwd20'].mean():+.2f}%")
print(f"Normal (-1..1):     N={len(df[df['gap_z'].between(-1,1)]):,}  fwd20 {df[df['gap_z'].between(-1,1)]['fwd20'].mean():+.2f}%")
print("\nNOTE: gap_z is a DAILY proxy for intraday abnormality (full-universe intraday bars absent);")
print("intraday=Close/Open-1 maps onto the Layer-3 Open-vs-ATC choice. profit_1M = research only.")
