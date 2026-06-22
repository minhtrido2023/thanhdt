#!/usr/bin/env python3
"""backtest_recovery_alloc.py — exposure-overlay backtest of the valuation-conditioned recovery
re-risk thesis (build step 2). Faithful to backtest_workflow.py NAV mechanics; tests the thesis at
the EXPOSURE altitude (VNINDEX beta, how DT5G itself was validated), NOT the custom30V stock-picker.

Baseline DT5G curve: state->weight {CRISIS 0.0, BEAR 0.2, NEUTRAL 0.7, BULL 1.0, EXBULL 1.3}.
Recovery variant: in CRISIS/BEAR, IF market cheap (causal median pb_z over liquid ticker_prune,
prior-month, <= thr) -> deploy MORE (boosted weight). Everything else identical.

NAV: pv[t]=pv[t-1]*(1 + w*r_vni + max(0,1-w)*dep - max(0,w-1)*borrow - |dw|*TC); T+1 (weight lagged),
3-session ramp, TC=0.1%/traded, deposit=actual Big-4 (idle cash yield, honest), borrow=10%/yr.
No look-ahead: state & pb_z & deposit all causal/lagged. Usage: source ./wc_env.sh && $DNA_PYEXE backtest_recovery_alloc.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import bq
from deposit_rate_vn import DEPOSIT_EVENTS

WMAP = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}     # baseline DT5G allocation curve
TC, BORROW = 0.001, 0.10
RAMP = 3

def load():
    vni = bq("SELECT t.time, ANY_VALUE(t.VNINDEX) v FROM tav2_bq.ticker AS t WHERE t.VNINDEX IS NOT NULL AND t.time>=DATE '2014-01-01' GROUP BY t.time ORDER BY t.time")
    vni["time"] = pd.to_datetime(vni["time"]); vni = vni.set_index("time")
    st = bq("SELECT time, state FROM tav2_bq.vnindex_5state_dt5g_live ORDER BY time")
    st["time"] = pd.to_datetime(st["time"]); st = st.set_index("time")["state"]
    mc = bq("""SELECT FORMAT_DATE('%Y-%m', t.time) ym,
      APPROX_QUANTILES(SAFE_DIVIDE(t.PB - t.PB_MA5Y, NULLIF(t.PB_SD5Y,0)), 2)[OFFSET(1)] AS med_pbz
    FROM tav2_bq.ticker_prune AS t WHERE t.PB_SD5Y>0 AND t.Trading_Value_1M_P50>3e9 AND t.time>=DATE '2013-01-01'
    GROUP BY ym ORDER BY ym""")
    mc["m"] = pd.PeriodIndex(mc["ym"], freq="M")
    pbz_m = mc.set_index("m")["med_pbz"]
    d = vni.copy()
    d["r"] = d["v"].pct_change().fillna(0.0)
    d["state"] = st.reindex(d.index).ffill()
    # causal cheap signal: use PRIOR completed month's median pb_z (known before the month starts)
    cur_m = d.index.to_period("M")
    d["pbz"] = [pbz_m.get(m - 1, np.nan) for m in cur_m]
    d["pbz"] = d["pbz"].ffill()
    dep = pd.Series({pd.Timestamp(dt): v for dt, v in DEPOSIT_EVENTS}).sort_index()
    d["dep_yr"] = dep.reindex(dep.index.union(d.index)).ffill().reindex(d.index) / 100.0
    return d.dropna(subset=["state"])

def run(d, recovery=None, thr=-0.3, depth=None):
    """recovery: None=baseline; dict {1,2}=fixed boost when pbz<=thr.
    depth=(thr_start, thr_full, wmax): DEPTH-SCALED — in CRISIS/BEAR, deploy scales linearly with
    cheapness from base (at pbz=thr_start) up to wmax (at pbz<=thr_full). Bet bigger the cheaper."""
    n = len(d); w = np.zeros(n); pv = np.ones(n)
    r = d["r"].values; state = d["state"].values.astype(int)
    pbz = d["pbz"].values; dep_d = (1 + d["dep_yr"].values) ** (1/252) - 1
    bor_d = (1 + BORROW) ** (1/252) - 1
    w_prev = 0.0
    targets = np.zeros(n)
    for t in range(n):
        s = state[t]; base = WMAP[s]
        tgt = base
        if depth and s in (1, 2) and pd.notna(pbz[t]) and pbz[t] <= depth[0]:
            ts, tf, wmax = depth
            frac = min(max((ts - pbz[t]) / (ts - tf), 0.0), 1.0)
            tgt = base + frac * (wmax - base)
        elif recovery and s in (1, 2) and pd.notna(pbz[t]) and pbz[t] <= thr:
            tgt = recovery[s]
        targets[t] = tgt
    for t in range(n):
        # T+1 execution: weight applied today was decided from YESTERDAY's target (lag), ramped 3 sessions
        tgt = targets[t-1] if t > 0 else 0.0
        step = (tgt - w_prev) / RAMP
        w_t = w_prev + step if abs(tgt - w_prev) > 0.03 else tgt    # snap if tiny
        w_t = max(min(w_t, tgt), w_prev) if tgt >= w_prev else min(max(w_t, tgt), w_prev)
        dw = abs(w_t - w_prev)
        gross = (1 + w_t * r[t] + max(0.0, 1 - w_t) * dep_d[t]
                 - max(0.0, w_t - 1) * bor_d - dw * TC)
        pv[t] = (pv[t-1] if t > 0 else 1.0) * gross
        w[t] = w_t; w_prev = w_t
    out = d.copy(); out["nav"] = pv; out["w"] = w
    return out

def metrics(out):
    nav = out["nav"]; r = nav.pct_change().dropna()
    yrs = (out.index[-1] - out.index[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1/yrs) - 1
    spd = len(r) / yrs                                  # sessions/year (calendar-faithful)
    sharpe = r.mean() / r.std() * np.sqrt(spd) if r.std() > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min()
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    return cagr, sharpe, dd, calmar

def seg(out, lo, hi):
    s = out[(out.index.year >= lo) & (out.index.year <= hi)]
    if len(s) < 50: return np.nan
    nav = s["nav"] / s["nav"].iloc[0]; yrs = (s.index[-1]-s.index[0]).days/365.25
    return nav.iloc[-1] ** (1/yrs) - 1

def main():
    d = load()
    print(f"loaded {len(d)} sessions {d.index[0].date()} -> {d.index[-1].date()}; "
          f"cheap-months coverage pbz: {d['pbz'].notna().mean():.2f}")
    variants = {
        "BASELINE (DT5G curve)":          dict(),
        "recovery mild  (C.35,B.55)":     dict(recovery={1:0.35, 2:0.55}, thr=-0.3),
        "recovery deep  (C.70,B.70)":     dict(recovery={1:0.70, 2:0.70}, thr=-0.3),
        "DEPTH-scaled wmax0.9 (-.2..-.8)":dict(depth=(-0.2, -0.8, 0.9)),
        "DEPTH-scaled wmax1.0 (-.3..-.7)":dict(depth=(-0.3, -0.7, 1.0)),
        "DEPTH margin wmax1.3 (-.3..-.7)":dict(depth=(-0.3, -0.7, 1.3)),
        "DEPTH margin wmax1.5 (-.3..-.7)":dict(depth=(-0.3, -0.7, 1.5)),
        "DEPTH margin wmax1.7 (-.3..-.7)":dict(depth=(-0.3, -0.7, 1.7)),
    }
    # verified drop-to-call by leverage (Mafee broker-API + Wendy, equity-basis call40/forcesell30)
    CALL = {1.0: None, 1.2: -0.722, 1.3: -0.615, 1.5: -0.444, 1.7: -0.314, 2.0: -0.167}
    print(f"\n{'variant':33} {'CAGR':>6} {'Sharpe':>6} {'MaxDD':>7} {'Calmar':>6} | {'IS14-19':>7} {'OOS20+':>7}")
    rows = {}
    for name, kw in variants.items():
        out = run(d, **kw)
        c, sh, dd, cal = metrics(out)
        isv, oosv = seg(out, 2014, 2019), seg(out, 2020, 2026)
        rows[name] = out
        print(f"{name:33} {c*100:>5.1f}% {sh:>6.2f} {dd*100:>6.1f}% {cal:>6.2f} | {isv*100:>6.1f}% {oosv*100:>6.1f}%")
    # ---- SAFE-LEVERAGE stress test: worst NAV drawdown experienced WHILE LEVERED (w>1) vs verified call ----
    print(f"\n{'leverage variant':33} {'peak_w':>6} {'worstDD-while-levered':>21} {'call-thr':>9} {'buffer':>7}")
    for name, kw in variants.items():
        wmax = kw.get("depth", (0,0,1.0))[2]
        if wmax <= 1.0: continue
        out = rows[name].reset_index(drop=True); lev_mask = out["w"] > 1.0
        if not lev_mask.any(): continue
        # for each contiguous LEVERED episode, anchor at its start NAV, measure worst drop until de-levered
        worst = 0.0; runs = (lev_mask != lev_mask.shift()).cumsum()
        for _, grp in out.groupby(runs):
            if grp["w"].iloc[0] > 1.0:
                anchor = grp["nav"].iloc[0]
                worst = min(worst, (grp["nav"]/anchor - 1.0).min())   # drop from where we levered up
        callt = CALL.get(round(wmax,1))
        buf = f"{(callt - worst):.0%}" if callt else "—"
        print(f"{name:33} {out['w'].max():>6.2f} {worst*100:>20.1f}% {(callt*100 if callt else 0):>8.1f}% {buf:>7}")
    print("  worstDD-while-levered = deepest NAV drop during w>1 windows; call-thr = verified margin-call drop;")
    print("  buffer = how much MORE the market must fall past the realized worst before a call. Bigger = safer.")
    # self-check: deploy fired + no look-ahead
    bo = rows["DEPTH-scaled wmax1.0 (-.3..-.7)"]
    fired = ((bo["state"].isin([1,2])) & (bo["pbz"] <= -0.3)).sum()
    print(f"\nself-check: recovery deploy fired {fired} sessions (cheap CRISIS/BEAR); "
          f"weight is yesterday-target ramped (T+1, no look-ahead); deposit/pbz causal.")
    # show WHEN it deployed (episode faithfulness: should hit COVID-2020 & SCB-2022, NOT mid-2022 expensive)
    fb = bo[(bo["state"].isin([1,2])) & (bo["pbz"] <= -0.3)]
    if len(fb):
        yrs = fb.groupby(fb.index.to_period("M")).size()
        print("deploy-fired months:", ", ".join(str(m) for m in yrs.index.astype(str)))

if __name__ == "__main__":
    main()
