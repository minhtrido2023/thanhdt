# -*- coding: utf-8 -*-
"""b_forecast.py — PRELOCK §2 (A). In: ../out/events.parquet. Out: ../out/fc.parquet (dự báo + sai số), ../out/A_*.csv, ../out/A_summary.json"""
import os, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "..", "out")
SEED = 20261125; B = 2000
ev = pd.read_parquet(os.path.join(OUT, "events.parquet"))
ev = ev[ev.iuK & ev.hist8 & (ev.E > 0) & ev.era.isin(["IS", "OOS"])].copy().reset_index(drop=True)
NP = ev[[f"NP_P{k}" for k in range(8)]].values; RV = ev[[f"Revenue_P{k}" for k in range(8)]].values; E = ev.E.values
ttm = NP[:, :4].sum(1); ttm_prev = NP[:, 4:].sum(1)
drift = (NP[:, :4] - NP[:, 4:]).mean(1)
with np.errstate(all="ignore"):
    g = np.clip(RV[:, :4].sum(1) / RV[:, 4:].sum(1) - 1, -0.5, 0.5)
    m = np.clip(ttm / RV[:, :4].sum(1), -0.5, 0.5)
g = np.where(np.isfinite(g), g, np.nan); m = np.where(np.isfinite(m), m, np.nan)
rho = ttm / E; rbar = ev.roe_tc5.values
MODELS = ["SRW", "RW", "TTM4", "SRWD", "MxR", "MR", "ENS", "D0imp"]
rows = []
for h in (1, 2, 3, 4):
    F = {}
    F["SRW"] = NP[:, 4 - h]; F["RW"] = NP[:, 0]; F["TTM4"] = ttm / 4; F["SRWD"] = NP[:, 4 - h] + drift
    F["MxR"] = RV[:, 4 - h] * (1 + g) * m
    F["MR"] = E * (rbar + 0.65 ** (h / 4) * (rho - rbar)) / 4
    F["ENS"] = np.nanmedian(np.vstack([F["SRWD"], F["MxR"], F["MR"]]), axis=0)
    F["ENS"] = np.where(np.isfinite(F["SRWD"]) & np.isfinite(F["MxR"]) & np.isfinite(F["MR"]), F["ENS"], np.nan)   # ENS chỉ khi đủ 3 thành phần
    F["D0imp"] = rbar * E / 4
    A = ev[f"A{h}"].values; base = NP[:, 4 - h]
    d = pd.DataFrame({"ticker": ev.ticker, "qp": ev.qp.astype(str), "yr": ev.yr, "era": ev.era, "route": ev.route.fillna("NA"), "h": h, "A": A, "base": base,
                      "E": E, "MC_rel": ev.MC_rel, "roe_sd5": ev.roe_sd5, "rating": ev.rating})
    for k in MODELS:
        d["F_" + k] = F[k]; d["e_" + k] = (A - F[k]) / E
    rows.append(d)
fc = pd.concat(rows, ignore_index=True)
ecols = ["e_" + k for k in MODELS]
common = fc.A.notna() & np.isfinite(fc[ecols]).all(axis=1)
fc["common"] = common
fc.to_parquet(os.path.join(OUT, "fc.parquet"))
cf = fc[common].copy()
# lớp mô tả
cf["size_t"] = cf.groupby(["h", "qp"]).MC_rel.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["S", "M", "L"]))
cf["vol_t"] = cf.groupby(["h", "qp"]).roe_sd5.transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["lowvol", "midvol", "hivol"]) if s.notna().sum() >= 9 else pd.Series(np.nan, index=s.index))
cf["rat_g"] = np.where(cf.rating <= 3, "r<=3", np.where(cf.rating >= 4, "r>=4", "r_na"))

def per_q(df):
    q = df.groupby("qp")
    out = pd.DataFrame({k: q["e_" + k].apply(lambda x: np.median(np.abs(x))) for k in MODELS}); out["yr"] = q.yr.first(); out["n"] = q.size()
    return out
