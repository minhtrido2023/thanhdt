#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B3 — auto_exit_inject.process_account() THẬT (book_lot_snapshot → park_holdings THẬT, không mock)
qua vòng đời quyền mua SCL LAG. Sandbox tạm; mọi đường ghi của aei/ps/ph/capit trỏ vào sandbox;
AUTO_EXIT_TEST_MODE=1 + subprocess recorder ⇒ không bus/Discord. Chạy: $DNA_PYEXE b3_auto_exit.py"""
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b3_common as C  # noqa: E402  (test-mode env đặt trước import trading_bot)
import auto_exit_inject as aei  # noqa: E402
import portfolio_status as ps  # noqa: E402
import capit_episode  # noqa: E402
import park_holdings as ph  # noqa: E402

CALLS = []
aei.subprocess.run = lambda cmd, *a, **k: (CALLS.append(cmd), subprocess.CompletedProcess(cmd, 0))[1]

E = dt.date(2026, 10, 26)
T25 = C.nth_session_after(E, 25)


def scenario(name, signal, raw_days, fills=(), acts=(), lag_cost=C.PX_CUM):
    """raw_days = [(date, open, trade, mp)] — dnse_raw ghi cho từng ngày (cần ngày = signal)."""
    td, EX, PL = C.sandbox()
    C.write_journal(EX, E.isoformat(), [(C.LAG_TK, "buy", C.QTY_OLD, C.PX_CUM, "LAG")])
    for d, tk_side_q_book in fills:
        C.write_journal(EX, d.isoformat(), [tk_side_q_book])
    for d, op, tr, mp in raw_days:
        C.write_raw(EX, d.isoformat(), op, tr, mp, cash_total=100e6, cash_avail=100e6,
                    lag_cost=lag_cost)
    ledger = os.path.join(td, "capit.json")
    json.dump({"episodes": []}, open(ledger, "w"))
    ps.EXEC_DIR, aei.PLAN_DIR, capit_episode.LEDGER_PATH = EX, PL, ledger
    aei.BLOCK_ALERT_STATE_PATH = os.path.join(td, "alert_state.json")
    aei.account_no_for = lambda a: C.ACCOUNT_NO if a == C.ACCOUNT else None
    d0 = list(ph.park_holdings.__defaults__)
    d0[1], d0[2] = PL, EX
    ph.park_holdings.__defaults__ = tuple(d0)
    ph.account_profile = lambda label: {"account_id": C.ACCOUNT_NO, "excluded_tickers": []}
    ph.load_corp_actions = lambda *a, **k: list(acts)
    plan_date = C.next_trading_day(signal).isoformat()
    pp = os.path.join(PL, f"plan_{C.ACCOUNT}_{plan_date}.json")
    json.dump({"plan_date": plan_date, "orders": [], "account": C.ACCOUNT}, open(pp, "w"))
    print(f"\n== {name}  signal={signal} plan_date={plan_date}")
    rc = aei.process_account(C.ACCOUNT, plan_date, signal.isoformat(), dry_run=False)
    plan = json.load(open(pp))
    sells = [(o["ticker"], o["book"], o["qty"], o["note"][-60:]) for o in plan["orders"]]
    notes = plan.get("auto_exit_inject_notes") or []
    print(f"  rc={rc} SELL={sells}")
    for n in notes:
        for k in ("blocked", "capped"):
            if n.get(k):
                print(f"  {k}: {json.dumps(n[k], ensure_ascii=False)[:300]}")
    if not notes:
        print("  auto_exit_inject_notes: (không có — không lệnh, không cờ chặn/cắt)")
    h = ph.park_holdings(C.ACCOUNT, asof=signal.isoformat(), need_price=False)
    lots, ok, _r, blk = ps.book_lot_snapshot(C.ACCOUNT, "LAG", asof=signal.isoformat())
    print(f"  park_holdings: reconcile_ok={h['reconcile']['ok']} mismatches={h['reconcile']['mismatches']}"
          f" | book_lot_snapshot LAG lots={lots} blocked={blk}")
    return rc, plan


print(f"E (mua LAG)={E}  T+25={T25}  T0(GDKHQ)={C.nth_session_after(E, 10)}")
# X1 — CP quyền CHƯA hiện ở broker (dạng B, hoặc dạng A trước ngày credit): bán đúng 14.000?
scenario("X1 trước khi CP mới về (14.000/14.000)", T25, [(T25, 14_000, 14_000, C.PX_EX)])
# X2 — dạng A: CP mới đã vào openQuantity, chưa niêm yết (19.000 open / 14.000 trade)
scenario("X2 dạng A: CP mới về, chưa niêm yết (19.000/14.000)", T25, [(T25, 19_000, 14_000, C.PX_EX)])
# X3 — sau niêm yết 19.000/19.000, sổ chưa sửa
LIST = C.nth_session_after(T25, 40)
scenario("X3 sau niêm yết, sổ chưa sửa (19.000/19.000)", LIST, [(LIST, 19_000, 19_000, C.PX_EX)])
# X4 — 14.000 ĐÃ bán qua plan (FILL SELL LAG) rồi lô 5.000 về/niêm yết: lô mới có mồ côi không?
S = C.nth_session_after(T25, 1)
scenario("X4 đã bán 14.000 lúc T+26, sau niêm yết broker còn 5.000/5.000", LIST,
         [(LIST, 5_000, 5_000, C.PX_EX)], fills=[(S, (C.LAG_TK, "sell", 14_000, C.PX_EX, "LAG"))])
scenario("X4b như X4 nhưng 5.000 chưa niêm yết (5.000/0)", LIST, [(LIST, 5_000, 0, C.PX_EX)],
         fills=[(S, (C.LAG_TK, "sell", 14_000, C.PX_EX, "LAG"))])
# X5 — workaround corp_actions BONUS_ISSUE ×19/14 (ex=T0, credit trước T+25)
T0 = C.nth_session_after(E, 10)
CREDIT = C.nth_session_after(T0, 10)   # credit TRƯỚC T+25 (để workaround kịp áp)
act = {"id": "SCL-RIGHTS-AS-BONUS", "ticker": "SCL", "event_type": "BONUS_ISSUE",
       "qty_multiplier": 19 / 14, "ex_date": T0.isoformat(), "record_date": T0.isoformat(),
       "broker_effective_ts": f"{CREDIT}T19:00:00", "_status": "CONFIRMED test", "evidence": []}
scenario("X5 workaround BONUS_ISSUE ×19/14, 19.000 open / 14.000 trade", T25,
         [(T25, 19_000, 14_000, C.PX_EX)], acts=[act])
CREDIT_LATE = C.nth_session_after(T25, 5)
act_late = dict(act, broker_effective_ts=f"{CREDIT_LATE}T19:00:00")
scenario("X5d workaround nhưng CP về SAU khi đã bán 14.000 (5.000/0)", LIST,
         [(LIST, 5_000, 0, C.PX_EX)], fills=[(S, (C.LAG_TK, "sell", 14_000, C.PX_EX, "LAG"))],
         acts=[act_late])
scenario("X5b workaround, ĐÃ bán 14.000 lúc T+26, 5.000 chưa niêm yết (5.000/0)", LIST,
         [(LIST, 5_000, 0, C.PX_EX)], fills=[(S, (C.LAG_TK, "sell", 14_000, C.PX_EX, "LAG"))],
         acts=[act])
scenario("X5c workaround, sau niêm yết (5.000/5.000)", LIST, [(LIST, 5_000, 5_000, C.PX_EX)],
         fills=[(S, (C.LAG_TK, "sell", 14_000, C.PX_EX, "LAG"))], acts=[act])
# X6 — mốc T+25 rơi TRƯỚC GDKHQ quyền mua: auto_exit có kiểm ex-date không?
EX_LATE = C.nth_session_after(T25, 2)
rc, plan = scenario(f"X6 GDKHQ quyền={EX_LATE} SAU plan_date (bán ở đây = mất quyền)", T25,
                    [(T25, 14_000, 14_000, C.PX_CUM)])
print(f"  plan_date < GDKHQ: {plan['plan_date'] < EX_LATE.isoformat()} — lệnh vẫn chèn: "
      f"{bool(plan['orders'])}")
print(f"\nsubprocess calls (phải rỗng/không có bus thật): {CALLS}")
