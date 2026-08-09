#!/usr/bin/env python3
"""Vá 3 lỗi phái sinh của bản patch giá 2026-08-09 (commit 09f1821b/a29ab4f) trên plan 08-10.

Bản patch đó đổi ref_price = anchor THẬT (đúng, vì trần cứng nay do load_plan suy ra), nhưng
giữ nguyên qty và không cập nhật các số tổng phái sinh. Hệ quả đo được:
  1. qty vẫn = floor(slot / (anchor/1,04)) ⇒ ở giá xấu nhất (khớp đúng anchor) giá trị lệnh
     VƯỢT slot 2,6–3,4%. Giá ràng buộc thật bây giờ là anchor ⇒ phải re-derive qty theo anchor.
     Chính patch của Taylor ghi "sizing là quyết định của DollarBill/user" ⇒ đây là việc của tôi.
  2. orders_summary.buy_gross_vnd còn số CŨ (thiếu 5,98tr SpaceX / 3,85tr ZaloPay) và
     cash_after_all_orders_vnd không khớp chính net_cash_change của nó.
  3. lag_analysis.enforcement_anchor còn mô tả mẹo cũ "ref_price = anchor/1,04" — đã bị thay.

KHÔNG đụng: L1 park_trim, L2 jit_unpark, lệnh BÁN, state, nav_basis, approved_by.
"""
import json
import math
import os
import csv

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
PLAN_DIR = os.path.join(WORKDIR, "data/trade_plans")
CSV_PATH = os.path.join(WORKDIR, "deploy_golive_dt5g_v4/out/golive_v23_recommendations_2026-08-07.csv")
FEE_RATE = 0.00075  # 0,075% — phí thật đã xác minh (coding_guidelines §6)
LOT = 100

