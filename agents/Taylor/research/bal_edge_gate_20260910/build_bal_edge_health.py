# -*- coding: utf-8 -*-
"""build_bal_edge_health.py — BAL shadow-cohort edge ledger (AMH #1, job Taylor_20260910_131906).

SYMMETRY WITH LAG (edge_health_monitor.lag_edge_health(), lines ~118-195)
------------------------------------------------------------------------
`lag_edge_health()` does NOT read the book's realized fills. It rebuilds the LAG *entry cohort*
from the daily-refreshed caches (NP_R>=15 & prior_n_good>=4 & pa_HL3>=5), enters T+5 after
release, holds the book's own horizon (25 sessions), and measures a plain per-event price return
-- no sizing, no slot cap, no parking, no capital constraint. That is WHY the series stays alive
even when the book is parked, and why it is causal (a signal-level realized return, not the
book's own NAV -> no circularity when it feeds the allocator).

This script builds the exact analogue for BAL:
  cohort  = SIGNAL_V11 BUY tiers restricted to TIER_BAL, after the book's own signal-layer
            filters: SV_TIGHT (days_since_release by state), overheat AVOID, EXBULL momentum
            suppression. NOT applied: max_positions=12, sector cap, regime_size weights,
            parking, CAPIT -- those are CAPITAL constraints, the LAG analogue omits them too.
  entry   = T+1 Open   (book: t1_open_exec=True)
  exit    = Open[t+1+45] (book: hold_days=45) OR next Open after Close <= entry*(1-0.20)
            (book: stop_loss=-0.20, close-based hard stop)
  ret     = (exit/entry - 1) * 100, gross (no TC) -- same convention as lag_edge_health

OUTPUT: data/bal_edge_health.csv   columns: entry,ticker,play_type,exit,ret,mean12,win12,n12
(same column spirit as data/lag_edge_health.csv, which has entry,ret,mean12,win12,n12).
Writing a NEW file; data/lag_edge_health.csv is a production contract and is never touched.

Env: BQ_LOCAL_CACHE / BQ_CACHE_THREADS / AUDIT_END honoured (same pins as pt_v23_audit_2014.py).
"""
import os, sys, io
import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

from simulate_holistic_nav import bq
from signal_v11_sql import SIGNAL_V11
from pt_dates import detect_end_date

START_DATE = os.environ.get("BAL_EDGE_START", "2014-01-02")
END_DATE   = os.environ.get("AUDIT_END") or detect_end_date()
STATE_TABLE = "tav2_bq.vnindex_5state_dt5g_live"
OUT = os.environ.get("BAL_EDGE_OUT", os.path.join(WORKDIR, "data", "bal_edge_health.csv"))

HOLD_DAYS = 45
STOP_LOSS = -0.20

# mirror pt_v23_audit_2014 / pt_v22_dt5g exactly
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                 "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO",
                 "RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
EXB_MOM = {"MEGA","MOMENTUM","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A","S_PRO"}

print(f"[bal-edge] window {START_DATE} -> {END_DATE}; cache={os.environ.get('BQ_LOCAL_CACHE','(live BQ)')}")

# ---------------------------------------------------------------- 1. signals
sig = bq(SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s", STATE_TABLE + " AS s")
                   .format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"[bal-edge] raw signals: {len(sig):,}")

state_df = bq(f"SELECT s.time, s.state FROM {STATE_TABLE} AS s WHERE s.time <= DATE '{END_DATE}'")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))
sig["state"] = sig["time"].map(state_by_date)

vni = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
vni["time"] = pd.to_datetime(vni["time"])
vni["overheat"] = (vni["Close"]/vni["MA200"] > 1.30) & \
                  ((vni["time"].map(state_by_date) == 5) | (vni["D_RSI"] > 0.75))
overheat_dates = set(vni[vni["overheat"]]["time"])

# ------------------------------------------- 2. book's own signal-layer filters
def sv_tight_keep(row):
    s = row["state"]; days = row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4, 5): return True
    if s == 1: return pd.notna(days) and days <= 30
    if s in (2, 3): return pd.notna(days) and days <= 60
    return True

