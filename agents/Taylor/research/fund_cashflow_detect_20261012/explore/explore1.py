#!/usr/bin/env python3
"""Khảo sát (CHỈ ĐỌC): phần dư đẳng thức tiền theo ngày, 2 cách đo tiền khớp lệnh."""
import csv, glob, json, os, sys, collections
EX = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}

def load_raw():
    recs = collections.defaultdict(list)   # date -> recs
    for p in sorted(glob.glob(f"{EX}/dnse_raw_*.jsonl")):
        d = os.path.basename(p)[9:19]
        for line in open(p, encoding="utf-8"):
            try: r = json.loads(line)
            except Exception: continue
            if r.get("kind") in ("balances", "positions", "orders", "place_order"):
                recs[d].append(r)
    return recs

RAW = load_raw()

def is_acct(r, label, no):
    a = r.get("account_no")
    if a is None:
        # bản ghi cũ không tag: chỉ SpaceX tồn tại trước 2026-07-06
        if r.get("kind") == "positions":
            ps = (r.get("payload") or {}).get("positions") or []
            return bool(ps) and ps[0].get("accountNo") == no or (not ps and label == "SpaceX")
        return label == "SpaceX"
    return a == no

def rec_at(label, no, kind, ts):
    """bản ghi `kind` mới nhất có ts <= ts (cùng file ngày của ts)."""
    d = ts[:10]; best = None
    for r in RAW.get(d, []):
        if r.get("kind") == kind and is_acct(r, label, no) and r["ts"] <= ts:
            best = r
    return best

def pos_cum(rec):
    tot = 0.0; n = 0
    for p in (rec.get("payload") or {}).get("positions") or []:
        tot += (p.get("closedQuantity") or 0) * (p.get("averageClosePrice") or 0) \
             - (p.get("accumulateQuantity") or 0) * (p.get("costPrice") or 0)
        n += 1
    return tot, n

def fills_cash(label, no, d0, d1):
    """Σ bán − Σ mua của các order có transDate/ngày file trong (d0, d1]."""
    net = 0.0; buy = sell = 0.0
    for d in sorted(RAW):
        if not (d0 < d <= d1): continue
        latest = {}
        for r in RAW[d]:
            os_ = []
            if r.get("kind") == "orders": os_ = (r.get("payload") or {}).get("orders") or []
            elif r.get("kind") == "place_order":
                x = (r.get("payload") or {}).get("resp") or {}
                if x.get("id") is not None: os_ = [x]
            for o in os_:
                if o.get("accountNo") not in (None, no): continue
                if o.get("accountNo") is None and not is_acct(r, label, no): continue
                latest[o["id"]] = o
        for o in latest.values():
            fq = o.get("fillQuantity") or 0
            if fq <= 0: continue
            v = fq * float(o.get("averagePrice") or o.get("price") or 0)
            if str(o.get("side", "")).upper().startswith("NS"): sell += v
            else: buy += v
    return sell - buy, buy, sell

for label, no in ACC.items():
    rows = list(csv.DictReader(open(f"{EX}/nav_history_{label}.csv")))
    print(f"== {label}")
    print("date   dC         posTrade   fillTrade  buy        sell       dDivRecv  res_pos    res_fill   %nav_fill  note")
    prev = None
    for r in rows:
        ts = r["balance_ts"]; nav = float(r["nav"]); C = nav - float(r["mtm_stock"])
        b = rec_at(label, no, "balances", ts); p = rec_at(label, no, "positions", ts)
        st = ((b or {}).get("payload") or {}).get("stock") or {}
        egg = (((b or {}).get("payload") or {}).get("egg") or {}).get("totalValue") or 0
        Craw = (st.get("totalCash") or 0) - (st.get("totalDebt") or 0) + egg if b else None
        pc, npos = pos_cum(p) if p else (None, 0)
        cur = dict(date=r["date"], C=C, pc=pc, div=st.get("cashDividendReceiving") or 0, nav=nav,
                   bts=(b or {}).get("ts"), pts=(p or {}).get("ts"), Craw=Craw)
        if prev:
            dC = C - prev["C"]
            ft, buy, sell = fills_cash(label, no, prev["date"], r["date"])
            pt = (pc - prev["pc"]) if (pc is not None and prev["pc"] is not None) else None
            dd = cur["div"] - prev["div"]
            note = ""
            if Craw is None: note += " noBal"
            elif abs(Craw - C) > 1: note += f" C-Craw={C-Craw:,.0f}"
            if cur["bts"] and cur["bts"] != ts: note += f" bts={cur['bts'][5:16]}"
            rp = dC - pt if pt is not None else float("nan")
            rf = dC - ft
            print(f"{r['date'][5:]} {dC:>12,.0f} {(float('nan') if pt is None else pt):>12,.0f} {ft:>12,.0f} {buy:>12,.0f} {sell:>12,.0f} {dd:>10,.0f} {rp:>12,.0f} {rf:>12,.0f} {rf/prev['nav']*100:>8.3f}{note}")
        prev = cur
