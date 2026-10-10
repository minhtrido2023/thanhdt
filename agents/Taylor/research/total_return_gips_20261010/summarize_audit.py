#!/usr/bin/env python3
"""Tóm tắt sent_reports_audit.out: dòng nào công bố lệch số đúng chuẩn > TOL điểm %."""
import json, sys, collections
TOL = 0.05
rows = [json.loads(l) for l in open(sys.argv[1] if len(sys.argv) > 1 else "sent_reports_audit.out")]
by = collections.OrderedDict()
for r in rows:
    by.setdefault(r["report"], []).append(r)
tot = bad = 0
for rep, rs in by.items():
    errs = [r for r in rs if "error" in r]
    chk = [r for r in rs if "error" not in r]
    off = [r for r in chk if r.get("correct") is None or abs(r["diff"]) > TOL]
    tot += len(chk); bad += len(off)
    print(f"{rep}: {len(chk)} dòng khớp vị thế, {len(off)} lệch" + (f"  LỖI: {errs[0]['error'][:120]}" if errs else ""))
    for r in off:
        if r.get("correct") is None:
            print(f"    {r['acct']:8} {r['tk']} KL={r['qty']:.0f} công bố {r['published']:+.2f}% | KHÔNG dựng được: {r['why'][0][:150]}")
        else:
            print(f"    {r['acct']:8} {r['tk']} KL={r['qty']:.0f} công bố {r['published']:+.2f}% | đúng {r['correct']:+.2f}% | lệch {r['diff']:+.2f}pp | cổ tức/cp {r['gross']:,.2f} giá vốn thô {r['raw']:,.2f} (cp broker {r['cp']:,.2f}, giá {r['mkt']:,.0f})")
print(f"\nTỔNG: {tot} dòng, {bad} lệch > {TOL}pp")
