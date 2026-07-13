"""
Walk-forward validation of ecology_dashboard.py mood signal + P(NEUTRAL->BEAR/CRISIS)
Job: Taylor_20260713_042317 (research only, no production change)

Part 1: mood vs forward VNINDEX return
  - IS 2014-2019: decile edges from IS mood only; fwd20/fwd60 by decile; Spearman IC
  - OOS 2020+  : apply IS edges (no re-fit); same stats
  - Non-overlapping subsample (every 60th session) as autocorrelation sanity check
Part 2: P(NEUTRAL -> hits BEAR(2) or CRISIS(1) within N sessions), N=20/40/60,
  from fresh dt5g_vnindex.csv (through 2026-07-10), full sample + post-2020.
"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

W = "/home/trido/thanhdt/WorkingClaude"
WIN = 504

def rz(s, win=WIN):
    m = s.rolling(win, min_periods=120).mean()
    sd = s.rolling(win, min_periods=120).std()
    return (s - m) / sd

def rpct(s, win=WIN):
    return s.rolling(win, min_periods=120).apply(lambda x: (x.iloc[-1] >= x).mean(), raw=False)

e = pd.read_csv(W + "/data/ecology_panel.csv", parse_dates=["time"])
st = pd.read_csv(W + "/data/dt5g_vnindex.csv", parse_dates=["time"])[["time", "state", "vnindex"]]
df = e.merge(st, on="time", how="left").sort_values("time").reset_index(drop=True)
df["state"] = df["state"].ffill()
df["vnindex"] = df["vnindex"].ffill()
df["disp_s"] = df["disp"].rolling(10).mean()
df["opportunity"] = rpct(df["disp_s"])
df["mood"] = (rz(df["breadth200"]) + rz(df["pct_overbought"] - df["pct_oversold"]) + rz(df["pbz_med"])) / 3.0
df["fwd20"] = df["vnindex"].shift(-20) / df["vnindex"] - 1
df["fwd60"] = df["vnindex"].shift(-60) / df["vnindex"] - 1

d = df.dropna(subset=["mood", "fwd60"]).copy()
is_m = d["time"] < "2020-01-01"
IS, OOS = d[is_m].copy(), d[~is_m].copy()
print(f"IS: {IS['time'].min().date()}->{IS['time'].max().date()} n={len(IS)} | OOS: {OOS['time'].min().date()}->{OOS['time'].max().date()} n={len(OOS)}")

# IS decile edges, applied unchanged to OOS
edges = IS["mood"].quantile(np.linspace(0, 1, 11)).values.copy()
edges[0], edges[-1] = -np.inf, np.inf

def dec_table(x, label):
    x = x.copy()
    x["dec"] = pd.cut(x["mood"], edges, labels=False, include_lowest=True)
    g = x.groupby("dec").agg(mood=("mood", "mean"), fwd20=("fwd20", "mean"),
                             fwd60=("fwd60", "mean"), win60=("fwd60", lambda v: (v > 0).mean()),
                             n=("fwd60", "size"))
    g[["fwd20", "fwd60", "win60"]] = (g[["fwd20", "fwd60", "win60"]] * 100).round(2)
    g["mood"] = g["mood"].round(2)
    print(f"\n--- {label} (IS-fixed decile edges) ---")
    print(g.to_string())
    lo, hi = g.iloc[0], g.iloc[-1]
    print(f"spread fwd60 (bottom-top decile) = {lo['fwd60']-hi['fwd60']:+.2f}pp | "
          f"contrarian requires >0")
    ic20 = spearmanr(x["mood"], x["fwd20"])
    ic60 = spearmanr(x["mood"], x["fwd60"])
    print(f"Spearman IC mood->fwd20: {ic20.statistic:+.3f} (p={ic20.pvalue:.1e}) | "
          f"mood->fwd60: {ic60.statistic:+.3f} (p={ic60.pvalue:.1e})  [overlap-inflated p]")
    # non-overlapping every-60th sanity
    xs = x.iloc[::60]
    if len(xs) >= 15:
        icn = spearmanr(xs["mood"], xs["fwd60"])
        print(f"Non-overlap (every 60th, n={len(xs)}): IC fwd60 = {icn.statistic:+.3f} (p={icn.pvalue:.3f})")
    return g

g_is = dec_table(IS, "IS 2014-2019")
g_oos = dec_table(OOS, "OOS 2020+")

# sign stability of decile ordering IS vs OOS
sp = spearmanr(g_is["fwd60"], g_oos["fwd60"])
print(f"\nDecile-profile stability IS-vs-OOS (Spearman of fwd60 by decile): {sp.statistic:+.3f} (p={sp.pvalue:.3f})")

# ---------- Part 2: P(NEUTRAL -> BEAR/CRISIS within N) ----------
print("\n================ P(NEUTRAL -> BEAR/CRISIS within N sessions) — DT5G live, fresh ================")
s = st.dropna(subset=["state"]).sort_values("time").reset_index(drop=True)
s["state"] = s["state"].astype(int)
print(f"state series: {s['time'].min().date()} -> {s['time'].max().date()} | {len(s)} sessions")
arr = s["state"].values
bad = np.isin(arr, [1, 2]).astype(int)
# forward-any-bad within N via reversed cumulative trick
for scope, mask in [("FULL 2014+", np.ones(len(s), bool)),
                    ("2020+", (s["time"] >= "2020-01-01").values)]:
    print(f"\n[{scope}]")
    for N in (20, 40, 60):
        hit = np.array([bad[i+1:i+1+N].max() if i + 1 < len(arr) else 0 for i in range(len(arr))])
        valid = np.arange(len(arr)) < len(arr) - N   # full forward window available
        neu = (arr == 3) & valid & mask
        p = hit[neu].mean() * 100
        print(f"  N={N:3d}: P = {p:5.1f}%   (n NEUTRAL obs = {neu.sum()})")
# episode count context
trans = (s["state"] != s["state"].shift()).cumsum()
ep = s.groupby(trans)["state"].first()
print(f"\ntransitions total: {len(ep)-1} | current run: state={arr[-1]} "
      f"({(trans == trans.iloc[-1]).sum()} sessions ending {s['time'].iloc[-1].date()})")
