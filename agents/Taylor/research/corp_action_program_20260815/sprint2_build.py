#!/usr/bin/env python3
"""sprint2_build.py — assemble the cash-dividend event panel for Sprint 2.

Read-only against BigQuery. Every artifact lands in `out2/`. Nothing outside this directory
is written, no table/view/cron is created.

Design note that matters more than the code
-------------------------------------------
The one hard constraint from the Sprint 1 gate is: **never read `ticker.Price` on the ex-date
row** (that row carries the CUM price for an unknown share of events — Winston's finding, and
`ticker.Price` is a reconcile of two vendors that disagree exactly there).

This build never needs it. Under the vendor's multiplicative back-adjustment convention,

    Close_k = Price_k * PROD(factor of every event AFTER k),    factor_ex = (P_cum - D)/P_cum

so the ex-day return measured on the ADJUSTED series is algebraically the raw price measured
against the theoretical ex-reference price:

    Close_0 / Close_{-1}  ==  Price_0 / (Price_{-1} - D)

`Price` is read only at k = -1 (cum side, before the broken row) and at k = +1..+3 (after it),
where it is used solely to recover the adjustment ratio r = Price/Close. The raw ex-day price,
when it is needed at all (secondary outcome only), is RECONSTRUCTED as Close_0 * r_{+1}.

SQL, not pandas, for the windows
--------------------------------
The event list has ~12.5k rows and the price panel ~3.4M; pulling the panel down to join it
locally would move ~200MB through the `bq` CLI. The window extraction therefore happens
server-side and only one wide row per event comes back. The event's dividend amount is
re-derived in SQL with the SAME economic dedup key Sprint 1 chose, and `selfcheck_sprint2.py`
asserts the SQL total equals the ledger's `div_total_on_exdate` on every (ticker, ex-date) —
if that assert ever fails, the SQL is wrong, not the ledger.
"""
from __future__ import annotations

import csv
import gzip
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out2")
SQLDIR = os.path.join(OUT, "sql")
BQ_PROJECT = "lithe-record-440915-m9"

EX_MIN = "2014-01-01"
EX_MAX = "2026-06-30"
PANEL_START = "2013-01-01"   # >= 130 sessions of lookback before the earliest ex-date


def bq_csv(sql: str, name: str, timeout: int = 1800) -> list[dict]:
    """Run read-only SQL from a FILE (queries here exceed comfortable argv size) -> list of dict.

    CSV, not JSON: `bq --format=json` renders every numeric as a string (Sprint 1 issue B2) and
    is ~4x the bytes. The caller converts explicitly via `f()`.
    """
    os.makedirs(SQLDIR, exist_ok=True)
    path = os.path.join(SQLDIR, f"{name}.sql")
    with open(path, "w") as fh:
        fh.write(sql)
    cmd = ["bq", "query", "--use_legacy_sql=false", "--format=csv",
           f"--project_id={BQ_PROJECT}", "--max_rows=2000000", "--quiet"]
    with open(path) as fh:
        p = subprocess.run(cmd, stdin=fh, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"bq failed rc={p.returncode} ({name})\n{p.stderr[-3000:]}")
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    if not lines:
        return []
    return list(csv.DictReader(lines))


def f(v):
    """CSV scalar -> float or None. Empty string is a NULL, not a zero."""
    if v is None or v == "" or v == "NULL":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def d(v):
    if not v:
        return None
    return date.fromisoformat(v[:10])


# ------------------------------------------------------------------------------------------
# SQL
# ------------------------------------------------------------------------------------------
# Economic dedup key for DIV, copied from Sprint 1 §7.1: (ticker, exright_date, dividend_year,
# dividend_stage_vi). Collapsing on (ticker, ex-date) alone would silently halve any company
# paying two tranches on one ex-date (PHN 2026-06-05 is the worked counter-example).
DIV_EVENTS = f"""
WITH div_dedup AS (
  SELECT c.ticker, c.exright_date AS ex_date, c.value_per_share,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `{BQ_PROJECT}.tav2_bq.corporate_action` AS c
  WHERE c.event_code = 'DIV'
    AND c.event_status = 'executed'
    AND c.exright_date IS NOT NULL
    AND c.value_per_share > 0
)
SELECT ticker, ex_date, SUM(value_per_share) AS div_total, COUNT(*) AS n_tranche
FROM div_dedup
WHERE rn = 1
GROUP BY ticker, ex_date
HAVING ex_date BETWEEN DATE '{EX_MIN}' AND DATE '{EX_MAX}'
ORDER BY ticker, ex_date
"""

