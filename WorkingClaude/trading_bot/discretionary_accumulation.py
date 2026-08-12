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

# ------------------------------- Target theo % active_nav (mặc định TẮT — xem resolve_target_qty)
# 25% active_nav vào MỘT tên discretionary thanh khoản mỏng là ngoài mọi ý định đã duyệt (mức
# user chốt 2026-08-10 là 5%); giá trị lớn hơn gần như chắc chắn là sai đơn vị (5 thay vì 0,05).
# Từ chối, không "kẹp về trần" — kẹp im lặng biến một typo thành một vị thế 25% NAV.
TARGET_PCT_ACTIVE_NAV_MAX = 0.25
# Dung sai của trần chi phí MỘT PHIÊN quanh ngân sách mục tiêu (xem bước 7b). Đặt bằng
# DYNAMIC_CEILING_TAU_MAX: mức nới giá tối đa mà luật trần động được phép, nên một lệnh hợp lệ
# không bao giờ chạm trần này, còn mọi cách hỏng đã biết (trần lệch pha với target, giá sai đơn
# vị) đều vượt nó nhiều lần. ⇒ bờ chặn phát biểu được: MỘT lệnh không bao giờ cam kết quá
# (1+slack) × target_pct × active_nav, tức ≤5,5% active_nav ở target 5%.
SESSION_BUDGET_CAP_SLACK = DYNAMIC_CEILING_TAU_MAX


def _pos_num(x):
    """True khi x là số dương THẬT (bool bị loại — `isinstance(True, int)` là True;
    inf/nan bị loại — `inf > 0` là True nhưng `int(floor(inf))` ném OverflowError, biến một
    giá trị rác thành CRASH giữa vòng lặp injector thay vì một fail-safe. Bắt được bằng chính
    selfcheck của mục tiêu tỷ trọng, 2026-08-12)."""
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x) and x > 0)


def _floor_to_lot(qty, lot_size):
    if lot_size <= 0:
        return 0
    return int(math.floor(qty / lot_size)) * lot_size


