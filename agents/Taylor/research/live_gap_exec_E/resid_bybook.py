"""Truy phần DƯ của waterfall: đóng góp pp theo BOOK live, theo tháng (từ 04/08 có sổ). pnl_book,t = Σ_tickers qty_{t−1}·Price_{t−1}·
(Close_t/Close_{t−1} − 1) (Close BQ điều chỉnh ⇒ tổng lợi suất gồm cổ tức/chia tách; Price = giá thực); pp = Σ pnl/NAV_{t−1}.
Bỏ qua P&L trong phiên của lệnh mới (đã nằm ở W4). Engine: Σ (stocks_ref|etf_ref)_{t−1}/NAV_{t−1} · r_rổ_t, r_rổ từ chênh ref trừ dòng TX."""
import glob, json, os, sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../live_gap_phase1c_20261112")))
import decompose3 as D3
R = os.path.dirname(os.path.abspath(__file__)); LB = f"{D3.R}/live_books"
X = pd.read_parquet(f"{R}/sb/data/bq_cache_asof20261111/ticker/2026.parquet", columns=["time", "ticker", "Close", "Price"])
X["time"] = pd.to_datetime(X.time).dt.strftime("%Y-%m-%d"); C = X.pivot(index="time", columns="ticker", values="Close"); P = X.pivot(index="time", columns="ticker", values="Price")
M = [("thang 8 (từ 04/08)", "2026-08-04", "2026-08-31"), ("thang 9", "2026-08-31", "2026-09-30"), ("thang 10", "2026-09-30", "2026-10-30"), ("Nov→11/11", "2026-10-30", "2026-11-11")]
rows = []
for acct in ("SpaceX", "ZaloPay"):
    h = pd.read_csv(f"{D3.EL}/nav_history_{acct}.csv").drop_duplicates("date", keep="last").set_index("date")
    nav = h["nav"].astype(float) if acct == "SpaceX" else pd.read_csv(f"{D3.EL}/nav_sleeve_history_ZaloPay.csv").drop_duplicates("date", keep="last").set_index("date")["nav_b"].astype(float)
    books = {}
    for f in sorted(glob.glob(f"{LB}/{acct}_2026-*.json")):
        ds = os.path.basename(f)[len(acct) + 1:-5]
        if ds < "2026-08-04" or os.path.getsize(f) == 0: continue
        q = {}
        for l in json.load(open(f))["lots"]:
            if l["book"] == "EXCLUDED": continue
            q[(l["book"], l["ticker"])] = q.get((l["book"], l["ticker"]), 0) + l["qty"]
        books[ds] = q
    days = [d for d in sorted(books) if d in C.index]; pnl = {}  # bỏ ngày nghỉ (sổ chụp nhưng không có phiên)
    for i in range(1, len(days)):
        d0, d1 = days[i - 1], days[i]
        for (bk, t), qty in books[d0].items():
            if t not in C or pd.isna(C.at[d1, t]) or pd.isna(C.at[d0, t]): continue
            v = qty * P.at[d0, t] * (C.at[d1, t] / C.at[d0, t] - 1) / float(nav.get(d0, nav[nav.index <= d0].iloc[-1]))
            pnl[(d1, bk)] = pnl.get((d1, bk), 0) + v
    S = pd.Series(pnl); S.index = pd.MultiIndex.from_tuples(S.index, names=["d", "book"])
    for lab, a, b in M:
        s = S[(S.index.get_level_values(0) > a) & (S.index.get_level_values(0) <= b)].groupby(level=1).sum() * 100
        for bk, v in s.items(): rows.append(dict(TK=acct, ky=lab, book=bk, pp=v))
T = pd.DataFrame(rows); T.to_csv(f"{R}/resid_bybook_live.csv", index=False, float_format="%.3f")
print(T.pivot_table(index=["TK", "book"], columns="ky", values="pp", aggfunc="sum").round(2).to_string())
