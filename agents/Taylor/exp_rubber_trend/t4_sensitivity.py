#!/usr/bin/env python3
"""T4 — is the MA10 result a plateau or a knife-edge? Plus IS/OOS split and the
recall/precision surface over the whole (window x confirm) grid. The headline claim
of T3(a) is recall+precision on real down-cycles, so THAT is what gets the grid."""
import numpy as np, pandas as pd

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


def events(win, k):
    ma = p.rolling(win).mean()
    below = p < ma
    if k <= 1:
        sig = below & ~below.shift(1, fill_value=False) & ma.notna()
    else:
        run = below.copy()
        for j in range(1, k):
            run &= below.shift(j, fill_value=False)
        run &= ma.notna()
        sig = run & ~run.shift(1, fill_value=False)
    return [i for i, s in enumerate(sig.values) if s]


def score(ev, cycles, lo=0, hi=10**6):
    ev = [e for e in ev if lo <= e <= hi]
    cyc = [(j, k) for j, k, _ in cycles if lo <= j <= hi]
    if not cyc:
        return None
    hits = sum(any(j <= e <= k for e in ev) for j, k in cyc)
    in_c = set()
    for j, k in cyc: in_c.update(range(j, k + 1))
    tp = sum(e in in_c for e in ev)
    return hits, len(cyc), tp, len(ev)


piv = zigzag(px, 0.25)
cycles = [(i1, i2, px[i2] / px[i1] - 1) for (k1, i1), (k2, i2) in zip(piv, piv[1:])
          if k1 == "P" and k2 == "T"]

print("=" * 88)
print("SENSITIVITY GRID — recall (chu kỳ giảm >=25% bắt được) / precision (báo trong chu kỳ)")
print("Toàn mẫu 2006-04..2026-07, N chu kỳ =", len(cycles))
print("=" * 88)
print(f"{'window':>8} | " + " | ".join(f"confirm {k}m".center(26) for k in (1, 2, 3)))
for win in (6, 8, 9, 10, 11, 12, 15):
    cells = []
    for k in (1, 2, 3):
        r = score(events(win, k), cycles)
        hits, nc, tp, ne = r
        yrs = (p.index[-1] - p.index[0]).days / 365.25
        cells.append(f"R {hits}/{nc}  P {tp}/{ne}={100*tp/ne if ne else 0:3.0f}%  1/{yrs*12/ne if ne else 0:4.1f}m")
    star = " <-- MA200 daily eq" if win == 10 else (" <-- MA100 daily eq" if win == 5 else "")
    print(f"MA{win:>6} | " + " | ".join(c.center(26) for c in cells) + star)
r = score(events(5, 1), cycles); print(f"MA{5:>6} | " + " | ".join(
    (lambda rr: f"R {rr[0]}/{rr[1]}  P {rr[2]}/{rr[3]}={100*rr[2]/rr[3]:3.0f}%  1/{(p.index[-1]-p.index[0]).days/365.25*12/rr[3]:4.1f}m")(
        score(events(5, k), cycles)).center(26) for k in (1, 2, 3)) + " <-- MA100 daily eq")

print("\n" + "=" * 88)
print("IS / OOS SPLIT (IS = 2006-04..2016-12, OOS = 2017-01..2026-07)")
print("=" * 88)
cut = int(np.argmax(p.index >= pd.Timestamp("2017-01-01")))
for lbl, lo, hi in (("IS ", 0, cut - 1), ("OOS", cut, len(px) - 1)):
    for win, k in ((10, 1), (10, 2), (5, 2)):
        r = score(events(win, k), cycles, lo, hi)
        if r is None:
            print(f"  {lbl} MA{win} c{k}m: no cycle in window"); continue
        hits, nc, tp, ne = r
        print(f"  {lbl} MA{win:2d} confirm-{k}m: recall {hits}/{nc}  precision {tp}/{ne}"
              f"={100*tp/ne if ne else 0:3.0f}%")

print("\n" + "=" * 88)
print("ĐỘ TRỄ so với đỉnh chu kỳ (tháng) — cái giá của xác nhận")
print("=" * 88)
for win, k in ((10, 1), (10, 2), (10, 3), (5, 2)):
    ev = events(win, k)
    lags, gone = [], []
    for j, kk, _ in cycles:
        a = [e for e in ev if j <= e <= kk]
        if a:
            lags.append(a[0] - j); gone.append((px[a[0]] / px[j] - 1) * 100)
    print(f"  MA{win} confirm-{k}m: trễ trung vị {np.median(lags):.0f}m (khoảng {min(lags)}-{max(lags)}m) | "
          f"đã mất trung vị {np.median(gone):+.0f}% khi báo (khoảng {min(gone):+.0f}..{max(gone):+.0f}%)")

print("\n" + "=" * 88)
print("N TRIALS đã so sánh trong nghiên cứu này (kỷ luật multiple-testing)")
print("=" * 88)
print("  T2: 3 định nghĩa đường (MA10/MA5/OLS-5m) x 2 confirm x 3 horizon = 18 ô so sánh")
print("  T3: 2 biến thể x 3 horizon trên giá  + 2 x 3 trên rổ cổ phiếu = 12")
print("  T3b: 3 ngưỡng sụt x 3 nhánh = 9   |   T4 grid: 8 window x 3 confirm = 24")
print("  => N_trials ~ 63. Với 63 phép so sánh, 1-2 CI95 vừa đủ loại 0 KHÔNG phải bằng chứng.")
print("     Kết luận chỉ được dựa vào (i) recall/precision chu kỳ — cấu trúc đặt trước, không dò,")
print("     và (ii) plateau của grid trên, KHÔNG dựa vào ô có p-value đẹp nhất.")
