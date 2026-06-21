#!/usr/bin/env python3
"""
moat_5f.py — 5F (Porter 5-Forces) → 8L L4-Moat overlay
======================================================
Bridges the QUALITATIVE 5F analyst (Porter's 5 Forces persona, see 5F.md) into the
QUANTITATIVE 8L ranker (rank_8l.py). 5F produces a durability verdict on a firm's
economic moat from industry structure; 8L's L4 currently only has an ROE *proxy*
for moat, which is fooled by cyclical/transient high ROE (the DRC "no-moat → transient"
trap). This module lets a human transcribe a 5F run into a tag and have it act as a
DURABILITY GATE on the score — NOT free additive points.

DESIGN PRINCIPLES (encode validated lessons — do not turn this into a ranker):
  1. "Quality = GATE, not ranker" (8L_README; fa_layer_ic_audit_2026: FA-as-ranker
     FAILS full-NAV prodspec). So the overlay only ADJUSTS the existing moat+dislocation
     block within a hard cap; it never mints unbounded new points.
  2. WIDE moat   -> floor L4 near its ceiling + let buy-fear (dislocation) pay a small
                    DURABILITY bonus (durable moat => deep dd is opportunity, VCS-style).
  3. NONE moat   -> HAIRCUT L4 (high ROE w/o a barrier = transient, DRC-style) and
                    half-discount buy-fear (deep dd w/o moat = falling knife). This is
                    the real value-add: catching ROE-without-moat false positives.
  4. NARROW      -> neutral (x1.0).
  5. Backward-compatible: if data/moat_tags.csv is absent, the overlay is a no-op and
     rank_8l output is byte-identical to before.
  6. LIVE-ONLY: 5F runs on LLM knowledge (post-hoc, non-point-in-time, non-deterministic)
     -> it must NEVER feed a historical backtest (look-ahead/hindsight contamination).
     rank_8l.py is a live snapshot tool, so consuming it here is safe; the prodspec
     backtester (run_5systems_prodspec.py) must stay 5F-free.

TAG SCHEMA (data/moat_tags.csv) — one row per name, transcribed from a 5F run:
  ticker      : symbol
  moat_tier   : WIDE | NARROW | NONE   (5F headline verdict on moat DURABILITY)
  moat_type   : TECH|BRAND|LOCATION|SCALE|COST|REGULATORY|NETWORK|NONE  (L4 type label)
  entry       : H|M|L  (industry structural attractiveness; 5F "ngành hấp dẫn mức nào")
  risk1       : free text — the #1 risk to watch (5F's mandatory output)
  asof        : YYYY-MM-DD of the 5F run (staleness check)
  src         : 5f | 5f_validated | manual
"""
import os, csv

VALID_TIERS = {"WIDE", "NARROW", "NONE"}

# bounded overlay knobs (kept conservative on purpose — gate, not ranker)
L4_CEILING       = 15     # existing L4_moat max in rank_8l (do not exceed)
WIDE_FLOOR       = 12     # a confirmed wide moat floors L4 here (can't inflate past ceiling)
NONE_CAP         = 3      # no real barrier => transient => cap L4 here
WIDE_DUR_FACTOR  = 0.15   # +15% of dislocation as a durability bonus (buy-fear pays for durable moats)
NONE_DUR_FACTOR  = -0.50  # half-discount buy-fear for no-moat names (falling-knife risk)


def load_moat_tags(workdir):
    """Return {ticker: {tier, type, entry, risk1, asof, src}}; {} if file absent."""
    path = os.path.join(workdir, "data", "moat_tags.csv")
    if not os.path.exists(path):
        return {}
    out = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            t = (row.get("ticker") or "").strip().upper()
            tier = (row.get("moat_tier") or "").strip().upper()
            if not t or tier not in VALID_TIERS:
                continue
            out[t] = {
                "tier": tier,
                "type": (row.get("moat_type") or "").strip().upper(),
                "entry": (row.get("entry") or "").strip().upper(),
                "risk1": (row.get("risk1") or "").strip(),
                "asof": (row.get("asof") or "").strip(),
                "src": (row.get("src") or "").strip(),
            }
    return out


def apply_moat_overlay(comp, ticker, tags):
    """Mutate `comp` (the per-row component dict) IN PLACE with the 5F moat gate.

    Adds keys: 'moat5f_dur' (bounded durability adj) and may rewrite 'L4_moat'.
    Returns the tier string applied (or None). Bounded + no-op when untagged.
    """
    info = tags.get(str(ticker).upper())
    if not info:
        return None
    tier = info["tier"]
    moat = comp.get("L4_moat", 0) or 0
    dis = comp.get("dislocation", 0) or 0
    if tier == "WIDE":
        # confirm durable moat: floor L4 (but never exceed its ceiling) + small durability bonus on buy-fear
        comp["L4_moat"] = min(L4_CEILING, max(moat, WIDE_FLOOR))
        if dis > 0:
            comp["moat5f_dur"] = round(dis * WIDE_DUR_FACTOR, 1)
    elif tier == "NONE":
        # no barrier: high ROE is likely cyclical/transient -> haircut L4 + discount buy-fear (falling knife)
        comp["L4_moat"] = min(moat, NONE_CAP)
        if dis > 0:
            comp["moat5f_dur"] = round(dis * NONE_DUR_FACTOR, 1)
    # NARROW -> neutral, intentionally no change
    return tier
