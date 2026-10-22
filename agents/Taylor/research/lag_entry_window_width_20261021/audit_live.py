#!/usr/bin/env python3
"""A — kiểm toán live cửa sổ entry LAG 2026-07-01..2026-10-21 (READ-ONLY).

Ứng viên = dòng book=LAG trong golive_v23_recommendations_*.csv. Fill thật = dnse_raw orders
(lọc accountNo trước mọi phép tính, §12), kiểm chéo email khớp lệnh broker nếu có file.
Ghi audit_live_rows.csv + in bảng tóm tắt.
"""
import csv, glob, json, os, re, sys, collections
import datetime as dt

WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
from trading_bot.vn_market import next_trading_day  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
LO, HI = dt.date(2026, 7, 1), dt.date(2026, 10, 21)
EL = f"{WC}/data/execution_logs"


def nth_session(d, n):
    for _ in range(n):
        d = next_trading_day(d)
    return d


# ---------- 1. ứng viên
cands = collections.defaultdict(lambda: {"votes": collections.Counter(), "rows": []})
for f in sorted(glob.glob(f"{WC}/deploy_golive_dt5g_v4/out/golive_v23_recommendations_2026-*.csv")):
    sd = dt.date.fromisoformat(os.path.basename(f)[27:37])
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if (r.get("book") or "").strip() != "LAG":
            continue
        st = (r.get("status") or "").strip()
        m = re.search(r"(\d{4}-\d{2}-\d{2})", st)
        mt = re.match(r"UPCOMING\s+T\+(\d+)", st)
        if m:
            e = dt.date.fromisoformat(m.group(1))
        elif mt:
            e = nth_session(sd, int(mt.group(1)))
        else:
            continue
        c = cands[r["ticker"]]
        c["votes"][e] += 1
        c["rows"].append((sd, st, r.get("weight_pct"), (r.get("due_diligence") or "")[:300]))

events = []
for tk, c in cands.items():
    # một mã có thể có >1 sự kiện (quý khác nhau) — gom theo cụm entry cách nhau >20 ngày
    ds = sorted(c["votes"])
    groups, cur = [], [ds[0]]
    for d in ds[1:]:
        if (d - cur[-1]).days > 20:
            groups.append(cur); cur = [d]
        else:
            cur.append(d)
    groups.append(cur)
    for g in groups:
        # ưu tiên ngày tường minh (WINDOW_PASSED/UPCOMING date) — cái có nhiều phiếu nhất
        e = max(g, key=lambda d: c["votes"][d])
        if LO <= e <= HI:
            last = [x for x in c["rows"] if abs((x[0] - e).days) <= 12]
            events.append({"ticker": tk, "entry": e, "n_csv": len(last),
                           "dd": last[-1][3] if last else "", "votes": {str(k): v for k, v in c["votes"].items() if k in g}})
events.sort(key=lambda x: (x["entry"], x["ticker"]))

# ---------- 2. fill thật
_fill_cache = {}


def fills(day, acct_no):
    key = (day, acct_no)
    if key in _fill_cache:
        return _fill_cache[key]
    best = {}
    p = f"{EL}/dnse_raw_{day}.jsonl"
    if os.path.exists(p):
        for line in open(p):
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if str(rec.get("account_no")) != acct_no:      # §12 — lọc account TRƯỚC
                continue
            if rec.get("kind") != "orders":
                continue
            for o in (rec.get("payload") or {}).get("orders") or []:
                if str(o.get("accountNo")) != acct_no:
                    continue
                oid = o.get("id")
                if oid not in best or (o.get("fillQuantity") or 0) >= (best[oid].get("fillQuantity") or 0):
                    best[oid] = o
    agg = collections.defaultdict(lambda: {"fill": 0, "placed": 0, "prices": set(), "val": 0.0})
    for o in best.values():
        if o.get("side") != "NB":
            continue
        a = agg[o["symbol"]]
        a["fill"] += o.get("fillQuantity") or 0
        a["placed"] += o.get("quantity") or 0
        a["prices"].add(o.get("price"))
        a["val"] += (o.get("fillQuantity") or 0) * (o.get("averagePrice") or 0)
    _fill_cache[key] = (os.path.exists(p), agg)
    return _fill_cache[key]


def broker_email(day, acct_no, tk):
    p = f"{EL}/dnse_khoplenh_broker_confirm_{day.strftime('%d-%m-%Y')}.csv"
    if not os.path.exists(p):
        return None
    q = 0
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if r["tieu_khoan"] == acct_no and r["ma"] == tk and r["loai_lenh"] == "MUA":
            q += int(float(r["khoi_luong"]))
    return q


