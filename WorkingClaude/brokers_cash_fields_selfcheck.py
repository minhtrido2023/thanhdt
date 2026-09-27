#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho hai đường đọc TIỀN của `DNSEBroker` (§25) — code-quality-weekly 2026-09-27.

Chạy:  python3 WorkingClaude/brokers_cash_fields_selfcheck.py
       cd /tmp && env -u TZ python3 <repo>/WorkingClaude/brokers_cash_fields_selfcheck.py

KHÔNG gọi DNSE thật: dựng `DNSEBroker` trần rồi gắn client giả + tắt `_raw_log`.

Khoá 2 thứ, mỗi thứ là một câu hỏi §25 KHÁC nhau — trộn hai câu là bug, không phải style:
  1. `get_cash()` = "TIÊU ĐƯỢC NGAY" (executor WAIT_CASH `get_cash() < need`, biên dưới
     fallback của `check_plan_funding`). CHỈ được đọc họ availableCash. Chuỗi alias cũ kết
     thúc ở `purchasingpower`/`totalcash`/`cash`/`balance` ⇒ DNSE đổi tên field là cổng tiền
     ÂM THẦM nhảy lên số "SỞ HỮU" (đo thật SpaceX 2026-08-07: 4,82M vs 203,66M — gấp 42 lần).
  2. `_cash_totalcash_minus_debt()` = "SỞ HỮU" (cơ sở NAV, caller `plan.py` nav_live) phải có
     ĐỦ BA guard của `mike/bin/park_holdings.py`. Bản cũ chỉ có 2/3 — thiếu bất biến
     `totalCash ≥ availableCash`, nên lỗi feed ăn HAI trong ba field lọt nguyên vẹn.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")          # §5b

from trading_bot.brokers import DNSEBroker   # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


class _FakeClient:
    def __init__(self, stock):
        self._stock = stock

    def balances(self, account_id):
        return {"stock": dict(self._stock), "derivative": {}}


def _broker(stock):
    b = DNSEBroker(account_id="TEST", label="SELFCHK")
    b._raw_log = None                      # không ghi dnse_raw thật
    b.client = _FakeClient(stock)
    return b


# Số THẬT SpaceX 2026-08-07 (§25 bảng): availableCash 4.821.143 vs totalCash 203.656.265.
REAL = {"availableCash": 4_821_143.0, "totalCash": 203_656_265.0, "totalDebt": 0.0,
        "depositInterest": 1_200.0}

print("1. get_cash() = TIÊU ĐƯỢC NGAY — chỉ họ availableCash")
check("1a payload thật ⇒ 4.821.143 (KHÔNG phải totalCash 203.656.265)",
      _broker(REAL).get_cash() == 4_821_143.0, _broker(REAL).get_cash())
_no_av = {k: v for k, v in REAL.items() if k != "availableCash"}
check("1b DNSE bỏ/đổi tên availableCash, totalCash 203,66M còn sống ⇒ 0.0 (fail-closed), "
      "TUYỆT ĐỐI không trả 203.656.265", _broker(_no_av).get_cash() == 0.0,
      _broker(_no_av).get_cash())
check("1c purchasingPower có mặt cũng KHÔNG được dùng (đó là câu hỏi của ppse/get_buying_power)",
      _broker({**_no_av, "purchasingPower": 300_000_000.0}).get_cash() == 0.0,
      _broker({**_no_av, "purchasingPower": 300_000_000.0}).get_cash())
check("1d `cash`/`balance` (tên mơ hồ) KHÔNG được dùng",
      _broker({**_no_av, "cash": 99_000_000.0, "balance": 88_000_000.0}).get_cash() == 0.0)
check("1e biến thể viết khác của CÙNG khái niệm vẫn nhận (cashAvailable)",
      _broker({**_no_av, "cashAvailable": 7_000_000.0}).get_cash() == 7_000_000.0)
check("1f withdrawableCash cũng nhận", _broker({**_no_av, "withdrawableCash": 5.0}).get_cash() == 5.0)
check("1g availableCash = 0 THẬT ⇒ 0.0, không nổ", _broker({**REAL, "availableCash": 0.0}).get_cash() == 0.0)

print("2. _cash_totalcash_minus_debt() = SỞ HỮU — đủ BA guard §25")
m = lambda st: _broker(st)._cash_totalcash_minus_debt()   # noqa: E731
check("2a payload thật ⇒ 203.656.265 − 0", m(REAL) == 203_656_265.0, m(REAL))
check("2b thiếu totalCash ⇒ None", m({k: v for k, v in REAL.items() if k != "totalCash"}) is None)
check("2c thiếu totalDebt ⇒ None", m({k: v for k, v in REAL.items() if k != "totalDebt"}) is None)
check("2d cả ba field tiền = 0 ⇒ None (guard _cash_fields_all_zero)",
      m({"totalCash": 0.0, "totalDebt": 0.0, "availableCash": 0.0,
         "depositInterest": 318.0}) is None)
check("2e GUARD MỚI: totalCash 0 < availableCash 5.000.000 ⇒ None (bất biến kế toán; bản cũ "
      "trả 0.0 như thể tiền thật về 0)",
      m({"totalCash": 0.0, "totalDebt": 0.0, "availableCash": 5_000_000.0,
         "depositInterest": 318.0}) is None,
      m({"totalCash": 0.0, "totalDebt": 0.0, "availableCash": 5_000_000.0,
         "depositInterest": 318.0}))
check("2f GUARD MỚI, ca tổng quát hơn: totalCash 1tr < availableCash 5tr (không field nào = 0) "
      "⇒ None", m({"totalCash": 1_000_000.0, "totalDebt": 0.0,
                   "availableCash": 5_000_000.0}) is None)
check("2g CHỨNG MINH NGƯỢC 2e/2f: totalCash == availableCash (bất biến THOẢ dạng ≥) ⇒ trả 5tr",
      m({"totalCash": 5_000_000.0, "totalDebt": 0.0, "availableCash": 5_000_000.0}) == 5_000_000.0)
check("2h CHỨNG MINH NGƯỢC: thiếu availableCash nhưng totalCash/totalDebt sống ⇒ vẫn trả hiệu "
      "(guard mới không được chặn oan)",
      m({"totalCash": 10_000_000.0, "totalDebt": 4_000_000.0}) == 6_000_000.0)
check("2i nợ > tiền (margin call) vẫn trả số ÂM, không kẹp về 0",
      m({"totalCash": 10_000_000.0, "totalDebt": 15_000_000.0,
         "availableCash": 0.0}) == -5_000_000.0)

print("3. RANH GIỚI — hai hàm KHÔNG được trả cùng một số trên payload thật")
check("3a get_cash() ≠ _cash_totalcash_minus_debt() trên payload thật (nếu bằng nhau thì một "
      "trong hai đã trả lời sai câu hỏi §25 của nó)",
      _broker(REAL).get_cash() != m(REAL))

print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
if FAIL:
    for n in FAIL:
        print(f"  - {n}")
sys.exit(1 if FAIL else 0)
