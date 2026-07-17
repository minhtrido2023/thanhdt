#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
append_deposit_rate.py — append ONE new Big-4 12M deposit-rate anchor to the append-only live
extension data/deposit_rate_vn_events.csv, read by deposit_rate_vn.py::deposit_events_df().

This NEVER edits the 26 frozen historical anchors hardcoded in deposit_rate_vn.py. It is the
human-verified write endpoint for the monthly refresh routine: refresh_deposit_rate_vn.sh only
*reminds* (best-effort fetch, no auto-write); a human runs this with the confirmed number.

deposit_rate_vn is a LIVE production input (rating_8l.py NEUTRAL-only deposit tilt, daily). Only
anchors with an effective_date strictly newer than the last frozen anchor (2026-06-01) take effect.

Usage:
  python3 append_deposit_rate.py --rate 6.9 --effective 2026-07-01 --source manual_verify \
          [--collected 2026-07-03] [--note "VCB +0.1pp so thang truoc"] [--force]

Idempotent: re-running with an effective_date already present is skipped (unless --force), so a
killed-then-rerun invocation does not duplicate a row.
"""
import argparse
import csv
import os
import sys
import tempfile
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "data", "deposit_rate_vn_events.csv")
HEADER = ["effective_date", "deposit_rate", "collected_date", "source", "note"]
VALID_SOURCES = {"vcb_web", "bidv_web", "ctg_web", "agribank_web", "cafef", "vietstock", "manual_verify"}


def _read_rows():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if r.get("effective_date")]


def _valid_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def main():
    ap = argparse.ArgumentParser(description="Append one Big-4 12M deposit-rate anchor (append-only).")
    ap.add_argument("--rate", type=float, required=True, help="Big-4 12M deposit rate, %%/yr (e.g. 6.9)")
    ap.add_argument("--effective", required=True, help="effective date YYYY-MM-DD (rate posted/effective)")
    ap.add_argument("--source", required=True,
                    help="one of: " + " | ".join(sorted(VALID_SOURCES)))
    ap.add_argument("--collected", default=None,
                    help="real collection date YYYY-MM-DD (default: today) — point-in-time marker")
    ap.add_argument("--note", default="", help="free-text note (e.g. 'BIDV +0.2pp')")
    ap.add_argument("--force", action="store_true",
                    help="append even if this effective_date already exists (default: skip = idempotent)")
    args = ap.parse_args()

    # --- validate ---
    try:
        eff = _valid_date(args.effective)
    except ValueError:
        sys.exit(f"ERROR: --effective '{args.effective}' is not YYYY-MM-DD")
    collected = args.collected or date.today().isoformat()
    try:
        _valid_date(collected)
    except ValueError:
        sys.exit(f"ERROR: --collected '{collected}' is not YYYY-MM-DD")
    if not (0.0 < args.rate < 30.0):
        sys.exit(f"ERROR: --rate {args.rate} out of sane range (0, 30) — refuse to write")
    if args.source not in VALID_SOURCES:
        sys.exit(f"ERROR: --source '{args.source}' not in {sorted(VALID_SOURCES)}")

    rows = _read_rows()
    existing = {r["effective_date"] for r in rows}
    if args.effective in existing and not args.force:
        print(f"SKIP: effective_date {args.effective} already present (use --force to override). "
              f"No write — CSV unchanged.")
        return 0

    if args.force:
        rows = [r for r in rows if r["effective_date"] != args.effective]
    new_row = {"effective_date": args.effective, "deposit_rate": f"{args.rate:g}",
               "collected_date": collected, "source": args.source, "note": args.note}
    rows.append(new_row)

    # --- atomic rewrite: temp file in same dir -> os.replace (survives a mid-write kill) ---
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(CSV_PATH), prefix=".dep_", suffix=".csv")
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

    # --- verify reload through the real consumer path ---
    sys.path.insert(0, HERE)
    import importlib
    import deposit_rate_vn
    importlib.reload(deposit_rate_vn)  # pick up the just-written CSV
    ev = deposit_rate_vn.deposit_events_df()
    frozen_max = max(datetime.strptime(d, "%Y-%m-%d").date()
                     for d, _ in deposit_rate_vn.DEPOSIT_EVENTS)
    cur = deposit_rate_vn.current_deposit_rate()
    print(f"OK: appended {args.effective} = {args.rate:g}% (source={args.source}, collected={collected}).")
    print(f"    deposit_events_df() now has {len(ev)} anchors; current_deposit_rate() = {cur:.2f}%.")
    entered = (ev["time"].dt.date == eff).any()
    if not entered:
        print(f"    WARNING: {eff} did NOT enter the live series — deposit_events_df() only appends "
              f"anchors newer than the last frozen anchor {frozen_max}. Row saved to CSV but INERT "
              f"until an effective_date > {frozen_max} is added.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
