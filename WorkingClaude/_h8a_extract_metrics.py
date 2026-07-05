#!/usr/bin/env python3
"""Wave1/H8a helper — slice Full/IS(2014-19)/OOS(2020+) metrics from a pt_v23 audit CSV's DAILY section.
Replicates pt_v23_audit_2014.calc_metrics byte-faithfully. Read-only; no side effects."""
import sys, numpy as np, pandas as pd

def calc_metrics(s):
    s = s.dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    r = s.pct_change().dropna()
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    sh252 = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    peak = s.cummax(); dds = s / peak - 1
    maxdd = dds.min()
    return dict(years=yrs, cagr=cagr, sharpe_252=sh252,
                max_dd=maxdd, calmar=cagr/abs(maxdd) if maxdd < 0 else 0)

def load_daily(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    d = d.sort_values("ymd").set_index("ymd")
    return pd.to_numeric(d["combined_nav"], errors="coerce").dropna()

def report(path):
    nav = load_daily(path)
    full = calc_metrics(nav)
    is_ = calc_metrics(nav[nav.index <= "2019-12-31"])
    oos = calc_metrics(nav[nav.index >= "2020-01-01"])
    print(f"  file: {path.split('/')[-1]}")
    print(f"  n_daily={len(nav)}  final={nav.iloc[-1]/1e9:.4f}B  span {nav.index[0].date()}->{nav.index[-1].date()}")
    for lbl, m in [("FULL", full), ("IS(<=2019)", is_), ("OOS(>=2020)", oos)]:
        print(f"  {lbl:12s} CAGR {m['cagr']*100:6.2f}%  Sharpe {m['sharpe_252']:.2f}  "
              f"MaxDD {m['max_dd']*100:6.1f}%  Calmar {m['calmar']:.2f}  ({m['years']:.2f}y)")
    return {"FULL": full, "IS": is_, "OOS": oos}

if __name__ == "__main__":
    paths = sys.argv[1:]
    res = {}
    for p in paths:
        print("=" * 78)
        res[p] = report(p)
    if len(paths) == 2:
        base, treat = res[paths[0]], res[paths[1]]
        print("=" * 78)
        print("  DELTA (treatment - baseline), pp for CAGR/DD, abs for Sharpe/Calmar:")
        for k in ["FULL", "IS", "OOS"]:
            b, t = base[k], treat[k]
            print(f"  {k:5s}  dCAGR {(t['cagr']-b['cagr'])*100:+.2f}pp  dSharpe {t['sharpe_252']-b['sharpe_252']:+.3f}  "
                  f"dMaxDD {(t['max_dd']-b['max_dd'])*100:+.2f}pp  dCalmar {t['calmar']-b['calmar']:+.3f}")
