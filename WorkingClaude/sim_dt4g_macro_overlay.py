# -*- coding: utf-8 -*-
"""
sim_dt4g_macro_overlay.py  —  CANONICAL BACKTEST for DT5G (with breadth gate)
=========================
DT5G = DT 4-gate + Macro gate (SBV money + US panic) + breadth-decoupling guard
(suppress US cap when VN breadth healthy). Produces the canonical figure (nav_base
19.17% / nav_macro = DT5G 20.13% / 113.x B, 2000-now, 1B).
ONE consolidated macro layer on top of DT4G (avoids stacking separate overlays).
It fuses the existing rule families into a single module that emits ONE signal:

  Pillar A  DOMESTIC MONEY  — SBV refinancing-rate 6-month momentum (clean policy
            series from sbv_macro_overlay.SBV_REFI_EVENTS). Subsumes both "SBV
            policy" and the domestic rate-momentum finding (same driver → no overlap).
  Pillar B  US PANIC        — VIX + SPX 1-year drawdown (validated 3-tier linkage
            from analyze_us_vn_linkage.py). US aligned to VN T-1 (causal).

Two asymmetric legs (matching the empirical evidence):
  DEFENSIVE  stress high  -> CAP the DT4G state ceiling (CRISIS/BEAR/NEUTRAL)
             => de-risk EARLIER in inflation/panic crises (2008, 2011, 2022).
  RECOVERY   SBV cutting from a peak AND US panic subsiding -> FLOOR at NEUTRAL
             => re-enter FASTER on monetary easing (fixes DT's V-recovery lag;
                rate-driven, more reliable than breadth-thrust which failed).

Applied as an OUTER ceiling/floor over the recommended config
(DT4G + #2 trend overlay + #4 confirm10 + time-varying bond-cash). All signals
lagged (US T-1, refi +5 sessions) => no look-ahead. 1B VND, real BQ prices.

Output: data/dt4g_macro_overlay_report.md, data/dt4g_macro_overlay_nav.csv
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
DATADIR = os.path.join(WORKDIR, "data"); os.makedirs(DATADIR, exist_ok=True)
from simulate_holistic_nav import bq
from sbv_macro_overlay import SBV_REFI_EVENTS

STATE_ALLOC = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
TC, TAX, BORROW, INIT = 0.001, 0.001, 0.10, 1_000_000_000
NEUTRAL, CRISIS, BEAR = 3, 1, 2
RF = 0.001
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}

# ── thresholds ──
US_REFI_LAG = 5                       # sessions refi is applied with (public announcement)
T_DOM_MILD, T_DOM_STRONG, T_DOM_EXTREME = 0.5, 1.5, 3.0   # refi 6m-change (pp) tiers
REFI_CUT_FROM_PEAK = 0.5              # rate is >=0.5pp below trailing-6m max -> easing cycle
# VN-breadth decoupling guard on Pillar B (free insurance, 2026-05-29): suppress the US cap
# only when VN breadth_MA200 is broadly HEALTHY (>=TH) on a large universe (>=MIN_UNIV) while
# US panics. Fail-safe: weak/missing/small-universe breadth => no suppression => US cap fires.
BREADTH_FILE = r"/home/trido/thanhdt/WorkingClaude/data/preprocess_others_market_indicators_all_tickers.csv"
BREADTH_TH, BREADTH_MIN_UNIVERSE = 0.50, 100

# ───────────────────────────────────────────────── 1. data
print("[1] VNINDEX + DT4G state + MA200/RSI (BQ); US VIX/SPX; SBV refi...")
px = bq("""SELECT p.time, p.Close, p.MA200, p.D_RSI, s.state FROM tav2_bq.ticker AS p
JOIN tav2_bq.vnindex_5state_dt_4gate AS s ON s.time=p.time
WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"]); px["state"] = px["state"].astype(int)
px = px.dropna(subset=["Close", "state"]).sort_values("time").reset_index(drop=True)

us = pd.read_csv("us_market_history.csv", parse_dates=["time"]).sort_values("time")
# align US to VN T-1 (US closes before next VN session): merge_asof on (vn_time - 1d)
key = px[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time": "us_time"}),
                   left_on="jt", right_on="us_time", direction="backward")