mb = sig["play_type"].isin(BUY_TIERS_V11)
sig = sig[(~mb) | sig.apply(sv_tight_keep, axis=1)].copy()
sig.loc[sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
n_exb = int(((sig["state"] == 5) & sig["play_type"].isin(EXB_MOM)).sum())
sig.loc[(sig["state"] == 5) & sig["play_type"].isin(EXB_MOM), "play_type"] = "AVOID_exbull"
print(f"[bal-edge] EXBULL-suppressed {n_exb}")

coh = sig[sig["play_type"].isin(TIER_BAL)][["ticker", "time", "play_type", "state"]].copy()
coh = coh.drop_duplicates(["ticker", "time"]).sort_values(["time", "ticker"]).reset_index(drop=True)
print(f"[bal-edge] BAL cohort signals: {len(coh):,}  ({coh['time'].min().date()} -> {coh['time'].max().date()})")

# ---------------------------------------------------------------- 3. price panel
tks = sorted(coh["ticker"].unique())
px = bq(f"""SELECT t.ticker, t.time, t.Open, t.Close FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
px["time"] = pd.to_datetime(px["time"])
op = px.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index()
cl = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index()
idx = op.index
print(f"[bal-edge] price panel {op.shape[0]} sessions x {op.shape[1]} tickers")

# ---------------------------------------------------------------- 4. shadow trades
rows = []
n_skip_px = n_skip_short = 0
op_v = {t: op[t].values for t in op.columns}
cl_v = {t: cl[t].values for t in cl.columns}
pos_of = {d: i for i, d in enumerate(idx)}

for r in coh.itertuples(index=False):
    tk = r.ticker
    if tk not in op_v:
        n_skip_px += 1; continue
    i0 = pos_of.get(r.time)
    if i0 is None:
        i0 = int(idx.searchsorted(r.time, side="right")) - 1
        if i0 < 0: n_skip_px += 1; continue
    ent = i0 + 1                              # T+1 Open entry
    if ent >= len(idx): n_skip_short += 1; continue
    p0 = op_v[tk][ent]
    if not np.isfinite(p0) or p0 <= 0: n_skip_px += 1; continue
    hi = ent + HOLD_DAYS
    if hi >= len(idx): n_skip_short += 1; continue      # need a COMPLETE hold (mirrors lag ledger)
    ex = hi; reason = "TIME"
    cseg = cl_v[tk][ent:hi + 1]
    stop_lvl = p0 * (1.0 + STOP_LOSS)
    hit = np.where(np.isfinite(cseg) & (cseg <= stop_lvl))[0]
    if len(hit):
        k = ent + int(hit[0])
        if k + 1 <= hi:
            ex = k + 1; reason = "STOP"
    p1 = op_v[tk][ex]
    if not np.isfinite(p1) or p1 <= 0:
        p1 = cl_v[tk][ex]
        if not np.isfinite(p1) or p1 <= 0: n_skip_px += 1; continue
    rows.append({"entry": idx[ent], "ticker": tk, "play_type": r.play_type,
                 "state": r.state, "exit": idx[ex], "reason": reason,
                 "ret": (p1 / p0 - 1.0) * 100.0})

print(f"[bal-edge] shadow trades: {len(rows):,}  (skip px={n_skip_px}, skip incomplete-hold={n_skip_short})")
d = pd.DataFrame(rows).sort_values(["entry", "ticker"]).reset_index(drop=True)

# ---------------------------------------------- 5. causal trailing-12M rolling stats
ent_ns = d["entry"].values.astype("datetime64[ns]")
ret_v = d["ret"].values
yr = np.timedelta64(365, "D")
lo_idx = np.searchsorted(ent_ns, ent_ns - yr, side="right")
hi_idx = np.searchsorted(ent_ns, ent_ns, side="right")
csum = np.concatenate([[0.0], np.cumsum(ret_v)])
cwin = np.concatenate([[0.0], np.cumsum((ret_v > 0).astype(float))])
n12 = (hi_idx - lo_idx).astype(float)
d["mean12"] = (csum[hi_idx] - csum[lo_idx]) / np.where(n12 > 0, n12, np.nan)
d["win12"] = (cwin[hi_idx] - cwin[lo_idx]) / np.where(n12 > 0, n12, np.nan) * 100.0
d["n12"] = n12
d["pctile12"] = d["mean12"].expanding().apply(lambda s: (s <= s.iloc[-1]).mean() * 100.0, raw=False)

d.to_csv(OUT, index=False)
print(f"[bal-edge] wrote {OUT}  rows={len(d):,}")
m12 = d["mean12"].iloc[-1]; w12 = d["win12"].iloc[-1]; nn = int(d["n12"].iloc[-1])
print(f"[bal-edge] LATEST asof={d['entry'].iloc[-1].date()}  mean12={m12:.2f}%  win12={w12:.1f}%  n12={nn}"
      f"  pctile(expanding)={d['pctile12'].iloc[-1]:.0f}")
mo = d.set_index("entry")["mean12"].resample("ME").last().dropna()
neg = 0
for v in mo.values[::-1]:
    if v < 0: neg += 1
    else: break
print(f"[bal-edge] months-below-zero streak = {neg}")
print("[bal-edge] mean12 by calendar year (last reading of each year):")
print(d.set_index("entry")["mean12"].resample("YE").last().round(2).to_string())
