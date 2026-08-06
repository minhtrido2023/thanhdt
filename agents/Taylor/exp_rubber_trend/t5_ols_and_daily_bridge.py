#!/usr/bin/env python3
"""T5 — two gaps left open by T2-T4:
(A) The user asked "đường xu thế 100 ngày" = OLS regression line OR MA100? T2 compared
    them on forward returns only. Compare them on the metric that decided the design
    (recall/precision on real down-cycles) so the answer is apples-to-apples.
(B) The bridge risk: the backtest runs on MONTHLY averages, but production will run
    MA200 on DAILY prints. Daily crosses a line far more often than a monthly average
    does. Calibrate that inflation on a long DAILY series we DO hold — the rubber
    stocks themselves (BQ, 2007+) — by counting MA200-daily breaks vs MA10-monthly
    breaks on the SAME asset."""
import numpy as np, pandas as pd, os

W = "/home/trido/thanhdt/WorkingClaude"
m = pd.read_csv(f"{W}/data/rubber_monthly.csv")
m["dt"] = pd.to_datetime(m["month"].astype(str) + "-15")
m = m[m["price"].notna()].sort_values("dt").reset_index(drop=True)
p = pd.Series(m["price"].astype(float).values, index=m["dt"])
px = p.values


def zigzag(v, thr=0.25):
    piv, mode, last_i = [], None, 0
    for i in range(1, len(v)):
        if mode in (None, "up"):
            if v[i] > v[last_i]: last_i = i
            elif v[i] / v[last_i] - 1 <= -thr:
                piv.append(("P", last_i)); mode, last_i = "down", i; continue
        if mode in (None, "down"):
            if v[i] < v[last_i]: last_i = i
            elif v[i] / v[last_i] - 1 >= thr:
                piv.append(("T", last_i)); mode, last_i = "up", i
    return piv


piv = zigzag(px, 0.25)
cycles = [(i1, i2) for (k1, i1), (k2, i2) in zip(piv, piv[1:]) if k1 == "P" and k2 == "T"]


def breaks_from_below(below, k):
    below = below.fillna(False)
    if k <= 1:
        return below & ~below.shift(1, fill_value=False)
    run = below.copy()
    for j in range(1, k):
        run &= below.shift(j, fill_value=False)
    return run & ~run.shift(1, fill_value=False)


def ma_below(price, win):
    ma = price.rolling(win).mean()
    return (price < ma) & ma.notna()


def reg_below(price, win):
    x = np.arange(win, dtype=float); v = price.values
    fit = pd.Series(np.nan, index=price.index)
    for i in range(win - 1, len(v)):
        b, a = np.polyfit(x, v[i - win + 1:i + 1], 1)
        fit.iloc[i] = a + b * (win - 1)
    return (price < fit) & fit.notna()


def rp(sig):
    ev = [i for i, s in enumerate(sig.values) if s]
    hits = sum(any(j <= e <= kk for e in ev) for j, kk in cycles)
    in_c = set()
    for j, kk in cycles: in_c.update(range(j, kk + 1))
    tp = sum(e in in_c for e in ev)
    yrs = (p.index[-1] - p.index[0]).days / 365.25
    return hits, tp, len(ev), yrs * 12 / len(ev) if ev else 0


print("=" * 86)
print("(A) 'ĐƯỜNG XU THẾ 100 NGÀY' = HỒI QUY hay MA100? — cùng thước đo recall/precision")
print(f"    N chu kỳ giảm >=25% trong 2006-04..2026-07 = {len(cycles)}")
print("=" * 86)
rows = [("OLS hồi quy 5 tháng (~100 phiên)", reg_below(p, 5)),
        ("MA5 monthly       (~MA100 ngày)", ma_below(p, 5)),
        ("MA10 monthly      (~MA200 ngày)", ma_below(p, 10)),
        ("OLS hồi quy 10 tháng (~200 phiên)", reg_below(p, 10))]
