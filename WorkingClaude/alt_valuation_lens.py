# -*- coding: utf-8 -*-
"""Lăng kính định giá THAY THẾ khi DCF trả NOT_COMPUTED (job Taylor_20260720_101638).

VÌ SAO CẦN: `dcf_valuation.py` loại hẳn nhóm tài chính (ngân hàng/bảo hiểm/chứng khoán) và
mọi tên có FCFE âm (capex-buildout: vận tải biển, cảng, hạ tầng viễn thông). Trước đây các
mã này hiện "DCF: NOT_COMPUTED (...)" rồi bỏ trống — đúng về mặt kỹ thuật nhưng để lại
khoảng trống định giá ở đúng những ngành mà lăng kính chuyên ngành ĐÃ CÓ SẴN trong session.

THUẦN HIỂN THỊ/THÔNG TIN: không chặn lệnh, không tham gia chọn mã, không đụng production
trading logic. Mọi lỗi → trả None, caller hiện dòng NOT_COMPUTED như cũ.

NGUỒN: `data/rating_8l.csv` — CANONICAL live snapshot (data_registry.md dòng 117), refresh
17:45 ICT mỗi ngày bởi `pt_8l_daily.sh`. Có sẵn route + ICB_Code + PB/ROE5Y/ROE_Trailing/
earn_yield/eveb_yield trong 1 file phẳng → 1 lần đọc, không gọi BQ.
⚠ Đây là SNAPSHOT HÔM NAY, KHÔNG phải point-in-time — chỉ dùng cho report LIVE (kế hoạch
T+1 / EOD / paper sleeve hôm nay), TUYỆT ĐỐI không join ngược vào backtest lịch sử.

BẢNG LĂNG KÍNH (độ tin cậy khai báo thẳng, không đánh đồng validated với fallback thô):
  BANK        Gordon justified P/B = (ROE5Y-0.05)/0.08      [validated] bank_compounder_screen.py
  SECURITIES  P/B band <1.8 + ROE_Trailing >0.08            [framework] securities_screen.py
  INSURANCE   P/B thô + ROE5Y                               [thô] chưa có lens chuyên biệt
  ICB 2773    vận tải biển — P/B trough <0.9                [framework] logistics_port_screen.py
  ICB 2777    cảng/hạ tầng — EV/EBITDA <8                   [framework] logistics_port_screen.py
  ICB 6535/2357 viễn thông-hạ tầng — EV/EBITDA <8           [framework] telecom_valuation_framework.md
  còn lại     8L fallback rộng: rating + earn_yield (1/PE)  [fallback] rating_8l.py
  không có dòng → None (caller hiện "chưa có lăng kính")
"""

import csv
import logging
import os

from trading_bot.config import WORKDIR

_log = logging.getLogger(__name__)

RATING_8L_CSV = os.path.join(WORKDIR, "data", "rating_8l.csv")

# Gordon: COE 13% (VN bank cost of equity), g 5% perpetual book-growth → mẫu số 0.08.
# Giữ nguyên hằng số của bank_compounder_screen.py để 2 nơi không bao giờ lệch nhau.
_COE, _GG = 0.13, 0.05

_SHIP_ICB, _PORT_ICB = 2773.0, 2777.0
_TELECOM_INFRA_ICB = {6535.0, 2357.0}      # FOX (viễn thông cố định), CTR (tower-co)

_cache = {}


