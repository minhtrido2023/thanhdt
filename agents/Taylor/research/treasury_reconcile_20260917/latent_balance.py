"""A.1c — CP quỹ đang TỒN (latent): tại dòng BCTC mới nhất, số niêm yết (AIS gần nhất <= dòng quý,
lăn qua ISS ở giữa) − OShares BCTC. Dương ⇒ niêm yết > lưu hành ⇒ nhiều khả năng CP quỹ đang giữ.
Rủi ro: ngày nào neo AIS tươi (<=90 ngày) thì oshares_live phục vụ số NIÊM YẾT ⇒ thừa đúng phần này."""
import csv, sys, os, json
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import oshares_live as OL
from corp_action_lib import dilutes_share_count
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
T = {r["ticker"]: r for r in csv.DictReader(open(f"{OUT}/tickers_today.csv"))}
held = json.load(open(f"{OUT}/held.json"))["held"]; H = set(held["SpaceX"]) | set(held["ZaloPay"])
Q, C = OL._fetch(sorted(T), TODAY)
rows = []
for t in sorted(T):
    qs = [q for q in Q if q["ticker"] == t]
    if not qs:
        continue
    fq = qs[-1]
    ais = [c for c in C if c["ticker"] == t and c["event_code"] == "AIS" and c["effective_date"]
           and c["effective_date"] <= fq["time"] and c["shares_total_after"]]
    if not ais:
        continue
    a = ais[-1]
    iss = OL._dedup_iss([c for c in C if c["ticker"] == t and c["event_code"] == "ISS" and c["exright_date"]
                         and a["effective_date"] < c["exright_date"] <= fq["time"] and dilutes_share_count(c)])
    listed, _, blk = OL._roll(float(a["shares_total_after"]), iss)
    if listed is None or blk:
        continue
    gap = listed - float(fq["OShares"])
    rows.append({"ticker": t, "fin_time": fq["time"], "fin": fq["OShares"], "ais_date": a["effective_date"],
                 "n_iss_between": len(iss), "listed_rolled": listed, "gap": gap,
                 "gap_pct": 100 * gap / float(fq["OShares"]), "held": t in H, "prune": T[t]["in_prune_45d"],
                 "n_done": T[t]["n_done_events"], "live_method_today": T[t]["method"]})
with open(f"{OUT}/latent_balance.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
pos = [r for r in rows if r["gap_pct"] > 0.1]; neg = [r for r in rows if r["gap_pct"] < -0.1]
print("evaluated", len(rows), "gap>0.1%", len(pos), "gap<-0.1%", len(neg), "|gap|<=0.1%", len(rows) - len(pos) - len(neg))
for lo, hi in ((0.1, 0.5), (0.5, 1), (1, 2), (2, 5), (5, 15), (15, 1e9)):
    print(f" +[{lo},{hi}) {sum(lo <= r['gap_pct'] < hi for r in pos)}")
print("prune & gap>0.1%:", sorted((r["ticker"], round(r["gap_pct"], 2)) for r in pos if r["prune"] == "True"))
print("held:", [(r["ticker"], round(r["gap_pct"], 2), r["ais_date"], r["live_method_today"]) for r in rows if r["held"]])
