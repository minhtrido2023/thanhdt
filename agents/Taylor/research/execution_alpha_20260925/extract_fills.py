#!/usr/bin/env python3
"""Extract REAL fills from data/execution_logs/dnse_raw_*.jsonl.

Source of truth per coding_guidelines §6: broker's own order record
(averagePrice / fillQuantity), never a downstream estimate field.

§12: accountNo filter is the FIRST thing done to every record.

Output: fills.csv — one row per (trans_date, account, order_id).
"""
import json, glob, os, csv, sys
from collections import defaultdict

LOGDIR = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"
ACCOUNTS = {"0002023347": "SpaceX", "0001743768": "ZaloPay"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fills.csv")

# key = (account_no, order_id) -> best (most-filled / latest) snapshot
best = {}
# first time we ever SAW the order in any poll, and the earliest placement evidence
first_seen = {}
place_req = {}   # (acct, oid) -> {"ts":..., "req":[sym,qty,side,price,type]}
cancels = {}

def note_order(acct, o, ts, kind):
    oid = o.get("id")
    if oid is None:
        return
    k = (acct, str(oid))
    prev = best.get(k)
    fq = o.get("fillQuantity") or 0
    # keep the record with the largest fillQuantity; tie -> latest modifiedDate
    if prev is None or (fq, o.get("modifiedDate") or "") > (prev.get("fillQuantity") or 0, prev.get("modifiedDate") or ""):
        best[k] = dict(o)
    if k not in first_seen:
        first_seen[k] = ts

n_lines = 0
n_skipped_acct = 0
for f in sorted(glob.glob(os.path.join(LOGDIR, "dnse_raw_*.jsonl"))):
    for line in open(f):
        line = line.strip()
        if not line:
            continue
        n_lines += 1
        try:
            rec = json.loads(line)
        except Exception:
            continue
        kind = rec.get("kind")
        ts = rec.get("ts")
        if kind == "orders":
            # §12: account filter FIRST — the poll is per-account, but each
            # order ALSO carries accountNo; require both to agree.
            acct_rec = str(rec.get("account_no") or "")
            for o in rec["payload"].get("orders") or []:
                acct = str(o.get("accountNo") or "")
                if acct not in ACCOUNTS:
                    n_skipped_acct += 1
                    continue
                if acct_rec and acct_rec != acct:
                    n_skipped_acct += 1
                    continue
                note_order(acct, o, ts, kind)
        elif kind in ("place_order", "cancel_order"):
            resp = (rec.get("payload") or {}).get("resp") or {}
            acct = str(resp.get("accountNo") or "")
            if acct not in ACCOUNTS:
                n_skipped_acct += 1
                continue
            note_order(acct, resp, ts, kind)
            if kind == "place_order":
                place_req[(acct, str(resp.get("id")))] = {
                    "place_ts": ts,
                    "req": (rec.get("payload") or {}).get("req"),
                }
            else:
                cancels[(acct, str(resp.get("id")))] = ts

rows = []
for (acct, oid), o in best.items():
    fq = o.get("fillQuantity") or 0
    if fq <= 0:
        continue
    ap = o.get("averagePrice") or 0
    if ap <= 0:
        continue
    pr = place_req.get((acct, oid), {})
    rows.append({
        "trans_date": o.get("transDate"),
        "account": ACCOUNTS[acct],
        "account_no": acct,
        "order_id": oid,
        "ticker": o.get("symbol"),
        "side": o.get("side"),              # NB=buy, NS=sell
        "order_type": o.get("orderType"),
        "limit_price": o.get("price"),
        "avg_fill_price": ap,
        "qty_ordered": o.get("quantity"),
        "fill_qty": fq,
        "cancel_qty": o.get("canceledQuantity") or 0,
        "leave_qty": o.get("leaveQuantity") or 0,
        "status": o.get("orderStatus"),
        "created_utc": o.get("createdDate"),
        "modified_utc": o.get("modifiedDate"),
        "first_seen_local": first_seen.get((acct, oid)),
        "place_ts_local": pr.get("place_ts"),
        "notional_vnd": ap * fq,
    })

rows.sort(key=lambda r: (r["trans_date"] or "", r["account"], r["ticker"] or "", r["order_id"]))
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"lines read      : {n_lines}")
print(f"records skipped (account filter): {n_skipped_acct}")
print(f"distinct orders : {len(best)}")
print(f"FILLED orders   : {len(rows)}  -> {OUT}")
by = defaultdict(int)
for r in rows:
    by[r["account"]] += 1
print("by account      :", dict(by))
print("date range      :", min(r['trans_date'] for r in rows), "->", max(r['trans_date'] for r in rows))
print("total notional  : {:,.0f} VND".format(sum(r["notional_vnd"] for r in rows)))
