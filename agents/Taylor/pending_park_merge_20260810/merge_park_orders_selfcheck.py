#!/usr/bin/env python3
"""Selfcheck cho merge_park_orders.py.

Quy ước §24: MỌI ca "chặn được" đều đi kèm một ca CHỨNG MINH NGƯỢC (bỏ cơ chế chặn ra thì
thật sự vượt/thật sự trùng) — không khẳng định suông trên một rổ rỗng.

Không đụng file production, không đọc trạng thái sống: mọi fixture đóng băng trong file này,
riêng nhóm R (regression 08-07) dựng từ SỐ THẬT của phiên 2026-08-07 chép cứng vào đây.
"""
import contextlib
import copy
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merge_park_orders import (  # noqa: E402
    OWNER, is_owned, merge_park_orders, print_report,
)
from merge_park_orders import _APPROVAL_KEYS as mpo_APPROVAL_KEYS  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ✔ {name}")
    else:
        print(f"  ✘ {name} — {detail}")
        FAILS.append(f"{name}: {detail}")


# ══════════════════════════════════════════════════════════════════════════════════════
# fixtures
# ══════════════════════════════════════════════════════════════════════════════════════
def buy_order(oid="BUY-DRI-LAG-01", ticker="DRI", qty=1800, pri=1):
    return {"id": oid, "ticker": ticker, "side": "buy", "qty": qty, "ref_price": 13100.0,
            "book": "LAG", "play_type": "LAG_HI", "priority": pri,
            "total_with_fee_vnd": 23_597_685}


def plan(orders=None, **kw):
    # `orders=[]` (rỗng CÓ CHỦ Ý) khác `orders=None` (mặc định) — dùng `is None`, không dùng
    # `or`, nếu không ca V9 sẽ âm thầm nhận lệnh mua mặc định và test tự vô hiệu.
    p = {"plan_date": "2026-08-11", "account": "ZaloPay",
         "orders": [buy_order()] if orders is None else list(orders),
         "approved_by": None, "requires_user_approval": True}
    p.update(kw)
    return p


def l1_art(orders, decision="TRIM", **kw):
    a = {"decision": decision, "reconcile_ok": True, "orders": orders,
         "account_label": "ZaloPay", "trim_proposed_vnd": 0}
    a.update(kw)
    return a


def l2_art(orders, decision="JIT", amendments=None, **kw):
    a = {"decision": decision, "reconcile_ok": True, "orders": orders,
         "account_label": "ZaloPay", "buy_amendments": amendments or [],
         "jit_sell_total_vnd": 0}
    a.update(kw)
    return a


def s(ticker, qty, px, sellable, play="PARK_TRIM", **kw):
    o = {"ticker": ticker, "side": "sell", "qty": qty, "ref_price": float(px),
         "value_vnd": qty * px, "book": "PARK", "play_type": play, "sellable": sellable}
    o.update(kw)
    return o


def sell_qty(p, tk):
    return sum(o["qty"] for o in p["orders"]
               if o["side"] == "sell" and o["ticker"] == tk)


# ══════════════════════════════════════════════════════════════════════════════════════
# R — REGRESSION: tái lập ĐÚNG bug 2026-08-07 (bán trùng do 2 namespace id)
#     Số thật ZaloPay 08-07: VHM sellable=300, L1=200, L2=100. Script cũ ghi lệnh GỘP
#     (300cp) rồi approve_plan_with_jit.sh ghi THÊM lệnh JIT gốc (100cp) vì id khác nhau
#     ⇒ 400cp > 300cp sellable.
# ══════════════════════════════════════════════════════════════════════════════════════
print("\n[R] Regression sự cố 2026-08-07 — bán trùng khi có cả lệnh gộp lẫn lệnh JIT gốc")

L1_0807 = l1_art([s("BID", 200, 37900, 900), s("VHM", 200, 76500, 300),
                  s("VCB", 300, 62800, 800)])
L2_0807 = l2_art([s("BID", 100, 37900, 900, play="JIT_UNPARK", for_order_id="BUY-DRI-LAG-01"),
                  s("VHM", 100, 76500, 300, play="JIT_UNPARK", for_order_id="BUY-DRI-LAG-01"),
                  s("VCB", 100, 62800, 800, play="JIT_UNPARK", for_order_id="BUY-DRI-LAG-01")],
                 amendments=[{"order_id": "BUY-DRI-LAG-01", "status": "FUNDED_BY_JIT",
                              "qty_final": 1800, "reason": "bán PARK đủ tài trợ"}])

# ── R0: chứng minh NGƯỢC — cơ chế cũ (dedup theo id) THẬT SỰ tạo ra 400cp ──────────────
legacy_merged = [
    {"id": "SELL-VHM-PARK-07", "ticker": "VHM", "side": "sell", "qty": 300,
     "ref_price": 76500.0, "book": "PARK", "play_type": "PARK_TRIM+JIT_UNPARK",
     "priority": 0, "sellable": 300,
     "merged_from": {"L1_park_trim_qty": 200, "L2_jit_unpark_qty": 100,
                     "sellable_at_calc": 300}},
    # ← lệnh JIT GỐC còn nguyên: id namespace KHÁC nên dedup `oid in existing_ids` không thấy
    {"id": "SELL-JIT-PARK-VHM-01", "ticker": "VHM", "side": "sell", "qty": 100,
     "ref_price": 76500.0, "book": "PARK", "play_type": "JIT_UNPARK", "priority": 0},
    buy_order(),
]
broken = plan(legacy_merged)
check("R0 chứng minh ngược: trạng thái 08-07 THẬT SỰ bán 400cp > 300cp sellable",
      sell_qty(broken, "VHM") == 400,
      f"đo được {sell_qty(broken, 'VHM')}cp")

# ── R1: merge mới chạy trên ĐÚNG trạng thái hỏng đó ⇒ hội tụ, không nhân đôi ──────────
fixed, rep = merge_park_orders(broken, L1_0807, L2_0807)
check("R1 status OK", rep["status"] == "OK", json.dumps(rep["errors"], ensure_ascii=False))
check("R1 VHM về đúng 300cp (200 L1 + 100 L2), KHÔNG còn 400",
      sell_qty(fixed, "VHM") == 300, f"đo được {sell_qty(fixed, 'VHM')}cp")
check("R1 chỉ còn 1 lệnh bán/mã",
      all(sum(1 for o in fixed["orders"] if o["side"] == "sell" and o["ticker"] == t) == 1
          for t in ("BID", "VHM", "VCB")))
check("R1 lệnh JIT gốc di sản đã bị NHẬN NUÔI + xoá",
      not any(o["id"] == "SELL-JIT-PARK-VHM-01" for o in fixed["orders"]))
check("R1 lệnh gộp di sản (id cũ) cũng bị xoá",
      not any(o["id"] == "SELL-VHM-PARK-07" for o in fixed["orders"]))
check("R1 lệnh MUA giữ nguyên qty",
      [o for o in fixed["orders"] if o["side"] == "buy"][0]["qty"] == 1800)
check("R1 báo cáo ghi rõ 2 lệnh di sản đã bị xoá",
      len([d for d in rep["dropped_owned"] if d["ticker"] == "VHM"]) == 2,
      str(rep["dropped_owned"]))

# ── R2: chứng minh cơ chế NHẬN NUÔI là thứ chặn được (bỏ nó ra thì hỏng) ─────────────
check("R2 is_owned() nhận diện lệnh di sản KHÔNG có dấu merge_owner",
      is_owned({"side": "sell", "book": "PARK", "play_type": "JIT_UNPARK"}) is True)
check("R2 is_owned() KHÔNG nhận lệnh bán của book khác (không được xoá nhầm)",
      is_owned({"side": "sell", "book": "BAL", "play_type": "EXIT"}) is False)
