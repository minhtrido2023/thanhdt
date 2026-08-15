# -*- coding: utf-8 -*-
"""Trần giá mua "không đuổi" (no-chase ceiling) — luật A, sinh MỘT LẦN lúc lập plan.

QUYẾT ĐỊNH CHÍNH SÁCH, KHÔNG PHẢI EDGE (user chốt 2026-08-15, bus event
`ceiling-rule-AB-user-decision-CORRECTED`, decided_by=user). Nghiên cứu nền:
`mike/agents/Taylor/research/ceiling_ab_pacing_20260814/README.md`.

  · Rule A thắng Rule B (mean-5) về FILL ở 30/30 mã (+1,93pp) — nhưng thắng vì **trả giá cao
    hơn** (+16,5 bps so VWAP; giá BIÊN của phần mua thêm +85 bps), không phải vì thực thi khéo.
  · Trên implementation shortfall (gộp cả giá lẫn phần chưa mua được): Δ(A−B) = +4,89 bps
    NGHIÊNG VỀ B, **không có ý nghĩa thống kê** (t gộp-theo-ngày = +0,20, N=475 ngày) và **ĐỔI
    DẤU** theo giả định mua bù (lag 0/5/20 phiên ⇒ t = +1,34 / +0,20 / −0,83).
  · 65,1% campaign hai luật cho kết quả Y HỆT.
  · DSR/PBO KHÔNG áp dụng được (không có chuỗi NAV) ⇒ **cấm trích bất kỳ số nào ở đây như
    CAGR/edge/"cải tiến có bằng chứng"**.

Lý do wire là hình dạng BẢO HIỂM: B thắng nhỏ và thường xuyên; A thắng hiếm nhưng rất lớn (đuôi
trái của B tới −3.195 bps ở ca giá chạy mất, không mua được gì). Chấp nhận trả thêm ~16 bps
trung bình để cắt rủi ro kẹt hoàn toàn — cùng khuôn mẫu đã dùng cho sàn ADV3T 2 tỷ (wire vì hiệu
quả vốn, backtest nói ngược, ghi rõ trong comment code).

BỐN BẤT BIẾN — hỏng bất kỳ cái nào ⇒ FAIL-CLOSED về luật cũ (trần = `entry_anchor_price`):
  1. τ ∈ (0, RULE_A_TAU_MAX]. τ > 10% = gần như bỏ trần, đó là từ chối chứ không phải "nới".
  2. anchor > 0 và parse được.
  3. `hard_no_chase_ceiling_vnd` trong plan PHẢI tái lập ĐÚNG BẰNG `floor(anchor × (1+τ))` —
     đây là cái chặn plan sửa tay ghi một con số to rồi dán nhãn "rule A".
  4. `ceiling_anchor_date` < `plan_date`. **Đây là bất biến CỐT LÕI**: trần chỉ được neo vào
     phiên ĐÃ ĐÓNG trước ngày thực thi, tái lập 1 lần/ngày lúc lập plan. Trượt/tái tính TRONG
     PHIÊN là đuổi giá thật sự — khác hẳn thứ đã đo trong nghiên cứu, và sẽ làm mọi kết luận
     CONFIRMED ở trên hết hiệu lực.

§24 coding_guidelines: trần là **field riêng cưỡng chế bằng code**. `executor.py` chỉ ĐỌC
`hard_no_chase_ceiling_vnd` qua `_hard_buy_ceiling()` — file này KHÔNG đụng executor, và
executor không bao giờ tự suy ra trần.
"""
import datetime as dt
import math

RULE_A = "A"

# τ = 3%: giá trị user chốt 2026-08-12 cho cả lớp discretionary (điểm gãy của đường đổi chác
# trong exp_ceiling_tolerance.py, job Taylor_20260812_091343). CÙNG một con số với
# discretionary_accumulation.DYNAMIC_CEILING_TAU_DEFAULT — cố ý, một chính sách một số.
RULE_A_TAU_DEFAULT = 0.03
RULE_A_TAU_MAX = 0.10

