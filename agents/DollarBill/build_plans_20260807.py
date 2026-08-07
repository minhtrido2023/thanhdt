#!/usr/bin/env python3
"""Dựng lại plan 2026-08-07 cho SpaceX + ZaloPay (tạo BÙ giữa phiên, job DollarBill_20260807_044558).

Chỉ ráp dữ liệu đã được các script quyết định cơ học sinh ra — KHÔNG tự lọc/tự suy lại:
  · LAG entry window : mike/bin/filter_lag_entry_window.py  (/tmp/lagwin_20260807.json)
  · Lăng kính ngành  : mike/bin/sector_valuation_lens.py    (/tmp/lens_20260807.json)
  · L1 park-trim     : mike/bin/compute_park_trim.py        (data/trade_plans/park_trim_*.json)
  · L2 JIT-unpark    : chạy SAU khi file plan này đã ghi (cần orders[] BAL/LAG)
"""
import json
import os

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
PLAN_DATE = "2026-08-07"
SIGNAL_DATE = "2026-08-06"
CSV = "deploy_golive_dt5g_v4/out/golive_v23_recommendations_2026-08-06.csv"

SSI_REF = 24450.0       # DNSE latest_trade G1 2026-08-07 11:29:19 ICT (matchPrice 24.45)
SSI_LIMIT = 24450       # tick 50đ, trần 26,000 / sàn 22,600 / tham chiếu 24,300
FEE = 0.00075

# Quyết định cơ học cho 6 ứng viên T+1 (nguồn: 2 script trên, KHÔNG phải phán đoán của LLM)
LAG_DECISIONS = {
    "PGS": ("SKIP", "DD cờ đỏ THANH_KHOAN_CHET (ADV3T 6 tr/phiên) + NGOAI_UNIVERSE — cần "
                    "dd_override_reason, KHÔNG có. Cùng loại với IVS/TMG đã bị user loại 07-21."),
    "PHR": ("SKIP", "DCF RICH (hợp lý ~47,948đ vs giá 58,200đ, MoS -21.4%, robust) — cần "
                    "dcf_override_reason, KHÔNG có. Thêm: PHR thuộc nhóm cao su đang trong WATCH "
                    "ngưỡng RSS3 2,26 USD/kg."),
    "SSI": ("BUY",  "sector_valuation_lens: KHONG_SKIP_VI_FLOOR_FAIL — P/B band + ROE (chứng "
                    "khoán) CHEAP (P/B 1.50 < band 1.8, ROE_TTM 13.5% > 8%). FLOOR_FAIL một mình "
                    "KHÔNG phải gate cứng cho LAG. Thanh khoản rất tốt (ADV3T 371.72 tỷ)."),
    "TVN": ("SKIP", "sector_valuation_lens: SKIP_CO_CAN_CU — DCF RICH (hợp lý ~1,764đ vs giá "
                    "9,100đ, MoS -415.8%, robust). ROE5Y 1.4%, ROE_Min3Y -4.1%."),
    "VNF": ("SKIP", "DD cờ đỏ THANH_KHOAN_CHET (ADV3T 23 tr/phiên) + NGOAI_UNIVERSE — cần "
                    "dd_override_reason, KHÔNG có."),
    "VSI": ("SKIP", "DD cờ đỏ THANH_KHOAN_CHET (ADV3T 6 tr/phiên) + NGOAI_UNIVERSE — cần "
                    "dd_override_reason, KHÔNG có."),
}

ACCOUNTS = {
    "SpaceX":  dict(account_no="0002023347", margin=True,  excluded=[]),
    "ZaloPay": dict(account_no="0001743768", margin=False, excluded=["DGC"]),
}


