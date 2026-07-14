# -*- coding: utf-8 -*-
"""reconcile_finweight.py — WHICH definition of "bank weight" is the 24.1% everyone has been citing?

Job Taylor_20260714_140127. Research-only.

basket_picture.py measures the LIVE custom30V (yieldcombo) at mean 47.4% / 2026Q2 82.7% financial.
Today's established premise cites 24.1% full-period / 35.8% OOS / ~50% peak. Both cannot describe
the same quantity. Before ANY verdict cites either number, establish exactly which slice each is:
  - BANK route only, vs BANK+INSURANCE+SECURITIES ("financial", what the v4final cap governs)
  - weight share vs name-count share
  - full period vs OOS-only
A verdict that quietly mixes two definitions is the same class of error (comparing things that are
not the same quantity) this whole day's research chain has been about.
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
from v4final_lib import daily_fin_weights, route_asof  # noqa: E402

OUT = os.path.join(WORKDIR, "mike", "agents", "Taylor", "v4final_exp")
START, END = "2014-01-02", "2026-06-19"
PIT = dict(quality="none", rebal="q2m5", gate_rating=3, top_n=30, name_cap=0.10, qtilt=None)

os.environ["BASKET_SELECT"] = "yieldcombo"
lvl, adv, mem, bx = cb.build_pit(bq, START, END, weight_scheme="namecap", **PIT)

DEFS = {
    "BANK only":                 {"BANK"},
    "BANK+SECURITIES":           {"BANK", "SECURITIES"},
    "BANK+INSURANCE+SECURITIES": {"BANK", "INSURANCE", "SECURITIES"},
}

print("\n" + "=" * 104)
print("LIVE custom30V (yieldcombo/namecap) — financial share under each definition")
print("=" * 104)
rows = []
import v4final_lib as V

for label, routes in DEFS.items():
    V.FIN_ROUTES = routes                      # daily_fin_weights reads the module global
    fw = daily_fin_weights(bx, mem, name_cap=0.10, fin_cap=None)
    fw["time"] = pd.to_datetime(fw["time"])
    oos = fw[fw.time >= "2020-01-01"]
    q = fw.set_index("time").fin_w.groupby(pd.Grouper(freq="QE")).mean()
    rows.append({
        "definition": label,
        "w_full": fw.fin_w.mean(), "w_IS_2014_19": fw[fw.time < "2020-01-01"].fin_w.mean(),
        "w_OOS_2020+": oos.fin_w.mean(), "w_peak_quarter": q.max(),
        "n_names_full": fw.n_fin.mean(), "n_names_OOS": oos.n_fin.mean(),
    })
V.FIN_ROUTES = {"BANK", "INSURANCE", "SECURITIES"}          # restore

R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUT, "finweight_definitions.csv"), index=False)
print(R.round(3).to_string(index=False))

print("""
READ:
  w_*          = share of the daily WEIGHT vector (what risk actually is)
  n_names_*    = mean COUNT of such names in the 30 (what a basket listing shows)
The premise cited today (24.1% full / 35.8% OOS / ~50% peak) matches whichever row reproduces all
three at once. Anything else means the cited number was a different quantity than the cap governs.
""")
