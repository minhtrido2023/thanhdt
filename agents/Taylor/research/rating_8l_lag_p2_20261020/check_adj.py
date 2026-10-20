"""Kiểm Close đã điều chỉnh corp-action: ở ngày Price thô rơi mạnh (chia tách/CP thưởng), r(Close) phải bình thường."""
import pandas as pd, numpy as np, db_dtypes  # noqa: F401 (dbdate trong parquet)
px = pd.read_parquet("raw/px.parquet").assign(time=lambda d: pd.to_datetime(d.time.astype(str))).sort_values(["ticker", "time"])
g = px.groupby("ticker")
px["rP"] = g.Price.pct_change(); px["rC"] = g.Close.pct_change()
big = px[px.rP < -0.25]
print("ngày Price thô rơi >25%:", len(big), "| trong đó |r(Close)|>15%:", (big.rC.abs() > 0.15).sum())
bad = big[big.rC.abs() > 0.15]
print("các ca |r(Close)|>15% theo năm:", bad.time.dt.year.value_counts().sort_index().to_dict())
print(bad.sort_values("time").tail(12)[["ticker", "time", "rP", "rC"]].to_string())
for tk in ["HPG", "FPT", "MWG", "VHM"]:
    s2 = big[big.ticker == tk]
    print(tk, s2[["time", "rP", "rC"]].to_string(index=False, header=False))
print("tất cả ngày |r(Close)|>40%:", (px.rC.abs() > 0.40).sum(), "/", px.rC.notna().sum())
print(big.sort_values("rP").head(8)[["ticker", "time", "rP", "rC"]].to_string())
