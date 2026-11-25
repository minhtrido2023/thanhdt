# -*- coding: utf-8 -*-
"""g_selfcheck3.py — tự kiểm ĐỘC LẬP (đường code khác với c/d/e). Thoát mã 1 nếu có mục FAIL.
[V3: thêm 8 = giá T+1 holdings tính lại từ px_t1 bằng đường khác; 9 = null E/P cảnh báo bằng vòng lặp pandas; hedonic dùng trung vị tháng PIT] 1 NAV tính lại từ CSV danh mục (lệch VND) · 2 V/B D0 bằng vòng lặp thuần · 3 PIT known ≤ time · 4 hệ số hedonic 1 tháng tính lại từ dòng thô
· 5 IC36 ENS1w bằng scipy · 6 U-hit ENS1w bằng vòng lặp pandas · 7 cảnh báo đắt D0 (đúng-tương đối) bằng vòng lặp pandas."""
import os, sys, json, math
import numpy as np, pandas as pd
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "out"); fails = []
def chk(name, ok, detail):
    print(("PASS" if ok else "FAIL"), name, detail); (None if ok else fails.append(name))
# 1. NAV
for nm in ("S1_ENS1w_f1", "S1_ENS2_f1", "S1_D0_f1", "S3f_f1", "S3f_ENS2_f1", "S7_D0_f1", "S7_EPN_E2_f1"):
    h = pd.read_csv(os.path.join(OUT, f"bt2_holdings_{nm}.csv")); m = pd.read_csv(os.path.join(OUT, f"bt2_monthly_{nm}.csv"))
    nav = 50e9; prev = {}
    for ym in m.ym:
        g = h[h.ym == ym]; w = dict(zip(g.ticker, g.w)); gross = float(sum(a * b for a, b in zip(g.w, g.ret)))
        to = sum(abs(w.get(t, 0.0) - prev.get(t, 0.0)) for t in set(w) | set(prev)); nav *= 1 + gross - 0.001 * to
        prev = {t: a * (1 + b) / (1 + gross) for t, a, b in zip(g.ticker, g.w, g.ret)}
    d = abs(nav - m.nav.iloc[-1]); chk(f"NAV {nm}", d < 1.0, f"lệch {d:.6f} VND trên {m.nav.iloc[-1]:,.0f}")
vp = pd.read_parquet(os.path.join(OUT, "vp2.parquet"))
# 2. D0 thuần
rng = np.random.RandomState(7); s = vp[vp.lv_D0.notna() & (vp.E > 0)].sample(200, random_state=7); mx = 0.0
for r in s.itertuples():
    tc = min(max(r.roe_tc5, -0.1), 0.4); ret = min(max(1 - (0.3 if r.payout != r.payout else r.payout), 0.1), 1.0); R = 0.1225; gT = 0.055
    lr = R + 0.4 * (tc - R); B = 1.0; pv = 0.0
    for t in range(1, 11):
        roe_t = tc + (lr - tc) * t / 10.0; g = min(max(roe_t * ret, 0), 0.15); g = gT + (g - gT) * (10 - t) / 9.0; g = min(g, max(roe_t, 0.0))
        pv += (roe_t - R) * B / (1 + R) ** t; B *= 1 + g
    vb = max(1 + pv + (lr - R) * B / (R - min(gT, max(lr, 0.0))) / (1 + R) ** 10, 0.2)
    mx = max(mx, abs(math.log(vb * r.E / r.mc) - r.lv_D0))
chk("D0 V/B vòng lặp thuần (200 dòng)", mx < 1e-9, f"lệch tối đa {mx:.2e}")
# 3. PIT
chk("PIT known ≤ time", bool((vp.known <= vp.time).all()), f"{len(vp)} dòng; tuổi BCTC tối đa {(vp.time - vp.known).dt.days.max()} ngày")
# 4. hedonic 1 tháng
fit = json.load(open(os.path.join(OUT, "models_fit.json"))); cols = fit["hed_cols"]; M = 2020 * 12 + 1
vp["lpb"] = np.log(vp.mc / vp.E.where(vp.E > 0))
X = pd.DataFrame({"c": 1.0, "tc": vp.roe_tc5.clip(-0.1, 0.4), "roe": vp.roe.clip(-0.3, 0.5), "loss": (vp.np_ttm < 0).astype(float), "revg": vp.revg.fillna(0), "po": vp.payout.fillna(0.3).clip(0, 1),
                  "lev": (vp.debt.fillna(0) / vp.E.where(vp.E > 0)).clip(0, 3), "sd": vp.roe_sd5.fillna(vp.groupby("mi").roe_sd5.transform("median")), "le": np.log(vp.E.where(vp.E > 0))})
