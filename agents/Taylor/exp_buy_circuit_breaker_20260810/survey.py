#!/usr/bin/env python3
"""Calibration survey: how big is a 'normal' intraday down-move for the names we actually buy?

All measures causal (rvol_20d uses ONLY prior sessions). Adjusted basis (Open/High/Low/Close all
verified inside the same adjusted basis; `Price` is the unadjusted column and is NOT used).
"""
import pandas as pd, numpy as np

d = pd.read_csv('bars_universe.csv', parse_dates=['time']).sort_values(['ticker', 'time'])
g = d.groupby('ticker', group_keys=False)
d['prev_close'] = g['close'].shift(1)
d['ret'] = d['close'] / d['prev_close'] - 1
# causal 20d realised vol: shift(1) so today's own return is excluded
d['rvol_20d'] = g['ret'].apply(lambda s: s.shift(1).rolling(20, min_periods=15).std())
d['dd_prevclose'] = d['low'] / d['prev_close'] - 1      # worst drop vs prior close
d['dd_open'] = d['low'] / d['open'] - 1                 # worst drop vs today's open
d['gap'] = d['open'] / d['prev_close'] - 1
d['c2o'] = d['close'] / d['open'] - 1
d['bounce'] = d['close'] / d['low'] - 1                 # recovery off the low by the close
d['range'] = d['high'] / d['low'] - 1
for h in (5, 10, 20):
    d[f'fwd{h}'] = g['close'].shift(-h) / d['close'] - 1
d['z_prevclose'] = d['dd_prevclose'] / d['rvol_20d']
d['z_open'] = d['dd_open'] / d['rvol_20d']

d['is_lag'] = d['books'].fillna('').str.contains('LAG')
d['is_park'] = d['books'].fillna('').str.contains('PARK')
v = d.dropna(subset=['rvol_20d', 'dd_prevclose', 'dd_open'])
v = v[v['rvol_20d'] > 0]
recent = v[v.time >= '2024-01-01']

def block(name, s):
    print(f"\n=== {name}  (n ticker-days = {len(s):,}, distinct tickers = {s.ticker.nunique()})")
    print(f"  rvol_20d      : med {s.rvol_20d.median()*100:5.2f}%  p25 {s.rvol_20d.quantile(.25)*100:5.2f}%  p75 {s.rvol_20d.quantile(.75)*100:5.2f}%")
    print(f"  day range H/L : med {s['range'].median()*100:5.2f}%  p90 {s['range'].quantile(.9)*100:5.2f}%")
    for col, lab in (('dd_prevclose', 'drop vs PREV CLOSE'), ('dd_open', 'drop vs OPEN     ')):
        q = s[col].quantile([.5, .25, .10, .05, .02, .01])
        print(f"  {lab}: med {q[.5]*100:6.2f}% | p25 {q[.25]*100:6.2f}% | p10 {q[.10]*100:6.2f}% | p5 {q[.05]*100:6.2f}% | p2 {q[.02]*100:6.2f}% | p1 {q[.01]*100:6.2f}%")
    for col, lab in (('z_prevclose', 'z vs PREV CLOSE'), ('z_open', 'z vs OPEN     ')):
        print(f"  {lab}: med {s[col].median():5.2f} | p10 {s[col].quantile(.10):5.2f} | p5 {s[col].quantile(.05):5.2f} | p1 {s[col].quantile(.01):5.2f}")
    print("  --- % of sessions where a breaker at threshold z would TRIP (i.e. price touched -z*rvol):")
    for z in (1.0, 1.5, 2.0, 2.5, 3.0):
        a = (s.z_prevclose <= -z).mean() * 100
        b = (s.z_open <= -z).mean() * 100
        print(f"      z={z:<4} vs prev-close {a:5.2f}%   vs open {b:5.2f}%")

block("LAG names, 2024+", recent[recent.is_lag])
block("PARK/custom30V names, 2024+", recent[recent.is_park & ~recent.is_lag])
block("SCL only, 2024+", recent[recent.ticker == 'SCL'])