for lbl, below in rows:
    for k in (1, 2):
        h, tp, ne, per = rp(breaks_from_below(below, k))
        # whipsaw: back above within 2 obs
        ev = [i for i, s in enumerate(breaks_from_below(below, k).values) if s]
        whip = np.mean([bool((~below.iloc[i+1:i+3]).any()) for i in ev]) * 100 if ev else 0
        print(f"  {lbl:34s} confirm-{k}: recall {h}/{len(cycles)}  "
              f"precision {tp:2d}/{ne:2d}={100*tp/ne if ne else 0:3.0f}%  "
              f"tần suất 1/{per:4.1f} tháng  whipsaw {whip:3.0f}%")

print("\n" + "=" * 86)
print("(B) CẦU NỐI THÁNG -> NGÀY: chuỗi ngày cắt đường nhiều hơn bao nhiêu lần?")
print("    Đo trên tài sản CÓ chuỗi ngày dài thật: chính rổ cổ phiếu cao su (BQ 2007+)")
print("=" * 86)
cache = f"{W}/mike/agents/Taylor/exp_rubber_trend/rubber_stocks.csv"
if not os.path.exists(cache):
    print("  [skip] chưa có cache cổ phiếu"); raise SystemExit(0)
s = pd.read_csv(cache); s["time"] = pd.to_datetime(s["time"])
s = s[s["Close"].notna()]
tot_d = tot_m = 0
for tk, g in s.groupby("ticker"):
    d = g.sort_values("time").set_index("time")["Close"].astype(float)
    if len(d) < 900:
        print(f"  {tk}: {len(d)} phiên — quá ngắn, bỏ"); continue
    yrs = (d.index[-1] - d.index[0]).days / 365.25
    bd = breaks_from_below(ma_below(d, 200), 1).sum()
    bd2 = breaks_from_below(ma_below(d, 200), 2).sum()
    bd5 = breaks_from_below(ma_below(d, 200), 5).sum()
    mo = d.resample("ME").mean()
    bm = breaks_from_below(ma_below(mo, 10), 1).sum()
    bm2 = breaks_from_below(ma_below(mo, 10), 2).sum()
    tot_d += bd; tot_m += bm
    print(f"  {tk}: {yrs:4.1f}y | MA200 NGÀY: {bd:3d} lần (1/{yrs*12/max(bd,1):4.1f}m), "
          f"confirm-2 phiên {bd2:3d}, confirm-5 phiên {bd5:3d} | "
          f"MA10 THÁNG: {bm:2d} lần (1/{yrs*12/max(bm,1):4.1f}m), confirm-2 {bm2:2d}")
print(f"\n  => chuỗi NGÀY báo nhiều gấp ~{tot_d/max(tot_m,1):.1f} lần chuỗi THÁNG trên cùng tài sản.")
print("     Xác nhận theo PHIÊN không bù được: confirm-2/5 phiên chỉ cắt phần nhỏ.")
print("     Hàm ý thiết kế: hoặc chạy tín hiệu trên trung bình THÁNG (giữ đúng thứ đã backtest),")
print("     hoặc thêm vùng đệm % + xác nhận dài (>=10 phiên) rồi backtest lại khi có chuỗi ngày.")

# how much does a % buffer help on the daily series?
print("\n  Vùng đệm %: số lần báo MA200 ngày khi yêu cầu giá < MA200*(1-buf), confirm-5 phiên")
for buf in (0.0, 0.02, 0.05):
    tot = 0; yrs_all = 0
    for tk, g in s.groupby("ticker"):
        d = g.sort_values("time").set_index("time")["Close"].astype(float)
        if len(d) < 900: continue
        ma = d.rolling(200).mean()
        below = (d < ma * (1 - buf)) & ma.notna()
        tot += breaks_from_below(below, 5).sum()
        yrs_all += (d.index[-1] - d.index[0]).days / 365.25
    print(f"    đệm {buf*100:3.0f}%: {tot:3d} lần / {yrs_all:.0f} mã-năm = 1 lần/{yrs_all*12/max(tot,1):4.1f} tháng-mã")
