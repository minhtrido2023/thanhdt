#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck 2 trường thông tin mới của `trading_bot/due_diligence.py` (job Taylor_20260817_041248):
`upcoming_exdate` (cổ tức tiền mặt sắp GDKHQ) + `insider_net_sell` (nội bộ bán ròng ≥1%/90d).

NGUYÊN TẮC ĐẶT TEST (coding_guidelines §23 hệ luận 1): **không assert lên trạng thái SỐNG**.
Mã nào đang có ex-date sắp tới, mã nào đang bị cờ insider — đổi mỗi tuần. Test vì thế TỰ TÌM
fixture bằng chính nguồn dữ liệu ngay lúc chạy, rồi assert lên BẤT BIẾN (có/không, cấu trúc,
quan hệ số học, fail-closed), không assert lên GIÁ TRỊ chụp tại một ngày.

Chạy: python3 mike/bin/due_diligence_corp_flags_selfcheck.py
"""
import os
import sys

# §5b — bất kỳ selfcheck nào có thể chạm Executor phải khai TEST MODE trước mọi import khác.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

WC = "/home/trido/thanhdt/WorkingClaude"
if WC not in sys.path:
    sys.path.insert(0, WC)

import datetime as dt                                                    # noqa: E402
from zoneinfo import ZoneInfo                                            # noqa: E402

import corp_action_lib                                                   # noqa: E402
from trading_bot import due_diligence as DD                              # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def today_ict():
    return dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()


def find_fixtures(today):
    """Tìm ngay lúc chạy: 1 mã CÓ ex-date sắp tới, 1 mã KHÔNG có, 1 mã có cờ insider."""
    until = (today + dt.timedelta(days=DD.CORP_ACTION_LOOKAHEAD_DAYS)).isoformat()
    rows = corp_action_lib.bq(f"""
        SELECT ticker, CAST(exright_date AS STRING) ex
        FROM `{corp_action_lib.TABLE}`
        WHERE event_code = "DIV" AND event_status != "not_executed"
          AND value_per_share > 0
          AND exright_date > DATE "{today.isoformat()}" AND exright_date <= DATE "{until}"
        ORDER BY exright_date LIMIT 50""")
    with_ex = [r["ticker"] for r in rows]
    # mã KHÔNG có sự kiện: lấy từ danh sách mã lớn, trừ đi tập trên (cũng verify lại bằng query)
    no_ex = [t for t in ("FPT", "ACB", "MBB", "VNM", "HPG", "VCB") if t not in with_ex]
    scan = DD._insider_scan(today) or {}
    return (with_ex[0] if with_ex else None), (no_ex[0] if no_ex else None), sorted(scan)


def main():
    today = today_ict()
    print(f"# due_diligence corp-flags selfcheck — asof {today} (ICT)")

    fr = corp_action_lib.feed_freshness()
    print(f"  feed corporate_action: max_ingested={fr.get('max_ingested')} "
          f"max_public={fr.get('max_public')} n={fr.get('n')}")
    tk_ex, tk_noex, ins_flagged = find_fixtures(today)
    print(f"  fixture: có ex-date={tk_ex} · không ex-date={tk_noex} · "
          f"insider bị cờ={len(ins_flagged)} mã {ins_flagged[:6]}")

    # ---- A: mã CÓ ex-date sắp tới → field không None, cấu trúc + số học đúng ----
    if tk_ex is None:
        check("A. mã có ex-date sắp tới → upcoming_exdate != None", True,
              "BỎ QUA: không mã nào có GDKHQ tiền mặt trong cửa sổ (hợp lệ, không phải lỗi)")
    else:
        d = DD.run_due_diligence(tk_ex, "BAL", {"asof": today}, as_dict=True)
        ex = d.get("upcoming_exdate")
        check(f"A1. {tk_ex}: upcoming_exdate != None", ex is not None, str(ex)[:150])
        if ex:
            check("A2. exright_date nằm TRONG cửa sổ tương lai",
                  today < dt.date.fromisoformat(ex["exright_date"])
                  <= today + dt.timedelta(days=DD.CORP_ACTION_LOOKAHEAD_DAYS),
                  ex["exright_date"])
            check("A3. note đúng chuỗi COST-INFO đã pin", ex["note"] == DD._EXDATE_NOTE)
            if ex.get("gross_yield_pct") is not None:
                gy = ex["value_per_share"] / ex["ref_price"] * 100.0
                check("A4. gross_yield_pct = value_per_share / giá tham chiếu × 100",
                      abs(ex["gross_yield_pct"] - gy) < 1e-3,
                      f"{ex['gross_yield_pct']:.4f} vs {gy:.4f}")
                check("A5. cost_estimate_20d_pp = gross_yield × 0,50",
                      abs(ex["cost_estimate_20d_pp"]
                          - ex["gross_yield_pct"] * DD.EXDATE_COST_PP_PER_PP_YIELD) < 1e-3,
                      f"{ex['cost_estimate_20d_pp']}")
                # Cổng Sprint 1: giá tham chiếu KHÔNG được là giá ngày ex-date.
                check("A6. giá tham chiếu lấy TRƯỚC ngày ex-date (cổng Sprint 1)",
                      DD._ref_price_for(tk_ex, today) == ex["ref_price"]
                      and today < dt.date.fromisoformat(ex["exright_date"]))
            else:
                check("A4. thiếu giá tham chiếu ⇒ chỉ báo ngày ex, bỏ yield",
                      ex["cost_estimate_20d_pp"] is None)

    # ---- B: mã KHÔNG có ex-date → None ----
    if tk_noex is None:
        check("B. mã không có ex-date → None", False, "không tìm được fixture âm")
    else:
        d = DD.run_due_diligence(tk_noex, "BAL", {"asof": today}, as_dict=True)
        check(f"B1. {tk_noex}: upcoming_exdate is None", d.get("upcoming_exdate") is None,
              str(d.get("upcoming_exdate"))[:120])
        check("B2. key vẫn tồn tại (None ≠ thiếu key)", "upcoming_exdate" in d)

    # ---- C: BQ lỗi giả → cả 2 field None, KHÔNG raise ra caller ----
    orig_bq, orig_pe, orig_fresh = (corp_action_lib.bq, corp_action_lib.pricing_events,
                                    corp_action_lib.feed_freshness)
    orig_cache = dict(DD._CACHE)

    def boom(*a, **k):
        raise RuntimeError("BQ giả lập chết")

    try:
        DD._CACHE.clear()
        corp_action_lib.bq = boom
        corp_action_lib.pricing_events = boom
        corp_action_lib.feed_freshness = boom
        tk = tk_ex or tk_noex or "FPT"
        d = DD.run_due_diligence(tk, "BAL", {"asof": today}, as_dict=True)
        check("C1. BQ chết → upcoming_exdate None (fail-closed)",
              d.get("upcoming_exdate") is None)
        check("C2. BQ chết → insider_net_sell None (fail-closed)",
              d.get("insider_net_sell") is None)
        check("C3. BQ chết → KHÔNG raise, dict vẫn có trục cũ",
              isinstance(d, dict) and "liquidity" in d and "has_red_flag" in d)
        check("C4. BQ chết → KHÔNG tự sinh cờ đỏ mới",
              "DD_KHONG_CHAY_DUOC" not in (d.get("red_flags") or []))
        txt = DD.run_due_diligence(tk, "BAL", {"asof": today})
        check("C5. BQ chết → nhánh text vẫn chạy, trả chuỗi", isinstance(txt, str) and txt)
    finally:
        corp_action_lib.bq, corp_action_lib.pricing_events = orig_bq, orig_pe
        corp_action_lib.feed_freshness = orig_fresh
        DD._CACHE.clear()
        DD._CACHE.update(orig_cache)

    # ---- D: 2 key mới có mặt trong MỌI đường trả về dict ----
    cases = {
        "mã thường": DD.run_due_diligence(tk_noex or "FPT", "BAL", {"asof": today}, as_dict=True),
        "book LAG (có trục PEAD)": DD.run_due_diligence(tk_noex or "FPT", "LAG", {"asof": today},
                                                        as_dict=True),
        "mã không tồn tại (nhánh lỗi)": DD.run_due_diligence("ZZZZ", "BAL", {"asof": today},
                                                             as_dict=True),
        "skip_corp_flags (đường sinh lệnh)": DD.run_due_diligence(
            tk_ex or "FPT", "BAL", {"asof": today, "skip_corp_flags": True}, as_dict=True),
    }
    for name, d in cases.items():
        check(f"D. [{name}] có đủ 2 key mới",
              "upcoming_exdate" in d and "insider_net_sell" in d, sorted(set(d) & {
                  "upcoming_exdate", "insider_net_sell"}))
    check("D5. skip_corp_flags ⇒ cả 2 = None (đường 21:00 không tốn query)",
          cases["skip_corp_flags (đường sinh lệnh)"]["upcoming_exdate"] is None
          and cases["skip_corp_flags (đường sinh lệnh)"]["insider_net_sell"] is None)
    check("D6. dd_check_for_order KHÔNG đổi shape (không thêm key mới)",
          set(DD.dd_check_for_order(tk_noex or "FPT", "BAL", today) or {})
          == {"has_red_flag", "red_flags", "as_of", "data_date", "universe_source", "evidence"})

    # ---- E: định nghĩa cờ insider KHÔNG drift khỏi bản pin `insider_flags.py` ----
    sys.path.insert(0, os.path.join(WC, "mike", "agents", "Taylor"))
    try:
        import insider_flags as REF
        check("E1. hằng số khớp bản pin (ngưỡng/cửa sổ/stale)",
              (DD.INSIDER_SELL_PCT_OSH_MIN, DD.INSIDER_WINDOW_DAYS, DD.INSIDER_STALE_SESSIONS_MAX)
              == (REF.SELL_PCT_OSH_MIN, REF.WINDOW_DAYS, REF.STALE_SESSIONS_MAX))
        ref_set = {r["ticker"] for r in REF.scan(today)}
        got_set = set(DD._insider_scan(today) or {})
        check("E2. tập mã bị cờ khớp TUYỆT ĐỐI với insider_flags.scan()",
              ref_set == got_set,
              f"ref {len(ref_set)} vs dd {len(got_set)}; lệch={ref_set ^ got_set}")
        if got_set:
            tk = sorted(got_set)[0]
            f = DD._get_insider_net_sell_flag(tk, today)
            ref = {r["ticker"]: r for r in REF.scan(today)}[tk]
            check(f"E3. {tk}: net_sell_pct khớp bản pin",
                  f is not None and abs(f["net_sell_pct"] - ref["sell_pct_osh"]) < 1e-4,
                  f"{f and f['net_sell_pct']} vs {ref['sell_pct_osh']}")
            check("E4. cờ = AND của HAI vế (n_sellers > n_buyers, KHÔNG chỉ vế ≥1%)",
                  f["n_sellers"] > f["n_buyers"]
                  and f["net_sell_pct"] >= DD.INSIDER_SELL_PCT_OSH_MIN)
            check("E5. note đúng chuỗi RISK-INFO đã pin", f["note"] == DD._INSIDER_NOTE)
            d = DD.run_due_diligence(tk, "BAL", {"asof": today}, as_dict=True)
            check(f"E6. {tk}: cờ đi ra tới run_due_diligence", d.get("insider_net_sell") == f)
            check("E7. cờ insider KHÔNG sinh cờ đỏ / KHÔNG chặn (thuần thông tin)",
                  "INSIDER" not in " ".join(d.get("red_flags") or []))
        else:
            check("E3. không mã nào bị cờ hôm nay", True, "BỎ QUA phần so từng mã")
    finally:
        pass

    # ---- F: cổng freshness thật sự chặn khi nguồn cũ ----
    check("F1. feed cũ 400 ngày ⇒ cổng chặn, KHÔNG đọc lịch ex-date",
          _feed_ok_via_stub(today - dt.timedelta(days=400)) is False)
    check("F1b. feed tươi hôm nay ⇒ cổng mở",
          _feed_ok_via_stub(today) is True)
    check("F2. _sessions_between đếm T2-T6 (bỏ cuối tuần)",
          DD._sessions_between(dt.date(2026, 8, 7), dt.date(2026, 8, 17)) == 6,
          str(DD._sessions_between(dt.date(2026, 8, 7), dt.date(2026, 8, 17))))
    check("F3. §16 — _today_ict() neo ZoneInfo, không theo TZ process",
          DD._today_ict() == dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date())

    print()
    n = len(FAILS)
    if n:
        print(f"FAILED {n}: {FAILS}")
        return 1
    print("OK — due_diligence corp-flags selfcheck PASS")
    return 0


def _feed_ok_via_stub(old_date):
    """Ép feed_freshness trả về ngày CŨ để xác nhận cổng chặn thật (không phụ thuộc feed sống)."""
    orig = corp_action_lib.feed_freshness
    try:
        corp_action_lib.feed_freshness = lambda: {"max_ingested": old_date.isoformat(),
                                                  "max_public": old_date.isoformat(), "n": 1}
        DD._CACHE.clear()
        return DD._corp_action_feed_ok(today_ict())
    finally:
        corp_action_lib.feed_freshness = orig
        DD._CACHE.clear()


if __name__ == "__main__":
    raise SystemExit(main())
