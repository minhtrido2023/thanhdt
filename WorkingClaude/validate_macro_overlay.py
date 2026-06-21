# -*- coding: utf-8 -*-
"""
validate_macro_overlay.py
=========================
Robustness validation of the consolidated macro overlay (step 1).
Anti-overfit checks on the FAST pure-index sim:
  A. Parameter sensitivity (one-at-a-time): vary US/SBV thresholds, easing confirm
     dwell, price-confirm lookback, refi lag, bull-bypass on/off. Alpha must be a
     PLATEAU (robust) not a SPIKE (overfit to one config).
  B. Leave-one-year-out (modern): which years drive the modern alpha — is it
     distributed or only 2020/2022?
All causal (US T-1, refi +5d). 1B VND, real BQ prices.
Output: data/validate_macro_report.md
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
DATADIR = os.path.join(WORKDIR, "data"); os.makedirs(DATADIR, exist_ok=True)
from simulate_holistic_nav import bq
from sbv_macro_overlay import SBV_REFI_EVENTS

STATE_ALLOC = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}
TC, TAX, BORROW, INIT, RF = 0.001, 0.001, 0.10, 1_000_000_000, 0.001
NEUTRAL, CRISIS, BEAR = 3, 1, 2
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}

# default macro params
BASE_P = dict(vix_mult=1.0, spx_mult=1.0, sbv_mult=1.0, refi_lag=5,
              ez_confirm=10, ez_price_lb=10, bull_bypass=True)

print("[1] data...")
px = bq("""SELECT p.time,p.Close,p.MA200,p.D_RSI,s.state FROM tav2_bq.ticker AS p
JOIN tav2_bq.vnindex_5state_dt_4gate AS s ON s.time=p.time
WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"]); px["state"] = px["state"].astype(int)
px = px.dropna(subset=["Close", "state"]).reset_index(drop=True)
us = pd.read_csv("us_market_history.csv", parse_dates=["time"]).sort_values("time")
key = px[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time": "us_time"}),
                   left_on="jt", right_on="us_time", direction="backward").sort_values("time").reset_index(drop=True)
px = px.merge(um[["time", "vix", "spx_dd_1y", "vix_ma252"]], on="time", how="left")
ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev["time"])
dr = pd.DataFrame({"time": pd.date_range(px["time"].min(), px["time"].max(), freq="D")}).merge(ev, on="time", how="left")
dr["refi"] = dr["refi"].ffill().bfill()
px = px.merge(dr, on="time", how="left"); px["refi"] = px["refi"].ffill().bfill()
px["refi_raw6m"] = px["refi"] - px["refi"].shift(126)
px["refi_peak6m"] = px["refi"].rolling(126, min_periods=20).max()
px["cut_raw"] = (px["refi_peak6m"] - px["refi"]) >= 0.5
px["vni_r6m"] = px["Close"] / px["Close"].shift(126) - 1
px["bull_flag"] = ((px["vni_r6m"] > 0.15) & (px["Close"] > px["MA200"])).shift(1).fillna(False)
NREC = len(px)


def macro_state(P):
    n = NREC
    vix = px["vix"].values; sdd = px["spx_dd_1y"].values; vixma = px["vix_ma252"].values
    rc6 = px["refi_raw6m"].shift(P["refi_lag"]).values
    cut = px["cut_raw"].shift(P["refi_lag"]).fillna(False).values.astype(bool)
    bull = px["bull_flag"].values.astype(bool); close = px["Close"].values
    vc, vb, vm = 35 * P["vix_mult"], 25 * P["vix_mult"], 20 * P["vix_mult"]
    sc, sb, sm_ = -0.25 * P["spx_mult"], -0.15 * P["spx_mult"], -0.10 * P["spx_mult"]
    de, ds, dm = 3.0 * P["sbv_mult"], 1.5 * P["sbv_mult"], 0.5 * P["sbv_mult"]
    cap = np.full(n, 9); easing = np.zeros(n, bool)
    for t in range(n):
        v, dd, vma, rr = vix[t], sdd[t], vixma[t], rc6[t]
        if P["bull_bypass"] and bull[t]:
            uc = ub = um_ = False
        else:
            uc = (not np.isnan(dd) and dd < sc) or (not np.isnan(v) and v > vc)
            ub = (not np.isnan(dd) and dd < sb) and (not np.isnan(v) and v > vb)
            um_ = (not np.isnan(dd) and dd < sm_) and (not np.isnan(v) and v > vm)
        de_ = (not np.isnan(rr) and rr >= de); ds_ = (not np.isnan(rr) and rr >= ds); dm_ = (not np.isnan(rr) and rr >= dm)
        if uc or de_: cap[t] = CRISIS
        elif ub or ds_: cap[t] = BEAR
        elif um_ or dm_: cap[t] = NEUTRAL
        calm = (not np.isnan(v) and not np.isnan(vma) and v < vma) and (not np.isnan(dd) and dd > -0.05)
        if cap[t] == 9 and cut[t] and calm: easing[t] = True
    persist = np.zeros(n, int)
    for t in range(n):
        persist[t] = persist[t-1] + 1 if (t > 0 and easing[t]) else (1 if easing[t] else 0)
    pup = np.zeros(n, bool); lb = P["ez_price_lb"]; pup[lb:] = close[lb:] > close[:-lb]
    ez = easing & (persist >= P["ez_confirm"]) & pup
    st = px["state"].values.astype(int)
    sm = np.where(cap != 9, np.minimum(st, cap), st)
    sm = np.where((cap == 9) & ez & (sm < NEUTRAL), NEUTRAL, sm).astype(int)
    return sm


