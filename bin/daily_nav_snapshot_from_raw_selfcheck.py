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


# Fixture phải là record ĐẦY ĐỦ như trong data/corp_actions.json thật (`event_type` +
# `broker_effective_ts` là trường BẮT BUỘC của `corp_actions.validate()`): từ code-quality
# 2026-09-27 cả ba đường đọc sổ trong daily_nav_snapshot.py đều đi qua `validate()`, nên fixture
# thiếu trường sẽ ném CorpActionError thay vì "được bỏ qua" — đó là hành vi ĐÚNG mới.
def _ca(ticker, ex_date, mult, status, event_type="BONUS_ISSUE"):
    return {"ticker": ticker, "ex_date": ex_date, "qty_multiplier": mult, "_status": status,
            "event_type": event_type, "broker_effective_ts": f"{ex_date}T19:25:01+07:00"}


MSB = [_ca("MSB", "2026-08-28", 1.2, "CONFIRMED — test"),
       _ca("VHM", "2026-08-06", 2.0, "CONFIRMED — test"),
       _ca("XXX", "2026-08-28", 1.2, "PROPOSED — test")]

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

# Biên kiểm tra thêm: nhánh 2 (cash_div_confirmed) đúng khi bất biến khẳng định DƯƠNG —
# in_bq_list=True (BQ đã tự xác nhận CHÍNH mã này pending).
verdict, detail = g(ev_div, qty_now=1000.0, qty_prev=1000.0, price_ref=15_000, mkt_price=14_000,
                    tol_pct=5.0, cum_div_amount=1_000_000, cum_div_tickers=["DRI"],
                    cum_div_warnings=["BQ chưa có phiên hôm nay"])
check("cash_div_confirmed khi in_bq_list=True dù có warning biên độ (net/gross)",
      verdict == "cash_div_confirmed" and abs(detail["expected_amount"] - 1_000_000) < 1,
      (verdict, detail))

# Ghim hằng số dung sai giá cổ tức — mutation 200 → 20.000 SỐNG SÓT ở vòng 1 vì không assertion
# nào chạm tới nó. 20.000đ nuốt trọn cả một cú rơi giá thật (DRI 14.800 → 13.700) nên "cổ tức
# tiền mặt" sẽ khớp cho những ca KHÔNG phải cổ tức.
check("CASH_DIV_PRICE_TOL_VND ghim = 200đ", D.CASH_DIV_PRICE_TOL_VND == 200,
      D.CASH_DIV_PRICE_TOL_VND)
_ev_tol = {"price_adjusting": True, "event_code": "DIV", "value_per_share": 1000.0, "ticker": "DRI"}
_v_tol, _ = g(_ev_tol, qty_now=1000.0, qty_prev=1000.0, price_ref=14_800, mkt_price=13_700,
              tol_pct=5.0, cum_div_amount=1_000_000, cum_div_tickers=["DRI"], cum_div_warnings=[])
check("DRI rơi 1.100đ trong khi cổ tức công bố 1.000đ ⇒ lệch 100đ ≤ 200 ⇒ vẫn confirm",
      _v_tol == "cash_div_confirmed", _v_tol)
_v_tol2, _ = g(_ev_tol, qty_now=1000.0, qty_prev=1000.0, price_ref=14_800, mkt_price=11_000,
               tol_pct=5.0, cum_div_amount=1_000_000, cum_div_tickers=["DRI"], cum_div_warnings=[])
check("rơi 3.800đ ≫ cổ tức 1.000đ (lệch 2.800 > 200) ⇒ KHÔNG confirm — nới TOL lên 20.000 sẽ giết case này",
      _v_tol2 == "unexplained", _v_tol2)

print("5. classify_qty_residual (§29 — phần dư KL sau khi trừ lệnh khớp thật)")
q = D.classify_qty_residual
EV_VIB = {"ticker": "VIB", "date": "2026-09-10", "event_code": "ISS", "price_adjusting": True,
          "exercise_ratio": "0.095"}
EV_BID = {"ticker": "BID", "date": "2026-08-17", "event_code": "ISS", "price_adjusting": True,
          "exercise_ratio": "0.068433"}
EV_DRI = {"ticker": "DRI", "date": "2026-09-22", "event_code": "DIV", "price_adjusting": True,
          "exercise_ratio": "0.1", "value_per_share": "1000.0"}

