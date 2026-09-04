# -*- coding: utf-8 -*-
"""
DT5G extended-to-2008 research run. Research-only — writes to local CSV, never touches
production tables/config. Uses get_macro_state() UNCHANGED (no param retune) with
start='2008-01-01'.
"""
import os, sys
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
import pandas as pd
from macro_state_live import get_macro_state
from simulate_holistic_nav import bq

END = "2026-09-03"  # last common trading day across sources, avoid partial-day noise

m = get_macro_state("2008-01-01", END, bq=bq)
m.to_csv("mike/agents/Taylor/research/dt5g_ext_2008_20260904/dt5g_ext_2008_full.csv", index=False)
print(f"rows={len(m)}  range={m['time'].min().date()}..{m['time'].max().date()}")
print(m.head(3).to_string())
print(m.tail(3).to_string())
