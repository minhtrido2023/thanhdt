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
import math
import os
import sys

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


def verify_post_event_price(px_cum, market_price, multiplier, cash_per_share=0.0):
    """(px, evidence) nếu `market_price` THẬT SỰ ở hệ SAU sự kiện; (None, lý do) nếu không.

    PURE — không đọc file, không gọi API, không phụ thuộc TZ. Toàn bộ quyết định nằm trong bốn
    con số truyền vào, nên thông điệp trả về luôn trích được bằng chứng đã đọc (§29).

    Kiểm định: `market_price ≈ (px_cum − cash_per_share) / multiplier`. Với sự kiện làm TĂNG số
    cổ phiếu (thưởng, cổ tức bằng CP, chia tách) và KHÔNG kèm chân tiền mặt, giá tham chiếu sở
    giao dịch đúng bằng `px_cum / multiplier` (`cash_per_share=0.0`, mặc định — hành vi CŨ giữ
    nguyên 100%). Sự kiện QUYỀN MUA có thêm dòng tiền VÀO (`ref = (P_cum + r×giá_phát_hành)/
    (1+r)`) nên sẽ KHÔNG khớp và hàm này fail-closed — đúng ý: quyền mua chưa nộp tiền thì
    broker cũng chưa credit, KL không nhảy, và ca đó không được phép đi qua đây trong im lặng.

    `cash_per_share` — chân CỔ TỨC TIỀN MẶT đi CÙNG ex-date với sự kiện cổ phiếu (vd TPB
    2026-10-02: ISS 15% + DIV 500đ/cp CÙNG ngày). Công thức sở trừ chân tiền TRƯỚC khi chia hệ
    số (`trading_bot/price_frame.py::expected_reference_price` — cùng công thức, đo khớp TUYỆT
    ĐỐI HOSE/HNX 2026-08-18 n=509). Bỏ qua chân này (`cash_per_share=0.0`, hành vi trước
    2026-10-01) khiến `expected` cao hơn thật đúng `cash_per_share/multiplier` ⇒ FAIL oan mọi sự
    kiện cổ phiếu có kèm cổ tức tiền mặt cùng ngày (TPB: kỳ vọng 12.521,7 thay vì đúng 12.087,
    lệch 434,7 > dung sai) dù `marketPrice` broker HOÀN TOÀN đúng hệ quy chiếu sau sự kiện.
    Caller PHẢI nêu RÕ nguồn của `cash_per_share` trong bằng chứng của nó (§28/§29) — hàm này
    không tự suy, không mặc định khác 0 trừ khi caller đưa vào.
    """
    try:
        px_cum = float(px_cum)
        market_price = float(market_price or 0)
        multiplier = float(multiplier)
        cash_per_share = float(cash_per_share or 0)
    except (TypeError, ValueError) as e:
        return None, f"không ép được về số ({e})"
    if multiplier <= 0:
        return None, f"hệ số sự kiện {multiplier} ≤ 0 — vô nghĩa"
    if not math.isfinite(cash_per_share):
        return None, (f"cash_per_share {cash_per_share} không phải số hữu hạn (nan/inf) — §29: "
                      f"so sánh với nan luôn False nên guard < 0 phía dưới sẽ ÂM THẦM bỏ qua")
    if cash_per_share < 0:
        return None, f"cash_per_share {cash_per_share} < 0 — vô nghĩa (cổ tức tiền mặt không âm)"
    if market_price <= 0:
        return None, ("broker KHÔNG trả `marketPrice` cho mã này (0/None) ⇒ không có giá nào "
                      "CÙNG HỆ với khối lượng đã credit — không đoán")
    px_ex = px_cum - cash_per_share
    if px_ex <= 0:
        return None, (f"giá cum {px_cum:,.0f} − chân tiền mặt {cash_per_share:,.0f} = {px_ex:,.0f} "
                      f"≤ 0 — vô nghĩa, kiểm lại cash_per_share")
    expected = px_ex / multiplier
    tol = max(FRAME_TOL_VND, expected * FRAME_TOL_PCT)
    diff = market_price - expected
    cash_note = f" − chân tiền mặt {cash_per_share:,.0f}" if cash_per_share else ""
    if abs(diff) > tol:
        return None, (f"marketPrice {market_price:,.0f} KHÔNG tái tạo được giá cum "
                      f"{px_cum:,.0f}{cash_note} qua hệ số {multiplier} (kỳ vọng {expected:,.1f}, "
                      f"lệch {diff:+,.1f} > dung sai {tol:,.1f}) — hai số này KHÔNG cùng một hệ "
                      f"quy chiếu, có thể là ca DNSE điều chỉnh THEO GÓI VAY chưa xong "
                      f"(price_frame.py §G4)")
    return market_price, (f"marketPrice {market_price:,.0f} = (giá cum {px_cum:,.0f}{cash_note}) "
                          f"/ hệ số {multiplier} (kỳ vọng {expected:,.1f}, lệch {diff:+,.1f} ≤ "
                          f"dung sai {tol:,.1f})")


