#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mốc so sánh "gửi tiết kiệm cùng kỳ" cho bảng hiệu suất (Luồng B live-gap, user duyệt 2026-11-12).

Lãi = bậc thang THEO NGÀY của `deposit_rate_vn.effective_deposit_events_df()` (max(Big-4 12T online,
CCTG 12T Big-4 cao nhất), point-in-time), cộng dồn LÃI ĐƠN actual/365 trên [from_date, to_date) —
cùng quy ước GĐ0 (`research/live_gap_phase0_20261112/hurdle_pit.py`; module này là bản nâng cấp,
KHÔNG đổi công thức). Không quy năm cho kỳ < 365 ngày (chính sách 2026-10-10) — dùng cửa
`nav_period_returns.annualize_or_null`. KHÔNG tính thuế (nói về thuế = chưa xác minh, không nêu).

`report_savings(from, to, tr_return_pct)` KHÔNG BAO GIỜ ném lỗi: thiếu số ⇒ ô None + `reason`.
"""
import datetime as dt
import os
import sys

WC_ROOT = os.environ.get("WC_ROOT", "/home/trido/thanhdt/WorkingClaude")
DAYS_YEAR = 365.0                  # mẫu số lãi đơn (act/365)
MAX_RATE_AGE_DAYS = 200            # mốc lãi cũ hơn thế (so với to_date) ⇒ không công bố
BASIS = ("lãi tiền gửi kỳ hạn 12 tháng (max: Big-4 niêm yết online, CCTG 12T cao nhất Big-4), "
         "lãi đơn actual/365, chưa tính thuế")
FOOTNOTE = ("Gửi tiết kiệm cùng kỳ: " + BASIS + ". Là mốc tham chiếu thượng cận (rút trước hạn chỉ "
            "hưởng lãi không kỳ hạn).")
ANCHOR_WARNING = ("Kỳ này có đoạn lãi suất lấy từ các mốc neo thủ công 2011→2026-06 "
                  "(không phải chuỗi công bố theo ngày) — số tiết kiệm mang tính tham chiếu.")

_CACHE = {}


def _series():
    """(DataFrame time, rate_pct) bậc thang + ngày mốc neo cuối. Cache theo tiến trình."""
    if "s" not in _CACHE:
        if WC_ROOT not in sys.path:
            sys.path.insert(0, WC_ROOT)
        import deposit_rate_vn as D
        ev = D.effective_deposit_events_df().dropna().sort_values("time").reset_index(drop=True)
        last_anchor = max(dt.date.fromisoformat(str(t)[:10]) for t, _ in D.DEPOSIT_EVENTS)
        _CACHE["s"] = (ev, last_anchor)
    return _CACHE["s"]


def _d(x):
    return x if isinstance(x, dt.date) and not isinstance(x, dt.datetime) else \
        dt.date.fromisoformat(str(x)[:10])


def accrual_pct(from_date, to_date, ev=None):
    """Lãi đơn tích luỹ (%) trên [from_date, to_date). Ném ValueError nếu thiếu mốc lãi phủ kỳ."""
    a, b = _d(from_date), _d(to_date)
    if ev is None:
        ev = _series()[0]
    if b <= a:
        raise ValueError(f"kỳ {a}→{b} không dương")
    times = [t.date() for t in ev["time"]]
    rates = list(ev["deposit_rate"])
    if not times or times[0] > a:
        raise ValueError(f"chuỗi lãi bắt đầu {times[0] if times else None} sau from_date {a}")
    total = 0.0
    for i, (t, r) in enumerate(zip(times, rates)):
        nxt = times[i + 1] if i + 1 < len(times) else dt.date.max
        lo, hi = max(t, a), min(nxt, b)
        if hi > lo:
            total += float(r) * (hi - lo).days
    age = (b - max(t for t in times if t <= b)).days
    return total / DAYS_YEAR, age


def report_savings(from_date, to_date, tr_return_pct=None, ev=None) -> dict:
    """Khối `savings` của một kỳ. `tr_return_pct` = `return_pct` TWR của kỳ (nav_period_returns)."""
    out = {"from_date": str(from_date)[:10], "to_date": str(to_date)[:10], "hurdle_pct": None,
           "excess_vs_savings_pp": None, "rate_basis": BASIS, "footnote": FOOTNOTE,
           "anchor_warning": None, "annualized_pct": None, "status": "ok"}
    try:
        a, b = _d(from_date), _d(to_date)
        days = (b - a).days
        out["days"] = days
        if ev is None:
            ev, last_anchor = _series()
        else:
            last_anchor = dt.date(2026, 6, 1)
        h, age = accrual_pct(a, b, ev)
        if age > MAX_RATE_AGE_DAYS:
            raise ValueError(f"mốc lãi gần nhất cách to_date {age} ngày > {MAX_RATE_AGE_DAYS}")
        out["hurdle_pct"] = round(h, 3)
        out["rate_age_days"] = age
        if a <= last_anchor:                      # cờ code; báo cáo chỉ hiện khi true
            out["anchor_warning"] = ANCHOR_WARNING
        if tr_return_pct is not None:
            out["excess_vs_savings_pp"] = round(tr_return_pct - h, 3)
        from nav_period_returns import annualize_or_null
        out["annualized_pct"], note = annualize_or_null(1 + h / 100.0, days)
        if note:
            out["annualized_note"] = note
    except Exception as exc:                      # noqa: BLE001
        out.update({"hurdle_pct": None, "excess_vs_savings_pp": None, "annualized_pct": None,
                    "status": "unavailable", "reason": f"{type(exc).__name__}: {exc}"})
    return out


def savings_fn():
    """Hàm `(from, to, return_pct) -> dict` cho `nav_period_returns` (đường cảnh báo, không ném)."""
    return lambda a, b, r=None: report_savings(a, b, r)
