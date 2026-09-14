"""Kiểm chứng số trước/sau vá bằng dữ liệu SAU asof: dòng quý kế tiếp và AIS kế tiếp (sự thật hậu nghiệm)."""
import json, sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import oshares_live as ol
ch = [c for c in json.load(open("sweep_changes_20260914.json"))["changes"] if c["branch"] == "live"]
tks = sorted({c["ticker"] for c in ch})
q, corp = ol._fetch(tks, "2026-09-14")
res = []
for c in ch:
    nq = sorted([x for x in q if x["ticker"] == c["ticker"] and x["time"] > c["asof"]], key=lambda x: x["time"])
    na = sorted([x for x in corp if x["ticker"] == c["ticker"] and x["event_code"] == "AIS" and x["effective_date"]
                 and x["effective_date"] > c["asof"] and x["shares_total_after"]], key=lambda x: x["effective_date"])
    truth = []
    if nq: truth.append(("next_q", nq[0]["time"], float(nq[0]["OShares"])))
    if na: truth.append(("next_ais", na[0]["effective_date"], float(na[0]["shares_total_after"])))
    def err(v, t): return None if v is None else round((v / t - 1) * 100, 3)
    res.append({**{k: c[k] for k in ("ticker", "row_time", "asof", "old", "new", "new_method", "held")},
                "truth": [(k, d, v, err(c["old"], v), err(c["new"], v)) for k, d, v in truth]})
w = {"new_closer": 0, "old_closer": 0, "tie": 0, "no_truth": 0}
for r in res:
    t = [x for x in r["truth"] if x[0] == "next_q"] or r["truth"]
    if not t or r["new"] is None: w["no_truth"] += 1; continue
    eo, en = abs(t[0][3]), abs(t[0][4])
    w["new_closer" if en < eo - 1e-9 else ("old_closer" if eo < en - 1e-9 else "tie")] += 1
    print(f"{r['ticker']:4} asof={r['asof']} old_err={t[0][3]:+8.3f}% new_err={t[0][4]:+8.3f}%  vs {t[0][0]} {t[0][1]} {t[0][2]:,.0f}")
for r in res:
    if r["new"] is None: print("AMBIG", r["ticker"], r["asof"], "old", r["old"], "truth", r["truth"])
print(w)
json.dump(res, open("audit_future_truth_20260914.json", "w"), ensure_ascii=False, indent=1)
