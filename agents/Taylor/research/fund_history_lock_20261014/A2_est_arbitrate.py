#!/usr/bin/env python3
"""A2 — phân xử từng MÃ của 14 dòng ước tính: giá BQ `Price` (đã dùng ghi sổ) vs marketPrice của
broker lúc chụp vs marketPrice của broker ở bản ghi positions ĐẦU TIÊN sau đó nhưng trước giờ mở
cửa phiên kế (nguồn thứ ba: lúc đó feed đã kịp cập nhật giá đóng cửa). CHỈ ĐỌC.
Dùng: A2_est_arbitrate.py <sandbox> <bq_price.csv>"""
import csv, datetime, glob, json, os, re, sys
S, PX = sys.argv[1], sys.argv[2]
ED = os.path.join(S, "data", "execution_logs")
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
sys.path.insert(0, S)
from trading_bot.vn_market import is_holiday
px = {}
for r in csv.DictReader(open(PX)):
    px[(r["ticker"], r["time"])] = float(r["Price"])
days = sorted({d for _, d in px})
def prev_day(d):
    i = days.index(d); return days[i - 1]
def next_session(d):
    d = datetime.date.fromisoformat(d) + datetime.timedelta(days=1)
    while d.weekday() >= 5 or is_holiday(d):
        d += datetime.timedelta(days=1)
    return d.isoformat()
_cache = {}
def raw_positions(no):
    if no not in _cache:
        out = []
        for p in sorted(glob.glob(os.path.join(ED, "dnse_raw_*.jsonl"))):
            for line in open(p, encoding="utf-8"):
                if '"positions"' not in line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("kind") == "positions" and r.get("account_no") == no:
                    out.append((r["ts"], r["payload"].get("positions") or []))
        _cache[no] = sorted(out, key=lambda x: x[0])
    return _cache[no]
def agg(ps):
    o = {}
    for p in ps:
        q = float(p.get("openQuantity") or 0)
        if q > 0:
            e = o.setdefault(p["symbol"], [0.0, p.get("marketPrice")])
            e[0] += q
    return o
tot = {}
for acct, no in ACC.items():
    rows = list(csv.DictReader(open(os.path.join(ED, f"nav_history_{acct}.csv"))))
    for r in rows:
        if r["nav_is_estimate"] != "True":
            continue
        d = r["date"]; nav = float(r["nav"])
        pts = re.search(r"positions@(\S+)", r["nav_source"]).group(1)
        allp = raw_positions(no)
        cur = agg(next(ps for ts, ps in allp if ts == pts))
        nxt_open = next_session(d) + "T09:00:00"
        later = [(ts, ps) for ts, ps in allp if pts < ts < nxt_open]
        # bản ghi muộn nhất trước giờ mở cửa phiên kế = feed có nhiều thời gian nhất để cập nhật
        third = agg(later[-1][1]) if later else {}
        third_ts = later[-1][0] if later else None
        mtm_bq = sum(q * px.get((t, d), float("nan")) for t, (q, _) in cur.items())
        mtm_3 = sum(q * (third[t][1] if t in third and third[t][0] == q else float("nan")) for t, (q, _) in cur.items()) if third else float("nan")
        line = []
        n_stale = n_other = 0; v_stale = v_other = 0.0
        for t, (q, mp) in sorted(cur.items()):
            p = px.get((t, d)); pp = px.get((t, prev_day(d)))
            if p is None or mp is None or abs(p - mp) < 0.5:
                continue
            p3 = third.get(t, [None, None])[1]
            kind = "broker trễ (=giá phiên trước)" if pp is not None and abs(mp - pp) < 0.5 else "KHÁC"
            ok3 = ("nguồn 3 = BQ" if p3 is not None and abs(p3 - p) < 0.5 else
                   "nguồn 3 = broker cũ" if p3 is not None and abs(p3 - mp) < 0.5 else f"nguồn 3 = {p3}")
            if kind.startswith("broker"):
                n_stale += 1; v_stale += q * (p - mp)
            else:
                n_other += 1; v_other += q * (p - mp)
            line.append(f"      {t}: KL {q:,.0f} BQ {p:,.0f} broker {mp:,.0f} phiên trước {pp:,.0f} ⇒ {kind}; {ok3} ({(third_ts or '')[5:16]}); {q*(p-mp):+,.0f} đ")
        print(f"{acct} {d}: mtm sổ {float(r['mtm_stock']):,.0f} | tính lại BQ {mtm_bq:,.0f} (lệch sổ {float(r['mtm_stock'])-mtm_bq:+,.0f}) | "
              f"nguồn 3 @{(third_ts or '—')[5:16]} {mtm_3:,.0f} (sổ − nguồn 3 = {float(r['mtm_stock'])-mtm_3:+,.0f} = {(float(r['mtm_stock'])-mtm_3)/nav*100:+.4f}% NAV) | "
              f"mã lệch: {n_stale} do broker trễ ({v_stale:+,.0f}), {n_other} KHÁC ({v_other:+,.0f} = {v_other/nav*100:+.4f}% NAV)")
        print("\n".join(line))
