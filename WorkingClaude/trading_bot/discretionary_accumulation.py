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

# ------------------------------------------------------- P1: trần no-chase ĐỘNG (mặc định TẮT)
# Trần cố định là một SỐ chốt tại ngày duyệt; nó đúng cho tới khi giá đi khỏi vùng đó rồi IM
# LẶNG biến chương trình gom thành "không bao giờ khớp". Ca thật TV1: trần 20.000đ duyệt
# 2026-07-23 (giá lúc đó 19.900), tới 2026-08-12 thị trường 20.200-20.500 ⇒ **0cp** khớp ở giá
# ≤20.000đ trên tổng 39.500cp cả phiên. Không cơ chế nào phát hiện việc trần đã hết đúng.
#
# Nghiên cứu Taylor_20260812_091343 (mike/agents/Taylor/research/thin_exec_20260812/, N=1.840
# phiên-mã, rổ 23 mã ADV20 200-2.500tr): trần = anchor×(1+τ), anchor = TRUNG BÌNH giá 5 phiên
# gần nhất, τ=3% ⇒ fill 0,627→0,783, %phiên trắng tay 22,4%→6,1%, giá trả thêm +0,77pp
# (đổi chác ~20:1 nghiêng về nới). Anchor càng cũ càng ĐẮT mà fill gần như không hơn — giữ trần
# cũ KHÔNG "mua rẻ", nó chỉ mua ÍT.
#
# MẶC ĐỊNH TẮT. Bật cần ĐỒNG THỜI hai thứ, vì đây là quyết định CHÍNH SÁCH (§22) không phải
# kỹ thuật:
#   1. state["dynamic_ceiling"]["enabled"] = true
#   2. state["price_band"]["max_no_chase_ceiling"] = <VND> — trần TUYỆT ĐỐI user duyệt MỘT LẦN
#      cho cả chương trình. Không có nó thì trần động không có cận trên nào: anchor trôi lên
#      vài tháng có thể đưa giá mua vượt xa mức user đã đồng ý. Thiếu ⇒ fail-safe về band cố định.
# Mọi điều kiện khác thiếu/rác ⇒ CŨNG fail-safe về band cố định. Không có đường nào fail-OPEN.
DYNAMIC_CEILING_TAU_DEFAULT = 0.03      # chính sách user duyệt 2026-08-12 (John, qua Mike)
DYNAMIC_CEILING_TAU_MAX = 0.10          # τ > 10% = gần như bỏ trần → từ chối, không phải "nới"
DYNAMIC_CEILING_SESSIONS_DEFAULT = 5    # đúng anchor đã đo trong exp_ceiling_tolerance.py
DYNAMIC_CEILING_SESSIONS_MAX = 20
# Giá anchor lệch quá xa giá mới nhất ⇒ nghi sai ĐƠN VỊ (nghìn đồng vs VND — lỗi thật đã cắn
# trong chính nghiên cứu này) hoặc feed hỏng ⇒ fail-safe, KHÔNG dùng để tính trần.
_ANCHOR_SANITY_LO, _ANCHOR_SANITY_HI = 0.5, 2.0


def _pos_num(x):
    """True khi x là số dương THẬT (bool bị loại — `isinstance(True, int)` là True)."""
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x > 0


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


