#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nav_exdate_forecast.py — cảnh báo TRƯỚC giờ đóng cửa cho sự kiện corp-action (ex-date/AIS)
sắp tới trên mã ĐANG GIỮ, dịch lại `upcoming_events_held` của `corp_action_daily.py` (Lớp 6)
sang ngôn ngữ "tối nay NAV sẽ thấy gì" cho người trực NAV — thay vì để cổng PRICE_XCHECK của
`daily_nav_snapshot.py` là người ĐẦU TIÊN báo động lúc chạy NAV cuối ngày.

VÌ SAO TỒN TẠI (L1, quyết định user 2026-09-22): lớp lỗi "NAV bị PRICE_XCHECK chặn vì corp-action"
tái diễn ≥4 lần (PVT 09-08, DGC 09-11, VIB 09-09, VHM 08-05, DRI 09-21) — mỗi lần dữ liệu trả
lời được "vì sao lệch" đã nằm sẵn trên đĩa (`data/corp_action_daily/corp_action_daily_<date>.json`,
ghi bởi cron 07:30) NHIỀU GIỜ trước khi ai đó phát hiện NAV bị chặn. File này KHÔNG đổi logic
NAV/PRICE_XCHECK (đó là việc L2-L4 riêng, xem `kb/coding_guidelines.md` §21 + docstring
`daily_nav_snapshot.cum_dividend_double_count`) — nó CHỈ đọc lại đúng field `upcoming_events_held`
đã có sẵn, lọc `days_ahead<=1`, và in ra một câu người đọc hiểu ngay, đủ sớm để không bất ngờ.

Phân loại (2 nhánh, cố ý tách vì hệ quả khác nhau):
  * CASH_DIV  (event_code=DIV, price_adjusting)   — giá dự kiến giảm ĐÚNG bằng value_per_share/cp,
    NAV vẫn tính được bình thường qua đường cum_dividend_double_count (§21) — chỉ là THÔNG BÁO,
    không cần ai xử lý tay.
  * SHARE_EVENT (price_adjusting, event_code≠DIV — cổ tức CP/thưởng/quyền mua) — broker sẽ đổi
    CẢ giá LẪN khối lượng cùng lúc; PRICE_XCHECK của daily_nav_snapshot.py SẼ CHẶN (đúng thiết
    kế, xem corp_action_adj ở đó) và CẦN NGƯỜI backfill bằng `--from-raw` hoặc đợi broker đồng
    bộ. Cảnh báo ở đây MẠNH HƠN cho đúng nhánh này.
  * (price_adjusting=False, vd AIS effective_date) không tạo dòng cảnh báo NAV — không có tác
    động giá/KL dự kiến hôm đó (AIS chỉ chính thức hoá con số CP, không đổi giá bảng điện).

KHÔNG chặn gì, KHÔNG đổi số — chỉ đọc + in/gửi. Nguồn dữ liệu (`corp_action_daily_<asof>.json`,
`active_nav_<label>.json`) là 2 artifact đã tồn tại, không tự tính lại corp-action.

Usage:
    python3 mike/bin/nav_exdate_forecast.py [--asof YYYY-MM-DD]      # in báo cáo ra stdout
    python3 mike/bin/nav_exdate_forecast.py --alert                 # + gửi Discord/bus khi có gì
    python3 mike/bin/nav_exdate_forecast.py --note ACCOUNT           # chuỗi bơm vào prompt DollarBill
                                                                     # (rỗng nếu account không dính)
Exit: luôn 0 — đây là cảnh báo sớm, không phải cổng chặn.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import sys

MIKE_BIN = os.path.dirname(os.path.abspath(__file__))
if MIKE_BIN not in sys.path:
    sys.path.insert(0, MIKE_BIN)

import wc_paths  # noqa: E402

