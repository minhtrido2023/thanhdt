# -*- coding: utf-8 -*-
"""g_selfcheck.py — tự kiểm độc lập (đường code khác e_backtest): (1) tính lại NAV S1 từ holdings CSV, lệch 0 VND;
(2) PIT: mọi dòng panel có fin_time<=known<=time; (3) tính lại V/B mô hình D0 bằng vòng lặp thuần Python trên 200 dòng
ngẫu nhiên; (4) tính lại cắt-36T bằng brute-force trên 300 dòng ngẫu nhiên. Không phụ thuộc TZ (không gọi now())."""
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
vp = pd.read_parquet(os.path.join(OUT, "vp.parquet")).sort_values(["ticker", "ym"]).reset_index(drop=True)
fails = 0
# (1)
for v in ("D0_fix", "G1D0_fix", "B_slow"):
    h = pd.read_csv(os.path.join(OUT, f"holdings_S1_{v}.csv")); m = pd.read_csv(os.path.join(OUT, f"bt_monthly_S1_{v}.csv"))
    px = {(t, y): c for t, y, c in zip(vp.ticker, vp.ym, vp.t1_close) if c == c}
    nav = 1e9; wprev = {}
    for ym in m.ym:
        nxt = str(pd.Period(ym, freq="M") + 1)
        ts = [t for t in h[h.ym == ym].ticker if (t, ym) in px]
        w = {t: 1.0 / len(ts) for t in ts}
        turn = sum(abs(w.get(t, 0) - wprev.get(t, 0)) for t in set(w) | set(wprev))
        rets = {t: (px[(t, nxt)] / px[(t, ym)] - 1 if (t, nxt) in px else 0.0) for t in ts}
        port = sum(w[t] * rets[t] for t in ts)
        nav *= (1 - 0.001 * turn) * (1 + port)
        tot = sum(w[t] * (1 + rets[t]) for t in ts) or 1.0
        wprev = {t: w[t] * (1 + rets[t]) / tot for t in ts}
    main = 1e9 * float(np.prod(1 + m.ret.values)); d = abs(nav - main)
    print(f"[1] S1_{v}: NAV chính {main:,.0f} | tính lại {nav:,.0f} | lệch {d:.6f} VND", "PASS" if d < 1 else "FAIL"); fails += d >= 1
# (2)
ok = bool(((vp.fin_time <= vp.known) & (vp.known <= vp.time)).all()); print("[2] PIT fin_time<=known<=time:", "PASS" if ok else "FAIL", len(vp)); fails += (not ok)
# (3)
rng = np.random.default_rng(1); s = vp[vp.vb_D0_fix.notna()].sample(200, random_state=1); mx = 0.0
for _, r_ in s.iterrows():
    r = 0.1225; gT = min(0.055, r - 0.04); rn = min(max(r_.roe_tc5, -0.1), 0.4); ret = min(max(1 - (0.3 if r_.payout != r_.payout else r_.payout), 0.1), 1.0)
    lr = r + 0.4 * (rn - r); B = 1.0; pv = 0.0
    for t in range(1, 11):
        roe_t = rn + (lr - rn) * t / 10.0; g = gT + (min(max(roe_t * ret, 0), 0.15) - gT) * (10 - t) / 9.0; g = min(g, max(roe_t, 0.0))
        pv += (roe_t - r) * B / (1 + r) ** t; B *= 1 + g
    vb = max(1 + pv + (lr - r) * B / (r - min(gT, max(lr, 0))) / (1 + r) ** 10, 0.2); mx = max(mx, abs(vb - r_.vb_D0_fix))
print(f"[3] V/B D0 tính lại 200 dòng: lệch tối đa {mx:.2e}", "PASS" if mx < 1e-9 else "FAIL"); fails += mx >= 1e-9
# (4)
u = vp[vp.in_universe & (vp.ym >= "2014-01") & (vp.ym <= "2019-12") & vp.fwd36.notna() & vp.lv_D0_fix.notna()]
smp = u.sample(300, random_state=2); byt = {t: g.set_index("ym").lv_D0_fix for t, g in vp[vp.ticker.isin(smp.ticker)].groupby("ticker")}
cr = []
for _, r_ in smp.iterrows():
    sr = byt[r_.ticker]; p0 = pd.Period(r_.ym, freq="M"); s0 = np.sign(r_.lv_D0_fix)
    cr.append(any((str(p0 + k) in sr.index) and sr[str(p0 + k)] == sr[str(p0 + k)] and np.sign(sr[str(p0 + k)]) == -s0 for k in range(1, 37)))
print(f"[4] cắt-36T IS brute-force 300 dòng: {np.mean(cr):.3f} (toàn mẫu metrics.csv: {pd.read_csv(os.path.join(OUT,'metrics.csv')).set_index('variant').loc['D0_fix','IS_cross36']:.3f})")
print("SELFCHECK", "PASS" if fails == 0 else f"FAIL({fails})"); sys.exit(1 if fails else 0)
