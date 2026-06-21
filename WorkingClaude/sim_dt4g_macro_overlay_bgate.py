# -*- coding: utf-8 -*-
"""
sim_dt4g_macro_overlay_bgate.py  —  DT5G breadth-gate validation (research)
===============================
Validates the VN-breadth decoupling guard now folded into DT5G (canonical
sim_dt4g_macro_overlay.py). Kept as the standalone validation harness.
EXACT COPY of the canonical sim_dt4g_macro_overlay.py harness (same BQ data, same
build_weight, same simulate, same costs/deposit, same macro fusion) + an optional
VN-BREADTH GATE on Pillar B (US panic). Purpose: validate the breadth gate on the
SAME config that produces the canonical DT5G figure (nav_base 19.17% / nav_macro
20.10% / 113.3B), so results are directly comparable.

Sanity: with the gate OFF, nav_macro MUST reproduce 20.10% (proves harness identity).

Breadth gate: a US-driven cap (Pillar B) binds ONLY if Breadth_MA200 is valid
(universe >= 100 stocks) AND < 0.50 (shift 1, causal). SBV pillar (A) + bull-bypass
unchanged. Output: data/dt4g_macro_bgate_nav.csv + console comparison (does NOT
overwrite the canonical data/dt4g_macro_overlay_nav.csv).
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
DATADIR = os.path.join(WORKDIR, "data")
from simulate_holistic_nav import bq
from sbv_macro_overlay import SBV_REFI_EVENTS

STATE_ALLOC = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
TC, TAX, BORROW, INIT, RF = 0.001, 0.001, 0.10, 1_000_000_000, 0.001
NEUTRAL, CRISIS, BEAR = 3, 1, 2
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}
US_REFI_LAG = 5
T_DOM_MILD, T_DOM_STRONG, T_DOM_EXTREME = 0.5, 1.5, 3.0
REFI_CUT_FROM_PEAK = 0.5
CAP_COMMIT = 7
BREADTH_FILE = r"/home/trido/thanhdt/WorkingClaude/data/preprocess_others_market_indicators_all_tickers.csv"
BREADTH_TH = 0.50
BREADTH_MIN_UNIVERSE = 100

# ── 1. data (IDENTICAL to canonical) ──
print("[1] BQ VNINDEX + dt_4gate state + MA200/RSI; US; SBV; breadth...")
px = bq("""SELECT p.time, p.Close, p.MA200, p.D_RSI, s.state FROM tav2_bq.ticker AS p
JOIN tav2_bq.vnindex_5state_dt_4gate AS s ON s.time=p.time
WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"]); px["state"] = px["state"].astype(int)
px = px.dropna(subset=["Close", "state"]).sort_values("time").reset_index(drop=True)
us = pd.read_csv("data/us_market_history.csv", parse_dates=["time"]).sort_values("time")
key = px[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time": "us_time"}),
                   left_on="jt", right_on="us_time", direction="backward").sort_values("time").reset_index(drop=True)
px = px.merge(um[["time", "vix", "spx_dd_1y", "vix_ma252"]], on="time", how="left")
ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev["time"])
dr = pd.DataFrame({"time": pd.date_range(px["time"].min(), px["time"].max(), freq="D")}).merge(ev, on="time", how="left")
dr["refi"] = dr["refi"].ffill().bfill()
px = px.merge(dr, on="time", how="left"); px["refi"] = px["refi"].ffill().bfill()
px["refi_chg6m"] = (px["refi"] - px["refi"].shift(126)).shift(US_REFI_LAG)
px["refi_peak6m"] = px["refi"].rolling(126, min_periods=20).max()
px["refi_cut"] = ((px["refi_peak6m"] - px["refi"]) >= REFI_CUT_FROM_PEAK).shift(US_REFI_LAG).fillna(False)
px["vni_r6m"] = px["Close"] / px["Close"].shift(126) - 1
px["bull"] = ((px["vni_r6m"] > 0.15) & (px["Close"] > px["MA200"])).shift(1).fillna(False)
# breadth merge (T-aligned backward) + causal confirm
bd = pd.read_csv(BREADTH_FILE); bd["time"] = pd.to_datetime(bd["time"])
bd = bd[["time", "Breadth_MA200", "Breadth_Total_MA200"]].sort_values("time")
px = pd.merge_asof(px.sort_values("time"), bd, on="time", direction="backward").sort_values("time").reset_index(drop=True)
# PRODUCTION-SAFE semantics: suppress the US cap ONLY on POSITIVE decoupling evidence
# (breadth valid universe>=100 AND HEALTHY >= TH). Missing/weak/small-universe breadth
# => NO suppression => US cap fires (never miss crisis protection on a data gap). Causal (shift 1).
b_valid = (px["Breadth_Total_MA200"].fillna(0) >= BREADTH_MIN_UNIVERSE)
px["us_decoupled"] = (b_valid & (px["Breadth_MA200"] >= BREADTH_TH)).shift(1).fillna(False)
print(f"  {len(px):,} rows {px['time'].iloc[0].date()}->{px['time'].iloc[-1].date()}  bull {int(px['bull'].sum())}d")