um = um.sort_values("time").reset_index(drop=True)
px = px.merge(um[["time", "vix", "spx_dd_1y", "vix_ma252"]], on="time", how="left")

# SBV refi daily series -> 6m change, lagged
ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev["time"])
dr = pd.DataFrame({"time": pd.date_range(px["time"].min(), px["time"].max(), freq="D")})
dr = dr.merge(ev, on="time", how="left"); dr["refi"] = dr["refi"].ffill().bfill()
px = px.merge(dr, on="time", how="left"); px["refi"] = px["refi"].ffill().bfill()
px["refi_chg6m"] = (px["refi"] - px["refi"].shift(126)).shift(US_REFI_LAG)
px["refi_peak6m"] = px["refi"].rolling(126, min_periods=20).max()
px["refi_cut"] = ((px["refi_peak6m"] - px["refi"]) >= REFI_CUT_FROM_PEAK).shift(US_REFI_LAG).fillna(False)
# VN bull regime (v3.4b "BTC" bull-aware bypass): 6m return >15% AND price>MA200, lagged 1d.
# In a confirmed VN bull, US panic is noise (memory: US override 100% wrong in bull) -> bypass
# Pillar B; domestic SBV tightening (Pillar A) still applies (real warning, e.g. 2007).
px["vni_r6m"] = px["Close"] / px["Close"].shift(126) - 1
px["bull"] = ((px["vni_r6m"] > 0.15) & (px["Close"] > px["MA200"])).shift(1).fillna(False)
# breadth decoupling flag (causal T-1); fail-safe to False (=no suppression) if file/data missing
px["us_decoupled"] = False
try:
    bd = pd.read_csv(BREADTH_FILE); bd["time"] = pd.to_datetime(bd["time"])
    bd = bd[["time", "Breadth_MA200", "Breadth_Total_MA200"]].sort_values("time")
    px = pd.merge_asof(px.sort_values("time"), bd, on="time", direction="backward").sort_values("time").reset_index(drop=True)
    px["us_decoupled"] = ((px["Breadth_Total_MA200"].fillna(0) >= BREADTH_MIN_UNIVERSE)
                          & (px["Breadth_MA200"] >= BREADTH_TH)).shift(1).fillna(False)
except Exception as e:
    print(f"  [breadth guard inactive: {e} -> US pillar ungated (fail-safe)]")
print(f"  {len(px):,} rows {px['time'].iloc[0].date()}->{px['time'].iloc[-1].date()}  bull days {int(px['bull'].sum())}  "
      f"decoupling-guard days {int(px['us_decoupled'].sum())}")


