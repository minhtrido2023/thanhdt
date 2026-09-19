#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tính lợi nhuận theo kỳ (WTD/MTD/từ khi bắt đầu hoạt động) cho MỘT account, từ
`nav_history_{account}.csv` + baseline khởi điểm ở `data/account_inception.json`.

Nguồn chuẩn tắc DUY NHẤT cho hàng "Hiệu suất lũy kế" trong báo cáo SpaceX weekly/monthly
(coding_guidelines §6/§9 — không tự tính lại từ nav_history raw). Lý do cần script riêng: dòng
đầu tiên trong `nav_history_SpaceX.csv` (07-02) là snapshot SAU phiên giao dịch đầu tiên, không
phải vốn khởi điểm thật (1.000.000.000đ nạp ngày 01/07) — dùng thẳng dòng đầu làm baseline sẽ ra
return sai lệch so với thực tế (đã xảy ra thật trong báo cáo tuần 09-14→09-18: báo -1,66% thay vì
-2,177%). ZaloPay không bị lỗi này (không có `starting_capital` ⇒ dùng dòng đầu, vì tài khoản có
vị thế legacy trước khi bot go-live, không có mốc "vốn nạp ngày 1" sạch).

Dùng: python3 mike/bin/nav_period_returns.py --account SpaceX --report-date 2026-09-18
Selfcheck: python3 mike/bin/nav_period_returns.py --selfcheck
"""
import argparse
import csv
import datetime
import json
import os
import sys
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")

WC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INCEPTION_PATH = os.path.join(WC_ROOT, "data", "account_inception.json")
NAV_HISTORY_DIR = os.path.join(WC_ROOT, "data", "execution_logs")


def _parse_date(s: str) -> datetime.date:
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()


def load_inception(account: str, inception_path: str = INCEPTION_PATH) -> dict:
    with open(inception_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if account not in cfg:
        raise ValueError(f"account '{account}' không có entry trong {inception_path}")
    return cfg[account]


def load_nav_history(account: str, nav_dir: str = NAV_HISTORY_DIR) -> list:
    """Trả list [(date, nav), ...] tăng dần theo ngày."""
    path = os.path.join(nav_dir, f"nav_history_{account}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"thiếu {path}")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            if not rec.get("date") or not rec.get("nav"):
                continue
            rows.append((_parse_date(rec["date"]), float(rec["nav"])))
    rows.sort(key=lambda r: r[0])
    if not rows:
        raise ValueError(f"{path} rỗng")
    return rows


def _last_on_or_before(rows: list, d: datetime.date):
    """Row cuối cùng có date <= d, hoặc None."""
    found = None
    for rd, nav in rows:
        if rd <= d:
            found = (rd, nav)
        else:
            break
    return found


def _last_before(rows: list, d: datetime.date):
    """Row cuối cùng có date < d, hoặc None."""
    found = None
    for rd, nav in rows:
        if rd < d:
            found = (rd, nav)
        else:
            break
    return found


def _inception_baseline(rows: list, inception: dict):
    """(from_date, nav0) khởi điểm thật: starting_capital nếu có, else dòng đầu tiên."""
    starting_capital = inception.get("starting_capital")
    if starting_capital is not None:
        return _parse_date(inception["inception_date"]), float(starting_capital)
    first_date, first_nav = rows[0]
    return first_date, first_nav


def _period(rows: list, report_date: datetime.date, period_start_exclusive: datetime.date,
            inception_from: datetime.date, inception_nav0: float, nav1_date: datetime.date,
            nav1: float) -> dict:
    """Baseline = row cuối < period_start_exclusive; nếu không có (kỳ bắt đầu trước/đúng lúc
    inception) thì lùi về chính baseline khởi điểm — không có dữ liệu nào trước điểm đó."""
    prior = _last_before(rows, period_start_exclusive)
    if prior is not None and prior[0] >= inception_from:
        from_date, nav0 = prior
    else:
        from_date, nav0 = inception_from, inception_nav0
    return {
        "from_date": from_date.isoformat(),
        "to_date": nav1_date.isoformat(),
        "nav0": nav0,
        "nav1": nav1,
        "return_pct": round((nav1 / nav0 - 1) * 100, 3),
    }


def compute_period_returns(account: str, report_date: datetime.date, rows: list, inception: dict) -> dict:
    nav1_row = _last_on_or_before(rows, report_date)
    if nav1_row is None:
        raise ValueError(f"không có dòng nav_history nào <= {report_date} cho {account}")
    nav1_date, nav1 = nav1_row

    inception_from, inception_nav0 = _inception_baseline(rows, inception)
    if nav1_date < inception_from:
        raise ValueError(f"report-date {report_date} có nav1_date {nav1_date} trước inception "
                          f"{inception_from} cho {account}")

    monday = report_date - datetime.timedelta(days=report_date.weekday())
    month_start = report_date.replace(day=1)

    out = {
        "account": account,
        "report_date": report_date.isoformat(),
        "inception": {
            "from_date": inception_from.isoformat(),
            "to_date": nav1_date.isoformat(),
            "nav0": inception_nav0,
            "nav1": nav1,
            "return_pct": round((nav1 / inception_nav0 - 1) * 100, 3),
        },
        "wtd": _period(rows, report_date, monday, inception_from, inception_nav0, nav1_date, nav1),
        "mtd": _period(rows, report_date, month_start, inception_from, inception_nav0, nav1_date, nav1),
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--account", choices=["SpaceX", "ZaloPay"])
    ap.add_argument("--report-date", help="YYYY-MM-DD (giờ ICT); mặc định hôm nay ICT")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()

    if args.selfcheck:
        return _selfcheck()

    if not args.account:
        ap.error("cần --account (hoặc --selfcheck)")

    try:
        report_date = (_parse_date(args.report_date) if args.report_date
                        else datetime.datetime.now(ICT).date())
        rows = load_nav_history(args.account)
        inception = load_inception(args.account)
        result = compute_period_returns(args.account, report_date, rows, inception)
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"LỖI nav_period_returns: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _selfcheck() -> int:
    """5+ assertion trên data thật (nav_history_SpaceX/ZaloPay.csv, account_inception.json)."""
    n = 0

    spacex_rows = load_nav_history("SpaceX")
    spacex_inception = load_inception("SpaceX")
    assert spacex_inception["starting_capital"] == 1_000_000_000, "SpaceX starting_capital phải 1B"
    n += 1

    first_date, first_nav = spacex_rows[0]
    assert first_date == datetime.date(2026, 7, 2), f"dòng đầu SpaceX phải 07-02, được {first_date}"
    n += 1

    # Ca thật đã cắn: báo cáo tuần 09-14->09-18 dùng first-row baseline ra -1.66%; đúng phải -2.177%
    result = compute_period_returns("SpaceX", datetime.date(2026, 9, 18), spacex_rows, spacex_inception)
    assert result["inception"]["nav0"] == 1_000_000_000.0, "inception nav0 phải = starting_capital"
    assert result["inception"]["from_date"] == "2026-07-01", "inception from_date phải = inception_date"
    assert abs(result["inception"]["return_pct"] - (-2.177)) < 0.01, \
        f"inception return_pct sai: {result['inception']['return_pct']} (kỳ vọng ~-2.177)"
    n += 1

    zalopay_rows = load_nav_history("ZaloPay")
    zalopay_inception = load_inception("ZaloPay")
    assert zalopay_inception["starting_capital"] is None, "ZaloPay starting_capital phải null"
    zfirst_date, zfirst_nav = zalopay_rows[0]
    zresult = compute_period_returns("ZaloPay", datetime.date(2026, 9, 18), zalopay_rows, zalopay_inception)
    assert zresult["inception"]["nav0"] == zfirst_nav, "ZaloPay inception nav0 phải = dòng đầu (không starting_capital)"
    assert zresult["inception"]["from_date"] == zfirst_date.isoformat()
    n += 1

    # WTD: baseline phải là dòng cuối TRƯỚC thứ Hai của tuần chứa report_date (tuần 09-14..09-18,
    # thứ Hai = 09-14, nên baseline = dòng cuối trước 09-14 = 09-11 nếu tồn tại).
    monday = datetime.date(2026, 9, 14) - datetime.timedelta(days=datetime.date(2026, 9, 14).weekday())
    assert monday == datetime.date(2026, 9, 14), "sanity: 2026-09-14 phải là thứ Hai"
    wtd = result["wtd"]
    assert datetime.datetime.strptime(wtd["from_date"], "%Y-%m-%d").date() < monday, \
        "wtd from_date phải trước thứ Hai của tuần report_date"
    n += 1

    # MTD: baseline phải trước 2026-09-01
    mtd = result["mtd"]
    assert datetime.datetime.strptime(mtd["from_date"], "%Y-%m-%d").date() < datetime.date(2026, 9, 1), \
        "mtd from_date phải trước đầu tháng 9"
    n += 1

    # Edge case: report_date == inception_date-adjacent (kỳ WTD/MTD lùi về trước cả inception)
    # -> baseline phải fallback về chính inception, không lỗi/không âm vô hạn.
    early = compute_period_returns("SpaceX", datetime.date(2026, 7, 3), spacex_rows, spacex_inception)
    assert early["wtd"]["from_date"] == "2026-07-01", \
        f"wtd đầu kỳ phải fallback về inception_date, được {early['wtd']['from_date']}"
    n += 1

    # Fail path: account không tồn tại trong inception config
    try:
        load_inception("NoSuchAccount")
        raise AssertionError("load_inception phải raise cho account không tồn tại")
    except ValueError:
        pass
    n += 1

    print(f"OK — {n} assertion PASS (nav_period_returns.py)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
