#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
append_cctg_rate.py — append ONE new Big-4 CCTG (6-month tenor) rate anchor to the append-only
data/cctg_rate_vn_events.csv, read by cctg_rate_vn.py::cctg_events_df().

Sibling of append_deposit_rate.py (Big-4 12M term deposit) — SEPARATE series, SEPARATE CSV, never
merges into or overwrites the deposit CSV. Reuses append_deposit_rate.py's owner-group domain
logic (`_owner_group`, `SAME_OWNER_GROUPS`) by import rather than duplicating it — that logic is
already hardened through 8 rounds of adversarial review (see that file's docstring) and must not
drift into two copies that silently diverge.

Caller-identity gating (JOB_ID-bound, never a self-declared flag) is IDENTICAL in spirit to
append_deposit_rate.py: a dispatched agent may only use --source web_crosscheck_auto, --force is
human-only, --collected must be today. See that file's docstring for the full threat-model
rationale — not re-litigated here.

NEW requirement vs the Big-4 script (user directive, job Taylor_20261001_054108, weekly CCTG
mechanism): each --sources entry must carry its OWN cited `rate` (%, not just publisher/url/date).
The script mechanically checks that (a) all cited rates agree within CROSS_SOURCE_TOLERANCE_PP of
each other, and (b) --rate itself matches at least one cited source within FLOAT_EPS — so the
agent cannot synthesize a number no single source actually said. This is a genuine gap the Big-4
script does NOT close (its --sources schema has no rate field at all) — deliberately NOT
retrofitted into append_deposit_rate.py here to avoid touching an already-CONFIRMED production
guard outside the scope of this job; flagged for Mike/user to consider porting back separately.

Usage (human, interactive):
  python3 append_cctg_rate.py --rate 7.6 --effective 2026-10-08 --source manual_verify \
          --note "VietnamNet 08/10"

Usage (agent, web_crosscheck_auto):
  python3 append_cctg_rate.py --rate 7.6 --effective 2026-10-08 --source web_crosscheck_auto \
          --sources '[{"publisher":"VietnamNet","url":"https://vietnamnet.vn/...","date":"2026-10-06","rate":7.6},
                       {"publisher":"VnExpress","url":"https://vnexpress.net/...","date":"2026-10-07","rate":7.6}]' \
          --note "..."

