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
# GIỮ NGUYÊN 1,00% qua bản vá 2026-08-15 — CỐ Ý KHÔNG re-tune: đổi cơ sở giá và đổi ngưỡng
# cùng lúc thì không còn quy được thay đổi hành vi về nguyên nhân nào.
#   · CẬN DƯỚI — thứ dung sai phải DUNG NẠP: **sau bản vá, hai vế của phép so là CÙNG một
#     trường, cùng một feed, cùng một phiên** (anchor lấy `q.ref` lúc lập plan, mốc sống lấy
#     `q.ref` lúc đặt lệnh) ⇒ đúng phiên thì lệch **0,0000%**, đo 43/43 mã ngày 2026-08-15.
#     Chỉ còn phải nuốt nhiễu chéo-feed ở chân HOSE/HNX nếu caller lấy anchor từ BQ
#     `ticker.Price` thay vì DNSE (đo 2026-08-14: khớp tuyệt đối 28/29 mã; ca thứ 29 là SSI —
#     KHÔNG phải nhiễu mà là **sự kiện quyền** ex-right 08-17, đúng thứ cổng phải bắt).
#     TRƯỚC bản vá, dung sai này còn phải nuốt cả CHÊNH LỆCH ĐỊNH NGHĨA giữa "giá tham chiếu"
#     và "giá đóng cửa" trên UPCOM (median 0,36%, p90 1,27%) — nay không còn.
#   · CẬN TRÊN — phải NHỎ HƠN HẲN τ=3%: sai số x% ở cơ sở giá dịch gần 1:1 thành x% dư/thiếu
#     dư địa đuổi trên tổng ngân sách 3% mà user duyệt. 1% = 1/3 ngân sách, và vẫn nằm dưới
#     `max_chase_pct_buy`=1,5% ⇒ một sai số lọt cổng KHÔNG BAO GIỜ ăn hết trần đuổi tĩnh.
#   · Đối chiếu các ngưỡng đã có trong hệ: τ=3% (chính luật A), `chase_cap_vol_ceil`=4%,
#     `max_chase_pct_buy`=1,5%. 1% là số duy nhất nằm dưới CẢ BA mà vẫn trên nhiễu đo được.
# GIỚI HẠN ĐÃ BIẾT (công bố, không giấu): plan trễ đúng một phiên mà giá tham chiếu đi <1% qua
# đêm sẽ LỌT cổng — nhưng khi ấy sai số trần cũng <1%, tức bị chặn bởi chính cận trên ở trên.
# Cổng này chặn sai số LỚN, không hứa phát hiện mọi plan cũ.
RULE_A_REF_TOL_DEFAULT = 0.01

# 🔴 ĐÍNH CHÍNH 2026-08-15 (job Taylor_20260815_034407) — khối chú thích cũ ở đây kết luận
# NGƯỢC và đã bị gỡ. Nó nói "KHÔNG dùng `q.ref`, mốc đúng là giá ĐÓNG phiên trước", suy từ
# đúng số đo N=66 dưới đây nhưng gán nhân quả sai chiều:
#
#   Số đo (vẫn đúng): `q.ref` khớp giá đóng phiên trước TUYỆT ĐỐI ở 59/66 mã; 7 ca lệch đều
#   là UPCOM — SCL −3,376%, TMG +0,949%, TV1 −0,497% trong ngày HOÀN TOÀN BÌNH THƯỜNG.
#
#   Diễn giải cũ (SAI): "`q.ref` sai cơ sở trên UPCOM ⇒ bỏ `q.ref`, dùng giá đóng".
#   Sự thật: **`q.ref` MỚI LÀ số đúng, `giá đóng` mới là cái sai** — vì `giá tham chiếu` của
#   UPCOM theo quy chế là BÌNH QUÂN GIA QUYỀN giá khớp lô chẵn phiên trước, còn HOSE/HNX mới
#   lấy giá đóng cửa. Hai định nghĩa trùng nhau ở 2/3 sàn, nên bug ẩn được.
#
# BẰNG CHỨNG CƠ CHẾ (không phải tương quan): dựng lại bình quân gia quyền phiên 2026-08-14 từ
# bar 1 PHÚT nguồn VCI — đường dữ liệu ĐỘC LẬP HOÀN TOÀN với DNSE — rồi làm tròn về bước giá
# 100đ của UPCOM ⇒ trùng `q.ref` ở **6/7 mã TỚI TỪNG TICK** (SCL: tái lập sai lệch −3,3634%
# so với −3,3755% đo thật, sai số 0,012 điểm phần trăm). Mã còn lại lệch đúng 1 tick vì bar
# bị cắt lúc 14:50. Chi tiết + phân bố 12 tháng (N=1.618 phiên-mã: median 0,361%, p90 1,271%,
# 1,2% số phiên vượt CẢ τ=3%): `mike/agents/Taylor/research/upcom_ref_anchor_20260815/`.
#
# `q.ref` còn đúng ở một chiều nữa mà giá đóng KHÔNG BAO GIỜ đúng: **ngày giao dịch không
# hưởng quyền**. Ca thật SSI ex-right 2026-08-17 (thưởng CP 20% + cổ tức 1.000đ): tham chiếu
# chính thức (24.500−1.000)/1,2 → tick 50đ = **19.600đ** = ĐÚNG `q.ref`, trong khi giá đóng
# phiên trước là 24.500đ. Trần luật A dựng trên giá đóng = 25.235đ, **cao hơn cả GIÁ TRẦN hợp
# lệ của phiên (20.972đ)** ⇒ luật A vô hiệu hoàn toàn, im lặng. Đúng loại hỏng cơ chế này
# sinh ra để chặn.

