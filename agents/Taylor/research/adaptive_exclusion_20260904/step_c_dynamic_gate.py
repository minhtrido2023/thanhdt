import os, sys, numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
sys.path.insert(0, os.path.join(WORKDIR, "mike/agents/Taylor/research/adaptive_exclusion_20260904"))
from simulate_holistic_nav import bq
import custom_basket_dynfork as cbd

START, END = "2014-01-01", "2026-06-15"
CACHE = os.path.join(WORKDIR, "mike/agents/Taylor/research/adaptive_exclusion_20260904/cache")
DYN_CSV = os.path.join(WORKDIR, "mike/agents/Taylor/research/adaptive_exclusion_20260904/dynamic_exclude_events.csv")

navp = os.path.join(CACHE, "nav_dynamic_gate.csv"); memp = os.path.join(CACHE, "mem_dynamic_gate.csv")
if os.path.exists(navp) and os.path.exists(memp):
    print("[load cached] dynamic_gate")
else:
    os.environ["BASKET_SELECT"] = "yieldcombo"
    os.environ["BASKET_EXCLUDE"] = ""
    os.environ["BASKET_DYNAMIC_GATE_CSV"] = DYN_CSV
    print("[build] dynamic_gate (no static BANNED, PIT leverage/equity/dilution gate)")
    lvl, adv, memdf, bx = cbd.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                        gate_rating=3, weight_scheme="namecap")
    s = pd.Series(lvl); s.index = pd.to_datetime(s.index)
    s.sort_index().rename("nav").rename_axis("date").to_csv(navp)
    memdf.to_csv(memp, index=False)
    print("[done build]")