# One wide row per event. `k` is the session offset relative to the ex-date session; k = 0 IS the
# ex-date. Note which columns are read at which k:
#   Price  -> only k = -1 and k = +1,+2,+3        (NEVER k = 0)
#   Close  -> any k                               (adjusted series, safe on the ex-date row)
PANEL = f"""
WITH div_dedup AS (
  SELECT c.ticker, c.exright_date AS ex_date, c.value_per_share,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `{BQ_PROJECT}.tav2_bq.corporate_action` AS c
  WHERE c.event_code = 'DIV' AND c.event_status = 'executed'
    AND c.exright_date IS NOT NULL AND c.value_per_share > 0
),
ev AS (
  SELECT ticker, ex_date, SUM(value_per_share) AS div_total
  FROM div_dedup WHERE rn = 1
  GROUP BY ticker, ex_date
  HAVING ex_date BETWEEN DATE '{EX_MIN}' AND DATE '{EX_MAX}'
),
px AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume, t.PE, t.PB, t.ICB_Code,
         SAFE_DIVIDE(t.Close, LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret,
         ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time) AS si
  FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
  WHERE t.time >= DATE '{PANEL_START}'
    AND t.Close IS NOT NULL AND t.Close > 0
    AND t.ticker IN (SELECT DISTINCT ticker FROM ev)
),
anchor AS (
  SELECT e.ticker, e.ex_date, e.div_total, p.si AS si0
  FROM ev AS e
  JOIN px AS p ON p.ticker = e.ticker AND p.time = e.ex_date
),
w AS (
  SELECT a.ticker, a.ex_date, a.div_total, p.si - a.si0 AS k,
         p.time AS dt, p.Close, p.Price, p.Volume, p.PE, p.PB, p.ICB_Code, p.ret
  FROM anchor AS a
  JOIN px AS p ON p.ticker = a.ticker AND p.si BETWEEN a.si0 - 260 AND a.si0 + 62
)
SELECT
  ticker, ex_date, ANY_VALUE(div_total) AS div_total,
  MAX(IF(k = -250, Close, NULL)) AS c_m250,
  MAX(IF(k = -250, dt,    NULL)) AS d_m250,
  MAX(IF(k = -230, Close, NULL)) AS c_m230,
  MAX(IF(k = -230, dt,    NULL)) AS d_m230,
  MAX(IF(k = -126, Close, NULL)) AS c_m126,
  MAX(IF(k = -41,  Close, NULL)) AS c_m41,
  MAX(IF(k = -40,  Close, NULL)) AS c_m40,
  MAX(IF(k = -40,  dt,    NULL)) AS d_m40,
  MAX(IF(k = -21,  Close, NULL)) AS c_m21,
  MAX(IF(k = -21,  dt,    NULL)) AS d_m21,
  MAX(IF(k = -20,  Close, NULL)) AS c_m20,
  MAX(IF(k = -20,  dt,    NULL)) AS d_m20,
  MAX(IF(k = -1,   Close, NULL)) AS c_m1,
  MAX(IF(k = -1,   Price, NULL)) AS p_m1,
  MAX(IF(k = -1,   dt,    NULL)) AS d_m1,
  MAX(IF(k = -1,   PE,    NULL)) AS pe_m1,
  MAX(IF(k = -1,   PB,    NULL)) AS pb_m1,
  MAX(IF(k = -1,   ICB_Code, NULL)) AS icb,
  MAX(IF(k = 0,    Close, NULL)) AS c_0,
  MAX(IF(k = 0,    dt,    NULL)) AS d_0,
  MAX(IF(k = 0,    Volume,NULL)) AS v_0,
  MAX(IF(k = 1,    Close, NULL)) AS c_1,
  MAX(IF(k = 1,    dt,    NULL)) AS d_1,
  MAX(IF(k = 1,    Price, NULL)) AS p_1,
  MAX(IF(k = 2,    Close, NULL)) AS c_2,
  MAX(IF(k = 2,    Price, NULL)) AS p_2,
  MAX(IF(k = 3,    Close, NULL)) AS c_3,
  MAX(IF(k = 3,    Price, NULL)) AS p_3,
  MAX(IF(k = 5,    Close, NULL)) AS c_5,
  MAX(IF(k = 5,    dt,    NULL)) AS d_5,
  MAX(IF(k = 10,   Close, NULL)) AS c_10,
  MAX(IF(k = 10,   dt,    NULL)) AS d_10,
  MAX(IF(k = 20,   Close, NULL)) AS c_20,
  MAX(IF(k = 20,   dt,    NULL)) AS d_20,
  MAX(IF(k = 60,   Close, NULL)) AS c_60,
  MAX(IF(k = 60,   dt,    NULL)) AS d_60,
  AVG(IF(k BETWEEN -60 AND -6, Volume, NULL))          AS advol_60,
  AVG(IF(k BETWEEN -60 AND -6, Volume * Price, NULL))  AS advnd_60,
  AVG(IF(k BETWEEN  1 AND  5,  Volume, NULL))          AS vol_p1_5,
  STDDEV(IF(k BETWEEN -60 AND -1, ret, NULL))          AS rvol_60,
  COUNTIF(k BETWEEN -60 AND -1)                        AS n_pre_sessions
FROM w
GROUP BY ticker, ex_date
ORDER BY ticker, ex_date
"""