def resolve_price_band(state, anchor_prices=None, latest_price=None):
    """→ (no_chase_ceiling, resting_limit, info) — band GIÁ dùng cho phiên này.

    MẶC ĐỊNH (không truyền `anchor_prices`, hoặc cờ tắt) trả về ĐÚNG band cố định trong
    state — hành vi cũ nguyên vẹn.

    `anchor_prices`: giá tham chiếu các phiên ĐÃ HOÀN TẤT, thứ tự CŨ→MỚI (chronological).
    Chỉ `sessions` phần tử cuối được dùng. `latest_price`: giá mới nhất, dùng làm mốc kiểm
    tra tỉnh táo (sanity) cho anchor; None ⇒ dùng chính phần tử cuối của anchor_prices.

    Khi trần động ăn: `ceiling = min(mean(anchor 5 phiên)×(1+τ), max_no_chase_ceiling)`, và
    `resting_limit` được KÉO THEO CÙNG TỈ LỆ (`resting/ceiling` của band đã duyệt giữ nguyên
    hình dạng, chỉ đổi MỨC). Vì sao phải kéo theo: executor tính giá đặt từ `ref_price`
    (= resting_limit) — `cap = ref×(1+chase%)` rồi mới min với trần cứng — nên nâng RIÊNG
    trần cứng mà để resting đứng yên thì `ref×(1+chase%)` trở thành ràng buộc buộc, và với
    chase động (clamp(2×rvol, 1,5%, 4%)) phần lớn lợi ích của P1 bốc hơi.

    Trần động có thể HẠ trần xuống khi anchor đi xuống — đó là ĐÚNG luật, không phải lỗi:
    luật đối xứng, và hạ trần chỉ làm mua rẻ hơn/ít hơn, không bao giờ mua đắt hơn.
    """
    band = state["price_band"]
    fixed_ceiling = float(band["no_chase_ceiling"])
    fixed_resting = float(band["resting_limit"])
    info = {"mode": "fixed", "ceiling_vnd": fixed_ceiling, "resting_vnd": fixed_resting,
            "fixed_ceiling_vnd": fixed_ceiling, "fixed_resting_vnd": fixed_resting}

    cfg = state.get("dynamic_ceiling") or {}
    if cfg.get("enabled") is not True:
        info["reason"] = "dynamic_ceiling.enabled ≠ true (MẶC ĐỊNH TẮT)"
        return fixed_ceiling, fixed_resting, info

    def _failsafe(reason):
        info["mode"] = "fixed_failsafe"
        info["reason"] = f"FAIL-SAFE → band cố định: {reason}"
        return fixed_ceiling, fixed_resting, info

    tau = cfg.get("tau", DYNAMIC_CEILING_TAU_DEFAULT)
    if not _pos_num(tau) or tau > DYNAMIC_CEILING_TAU_MAX:
        return _failsafe(f"tau={tau!r} ngoài (0, {DYNAMIC_CEILING_TAU_MAX}]")
    n = cfg.get("sessions", DYNAMIC_CEILING_SESSIONS_DEFAULT)
    if (not isinstance(n, int) or isinstance(n, bool) or n < 1
            or n > DYNAMIC_CEILING_SESSIONS_MAX):
        return _failsafe(f"sessions={n!r} ngoài [1, {DYNAMIC_CEILING_SESSIONS_MAX}]")

    max_cap = band.get("max_no_chase_ceiling")
    if not _pos_num(max_cap):
        return _failsafe("price_band.max_no_chase_ceiling chưa khai — trần động BẮT BUỘC có "
                         "cận trên tuyệt đối do user duyệt (§chính sách)")
    if fixed_ceiling <= 0 or fixed_resting <= 0:
        return _failsafe("band cố định không hợp lệ (≤0)")

    prices = list(anchor_prices or [])
    if not all(_pos_num(p) for p in prices):
        return _failsafe("anchor_prices có phần tử không phải số dương")
    if len(prices) < n:
        return _failsafe(f"chỉ có {len(prices)} giá anchor, cần {n} phiên")
    prices = [float(p) for p in prices[-n:]]

    ref = float(latest_price) if _pos_num(latest_price) else prices[-1]
    if any(not (_ANCHOR_SANITY_LO * ref <= p <= _ANCHOR_SANITY_HI * ref) for p in prices):
        return _failsafe(f"giá anchor lệch >{_ANCHOR_SANITY_HI:g}× hoặc <{_ANCHOR_SANITY_LO:g}× "
                         f"giá mới nhất ({ref:,.0f}) — nghi sai đơn vị/feed hỏng")

    anchor = sum(prices) / len(prices)
    ceiling = math.floor(min(anchor * (1.0 + tau), float(max_cap)))
    if ceiling <= 0:
        return _failsafe("trần động tính ra ≤0")
    resting = math.floor(min(float(ceiling), fixed_resting * ceiling / fixed_ceiling))
    if resting <= 0:
        return _failsafe("resting động tính ra ≤0")
    if resting > ceiling:   # bất biến no-chase — không thể xảy ra theo công thức, chặn ở đây
        return _failsafe(f"resting động ({resting}) > trần động ({ceiling}) — vi phạm no-chase")

    info.update({
        "mode": "dynamic", "ceiling_vnd": float(ceiling), "resting_vnd": float(resting),
        "tau": float(tau), "sessions": n, "anchor_vnd": round(anchor, 2),
        "anchor_prices": prices, "max_no_chase_ceiling_vnd": float(max_cap),
        "capped_by_max": bool(anchor * (1.0 + tau) > float(max_cap)),
        "reason": (f"trần động = mean({n} phiên)={anchor:,.0f}×(1+{tau:.2%}) "
                   f"→ {ceiling:,} (cố định {fixed_ceiling:,.0f}), resting kéo theo "
                   f"cùng tỉ lệ → {resting:,}"),
    })
    return float(ceiling), float(resting), info


def compute_session_order(state, filled_qty, prev_turnover_vnd, prev_price_vnd,
                          plan_date, now_iso, anchor_prices=None):
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
    #    Trần ĐỘNG (P1) chỉ ăn khi state bật cờ + khai cận trên tuyệt đối + đủ giá anchor;
    #    mọi trường hợp khác trả đúng band cố định (xem resolve_price_band).
    ceiling, limit_price, band_info = resolve_price_band(state, anchor_prices, prev_price_vnd)
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
        "price_band_rule": band_info,
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
        # plan: "CASH — KHÔNG dùng margin"). cash_only=True → executor chọn gói vay hợp
        # lệ RIÊNG cho mã (bug TV1 07-28: gói 1841 mainboard SpaceX gắn tự động → DNSE
        # reject mã UPCOM; đúng gói cho TV1 = 1122). Đọc từ state, default True cho cả họ.
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
            # Audit-trail: band giá phiên này đến từ đâu (cố định hay luật động P1). Field này
            # KHÔNG có trong PlannedOrder ⇒ load_plan() bỏ qua; nó tồn tại cho người đọc plan
            # và cho ledger, không phải cho executor.
            "price_band_rule": band_info,
        },
        "source_plan": state.get("source_plan"),
        "note": (
            f"AUTO-INJECT lệnh gom {ticker} (playbook Low-Liquidity Discretionary "
            f"Accumulation). Đã gom {filled_qty}/{target}cp, còn {remaining}cp. "
            f"Phiên này {session_qty}cp (cap {cap_qty}"
            + (f", OPPORTUNISTIC ×{m:g} vì turnover phiên gần nhất "
               f"{prev_turnover_vnd/1e6:,.0f}tr ≥ {k:g}×adv_ref" if opportunistic else "")
            + f"). Book=DISCRETIONARY_SPECIAL → TÁCH kế toán V2.4. No-chase ≤{int(ceiling):,}"
            + (f" [TRẦN ĐỘNG: {band_info.get('reason', '')}]"
               if band_info.get("mode") == "dynamic" else "")
            + ". Hết hạn theo catalyst phi-giá (hard_expiry), không theo lịch."),
        "dcf_check": "N/A (SOTP/asset-backed deep-value, không dùng LAG/BAL gate)",
        "dcf_override_reason": "",
    }
    return order, _decide("inject", f"chèn {session_qty}cp", decision_extra)
