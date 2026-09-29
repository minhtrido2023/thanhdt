#!/usr/bin/env python3
"""Baseline (prod custom30V funnel: gate fa_ratings_8l.rating<=3 -> top-60 liquid pool ->
yieldcombo rank(1/PE)+rank(1/PCF) -> top-30, equal-weight, quarterly rebal) vs GOLDEN-FLOOR
(same funnel + additionally require ROE_Min3Y>=0 & CF_OA_TTM>0 before the yieldcombo rank).
Standalone research script -- does NOT touch custom_basket.py (the live-cron production module).
Simplifications vs full pt_v23_audit_2014.py harness (declared, not hidden):
  - equal-weight (production uses weight_scheme="namecap", cap 10%/name -- with 30 names
    equal-weight is 3.3%/name, well under cap, so namecap only binds after MTM drift; the
    static rebalance NAV path is expected to be very close, not identical).
  - rebal = calendar quarter-start (qstart), production live default is q2m5 (quarter start
    +5 sessions after the BCTC-deadline cluster). Timing shift of a few days at 48 rebalance
    points over 12y, not a selection-logic difference.
  - no transaction cost / no margin -- gross NAV only, for isolating the SELECTION effect.
  - ROE_Min3Y / CF_OA read off tav2_bq.ticker daily cadence (same as PE), NOT Release_Date-
    staggered like custom_basket.py's own QFLOOR knob.
"""
import pandas as pd, numpy as np, os

W = os.path.dirname(os.path.abspath(__file__))
POOL_N, TOP_N = 60, 30

rat = pd.read_csv(f"{W}/fa_ratings_8l.csv", parse_dates=["eff_date"])
q = pd.read_csv(f"{W}/quarterly_panel.csv", parse_dates=["q"])
px = pd.read_csv(f"{W}/daily_close.csv", parse_dates=["time"])
vni = pd.read_csv(f"{W}/vnindex.csv", parse_dates=["time"])

rat = rat.sort_values(["ticker", "eff_date"])
rat_by_tk = {tk: (g["eff_date"].tolist(), g["rating"].tolist()) for tk, g in rat.groupby("ticker")}

def rating_asof(tk, d):
    e = rat_by_tk.get(tk)
    if not e:
        return np.nan
    import bisect
    i = bisect.bisect_right(e[0], d) - 1
    return e[1][i] if i >= 0 else np.nan

pivot = px.pivot_table(index="time", columns="ticker", values="Close").sort_index()
dates = pivot.index

qtrs = sorted(q["q"].unique())
qtrs = [pd.Timestamp(x) for x in qtrs]

def select_pool(qd_src, golden_floor):
    """qd_src = the completed quarter whose stats feed selection for the NEXT quarter's rebal."""
    day = q[q["q"] == qd_src].copy()
    day = day[day["liq"].notna()]
    day = day.sort_values("liq", ascending=False)
    gated = []
    for r in day.itertuples():
        rt = rating_asof(r.ticker, qd_src)
        if not (pd.notna(rt) and rt <= 3):
            continue
        if golden_floor:
            if not (pd.notna(r.roe_min3y) and r.roe_min3y >= 0 and pd.notna(r.cfo_ttm) and r.cfo_ttm > 0):
                continue
        gated.append(r.ticker)
        if len(gated) >= POOL_N:
            break
    pool = day[day["ticker"].isin(gated)]
    ey_r = pool.set_index("ticker")["ey"].rank(pct=True)
    cfy_r = pool.set_index("ticker")["cfy"].rank(pct=True)
    score = (ey_r.fillna(0.5) + cfy_r.fillna(0.5)).sort_values(ascending=False)
    return list(score.index[:TOP_N]), len(gated)

def build_nav(golden_floor):
    qtr_series = pd.Series(dates).dt.to_period("Q").apply(lambda p: p.start_time).values
    nav, nav_dates, pool_sizes = [], [], []
    current_qtr, current_weights, port_value = None, None, 1.0
    weight_check = []
    for i, d in enumerate(dates):
        qd = pd.Timestamp(qtr_series[i])
        if qd != current_qtr:
            prior_qs = [x for x in qtrs if x < qd]
            src_q = max(prior_qs) if prior_qs else None
            if src_q is not None:
                sel, npool = select_pool(src_q, golden_floor)
                sel = [t for t in sel if t in pivot.columns and not pd.isna(pivot.loc[d, t])]
                pool_sizes.append(npool)
            else:
                sel = []
            current_qtr = qd
            if len(sel) == 0:
                current_weights = None
            else:
                w_each = port_value / len(sel)
                current_weights = {t: w_each / pivot.loc[d, t] for t in sel}
                tot_w = sum(u * pivot.loc[d, t] for t, u in current_weights.items())
                weight_check.append(abs(tot_w - port_value))
        if current_weights is not None:
            vals = []
            for t, u in list(current_weights.items()):
                p = pivot.loc[d, t]
                if pd.isna(p):
                    col = pivot[t]
                    p = col.loc[:d].ffill().iloc[-1]
                if not pd.isna(p):
                    vals.append(u * p)
            if vals:
                port_value = sum(vals)
        nav.append(port_value)
        nav_dates.append(d)
    NAV = pd.DataFrame({"time": nav_dates, "nav": nav})
    return NAV, weight_check, pool_sizes

for gf, tag in [(False, "baseline"), (True, "gfloor")]:
    NAV, wchk, poolsz = build_nav(gf)
    NAV.to_csv(f"{W}/nav_{tag}.csv", index=False)
    years = (NAV.time.iloc[-1] - NAV.time.iloc[0]).days / 365.25
    cagr = NAV.nav.iloc[-1] ** (1 / years) - 1
    print(f"[{tag}] weight-check max_err={max(wchk):.2e} pool_size median={np.median(poolsz):.0f} "
          f"min={min(poolsz)} max={max(poolsz)}")
    print(f"[{tag}] CAGR={100*cagr:.2f}% total={100*(NAV.nav.iloc[-1]-1):.1f}% "
          f"range={NAV.time.min().date()}..{NAV.time.max().date()}")
