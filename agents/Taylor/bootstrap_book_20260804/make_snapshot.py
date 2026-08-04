# -*- coding: utf-8 -*-
"""Sinh bootstrap book snapshot (.json.proposed) tu so lo FIFO-theo-book.

CHI DOC production; chi GHI ra file duoi .json.proposed (dieu 13 coding_guidelines).
"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_ledger import plan_orders, journal_fills, dates_for, EXEC
from reconcile import broker_positions, ledger, ACC

WD = "/home/trido/thanhdt/WorkingClaude"
ASOF = "2026-08-03"          # phien giao dich cuoi cung co du lieu broker
DAY0 = "2026-08-04"          # ngay khoi tao (chua co fill nao)

# Chuan hoa ten book cua plan -> ten book canonical cua thiet ke muc F
BOOK_MAP = {
    "custom30V_parking": "PARK",
    "PARK": "PARK",
    "CAPIT": "CAPIT",
    "LAG": "LAG",
    "BAL": "BAL",
    "DISCRETIONARY_SPECIAL": "DISCRETIONARY_SPECIAL",
    "legacy_orphan": "LEGACY_ORPHAN",
}

# Lo mo dau (truoc khi bot quan ly) — tu snapshot broker dau tien cua account.
# SpaceX: khong co (account sach, bat dau 2026-07-01).
OPENING = {
    "SpaceX": [],
    "ZaloPay": [
        # symbol, qty, cost, created(broker), book_de_xuat, can_nguoi_xac_nhan
        ("DGC", 10000, 47775.0,  "2026-06-26", "EXCLUDED",      False),
        ("MSH",   200, 35000.0,  "2026-03-23", "LEGACY_ORPHAN", False),
        ("TCM",  2310, 21305.2,  "2026-03-23", "LEGACY_ORPHAN", False),
        ("TLG",   200, 49950.0,  "2026-06-23", "LEGACY_ORPHAN", False),
        ("VHC",  1800, 60188.9,  "2025-11-19", "LEGACY_ORPHAN", False),
        ("VIB",  9200, 15251.1,  "2026-03-10", "LEGACY_ORPHAN", False),
        ("VPB",  7500, 27886.7,  "2025-11-20", "PARK",          True),
    ],
}

# Ghi de book cho cac fill KHONG co truong `book` trong plan, nhung co bang chung van ban ro.
BOOK_OVERRIDE = {
    ("SpaceX", "2026-07-15", "BUY-LPB-01"):  ("PARK", "plan_SpaceX_2026-07-15.json: strategy=v24_custom30v, "
        "allocation_strategy.rule='neutral_parking v2.1 + basket_drift_swap', buy_note='Mua LPB 900 co de thay the HPG "
        "(basket swap, weight 5.22% trong CUSTOM30V_8L)'; allocator_w_lag.actionable=false, 'BAL/LAG deu co 0 active deals'"),
    ("SpaceX", "2026-07-15", "SELL-HPG-00"): ("PARK", "cung plan: 'HPG OUT khoi CUSTOM30V_8L effective 07-13' — ban chan PARK"),
}


class Lots:
    def __init__(self):
        self.by = collections.defaultdict(list)   # (ticker, book) -> [lot]
        self.warn = []

    def buy(self, ticker, book, qty, price, date, ev):
        self.by[(ticker, book)].append({"qty": qty, "cost_price": price,
                                        "entry_date": date, "evidence": ev})

    def sell(self, ticker, book, qty, date, ev):
        q = qty
        pool = self.by[(ticker, book)]
        while q > 0 and pool:
            lot = pool[0]
            take = min(q, lot["qty"])
            lot["qty"] -= take
            q -= take
            if lot["qty"] == 0:
                pool.pop(0)
        if q > 0:
            self.warn.append(f"{date} {ticker}: ban {q} vuot so lo book={book} -> KHONG tu bu, ghi nhan lech")


def build(label):
    lots = Lots()
    for sym, qty, cost, created, book, _need in OPENING[label]:
        lots.buy(sym, book, qty, cost, created,
                 f"vi the mo dau truoc khi bot quan ly; broker snapshot dau tien cua account "
                 f"(dnse_raw_2026-07-06.jsonl, accountNo={ACC[label]}): openQuantity={qty}, costPrice={cost}, createdDate={created}")
    unresolved = []
    for e in ledger(label):
        key = (label, e["date"], e["parent_id"])
        book_raw, why = e["book"], ""
        if key in BOOK_OVERRIDE:
            book, why = BOOK_OVERRIDE[key]
        elif book_raw:
            book, why = BOOK_MAP.get(book_raw, book_raw), f"plan_{label}_{e['date']}.json order id={e['parent_id']} book='{book_raw}'"
        else:
            book, why = "UNRESOLVED", "khong co truong book trong plan va khong co bang chung van ban"
            unresolved.append(e)
        ev = (f"{e['date']} {e['side'].upper()} {e['qty']}@{e['vwap']:.0f} "
              f"(journal exec_{label}_{e['date']}_journal.csv, parent_id={e['parent_id']}); {why}")
        if e["side"] == "buy":
            lots.buy(e["ticker"], book, e["qty"], e["vwap"], e["date"], ev)
        else:
            lots.sell(e["ticker"], book, e["qty"], e["date"], ev)
    return lots, unresolved


def main():
    for label, acc_no in ACC.items():
        pos, ts = broker_positions(acc_no)
        lots, unresolved = build(label)
        recs, per_ticker = [], collections.Counter()
        for (ticker, book), pool in sorted(lots.by.items()):
            for lot in pool:
                if lot["qty"] <= 0:
                    continue
                recs.append({"ticker": ticker, "qty": lot["qty"], "book": book,
                             "entry_date": lot["entry_date"],
                             "cost_price_vnd": round(lot["cost_price"], 2),
                             "evidence": lot["evidence"]})
                per_ticker[ticker] += lot["qty"]
        # doi soat bat buoc (F4)
        recon, ok = [], True
        for t in sorted(set(pos) | set(per_ticker)):
            b = pos[t]["openQuantity"] if t in pos else 0
            l = per_ticker.get(t, 0)
            if b != l:
                ok = False
            recon.append({"ticker": t, "broker_openQuantity": b, "ledger_qty": l, "diff": b - l,
                          "broker_cost_price": pos[t]["costPrice"] if t in pos else None})
        print(f"[{label}] lots={len(recs)} reconcile_ok={ok} warn={lots.warn} unresolved={len(unresolved)}")
        for r in recon:
            if r["diff"]:
                print("   LECH:", r)
        json.dump({"_meta": {"label": label, "account_no": acc_no}, "positions": recs,
                   "reconcile": recon, "warnings": lots.warn}, open(
            f"/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/bootstrap_book_20260804/_raw_{label}.json", "w"),
            indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
