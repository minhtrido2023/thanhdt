#!/usr/bin/env python3
"""oshares_pit.py — the two adapters a consumer uses to read `oshares_live` safely.

`oshares_live.oshares_at()` answers "how many shares were outstanding at date D" from the corp-
action feed instead of the quarterly `ticker_financial.OShares`. It is more correct where it
answers — but it **declines to answer** whenever the feed cannot support a checked number
(`value is None` for `UNKNOWN_RATIO` / `NO_ANCHOR`), and that happens far more often the further
back you look. Measured 2026-08-13 on a 108-name top-liquidity universe:

    date          value is None
    2014-07-01      33,3%
    2016-01-05      28,7%
    2018-01-03      25,0%
    2020-01-06      12,0%
    2024-01-03      13,9%
    2026-08-12       2,8%

So a NAKED substitution is not a fix — in a 2014-start backtest it would blank a third of the
early cross-section and replace a look-ahead bias with a data-availability bias that is larger and
harder to see. Every consumer needs a fallback, and the two consumers wired on 2026-08-13 need
DIFFERENT fallbacks because they are exposed to different risks:

  `oshares_pit()`         — HISTORICAL / point-in-time work. Look-ahead is the whole defect being
                            fixed, so prefer `oshares_live` where it answers AND the anchor it
                            answered from can be CERTIFIED; fall back to the quarterly number
                            everywhere else (it declines, or the anchor cannot be certified).

⚠️ IT IS NOT "STRICTLY BETTER THAN STATUS QUO", AND THE VERSION THAT SAID SO WAS REFUTED WITH A
REPRODUCIBLE COUNTEREXAMPLE (quant-skeptic, 2026-08-13). The vendor feed contains WRONG rows, so
serving one unchecked replaces a correct number with a wrong one — at FPT's real 2020-05-05
rebalance the first wire returned 461.723.054 against a true 681.668.102 (−32,3%), at the
highest-confidence label `AIS_EXACT`. What this module removes is MOST of the look-ahead, not all
of it, and it guarantees exactly one thing: **a row that falls back is byte-identical to what the
caller does today**. Rows that are SERVED carry the residual risk of a bad vendor row that the
certification gate below happened to certify. That is a smaller risk than before, not zero.

  `oshares_reconciled()`  — LIVE numbers in use right now. `corp_action_daily.py` went on cron
                            only today (2026-08-13) and has not seen one real vendor batch roll or
                            one real backfill in production, so the fresher number does not yet get
                            to override anything. Take `oshares_live` ONLY where it AGREES with the
                            quarterly number within `EXPLAIN_TOL`; on any divergence, miss, or
                            error, keep the quarterly number the consumer already uses.

⚠️ READ THIS BEFORE BELIEVING `oshares_reconciled` IMPROVES A NUMBER — IT DOES NOT, BY DESIGN.
Agreement within 0,1% means the two sources are interchangeable, and divergence — the ONLY case
where the fresh count would have changed an answer (a 15% stock dividend that has gone ex but not
yet reached a quarterly row) — is exactly the case routed back to the stale number. The wrapper is
therefore **behaviourally ~neutral on purpose**: what it buys during burn-in is a per-day COUNT of
how often the two sources part company, and on which tickers. Flipping the divergence branch to
prefer `oshares_live` is the change that would actually deliver the freshness, and it is a policy
decision for the user after burn-in, not a default this module may take on its own.

Both functions are TOTAL: they never raise and never return fewer tickers than they were given.
Any failure inside `oshares_live` (BQ down, feed dead, an unhandled shape) degrades the whole batch
to the caller's own fallback values, which is precisely today's behaviour.

The tolerance is `oshares_live.EXPLAIN_TOL` (0,1%), IMPORTED, never re-declared — same constant the
daily reconciliation gate in `corp_action_daily.py` uses. Two thresholds for one notion of "equal"
is how two parts of the fleet reach opposite conclusions on identical data.

Sources (§9 — both already in `mike/kb/data_registry/`):
  * `tav2_bq.corporate_action` — vendor feed, via `oshares_live` / `corp_action_lib`.
  * `tav2_bq.ticker_financial.OShares` — filed **TRAP** (restated, not point-in-time):
    `mike/kb/data_registry/fundamentals/ticker_financial_oshares.md`. It stays as the fallback
    because a restated number is still better than no number, but it is never the preferred one in
    historical work.
"""
from __future__ import annotations

import csv
import datetime as dt
import os

from oshares_live import EXPLAIN_TOL, _dedup_iss, _fetch, _roll, oshares_at

__all__ = ["EXPLAIN_TOL", "fetch_cache", "oshares_pit", "oshares_reconciled",
           "summarize", "append_log"]

# `value is None` carries these two methods and no others (invariant asserted in
# oshares_live._selfcheck check 10). Named here so a reader of a fallback record does not have to
# go and look up what "declined" means.
_DECLINED = ("UNKNOWN_RATIO", "NO_ANCHOR")

# ── CỔNG HỢP LÝ (thêm 2026-08-13 sau khi wire thử Việc A lộ ra ca THẬT) ──────────────────────
# `oshares_live` coi `AIS.shares_total_after` là "neo chính xác — lời khẳng định của chính sở giao
# dịch" và nhận VÔ ĐIỀU KIỆN: `AIS_EXACT` là nhãn tin cậy nhất mà lại là nhánh DUY NHẤT không có
# cổng kiểm nào (dòng quý thì có cổng giải thích). Nhưng số của vendor CÓ THỂ SAI:
#
#   IDC, AIS 2020-05-28: shares_delta = 108.000.000, shares_total_after = 3.000.000.000
#   — trong khi AIS liền trước (2019-06-13) = 300.000.000. 300tr + 108tr = 408tr, KHÔNG phải 3 tỷ.
#   Ba nguồn độc lập bác nó: AIS trước (300tr), 8 quý `ticker_financial` sau đó (vẫn 300tr), và
#   AIS kế tiếp 2022-09-05 (329.999.929 = 300tr + 29.999.929). Sai hệ số ~10.
#   `oshares_live` trả 3.000.000.000 cho MỌI ngày 2020-05-28 → 2022-09-05: sai 10 lần, hơn 2 năm.
#
# Quét toàn bảng (2026-08-13, 2.807 cặp AIS liên tiếp có đủ `shares_delta` + `shares_total_after`):
# 1.947 (69,4%) khớp tuyệt đối bất biến `total_after − delta == total_after liền trước`; **110 cặp
# / 74 mã lệch thô** (40 cặp ngụ ý số trước lớn hơn 2× số trước thật, 70 cặp nhỏ hơn nửa). Đó là
# một PHÉP SÀNG, không phải 110 lỗi đã xác nhận từng ca — chỉ ca IDC được kiểm tay ba nguồn.
#
# Cổng dưới đây là lớp NGƯỜI TIÊU THỤ, cố ý thô: một số CP nhảy quá `SANITY_FACTOR` lần so với
# dòng quý gần nhất gần như chắc chắn là lỗi dữ liệu chứ không phải sự kiện thật (thưởng 1:2 =
# ×3 đã là cực hiếm ở VN, và mọi ca vượt cổng đều được in ra để soi tay). Nó KHÔNG sửa
# `oshares_live` — chỗ đúng để vá là cổng nhận neo AIS trong module đó, cần một vòng
# quant-skeptic riêng; xem khuyến nghị trong báo cáo job Taylor_20260813_125526.
#
# ── SWEEP `SANITY_FACTOR` (quant-skeptic yêu cầu vòng 2: "một ngưỡng gánh ~0,95pp không được ở
# lại dạng lập luận"). Đo 2026-08-13 sau khi cổng CHỨNG NHẬN được vá, `custom30_core_select_audit`
# chạy đủ, mỗi chân SELF-CHECK PASS + SPOTCHECK PASS:
#
#   ×      1,5    2,0    2,5    3,0    4,0    5,0    7,5   10,0   12,0 | 15,0   30,0  100,0 |  tắt
#   liq  12,43  12,44  12,44  12,44  12,44  12,44  12,44  12,44  12,44 | 12,51  12,51  12,51 | 13,12
#   chặn   515    503    502    500    500    500    500    500    499 |   472    472    470 |   457
#
# ⇒ HAI kết luận tách bạch, đừng gộp:
#   (1) NGƯỠNG không còn gánh gì: [1,5 … 12] là một BÌNH NGUYÊN THẬT — 0,01pp biên độ trên dải
#       rộng 8×, và 3,0 nằm giữa. Đây là số ĐO, không còn là lập luận. (Trước khi vá cổng chứng
#       nhận, ngưỡng này gánh ~0,95pp; giờ cổng chứng nhận bắt trước phần lớn.)
#   (2) BẢN THÂN CỔNG thì VẪN gánh: tắt hẳn ⇒ 13,12% (+0,68pp giả). Bậc thang ở ~13-14× (12,44 →
#       12,51) là 27 ô lỗi thô mà cổng chứng nhận KHÔNG bắt được. Nên giữ cổng, và giữ nó thô.
# Tái lập: `OSHARES_SANITY_FACTOR=<x> python custom30_core_select_audit.py`.
#
# Đọc từ env để SWEEP tái lập được bằng lệnh, không phải bằng cách sửa file rồi sửa lại.
# Mặc định 3,0 = giá trị production.
SANITY_FACTOR = float(os.environ.get("OSHARES_SANITY_FACTOR", "3.0"))


