#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macro_confidence_regime.py  (RESEARCH / DISPLAY-ONLY — job Taylor_20260706_100438)

Tests a SPECIFIC user hypothesis (not simple pairwise correlation):

  "When gold rises AND USD/VND rises AND (inflation is high OR bank deposit rates
   rise) — usually a sign the public is losing confidence in state policy — it is a
   BAD regime for stocks: thin liquidity (low turnover) AND broad price decline."

This is a COMBINED (multi-variable, simultaneous) regime, tested on its own — the
prior job (Taylor_20260706_094519) only found SBV policy-rate had a stable link and
gold/USD alone were noise. A joint regime can behave differently, so we test it fresh.

Inputs (all local / repo, DISPLAY-ONLY, nothing touches production):
  - VNINDEX level + fwd returns : data/macro_features.csv   (2011-01 .. 2026-05)
  - Market turnover (VND/day)   : /tmp/vn_turnover.csv       SUM(Trading_Value) ticker_prune (BQ)
  - Gold (world, USD/oz)        : /tmp/gold_world.csv        (2016-07+)  <-- limits full regime
  - USD/VND                     : data/macro_features.csv    (2011+)
  - CPI YoY (%)                 : cpi_vn.py         PROXY anchor series (see file header)
  - Big-4 12M deposit rate (%)  : deposit_rate_vn.py PROXY step series (see file header)

