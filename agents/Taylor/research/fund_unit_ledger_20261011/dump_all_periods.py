#!/usr/bin/env python3
"""In JSON {account: {date: compute_period_returns(...)}} cho MỌI ngày nav_history thật của 2 TK,
dùng cây code ở argv[1] (thư mục bin). Chạy 2 lần (master / nhánh) rồi so bằng compare_control.py."""
import datetime, json, sys
sys.path.insert(0, sys.argv[1])
import nav_period_returns as npr
out = {}
for acct in ("SpaceX", "ZaloPay"):
    rows = npr.load_nav_history(acct)
    inc = npr.load_inception(acct)
    out[acct] = {}
    d = rows[0][0]
    last = rows[-1][0]
    while d <= last:          # mọi ngày LỊCH (kể cả cuối tuần: report-date rơi vào ngày không phiên)
        try:
            out[acct][d.isoformat()] = npr.compute_period_returns(acct, d, rows, inc)
        except Exception as exc:
            out[acct][d.isoformat()] = {"error": f"{type(exc).__name__}: {exc}"}
        d += datetime.timedelta(days=1)
json.dump(out, sys.stdout, ensure_ascii=False, sort_keys=True)
