# -*- coding: utf-8 -*-
"""
tune_macro_smoothing.py
=======================
Fix macro-overlay whipsaw: the DEFENSIVE cap reacts instantly (caps when VIX/SPX
cross a threshold, releases the moment they cross back) -> flicker in choppy
months (e.g. Apr-2025 Trump-tariff VIX oscillation = ~10 meaningless transitions).

Fix (DT4 philosophy, causal): add a CONFIRMATION DWELL to the cap — a new cap
level must persist K sessions before it commits (debounces both tighten & release).
Real crises persist for weeks so protection is kept; 1-3 day blips are absorbed.

Tests cap-commit K in {0(base),3,5,7,10} on the recommended pure-index config.
Reports: transitions (full + Apr-2025), Full/2011/2014 CAGR, crisis windows
(2008/2011/2020/2022). Target: transitions close to DT4-only (~93) while keeping
the validated crisis alpha. Output: data/tune_macro_smoothing.md
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
DATADIR = os.path.join(WORKDIR, "data")
from simulate_holistic_nav import bq
from sbv_macro_overlay import SBV_REFI_EVENTS

STATE_ALLOC = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}
TC, TAX, BORROW, INIT, RF = 0.001, 0.001, 0.10, 1_000_000_000, 0.001
NEUTRAL, CRISIS, BEAR = 3, 1, 2
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}

print("[1] data...")
px = bq("""SELECT p.time,p.Close,p.MA200,p.D_RSI,s.state FROM tav2_bq.ticker AS p
JOIN tav2_bq.vnindex_5state_dt_4gate AS s ON s.time=p.time
WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"]); px["state"] = px["state"].astype(int)
px = px.dropna(subset=["Close", "state"]).reset_index(drop=True)
us = pd.read_csv("data/us_market_history.csv", parse_dates=["time"]).sort_values("time")
key = px[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time": "us_time"}),
                   left_on="jt", right_on="us_time", direction="backward").sort_values("time").reset_index(drop=True)
px = px.merge(um[["time", "vix", "spx_dd_1y", "vix_ma252"]], on="time", how="left")
ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev["time"])
dr = pd.DataFrame({"time": pd.date_range(px["time"].min(), px["time"].max(), freq="D")}).merge(ev, on="time", how="left")
dr["refi"] = dr["refi"].ffill().bfill()
px = px.merge(dr, on="time", how="left"); px["refi"] = px["refi"].ffill().bfill()
px["refi_chg6m"] = (px["refi"] - px["refi"].shift(126)).shift(5)
px["refi_cut"] = ((px["refi"].rolling(126, min_periods=20).max() - px["refi"]) >= 0.5).shift(5).fillna(False)
px["bull"] = ((px["Close"] / px["Close"].shift(126) - 1 > 0.15) & (px["Close"] > px["MA200"])).shift(1).fillna(False)
N = len(px)


def raw_cap_easing():
    vix = px["vix"].values; sdd = px["spx_dd_1y"].values; vma = px["vix_ma252"].values
    rc6 = px["refi_chg6m"].values; cut = px["refi_cut"].values.astype(bool); bull = px["bull"].values.astype(bool)
    cap = np.full(N, 9); easing = np.zeros(N, bool)
    for t in range(N):
        v, dd, vm, rr = vix[t], sdd[t], vma[t], rc6[t]
        if bull[t]: uc = ub = um_ = False
        else:
            uc = (not np.isnan(dd) and dd < -0.25) or (not np.isnan(v) and v > 35)
            ub = (not np.isnan(dd) and dd < -0.15) and (not np.isnan(v) and v > 25)
            um_ = (not np.isnan(dd) and dd < -0.10) and (not np.isnan(v) and v > 20)
        de = (not np.isnan(rr) and rr >= 3.0); ds = (not np.isnan(rr) and rr >= 1.5); dm = (not np.isnan(rr) and rr >= 0.5)
        if uc or de: cap[t] = CRISIS
        elif ub or ds: cap[t] = BEAR
        elif um_ or dm: cap[t] = NEUTRAL
        calm = (not np.isnan(v) and not np.isnan(vm) and v < vm) and (not np.isnan(dd) and dd > -0.05)
        if cap[t] == 9 and cut[t] and calm: easing[t] = True
    return cap, easing


def commit(arr, K):
    """Causal dwell: a new value must persist K sessions before it commits."""
    if K <= 1: return arr.copy()
    out = arr.copy(); c = arr[0]; ps, pr = arr[0], 1
    for t in range(1, len(arr)):
        if arr[t] == ps: pr += 1
        else: ps, pr = arr[t], 1
        if pr >= K: c = ps
        out[t] = c
    return out


RAWCAP, EASING = raw_cap_easing()
# confirmed easing (already validated): persist>=10 + price up
persist = np.zeros(N, int)
for t in range(N): persist[t] = persist[t-1] + 1 if (t > 0 and EASING[t]) else (1 if EASING[t] else 0)
pup = np.zeros(N, bool); pup[10:] = px["Close"].values[10:] > px["Close"].values[:-10]
EZ = EASING & (persist >= 10) & pup


def build_w(state):
    close = px["Close"].values; ma200 = px["MA200"].values; rsi = px["D_RSI"].values
    w = np.array([STATE_ALLOC[s] for s in state], float)
    up_raw = (close > ma200) & (~np.isnan(ma200)) & (np.nan_to_num(rsi, nan=0.0) <= 0.72)
    up = np.zeros(N, bool); cf = False; ru = rd = 0
    for t in range(N):
        if up_raw[t]: ru += 1; rd = 0
        else: rd += 1; ru = 0
        if not cf and ru >= 10: cf = True
        elif cf and rd >= 10: cf = False
        up[t] = cf
    w[(state == NEUTRAL) & up] = 0.90
    return w


