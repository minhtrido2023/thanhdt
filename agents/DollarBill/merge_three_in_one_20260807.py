#!/usr/bin/env python3
"""Bước 2/2 — MERGE 3 thành phần vào orders[] THẬT của plan 2026-08-07 (SpaceX + ZaloPay).

Lý do phải merge (user John, job DollarBill_20260807_050844): lần trước plan được duyệt nhưng
L1/L2 nằm ở key riêng, bot `load_plan()` chỉ đọc `orders[]` nên KHÔNG bán PARK ⇒ không có tiền
⇒ lệnh mua không chạy được. Lần này gộp 3-trong-1 để duyệt 1 lần là chạy được ngay.

  (1) 1 lệnh MUA DRI                       — priority 1
  (2) N lệnh BÁN PARK từ L1 park_trim      — priority 0
  (3) M lệnh BÁN PARK từ L2 jit_unpark     — priority 0

Mã xuất hiện ở CẢ L1 và L2 ⇒ GỘP thành 1 order duy nhất, cộng dồn qty (chỉ thị của user).
An toàn về lô: compute_jit_unpark.py đã chạy với --l1-json nên L2 KHÔNG đề xuất lại phần lô mà
L1 đã reserve — cộng dồn là đúng, không phải bán trùng. Script vẫn tự kiểm tra lại ≤ sellable.

KHÔNG set approved_by — user duyệt sau.
"""
import json

BASE = "/home/trido/thanhdt/WorkingClaude/data/trade_plans"
DATE = "2026-08-07"