def fetch_cache(tickers, until):
    """One BQ round-trip serving EVERY date <= `until`.

    `oshares_at` clips the cache to `asof` internally, so a backtest fetches once at its end date
    and then answers 48 rebalance dates in pure Python. Returns None on any failure — callers
    treat that as "no live source today" and fall back, they do not crash.
    """
    try:
        return _fetch(sorted(set(tickers)), until)
    except Exception as e:                                  # noqa: BLE001 — total by contract
        print(f"[oshares_pit] fetch_cache FAILED ({type(e).__name__}: {e}) "
              f"-> mọi mã sẽ dùng số dự phòng (ticker_financial)")
        return None


def _live(tickers, asof, cache):
    """({ticker: record}, cache) from oshares_live — ({}, cache) if the call fails outright.

    Builds the cache when the caller did not pass one, so the suspect-anchor audit below has the
    same corp-action rows the answer was derived from (and it costs one BQ round-trip, not two).
    """
    if cache is None:
        cache = fetch_cache(tickers, asof)
    try:
        return oshares_at(list(tickers), asof, _cache=cache), cache
    except Exception as e:                                  # noqa: BLE001 — total by contract
        print(f"[oshares_pit] oshares_at({asof}) FAILED ({type(e).__name__}: {e}) "
              f"-> mọi mã dùng số dự phòng")
        return {}, cache


# Verdict nào của một neo AIS thì ĐƯỢC PHỤC VỤ. Đây là dòng CHÍNH SÁCH của cả module — mọi thứ
# khác chỉ là cách tính verdict. Đo 2026-08-13 (job Taylor_20260813_142812), xem § CỔNG:
#   "OK"        — đối chiếu được với AIS liền trước và KHỚP.
#   "NO_PRIOR"  — là AIS ĐẦU TIÊN có `shares_total_after` của mã: KHÔNG CÓ GÌ để đối chiếu, khác
#                 hẳn "dựng được kỳ vọng và nó SAI". Phục vụ, đúng như
#                 `oshares_live._explain_quarterly` xử lý dòng quý không có AIS nào trước nó (nhận,
#                 nhưng không coi là đã kiểm) — và neo này vẫn còn cổng biên độ `_sane` đứng sau.
#                 ĐO ĐƯỢC (rổ 171 mã × 48 ngày rebal = 7.610 ô):
#                   phục vụ NO_PRIOR (đang chạy) : live 6.603 (86,8%) · liq CAGR 12,44%
#                   loại NO_PRIOR  (biến thể chặt): live 6.290 (82,7%) · liq CAGR 12,46%
#                 ⇒ chặt hơn đẩy thêm 313 ô (4,1pp phủ) về lại số quý RESTATE — tức đổi look-ahead
#                 lấy look-ahead — để mua 0,02pp CAGR, nằm trong nhiễu. Không có ca hại nào đo
#                 được ở nhánh này: FPT 2017-07-03 (AIS đầu tiên, 530.961.105) đối chiếu ĐÚNG với
#                 dòng quý 2017-08-01 (530.878.729, lệch 0,015%).
#                 Đây là điểm PHÁN ĐOÁN duy nhất còn lại của cổng; đổi chính sách = sửa 1 dòng này.
#   "UNVERIFIED"— mọi trường hợp còn lại (dựng được kỳ vọng nhưng lệch, HOẶC không dựng nổi kỳ
#                 vọng nào). KHÔNG phục vụ.
_SERVE_AIS_VERDICTS = ("OK", "NO_PRIOR")


def _anchor_unverified(cache, tk, asof, rec):
    """Neo AIS của câu trả lời này có được CHỨNG NHẬN không? Xem `_ais_verdicts`.

    FAIL-CLOSED: thiếu cache, verdict lạ, hay bản thân hàm chứng nhận ném lỗi ⇒ coi như CHƯA
    chứng nhận. Bản trước trả `False` (= phục vụ) ở cả ba nhánh đó — cùng một lỗi "không kiểm
    được thì cho qua" mà quant-skeptic bác ở `_suspect_ais`, chỉ nằm ở một tầng khác.
    """
    if rec.get("anchor_source") != "corporate_action.AIS":
        return False                    # neo dòng quý: đã có cổng riêng trong `oshares_live`
    if not cache:
        return True
    try:
        return _ais_verdicts(cache[1], tk, asof).get(rec.get("anchor_date")) \
            not in _SERVE_AIS_VERDICTS
    except Exception:                                       # noqa: BLE001 — total by contract
        return True


def _rec(ticker, value, source, reason, method=None, rel_diff=None, live_value=None):
    return {"ticker": ticker, "value": value, "source": source, "reason": reason,
            "method": method, "rel_diff": rel_diff, "live_value": live_value}


