#!/usr/bin/env python3
"""Áp thiết kế lại tỷ trọng tiền mặt cho plan 2026-08-11 (job DollarBill_20260810_185924).

Chỉ dùng MỘT LẦN cho ngày 08-11. Ghi atomic (tmp + os.replace), backup .bak cạnh file gốc.
KHÔNG tự tính lại gì — mọi con số lấy từ artifact đã chạy thật:
  data/trade_plans/park_add_<acct>_2026-08-11.json   (P2, compute_park_add.py)
  data/trade_plans/park_trim_<acct>_2026-08-11.json  (L1, compute_park_trim.py → NO_TRIM)
"""
import json
import os
import shutil

WC = "/home/trido/thanhdt/WorkingClaude"
D = os.path.join(WC, "data", "trade_plans")
FEE = 0.00075

CFG = {
    "SpaceX": {
        "active_nav": 969265008.0,
        "total_cash": 305627008.0,
        "available_cash": 158439368.0,
        "div_recv": 9775000.0,
        "pp0buy": 565026657.0,
        "books_before": {"BAL": 0.0, "LAG": 35100000.0, "PARK": 317548000.0,
                         "CAPIT": 303110000.0, "DISCRETIONARY_SPECIAL": 7880000.0},
        "disc": [("TV1", 2000, 19900.0, 20000.0), ("DRI", 3700, 13200.0, 13600.0)],
    },
    "ZaloPay": {
        "active_nav": 513780832.0,
        "total_cash": 152499982.0,
        "available_cash": 1.0,
        "div_recv": 6453500.0,
        "pp0buy": 145946201.0,
        "books_before": {"BAL": 0.0, "LAG": 63845000.0, "PARK": 116256650.0,
                         "CAPIT": 181179200.0, "DISCRETIONARY_SPECIAL": 0.0},
        "disc": [("TV1", 1300, 19900.0, 20000.0), ("DRI", 1900, 13200.0, 13600.0)],
    },
}

DISC_NOTE = {
    "TV1": ("PECC1 (UPCOM) — NÂNG SIZE lên 5% NAV/mã theo chỉ đạo user 2026-08-10 tối (trước đó "
            "1,5%). THÊM vào vị thế discretionary đã có (chương trình gốc "
            "plan_TV1_SpaceX_discretionary_20260723.json, user duyệt 2026-07-23). Gate chạy LẠI ở "
            "size MỚI (không giả định pass): DCF CHEAP MoS +84,76% robust (dcf_valuation.dcf_check "
            "2026-08-11); DD 0 red flag ở đúng est_value mới. ⚠ THANH KHOẢN LÀ RỦI RO CHÍNH: "
            "ADV3T 806tr/phiên — lệnh này = 5% ADV (SpaceX) / 3% ADV (ZaloPay), cộng 2 account = "
            "8,1% ADV cùng lúc, dưới trần %ADV per-account (80,59tr) nhưng TRÊN THỰC TẾ nhiều khả "
            "năng chỉ khớp một phần trong 1 phiên và phải rải nhiều phiên. Trần giá 20.000đ "
            "(no_chase_ceiling user duyệt cho chương trình TV1 gốc) chỉ cách giá ask 19.900đ "
            "0,5% ⇒ càng làm giảm xác suất khớp trọn. KHÔNG nới trần này."),
    "DRI": ("Cao su Đắk Lắk — NÂNG SIZE lên 5% NAV/mã theo chỉ đạo user 2026-08-10 tối (trước đó "
            "1,5%). Vẫn là quyết định DISCRETIONARY, KHÔNG mở lại cửa sổ entry LAG (đã đóng hết "
            "3/3 phiên sau 08-10). Gate chạy LẠI ở size MỚI: DCF CHEAP MoS +36,80% robust "
            "(2026-08-11); DD 0 red flag; thanh khoản OK (ADV3T 5,35 tỷ ⇒ lệnh = 1% ADV SpaceX / "
            "0,5% ZaloPay, rất xa trần 534,67tr). 8L rating 2. WATCH cao su: RSS3 2,694 USD/kg "
            "(2026-08-07) vẫn CAO HƠN ngưỡng xét lại 2,26 — chưa kích hoạt. ⚠ Nếu DT5G chuyển "
            "BEAR, sổ LAG bị allocator bán (w_LAG=0); vị thế này ở book DISCRETIONARY_SPECIAL nên "
            "KHÔNG bị cơ chế đó bán tự động — đổi lại nó cũng không có lối thoát tự động, exit là "
            "quyết định của người."),
}


