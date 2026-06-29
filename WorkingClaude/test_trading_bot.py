# -*- coding: utf-8 -*-
"""Smoke test offline cho trading_bot — fixture giả lập, không chạm PHS/BQ.

Cover: build plan (mirror/recs/ETF/sell-sync/HALF_SIZE/LAG T+1) + executor
slicing/fill/journal/report + ĐA TÀI KHOẢN (plan riêng từng account, chạy chung
1 session, quota participation tính gộp fleet).

  python test_trading_bot.py
"""

import datetime as dt
import json
import os
import shutil
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd

from trading_bot import config as cfgmod
from trading_bot import strategies as strat
from trading_bot import brokers as brk
from trading_bot import plan as planmod
from trading_bot import executor as execmod
from trading_bot.brokers import PaperBroker
from trading_bot.executor import Executor, run_session
from trading_bot.strategies import V23Strategy

TMP = tempfile.mkdtemp(prefix="bot_test_")
print(f"fixture dir: {TMP}")

# --- chuyển hướng mọi path sang TMP ---
strat.STATUS_FILE = os.path.join(TMP, "status.json")
strat.PT_LOGS = os.path.join(TMP, "logs.csv")
strat.PT_POSITIONS = os.path.join(TMP, "positions.csv")
strat.PT_TRANSACTIONS = os.path.join(TMP, "tx.csv")
strat.GOLIVE_OUT = TMP
planmod.PLAN_DIR = os.path.join(TMP, "plans")
execmod.EXEC_DIR = os.path.join(TMP, "exec")
execmod.STOP_FILE = os.path.join(TMP, "BOT_STOP")
brk.DATA_DIR = TMP
brk.EXEC_DIR = os.path.join(TMP, "exec")
brk.PAPER_STATE_FILE = os.path.join(TMP, "paper_main.json")

# --- fixtures ---
SIG = "2026-06-11"
json.dump({"date": SIG, "signal_date": SIG, "state": 3, "state_name": "NEUTRAL",
           "capit_fired": False, "n_capit_basket": 0},
          open(strat.STATUS_FILE, "w", encoding="utf-8"))

pd.DataFrame([
    ["BAL", "AAA", "MOMENTUM", 80.0, 10_000, 3, 10.0, "FULL"],
    ["BAL", "BBB", "MEGA", 70.0, 50_000, 8, 10.0, "HALF_SIZE"],
    ["LAG", "CCC", "LAG_HI", None, 20_000, 5, 10.0, "UPCOMING T+1 phiên tới"],
    ["LAG", "DDD", "LAG_LO", None, 30_000, 5, 8.0, "UPCOMING T+5 phiên tới"],  # loại
], columns=["book", "ticker", "play_type", "ta", "close", "sector",
            "weight_pct", "status"]).to_csv(
    os.path.join(TMP, f"golive_v23_recommendations_{SIG}.csv"), index=False)

pd.DataFrame([{
    "ymd": SIG, "nav": 50e9, "BAL_cash": 20e9, "BAL_stocks": 4e9, "BAL_etf": 1e9,
    "SECOND_cash": 25e9, "SECOND_stocks": 0.0, "SECOND_etf": 0.0,
    "cash": 45e9, "cash_etf": 1e9, "stocks_mv": 4e9, "num_holdings": 1,
    "num_transactions": 1, "state": 3, "active_leg": "LAG_ALLOC", "ens_signal": 0,
}]).to_csv(strat.PT_LOGS, index=False)
pd.DataFrame([{"ticker": "XYZ", "holding_id": "h1", "shares": 100_000, "book": "BAL"}]
             ).to_csv(strat.PT_POSITIONS, index=False)
pd.DataFrame([{"ymd": SIG, "ticker": "XYZ", "action": "buy", "buy_amount": 4e9,
               "sell_amount": 0, "fee": 0, "adj_price": 40_000, "shares": 100_000,
               "holding_id": "h1", "play_type": "MOMENTUM", "cash_after": 0,
               "reason": "SIGNAL_ENTRY", "book": "BAL"}]).to_csv(
    strat.PT_TRANSACTIONS, index=False)

