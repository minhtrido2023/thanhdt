#!/usr/bin/env python3
"""oshares_dcf.py — số cổ phiếu "sống" cho DCF + phân loại lệch OShares DIV (tiền) vs ISS (cổ phiếu).

Job `Taylor_20261030_094435` (user duyệt 30/10). Hai việc, một module, vì cùng một câu hỏi: "giá
đã pha loãng vì một sự kiện cổ phiếu, mà `ticker_financial.OShares` đã theo kịp chưa?".

1. `oshares_for(ticker, asof, fin_value)` — số CP cho `dcf_valuation.fair_value` khi bật
   `DCF_OSHARES_SOURCE=live`. Chính sách = ĐÚNG `oshares_pit.oshares_pit` (ưu tiên `oshares_live`,
   rơi về số quý ở mọi ca nó từ chối, cổng biên độ ×SANITY_FACTOR), không thêm gì.
   Bản đầu (job Taylor_20261030_094435) có thêm nhánh đưa ISS `announced` đã ex vào cache (vendor
   lật status trễ: TCB ISS 50% ex 2026-10-29). Đã BỎ ở R4 (job Taylor_20261030_155013): cột
   `ann_added` RỖNG ở cả 1.557 hàng đo ảnh hưởng 4 asof (`oshares_live_dcf_20261030/out_impact_*.csv`)
   — hai ca nó nhắm tới: TCB là ngân hàng (`fair_value` loại trước khi đọc số CP), NED không nằm
   trong universe đo ở asof 2026-10-29 ⇒ nhánh chưa từng có hiệu lực trên một FV nào.
   Hệ quả đã biết: trong cửa sổ vendor chưa lật status, `live` thấy số CP TRƯỚC sự kiện trong khi
   giá đã SAU sự kiện — đúng lớp sai số mà `fin` (số quý) cũng mắc, không tệ hơn. Khoá khung ex-date
   (R5, `dcf_valuation._live_oshares`) chỉ bắt lệch giữa ngày giá và asof, KHÔNG bắt trễ vendor.

2. `classify_oshares_gap(...)` — thay quy tắc lọc `Close/Price<0,93 & OShares<95% kỳ vọng`
   (`erp_domestic_v2_20261030/impact_v2.py` mục [4]) vốn coi MỌI điều chỉnh giá là pha loãng CP
   nên bắt nhầm cổ tức TIỀN (DGC/TV1). Kỳ vọng tỉ lệ OShares chỉ lấy từ ISS tạo CP cho cổ đông
   hiện hữu trong cửa sổ, đọc từ `tav2_bq.corporate_action`; DIV không tạo CP.
"""
from __future__ import annotations

import sys

from corp_action_lib import pricing_events

# ISS chắc chắn tạo CP cho cổ đông hiện hữu tại ex-date (không phụ thuộc đăng ký mua).
SHARE_CREATING_ISS = {"Trả Cổ tức bằng Cổ phiếu", "Cổ phiếu thưởng"}
RIGHTS_ISS = "Quyền mua CP cho Cổ đông hiện hữu"

# Dung sai giữ đúng quy tắc cũ (95% kỳ vọng) để so sánh được hai quy tắc trên cùng ngưỡng.
LAG_TOL = 0.05
# Ngưỡng "giá có điều chỉnh đáng kể" — chỉ dùng để gắn nhãn UNEXPLAINED_PRICE_ADJ, không quyết cờ lag.
ADJ_TRIGGER = 0.93


# ─────────────────────────────────────────────────────────────── 1. số CP sống cho DCF
def fetch_cache(tickers, until):
    """(quarters, corp_executed) — cache `oshares_live`, một lần BQ cho mọi asof <= until. None nếu lỗi."""
    from oshares_live import _fetch
    try:
        tickers = sorted(set(tickers))
        return _fetch(tickers, until)
    except Exception as e:                                  # noqa: BLE001 — fail-safe về số quý
        # STDERR, không phải stdout: send_plan_report.sh lấy dòng đầu stdout của khối Python làm STATUS
        print(f"[oshares_dcf] fetch_cache FAILED ({type(e).__name__}: {e}) -> dùng OShares quý", file=sys.stderr)
        return None


_CACHE = {"tickers": frozenset(), "until": None, "data": None}


def prime(tickers, until):
    """Nạp sẵn cache cho một lô mã (backtest/đo toàn universe) — tránh 3 truy vấn BQ mỗi lần gọi."""
    _CACHE.update(tickers=frozenset(tickers), until=until, data=fetch_cache(tickers, until))


