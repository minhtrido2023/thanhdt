#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fixture dùng chung cho B2b/B3 (audit quyền mua LAG, 2026-10-22). CHỈ sandbox tạm (mkdtemp):
bootstrap giả + journal giả + dnse_raw giả, account giả RightsAcct/8888888888. KHÔNG ghi vào
data/, mike/data, mike/state; KHÔNG gọi DNSE/BQ/bus (env test-mode đặt TRƯỚC mọi import).
Tái dùng khuôn của bin/auto_exit_inject_selfcheck.py (patch_all_e2e: sửa park_holdings.__defaults__,
account_profile, load_corp_actions) và bin/compute_park_trim_selfcheck.py (STATE_FILE tạm)."""
import os
os.environ["MIKE_BOT_TEST_MODE"] = "1"      # §5b — TRƯỚC mọi import trading_bot
os.environ["AUTO_EXIT_TEST_MODE"] = "1"     # auto_exit_inject: không bus/notify
import csv
import json
import sys
import tempfile

WT_BIN = "/home/trido/thanhdt/WorkingClaude/wt-lag-rights-20261022/bin"
sys.path.insert(0, WT_BIN)
import wc_paths  # noqa: E402
WC_ROOT = wc_paths.find_wc_root(os.path.join(WT_BIN, "x.py"))
sys.path.insert(0, WC_ROOT)

import park_holdings as ph  # noqa: E402
from trading_bot.vn_market import next_trading_day  # noqa: E402,F401

ACCOUNT = "RightsAcct"
ACCOUNT_NO = "8888888888"
OTHER_NO = "7777777777"           # record account khác trong cùng file — kiểm §12
DAY0 = "2026-10-01"
LAG_TK = "SCL"
QTY_OLD = 14_000
QTY_NEW = 5_000                   # 14:5 ⇒ 35,714286%
RIGHTS_PX = 12_500
PX_CUM = 30_000
PX_EX = 25_400                    # (30.000 + 5/14×12.500)/(19/14) = 25.394,7 → bước 50đ
PAYMENT = QTY_NEW * RIGHTS_PX     # 62.500.000đ
PARK = {"FPT": (6_000, 100_000), "MBB": (30_000, 25_000)}   # PARK 600tr + 750tr = 1.350tr


def nth_session_after(start, n):
    d = start
    for _ in range(n):
        d = next_trading_day(d)
    return d


def sandbox():
    td = tempfile.mkdtemp(prefix="lag_rights_b3_")
    ex, pl = os.path.join(td, "execution_logs"), os.path.join(td, "trade_plans")
    os.makedirs(ex)
    os.makedirs(pl)
    snap = {"_status": "APPROVED by audit fixture", "account_label": ACCOUNT,
            "account_no": ACCOUNT_NO, "day0_date": DAY0,
            "broker_source": {"file": "fixture", "ts": f"{DAY0}T00:00:00"}, "reconcile_ok": True,
            "positions": [{"ticker": tk, "qty": q, "book": "custom30V_parking",
                           "entry_date": DAY0, "cost_price_vnd": px}
                          for tk, (q, px) in PARK.items()]}
    with open(os.path.join(pl, f"bootstrap_book_snapshot_{ACCOUNT}_{DAY0.replace('-', '')}.json"),
              "w") as f:
        json.dump(snap, f)
    return td, ex, pl


JCOLS = ["ts", "event", "parent_id", "child_oid", "ticker", "side", "qty", "price", "book",
         "play_type"]


def write_journal(exec_dir, date, fills):
    """fills = [(ticker, side, qty, price, book)] — FILL qty tích luỹ theo child_oid (mỗi fill 1 oid)."""
    p = os.path.join(exec_dir, f"exec_{ACCOUNT}_{date}_journal.csv")
    new = not os.path.exists(p)
    with open(p, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=JCOLS)
        if new:
            w.writeheader()
        for i, (tk, side, q, px, book) in enumerate(fills):
            w.writerow({"ts": f"{date}T09:30:0{i}", "event": "FILL", "parent_id": f"P-{tk}-{date}",
                        "child_oid": f"C-{tk}-{date}-{i}", "ticker": tk, "side": side, "qty": q,
                        "price": px, "book": book, "play_type": "LAG_LO" if book == "LAG" else ""})


def write_raw(exec_dir, date, lag_open, lag_trade, lag_mp, cash_total, cash_avail, debt=0.0,
              egg=300e6, lag_cost=PX_CUM, extra_rows=()):
    """dnse_raw_{date}.jsonl: positions + balances của account + 1 record nhiễu của account khác."""
    rows = [{"accountNo": ACCOUNT_NO, "symbol": tk, "openQuantity": q, "tradeQuantity": q,
             "marketPrice": px, "costPrice": px, "status": "OPEN"} for tk, (q, px) in PARK.items()]
    if lag_open:
        rows.append({"accountNo": ACCOUNT_NO, "symbol": LAG_TK, "openQuantity": lag_open,
                     "tradeQuantity": lag_trade, "marketPrice": lag_mp, "costPrice": lag_cost,
                     "status": "OPEN"})
    rows += list(extra_rows)
    recs = [
        {"ts": f"{date}T20:30:00", "kind": "positions", "account_no": OTHER_NO,
         "payload": {"positions": [{"accountNo": OTHER_NO, "symbol": LAG_TK, "openQuantity": 999,
                                    "tradeQuantity": 999, "marketPrice": 1, "costPrice": 1}]}},
        {"ts": f"{date}T20:30:01", "kind": "positions", "account_no": ACCOUNT_NO,
         "payload": {"positions": rows}},
        {"ts": f"{date}T20:30:02", "kind": "balances", "account_no": ACCOUNT_NO,
         "payload": {"stock": {"availableCash": cash_avail, "totalCash": cash_total,
                               "totalDebt": debt, "cashDividendReceiving": 0.0,
                               "depositInterest": 1.0},
                     "egg": {"totalValue": egg}}},
    ]
    with open(os.path.join(exec_dir, f"dnse_raw_{date}.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")


def price_fn_for(lag_px):
    def _f(tks, _d):
        px = {tk: float(p) for tk, (_q, p) in PARK.items()}
        px[LAG_TK] = float(lag_px)
        return {t: px[t] for t in tks if t in px}
    return _f


def holdings(asof, plan_dir, exec_dir, lag_px, corp_actions=()):
    ph.account_profile = lambda label: {"account_id": ACCOUNT_NO, "excluded_tickers": []}
    return ph.park_holdings(ACCOUNT, asof=asof, plan_dir=plan_dir, exec_dir=exec_dir,
                            corp_actions=list(corp_actions), price_fn=price_fn_for(lag_px))
