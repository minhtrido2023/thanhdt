#!/usr/bin/env python3
"""Wave1/H3 analysis — VOL-MANAGED BAL overlay vs baseline R3.

Reads the DAILY combined_nav series from each audit CSV (baseline + overlay variants),
computes FULL / IS(2014-2019) / OOS(2020+) metrics + turnover, and prints a PASS/FAIL table.

RESEARCH ONLY. Does NOT touch production. Reads frozen audit CSVs written by
pt_v23_audit_2014.py (contemporaneous runs on the same pinned AUDIT_END + same cache).

PASS (per the H3 spec) requires ALL of:
  - OOS Sharpe up AND OOS Calmar up vs baseline
  - MaxDD (FULL) not deeper than baseline
  - CAGR give-up (FULL) <= 0.5pp
  - IS not meaningfully negative (IS CAGR delta > -0.5pp treated as "not negative appreciably")
  - self-check 0 VND (checked separately from METRIC rows in the CSV)
  - turnover-cost-adjusted still PASS (cost already baked into NAV; we also report a 4x-TC stress)
"""
import sys, os
import numpy as np
import pandas as pd

IS_END = pd.Timestamp("2019-12-31")


def load_daily(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    s = pd.Series(d["combined_nav"].astype(float).values, index=d["ymd"].values).sort_index()
    return s


def load_metrics(path):
    df = pd.read_csv(path, low_memory=False)
    m = df[df["record_type"] == "METRIC"][["key", "value"]].copy()
    return dict(zip(m["key"], pd.to_numeric(m["value"], errors="coerce")))


def calc(s):
    s = s.dropna()
    if len(s) < 3:
        return None
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    r = s.pct_change().dropna()
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0.0
    peak = s.cummax(); dd = (s / peak - 1).min()
    calmar = cagr / abs(dd) if dd < 0 else 0.0
    return dict(cagr=cagr, sharpe=sh, maxdd=dd, calmar=calmar, yrs=yrs)


def windows(s):
    return {"FULL": calc(s),
            "IS": calc(s[s.index <= IS_END]),
            "OOS": calc(s[s.index > IS_END])}


def fmt(m):
    if m is None:
        return "   n/a"
    return f"CAGR {m['cagr']*100:6.2f}%  Sh {m['sharpe']:4.2f}  DD {m['maxdd']*100:6.1f}%  Cal {m['calmar']:4.2f}"


def main():
    base_path = sys.argv[1]
    variant_paths = sys.argv[2:]
    base = windows(load_daily(base_path))
    base_m = load_metrics(base_path)
    print("=" * 92)
    print(f"BASELINE R3  {os.path.basename(base_path)}")
    for w in ("FULL", "IS", "OOS"):
        print(f"  {w:4s}  {fmt(base[w])}")
    # self-check from METRIC rows
    sc_keys = [k for k in base_m if "err_vnd" in k or "borrow_cost" in k]
    sc_max = max((abs(base_m[k]) for k in sc_keys if pd.notna(base_m[k])), default=0.0)
    print(f"  self-check max |err/borrow| = {sc_max:,.0f} VND")
    print("=" * 92)

    for vp in variant_paths:
        if not os.path.exists(vp):
            print(f"\n[MISSING] {vp}")
            continue
        v = windows(load_daily(vp))
        vm = load_metrics(vp)
        print(f"\nVARIANT  {os.path.basename(vp)}")
        for w in ("FULL", "IS", "OOS"):
            print(f"  {w:4s}  {fmt(v[w])}")
        # deltas
        dF = v["FULL"]; bF = base["FULL"]; dO = v["OOS"]; bO = base["OOS"]; dI = v["IS"]; bI = base["IS"]
        d_cagr_full = (dF["cagr"] - bF["cagr"]) * 100
        d_dd_full = (dF["maxdd"] - bF["maxdd"]) * 100   # >0 means shallower (better)
        d_sh_oos = dO["sharpe"] - bO["sharpe"]
        d_cal_oos = dO["calmar"] - bO["calmar"]
        d_cagr_is = (dI["cagr"] - bI["cagr"]) * 100
        # turnover
        n_vr = vm.get("volmanage_n_volrebal", np.nan)
        turn = vm.get("volmanage_vol_turnover_vnd", np.nan)
        cost = vm.get("volmanage_vol_cost_vnd", np.nan)
        mean_m = vm.get("volmanage_mean_m", np.nan)
        scaled = vm.get("volmanage_scaled_days", np.nan)
        sig_t = vm.get("volmanage_sigma_target_ann", np.nan)
        # self-check
        sc_keys_v = [k for k in vm if "err_vnd" in k or "borrow_cost" in k]
        sc_max_v = max((abs(vm[k]) for k in sc_keys_v if pd.notna(vm[k])), default=0.0)
        # 4x-TC stress: extra drag if TC were 0.3% instead of 0.075% (linear in turnover)
        tc = vm.get("volmanage_tc", 0.00075)
        extra_cost_4x = turn * (0.003 - tc) if pd.notna(turn) else np.nan
        init_nav = vm.get("init_nav_vnd", 50e9)
        # approx pp/yr drag of the extra cost over the full horizon
        yrs = dF["yrs"]
        extra_drag_pp = (extra_cost_4x / init_nav / yrs) * 100 if pd.notna(extra_cost_4x) else np.nan

        print(f"  overlay: sigma_target(ann)={sig_t*100:.1f}%  mean_m={mean_m:.3f}  "
              f"scaled_days={scaled:.0f}  n_volrebal={n_vr:.0f}")
        print(f"  turnover={turn/1e9:.2f}B  TC_drag(@0.075%)={cost/1e6:.1f}M VND  "
              f"self-check max|err|={sc_max_v:,.0f} VND")
        print(f"  DELTAS vs baseline:")
        print(f"    FULL: CAGR {d_cagr_full:+.2f}pp   MaxDD {d_dd_full:+.2f}pp (>0=shallower/better)")
        print(f"    OOS : Sharpe {d_sh_oos:+.3f}   Calmar {d_cal_oos:+.3f}")
        print(f"    IS  : CAGR {d_cagr_is:+.2f}pp")
        print(f"    4x-TC stress (0.3%/side): extra {extra_cost_4x/1e6:.1f}M VND ~= {extra_drag_pp:+.3f}pp/yr drag")
        # PASS gates
        gates = {
            "OOS Sharpe up": d_sh_oos > 0,
            "OOS Calmar up": d_cal_oos > 0,
            "MaxDD not deeper (FULL)": d_dd_full >= -1e-9,
            "CAGR give-up <=0.5pp (FULL)": d_cagr_full >= -0.5,
            "IS not appreciably negative": d_cagr_is >= -0.5,
            "self-check ~0 VND": sc_max_v < 1e6,
        }
        verdict = "PASS" if all(gates.values()) else "FAIL"
        print(f"  GATES: " + " | ".join(f"{k}:{'Y' if v else 'N'}" for k, v in gates.items()))
        print(f"  ==> {verdict}")


if __name__ == "__main__":
    main()
