# -*- coding: utf-8 -*-
"""
audit_dt5g_events_2000.py
=========================
FULL-HISTORY (2000-07 → now) event-level audit of the DT5G macro overlay vs DT4.
get_macro_state() hardcodes a 2014 warmup and uses BQ `ticker` (2014+ only), so this
script rebuilds the SAME fusion on LOCAL full-history sources, importing the exact
helpers/params from macro_state_live (no logic drift):
  - base state: vnindex_5state_tam_quan_v3_4b_full_history.csv (2000+) -> _dt_4gate
  - price/MA200: VNINDEX.csv (local, 2000+)   - US: us_market_history.csv (2000+)
  - SBV refi: sbv_macro_overlay.SBV_REFI_EVENTS
Purpose: does the macro overlay (esp. the easing/RE-RISK arm) ever earn its keep in the
2008 GFC / 2011 inflation / SBV 15%->cut cycles that it was theoretically designed for?
Output: data/audit_dt5g_events_2000.md
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from macro_state_live import _dt_4gate, _commit, P, NEUTRAL, CRISIS, BEAR
from sbv_macro_overlay import SBV_REFI_EVENTS

SNAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL", 9: "none"}
START = "2000-01-01"

# ── base state (full history) + DT-4gate ──
sf = pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
sf["time"] = pd.to_datetime(sf["time"]); sf = sf.sort_values("time").reset_index(drop=True)
sf["state_dt"] = _dt_4gate(sf["state"].values.astype(int))

# ── VNINDEX price (local) + MA200 ──
vx = pd.read_csv("data/VNINDEX.csv"); vx["time"] = pd.to_datetime(vx["time"])
vx = vx.sort_values("time").reset_index(drop=True)
vx["MA200"] = vx["Close"].rolling(200, min_periods=50).mean()
df = vx[["time", "Close", "MA200"]].merge(sf[["time", "state_dt"]], on="time", how="inner")
df = df.sort_values("time").reset_index(drop=True)
df["state_dt"] = df["state_dt"].astype(int)

# ── Pillar B US (T-1) ──
us = pd.read_csv("data/us_market_history.csv", parse_dates=["time"]).sort_values("time")
key = df[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time": "us_time"}),
                   left_on="jt", right_on="us_time", direction="backward").sort_values("time").reset_index(drop=True)
df = df.merge(um[["time", "vix", "spx_dd_1y", "vix_ma252"]], on="time", how="left")

# ── Pillar A SBV refi (lagged) ── (verbatim from macro_state_live.get_macro_state)
ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev["time"])
dr = pd.DataFrame({"time": pd.date_range(df["time"].min(), df["time"].max(), freq="D")}).merge(ev, on="time", how="left")
dr["refi"] = dr["refi"].ffill().bfill()
df = df.merge(dr, on="time", how="left"); df["refi"] = df["refi"].ffill().bfill()
df["refi_chg6m"] = (df["refi"] - df["refi"].shift(P["refi_chg_win"])).shift(P["refi_lag"])
peak = df["refi"].rolling(P["refi_chg_win"], min_periods=20).max()
df["refi_cut"] = ((peak - df["refi"]) >= P["refi_cut_drop"]).shift(P["refi_lag"]).fillna(False)
df["bull"] = ((df["Close"] / df["Close"].shift(P["refi_chg_win"]) - 1 > P["bull_r6m"]) & (df["Close"] > df["MA200"])).shift(1).fillna(False)

# ── fuse to cap + easing (verbatim) ──
n = len(df); vix = df["vix"].values; sdd = df["spx_dd_1y"].values; vma = df["vix_ma252"].values
rc6 = df["refi_chg6m"].values; cut = df["refi_cut"].values.astype(bool); bull = df["bull"].values.astype(bool)
close = df["Close"].values
cap = np.full(n, 9); easing = np.zeros(n, bool)
for t in range(n):
    v, dd, vm, rr = vix[t], sdd[t], vma[t], rc6[t]
    if bull[t]:
        uc = ub = umild = False
    else:
        uc = (not np.isnan(dd) and dd < P["spx_crisis"]) or (not np.isnan(v) and v > P["vix_crisis"])
        ub = (not np.isnan(dd) and dd < P["spx_bear"]) and (not np.isnan(v) and v > P["vix_bear"])
        umild = (not np.isnan(dd) and dd < P["spx_mild"]) and (not np.isnan(v) and v > P["vix_mild"])
    de = (not np.isnan(rr) and rr >= P["dom_extreme"]); ds = (not np.isnan(rr) and rr >= P["dom_strong"])
    dm = (not np.isnan(rr) and rr >= P["dom_mild"])
    if uc or de: cap[t] = CRISIS
    elif ub or ds: cap[t] = BEAR
    elif umild or dm: cap[t] = NEUTRAL
    calm = (not np.isnan(v) and not np.isnan(vm) and v < vm) and (not np.isnan(dd) and dd > -0.05)
    if cap[t] == 9 and cut[t] and calm: easing[t] = True
persist = np.zeros(n, int)
for t in range(n):
    persist[t] = persist[t-1] + 1 if (t > 0 and easing[t]) else (1 if easing[t] else 0)
lb = P["ez_price_lb"]; pup = np.zeros(n, bool); pup[lb:] = close[lb:] > close[:-lb]
ez = easing & (persist >= P["ez_confirm"]) & pup
cap = _commit(cap, P["cap_commit"])
st = df["state_dt"].values
sm = np.where(cap != 9, np.minimum(st, cap), st)
sm = np.where((cap == 9) & ez & (sm < NEUTRAL), NEUTRAL, sm).astype(int)
m = pd.DataFrame({"time": df["time"], "state": sm, "state_dt4": st, "cap": cap,
                  "easing": ez, "Close": close, "bull": bull, "vix": vix,
                  "spx_dd_1y": sdd, "refi_chg6m": rc6})

# ── episodes ──
def fwd(i, h):
    if i + h < n and close[i] > 0 and not np.isnan(close[i + h]):
        return (close[i + h] / close[i] - 1) * 100
    return np.nan
diff = (m["state"].values != m["state_dt4"].values)
direction = np.sign(m["state"].values - m["state_dt4"].values)
episodes = []; i = 0
while i < n:
    if not diff[i]: i += 1; continue
    d0 = direction[i]; j = i
    while j + 1 < n and diff[j + 1] and direction[j + 1] == d0: j += 1
    episodes.append((i, j, d0)); i = j + 1
rows = []
for (a, b, d0) in episodes:
    typ = "DE-RISK" if d0 < 0 else "RE-RISK"
    ep_ret = (close[b] / close[a] - 1) * 100 if close[a] > 0 else np.nan
    v0 = m["vix"].iloc[a]; dd0 = m["spx_dd_1y"].iloc[a]; rr0 = m["refi_chg6m"].iloc[a]
    us_on = (not np.isnan(v0) and v0 > P["vix_mild"]) or (not np.isnan(dd0) and dd0 < P["spx_mild"])
    if d0 < 0:
        sbv_on = (not np.isnan(rr0) and rr0 >= P["dom_mild"])
        driver = "US+SBV" if (us_on and sbv_on) else ("US" if us_on else ("SBV" if sbv_on else "?"))
    else:
        driver = "SBV-easing"
    rows.append(dict(start=m["time"].iloc[a].date(), end=m["time"].iloc[b].date(), type=typ,
                     dur=int(b - a + 1), base=SNAME[int(m["state_dt4"].iloc[a])],
                     macro=SNAME[int(m["state"].iloc[a])], driver=driver,
                     in_bull=bool(m["bull"].iloc[a:b + 1].any()), ep_ret=ep_ret,
                     fwd20=fwd(a, 20), fwd60=fwd(a, 60)))
ed = pd.DataFrame(rows)
derisk = ed[ed["type"] == "DE-RISK"]; rerisk = ed[ed["type"] == "RE-RISK"]
pre14 = ed[pd.to_datetime(ed["start"]) < "2014-01-01"]; post14 = ed[pd.to_datetime(ed["start"]) >= "2014-01-01"]

L = ["# DT5G Macro Overlay — FULL-HISTORY Event Audit (2000→now)\n",
     f"*{m['time'].iloc[0].date()} → {m['time'].iloc[-1].date()} | {n} sessions. "
     f"Macro differs from DT4 on {int(diff.sum())} sessions ({diff.sum()/n*100:.1f}%), "
     f"{len(ed)} episodes ({len(derisk)} de-risk, {len(rerisk)} re-risk). "
     f"Pre-2014: {len(pre14)} episodes | 2014+: {len(post14)} episodes.*\n",
     "EpRet% = VNINDEX return during the differ-window (overlay's marginal cost/benefit). "
     "T+20/T+60 from start = reference only (mix in base-machine behavior after CRISIS exit).\n",
     "## Episode ledger (full history)\n",
     "| Start | End | Type | Dur | DT4→DT5G | Driver | InBull | EpRet% | T+20 | T+60 |",
     "|---|---|---|---|---|---|---|---|---|---|"]
for _, r in ed.iterrows():
    L.append(f"| {r['start']} | {r['end']} | {r['type']} | {r['dur']} | {r['base']}→{r['macro']} | "
             f"{r['driver']} | {'⚠️YES' if r['in_bull'] else 'no'} | {r['ep_ret']:+.1f} | "
             f"{r['fwd20']:+.1f} | {r['fwd60']:+.1f} |")
L.append("\n## Summary")
L.append(f"- DE-RISK: {len(derisk)} episodes | mean EpRet {derisk['ep_ret'].mean():+.2f}% "
         f"| {(derisk['ep_ret']<=0).mean()*100:.0f}% landed on weakness | in-bull {int(derisk['in_bull'].sum())}")
if len(rerisk):
    L.append(f"- RE-RISK (easing floor): {len(rerisk)} episodes | mean EpRet {rerisk['ep_ret'].mean():+.2f}% "
             f"| {(rerisk['ep_ret']>0).mean()*100:.0f}% preceded strength | mean T+60 {rerisk['fwd60'].mean():+.2f}%")
else:
    L.append("- RE-RISK (easing floor): **0 episodes even over 2000-now** → easing arm is dead code.")
L.append(f"- Pre-2014 episodes: {len(pre14)} | 2014+ episodes: {len(post14)}")
with open("data/audit_dt5g_events_2000.md", "w", encoding="utf-8") as f:
    f.write("\n".join(L))

print(f"FULL HISTORY {m['time'].iloc[0].date()} -> {m['time'].iloc[-1].date()} | {n} sessions")
print(f"Episodes: {len(ed)} ({len(derisk)} de-risk, {len(rerisk)} re-risk) | pre-2014: {len(pre14)} | 2014+: {len(post14)}")
print(ed.to_string(index=False))
if len(rerisk): print(f"\nRE-RISK mean EpRet {rerisk['ep_ret'].mean():+.2f}% | T+60 {rerisk['fwd60'].mean():+.2f}%")
print("\nReport: data/audit_dt5g_events_2000.md")
