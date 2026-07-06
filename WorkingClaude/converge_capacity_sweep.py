#!/usr/bin/env python3
"""ConvergePort capacity-appropriate-scale sweep (job Taylor_20260706_105156).

Reuses the EXACT capacity/ADV logic from converge_fullharness_test.py (L2298-2318):
  req      = CONV_WPN * NAV               # per-name target position
  adv      = median(Volume_3M_P50*Price)  # over the recent 120-calendar-day window
  cap_day  = 0.20 * adv                    # 20%-of-ADV/day fill rule
  days     = req / cap_day                 # sessions to build one full name
  flag     = OK (<=1) / WATCH (1-3) / BREACH (>3)

Light: pulls only the liqdf (no simulate() engine), sweeps NAV over many levels.
"""
import os
import numpy as np
import pandas as pd

import sector_lens_monitor as slm
from simulate_holistic_nav import bq
from pt_dates import detect_end_date

CONV_WPN   = float(os.environ.get("CONV_WPN", "0.11"))   # per-name fraction of NAV (== fullharness default)
START_DATE = "2014-01-02"
END_DATE   = os.environ.get("AUDIT_END") or detect_end_date()
WL_TK      = [n[0] for n in slm.NAMES]                    # 16-name available universe

print(f"ConvergePort capacity sweep — WPN={CONV_WPN:.3f}, WL={len(WL_TK)} names, "
      f"data snapshot END={END_DATE}")
print("WL:", WL_TK)

# ---- pull liqdf exactly as the fullharness does ----
_liqdf = bq(f"""SELECT t.ticker, t.time, t.Volume_3M_P50, t.Price
FROM tav2_bq.ticker AS t WHERE t.ticker IN ({','.join(f"'{t}'" for t in WL_TK)})
  AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
_liqdf["time"] = pd.to_datetime(_liqdf["time"])
_liqdf["notional"] = _liqdf["Volume_3M_P50"].fillna(0) * _liqdf["Price"].fillna(0)

# ---- recent-120d median ADV per name (identical windowing to fullharness) ----
_ld = _liqdf.copy().sort_values(["ticker", "time"])
_recent = _ld[_ld["time"] >= (_ld["time"].max() - pd.Timedelta(days=120))]
adv_map = {}
for tk in WL_TK:
    g = _recent[_recent["ticker"] == tk]["notional"]
    adv_map[tk] = float(g.median()) if len(g) else 0.0

# analytic breach/watch NAV per name:
#   days>1 (leaves OK) at NAV = 0.2*adv/WPN            (WATCH onset)
#   days>3 (BREACH)   at NAV = 3*0.2*adv/WPN = 0.6*adv/WPN
watch_nav = {tk: (0.20 * adv_map[tk] / CONV_WPN) if adv_map[tk] > 0 else 0.0 for tk in WL_TK}
breach_nav = {tk: (0.60 * adv_map[tk] / CONV_WPN) if adv_map[tk] > 0 else 0.0 for tk in WL_TK}

print("\nPer-name ADV60 (recent-120d median notional) and onset NAV thresholds:")
print(f"  {'ticker':<8}{'ADV60_B':>10}{'20%ADV_B':>10}{'WATCH@NAV_B':>13}{'BREACH@NAV_B':>14}")
for tk in sorted(WL_TK, key=lambda t: adv_map[t]):
    print(f"  {tk:<8}{adv_map[tk]/1e9:>10.3f}{0.2*adv_map[tk]/1e9:>10.3f}"
          f"{watch_nav[tk]/1e9:>13.3f}{breach_nav[tk]/1e9:>14.3f}")

# thinnest name drives the safe ceiling
thin_watch = min(WL_TK, key=lambda t: watch_nav[t] if watch_nav[t] > 0 else float("inf"))
thin_breach = min(WL_TK, key=lambda t: breach_nav[t] if breach_nav[t] > 0 else float("inf"))
print(f"\nThinnest name (first WATCH):  {thin_watch}  -> all-OK ceiling  = {watch_nav[thin_watch]/1e9:.3f}B")
print(f"Thinnest name (first BREACH): {thin_breach} -> no-breach ceiling = {breach_nav[thin_breach]/1e9:.3f}B")

# ---- sweep table ----
SWEEP = [1e9, 3e9, 5e9, 10e9, 15e9, 20e9, 30e9, 50e9]
print("\n" + "=" * 92)
print("NAV SWEEP x CAPACITY  (days_build per name = WPN*NAV / (20%*ADV60))")
print("=" * 92)
order = sorted(WL_TK, key=lambda t: adv_map[t])   # thinnest first
hdr = f"{'ticker':<7}{'ADV60_B':>9}"
for nav in SWEEP:
    hdr += f"{nav/1e9:>7.0f}B"
print(hdr)
for tk in order:
    row = f"{tk:<7}{adv_map[tk]/1e9:>9.3f}"
    for nav in SWEEP:
        req = CONV_WPN * nav
        cap_day = 0.20 * adv_map[tk]
        days = (req / cap_day) if cap_day > 0 else float("inf")
        row += f"{days:>8.2f}"
    print(row)

print("\nFlag summary per NAV (OK<=1 / WATCH 1-3 / BREACH>3):")
for nav in SWEEP:
    req = CONV_WPN * nav
    brs, was = [], []
    for tk in WL_TK:
        cap_day = 0.20 * adv_map[tk]
        days = (req / cap_day) if cap_day > 0 else float("inf")
        if days > 3.0:
            brs.append(tk)
        elif days > 1.0:
            was.append(tk)
    print(f"  NAV={nav/1e9:>4.0f}B  BREACH={brs or 'none'}  WATCH={was or 'none'}")

print("\nDone.")
