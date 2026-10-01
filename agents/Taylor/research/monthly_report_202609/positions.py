import sys, json
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/bin")
import report_return_gate as g
ACC = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
asof = "2026-09-30"
res = {}
for lb, no in ACC.items():
    pos = g.broker_positions(no, asof)
    gross, mism = g.entitled_gross(pos.keys(), no, asof)
    rows = []
    for s, (q, cp, px) in pos.items():
        pct, pl, raw = g.expected_pct(q, cp, px, gross.get(s, 0.0))
        rows.append(dict(sym=s, qty=q, cost_broker=cp, gross_div=gross.get(s, 0.0), raw_cost=raw, px=px, mv=q*px, pl=pl, pct=pct))
    rows.sort(key=lambda r: -r["mv"])
    res[lb] = dict(rows=rows, mismatches=[list(m) for m in mism], excluded=sorted(g.excluded_tickers(lb)))
json.dump(res, open("positions_20260930.json", "w"), indent=1, default=str)
for lb, d in res.items():
    print("==", lb, "n=", len(d["rows"]), "mv=", round(sum(r["mv"] for r in d["rows"])), "excluded", d["excluded"], "mism", d["mismatches"])
    for r in d["rows"]:
        print(f'{r["sym"]} {r["qty"]:.0f} cp={r["cost_broker"]:.0f} div={r["gross_div"]:.0f} raw={r["raw_cost"]:.0f} px={r["px"]:.0f} mv={r["mv"]:.0f} pl={r["pl"]:.0f} pct={r["pct"]:.2f}')
