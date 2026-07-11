#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""momdeal Phase 0 step 1 — rebuild data/ba_v11_unified_12y_sig.pkl on DT5G state.

Job Taylor_20260711_165407 (plan_momentum_deals_20260711.md §6 CP0).
Old pkl (frozen 2026-06-16) was built pre-F3-fix: its state5/play_type came from
bare tav2_bq.vnindex_5state (v3.4b BASE). This rebuild applies the same one-line
.replace the F3 fix (commit 0537514) applied to pt_v4/pt_v22:
    SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s", STATE_TABLE + " AS s")
and extends END to 2026-07-10 (bq_cache max_time).

Verification after build (dispatch hard requirement):
  pull dt5g_live + base from cache, find dates where they DIFFER, and assert the
  new pkl's state5 equals the DT5G value (ffill as-of) on those dates — direct
  proof the rebuilt pkl is DT5G-sourced, not base.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, shutil
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache")

from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11

PKL   = "data/ba_v11_unified_12y_sig.pkl"
BAK   = PKL + ".bak_predt5g_20260711"
START = "2014-01-01"
END   = "2026-07-10"
STATE_TABLE = "tav2_bq.vnindex_5state_dt5g_live"

# 1. backup old pkl
if os.path.exists(PKL) and not os.path.exists(BAK):
    shutil.copy2(PKL, BAK); print(f"[backup] {PKL} -> {BAK}")
old = pickle.load(open(PKL, "rb")); old["time"] = pd.to_datetime(old["time"])
print(f"[old] rows={len(old):,}  max_date={old['time'].max().date()}  cols={list(old.columns)}")

# 2. rebuild with DT5G state (F3 .replace pattern)
sql = SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s", STATE_TABLE + " AS s")
assert "tav2_bq.vnindex_5state AS s" not in sql and STATE_TABLE in sql, "state-table swap failed"
print(f"\n[build] SIGNAL_V11 {START} -> {END}  state={STATE_TABLE} (cache={os.environ['BQ_LOCAL_CACHE']})")
new = bq(sql.format(start=START, end=END))
new["time"] = pd.to_datetime(new["time"])
print(f"[new] rows={len(new):,}  max_date={new['time'].max().date()}")

# 3. schema check vs old
miss = set(old.columns) - set(new.columns)
print(f"[check] cols in old missing from new: {miss if miss else 'none'}")
if miss:
    print("ABORT: schema mismatch, not overwriting."); sys.exit(1)

# 4. play_type distribution old vs new
print(f"\n[dist] {'play_type':<22} {'old(base,06-16)':>16} {'new(dt5g,07-10)':>16} {'Δ':>9}")
oc, nc = old["play_type"].value_counts(), new["play_type"].value_counts()
for t in sorted(set(oc.index) | set(nc.index)):
    print(f"       {t:<22} {int(oc.get(t,0)):>16,} {int(nc.get(t,0)):>16,} {int(nc.get(t,0))-int(oc.get(t,0)):>+9,}")

# 5. VERIFY state source = DT5G, not base
dt5g = bq(f"SELECT s.time, s.state FROM {STATE_TABLE} AS s ORDER BY s.time")
base = bq("SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s ORDER BY s.time")
dt5g["time"] = pd.to_datetime(dt5g["time"]); base["time"] = pd.to_datetime(base["time"])
cmp_ = dt5g.merge(base, on="time", suffixes=("_dt5g", "_base"))
cmp_ = cmp_[cmp_["time"] >= "2014-01-01"]
diff_days = cmp_[cmp_["state_dt5g"] != cmp_["state_base"]]
print(f"\n[verify] days where dt5g != base (2014+): {len(diff_days):,}")
pkl_state = new[["time", "state5"]].drop_duplicates("time").set_index("time")["state5"]
chk = diff_days[diff_days["time"].isin(pkl_state.index)]
match_dt5g = int((pkl_state.loc[chk["time"]].values == chk["state_dt5g"].values).sum())
match_base = int((pkl_state.loc[chk["time"]].values == chk["state_base"].values).sum())
print(f"[verify] on {len(chk):,} divergent days present in pkl: state5==dt5g {match_dt5g:,} | state5==base {match_base:,}")
if len(chk) == 0 or match_dt5g < len(chk) * 0.99:
    print("ABORT: pkl state5 does NOT track dt5g_live — not overwriting."); sys.exit(1)
# spot: fake-BULL window 2026-06-29..07-09 must be NEUTRAL(3) under dt5g
win = pkl_state.loc[(pkl_state.index >= "2026-06-29") & (pkl_state.index <= "2026-07-09")]
print(f"[verify] fake-BULL window 06-29..07-09 state5 values in pkl: {sorted(win.unique())} (expect [3])")

# 6. overwrite canonical research cache
new = new[list(old.columns)]
new.to_pickle(PKL)
print(f"\n[write] {PKL} rebuilt: {len(new):,} rows, max date {new['time'].max().date()}, state={STATE_TABLE}")
print("DONE.")
