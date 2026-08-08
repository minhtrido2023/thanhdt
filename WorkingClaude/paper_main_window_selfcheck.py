# -*- coding: utf-8 -*-
"""Self-check for the paper-main morning-window evidence chain (job Taylor_20260709_104834).

Two root causes made the paper 'main' fill-timing harness produce ZERO morning evidence
on 2026-07-08/09 (journals show only GHOST_ORDER at 02:10 UTC, run logs 0 bytes):

1. TZ: the paper-main cron lines invoked python3 directly (unlike live accounts, which go
   through mike/bin/run_bot.sh sourcing TZ=Asia/Ho_Chi_Minh). System tz is Etc/UTC, so
   datetime.now() returned UTC and session_phase() saw 02:10 → CLOSED all session.
   Fix: TZ=Asia/Ho_Chi_Minh added to the paper-main crontab lines.

2. PaperBroker.poll_orders() returned EVERY order ever stored in bot_paper_account.json
   (persists across sessions), while the real DNSEBroker returns TODAY's order book only.
   Yesterday's FILLED orders are unknown to today's fresh executor state → the ghost
   guard (Executor._ghost_tickers) flagged them and paused every probe ticker.
   Fix: poll_orders() now day-scopes both the fill loop and the returned updates.

Checks here:
  A. day-scope: yesterday's filled order is not returned and no longer ghosts today's run
  B. same-day ghost rehearsal is preserved (the guard itself must keep working on paper)
  C. sim 10:46 MORNING step: BUY orders PLACE with ft:in-window (10:45-11:15 evidence)
  D. sim 09:16 MORNING step: SELL orders PLACE with ft:in-window (09:15-09:45), BUY ft:out
  E. TZ mechanism: TZ=Asia/Ho_Chi_Minh makes datetime.now() run at UTC+7

Run: python3 paper_main_window_selfcheck.py   (exit 0 = all pass)
"""
import datetime as dt
import glob
import os
import subprocess
import sys
import tempfile

# Test-mode: KHÔNG cho Executor._publish_bot_event ghi event GIẢ vào bus production
# (retro-2026-08-07 Pattern 1 — 4 lần tái diễn 08-03/04/05/07). Xem coding_guidelines §5.
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot.brokers import PaperBroker, OrderUpdate  # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan  # noqa: E402
from trading_bot.executor import Executor  # noqa: E402
from trading_bot.config import load_config, EXEC_DIR  # noqa: E402

# Unique tag + stale-fixture cleanup — see ghost_order_selfcheck.py TAG comment.
TAG = "selfcheck-ftwin"
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(f)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


REFS = {"FPT": 72100, "MBB": 26000}
TODAY = dt.date.today().isoformat()
YESTERDAY = (dt.date.today() - dt.timedelta(days=1)).isoformat()


def make_env(tmp, sub):
    broker = PaperBroker(label=TAG)
    broker.state_file = os.path.join(tmp, f"paper_{sub}.json")
    broker.connect()
    broker.set_fallback_refs(REFS)
    broker.state["positions"]["FPT"] = 400        # sellable position for the SELL leg
    orders = [
        PlannedOrder(id="SELL-FPT-00", ticker="FPT", side="sell", qty=400,
                     ref_price=REFS["FPT"], priority=1),
        PlannedOrder(id="BUY-MBB-01", ticker="MBB", side="buy", qty=1000,
                     ref_price=REFS["MBB"], priority=5),
    ]
    plan = TradePlan(plan_date=TODAY, signal_date=TODAY, strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=orders,
                     account=TAG, created_at=f"{TODAY}T00:00:00")
    cfg = load_config()
    cfg["mode"] = "paper"
    ex = Executor(plan, broker, cfg, shared={})
    ex.state_file = os.path.join(tmp, f"state_{sub}.json")
    ex.journal_file = os.path.join(tmp, f"journal_{sub}.csv")
    return broker, ex


def journal_places(path):
    import csv
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["event"] == "PLACE":
                rows.append(r)
    return rows