def oshares_for(ticker, asof, fin_value):
    """Bản ghi `oshares_pit` cho một mã. Tổng: mọi lỗi ⇒ số quý."""
    from oshares_pit import oshares_pit
    asof = str(asof)[:10]
    try:
        if _CACHE["data"] is not None and ticker in _CACHE["tickers"] and asof <= _CACHE["until"]:
            cache = _CACHE["data"]
        else:
            cache = fetch_cache([ticker], asof)
        if cache is None:
            raise RuntimeError("không có cache corp-action")
        return oshares_pit([ticker], asof, {ticker: fin_value}, cache=cache)[ticker]
    except Exception as e:                                  # noqa: BLE001 — fail-safe về số quý
        return {"ticker": ticker, "value": fin_value, "source": "ticker_financial",
                "reason": f"oshares_dcf lỗi ({type(e).__name__}: {e}) ⇒ giữ số quý",
                "method": "ERROR", "rel_diff": None, "live_value": None}


# ─────────────────────────────────────────────────────────────── 2. phân loại lệch OShares
def _dedup(events):
    seen, out = set(), []
    for e in sorted(events, key=lambda r: (r.get("exright_date") or "", r.get("public_date") or "")):
        key = (e.get("exright_date"), e.get("event_code"), (e.get("issue_method_name_vi") or "").strip(),
               str(e.get("exercise_ratio")))
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


def classify_oshares_gap(oshares_ratio, events, adj_factor=None, tol=LAG_TOL):
    """(verdict, detail) — OShares có theo kịp các sự kiện CỔ PHIẾU trong cửa sổ không? Thuần.

    `events` = mọi DIV/ISS của MỘT mã có ex-date trong cửa sổ (đã lọc bỏ `not_executed`).
    `oshares_ratio` = OShares cuối / OShares đầu cửa sổ. `adj_factor` = Close/Price đầu cửa sổ
    (tuỳ chọn, chỉ để gắn nhãn).

    Verdict (chỉ `OSHARES_LAG` là cờ lỗi số CP):
      OSHARES_LAG          có ISS tạo CP, OShares tăng < (1−tol) × Π(1+ratio)
      ISS_REFLECTED        có ISS tạo CP và OShares đã theo kịp
      ISS_UNSIZED          có ISS tạo CP nhưng không ratio/volume ⇒ không kết luận được
      RIGHTS_PENDING       chỉ có quyền mua — CP mới tuỳ đăng ký, OShares chưa đổi là bình thường
      CASH_DIV             giá điều chỉnh nhưng chỉ vì cổ tức tiền
      UNEXPLAINED_PRICE_ADJ  giá điều chỉnh ≥ (1−ADJ_TRIGGER) mà không có DIV/ISS nào (việc data-ops)
      NO_EVENT             không sự kiện, giá không điều chỉnh đáng kể
    """
    ev = _dedup(events)
    share = [e for e in ev if e.get("event_code") == "ISS"
             and (e.get("issue_method_name_vi") or "").strip() in SHARE_CREATING_ISS]
    rights = [e for e in ev if e.get("event_code") == "ISS"
              and (e.get("issue_method_name_vi") or "").strip() == RIGHTS_ISS]
    divs = [e for e in ev if e.get("event_code") == "DIV"]
    detail = {"n_share_iss": len(share), "n_rights": len(rights), "n_div": len(divs),
              "oshares_ratio": oshares_ratio, "adj_factor": adj_factor}
    if share:
        expected = 1.0
        for e in share:
            r = e.get("exercise_ratio")
            if r is None or float(r) <= 0:
                return "ISS_UNSIZED", detail
            expected *= 1.0 + float(r)
        detail["expected_ratio"] = expected
        if oshares_ratio is None:
            return "ISS_UNSIZED", detail
        detail["fill"] = oshares_ratio / expected
        return ("OSHARES_LAG" if oshares_ratio < (1.0 - tol) * expected else "ISS_REFLECTED"), detail
    if rights:
        return "RIGHTS_PENDING", detail
    adjusted = adj_factor is not None and adj_factor < ADJ_TRIGGER
    if divs:
        return "CASH_DIV", detail
    return ("UNEXPLAINED_PRICE_ADJ" if adjusted else "NO_EVENT"), detail


def oshares_gap_check(frame, d0, d1):
    """{ticker: (verdict, detail)} cho các mã trong `frame` (cột ticker, Close_d0, Price_d0,
    OShares_d0, OShares_d1). Đọc sự kiện (d0, d1] qua `corp_action_lib.pricing_events` (gồm
    `announced`, bỏ `not_executed`) — một truy vấn BQ cho cả lô."""
    tickers = sorted(set(frame["ticker"]))
    evs = pricing_events(tickers, since=d0, until=d1, codes=("DIV", "ISS"))
    by = {}
    for e in evs:
        if (e.get("public_date") or "9999") <= d1:
            by.setdefault(e["ticker"], []).append(e)
    out = {}
    for r in frame.itertuples(index=False):
        ratio = (r.OShares_d1 / r.OShares_d0) if r.OShares_d0 and r.OShares_d0 > 0 else None
        adj = (r.Close_d0 / r.Price_d0) if r.Price_d0 and r.Price_d0 > 0 else None
        out[r.ticker] = classify_oshares_gap(ratio, by.get(r.ticker, []), adj)
    return out
