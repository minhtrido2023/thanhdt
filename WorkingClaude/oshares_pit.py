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
                            fixed, so prefer `oshares_live` whenever it answers; fall back to the
                            quarterly number only where it declines. Strictly better than status
                            quo: every row that falls back is byte-identical to today.

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
SANITY_FACTOR = 3.0


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


def _anchor_is_suspect(cache, tk, asof, rec):
    """Câu trả lời này có đang neo vào một AIS tự mâu thuẫn không? Xem `_suspect_ais`."""
    if not cache or rec.get("anchor_source") != "corporate_action.AIS":
        return False
    try:
        return rec.get("anchor_date") in _suspect_ais(cache[1], tk, asof)
    except Exception:                                       # noqa: BLE001 — total by contract
        return False


def _rec(ticker, value, source, reason, method=None, rel_diff=None, live_value=None):
    return {"ticker": ticker, "value": value, "source": source, "reason": reason,
            "method": method, "rel_diff": rel_diff, "live_value": live_value}


def _suspect_ais(corp, ticker, asof):
    """{effective_date} của những AIS mà `shares_total_after` MÂU THUẪN với chính nó.

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

    Không dựng được kỳ vọng (thiếu `shares_delta`, ISS chắn đường không có tỉ lệ, không có AIS
    liền trước) ⇒ KHÔNG gắn cờ. Cùng nguyên tắc `oshares_live` dùng cho dòng quý: không kiểm
    chứng được thì khác với đã bác bỏ.

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
    bad = set()
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
        if blockers:
            continue                                        # không kiểm chứng được ≠ đã bác bỏ
        cands.append(rolled)                                 # (a)
        delta = cur.get("shares_delta")
        if delta is not None and float(delta) > 0:
            cands.append(base_prev + float(delta))           # (b)
        if all(e > 0 and abs(actual - e) / e > EXPLAIN_TOL for e in cands):
            bad.add(cur["effective_date"])
    return bad


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

    Rows that fall back are IDENTICAL to the caller's current behaviour, so the net effect can only
    be to remove look-ahead, never to introduce a new gap.
    """
    live, cache = _live(tickers, asof, cache)
    out = {}
    for tk in tickers:
        fb = _fallback_value(fallback, tk)
        r = live.get(tk)
        lv = None if r is None or r.get("value") is None else float(r["value"])
        if lv is not None and _anchor_is_suspect(cache, tk, asof, r):
            out[tk] = _rec(tk, fb, "ticker_financial" if fb is not None else "none",
                           f"KHÔNG HỢP LÝ: neo vào AIS {r['anchor_date']} tự mâu thuẫn "
                           f"(total_after ≠ AIS trước + shares_delta) ⇒ bỏ live {lv:,.0f}",
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
        if lv is not None and _anchor_is_suspect(cache, tk, asof, r):
            out[tk] = _rec(tk, fb, "ticker_financial" if fb is not None else "none",
                           f"KHÔNG HỢP LÝ: neo vào AIS {r['anchor_date']} tự mâu thuẫn "
                           f"⇒ bỏ live {lv:,.0f}, giữ số cũ (bq_admin)",
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


def summarize(records):
    """Counts + the worst divergence, for one printed line and one log row."""
    vals = list(records.values())
    diverged = [r for r in vals if r["source"] == "ticker_financial"
                and r["reason"].startswith("LỆCH")]
    insane = [r for r in vals if r["source"] == "ticker_financial"
              and r["reason"].startswith("KHÔNG HỢP LÝ")]
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
                                and not r["reason"].startswith(("LỆCH", "KHÔNG HỢP LÝ"))
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

        print("== Cổng BẤT BIẾN AIS trên dữ liệu THẬT ==")
        cc = fetch_cache(["IDC", "AAA", "FPT", "VNM"], "2026-06-16")
        sus = {t: _suspect_ais(cc[1], t, "2026-06-16") for t in ("IDC", "AAA", "FPT", "VNM")}
        check("A1. IDC 2020-05-28 bị gắn cờ (ca đã kiểm tay 3 nguồn)",
              "2020-05-28" in sus["IDC"], str(sorted(sus["IDC"])))
        check("A2. AAA 2019-06-03 bị gắn cờ — CA MÀ CỔNG THÔ ×3 BỎ LỌT",
              "2019-06-03" in sus["AAA"]
              and _sane(58_664_988.0, 171_199_976.0),      # 0,343 > 1/3 ⇒ cổng thô cho qua
              f"suspects={sorted(sus['AAA'])}; _sane(58,66tr/171,20tr)="
              f"{_sane(58_664_988.0, 171_199_976.0)}")
        # HỒI QUY: bản đầu của `_suspect_ais` cộng cả roll() LẪN delta ⇒ đếm hai lần ⇒ gắn cờ
        # 12/12 AIS của FPT, kể cả dòng mà oshares_live._selfcheck đã chứng minh là ĐÚNG.
        check("A3. HỒI QUY: FPT 2025-09-12 (= 1.703.507.121, đã chứng minh đúng) KHÔNG bị gắn cờ",
              "2025-09-12" not in sus["FPT"], str(sorted(sus["FPT"])))
        check("A4. ĐỐI CHỨNG: có mã KHÔNG có AIS nào bị gắn cờ (cổng không bắt bừa tất cả)",
              len(sus["VNM"]) == 0, f"VNM={sorted(sus['VNM'])}")
        # POINT-IN-TIME: quyết định LOẠI cũng không được dùng dòng của tương lai
        check("A5. PIT: xét tại 2020-01-01 thì AIS 2022-09-05 chưa tồn tại ⇒ không nằm trong tập cờ",
              "2022-09-05" not in _suspect_ais(cc[1], "IDC", "2020-01-01"),
              str(sorted(_suspect_ais(cc[1], "IDC", "2020-01-01"))))
        # BẰNG CHỨNG NGƯỢC: không có cổng bất biến thì AAA THẬT SỰ lọt
        _k = M.SANITY_FACTOR
        _sa = M._suspect_ais
        M._suspect_ais = lambda *_a, **_k2: set()
        try:
            aaa_nogate = M.oshares_pit(["AAA"], "2019-08-05", {"AAA": 171_199_976.0}, cache=cc)
        finally:
            M._suspect_ais, M.SANITY_FACTOR = _sa, _k
        check("A6. CHỨNG MINH NGƯỢC: tắt cổng bất biến ⇒ AAA nhận 58.664.988 (sai −65,7%)",
              aaa_nogate["AAA"]["value"] == 58_664_988.0
              and aaa_nogate["AAA"]["source"] == "oshares_live",
              f"{aaa_nogate['AAA']['value']:,.0f} từ {aaa_nogate['AAA']['source']}")
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
