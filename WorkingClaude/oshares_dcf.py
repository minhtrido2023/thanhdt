#!/usr/bin/env python3
"""oshares_dcf.py — số cổ phiếu "sống" cho DCF + phân loại lệch OShares DIV (tiền) vs ISS (cổ phiếu).

Job `Taylor_20261030_094435` (user duyệt 30/10). Hai việc, một module, vì cùng một câu hỏi: "giá
đã pha loãng vì một sự kiện cổ phiếu, mà `ticker_financial.OShares` đã theo kịp chưa?".

1. `oshares_for(ticker, asof, fin_value)` — số CP cho `dcf_valuation.fair_value` khi bật
   `DCF_OSHARES_SOURCE=live`. Chính sách = `oshares_pit.oshares_pit` (ưu tiên `oshares_live`,
   rơi về số quý ở mọi ca nó từ chối, cổng biên độ ×SANITY_FACTOR), cộng ĐÚNG MỘT bổ sung:
   ISS cổ tức-bằng-CP / thưởng CP còn `event_status="announced"` mà ex-date ĐÃ QUA được đưa vào
   như ISS đã thực hiện. Lý do: vendor lật `announced`→`executed` trễ (TCB ISS 50% ex 2026-10-29
   vẫn `announced` lúc 30/10 16:4x ICT, `issue_volumn=0`), và `oshares_live._fetch` chỉ đọc
   `executed` ⇒ không có bổ sung này thì `oshares_live` trả 7.086.240.414 cho TCB y như số quý.
   PIT: chỉ nhận dòng có `exright_date <= asof` VÀ `public_date <= asof`; chỉ 2 phương thức chắc
   chắn tạo CP cho cổ đông hiện hữu (không nhận quyền mua — CP mới chỉ có khi được mua hết).
   Không sửa `oshares_live` (module đã qua 4 vòng skeptic): bổ sung đi vào bằng `_cache`.

2. `classify_oshares_gap(...)` — thay quy tắc lọc `Close/Price<0,93 & OShares<95% kỳ vọng`
   (`erp_domestic_v2_20261030/impact_v2.py` mục [4]) vốn coi MỌI điều chỉnh giá là pha loãng CP
   nên bắt nhầm cổ tức TIỀN (DGC/TV1). Kỳ vọng tỉ lệ OShares chỉ lấy từ ISS tạo CP cho cổ đông
   hiện hữu trong cửa sổ, đọc từ `tav2_bq.corporate_action`; DIV không tạo CP.
"""
from __future__ import annotations

from corp_action_lib import TABLE, bq, pricing_events

# ISS chắc chắn tạo CP cho cổ đông hiện hữu tại ex-date (không phụ thuộc đăng ký mua).
SHARE_CREATING_ISS = {"Trả Cổ tức bằng Cổ phiếu", "Cổ phiếu thưởng"}
RIGHTS_ISS = "Quyền mua CP cho Cổ đông hiện hữu"

# Dung sai giữ đúng quy tắc cũ (95% kỳ vọng) để so sánh được hai quy tắc trên cùng ngưỡng.
LAG_TOL = 0.05
# Ngưỡng "giá có điều chỉnh đáng kể" — chỉ dùng để gắn nhãn UNEXPLAINED_PRICE_ADJ, không quyết cờ lag.
ADJ_TRIGGER = 0.93


# ─────────────────────────────────────────────────────────────── 1. số CP sống cho DCF
def _fetch_announced(tickers, until):
    tk = ",".join(f'"{t}"' for t in tickers)
    meth = ",".join(f'"{m}"' for m in sorted(SHARE_CREATING_ISS))
    rows = bq(f"""
        SELECT ticker, event_code, CAST(exright_date AS STRING) exright_date,
               CAST(effective_date AS STRING) effective_date,
               CAST(listing_date AS STRING) listing_date,
               exercise_ratio, issue_volumn, issue_method_name_vi, shares_delta,
               shares_total_after, SUBSTR(event_title_vi, 1, 70) AS title,
               CAST(public_date AS STRING) public_date
        FROM `{TABLE}`
        WHERE ticker IN ({tk}) AND event_status = "announced" AND event_code = "ISS"
          AND issue_method_name_vi IN ({meth})
          AND exright_date IS NOT NULL AND exright_date <= DATE "{until}"
        ORDER BY ticker, exright_date
    """)
    return rows


