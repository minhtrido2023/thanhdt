#!/usr/bin/env python3
"""Dump membership + raw panel + BOTH production return legs of the pinned R3 custom30V park basket.

Runs `custom_basket.build_pit()` with the EXACT pinned R3 parameters (see PREREG.md §Nguon /
§Quy uoc 1) and writes everything the position-replay needs to a parquet set, so the replay is a
pure offline recomputation an auditor can rerun without touching BQ again.

Two build_pit calls, differing in ONE env var (BASKET_RETURN_OSHARES) -> the FLAT (production)
and LEGACY (pre-fix) level series. Weight leg / selection are identical by construction (module
header SCOPE OF THE FIX), asserted here on members_df.
"""
import os, sys
os.environ.setdefault("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude")
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
os.chdir(WC)
import pandas as pd

OUT = f"{WC}/mike/agents/Taylor/research/c30v_position_replay_20260927"
START, END = "2014-01-02", "2026-06-19"

from simulate_holistic_nav import bq
import custom_basket as cb

# pinned R3 basket params: ETF_LIQ=custompitg -> (quality, rebal, gate) = ("none","q2m5",3)
KW = dict(quality="none", rebal="q2m5", gate_rating=3, weight_scheme="namecap",
          top_n=30, name_cap=0.10, qtilt=None)
print(f"[cfg] UNIVERSE_SOURCE={cb.UNIVERSE_SOURCE} BASKET_SELECT={os.environ.get('BASKET_SELECT')} "
      f"BASKET_PRICE_BASIS={os.environ.get('BASKET_PRICE_BASIS','split (default)')} "
      f"BASKET_OSHARES_STEP={os.environ.get('BASKET_OSHARES_STEP','exdate (default)')} "
      f"CA_SNAPSHOT={os.environ.get('BASKET_CA_SNAPSHOT')}", flush=True)

legs = {}
for tag, val in (("flat", "flat"), ("legacy", "legacy")):
    os.environ["BASKET_RETURN_OSHARES"] = val
    assert cb.retchain_legacy() == (val == "legacy")
    lvl, adv, mem, bx = cb.build_pit(bq, START, END, **KW)
    legs[tag] = (lvl, adv, mem, bx)
    print(f"[leg {tag}] level n={len(lvl)} first={min(lvl)} last={max(lvl)}", flush=True)
os.environ.pop("BASKET_RETURN_OSHARES", None)

mf, ml = legs["flat"][2], legs["legacy"][2]
assert mf.equals(ml), "members_df khac nhau giua 2 chan -> A/B khong con 1 bien"
bxf, bxl = legs["flat"][3], legs["legacy"][3]
assert bxf.reset_index(drop=True).equals(bxl.reset_index(drop=True)), "bx khac nhau giua 2 chan"

bxf.to_parquet(f"{OUT}/panel_bx.parquet", index=False)
mf.to_parquet(f"{OUT}/members_df.parquet", index=False)
for tag in ("flat", "legacy"):
    lvl = legs[tag][0]
    pd.Series(lvl).sort_index().rename("level").to_frame().to_parquet(f"{OUT}/level_{tag}.parquet")
pd.Series(legs["flat"][1]).sort_index().rename("adv").to_frame().to_parquet(f"{OUT}/adv_flat.parquet")

print(f"[dump] panel rows={len(bxf):,} cols={list(bxf.columns)}")
print(f"[dump] members rows={len(mf):,} cols={list(mf.columns)} rebals={mf['rebal_date'].nunique()} "
      f"union={mf['ticker'].nunique()}")
for tag in ("flat", "legacy"):
    s = pd.Series(legs[tag][0]).sort_index()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    print(f"[dump] {tag}: level {s.iloc[0]:.1f} -> {s.iloc[-1]:.1f}  "
          f"CAGR {((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100:.2f}%  ({yrs:.2f}y)")