WC_ROOT = wc_paths.find_wc_root(__file__)
MIKE = os.path.join(WC_ROOT, "mike")
for _p in (WC_ROOT, os.path.join(MIKE, "bin")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from corp_action_daily import notify, bus, snapshot_path, today_ict  # noqa: E402
from trading_bot.vn_market import next_trading_day  # noqa: E402

ACTIVE_NAV_GLOB = os.path.join(WC_ROOT, "data", "execution_logs", "active_nav_*.json")
CHANNEL = "trading_daily"
ALERT_MARKER = os.path.join(WC_ROOT, "data", "nav_exdate_forecast_alerted.json")
DAYS_AHEAD_MAX = 1   # hôm nay (0) hoặc PHIÊN GIAO DỊCH kế tiếp (1) — cùng cửa sổ PRICE_XCHECK sẽ
                     # chạm tối nay/mai. Cố ý dùng khoảng cách PHIÊN, không phải days_ahead lịch
                     # của snapshot (corp_action_daily.py tính bằng hiệu ngày dương lịch thô) —
                     # thứ Sáu -> thứ Hai là days_ahead=3 nhưng chỉ cách 1 PHIÊN (bug thật đo trên
                     # BID ex-date 2026-08-17, một thứ Hai: cảnh báo lẽ ra phải hiện thứ Sáu 08-14
                     # nhưng lọc days_ahead<=1 bỏ sót). classify_price_mismatch (L2) đã dùng đúng
                     # cách này (valid_dates = {date, next_trading_day(date)}) — nav_exdate_forecast
                     # phải khớp cùng logic để không "cảnh báo sớm" sai cửa sổ mà cổng NAV áp dụng.


def _already_alerted_today(asof):
    """True nếu đã notify+bus cho ĐÚNG `asof` này rồi — tránh gửi Discord/bus trùng khi người
    vận hành chạy lại pipeline-0 cùng ngày sau khi sửa BQ stale (R2 khiến 3b chạy cả ở lần
    abort, §5 idempotent-side-effects). Đọc `ALERT_MARKER` qua tên module-level (không phải
    default-arg) để test monkeypatch `m.ALERT_MARKER` có tác dụng thật — default-arg bind giá
    trị NGAY LÚC ĐỊNH NGHĨA hàm, monkeypatch attribute sau đó sẽ vô hiệu."""
    return _read_json(ALERT_MARKER, {}).get("asof") == asof


def _mark_alerted_today(asof):
    tmp = ALERT_MARKER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"asof": asof}, f)
    os.replace(tmp, ALERT_MARKER)


def _read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def read_active_nav_positions(nav_glob=ACTIVE_NAV_GLOB):
    """{label: {ticker: {"qty":…, "price":…}}} từ artifact `compute_active_nav_all.sh` 20:15 ICT
    T-1 — CÙNG artifact `corp_action_daily.read_positions` dùng, đọc thêm field `price` (không
    có trong `read_positions`) để ước lượng % giá dự kiến giảm mà không cần gọi broker/BQ."""
    out = {}
    for path in sorted(glob.glob(nav_glob)):
        d = _read_json(path)
        if not d:
            continue
        label = d.get("account") or os.path.basename(path)
        pos = {}
        for p in d.get("positions") or []:
            tk, qty = p.get("ticker"), int(p.get("qty") or 0)
            if not tk or qty <= 0:
                continue
            pos[tk] = {"qty": qty, "price": p.get("price")}
        out[label] = pos
    return out


def trading_day_window(asof, days_ahead_max):
    """{asof, asof+1 PHIÊN, ..., asof+days_ahead_max PHIÊN} — khoảng cách PHIÊN GIAO DỊCH, không
    phải ngày lịch. `days_ahead` trong snapshot là hiệu ngày dương lịch thô (corp_action_daily.py
    dòng ~1273) nên thứ Sáu→thứ Hai = 3, không phải 1 — lọc thẳng bằng field đó bỏ sót cảnh báo
    sớm cho mọi ex-date rơi vào thứ Hai (bug thật: BID ex-date 2026-08-17)."""
    dates = {asof}
    d = datetime.date.fromisoformat(asof)
    for _ in range(max(days_ahead_max, 0)):
        d = next_trading_day(d)
        dates.add(d.isoformat())
    return dates