# Ca THẬT đã đo (dnse_raw + journal, 2026-08-01→09-22): 6 sự kiện × 2 account, phần dư khớp tỉ lệ.
for nm, ev, prev, now, ratio_ok in [
        ("VIB SpaceX 500→547 (0,095 ⇒ 47,5, broker làm tròn 47)", EV_VIB, 500.0, 547.0, True),
        ("VIB ZaloPay 200→219", EV_VIB, 200.0, 219.0, True),
        ("BID SpaceX 1.100→1.175 (0,068433 ⇒ 75,28)", EV_BID, 1100.0, 1175.0, True)]:
    v, d = q(ev, qty_now=now, qty_prev=prev, net_fill=0.0, prev_date="2026-09-08")
    check(f"(5a) {nm} ⇒ share_event_credit", v == "share_event_credit", (v, d))

# §29 — chính lỗi mục [2]: MUA đúng phiên cum thì KL đổi mà KHÔNG phải credit sớm.
v, d = q(EV_VIB, qty_now=600.0, qty_prev=500.0, net_fill=100.0, prev_date="2026-09-08")
check("(5b) KL +100 do MUA 100 cùng mã ⇒ ok, KHÔNG rc=5 giả (bỏ net_fill sẽ giết case này)",
      v == "ok", (v, d))
v, d = q(EV_VIB, qty_now=447.0, qty_prev=500.0, net_fill=-100.0, prev_date="2026-09-08")
check("(5c) vừa BÁN 100 vừa credit 47 ⇒ vẫn bắt được phần dư +47 khớp tỉ lệ",
      v == "share_event_credit" and abs(d["residual"] - 47.0) < 1e-9, (v, d))

# gap D: KL đổi thật nhưng LỊCH không có sự kiện nào ⇒ phải CHẶN, và nói đúng là "chưa giải thích".
v, d = q(None, qty_now=1200.0, qty_prev=1000.0, net_fill=0.0, prev_date="2026-09-21")
check("(5d) gap D — KL +200 không lệnh khớp, lịch KHÔNG có sự kiện ⇒ qty_unexplained (CHẶN)",
      v == "qty_unexplained" and d["ex_date"] is None, (v, d))
v, d = q(EV_VIB, qty_now=700.0, qty_prev=500.0, net_fill=0.0, prev_date="2026-09-08")
check("(5e) lịch CÓ sự kiện nhưng phần dư +200 ≠ tỉ lệ 0,095 (47,5) ⇒ qty_unexplained, KHÔNG "
      "được khẳng định 'credit sớm thật'",
      v == "qty_unexplained" and d["evidence"] == "residual_not_explained_by_fills_or_ratio", (v, d))

# exercise_ratio của DIV là tỉ lệ trên MỆNH GIÁ, không phải tỉ lệ cổ phiếu — dùng nhầm sẽ
# "giải thích" khống đúng 10% KL. Bỏ điều kiện `event_code != "DIV"` sẽ giết case này.
v, d = q(EV_DRI, qty_now=1100.0, qty_prev=1000.0, net_fill=0.0, prev_date="2026-09-21")
check("(5f) DIV ratio 0,1 KHÔNG được dùng giải thích KL +10% ⇒ qty_unexplained",
      v == "qty_unexplained" and "exercise_ratio" not in d, (v, d))

v, d = q(EV_VIB, qty_now=547.0, qty_prev=None, net_fill=None, prev_date=None)
check("(5g) qty_prev=None (mã mới mua / thiếu file ngày trước) ⇒ ok, fail-open KHÔNG chặn",
      v == "ok" and d is None, (v, d))
v, d = q(EV_VIB, qty_now=500.0, qty_prev=500.0, net_fill=0.0, prev_date="2026-09-08")
check("(5h) KL không đổi dù lịch có sự kiện ⇒ ok (chống over-block theo LỊCH, lỗi v1)",
      v == "ok", (v, d))

