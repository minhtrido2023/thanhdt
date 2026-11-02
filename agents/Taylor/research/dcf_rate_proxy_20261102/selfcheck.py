# -*- coding: utf-8 -*-
"""Selfcheck theo PREREG §Self-check (1)(2) + r* đúng nghiệm. (3) TZ: chạy bằng selfcheck_tz.sh."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analysis as A0  # noqa: E402
sys.path.insert(0, os.path.join(A0.RES, "dcf_level_rerun_20261102"))
import level as LV     # noqa: E402
p = A0.load_panel(); fail = 0
a = A0.fv(p, 0.1225, 0.055); b = LV.fv(p, p.os_live.values, 0.5, 0.055)
d = np.nanmax(np.abs(a - b)); print(f"(1) FV analysis.fv vs level.fv (VND/cp) max|Δ| = {d:.3e}"); fail += d > 1e-6
T = pd.read_csv(os.path.join(A0.OUT, "scen_today.csv")).set_index("scen")
V = pd.read_csv(os.path.join(A0.RES, "dcf_level_rerun_20261102", "out", "level_live_impact_20261030.csv"))
v0 = V[V.variant.str.startswith("V0 live")].iloc[0]
print(f"(2) %RẺ (a) {T.at['a_const','pct_RE']:.6f} vs V0 {v0.pct_RE:.6f}; n {T.at['a_const','n']} vs {v0.n}")
fail += abs(T.at["a_const", "pct_RE"] - v0.pct_RE) > 1e-9 or T.at["a_const", "n"] != v0.n
M = pd.read_csv(os.path.join(A0.OUT, "monthly_series.csv"), index_col=0)
rs = M.rstar.dropna(); rs.index = pd.PeriodIndex(rs.index, freq="M")
r_row = rs.reindex(p.m).values / 100
l = np.log(p.Price.values / A0.fv(p, r_row, 0.055))
med = pd.Series(l).groupby(p.m.values).median()
print(f"(3) r*: max|median log P/FV| tại r* = {med.abs().max():.2e} trên {len(med)} tháng (r* làm tròn 4 số ⇒ dung sai 1e-3)")
fail += med.abs().max() > 1e-3
print("SELFCHECK", "PASS" if not fail else f"FAIL ({fail})")
sys.exit(int(fail > 0))