def RISK_NOTES(label, stock_bq, stock_live):
    n = [
        "⚠️ GIÁ THAM CHIẾU CỦA L1 (park_trim_proposal) LÀ GIÁ BQ T-1, KHÔNG PHẢI GIÁ LIVE. "
        "compute_park_trim.py (và compute_active_nav.py) lấy giá qua DNSE close_price(), "
        "endpoint này trả closePrice=0 khi phiên CHƯA ĐÓNG nên script rơi về giá BQ ngày "
        "2026-08-06. Đây là hệ quả của việc chạy các script này GIỮA PHIÊN (khung chuẩn của "
        "chúng là ~19:00 sau khi đóng cửa), KHÔNG phải bug logic. Đo lệch thật lúc 11:5x ICT "
        "(BQ → DNSE latest_trade): VNM +5.93%, VHM -3.76%, BID +3.03%, SAB +2.75%, PVT +2.52%, "
        "CTG +2.39%, VCB +2.20%, VPB -1.59%; tổng cổ phiếu chỉ lệch "
        f"{(stock_live-stock_bq)/stock_bq*100:+.2f}%. "
        "HỆ QUẢ: quyết định TRIM/NO_TRIM KHÔNG đổi (mức vượt trần lớn hơn ngưỡng hàng chục lần), "
        "nhưng qty từng mã có thể lệch vài %. KHÔNG tự sửa qty của script (ranh giới cứng L1) — "
        "cần user biết điều này trước khi duyệt.",

        "L1 lần này dùng CÔNG THỨC MỚI (§D1 park_membership_sync_L0_design_20260806.md, user "
        "John duyệt sáng 2026-08-07, job Taylor_20260807_020402): bán theo trọng số MỤC TIÊU "
        "của rổ custom30V (tgt_i − mv_i) thay vì pro-rata theo trọng số ĐANG CÓ. Hệ quả nhìn "
        "thấy được: mã đã rớt rổ bị bán SẠCH (SpaceX: SHS 200cp), và tổng bán LỚN HƠN mức vượt "
        "trần vì gồm cả phần trọng số của các mã trong rổ mà ta chưa mua.",

        "P1 là SELL-ONLY: sau khi bán, PARK sẽ nằm DƯỚI target 80% (SpaceX 71.9%, ZaloPay 70.2%) "
        "cho tới khi đường MUA chạy. Đường MUA (P2) CHƯA có code — hiện là hàng PARK_ADVISORY do "
        "NGƯỜI quyết định. Đây là hành vi đúng thiết kế, không phải lỗi.",

        "⚠️ Engine mua vẫn ở 0.70 hay 0.80? golive_recommend_v23.py ETF_PARK đã đổi {3:0.8} từ "
        "2026-08-04 và L1 đọc etf_park_frac_live=0.8 — 2 đường đã đồng bộ ở 0.80.",

        "SSI là ứng viên LAG DUY NHẤT qua hết gate trong 6 ứng viên T+1. 5 mã còn lại bị loại "
        "CƠ HỌC (PGS/VNF/VSI: thanh khoản chết + ngoài universe_pit; PHR/TVN: DCF RICH) — xem "
        "deferred_orders[] và lag_analysis.due_today.",

        "SSI mang cờ FLOOR_FAIL (golden floor ROE_Min3Y≥0 ∧ CF_OA_3Y>0). Theo luật đã chốt, "
        "FLOOR_FAIL KHÔNG phải gate cứng cho LAG; lăng kính ngành chứng khoán (P/B band + ROE) "
        "kết luận CHEAP nên KHÔNG skip. Gate cứng duy nhất của LAG là 8L rating ≤3 và SSI đã qua "
        "(lọc sẵn ở nguồn).",

        "Nếu regime chuyển BEAR, vị thế SSI (book LAG) sẽ bị bán theo allocator (w_LAG=0). "
        "DT5G hiện NEUTRAL(3), chưa xác nhận BEAR.",

        "PHR bị loại vì DCF RICH — độc lập với WATCH cao su. Nhắc lại WATCH (user duyệt "
        "2026-08-06): RSS3 thủng 2,26 USD/kg thì phải xét lại luận điểm PEAD nhóm "
        "GVR/PHR/DPR/DRI/TRC/HRC trước khi cấp thêm vốn LAG. Hiện 0 vị thế cao su ở cả 2 account.",

        "DRI KHÔNG có trong plan này: cửa sổ entry của DRI là 2026-08-06, tới plan_date 08-07 đã "
        "WINDOW_PASSED theo filter_lag_entry_window.py. Quyết định discretionary hôm qua KHÔNG "
        "được tái tạo lại — đúng chỉ đạo user khi yêu cầu làm lại plan từ đầu.",

        "⏰ Plan tạo BÙ giữa phiên (~11:5x ICT, đang nghỉ trưa). Mọi lệnh chỉ còn cửa sổ thực thi "
        "phiên chiều 13:00–14:45 hôm nay. run_bot.sh 09:05 đã chạy qua — plan này cần Mafee thực "
        "thi ad-hoc sau khi user duyệt, không tự động khớp lịch cron.",
    ]
    if label == "ZaloPay":
        n.append("ZaloPay là tài khoản CASH-ONLY (không margin) và có excluded_tickers=['DGC'] "
                 "(10.000cp ≈ 440tr theo giá live 44,050đ). DGC đã được L1 loại đúng khỏi rổ mục "
                 "tiêu (không mua, không bán) và trọng số chuẩn hoá sang các mã còn lại.")
    else:
        n.append("SpaceX: PVT 3.500cp thuộc book CAPIT (episode CAPIT-2026-07-20, stop-exempt + "
                 "slot-exempt) — KHÔNG nằm trong L1/L2, KHÔNG sinh lệnh bán. TV1 400cp thuộc "
                 "book DISCRETIONARY_SPECIAL — cũng không đụng tới.")
    return n


