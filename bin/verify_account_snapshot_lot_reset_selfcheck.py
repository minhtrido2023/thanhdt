#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `CostBook` / `build_cost_books()` trong verify_account_snapshot.py.

Chạy:  python3 mike/bin/verify_account_snapshot_lot_reset_selfcheck.py
Phải PASS y hệt khi chạy từ thư mục khác và không có TZ (§16 + skill `verify-before-done`):
       cd /tmp && env -u TZ python3 <repo>/mike/bin/verify_account_snapshot_lot_reset_selfcheck.py

Bug gốc (2026-08-10, job Taylor_20260810_044215): giá vốn bình quân gia quyền cộng dồn
buy_qty/buy_value qua MỌI ngày rồi chia một lần, KHÔNG reset khi vị thế về 0. Ca thật LPB
(SpaceX): mua 900cp 01/07 → BÁN SẠCH 06/07 → mua lại 900cp 15/07 ⇒ lô đã tất toán bị trộn
vào lô mới, ra 52.583,33 thay vì 51.466,67 (= đúng `costPrice` broker).

Mọi ca "chặn được" đều đi kèm CA CHỨNG MINH NGƯỢC: tính lại bằng đúng công thức CŨ trên
cùng dữ liệu và xác nhận nó THẬT SỰ ra số sai — nếu không, test chỉ đang khẳng định suông.
Fixture đóng băng: 3 ngày fill LỊCH SỬ (01/07, 06/07, 15/07) — không đọc trạng thái sống,
không phụ thuộc giao dịch LPB phát sinh sau này (§23 hệ luận 1).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import verify_account_snapshot as VAS  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def old_formula(events_by_date):
    """Công thức CŨ (đã bị thay): {ticker: buy_value/buy_qty} cộng dồn cả đời, không lô."""
    bq, bv = {}, {}
    for date in sorted(events_by_date):
        for _ts, _k, tk, side, qty, price in events_by_date[date]:
            if side == "buy":
                bq[tk] = bq.get(tk, 0.0) + qty
                bv[tk] = bv.get(tk, 0.0) + qty * price
    return {tk: bv[tk] / bq[tk] for tk in bq if bq[tk]}


print("[1] mua → bán SẠCH → mua lại: giá vốn = CHỈ lô mới (đúng bản chất bug LPB)")
b = VAS.CostBook()
b.buy(900, 900 * 53700)
b.sell(900)
b.buy(900, 900 * 51466.666667)
check("avg_cost = 51.466,67 (không trộn lô đã tất toán)", abs(b.avg_cost - 51466.666667) < 1e-4,
      b.avg_cost)
check("đếm được 1 lần vị thế về 0 (resets=1)", b.resets == 1, b.resets)
check("CHỨNG MINH NGƯỢC: công thức CŨ trên cùng dữ liệu ra 52.583,33 (sai thật)",
      abs((900 * 53700 + 900 * 51466.666667) / 1800 - 52583.333333) < 1e-4)

print("\n[2] bán BỚT (chưa về 0) KHÔNG làm đổi giá bình quân — quy ước weighted-average")
b = VAS.CostBook()
b.buy(1000, 1000 * 20000)
b.sell(400)
check("avg_cost vẫn = 20.000", abs(b.avg_cost - 20000) < 1e-9, b.avg_cost)
check("KL còn 600", abs(b.qty - 600) < 1e-9, b.qty)
check("chưa về 0 ⇒ KHÔNG reset (resets=0)", b.resets == 0, b.resets)
check("cơ sở giá vốn rút theo TỈ LỆ (600×20.000)", abs(b.basis - 12_000_000) < 1e-6, b.basis)

print("\n[3] bán BỚT rồi MUA THÊM: bình quân chạy trên phần CÒN LẠI, không trên tổng đã mua")
b = VAS.CostBook()
b.buy(100, 100 * 10000)
b.sell(50)
b.buy(100, 100 * 20000)
# đúng: (50×10.000 + 100×20.000)/150 = 16.666,67 — KHÁC hẳn công thức cũ (3.000.000/200 = 15.000)
check("avg_cost = 16.666,67", abs(b.avg_cost - 16666.666667) < 1e-4, b.avg_cost)
check("CHỨNG MINH NGƯỢC: công thức CŨ ra 15.000 (khác thật, không phải khác biệt lý thuyết)",
      abs((100 * 10000 + 100 * 20000) / 200 - 15000) < 1e-9)

print("\n[4] về 0 rồi mua lại NHIỀU LẦN: mỗi lần đều reset")
b = VAS.CostBook()
for px in (10000, 20000, 30000):
    b.buy(100, 100 * px)
    b.sell(100)
b.buy(100, 100 * 40000)
check("avg_cost = 40.000 (chỉ lô cuối)", abs(b.avg_cost - 40000) < 1e-9, b.avg_cost)
check("resets = 3", b.resets == 3, b.resets)

