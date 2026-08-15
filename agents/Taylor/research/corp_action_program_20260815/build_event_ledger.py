#!/usr/bin/env python3
"""build_event_ledger.py — one row per deduplicated ECONOMIC event, with full raw lineage.

READ-ONLY against BigQuery. Writes only into ./out/.
Run:  python3 build_event_ledger.py

Outputs
  out/event_ledger.csv.gz        full ledger (NOT committed - rebuild with this script)
  out/event_ledger_sample.csv    200-row spot-check sample carrying lineage
  out/ledger_summary.json        every count quoted in SPRINT1.md
  out/iss_ratio_title_vs_column.csv  rows where the title ratio and the numeric column disagree
  out/dedup_dropped_sample.csv   rows the dedup dropped, with the id that survived
  out/vintage_asof_<max_ingested_at>.csv.gz  id -> hash of mutable fields (amendment tracking)

DEDUP POLICY (the one judgement call in this file, stated so it can be attacked)
------------------------------------------------------------------------------
A naive `(ticker, exright_date, event_code)` key destroys real events: measured on this table it
collapses 404 DIV groups / 829 rows, but inspection shows those are genuine dividend TRANCHES --
PHN went ex on 2026-06-05 for BOTH "2025 Đợt 3" (1.000đ) and "2026 Đợt 1" (1.000đ); identical
value, different entitlement, both really paid. Keying on the tranche
`(ticker, exright_date, dividend_year, dividend_stage_vi)` leaves only 6 residual duplicate
groups (13 rows, 0,08% of DIV). So: dedup on the ECONOMIC key, then SUM across tranches to get
the ex-date total. Summing raw rows without the tranche key would double-count the 6 residual
groups; deduping on ticker+date alone would silently halve PHN's dividend.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ca_lib import TABLE, bq, classify, is_price_adjusting, num, title_ratio  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# Every column the ledger derives from. Pulled once; no second query can disagree with the first.
PULL_SQL = f"""
SELECT id, ticker, organ_code, event_code, event_status, issue_status_vi,
       event_title_vi, event_description_vi,
       public_date, exright_date, record_date, issue_date, payout_date, listing_date,
       effective_date, value_per_share, exercise_ratio, ref_price,
       dividend_year, dividend_stage_vi, issue_method_code, issue_method_name_vi,
       issue_volumn, total_value, shares_delta, shares_total_after, icb_code_lv1,
       CAST(ingested_at AS STRING) ingested_at,
       CASE WHEN REGEXP_CONTAINS(id, r'^[0-9a-f]{{24}}$')
            THEN CAST(DATE(TIMESTAMP_SECONDS(CAST(CONCAT('0x',SUBSTR(id,1,8)) AS INT64))) AS STRING)
            END id_created_date