print("6. _corp_action_daily_snapshot + _corp_action_gate_status (§14 — gate phải NÓI khi bị tắt tiếng)")
with tempfile.TemporaryDirectory() as tmp:
    import corp_action_daily as _cad
    _old_dir = getattr(_cad, "OUT_DIR", None)
    _old_path = _cad.snapshot_path
    _cad.snapshot_path = lambda d: os.path.join(tmp, f"corp_action_daily_{d}.json")
    try:
        check("(6a) thiếu file ⇒ None (im lặng, KHÔNG phải lỗi)",
              D._corp_action_daily_snapshot("2026-09-22") is None)
        with open(os.path.join(tmp, "corp_action_daily_2026-09-19.json"), "w") as f:
            f.write('{"asof": "2026-09-19", "status": "OK"')     # JSON hỏng (thiếu })
        check("(6b) JSON hỏng ⇒ None + có cảnh báo (không nuốt im lặng)",
              D._corp_action_daily_snapshot("2026-09-19") is None)
        good = {"asof": "2026-09-22", "status": "OK", "usable": True, "feed_status": "FRESH",
                "upcoming_events_held": []}
        with open(os.path.join(tmp, "corp_action_daily_2026-09-22.json"), "w") as f:
            json.dump(good, f)
        check("(6c) file OK ⇒ đọc được", D._corp_action_daily_snapshot("2026-09-22") == good)
    finally:
        _cad.snapshot_path = _old_path

a, n = D._corp_action_gate_status(None, "2026-09-22")
check("(6d) snapshot None ⇒ active=False + note nói rõ nhánh KL vẫn chạy",
      a is False and "KHỐI LƯỢNG vẫn chạy" in n, (a, n))
# Producer CÓ fail thật: corp_action_daily_2026-08-27_FAILED.json tồn tại trên đĩa.
a, n = D._corp_action_gate_status({"asof": "2026-08-27", "status": "FAILED", "usable": False},
                                  "2026-08-27")
check("(6e) status=FAILED / usable=False ⇒ active=False", a is False and "FAILED" in n, (a, n))
a, n = D._corp_action_gate_status({"asof": "2026-09-19", "status": "OK", "usable": True},
                                  "2026-09-22")
check("(6f) snapshot của NGÀY KHÁC (asof lệch) ⇒ active=False — không tin lịch cũ",
      a is False and "asof" in n, (a, n))
a, n = D._corp_action_gate_status({"asof": "2026-09-22", "status": "OK", "usable": True,
                                   "feed_status": "FRESH"}, "2026-09-22")
check("(6g) asof đúng + OK + usable ⇒ active=True", a is True, (a, n))

print("7. held_event_next_session — biên PHIÊN (cuối tuần + nghỉ lễ), KHÔNG phải ngày lịch")
_snap_bid = {"upcoming_events_held": [dict(EV_BID)]}
check("(7a) T6 14/08 → phiên kế tiếp T2 17/08 = ex-date ⇒ KHỚP (days_ahead thô = 3, sẽ trượt)",
      D.held_event_next_session(_snap_bid, "2026-08-14", "BID") is not None)
check("(7b) T5 13/08 → phiên kế tiếp 14/08 ≠ 17/08 ⇒ KHÔNG khớp",
      D.held_event_next_session(_snap_bid, "2026-08-13", "BID") is None)
# Nghỉ Quốc khánh 31/08–02/09/2026: phiên sau T6 28/08 là T5 03/09 (KHÔNG phải 31/08).
_snap_hol = {"upcoming_events_held": [{"ticker": "ZZZ", "date": "2026-09-03",
                                       "price_adjusting": True, "event_code": "ISS"}]}
check("(7c) nghỉ lễ 31/08–02/09: T6 28/08 → phiên kế tiếp 03/09 ⇒ KHỚP",
      D.held_event_next_session(_snap_hol, "2026-08-28", "ZZZ") is not None)
_snap_hol2 = {"upcoming_events_held": [{"ticker": "ZZZ", "date": "2026-08-31",
                                        "price_adjusting": True, "event_code": "ISS"}]}
check("(7d) 31/08 là ngày NGHỈ ⇒ không bao giờ là 'phiên kế tiếp' của 28/08",
      D.held_event_next_session(_snap_hol2, "2026-08-28", "ZZZ") is None)
check("(7e) snapshot None ⇒ None (không nổ)", D.held_event_next_session(None, "2026-09-22", "VIB") is None)
check("(7f) mã khác không khớp", D.held_event_next_session(_snap_bid, "2026-08-14", "VIB") is None)

