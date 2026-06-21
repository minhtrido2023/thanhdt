# -*- coding: utf-8 -*-
"""
VNINDEX Market State Analysis
5-State Classification: PE + P3M + Technical Indicators
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# --- 1. LOAD DATA ---
CSV_PATH = r'/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv'

cols_needed = [
    'time', 'Close', 'VNINDEX_PE', 'O3M',
    'VNINDEX_RSI', 'VNINDEX_CMF', 'VNINDEX_MA200',
    'MA200', 'D_RSI', 'D_CMF', 'D_RSI_T1W',
    'VNINDEX_PE_MA2Y', 'VNINDEX_PE_MA4Y', 'VNINDEX_PE_MA5Y'
]

df_full = pd.read_csv(CSV_PATH, parse_dates=['time'], low_memory=False)
print(f"Loaded {len(df_full):,} rows from CSV")

available = [c for c in cols_needed if c in df_full.columns]
missing_cols = [c for c in cols_needed if c not in df_full.columns]
if missing_cols:
    print(f"Missing columns (will skip): {missing_cols}")

df = df_full[available].copy()
df = df.sort_values('time').reset_index(drop=True)

# --- 2. COMPUTE P3M ---
df['P3M'] = 100.0 * (df['O3M'] - 1.0)

# --- 3. DROP ROWS WHERE PE OR O3M IS NaN ---
df_valid = df.dropna(subset=['VNINDEX_PE', 'O3M']).copy()
print(f"Rows with valid PE + O3M: {len(df_valid):,}  "
      f"(date range: {df_valid['time'].min().date()} to {df_valid['time'].max().date()})")

# --- 4. COMPUTE PE PERCENTILES ---
pe_series = df_valid['VNINDEX_PE']
pe_pcts = {
    'P5':  np.percentile(pe_series, 5),
    'P10': np.percentile(pe_series, 10),
    'P20': np.percentile(pe_series, 20),
    'P40': np.percentile(pe_series, 40),
    'P60': np.percentile(pe_series, 60),
    'P65': np.percentile(pe_series, 65),
    'P80': np.percentile(pe_series, 80),
    'P90': np.percentile(pe_series, 90),
    'P95': np.percentile(pe_series, 95),
}

# --- 5. COMPUTE P3M PERCENTILES ---
p3m_series = df_valid['P3M']
p3m_pcts = {
    'P5':  np.percentile(p3m_series, 5),
    'P10': np.percentile(p3m_series, 10),
    'P20': np.percentile(p3m_series, 20),
    'P50': np.percentile(p3m_series, 50),
    'P80': np.percentile(p3m_series, 80),
    'P90': np.percentile(p3m_series, 90),
    'P95': np.percentile(p3m_series, 95),
}

# --- 6. CLASSIFY EACH ROW INTO 5 STATES ---
def classify_state(row):
    pe    = row['VNINDEX_PE']
    p3m   = row['P3M']
    close = row['Close']
    ma200 = row.get('VNINDEX_MA200', row.get('MA200', np.nan))
    above_ma200 = (not pd.isna(ma200)) and (close > ma200)

    # State 1: EUPHORIA -- PE extreme AND momentum extreme
    if pe >= pe_pcts['P90'] and p3m >= p3m_pcts['P80']:
        return 1

    # State 5: OVERSELL / PANIC -- deep crash in 3M return
    if p3m <= p3m_pcts['P10']:
        return 5

    # State 2: EXPENSIVE / CAUTION -- PE elevated OR momentum elevated
    if pe >= pe_pcts['P60'] or p3m >= p3m_pcts['P80']:
        return 2

    # State 4: CHEAP / OPPORTUNITY -- PE low AND above MA200
    if pe <= pe_pcts['P20'] and above_ma200:
        return 4

    # State 3: NEUTRAL -- everything in between
    return 3

df_valid['State'] = df_valid.apply(classify_state, axis=1)

STATE_LABELS = {
    1: "EUPHORIA / VERY EXPENSIVE",
    2: "EXPENSIVE / CAUTION",
    3: "NEUTRAL",
    4: "CHEAP / OPPORTUNITY",
    5: "OVERSELL / PANIC",
}

STATE_ALLOCATION = {
    1: "Cash 80-100% (minimal equity)",
    2: "Cash 50-70%",
    3: "Cash 30-40%",
    4: "Cash 20-30% (accumulate on dips)",
    5: "Cash 10-20% (contrarian accumulation)",
}

# --- 7. CURRENT (LAST) ROW ---
last = df_valid.iloc[-1]
cur_date   = last['time'].date()
cur_close  = last['Close']
cur_pe     = last['VNINDEX_PE']
cur_p3m    = last['P3M']
cur_rsi    = last.get('VNINDEX_RSI', last.get('D_RSI', np.nan))
cur_cmf    = last.get('VNINDEX_CMF', last.get('D_CMF', np.nan))
cur_ma200  = last.get('VNINDEX_MA200', last.get('MA200', np.nan))

cur_pe_ma2y = last.get('VNINDEX_PE_MA2Y', np.nan)
cur_pe_ma4y = last.get('VNINDEX_PE_MA4Y', np.nan)
cur_pe_ma5y = last.get('VNINDEX_PE_MA5Y', np.nan)

cur_state  = last['State']
above_ma200 = (not pd.isna(cur_ma200)) and (cur_close > cur_ma200)

cur_pe_pctile  = (pe_series <= cur_pe).mean() * 100
cur_p3m_pctile = (p3m_series <= cur_p3m).mean() * 100

# --- 8. FORWARD RETURN STATS BY STATE ---
df_valid = df_valid.reset_index(drop=True)
df_valid['fwd_3M'] = df_valid['Close'].shift(-60) / df_valid['Close'] - 1
df_valid['fwd_6M'] = df_valid['Close'].shift(-120) / df_valid['Close'] - 1

state_stats = {}
for s in [1, 2, 3, 4, 5]:
    sub = df_valid[df_valid['State'] == s]
    n = len(sub)
    fwd3_mean = sub['fwd_3M'].dropna().mean() * 100
    fwd6_mean = sub['fwd_6M'].dropna().mean() * 100
    pe_mean   = sub['VNINDEX_PE'].mean()
    p3m_mean  = sub['P3M'].mean()
    state_stats[s] = {
        'n': n,
        'pct': n / len(df_valid) * 100,
        'fwd_3M_avg': fwd3_mean,
        'fwd_6M_avg': fwd6_mean,
        'pe_avg': pe_mean,
        'p3m_avg': p3m_mean,
    }

# --- 9. PE HISTOGRAM (TEXT) ---
pe_min = pe_series.min()
pe_max = pe_series.max()
n_bins = 20
bins = np.linspace(pe_min, pe_max, n_bins + 1)
hist, edges = np.histogram(pe_series, bins=bins)
max_count = max(hist)
bar_width = 40

def pe_histogram_text(hist, edges, cur_pe, max_count, bar_width):
    lines = []
    lines.append(f"  {'PE Range':<16} {'Count':>6}  {'Distribution (# = frequency)':<{bar_width}}  Note")
    lines.append("  " + "-" * 78)
    for lo, hi, cnt in zip(edges[:-1], edges[1:], hist):
        bar_len = int(cnt / max_count * bar_width)
        bar = '#' * bar_len
        note = "<< CURRENT" if lo <= cur_pe < hi else ""
        lines.append(f"  {lo:6.1f} -{hi:6.1f}  {cnt:>6}  {bar:<{bar_width}}  {note}")
    return "\n".join(lines)

# --- 10. RECENT TREND (last 20 trading days) ---
recent = df_valid.tail(20)[['time', 'Close', 'VNINDEX_PE', 'P3M', 'State']].copy()

# --- 11. STATE TRANSITIONS ---
df_valid['prev_state'] = df_valid['State'].shift(1)
df_valid['state_change'] = df_valid['State'] != df_valid['prev_state']
last_changes = df_valid[df_valid['state_change']].tail(8)

# --- PRINT REPORT ---
SEP = "=" * 80
SEC = "-" * 80

print()
print(SEP)
print("  VNINDEX MARKET STATE ANALYSIS -- 5-STATE CLASSIFICATION SYSTEM")
print(f"  Analysis Date: 2026-04-23  |  Latest Data: {cur_date}")
print(SEP)

print()
print(SEC)
print("  SECTION 1: CURRENT MARKET VALUES")
print(SEC)
print(f"  VNINDEX Close:          {cur_close:>10.2f}")
print(f"  VNINDEX MA200:          {cur_ma200:>10.2f}  ({'ABOVE' if above_ma200 else 'BELOW'} MA200)")
print(f"  MA200 gap:              {(cur_close/cur_ma200 - 1)*100:>+9.2f}%")
print()
print(f"  VNINDEX PE (current):   {cur_pe:>10.2f}  (historical pctile: {cur_pe_pctile:.1f}%)")
if not pd.isna(cur_pe_ma2y):
    print(f"  PE vs MA2Y ({cur_pe_ma2y:.2f}):   {(cur_pe/cur_pe_ma2y - 1)*100:>+9.2f}%")
if not pd.isna(cur_pe_ma4y):
    print(f"  PE vs MA4Y ({cur_pe_ma4y:.2f}):   {(cur_pe/cur_pe_ma4y - 1)*100:>+9.2f}%")
if not pd.isna(cur_pe_ma5y):
    print(f"  PE vs MA5Y ({cur_pe_ma5y:.2f}):   {(cur_pe/cur_pe_ma5y - 1)*100:>+9.2f}%")
print()
print(f"  P3M (3M return):        {cur_p3m:>+9.2f}%  (historical pctile: {cur_p3m_pctile:.1f}%)")

rsi_val = cur_rsi
if not pd.isna(rsi_val) and rsi_val <= 1.0:
    rsi_val = rsi_val * 100
print(f"  VNINDEX RSI (0-100):    {rsi_val:>10.2f}")
print(f"  VNINDEX CMF:            {cur_cmf:>10.4f}")

print()
print(SEC)
print("  SECTION 2: PE PERCENTILE THRESHOLDS")
print(SEC)
print(f"  {'Percentile':<12}  {'PE Value':>10}  Meaning")
print(f"  {'-'*70}")
meanings = {
    'P5':  'Extreme cheapness (rare)',
    'P10': 'Very cheap',
    'P20': 'Cheap threshold -- State 4 boundary',
    'P40': 'Below median',
    'P60': 'Caution threshold -- State 2 boundary',
    'P65': 'Moderately expensive',
    'P80': 'Expensive',
    'P90': 'Euphoria threshold -- State 1 boundary',
    'P95': 'Extreme overvaluation',
}
for k, v in pe_pcts.items():
    pnum = float(k[1:])
    marker = "  << CURRENT" if abs(cur_pe_pctile - pnum) < 5 else ""
    print(f"  {k:<12}  {v:>10.2f}  {meanings.get(k, '')}{marker}")
print(f"  {'CURRENT PE':<12}  {cur_pe:>10.2f}  [{cur_pe_pctile:.1f}th percentile]")

print()
print(SEC)
print("  SECTION 3: P3M (3-MONTH RETURN) PERCENTILE THRESHOLDS")
print(SEC)
print(f"  {'Percentile':<12}  {'P3M Value':>12}  Meaning")
print(f"  {'-'*70}")
p3m_meanings = {
    'P5':  'Extreme crash (rare)',
    'P10': 'Panic/oversell threshold -- State 5 boundary',
    'P20': 'Weak/declining market',
    'P50': 'Median 3M return',
    'P80': 'Overbought threshold -- State 1/2 boundary',
    'P90': 'Strong momentum',
    'P95': 'Extreme momentum (rare)',
}
for k, v in p3m_pcts.items():
    pnum = float(k[1:])
    marker = "  << CURRENT" if abs(cur_p3m_pctile - pnum) < 5 else ""
    print(f"  {k:<12}  {v:>+11.2f}%  {p3m_meanings.get(k, '')}{marker}")
print(f"  {'CURRENT P3M':<12}  {cur_p3m:>+11.2f}%  [{cur_p3m_pctile:.1f}th percentile]")

print()
print(SEC)
print("  SECTION 4: CURRENT STATE DETERMINATION")
print(SEC)
print(f"  Current State:  STATE {cur_state} -- {STATE_LABELS[cur_state]}")
print(f"  Allocation:     {STATE_ALLOCATION[cur_state]}")
print()
print("  Reasoning:")
print(f"    PE = {cur_pe:.2f} (pctile {cur_pe_pctile:.1f}%)")
print(f"      vs P20={pe_pcts['P20']:.2f}, P60={pe_pcts['P60']:.2f}, P90={pe_pcts['P90']:.2f}")
print(f"    P3M = {cur_p3m:+.2f}% (pctile {cur_p3m_pctile:.1f}%)")
print(f"      vs P10={p3m_pcts['P10']:+.2f}%, P80={p3m_pcts['P80']:+.2f}%")
print(f"    MA200 position: {'ABOVE' if above_ma200 else 'BELOW'} "
      f"(Close={cur_close:.2f}, MA200={cur_ma200:.2f})")
print()

if cur_state == 1:
    print("    [EUPHORIA] PE in top 10% AND 3M momentum in top 20%.")
    print("    Market is both fundamentally expensive and momentum-extended.")
    print("    Historically high risk of sharp correction. Reduce equity significantly.")
elif cur_state == 2:
    print("    [EXPENSIVE/CAUTION] PE >= P60 OR P3M >= P80.")
    if cur_pe >= pe_pcts['P60']:
        print(f"    PE ({cur_pe:.2f}) exceeds P60 ({pe_pcts['P60']:.2f}) -- valuations stretched.")
    if cur_p3m >= p3m_pcts['P80']:
        print(f"    P3M ({cur_p3m:+.2f}%) exceeds P80 ({p3m_pcts['P80']:+.2f}%) -- market overbought.")
    print("    Reduce exposure, wait for better entry points.")
elif cur_state == 3:
    print("    [NEUTRAL] PE and P3M both within normal ranges.")
    print("    Standard allocation. No strong bias for over- or under-weighting equity.")
elif cur_state == 4:
    print("    [CHEAP/OPPORTUNITY] PE <= P20 AND market above MA200.")
    print("    Valuations are historically cheap and trend is intact.")
    print("    Good entry zone for long-term accumulation.")
elif cur_state == 5:
    print("    [OVERSELL/PANIC] P3M <= P10 (deep 3-month crash).")
    print("    Market in capitulation zone. Contrarian accumulation opportunity.")
    print("    High volatility -- scale in gradually.")

print()
print(SEC)
print("  SECTION 5: HISTORICAL STATE DISTRIBUTION")
print(SEC)
print(f"  {'St':<3}  {'Label':<28}  {'Days':>6}  {'%Time':>6}  {'AvgPE':>7}  "
      f"{'AvgP3M':>8}  {'Fwd3M':>7}  {'Fwd6M':>7}")
print(f"  {'-'*80}")
for s in [1, 2, 3, 4, 5]:
    st = state_stats[s]
    cur_mk = " <<" if s == cur_state else ""
    print(f"  {s:<3}  {STATE_LABELS[s]:<28}  {st['n']:>6}  {st['pct']:>5.1f}%  "
          f"{st['pe_avg']:>7.2f}  {st['p3m_avg']:>+7.2f}%  "
          f"{st['fwd_3M_avg']:>+6.1f}%  {st['fwd_6M_avg']:>+6.1f}%{cur_mk}")
print()
print("  Note: Fwd3M/Fwd6M = avg forward return using 60/120 trading-day shifts")

print()
print(SEC)
print("  SECTION 6: PE HISTOGRAM (HISTORICAL DISTRIBUTION)")
print(SEC)
print(f"  PE range: {pe_min:.1f} to {pe_max:.1f} | Current PE: {cur_pe:.2f} ({cur_pe_pctile:.1f}th pctile)")
print(f"  Mean PE: {pe_series.mean():.2f} | Median PE: {pe_series.median():.2f} | Std: {pe_series.std():.2f}")
print()
print(pe_histogram_text(hist, edges, cur_pe, max_count, bar_width))

print()
print(SEC)
print("  SECTION 7: RECENT 20-DAY MARKET HISTORY")
print(SEC)
print(f"  {'Date':<12}  {'Close':>8}  {'PE':>6}  {'P3M':>8}  {'St':<3}  Label")
print(f"  {'-'*75}")
for _, row in recent.iterrows():
    s = int(row['State'])
    print(f"  {str(row['time'].date()):<12}  {row['Close']:>8.2f}  "
          f"{row['VNINDEX_PE']:>6.2f}  {row['P3M']:>+7.2f}%  {s:<3}  {STATE_LABELS[s]}")

print()
print(SEC)
print("  SECTION 8: RECENT STATE TRANSITIONS")
print(SEC)
print(f"  {'Date':<12}  {'From':>4}  ->  {'To':<3}  Label")
print(f"  {'-'*65}")
for _, row in last_changes.iterrows():
    prev = row['prev_state']
    cur_s = row['State']
    prev_str = f"{int(prev)}" if not pd.isna(prev) else "?"
    print(f"  {str(row['time'].date()):<12}  {prev_str:>4}  ->  {int(cur_s):<3}  {STATE_LABELS[int(cur_s)]}")

print()
print(SEC)
print("  SECTION 9: PE vs MOVING AVERAGES (VALUATION CONTEXT)")
print(SEC)
if 'VNINDEX_PE_MA2Y' in df_valid.columns:
    pe_ma2y_s = df_valid['VNINDEX_PE_MA2Y'].values
    pe_ma4y_s = df_valid['VNINDEX_PE_MA4Y'].values
    pe_ma5y_s = df_valid['VNINDEX_PE_MA5Y'].values
    pe_vals   = df_valid['VNINDEX_PE'].values
    pe_rel2y  = (pe_vals / pe_ma2y_s - 1) * 100
    pe_rel4y  = (pe_vals / pe_ma4y_s - 1) * 100
    pe_rel5y  = (pe_vals / pe_ma5y_s - 1) * 100

    print(f"  {'Metric':<28}  {'vs 2Y MA':>10}  {'vs 4Y MA':>10}  {'vs 5Y MA':>10}")
    print(f"  {'-'*65}")
    print(f"  {'PE MA value (current)':28}  {cur_pe_ma2y:>10.2f}  {cur_pe_ma4y:>10.2f}  {cur_pe_ma5y:>10.2f}")
    print(f"  {'Current PE vs MA (%)':28}  "
          f"{(cur_pe/cur_pe_ma2y-1)*100:>+9.2f}%  "
          f"{(cur_pe/cur_pe_ma4y-1)*100:>+9.2f}%  "
          f"{(cur_pe/cur_pe_ma5y-1)*100:>+9.2f}%")
    print()
    print(f"  Historical PE-vs-MA distribution:")
    print(f"  {'Pctile':<12}  {'PE/MA2Y-1':>12}  {'PE/MA4Y-1':>12}  {'PE/MA5Y-1':>12}")
    print(f"  {'-'*55}")
    for p in [10, 25, 50, 75, 90]:
        r2 = np.nanpercentile(pe_rel2y, p)
        r4 = np.nanpercentile(pe_rel4y, p)
        r5 = np.nanpercentile(pe_rel5y, p)
        print(f"  P{p:<10}  {r2:>+11.1f}%  {r4:>+11.1f}%  {r5:>+11.1f}%")

    cur_r2_pct = float(np.nanmean(pe_rel2y <= (cur_pe/cur_pe_ma2y-1)*100)*100)
    cur_r4_pct = float(np.nanmean(pe_rel4y <= (cur_pe/cur_pe_ma4y-1)*100)*100)
    cur_r5_pct = float(np.nanmean(pe_rel5y <= (cur_pe/cur_pe_ma5y-1)*100)*100)
    print(f"  {'CURRENT pctile':<12}  {cur_r2_pct:>11.1f}%  {cur_r4_pct:>11.1f}%  {cur_r5_pct:>11.1f}%")
else:
    print("  PE MA columns not found.")

print()
print(SEC)
print("  SECTION 10: ALLOCATION SUMMARY")
print(SEC)
print(f"  Current State: {cur_state} -- {STATE_LABELS[cur_state]}")
print()
print(f"  Recommended:  {STATE_ALLOCATION[cur_state]}")
print()
print("  Full allocation guide:")
for s in [1, 2, 3, 4, 5]:
    marker = "  << CURRENT" if s == cur_state else ""
    print(f"    State {s}: {STATE_LABELS[s]:<28}  {STATE_ALLOCATION[s]}{marker}")

print()
print(SEP)
print("  END OF ANALYSIS")
print(SEP)
