#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `daily_nav_snapshot.py --from-raw` (aria-A2, 2026-09-13).

Chạy:  python3 mike/bin/daily_nav_snapshot_from_raw_selfcheck.py
Phải PASS y hệt khi chạy từ thư mục khác và không có TZ:
       cd /tmp && env -u TZ python3 <repo>/mike/bin/daily_nav_snapshot_from_raw_selfcheck.py

Fixture tổng hợp + số thật đã đo (giá PVT/MSB/VHM tháng 8) đóng băng thành hằng số — không đọc
dnse_raw thật, không gọi broker, không gọi BQ. Khoá 3 thứ:
  1. classify_raw_price_gap: chỉ chấp nhận lệch giá khi có bằng chứng cơ khí (feed trễ 1 phiên
     hoặc broker ghi có corp-action sớm); ca VHM 06/08 (BQ Price đứng giá cũ) PHẢI bị từ chối.
  2. raw_positions: lọc account tuyệt đối (§12), gộp loan package, lấy bản ghi CUỐI + ts.
  3. cum_dividend_double_count nhận positions dạng dict {"qty","marketPrice"} của main() —
     bản cũ TypeError (dict × float) ngay khi có cổ tức chờ ex-date.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import daily_nav_snapshot as D  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


MSB = [{"ticker": "MSB", "ex_date": "2026-08-28", "qty_multiplier": 1.2, "_status": "CONFIRMED — test"},
       {"ticker": "VHM", "ex_date": "2026-08-06", "qty_multiplier": 2.0, "_status": "CONFIRMED — test"},
       {"ticker": "XXX", "ex_date": "2026-08-28", "qty_multiplier": 1.2, "_status": "PROPOSED — test"}]

print("1. classify_raw_price_gap")
c = D.classify_raw_price_gap
check("lệch 2,1% ⇒ ok", c("LPB", "2026-07-21", 54_600, 53_000, 53_500, 5.0, MSB) == ("ok", None))
check("PVT 10/08: marketPrice 18.350 = giá phiên trước ⇒ stale_market_price",
      c("PVT", "2026-08-10", 19_400, 18_350, 18_350, 5.0, MSB) == ("stale_market_price", None))
check("MSB 27/08: 15.700/1,2 ≈ 13.100, ex 28/08 CONFIRMED ⇒ early_credit 1,2",
      c("MSB", "2026-08-27", 15_700, 15_650, 13_100, 5.0, MSB) == ("early_credit", 1.2))
check("VHM 06/08: Price 153.000 (=phiên trước), mp 76.500, ex_date = CHÍNH ngày ⇒ unexplained",
      c("VHM", "2026-08-06", 153_000, 153_000, 76_500, 5.0, MSB) == ("unexplained", None))
check("corp-action PROPOSED không được dùng làm lý do",
      c("XXX", "2026-08-27", 15_700, 15_650, 13_100, 5.0, MSB) == ("unexplained", None))
check("ex_date ĐÃ qua không phải ghi có sớm",
      c("MSB", "2026-08-29", 15_700, 15_650, 13_100, 5.0, MSB) == ("unexplained", None))

print("2. raw_positions")
with tempfile.TemporaryDirectory() as tmp:
    old = D.EXEC_DIR
    D.EXEC_DIR = tmp
    try:
        def pos_rec(acct, ts, rows):
            return {"kind": "positions", "ts": ts, "account_no": acct, "payload": {"positions": rows}}
        with open(os.path.join(tmp, "dnse_raw_2026-08-10.jsonl"), "w") as f:
            for rec in (
                pos_rec("A1", "2026-08-10T15:00", [{"symbol": "AAA", "openQuantity": 999, "marketPrice": 1}]),
                pos_rec("A1", "2026-08-10T19:12", [{"symbol": "AAA", "openQuantity": 300, "marketPrice": 10},
                                                   {"symbol": "AAA", "openQuantity": 200, "marketPrice": 10},
                                                   {"symbol": "BBB", "openQuantity": 0, "marketPrice": 5}]),
                pos_rec("A2", "2026-08-10T19:13", [{"symbol": "CCC", "openQuantity": 7, "marketPrice": 3}]),
                pos_rec(None, "2026-08-10T19:14", [{"symbol": "DDD", "openQuantity": 7, "marketPrice": 3}]),
            ):
                f.write(json.dumps(rec) + "\n")
            f.write("{hỏng\n")
        pos, ts = D.raw_positions("A1", "2026-08-10")
        check("bản ghi CUỐI của A1, gộp loan package 300+200, bỏ KL 0",
              pos == {"AAA": {"qty": 500.0, "marketPrice": 10}}, pos)
        check("ts của bản ghi đó", ts == "2026-08-10T19:12", ts)
        check("bản ghi account khác / thiếu tag không lọt", "CCC" not in pos and "DDD" not in pos, pos)
        check("account không có bản ghi ⇒ (None, None)", D.raw_positions("ZZ", "2026-08-10") == (None, None))
        check("không có file ngày ⇒ (None, None)", D.raw_positions("A1", "2026-08-11") == (None, None))
    finally:
        D.EXEC_DIR = old

print("3. cum_dividend_double_count với positions dạng dict")


class Adj:
    def __init__(self, ticker, last_cum, ex, per_share):
        self.ticker, self.last_cum_date, self.ex_date, self.per_share = ticker, last_cum, ex, per_share


def bal(ts, cd):
    return {"ts": ts, "payload": {"stock": {"cashDividendReceiving": cd}}}


