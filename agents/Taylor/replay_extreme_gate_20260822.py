# -*- coding: utf-8 -*-
"""Gate-5 evidence replay: feed the RECORDED probe tick log through the REAL production
gate functions (Executor._extreme_regime / _floor_guard_buy) with extreme_regime_enabled=True,
and count how many ticks would have armed EXTREME.

Not production code, not wired anywhere. Read-only over data/execution_logs/probe_ticks_main_*.csv.
Inputs are the values the harness actually recorded live (last/floor/ref/r15/rvol_20d) — r15 is
injected as recorded (monkeypatched) rather than re-derived, because the intraday price buffer
that produced it is not persisted.
"""
import csv, datetime as dt, glob, os, sys
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

from trading_bot.config import DEFAULTS, EXEC_DIR
from trading_bot.plan import PlannedOrder, TradePlan
from trading_bot.executor import Executor

TAG = "selfcheck-replay-extreme"
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(_f)


class Q:
    def __init__(self, last, ref, floor, ceiling):
        self.symbol = "X"; self.exchange = "HOSE"
        self.last = last; self.ref = ref; self.bid = last; self.ask = last
        self.floor = floor; self.ceiling = ceiling; self.day_volume = 1_000_000
    def ok(self):
        return self.last is not None


class B:
    name = "fake"
    def __init__(self): self.placed = []
    def get_quote(self, s): return None
    def place_order(self, **kw): raise AssertionError("replay must never place")
    def cancel_order(self, oid): pass
    def poll_orders(self): return {}
    def get_cash(self): return 10_000_000_000


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


rows = []
for path in sorted(glob.glob("data/execution_logs/probe_ticks_main_*.csv")):
    with open(path) as fh:
        for r in csv.DictReader(fh):
            r["_file"] = os.path.basename(path)
            rows.append(r)

if not rows:
    print("NO TICK ROWS — cannot replay"); sys.exit(2)

cfg = dict(DEFAULTS)
cfg.update({"extreme_regime_enabled": True, "mode": "paper"})
tickers = sorted({r["ticker"] for r in rows})
orders = [PlannedOrder(id=f"BUY-{t}", ticker=t, side="buy", qty=100, ref_price=f(
    next(x["ref"] for x in rows if x["ticker"] == t)) or 10000.0) for t in tickers]
plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="replay",
                 strategy_version="0", state=3, state_name="NEUTRAL", nav_basis={},
                 orders=orders, account=TAG, created_at="2099-01-01T00:00:00")
ex = Executor(plan, B(), cfg)
by_t = {o.ticker: o for o in orders}

_r15_now = {}
ex._r15 = lambda ticker, now: _r15_now.get(ticker)   # inject the RECORDED r15

armed, guarded, by_day = 0, 0, {}
for r in rows:
    t = r["ticker"]; o = by_t[t]
    now = dt.datetime.fromisoformat(r["ts"])
    _r15_now[t] = f(r.get("r15"))
    rv = f(r.get("rvol_20d"))
    if rv is not None:
        ex._gap_ref[t] = {"rvol_20d": rv}
    q = Q(f(r["last"]), f(r["ref"]), f(r["floor"]), f(r["ceiling"]))
    a = ex._extreme_regime(o, q, now)
    g = ex._floor_guard_buy(o, q)
    d = r["ts"][:10]
    b = by_day.setdefault(d, {"n": 0, "armed": 0, "guard": 0})
    b["n"] += 1; b["armed"] += int(bool(a)); b["guard"] += int(bool(g))
    armed += int(bool(a)); guarded += int(bool(g))
    if a or g:
        print(f"  TRIGGER {r['ts']} {t} armed={a} guard={g} last={r['last']} floor={r['floor']}")

print(f"replayed rows={len(rows)} tickers={len(tickers)} files="
      f"{sorted({r['_file'] for r in rows})}")
for d in sorted(by_day):
    b = by_day[d]
    print(f"  {d}: ticks={b['n']:4d}  _extreme_regime armed={b['armed']}  _floor_guard_buy={b['guard']}")
print(f"TOTAL armed={armed} floor_guard={guarded}")
print("RESULT: " + ("PASS — 0 arm, 0 floor-guard over the replayed ticks"
                    if (armed == 0 and guarded == 0) else "FAIL — gate would have fired"))
sys.exit(0 if (armed == 0 and guarded == 0) else 1)