def _ais_verdicts(corp, ticker, asof):
    """{effective_date: "OK" | "NO_PRIOR" | "UNVERIFIED"} cho MỌI AIS của mã, tại `asof`.

    ⚠️ ĐỔI NGHĨA 2026-08-13 (quant-skeptic REFUTED bản trước, job Taylor_20260813_142812).
    Bản trước là `_suspect_ais` — một bộ **BẮT LỖI**: trả về tập AIS *chứng minh được là sai*, và
    mọi dòng còn lại được phục vụ ở nhãn tin cậy cao nhất `AIS_EXACT`. Đó là thế giới MỞ: "chưa
    bắt được" bị đọc thành "đã kiểm". Hàm này là bộ **CHỨNG NHẬN**: nó chỉ nói dòng nào đối chiếu
    ĐƯỢC và KHỚP; consumer chỉ phục vụ những dòng đó (`_SERVE_AIS_VERDICTS`).

    Vì sao phải đổi, chứ không phải vá thêm một luật: quant-skeptic chỉ ra tập cờ cũ không phải
    "lỗi vendor" mà là "transition NẰM CẠNH một bất thường" — IDC 2022-09-05 (dòng ĐÚNG) bị gắn cờ
    chỉ vì đứng sau dòng 3 tỷ hỏng, trong khi FPT 2020-04-06 (dòng SAI) lọt lưới. Một bộ bắt lỗi
    không thể sửa được bằng cách bắt giỏi hơn; phải thôi tuyên bố "đây là lỗi" và chỉ tuyên bố
    "đây là dòng tôi kiểm được".

    Bất biến kiểm được, chỉ dùng dữ liệu của riêng feed corp-action (không mượn số quý). Có HAI
    cách hợp lệ để tới `shares_total_after[i]`, và một dòng đúng chỉ cần khớp MỘT trong hai:

        (a) roll(shares_total_after[i-1], ISS ở giữa)     — sự kiện ISS đã cộng phần tăng rồi,
                                                             AIS chỉ là lần đăng ký niêm yết của
                                                             CHÍNH số CP đó
        (b) shares_total_after[i-1] + shares_delta[i]      — không có bản ghi ISS nào tương ứng,
                                                             `shares_delta` là nguồn duy nhất

    ⚠️ Cộng cả hai (`roll(...) + delta`) là ĐẾM HAI LẦN và đó là lỗi bản đầu của hàm này: nó gắn
    cờ 12/12 AIS của FPT, kể cả 2025-09-12 = 1.703.507.121 mà `oshares_live._selfcheck` đã chứng
    minh là ĐÚNG. Dùng lại `oshares_live._roll` nên phần lăn sự kiện là CÙNG một hàm với phần tính
    số, không phải bản chép tay thứ hai.

    Chỉ xét AIS có `effective_date <= asof`: quyết định LOẠI cũng phải point-in-time, nếu không
    một AIS năm 2026 lại đang bác một câu trả lời của năm 2019.

    ⚠️ MỘT ISS CHẮN ĐƯỜNG CHỈ GIẾT ỨNG VIÊN (a), KHÔNG GIẾT (b). Đây chính là lỗ hổng đã bị bác:
    bản trước `continue` ngay khi `_roll` trả blocker, vứt bỏ luôn ứng viên (b) — dù (b) =
    `prev + shares_delta` không cần lăn qua ISS nào cả. Quét toàn bảng 2026-08-13: **213/2.505
    transition (129 mã)** có đúng hình dạng "blocker chắn đường NHƯNG (b) dựng được và MÂU THUẪN"
    — tức 213 dòng vendor sai đang được phục vụ ở nhãn `AIS_EXACT` mà không ai kiểm. Ca FPT
    2020-05-05 (461.723.054 thay vì 681.668.102, −32,3%) là một trong số đó. Thêm 7 ca
    (6 mã) không dựng được ứng viên NÀO ⇒ nay là "UNVERIFIED", trước là phục vụ im lặng.

    Chi phí của chiều ngược lại đã cân nhắc và CHẤP NHẬN: khi có ISS thật xen giữa, (b) thiếu
    phần cổ phiếu do ISS sinh ra nên có thể báo UNVERIFIED oan. Hậu quả của báo oan là **rơi về
    đúng số caller đang dùng hôm nay** — không mất gì; hậu quả của bỏ lọt là thay một số đúng
    bằng một số sai −32%. Hai chiều KHÔNG đối xứng, nên cổng cố ý lệch về phía báo oan.

    HAI CA THẬT nó bắt được, cả hai đã kiểm tay bằng ba nguồn độc lập:
      IDC 2020-05-28  delta 108.000.000, total_after 3.000.000.000, AIS trước 300.000.000
                      ⇒ kỳ vọng 408.000.000, lệch ~7,4×. (8 quý sau đó vẫn 300tr; AIS kế 329.999.929.)
      AAA 2019-06-03  delta 1.700.000, total_after 58.664.988, AIS trước 171.199.976
                      ⇒ kỳ vọng 172.899.976. Ca này LỌT qua cổng thô ×3 (58,66/171,20 = 0,343,
                      hụt biên 1/3 = 0,333) — đó là lý do phải có cổng theo bất biến, không chỉ
                      cổng theo biên độ.
    """
    rows = sorted((c for c in corp
                   if c["ticker"] == ticker and c["event_code"] == "AIS"
                   and c["effective_date"] and c["effective_date"] <= asof
                   and c["shares_total_after"]),
                  key=lambda r: r["effective_date"])
    iss = [c for c in corp if c["ticker"] == ticker and c["event_code"] == "ISS"
           and c["exright_date"] and c["exright_date"] <= asof]
    verdicts = {}
    if rows:
        verdicts[rows[0]["effective_date"]] = "NO_PRIOR"
    for prev, cur in zip(rows, rows[1:]):
        if cur["effective_date"] == prev["effective_date"]:
            continue                                        # cùng ngày: không suy ra thứ tự được
        base_prev = float(prev["shares_total_after"])
        actual = float(cur["shares_total_after"])
        cands = []
        between = _dedup_iss([e for e in iss
                              if prev["effective_date"] < e["exright_date"]
                              <= cur["effective_date"]])
        rolled, _applied, blockers = _roll(base_prev, between)
        if not blockers:
            cands.append(rolled)                             # (a) — chỉ khi lăn được HẾT ISS
        delta = cur.get("shares_delta")
        if delta is not None and float(delta) > 0:
            cands.append(base_prev + float(delta))           # (b) — không phụ thuộc ISS
        # `cands` RỖNG (blocker chắn (a) VÀ không có delta cho (b)) ⇒ không dựng được kỳ vọng nào
        # ⇒ UNVERIFIED. Đây là chỗ `all([]) == True` từng làm nghĩa của hàm đảo ngược nếu viết
        # gọn, nên điều kiện được viết TƯỜNG MINH.
        ok = bool(cands) and any(e > 0 and abs(actual - e) / e <= EXPLAIN_TOL for e in cands)
        verdicts[cur["effective_date"]] = "OK" if ok else "UNVERIFIED"
    return verdicts


def _sane(live_value, fallback_value):
    """Số CP có nhảy quá `SANITY_FACTOR` lần so với dòng quý gần nhất không? Xem §CỔNG HỢP LÝ."""
    if fallback_value is None or fallback_value <= 0 or live_value is None:
        return True                      # không có gì để so ⇒ không phải chỗ để chặn
    ratio = live_value / fallback_value
    return 1.0 / SANITY_FACTOR <= ratio <= SANITY_FACTOR


