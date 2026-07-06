#!/usr/bin/env python3
"""
hog_price_feed.py — Weekly VN live hog price feed from 3tres3.com/vn (no login required).

Fetches 3 markets via undocumented but public POST API (accio=cotitzacions):
  166 = Việt Nam - Miền Bắc - Hơi
  169 = Việt Nam - Miền Trung - Hơi
  170 = Việt Nam - Miền Nam - Hơi

Usage:
  python3 hog_price_feed.py              # fetch all available history, append new rows
  python3 hog_price_feed.py --since YYYY-MM-DD  # only fetch entries on/after this date

Output:
  data/hog_price_vn.csv  — idempotent append (skip if date+region already present)
  logs/hog_price_feed.log
"""

import argparse
import csv
import datetime
import logging
import sys
from pathlib import Path

import requests

WORKDIR = Path(__file__).resolve().parent
CSV_PATH = WORKDIR / "data" / "hog_price_vn.csv"
LOG_PATH = WORKDIR / "logs" / "hog_price_feed.log"
CSV_COLUMNS = ["date", "region", "price_vnd_kg"]

# 3tres3 market IDs for Vietnam regions
MARKETS = {
    166: "Bắc",
    169: "Trung",
    170: "Nam",
}

# Public API endpoint (no auth required; POST with form params)
API_URL = "https://www.3tres3.com/vn/Gi%C3%A1-heo/vi%E1%BB%87t-nam_166/?accio=cotitzacions"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def fetch_market(market_id: int) -> list[dict]:
    """
    Fetch all available price entries for market_id.
    Returns list of {date: str, region: str, price_vnd_kg: float}.
    3tres3 API uses JavaScript 0-indexed months in date array.
    """
    resp = requests.post(
        API_URL,
        data={"moneda": "VND", "unitats": "kg", "mercats": str(market_id)},
        headers={"X-Requested-With": "XMLHttpRequest"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    out = data.get("out", {})
    grafic = out.get("grafic", [])
    region = MARKETS[market_id]
    records = []
    for entry in grafic:
        d_arr, price = entry[0], entry[1]
        if price is None:
            continue
        # JS month is 0-indexed: [year, month_0idx, day]
        year, month_0, day = int(d_arr[0]), int(d_arr[1]), int(d_arr[2])
        dt = datetime.date(year, month_0 + 1, day).isoformat()
        records.append({"date": dt, "region": region, "price_vnd_kg": float(price)})
    return records


def load_existing_keys() -> set:
    """Return set of (date, region) tuples already in CSV."""
    if not CSV_PATH.exists():
        return set()
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        return {(r["date"], r["region"]) for r in reader}


def append_records(records: list[dict]) -> int:
    """Append records to CSV. Returns number of rows written."""
    existing = load_existing_keys()
    new_rows = [r for r in records if (r["date"], r["region"]) not in existing]
    if not new_rows:
        return 0
    file_exists = CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        for row in new_rows:
            writer.writerow(row)
    return len(new_rows)


def run(since: str | None = None) -> bool:
    """Fetch all markets and append new rows. Returns True on success."""
    since_date = None
    if since:
        try:
            since_date = datetime.date.fromisoformat(since)
        except ValueError:
            log.error(f"Invalid --since date: {since}")
            return False

    all_records = []
    for market_id, region in MARKETS.items():
        try:
            records = fetch_market(market_id)
            if since_date:
                records = [r for r in records if r["date"] >= since]
            log.info(f"Market {market_id} ({region}): {len(records)} entries fetched")
            all_records.extend(records)
        except requests.RequestException as e:
            log.error(f"Network error for market {market_id} ({region}): {e}")
            return False
        except Exception as e:
            log.error(f"Parse error for market {market_id} ({region}): {e}")
            return False

    written = append_records(all_records)
    log.info(f"Done: {written} new rows appended to {CSV_PATH}")
    if written > 0:
        # Log latest values per region for quick sanity check
        by_region = {}
        for r in all_records:
            rname = r["region"]
            if rname not in by_region or r["date"] > by_region[rname]["date"]:
                by_region[rname] = r
        for rname in ["Bắc", "Trung", "Nam"]:
            if rname in by_region:
                latest = by_region[rname]
                log.info(f"  Latest {rname}: {latest['date']} = {latest['price_vnd_kg']:.0f} VND/kg")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3tres3.com VN hog price weekly feed")
    parser.add_argument(
        "--since",
        default=None,
        help="Only fetch entries on/after YYYY-MM-DD (default: all available history)",
    )
    args = parser.parse_args()

    ok = run(args.since)
    sys.exit(0 if ok else 1)
