# -*- coding: utf-8 -*-
"""grid_park.py (job Taylor_20260930_122400) — Việc 2: park-fraction grid, 2 đích giải ngân
(custom30V-only vs DC-waterfall) x 4 mức park {0.0,0.3,0.5,0.7} = 8 trials, FULL window.
r_base + w_park(t-1) each pulled from the AUDIT RUN AT THAT PARK LEVEL (own w_park), matching
dc_waterfall_deepdive_regen.py's overlay() formula exactly. Read-only research script.
"""
import os, sys
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

AUDITS = {
    0.0: "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-0_advprice_exp_dcwf_grid_00_20260930_univpit.csv",
    0.3: "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-30_advprice_exp_dcwf_r3_20260930_univpit.csv",
    0.5: "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-50_advprice_exp_dcwf_grid_05_20260930_univpit.csv",
    0.7: "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_advprice_exp_dcwf_grid_07_20260930_univpit.csv",
}
SLEEVE = "data/converge_portfolio_backtest_nav_dcwf_r3_20260930.csv"
NAV_TOTAL_B = 50.0


def load_audit(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    for c in ["state", "bal_etf_ref", "lag_etf_ref", "combined_nav"]:
        d[c] = pd.to_numeric(d[c])
    d = d.set_index("ymd").sort_index()
    met = df[df["record_type"] == "METRIC"].set_index("key")["value"]
    return d, met


def metrics(r):
    r = r.dropna()
    nav = (1 + r).cumprod()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1 / yrs) - 1
    sd = r.std()
    sh = r.mean() / sd * np.sqrt(252) if sd > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min()
    cal = cagr / abs(dd) if dd < 0 else np.nan
    return cagr * 100, sh, dd * 100, cal


def overlay(r_base, w_park_prev, delta_vehicle):
    dv = delta_vehicle.reindex(r_base.index).fillna(0.0)
    return r_base + w_park_prev.reindex(r_base.index).fillna(0.0) * dv


slv = pd.read_csv(SLEEVE, parse_dates=["date"]).set_index("date")
r_c30v = slv["baseline_ret"]
r_wf = slv["ConvergePort (equal-weight)"]

hdr = f"{'park lvl':<10}{'target':<20}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}{'w_park mean(NEU)':>18}"
print(hdr)
print("-" * len(hdr))
rows_for_capacity = {}
for p, path in AUDITS.items():
    aud, met = load_audit(path)
    nav = aud["combined_nav"]
    r_base = nav.pct_change().dropna()
    w_park = (aud["bal_etf_ref"] + aud["lag_etf_ref"]) / aud["combined_nav"]
    w_park_prev = w_park.shift(1).reindex(r_base.index).fillna(0.0)
    st = aud["state"]
    w_park_neu_mean = w_park[st == 3].mean() if (st == 3).any() else 0.0

    r_c30v_only = r_base   # target 1: 100% of the parked sleeve stays in custom30V (= audit's own base)
    r_wfall = overlay(r_base, w_park_prev, (r_wf - r_c30v))  # target 2: DC-waterfall substitution

    c1 = metrics(r_c30v_only); c2 = metrics(r_wfall)
    print(f"{p:<10.2f}{'custom30V-only':<20}{c1[0]:>7.2f}%{c1[1]:>8.2f}{c1[2]:>7.1f}%{c1[3]:>8.2f}{w_park_neu_mean*100:>17.1f}%")
    print(f"{p:<10.2f}{'DC-waterfall':<20}{c2[0]:>7.2f}%{c2[1]:>8.2f}{c2[2]:>7.1f}%{c2[3]:>8.2f}{w_park_neu_mean*100:>17.1f}%")
    rows_for_capacity[p] = w_park_neu_mean

print("\n=== Capacity check (DC-waterfall sleeve, capacity ~10-15B per kb/projects/rnd-pipeline-tracker.md) ===")
print("  NOTE: w_park_mean(NEUTRAL) already reflects the park_frac p baked into that audit run's own")
print("  cash_etf_states policy (bal_etf_ref+lag_etf_ref)/combined_nav — do NOT multiply by p again.")
REAL_NAV_B = 1.952  # SpaceX ~987tr + ZaloPay ~965tr VND, 2026-09-30 approx (units: tr VND = 0.001B)
for p, w_neu in rows_for_capacity.items():
    cap_deployed_b = NAV_TOTAL_B * w_neu
    flag = "OVER 10-15B" if cap_deployed_b > 10 else "ok"
    print(f"  park={p:.2f}  NAV_TOTAL={NAV_TOTAL_B:.0f}B x w_park_mean(NEUTRAL)={w_neu*100:.1f}%"
          f"  => deployed into DC-waterfall sleeve ~ {cap_deployed_b:.2f}B  [{flag}]")
    if w_neu > 0:
        nav_at_10b = 10.0 / w_neu
        nav_at_15b = 15.0 / w_neu
        real_deployed = REAL_NAV_B * w_neu
        print(f"           -> hits 10B ceiling at NAV_TOTAL ~ {nav_at_10b:.0f}B, 15B ceiling at ~ {nav_at_15b:.0f}B"
              f"  | at REAL current NAV ({REAL_NAV_B:.2f}B): deployed ~ {real_deployed*1000:.0f}tr VND (negligible)")