Outputs: stdout tables + /tmp charts. Writes nothing to production paths.
"""
import json, warnings
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import sys
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from cpi_vn import merge_cpi
from deposit_rate_vn import merge_deposit

ROOT = '/home/trido/thanhdt/WorkingClaude'

# ---------------- load & assemble daily frame ----------------
mf = pd.read_csv(f'{ROOT}/data/macro_features.csv', parse_dates=['time'])
mf = mf[['time', 'VNI', 'DXY', 'USDVND']].sort_values('time').reset_index(drop=True)

turn = pd.read_csv('/tmp/vn_turnover.csv', parse_dates=['time'])[['time', 'turnover']]
gold = pd.read_csv('/tmp/gold_world.csv', parse_dates=['time']).rename(columns={'close': 'GOLD'})

df = mf.merge(turn, on='time', how='left').merge(gold[['time', 'GOLD']], on='time', how='left')
df = df.sort_values('time').reset_index(drop=True)
df = merge_cpi(df)        # adds cpi_yoy, cpi_yoy_chg3  (monthly, as-of backward)
df = merge_deposit(df)    # adds deposit_rate           (step, as-of backward)

# ---------------- derived signals ----------------
TD = 21   # ~trading days / month
df['VNI_ret'] = df['VNI'].pct_change()

# forward VNINDEX returns (recompute, no look-ahead — pure shift of realized level)
df['fwd20'] = df['VNI'].shift(-20) / df['VNI'] - 1.0
df['fwd60'] = df['VNI'].shift(-60) / df['VNI'] - 1.0

# volatility
df['vol20'] = df['VNI_ret'].rolling(20).std() * np.sqrt(252)

# turnover normalised to its OWN trailing 1y median (turnover has huge secular uptrend;
# raw VND is not comparable across 2011 vs 2026). rel<1 == "thinner than typical".
df['turn_med252'] = df['turnover'].rolling(252, min_periods=120).median()
df['turn_rel'] = df['turnover'] / df['turn_med252']

# momentum (level today vs N trading days ago)
df['gold_mom126'] = df['GOLD'] / df['GOLD'].shift(6 * TD) - 1.0      # 6-month gold momentum
df['gold_mom63']  = df['GOLD'] / df['GOLD'].shift(3 * TD) - 1.0      # 3-month
df['usd_mom126']  = df['USDVND'] / df['USDVND'].shift(6 * TD) - 1.0
df['usd_mom63']   = df['USDVND'] / df['USDVND'].shift(3 * TD) - 1.0
# deposit-rate change over last 6 months (rising = tightening / stress)
df['dep_chg6m']   = df['deposit_rate'] - df['deposit_rate'].shift(6 * TD)

print(f"[range] {df.time.min().date()} .. {df.time.max().date()}  ({len(df)} rows)")
print(f"[gold ] first valid gold: {df.loc[df.GOLD.first_valid_index(),'time'].date()}")

# ---------------- regime flags (several thresholds, not one) ----------------
# "monetary/inflation stress" leg: CPI accelerating OR high, OR deposit rate rising
df['infl_hot']  = (df['cpi_yoy_chg3'] > 0) | (df['cpi_yoy'] > 4.0)
df['dep_rising'] = df['dep_chg6m'] > 0
df['stress_leg'] = df['infl_hot'] | df['dep_rising']

# gold & usd "up" legs
df['gold_up126'] = df['gold_mom126'] > 0
df['usd_up126']  = df['usd_mom126'] > 0

# --- Regime A: FULL user hypothesis, 6m momentum (needs gold -> 2016+) ---
df['REG_A'] = df['gold_up126'] & df['usd_up126'] & df['stress_leg']

# --- Regime A_strict: require CPI HIGH>4 AND deposit rising (both), gold+usd up ---
df['REG_A_strict'] = df['gold_up126'] & df['usd_up126'] & (df['cpi_yoy'] > 4.0) & df['dep_rising']

# --- Regime B: DROP gold (world price, weak VN link + short sample) -> 2011+ longer sample ---
#     confidence loss = USD up AND (inflation hot OR deposit rising)
df['REG_B'] = df['usd_up126'] & df['stress_leg']

# --- Regime C: pure monetary stress, ignore FX/gold (2011+): CPI hot OR deposit rising ---
df['REG_C'] = df['stress_leg']

REGIMES = ['REG_A', 'REG_A_strict', 'REG_B', 'REG_C']

# ---------------- group comparison ----------------
def summarize(mask, label):
    d = df[mask]
    n = len(d)
    if n == 0:
        print(f"  {label:14s} n=0  (never true)")
        return None
    row = dict(
        regime=label, n=n, days_pct=100 * n / df[['fwd60']].dropna().shape[0],
        fwd20=100 * d['fwd20'].mean(), fwd20_med=100 * d['fwd20'].median(),
        fwd20_pos=100 * (d['fwd20'] > 0).mean(),
        fwd60=100 * d['fwd60'].mean(), fwd60_med=100 * d['fwd60'].median(),
        fwd60_pos=100 * (d['fwd60'] > 0).mean(),
        turn_rel=d['turn_rel'].median(), vol20=100 * d['vol20'].median(),
    )
    return row

print("\n" + "=" * 100)
print("GROUP COMPARISON — regime TRUE vs FALSE  (fwd = forward VNINDEX return %, turn_rel = turnover/1y-median)")
print("=" * 100)
hdr = f"{'regime':16s} {'n':>5s} {'%days':>6s} | {'fwd20':>7s} {'f20med':>7s} {'f20+%':>6s} | {'fwd60':>7s} {'f60med':>7s} {'f60+%':>6s} | {'turnR':>6s} {'vol20':>6s}"
for reg in REGIMES:
    print("-" * 100)
    print(hdr)
    for val, tag in [(True, f"{reg}=TRUE"), (False, f"{reg}=FALSE")]:
        m = (df[reg] == val) & df['fwd60'].notna()
        # for REG_A/A_strict also require gold present (else FALSE is polluted by pre-2016 no-gold)
        if reg in ('REG_A', 'REG_A_strict'):
            m = m & df['GOLD'].notna()
        r = summarize(m, tag)
        if r:
            print(f"{r['regime']:16s} {r['n']:5d} {r['days_pct']:5.1f}% | "
                  f"{r['fwd20']:6.2f}% {r['fwd20_med']:6.2f}% {r['fwd20_pos']:5.0f}% | "
                  f"{r['fwd60']:6.2f}% {r['fwd60_med']:6.2f}% {r['fwd60_pos']:5.0f}% | "
                  f"{r['turn_rel']:5.2f}x {r['vol20']:5.1f}%")

# ---------------- event study: contiguous regime episodes ----------------
def episodes(reg, min_gap=5, min_len=10, need_gold=False):
    d = df.copy()
    if need_gold:
        d = d[d['GOLD'].notna()]
    d = d.reset_index(drop=True)
    flag = d[reg].fillna(False).values
    eps, i, N = [], 0, len(d)
    while i < N:
        if flag[i]:
            j = i
            gap = 0
            k = i
            while k < N:
                if flag[k]:
                    j = k; gap = 0
                else:
                    gap += 1
                    if gap > min_gap:
                        break
                k += 1
            if j - i + 1 >= min_len:
                eps.append((i, j, d))
            i = k
        else:
            i += 1
    return eps

print("\n" + "=" * 100)
print("EVENT STUDY — contiguous episodes (allow <=5d gaps, min 10d)")
print("=" * 100)
for reg, need_gold in [('REG_A', True), ('REG_B', False), ('REG_C', False)]:
    print(f"\n### {reg} episodes ###")
    eps = episodes(reg, need_gold=need_gold)
    if not eps:
        print("  (no episodes)")
        continue
    print(f"{'start':12s} {'end':12s} {'len':>4s} | {'VNI chg during':>14s} | {'fwd60 @start':>12s} | {'turnR med':>9s} | {'cpi':>5s} {'dep':>5s}")
    for i, j, d in eps:
        seg = d.iloc[i:j + 1]
        vni_chg = 100 * (d['VNI'].iloc[j] / d['VNI'].iloc[i] - 1.0)
        f60 = seg['fwd60'].iloc[0]
        f60s = f"{100*f60:6.1f}%" if pd.notna(f60) else "   n/a"
        print(f"{d['time'].iloc[i].date()!s:12s} {d['time'].iloc[j].date()!s:12s} {j-i+1:4d} | "
              f"{vni_chg:12.1f}% | {f60s:>12s} | {seg['turn_rel'].median():7.2f}x | "
              f"{seg['cpi_yoy'].median():4.1f} {seg['deposit_rate'].median():4.1f}")

# ---------------- baseline for context ----------------
base = df[df['fwd60'].notna()]
print("\n" + "=" * 100)
print("BASELINE (all days, fwd defined):")
print(f"  fwd20 mean {100*base['fwd20'].mean():.2f}%  fwd60 mean {100*base['fwd60'].mean():.2f}%  "
      f"fwd60 +% {100*(base['fwd60']>0).mean():.0f}%  turn_rel med {base['turn_rel'].median():.2f}x  "
      f"vol20 med {100*base['vol20'].median():.1f}%")
print("=" * 100)

df.to_csv('/tmp/macro_confidence_regime_frame.csv', index=False)
print("\n[saved] /tmp/macro_confidence_regime_frame.csv")
