#!/usr/bin/env python3
"""Multiple-testing discipline for the Top-5 sleeve: pre-declared variant grid + DSR + PBO(CSCV).

N_trials is the FULL grid below (24 configs), declared before any variant result was read.
The gating pool is lens-independent, so pool_primary.csv is reused verbatim for every config —
only the score aggregation (lenses), the cut (n_top) and the weighting change.

DSR  : Bailey & Lopez de Prado (2014), on daily NAV returns of the BEST config,
       deflated by the observed dispersion of Sharpe across the 24 trials.
PBO  : CSCV (Bailey et al. 2016), S=8 season-blocks -> C(8,4)=70 IS/OOS splits,
       ranked on season-level excess-vs-VNINDEX mean (the sleeve's decision metric).
"""
import os, sys, json, itertools
import numpy as np, pandas as pd
from math import comb
from scipy.stats import norm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import load, price_frame, next_td, metrics, fwd_ret, OUT, CAPITAL, TC

LENS_SETS = [("ey",), ("ey", "cfy"), ("ey", "cfy", "ps")]
N_TOPS    = [3, 5, 10, 15]
WEIGHTS   = ["equal", "score"]
N_TRIALS  = len(LENS_SETS) * len(N_TOPS) * len(WEIGHTS)
COL = {"ey": "ey_p", "cfy": "cfy_p", "ps": "ps_p"}


def sel_for(pool, lenses, n_top, weighting):
    use = [COL[l] for l in lenses]
    p = pool.copy()
    p["score"] = p[use].mean(axis=1, skipna=True)
    p = p.dropna(subset=["score"])
    p = p.sort_values(["season", "score", "ticker"], ascending=[True, False, True])
    top = p.groupby("season", sort=False).head(n_top).copy()
    if weighting == "equal":
        top["w"] = 1.0
    else:                      # score-weighted, renormalised inside each season
        top["w"] = top["score"].clip(lower=1e-9)
    top["w"] = top["w"] / top.groupby("season")["w"].transform("sum")
    return top


def simulate_w(sel, P, cal, seasons, capital=CAPITAL, tc=TC):
    """Same book as engine.simulate but honouring per-name target weights."""
    rebals = [pd.Timestamp(x) for x in seasons["rebal"]]
    execs = [next_td(cal, r, 1) for r in rebals]
    pairs = [(s, e) for s, e in zip(seasons["season"], execs) if e is not None]
    exec_dates = {e: s for s, e in pairs}
    cash, shares, last_px = capital, {}, {}
    fees = 0.0; notional_abs = 0.0
    rows = []
    for d in cal[cal >= pairs[0][1]]:
        if d in P.index:
            row = P.loc[d]
            for t in list(shares):
                v = row.get(t, np.nan)
                if pd.notna(v): last_px[t] = float(v)
        if d in exec_dates:
            g = sel[sel["season"] == exec_dates[d]]
            tw = dict(zip(g["ticker"], g["w"]))
            for t in list(tw):
                v = P.at[d, t] if (d in P.index and t in P.columns) else np.nan
                if pd.notna(v): last_px[t] = float(v)
            tw = {t: w for t, w in tw.items() if last_px.get(t)}
            s = sum(tw.values())
            nav = cash + sum(sh * last_px.get(t, 0.0) for t, sh in shares.items())
            new_sh = {t: (nav * w / s) / last_px[t] for t, w in tw.items()} if s > 0 else {}
            for t in set(list(shares) + list(new_sh)):
                dsh = new_sh.get(t, 0.0) - shares.get(t, 0.0)
                if abs(dsh) < 1e-12: continue
                n_ = dsh * last_px[t]; f_ = abs(n_) * tc
                cash -= n_ + f_; fees += f_; notional_abs += abs(n_)
            shares = {t: s_ for t, s_ in new_sh.items() if abs(s_) > 1e-12}
        rows.append({"time": d, "nav": cash + sum(sh * last_px.get(t, 0.0) for t, sh in shares.items())})
    nav = pd.DataFrame(rows).set_index("time")["nav"]
    return nav, {"fees_vnd": fees, "turnover_vnd": notional_abs}


def season_excess(sel, P, cal, seasons):
    """Season-level sleeve return (weighted) and excess vs VNINDEX, horizon = to next rebalance."""
    ex = [next_td(cal, pd.Timestamp(r), 1) for r in seasons["rebal"]]
    out = []
    for i, s in enumerate(seasons["season"]):
        e0 = ex[i]; e1 = ex[i + 1] if i + 1 < len(ex) else None
        if e0 is None or e1 is None or e1 > P.index.max(): continue
        g = sel[sel["season"] == s]
        r, w = [], []
        for t, wi in zip(g["ticker"], g["w"]):
            v = fwd_ret(P, cal, t, e0, e1)
            if np.isfinite(v): r.append(v); w.append(wi)
        if not r: continue
        w = np.array(w) / np.sum(w)
        vni = fwd_ret(P, cal, "VNINDEX", e0, e1)
        out.append({"season": s, "ret": float(np.dot(w, r)),
                    "exc": float(np.dot(w, r) - vni) if np.isfinite(vni) else np.nan})
    return pd.DataFrame(out)


