#!/usr/bin/env python3
"""profile_corp_action.py — Sprint 1 data-quality profile of `tav2_bq.corporate_action`.

READ-ONLY. Writes only into ./out/. Run:  python3 profile_corp_action.py

Every number quoted in SPRINT1.md comes from here, so the report is re-derivable by re-running
this one file. Queries are kept in `QUERIES` as named SQL so each can be pasted into `bq` by hand.
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ca_lib import bq  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
T = "tav2_bq.corporate_action"

QUERIES: dict[str, str] = {}

# --- 1. header / freshness -------------------------------------------------------------------
QUERIES["header"] = f"""
SELECT COUNT(*) n_rows, COUNT(DISTINCT id) n_id, COUNT(DISTINCT ticker) n_ticker,
       MIN(public_date) min_public_date, MAX(public_date) max_public_date,
       MIN(exright_date) min_exright, MAX(exright_date) max_exright,
       MIN(ingested_at) min_ingested_at, MAX(ingested_at) max_ingested_at
FROM {T}
"""

# Ingest batches. The decisive column is `n_public_older_30d`: rows written in a batch whose
# public_date long predates it are re-writes of existing events, not newly announced ones.
QUERIES["ingest_batches"] = f"""
SELECT DATE(ingested_at) ingest_date, COUNT(*) n_rows, COUNT(DISTINCT ticker) n_ticker,
       MIN(ingested_at) batch_start, MAX(ingested_at) batch_end,
       MIN(public_date) min_public_date, MAX(public_date) max_public_date,
       COUNTIF(public_date < DATE_SUB(DATE(ingested_at), INTERVAL 30 DAY)) n_public_older_30d
FROM {T} GROUP BY ingest_date ORDER BY ingest_date
"""

# --- 2. coverage -----------------------------------------------------------------------------
QUERIES["coverage_year_code_status"] = f"""
SELECT EXTRACT(YEAR FROM public_date) year, event_code, event_status,
       COUNT(*) n_rows, COUNT(DISTINCT ticker) n_ticker,
       COUNTIF(exright_date IS NOT NULL) n_with_exright
FROM {T} GROUP BY 1,2,3 ORDER BY 1,2,3
"""

# NOTE: `corporate_action` has NO exchange column (HOSE/HNX/UPCOM). `icb_code_lv1` is an INDUSTRY
# code, not a listing venue. Sector is reported instead and the gap is disclosed in SPRINT1.md.
QUERIES["coverage_icb"] = f"""
SELECT IFNULL(icb_code_lv1,'<NULL>') icb_code_lv1, event_code, COUNT(*) n_rows,
       COUNT(DISTINCT ticker) n_ticker
FROM {T} GROUP BY 1,2 ORDER BY n_rows DESC
"""

QUERIES["event_code_status"] = f"""
SELECT event_code, IFNULL(event_status,'<NULL>') event_status, COUNT(*) n_rows,
       COUNT(DISTINCT ticker) n_ticker, MIN(public_date) min_pub, MAX(public_date) max_pub
FROM {T} GROUP BY 1,2 ORDER BY event_code, n_rows DESC
"""

# --- 3. missingness --------------------------------------------------------------------------
_MISS_COLS = [
    "public_date", "display_date1", "display_date2", "exright_date", "record_date", "issue_date",
    "payout_date", "listing_date", "effective_date", "value_per_share", "exercise_ratio",
    "ref_price", "issue_volumn", "total_value", "shares_delta", "shares_total_after",
    "dividend_year", "dividend_stage_vi", "issue_method_code", "issue_method_name_vi",
    "issue_status_vi", "category", "event_title_vi", "event_description_vi", "source_url",
    "organ_code", "icb_code_lv1",
]
QUERIES["missingness"] = f"""
SELECT event_code, COUNT(*) n_rows,
       {', '.join(f'ROUND(100*COUNTIF({c} IS NULL)/COUNT(*),2) pct_null_{c}' for c in _MISS_COLS)}
