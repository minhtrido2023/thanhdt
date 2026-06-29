"""EV / blast-radius of the gap-adaptive fill rule, by LIQUIDITY tier (the names we actually trade).
Daily proxy on ticker_prune (same construction as gap_adaptive_proxy.py). Focus: down-gap (z<-2) buy-at-open
edge + how OFTEN it fires (blast radius) + does it concentrate in stress years (when we deploy most)."""
import duckdb, numpy as np, pandas as pd
pd.set_option("display.width", 200)
PARQ = "data/bq_cache/ticker_prune.parquet"
q = f"""
WITH base AS (
  SELECT ticker, time, Open, Close, Close_T1, Trading_Value_1M_P50 AS liq, Close/Close_T1-1 AS ret, profit_1M
  FROM read_parquet('{PARQ}')
  WHERE time>=DATE '2014-01-01' AND Open>0 AND Close_T1>0 AND profit_1M IS NOT NULL
),
z AS (SELECT *, Open/Close_T1-1 AS gap, Close/Open-1 AS intraday,
        stddev_samp(ret) OVER (PARTITION BY ticker ORDER BY time ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS rvol
      FROM base)
SELECT time, gap, intraday, rvol, liq, profit_1M AS fwd20 FROM z
WHERE rvol>0 AND liq>=5e9 AND abs(Open/Close_T1-1)<=0.15
"""
df = duckdb.connect().execute(q).df()
df["gap_z"] = df["gap"]/df["rvol"]; df = df[df["gap_z"].abs()<=8].copy()
df["yr"] = pd.to_datetime(df["time"]).dt.year
TIERS = [(5e9,10e9,"5-10B micro"),(10e9,50e9,"10-50B small"),(50e9,200e9,"50-200B mid"),(200e9,1e15,">200B large")]

print(f"=== Down-gap (z<-2) buy-at-OPEN edge by liquidity tier (N={len(df):,} liquid ticker-days) ===")
print(f"{'tier':>14} {'tier_days':>9} {'z<-2 N':>7} {'freq%':>6} {'OpenATC_bps':>11} {'t':>5} {'~11:15save':>10} {'fwd20%':>7}")
for lo,hi,lab in TIERS:
    t = df[(df["liq"]>=lo)&(df["liq"]<hi)]
    dn = t[t["gap_z"]<-2]
    if len(dn)<5: continue
    bps = dn["intraday"].mean()*1e4; tt = dn["intraday"].mean()/(dn["intraday"].std()/np.sqrt(len(dn)))
    freq = len(dn)/len(t)*100
    print(f"{lab:>14} {len(t):>9,} {len(dn):>7,} {freq:>5.2f}% {bps:>10.0f} {tt:>5.1f} {bps*0.56:>9.0f} {dn['fwd20'].mean():>6.2f}")
print("  (~11:15save = est. bps saved vs CURRENT rule buying at 11:15 = OpenATC*0.56, the 16-name down-gap path ratio)")

print(f"\n=== UP-gap (z>2) give-back by tier (current rule already waits = correct; shown for completeness) ===")
print(f"{'tier':>14} {'z>2 N':>7} {'freq%':>6} {'OpenATC_bps':>11} {'t':>5}")
for lo,hi,lab in TIERS:
    t = df[(df["liq"]>=lo)&(df["liq"]<hi)]; up = t[t["gap_z"]>2]
    if len(up)<5: continue
    bps = up["intraday"].mean()*1e4; tt = up["intraday"].mean()/(up["intraday"].std()/np.sqrt(len(up)))
    print(f"{lab:>14} {len(up):>7,} {len(up)/len(t)*100:>5.2f}% {bps:>10.0f} {tt:>5.1f}")

print(f"\n=== Does down-gap CONCENTRATE in stress years? (z<-2 freq by year) ===")
yr = df.groupby("yr").apply(lambda g:(g["gap_z"]<-2).mean()*100, include_groups=False).round(2)
print(yr.to_string())
print("\nBLAST-RADIUS READ: freq% = share of buy-able days that gap down abnormally. EV/yr ~ (our buy-fills/yr) x freq x bps.")
print("Stress-year concentration => the edge fires most exactly when the recovery sleeve deploys = aligned, not uniform.")