with tempfile.TemporaryDirectory() as tmp:
    # ---- A. day-scope: yesterday's filled order must not ghost today's run ----
    broker, ex = make_env(tmp, "a")
    broker.state["open_orders"]["P000001"] = {
        "symbol": "FPT", "qty": 400, "side": "buy", "price": 72000, "type": "LO",
        "filled": 400, "status": "filled", "avg_price": 72000,
        "ts": f"{YESTERDAY}T14:19:38"}
    updates = broker.poll_orders()
    check("A1 yesterday's order absent from poll_orders()", "P000001" not in updates,
          detail=f"returned={list(updates)}")
    check("A2 no ghost pause from yesterday's order",
          ex._ghost_tickers(updates) == set(), detail=str(ex._ghost_tickers(updates)))
    # Negative control — the exact 2026-07-08/09 incident signature (pre-fix behavior):
    stale = {"P000001": OrderUpdate("P000001", "filled", 400, 72000, raw={"symbol": "FPT"})}
    check("A3 negative control: same update WOULD ghost if still returned",
          ex._ghost_tickers(stale) == {"FPT"})

    # ---- B. same-day ghost rehearsal preserved ----
    broker.state["open_orders"]["P000002"] = {
        "symbol": "FPT", "qty": 100, "side": "buy", "price": 72100, "type": "LO",
        "filled": 100, "status": "filled", "avg_price": 72100,
        "ts": f"{TODAY}T09:20:00"}
    updates = broker.poll_orders()
    check("B1 today's unknown filled order still returned and ghosts",
          "P000002" in updates and ex._ghost_tickers(updates) == {"FPT"},
          detail=str(ex._ghost_tickers(updates)))

    # ---- C. sim: run starting in the BUY window (Tue/Thu 10:46 cron) ----
    broker, ex = make_env(tmp, "c")
    now = dt.datetime.combine(dt.date.today(), dt.time(10, 46, 30))
    ex.step(now, "MORNING", True)
    places = journal_places(ex.journal_file)
    buys = [r for r in places if r["side"] == "buy"]
    sells = [r for r in places if r["side"] == "sell"]
    check("C1 BUY placed in a 10:46 step", len(buys) == 1, detail=f"{len(buys)} buy PLACE")
    check("C2 BUY tagged ft:in-window (10:45-11:15)",
          buys and "ft:in-window" in buys[0]["note"], detail=buys[0]["note"] if buys else "")
    check("C3 SELL still places at 10:46, tagged ft:out",
          sells and "ft:out" in sells[0]["note"], detail=sells[0]["note"] if sells else "")

    # ---- D. sim: run starting at open (Mon/Wed/Fri 09:10 cron → first step ~09:16) ----
    broker, ex = make_env(tmp, "d")
    now = dt.datetime.combine(dt.date.today(), dt.time(9, 16, 0))
    ex.step(now, "MORNING", True)
    places = journal_places(ex.journal_file)
    buys = [r for r in places if r["side"] == "buy"]
    sells = [r for r in places if r["side"] == "sell"]
    check("D1 SELL placed at 09:16 tagged ft:in-window (09:15-09:45)",
          sells and "ft:in-window" in sells[0]["note"], detail=sells[0]["note"] if sells else "")
    check("D2 BUY places immediately at 09:16 (first slice ignores window) tagged ft:out",
          buys and "ft:out" in buys[0]["note"], detail=buys[0]["note"] if buys else "")

    # ---- E. TZ mechanism (what the crontab fix relies on) ----
    r = subprocess.run(
        [sys.executable, "-c",
         "import datetime as dt;"
         "print((dt.datetime.now() - dt.datetime.utcnow()).total_seconds())"],
        env={**os.environ, "TZ": "Asia/Ho_Chi_Minh"}, capture_output=True, text=True)
    offset_h = float(r.stdout.strip()) / 3600 if r.returncode == 0 else None
    check("E1 TZ=Asia/Ho_Chi_Minh gives datetime.now() = UTC+7",
          offset_h is not None and abs(offset_h - 7) < 0.02, detail=f"offset={offset_h}h")

for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(f)

print("\n" + ("ALL PASS" if not fails else "FAILED: " + ", ".join(fails)))
sys.exit(1 if fails else 0)
