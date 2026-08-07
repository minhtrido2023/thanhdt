#!/usr/bin/env python3
"""Bước 1/2 — thay lệnh MUA SSI bằng lệnh MUA DRI trong orders[] của plan 2026-08-07.

Chạy TRƯỚC compute_jit_unpark.py (script đó đọc orders[] side==buy để biết cần tài trợ bao nhiêu).
Chưa merge L1/L2 ở bước này — merge ở bước 2 (merge_three_in_one_20260807.py).

DRI = discretionary override của user qua Mike (status CSV = WINDOW_PASSED 2026-08-06),
KHÔNG phải tín hiệu T+1 tự động.
"""
import json

PLAN = "/home/trido/thanhdt/WorkingClaude/data/trade_plans/plan_{acct}_2026-08-07.json"

# Giá LIVE DNSE 2026-08-07 ~12:1x ICT (phiên nghỉ trưa) — matchPrice G1
DRI_PX = 13100.0
DRI_PX_SRC = ("DNSE latest_trade G1 2026-08-07 ~12:15 ICT (matchPrice 13.10, ref 12.90, "
              "bid1 13.00 / offer1 13.10, trần 14.80 / sàn 11.00) — giá LIVE trong phiên, "
              "KHÔNG dùng BQ. Plan cũ ghi 12,900đ (= giá THAM CHIẾU, không phải giá khớp); "
              "giá khớp live đã +1.55% so với mức đó nên ref_price dùng 13,100đ.")

DD_RAW = ("DD DRI [LAG] (data 2026-08-05): thanh khoản OK (ADV3T 5.46 tỷ/phiên) · nền YoY dương "
          "(surprise không phồng do nền âm) | FA: ROE5Y 15.8% · ROE_Min3Y 13.5% · FSCORE 6 · "
          "D/E 0.28 · PE 4.21 | 🟢 DCF: CHEAP (giá trị hợp lý ~20,885đ vs giá 13,000đ, "
          "MoS +37.8%, robust)")

QTY = {"SpaceX": 3500, "ZaloPay": 1800}
# active_nav dùng cho sizing_note (đã tính lại theo DNSE live trong nav_basis của plan)
ANAV = {"SpaceX": 951711143, "ZaloPay": 502841454}


