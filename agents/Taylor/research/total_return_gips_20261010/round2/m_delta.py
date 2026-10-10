import sys
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/wt-totalreturn-1010/bin")
import dividend_adjusted_return as dar
for lb, no in dar.ACCOUNTS.items():
    deltas = dar.broker_cash_deltas(no)
    series = dar.broker_cost_series(no)
    by_day = {}
    for tk, rows in series.items():
        for st in dar.classify_cost_steps(rows):
            by_day.setdefault(st["ts"][:10], []).append((tk, st["kind"], round(st["cash"],2), st["q0"], st["q1"], st["ts"][11:16]))
    days = sorted(set(deltas) | {d for d, v in by_day.items() if any(k in ("cash","cash+stock","stock") for _,k,*_ in v)})
    print("=====", lb)
    for d in days:
        corp = [x for x in by_day.get(d, []) if x[1] in ("cash","cash+stock","stock")]
        s = sum(q0*c for _,k,c,q0,_,_ in corp)
        print(d, "delta=%12.0f" % deltas.get(d,0), "Σstep=%12.0f" % s, "diff=%10.0f" % (deltas.get(d,0)-s), corp)
    oth = {}
    for d, v in by_day.items():
        for x in v:
            if x[1] in ("other","buy"): oth[x[1]] = oth.get(x[1],0)+1
    print("buy/other counts:", oth)
