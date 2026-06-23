#!/usr/bin/env python3
"""backtest_recovery_alloc_2011.py — extend the valuation-conditioned recovery re-risk + MARGIN test
back to 2011, the user's recalled "2012 = great buy" crisis. Sibling of backtest_recovery_alloc.py
(which starts 2014 on DT5G). Two honest changes for the longer window:

  1. REGIME source = base `vnindex_5state` (v3.4b), which runs from 2000 (DT5G live only 2014+).
     Consistent across the whole 2011-2026 run. DT5G == base in benign windows and only ADDS a
     macro cap on 4 episodes 2014+ -> using the base is the MORE permissive (harder) test of the
     levered recovery deploy: no extra macro cap protects the levered book.
  2. BORROW cost = era-aware = deposit_rate + MARGIN_SPREAD (default 4%). VN margin lending in
     2011-12 was ~18-24%/yr (deposit ~14% + spread), NOT 10%. A flat 10% would flatter margin in
     exactly the high-rate crisis we are testing. dep+4% gives 2012~18%, 2020~9% — honest & causal.

NAV mechanics identical to backtest_recovery_alloc.py / backtest_workflow.py: T+1 weight lag,
3-session ramp, TC=0.1%/traded, deposit=actual Big-4 idle yield, no look-ahead (state/pbz/dep causal).
Usage: source ./wc_env.sh && $DNA_PYEXE backtest_recovery_alloc_2011.py
"""
import warnings; warnings.filterwarnings("ignore")
import os
import numpy as np, pandas as pd
from ic_panel_8l import bq
from deposit_rate_vn import DEPOSIT_EVENTS

WMAP = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}     # baseline DT5G/base allocation curve
TC = 0.001
RAMP = 3
START = os.environ.get("START", "2011-01-01")
MARGIN_SPREAD = float(os.environ.get("MARGIN_SPREAD", "0.04"))   # borrow = deposit + this
REGIME = os.environ.get("REGIME", "base")    # 'base' = vnindex_5state (2000+); 'dt5g' = live (2014+)

def load():
    vni = bq(f"SELECT t.time, ANY_VALUE(t.VNINDEX) v FROM tav2_bq.ticker AS t "
             f"WHERE t.VNINDEX IS NOT NULL AND t.time>=DATE '{START}' GROUP BY t.time ORDER BY t.time")
    vni["time"] = pd.to_datetime(vni["time"]); vni = vni.set_index("time")
    tbl = "tav2_bq.vnindex_5state_dt5g_live" if REGIME == "dt5g" else "tav2_bq.vnindex_5state"
    st = bq(f"SELECT s.time, s.state FROM {tbl} AS s ORDER BY s.time")
    st["time"] = pd.to_datetime(st["time"]); st = st.set_index("time")["state"]
    mc = bq(f"""SELECT FORMAT_DATE('%Y-%m', t.time) ym,
      APPROX_QUANTILES(SAFE_DIVIDE(t.PB - t.PB_MA5Y, NULLIF(t.PB_SD5Y,0)), 2)[OFFSET(1)] AS med_pbz
    FROM tav2_bq.ticker_prune AS t WHERE t.PB_SD5Y>0 AND t.Trading_Value_1M_P50>3e9
      AND t.time>=DATE '2010-06-01'
    GROUP BY ym ORDER BY ym""")
    mc["m"] = pd.PeriodIndex(mc["ym"], freq="M")
    pbz_m = mc.set_index("m")["med_pbz"]
    # market PE -> earnings yield monthly (VNINDEX_PE mirror is sane back to 2006; per-stock t.PE is NOT)
    pe = bq("""SELECT FORMAT_DATE('%Y-%m', t.time) ym, ANY_VALUE(t.VNINDEX_PE) vpe
      FROM tav2_bq.ticker_prune AS t WHERE t.VNINDEX_PE>0 AND t.time>=DATE '2010-06-01'
      GROUP BY ym ORDER BY ym""")
    pe["m"] = pd.PeriodIndex(pe["ym"], freq="M")
    eyield_m = (1.0 / pe.set_index("m")["vpe"])
    d = vni.copy()
    d["r"] = d["v"].pct_change().fillna(0.0)
    d["state"] = st.reindex(d.index).ffill()
    cur_m = d.index.to_period("M")
    d["pbz"] = [pbz_m.get(m - 1, np.nan) for m in cur_m]   # causal: prior completed month
    d["pbz"] = d["pbz"].ffill()
    d["eyield"] = [eyield_m.get(m - 1, np.nan) for m in cur_m]   # causal prior-month market earnings yield
    d["eyield"] = d["eyield"].ffill()
    dep = pd.Series({pd.Timestamp(dt): v for dt, v in DEPOSIT_EVENTS}).sort_index()
    d["dep_yr"] = dep.reindex(dep.index.union(d.index)).ffill().reindex(d.index) / 100.0
    d["fed_spread"] = d["eyield"] - d["dep_yr"]           # market earnings yield - deposit (cheap-vs-cash)
    return d.dropna(subset=["state"])

