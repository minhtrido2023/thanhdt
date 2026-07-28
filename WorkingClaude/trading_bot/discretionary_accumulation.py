"""discretionary_accumulation.py — engine tính lệnh gom cho vị thế DISCRETIONARY_SPECIAL
thanh khoản thấp ("Low-Liquidity Discretionary Accumulation" playbook, Taylor 2026-07-24,
memo mike/agents/Taylor/research/lowliq_execution_playbook_20260724.md).

Đây là engine THUẦN (không I/O, không gọi broker/BQ) để dễ selfcheck. Driver I/O nằm ở
`mike/bin/discretionary_accumulation_inject.py` (đọc broker positions live + DNSE quote,
chèn lệnh vào plan_<account>_<date>.json, cập nhật state).

Doctrine (bất biến — §4 memo):
  1. Kỷ luật là GIÁ (price-band) + KIÊN NHẪN (nhiều phiên), KHÔNG phải lịch/%-KL-trong-ngày.
  2. Gom NHIỀU khi người bán XUẤT HIỆN (opportunistic), ÍT/không khi họ vắng.
  3. Under-fill giá tốt > full-fill do chase.
  4. Hết hạn theo CATALYST (phi-giá), không theo calendar.
  5. Đây là TỐI THIỂU-HOÁ CHI PHÍ THỰC THI, KHÔNG phải alpha — không có edge backtest-able.

KHÔNG chạm kế toán V2.4 (BAL/LAG/CAPIT/PARK). Book cố định = DISCRETIONARY_SPECIAL.
"""

import math

BOOK = "DISCRETIONARY_SPECIAL"


def _floor_to_lot(qty, lot_size):
    if lot_size <= 0:
        return 0
    return int(math.floor(qty / lot_size)) * lot_size


def validate_state(state):
    """Kiểm tra bất biến cấu hình state — raise ValueError nếu no-chase có thể bị vi phạm
    hoặc tham số vô nghĩa. Gọi khi load state, TRƯỚC khi tính lệnh."""
    band = state.get("price_band") or {}
    ceiling = band.get("no_chase_ceiling")
    resting = band.get("resting_limit")
    if ceiling is None or resting is None:
        raise ValueError("price_band thiếu no_chase_ceiling/resting_limit")
    if resting > ceiling:
        raise ValueError(
            f"resting_limit ({resting}) > no_chase_ceiling ({ceiling}) — vi phạm no-chase")
    if state.get("target_qty", 0) <= 0:
        raise ValueError("target_qty phải > 0")
    lot = state.get("lot_size", 0)
    if lot <= 0:
        raise ValueError("lot_size phải > 0")
    cap_pct = state.get("per_session_cap_pct_adv")
    if cap_pct is None or not (0 < cap_pct <= 1):
        raise ValueError("per_session_cap_pct_adv phải trong (0,1]")
    return True


