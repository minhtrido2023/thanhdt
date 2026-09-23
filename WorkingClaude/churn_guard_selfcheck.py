# -*- coding: utf-8 -*-
"""Regression + behaviour self-check for the cancel/replace churn-guard fix.

Bug found live 2026-07-01 (SpaceX go-live): 9 BUY tickers pinned at the static
chase cap were CANCEL_STALE'd + re-PLACEd ~33x each every 8min, byte-identical
price+qty every cycle, 0 fills — pure FIFO-priority waste, no benefit.

Fix: `Executor._would_be_unchanged()` recomputes the would-be (px, qty) before
cancelling; if identical to the resting (unfilled) child, skip the cancel and
just reset the child's age clock (keeps broker order + FIFO position intact).

Drives trading_bot.executor.Executor with a fake broker/quote (no network, no
live state, no real orders). Asserts:
  A. Constant-quote churn case (the live bug) → cancel_order called ZERO times
     across many stale cycles; REFRESH_SKIP journaled instead.
  B. Quote that genuinely moves → cancel_order still fires (regression: chase
     behaviour must be unchanged when price should actually update).
  C. Partially-filled resting child → ALWAYS cancels, even if recompute would
     be identical (conservative: never suppress on a partial fill).
  D. EXTREME_DOWN + BUY transitioning to pause → always cancels (placing
     nothing next cycle is not "unchanged").

Run: python churn_guard_selfcheck.py   (exit 0 = all pass, non-zero = a check failed)
"""
import datetime as dt
import glob
import os
import sys

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")  # coding_guidelines §5b — before any Executor()

from trading_bot.config import DEFAULTS, EXEC_DIR

# Fresh journal AND state files each run — the journal path is keyed by account tag +
# plan_date and opened in APPEND mode, so a stale file from a prior run (or another
# scenario reusing the same tag) would leak old CANCEL_STALE/REFRESH_SKIP rows into this
# run's assertions. Also wipe state.json: Executor.__init__ eagerly loads it BEFORE any
# test code can override paths, so a stale "done"/filled state from an earlier run makes
# _place_slices silently skip everything this run (found 2026-07-06 — journal-only
# cleanup here was incomplete, state.json was still leaking across runs).
for _f in glob.glob(os.path.join(EXEC_DIR, "exec_selfcheck-*_journal.csv")):
    os.remove(_f)
for _f in glob.glob(os.path.join(EXEC_DIR, "exec_selfcheck-*_state.json")):
    os.remove(_f)
from trading_bot.plan import PlannedOrder, TradePlan
from trading_bot.executor import Executor
from trading_bot.vn_market import round_price

REF = 26_750.0
CAP = round_price(REF * 1.015, "ZZZFAKE", "HOSE", "down")   # +1.5% chase ceiling (the live-bug price)
FLOOR = round(REF * 0.93, -1)
CEIL = round(REF * 1.07, -1)


class FakeQuote:
    def __init__(self, last, bid, ask, floor=FLOOR, ceiling=CEIL, day_volume=5_000_000):
        self.symbol = "ZZZFAKE"; self.exchange = "HOSE"
        self.last = last; self.ref = REF; self.bid = bid; self.ask = ask
        self.floor = floor; self.ceiling = ceiling; self.day_volume = day_volume

    def ok(self):
        return self.last is not None or self.ref is not None


class FakeBroker:
    """Minimal broker: one (mutable) quote per ticker; records place/cancel calls."""
    name = "fake"

    def __init__(self, quotes):
        self.quotes = quotes; self.placed = []; self.cancelled = []; self._oid = 0
        self.cash = 10_000_000_000

    def get_quote(self, sym):
        return self.quotes.get(sym)

    def place_order(self, symbol, qty, side, price=None, order_type="LO",
                    cash_only=False, loan_package_id=None):
        self._oid += 1
        oid = f"OID{self._oid}"
        self.placed.append(dict(oid=oid, symbol=symbol, qty=qty, side=side, price=price))
        return oid

    def cancel_order(self, oid):
        self.cancelled.append(oid)

    def poll_orders(self):
        return {}

    def get_cash(self):
        return self.cash


def make_exec(cfg_over, orders, quote, tag):
    cfg = dict(DEFAULTS); cfg.update(cfg_over); cfg["mode"] = "paper"
    cfg["slice_interval_min"] = 8   # match production default (live-bug cadence)
    cfg["fill_timing_enabled"] = False  # isolate churn-guard from the unrelated fill-timing
    # layer (Layer-3 buy-window slowdown only applies in paper mode outside 10:45-11:15;
    # on LIVE it's always bypassed via fill_timing_live_gate, matching the real bug's cadence)
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={}, orders=orders, account=f"selfcheck-{tag}",
                     created_at="2099-01-01T00:00:00")
    return Executor(plan, FakeBroker({"ZZZFAKE": quote}), cfg), quote


