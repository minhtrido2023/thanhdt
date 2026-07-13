#!/usr/bin/env python3
"""probe_beta_cap_c30v.py — job Taylor_20260713_114905: user asks whether custom30V should
restrict high-beta names (e.g. VIX, beta 1.50, Beta-bin 5/5) when macro turns defensive
(deposit rates rising, CPI up, liquidity down) even while DT5G stays NEUTRAL.

Pre-registered N=2 configs (declared BEFORE running, no grid — same discipline as H1/H6a):
  1. EXCL-B5-UNCOND : drop names whose PRIOR-quarter risk_rating Beta bin == 5 from the
     top-60 liquid gated pool BEFORE ranking yieldcombo = rank(1/PE)+rank(1/PCF) top-30.
     Answers: "is high beta a problem in custom30V at all?"
  2. EXCL-B5-DEFENS : same drop but ONLY in quarters where the macro is defensive =
     deposit rate 6m-momentum > +0.25pp (causal, from DEPOSIT_EVENTS step series).
     Answers the user's exact conditional proposal.

PASS = mean profit_2M >= base in BOTH IS(2014-2019) AND OOS(2020+), win%q >= 50%.
Fail at proxy tier = close the question, do NOT build a pt_v23 harness run.
Prior evidence stacked against: H1 (FSCORE-excl) FAIL, H6a (MAX5 lottery-excl AND
soft-penalty) FAIL — same mechanism (concentrated pool, exclusion dilutes value rank).
Beta PIT: risk_rating quarterly Beta bin shifted +1 quarter per ticker (prior-quarter, causal).
Usage: source ./wc_env.sh && BQ_CACHE_THREADS=1 $DNA_PYEXE probe_beta_cap_c30v.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import load
from deposit_rate_vn import deposit_events_df

POOL_N, PICK_N = 60, 30
TGT = "profit_2M"
CONFIGS = ["base", "excl_b5_uncond", "excl_b5_defens"]

def beta_bins():
    import duckdb
    con = duckdb.connect()
    rr = con.execute("""SELECT DISTINCT ticker, quarter, Beta
        FROM read_parquet('data/bq_cache/risk_rating.parquet')""").df()
    rr["qp"] = pd.PeriodIndex(rr["quarter"].str.replace("Q", "Q"), freq="Q")
    # prior-quarter (causal): bin known for quarter q is applied to rebalances in q+1
    rr["q_apply"] = rr["qp"] + 1
    return rr.set_index(["ticker", "q_apply"])["Beta"].to_dict()

def defensive_quarters(qs):
    """quarter -> True if deposit rate rose >0.25pp over trailing 6 months (causal step series)."""
    ev = deposit_events_df()
    out = {}
    for q in qs:
        t_end = q.to_timestamp(how="end")
        t_6m = t_end - pd.DateOffset(months=6)
        cur = ev[ev.time <= t_end].deposit_rate.iloc[-1] if (ev.time <= t_end).any() else np.nan
        prv = ev[ev.time <= t_6m].deposit_rate.iloc[-1] if (ev.time <= t_6m).any() else np.nan
        out[q] = bool(cur - prv > 0.25) if np.isfinite(cur) and np.isfinite(prv) else False
    return out

def main():
    d = load()
    d = d[(d["rating"] <= 3)].copy()
    d["liq"] = pd.to_numeric(d.get("turnover"), errors="coerce")
    d = d[d["liq"].notna() & d[TGT].notna()]
    bmap = beta_bins()
    qs = sorted(d["q"].unique())
    defq = defensive_quarters(qs)
    rk = lambda s: s.rank(pct=True)
    perq = {c: [] for c in CONFIGS}; perq_yr = {c: [] for c in CONFIGS}
    dropped = {c: [] for c in CONFIGS}
    nq = 0
    for qtr, g in d.groupby("q"):
        g = g.sort_values("liq", ascending=False).head(POOL_N)
        if len(g) < PICK_N + 5: continue
        ey_v  = pd.Series(np.where(g["PE"]  > 0, 1.0/g["PE"],  np.nan), index=g.index)
        cfy_v = pd.Series(np.where(g["PCF"] > 0, 1.0/g["PCF"], np.nan), index=g.index)
        yc = rk(ey_v).fillna(0.5) + rk(cfy_v).fillna(0.5)
        b5 = g["ticker"].map(lambda t: bmap.get((t, qtr)) == 5)   # NaN/missing -> False (fail-safe keep)
        nq += 1
        for c in CONFIGS:
            if c == "base":
                pool = g
            elif c == "excl_b5_uncond":
                pool = g[~b5]
            else:  # excl_b5_defens
                pool = g[~b5] if defq.get(qtr, False) else g
            dropped[c].append(int(len(g) - len(pool)))
            if len(pool) < PICK_N: pool = g   # safety: never pick <30
            sc = yc.loc[pool.index]
            pick = pool.loc[sc.sort_values(ascending=False).head(PICK_N).index]
            m = pick[TGT].mean()
            perq[c].append(m); perq_yr[c].append((qtr.year, m))
    base = np.array(perq["base"])
    print(f"beta-cap probe — fwd {TGT} of top-{PICK_N} yieldcombo picks from top-{POOL_N} liquid "
          f"gate<=3 pool, {nq} quarters | defensive quarters: "
          f"{sum(defq.values())}/{len(defq)} ({[str(q) for q,v in defq.items() if v]})\n")
    print(f"{'config':>16} {'mean2M%':>9} {'vs base':>9} {'IS(14-19)':>10} {'OOS(20+)':>9} "
          f"{'win%q':>6} {'avg_drop':>9}")
    for c in CONFIGS:
        arr = np.array(perq[c]); yrs = np.array([y for y, _ in perq_yr[c]])
        is_m  = arr[yrs <= 2019].mean(); oos_m = arr[yrs >= 2020].mean()
        win = float((arr >= base[:len(arr)]).mean()) * 100 if c != "base" else np.nan
        print(f"{c:>16} {arr.mean():>9.2f} {arr.mean()-base.mean():>+9.2f} {is_m:>10.2f} "
              f"{oos_m:>9.2f} {win:>6.0f} {np.mean(dropped[c]):>9.1f}")
    # per-year detail for the two test arms
    for c in CONFIGS[1:]:
        df = pd.DataFrame(perq_yr[c], columns=["y", "m"]).groupby("y").m.mean()
        db = pd.DataFrame(perq_yr["base"], columns=["y", "m"]).groupby("y").m.mean()
        dd = (df - db).round(2)
        print(f"\n{c} per-year delta vs base (pp): " +
              " ".join(f"{y}:{v:+.2f}" for y, v in dd.items() if abs(v) > 0.005))

if __name__ == "__main__":
    main()