# ── 2. macro signal (canonical + optional breadth gate on Pillar B) ──
def macro_signal(d, bgate=False):
    n = len(d)
    vix = d["vix"].values; sdd = d["spx_dd_1y"].values; vixma = d["vix_ma252"].values
    rc6 = d["refi_chg6m"].values; cut = d["refi_cut"].values.astype(bool)
    bull = d["bull"].values.astype(bool); decoup = d["us_decoupled"].values.astype(bool)
    cap = np.full(n, 9); easing = np.zeros(n, bool); src = np.array([""] * n, dtype=object)
    for t in range(n):
        v, dd, vm, rr = vix[t], sdd[t], vixma[t], rc6[t]
        us_allowed = (not bull[t]) and ((not bgate) or (not decoup[t]))   # <-- breadth gate: suppress US only on decoupling
        if not us_allowed:
            us_crisis = us_bear = us_mild = False
        else:
            us_crisis = (not np.isnan(dd) and dd < -0.25) or (not np.isnan(v) and v > 35)
            us_bear   = (not np.isnan(dd) and dd < -0.15) and (not np.isnan(v) and v > 25)
            us_mild   = (not np.isnan(dd) and dd < -0.10) and (not np.isnan(v) and v > 20)
        dom_ext = (not np.isnan(rr) and rr >= T_DOM_EXTREME); dom_str = (not np.isnan(rr) and rr >= T_DOM_STRONG)
        dom_mild = (not np.isnan(rr) and rr >= T_DOM_MILD)
        if us_crisis or dom_ext: cap[t] = CRISIS; src[t] = "US-crisis" if us_crisis else "SBV-tighten-extreme"
        elif us_bear or dom_str: cap[t] = BEAR; src[t] = "US-bear" if us_bear else "SBV-tighten-strong"
        elif us_mild or dom_mild: cap[t] = NEUTRAL; src[t] = "US-mild" if us_mild else "SBV-tighten-mild"
        us_calm = (not np.isnan(v) and not np.isnan(vm) and v < vm) and (not np.isnan(dd) and dd > -0.05)
        if cap[t] == 9 and cut[t] and us_calm: easing[t] = True; src[t] = "SBV-cut+US-calm"
    close = d["Close"].values; persist = np.zeros(n, int)
    for t in range(n): persist[t] = persist[t-1] + 1 if (t > 0 and easing[t]) else (1 if easing[t] else 0)
    price_up = np.zeros(n, bool); price_up[10:] = close[10:] > close[:-10]
    easing_conf = easing & (persist >= 10) & price_up
    return cap, easing, easing_conf, src

def _commit_cap(arr, K):
    if K <= 1: return arr.copy()
    out = arr.copy(); c = arr[0]; ps, pr = arr[0], 1
    for t in range(1, len(arr)):
        if arr[t] == ps: pr += 1
        else: ps, pr = arr[t], 1
        if pr >= K: c = ps
        out[t] = c
    return out

# ── 3. build_weight + simulate (IDENTICAL to canonical) ──
def build_weight(d, trend=True, confirm=10):
    n = len(d); st = d["state"].values.astype(int)
    close = d["Close"].values; ma200 = d["MA200"].values; rsi = d["D_RSI"].values
    w = np.array([STATE_ALLOC[s] for s in st], float)
    if trend:
        up_raw = (close > ma200) & (~np.isnan(ma200)) & (np.nan_to_num(rsi, nan=0.0) <= 0.72)
        up = np.zeros(n, bool); curf = False; ru = rd = 0
        for t in range(n):
            if up_raw[t]: ru += 1; rd = 0
            else: rd += 1; ru = 0
            if not curf and ru >= confirm: curf = True
            elif curf and rd >= confirm: curf = False
            up[t] = curf
        w[(st == NEUTRAL) & up] = 0.90
    return w

def simulate(d, cap, easing_conf, use_macro=False):
    n = len(d); close = d["Close"].values
    r = np.zeros(n); r[1:] = close[1:] / close[:-1] - 1
    yrs = (d["time"].iloc[-1] - d["time"].iloc[0]).days / 365.25; spy = n / yrs
    tgt = build_weight(d)
    if use_macro:
        ceil = np.where(cap == 9, 1.30, np.array([STATE_ALLOC.get(c, 1.30) for c in cap]))
        tgt = np.minimum(tgt, ceil)
        tgt = np.where(easing_conf & (tgt < 0.70), 0.70, tgt)
    tgt_lag = np.concatenate([[0.0], tgt[:-1]])
    ya = d["time"].dt.year.values; dep = np.array([VGB_1Y.get(int(y), 0.001) for y in ya])
    nav = np.empty(n); nav[0] = INIT; dd = np.zeros(n); held = tgt_lag
    for t in range(n):
        w = held[t]; wp = held[t-1] if t > 0 else 0.0
        cf = max(0.0, 1 - w); lf = max(0.0, w - 1); buy = max(0.0, w - wp); sell = max(0.0, wp - w)
        dd[t] = w * r[t] + cf * dep[t] / spy - lf * BORROW / spy - (buy + sell) * TC - sell * TAX
        if t > 0: nav[t] = nav[t-1] * (1 + dd[t])
    out = d[["time", "Close", "state"]].copy(); out["w"] = held; out["nav"] = nav; out["ret"] = dd
    return out, spy

