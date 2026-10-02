# -*- coding: utf-8 -*-
"""Selfcheck: get_positions() KHÔNG được đổi tradeQuantity=0 thành sellable=total
(`int(x or total)` cũ). Job Taylor_20261002_103812.

Phủ DNSEBroker, PHSBroker, PHSFlashBroker (3 site cùng lỗi) + bản ghi THẬT cuối ngày
2026-10-02 của cả 2 account (live get_positions()['sellable'] == nhánh jsonl
park_holdings.aggregate_position_rows). Run: python brokers_tradequantity_selfcheck.py
"""
import json
import os
import sys

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")  # §5b (không dựng Executor, nhưng giữ guard)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MIKE_BIN = os.environ.get("MIKE_BIN", "/home/trido/thanhdt/WorkingClaude/mike/bin")
sys.path.insert(0, MIKE_BIN)
from trading_bot.brokers import DNSEBroker, PHSBroker, PHSFlashBroker  # noqa: E402

FIXTURE = os.path.join(MIKE_BIN, "fixtures", "dnse_positions_eod_20261002.json")
fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


class _C:
    def __init__(self, payload):
        self.payload = payload

    def positions(self, acc):
        return self.payload

    def portfolio(self, acc):
        return self.payload

    def get_positions(self, acc):
        return self.payload


def mk(cls, payload):
    b = cls(account_id="X")
    b.client = _C(payload)
    b._log_raw = lambda *a, **k: None
    return b


def dn(rows, **kw):
    return mk(DNSEBroker, {"positions": rows}).get_positions()


def row(sym="AAA", open_=100, **kw):
    r = {"symbol": sym, "status": "OPEN", "openQuantity": open_, "marketPrice": 10000}
    r.update(kw)
    return r


print("== DNSEBroker synthetic")
check("D1 tq=0 -> sellable 0", dn([row(tradeQuantity=0)])["AAA"]["sellable"] == 0)
check("D2 tq vắng -> total", dn([row()])["AAA"]["sellable"] == 100)
check("D3 tq=30/total 100 -> 30", dn([row(tradeQuantity=30)])["AAA"]["sellable"] == 30)
check("D4 tq=150>total 100 -> 150 (không cắt, cùng quy ước loan-package)",
      dn([row(tradeQuantity=150)])["AAA"]["sellable"] == 150)
check("D5 tq âm -> 0", dn([row(tradeQuantity=-5)])["AAA"]["sellable"] == 0)
r = dn([row("BID", 7, loanPackageId=1, tradeQuantity=0),
        row("BID", 20, loanPackageId=2, tradeQuantity=0)])
check("D6 BID 7+20 tq 0+0 -> qty 27 sellable 0", r["BID"]["total"] == 27 and r["BID"]["sellable"] == 0, str(r))
r = dn([row("MBB", 52, loanPackageId=1, tradeQuantity=2), row("MBB", 223, loanPackageId=2, tradeQuantity=223)])
check("D7 gộp tq 2+223 -> 225, total 275", r["MBB"]["sellable"] == 225 and r["MBB"]["total"] == 275, str(r))
r = dn([row("X1", 10, loanPackageId=1, tradeQuantity=0), row("X1", 20, loanPackageId=2)])
check("D8 gộp: 1 dòng tq=0 + 1 dòng khoá vắng -> 0+20", r["X1"]["sellable"] == 20, str(r))
for tok in ("NaN", "Infinity", "-Infinity"):
    try:
        got = dn([row(tradeQuantity=float(tok.lower().replace("infinity", "inf")))])["AAA"]
        check(f"D9 tq={tok} không ném, sellable 0, total giữ 100",
              got["sellable"] == 0 and got["total"] == 100, str(got))
    except Exception as e:  # noqa: BLE001
        check(f"D9 tq={tok} không ném", False, repr(e))
for alias in ("availablequantity", "sellablequantity", "availableqty"):
    check(f"D10 alias {alias}=0 -> 0", dn([row(**{alias: 0})])["AAA"]["sellable"] == 0)
    check(f"D10 alias {alias}=40 -> 40", dn([row(**{alias: 40})])["AAA"]["sellable"] == 40)
check("D11 tq='' / null (qget bỏ qua) -> total", dn([row(tradeQuantity=None)])["AAA"]["sellable"] == 100)
check("D12 tq chuỗi '0' -> 0", dn([row(tradeQuantity="0")])["AAA"]["sellable"] == 0)
check("D13 field khác không đổi (total/price)", dn([row(tradeQuantity=0)])["AAA"]["marketPrice"] == 10000)