# Cơ sở giá HỢP LỆ DUY NHẤT của anchor luật A, ghi thẳng vào provenance plan
# (`ceiling_anchor_basis`). Mục đích: plan sinh bởi bản CŨ (anchor = giá đóng cửa) KHÔNG mang
# field này ⇒ `_verify_rule_a` fail-closed về luật cũ. Bản vá tự vô hiệu hoá vintage lỗi, thay
# vì trông chờ không còn plan cũ nào — §22 coding_guidelines (luật văn xuôi → cưỡng chế bằng
# code).
ANCHOR_BASIS_OFFICIAL_REF = "official_reference_price"

# Biên độ dao động giá theo sàn — dùng làm phép kiểm TRỰC GIAO cho snapshot giá tham chiếu
# (xem `check_reference_snapshot`). Trùng `brokers.EXCHANGE_BAND_PCT`; định nghĩa lại ở đây có
# CHỦ ĐÍCH để file này giữ được tính THUẦN (không import broker ⇒ selfcheck chạy không cần
# DNSE, không rủi ro import vòng). Hai bản phải bằng nhau — khoá bằng test trong selfcheck.
EXCHANGE_BAND_PCT = {"HOSE": 0.07, "HNX": 0.10, "UPCOM": 0.15}

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


def check_reference_snapshot(ref, ceiling, floor, exchange, exchange_known,
                             prev_low=None, prev_high=None, band_tol=0.01):
    """Snapshot giá tham chiếu SỐNG có dùng làm anchor luật A được không → (ok, info).

    Hàm THUẦN (không I/O) — caller lo việc lấy `ref/ceiling/floor/exchange` từ DNSE và
    `prev_low/prev_high` từ BQ. FAIL-CLOSED mọi hướng: thiếu dữ liệu ⇒ False.

    Ba cổng, mỗi cổng bắt một cách hỏng mà hai cổng kia MÙ:

      **G1 — sàn phải XÁC ĐỊNH ĐƯỢC.** Không biết sàn thì không biết giá tham chiếu được
      tính theo công thức nào (giá đóng cửa hay bình quân gia quyền), và cũng không kiểm được
      biên độ. `Quote.exchange` mặc định "HOSE" cho mọi mã khi feed câm (bug fail-OPEN đo được
      2026-08-15) nên **phải hỏi `exchange_known`, không được hỏi `exchange`**.

      **G2 — biên độ phải khớp sàn.** `ceiling/ref − 1 ≈ +biên`, `floor/ref − 1 ≈ −biên`.
      Đây là tín hiệu TRỰC GIAO với `marketId`: nó chứng minh `ref`, `ceiling`, `floor` là MỘT
      snapshot nhất quán CỦA CÙNG MỘT PHIÊN, và ánh xạ sàn không sai. Dung sai mặc định 1%
      *tương đối trên biên độ* để nuốt việc sàn làm tròn trần/sàn về bước giá (đo thật: HOSE
      6,69–7,00%, HNX 9,77–9,80%, UPCOM 14,29–15,00% trên 43 mã).

      **G3 — tham chiếu phải nằm TRONG biên độ giá phiên trước.** Bất biến của chính công
      thức: giá đóng cửa ∈ [Low, High] hiển nhiên, và bình quân gia quyền của các giá khớp
      trong phiên cũng ∈ [Low, High] theo cấu tạo. Đây là cổng duy nhất bắt được **snapshot
      CŨ** (`ref` của phiên T−1 bị phục vụ nhầm cho phiên T). Bỏ qua khi caller không truyền
      `prev_low/prev_high` — caller có trách nhiệm nói rõ vì sao bỏ (ví dụ: ngày GDKHQ, lúc đó
      tham chiếu ĐÃ ĐIỀU CHỈNH nên nằm ngoài biên phiên trước là ĐÚNG, không phải lỗi).
    """
    info = {"ref": ref, "ceiling": ceiling, "floor": floor, "exchange": exchange,
            "exchange_known": bool(exchange_known)}
    r = _as_pos_float(ref)
    if r is None:
        info["gate"] = "G0"
        info["reason"] = f"không có giá tham chiếu sống ({ref!r})"
        return False, info

    ex = str(exchange or "").strip().upper()
    if not exchange_known or ex not in EXCHANGE_BAND_PCT:
        info["gate"] = "G1"
        info["reason"] = (f"không xác định được SÀN của mã (exchange={exchange!r}, "
                          f"known={bool(exchange_known)}) — không biết giá tham chiếu tính "
                          f"theo công thức nào ⇒ từ chối thay vì đoán")
        return False, info
    band = EXCHANGE_BAND_PCT[ex]
    info["band_expected"] = band

    for name, v, sign in (("ceiling", ceiling, +1.0), ("floor", floor, -1.0)):
        got = _as_pos_float(v)
        if got is None:
            info["gate"] = "G2"
            info["reason"] = f"thiếu giá {name} sống ({v!r}) — không kiểm chéo được biên độ"
            return False, info
        dev = got / r - 1.0
        info[f"band_{name}"] = dev
        if abs(dev - sign * band) > band * band_tol + 1e-9:
            info["gate"] = "G2"
            info["reason"] = (f"biên độ {name} đo được {dev:+.3%} không khớp biên ±{band:.0%} "
                              f"của sàn {ex} — snapshot giá tham chiếu KHÔNG nhất quán "
                              f"(sai sàn, hoặc trộn hai phiên)")
            return False, info

    lo, hi = _as_pos_float(prev_low), _as_pos_float(prev_high)
    if lo is not None and hi is not None:
        info.update({"prev_low": lo, "prev_high": hi})
        if not (lo - 1e-9 <= r <= hi + 1e-9):
            info["gate"] = "G3"
            info["reason"] = (f"giá tham chiếu {r:,.0f}đ nằm NGOÀI biên giá phiên trước "
                              f"[{lo:,.0f}; {hi:,.0f}] — bất biến của công thức bị vi phạm "
                              f"(snapshot cũ, hoặc có sự kiện quyền chưa khai)")
            return False, info

    info["gate"] = None
    info["reason"] = (f"snapshot hợp lệ: sàn {ex}, biên ±{band:.0%}, tham chiếu {r:,.0f}đ"
                      + (f" ∈ [{lo:,.0f}; {hi:,.0f}]" if lo is not None and hi is not None
                         else " (không kiểm biên phiên trước — caller đã khai lý do)"))
    return True, info


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
    # CƠ SỞ GIÁ của anchor — cổng vintage. Plan sinh bởi bản CŨ (anchor = giá đóng phiên
    # trước) không mang field này, và trên UPCOM/ngày GDKHQ thì cơ sở đó SAI (job
    # Taylor_20260815_034407). Không có cách nào phân biệt hai vintage từ con số, nên phải
    # đòi khai tường minh: thiếu ⇒ fail-closed về luật cũ, không phải suy đoán là ổn.
    basis = str(order.get("ceiling_anchor_basis") or "").strip()
    if basis != ANCHOR_BASIS_OFFICIAL_REF:
        return False, (f"ceiling_anchor_basis={basis!r} ≠ {ANCHOR_BASIS_OFFICIAL_REF!r} — "
                       f"anchor luật A PHẢI là giá tham chiếu chính thức của phiên đang chạy "
                       f"(plan vintage cũ dùng giá đóng cửa: sai trên UPCOM và mọi ngày GDKHQ)")
    ex = str(order.get("ceiling_exchange") or "").strip().upper()
    if ex not in EXCHANGE_BAND_PCT:
        return False, (f"ceiling_exchange={order.get('ceiling_exchange')!r} không thuộc "
                       f"{sorted(EXCHANGE_BAND_PCT)} — sàn quyết định công thức giá tham chiếu")
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
    `anchors` : {ticker: (anchor_price_vnd, anchor_date_iso, exchange)} — **GIÁ THAM CHIẾU
                CHÍNH THỨC của phiên `plan_date`**, không phải giá đóng phiên trước. Caller lo
                việc tra + kiểm (`check_reference_snapshot`); hàm này thuần tính toán nên test
                được không cần BQ/DNSE.
                ⚠️ ĐỔI SEMANTIC 2026-08-15 (job Taylor_20260815_034407, SỬA LỖI): trước đây
                đây là `tav2_bq.ticker.Price` phiên trước = giá đóng cửa thô. Đúng cho HOSE/HNX
                ngày thường, SAI cho UPCOM (tham chiếu là bình quân gia quyền) và SAI cho MỌI
                sàn vào ngày GDKHQ (tham chiếu đã điều chỉnh theo quyền). `anchor_date` giờ là
                ngày PHIÊN SINH RA tham chiếu (phiên đã đóng gần nhất), giữ nguyên bất biến #4.

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
        try:
            a_px, a_date, a_ex = got
        except (TypeError, ValueError):
            notes.append(f"{tk}: BỎ QUA — anchor phải là bộ 3 (giá, ngày, sàn), nhận {got!r}")
            continue
        ex = str(a_ex or "").strip().upper()
        if ex not in EXCHANGE_BAND_PCT:
            notes.append(f"{tk}: BỎ QUA — sàn {a_ex!r} không xác định, không gắn luật A "
                         f"(sàn quyết định công thức giá tham chiếu)")
            continue
        ceil, why = rule_a_ceiling(a_px, tau)
        if ceil is None:
            notes.append(f"{tk}: BỎ QUA — {why}")
            continue
        o["hard_no_chase_ceiling_vnd"] = ceil
        o["ceiling_rule"] = RULE_A
        o["ceiling_anchor_price"] = float(a_px)
        o["ceiling_anchor_date"] = str(a_date)
        o["ceiling_tau"] = float(tau)
        o["ceiling_anchor_basis"] = ANCHOR_BASIS_OFFICIAL_REF
        o["ceiling_exchange"] = ex
        n += 1
        notes.append(f"{tk}: Rule A {why} (tham chiếu {ex} phiên {a_date}, entry_anchor "
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


def check_ref_vs_live(order, live_reference_price, chase_pct,
                      tol=RULE_A_REF_TOL_DEFAULT):
    """Cổng FAIL-SAFE: cơ sở giá của lệnh luật A còn khớp phiên giao dịch SỐNG không?

    → `(ok: bool, info: dict)`. Hàm THUẦN (không I/O, không broker) — caller lo việc lấy
    `live_reference_price` từ feed sống; nhờ vậy selfcheck chạy được không cần DNSE.

    `live_reference_price` = **giá tham chiếu CHÍNH THỨC của phiên đang chạy**, đọc từ DNSE
    `q.ref` (secdef `refPrice`/`basicPrice`). Đây phải là **ĐÚNG CÙNG MỘT ĐẠI LƯỢNG** mà tầng
    lập plan đã neo vào (`ceiling_anchor_basis = official_reference_price`) — so đúng loại với
    đúng loại. `chase_pct` = trần đuổi % mà executor SẼ dùng cho chính lệnh này
    (`Executor._buy_chase_pct`), không phải hằng số tĩnh.

    ⚠️ ĐỔI MỐC 2026-08-15 (job Taylor_20260815_034407, SỬA LỖI — không phải nới cổng): mốc cũ
    là giá ĐÓNG phiên đã hoàn tất (DNSE `ohlc` 1D). Mốc đó sai cùng một lỗi với anchor cũ: nó
    KHÔNG phải giá tham chiếu trên UPCOM (bình quân gia quyền, lệch median 0,36% / p90 1,27%
    / 1,2% số phiên vượt cả τ=3%) và KHÔNG phải giá tham chiếu ở mọi ngày GDKHQ (ca SSI
    2026-08-17: 24.500 vs 19.600). Giữ mốc cũ trong khi anchor đã đổi cơ sở sẽ **chặn oan sạch
    UPCOM** — hai vế của phép so đứng trên hai định nghĩa khác nhau.

    Đổi mốc còn làm cổng CHẶT HƠN chứ không lỏng hơn: anchor và mốc sống giờ là cùng một
    trường, cùng một feed, cùng một phiên ⇒ đúng phiên thì lệch **0,0000%** (đo 43/43 mã), sai
    phiên thì lệch nguyên một bước giá. Dung sai giữ nguyên 1% (KHÔNG re-tune — số cũ đã chọn
    từ đo và vẫn nằm dưới τ=3%, `chase_cap_vol_ceil`=4%, `max_chase_pct_buy`=1,5%); nó chỉ còn
    phải nuốt nhiễu chéo-feed chứ không phải nuốt chênh lệch định nghĩa nữa.

    HAI phép kiểm, cả hai đều FAIL-CLOSED (thiếu dữ liệu ⇒ từ chối):

      **C1 — anchor còn đúng phiên.** `|ceiling_anchor_price / live_reference_price − 1| ≤ tol`.
      Đây là phát biểu chính xác của yêu cầu "ref_price khác giá live thì từ chối": trần luật
      A = `anchor × (1+τ)`, nên anchor SAI ⇒ trần sai đúng bấy nhiêu, im lặng. Bắt được: plan
      thực thi trễ phiên, sự kiện quyền, sai đơn vị (nghìn↔VND), feed vỡ.
      So với giá tham chiếu chứ KHÔNG so với giá khớp hiện tại (`q.last`) là CỐ Ý: giá khớp
      chạy suốt phiên, và luật A CHO PHÉP thị trường chạy tới +τ trên anchor — lấy `q.last`
      làm mốc sẽ chặn oan đúng cái vùng vận hành mà luật A sinh ra để phục vụ.

      **C2 — trần % theo `ref_price` không được âm thầm THAY trần luật A.** Executor tính
      `cap = ref_price × (1 + chase_pct)` rồi mới `min()` với trần cứng. Nếu `ref_price` cũ
      hơn thị trường thì `cap` tụt xuống dưới cả trần LẪN giá tham chiếu sống, lệnh nằm ở một
      mức không ai chào — luật A còn nguyên trên giấy nhưng mất sạch tác dụng, và KHÔNG có
      log nào nói điều đó. Điều kiện:
      `ref_price × (1 + chase_pct) ≥ min(trần, live_reference_price)`.
      MỘT CHIỀU có chủ đích: `ref_price` CAO hơn anchor là thiết kế hợp lệ (book
      DISCRETIONARY_SPECIAL cố ý kéo `resting_limit` lên cùng tỉ lệ với trần đúng để tránh
      cái bẫy này) và vô hại vì trần cứng vẫn kẹp phía trên.

    `info` luôn mang đủ số để người đọc log tái lập kết luận mà không phải chạy lại gì.
    """
    info = {"live_reference_price": live_reference_price, "tol": tol, "chase_pct": chase_pct,
            "ticker": getattr(order, "ticker", None)}
    live = _as_pos_float(live_reference_price)
    if live is None:
        info["reason"] = (f"KHÔNG lấy được giá tham chiếu phiên đang chạy từ feed sống "
                          f"({live_reference_price!r}) — không đối soát được cơ sở giá")
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
        info["reason"] = (f"anchor luật A {anchor:,.0f}đ lệch {dev:+.2%} so với GIÁ THAM CHIẾU "
                          f"phiên đang chạy trên feed sống {live:,.0f}đ (dung sai ±{tol:.2%}) — "
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
