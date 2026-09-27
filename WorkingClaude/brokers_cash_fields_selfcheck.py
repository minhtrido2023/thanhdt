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
  2. `_cash_totalcash_minus_debt()` = "SỞ HỮU" (cơ sở NAV, caller `plan.py` nav_live). Nó CỐ Ý
     KHÔNG mang bất biến `totalCash ≥ availableCash` của `mike/bin/park_holdings.py`: bất biến đó
     chỉ đúng SAU GIỜ ĐÓNG CỬA. Đo thật trên dnse_raw_*.jsonl: 1.911/7.181 record `balances` có
     totalCash < availableCash, 881/1.438 (61%) ở giờ 13 — và trả None ở đây làm plan.py rơi về
     `get_cash()` (LỚN HƠN) ⇒ thổi nav_live đúng chiều nới vay. Mục 2e/2f/2g dùng SỐ THẬT để ghim
     việc guard đó không được thêm lại; mục 4 ghim việc nó vẫn sống ở đường post-close.
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

print("2. _cash_totalcash_minus_debt() = SỞ HỮU — guard đúng PHẠM VI caller")
m = lambda st: _broker(st)._cash_totalcash_minus_debt()   # noqa: E731
check("2a payload thật ⇒ 203.656.265 − 0", m(REAL) == 203_656_265.0, m(REAL))
check("2b thiếu totalCash ⇒ None", m({k: v for k, v in REAL.items() if k != "totalCash"}) is None)
check("2c thiếu totalDebt ⇒ None", m({k: v for k, v in REAL.items() if k != "totalDebt"}) is None)
check("2d cả ba field tiền = 0 ⇒ None (guard _cash_fields_all_zero)",
      m({"totalCash": 0.0, "totalDebt": 0.0, "availableCash": 0.0,
         "depositInterest": 318.0}) is None)
# ── 2e/2f: BẤT BIẾN `totalCash ≥ availableCash` KHÔNG ĐÚNG Ở HÀM NÀY ────────────────────
# Bản đầu (2026-09-27) thêm guard `tc < av ⇒ None` vào đây theo finding của code-quality report.
# arch-review CHẶN, và đo thật cho thấy finding SAI Ở ĐIỂM NÀY: trên toàn bộ dnse_raw_*.jsonl
# (7.181 record `balances` có cả hai field) có **1.911 record totalCash < availableCash**, tập
# trung đúng giờ giao dịch — 881/1.438 (61%) ở giờ 13, 416/655 ở giờ 14, 0/819 ngoài giờ — trải
# 10 ngày, gồm 2026-09-17 và 2026-09-18. Ngữ nghĩa feed: `availableCash ≈ totalCash +
# secureAmount` (DNSE không hạ availableCash trong phiên; phần bị giữ nằm ở secureAmount).
# Trả None ở đây khiến `plan.py:1977` rơi về `get_cash()` = CHÍNH họ availableCash ⇒ LỚN HƠN ⇒
# nav_live thổi lên ⇒ `plan.py:2000` nới lỏng đúng chiều sinh ra vay vượt mức. Giờ 13 là lúc
# `run_bot.sh` chạy lại (crontab "13:00 ICT — khởi động lại sau nghỉ trưa").
# BA ca dưới dùng SỐ THẬT đọc từ dnse_raw, không phải fixture bịa — đó là điểm mà bộ 17 fixture
# tổng hợp của bản đầu không thể phát hiện được.
check("2e SỐ THẬT SpaceX 2026-09-18T13:30 (tc 35.011.893 < av 45.693.614, secureAmount "
      "25.044.269) ⇒ PHẢI trả 35.011.893, KHÔNG được None (None ⇒ plan.py rơi về availableCash "
      "= 45.693.614, thổi nav_live lên 10,7tr đúng chiều nới vay)",
      m({"totalCash": 35_011_893.0, "totalDebt": 0.0, "availableCash": 45_693_614.0,
         "secureAmount": 25_044_269.0}) == 35_011_893.0,
      m({"totalCash": 35_011_893.0, "totalDebt": 0.0, "availableCash": 45_693_614.0,
         "secureAmount": 25_044_269.0}))
