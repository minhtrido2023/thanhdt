#!/usr/bin/env python3
"""W2b step 1 — the PREREG §3(3) overlay the REPORT omitted (quant-skeptic recommended_rerun #1).

Applies the idle-cash carry ARITHMETICALLY on top of the carry-0% NAV paths, i.e. WITHOUT letting it
re-route the simulator's trades. That is exactly what makes it the right cross-check here: the
engine-rerun legs mix TWO effects (the carry itself + a different discrete trade path), and only this
overlay isolates the first. PREREG §3 point (2) is still the reason it is not the number of record —
overlay does not feed carry into sizing, which structurally understates the no-park leg D.

Carry-0% paths used (both are REAL pinned legs, not reconstructions):
  w2d_off  = park 0.0, carry 0%   -> the D vehicle
  w2ctrl2  = park 0.3, carry 0%   -> the A vehicle, AND the control leg whose ledger md5 is 4707bcbe

Per session d:  nav_ov(d) = nav_ov(d-1) * (1 + r_eng(d)) + idle_cash(d-1) * rate(d)/252
  r_eng(d)   = combined_nav log/simple return of the carry-0% engine path
  idle_cash  = bal_cash_ref + lag_cash_ref  (the SAME quantity simulate() credits: cash>0 only,
               parked money already sits in bal_etf_ref/lag_etf_ref)
  rate(d)    = idle_rate_proxy.r_idle(d, tier), /252 per session, 0 before the series starts
               -- identical convention to the engine knob (PREREG §3).
The credit is scaled by nav_ov/nav_eng so the overlay compounds on its own equity, not the engine's.
"""
import json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-w2q2-2709/WorkingClaude")
import idle_rate_proxy as irp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paired_w2 import leg_path, metrics, boot, L, B, SEED   # same bootstrap engine, not a re-derivation

def load_daily(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["t"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["t", "combined_nav"]).sort_values("t")
    g = d.groupby(d["t"].dt.normalize()).last()
    idle = g["bal_cash_ref"].astype(float) + g["lag_cash_ref"].astype(float)
    return g["combined_nav"].astype(float), idle

def rate_series(dates, tier):
    out, nostart = [], 0
    for d in dates:
        try:
            out.append(irp.r_idle(d, tier=tier) / 100.0)
        except ValueError:
            out.append(0.0); nostart += 1
    return np.array(out), nostart

def overlay(nav, idle, tier):
    """Return the overlaid NAV series. Day 0 unchanged; credit uses PREVIOUS session's idle cash."""
    rate, nostart = rate_series(nav.index, tier)
    nav_v, idle_v = nav.values, idle.values
    ov = np.empty_like(nav_v); ov[0] = nav_v[0]
    for i in range(1, len(nav_v)):
        r_eng = nav_v[i] / nav_v[i-1] - 1.0
        credit = max(idle_v[i-1], 0.0) * rate[i] / 252.0 * (ov[i-1] / nav_v[i-1])
        ov[i] = ov[i-1] * (1.0 + r_eng) + credit
    return pd.Series(ov, index=nav.index), nostart, rate

def hdr(s, nav):
    r = np.diff(np.log(nav.values))
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    ann = len(r) / yrs
    c, sh, dd, k = metrics(r[:, None], ann)
    return {"cagr_pct": round(float(c[0])*100, 3), "sharpe": round(float(sh[0]), 3),
            "maxdd_pct": round(float(dd[0])*100, 2), "calmar": round(float(k[0]), 4)}

if __name__ == "__main__":
    legs = {"D": leg_path("w2d_off"), "A": leg_path("w2ctrl2")}
    nav0, idle0 = {}, {}
    for nm, p in legs.items():
        nav0[nm], idle0[nm] = load_daily(p)
    ix = nav0["D"].index
    assert nav0["A"].index.equals(ix), "date index differs between the two carry-0% legs"
    res = {"_legs": legs, "_n_daily": int(len(ix)),
           "_window": [str(ix[0].date()), str(ix[-1].date())]}
    # mean idle-cash fraction of NAV, per leg -- the lever the overlay acts through
    for nm in legs:
        res[f"idle_frac_mean_{nm}"] = round(float((idle0[nm] / nav0[nm]).mean()), 4)
    series = {}
    for nm in legs:
        res[f"{nm}_carry0"] = hdr(nm, nav0[nm]); series[f"{nm}_carry0"] = nav0[nm]
    for tier in ("baseline", "floor"):
        for nm in legs:
            ov, nostart, rate = overlay(nav0[nm], idle0[nm], tier)
            res[f"{nm}_ov_{tier}"] = hdr(nm, ov)
            res[f"{nm}_ov_{tier}"]["pre_series_zero_sessions"] = int(nostart)
            res[f"{nm}_ov_{tier}"]["rate_mean_pct"] = round(float(rate.mean())*100, 3)
            # direct carry contribution in pp of CAGR
            res[f"{nm}_ov_{tier}"]["delta_cagr_pp"] = round(
                res[f"{nm}_ov_{tier}"]["cagr_pct"] - res[f"{nm}_carry0"]["cagr_pct"], 3)
            series[f"{nm}_ov_{tier}"] = ov
    # PAIRED bootstrap across the 6 overlay/carry0 paths (same block-index world, same seed as W2)
    names = list(series)
    R = np.column_stack([np.diff(np.log(series[nm].values)) for nm in names])
    N = R.shape[0]; YRS = (ix[-1]-ix[0]).days/365.25; ANN = N/YRS
    C, S, D, K = boot(R, ANN, N)
    EK = K.mean(axis=0); D5 = np.percentile(D, 5, axis=0)
    for i, nm in enumerate(names):
        res[nm]["E_calmar"] = round(float(EK[i]), 4)
        res[nm]["dd5th_pct"] = round(float(D5[i])*100, 2)
    # P(A > D) on Calmar, within each tier and at carry 0
    for suf in ("carry0", "ov_baseline", "ov_floor"):
        ja = names.index(f"A_{suf}"); jd = names.index(f"D_{suf}")
        res[f"P_A_gt_D_{suf}"] = round(float((K[:, ja] > K[:, jd]).mean()), 4)
    out = os.path.join(HERE, "w2b_overlay.json")
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res, indent=1))
    print("->", out)
