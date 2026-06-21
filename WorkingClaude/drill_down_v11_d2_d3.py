#!/usr/bin/env python3
"""Drill down Đợt 2 (Aug 2025) và Đợt 3 (Jan 2026) trades với entry/exit context."""
import warnings; warnings.filterwarnings("ignore")
import os, sys, bisect, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import bq, VNI_QUERY
from test_round14_stability import SIGNAL_V10

# ─── Load trades & cached signal data ─────────────────────────────────
trades = pd.read_csv("data/sim_v11_jun2025_trades.csv")
trades["entry_date"] = pd.to_datetime(trades["entry_date"])
trades["exit_date"] = pd.to_datetime(trades["exit_date"])
trades = trades.sort_values("entry_date").reset_index(drop=True)

# Đợt 2: entries 2025-08-12 to 2025-08-14
# Đợt 3: entries 2026-01-09 to 2026-01-15
d2 = trades[(trades["entry_date"] >= "2025-08-12") & (trades["entry_date"] <= "2025-08-14")].copy()
d3 = trades[(trades["entry_date"] >= "2026-01-09") & (trades["entry_date"] <= "2026-01-15")].copy()

# Reload signals (with context columns)
print("Loading signals + context ...")
sig = bq(SIGNAL_V10.format(start="2025-01-01", end="2026-04-30"))
sig["time"] = pd.to_datetime(sig["time"])

# Load release dates
releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '2023-01-01' AND DATE '2026-04-30'""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(sorted).to_dict()

