#!/usr/bin/env python3
"""exdate_frame.py — "khối lượng của ai thì giá của người đó", cho cửa sổ ĐÊM TRƯỚC GDKHQ.

VẤN ĐỀ (đo thật 2026-09-23, VPB ISS tỉ lệ 0,2604104, ex-date 24/09). Tối T-1, DNSE credit
số cổ phiếu MỚI vào `positions.openQuantity` (SpaceX 1.100→1.386) và đồng thời hạ
`positions.marketPrice` về giá tham chiếu sau sự kiện (28.000→22.050). Nhưng giá ĐÓNG CỬA
phiên T-1 (`dnse_close_prices`, board G1) vẫn là 27.800 — và ĐÓ LÀ ĐÚNG: hôm nay mã vẫn
giao dịch có quyền. Hai con số đều đúng, ở HAI HỆ QUY CHIẾU khác nhau. Nhân chéo:

    (a) TRƯỚC sự kiện, tự nhất quán:  1.100 × 27.800 = 30.580.000
    (b) SAU   sự kiện, tự nhất quán:  1.386 × 22.050 = 30.561.300   ← vị thế THẬT từ phiên mai
    (c) TRỘN (lỗi đã xảy ra):         1.386 × 27.800 = 38.530.800   ⇒ PHỒNG 7.969.500đ

Đây đúng lớp lỗi mà `trading_bot/price_frame.py` đã đóng ở tầng ĐẶT LỆNH ("đừng đi tìm nguồn
giá đúng — hãy cưỡng chế MỘT hệ quy chiếu duy nhất"); module này đóng nó ở tầng ĐỊNH GIÁ VỊ
THẾ (`compute_active_nav.py` = mẫu số sizing, `park_holdings.py` = mẫu số PARK_TRIM).

CHỌN (b) CHỨ KHÔNG PHẢI (a). Hai consumer đều định cỡ LỆNH CỦA PHIÊN MAI, mà từ phiên mai vị
thế thật là 1.386cp ở giá đã điều chỉnh. (a) đúng cho hôm nay nhưng sai cho ngày dùng số.

KHÔNG phải "đổi nguồn giá sang marketPrice". `resolve_close_prices`/`dnse_close_prices` giữ
NGUYÊN vai trò nguồn giá chính — `marketPrice` KHÔNG phải giá đóng cửa ATC và đã sai thật
(SCL 2026-08-28: marketPrice đứng im 27.600 trong khi phiên đóng 27.800). Module này chỉ
thay giá cho ĐÚNG những mã có bằng chứng broker đã credit sớm, và chỉ sau khi ĐỐI SOÁT.

VÌ SAO PHẢI ĐỐI SOÁT chứ không tin thẳng `marketPrice`: `price_frame.py` §G4 đo được DNSE
điều chỉnh **theo TỪNG GÓI VAY và KHÔNG NGUYÊN TỬ** — một bản đọc positions của BID
2026-08-14 mang đồng thời marketPrice 35.800 (đã điều chỉnh) và 38.850 (chưa).
`DNSEBroker.get_positions()` cộng gộp lô rồi giữ "marketPrice mới nhất khác None" ⇒ nhìn từ
đó bản đọc hỏng đó trông hoàn toàn lành. Nên ở đây `marketPrice` chỉ được dùng khi nó TÁI
TẠO ĐƯỢC giá cum đã biết qua chính hệ số sự kiện — bằng chứng cơ khí, §29.
"""

# Sai số cho phép giữa `marketPrice` broker và giá tham chiếu tự dựng `px_cum / multiplier`.
# Hai nguồn sai số, cả hai đều NHỎ và có cận trên cơ khí:
#   · làm tròn theo BƯỚC GIÁ: sở làm tròn TERP về tick, broker có thể làm tròn lệch thêm một
#     bước ⇒ ≤ 2 tick. Tick lớn nhất trong mọi bảng (UPCOM/HNX) = 100đ ⇒ 200đ phủ hết.
#   · độ chính xác của `qty_multiplier`/`exercise_ratio`: vendor ghi 7 chữ số thập phân ⇒
#     đóng góp cỡ 1e-5 tương đối, bỏ qua được.
# 0,5% là sàn tương đối cho mã giá cao (VNM/SAB: 2 tick = 200đ < 0,5%). KHÔNG nới thêm: nới
# tới ~5% là bắt đầu "giải thích" được cả một cú lệch hệ quy chiếu thật của sự kiện tỉ lệ nhỏ.
FRAME_TOL_VND = 200.0
FRAME_TOL_PCT = 0.005


