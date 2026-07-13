# -*- coding: utf-8 -*-
"""
probe_real_premium_20260713.py — DESCRIPTIVE ONLY (no backtest).
Job Taylor_20260713_131230: real deposit premium = Big-4 12M deposit − CPI YoY,
its 6m-change, and episode enumeration vs the borrowed Pillar A thresholds
{+0.5 / +1.5 / +3.0} pp/6m — to update §1 of plan_deposit_rate_signal_20260713.md
BEFORE any backtest runs (pre-registration refinement).

CPI availability: GSO publishes month-M CPI around the 29th of month M → the value
is treated as usable from the 1st of month M+1 (1-month publication shift). This is
a data-alignment choice, not a tuned parameter.
"""
import sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import pandas as pd
from deposit_rate_vn import deposit_events_df
from cpi_vn import cpi_monthly_df

# Monthly grid
idx = pd.date_range("2011-01-01", "2026-07-01", freq="MS")
dep = deposit_events_df().set_index("time")["deposit_rate"].reindex(idx, method="ffill")

cpi_raw = cpi_monthly_df(end="2026-06-01").set_index("time")["cpi_yoy"]
# publication shift: month-M value usable from month M+1
cpi = cpi_raw.copy()
cpi.index = cpi.index + pd.DateOffset(months=1)
cpi = cpi.reindex(idx, method="ffill")

df = pd.DataFrame({"dep": dep, "cpi_avail": cpi})
df["real_prem"] = df["dep"] - df["cpi_avail"]
df["dep_chg6m"] = df["dep"].diff(6)
df["cpi_chg6m"] = df["cpi_avail"].diff(6)
df["real_prem_chg6m"] = df["real_prem"].diff(6)

TH = [("MILD", 0.5), ("STRONG", 1.5), ("EXTREME", 3.0)]

def episodes(s, th):
    on = s >= th
    out, start = [], None
    for t, v in on.items():
        if v and start is None:
            start = t
        elif not v and start is not None:
            seg = s.loc[start:t]
            out.append((start, t - pd.DateOffset(months=1), seg.max()))
            start = None
    if start is not None:
        seg = s.loc[start:]
        out.append((start, s.index[-1], seg.max()))
    return out

print("=== Real premium series (annual snapshot, Jan & Jun) ===")
snap = df.loc[df.index.month.isin([1, 6])]
print(snap.round(2).to_string())

for name, sig in [("NOMINAL dep_chg6m (D1 input)", "dep_chg6m"),
                  ("REAL   real_prem_chg6m (D0 input)", "real_prem_chg6m")]:
    print(f"\n=== Episodes — {name} ===")
    for tname, th in TH:
        eps = episodes(df[sig], th)
        if not eps:
            print(f"  {tname} >= +{th}: (none)")
        for a, b, pk in eps:
            print(f"  {tname} >= +{th}: {a:%Y-%m} -> {b:%Y-%m}  peak {pk:+.2f}")

print("\n=== Key windows detail ===")
for lo, hi in [("2016-07", "2018-06"), ("2022-01", "2023-09"), ("2025-06", "2026-07")]:
    print(f"\n-- {lo}..{hi} --")
    print(df.loc[lo:hi, ["dep", "cpi_avail", "real_prem", "dep_chg6m", "real_prem_chg6m"]]
          .round(2).to_string())