def relevant_events(snap, asof, days_ahead_max=DAYS_AHEAD_MAX):
    """Sự kiện trong `upcoming_events_held` có `date` rơi vào cửa sổ PHIÊN GIAO DỊCH kể từ
    `asof` (xem `trading_day_window`) — KHÔNG dùng thẳng field `days_ahead` của snapshot (đó là
    khoảng cách NGÀY LỊCH, sai lệch quanh cuối tuần/lễ)."""
    valid_dates = trading_day_window(asof, days_ahead_max)
    return [e for e in (snap or {}).get("upcoming_events_held") or [] if e.get("date") in valid_dates]


def classify(event):
    if not event.get("price_adjusting"):
        return "INFO"
    if event.get("event_code") == "DIV":
        return "CASH_DIV"
    return "SHARE_EVENT"


def _holders_for(ticker, positions_by_account):
    return {lb: p[ticker] for lb, p in positions_by_account.items() if ticker in p}


def _fmt_pct(x):
    return f"{x:.2f}%" if x is not None else "?"


def _session_word(asof, event_date):
    """Cụm danh từ THUẦN mô tả vị trí phiên của event_date so với asof — tách khỏi mệnh đề
    "broker đổi giá/KL TỐI NAY" (xem `_adjust_clause`, C3): hai câu chỉ CÙNG đúng khi event_date
    là đúng phiên kế tiếp; ghép chung vào day_word khiến event cách ≥2 phiên bị gán nhầm "TỐI
    NAY" (bug thật: VPB ex-right 2026-09-24 cách asof 2026-09-22 tới 2 phiên)."""
    if event_date == asof:
        return "HÔM NAY"
    d = datetime.date.fromisoformat(asof)
    n = 0
    while d.isoformat() != event_date and n <= 30:
        d = next_trading_day(d)
        n += 1
    return f"PHIÊN KẾ TIẾP ({event_date})" if n == 1 else f"{n} PHIÊN TỚI ({event_date})"


def _adjust_clause(asof, event_date):
    """"broker đổi giá/KL TỐI NAY" CHỈ đúng khi event_date == next_trading_day(asof) — broker
    điều chỉnh vào đêm NGAY TRƯỚC phiên diễn ra sự kiện, không phải đêm của asof khi event còn
    cách ≥2 phiên. Rỗng khi event_date==asof (đã điều chỉnh từ đêm trước, không còn gì "sắp" xảy ra)."""
    if event_date == asof:
        return ""
    nxt = next_trading_day(datetime.date.fromisoformat(asof)).isoformat()
    if event_date == nxt:
        return "Broker đổi giá/KL TỐI NAY"
    return f"Broker đổi giá/KL vào đêm trước phiên {event_date}"