def journal_topics(ex):
    import csv
    if not __import__("os").path.exists(ex.journal_file):
        return []
    with open(ex.journal_file, encoding="utf-8") as f:
        return [row[1] for row in csv.reader(f) if row]


fails = []
def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


now = dt.datetime(2099, 1, 1, 10, 0, 0)
buy_o = PlannedOrder(id="BUY-TST-01", ticker="ZZZFAKE", side="buy", qty=28_000, ref_price=REF)

# ---------------------------------------------------------------- A. the live bug: constant quote
print("A. Constant quote (gap-up pinned at chase cap) — the live 2026-07-01 bug")
ex_a, q_a = make_exec({"extreme_regime_enabled": False}, [buy_o],
                      FakeQuote(last=CAP + 500, bid=CAP + 400, ask=CAP + 500), "a")  # market above cap all day
t = now
ex_a._place_slices(t, "MORNING")                      # cycle 0: initial placement
check("A0 initial PLACE happened", len(ex_a.broker.placed) == 1)
placed_px = ex_a.broker.placed[0]["price"]
check("A0b placed at the +1.5% chase cap (pinned, matches live bug)", placed_px == CAP,
      f"placed={placed_px} cap={CAP}")
for i in range(1, 6):   # 5 more stale cycles, quote never moves
    t = t + dt.timedelta(minutes=8, seconds=1)
    ex_a._cancel_stale(t)
    ex_a._place_slices(t, "MORNING")
check("A1 cancel_order NEVER called across 5 stale cycles (churn eliminated)",
      len(ex_a.broker.cancelled) == 0, f"cancelled={ex_a.broker.cancelled}")
check("A2 place_order still only called ONCE total (no re-place)",
      len(ex_a.broker.placed) == 1, f"placed={len(ex_a.broker.placed)}")
check("A3 REFRESH_SKIP journaled (visible in journal for audit)",
      "REFRESH_SKIP" in journal_topics(ex_a))
check("A4 CANCEL_STALE NOT journaled", "CANCEL_STALE" not in journal_topics(ex_a))

# ---------------------------------------------------------------- B. regression: quote genuinely moves
print("B. Quote moves down each cycle — must still cancel+reprice (regression)")
mover_q = FakeQuote(last=CAP - 200, bid=CAP - 300, ask=CAP - 200)
ex_b, q_b = make_exec({"extreme_regime_enabled": False}, [buy_o], mover_q, "b")
t = now
ex_b._place_slices(t, "MORNING")
check("B0 initial PLACE happened", len(ex_b.broker.placed) == 1)
for i in range(1, 4):
    t = t + dt.timedelta(minutes=8, seconds=1)
    q_b.ask -= 50; q_b.bid -= 50; q_b.last -= 50   # price genuinely drifts down each cycle
    ex_b._cancel_stale(t)
    ex_b._place_slices(t, "MORNING")
check("B1 cancel_order called every cycle price moved (chase preserved)",
      len(ex_b.broker.cancelled) == 3, f"cancelled={len(ex_b.broker.cancelled)}")
check("B2 place_order called 4x total (1 initial + 3 reprices)",
      len(ex_b.broker.placed) == 4, f"placed={len(ex_b.broker.placed)}")
check("B3 CANCEL_STALE journaled (unchanged regression behaviour)",
      "CANCEL_STALE" in journal_topics(ex_b))

# ---------------------------------------------------------------- C. partial fill → always cancel
print("C. Resting child partially filled → always cancel even if px/qty would repeat")
ex_c, q_c = make_exec({"extreme_regime_enabled": False}, [buy_o],
                      FakeQuote(last=CAP + 500, bid=CAP + 400, ask=CAP + 500), "c")
t = now
ex_c._place_slices(t, "MORNING")
child = ex_c.state["parents"][buy_o.id]["children"][0]
child["filled"] = 100  # simulate a partial fill on the resting child
t = t + dt.timedelta(minutes=8, seconds=1)
ex_c._cancel_stale(t)
check("C1 partially-filled child still cancelled (conservative — no suppression)",
      len(ex_c.broker.cancelled) == 1, f"cancelled={ex_c.broker.cancelled}")

# ---------------------------------------------------------------- D. EXTREME_DOWN+BUY → always cancel
print("D. EXTREME_DOWN arms on a BUY ticker → must cancel (next cycle pauses, not 'unchanged')")
ex_d, q_d = make_exec({"extreme_regime_enabled": True}, [buy_o],
                      FakeQuote(last=CAP + 500, bid=CAP + 400, ask=CAP + 500), "d")
