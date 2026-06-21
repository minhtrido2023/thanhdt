# -*- coding: utf-8 -*-
"""Smoke test offline cho trading_bot — fixture giả lập, không chạm PHS/BQ.

Cover: build plan (mirror/recs/ETF/sell-sync/HALF_SIZE/LAG T+1) + executor
slicing/fill/journal/report + ĐA TÀI KHOẢN (plan riêng từng account, chạy chung
1 session, quota participation tính gộp fleet).

  python test_trading_bot.py
"""

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
shutil.rmtree(TMP, ignore_errors=True)