def boot_logratio(pq, k, ref="SRW", seed=SEED):
    lr = np.log(pq[k] / pq[ref]); ys = pq.yr.unique(); rng = np.random.RandomState(seed); by = {y: lr[pq.yr == y].values for y in ys}
    res = np.array([np.concatenate([by[y] for y in rng.choice(ys, len(ys))]).mean() for _ in range(B)])
    return float(np.exp(lr.mean())), float(np.exp(np.percentile(res, 0.35))), float(np.exp(np.percentile(res, 99.65))), float(np.exp(np.percentile(res, 2.5))), float(np.exp(np.percentile(res, 97.5)))
summ = []
for h in (1, 2, 3, 4):
    for era in ("IS", "OOS"):
        sub = cf[(cf.h == h) & (cf.era == era)]
        pq = per_q(sub)
        for k in MODELS:
            e = sub["e_" + k]; lo, hi = e.quantile([0.01, 0.99])
            nz = sub.A.abs() >= 0.0025 * sub.E
            dirm = (np.sign(sub["F_" + k] - sub.base) != 0) & (np.sign(sub.A - sub.base) != 0)
            hit = float((np.sign(sub["F_" + k] - sub.base) == np.sign(sub.A - sub.base))[dirm].mean()) if k != "SRW" and dirm.sum() else np.nan
            R, lo99, hi99, lo95, hi95 = boot_logratio(pq, k) if k != "SRW" else (1.0, np.nan, np.nan, np.nan, np.nan)
            summ.append({"h": h, "era": era, "model": k, "n_events": int(len(sub)), "n_q": int(len(pq)), "n_yr": int(pq.yr.nunique()),
                         "MdAE_pooled": float(e.abs().median()), "MdAE_q_mean": float(pq[k].mean()), "R_vs_SRW": R, "R_ci99_lo": lo99, "R_ci99_hi": hi99, "R_ci95_lo": lo95, "R_ci95_hi": hi95,
                         "meanAE_w": float(e.clip(lo, hi).abs().mean()), "MdAPE": float((e[nz].abs() * sub.E[nz] / sub.A[nz].abs()).median()),
                         "bias_med": float(e.median()), "bias_mean_w": float(e.clip(lo, hi).mean()), "dir_hit": hit, "dir_n": int(dirm.sum())})
S = pd.DataFrame(summ); S.to_csv(os.path.join(OUT, "A_summary.csv"), index=False)
# cắt lớp h=1 (mô tả)
seg = []
for col in ("route", "size_t", "vol_t", "rat_g"):
    for (era, gv), sub in cf[cf.h == 1].groupby(["era", col], observed=True):
        if len(sub) < 100:
            continue
        r = {"era": era, "cut": col, "grp": str(gv), "n": int(len(sub))}
        for k in MODELS:
            r["MdAE_" + k] = float(sub["e_" + k].abs().median())
        for k in ("ENS", "D0imp", "SRWD"):
            r["R_" + k] = r["MdAE_" + k] / r["MdAE_SRW"]; r["bias_" + k] = float(sub["e_" + k].median())
        seg.append(r)
pd.DataFrame(seg).to_csv(os.path.join(OUT, "A_segments.csv"), index=False)
# theo năm h=1
yr = cf[cf.h == 1].groupby("yr").apply(lambda s: pd.Series({**{"MdAE_" + k: s["e_" + k].abs().median() for k in MODELS}, "n": len(s)}))
yr.to_csv(os.path.join(OUT, "A_by_year.csv"))
json.dump({"n_common_by_h_era": {f"{a}_{b}": int(v) for (a, b), v in cf.groupby(["h", "era"]).size().items()},
           "dropped_noncommon_h1": int(((fc.h == 1) & ~fc.common).sum())}, open(os.path.join(OUT, "A_meta.json"), "w"), indent=1)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(S[["h", "era", "model", "n_events", "n_q", "MdAE_pooled", "R_vs_SRW", "R_ci99_lo", "R_ci99_hi", "MdAPE", "bias_med", "dir_hit"]].round(4).to_string(index=False))
