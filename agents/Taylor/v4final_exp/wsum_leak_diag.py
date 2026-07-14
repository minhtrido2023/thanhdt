# -*- coding: utf-8 -*-
"""wsum_leak_diag.py — why does the CAPPED weight vector not sum to 1?

Job Taylor_20260714_152605. cap_peak_check.py measured |sum(W)-1| up to 0.0096 on every capped
level while the uncapped path is exact to 1e-16. A weight vector that sums to <1 means the arm
silently parks the remainder in CASH — which would understate every capped arm's return and would
make the cap NO-GO partly an artifact. Before reporting any cap number, find out which days leak and
why.

Run: $DNA_PYEXE mike/agents/Taylor/v4final_exp/wsum_leak_diag.py
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
from v4final_lib import _cap_group_jointly, _cap_names, daily_fin_weights  # noqa: E402

START, END = "2014-01-02", "2026-06-19"
PIT = dict(quality="none", rebal="q2m5", gate_rating=3, top_n=30, name_cap=0.10, qtilt=None)

os.environ["BASKET_SELECT"] = "eyonly"
os.environ.pop("BASKET_DY_TIEBREAK", None)
lvl, adv, mem, bx = cb.build_pit(bq, START, END, weight_scheme="namecap", **PIT)

fw = daily_fin_weights(bx, mem, name_cap=0.10, fin_cap=0.30)
fw["err"] = (fw["wsum"] - 1.0).abs()
bad = fw[fw["err"] > 1e-9].copy()
print(f"days with sum(W) != 1 under cap 0.30: {len(bad)}/{len(fw)}")
if len(bad):
    print(f"  worst err {bad['err'].max():.6f}; date range {bad['time'].min().date()} → "
          f"{bad['time'].max().date()}")
    print(f"  n_active on leaking days: min {bad['n_active'].min()} / max {bad['n_active'].max()}")
    print(f"  n_fin on leaking days:    min {bad['n_fin'].min()} / max {bad['n_fin'].max()}")
    print("\n  sample:")
    print(bad[["time", "fin_w", "wsum", "err", "n_fin", "n_active"]].head(8).to_string(index=False))

# ---- reproduce the leak in isolation on the worst day's shape -------------------------------------
if len(bad):
    w0 = bad.iloc[bad["err"].values.argmax()]
    n_act, n_fin = int(w0["n_active"]), int(w0["n_fin"])
    n_non = n_act - n_fin
    print(f"\nworst day {pd.Timestamp(w0['time']).date()}: n_active={n_act} n_fin={n_fin} "
          f"n_nonfin={n_non}")
    # the mechanism: gcap_eff floors the group budget so the OUT-group can hold 1-b_in at ncap each.
    ncap, gcap = 0.10, 0.30
    gcap_eff = max(gcap, 1.0 - n_non * ncap)
    print(f"  gcap_eff = max({gcap}, 1 - {n_non}*{ncap}) = {gcap_eff:.4f}")
    print(f"  -> IN-group budget b_in <= {gcap_eff:.4f}; OUT-group budget = {1 - gcap_eff:.4f} "
          f"spread over {n_non} names at name_cap {ncap} -> capacity {n_non * ncap:.4f}")
    # feasibility of the IN group at its OWN rescaled name cap:
    print(f"  IN-group capacity check: {n_fin} names x (ncap/b_in = {ncap / gcap_eff:.4f}) "
          f"= {n_fin * ncap / gcap_eff:.4f} (needs >= 1.0)")

# ---- does the leak exist in the PRODUCTION module too, or only in the audit lib? ------------------
# The two implementations are independent by design; a leak in ONE of them is a different (and much
# smaller) problem than a leak in BOTH.
print("\n--- synthetic: IN-group infeasible at its own rescaled cap ---")
for n_fin, n_non in [(18, 12), (20, 10), (25, 5), (28, 2), (30, 0)]:
    w = np.ones(n_fin + n_non) / (n_fin + n_non)
    g = np.array([True] * n_fin + [False] * n_non)
    out, ce = _cap_group_jointly(w, g, 0.30, 0.10)
    flag = "" if abs(out.sum() - 1) < 1e-9 else "   <-- LEAK"
    print(f"  n_fin={n_fin:2d} n_non={n_non:2d}: cap_eff={ce:.3f} sum(W)={out.sum():.6f}"
          f" fin_w={out[g].sum():.4f}{flag}")