print("8. previous_raw_qty — thiếu file / mã mới ⇒ (None, None), KHÔNG chặn")
with tempfile.TemporaryDirectory() as tmp:
    _old = D.EXEC_DIR
    D.EXEC_DIR = tmp
    try:
        def _pos(acct, ts, rows):
            return {"kind": "positions", "ts": ts, "account_no": acct,
                    "payload": {"positions": rows}}
        check("(8a) KHÔNG có file dnse_raw nào ⇒ (None, None)",
              D.previous_raw_qty("A1", "VIB", "2026-09-09") == (None, None))
        with open(os.path.join(tmp, "dnse_raw_2026-09-08.jsonl"), "w") as f:
            f.write(json.dumps(_pos("A1", "2026-09-08T19:00:00",
                                    [{"symbol": "VIB", "openQuantity": 500, "marketPrice": 21000}])) + "\n")
        check("(8b) có file ngày trước ⇒ (500, '2026-09-08')",
              D.previous_raw_qty("A1", "VIB", "2026-09-09") == (500.0, "2026-09-08"))
        check("(8c) mã MỚI mua (không có trong bản ghi trước) ⇒ (None, ngày) ⇒ gate fail-open",
              D.previous_raw_qty("A1", "VPI", "2026-09-09") == (None, "2026-09-08"))
        check("(8d) account KHÁC (§12 lọc tuyệt đối) ⇒ (None, None)",
              D.previous_raw_qty("A2", "VIB", "2026-09-09") == (None, None))
        check("(8e) chỉ lấy ngày TRƯỚC `date`, không lấy chính ngày đó",
              D.previous_raw_qty("A1", "VIB", "2026-09-08") == (None, None))
    finally:
        D.EXEC_DIR = _old

print("9. net_fills_between — cột `qty` của FILL là LŨY KẾ theo child_oid, KHÔNG cộng dồn")
with tempfile.TemporaryDirectory() as tmp:
    import verify_account_snapshot as V
    _oldD, _oldV = D.EXEC_DIR, V.EXEC_DIR
    D.EXEC_DIR = V.EXEC_DIR = tmp
    try:
        hdr = "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n"
        # Ca THẬT VCB 2026-08-10: 2 dòng FILL cùng child_oid 54871 (200 rồi 400 LŨY KẾ),
        # DONE ghi "khớp đủ 400". Cộng dồn ⇒ 600 (sai 200) ⇒ phần dư giả ⇒ rc=5 oan.
        with open(os.path.join(tmp, "exec_A1_2026-08-10_journal.csv"), "w") as f:
            f.write(hdr)
            f.write("2026-08-10T09:16:31,FILL,SELL-VCB,VCB,sell,54871,200,60200.0,0,PARK,JIT,\n")
            f.write("2026-08-10T09:16:51,FILL,SELL-VCB,VCB,sell,54871,400,60200.0,200,PARK,JIT,\n")
        with open(os.path.join(tmp, "exec_A1_2026-08-11_journal.csv"), "w") as f:
            f.write(hdr)
            f.write("2026-08-11T09:18:53,FILL,BUY-VCB,VCB,buy,45081,200,60500.0,0,PARK,PARK_ADD,\n")
        r = D.net_fills_between("A1", "2026-08-09", "2026-08-10")
        check("(9a) 2 dòng lũy kế 200→400 của CÙNG child ⇒ −400, KHÔNG phải −600",
              r.get("VCB") == -400.0, r)
        r = D.net_fills_between("A1", "2026-08-09", "2026-08-11")
        check("(9b) cửa sổ 2 ngày: −400 (bán) +200 (mua) = −200", r.get("VCB") == -200.0, r)
        r = D.net_fills_between("A1", "2026-08-10", "2026-08-11")
        check("(9c) biên MỞ bên trái: (10, 11] chỉ tính ngày 11 ⇒ +200", r.get("VCB") == 200.0, r)
        check("(9d) không có ngày nào trong khoảng ⇒ rỗng",
              D.net_fills_between("A1", "2026-08-11", "2026-08-12") == {})
        _c = {}
        D.net_fills_between("A1", "2026-08-09", "2026-08-10", _c)
        check("(9e) cache dùng được", ("A1", "2026-08-09", "2026-08-10") in _c, _c)
        # [N2] arch-review vòng 3 — §28/§29: ngày GIAO DỊCH thiếu journal phải NÓI RA, không
        # được để "lệnh khớp thật +0" thành suy diễn từ SỰ VẮNG MẶT. `journal_fill_events` chỉ
        # trả err cho ca thiếu file mà vòng lặp chỉ duyệt file CÓ THẬT (glob) ⇒ giữ mỗi `_err`
        # là VÔ DỤNG; phải đối chiếu NGƯỢC với lịch phiên.
        _m = []
        r = D.net_fills_between("A1", "2026-08-09", "2026-08-11", missing_out=_m)
        check("(9f) 08-09→08-11 có đủ 2 journal ⇒ KHÔNG báo thiếu ngày nào",
              r.get("VCB") == -200.0 and _m == [], _m)
        _m = []
        # 08-12 (Thứ Tư) là ngày GIAO DỊCH và KHÔNG có journal ⇒ phải lộ ra.
        r = D.net_fills_between("A1", "2026-08-11", "2026-08-12", missing_out=_m)
        check("(9g) ngày giao dịch thiếu journal ⇒ liệt kê ra, out vẫn rỗng (không đoán +0)",
              r == {} and len(_m) == 1 and _m[0].startswith("2026-08-12:")
              and "exec_A1_2026-08-12_journal.csv" in _m[0], _m)
        _m = []
        # 08-15 Thứ Bảy / 08-16 Chủ Nhật KHÔNG phải ngày giao dịch ⇒ thiếu journal là BÌNH
        # THƯỜNG (42-43/53 ngày), không được báo động giả.
        D.net_fills_between("A1", "2026-08-14", "2026-08-16", missing_out=_m)
        check("(9h) cuối tuần thiếu journal ⇒ KHÔNG báo (chỉ đếm ngày giao dịch)", _m == [], _m)
        _m2 = []
        _c2 = {}
        D.net_fills_between("A1", "2026-08-11", "2026-08-12", _c2)
        D.net_fills_between("A1", "2026-08-11", "2026-08-12", _c2, missing_out=_m2)
        check("(9i) cache trả lại CẢ danh sách ngày thiếu, không nuốt mất",
              len(_m2) == 1 and _m2[0].startswith("2026-08-12:"), _m2)
    finally:
        D.EXEC_DIR, V.EXEC_DIR = _oldD, _oldV