def _load():
    """{ticker: row-dict} từ rating_8l.csv, cache theo mtime (file refresh 17:45 mỗi ngày)."""
    try:
        mtime = os.path.getmtime(RATING_8L_CSV)
    except OSError:
        return {}
    if _cache.get("_mtime") == mtime:
        return _cache["rows"]
    rows = {}
    try:
        with open(RATING_8L_CSV, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                t = (r.get("ticker") or "").strip().upper()
                if t:
                    rows[t] = r
    except Exception as exc:
        _log.warning("alt_valuation_lens: đọc %s lỗi: %s", RATING_8L_CSV, exc)
        return {}
    _cache.clear()
    _cache.update(_mtime=mtime, rows=rows)
    return rows


def _f(row, key):
    """float hoặc None (ô rỗng/NaN/không parse được → None, không raise)."""
    v = (row.get(key) or "").strip()
    if not v:
        return None
    try:
        x = float(v)
    except ValueError:
        return None
    return None if x != x else x            # loại NaN


def alt_lens(ticker):
    """Lăng kính định giá thay thế cho 1 ticker.

    Trả dict {lens, verdict, detail, confidence} — verdict ∈ {CHEAP, RICH, N/A};
    hoặc None khi không có dữ liệu (caller giữ nguyên dòng NOT_COMPUTED).
    Fail-safe tuyệt đối: mọi lỗi → None.
    """
    try:
        row = _load().get(str(ticker).strip().upper())
        if not row:
            return None
        route = (row.get("route") or "").strip().upper()
        icb = _f(row, "ICB_Code")
        pb = _f(row, "PB")
        roe5y = _f(row, "ROE5Y")
        roe_tr = _f(row, "ROE_Trailing")
        # rating_8l.csv lưu eveb_yield = 1/EVEB; ngưỡng "EVEB < 8" ⇔ eveb_yield > 0.125
        eveb_y = _f(row, "eveb_yield")
        eveb = (1.0 / eveb_y) if (eveb_y and eveb_y > 0) else None

        if route == "BANK":
            if pb is None or roe5y is None or pb <= 0:
                return None
            just_pb = (roe5y - _GG) / (_COE - _GG)
            return dict(
                lens="Gordon P/B (ngân hàng)",
                verdict="CHEAP" if pb < just_pb else "RICH",
                detail=f"P/B {pb:.2f} vs hợp lý {just_pb:.2f} (ROE5Y {roe5y * 100:.1f}%, COE 13%/g 5%)",
                confidence="đã validate (bank_compounder_screen)")

        if route == "SECURITIES":
            if pb is None or pb <= 0:
                return None
            cheap = pb < 1.8 and roe_tr is not None and roe_tr > 0.08
            roe_s = f"{roe_tr * 100:.1f}%" if roe_tr is not None else "n/a"
            return dict(
                lens="P/B band + ROE (chứng khoán)",
                verdict="CHEAP" if cheap else "RICH",
                detail=f"P/B {pb:.2f} (band cheap <1.8), ROE_TTM {roe_s} (cần >8%)",
                confidence="framework (screen gate, KHÔNG phải giá trị hợp lý)")

        if route == "INSURANCE":
            if pb is None or pb <= 0:
                return None
            roe_s = f"{roe5y * 100:.1f}%" if roe5y is not None else "n/a"
            return dict(
                lens="P/B thô (bảo hiểm)",
                verdict="N/A",
                detail=f"P/B {pb:.2f}, ROE5Y {roe_s}",
                confidence="THÔ — chưa có lens chuyên biệt (combined-ratio/EV không có trong BQ)")

        if icb == _SHIP_ICB:
            if pb is None or pb <= 0:
                return None
            return dict(
                lens="P/B trough (vận tải biển)",
                verdict="CHEAP" if pb < 0.9 else "RICH",
                detail=f"P/B {pb:.2f} (trough buy <0.9 — chu kỳ sâu, không có moat)",
                confidence="framework (logistics_port_screen)")

        if icb == _PORT_ICB or icb in _TELECOM_INFRA_ICB:
            if eveb is None or eveb <= 0:
                return None
            what = "cảng/hạ tầng" if icb == _PORT_ICB else "viễn thông-hạ tầng"
            return dict(
                lens=f"EV/EBITDA ({what})",
                verdict="CHEAP" if eveb < 8 else "RICH",
                detail=f"EV/EBITDA {eveb:.1f}x (cheap <8x, benchmark mature 4-8x)",
                confidence="framework (n nhỏ — cần margin/ROIC xác nhận kèm)")

        # fallback rộng: 8L. rating là GATE chất lượng (≤3 tốt), earn_yield=1/PE là trục value
        # có IC cao nhất trong 8L — nhưng đây KHÔNG phải giá trị hợp lý tuyệt đối.
        ey = _f(row, "earn_yield")
        rating = (row.get("rating") or "").strip()
        if ey is None and not rating:
            return None
        bits = []
        if rating:
            bits.append(f"8L rating {rating}/5")
        if ey is not None:
            bits.append(f"earnings yield {ey * 100:.1f}% (1/PE)")
        return dict(
            lens="8L (fallback rộng)",
            verdict="N/A",
            detail=", ".join(bits),
            confidence="FALLBACK — gate chất lượng + trục value, không phải giá trị hợp lý")

    except Exception as exc:
        _log.warning("alt_lens lỗi cho %s: %s", ticker, exc)
        return None


def format_alt_lens(ticker):
    """1 đoạn hiển thị nối sau dòng DCF NOT_COMPUTED. "" khi không có gì để nói."""
    d = alt_lens(ticker)
    if not d:
        return " → chưa có lăng kính định giá cho ngành này"
    icon = {"CHEAP": "🟢 ", "RICH": "🔴 "}.get(d["verdict"], "")
    verdict_s = f" — {d['verdict']}" if d["verdict"] != "N/A" else ""
    return (f" → thay thế: {icon}{d['lens']}: {d['detail']}{verdict_s}"
            f" [{d['confidence']}]")
