# -*- coding: utf-8 -*-
"""EXTREME-regime gate — week-1 stress-injection harness (Taylor, 2026-07-01).

Drives the REAL executor path (trading_bot.executor.Executor + real Quote objects
via a recording FakeBroker) with crafted limit-down / 3-sigma-down quotes, and
asserts the four mechanics fire through the genuine paper wiring:
  1. ARM        — 2-poll confirm on (i) near-floor and (ii) r15 < -zσ, sets cooldown.
  2. BUY-PAUSE  — armed BUY → EXTREME_PAUSE, no place_order.
  3. SELL-TO-FLOOR — armed SELL prices at the daily floor (bypasses the -3% chase cap).
  4. CADENCE x0.25 — armed → _extreme_slice_mult=0.25 → _cancel_stale cancels at 2min.
Plus negative controls: NORMAL quote never arms, and the LIVE (SpaceX) effective
config (extreme_regime_enabled=False) never arms on the SAME stress quote.

The config is read through the REAL load_config()/load_accounts() resolution so the
test proves the paper-only override actually took effect. No secrets are printed.
"""
import datetime as dt
import os
import sys

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")

from trading_bot.config import load_config, load_accounts
from trading_bot.brokers import Quote
from trading_bot.plan import PlannedOrder, TradePlan
from trading_bot.executor import Executor

NOW = dt.datetime(2026, 7, 1, 10, 0, 0)          # mid-session ICT
PLAN_DATE = "2026-07-01"
FAILS = []


def check(name, cond):
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {name}")
    if not cond:
        FAILS.append(name)


class FakeBroker:
    """Records place/cancel; serves crafted Quotes. Genuine Quote objects, real
    normalization path. quote_map: ticker -> raw dict."""
    name = "fake"

    def __init__(self, quote_map):
        self.quote_map = quote_map
        self.placed = []      # (ticker, qty, side, price)
        self.cancelled = []   # oid
        self._oid = 0

    def get_quote(self, symbol):
        raw = self.quote_map.get(symbol)
        return Quote(raw) if raw else None

    def get_cash(self):
        return 10_000_000_000

    def place_order(self, symbol, qty, side, price=None, order_type="LO"):
        self._oid += 1
        self.placed.append((symbol, qty, side, price))
        return f"OID{self._oid}"

    def cancel_order(self, order_id):
        self.cancelled.append(order_id)


def raw_quote(sym, last, ref, floor, ceil, bid, ask, vol=5_000_000):
    return {"symbol": sym, "exchange": "HOSE", "lastprice": last, "refprice": ref,
            "floor": floor, "ceiling": ceil, "bidprice1": bid, "askprice1": ask,
            "totalvolume": vol}


def make_plan(orders, account="STRESSTEST"):   # throwaway label — never touches real main/SpaceX exec logs
    return TradePlan(plan_date=PLAN_DATE, signal_date="2026-06-30", strategy="v23",
                     strategy_version="2.4", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "paper_nav": 1e9, "scale": 1.0},
                     orders=orders, account=account,
                     created_at="2026-07-01T09:00:00")


def eff_cfg(label):
    cfg = load_config()
    for p in load_accounts(cfg):
        if p["label"] == label:
            return p["cfg"]
    raise KeyError(label)


# ---- config wiring proof -----------------------------------------------------
print("== 0. CONFIG WIRING (real load_config/load_accounts) ==")
paper_cfg = eff_cfg("main")
live_cfg = eff_cfg("SpaceX")
check("paper(main) extreme_regime_enabled == True", paper_cfg["extreme_regime_enabled"] is True)
check("live(SpaceX) extreme_regime_enabled == False", live_cfg["extreme_regime_enabled"] is False)
check("global DEFAULT stays False", load_config()["extreme_regime_enabled"] is False)
check("paper params match approved (band .03/z 3.0/mult .25/cd 15)",
      paper_cfg["extreme_band"] == 0.03 and paper_cfg["extreme_move_z"] == 3.0
      and paper_cfg["extreme_slice_mult"] == 0.25 and paper_cfg["extreme_cooldown_min"] == 15)

# ---- 1. ARM via near-floor (trigger i) --------------------------------------
print("\n== 1. ARM via near-floor limit-down (trigger i, 2-poll confirm) ==")
# ref 20000, floor 18600 (-7%). last 18700 <= floor*1.03=19158 -> trip.
sell = PlannedOrder(id="SELL-STR-01", ticker="STR", side="sell", qty=10000,
                    ref_price=20000, priority=1)
qmap = {"STR": raw_quote("STR", last=18700, ref=20000, floor=18600, ceil=21400,
                         bid=18600, ask=18700)}