def compute_session_order(state, filled_qty, prev_turnover_vnd, prev_price_vnd,
                          plan_date, now_iso):
    """Tính lệnh gom cho MỘT phiên (plan_date).

    Inputs:
      state              : dict cấu hình + ledger (xem schema state file).
      filled_qty         : SỐ CP đã gom được TÍNH TỪ BROKER (nguồn chân lý, không phải bộ
                           đếm nội bộ). = broker_total(ticker) − baseline_qty_before_program.
                           None nếu KHÔNG đọc được broker → fail-safe skip.
      prev_turnover_vnd  : notional (VND) của phiên hoàn tất gần nhất (KL × giá khớp). None
                           nếu không đọc được → fail-safe skip (rule c).
      prev_price_vnd     : giá khớp/đóng cửa phiên gần nhất (context + opportunistic gate).
                           None → fail-safe skip.
      plan_date          : "YYYY-MM-DD" ngày lệnh sẽ được đặt.
      now_iso            : timestamp ISO để ghi vào order/decision.

    Returns (order_or_None, decision) — decision luôn có 'action' ∈
      {'inject','skip','completed','failsafe','halted','inactive'} + 'reason'.
    order_or_None: dict order sẵn để chèn vào plan['orders'] (book=DISCRETIONARY_SPECIAL),
    hoặc None nếu không nên đặt lệnh phiên này.
    """
    validate_state(state)
    ticker = state["ticker"]

    def _decide(action, reason, extra=None):
        d = {"action": action, "reason": reason, "ticker": ticker,
             "plan_date": plan_date, "filled_qty": filled_qty}
        if extra:
            d.update(extra)
        return d

    # 1) trạng thái chương trình
    status = state.get("status", "active")
    if status != "active":
        return None, _decide("inactive", f"status={status} (không active)")

    # 2) hard_expiry — CATALYST phi-giá, do NGƯỜI xác nhận (kiểm toán/đình chỉ giao dịch).
    #    Engine chỉ TÔN TRỌNG cờ halted; KHÔNG tự suy ra sự kiện pháp lý/kiểm toán.
    hx = state.get("hard_expiry") or {}
    if hx.get("halted"):
        return None, _decide("halted",
                             f"hard_expiry halted: {hx.get('halted_reason', 'n/a')}")

    # 3) fail-safe: thiếu dữ liệu → KHÔNG mua bởi thiếu thông tin (rule c).
    if filled_qty is None:
        return None, _decide("failsafe",
                             "FAILSAFE: không đọc được vị thế broker → không mua bởi thiếu thông tin")
    if prev_turnover_vnd is None or prev_price_vnd is None:
        return None, _decide("failsafe",
                             "FAILSAFE: thiếu giá/KL phiên gần nhất (DNSE) → không mua bởi thiếu thông tin")

    # 4) đã đủ target → dừng, KHÔNG mua quá (rule e). Caller đánh dấu status=completed.
    target = int(state["target_qty"])
    remaining = target - int(filled_qty)
    if remaining <= 0:
        return None, _decide("completed",
                             f"đã gom đủ: filled {filled_qty} ≥ target {target}",
                             {"remaining": remaining, "mark_completed": True})

    # 5) price-band: LO ≤ resting_limit, resting_limit ≤ no_chase_ceiling (validate_state
    #    đã đảm bảo). No-chase là bất biến — không bao giờ đặt > ceiling.
    band = state["price_band"]
    ceiling = float(band["no_chase_ceiling"])
    limit_price = float(band["resting_limit"])
    lot = int(state["lot_size"])
    adv_ref = float(state["adv_ref_vnd"])
    cap_pct = float(state["per_session_cap_pct_adv"])

    # 6) trần participation/phiên (bảo vệ, thường KHÔNG bind ở size nhỏ).
    cap_vnd = cap_pct * adv_ref

    # opportunistic: phiên gần nhất có "bán thật" (turnover ≥ k×adv_ref) VÀ giá ≤ ceiling
    # → cho phép nhân cap × m để hốt phần bán thật (rule doctrine 2). Cơ học, không tuỳ nghi.
    opp = state.get("opportunistic") or {}
    k = float(opp.get("k", 2.0))
    m = float(opp.get("m", 2.0))
    opportunistic = (prev_turnover_vnd >= k * adv_ref) and (prev_price_vnd <= ceiling)
    boost = m if opportunistic else 1.0
    cap_vnd *= boost

    cap_qty = _floor_to_lot(cap_vnd / limit_price, lot)

    # 7) size phiên = min(remaining, cap_qty), làm tròn xuống lô.
    session_qty = _floor_to_lot(min(remaining, cap_qty), lot)

    decision_extra = {
        "remaining": remaining, "target": target, "cap_qty": cap_qty,
        "cap_vnd": round(cap_vnd), "opportunistic": opportunistic,
        "opportunistic_boost": boost, "adv_ref_vnd": adv_ref,
        "prev_turnover_vnd": round(prev_turnover_vnd), "prev_price_vnd": prev_price_vnd,
        "limit_price_vnd": limit_price, "no_chase_ceiling_vnd": ceiling,
    }

    if session_qty <= 0:
        return None, _decide("skip",
                             f"session_qty=0 (cap_qty={cap_qty}, remaining={remaining})",
                             decision_extra)

    order = {
        "id": f"BUY-{ticker}-DISC-{plan_date}",
        "ticker": ticker,
        "side": "buy",
        "qty": int(session_qty),
        "ref_price": int(limit_price),
        "ref_price_source": state.get("ref_price_source",
                                      "DNSE_G1_latest (LIVE same-day; KHÔNG dùng BQ)"),
        "order_type": "LO",
        "limit_price_vnd": int(limit_price),
        "hard_no_chase_ceiling_vnd": int(ceiling),
        "estimated_cost_vnd": int(session_qty * limit_price),
        "book": BOOK,
        # Lệnh gom discretionary special = thanh toán TIỀN MẶT theo thiết kế (master
        # plan: "CASH — KHÔNG dùng margin"). cash_only=True → executor đặt lệnh KHÔNG
        # gắn gói vay account (bug TV1 07-28: gói 1841 SpaceX gắn tự động → DNSE reject
        # mã UPCOM không đủ điều kiện). Đọc từ state, default True cho cả họ discretionary.
        "cash_only": bool(state.get("cash_only", True)),
        "play_type": "DISCRETIONARY_SPECIAL_SITUATION",
        "priority": int(state.get("priority", 5)),
        "urgency": "normal",
        "timing": (f"LO ≤{int(limit_price):,} no-chase — bỏ phiên nếu best offer "
                   f">{int(ceiling):,}; lệnh chờ dai dẳng (resting-bid), re-đặt mỗi phiên tới đủ target/hết catalyst"),
        "hold_periods": None,
        "hold_horizon": state.get("hold_horizon",
                                  "buy-and-hold dài hạn (asset-backed). No price stop; exit chỉ theo hard_expiry phi-giá."),
        "stop_exempt": True,
        "slot_exempt": True,
        "outside_v24_system": True,
        "auto_injected": True,
        "auto_injected_at": now_iso,
        "opportunistic": opportunistic,
        "accumulation_program": {
            "target_qty": target, "filled_before_this": int(filled_qty),
            "min_acceptable_qty": state.get("min_acceptable_qty"),
            "soft_window_sessions": state.get("soft_window_sessions"),
            "soft_window_start_date": state.get("soft_window_start_date"),
            "state_file": state.get("_state_file"),
        },
        "source_plan": state.get("source_plan"),
        "note": (
            f"AUTO-INJECT lệnh gom {ticker} (playbook Low-Liquidity Discretionary "
            f"Accumulation). Đã gom {filled_qty}/{target}cp, còn {remaining}cp. "
            f"Phiên này {session_qty}cp (cap {cap_qty}"
            + (f", OPPORTUNISTIC ×{m:g} vì turnover phiên gần nhất "
               f"{prev_turnover_vnd/1e6:,.0f}tr ≥ {k:g}×adv_ref" if opportunistic else "")
            + f"). Book=DISCRETIONARY_SPECIAL → TÁCH kế toán V2.4. No-chase ≤{int(ceiling):,}. "
            "Hết hạn theo catalyst phi-giá (hard_expiry), không theo lịch."),
        "dcf_check": "N/A (SOTP/asset-backed deep-value, không dùng LAG/BAL gate)",
        "dcf_override_reason": "",
    }
    return order, _decide("inject", f"chèn {session_qty}cp", decision_extra)