def build_event_line(event, positions_by_account, asof=None):
    tk = event["ticker"]
    kind = classify(event)
    holders = _holders_for(tk, positions_by_account)
    asof = asof or today_ict()
    day_word = _session_word(asof, event["date"])
    adjust_clause = _adjust_clause(asof, event["date"])
    # date_field phân biệt "chốt quyền/ex-right" (DIV/ISS thường) với "hiệu lực" (AIS chính thức
    # hoá số CP) — dùng đúng field snapshot đã gắn theo từng dòng, không đoán chung một chữ.
    verb = "hiệu lực" if event.get("date_field") == "effective_date" else "ex-right"
    when = f"{verb} {day_word}"
    who = ", ".join(f"{lb} {h['qty']:,}cp" for lb, h in holders.items()) or "(không xác định được vị thế)"

    if kind == "CASH_DIV":
        # value_per_share là TUỲ CHỌN ở producer (corp_action_daily.py:1286) dù
        # is_price_adjusting trả True cho MỌI DIV (corp_action_lib.py:59-61) — guard, đừng giả
        # định luôn có (quét 160 dòng DIV thật: 0 ca thiếu, nhưng vẫn không được crash nếu có).
        vps_raw = event.get("value_per_share")
        vps = float(vps_raw) if vps_raw is not None else None
        pct = None
        if vps is not None:
            for h in holders.values():
                if h.get("price"):
                    pct = vps / float(h["price"]) * 100
                    break
        pct_txt = f" (~{_fmt_pct(pct)} giá tham chiếu)" if pct is not None else ""
        vps_txt = f"{vps:,.0f}đ/cp" if vps is not None else "(chưa rõ mức cổ tức)"
        clause = f" {adjust_clause}." if adjust_clause else ""
        return (f"💰 **{tk}** {when} — cổ tức tiền mặt {vps_txt}{pct_txt}.{clause} "
                f"NAV sẽ thấy broker HẠ marketPrice đúng khoản này — ĐÂY LÀ KỲ VỌNG, "
                f"không phải lỗi (đường `cum_dividend_double_count`, §21, xử lý tự động). "
                f"Đang giữ: {who}.")

    if kind == "SHARE_EVENT":
        ratio = event.get("exercise_ratio")
        ratio_txt, drop_txt = "", ""
        if ratio:
            r = float(ratio)
            ratio_txt = f" tỉ lệ {r * 100:.2f}%"
            drop_txt = f" (giá tham chiếu dự kiến giảm ~{_fmt_pct(r / (1 + r) * 100)}, KL tăng ~{_fmt_pct(r * 100)})"
        method = f" — {event['issue_method_vi']}" if event.get("issue_method_vi") else ""
        # KHÔNG có nhánh is_executed: upcoming_events_held nằm ở "announced" cho tới ~22:2x ICT
        # đêm ex-date tự nó (corp_action_lib.py:121) — với một cảnh báo TRƯỚC ex-date, nhánh
        # "executed" KHÔNG BAO GIỜ đạt được (đo thật: 43/43 dòng upcoming_events_held đang
        # "announced", 0 "executed"). Bất định thật nằm ở "sự kiện có bị huỷ/dời không", KHÔNG
        # nằm ở "broker có điều chỉnh giá không nếu diễn ra" — luật chuẩn tắc của đội (VHM 08-05/
        # MBB 08-11/VIB 09-09) là sự kiện CỔ PHIẾU vẫn CHẶN NAV, không có ngoại lệ tự động.
        status = event.get("event_status")
        clause = f" {adjust_clause}." if adjust_clause else ""
        return (f"🚨 **{tk}** {event['event_code']}{method}{ratio_txt}, {when}{drop_txt}. "
                f"Sự kiện đang ở trạng thái `{status or 'chưa rõ'}` (có thể bị huỷ/dời).{clause} "
                f"NẾU diễn ra, broker SẼ đổi CẢ giá LẪN khối lượng — `daily_nav_snapshot.py` "
                f"PRICE_XCHECK **SẼ CHẶN NAV** (đúng thiết kế, không phải bug) cho tới khi broker "
                f"đồng bộ hoặc người backfill bằng `--from-raw`. CẦN NGƯỜI theo dõi khi chạy NAV "
                f"phiên {event['date']}. Đang giữ: {who}.")

    return None  # INFO — không tạo dòng cảnh báo NAV (xem docstring)


def build_report(asof=None, days_ahead_max=DAYS_AHEAD_MAX):
    """([dòng str], snap|None, [event dict])."""
    asof = asof or today_ict()
    snap = _read_json(snapshot_path(asof))
    if snap is None:
        return [], None, []
    events = relevant_events(snap, asof, days_ahead_max)
    positions = read_active_nav_positions()
    lines = [ln for ln in (build_event_line(e, positions, asof=asof) for e in events) if ln]
    return lines, snap, events


