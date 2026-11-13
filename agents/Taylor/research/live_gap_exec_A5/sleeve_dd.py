"""A5 việc 2c: DD THỰC TẾ sleeve BAL+LAG live (cổ phiếu, không gồm tiền) vs phân phối DD cửa sổ cùng độ dài của engine.
Live: fills ../live_gap_phase0_20261112/fills_booked.csv (journal per-account, book gắn bởi journal_book_attach.py),
  định giá total-return theo BQ Close (đơn vị điều chỉnh = qty × Price_d/Close_d tại ngày fill ⇒ cổ tức/thưởng đã nằm trong Close),
  phí 0,097%/chiều + thuế bán 0,1%. TWR Modified-Dietz theo ngày; ngày fill: giá fill → Close cuối ngày.
Engine: ledger L3P pin0% (md5 80f509ec, A4) — sleeve = bal_stocks_ref+lag_stocks_ref, dòng tiền = TX buy/sell/fee.
  Phân phối: (i) mọi cửa sổ trượt H phiên trong lịch sử; (ii) block bootstrap vòng L=21, B=4000, seed 12345 trên lợi suất ngày.
Cũng làm cho combined_nav (toàn danh mục engine) để thấy khác biệt sleeve vs tổng."""
import sys, numpy as np, pandas as pd
FEE, TAX = 0.00097, 0.001
f = pd.read_csv('../live_gap_phase0_20261112/fills_booked.csv'); f = f[f.book_inferred.isin(['BAL', 'LAG'])].copy()
px = pd.read_csv('logs/bq_sleeve_px.csv', parse_dates=['time']); px['Price'] = px.Price.fillna(px.Close)
C = px.pivot(index='time', columns='ticker', values='Close'); P = px.pivot(index='time', columns='ticker', values='Price')
days = C.index[(C.index >= pd.Timestamp(f.date.min()))]
def mdd(r):
    w = np.cumprod(1 + np.asarray(r)); return float((w / np.maximum.accumulate(np.r_[1.0, w])[1:] - 1).min())
def live_series(sub):
    units = {}; V_prev = 0.0; rs = []; vals = []
    for d in days:
        ff = sub[pd.to_datetime(sub.date) == d]; B = S = 0.0
        for _, x in ff.iterrows():
            u = x.qty * P.at[d, x.ticker] / C.at[d, x.ticker]   # units × Close_d = qty × Price_d
            if x.side == 'buy': units[x.ticker] = units.get(x.ticker, 0) + u; B += x.qty * x.price * (1 + FEE)
            else: units[x.ticker] = units.get(x.ticker, 0) - u; S += x.qty * x.price * (1 - FEE - TAX)
        V = sum(u * C.at[d, t] for t, u in units.items())
        den = V_prev + B
        rs.append((V - V_prev - B + S) / den if den > 0 else 0.0); vals.append(V); V_prev = V
    return pd.Series(rs, index=days), pd.Series(vals, index=days), units
out = {}
for acct in ['SpaceX', 'ZaloPay']:
    r, v, u = live_series(f[f.acct == acct]); out[acct] = (r, v)
    neg = {k: round(x, 3) for k, x in u.items() if x < -1e-6}
    print(f"LIVE {acct}: phiên {len(r)} ({days[0].date()}→{days[-1].date()}), TWR {np.prod(1+r)-1:+.2%}, MaxDD {mdd(r):.2%}, "
          f"giá trị sleeve max {v.max()/1e6:.0f}tr cuối {v.iloc[-1]/1e6:.0f}tr; units âm={neg}")
H = len(days)
L = pd.read_csv(sys.argv[1], low_memory=False)
D = L[L.record_type == 'DAILY'].copy(); D['ymd'] = pd.to_datetime(D.ymd); D = D.set_index('ymd')
S = D.bal_stocks_ref.astype(float) + D.lag_stocks_ref.astype(float)
T = L[L.record_type == 'TX'].copy(); T['ymd'] = pd.to_datetime(T.ymd)
g = T.groupby('ymd')[['buy_amount', 'sell_amount', 'fee']].sum().reindex(S.index).fillna(0)
den = S.shift(1) + g.buy_amount
rS = ((S - S.shift(1) - g.buy_amount + g.sell_amount - g.fee) / den).where(den > 0, 0.0).iloc[1:]
rN = D.combined_nav.astype(float).pct_change().iloc[1:]
rng = np.random.default_rng(12345)
for name, r in [('engine sleeve BAL+LAG', rS), ('engine combined_nav', rN)]:
    a = r.values; n = len(a)
    hist = np.array([mdd(a[i:i+H]) for i in range(n - H + 1)])
    nb = int(np.ceil(H / 21)); bs = []
    for _ in range(4000):
        st = rng.integers(0, n, nb); idx = (st[:, None] + np.arange(21)[None, :]).ravel()[:H] % n; bs.append(mdd(a[idx]))
    bs = np.array(bs); out[name] = (hist, bs)
    print(f"{name}: H={H} phiên | lịch sử trượt: p50 {np.median(hist):.2%} p5 {np.quantile(hist,.05):.2%} min {hist.min():.2%} | "
          f"bootstrap: p50 {np.median(bs):.2%} p5 {np.quantile(bs,.05):.2%} p1 {np.quantile(bs,.01):.2%}")
for acct in ['SpaceX', 'ZaloPay']:
    m = mdd(out[acct][0]); h, b = out['engine sleeve BAL+LAG']
    print(f"{acct} live sleeve MaxDD {m:.2%}: percentile trong engine-sleeve lịch sử {np.mean(h <= m):.1%} (tỉ lệ cửa sổ engine TỆ hơn hoặc bằng), bootstrap {np.mean(b <= m):.1%}")