print("== PHSBroker synthetic (alias trade/avlqtty/sellable/availableqtty)")
def ph(rows):
    return mk(PHSBroker, rows).get_positions()
check("P1 trade=0 -> 0", ph([{"symbol": "AAA", "total": 100, "trade": 0}])["AAA"]["sellable"] == 0)
check("P2 vắng -> total", ph([{"symbol": "AAA", "total": 100}])["AAA"]["sellable"] == 100)
check("P3 trade=30 -> 30", ph([{"symbol": "AAA", "total": 100, "trade": 30}])["AAA"]["sellable"] == 30)
check("P4 avlqtty=0 -> 0", ph([{"symbol": "AAA", "total": 100, "avlqtty": 0}])["AAA"]["sellable"] == 0)
check("P5 NaN không ném -> 0", ph([{"symbol": "AAA", "total": 100, "trade": float("nan")}])["AAA"]["sellable"] == 0)

print("== PHSFlashBroker synthetic")
def pf(rows):
    return mk(PHSFlashBroker, rows).get_positions()
check("F1 trade=0 -> 0", pf([{"symbol": "AAA", "total": 100, "trade": 0}])["AAA"]["sellable"] == 0)
check("F2 vắng -> total", pf([{"symbol": "AAA", "total": 100}])["AAA"]["sellable"] == 100)
check("F3 trade=30 -> 30", pf([{"symbol": "AAA", "total": 100, "trade": 30}])["AAA"]["sellable"] == 30)
check("F4 inf không ném -> 0", pf([{"symbol": "AAA", "total": 100, "trade": float("inf")}])["AAA"]["sellable"] == 0)
check("F5 receivable giữ nguyên", pf([{"symbol": "AAA", "total": 100, "trade": 0, "receivingT1": 7}])["AAA"]["receivable"] == 7)

print("== bản ghi THẬT 2026-10-02")
import park_holdings as ph_mod  # noqa: E402
recs = json.load(open(FIXTURE, encoding="utf-8"))["records"]
EXPECT0 = {"ZaloPay": {"VIB": 19, "MSB": 40, "BID": 27, "VPB": 312},
           "SpaceX": {"VIB": 47, "TPB": 30, "BID": 75, "MBB": 275, "MSB": 100, "VPB": 286}}
check("R0 fixture có 2 account", {r["account_label"] for r in recs} == {"ZaloPay", "SpaceX"})
for rec in recs:
    lab, acc = rec["account_label"], rec["account_no"]
    rows = rec["payload"]["positions"]
    live = mk(DNSEBroker, {"positions": rows}).get_positions()
    jl = ph_mod.aggregate_position_rows(rows, acc)
    check(f"R1 {lab}: live == jsonl (qty & sellable, {len(jl)} mã)",
          {k: (v["total"], v["sellable"]) for k, v in live.items()} ==
          {k: (v["qty"], v["sellable"]) for k, v in jl.items()},
          str({k for k in live if (live[k]["total"], live[k]["sellable"]) != (jl[k]["qty"], jl[k]["sellable"])}))
    for sym, qty in EXPECT0[lab].items():
        got = live.get(sym)
        # chỉ khẳng định các dòng tq=0 hoàn toàn: sellable phải = tổng tq thật của mã
        tq = sum(int(p.get("tradeQuantity") or 0) for p in rows
                 if p.get("symbol") == sym and p.get("status") != "CLOSED" and int(p.get("openQuantity") or 0) > 0)
        check(f"R2 {lab} {sym}: total {qty}, sellable == Σtq={tq}",
              got is not None and got["total"] == qty and got["sellable"] == tq, str(got))
        if tq == 0:
            check(f"R3 {lab} {sym}: tq=0 -> sellable 0", got["sellable"] == 0)
    # mọi mã: sellable == Σ tradeQuantity
    bad = {s: v for s, v in live.items()
           if v["sellable"] != sum(int(p.get("tradeQuantity") or 0) for p in rows
                                   if p.get("symbol") == s and p.get("status") != "CLOSED"
                                   and int(p.get("openQuantity") or 0) > 0)}
    check(f"R4 {lab}: mọi mã sellable == Σ tradeQuantity", not bad, str(bad))
r_ = {r["account_label"]: mk(DNSEBroker, {"positions": r["payload"]["positions"]}).get_positions() for r in recs}
check("R5 hai account cho kết quả KHÁC nhau (§12)", r_["ZaloPay"] != r_["SpaceX"])

print()
print("FAIL: " + ", ".join(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