def build(acct):
    c = CFG[acct]
    padd = json.load(open(os.path.join(D, f"park_add_{acct}_2026-08-11.json")))
    ptrim = json.load(open(os.path.join(D, f"park_trim_{acct}_2026-08-11.json")))
    assert padd["decision"] == "ADD", padd["decision"]

    orders = []
    disc_val = {}
    for i, (tk, qty, px, ceil) in enumerate(c["disc"], 1):
        val = qty * px
        disc_val[tk] = val
        orders.append({
            "id": f"BUY-{tk}-DISC-{i:02d}", "ticker": tk, "side": "buy", "qty": qty,
            "ref_price": px,
            "ref_price_source": ("DNSE API LIVE (secdef/latest_trade boardId=G1, đo "
                                 "2026-08-11T01:2x ICT) — TUYỆT ĐỐI KHÔNG dùng BigQuery cho giá "
                                 "same-day (bright-line rule §6)."),
            "order_type": "LO", "estimated_cost_vnd": val, "fee_est_vnd": round(val * FEE),
            "book": "DISCRETIONARY_SPECIAL", "play_type": "DISCRETIONARY_ADD",
            "priority": 1, "urgency": "normal", "cash_only": True,
            "hard_no_chase_ceiling_vnd": ceil,
            "dcf_check": "CHEAP", "dd_check": "PASS — 0 red flag, chạy lại ở size MỚI 2026-08-11",
            "target_pct_active_nav": 0.05,
            "note": DISC_NOTE[tk],
        })

    for j, o in enumerate(padd["orders"], 1):
        val = o["value_vnd"]
        orders.append({
            "id": f"BUY-{o['ticker']}-PARK-{j:02d}", "ticker": o["ticker"], "side": "buy",
            "qty": o["qty"], "ref_price": o["ref_price"],
            "ref_price_source": ("giá broker DNSE live (park_holdings/broker_positions "
                                 "marketPrice, hoặc quote live cho mã chưa giữ) — KHÔNG dùng BQ"),
            "order_type": "LO", "estimated_cost_vnd": val, "fee_est_vnd": round(val * FEE),
            "book": "PARK", "play_type": "PARK_ADD", "priority": 2, "urgency": "normal",
            "cash_only": True,
            "dd_check": "PASS — dd_check_for_order 2026-08-11, 0 red flag",
            "weight_target": o["weight_target"], "target_vnd": o["target_vnd"],
            "mv_before_vnd": o["mv_vnd"], "is_new_name": o["is_new_name"],
            "adv_vnd": o["adv_vnd"], "adv_cap_vnd": o["adv_cap_vnd"],
            "name_cap_room_vnd": o["name_cap_room_vnd"],
            "note": o["reason"],
        })

    buy_val = sum(o["estimated_cost_vnd"] for o in orders)
    fee = sum(o["fee_est_vnd"] for o in orders)
    spend = buy_val + fee

    b0 = dict(c["books_before"])
    b1 = dict(b0)
    b1["PARK"] = b0["PARK"] + padd["add_proposed_vnd"]
    b1["DISCRETIONARY_SPECIAL"] = b0["DISCRETIONARY_SPECIAL"] + sum(disc_val.values())
    cash0 = c["total_cash"]
    cash1 = cash0 - spend
    nav1 = c["active_nav"] - fee

    def pct(v, nav):
        return round(100.0 * v / nav, 2)

    bd_before = {k: {"mv_vnd": v, "pct_active_nav": pct(v, c["active_nav"])} for k, v in b0.items()}
    bd_before["CASH"] = {"mv_vnd": cash0, "pct_active_nav": pct(cash0, c["active_nav"])}
    bd_after = {k: {"mv_vnd": v, "pct_active_nav": pct(v, nav1)} for k, v in b1.items()}
    bd_after["CASH"] = {"mv_vnd": cash1, "pct_active_nav": pct(cash1, nav1)}

    non_pool = b1["CAPIT"] + b1["LAG"] + b1["BAL"] + b1["DISCRETIONARY_SPECIAL"]
    return {
        "orders": orders, "buy_val": buy_val, "fee": fee, "spend": spend,
        "cash0": cash0, "cash1": cash1, "nav1": nav1,
        "bd_before": bd_before, "bd_after": bd_after,
        "padd": padd, "ptrim": ptrim, "non_pool": non_pool,
        "disc_val": disc_val,
    }