REFS = {"AAA": 10_000, "BBB": 50_000, "CCC": 20_000, "DDD": 30_000,
        "XYZ": 40_000, "OLD": 12_000, "E1VFVN30": 25_000}
AAA_DAY_VOL = 20_000          # KL ngày nhỏ → test quota participation gộp fleet


class FakeQuotes:
    """Nguồn quote giả: bid=ask=last=ref, AAA thanh khoản thấp."""
    client = object()
    def connect(self):
        return self
    def get_quote(self, sym):
        ref = REFS.get(sym)
        if not ref:
            return None
        vol = AAA_DAY_VOL if sym == "AAA" else 10_000_000
        return brk.Quote({"symbol": sym, "refPrice": ref, "lastPrice": ref,
                          "bidPrice1": ref, "offerPrice1": ref,
                          "ceiling": ref * 1.07, "floor": ref * 0.93,
                          "totalTrading": vol, "exchange": "HOSE"})


cfg = dict(cfgmod.DEFAULTS)
cfg.update({"mode": "paper", "max_child_value": 20_000_000,
            "slice_interval_min": 0, "poll_interval_sec": 0,
            "min_order_value": 1_000_000})

fq = FakeQuotes()
brokerA = PaperBroker(init_cash=1_000_000_000, fee_rate=cfg["paper_fee_rate"],
                      quote_source=fq, label="testA").connect()
brokerA.state["positions"]["OLD"] = 5_000   # vị thế thừa → SELL sync
brokerA._save()
brokerB = PaperBroker(init_cash=500_000_000, fee_rate=cfg["paper_fee_rate"],
                      quote_source=fq, label="testB").connect()

# ============ 1) build plan từng account (scale theo NAV riêng) ============
planA = V23Strategy().build_plan(cfg, brokerA)
planA.account = "testA"
planB = V23Strategy().build_plan(cfg, brokerB)
planB.account = "testB"
print()
print(planA.summary())
print()
print(planB.summary())
pA, pB = planA.save(), planB.save()
assert pA != pB and "testA" in pA and "testB" in pB, "plan phải namespace theo account"
assert os.path.exists(brokerA.state_file) and os.path.exists(brokerB.state_file)
assert brokerA.state_file != brokerB.state_file, "paper state phải tách theo account"

osides = {(o.ticker, o.side) for o in planA.orders}
assert ("OLD", "sell") in osides, "thiếu lệnh SELL sync OLD"
assert {("AAA", "buy"), ("BBB", "buy"), ("CCC", "buy"), ("XYZ", "buy"),
        ("E1VFVN30", "buy")} <= osides
assert not any(o.ticker == "DDD" for o in planA.orders), "DDD (T+5) phải bị loại"
assert ("OLD", "sell") not in {(o.ticker, o.side) for o in planB.orders}

