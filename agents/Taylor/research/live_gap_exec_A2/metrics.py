"""A2: FULL/IS(2014-19)/OOS(2020+) CAGR (lịch, 365.25) / Sharpe / MaxDD / Calmar + lợi suất 2015, 2016, LAG stocks TB 2015Q4,
số lệnh mua LAG. Usage: metrics.py f1.csv ...  (đầu ra cùng định nghĩa với leg_metrics.log Luồng A — kiểm tái lập trên L2 cũ)"""
import sys, hashlib, numpy as np, pandas as pd
def seg(nav, a, b):
    s = nav[(nav.index >= a) & (nav.index <= b)]
    # như engine: kỳ bắt đầu từ phiên đầu của kỳ (không nối điểm cuối kỳ trước)
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    r = s.pct_change().dropna()
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(len(r) / yrs)
    dd = (s / s.cummax() - 1).min()
    return cagr, sh, dd
for p in sys.argv[1:]:
    X = pd.read_csv(p, low_memory=False); X["ymd"] = pd.to_datetime(X["ymd"].astype(str).str[:10], errors="coerce")
    D = X[X.record_type == "DAILY"].set_index("ymd").sort_index(); nav = D["combined_nav"].astype(float)
    tag = p.split("_exp_")[1].split("_univpit")[0]
    print(f"== {tag}  md5 {hashlib.md5(open(p,'rb').read()).hexdigest()}")
    for nm, a, b in (("FULL", "2014-01-01", "2026-12-31"), ("IS", "2014-01-01", "2019-12-31"), ("OOS", "2020-01-01", "2026-12-31")):
        c, s, d = seg(nav, pd.Timestamp(a), pd.Timestamp(b)); print(f"   {nm:4s} CAGR {c*100:6.2f}%  Sharpe {s:5.2f}  MaxDD {d*100:6.1f}%  Calmar {c/abs(d):5.2f}")
    y = nav.groupby(nav.index.year).last(); y0 = nav.iloc[0]
    yr = y.pct_change(); yr.iloc[0] = y.iloc[0] / y0 - 1
    print("   year:", " ".join(f"{k}:{v*100:.1f}" for k, v in yr.items() if k in (2014, 2015, 2016, 2017, 2018)))
    q = D.loc["2015-10-01":"2015-12-31", "lag_stocks_ref"].astype(float).mean() / 1e9
    T = X[X.record_type == "TX"]; lb = T[(T.action == "buy") & (T.book.astype(str) == "LAG")]
    lb15 = lb[pd.to_datetime(lb.ymd.astype(str).str[:10], errors="coerce").between("2015-07-01", "2016-06-30")]
    print(f"   LAG stocks mean 2015Q4 {q:.1f}B | LAG buy tx total {len(lb)} | 2015H2-16H1 {len(lb15)}")