check("R2 is_owned() KHÔNG nhận lệnh MUA",
      is_owned({"side": "buy", "book": "PARK", "play_type": "PARK_TRIM"}) is False)


# ══════════════════════════════════════════════════════════════════════════════════════
# I — IDEMPOTENT (§5 coding_guidelines)
# ══════════════════════════════════════════════════════════════════════════════════════
print("\n[I] Idempotent — chạy lại KHÔNG cộng dồn")

p1, _ = merge_park_orders(plan(), L1_0807, L2_0807)
p2, r2 = merge_park_orders(copy.deepcopy(p1), L1_0807, L2_0807)
p3, _ = merge_park_orders(copy.deepcopy(p2), L1_0807, L2_0807)


def _blob(p):
    """Toàn bộ plan TRỪ khối nhật ký chạy `merge_park_orders` (xem I1b)."""
    q = {k: v for k, v in p.items() if k != "merge_park_orders"}
    return json.dumps(q, sort_keys=True, ensure_ascii=False)


check("I1 lần 2 == lần 1 (orders[] byte-identical)",
      json.dumps(p1["orders"], sort_keys=True, ensure_ascii=False) ==
      json.dumps(p2["orders"], sort_keys=True, ensure_ascii=False))
check("I1a lần 2 == lần 1 trên MỌI field trừ khối nhật ký", _blob(p1) == _blob(p2))
# I1b — khác biệt DUY NHẤT được phép là `n_dropped_owned` (nhật ký chạy: lần 1 xoá 0 lệnh,
# lần 2 xoá 3 lệnh của lần 1). Không phải trạng thái quyết định — nhưng phải nêu tên tường
# minh, nếu không "idempotent" thành lời khẳng định suông che mất một field trôi thật.
d1, d2 = p1["merge_park_orders"], p2["merge_park_orders"]
diff_keys = sorted(k for k in set(d1) | set(d2)
                   if json.dumps(d1.get(k), sort_keys=True, ensure_ascii=False)
                   != json.dumps(d2.get(k), sort_keys=True, ensure_ascii=False))
check("I1b field DUY NHẤT khác giữa 2 lần chạy = n_dropped_owned (nhật ký, không phải quyết định)",
      diff_keys == ["n_dropped_owned"], f"khác: {diff_keys}")
check("I2 lần 3 == lần 2 (ổn định, không trôi — JSON đầy đủ)",
      json.dumps(p2, sort_keys=True, ensure_ascii=False) ==
      json.dumps(p3, sort_keys=True, ensure_ascii=False))
check("I3 số lệnh không nở ra", len(p1["orders"]) == len(p2["orders"]) == 4,
      f"{len(p1['orders'])}/{len(p2['orders'])}")
check("I4 lần 2 báo đã xoá đúng 3 lệnh của lần 1 (có dấu sở hữu)",
      len(r2["dropped_owned"]) == 3 and all(d["tagged"] for d in r2["dropped_owned"]))

# ── I5: chạy lại với artifact MỚI ⇒ ra số MỚI, không phải cũ+mới ─────────────────────
L1_new = l1_art([s("BID", 500, 37900, 900)])
p_new, _ = merge_park_orders(copy.deepcopy(p1), L1_new, None)
check("I5 artifact đổi ⇒ kết quả THAY THẾ, không chồng lên",
      sell_qty(p_new, "BID") == 500 and sell_qty(p_new, "VHM") == 0,
      f"BID={sell_qty(p_new, 'BID')} VHM={sell_qty(p_new, 'VHM')}")


# ══════════════════════════════════════════════════════════════════════════════════════
# P — PARTIAL reconcile (bản vá 2026-08-10): reconcile_ok=False NHƯNG có orders
# ══════════════════════════════════════════════════════════════════════════════════════
print("\n[P] PARTIAL reconcile — không kế thừa `assert reconcile_ok is True`")

L1_partial = l1_art([s("BID", 200, 37900, 900)], reconcile_ok=False, reconcile_partial=True)
L2_partial = l2_art([s("BID", 100, 37900, 900, play="JIT_UNPARK",
                       for_order_id="BUY-DRI-LAG-01")],
                    reconcile_ok=False, reconcile_partial=True)
pp, rp = merge_park_orders(plan(), L1_partial, L2_partial)
check("P1 PARTIAL vẫn merge được (status OK)", rp["status"] == "OK", str(rp["errors"]))
check("P1 sinh đúng 300cp BID (200 L1 + 100 L2)", sell_qty(pp, "BID") == 300,
      f"{sell_qty(pp, 'BID')}")
check("P1 cả 2 tầng được chấp nhận",
      rp["layers"]["L1"]["accepted"] and rp["layers"]["L2"]["accepted"])

# ── P2: chứng minh ngược — reconcile_ok=False mà KHÔNG có partial ⇒ tầng bị từ chối ──
L1_bad = l1_art([s("BID", 200, 37900, 900)], reconcile_ok=False)
pb, rb = merge_park_orders(plan(), L1_bad, None)
check("P2 chứng minh ngược: ok=False + không partial ⇒ tầng L1 bị từ chối, 0 lệnh",
      rb["layers"]["L1"]["accepted"] is False and sell_qty(pb, "BID") == 0)
check("P2 nhưng KHÔNG làm hỏng cả plan (status vẫn OK, lệnh mua còn)",
      rb["status"] == "OK" and any(o["side"] == "buy" for o in pb["orders"]))

# ── P3: bài học 08-06 — một tầng hỏng KHÔNG được khoá tầng kia ───────────────────────
p3b, r3b = merge_park_orders(plan(), L1_bad, L2_partial)
check("P3 L1 bị từ chối nhưng L2 vẫn cấp vốn (không khoá cả tài khoản)",
      r3b["layers"]["L1"]["accepted"] is False
      and r3b["layers"]["L2"]["accepted"] is True
      and sell_qty(p3b, "BID") == 100, f"BID={sell_qty(p3b, 'BID')}")

# ── P4: decision khác TRIM/JIT ⇒ tầng đó 0 lệnh, không crash ─────────────────────────
_, r4 = merge_park_orders(plan(), l1_art([], decision="BLOCKED_RECONCILE"),
                          l2_art([], decision="NO_JIT"))
check("P4 decision BLOCKED_RECONCILE/NO_JIT ⇒ 0 lệnh, không lỗi",
      r4["status"] == "OK" and not r4["generated"])
check("P4 artifact thiếu hẳn (None) cũng không lỗi",
      merge_park_orders(plan(), None, None)[1]["status"] == "OK")


# ══════════════════════════════════════════════════════════════════════════════════════
# S — TRẦN SELLABLE / T+2: merge tự chặn, KHÔNG dựa gate hạ nguồn
# ══════════════════════════════════════════════════════════════════════════════════════
print("\n[S] Trần sellable — cắt tại merge, cắt L1 trước")

L1_over = l1_art([s("VHM", 300, 76500, 300)])
L2_over = l2_art([s("VHM", 200, 76500, 300, play="JIT_UNPARK",
                    for_order_id="BUY-DRI-LAG-01")],
                 amendments=[{"order_id": "BUY-DRI-LAG-01", "status": "FUNDED_BY_JIT",
                              "qty_final": 1800, "reason": "x"}])
ps, rs = merge_park_orders(plan(), L1_over, L2_over)
check("S1 tổng đề xuất 500 > sellable 300 ⇒ cắt về đúng 300",
      sell_qty(ps, "VHM") == 300, f"{sell_qty(ps, 'VHM')}")
check("S1 cắt vào L1 TRƯỚC (L2 giữ nguyên 200)",
      rs["per_ticker"]["VHM"]["L2_final"] == 200
      and rs["per_ticker"]["VHM"]["L1_final"] == 100,
      str(rs["per_ticker"]["VHM"]))
check("S1 có cảnh báo nêu rõ đã cắt",
      any("CẮT theo trần sellable" in w for w in rs["warnings"]))