for c in cols:
    if c.startswith("r_"):
        X[c] = (vp.route == c[2:]).astype(float)
X = X[cols]; ok = np.isfinite(X.values).all(1) & np.isfinite(vp.lpb.values) & vp.in_universe.values & (vp.mi.values >= M - 60) & (vp.mi.values <= M - 1)
yy = vp.lpb[ok].groupby(vp.mi[ok]).transform(lambda s: s.clip(np.nanpercentile(s, 1), np.nanpercentile(s, 99)))
b = np.linalg.lstsq(X[ok].values, yy.values, rcond=None)[0]; ref = np.array([fit["hed_beta_frozen_2019-12"][c] for c in cols])
chk("hệ số hedonic đóng băng 2019-12 (tính lại từ dòng thô 2015-01..2019-12)", float(np.abs(b - ref).max()) < 2e-3, f"lệch hệ số tối đa {np.abs(b - ref).max():.2e}; tháng dùng {int(vp.mi[ok].min())}..{int(vp.mi[ok].max())} < {M}")
# 5–7 so với metrics2.csv
met = pd.read_csv(os.path.join(OUT, "metrics2.csv")); met = met[met.scope == "ALL"].set_index(["model", "era"])
u = vp[vp.in_universe].copy(); u["mth"] = pd.PeriodIndex(u.ym, freq="M").month
for era, a, b_ in (("IS", "2014-01", "2019-12"), ("OOS", "2020-01", "2023-10")):
    q = u[(u.ym >= a) & (u.ym <= b_) & u.mth.isin([3, 6, 9, 12])][["ym", "lv_ENS1w", "ex36"]].dropna()
    ic = np.mean([spearmanr(g.lv_ENS1w, g.ex36)[0] for _, g in q.groupby("ym") if len(g) >= 30]); ref = met.loc[("ENS1w", era), "ic36"]
    chk(f"IC36 ENS1w {era} (scipy)", abs(ic - ref) < 1e-9, f"{ic:.6f} vs {ref:.6f}")
piv = vp.pivot(index="mi", columns="ticker", values="lv_ENS1w"); pvP = vp.pivot(index="mi", columns="ticker", values="Close"); pvU = vp.pivot(index="mi", columns="ticker", values="in_universe").fillna(False).astype(bool)
pvD = vp.pivot(index="mi", columns="ticker", values="lv_D0"); pvX = vp.pivot(index="mi", columns="ticker", values="ex36")
full = range(int(vp.mi.min()), int(vp.mi.max()) + 1); piv, pvP, pvU, pvD, pvX = [x.reindex(full) for x in (piv, pvP, pvU, pvD, pvX)]; pvU = pvU.fillna(False).astype(bool)
def mi(ym): return int(ym[:4]) * 12 + int(ym[5:])
for era, a, b_ in (("IS", "2014-01", "2019-12"), ("OOS", "2020-01", "2023-10")):
    n = hit = 0; no = right = 0
    for tk in piv.columns:
        lv = piv[tk]; P = pvP[tk]; U = pvU[tk]; last = -99
        for t in range(mi(a), mi(b_) + 1):
            if U.get(t, False) and lv.get(t, np.nan) >= math.log(1.25) and t - last >= 36 and not (lv.loc[t - 6:t - 1] >= math.log(1.25)).any():
                n += 1; last = t; w = lv.loc[t + 1:t + 36]; hit += int(((w <= 0) & (P.loc[t + 1:t + 36] > P[t])).any())
        d = pvD[tk]; last = -99; run = 0
        for t in range(mi(a) - 6, mi(b_) + 1):
            run = run + 1 if d.get(t, np.nan) <= math.log(0.67) else 0
            if t >= mi(a) and U.get(t, False) and run >= 6 and t - last >= 36:
                last = t; e = pvX[tk].get(t, np.nan)
                if e == e:
                    no += 1; right += int(e < 0)
    r1 = met.loc[("ENS1w", era)]; r2 = met.loc[("D0", era)]
    chk(f"U-hit ENS1w {era} (vòng lặp pandas)", n == int(r1.U_n) and abs(hit / n - r1.U_hit) < 1e-12, f"{n} sự kiện, {hit / n:.4f} vs {int(r1.U_n)}, {r1.U_hit:.4f}")
    chk(f"cảnh báo đắt D0 {era} đúng-tương đối (vòng lặp pandas)", abs(right / no - r2.O_right_rel) < 1e-12, f"{right}/{no} = {right / no:.4f} vs {r2.O_right_rel:.4f}")

