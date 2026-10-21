#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B2 — chuỗi NAV qua sự kiện QUYỀN MUA (SCL-like) trên FIXTURE GIẢ, không chạm file thật.

Chạy:  python3 agents/Taylor/research/lag_rights_audit_20261022/b2_nav_chain.py [--bq]
  --bq  thêm mục F: chạy dividend_adjusted_return THẬT trên BQ cho SCL quanh ex 2025-10-17 (chỉ đọc).

Kịch bản (giá SCL thật từ tav2_bq.ticker, đo 2026-10-22):
  * giữ 14.000 SCL giá vốn 30.000; quyền mua 0,35714286 (14:5) giá 12.500 (total_value 1e11 /
    issue_volumn 8e6), GDKHQ 2025-10-17, ĐKCC 2025-10-20, niêm yết 2026-01-29 (corporate_action).
  * Price: 10-15 22.600 · 10-16 22.200 · 10-17 21.700 · 10-24 20.500 · 10-27 20.000 ·
    11-04 19.900 · 11-05 20.500 · 2026-01-28 20.800 · 2026-01-29 21.000.
  * ngày nộp tiền GIẢ ĐỊNH 2025-10-27 (5.000 cp, tiền −62.500.000).
  * dạng A (ĐO trên tiền lệ MBB 2026-08-28): openQuantity +5.000 NGAY khi nộp, tradeQuantity giữ,
    costPrice bình quân lại gồm giá phát hành. dạng B (GIẢ ĐỊNH): KL chỉ tăng ngày niêm yết.

