# -*- coding: utf-8 -*-
"""analyze.py — chấm 9 ứng viên nền theo PRELOCK.md (T1–T6) + đòn tấn công + mô tả N24/36.
Run: $DNA_PYEXE -W ignore analyze.py -> ../out/summary.json (+ cands_table.csv)
"""
import os, sys, json, itertools
import multiprocessing as mp
import numpy as np, pandas as pd
from scipy.stats import norm
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "out")
R = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(R, "dd_fcfe3y_decay_20261111", "calc"))
import bases as Bm
import lib as L
B = int(os.environ.get("IC_B", 1000)); BR = int(os.environ.get("IC_BR", 200)); SEED = 20261112
HP = (3, 6, 12); HS = (24, 36)

p, E1, E2, V, M0, AUX = Bm.build()
QC = pd.factorize(p.q.values, sort=True)[0]
QLAB = np.array(sorted(pd.unique(p.q.values)))
ctx = L.Ctx(QC, QLAB, p.ticker.values, SEED, B)
QY = ctx.Q_YR
MC0 = p.MC0.values
yN = {}
for N in (3, 6):
    yN[N] = np.where(E2[f"full{N}"].values, np.log(E2[f"TR{N}"].values), np.nan)
for N in (12, 24, 36):
    yN[N] = np.where(p[f"full{N}"].values, np.log(p[f"TR{N}"].values), np.nan)
lg = lambda v: np.where(np.isfinite(v) & (v > 0), np.log(v / MC0), np.nan)
X = {k: lg(v) for k, v in V.items()}
Q_IS = QY <= 2019; Q_OOS = QY >= 2020; ALL = np.ones(len(QLAB), bool)
SPL = {"IS": Q_IS, "OOS": Q_OOS, "ALL": ALL}
YEARS = list(range(2016, 2026))
heavy_bds = (p.grp.values == "BDS")
adv = E2.adv60.values
adv_lo = pd.Series(adv).groupby(QC).transform(lambda s: s.rank(pct=True)).values <= 1 / 3
fiin = (p.mc_src.values == "fiin")


def mask_for(k, extra=None):
    m = M0 & np.isfinite(X[k]) & np.isfinite(X["K"])
    if extra is not None:
        m &= extra
    return m


def yearly(pt, qok):
    return {y: (float(np.nanmean(pt[qok & (QY == y)])) if (qok & (QY == y)).any() else np.nan) for y in YEARS}


def evaluate(args):
    k, N, Bx, extra_name = args
    extra = {"none": None, "noBDS": ~heavy_bds, "noADVlo": ~adv_lo, "fiin": fiin}[extra_name]
    m = mask_for(k, extra)
    cols = {"K": X["K"], "X": X[k], "F": X["F"], "S": X["S"]}
    if k == "E":
        cols["Ec"] = X["E_const"]
    res = L.run(ctx, m, yN[N], cols, "K", seed=SEED + 100 * N + Bm.CANDS.index(k) if k in Bm.CANDS else SEED + N, B=Bx)
    o = {"n": res["n"], "n_tk": res["n_tk"]}
    for sp, qs in SPL.items():
        o[sp] = {nm: L.agg(ctx, res, nm, qs, yrblock=(extra_name == "none")) for nm in
                 ["IC:X", "IC:F", "IC:S", "IC:K", "PIC:X"] + (["IC:Ec"] if k == "E" else [])}
        if extra_name == "none":
            o[sp]["dXF"] = L.agg_diff(ctx, res, "IC:X", "IC:F", qs)
            o[sp]["dXS"] = L.agg_diff(ctx, res, "IC:X", "IC:S", qs)
            if k == "E":
                o[sp]["dEEc"] = L.agg_diff(ctx, res, "IC:X", "IC:Ec", qs)
    if extra_name == "none":
        q = res["qok"]; pt = res["point"]["IC:X"]
        yr = yearly(pt, q); o["ic_by_year"] = yr
        o["loyo"] = {y: float(np.nanmean(pt[q & (QY != y)])) for y in YEARS if (q & (QY == y)).any()}
        top2 = sorted([y for y in yr if np.isfinite(yr[y])], key=lambda y: -yr[y])[:2]
        o["drop_top2"] = {"years": top2, "ic": float(np.nanmean(pt[q & ~np.isin(QY, top2)]))}
        bt = np.nanmean(res["boot"]["PIC:X"][:, q], axis=1)
        o["p_PIC_K_all"] = float(max((bt <= 0).mean(), 1 / Bx))
        # t-stat khối năm cho IC toàn kỳ
        rng = np.random.default_rng(SEED + 77 + N)
        bs = L._yrboot(ctx, pt, q, rng, Bx)
        o["t_yr"] = float(np.nanmean(pt[q]) / np.std(bs))
        o["ic_by_year_F"] = yearly(res["point"]["IC:F"], q); o["ic_by_year_S"] = yearly(res["point"]["IC:S"], q)
    return (k, N, extra_name, o)


