# -*- coding: utf-8 -*-
"""F3 measurement (job Taylor_20260711_043508, audit F3 trace Taylor_20260711_031821).

SIGNAL_V11 play_type scored with tav2_bq.vnindex_5state (v3.4b BASE — current behavior of
pt_v4_dt5g/pt_v22_dt5g/pt_v23_audit_2014) vs tav2_bq.vnindex_5state_dt5g_live (docstring
claim + golive_recommend_v23 production behavior). Runs only over the bucket-diff episodes
(play_type CASE only sees state buckets {1,2}|{3}|{4,5}) — identical everywhere else.

Output: data/f3_exp/playtype_diff_sessions.csv (every (time,ticker) whose play_type flips)
        + console summary. Read-only vs production: writes ONLY under data/f3_exp/.
"""
import os, sys
import pandas as pd

WC = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WC); sys.path.insert(0, WC)
from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11

base = pd.read_parquet("data/bq_cache/vnindex_5state.parquet")[["time", "state"]].rename(columns={"state": "s_base"})
live = pd.read_parquet("data/bq_cache/vnindex_5state_dt5g_live.parquet")[["time", "state"]].rename(columns={"state": "s_live"})
for df in (base, live):
    df["time"] = pd.to_datetime(df["time"])
m = base.merge(live, on="time").sort_values("time")
m = m[m["time"] >= "2014-01-01"]
bucket = lambda s: s.map(lambda x: 0 if x in (1, 2) else (1 if x == 3 else 2))
d = m[bucket(m["s_base"]) != bucket(m["s_live"])].copy()
d["gap"] = (d["time"].diff().dt.days > 7).cumsum()
episodes = [(g["time"].min(), g["time"].max()) for _, g in d.groupby("gap")]
print(f"bucket-diff sessions: {len(d)} | episodes: {len(episodes)}")

diff_dates = set(d["time"])
SIG_LIVE = SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s", "tav2_bq.vnindex_5state_dt5g_live AS s")

out = []
for i, (lo, hi) in enumerate(episodes, 1):
    w = dict(start=lo.date().isoformat(), end=hi.date().isoformat())
    a = bq(SIGNAL_V11.format(**w))[["ticker", "time", "play_type", "ta"]]
    b = bq(SIG_LIVE.format(**w))[["ticker", "time", "play_type"]]
    for df in (a, b):
        df["time"] = pd.to_datetime(df["time"])
    a = a[a["time"].isin(diff_dates)]
    b = b[b["time"].isin(diff_dates)]
    j = a.merge(b, on=["ticker", "time"], suffixes=("_base", "_live"))
    flip = j[j["play_type_base"] != j["play_type_live"]]
    out.append(flip)
    print(f"  ep{i:02d} {w['start']}..{w['end']}: rows={len(j):,} flips={len(flip):,}")

flips = pd.concat(out, ignore_index=True).sort_values(["time", "ticker"])
flips.to_csv("data/f3_exp/playtype_diff_sessions.csv", index=False)

BUY_TIERS = {"MEGA", "S_PRO", "MOMENTUM", "MOMENTUM_QUALITY", "MOMENTUM_N",
             "COMPOUNDER_BUY", "DEEP_VALUE_RECOVERY", "MOMENTUM_S", "MOMENTUM_A", "MOMENTUM_S_N"}
flips["buy_base"] = flips["play_type_base"].isin(BUY_TIERS)
flips["buy_live"] = flips["play_type_live"].isin(BUY_TIERS)
print(f"\nTOTAL play_type flips (ticker-sessions): {len(flips):,}")
print(f"  BUY->nonBUY (live tắt tín hiệu mua): {int((flips['buy_base'] & ~flips['buy_live']).sum()):,}")
print(f"  nonBUY->BUY (live bật tín hiệu mua): {int((~flips['buy_base'] & flips['buy_live']).sum()):,}")
print(f"  tier-swap trong nhóm BUY:            {int((flips['buy_base'] & flips['buy_live']).sum()):,}")
print(f"  distinct sessions with >=1 flip: {flips['time'].nunique()} | distinct tickers: {flips['ticker'].nunique()}")
print("\ntop transitions:")
print(flips.groupby(["play_type_base", "play_type_live"]).size().sort_values(ascending=False).head(15))
print("\nflips per year:")
print(flips.groupby(flips["time"].dt.year).size())