# weight_pct lấy từ chính CSV golive (weight_base = LAG_book), không hardcode.
weights = {}
with open(CSV_PATH, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r.get("ticker"):
            weights[r["ticker"]] = (float(r["weight_pct"]) / 100.0, r.get("weight_base"))

ENFORCEMENT_NEW = {
    "co_che": "TRẦN GIÁ TUYỆT ĐỐI bằng CODE — không còn mẹo neo ref_price.",
    "chi_tiet": (
        "load_plan() (trading_bot/plan.py, commit 319e1b2) tự suy "
        "hard_no_chase_ceiling_vnd = entry_anchor_price cho MỌI lệnh mua có anchor — enforce ở "
        "MỘT chỗ, không phụ thuộc plan generator có nhớ ghi field thứ hai hay không. "
        "Executor._limit_price (commit a29ab4f) đặt giá = min(giá chào thật q.ask, "
        "ref×(1+chase), trần phiên, TRẦN CỨNG) và trả None (KHÔNG đặt lệnh) nếu ngay cả giá "
        "SÀN phiên đã > trần cứng. Giá trị rác chỉ được RƠI VỀ anchor, không vô hiệu hoá trần "
        "(commit aa0afea)."
    ),
    "da_kiem_chung_that": (
        "Nạp plan qua load_plan('2026-08-10', <account>) ngày 2026-08-09: cả 8 lệnh mua (4/account) "
        "đều có HARD_CEIL = đúng anchur tương ứng (DRI 13.000, POW 13.400, SCL 24.200, SSI 24.450). "
        "Kiểm chứng bằng CHẠY THẬT, không suy từ việc code đã commit."
    ),
    "vi_sao_bo_meo_cu": (
        "Mẹo cũ (ref_price = anchor/1,04) giả định chase cap luôn = 4%, nhưng "
        "chase = clamp(2×rvol20d, 1,5%, 4%) ⇒ khi rvol thấp trần thực chỉ ≈ 0,976×anchor, "
        "chặt hơn luật user duyệt và trôi theo rvol mỗi ngày. Nay bỏ hẳn."
    ),
    "he_qua_sizing": (
        "Vì giá ràng buộc thật đổi từ anchor/1,04 sang anchor, qty phải re-derive theo anchor — "
        "xem sizing_note từng lệnh (sửa 2026-08-09, job DollarBill_20260809_131002)."
    ),
}


def fix(account):
    path = os.path.join(PLAN_DIR, f"plan_{account}_2026-08-10.json")
    with open(path, encoding="utf-8") as f:
        d = json.load(f)

    lag_book = d["lag_analysis"]["sizing_basis"]["lag_book_vnd"]
    changes = []

    for o in d["orders"]:
        if o["side"] != "buy" or o.get("book") != "LAG":
            continue
        tk = o["ticker"]
        anchor = float(o["entry_anchor_price"])
        w, wbase = weights[tk]
        assert wbase == "LAG_book", f"{tk}: weight_base={wbase}, kỳ vọng LAG_book"
        assert float(o["ref_price"]) == anchor, f"{tk}: ref_price != anchor, dừng"
        slot = w * lag_book
        # Giá ràng buộc = anchor (trần cứng). Sizing phải bảo đảm notional ≤ slot ở MỌI kịch bản.
        new_qty = int(math.floor(slot / anchor / LOT)) * LOT
        old_qty = o["qty"]
        if new_qty == old_qty:
            continue
        assert new_qty < old_qty, f"{tk}: qty mới {new_qty} > cũ {old_qty} — không được PHÌNH lệnh"
        assert new_qty > 0, f"{tk}: qty mới = 0"
        cost = new_qty * anchor
        assert cost <= slot, f"{tk}: {cost} vẫn > slot {slot}"
        o["qty"] = new_qty
        o["estimated_cost_vnd"] = int(round(cost))
        o["fee_est_vnd"] = int(round(cost * FEE_RATE))
        o["total_with_fee_vnd"] = o["estimated_cost_vnd"] + o["fee_est_vnd"]
        o["sizing_note"] += (
            f" ⚠️ SỬA 2026-08-09 (job DollarBill_20260809_131002) — re-derive qty theo giá ràng "
            f"buộc THẬT: bản patch giá giữ qty {old_qty:,}cp vốn được tính bằng "
            f"floor(slot / (anchor/1,04)); nhưng trần cứng nay = anchor {anchor:,.0f}đ nên ở giá "
            f"xấu nhất lệnh sẽ là {old_qty * anchor:,.0f}đ = VƯỢT slot {slot:,.0f}đ "
            f"({old_qty * anchor / slot - 1:+.1%}). qty đúng = floor(slot / anchor) làm tròn lô "
            f"{LOT} = {new_qty:,}cp = {cost:,.0f}đ ≤ slot ✅ (bảo đảm trong MỌI kịch bản khớp, vì "
            f"anchor là giá cao nhất có thể khớp). Đây là thu hẹp theo đúng luật sizing của "
            f"engine, KHÔNG phải hạ qty để lách luật giá."
        )
        changes.append((tk, old_qty, new_qty, old_qty * anchor, cost, slot))

    # --- tổng hợp lại từ CHÍNH orders[], không tin số cũ ---
    buys = [o for o in d["orders"] if o["side"] == "buy"]
    sells = [o for o in d["orders"] if o["side"] == "sell"]
    bg = sum(o["qty"] * o["ref_price"] for o in buys)
    sg = sum(o["qty"] * o["ref_price"] for o in sells)
    bfee = int(round(bg * FEE_RATE))
    sfee = int(round(sg * FEE_RATE))
    buy_tot = int(round(bg)) + bfee
    sell_net = int(round(sg)) - sfee
    cash0 = float(d["nav_basis"]["available_cash_vnd"])
    funding = cash0 + sell_net
    cash_end = funding - buy_tot
    assert buy_tot <= funding, "VI PHẠM kỷ luật tiền mặt"

    s = d["orders_summary"]
    s.update({
        "total_orders": len(d["orders"]),
        "total_sell_orders": len(sells),
        "total_buy_orders": len(buys),
        "sell_gross_vnd": int(round(sg)),
        "sell_fee_est_vnd": sfee,
        "sell_net_proceeds_vnd": sell_net,
        "buy_gross_vnd": int(round(bg)),
        "buy_fee_est_vnd": bfee,
        "buy_total_with_fee_vnd": buy_tot,
        "net_cash_change_vnd": sell_net - buy_tot,
        "available_cash_before_vnd": cash0,
        "cash_after_all_orders_vnd": int(round(cash_end)),
        "funding_check_sell_ge_buy": sell_net >= buy_tot,
        "orders_within_cash": buy_tot <= funding,
        "recomputed_note": (
            "Mọi số tổng ở khối này TÍNH LẠI TỪ orders[] ngày 2026-08-09 (job "
            "DollarBill_20260809_131002). Bản trước còn số CŨ từ trước bản patch giá: "
            "buy_gross ghi 139.940.000đ (SpaceX) / 90.070.000đ (ZaloPay) trong khi orders[] thật "
            "đã là 145.920.000đ / 93.920.000đ, và cash_after_all_orders không khớp chính "
            "net_cash_change của nó. Đã đối chiếu lại bằng máy: tổng khớp orders[] 100%."
        ),
    })

    d["cash_planning"].update({
        "available_cash_vnd": cash0,
        "discipline_check": (
            f"Câu hỏi bắt buộc: tổng orders[] MUA có ≤ sức mua thực, KHÔNG giả định gì thêm? "
            f"MUA = {buy_tot:,}đ. Nguồn = cash {cash0:,.0f}đ + bán PARK ròng {sell_net:,}đ (nằm "
            f"NGAY TRONG orders[] này, priority 0, chạy TRƯỚC) = {funding:,.0f}đ ≥ {buy_tot:,}đ ✅. "
            f"KHÔNG có field funding_required, KHÔNG có câu 'chờ user nạp tiền', KHÔNG giả định "
            f"ngầm nào. (Số đã tính lại từ orders[] 2026-08-09.)"
        ),
        "cash_end_after_all_vnd": int(round(cash_end)),
    })

    d["lag_analysis"]["enforcement_anchor"] = ENFORCEMENT_NEW
    d["slot_sizing_fix_2026-08-09"] = {
        "job": "DollarBill_20260809_131002",
        "why": (
            "Bản patch giá (ref_price = anchor) đúng về cơ chế nhưng để lại 3 số phái sinh sai: "
            "qty chưa re-derive theo giá ràng buộc mới, orders_summary còn số cũ, "
            "enforcement_anchor mô tả cơ chế đã bị thay."
        ),
        "qty_changes": [
            {"ticker": t, "qty_old": qo, "qty_new": qn,
             "notional_old_vnd": int(round(no)), "notional_new_vnd": int(round(nn)),
             "slot_vnd": int(round(sl)), "overshoot_old": round(no / sl - 1, 4)}
            for t, qo, qn, no, nn, sl in changes
        ],
        "not_changed": "L1 park_trim, L2 jit_unpark, mọi lệnh BÁN, state, nav_basis, approved_by (vẫn null).",
        "jit_note": (
            "L2 jit_unpark tính ở notional TRƯỚC patch giá nên buy_amendments.needed_vnd của nó "
            "không còn khớp từng lệnh. KHÔNG chạy lại và KHÔNG sửa tay (ranh giới cứng: không sửa "
            "qty/ticker script đề xuất). Đã kiểm tra thứ thật sự quan trọng — ĐỦ TIỀN Ở MỨC TỔNG: "
            f"nguồn {funding:,.0f}đ ≥ nhu cầu {buy_tot:,}đ, và toàn bộ lệnh BÁN (priority 0) chạy "
            "trước lệnh MUA (priority 1)."
        ),
    }

    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)  # atomic

    print(f"=== {account}: LAG_book {lag_book:,.0f}")
    for t, qo, qn, no, nn, sl in changes:
        print(f"   {t}: {qo:,} -> {qn:,}cp | {no:,.0f} (+{no/sl-1:.1%} slot) -> {nn:,.0f} (slot {sl:,.0f})")
    if not changes:
        print("   (không lệnh nào cần chỉnh)")
    print(f"   BUY tong {bg:,.0f} + phi {bfee:,} = {buy_tot:,} | nguon {funding:,.0f} | con lai {cash_end:,.0f}")


for acc in ["SpaceX", "ZaloPay"]:
    fix(acc)
