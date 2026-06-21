# -*- coding: utf-8 -*-
"""Leading-IC + event study of CROSS-SECTIONAL DISPERSION & AVERAGE CORRELATION as a
stress-regime signal (research-only). Hypothesis: rising avg pairwise correlation
(everything moves together) = stress -> lower forward returns; low dispersion = same.
Universe = ticker_prune (2014+). avg-corr proxy: rho ~ (sigma_p^2/avg_var - 1/N)/(1-1/N)
over a rolling window (sigma_p = EW-portfolio vol, avg_var = mean single-stock var).
All features causal (trailing window, lagged 1d). NO deploy."""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq

print("[1] pull ticker_prune closes (2014+)...")
raw = bq("""SELECT t.time, t.ticker, t.Close FROM tav2_bq.ticker_prune AS t
WHERE t.Close IS NOT NULL AND t.time>=DATE '2014-01-01' ORDER BY t.time""")
raw["time"] = pd.to_datetime(raw["time"])
mat = raw.pivot_table(index="time", columns="ticker", values="Close").sort_index()
ret = mat.pct_change()
ret = ret.clip(-0.5, 0.5)   # guard splits/garbage
n = len(ret)
print(f"  {n} sessions, {mat.shape[1]} tickers, {ret.index[0].date()}->{ret.index[-1].date()}")

# daily cross-sectional dispersion (std across tickers), require >=100 names
valid = ret.notna().sum(axis=1)
xsec_disp = ret.std(axis=1).where(valid >= 100)
ew = ret.mean(axis=1).where(valid >= 100)   # equal-weight portfolio daily return

W = 20
sigma_p = ew.rolling(W, min_periods=15).std()
# avg single-stock variance over window: mean across tickers of rolling var
var_i = ret.rolling(W, min_periods=15).var()
avg_var = var_i.mean(axis=1)
N_eff = valid.clip(lower=1)
with np.errstate(divide="ignore", invalid="ignore"):
    rho = (sigma_p**2 / avg_var - 1.0/N_eff) / (1.0 - 1.0/N_eff)
rho = rho.clip(0, 1)
disp_ma = xsec_disp.rolling(W, min_periods=15).mean()

d = pd.DataFrame({"time": ret.index, "rho": rho.values, "disp": disp_ma.values}).reset_index(drop=True)
d["rho_chg20"] = d["rho"].diff(20); d["disp_chg20"] = d["disp"].diff(20)

# VNINDEX forward returns
px = bq("""SELECT p.time, p.Close FROM tav2_bq.ticker AS p WHERE p.ticker='VNINDEX' AND p.time>=DATE '2014-01-01' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"]); px = px.sort_values("time").reset_index(drop=True)
c = px["Close"].values; m = len(px)
fwd = {}
for h in (20, 60, 120):
    o = np.full(m, np.nan); o[:m-h] = c[h:]/c[:m-h]-1; fwd[f"f{h}"] = o
px = px.assign(**fwd)
d = d.merge(px, on="time", how="inner")
for col in ["rho", "disp", "rho_chg20", "disp_chg20"]:
    d[col+"_L"] = d[col].shift(1)   # causal

def ic(x, y):
    s = pd.concat([x, y], axis=1).dropna(); return s.corr("spearman").iloc[0,1] if len(s) > 50 else np.nan
print("\n[2] Leading IC (Spearman, causal feature vs forward VNINDEX return)")
print(f"  {'feature':18s}{'f20':>9s}{'f60':>9s}{'f120':>9s}")
for col, desc in [("rho_L","avg corr level"), ("rho_chg20_L","avg corr chg20"),
                  ("disp_L","dispersion level"), ("disp_chg20_L","dispersion chg20")]:
    print(f"  {desc:18s}" + "".join(f"{ic(d[col], d[f'f{h}']):>9.3f}" for h in (20,60,120)))

print("\n[3] Forward return conditioned on CORRELATION level (quintiles of rho_L)")
dd = d.dropna(subset=["rho_L","f60","f120"]).copy()
dd["q"] = pd.qcut(dd["rho_L"], 5, labels=False, duplicates="drop")
for q in sorted(dd["q"].dropna().unique()):
    g = dd[dd["q"]==q]; lo, hi = g["rho_L"].min(), g["rho_L"].max()
    print(f"  Q{int(q)+1} rho[{lo:.2f}-{hi:.2f}] n={len(g):4d}  fwd60 {g['f60'].mean()*100:+5.1f}%  fwd120 {g['f120'].mean()*100:+5.1f}%  P(f60<0) {(g['f60']<0).mean()*100:.0f}%")

print("\n[4] CORRELATION SPIKE event (rho_L high AND rising) — stress trigger")
hi_rho = dd["rho_L"] > dd["rho_L"].quantile(0.80)
rising = dd["rho_chg20_L"] > 0
for lbl, g in [("rho top20% & rising", dd[hi_rho & rising]),
               ("rho top20% (any)", dd[hi_rho]),
               ("baseline all", dd)]:
    if len(g) < 20: continue
    print(f"  {lbl:22s} n={len(g):4d}  fwd60 {g['f60'].mean()*100:+5.1f}%  fwd120 {g['f120'].mean()*100:+5.1f}%  P(f60<0) {(g['f60']<0).mean()*100:.0f}%")
print("\nDONE.")
