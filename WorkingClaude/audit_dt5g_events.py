# -*- coding: utf-8 -*-
"""
audit_dt5g_events.py
====================
EVENT-LEVEL audit of the DT5G macro overlay (vs DT4 base). The macro gate fires on
RARE macro episodes (SBV rate moves, US panic) — so aggregate CAGR can hide the fact
that the alpha rests on a handful of events. This script:

  1. Counts the DISTINCT macro-intervention episodes (sparsity headline).
  2. For each episode, measures forward VNINDEX returns (over the episode itself,
     and T+20 / T+60 from episode start) → did a DE-RISK actually precede a fall,
     and did a RE-RISK (easing floor) actually precede a rise?
  3. Bull-failure check: did ANY de-risk cap fire inside a confirmed VN bull regime?
     (the documented US-override-in-bull trap that v3.4b bull-bypass exists to avoid)
  4. Driver attribution per episode: US panic (Pillar B) vs SBV money (Pillar A).

All causal (US T-1, refi +5d), same inputs as macro_state_live. Output:
data/audit_dt5g_events.md
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
from macro_state_live import get_macro_state, P
from sbv_macro_overlay import SBV_REFI_EVENTS

START, END = "2014-01-01", "2026-05-15"
SNAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL", 9: "none"}

# ── macro state (has state=DT5G, state_dt4=DT4, cap, easing) ──
m = get_macro_state(START, END, bq=bq)
m = m.sort_values("time").reset_index(drop=True)

# ── VNINDEX close for forward returns + bull flag + driver inputs ──
px = bq(f"""SELECT t.time, t.Close, t.MA200 FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY t.time""")
px["time"] = pd.to_datetime(px["time"])
m = m.merge(px, on="time", how="left")
m["Close"] = m["Close"].ffill(); m["MA200"] = m["MA200"].ffill()

# bull regime (same def as macro_state_live: r6m>15% AND Close>MA200, shifted 1)
m["bull"] = ((m["Close"] / m["Close"].shift(P["refi_chg_win"]) - 1 > P["bull_r6m"]) & (m["Close"] > m["MA200"])).shift(1).fillna(False)

# US inputs (T-1) for driver attribution
us = pd.read_csv("us_market_history.csv", parse_dates=["time"]).sort_values("time")
key = m[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time": "us_time"}),
                   left_on="jt", right_on="us_time", direction="backward").sort_values("time").reset_index(drop=True)
m = m.merge(um[["time", "vix", "spx_dd_1y"]], on="time", how="left")
# SBV refi 6m change (lagged) for driver attribution
ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev["time"])
dr = pd.DataFrame({"time": pd.date_range(m["time"].min(), m["time"].max(), freq="D")}).merge(ev, on="time", how="left")
dr["refi"] = dr["refi"].ffill().bfill()
m = m.merge(dr, on="time", how="left"); m["refi"] = m["refi"].ffill().bfill()
m["refi_chg6m"] = (m["refi"] - m["refi"].shift(P["refi_chg_win"])).shift(P["refi_lag"])

close = m["Close"].values
n = len(m)

def fwd_ret(i, h):
    """VNINDEX close-to-close return from row i to i+h (sessions)."""
    if i + h < n and not np.isnan(close[i]) and not np.isnan(close[i + h]) and close[i] > 0:
        return close[i + h] / close[i] - 1
    return np.nan

# ── identify episodes: contiguous runs where DT5G != DT4 ──
diff = (m["state"].values != m["state_dt4"].values)
direction = np.sign(m["state"].values - m["state_dt4"].values)  # <0 de-risk, >0 re-risk
episodes = []
i = 0
while i < n:
    if not diff[i]:
        i += 1; continue
    d0 = direction[i]; j = i
    while j + 1 < n and diff[j + 1] and direction[j + 1] == d0:
        j += 1
    episodes.append((i, j, d0))
    i = j + 1

rows = []
for (a, b, d0) in episodes:
    seg = m.iloc[a:b + 1]
    typ = "DE-RISK" if d0 < 0 else "RE-RISK"
    # episode-internal VNINDEX return (start -> end)
    ep_ret = close[b] / close[a] - 1 if close[a] > 0 else np.nan
    # driver attribution at episode start
    v0 = m["vix"].iloc[a]; dd0 = m["spx_dd_1y"].iloc[a]; rr0 = m["refi_chg6m"].iloc[a]
    us_on = (not np.isnan(v0) and v0 > P["vix_mild"]) or (not np.isnan(dd0) and dd0 < P["spx_mild"])
    sbv_on = (not np.isnan(rr0) and rr0 >= P["dom_mild"]) if d0 < 0 else (m["easing"].iloc[a:b+1].any())
    if d0 < 0:
        driver = "US+SBV" if (us_on and sbv_on) else ("US" if us_on else ("SBV" if sbv_on else "?"))
    else:
        driver = "SBV-easing"
    bull_any = bool(m["bull"].iloc[a:b + 1].any())
    rows.append(dict(
        start=m["time"].iloc[a].date(), end=m["time"].iloc[b].date(),
        type=typ, dur=int(b - a + 1),
        base=SNAME[int(m["state_dt4"].iloc[a])], macro=SNAME[int(m["state"].iloc[a])],
        driver=driver, in_bull=bull_any,
        ep_ret=ep_ret * 100, fwd20=fwd_ret(a, 20) * 100, fwd60=fwd_ret(a, 60) * 100,
    ))
ed = pd.DataFrame(rows)

# ── summary stats ──
derisk = ed[ed["type"] == "DE-RISK"]; rerisk = ed[ed["type"] == "RE-RISK"]
n_macro_days = int(diff.sum())

L = []
L.append("# DT5G Macro Overlay — Event-Level Audit\n")
L.append(f"*Period {START} → {m['time'].iloc[-1].date()} | {n} sessions. "
         f"Macro state differs from DT4 on **{n_macro_days} sessions ({n_macro_days/n*100:.1f}%)** "
         f"across **{len(ed)} distinct episodes** ({len(derisk)} de-risk, {len(rerisk)} re-risk).*\n")
L.append("> Sparsity is the headline: a macro overlay validated on a handful of episodes "
         "cannot be confirmed by aggregate CAGR or even by a single IS/OOS split — each side of the "
         "split may contain only 1-3 events. Read the per-episode forward returns below.\n")

L.append("## A. Episode ledger\n")
L.append("**EpRet% = VNINDEX return DURING the differ-window** (the only stretch DT5G actually deviates "
         "from DT4) — this is the overlay's marginal cost/benefit. T+20/T+60 are from episode START and are "
         "REFERENCE ONLY: once the base state_dt4 catches up (CRISIS exit ≈10 sessions), both systems agree, "
         "so those horizons mix in BASE-machine behavior, NOT the overlay's effect. Read EpRet, not T+60.\n")
L.append("| Start | End | Type | Dur | DT4→DT5G | Driver | InBull | **EpRet%** | T+20%(ref) | T+60%(ref) |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for _, r in ed.iterrows():
    L.append(f"| {r['start']} | {r['end']} | {r['type']} | {r['dur']} | {r['base']}→{r['macro']} | "
             f"{r['driver']} | {'⚠️YES' if r['in_bull'] else 'no'} | **{r['ep_ret']:+.1f}** | "
             f"{r['fwd20']:+.1f} | {r['fwd60']:+.1f} |")

L.append("\n## B. Does DE-RISK precede weakness? (correctness test — use EpRet, the differ-window)\n")
if len(derisk):
    L.append(f"- De-risk episodes: **{len(derisk)}**\n")
    L.append(f"- **Mean VNINDEX return DURING the de-risk differ-window: {derisk['ep_ret'].mean():+.2f}%** "
             f"(median {derisk['ep_ret'].median():+.2f}%; {(derisk['ep_ret']<=0).mean()*100:.0f}% of episodes "
             f"≤0). Negative = overlay correctly held cash through a falling tape. This is the metric that "
             f"judges the overlay.")
    L.append(f"- (Reference only) Mean T+60 from start: {derisk['fwd60'].mean():+.2f}% — do NOT read as overlay "
             f"cost: after CRISIS exit (~10 sessions) the base state_dt4 governs, so this horizon reflects the "
             f"BASE machine's recovery lag, which is identical for DT4 and DT5G.")
    nbull = int(derisk["in_bull"].sum())
    L.append(f"- **Bull-failure check**: de-risk episodes that fired inside a confirmed bull = **{nbull}** "
             f"{'⚠️ (this is exactly the US-override-in-bull trap)' if nbull else '✅ (bull-bypass held)'}.")
else:
    L.append("- No de-risk episodes.")

L.append("\n## C. Does RE-RISK (easing floor) precede strength?\n")
if len(rerisk):
    L.append(f"- Re-risk episodes: **{len(rerisk)}**")
    L.append(f"- Mean VNINDEX return DURING the re-risk window: **{rerisk['ep_ret'].mean():+.2f}%** "
             f"(median {rerisk['ep_ret'].median():+.2f}%) — positive = correctly stayed invested.")
    L.append(f"- Mean T+60 from episode start: **{rerisk['fwd60'].mean():+.2f}%** "
             f"(% positive: {(rerisk['fwd60']>0).mean()*100:.0f}%).")
else:
    L.append("- No re-risk episodes.")

L.append("\n## D. Driver concentration\n")
L.append("| Driver | #episodes | mean dur | mean T+60% |")
L.append("|---|---|---|---|")
for drv, g in ed.groupby("driver"):
    L.append(f"| {drv} | {len(g)} | {g['dur'].mean():.0f} | {g['fwd60'].mean():+.2f} |")

L.append("\n## E. Verdict on overfit / walk-forward\n")
L.append(f"- **Effective sample size = {len(ed)} episodes** ({len(derisk)} de-risk). "
         "This is the number that governs overfit risk — NOT the ~3000 sessions.")
L.append("- A standard IS(2014-19)/OOS(2020-now) split divides these few episodes; if either side has "
         "<3 episodes, that split is statistically near-meaningless on its own and must be read "
         "alongside this per-episode ledger.")

with open("data/audit_dt5g_events.md", "w", encoding="utf-8") as f:
    f.write("\n".join(L))

print(f"Episodes: {len(ed)} total | {len(derisk)} de-risk | {len(rerisk)} re-risk")
print(f"Macro-diff days: {n_macro_days}/{n} ({n_macro_days/n*100:.1f}%)")
if len(derisk):
    print(f"De-risk mean ep_ret {derisk['ep_ret'].mean():+.2f}% | T+60 {derisk['fwd60'].mean():+.2f}% | in-bull {int(derisk['in_bull'].sum())}")
if len(rerisk):
    print(f"Re-risk mean ep_ret {rerisk['ep_ret'].mean():+.2f}% | T+60 {rerisk['fwd60'].mean():+.2f}%")
print(ed.to_string(index=False))
print("Report: data/audit_dt5g_events.md")
print("DONE.")
