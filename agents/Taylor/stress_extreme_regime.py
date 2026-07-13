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

# Stale-fixture cleanup (kb/coding_guidelines.md §7): Executor.__init__ eagerly resumes
# from the default state path — a state file left by a PREVIOUS run of this suite would
# silently corrupt this run's starting parents (KeyError on new order ids). Remove ours.
import glob
for _f in glob.glob("/home/trido/thanhdt/WorkingClaude/data/execution_logs/"
                    "exec_STRESSTEST*_2026-07-01_state.json"):
    os.remove(_f)


N_CHECKS = 0


def check(name, cond):
    global N_CHECKS
    N_CHECKS += 1
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

# ---- 6. POLL-1 LOOPHOLE — PNJ 2026-07-03 replay (job Taylor_20260713_075836) -
print("\n== 6. POLL-1 LOOPHOLE (PNJ replay): first BUY slice at locked floor ==")
# PNJ 2026-07-03: ref 63100, floor 58700 (-6.97%), khoá sàn từ ATO → quote đầu
# tiên của MORNING đã last==floor. NAV ~1B → lệnh mua điển hình 800cp × 58700 =
# 46.96M << max_child_value 200M → TOÀN BỘ lệnh gói trong 1 slice. Trước fix:
# poll-1 của _extreme_regime trả False (n=1, 2-poll debounce) và slice đầu VẪN
# được đặt → khớp hết tại sàn trước khi gate kịp arm. Fix = _floor_guard_buy
# (stateless, quote-only): chặn slice MUA ngay poll-1 khi last cận sàn.
buy_pnj = PlannedOrder(id="BUY-PNJ-01", ticker="PNJ", side="buy", qty=800,
                       ref_price=63100, priority=1)
qmap6 = {"PNJ": raw_quote("PNJ", last=58700, ref=63100, floor=58700, ceil=67500,
                          bid=58700, ask=58700, vol=25_600_000)}
brk6 = FakeBroker(qmap6)
ex6 = Executor(make_plan([buy_pnj], account="STRESSTEST_P1PNJ"), brk6, dict(paper_cfg))
jrows6 = []
_orig_j6 = ex6._journal
def _cap_j6(event, o=None, child_oid="", qty="", price="", note=""):
    jrows6.append((event, getattr(o, "ticker", None)))
    return _orig_j6(event, o, child_oid, qty, price, note)
ex6._journal = _cap_j6
ex6._place_slices(NOW, "CONT")                       # poll-1: lần đánh giá ĐẦU của session
pnj_buys = [p for p in brk6.placed if p[0] == "PNJ" and p[2] == "buy"]
check("PNJ poll-1: NO buy slice placed at locked floor", len(pnj_buys) == 0)
check("PNJ poll-1: EXTREME_FLOOR_GUARD journaled",
      any(r[0] == "EXTREME_FLOOR_GUARD" and r[1] == "PNJ" for r in jrows6))
# poll-2 (+20s): state machine arms như thiết kế → EXTREME_PAUSE tiếp quản
ex6._place_slices(NOW + dt.timedelta(seconds=20), "CONT")
pnj_buys2 = [p for p in brk6.placed if p[0] == "PNJ" and p[2] == "buy"]
check("PNJ poll-2: still no buy (gate armed → EXTREME_PAUSE)", len(pnj_buys2) == 0)
check("PNJ poll-2: 2-poll machine armed normally (cooldown set)",
      (ex6._extreme_state.get("PNJ") or {}).get("until") is not None)

# 6b. Normal-path control: quote KHÔNG cận sàn → slice đầu đặt ngay (0 latency mới)
print("\n== 6b. CONTROL: normal quote — first slice places immediately ==")
buy_nrm = PlannedOrder(id="BUY-NRM2-01", ticker="NR2", side="buy", qty=800,
                       ref_price=20000, priority=1)
qn2 = {"NR2": raw_quote("NR2", last=20000, ref=20000, floor=18600, ceil=21400,
                        bid=19950, ask=20000)}
brk6b = FakeBroker(qn2)
ex6b = Executor(make_plan([buy_nrm], account="STRESSTEST_P1NRM"), brk6b, dict(paper_cfg))
ex6b._place_slices(NOW, "CONT")
check("normal quote: first BUY slice placed on poll-1",
      len([p for p in brk6b.placed if p[0] == "NR2"]) == 1)

# 6c. LIVE control: cùng quote PNJ khoá sàn, cfg SpaceX (gate OFF) → hành vi live
#     byte-identical (slice VẪN đặt — guard không được phép chạm live path)
print("\n== 6c. CONTROL: LIVE cfg (gate OFF) — PNJ quote, slice still places ==")
brk6c = FakeBroker(qmap6)
ex6c = Executor(make_plan([buy_pnj], account="STRESSTEST_P1LIVE"), brk6c, dict(live_cfg))
ex6c._place_slices(NOW, "CONT")
check("LIVE cfg: buy slice at floor STILL places (no live behaviour change)",
      len([p for p in brk6c.placed if p[0] == "PNJ"]) == 1)

