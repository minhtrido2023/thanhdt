"""A3 bước 1a: BQ Volume_3M_P50 (nguồn adv_vnd live) bắt đầu có giá trị từ dòng thứ mấy của mã, và ở cửa sổ
chưa đủ 60 dòng nó có bằng trung vị các dòng hiện có (gồm t) không ⇒ min_periods tương đương của BQ.
Mã niêm yết SAU 2014-06 (dòng đầu tiên trong cache ≥ 2014-06-01) để chắc dòng đầu = phiên đầu. Usage: $DNA_PYEXE minp_probe.py"""
import duckdb, numpy as np, pandas as pd
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker/*.parquet"
df = duckdb.connect().execute(f"""SELECT ticker, time, Volume, Volume_3M_P50 FROM read_parquet('{C}')
  WHERE time <= DATE '2026-06-19' ORDER BY ticker, time""").df()
first = df.groupby("ticker").time.transform("min"); df = df[first >= "2014-06-01"].copy()
df["k"] = df.groupby("ticker").cumcount() + 1                       # số dòng tính tới t (gồm t)
df["med_incl"] = df.groupby("ticker")["Volume"].transform(lambda s: s.rolling(60, min_periods=1).median())
print("mã niêm yết sau 2014-06:", df.ticker.nunique(), "dòng", len(df))
f = df[df.Volume_3M_P50.notna()].groupby("ticker").k.min()
print("k tại dòng non-NULL ĐẦU TIÊN — phân vị:", f.quantile([0, .1, .25, .5, .75, .9, 1]).to_dict())
print("đếm k đầu tiên (top 10):", f.value_counts().head(10).to_dict())
for lo, hi in ((1, 9), (10, 19), (20, 39), (40, 59), (60, 10**9)):
    x = df[(df.k >= lo) & (df.k <= hi)]
    nn = x.Volume_3M_P50.notna()
    y = x[nn & (x.Volume_3M_P50 > 0)]
    ex = np.mean(np.abs(y.med_incl / y.Volume_3M_P50 - 1) < 1e-9) if len(y) else float("nan")
    print(f"k∈[{lo},{hi}]: dòng {len(x)} | non-NULL {nn.mean():.4f} | khớp trung vị-hiện-có (gồm t) {ex:.4f} (n={len(y)})")