# ── S2: chứng minh ngược — sellable rộng thì KHÔNG cắt ───────────────────────────────
L1_ok2 = l1_art([s("VHM", 300, 76500, 1000)])
L2_ok2 = l2_art([s("VHM", 200, 76500, 1000, play="JIT_UNPARK")])
ps2, rs2 = merge_park_orders(plan(), L1_ok2, L2_ok2)
check("S2 chứng minh ngược: sellable 1000 ⇒ giữ đủ 500cp, không cắt",
      sell_qty(ps2, "VHM") == 500 and not rs2["per_ticker"]["VHM"]["cut_L1"])

# ── S3: lệnh bán của writer KHÁC (book BAL) cũng tính vào trần ───────────────────────
foreign_sell = {"id": "SELL-VHM-BAL-01", "ticker": "VHM", "side": "sell", "qty": 200,
                "ref_price": 76500.0, "book": "BAL", "play_type": "EXIT", "priority": 0}
ps3, rs3 = merge_park_orders(plan([foreign_sell, buy_order()]), L1_over, L2_over)
check("S3 lệnh bán book BAL 200cp được tính vào trần ⇒ merge chỉ còn 100cp",
      sell_qty(ps3, "VHM") == 300 and rs3["per_ticker"]["VHM"]["qty"] == 100,
      f"tổng={sell_qty(ps3, 'VHM')} merge={rs3['per_ticker']['VHM']['qty']}")
check("S3 lệnh BAL KHÔNG bị xoá (ngoài vùng sở hữu)",
      any(o["id"] == "SELL-VHM-BAL-01" for o in ps3["orders"]))

# ── S4: qty sau khi cắt luôn là bội lô 100 ──────────────────────────────────────────
L1_odd = l1_art([s("HDB", 600, 24000, 659)])
ps4, _ = merge_park_orders(plan(), L1_odd, None)
check("S4 sellable lẻ 659 ⇒ qty làm tròn XUỐNG bội 100 (600 vừa khít, giữ 600)",
      sell_qty(ps4, "HDB") == 600)
L1_odd2 = l1_art([s("HDB", 700, 24000, 659)])
ps5, _ = merge_park_orders(plan(), L1_odd2, None)
check("S4b đề xuất 700 > sellable 659 ⇒ cắt xuống 600 (bội lô), KHÔNG phải 659",
      sell_qty(ps5, "HDB") == 600, f"{sell_qty(ps5, 'HDB')}")

# ── S5: cắt vào L2 ⇒ gắn cờ jit_underfunded lên lệnh mua ─────────────────────────────
# L2 MỘT MÌNH đã vượt trần (400 > 300) ⇒ cắt hết L1 vẫn chưa đủ, buộc phải cắt vào L2.
L1_big = l1_art([s("VHM", 100, 76500, 300)])
L2_big = l2_art([s("VHM", 400, 76500, 300, play="JIT_UNPARK")],
                amendments=[{"order_id": "BUY-DRI-LAG-01", "status": "FUNDED_BY_JIT",
                             "qty_final": 1800, "reason": "x"}])
ps6, rs6 = merge_park_orders(plan(), L1_big, L2_big)
buy = [o for o in ps6["orders"] if o["side"] == "buy"][0]
check("S5 cắt hết L1 vẫn vượt ⇒ cắt L2 và gắn cờ jit_underfunded lên lệnh mua",
      buy.get("jit_underfunded") is True
      and rs6["per_ticker"]["VHM"]["cut_L1"] == 100
      and rs6["per_ticker"]["VHM"]["cut_L2"] == 100
      and sell_qty(ps6, "VHM") == 300,
      str(rs6["per_ticker"]["VHM"]))
check("S5 chứng minh ngược: ca S1 (không cắt L2) KHÔNG gắn cờ",
      [o for o in ps["orders"] if o["side"] == "buy"][0].get("jit_underfunded") is None)

# ── S5b: nhãn JIT trên lệnh MUA phải DỰNG-LẠI-HOẶC-VẮNG-MẶT qua các lần chạy ──────────
# Khuyết tật #5 (quant-skeptic vòng 3, 2026-08-10): cơ chế "sở hữu vùng + dựng lại" chỉ áp
# cho lệnh BÁN. `jit_status`/`jit_note`/`jit_underfunded` ghi lên lệnh MUA nằm NGOÀI vùng
# sở hữu ⇒ trước bản vá KHÔNG BAO GIỜ bị xoá: chạy 1 với L2 đủ vốn ⇒ "FUNDED_BY_JIT"; L2
# sau đó bị TỪ CHỐI ⇒ chạy lại VẪN hiện "FUNDED_BY_JIT" dù JIT đã bị từ chối thật.
JIT_KEYS = ("jit_status", "jit_note", "jit_underfunded")
run1_buy = [o for o in ps6["orders"] if o["side"] == "buy"][0]
# (a) không vô căn cứ: chạy 1 THẬT SỰ đã ghi đủ 3 nhãn lên lệnh mua đó.
check("S5b tiền đề: chạy 1 (L2 nhận + bị cắt) ghi ĐỦ 3 nhãn jit_* lên lệnh mua",
      all(k in run1_buy for k in JIT_KEYS)
      and run1_buy["jit_status"] == "FUNDED_BY_JIT",
      str({k: run1_buy.get(k) for k in JIT_KEYS}))
# (b) chạy 2 trên CHÍNH plan đầu ra đó, L2 bị TỪ CHỐI (reconcile_ok=False, không partial).
L2_rejected = l2_art([s("VHM", 400, 76500, 300, play="JIT_UNPARK")],
                     amendments=[{"order_id": "BUY-DRI-LAG-01", "status": "FUNDED_BY_JIT",
                                  "qty_final": 1800, "reason": "x"}],
                     reconcile_ok=False)
ps7, rs7 = merge_park_orders(copy.deepcopy(ps6), L1_big, L2_rejected)
run2_buy = [o for o in ps7["orders"] if o["side"] == "buy"][0]
check("S5b L2 BỊ TỪ CHỐI ở lần chạy 2 ⇒ lệnh mua KHÔNG còn nhãn jit_* nào",
      rs7["status"] == "OK" and rs7["layers"]["L2"]["accepted"] is False
      and not any(k in run2_buy for k in JIT_KEYS),
      str({k: run2_buy.get(k) for k in JIT_KEYS}))
check("S5b lần chạy 2 KHÔNG đụng qty lệnh mua (chỉ xoá nhãn)",
      run2_buy["qty"] == run1_buy["qty"] == 1800)
check("S5b L2 bị từ chối ⇒ chỉ còn phần bán L1 (100cp), không còn 300cp của lần chạy 1",
      sell_qty(ps7, "VHM") == 100 and sell_qty(ps6, "VHM") == 300,
      f"run2={sell_qty(ps7, 'VHM')} run1={sell_qty(ps6, 'VHM')}")
# (c) cờ NGƯỢC HƯỚNG: chạy lại với sellable rộng rãi (không phải cắt) ⇒ `jit_status` được
#     DỰNG LẠI nhưng `jit_underfunded` biến mất, thay vì kẹt True từ lần trước.
L1_roomy = l1_art([s("VHM", 100, 76500, 3000)])
L2_roomy = l2_art([s("VHM", 400, 76500, 3000, play="JIT_UNPARK")],
                  amendments=[{"order_id": "BUY-DRI-LAG-01", "status": "FUNDED_BY_JIT",
                               "qty_final": 1800, "reason": "x"}])
ps8, rs8 = merge_park_orders(copy.deepcopy(ps6), L1_roomy, L2_roomy)
run3_buy = [o for o in ps8["orders"] if o["side"] == "buy"][0]
check("S5b chạy lại KHÔNG cắt ⇒ jit_underfunded biến mất (không kẹt True), jit_status dựng lại",
      "jit_underfunded" not in run3_buy and run3_buy.get("jit_status") == "FUNDED_BY_JIT"
      and rs8["per_ticker"]["VHM"]["cut_L2"] == 0,
      str({k: run3_buy.get(k) for k in JIT_KEYS}))
