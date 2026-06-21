# -*- coding: utf-8 -*-
"""
deposit_rate_vn.py — Big-4 (VCB/BIDV/CTG/Agribank) 12-month term-deposit rate, monthly.
Used as the ABSOLUTE Fed-model hurdle for the 8L valuation v3 deposit lens (state-conditional;
applied only in NEUTRAL/BEAR/CRISIS — see plan). NOT a cross-sectional valuation factor.

Source / calibration (2026-06-19):
  - Cyclical SHAPE from Trading Economics avg *lending* rate 1999-2023 (user-provided chart):
    2008~15.8, 2011~17(peak), 2013~10.4, 2014~8.7, 2015-17~7, 2018-22~7.4-7.9, 2023~9.2.
  - LEVELS pinned to known Big-4 12M *deposit* web anchors (the lending-deposit spread for Big-4
    is ~2%, narrower than the 3-3.5% SME rule, and widens in tight years):
      2026-06 BIDV 12M 6.8% (raised +1.2%); 2024 ~4.7; 2023 7.4(Q1)->5.0(Q4); 2022-12 ~7.5;
      2021/2022H1 ~5.5; 2020 6.0->5.7 (COVID cuts); 2015-17 ~5.5-6.5; 2014 ~7.0.
  - Pre-2014 (out of the value panel, kept for context): 2011 SBV cap ~14%; 2012 12->9; 2013 8->7.
⚠️ PROXY — levels are best-estimate (esp. 2022-H2 spike). Refine if a clean Big-4 series surfaces.
"""
import numpy as np, pandas as pd

# (effective_date, big4_12m_deposit_pct_pa) — step series, forward-filled between anchors
DEPOSIT_EVENTS = [
    ("2011-01-01", 14.0),   # SBV cap era (pre-panel, context only)
    ("2012-04-01", 12.0),
    ("2012-10-01",  9.0),
    ("2013-06-01",  7.5),
    ("2014-01-01",  7.0),
    ("2014-07-01",  6.3),
    ("2015-01-01",  5.5),
    ("2016-01-01",  5.5),
    ("2017-01-01",  6.5),
    ("2018-01-01",  6.8),
    ("2019-01-01",  7.0),
    ("2020-01-01",  6.5),
    ("2020-07-01",  5.7),   # COVID easing
    ("2021-01-01",  5.5),
    ("2022-01-01",  5.5),
    ("2022-10-01",  6.8),   # SBV hikes (Oct-2022)
    ("2022-12-01",  7.5),   # late-2022 peak
    ("2023-03-01",  7.2),
    ("2023-06-01",  6.3),
    ("2023-09-01",  5.5),
    ("2023-12-01",  5.0),
    ("2024-04-01",  4.7),   # trough
    ("2025-01-01",  4.8),
    ("2025-09-01",  5.2),   # gentle re-rise
    ("2026-01-01",  6.0),
    ("2026-06-01",  6.8),   # BIDV current (web, +1.2%)
]


def deposit_events_df():
    ev = pd.DataFrame(DEPOSIT_EVENTS, columns=["time", "deposit_rate"])
    ev["time"] = pd.to_datetime(ev["time"])
    return ev.sort_values("time").reset_index(drop=True)


def merge_deposit(df, time_col="time"):
    """as-of (backward) merge the deposit_rate onto a frame with a datetime `time_col`."""
    ev = deposit_events_df()
    d = df.sort_values(time_col).copy()
    d[time_col] = pd.to_datetime(d[time_col])
    return pd.merge_asof(d, ev, left_on=time_col, right_on="time",
                         direction="backward", suffixes=("", "_dep"))


def current_deposit_rate(asof=None):
    ev = deposit_events_df()
    if asof is None:
        return float(ev.deposit_rate.iloc[-1])
    asof = pd.to_datetime(asof)
    return float(ev[ev.time <= asof].deposit_rate.iloc[-1])


if __name__ == "__main__":
    ev = deposit_events_df()
    # annual view for eyeballing
    idx = pd.date_range("2014-01-01", "2026-06-01", freq="MS")
    s = pd.merge_asof(pd.DataFrame({"time": idx}), ev, on="time", direction="backward")
    ann = s.groupby(s.time.dt.year).deposit_rate.mean().round(2)
    print("Big-4 12M deposit proxy (annual mean, %):")
    for y, v in ann.items():
        print(f"  {y}: {v:.2f}")
    print(f"\ncurrent (2026-06) = {current_deposit_rate():.2f}%")