# Book có ENGINE TRẦN RIÊNG đã wire + đã được user duyệt cận trên tuyệt đối
# (`price_band.max_no_chase_ceiling`): discretionary_accumulation.resolve_price_band().
# Với book này, "Rule A" = đổi `dynamic_ceiling.sessions` 5 → 1 trong state file, KHÔNG phải
# thêm cơ chế thứ hai. Áp hai cơ chế lên cùng một lệnh là cách chắc chắn nhất để không ai
# còn truy được trần thật đến từ đâu.
BOOKS_WITH_OWN_CEILING_ENGINE = ("DISCRETIONARY_SPECIAL",)


def _pos_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x > 0


def _as_pos_float(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def _as_date(x):
    try:
        return dt.date.fromisoformat(str(x)[:10])
    except (TypeError, ValueError):
        return None


def rule_a_ceiling(anchor_price, tau=RULE_A_TAU_DEFAULT):
    """→ (ceiling_vnd | None, reason). `floor()` để trần luôn là số nguyên đồng và luôn
    làm CHẶT thêm chứ không nới (làm tròn lên sẽ cho phép trả cao hơn luật)."""
    a = _as_pos_float(anchor_price)
    if a is None:
        return None, f"anchor không hợp lệ ({anchor_price!r})"
    if not _pos_num(tau) or tau > RULE_A_TAU_MAX:
        return None, f"tau={tau!r} ngoài (0, {RULE_A_TAU_MAX}]"
    c = math.floor(a * (1.0 + tau))
    if c <= 0:
        return None, "trần tính ra ≤0"
    return float(c), f"{a:,.0f} × (1+{tau:.2%}) → {c:,}"


def resolve_buy_ceiling(order, plan_date=None):
    """Trần cứng cuối cùng cho MỘT lệnh mua → (ceiling_vnd | None, info).

    `order` = dict THÔ đọc từ plan JSON (chưa qua PlannedOrder). `plan_date` = ngày THỰC THI
    của plan (str/date), dùng cho bất biến #4; None ⇒ bỏ qua kiểm tra ngày (chỉ dùng trong
    test đơn vị, KHÔNG dùng ở đường nạp plan thật).

    Ba nhánh, theo đúng thứ tự ưu tiên:
      A. `ceiling_rule == "A"` và tái lập được ⇒ dùng trần Rule A. `entry_anchor_price` KHÔNG
         còn kẹp xuống nữa — đó chính là mục đích của Rule A (trần đóng băng ở phiên entry là
         thứ đã chặn sạch TV1 suốt 3 tuần, README §3.3).
      B. `ceiling_rule == "A"` nhưng KHÔNG tái lập được ⇒ **VỨT con số plan khai** và rơi về
         luật cũ. Không bao giờ giữ lại số đã khai: giữ lại = một plan sửa tay hỏng lại được
         hưởng trần rộng, đúng đường fail-OPEN.
      C. Không khai Rule A ⇒ luật cũ nguyên vẹn (user duyệt 2026-08-09): trần =
         min(trần generator ghi, entry_anchor_price), và giá trị rác chỉ được RƠI VỀ anchor.
    """
    info = {"rule": None, "mode": "legacy"}
    if str(order.get("side") or "").lower() != "buy":
        return None, {"rule": None, "mode": "not_a_buy"}

    declared = _as_pos_float(order.get("hard_no_chase_ceiling_vnd")) or 0.0
    anchor_entry = _as_pos_float(order.get("entry_anchor_price"))

    if str(order.get("ceiling_rule") or "").strip().upper() == RULE_A:
        info["rule"] = RULE_A
        ok, why = _verify_rule_a(order, declared, plan_date)
        if ok:
            info.update({"mode": "rule_a", "ceiling_vnd": declared,
                         "anchor_vnd": _as_pos_float(order.get("ceiling_anchor_price")),
                         "anchor_date": str(order.get("ceiling_anchor_date")),
                         "tau": _as_pos_float(order.get("ceiling_tau")),
                         "entry_anchor_price": anchor_entry, "reason": why})
            return declared, info
        info.update({"mode": "rule_a_failsafe", "reason": f"FAIL-CLOSED → luật cũ: {why}"})
        declared = 0.0          # nhánh B: vứt con số khai, không cho nó sống sót xuống dưới

    if anchor_entry:
        ceil = min(declared, anchor_entry) if declared > 0 else anchor_entry
        info.setdefault("reason", "trần = min(generator, entry_anchor_price)")
        info["ceiling_vnd"] = ceil
        return ceil, info
    info["ceiling_vnd"] = declared or None
    return (declared or None), info


def _verify_rule_a(order, declared, plan_date):
    """→ (True, mô tả) | (False, lý do). Tái lập trần từ provenance plan khai."""
    anchor = _as_pos_float(order.get("ceiling_anchor_price"))
    if anchor is None:
        return False, f"thiếu/rác ceiling_anchor_price ({order.get('ceiling_anchor_price')!r})"
    tau = _as_pos_float(order.get("ceiling_tau"))
    if tau is None or tau > RULE_A_TAU_MAX:
        return False, f"ceiling_tau={order.get('ceiling_tau')!r} ngoài (0, {RULE_A_TAU_MAX}]"
    expect, why = rule_a_ceiling(anchor, tau)
    if expect is None:
        return False, why
    if declared <= 0:
        return False, "khai ceiling_rule=A nhưng thiếu/rác hard_no_chase_ceiling_vnd"
    if abs(declared - expect) > 0.5:
        return False, (f"hard_no_chase_ceiling_vnd={declared:,.0f} KHÔNG tái lập được từ "
                       f"anchor {anchor:,.0f} × (1+{tau:.2%}) = {expect:,.0f}")
    a_date = _as_date(order.get("ceiling_anchor_date"))
    if a_date is None:
        return False, f"ceiling_anchor_date không parse được ({order.get('ceiling_anchor_date')!r})"
    if plan_date is not None:
        p_date = _as_date(plan_date)
        if p_date is None:
            return False, f"plan_date không parse được ({plan_date!r})"
        if a_date >= p_date:
            return False, (f"ceiling_anchor_date {a_date} KHÔNG nằm trước plan_date {p_date} — "
                           f"trần chỉ được neo vào phiên ĐÃ ĐÓNG (bất biến #4)")
    return True, why


def apply_rule_a(orders, anchors, tau=RULE_A_TAU_DEFAULT):
    """Gắn Rule A vào các lệnh TRONG PHẠM VI, tại chỗ. Dùng ở TẦNG LẬP PLAN, 1 lần/ngày.

    `orders`  : list dict order thô (schema plan JSON).
    `anchors` : {ticker: (anchor_price_vnd, anchor_date_iso)} — giá THÔ (`tav2_bq.ticker.Price`,
                KHÔNG phải `Close` đã điều chỉnh cổ tức) của phiên đã đóng gần nhất TRƯỚC
                `plan_date`. Caller lo việc tra; hàm này thuần tính toán nên test được không
                cần BQ/DNSE.

    PHẠM VI (đo thật trên 97 plan lịch sử, không đoán): lệnh MUA có `entry_anchor_price` —
    đúng lớp LAG entry-window (DRI/POW/SCL/SSI 08-10) mà DollarBill 08-09 phải tự chế
    workaround. BAL/CAPIT/momentum KHÔNG mang field này (0 hit) nên không bao giờ lọt vào.
    Book có engine trần riêng (DISCRETIONARY_SPECIAL) bị loại tường minh.

    → (n_applied, notes). Lệnh thiếu anchor bị BỎ QUA (giữ nguyên luật cũ), không phải lỗi.
    """
    n, notes = 0, []
    for o in orders:
        if str(o.get("side") or "").lower() != "buy":
            continue
        if not _as_pos_float(o.get("entry_anchor_price")):
            continue
        if str(o.get("book") or "") in BOOKS_WITH_OWN_CEILING_ENGINE:
            notes.append(f"{o.get('ticker')}: BỎ QUA — book {o.get('book')} có engine trần riêng")
            continue
        tk = o.get("ticker")
        got = anchors.get(tk)
        if not got:
            notes.append(f"{tk}: BỎ QUA — không tra được anchor phiên trước")
            continue
        a_px, a_date = got
        ceil, why = rule_a_ceiling(a_px, tau)
        if ceil is None:
            notes.append(f"{tk}: BỎ QUA — {why}")
            continue
        o["hard_no_chase_ceiling_vnd"] = ceil
        o["ceiling_rule"] = RULE_A
        o["ceiling_anchor_price"] = float(a_px)
        o["ceiling_anchor_date"] = str(a_date)
        o["ceiling_tau"] = float(tau)
        n += 1
        notes.append(f"{tk}: Rule A {why} (anchor {a_date}, entry_anchor "
                     f"{o.get('entry_anchor_price'):,.0f})")
    return n, notes
