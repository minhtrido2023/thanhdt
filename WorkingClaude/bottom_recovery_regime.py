#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bottom_recovery_regime.py  (RESEARCH / DISPLAY-ONLY — job Taylor_20260706_111335)

Tests the SYMMETRIC OPPOSITE of the confidence-loss regime (job Taylor_20260706_105930).

User hypothesis (bottom / recovery):
  After a high-rate period, when (1) rates ease, (2) real estate is cold (or already
  cold), (3) gold falls, AND (4) equities are cheap vs their own history — this combo
  marks a VNINDEX bottom / turn-up that draws capital back.

Design mirrors the confidence-loss study: build a daily flag from the 4 conditions,
event-study against known bottoms, compare forward returns vs baseline, and ask whether
the 4-way combo fires EARLIER / with LESS NOISE than the single "rates falling" signal
(the very thing EASING_FLOOR_ENABLED=False deemed untrustworthy on its own).

Inputs (all local/repo/BQ-cache — nothing touches production):
  - VNINDEX level + RE-sector return + VNINDEX_PE : /tmp/bottom_re_pe.csv (BQ ticker_prune, 2007+)
  - SBV refi rate                                 : sbv_refi_events.json (2006+)
  - Big-4 12M deposit rate (PROXY)                : deposit_rate_vn.py
  - Gold world USD/oz                             : /tmp/gold_world.csv (2016-07+  <-- LIMITS full flag)