FROM {T} GROUP BY event_code ORDER BY n_rows DESC
"""

# `exercise_ratio = 0` is NOT the same as NULL but is equally unusable as a dilution factor:
# multiplying by (1+0) is a silent no-op that looks like it was accounted for.
QUERIES["ratio_zero_vs_null"] = f"""
SELECT IFNULL(issue_method_code,'<NULL>') issue_method_code,
       IFNULL(issue_method_name_vi,'<NULL>') issue_method_name_vi,
       COUNT(*) n_rows, COUNTIF(event_status='executed') n_executed,
       COUNTIF(exercise_ratio IS NULL) n_ratio_null,
       COUNTIF(exercise_ratio = 0) n_ratio_zero,
       COUNTIF(exercise_ratio > 0) n_ratio_pos,
       COUNTIF(issue_volumn IS NULL OR issue_volumn = 0) n_volumn_missing_or_zero
FROM {T} WHERE event_code='ISS' GROUP BY 1,2 ORDER BY n_rows DESC
"""

# --- 4. point-in-time: is public_date usable as a knowledge timestamp? ------------------------
# A knowledge timestamp must strictly precede the event it predicts. Rows where
# public_date >= exright_date cannot support an announcement study for that event.
QUERIES["pit_public_vs_exright"] = f"""
SELECT event_code, COUNT(*) n_with_exright,
       COUNTIF(public_date < exright_date) n_pub_before_ex,
       COUNTIF(public_date = exright_date) n_pub_eq_ex,
       COUNTIF(public_date > exright_date) n_pub_after_ex,
       ROUND(100*COUNTIF(public_date >= exright_date)/COUNT(*),2) pct_pub_not_before_ex,
       MIN(DATE_DIFF(exright_date, public_date, DAY)) min_lead_days,
       APPROX_QUANTILES(DATE_DIFF(exright_date, public_date, DAY),100)[OFFSET(5)] p05_lead_days,
       APPROX_QUANTILES(DATE_DIFF(exright_date, public_date, DAY),100)[OFFSET(50)] p50_lead_days,
       APPROX_QUANTILES(DATE_DIFF(exright_date, public_date, DAY),100)[OFFSET(95)] p95_lead_days,
       MAX(DATE_DIFF(exright_date, public_date, DAY)) max_lead_days
FROM {T} WHERE exright_date IS NOT NULL AND public_date IS NOT NULL
GROUP BY event_code ORDER BY n_with_exright DESC
"""

# Same, split by era — a convention that only broke in the early years would be usable on a
# modern sample; one that still breaks today is not.
QUERIES["pit_public_vs_exright_by_year"] = f"""
SELECT event_code, EXTRACT(YEAR FROM exright_date) year, COUNT(*) n,
       COUNTIF(public_date >= exright_date) n_pub_not_before_ex,
       ROUND(100*COUNTIF(public_date >= exright_date)/COUNT(*),2) pct_bad
FROM {T} WHERE exright_date IS NOT NULL AND public_date IS NOT NULL AND event_code IN ('DIV','ISS')
GROUP BY 1,2 ORDER BY 1,2
"""

# `id` is a 24-hex MongoDB ObjectId whose first 4 bytes are a unix timestamp = vendor record
# CREATION time. It is a second, independent time anchor. Decoding it shows whether the history
# is a one-shot backfill (all ids created the same day) or genuinely accreted.
QUERIES["id_creation_epoch"] = f"""
WITH t AS (
  SELECT DATE(TIMESTAMP_SECONDS(CAST(CONCAT('0x',SUBSTR(id,1,8)) AS INT64))) id_created_date,
         public_date, exright_date
  FROM {T} WHERE REGEXP_CONTAINS(id, r'^[0-9a-f]{{24}}$'))
SELECT id_created_date, COUNT(*) n_rows, MIN(public_date) min_pub, MAX(public_date) max_pub,
       COUNTIF(public_date > id_created_date) n_public_after_id_creation
