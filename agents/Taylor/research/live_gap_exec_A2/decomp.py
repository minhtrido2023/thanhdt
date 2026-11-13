"""A2: phân rã chênh L1(off)→L2(lag) theo loại ADV ở ngày fill đầu (BQ Volume_3M_P50: NULL / <=0 / >0).
Holding LAG (holding_id) có mặt ở L1 mà không có ở L2 (theo ticker+ngày fill đầu) = bị chặn. P&L = sell - buy (+ giá trị
còn giữ cuối kỳ bỏ qua; chỉ holding đã đóng). Usage: decomp.py L1.csv L2.csv [from to]"""
import sys, duckdb, pandas as pd
C = "/home/trido/thanhdt/WorkingClaude/data/bq_cache_asof20260729_postrestate/ticker/*.parquet"
a, b = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else ("2014-01-01", "2026-12-31")
def hold(p):
    X = pd.read_csv(p, low_memory=False); T = X[(X.record_type == "TX") & (X.book.astype(str) == "LAG")].copy()
    T["ymd"] = pd.to_datetime(T.ymd.astype(str).str[:10])
    g = T.groupby("holding_id").agg(ticker=("ticker", "first"), d0=("ymd", "min"), buy=("buy_amount", "sum"),
                                     sell=("sell_amount", "sum"), fee=("fee", "sum"), nsell=("action", lambda s: (s == "sell").sum()))
    g["entry"] = g.index.str.split("_").str[1]
    return g[(g.d0 >= a) & (g.d0 <= b)]
h1, h2 = hold(sys.argv[1]), hold(sys.argv[2])
k2 = set(zip(h2.ticker, h2.entry))
h1["blocked"] = [(t, e) not in k2 for t, e in zip(h1.ticker, h1.entry)]
con = duckdb.connect(); tk = ",".join(f"'{t}'" for t in set(h1.ticker))
L = con.execute(f"SELECT ticker, time, Volume_3M_P50 v FROM read_parquet('{C}') WHERE ticker IN ({tk})").df()
L["time"] = pd.to_datetime(L.time); L = L.set_index(["ticker", "time"])["v"]
def cat(t, d):
    v = L.get((t, d), None)
    return "NULL" if v is None or pd.isna(v) else ("<=0" if v <= 0 else ">0")
h1["adv"] = [cat(t, d) for t, d in zip(h1.ticker, h1.d0)]
h1["pnl"] = h1.sell - h1.buy
cl = h1[h1.nsell > 0]
print(f"window {a}..{b}: L1 holdings {len(h1)} | blocked under L2 {int(h1.blocked.sum())}")
print((cl.groupby(["blocked", "adv"]).agg(n=("pnl", "size"), buy_B=("buy", lambda s: s.sum()/1e9), pnl_B=("pnl", lambda s: s.sum()/1e9))).round(2).to_string())
# Holding NULL-ở-L1 còn mua được ở L2: so cỡ mua / P&L hai bên (L2 bị trần 20% ADV × ≤5 phiên)
m = h1[(h1.adv == "NULL") & ~h1.blocked & (h1.nsell > 0)].merge(h2, on=["ticker", "entry"], suffixes=("_L1", "_L2"))
if len(m):
    print(f"NULL-at-L1 holdings still bought in L2: n={len(m)} buy L1 {m.buy_L1.sum()/1e9:.2f}B -> L2 {m.buy_L2.sum()/1e9:.2f}B; "
          f"pnl L1 {(m.sell_L1-m.buy_L1).sum()/1e9:.2f}B -> L2 {(m.sell_L2-m.buy_L2).sum()/1e9:.2f}B")