# (d) cả hai tầng đều không sinh lệnh ⇒ vẫn phải xoá sạch nhãn (không có tầng nào dựng lại).
ps9, rs9 = merge_park_orders(copy.deepcopy(ps6), None, L2_rejected)
run4_buy = [o for o in ps9["orders"] if o["side"] == "buy"][0]
check("S5b không tầng nào được nhận ⇒ nhãn jit_* vẫn bị xoá sạch (vắng mặt, không sót)",
      rs9["status"] == "OK" and not any(k in run4_buy for k in JIT_KEYS)
      and sell_qty(ps9, "VHM") == 0,
      str({k: run4_buy.get(k) for k in JIT_KEYS}))
# (e) REFUSED thì KHÔNG đụng gì cả — kể cả nhãn. Đây là hành vi CỐ Ý: fail-closed trả về
#     plan NGUYÊN VẸN, caller không ghi file ⇒ đĩa không đổi. Xoá nhãn ở nhánh REFUSED sẽ
#     phá đúng bất biến "REFUSED ⇒ plan không đổi" mà ca S6 canh.
before10 = copy.deepcopy(ps6)
before10["approved_by"] = "user (John) Discord"
ps11, rs11 = merge_park_orders(copy.deepcopy(before10), L1_big, L2_big)
check("S5b REFUSED ⇒ plan trả về NGUYÊN VẸN, nhãn jit_* cũ GIỮ NGUYÊN (cố ý, không ghi file)",
      rs11["status"] == "REFUSED"
      and json.dumps(ps11, sort_keys=True) == json.dumps(before10, sort_keys=True))

# ── S5c: khối ĐỀ XUẤT nhúng cũng phải DỰNG-LẠI-HOẶC-VẮNG-MẶT ─────────────────────────
# Khuyết tật #6 (quant-skeptic vòng 4, 2026-08-10) — CÙNG LỚP với #5, ở tầng cao hơn:
# `p["jit_unpark_proposal"]` chỉ được ghi lại KHI có artifact ⇒ chạy 1 có L2 (dán "✅ ĐÃ
# MERGE") rồi chạy 2 mất file artifact ⇒ khối đó Y NGUYÊN trong khi orders[] chỉ còn L1.
ps12, _ = merge_park_orders(plan(), L1_roomy, L2_roomy)
check("S5c tiền đề: chạy 1 có L2 ⇒ có khối jit_unpark_proposal dán 'ĐÃ MERGE'",
      "✅" in ps12["jit_unpark_proposal"]["_merged_into_orders"])
ps13, rs13 = merge_park_orders(copy.deepcopy(ps12), L1_roomy, None)
check("S5c chạy 2 KHÔNG có artifact L2 ⇒ khối cũ bị XOÁ khỏi plan (không sót 'ĐÃ MERGE')",
      "jit_unpark_proposal" not in ps13,
      str(ps13.get("jit_unpark_proposal", {}).get("_merged_into_orders"))[:80])
check("S5c có cảnh báo nêu rõ đã xoá khối kiểm toán cũ",
      any("VẮNG MẶT" in w and "jit_unpark_proposal" in w for w in rs13["warnings"]),
      str(rs13["warnings"]))
check("S5c chứng minh ngược: artifact L2 CÓ nhưng bị từ chối ⇒ khối vẫn còn, dán '⛔'",
      "⛔" in merge_park_orders(copy.deepcopy(ps12), L1_roomy,
                                L2_rejected)[0]["jit_unpark_proposal"]["_merged_into_orders"])
check("S5c khối L1 vẫn còn nguyên ở chạy 2 (chỉ tầng vắng artifact bị xoá)",
      "park_trim_proposal" in ps13)

# ── S5d: bước 0 xoá theo KHÔNG GIAN TÊN `jit_*`, không theo danh sách liệt kê ────────
# quant-skeptic vòng 5 **BÁC BỎ** bản neo trước (helper bắt buộc gọi + ca grep 3 tên
# literal): helper chỉ nổ khi có người GỌI, ca grep chỉ biết 3 tên đang có ⇒ nhãn thứ 4 gán
# thẳng `tgt["jit_x"] = …` lọt qua CẢ HAI và tái lập nguyên văn khuyết tật #5 với selfcheck
# vẫn xanh. Nay bước 0 xoá theo TIỀN TỐ ⇒ tập XOÁ luôn là tập CHA của mọi tập GHI, theo cấu
# trúc. Ca dưới đây kiểm đúng TÍNH CHẤT đó — độc lập với writer, không đọc mã nguồn.
# Đây chính là probe của quant-skeptic, dựng thành ca thường trực: một nhãn `jit_*` LẠ nằm
# sẵn trên lệnh mua (y như thứ mà "bước 5 phiên bản tương lai" sẽ để lại) phải biến mất.
future = dict(buy_order())
future["jit_funding_tier"] = "FUNDED_BY_JIT"   # nhãn thứ 4 chưa từng được khai báo ở đâu
future["jit_them_mot_nua"] = {"lồng": ["cả", "cấu", "trúc"]}
future["total_with_fee_vnd"] = 23_597_685      # khoá KHÔNG thuộc jit_* — phải còn nguyên
psd, _ = merge_park_orders(plan([future]), L1_roomy, None)
buy_d = [o for o in psd["orders"] if o["side"] == "buy"][0]
check("S5d nhãn jit_* LẠ (chưa khai báo ở bất kỳ đâu) vẫn bị xoá — xoá theo tiền tố",
      not [k for k in buy_d if k.startswith("jit_")],
      str([k for k in buy_d if k.startswith("jit_")]))
check("S5d chứng minh ngược: khoá KHÔNG thuộc jit_* KHÔNG bị đụng (không xoá bừa)",
      buy_d.get("total_with_fee_vnd") == 23_597_685 and buy_d["qty"] == 1800
      and buy_d["id"] == "BUY-DRI-LAG-01")
check("S5d tiền đề: đúng là 2 nhãn lạ ĐÃ CÓ trong plan đầu vào (ca không vô căn cứ)",
      len([k for k in future if k.startswith("jit_")]) == 2)
# và nhãn lạ đó cũng không sống sót qua đường L2 ĐƯỢC NHẬN (nhánh có ghi đè nhãn thật)
psd2, _ = merge_park_orders(plan([dict(future)]), L1_roomy, L2_roomy)
buy_d2 = [o for o in psd2["orders"] if o["side"] == "buy"][0]
# RANH GIỚI: bước 0 quét khoá **CẤP MỘT** của lệnh. Khoá `jit_` LỒNG trong dict con KHÔNG bị
# quét — ghim thành sự thật ĐÃ KIỂM (quant-skeptic vòng 6) thay vì giả định ngầm, để bước 5
# tương lai biết: muốn thêm nhãn thì ghi CẤP MỘT, đừng ghi lồng.
nested = dict(buy_order())
nested["meta"] = {"jit_nested": "khong bi quet"}
psn, _ = merge_park_orders(plan([nested]), L1_roomy, None)
check("S5d RANH GIỚI: khoá jit_ LỒNG trong dict con KHÔNG bị quét (bước 0 chỉ quét cấp một)",
      [o for o in psn["orders"] if o["side"] == "buy"][0]["meta"] == {"jit_nested": "khong bi quet"},
      "nếu ca này đổi ⇒ ranh giới đã đổi, cập nhật comment `_JIT_PREFIX`")