def _fallback_value(fallback, tk):
    """The consumer's own current number for `tk`, or None. Accepts NaN as 'missing'."""
    v = fallback.get(tk)
    if v is None:
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v if v == v and v > 0 else None                  # v != v -> NaN


def oshares_pit(tickers, asof, fallback, cache=None):
    """{ticker: record} — HISTORICAL policy: prefer `oshares_live`, fall back where it declines.

    `fallback` is {ticker: quarterly OShares} — whatever the caller reads today. Every returned
    record has `value` (may be None only when the fallback is missing too), `source`
    ("oshares_live" | "ticker_financial" | "none") and a `reason` string that survives into logs.

    Rows that fall back are IDENTICAL to the caller's current behaviour. Rows that are SERVED are
    not guaranteed better: `oshares_live` can carry a wrong vendor row, so the net effect is
    "most of the look-ahead removed, minus whatever bad vendor rows the certification gate below
    let through" — NOT "can only remove look-ahead" (that claim shipped here, was false, and was
    refuted at FPT 2020-05-05; see the module docstring).
    """
    live, cache = _live(tickers, asof, cache)
    out = {}
    for tk in tickers:
        fb = _fallback_value(fallback, tk)
        r = live.get(tk)
        lv = None if r is None or r.get("value") is None else float(r["value"])
        if lv is not None and _anchor_unverified(cache, tk, asof, r):
            out[tk] = _rec(tk, fb, "ticker_financial" if fb is not None else "none",
                           f"KHÔNG XÁC MINH ĐƯỢC: neo vào AIS {r['anchor_date']} không đối chiếu "
                           f"được với AIS liền trước ⇒ bỏ live {lv:,.0f}",
                           r.get("method"), None if fb is None else abs(lv - fb) / fb, lv)
        elif lv is not None and fb is not None and not _sane(lv, fb):
            out[tk] = _rec(tk, fb, "ticker_financial",
                           f"KHÔNG HỢP LÝ: live {lv:,.0f} lệch {lv / fb:.1f}× số quý {fb:,.0f} "
                           f"(> {SANITY_FACTOR:g}×) ⇒ nghi lỗi dữ liệu, giữ số quý",
                           r.get("method"), abs(lv - fb) / fb, lv)
        elif lv is not None:
            out[tk] = _rec(tk, lv, "oshares_live", "PIT", r.get("method"),
                           None if fb is None else abs(lv - fb) / fb, lv)
        elif fb is not None:
            why = r.get("method") if r else "NO_RESULT"
            out[tk] = _rec(tk, fb, "ticker_financial",
                           f"oshares_live từ chối trả lời ({why})", why)
        else:
            out[tk] = _rec(tk, None, "none", "cả hai nguồn đều không có số",
                           (r or {}).get("method"))
    return out


def oshares_reconciled(tickers, asof, fallback, cache=None):
    """{ticker: record} — LIVE policy: fail-safe onto the number the consumer already uses.

    `oshares_live` is taken ONLY when it agrees with `fallback` within `EXPLAIN_TOL`. Divergence,
    a declined answer, a missing ticker, or an outright failure all resolve to `fallback`.

    Deliberate asymmetry vs `oshares_pit`: when `fallback` is MISSING, this returns None even if
    `oshares_live` has a number. Today the consumer abstains on those rows; handing it a number
    that nothing checked would be a live behaviour change dressed up as a safety wrapper. The
    records are still emitted with reason "chỉ có oshares_live" so `summarize()` can report how
    much coverage is being left on the table during burn-in.
    """
    live, cache = _live(tickers, asof, cache)
    out = {}
    for tk in tickers:
        fb = _fallback_value(fallback, tk)
        r = live.get(tk)
        lv = None if r is None or r.get("value") is None else float(r["value"])
        method = (r or {}).get("method")
        if lv is not None and _anchor_unverified(cache, tk, asof, r):
            out[tk] = _rec(tk, fb, "ticker_financial" if fb is not None else "none",
                           f"KHÔNG XÁC MINH ĐƯỢC: neo vào AIS {r['anchor_date']} không đối chiếu "
                           f"được ⇒ bỏ live {lv:,.0f}, giữ số cũ (bq_admin)",
                           method, None if fb is None else abs(lv - fb) / fb, lv)
        elif fb is None:
            out[tk] = _rec(tk, None, "none",
                           "chỉ có oshares_live, không có số nền để đối soát" if lv is not None
                           else "cả hai nguồn đều không có số", method, None, lv)
        elif lv is None:
            out[tk] = _rec(tk, fb, "ticker_financial",
                           f"oshares_live từ chối trả lời ({method or 'NO_RESULT'})",
                           method, None, None)
        else:
            rel = abs(lv - fb) / fb
            if rel <= EXPLAIN_TOL:
                out[tk] = _rec(tk, lv, "oshares_live", "hai nguồn KHỚP", method, rel, lv)
            elif not _sane(lv, fb):
                # cùng một hành động (giữ số cũ) nhưng KHÁC nguyên nhân: "lệch" là hai nguồn nói
                # khác nhau, "không hợp lý" là một trong hai gần như chắc chắn hỏng. Gộp hai cái
                # đó vào một dòng log là cách một lỗi dữ liệu 10× lẫn vào nền nhiễu 15% thưởng CP.
                out[tk] = _rec(tk, fb, "ticker_financial",
                               f"KHÔNG HỢP LÝ: live {lv:,.0f} = {lv / fb:.1f}× số nền "
                               f"⇒ nghi lỗi dữ liệu, giữ số cũ (bq_admin)", method, rel, lv)
            else:
                out[tk] = _rec(tk, fb, "ticker_financial",
                               f"LỆCH {rel * 100:.2f}% > {EXPLAIN_TOL * 100:.1f}% "
                               f"⇒ giữ số cũ (bq_admin)", method, rel, lv)
    return out


# Hai lý do BỊ CHẶN, gộp vào cùng một ô đếm `n_fallback_implausible`: "KHÔNG HỢP LÝ" = cổng biên
# độ ×SANITY_FACTOR (gần như chắc chắn lỗi vendor), "KHÔNG XÁC MINH ĐƯỢC" = cổng chứng nhận AIS
# (không kết luận đúng/sai, chỉ là không kiểm được). Cố ý KHÔNG tách thành cột mới: `append_log`
# đang ghi vào `data/oshares_reconcile_log.csv` đã có dữ liệu burn-in của Việc B, thêm cột giữa
# chừng làm hỏng file đang đếm. Phân biệt vẫn còn nguyên trong chuỗi `reason` của từng bản ghi.
_BLOCKED_PREFIXES = ("KHÔNG HỢP LÝ", "KHÔNG XÁC MINH ĐƯỢC")