scaleA = planA.nav_basis["scale"]
aaaA = next(o for o in planA.orders if o.ticker == "AAA")
bbbA = next(o for o in planA.orders if o.ticker == "BBB")
exp_aaa = int(25e9 * scaleA * 0.10 / 10_000 // 100) * 100
assert abs(aaaA.qty - exp_aaa) <= 100, f"AAA qty {aaaA.qty} ≠ ~{exp_aaa}"
assert abs(bbbA.qty - exp_aaa * (10_000 / 50_000) * 0.5) <= 100, "BBB phải HALF_SIZE"
aaaB = next(o for o in planB.orders if o.ticker == "AAA")
assert aaaB.qty < aaaA.qty, "account B NAV nhỏ hơn → qty nhỏ hơn"

# ============ 2) run_session đa tài khoản, quota participation gộp ============
loadA = planmod.load_plan(planA.plan_date, account="testA")
loadB = planmod.load_plan(planB.plan_date, account="testB")
shared = {}
exA = Executor(loadA, brokerA, cfg, shared=shared)
exB = Executor(loadB, brokerB, cfg, shared=shared)
run_session([exA, exB], max_cycles=40, force_phase="MORNING")

# quota fleet: AAA chỉ được mua ≤ 10% × 20,000 = 2,000 CP TOÀN BỘ fleet
quota = int(cfg["max_participation"] * AAA_DAY_VOL)
assert shared.get("AAA", 0) <= quota, f"fleet mua AAA {shared.get('AAA')} > quota {quota}"
assert shared.get("AAA", 0) == quota, "fleet phải dùng hết quota AAA"
assert not exA.state["parents"][aaaA.id]["done"], "AAA A phải bị chặn quota"
fillA = exA.state["parents"][aaaA.id]["filled"]
fillB = exB.state["parents"][aaaB.id]["filled"]
assert fillA + fillB == quota, f"tổng fill AAA {fillA}+{fillB} ≠ quota {quota}"

# các mã thanh khoản tốt phải khớp đủ ở CẢ 2 account
for ex, plan in ((exA, loadA), (exB, loadB)):
    for o in plan.orders:
        if o.ticker != "AAA":
            assert ex.state["parents"][o.id]["done"], f"[{plan.account}] {o.id} chưa xong"

# slicing: XYZ A ~84M với child cap 20M → ≥4 lệnh con
xyzA = next(o for o in loadA.orders if o.ticker == "XYZ")
n_children = len(exA.state["parents"][xyzA.id]["children"])
assert n_children >= 4, f"XYZ phải bị cắt ≥4 lệnh con, got {n_children}"

# file output tách theo account
for ex in (exA, exB):
    assert os.path.exists(ex.report_file) and os.path.exists(ex.journal_file)
assert exA.report_file != exB.report_file

# paper account khớp đúng
posA = brokerA.get_positions()
assert posA.get("XYZ", {}).get("total") == xyzA.qty
assert "OLD" not in posA
assert brokerB.get_positions().get("AAA", {}).get("total", 0) == fillB

# ============ 3) DNSEBroker: lắp ráp quote + mapping sổ lệnh (fake client) ============
class FakeDNSE:
    def secdef(self, sym):
        return {"symbol": sym, "ceilingPrice": 24900, "floorPrice": 21700,
                "basicPrice": 23300}
    def latest_trade(self, sym):
        return {"matchPrice": 23450, "totalVolumeTraded": 5343800}
    def latest_quote(self, sym):
        return {"bids": [{"price": 23400, "qty": 100}],
                "offers": [{"price": 23450, "qty": 200}]}
    def orders(self, acc, market_type="STOCK", order_category=None):
        return {"orders": [{"id": 123, "orderStatus": "PartiallyFilled",
                            "fillQuantity": 700, "averagePrice": 23450}]}
    def positions(self, acc, market_type="STOCK"):
        return {"positions": [{"symbol": "HPG", "quantity": 1000,
                               "availableQuantity": 800}]}
    def balances(self, acc):
        return {"availableCash": 123_000_000}


db = brk.DNSEBroker(account_id="0001", label="dnsetest")
db.client = FakeDNSE()
q = db.get_quote("HPG")
assert (q.last, q.ref, q.bid, q.ask) == (23450, 23300, 23400, 23450), q
assert (q.ceiling, q.floor, q.day_volume) == (24900, 21700, 5343800), q
ups = db.poll_orders()
assert ups["123"].filled_qty == 700 and not ups["123"].is_dead, \
    "PartiallyFilled phải còn SỐNG"
assert db.get_positions() == {"HPG": {"total": 1000, "sellable": 800}}
assert db.get_cash() == 123_000_000

print("\n✅ TEST PASS — plan + slicing + fill + multi-account + fleet quota "
      "+ DNSE mapping đều đúng")

# ============ 4) gap-adaptive fill timing (paper, gap_adaptive_enabled) ============
from trading_bot.plan import PlannedOrder, TradePlan

print("\n--- gap-adaptive fill timing tests ---")

gap_order = PlannedOrder(id="BUY-GAP-01", ticker="GAPTEST", side="buy",
                         qty=1000, ref_price=10_000)
gap_plan = TradePlan(
    plan_date="2026-06-29", signal_date="2026-06-28",
    strategy="test", strategy_version="1", state=3, state_name="NEUTRAL",
    nav_basis={}, orders=[gap_order], account="gaptest",
)
gcfg = dict(cfgmod.DEFAULTS)
gcfg.update({
    "mode": "paper",
    "gap_adaptive_enabled": True,
    "fill_timing_enabled": True,
    "fill_timing_live_gate": True,
    "fill_timing_outside_mult": 4.0,
    "buy_window_start": "10:45",
    "buy_window_end": "11:15",
})
gap_broker = PaperBroker(init_cash=1_000_000_000, fee_rate=0.0015,
                          quote_source=fq, label="gaptest").connect()
gap_exec = Executor(gap_plan, gap_broker, gcfg, shared={})

# Bypass parquet by directly setting ref data (prior_close=10000, rvol=0.02)
# Then set gap_z = -3.0 (genuine down-gap, well below -2 threshold)
gap_exec._gap_ref["GAPTEST"] = {"prior_close": 10_000.0, "rvol_20d": 0.02}
gap_exec._gap_z_cache["GAPTEST"] = -3.0   # gap_z < -2.0 → override active

# Test 1a: down-gap at 09:30 (inside 09:15-09:45 window) → must return 1.0
t_in = dt.datetime(2026, 6, 29, 9, 30)
m_in = gap_exec._fill_timing_mult(gap_order, t_in)
assert m_in == 1.0, f"[FAIL] down-gap in window: expected 1.0, got {m_in}"
print(f"  [1a] down-gap 09:30 in-window  → mult={m_in} ✓")

# Test 1b: down-gap at 09:50 (after window) → falls through to normal rule (mult=4)
t_after = dt.datetime(2026, 6, 29, 9, 50)
m_after = gap_exec._fill_timing_mult(gap_order, t_after)
assert m_after == gcfg["fill_timing_outside_mult"], \
    f"[FAIL] down-gap after window: expected {gcfg['fill_timing_outside_mult']}, got {m_after}"
print(f"  [1b] down-gap 09:50 after-window → mult={m_after} ✓")

# Test 2a: up-gap (gap_z = +1.5) → normal rule, same as feature-disabled
gap_exec._gap_z_cache["GAPTEST"] = 1.5
m_up = gap_exec._fill_timing_mult(gap_order, t_in)
assert m_up == gcfg["fill_timing_outside_mult"], \
    f"[FAIL] up-gap: expected {gcfg['fill_timing_outside_mult']}, got {m_up}"
print(f"  [2a] up-gap 09:30                → mult={m_up} (normal rule) ✓")

# Test 2b: gap_adaptive_enabled=False with down-gap → byte-identical to current rule
gcfg_off = dict(gcfg)
gcfg_off["gap_adaptive_enabled"] = False
gap_exec_off = Executor(gap_plan, gap_broker, gcfg_off, shared={})
gap_exec_off._gap_z_cache["GAPTEST"] = -3.0  # would trigger, but feature is OFF
m_off = gap_exec_off._fill_timing_mult(gap_order, t_in)
assert m_off == gcfg["fill_timing_outside_mult"], \
    f"[FAIL] feature disabled: expected {gcfg['fill_timing_outside_mult']}, got {m_off}"
print(f"  [2b] feature disabled, down-gap  → mult={m_off} (normal rule) ✓")

# Test 3: rvol missing → no override (fail-safe to normal rule)
gap_exec._gap_z_cache.pop("GAPTEST", None)   # clear cache so _cache_gap_z would run
gap_exec._gap_ref.pop("GAPTEST", None)        # no ref data = rvol missing
# Simulate what _cache_gap_z does when ref is missing: sets None
gap_exec._gap_z_cache["GAPTEST"] = None
m_noref = gap_exec._fill_timing_mult(gap_order, t_in)
assert m_noref == gcfg["fill_timing_outside_mult"], \
    f"[FAIL] rvol missing: expected {gcfg['fill_timing_outside_mult']}, got {m_noref}"
print(f"  [3]  rvol missing → gap_z=None  → mult={m_noref} (fail-safe) ✓")

# Test 3b: ticker absent from cache entirely (not yet computed) → also fail-safe
gap_exec._gap_z_cache.pop("GAPTEST", None)
m_absent = gap_exec._fill_timing_mult(gap_order, t_in)
assert m_absent == gcfg["fill_timing_outside_mult"], \
    f"[FAIL] cache absent: expected {gcfg['fill_timing_outside_mult']}, got {m_absent}"
print(f"  [3b] cache absent (not computed) → mult={m_absent} (fail-safe) ✓")

# Test 4: SELL side is always unchanged (gap_adaptive never touches sell)
sell_order = PlannedOrder(id="SELL-GAP-01", ticker="GAPTEST", side="sell",
                          qty=1000, ref_price=10_000)
gap_exec._gap_z_cache["GAPTEST"] = -3.0  # down-gap, but this is a sell
t_sell_in = dt.datetime(2026, 6, 29, 9, 25)   # inside sell window
m_sell = gap_exec._fill_timing_mult(sell_order, t_sell_in)
assert m_sell == 1.0, f"[FAIL] sell in 09:15-09:45 should be 1.0 (sell window), got {m_sell}"
t_sell_out = dt.datetime(2026, 6, 29, 10, 0)   # outside sell window
m_sell_out = gap_exec._fill_timing_mult(sell_order, t_sell_out)
assert m_sell_out == gcfg["fill_timing_outside_mult"], \
    f"[FAIL] sell outside window should be mult, got {m_sell_out}"
print(f"  [4]  SELL unchanged (in={m_sell} out={m_sell_out}) ✓")

print("\n✅ gap-adaptive fill timing: all 7 assertions PASS")

# ============ 5) floor guard + journal marker + per-account config ============
import csv as _csv
print("\n--- gap floor guard + journal marker tests ---")

# 5a: open AT floor → _cache_gap_z sets None → override suppressed
q_at_floor = brk.Quote({"symbol": "GAPTEST", "lastPrice": 9_300, "refPrice": 10_000,
                         "floor": 9_300, "ceiling": 10_700,
                         "totalTrading": 10_000_000, "exchange": "HOSE"})
gap_exec._gap_ref["GAPTEST"] = {"prior_close": 10_000.0, "rvol_20d": 0.02}
gap_exec._gap_z_cache.pop("GAPTEST", None)
gap_exec._cache_gap_z("GAPTEST", q_at_floor)
assert gap_exec._gap_z_cache.get("GAPTEST") is None, \
    f"[FAIL] open at floor: gap_z should be None, got {gap_exec._gap_z_cache.get('GAPTEST')}"
m_5a = gap_exec._fill_timing_mult(gap_order, t_in)
assert m_5a == gcfg["fill_timing_outside_mult"], \
    f"[FAIL] at floor: expected {gcfg['fill_timing_outside_mult']}, got {m_5a}"
print(f"  [5a] open at floor (9300=floor) → gap_z=None → mult={m_5a} (fail-safe) ✓")

# 5b: open above floor (-5% vs floor at -7%) with genuine down-gap → override fires
q_above_floor = brk.Quote({"symbol": "GAPTEST", "lastPrice": 9_500, "refPrice": 10_000,
                            "floor": 9_300, "ceiling": 10_700,
                            "totalTrading": 10_000_000, "exchange": "HOSE"})
gap_exec._gap_z_cache.pop("GAPTEST", None)
gap_exec._cache_gap_z("GAPTEST", q_above_floor)
gz_5b = gap_exec._gap_z_cache.get("GAPTEST")
assert gz_5b is not None and gz_5b < -2.0, \
    f"[FAIL] above-floor down-gap: expected gap_z<-2, got {gz_5b}"
m_5b = gap_exec._fill_timing_mult(gap_order, t_in)  # t_in = 09:30, in window
assert m_5b == 1.0, f"[FAIL] above-floor down-gap at 09:30: expected 1.0, got {m_5b}"
print(f"  [5b] open above floor (9500, floor=9300) gap_z={gz_5b:.2f} → mult={m_5b} ✓")

# 5c: journal marker 'GAP_OPEN_OVERRIDE gap_z=...' in PLACE note when override fires
class _GapTestQuotes:
    client = object()
    def connect(self): return self
    def get_quote(self, sym):
        if sym == "GAPTEST":
            return brk.Quote({"symbol": "GAPTEST", "lastPrice": 9_500, "refPrice": 10_000,
                              "bidPrice1": 9_500, "offerPrice1": 9_500,
                              "floor": 9_300, "ceiling": 10_700,
                              "totalTrading": 10_000_000, "exchange": "HOSE"})
        return None

from trading_bot.plan import PlannedOrder as _PO, TradePlan as _TP
gap_order_j = _PO(id="BUY-GAP-J1", ticker="GAPTEST", side="buy",
                  qty=1000, ref_price=10_000)
gap_plan_j = _TP(plan_date="2026-06-29", signal_date="2026-06-28",
                 strategy="test", strategy_version="1", state=3, state_name="NEUTRAL",
                 nav_basis={}, orders=[gap_order_j], account="gapjournal")
gcfg_j = dict(gcfg)
gcfg_j.update({"slice_interval_min": 0, "poll_interval_sec": 0,
               "max_child_value": 200_000_000, "min_order_value": 1_000_000})
gap_broker_j = PaperBroker(init_cash=1_000_000_000, fee_rate=0.0015,
                            quote_source=_GapTestQuotes(), label="gapjournal").connect()
gap_exec_j = Executor(gap_plan_j, gap_broker_j, gcfg_j, shared={})
gap_exec_j._gap_z_cache["GAPTEST"] = -3.0  # genuine down-gap, no floor suppression
t_journal = dt.datetime(2026, 6, 29, 9, 30)
gap_exec_j.step(t_journal, "MORNING", cont=True)
with open(gap_exec_j.journal_file, newline="", encoding="utf-8") as _f:
    _rows = list(_csv.DictReader(_f))
place_notes = [r["note"] for r in _rows if r["event"] == "PLACE"]
assert place_notes, f"[FAIL] no PLACE events in journal: {[r['event'] for r in _rows]}"
assert any("GAP_OPEN_OVERRIDE" in n for n in place_notes), \
    f"[FAIL] journal marker missing from PLACE note: {place_notes}"
assert any("gap_z=" in n for n in place_notes), \
    f"[FAIL] gap_z value missing from journal note: {place_notes}"
print(f"  [5c] journal marker present: '{place_notes[0]}' ✓")

# 5d: per-account config — verify DNSE live accounts do NOT inherit gap_adaptive=True
from trading_bot.config import load_config, load_accounts
_cfg = load_config()
assert _cfg["gap_adaptive_enabled"] is False, "DEFAULTS must stay gap_adaptive_enabled=False"
_profiles = load_accounts(_cfg)
_paper_main = next((p for p in _profiles if p["label"] == "main"), None)
_dnse_live = [p for p in _profiles if p.get("broker") == "dnse" and p.get("mode") == "live"]
assert _paper_main is not None, "[FAIL] 'main' account not found"
assert _paper_main["cfg"]["gap_adaptive_enabled"] is True, \
    f"[FAIL] main paper: expected gap_adaptive_enabled=True, got {_paper_main['cfg']['gap_adaptive_enabled']}"
for _p in _dnse_live:
    assert _p["cfg"].get("gap_adaptive_enabled", False) is False, \
        f"[FAIL] {_p['label']} live: gap_adaptive_enabled must be False, got {_p['cfg'].get('gap_adaptive_enabled')}"
print(f"  [5d] per-account config: main paper=True, DNSE live accounts={[p['label'] for p in _dnse_live]} all False ✓")

print("\n✅ floor guard + journal marker + per-account config: all assertions PASS")

shutil.rmtree(TMP, ignore_errors=True)