# Ca cuối là TRIPWIRE có chủ ý: nó chốt ĐÚNG tập nhãn bước 5 ghi ra. Thêm nhãn `jit_*` mới ở
# bước 5 ⇒ ca này ĐỎ. Đó KHÔNG phải lỗi của bản vá (an toàn đã do tiền tố lo, đã đo: vá thêm
# `tgt["jit_funding_tier"]` vào bước 5 rồi chạy L2-bị-từ-chối trên dữ liệu SpaceX 08-07 thật ⇒
# 0 nhãn sống sót). Nó là **chuông báo đọc lại học thuyết**. Thấy đỏ thì làm ĐÚNG THỨ TỰ NÀY,
# đừng nới assertion cho hết đỏ: (1) xác nhận nhãn mới ghi ở **cấp một** của lệnh — lồng thì
# bước 0 không quét, phải sửa bước 0 trước; (2) xác nhận nó được ghi trong bước 5 nên **được
# dựng lại mỗi lần chạy**; rồi mới (3) thêm tên vào tập kỳ vọng dưới đây.
check("S5d nhãn lạ cũng bị xoá ở nhánh L2 ĐƯỢC NHẬN (chỉ còn nhãn dựng lại lần này)",
      set(k for k in buy_d2 if k.startswith("jit_")) == {"jit_status", "jit_note"},
      str(sorted(k for k in buy_d2 if k.startswith("jit_"))))

# ── S5e: CÙNG nguyên tắc namespace ở **CẤP PLAN** (mở rộng phạm vi 2026-08-10) ───────
# Ca THẬT làm ra bản vá: `plan_SpaceX_2026-08-10.json` mang khoá cấp plan `jit_unpark_note`
# = "L2 KHÔNG chạy cho plan này … không có gì cần JIT tài trợ", do writer lập plan ghi. Chạy
# merge với artifact L2 THẬT ⇒ sinh lệnh bán JIT vào orders[] trong khi câu đó vẫn nằm đó ⇒
# người duyệt đọc một câu khẳng định NGƯỢC HẲN với lệnh thật. Đúng lớp #5/#6, tầng cấp plan.
print("\n[S5e] namespace `jit_*` CẤP PLAN — dựng-lại-hoặc-vắng-mặt")

# Câu chữ chép từ plan thật (rút gọn), để ca này không phải giả định vô căn cứ.
REAL_NOTE = ("L2 (compute_jit_unpark.py) KHÔNG chạy cho plan này — plan này có 0 lệnh mua "
             "BAL/LAG. Không có gì cần JIT tài trợ.")
p_note = plan(jit_unpark_note=REAL_NOTE)
check("S5e tiền đề: khoá jit_unpark_note CÓ trong plan đầu vào (câu chữ từ plan thật)",
      p_note["jit_unpark_note"] == REAL_NOTE)

# (a) L2 ĐƯỢC NHẬN ⇒ có lệnh bán JIT thật ⇒ câu "không có gì cần JIT" phải BIẾN MẤT.
pe1, re1 = merge_park_orders(copy.deepcopy(p_note), L1_roomy, L2_roomy)
check("S5e L2 được nhận ⇒ khoá jit_* cấp plan của writer khác bị XOÁ",
      "jit_unpark_note" not in pe1, str(pe1.get("jit_unpark_note"))[:90])
check("S5e tiền đề của (a): lần chạy đó THẬT SỰ sinh lệnh bán (nếu không, ca vô nghĩa)",
      any(o["side"] == "sell" for o in pe1["orders"]))
check("S5e có cảnh báo nêu ĐÍCH DANH khoá đã xoá (không xoá im lặng)",
      any("jit_unpark_note" in w and "CẤP PLAN" in w for w in re1["warnings"]),
      str(re1["warnings"]))
check("S5e khoá merge SỞ HỮU vẫn được dựng lại ở cùng lần chạy đó",
      "✅" in pe1["jit_unpark_proposal"]["_merged_into_orders"])

# (b) L2 BỊ TỪ CHỐI ⇒ vẫn không sống sót. Đây là nửa quan trọng của "dựng-lại-HOẶC-VẮNG-MẶT":
#     xoá phải xảy ra ĐỘC LẬP với việc tầng L2 có được nhận hay không.
pe2, _ = merge_park_orders(copy.deepcopy(p_note), L1_roomy, L2_rejected)
check("S5e L2 BỊ TỪ CHỐI ⇒ khoá jit_* cấp plan vẫn KHÔNG sống sót",
      "jit_unpark_note" not in pe2, str(pe2.get("jit_unpark_note"))[:90])
check("S5e tiền đề của (b): tầng L2 đúng là bị từ chối ở lần chạy đó",
      "⛔" in pe2["jit_unpark_proposal"]["_merged_into_orders"])

# (c) KHÔNG có artifact L2 nào ⇒ vẫn xoá, và cảnh báo VẮNG MẶT của bản vá #6 KHÔNG được
#     mất (bước 0b xoá trước nên `p.pop()` ở bước 6 luôn trả None — bẫy tự bắn vào chân).
p_both = copy.deepcopy(pe1)                      # có sẵn khối jit_unpark_proposal "ĐÃ MERGE"
p_both["jit_unpark_note"] = REAL_NOTE            # + khoá của writer khác quay lại
pe3, re3 = merge_park_orders(p_both, L1_roomy, None)
check("S5e không có artifact L2 ⇒ CẢ khối sở hữu LẪN khoá writer khác đều vắng mặt",
      "jit_unpark_proposal" not in pe3 and "jit_unpark_note" not in pe3,
      str([k for k in pe3 if k.startswith("jit_")]))
check("S5e cảnh báo VẮNG MẶT (bản vá #6) KHÔNG bị bước 0b nuốt mất",
      any("VẮNG MẶT" in w and "jit_unpark_proposal" in w for w in re3["warnings"]),
      str(re3["warnings"]))

# (d) CHỨNG MINH NGƯỢC — biên của phạm vi xoá. Khoá cấp plan KHÔNG mang tiền tố `jit_` phải
#     còn NGUYÊN. Hai ca thật: `duplicate_jit_fix_note` (có chữ "jit", không có tiền tố) và
#     `park_trim_proposal` (tầng L1, do bước 6 tự quản theo luật riêng của nó).
FIX_NOTE = "SUA LOI 2026-08-07 … da xoa 15 lenh JIT goc khoi orders[]"
p_bound = plan(jit_unpark_note=REAL_NOTE, duplicate_jit_fix_note=FIX_NOTE,
               plan_note="khoa cua mot tinh nang hoan toan khac", jitter_budget_vnd=1_000_000)
pe4, _ = merge_park_orders(p_bound, L1_roomy, L2_roomy)
check("S5e chứng minh ngược: khoá cấp plan NGOÀI namespace `jit_` KHÔNG bị đụng",
      pe4.get("duplicate_jit_fix_note") == FIX_NOTE
      and pe4.get("plan_note") == "khoa cua mot tinh nang hoan toan khac"
      and pe4.get("jitter_budget_vnd") == 1_000_000
      and pe4.get("account") == "ZaloPay" and pe4.get("plan_date") == "2026-08-11",
      str({k: pe4.get(k) for k in ("duplicate_jit_fix_note", "plan_note",
                                   "jitter_budget_vnd")})[:200])
check("S5e chứng minh ngược: khoá trong namespace ở CÙNG plan đó thì có bị xoá thật "
      "(nếu không, ca (d) xanh vì merge chẳng xoá gì cả)",
      "jit_unpark_note" not in pe4)
check("S5e chứng minh ngược: khối L1 park_trim_proposal vẫn được dựng lại như cũ",
      "✅" in pe4["park_trim_proposal"]["_merged_into_orders"])
# `jitter_budget_vnd` là ca RANH GIỚI CHỮ: "jit" + "ter" — chỉ khoá bắt đầu bằng `jit_` mới
# thuộc namespace, `jitter_` thì không. Nếu ai đó đổi sang `k.startswith("jit")` (thiếu gạch
# dưới) ca trên sẽ ĐỎ.

