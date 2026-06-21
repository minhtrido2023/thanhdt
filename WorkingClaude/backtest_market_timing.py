"""
Backtest Market Timing Systems on VNINDEX 2000-2026
=====================================================
So sanh 8 he thong xac dinh trang thai thi truong:
  0. Buy & Hold (benchmark)
  1. MA200 Cross
  2. RSI Momentum (oversold/overbought)
  3. MA200 + RSI Combo
  4. MACD Trend
  5. Old PE Rule (market_rule.md - chi tu 2016)
  6. New Multi-factor Rule (de xuat moi)
  7. 5-State Machine (unified system)

Output: performance metrics, equity curves, best system recommendation
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
CSV_PATH = r"/home/trido/thanhdt/WorkingClaude/VNINDEX.csv"

NEEDED_COLS = [
    'time', 'Close', 'MA200',
    'D_RSI', 'D_CMF', 'D_MACDdiff',
    'VNINDEX_PE', 'Change_3M', 'Change_1M',
    'D_RSI_T1', 'D_RSI_T1W',
]

print("Loading VNINDEX data...")
df = pd.read_csv(CSV_PATH, usecols=lambda c: c in NEEDED_COLS + ['MA200_T1'], low_memory=False)
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time').reset_index(drop=True)

# Compute daily return of VNINDEX
df['daily_ret'] = df['Close'].pct_change().fillna(0)

# Compute trailing 3-month change if not available
if 'Change_3M' not in df.columns or df['Change_3M'].isna().all():
    df['Change_3M'] = df['Close'].pct_change(63)

# Clip/clean
df['D_RSI'] = pd.to_numeric(df['D_RSI'], errors='coerce')
df['D_CMF'] = pd.to_numeric(df['D_CMF'], errors='coerce')
df['D_MACDdiff'] = pd.to_numeric(df['D_MACDdiff'], errors='coerce')
df['MA200']  = pd.to_numeric(df['MA200'],  errors='coerce')
df['VNINDEX_PE'] = pd.to_numeric(df['VNINDEX_PE'], errors='coerce')
df['Change_3M']  = pd.to_numeric(df['Change_3M'],  errors='coerce')
df['Change_1M']  = pd.to_numeric(df['Change_1M'],  errors='coerce')

print(f"Data: {df['time'].min().date()} -> {df['time'].max().date()} ({len(df)} rows)")

# ─────────────────────────────────────────────
# 2. COMPUTE PE PERCENTILES (2016+ only)
# ─────────────────────────────────────────────
pe_series = df['VNINDEX_PE'].dropna()
pe_pct = {
    'P10': np.percentile(pe_series, 10),
    'P20': np.percentile(pe_series, 20),
    'P30': np.percentile(pe_series, 30),
    'P40': np.percentile(pe_series, 40),
    'P50': np.percentile(pe_series, 50),
    'P60': np.percentile(pe_series, 60),
    'P65': np.percentile(pe_series, 65),
    'P70': np.percentile(pe_series, 70),
    'P75': np.percentile(pe_series, 75),
    'P80': np.percentile(pe_series, 80),
    'P85': np.percentile(pe_series, 85),
    'P90': np.percentile(pe_series, 90),
    'P95': np.percentile(pe_series, 95),
}
print("\nVNINDEX_PE Percentiles (2016-2026):")
for k, v in pe_pct.items():
    print(f"  {k} = {v:.2f}x")

# ─────────────────────────────────────────────
# 3. SIGNAL GENERATION FUNCTIONS
# ─────────────────────────────────────────────

def signal_buyhold(df):
    """Always in market."""
    return pd.Series(1, index=df.index)

def signal_ma200(df):
    """
    IN when Close > MA200
    OUT when Close < MA200
    """
    sig = pd.Series(0, index=df.index)
    valid = df['MA200'].notna()
    sig[valid] = np.where(df.loc[valid, 'Close'] > df.loc[valid, 'MA200'], 1, 0)
    # Before MA200 available (first ~200 days), assume IN
    sig[~valid] = 1
    return sig

def signal_rsi(df):
    """
    IN: RSI < 0.35 (oversold) or RSI crosses up from < 0.40
    OUT: RSI > 0.70 (overbought)
    State machine: track position
    """
    rsi = df['D_RSI'].fillna(0.5)
    sig = pd.Series(0, index=df.index)
    in_market = True  # start IN
    for i in range(len(df)):
        r = rsi.iloc[i]
        if in_market:
            if r > 0.72:
                in_market = False
        else:
            if r < 0.35:
                in_market = True
        sig.iloc[i] = 1 if in_market else 0
    return sig

def signal_ma200_rsi(df):
    """
    IN: Close > MA200 AND RSI < 0.68
    OUT: Close < MA200 OR RSI > 0.72
    State machine
    """
    ma200 = df['MA200'].ffill()
    rsi = df['D_RSI'].fillna(0.5)
    close = df['Close']

    sig = pd.Series(0, index=df.index)
    in_market = True
    for i in range(len(df)):
        above_ma = close.iloc[i] > ma200.iloc[i] if pd.notna(ma200.iloc[i]) else True
        r = rsi.iloc[i]
        if in_market:
            if (not above_ma) or r > 0.73:
                in_market = False
        else:
            if above_ma and r < 0.60:
                in_market = True
        sig.iloc[i] = 1 if in_market else 0
    return sig

def signal_macd(df):
    """
    IN: MACDdiff >= 0 (bullish momentum)
    OUT: MACDdiff < 0 (bearish momentum)
    With 2-day confirmation to avoid whipsaws
    """
    macd = df['D_MACDdiff'].fillna(0)
    sig = pd.Series(0, index=df.index)
    in_market = True
    out_count = 0
    in_count  = 0
    for i in range(len(df)):
        m = macd.iloc[i]
        if in_market:
            if m < 0:
                out_count += 1
                in_count = 0
                if out_count >= 2:
                    in_market = False
                    out_count = 0
            else:
                out_count = 0
        else:
            if m > 0:
                in_count += 1
                out_count = 0
                if in_count >= 2:
                    in_market = True
                    in_count = 0
            else:
                in_count = 0
        sig.iloc[i] = 1 if in_market else 0
    return sig

def signal_old_pe_rule(df, pe_pct):
    """
    Old market_rule.md logic (2016+):
    - Sell trigger: PE >= P60 (16.3x)
    - Block window based on PE level:
      P60-P65: 30 days
      P65-P80: 60 days
      P80-P90: 90 days
      P90-P95: 365 days
      >=P95:   545 days
    - Reopen: PE <= P60 (or after window expiry)
    - Extreme rule: if sell_pe >= P90 -> need PE <= P20 to reopen

    Before 2016 (no PE): use MA200 filter
    """
    P60 = pe_pct['P60']
    P65 = pe_pct['P65']
    P80 = pe_pct['P80']
    P90 = pe_pct['P90']
    P95 = pe_pct['P95']
    P20 = pe_pct['P20']

    ma200 = df['MA200'].ffill()
    pe    = df['VNINDEX_PE']
    close = df['Close']
    time  = df['time']

    sig = pd.Series(0, index=df.index)
    in_market   = True
    block_until = None
    extreme_block = False  # sell_pe >= P90: need PE<=P20

    for i in range(len(df)):
        pe_val  = pe.iloc[i]
        cl      = close.iloc[i]
        ma_val  = ma200.iloc[i] if pd.notna(ma200.iloc[i]) else cl
        t       = time.iloc[i]
        has_pe  = pd.notna(pe_val)

        if not has_pe:
            # Pre-2016: use MA200
            in_market = (cl > ma_val)
            block_until = None
            extreme_block = False
        else:
            # Check if block expired
            if block_until is not None and t >= block_until:
                if extreme_block:
                    # Need PE <= P20 to unlock
                    if pe_val <= P20:
                        block_until = None
                        extreme_block = False
                        in_market = True
                else:
                    block_until = None
                    in_market = True

            if in_market:
                # Sell trigger
                if pe_val >= P60:
                    in_market = False
                    # Determine block window
                    if pe_val >= P95:
                        window = 545
                    elif pe_val >= P90:
                        window = 365
                    elif pe_val >= P80:
                        window = 90
                    elif pe_val >= P65:
                        window = 60
                    else:
                        window = 30
                    block_until = t + timedelta(days=window)
                    extreme_block = (pe_val >= P90)
            # (if not in_market, wait for block_until or PE condition)

        sig.iloc[i] = 1 if in_market else 0
    return sig

def signal_new_rule(df, pe_pct):
    """
    Proposed improved rule:
    - Sell trigger: PE >= P75 AND RSI > 0.65 AND Close > MA200
    - Block window: shorter
      P75-P80: 30 days
      P80-P90: 60 days
      P90-P95: 120 days
      >=P95:   180 days
    - Reopen: PE <= P60 OR RSI < 0.35 (BullDvgVNI proxy) OR after window
    - Extreme rule: if sell_pe >= P90 -> PE <= P40 OR RSI < 0.35
    - PANIC override: RSI < 0.30 AND below MA200 AND Change_3M < -20% -> FORCE IN

    Before 2016: use MA200 + RSI combo
    """
    P40 = pe_pct['P40']
    P60 = pe_pct['P60']
    P75 = pe_pct['P75']
    P80 = pe_pct['P80']
    P90 = pe_pct['P90']
    P95 = pe_pct['P95']

    ma200   = df['MA200'].ffill()
    pe      = df['VNINDEX_PE']
    rsi     = df['D_RSI'].fillna(0.5)
    close   = df['Close']
    c3m     = df['Change_3M'].fillna(0)
    time    = df['time']

    sig = pd.Series(0, index=df.index)
    in_market   = True
    block_until = None
    extreme_block = False

    for i in range(len(df)):
        pe_val  = pe.iloc[i]
        cl      = close.iloc[i]
        ma_val  = ma200.iloc[i] if pd.notna(ma200.iloc[i]) else cl
        r       = rsi.iloc[i]
        c3      = c3m.iloc[i]
        t       = time.iloc[i]
        has_pe  = pd.notna(pe_val)
        above_ma = (cl > ma_val)

        # PANIC override: RSI < 0.30 + below MA200 + C3M < -20%
        if r < 0.30 and (not above_ma) and c3 < -0.20:
            in_market = True
            block_until = None
            extreme_block = False
            sig.iloc[i] = 1
            continue

        if not has_pe:
            # Pre-2016: MA200 + RSI combo
            if in_market:
                if (not above_ma) or r > 0.73:
                    in_market = False
            else:
                if above_ma and r < 0.60:
                    in_market = True
        else:
            # Check block expiry
            if block_until is not None and t >= block_until:
                if extreme_block:
                    # Need PE <= P40 OR RSI < 0.35
                    if pe_val <= P40 or r < 0.35:
                        block_until = None
                        extreme_block = False
                        in_market = True
                else:
                    block_until = None
                    in_market = True

            # Check if still blocked - check reopen conditions
            if not in_market and block_until is not None:
                if extreme_block:
                    if pe_val <= P40 or r < 0.35:
                        block_until = None
                        extreme_block = False
                        in_market = True
                else:
                    if pe_val <= P60 or r < 0.35:
                        block_until = None
                        in_market = True

            if in_market:
                # Sell trigger: PE >= P75 AND RSI > 0.65 AND above MA200
                if has_pe and pe_val >= P75 and r > 0.65 and above_ma:
                    in_market = False
                    if pe_val >= P95:
                        window = 180
                    elif pe_val >= P90:
                        window = 120
                    elif pe_val >= P80:
                        window = 60
                    else:  # P75-P80
                        window = 30
                    block_until = t + timedelta(days=window)
                    extreme_block = (pe_val >= P90)

        sig.iloc[i] = 1 if in_market else 0
    return sig

def signal_5state_machine(df, pe_pct):
    """
    5-State Machine (most comprehensive):
    States:
      PANIC    → 100% IN (strong buy)
      BEAR     → 0% (OUT)
      CAUTION  → 0% (OUT or partial - for simplicity: OUT)
      BULL     → 100% IN
      NEUTRAL  → 100% IN

    State rules (with PE, 2016+):
      PANIC:   RSI < 0.30 AND below MA200 AND C3M < -0.15
      BEAR:    below MA200 AND RSI < 0.45 AND MACDdiff < 0
      CAUTION: PE >= P75 AND RSI > 0.65 AND above MA200
      BULL:    above MA200 AND MACDdiff >= 0 AND RSI < 0.70
      NEUTRAL: default

    Without PE (pre-2016):
      PANIC:   RSI < 0.30 AND below MA200 AND C3M < -0.20
      BEAR:    below MA200 AND RSI < 0.45 AND MACDdiff < 0
      CAUTION: above MA200 AND RSI > 0.72 AND C3M > 0.20
      BULL:    above MA200 AND MACDdiff >= 0 AND RSI < 0.68
      NEUTRAL: default

    With hysteresis: once in BEAR/CAUTION, need stronger signal to revert
    """
    P30 = pe_pct['P30']
    P40 = pe_pct['P40']
    P75 = pe_pct['P75']

    ma200   = df['MA200'].ffill()
    pe      = df['VNINDEX_PE']
    rsi     = df['D_RSI'].fillna(0.5)
    macd    = df['D_MACDdiff'].fillna(0)
    cmf     = df['D_CMF'].fillna(0)
    close   = df['Close']
    c3m     = df['Change_3M'].fillna(0)
    c1m     = df['Change_1M'].fillna(0)

    states = []
    sig    = pd.Series(0, index=df.index)
    prev_state = 'NEUTRAL'

    for i in range(len(df)):
        cl      = close.iloc[i]
        ma_val  = ma200.iloc[i] if pd.notna(ma200.iloc[i]) else cl
        r       = rsi.iloc[i]
        m       = macd.iloc[i]
        cf      = cmf.iloc[i]
        c3      = c3m.iloc[i]
        c1      = c1m.iloc[i]
        pe_val  = pe.iloc[i]
        has_pe  = pd.notna(pe_val)
        above_ma = (cl > ma_val)

        # ── Determine state ──
        # PANIC: extreme oversold with deep drawdown
        panic_cond = (r < 0.30 and (not above_ma) and c3 < -0.15)

        if has_pe:
            # BEAR: clear downtrend
            bear_cond = ((not above_ma) and r < 0.45 and m < 0)
            # CAUTION: overbought + overvalued
            caution_cond = (pe_val >= P75 and r > 0.65 and above_ma)
            # BULL: uptrend + not overvalued
            bull_cond = (above_ma and m >= 0 and r < 0.70 and pe_val < P75)
        else:
            bear_cond    = ((not above_ma) and r < 0.45 and m < 0)
            caution_cond = (above_ma and r > 0.72 and c3 > 0.18)
            bull_cond    = (above_ma and m >= 0 and r < 0.68)

        # State machine with hysteresis
        if panic_cond:
            state = 'PANIC'
        elif bear_cond:
            state = 'BEAR'
        elif caution_cond:
            state = 'CAUTION'
        elif bull_cond:
            state = 'BULL'
        else:
            # Hysteresis: stay in previous defensive state unless bullish
            if prev_state in ('BEAR', 'CAUTION'):
                # Need positive signal to exit defensive
                if above_ma and r < 0.60 and m >= 0:
                    state = 'NEUTRAL'
                else:
                    state = prev_state
            else:
                state = 'NEUTRAL'

        prev_state = state
        states.append(state)

        # Position: IN for PANIC, BULL, NEUTRAL; OUT for BEAR, CAUTION
        sig.iloc[i] = 1 if state in ('PANIC', 'BULL', 'NEUTRAL') else 0

    df['_state'] = states
    return sig, states

# ─────────────────────────────────────────────
# 4. BACKTEST ENGINE
# ─────────────────────────────────────────────
CASH_DAILY_RATE = 0.06 / 252  # 6% annual -> daily

def backtest(df, signal, name="Strategy", cash_rate=CASH_DAILY_RATE):
    """
    Simulate portfolio. Signal = 1 → hold VNINDEX, Signal = 0 → hold cash.
    Assume: trade at next day's open (= today's close for simplicity).
    """
    n = len(df)
    portfolio = np.zeros(n)
    portfolio[0] = 100.0

    sig = signal.values
    ret = df['daily_ret'].values

    for i in range(1, n):
        prev = portfolio[i-1]
        if sig[i-1] == 1:  # in market yesterday -> get today's market return
            portfolio[i] = prev * (1 + ret[i])
        else:  # in cash -> get cash rate
            portfolio[i] = prev * (1 + cash_rate)

    # ── Metrics ──
    port_s = pd.Series(portfolio, index=df.index)
    years  = (df['time'].iloc[-1] - df['time'].iloc[0]).days / 365.25

    total_ret = (portfolio[-1] / portfolio[0] - 1) * 100
    cagr      = ((portfolio[-1] / portfolio[0]) ** (1/years) - 1) * 100

    # Max drawdown
    peak = np.maximum.accumulate(portfolio)
    dd   = (portfolio - peak) / peak
    max_dd = dd.min() * 100

    # Daily returns of portfolio
    port_ret = np.diff(portfolio) / portfolio[:-1]
    sharpe   = (np.mean(port_ret) / np.std(port_ret)) * np.sqrt(252) if np.std(port_ret) > 0 else 0

    # Calmar ratio
    calmar = cagr / abs(max_dd) if max_dd != 0 else 0

    # Time in market
    time_in = sig.mean() * 100

    # Number of trades (signal changes)
    trades = int(np.sum(np.abs(np.diff(sig.astype(int)))))

    return {
        'name': name,
        'total_ret': total_ret,
        'cagr': cagr,
        'max_dd': max_dd,
        'sharpe': sharpe,
        'calmar': calmar,
        'time_in': time_in,
        'trades': trades,
        'portfolio': port_s,
    }

# ─────────────────────────────────────────────
# 5. PERIOD-SPECIFIC ANALYSIS
# ─────────────────────────────────────────────
PERIODS = {
    'Full (2000-2026)':   ('2000-01-01', '2026-12-31'),
    'Bull (2000-2007)':   ('2000-01-01', '2007-12-31'),
    'Bear (2007-2009)':   ('2007-10-01', '2009-03-31'),
    'Recovery (2009-14)': ('2009-03-01', '2014-12-31'),
    'Post-reform (2016-2021)': ('2016-01-01', '2021-04-30'),
    'Volatile (2021-2026)': ('2021-01-01', '2026-04-30'),
    'PE era (2016-2026)':  ('2016-04-01', '2026-04-30'),
}

# ─────────────────────────────────────────────
# 6. RUN ALL SYSTEMS
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("GENERATING SIGNALS...")
print("="*65)

sig0 = signal_buyhold(df)
sig1 = signal_ma200(df)
sig2 = signal_rsi(df)
sig3 = signal_ma200_rsi(df)
sig4 = signal_macd(df)
sig5 = signal_old_pe_rule(df, pe_pct)
sig6 = signal_new_rule(df, pe_pct)
sig7, states7 = signal_5state_machine(df, pe_pct)

SYSTEMS = [
    (sig0, "0. Buy & Hold"),
    (sig1, "1. MA200 Cross"),
    (sig2, "2. RSI Momentum"),
    (sig3, "3. MA200+RSI Combo"),
    (sig4, "4. MACD Trend"),
    (sig5, "5. Old PE Rule (mkt_rule)"),
    (sig6, "6. New Multi-factor Rule"),
    (sig7, "7. 5-State Machine"),
]

# ─────────────────────────────────────────────
# 7. FULL PERIOD RESULTS
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("BACKTEST: TOAN BO GIAI DOAN 2000-2026")
print("="*65)
print(f"{'System':<28} {'TotalRet':>9} {'CAGR':>7} {'MaxDD':>8} {'Sharpe':>7} {'Calmar':>7} {'%InMkt':>7} {'Trades':>7}")
print("-"*80)

results_full = {}
for sig, name in SYSTEMS:
    r = backtest(df, sig, name)
    results_full[name] = r
    print(f"{name:<28} {r['total_ret']:>8.1f}% {r['cagr']:>6.1f}% {r['max_dd']:>7.1f}% {r['sharpe']:>7.2f} {r['calmar']:>7.2f} {r['time_in']:>6.1f}% {r['trades']:>6d}")

# ─────────────────────────────────────────────
# 8. PERIOD-BY-PERIOD ANALYSIS
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("BACKTEST: THEO TUNG GIAI DOAN")
print("="*65)

for period_name, (start, end) in PERIODS.items():
    mask = (df['time'] >= start) & (df['time'] <= end)
    sub  = df[mask].copy().reset_index(drop=True)
    if len(sub) < 60:
        continue
    print(f"\n── {period_name} ({sub['time'].iloc[0].date()} -> {sub['time'].iloc[-1].date()}, {len(sub)} rows) ──")
    print(f"  VNINDEX: {sub['Close'].iloc[0]:.0f} -> {sub['Close'].iloc[-1]:.0f} ({(sub['Close'].iloc[-1]/sub['Close'].iloc[0]-1)*100:.1f}%)")
    print(f"  {'System':<28} {'CAGR':>7} {'MaxDD':>8} {'Sharpe':>7} {'Calmar':>7}")

    for sig, name in SYSTEMS:
        sub_sig = sig[mask].reset_index(drop=True)
        # Need to recompute daily_ret for sub period
        sub2 = sub.copy()
        r = backtest(sub2, sub_sig, name)
        marker = " ★" if name.startswith("7.") else ""
        print(f"  {name:<28} {r['cagr']:>6.1f}% {r['max_dd']:>7.1f}% {r['sharpe']:>7.2f} {r['calmar']:>7.2f}{marker}")

# ─────────────────────────────────────────────
# 9. STATE DISTRIBUTION ANALYSIS (System 7)
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("5-STATE MACHINE: PHAN BO TRANG THAI VA FORWARD RETURN")
print("="*65)

df['_state'] = states7

# Forward 3M return
df['fwd_3m'] = df['Close'].shift(-63) / df['Close'] - 1
df['fwd_1m'] = df['Close'].shift(-21) / df['Close'] - 1

for state in ['PANIC', 'BEAR', 'CAUTION', 'BULL', 'NEUTRAL']:
    mask = df['_state'] == state
    n = mask.sum()
    if n < 5:
        continue
    fwd3 = df.loc[mask, 'fwd_3m'].dropna()
    fwd1 = df.loc[mask, 'fwd_1m'].dropna()
    print(f"\n  State: {state:<10} (n={n:,d} days, {n/len(df)*100:.1f}% of time)")
    print(f"    Fwd 1M: median={fwd1.median()*100:+.1f}%  win={( fwd1>0).mean()*100:.1f}%")
    print(f"    Fwd 3M: median={fwd3.median()*100:+.1f}%  win={(fwd3>0).mean()*100:.1f}%")
    # PE range in state
    pe_in_state = df.loc[mask, 'VNINDEX_PE'].dropna()
    if len(pe_in_state) > 0:
        print(f"    PE range: {pe_in_state.min():.1f}x - {pe_in_state.max():.1f}x (median {pe_in_state.median():.1f}x)")
    close_in_state = df.loc[mask, 'Close']
    print(f"    VNINDEX range: {close_in_state.min():.0f} - {close_in_state.max():.0f}")

# ─────────────────────────────────────────────
# 10. KEY MARKET EVENTS TEST
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("KIEM TRA TAI CAC SU KIEN QUAN TRONG")
print("="*65)

KEY_EVENTS = {
    '2006-01 Bull start':        '2006-01-03',
    '2007-03 VNI peak 1170':     '2007-03-12',
    '2008-03 Bear start':        '2008-03-01',
    '2009-02 Bear bottom':       '2009-02-24',
    '2009-07 Recovery':          '2009-07-01',
    '2012-01 Bear bottom 350':   '2012-01-09',
    '2015-06 VNI 600 peak':      '2015-06-08',
    '2016-02 Low after sell-off':'2016-02-12',
    '2018-04 VNI 1200 peak':     '2018-04-09',
    '2018-10 Bear 2H2018':       '2018-10-23',
    '2020-03 COVID crash':        '2020-03-23',
    '2021-11 VNI 1500 peak':     '2021-11-24',
    '2022-11 Bear bottom 900':   '2022-11-16',
    '2024-07 VNI 1300+':         '2024-07-01',
    '2026-04 Current':           '2026-04-17',
}

print(f"\n{'Event':<32} {'VNINDEX':>8} {'RSI':>6} {'PE':>6} {'State':>10}")
print("-"*72)
for event, date_str in KEY_EVENTS.items():
    try:
        dt = pd.to_datetime(date_str)
        idx = df['time'].searchsorted(dt)
        if idx >= len(df):
            idx = len(df) - 1
        row = df.iloc[idx]
        pe_str = f"{row['VNINDEX_PE']:.1f}x" if pd.notna(row['VNINDEX_PE']) else "N/A"
        state  = row.get('_state', 'N/A')
        print(f"{event:<32} {row['Close']:>8.0f} {row['D_RSI']:>6.2f} {pe_str:>6} {state:>10}")
    except:
        pass

# ─────────────────────────────────────────────
# 11. OPTIMAL PARAMETER SEARCH (System 7 variants)
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("OPTIMAL THRESHOLD SEARCH (5-State Machine PE era 2016+)")
print("="*65)

pe_mask = df['VNINDEX_PE'].notna()
df_pe = df[pe_mask].copy().reset_index(drop=True)
df_pe['daily_ret'] = df_pe['Close'].pct_change().fillna(0)

best_calmar = -999
best_params = {}

for p_sell in [70, 72, 75, 78, 80]:       # PE sell percentile
    for rsi_sell in [0.62, 0.65, 0.68, 0.70]:  # RSI sell threshold
        for rsi_bear in [0.40, 0.43, 0.45, 0.48]:  # RSI bear threshold
            for rsi_panic in [0.28, 0.30, 0.32, 0.35]:  # RSI panic threshold

                pe_sell_val = np.percentile(pe_series, p_sell)

                ma200_p = df_pe['MA200'].ffill()
                rsi_p   = df_pe['D_RSI'].fillna(0.5)
                macd_p  = df_pe['D_MACDdiff'].fillna(0)
                close_p = df_pe['Close']
                c3m_p   = df_pe['Change_3M'].fillna(0)
                pe_p    = df_pe['VNINDEX_PE']

                sig_opt = pd.Series(0, index=df_pe.index)
                prev_st = 'NEUTRAL'

                for i in range(len(df_pe)):
                    cl = close_p.iloc[i]
                    ma = ma200_p.iloc[i] if pd.notna(ma200_p.iloc[i]) else cl
                    r  = rsi_p.iloc[i]
                    m  = macd_p.iloc[i]
                    c3 = c3m_p.iloc[i]
                    pv = pe_p.iloc[i]
                    above = (cl > ma)

                    if r < rsi_panic and not above and c3 < -0.15:
                        st = 'PANIC'
                    elif not above and r < rsi_bear and m < 0:
                        st = 'BEAR'
                    elif pv >= pe_sell_val and r > rsi_sell and above:
                        st = 'CAUTION'
                    elif above and m >= 0 and r < 0.70 and pv < pe_sell_val:
                        st = 'BULL'
                    else:
                        if prev_st in ('BEAR', 'CAUTION'):
                            if above and r < 0.60 and m >= 0:
                                st = 'NEUTRAL'
                            else:
                                st = prev_st
                        else:
                            st = 'NEUTRAL'
                    prev_st = st
                    sig_opt.iloc[i] = 1 if st in ('PANIC', 'BULL', 'NEUTRAL') else 0

                r_opt = backtest(df_pe, sig_opt, "opt")
                if r_opt['calmar'] > best_calmar and r_opt['trades'] < 200:
                    best_calmar = r_opt['calmar']
                    best_params = {
                        'pe_pctile': p_sell,
                        'pe_val': pe_sell_val,
                        'rsi_sell': rsi_sell,
                        'rsi_bear': rsi_bear,
                        'rsi_panic': rsi_panic,
                        'cagr': r_opt['cagr'],
                        'max_dd': r_opt['max_dd'],
                        'sharpe': r_opt['sharpe'],
                        'calmar': r_opt['calmar'],
                        'time_in': r_opt['time_in'],
                        'trades': r_opt['trades'],
                    }

print("\nBest parameters (by Calmar ratio, PE era 2016+):")
for k, v in best_params.items():
    if isinstance(v, float):
        print(f"  {k}: {v:.4f}")
    else:
        print(f"  {k}: {v}")

# ─────────────────────────────────────────────
# 12. FINAL RECOMMENDATION
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("KET LUAN VA HE THONG DE XUAT")
print("="*65)

# Compare top 3 systems on full period
ranked = sorted(results_full.values(), key=lambda x: x['calmar'], reverse=True)
print("\nTop 3 systems by Calmar ratio (Full period):")
for i, r in enumerate(ranked[:3], 1):
    print(f"  {i}. {r['name']}: CAGR={r['cagr']:.1f}%, MaxDD={r['max_dd']:.1f}%, Calmar={r['calmar']:.2f}, Sharpe={r['sharpe']:.2f}")

# PE era specific
results_pe = {}
pe_start = df[df['VNINDEX_PE'].notna()]['time'].min()
mask_pe = df['time'] >= pe_start
sub_pe = df[mask_pe].copy().reset_index(drop=True)
sub_pe['daily_ret'] = sub_pe['Close'].pct_change().fillna(0)
for sig, name in SYSTEMS:
    sub_sig = sig[mask_pe].reset_index(drop=True)
    r = backtest(sub_pe, sub_sig, name)
    results_pe[name] = r

ranked_pe = sorted(results_pe.values(), key=lambda x: x['calmar'], reverse=True)
print(f"\nTop 3 systems by Calmar ratio (PE era {pe_start.date()} onwards):")
for i, r in enumerate(ranked_pe[:3], 1):
    print(f"  {i}. {r['name']}: CAGR={r['cagr']:.1f}%, MaxDD={r['max_dd']:.1f}%, Calmar={r['calmar']:.2f}, Sharpe={r['sharpe']:.2f}")

# ─────────────────────────────────────────────
# 13. CURRENT MARKET STATE
# ─────────────────────────────────────────────
print("\n" + "="*65)
print("TRANG THAI THI TRUONG HIEN TAI (2026-04-17)")
print("="*65)

latest = df[df['time'] <= '2026-04-18'].iloc[-1]
print(f"\n  VNINDEX:    {latest['Close']:.0f}")
print(f"  MA200:      {latest['MA200']:.0f} ({'above' if latest['Close'] > latest['MA200'] else 'BELOW'})")
print(f"  RSI:        {latest['D_RSI']:.3f}")
print(f"  CMF:        {latest['D_CMF']:.3f}")
print(f"  MACDdiff:   {latest['D_MACDdiff']:.4f}")
print(f"  PE:         {latest['VNINDEX_PE']:.2f}x" if pd.notna(latest['VNINDEX_PE']) else "  PE:         N/A")
print(f"  Change_3M:  {latest['Change_3M']*100:.1f}%" if pd.notna(latest['Change_3M']) else "  Change_3M:  N/A")
print(f"  State (5SM):{latest['_state']}")
print(f"  Signal 7:   {'IN' if sig7[df['time'] <= '2026-04-18'].iloc[-1] == 1 else 'OUT'}")
print(f"  Signal 6:   {'IN' if sig6[df['time'] <= '2026-04-18'].iloc[-1] == 1 else 'OUT'}")
print(f"  Signal 5:   {'IN' if sig5[df['time'] <= '2026-04-18'].iloc[-1] == 1 else 'OUT'}")

# ─────────────────────────────────────────────
# 14. SAVE EQUITY CURVES
# ─────────────────────────────────────────────
curves = pd.DataFrame({'time': df['time']})
for sig, name in SYSTEMS:
    r = backtest(df, sig, name)
    col = name.split('.')[0].strip() + '_' + name.split('. ')[1].replace(' ', '_')[:20]
    curves[col] = r['portfolio'].values

curves['VNINDEX_Close'] = df['Close'].values
curves['state_5SM'] = states7
curves.to_csv(
    r"/home/trido/thanhdt/WorkingClaude/market_timing_equity_curves.csv",
    index=False
)
print("\nEquity curves saved to market_timing_equity_curves.csv")

print("\n" + "="*65)
print("DONE.")
print("="*65)