# ─────────────────────────────────────── 2. unified macro signal (causal)
def macro_signal(d):
    """Return cap_level (1/2/3 = max-allowed state; 9 = no cap), easing (bool),
       and per-day attribution of which pillar fired (for audit)."""
    n = len(d)
    vix = d["vix"].values; sdd = d["spx_dd_1y"].values; vixma = d["vix_ma252"].values
    rc6 = d["refi_chg6m"].values; cut = d["refi_cut"].values.astype(bool)
    bull = d["bull"].values.astype(bool); decoup = d["us_decoupled"].values.astype(bool)
    cap = np.full(n, 9); easing = np.zeros(n, bool); src = np.array([""] * n, dtype=object)
    for t in range(n):
        v, dd, vm, rr = vix[t], sdd[t], vixma[t], rc6[t]
        # Pillar B (US panic) — BYPASSED in a confirmed VN bull (v3.4b rule) OR on US-VN
        # decoupling (VN breadth broadly healthy while US panics = the breadth guard).
        if bull[t] or decoup[t]:
            us_crisis = us_bear = us_mild = False
        else:
            us_crisis = (not np.isnan(dd) and dd < -0.25) or (not np.isnan(v) and v > 35)
            us_bear   = (not np.isnan(dd) and dd < -0.15) and (not np.isnan(v) and v > 25)
            us_mild   = (not np.isnan(dd) and dd < -0.10) and (not np.isnan(v) and v > 20)
        dom_ext   = (not np.isnan(rr) and rr >= T_DOM_EXTREME)
        dom_str   = (not np.isnan(rr) and rr >= T_DOM_STRONG)
        dom_mild  = (not np.isnan(rr) and rr >= T_DOM_MILD)
        if us_crisis or dom_ext:
            cap[t] = CRISIS; src[t] = "US-crisis" if us_crisis else "SBV-tighten-extreme"
        elif us_bear or dom_str:
            cap[t] = BEAR;   src[t] = "US-bear" if us_bear else "SBV-tighten-strong"
        elif us_mild or dom_mild:
            cap[t] = NEUTRAL; src[t] = "US-mild" if us_mild else "SBV-tighten-mild"
        # recovery leg (RAW): only when no active stress cap
        us_calm = (not np.isnan(v) and not np.isnan(vm) and v < vm) and (not np.isnan(dd) and dd > -0.05)
        if cap[t] == 9 and cut[t] and us_calm:
            easing[t] = True; src[t] = "SBV-cut+US-calm"
    # (a) CONFIRMED easing — causal, a-priori rule (NOT fitted to history):
    #   easing must persist >=10 sessions AND price must itself turn up (Close>Close[t-10]).
    #   Avoids re-levering into a still-falling market on the monetary signal alone.
    close = d["Close"].values
    persist = np.zeros(n, int)
    for t in range(n):
        persist[t] = persist[t-1] + 1 if (t > 0 and easing[t]) else (1 if easing[t] else 0)
    price_up = np.zeros(n, bool); price_up[10:] = close[10:] > close[:-10]
    easing_conf = easing & (persist >= 10) & price_up
    return cap, easing, easing_conf, src


cap, easing, easing_conf, src = macro_signal(px)

# debounce the DEFENSIVE cap: a new cap level must persist CAP_COMMIT sessions to
# commit (causal; kills the 1-3 day VIX-flicker whipsaw, e.g. Apr-2025). K=7 chosen
# (best Full CAGR + 0 Apr-2025 flicker + crisis protection intact). 2026-05-29.
CAP_COMMIT = 7
def _commit_cap(arr, K):
    if K <= 1: return arr.copy()
    out = arr.copy(); c = arr[0]; ps, pr = arr[0], 1
    for t in range(1, len(arr)):
        if arr[t] == ps: pr += 1
        else: ps, pr = arr[t], 1
        if pr >= K: c = ps
        out[t] = c
    return out
cap = _commit_cap(cap, CAP_COMMIT)
print(f"[2] macro fires (cap committed K={CAP_COMMIT}): cap-CRISIS {int((cap==CRISIS).sum())}d  "
      f"cap-BEAR {int((cap==BEAR).sum())}d  cap-NEUTRAL {int((cap==NEUTRAL).sum())}d  "
      f"easing-confirmed {int(easing_conf.sum())}d")


# ─────────────────────────── 3. recommended-config target weight + macro layer
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


def simulate(d, use_macro=False, easing_mode="off", dep_by_year=VGB_1Y):
    n = len(d); close = d["Close"].values
    r = np.zeros(n); r[1:] = close[1:] / close[:-1] - 1
    yrs = (d["time"].iloc[-1] - d["time"].iloc[0]).days / 365.25; spy = n / yrs
    tgt = build_weight(d)
    if use_macro:
        ceil = np.where(cap == 9, 1.30, np.array([STATE_ALLOC.get(c, 1.30) for c in cap]))
        tgt = np.minimum(tgt, ceil)                              # DEFENSIVE: cap ceiling
        ez = {"raw": easing, "confirmed": easing_conf, "off": np.zeros(n, bool)}[easing_mode]
        tgt = np.where(ez & (tgt < 0.70), 0.70, tgt)             # RECOVERY: floor NEUTRAL
    tgt_lag = np.concatenate([[0.0], tgt[:-1]])
    years_arr = d["time"].dt.year.values
    dep_arr = np.array([dep_by_year.get(int(y), 0.001) for y in years_arr])
    nav = np.empty(n); nav[0] = INIT; dr = np.zeros(n); held = tgt_lag
    for t in range(n):
        w = held[t]; wp = held[t-1] if t > 0 else 0.0
        c_frac = max(0.0, 1 - w); l_frac = max(0.0, w - 1)
        buy = max(0.0, w - wp); sell = max(0.0, wp - w)
        dr[t] = w * r[t] + c_frac * dep_arr[t] / spy - l_frac * BORROW / spy - (buy + sell) * TC - sell * TAX
        if t > 0: nav[t] = nav[t-1] * (1 + dr[t])
    out = d[["time", "Close", "state"]].copy(); out["w"] = held; out["nav"] = nav; out["ret"] = dr
    return out, spy