FROM t GROUP BY 1 ORDER BY n_rows DESC LIMIT 40
"""

# --- 5. duplicates / amendments / multi-event days -------------------------------------------
QUERIES["dup_naive_key"] = f"""
WITH g AS (
  SELECT ticker, exright_date, event_code, COUNT(*) n,
         COUNT(DISTINCT IFNULL(CAST(value_per_share AS STRING),'~')) n_distinct_value,
         COUNT(DISTINCT IFNULL(CAST(exercise_ratio AS STRING),'~')) n_distinct_ratio,
         COUNT(DISTINCT IFNULL(issue_method_code,'~')) n_distinct_method
  FROM {T} WHERE exright_date IS NOT NULL GROUP BY 1,2,3)
SELECT event_code, COUNT(*) n_groups, COUNTIF(n>1) n_multi_row_groups,
       SUM(IF(n>1,n,0)) n_rows_in_multi_groups, MAX(n) max_rows_in_group,
       COUNTIF(n>1 AND n_distinct_value=1 AND n_distinct_ratio=1 AND n_distinct_method=1)
         n_groups_all_fields_equal
FROM g GROUP BY event_code ORDER BY n_groups DESC
"""

# The proposed economic key. For DIV a same-day pair is normally two genuine TRANCHES
# (different dividend_year / dividend_stage_vi) that both really go ex that day.
QUERIES["dup_economic_key_div"] = f"""
WITH g AS (
  SELECT ticker, exright_date, dividend_year, dividend_stage_vi, COUNT(*) n,
         COUNT(DISTINCT IFNULL(CAST(value_per_share AS STRING),'~')) n_distinct_value
  FROM {T} WHERE event_code='DIV' AND exright_date IS NOT NULL GROUP BY 1,2,3,4)
SELECT COUNT(*) n_groups, COUNTIF(n>1) n_residual_dup_groups,
       SUM(IF(n>1,n,0)) n_residual_dup_rows, MAX(n) max_rows_in_group,
       COUNTIF(n>1 AND n_distinct_value>1) n_residual_dup_conflicting_value
FROM g
"""

QUERIES["dup_economic_key_iss"] = f"""
WITH g AS (
  SELECT ticker, exright_date, issue_method_code,
         IFNULL(CAST(exercise_ratio AS STRING),'~') ratio,
         IFNULL(CAST(issue_volumn AS STRING),'~') volumn, COUNT(*) n
  FROM {T} WHERE event_code='ISS' AND exright_date IS NOT NULL GROUP BY 1,2,3,4,5)
SELECT COUNT(*) n_groups, COUNTIF(n>1) n_residual_dup_groups,
       SUM(IF(n>1,n,0)) n_residual_dup_rows, MAX(n) max_rows_in_group
FROM g
"""

# Windows where a cash dividend shares its ex-date with a share issuance: the ex-day price drop
# is then NOT attributable to the dividend alone. These must be excluded or handled explicitly.
QUERIES["same_day_multi_family"] = f"""
WITH g AS (
  SELECT ticker, exright_date, STRING_AGG(DISTINCT event_code ORDER BY event_code) codes,
         COUNT(DISTINCT event_code) n_codes, COUNT(*) n_rows
  FROM {T} WHERE exright_date IS NOT NULL AND event_status='executed' GROUP BY 1,2)
SELECT codes, COUNT(*) n_ticker_date_groups, SUM(n_rows) n_rows
FROM g WHERE n_codes>1 GROUP BY codes ORDER BY n_ticker_date_groups DESC
"""

# Contamination in the +/-N day neighbourhood, not just the same day — the real constraint on an
# event-study window.
QUERIES["div_window_contamination"] = f"""
WITH div AS (
  SELECT ticker, exright_date FROM {T}
  WHERE event_code='DIV' AND event_status='executed' AND exright_date IS NOT NULL
  GROUP BY 1,2),
 iss AS (
  SELECT ticker, exright_date FROM {T}
  WHERE event_code='ISS' AND event_status='executed' AND exright_date IS NOT NULL
  GROUP BY 1,2)