def summarize(records):
    """Counts + the worst divergence, for one printed line and one log row."""
    vals = list(records.values())
    diverged = [r for r in vals if r["source"] == "ticker_financial"
                and r["reason"].startswith("LỆCH")]
    insane = [r for r in vals if r["source"] == "ticker_financial"
              and r["reason"].startswith(_BLOCKED_PREFIXES)]
    worst = max(diverged + insane, key=lambda r: r["rel_diff"], default=None)
    return {
        "n": len(vals),
        "n_live": sum(1 for r in vals if r["source"] == "oshares_live"),
        "n_fallback_implausible": len(insane),
        "implausible_tickers": ",".join(sorted(r["ticker"] for r in insane)),
        "n_fallback_diverge": len(diverged),
        "n_fallback_declined": sum(1 for r in vals if r["source"] == "ticker_financial"
                                   and r["method"] in _DECLINED),
        "n_fallback_other": sum(1 for r in vals if r["source"] == "ticker_financial"
                                and not r["reason"].startswith(("LỆCH",) + _BLOCKED_PREFIXES)
                                and r["method"] not in _DECLINED),
        "n_no_value": sum(1 for r in vals if r["value"] is None),
        "n_live_only": sum(1 for r in vals if r["value"] is None and r["live_value"] is not None),
        "worst_ticker": worst["ticker"] if worst else "",
        "worst_rel_diff": round(worst["rel_diff"], 6) if worst else 0.0,
        "diverged_tickers": ",".join(sorted(r["ticker"] for r in diverged)),
    }


LOG_PATH = os.path.join(os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"),
                        "data", "oshares_reconcile_log.csv")