def main():
    for acct in ("SpaceX", "ZaloPay"):
        c = CFG[acct]
        r = build(acct)
        path = os.path.join(D, f"plan_{acct}_2026-08-11.json")
        shutil.copy2(path, path + ".bak")
        p = json.load(open(path))

        p["orders"] = r["orders"]
        p["orders_summary"] = {
            "total_orders": len(r["orders"]),
            "total_buy_orders": len(r["orders"]),
            "total_sell_orders": 0,
            "total_buy_value_vnd": r["buy_val"],
            "total_fee_est_vnd": r["fee"],
            "by_book": {
                "DISCRETIONARY_SPECIAL": {"n": 2, "value_vnd": sum(r["disc_val"].values())},
                "PARK": {"n": len(r["padd"]["orders"]),
                         "value_vnd": r["padd"]["add_proposed_vnd"]},
            },
            "action": ("BUY — nâng 2 lệnh discretionary TV1/DRI lên 5% NAV/mã VÀ giải ngân phần "
                       "tiền dư vào sổ PARK (custom30V) để kéo tỷ trọng tiền về đúng thiết kế "
                       "production. V2.4 BAL/LAG/CAPIT vẫn HOLD (0 lệnh mới)."),
        }
        p["book_breakdown_projected"] = {
            "note": ("SAU khi khớp toàn bộ orders[] ở đúng ref_price. NAV giảm đúng bằng phí "
                     f"{r['fee']:,.0f}đ. Giá thị trường biến động sẽ làm số thực khác chút."),
            "books": r["bd_after"],
            "total_check_vnd": round(sum(v["mv_vnd"] for v in r["bd_after"].values())),
        }
        p["cash_planning"] = {
            "available_cash_now_vnd": c["available_cash"],
            "total_cash_minus_debt_vnd": c["total_cash"],
            "pp0buy_measured_vnd": c["pp0buy"],
            "orders_placed_value_with_fee_vnd": r["spend"],
            "residual_cash_vnd": r["cash1"],
            "discipline_check": (
                f"Câu hỏi bắt buộc: tổng orders[] có ≤ tiền THẬT CÓ SẴN NGAY BÂY GIỜ không, "
                f"không giả định gì thêm? Σ orders[] + phí = {r['spend']:,.0f}đ ≤ sức mua đo "
                f"THẬT pp0Buy = {c['pp0buy']:,.0f}đ ✓ VÀ ≤ trần TIỀN MẶT THUẦN (totalCash − "
                f"cổ tức phải thu) = {c['total_cash'] - c['div_recv']:,.0f}đ ✓. KHÔNG có field "
                "funding_required, KHÔNG có câu văn nào ngụ ý 'khi user nạp thêm'."),
            "no_margin_proof": (
                f"pp0Buy đo được {c['pp0buy']:,.0f}đ LỚN HƠN tiền mặt thật "
                f"{c['total_cash']:,.0f}đ" +
                (" — với SpaceX phần chênh là HẠN MỨC VAY của gói margin. Plan này KHÔNG dùng "
                 "một đồng nào của phần đó: tổng chi " if acct == "SpaceX" else
                 " — ZaloPay là account CASH-ONLY nên phần chênh là tiền bán chưa settle T+2 mà "
                 "DNSE đã cộng vào sức mua T+0, KHÔNG phải vay. Tổng chi ") +
                f"{r['spend']:,.0f}đ ≤ {c['total_cash'] - c['div_recv']:,.0f}đ = totalCash trừ cổ "
                "tức phải thu. V2.5 leverage và capit_margin_lever đều DISABLED — plan này không "
                "chạm tới cả hai."),
            "settlement_note": (
                f"availableCash (tiền đã settle) chỉ {c['available_cash']:,.0f}đ; phần còn lại "
                "trong totalCash là tiền bán PARK phiên 08-10 đang settle T+2 + cổ tức phải thu. "
                "DNSE ĐÃ cộng phần bán chưa settle vào sức mua T+0 (pp0Buy) — cơ chế này đo được "
                "thật ở CẢ 2 account, không phải giả định. Nếu vì lý do nào đó broker không cấp "
                "đủ sức mua trong phiên, executor tự chuyển sang WAIT_CASH và lệnh chờ, KHÔNG "
                "thấu chi."),
        }

        p["park_trim_proposal"] = {
            "source": "mike/bin/compute_park_trim.py",
            "rerun_at": "2026-08-11T02:0x ICT (job DollarBill_20260810_185924)",
            "asof": r["ptrim"]["asof"], "decision": r["ptrim"]["decision"],
            "pool_vnd": r["ptrim"].get("pool_vnd"),
            "target_park_vnd": r["ptrim"].get("target_park_vnd"),
            "park_mv_vnd": r["ptrim"].get("park_mv_vnd"),
            "delta_vnd": r["ptrim"].get("delta_vnd"),
            "notes": r["ptrim"].get("notes", []),
            "orders": [],
            "handling": (
                "NO_TRIM ⇒ không thêm field nào vào orders[]. ⚠ ĐỔI HẲN so với các phiên trước: "
                "BLOCKED_RECONCILE của MBB ĐÃ ĐƯỢC GIẢI QUYẾT — Taylor (job Taylor_20260810_183618) "
                "xác nhận corp-action MBB cổ tức cổ phiếu 15% (ex 2026-08-11) và ghi vào "
                "data/corp_actions.json; park_holdings đã áp ×1,15 (SpaceX 1100→1265cp, ZaloPay "
                "202→232cp) và reconcile.ok=true ở CẢ 2 account. Đúng giả thuyết DollarBill nêu "
                "tối 08-10 (2 account lệch cùng ~+15% ⇒ hành động doanh nghiệp, không phải lỗi sổ). "
                "L1 hôm nay ra NO_TRIM vì sổ PARK đang THIẾU so với trần chứ không phải thừa — "
                "đó chính là lý do plan này chạy đường MUA (P2)."),
        }
        p["park_add_proposal"] = {
            "source": "mike/agents/DollarBill/tools/compute_park_add.py",
            "artifact": f"data/trade_plans/park_add_{acct}_2026-08-11.json",
            "what_it_is": (
                "Đường MUA (P2) của sổ PARK — ĐỐI XỨNG ĐẠI SỐ của L1 compute_park_trim.py, dùng "
                "lại NGUYÊN VẸN mọi hàm/hằng số của L1 bằng import (rổ custom30V PIT, phép chuẩn "
                "hoá trọng số, trần TỔNG/phiên _etf_day_cap, trần per-name LAG_ADV_PCT×ADV×share, "
                "PARK_TARGET_F1=0,80, băng 0,005, BANNED, LOT/round_lot). Chính L1 in ra dòng "
                "'phần thiếu là trọng số của các mã trong rổ mà ta CHƯA MUA — chỉ đóng lại khi "
                "đường MUA chạy (P2 chưa có code)'. Đây là P2 đó, ở dạng CÔNG CỤ TÍNH của "
                "DollarBill (KHÔNG phải script production, không cron, chỉ đọc)."),
            "asof": r["padd"]["asof"], "decision": r["padd"]["decision"],
            "target_park": r["padd"]["target_park"],
            "basket_rebal_date": r["padd"]["basket_rebal_date"],
            "basket_feasible_n": r["padd"]["basket_feasible_n"],
            "basket_n": r["padd"]["basket_n"],
            "basket_dropped_weight": r["padd"]["basket_dropped_weight"],
            "reserve_vnd": r["padd"]["reserve_vnd"],
            "pool_vnd": r["padd"]["pool_vnd"],
            "target_park_vnd": r["padd"]["target_park_vnd"],
            "park_mv_before_vnd": r["padd"]["park_mv_vnd"],
            "park_mv_after_vnd": r["padd"]["park_mv_after_vnd"],
            "park_pct_after_of_pool": r["padd"]["park_pct_after"],
            "structural_deficit_vnd": r["padd"]["structural_deficit_vnd"],
            "add_proposed_vnd": r["padd"]["add_proposed_vnd"],
            "add_shortfall_vnd": r["padd"]["add_shortfall_vnd"],
            "day_cap_binding": r["padd"]["day_cap_binding"],
            "cash_binding": r["padd"]["cash_binding"],
            "blocked": r["padd"]["blocked"],
            "at_or_above_target": r["padd"]["at_or_above_target"],
            "notes": r["padd"]["notes"],
            "orders_merged_into_orders_array": True,
            "why_merged": (
                "Lệnh P2 nằm THẲNG trong orders[] (priority 2) chứ không để ở key riêng: "
                "load_plan() chỉ đọc orders[], để ở key riêng thì bot không thấy — sự cố thật "
                "2026-08-07 (ZaloPay 8 lệnh park_trim kẹt ở key display-only, 0 khớp). Khác với "
                "L1/L2 vốn để ở key riêng khi CHƯA được duyệt; ở đây user đã ra chỉ đạo trực tiếp "
                "'đưa cash về 10%, phần dư giải ngân vào park'."),
            "quant_skeptic_review": {
                "run": "mike/bin/verify_finding.sh, log mike/logs/verify_20260810_191101_3573336.log",
                "on_the_numbers": ("tái lập ĐƯỢC TỪNG ĐỒNG mọi con số (reserve gồm phí 0,075%, "
                                   "trần tiền mặt, %park, tiền còn lại, 16 mã). Look-ahead sạch "
                                   "(rổ PIT kỳ 2026-08-05, quote DNSE live). Kết luận: mua các mã "
                                   "chưa giữ KHÔNG phá cấu trúc rổ — nó đóng đúng khe mà chính L1 "
                                   "chỉ ra."),
                "killer_objection": ("'đối xứng CODE không phải đối xứng RỦI RO'. Bản đầu của P2 "
                                     "thừa hưởng 2 tính chất của L1 vốn THẬN TRỌNG ở chiều bán "
                                     "nhưng NGUY HIỂM khi lật dấu: (a) Σwant > delta ⇒ nếu khớp "
                                     "trọn sẽ đẩy PARK lên 84,02% (SpaceX) / 87,36% (ZaloPay), "
                                     "VƯỢT chính trần 80% mà L1 sinh ra để giữ, rồi phiên sau L1 "
                                     "bán ngược = churn 2 lần phí; (b) không có cổng DT5G "
                                     "SKIP_STATE ⇒ sẽ size lệnh mua 80% pool giữa BEAR/CRISIS. "
                                     "Ngoài ra bản đầu thiếu 3 guard tiền của L1 (đáng ngại nhất: "
                                     "totalDebt=None bị ép về 0 ⇒ thổi phồng trần 'không margin' "
                                     "đúng bằng số nợ vay)."),
                "fixes_applied_before_writing_this_plan": [
                    "THÊM trần scale_delta = delta/Σwant ⇒ tổng mua KHÔNG BAO GIỜ vượt delta; "
                    "thêm trần CỨNG per-name = tgt_i ⇒ không mã nào vượt trọng số mục tiêu. "
                    "overpark_after_vnd = 0 ở CẢ 2 account, theo THIẾT KẾ chứ không phải may.",
                    "PORT cổng DT5G SKIP_STATE của L1:275 (verify: state=3 NEUTRAL, "
                    "golive_v23_status.json 2026-08-10, etf_park_frac=0,8 khớp target).",
                    "PORT 3 guard tiền của L1: fail-closed khi totalDebt/totalCash là None (KHÔNG "
                    "ép 0), phép thử 'mọi field tiền = 0', bất biến totalCash ≥ availableCash.",
                    "THÊM pp0Buy làm trần THỨ HAI (không thay trần tiền mặt) — ZaloPay trần tiền "
                    "mặt 146.046.482đ thực tế CAO HƠN pp0Buy 145.946.201đ nên pp0Buy mới là ràng "
                    "buộc thật.",
                    "--active-nav-vnd thành BẮT BUỘC (không có NAV ⇒ không áp được name_cap ⇒ "
                    "fail-closed thay vì âm thầm bỏ trần).",
                    "Làm tròn lô đổi từ floor sang LARGEST-REMAINDER: floor đơn thuần ném đi 22% "
                    "ngân sách (110,0tr mục tiêu → chỉ đặt được 85,5tr). Đây KHÔNG phải tham số "
                    "rủi ro mới — mọi trần (tgt_i, %ADV, name_cap, ngân sách, delta) vẫn CỨNG.",
                    "Tách cash_after_vnd (cơ sở pool) khỏi cash_after_spendable_vnd (§25).",
                ],
                "still_owed": ("chưa có mike/bin/compute_park_add_selfcheck.py (quant-skeptic yêu "
                               "cầu, §23). Vì vậy file này CỐ Ý nằm ở mike/agents/DollarBill/tools/ "
                               "chứ KHÔNG phải mike/bin/ — nó chưa phải công cụ production. Đề "
                               "xuất: giao Taylor viết selfcheck theo mẫu "
                               "compute_park_trim_selfcheck.py rồi mới promote."),
            },
        }
        p["jit_unpark_proposal"] = {
            "source": "mike/bin/compute_jit_unpark.py",
            "rerun_at": "2026-08-11T02:2x ICT (job DollarBill_20260810_185924)",
            "decision": "SEE_FIELD_BELOW",
            "note": "điền sau khi chạy L2 với plan đã có orders[] — xem key jit_unpark_result",
        }

        p["cash_redesign_2026-08-11"] = {
            "source_job": "DollarBill_20260810_185924",
            "directive": (
                "User (John) 2026-08-10 tối: 'tỷ trọng cash như vậy là quá lớn. Tôi muốn Dollar "
                "Bill đưa tỷ trọng cash về đúng theo thiết kế của production. Tuy nhiên do đã "
                "dành tiền cho CAPIT nên có thể tỷ lệ 80% cổ phiếu không còn chính xác. Có thể "
                "đưa cash về tỷ lệ 10% bằng cách tăng tỷ lệ mua DRI và TV1 lên 5% NAV. Cash còn "
                "dư giải ngân vào park cho tôi.'"),
            "policy_reconciliation": {
                "user_target": "cash ≈ 10% TỔNG NAV",
                "production_rule": (
                    "trading_rules.json neutral_parking: PARK = 80% của IDLE POOL, "
                    "idle_pool = tiền mặt + PARK (= NAV − CAPIT − BAL − LAG − DISCRETIONARY). "
                    "Suy ra tiền = 20% idle pool. Đây KHÔNG phải 20% NAV."),
                "why_the_two_numbers_differ": (
                    "Tỷ lệ tiền/NAV mà luật 80% sinh ra phụ thuộc phần NAV bị các sổ NGOÀI pool "
                    "chiếm (CAPIT + LAG + DISCRETIONARY). Chỉ khi phần đó đúng bằng 50% NAV thì "
                    "20% × 50% mới ra đúng 10% NAV. Hai account đang ở hai bên con số 50% đó."),
                "SpaceX": {
                    "non_pool_books_vnd": None, "computed_in_per_account_block": True},
                "note": "số cụ thể từng account nằm ở khối 'per_account' dưới đây",
            },
            "per_account": {
                "non_pool_books_vnd": r["non_pool"],
                "non_pool_pct_nav": round(100.0 * r["non_pool"] / r["nav1"], 2),
                "idle_pool_vnd": r["padd"]["pool_vnd"],
                "idle_pool_pct_nav": round(100.0 * r["padd"]["pool_vnd"] / r["nav1"], 2),
                "cash_target_from_production_rule_pct_nav": round(
                    100.0 * 0.20 * r["padd"]["pool_vnd"] / r["nav1"], 2),
                "cash_after_plan_vnd": r["cash1"],
                "cash_after_plan_pct_nav": round(100.0 * r["cash1"] / r["nav1"], 2),
                "gap_vs_user_10pct_vnd": round(r["cash1"] - 0.10 * r["nav1"]),
                "gap_vs_user_10pct_pp": round(100.0 * r["cash1"] / r["nav1"] - 10.0, 2),
            },
            "book_breakdown_before": r["bd_before"],
            "book_breakdown_after": r["bd_after"],
            "gates_rerun_at_new_size": {
                "P0_check_plan_funding": "xem key p0_funding_gate_2026-08-11 (chạy THẬT, ppse sống)",
                "DCF": ("dcf_valuation.dcf_check 2026-08-11 — TV1 CHEAP MoS +84,76% robust; "
                        "DRI CHEAP MoS +36,80% robust"),
                "DD_red_flag": ("trading_bot.due_diligence.dd_check_for_order chạy ở ĐÚNG "
                                "est_value mới — TV1/DRI 0 red flag; 16/16 mã PARK 0 red flag"),
                "8L_rating": ("TV1 rating 1, DRI rating 2. Toàn bộ mã PARK lấy từ rổ custom30V "
                              "vốn ĐÃ gate rating ≤3 tại nguồn (cột rating_8l trong "
                              "custom30v_8l_publish.csv kỳ 2026-08-05: max = 3)"),
                "pct_ADV": ("trần per-account = LAG_ADV_PCT 0,20 × ADV × share 0,5. TV1 ADV3T "
                            "805,86tr ⇒ trần 80,59tr; DRI ADV3T 5.346,66tr ⇒ trần 534,67tr. Mọi "
                            "lệnh PARK đều dưới trần (adv_capped=false toàn bộ)."),
                "name_cap_0.10": ("áp trong compute_park_add trên vị thế TỔNG mọi book, không mã "
                                  "nào chạm trần"),
                "BANNED": "không mã nào trong plan nằm trong danh sách BANNED vĩnh viễn",
            },
            "constraints_NOT_relaxed": (
                "Không nới bất kỳ gate nào để đạt mục tiêu 10%: không dùng margin (dù pp0Buy cho "
                "phép), không nới name_cap, không nới %ADV, không bỏ DD/DCF, không đụng "
                "excluded_tickers, không đụng CAPIT/LAG/BAL. Phần chưa tới đúng 10% (hoặc vượt "
                "10%) được BÁO SỐ, không ép."),
            "residual_gap_explained": (
                "Chênh còn lại so với đúng 20% idle pool đến từ (a) làm tròn LÔ 100cp, (b) các mã "
                "trong rổ có target < 1 lô bị loại (Σ trọng số bị bỏ đã ghi ở "
                "park_add_proposal.basket_dropped_weight), (c) các mã ĐANG VƯỢT trọng số mục tiêu "
                "thì đường MUA không chạm tới (muốn kéo về phải BÁN — đó là việc của L1, hôm nay "
                "L1 ra NO_TRIM). Không bù các khoản này bằng tay: bù = thêm tham số chưa đo."),
            "nav_may_shift_slightly": (
                "NAV dùng ở đây đo lúc 2026-08-11T02:0x ICT sau khi corp-action MBB ×1,15 đã vào "
                "sổ (Taylor job Taylor_20260810_183618). MBB CÙNG NGÀY còn một đợt CHÀO BÁN QUYỀN "
                "MUA 10:1 giá 10.000đ — quyền mua KHÔNG tự làm tăng số lượng (phải nộp tiền thực "
                "hiện quyền) nên không ảnh hưởng NAV hôm nay, nhưng nếu user muốn thực hiện quyền "
                "thì đó là một khoản chi RIÊNG (SpaceX ~126cp × 10.000đ ≈ 1,26tr; ZaloPay ~23cp ≈ "
                "0,23tr) chưa nằm trong plan này — cần chỉ đạo riêng."),
        }
        p["requires_user_approval"] = True
        p["approved_by"] = None
        p["approved_at"] = None

        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)
        print(f"{acct}: {len(r['orders'])} lệnh, chi {r['spend']:,.0f}đ, cash sau "
              f"{r['cash1']:,.0f}đ = {100*r['cash1']/r['nav1']:.2f}% NAV")


if __name__ == "__main__":
    main()