def run(d, recovery=None, thr=-0.3, depth=None, dep_gate=None, fed_gate=None):
    """dep_gate=(dep_floor, dep_ceiling): money-condition multiplier m on the recovery DEPLOY via the
    DEPOSIT LEVEL: m=clip((dep_ceiling-deposit)/(dep_ceiling-dep_floor),0,1). High deposit -> m->0.
    fed_gate=(spread_floor, spread_ceil): RICHER money-gate via the market Fed-spread = (1/VNINDEX_PE)
    - deposit (earnings yield vs cash). m=clip((spread-spread_floor)/(spread_ceil-spread_floor),0,1).
    Captures BOTH how cheap stocks are AND the cash hurdle in one number (the user's '1/PE thi truong vs
    lai gui'). VNINDEX_PE is sane back to 2006 (only per-stock t.PE is corrupt). Use one gate or neither."""
    n = len(d); w = np.zeros(n); pv = np.ones(n)
    r = d["r"].values; state = d["state"].values.astype(int)
    pbz = d["pbz"].values; dep_yr = d["dep_yr"].values; fed = d["fed_spread"].values
    dep_d = (1 + dep_yr) ** (1/252) - 1
    bor_yr = dep_yr + MARGIN_SPREAD                            # era-aware margin cost
    bor_d = (1 + bor_yr) ** (1/252) - 1
    w_prev = 0.0
    targets = np.zeros(n)
    for t in range(n):
        s = state[t]; base = WMAP[s]; tgt = base
        m = 1.0
        if dep_gate is not None:
            df, dc = dep_gate
            m = min(max((dc - dep_yr[t]) / (dc - df), 0.0), 1.0)
        if fed_gate is not None:
            sf, sc = fed_gate
            mf = (min(max((fed[t] - sf) / (sc - sf), 0.0), 1.0) if pd.notna(fed[t]) else 1.0)
            m = min(m, mf)
        if depth and s in (1, 2) and pd.notna(pbz[t]) and pbz[t] <= depth[0]:
            ts, tf, wmax = depth
            frac = min(max((ts - pbz[t]) / (ts - tf), 0.0), 1.0)
            tgt = base + m * frac * (wmax - base)
        elif recovery and s in (1, 2) and pd.notna(pbz[t]) and pbz[t] <= thr:
            tgt = base + m * (recovery[s] - base)
        targets[t] = tgt
    for t in range(n):
        tgt = targets[t-1] if t > 0 else 0.0
        step = (tgt - w_prev) / RAMP
        w_t = w_prev + step if abs(tgt - w_prev) > 0.03 else tgt
        w_t = max(min(w_t, tgt), w_prev) if tgt >= w_prev else min(max(w_t, tgt), w_prev)
        dw = abs(w_t - w_prev)
        gross = (1 + w_t * r[t] + max(0.0, 1 - w_t) * dep_d[t]
                 - max(0.0, w_t - 1) * bor_d[t] - dw * TC)
        pv[t] = (pv[t-1] if t > 0 else 1.0) * gross
        w[t] = w_t; w_prev = w_t
    out = d.copy(); out["nav"] = pv; out["w"] = w
    return out

