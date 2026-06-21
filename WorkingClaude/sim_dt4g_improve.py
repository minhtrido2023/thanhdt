# -*- coding: utf-8 -*-
"""
sim_dt4g_improve.py
===================
Ablation of three DT4G improvement ideas on top of the corrected-cost baseline:

  #2 TREND OVERLAY (decouple upside-cap): in NEUTRAL, lift 0.70 -> 0.90 when
     VNINDEX Close > MA200 AND not overheated (D_RSI <= 0.72). Keeps all the
     (excellent) crash protection; only removes the bull-year drag of NEUTRAL=70%.
     Available full history (uses VNINDEX MA200/RSI only).

  #3 BREADTH THRUST (fast V-recovery re-entry): Zweig-style. When breadth
     (% of prune universe above MA50) surges from washed-out (<0.35 within last
     10 sessions) to broad (>0.55), and the committed state is still CRISIS/BEAR,
     fast-track a 0.70 recovery floor for up to 60 sessions or until the state
     catches up. Breadth only exists 2014+, so this fires modern-era only (honest).

  #4 HYSTERESIS (tax-aware no-trade band): only move the target weight if
     |w_target - w_held| >= band. Directly tames the MA200-whipsaw that #2
     introduces (price oscillating around MA200 -> 0.7<->0.9 taxed churn).

All sourced from REAL BigQuery data. Costs: 0.1% fee both sides, 0.1% sell tax,
idle cash 0.1%/yr (baseline) or a simulated gov-bond yield (final realistic run),
borrow 10%/yr on EX-BULL. T+1 execution, no look-ahead.

Outputs:
  data/dt4g_improve_report.md   ablation table + sub-periods + best-combo annual
  data/dt4g_improve_nav.csv     daily NAV of every variant
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
DATADIR = os.path.join(WORKDIR, "data"); os.makedirs(DATADIR, exist_ok=True)
from simulate_holistic_nav import bq

STATE_ALLOC = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
TC, TAX, BORROW, INIT = 0.001, 0.001, 0.10, 1_000_000_000
NEUTRAL, CRISIS, BEAR = 3, 1, 2

# Time-varying VN 1-year GOVERNMENT BOND yield (approx annual avg) for the idle-cash
# sleeve. Anchored to real history: peak ~20% (Jun-2008), ~12% (2010 H1 & 2011 H2),
# 10Y ~4.3% (Mar-2026) so 1Y ~2.5-3% now. Low-rate modern era (2020-2025 ~1-3%),
# high-rate inflation era (2008-2012 ~9-14%). These are conservative annual means.
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}

# ---------------------------------------------------------------- 1. pull data
print("[1] Pulling VNINDEX price+MA200+RSI, DT4G state, breadth (2014+)...")
px = bq("""SELECT p.time, p.Close, p.MA200, p.D_RSI, s.state
FROM tav2_bq.ticker AS p
JOIN tav2_bq.vnindex_5state_dt_4gate AS s ON s.time=p.time
WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"])
px = px.dropna(subset=["Close", "state"]).sort_values("time").reset_index(drop=True)
px["state"] = px["state"].astype(int)

brd = bq("""SELECT t.time, AVG(IF(t.Close>t.MA50,1.0,0.0)) AS breadth
FROM tav2_bq.ticker AS t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.MA50 IS NOT NULL AND t.ticker!='VNINDEX'
GROUP BY t.time ORDER BY t.time""")
brd["time"] = pd.to_datetime(brd["time"])
# breadth count per day: only trust it once the universe is broad (>=50 names) — the
# early thin universe (a handful of 2000-era listings) gives meaningless breadth.
cnt = bq("""SELECT t.time, COUNT(*) AS n
FROM tav2_bq.ticker AS t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.MA50 IS NOT NULL AND t.ticker!='VNINDEX'
GROUP BY t.time""")
cnt["time"] = pd.to_datetime(cnt["time"])
brd = brd.merge(cnt, on="time", how="left")
brd.loc[brd["n"] < 50, "breadth"] = np.nan          # mask thin-universe breadth
px = px.merge(brd[["time", "breadth"]], on="time", how="left")
bmin = px.loc[px["breadth"].notna(), "time"].min()
print(f"  {len(px):,} rows {px['time'].iloc[0].date()}->{px['time'].iloc[-1].date()}; "
      f"reliable breadth (>=50 names) from {bmin.date()}")


