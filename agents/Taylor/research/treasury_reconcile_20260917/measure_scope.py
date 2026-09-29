"""Nhánh A.1 — đo quy mô ảnh hưởng thật của sự kiện treasury buy_done/sell_done lên OShares.
READ-ONLY BQ. Chạy: cd WorkingClaude && $DNA_PYEXE mike/agents/Taylor/research/treasury_reconcile_20260917/measure_scope.py
"""
import json, sys, glob, os, csv
from datetime import date, timedelta
from zoneinfo import ZoneInfo
from datetime import datetime
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
import oshares_live as OL
from corp_action_lib import bq
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()

# 1) sự kiện, gộp trùng (ticker, public_date, action_type) — Bẫy (4) registry treasury_news
ev = bq("""
  SELECT ticker, CAST(public_date AS STRING) public_date, action_type,
         MAX(ABS(shares_delta)) abs_delta, COUNT(*) n_src, ANY_VALUE(news_id) news_id,
         ANY_VALUE(SUBSTR(title,1,100)) title
  FROM `lithe-record-440915-m9.tav2_bq.treasury_news` AS t
  WHERE action_type IN ('buy_done','sell_done')
  GROUP BY 1,2,3 ORDER BY 1,2""")
tickers = sorted({e["ticker"] for e in ev})
quarters, corp = OL._fetch(tickers, TODAY)
prune = {r["ticker"] for r in bq(f"""SELECT DISTINCT ticker FROM `lithe-record-440915-m9.tav2_bq.ticker_prune` AS p
  WHERE time >= DATE_SUB(DATE "{TODAY}", INTERVAL 45 DAY)""")}

def fin_before(tk, d):
    rows = [q for q in quarters if q["ticker"] == tk and q["time"] <= d]
    return float(rows[-1]["OShares"]) if rows else None

def ais_listed(tk, d):
    rows = [c for c in corp if c["ticker"] == tk and c["event_code"] == "AIS" and c["effective_date"]
            and c["effective_date"] <= d and c["shares_total_after"]]
    return (float(rows[-1]["shares_total_after"]), rows[-1]["effective_date"]) if rows else (None, None)

rows = []
for e in ev:
    base = fin_before(e["ticker"], e["public_date"])
    d = float(e["abs_delta"]) if e["abs_delta"] is not None else None
    sign = 1 if e["action_type"] == "buy_done" else -1   # buy_done ⇒ CP lưu hành GIẢM
    rows.append({**e, "signed_outstanding_delta": (-sign * d) if d else None,
                 "fin_oshares_before": base,
                 "pct_of_oshares": (100 * d / base) if (d and base) else None,
                 "in_prune_45d": e["ticker"] in prune})

# 2) ảnh hưởng HÔM NAY: oshares_live(live=True) vs dòng BCTC mới nhất vs AIS niêm yết
live = OL.oshares_at(tickers, TODAY, _cache=(quarters, corp), live=True)
tk_rows = []
for tk in tickers:
    r = live.get(tk) or {}
    fin = fin_before(tk, TODAY); lst, lst_d = ais_listed(tk, TODAY)
    v = r.get("value")
    net_known = sum((x["signed_outstanding_delta"] or 0) for x in rows if x["ticker"] == tk)
    tk_rows.append({"ticker": tk, "live_value": v, "method": r.get("method"),
                    "anchor_source": r.get("anchor_source"), "anchor_date": r.get("anchor_date"),
                    "fin_latest": fin, "ais_listed": lst, "ais_date": lst_d,
                    "live_minus_fin_pct": (100 * (v - fin) / fin) if (v and fin) else None,
                    "listed_minus_fin_pct": (100 * (lst - fin) / fin) if (lst and fin) else None,
                    "n_done_events": sum(1 for x in rows if x["ticker"] == tk),
                    "n_with_delta": sum(1 for x in rows if x["ticker"] == tk and x["abs_delta"]),
                    "net_known_outstanding_delta": net_known, "in_prune_45d": tk in prune})

# 3) mã đang nắm giữ — lọc account_no từng dòng (§12)
held = {}
f = sorted(glob.glob(f"{WC}/data/execution_logs/dnse_raw_*.jsonl"))[-1]
last = {}
for l in open(f):
    rec = json.loads(l)
    if rec.get("kind") != "positions":
        continue
    last[str(rec.get("account_no"))] = rec
for acct, label in (("0002023347", "SpaceX"), ("0001743768", "ZaloPay")):
    rec = last.get(acct)
    if rec is None or str(rec.get("account_no")) != acct:
        continue
    p = rec["payload"]; items = p if isinstance(p, list) else (p.get("deals") or p.get("positions") or p.get("data") or [])
    held[label] = sorted({(i.get("symbol") or i.get("ticker")) for i in items
                          if float(i.get("accumulateQuantity") or i.get("quantity") or i.get("totalQuantity") or 0) > 0})

for name, data in (("events_scope.csv", rows), ("tickers_today.csv", tk_rows)):
    with open(f"{OUT}/{name}", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)
json.dump({"positions_file": f, "held": held, "today": TODAY}, open(f"{OUT}/held.json", "w"), ensure_ascii=False, indent=1)
print("events", len(ev), "tickers", len(tickers), "with_delta", sum(1 for r in rows if r["abs_delta"]))
print("held", held)
