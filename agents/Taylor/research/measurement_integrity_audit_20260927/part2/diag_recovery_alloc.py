"""Chan doan: vi sao backtest_recovery_alloc.py khong tai lap so pin registry 2026-06-22.
Paper-only, khong sua file goc."""
import sys, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0,"/home/trido/thanhdt/WorkingClaude")
import pandas as pd, numpy as np
import backtest_recovery_alloc as M
d = M.load()
for end in ("2026-06-19","2026-09-25"):
    dd = d[d.index <= end]
    fired = ((dd["state"].isin([1,2])) & (dd["pbz"] <= -0.3)).sum()
    out = M.run(dd); c,sh,mdd,cal = M.metrics(out)
    o2 = M.run(dd, recovery={1:0.35,2:0.55}, thr=-0.3); c2,sh2,mdd2,_ = M.metrics(o2)
    print(f"END={end} n={len(dd)} fired={fired} | BASE {c*100:.1f}% Sh{sh:.2f} DD{mdd*100:.1f}% "
          f"| MILD {c2*100:.1f}% Sh{sh2:.2f} DD{mdd2*100:.1f}%")
# phan ra: bao nhieu phien fire theo nam, va pbz theo nam
f = d[(d["state"].isin([1,2]))]
print("\nphien CRISIS/BEAR theo nam:", f.groupby(f.index.year).size().to_dict())
g = d[(d["state"].isin([1,2])) & (d["pbz"]<=-0.3)]
print("phien fire theo nam:", g.groupby(g.index.year).size().to_dict())
print("\npbz median theo nam:", d.groupby(d.index.year)["pbz"].median().round(3).to_dict())
