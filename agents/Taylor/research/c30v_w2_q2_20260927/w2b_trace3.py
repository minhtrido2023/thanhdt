#!/usr/bin/env python3
"""W2b step 2c — classify the divergent orders against the engine's three DISCRETE rails.

Rails read out of simulate_holistic_nav.py (not guessed):
  R-a  min-ticket      `if buy_value >= 100_000` (line 1240) — buy_value = min(remaining, ADV cap,
       buying power incl. cash). Cash enters directly, so a cash difference can put one leg above
       and the other below a HARD 100k VND boundary.
  R-b  fill completion `done = fill_pct >= 0.95 or days_filling >= max_fill_days` (1263) and then
       `fill_pct >= min_fill_pct (0.30)` decides POSITION vs ABANDONED_REFUND (1295). Two hard
       thresholds on a ratio whose numerator is cash-constrained.
  R-c  slot counting   `_n_slots >= max_positions` (1082) and the intake gate
       `len(positions)+len(pending) < max_positions*3` (1264). Integer occupancy: once R-a/R-b put a
       different name in a slot, admission of every LATER signal changes.
Lot size is NOT a rail: shares are fractional in this engine (verified in w2b_trace2).
"""
import os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from paired_w2 import leg_path

def tx(p):
    df = pd.read_csv(p, low_memory=False)
    t = df[df["record_type"] == "TX"].copy()
    t["t"] = pd.to_datetime(t["ymd"], errors="coerce")
    t["k"] = t["t"].astype(str) + "|" + t[["book", "ticker", "action"]].agg("|".join, axis=1)
    return t

def cls(tag_a, tag_b):
    a, b = tx(leg_path(tag_a)), tx(leg_path(tag_b))
    ka, kb = set(a["k"]), set(b["k"])
    onlya = a[a["k"].isin(ka - kb)]; onlyb = b[b["k"].isin(kb - ka)]
    out = {"legs": [tag_a, tag_b],
           "n_tx": [len(a), len(b)],
           "n_tx_only_in_a": len(onlya), "n_tx_only_in_b": len(onlyb),
           "reason_only_in_a": onlya["reason"].value_counts().to_dict(),
           "reason_only_in_b": onlyb["reason"].value_counts().to_dict(),
           "n_ABANDONED_REFUND": [int((a["reason"] == "ABANDONED_REFUND").sum()),
                                  int((b["reason"] == "ABANDONED_REFUND").sum())]}
    # R-a exposure: how many buy fills sit within 2x of the 100k min-ticket boundary?
    for nm, d in (("a", a), ("b", b)):
        buys = d[d["action"] == "buy"]
        gross = buys["buy_amount"].astype(float) + buys["fee"].astype(float)
        out[f"buys_within_2x_of_100k_{nm}"] = int(((gross >= 100_000) & (gross < 200_000)).sum())
        out[f"n_buys_{nm}"] = int(len(buys))
        out[f"min_buy_gross_{nm}"] = round(float(gross.min()), 1)
    # R-b exposure: distinct holding_ids that exist in one leg only (= a whole different position)
    ha = set(a["holding_id"].dropna()); hb = set(b["holding_id"].dropna())
    out["holding_ids"] = {"only_a": len(ha - hb), "only_b": len(hb - ha), "shared": len(ha & hb)}
    # R-c exposure: sessions where the COUNT of open BAL/LAG buys differs
    ca = a[a["action"] == "buy"].groupby(["t", "book"]).size()
    cb = b[b["action"] == "buy"].groupby(["t", "book"]).size()
    j = pd.concat([ca.rename("a"), cb.rename("b")], axis=1).fillna(0)
    out["sessions_with_diff_buy_count"] = int((j["a"] != j["b"]).sum())
    out["sessions_with_buys"] = int(len(j))
    return out

if __name__ == "__main__":
    res = {"D_tier1_vs_tier2": cls("w2d_baseline", "w2d_floor"),
           "A_tier1_vs_tier2": cls("w2a_baseline", "w2a_floor"),
           "D_flat3.0_vs_flat3.5": cls("w2bn_d300", "w2bn_d350"),
           "D_flat3.5_vs_flat4.0": cls("w2bn_d350", "w2bn_d400")}
    json.dump(res, open(os.path.join(HERE, "w2b_trace3.json"), "w"), indent=1)
    print(json.dumps(res, indent=1, ensure_ascii=False))
