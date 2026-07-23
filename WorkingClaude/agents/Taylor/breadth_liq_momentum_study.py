# -*- coding: utf-8 -*-
"""
breadth_liq_momentum_study.py  (job Taylor_20260723_064214, BUOC 3)

Design + test a breadth-MOMENTUM + liquidity-stress CONFLUENCE gate as a candidate
EARLY de-risk signal vs DT5G (which reacts only via price, ~50-session lag).

Signals (all causal, T-1):
  S1 breadth-momentum : b_mom(N) = breadth - breadth.shift(N)  (breadth = % of ticker_prune > MA200)
  S2 liquidity-stress : turn_ratio = turnover_20d_mean / turnover_90d_mean  (<1 => draining)
  S3 price            : DT5G base de-risk proxy: Close < MA200  (already what DT5G keys on, slow)

Pre-registered grid (see bus decision, job Taylor_20260723_064214):
  b_mom_window   in {20,40}
  b_mom_bleed    in {-0.08,-0.10}
  liq_ratio_th   in {0.85,0.75}
  confluence     in {2_of_3, 3_of_3}
Primary (fixed before results): window=40, bleed=-0.10, liq<0.85, 2_of_3.
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq

# ---------- data ----------
px = bq("""SELECT t.time, t.Close, t.MA200 FROM tav2_bq.ticker t
           WHERE t.ticker='VNINDEX' AND t.time>=DATE '2013-01-01' ORDER BY t.time""")
px["time"] = pd.to_datetime(px["time"])

# breadth (recompute from ticker_prune, to 2026-07-22)
bd = bq("""SELECT t.time, AVG(IF(t.Close>t.MA200,1.0,0.0)) AS breadth, COUNT(*) AS univ
           FROM tav2_bq.ticker_prune t
           WHERE t.MA200 IS NOT NULL AND t.time>=DATE '2013-01-01'
           GROUP BY t.time ORDER BY t.time""")
bd["time"] = pd.to_datetime(bd["time"])

# turnover (liquidity)
tv = bq("""SELECT t.time, SUM(t.Volume*t.Close) AS turnover
           FROM tav2_bq.ticker_prune t
           WHERE t.time>=DATE '2013-01-01' GROUP BY t.time ORDER BY t.time""")
tv["time"] = pd.to_datetime(tv["time"])

# DT5G live state
st = bq("""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s
           WHERE s.time>=DATE '2013-01-01' ORDER BY s.time""")
st["time"] = pd.to_datetime(st["time"]); st["state"] = st["state"].astype(int)

df = px.merge(bd, on="time", how="left").merge(tv, on="time", how="left").merge(st, on="time", how="left")
df = df.sort_values("time").reset_index(drop=True)
df["breadth"] = df["breadth"].ffill()
df["univ"] = df["univ"].ffill()
df["turnover"] = df["turnover"].ffill()
df["state"] = df["state"].ffill()

# ---------- features (causal) ----------
df["b_mom20"] = (df["breadth"] - df["breadth"].shift(20)).shift(1)
df["b_mom40"] = (df["breadth"] - df["breadth"].shift(40)).shift(1)
df["turn20"] = df["turnover"].rolling(20).mean()
df["turn90"] = df["turnover"].rolling(90).mean()
df["turn_ratio"] = (df["turn20"] / df["turn90"]).shift(1)
df["below_ma200"] = (df["Close"] < df["MA200"]).shift(1).fillna(False)
# forward VNINDEX returns for signal-quality
for h in (20, 60, 120):
    df[f"fwd{h}"] = df["Close"].shift(-h) / df["Close"] - 1
df["r_fwd60"] = df["fwd60"]

def gate(window, bleed, liq_th, rule):
    s1 = df[f"b_mom{window}"] < bleed
    s2 = df["turn_ratio"] < liq_th
    s3 = df["below_ma200"]
    votes = s1.astype(int) + s2.astype(int) + s3.astype(int)
    need = 2 if rule == "2_of_3" else 3
    return (votes >= need).fillna(False), s1.fillna(False), s2.fillna(False), s3.fillna(False)

# ---------- signal-quality: forward return when gate ON vs OFF ----------
print("="*90)
print("  BREADTH-MOMENTUM + LIQUIDITY CONFLUENCE — signal quality (2014-2026, causal)")
print("="*90)
mask_period = df["time"] >= "2014-01-01"
print(f"\n[A] fwd60 VNINDEX return: gate ON vs OFF  (full grid, {int(mask_period.sum())} sessions)")
print(f"  {'window':>7}{'bleed':>7}{'liq':>6}{'rule':>8}{'ON_n':>7}{'ON_fwd60':>10}{'OFF_fwd60':>11}{'sep':>8}")
rows = []
for window in (20, 40):
    for bleed in (-0.08, -0.10):
        for liq_th in (0.85, 0.75):
            for rule in ("2_of_3", "3_of_3"):
                g, s1, s2, s3 = gate(window, bleed, liq_th, rule)
                gm = g & mask_period
                on = df.loc[gm, "fwd60"].mean()
                off = df.loc[(~g) & mask_period, "fwd60"].mean()
                rows.append((window, bleed, liq_th, rule, int(gm.sum()), on, off, on-off))
                print(f"  {window:>7}{bleed:>7.2f}{liq_th:>6.2f}{rule:>8}{int(gm.sum()):>7}"
                      f"{on*100:>9.2f}%{off*100:>10.2f}%{(on-off)*100:>7.2f}%")

# single-signal ablation
print("\n[B] single-signal ablation (fwd60 ON vs OFF, primary window=40)")
for name, sig in [("S1 breadth_mom40<-0.10", df["b_mom40"] < -0.10),
                  ("S2 turn_ratio<0.85", df["turn_ratio"] < 0.85),
                  ("S3 below_ma200", df["below_ma200"])]:
    sm = sig.fillna(False) & mask_period
    on = df.loc[sm, "fwd60"].mean(); off = df.loc[(~sig.fillna(False)) & mask_period, "fwd60"].mean()
    print(f"  {name:<26} ON_n={int(sm.sum()):>5}  ON {on*100:+.2f}%  OFF {off*100:+.2f}%  sep {(on-off)*100:+.2f}%")

# ---------- episode analysis: lead/lag vs DT5G ----------
print("\n[C] EPISODE lead/lag vs DT5G de-risk (primary spec: w40,bleed-0.10,liq0.85,2of3)")
g_primary, _, _, _ = gate(40, -0.10, 0.85, "2_of_3")
df["gate_primary"] = g_primary
# DT5G de-risk onset = state drops to <=2 (BEAR/CRISIS)
df["derisk"] = (df["state"] <= 2)
def first_true_on_or_after(series, start, end):
    seg = df[(df.time >= start) & (df.time <= end) & series]
    return seg.time.iloc[0] if len(seg) else None
episodes = [
    ("2018 selloff", "2018-03-01", "2018-08-01", True),
    ("2020 COVID", "2020-02-15", "2020-05-01", True),
    ("2022 bear", "2022-03-15", "2022-12-01", True),
    ("2025-04 tariff washout", "2025-03-15", "2025-06-01", True),
    ("2026-05 current", "2026-05-10", "2026-07-22", True),
    ("2014-09 benign dip", "2014-08-15", "2014-12-01", False),
    ("2026-01 benign dip", "2025-12-15", "2026-03-01", False),
]
print(f"  {'episode':<26}{'real?':>6}{'gate_first':>13}{'DT5G_first':>13}{'lead(days)':>11}")
for name, s, e, real in episodes:
    gf = first_true_on_or_after(df["gate_primary"], s, e)
    dd = first_true_on_or_after(df["derisk"], s, e)
    lead = ""
    if gf is not None and dd is not None:
        lead = f"{(dd - gf).days:+d}"
    elif gf is not None and dd is None:
        lead = "gate-only"
    elif gf is None and dd is not None:
        lead = "DT5G-only"
    else:
        lead = "neither"
    gfx = gf.date().isoformat() if gf is not None else "—"
    ddx = dd.date().isoformat() if dd is not None else "—"
    tag = "REAL" if real else "benign"
    print(f"  {name:<26}{tag:>6}{gfx:>13}{ddx:>13}{lead:>11}")

# ---------- false-alarm count: gate fires but no real drawdown follows ----------
print("\n[D] FALSE-ALARM audit: gate-ON episodes where fwd60 VNINDEX did NOT fall")
gm = df["gate_primary"] & mask_period
onset = df.index[df["gate_primary"].astype(int).diff() == 1]
onset = [i for i in onset if df.loc[i, "time"] >= pd.Timestamp("2014-01-01")]
fa = 0; tot = 0
for i in onset:
    f60 = df.loc[i, "fwd60"]
    if pd.isna(f60): continue
    tot += 1
    if f60 > 0.0: fa += 1
print(f"  gate onsets (2014+): {tot}  |  followed by POSITIVE fwd60 (false-alarm): {fa}  ({100*fa/max(tot,1):.0f}%)")
print(f"  mean fwd60 across all onsets: {df.loc[onset,'fwd60'].mean()*100:+.2f}%  (baseline all-days {df.loc[mask_period,'fwd60'].mean()*100:+.2f}%)")

# ---------- current status ----------
last = df.iloc[-1]
print("\n[E] CURRENT status (asof %s)" % last["time"].date())
print(f"  breadth={last['breadth']:.3f}  b_mom40={last['b_mom40']:+.3f}  b_mom20={last['b_mom20']:+.3f}")
print(f"  turn_ratio={last['turn_ratio']:.3f}  below_ma200={bool(last['below_ma200'])}  DT5G_state={int(last['state'])}")
print(f"  gate_primary ON = {bool(last['gate_primary'])}")
print("\nDONE.")

# ============================================================================
# [F] NAV market-timing OVERLAY test (weight 0 when de-risk ON) — criterion (c)
# ============================================================================
def nav_stats(ret, w, label):
    # ret = daily VNINDEX return; w = target weight (0/1), T+1 applied
    wl = pd.Series(w).shift(1).fillna(1.0).values
    r = ret.values
    tc = 0.001
    dw = np.abs(np.diff(np.concatenate([[1.0], wl])))
    pv = np.cumprod(1.0 + wl*r - dw*tc)
    d = df["time"].values
    yrs = (pd.Timestamp(d[-1]) - pd.Timestamp(d[0])).days/365.25
    cagr = pv[-1]**(1/yrs) - 1
    dr = np.diff(np.concatenate([[1.0], pv]))/np.concatenate([[1.0], pv])[:-1]
    n_per_yr = len(pv)/yrs
    sharpe = dr.mean()/dr.std()*np.sqrt(n_per_yr)
    downside = dr[dr<0].std()*np.sqrt(n_per_yr)
    sortino = dr.mean()*n_per_yr/downside if downside>0 else np.nan
    peak = np.maximum.accumulate(pv); dd = (pv/peak-1).min()
    calmar = cagr/abs(dd) if dd<0 else np.nan
    print(f"  {label:<30} CAGR {cagr*100:6.2f}%  Sharpe {sharpe:4.2f}  Sortino {sortino:4.2f}  MaxDD {dd*100:6.1f}%  Calmar {calmar:4.2f}")
    return cagr, sharpe, dd, calmar

sub = df[df["time"] >= "2014-01-01"].reset_index(drop=True)
ret = sub["Close"].pct_change().fillna(0.0)
print("\n[F] NAV market-timing overlay (VNINDEX proxy, weight->0 when signal ON, TC=0.1%, 2014-2026)")
nav_stats(ret, np.ones(len(sub)), "Buy&Hold VNINDEX")
# confluence primary
gP,_ ,_,_ = None,None,None,None
def gate_sub(window, bleed, liq_th, rule, d2):
    s1 = d2[f"b_mom{window}"] < bleed
    s2 = d2["turn_ratio"] < liq_th
    s3 = d2["below_ma200"]
    votes = s1.astype(int)+s2.astype(int)+s3.astype(int)
    need = 2 if rule=="2_of_3" else 3
    return (votes>=need).fillna(False)
w_conf = np.where(gate_sub(40,-0.10,0.85,"2_of_3",sub), 0.0, 1.0)
nav_stats(ret, w_conf, "Confluence 2of3 (primary)")
w_s1 = np.where((sub["b_mom40"]<-0.10).fillna(False), 0.0, 1.0)
nav_stats(ret, w_s1, "S1 breadth-mom only")
w_s2 = np.where((sub["turn_ratio"]<0.85).fillna(False), 0.0, 1.0)
nav_stats(ret, w_s2, "S2 liquidity-stress only")
w_s3 = np.where(sub["below_ma200"].fillna(False), 0.0, 1.0)
nav_stats(ret, w_s3, "S3 below_ma200 only")
# DT5G de-risk overlay as reference
w_dt = np.where(sub["state"]<=2, 0.0, 1.0)
nav_stats(ret, w_dt, "DT5G de-risk (state<=2) ref")
# S2 + DT5G confluence (both must agree to de-risk? or either)
w_s2dt = np.where((sub["turn_ratio"]<0.85).fillna(False) | (sub["state"]<=2), 0.0, 1.0)
nav_stats(ret, w_s2dt, "S2 OR DT5G (either de-risk)")
print("\nDONE-F.")