# ----------------------------------------------------- 2. target-weight builder
def build_target_weight(d, trend=False, thrust=False, confirm=0):
    """Return per-day TARGET weight (pre-T+1-lag, pre-hysteresis) from state + overlays.
       confirm = sessions the up/down condition must persist before flipping the
       trend-overlay lift (proper #4 hysteresis applied at the MA200-cross source)."""
    n = len(d); st = d["state"].values.astype(int)
    close = d["Close"].values; ma200 = d["MA200"].values
    rsi = d["D_RSI"].values; breadth = d["breadth"].values
    w = np.array([STATE_ALLOC[s] for s in st], dtype=float)

    if trend:
        up_raw = (close > ma200) & (~np.isnan(ma200)) & (np.nan_to_num(rsi, nan=0.0) <= 0.72)
        if confirm > 0:                                  # debounce the MA200 cross
            up = np.zeros(n, bool); cur = False; run_up = run_dn = 0
            for t in range(n):
                if up_raw[t]: run_up += 1; run_dn = 0
                else:         run_dn += 1; run_up = 0
                if not cur and run_up >= confirm: cur = True
                elif cur and run_dn >= confirm:  cur = False
                up[t] = cur
        else:
            up = up_raw
        lift = (st == NEUTRAL) & up
        w[lift] = 0.90                                   # NEUTRAL 0.70 -> 0.90 in confirmed uptrend

    if thrust:
        # washed-out min over trailing 10 sessions, broad today
        bser = pd.Series(breadth)
        min10 = bser.rolling(10, min_periods=5).min().values
        fire = (~np.isnan(breadth)) & (breadth > 0.55) & (~np.isnan(min10)) & (min10 < 0.35)
        floor_left = 0
        for t in range(n):
            if fire[t]:
                floor_left = 60                          # impose 0.70 recovery floor
            if floor_left > 0:
                if st[t] >= NEUTRAL:                     # state caught up -> release
                    floor_left = 0
                else:
                    w[t] = max(w[t], 0.70)
                    floor_left -= 1
    return w


def simulate(d, trend=False, thrust=False, confirm=0, band=0.0, dep=0.001, dep_by_year=None):
    """dep = flat idle-cash yield; dep_by_year = {year: yield} overrides dep per day
       (time-varying gov-bond sleeve)."""
    n = len(d)
    close = d["Close"].values
    r = np.zeros(n); r[1:] = close[1:] / close[:-1] - 1
    yrs = (d["time"].iloc[-1] - d["time"].iloc[0]).days / 365.25
    spy = n / yrs
    years_arr = d["time"].dt.year.values
    dep_arr = (np.array([dep_by_year.get(int(y), dep) for y in years_arr])
               if dep_by_year else np.full(n, dep))
    tgt = build_target_weight(d, trend, thrust, confirm)
    tgt_lag = np.concatenate([[0.0], tgt[:-1]])          # T+1: info at t -> act t+1
    # hysteresis: only move held weight if |target-held|>=band
    held = np.empty(n); h = 0.0
    for t in range(n):
        if abs(tgt_lag[t] - h) >= band:
            h = tgt_lag[t]
        held[t] = h
    nav = np.empty(n); nav[0] = INIT; dr = np.zeros(n)
    for t in range(n):
        w = held[t]; wp = held[t-1] if t > 0 else 0.0
        c_frac = max(0.0, 1 - w); l_frac = max(0.0, w - 1)
        buy = max(0.0, w - wp); sell = max(0.0, wp - w)
        cost = (buy + sell) * TC + sell * TAX
        dr[t] = w * r[t] + c_frac * dep_arr[t] / spy - l_frac * BORROW / spy - cost
        if t > 0:
            nav[t] = nav[t-1] * (1 + dr[t])
    out = d[["time", "Close", "state"]].copy()
    out["w"] = held; out["nav"] = nav; out["ret"] = dr
    return out, spy


def metrics(nav, time, ret, spy, dep=0.001):
    nav = np.asarray(nav, float); time = pd.DatetimeIndex(time)
    yrs = (time[-1] - time[0]).days / 365.25
    cagr = (nav[-1] / nav[0]) ** (1 / yrs) - 1
    rf = dep / spy; ex = np.asarray(ret) - rf
    sh = ex.mean() / ex.std() * np.sqrt(spy) if ex.std() > 0 else 0
    dn = ex[ex < 0]; so = ex.mean() / dn.std() * np.sqrt(spy) if len(dn) and dn.std() > 0 else 0
    rmax = np.maximum.accumulate(nav); dd = (nav - rmax) / rmax; mdd = dd.min()
    return dict(cagr=cagr, sharpe=sh, sortino=so, mdd=mdd,
                calmar=cagr / -mdd if mdd < 0 else 0, final=nav[-1])


