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

ACTIVE_NAV_GLOB = os.path.join(WC_ROOT, "data", "execution_logs", "active_nav_*.json")
CHANNEL = "trading_daily"
DAYS_AHEAD_MAX = 1   # hôm nay (0) hoặc ngày mai (1) — cùng cửa sổ PRICE_XCHECK sẽ chạm tối nay/mai


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


def relevant_events(snap, days_ahead_max=DAYS_AHEAD_MAX):
    """Sự kiện trong `upcoming_events_held` rơi vào cửa sổ `days_ahead<=days_ahead_max` —
    CHÍNH XÁC field snapshot đã tính sẵn (Lớp 6 của corp_action_daily.py), không tính lại."""
    return [e for e in (snap or {}).get("upcoming_events_held") or []
            if isinstance(e.get("days_ahead"), int) and e["days_ahead"] <= days_ahead_max]


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


def build_event_line(event, positions_by_account):
    tk = event["ticker"]
    kind = classify(event)
    holders = _holders_for(tk, positions_by_account)
    day_word = "HÔM NAY" if event["days_ahead"] == 0 else f"NGÀY MAI ({event['date']})"
    # date_field phân biệt "chốt quyền/ex-right" (DIV/ISS thường) với "hiệu lực" (AIS chính thức
    # hoá số CP) — dùng đúng field snapshot đã gắn theo từng dòng, không đoán chung một chữ.
    verb = "hiệu lực" if event.get("date_field") == "effective_date" else "ex-right"
    when = f"{verb} {day_word}"
    who = ", ".join(f"{lb} {h['qty']:,}cp" for lb, h in holders.items()) or "(không xác định được vị thế)"

    if kind == "CASH_DIV":
        vps = event.get("value_per_share")
        pct = None
        for h in holders.values():
            if h.get("price"):
                pct = float(vps) / float(h["price"]) * 100
                break
        pct_txt = f" (~{_fmt_pct(pct)} giá tham chiếu)" if pct is not None else ""
        return (f"💰 **{tk}** {when} — cổ tức tiền mặt {float(vps):,.0f}đ/cp{pct_txt}. "
                f"Tối nay/mai NAV sẽ thấy broker HẠ marketPrice đúng khoản này — ĐÂY LÀ KỲ VỌNG, "
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
        return (f"🚨 **{tk}** {event['event_code']}{method}{ratio_txt}, {when}{drop_txt}. "
                f"Broker sẽ đổi CẢ giá LẪN khối lượng cùng lúc — `daily_nav_snapshot.py` "
                f"PRICE_XCHECK **SẼ CHẶN NAV** (đúng thiết kế, không phải bug) cho tới khi broker "
                f"đồng bộ hoặc người backfill bằng `--from-raw`. CẦN NGƯỜI theo dõi khi chạy NAV "
                f"{when.lower()}. Đang giữ: {who}.")

    return None  # INFO — không tạo dòng cảnh báo NAV (xem docstring)


def build_report(asof=None, days_ahead_max=DAYS_AHEAD_MAX):
    """([dòng str], snap|None, [event dict])."""
    asof = asof or today_ict()
    snap = _read_json(snapshot_path(asof))
    if snap is None:
        return [], None, []
    events = relevant_events(snap, days_ahead_max)
    positions = read_active_nav_positions()
    lines = [ln for ln in (build_event_line(e, positions) for e in events) if ln]
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
    bits = [" CẢNH BÁO CORP-ACTION ≤1 NGÀY TỚI trên mã đang giữ (nav_exdate_forecast.py, đọc lại "
            "corp_action_daily — KHÔNG tự suy diễn thêm, chỉ nhắc để không nhầm biến động giá dự "
            "kiến này với tín hiệu thị trường):"]
    for e in mine:
        kind = classify(e)
        tag = "cổ tức tiền mặt (giá giảm dự kiến, bình thường)" if kind == "CASH_DIV" else \
              "sự kiện CỔ PHIẾU (giá+KL đổi, NAV có thể bị chặn tối nay/mai)" if kind == "SHARE_EVENT" else "AIS"
        bits.append(f" • {e['ticker']} {e['event_code']} {e['date']} — {tag}.")
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
        print(f"[nav_exdate_forecast] không có snapshot corp_action_daily cho {asof} — "
              f"{os.path.relpath(snapshot_path(asof), WC_ROOT)} chưa tồn tại.")
        return 0
    if not lines:
        print(f"[nav_exdate_forecast] {asof}: không có sự kiện corp-action nào trong "
              f"≤{a.days_ahead_max} ngày tới trên mã đang giữ.")
        return 0

    header = f"📆 **Corp-action sắp tới ≤{a.days_ahead_max} ngày, mã đang giữ** ({asof}):"
    msg = "\n".join([header] + lines)
    print(msg)
    if a.alert:
        notify(msg, channel=CHANNEL)
        bus("finding", f"nav-exdate-forecast {asof}",
            {"asof": asof, "n_events": len(events),
             "tickers": sorted({e["ticker"] for e in events}),
             "kinds": sorted({classify(e) for e in events})}, a.trace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