FROM {TABLE}
"""

# Mutable payload of a row. Hashing it now lets a re-run on a later date report exactly which
# events the vendor rewrote -- the only way to turn "amendments happen" into a measured rate.
VINTAGE_FIELDS = [
    "event_status", "public_date", "exright_date", "record_date", "payout_date", "effective_date",
    "value_per_share", "exercise_ratio", "issue_volumn", "shares_delta", "shares_total_after",
    "issue_method_code", "dividend_year", "dividend_stage_vi",
]

LEDGER_COLS = [
    # lineage
    "event_uid", "src_ids", "n_raw_rows", "survivor_id", "dropped_ids",
    # identity
    "ticker", "organ_code", "icb_code_lv1", "event_family", "event_subtype",
    "taxonomy_rule", "taxonomy_evidence",
    # dates
    "public_date", "exright_date", "record_date", "issue_date", "payout_date", "listing_date",
    "effective_date", "id_created_date", "ingested_at",
    # status
    "event_status", "issue_status_vi",
    # knowledge time
    "known_date", "known_date_confidence", "known_date_lead_days", "fleet_known_from",
    # values
    "value_per_share", "div_total_on_exdate", "exercise_ratio", "issue_volumn", "total_value",
    "shares_delta", "shares_total_after", "ref_price",
    # flags
    "is_price_adjusting", "flag_cancelled", "flag_announced_only", "flag_no_exright",
    "flag_div_no_value", "flag_ratio_unusable", "flag_unknown_subtype",
    "flag_pit_public_not_before_ex", "flag_same_exdate_other_family", "flag_residual_dup",
    "actionable",
]

# The first day this fleet held ANY row of this table. No backtest run by us can honestly claim
# knowledge of a corporate action before this date, whatever `public_date` says.
FLEET_KNOWN_FROM = "2026-08-12"


def _d(v):
    """Normalise a BQ value to a plain string ('' for NULL) for stable hashing/CSV."""
    return "" if v is None else str(v)


def economic_key(r: dict) -> tuple:
    """The key that identifies ONE economic event. See the dedup policy in the module docstring."""
    code = r["event_code"]
    if code == "DIV":
        return ("DIV", r["ticker"], _d(r["exright_date"]), _d(r["dividend_year"]),
                _d(r["dividend_stage_vi"]))
    if code == "ISS":
        return ("ISS", r["ticker"], _d(r["exright_date"]), _d(r["issue_method_code"]),
                _d(r["exercise_ratio"]), _d(r["issue_volumn"]))
    # Listing/suspension/move/M&A: keyed on the date they take effect plus the share numbers,
    # which is what makes two such rows the same event.
    return (code, r["ticker"], _d(r["effective_date"]) or _d(r["public_date"]),
            _d(r["shares_delta"]), _d(r["shares_total_after"]))


def pick_survivor(rows: list[dict]) -> dict:
    """Latest `public_date`, then latest vendor record creation, then id — fully deterministic.

    Latest-public_date is the amendment convention: when the vendor writes the same economic
    event twice, the later publication supersedes. Determinism matters more than cleverness here
    because the ledger must rebuild byte-identically for the selfcheck to mean anything.
    """
    return sorted(rows, key=lambda r: (_d(r["public_date"]), _d(r["id_created_date"]), r["id"]))[-1]


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    print("[ledger] pulling raw rows ...", flush=True)
    raw = bq(PULL_SQL)
    print(f"[ledger] {len(raw)} raw rows", flush=True)

    # --- group into economic events ----------------------------------------------------------
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in raw:
        groups[economic_key(r)].append(r)

    # Tickers/dates where an executed DIV and an executed ISS share an ex-date: the ex-day move
    # is then not attributable to either alone.
    fam_on_date: dict[tuple, set] = defaultdict(set)
    for r in raw:
        if r["exright_date"] and r["event_status"] == "executed":
            fam_on_date[(r["ticker"], r["exright_date"])].add(r["event_code"])

    ledger: list[dict] = []
    dropped_rows: list[dict] = []
    confusion: list[dict] = []
    ratio_checked: Counter = Counter()

    for key, rows in groups.items():
        surv = pick_survivor(rows)
        dropped = [r for r in rows if r["id"] != surv["id"]]
        cls = classify(surv)
        ex = surv["exright_date"]
        pub = surv["public_date"]

        lead = None
        if ex and pub:
            from datetime import date
            y1, m1, d1 = map(int, pub.split("-"))
            y2, m2, d2 = map(int, ex.split("-"))
            lead = (date(y2, m2, d2) - date(y1, m1, d1)).days

        # Knowledge-time grading. Nothing here is stronger than WEAK, on purpose: the table is
        # rewritten in place with no vintage history, so "public_date was always this value"
        # is an assumption, not a measurement. See SPRINT1.md §5.
        if not pub:
            conf = "UNUSABLE_NO_PUBLIC_DATE"
        elif ex and lead is not None and lead <= 0:
            conf = "UNUSABLE_NOT_BEFORE_EVENT"
        else:
            conf = "WEAK_UNVERIFIED_VINTAGE"

        subtype = cls["subtype"]
        cancelled = surv["event_status"] == "not_executed"
        announced = surv["event_status"] == "announced"
        # `num()` is mandatory here: bq's JSON renders numerics as strings, so a bare `== 0`
        # silently never matches (measured: caught 48 of ~3.900 unusable ratios before the fix).
        ratio_val = num(surv["exercise_ratio"])
        vps_val = num(surv["value_per_share"])
        ratio_unusable = surv["event_code"] == "ISS" and (ratio_val is None or ratio_val == 0.0)
        div_no_value = surv["event_code"] == "DIV" and (vps_val is None or vps_val <= 0)
        codes_today = fam_on_date.get((surv["ticker"], ex), set()) if ex else set()

        actionable = bool(
            surv["event_status"] == "executed" and ex
            and not (surv["event_code"] == "DIV" and div_no_value)
            and not (surv["event_code"] == "ISS" and subtype == "UNKNOWN")
        )

        uid = hashlib.sha1("|".join(str(k) for k in key).encode()).hexdigest()[:16]
        ledger.append({
            "event_uid": uid,
            "src_ids": ";".join(sorted(r["id"] for r in rows)),
            "n_raw_rows": len(rows),
            "survivor_id": surv["id"],
            "dropped_ids": ";".join(sorted(r["id"] for r in dropped)),
            "ticker": surv["ticker"], "organ_code": _d(surv["organ_code"]),
            "icb_code_lv1": _d(surv["icb_code_lv1"]),
            "event_family": cls["family"], "event_subtype": subtype,
            "taxonomy_rule": cls["rule"], "taxonomy_evidence": cls["evidence"],
            "public_date": _d(pub), "exright_date": _d(ex),
            "record_date": _d(surv["record_date"]), "issue_date": _d(surv["issue_date"]),
            "payout_date": _d(surv["payout_date"]), "listing_date": _d(surv["listing_date"]),
            "effective_date": _d(surv["effective_date"]),
            "id_created_date": _d(surv["id_created_date"]), "ingested_at": _d(surv["ingested_at"]),
            "event_status": _d(surv["event_status"]), "issue_status_vi": _d(surv["issue_status_vi"]),
            "known_date": _d(pub), "known_date_confidence": conf,
            "known_date_lead_days": "" if lead is None else lead,
            "fleet_known_from": FLEET_KNOWN_FROM,
            "value_per_share": _d(surv["value_per_share"]),
            "div_total_on_exdate": "",          # filled in the second pass below
            "exercise_ratio": _d(surv["exercise_ratio"]),
            "issue_volumn": _d(surv["issue_volumn"]), "total_value": _d(surv["total_value"]),
            "shares_delta": _d(surv["shares_delta"]),
            "shares_total_after": _d(surv["shares_total_after"]),
            "ref_price": _d(surv["ref_price"]),
            "is_price_adjusting": int(is_price_adjusting(surv)),
            "flag_cancelled": int(cancelled), "flag_announced_only": int(announced),
            "flag_no_exright": int(ex is None), "flag_div_no_value": int(div_no_value),
            "flag_ratio_unusable": int(ratio_unusable),
            "flag_unknown_subtype": int(subtype == "UNKNOWN"),
            "flag_pit_public_not_before_ex": int(conf.startswith("UNUSABLE")),
            "flag_same_exdate_other_family": int(len(codes_today) > 1),
            "flag_residual_dup": int(len(rows) > 1),
            "actionable": int(actionable),
        })

        for r in dropped:
            dropped_rows.append({
                "event_uid": uid, "dropped_id": r["id"], "survivor_id": surv["id"],
                "ticker": r["ticker"], "event_code": r["event_code"],
                "exright_date": _d(r["exright_date"]), "public_date": _d(r["public_date"]),
                "value_per_share": _d(r["value_per_share"]),
                "exercise_ratio": _d(r["exercise_ratio"]),
                "dividend_stage_vi": _d(r["dividend_stage_vi"]),
                "event_title_vi": _d(r["event_title_vi"])[:120],
            })

        # Independent cross-check on exercise_ratio: the ratio the vendor wrote into the title
        # text vs the ratio it wrote into the numeric column. Disagreement means one of the two
        # is wrong and neither can be trusted for that event.
        if surv["event_code"] == "ISS":
            tr = title_ratio(surv)
            if tr is not None:
                # Tolerance = the title's own precision. It prints one decimal of a percent, so
                # 7,15% is rendered "7.2%" and an exact comparison flags 1.132 false conflicts
                # that are pure rounding. +/-0,05pp is the tightest HONEST tolerance.
                agree = ratio_val is not None and abs(tr - ratio_val) <= 0.0005 + 1e-9
                if not agree:
                    confusion.append({
                        "survivor_id": surv["id"], "ticker": surv["ticker"],
                        "exright_date": _d(ex), "subtype": subtype,
                        "issue_method_code": _d(surv["issue_method_code"]),
                        "exercise_ratio_column": _d(surv["exercise_ratio"]),
                        "ratio_from_title": tr,
                        "event_title_vi": _d(surv["event_title_vi"])[:160],
                    })
                ratio_checked[agree] += 1

    # --- second pass: cash actually going ex on a given ticker-date, summed over TRANCHES -----
    div_tot: dict[tuple, float] = defaultdict(float)
    for e in ledger:
        if e["event_family"] == "CASH_DIVIDEND" and e["exright_date"] and not e["flag_cancelled"] \
                and num(e["value_per_share"]):
            div_tot[(e["ticker"], e["exright_date"])] += num(e["value_per_share"])
    for e in ledger:
        if e["event_family"] == "CASH_DIVIDEND" and e["exright_date"]:
            e["div_total_on_exdate"] = round(div_tot.get((e["ticker"], e["exright_date"]), 0.0), 6)

    ledger.sort(key=lambda e: (e["ticker"], e["exright_date"] or e["public_date"], e["event_uid"]))

    # --- write -------------------------------------------------------------------------------
    lpath = os.path.join(OUT, "event_ledger.csv.gz")
    with gzip.open(lpath, "wt", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LEDGER_COLS)
        w.writeheader()
        w.writerows(ledger)

    # Sample stratified across subtypes so the spot-check is not all cash dividends.
    by_sub: dict[str, list] = defaultdict(list)
    for e in ledger:
        by_sub[e["event_subtype"]].append(e)
    sample = []
    for sub in sorted(by_sub):
        rows_s = sorted(by_sub[sub], key=lambda e: e["event_uid"])
        step = max(1, len(rows_s) // 15)
        sample.extend(rows_s[::step][:15])
    with open(os.path.join(OUT, "event_ledger_sample.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LEDGER_COLS)
        w.writeheader()
        w.writerows(sample)

    with open(os.path.join(OUT, "dedup_dropped_sample.csv"), "w", newline="") as fh:
        cols = list(dropped_rows[0].keys()) if dropped_rows else ["event_uid"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(sorted(dropped_rows, key=lambda r: r["event_uid"])[:400])

    with open(os.path.join(OUT, "iss_ratio_title_vs_column.csv"), "w", newline="") as fh:
        cols = list(confusion[0].keys()) if confusion else ["survivor_id"]
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(confusion)

    # Vintage snapshot for future amendment measurement. Stamped with the table's own newest
    # `ingested_at` rather than the wall clock, so a re-run on unchanged data reproduces the same
    # filename and the artifact is derived from the data, not from when someone happened to run it.
    asof = max((r["ingested_at"] or "")[:10] for r in raw).replace("-", "")
    with gzip.open(os.path.join(OUT, f"vintage_asof_{asof}.csv.gz"), "wt", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "payload_sha1", "public_date", "event_status"])
        for r in sorted(raw, key=lambda x: x["id"]):
            blob = "|".join(_d(r[f]) for f in VINTAGE_FIELDS)
            w.writerow([r["id"], hashlib.sha1(blob.encode()).hexdigest(),
                        _d(r["public_date"]), _d(r["event_status"])])

    # --- summary -----------------------------------------------------------------------------
    sub_ct = Counter(e["event_subtype"] for e in ledger)
    rule_ct = Counter(e["taxonomy_rule"] for e in ledger)
    conf_ct = Counter(e["known_date_confidence"] for e in ledger)
    div = [e for e in ledger if e["event_family"] == "CASH_DIVIDEND"]
    summary = {
        "generated_from_table": TABLE,
        "n_raw_rows": len(raw),
        "n_ledger_events": len(ledger),
        "n_rows_collapsed_by_dedup": len(raw) - len(ledger),
        "n_events_with_multiple_raw_rows": sum(1 for e in ledger if e["n_raw_rows"] > 1),
        "subtype_counts": dict(sub_ct.most_common()),
        "taxonomy_rule_counts": dict(rule_ct.most_common()),
        "taxonomy_unknown_pct": round(100 * sub_ct.get("UNKNOWN", 0) / max(1, len(ledger)), 3),
        "iss_ratio_title_vs_column": {
            "n_checked": sum(ratio_checked.values()),
            "n_agree": ratio_checked[True],
            "n_disagree": ratio_checked[False],
            "pct_agree": round(100 * ratio_checked[True] / max(1, sum(ratio_checked.values())), 3),
            "note": ("event_title_vi is mechanically built from issue_method_name_vi, so it "
                     "CANNOT corroborate the subtype label; only the embedded ratio is an "
                     "independent read."),
        },
        "known_date_confidence_counts": dict(conf_ct.most_common()),
        "fleet_known_from": FLEET_KNOWN_FROM,
        "cash_dividend": {
            "n_events": len(div),
            "n_executed": sum(1 for e in div if e["event_status"] == "executed"),
            "n_cancelled": sum(1 for e in div if e["flag_cancelled"]),
            "n_announced_only": sum(1 for e in div if e["flag_announced_only"]),
            "n_actionable": sum(1 for e in div if e["actionable"]),
            "n_no_exright": sum(1 for e in div if e["flag_no_exright"]),
            "n_no_value": sum(1 for e in div if e["flag_div_no_value"]),
            "n_same_exdate_other_family": sum(1 for e in div
                                              if e["flag_same_exdate_other_family"]),
            "n_pit_unusable": sum(1 for e in div if e["flag_pit_public_not_before_ex"]),
            "n_distinct_ticker_exdate": len({(e["ticker"], e["exright_date"]) for e in div
                                             if e["exright_date"]}),
        },
        "issuance": {
            "n_events": sum(1 for e in ledger if e["event_family"] == "ISSUANCE"),
            "n_cancelled": sum(1 for e in ledger
                               if e["event_family"] == "ISSUANCE" and e["flag_cancelled"]),
            "n_unknown_subtype": sub_ct.get("UNKNOWN", 0),
            "n_ratio_unusable": sum(1 for e in ledger if e["flag_ratio_unusable"]),
        },
    }
    json.dump(summary, open(os.path.join(OUT, "ledger_summary.json"), "w"),
              indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2, ensure_ascii=False)[:2600])
    print(f"\n[ledger] {len(ledger)} events -> {lpath} "
          f"({os.path.getsize(lpath)/1e6:.2f} MB gz)")


if __name__ == "__main__":
    main()
