#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck khối `savings` (Luồng B live-gap 2026-11-12). Không BQ/mạng/ghi data/.
Chạy dưới `env -u TZ` và TZ lạ:
    env -u TZ python3 mike/bin/savings_hurdle_selfcheck.py
    TZ=Pacific/Kiritimati python3 mike/bin/savings_hurdle_selfcheck.py
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pandas as pd  # noqa: E402
import nav_period_returns as npr  # noqa: E402
import savings_hurdle as sh  # noqa: E402

N = 0


def ok(c, m):
    global N
    if not c:
        raise AssertionError(m)
    N += 1


def near(a, b, tol, m):
    ok(a is not None and abs(a - b) <= tol, f"{m}: {a} vs {b}")


def synth(rows):
    return pd.DataFrame({"time": pd.to_datetime([r[0] for r in rows]), "deposit_rate": [r[1] for r in rows]})


def brute(a, b, rows):
    """Tái tính độc lập: lặp từng ngày."""
    a, b = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    tot, d = 0.0, a
    while d < b:
        r = [x[1] for x in rows if dt.date.fromisoformat(x[0]) <= d][-1]
        tot += r
        d += dt.timedelta(days=1)
    return tot / 365.0


# 1. Công thức trên chuỗi tổng hợp: kỳ 1 ngày, vắt qua đổi mốc, trùng brute-force
EV = synth([("2026-01-01", 5.0), ("2026-03-01", 7.0), ("2026-05-01", 6.0)])
R = [("2026-01-01", 5.0), ("2026-03-01", 7.0), ("2026-05-01", 6.0)]
s = sh.report_savings("2026-02-10", "2026-02-11", 0.5, ev=EV)
near(s["hurdle_pct"], 5.0 / 365, 0.0006, "kỳ 1 ngày")
ok(s["annualized_pct"] is None and "365" in s["annualized_note"], "kỳ 1 ngày không quy năm")
s = sh.report_savings("2026-02-20", "2026-03-10", 1.0, ev=EV)      # vắt qua 03-01 (5→7)
near(s["hurdle_pct"], brute("2026-02-20", "2026-03-10", R), 0.0006, "vắt qua đổi mốc")
near(s["hurdle_pct"], (9 * 5 + 9 * 7) / 365, 0.0006, "vắt qua đổi mốc (tay)")
near(s["excess_vs_savings_pp"], 1.0 - s["hurdle_pct"], 0.0006, "excess = TWR − hurdle")
for a, b in (("2026-01-05", "2026-01-12"), ("2026-03-02", "2026-03-31"), ("2026-01-01", "2026-06-01")):
    near(sh.report_savings(a, b, None, ev=EV)["hurdle_pct"], brute(a, b, R), 0.0006, f"brute {a}→{b}")
ok(sh.report_savings("2026-02-20", "2026-03-10", None, ev=EV)["excess_vs_savings_pp"] is None,
   "TWR None ⇒ excess None")

# 2. Thiếu dữ liệu ⇒ null + reason, không bịa 0
s = sh.report_savings("2025-12-01", "2026-01-10", 1.0, ev=EV)       # from trước mốc đầu
ok(s["status"] == "unavailable" and s["hurdle_pct"] is None and s["reason"], "thiếu mốc đầu")
s = sh.report_savings("2026-05-02", "2026-12-30", 1.0, ev=EV)       # mốc cuối quá cũ
ok(s["status"] == "unavailable" and s["hurdle_pct"] is None, "mốc lãi quá cũ")
s = sh.report_savings("2026-03-10", "2026-03-10", 1.0, ev=EV)
ok(s["status"] == "unavailable" and s["hurdle_pct"] is None, "kỳ 0 ngày")
s = sh.report_savings("garbage", "2026-03-10", 1.0, ev=EV)
ok(s["status"] == "unavailable", "ngày hỏng không ném lỗi")

# 3. Kỳ ≥ 365 ngày được quy năm qua đúng cửa annualize_or_null
EV2 = synth([("2024-01-01", 6.0), ("2025-03-01", 6.0)])
s = sh.report_savings("2024-06-01", "2025-06-01", 8.0, ev=EV2)
ok(s["days"] == 365 and s["annualized_pct"] is not None, "365 ngày được quy năm")
near(s["annualized_pct"], npr.annualize_or_null(1 + s["hurdle_pct"] / 100, 365)[0], 1e-9, "dùng cửa chung")