def checkshrink():
    """K_shrink: IC(X^c) == IC(X) — rank bất biến."""
    worst = 0.0
    for k in Bm.CANDS:
        m = mask_for(k)
        for c in (0.25, 0.5, 0.75):
            xc = np.log((MC0 ** (1 - c) * V[k] ** c) / MC0)
            for N in HP:
                r1 = L.run(ctx, m, yN[N], {"K": X["K"], "X": X[k]}, "K", B=5)
                r2 = L.run(ctx, m, yN[N], {"K": X["K"], "X": xc}, "K", B=5)
                d = np.nanmax(np.abs(r1["point"]["IC:X"] - r2["point"]["IC:X"]))
                worst = max(worst, float(d))
    assert worst < 1e-12, worst
    return worst


def pbo_cscv(mat):
    """mat: (năm × cấu hình) IC. CSCV chia đôi năm."""
    T, Kc = mat.shape
    idx = range(T); lam = []
    for S in itertools.combinations(idx, T // 2):
        Sb = [i for i in idx if i not in S]
        isv = np.nanmean(mat[list(S)], 0); oov = np.nanmean(mat[Sb], 0)
        best = int(np.nanargmax(isv))
        rk = (pd.Series(oov).rank().values[best]) / (Kc + 1)
        lam.append(np.log(rk / (1 - rk)))
    lam = np.array(lam)
    return float((lam <= 0).mean())


def emax(n):
    g = 0.5772156649
    return float((1 - g) * norm.ppf(1 - 1 / n) + g * norm.ppf(1 - 1 / (n * np.e)))


if __name__ == "__main__":
    S = {"prelock": open(os.path.join(OUT, "prelock_md5.txt")).read().split("\n")[0], "B": B, "BR": BR,
         "n_M0": int(M0.sum()), "wbar": AUX["wbar"], "n_trials": 9, "n_trials_cum": 434}
    S["shrink_maxdev"] = checkshrink(); print("shrink ok", S["shrink_maxdev"], flush=True)
    keys = Bm.CANDS + ["C4"]
    jobs = [(k, N, B, "none") for k in keys for N in HP]
    jobs += [(k, N, BR, "none") for k in keys for N in HS]
    jobs += [(k, N, BR, e) for k in Bm.CANDS for N in HP for e in ("noBDS", "noADVlo", "fiin")]
    with mp.get_context("fork").Pool(int(os.environ.get("NPROC", 6))) as pool:
        res = pool.map(evaluate, jobs, chunksize=1)
    R_ = {}
    for k, N, e, o in res:
        R_.setdefault(k, {}).setdefault(e, {})[str(N)] = o
    S["res"] = R_

    # ---------------- chấm T1–T6
    ex0 = lambda ci: ci[0] is not None and ci[0] > 0
    rows = []
    # BH theo N
    bh = {}
    for N in HP:
        ps = np.array([R_[k]["none"][str(N)]["p_PIC_K_all"] for k in Bm.CANDS])
        o = np.argsort(ps); m = len(ps); thr = 0.10 * (np.arange(1, m + 1)) / m
        passed = ps[o] <= thr
        kmax = np.max(np.where(passed)[0]) if passed.any() else -1
        surv = np.zeros(m, bool); surv[o[:kmax + 1]] = True
        bh[N] = dict(zip(Bm.CANDS, surv.tolist()))
    S["BH"] = {str(N): bh[N] for N in HP}
    # PBO N=6 trên IC theo năm (hỗ trợ riêng)
    cfg = Bm.CANDS + ["F", "S", "C4"]
    mat = []
    for k in Bm.CANDS:
        mat.append([R_[k]["none"]["6"]["ic_by_year"][y] for y in YEARS])
    mat.append([R_["A1"]["none"]["6"]["ic_by_year_F"][y] for y in YEARS])   # F, S trên hỗ trợ A1 (rộng nhất ~M0)
    mat.append([R_["A1"]["none"]["6"]["ic_by_year_S"][y] for y in YEARS])
    mat.append([R_["C4"]["none"]["6"]["ic_by_year"][y] for y in YEARS])
    mat = np.array(mat).T
    S["PBO_N6"] = pbo_cscv(mat); S["PBO_cfg"] = cfg
    S["Emax_9"] = emax(9); S["Emax_434"] = emax(434)
    for k in Bm.CANDS:
        r = R_[k]["none"]; g = lambda N, sp, nm: r[str(N)][sp][nm]
        t1 = (sum(g(N, "IS", "IC:X")["pt"] > 0 for N in HP) >= 2 and
              all(g(N, "OOS", "IC:X")["pt"] > 0 for N in HP) and
              sum(ex0(g(N, "OOS", "IC:X")["ci_tk"]) for N in HP) >= 2)
        t2 = (sum(g(N, "ALL", "PIC:X")["pt"] > 0 and ex0(g(N, "ALL", "PIC:X")["ci_tk"]) for N in HP) >= 2 and
              sum(g(N, "IS", "PIC:X")["pt"] > 0 and g(N, "OOS", "PIC:X")["pt"] > 0 for N in HP) >= 2)
        if k == "E":
            t2 = t2 and sum(g(N, "ALL", "dEEc")["pt"] > 0 for N in HP) >= 2
        t3 = (all(min(r[str(N)]["loyo"].values()) > 0 for N in HP) and
              sum(r[str(N)]["drop_top2"]["ic"] > 0 for N in HP) >= 2)
        t4 = sum(ex0(g(N, "ALL", "IC:X")["ci_yr"]) for N in HP) >= 2
        t5 = sum(bh[N][k] for N in HP) >= 2
        t6 = (sum(g(N, "OOS", "dXF")["pt"] > 0 and ex0(g(N, "OOS", "dXF")["ci_tk"]) for N in HP) >= 2 and
              all(g(N, "IS", "dXF")["pt"] >= -0.03 for N in HP) and S["PBO_N6"] < 0.5 and
              r["6"]["t_yr"] > S["Emax_9"])
        rows.append({"cand": k, "T1": t1, "T2": t2, "T3": t3, "T4": t4, "T5": t5, "T6": t6,
                     "display_ok": all([t1, t2, t3, t4, t5]), "replace_ok": all([t1, t2, t3, t4, t5, t6]),
                     **{f"IC{N}_{sp}": round(g(N, sp, "IC:X")["pt"], 4) for N in HP for sp in ("IS", "OOS")},
                     **{f"PICK{N}_ALL": round(g(N, "ALL", "PIC:X")["pt"], 4) for N in HP},
                     **{f"dXF{N}_OOS": round(g(N, "OOS", "dXF")["pt"], 4) for N in HP},
                     "t_yr6": round(r["6"]["t_yr"], 2), "n12": r["12"]["n"]})
    T = pd.DataFrame(rows); T.to_csv(os.path.join(OUT, "cands_table.csv"), index=False)
    S["table"] = rows
    print(T.to_string(), flush=True)
    print("PBO", S["PBO_N6"], "Emax9", S["Emax_9"], "Emax434", S["Emax_434"])

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if not np.isfinite(o) else round(float(o), 10)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        return o
    json.dump(clean(S), open(os.path.join(OUT, "summary.json"), "w"), indent=1, sort_keys=True)
