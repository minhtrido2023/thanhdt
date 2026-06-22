#!/usr/bin/env python3
"""probe_regime_momentum.py — (c) diagnostic BEFORE building a regime-aware selector.
Tests the user's hypothesis ('crazy market behaves differently'): does MOMENTUM's forward-return IC
rise in BULL/EXBULL while VALUE (1/PE) IC is strongest in NEUTRAL? If yes, a DT5G-conditioned
selector (value when cautious, +momentum when bull) is justified -> backtest it. If not, drop it.

DT5G state encoding (verified from tav2_bq.vnindex_5state_dt5g_live): 1=CRISIS 2=BEAR 3=NEUTRAL
4=BULL 5=EXBULL. Buckets: DOWN(1,2), NEUTRAL(3), BULL(4,5).
Inputs: ic_panel_8l.load() (value+fwd) + mom200 per ticker-quarter from BQ + DT5G state asof obs.
Usage: source ./wc_env.sh && $DNA_PYEXE probe_regime_momentum.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import load, bq, ic_series, summ

TGT = "profit_2M"
REGIME = {1: "DOWN", 2: "DOWN", 3: "NEUTRAL", 4: "BULL", 5: "BULL"}

def main():
    d = load()
    # momentum lens: prior-quarter avg Close/MA200-1 (same construction as custom_basket._mom_piv)
    mom = bq("""SELECT t.ticker, DATE_TRUNC(t.time, QUARTER) AS q, AVG(SAFE_DIVIDE(t.Close,NULLIF(t.MA200,0))-1) AS mom
FROM tav2_bq.ticker t WHERE t.MA200>0 AND t.time BETWEEN DATE '2013-06-01' AND DATE '2026-06-19'
GROUP BY t.ticker, q""")
    mom["q"] = pd.to_datetime(mom["q"]).dt.to_period("Q")
    d["qp"] = d["q"]                                  # d['q'] is already Period[Q]
    d = d.merge(mom.rename(columns={"q": "qp"}), on=["ticker", "qp"], how="left")
    # DT5G state as-of each obs date
    st = bq("SELECT time, state FROM tav2_bq.vnindex_5state_dt5g_live ORDER BY time")
    st["time"] = pd.to_datetime(st["time"])
    d = pd.merge_asof(d.sort_values("time"), st.sort_values("time"), on="time", direction="backward")
    d["regime"] = d["state"].map(REGIME)
    print(f"obs by regime: {d.groupby('regime').size().to_dict()}")
    print(f"quarters by regime: { {r: g['q'].nunique() for r,g in d.groupby('regime')} }\n")

    fmt = lambda v: f"{v:+.3f}" if pd.notna(v) else "  -  "
    print(f"forward {TGT} IC by DT5G regime — does momentum overtake value in BULL?\n")
    print(f"{'regime':9} {'nq':>3} {'avgN':>6} | {'IC_ey(value)':>13} {'t':>5} | {'IC_mom':>8} {'t':>5} | {'mom-ey':>7}")
    for rg in ["DOWN", "NEUTRAL", "BULL"]:
        m = d["regime"] == rg
        ey_i, n = ic_series(d, "ey", TGT, m);  se = summ(ey_i)
        mo_i, _ = ic_series(d, "mom", TGT, m); sm = summ(mo_i)
        gap = (sm["ic"] - se["ic"]) if (pd.notna(sm["ic"]) and pd.notna(se["ic"])) else np.nan
        print(f"{rg:9} {se['n']:>3} {n:>6.0f} | {fmt(se['ic']):>13} {se['t']:>5.1f} | "
              f"{fmt(sm['ic']):>8} {sm['t']:>5.1f} | {fmt(gap):>7}")
    print("\nread: if IC_mom > IC_ey in BULL (gap>0) but IC_ey leads in NEUTRAL/DOWN -> regime-aware")
    print("selector justified (value when cautious, +momentum when crazy). Else value-led everywhere.")

if __name__ == "__main__":
    main()