def merge_account(acct):
    plan_path = f"{BASE}/plan_{acct}_{DATE}.json"
    p = json.load(open(plan_path, encoding="utf-8"))
    l1 = p["park_trim_proposal"]
    l2 = json.load(open(f"{BASE}/jit_unpark_{acct}_{DATE}.json", encoding="utf-8"))

    assert l1["decision"] == "TRIM", f"{acct}: L1 decision={l1['decision']} — dừng"
    assert l2["decision"] == "JIT", f"{acct}: L2 decision={l2['decision']} — dừng"
    assert l2.get("reconcile_ok") is True, f"{acct}: L2 reconcile_ok không True — dừng"

    buy = [o for o in p["orders"] if o["side"] == "buy"]
    assert len(buy) == 1 and buy[0]["ticker"] == "DRI", f"{acct}: orders[] không phải 1 lệnh mua DRI"
    buy = buy[0]

    # ── gộp bán theo ticker ───────────────────────────────────────────────────────────
    agg = {}
    for src, orders in (("L1", l1["orders"]), ("L2", l2["orders"])):
        for o in orders:
            tk = o["ticker"]
            d = agg.setdefault(tk, {"ticker": tk, "ref_price": float(o["ref_price"]),
                                    "L1": 0, "L2": 0, "sellable": None})
            assert float(o["ref_price"]) == d["ref_price"], \
                f"{acct}/{tk}: ref_price L1≠L2 ({d['ref_price']} vs {o['ref_price']}) — dừng"
            d[src] += int(o["qty"])
            if o.get("sellable") is not None:
                d["sellable"] = int(o["sellable"])

    # ── kiểm tra độc lập: tổng bán ≤ sellable (chống bán trùng lô) ────────────────────
    over = [(t, d["L1"] + d["L2"], d["sellable"]) for t, d in agg.items()
            if d["sellable"] is not None and d["L1"] + d["L2"] > d["sellable"]]
    assert not over, f"{acct}: BÁN VƯỢT SELLABLE {over} — dừng, KHÔNG ghi plan"

    sells = []
    for i, tk in enumerate(sorted(agg), 1):
        d = agg[tk]
        qty = d["L1"] + d["L2"]
        val = int(round(qty * d["ref_price"]))
        srcs = [s for s in ("L1", "L2") if d[s]]
        ptype = {"L1": "PARK_TRIM", "L2": "JIT_UNPARK",
                 "L1L2": "PARK_TRIM+JIT_UNPARK"}["".join(srcs)]
        parts = " + ".join(
            f"{d[s]}cp {'L1 park_trim (tuân thủ trần PARK 80%)' if s == 'L1' else 'L2 jit_unpark (tài trợ lệnh mua DRI)'}"
            for s in srcs)
        sells.append({
            "id": f"SELL-{tk}-PARK-{i:02d}",
            "ticker": tk, "side": "sell", "qty": qty, "ref_price": d["ref_price"],
            "ref_price_source": ("giá BQ T-1 (2026-08-06) do compute_park_trim/compute_jit_unpark "
                                 "chạy GIỮA PHIÊN — xem risk_notes cảnh báo lệch giá. Executor "
                                 "định giá lại từ ref_price + urgency lúc đặt lệnh."),
            "order_type": "LO",
            "estimated_proceeds_vnd": val,
            "fee_est_vnd": int(round(val * 0.00075)),
            "book": "PARK", "play_type": ptype,
            "priority": 0, "urgency": "normal", "timing": "SELL@13:05",
            "merged_from": {"L1_park_trim_qty": d["L1"], "L2_jit_unpark_qty": d["L2"],
                            "sellable_at_calc": d["sellable"]},
            "note": f"BÁN PARK gộp: {parts}. Tổng {qty}cp × {d['ref_price']:,.0f}đ = {val:,}đ.",
            "reason": ("Gộp 2 nguồn ĐỀ XUẤT BÁN cùng mã thành 1 lệnh (chỉ thị user 2026-08-07) — "
                       "KHÔNG bán trùng lô: compute_jit_unpark.py chạy với --l1-json nên phần lô "
                       "L1 đã reserve bị trừ ra trước khi L2 đề xuất thêm."
                       if len(srcs) == 2 else
                       ("L1 park_trim — đưa tỷ trọng PARK về trần 80% pool (SELL-ONLY)."
                        if srcs == ["L1"] else
                        "L2 jit_unpark — bán đúng lượng cần để tài trợ lệnh mua DRI trong cùng plan.")),
            "stop_exempt": False, "slot_exempt": False,
        })

    buy["priority"] = 1
    ja = l2["buy_amendments"][0]
    buy["jit_status"] = ja["status"]
    buy["qty_final"] = ja["qty_final"]
    buy["jit_note"] = (
        f"L2 JIT-unpark (tính LẠI cho DRI, không phải số của SSI): {ja['status']} — bán PARK "
        f"{ja['jit_sell_vnd']:,.0f}đ (thu ròng {ja['jit_proceeds_net_vnd']:,.0f}đ sau friction "
        f"0.15%) ⇒ đủ tiền mua nguyên lệnh. qty giữ NGUYÊN {ja['qty_final']:,}cp, KHÔNG shrink, "
        f"KHÔNG drop. Cash sau khi thực hiện = {ja['cash_after_vnd']:,.0f}đ.")
    assert ja["qty_final"] == buy["qty"], f"{acct}: qty_final≠qty — dừng"

    p["orders"] = sells + [buy]

    # ── tổng kết + kiểm tra đủ tiền ──────────────────────────────────────────────────
    sell_gross = sum(o["estimated_proceeds_vnd"] for o in sells)
    sell_fee = sum(o["fee_est_vnd"] for o in sells)
    sell_net = sell_gross - sell_fee
    buy_total = buy["total_with_fee_vnd"]
    cash0 = p["nav_basis"]["available_cash_vnd"]

    p["orders_summary"] = {
        "total_orders": len(p["orders"]),
        "total_sell_orders": len(sells),
        "total_buy_orders": 1,
        "merge_note": ("✅ ĐÃ MERGE 3-TRONG-1 VÀO orders[] THẬT (chỉ thị user 2026-08-07, job "
                       "DollarBill_20260807_050844): (1) 1 lệnh MUA DRI + (2) L1 park_trim + "
                       "(3) L2 jit_unpark. Duyệt 1 lần là bot chạy được cả gói — KHÔNG còn tình "
                       "trạng plan approved nhưng bot không thấy lệnh bán nên thiếu tiền."),
        "sell_gross_vnd": sell_gross,
        "sell_fee_est_vnd": sell_fee,
        "sell_net_proceeds_vnd": sell_net,
        "buy_gross_vnd": buy["estimated_cost_vnd"],
        "buy_fee_est_vnd": buy["fee_est_vnd"],
        "buy_total_with_fee_vnd": buy_total,
        "net_cash_change_vnd": sell_net - buy_total,
        "available_cash_before_vnd": cash0,
        "cash_after_all_orders_vnd": cash0 + sell_net - buy_total,
        "funding_check_sell_ge_buy": sell_net >= buy_total,
        "orders_within_cash": (cash0 + sell_net) >= buy_total,
        "execution_order_note": ("priority 0 (BÁN) chạy TRƯỚC priority 1 (MUA) — executor sắp xếp "
                                 "`sorted(orders, key=priority)` tăng dần (executor.py:996). Tiền "
                                 "bán về mới đủ mua."),
        "sell_split_note": (f"Trong {len(sells)} lệnh bán: L1 park_trim "
                            f"{sum(o['merged_from']['L1_park_trim_qty'] for o in sells):,}cp / "
                            f"{l1['trim_proposed_vnd']:,.0f}đ; L2 jit_unpark "
                            f"{sum(o['merged_from']['L2_jit_unpark_qty'] for o in sells):,}cp / "
                            f"{l2['jit_sell_total_vnd']:,.0f}đ. "
                            f"{sum(1 for o in sells if o['merged_from']['L1_park_trim_qty'] and o['merged_from']['L2_jit_unpark_qty'])}"
                            f" mã có mặt ở CẢ 2 nguồn ⇒ đã gộp thành 1 lệnh/mã."),
    }

    p["cash_planning"] = {
        "available_cash_vnd": cash0,
        "discipline_check": (
            f"Câu hỏi bắt buộc: tổng orders[] MUA có ≤ sức mua thực KHÔNG giả định gì thêm? "
            f"MUA = {buy_total:,}đ. Nguồn tiền = cash {cash0:,.0f}đ + tiền BÁN PARK ròng "
            f"{sell_net:,}đ (lệnh bán nằm NGAY TRONG orders[] này, priority 0, chạy trước) = "
            f"{cash0 + sell_net:,.0f}đ ≥ {buy_total:,}đ ✅. KHÔNG có field funding_required, "
            f"KHÔNG có giả định user nạp thêm tiền — 100% nguồn là bán tài sản ĐANG CÓ."),
        "funding_source": ("Bán PARK trong cùng plan (L1 tuân thủ trần + L2 tài trợ), đã merge vào "
                           "orders[] priority 0."),
        "cash_end_after_all_vnd": cash0 + sell_net - buy_total,
    }

    p["approval_required"] = {
        "requires_user_approval": True,
        "why": [
            "Mọi plan V2.4 đều cần user duyệt trước khi Mafee thực thi LIVE (human-in-the-loop).",
            f"GÓI 3-TRONG-1: duyệt plan này = duyệt CẢ {len(sells)} lệnh BÁN PARK "
            f"({sell_gross:,}đ) LẪN lệnh MUA DRI ({buy_total:,}đ). Không còn duyệt tách 3 lần.",
            "⚠️ Lệnh MUA DRI là DISCRETIONARY OVERRIDE của user (DRI đã qua cửa sổ entry T+1 "
            "chuẩn — CSV ghi WINDOW_PASSED 2026-08-06), KHÔNG phải tín hiệu tự động.",
            "⚠️ ref_price của các lệnh BÁN là giá BQ T-1 (script L1/L2 chạy giữa phiên) — "
            "xem risk_notes.",
        ],
        "approved_by": None,
    }
    p["approved_by"] = None
    p["approved_at"] = None

    p["risk_notes"] = [
        ("📦 GÓI 3-TRONG-1 CHỜ DUYỆT 1 LẦN (chỉ thị user John 2026-08-07, job "
         "DollarBill_20260807_050844). orders[] đã MERGE THẬT cả 3 thành phần: "
         f"{len(sells)} lệnh BÁN PARK (priority 0) + 1 lệnh MUA DRI (priority 1). "
         "LÝ DO PHẢI MERGE: lần trước plan được approve nhưng L1/L2 để ở key riêng, "
         "`load_plan()` chỉ đọc `orders[]` nên bot KHÔNG bán PARK ⇒ không có tiền ⇒ lệnh mua "
         "không chạy được. Lần này duyệt 1 lần là chạy được cả gói."),
        ("🔁 THAY LỆNH: plan bản trước đề xuất MUA SSI (tín hiệu T+1 tự động). User đã chỉ đạo "
         "THAY bằng MUA DRI. DRI là DISCRETIONARY OVERRIDE — golive_v23_recommendations_"
         "2026-08-06.csv ghi DRI status = 'WINDOW_PASSED 2026-08-06', DRI KHÔNG nằm trong 6 mã "
         "due_today của filter_lag_entry_window.py. Ghi rõ để kiểm toán về sau không nhầm đây là "
         "tín hiệu máy."),
        ("💰 GIÁ DRI DÙNG LÀ GIÁ LIVE, KHÔNG COPY SỐ CŨ: DNSE latest_trade G1 lúc ~12:15 ICT "
         "2026-08-07 → matchPrice 13,100đ (ref 12,900đ, bid1 13,000 / offer1 13,100). Con số "
         "12,900đ trong chỉ đạo là giá THAM CHIẾU; giá khớp thật đã cao hơn 1.55% nên ref_price "
         "dùng 13,100đ. Qty giữ NGUYÊN theo chỉ định của user (SpaceX 3,500cp / ZaloPay 1,800cp)."),
        ("✅ DD DRI ĐÃ CHẠY LẠI, KHÔNG CHÉP MÙ: 8L rating = 2 (truy vấn point-in-time "
         "tav2_bq.fa_ratings_8l, time 2026-07-30 ≤ asof 2026-08-06, đúng SQL của "
         "lag_filter_low_rating) ⇒ PASS gate cứng ≤3. DCF CHEAP, giá trị hợp lý ~20,885đ vs giá "
         "13,000đ, MoS +37.8%, robust. FA: ROE5Y 15.8% · ROE_Min3Y 13.5% (golden floor OK) · "
         "FSCORE 6 · D/E 0.28 · PE 4.21. Thanh khoản ADV3T 5.46 tỷ/phiên, không cờ đỏ DD."),
        ("🟡 WATCH cao su — CHƯA kích hoạt: DRI thuộc nhóm GVR/PHR/DPR/DRI/TRC/HRC. Ngưỡng xét "
         "lại luận điểm PEAD = RSS3 thủng 2.26 USD/kg. Đã đọc TAY data/rubber_monthly.csv "
         "(2026-07 = 2.78) và data/rubber_weekly.csv (2026-08-05 = 2.654) — cả hai TRÊN ngưỡng "
         "(+17.4%) ⇒ không phải xét lại. KHÔNG dùng nhãn 'phá đáy 52 tuần' của rubber_weekly.py "
         "(đã xác nhận là bug đo lường 2026-08-06)."),
        ("⚠️ Nếu regime DT5G chuyển BEAR, vị thế DRI sẽ bị BÁN theo allocator (w_LAG=0 khi BEAR) "
         "— cơ chế sẵn có, công khai để user biết trước khi duyệt."),
        ("⚠️ GIÁ THAM CHIẾU CỦA CÁC LỆNH BÁN LÀ GIÁ BQ T-1, KHÔNG PHẢI GIÁ LIVE. "
         "compute_park_trim.py / compute_jit_unpark.py lấy giá qua DNSE close_price(), endpoint "
         "này trả closePrice=0 khi phiên CHƯA ĐÓNG nên rơi về giá BQ 2026-08-06. Hệ quả của việc "
         "chạy script GIỮA PHIÊN (khung chuẩn ~19:00 sau đóng cửa), KHÔNG phải bug logic. Đo lệch "
         "thật lúc 11:5x ICT: VNM +5.93%, VHM -3.76%, BID +3.03%, CTG +2.39%, VCB +2.20%, "
         "VPB -1.59%; tổng cổ phiếu lệch +1.13%. Quyết định TRIM/JIT KHÔNG đổi, nhưng qty từng mã "
         "có thể lệch vài %. KHÔNG tự sửa qty của script (ranh giới cứng L1/L2)."),
        ("🔒 KHÔNG BÁN TRÙNG LÔ: compute_jit_unpark.py đã chạy với --l1-json trỏ đúng file L1 cùng "
         "phiên, nên phần lô L1 đã reserve bị TRỪ RA trước khi L2 đề xuất thêm (bằng chứng: L2 log "
         "'đã trừ L1', và SpaceX/SHS bị L2 bỏ qua vì hết dư địa sau L1). Mã có mặt ở cả 2 nguồn đã "
         "được GỘP thành 1 lệnh duy nhất, qty cộng dồn — script merge tự kiểm tra lại tổng qty ≤ "
         "sellable của từng mã trước khi ghi (assert, không ghi nếu vượt)."),
        ("📉 P1 là SELL-ONLY: sau khi bán, PARK sẽ nằm DƯỚI target 80% cho tới khi đường MUA chạy. "
         "Đường MUA (P2) CHƯA có code — hiện là hàng PARK_ADVISORY do NGƯỜI quyết định. Đúng thiết "
         "kế, không phải lỗi."),
        ("⚠️ Engine mua vẫn publish etf_park_frac=0.70 trong khi chính sách target = 0.80 "
         "(neutral_parking.pending_engine_consistency) — hệ đang ở trạng thái LAI: MUA tới 70%, "
         "chỉ TRIM khi vượt 80%. Dòng 'CỔNG CHƯA MỞ' mà compute_park_trim.py tự in nói về việc "
         "đường MUA của engine chưa đồng bộ, KHÔNG phải cổng chính sách (cổng chính sách đã mở "
         "2026-08-04)."),
        ("L1 lần này dùng CÔNG THỨC MỚI (§D1 park_membership_sync_L0_design_20260806.md, user John "
         "duyệt sáng 2026-08-07, job Taylor_20260807_020402): bán theo trọng số MỤC TIÊU của rổ "
         "custom30V (tgt_i − mv_i) thay vì pro-rata theo trọng số ĐANG CÓ. Hệ quả: mã đã rớt rổ bị "
         "bán SẠCH, và tổng bán LỚN HƠN mức vượt trần vì gồm cả phần trọng số của các mã trong rổ "
         "mà ta chưa mua."),
        ("⏰ Cửa sổ thực thi còn lại: phiên chiều 13:00–14:45 ngày 2026-08-07 (plan hoàn tất trong "
         "giờ nghỉ trưa). Cần user duyệt TRƯỚC 13:00 để kịp."),
    ]

    l1["_merged_into_orders"] = ("✅ ĐÃ MERGE vào orders[] của plan này (priority 0). Giữ key này "
                                 "làm NGUỒN KIỂM TOÁN — KHÔNG thực thi riêng, sẽ bán 2 lần.")
    l2_copy = dict(l2)
    l2_copy["_merged_into_orders"] = ("✅ ĐÃ MERGE vào orders[] của plan này (priority 0). Giữ key "
                                      "này làm NGUỒN KIỂM TOÁN — KHÔNG thực thi riêng.")
    l2_copy["_recomputed_for"] = ("Tính LẠI cho lệnh mua DRI (45.85tr SpaceX / 23.58tr ZaloPay), "
                                  "KHÔNG phải số cũ của SSI (75.80tr / 39.12tr).")
    p["jit_unpark_proposal"] = l2_copy

    p["regeneration_note"] = (
        "Bản 2026-08-07 ~12:2x ICT — THAY lệnh MUA SSI bằng MUA DRI (discretionary override của "
        "user John qua Mike) VÀ MERGE 3-trong-1 vào orders[] thật (L1 park_trim + L2 jit_unpark + "
        "lệnh mua). Job DollarBill_20260807_050844. L2 đã tính lại cho giá trị lệnh DRI. "
        "approved_by để None — chờ user duyệt.")

    json.dump(p, open(plan_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return p, sells, buy


def main():
    for acct in ("SpaceX", "ZaloPay"):
        p, sells, buy = merge_account(acct)
        s = p["orders_summary"]
        print(f"\n{'='*70}\n{acct} — {len(p['orders'])} lệnh trong orders[]")
        print(f"{'-'*70}")
        for o in p["orders"]:
            if o["side"] == "sell":
                m = o["merged_from"]
                tag = f"L1={m['L1_park_trim_qty']:>4} L2={m['L2_jit_unpark_qty']:>4}"
                print(f"  p{o['priority']} BÁN  {o['ticker']:<4} {o['qty']:>5,}cp @ "
                      f"{o['ref_price']:>9,.0f} = {o['estimated_proceeds_vnd']:>12,}đ  [{tag}]")
        print(f"  p{buy['priority']} MUA  {buy['ticker']:<4} {buy['qty']:>5,}cp @ "
              f"{buy['ref_price']:>9,.0f} = {buy['estimated_cost_vnd']:>12,}đ  [LAG_HI]")
        print(f"{'-'*70}")
        print(f"  Σ BÁN gộp        : {s['sell_gross_vnd']:>15,}đ  ({s['total_sell_orders']} lệnh)")
        print(f"  Σ BÁN ròng (−phí): {s['sell_net_proceeds_vnd']:>15,}đ")
        print(f"  Σ MUA (+phí)     : {s['buy_total_with_fee_vnd']:>15,}đ  (1 lệnh)")
        print(f"  Chênh lệch ròng  : {s['net_cash_change_vnd']:>+15,}đ")
        print(f"  Cash trước → sau : {s['available_cash_before_vnd']:>15,.0f}đ → "
              f"{s['cash_after_all_orders_vnd']:,.0f}đ")
        print(f"  ✅ Σbán ròng ≥ Σmua: {s['funding_check_sell_ge_buy']}   "
              f"| đủ tiền: {s['orders_within_cash']}  | approved_by={p['approved_by']}")


if __name__ == "__main__":
    main()