# (e) IDEMPOTENT trên chính ca này: chạy 2 lần liên tiếp cùng input ⇒ plan giống hệt.
#     Lưu ý ĐÃ ĐO, không phải khẳng định suông: `warnings` KHÁC nhau (lần 2 không còn khoá
#     writer khác để mà báo đã xoá) — đó là quan sát VỀ ĐẦU VÀO, không phải trạng thái plan.
pe5a, re5a = merge_park_orders(copy.deepcopy(p_note), L1_roomy, L2_roomy)
pe5b, re5b = merge_park_orders(copy.deepcopy(pe5a), L1_roomy, L2_roomy)
check("S5e idempotent: lần 2 == lần 1 trên MỌI field trừ khối nhật ký", _blob(pe5a) == _blob(pe5b))
check("S5e idempotent: orders[] byte-identical",
      json.dumps(pe5a["orders"], sort_keys=True, ensure_ascii=False) ==
      json.dumps(pe5b["orders"], sort_keys=True, ensure_ascii=False))
check("S5e idempotent: 0 khoá jit_* lạ ở CẢ hai lần",
      [k for k in pe5a if k.startswith("jit_")] == ["jit_unpark_proposal"]
      and [k for k in pe5b if k.startswith("jit_")] == ["jit_unpark_proposal"],
      str([sorted(k for k in pe5a if k.startswith("jit_")),
           sorted(k for k in pe5b if k.startswith("jit_"))]))
check("S5e idempotent: chênh lệch DUY NHẤT là cảnh báo về đầu vào (nêu tên, không giấu)",
      any("jit_unpark_note" in w for w in re5a["warnings"])
      and not any("jit_unpark_note" in w for w in re5b["warnings"]),
      str(re5b["warnings"]))

# (f) REFUSED ⇒ plan NGUYÊN VẸN, kể cả khoá cấp plan. Cùng bất biến S5b/S6 canh: fail-closed
#     không được sửa gì trên đĩa.
p_ref = copy.deepcopy(p_note)
p_ref["approved_by"] = "user (John) Discord"
pe6, re6 = merge_park_orders(copy.deepcopy(p_ref), L1_roomy, L2_roomy)
check("S5e REFUSED ⇒ khoá jit_* cấp plan GIỮ NGUYÊN (cố ý — caller không ghi file)",
      re6["status"] == "REFUSED"
      and json.dumps(pe6, sort_keys=True) == json.dumps(p_ref, sort_keys=True),
      str(re6["errors"]))


# ── S6: lệnh ngoài vùng sở hữu ĐÃ vượt trần ⇒ REFUSED, plan không đổi ────────────────
huge_foreign = {"id": "SELL-VHM-BAL-01", "ticker": "VHM", "side": "sell", "qty": 400,
                "ref_price": 76500.0, "book": "BAL", "play_type": "EXIT", "priority": 0,
                "sellable": 300}
before = plan([huge_foreign, buy_order()])
after, r6 = merge_park_orders(copy.deepcopy(before), L1_over, L2_over)
check("S6 lệnh ngoài vùng đã vượt trần ⇒ REFUSED (không phải việc merge sửa)",
      r6["status"] == "REFUSED", str(r6["errors"]))
check("S6 plan trả về NGUYÊN VẸN khi REFUSED",
      json.dumps(after, sort_keys=True) == json.dumps(before, sort_keys=True))


# ══════════════════════════════════════════════════════════════════════════════════════
# A — CỔNG DUYỆT
# ══════════════════════════════════════════════════════════════════════════════════════
print("\n[A] Cổng duyệt — không tự duyệt, không sửa lén plan đã duyệt")

pa, ra = merge_park_orders(plan(approved_by="user (John) Discord"), L1_0807, L2_0807)
check("A1 plan ĐÃ duyệt ⇒ REFUSED, không sửa", ra["status"] == "REFUSED")
check("A1 orders[] giữ nguyên", len(pa["orders"]) == 1)
pa2, ra2 = merge_park_orders(plan(approved_by="user (John) Discord"), L1_0807, L2_0807,
                             allow_approved=True)
check("A2 --force-clear-approval ⇒ chạy được NHƯNG xoá approved_by (buộc duyệt lại)",
      ra2["status"] == "OK" and pa2["approved_by"] is None)
# ── A5: cổng duyệt phải đọc ĐỦ tập tên field mà tầng dưới công nhận ─────────────────
# quant-skeptic vòng 8 — lỗ FAIL-OPEN thật, trên chính cái cổng sinh ra để fail-closed:
# `trading_bot/plan.py:182-183` hồi sinh `approved_by` từ `approved_by_user`, và
# `preflight_check.sh:60` cũng công nhận tên đó. Cổng cũ chỉ đọc `approved_by` ⇒ plan duyệt
# bằng tên thay thế KHÔNG bị từ chối, orders[] bị dựng lại, rồi `load_plan()` gắn lại chữ ký
# ⇒ lệnh MỚI chạy dưới chữ ký duyệt của bộ lệnh CŨ. Hôm nay 0/84 plan mang field đó — lỗ TIỀM
# ẨN, và "hôm nay chưa ai dùng" là sự thật CÓ HẠN SỬ DỤNG.
p_alias = plan()
p_alias.pop("approved_by", None)
p_alias["approved_by_user"] = "user (John) Discord"
pa5, ra5 = merge_park_orders(copy.deepcopy(p_alias), L1_0807, L2_0807)
check("A5 plan duyệt bằng TÊN THAY THẾ `approved_by_user` ⇒ vẫn REFUSED (không fail-open)",
      ra5["status"] == "REFUSED" and "approved_by_user" in ra5["errors"][0],
      f"status={ra5['status']} errors={ra5['errors']}")
check("A5 REFUSED ⇒ plan trả về NGUYÊN VẸN (orders[] không bị dựng lại)",
      json.dumps(pa5, sort_keys=True) == json.dumps(p_alias, sort_keys=True))
# chứng minh ngược 1: bỏ chữ ký ra thì merge CHẠY THẬT — ca trên không xanh vì lý do khác
p_noalias = copy.deepcopy(p_alias)
p_noalias["approved_by_user"] = None
pa5b, ra5b = merge_park_orders(p_noalias, L1_0807, L2_0807)
check("A5 chứng minh ngược: cùng plan nhưng KHÔNG có chữ ký ⇒ chạy được, có sinh lệnh",
      ra5b["status"] == "OK" and any(o["side"] == "sell" for o in pa5b["orders"]),
      f"status={ra5b['status']}")
# chứng minh ngược 2: --force-clear-approval phải gỡ chữ ký ở MỌI tên field, nếu không
# `load_plan()` sẽ hồi sinh nó và lệnh mới chạy dưới chữ ký cũ.
pa5c, ra5c = merge_park_orders(copy.deepcopy(p_alias), L1_0807, L2_0807, allow_approved=True)
check("A5 --force-clear-approval gỡ chữ ký ở MỌI tên field (không sót alias)",
      ra5c["status"] == "OK"
      and not any(pa5c.get(k) for k in ("approved_by", "approved_by_user")),
      str({k: pa5c.get(k) for k in ("approved_by", "approved_by_user")}))
check("A5 mô phỏng `plan.py:182-183`: sau khi gỡ, KHÔNG hồi sinh được chữ ký nào",
      not (pa5c.get("approved_by") or pa5c.get("approved_by_user")))
check("A5 tiền đề: mô phỏng đó THẬT SỰ hồi sinh được nếu còn sót alias (ca không vô căn cứ)",
      (lambda d: bool(d.get("approved_by") or d.get("approved_by_user")))(
          dict(pa5c, approved_by_user="user (John) Discord")))
check("A5 cả 2 tên field đều nằm trong hằng số cổng duyệt (thêm alias mới phải sửa 1 chỗ)",
      set(mpo_APPROVAL_KEYS) == {"approved_by", "approved_by_user"},
      str(mpo_APPROVAL_KEYS))