def dsr(ret, n_trials, sr_variance):
    """Deflated Sharpe Ratio on a per-observation return series."""
    r = np.asarray(ret, float); r = r[np.isfinite(r)]
    T = len(r); sr = r.mean() / r.std(ddof=1)
    g3 = pd.Series(r).skew(); g4 = pd.Series(r).kurtosis() + 3.0
    e = np.euler_gamma
    sr0 = np.sqrt(sr_variance) * ((1 - e) * norm.ppf(1 - 1.0 / n_trials)
                                  + e * norm.ppf(1 - 1.0 / (n_trials * np.e)))
    den = np.sqrt(1 - g3 * sr + (g4 - 1) / 4.0 * sr ** 2)
    return float(norm.cdf((sr - sr0) * np.sqrt(T - 1) / den)), float(sr), float(sr0)


def pbo_cscv(M, S=8):
    """M: (n_seasons x n_configs) excess-return matrix. Returns PBO."""
    n, k = M.shape
    blocks = np.array_split(np.arange(n), S)
    lam = []
    for idx in itertools.combinations(range(S), S // 2):
        is_i = np.concatenate([blocks[i] for i in idx])
        oos_i = np.concatenate([blocks[i] for i in range(S) if i not in idx])
        is_perf, oos_perf = M[is_i].mean(axis=0), M[oos_i].mean(axis=0)
        best = int(np.argmax(is_perf))
        rank = (oos_perf < oos_perf[best]).sum() + 1        # 1..k, k = best OOS
        w_ = rank / (k + 1.0)
        lam.append(np.log(w_ / (1 - w_)))
    lam = np.array(lam)
    return float((lam <= 0).mean()), lam


if __name__ == "__main__":
    d = load()
    P = price_frame(d["px"]).ffill()
    cal = d["calendar"]["time"].sort_values().reset_index(drop=True)
    seasons = d["seasons"]
    pool = pd.read_csv(os.path.join(OUT, "pool_primary.csv"))
    print(f"=== variant grid: N_trials = {N_TRIALS} (pre-declared) ===")

    res, exc_cols, nav_ret = [], {}, {}
    for lenses, n_top, wt in itertools.product(LENS_SETS, N_TOPS, WEIGHTS):
        name = f"{'+'.join(lenses)}|top{n_top}|{wt}"
        sel = sel_for(pool, lenses, n_top, wt)
        nav, cost = simulate_w(sel, P, cal, seasons)
        m = metrics(nav)
        se = season_excess(sel, P, cal, seasons)
        exc_cols[name] = se.set_index("season")["exc"]
        nav_ret[name] = nav.pct_change().dropna()
        res.append({"config": name, "lenses": "+".join(lenses), "n_top": n_top, "weighting": wt,
                    "CAGR": m["CAGR"], "Sharpe": m["Sharpe"], "MaxDD": m["MaxDD"],
                    "Calmar": m["Calmar"], "exc_mean": se["exc"].mean(),
                    "exc_med": se["exc"].median(), "win": (se["exc"] > 0).mean(),
                    "fees_vnd": cost["fees_vnd"]})
        print(f"  {name:26s} CAGR {m['CAGR']*100:6.2f}%  Sharpe {m['Sharpe']:.3f}  "
              f"MaxDD {m['MaxDD']*100:7.2f}%  excVNI {se['exc'].mean()*100:5.2f}%")

    R = pd.DataFrame(res).sort_values("Sharpe", ascending=False)
    R.to_csv(os.path.join(OUT, "variants.csv"), index=False)
    print("\n=== ranked by Sharpe ===")
    print(R.to_string(index=False))

    E = pd.DataFrame(exc_cols).dropna()
    M = E.values
    pbo, lam = pbo_cscv(M, S=8)
    best = R.iloc[0]["config"]
    sr_var = np.var([r["Sharpe"] for r in res], ddof=1) / 252.0   # per-observation scale
    dsr_v, sr, sr0 = dsr(nav_ret[best], N_TRIALS, sr_var)
    prim = "ey+cfy+ps|top5|equal"
    dsr_p, sr_p, _ = dsr(nav_ret[prim], N_TRIALS, sr_var)

    summ = {"N_trials": N_TRIALS, "n_seasons": int(E.shape[0]), "n_configs": int(E.shape[1]),
            "PBO_cscv_S8": pbo, "n_splits": comb(8, 4),
            "best_by_sharpe": best, "DSR_best": dsr_v, "SR_best_daily": sr, "SR0_threshold": sr0,
            "primary": prim, "DSR_primary": dsr_p, "SR_primary_daily": sr_p,
            "primary_rank_by_sharpe": int(R.reset_index(drop=True).index[R.reset_index(drop=True)["config"] == prim][0]) + 1}
    print("\n=== multiple-testing ===")
    for k, v in summ.items(): print(f"  {k:22s} {v}")
    json.dump(summ, open(os.path.join(OUT, "multiple_testing.json"), "w"), indent=2, default=str)
    E.to_csv(os.path.join(OUT, "variant_season_excess.csv"))
    print("\nartifacts ->", OUT)
