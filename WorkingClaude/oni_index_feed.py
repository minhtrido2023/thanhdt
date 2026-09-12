#!/usr/bin/env python3
"""
oni_index_feed.py — Fetch NOAA CPC Oceanic Nino Index (ONI) direct from the fixed-width
ASCII source (no HTML/model summarization step).

Source: https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt
Format: "SEAS YR TOTAL ANOM" fixed-width columns, one row per overlapping 3-month season,
1950 -> present (updated ~mid-month by NOAA CPC).

Usage:
  python3 oni_index_feed.py              # fetch full history, overwrite data/oni_index.csv
  python3 oni_index_feed.py --since 2006  # only keep years >= 2006 in the output

Output:
  data/oni_index.csv  (year,season,total,anom)
  logs/oni_index_feed.log
"""

import argparse
import csv
import logging
import sys
import urllib.request
from pathlib import Path

WORKDIR = Path(__file__).resolve().parent
CSV_PATH = WORKDIR / "data" / "oni_index.csv"
LOG_PATH = WORKDIR / "logs" / "oni_index_feed.log"
CSV_COLUMNS = ["year", "season", "total", "anom"]

SOURCE_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def fetch_raw() -> str:
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse(raw: str) -> list[dict]:
    """Parse 'SEAS YR TOTAL ANOM' whitespace-delimited rows, skip header."""
    records = []
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) != 4 or parts[0] == "SEAS":
            continue
        season, year, total, anom = parts
        records.append(
            {"year": int(year), "season": season, "total": float(total), "anom": float(anom)}
        )
    return records


def write_csv(records: list[dict], since_year: int | None = None) -> int:
    if since_year is not None:
        records = [r for r in records if r["year"] >= since_year]
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for r in records:
            writer.writerow(r)
    return len(records)


def run(since_year: int | None = None) -> bool:
    try:
        raw = fetch_raw()
    except Exception as e:
        log.error(f"Fetch error: {e}")
        return False

    records = parse(raw)
    if not records:
        log.error("Parsed 0 records — source format may have changed")
        return False

    written = write_csv(records, since_year)
    log.info(f"Done: {written} rows written to {CSV_PATH}")
    latest = records[-1]
    log.info(f"  Latest: {latest['season']} {latest['year']} ANOM={latest['anom']}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NOAA CPC ONI index fetch (direct ASCII source)")
    parser.add_argument(
        "--since",
        type=int,
        default=None,
        help="Only keep rows with year >= this value (default: full history from 1950)",
    )
    args = parser.parse_args()

    ok = run(args.since)
    sys.exit(0 if ok else 1)
