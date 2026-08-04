# -*- coding: utf-8 -*-
"""Truy nguoc so lo (lot ledger) theo book tu journal thuc thi + plan file.

CHI DOC. Khong sua production. Output = du lieu tho de Taylor doc va phan dinh tay.
Bay so 1 (F2): qty trong dong FILL la TICH LUY theo child_oid -> phai lay delta.
"""
import csv, glob, json, os, sys, collections, datetime as dt

WD = "/home/trido/thanhdt/WorkingClaude"
EXEC = os.path.join(WD, "data/execution_logs")
PLANS = os.path.join(WD, "data/trade_plans")


def plan_orders(label, date):
    """id -> dict(book, play_type, ticker, side, qty). Doc plan JSON tho (khong qua load_plan)."""
    p = os.path.join(PLANS, f"plan_{label}_{date}.json")
    if not os.path.exists(p):
        return {}, None
    d = json.load(open(p, encoding="utf-8"))
    out = {}
    for o in d.get("orders", []):
        oid = o.get("id") or "%s-%s-%02d" % (str(o.get("side", "?")).upper(),
                                            o.get("ticker", "?"), int(o.get("priority") or 0))
        out[oid] = {"book": o.get("book") or "", "play_type": o.get("play_type") or "",
                    "ticker": o.get("ticker"), "side": o.get("side"), "qty": o.get("qty"),
                    "strategy": d.get("strategy", ""), "note": o.get("note", "")}
    return out, d


def journal_fills(label, date):
    """Tra ve list dong FILL da quy ve DELTA theo child_oid, theo thu tu ts."""
    p = os.path.join(EXEC, f"exec_{label}_{date}_journal.csv")
    if not os.path.exists(p):
        return []
    seen = {}          # child_oid -> qty tich luy da ghi nhan
    out = []
    with open(p, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("event") != "FILL":
                continue
            oid = row.get("child_oid") or ""
            try:
                q = float(row.get("qty") or 0)
            except ValueError:
                continue
            prev = seen.get(oid, 0.0)
            delta = q - prev
            seen[oid] = max(prev, q)
            if delta <= 0:
                continue
            out.append({"ts": row["ts"], "parent_id": row["parent_id"], "ticker": row["ticker"],
                        "side": row["side"], "child_oid": oid, "delta": int(delta),
                        "price": float(row["price"] or 0),
                        "book_col": row.get("book", "")})   # 10-cot cu -> khong co
    return out


def dates_for(label):
    ds = set()
    for p in glob.glob(os.path.join(EXEC, f"exec_{label}_*_journal.csv")):
        b = os.path.basename(p)
        d = b[len(f"exec_{label}_"):-len("_journal.csv")]
        if len(d) == 10 and d[:2] == "20":
            ds.add(d)
    return sorted(ds)


def main():
    for label in ("SpaceX", "ZaloPay"):
        print("=" * 78)
        print("ACCOUNT", label)
        for date in dates_for(label):
            po, plan = plan_orders(label, date)
            fills = journal_fills(label, date)
            if not fills:
                print(f"  {date}: journal khong co FILL nao (plan orders={len(po)})")
                continue
            agg = collections.defaultdict(lambda: {"qty": 0, "val": 0.0})
            for f in fills:
                k = (f["parent_id"], f["ticker"], f["side"])
                agg[k]["qty"] += f["delta"]
                agg[k]["val"] += f["delta"] * f["price"]
            print(f"  {date}: strategy={plan.get('strategy') if plan else 'NO_PLAN'}")
            for (pid, tk, side), v in sorted(agg.items()):
                meta = po.get(pid, {})
                book = meta.get("book", "?MISSING_ORDER?")
                pt = meta.get("play_type", "")
                vwap = v["val"] / v["qty"] if v["qty"] else 0
                print("     %-18s %-4s %-5s qty=%6d vwap=%9.1f book=%-20s play=%s"
                      % (pid, side, tk, v["qty"], vwap, book or "(empty)", pt))


if __name__ == "__main__":
    main()
