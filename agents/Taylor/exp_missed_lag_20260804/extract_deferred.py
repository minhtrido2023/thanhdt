#!/usr/bin/env python3
"""Quet moi plan file that -> liet ke MOI order bi defer/skip, phan loai book + ly do."""
import json, glob, os, re, sys

ROOT = "/home/trido/thanhdt/WorkingClaude"
FILES = sorted(glob.glob(f"{ROOT}/data/trade_plans/plan_SpaceX_2026-*.json")) + \
        sorted(glob.glob(f"{ROOT}/data/trade_plans/plan_ZaloPay_2026-*.json"))

CASH_PAT = re.compile(r"thi[eế]u\s*ti[eề]n|thieu tien|kh[oô]ng đủ ti[eề]n|khong du tien|insufficient|thi[eế]u v[oố]n|thieu von|thi[eế]u cash", re.I)
LISTKEYS = ["deferred_orders", "skipped_orders", "orders_hold", "removed_orders", "fallback_order"]

rows = []
for f in FILES:
    d = json.load(open(f))
    base = os.path.basename(f)
    if "superseded" in base or "wrongdate" in base:
        continue
    acct = d.get("account"); pdate = d.get("plan_date")
    for k in LISTKEYS:
        v = d.get(k)
        if not v: continue
        if isinstance(v, dict): v = [v]
        for o in v:
            if not isinstance(o, dict): continue
            reason = " ".join(str(o.get(x, "")) for x in
                              ("defer_reason","deferred_reason","removed_reason","reason","skip_reason","status","note"))
            rows.append(dict(file=base, account=acct, plan_date=pdate, field=k,
                             ticker=o.get("ticker"), book=o.get("book"),
                             play=o.get("play_type"), qty=o.get("qty"),
                             ref_price=o.get("ref_price"),
                             cost=o.get("estimated_cost_vnd") or o.get("total_with_fee_vnd"),
                             hold_periods=o.get("hold_periods"),
                             hold_from=o.get("hold_from"),
                             cash_reason=bool(CASH_PAT.search(reason)),
                             reason=reason.strip()[:400]))
    # orders[] co status defer/skip
    for o in d.get("orders", []) or []:
        if not isinstance(o, dict): continue
        st = str(o.get("status","")) + str(o.get("execution_status",""))
        blob = json.dumps(o, ensure_ascii=False)
        if re.search(r"defer|skip|hold|cancel", st, re.I):
            rows.append(dict(file=base, account=acct, plan_date=pdate, field="orders[status]",
                             ticker=o.get("ticker"), book=o.get("book"), play=o.get("play_type"),
                             qty=o.get("qty"), ref_price=o.get("ref_price"),
                             cost=o.get("estimated_cost_vnd"), hold_periods=o.get("hold_periods"),
                             hold_from=o.get("hold_from"),
                             cash_reason=bool(CASH_PAT.search(blob)), reason=st[:400]))

print(f"TONG so ban ghi defer/skip/remove/hold: {len(rows)}\n")
print(f"{'DATE':<11}{'ACCT':<9}{'FIELD':<18}{'TICK':<6}{'BOOK':<8}{'CASH?':<6}COST")
for r in rows:
    print(f"{r['plan_date']:<11}{str(r['account']):<9}{r['field']:<18}{str(r['ticker']):<6}{str(r['book']):<8}{str(r['cash_reason']):<6}{r['cost']}")

json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "deferred_raw.json"), "w"),
          ensure_ascii=False, indent=1)
print("\n--- LAG + cash_reason=True ---")
lag = [r for r in rows if r["book"] == "LAG" and r["cash_reason"]]
for r in lag:
    print(f"{r['plan_date']} {r['account']} {r['ticker']} qty={r['qty']} ref={r['ref_price']} hold={r['hold_periods']} from={r['hold_from']}")
    print("   ", r["reason"][:260])
print(f"N LAG-thieu-tien (ban ghi, chua dedupe) = {len(lag)}")
