#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck HERMETIC cho nav_exdate_forecast.py — không đọc BQ, không gọi broker, không ping
Discord thật (`notify`/`bus` bị monkeypatch ở test dùng chúng). Chạy:

    python3 mike/bin/nav_exdate_forecast_selfcheck.py
    env -u TZ python3 mike/bin/nav_exdate_forecast_selfcheck.py     # §16/§19: không tin TZ host
    TZ=America/New_York python3 mike/bin/nav_exdate_forecast_selfcheck.py

Không có mutation bắn vào `cum_dividend_double_count` ở đây — file này KHÔNG chạm hàm đó (đó là
việc L2/L3 riêng, xem `daily_nav_snapshot.py`). Mutation ở đây nhắm vào chính 2 quyết định mà
`nav_exdate_forecast.py` đưa ra: (a) phân loại CASH_DIV/SHARE_EVENT/INFO, (b) cửa sổ
`days_ahead<=N` — sai 1 trong 2 cái này là quay lại đúng lớp lỗi "dữ liệu có sẵn nhưng không ai
đọc kịp" mà file này tồn tại để chặn.
"""
import json
import os
import sys
import tempfile

MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
if MIKE_BIN not in sys.path:
    sys.path.insert(0, MIKE_BIN)

import nav_exdate_forecast as m  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name if not detail else f"{name} — {detail}")


DRI_DIV = {"ticker": "DRI", "date": "2026-09-22", "date_field": "exright_date",
           "event_code": "DIV", "event_status": "announced", "days_ahead": 1,
           "price_adjusting": True, "value_per_share": "1000.0", "exercise_ratio": "0.1",
           "issue_method_vi": None, "title": "Trả cổ tức bằng tiền mặt"}

VPB_ISS = {"ticker": "VPB", "date": "2026-09-24", "date_field": "exright_date",
           "event_code": "ISS", "event_status": "announced", "days_ahead": 1,
           "price_adjusting": True, "value_per_share": None, "exercise_ratio": "0.2604104",
           "issue_method_vi": "Trả Cổ tức bằng Cổ phiếu",
           "title": "Phát hành cổ phiếu tỉ lệ 26.0%"}

VIX_AIS = {"ticker": "VIX", "date": "2026-09-28", "date_field": "effective_date",
           "event_code": "AIS", "event_status": "announced", "days_ahead": 0,
           "price_adjusting": False, "value_per_share": None, "exercise_ratio": None,
           "issue_method_vi": None, "title": "Niêm yết bổ sung"}

POSITIONS = {"SpaceX": {"DRI": {"qty": 3700, "price": 14900.0},
                        "VPB": {"qty": 1100, "price": 34000.0}},
             "ZaloPay": {"DRI": {"qty": 1900, "price": 14900.0},
                        "VPB": {"qty": 1300, "price": 34000.0}}}


# ── 1. classify() ────────────────────────────────────────────────────────────
check("classify DIV price_adjusting → CASH_DIV", m.classify(DRI_DIV) == "CASH_DIV")
check("classify ISS price_adjusting → SHARE_EVENT", m.classify(VPB_ISS) == "SHARE_EVENT")
check("classify price_adjusting=False → INFO", m.classify(VIX_AIS) == "INFO")
# mutation: DIV nhưng price_adjusting False (VD cổ tức đã huỷ/điều chỉnh) phải KHÔNG rơi vào CASH_DIV
_div_not_adj = {**DRI_DIV, "price_adjusting": False}
check("mutation: DIV+price_adjusting=False → INFO (không phải CASH_DIV)",
      m.classify(_div_not_adj) == "INFO")

# ── 2. relevant_events() cửa sổ PHIÊN GIAO DỊCH (không phải days_ahead lịch) ─
# asof = 2026-09-22 (thứ Ba) — next_trading_day = 2026-09-23 (thứ Tư, xác nhận bằng
# trading_bot.vn_market.next_trading_day thật, không đoán). Events đặt date SÁT với window
# thật để bài test phản ánh đúng cách relevant_events() vận hành trên dữ liệu thật, không phải
# field days_ahead tự khai (đã CHỦ ĐỘNG bỏ dùng field đó — xem lý do ở docstring trading_day_window).
ASOF = "2026-09-22"
DRI_TODAY = {**DRI_DIV, "date": ASOF}                       # HÔM NAY — luôn trong cửa sổ
VPB_NEXT_SESSION = {**VPB_ISS, "date": "2026-09-23"}        # đúng 1 PHIÊN kế tiếp — phải lọt
FAR_2_SESSIONS = {**VPB_ISS, "ticker": "FAR", "date": "2026-09-24"}  # 2 phiên kế tiếp — phải bị loại
snap = {"feed_status": "FRESH", "upcoming_events_held": [DRI_TODAY, VPB_NEXT_SESSION, FAR_2_SESSIONS]}
ev1 = m.relevant_events(snap, ASOF, days_ahead_max=1)
check("trading-day window<=1: giữ DRI (hôm nay) + VPB (1 phiên sau), loại FAR (2 phiên sau)",
      {e["ticker"] for e in ev1} == {"DRI", "VPB"}, sorted(e["ticker"] for e in ev1))
ev0 = m.relevant_events(snap, ASOF, days_ahead_max=0)
check("window<=0 chỉ giữ sự kiện ĐÚNG hôm nay (DRI)",
      {e["ticker"] for e in ev0} == {"DRI"}, sorted(e["ticker"] for e in ev0))
check("days_ahead_max âm → chỉ còn đúng hôm nay (range() rỗng, không mở rộng cửa sổ)",
      {e["ticker"] for e in m.relevant_events(snap, ASOF, days_ahead_max=-1)} == {"DRI"})
check("snapshot rỗng/None → rỗng, không crash", m.relevant_events(None, ASOF) == [])
check("thiếu key upcoming_events_held → rỗng, không crash", m.relevant_events({}, ASOF) == [])

# MUTATION/REGRESSION quan trọng nhất của bản vá này — bug thật đã đo: BID ex-date 2026-08-17
# là thứ Hai; asof thứ Sáu 2026-08-14 lọc bằng days_ahead<=1 (lịch) sẽ BỎ SÓT vì days_ahead=3.
# Cửa sổ theo PHIÊN phải bắt được: next_trading_day(2026-08-14 thứ Sáu) == 2026-08-17 thứ Hai.
bid_monday = {**DRI_DIV, "ticker": "BID", "date": "2026-08-17"}
snap_fri = {"upcoming_events_held": [bid_monday]}
ev_fri = m.relevant_events(snap_fri, "2026-08-14", days_ahead_max=1)
check("REGRESSION BID: thứ Sáu 08-14 vẫn bắt được ex-date thứ Hai 08-17 (1 PHIÊN, 3 ngày lịch)",
      {e["ticker"] for e in ev_fri} == {"BID"}, sorted(e["ticker"] for e in ev_fri))
# và ngày lịch<=1 tính từ thứ Sáu (thứ Bảy) thì KHÔNG được lọt (window chỉ gồm 2 phiên: 08-14, 08-17)
bid_saturday_calendar = {**DRI_DIV, "ticker": "SATFAKE", "date": "2026-08-15"}
ev_fri2 = m.relevant_events({"upcoming_events_held": [bid_saturday_calendar]}, "2026-08-14", days_ahead_max=1)
check("thứ Bảy 08-15 (không phải phiên giao dịch) không nằm trong cửa sổ 2 phiên → rỗng",
      ev_fri2 == [], ev_fri2)

# ── 3. build_event_line() — số học phải khớp tay ────────────────────────────
# asof=ASOF luôn truyền TƯỜNG MINH — không dựa vào today_ict() thật (tránh false-pass tình cờ
# khi selfcheck chạy đúng ngày ASOF, và không lệ thuộc TZ host, §16/§19).
line_dri = m.build_event_line(DRI_DIV, POSITIONS, asof=ASOF)
check("DRI: có % giá (~6.71%)", "6.71%" in line_dri, line_dri)
check("DRI: nêu đúng cả 2 account giữ", "SpaceX 3,700cp" in line_dri and "ZaloPay 1,900cp" in line_dri)
check("DRI: gắn nhãn KỲ VỌNG không phải lỗi", "KHÔNG PHẢI LỖI".lower() in line_dri.lower()
      or "kỳ vọng" in line_dri.lower())
check("DRI (date==asof) → day_word 'HÔM NAY'", "HÔM NAY" in line_dri, line_dri)
# V1 REGRESSION — nhánh CASH_DIV phải dùng adjust_clause thật, KHÔNG hardcode "Tối nay/mai" cho
# ca đã diễn ra hôm nay (broker đã hạ giá đêm TRƯỚC hôm nay, không phải "sắp" hạ).
check("V1 REGRESSION: DRI hôm nay KHÔNG chứa 'Tối nay/mai' (đã điều chỉnh từ đêm trước)",
      "Tối nay/mai" not in line_dri, line_dri)

_dri_2_sessions = {**DRI_DIV, "date": "2026-09-24"}  # cách ASOF 2 phiên, giống VPB_ISS
line_dri_2s = m.build_event_line(_dri_2_sessions, POSITIONS, asof=ASOF)
check("V1 REGRESSION: DIV cách 2 phiên nêu đúng 'đêm trước phiên 2026-09-24' qua adjust_clause",
      "đêm trước phiên 2026-09-24" in line_dri_2s and "Tối nay/mai" not in line_dri_2s, line_dri_2s)
# V5 REGRESSION — CASH_DIV KHÔNG được khẳng định broker đổi KL (chỉ đổi giá tham chiếu); vòng 4
# gộp chung _adjust_clause cho cả 2 lớp sự kiện khiến dòng cổ tức tiền mặt nói sai "đổi giá/KL".
check("V5 REGRESSION: adjust_clause của CASH_DIV KHÔNG chứa 'KL' (broker chỉ đổi giá)",
      "KL" not in line_dri_2s, line_dri_2s)

line_vpb = m.build_event_line(VPB_ISS, POSITIONS, asof=ASOF)
# ratio=0.2604104 → drop = r/(1+r) = 20.6647...%  → làm tròn 2 chữ số = 20.66%
check("VPB: % giá giảm đúng công thức r/(1+r)=20.66%", "20.66%" in line_vpb, line_vpb)
check("VPB: % KL tăng = ratio*100 = 26.04%", "26.04%" in line_vpb, line_vpb)
# C1 (vòng 3) — KHÔNG còn nhánh is_executed: upcoming_events_held luôn "announced" trước ex-date
# thật (corp_action_lib.py:121), "executed" KHÔNG BAO GIỜ đạt được cho use-case cảnh báo TRƯỚC
# (đo thật: 43/43 dòng announced, 0 executed). Bất định chỉ gắn vào "có huỷ/dời không" — KHÔNG
# được hạ giọng hệ quả NAV xuống "CÓ THỂ CHẶN" nữa (luật chuẩn tắc: sự kiện CỔ PHIẾU luôn CHẶN).
check("VPB (announced): trạng thái announced nêu rõ, có thể huỷ/dời",
      "announced" in line_vpb and "có thể bị huỷ/dời" in line_vpb, line_vpb)
check("VPB: PRICE_XCHECK khẳng định SẼ CHẶN NAV, KHÔNG hạ giọng 'CÓ THỂ CHẶN'",
      "SẼ CHẶN NAV" in line_vpb and "CÓ THỂ CHẶN" not in line_vpb, line_vpb)
_vpb_executed = m.build_event_line({**VPB_ISS, "event_status": "executed"}, POSITIONS, asof=ASOF)
check("VPB (executed): cùng khẳng định SẼ CHẶN NAV như announced (không còn nhánh is_executed riêng)",
      "SẼ CHẶN NAV" in _vpb_executed and "executed" in _vpb_executed, _vpb_executed)
# C3 (vòng 3) — VPB_ISS date=2026-09-24 cách ASOF=2026-09-22 ĐÚNG 2 PHIÊN (qua 2026-09-23), KHÔNG
# phải phiên kế tiếp — bug thật đã đo: bản cũ gọi "PHIÊN KẾ TIẾP" + "TỐI NAY" cho ca này (sai đêm,
# thực tế broker chỉnh tối 09-23 chứ không phải tối asof 09-22).
check("VPB cách 2 phiên: day_word là '2 PHIÊN TỚI', KHÔNG PHẢI 'PHIÊN KẾ TIẾP'",
      "2 PHIÊN TỚI" in line_vpb and "PHIÊN KẾ TIẾP" not in line_vpb, line_vpb)
check("VPB cách 2 phiên: adjust_clause nêu đúng đêm trước phiên 2026-09-24, KHÔNG PHẢI 'TỐI NAY'",
      "đêm trước phiên 2026-09-24" in line_vpb and "TỐI NAY" not in line_vpb, line_vpb)

_share_next_session = {**VPB_ISS, "ticker": "NEXTSESS", "date": "2026-09-23"}
line_next = m.build_event_line(_share_next_session, POSITIONS, asof=ASOF)
check("SHARE_EVENT đúng 1 PHIÊN kế tiếp (không phải 2 như VPB): day_word 'PHIÊN KẾ TIẾP' + "
      "adjust_clause đúng 'TỐI NAY'", "PHIÊN KẾ TIẾP" in line_next and "TỐI NAY" in line_next, line_next)
# V5 REGRESSION — SHARE_EVENT PHẢI giữ nguyên "giá/KL" trong adjust_clause (broker đổi cả 2).
check("V5 REGRESSION: adjust_clause của SHARE_EVENT có 'giá/KL TỐI NAY'",
      "giá/KL TỐI NAY" in line_next, line_next)

# C4/M11 (vòng 3) — DIV thiếu value_per_share KHÔNG được crash (guard pre-existing ở producer
# nhưng phải giữ nguyên khi revert vô tình xoá) — không có % và ghi rõ "chưa rõ mức cổ tức".
_dri_no_vps = {**DRI_DIV, "value_per_share": None}
line_dri_no_vps = m.build_event_line(_dri_no_vps, POSITIONS, asof=ASOF)
check("M11 REGRESSION: DIV thiếu value_per_share → không crash, 'chưa rõ mức cổ tức', không có %",
      line_dri_no_vps is not None and "chưa rõ mức cổ tức" in line_dri_no_vps
      and "giá tham chiếu" not in line_dri_no_vps, line_dri_no_vps)

line_vix = m.build_event_line(VIX_AIS, POSITIONS, asof=ASOF)
check("VIX (INFO, price_adjusting=False) → None, không tạo dòng cảnh báo NAV", line_vix is None)

# mã không ai giữ → vẫn ra dòng, nhưng ghi rõ "không xác định được vị thế"
line_orphan = m.build_event_line({**DRI_DIV, "ticker": "ZZZ"}, POSITIONS, asof=ASOF)
check("mã không có vị thế nào → nêu rõ, không KeyError/crash",
      "không xác định được vị thế" in line_orphan, line_orphan)

# thiếu giá (price=None) ở TẤT CẢ holder → không tính % (không chia cho None), vẫn ra dòng
pos_no_price = {"SpaceX": {"DRI": {"qty": 100, "price": None}}}
line_no_price = m.build_event_line(DRI_DIV, pos_no_price, asof=ASOF)
check("thiếu price ở holder → KHÔNG crash, bỏ qua %", "1,000đ/cp" in line_no_price
      and "%" not in line_no_price.split("1,000đ/cp")[1].split(".")[0], line_no_price)

# MUTATION quan trọng nhất R4 — day_word PHẢI suy theo VỊ TRÍ TRONG CỬA SỔ PHIÊN (asof vs
# event["date"]), KHÔNG theo field days_ahead lịch. Đảo ngược điều kiện `event["date"] == asof`
# trước đây (dùng `event["days_ahead"] == 0`) đã PASS im lặng trên đúng ca BID (thứ Sáu ->
# ex-date thứ Hai) — event["days_ahead"] tự khai =1 nhưng thực chất KHÔNG PHẢI hôm nay.
bid_friday_asof = "2026-08-14"
bid_monday_event = {**DRI_DIV, "ticker": "BID", "date": "2026-08-17", "days_ahead": 1}
line_bid = m.build_event_line(bid_monday_event, {"SpaceX": {"BID": {"qty": 100, "price": 40000.0}}},
                               asof=bid_friday_asof)
check("REGRESSION day_word: asof=thứ Sáu 08-14, event date=thứ Hai 08-17 (ngày KHÁC asof) "
      "→ PHẢI là 'PHIÊN KẾ TIẾP', TUYỆT ĐỐI KHÔNG 'HÔM NAY' dù days_ahead tự khai =1",
      "PHIÊN KẾ TIẾP" in line_bid and "HÔM NAY" not in line_bid, line_bid)
line_today_explicit = m.build_event_line({**DRI_DIV, "days_ahead": 99}, POSITIONS, asof=ASOF)
check("REGRESSION day_word: event date==asof → 'HÔM NAY' dù days_ahead tự khai lệch (99)",
      "HÔM NAY" in line_today_explicit, line_today_explicit)

# ── 4. date_field → verb đúng (ex-right vs hiệu lực) ────────────────────────
check("DIV/ISS (exright_date) dùng chữ 'ex-right'", "ex-right" in line_dri and "ex-right" in line_vpb)
vix_effective_forced = {**VIX_AIS, "price_adjusting": True, "event_code": "DIV",
                        "value_per_share": "500"}
line_eff = m.build_event_line(vix_effective_forced, POSITIONS, asof=ASOF)
check("effective_date → dùng chữ 'hiệu lực', KHÔNG 'ex-right'",
      "hiệu lực" in line_eff and "ex-right" not in line_eff, line_eff)

# ── 5. build_report() qua monkeypatch _read_json + read_active_nav_positions ─
_orig_read_json, _orig_positions = m._read_json, m.read_active_nav_positions
try:
    m._read_json = lambda path, default=None: snap if "corp_action_daily_2026-09-22" in path else default
    m.read_active_nav_positions = lambda *a, **k: POSITIONS
    lines, got_snap, events = m.build_report(asof="2026-09-22", days_ahead_max=1)
    check("build_report: đúng số dòng (DRI hôm nay + VPB 1 phiên sau, FAR 2 phiên sau bị loại)",
          len(lines) == 2, lines)
    check("build_report: trả lại snap gốc", got_snap is snap)

    lines_missing, snap_missing, events_missing = m.build_report(asof="2099-01-01")
    check("build_report: asof không có snapshot → ([], None, [])",
          lines_missing == [] and snap_missing is None and events_missing == [])

    note_spacex = m.prompt_note("SpaceX", asof="2026-09-22", days_ahead_max=1)
    check("prompt_note SpaceX: có nội dung (giữ DRI+VPB)",
          "DRI" in note_spacex and "VPB" in note_spacex, note_spacex)
    # M13 REGRESSION — prompt_note() PHẢI dùng đơn vị PHIÊN (mutation M13: hardcode "≤1 NGÀY TỚI").
    check("M13 REGRESSION: prompt_note dùng 'PHIÊN', KHÔNG dùng 'ngày' (case-insensitive)",
          "PHIÊN" in note_spacex and "ngày" not in note_spacex.lower(), note_spacex)
    # C4/M15 REGRESSION — câu R6d ("KHÔNG đổi quyết định mua/bán") là ranh giới quan trọng cho
    # DollarBill khi đọc note này; xoá mất câu này là hồi quy im lặng, không assertion nào bắt
    # được trước bản vá vòng 3.
    check("M15 REGRESSION: prompt_note giữ nguyên câu 'KHÔNG đổi quyết định mua/bán vì thông tin này'",
          "KHÔNG đổi quyết định mua/bán vì thông tin này" in note_spacex, note_spacex)
    note_ghost = m.prompt_note("KhongTonTai", asof="2026-09-22", days_ahead_max=1)
    check("prompt_note account không giữ gì liên quan → rỗng", note_ghost == "", repr(note_ghost))

    # C4/M14 REGRESSION — build_report() PHẢI truyền asof= xuống build_event_line() (dòng ~205
    # trước sửa). Dùng FAKE_ASOF khác hẳn ngày thật hệ thống đang chạy: nếu build_report() quên
    # truyền asof, build_event_line() sẽ tự rơi về today_ict() THẬT — event["date"]==FAKE_ASOF sẽ
    # KHÔNG khớp today_ict() thật, day_word sẽ không còn là "HÔM NAY" nữa.
    FAKE_ASOF = "2026-01-15"
    _orig_read_json_inner = m._read_json
    m._read_json = lambda path, default=None: (
        {"feed_status": "FRESH", "upcoming_events_held": [{**DRI_DIV, "date": FAKE_ASOF}]}
        if f"corp_action_daily_{FAKE_ASOF}" in path else default)
    try:
        lines_fake, _snap_fake, _events_fake = m.build_report(asof=FAKE_ASOF, days_ahead_max=1)
        check("M14 REGRESSION: build_report() truyền asof xuống build_event_line (day_word "
              "'HÔM NAY' đúng FAKE_ASOF, không rơi về today_ict() thật)",
              len(lines_fake) == 1 and "HÔM NAY" in lines_fake[0], lines_fake)
    finally:
        m._read_json = _orig_read_json_inner
finally:
    m._read_json, m.read_active_nav_positions = _orig_read_json, _orig_positions

# ── 6. main() không bao giờ ném lỗi ra ngoài, luôn rc=0 (đây là cảnh báo, không phải gate) ──
_orig_argv = sys.argv
try:
    sys.argv = ["nav_exdate_forecast.py", "--asof", "2099-01-01"]
    rc = m.main()
    check("main() với asof không tồn tại → rc=0, không raise", rc == 0)
finally:
    sys.argv = _orig_argv

# C4/M13+M17 REGRESSION — header/dòng "không có sự kiện" của main() PHẢI dùng đơn vị PHIÊN,
# KHÔNG PHẢI "ngày" (mutation M13: hardcode lại "≤1 NGÀY TỚI"; M17: đổi header). Bắt bằng cách
# CHẠY THẬT main() và đọc stdout — grep xanh trên chuỗi nguồn không đủ (đã lọt vòng 2: khác chữ
# hoa/thường "ngày" vs "NGÀY" khiến grep pass trong khi output thật vẫn in "ngày").
import contextlib  # noqa: E402
import io  # noqa: E402
_orig_read_json4, _orig_positions4, _orig_argv2 = m._read_json, m.read_active_nav_positions, sys.argv
try:
    m._read_json = lambda path, default=None: snap if "corp_action_daily_2026-09-22" in path else default
    m.read_active_nav_positions = lambda *a, **k: POSITIONS
    sys.argv = ["nav_exdate_forecast.py", "--asof", "2026-09-22", "--days-ahead-max", "1"]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc_main = m.main()
    out = buf.getvalue()
    check("M13/M17 REGRESSION: main() rc=0 khi có sự kiện", rc_main == 0)
    check("M13/M17 REGRESSION: header/stdout dùng 'PHIÊN', KHÔNG dùng 'ngày' (case-insensitive)",
          "PHIÊN" in out and "ngày" not in out.lower(), out)
finally:
    m._read_json, m.read_active_nav_positions, sys.argv = _orig_read_json4, _orig_positions4, _orig_argv2

# M17b REGRESSION — nhánh "KHÔNG có sự kiện" (snapshot tồn tại, cửa sổ rỗng) của main() cũng
# PHẢI dùng đơn vị PHIÊN. Khối trên chỉ chạy nhánh CÓ sự kiện; mutation đổi riêng dòng "không có
# sự kiện" (:302-303) về "ngày" vẫn qua 50/0 nếu không có test nào thật sự đi nhánh này.
_orig_read_json6, _orig_positions6, _orig_argv4 = m._read_json, m.read_active_nav_positions, sys.argv
try:
    snap_empty = {"feed_status": "FRESH", "upcoming_events_held": []}
    m._read_json = lambda path, default=None: snap_empty if "corp_action_daily_2026-09-22" in path else default
    m.read_active_nav_positions = lambda *a, **k: POSITIONS
    sys.argv = ["nav_exdate_forecast.py", "--asof", "2026-09-22", "--days-ahead-max", "1"]
    buf_empty = io.StringIO()
    with contextlib.redirect_stdout(buf_empty):
        rc_empty = m.main()
    out_empty = buf_empty.getvalue()
    check("M17b REGRESSION: main() rc=0 khi KHÔNG có sự kiện", rc_empty == 0)
    check("M17b REGRESSION: dòng 'không có sự kiện' dùng 'PHIÊN', KHÔNG dùng 'ngày' (case-insensitive)",
          "PHIÊN" in out_empty and "ngày" not in out_empty.lower(), out_empty)
finally:
    m._read_json, m.read_active_nav_positions, sys.argv = _orig_read_json6, _orig_positions6, _orig_argv4

# R3 — snapshot thiếu + --alert PHẢI notify() (không im lặng, không trông giống "hôm nay yên ả")
_orig_notify = m.notify
_notify_calls = []
try:
    m.notify = lambda msg, channel=None: _notify_calls.append((msg, channel))
    sys.argv = ["nav_exdate_forecast.py", "--asof", "2099-01-01", "--alert"]
    rc = m.main()
    check("R3: --alert + snapshot thiếu → rc=0", rc == 0)
    check("R3: --alert + snapshot thiếu → notify() ĐƯỢC gọi (không im lặng, §14/§28)",
          len(_notify_calls) == 1, _notify_calls)
    check("R3: nội dung notify nêu rõ 'KHÔNG có cảnh báo'",
          _notify_calls and "KHÔNG có cảnh báo" in _notify_calls[0][0], _notify_calls)
    _notify_calls.clear()
    sys.argv = ["nav_exdate_forecast.py", "--asof", "2099-01-01"]  # không --alert → không notify
    m.main()
    check("R3: KHÔNG --alert + snapshot thiếu → notify() KHÔNG được gọi", len(_notify_calls) == 0)
finally:
    m.notify = _orig_notify
    sys.argv = _orig_argv

# C5 — dedupe theo NGÀY cho notify+bus: chạy --alert 2 lần liên tiếp cùng asof (có sự kiện thật)
# chỉ được notify+bus ĐÚNG 1 LẦN — mô phỏng người vận hành sửa BQ stale rồi chạy lại pipeline-0
# cùng ngày (R2 khiến 3b chạy cả ở lần abort, §5 idempotent-side-effects).
_orig_marker = m.ALERT_MARKER
_orig_read_json5, _orig_positions5, _orig_notify2, _orig_bus, _orig_argv3 = (
    m._read_json, m.read_active_nav_positions, m.notify, m.bus, sys.argv)
_bus_calls = []
with tempfile.TemporaryDirectory() as tmpdir:
    try:
        snap_next = {"feed_status": "FRESH", "upcoming_events_held": [{**DRI_DIV, "date": "2026-09-23"}]}
        m.ALERT_MARKER = os.path.join(tmpdir, "nav_exdate_forecast_alerted.json")
        m._read_json = lambda path, default=None: (
            snap if "corp_action_daily_2026-09-22" in path
            else snap_next if "corp_action_daily_2026-09-23" in path
            else (json.load(open(path, encoding="utf-8")) if os.path.exists(path) else default))
        m.read_active_nav_positions = lambda *a, **k: POSITIONS
        m.notify = lambda msg, channel=None: _notify_calls.append((msg, channel))
        m.bus = lambda *a, **k: _bus_calls.append(a)
        sys.argv = ["nav_exdate_forecast.py", "--asof", "2026-09-22", "--days-ahead-max", "1", "--alert"]
        _notify_calls.clear()
        m.main()
        m.main()  # lần chạy lại thứ 2, cùng asof
        check("C5: notify() chỉ gọi 1 lần dù --alert chạy 2 lần cùng asof (dedupe theo ngày)",
              len(_notify_calls) == 1, _notify_calls)
        check("C5: bus() chỉ gọi 1 lần dù --alert chạy 2 lần cùng asof (dedupe theo ngày)",
              len(_bus_calls) == 1, _bus_calls)
        # C5c MUTATION GUARD — mutant `.get("asof") is not None` (bỏ so khớp asof, coi MỌI marker
        # là "đã alert") vẫn qua 2 check trên vì cả 2 lượt CÙNG asof. Đổi asof ở lượt thứ 3: code
        # đúng phải coi đây là ngày MỚI → notify lại (tổng 2); mutant sẽ dừng ở 1 mãi mãi.
        sys.argv = ["nav_exdate_forecast.py", "--asof", "2026-09-23", "--days-ahead-max", "1", "--alert"]
        m.main()
        check("C5c: --alert với asof KHÁC sau đó vẫn notify lại (không bị marker ngày cũ chặn)",
              len(_notify_calls) == 2, _notify_calls)
    finally:
        (m.ALERT_MARKER, m._read_json, m.read_active_nav_positions, m.notify, m.bus, sys.argv) = (
            _orig_marker, _orig_read_json5, _orig_positions5, _orig_notify2, _orig_bus, _orig_argv3)

# ── 7. R5 — read_active_nav_positions() phải chạm SCHEMA THẬT của active_nav_*.json, không
# 100% monkeypatch (mutation "bỏ lọc qty<=0" hoặc đọc sai field trước đây không bị bắt).
with tempfile.TemporaryDirectory() as tmpdir:
    good_path = os.path.join(tmpdir, "active_nav_SpaceX.json")
    with open(good_path, "w", encoding="utf-8") as f:
        json.dump({"account": "SpaceX", "positions": [
            {"ticker": "DRI", "qty": 3700, "price": 14900.0},
            {"ticker": "VPB", "qty": 0, "price": 34000.0},      # qty=0 phải bị lọc
            {"ticker": "ZZZ", "qty": -5, "price": 1000.0},      # qty âm phải bị lọc
            {"ticker": "", "qty": 100, "price": 1000.0},        # thiếu ticker phải bị lọc
        ]}, f)
    bad_path = os.path.join(tmpdir, "active_nav_Broken.json")
    with open(bad_path, "w", encoding="utf-8") as f:
        f.write("{not valid json")
    glob_pat = os.path.join(tmpdir, "active_nav_*.json")
    real_pos = m.read_active_nav_positions(nav_glob=glob_pat)
    check("R5: đọc đúng account label từ field 'account'", "SpaceX" in real_pos, real_pos)
    check("R5: lọc đúng qty<=0 và ticker rỗng, chỉ giữ DRI",
          real_pos.get("SpaceX") == {"DRI": {"qty": 3700, "price": 14900.0}}, real_pos)
    check("R5: file JSON hỏng → bỏ qua, không crash toàn hàm",
          "Broken" not in real_pos, real_pos)

# ── 8. FEED STATUS (2026-10-04, Taylor finding broker-primary-20261003 q6) ─────────────────
# Lịch corp-action từ feed STALE/FAILED KHÔNG được in "không có sự kiện" như thể yên ả. Fixture là
# BẢN SAO THẬT của data/corp_action_daily/ (bin/fixtures/corp_action_daily/): _FAILED 10-02 nguyên
# bản; 09-25 (FRESH) + 09-29/09-30/10-01 (STALE streak 1/2/3) chỉ lược bớt field module không đọc.
import contextlib  # noqa: E402,F811
import io  # noqa: E402,F811

FIXDIR = os.path.join(MIKE_BIN, "fixtures", "corp_action_daily")
ALL_CLEAR = "không có sự kiện corp-action nào"


def _run(argv, snapdir, positions=POSITIONS):
    """Chạy main() HERMETIC: snapshot_path → snapdir, notify/bus/marker bị chặn. Trả (rc, stdout, notify, bus)."""
    saved = (m.snapshot_path, m.read_active_nav_positions, m.notify, m.bus, m.ALERT_MARKER, sys.argv)
    nots, buses = [], []
    with tempfile.TemporaryDirectory() as td:
        try:
            m.snapshot_path = lambda asof, failed=False: os.path.join(
                snapdir, f"corp_action_daily_{asof}{'_FAILED' if failed else ''}.json")
            m.read_active_nav_positions = lambda *a, **k: positions
            m.notify = lambda msg, channel=None: nots.append((msg, channel))
            m.bus = lambda *a, **k: buses.append(a)
            m.ALERT_MARKER = os.path.join(td, "alerted.json")
            sys.argv = ["nav_exdate_forecast.py"] + argv
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = m.main()
            return rc, buf.getvalue(), nots, buses
        finally:
            (m.snapshot_path, m.read_active_nav_positions, m.notify, m.bus, m.ALERT_MARKER, sys.argv) = saved


def _note(account, asof, snapdir, positions=POSITIONS):
    saved = (m.snapshot_path, m.read_active_nav_positions)
    try:
        m.snapshot_path = lambda a, failed=False: os.path.join(
            snapdir, f"corp_action_daily_{a}{'_FAILED' if failed else ''}.json")
        m.read_active_nav_positions = lambda *a, **k: positions
        return m.prompt_note(account, asof=asof)
    finally:
        m.snapshot_path, m.read_active_nav_positions = saved


# 8a. STALE thật (fixture 10-01, streak 3), không có sự kiện trong cửa sổ — ca TPB 10-01
rc, out, nots, buses = _run(["--asof", "2026-10-01", "--alert"], FIXDIR)
check("FEED-STALE: rc=0 (không đổi exit code)", rc == 0)
check("FEED-STALE: dòng ĐẦU stdout là cảnh báo 'LỊCH CORP-ACTION KHÔNG TIN CẬY'",
      out.splitlines()[0].startswith("⚠️ LỊCH CORP-ACTION KHÔNG TIN CẬY"), out)
check("FEED-STALE: nêu đúng streak 3 ngày + asof + thời điểm nạp gần nhất + 'bỏ sót'",
      "feed stale 3 ngày" in out and "asof 2026-10-01" in out
      and "2026-09-26T22:43:40+07:00" in out and "có thể bị bỏ sót" in out, out)
check("FEED-STALE no-events: dòng 2 nói rõ 'KHÔNG phải all-clear' (cảnh báo không bị đọc như yên ả)",
      len(out.splitlines()) == 2 and "NHƯNG lịch không đáng tin" in out.splitlines()[1]
      and "không phải all-clear" in out.splitlines()[1], out)
check("FEED-STALE: KHÔNG in câu all-clear 'không có sự kiện corp-action nào'", ALL_CLEAR not in out, out)
check("FEED-STALE: --alert notify ĐÚNG 1 lần, cảnh báo ở ĐẦU message, đúng kênh",
      len(nots) == 1 and nots[0][0].startswith("⚠️ LỊCH CORP-ACTION KHÔNG TIN CẬY")
      and nots[0][1] == m.CHANNEL, nots)
check("FEED-STALE no-events: không bắn bus finding (tránh spam KB hằng ngày)", buses == [], buses)
rc_ns, out_ns, nots_ns, _b = _run(["--asof", "2026-10-01"], FIXDIR)
check("FEED-STALE: KHÔNG --alert → vẫn in cảnh báo ra stdout nhưng không notify",
      out_ns.startswith("⚠️ LỊCH CORP-ACTION") and nots_ns == [], (out_ns, nots_ns))
for dt, n in (("2026-09-29", 1), ("2026-09-30", 2)):
    _rc, _o, _n, _b = _run(["--asof", dt], FIXDIR)
    check(f"FEED-STALE fixture {dt}: streak {n} đọc đúng từ feed_stale_streak",
          f"feed stale {n} ngày" in _o and ALL_CLEAR not in _o, _o)

# 8b. STALE + CÓ sự kiện: cảnh báo ĐẦU message, rồi header, rồi dòng sự kiện; bus mang feed_status
with tempfile.TemporaryDirectory() as td:
    d = json.load(open(os.path.join(FIXDIR, "corp_action_daily_2026-09-29.json"), encoding="utf-8"))
    d["upcoming_events_held"] = [{**DRI_DIV, "date": "2026-09-29"}]
    json.dump(d, open(os.path.join(td, "corp_action_daily_2026-09-29.json"), "w", encoding="utf-8"))
    rc, out, nots, buses = _run(["--asof", "2026-09-29", "--alert"], td)
    ls = out.splitlines()
    check("FEED-STALE+event: dòng 1=cảnh báo, dòng 2=header, dòng 3=sự kiện DRI",
          len(ls) == 3 and ls[0].startswith("⚠️ LỊCH CORP-ACTION KHÔNG TIN CẬY")
          and ls[1].startswith("📆") and "DRI" in ls[2], out)
    check("FEED-STALE+event: notify 1 lần, message bắt đầu bằng cảnh báo",
          len(nots) == 1 and nots[0][0].startswith("⚠️ LỊCH CORP-ACTION KHÔNG TIN CẬY"), nots)
    check("FEED-STALE+event: bus payload mang feed_status=STALE",
          len(buses) == 1 and buses[0][2].get("feed_status") == "STALE", buses)
    note = _note("SpaceX", "2026-09-29", td)
    check("FEED-STALE+event: --note bắt đầu bằng cảnh báo rồi tới CẢNH BÁO CORP-ACTION",
          note.startswith(" ⚠️ LỊCH CORP-ACTION KHÔNG TIN CẬY") and "CẢNH BÁO CORP-ACTION" in note
          and note.index("⚠️") < note.index("CẢNH BÁO CORP-ACTION"), note)

# 8c. STALE + --note, account không dính sự kiện nào: VẪN phải mang cảnh báo (không '')
note = _note("ZaloPay", "2026-10-01", FIXDIR)
check("FEED-STALE: --note KHÔNG rỗng dù account không dính sự kiện", note != "", repr(note))
check("FEED-STALE: --note nêu cảnh báo + giữ ranh giới 'KHÔNG đổi quyết định mua/bán'",
      "LỊCH CORP-ACTION KHÔNG TIN CẬY" in note and "KHÔNG đổi quyết định mua/bán" in note, note)

# 8d. FAILED thật (fixture 10-02 nguyên bản)
rc, out, nots, buses = _run(["--asof", "2026-10-02", "--alert"], FIXDIR)
check("FEED-FAILED: rc=0", rc == 0)
check("FEED-FAILED: nêu 'calendar UNAVAILABLE (feed_dead)'", "calendar UNAVAILABLE (feed_dead)" in out, out)
check("FEED-FAILED: nêu failed_gate + max_ingested_utc thật của file",
      "failed_gate=feed_dead" in out and "2026-09-26 15:43:40.417516+00" in out, out)
check("FEED-FAILED: KHÔNG rơi về câu chung chung 'KHÔNG có snapshot'", "KHÔNG có snapshot" not in out, out)
check("FEED-FAILED: --alert notify 1 lần với cùng nội dung",
      len(nots) == 1 and "calendar UNAVAILABLE (feed_dead)" in nots[0][0], nots)
note = _note("SpaceX", "2026-10-02", FIXDIR)
check("FEED-FAILED: --note trả 'calendar UNAVAILABLE (feed_dead)', KHÔNG phải chuỗi rỗng",
      "calendar UNAVAILABLE (feed_dead)" in note, repr(note))

# 8e. FEED KHOẺ (fixture 09-25 thật) → đầu ra BYTE-IDENTICAL bản cũ
rc, out, nots, buses = _run(["--asof", "2026-09-25", "--alert"], FIXDIR)
check("FEED-FRESH no-events: stdout BYTE-IDENTICAL câu cũ, không notify/bus",
      out == "[nav_exdate_forecast] 2026-09-25: không có sự kiện corp-action nào trong ≤1 PHIÊN tới "
             "trên mã đang giữ.\n" and nots == [] and buses == [], (out, nots, buses))
check("FEED-FRESH: --note rỗng như cũ (account không dính)", _note("SpaceX", "2026-09-25", FIXDIR) == "")
with tempfile.TemporaryDirectory() as td:
    d = json.load(open(os.path.join(FIXDIR, "corp_action_daily_2026-09-25.json"), encoding="utf-8"))
    d["upcoming_events_held"] = [{**DRI_DIV, "date": "2026-09-25"}, {**VPB_ISS, "date": "2026-09-28"}]
    json.dump(d, open(os.path.join(td, "corp_action_daily_2026-09-25.json"), "w", encoding="utf-8"))
    rc, out, nots, buses = _run(["--asof", "2026-09-25", "--alert"], td)
    _lines = [m.build_event_line(e, POSITIONS, asof="2026-09-25") for e in d["upcoming_events_held"]]
    _expect = "\n".join(["📆 **Corp-action sắp tới ≤1 PHIÊN, mã đang giữ** (2026-09-25):"] + _lines) + "\n"
    check("FEED-FRESH+event: stdout BYTE-IDENTICAL (header+dòng sự kiện, không dòng cảnh báo nào)",
          out == _expect and "⚠️" not in out, out)
    check("FEED-FRESH+event: notify message KHÔNG có tiền tố cảnh báo; bus payload KHÔNG có feed_status",
          len(nots) == 1 and nots[0][0] == _expect.rstrip("\n")
          and len(buses) == 1 and "feed_status" not in buses[0][2], (nots, buses))
    note = _note("SpaceX", "2026-09-25", td)
    check("FEED-FRESH+event: --note không chứa cảnh báo feed", "⚠️" not in note
          and note.startswith(" CẢNH BÁO CORP-ACTION"), note)

# 8f. FAIL-CLOSED: không đọc được trạng thái feed ⇒ 'không xác định được', không bao giờ all-clear
for label, mut in (("thiếu feed_status", lambda d: d.pop("feed_status")),
                   ("feed_status=DEAD", lambda d: d.update(feed_status="DEAD")),
                   ("feed_status='fresh' (sai hoa/thường)", lambda d: d.update(feed_status="fresh")),
                   ("feed_status=None", lambda d: d.update(feed_status=None))):
    with tempfile.TemporaryDirectory() as td:
        d = json.load(open(os.path.join(FIXDIR, "corp_action_daily_2026-09-25.json"), encoding="utf-8"))
        mut(d)
        json.dump(d, open(os.path.join(td, "corp_action_daily_2026-09-25.json"), "w", encoding="utf-8"))
        rc, out, nots, buses = _run(["--asof", "2026-09-25", "--alert"], td)
        check(f"FEED-UNKNOWN [{label}]: nói 'không xác định được', KHÔNG all-clear, có notify",
              "không xác định được trạng thái feed" in out and ALL_CLEAR not in out and len(nots) == 1, out)
        check(f"FEED-UNKNOWN [{label}]: --note mang cảnh báo",
              "không xác định được trạng thái feed" in _note("SpaceX", "2026-09-25", td))
with tempfile.TemporaryDirectory() as td:   # không có CẢ snapshot lẫn _FAILED
    check("FEED-MISSING: --note nói 'không xác định được' (không ''), main vẫn câu 'KHÔNG có snapshot'",
          "không xác định được trạng thái feed" in _note("SpaceX", "2099-01-01", td)
          and "KHÔNG có snapshot" in _run(["--asof", "2099-01-01"], td)[1])
    open(os.path.join(td, "corp_action_daily_2099-01-02_FAILED.json"), "w").write("{hỏng")
    check("FEED-MISSING: file _FAILED hỏng JSON → coi như không đọc được, KHÔNG crash, rc=0",
          _run(["--asof", "2099-01-02"], td)[0] == 0
          and "KHÔNG có snapshot" in _run(["--asof", "2099-01-02"], td)[1])
    open(os.path.join(td, "corp_action_daily_2099-01-03_FAILED.json"), "w").write("[]")
    try:
        _rc3 = _run(["--asof", "2099-01-03"], td)[0]
    except Exception as exc:  # noqa: BLE001 — biến crash thành assertion CÓ TÊN
        _rc3 = repr(exc)
    check("FEED-MISSING: _FAILED không phải object → không crash, rc=0", _rc3 == 0, _rc3)

# 8g. dedupe: STALE no-events chạy --alert 2 lần cùng asof → notify 1 lần (§5)
_saved = (m.snapshot_path, m.read_active_nav_positions, m.notify, m.bus, m.ALERT_MARKER, sys.argv)
with tempfile.TemporaryDirectory() as td:
    _n2 = []
    try:
        m.snapshot_path = lambda a, failed=False: os.path.join(
            FIXDIR, f"corp_action_daily_{a}{'_FAILED' if failed else ''}.json")
        m.read_active_nav_positions = lambda *a, **k: POSITIONS
        m.notify = lambda msg, channel=None: _n2.append(msg)
        m.bus = lambda *a, **k: None
        m.ALERT_MARKER = os.path.join(td, "alerted.json")
        sys.argv = ["nav_exdate_forecast.py", "--asof", "2026-10-01", "--alert"]
        with contextlib.redirect_stdout(io.StringIO()):
            m.main()
            m.main()
        check("FEED-STALE: --alert 2 lần cùng asof → notify chỉ 1 lần (dedupe theo ngày)", len(_n2) == 1, _n2)
    finally:
        (m.snapshot_path, m.read_active_nav_positions, m.notify, m.bus, m.ALERT_MARKER, sys.argv) = _saved

# 8h. arch-review 2026-10-04 — các ca reviewer đề xuất
def _wr(td, name, obj):
    with open(os.path.join(td, name), "w", encoding="utf-8") as f:
        (f.write(obj) if isinstance(obj, str) else json.dump(obj, f))


def _load(name):
    return json.load(open(os.path.join(FIXDIR, name), encoding="utf-8"))


# (1) dedupe CHÉO NHÁNH: cảnh báo feed_warn (không sự kiện) KHÔNG được nuốt alert sự kiện cùng asof
_saved = (m.snapshot_path, m.read_active_nav_positions, m.notify, m.bus, m.ALERT_MARKER, sys.argv)
with tempfile.TemporaryDirectory() as td:
    _n3, _b3 = [], []
    try:
        m.snapshot_path = lambda a, failed=False: os.path.join(
            td, f"corp_action_daily_{a}{'_FAILED' if failed else ''}.json")
        m.read_active_nav_positions = lambda *a, **k: POSITIONS
        m.notify = lambda msg, channel=None: _n3.append(msg)
        m.bus = lambda *a, **k: _b3.append(a)
        m.ALERT_MARKER = os.path.join(td, "alerted.json")
        sys.argv = ["nav_exdate_forecast.py", "--asof", "2026-10-01", "--alert"]
        _d = _load("corp_action_daily_2026-10-01.json")
        _wr(td, "corp_action_daily_2026-10-01.json", _d)          # STALE, không sự kiện
        with contextlib.redirect_stdout(io.StringIO()):
            m.main()
        _d["upcoming_events_held"] = [{**DRI_DIV, "date": "2026-10-01"}]
        _wr(td, "corp_action_daily_2026-10-01.json", _d)          # chạy lại snapshot: nay CÓ sự kiện
        with contextlib.redirect_stdout(io.StringIO()):
            m.main()
            m.main()                                                # lần 3: events đã alert → dedupe
        check("DEDUPE-CROSS-BRANCH: feed_warn rồi alert SỰ KIỆN cùng asof vẫn bắn (notify=2, bus=1)",
              len(_n3) == 2 and "DRI" in _n3[1] and len(_b3) == 1, (_n3, _b3))
        check("DEDUPE-CROSS-BRANCH: lần chạy thứ 3 (events đã alert) vẫn dedupe", len(_n3) == 2, _n3)
        check("DEDUPE-CROSS-BRANCH: marker lưu cả 2 kind", sorted(json.load(open(m.ALERT_MARKER))["kinds"])
              == ["events", "feed_warn"], open(m.ALERT_MARKER).read())
        _wr(td, "alerted.json", {"asof": "2026-10-01"})            # marker CŨ (không kinds) = events
        check("DEDUPE-LEGACY-MARKER: marker cũ {asof} coi là đã alert events, chưa alert feed_warn",
              m._already_alerted_today("2026-10-01") and not m._already_alerted_today("2026-10-01", "feed_warn"))
    finally:
        (m.snapshot_path, m.read_active_nav_positions, m.notify, m.bus, m.ALERT_MARKER, sys.argv) = _saved

# (2) _FAILED dạng DEAD-parse-error: chỉ có `max_ingested` (corp_action_daily.py:1510-1515)
with tempfile.TemporaryDirectory() as td:
    _f = _load("corp_action_daily_2026-10-02_FAILED.json")
    _f["feed"] = {"max_ingested": "2026-09-26 15:43:40+00", "reason": "parse"}
    _wr(td, "corp_action_daily_2026-10-02_FAILED.json", _f)
    check("FEED-FAILED DEAD-parse: dùng fallback `max_ingested`, không 'không rõ'",
          "2026-09-26 15:43:40+00" in _run(["--asof", "2026-10-02"], td)[1], _run(["--asof", "2026-10-02"], td)[1])
    # (5) failed_gate khác feed_dead vẫn ra thông điệp FAILED cụ thể
    _f["failed_gate"] = "selfcheck"
    _wr(td, "corp_action_daily_2026-10-02_FAILED.json", _f)
    _o = _run(["--asof", "2026-10-02"], td)[1]
    check("FEED-FAILED gate=selfcheck: nêu 'calendar UNAVAILABLE (selfcheck)' + failed_gate=selfcheck",
          "calendar UNAVAILABLE (selfcheck)" in _o and "failed_gate=selfcheck" in _o, _o)

# (3) snapshot hợp lệ JSON nhưng KHÔNG phải object → UNKNOWN, không crash (main + note)
for _label, _raw in (("[]", "[]"), ("[1]", "[1]"), ('"x"', '"x"'), ("5", "5")):
    with tempfile.TemporaryDirectory() as td:
        _wr(td, "corp_action_daily_2026-09-25.json", _raw)
        try:
            _r = _run(["--asof", "2026-09-25", "--alert"], td)
            _nt = _note("SpaceX", "2026-09-25", td)
            _ok = (_r[0] == 0 and "không xác định được trạng thái feed" in _r[1] and len(_r[2]) == 1
                   and "không xác định được trạng thái feed" in _nt)
            _det = (_r[1], _nt)
        except Exception as exc:  # noqa: BLE001 — crash thành assertion CÓ TÊN
            _ok, _det = False, repr(exc)
        check(f"FEED-UNKNOWN non-object snapshot {_label}: rc=0, cảnh báo, notify, note — không crash", _ok, _det)

# (4) feed_status=FRESH nhưng usable=False → UNKNOWN
with tempfile.TemporaryDirectory() as td:
    _d = _load("corp_action_daily_2026-09-25.json"); _d["usable"] = False
    _wr(td, "corp_action_daily_2026-09-25.json", _d)
    _o = _run(["--asof", "2026-09-25"], td)[1]
    check("FEED-UNKNOWN FRESH+usable=False: KHÔNG all-clear",
          ALL_CLEAR not in _o and "không xác định được trạng thái feed" in _o, _o)
    _d["usable"] = True
    _wr(td, "corp_action_daily_2026-09-25.json", _d)
    check("FEED-FRESH usable=True: vẫn all-clear cũ (không báo nhầm)", ALL_CLEAR in _run(["--asof", "2026-09-25"], td)[1])

# (M2/M14) STALE thiếu feed_stale_streak → '?', KHÔNG 'None'/'0'
with tempfile.TemporaryDirectory() as td:
    _d = _load("corp_action_daily_2026-10-01.json"); _d.pop("feed_stale_streak")
    _wr(td, "corp_action_daily_2026-10-01.json", _d)
    _o = _run(["--asof", "2026-10-01"], td)[1]
    check("FEED-STALE thiếu streak: 'feed stale ? ngày' (không 'None'/'0')",
          "feed stale ? ngày" in _o and "None" not in _o and "stale 0" not in _o, _o)

# _FAILED + snapshot cùng tồn tại → snapshot thắng (bản chạy lại thành công), không cảnh báo FAILED
with tempfile.TemporaryDirectory() as td:
    _wr(td, "corp_action_daily_2026-09-25.json", _load("corp_action_daily_2026-09-25.json"))
    _wr(td, "corp_action_daily_2026-09-25_FAILED.json", _load("corp_action_daily_2026-10-02_FAILED.json"))
    _o = _run(["--asof", "2026-09-25"], td)[1]
    check("COEXIST _FAILED+snapshot FRESH cùng asof: snapshot thắng (all-clear cũ, không 'UNAVAILABLE')",
          ALL_CLEAR in _o and "UNAVAILABLE" not in _o, _o)

print(f"PASS={len(PASS)} FAIL={len(FAIL)}")
for f in FAIL:
    print(f"  FAIL: {f}")
sys.exit(1 if FAIL else 0)
