# -*- coding: utf-8 -*-
"""Helper DCF lens dùng chung cho đường REPORT/due-diligence (Pha 2, 2026-07-14).

`_dcf_check_for_order` / `format_dcf_check` / `log_dcf_history` — caller: send_plan_report.sh,
eod_trading_report.sh, trading_bot/due_diligence.py, dc_book_waterfall_paper.py.

Lớp strategy V2.3 cũ (StrategyBase/V23Strategy/REGISTRY/get_strategy, entry bot_prepare_plan.py)
đã GỠ 2026-09-13 (cq-20260913-remove-v23, user duyệt): 0/148 plan 2026 dùng đường đó, và chạy
bot_prepare_plan.py không --account ghi đè plan đã duyệt của SpaceX/ZaloPay. Bản cũ nằm trong
git history; plan live do DollarBill lập (strategy "V2.4").
"""

import csv
import datetime as dt
import os
import logging

from .config import WORKDIR

_log = logging.getLogger(__name__)

# ---------------------------------------------------------------- DCF check (Pha 2, 2026-07-14)

_DCF_SENS_KEYS = ["r-1%", "r+1%", "g-2%", "g+2%"]

DCF_HISTORY_CSV = os.path.join(WORKDIR, "data", "dcf_lens_history.csv")
_DCF_HISTORY_COLS = ["logged_at", "as_of", "ticker", "source", "status",
                     "fair_value_ps", "price", "margin_of_safety", "robust", "conglomerate"]


def _dcf_is_conglomerate(ticker):
    """Cờ đa ngành/holding (chỉ để cảnh báo hiển thị). Fail-safe: import lỗi → False."""
    try:
        import sys as _sys
        if WORKDIR not in _sys.path:
            _sys.path.insert(0, WORKDIR)
        import dcf_valuation as _dcf
        return _dcf.is_conglomerate(ticker)
    except Exception:
        return False


def _dcf_check_for_order(ticker, price, asof):
    """Tính dcf_check dict cho 1 BUY order (non-financial, informational only).

    Đọc từ data/bq_cache/ticker_financial.parquet (local parquet, không gọi BQ live).
    Fail-safe: mọi lỗi đều trả NOT_COMPUTED với reason="dcf_error:...", KHÔNG raise.

    robust = True khi MoS KHÔNG đổi dấu qua toàn bộ sensitivity box
             (±1pp discount rate, ±2pp growth) — ngưỡng thống nhất theo Spyros/họp round-table.
    """
    try:
        import sys as _sys
        if WORKDIR not in _sys.path:
            _sys.path.insert(0, WORKDIR)
        import dcf_valuation as _dcf

        res = _dcf.fair_value(ticker, asof, price=price)

        if not res["ok"]:
            reason = res.get("reason", "unknown")
            if "financial-sector" in reason:
                nc_reason = "financial_sector_excluded"
            elif "positive FCFE" in reason or "FCFE <= 0" in reason:
                nc_reason = "fcfe_negative_buildout"
            elif "insufficient financial" in reason:
                nc_reason = "insufficient_history"
            else:
                nc_reason = reason[:80]
            return {"status": "NOT_COMPUTED", "margin_of_safety": None,
                    "robust": False, "reason": nc_reason,
                    "conglomerate": _dcf.is_conglomerate(ticker), "as_of": str(asof)[:10]}

        mos = res.get("margin_of_safety")
        status = "CHEAP" if (mos is not None and mos > 0) else "RICH"

        # robust: kiểm tra MoS không đổi dấu qua sensitivity box
        sens = res.get("sensitivity", {})
        robust = False
        if mos is not None and price and price > 0:
            mos_positive = mos > 0
            sens_signs = []
            for k in _DCF_SENS_KEYS:
                s = sens.get(k, {})
                fv_s = s.get("fv")
                if fv_s and fv_s > 0:
                    mos_s = (fv_s - price) / fv_s
                    sens_signs.append(mos_s > 0)
            robust = bool(sens_signs) and all(sg == mos_positive for sg in sens_signs)

        # fair_value_ps + price: HIỂN THỊ ONLY (user directive 2026-07-15) — neo số tuyệt đối
        # cho quyết định mua/bán + cho phép so giá dự báo vs giá thị trường sau này. KHÔNG
        # tham gia logic status/robust/gate nào. price = đúng giá MoS được tính trên đó, nên
        # dòng hiển thị luôn tự nhất quán mà không cần caller truyền lại giá.
        fv_ps = res.get("fair_value_ps")
        return {
            "status": status,
            "margin_of_safety": round(float(mos), 4) if mos is not None else None,
            "robust": robust,
            "fair_value_ps": round(float(fv_ps), 0) if fv_ps is not None else None,
            "price": round(float(price), 0) if price is not None else None,
            # đa ngành/holding: CẢNH BÁO hiển thị (user directive 2026-07-15) — DCF 1-dòng-tiền
            # có thể vô nghĩa với cấu trúc nhiều mảng. KHÔNG loại khỏi DCF, không đụng
            # status/robust/gate — y hệt fair_value_ps, thuần hiển thị.
            "conglomerate": _dcf.is_conglomerate(ticker),
            "as_of": str(asof)[:10],
        }

    except Exception as exc:
        _log.warning("DCF check lỗi cho %s: %s", ticker, exc)
        return {"status": "NOT_COMPUTED", "margin_of_safety": None,
                "robust": False, "reason": f"dcf_error: {str(exc)[:80]}",
                "conglomerate": _dcf_is_conglomerate(ticker), "as_of": str(asof)[:10]}

