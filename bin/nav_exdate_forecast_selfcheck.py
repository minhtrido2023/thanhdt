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
import os
import sys

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

# ── 2. relevant_events() cửa sổ days_ahead<=N (biên) ────────────────────────
snap = {"upcoming_events_held": [DRI_DIV, VPB_ISS, VIX_AIS,
                                 {**VPB_ISS, "ticker": "FAR", "days_ahead": 2}]}
ev1 = m.relevant_events(snap, days_ahead_max=1)
check("days_ahead<=1 giữ đúng 3 sự kiện (loại FAR days_ahead=2)",
      {e["ticker"] for e in ev1} == {"DRI", "VPB", "VIX"}, sorted(e["ticker"] for e in ev1))
ev0 = m.relevant_events(snap, days_ahead_max=0)
check("days_ahead<=0 chỉ giữ VIX (days_ahead=0)",
      {e["ticker"] for e in ev0} == {"VIX"}, sorted(e["ticker"] for e in ev0))
check("days_ahead_max âm → rỗng (không lọt sự kiện nào qua biên sai hướng)",
      m.relevant_events(snap, days_ahead_max=-1) == [])
check("snapshot rỗng/None → rỗng, không crash", m.relevant_events(None) == [])
check("thiếu key upcoming_events_held → rỗng, không crash", m.relevant_events({}) == [])

# ── 3. build_event_line() — số học phải khớp tay ────────────────────────────
line_dri = m.build_event_line(DRI_DIV, POSITIONS)
check("DRI: có % giá (~6.71%)", "6.71%" in line_dri, line_dri)
check("DRI: nêu đúng cả 2 account giữ", "SpaceX 3,700cp" in line_dri and "ZaloPay 1,900cp" in line_dri)
check("DRI: gắn nhãn KỲ VỌNG không phải lỗi", "KHÔNG PHẢI LỖI".lower() in line_dri.lower()
      or "kỳ vọng" in line_dri.lower())

line_vpb = m.build_event_line(VPB_ISS, POSITIONS)
# ratio=0.2604104 → drop = r/(1+r) = 20.6647...%  → làm tròn 2 chữ số = 20.66%
check("VPB: % giá giảm đúng công thức r/(1+r)=20.66%", "20.66%" in line_vpb, line_vpb)
check("VPB: % KL tăng = ratio*100 = 26.04%", "26.04%" in line_vpb, line_vpb)
check("VPB: cảnh báo PRICE_XCHECK SẼ CHẶN", "SẼ CHẶN NAV" in line_vpb, line_vpb)

line_vix = m.build_event_line(VIX_AIS, POSITIONS)
check("VIX (INFO, price_adjusting=False) → None, không tạo dòng cảnh báo NAV", line_vix is None)

# mã không ai giữ → vẫn ra dòng, nhưng ghi rõ "không xác định được vị thế"
line_orphan = m.build_event_line({**DRI_DIV, "ticker": "ZZZ"}, POSITIONS)
check("mã không có vị thế nào → nêu rõ, không KeyError/crash",
      "không xác định được vị thế" in line_orphan, line_orphan)

# thiếu giá (price=None) ở TẤT CẢ holder → không tính % (không chia cho None), vẫn ra dòng
pos_no_price = {"SpaceX": {"DRI": {"qty": 100, "price": None}}}
line_no_price = m.build_event_line(DRI_DIV, pos_no_price)
check("thiếu price ở holder → KHÔNG crash, bỏ qua %", "1,000đ/cp" in line_no_price
      and "%" not in line_no_price.split("1,000đ/cp")[1].split(".")[0], line_no_price)

# ── 4. date_field → verb đúng (ex-right vs hiệu lực) ────────────────────────
check("DIV/ISS (exright_date) dùng chữ 'ex-right'", "ex-right" in line_dri and "ex-right" in line_vpb)
vix_effective_forced = {**VIX_AIS, "price_adjusting": True, "event_code": "DIV",
                        "value_per_share": "500"}
line_eff = m.build_event_line(vix_effective_forced, POSITIONS)
check("effective_date → dùng chữ 'hiệu lực', KHÔNG 'ex-right'",
      "hiệu lực" in line_eff and "ex-right" not in line_eff, line_eff)

# ── 5. build_report() qua monkeypatch _read_json + read_active_nav_positions ─
_orig_read_json, _orig_positions = m._read_json, m.read_active_nav_positions
try:
    m._read_json = lambda path, default=None: snap if "corp_action_daily_2026-09-22" in path else default
    m.read_active_nav_positions = lambda *a, **k: POSITIONS
    lines, got_snap, events = m.build_report(asof="2026-09-22", days_ahead_max=1)
    check("build_report: đúng số dòng (DRI+VPB, VIX bị lọc vì INFO)", len(lines) == 2, lines)
    check("build_report: trả lại snap gốc", got_snap is snap)

    lines_missing, snap_missing, events_missing = m.build_report(asof="2099-01-01")
    check("build_report: asof không có snapshot → ([], None, [])",
          lines_missing == [] and snap_missing is None and events_missing == [])

    note_spacex = m.prompt_note("SpaceX", asof="2026-09-22", days_ahead_max=1)
    check("prompt_note SpaceX: có nội dung (giữ DRI+VPB)",
          "DRI" in note_spacex and "VPB" in note_spacex, note_spacex)
    note_ghost = m.prompt_note("KhongTonTai", asof="2026-09-22", days_ahead_max=1)
    check("prompt_note account không giữ gì liên quan → rỗng", note_ghost == "", repr(note_ghost))
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

print(f"PASS={len(PASS)} FAIL={len(FAIL)}")
for f in FAIL:
    print(f"  FAIL: {f}")
sys.exit(1 if FAIL else 0)