def build_w(state):
    n = NREC; close = px["Close"].values; ma200 = px["MA200"].values; rsi = px["D_RSI"].values
    w = np.array([STATE_ALLOC[s] for s in state], float)
    up_raw = (close > ma200) & (~np.isnan(ma200)) & (np.nan_to_num(rsi, nan=0.0) <= 0.72)
    up = np.zeros(n, bool); cf = False; ru = rd = 0
    for t in range(n):
        if up_raw[t]: ru += 1; rd = 0
        else: rd += 1; ru = 0
        if not cf and ru >= 10: cf = True
        elif cf and rd >= 10: cf = False
        up[t] = cf
    w[(state == NEUTRAL) & up] = 0.90
    return w


def sim(state, mask=None):
    n = NREC; close = px["Close"].values
    r = np.zeros(n); r[1:] = close[1:] / close[:-1] - 1
    tgt = build_w(state); tgt_lag = np.concatenate([[0.0], tgt[:-1]])
    yr = px["time"].dt.year.values; dep = np.array([VGB_1Y.get(int(y), 0.001) for y in yr])
    yrs = (px["time"].iloc[-1] - px["time"].iloc[0]).days / 365.25; spy = n / yrs
    nav = np.empty(n); nav[0] = INIT; dret = np.zeros(n)
    for t in range(n):
        w = tgt_lag[t]; wp = tgt_lag[t-1] if t > 0 else 0.0
        cf = max(0.0, 1 - w); lf = max(0.0, w - 1); buy = max(0.0, w - wp); sell = max(0.0, wp - w)
        dret[t] = w * r[t] + cf * dep[t] / spy - lf * BORROW / spy - (buy + sell) * TC - sell * TAX
        if t > 0: nav[t] = nav[t-1] * (1 + dret[t])
    out = pd.DataFrame({"time": px["time"], "nav": nav, "ret": dret})
    return out, spy


def met(out, spy, a=None, b=None):
    o = out
    if a is not None:
        o = out[(out["time"] >= a) & (out["time"] <= b)].reset_index(drop=True)
        if len(o) < 20: return None
        nv = INIT * o["nav"].values / o["nav"].values[0]
    else:
        nv = o["nav"].values
    time = pd.DatetimeIndex(o["time"]); yrs = (time[-1] - time[0]).days / 365.25
    cagr = (nv[-1] / nv[0]) ** (1 / yrs) - 1; ex = o["ret"].values - RF / spy
    sh = ex.mean() / ex.std() * np.sqrt(spy) if ex.std() > 0 else 0
    dd = ((nv - np.maximum.accumulate(nv)) / np.maximum.accumulate(nv)).min()
    return dict(cagr=cagr * 100, sharpe=sh, dd=dd * 100)


# baseline (DT4 state, no macro)
base_state = px["state"].values.astype(int)
ob, spy = sim(base_state)
MOD = (pd.Timestamp("2014-01-01"), px["time"].max())
mb_full = met(ob, spy); mb_mod = met(ob, spy, *MOD)
print(f"[2] Baseline (no macro): Full {mb_full['cagr']:+.2f}% Sh{mb_full['sharpe']:.2f}  Modern {mb_mod['cagr']:+.2f}%")

# ── A. sensitivity grid (one-at-a-time) ──
print("[3] Parameter sensitivity (Δ vs baseline, Full & Modern CAGR)...")
def run_params(P):
    sm = macro_state(P); o, _ = sim(sm)
    return met(o, spy), met(o, spy, *MOD)
