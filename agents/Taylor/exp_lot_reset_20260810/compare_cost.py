#!/usr/bin/env python3
"""So sanh gia von OLD (buy_val/buy_qty) vs NEW (running weighted-avg, reset khi ve 0)
vs costPrice cua broker, cho ca 2 account."""
import json, glob, os, sys
from collections import defaultdict

WC = "/home/trido/thanhdt/WorkingClaude"
EXEC = os.path.join(WC, "data", "execution_logs")
sys.path.insert(0, os.path.join(WC, "mike", "bin"))
from corp_actions import load_corp_actions
import verify_account_snapshot as VAS

ACCTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}


def fill_events(account_no, date):
    """(ts, ticker, side, qty, price) sorted."""
    path = os.path.join(EXEC, f"dnse_raw_{date}.jsonl")
    latest = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            orders = []
            if rec.get("kind") == "orders":
                orders = rec.get("payload", {}).get("orders") or []
            elif rec.get("kind") == "place_order":
                r = rec.get("payload", {}).get("resp") or {}
                if r.get("id") is not None:
                    orders = [r]
            for o in orders:
                oid = o.get("id")
                if oid is None:
                    continue
                if account_no and o.get("accountNo") not in (None, account_no):
                    continue
                latest[oid] = o
    ev = []
    for oid, o in latest.items():
        fq = o.get("fillQuantity") or 0
        if fq <= 0:
            continue
        ts = o.get("modifiedDate") or o.get("createdDate") or ""
        side = str(o.get("side") or "").upper()
        ev.append((ts, oid, o.get("symbol"), side,
                   float(fq), float(o.get("averagePrice") or o.get("price") or 0)))
    ev.sort(key=lambda e: (e[0], e[1]))
    return ev


def broker_cost(account_no, date):
    """costPrice moi ma tu ban ghi positions moi nhat cua account."""
    path = os.path.join(EXEC, f"dnse_raw_{date}.jsonl")
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("kind") != "positions":
                continue
            if str(rec.get("accountNo") or rec.get("account_no") or "") not in ("", str(account_no)):
                continue
            pl = rec.get("payload", {})
            items = pl.get("positions") or pl.get("data") or (pl if isinstance(pl, list) else [])
            if isinstance(items, dict):
                items = items.get("positions") or []
            for p in items:
                sym = p.get("symbol") or p.get("ticker")
                if not sym:
                    continue
                out[sym] = {k: p.get(k) for k in
                            ("costPrice", "quantity", "openQuantity", "availableQuantity",
                             "breakEvenPrice", "marketPrice")}
    return out


def main(asof):
    actions = load_corp_actions()
    dates = sorted(os.path.basename(p)[9:19]
                   for p in glob.glob(os.path.join(EXEC, "dnse_raw_*.jsonl")))
    dates = [d for d in dates if d <= asof]
    for label, acct in ACCTS.items():
        old = defaultdict(lambda: [0.0, 0.0, 0.0])   # qty, buy_qty, buy_val
        run = defaultdict(lambda: [0.0, 0.0])        # qty, basis
        resets = defaultdict(int)
        for d in dates:
            for ts, oid, sym, side, fq, px in fill_events(acct, d):
                m = VAS.corp_action_multiplier(sym, d, asof, actions)
                q = fq * m
                if side.startswith("NS") or side == "SELL":
                    old[sym][0] -= q
                    rq, basis = run[sym]
                    if rq > 0:
                        basis -= basis * min(q, rq) / rq
                    rq -= q
                    if rq <= 1e-9:
                        rq, basis = (rq if rq < -1e-9 else 0.0), 0.0
                        resets[sym] += 1
                    run[sym] = [rq, basis]
                else:
                    old[sym][0] += q
                    old[sym][1] += q
                    old[sym][2] += fq * px
                    run[sym][0] += q
                    run[sym][1] += fq * px
        bc = broker_cost(acct, asof)
        print(f"\n===== {label} (asof {asof}, {len(dates)} ngay fill) =====")
        print(f"{'MA':6s} {'QTY':>7s} {'OLD':>11s} {'NEW':>11s} {'DIFF':>9s} "
              f"{'BROKER':>11s} {'NEW-BROKER':>11s} reset")
        for sym in sorted(old):
            qty = old[sym][0]
            if qty <= 0:
                continue
            o = old[sym][2] / old[sym][1] if old[sym][1] else 0
            n = run[sym][1] / run[sym][0] if run[sym][0] else 0
            b = bc.get(sym, {}).get("costPrice")
            bs = f"{b:11,.2f}" if b is not None else f"{'n/a':>11s}"
            nb = f"{n - b:11,.2f}" if b is not None else f"{'':>11s}"
            print(f"{sym:6s} {qty:7.0f} {o:11,.2f} {n:11,.2f} {n-o:9,.2f} {bs} {nb} "
                  f"{resets[sym]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-08-07")
