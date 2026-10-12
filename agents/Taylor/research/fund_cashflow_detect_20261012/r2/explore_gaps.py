import sys, json, datetime, math
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/wt-fundcf-1012/bin")
import cash_identity as ci, corp_actions as ca
D = "/home/trido/thanhdt/WorkingClaude/data"; E = D + "/execution_logs"
acts = ca.load_corp_actions(D + "/corp_actions.json")
print([(a["ticker"], a["qty_multiplier"], str(a.get("broker_effective_ts")), str(a["ex_date"])) for a in acts])
for acc in ("SpaceX", "ZaloPay"):
    no = ci.load_account_no(acc, D + "/account_inception.json")
    rows = ci.load_nav_rows(acc, E); raw = ci.RawLog(no, E)
    for prev, cur in zip(rows, rows[1:]):
        s0, s1 = prev["snap"], cur["snap"]
        q0, q1 = raw.quantities_at(s0), raw.quantities_at(s1)
        if q0 is None or q1 is None:
            for s, q in ((s0, q0), (s1, q1)):
                if q is None:
                    ts = [t for t, _ in raw.day(s.date())["positions"]]
                    print(acc, "NOPOS", s, "positions trong ngày:", ts[:3], "…", ts[-2:], "n=", len(ts), "file:", raw.day(s.date())["exists"])
            continue
        fills = raw.fills_between(s0, s1); net = {}
        for fx in fills: net[fx["symbol"]] = net.get(fx["symbol"], 0) + (fx["qty"] if fx["side"] == "buy" else -fx["qty"])
        for sym in set(q0) | set(q1) | set(net):
            g = q1.get(sym, 0) - q0.get(sym, 0) - net.get(sym, 0)
            if abs(g) < 1e-6: continue
            cands = [a for a in acts if a["ticker"] == sym]
            info = [(a["qty_multiplier"], str(a.get("broker_effective_ts")), [round(b * (a["qty_multiplier"] - 1), 3) for b in (q0.get(sym, 0), q0.get(sym, 0) + net.get(sym, 0))]) for a in cands]
            print(acc, f"{prev['date']}→{cur['date']} {s0:%H:%M:%S}→{s1:%H:%M:%S}", sym, "gap", g, "q0", q0.get(sym, 0), "net", net.get(sym, 0), "q1", q1.get(sym, 0), info)
            if sym == "VHC":
                for o in raw.day(s1.date())["orders"].values():
                    if o.get("symbol") == "VHC": print("    VHC order", o.get("id"), o.get("side"), o.get("fillQuantity"), o.get("quantity"), o.get("orderStatus"), o.get("modifiedDate"), o.get("createdDate"))
                for d in (s0.date(), s1.date()):
                    for ts, ps in raw.day(d)["positions"][-4:]:
                        print("    pos", ts, [(p.get("openQuantity"), p.get("accumulateQuantity"), p.get("closedQuantity"), p.get("status")) for p in ps if p.get("symbol") == "VHC"])
