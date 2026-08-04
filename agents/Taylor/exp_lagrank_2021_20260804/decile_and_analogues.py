# -*- coding: utf-8 -*-
"""Top-decile behaviour of the ranking key + search for 2021-analogue years (Taylor_20260804_061252).

Resolves the apparent contradiction found earlier:
  - full-pool rank-IC of `surprise_B_MA` in 2021 was +0.181 (2nd best of 13 years), yet
  - the engine's median realised LAG position return at NAV 1B fell 12.5% (FIFO) -> 7.9% (w5).
At NAV 1B only ~10% of the candidate pool gets funded, so what matters is not the full-pool IC but
the TOP DECILE of the ranking key. A positive IC with a non-monotonic top tail produces exactly this.
So: mean realised drift by DECILE of the ranking key, per year.

Also (dispatch question 3): score every year on the "indiscriminate melt-up" markers measured in
dispersion_by_year.py, to see whether 2021 is unique in the sample or one of a repeating pattern.

Usage: python decile_and_analogues.py
"""
import numpy as np
import pandas as pd
from dispersion_by_year import build_events, YEARS

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 60)

pool = build_events()
pool = pool[pool["post_ret"].notna()]

print("=== Mean realised T+5->T+30 drift (%) by DECILE of surprise_B_MA, per release year ===")
print("    (D10 = highest surprise = what a surprise-ranking rule funds first when capital binds)\n")
rows = []
for y in YEARS:
    g = pool[pool["year"] == y]
    if len(g) < 60:
        continue
    q = pd.qcut(g["surprise_B_MA"].rank(method="first"), 10, labels=range(1, 11))
    m = g.groupby(q, observed=True)["post_ret"].mean()
    r = {"year": y, "N": len(g), "all": g["post_ret"].mean()}
    for k in range(1, 11):
        r[f"D{k}"] = m.get(k, np.nan)
    r["D10_minus_all"] = r["D10"] - r["all"]
    r["top20_minus_all"] = (m.get(10, np.nan) + m.get(9, np.nan)) / 2 - r["all"]
    rows.append(r)
dec = pd.DataFrame(rows).set_index("year")
print(dec.round(1).to_string())
print("\n  ranked by D10 minus pool mean (how much the funded top decile beat the average candidate):")
print(dec["D10_minus_all"].sort_values(ascending=False).round(2).to_string())

# ---------------------------------------------------------------- 2021-analogue search
print("\n\n=== 2021-analogue search — melt-up markers per year, z-scored across the sample ===")
t2 = pd.read_csv("tier2_market_by_year.csv", index_col=0)
t2 = t2[t2["N_names"] > 0]
mk = pd.DataFrame(index=t2.index)
mk["breadth%"] = t2["breadth_MA200_mean%"]
mk["pos_ret%"] = t2["pos_ret%"]
mk["ret_mean%"] = t2["ret_mean%"]
mk["turnover_yoy%"] = t2["turnover_Bvnd"].pct_change() * 100
mk["quality_IC"] = t2["IC_ROEmin_ret"]          # negative = quality punished
mk["cheap_minus_exp"] = t2["cheapPE_minus_exp%"]  # negative = value punished
z = pd.DataFrame(index=mk.index)
for c in ("breadth%", "pos_ret%", "ret_mean%", "turnover_yoy%"):
    z[c] = (mk[c] - mk[c].mean()) / mk[c].std()
for c in ("quality_IC", "cheap_minus_exp"):      # invert: more negative = more melt-up-like
    z[c] = -(mk[c] - mk[c].mean()) / mk[c].std()
mk["meltup_z"] = z.mean(axis=1)
print(mk.round(2).to_string())
print("\n  composite melt-up score (mean of 6 z-scores, higher = more indiscriminate):")
print(mk["meltup_z"].sort_values(ascending=False).round(2).to_string())
dec.to_csv("decile_by_year.csv")
mk.to_csv("meltup_markers_by_year.csv")
print("\nwrote decile_by_year.csv / meltup_markers_by_year.csv")