print("10. confirmed_share_event_multiplier — đường PHỤC HỒI --from-raw (mục [1])")
# Ca THẬT VIB: corp_action_auto_confirm.py ghi CONFIRMED lúc 2026-09-09T19:25:01, mult 1.095.
ACTS = [_ca("VIB", "2026-09-10", 1.095,
            "CONFIRMED — corp_action_auto_confirm.py 2026-09-09T19:25:01+07:00"),
        _ca("VPB", "2026-09-24", 1.2604104, "PROPOSED — chưa ai ký")]
m = D.confirmed_share_event_multiplier
check("(10a) VIB ngày 09-09, ex 09-10, CONFIRMED ⇒ 1.095 (bỏ điều kiện CONFIRMED thì (10b) chết)",
      m("VIB", "2026-09-09", "2026-09-10", ACTS) == 1.095)
check("(10b) VPB PROPOSED (chưa ký) ⇒ None — mô hình tin cậy KHÔNG đổi",
      m("VPB", "2026-09-22", "2026-09-24", ACTS) is None)
check("(10c) ex_date ĐÃ qua ⇒ None", m("VIB", "2026-09-10", None, ACTS) is None)
check("(10d) ex_date truyền vào KHÁC ex_date của bản ghi ⇒ None (không vơ bừa sự kiện khác)",
      m("VIB", "2026-09-09", "2026-09-11", ACTS) is None)
check("(10e) mã không có bản ghi ⇒ None", m("ZZZ", "2026-09-09", None, ACTS) is None)

print("11. _write_json_atomic (§5) — ghi hỏng giữa chừng KHÔNG được để lại file dở")
with tempfile.TemporaryDirectory() as tmp:
    f = os.path.join(tmp, "nav_gate_block_A1_2026-09-09.json")
    with open(f, "w", encoding="utf-8") as fh:
        fh.write('{"nav": 123}')
    try:
        # set không serialize được ⇒ json.dump nổ GIỮA CHỪNG. Ghi thẳng vào file đích (không
        # atomic) sẽ truncate mất nội dung cũ; tmp + os.replace thì file cũ còn nguyên.
        D._write_json_atomic(f, {"x": {1, 2}})
        _raised = False
    except TypeError:
        _raised = True
    check("(11a) lỗi serialize được ném ra, không nuốt", _raised)
    check("(11b) file cũ còn NGUYÊN sau lần ghi hỏng (ghi trực tiếp sẽ giết case này)",
          open(f, encoding="utf-8").read() == '{"nav": 123}',
          open(f, encoding="utf-8").read())
    D._write_json_atomic(f, {"nav": None, "rc": 5})
    check("(11c) ghi thành công thì thay được nội dung",
          json.load(open(f, encoding="utf-8"))["rc"] == 5)