def metrics(out):
    nav = out["nav"]; r = nav.pct_change().dropna()
    yrs = (out.index[-1] - out.index[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1/yrs) - 1
    spd = len(r) / yrs
    sharpe = r.mean() / r.std() * np.sqrt(spd) if r.std() > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min()
    calmar = cagr / abs(dd) if dd < 0 else np.nan
    return cagr, sharpe, dd, calmar

def seg(out, lo, hi):
    s = out[(out.index.year >= lo) & (out.index.year <= hi)]
    if len(s) < 50: return np.nan
    nav = s["nav"] / s["nav"].iloc[0]; yrs = (s.index[-1]-s.index[0]).days/365.25
    return nav.iloc[-1] ** (1/yrs) - 1

def bh(d, lo, hi):
    s = d[(d.index.year >= lo) & (d.index.year <= hi)]
    if len(s) < 50: return np.nan
    yrs = (s.index[-1]-s.index[0]).days/365.25
    return (s["v"].iloc[-1]/s["v"].iloc[0]) ** (1/yrs) - 1

def main():
    d = load()
    print(f"REGIME={REGIME} | borrow=deposit+{MARGIN_SPREAD:.0%} (era-aware) | "
          f"loaded {len(d)} sessions {d.index[0].date()} -> {d.index[-1].date()}")
    print(f"pbz coverage: {d['pbz'].notna().mean():.2f}; "
          f"state dist 2011-13: " + str(d[d.index.year<=2013]['state'].value_counts().sort_index().to_dict()))
    variants = {
        "BASELINE (no recovery)":         dict(),
        "recovery deep  (C.70,B.70)":     dict(recovery={1:0.70, 2:0.70}, thr=-0.3),
        "DEPTH lev-free wmax0.95(-.3..-.5)":dict(depth=(-0.3, -0.5, 0.95)),  # the go-live config altitude
        "DEPTH margin wmax1.3 (-.3..-.7)":dict(depth=(-0.3, -0.7, 1.3)),
        "DEPTH margin wmax1.5 (-.3..-.7)":dict(depth=(-0.3, -0.7, 1.5)),
        "DEPTH margin wmax1.7 (-.3..-.7)":dict(depth=(-0.3, -0.7, 1.7)),
        "+DEPgate m1.5 (dep6-12%)":       dict(depth=(-0.3, -0.7, 1.5), dep_gate=(0.06, 0.12)),
        "+DEPgate lev-free0.95(dep6-12%)":dict(depth=(-0.3, -0.5, 0.95), dep_gate=(0.06, 0.12)),
        "+FEDgate m1.5 (spr0..1.5%)":     dict(depth=(-0.3, -0.7, 1.5), fed_gate=(0.0, 0.015)),
        "+FEDgate lev-free0.95(spr0-1.5)":dict(depth=(-0.3, -0.5, 0.95), fed_gate=(0.0, 0.015)),
    }
    CALL = {1.0: None, 1.2: -0.722, 1.3: -0.615, 1.5: -0.444, 1.7: -0.314, 2.0: -0.167}
    print(f"\nFULL 2011-2026 + segments (CAGR). B&H VNINDEX: full {bh(d,2011,2026)*100:.1f}% | "
          f"crisis'11-13 {bh(d,2011,2013)*100:+.1f}%")
    print(f"\n{'variant':35} {'CAGR':>6} {'Sharpe':>6} {'MaxDD':>7} {'Cal':>5} | "
          f"{'11-13':>6} {'14-19':>6} {'20-26':>6}")
    rows = {}
    for name, kw in variants.items():
        out = run(d, **kw); rows[name] = out
        c, sh, dd, cal = metrics(out)
        s1, s2, s3 = seg(out,2011,2013), seg(out,2014,2019), seg(out,2020,2026)
        print(f"{name:35} {c*100:>5.1f}% {sh:>6.2f} {dd*100:>6.1f}% {cal:>5.2f} | "
              f"{s1*100:>5.1f}% {s2*100:>5.1f}% {s3*100:>5.1f}%")
    # margin-call buffer stress (worst NAV drop WHILE levered vs verified call thr)
    print(f"\n{'leverage variant':35} {'peak_w':>6} {'worstDD-levered':>15} {'call-thr':>9} {'buffer':>7}")
    for name, kw in variants.items():
        wmax = kw.get("depth", (0,0,1.0))[2]
        if wmax <= 1.0: continue
        out = rows[name].reset_index(drop=True); lev_mask = out["w"] > 1.0
        if not lev_mask.any():
            print(f"{name:35} {'(never levered)':>40}"); continue
        worst = 0.0; runs = (lev_mask != lev_mask.shift()).cumsum()
        for _, grp in out.groupby(runs):
            if grp["w"].iloc[0] > 1.0:
                anchor = grp["nav"].iloc[0]
                worst = min(worst, (grp["nav"]/anchor - 1.0).min())
        callt = CALL.get(round(wmax,1))
        buf = f"{(callt - worst):.0%}" if callt else "—"
        print(f"{name:35} {out['w'].max():>6.2f} {worst*100:>14.1f}% "
              f"{(callt*100 if callt else 0):>8.1f}% {buf:>7}")
    # when did margin actually fire (should cluster at 2011-12 deep-cheap + COVID-2020)
    bo = rows["DEPTH margin wmax1.5 (-.3..-.7)"]
    levm = bo[bo["w"] > 1.0]
    if len(levm):
        mm = levm.groupby(levm.index.to_period("M")).size()
        print(f"\nmargin (w>1) fired {len(levm)} sessions, months: " +
              ", ".join(str(m) for m in mm.index.astype(str)))
    else:
        print("\nmargin never crossed w>1 (deploy ramps cap below 1.0 in practice)")

if __name__ == "__main__":
    main()