VNINDEX = f"""
SELECT t.time AS dt, t.Close AS c
FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
WHERE t.ticker = 'VNINDEX' AND t.time >= DATE '{PANEL_START}' AND t.Close > 0
ORDER BY t.time
"""

# Equal-weighted point-in-time universe return. Membership is required at BOTH ends of the
# return so a name entering/leaving the universe cannot manufacture a return.
EWUNIV = f"""
WITH u AS (
  SELECT up.time, up.ticker
  FROM `{BQ_PROJECT}.tav2_mike.universe_pit` AS up
  WHERE up.in_universe AND up.time >= DATE '{PANEL_START}'
),
p AS (
  SELECT t.ticker, t.time, t.Close,
         LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_prev,
         LAG(t.time)  OVER (PARTITION BY t.ticker ORDER BY t.time) AS t_prev
  FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
  WHERE t.time >= DATE '{PANEL_START}' AND t.Close IS NOT NULL AND t.Close > 0
),
r AS (
  SELECT p.time AS dt, p.ticker, p.Close / p.c_prev - 1 AS ret
  FROM p
  JOIN u        ON u.ticker = p.ticker AND u.time = p.time
  JOIN u AS upv ON upv.ticker = p.ticker AND upv.time = p.t_prev
  WHERE p.c_prev IS NOT NULL AND p.c_prev > 0
)
SELECT dt,
       AVG(ret) AS ew_ret_raw,
       AVG(IF(ABS(ret) <= 0.5, ret, NULL)) AS ew_ret,
       COUNT(*) AS n_names,
       COUNTIF(ABS(ret) > 0.5) AS n_impossible
FROM r GROUP BY dt ORDER BY dt
"""

# PIT universe membership of each event ticker on its own ex-date.
UNIV_AT_EX = f"""
WITH div_dedup AS (
  SELECT c.ticker, c.exright_date AS ex_date,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `{BQ_PROJECT}.tav2_bq.corporate_action` AS c
  WHERE c.event_code = 'DIV' AND c.event_status = 'executed'
    AND c.exright_date IS NOT NULL AND c.value_per_share > 0
),
ev AS (
  SELECT DISTINCT ticker, ex_date FROM div_dedup WHERE rn = 1
  AND ex_date BETWEEN DATE '{EX_MIN}' AND DATE '{EX_MAX}'
)
SELECT e.ticker, e.ex_date,
       IFNULL(up.in_universe, FALSE) AS in_universe,
       IFNULL(up.backfilled, FALSE)  AS backfilled
FROM ev AS e
LEFT JOIN `{BQ_PROJECT}.tav2_mike.universe_pit` AS up
  ON up.ticker = e.ticker AND up.time = e.ex_date
"""

