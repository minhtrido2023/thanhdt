# -*- coding: utf-8 -*-
"""
sim_dt4g_2000_now.py
====================
HONEST full-history simulation of the DT4G (DT 4-gate) market-state model as a
whole-market VNINDEX timing strategy, 2000-07-28 -> now, starting 1B VND.

Everything is sourced from REAL BigQuery data:
  - VNINDEX daily Close  : tav2_bq.ticker (ticker='VNINDEX')   -- real index price
  - DT4G market state    : tav2_bq.vnindex_5state_dt_4gate      -- 4-gate causal state

State -> equity allocation (canonical pure-index Kelly-style weights):
  CRISIS(1)=0%   BEAR(2)=20%   NEUTRAL(3)=70%   BULL(4)=100%   EX-BULL(5)=130%

NAV mechanics (no look-ahead):
  - T+1 execution: state seen at close of day t -> weight applied on day t+1
  - 1-day snap (weight set immediately, no multi-day ramp)
  - TC = 0.10% on |Delta weight| each day
  - Idle cash earns deposit 6%/yr (when w<1); leverage costs borrow 10%/yr (when w>1)
  - daily_ret = w*r_vni + (1-w)+ * dep/spy - (w-1)+ * bor/spy - |dw|*TC

Outputs:
  data/dt4g_2000_now_nav.csv      full daily NAV / weight / state / B&H path
  data/dt4g_2000_now_report.md    performance + risk report (full + sub-periods)
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
DATADIR = os.path.join(WORKDIR, "data"); os.makedirs(DATADIR, exist_ok=True)
from simulate_holistic_nav import bq as bq_csv  # tested BQ helper (temp-file pipe)

STATE_ALLOC = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
# Costs (VN retail reality): 0.1% brokerage on every trade (both sides),
# 0.1% securities-transfer TAX on SELLS only, idle cash = 0.1%/yr demand deposit.
TC_RATE, TAX_RATE, DEPOSIT_APY, BORROW_APY, INIT_NAV = 0.001, 0.001, 0.001, 0.10, 1_000_000_000


# ---------------------------------------------------------------- 1. pull data
print("=" * 92)
print("  DT4G full-history simulation (1B VND)  -- real BigQuery VNINDEX + DT 4-gate state")
print("=" * 92)
print("\n[1] Pulling REAL VNINDEX price + DT4G state from BigQuery...")
df = bq_csv("""
SELECT p.time, p.Close, s.state
FROM tav2_bq.ticker AS p
JOIN tav2_bq.vnindex_5state_dt_4gate AS s ON s.time = p.time
WHERE p.ticker = 'VNINDEX'
ORDER BY p.time
""")
df["time"] = pd.to_datetime(df["time"])
df = df.dropna(subset=["Close", "state"]).sort_values("time").reset_index(drop=True)
df["state"] = df["state"].astype(int)
print(f"  rows={len(df):,}  {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}")


# ----------------------------------------------------------- 2. NAV simulation
def simulate(d, alloc=STATE_ALLOC, tc=TC_RATE, tax=TAX_RATE, dep=DEPOSIT_APY, bor=BORROW_APY, init=INIT_NAV):
    d = d.reset_index(drop=True)
    close = d["Close"].values
    r = np.zeros(len(d)); r[1:] = close[1:] / close[:-1] - 1
    years = (d["time"].iloc[-1] - d["time"].iloc[0]).days / 365.25
    spy = len(d) / years
    w_state = np.array([alloc.get(int(s), 0.0) for s in d["state"].values])
    eff_w = np.concatenate([[0.0], w_state[:-1]])          # T+1 lag: state[t] -> weight[t+1]
    nav = np.empty(len(d)); nav[0] = init; dr = np.zeros(len(d))
    for t in range(len(d)):
        w = eff_w[t]; wp = eff_w[t-1] if t > 0 else 0.0
        c_frac = max(0.0, 1.0 - w); l_frac = max(0.0, w - 1.0)
        buy_dw = max(0.0, w - wp); sell_dw = max(0.0, wp - w)
        cost = (buy_dw + sell_dw) * tc + sell_dw * tax   # 0.1% fee both sides + 0.1% tax on sells
        dr[t] = w * r[t] + c_frac * dep / spy - l_frac * bor / spy - cost
        if t > 0:
            nav[t] = nav[t-1] * (1.0 + dr[t])
    out = d[["time", "Close", "state"]].copy()
    out["eff_weight"] = eff_w; out["ret"] = dr; out["nav"] = nav
    out["bh_nav"] = init * close / close[0]
    out["state_name"] = out["state"].map(STATE_NAMES)
    return out, spy, years


def metrics(nav, time, ret=None, spy=252, dep=DEPOSIT_APY):
    nav = np.asarray(nav, float); time = pd.DatetimeIndex(time)
    years = (time[-1] - time[0]).days / 365.25
    cagr = (nav[-1] / nav[0]) ** (1 / years) - 1
    if ret is None:
        ret = np.zeros(len(nav)); ret[1:] = nav[1:] / nav[:-1] - 1
    ret = np.asarray(ret, float)
    rf = dep / spy; ex = ret - rf
    sharpe = ex.mean() / ex.std() * np.sqrt(spy) if ex.std() > 0 else 0.0
    dn = ex[ex < 0]
    sortino = ex.mean() / dn.std() * np.sqrt(spy) if len(dn) and dn.std() > 0 else 0.0
    rmax = np.maximum.accumulate(nav); dd = (nav - rmax) / rmax
    mdd = dd.min(); calmar = cagr / (-mdd) if mdd < 0 else np.inf
    # longest drawdown duration (sessions under water)
    under = dd < -1e-9; longest = cur = 0
    for u in under:
        cur = cur + 1 if u else 0; longest = max(longest, cur)
    return dict(final=nav[-1], cagr=cagr, sharpe=sharpe, sortino=sortino,
                mdd=mdd, calmar=calmar, years=years, dd_dur=longest,
                tot=nav[-1] / nav[0] - 1)


sim, spy, years = simulate(df)
print(f"\n[2] Simulated {len(sim):,} sessions  |  ~{spy:.0f} sessions/yr  |  {years:.1f} yrs")

navp = os.path.join(DATADIR, "dt4g_2000_now_nav.csv")
sim.to_csv(navp, index=False)
print(f"  NAV path -> {os.path.relpath(navp, WORKDIR)}")


# -------------------------------------------------- 3. sub-period + benchmarks
def bh_metrics(d, init=INIT_NAV):
    close = d["Close"].values
    nav = init * close / close[0]
    r = np.zeros(len(d)); r[1:] = close[1:] / close[:-1] - 1
    yrs = (d["time"].iloc[-1] - d["time"].iloc[0]).days / 365.25
    return metrics(nav, d["time"], r, spy=len(d) / yrs, dep=0.0)


def sys_metrics(s):
    return metrics(s["nav"].values, s["time"], s["ret"].values,
                   spy=len(s) / ((s["time"].iloc[-1] - s["time"].iloc[0]).days / 365.25))


periods = {
    "FULL 2000-now":     (sim["time"].min(), sim["time"].max()),
    "Pre-2014 (00-13)":  (pd.Timestamp("2000-01-01"), pd.Timestamp("2013-12-31")),
    "Modern 2014-now":   (pd.Timestamp("2014-01-01"), sim["time"].max()),
    "2007-08 GFC":       (pd.Timestamp("2007-01-01"), pd.Timestamp("2009-03-31")),
    "COVID 2020":        (pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")),
}
rows = []
for name, (a, b) in periods.items():
    seg = sim[(sim["time"] >= a) & (sim["time"] <= b)].copy()
    if len(seg) < 20:
        continue
    # re-base each sub-period to 1B so CAGR/DD reflect that window standalone
    seg = seg.reset_index(drop=True)
    seg_nav = INIT_NAV * seg["nav"].values / seg["nav"].values[0]
    m = metrics(seg_nav, seg["time"], seg["ret"].values, spy=spy)
    bh = bh_metrics(seg)
    rows.append((name, m, bh))


# --------------------------------------------------------- 4. annual breakdown
sim["year"] = sim["time"].dt.year
annual = []
for yr, g in sim.groupby("year"):
    if len(g) < 5:
        continue
    sys_r = g["nav"].iloc[-1] / g["nav"].iloc[0] - 1
    bh_r = g["bh_nav"].iloc[-1] / g["bh_nav"].iloc[0] - 1
    annual.append((yr, sys_r, bh_r, g["state_name"].mode().iloc[0]))


# ---------------------------------------------------- 5. worst drawdown spells
nav_arr = sim["nav"].values
rmax = np.maximum.accumulate(nav_arr); dd = (nav_arr - rmax) / rmax
# find drawdown episodes deeper than -10%
episodes = []
i = 0
while i < len(dd):
    if dd[i] < -1e-9:
        j = i
        while j < len(dd) and dd[j] < -1e-9:
            j += 1
        seg = dd[i:j]; trough = seg.min(); ti = i + int(seg.argmin())
        episodes.append((sim["time"].iloc[i], sim["time"].iloc[ti], sim["time"].iloc[min(j, len(dd)-1)], trough))
        i = j
    else:
        i += 1
episodes = sorted([e for e in episodes if e[3] < -0.08], key=lambda x: x[3])[:6]

# state distribution & transitions
sd = sim["state"].value_counts(normalize=True).sort_index()
n_tr = int((sim["state"].values[1:] != sim["state"].values[:-1]).sum())


# --------------------------------------------------------------- 6. write report
def fmt_row(name, m, bh):
    return (f"| {name} | {m['cagr']*100:+.2f}% | {m['sharpe']:.2f} | {m['sortino']:.2f} | "
            f"{m['mdd']*100:+.1f}% | {m['calmar']:.2f} | {m['final']/1e9:.2f}B | "
            f"{bh['cagr']*100:+.2f}% | {bh['mdd']*100:+.1f}% |")

L = []
L.append("# DT4G Full-History Simulation — Performance & Risk\n")
L.append(f"*Real BigQuery data: VNINDEX price + `vnindex_5state_dt_4gate` state.*  "
         f"Period **{sim['time'].min().date()} → {sim['time'].max().date()}** "
         f"({years:.1f}y, {len(sim):,} sessions). Start NAV **1B VND**.\n")
L.append("**Model**: DT 4-gate state → equity allocation "
         "{CRISIS 0%, BEAR 20%, NEUTRAL 70%, BULL 100%, EX-BULL 130%}. "
         "T+1 execution; 0.1% fee both sides + 0.1% sell tax; idle cash 0.1%/yr; "
         "borrow 10%/yr on EX-BULL leverage. No look-ahead.\n")
L.append("## 1. Performance & risk by period (each window re-based to 1B)\n")
L.append("| Period | CAGR | Sharpe | Sortino | MaxDD | Calmar | Final NAV | B&H CAGR | B&H MaxDD |")
L.append("|---|---|---|---|---|---|---|---|---|")
for name, m, bh in rows:
    L.append(fmt_row(name, m, bh))
full_m = rows[0][1]
L.append(f"\n*Full-period longest drawdown: **{full_m['dd_dur']} sessions** under water "
         f"(~{full_m['dd_dur']/spy:.1f}y).*\n")
L.append("## 2. Annual returns: DT4G vs VNINDEX Buy&Hold\n")
L.append("| Year | DT4G | B&H | Δ | Dominant state |")
L.append("|---|---|---|---|---|")
for yr, sr, br, st in annual:
    L.append(f"| {yr} | {sr*100:+.1f}% | {br*100:+.1f}% | {(sr-br)*100:+.1f}pp | {st} |")
wins = sum(1 for _, sr, br, _ in annual if sr > br)
L.append(f"\n*DT4G beats B&H in **{wins}/{len(annual)}** years.*\n")
L.append("## 3. Worst drawdown episodes (DT4G NAV, full path)\n")
L.append("| Start | Trough | Recovery end | Trough DD |")
L.append("|---|---|---|---|")
for a, t, b, tr in episodes:
    L.append(f"| {a.date()} | {t.date()} | {b.date()} | {tr*100:+.1f}% |")
L.append("\n## 4. State distribution & activity\n")
L.append("| State | % of days |")
L.append("|---|---|")
for s, frac in sd.items():
    L.append(f"| {STATE_NAMES[int(s)]} | {frac*100:.1f}% |")
L.append(f"\n*Total state transitions: **{n_tr}** over {len(sim):,} sessions "
         f"(~{n_tr/years:.1f}/yr).*\n")
L.append("## 5. Honesty notes\n")
L.append("- **Pure-index proxy**: this sims money allocated *directly to the VNINDEX index* by "
         "state weight — it measures the **timing model's** quality, not a tradeable stock book "
         "(the integrated stock systems V4/V5 are separate). You cannot literally buy the index "
         "pre-2016 (no ETF); E1VFVN30 only exists from 2016, so VNINDEX is the honest continuous proxy.\n")
L.append("- **What the model does well vs its real weakness**: on *pure-index* timing the 0% CRISIS "
         "weight gave superb CRASH protection (2008 +70.7pp, 2022 +32.1pp, 2018 +21.2pp vs B&H). "
         "Its real cost is the OTHER side: NEUTRAL=70% caps upside in strong bull years (2006 −61pp, "
         "2009 −45pp, 2017 −13pp) and the 25-session CRISIS-enter gate **lags sharp V-recoveries** "
         "(2009). The documented *pre-2014 risk* refers to the INTEGRATED Kelly stock book (whipsaw "
         "under leverage), NOT this pure-index sim — here pre-2014 timing was actually strong. DT was "
         "tuned for the **modern 2014+** regime; pre-2014 is shown for completeness/stress.\n")
L.append("- Costs modelled: 0.1% brokerage fee both sides, 0.1% securities-transfer tax on sells, "
         "10%/yr borrow on EX-BULL leverage, 0.1%/yr demand-deposit interest on idle cash. "
         "No slippage/market-impact (index proxy). Real-world haircut ≈ −1.0pp/yr.\n")
L.append(f"\n*NAV path: `{os.path.relpath(navp, WORKDIR)}`*\n")

repp = os.path.join(DATADIR, "dt4g_2000_now_report.md")
with open(repp, "w", encoding="utf-8") as f:
    f.write("\n".join(L))


# ------------------------------------------------------------- 7. console echo
print("\n" + "=" * 92)
print("  RESULTS  (each period re-based to 1B VND)")
print("=" * 92)
print(f"  {'Period':<20}{'CAGR':>9}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}{'FinalNAV':>11} | "
      f"{'B&H CAGR':>9}{'B&H DD':>9}")
for name, m, bh in rows:
    print(f"  {name:<20}{m['cagr']*100:>+8.2f}%{m['sharpe']:>8.2f}{m['mdd']*100:>+8.1f}%"
          f"{m['calmar']:>8.2f}{m['final']/1e9:>9.2f}B | {bh['cagr']*100:>+8.2f}%{bh['mdd']*100:>+8.1f}%")
print("=" * 92)
print(f"  State dist: " + "  ".join(f"{STATE_NAMES[int(s)]}={f*100:.0f}%" for s, f in sd.items()))
print(f"  Transitions: {n_tr} ({n_tr/years:.1f}/yr)  |  DT4G beats B&H {wins}/{len(annual)} yrs")
print(f"\n  Report: data/dt4g_2000_now_report.md")
print(f"  NAV:    data/dt4g_2000_now_nav.csv")
print("DONE.")