def append_log(consumer, asof, summary, path=LOG_PATH):
    """One row per (consumer, run). This is the frequency record the burn-in is FOR.

    Best-effort by contract — a logging failure must never take down a report (§ the whole point
    of this module). Returns the path written, or None.

    §5b: a selfcheck driving a consumer must not write into the shared artifact the burn-in is
    counted from — test rows would show up as real days. Gate is an EXPLICIT env var, never
    inferred from a field value.
    """
    if os.environ.get("MIKE_BOT_TEST_MODE") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        return None
    cols = ["logged_at", "consumer", "asof", "n", "n_live", "n_fallback_diverge",
            "n_fallback_implausible", "n_fallback_declined", "n_fallback_other", "n_no_value",
            "n_live_only", "worst_ticker", "worst_rel_diff", "diverged_tickers",
            "implausible_tickers"]
    row = {"logged_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "consumer": consumer, "asof": asof, **{k: summary.get(k, "") for k in cols[3:]}}
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        new = not os.path.exists(path)
        with open(path, "a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            if new:
                w.writeheader()
            w.writerow(row)
        return path
    except Exception as e:                                  # noqa: BLE001
        print(f"[oshares_pit] không ghi được log đối soát ({type(e).__name__}: {e})")
        return None


def _selfcheck() -> int:                                    # noqa: C901 — a flat list of cases
    fails, ran = [], []

    def check(name, cond, detail=""):
        ran.append(name)
        print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
        if not cond:
            fails.append(name)

    # ── Phần 1: chính sách, trên dữ liệu DỰNG TAY. Hermetic: không chạm BQ, nên nó kiểm ĐÚNG
    # cái logic rẽ nhánh chứ không kiểm "hôm nay BQ trả gì".
    print("== Chính sách rẽ nhánh (hermetic, monkeypatch oshares_at) ==")
    import oshares_pit as M
    real = M.oshares_at
    FB = {"AGREE": 100_000_000.0, "DIVERGE": 100_000_000.0, "DECLINE": 100_000_000.0,
          "NOFB": None, "EDGE_IN": 100_000_000.0, "EDGE_OUT": 100_000_000.0, "BOTHNONE": None,
          "INSANE": 300_000_000.0, "SANE_EDGE": 100_000_000.0}
    LIVE = {
        "AGREE":    {"value": 100_050_000.0, "method": "AIS_EXACT"},      # +0,05% — trong ngưỡng
        "DIVERGE":  {"value": 115_000_000.0, "method": "ISS_ESTIMATE"},   # +15%   — thưởng CP
        "DECLINE":  {"value": None, "method": "UNKNOWN_RATIO"},
        "NOFB":     {"value": 123_000_000.0, "method": "AIS_EXACT"},
        "EDGE_IN":  {"value": 100_000_000.0 * (1 + EXPLAIN_TOL), "method": "AIS_EXACT"},
        "EDGE_OUT": {"value": 100_000_000.0 * (1 + EXPLAIN_TOL * 1.01), "method": "AIS_EXACT"},
        "BOTHNONE": {"value": None, "method": "NO_ANCHOR"},
        # ca THẬT của IDC 2020-05-28, giữ nguyên con số: AIS ghi 3 tỷ trong khi quý nói 300 triệu
        "INSANE":   {"value": 3_000_000_000.0, "method": "AIS_EXACT"},
        # đúng biên trên: ×3,0 vẫn được nhận (thưởng 1:2 là sự kiện thật, hiếm nhưng có)
        "SANE_EDGE": {"value": 300_000_000.0, "method": "ISS_ESTIMATE"},
    }
    TK = sorted(FB)
    # cache RỖNG (không phải None): giữ phần này HERMETIC. cache=None sẽ khiến adapter tự gọi
    # `fetch_cache` ⇒ chạm BQ thật, và một test "hermetic" lén ra mạng là test nói dối.
    NOCACHE = ([], [])
    M.oshares_at = lambda tks, asof, _cache=None: {t: dict(LIVE[t], ticker=t) for t in tks}
    try:
        rc = M.oshares_reconciled(TK, "2026-08-13", FB, cache=NOCACHE)
        pit = M.oshares_pit(TK, "2026-08-13", FB, cache=NOCACHE)
    finally:
        M.oshares_at = real

    check("R1. KHỚP trong ngưỡng ⇒ lấy oshares_live",
          rc["AGREE"]["value"] == 100_050_000.0 and rc["AGREE"]["source"] == "oshares_live")
    check("R2. LỆCH quá ngưỡng ⇒ fail-safe về bq_admin (KHÔNG lấy số mới)",
          rc["DIVERGE"]["value"] == 100_000_000.0
          and rc["DIVERGE"]["source"] == "ticker_financial"
          and rc["DIVERGE"]["reason"].startswith("LỆCH"),
          rc["DIVERGE"]["reason"])
    check("R3. oshares_live từ chối (UNKNOWN_RATIO) ⇒ bq_admin",
          rc["DECLINE"]["value"] == 100_000_000.0
          and rc["DECLINE"]["source"] == "ticker_financial")
    check("R4. không có số nền ⇒ LIVE vẫn KHÔNG được dùng (không đổi hành vi hôm nay)",
          rc["NOFB"]["value"] is None and rc["NOFB"]["live_value"] == 123_000_000.0)
    check("R5. đúng BIÊN ngưỡng (rel == EXPLAIN_TOL) ⇒ vẫn coi là khớp",
          rc["EDGE_IN"]["source"] == "oshares_live", f"rel={rc['EDGE_IN']['rel_diff']:.6f}")
    check("R6. nhích qua biên ⇒ đã là lệch",
          rc["EDGE_OUT"]["source"] == "ticker_financial",
          f"rel={rc['EDGE_OUT']['rel_diff']:.6f}")
    check("R7. cả hai nguồn rỗng ⇒ None, không bịa số",
          rc["BOTHNONE"]["value"] is None and rc["BOTHNONE"]["source"] == "none")

    # ĐỐI CHỨNG — cái phải chứng minh cho Việc B: khi hai nguồn khớp hết, kết quả PHẢI trùng
    # baseline trong dung sai, và khi lệch thì phải trùng baseline TUYỆT ĐỐI.
    check("R8. ĐỐI CHỨNG: mọi mã KHÔNG lấy được live ⇒ giá trị == số nền TUYỆT ĐỐI",
          all(rc[t]["value"] == FB[t] for t in TK
              if rc[t]["source"] == "ticker_financial"))
    M.oshares_at = lambda tks, asof, _cache=None: {t: {"value": FB[t], "method": "AIS_EXACT"}
                                                   for t in tks if FB[t] is not None}
    try:
        same = M.oshares_reconciled(TK, "2026-08-13", FB, cache=NOCACHE)
    finally:
        M.oshares_at = real
    check("R9. ĐỐI CHỨNG: hai nguồn TRÙNG KHỚP ⇒ không đổi một đồng nào so với baseline",
          all(same[t]["value"] == FB[t] for t in TK if FB[t] is not None),
          f"{ {t: same[t]['value'] for t in TK} }")

    check("P1. PIT: có live ⇒ ưu tiên live (kể cả khi lệch — đây là chỗ khử look-ahead)",
          pit["DIVERGE"]["value"] == 115_000_000.0
          and pit["DIVERGE"]["source"] == "oshares_live")
    check("P2. PIT: live từ chối ⇒ dùng số quý, Y HỆT hành vi hiện tại",
          pit["DECLINE"]["value"] == 100_000_000.0
          and pit["DECLINE"]["source"] == "ticker_financial")
    check("P3. PIT: không có số quý nhưng có live ⇒ dùng live (lấp thêm phủ, không phải live money)",
          pit["NOFB"]["value"] == 123_000_000.0 and pit["NOFB"]["source"] == "oshares_live")
    check("P4. PIT: cả hai rỗng ⇒ None",
          pit["BOTHNONE"]["value"] is None)

    print("== CỔNG HỢP LÝ (ca IDC 2020-05-28: AIS 3 tỷ vs quý 300 triệu) ==")
    check("G1. PIT: live gấp 10× số quý ⇒ TỪ CHỐI live, giữ số quý (đây là lỗi vendor, không "
          "phải sự kiện)",
          pit["INSANE"]["value"] == 300_000_000.0
          and pit["INSANE"]["source"] == "ticker_financial"
          and pit["INSANE"]["reason"].startswith("KHÔNG HỢP LÝ"),
          pit["INSANE"]["reason"])
    check("G2. PIT: đúng BIÊN ×3,0 ⇒ VẪN nhận (cổng không nuốt sự kiện thật)",
          pit["SANE_EDGE"]["value"] == 300_000_000.0
          and pit["SANE_EDGE"]["source"] == "oshares_live")
    check("G3. đối xứng: nhỏ hơn 1/3 lần cũng bị chặn",
          not _sane(30_000_000.0, 100_000_000.0) and _sane(100_000_000.0 / 3, 100_000_000.0))
    check("G4. LIVE: cùng ca đó, `reconciled` cũng giữ số cũ nhưng ghi RIÊNG lý do "
          "(lỗi dữ liệu ≠ hai nguồn lệch nhau)",
          rc["INSANE"]["value"] == 300_000_000.0
          and rc["INSANE"]["reason"].startswith("KHÔNG HỢP LÝ")
          and rc["DIVERGE"]["reason"].startswith("LỆCH"))
    check("G5. không có số nền ⇒ cổng KHÔNG chặn (không có gì để so, và chặn thì mất phủ)",
          _sane(3_000_000_000.0, None))
    # BẰNG CHỨNG NGƯỢC: bỏ cổng ra thì giá trị THẬT SỰ đổi — nếu không, G1 chỉ là lời khẳng định.
    _keep = M.SANITY_FACTOR
    M.SANITY_FACTOR = 1e9
    M.oshares_at = lambda tks, asof, _cache=None: {t: dict(LIVE[t], ticker=t) for t in tks}
    try:
        nogate = M.oshares_pit(["INSANE"], "2026-08-13", FB, cache=NOCACHE)
    finally:
        M.SANITY_FACTOR = _keep
        M.oshares_at = real
    check("G6. CHỨNG MINH NGƯỢC: tắt cổng ⇒ 3 tỷ THẬT SỰ lọt vào (cổng đang chặn thật, "
          "không phải ca rỗng)",
          nogate["INSANE"]["value"] == 3_000_000_000.0
          and nogate["INSANE"]["source"] == "oshares_live",
          f"{nogate['INSANE']['value']:,.0f} từ {nogate['INSANE']['source']}")

    print("== Tổng hợp đếm được ==")
    s = summarize(rc)
    check("S1. tách ĐÚNG hai nguyên nhân: LỆCH = 3 ca, KHÔNG HỢP LÝ = 1 ca (INSANE)",
          s["n_fallback_diverge"] == 3 and s["n_fallback_implausible"] == 1
          and s["implausible_tickers"] == "INSANE"
          and s["diverged_tickers"] == "DIVERGE,EDGE_OUT,SANE_EDGE", str(s))
    check("S2. đếm đúng phủ bị bỏ lại (NOFB: có live mà không dùng)",
          s["n_live_only"] == 1 and s["n_no_value"] == 2, str(s))
    check("S3. tổng các nhánh == n (không mã nào rơi ra ngoài phân loại)",
          s["n_live"] + s["n_fallback_diverge"] + s["n_fallback_implausible"]
          + s["n_fallback_declined"] + s["n_fallback_other"] + s["n_no_value"] == s["n"], str(s))

    # ── Phần 2: TOÀN PHẦN. Đây là bất biến sống còn — report không bao giờ được chết vì module này.
    print("== Bất biến TOÀN PHẦN: hỏng thế nào cũng không được ném lỗi ==")

    def boom(*_a, **_k):
        raise RuntimeError("BQ sập giả lập")

    M.oshares_at = boom
    try:
        crashed = M.oshares_reconciled(TK, "2026-08-13", FB, cache=NOCACHE)
        crashed_pit = M.oshares_pit(TK, "2026-08-13", FB, cache=NOCACHE)
    finally:
        M.oshares_at = real
    check("T1. oshares_at NÉM LỖI ⇒ vẫn trả đủ mã, mọi giá trị == số nền",
          set(crashed) == set(TK)
          and all(crashed[t]["value"] == FB[t] for t in TK if FB[t] is not None))
    check("T2. lỗi cũng không làm PIT chết; PIT rơi về đúng số nền",
          set(crashed_pit) == set(TK)
          and all(crashed_pit[t]["value"] == FB[t] for t in TK if FB[t] is not None))
    # "not-a-date" là lỗi cú pháp BQ tất định ⇒ đây là khẳng định THẬT (`is None`), không phải
    # ca rỗng đội lốt PASS.
    check("T3. fetch_cache nuốt lỗi và trả None thay vì ném",
          fetch_cache(["KHONG_TON_TAI_XYZ"], "not-a-date") is None)

    M.oshares_at = lambda tks, asof, _cache=None: {}          # trả rỗng, không lỗi
    try:
        empty = M.oshares_reconciled(TK, "2026-08-13", FB, cache=NOCACHE)
    finally:
        M.oshares_at = real
    check("T4. oshares_at trả RỖNG (im lặng) ⇒ vẫn fallback đủ, không KeyError",
          set(empty) == set(TK)
          and all(empty[t]["value"] == FB[t] for t in TK if FB[t] is not None))

    fb_nan = dict(FB, AGREE=float("nan"))
    M.oshares_at = lambda tks, asof, _cache=None: {t: dict(LIVE[t], ticker=t) for t in tks}
    try:
        nanr = M.oshares_reconciled(TK, "2026-08-13", fb_nan, cache=NOCACHE)
    finally:
        M.oshares_at = real
    check("T5. số nền là NaN ⇒ coi như THIẾU (không sinh rel_diff = nan rồi lọt cổng so sánh)",
          nanr["AGREE"]["value"] is None and nanr["AGREE"]["source"] == "none")

    # ── Phần 3: dữ liệu THẬT. Ít ca, nhưng phải có — Phần 1 mù hoàn toàn với việc BQ đổi shape.
    print("== Dữ liệu THẬT (BQ) ==")
    try:
        live_real = real(["FPT", "MBB"], "2026-08-12")
        # MBB: số nền = số live chia 1,15 — mô phỏng ĐÚNG ca đang thật hôm nay (cổ tức CP 15% đã
        # ex 2026-08-11, dòng quý chưa kịp cập nhật). Lệch 15% là HỢP LÝ, không phải lỗi dữ liệu:
        # đây là ca duy nhất phân biệt được hai chính sách trên dữ liệu thật.
        fb_real = {"FPT": live_real["FPT"]["value"], "MBB": live_real["MBB"]["value"] / 1.15}
        rr = oshares_reconciled(["FPT", "MBB"], "2026-08-12", fb_real)
        check("L1. FPT: số nền == live ⇒ nhận live, nguồn = oshares_live",
              rr["FPT"]["source"] == "oshares_live", f"{rr['FPT']['value']:,.0f}")
        check("L2. MBB lệch 15% (hợp lý) ⇒ LIVE giữ số cũ, và lý do là LỆCH chứ không phải lỗi DL",
              rr["MBB"]["value"] == fb_real["MBB"]
              and rr["MBB"]["source"] == "ticker_financial"
              and rr["MBB"]["reason"].startswith("LỆCH"), rr["MBB"]["reason"])
        pr = oshares_pit(["MBB"], "2026-08-12", fb_real)
        check("L3. CÙNG dữ liệu đó, PIT lấy live — hai chính sách thật sự rẽ khác nhau",
              pr["MBB"]["source"] == "oshares_live"
              and pr["MBB"]["value"] == live_real["MBB"]["value"],
              f"{pr['MBB']['value']:,.0f} vs nền {fb_real['MBB']:,.0f}")
        # ca IDC THẬT — cổng hợp lý chạy trên dữ liệu sống, không chỉ trên fixture dựng tay
        idc = oshares_pit(["IDC"], "2021-02-05", {"IDC": 300_000_000.0})
        check("L4. IDC 2021-02-05 THẬT: AIS vendor nói 3 tỷ ⇒ cổng chặn, giữ 300 triệu",
              idc["IDC"]["value"] == 300_000_000.0
              and idc["IDC"]["source"] == "ticker_financial"
              and idc["IDC"]["live_value"] == 3_000_000_000.0, idc["IDC"]["reason"])

        print("== Cổng CHỨNG NHẬN neo AIS trên dữ liệu THẬT ==")
        cc = fetch_cache(["IDC", "AAA", "FPT", "VNM"], "2026-06-16")
        vd = {t: _ais_verdicts(cc[1], t, "2026-06-16") for t in ("IDC", "AAA", "FPT", "VNM")}

        def _served(t, d):
            return vd[t].get(d) in _SERVE_AIS_VERDICTS

        check("A1. IDC 2020-05-28 KHÔNG được chứng nhận (ca đã kiểm tay 3 nguồn)",
              not _served("IDC", "2020-05-28"), f"verdict={vd['IDC'].get('2020-05-28')}")
        check("A2. AAA 2019-06-03 KHÔNG được chứng nhận — CA MÀ CỔNG THÔ ×3 BỎ LỌT",
              not _served("AAA", "2019-06-03")
              and _sane(58_664_988.0, 171_199_976.0),      # 0,343 > 1/3 ⇒ cổng thô cho qua
              f"verdict={vd['AAA'].get('2019-06-03')}; _sane(58,66tr/171,20tr)="
              f"{_sane(58_664_988.0, 171_199_976.0)}")
        # HỒI QUY: bản đầu cộng cả roll() LẪN delta ⇒ đếm hai lần ⇒ loại 12/12 AIS của FPT, kể cả
        # dòng mà oshares_live._selfcheck đã chứng minh là ĐÚNG. Cổng phải VẪN chứng nhận dòng đó.
        check("A3. HỒI QUY: FPT 2025-09-12 (= 1.703.507.121, đã chứng minh đúng) VẪN được chứng nhận",
              vd["FPT"].get("2025-09-12") == "OK", f"verdict={vd['FPT'].get('2025-09-12')}")
        check("A4. ĐỐI CHỨNG: mã sạch vẫn được chứng nhận PHẦN LỚN, kể cả neo mới nhất "
              "(cổng không loại bừa tất cả)",
              sum(1 for v in vd["VNM"].values() if v in _SERVE_AIS_VERDICTS) >= 4
              and vd["VNM"][max(vd["VNM"])] == "OK", f"VNM={vd['VNM']}")
        # GIÁ PHẢI TRẢ, ĐO ĐƯỢC — ghi thành ca test để nó không biến mất khỏi trí nhớ: khi một ISS
        # THẬT xen giữa mà feed không mô tả nổi (ESOP 2016-07-11 tỉ lệ 0,0), ứng viên (a) chết vì
        # blocker và (b) = prev+delta thiếu đúng phần ESOP đó ⇒ VNM 2016-09-20 bị coi là KHÔNG xác
        # minh được dù nó ĐÚNG (1.451.453.429 vs dòng quý 2016-11-01 = 1.451.426.329, lệch 0,002%).
        # Đây là chiều sai AN TOÀN: rơi về đúng số caller đang dùng, ở đây lệch 0,002%.
        check("A4b. GIÁ PHẢI TRẢ: VNM 2016-09-20 (dòng ĐÚNG) bị UNVERIFIED vì ESOP tỉ lệ 0 xen "
              "giữa — chi phí là rơi về số quý lệch 0,002%, KHÔNG phải mất số",
              vd["VNM"].get("2016-09-20") == "UNVERIFIED"
              and abs(1_451_453_429 - 1_451_426_329) / 1_451_426_329 < 0.0001,
              f"verdict={vd['VNM'].get('2016-09-20')}")
        # POINT-IN-TIME: quyết định cũng không được dùng dòng của tương lai
        check("A5. PIT: xét tại 2020-01-01 thì AIS 2022-09-05 chưa tồn tại ⇒ không có verdict",
              "2022-09-05" not in _ais_verdicts(cc[1], "IDC", "2020-01-01"),
              str(sorted(_ais_verdicts(cc[1], "IDC", "2020-01-01"))))
        # BẰNG CHỨNG NGƯỢC: không có cổng chứng nhận thì AAA THẬT SỰ lọt
        _k = M.SANITY_FACTOR
        _sa = M._ais_verdicts
        M._ais_verdicts = lambda *_a, **_k2: {}
        try:
            M._SERVE_AIS_VERDICTS = (None,)                  # {}.get(d) is None ⇒ "được phục vụ"
            aaa_nogate = M.oshares_pit(["AAA"], "2019-08-05", {"AAA": 171_199_976.0}, cache=cc)
        finally:
            M._ais_verdicts, M.SANITY_FACTOR = _sa, _k
            M._SERVE_AIS_VERDICTS = ("OK", "NO_PRIOR")
        check("A6. CHỨNG MINH NGƯỢC: tắt cổng chứng nhận ⇒ AAA nhận 58.664.988 (sai −65,7%)",
              aaa_nogate["AAA"]["value"] == 58_664_988.0
              and aaa_nogate["AAA"]["source"] == "oshares_live",
              f"{aaa_nogate['AAA']['value']:,.0f} từ {aaa_nogate['AAA']['source']}")

        # ── HỒI QUY VÒNG 3 — ca quant-skeptic dùng để BÁC BỎ bản trước (job Taylor_20260813_142812)
        print("== HỒI QUY: ca REFUTED của quant-skeptic (FPT chuỗi AIS đan xen) ==")
        fcc = fetch_cache(["FPT"], "2026-06-16")
        # FPT 2020-05-05: bản trước trả 461.723.054 ở nhãn AIS_EXACT vì ESOP 2020-03-26 (tỉ lệ 0)
        # là _roll blocker ⇒ `continue` ⇒ dòng đi qua KHÔNG kiểm chứng. Sự thật = 681.668.102, xác
        # nhận độc lập 2 nguồn (2 quý liên tiếp ticker_financial; AIS kế 783.987.486 = ×1,15 sau
        # cổ tức CP 15% ngày 2020-05-13, khớp 0,0088%).
        f1 = oshares_pit(["FPT"], "2020-05-05", {"FPT": 681_668_102.0}, cache=fcc)["FPT"]
        check("A7. FPT 2020-05-05 KHÔNG trả 461.723.054 nữa (ca REFUTED vòng 2)",
              f1["value"] != 461_723_054.0, f"{f1['value']:,.0f} từ {f1['source']}")
        check("A8. …và rơi về ĐÚNG số nền 681.668.102, không bịa số thứ ba",
              f1["value"] == 681_668_102.0 and f1["source"] == "ticker_financial"
              and f1["live_value"] == 461_723_054.0, f"{f1['reason']}")
        check("A9. verdict của chính neo đó là UNVERIFIED (chặn ĐÚNG lý do, không phải trùng hợp)",
              _ais_verdicts(fcc[1], "FPT", "2020-05-05").get("2020-04-06") == "UNVERIFIED",
              str(_ais_verdicts(fcc[1], "FPT", "2020-05-05")))
        # ca thứ hai quant-skeptic nêu: đã bị chặn từ trước (chuỗi đứt KHÔNG có blocker) — giữ làm
        # hồi quy để một lần nới cổng sau này không mở lại nó.
        f2 = oshares_pit(["FPT"], "2023-04-10", {"FPT": 1_097_026_572.0}, cache=fcc)["FPT"]
        check("A10. FPT 2023-04-10 KHÔNG trả 681.780.478 (dòng cùng chuỗi sai, −37,9%)",
              f2["value"] == 1_097_026_572.0 and f2["source"] == "ticker_financial",
              f"{f2['value']:,.0f} từ {f2['source']}")
        # BẰNG CHỨNG NGƯỢC cho A7/A8: đúng ca đó, bỏ cổng ra thì số sai THẬT SỰ lọt vào.
        M._ais_verdicts = lambda *_a, **_k2: {}
        try:
            M._SERVE_AIS_VERDICTS = (None,)
            f1_nogate = M.oshares_pit(["FPT"], "2020-05-05", {"FPT": 681_668_102.0}, cache=fcc)
        finally:
            M._ais_verdicts = _sa
            M._SERVE_AIS_VERDICTS = ("OK", "NO_PRIOR")
        check("A11. CHỨNG MINH NGƯỢC: tắt cổng ⇒ FPT 2020-05-05 THẬT SỰ trả 461.723.054 (−32,3%)",
              f1_nogate["FPT"]["value"] == 461_723_054.0
              and f1_nogate["FPT"]["source"] == "oshares_live",
              f"{f1_nogate['FPT']['value']:,.0f} từ {f1_nogate['FPT']['source']}")
        # CA GƯƠNG (quant-skeptic): IDC 2022-09-05 là dòng ĐÚNG bị gắn cờ chỉ vì đứng sau dòng
        # hỏng. Bản mới KHÔNG còn tuyên bố "đây là lỗi vendor" — nó chỉ nói "không chứng nhận
        # được" và rơi về số cũ. Hành động an toàn, nhãn trung thực.
        idc2 = oshares_pit(["IDC"], "2022-10-03", {"IDC": 330_000_000.0}, cache=cc)["IDC"]
        check("A12. CA GƯƠNG IDC 2022-09-05 (dòng ĐÚNG): rơi về số nền, lý do là KHÔNG XÁC MINH "
              "ĐƯỢC chứ không phải quy kết lỗi vendor",
              idc2["source"] == "ticker_financial"
              and idc2["value"] == 330_000_000.0
              and idc2["reason"].startswith("KHÔNG XÁC MINH ĐƯỢC"), idc2["reason"])
        # FAIL-CLOSED ở tầng gọi: thiếu cache ⇒ không kiểm được ⇒ không phục vụ (bản trước cho qua)
        check("A13. FAIL-CLOSED: cache rỗng/None ⇒ neo AIS coi như CHƯA chứng nhận",
              _anchor_unverified(None, "FPT", "2020-05-05",
                                 {"anchor_source": "corporate_action.AIS",
                                  "anchor_date": "2020-04-06"}))
        check("A14. FAIL-CLOSED: hàm chứng nhận NÉM LỖI ⇒ vẫn coi như CHƯA chứng nhận",
              _anchor_unverified(("boom",), "FPT", "2020-05-05",
                                 {"anchor_source": "corporate_action.AIS",
                                  "anchor_date": "2020-04-06"}))
        check("A15. neo KHÔNG phải AIS (dòng quý) ⇒ cổng này không can thiệp (đã có cổng riêng)",
              not _anchor_unverified(cc, "FPT", "2020-05-05",
                                     {"anchor_source": "ticker_financial",
                                      "anchor_date": "2020-03-31"}))
    except Exception as e:                                  # noqa: BLE001
        check("L1-L3. gọi được BQ", False, f"{type(e).__name__}: {e}")

    print()
    if fails:
        print(f"FAILED {len(fails)}/{len(ran)}: {fails}")
        return 1
    print(f"OK — oshares_pit selfcheck PASS {len(ran)}/{len(ran)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selfcheck())
