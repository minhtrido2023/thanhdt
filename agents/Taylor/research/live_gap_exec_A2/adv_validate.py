"""A2 bước 1: đo đường ADV thay thế (trung vị Volume N phiên) so với BQ Volume_3M_P50 trên cache 0729.
Biến thể: incl = cửa sổ [t-N+1..t] (gồm ngày t), excl = [t-N..t-1] (PIT, không gồm ngày t).
Phiên = các dòng có của mã đó (BQ ticker có dòng cả ngày Volume=0?). Đo: sai số tương đối trung vị/p90 khi Volume_3M_P50 không NULL,
phủ ngày NULL. Usage: $DNA_PYEXE adv_validate.py"""
import duckdb, numpy as np, pandas as pd, sys
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker/*.parquet"
con = duckdb.connect()
df = con.execute(f"""SELECT ticker, time, Volume, Volume_3M_P50, COALESCE(Price, Close) AS Px
  FROM read_parquet('{C}') WHERE time BETWEEN DATE '2013-01-01' AND DATE '2026-06-19' ORDER BY ticker, time""").df()
df["time"] = pd.to_datetime(df["time"])
print("rows", len(df), "tickers", df.ticker.nunique(), "min", df.time.min().date())
out = {}
g = df.groupby("ticker", sort=False)["Volume"]
for N in (60, 63):
    df[f"incl{N}"] = g.transform(lambda s: s.rolling(N, min_periods=N//2).median())
    df[f"excl{N}"] = g.transform(lambda s: s.shift(1).rolling(N, min_periods=N//2).median())
m = df[(df.time >= "2014-01-01") & df.Volume_3M_P50.notna() & (df.Volume_3M_P50 > 0)]
for c in ("incl60", "excl60", "incl63", "excl63"):
    x = m[m[c].notna() & (m[c] > 0)]
    r = (x[c] / x.Volume_3M_P50 - 1).abs()
    print(f"{c}: n={len(x)} exact(<1e-9)={np.mean(r<1e-9):.4f} |rel| p50={r.median():.4f} p90={r.quantile(.9):.4f} p99={r.quantile(.99):.4f} within5%={np.mean(r<.05):.4f}")
# NULL coverage
v = df[df.time >= "2014-01-01"]
nul = v[v.Volume_3M_P50.isna() & (v.Volume.fillna(0) > 0)]
print("NULL Volume_3M_P50 on traded rows (2014..06-19):", len(nul), "tickers", nul.ticker.nunique(), "| excl60 available:", int(nul.excl60.notna().sum()), "(>0:", int((nul.excl60 > 0).sum()), ")")
by = nul.groupby(nul.time.dt.to_period("Q")).size()
print("NULL by quarter (top 12):"); print(by.sort_values(ascending=False).head(12).to_string())
nul2 = nul.assign(adv=nul.excl60 * nul.Px)
print("NULL rows 2015Q3-2016Q2 ADV(excl60 VND) quantiles:", nul2[(nul2.time>='2015-07-01')&(nul2.time<'2016-07-01')].adv.quantile([.1,.5,.9]).round(-6).to_dict())