Idempotent: re-running with an effective_date already present is skipped (unless --force).
"""
import argparse
import csv
import json
import os
import sys
import tempfile
from datetime import date, datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")  # coding_guidelines §16: never trust the host system TZ

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from append_deposit_rate import (  # noqa: E402 — reuse hardened domain logic, not a dup
    _owner_group, _check_urls_not_reused, _save_last_auto_urls)

CSV_PATH = os.path.join(HERE, "data", "cctg_rate_vn_events.csv")
# Own sidecar name, separate from append_deposit_rate.py's — two independent series, two
# independent reuse windows (coord job Taylor_20261001_061238 item 3; see
# append_deposit_rate.py's docstring for the full rationale). Derived from CSV_PATH's directory,
# same reasoning as that module's _last_auto_sources_path() — automatically test-isolated
# whenever CSV_PATH itself is monkeypatched to a tmpdir.
LAST_AUTO_SOURCES_NAME = "cctg_rate_last_auto_sources.json"


def _last_auto_sources_path():
    return os.path.join(os.path.dirname(CSV_PATH), LAST_AUTO_SOURCES_NAME)
HEADER = ["effective_date", "cctg_rate", "collected_date", "source", "note"]
VALID_SOURCES = {"manual_verify", "web_crosscheck_auto"}
SOURCES_REQUIRING_NOTE = {"web_crosscheck_auto"}
SOURCES_REQUIRING_STRUCTURED_SOURCES = {"web_crosscheck_auto"}
MIN_DISTINCT_OWNERS = 2
MAX_SOURCE_AGE_DAYS = 35
MAX_FUTURE_EFFECTIVE_DAYS = 2
NONINERT_DELTA_PP = 1.0  # same threshold family as append_deposit_rate.py's guard
CROSS_SOURCE_TOLERANCE_PP = 0.1  # per dispatch: sources must agree within 0.1pp of each other
FLOAT_EPS = 1e-6
RATE_MIN_PCT, RATE_MAX_PCT = 0.5, 30.0  # matches cctg_rate_vn.py's own sanity fence


def _read_rows():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("effective_date")]


def _valid_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def main():
    ap = argparse.ArgumentParser(description="Append one Big-4 CCTG 6M rate anchor (append-only).")
    ap.add_argument("--rate", type=float, required=True, help="Big-4 CCTG 6M rate, %%/yr (e.g. 7.6)")
    ap.add_argument("--effective", required=True, help="effective date YYYY-MM-DD")
    ap.add_argument("--source", required=True, help="one of: " + " | ".join(sorted(VALID_SOURCES)))
    ap.add_argument("--collected", default=None, help="real collection date YYYY-MM-DD (default: today)")
    ap.add_argument("--note", default="", help="free-text note")
    ap.add_argument("--sources", default=None,
                    help='JSON array of {"publisher","url","date","rate"} — REQUIRED for '
                         '--source web_crosscheck_auto')
    ap.add_argument("--force", action="store_true",
                    help="append even if effective_date exists / override delta guard. REFUSED "
                         "when JOB_ID env is set.")
    args = ap.parse_args()

    is_dispatched_agent = os.environ.get("JOB_ID") is not None
    if is_dispatched_agent and args.force:
        sys.exit("ERROR: --force is refused — JOB_ID is set (dispatched headless agent). "
                 "Human-only override; resolve escalations interactively.")
    if is_dispatched_agent and args.source != "web_crosscheck_auto":
        sys.exit(f"ERROR: --source '{args.source}' is refused — JOB_ID is set. A dispatched "
                 f"agent may ONLY use --source web_crosscheck_auto. Escalate instead.")

    try:
        eff = _valid_date(args.effective)
    except ValueError:
        sys.exit(f"ERROR: --effective '{args.effective}' is not YYYY-MM-DD")
    real_today = datetime.now(_ICT).date().isoformat()
    if is_dispatched_agent:
        eff_age_days = (eff - _valid_date(real_today)).days
        if eff_age_days > MAX_FUTURE_EFFECTIVE_DAYS or eff_age_days < -MAX_SOURCE_AGE_DAYS:
            sys.exit(f"ERROR: --effective '{args.effective}' is {eff_age_days} days from today "
                     f"({real_today}) — refused for a dispatched agent (max "
                     f"{MAX_FUTURE_EFFECTIVE_DAYS} days forward, {MAX_SOURCE_AGE_DAYS} days back).")
    collected = args.collected or real_today
    try:
        _valid_date(collected)
    except ValueError:
        sys.exit(f"ERROR: --collected '{collected}' is not YYYY-MM-DD")
    if is_dispatched_agent and collected != real_today:
        sys.exit(f"ERROR: --collected '{collected}' is refused — JOB_ID is set, --collected may "
                 f"ONLY be today ({real_today}).")
    if not (RATE_MIN_PCT < args.rate < RATE_MAX_PCT):
        sys.exit(f"ERROR: --rate {args.rate} out of sane range ({RATE_MIN_PCT}, {RATE_MAX_PCT}) "
                 f"— refuse to write")
    if args.source not in VALID_SOURCES:
        sys.exit(f"ERROR: --source '{args.source}' not in {sorted(VALID_SOURCES)}")
    if args.source in SOURCES_REQUIRING_NOTE and not args.note.strip():
        sys.exit(f"ERROR: --source {args.source} requires a non-empty --note.")

    # --- idempotency check FIRST, before the "not newer than last anchor" guard below (fix,
    # coord job Taylor_20261001_061238 item B1): a same-day re-run of the weekly cron used to hit
    # the "not newer" guard instead of this SKIP, because the FIRST run's own write becomes the
    # new last_date seen by the SECOND run — so re-running on an already-written date raised
    # "ERROR: not newer than the last anchor" (rc=1) instead of the intended idempotent SKIP
    # (rc=0), firing a false Winston escalate-question every time the cron (or a human) re-ran on
    # a day already confirmed. append_deposit_rate.py never had this ordering bug because it has
    # no equivalent "not newer" pre-check — only this CCTG script does.
    rows = _read_rows()
    existing = {r["effective_date"] for r in rows}
    if args.effective in existing and not args.force:
        print(f"SKIP: effective_date {args.effective} already present (use --force to override). "
              f"No write — CSV unchanged.")
        return 0

    # --- date-newer-than-last-anchor guard (fail fast, before writing a row cctg_events_df()
    # would reject on next load anyway — avoid leaving the CSV in a state nobody notices is broken
    # until the next unrelated reader crashes) ---
    import cctg_rate_vn
    existing_ev = cctg_rate_vn.cctg_events_df()
    last_date = existing_ev["time"].max().date()
    if eff <= last_date:
        sys.exit(f"ERROR: --effective {eff} is not newer than the last anchor {last_date} — "
                 f"cctg_events_df() treats this as corrupt/duplicate data and will raise loudly "
                 f"on next load. Refuse to write (typo'd year? duplicate run?).")

    # --- publisher independence + cross-source rate agreement: mechanically checked ---
    if args.source in SOURCES_REQUIRING_STRUCTURED_SOURCES:
        if not args.sources:
            sys.exit(f"ERROR: --source {args.source} requires --sources (JSON array of "
                     f">= {MIN_DISTINCT_OWNERS} {{publisher,url,date,rate}} entries).")
        try:
            sources = json.loads(args.sources)
        except json.JSONDecodeError as e:
            sys.exit(f"ERROR: --sources is not valid JSON: {e}")
        if not isinstance(sources, list) or len(sources) < MIN_DISTINCT_OWNERS:
            sys.exit(f"ERROR: --sources must be a JSON array with >= {MIN_DISTINCT_OWNERS} "
                     f"entries, got {sources!r}")
        urls = [s.get("url", "") for s in sources if isinstance(s, dict)]
        if len(urls) != len(sources) or not all(urls):
            sys.exit("ERROR: every --sources entry must be an object with a non-empty 'url'.")
        try:
            owner_groups = {_owner_group(u) for u in urls}
        except ValueError as e:
            sys.exit(f"ERROR: {e}")
        if len(owner_groups) < MIN_DISTINCT_OWNERS:
            sys.exit(f"ERROR: --sources resolve to only {len(owner_groups)} distinct owner "
                     f"group(s) ({sorted(owner_groups)}) — need >= {MIN_DISTINCT_OWNERS}. Refuse.")
        _check_urls_not_reused(urls, _last_auto_sources_path())
        today_d = _valid_date(real_today)
        src_rates = []
        for s in sources:
            raw_date = s.get("date", "")
            try:
                src_date = _valid_date(raw_date)
            except ValueError:
                sys.exit(f"ERROR: --sources entry has invalid/missing 'date' ('{raw_date}').")
            age_days = (today_d - src_date).days
            if age_days < 0 or age_days > MAX_SOURCE_AGE_DAYS:
                sys.exit(f"ERROR: --sources entry dated {raw_date} is {age_days} days from "
                         f"today ({real_today}) (max {MAX_SOURCE_AGE_DAYS}, or future) — too "
                         f"stale/invalid. Refuse to write.")
            raw_rate = s.get("rate", None)
            if raw_rate is None:
                sys.exit(f"ERROR: --sources entry missing 'rate' field (url={s.get('url')!r}) — "
                         f"each cited source must carry its own observed rate for cross-check.")
            try:
                src_rate = float(raw_rate)
            except (TypeError, ValueError):
                sys.exit(f"ERROR: --sources entry 'rate'={raw_rate!r} is not a number.")
            if not (RATE_MIN_PCT < src_rate < RATE_MAX_PCT):
                sys.exit(f"ERROR: --sources entry rate={src_rate} out of sane range "
                         f"({RATE_MIN_PCT}, {RATE_MAX_PCT}).")
            src_rates.append(src_rate)
        spread = max(src_rates) - min(src_rates)
        if spread > CROSS_SOURCE_TOLERANCE_PP + FLOAT_EPS:
            sys.exit(f"ERROR: cited source rates {src_rates} disagree by {spread:.3f}pp "
                     f"(> tolerance {CROSS_SOURCE_TOLERANCE_PP}pp) — refuse to write. Escalate "
                     f"for human review instead of picking one.")
        if not any(abs(args.rate - r) <= FLOAT_EPS for r in src_rates):
            sys.exit(f"ERROR: --rate {args.rate} does not match any cited source rate "
                     f"{src_rates} — refuse to write a number no cited source actually said.")

    # --- delta guard vs current + last human-confirmed anchor ---
    # (rows/existing already loaded by the idempotency check above — nothing has written to disk
    # since, so reusing them here is safe and avoids a second redundant _read_rows() call)
    current_rate, _ = cctg_rate_vn.current_cctg_rate()
    human_rows = sorted(
        (r for r in rows if r.get("source") not in SOURCES_REQUIRING_STRUCTURED_SOURCES),
        key=lambda r: r["effective_date"])
    last_human_rate = (float(human_rows[-1]["cctg_rate"]) if human_rows
                       else cctg_rate_vn.CCTG_EVENTS[-1][1])
    bases = [b for b in (current_rate, last_human_rate) if b is not None]
    deltas = [abs(args.rate - b) for b in bases]
    if deltas and max(deltas) >= NONINERT_DELTA_PP and not args.force:
        sys.exit(f"ERROR: rate {args.rate:g}% differs from reference(s) {bases} by up to "
                 f"{max(deltas):.2f}pp (>= {NONINERT_DELTA_PP}pp) — refuse to write. Escalate for "
                 f"human review (--force is human-only).")

    if args.force:
        rows = [r for r in rows if r["effective_date"] != args.effective]
    new_row = {"effective_date": args.effective, "cctg_rate": f"{args.rate:g}",
               "collected_date": collected, "source": args.source, "note": args.note}
    rows.append(new_row)

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(CSV_PATH), prefix=".cctg_", suffix=".csv")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HEADER)
            w.writeheader()
            w.writerows(rows)
        os.replace(tmp, CSV_PATH)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

    if args.source in SOURCES_REQUIRING_STRUCTURED_SOURCES:
        _save_last_auto_urls(_last_auto_sources_path(), args.effective, urls)

    import importlib
    importlib.reload(cctg_rate_vn)
    ev = cctg_rate_vn.cctg_events_df()
    cur, cur_date = cctg_rate_vn.current_cctg_rate()
    print(f"OK: appended {args.effective} = {args.rate:g}% (source={args.source}, collected={collected}).")
    print(f"    cctg_events_df() now has {len(ev)} anchors; current_cctg_rate() = {cur:.2f}% "
          f"(as of {cur_date}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