SELECT COUNT(*) n_div_events,
       COUNTIF(EXISTS(SELECT 1 FROM iss i WHERE i.ticker=d.ticker
               AND i.exright_date = d.exright_date)) n_iss_same_day,
       COUNTIF(EXISTS(SELECT 1 FROM iss i WHERE i.ticker=d.ticker
               AND ABS(DATE_DIFF(i.exright_date, d.exright_date, DAY)) <= 5)) n_iss_within_5d,
       COUNTIF(EXISTS(SELECT 1 FROM iss i WHERE i.ticker=d.ticker
               AND ABS(DATE_DIFF(i.exright_date, d.exright_date, DAY)) <= 21)) n_iss_within_21d
FROM div d
"""

# --- 6. price + universe coverage ------------------------------------------------------------
QUERIES["div_price_coverage_by_year"] = f"""
WITH d AS (
  SELECT ticker, exright_date FROM {T}
  WHERE event_code='DIV' AND event_status='executed' AND exright_date IS NOT NULL GROUP BY 1,2)
SELECT EXTRACT(YEAR FROM d.exright_date) year, COUNT(*) n_div_events,
       COUNTIF(t.time IS NOT NULL) n_with_price_on_exday,
       ROUND(100*COUNTIF(t.time IS NOT NULL)/COUNT(*),1) pct_with_price,
       COUNTIF(u.in_universe) n_in_universe_pit,
       ROUND(100*COUNTIF(u.in_universe)/COUNT(*),1) pct_in_universe_pit
FROM d
LEFT JOIN tav2_bq.ticker AS t ON t.ticker=d.ticker AND t.time=d.exright_date
LEFT JOIN tav2_mike.universe_pit AS u ON u.ticker=d.ticker AND u.time=d.exright_date
GROUP BY year ORDER BY year
"""

# Does the price series actually step at the recorded ex-date? `Close` is back-adjusted and
# `Price` is raw, so r = Price/Close is the running adjustment factor; it must fall across a
# real ex-date. Measured on CLEAN events only (single DIV, no ISS that day) because a mixed day
# has no single expected step.
#
# The T-1 -> T+1 span deliberately SKIPS the ex-date row: `ticker.Price` on the ex-date row is a
# known TRAP (it can be the cum-basis price copied from T-1 -- registry
# `price-volume/ticker_price_stale_on_exdate.md`, VHM 2026-08-06 off by +98,4%).
QUERIES["div_price_step_alignment"] = f"""
WITH clean AS (
  SELECT c.ticker, c.exright_date, SUM(c.value_per_share) div_per_share
  FROM {T} c
  WHERE c.event_code='DIV' AND c.event_status='executed' AND c.exright_date IS NOT NULL
    AND c.value_per_share IS NOT NULL AND c.exright_date >= '2014-01-01'
    AND NOT EXISTS (SELECT 1 FROM {T} x WHERE x.ticker=c.ticker AND x.event_code='ISS'
                    AND x.event_status='executed'
                    AND ABS(DATE_DIFF(x.exright_date, c.exright_date, DAY)) <= 3)
  GROUP BY 1,2),
 px AS (
  SELECT t.ticker, t.time, SAFE_DIVIDE(t.Price, t.Close) r, t.Price AS px_raw
  FROM tav2_bq.ticker AS t WHERE t.time >= '2013-12-01' AND t.Close > 0 AND t.Price IS NOT NULL),
 bef AS (
  SELECT cl.ticker, cl.exright_date,
         ARRAY_AGG(STRUCT(p.r AS r, p.px_raw AS c) ORDER BY p.time DESC LIMIT 1)[OFFSET(0)] b
  FROM clean cl JOIN px p ON p.ticker=cl.ticker
       AND p.time < cl.exright_date AND p.time >= DATE_SUB(cl.exright_date, INTERVAL 15 DAY)
  GROUP BY 1,2),
 aft AS (
  SELECT cl.ticker, cl.exright_date,
         ARRAY_AGG(STRUCT(p.r AS r) ORDER BY p.time ASC LIMIT 1)[OFFSET(0)] a
  FROM clean cl JOIN px p ON p.ticker=cl.ticker
       AND p.time > cl.exright_date AND p.time <= DATE_ADD(cl.exright_date, INTERVAL 15 DAY)
  GROUP BY 1,2),
 j AS (
  SELECT cl.ticker, cl.exright_date, cl.div_per_share, bef.b.r r_before, bef.b.c cum_price_raw,
         aft.a.r r_after
  FROM clean cl LEFT JOIN bef USING (ticker, exright_date)
                LEFT JOIN aft USING (ticker, exright_date))