REGISTRY_FALLBACK_ENV = "MIKE_EXDATE_REGISTRY_FALLBACK"
_REGISTRY_CODE = {"SPLIT": "SPLIT"}        # BONUS_ISSUE/STOCK_DIVIDEND ⇒ "ISS" (mã vendor cùng loại)


def registry_fallback_enabled():
    """Công tắc lùi — MẶC ĐỊNH TẮT ("1" mới bật). Bật cần user duyệt (job Taylor_20261003_033512)."""
    return os.environ.get(REGISTRY_FALLBACK_ENV, "0").strip() == "1"


def registry_event_next_session(ticker, asof, path=None):
    """Sự kiện CONFIRMED trong `data/corp_actions.json` của `ticker` có ex_date = phiên KẾ TIẾP
    `asof`, dựng theo đúng hình dạng `upcoming_events_held` để `classify_qty_residual` kiểm.

    CHỈ dùng khi lịch vendor KHÔNG có sự kiện cho mã (feed đứng — ca TPB 2026-10-01: user đã ký
    CONFIRMED mà compute_active_nav vẫn chặn vì cổng chỉ đọc lịch vendor). KHÔNG nới cổng: phần
    dư KL vẫn phải khớp đúng hệ số (dung sai cũ), và giá vẫn phải qua `verify_post_event_price`
    ở caller. Record chưa CONFIRMED (PROPOSED/REVOKED) và record provenance=broker không bao giờ
    được trả về.

    `event_code` dùng mã VENDOR cùng loại ("ISS"/"SPLIT") chứ không phải nhãn riêng: khoá chống
    cộng-hai-lần của `discretionary_accumulation_inject` là (ticker, ex_date, event_code) — nhãn
    khác sẽ khiến cùng sự kiện bị quy đổi baseline lần 2 nếu feed vendor sống lại giữa chừng.
    """
    import datetime as _dt
    import json as _json
    import corp_actions
    from trading_bot.vn_market import next_trading_day
    path = path or corp_actions.REGISTRY
    nxt = next_trading_day(_dt.date.fromisoformat(asof)).isoformat()
    if not os.path.exists(path):                     # sổ vắng mặt = không có sự kiện (như load_all)
        return None
    # Record do CHÍNH broker suy ra (provenance=broker) KHÔNG được làm "nguồn thứ hai" cho cổng
    # này: cổng đối chiếu KL broker với một nguồn ĐỘC LẬP; broker xác nhận broker = 1 nguồn
    # (arch-review v1 M6). `validate()` bỏ khoá provenance ⇒ đọc thô để lọc theo id.
    with open(path, encoding="utf-8") as f:
        broker_ids = {r.get("id") for r in (_json.load(f).get("actions") or [])
                      if str(r.get("provenance", "")).lower() == "broker"}
    for a in corp_actions.load_corp_actions(path=path, ticker=ticker):
        if a["ex_date"] == nxt and a["id"] not in broker_ids:
            return {"ticker": a["ticker"], "date": nxt, "price_adjusting": True,
                    "event_code": _REGISTRY_CODE.get(a["event_type"], "ISS"),
                    "exercise_ratio": a["qty_multiplier"] - 1.0,
                    "cash_leg_vnd_per_share": a["cash_leg_vnd_per_share"],
                    "source": f"corp_actions.json:{a['id']}"}
    return None


