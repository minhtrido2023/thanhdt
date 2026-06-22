#!/usr/bin/env python3
"""probe_recovery_signal.py — event-study (build step 1) for the valuation-conditioned recovery
re-risk thesis. Tests whether deploying in the low-allocation regime (CRISIS/BEAR) conditioned on
(cheap valuation) and/or (macro rate-easing confirm) beats naive deploy, ACROSS episodes — before
wiring anything into the DT5G allocation curve.

Monthly panel 2009-2026: DT5G state | market cheapness (median pb_z over ticker_prune) | SBV refi |
Big-4 deposit | forward 6M VNINDEX return. Candidate-deploy months = state in {1,2} (CRISIS/BEAR,
where DT5G currently allocates 0-20%). Partition by cheap / rate-easing variants; compare fwd-6M.
Crucial episode checks printed: 2020-03/04 (COVID V), 2022-06 (FALSE bounce), 2022-11 (SCB bottom),
2023-01 (real recovery). Usage: source ./wc_env.sh && $DNA_PYEXE probe_recovery_signal.py
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from ic_panel_8l import bq
from deposit_rate_vn import DEPOSIT_EVENTS
from sbv_macro_overlay import SBV_REFI_EVENTS

def step_series(events, idx):
    """forward-fill a (date,value) step series onto a monthly DatetimeIndex."""
    s = pd.Series({pd.Timestamp(d): v for d, v in events}).sort_index()
    return s.reindex(s.index.union(idx)).ffill().reindex(idx)

def main():
    # (1) DT5G state -> monthly (last obs in month)
    st = bq("SELECT time, state FROM tav2_bq.vnindex_5state_dt5g_live ORDER BY time")
    st["time"] = pd.to_datetime(st["time"]); st = st.set_index("time")
    stm = st["state"].resample("ME").last()
    # (2) market cheapness: monthly median pb_z over liquid ticker_prune (PB vs own 5Y)
    mc = bq("""SELECT FORMAT_DATE('%Y-%m', t.time) ym,
      APPROX_QUANTILES(SAFE_DIVIDE(t.PB - t.PB_MA5Y, NULLIF(t.PB_SD5Y,0)), 2)[OFFSET(1)] AS med_pbz
    FROM tav2_bq.ticker_prune AS t
    WHERE t.PB_SD5Y > 0 AND t.Trading_Value_1M_P50 > 3e9 AND t.time >= DATE '2009-01-01'
    GROUP BY ym ORDER BY ym""")
    mc.index = pd.PeriodIndex(mc["ym"], freq="M").to_timestamp(how="end").normalize()
    medpbz = mc["med_pbz"]
    # (3) VNINDEX monthly close -> forward 6M return
    vni = bq("SELECT t.time, ANY_VALUE(t.VNINDEX) c FROM tav2_bq.ticker AS t WHERE t.VNINDEX IS NOT NULL AND t.time >= DATE '2009-01-01' GROUP BY t.time ORDER BY t.time")
    vni["time"] = pd.to_datetime(vni["time"]); vnim = vni.set_index("time")["c"].resample("ME").last()
    fwd6 = vnim.shift(-6) / vnim - 1.0
    # (4) rate step series onto the monthly index
    idx = stm.index
    refi = step_series(SBV_REFI_EVENTS, idx)
    dep  = step_series(DEPOSIT_EVENTS, idx)
    df = pd.DataFrame({"state": stm, "med_pbz": medpbz.reindex(idx), "refi": refi,
                       "dep": dep, "vni": vnim.reindex(idx), "fwd6": fwd6.reindex(idx)}).dropna(subset=["state"])
    # signals
    df["cheap"] = df["med_pbz"] <= -0.3                              # market cheap vs own 5Y history
    df["refi_not_rising"] = df["refi"] <= df["refi"].shift(3)        # policy rate flat/falling 3m
    df["dep_rollover"]    = df["dep"]  <  df["dep"].shift(3)         # deposit rate rolling DOWN off peak
    df["low_regime"] = df["state"].isin([1, 2])                     # CRISIS/BEAR = deploy-candidate zone

    cand = df[df["low_regime"] & df["fwd6"].notna()]
    def stat(m, lbl):
        s = cand[m]["fwd6"]
        return f"{lbl:38} n={len(s):3d}  fwd6M mean {s.mean()*100:+6.1f}%  med {s.median()*100:+6.1f}%  win {(s>0).mean()*100:3.0f}%"
    print(f"FORWARD-6M VNINDEX after deploying in CRISIS/BEAR months (2009-2026), by gate:\n")
    print(stat(cand.index == cand.index, "ALL low-regime (naive deploy)"))
    print(stat(cand["cheap"], "+ cheap (med pb_z<=-0.3)"))
    print(stat(cand["refi_not_rising"], "+ refi not rising (3m)"))
    print(stat(cand["dep_rollover"], "+ deposit rolling over (3m)"))
    print(stat(cand["cheap"] & cand["refi_not_rising"], "+ cheap & refi-not-rising"))
    print(stat(cand["cheap"] & cand["dep_rollover"], "+ cheap & deposit-rollover"))
    print(stat(cand["cheap"] & (cand["refi_not_rising"] | cand["dep_rollover"]), "+ cheap & (refi-flat OR dep-rollover)"))

    print("\nEPISODE CHECK (does each gate FIRE that month? want NO at 2022-06, YES at 2020-04 / 2023-01):")
    keys = ["2020-03","2020-04","2022-06","2022-09","2022-11","2023-01","2023-02"]
    print(f"{'month':8} {'state':5} {'med_pbz':>8} {'refi':>5} {'dep':>5} | {'cheap':>5} {'refi_flat':>9} {'dep_roll':>8} | {'fwd6M':>7}")
    for k in keys:
        ts = pd.Period(k, freq="M").to_timestamp(how="end").normalize()
        if ts not in df.index: continue
        r = df.loc[ts]
        f6 = f"{r.fwd6*100:+.0f}%" if pd.notna(r.fwd6) else "  -  "
        print(f"{k:8} {int(r.state):5d} {r.med_pbz:>8.2f} {r.refi:>5.1f} {r.dep:>5.1f} | "
              f"{str(bool(r.cheap)):>5} {str(bool(r.refi_not_rising)):>9} {str(bool(r.dep_rollover)):>8} | {f6:>7}")

if __name__ == "__main__":
    main()