print("12. cash_block_reject_reason — CẢ BA guard §25 (code-quality 2026-09-27)")
# Bản cũ chỉ có bản copy cục bộ `_stock_all_zero` ⇒ hai hình dạng lỗi feed (12b)/(12c) LỌT
# NGUYÊN VẸN và ghi một dòng NAV sai vào nav_history. park_holdings.py đã có đủ ba guard từ
# 2026-08-09 (quant-skeptic REFUTED 2 vòng mới ra đủ) — đây là tái dùng, không viết lại.
import park_holdings as _PH  # noqa: E402

r = D.cash_block_reject_reason
check("(12a) block stock TOÀN SỐ 0 ⇒ từ chối",
      r({"totalCash": 0, "totalDebt": 0, "availableCash": 0, "depositInterest": 0}) is not None)
check("(12b) CHỈ ba field tiền = 0, depositInterest còn sống ⇒ từ chối "
      "(guard _cash_fields_all_zero; bản cũ LỌT)",
      r({"totalCash": 0, "totalDebt": 0, "availableCash": 0, "depositInterest": 318.0})
      is not None)
check("(12c) totalCash 0 < availableCash 5.000.000 ⇒ từ chối "
      "(bất biến kế toán; bản cũ LỌT)",
      r({"totalCash": 0, "totalDebt": 0, "availableCash": 5_000_000.0,
         "depositInterest": 318.0}) is not None)
check("(12d) block tiền LÀNH MẠNH (số thật SpaceX 2026-08-07) ⇒ None, không chặn oan",
      r({"totalCash": 203_656_265.0, "totalDebt": 0.0, "availableCash": 4_821_143.0,
         "depositInterest": 1_200.0}) is None)
check("(12e) 0 đồng tiền mặt HỢP LỆ (availableCash=0 nhưng totalDebt sống) ⇒ None",
      r({"totalCash": 0.0, "totalDebt": 50_000_000.0, "availableCash": 0.0,
         "depositInterest": 318.0}) is None)
check("(12f) ba guard là CHÍNH hàm của park_holdings, không phải bản copy "
      "(chống lệch lại — park_holdings.py:148)",
      D._stock_block_all_zero is _PH._stock_block_all_zero
      and D._cash_fields_all_zero is _PH._cash_fields_all_zero
      and D._cash_fields_inconsistent is _PH._cash_fields_inconsistent)
check("(12g) alias `_stock_all_zero` (previous_balance dùng) trỏ về guard đã import",
      D._stock_all_zero is _PH._stock_block_all_zero)


print("13. MỘT đường đọc corp_actions.json duy nhất (code-quality 2026-09-27)")
# Trước bản vá, CÙNG file parse sổ theo 2 luật khác nhau: `confirmed_qty_multiplier_after()` đã
# qua `corp_actions.validate()` (§29 vòng 6) và CHẶN NAV khi sổ hỏng, còn `classify_raw_price_gap`
# + `confirmed_share_event_multiplier` mở file thô + `except (TypeError, ValueError): continue`
# ⇒ BỎ QUA IM LẶNG. Một sổ hỏng cho hai kết luận khác nhau tuỳ đường nào chạm tới trước.
import corp_actions as _CA  # noqa: E402

_BAD = [
    ("qty_multiplier = nan (mọi so sánh ngưỡng ÂM THẦM False — §29)",
     _ca("MSB", "2026-08-28", float("nan"), "CONFIRMED — test")),
    ("qty_multiplier = '1,30' (dấu phẩy kiểu VN, float() nổ ValueError)",
     _ca("MSB", "2026-08-28", "1,30", "CONFIRMED — test")),
    ("qty_multiplier = 13 (gõ tay thiếu dấu chấm, > QTY_MULT_MAX)",
     _ca("MSB", "2026-08-28", 13, "CONFIRMED — test")),
    ("qty_multiplier = 1.0 (sổ này chỉ mô tả sự kiện LÀM TĂNG KL)",
     _ca("MSB", "2026-08-28", 1.0, "CONFIRMED — test")),
    ("ex_date = '28/08/2026' (không phải ISO)",
     _ca("MSB", "28/08/2026", 1.2, "CONFIRMED — test")),
]
for _why, _rec in _BAD:
    _raised = []
    for _fname, _call in (
            ("classify_raw_price_gap",
             lambda r=_rec: D.classify_raw_price_gap("MSB", "2026-08-27", 15_700, 15_650,
                                                    13_100, 5.0, [r])),
            ("confirmed_share_event_multiplier",
             lambda r=_rec: D.confirmed_share_event_multiplier("MSB", "2026-08-27", None, [r])),
    ):
        try:
            _call()
        except _CA.CorpActionError:
            _raised.append(_fname)
        except Exception as _e:                                   # noqa: BLE001
            _raised.append(f"{_fname}:SAI_LOẠI({type(_e).__name__})")
    check(f"(13) record hỏng — {_why} — CẢ HAI đường ném CorpActionError (bản cũ bỏ qua im lặng)",
          _raised == ["classify_raw_price_gap", "confirmed_share_event_multiplier"], _raised)

