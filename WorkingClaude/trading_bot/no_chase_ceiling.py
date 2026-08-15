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

# Dung sai của cổng đối soát CƠ SỞ GIÁ tại thời điểm ĐẶT LỆNH (xem `check_ref_vs_live`).
# CHỌN TỪ SỐ ĐO THẬT, không phải số tròn cho đẹp (probe 2026-08-15, N=66 mã trên feed DNSE
# sống + BQ `ticker.Price`, script `mike/agents/Taylor/research/rule_a_ref_guard_20260815/
# probe_ref_vs_close.py`, dữ liệu thô `ref_vs_close_probe.json`):
#   · CẬN DƯỚI — thứ dung sai phải DUNG NẠP: nhiễu chéo-feed giữa cơ sở giá của anchor
#     (BQ `ticker.Price`) và giá đóng phiên đã hoàn tất trên DNSE `ohlc` 1D. Đo 29 mã cùng
#     ngày 2026-08-14: **28/29 khớp TUYỆT ĐỐI tới từng đồng**; ca còn lại (SSI) lệch −20%,
#     tức KHÔNG phải nhiễu mà là feed hỏng thật — đúng thứ cổng này phải bắt. Nhiễu cấu trúc
#     duy nhất còn lại là độ phân giải 10đ của payload `ohlc` ⇒ ≤0,10% ở mã 10.000đ,
#     ≤1,00% ở mã 1.000đ (sàn thanh khoản ADV3T 2 tỷ khiến mã dưới 2.000đ gần như không có
#     trong sổ, nhưng 1% vẫn phủ trọn cả ca đó).
#   · CẬN TRÊN — phải NHỎ HƠN HẲN τ=3%: sai số x% ở cơ sở giá dịch gần 1:1 thành x% dư/thiếu
#     dư địa đuổi trên tổng ngân sách 3% mà user duyệt. 1% = 1/3 ngân sách, và vẫn nằm dưới
#     `max_chase_pct_buy`=1,5% ⇒ một sai số lọt cổng KHÔNG BAO GIỜ ăn hết trần đuổi tĩnh.
#   · Đối chiếu các ngưỡng đã có trong hệ: τ=3% (chính luật A), `chase_cap_vol_ceil`=4%,
#     `max_chase_pct_buy`=1,5%. 1% là số duy nhất nằm dưới CẢ BA mà vẫn trên nhiễu đo được.
# GIỚI HẠN ĐÃ BIẾT (công bố, không giấu): plan trễ đúng một phiên mà mã đó đi <1% qua đêm sẽ
# LỌT cổng — nhưng khi ấy sai số trần cũng <1%, tức bị chặn bởi chính cận trên ở trên. Cổng
# này chặn sai số LỚN, không hứa phát hiện mọi plan cũ.
RULE_A_REF_TOL_DEFAULT = 0.01

# ⚠️ KHÔNG dùng `q.ref` (secdef `basicPrice`) làm mốc sống để so với anchor. Đã đo và BÁC BỎ
# 2026-08-15 trên cùng N=66: với mã HOSE thì `q.ref` == giá đóng phiên trước tuyệt đối
# (59/66 lệch đúng 0,000%), NHƯNG với UPCOM (biên ±15% — TV1/DRI/SCL/SGP/TMG/QNS/ACV) giá
# tham chiếu phiên là BÌNH QUÂN GIA QUYỀN phiên trước chứ không phải giá đóng: SCL lệch
# −3,376%, TMG +0,949%, TV1 −0,497% trong một ngày HOÀN TOÀN BÌNH THƯỜNG (SCL 08-14
# o=23,0 h=24,0 l=22,4 c=23,7 ⇒ bình quân ~22,9 là hợp lý, không có sự kiện quyền nào).
# Mà TV1/DRI/SCL đều là mã ĐANG trong sổ. Dùng `q.ref` thì mọi dung sai đủ chặt để bắt plan
# cũ (≤1%) sẽ chặn oan sạch UPCOM, còn dung sai đủ rộng cho UPCOM (>3,4%) thì to hơn cả τ=3%
# ⇒ vô dụng. Mốc ĐÚNG là giá ĐÓNG phiên đã hoàn tất, CÙNG CƠ SỞ với anchor.

