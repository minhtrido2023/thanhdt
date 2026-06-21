#!/usr/bin/env python3
"""build_pkl_v11_current.py — rebuild ba_v11_unified_12y_sig.pkl from SIGNAL_V11 with the
CURRENT vnindex_5state, fixing the stale-state5 artifact (memory: v5-prodspec-integrity-audit).
Backs up the old pkl first. Verifies AVOID_bear 2024+ drops to live levels.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11

PKL="data/ba_v11_unified_12y_sig.pkl"; START="2014-01-01"; END="2026-05-26"
TIER_BAL={'MEGA','MOMENTUM','MOMENTUM_N','MOMENTUM_S','DEEP_VALUE_RECOVERY','RE_BACKLOG_BUY'}

# 1. backup
bak=PKL+".bak_stale_20260520"
if os.path.exists(PKL) and not os.path.exists(bak):
    shutil.copy2(PKL,bak); print(f"[backup] {PKL} -> {bak}")
old=pickle.load(open(PKL,"rb")); old["time"]=pd.to_datetime(old["time"])
old24=old[(old["time"]>="2024-01-01")&(old["time"]<="2026-05-15")]
print(f"[old] rows={len(old):,}  cols={list(old.columns)}")
print(f"[old] 2024+ AVOID_bear={int((old24['play_type']=='AVOID_bear').sum()):,}  TIER_BAL={int(old24['play_type'].isin(TIER_BAL).sum()):,}")

# 2. rebuild from SIGNAL_V11 (current vnindex_5state via the s5_ff join)
print(f"\n[build] running SIGNAL_V11 {START} -> {END} (current state)...")
new=bq(SIGNAL_V11.format(start=START,end=END))
new["time"]=pd.to_datetime(new["time"])
print(f"[new] rows={len(new):,}  cols={list(new.columns)}")
new24=new[(new["time"]>="2024-01-01")&(new["time"]<="2026-05-15")]
print(f"[new] 2024+ AVOID_bear={int((new24['play_type']=='AVOID_bear').sum()):,}  TIER_BAL={int(new24['play_type'].isin(TIER_BAL).sum()):,}")

# 3. sanity: column match
miss=set(old.columns)-set(new.columns)
print(f"\n[check] columns in old missing from new: {miss if miss else 'none'}")
if miss:
    print("  ABORT: schema mismatch, not overwriting."); sys.exit(1)

# 4. overwrite
new=new[list(old.columns)]  # preserve column order
new.to_pickle(PKL)
print(f"[write] {PKL} rebuilt: {len(new):,} rows, max date {new['time'].max().date()}")
print("DONE.")
