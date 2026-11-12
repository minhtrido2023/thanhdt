"""Tóm tắt các ledger _exp_gap_* (job Taylor_20261112_104204): NAV đầu/cuối, lợi suất kỳ, theo tháng,
tỷ trọng cổ phiếu TB (không tính custom30V park), số lệnh BAL/LAG/CAPIT, md5. Usage: leg_summary.py out.json f1.csv ..."""
import sys, json, hashlib, pandas as pd
out = {}
for p in sys.argv[2:]:
    tag = p.split("_exp_gap_")[1].split("_univpit")[0]
    X = pd.read_csv(p, low_memory=False); X["ymd"] = pd.to_datetime(X["ymd"].astype(str).str[:10], errors="coerce")
    D = X[X.record_type == "DAILY"].set_index("ymd").sort_index()
    nav = D["combined_nav"].astype(float); meta = X[X.record_type == "META"].set_index("key")["value"].to_dict()
    nav0 = float(meta.get("nav_total", nav.iloc[0])) if False else None
    T = X[X.record_type == "TX"]; buys = T[(T.action == "buy") & ~T.ticker.astype(str).str.startswith("CUSTOM")]
    stocks = D["bal_stocks_ref"].astype(float) + D["lag_stocks_ref"].astype(float)
    etf = D["bal_etf_ref"].astype(float) + D["lag_etf_ref"].astype(float)
    m = nav.groupby(nav.index.to_period("M")).last()
    out[tag] = dict(md5=hashlib.md5(open(p, "rb").read()).hexdigest(), first=str(nav.index[0].date()), last=str(nav.index[-1].date()),
        nav_first=nav.iloc[0], nav_last=nav.iloc[-1], n_days=len(nav),
        stock_share_mean=float((stocks / nav).mean()), etf_share_mean=float((etf / nav).mean()),
        month_end_nav={str(k): float(v) for k, v in m.items()},
        buys_by_book={b: int(n) for b, n in buys.groupby("book").size().items()},
        buys_by_tier=buys.groupby(buys.play_type.astype(str).str.replace(r"_E\d+$", "_E*", regex=True)).size().to_dict(),
        buy_tickers=sorted(set(buys.ticker.astype(str))))
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
for k, v in out.items(): print(k, v["first"], v["last"], f"{v['nav_first']:.4e}->{v['nav_last']:.4e}", v["md5"][:8], v["buys_by_book"], f"stk={v['stock_share_mean']:.2f} etf={v['etf_share_mean']:.2f}")