# Book có ENGINE TRẦN RIÊNG đã wire + đã được user duyệt cận trên tuyệt đối
# (`price_band.max_no_chase_ceiling`): discretionary_accumulation.resolve_price_band().
# Với book này, luật A được bật TRONG CHÍNH ENGINE ĐÓ (`dynamic_ceiling.ceiling_rule = "A"`,
# user chốt 2026-08-15) và engine đó gọi ngược `rule_a_ceiling()` ở file này — một chính sách,
# một chỗ tính công thức. `apply_rule_a()` vẫn LOẠI book này: áp hai cơ chế lên cùng một lệnh
# là cách chắc chắn nhất để không ai còn truy được trần thật đến từ đâu.
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


# --------------------------------------------------------- cổng đối soát lúc ĐẶT LỆNH (V2)

def rule_a_in_force(order):
    """True khi lệnh này THỰC SỰ đang chạy dưới luật A ở tầng executor.

    Không đủ nếu chỉ `ceiling_rule == "A"`: `load_plan()` fail-closed về LUẬT CŨ khi provenance
    hỏng nhưng KHÔNG xoá nhãn `ceiling_rule` khỏi `PlannedOrder` (nó là field hợp lệ của
    dataclass). Lệnh như vậy đang chạy trần LUẬT CŨ — áp cổng luật A lên nó là chặn oan một
    hành vi nằm ngoài phạm vi thay đổi này. Điều kiện đúng = trần ĐANG hiệu lực tái lập được
    từ đúng provenance đã khai, tức chính bất biến #3.
    """
    if str(getattr(order, "side", "") or "").lower() != "buy":
        return False
    if str(getattr(order, "ceiling_rule", "") or "").strip().upper() != RULE_A:
        return False
    declared = _as_pos_float(getattr(order, "hard_no_chase_ceiling_vnd", None))
    anchor = _as_pos_float(getattr(order, "ceiling_anchor_price", None))
    tau = _as_pos_float(getattr(order, "ceiling_tau", None))
    if declared is None or anchor is None or tau is None:
        return False
    expect, _ = rule_a_ceiling(anchor, tau)
    return expect is not None and abs(declared - expect) <= 0.5