t = now
ex_d._place_slices(t, "MORNING")
check("D0 initial PLACE happened", len(ex_d.broker.placed) == 1)
# force-arm EXTREME_DOWN on this ticker (as the 2-poll confirm would after a real trigger)
ex_d._extreme_state["ZZZFAKE"] = {"n": 2,
    "until": (t + dt.timedelta(minutes=15)).isoformat(timespec="seconds")}
t = t + dt.timedelta(minutes=8, seconds=1)
ex_d._cancel_stale(t)
check("D1 cancelled once EXTREME_DOWN armed on a BUY (would pause, not repeat)",
      len(ex_d.broker.cancelled) == 1, f"cancelled={ex_d.broker.cancelled}")

# ---------------------------------------------------------------- E. no double-poll-count
print("E. Same-cycle double call (_cancel_stale then _place_slices) must NOT double-count "
      "the 2-poll EXTREME confirm (quant-skeptic-flagged side-effect, fixed via _extreme_cache)")
ex_e, q_e = make_exec({"extreme_regime_enabled": True}, [buy_o],
                      FakeQuote(last=CAP + 500, bid=CAP + 400, ask=CAP + 500), "e")
t_e = now
ex_e._place_slices(t_e, "MORNING")   # cycle0: places a resting child, no EXTREME condition yet
child_e = ex_e._open_child(ex_e.state["parents"][buy_o.id])
t_e = t_e + dt.timedelta(minutes=8, seconds=1)
# force the underlying trigger condition true (near-floor) without touching the poll counter
q_e.last = q_e.floor * 1.01; q_e.bid = q_e.last; q_e.ask = q_e.last + 100
# one cycle where BOTH callers ask about the same (ticker, now) — must mutate the counter ONCE
ex_e._would_be_unchanged(buy_o, ex_e.state["parents"][buy_o.id], child_e, t_e)
n_after_cancel_stale_peek = ex_e._extreme_state["ZZZFAKE"]["n"]
ex_e._extreme_regime(buy_o, q_e, t_e)   # what _place_slices would call next in the same cycle
n_after_second_call = ex_e._extreme_state["ZZZFAKE"]["n"]
check("E1 poll counter advances by exactly 1 across 2 same-cycle callers (not 2)",
      n_after_cancel_stale_peek == 1 and n_after_second_call == 1,
      f"n_after_1st_call={n_after_cancel_stale_peek} n_after_2nd_call={n_after_second_call}")
# a genuinely NEW cycle (different `now`) must still be free to advance the counter normally
t_e2 = t_e + dt.timedelta(seconds=20)
ex_e._extreme_regime(buy_o, q_e, t_e2)
check("E2 a real NEW poll (different `now`) still advances the counter (2nd real poll arms)",
      ex_e._extreme_state["ZZZFAKE"]["n"] >= 2, f"n={ex_e._extreme_state['ZZZFAKE']['n']}")

# ---------------------------------------------------------------- F. gap-ref staleness/contiguity guard
print("F. Real-but-gappy ticker (TST — excluded from ticker_prune, present but sparse in the "
      "full ticker superset) must still resolve to the STATIC chase cap: proves the recency/"
      "contiguity guard in _load_gap_ref_data() blocks an inflated rvol_20d computed from a "
      "gappy tail(22) instead of silently widening the LIVE chase_cap_vol_scale_enabled cap")
gappy_o = PlannedOrder(id="BUY-TST-01F", ticker="TST", side="buy", qty=28_000, ref_price=REF)
cap_tst = round_price(REF * 1.015, "TST", "HOSE", "down")
plan_f = TradePlan(plan_date="2026-09-19", signal_date="2026-09-19", strategy="tst",
                    strategy_version="0", state=3, state_name="NEUTRAL",
                    nav_basis={}, orders=[gappy_o], account="selfcheck-f",
                    created_at="2026-09-19T00:00:00")
cfg_f = dict(DEFAULTS); cfg_f.update({"mode": "paper", "slice_interval_min": 8,
                                       "fill_timing_enabled": False, "extreme_regime_enabled": False})
q_f = FakeQuote(last=cap_tst + 500, bid=cap_tst + 400, ask=cap_tst + 500)
q_f.symbol = "TST"
ex_f = Executor(plan_f, FakeBroker({"TST": q_f}), cfg_f)
check("F1 TST absent from _gap_ref (gappy/stale history filtered by guard)",
      "TST" not in ex_f._gap_ref, f"_gap_ref={ex_f._gap_ref}")