# 4. Cờ mốc neo (code luôn có; ev tổng hợp ⇒ last_anchor 2026-06-01)
ok(sh.report_savings("2026-02-01", "2026-03-01", 0, ev=EV)["anchor_warning"], "kỳ chạm neo ⇒ cờ")
ok(sh.report_savings("2026-06-02", "2026-06-20", 0, ev=synth([("2026-01-01", 5.0)]))["anchor_warning"] is None,
   "kỳ sau neo ⇒ không cờ")

# 5. Dữ liệu thật: khớp GĐ0 vs_savings_table
real = sh.report_savings("2026-07-01", "2026-11-11", -3.862)
near(real["hurdle_pct"], 2.548, 0.0006, "GĐ0 SpaceX 01/07→11/11")
near(sh.report_savings("2026-07-06", "2026-11-11", None)["hurdle_pct"], 2.455, 0.0006, "GĐ0 ZaloPay 06/07→11/11")
near(real["excess_vs_savings_pp"], -3.862 - 2.548, 0.0006, "excess SpaceX")
ok(abs(real["hurdle_pct"] - 7.4 * 133 / 365) > 0.1, "KHÔNG phải số phẳng 7,4% (2,70%)")
# kỳ vắt qua đổi mốc lãi THẬT (CCTG vào 2026-09-30)
ev_real = sh._series()[0]
x = sh.report_savings("2026-09-25", "2026-10-10", 0.0)
near(x["hurdle_pct"], sh.accrual_pct("2026-09-25", "2026-10-10", ev_real)[0], 0.0006, "đối chứng accrual")
ok(x["status"] == "ok", "kỳ qua mốc CCTG ok")
# thứ tự: kỳ dài hơn ⇒ hurdle không giảm
ok(sh.report_savings("2026-07-01", "2026-11-11")["hurdle_pct"]
   > sh.report_savings("2026-10-01", "2026-11-11")["hurdle_pct"], "đơn điệu theo độ dài")

# 6. Tích hợp nav_period_returns: không truyền savings ⇒ byte-identical; có ⇒ 4 kỳ đều có khối
for acct in ("SpaceX", "ZaloPay"):
    rows, inc = npr.load_nav_history(acct), npr.load_inception(acct)
    rd = dt.date(2026, 11, 11)
    base = npr.compute_period_returns(acct, rd, rows, inc)
    ok(all("savings" not in (base[k] or {}) for k in ("inception", "wtd", "mtd", "day")), "mặc định không savings")
    withs = npr.compute_period_returns(acct, rd, rows, inc, savings=sh.savings_fn())
    for k in ("inception", "wtd", "mtd", "day"):
        sv = withs[k].pop("savings")
        ok(sv["hurdle_pct"] is not None, f"{acct} {k} có hurdle")
        near(sv["excess_vs_savings_pp"], withs[k]["return_pct"] - sv["hurdle_pct"], 0.0006, f"{acct} {k} excess")
        ok(sv["from_date"] == withs[k]["from_date"] and sv["to_date"] == withs[k]["to_date"], "mốc = mốc sổ đơn vị")
    ok(json.dumps(withs, sort_keys=True, default=str) == json.dumps(base, sort_keys=True, default=str),
       f"{acct}: TWR/trường cũ KHÔNG đổi khi thêm savings")
    if acct == "SpaceX":
        near(withs["inception"]["return_pct"], -3.862, 0.0006, "TWR SpaceX inception")
        ok(withs["inception"]["from_date"] == "2026-07-01", "SpaceX từ 07-01")

# 7. Hàm lỗi không làm mất TWR
def boom(a, b, r=None):
    raise RuntimeError("x")
try:
    npr.compute_period_returns("SpaceX", dt.date(2026, 11, 11), npr.load_nav_history("SpaceX"),
                               npr.load_inception("SpaceX"), savings=boom)
    ok(False, "savings ném lỗi phải lan (đường _savings_fn bọc ở CLI)")
except RuntimeError:
    ok(True, "")
f = npr._savings_fn()
ok(callable(f), "CLI fn")

print(f"savings_hurdle_selfcheck: {N} assertion PASS")
