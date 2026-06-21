"""
Direction 3: Anticipate CRISIS exit — fire boost WHILE state is still CRISIS,
when capitulation + low-PE conditions are met, BEFORE state machine confirms exit.

Trigger:
  - state == 1 (CRISIS) NOW
  - crisis_dur_so_far >= MIN_DUR (already sufficient capitulation)
  - pe_rank <= PE_TH (cheap historically)
  - Optional confirmation: RSI(14) bullish divergence (RSI rising while price still falling)

Hold:
  - HOLD_DAYS sessions OR until state regresses deeper (no regression possible from CRISIS — drop)
  - Cooldown after a fire to avoid re-firing the same capitulation

Baseline BA NAV is flat in CRISIS (cash). Boost adds margin × VNI return.
"""

import pandas as pd
import numpy as np
from itertools import product

# --- Load ---
ba = pd.read_csv('ba_v11_nav.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
vni = pd.read_csv('VNINDEX.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
vni['Pe'] = pd.to_numeric(vni['Pe'], errors='coerce')
vni['pe_rank'] = vni['Pe'].expanding(min_periods=252).apply(
    lambda s: s.rank(pct=True).iloc[-1], raw=False
)
vni['vni_ret'] = vni['Close'].pct_change().fillna(0.0)

# RSI Wilder(14)
def rsi_wilder(close, n=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/n, adjust=False, min_periods=n).mean()
    avg_loss = loss.ewm(alpha=1/n, adjust=False, min_periods=n).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - 100/(1+rs)

vni['rsi14'] = rsi_wilder(vni['Close'], 14)

# Bullish divergence: in last K sessions, price made a new K-low BUT
# RSI at this low > RSI at price low K sessions ago.
def bullish_div(close, rsi, K=20):
    out = np.zeros(len(close), dtype=bool)
    cl = close.values; rs = rsi.values
    for i in range(K, len(cl)):
        win = cl[i-K:i+1]
        rwin = rs[i-K:i+1]
        if np.isnan(rwin).any():
            continue
        # Current price is the min over window AND RSI now > RSI at the prev local low half
        if cl[i] == win.min():
            # find the earlier low in the first half
            half = K // 2
            earlier_min_idx = int(np.argmin(cl[i-K:i-half+1]))
            earlier_min_price = cl[i-K:i-half+1][earlier_min_idx]
            earlier_min_rsi = rs[i-K:i-half+1][earlier_min_idx]
            # Lower low in price, higher low in RSI
            if cl[i] < earlier_min_price and rs[i] > earlier_min_rsi:
                out[i] = True
    return out

vni['bull_div'] = bullish_div(vni['Close'], vni['rsi14'], K=20)

# Load state
state = pd.read_csv('_state.csv', parse_dates=['time'])

# Merge
df = ba.merge(vni[['time','Close','Pe','pe_rank','vni_ret','rsi14','bull_div']], on='time', how='left')
df = df.merge(state, on='time', how='left')
df['state'] = df['state'].ffill()
df['ba_ret'] = df['BA_v11'].pct_change().fillna(0.0)

# Track running CRISIS duration (today inclusive)
crisis_dur = []
cur = 0
for st in df['state'].values:
    if st == 1:
        cur += 1
    else:
        cur = 0
    crisis_dur.append(cur)
df['crisis_dur'] = crisis_dur

# --- Backtest ---
def run_anticipate(df, pe_th, min_dur, margin_pct, hold_days,
                    require_div=False, borrow_annual=0.10, cooldown=180):
    n = len(df)
    boosted = df['BA_v11'].copy().values.astype(float)
    overlay_left = 0
    cooldown_left = 0
    fired = []
    daily_borrow = borrow_annual / 250.0

    state_arr = df['state'].fillna(3).values
    pe_rank = df['pe_rank'].values
    vni_ret = df['vni_ret'].values
    dur = df['crisis_dur'].values
    div = df['bull_div'].values
    ba_ret = df['ba_ret'].values

    for i in range(1, n):
        boosted[i] = boosted[i-1] * (1 + ba_ret[i])

        if overlay_left == 0 and cooldown_left == 0:
            cond = (state_arr[i] == 1
                    and dur[i] >= min_dur
                    and not np.isnan(pe_rank[i])
                    and pe_rank[i] <= pe_th)
            if require_div:
                cond = cond and bool(div[i])
            if cond:
                overlay_left = hold_days
                cooldown_left = cooldown
                fired.append((df['time'].iloc[i], pe_rank[i], int(dur[i]), bool(div[i])))

        if overlay_left > 0:
            extra = margin_pct * (vni_ret[i] - daily_borrow)
            boosted[i] = boosted[i-1] * (1 + ba_ret[i] + extra)
            overlay_left -= 1

        if cooldown_left > 0:
            cooldown_left -= 1

    return boosted, fired

def stats(nav, dates):
    rets = pd.Series(nav).pct_change().dropna()
    n_years = (dates.iloc[-1] - dates.iloc[0]).days / 365.25
    cagr = (nav[-1] / nav[0]) ** (1.0/n_years) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(250) if rets.std() > 0 else 0
    cummax = pd.Series(nav).cummax()
    dd = (pd.Series(nav) / cummax - 1).min()
    calmar = cagr / abs(dd) if dd != 0 else 0
    return dict(cagr=cagr*100, sharpe=sharpe, dd=dd*100, calmar=calmar)

base = stats(df['BA_v11'].values, df['time'])
print(f"Baseline BA v11: CAGR={base['cagr']:.2f}% Sh={base['sharpe']:.2f} DD={base['dd']:.2f}% Calmar={base['calmar']:.2f}")
print()

print("=== Grid: NO divergence requirement ===")
print(f"{'PE_th':>6} {'mindur':>7} {'margin':>6} {'hold':>4} {'n_fire':>6} "
      f"{'CAGR':>7} {'dCAGR':>7} {'Sh':>5} {'DD':>7} {'Calmar':>6}")
rows = []
for pe_th, min_dur, margin_pct, hold_days in product(
    [0.05, 0.10, 0.15], [30, 50, 70], [0.20, 0.30, 0.50], [60, 90, 120]):
    nav, fires = run_anticipate(df, pe_th, min_dur, margin_pct, hold_days,
                                 require_div=False)
    s = stats(nav, df['time'])
    rows.append({'pe_th':pe_th, 'min_dur':min_dur, 'margin':margin_pct,
                 'hold':hold_days, 'n_fire':len(fires), **s,
                 'dCAGR':s['cagr']-base['cagr']})
res_nodiv = pd.DataFrame(rows)
print(res_nodiv.nlargest(12, 'cagr').to_string(index=False))
print()
print(res_nodiv.nlargest(8, 'sharpe')[['pe_th','min_dur','margin','hold','n_fire','cagr','dCAGR','sharpe','dd','calmar']].to_string(index=False))

print()
print("=== Grid: WITH bullish divergence required ===")
rows = []
for pe_th, min_dur, margin_pct, hold_days in product(
    [0.05, 0.10, 0.20, 0.30], [20, 30, 50], [0.20, 0.30, 0.50], [60, 90, 120]):
    nav, fires = run_anticipate(df, pe_th, min_dur, margin_pct, hold_days,
                                 require_div=True)
    s = stats(nav, df['time'])
    rows.append({'pe_th':pe_th, 'min_dur':min_dur, 'margin':margin_pct,
                 'hold':hold_days, 'n_fire':len(fires), **s,
                 'dCAGR':s['cagr']-base['cagr']})
res_div = pd.DataFrame(rows)
print(res_div.nlargest(12, 'cagr').to_string(index=False))

# --- Fire detail for chosen config ---
print()
print("=== Fires detail: PE<=10%, mindur=50, margin=30%, hold=90, NO div ===")
nav, fires = run_anticipate(df, 0.10, 50, 0.30, 90, require_div=False)
for d, pr, dr, dv in fires:
    print(f"  {d.date()}  PE_rank={pr:.3f}  CRISIS_so_far={dr} phien  bull_div={dv}")
print(f"  -> final stats: {stats(nav, df['time'])}")

print()
print("=== Fires detail: PE<=20%, mindur=30, margin=30%, hold=90, WITH div ===")
nav, fires = run_anticipate(df, 0.20, 30, 0.30, 90, require_div=True)
for d, pr, dr, dv in fires:
    print(f"  {d.date()}  PE_rank={pr:.3f}  CRISIS_so_far={dr} phien  bull_div={dv}")
print(f"  -> final stats: {stats(nav, df['time'])}")

# Compare per-fire outcome: forward 60d VNI return at fire
print()
print("=== Per-fire forward 60d/120d VNI returns ===")
nav, fires = run_anticipate(df, 0.20, 30, 0.30, 90, require_div=True)
vni_idx = df.set_index('time')
for d, pr, dr, dv in fires:
    idx = df.index[df['time']==d][0]
    fwd60 = df['Close'].iloc[min(idx+60,len(df)-1)] / df['Close'].iloc[idx] - 1
    fwd120 = df['Close'].iloc[min(idx+120,len(df)-1)] / df['Close'].iloc[idx] - 1
    print(f"  {d.date()}: PE={pr:.3f} CRISIS={dr} VNI fwd60={fwd60*100:+.2f}% fwd120={fwd120*100:+.2f}%")

res_nodiv.to_csv('anticipate_exit_grid_nodiv.csv', index=False)
res_div.to_csv('anticipate_exit_grid_div.csv', index=False)
