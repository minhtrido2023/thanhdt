"""IS/OOS metric splitter for a pt_v23 audit CSV. Computes CAGR/Sharpe/MaxDD/Calmar on the DAILY
combined_nav series for FULL / IS(<=2019-12-31) / OOS(>=2020-01-01) — same formulas as harness calc_metrics."""
import sys, numpy as np, pandas as pd
df = pd.read_csv(sys.argv[1], low_memory=False)
d = df[df["record_type"] == "DAILY"].copy()
d["ymd"] = pd.to_datetime(d["ymd"]); d = d.sort_values("ymd")
nav = pd.Series(d["combined_nav"].astype(float).values, index=d["ymd"].values)

def metrics(s):
    s = s.dropna()
    if len(s) < 5: return None
    days = (s.index[-1] - s.index[0]).days
    cagr = (s.iloc[-1]/s.iloc[0]) ** (365.25/max(days,1)) - 1
    r = s.pct_change().dropna()
    sh = r.mean()/r.std()*np.sqrt(252) if r.std() > 0 else float("nan")
    dd = (s/s.cummax() - 1).min()
    cal = cagr/abs(dd) if dd < 0 else float("nan")
    return cagr*100, sh, dd*100, cal

label = sys.argv[2] if len(sys.argv) > 2 else ""
print(f"{label:>22} {'window':>5} {'CAGR%':>7} {'Sharpe':>7} {'MaxDD%':>7} {'Calmar':>7}")
for w, s in [("FULL", nav),
             ("IS", nav[nav.index <= "2019-12-31"]),
             ("OOS", nav[nav.index >= "2020-01-01"])]:
    m = metrics(s)
    if m: print(f"{label:>22} {w:>5} {m[0]:>7.2f} {m[1]:>7.2f} {m[2]:>7.1f} {m[3]:>7.2f}")
