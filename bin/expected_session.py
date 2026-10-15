#!/usr/bin/env python3
"""Phiên giao dịch gần nhất mà dữ liệu EOD ĐÃ ĐƯỢC KỲ VỌNG có mặt — dùng cho chạy tay buổi sáng.

Luật: hôm nay (ICT) là ngày giao dịch VÀ giờ >= CUTOFF (17:00) -> hôm nay; ngược lại lùi về phiên
trước. In:  --session -> YYYY-MM-DD | --next -> ngày giao dịch kế tiếp sau phiên đó | (mặc định) cả hai.
`MIKE_NOW_ICT` (ISO, không tz) chỉ để selfcheck. Dùng bởi bq_freshness_check.sh và
daily_refresh_v34b_linux.sh khi MIKE_MORNING_RUN=1 (opt-in; cron KHÔNG đặt biến này).
"""
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"))
from trading_bot.vn_market import is_holiday, next_trading_day  # noqa: E402

CUTOFF_HOUR = 17


def _trading(d):
    return d.weekday() < 5 and not is_holiday(d)


def expected_session(now):
    d = now.date()
    if not (_trading(d) and now.hour >= CUTOFF_HOUR):
        d -= dt.timedelta(days=1)
        while not _trading(d):
            d -= dt.timedelta(days=1)
    return d


def main(argv):
    raw = os.environ.get("MIKE_NOW_ICT")
    now = dt.datetime.fromisoformat(raw) if raw else dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    s = expected_session(now)
    n = next_trading_day(s)
    if "--session" in argv:
        print(s)
    elif "--next" in argv:
        print(n)
    else:
        print(s, n)


if __name__ == "__main__":
    main(sys.argv[1:])