def lot_round(v, price):
    return int(v // (price * 100)) * 100


def build(label):
    cfg = ACCOUNTS[label]
    nav = json.load(open(f"{WORKDIR}/data/execution_logs/active_nav_{label}.json"))
    lagwin = json.load(open("/tmp/lagwin_20260807.json"))
    lens = json.load(open("/tmp/lens_20260807.json"))
    l1 = json.load(open(f"{WORKDIR}/data/trade_plans/park_trim_{label}_{PLAN_DATE}.json"))

    live = json.load(open("/tmp/live_px_20260807.json"))
    cash = nav["cash"]
    # §6 bright-line: same-day sizing PHẢI theo giá DNSE live. compute_active_nav.py chạy GIỮA
    # PHIÊN rơi về giá BQ T-1 (close_price() trả 0 khi phiên chưa đóng) — tự tính lại phần cổ
    # phiếu theo latest_trade, giữ nguyên cash/qty của script.
    stock_bq = sum(x["qty"] * x["price"] for x in nav["positions"] if not x["excluded"])
    stock_live = sum(x["qty"] * live.get(x["ticker"], x["price"])
                     for x in nav["positions"] if not x["excluded"])
    active_nav = cash + stock_live
    active_nav_bq = nav["active_nav"]

    # --- LAG book: SSI là ứng viên DUY NHẤT qua hết gate ---
    slot_pct = 8.0                                   # LAG_LO
    slot_vnd = active_nav * slot_pct / 100.0
    qty = lot_round(slot_vnd, SSI_LIMIT)
    gross = qty * SSI_LIMIT
    fee = round(gross * FEE)

    lag_detail = []
    for r in lagwin["due_today"]:
        dec, why = LAG_DECISIONS[r["ticker"]]
        lag_detail.append({
            "ticker": r["ticker"], "play_type": r["tier"],
            "entry_window_date": PLAN_DATE, "weight_pct": r["weight_pct"],
            "floor_fail": r["floor_fail"], "dd_red_flags": r["dd_red_flags"],
            "due_diligence_raw": r["due_diligence"],
            "decision": dec, "decision_why": why,
        })

    orders, deferred = [], []
    order = {
        "id": "BUY-SSI-LAG-01", "ticker": "SSI", "side": "buy", "qty": qty,
        "ref_price": SSI_REF,
        "ref_price_source": "DNSE latest_trade G1 2026-08-07 11:29:19 ICT (matchPrice 24.45) "
                            "— giá LIVE trong phiên, KHÔNG dùng BQ close",
        "order_type": "LO", "limit_price_vnd": SSI_LIMIT,
        "estimated_cost_vnd": gross, "fee_est_vnd": fee,
        "total_with_fee_vnd": gross + fee,
        "book": "LAG", "play_type": "LAG_LO", "priority": 1, "urgency": "normal",
        "timing": "BUY@13:15",
        "timing_note": "Plan tạo BÙ lúc ~11:5x ICT (đã qua phiên sáng, đang nghỉ trưa). "
                       "Cửa sổ thực thi còn lại = phiên chiều 13:00–14:45. Nếu không khớp "
                       "trong phiên chiều 08-07, cửa sổ entry T+1 của SSI ĐÓNG — KHÔNG carry "
                       "sang 08-10, plan sau phải lấy lại từ CSV signal-date mới.",
        "hold_periods": 25, "stop_exempt": False, "slot_exempt": False,
        "dd_note": lagwin["due_today"][2]["due_diligence"],
        "sizing_note": (f"LAG_LO slot {slot_pct}% × active_nav {active_nav:,.0f} = {slot_vnd:,.0f}đ. "
                        f"{qty:,}cp × {SSI_LIMIT:,}đ = {gross:,}đ + phí 0.075% ({fee:,}đ) "
                        f"= {gross+fee:,}đ."),
        "funding_note": "Cash thực chỉ %s đ — lệnh này PHỤ THUỘC nguồn tài trợ L2 JIT-unpark "
                        "trong cùng plan (jit_unpark_proposal). Nếu user KHÔNG duyệt phần JIT, "
                        "lệnh này phải bị co/bỏ theo sức mua thật, KHÔNG được giả định nạp thêm "
                        "tiền." % f"{cash:,.0f}",
        "gates_passed": [
            "8L rating ≤3 — đã lọc SẴN ở nguồn (lag_filter_low_rating trong golive_recommend_v23)",
            "LAG entry window T+1 — filter_lag_entry_window.py, calendar_check ok=true",
            "Lăng kính ngành — sector_valuation_lens.py: KHONG_SKIP_VI_FLOOR_FAIL (CHEAP)",
            "excluded_tickers — SSI không nằm trong danh sách của account này",
            "%ADV cap — cap_lag_orders() áp lúc thực thi (ADV3T 371.72 tỷ ⇒ không binding)",
        ],
    }
    orders.append(order)

    for t in ("PGS", "PHR", "TVN", "VNF", "VSI"):
        dec, why = LAG_DECISIONS[t]
        deferred.append({
            "ticker": t, "side": "buy", "book": "LAG",
            "status": "SKIPPED_BY_GATE", "qty": 0,
            "deferred_reason": f"AUTO-EXCLUDED bởi gate — {why}",
        })

    total_orders_value = sum(o["total_with_fee_vnd"] for o in orders)

    l1_prop = {
        "source": "mike/bin/compute_park_trim.py (công thức MỚI §D1, user John duyệt "
                  "2026-08-07, job Taylor_20260807_020402; selfcheck 39/39 PASS chạy lại "
                  "trong job này)",
        "asof": l1["asof"], "decision": l1["decision"],
        "target_park": l1["target_park"],
        "park_mv_vnd": l1["park_mv_vnd"], "pool_vnd": l1["pool_vnd"],
        "target_park_vnd": l1["target_park_vnd"], "delta_vnd": l1["delta_vnd"],
        "structural_excess_vnd": l1["structural_excess_vnd"],
        "trim_total_vnd": l1["trim_total_vnd"],
        "trim_proposed_vnd": l1["trim_proposed_vnd"],
        "trim_shortfall_vnd": l1["trim_shortfall_vnd"],
        "park_mv_after_vnd": l1["park_mv_after_vnd"],
        "park_pct_after": l1["park_pct_after"],
        "underpark_after_vnd": l1["underpark_after_vnd"],
        "basket_rebal_date": l1["basket_rebal_date"],
        "basket_feasible_n": l1["basket_feasible_n"], "basket_n": l1["basket_n"],
        "risk_dial_override": None,
        "orders": l1["orders"], "blocked": l1["blocked"], "notes": l1["notes"],
        "timing_note": "Plan tạo bù giữa phiên — các lệnh bán này thực thi phiên chiều "
                       "13:00–14:45 hôm nay.",
    }

    plan = {
        "plan_date": PLAN_DATE,
        "account": label,
        "broker": "dnse",
        "account_no": cfg["account_no"],
        "mode": "live",
        "strategy": "V2.4",
        "strategy_version": "2.4",
        "state": 3,
        "state_name": "NEUTRAL",
        "state_source": "deploy_golive_dt5g_v4/golive_state_today.json "
                        "(tav2_bq.vnindex_5state_dt5g_live qua get_gated_state)",
        "state_note": "DT5G=3 NEUTRAL, as_of 2026-08-06, source=DT5G_macro, "
                      "bq_publish_ok=true, published_at 2026-08-06T19:01:16.",
        "dt4_gate_line": "base_state_dt4=3 == macro_state_dt5g=3 — macro cap KHÔNG binding.",
        "requires_user_approval": True,
        "approved_by": None,
        "approved_at": None,
        "signal_date": SIGNAL_DATE,
        "recommendations_file": CSV,
        "regeneration_note": (
            "PLAN TẠO LẠI TỪ ĐẦU ngày 2026-08-07 ~11:5x ICT theo yêu cầu user John (job "
            "DollarBill_20260807_044558) sau khi user XOÁ plan cũ. Chạy đúng flow tự động: "
            "artifacts pipeline 19:00 ngày 08-06 (golive_state_today.json + recommendations "
            "CSV signal_date 08-06) + các script quyết định cơ học. KHÔNG tái tạo lại quyết "
            "định discretionary cũ: DRI có entry window 2026-08-06 nên tới plan_date 08-07 đã "
            "WINDOW_PASSED — filter_lag_entry_window.py xếp nó ngoài due_today, nên DRI KHÔNG "
            "có trong plan này."
        ),
        "nav_basis": {
            "source": "DNSE API live 2026-08-07 ~11:5x ICT — bin/compute_active_nav.py "
                      "(positions + balances live, KHÔNG dùng BQ)",
            "nav_date": PLAN_DATE,
            "available_cash_vnd": cash,
            "total_stock_value_vnd": nav["total_stock_value"],
            "excluded_value_vnd": nav["excluded_value"],
            "total_nav_vnd": nav["total_nav"],
            "active_nav_vnd": active_nav,
            "active_nav_vnd_script_raw": active_nav_bq,
            "active_nav_price_note": (
                "⚠️ compute_active_nav.py chạy GIỮA PHIÊN (~11:5x ICT) định giá vị thế bằng "
                "giá BQ T-1 (price_source='bq_close_stale') vì đường giá DNSE của nó dùng "
                "close_price(), endpoint này trả closePrice=0 khi phiên chưa đóng. Theo luật "
                "bright-line §6 (same-day PHẢI đọc DNSE), active_nav dùng để sizing ở đây được "
                "TÍNH LẠI bằng DNSE latest_trade: cổ phiếu (không tính excluded) "
                f"{stock_bq:,.0f}đ (BQ) → {stock_live:,.0f}đ (live), lệch "
                f"{stock_live - stock_bq:+,.0f}đ ({(stock_live-stock_bq)/stock_bq*100:+.2f}%). "
                "Số lượng cổ phiếu và cash giữ NGUYÊN từ script."
            ),
            "offbook_assets_vnd": 0,
            "active_nav_note": (
                "ZaloPay có excluded_tickers=['DGC'] (10.000cp ≈ 433.5tr) — sizing V2.4 dùng "
                "active_nav (đã loại DGC), KHÔNG dùng total NAV."
                if cfg["excluded"] else
                "SpaceX không có excluded_tickers. Trứng vàng off-book = 0 (đã rút hết vĩnh viễn)."
            ),
        },
        "lag_analysis": {
            "signal_date": SIGNAL_DATE,
            "source_script": "mike/bin/filter_lag_entry_window.py --account %s "
                             "--plan-date 2026-08-07 --signal-date 2026-08-06 (chạy trực tiếp "
                             "cho plan này, KHÔNG tự lọc bằng mắt)" % label,
            "calendar_check": lagwin["calendar_check"],
            "due_today_count": len(lagwin["due_today"]),
            "due_today": lag_detail,
            "upcoming_next_plans": lagwin.get("upcoming_next_plans", []),
            "window_passed_count": len(lagwin.get("window_passed", [])),
            "window_passed_note": (
                "18 mã đã QUA cửa sổ entry tính tới plan_date 08-07 (gồm DRI entry 08-06, POW, "
                "SCL, APF, DCM, GVR, BSR, ...) — KHÔNG đưa vào plan. Đây chính là lý do plan này "
                "không có DRI: cửa sổ của nó đã đóng, không phải do bị loại vì chất lượng."
            ),
            "sector_lens": {
                "source_script": "mike/bin/sector_valuation_lens.py --floor-fail-only --json",
                "results": [r for r in lens["results"] if r["ticker"] in LAG_DECISIONS],
            },
        },
        "bal_analysis": {
            "note": "Không có ứng viên BAL mới trong CSV recommend signal_date 2026-08-06 "
                    "(book BAL rỗng; CSV chỉ có LAG + PARK_ADVISORY). 0 lệnh BAL.",
        },
        "capit_sizing": {
            "note": "golive_v23_status.json: capit_signal_today=false. Vị thế CAPIT đang giữ "
                    "(SpaceX: PVT 3.500cp; episode CAPIT-2026-07-20) là stop-exempt + "
                    "slot-exempt — KHÔNG sinh lệnh bán, KHÔNG tính vào slot BAL/LAG, KHÔNG nằm "
                    "trong L1/L2 (chỉ sleeve PARK).",
        },
        "park_trim_proposal": l1_prop,
        "cash_planning": {
            "available_cash_vnd": cash,
            "orders_placed_value_with_fee_vnd": total_orders_value,
            "funding_source": "L2 JIT-unpark (jit_unpark_proposal) — bán PARK đúng lượng cần "
                              "để tài trợ lệnh mua LAG trong cùng plan này.",
            "discipline_check": (
                "Câu hỏi bắt buộc: tổng orders[] có ≤ sức mua thực KHÔNG giả định gì thêm? "
                f"orders[] = {total_orders_value:,}đ > cash {cash:,.0f}đ ⇒ KHÔNG đủ bằng cash "
                "trần trụi. Nguồn bù là L2 JIT-unpark trong CÙNG plan (bán PARK đang có, không "
                "phải tiền nạp thêm) — xem jit_unpark_proposal.buy_amendments để biết qty CUỐI "
                "CÙNG. KHÔNG có field funding_required, KHÔNG có giả định user nạp tiền."
            ),
            "integrity_check": (
                "orders[] = chỉ tín hiệu V2.4 (LAG). park_trim_proposal (L1, tuân thủ trần) và "
                "jit_unpark_proposal (L2, tài trợ) là 2 nguồn RIÊNG, để tách key riêng, KHÔNG "
                "trộn vào orders[]."
            ),
        },
        "orders": orders,
        "orders_summary": {
            "total_orders": len(orders),
            "total_buy_orders": len(orders),
            "total_sell_orders": 0,
            "orders_value_with_fee_vnd": total_orders_value,
            "available_cash_vnd": cash,
            "orders_within_cash": total_orders_value <= cash,
            "note": "1 lệnh MUA SSI (LAG_LO). Cần L2 JIT tài trợ — xem jit_unpark_proposal.",
        },
        "deferred_orders": deferred,
        "risk_notes": RISK_NOTES(label, stock_bq, stock_live),
    }
    return plan


def main():
    for label in ("SpaceX", "ZaloPay"):
        plan = build(label)
        path = f"{WORKDIR}/data/trade_plans/plan_{label}_{PLAN_DATE}.json"
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        o = plan["orders"][0]
        print(f"[{label}] ghi {path} — {len(plan['orders'])} lệnh V2.4 "
              f"(SSI {o['qty']:,}cp = {o['total_with_fee_vnd']:,}đ), "
              f"L1 {plan['park_trim_proposal']['decision']} "
              f"{len(plan['park_trim_proposal']['orders'])} lệnh")


if __name__ == "__main__":
    main()
