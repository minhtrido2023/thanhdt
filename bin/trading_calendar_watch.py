#!/usr/bin/env python3
"""Nhắc HẰNG TUẦN: ngày T2-T6 trong 14 ngày tới CHƯA được xác nhận lịch giao dịch.

Sự cố "không ra plan 25/11" (2026-11-25): lễ Ngày Văn hóa 24/11 chỉ được khai vào vn_market.py lúc
00:01 ngày 24/11 — SAU chuỗi 19:00/21:00/23:00 ngày 23/11 ⇒ hệ thống tin T+1=24/11, mở báo động giả.
Script này KHÔNG đoán ngày lễ và KHÔNG đổi lịch: nó chỉ liệt kê và nhắc người đối chiếu thông báo
SSI/HOSE, rồi (a) thêm ngày nghỉ vào `_VARIABLE_HOLIDAYS` hoặc (b) nâng `CALENDAR_CONFIRMED_THROUGH`
trong trading_bot/vn_market.py. Nguồn lịch duy nhất = vn_market.py (đọc qua bin/trading_calendar.py).

Gửi: có ngày chưa xác nhận ⇒ Telegram + Discord trading_daily; đủ xác nhận ⇒ 1 dòng Discord (heartbeat).
rc: 0 OK · 3 NOTIFY_FAILED (không kênh nào nhận). --dry-run: chỉ in.
Cron đề xuất (cài khi merge): `8 1 * * 1` = 08:08 ICT thứ Hai.
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trading_calendar as TC  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build(today=None, days=14):
    u = TC.upcoming(today, days)
    head = f"📅 LỊCH GIAO DỊCH {u['today'].strftime('%d/%m')}→{u['end'].strftime('%d/%m')}"
    hol = ", ".join(TC.fmt_day(d) for d in u["holidays"]) or "không có"
    ct = u["confirmed_through"].strftime("%d/%m/%Y") if u["confirmed_through"] else "CHƯA ĐẶT"
    if not u["unconfirmed"]:
        return False, f"{head}: đã xác nhận tới {ct} · ngày nghỉ T2-T6 đã khai: {hol}. Không cần làm gì."
    lst = ", ".join(TC.fmt_day(d) for d in u["unconfirmed"])
    msg = (f"{head} — ⚠️ {len(u['unconfirmed'])} ngày T2-T6 CHƯA XÁC NHẬN lịch: {lst}.\n"
           f"Ngày nghỉ T2-T6 đã khai trong cửa sổ: {hol} · mốc xác nhận hiện tại: {ct}.\n"
           "Việc cần làm: đối chiếu thông báo lịch nghỉ giao dịch của SSI/HOSE. Có ngày nghỉ ⇒ thêm vào "
           "`_VARIABLE_HOLIDAYS` trong trading_bot/vn_market.py; không có ⇒ đặt `CALENDAR_CONFIRMED_THROUGH` = "
           "ngày cuối đã đối chiếu. Hệ thống KHÔNG tự đoán/đổi lịch — ngày nghỉ khai muộn = plan T+1 sai ngày + "
           "báo động giả (sự cố 24/11/2026).")
    return True, msg


def send(argv):
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--days", type=int, default=14)
    a = ap.parse_args(argv)
    warn, msg = build(days=a.days)
    print(msg)
    if a.dry_run:
        return 0
    ok = send([os.path.join(ROOT, "bin", "notify_thread.sh"), msg, "trading_daily"])
    if warn:
        ok = send([os.path.join(ROOT, "bin", "notify.sh"), msg]) or ok
    if not ok:
        print("trading_calendar_watch: NOTIFY_FAILED — không kênh nào nhận", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
