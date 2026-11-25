# -*- coding: utf-8 -*-
"""j_delta.py — bảng delta giữa các giai đoạn chạy (out_A = V2 tái lập, out_B…). Dùng: python j_delta.py out_A out_C [...]  → in markdown + ghi out/delta_<a>_<b>.csv"""
import os, sys, json, numpy as np, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
dirs = sys.argv[1:]
def load(d):
    p = os.path.join(ROOT, d); m = pd.read_csv(os.path.join(p, "metrics2.csv")); m = m[m.scope == "ALL"].set_index(["model", "era"])
    b = pd.read_csv(os.path.join(p, "bt2_summary.csv")) if os.path.exists(os.path.join(p, "bt2_summary.csv")) else None
    return m, b
rows = []
D = {d: load(d) for d in dirs}
MOD = ["D0", "D0B", "EPV", "MULT", "HEDf", "ENS1", "ENS1w", "ENS2", "N0"]
for mod in MOD:
    for era in ("IS", "OOS"):
        r = {"item": f"{mod} {era}"}
        for d in dirs:
            m = D[d][0]
            if (mod, era) in m.index:
                x = m.loc[(mod, era)]; r[f"{d}"] = f"IC {x.ic36:.3f} | Uhit {x.U_hit*100:.1f} Ust {x.U_static*100:.1f} | đúng {x.O_right_rel*100:.1f} sai {x.O_false*100:.1f} (nO={int(x.O_n)})"
        rows.append(r)
bt = ["EW_f1", "S1_ENS1w_f1", "S1_D0_f1", "S3f_f1", "S3f_D0_f1", "S7_ENS1w_f1", "S7_D0_f1", "S7_EPN_f1", "S1_ENS1w_f1_deadin", "EW_f1_bqonly", "S2_ENS1w_f1", "S5_ENS1w_f1"]
for s in bt:
    r = {"item": s}
    for d in dirs:
        b = D[d][1]
        if b is None:
            continue
        x = b[b.strategy == s].set_index("era")
        if len(x):
            r[d] = f"ALL {x.loc['ALL','cagr']*100:.2f} | IS {x.loc['IS','cagr']*100:.2f} | OOS {x.loc['OOS','cagr']*100:.2f} | Sh {x.loc['ALL','sharpe']:.2f} | DD {x.loc['ALL','maxdd']*100:.1f}"
    rows.append(r)
df = pd.DataFrame(rows); print(df.to_string(index=False, max_colwidth=120)); df.to_csv(os.path.join(ROOT, "out", f"delta_{'_'.join(dirs)}.csv"), index=False)
