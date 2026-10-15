#!/usr/bin/env python3
"""Selfcheck cho bin/daily_dashboard.py — logic thuần (ngày/định dạng), không chạm BQ/DNSE/mạng."""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import daily_dashboard as dd  # noqa: E402

fails = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


T = date(2026, 10, 16)
reg = {"programs": [
    {"id": "overdue", "end": "2026-10-10"},
    {"id": "soon", "review_date": "2026-11-01"},
    {"id": "far", "end": "2027-03-01"},
    {"id": "grad", "status": "graduated-live 2026-08-22", "end": "2026-08-24"},
    {"id": "closed", "status": "closed 2026-10-14", "end": "2026-10-14"},
    {"id": "wait", "status": "review-done 2026-10-01 — chờ user quyết", "end": "2026-09-30"},
    {"id": "ev"},
    {"id": "ev_dated"},
    {"id": "quiet", "reporting": False},
]}
watch = {"milestones": [
    {"date": "2026-10-21", "label": "M1"},
    {"date": "2026-12-01", "label": "M-far"},
    {"date": "2026-11-30", "label": "M-ev", "program_ids": ["ev_dated"]},
    {"date": "2026-10-01", "label": "M-over"},
]}
items, ev, waiting = dd.due_items(T, reg, watch)
labels = [i[1] for i in items]
check("quá hạn có mặt, sắp xếp theo ngày", items[0][0] == date(2026, 10, 1) and labels[1].startswith("paper `overdue`"))
check("review trong 21 ngày có mặt", any("`soon`" in x for x in labels))
check("ngoài 21 ngày bị loại", not any("`far`" in x or "M-far" in x for x in labels))
check("graduated/closed/review-done không vào danh sách mốc",
      not any(k in " ".join(labels) for k in ("`grad`", "`closed`", "`wait`")))
check("review-done 'chờ user' vào waiting", waiting == ["wait"])
check("event-driven: có ev, loại ev_dated (đã có mốc watchlist), loại reporting:false không ngày",
      ev == ["ev"])
check("cửa sổ re-rate: 10/10 mở, 09/10 đóng, 10/11 mở, 11/11 đóng, 15/12 đóng",
      dd._in_window(date(2026, 10, 10)) and not dd._in_window(date(2026, 10, 9))
      and dd._in_window(date(2026, 11, 10)) and not dd._in_window(date(2026, 11, 11))
      and not dd._in_window(date(2026, 12, 15)))
check("định dạng số VN", dd._n(1719.42, ",.2f") == "1.719,42" and dd._pct(-0.09) == "-0,09%" and dd._pct(None) == "n/a")
check("_vnd_m", dd._vnd_m(969196007.0) == "969tr")
sys.exit(1 if fails else 0)