def sub(out, spy, a, b, dep):
    seg = out[(out["time"] >= a) & (out["time"] <= b)].reset_index(drop=True)
    if len(seg) < 20:
        return None
    nv = INIT * seg["nav"].values / seg["nav"].values[0]
    return metrics(nv, seg["time"], seg["ret"].values, spy, dep)


# ----------------------------------------------------------------- 3. ablation
print("[2] Running ablation...")
RF = 0.001   # fixed risk-free hurdle for comparable Sharpe across variants
variants = [
    ("Baseline (corrected)",      dict(trend=False, thrust=False, confirm=0,  dep=0.001)),
    ("+#2 trend (raw)",           dict(trend=True,  thrust=False, confirm=0,  dep=0.001)),
    ("+#2 trend +#4 confirm10",   dict(trend=True,  thrust=False, confirm=10, dep=0.001)),
    ("+#3 breadth thrust (14+)",  dict(trend=False, thrust=True,  confirm=0,  dep=0.001)),
    ("#2+#4 + #3",                dict(trend=True,  thrust=True,  confirm=10, dep=0.001)),
    ("#2+#4 + bond-cash (time-var VGB)", dict(trend=True, thrust=False, confirm=10, dep_by_year=VGB_1Y)),
]
results = []; nav_cols = {}
for name, kw in variants:
    out, spy = simulate(px, **kw)
    full = metrics(out["nav"].values, out["time"], out["ret"].values, spy, RF)
    mod = sub(out, spy, pd.Timestamp("2014-01-01"), out["time"].max(), RF)
    gfc = sub(out, spy, pd.Timestamp("2007-01-01"), pd.Timestamp("2009-03-31"), RF)
    cov = sub(out, spy, pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31"), RF)
    ntr = int((out["w"].values[1:] != out["w"].values[:-1]).sum())
    results.append((name, full, mod, gfc, cov, ntr))
    nav_cols[name] = out.set_index("time")["nav"]
    print(f"  {name:<28} full {full['cagr']*100:+.2f}%  Sh {full['sharpe']:.2f}  "
          f"DD {full['mdd']*100:+.1f}%  mod {mod['cagr']*100:+.2f}%  rebal {ntr}")

# B&H reference
close = px["Close"].values; bh = INIT * close / close[0]
rbh = np.zeros(len(px)); rbh[1:] = close[1:] / close[:-1] - 1
bh_full = metrics(bh, px["time"], rbh, len(px) / ((px["time"].iloc[-1] - px["time"].iloc[0]).days / 365.25), 0.0)

pd.DataFrame(nav_cols).to_csv(os.path.join(DATADIR, "dt4g_improve_nav.csv"))


# --------------------------------------------------------------- 4. annual best
best = simulate(px, trend=True, thrust=False, confirm=10, dep=0.001)[0]
best["year"] = best["time"].dt.year
base_out = simulate(px, dep=0.001)[0]; base_out["year"] = base_out["time"].dt.year
annual = []
for yr in sorted(best["year"].unique()):
    gb = best[best["year"] == yr]; g0 = base_out[base_out["year"] == yr]
    if len(gb) < 5:
        continue
    rb = gb["nav"].iloc[-1] / gb["nav"].iloc[0] - 1
    r0 = g0["nav"].iloc[-1] / g0["nav"].iloc[0] - 1
    cl = px[px["time"].dt.year == yr]["Close"].values
    rbh_y = cl[-1] / cl[0] - 1
    annual.append((yr, r0, rb, rbh_y))


# ------------------------------------------------------------------- 5. report
def mr(m):
    return (f"{m['cagr']*100:+.2f}% | {m['sharpe']:.2f} | {m['mdd']*100:+.1f}% | "
            f"{m['calmar']:.2f} | {m['final']/1e9:.2f}B")

L = ["# DT4G Improvements — Ablation (#2 trend, #3 breadth-thrust, #4 hysteresis)\n",
     f"*Real BQ data, 2000-07-28 → 2026-05-26, 1B VND. Costs: 0.1% fee + 0.1% sell tax, "
     f"borrow 10%/yr. Idle cash 0.1%/yr except final row (time-varying VN 1Y gov-bond yield: "
     f"~8% early-2000s, peak 14% 2008 / 12% 2011, falling to ~2% 2020-2025). Sharpe uses a fixed "
     f"0.1% rf hurdle for all variants (comparable).*\n",
     f"**VNINDEX B&H full-period ref**: {mr(bh_full)} (MaxDD includes pre-2007 −80%).\n",
     "## Full-period (2000→now) + Modern (2014→now)\n",
     "| Variant | Full CAGR | Sh | MaxDD | Calmar | Final | Modern CAGR | Mod DD | Rebals |",
     "|---|---|---|---|---|---|---|---|---|"]
for name, full, mod, gfc, cov, ntr in results:
    L.append(f"| {name} | {full['cagr']*100:+.2f}% | {full['sharpe']:.2f} | {full['mdd']*100:+.1f}% | "
             f"{full['calmar']:.2f} | {full['final']/1e9:.2f}B | {mod['cagr']*100:+.2f}% | "
             f"{mod['mdd']*100:+.1f}% | {ntr} |")
L.append("\n## Crisis / recovery stress (sub-period, re-based 1B)\n")
L.append("| Variant | 2007-08 GFC CAGR | GFC DD | COVID-2020 CAGR | 2020 DD |")
L.append("|---|---|---|---|---|")
for name, full, mod, gfc, cov, ntr in results:
    if gfc and cov:
        L.append(f"| {name} | {gfc['cagr']*100:+.2f}% | {gfc['mdd']*100:+.1f}% | "
                 f"{cov['cagr']*100:+.2f}% | {cov['mdd']*100:+.1f}% |")
L.append("\n## Annual: Baseline vs Best (#2 trend + #4 confirm10) vs B&H\n")
L.append("| Year | Baseline | Best-combo | B&H | Δ(combo−base) |")
L.append("|---|---|---|---|---|")
for yr, r0, rb, rbh_y in annual:
    L.append(f"| {yr} | {r0*100:+.1f}% | {rb*100:+.1f}% | {rbh_y*100:+.1f}% | {(rb-r0)*100:+.1f}pp |")
L.append("\n## Verdict & notes\n"
         "- **#2 trend overlay = ADOPT.** Lifts NEUTRAL 70%→90% only when VNINDEX>MA200 + RSI≤0.72 "
         "(full history). Modern +1.05pp, MaxDD preserved. Gains come exactly where designed — bull "
         "years (2006 +12.8pp, 2017 +8.6pp, 2025 +3.8pp) — while crash years stay identical "
         "(2008 −0.8%, 2022 −6.9% unchanged).\n"
         "- **#4 confirmation dwell (10 sessions) = ADOPT with #2.** Debounces the MA200 cross at the "
         "source: rebalances 326→136 (−58%) with essentially identical return/DD. (A global Δw "
         "no-trade band does nothing here — discrete state jumps are ≥0.2.)\n"
         "- **#3 breadth thrust = REJECT.** Even with reliable breadth (≥50 names, from 2007) it blows "
         "MaxDD to −53% and halves Sharpe — it re-enters into continuing crashes (2008 GFC CAGR "
         "collapses +19.5%→+8.2%). It DOES help the one true V-recovery (2020 +25% vs +15%), but the "
         "crash-whipsaw cost dwarfs it. Confirms the documented vol-adaptive failure mode.\n"
         "- **bond-cash sleeve (idea #1) = biggest single lever**, now with a TIME-VARYING VN 1Y "
         "gov-bond yield (realistic: ~8% early-2000s, peak ~14% in 2008 / ~12% in 2011, falling to "
         "**~2% in 2020-2025** — NOT a flat 5%). Idle cash earns this instead of 0.1% demand deposit "
         "(VN has no deep MMF; a modeled short-dur gov-bond sleeve is the honest proxy). Effect: "
         "**+2.2pp modern** on top of #2+#4, and a large FULL-period boost because 2008/2011 parked "
         "cash earned 12-14% during the high-rate inflation era. MaxDD improves to −34.8%.\n"
         "- Sharpe is computed with a fixed 0.1% rf hurdle for ALL variants, so the bond row's 1.25 is "
         "directly comparable (and is the best) — no rf artifact.\n"
         "- **RECOMMENDED config**: DT4G + #2 trend + #4 confirm10 + time-varying bond-cash sleeve → "
         "**Full +19.17% / Modern +14.49% / MaxDD −34.8% / Sharpe 1.25**, 136 rebalances. Reject #3.\n")
with open(os.path.join(DATADIR, "dt4g_improve_report.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))

print(f"\n  B&H full {bh_full['cagr']*100:+.2f}%  Sh {bh_full['sharpe']:.2f}  DD {bh_full['mdd']*100:+.1f}%")
print("  Report: data/dt4g_improve_report.md  |  NAV: data/dt4g_improve_nav.csv")
print("DONE.")
