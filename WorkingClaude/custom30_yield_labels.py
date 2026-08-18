# -*- coding: utf-8 -*-
"""custom30_yield_labels.py — nhãn QUAN SÁT `yield_floor` cho rổ custom30 (Phase 1 Option C).

**DISPLAY_ONLY, THUẦN QUAN SÁT.** Module này KHÔNG chọn mã, KHÔNG đổi weight/cap, KHÔNG gate.
Nó chỉ gắn 2 cột nhãn vào rổ ĐÃ ĐƯỢC CHỌN XONG (`custom30_history.py`) để có dữ liệu thật cho
quyết định B ở kỳ review 2027-02-10 (chương trình `yield_floor_custom30v_observe` trong
`mike/kb/paper_programs_registry.json`).

Ngữ nghĩa nhãn = ĐÚNG `trading_bot/due_diligence._yield_floor()` (đừng chế lại): cửa sổ 365 ngày
lịch, dedup DIV theo (ticker, exright_date, dividend_year, dividend_stage_vi) lấy `public_date`
mới nhất, giá tham chiếu raw `COALESCE(Price, Close)`, `prox = px / (div0 / (dep/100))`,
ngưỡng [0,97; 1,03], ngân hàng ICB 8355 loại khỏi diễn giải.

**Vì sao BATCH chứ không gọi `_yield_floor()` cho từng mã** (research phase 1, FINDINGS §5.2):
`_yield_floor()` là 1 query BQ/mã, cache chỉ trong-process, còn `custom30_history.py` dựng lại
TOÀN BỘ ~50 kỳ rebal MỖI NGÀY ⇒ gọi per-ticker = ~3.000 query/ngày thêm vào chain 15:30. Bản
batch này = 2 query (đo thật: leg giá ~77 MB/lần). Tương đương đã KIỂM CHỨNG, không phải khẳng
định suông: `research/yield_floor_custom30v_phase1_20260818/probe_panel_equiv.py` so từng ô với
`_yield_floor()` trên 24 mã × 5 kỳ phủ cả 5 nhãn — khớp 120/120; quant-skeptic tái lập độc lập
25/25 (job Taylor_20260818_131745).

Đọc con số này thế nào (research `dividend_yield_floor_20260818`): CONFIRMED chân H2 (đệm đuôi
trái, ΔMDD60 +3,46pp) / **REFUTED chân H1 (KHÔNG có alpha lợi suất — BHAR60 t=0,67, median ÂM)**.
⇒ TUYỆT ĐỐI không đọc BELOW_FLOOR như tín hiệu mua.
"""
import bisect

import pandas as pd

# Import `trading_bot.due_diligence` nằm TRONG `label_basket()`, không ở tầng module: đây là
# đường quan sát phụ của một pipeline money-path — một ImportError ở đây KHÔNG được phép giết
# `custom30_history.py`. Ngưỡng lấy thẳng từ due_diligence (một nguồn sự thật), không chép lại.

PRICE_LOOKBACK_DAYS = 20          # như panel research: giá gần nhất ≤ 20 ngày lịch trước rebal
DIV_LOOKBACK_DAYS = 1095          # 3 cửa sổ 365 ngày


def _empty(pairs):
    """Fail-open: mọi cặp về nhãn trung tính, KHÔNG chặn gì, KHÔNG raise."""
    return {(tk, str(pd.Timestamp(d).date())): ("NO_DATA", None) for tk, d in pairs}


