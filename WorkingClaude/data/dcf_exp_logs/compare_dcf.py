# -*- coding: utf-8 -*-
"""compare_dcf.py — Pha-3 DCF selector comparison table (job Taylor_20260714_070221).

Recomputes CAGR/Sharpe/MaxDD/Calmar for IS(2014-19)/OOS(2020+)/FULL independently from each run's
daily `combined_nav` CSV (the §8 "recompute from CSV, don't trust the print" step).

Run: $DNA_PYEXE data/dcf_exp_logs/compare_dcf.py
"""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
BASE = f"{WORKDIR}/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap"
RUNS = [("baseline (ctrl)", f"{BASE}_exp_dcfctrl20260714.csv"),
        ("A exclude_rich",  f"{BASE}_exp_dcfexrich.csv"),
        ("B tiebreak W.25", f"{BASE}_exp_dcftb025.csv")]
WINDOWS = [("IS 2014-19", "2014-01-01", "2019-12-31"),
           ("OOS 2020+",  "2020-01-01", "2099-12-31"),
           ("FULL",       "2014-01-01", "2099-12-31")]


def nav_series(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)


def metrics(s):
    s = s.dropna()
    if len(s) < 20:
        return dict(cagr=np.nan, sharpe=np.nan, mdd=np.nan, calmar=np.nan)
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = ((s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1) * 100
    r = np.log(s / s.shift(1)).dropna()
    spy = len(r) / yrs                       # actual sessions/yr (registry convention, not 252)
    sharpe = (r.mean() / r.std(ddof=1)) * np.sqrt(spy) if r.std(ddof=1) > 0 else np.nan
    mdd = ((s / s.cummax()) - 1).min() * 100
    calmar = cagr / abs(mdd) if mdd < 0 else np.nan
    return dict(cagr=cagr, sharpe=sharpe, mdd=mdd, calmar=calmar)


def main():
    navs = {}
    for label, path in RUNS:
        try:
            navs[label] = nav_series(path)
        except FileNotFoundError:
            print(f"MISSING: {path}")
    if not navs:
        sys.exit("no CSVs")

    base_label = RUNS[0][0]
    for wname, w0, w1 in WINDOWS:
        print(f"\n=== {wname} " + "=" * 62)
        print(f"{'config':<18} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>9} {'Calmar':>8}   vs baseline")
        base_m = None
        for label, _ in RUNS:
            if label not in navs: continue
            s = navs[label]
            m = metrics(s[(s.index >= w0) & (s.index <= w1)])
            if base_m is None:
                base_m = m; delta = ""
            else:
                delta = (f"ΔCAGR {m['cagr']-base_m['cagr']:+.2f}pp  "
                         f"ΔSharpe {m['sharpe']-base_m['sharpe']:+.3f}  "
                         f"ΔCalmar {m['calmar']-base_m['calmar']:+.3f}")
            print(f"{label:<18} {m['cagr']:>8.2f} {m['sharpe']:>8.2f} {m['mdd']:>9.1f} "
                  f"{m['calmar']:>8.2f}   {delta}")

    # pre-registered gate: must beat baseline on Sharpe AND Calmar in BOTH IS and OOS
    print("\n=== PRE-REGISTERED GATE (Sharpe AND Calmar > baseline in BOTH IS and OOS) " + "=" * 5)
    for label, _ in RUNS[1:]:
        if label not in navs: continue
        verdict = []
        for wname, w0, w1 in WINDOWS[:2]:
            b = metrics(navs[base_label][(navs[base_label].index >= w0) & (navs[base_label].index <= w1)])
            m = metrics(navs[label][(navs[label].index >= w0) & (navs[label].index <= w1)])
            ok = (m["sharpe"] > b["sharpe"]) and (m["calmar"] > b["calmar"])
            verdict.append(ok)
            print(f"  {label:<18} {wname:<11} Sharpe {m['sharpe']:.2f} vs {b['sharpe']:.2f} | "
                  f"Calmar {m['calmar']:.2f} vs {b['calmar']:.2f} -> {'PASS' if ok else 'FAIL'}")
        print(f"  ==> {label}: {'GO (both windows)' if all(verdict) else 'NO-GO'}\n")

    # per-year, for the LOO read
    print("=== per-year total return (%) " + "=" * 45)
    yrs = sorted({y for s in navs.values() for y in s.index.year})
    print(f"{'year':<6}" + "".join(f"{l:>19}" for l in navs))
    for y in yrs:
        row = f"{y:<6}"
        for label in navs:
            s = navs[label]; ny = s[s.index.year == y]
            row += f"{((ny.iloc[-1]/ny.iloc[0]-1)*100 if len(ny) > 4 else float('nan')):>19.1f}"
        print(row)


if __name__ == "__main__":
    main()
