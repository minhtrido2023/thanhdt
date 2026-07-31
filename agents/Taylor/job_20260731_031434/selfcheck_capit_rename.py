# -*- coding: utf-8 -*-
"""Self-check Bước 3 (job Taylor_20260731_031434): đổi tên capit_fired -> capit_signal_today.

Câu hỏi phải trả lời — KHÔNG chỉ "code chạy được":
  1. Nhánh quyết định CAPIT trong trading_bot/strategies.py có còn sinh lệnh khi cờ bật?
  2. Status file kiểu CŨ (chỉ có `capit_fired`) có còn hoạt động đúng không (fallback)?
     — quan trọng vì file trên đĩa lúc deploy là bản ghi TRƯỚC lần đổi tên.
  3. Cờ tắt -> KHÔNG có lệnh CAPIT (không đảo ngược ý nghĩa cờ).
Chạy: /home/trido/thanhdt/wc_venv/bin/python mike/agents/Taylor/job_20260731_031434/selfcheck_capit_rename.py
"""
import json, os, sys, tempfile
import pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from trading_bot import strategies as strat
from trading_bot import config as cfgmod
from trading_bot import brokers as brk
from trading_bot.brokers import PaperBroker
from trading_bot.strategies import V23Strategy

TMP = tempfile.mkdtemp(prefix="capit_rename_")
strat.STATUS_FILE = os.path.join(TMP, "status.json")
strat.PT_LOGS = os.path.join(TMP, "logs.csv")
strat.PT_POSITIONS = os.path.join(TMP, "positions.csv")
strat.PT_TRANSACTIONS = os.path.join(TMP, "tx.csv")
strat.GOLIVE_OUT = TMP
brk.DATA_DIR = TMP
brk.EXEC_DIR = os.path.join(TMP, "exec")
brk.PAPER_STATE_FILE = os.path.join(TMP, "paper_capit_rename.json")

SIG = "2026-07-20"

pd.DataFrame([["CAPIT", "NCT", "CAPIT", None, 10_000, 3, 20.0, "WASHOUT"]],
             columns=["book", "ticker", "play_type", "ta", "close", "sector",
                      "weight_pct", "status"]).to_csv(
    os.path.join(TMP, f"golive_v23_recommendations_{SIG}.csv"), index=False)

# paper book: chỉ cần lag_nav (= SECOND_*) > 0 để book CAPIT có vốn — CAPIT size tính trên NAV
# book LAG. Cột đúng theo _load_paper_book().
pd.DataFrame([{"ymd": SIG, "nav": 1_000_000_000.0,
               "BAL_cash": 0.0, "BAL_stocks": 0.0, "BAL_etf": 0.0,
               "SECOND_cash": 1_000_000_000.0, "SECOND_stocks": 0.0, "SECOND_etf": 0.0}]).to_csv(
    strat.PT_LOGS, index=False)
pd.DataFrame(columns=["ymd", "ticker", "shares"]).to_csv(strat.PT_POSITIONS, index=False)
pd.DataFrame(columns=["ymd", "ticker", "price"]).to_csv(strat.PT_TRANSACTIONS, index=False)


class FakeQuotes:
    client = object()
    def connect(self):
        return self
    def get_quote(self, sym):
        ref = 10_000
        return brk.Quote({"symbol": sym, "refPrice": ref, "lastPrice": ref,
                          "bidPrice1": ref, "offerPrice1": ref,
                          "ceiling": ref * 1.07, "floor": ref * 0.93,
                          "totalTrading": 10_000_000, "exchange": "HOSE"})


CFG = dict(cfgmod.DEFAULTS)
CFG.update({"mode": "paper", "min_order_value": 1_000_000})


def n_capit_orders(status_dict, tag):
    with open(strat.STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status_dict, f)
    broker = PaperBroker(init_cash=1_000_000_000, fee_rate=CFG["paper_fee_rate"],
                         quote_source=FakeQuotes(), label=tag).connect()
    plan = V23Strategy().build_plan(CFG, broker, signal_date=SIG)
    return sum(1 for o in plan.orders if o.ticker == "NCT" and str(o.side).lower() == "buy")


BASE = {"date": SIG, "signal_date": SIG, "state": 3, "state_name": "NEUTRAL",
        "capit_size": 0.75, "n_capit_basket": 1}

cases = [
    ("tên MỚI, cờ BẬT   -> phải có lệnh", {**BASE, "capit_signal_today": True}, 1),
    ("tên MỚI, cờ TẮT   -> không lệnh  ", {**BASE, "capit_signal_today": False}, 0),
    ("tên CŨ,  cờ BẬT   -> fallback OK ", {**BASE, "capit_fired": True}, 1),
    ("tên CŨ,  cờ TẮT   -> không lệnh  ", {**BASE, "capit_fired": False}, 0),
    ("thiếu CẢ HAI key  -> fail-safe 0 ", {**BASE}, 0),
]

fails = []
for i, (label, st, want) in enumerate(cases):
    got = n_capit_orders(st, f"cr{i}")
    ok = (got == want) if want == 0 else (got >= 1)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label} | lệnh CAPIT = {got} (kỳ vọng {want})")
    if not ok:
        fails.append(label)

# _load_status phải chuẩn hoá key cũ -> key mới
with open(strat.STATUS_FILE, "w", encoding="utf-8") as f:
    json.dump({**BASE, "capit_fired": True}, f)
norm = V23Strategy()._load_status()
ok = norm.get("capit_signal_today") is True and norm.get("capit_fired") is True
print(f"  [{'PASS' if ok else 'FAIL'}] _load_status chuẩn hoá capit_fired -> capit_signal_today")
if not ok:
    fails.append("_load_status normalize")

print("\nSELF-CHECK PASS" if not fails else "\nSELF-CHECK FAIL: " + "; ".join(fails))
sys.exit(0 if not fails else 1)