def fetch_cache(tickers, until):
    """(quarters, corp_executed, announced) — một lần BQ cho mọi asof <= until. None nếu lỗi."""
    from oshares_live import _fetch
    try:
        tickers = sorted(set(tickers))
        q, corp = _fetch(tickers, until)
        return q, corp, _fetch_announced(tickers, until)
    except Exception as e:                                  # noqa: BLE001 — fail-safe về số quý
        print(f"[oshares_dcf] fetch_cache FAILED ({type(e).__name__}: {e}) -> dùng OShares quý")
        return None


# Trễ lật status của vendor tính bằng NGÀY (reload ~22:2x ICT đêm ex-date). Dòng `announced` đã ex
# lâu hơn ngưỡng này gần như chắc là dòng mồ côi (BKC còn 2 ISS `announced` từ 2012-04-26) ⇒ không
# nhận: tới lúc đó AIS/dòng quý đã phải bắt kịp, và một sự kiện có thể đã huỷ không được đẩy vào cổng.
PROMOTE_MAX_AGE_DAYS = 45


def _clip(cache, asof):
    """Cache `oshares_live` cho đúng `asof`: thêm ISS announced đã biết (public_date<=asof), đã ex
    (exright<=asof) và ex chưa quá PROMOTE_MAX_AGE_DAYS; bỏ dòng trùng một ISS executed cùng
    (mã, ex-date, phương thức). Dòng thêm vào chỉ được LĂN nếu ex sau neo — `oshares_at` quyết."""
    from datetime import date, timedelta
    q, corp, ann = cache
    floor = (date.fromisoformat(asof) - timedelta(days=PROMOTE_MAX_AGE_DAYS)).isoformat()
    have = {(c["ticker"], c["exright_date"], c.get("issue_method_name_vi"))
            for c in corp if c["event_code"] == "ISS"}
    extra = [a for a in ann
             if floor <= a["exright_date"] <= asof and (a.get("public_date") or "9999") <= asof
             and (a["ticker"], a["exright_date"], a.get("issue_method_name_vi")) not in have]
    return q, corp + extra, extra


_CACHE = {"tickers": frozenset(), "until": None, "data": None}


def prime(tickers, until):
    """Nạp sẵn cache cho một lô mã (backtest/đo toàn universe) — tránh 3 truy vấn BQ mỗi lần gọi."""
    _CACHE.update(tickers=frozenset(tickers), until=until, data=fetch_cache(tickers, until))


def oshares_for(ticker, asof, fin_value):
    """Bản ghi `oshares_pit` (+ `announced_added` = ex-date các ISS announced đã đưa vào cache) cho một mã. Tổng: mọi lỗi ⇒ số quý."""
    from oshares_pit import oshares_pit
    asof = str(asof)[:10]
    try:
        if _CACHE["data"] is not None and ticker in _CACHE["tickers"] and asof <= _CACHE["until"]:
            cache = _CACHE["data"]
        else:
            cache = fetch_cache([ticker], asof)
        if cache is None:
            raise RuntimeError("không có cache corp-action")
        clipped = _clip(cache, asof)
        rec = oshares_pit([ticker], asof, {ticker: fin_value}, cache=clipped[:2])[ticker]
        rec["announced_added"] = [e["exright_date"] for e in clipped[2] if e["ticker"] == ticker]
        return rec
    except Exception as e:                                  # noqa: BLE001 — fail-safe về số quý
        return {"ticker": ticker, "value": fin_value, "source": "ticker_financial",
                "reason": f"oshares_dcf lỗi ({type(e).__name__}: {e}) ⇒ giữ số quý",
                "method": "ERROR", "rel_diff": None, "live_value": None,
                "announced_added": []}


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
