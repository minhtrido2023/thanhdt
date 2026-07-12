# -*- coding: utf-8 -*-
"""dvr8l_tilt.py — DVR entry-time sizing tilt by 8L route/rating. EXPERIMENT (job Taylor_20260711_235305).

Pre-registered family (mike/agents/Taylor/plan_dvr_8l_sizing_20260712.md §4, N-ledger closed at 5):
  R1 route-tilt:     DVR entry with route in {COMPOUNDER, POWER} -> half size (else full)
  R2 fragility-tilt: DVR entry with rating8l >= 4 -> half size (else full)
  R3 combined:       multiplicative x0.5 per axis, floor = half*0.5 (full/half/quarter)

Mechanism mirrors regime_size_overlay (VALIDATED pattern): split DEEP_VALUE_RECOVERY rows whose
8L ROUTE is bad into sub-tier '<tier>_X' with its own tier weight. The rating>=4 axis reuses the
'_W' split ALREADY made by apply_regime_size (same table tav2_bq.fa_ratings_8l, same merge_asof
backward PIT semantics — rating8l column is left on sig by that call); R2/R3 assign a base tier
weight to DEEP_VALUE_RECOVERY_W, which in the baseline inherits full size outside stress states.

WEIGHT-ONLY change (plan §5): TIER_PRIORITY for each new '_X' name mirrors what the SAME row
resolved to before the rename (DEEP_VALUE_RECOVERY_X = 55; DEEP_VALUE_RECOVERY_W_X = 0, the
.get() default the _W name already resolves to in the baseline) -> execution order / eviction
identical; only target_value at first fill changes.

Stress-state composition (plan §8.6, accepted by design): regime_size halves rating-weak (_W)
tiers in states 1-2; the entry tilt composes multiplicatively on top (e.g. R3 W_X in CRISIS =
quarter*0.5). Encoded in tier_weights_by_state below.

Fail-open (plan §4): missing route/rating as-of entry -> treated GOOD (full size). The rule may
only shrink size on positive evidence of a bad group, never punish missing data.
"""
import os
import pandas as pd

BAD_ROUTES = ("COMPOUNDER", "POWER")   # category, pre-registered — no tuned threshold
DVR = "DEEP_VALUE_RECOVERY"


def apply_dvr8l_tilt(sig, RS, bq, end, mode, full=0.10, half=0.05, dump_dir=None):
    """Apply pre-registered DVR sizing tilt R1/R2/R3 on top of apply_regime_size output.

    sig: signal frame AFTER apply_regime_size (has rating8l column; weak rows already '<tier>_W').
    RS:  the dict returned by apply_regime_size — mutated copy returned.
    Returns (sig_out, RS_out).
    """
    mode = mode.lower()
    assert mode in ("r1", "r2", "r3"), mode
    quarter = half * 0.5
    s = sig.copy()
    RS = dict(RS)
    tw = dict(RS["tier_weights"])
    twbs = {st: dict(d) for st, d in RS["tier_weights_by_state"].items()}
    allowed = list(RS["allowed_tiers"])

    is_dvr = s["play_type"].isin([DVR, DVR + "_W"])
    n_dvr = int(is_dvr.sum())

    dump = None
    if mode in ("r1", "r3"):
        # ROUTE axis: PIT merge_asof backward on (ticker, time) — identical pattern to
        # regime_size_overlay.load_rating8l, same canonical table (data_registry: CANONICAL).
        rt = bq(f"""SELECT f.ticker, f.time, f.route FROM tav2_bq.fa_ratings_8l AS f
    WHERE f.time <= DATE '{end}'""")
        rt["time"] = pd.to_datetime(rt["time"])
        rt = rt.sort_values("time")
        rt = rt.rename(columns={"time": "r8l_eff_date"})
        s = s.sort_values("time")
        s = pd.merge_asof(s, rt, left_on="time", right_on="r8l_eff_date",
                          by="ticker", direction="backward")
        # merge_asof returns a fresh RangeIndex -> recompute the DVR mask on the merged frame
        is_dvr_m = s["play_type"].isin([DVR, DVR + "_W"])
        bad_route = s["route"].isin(BAD_ROUTES) & is_dvr_m
        n_bad = int(bad_route.sum())
        s.loc[bad_route, "play_type"] = s.loc[bad_route, "play_type"].astype(str) + "_X"
        # audit dump AFTER the rename: play_type shows the final tier incl. '_X' for the spot-check
        if dump_dir:
            dump = s.loc[is_dvr_m,
                         ["ticker", "time", "play_type", "route", "r8l_eff_date", "rating8l"]].copy()
        s = s.drop(columns=["route", "r8l_eff_date"])
        x_tiers = [DVR + "_X", DVR + "_W_X"]
        allowed += x_tiers
        # priority mirror: _X = pre-rename name's resolved priority (weight-only change)
        import simulate_holistic_nav as shn
        shn.TIER_PRIORITY[DVR + "_X"] = shn.TIER_PRIORITY.get(DVR, 0)          # 55
        shn.TIER_PRIORITY[DVR + "_W_X"] = shn.TIER_PRIORITY.get(DVR + "_W", 0)  # 0 (same as _W today)
        print(f"  [dvr8l {mode}] route axis: {n_bad:,}/{n_dvr:,} DVR rows route-bad "
              f"({'/'.join(BAD_ROUTES)}) -> '_X' half-size {half:.1%}")

    if mode == "r1":
        tw[DVR + "_X"] = half
        tw[DVR + "_W_X"] = half                      # route tilt only; rating axis untouched
        for st in twbs:                              # stress: regime halving on _W composes
            twbs[st][DVR + "_X"] = half
            twbs[st][DVR + "_W_X"] = quarter
    elif mode == "r2":
        tw[DVR + "_W"] = half                        # rating>=4 -> half at entry, ALL states
        for st in twbs:
            twbs[st][DVR + "_W"] = quarter           # stress: regime halving composes
        n_w = int((s["play_type"] == DVR + "_W").sum())
        if dump_dir:
            dump = s.loc[s["play_type"].isin([DVR, DVR + "_W"]),
                         ["ticker", "time", "play_type", "rating8l"]].copy()
        print(f"  [dvr8l r2] fragility axis: {n_w:,}/{n_dvr:,} DVR rows rating>=4 (_W) "
              f"-> entry size {half:.1%} in ALL states (stress composes to {quarter:.1%})")
    else:  # r3 combined, multiplicative with floor half*0.5
        tw[DVR + "_X"] = half                        # route-bad only
        tw[DVR + "_W"] = half                        # rating-weak only
        tw[DVR + "_W_X"] = quarter                   # both -> floor
        for st in twbs:
            twbs[st][DVR + "_X"] = half
            twbs[st][DVR + "_W"] = quarter
            twbs[st][DVR + "_W_X"] = quarter * 0.5
        print(f"  [dvr8l r3] combined: DVR {full:.1%} / single-axis {half:.1%} / both {quarter:.1%}")

    if dump_dir and dump is not None:
        os.makedirs(dump_dir, exist_ok=True)
        p = os.path.join(dump_dir, f"dvr8l_rows_{mode}.csv")
        dump.to_csv(p, index=False)
        print(f"  [dvr8l] audit dump {len(dump):,} DVR rows -> {p}")

    RS["allowed_tiers"] = allowed
    RS["tier_weights"] = tw          # tw = copy of original (all full) + tilt overrides + new _X tiers
    RS["tier_weights_by_state"] = twbs
    return s, RS