grid = {
    "vix_mult": [0.85, 1.0, 1.15], "spx_mult": [0.85, 1.0, 1.15],
    "sbv_mult": [0.7, 1.0, 1.3], "refi_lag": [5, 21, 63],
    "ez_confirm": [5, 10, 15, 20], "ez_price_lb": [5, 10, 20],
    "bull_bypass": [True, False],
}
L = ["# Macro Overlay — Robustness Validation\n",
     f"*Pure-index, real BQ, 1B. Baseline (no macro): Full {mb_full['cagr']:+.2f}%/Sh {mb_full['sharpe']:.2f}/DD {mb_full['dd']:.1f}%, "
     f"Modern {mb_mod['cagr']:+.2f}%/DD {mb_mod['dd']:.1f}%.*\n",
     "## A. One-at-a-time parameter sensitivity (Δ vs baseline)\n",
     "| Param | Value | ΔFull CAGR | ΔModern CAGR | Full Sh | Full DD |", "|---|---|---|---|---|---|"]
rows_sens = []
for pname, vals in grid.items():
    for v in vals:
        P = dict(BASE_P); P[pname] = v
        mf, mm = run_params(P)
        df = mf["cagr"] - mb_full["cagr"]; dm = mm["cagr"] - mb_mod["cagr"]
        star = " ←base" if v == BASE_P[pname] else ""
        L.append(f"| {pname} | {v}{star} | {df:+.2f}pp | {dm:+.2f}pp | {mf['sharpe']:.2f} | {mf['dd']:.1f}% |")
        rows_sens.append((pname, v, df, dm))
        print(f"  {pname:<12}={str(v):<6} ΔFull {df:+.2f}pp  ΔMod {dm:+.2f}pp")

dfs = [r[2] for r in rows_sens]; dms = [r[3] for r in rows_sens]
L.append(f"\n*ΔFull range [{min(dfs):+.2f}, {max(dfs):+.2f}]pp, all {'POSITIVE' if min(dfs)>0 else 'mixed'}; "
         f"ΔModern range [{min(dms):+.2f}, {max(dms):+.2f}]pp. "
         f"Plateau (not spike) ⇒ {'ROBUST' if min(dfs)>-0.2 else 'sensitive'}.*\n")

# ── B. leave-one-year-out (modern) ──
print("[4] Leave-one-year-out (modern alpha attribution)...")
sm_base = macro_state(BASE_P); om, _ = sim(sm_base)
full_alpha_mod = met(om, spy, *MOD)["cagr"] - mb_mod["cagr"]
L.append("## B. Leave-one-year-out — modern alpha attribution\n")
L.append(f"Macro modern alpha (all years) = **{full_alpha_mod:+.2f}pp**. Drop each year, recompute "
         "modern-window alpha; a big drop = that year drives the alpha.\n")
L.append("| Excluded year | Modern alpha w/o it | Δ vs all-years |", )
L.append("|---|---|---|")
om["year"] = om["time"].dt.year; ob["year"] = ob["time"].dt.year
loo = []
for yr in range(2014, 2027):
    mask = om["year"] != yr
    oo = om[mask].reset_index(drop=True); bb = ob[ob["year"] != yr].reset_index(drop=True)
    if len(oo) < 100: continue
    # recompute alpha on remaining modern days
    def cagr_of(o):
        nv = INIT * o["nav"].values / o["nav"].values[0]
        t = pd.DatetimeIndex(o["time"]); y = (t[-1] - t[0]).days / 365.25
        return ((nv[-1] / nv[0]) ** (1 / y) - 1) * 100
    om_mod = om[(om["time"] >= MOD[0]) & (om["year"] != yr)].reset_index(drop=True)
    ob_mod = ob[(ob["time"] >= MOD[0]) & (ob["year"] != yr)].reset_index(drop=True)
    a = cagr_of(om_mod) - cagr_of(ob_mod)
    loo.append((yr, a)); L.append(f"| {yr} | {a:+.2f}pp | {a-full_alpha_mod:+.2f}pp |")
    print(f"  drop {yr}: modern alpha {a:+.2f}pp ({a-full_alpha_mod:+.2f}pp)")
worst = min(loo, key=lambda x: x[1])
L.append(f"\n*Most alpha-carrying year: dropping **{worst[0]}** leaves {worst[1]:+.2f}pp "
         f"(vs {full_alpha_mod:+.2f}pp all-years). If alpha stays positive after dropping the biggest "
         f"contributor, it is NOT a single-event artifact.*\n")
with open(os.path.join(DATADIR, "validate_macro_report.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print(f"\n  Full ΔCAGR range [{min(dfs):+.2f},{max(dfs):+.2f}]pp; LOO worst-drop alpha {worst[1]:+.2f}pp (drop {worst[0]})")
print("  Report: data/validate_macro_report.md")
print("DONE.")
