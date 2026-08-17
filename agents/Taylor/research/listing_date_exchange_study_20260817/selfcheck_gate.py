#!/usr/bin/env python3
"""Selfcheck for the Step-1 listing_date gate. Offline — recomputes from out/*.csv only.

Purpose: every number quoted in GATE_REPORT.md must be recomputable from the dumped CSVs, and the
GATE verdict must follow mechanically from the preregistered thresholds rather than from prose.
Run: python3 selfcheck_gate.py
"""
from __future__ import annotations

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# Gate thresholds, copied verbatim from the dispatch (job Taylor_20260817_112844):
#   PASS iff median(exright_date - listing_date) for RIGHTS is in [5, 20] calendar days
#   AND >= 70% of RIGHTS events have that gap in [3, 30].
GATE_MEDIAN_LO, GATE_MEDIAN_HI = 5, 20
GATE_PCT_MIN = 70.0

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


def load(name: str) -> list[dict]:
    path = os.path.join(OUT, name)
    if not os.path.exists(path):
        raise SystemExit(f"missing artifact: {path} — run gate_build.py first")
    with open(path) as fh:
        return list(csv.DictReader(fh))


def by(rows: list[dict], key: str, val: str) -> dict:
    hit = [r for r in rows if r[key] == val]
    if len(hit) != 1:
        raise SystemExit(f"expected exactly 1 row {key}={val}, got {len(hit)}")
    return hit[0]


m1 = load("m1_fill_by_event_code.csv")
m2 = load("m2_gap_by_subtype.csv")
m3 = load("m3_ais_match.csv")
m4 = load("m4_sample20.csv")
m5 = load("m5_zero_gap_by_year.csv")
m6 = load("m6_listing_before_ex.csv")
m7 = load("m7_ais_match_scoped.csv")

# --- T1..T3: the Sprint-1 DATA_DICTIONARY claim "listing_date 100% NULL toan bang" is false, and
# false in a specific way — NULL on every event_code EXCEPT ISS.
iss = by(m1, "event_code", "ISS")
check("T1 ISS carries listing_date", int(iss["n_listing"]) > 0,
      f'{iss["n_listing"]}/{iss["n"]} = {iss["pct_listing"]}%')
check("T2 ISS fill rate is the ~82% quoted in the report",
      abs(float(iss["pct_listing"]) - 81.8) < 0.15, iss["pct_listing"])
non_iss = [r for r in m1 if r["event_code"] != "ISS"]
check("T3 every non-ISS event_code is 100% NULL",
      all(int(r["n_listing"]) == 0 for r in non_iss),
      ",".join(f'{r["event_code"]}={r["n_listing"]}' for r in non_iss))

# --- T4..T7: the gate itself. Sign convention: gap = exright_date - listing_date, so a POSITIVE
# gap means listing_date precedes the ex-date (the exchange-notification hypothesis).
rights = by(m2, "subtype", "RIGHTS")
median_gap = int(rights["median_gap"])
pct_in_band = float(rights["pct_gap_in_3_30"])

check("T4 RIGHTS median gap is the -91 days quoted", median_gap == -91, str(median_gap))
check("T5 RIGHTS median gap FAILS the [5,20] window",
      not (GATE_MEDIAN_LO <= median_gap <= GATE_MEDIAN_HI),
      f"{median_gap} vs [{GATE_MEDIAN_LO},{GATE_MEDIAN_HI}]")
check("T6 RIGHTS share in [3,30] FAILS the >=70% bar",
      pct_in_band < GATE_PCT_MIN, f"{pct_in_band}% vs {GATE_PCT_MIN}%")
gate_pass = (GATE_MEDIAN_LO <= median_gap <= GATE_MEDIAN_HI) and pct_in_band >= GATE_PCT_MIN
check("T7 GATE verdict computes to FAIL", gate_pass is False, f"gate_pass={gate_pass}")

# T8: the band share is recomputable from the raw counts, not just read off a column.
recomputed = 100.0 * int(rights["n_gap_in_3_30"]) / int(rights["n_both"])
check("T8 pct_gap_in_3_30 recomputes from n_gap_in_3_30/n_both",
      abs(recomputed - pct_in_band) < 0.05, f"{recomputed:.3f} vs {pct_in_band}")

# T9: the three sign buckets must partition the events that have BOTH dates. If they don't, the
# gap column is being computed on a different row set than the counts and nothing else is safe.
for sub in ("RIGHTS", "PRIVATE_PLACEMENT"):
    r = by(m2, "subtype", sub)
    tot = int(r["n_listing_before_ex"]) + int(r["n_listing_eq_ex"]) + int(r["n_listing_after_ex"])
    check(f"T9 {sub} sign buckets partition n_both", tot == int(r["n_both"]),
          f'{tot} vs {r["n_both"]}')

