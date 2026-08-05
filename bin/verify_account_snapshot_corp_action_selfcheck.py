#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `corp_action_multiplier()` trong verify_account_snapshot.py.

Chạy:  python3 mike/bin/verify_account_snapshot_corp_action_selfcheck.py
Phải PASS y hệt khi chạy từ thư mục khác (§16 + skill `verify-before-done` bước 3):
       cd /tmp && python3 <repo>/mike/bin/verify_account_snapshot_corp_action_selfcheck.py

Bug gốc (2026-08-05, VHM chia cổ tức cổ phiếu 1:1): `verify_account_snapshot.py` gộp fill
theo NGÀY từ `true_fills_from_dnse_raw()` (KHÔNG đọc vị thế broker sống), nên qty/giá vốn
per-position ĐÃ AN TOÀN trong ngày sự kiện — nhưng KHÔNG có cơ chế nào tự cập nhật khi ngày
báo cáo (`asof`) đi QUA ex_date thật (2026-08-06): giá BQ/close_price sẽ tự động phản ánh
split từ ex_date trở đi, còn qty gộp-từ-fill vẫn đứng yên ở số CŨ nếu không có
`corp_action_multiplier()` — tạo ra đúng loại lệch cặp qty/giá mà bug NAV gốc đã gây ra,
chỉ khác chỗ (per-position thay vì NAV tổng) và khác NGÀY kích hoạt (mai, không phải hôm nay).

Test THUẦN LOGIC (không mạng, không BQ, không broker) — `corp_action_multiplier()` chỉ so
sánh 3 chuỗi ngày ISO, không gọi network/TZ/cwd nào, nên không cần cô lập môi trường như
`corp_action_selfcheck.py`. Case 6 mô phỏng đủ 2 phía ranh giới ex_date bằng dữ liệu fill
thật lấy qua `true_fills_from_dnse_raw()` (đọc file tĩnh trên đĩa, không gọi mạng).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import verify_account_snapshot as VAS  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


FAKE_ACTS = [{"ticker": "VHM", "ex_date": "2026-08-06", "qty_multiplier": 2.0,
             "id": "VHM-2026-08-06-STOCK-DIVIDEND"}]

print("[1] fill trước ex_date, asof TRƯỚC ex_date ⇒ chưa nhân (đúng trạng thái hôm nay 08-05)")
m = VAS.corp_action_multiplier("VHM", "2026-07-01", "2026-08-05", FAKE_ACTS)
check("multiplier = 1.0", m == 1.0, m)

print("\n[2] fill trước ex_date, asof ĐÚNG ex_date ⇒ nhân (kích hoạt đúng ngày mai 08-06)")
m = VAS.corp_action_multiplier("VHM", "2026-07-01", "2026-08-06", FAKE_ACTS)
check("multiplier = 2.0", m == 2.0, m)

print("\n[3] fill trước ex_date, asof SAU ex_date nhiều ngày ⇒ vẫn nhân (không tự tắt)")
m = VAS.corp_action_multiplier("VHM", "2026-07-01", "2026-08-20", FAKE_ACTS)
check("multiplier = 2.0", m == 2.0, m)

print("\n[4] fill NGAY ex_date (không phải trước) ⇒ KHÔNG hưởng quyền, không nhân")
m = VAS.corp_action_multiplier("VHM", "2026-08-06", "2026-08-20", FAKE_ACTS)
check("multiplier = 1.0 (mua đúng ngày ex không được hưởng quyền)", m == 1.0, m)

print("\n[5] fill SAU ex_date (mua sau khi đã chia rồi) ⇒ không nhân")
m = VAS.corp_action_multiplier("VHM", "2026-08-10", "2026-08-20", FAKE_ACTS)
check("multiplier = 1.0", m == 1.0, m)

print("\n[5b] mã KHÁC không có corp action ⇒ luôn 1.0 (không đụng mã khác)")
m = VAS.corp_action_multiplier("VNM", "2026-07-01", "2026-08-06", FAKE_ACTS)
check("multiplier = 1.0", m == 1.0, m)

print("\n[6] end-to-end trên fill THẬT (dnse_raw), 2 phía ranh giới ex_date")
DATES = ["2026-07-01", "2026-07-02", "2026-07-06", "2026-07-15", "2026-07-21",
         "2026-07-24", "2026-07-27", "2026-07-28", "2026-07-29"]


def _agg(asof):
    agg = [0.0, 0.0, 0.0]
    for d in DATES:
        raw, err = VAS.true_fills_from_dnse_raw("0002023347", d)
        if err or "VHM" not in raw:
            continue
        nq, bq, bv = raw["VHM"]
        m = VAS.corp_action_multiplier("VHM", d, asof, FAKE_ACTS)
        agg[0] += nq * m
        agg[1] += bq * m
        agg[2] += bv
    return agg


before = _agg("2026-08-05")   # trước ex_date — trạng thái hôm nay
after = _agg("2026-08-06")    # đúng ex_date — trạng thái mai

check("qty TRƯỚC ex_date = 500 (đúng số hôm nay, không bị nhân sớm)",
      before[0] == 500.0, before[0])
check("qty TỪ ex_date = 1000 (đúng x2)", after[0] == 1000.0, after[0])
check("buy_qty cũng nhân theo đúng tỉ lệ (500/1000 == before/after)",
      abs(before[1] * 2 - after[1]) < 1e-9, (before[1], after[1]))
check("buy_value (tổng tiền đã bỏ ra) BẤT BIẾN qua ranh giới split",
      abs(before[2] - after[2]) < 1e-6, (before[2], after[2]))

cost_before = before[2] / before[1]
cost_after = after[2] / after[1]
check("true_avg_cost SAU = ĐÚNG PHÂN NỬA true_avg_cost TRƯỚC (chia giá vốn theo hệ số)",
      abs(cost_before - cost_after * 2) < 1e-6, (cost_before, cost_after))

# P&L% phải LIÊN TỤC qua ranh giới split — kinh tế không đổi, chỉ đổi cách đếm.
PX_BEFORE, PX_AFTER = 153000.0, 76500.0   # PX_AFTER = PX_BEFORE/2, đúng cơ chế broker đã làm
pnl_pct_before = (before[0] * PX_BEFORE - before[0] * cost_before) / (before[0] * cost_before) * 100
pnl_pct_after = (after[0] * PX_AFTER - after[0] * cost_after) / (after[0] * cost_after) * 100
check("unrealized_pnl_pct LIÊN TỤC qua ranh giới split (kinh tế không đổi)",
      abs(pnl_pct_before - pnl_pct_after) < 1e-6, (pnl_pct_before, pnl_pct_after))

print(f"\n{'=' * 70}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAIL:")
    for f in FAIL:
        print("  ·", f)
    sys.exit(1)
