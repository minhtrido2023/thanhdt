"""NGOÀI PREREG (post-hoc chẩn đoán): Q4 hiệu chỉnh phơi nhiễm. Sổ BAL nắm phần lớn tiền ⇒ BAL−VNI âm cơ học
ngày VNI tăng mạnh. ex_adj = r_BAL − w(t−1)·r_VNI, w = (bal_stocks_ref + bal_etf_ref)/nav_bal_ref (ETF park ~ rổ VN30-proxy, giả định β≈1)."""
import json, math, os, numpy as np, pandas as pd
import backtest_compare as B   # tái dùng D, rb, rv, episodes(); chạy lại (in JSON) — read-only
HERE = os.path.dirname(os.path.abspath(__file__))
D, rb, rv = B.D, B.rb, B.rv
w = ((D.bal_stocks_ref + D.bal_etf_ref) / D.nav_bal_ref).shift(1)
ws = (D.bal_stocks_ref / D.nav_bal_ref).shift(1)
exa = rb - w * rv
def f5(s, t): return float(np.nansum(s.iloc[t:t+5].values)) if t + 5 <= len(s) else np.nan
U = pd.DataFrame({"a1": exa, "a5": [f5(exa, t) for t in range(len(exa))], "w": w}).iloc[61:-5].dropna()
rng = np.random.default_rng(20261022); res = {}
for name, (a, b) in {"main_-8_+2.0": (0.08, 0.02), "sens_-10_+2.5": (0.10, 0.025)}.items():
    ts = [t for t in B.episodes(a, b) if not np.isnan(exa.iloc[t])]
    E = pd.DataFrame([dict(date=str(D.index[t].date()), w=w.iloc[t], w_stock=ws.iloc[t], exadj_1d=exa.iloc[t], exadj_5d=f5(exa, t)) for t in ts])
    E.to_csv(f"{HERE}/q4adj_episodes_{name}.csv", index=False)
    N = len(E); m1, m5 = U.a1.median(), U.a5.median()
    k1 = int((E.exadj_1d < m1).sum()); k5 = int((E.exadj_5d < m5).sum())
    binom = lambda k, n: sum(math.comb(n, j) for j in range(k, n + 1)) / 2 ** n
    s1 = np.array([np.median(rng.choice(U.a1.values, N, replace=False)) for _ in range(10000)])
    s5 = np.array([np.median(rng.choice(U.a5.values, N, replace=False)) for _ in range(10000)])
    res[name] = dict(N=N, ep_median_w=float(E.w.median()), uncond_median_w=float(U.w.median()),
                     ep_median_exadj1=float(E.exadj_1d.median()), uncond_median_exadj1=float(m1),
                     ep_median_exadj5=float(E.exadj_5d.median()), uncond_median_exadj5=float(m5),
                     k_below1=k1, k_below5=k5, binom1=binom(k1, N), binom5=binom(k5, N),
                     resample_pct1=float((s1 <= E.exadj_1d.median()).mean()), resample_pct5=float((s5 <= E.exadj_5d.median()).mean()),
                     ep_w_ge_0_5=int((E.w >= 0.5).sum()), ep_median_exadj5_w_ge_0_5=float(E[E.w >= 0.5].exadj_5d.median()) if (E.w >= 0.5).any() else None)
json.dump(res, open(f"{HERE}/q4_exposure_adj.json", "w"), indent=1)
print("=====ADJ"); print(json.dumps(res, indent=1))
for n in res: print(n); print(pd.read_csv(f"{HERE}/q4adj_episodes_{n}.csv").round(4).to_string())
