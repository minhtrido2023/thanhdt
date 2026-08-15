#!/usr/bin/env python3
"""selfcheck_sprint1.py — invariants for the taxonomy, the dedup and the no-look-ahead rules.

Run:  python3 selfcheck_sprint1.py      (requires out/event_ledger.csv.gz to exist)

Design rule followed here (coding_guidelines §23 corollary 1): assert on INVARIANTS — relations,
signs, fail-safe direction — not on live counts. The one exception is T8, which deliberately
asserts against BigQuery because "the fleet's earliest possible knowledge date" is precisely the
fact that must not drift silently; it is written to FAIL LOUD if the vendor backfills earlier.
"""
from __future__ import annotations

import csv
import gzip
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ca_lib import TABLE, bq, classify, is_price_adjusting, num  # noqa: E402

LEDGER = os.path.join(HERE, "out", "event_ledger.csv.gz")
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""), flush=True)


def load_ledger() -> list[dict]:
    with gzip.open(LEDGER, "rt") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    led = load_ledger()
    print(f"[selfcheck] ledger rows = {len(led)}\n")

    # ---- T1 taxonomy agrees with the production module it refines -------------------------
    # `corp_action_lib` is the LIVE binary answer used by oshares_live / dividend_adjusted_return.
    # If this sprint's finer taxonomy disagreed with it on even one row, one of the two is wrong
    # and the sprint's numbers could not be reconciled with production behaviour.
    sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
    try:
        import corp_action_lib as prod
        rows = bq(f"""SELECT event_code, issue_method_code, issue_method_name_vi
                      FROM {TABLE} WHERE event_code IN ('DIV','ISS')""")
        bad = [r for r in rows if is_price_adjusting(r) != prod.is_price_adjusting(r)]
        check("T1 taxonomy matches production corp_action_lib.is_price_adjusting",
              not bad, f"{len(bad)} disagreements over {len(rows)} rows")
    except ImportError as e:                                     # pragma: no cover
        check("T1 taxonomy matches production corp_action_lib", False, f"import failed: {e}")

    # ---- T2 every label is backed by a stored field value, never a guess -------------------
    unlabelled = [e for e in led if e["event_subtype"] != "UNKNOWN" and not e["taxonomy_evidence"]]
    check("T2a every non-UNKNOWN subtype carries evidence", not unlabelled,
          f"{len(unlabelled)} labelled rows with empty evidence")
    leaked = [e for e in led if e["event_subtype"] == "UNKNOWN" and e["taxonomy_rule"] != "unmatched"]
    check("T2b UNKNOWN is only ever produced by the 'unmatched' path", not leaked,
          f"{len(leaked)} UNKNOWN rows claiming a matched rule")

    # ---- T3 dedup is lossless: every raw id survives in exactly one ledger row -------------
    seen: dict[str, int] = defaultdict(int)
    for e in led:
        for i in e["src_ids"].split(";"):
            if i:
                seen[i] += 1
    dupe_ids = [i for i, n in seen.items() if n > 1]
    n_raw = int(bq(f"SELECT COUNT(*) n FROM {TABLE}")[0]["n"])
    check("T3a no raw id appears in two ledger events", not dupe_ids, f"{len(dupe_ids)} shared ids")
    check("T3b ledger lineage covers every raw row exactly once",
          len(seen) == n_raw, f"lineage ids={len(seen)} vs raw rows={n_raw}")
    check("T3c n_raw_rows sums to the raw row count",
          sum(int(e["n_raw_rows"]) for e in led) == n_raw,
          f"sum={sum(int(e['n_raw_rows']) for e in led)} vs {n_raw}")

    uids = [e["event_uid"] for e in led]
    check("T3d event_uid is unique", len(set(uids)) == len(uids),
          f"{len(uids) - len(set(uids))} collisions")

    # A survivor must be one of its own source rows — a survivor id not in src_ids would mean
    # the ledger row describes an event whose lineage does not contain it.
    orphan = [e for e in led if e["survivor_id"] not in e["src_ids"].split(";")]
    check("T3e survivor_id is always inside src_ids", not orphan, f"{len(orphan)} orphans")

    # ---- T4 cancelled events keep lineage but never enter the actionable sample ------------
    leaked_cancel = [e for e in led if e["flag_cancelled"] == "1" and e["actionable"] == "1"]
    check("T4a no not_executed event is actionable", not leaked_cancel,
          f"{len(leaked_cancel)} cancelled-but-actionable")
    n_cancel = sum(1 for e in led if e["flag_cancelled"] == "1")
    check("T4b cancelled events are still present (lineage kept, not dropped)", n_cancel > 0,
          f"{n_cancel} not_executed events retained")
    leaked_ann = [e for e in led if e["flag_announced_only"] == "1" and e["actionable"] == "1"]
    check("T4c announced-only events are not actionable", not leaked_ann,
          f"{len(leaked_ann)} announced-but-actionable")

    # ---- T5 no look-ahead in the knowledge-time grading ------------------------------------
    # The only thing that makes an announcement study safe is this: a row may NOT be graded
    # usable if its stated knowledge date does not strictly precede the event.
    bad_pit = [e for e in led if e["exright_date"] and e["known_date_lead_days"] != ""
               and int(e["known_date_lead_days"]) <= 0
               and not e["known_date_confidence"].startswith("UNUSABLE")]
    check("T5a lead<=0 is always graded UNUSABLE", not bad_pit,
          f"{len(bad_pit)} rows graded usable despite lead<=0")
    no_pub = [e for e in led if not e["known_date"]
              and e["known_date_confidence"] != "UNUSABLE_NO_PUBLIC_DATE"]
    check("T5b missing public_date is always graded UNUSABLE", not no_pub, f"{len(no_pub)} rows")
    over = [e for e in led if e["known_date_confidence"] not in
            ("WEAK_UNVERIFIED_VINTAGE", "UNUSABLE_NOT_BEFORE_EVENT", "UNUSABLE_NO_PUBLIC_DATE")]
    check("T5c no grade stronger than WEAK exists (vintage history absent)", not over,
          f"{len(over)} rows with an unexpected grade")

    # ---- T6 the dividend total is a sum over DEDUPLICATED tranches, recomputed here ---------
    recomputed: dict[tuple, float] = defaultdict(float)
    for e in led:
        if (e["event_family"] == "CASH_DIVIDEND" and e["exright_date"]
                and e["flag_cancelled"] != "1" and num(e["value_per_share"])):
            recomputed[(e["ticker"], e["exright_date"])] += num(e["value_per_share"])
    mism = [e for e in led if e["event_family"] == "CASH_DIVIDEND" and e["exright_date"]
            and abs(num(e["div_total_on_exdate"] or 0)
                    - recomputed.get((e["ticker"], e["exright_date"]), 0.0)) > 1e-6]
    check("T6a div_total_on_exdate recomputes independently", not mism, f"{len(mism)} mismatches")
    # And it must never be LESS than any single tranche it contains — the failure mode of a
    # ticker+date dedup that silently drops a tranche.
    short = [e for e in led if e["event_family"] == "CASH_DIVIDEND" and e["exright_date"]
             and e["flag_cancelled"] != "1" and num(e["value_per_share"])
             and num(e["div_total_on_exdate"] or 0) < num(e["value_per_share"]) - 1e-9]
    check("T6b ex-date total >= each of its tranches", not short, f"{len(short)} shortfalls")

    # ---- T7 actionable cash dividends are economically usable ------------------------------
    bad_val = [e for e in led if e["event_family"] == "CASH_DIVIDEND" and e["actionable"] == "1"
               and not (num(e["value_per_share"]) and num(e["value_per_share"]) > 0)]
    check("T7a actionable cash dividends have a positive per-share value", not bad_val,
          f"{len(bad_val)} actionable with null/zero value")
    no_ex = [e for e in led if e["actionable"] == "1" and not e["exright_date"]]
    check("T7b actionable events always have an ex-date", not no_ex, f"{len(no_ex)} without ex-date")
    unk_act = [e for e in led if e["actionable"] == "1" and e["flag_unknown_subtype"] == "1"]
    check("T7c UNKNOWN-subtype issuance never becomes actionable", not unk_act,
          f"{len(unk_act)} actionable UNKNOWN")

    # ---- T8 the fleet's knowledge horizon has not silently moved ---------------------------
    mn = bq(f"SELECT CAST(MIN(DATE(ingested_at)) AS STRING) d FROM {TABLE}")[0]["d"]
    declared = led[0]["fleet_known_from"] if led else ""
    check("T8 fleet_known_from equals the true earliest ingest date", mn == declared,
          f"BQ min ingest={mn} vs ledger declares {declared}")

    # ---- T9 dedup survivor selection is deterministic under input reordering ---------------
    from build_event_ledger import economic_key, pick_survivor
    probe = bq(f"""SELECT id, ticker, event_code, event_status, public_date, exright_date,
                          record_date, payout_date, effective_date, value_per_share,
                          exercise_ratio, issue_volumn, shares_delta, shares_total_after,
                          issue_method_code, dividend_year, dividend_stage_vi,
                          CASE WHEN REGEXP_CONTAINS(id, r'^[0-9a-f]{{24}}$')
                               THEN CAST(DATE(TIMESTAMP_SECONDS(
                                    CAST(CONCAT('0x',SUBSTR(id,1,8)) AS INT64))) AS STRING) END
                               id_created_date
                   FROM {TABLE} WHERE event_code='DIV' LIMIT 4000""")
    grp: dict[tuple, list] = defaultdict(list)
    for r in probe:
        grp[economic_key(r)].append(r)
    stable = all(pick_survivor(v)["id"] == pick_survivor(list(reversed(v)))["id"]
                 for v in grp.values())
    check("T9 survivor selection is order-independent", stable,
          f"{len(grp)} groups probed")

    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\n[selfcheck] {len(RESULTS) - n_fail}/{len(RESULTS)} PASS, {n_fail} FAIL")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