def metrics(nv, time, ret, spy):
    nv = np.asarray(nv, float); time = pd.DatetimeIndex(time)
    yrs = (time[-1] - time[0]).days / 365.25; cagr = (nv[-1] / nv[0]) ** (1 / yrs) - 1
    ex = np.asarray(ret) - RF / spy; sh = ex.mean() / ex.std() * np.sqrt(spy) if ex.std() > 0 else 0
    mdd = ((nv - np.maximum.accumulate(nv)) / np.maximum.accumulate(nv)).min()
    return dict(cagr=cagr*100, sharpe=sh, mdd=mdd*100, calmar=cagr/-mdd if mdd<0 else 0, final=nv[-1]/1e9)
def sub(out, spy, a, b):
    s = out[(out["time"] >= a) & (out["time"] <= b)].reset_index(drop=True)
    if len(s) < 20: return None
    nv = INIT * s["nav"].values / s["nav"].values[0]
    return metrics(nv, s["time"], s["ret"].values, spy)

# ── 4. run base / macro / macro+gate ──
cap0, _, ez0, _ = macro_signal(px, bgate=False); cap0 = _commit_cap(cap0, CAP_COMMIT)
capg, _, ezg, _ = macro_signal(px, bgate=True);  capg = _commit_cap(capg, CAP_COMMIT)
base, spy = simulate(px, cap0, ez0, use_macro=False)
mac,  _   = simulate(px, cap0, ez0, use_macro=True)    # canonical DT5G (no gate)
macg, _   = simulate(px, capg, ezg, use_macro=True)    # DT5G + breadth gate

pd.DataFrame({"time": base["time"], "nav_base": base["nav"], "nav_macro": mac["nav"],
              "nav_macro_bgate": macg["nav"]}).to_csv(os.path.join(DATADIR, "dt4g_macro_bgate_nav.csv"), index=False)

PERIODS = {"FULL 2000-now": (px["time"].min(), px["time"].max()),
           "2003+ (drop nascent)": (pd.Timestamp("2003-01-01"), px["time"].max()),
           "Pre-2014": (pd.Timestamp("2000-01-01"), pd.Timestamp("2013-12-31")),
           "Modern 2014-now": (pd.Timestamp("2014-01-01"), px["time"].max()),
           "2007-08 GFC": (pd.Timestamp("2007-01-01"), pd.Timestamp("2009-03-31")),
           "2011 inflation": (pd.Timestamp("2011-01-01"), pd.Timestamp("2012-06-30")),
           "COVID 2020": (pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")),
           "2022 hikes": (pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"))}
mfull_b = metrics(base["nav"].values, base["time"], base["ret"].values, spy)
mfull_m = metrics(mac["nav"].values, mac["time"], mac["ret"].values, spy)
mfull_g = metrics(macg["nav"].values, macg["time"], macg["ret"].values, spy)
print("\n" + "="*96)
print("  HARNESS-IDENTITY CHECK (gate OFF must = canonical 20.10% / 113.3B):")
print(f"    nav_base  CAGR {mfull_b['cagr']:.2f}%  final {mfull_b['final']:.1f}B   (canonical 19.17% / 92.7B)")
print(f"    nav_macro CAGR {mfull_m['cagr']:.2f}%  final {mfull_m['final']:.1f}B   (canonical 20.10% / 113.3B)")
print(f"    nav_macro+GATE CAGR {mfull_g['cagr']:.2f}%  final {mfull_g['final']:.1f}B")
print("="*96)
print(f"  {'Period':<22}{'DT4(base)':>11}{'DT5G':>10}{'DT5G+GATE':>11}{'Δgate':>8}{'gDD':>9}")
for name, (a, b) in PERIODS.items():
    mb = sub(base, spy, a, b); mm = sub(mac, spy, a, b); mg = sub(macg, spy, a, b)
    if not (mb and mm and mg): continue
    print(f"  {name:<22}{mb['cagr']:>+10.2f}%{mm['cagr']:>+9.2f}%{mg['cagr']:>+10.2f}%{mg['cagr']-mm['cagr']:>+7.2f}{mg['mdd']:>+8.1f}%")
# episode counts
def n_us_episodes(cap):
    capped = cap != 9; cnt = 0
    for t in range(len(cap)):
        if capped[t] and (t == 0 or not capped[t-1]): cnt += 1
    return cnt
print("="*96)
print(f"  US/SBV cap episodes — DT5G no-gate: {n_us_episodes(cap0)} | DT5G+gate: {n_us_episodes(capg)}")
print(f"  cap-days   no-gate: {int((cap0!=9).sum())} | gate: {int((capg!=9).sum())}")
print("  Saved: data/dt4g_macro_bgate_nav.csv")
print("DONE.")