def _format_alt_lens(ticker):
    """Lăng kính định giá thay thế khi DCF NOT_COMPUTED. Fail-safe: import/lỗi → ""."""
    if not ticker:
        return ""
    try:
        import sys as _sys
        if WORKDIR not in _sys.path:
            _sys.path.insert(0, WORKDIR)
        from alt_valuation_lens import format_alt_lens
        return format_alt_lens(ticker)
    except Exception as exc:
        _log.warning("alt lens lỗi cho %s: %s", ticker, exc)
        return ""


def format_dcf_check(dcf, side="buy", has_override=False, ticker=None):
    """1 dòng hiển thị chuẩn cho dcf_check dict (Pha 2) — dùng chung mọi report echo
    (send_plan_report / eod_trading_report / paper sleeve). Informational only.
    Trả "" khi dcf rỗng/None — caller bỏ dòng, không hiện gì.

    ticker: khi có, NOT_COMPUTED được nối thêm LĂNG KÍNH ĐỊNH GIÁ THAY THẾ theo ngành
    (job Taylor_20260720_101638) thay vì để trống. Bỏ trống ticker → dòng cũ nguyên vẹn."""
    if not dcf or not isinstance(dcf, dict):
        return ""
    status = dcf.get("status")
    # đa ngành/holding: cảnh báo NGAY trên dòng có con số, không giấu trong footnote
    cong_s = " ⚠ đa ngành — DCF gộp 1 dòng tiền, có thể không phản ánh đúng" \
        if dcf.get("conglomerate") else ""
    if status == "NOT_COMPUTED":
        return (f"DCF: NOT_COMPUTED ({dcf.get('reason', '?')})"
                + _format_alt_lens(ticker or dcf.get("ticker")))
    mos = dcf.get("margin_of_safety")
    mos_s = f"{mos * 100:+.1f}%" if isinstance(mos, (int, float)) else "n/a"
    robust_s = "robust" if dcf.get("robust") else "không robust"
    icon = "🟢" if status == "CHEAP" else "🔴"
    # giá trị hợp lý tuyệt đối — bỏ qua khi dcf cũ (plan trước 2026-07-15) không có field
    fv, px = dcf.get("fair_value_ps"), dcf.get("price")
    fv_s = ""
    if isinstance(fv, (int, float)):
        fv_s = f"giá trị hợp lý ~{fv:,.0f}đ"
        if isinstance(px, (int, float)):
            fv_s += f" vs giá {px:,.0f}đ"
        fv_s += ", "
    out = f"{icon} DCF: {status} ({fv_s}MoS {mos_s}, {robust_s})"
    if status == "RICH" and dcf.get("robust") and str(side).lower() == "buy":
        out += " ⚠" if has_override else " ⚠ cần dcf_override_reason"
    return out + cong_s


def log_dcf_history(ticker, dcf, source, asof=None):
    """Ghi 1 dòng vào data/dcf_lens_history.csv (append-only) mỗi lần một report tính dcf_check.

    Mục đích (user directive 2026-07-15): tích luỹ fair_value_ps đã dự báo + giá thị trường lúc
    tính, để SAU NÀY đối chiếu với giá thật tại T+1M/3M/6M và đánh giá lăng kính DCF có hữu ích
    không. Đây thuần là BƯỚC GHI DỮ LIỆU — không phân tích, không quyết định gì.

    Chỉ gọi từ đường REPORT (send_plan_report / eod_trading_report / dc_book_waterfall_paper),
    KHÔNG từ đường dựng plan: plan đã duyệt không được ghi ngược (rủi ro, theo dispatch).
    Fail-safe: mọi lỗi → bỏ qua im lặng (log warning), report không bao giờ vì dòng này mà hỏng.
    """
    try:
        if not dcf or not isinstance(dcf, dict):
            return
        row = {
            "logged_at": dt.datetime.now().isoformat(timespec="seconds"),
            "as_of": dcf.get("as_of") or (str(asof)[:10] if asof else ""),
            "ticker": ticker,
            "source": source,
            "status": dcf.get("status"),
            "fair_value_ps": dcf.get("fair_value_ps"),
            "price": dcf.get("price"),
            "margin_of_safety": dcf.get("margin_of_safety"),
            "robust": dcf.get("robust"),
            "conglomerate": dcf.get("conglomerate"),
        }
        os.makedirs(os.path.dirname(DCF_HISTORY_CSV), exist_ok=True)
        write_header = not os.path.exists(DCF_HISTORY_CSV)
        with open(DCF_HISTORY_CSV, "a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=_DCF_HISTORY_COLS)
            if write_header:
                w.writeheader()
            w.writerow(row)
    except Exception as exc:
        _log.warning("log_dcf_history lỗi cho %s: %s", ticker, exc)