ex_f._place_slices(dt.datetime(2026, 9, 19, 10, 0, 0), "MORNING")
placed_px_f = ex_f.broker.placed[0]["price"]
check("F2 placed at the STATIC cap despite chase_cap_vol_scale ON (fail-safe held)",
      placed_px_f == cap_tst, f"placed={placed_px_f} cap={cap_tst}")

# ---------------------------------------------------------------- G. gap-ref DATA SOURCE pin
# Section F proves the recency/contiguity guard works, but it does NOT pin WHICH cache dir
# `_load_gap_ref_data()` reads: its fixture ticker (TST) is absent from BOTH `ticker` and
# `ticker_prune`, so reverting the source back to the TRAP table still passes F (verified by
# mutation 2026-09-24, job Taylor_20260923_235320). G closes that hole with a SYNTHETIC
# two-source cache so the assertion is deterministic and needs no real bq_cache on disk:
#   bq_cache/ticker/       ZZZSRC @ 20_000  <- the LIVE source (commit fd3f5597)
#   bq_cache/ticker_prune/ ZZZSRC @ 50_000  <- decoy; reading it yields a WRONG prior_close
# Reverting chunk_dir to "ticker_prune" therefore dies on an ASSERTION (wrong value), not a crash.
print("G. gap-ref must read the tav2_bq.ticker cache, not the TRAP ticker_prune cache "
      "(fd3f5597 / universe_pit migration gate G8.1) — pinned by value with a decoy fixture")
import tempfile, shutil
_g_tmp = tempfile.mkdtemp(prefix="gapref_src_")
_g_prev_cache = os.environ.get("BQ_LOCAL_CACHE")
try:
    import pandas as _pd
    G_PLAN_DATE = "2026-09-24"          # fixed: no now()/TZ dependency
    _g_days = _pd.bdate_range(end="2026-09-23", periods=22)
    def _g_write(sub, close):
        d = os.path.join(_g_tmp, sub); os.makedirs(d, exist_ok=True)
        # alternating +/-1 tick keeps rvol_20d > 0 (else the loader skips the ticker)
        px = [close + (100 if i % 2 else 0) for i in range(len(_g_days))]
        px[-1] = close
        _pd.DataFrame({"time": _g_days, "ticker": "ZZZSRC", "Close": [float(x) for x in px]}
                      ).to_parquet(os.path.join(d, "chunk.parquet"), index=False)
    _g_write("ticker", 20_000.0)         # LIVE source
    _g_write("ticker_prune", 50_000.0)   # decoy — only reachable if the source is reverted
    os.environ["BQ_LOCAL_CACHE"] = _g_tmp
    g_o = PlannedOrder(id="BUY-SRC-01G", ticker="ZZZSRC", side="buy", qty=1_000, ref_price=REF)
    plan_g = TradePlan(plan_date=G_PLAN_DATE, signal_date=G_PLAN_DATE, strategy="tst",
                       strategy_version="0", state=3, state_name="NEUTRAL",
                       nav_basis={}, orders=[g_o], account="selfcheck-g",
                       created_at=G_PLAN_DATE + "T00:00:00")
    cfg_g = dict(DEFAULTS); cfg_g.update({"mode": "paper", "slice_interval_min": 8,
                                          "fill_timing_enabled": False,
                                          "extreme_regime_enabled": False})
    q_g = FakeQuote(last=20_000, bid=19_900, ask=20_000); q_g.symbol = "ZZZSRC"
    ex_g = Executor(plan_g, FakeBroker({"ZZZSRC": q_g}), cfg_g)
    _g_ref = ex_g._gap_ref.get("ZZZSRC")
    check("G1 gap-ref resolved from the synthetic cache at all (loader reached a chunk dir)",
          _g_ref is not None, f"_gap_ref={ex_g._gap_ref}")
    check("G2 prior_close comes from bq_cache/ticker, NOT the ticker_prune decoy",
          _g_ref is not None and _g_ref["prior_close"] == 20_000.0,
          f"prior_close={_g_ref and _g_ref['prior_close']} expected=20000.0 decoy=50000.0")
finally:
    if _g_prev_cache is None:
        os.environ.pop("BQ_LOCAL_CACHE", None)
    else:
        os.environ["BQ_LOCAL_CACHE"] = _g_prev_cache
    shutil.rmtree(_g_tmp, ignore_errors=True)


print()
if fails:
    print(f"FAILED {len(fails)} check(s): {fails}")
    sys.exit(1)
print("ALL CHECKS PASSED — churn eliminated on constant quote; chase/cancel regression intact;"
      " partial-fill and EXTREME-pause cases stay conservative (always cancel).")
sys.exit(0)
