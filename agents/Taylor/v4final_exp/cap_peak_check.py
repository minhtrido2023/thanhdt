# -*- coding: utf-8 -*-
"""cap_peak_check.py — does a cap at level X actually BLOCK the 82.7% financial peak, and on how
many days does it bind at all?

Job Taylor_20260714_152605, Viec 2. Research-only.

The backtest arms answer "what does cap X cost". They do NOT answer "does cap X do the thing it was
proposed to do" — that is a property of the daily WEIGHT VECTOR, not of a CAGR. risk-auditor's
proposal is explicitly about the PEAK (2026Q2 = 82.7% financial by weight), so the peak is what has
to be measured.

One build serves every level: the cap is a WEIGHT rule, not a SELECTION rule — every capped arm holds
the same 30 names as A2 (verified in §12.5, and re-asserted here). So membership is built once from
`eyonly` and each cap is applied to that same daily vector.

Weights come from v4final_lib's independent re-derivation, not custom_basket's internals — measuring
a cap with the code under test would be circular (same reason as §12.6).

Run: $DNA_PYEXE mike/agents/Taylor/v4final_exp/cap_peak_check.py
"""
import os
import sys

import numpy as np
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq  # noqa: E402
import custom_basket as cb  # noqa: E402
from v4final_lib import daily_fin_weights  # noqa: E402

OUT = os.path.join(WORKDIR, "mike", "agents", "Taylor", "v4final_exp")
START, END = "2014-01-02", "2026-06-19"
PIT = dict(quality="none", rebal="q2m5", gate_rating=3, top_n=30, name_cap=0.10, qtilt=None)
LEVELS = [None, 0.30, 0.45, 0.50, 0.55, 0.60]

os.environ["BASKET_SELECT"] = "eyonly"
os.environ.pop("BASKET_DY_TIEBREAK", None)          # Viec 2 is measured on the A2 base, no DY
print("building A2 (eyonly) once — cap is a weight rule, so membership is level-invariant")
lvl, adv, mem, bx = cb.build_pit(bq, START, END, weight_scheme="namecap", **PIT)

rows, byq = [], {}
for X in LEVELS:
    fw = daily_fin_weights(bx, mem, name_cap=0.10, fin_cap=X)
    fw["q"] = pd.to_datetime(fw["time"]).dt.to_period("Q")
    tag = "uncapped" if X is None else f"cap{X:.2f}"
    # "binds" = the UNCAPPED vector would have exceeded X on that day, i.e. the cap actually acted.
    base = daily_fin_weights(bx, mem, name_cap=0.10, fin_cap=None) if X is not None else fw
    binds = (base["fin_w"] > (X + 1e-9)) if X is not None else pd.Series(False, index=fw.index)
    q2 = fw.loc[fw["q"] == pd.Period("2026Q2"), "fin_w"]
    rows.append({
        "level": tag,
        "days": len(fw),
        "fin_w_mean": fw["fin_w"].mean(),
        "fin_w_max": fw["fin_w"].max(),
        "fin_w_p95": fw["fin_w"].quantile(0.95),
        "2026Q2_mean": q2.mean() if len(q2) else np.nan,
        "2026Q2_max": q2.max() if len(q2) else np.nan,
        "pct_days_cap_binds": 100.0 * binds.mean(),
        "wsum_err": abs(fw["wsum"] - 1.0).max(),
    })
    byq[tag] = fw.groupby("q")["fin_w"].mean()
    print(f"  {tag:9s}: mean {rows[-1]['fin_w_mean']:.3f} max {rows[-1]['fin_w_max']:.3f} "
          f"2026Q2 max {rows[-1]['2026Q2_max']:.3f} binds {rows[-1]['pct_days_cap_binds']:5.1f}% of days")

df = pd.DataFrame(rows)
df.to_csv(os.path.join(OUT, "cap_peak_summary.csv"), index=False)
pd.DataFrame(byq).to_csv(os.path.join(OUT, "cap_peak_by_quarter.csv"))

print("\n" + "=" * 78)
print("PEAK CONTROL — what each level does to the episode risk-auditor named (2026Q2 = 82.7%)")
print("=" * 78)
print(df.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

# the honest framing: how much of the SAMPLE does each cap touch, and is the peak the only thing hit?
un = byq["uncapped"]
print(f"\nUncapped financial weight by quarter: min {un.min():.3f} / med {un.median():.3f} / "
      f"max {un.max():.3f} ({un.idxmax()})")
for X in [0.30, 0.45, 0.50, 0.55, 0.60]:
    nq = int((un > X).sum())
    print(f"  cap {X:.2f}: binds in {nq}/{len(un)} quarters ({100 * nq / len(un):.0f}% of the sample)")
print("\nwsum max error (must be ~0):", df["wsum_err"].max())