events = {"CTG": [Adj("CTG", "2026-07-22", "2026-07-23", 450.0)],
          "VCB": [Adj("VCB", "2026-07-22", "2026-07-23", 450.0)]}
positions = {"CTG": {"qty": 2300.0, "marketPrice": 1}, "VCB": {"qty": 1300.0, "marketPrice": 1}}
try:
    r = D.cum_dividend_double_count("A1", "2026-07-22", positions, bal("2026-07-22T19:10", 2_475_000),
                                    bal("2026-07-21T19:10", 855_000), events=events,
                                    bq_max_date="2026-07-24")
    check("SpaceX 22/07 số thật: trừ 1.620.000, expected_bq = (2300+1300)×450",
          abs(r["amount"] - 1_620_000) < 1 and abs(r["expected_bq"] - 1_620_000) < 1
          and not r["warnings"], r)
except TypeError as e:
    check("không TypeError với positions dict", False, e)
r = D.cum_dividend_double_count("A1", "2026-07-22", {"CTG": 2300, "VCB": 1300},
                                bal("2026-07-22T19:10", 2_475_000), bal("2026-07-21T19:10", 855_000),
                                events=events, bq_max_date="2026-07-24")
check("dạng {mã: qty} của selfcheck cũ vẫn chạy như trước", abs(r["expected_bq"] - 1_620_000) < 1, r)

print("4. classify_corp_action_gap (corp_action_gate_v2, job Taylor_20260922_111128)")
g = D.classify_corp_action_gap

# (a) FAIL-CLOSED: khoản cổ tức ĐÃ nằm trong tiền (không còn pending) — mã không có trong
# cum_div_tickers và amount tổng không khớp kỳ vọng của riêng mã này. Đảo `bool(cum_div_amount)`
# thành hằng True hoặc bỏ check `in_bq_list or magnitude_ok` sẽ làm test này chết.
ev_div = {"price_adjusting": True, "event_code": "DIV", "value_per_share": 1000.0, "ticker": "DRI"}
verdict, detail = g(ev_div, qty_now=1000.0, qty_prev=1000.0, price_ref=15_000, mkt_price=14_000,
                    tol_pct=5.0, cum_div_amount=0, cum_div_tickers=[], cum_div_warnings=[])
check("(a) cổ tức đã nằm trong tiền (amount=0, không pending) ⇒ unexplained, FAIL-CLOSED",
      verdict == "unexplained", (verdict, detail))
verdict2, _ = g(ev_div, qty_now=1000.0, qty_prev=1000.0, price_ref=15_000, mkt_price=14_000,
                tol_pct=5.0, cum_div_amount=250_000, cum_div_tickers=["OTHER"],
                cum_div_warnings=[])
check("(a2) amount thuộc mã KHÁC (không khớp expected, không trong tickers) ⇒ unexplained",
      verdict2 == "unexplained", verdict2)

# (b) Sự kiện cổ phiếu tỉ lệ NHỎ (~1%, giá rơi <5% nên PRICE_XCHECK cũ không bắt được — lỗ
# hổng L4 đã biết) vẫn PHẢI bị chặn, vì nhánh 1 dựa KHỐI LƯỢNG, không phụ thuộc biên độ giá.
ev_share_small = {"price_adjusting": True, "event_code": "ISSUE", "exercise_ratio": "100:1",
                  "issue_method_vi": "Phát hành thêm", "ticker": "XYZ", "date": "2026-09-23"}
verdict, detail = g(ev_share_small, qty_now=101_000.0, qty_prev=100_000.0, price_ref=50_000,
                    mkt_price=49_600, tol_pct=5.0, cum_div_amount=0, cum_div_tickers=[],
                    cum_div_warnings=[])
check("(b) sự kiện cổ phiếu ~1% (giá rơi 0,8% <5%) vẫn bị chặn (share_event_block)",
      verdict == "share_event_block", (verdict, detail))

# (c) qty KHÔNG đổi (qty_moved=False) dù lịch có sự kiện + giá trong dung sai ⇒ KHÔNG được
# chặn — chống over-block (~10/28 phiên đo thật khi dò theo LỊCH thay vì bằng chứng credit).
ev_share_noop = {"price_adjusting": True, "event_code": "ISSUE", "exercise_ratio": "100:1",
                 "ticker": "VPB", "date": "2026-09-24"}
verdict, detail = g(ev_share_noop, qty_now=100_000.0, qty_prev=100_000.0, price_ref=20_000,
                    mkt_price=20_000, tol_pct=5.0, cum_div_amount=0, cum_div_tickers=[],
                    cum_div_warnings=[])
check("(c) qty_moved=False + lịch có sự kiện + giá trong dung sai ⇒ ok, KHÔNG chặn",
      verdict == "ok", (verdict, detail))

# Biên kiểm tra thêm: nhánh 2 (cash_div_confirmed) đúng khi bất biến khẳng định DƯƠNG —
# in_bq_list=True (BQ đã tự xác nhận CHÍNH mã này pending).
verdict, detail = g(ev_div, qty_now=1000.0, qty_prev=1000.0, price_ref=15_000, mkt_price=14_000,
                    tol_pct=5.0, cum_div_amount=1_000_000, cum_div_tickers=["DRI"],
                    cum_div_warnings=["BQ chưa có phiên hôm nay"])
check("cash_div_confirmed khi in_bq_list=True dù có warning biên độ (net/gross)",
      verdict == "cash_div_confirmed" and abs(detail["expected_amount"] - 1_000_000) < 1,
      (verdict, detail))

print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
sys.exit(1 if FAIL else 0)
