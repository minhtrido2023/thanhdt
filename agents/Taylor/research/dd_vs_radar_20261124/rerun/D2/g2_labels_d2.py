#!/usr/bin/env python3
"""D2 (5): nhãn hướng của mô-đun G2 lấy từ CHÍNH cột `direction` của waterfall D1 (không gán tay).
D1 REPORT xếp r_cost_of_equity vào nhóm 'một chiều' — CSV ghi two_way ở 19/19 dòng r. Ghi bảng đã sửa."""
import os
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); D1 = os.path.join(H, "..", "..", "D1", "calc")
w = pd.concat([pd.read_csv(os.path.join(D1, f)) for f in ("g2_waterfall_A.csv", "g2_waterfall_B.csv")])
w["base"] = w["module"].str.split(" ").str[0]
lab = w.groupby("base")["direction"].agg(lambda s: "|".join(sorted(set(s.dropna()))))
s = pd.read_csv(os.path.join(D1, "g2_module_summary.csv")).merge(lab.rename("direction_csv"), on="base", how="left")
os.makedirs(os.path.join(H, "out"), exist_ok=True)
s.to_csv(os.path.join(H, "out", "g2_module_summary_d2.csv"), index=False)
print(s[["base", "n_steps", "median_step_pct", "n_down", "n_up", "direction_csv"]].to_string(index=False))