SELECT COUNT(*) n_clean_div_events,
       COUNTIF(r_before IS NOT NULL AND r_after IS NOT NULL) n_measurable,
       COUNTIF(r_before > r_after*1.00005) n_ratio_stepped_down,
       COUNTIF(ABS(SAFE_DIVIDE(r_before, r_after)
                   - SAFE_DIVIDE(cum_price_raw, cum_price_raw - div_per_share)) <= 0.002)
         n_step_matches_dividend_0p2pct,
       COUNTIF(ABS(SAFE_DIVIDE(r_before, r_after)
                   - SAFE_DIVIDE(cum_price_raw, cum_price_raw - div_per_share)) <= 0.01)
         n_step_matches_dividend_1pct,
       COUNTIF(r_before IS NOT NULL AND r_after IS NOT NULL
               AND ABS(r_before - r_after) < 0.00001) n_no_step_at_all
FROM j
"""

# Same measurement, kept per-event so the mismatches can be inspected rather than only counted.
QUERIES["div_price_step_detail"] = QUERIES["div_price_step_alignment"].replace(
    """SELECT COUNT(*) n_clean_div_events,
       COUNTIF(r_before IS NOT NULL AND r_after IS NOT NULL) n_measurable,
       COUNTIF(r_before > r_after*1.00005) n_ratio_stepped_down,
       COUNTIF(ABS(SAFE_DIVIDE(r_before, r_after)
                   - SAFE_DIVIDE(cum_price_raw, cum_price_raw - div_per_share)) <= 0.002)
         n_step_matches_dividend_0p2pct,
       COUNTIF(ABS(SAFE_DIVIDE(r_before, r_after)
                   - SAFE_DIVIDE(cum_price_raw, cum_price_raw - div_per_share)) <= 0.01)
         n_step_matches_dividend_1pct,
       COUNTIF(r_before IS NOT NULL AND r_after IS NOT NULL
               AND ABS(r_before - r_after) < 0.00001) n_no_step_at_all
FROM j
""",
    """SELECT ticker, exright_date, div_per_share, cum_price_raw, r_before, r_after,
       ROUND(SAFE_DIVIDE(r_before, r_after),6) observed_factor,
       ROUND(SAFE_DIVIDE(cum_price_raw, cum_price_raw - div_per_share),6) expected_factor,
       ROUND(SAFE_DIVIDE(r_before, r_after)
             - SAFE_DIVIDE(cum_price_raw, cum_price_raw - div_per_share),6) factor_error
FROM j WHERE r_before IS NOT NULL AND r_after IS NOT NULL
""")

# Sanity ceiling on the dividend value itself: a per-share cash dividend larger than the cum
# price is economically impossible and marks a unit error (VND vs '000 VND) or a bad row.
QUERIES["div_value_sanity"] = f"""
WITH d AS (
  SELECT c.ticker, c.exright_date, SUM(c.value_per_share) div_per_share
  FROM {T} c WHERE c.event_code='DIV' AND c.event_status='executed'
    AND c.exright_date IS NOT NULL AND c.value_per_share IS NOT NULL GROUP BY 1,2),
 px AS (SELECT t.ticker, t.time, t.Price AS px_raw FROM tav2_bq.ticker AS t WHERE t.Price > 0),
 cum AS (
  SELECT d.ticker, d.exright_date,
         ARRAY_AGG(p.px_raw ORDER BY p.time DESC LIMIT 1)[OFFSET(0)] cum_price_raw
  FROM d JOIN px p ON p.ticker=d.ticker AND p.time < d.exright_date
       AND p.time >= DATE_SUB(d.exright_date, INTERVAL 15 DAY)
  GROUP BY 1,2)