check("2f SỐ THẬT SpaceX 2026-09-17T13:10 (tc 45.694.517 < av 58.105.642) ⇒ trả 45.694.517",
      m({"totalCash": 45_694_517.0, "totalDebt": 0.0, "availableCash": 58_105_642.0,
         "secureAmount": 12_412_028.0}) == 45_694_517.0)
check("2g SỐ THẬT go-live 2026-07-01T13:00 (tc 506.919.547 < av 1.000.021.918, secureAmount "
      "493.107.851 — đúng hằng đẳng thức av ≈ tc + secure) ⇒ trả 506.919.547",
      m({"totalCash": 506_919_547.0, "totalDebt": 0.0, "availableCash": 1_000_021_918.0,
         "secureAmount": 493_107_851.0}) == 506_919_547.0)
check("2g2 totalCash == availableCash (ca post-close bình thường) ⇒ trả 5tr",
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

print("4. RANH GIỚI THỜI GIAN — guard `tc < av` vẫn ĐÚNG ở caller POST-CLOSE")
# Không phải "bất biến này sai", mà là "nó sai Ở CALLER NÀY". `park_holdings
# ._cash_fields_inconsistent` đọc bản ghi CUỐI của ngày (sau đóng cửa), nơi secureAmount đã về 0:
# đo 2/165 cặp (ngày, account) vi phạm, cả hai là ngày go-live và một bản ghi có totalCash ÂM —
# ở đó chặn là đúng. Mục này ghim việc guard KHÔNG bị xoá lây khỏi đường post-close.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mike", "bin"))
try:
    import park_holdings as _PH4
except Exception as _e4:                                       # noqa: BLE001
    check(f"4a nạp được mike/bin/park_holdings.py ({_e4})", False)
else:
    check("4a park_holdings._cash_fields_inconsistent VẪN chặn tc < av (đường post-close)",
          _PH4._cash_fields_inconsistent({"totalCash": 0.0, "availableCash": 5_000_000.0}) is True)
    check("4b …và KHÔNG chặn khi tc ≥ av",
          _PH4._cash_fields_inconsistent({"totalCash": 5_000_000.0,
                                          "availableCash": 5_000_000.0}) is False)
    # Kiểm bằng AST trên SO SÁNH THẬT, không bằng cắt chuỗi. Bản đầu dùng
    # `.split("⛔")[-1]` nên MÙ với đúng hai hình dạng dễ xảy ra nhất (arch-review vòng 2 đo được):
    # guard thêm lại PHÍA TRÊN khối ⛔ — chính chỗ 6a5ebca7 đặt nó — và cách viết
    # `float(tc) < float(av)`. Đây là lần thứ NĂM trong job này phép kiểm source bằng chuỗi cho
    # kết quả sai. Cổng thật vẫn là 2e/2f/2g (hành vi, bắt mọi cách viết); mục này chỉ để chỉ
    # đúng tên thủ phạm khi chúng đỏ.
    import ast as _a4      # noqa: E402
    import inspect as _i4  # noqa: E402
    import textwrap as _t4  # noqa: E402

    def _names4(node):
        """Tên biến xuất hiện trong một biểu thức, kể cả qua float()/Decimal()."""
        return {n.id for n in _a4.walk(node) if isinstance(n, _a4.Name)}

    _fn4 = _a4.parse(_t4.dedent(
        _i4.getsource(DNSEBroker._cash_totalcash_minus_debt))).body[0]
    _bad4 = [c.lineno for c in _a4.walk(_fn4)
             if isinstance(c, _a4.Compare)
             and any(isinstance(o, (_a4.Lt, _a4.LtE)) for o in c.ops)
             and "tc" in _names4(c.left)
             and any("av" in _names4(cp) for cp in c.comparators)]
    check("4c `DNSEBroker._cash_totalcash_minus_debt` KHÔNG có phép so sánh nào dạng `tc < av` "
          "(bắt cả `float(tc) < float(av)` và cả khi guard đặt TRÊN khối ⛔) — thêm lại thì "
          "2e/2f/2g chết trước, mục này chỉ gọi đúng tên thủ phạm",
          _bad4 == [], _bad4)

print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
if FAIL:
    for n in FAIL:
        print(f"  - {n}")
sys.exit(1 if FAIL else 0)