# 8. [V3 NB-2] giá T+1 của holdings: tính lại từ px_t1 (thô) bằng vòng lặp thuần, KHÔNG dùng _px_at/searchsorted của e_bt2
t1 = pd.read_parquet(os.path.join(OUT, "px_t1.parquet")); lg = pd.read_parquet(os.path.join(OUT, "px_last.parquet")).set_index("ticker")
tk = {t: dict(zip(g.ym, g.c1)) for t, g in t1.groupby("ticker")}
def mm(ym, k): p = pd.Period(ym, freq="M") + k; return str(p)
def first_at_or_after(t, ym):
    d = tk[t]; yms = sorted(y for y in d if y >= ym)
    return d[yms[0]] if yms else np.nan
h = pd.read_csv(os.path.join(OUT, "bt2_holdings_EW_f1.csv")); h = pd.concat([h.sample(400, random_state=11), h[h.ret <= -0.45].head(300)]).drop_duplicates(); mxd = 0.0; nfall = 0; cl = vp.set_index(["ticker", "ym"]).Close
for r in h.itertuples():
    m1, m2 = mm(r.ym, 1), mm(r.ym, 2); last = lg.last_ym[r.ticker]
    a = first_at_or_after(r.ticker, m1) if last >= m1 else np.nan
    if not np.isfinite(a): a = cl.get((r.ticker, r.ym), np.nan)
    if last < m2: ret = lg.last_close[r.ticker] * 0.5 / a - 1; nfall += 1
    else: ret = first_at_or_after(r.ticker, m2) / a - 1
    mxd = max(mxd, abs(ret - r.ret))
chk("giá T+1 holdings EW_f1 (400 dòng ngẫu nhiên + ≤300 dòng ret ≤ −45%, tính lại từ px_t1 thô)", mxd < 1e-9, f"lệch tối đa {mxd:.2e}; {nfall} dòng thuộc nhánh ngừng giao dịch")
# 9. [V3 B-1] cảnh báo đắt của null E/P (lv_EPN_E2 khớp cờ ENS2) và ENS2 — vòng lặp pandas, đối chiếu metrics2.csv / null_ep.csv
ne = pd.read_csv(os.path.join(OUT, "null_ep.csv")).set_index(["model", "era"])
pvE = vp.pivot(index="mi", columns="ticker", values="lv_EPN_E2").reindex(full); pvS = vp.pivot(index="mi", columns="ticker", values="lv_ENS2").reindex(full)
for era, a, b_ in (("IS", "2014-01", "2019-12"), ("OOS", "2020-01", "2023-10")):
    for nm, pv, ref in (("EPN_E2", pvE, ne.loc[("EPN_E2", era), "right_rel"]), ("ENS2", pvS, met.loc[("ENS2", era), "O_right_rel"])):
        no = right = 0
        for tk_ in pv.columns:
            d = pv[tk_]; U = pvU[tk_]; last = -99; run = 0
            for t in range(mi(a) - 6, mi(b_) + 1):
                run = run + 1 if d.get(t, np.nan) <= math.log(0.67) else 0
                if t >= mi(a) and U.get(t, False) and run >= 6 and t - last >= 36:
                    last = t; e = pvX[tk_].get(t, np.nan)
                    if e == e: no += 1; right += int(e < 0)
        chk(f"cảnh báo đắt {nm} {era} đúng-tương đối (vòng lặp pandas)", abs(right / no - ref) < 1e-12, f"{right}/{no} = {right / no:.4f} vs {ref:.4f}")
print("TỔNG:", "PASS" if not fails else f"FAIL {fails}"); sys.exit(1 if fails else 0)