# Days since release per signal row
ds = np.empty(len(sig))
for i, (tk, t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
    arr = release_by_ticker.get(tk)
    if not arr: ds[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(t))
    if idx == 0: ds[i] = np.nan; continue
    ds[i] = (pd.Timestamp(t) - arr[idx-1]).days
sig["days_since_release"] = ds

# State5 daily
state_df = bq("""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
                 WHERE s.time BETWEEN DATE '2025-01-01' AND DATE '2026-04-30' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

# VNI daily
vni = bq("""SELECT t.time, t.Close, t.D_RSI, t.MA200 FROM tav2_bq.ticker AS t
            WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '2025-01-01' AND DATE '2026-04-30'""")
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
if vni["MA200"].isna().all():
    vni["MA200"] = vni["Close"].rolling(200, min_periods=200).mean()
vni["ratio"] = vni["Close"] / vni["MA200"]
vni_lookup = vni.set_index("time")[["Close","MA200","ratio","D_RSI"]]

# ─── Helper to get entry context ──────────────────────────────────────
def get_context(ticker, date):
    """Get signal row at entry date for ticker."""
    row = sig[(sig["ticker"]==ticker) & (sig["time"]==date)]
    if len(row) == 0:
        # Try adjacent days
        ticker_sig = sig[sig["ticker"]==ticker].sort_values("time")
        before = ticker_sig[ticker_sig["time"] <= date]
        if len(before) == 0: return None
        row = before.tail(1)
    return row.iloc[0]

def get_vni_ctx(date):
    """Get VNI metrics on date."""
    if date in vni_lookup.index:
        return vni_lookup.loc[date]
    # nearest before
    earlier = vni_lookup[vni_lookup.index <= date]
    if len(earlier) > 0: return earlier.iloc[-1]
    return None

def get_state_path(start, end):
    """Get state5 sequence between start and end."""
    states = []
    for d in pd.date_range(start, end, freq="D"):
        s = state_by_date.get(d)
        if s is not None:
            states.append((d, int(s)))
    # Compress to transitions
    if not states: return ""
    transitions = [states[0]]
    for d, s in states[1:]:
        if s != transitions[-1][1]:
            transitions.append((d, s))
    if states[-1] != transitions[-1]:
        transitions.append(states[-1])
    return " → ".join(f"{t[1]}({t[0].strftime('%m-%d')})" for t in transitions)

# ─── Drill down format ───────────────────────────────────────────────
def print_trade_detail(t):
    """Print full context for one trade."""
    tk = t["ticker"]; ed = t["entry_date"]; xd = t["exit_date"]
    days = int(t["days_held"])
    entry_ctx = get_context(tk, ed)
    if entry_ctx is None:
        print(f"  ❌ Cannot find context for {tk}@{ed.date()}"); return
    state_at_entry = state_by_date.get(ed)
    state_at_exit = state_by_date.get(xd)
    vni_at_entry = get_vni_ctx(ed)
    vni_at_exit = get_vni_ctx(xd)
    state_path = get_state_path(ed, xd)

    ret = t["ret_net"] * 100
    icon = "🟢" if ret > 10 else "🟡" if ret > 0 else "🔴" if ret > -15 else "🛑"
    print(f"\n{icon} {tk}  {ed.date()} → {xd.date()} ({days}d)  ret={ret:+.2f}%  reason={t['reason']}")
    fa_tier = "?"  # not available in SIGNAL_V10 output, look up later if needed
    state_str = f"{int(state_at_entry)}" if state_at_entry is not None else "?"
    print(f"   entry: TA={int(entry_ctx['ta'])}  state5={state_str}  play_type={entry_ctx['play_type']}  sector={int(entry_ctx['sec']) if pd.notna(entry_ctx['sec']) else '?'}")
    print(f"   stock: liq={entry_ctx.get('liq',0)/1e9:.1f}B  "
          f"days_since_rel={int(entry_ctx['days_since_release']) if pd.notna(entry_ctx['days_since_release']) else 'n/a'}")
    if vni_at_entry is not None:
        oh = "🔥OVERHEATED" if (vni_at_entry['ratio']>1.30 and (state_at_entry==5 or vni_at_entry['D_RSI']>0.75)) else ""
        print(f"   market@entry: VNI={vni_at_entry['Close']:.0f}  MA200={vni_at_entry['MA200']:.0f}  "
              f"ratio={vni_at_entry['ratio']:.3f}  RSI={vni_at_entry['D_RSI']:.3f}  {oh}")
    if vni_at_exit is not None:
        print(f"   market@exit:  VNI={vni_at_exit['Close']:.0f}  ratio={vni_at_exit['ratio']:.3f}  RSI={vni_at_exit['D_RSI']:.3f}")
    print(f"   state path: {state_path}")

# ─── DỢT 2 ─────────────────────────────────────────────────────────────
print("="*120)
print(f"  💛 ĐỢT 2: {len(d2)} entries 12-14/08/2025  (state 5 EX-BULL period — top before CRISIS)")
print("="*120)
for _, t in d2.iterrows():
    print_trade_detail(t)

# Pattern analysis
print(f"\n📊 ĐỢT 2 Pattern:")
d2_win = d2[d2["ret_net"]>0]; d2_loss = d2[d2["ret_net"]<=0]
print(f"   Winners ({len(d2_win)}/{len(d2)}): {', '.join(d2_win['ticker'].tolist())}")
print(f"   Losers  ({len(d2_loss)}/{len(d2)}): {', '.join(d2_loss['ticker'].tolist())}")
stops = d2[d2["reason"]=="STOP"]
print(f"   Stops:  {', '.join(stops['ticker'].tolist())} — {', '.join(f'{r:.1f}%' for r in stops['ret_net']*100)}")

# ─── ĐỢT 3 ─────────────────────────────────────────────────────────────
print("\n" + "="*120)
print(f"  🟢 ĐỢT 3: {len(d3)} entries 09-15/01/2026  (state 3 NEUTRAL transition, before Q1 BEAR)")
print("="*120)
for _, t in d3.iterrows():
    print_trade_detail(t)

print(f"\n📊 ĐỢT 3 Pattern:")
d3_win = d3[d3["ret_net"]>0]; d3_loss = d3[d3["ret_net"]<=0]
print(f"   Winners ({len(d3_win)}/{len(d3)}): {', '.join(d3_win['ticker'].tolist())}")
print(f"   Losers  ({len(d3_loss)}/{len(d3)}): {', '.join(d3_loss['ticker'].tolist())}")
stops = d3[d3["reason"]=="STOP"]
print(f"   Stops:  {', '.join(stops['ticker'].tolist())} — {', '.join(f'{r:.1f}%' for r in stops['ret_net']*100)}")