def resolve_target_qty(state, active_nav_vnd=None, price_vnd=None):
    """→ (target_qty | None, info) — SỐ CP mục tiêu của chương trình cho phiên này.

    Hai chế độ, chọn bằng sự CÓ MẶT của `state["target_pct_active_nav"]`:

    * `fixed_qty` (MẶC ĐỊNH, hành vi cũ nguyên vẹn) — `state["target_qty"]`, một con số chốt
      tại ngày duyệt. Đúng cho chương trình "gom đủ N cp rồi đóng" (TV1 bản gốc: 400cp).
    * `pct_active_nav` — mục tiêu là một TỶ TRỌNG (`0,05` = 5% active_nav), suy lại MỖI PHIÊN
      từ active_nav mới nhất. Đúng cho chỉ đạo user 2026-08-10 ("5% NAV/mã") vì active_nav đổi
      hằng ngày: một con số cp chốt cứng hôm nay là sai tỷ trọng ngày mai.

    Vì sao chia MẪU bằng GIÁ THỊ TRƯỜNG (`price_vnd` = giá phiên hoàn tất gần nhất) chứ không
    bằng trần no-chase: "5% NAV" là mệnh đề về GIÁ TRỊ THỊ TRƯỜNG của vị thế, đo tại giá thị
    trường. Neo mẫu vào trần sẽ làm QUY MÔ mục tiêu nhúc nhích theo một núm CHÍNH SÁCH (trần)
    — đúng cái lỗi §24 CLAUDE.md cấm (bẻ cong field này để field kia "vô tình" ra đúng số).
    Hệ quả có bờ: nếu khớp toàn bộ ở đúng trần động thì chi phí vượt mục tiêu tối đa τ (3%)
    của phần mua, tức ≤0,15% NAV — trong khi tầng thực thi (gate tiền P0 + cash-gate injector)
    vẫn chặn theo tiền thật.

    ⚠️ TÍNH CHẤT PHẢI BIẾT của chế độ tỷ trọng: đây là mục tiêu DUY TRÌ TỶ TRỌNG, không phải
    hạn mức chi phí tích luỹ. Giá giảm ⇒ mục tiêu (số cp) TĂNG ⇒ chương trình mua thêm để giữ
    5%; tổng tiền đã chi có thể vượt 5% NAV. Đó chính là hành vi DollarBill đang làm tay từ
    2026-08-11 (size theo GAP tới 5% mỗi ngày), không phải hành vi mới — nhưng nó là một quyết
    định CHÍNH SÁCH và phải được đọc như vậy. Chặn đà "bắt dao rơi" là việc của `hard_expiry`
    (catalyst phi-giá) + `max_no_chase_ceiling`, không phải của hàm này.

    None ⇒ caller PHẢI fail-safe (không đặt lệnh). Không có đường nào fail-OPEN.
    """
    lot = int(state.get("lot_size", 0) or 0)
    pct = state.get("target_pct_active_nav")
    if pct is None:
        q = state.get("target_qty")
        if not _pos_num(q):
            return None, {"mode": "fixed_qty", "reason": f"target_qty={q!r} không hợp lệ"}
        return int(q), {"mode": "fixed_qty", "target_qty": int(q),
                        "reason": "target CỐ ĐỊNH theo state.target_qty"}

    info = {"mode": "pct_active_nav", "target_pct_active_nav": pct}
    if not _pos_num(pct) or pct > TARGET_PCT_ACTIVE_NAV_MAX:
        info["reason"] = (f"target_pct_active_nav={pct!r} ngoài (0, "
                          f"{TARGET_PCT_ACTIVE_NAV_MAX}] — nghi sai đơn vị (0,05 ≠ 5)")
        return None, info
    if not _pos_num(active_nav_vnd):
        info["reason"] = (f"active_nav={active_nav_vnd!r} thiếu/không dương — KHÔNG suy được "
                          f"mục tiêu theo tỷ trọng (fail-safe, không đoán bằng số cũ)")
        return None, info
    if not _pos_num(price_vnd):
        info["reason"] = f"giá tham chiếu={price_vnd!r} thiếu/không dương"
        return None, info
    if lot <= 0:
        info["reason"] = f"lot_size={lot!r} không hợp lệ"
        return None, info

    target_value = float(pct) * float(active_nav_vnd)
    target_qty = _floor_to_lot(target_value / float(price_vnd), lot)
    info.update({"active_nav_vnd": float(active_nav_vnd), "price_vnd": float(price_vnd),
                 "target_value_vnd": round(target_value), "target_qty": int(target_qty)})
    if target_qty < lot:
        # NAV quá nhỏ / giá quá cao để mua nổi 1 lô. Fail-safe chứ KHÔNG trả 0: target=0 sẽ
        # bị tầng trên đọc nhầm là "đã gom đủ" và đóng chương trình.
        info["reason"] = (f"mục tiêu {target_value:,.0f}đ ÷ giá {price_vnd:,.0f} < 1 lô "
                          f"({lot}cp) — không đủ để đặt lệnh")
        return None, info
    info["reason"] = (f"target ĐỘNG = {pct:.2%} × active_nav {active_nav_vnd:,.0f}đ "
                      f"= {target_value:,.0f}đ ÷ giá {price_vnd:,.0f}đ → {target_qty:,}cp "
                      f"(làm tròn xuống lô {lot})")
    return int(target_qty), info


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
    pct = state.get("target_pct_active_nav")
    if pct is None:
        if state.get("target_qty", 0) <= 0:
            raise ValueError("target_qty phải > 0")
    else:
        # Target theo TỶ TRỌNG: `target_qty` không còn bắt buộc (nó được suy lại mỗi phiên).
        if not _pos_num(pct) or pct > TARGET_PCT_ACTIVE_NAV_MAX:
            raise ValueError(f"target_pct_active_nav={pct!r} ngoài (0, "
                             f"{TARGET_PCT_ACTIVE_NAV_MAX}] — nghi sai đơn vị (0,05 ≠ 5)")
        gap = state.get("topup_min_gap_pct_active_nav")
        if gap is not None and not (isinstance(gap, (int, float))
                                    and not isinstance(gap, bool) and 0 <= gap <= pct):
            raise ValueError(f"topup_min_gap_pct_active_nav={gap!r} phải trong [0, "
                             f"target_pct_active_nav] — deadband ≥ chính target là vô nghĩa")
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
                          plan_date, now_iso, anchor_prices=None, active_nav_vnd=None):
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
      active_nav_vnd     : active_nav mới nhất của account (mike/bin/compute_active_nav.py).
                           CHỈ dùng khi state khai `target_pct_active_nav`; thiếu ⇒ fail-safe
                           skip (KHÔNG rơi về một target_qty cũ — xem resolve_target_qty).

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

    # 4) mục tiêu chương trình — CỐ ĐỊNH (target_qty) hoặc TỶ TRỌNG (target_pct_active_nav,
    #    suy lại mỗi phiên từ active_nav + giá thị trường). Xem resolve_target_qty.
    target, target_info = resolve_target_qty(state, active_nav_vnd, prev_price_vnd)
    if target is None:
        return None, _decide("failsafe", f"FAILSAFE: {target_info['reason']}",
                             {"target_rule": target_info})
    pct_mode = target_info["mode"] == "pct_active_nav"
    remaining = target - int(filled_qty)

    # đã đủ target → dừng, KHÔNG mua quá (rule e).
    if remaining <= 0:
        if pct_mode:
            # Chương trình DUY TRÌ TỶ TRỌNG: "đủ" chỉ đúng cho PHIÊN NÀY. Đóng hẳn state ở đây
            # là sai — mai NAV tăng/giá giảm thì tỷ trọng lại tụt dưới mục tiêu mà không còn
            # state active nào để phát hiện. Chỉ có hard_expiry (catalyst phi-giá) mới đóng.
            return None, _decide("skip",
                                 f"đã đạt tỷ trọng mục tiêu: filled {filled_qty} ≥ target "
                                 f"{target} ({target_info['reason']}) — GIỮ state active để "
                                 f"phiên sau đo lại",
                                 {"remaining": remaining, "target": target,
                                  "target_rule": target_info})
        return None, _decide("completed",
                             f"đã gom đủ: filled {filled_qty} ≥ target {target}",
                             {"remaining": remaining, "mark_completed": True,
                              "target_rule": target_info})

    # 4b) deadband top-up (chỉ chế độ tỷ trọng): user chốt 2026-08-10/11 "không rải thêm chỉ vì
    #     lệch do lot-size, chỉ rải thêm nếu vị thế rơi RÕ RỆT dưới mục tiêu". Đây đúng là luật
    #     §22 (suy dẫn thuần từ dữ liệu sẵn có) nên phải là CODE, không phải văn xuôi để mỗi
    #     lượt LLM tự diễn giải một kiểu. Thiếu field ⇒ deadband = 0 (hành vi cũ).
    if pct_mode:
        gap_pct = state.get("topup_min_gap_pct_active_nav")
        if _pos_num(gap_pct):
            gap_vnd = remaining * float(prev_price_vnd)
            min_gap_vnd = float(gap_pct) * float(active_nav_vnd)
            target_info.update({"topup_min_gap_pct_active_nav": float(gap_pct),
                                "gap_vnd": round(gap_vnd),
                                "min_gap_vnd": round(min_gap_vnd)})
            if gap_vnd < min_gap_vnd:
                return None, _decide(
                    "skip",
                    f"deadband: thiếu {remaining}cp ({gap_vnd:,.0f}đ = "
                    f"{gap_vnd / float(active_nav_vnd):.2%} active_nav) < ngưỡng top-up "
                    f"{gap_pct:.2%} ({min_gap_vnd:,.0f}đ) — chưa rơi RÕ RỆT dưới mục tiêu",
                    {"remaining": remaining, "target": target, "target_rule": target_info})

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

    # 7b) TRẦN CHI PHÍ MỘT PHIÊN (chỉ chế độ tỷ trọng) — bất biến bằng TIỀN, không bằng số cp:
    #     chi phí xấu nhất của MỘT lệnh (`qty × giá đặt`) ≤ (1+slack) × toàn bộ ngân sách mục
    #     tiêu. Đây là thứ biến "5% NAV" từ một ý định thành một BỜ CHẶN kiểm chứng được.
    #     Vì sao cần (2 lỗ hổng cùng một gốc: SỐ LƯỢNG suy từ giá A trong khi TIỀN trả theo
    #     giá B). Mọi con số dưới đây ĐO ĐƯỢC LẠI bằng ca chạy trong
    #     `discretionary_target_pct_selfcheck.py` khối [I] — đừng trích số ở đây mà không chạy
    #     ca tương ứng; bản trước của comment này nêu 2 magnitude không truy được về ca nào và
    #     quant-skeptic đã bác đúng chỗ đó (vòng 1, 2026-08-12):
    #       · trần động neo TRUNG BÌNH 5 phiên còn target neo giá phiên CUỐI ⇒ thị trường rơi
    #         nhanh thì tỉ số hai giá vượt xa (1+τ). Ca I1/I2 (anchor 24k→14k): bỏ trần ⇒
    #         **7,39% NAV** trên mục tiêu 5%; có trần ⇒ 5,49%.
    #       · `prev_price` sai ĐƠN VỊ (feed trả giá ÷100) ⇒ target nở đúng 100× (ca I5:
    #         2.300cp → 239.900cp), mà guard sanity đơn vị chỉ tồn tại ở nhánh TRẦN
    #         (resolve_price_band), KHÔNG ở nhánh TARGET. Trần theo TIỀN chặn cả hai mà không
    #         cần đoán dải giá hợp lệ.
    #     ⚠️ THỨ TỰ LỚP — đây KHÔNG phải lớp duy nhất (quant-skeptic vòng 2 bác đúng chỗ này;
    #     bản trước của comment nói "duy nhất" và trích 51,26% là SAI khung cảnh):
    #       · BỜ NGOÀI = trần %ADV, `cap_vnd = per_session_cap_pct_adv × adv_ref_vnd`. Nó tính
    #         bằng TIỀN nên MIỄN NHIỄM lỗi đơn vị giá. Ở cấu hình thật của TV1 (adv_ref 720tr)
    #         nó một mình giữ ca sai đơn vị ở **7,35% NAV** (ca I10/I11).
    #       · BỜ TRONG = trần ngân sách này, siết tiếp 7,35% → **5,31%** (ca I12).
    #       · Con số **51,26%** (ca I6) chỉ đạt được khi CÔ LẬP lớp: harness thổi adv_ref lên
    #         5 tỷ (~7× thật) để tắt bờ ngoài. Đúng cho việc đo riêng một lớp, KHÔNG phải bán
    #         kính vụ nổ ở production — đừng trích nó ra khỏi ngữ cảnh đó.
    #     ⇒ Ai chỉnh `per_session_cap_pct_adv`/`adv_ref_vnd` là đang nới BỜ NGOÀI; ca I10 neo
    #     bất biến `worst_cost ≤ cap_vnd` để việc nới đó không lặng lẽ gỡ mất lưới còn lại.
    #       · Ca I8 là mặt kia của bờ: ở lệnh HỢP LỆ thật (SpaceX 08-13, 1.800cp) trần này
    #         KHÔNG bind — nếu nó bind ở ca thật thì nó là một núm sizing lén, không phải lưới.
    #     Hành vi: CO lệnh về vừa trần (không huỷ) — ca hợp lệ vẫn chạy; co xuống dưới 1 lô thì
    #     bỏ phiên. Luôn ghi lại thành số để người đọc plan thấy, không co lén.
    budget_shrink = None
    if pct_mode and session_qty > 0:
        budget_cap_vnd = float(target_info["target_value_vnd"]) * (1.0 + SESSION_BUDGET_CAP_SLACK)
        worst_cost_vnd = session_qty * limit_price
        if worst_cost_vnd > budget_cap_vnd:
            fitted = _floor_to_lot(budget_cap_vnd / limit_price, lot)
            budget_shrink = {"from_qty": int(session_qty), "to_qty": int(fitted),
                             "worst_cost_vnd": round(worst_cost_vnd),
                             "budget_cap_vnd": round(budget_cap_vnd),
                             "slack": SESSION_BUDGET_CAP_SLACK,
                             "reason": (f"chi phí xấu nhất {worst_cost_vnd:,.0f}đ "
                                        f"({session_qty}cp × {limit_price:,.0f}) vượt trần ngân "
                                        f"sách phiên {budget_cap_vnd:,.0f}đ "
                                        f"(= {1 + SESSION_BUDGET_CAP_SLACK:.2f} × mục tiêu) "
                                        f"⇒ CO còn {fitted}cp")}
            session_qty = fitted

    decision_extra = {
        "remaining": remaining, "target": target, "cap_qty": cap_qty,
        "cap_vnd": round(cap_vnd), "opportunistic": opportunistic,
        "opportunistic_boost": boost, "adv_ref_vnd": adv_ref,
        "prev_turnover_vnd": round(prev_turnover_vnd), "prev_price_vnd": prev_price_vnd,
        "limit_price_vnd": limit_price, "no_chase_ceiling_vnd": ceiling,
        "price_band_rule": band_info, "target_rule": target_info,
        "session_budget_shrink": budget_shrink,
    }

    if session_qty <= 0:
        if budget_shrink:
            return None, _decide("skip",
                                 f"trần ngân sách phiên co lệnh xuống dưới 1 lô: "
                                 f"{budget_shrink['reason']}", decision_extra)
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
            # Mục tiêu đến từ đâu: số cố định đã duyệt, hay tỷ trọng suy lại theo active_nav
            # hôm nay. Người đọc plan phải tái lập được con số target mà không cần chạy lại gì.
            "target_rule": target_info,
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
            + f"). Book=DISCRETIONARY_SPECIAL → TÁCH kế toán V2.4."
            + (f" [TARGET ĐỘNG: {target_info.get('reason', '')}]" if pct_mode else "")
            + (f" ⚠️ [TRẦN NGÂN SÁCH PHIÊN: {budget_shrink['reason']}]" if budget_shrink else "")
            + f" No-chase ≤{int(ceiling):,}"
            + (f" [TRẦN ĐỘNG: {band_info.get('reason', '')}]"
               if band_info.get("mode") == "dynamic" else "")
            + ". Hết hạn theo catalyst phi-giá (hard_expiry), không theo lịch."),
        "dcf_check": "N/A (SOTP/asset-backed deep-value, không dùng LAG/BAL gate)",
        "dcf_override_reason": "",
    }
    return order, _decide("inject", f"chèn {session_qty}cp", decision_extra)