# Shares outstanding, point-in-time: latest quarter whose Release_Date is on or before T-1.
# Release_Date (not `time`) is the only field that says when the number could have been known.
OSHARES = f"""
WITH div_dedup AS (
  SELECT c.ticker, c.exright_date AS ex_date,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `{BQ_PROJECT}.tav2_bq.corporate_action` AS c
  WHERE c.event_code = 'DIV' AND c.event_status = 'executed'
    AND c.exright_date IS NOT NULL AND c.value_per_share > 0
),
ev AS (
  SELECT DISTINCT ticker, ex_date FROM div_dedup WHERE rn = 1
  AND ex_date BETWEEN DATE '{EX_MIN}' AND DATE '{EX_MAX}'
),
j AS (
  SELECT e.ticker, e.ex_date, tf.OShares, tf.Release_Date,
         ROW_NUMBER() OVER (PARTITION BY e.ticker, e.ex_date
                            ORDER BY tf.Release_Date DESC) AS rn
  FROM ev AS e
  JOIN `{BQ_PROJECT}.tav2_bq.ticker_financial` AS tf
    ON tf.ticker = e.ticker
   AND tf.Release_Date IS NOT NULL
   AND tf.Release_Date < e.ex_date
   AND tf.OShares IS NOT NULL AND tf.OShares > 0
)
SELECT ticker, ex_date, OShares AS oshares, Release_Date AS oshares_release
FROM j WHERE rn = 1
"""


# ------------------------------------------------------------------------------------------
def load_ledger() -> list[dict]:
    path = os.path.join(HERE, "out", "event_ledger.csv.gz")
    with gzip.open(path, "rt", newline="") as fh:
        return list(csv.DictReader(fh))


