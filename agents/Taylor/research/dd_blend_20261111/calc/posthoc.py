# -*- coding: utf-8 -*-
"""posthoc.py — HẬU KIỂM (NGOÀI PRELOCK, viết SAU khi thấy K3n): K3n là TỈ SỐ nên phạt V có khoảng cách
ban đầu nhỏ. Đo thêm, cùng mẫu chính:
  AE_N   = median |log(MC0·TR_N / (V·(1+r)^{N/12}))|      (sai số tuyệt đối, trung lập drift r)
  AEdm_N = như trên nhưng drift = trung vị log TR_N của CÙNG quý as-of (bỏ drift chung thị trường)
  naive  = V := MC0 (giá luôn đúng) — mốc so sánh
  β_N, tương quan hạng Spearman log(V/MC0) ~ log TR_N; chạm khi V<MC0.
Chọn w trên IS theo (i) min AEdm_36, (ii) max β_36; chấm OOS, CI cụm mã cho Δ so với w=0.
Thêm: cờ phân kỳ D=|log(Vs/Vl)| — β/chạm ở dòng có cờ vs không cờ, CI Δ.
Trials thêm: 11 w × 4 N × 2 tiêu chí = 88 (N tổng = 306 + 88 = 394).
"""
import os, sys, json
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

p = load()
r3 = (p.rating <= 3).values; fin_ok = np.isfinite(p.MC0.values)
MAIN = r3 & fin_ok & (p.V_s > 0).values & (p.V_l3 > 0).values
IS = MAIN & (p.yr <= 2019).values; OOS = MAIN & (p.yr >= 2020).values
VL = p.V_l3.values
qv = p.q.values


def parts(V, m, N):
    k = m & p[f"full{N}"].values & np.isfinite(V) & (V > 0)
    idx = np.where(k)[0]
    x = np.log(V[idx] / p.MC0.values[idx]); y = np.log(p[f"TR{N}"].values[idx])
    drift_r = N / 12 * np.log(1 + p.r.values[idx])
    cm = pd.Series(y).groupby(qv[idx]).transform("median").values
    return idx, x, y, drift_r, cm


def stat(x, y, dr, cm):
    return {"AE": float(np.median(np.abs(y - dr - x))), "AEdm": float(np.median(np.abs(y - cm - x))),
            "AE_naive": float(np.median(np.abs(y - dr))), "AEdm_naive": float(np.median(np.abs(y - cm))),
            "beta": float(np.polyfit(x, y, 1)[0]),
            "spearman": float(pd.Series(x).rank().corr(pd.Series(y).rank()))}


rows = []
for N in HZ:
    for w in WGRID:
        V = blend(p, w, VL)
        for lab, m in (("IS", IS), ("OOS", OOS)):
            idx, x, y, dr, cm = parts(V, m, N)
            o = stat(x, y, dr, cm); o.update({"N": N, "w": float(w), "split": lab, "n": len(idx),
                                              "touch_VltP": float(((p.MC0.values[idx] * p[f"minTR{N}"].values[idx]) <= V[idx])[x < 0].mean())})
            rows.append(o)
R = pd.DataFrame(rows)
R.round(4).to_csv(os.path.join(OUT, "posthoc_grid.csv"), index=False)


def boot_pair(N, w1, w0, m, B=1000):
    V1, V0 = blend(p, w1, VL), blend(p, w0, VL)
    i1, x1, y, dr, cm = parts(V1, m, N); i0, x0, _, _, _ = parts(V0, m, N)
    assert (i1 == i0).all()
    groups = list(pd.Series(np.arange(len(i1))).groupby(p.ticker.values[i1]).indices.values())
    rng = np.random.default_rng(SEED); out = []
    for _ in range(B):
        s = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
        a = stat(x1[s], y[s], dr[s], cm[s]); b = stat(x0[s], y[s], dr[s], cm[s])
        out.append([a["AEdm"] - b["AEdm"], a["beta"] - b["beta"], a["AE"] - b["AE"], a["AEdm"] - a["AEdm_naive"], a["beta"]])
    out = np.array(out)
    return {"dAEdm_ci": ci(out[:, 0]), "dbeta_ci": ci(out[:, 1]), "dAE_ci": ci(out[:, 2]),
            "AEdm_minus_naive_ci": ci(out[:, 3]), "beta_ci": ci(out[:, 4]), "n": len(i1), "n_tickers": len(groups)}


S = {"selection": {}}
for N in HZ:
    isr = R[(R.N == N) & (R.split == "IS")]
    w_ae = float(isr.sort_values(["AEdm", "w"]).iloc[0].w)
    w_b = float(isr.sort_values(["beta", "w"], ascending=[False, True]).iloc[0].w)
    S["selection"][N] = {"w_minAEdm_IS": w_ae, "w_maxBeta_IS": w_b,
                         "OOS_w_ae_vs_0": boot_pair(N, w_ae, 0.0, OOS), "OOS_w_b_vs_0": boot_pair(N, w_b, 0.0, OOS),
                         "OOS_w05_vs_0": boot_pair(N, 0.5, 0.0, OOS)}
    print(N, "w_ae", w_ae, "w_b", w_b, flush=True)

# cờ phân kỳ: dòng có cờ vs không (w=0.5), β và chạm, OOS + ALL, CI Δβ cụm mã
D = np.abs(np.log(p.V_s.values / VL))
S["flag"] = {}
for tau_lab, tau in (("log2", np.log(2)), ("log3", np.log(3))):
    for N in (12, 36):
        V = blend(p, 0.5, VL)
        res = {}
        for lab, m in (("OOS", OOS), ("ALL", MAIN)):
            o = {}
            for fl, mm in (("flagged", m & (D > tau)), ("not", m & (D <= tau))):
                idx, x, y, dr, cm = parts(V, mm, N)
                o[fl] = stat(x, y, dr, cm); o[fl]["n"] = len(idx)
                o[fl]["touch_VltP"] = float(((p.MC0.values[idx] * p[f"minTR{N}"].values[idx]) <= V[idx])[x < 0].mean())
            # bootstrap Δβ (không cờ − có cờ), cụm mã
            idx, x, y, dr, cm = parts(V, m, N); f = D[idx] > tau
            groups = list(pd.Series(np.arange(len(idx))).groupby(p.ticker.values[idx]).indices.values())
            rng = np.random.default_rng(SEED); out = []
            for _ in range(1000):
                s = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
                a, b = s[~f[s]], s[f[s]]
                out.append(np.polyfit(x[a], y[a], 1)[0] - np.polyfit(x[b], y[b], 1)[0])
            o["dbeta_not_minus_flag_ci"] = ci(np.array(out)); o["flag_rate"] = float(f.mean())
            res[lab] = o
        S["flag"][f"{tau_lab}_N{N}"] = res
json.dump(S, open(os.path.join(OUT, "posthoc.json"), "w"), indent=1, default=float)
pd.set_option("display.width", 250)
for N in HZ:
    print(R[R.N == N].pivot_table(index="w", columns="split", values=["AE", "AEdm", "beta", "spearman"]).round(3))
    print("naive", R[(R.N == N)].groupby("split")[["AE_naive", "AEdm_naive"]].first().round(3).to_dict())
print(json.dumps(S, indent=0, default=float)[:5000])
