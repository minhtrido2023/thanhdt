# -*- coding: utf-8 -*-
"""analyze_basket.py — POSITION/BASKET-TIER analysis of the FSCORE enhancer legs.
Job Taylor_20260801_131833.

Tier 1 of the two-tier requirement (quant-research skill §6). Answers, for each variant:
  (i)  what the custom30V vehicle itself did — Full / IS(2014-2019) / OOS(2020+) CAGR, Sharpe,
       MaxDD, Calmar of the basket level series;
  (ii) the kept-vs-swapped decomposition (§10): for every rebalance where the enhancer changed
       membership, the forward quarter return of the names it ADDED vs the names it REMOVED —
       the direct test of "did FSCORE pick better at the margin", independent of concentration.

NOTE (stated, not buried): the basket level series is the PARKING VEHICLE's own total return.
The portfolio only parks 70% of idle cash in NEUTRAL, so a basket-tier delta does NOT translate
1:1 to NAV. That is why the engine legs exist; this file never substitutes for them.
"""
import os, sys, glob
import numpy as np, pandas as pd

WORK = "/home/trido/thanhdt/WorkingClaude"
EXPDIR = os.path.join(WORK, "data", "fscore_c30v_20260801")
sys.path.insert(0, WORK); os.chdir(WORK)

IS_END = pd.Timestamp("2019-12-31")
LEG_ORDER = ["ctrl", "tieb_k05", "tieb_k10", "tieb_k20",
             "blend_w010", "blend_w020", "blend_w040", "blend_w080", "blend_w200",
             "wtilt_t030", "wtilt_t060"]


def metrics(s):
    s = s.sort_index()
    r = s.pct_change().dropna()
    if len(r) < 50:
        return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan, Calmar=np.nan)
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (s / s.cummax() - 1).min()
    return dict(CAGR=100 * cagr, Sharpe=sh, MaxDD=100 * dd,
                Calmar=(cagr / abs(dd) if dd < 0 else np.nan))


def load_lvl(tag):
    p = os.path.join(EXPDIR, f"lvl_{tag}.csv")
    d = pd.read_csv(p, index_col=0)
    d.index = pd.to_datetime(d.index)
    return d["level"]


