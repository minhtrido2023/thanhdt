# -*- coding: utf-8 -*-
"""F3 experiment (job Taylor_20260711_051033): measure play_type impact of switching
SIGNAL_V11's state5 forward-fill source from base `vnindex_5state` (v3.4b) to
`vnindex_5state_dt5g_live` (DT5G production), same swap golive_recommend_v23.py:77 does.
Read-only vs production; writes only under data/f3_exp/."""
import os, sys
os.environ.setdefault("BQ_LOCAL_CACHE", "data/bq_cache")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")
import pandas as pd
from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11

START, END = "2014-01-01", "2026-07-10"
BUY_TIERS = {"MEGA","S_PRO","MOMENTUM","MOMENTUM_QUALITY","MOMENTUM_N",
             "COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","MOMENTUM_S","MOMENTUM_A","MOMENTUM_S_N"}

sql_base = SIGNAL_V11.format(start=START, end=END)
sql_live = SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s",
                              "tav2_bq.vnindex_5state_dt5g_live AS s").format(start=START, end=END)
print("[1] run SIGNAL_V11 (base)...", flush=True)
a = bq(sql_base)[["ticker","time","play_type","ta","state5"]]
print(f"    rows={len(a):,}", flush=True)
print("[2] run SIGNAL_V11 (dt5g_live)...", flush=True)
b = bq(sql_live)[["ticker","time","play_type","state5"]]
print(f"    rows={len(b):,}", flush=True)

m = a.merge(b, on=["ticker","time"], suffixes=("_base","_live"), how="outer", indicator=True)
print("merge:", m["_merge"].value_counts().to_dict())
m = m[m["_merge"]=="both"]
m["time"] = pd.to_datetime(m["time"])

flip = m[m["play_type_base"] != m["play_type_live"]]
n = len(m)
print(f"\nTOTAL signal rows: {n:,}")
print(f"play_type flips:  {len(flip):,} ({len(flip)/n*100:.2f}%)")

b2b = flip[flip["play_type_base"].isin(BUY_TIERS) | flip["play_type_live"].isin(BUY_TIERS)]
gain = flip[~flip["play_type_base"].isin(BUY_TIERS) & flip["play_type_live"].isin(BUY_TIERS)]
lose = flip[flip["play_type_base"].isin(BUY_TIERS) & ~flip["play_type_live"].isin(BUY_TIERS)]
swap = flip[flip["play_type_base"].isin(BUY_TIERS) & flip["play_type_live"].isin(BUY_TIERS)]
print(f"BUY-relevant flips: {len(b2b):,} ({len(b2b)/n*100:.2f}% of all rows)")
print(f"  NEW buys under dt5g (base blocked): {len(gain):,}")
print(f"  LOST buys under dt5g (base allowed): {len(lose):,}")
print(f"  tier swap (both BUY, tier changed):  {len(swap):,}")

base_buys = m["play_type_base"].isin(BUY_TIERS).sum()
live_buys = m["play_type_live"].isin(BUY_TIERS).sum()
print(f"\nBUY rows base: {base_buys:,} | dt5g: {live_buys:,} | delta {live_buys-base_buys:+,} ({(live_buys-base_buys)/base_buys*100:+.1f}%)")

print("\ntop flip pairs:")
print(flip.groupby(["play_type_base","play_type_live"]).size().sort_values(ascending=False).head(15).to_string())

print("\nBUY-relevant flips by year:")
print(b2b.groupby(b2b["time"].dt.year).size().to_string())

# distinct dates affected
print(f"\ndates with >=1 BUY-relevant flip: {b2b['time'].nunique()} / {m['time'].nunique()} total dates")

out = "data/f3_exp/f3_playtype_flips.csv"
flip.drop(columns=["_merge"]).to_csv(out, index=False)
print(f"\nwrote {out}")