# T10: PP's median gap is 0 only because ~69% of PP rows carry the degenerate listing==exright
# value. Report says so; lock it, because a reader could mistake median 0 for "same-day listing".
pp = by(m2, "subtype", "PRIVATE_PLACEMENT")
pp_eq_share = 100.0 * int(pp["n_listing_eq_ex"]) / int(pp["n_both"])
check("T10 PP median 0 is driven by a >60% zero-gap mass",
      int(pp["median_gap"]) == 0 and pp_eq_share > 60, f"{pp_eq_share:.1f}%")

# --- T11..T13: rival hypothesis. listing_date == AIS.effective_date (additional-listing date).
for sub in ("RIGHTS", "STOCK_DIVIDEND", "BONUS", "PRIVATE_PLACEMENT"):
    r = by(m7, "subtype", sub)
    hit, plac = float(r["pct_hit_listing"]), float(r["pct_hit_exright_placebo"])
    check(f"T11 {sub} listing_date beats the exright placebo against AIS by >=5x",
          hit >= 5 * max(plac, 0.1) and hit > 60, f"listing={hit}% placebo={plac}%")

# T12: scoping to tickers with a nearby AIS row must RAISE the match rate vs the unscoped M3 —
# otherwise the scope filter is selecting on the outcome rather than on data availability.
for sub in ("RIGHTS", "STOCK_DIVIDEND", "PRIVATE_PLACEMENT"):
    check(f"T12 {sub} scoped match rate exceeds unscoped",
          float(by(m7, "subtype", sub)["pct_hit_listing"])
          > float(by(m3, "subtype", sub)["pct_ais_exact"]),
          f'{by(m7,"subtype",sub)["pct_hit_listing"]} > {by(m3,"subtype",sub)["pct_ais_exact"]}')

# T13: the exact-match and +/-3d-window match rates must be near-identical. A large gap between
# them would mean the dates merely CLUSTER rather than being the same field.
for r in m3:
    check(f"T13 {r['subtype']} exact vs +/-3d match rates agree within 1pp",
          abs(float(r["pct_ais_pm3"]) - float(r["pct_ais_exact"])) <= 1.0,
          f'{r["pct_ais_exact"]} vs {r["pct_ais_pm3"]}')

# --- T14..T16: the manual-inspection sample must actually support the verdict.
check("T14 sample has 20 events across both strata", len(m4) == 20
      and len({r["stratum"] for r in m4}) == 2, f"{len(m4)} rows")
check("T15 every sampled event has listing_date AFTER exright_date",
      all(int(r["gap_ex_minus_listing"]) < 0 for r in m4),
      f'max gap = {max(int(r["gap_ex_minus_listing"]) for r in m4)}')
check("T16 sample is restricted to RIGHTS/PP",
      {r["subtype"] for r in m4} <= {"RIGHTS", "PRIVATE_PLACEMENT"},
      str(sorted({r["subtype"] for r in m4})))

# --- T17..T18: the pro-hypothesis evidence, characterised honestly rather than dismissed.
r_before = [r for r in m6 if r["subtype"] == "RIGHTS"]
check("T17 RIGHTS-with-listing-before-ex count matches M2", len(r_before) == 11, str(len(r_before)))
notice_like = [r for r in r_before if 3 <= int(r["gap_ex_minus_listing"]) <= 30]
check("T18 at most a handful of RIGHTS look notice-like (3-30d)",
      len(notice_like) <= 2,
      ",".join(f'{r["ticker"]}:{r["gap_ex_minus_listing"]}' for r in notice_like) or "none")

# --- T19: the zero-gap mass is an early-history artifact that decays to ~0, i.e. it is vendor
# fallback, not a real same-day listing regime.
rights_yr = sorted((r for r in m5 if r["subtype"] == "RIGHTS"), key=lambda z: int(z["yr"]))
early = [r for r in rights_yr if int(r["yr"]) <= 2008 and r["pct_eq"]]
late = [r for r in rights_yr if int(r["yr"]) >= 2023 and r["pct_eq"]]
check("T19 zero-gap share decays from early history to ~0 recently",
      early and late
      and sum(float(r["pct_eq"]) for r in early) / len(early) > 50
      and sum(float(r["pct_eq"]) for r in late) / len(late) < 10,
      f'early={sum(float(r["pct_eq"]) for r in early)/len(early):.1f}% '
      f'late={sum(float(r["pct_eq"]) for r in late)/len(late):.1f}%')

# --- T20: N is declared as independent issuers, not row count (coding_guidelines §18).
check("T20 RIGHTS issuer count is present and far below event count",
      0 < int(rights["n_issuers"]) < int(rights["n_events"]),
      f'{rights["n_issuers"]} issuers / {rights["n_events"]} events')

npass = sum(1 for _, ok, _ in RESULTS if ok)
for name, ok, detail in RESULTS:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
print(f"\n{npass}/{len(RESULTS)} PASS")
sys.exit(0 if npass == len(RESULTS) else 1)
