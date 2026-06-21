import sys, pandas as pd, numpy as np
df = pd.read_csv(sys.argv[1], low_memory=False)
d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
d = d.dropna(subset=["ymd"]).sort_values("ymd")
nav = d.groupby("ymd")["combined_nav"].last().astype(float)
def cagr(s):
    s = s.dropna()
    if len(s) < 5: return float("nan")
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    return ((s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1) * 100
print(f"    FULL {cagr(nav):.2f}%  IS {cagr(nav[nav.index<='2019-12-31']):.2f}%  OOS {cagr(nav[nav.index>='2020-01-01']):.2f}%")
ys = []
for y in range(int(nav.index[0].year), int(nav.index[-1].year) + 1):
    ny = nav[nav.index.year == y]
    if len(ny) < 5: continue
    ys.append(f"{y}:{(ny.iloc[-1]/ny.iloc[0]-1)*100:+.0f}")
print("    per-year: " + "  ".join(ys))
