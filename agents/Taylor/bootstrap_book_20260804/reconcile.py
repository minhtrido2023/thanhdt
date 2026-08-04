# -*- coding: utf-8 -*-
"""Doi soat: so lo dung tu journal+plan  vs  openQuantity cua broker (08-03 EOD).
CHI DOC. In ra bang lech de Taylor phan dinh tay."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ledger import plan_orders, journal_fills, dates_for, EXEC

ASOF_RAW = os.path.join(EXEC, "dnse_raw_2026-08-03.jsonl")
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}


def broker_positions(account_no):
    last = None
    with open(ASOF_RAW, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            # §12: loc account NGAY dong dau, truoc moi phep tinh
            if r.get("account_no") != account_no:
                continue
            if r.get("kind") == "positions":
                last = r
    return {p["symbol"]: p for p in last["payload"]["positions"]}, last["ts"]


def ledger(label):
    """[{date, ticker, side, qty, vwap, book, play_type, parent_id, plan_strategy}] theo thu tu ngay."""
    out = []
    for date in dates_for(label):
        po, plan = plan_orders(label, date)
        agg = collections.defaultdict(lambda: {"qty": 0, "val": 0.0})
        for f in journal_fills(label, date):
            k = (f["parent_id"], f["ticker"], f["side"])
            agg[k]["qty"] += f["delta"]
            agg[k]["val"] += f["delta"] * f["price"]
        for (pid, tk, side), v in sorted(agg.items()):
            m = po.get(pid, {})
            out.append({"date": date, "ticker": tk, "side": side, "qty": v["qty"],
                        "vwap": round(v["val"] / v["qty"], 2) if v["qty"] else 0,
                        "book": m.get("book", ""), "play_type": m.get("play_type", ""),
                        "parent_id": pid, "plan_strategy": (plan or {}).get("strategy", ""),
                        "in_plan": pid in po})
    return out


for label, acc_no in ACC.items():
    pos, ts = broker_positions(acc_no)
    led = ledger(label)
    net = collections.Counter()
    for e in led:
        net[e["ticker"]] += e["qty"] if e["side"] == "buy" else -e["qty"]
    print("=" * 78)
    print(f"{label} ({acc_no})  broker snapshot ts={ts}")
    print("%-6s %10s %10s %10s   %s" % ("ticker", "broker_open", "journal_net", "diff", "ghi chu"))
    tickers = sorted(set(pos) | {t for t in net if net[t] != 0})
    for t in tickers:
        b = pos[t]["openQuantity"] if t in pos else 0
        j = net.get(t, 0)
        d = b - j
        note = ""
        if t not in pos:
            note = "journal thua (da ban het o broker)"
        elif j == 0 and b > 0:
            note = "KHONG CO trong journal -> legacy/ngoai bot"
        elif d != 0:
            note = "LECH"
        print("%-6s %10d %10d %10d   %s" % (t, b, j, d, note))
