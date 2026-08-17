#!/usr/bin/env python3
"""Chụp DNSE latest_trade().avgPrice (board G1) cho toàn bộ mã UPCOM sau giờ đóng cửa và
append vào lịch sử cục bộ mike/data/upcom_vwap_history.csv.

Vì sao script này tồn tại: DNSE không có API lịch sử VWAP — latest_trade() chỉ giữ phiên
gần nhất. G5 (gate GDKHQ UPCOM) cần lịch sử để chạy trước giờ mở cửa ⇒ phải tự dựng bằng cách
chụp lại mỗi phiên. Nguồn + bẫy đầy đủ:
mike/kb/data_registry/price-volume/dnse_latest_trade_avgprice_upcom.md

Cửa sổ chạy hợp lệ: sau ~15:05 ICT tới trước 09:00 ICT hôm sau (đọc trong phiên ra avgPrice
dở dang — script tự chặn, không cưỡng chế qua cron time).
"""
import csv
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

WORKDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # mike/
ROOT = os.path.dirname(WORKDIR)  # WorkingClaude/
sys.path.insert(0, ROOT)

from dnse_api import DNSEClient, DNSEError  # noqa: E402

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
SEED_FILE = os.path.join(WORKDIR, "data", "upcom_tickers_seed.csv")
OUT_FILE = os.path.join(WORKDIR, "data", "upcom_vwap_history.csv")
CSV_HEADER = ["date", "ticker", "avg_price", "total_volume_g1"]

# Cửa sổ đọc hợp lệ (bẫy #2 trong data_registry entry): trong phiên avgPrice là số dở dang.
MARKET_CLOSE_HOUR_ICT = 15


def load_seed_tickers(path=SEED_FILE):
    with open(path, newline="", encoding="utf-8") as f:
        return [row["ticker"].strip() for row in csv.DictReader(f) if row["ticker"].strip()]


def fetch_g1_avg_price(client, ticker):
    """Trả (avg_price, total_volume) hoặc (None, None) nếu mã không có board G1 phiên đó."""
    resp = client.latest_trade(ticker)
    trades = resp.get("trades", []) if isinstance(resp, dict) else []
    g1 = [t for t in trades if t.get("boardId") == "G1"]
    if not g1:
        return None, None
    rec = g1[0]
    return rec.get("avgPrice"), rec.get("totalVolumeTraded")


def already_captured_today(out_path, date_str):
    if not os.path.exists(out_path):
        return False
    with open(out_path, newline="", encoding="utf-8") as f:
        return any(row.get("date") == date_str for row in csv.DictReader(f))


def append_rows(out_path, rows):
    is_new = not os.path.exists(out_path)
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADER)
        if is_new:
            w.writeheader()
        w.writerows(rows)


def main():
    now = datetime.now(ICT)
    date_str = now.strftime("%Y-%m-%d")

    # Cửa sổ xuyên nửa đêm (15:00 ICT hôm nay → 09:00 ICT hôm sau) ⇒ OR, không phải range đơn giản.
    in_window = now.hour >= MARKET_CLOSE_HOUR_ICT or now.hour < 9
    if not in_window:
        print(f"[skip] {now.isoformat()} nằm trong phiên (09:00-15:00 ICT) — "
              f"avgPrice sẽ dở dang, không chụp.")
        return 1

    if already_captured_today(OUT_FILE, date_str):
        print(f"[skip] {date_str} đã capture rồi (idempotent) — không ghi trùng.")
        return 0

    tickers = load_seed_tickers()
    client = DNSEClient.from_credentials_file()

    rows = []
    ok, no_g1, errors = 0, 0, 0
    for t in tickers:
        try:
            avg_price, vol = fetch_g1_avg_price(client, t)
        except DNSEError as e:
            print(f"[err] {t}: {e}")
            errors += 1
            rows.append({"date": date_str, "ticker": t, "avg_price": "", "total_volume_g1": ""})
            continue
        if avg_price is None:
            no_g1 += 1
            rows.append({"date": date_str, "ticker": t, "avg_price": "", "total_volume_g1": ""})
        else:
            ok += 1
            rows.append({"date": date_str, "ticker": t, "avg_price": avg_price,
                         "total_volume_g1": vol})

    append_rows(OUT_FILE, rows)
    print(f"[done] {date_str}: {ok}/{len(tickers)} mã capture được avgPrice G1 "
          f"({no_g1} không có board G1, {errors} lỗi API) → {OUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
