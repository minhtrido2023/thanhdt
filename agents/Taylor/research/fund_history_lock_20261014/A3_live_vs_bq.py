#!/usr/bin/env python3
"""A3 — với MỌI dòng nav_history: mtm sổ so với (a) KL broker lúc chụp × BQ Price ngày đó,
(b) KL × marketPrice broker lúc chụp, (c) KL × marketPrice broker ở bản ghi muộn nhất trước giờ mở
cửa phiên kế ("giá chốt broker"). Cho biết dòng LIVE định giá theo quy ước nào ⇒ dòng ước tính
(BQ Price) có cùng quy ước không. CHỈ ĐỌC. Dùng: A3_live_vs_bq.py <sandbox> <bq_price.csv>"""
import csv, datetime, glob, json, os, sys, collections
S, PX = sys.argv[1], sys.argv[2]
ED = os.path.join(S, "data", "execution_logs")
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
sys.path.insert(0, S)
from trading_bot.vn_market import is_holiday
px = {(r["ticker"], r["time"]): float(r["Price"]) for r in csv.DictReader(open(PX))}
def next_session(d):
    d = datetime.date.fromisoformat(d) + datetime.timedelta(days=1)
    while d.weekday() >= 5 or is_holiday(d):
        d += datetime.timedelta(days=1)
    return d.isoformat()
def load(no):
    out = []
    for p in sorted(glob.glob(os.path.join(ED, "dnse_raw_*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            if '"positions"' not in line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("kind") == "positions" and r.get("account_no") in (no, None):
                out.append((r["ts"], r["payload"].get("positions") or []))
    return sorted(out, key=lambda x: x[0])
def agg(ps):
    o = {}
    for p in ps:
        q = float(p.get("openQuantity") or 0)
        if q > 0:
            e = o.setdefault(p["symbol"], [0.0, p.get("marketPrice")]); e[0] += q
    return o
per_t = collections.defaultdict(lambda: [0, 0, 0.0])
for acct, no in ACC.items():
    allp = load(no)
    rows = list(csv.DictReader(open(os.path.join(ED, f"nav_history_{acct}.csv"))))
    print(f"\n== {acct}: sổ − (a) BQ Price | sổ − (b) broker lúc chụp | sổ − (c) giá chốt broker (sáng phiên kế); đơn vị đ và % NAV")
    for r in rows:
        d, bts, nav, mtm = r["date"], r["balance_ts"][:19], float(r["nav"]), float(r["mtm_stock"])
        near = [(ts, ps) for ts, ps in allp if ts[:10] >= d and abs((datetime.datetime.fromisoformat(ts[:19]) - datetime.datetime.fromisoformat(bts)).total_seconds()) <= 600]
        if not near:
            print(f"  {d} {'EST ' if r['nav_is_estimate']=='True' else 'live'} không có positions ±10' quanh {bts[11:]}")
            continue
        cur = agg(min(near, key=lambda x: abs((datetime.datetime.fromisoformat(x[0][:19]) - datetime.datetime.fromisoformat(bts)).total_seconds()))[1])
        nxt = next_session(d) + "T09:00:00"
        later = [(ts, ps) for ts, ps in allp if bts < ts < nxt]
        third = agg(later[-1][1]) if later else {}
        a = sum(q * px.get((t, d), float("nan")) for t, (q, _) in cur.items())
        b = sum(q * float(mp or 0) for t, (q, mp) in cur.items())
        same_q = third and all(t in third and third[t][0] == q for t, (q, _) in cur.items())
        c = sum(q * float(third[t][1] or 0) for t, (q, _) in cur.items()) if same_q else float("nan")
        flag = ""
        if r["nav_is_estimate"] != "True":
            for t, (q, mp) in cur.items():
                p = px.get((t, d))
                if p is not None and mp is not None:
                    per_t[t][0] += 1
                    if abs(p - float(mp)) >= 0.5:
                        per_t[t][1] += 1; per_t[t][2] += abs(q * (p - float(mp)))
        print(f"  {d} {'EST ' if r['nav_is_estimate']=='True' else 'live'} sổ−BQ {mtm-a:+13,.0f} ({(mtm-a)/nav*100:+.4f}%) | sổ−broker {mtm-b:+13,.0f} ({(mtm-b)/nav*100:+.4f}%) | sổ−chốt {mtm-c:+13,.0f} ({(mtm-c)/nav*100:+.4f}%)")
print("\n== dòng LIVE: mã nào BQ Price ≠ marketPrice broker lúc chụp (số ngày lệch / số ngày giữ, tổng |lệch| đ)")
for t, (n, k, v) in sorted(per_t.items(), key=lambda x: -x[1][2]):
    if k:
        print(f"  {t}: {k}/{n} ngày, {v:,.0f} đ")