SELECT COUNT(*) n_div_ticker_dates,
       COUNTIF(d.div_per_share <= 0) n_non_positive_value,
       COUNTIF(c.cum_price_raw IS NULL) n_no_cum_price,
       COUNTIF(c.cum_price_raw IS NOT NULL AND d.div_per_share > c.cum_price_raw) n_div_gt_price,
       COUNTIF(c.cum_price_raw IS NOT NULL AND d.div_per_share > 0.5*c.cum_price_raw)
         n_div_gt_half_price,
       COUNTIF(c.cum_price_raw < 1000) n_cum_price_below_1000vnd,
       ROUND(APPROX_QUANTILES(SAFE_DIVIDE(d.div_per_share, c.cum_price_raw),1000)[OFFSET(500)],5)
         p50_gross_yield,
       ROUND(APPROX_QUANTILES(SAFE_DIVIDE(d.div_per_share, c.cum_price_raw),1000)[OFFSET(990)],5)
         p99_gross_yield
FROM d LEFT JOIN cum c USING (ticker, exright_date)
"""

# Coverage restricted to what the fleet can actually trade. The unrestricted number is dominated
# by illiquid names that carry a corporate action but no usable price series.
QUERIES["div_coverage_investable"] = f"""
WITH d AS (
  SELECT ticker, exright_date FROM {T}
  WHERE event_code='DIV' AND event_status='executed' AND exright_date IS NOT NULL
    AND exright_date >= '2014-01-01' GROUP BY 1,2)
SELECT EXTRACT(YEAR FROM d.exright_date) year, COUNT(*) n_div_events,
       COUNTIF(u.in_universe) n_in_universe_pit,
       COUNTIF(pr.time IS NOT NULL) n_in_ticker_prune,
       COUNTIF(t.time IS NOT NULL) n_with_any_price
FROM d
LEFT JOIN tav2_mike.universe_pit AS u ON u.ticker=d.ticker AND u.time=d.exright_date
LEFT JOIN tav2_bq.ticker_prune AS pr ON pr.ticker=d.ticker AND pr.time=d.exright_date
LEFT JOIN tav2_bq.ticker AS t ON t.ticker=d.ticker AND t.time=d.exright_date
GROUP BY year ORDER BY year
"""

# --- 7. taxonomy input -----------------------------------------------------------------------
QUERIES["iss_rows_for_taxonomy"] = f"""
SELECT id, ticker, public_date, exright_date, event_status, issue_method_code,
       issue_method_name_vi, event_title_vi, event_description_vi, exercise_ratio, issue_volumn
FROM {T} WHERE event_code='ISS'
"""


def write_csv(name: str, rows: list[dict]) -> str:
    path = os.path.join(OUT, f"{name}.csv")
    if not rows:
        open(path, "w").write("")
        return path
    cols = list(rows[0].keys())
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return path


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    only = sys.argv[1:] or None
    index = {}
    for name, sql in QUERIES.items():
        if only and name not in only:
            continue
        if name == "iss_rows_for_taxonomy":
            continue  # consumed by build_event_ledger.py, not dumped here
        print(f"[profile] {name} ...", flush=True)
        rows = bq(sql)
        write_csv(name, rows)
        index[name] = {"n_rows": len(rows), "csv": f"out/{name}.csv"}
        with open(os.path.join(OUT, "sql", f"{name}.sql"), "w") as fh:
            fh.write(sql)
    idx_path = os.path.join(OUT, "profile_index.json")
    prior = {}
    if os.path.exists(idx_path):
        prior = json.load(open(idx_path))
    prior.update(index)
    json.dump(prior, open(idx_path, "w"), indent=2, ensure_ascii=False)
    print(f"[profile] wrote {len(index)} result sets to {OUT}")


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "sql"), exist_ok=True)
    main()
