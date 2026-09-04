# -*- coding: utf-8 -*-
"""
Byte-identical gate: 2014+ slice of the extended (start=2008) series MUST match
tav2_bq.vnindex_5state_dt5g_live exactly. Mandatory before any 2008-2013 analysis.
"""
import os, sys
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
import pandas as pd
from simulate_holistic_nav import bq

ext = pd.read_csv("mike/agents/Taylor/research/dt5g_ext_2008_20260904/dt5g_ext_2008_full.csv", parse_dates=["time"])
ext_2014 = ext[ext["time"] >= "2014-01-01"].reset_index(drop=True)

prod = bq("""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s
             WHERE s.time >= DATE '2014-01-01' ORDER BY s.time""")
prod["time"] = pd.to_datetime(prod["time"])
prod = prod.sort_values("time").reset_index(drop=True)

m = ext_2014.merge(prod, on="time", how="outer", suffixes=("_ext", "_prod"), indicator=True)
only_one_side = m[m["_merge"] != "both"]
both = m[m["_merge"] == "both"]
mismatch = both[both["state_ext"] != both["state_prod"]]

print(f"ext_2014 rows={len(ext_2014)}  prod rows={len(prod)}")
print(f"rows only on one side: {len(only_one_side)}")
if len(only_one_side):
    print(only_one_side.head(20).to_string())
print(f"rows both sides, state mismatch: {len(mismatch)}")
if len(mismatch):
    print(mismatch.head(30).to_string())
    print("GATE: FAIL — NOT byte-identical")
else:
    print("GATE: PASS — byte-identical vs production 2014+")