print("\n[5] bán QUÁ KL trace được (vị thế legacy mua trước bot): qty âm, cơ sở về 0, avg=0")
b = VAS.CostBook()
b.buy(100, 100 * 10000)
b.sell(300)
check("qty = -200 (giữ nguyên dấu âm để cảnh báo lệch KL vẫn nổ)", abs(b.qty + 200) < 1e-9, b.qty)
check("avg_cost = 0 (không bịa giá vốn cho phần không trace được)", b.avg_cost == 0, b.avg_cost)

print("\n[6] float: bán sạch bằng NHIỀU lệnh lẻ vẫn nhận diện được vị thế về 0")
b = VAS.CostBook()
b.buy(900, 900 * 53700)
for q in (100, 200, 200, 400):        # đúng chuỗi 4 lệnh bán LPB thật ngày 06/07
    b.sell(q)
check("qty = 0 chính xác", b.qty == 0.0, b.qty)
check("basis = 0 chính xác (không còn dư float)", b.basis == 0.0, b.basis)
check("resets = 1", b.resets == 1, b.resets)

print("\n[7] end-to-end trên dnse_raw THẬT — LPB/SpaceX, fixture 3 ngày đóng băng")
LPB_DATES = ["2026-07-01", "2026-07-06", "2026-07-15"]
ACCT = "0002023347"
events = {}
missing = []
for d in LPB_DATES:
    ev, err = VAS.dnse_fill_events(ACCT, d)
    if ev is None:
        missing.append(f"{d}: {err}")
        continue
    events[d] = [e for e in ev if e[2] == "LPB"]
check("đọc được cả 3 ngày dnse_raw (fixture còn nguyên)", not missing, missing)

if not missing:
    books = VAS.build_cost_books(events, "2026-07-31", VAS.load_corp_actions())
    lpb = books["LPB"]
    check("KL còn 900 sau chuỗi mua/bán/mua lại", abs(lpb.qty - 900) < 1e-9, lpb.qty)
    check("giá vốn = 51.466,67 — KHỚP costPrice broker", abs(lpb.avg_cost - 51466.67) < 0.01,
          lpb.avg_cost)
    check("nhận diện đúng 1 lần vị thế về 0", lpb.resets == 1, lpb.resets)
    old = old_formula(events).get("LPB")
    check("CHỨNG MINH NGƯỢC trên dữ liệu THẬT: công thức CŨ tái hiện đúng số sai 52.583,33",
          old is not None and abs(old - 52583.33) < 0.01, old)

    print("\n[8] thứ tự ngày truyền vào LỘN XỘN vẫn ra cùng kết quả (build_cost_books tự sắp)")
    shuffled = {d: events[d] for d in reversed(LPB_DATES)}
    b2 = VAS.build_cost_books(shuffled, "2026-07-31", VAS.load_corp_actions())["LPB"]
    check("cùng giá vốn 51.466,67", abs(b2.avg_cost - 51466.67) < 0.01, b2.avg_cost)

    print("\n[9] KHÔNG hồi quy: mã chưa từng về 0 phải ra Y HỆT công thức cũ")
    ALL_DATES = ["2026-07-01", "2026-07-02", "2026-07-06", "2026-07-15", "2026-07-21",
                 "2026-07-24", "2026-07-27", "2026-07-28", "2026-07-29"]
    ev_all = {}
    for d in ALL_DATES:
        e, err = VAS.dnse_fill_events(ACCT, d)
        if e is not None:
            ev_all[d] = e
    new_books = VAS.build_cost_books(ev_all, "2026-07-31", [])   # [] = bỏ corp action cho phép so 1-1
    old_all = old_formula(ev_all)
    diffs = []
    for tk, bk in sorted(new_books.items()):
        if bk.resets or bk.qty <= 0:
            continue
        o = old_all.get(tk)
        if o is not None and abs(o - bk.avg_cost) > 0.01:
            diffs.append((tk, o, bk.avg_cost))
    n_same = sum(1 for bk in new_books.values() if not bk.resets and bk.qty > 0)
    check(f"{n_same} mã không-reset giữ nguyên giá vốn (0 mã đổi số ngoài ý muốn)",
          not diffs, diffs)
    # Nhiều mã từng về 0 rồi THÔI (đã thoát hẳn, qty=0) — chúng không vào báo cáo vị thế nên
    # bản vá không đổi số nào của chúng. Mã DUY NHẤT vừa còn giữ vừa từng về 0 mới là mã có
    # số bị sửa: LPB. Đây chính là ranh giới "ảnh hưởng thật" vs "reset vô hại".
    held_reset = sorted(tk for tk, bk in new_books.items() if bk.resets and bk.qty > 0)
    check("đúng 1 mã ĐANG GIỮ bị đổi số bởi bản vá, và đó là LPB",
          held_reset == ["LPB"], held_reset)
    exited_reset = sorted(tk for tk, bk in new_books.items() if bk.resets and bk.qty <= 0)
    check(f"{len(exited_reset)} mã từng về 0 nhưng đã thoát hẳn ⇒ không vào báo cáo, "
          f"không đổi số nào", all(new_books[tk].avg_cost == 0 for tk in exited_reset),
          exited_reset)

print(f"\n{'=' * 70}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAIL:")
    for f in FAIL:
        print("  ·", f)
    sys.exit(1)
