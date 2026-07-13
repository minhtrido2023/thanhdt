# -*- coding: utf-8 -*-
"""Regression self-check for the plan approval code-gate (approval_block_reason).

Incident 2026-07-13 (kb/INCIDENTS.md "Unapproved ZaloPay plan"): plan_ZaloPay_2026-07-13
had requires_user_approval=true + approved_by=null with 2 live orders, and bot_execute.py
would have executed it at 09:05 because NOTHING in the execution path read those fields —
load_plan() even silently dropped them (dataclass field filter). The only defenses were
send_plan_report.sh (notification, can be missed — it was) and preflight_check.sh (display
only, RED does not stop the 09:05 cron).

Fix (trading_bot/plan.py approval_block_reason + bot_execute.py wiring, 2026-07-13):
second, independent, code-enforced layer — if a plan declares requires_user_approval=true
and approved_by is missing/empty while it has >0 executable orders, bot_execute REFUSES
that account (no orders placed, alert Discord+Telegram+bus, exit code 2), same fail-safe-
pause principle as Executor._ghost_tickers (coding_guidelines.md §5).

Backward-compat decision (surveyed all plan_*.json 2026-06-30→07-13 before writing code):
- routine SpaceX dailies: requires_user_approval=false + approved_by="auto"  → never gated
- paper account `main` dailies: NO approval fields at all (12 orders/day)     → must run
- ZaloPay transition: requires_user_approval=true + approved_by set by Mike   → runs
so a MISSING requires_user_approval field defaults to False (gate silent) — treating
absence as "needs approval" would have blocked the live paper trials the next morning.

Run: python3 approval_gate_selfcheck.py   (exit 0 = all pass)
"""
import glob
import inspect
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.plan import load_plan, approval_block_reason, TradePlan, PlannedOrder  # noqa: E402
from trading_bot.config import PLAN_DIR  # noqa: E402

# Unique per-file account tag + wipe leftover fixtures BEFORE the run (same pattern as
# ghost_order_selfcheck.py's TAG cleanup — a stale fixture from an earlier run must not
# leak into this one, and this tag must not be shared with any other selfcheck file).
TAG = "selfcheck-apprgate"
_PLAN_DATE = "2020-01-02"  # far past — can never collide with a real trading day's plan


def _wipe():
    for f in glob.glob(os.path.join(PLAN_DIR, f"plan_{TAG}_*.json")):
        os.remove(f)


_wipe()

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


_ORDER = {"id": "SELL-VIB-01", "ticker": "VIB", "side": "sell", "qty": 100,
          "ref_price": 16000, "book": "BAL", "priority": 1}
_BASE = {"plan_date": _PLAN_DATE, "signal_date": "2020-01-01", "strategy": "selfcheck",
         "strategy_version": "0", "state": 3, "state_name": "NEUTRAL",
         "nav_basis": {"account_nav": 0, "paper_nav": 0, "scale": 0},
         "account": TAG}


def write_and_load(extra, orders=1):
    """Write a plan JSON exactly as a generator would, then load through the REAL
    load_plan() — the gate must be tested on what survives deserialization, not on a
    hand-built TradePlan (load_plan's field filter was part of the original bug)."""
    d = dict(_BASE)
    d["orders"] = [dict(_ORDER) for _ in range(orders)]
    d.update(extra)
    with open(os.path.join(PLAN_DIR, f"plan_{TAG}_{_PLAN_DATE}.json"), "w",
              encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    return load_plan(_PLAN_DATE, account=TAG)


try:
    print("A. requires_user_approval=true + approved_by=null + orders>0 → BLOCK")
    p = write_and_load({"requires_user_approval": True, "approved_by": None})
    r = approval_block_reason(p)
    check("A1 blocked", r is not None, repr(r))
    check("A2 reason names the account", r is not None and TAG in r)

    print("B. approved (approved_by='user') + orders>0 → RUN")
    p = write_and_load({"requires_user_approval": True, "approved_by": "user",
                        "mafee_authorized": True})
    check("B1 not blocked", approval_block_reason(p) is None)
    long_delegation = ("user (ủy quyền duyệt-gộp ngày 2-5 chốt 2026-07-06; áp dụng "
                       "day 3/5 — day 2 sạch)")  # real ZaloPay-transition shape
    p = write_and_load({"requires_user_approval": True, "approved_by": long_delegation})
    check("B2 delegation-string approval not blocked", approval_block_reason(p) is None)

    print("C. requires_user_approval=false / field MISSING + orders>0 → RUN (no regression)")
    p = write_and_load({"requires_user_approval": False})
    check("C1 explicit false not blocked", approval_block_reason(p) is None)
    p = write_and_load({})  # both fields absent — legacy + paper `main` plan shape
    check("C2 fields missing entirely not blocked", approval_block_reason(p) is None)
    check("C3 missing field loads as default False", p.requires_user_approval is False)

    print("D. orders=0 (HOLD) + unapproved → RUN (nothing to execute, no risk)")
    p = write_and_load({"requires_user_approval": True, "approved_by": None}, orders=0)
    check("D1 HOLD not blocked", approval_block_reason(p) is None)

    print("E. empty/whitespace approved_by counts as UNAPPROVED")
    p = write_and_load({"requires_user_approval": True, "approved_by": ""})
    check("E1 empty string blocked", approval_block_reason(p) is not None)
    p = write_and_load({"requires_user_approval": True, "approved_by": "   "})
    check("E2 whitespace-only blocked", approval_block_reason(p) is not None)
    p = write_and_load({"requires_user_approval": True, "approved_by": "None"})
    check("E3 literal 'None' string blocked", approval_block_reason(p) is not None)
    p = write_and_load({"requires_user_approval": True, "approved_by": "null"})
    check("E4 literal 'null' string blocked", approval_block_reason(p) is not None)

    print("F. approved_by_user alternate field name (preflight_check.sh accepts it)")
    p = write_and_load({"requires_user_approval": True, "approved_by_user": "user"})
    check("F1 approved_by_user honoured", approval_block_reason(p) is None)

    print("G. LLM-authored string booleans normalized")
    p = write_and_load({"requires_user_approval": "true", "approved_by": None})
    check("G1 'true' string blocked", approval_block_reason(p) is not None)
    p = write_and_load({"requires_user_approval": "false", "approved_by": None})
    check("G2 'false' string not blocked", approval_block_reason(p) is None)

    print("H. wiring — bot_execute.main actually calls the gate (accidental-removal guard)")
    import bot_execute  # noqa: E402
    src = inspect.getsource(bot_execute.main)
    check("H1 gate called in main()", "approval_block_reason(plan)" in src)
    check("H2 blocked account skipped, not executed",
          "approval_blocked.append" in src and "_alert_approval_block" in src)
    check("H3 non-zero exit on block", "return 2" in src)
    gate_at = src.index("approval_block_reason(plan)")
    check("H4 gate AFTER excluded filter, BEFORE lock/broker",
          src.index("filter_excluded_tickers") < gate_at < src.index("_acquire_account_lock"))
finally:
    _wipe()

print()
if fails:
    print(f"❌ {len(fails)} FAILED: {fails}")
    sys.exit(1)
print("✅ approval_gate_selfcheck: ALL PASS")
sys.exit(0)