def check_ref_vs_live(order, live_prev_close, chase_pct,
                      tol=RULE_A_REF_TOL_DEFAULT):
    """Cổng FAIL-SAFE: cơ sở giá của lệnh luật A còn khớp phiên giao dịch SỐNG không?

    → `(ok: bool, info: dict)`. Hàm THUẦN (không I/O, không broker) — caller lo việc lấy
    `live_prev_close` từ feed sống; nhờ vậy selfcheck chạy được không cần DNSE.

    `live_prev_close` = giá ĐÓNG của phiên ĐÃ HOÀN TẤT gần nhất, lấy từ FEED SỐNG (DNSE
    `ohlc` 1D). **KHÔNG được lấy từ BigQuery** (§6 coding_guidelines: BQ sync 23:45 nên luôn
    trễ ≥1 phiên) và **KHÔNG được lấy `q.ref`** (xem khối chú thích ở đầu file — sai cơ sở
    trên UPCOM). `chase_pct` = trần đuổi % mà executor SẼ dùng cho chính lệnh này
    (`Executor._buy_chase_pct`), không phải hằng số tĩnh.

    HAI phép kiểm, cả hai đều FAIL-CLOSED (thiếu dữ liệu ⇒ từ chối):

      **C1 — anchor còn đúng phiên.** `|ceiling_anchor_price / live_prev_close − 1| ≤ tol`.
      Đây là phát biểu chính xác của yêu cầu "ref_price khác giá live thì từ chối": trần luật
      A = `anchor × (1+τ)`, nên anchor SAI ⇒ trần sai đúng bấy nhiêu, im lặng. Bắt được: plan
      thực thi trễ phiên, sự kiện quyền (điều chỉnh giá tham chiếu), sai đơn vị (nghìn↔VND),
      feed vỡ (ca SSI đo được 2026-08-15: BQ 24.500 vs DNSE 19.580).
      So với `live_prev_close` chứ KHÔNG so với giá khớp hiện tại (`q.last`) là CỐ Ý: giá
      khớp chạy suốt phiên, và luật A CHO PHÉP thị trường chạy tới +τ trên anchor — lấy
      `q.last` làm mốc sẽ chặn oan đúng cái vùng vận hành mà luật A sinh ra để phục vụ.

      **C2 — trần % theo `ref_price` không được âm thầm THAY trần luật A.** Executor tính
      `cap = ref_price × (1 + chase_pct)` rồi mới `min()` với trần cứng. Nếu `ref_price` cũ
      hơn thị trường thì `cap` tụt xuống dưới cả trần LẪN giá tham chiếu sống, lệnh nằm ở một
      mức không ai chào — luật A còn nguyên trên giấy nhưng mất sạch tác dụng, và KHÔNG có
      log nào nói điều đó. Điều kiện: `ref_price × (1 + chase_pct) ≥ min(trần, live_prev_close)`.
      MỘT CHIỀU có chủ đích: `ref_price` CAO hơn anchor là thiết kế hợp lệ (book
      DISCRETIONARY_SPECIAL cố ý kéo `resting_limit` lên cùng tỉ lệ với trần đúng để tránh
      cái bẫy này) và vô hại vì trần cứng vẫn kẹp phía trên.

    `info` luôn mang đủ số để người đọc log tái lập kết luận mà không phải chạy lại gì.
    """
    info = {"live_prev_close": live_prev_close, "tol": tol, "chase_pct": chase_pct,
            "ticker": getattr(order, "ticker", None)}
    live = _as_pos_float(live_prev_close)
    if live is None:
        info["reason"] = (f"KHÔNG lấy được giá đóng phiên trước từ feed sống "
                          f"({live_prev_close!r}) — không đối soát được cơ sở giá")
        info["check"] = "live_unavailable"
        return False, info

    anchor = _as_pos_float(getattr(order, "ceiling_anchor_price", None))
    if anchor is None:
        info["reason"] = "lệnh khai luật A nhưng thiếu/rác ceiling_anchor_price"
        info["check"] = "C1"
        return False, info
    dev = anchor / live - 1.0
    info.update({"anchor_vnd": anchor, "anchor_dev": dev,
                 "anchor_date": str(getattr(order, "ceiling_anchor_date", None))})
    if abs(dev) > tol:
        info["check"] = "C1"
        info["reason"] = (f"anchor luật A {anchor:,.0f}đ lệch {dev:+.2%} so với giá đóng phiên "
                          f"đã hoàn tất trên feed sống {live:,.0f}đ (dung sai ±{tol:.2%}) — "
                          f"cơ sở giá của trần KHÔNG còn mô tả phiên hiện tại")
        return False, info

    ref = _as_pos_float(getattr(order, "ref_price", None))
    ceiling = _as_pos_float(getattr(order, "hard_no_chase_ceiling_vnd", None))
    chase = chase_pct if _pos_num(chase_pct) else None
    if ref is None or ceiling is None or chase is None:
        info["check"] = "C2"
        info["reason"] = (f"thiếu dữ liệu để kiểm trần đuổi (ref_price={ref!r}, "
                          f"trần={ceiling!r}, chase_pct={chase_pct!r})")
        return False, info
    cap_chase = ref * (1.0 + chase)
    need = min(ceiling, live)
    info.update({"ref_price": ref, "ceiling_vnd": ceiling,
                 "cap_from_ref_price": cap_chase, "cap_required_at_least": need})
    if cap_chase < need:
        info["check"] = "C2"
        info["reason"] = (f"trần đuổi suy từ ref_price ({ref:,.0f} × (1+{chase:.2%}) = "
                          f"{cap_chase:,.0f}đ) THẤP HƠN mức tối thiểu {need:,.0f}đ "
                          f"(= min(trần luật A {ceiling:,.0f}, tham chiếu sống {live:,.0f})) — "
                          f"ref_price đã cũ, trần luật A không còn là ràng buộc quyết định")
        return False, info

    info["check"] = "OK"
    info["reason"] = (f"anchor {anchor:,.0f} lệch {dev:+.2%} vs phiên trước {live:,.0f} "
                      f"(≤{tol:.2%}); trần đuổi từ ref {cap_chase:,.0f} ≥ {need:,.0f}")
    return True, info