DISPLAY-ONLY. Writes nothing to production paths. Does NOT propose re-enabling the easing floor.
"""
import json, warnings, sys
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from deposit_rate_vn import merge_deposit

ROOT = '/home/trido/thanhdt/WorkingClaude'
TD = 21  # trading days / month

# ---------------- assemble daily frame ----------------
df = pd.read_csv('/tmp/bottom_re_pe.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
df = df[df['vni'] > 0].reset_index(drop=True)

# refi rate (step, forward-fill)
ev = json.load(open(f'{ROOT}/sbv_refi_events.json'))['events']
refi = pd.DataFrame(ev, columns=['time', 'refi']); refi['time'] = pd.to_datetime(refi['time'])
df = pd.merge_asof(df, refi.sort_values('time'), on='time', direction='backward')

# deposit rate proxy
df = merge_deposit(df)

# gold (2016+)
gold = pd.read_csv('/tmp/gold_world.csv', parse_dates=['time']).rename(columns={'close': 'gold'})
df = pd.merge_asof(df, gold.sort_values('time'), on='time', direction='backward')

# ---------------- derived signals ----------------
df['vni_ret'] = df['vni'].pct_change()
# forward returns (pure shift of realised level, no look-ahead)
for h in (60, 120, 250):
    df[f'fwd{h}'] = df['vni'].shift(-h) / df['vni'] - 1.0

# (1) RATES EASING: refi OR deposit fell over trailing ~6m, AND had been elevated.
df['refi_chg6m'] = df['refi'] - df['refi'].shift(6 * TD)
df['dep_chg6m']  = df['deposit_rate'] - df['deposit_rate'].shift(6 * TD)
# "had been elevated" = rate 6m ago was in the upper half of its trailing 3y range
df['refi_hi'] = df['refi'].shift(6 * TD) >= df['refi'].rolling(3 * 252, min_periods=252).median()
df['rates_easing'] = ((df['refi_chg6m'] < 0) | (df['dep_chg6m'] < 0)) & df['refi_hi'].fillna(False)

# (2) GOLD FALLING over trailing 6m (only meaningful 2016+)
df['gold_mom6m'] = df['gold'] / df['gold'].shift(6 * TD) - 1.0
df['gold_falling'] = df['gold_mom6m'] < 0

# (3) RE COLD: RE-sector cumulative return underperforms VNINDEX over trailing 9m.
df['re_cum'] = (1 + df['re_ret'].fillna(0)).cumprod()
LB = 9 * TD
df['re_rel_9m'] = (df['re_cum'] / df['re_cum'].shift(LB)) - (df['vni'] / df['vni'].shift(LB))
df['re_cold'] = df['re_rel_9m'] < 0

# (4) CHEAP: VNINDEX_PE below 30th pct of its EXPANDING history (causal, min 3y warmup)
def expanding_pctile(s):
    out = np.full(len(s), np.nan)
    vals = s.values
    for i in range(len(vals)):
        if i < 252 * 3 or np.isnan(vals[i]):
            continue
        hist = vals[:i + 1]
        hist = hist[~np.isnan(hist)]
        out[i] = (hist <= vals[i]).mean()
    return out
df['pe_pctile'] = expanding_pctile(df['vni_pe'])
df['cheap'] = df['pe_pctile'] < 0.30

# ---------------- flags ----------------
df['flag3'] = df['rates_easing'] & df['re_cold'] & df['cheap']            # no gold (2008+)
df['flag4'] = df['flag3'] & df['gold_falling']                            # +gold (2016+)
df['rates_only'] = df['rates_easing']                                     # single-signal baseline

def rising_edges(flag):
    f = flag.fillna(False).astype(int)
    return df.index[(f.diff() == 1)].tolist()

print("=" * 78)
print("BOTTOM-RECOVERY REGIME  —  job Taylor_20260706_111335  (DISPLAY-ONLY)")
print("=" * 78)
print(f"Frame: {df['time'].min().date()} .. {df['time'].max().date()}  ({len(df)} sessions)")
print(f"Gold coverage starts: {df.dropna(subset=['gold'])['time'].min().date()}  (flag4 only valid after)")
print()

def summarise(name, mask):
    m = mask.fillna(False)
    n_days = int(m.sum())
    base = df.dropna(subset=['fwd60'])
    row = {}
    for h in (60, 120, 250):
        sub = df.loc[m].dropna(subset=[f'fwd{h}'])
        b = base[f'fwd{h}'].dropna()
        row[h] = (sub[f'fwd{h}'].mean() if len(sub) else np.nan,
                  sub[f'fwd{h}'].median() if len(sub) else np.nan,
                  (sub[f'fwd{h}'] > 0).mean() if len(sub) else np.nan,
                  len(sub))
    print(f"--- {name}: {n_days} flagged sessions ---")
    print(f"   {'H':>4} {'mean':>8} {'median':>8} {'hit%':>6} {'n':>5}   |  baseline mean")
    for h in (60, 120, 250):
        mn, md, hit, n = row[h]
        bm = base[f'fwd{h}'].mean()
        print(f"   {h:>4} {mn*100:>7.1f}% {md*100:>7.1f}% {hit*100:>5.0f}% {n:>5}   |  {bm*100:>6.1f}%")
    return row

print("### Forward VNINDEX returns after flag TRUE (vs unconditional baseline)")
summarise("flag4 (rates+RE+cheap+gold, 2016+)", df['flag4'])
print()
summarise("flag3 (rates+RE+cheap, 2008+)", df['flag3'])
print()
summarise("rates_only (single signal, baseline)", df['rates_only'])
print()
summarise("cheap-only", df['cheap'])
print()

# ---------------- episodes / clustering ----------------
def episodes(flag, gap=30):
    idx = rising_edges(flag)
    # collapse rising edges that are within `gap` sessions into one episode start
    eps, last = [], -10 ** 9
    m = flag.fillna(False).values
    # find contiguous TRUE runs
    runs = []
    i = 0
    while i < len(m):
        if m[i]:
            j = i
            while j + 1 < len(m) and (m[j + 1] or (j + 1 - i) < 0):
                j += 1
            # extend across small gaps
            k = j
            while k + 1 < len(m):
                nxt = np.where(m[k + 1:k + 1 + gap])[0]
                if len(nxt) == 0:
                    break
                k = k + 1 + nxt[-1]
            runs.append((i, k))
            i = k + 1
        else:
            i += 1
    return runs

print("### flag3 episodes (contiguous, small gaps merged) — start date, length, fwd120 at start")
for a, b in episodes(df['flag3']):
    t0 = df['time'].iloc[a].date()
    t1 = df['time'].iloc[b].date()
    f120 = df['fwd120'].iloc[a]
    print(f"   {t0} .. {t1}  ({b - a + 1:>3} sess)  fwd120@start = {f120*100:>6.1f}%" if pd.notna(f120)
          else f"   {t0} .. {t1}  ({b - a + 1:>3} sess)  fwd120@start = n/a")
print()
print("### flag4 episodes (2016+ only)")
for a, b in episodes(df['flag4']):
    t0 = df['time'].iloc[a].date(); t1 = df['time'].iloc[b].date()
    f120 = df['fwd120'].iloc[a]
    print(f"   {t0} .. {t1}  ({b - a + 1:>3} sess)  fwd120@start = {f120*100:>6.1f}%" if pd.notna(f120)
          else f"   {t0} .. {t1}  ({b - a + 1:>3} sess)  fwd120@start = n/a")
print()

# ---------------- known bottoms: was flag on within +/- 40 sessions? ----------------
bottoms = {
    '2008-09 GFC low (~2009-02)': '2009-02-24',
    '2011-12 low (~2012-01)':     '2012-01-06',
    '2020-03 COVID low':          '2020-03-24',
    '2022-11 low':                '2022-11-15',
}
print("### Did flags fire NEAR known VNINDEX bottoms? (window ±40 sessions)")
for label, d in bottoms.items():
    dt = pd.to_datetime(d)
    win = df[(df['time'] >= dt - pd.Timedelta(days=90)) & (df['time'] <= dt + pd.Timedelta(days=60))]
    f3 = win['flag3'].fillna(False).any()
    f4 = win['flag4'].fillna(False).any()
    ro = win['rates_only'].fillna(False).any()
    # lead/lag of flag3 first-true vs bottom
    ft = win[win['flag3'].fillna(False)]['time']
    lead = (dt - ft.min()).days if len(ft) else None
    print(f"   {label:<32} flag3={str(f3):<5} flag4={str(f4):<5} rates_only={str(ro):<5}  "
          f"flag3 first-fire lead = {lead if lead is not None else 'n/a'} days before low")
print()

# live snapshot
last = df.iloc[-1]
print("### LIVE snapshot (last session)")
print(f"   date={last['time'].date()}  VNI={last['vni']:.0f}  PE={last['vni_pe']:.1f} (pctile={last['pe_pctile']:.2f})")
print(f"   rates_easing={bool(last['rates_easing'])}  re_cold={bool(last['re_cold'])}  "
      f"cheap={bool(last['cheap'])}  gold_falling={bool(last['gold_falling'])}")
print(f"   flag3={bool(last['flag3'])}  flag4={bool(last['flag4'])}")
print("=" * 78)
