"""Do do lech quy uoc CLAUDE.md: 'lai tien gui nhan roi 0%/nam' vs 2 file dung Big-4 that."""
import sys, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0,"/home/trido/thanhdt/WorkingClaude")
import pandas as pd, numpy as np
import backtest_recovery_alloc as A, backtest_recovery_alloc_2011 as B
for nm, M, vs in (("alloc2014", A, {"BASELINE":dict(),"DEPTH1.0":dict(depth=(-0.3,-0.7,1.0)),"DEPTH1.5":dict(depth=(-0.3,-0.7,1.5))}),
                  ("alloc2011", B, {"BASELINE":dict(),"DEPTH0.95":dict(depth=(-0.3,-0.5,0.95)),"DEPTH1.5":dict(depth=(-0.3,-0.7,1.5))})):
    d = M.load(); d = d[d.index <= "2026-06-19"]
    d0 = d.copy(); d0["dep_yr"] = 0.0
    print(f"\n=== {nm} (n={len(d)}, {d.index[0].date()}..{d.index[-1].date()}) dep_yr mean that={d['dep_yr'].mean():.4f}")
    print(f"{'variant':12}{'CAGR dep=THAT':>15}{'CAGR dep=0':>12}{'delta pp':>10}")
    for v,kw in vs.items():
        c1 = M.metrics(M.run(d, **kw))[0]; c2 = M.metrics(M.run(d0, **kw))[0]
        print(f"{v:12}{c1*100:>14.2f}%{c2*100:>11.2f}%{(c1-c2)*100:>9.2f}")