def net_fills_journal_and_broker(account_label, after_date, upto_date, cache=None,
                                 missing_out=None, wc_root=None, notes_out=None):
    """Như `daily_nav_snapshot.net_fills_between` nhưng HỢP NHẤT thêm statement DNSE.

    VÌ SAO (ca thật 2026-10-21, user DUYỆT 23:53): user bán TAY DRI ngoài bot (SpaceX −1.200cp,
    ZaloPay −600cp @15.400). Journal `exec_<acc>_<date>_journal.csv` chỉ ghi lệnh CỦA BOT ⇒
    "lệnh khớp thật +0", phần dư −1.200 bị coi là KL đổi ngoài lệnh ⇒ rc=6 suốt, active_nav
    không làm mới được. Statement `dnse_khoplenh_broker_confirm_<DD-MM-YYYY>.csv` (CANONICAL cho
    fill THẬT — kb/data_registry/trading-bot/dnse_khoplenh_broker_email.md) liệt kê MỌI dòng
    khớp của tiểu khoản, kể cả lệnh đặt tay trong app.

    KHỬ TRÙNG theo (ngày, mã, chiều): `max(journal, statement)`, KHÔNG cộng. Fill của bot nằm ở
    CẢ HAI nguồn; statement ⊇ journal khi cả hai đúng ⇒ max = statement. Chiều ngược (journal >
    statement — statement thiếu dòng) thì max = journal = đúng hành vi CŨ, nên bản vá không bao giờ
    giải thích ÍT hơn và cũng không "giải thích" được gì mà không nguồn nào ghi. Lệch hai nguồn
    được ghi vào `notes_out` để thông điệp chặn nói ra, không nuốt.

    Đọc statement qua `broker_fill_confirm.load_broker_fills` (lọc ĐÚNG tiểu khoản §12, dtype=str
    cho số 0 dẫn đầu, phân biệt "account khớp 0" vs "ánh xạ hỏng") với `allow_fetch=False`: đường
    sizing không tự gọi Gmail; statement do cron leg 3 EOD (19:10) / `fetch_dnse_khoplenh_email.py`
    tải sẵn.

    `missing_out`: ngày GIAO DỊCH trong cửa sổ mà CẢ journal LẪN statement đều không dùng được —
    chỉ khi đó "lệnh khớp thật" mới là suy diễn từ vắng mặt (§28). Có statement dùng được thì ngày
    đó ĐÃ có bằng chứng đầy đủ dù journal thiếu (ca 21/10: bot không chạy, chỉ có lệnh tay).
    """
    key = (account_label, after_date, upto_date, "journal+broker")
    if cache is not None and key in cache:
        out, missing, notes = cache[key]
        if missing_out is not None:
            missing_out[:] = missing
        if notes_out is not None:
            notes_out[:] = notes
        return out
    import datetime as _dt
    import glob
    import daily_nav_snapshot as dns
    import verify_account_snapshot as vas
    from broker_fill_confirm import BrokerFills, load_broker_fills
    from trading_bot.vn_market import next_trading_day

    wc_root = wc_root or dns.WC_ROOT
    prefix, suffix = f"exec_{account_label}_", "_journal.csv"
    days = set()
    for path in glob.glob(os.path.join(vas.EXEC_DIR, prefix + "*" + suffix)):
        d = os.path.basename(path)[len(prefix):-len(suffix)]
        if after_date < d <= upto_date:
            days.add(d)
    d_, end = (next_trading_day(_dt.date.fromisoformat(after_date)),
               _dt.date.fromisoformat(upto_date))
    while d_ <= end:
        days.add(d_.isoformat())
        d_ = next_trading_day(d_)

    out, missing, notes = {}, [], []
    for d in sorted(days):
        events, jerr = vas.journal_fill_events(account_label, d)
        try:
            broker = load_broker_fills(d, account_label, wc_root, allow_fetch=False)
        except Exception as e:  # dòng statement hỏng (vd khối lượng NaN) KHÔNG được làm sập sizing
            broker = BrokerFills(False, f"statement {d} không parse được: {type(e).__name__}: {e}")
        jq = {}
        for _ts, _oid, tk, side, qty, _px in events or []:
            jq[(tk, side)] = jq.get((tk, side), 0.0) + qty
        if broker.available:
            per_day = {}
            for k in set(jq) | set(broker.by_key):
                j, b = jq.get(k, 0.0), float(broker.qty(*k))
                per_day[k] = max(j, b)
                if j > b:
                    notes.append(f"{d} {k[0]} {k[1]}: journal {j:,.0f} > statement {b:,.0f}")
                elif b > j:
                    notes.append(f"{d} {k[0]} {k[1]}: +{b - j:,.0f}cp chỉ có ở statement DNSE "
                                 f"(ngoài journal bot)")
        elif events is not None:
            per_day = jq
        else:
            missing.append(f"{d}: {jerr}; statement: {broker.reason}")
            continue
        for (tk, side), q in per_day.items():
            out[tk] = out.get(tk, 0.0) + (q if side == "buy" else -q)
    if cache is not None:
        cache[key] = (out, missing, notes)
    if missing_out is not None:
        missing_out[:] = missing
    if notes_out is not None:
        notes_out[:] = notes
    return out