def prompt_note(account, asof=None, days_ahead_max=DAYS_AHEAD_MAX):
    """Chuỗi bơm vào prompt DollarBill cho ĐÚNG `account` — rỗng nếu account không giữ mã nào
    dính sự kiện trong cửa sổ. Cùng khuôn `signal_holds.prompt_note` (KHÔNG hardcode kênh Discord
    ở đây — đây là note cho LLM viết plan, không phải tin nhắn)."""
    lines, _snap, events = build_report(asof, days_ahead_max)
    positions = read_active_nav_positions()
    held = positions.get(account) or {}
    mine = [e for e in events if e["ticker"] in held]
    if not mine:
        return ""
    bits = [f" CẢNH BÁO CORP-ACTION ≤{days_ahead_max} PHIÊN TỚI trên mã đang giữ (nav_exdate_forecast.py, "
            "đọc lại corp_action_daily — KHÔNG tự suy diễn thêm, chỉ nhắc để không nhầm biến động giá dự "
            "kiến này với tín hiệu thị trường):"]
    for e in mine:
        kind = classify(e)
        tag = "cổ tức tiền mặt (giá giảm dự kiến, bình thường)" if kind == "CASH_DIV" else \
              "sự kiện CỔ PHIẾU (giá+KL đổi, NAV có thể bị chặn tối nay/mai)" if kind == "SHARE_EVENT" else "AIS"
        bits.append(f" • {e['ticker']} {e['event_code']} {e['date']} — {tag}.")
    bits.append(" KHÔNG đổi quyết định mua/bán vì thông tin này — đây chỉ là thông báo để không "
                "nhầm biến động giá dự kiến với tín hiệu thị trường.")
    return "".join(bits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof")
    ap.add_argument("--days-ahead-max", type=int, default=DAYS_AHEAD_MAX)
    ap.add_argument("--alert", action="store_true", help="gửi Discord/bus khi có sự kiện")
    ap.add_argument("--note", help="in prompt_note() cho ACCOUNT rồi thoát")
    ap.add_argument("--trace")
    a = ap.parse_args()

    if a.note:
        print(prompt_note(a.note, asof=a.asof, days_ahead_max=a.days_ahead_max))
        return 0

    lines, snap, events = build_report(a.asof, a.days_ahead_max)
    asof = a.asof or today_ict()
    if snap is None:
        # snapshot thiếu/hỏng KHÔNG được phép im lặng trông giống "hôm nay không có sự kiện" —
        # đó là ca phổ biến nhất (§14/§28) và feature này chết theo cách không ai nhận ra nếu
        # nhánh --alert không tự lên tiếng khi chính nguồn dữ liệu của nó vắng mặt.
        warn = (f"⚠️ [nav_exdate_forecast] KHÔNG có snapshot corp_action_daily cho {asof} — "
                f"{os.path.relpath(snapshot_path(asof), WC_ROOT)} chưa tồn tại/đọc lỗi. "
                f"KHÔNG có cảnh báo corp-action hôm nay từ pipeline này — kiểm tay.")
        print(warn)
        if a.alert:
            notify(warn, channel=CHANNEL)
        return 0
    if not lines:
        print(f"[nav_exdate_forecast] {asof}: không có sự kiện corp-action nào trong "
              f"≤{a.days_ahead_max} PHIÊN tới trên mã đang giữ.")
        return 0

    header = f"📆 **Corp-action sắp tới ≤{a.days_ahead_max} PHIÊN, mã đang giữ** ({asof}):"
    msg = "\n".join([header] + lines)
    print(msg)
    if a.alert:
        if _already_alerted_today(asof):
            print(f"[nav_exdate_forecast] {asof}: đã alert Discord/bus rồi hôm nay — bỏ qua lần "
                  f"chạy lại này (tránh trùng, §5).")
        else:
            notify(msg, channel=CHANNEL)
            bus("finding", f"nav-exdate-forecast {asof}",
                {"asof": asof, "n_events": len(events),
                 "tickers": sorted({e["ticker"] for e in events}),
                 "kinds": sorted({classify(e) for e in events})}, a.trace)
            _mark_alerted_today(asof)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
