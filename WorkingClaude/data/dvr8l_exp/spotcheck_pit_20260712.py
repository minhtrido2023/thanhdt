# -*- coding: utf-8 -*-
"""Spot-check 20 DVR rows from the dvr8l tilt dump: rating/route must be the true as-of PIT row
from tav2_bq.fa_ratings_8l (read INDEPENDENTLY from the raw parquet, not via the engine's bq()),
and the matched eff_date must be <= entry date (no look-ahead). Job Taylor_20260711_235305."""
import sys
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
dump = pd.read_csv(f"{WORKDIR}/data/dvr8l_exp/dvr8l_rows_r3.csv", parse_dates=["time", "r8l_eff_date"])
raw = pd.read_parquet(f"{WORKDIR}/data/bq_cache/fa_ratings_8l.parquet")
raw["time"] = pd.to_datetime(raw["time"])

# deterministic stratified sample: spread over years, fixed seed
dump["year"] = dump["time"].dt.year
parts = [g.sample(min(2, len(g)), random_state=42) for _, g in dump.groupby("year")]
sample = pd.concat(parts)
if len(sample) < 20:
    extra = dump.drop(sample.index).sample(20 - len(sample), random_state=42)
    sample = pd.concat([sample, extra])
sample = sample.head(20) if len(sample) > 20 else sample

fails = 0
for _, r in sample.iterrows():
    hist = raw[(raw["ticker"] == r["ticker"]) & (raw["time"] <= r["time"])]
    if hist.empty:
        # fail-open case: no as-of row -> dump must show NaN route and NO _X suffix
        ok = pd.isna(r.get("route")) and not str(r["play_type"]).endswith("_X")
        status = "OK(fail-open)" if ok else "FAIL(fail-open violated)"
        if not ok: fails += 1
        print(f"{r['ticker']} {r['time'].date()} no-asof-row {status} play={r['play_type']}")
        continue
    true_row = hist.sort_values("time").iloc[-1]
    exp_route, exp_rating, eff = true_row["route"], int(true_row["rating"]), true_row["time"]
    got_route = r.get("route")
    got_rating = r.get("rating8l")
    pt = str(r["play_type"])
    # NOTE: dump in the 2026-07-12 runs was captured BEFORE the '_X' rename (module since fixed to
    # capture after) — suffix correctness is verified separately at TX level in part B below.
    checks = {
        "route_match": (got_route == exp_route) if pd.notna(got_route) else pd.isna(exp_route),
        "rating_match": (pd.notna(got_rating) and int(got_rating) == exp_rating),
        "eff_date_match": (pd.notna(r["r8l_eff_date"]) and r["r8l_eff_date"] == eff),
        "no_lookahead": (pd.isna(r["r8l_eff_date"]) or r["r8l_eff_date"] <= r["time"]),
        "w_flag_correct": (("_W" in pt) == (exp_rating >= 4)),
    }
    bad = [k for k, v in checks.items() if not v]
    if bad:
        fails += 1
        print(f"FAIL {r['ticker']} {r['time'].date()} play={pt} dump=({got_route},{got_rating},"
              f"{r['r8l_eff_date']}) true=({exp_route},{exp_rating},{eff.date()}) bad={bad}")
    else:
        print(f"OK   {r['ticker']} {r['time'].date()} play={pt:<28} route={exp_route:<11} "
              f"rating={exp_rating} eff={eff.date()} (lag {(r['time']-eff).days}d)")

print(f"\nPart A (signal-level PIT): {len(sample)} rows checked, {fails} FAIL")

# consistency: engine log said 2,704 route-bad rows flagged — recount from the dump
n_bad_dump = int(dump["route"].isin(("COMPOUNDER", "POWER")).sum())
print(f"Part A2: route-bad rows in dump = {n_bad_dump:,} (engine log flagged 2,907)")
if n_bad_dump != 2907:
    fails += 1

# ---- Part B: TX-level — every DVR BUY entry in the r3 run must carry the suffix implied by the
# as-of route/rating at its SIGNAL date (fill = T+1 Open after signal). Uses the r3 audit CSV
# (actual traded entries) x the PIT-verified dump.
tx = pd.read_csv(f"{WORKDIR}/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_"
                 f"etfliqcustompitg_wtnamecap_exp_dvr8lr3.csv", low_memory=False)
ent = tx[(tx["action"].astype(str).str.lower() == "buy") & tx["play_type"].astype(str).str.startswith("DEEP_VALUE_RECOVERY")].copy()
ent["ymd"] = pd.to_datetime(ent["ymd"])
ent = ent.drop_duplicates(subset=["ticker", "holding_id"])   # one row per entry
dmp = dump.sort_values("time")
bfails, checked = 0, 0
ent_s = pd.concat([g.sample(min(2, len(g)), random_state=7) for _, g in ent.groupby(ent["ymd"].dt.year)]).head(24)
for _, e in ent_s.iterrows():
    sig_rows = dmp[(dmp["ticker"] == e["ticker"]) & (dmp["time"] < e["ymd"])]
    if sig_rows.empty:
        print(f"B?   {e['ticker']} {e['ymd'].date()} no signal row before fill (unexpected)"); bfails += 1; continue
    srow = sig_rows.iloc[-1]
    exp_x = srow["route"] in ("COMPOUNDER", "POWER") if pd.notna(srow["route"]) else False
    exp_w = pd.notna(srow["rating8l"]) and srow["rating8l"] >= 4
    pt = str(e["play_type"])
    ok = (pt.endswith("_X") == exp_x) and (("_W" in pt) == exp_w)
    checked += 1
    tag = "OK  " if ok else "FAIL"
    if not ok: bfails += 1
    print(f"B{tag} {e['ticker']} fill={e['ymd'].date()} sig={srow['time'].date()} play={pt:<30} "
          f"route={srow['route']} rating={srow['rating8l']} -> exp _X={exp_x} _W={exp_w}")
print(f"\nPart B (TX entry-level suffix): {checked} entries checked, {bfails} FAIL")
sys.exit(1 if (fails or bfails) else 0)
