#!/usr/bin/env python
"""Extract CAGR/Sharpe252/MaxDD/Calmar x FULL/IS(<=2019)/OOS(>=2020) from pt_v23 audit CSV daily combined_nav.
Convention = engine metric_formulas (job 130720 table): CAGR calendar-days/365.25, Sharpe_252, MaxDD on daily NAV, Calmar=CAGR/|MaxDD|.
Usage: park20_extract.py <csv> [<csv> ...]
"""
import sys, pandas as pd, numpy as np

def metrics(nav):
    nav = nav.dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = nav.pct_change().dropna()
    sh = r.mean() / r.std() * np.sqrt(252)
    dd = (nav / nav.cummax() - 1).min()
    return dict(cagr=cagr * 100, sharpe=sh, maxdd=dd * 100, calmar=cagr / abs(dd))

for f in sys.argv[1:]:
    df = pd.read_csv(f, low_memory=False)
    d = df[(df.record_type == "DAILY") & df.combined_nav.notna()].copy()
    d["ymd"] = pd.to_datetime(d.ymd)
    nav = d.groupby("ymd").combined_nav.last().astype(float).sort_index()
    sc = df[df.record_type == "METRIC"]
    err = sc[sc.key.astype(str).str.contains("cash_flow_identity", na=False)].value.astype(float).abs().max()
    print(f"== {f.split('/')[-1]}")
    for tag, s in [("FULL", nav), ("IS  ", nav[nav.index <= "2019-12-31"]), ("OOS ", nav[nav.index >= "2020-01-01"])]:
        m = metrics(s)
        print(f"  {tag} CAGR {m['cagr']:6.2f}%  Sharpe {m['sharpe']:.2f}  MaxDD {m['maxdd']:6.1f}%  Calmar {m['calmar']:.2f}")
    print(f"  self-check max cash-flow err = {err:,.6f} VND")