def classify_positions(account_label, account_no, asof, positions, broker_statement=False):
    """Mã nào đang ở hệ SAU sự kiện trong khi giá đóng cửa còn ở hệ TRƯỚC.

    Trả `(credited, blocked)`:
      credited {tk: detail}  — KL đổi KHỚP ĐÚNG tỉ lệ sự kiện có ex-date = phiên KẾ TIẾP
                               `asof` ⇒ broker đã credit sớm, ĐÃ CHỨNG MINH. `detail` mang
                               `exercise_ratio` để caller dựng giá hệ mới.
      blocked  {tk: lý do}   — KL đổi mà LỆNH KHỚP THẬT không giải thích được và cũng không
                               khớp tỉ lệ nào. Caller PHẢI fail-closed: đây là đường sizing,
                               đoán sai ở đây là đặt lệnh sai khối lượng bằng tiền thật.

    §28/§29 — thông điệp `blocked` PHẢI mang theo trạng thái của hai kênh bằng chứng mà nó dựa
    vào, vì CẢ HAI đều fail được trong im lặng:
      · LỊCH corp-action — `_corp_action_daily_snapshot` trả `None` khi thiếu file, và producer
        fail thật (`corp_action_daily_2026-08-27_FAILED.json` còn trên đĩa). Không phân biệt thì
        "lịch KHÔNG có sự kiện nào cho mã này" là suy diễn từ SỰ VẮNG MẶT của một kênh — replay
        vòng 1 in đúng câu đó cho VHM 2026-08-05 và MBB 2026-08-11, hai ngày mà file lịch KHÔNG
        TỒN TẠI. Dùng `_corp_action_gate_status` (đã có sẵn, `daily_nav_snapshot` in nó từ vòng 2).
      · JOURNAL fill — `net_fills_between(missing_out=...)` trả danh sách ngày GIAO DỊCH mà
        journal không đọc được; thiếu nó thì "lệnh khớp thật +0" cũng là suy diễn từ vắng mặt
        (đúng lỗi đã vá ở vòng 3 của `daily_nav_snapshot`, mục [N2]).
      · `broker_statement=True` (chỉ `compute_active_nav` bật, 2026-10-21) — "lệnh khớp thật"
        hợp nhất thêm statement DNSE (`net_fills_journal_and_broker`) để lệnh BÁN/MUA TAY của user
        không bị coi là KL đổi ngoài lệnh. Ngưỡng/phân loại KHÔNG đổi: phần dư còn lại sau hợp
        nhất vẫn bị chặn y hệt. Mặc định False ⇒ caller khác giữ nguyên hành vi.

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
    ca_active, ca_note = dns._corp_action_gate_status(snap, asof)
    credited, blocked, fill_cache = {}, {}, {}
    for tk in sorted(positions):
        p = positions[tk] or {}
        qty_now = p.get("total", p.get("qty"))
        qty_prev, prev_d = dns.previous_raw_qty(account_no, tk, asof)
        if prev_d is not None and qty_prev is None:
            qty_prev = 0.0                      # [B2] bản ghi ngày trước CÓ mà vắng mã ⇒ "chưa giữ"
        journal_gaps, fill_notes = [], []
        if not prev_d:
            net_fill = None
        elif broker_statement:
            net_fill = net_fills_journal_and_broker(
                account_label, prev_d, asof, fill_cache, missing_out=journal_gaps,
                notes_out=fill_notes).get(tk)
        else:
            net_fill = dns.net_fills_between(account_label, prev_d, asof, fill_cache,
                                             missing_out=journal_gaps).get(tk)
        ev = dns.held_event_next_session(snap, asof, tk)
        if ev is None and registry_fallback_enabled():
            try:
                ev = registry_event_next_session(tk, asof)
            except Exception as e:   # registry hỏng ⇒ KHÔNG đoán, chặn đúng mã này (§29: lỗi thật)
                blocked[tk] = f"không đọc được data/corp_actions.json để tra sự kiện: {e}"
                continue
        verdict, detail = dns.classify_qty_residual(ev, qty_now, qty_prev, net_fill, prev_d)
        if verdict == "qty_unexplained" and detail["residual"] > 0:
            # N3: user nộp tiền mua quyền (lệnh tay hợp lệ) — KL tăng, giá không đổi hệ ⇒ không chặn,
            # không phải "credited" (không có gì để quy đổi giá).
            rs_ok, rs_info = dns.rights_subscription_check(account_no, tk, asof, prev_d, detail)
            if rs_ok:
                print(f"ℹ️ [{asof}] {tk}: phần dư {detail['residual']:+,.0f} = nộp tiền mua quyền "
                      f"({rs_info['event_id']}, giá {rs_info['issue_price']:,.0f}) — không chặn", file=sys.stderr)
                continue
            detail["rights_check"] = rs_info
        if verdict == "share_event_credit":
            if ev and ev.get("source"):
                detail["event_source"] = ev["source"]
                detail["cash_leg_vnd_per_share"] = ev.get("cash_leg_vnd_per_share", 0.0)
            credited[tk] = detail
        elif verdict == "qty_unexplained":
            blocked[tk] = (
                f"KL {detail['qty_prev']:,.0f}→{detail['qty_now']:,.0f} (so với "
                f"{detail['prev_qty_date']}), lệnh khớp thật {detail['net_fill']:+,.0f} ⇒ phần dư "
                f"{detail['residual']:+,.0f} CHƯA GIẢI THÍCH ĐƯỢC"
                + _calendar_clause(detail, ca_active, ca_note, asof)
                + _journal_caveat(journal_gaps, broker_statement)
                + _fill_notes_clause(fill_notes, tk)
                + (f" [không nhận là nộp tiền quyền mua: {detail['rights_check']}]"
                   if detail.get("rights_check") else ""))
    return credited, blocked


def _calendar_clause(detail, ca_active, ca_note, asof):
    """Vế "lịch nói gì" của thông điệp blocked — BA ca, không phải hai (§28/§29).

    Ca thứ ba (`ca_active is False`) chính là lỗ hổng vòng 1: lịch KHÔNG ĐỌC ĐƯỢC thì mọi mã rơi
    vào `qty_unexplained` với `ex_date=None`, và câu "lịch KHÔNG có sự kiện nào" đẩy người xử lý
    đi kiểm đúng cái không cần kiểm. Ghép `ca_note` vào MỌI ca để người đọc thấy nguồn bằng chứng
    ngay trên dòng chẩn đoán, không phải suy ra.
    """
    if detail.get("ex_date"):
        why = (f" — lịch có {detail['event_code']} ex-date {detail['ex_date']} nhưng phần dư "
               f"KHÔNG khớp tỉ lệ {detail.get('exercise_ratio')} (kỳ vọng "
               f"{detail.get('expected_residual')})")
    elif ca_active:
        why = " — lịch corp-action KHÔNG có sự kiện nào cho mã này vào phiên kế tiếp"
    else:
        why = (f" — KHÔNG ĐỌC ĐƯỢC LỊCH corp-action cho {asof} ⇒ KHÔNG kết luận được mã này "
               f"CÓ hay KHÔNG CÓ sự kiện; kiểm lịch TRƯỚC khi nghi nguyên nhân khác")
    return why + f" [lịch: {ca_note}]"


def _fill_notes_clause(notes, tk):
    """Lệch journal↔statement của ĐÚNG mã này (nếu có) — để người xử lý thấy nguồn fill nào nói gì."""
    mine = [n for n in notes if f" {tk} " in n]
    return f" [fill: {'; '.join(mine[:5])}]" if mine else ""


def _journal_caveat(gaps, broker_statement=False):
    """Vế "journal có đọc được không" — thiếu nó thì `net_fill` +0 là suy diễn, không phải số đo.

    Cắt còn 5 mục đầu vì cùng lý do §29 đã ghi ở `daily_nav_snapshot`: cửa sổ dài sinh chuỗi vài
    nghìn ký tự trên MỘT dòng stderr, không ai đọc được.
    """
    if not gaps:
        return ""
    g = sorted(set(gaps))
    head = "; ".join(g[:5])
    tail = f"; … và {len(g) - 5} ngày nữa" if len(g) > 5 else ""
    what = "journal LẪN statement DNSE" if broker_statement else "journal"
    return (f" [⚠️ {what} KHÔNG đọc được cho {len(g)} ngày GIAO DỊCH trong cửa sổ "
            f"({head}{tail}) ⇒ 'lệnh khớp thật' phía trên có thể THIẾU; kiểm journal TRƯỚC "
            f"khi nghi corp-action]")