def label_basket(bq, pairs, verbose=True):
    """-> {(ticker, 'YYYY-MM-DD'): (yield_floor_note, is_stable_payer)}.

    `bq` = callable SQL -> DataFrame (truyền vào để dùng đúng reader của caller).
    `pairs` = iterable (ticker, rebal_date). Mọi đường hỏng (feed cũ, query lỗi, thiếu giá,
    thiếu cổ tức) đều về ("NO_DATA", None) cho cặp đó — KHÔNG bao giờ raise ra ngoài.
    """
    pairs = [(str(tk), pd.Timestamp(d)) for tk, d in pairs]
    if not pairs:
        return {}
    out = _empty(pairs)
    try:
        import corp_action_lib
        from deposit_rate_vn import current_deposit_rate
        from trading_bot.due_diligence import (_corp_action_feed_ok, YIELD_FLOOR_NEAR_LO,
                                               YIELD_FLOOR_NEAR_HI, YIELD_FLOOR_ICB_BANKING)

        dates = sorted({d for _, d in pairs})
        tickers = sorted({tk for tk, _ in pairs})
        d_max = max(dates)

        # §14/registry: `corporate_action` KHÔNG có writer trong repo ⇒ verify freshness mỗi
        # lần đọc, đúng cổng mà `_yield_floor()` dùng. Feed cũ ⇒ toàn bộ NO_DATA (fail-open).
        if not _corp_action_feed_ok(d_max.date()):
            if verbose:
                print("  [yield_floor] corporate_action feed KHONG tuoi -> toan bo NO_DATA")
            return out

        inlist = ",".join(f"'{t}'" for t in tickers)
        div_lo = (min(dates) - pd.Timedelta(days=DIV_LOOKBACK_DAYS)).date()
        div = pd.DataFrame(corp_action_lib.bq(f"""WITH dd AS (
  SELECT c.ticker, c.exright_date AS ex, c.value_per_share,
    ROW_NUMBER() OVER (PARTITION BY c.ticker,c.exright_date,c.dividend_year,c.dividend_stage_vi
                       ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` c
  WHERE c.event_code="DIV" AND c.event_status="executed" AND c.ticker IN ({inlist})
    AND c.exright_date IS NOT NULL AND c.value_per_share > 0
    AND c.exright_date BETWEEN DATE '{div_lo}' AND DATE '{d_max.date()}')
SELECT ticker, ex, value_per_share FROM dd WHERE rn=1"""))
        if div.empty:
            div = pd.DataFrame(columns=["ticker", "ex", "value_per_share"])
        div["ex"] = pd.to_datetime(div["ex"])
        div["value_per_share"] = pd.to_numeric(div["value_per_share"], errors="coerce")
        div = div[div["value_per_share"] > 0]
        div_by_tk = {tk: g.sort_values("ex") for tk, g in div.groupby("ticker")}

        # Leg giá: CHỈ các cửa sổ 21 ngày trước mỗi rebal, không phải cả dải 2014→2026 (partition
        # pruning trên BQ live: dry_run 77 MB/lần).
        #   ⚠️ ĐỪNG "tối ưu" thành OR-nhóm (mã của kỳ đó × cửa sổ của kỳ đó) — nghe thì chặt hơn
        #   (20.086 dòng thay vì 126.971) nhưng ĐÃ ĐO và nó CHẬM HƠN 20× trên chính đường
        #   production: `wc_env.sh` bật `BQ_LOCAL_CACHE` ⇒ query chạy trong DuckDB, nơi 49 nhóm
        #   `IN (...) AND BETWEEN` tốn 16,0s còn dạng dưới đây tốn 0,7s (đo 2 lần, đảo thứ tự để
        #   loại hiệu ứng cache; kết quả 2 dạng khớp từng dòng).
        wins = " OR ".join(
            f"t.time BETWEEN DATE '{(d - pd.Timedelta(days=PRICE_LOOKBACK_DAYS)).date()}' "
            f"AND DATE '{d.date()}'" for d in dates)
        px = bq(f"""SELECT t.ticker, t.time, COALESCE(t.Price,t.Close) AS price, t.ICB_Code AS icb
FROM tav2_bq.ticker t WHERE t.ticker IN ({inlist}) AND ({wins})
  AND COALESCE(t.Price,t.Close) > 0""")
        px["time"] = pd.to_datetime(px["time"])
        px = px.sort_values(["ticker", "time"])
        px_map = {}
        for tk, g in px.groupby("ticker"):
            ts = list(g["time"]); pr = list(g["price"]); ic = list(g["icb"])
            for d in dates:
                i = bisect.bisect_right(ts, d) - 1
                if i >= 0 and (d - ts[i]).days <= PRICE_LOOKBACK_DAYS:
                    px_map[(tk, d)] = (float(pr[i]),
                                       (None if pd.isna(ic[i]) else int(ic[i])))

        dep_cache = {}
        for tk, d in pairs:
            out[(tk, str(d.date()))] = _label_one(
                tk, d, px_map, div_by_tk, dep_cache, current_deposit_rate,
                (YIELD_FLOOR_NEAR_LO, YIELD_FLOOR_NEAR_HI, YIELD_FLOOR_ICB_BANKING))
    except Exception as exc:                      # lưới cuối — pipeline rổ KHÔNG được chết vì nhãn
        print(f"  [yield_floor] batch loi -> toan bo NO_DATA: {str(exc)[:200]}")
        return _empty(pairs)
    return out


def _label_one(tk, d, px_map, div_by_tk, dep_cache, current_deposit_rate, thr):
    """Nhân bản logic nhãn của `_yield_floor()` — thứ tự nhánh giữ NGUYÊN (đã đối chiếu 120/120)."""
    near_lo, near_hi, icb_banking = thr
    p = px_map.get((tk, d))
    if p is None:
        return ("NO_DATA", None)
    price, icb = p
    if icb is not None and icb == icb_banking:
        return ("BANKING_EXCLUDED", None)
    g = div_by_tk.get(tk)
    if g is None:
        return ("NO_DATA", False)
    w = [(d - pd.Timedelta(days=365 * (k + 1)), d - pd.Timedelta(days=365 * k)) for k in range(3)]
    n = [int(((g["ex"] > lo) & (g["ex"] <= hi)).sum()) for lo, hi in w]
    div0 = float(g.loc[(g["ex"] > w[0][0]) & (g["ex"] <= w[0][1]), "value_per_share"].sum())
    stable = (n[0] >= 1 and n[1] >= 1 and n[2] >= 1)
    key = str(d.date())
    if key not in dep_cache:
        dep_cache[key] = float(current_deposit_rate(key))
    dep = dep_cache[key]
    if div0 <= 0 or dep <= 0:
        return ("NO_DATA", stable)
    if not stable:
        return ("NO_DATA", False)
    prox = price / (div0 / (dep / 100.0))
    return (("BELOW_FLOOR" if prox < near_lo else
             "ABOVE_FLOOR" if prox > near_hi else "NEAR_FLOOR"), True)