def build_order(acct):
    qty = QTY[acct]
    val = int(round(qty * DRI_PX))
    fee = int(round(val * 0.00075))
    return {
        "id": "BUY-DRI-LAG-01",
        "ticker": "DRI",
        "side": "buy",
        "qty": qty,
        "ref_price": DRI_PX,
        "ref_price_source": DRI_PX_SRC,
        "order_type": "LO",
        "limit_price_vnd": int(DRI_PX),
        "estimated_cost_vnd": val,
        "fee_est_vnd": fee,
        "total_with_fee_vnd": val + fee,
        "book": "LAG",
        "play_type": "LAG_HI",
        "priority": 1,
        "urgency": "normal",
        "timing": "BUY@13:15",
        "timing_note": (
            "Phiên chiều 13:00–14:45 là cửa sổ thực thi còn lại của ngày 2026-08-07. "
            "DRI KHÔNG bị ràng buộc cửa sổ entry T+1 tự động (status CSV = WINDOW_PASSED "
            "2026-08-06) — đây là lệnh discretionary override của user, nên nếu không khớp "
            "chiều nay thì user quyết định có carry sang phiên sau hay không, KHÔNG tự động đóng."),
        "hold_periods": 25,
        "stop_exempt": False,
        "slot_exempt": False,
        "dd_note": DD_RAW,
        "sizing_note": (
            f"Qty {qty:,}cp do USER CHỈ ĐỊNH (discretionary override qua Mike, giữ nguyên số lượng "
            f"đã chốt hôm qua), KHÔNG phải do allocator sizing lại. {qty:,}cp × {DRI_PX:,.0f}đ = "
            f"{val:,}đ + phí 0.075% ({fee:,}đ) = {val+fee:,}đ. Đối chiếu slot lý thuyết: LAG_HI "
            f"10.0% × active_nav {ANAV[acct]:,} = {int(ANAV[acct]*0.10):,}đ ⇒ lệnh này "
            f"({val:,}đ) NẰM DƯỚI slot, không vượt. %ADV: {val:,}đ / ADV3T 5,460,000,000đ = "
            f"{val/5.46e9*100:.2f}% ⇒ cap_lag_orders KHÔNG binding."),
        "funding_note": (
            "Lệnh này PHỤ THUỘC nguồn tài trợ L2 JIT-unpark trong CÙNG plan (bán PARK đang có, "
            "KHÔNG phải tiền nạp thêm). Nếu user KHÔNG duyệt phần L2, lệnh phải bị co/bỏ theo "
            "sức mua thật."),
        "gates_passed": [
            "8L rating = 2 (≤3) — truy vấn point-in-time tav2_bq.fa_ratings_8l, time=2026-07-30 "
            "≤ asof 2026-08-06, ĐÚNG SQL của lag_filter_low_rating(). PASS gate cứng LAG.",
            "Golden floor — ROE_Min3Y 13.5% ≥ 0 (đã encode trong rating 8L v3).",
            "DCF — CHEAP, giá trị hợp lý ~20,885đ vs giá 13,000đ, MoS +37.8%, robust ⇒ KHÔNG "
            "cần dcf_override_reason.",
            "DD cờ đỏ — dd_red_flags rỗng trong CSV nguồn; thanh khoản ADV3T 5.46 tỷ/phiên "
            "(trên sàn 2 tỷ), nền YoY dương.",
            "excluded_tickers — DRI không nằm trong danh sách của account này.",
            "LAG EXCLUDE list (IVS/TMG) — DRI không thuộc danh sách user đã loại tường minh.",
            "%ADV cap — cap_lag_orders() áp lúc thực thi, không binding (xem sizing_note).",
        ],
        "override_note": (
            "⚠️ ĐÂY LÀ LỆNH DISCRETIONARY OVERRIDE CỦA USER (John) qua Mike, job "
            "DollarBill_20260807_050844 — KHÔNG phải tín hiệu tự động. Bằng chứng: "
            "golive_v23_recommendations_2026-08-06.csv ghi DRI status = 'WINDOW_PASSED "
            "2026-08-06', tức DRI ĐÃ QUA cửa sổ entry T+1 chuẩn và KHÔNG nằm trong 6 mã "
            "due_today của filter_lag_entry_window.py (PGS/PHR/SSI/TVN/VNF/VSI). Lệnh này thay "
            "cho lệnh MUA SSI mà plan bản trước đề xuất."),
        "watch_note": (
            "🟡 WATCH cao su (context_planning_mini, user duyệt 2026-08-06): DRI thuộc nhóm "
            "GVR/PHR/DPR/DRI/TRC/HRC. Ngưỡng xét lại luận điểm PEAD ngành = RSS3 thủng 2.26 "
            "USD/kg. ĐÃ KIỂM TRA HÔM NAY: data/rubber_monthly.csv mới nhất 2026-07 = 2.78; "
            "data/rubber_weekly.csv mới nhất có giá 2026-08-05 = 2.654. Cả hai ĐỀU TRÊN 2.26 "
            "(+17.4% so ngưỡng) ⇒ WATCH CHƯA kích hoạt, không phải xét lại luận điểm. "
            "(KHÔNG dùng nhãn 'phá đáy 52 tuần' của rubber_weekly.py — nhãn đó là bug đo lường "
            "đã xác nhận 2026-08-06.)"),
        "bear_risk_note": (
            "⚠️ Nếu regime DT5G chuyển BEAR, vị thế này sẽ bị BÁN theo allocator (w_LAG=0 khi "
            "BEAR). Đây là cơ chế sẵn có, công khai để user biết trước khi duyệt."),
        "dcf_check": {
            "status": "CHEAP",
            "fair_value_vnd": 20885,
            "price_at_dcf_vnd": 13000,
            "margin_of_safety": 0.378,
            "robust": True,
            "as_of": "2026-08-06",
            "data_date": "2026-08-05",
            "note": ("DCF CHEAP + robust ⇒ KHÔNG cần dcf_override_reason. Lưu ý giá dùng trong "
                     "DCF là 13,000đ (T-1); giá live hôm nay 13,100đ ⇒ MoS thực tế ~37.3%, "
                     "vẫn CHEAP rộng rãi."),
        },
        "dcf_override_reason": "",
        "dd_check": {
            "has_red_flag": False,
            "red_flags": [],
            "as_of": "2026-08-06",
            "data_date": "2026-08-05",
            "evidence": ("CSV nguồn golive_v23_recommendations_2026-08-06.csv: due_diligence của "
                         "DRI không có cờ đỏ nào (không THANH_KHOAN_CHET, không NGOAI_UNIVERSE, "
                         "không FLOOR_FAIL). ADV3T 5.46 tỷ/phiên."),
        },
        "dd_override_reason": "",
        "limit_price_note": ("limit_price_vnd là THÔNG TIN cho người đọc — PlannedOrder không có "
                             "field này, load_plan() lọc bỏ. Executor định giá từ ref_price "
                             "(13,100đ, DNSE live) + urgency."),
    }


def main():
    for acct in ("SpaceX", "ZaloPay"):
        path = PLAN.format(acct=acct)
        p = json.load(open(path, encoding="utf-8"))
        assert [o["ticker"] for o in p["orders"]] == ["SSI"], \
            f"{acct}: orders[] không phải đúng 1 lệnh SSI như kỳ vọng — dừng, không ghi đè mù"
        p["orders"] = [build_order(acct)]
        o = p["orders"][0]
        p["orders_summary"] = {
            "total_orders": 1,
            "total_buy_orders": 1,
            "total_sell_orders": 0,
            "orders_value_with_fee_vnd": o["total_with_fee_vnd"],
            "available_cash_vnd": p["nav_basis"]["available_cash_vnd"],
            "orders_within_cash": False,
            "note": "TẠM (bước 1/2) — 1 lệnh MUA DRI. L1/L2 sẽ được MERGE vào orders[] ở bước 2.",
        }
        json.dump(p, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"{acct}: orders[] ← BUY DRI {o['qty']:,}cp @ {o['ref_price']:,.0f}đ "
              f"= {o['estimated_cost_vnd']:,}đ (+phí {o['fee_est_vnd']:,}) "
              f"= {o['total_with_fee_vnd']:,}đ")


if __name__ == "__main__":
    main()