# ── A5b: TỰ PHÁT HIỆN alias, không chốt danh sách literal ────────────────────────────
# quant-skeptic vòng 9: ca A5 trên chỉ ghim ĐÚNG 2 tên ĐANG CÓ ⇒ một alias thứ 3 thêm ở tầng
# dưới sau này sẽ **lặng lẽ mở lại lỗ fail-open** với selfcheck vẫn xanh. Đó chính xác là khuyết
# tật #6b (bản neo bằng danh sách literal) mà vòng 5 đã REFUTED một lần rồi — tôi vừa tái phạm
# ở một tầng khác. Ca này QUÉT mã nguồn 2 tầng dưới để suy ra tập alias THẬT, rồi so với hằng số.
# Nó biến "một lần grep tay của người" thành CỔNG THƯỜNG TRỰC.
_WC = "/home/trido/thanhdt/WorkingClaude"
_LOWER_LAYERS = [f"{_WC}/trading_bot/plan.py", f"{_WC}/mike/bin/preflight_check.sh"]
_discovered, _readable = set(), []
for _p in _LOWER_LAYERS:
    try:
        _src = open(_p, encoding="utf-8").read()
    except OSError:
        continue
    _readable.append(_p)
    # bắt mọi tên field dạng `approved_by*` được ĐỌC ra khỏi dict plan
    for _m in re.finditer(r'["\'](approved_by\w*)["\']', _src):
        _discovered.add(_m.group(1))
check("A5b tiền đề: đọc được CẢ 2 file tầng dưới (bộ lọc rỗng ⇒ ca vô căn cứ)",
      len(_readable) == 2, f"đọc được: {_readable}")
check("A5b tập alias TỰ PHÁT HIỆN ở tầng dưới == hằng số cổng duyệt (alias mới ⇒ ca này ĐỎ)",
      _discovered == set(mpo_APPROVAL_KEYS),
      f"phát hiện={sorted(_discovered)} vs hằng số={sorted(mpo_APPROVAL_KEYS)} — "
      f"nếu tầng dưới vừa thêm alias, THÊM VÀO _APPROVAL_KEYS chứ đừng nới ca này")
check("A5b chứng minh ngược: thêm một alias giả vào tập phát hiện ⇒ phép so PHẢI gãy "
      "(nếu không, ca trên xanh vì so hai tập rỗng)",
      (_discovered | {"approved_by_ceo"}) != set(mpo_APPROVAL_KEYS) and len(_discovered) >= 2)

check("A3 merge KHÔNG BAO GIỜ tự ghi approved_by",
      p1.get("approved_by") is None and p1["requires_user_approval"] is True)
# A4 — mọi nhánh trả về (kể cả REFUSED SỚM ở cổng duyệt) phải có report ĐỦ KHOÁ cho caller.
# Bug thật 2026-08-10: `refuse()` ở cổng duyệt trả về trước khi `layers` được điền ⇒ print_report
# KeyError('L1'). Selfcheck hàm thuần 58/58 xanh vẫn không thấy — chỉ chạy CLI thật mới lộ.
#
# ⚠️ Bản đầu của ca này CHỈ so `set(_rp["layers"])` trên 3 nhánh rồi gọi `print_report` đúng
# MỘT lần — tức là kiểm HÌNH DẠNG bằng proxy, trong khi print_report còn đọc `dropped_owned`
# / `per_ticker` / `invariants` / `warnings` / `errors` mà proxy đó không phủ (quant-skeptic
# vòng 3, 2026-08-10). Bản này GỌI THẬT print_report trên cả 5 nhánh (thêm I1-dup và
# không-artifact) và bắt lỗi tại chỗ, thay vì suy từ tập khoá.
_dupe = dict(buy_order(oid="BUY-DUP-01"))
_, r_dup = merge_park_orders(plan([_dupe, dict(_dupe)]), L1_0807, L2_0807)
_, r_noart = merge_park_orders(plan(), None, None)
for _nm, _rp in (("REFUSED-đã-duyệt", ra), ("REFUSED-vượt-trần", r6), ("OK", rep),
                 ("REFUSED-I1-dup", r_dup), ("không-artifact", r_noart)):
    _buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(_buf):
            print_report(_rp)          # ← chạy THẬT, không phải proxy hình dạng
        _err = None
    except Exception as e:             # noqa: BLE001 — đây chính là thứ cần bắt
        _err = f"{type(e).__name__}: {e}"
    _out = _buf.getvalue()
    check(f"A4 print_report CHẠY THẬT không nổ ở nhánh {_nm}",
          _err is None and _out.startswith("status:") and len(_out.splitlines()) >= 3,
          _err or repr(_out[:120]))
check("A4 nhánh I1-dup đúng là REFUSED vì id trùng (không phải nhánh khác)",
      r_dup["status"] == "REFUSED"
      and any("I1" in e for e in r_dup["errors"]), str(r_dup["errors"]))
# chứng minh ngược: bỏ phần trùng id ra thì CHÍNH plan đó chạy OK ⇒ ca trên không vô căn cứ
check("A4 chứng minh ngược: cùng plan nhưng id KHÔNG trùng ⇒ OK",
      merge_park_orders(plan([_dupe, buy_order(oid="BUY-DUP-02")]),
                        L1_0807, L2_0807)[1]["status"] == "OK")
# nhánh OK phải thực sự có dữ liệu để print_report ĐỤNG tới, không phải in rỗng
check("A4 nhánh OK có dropped_owned + per_ticker + invariants khác rỗng (print_report đọc thật)",
      rep["dropped_owned"] and rep["per_ticker"] and rep["invariants"])
print_report(ra)  # in ra màn hình 1 nhánh làm bằng chứng mắt thường


# ══════════════════════════════════════════════════════════════════════════════════════
# V — BẤT BIẾN + biên
# ══════════════════════════════════════════════════════════════════════════════════════
print("\n[V] Bất biến hậu kiểm + ca biên")

check("V1 lệnh bán chạy TRƯỚC lệnh mua (priority nhỏ hơn)",
      max(o["priority"] for o in p1["orders"] if o["side"] == "sell")
      < min(o["priority"] for o in p1["orders"] if o["side"] == "buy"))
# V1b — lệnh MUA ở priority 0. Bản đầu clamp `max(0, min(buy)-1)` ⇒ bán và mua BẰNG nhau ⇒ I3
# hỏng ⇒ TỪ CHỐI CẢ PLAN ⇒ 0 lệnh bán PARK = đúng hình dạng mất-phiên 08-06.
# ⚠️ Bản đầu của ca này assert `all(... for o in ... if side=='sell')` trên plan bị REFUSED —
# danh sách RỖNG nên `all()` trả True VÔ CĂN CỨ, che mất chính lỗi nó tuyên bố kiểm
# (quant-skeptic bắt được 2026-08-10). Ca mới bắt buộc status OK + tập lệnh bán KHÁC RỖNG
# trước khi so priority.
pv, rv1b = merge_park_orders(plan([buy_order(pri=0)]), L1_0807, None)
pv_sells = [o for o in pv["orders"] if o["side"] == "sell"]
check("V1b lệnh mua priority=0 ⇒ KHÔNG từ chối plan (status OK)",
      rv1b["status"] == "OK", str(rv1b["errors"]))
check("V1b vẫn sinh đủ 3 lệnh bán (tập KHÁC RỖNG — chống assert vô căn cứ)",
      len(pv_sells) == 3, f"{len(pv_sells)} lệnh bán")
check("V1b bán ở priority −1 < mua 0 (priority ÂM hợp lệ: chỉ dùng làm khoá sắp xếp)",
      pv_sells and all(o["priority"] == -1 for o in pv_sells),
      str([o["priority"] for o in pv_sells]))
check("V2 mọi bất biến PASS ở ca bình thường",
      all(c["ok"] for c in rep["invariants"]),
      str([c for c in rep["invariants"] if not c["ok"]]))