def journal(acct, day, tk):
    p = f"{EL}/exec_{acct}_{day}_journal.csv"
    if not os.path.exists(p):
        return None
    c = collections.Counter()
    notes = []
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if r.get("ticker") == tk and (r.get("side") or "").lower() == "buy":
            c[r["event"]] += 1
            if r["event"] in ("WAIT_CASH", "GHOST_ORDER_DETECTED", "HARD_CEILING_BLOCK", "PLACE_FAIL", "STEP_FAIL") and len(notes) < 2:
                notes.append(f"{r['event']}:{(r.get('note') or '')[:80]}")
    return dict(c), notes


def plan_info(acct, day, tk):
    p = f"{WC}/data/trade_plans/plan_{acct}_{day}.json"
    if not os.path.exists(p):
        return {"plan": "NO_PLAN"}
    try:
        d = json.load(open(p))
    except Exception as e:
        return {"plan": f"BAD_JSON {e}"}
    ords = [o for o in d.get("orders") or [] if o.get("ticker") == tk and str(o.get("side")).lower() == "buy"]
    dfr = [o for o in d.get("deferred_orders") or [] if o.get("ticker") == tk]
    la = json.dumps(d.get("lag_analysis") or {}, ensure_ascii=False)
    snip = ""
    i = la.find(f'"{tk}')
    if i >= 0:
        snip = la[i:i + 220]
    ptd = (d.get("park_trim_proposal") or {}).get("decision") if isinstance(d.get("park_trim_proposal"), dict) else None
    return {"plan": "OK", "n_orders": len(d.get("orders") or []),
            "lag_buy": [(o.get("quantity"), o.get("limit_price") or o.get("ref_price"), o.get("book"),
                         o.get("hard_no_chase_ceiling_vnd"), o.get("entry_window_day")) for o in ords],
            "deferred": [(o.get("quantity") or o.get("qty"), o.get("reason") or o.get("note") or o.get("status"),
                          o.get("target_value_vnd") or o.get("value_vnd")) for o in dfr],
            "lag_snip": snip, "park_trim": ptd}


rows = []
for ev in events:
    tk, e = ev["ticker"], ev["entry"]
    days = [e, nth_session(e, 1), nth_session(e, 2), nth_session(e, 3), nth_session(e, 4)]
    for acct, no in ACC.items():
        row = {"ticker": tk, "entry": str(e), "account": acct, "dd": ev["dd"][:160]}
        for k, d in enumerate(days, 1):
            ok, agg = fills(d, no)
            a = agg.get(tk)
            row[f"d{k}"] = str(d)
            row[f"d{k}_raw"] = ok
            row[f"d{k}_fill"] = a["fill"] if a else 0
            row[f"d{k}_placed"] = a["placed"] if a else 0
            row[f"d{k}_px"] = "|".join(str(x) for x in sorted(a["prices"])) if a else ""
            row[f"d{k}_email"] = broker_email(d, no, tk)
            if k <= 3:
                row[f"d{k}_plan"] = json.dumps(plan_info(acct, d, tk), ensure_ascii=False, default=str)
                j = journal(acct, d, tk)
                row[f"d{k}_journal"] = json.dumps(j, ensure_ascii=False) if j else ""
        rows.append(row)

with open(f"{OUT}/audit_live_rows.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print(f"events={len(events)} rows={len(rows)}")
for r in rows:
    pl = [json.loads(r[f"d{k}_plan"]) for k in (1, 2, 3)]
    tag = []
    for k, p in enumerate(pl, 1):
        if p.get("plan") != "OK":
            tag.append(f"d{k}:{p['plan']}")
        else:
            s = f"d{k}:"
            if p["lag_buy"]: s += f"BUY{p['lag_buy']}"
            if p["deferred"]: s += f"DFR{[x[1] for x in p['deferred']][:1]}"
            if p["lag_snip"] and not p["lag_buy"]: s += "SNIP:" + p["lag_snip"][:90]
            if s.endswith(":"): s += f"none(n_ord={p['n_orders']},pt={p['park_trim']})"
            tag.append(s)
    fl = [r[f"d{k}_fill"] for k in range(1, 6)]
    em = [r[f"d{k}_email"] for k in range(1, 4)]
    print(f"{r['ticker']:4} {r['entry']} {r['account']:7} fill{fl} email{em} || " + " | ".join(tag))