AN TOÀN: mọi ghi file bị chặn nếu đích nằm ngoài thư mục tạm của lượt chạy (guard trên open/
os.replace/os.rename); không broker, không notify, không append_event.
"""
import builtins
import contextlib
import csv
import datetime
import io
import json
import os
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BIN = os.path.join(WT, "bin")
sys.path.insert(0, BIN)

ROOT_TMP = tempfile.mkdtemp(prefix="b2_nav_chain_")
os.environ["VERIFY_ACCOUNT_EXEC_DIR"] = ROOT_TMP           # trước khi import V
os.environ["VERIFY_ACCOUNT_KNOWN_DISCREPANCIES"] = os.path.join(ROOT_TMP, "kd_none.json")

# ---------------- write guard ----------------
_real_open, _real_replace, _real_rename = builtins.open, os.replace, os.rename
ALLOWED = (ROOT_TMP, "/tmp/")


def _chk(path):
    p = os.path.realpath(str(path))
    if not any(p.startswith(os.path.realpath(a)) for a in ALLOWED):
        raise PermissionError(f"B2 GUARD: chặn ghi ngoài sandbox: {p}")


def _open(file, mode="r", *a, **k):
    if isinstance(file, (str, bytes, os.PathLike)) and any(c in mode for c in "wax+"):
        _chk(file)
    return _real_open(file, mode, *a, **k)


def _replace(src, dst, *a, **k):
    _chk(dst)
    return _real_replace(src, dst, *a, **k)


builtins.open, os.replace = _open, _replace
os.rename = lambda s, d, *a, **k: (_chk(d), _real_rename(s, d, *a, **k))[1]

import daily_nav_snapshot as D  # noqa: E402
import corp_action_daily as CAD  # noqa: E402
import verify_account_snapshot as V  # noqa: E402
import exdate_frame as EF  # noqa: E402
import cash_identity as CI  # noqa: E402
import dividend_adjusted_return as DAR  # noqa: E402
import reconcile_equity as RE  # noqa: E402

ACCT, ACCT_NO, TK = "SpaceX", "0002023347", "SCL"
Q0, COST, R, S, RQ = 14000.0, 30000.0, 0.35714286, 12500.0, 5000.0
CASH_BUY = 899_592_600.0        # 1.32 tỷ − 14.000×30.000 − phí 0,097%
PRICE = {"2025-10-01": 30000.0, "2025-10-15": 22600.0, "2025-10-16": 22200.0,
         "2025-10-17": 21700.0, "2025-10-24": 20500.0, "2025-10-27": 20000.0,
         "2025-11-04": 19900.0, "2025-11-05": 20500.0, "2026-01-28": 20800.0,
         "2026-01-29": 21000.0}
TERP_1016 = round((22200 * 14 + S * 5) / 19 / 50) * 50     # 19.650 — giá tham chiếu sau quyền
RIGHTS_EV = {"ticker": TK, "date": "2025-10-17", "event_code": "ISS", "price_adjusting": True,
             "exercise_ratio": "0.35714286", "issue_method_vi": "Quyền mua CP cho Cổ đông hiện hữu",
             "value_per_share": None, "event_status": "executed"}
SDIV_EV = {"ticker": TK, "date": "2025-11-06", "event_code": "ISS", "price_adjusting": True,
           "exercise_ratio": "0.09", "issue_method_vi": "Trả Cổ tức bằng Cổ phiếu",
           "value_per_share": None, "event_status": "executed"}
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


# ---------------- fixture builders ----------------
def pos_rec(ts, qty, mp, trade=None, cost=None):
    return {"kind": "positions", "ts": ts, "account_no": ACCT_NO, "payload": {"positions": [
        {"symbol": TK, "accountNo": ACCT_NO, "openQuantity": qty,
         "tradeQuantity": qty if trade is None else trade, "marketPrice": mp,
         "costPrice": COST if cost is None else cost, "status": "OPEN", "loanPackageId": 1841}]}}


def bal_rec(ts, cash, debt=0.0):
    return {"kind": "balances", "ts": ts, "account_no": ACCT_NO, "payload": {
        "stock": {"totalCash": cash, "availableCash": cash, "totalDebt": debt,
                  "withdrawableCash": cash, "depositInterest": 1000.0, "depositFeeAmount": 0.0,
                  "cashDividendReceiving": 0.0, "secureAmount": 0.0, "orderSecured": 0.0},
        "egg": {"totalValue": 0.0}}}


def buy_order_rec(date):
    return {"kind": "orders", "ts": f"{date}T15:00:00", "account_no": ACCT_NO, "payload": {"orders": [
        {"id": 1, "accountNo": ACCT_NO, "symbol": TK, "side": "NB", "fillQuantity": Q0,
         "averagePrice": COST, "price": COST, "modifiedDate": f"{date}T02:30:00Z",
         "createdDate": f"{date}T02:20:00Z", "orderStatus": "Filled"}]}}


def write_raw(d, date, recs):
    with open(os.path.join(d, f"dnse_raw_{date}.jsonl"), "a", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


JHDR = "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n"


def write_journal(d, date, rows=()):
    with open(os.path.join(d, f"exec_{ACCT}_{date}_journal.csv"), "w", encoding="utf-8") as f:
        f.write(JHDR)
        for r in rows:
            f.write(r + "\n")


def rights_journal_row(date, qty=RQ):
    # đúng khuôn tiền lệ MBB-RIGHTS-2026-08-28 (data/execution_logs/exec_SpaceX_2026-08-28_journal.csv)
    return (f"{date}T10:04:48,FILL,{TK}-RIGHTS-{date},{TK},buy,{TK}-RIGHTS-SPACEX-{date},{int(qty)},"
            f"{S},{int(qty)},CORP_ACTION,RIGHTS_SUBSCRIPTION,")


def write_nav_hist(d, rows):
    fn = ["date", "nav", "mtm_stock", "cash", "margin_debt", "offbook_assets", "egg_assets",
          "balance_ts", "cum_dividend_excl", "nav_is_estimate", "nav_source"]
    with open(os.path.join(d, f"nav_history_{ACCT}.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fn)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fn})


def hist_row(date, qty, px, cash, ts):
    return {"date": date, "nav": f"{qty * px + cash:.0f}", "mtm_stock": f"{qty * px:.0f}",
            "cash": f"{cash:.0f}", "margin_debt": "0", "offbook_assets": "0", "egg_assets": "0",
            "balance_ts": ts, "cum_dividend_excl": "0", "nav_is_estimate": "False", "nav_source": "fx"}


def write_ca_snapshot(d, date, events):
    with open(os.path.join(d, f"corp_action_daily_{date}.json"), "w", encoding="utf-8") as f:
        json.dump({"asof": date, "status": "OK", "usable": True, "feed_status": "FRESH",
                   "upcoming_events_held": events}, f)


def write_corp_actions(d, actions=()):
    with open(os.path.join(d, "corp_actions.json"), "w", encoding="utf-8") as f:
        json.dump({"actions": list(actions)}, f)


def sdiv_confirmed():
    return {"id": "SCL-2025-11-06-SDIV", "ticker": TK, "event_type": "STOCK_DIVIDEND",
            "qty_multiplier": 1.09, "ex_date": "2025-11-06",
            "broker_effective_ts": "2025-11-05T19:30:00", "_status": "CONFIRMED — fixture"}


def day_fixture(d, prev, date, q_prev, q_now, mp_prev, mp_now, cash_prev, cash_now,
                trade_now=None, cost_now=None, events=(), journal=(), ts="19:10:00"):
    write_raw(d, prev, [pos_rec(f"{prev}T19:05:00", q_prev, mp_prev),
                        bal_rec(f"{prev}T19:05:10", cash_prev)])
    write_raw(d, date, [pos_rec(f"{date}T{ts}", q_now, mp_now, trade_now, cost_now),
                        bal_rec(f"{date}T{ts[:6]}20", cash_now)])
    write_journal(d, "2025-10-01")   # để trading_dates_with_fills ≠ rỗng
    write_journal(d, prev)
    write_journal(d, date, journal)
    write_ca_snapshot(d, date, list(events))
    write_corp_actions(d)
    write_nav_hist(d, [hist_row(prev, q_prev, PRICE.get(prev, mp_prev), cash_prev,
                                f"{prev}T19:05:10")])


# ---------------- runner: daily_nav_snapshot.main() ----------------
class _Stub:
    class R:
        returncode, stdout, stderr = 0, "", ""

    @staticmethod
    def run(*a, **k):
        return _Stub.R()


def run_nav(d, date, prev, from_raw=True, live_positions=None, live_close=None):
    old = (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path, D.bq_raw_prices,
           D.cum_dividend_double_count, sys.argv, V.EXEC_DIR, D.broker_positions,
           V.dnse_close_prices, D.subprocess, os.environ.get("NAV_SANITY_MAX_PCT"))
    D.EXEC_DIR = V.EXEC_DIR = d
    D.CORP_ACTIONS_FILE = os.path.join(d, "corp_actions.json")
    D.HISTORY_FILE_TMPL = os.path.join(d, "nav_history_{account}.csv")
    CAD.snapshot_path = lambda x, failed=False: os.path.join(d, f"corp_action_daily_{x}.json")
    D.bq_raw_prices = lambda tickers, dt_: ({t: PRICE[date] for t in tickers},
                                             {t: PRICE[prev] for t in tickers}, None)
    D.cum_dividend_double_count = lambda *a, **k: {
        "amount": 0.0, "delta": 0.0, "expected_bq": None, "tickers": [], "bq_max_date": None,
        "note": "", "warnings": []}
    if not from_raw:
        D.broker_positions = lambda *a, **k: json.loads(json.dumps(live_positions))
        V.dnse_close_prices = lambda tickers, with_source=False: dict(live_close)
        D.subprocess = _Stub
    os.environ.pop("NAV_SANITY_MAX_PCT", None)       # ngưỡng 15% MẶC ĐỊNH thật
    sys.argv = ["daily_nav_snapshot.py", "--account", ACCT, "--account-no", ACCT_NO,
                "--date", date] + (["--from-raw"] if from_raw else [])
    err, out = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            rc = D.main()
    finally:
        (D.EXEC_DIR, D.CORP_ACTIONS_FILE, D.HISTORY_FILE_TMPL, CAD.snapshot_path, D.bq_raw_prices,
         D.cum_dividend_double_count, sys.argv, V.EXEC_DIR, D.broker_positions,
         V.dnse_close_prices, D.subprocess, envv) = old
        if envv is not None:
            os.environ["NAV_SANITY_MAX_PCT"] = envv
    snap_p = os.path.join(d, f"nav_snapshot_{ACCT}_{date}.json")
    snap = json.load(open(snap_p)) if os.path.exists(snap_p) else None
    blk_p = os.path.join(d, f"nav_gate_block_{ACCT}_{date}.json")
    blk = json.load(open(blk_p)) if os.path.exists(blk_p) else None
    return rc, err.getvalue(), out.getvalue(), snap, blk


def short(s, n=420):
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n] + " …"


def newdir(tag):
    d = os.path.join(ROOT_TMP, tag)
    os.makedirs(d)
    return d


def nav_case(tag, prev, date, **kw):
    d = newdir(tag)
    from_raw = kw.pop("from_raw", True)
    live = kw.pop("live", None)
    acts = kw.pop("corp_actions", None)
    day_fixture(d, prev, date, **kw)
    if acts is not None:
        write_corp_actions(d, acts)
    lp = lc = None
    if live:
        lp = {TK: {"qty": kw["q_now"], "marketPrice": kw["mp_now"]}}
        lc = {TK: live}
    rc, err, out, snap, blk = run_nav(d, date, prev, from_raw=from_raw, live_positions=lp, live_close=lc)
    say(f"\n[{tag}] rc={rc}")
    if snap:
        say(f"   NAV={snap['nav']:,.0f} mtm={snap['mtm_stock']:,.0f} cash={snap['cash']:,.0f} "
            f"day_change={snap['day_change']:+,.0f} ({snap['day_change'] / snap['prev_nav'] * 100:+.2f}%) "
            f"qty_adj={snap['corp_action_qty_adj']}")
    if blk:
        g = blk["corp_action_gate_v2"]
        say("   nav_gate_block:", short(json.dumps({"share_event_blocks": g["share_event_blocks"],
                                                     "qty_unexplained": g["qty_unexplained"]},
                                                    ensure_ascii=False), 600))
    if err.strip():
        say("   stderr:", short(err))
    return rc, snap, blk, d


# ============================ A. daily_nav_snapshot ============================
say("=" * 100)
say("A. daily_nav_snapshot.py — cổng KL (classify_qty_residual) + cổng giá + bước nhảy")
say(f"   TERP tự dựng 10-16 = {TERP_1016:,} (=(22.200×14+12.500×5)/19, làm tròn 50đ)")

C_PREV, C = "2025-10-15", "2025-10-16"
nav_case("A1_cum_evening_mp_adjusted_fromraw", C_PREV, C, q_prev=Q0, q_now=Q0,
         mp_prev=22600, mp_now=TERP_1016, cash_prev=CASH_BUY, cash_now=CASH_BUY, events=[RIGHTS_EV])
nav_case("A1b_cum_evening_mp_not_adjusted_fromraw", C_PREV, C, q_prev=Q0, q_now=Q0,
         mp_prev=22600, mp_now=22200, cash_prev=CASH_BUY, cash_now=CASH_BUY, events=[RIGHTS_EV])

TODAY = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).date().isoformat()
YEST = (datetime.date.fromisoformat(TODAY) - datetime.timedelta(days=1)).isoformat()
PRICE[TODAY], PRICE[YEST] = 22200.0, 22600.0
ev_live = dict(RIGHTS_EV, date=D.__dict__.get("next_trading_day", None) or "")
from trading_bot.vn_market import next_trading_day  # noqa: E402
ev_live["date"] = next_trading_day(datetime.date.fromisoformat(TODAY)).isoformat()
nav_case("A1_live_cum_evening_mp_adjusted", YEST, TODAY, q_prev=Q0, q_now=Q0, mp_prev=22600,
         mp_now=TERP_1016, cash_prev=CASH_BUY, cash_now=CASH_BUY, events=[ev_live],
         from_raw=False, live=22200.0)

nav_case("A2_exdate_T0_fromraw", C, "2025-10-17", q_prev=Q0, q_now=Q0, mp_prev=TERP_1016,
         mp_now=21700, cash_prev=CASH_BUY, cash_now=CASH_BUY)

P_PREV, P = "2025-10-24", "2025-10-27"
CASH_PAID = CASH_BUY - RQ * S
COST_BLEND = (Q0 * COST + RQ * S) / (Q0 + RQ)
nav_case("A3_payday_formA_no_journal_fromraw", P_PREV, P, q_prev=Q0, q_now=Q0 + RQ, mp_prev=20500,
         mp_now=20000, cash_prev=CASH_BUY, cash_now=CASH_PAID, trade_now=Q0, cost_now=COST_BLEND)
nav_case("A3_payday_formA_manual_journal_fromraw", P_PREV, P, q_prev=Q0, q_now=Q0 + RQ,
         mp_prev=20500, mp_now=20000, cash_prev=CASH_BUY, cash_now=CASH_PAID, trade_now=Q0,
         cost_now=COST_BLEND, journal=[rights_journal_row(P)])
PRICE[TODAY], PRICE[YEST] = 20000.0, 20500.0
nav_case("A3_live_payday_formA_no_journal", YEST, TODAY, q_prev=Q0, q_now=Q0 + RQ, mp_prev=20500,
         mp_now=20000, cash_prev=CASH_BUY, cash_now=CASH_PAID, trade_now=Q0, cost_now=COST_BLEND,
         from_raw=False, live=20000.0)
nav_case("A3_payday_formB_qty_unchanged_fromraw", P_PREV, P, q_prev=Q0, q_now=Q0, mp_prev=20500,
         mp_now=20000, cash_prev=CASH_BUY, cash_now=CASH_PAID)

L_PREV, L = "2026-01-28", "2026-01-29"
nav_case("A4_listing_formB_qty_jump_fromraw", L_PREV, L, q_prev=Q0, q_now=Q0 + RQ, mp_prev=20800,
         mp_now=21000, cash_prev=CASH_PAID, cash_now=CASH_PAID)
nav_case("A4_listing_formA_only_tradeQty_changes_fromraw", L_PREV, L, q_prev=Q0 + RQ,
         q_now=Q0 + RQ, mp_prev=20800, mp_now=21000, cash_prev=CASH_PAID, cash_now=CASH_PAID,
         trade_now=Q0 + RQ)

SD_PREV, SD = "2025-11-04", "2025-11-05"
MP_SD = round(20500 / 1.09)
for tag, qp, qn, acts in [
        ("A5_control_no_rights_sdiv_9pct_CONFIRMED_fromraw", Q0, Q0 + 1260, [sdiv_confirmed()]),
        ("A5_rights_pending_NOT_entitled_sdiv_credit1260_CONFIRMED_fromraw", Q0 + RQ, Q0 + RQ + 1260,
         [sdiv_confirmed()]),
        ("A5_rights_pending_entitled_sdiv_credit1710_CONFIRMED_fromraw", Q0 + RQ, Q0 + RQ + 1710,
         [sdiv_confirmed()]),
        ("A5_rights_pending_NOT_entitled_sdiv_credit1260_NOT_confirmed_fromraw", Q0 + RQ,
         Q0 + RQ + 1260, [])]:
    nav_case(tag, SD_PREV, SD, q_prev=qp, q_now=qn, mp_prev=19900, mp_now=MP_SD,
             cash_prev=CASH_PAID, cash_now=CASH_PAID, events=[SDIV_EV], corp_actions=acts)


# ============================ B. exdate_frame (compute_active_nav gate) ============================
say("\n" + "=" * 100)
say("B. exdate_frame.classify_positions + verify_post_event_price (cổng của compute_active_nav)")


def ef_case(tag, prev, date, q_prev, q_now, events, journal=(), px_cum=None, mp=None, mult=None):
    d = newdir("B_" + tag)
    day_fixture(d, prev, date, q_prev=q_prev, q_now=q_now, mp_prev=mp or 0, mp_now=mp or 0,
                cash_prev=CASH_PAID, cash_now=CASH_PAID, events=events, journal=journal)
    old = (D.EXEC_DIR, V.EXEC_DIR, CAD.snapshot_path)
    D.EXEC_DIR = V.EXEC_DIR = d
    CAD.snapshot_path = lambda x, failed=False: os.path.join(d, f"corp_action_daily_{x}.json")
    try:
        credited, blocked = EF.classify_positions(ACCT, ACCT_NO, date,
                                                  {TK: {"total": q_now, "marketPrice": mp}})
    finally:
        D.EXEC_DIR, V.EXEC_DIR, CAD.snapshot_path = old
    say(f"\n[B_{tag}] credited={list(credited)} blocked={list(blocked)}")
    for tk, why in blocked.items():
        say("   blocked:", short(why, 360))
    for tk, det in credited.items():
        px, why = EF.verify_post_event_price(px_cum, mp, 1.0 + float(det["exercise_ratio"]))
        say(f"   credited residual={det['residual']:+,.0f} → verify_post_event_price={px} ({short(why, 200)})")
    return credited, blocked


ef_case("cum_evening_rights_qty_unchanged", C_PREV, C, Q0, Q0, [RIGHTS_EV], mp=TERP_1016)
ef_case("payday_formA_no_journal", P_PREV, P, Q0, Q0 + RQ, [], mp=20000)
ef_case("payday_formA_manual_journal", P_PREV, P, Q0, Q0 + RQ, [], journal=[rights_journal_row(P)],
        mp=20000)
ef_case("listing_formB", L_PREV, L, Q0, Q0 + RQ, [], mp=21000)
ef_case("sdiv_cum_rights_pending_not_entitled_1260", SD_PREV, SD, Q0 + RQ, Q0 + RQ + 1260, [SDIV_EV],
        px_cum=20500, mp=MP_SD)
ef_case("sdiv_cum_rights_pending_entitled_1710", SD_PREV, SD, Q0 + RQ, Q0 + RQ + 1710, [SDIV_EV],
        px_cum=20500, mp=MP_SD)
# Lớp hệ quy chiếu trên chính quyền mua: nếu KL quyền có lúc rơi đúng phiên kế tiếp ex-date quyền
# mua (không xảy ra với DNSE theo tiền lệ MBB, chỉ để đo nhánh giá): residual 5.000 = 14.000×0,357
cr, bl = ef_case("HYPOTHETICAL_rights_qty_credited_on_cum_evening", C_PREV, C, Q0, Q0 + RQ,
                 [RIGHTS_EV], px_cum=22200, mp=TERP_1016)


# ============================ C. verify_account_snapshot ============================
say("\n" + "=" * 100)
say("C. verify_account_snapshot.py — giá vốn / P&L sau ngày nộp tiền (dạng A)")


def vas_case(tag, journal_rights, kd=None):
    d = newdir("C_" + tag)
    write_raw(d, "2025-10-01", [buy_order_rec("2025-10-01"),
                                pos_rec("2025-10-01T19:00:00", Q0, 30000),
                                bal_rec("2025-10-01T19:00:10", CASH_BUY)])
    write_journal(d, "2025-10-01", [f"2025-10-01T09:30:00,FILL,P1,{TK},buy,C1,{int(Q0)},{COST},"
                                    f"{int(Q0)},LAG,PEAD,"])
    write_raw(d, P, [pos_rec(f"{P}T19:10:00", Q0 + RQ, 20000, Q0, COST_BLEND),
                     bal_rec(f"{P}T19:10:20", CASH_PAID)])
    write_journal(d, P, [rights_journal_row(P)] if journal_rights else [])
    kdp = os.path.join(d, "kd.json")
    with open(kdp, "w") as f:
        json.dump({"discrepancies": kd or []}, f)
    out_json = os.path.join(d, f"verified_snapshot_{ACCT}_{P}.json")
    old = (V.EXEC_DIR, V.KNOWN_DISCREPANCY_PATH, V.bq_close_prices, sys.argv)
    V.EXEC_DIR, V.KNOWN_DISCREPANCY_PATH = d, kdp
    V.bq_close_prices = lambda tickers, asof: ({t: PRICE[asof] for t in tickers}, None)
    sys.argv = ["verify_account_snapshot.py", "--account", ACCT, "--account-no", ACCT_NO,
                "--dates", f"2025-10-01,{P}", "--asof", P, "--out", out_json]
    err, out = io.StringIO(), io.StringIO()
    rc = 0
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            try:
                V.main()
            except SystemExit as e:
                rc = e.code
    finally:
        V.EXEC_DIR, V.KNOWN_DISCREPANCY_PATH, V.bq_close_prices, sys.argv = old
    res = json.load(open(out_json))
    p = res["positions"][0] if res["positions"] else {}
    say(f"\n[C_{tag}] rc={rc} verified={res['verified']} qty={p.get('qty')} "
        f"true_avg_cost={p.get('true_avg_cost')} unrealized={p.get('unrealized_pnl', 0):+,.0f} "
        f"({p.get('unrealized_pnl_pct', 0):+.2f}%) total_mtm={res['total_mtm_value']:,.0f}")
    say("   warnings:", short(json.dumps(res["warnings"], ensure_ascii=False), 500))
    say(f"   broker (dnse_raw positions): openQuantity={Q0 + RQ:,.0f} costPrice={COST_BLEND:,.2f} "
        f"⇒ broker unrealized={(Q0 + RQ) * (PRICE[P] - COST_BLEND):+,.0f}")
    return d, out_json


dC, snapC = vas_case("formA_no_journal", False)
vas_case("formA_manual_journal_no_ack", True)
vas_case("formA_manual_journal_with_known_discrepancy", True,
         kd=[{"account": ACCT, "ticker": TK, "qty_delta": RQ, "reason": "fixture rights",
              "expires_at": "2099-01-01"}])


# ============================ D. reconcile_equity ============================
say("\n" + "=" * 100)
say("D. reconcile_equity.py — đẳng thức vốn sau ngày nộp tiền (dạng A, snapshot mục C)")
old = (V.EXEC_DIR, DAR.EXEC_LOG_DIR, sys.argv)
V.EXEC_DIR = DAR.EXEC_LOG_DIR = dC
sys.argv = ["reconcile_equity.py", "--account", ACCT, "--account-no", ACCT_NO,
            "--starting-capital", "1320000000", "--snapshot", snapC,
            "--balance-raw", os.path.join(dC, f"dnse_raw_{P}.jsonl")]
err, out = io.StringIO(), io.StringIO()
rc = 0
try:
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
        try:
            RE.main()
        except SystemExit as e:
            rc = e.code
finally:
    V.EXEC_DIR, DAR.EXEC_LOG_DIR, sys.argv = old
rj = json.load(open(snapC.replace("verified_snapshot", "reconcile_equity")))
say(f"[D] rc={rc} lhs={rj['lhs_pnl_path']:,.0f} rhs={rj['rhs_balance_sheet_path']:,.0f} "
    f"residual={rj['residual']:+,.0f} ({rj['residual_pct_of_rhs']:+.3f}%) "
    f"within_tolerance={rj['within_tolerance']} unexplained_after_estimates={rj['unexplained_after_estimates']:+,.0f}")
for ln in out.getvalue().splitlines():
    if "CHƯA" in ln or "Residual" in ln or "CHÊNH" in ln:
        say("   stdout:", short(ln, 260))


# ============================ E. cash_identity ============================
say("\n" + "=" * 100)
say("E. cash_identity.py — cửa sổ chứa ngày nộp tiền quyền mua")


def ci_case(tag, q_now, seed_fill=False):
    d = newdir("E_" + tag)
    seed = os.path.join(d, "seed.json")
    with open(seed, "w") as f:
        json.dump({ACCT: {"missing_fills_broker_confirmed": [
            {"date": P, "ticker": TK, "side": "buy", "qty": RQ, "price": S,
             "evidence": "fixture: quyền mua"}]}} if seed_fill else {}, f)
    write_raw(d, P_PREV, [pos_rec(f"{P_PREV}T19:05:00", Q0, 20500), bal_rec(f"{P_PREV}T19:05:10", CASH_BUY)])
    write_raw(d, P, [pos_rec(f"{P}T19:10:00", q_now, 20000, Q0, COST_BLEND if q_now > Q0 else COST),
                     bal_rec(f"{P}T19:10:20", CASH_PAID)])
    write_nav_hist(d, [hist_row(P_PREV, Q0, 20500, CASH_BUY, f"{P_PREV}T19:05:10"),
                       hist_row(P, q_now, 20000, CASH_PAID, f"{P}T19:10:20")])
    inc = os.path.join(d, "inc.json")
    with open(inc, "w") as f:
        json.dump({ACCT: {"account_no": ACCT_NO, "inception_date": "2025-09-30"}}, f)
    flows = os.path.join(d, "flows.json")
    with open(flows, "w") as f:
        json.dump({"flows": []}, f)
    with open(os.path.join(d, "acks.json"), "w") as f:
        json.dump({}, f)
    write_corp_actions(d)
    try:
        res = CI.check_account(ACCT, nav_dir=d, raw_dir=d, flows_path=flows, inception_path=inc,
                               seed_path=seed,
                               acks_path=os.path.join(d, "acks.json"),
                               corp_actions_path=os.path.join(d, "corp_actions.json"))
    except Exception as e:                       # noqa: BLE001
        say(f"[E_{tag}] LỖI {type(e).__name__}: {e}")
        return
    for w in res["windows"]:
        if w.get("checkable"):
            say(f"[E_{tag}] {w['date0']}→{w['date1']} delta_k={w['delta_k']:+,.0f} "
                f"unexplained={w['unexplained']:+,.0f} ({w['pct_nav']:+.3f}%) kind={w['kind']!r} "
                f"qty_gaps={w['qty_gaps']} suspect={w['suspect']}")
            if w["kind"]:
                say("   line:", short(CI.suspect_line(ACCT, w), 700))
        else:
            say(f"[E_{tag}] uncheckable: {w.get('reason')}")


ci_case("formA_shares_same_window", Q0 + RQ)
ci_case("formB_no_shares", Q0)
ci_case("formA_with_seed_missing_fill_rights", Q0 + RQ, seed_fill=True)


# ============================ F. dividend_adjusted_return (BQ thật, tuỳ chọn) ============================
if "--bq" in sys.argv[1:] or os.environ.get("B2_BQ") == "1":
    say("\n" + "=" * 100)
    say("F. dividend_adjusted_return — resolve_dividends THẬT cho SCL 2025-10-01→2025-10-31 (BQ, chỉ đọc)")
    try:
        adjs = DAR.resolve_dividends([TK], "2025-10-01", "2025-10-31", with_crosscheck=False)
        for a in adjs:
            say(f"   {a.ticker} ex={a.ex_date} kind={a.kind} resolved={a.resolved} "
                f"mult={a.share_multiplier} cash_per_share={a.cash_per_share} "
                f"vendor_check={a.vendor_check} note={short(a.note or '', 160)}")
        pr = DAR.build_position_return(TK, Q0, COST, PRICE["2025-10-27"], adjs)
        say(f"   build_position_return(14000@30000 → 20000): unverified={[a.ex_date for a in pr.unverified]} "
            f"div/cp={pr.dividend_per_share} mult={pr.share_multiplier}")
        for nm in ("total_return_pct", "price_return_pct", "total_return"):
            if hasattr(pr, nm):
                say(f"   {nm}={getattr(pr, nm)}")
    except Exception as e:                       # noqa: BLE001
        say(f"   LỖI {type(e).__name__}: {e}")

say(f"\n(sandbox: {ROOT_TMP})")
with _real_open(os.path.join(HERE, "b2_nav_chain_output.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