# 6d. Glitch false-positive cost: 1 quote lỗi cận sàn → chỉ trễ 1 chu kỳ, KHÔNG
#     arm state machine, KHÔNG sell-to-floor; quote sau bình thường → đặt lại ngay
print("\n== 6d. GLITCH: one bad near-floor quote costs exactly one cycle ==")
buy_gl = PlannedOrder(id="BUY-GLT-01", ticker="GLT", side="buy", qty=800,
                      ref_price=20000, priority=1)
qmap6d = {"GLT": raw_quote("GLT", last=18700, ref=20000, floor=18600, ceil=21400,
                           bid=18600, ask=18700)}
brk6d = FakeBroker(qmap6d)
ex6d = Executor(make_plan([buy_gl], account="STRESSTEST_P1GLT"), brk6d, dict(paper_cfg))
ex6d._place_slices(NOW, "CONT")                      # glitch: guard chặn
check("glitch poll-1: buy blocked", len(brk6d.placed) == 0)
qmap6d["GLT"] = raw_quote("GLT", last=20000, ref=20000, floor=18600, ceil=21400,
                          bid=19950, ask=20000)      # quote hồi bình thường
ex6d._place_slices(NOW + dt.timedelta(seconds=20), "CONT")
check("glitch recovered: buy places next cycle (cost = 1 cycle delay)",
      len(brk6d.placed) == 1)
check("glitch never armed the state machine",
      (ex6d._extreme_state.get("GLT") or {}).get("until") is None)

# 6e. Fail-safe: quote thiếu floor → guard không chặn (giống trigger (i) hiện có)
print("\n== 6e. FAIL-SAFE: missing floor — guard inert, slice places ==")
buy_nf = PlannedOrder(id="BUY-NFL-01", ticker="NFL", side="buy", qty=800,
                      ref_price=20000, priority=1)
qnf = {"NFL": raw_quote("NFL", last=19000, ref=20000, floor=0, ceil=21400,
                        bid=18900, ask=19000)}
brk6e = FakeBroker(qnf)
ex6e = Executor(make_plan([buy_nf], account="STRESSTEST_P1NFL"), brk6e, dict(paper_cfg))
ex6e._place_slices(NOW, "CONT")
check("missing floor: buy slice places (fail-safe = old behaviour)",
      len([p for p in brk6e.placed if p[0] == "NFL"]) == 1)

# 6f. SELL poll-1 cận sàn: KHÔNG đổi hành vi (guard buy-only) — sell đặt bình
#     thường tại chase-cap −3% (chưa sell-to-floor vì chưa arm)
print("\n== 6f. SELL at near-floor poll-1: unchanged (guard is buy-only) ==")
sell_pf = PlannedOrder(id="SELL-PF-01", ticker="SPF", side="sell", qty=800,
                       ref_price=20000, priority=1)
qspf = {"SPF": raw_quote("SPF", last=18700, ref=20000, floor=18600, ceil=21400,
                         bid=18600, ask=18700)}
brk6f = FakeBroker(qspf)
ex6f = Executor(make_plan([sell_pf], account="STRESSTEST_P1SPF"), brk6f, dict(paper_cfg))
ex6f._place_slices(NOW, "CONT")
spf = [p for p in brk6f.placed if p[0] == "SPF"]
check("sell poll-1: slice placed (not blocked)", len(spf) == 1)
check("sell poll-1: price at -3% chase cap 19400 (not floor — not armed yet)",
      bool(spf) and spf[0][3] == 19400)

# 6g. Per-account LIVE controls (đính chính họp team 07-13): 6c dùng live_cfg
#     chụp sẵn ở section 0 — đây là bằng chứng TRỰC TIẾP per-account: resolve
#     cfg hiệu dụng TƯƠI từ secrets thật cho TỪNG account live (SpaceX, ZaloPay),
#     chạy đúng code path _place_slices với quote PNJ khoá sàn → khẳng định
#     trong CÙNG một check: flag OFF ∧ slice mua VẪN đặt (guard không kích).
print("\n== 6g. PER-ACCOUNT LIVE CONTROLS: SpaceX & ZaloPay untouched by guard ==")
for _acct in ("SpaceX", "ZaloPay"):
    _cfg = eff_cfg(_acct)                              # resolve tươi, không dùng bản chụp
    _brk = FakeBroker(qmap6)
    _ex = Executor(make_plan([buy_pnj], account=f"STRESSTEST_P1{_acct.upper()}"),
                   _brk, dict(_cfg))
    _ex._place_slices(NOW, "CONT")
    check(f"{_acct}: extreme_regime_enabled False AND PNJ buy slice at floor still places",
          _cfg["extreme_regime_enabled"] is False
          and len([p for p in _brk.placed if p[0] == "PNJ" and p[2] == "buy"]) == 1)

print("\n" + "=" * 60)
if FAILS:
    print(f"RESULT: {len(FAILS)}/{N_CHECKS} FAILED -> {FAILS}")
    sys.exit(1)
print(f"RESULT: ALL {N_CHECKS}/{N_CHECKS} PASS — extreme-regime gate fires on stress, silent when NORMAL,")
print("        and the LIVE account gate stays OFF.")