def build_contamination(ledger: list[dict]):
    """Per-ticker sorted lists of the other-event dates the prereg's X1a / X1b rules need.

    X1a = price-adjusting ISSUANCE (stock dividend / bonus / rights).  X1b = any OTHER
    (ticker, ex-date) cash-dividend pair.  Both are taken from the ledger, so the exclusion
    uses exactly the same event definition the study population does.
    """
    iss_adj = defaultdict(list)
    div_dates = defaultdict(set)
    for r in ledger:
        if r["actionable"] != "1" or not r["exright_date"]:
            continue
        ex = d(r["exright_date"])
        if r["event_family"] == "ISSUANCE" and r["event_subtype"] in (
                "STOCK_DIVIDEND", "BONUS", "RIGHTS"):
            iss_adj[r["ticker"]].append(ex)
        elif r["event_family"] == "CASH_DIVIDEND":
            div_dates[r["ticker"]].add(ex)
    return ({k: sorted(v) for k, v in iss_adj.items()},
            {k: sorted(v) for k, v in div_dates.items()})


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    log = print

    log("[1/6] ledger -> contamination index")
    ledger = load_ledger()
    iss_adj, div_dates = build_contamination(ledger)
    # canonical dividend totals, for the selfcheck cross-check against SQL
    led_div = {}
    for r in ledger:
        if r["event_family"] == "CASH_DIVIDEND" and r["actionable"] == "1" and r["exright_date"]:
            led_div[(r["ticker"], r["exright_date"])] = float(r["div_total_on_exdate"])
    log(f"      ledger rows={len(ledger)}  actionable DIV (ticker,ex) pairs={len(led_div)}")

    log("[2/6] BQ: dividend events (SQL dedup, same economic key as Sprint 1)")
    ev = bq_csv(DIV_EVENTS, "q1_div_events")
    log(f"      events {EX_MIN}..{EX_MAX}: {len(ev)}")

    log("[3/6] BQ: event window panel (server-side; Price never read at k=0)")
    panel = bq_csv(PANEL, "q2_panel")
    log(f"      panel rows (events with a session ON the ex-date): {len(panel)}")

    log("[4/6] BQ: VNINDEX + EW universe_pit benchmark + PIT membership + PIT OShares")
    vni = bq_csv(VNINDEX, "q3_vnindex")
    ew = bq_csv(EWUNIV, "q4_ew_universe")
    univ = bq_csv(UNIV_AT_EX, "q5_univ_at_ex")
    osh = bq_csv(OSHARES, "q6_oshares_pit")
    log(f"      vnindex sessions={len(vni)}  ew sessions={len(ew)}  "
        f"univ rows={len(univ)}  oshares rows={len(osh)}")

    log("[5/6] assemble")
    univ_map = {(r["ticker"], r["ex_date"]): r for r in univ}
    osh_map = {(r["ticker"], r["ex_date"]): r for r in osh}
    sql_div = {(r["ticker"], r["ex_date"]): float(r["div_total"]) for r in ev}

    rows = []
    for r in panel:
        key = (r["ticker"], r["ex_date"])
        ex = d(r["ex_date"])
        tk = r["ticker"]
        # --- contamination (prereg §3) -------------------------------------------------
        def near(dates, lo_days, hi_days):
            lo, hi = ex - timedelta(days=lo_days), ex + timedelta(days=hi_days)
            return [x for x in dates if lo <= x <= hi]
        n_iss21 = len(near(iss_adj.get(tk, []), 21, 21))
        n_iss90 = len(near(iss_adj.get(tk, []), 21, 90))
        n_iss5 = len(near(iss_adj.get(tk, []), 5, 5))
        other_div = [x for x in div_dates.get(tk, []) if x != ex]
        n_div21 = len(near(other_div, 21, 21))
        n_div90 = len(near(other_div, 21, 90))
        n_div5 = len(near(other_div, 5, 5))

        u = univ_map.get(key, {})
        o = osh_map.get(key, {})
        out = {
            "ticker": tk, "ex_date": r["ex_date"],
            "div_total": f(r["div_total"]),
            "div_ledger": led_div.get(key),
            "div_sql": sql_div.get(key),
            "in_universe_pit": 1 if u.get("in_universe") == "true" else 0,
            "univ_backfilled": 1 if u.get("backfilled") == "true" else 0,
            "oshares": f(o.get("oshares")), "oshares_release": o.get("oshares_release", ""),
            "n_iss_adj_21": n_iss21, "n_iss_adj_90": n_iss90, "n_iss_adj_5": n_iss5,
            "n_other_div_21": n_div21, "n_other_div_90": n_div90, "n_other_div_5": n_div5,
        }
        for c in ("c_m126", "c_m41", "c_m40", "c_m21", "c_m20", "c_m1", "p_m1", "pe_m1",
                  "pb_m1", "c_0", "v_0", "c_1", "p_1", "c_2", "p_2", "c_3", "p_3",
                  "c_5", "c_10", "c_20", "c_60", "c_m250", "c_m230", "advol_60", "advnd_60", "vol_p1_5",
                  "rvol_60", "n_pre_sessions"):
            out[c] = f(r.get(c))
        for c in ("d_m250", "d_m230", "d_m40", "d_m21", "d_m20", "d_m1", "d_0", "d_1",
                  "d_5", "d_10", "d_20", "d_60"):
            out[c] = r.get(c) or ""
        out["icb"] = r.get("icb") or ""
        rows.append(out)

    def dump(name, recs, fields=None):
        path = os.path.join(OUT, name)
        fields = fields or list(recs[0].keys())
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(recs)
        return path

    dump("event_panel.csv", rows)
    dump("vnindex.csv", [{"dt": r["dt"], "c": r["c"]} for r in vni])
    dump("ew_universe.csv", [{"dt": r["dt"], "ew_ret": r["ew_ret"],
                              "ew_ret_raw": r["ew_ret_raw"], "n_names": r["n_names"],
                              "n_impossible": r["n_impossible"]} for r in ew])

    log("[6/6] summary")
    n_sql_only = len(sql_div) - sum(1 for k in sql_div if k in led_div)
    n_led_only = len(led_div) - sum(1 for k in led_div if k in sql_div)
    summary = {
        "ex_date_range": [EX_MIN, EX_MAX],
        "n_events_sql": len(ev),
        "n_events_with_exdate_session": len(panel),
        "n_ledger_actionable_div_pairs_all_years": len(led_div),
        "n_sql_pairs_not_in_ledger": n_sql_only,
        "n_ledger_pairs_not_in_sql_same_window": n_led_only,
        "n_in_universe_pit": sum(r["in_universe_pit"] for r in rows),
        "n_univ_backfilled": sum(r["univ_backfilled"] for r in rows),
        "n_oshares_matched": sum(1 for r in rows if r["oshares"]),
        "oshares_coverage_pct": round(
            100.0 * sum(1 for r in rows if r["oshares"]) / max(len(rows), 1), 2),
        "vnindex_sessions": len(vni),
        "ew_sessions": len(ew),
        "ew_impossible_returns_total": sum(int(r["n_impossible"]) for r in ew),
        "ew_median_names": sorted(int(r["n_names"]) for r in ew)[len(ew) // 2] if ew else 0,
    }
    with open(os.path.join(OUT, "build_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    log(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