brk = FakeBroker(qmap)
ex = Executor(make_plan([sell]), brk, dict(paper_cfg))
q = brk.get_quote("STR")
p1 = ex._extreme_regime(sell, q, NOW)
p2 = ex._extreme_regime(sell, q, NOW + dt.timedelta(seconds=20))
check("poll-1 not armed (2-poll debounce)", p1 is False)
check("poll-2 armed", p2 is True)
st = ex._extreme_state["STR"]
check("cooldown 'until' set ~15min", st["until"] is not None)
armed_until = dt.datetime.fromisoformat(st["until"])
check("cooldown ≈15min from poll-2", abs((armed_until - (NOW + dt.timedelta(seconds=20))
                                          ).total_seconds() - 15 * 60) < 2)
check("stays armed inside cooldown (single poll)",
      ex._extreme_regime(sell, q, NOW + dt.timedelta(minutes=5)) is True)

# ---- 2. ARM via 3-sigma intraday drop (trigger ii) --------------------------
print("\n== 2. ARM via r15 < -3σ intraday (trigger ii, floor far away) ==")
sell2 = PlannedOrder(id="SELL-SIG-01", ticker="SIG", side="sell", qty=10000,
                     ref_price=20000, priority=1)
# last 19000, floor 15000 -> near-floor NOT tripped (15000*1.03=15450 < 19000).
qmap2 = {"SIG": raw_quote("SIG", last=19000, ref=20000, floor=15000, ceil=25000,
                          bid=18900, ask=19000)}
brk2 = FakeBroker(qmap2)
ex2 = Executor(make_plan([sell2]), brk2, dict(paper_cfg))
ex2._gap_ref["SIG"] = {"prior_close": 20000, "rvol_20d": 0.01}   # 1% daily vol
# px_hist: ~15min ago 20000, now 19000 -> r15 = -5% < -3*0.01 = -3%
ex2.state["px_hist"]["SIG"] = [
    [(NOW - dt.timedelta(minutes=15)).isoformat(timespec="seconds"), 20000.0],
    [NOW.isoformat(timespec="seconds"), 19000.0],
]
check("r15 computed ≈ -5%", abs(ex2._r15("SIG", NOW) + 0.05) < 1e-6)
s1 = ex2._extreme_regime(sell2, brk2.get_quote("SIG"), NOW)
# refresh last sample so r15 stays fresh for poll-2
ex2.state["px_hist"]["SIG"].append(
    [(NOW + dt.timedelta(seconds=20)).isoformat(timespec="seconds"), 19000.0])
s2 = ex2._extreme_regime(sell2, brk2.get_quote("SIG"), NOW + dt.timedelta(seconds=20))
check("3σ trigger: poll-1 not armed", s1 is False)
check("3σ trigger: poll-2 armed", s2 is True)

# ---- 3. SELL-TO-FLOOR + 4. BUY-PAUSE via real _place_slices -----------------
print("\n== 3+4. _place_slices: armed SELL→floor, armed BUY→pause ==")
sell3 = PlannedOrder(id="SELL-PS-01", ticker="PSS", side="sell", qty=10000,
                     ref_price=20000, priority=1)
buy3 = PlannedOrder(id="BUY-PS-01", ticker="PSB", side="buy", qty=10000,
                    ref_price=20000, priority=2)
qmap3 = {"PSS": raw_quote("PSS", last=18700, ref=20000, floor=18600, ceil=21400,
                          bid=18600, ask=18700),
         "PSB": raw_quote("PSB", last=18700, ref=20000, floor=18600, ceil=21400,
                          bid=18600, ask=18700)}
brk3 = FakeBroker(qmap3)
ex3 = Executor(make_plan([sell3, buy3]), brk3, dict(paper_cfg))
# pre-arm both via 2 polls (real arming method)
for o, t in ((sell3, "PSS"), (buy3, "PSB")):
    qq = brk3.get_quote(t)
    ex3._extreme_regime(o, qq, NOW)
    ex3._extreme_regime(o, qq, NOW + dt.timedelta(seconds=20))
check("PSS armed", ex3._extreme_state["PSS"]["until"] is not None)
check("PSB armed", ex3._extreme_state["PSB"]["until"] is not None)
# capture journal events in-memory (still writes file for fidelity)
jrows = []
_orig_j = ex3._journal
def _cap_j(event, o=None, child_oid="", qty="", price="", note=""):
    jrows.append((event, getattr(o, "ticker", None)))
    return _orig_j(event, o, child_oid, qty, price, note)