# Ba đường PHẢI là cùng một hàm đọc — không phải ba khối parse giống nhau (chống lệch lại).
_src13 = open(os.path.join(os.path.dirname(os.path.abspath(D.__file__)),
                           "daily_nav_snapshot.py"), encoding="utf-8").read()
check("(13x) daily_nav_snapshot.py KHÔNG còn mở CORP_ACTIONS_FILE thô ở bất kỳ đâu",
      "CORP_ACTIONS_FILE, encoding" not in _src13 and "open(CORP_ACTIONS_FILE" not in _src13)
import ast as _ast13  # noqa: E402
_t13 = _ast13.parse(_src13)
# Đếm bằng AST, KHÔNG bằng chuỗi: hai DOCSTRING trong file cố ý nhắc `except (TypeError,
# ValueError)` để giải thích bản cũ sai ở đâu ⇒ phép đếm chuỗi tính cả lời giải thích (đã xảy ra
# khi viết mục này). Handler HỢP LỆ duy nhất còn lại nằm ở `classify_qty_residual`, và nó đọc
# `ev["exercise_ratio"]` của corp_action_daily snapshot — NGUỒN KHÁC, không phải corp_actions.json.
_tv_owners = sorted(
    fn.name
    for fn in _ast13.walk(_t13) if isinstance(fn, _ast13.FunctionDef)
    for h in _ast13.walk(fn)
    if isinstance(h, _ast13.ExceptHandler) and isinstance(h.type, _ast13.Tuple)
    and {getattr(x, "id", None) for x in h.type.elts} == {"TypeError", "ValueError"})
check("(13y) `except (TypeError, ValueError)` chỉ còn ở `classify_qty_residual` (đọc "
      "exercise_ratio của corp_action_daily — NGUỒN KHÁC), không còn ở đường đọc corp_actions.json",
      _tv_owners == ["classify_qty_residual"], _tv_owners)


def _calls13(fn):
    f = next(n for n in _ast13.walk(_t13)
             if isinstance(n, _ast13.FunctionDef) and n.name == fn)
    return {n.func.id for n in _ast13.walk(f)
            if isinstance(n, _ast13.Call) and isinstance(n.func, _ast13.Name)}


for _fn in ("confirmed_qty_multiplier_after", "classify_raw_price_gap",
            "confirmed_share_event_multiplier"):
    check(f"(13z) `{_fn}` đọc sổ qua `confirmed_actions_after()` — MỘT đường duy nhất",
          "confirmed_actions_after" in _calls13(_fn), sorted(_calls13(_fn)))

# CHỨNG MINH NGƯỢC: sổ LÀNH vẫn cho đúng kết quả cũ (guard mới không chặn oan) — đã phủ ở mục 1
# và 10, khẳng định lại ở đây trên CÙNG record đầy đủ để hai mục không thể trôi khỏi nhau.
check("(13w) record ĐẦY ĐỦ, hợp lệ ⇒ vẫn early_credit 1,2 như mục 1",
      D.classify_raw_price_gap("MSB", "2026-08-27", 15_700, 15_650, 13_100, 5.0,
                               MSB) == ("early_credit", 1.2))
check("(13v) record ĐẦY ĐỦ, hợp lệ ⇒ confirmed_share_event_multiplier vẫn 1.095 như mục 10",
      D.confirmed_share_event_multiplier("VIB", "2026-09-09", "2026-09-10", ACTS) == 1.095)

print(f"\n{len(PASS)} PASS, {len(FAIL)} FAIL")
sys.exit(1 if FAIL else 0)
