#!/usr/bin/env python3
"""
vcb_fx_feed.py — Daily USD/VND exchange rate feed from Vietcombank (VCB).

Usage:
  python3 vcb_fx_feed.py              # today's date
  python3 vcb_fx_feed.py --date YYYY-MM-DD

Output:
  data/vcb_fx_rate.csv  — idempotent append (skip if date already present)
  logs/vcb_fx_feed.log  — rotating log
"""

import argparse
import base64
import csv
import logging
import os
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

import requests
import pandas as pd

WORKDIR = Path(__file__).resolve().parent
CSV_PATH = WORKDIR / "data" / "vcb_fx_rate.csv"
LOG_PATH = WORKDIR / "logs" / "vcb_fx_feed.log"
CSV_COLUMNS = ["date", "buy_cash", "buy_transfer", "sell"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def fetch_vcb(date: str) -> dict:
    """Fetch VCB exchange rate for given date. Returns dict with USD fields or raises."""
    url = f"https://www.vietcombank.com.vn/api/exchangerates/exportexcel?date={date}"
    log.info(f"Fetching VCB rate for {date}: {url}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    json_data = resp.json()
    excel_bytes = base64.b64decode(json_data["Data"])
    df = pd.read_excel(BytesIO(excel_bytes), sheet_name="ExchangeRate", header=None)
    # Rows: row 0 = title, row 1 = header, rows 2..N-4 = data, last 4 = footer
    df.columns = ["currency_code", "currency_name", "buy_cash", "buy_transfer", "sell"]
    df = df.iloc[2:-4].reset_index(drop=True)

    # Filter USD row
    usd = df[df["currency_code"].astype(str).str.strip().str.upper() == "USD"]
    if usd.empty:
        raise ValueError(f"USD row not found in VCB response for {date}")

    row = usd.iloc[0]

    def clean(v):
        """Strip commas/spaces from VCB number strings and convert to float."""
        s = str(v).replace(",", "").replace(" ", "").strip()
        return float(s) if s and s != "nan" else None

    return {
        "date": date,
        "buy_cash": clean(row["buy_cash"]),
        "buy_transfer": clean(row["buy_transfer"]),
        "sell": clean(row["sell"]),
    }


def already_in_csv(date: str) -> bool:
    """Return True if date already exists in CSV."""
    if not CSV_PATH.exists():
        return False
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("date", "").strip() == date:
                return True
    return False


def append_to_csv(record: dict) -> None:
    """Append one record to CSV, creating file with header if needed."""
    file_exists = CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


def run(date: str) -> bool:
    """Fetch and record VCB USD rate for date. Returns True on success."""
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        log.error(f"Invalid date format: {date} (expected YYYY-MM-DD)")
        return False

    if already_in_csv(date):
        log.info(f"Date {date} already in CSV — skip (idempotent)")
        return True

    try:
        record = fetch_vcb(date)
    except requests.exceptions.RequestException as e:
        log.error(f"Network error fetching VCB for {date}: {e}")
        return False
    except Exception as e:
        log.error(f"Parse/unexpected error for {date}: {e}")
        return False

    append_to_csv(record)
    log.info(
        f"Appended {date}: buy_cash={record['buy_cash']}, "
        f"buy_transfer={record['buy_transfer']}, sell={record['sell']}"
    )
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VCB USD/VND daily feed")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Date YYYY-MM-DD (default: today)",
    )
    args = parser.parse_args()

    ok = run(args.date)
    sys.exit(0 if ok else 1)
