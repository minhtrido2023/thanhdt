"""A7: độ phơi nhiễm cổ phiếu theo NAV — (bal_stocks+lag_stocks)/combined_nav, ETF riêng; trung bình theo ngày, toàn kỳ + trong 2 cửa sổ DD sâu.
Usage: expo.py lab=ledger ..."""
import sys, pandas as pd, numpy as np
for lab, p in (a.split("=", 1) for a in sys.argv[1:]):
    X = pd.read_csv(p, low_memory=False); D = X[X.record_type == "DAILY"].copy(); D["ymd"] = pd.to_datetime(D.ymd.astype(str).str[:10])
    D = D.set_index("ymd").sort_index(); f = lambda c: D[c].astype(float).fillna(0)
    nav = f("combined_nav"); stk = (f("bal_stocks_ref") + f("lag_stocks_ref")) / nav; etf = (f("bal_etf_ref") + f("lag_etf_ref")) / nav
    lag = f("lag_stocks_ref") / nav; dd = nav / nav.cummax() - 1; t = dd.idxmin()
    w = (D.index >= t - pd.Timedelta(days=120)) & (D.index <= t)
    print(f"{lab:>10} stock {stk.mean():.1%} (LAG {lag.mean():.1%}) etf {etf.mean():.1%} | MaxDD {dd.min():.1%} đáy {t.date()} | 120 ngày trước đáy: stock {stk[w].mean():.1%} LAG {lag[w].mean():.1%}")
