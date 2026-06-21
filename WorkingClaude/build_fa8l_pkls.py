#!/usr/bin/env python3
"""build_fa8l_pkls.py — build TWO V11 signal pkls over full history, identical except the FA table:
  ba_v11_FAbase_sig.pkl  — SIGNAL_V11 with tav2_bq.fa_ratings        (control, rebuilt same code/window)
  ba_v11_FA8l_sig.pkl    — SIGNAL_V11 with tav2_bq.fa_ratings_8l     (per-group 8L rating mapped A-E)
Isolates the pure FA-rating-replacement effect on the V11 stock book.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11

START="2014-01-01"; END="2026-05-26"
TIER_BAL={'MEGA','MOMENTUM','MOMENTUM_N','MOMENTUM_S','DEEP_VALUE_RECOVERY','RE_BACKLOG_BUY'}

for tag, fa_table in [("FAbase","tav2_bq.fa_ratings"), ("FA8l","tav2_bq.fa_ratings_8l")]:
    sql = SIGNAL_V11.replace("tav2_bq.fa_ratings", fa_table)
    print(f"\n[build {tag}] FA table = {fa_table} ...")
    df = bq(sql.format(start=START, end=END))
    df["time"] = pd.to_datetime(df["time"])
    sub = df[(df["time"]>="2024-01-01")&(df["time"]<="2026-05-15")]
    print(f"  rows={len(df):,}  TIER_BAL(2024+)={int(sub['play_type'].isin(TIER_BAL).sum()):,}  "
          f"AVOID_faE(2024+)={int((sub['play_type']=='AVOID_faE').sum()):,}")
    pth=f"ba_v11_{tag}_sig.pkl"; df.to_pickle(pth)
    print(f"  wrote {pth}  (play_type dist below)")
    print(df["play_type"].value_counts().head(20).to_string())
print("\nDONE.")