if __name__ == "__main__":
    print("=" * 100)
    print("TIER 1a — custom30V BASKET level series (the parking vehicle itself)")
    print("=" * 100)
    rows = []
    for tag in LEG_ORDER:
        if not os.path.exists(os.path.join(EXPDIR, f"lvl_{tag}.csv")):
            print(f"  (missing {tag})"); continue
        s = load_lvl(tag)
        f = metrics(s); i = metrics(s[s.index <= IS_END]); o = metrics(s[s.index > IS_END])
        rows.append({"leg": tag, "CAGR": f["CAGR"], "Sharpe": f["Sharpe"], "MaxDD": f["MaxDD"],
                     "Calmar": f["Calmar"], "IS_CAGR": i["CAGR"], "OOS_CAGR": o["CAGR"],
                     "IS_Sharpe": i["Sharpe"], "OOS_Sharpe": o["Sharpe"]})
    bt = pd.DataFrame(rows).set_index("leg")
    for c in ("CAGR", "IS_CAGR", "OOS_CAGR"):
        bt["d_" + c] = bt[c] - bt.loc["ctrl", c]
    print(bt.round(3).to_string())
    bt.to_csv(os.path.join(EXPDIR, "tier1_basket_metrics.csv"))

    # ---------------------------------------------------------------- kept vs swapped (§10)
    print()
    print("=" * 100)
    print("TIER 1b — KEPT vs SWAPPED decomposition: forward-quarter return of names ADDED by the")
    print("enhancer vs names it REMOVED. Basket size is ALWAYS 30, so this isolates selection")
    print("quality with zero concentration effect.")
    print("=" * 100)
    from simulate_holistic_nav import bq
    ctrl = pd.read_csv(os.path.join(EXPDIR, "mem_ctrl.csv"))
    ctrl["rebal_date"] = pd.to_datetime(ctrl["rebal_date"])
    rebals = sorted(ctrl["rebal_date"].unique())
    # universe of every ticker that appears in ANY leg
    univ = set()
    for tag in LEG_ORDER:
        p = os.path.join(EXPDIR, f"mem_{tag}.csv")
        if os.path.exists(p):
            univ |= set(pd.read_csv(p)["ticker"])
    inlist = ",".join(f"'{t}'" for t in sorted(univ))
    px = bq(f"""SELECT t.ticker, t.time, t.Close FROM tav2_bq.ticker t
WHERE t.ticker IN ({inlist}) AND t.time BETWEEN DATE '2013-12-01' AND DATE '2026-06-19'
  AND t.Close IS NOT NULL""")
    px["time"] = pd.to_datetime(px["time"])
    piv = px.pivot_table(index="time", columns="ticker", values="Close").sort_index()

    def fwd(tk, d0, d1):
        """Holding-period return of `tk` from rebal date d0 to the next rebal d1, on adjusted
        Close (the same series the basket index is chained on). NaN when either mark is absent."""
        if tk not in piv.columns:
            return np.nan
        s = piv[tk]
        a = s.loc[s.index <= d0]
        b = s.loc[s.index <= d1]
        if a.empty or b.empty:
            return np.nan
        p0, p1 = a.iloc[-1], b.iloc[-1]
        return np.nan if (not p0 or p0 <= 0) else p1 / p0 - 1

    out = []
    for tag in LEG_ORDER:
        if tag == "ctrl" or not os.path.exists(os.path.join(EXPDIR, f"mem_{tag}.csv")):
            continue
        m = pd.read_csv(os.path.join(EXPDIR, f"mem_{tag}.csv"))
        m["rebal_date"] = pd.to_datetime(m["rebal_date"])
        cs = {d: set(g["ticker"]) for d, g in ctrl.groupby("rebal_date")}
        ts = {d: set(g["ticker"]) for d, g in m.groupby("rebal_date")}
        recs = []
        for k, d0 in enumerate(rebals[:-1]):
            d1 = rebals[k + 1]
            add = ts.get(d0, set()) - cs.get(d0, set())
            rem = cs.get(d0, set()) - ts.get(d0, set())
            if not add or not rem:
                continue
            ra = np.nanmean([fwd(t, d0, d1) for t in add])
            rr = np.nanmean([fwd(t, d0, d1) for t in rem])
            if np.isnan(ra) or np.isnan(rr):
                continue
            recs.append({"rebal": d0, "n_add": len(add), "n_rem": len(rem),
                         "ret_add": ra, "ret_rem": rr, "diff": ra - rr,
                         "half": "IS" if d0 <= IS_END else "OOS"})
        if not recs:
            out.append({"leg": tag, "n_events": 0}); continue
        R = pd.DataFrame(recs)
        R.to_csv(os.path.join(EXPDIR, f"swap_{tag}.csv"), index=False)
        d = R["diff"]
        t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d))) if d.std(ddof=1) > 0 else np.nan
        o = {"leg": tag, "n_events": len(R), "mean_add_%": 100 * R.ret_add.mean(),
             "mean_rem_%": 100 * R.ret_rem.mean(), "mean_diff_pp": 100 * d.mean(),
             "t_stat": t, "hit_%": 100 * (d > 0).mean()}
        for h in ("IS", "OOS"):
            sub = R[R.half == h]["diff"]
            o[f"{h}_n"] = len(sub)
            o[f"{h}_diff_pp"] = 100 * sub.mean() if len(sub) else np.nan
            o[f"{h}_hit_%"] = 100 * (sub > 0).mean() if len(sub) else np.nan
        out.append(o)
    S = pd.DataFrame(out)
    print(S.round(3).to_string(index=False))
    S.to_csv(os.path.join(EXPDIR, "tier1_swap_decomp.csv"), index=False)
    print("\nN = independent REBALANCE EVENTS (quarterly), not name-rows. Max possible = "
          f"{len(rebals)-1} over 2014-2026.")
