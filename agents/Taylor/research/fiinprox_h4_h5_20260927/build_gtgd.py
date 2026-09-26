"""Daily market turnover (GTGD, bn VND) from the FULL `ticker` table -- no universe filter
(avoids the coding_guidelines 9b ticker_prune look-ahead-universe anti-pattern)."""
import duckdb, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
c = duckdb.connect()
q = f"""
SELECT time AS date,
       SUM(COALESCE(Price, Close) * Volume)/1e9 AS gtgd_bn,
       COUNT(*) AS n_names
FROM read_parquet('{WC}/data/bq_cache/ticker/*.parquet')
WHERE ticker <> 'VNINDEX' AND Volume > 0
GROUP BY 1 ORDER BY 1
"""
df = c.execute(q).df()
df["date"] = pd.to_datetime(df["date"])
df.to_csv("gtgd_daily.csv", index=False)
print(f"rows={len(df)}  {df.date.min().date()} -> {df.date.max().date()}")
print(df.set_index("date").resample("YE")["gtgd_bn"].median().round(0).to_string())
