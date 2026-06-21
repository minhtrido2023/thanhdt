# -*- coding: utf-8 -*-
"""
sweep_ew_liq_threshold.py
=========================
Settle the trading-value / EW-liquidity-gate question definitively.
Sweeps the EW-universe liquidity threshold LIQ_MIN on the REAL (Price) tv gate, rebuilds the
ew_v1 5-state for each, and scores each config on 3 axes (user objective = balanced):
  (1) State predictive quality  — monotonicity of forward VNINDEX T+5/T+20/T+60 return by state
  (2) Risk-adjusted NAV         — pure-index alloc (1B, dep 0%, borrow 10%) on the ew-state
  (3) Stability                 — transitions + universe-size stability (CV)
Also runs the current production config (Close, 500M) as the reference row.

Phase-1 (ew_v1 level, fast via cache). Pick 1-2 winners → then full chain + integrated V4/V5.
Output: data/sweep_ew_liq_threshold.md
"""
import sys, io, os, subprocess
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)

PY = sys.executable
STATE_ALLOC = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.3}
INIT, BORROW, DEPOSIT, TC, TAX = 1_000_000_000, 0.10, 0.0, 0.001, 0.001

# configs: (label, tv_price, liq_min, topn)
CONFIGS = [
    ("Close 500M (PROD)", "0", 5e8, 0),
    ("Price 100M",        "1", 1e8, 0),
    ("Price 250M",        "1", 2.5e8, 0),
    ("Price 500M",        "1", 5e8, 0),
    ("Price 1B",          "1", 1e9, 0),
    ("Price 2B",          "1", 2e9, 0),
    ("Price 5B",          "1", 5e9, 0),
    ("TopN 50",           "1", 0, 50),
    ("TopN 100",          "1", 0, 100),
    ("TopN 150",          "1", 0, 150),
    ("TopN 200",          "1", 0, 200),
]

def run_ewv1(tv_price, liq_min, tag, topn=0):
    env = dict(os.environ)
    env["TV_PRICE"] = tv_price; env["LIQ_MIN"] = str(liq_min); env["OUT_TAG"] = tag; env["TOPN"] = str(topn)
    r = subprocess.run([PY, "vnindex_5state_ew_v1.py"], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [FAIL] {tag}\n{r.stderr[-800:]}"); return None
    return pd.read_csv(os.path.join(WORKDIR, f"vnindex_5state_ew_full{tag}.csv"), parse_dates=["time"])

# VNINDEX forward returns (the regime we predict / trade)
vni = pd.read_csv("VNINDEX.csv", usecols=["time","Close"]); vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for h in (5,20,60):
    vni[f"fwd{h}"] = vni["Close"].shift(-h)/vni["Close"] - 1
vni["r1"] = vni["Close"]/vni["Close"].shift(1) - 1

def monotonicity(state, fwd):
    """Spearman-like: corr between state rank (1..5) and mean forward return per state."""
    d = pd.DataFrame({"s":state, "f":fwd}).dropna()
    m = d.groupby("s")["f"].mean()
    if len(m) < 3: return np.nan, m
    # rank correlation between ordered states present and their mean fwd
    s_vals = m.index.values.astype(float); f_vals = m.values
    return np.corrcoef(s_vals, f_vals)[0,1], m

def nav_metrics(df_state):
    """pure-index alloc by ew-state, T+1, 1B, dep0/borrow10."""
    d = df_state[["time","state"]].merge(vni[["time","r1"]], on="time", how="inner").dropna(subset=["state"]).reset_index(drop=True)
    d = d[d["time"]>="2014-01-01"].reset_index(drop=True)
    w = d["state"].map(STATE_ALLOC).astype(float).values
    wl = np.concatenate([[0.0], w[:-1]])   # T+1
    r = d["r1"].values; n = len(d)
    spy = n / ((d["time"].iloc[-1]-d["time"].iloc[0]).days/365.25)
    nav = np.empty(n); nav[0]=INIT; ret=np.zeros(n)
    for t in range(1,n):
        ww=wl[t]; wp=wl[t-1]; cf=max(0,1-ww); lf=max(0,ww-1); tr=abs(ww-wp)
        ret[t]=ww*r[t]+cf*DEPOSIT/spy-lf*BORROW/spy-tr*TC-max(0,wp-ww)*TAX
        nav[t]=nav[t-1]*(1+ret[t])
    yrs=(d["time"].iloc[-1]-d["time"].iloc[0]).days/365.25
    cagr=(nav[-1]/nav[0])**(1/yrs)-1
    ex=ret[1:]; sh=ex.mean()/ex.std()*np.sqrt(spy) if ex.std()>0 else 0
    dd=((nav-np.maximum.accumulate(nav))/np.maximum.accumulate(nav)).min()
    return cagr*100, sh, dd*100, cagr/abs(dd) if dd<0 else 0

rows=[]
for label, tvp, lm, tn in CONFIGS:
    tag = "_sw_" + "".join(c for c in label.split("(")[0].strip().lower().replace(" ","_") if c.isalnum() or c=="_")
    print(f"[run] {label} (TV_PRICE={tvp}, LIQ_MIN={lm:.0f}, TOPN={tn}) ...")
    df = run_ewv1(tvp, lm, tag, tn)
    if df is None: continue
    post = df[df["time"]>="2014-01-01"].copy()
    nu = post["n_universe"].dropna()
    trans = int((post["state"].diff().fillna(0)!=0).sum())
    sm = post[["time","state"]].merge(vni, on="time", how="left")
    mono20,_ = monotonicity(sm["state"].values, sm["fwd20"].values)
    mono60,_ = monotonicity(sm["state"].values, sm["fwd60"].values)
    cagr, sh, dd, cal = nav_metrics(df)
    rows.append(dict(cfg=label, n_uni_med=nu.median(), n_uni_min=nu.min(),
                     n_uni_cv=nu.std()/nu.mean(), trans=trans, mono20=mono20, mono60=mono60,
                     cagr=cagr, sh=sh, dd=dd, cal=cal))
    print(f"    uni med={nu.median():.0f} min={nu.min():.0f} cv={nu.std()/nu.mean():.3f} | trans={trans} | "
          f"mono20={mono20:.3f} mono60={mono60:.3f} | NAV CAGR={cagr:.2f}% Sh={sh:.2f} DD={dd:.1f}%")

R = pd.DataFrame(rows)
L = ["# EW liquidity-threshold sweep (real Price tv gate) — balanced objective\n",
     "*ew_v1-level 5-state, 2014+. Pure-index NAV = STATE_ALLOC alloc, 1B, dep 0%, borrow 10%, T+1. "
     "mono = corr(state-rank, mean forward VNINDEX return); higher = sharper regime ordering. "
     "n_uni_cv = universe-size coeff-of-variation (lower = more stable basket).*\n",
     "| Config | Uni med | Uni min | Uni CV | Trans | Mono T+20 | Mono T+60 | NAV CAGR | Sharpe | MaxDD | Calmar |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for _,r in R.iterrows():
    L.append(f"| {r.cfg} | {r.n_uni_med:.0f} | {r.n_uni_min:.0f} | {r.n_uni_cv:.3f} | {int(r.trans)} | "
             f"{r.mono20:.3f} | {r.mono60:.3f} | {r.cagr:+.2f}% | {r.sh:.2f} | {r.dd:.1f}% | {r.cal:.2f} |")
open("data/sweep_ew_liq_threshold.md","w",encoding="utf-8").write("\n".join(L))
print("\nReport: data/sweep_ew_liq_threshold.md")
print(R.to_string(index=False))