check("V3 id sinh ra deterministic theo mã (không đánh số chạy)",
      {o["id"] for o in p1["orders"] if o["side"] == "sell"} ==
      {"PARKMERGE-SELL-BID", "PARKMERGE-SELL-VHM", "PARKMERGE-SELL-VCB"})
check("V4 mọi lệnh sinh ra mang dấu sở hữu",
      all(o.get("merge_owner") == OWNER for o in p1["orders"] if o["side"] == "sell"))

# ── V5: ref_price L1≠L2 ⇒ cảnh báo + lấy giá thấp, KHÔNG dừng (bài học 08-06) ────────
pv5, rv5 = merge_park_orders(
    plan(), l1_art([s("BID", 200, 37900, 900)]),
    l2_art([s("BID", 100, 38500, 900, play="JIT_UNPARK")]))
sell = [o for o in pv5["orders"] if o["ticker"] == "BID"][0]
check("V5 ref_price lệch ⇒ dùng giá THẤP hơn, vẫn merge",
      rv5["status"] == "OK" and sell["ref_price"] == 37900.0 and sell["qty"] == 300)
check("V5 có cảnh báo về lệch giá",
      any("ref_price L1≠L2" in w for w in rv5["warnings"]))

# ── V6: buy_amendments trỏ order_id không tồn tại ⇒ cảnh báo, KHÔNG tạo lệnh mới ─────
pv6, rv6 = merge_park_orders(
    plan(), None, l2_art([s("BID", 100, 37900, 900, play="JIT_UNPARK")],
                         amendments=[{"order_id": "BUY-GHOST-99", "status": "x",
                                      "qty_final": 100}]))
check("V6 amendment mồ côi ⇒ cảnh báo, không tạo lệnh mua ma",
      rv6["status"] == "OK"
      and not any(o["id"] == "BUY-GHOST-99" for o in pv6["orders"])
      and any("KHÔNG có trong orders[]" in w for w in rv6["warnings"]))

# ── V7: merge KHÔNG đổi qty lệnh mua kể cả khi L2 báo qty_final khác ─────────────────
pv7, rv7 = merge_park_orders(
    plan(), None, l2_art([s("BID", 100, 37900, 900, play="JIT_UNPARK")],
                         amendments=[{"order_id": "BUY-DRI-LAG-01", "status": "SHRUNK",
                                      "qty_final": 900}]))
check("V7 L2 qty_final=900 ≠ plan 1800 ⇒ GIỮ 1800, chỉ cảnh báo",
      [o for o in pv7["orders"] if o["side"] == "buy"][0]["qty"] == 1800
      and any("GIỮ NGUYÊN qty" in w for w in rv7["warnings"]))

# ── V8: artifact rác (thiếu ref_price / qty âm) ⇒ bỏ lệnh đó, không crash ────────────
pv8, rv8 = merge_park_orders(
    plan(), l1_art([{"ticker": "XXX", "side": "sell", "qty": 100, "sellable": 500},
                    s("BID", 200, 37900, 900)]), None)
check("V8 lệnh thiếu ref_price bị bỏ, lệnh hợp lệ vẫn chạy",
      rv8["status"] == "OK" and sell_qty(pv8, "XXX") == 0 and sell_qty(pv8, "BID") == 200)

# ── V9: plan không có lệnh mua nào ⇒ vẫn merge được lệnh bán ─────────────────────────
pv9, rv9 = merge_park_orders(plan([]), L1_0807, None)
check("V9 plan rỗng orders[] ⇒ vẫn sinh lệnh bán, priority 0",
      rv9["status"] == "OK" and len(pv9["orders"]) == 3
      and all(o["priority"] == 0 for o in pv9["orders"]))

# ── V10: plan gốc KHÔNG bị sửa tại chỗ (pure function) ───────────────────────────────
src = plan()
snapshot = json.dumps(src, sort_keys=True)
merge_park_orders(src, L1_0807, L2_0807)
check("V10 plan đầu vào không bị mutate", json.dumps(src, sort_keys=True) == snapshot)

# ── V12: artifact trả qty LẺ (không bội lô) ⇒ làm tròn XUỐNG, KHÔNG từ chối cả plan ──
#   quant-skeptic vòng 2: bản trước để I4 chặn cứng ⇒ 1 qty lẻ giết cả plan = lại đúng hình
#   dạng mất-phiên 08-06. Phơi nhiễm hiện tại bằng 0 (compute_park_trim dùng round_lot,
#   compute_jit_unpark cấp theo bội LOT) nhưng đó là bất biến của FILE KHÁC.
pv12, rv12 = merge_park_orders(plan(), l1_art([s("BID", 250, 37900, 900)]), None)
check("V12 qty lẻ 250 ⇒ làm tròn xuống 200, status vẫn OK (không bắt cả plan làm con tin)",
      rv12["status"] == "OK" and sell_qty(pv12, "BID") == 200,
      f"status={rv12['status']} qty={sell_qty(pv12, 'BID')}")
check("V12 có cảnh báo nêu rõ đã làm tròn",
      any("không phải bội 100" in w for w in rv12["warnings"]), str(rv12["warnings"]))
# chứng minh ngược: I4 thấy lệnh "giống của merge" qty lẻ do writer KHÁC ghi ⇒ cảnh báo, KHÔNG chặn
odd_foreign = {"id": "SELL-ODD-PARK-01", "ticker": "ODD", "side": "sell", "qty": 150,
               "ref_price": 1000.0, "book": "PARK", "play_type": "PARK_TRIM", "priority": 0,
               "merge_owner": OWNER}
pv12b, rv12b = merge_park_orders(plan([odd_foreign, buy_order()]), L1_0807, None)
i4 = [c for c in rv12b["invariants"] if c["name"].startswith("I4")][0]
check("V12b chứng minh ngược: I4 vẫn PHÁT HIỆN được qty lẻ, chỉ là không chặn nữa",
      rv12b["status"] == "OK" and i4["ok"] is True,
      "lệnh lẻ thuộc vùng sở hữu nên bị xoá+dựng lại ⇒ I4 sạch: " + str(i4))

# ── V11: lệnh bán của writer KHÁC nằm SAU lệnh mua ⇒ cảnh báo (I3b), KHÔNG chặn ──────
#   Khác ca S6 có chủ đích: ở S6 chạy tiếp làm tình trạng vượt sellable NẶNG THÊM ⇒ fail-closed.
#   Ở đây lệnh của người khác sai thứ tự là vấn đề CÓ SẴN, merge không làm nặng thêm ⇒ từ chối
#   cả plan chỉ tái lập đúng hình dạng mất-phiên 08-06.
late = {"id": "SELL-XXX-BAL-09", "ticker": "XXX", "side": "sell", "qty": 100,
        "ref_price": 1000.0, "book": "BAL", "play_type": "EXIT", "priority": 9}
pv11, rv11 = merge_park_orders(plan([late, buy_order()]), L1_0807, None)
i3b = [c for c in rv11["invariants"] if c["name"].startswith("I3b")][0]
check("V11 lệnh bán ngoài vùng chạy SAU mua ⇒ I3b báo, nhưng plan vẫn OK",
      rv11["status"] == "OK" and i3b["ok"] is False
      and "SELL-XXX-BAL-09" in i3b["detail"], str(i3b))
check("V11 chứng minh ngược: lệnh đó ở priority 0 ⇒ I3b sạch",
      [c for c in merge_park_orders(
          plan([dict(late, priority=0), buy_order()]), L1_0807, None)[1]["invariants"]
       if c["name"].startswith("I3b")][0]["ok"] is True)


# ══════════════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
if FAILS:
    print(f"FAIL — {len(FAILS)} ca hỏng:")
    for f in FAILS:
        print(f"  · {f}")
    sys.exit(1)
print("PASS — toàn bộ selfcheck merge_park_orders")