def verify_post_event_price(px_cum, market_price, multiplier):
    """(px, evidence) nếu `market_price` THẬT SỰ ở hệ SAU sự kiện; (None, lý do) nếu không.

    PURE — không đọc file, không gọi API, không phụ thuộc TZ. Toàn bộ quyết định nằm trong ba
    con số truyền vào, nên thông điệp trả về luôn trích được bằng chứng đã đọc (§29).

    Kiểm định: `market_price ≈ px_cum / multiplier`. Với sự kiện làm TĂNG số cổ phiếu (thưởng,
    cổ tức bằng CP, chia tách) giá tham chiếu sở giao dịch đúng bằng thương đó. Sự kiện QUYỀN
    MUA có thêm dòng tiền vào (`ref = (P_cum + r×giá_phát_hành)/(1+r)`) nên sẽ KHÔNG khớp và
    hàm này fail-closed — đúng ý: quyền mua chưa nộp tiền thì broker cũng chưa credit, KL
    không nhảy, và ca đó không được phép đi qua đây trong im lặng.
    """
    try:
        px_cum = float(px_cum)
        market_price = float(market_price or 0)
        multiplier = float(multiplier)
    except (TypeError, ValueError) as e:
        return None, f"không ép được về số ({e})"
    if multiplier <= 0:
        return None, f"hệ số sự kiện {multiplier} ≤ 0 — vô nghĩa"
    if market_price <= 0:
        return None, ("broker KHÔNG trả `marketPrice` cho mã này (0/None) ⇒ không có giá nào "
                      "CÙNG HỆ với khối lượng đã credit — không đoán")
    expected = px_cum / multiplier
    tol = max(FRAME_TOL_VND, expected * FRAME_TOL_PCT)
    diff = market_price - expected
    if abs(diff) > tol:
        return None, (f"marketPrice {market_price:,.0f} KHÔNG tái tạo được giá cum "
                      f"{px_cum:,.0f} qua hệ số {multiplier} (kỳ vọng {expected:,.1f}, lệch "
                      f"{diff:+,.1f} > dung sai {tol:,.1f}) — hai số này KHÔNG cùng một hệ quy "
                      f"chiếu, có thể là ca DNSE điều chỉnh THEO GÓI VAY chưa xong "
                      f"(price_frame.py §G4)")
    return market_price, (f"marketPrice {market_price:,.0f} = giá cum {px_cum:,.0f} / hệ số "
                          f"{multiplier} (kỳ vọng {expected:,.1f}, lệch {diff:+,.1f} ≤ dung sai "
                          f"{tol:,.1f})")


def classify_positions(account_label, account_no, asof, positions):
    """Mã nào đang ở hệ SAU sự kiện trong khi giá đóng cửa còn ở hệ TRƯỚC.

    Trả `(credited, blocked)`:
      credited {tk: detail}  — KL đổi KHỚP ĐÚNG tỉ lệ sự kiện có ex-date = phiên KẾ TIẾP
                               `asof` ⇒ broker đã credit sớm, ĐÃ CHỨNG MINH. `detail` mang
                               `exercise_ratio` để caller dựng giá hệ mới.
      blocked  {tk: lý do}   — KL đổi mà LỆNH KHỚP THẬT không giải thích được và cũng không
                               khớp tỉ lệ nào. Caller PHẢI fail-closed: đây là đường sizing,
                               đoán sai ở đây là đặt lệnh sai khối lượng bằng tiền thật.

    TÁI DÙNG NGUYÊN `daily_nav_snapshot.classify_qty_residual` và bộ plumbing quanh nó
    (`_corp_action_daily_snapshot` / `held_event_next_session` / `previous_raw_qty` /
    `net_fills_between`) — hàm đó đã qua 5 vòng arch-review và đã đo trên 104 cặp phiên của cả
    2 account: 12 phần dư, 12/12 là corp-action thật, 0 nhiễu. Viết lại phép phân loại ở đây
    là nhân đôi rủi ro, không phải nhân đôi bảo vệ.

    ⚠️ `import daily_nav_snapshot` đặt `os.environ["TZ"]="Asia/Ho_Chi_Minh"` + `tzset()` ở
    module level. Vô hại cho hai caller hiện tại (cả hai neo ngày bằng `today_ict()`, không
    đọc TZ host) nhưng là side-effect THẬT — selfcheck chạy dưới `env -u TZ` và một TZ lạ để
    chứng minh kết quả không đổi, thay vì giả định.

    `positions` = {tk: {"total"/"qty": n, ...}} — chấp cả hai tên khoá vì `DNSEBroker.
    get_positions()` dùng `total` còn `park_holdings.read_broker_snapshot` dùng `qty`.
    """
    import daily_nav_snapshot as dns

    snap = dns._corp_action_daily_snapshot(asof)
    credited, blocked, fill_cache = {}, {}, {}
    for tk in sorted(positions):
        p = positions[tk] or {}
        qty_now = p.get("total", p.get("qty"))
        qty_prev, prev_d = dns.previous_raw_qty(account_no, tk, asof)
        if prev_d is not None and qty_prev is None:
            qty_prev = 0.0                      # [B2] bản ghi ngày trước CÓ mà vắng mã ⇒ "chưa giữ"
        net_fill = (dns.net_fills_between(account_label, prev_d, asof, fill_cache).get(tk)
                    if prev_d else None)
        ev = dns.held_event_next_session(snap, asof, tk)
        verdict, detail = dns.classify_qty_residual(ev, qty_now, qty_prev, net_fill, prev_d)
        if verdict == "share_event_credit":
            credited[tk] = detail
        elif verdict == "qty_unexplained":
            blocked[tk] = (
                f"KL {detail['qty_prev']:,.0f}→{detail['qty_now']:,.0f} (so với "
                f"{detail['prev_qty_date']}), lệnh khớp thật {detail['net_fill']:+,.0f} ⇒ phần dư "
                f"{detail['residual']:+,.0f} CHƯA GIẢI THÍCH ĐƯỢC"
                + (f" — lịch có {detail['event_code']} ex-date {detail['ex_date']} nhưng phần dư "
                   f"KHÔNG khớp tỉ lệ {detail.get('exercise_ratio')} (kỳ vọng "
                   f"{detail.get('expected_residual')})" if detail.get("ex_date")
                   else " — lịch corp-action KHÔNG có sự kiện nào cho mã này vào phiên kế tiếp"))
    return credited, blocked
