#!/usr/bin/env python3
"""A — rà từng dòng nav_history: (1) dòng nav_is_estimate=True: dựng lại mtm bằng marketPrice của
CHÍNH bản ghi positions broker đã dùng (nguồn giá thứ hai, độc lập BQ Price) + đọc lại
cash/debt/egg từ bản ghi balances đã dùng; (2) mọi dòng: lần chụp so với giờ đóng cửa phiên của
chính nó / phiên kế; (3) lần chụp so với cú khớp cuối trong ngày.
CHỈ ĐỌC. Dùng: A_review_rows.py <sandbox>"""
import csv, datetime, json, os, re, sys
S = sys.argv[1]
ED = os.path.join(S, "data", "execution_logs")
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
CLOSE = datetime.time(14, 45)
sys.path.insert(0, S); sys.path.insert(0, os.path.join(S, "mike", "bin"))
from trading_bot.vn_market import is_holiday

def is_session(d):
    return d.weekday() < 5 and not is_holiday(d)

def next_session(d):
    d += datetime.timedelta(days=1)
    while not is_session(d):
        d += datetime.timedelta(days=1)
    return d

def raw(date):
    p = os.path.join(ED, f"dnse_raw_{date}.jsonl")
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def last_fill(acct, date):
    p = os.path.join(ED, f"exec_{acct}_{date}_journal.csv")
    ts = ""
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            if r.get("event") == "FILL" and r.get("ts", "") > ts:
                ts = r["ts"]
    return ts

for acct, no in ACC.items():
    rows = list(csv.DictReader(open(os.path.join(ED, f"nav_history_{acct}.csv"))))
    print(f"\n===== {acct}: {len(rows)} dòng, {sum(r['nav_is_estimate']=='True' for r in rows)} dòng nav_is_estimate=True")
    print("-- (1) dòng ước tính: mtm theo BQ Price (đã ghi) so với mtm theo marketPrice broker cùng bản ghi positions")
    for r in rows:
        if r["nav_is_estimate"] != "True":
            continue
        m = re.search(r"positions@(\S+) balances@(\S+)", r["nav_source"])
        pts, bts = m.group(1), m.group(2)
        recs = raw(r["date"])
        pos = [x for x in recs if x.get("kind") == "positions" and x.get("account_no") == no and x.get("ts") == pts]
        bal = [x for x in recs if x.get("kind") == "balances" and x.get("account_no") == no and x.get("ts") == bts]
        n_bal_after = sum(1 for x in recs if x.get("kind") == "balances" and x.get("account_no") == no
                          and x.get("ts", "")[11:19] >= "14:45:00")
        nav, mtm = float(r["nav"]), float(r["mtm_stock"])
        if not pos or not bal:
            print(f"  {r['date']}: KHÔNG tìm lại được bản ghi nguồn (positions {len(pos)}, balances {len(bal)})")
            continue
        mtm_b, worst = 0.0, []
        for p in pos[-1]["payload"]["positions"]:
            q = float(p.get("openQuantity") or 0)
            if q > 0:
                mtm_b += q * float(p.get("marketPrice") or 0)
        st = bal[-1]["payload"]["stock"]
        egg = float((bal[-1]["payload"].get("egg") or {}).get("totalValue") or 0)
        cash_ok = abs(st["totalCash"] - float(r["cash"]) - float(r["cum_dividend_excl"] or 0)) < 1
        debt_ok = abs(st["totalDebt"] - float(r["margin_debt"])) < 1
        egg_ok = abs(egg - float(r["egg_assets"] or 0)) < 1
        d = mtm - mtm_b
        print(f"  {r['date']} chụp {bts[11:19]} | pos {pts[11:19]} | balances sau 14:45: {n_bal_after} bản | "
              f"mtm BQ {mtm:,.0f} vs broker {mtm_b:,.0f} lệch {d:+,.0f} ({d/nav*100:+.4f}% NAV) | "
              f"cash {'=' if cash_ok else 'KHÁC'} debt {'=' if debt_ok else 'KHÁC'} egg {'=' if egg_ok else 'KHÁC'}"
              f" | cú khớp cuối {last_fill(acct, r['date'])[11:19] or '—'}")
    print("-- (2) lần chụp so với giờ đóng cửa")
    for r in rows:
        d = datetime.date.fromisoformat(r["date"])
        bt = datetime.datetime.fromisoformat(r["balance_ts"][:19])
        tags = []
        if is_session(d) and bt < datetime.datetime.combine(d, CLOSE):
            tags.append("CHỤP TRƯỚC giờ đóng cửa phiên của chính nó")
        if bt >= datetime.datetime.combine(next_session(d), CLOSE):
            tags.append("K3: chụp SAU khi phiên kế đã đóng cửa")
        if bt.date() != d and not tags:
            tags.append(f"chụp ngày {bt.date()} {bt.time()} (trước giờ đóng cửa phiên kế — hợp lệ)")
        lf = last_fill(acct, r["date"])
        if lf and r["balance_ts"][:19] <= lf:
            tags.append(f"số dư CŨ HƠN cú khớp cuối {lf[11:19]}")
        if not is_session(d):
            tags.append("ngày KHÔNG có phiên")
        if tags:
            print(f"  {r['date']} balance_ts {r['balance_ts'][:19]}: " + "; ".join(tags))
    print("-- (3) phiên THIẾU dòng")
    have = {r["date"] for r in rows}
    d = datetime.date.fromisoformat(rows[0]["date"])
    end = datetime.date.fromisoformat(rows[-1]["date"])
    while d <= end:
        if is_session(d) and d.isoformat() not in have:
            recs = raw(d.isoformat())
            nb = [x["ts"][11:19] for x in recs if x.get("kind") == "balances" and x.get("account_no") == no]
            print(f"  {d}: thiếu dòng; dnse_raw có {len(nb)} bản ghi balances" + (f" ({nb[0]} … {nb[-1]})" if nb else ""))
        d += datetime.timedelta(days=1)