def metrics(nav, time, ret, spy):
    nav = np.asarray(nav, float); time = pd.DatetimeIndex(time)
    yrs = (time[-1] - time[0]).days / 365.25; cagr = (nav[-1] / nav[0]) ** (1 / yrs) - 1
    ex = np.asarray(ret) - RF / spy
    sh = ex.mean() / ex.std() * np.sqrt(spy) if ex.std() > 0 else 0
    dn = ex[ex < 0]; so = ex.mean() / dn.std() * np.sqrt(spy) if len(dn) and dn.std() > 0 else 0
    rmax = np.maximum.accumulate(nav); mdd = ((nav - rmax) / rmax).min()
    return dict(cagr=cagr, sharpe=sh, sortino=so, mdd=mdd, calmar=cagr / -mdd if mdd < 0 else 0, final=nav[-1])


def sub(out, spy, a, b):
    seg = out[(out["time"] >= a) & (out["time"] <= b)].reset_index(drop=True)
    if len(seg) < 20: return None
    nv = INIT * seg["nav"].values / seg["nav"].values[0]
    return metrics(nv, seg["time"], seg["ret"].values, spy)


# ─────────────────────────────────────────────────── 4. run + compare
print("[3] Simulating baseline vs +macro(raw easing) vs +macro(confirmed easing)...")
base, spy = simulate(px, use_macro=False)
mac_raw, _ = simulate(px, use_macro=True, easing_mode="raw")
mac, _ = simulate(px, use_macro=True, easing_mode="confirmed")   # (a) refined: confirmed easing
PERIODS = {"FULL 2000-now": (px["time"].min(), px["time"].max()),
           "Pre-2014": (pd.Timestamp("2000-01-01"), pd.Timestamp("2013-12-31")),
           "Modern 2014-now": (pd.Timestamp("2014-01-01"), px["time"].max()),
           "2007-08 GFC": (pd.Timestamp("2007-01-01"), pd.Timestamp("2009-03-31")),
           "2011 inflation": (pd.Timestamp("2011-01-01"), pd.Timestamp("2012-06-30")),
           "COVID 2020": (pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")),
           "2022 hikes": (pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31"))}
rows = []
for name, (a, b) in PERIODS.items():
    mb = sub(base, spy, a, b); mr = sub(mac_raw, spy, a, b); mm = sub(mac, spy, a, b)
    if mb and mm: rows.append((name, mb, mr, mm))

pd.DataFrame({"time": base["time"], "nav_base": base["nav"], "nav_macro": mac["nav"],
              "state": base["state"], "w_base": base["w"], "w_macro": mac["w"],
              "cap": cap, "easing": easing, "easing_conf": easing_conf, "src": src}).to_csv(
    os.path.join(DATADIR, "dt4g_macro_overlay_nav.csv"), index=False)

# ── macro-adjusted 5-STATE series (for integrated V5/Kelly test) ──
# defensive cap pushes state DOWN to the cap level; confirmed-easing floor pushes UP to NEUTRAL.
st_arr = px["state"].values.astype(int)
sm = st_arr.copy()
capped = cap != 9
sm = np.where(capped, np.minimum(st_arr, cap), st_arr)
sm = np.where((~capped) & easing_conf & (sm < NEUTRAL), NEUTRAL, sm).astype(int)
n_def = int((sm < st_arr).sum()); n_rec = int((sm > st_arr).sum())
pd.DataFrame({"time": px["time"].dt.strftime("%Y-%m-%d"), "state": sm, "state_raw": sm}).to_csv(
    os.path.join(WORKDIR, "vnindex_5state_dt4_macro.csv"), index=False)
print(f"  macro-state CSV: {n_def} days de-risked (cap), {n_rec} days re-risked (easing floor)")

# annual
base["year"] = base["time"].dt.year; mac["year"] = mac["time"].dt.year
annual = []
for yr in sorted(base["year"].unique()):
    gb = base[base["year"] == yr]; gm = mac[mac["year"] == yr]
    if len(gb) < 5: continue
    annual.append((yr, gb["nav"].iloc[-1] / gb["nav"].iloc[0] - 1, gm["nav"].iloc[-1] / gm["nav"].iloc[0] - 1))


# ─────────────────────────────────────────────────── 5. report
def fnav(m): return f"{m['cagr']*100:+.2f}% | {m['sharpe']:.2f} | {m['mdd']*100:+.1f}% | {m['calmar']:.2f} | {m['final']/1e9:.2f}B"

L = ["# DT4G + Consolidated Macro Overlay — one layer (SBV money + US panic)\n",
     f"*Real BQ prices, 2000→2026, 1B VND. Base = recommended config "
     f"(DT4G + #2 trend + #4 confirm10 + time-var bond-cash). Macro = SBV refi 6m-momentum "
     f"+ US VIX/SPX, fused into one cap/floor signal. Causal (US T-1, refi +5d).*\n",
     "## Baseline vs +Macro (raw easing) vs +Macro (confirmed easing = refined (a))\n",
     "| Period | Base CAGR\\|Sh\\|DD\\|Cal\\|NAV | +Macro raw | +Macro confirmed |",
     "|---|---|---|---|"]
for name, mb, mr, mm in rows:
    L.append(f"| {name} | {fnav(mb)} | {fnav(mr)} | {fnav(mm)} |")
L.append("\n## Annual return: base vs +macro\n| Year | Base | +Macro | Δ |\n|---|---|---|---|")
for yr, rb, rm in annual:
    L.append(f"| {yr} | {rb*100:+.1f}% | {rm*100:+.1f}% | {(rm-rb)*100:+.1f}pp |")
fires = pd.Series(src[src != ""]).value_counts()
L.append("\n## Macro signal attribution (days fired by pillar)\n| Trigger | Days |\n|---|---|")
for k, v in fires.items(): L.append(f"| {k} | {v} |")
L.append("\n## Design notes\n"
         "- **One module, not three overlays.** SBV-policy and the domestic rate-momentum finding are "
         "the SAME driver (policy rate) → fused into Pillar A (no double-counting). US panic = Pillar B. "
         "DXY/FX deliberately omitted to avoid over-stacking (weakest, overlaps US).\n"
         "- **Asymmetric**: stress → cap state ceiling (de-risk early); SBV-cut + US-calm → floor NEUTRAL "
         "(re-enter early). Recovery leg is the rate-driven fix for the V-recovery lag that breadth-thrust failed.\n"
         "- Caps use the validated US 3-tier (VIX/SPX-DD) OR'd with SBV refi 6m-change tiers "
         f"(mild {T_DOM_MILD}/strong {T_DOM_STRONG}/extreme {T_DOM_EXTREME} pp).\n")
with open(os.path.join(DATADIR, "dt4g_macro_overlay_report.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))

print("\n" + "=" * 90)
print(f"  {'Period':<18}{'Base':>9}{'Mac-raw':>9}{'Mac-conf':>9}{'BaseDD':>9}{'rawDD':>8}{'confDD':>8}{'cSh':>6}")
for name, mb, mr, mm in rows:
    print(f"  {name:<18}{mb['cagr']*100:>+8.2f}%{mr['cagr']*100:>+8.2f}%{mm['cagr']*100:>+8.2f}%"
          f"{mb['mdd']*100:>+8.1f}%{mr['mdd']*100:>+7.1f}%{mm['mdd']*100:>+7.1f}%{mm['sharpe']:>6.2f}")
print("=" * 90)
print(f"  fires: {dict(fires)}")
print("  Report: data/dt4g_macro_overlay_report.md")
print("DONE.")
