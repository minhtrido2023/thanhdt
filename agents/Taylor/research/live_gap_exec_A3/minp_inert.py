"""A3: vì sao LAG_ADV_MINP trơ — đếm lệnh LAG (mua) trong ledger rơi vào (mã, ngày fill) có < N dòng lịch sử TRƯỚC ngày fill
(tức key ADV pit chỉ tồn tại khi MINP ≤ số dòng đó). Usage: minp_inert.py ledger.csv"""
import sys, duckdb, pandas as pd
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker/*.parquet"
df = duckdb.connect().execute(f"SELECT ticker, time FROM read_parquet('{C}') WHERE time <= DATE '2026-06-19' ORDER BY ticker, time").df()
df["time"] = pd.to_datetime(df["time"]); df["prior_rows"] = df.groupby("ticker").cumcount()   # số dòng TRƯỚC t
X = pd.read_csv(sys.argv[1], low_memory=False); T = X[(X.record_type == "TX") & (X.book.astype(str) == "LAG")].copy()
T["time"] = pd.to_datetime(T.ymd.astype(str).str[:10]); print("LAG TX theo action:", T.action.value_counts().to_dict())
B = T[T.action == "buy"].merge(df, on=["ticker", "time"], how="left")
print("LAG buy tx", len(B), "| prior_rows min", int(B.prior_rows.min()), "p1", B.prior_rows.quantile(.01))
for n in (10, 20, 40, 60, 80): print(f"  buy tx với prior_rows < {n}: {int((B.prior_rows < n).sum())}")
# ứng viên LAG bị chặn (không có tx) không hiện trong ledger ⇒ kiểm thêm: mã có tx LAG bất kỳ mà lần mua ĐẦU nằm < 60 phiên kể từ niêm yết