def macro_state(cap_K):
    cap = commit(RAWCAP, cap_K)
    st = px["state"].values.astype(int)
    sm = np.where(cap != 9, np.minimum(st, cap), st)
    sm = np.where((cap == 9) & EZ & (sm < NEUTRAL), NEUTRAL, sm).astype(int)
    return sm


def sim(state):
    close = px["Close"].values; r = np.zeros(N); r[1:] = close[1:] / close[:-1] - 1
    tgt = build_w(state); tgt_lag = np.concatenate([[0.0], tgt[:-1]])
    yr = px["time"].dt.year.values; dep = np.array([VGB_1Y.get(int(y), 0.001) for y in yr])
    yrs = (px["time"].iloc[-1] - px["time"].iloc[0]).days / 365.25; spy = N / yrs
    nav = np.empty(N); nav[0] = INIT; dret = np.zeros(N)
    for t in range(N):
        w = tgt_lag[t]; wp = tgt_lag[t-1] if t > 0 else 0.0
        cf = max(0.0, 1 - w); lf = max(0.0, w - 1); buy = max(0.0, w - wp); sell = max(0.0, wp - w)
        dret[t] = w * r[t] + cf * dep[t] / spy - lf * BORROW / spy - (buy + sell) * TC - sell * TAX
        if t > 0: nav[t] = nav[t-1] * (1 + dret[t])
    return pd.DataFrame({"time": px["time"], "nav": nav, "ret": dret, "state": state}), spy


def met(o, spy, a=None, b=None):
    s = o if a is None else o[(o["time"] >= a) & (o["time"] <= b)].reset_index(drop=True)
    if len(s) < 20: return None
    nv = INIT * s["nav"].values / s["nav"].values[0]
    t = pd.DatetimeIndex(s["time"]); yrs = (t[-1] - t[0]).days / 365.25
    cagr = (nv[-1] / nv[0]) ** (1 / yrs) - 1; ex = s["ret"].values - RF / spy
    sh = ex.mean() / ex.std() * np.sqrt(spy) if ex.std() > 0 else 0
    dd = ((nv - np.maximum.accumulate(nv)) / np.maximum.accumulate(nv)).min()
    return dict(cagr=cagr * 100, sharpe=sh, dd=dd * 100)


def ntrans(state, a=None, b=None):
    s = pd.Series(state, index=px["time"])
    if a: s = s[(s.index >= a) & (s.index <= b)]
    v = s.values
    return int((v[1:] != v[:-1]).sum())


# DT4-only reference
dt_state = px["state"].values.astype(int)
o_dt, spy = sim(dt_state)
APR = (pd.Timestamp("2025-04-01"), pd.Timestamp("2025-04-30"))
MOD = (pd.Timestamp("2014-01-01"), px["time"].iloc[-1])

print("[2] testing cap-commit K...")
variants = [("DT4-only (ref)", None)] + [(f"macro cap_K={k}", k) for k in [0, 3, 5, 7, 10]]
rows = []
for name, k in variants:
    state = dt_state if k is None else macro_state(k)
    o, _ = sim(state)
    rows.append(dict(name=name,
                     tr=ntrans(state), tr_apr=ntrans(state, *APR),
                     full=met(o, spy), mod=met(o, spy, *MOD),
                     y08=met(o, spy, pd.Timestamp("2007-01-01"), pd.Timestamp("2009-03-31")),
                     y11=met(o, spy, pd.Timestamp("2011-01-01"), pd.Timestamp("2012-06-30")),
                     y20=met(o, spy, pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")),
                     y22=met(o, spy, pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"))))
    print(f"  {name:<18} trans={rows[-1]['tr']:>4} (Apr25={rows[-1]['tr_apr']})  "
          f"Full {rows[-1]['full']['cagr']:+.2f}%  Mod {rows[-1]['mod']['cagr']:+.2f}%  "
          f"2011 {rows[-1]['y11']['cagr']:+.2f}%/{rows[-1]['y11']['dd']:.0f}%")

# Apr-2025 transition detail for base macro (k=0) vs cap_K=5
print("\n[3] Apr-2025 transition detail:")
for k in [0, 5]:
    s = macro_state(k); ser = pd.Series(s, index=px["time"])
    apr = ser[(ser.index >= APR[0]) & (ser.index <= APR[1])]
    chg = apr[apr != apr.shift(1)]
    print(f"  cap_K={k}: {ntrans(s, *APR)} transitions in Apr-2025 -> states {list(apr.values)}")

L = ["# Macro Overlay — transition smoothing (cap confirmation dwell)\n",
     "*Pure-index recommended config. DEFENSIVE cap now needs K sessions to commit "
     "(causal, debounces tighten+release). Target: transitions ~ DT4-only (smooth) while "
     "keeping crisis alpha.*\n",
     "| Variant | Trans (full) | Apr-2025 | Full CAGR | Modern | 2008 | 2011 (DD) | 2020 | 2022 |",
     "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['name']} | {r['tr']} | {r['tr_apr']} | {r['full']['cagr']:+.2f}% | "
             f"{r['mod']['cagr']:+.2f}% | {r['y08']['cagr']:+.2f}% | "
             f"{r['y11']['cagr']:+.2f}% ({r['y11']['dd']:.0f}%) | {r['y20']['cagr']:+.2f}% | {r['y22']['cagr']:+.2f}% |")
L.append("\n*DT4-only is the smoothness reference. Pick the smallest K that brings Apr-2025 "
         "flicker to ~0-1 and total transitions near DT4 while preserving 2011/2022 crisis protection.*\n")
with open(os.path.join(DATADIR, "tune_macro_smoothing.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("\n  Report: data/tune_macro_smoothing.md")
print("DONE.")