ex3._journal = _cap_j
ex3._place_slices(NOW + dt.timedelta(seconds=40), "CONT")
placed_sells = [p for p in brk3.placed if p[0] == "PSS"]
placed_buys = [p for p in brk3.placed if p[0] == "PSB"]
check("armed SELL placed (sell-to-floor)", len(placed_sells) == 1)
check("armed SELL price == daily floor 18600",
      bool(placed_sells) and placed_sells[0][3] == 18600)
check("armed BUY paused (no order placed)", len(placed_buys) == 0)
check("EXTREME_PAUSE journaled for BUY",
      any(r[0] == "EXTREME_PAUSE" and r[1] == "PSB" for r in jrows))
# contrast: normal (non-extreme) sell would strand ABOVE floor at ref*(1-3%)
normal_px = ex3._limit_price(sell3, brk3.get_quote("PSS"), cross=True, extreme=False)
extreme_px = ex3._limit_price(sell3, brk3.get_quote("PSS"), cross=True, extreme=True)
check("normal sell stranded above floor (=19400)", normal_px == 19400)
check("extreme sell reaches floor (=18600)", extreme_px == 18600)

# ---- cadence x0.25 ----------------------------------------------------------
print("\n== 4b. CADENCE x0.25: _extreme_slice_mult + _cancel_stale ==")
check("armed slice_mult == 0.25", ex3._extreme_slice_mult(sell3, NOW + dt.timedelta(seconds=40)) == 0.25)
# child aged 3min: armed(2min thresh)->cancel; OFF(8min thresh)->keep
child_ts = (NOW).isoformat(timespec="seconds")
ps = ex3.state["parents"]["SELL-PS-01"]
ps["children"] = [{"oid": "C1", "qty": 5000, "price": 18600, "filled": 0,
                   "status": "open", "ts": child_ts}]
ex3._cancel_stale(NOW + dt.timedelta(minutes=3))
check("armed: 3min-old child CANCELLED (2min thresh)", "C1" in brk3.cancelled)
# OFF control: fresh executor, same 3min child, default mult 1.0 -> keep
ex_off = Executor(make_plan([sell3]), FakeBroker(qmap3), dict(paper_cfg))
ex_off.cfg = dict(paper_cfg); ex_off.cfg["extreme_regime_enabled"] = False
ex_off.state["parents"]["SELL-PS-01"]["children"] = [
    {"oid": "C2", "qty": 5000, "price": 18600, "filled": 0, "status": "open", "ts": child_ts}]
ex_off._cancel_stale(NOW + dt.timedelta(minutes=3))
check("OFF: 3min-old child KEPT (8min thresh)", "C2" not in ex_off.broker.cancelled)

# ---- negative controls ------------------------------------------------------
print("\n== 5. NEGATIVE CONTROLS (no false trigger) ==")
# 5a NORMAL quote never arms across many polls
nsell = PlannedOrder(id="SELL-NRM-01", ticker="NRM", side="sell", qty=10000,
                     ref_price=20000, priority=1)
qn = {"NRM": raw_quote("NRM", last=20000, ref=20000, floor=18600, ceil=21400,
                       bid=19950, ask=20000)}
exn = Executor(make_plan([nsell]), FakeBroker(qn), dict(paper_cfg))
qq = exn.broker.get_quote("NRM")
armed_any = any(exn._extreme_regime(nsell, qq, NOW + dt.timedelta(seconds=20 * i))
                for i in range(10))
check("NORMAL quote: never arms over 10 polls", armed_any is False)

# 5b LIVE (SpaceX) config gate off — same limit-down stress, never arms
lsell = PlannedOrder(id="SELL-LIV-01", ticker="STR", side="sell", qty=10000,
                     ref_price=20000, priority=1)
# label is throwaway; the LIVE-gate behaviour comes from live_cfg (SpaceX effective cfg), passed explicitly
exl = Executor(make_plan([lsell], account="STRESSTEST_LIVEOFF"), FakeBroker(qmap), dict(live_cfg))
ql = exl.broker.get_quote("STR")
live_armed = any(exl._extreme_regime(lsell, ql, NOW + dt.timedelta(seconds=20 * i))
                 for i in range(5))
check("LIVE cfg (gate OFF): limit-down never arms", live_armed is False)
check("LIVE cfg: slice_mult stays 1.0", exl._extreme_slice_mult(lsell, NOW) == 1.0)

print("\n" + "=" * 60)
if FAILS:
    print(f"RESULT: {len(FAILS)} FAILED -> {FAILS}")
    sys.exit(1)
print("RESULT: ALL PASS — extreme-regime gate fires on stress, silent when NORMAL,")
print("        and the LIVE account gate stays OFF.")
