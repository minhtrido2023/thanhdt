"""A.1b — mã mà oshares_live(live=True) HÔM NAY neo vào AIS (số NIÊM YẾT, gồm CP quỹ) —
so với dòng BCTC mới nhất lăn tiến qua cùng ISS sau nó (số LƯU HÀNH, đã trừ CP quỹ). READ-ONLY."""
import csv, sys, os
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import oshares_live as OL
from corp_action_lib import bq, dilutes_share_count
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
tk = sorted({r["ticker"] for r in csv.DictReader(open(f"{OUT}/tickers_today.csv"))})
Q, C = OL._fetch(tk, TODAY)
live = OL.oshares_at(tk, TODAY, _cache=(Q, C), live=True)
rows = []
for t in tk:
    r = live[t]
    if not (r.get("anchor_source") or "").startswith("corporate_action"):
        continue
    qs = [q for q in Q if q["ticker"] == t]
    if not qs or r.get("value") is None:
        continue
    fq = qs[-1]
    iss = OL._dedup_iss([c for c in C if c["ticker"] == t and c["event_code"] == "ISS" and c["exright_date"]
                         and fq["time"] < c["exright_date"] <= TODAY and dilutes_share_count(c)])
    rolled, _, blockers = OL._roll(float(fq["OShares"]), iss)
    gap = r["value"] - rolled if rolled else None
    rows.append({"ticker": t, "method": r["method"], "anchor_date": r.get("anchor_date"), "live": r["value"],
                 "fin_time": fq["time"], "fin": fq["OShares"], "n_iss_after_fin": len(iss),
                 "fin_rolled": rolled, "blockers": len(blockers or []),
                 "gap_shares": gap, "gap_pct": 100 * gap / rolled if rolled else None})
with open(f"{OUT}/ais_anchor_gap.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for x in sorted(rows, key=lambda x: -abs(x["gap_pct"] or 0)):
    print(x["ticker"], x["method"], x["anchor_date"], f'{x["live"]:,.0f}', x["fin_time"], f'{float(x["fin"]):,.0f}',
          "iss", x["n_iss_after_fin"], "blk", x["blockers"], "gap%", None if x["gap_pct"] is None else round(x["gap_pct"], 3), x["gap_shares"])
