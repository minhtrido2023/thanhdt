"""
Backtest Capitulation Boost overlay on top of BA v11 baseline NAV.

Trigger: state just entered NEUTRAL (within N days of CRISIS exit) AND
         prior CRISIS duration >= MIN_CRISIS sessions AND
         PE rank <= PE_TH at the trigger date.
Action:  boost allocation = 1 + margin (e.g. 1.20) for HOLD_DAYS sessions
         OR until state regresses to CRISIS/BEAR.
Cost:    borrow rate on the margin portion (annualised).

NAV with overlay = NAV_baseline * (1 + r_baseline) + margin_pct * VNINDEX_ret_window
                 - borrow_cost * margin_pct
We approximate the boost as: extra leg on VNINDEX returns
   delta_nav[t] = nav_base[t-1] * margin_pct * (vni_ret[t] - borrow/250)
This is the simplest reasonable proxy. Sensitivity to a more accurate
"BA-leg leveraged" version is small because BA correlates ~0.6-0.8 with VNI.
"""

import pandas as pd
import numpy as np
from itertools import product

# --- Load ---
ba = pd.read_csv('data/ba_v11_nav.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
vni = pd.read_csv('data/VNINDEX.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)
vni['Pe'] = pd.to_numeric(vni['Pe'], errors='coerce')
vni['pe_rank'] = vni['Pe'].expanding(min_periods=252).apply(
    lambda s: s.rank(pct=True).iloc[-1], raw=False
)
vni['vni_ret'] = vni['Close'].pct_change().fillna(0.0)

# Load state machine (exported via: bq query ... --max_rows=10000 > _state.csv)
state = pd.read_csv('data/_state.csv', parse_dates=['time'])

# --- Merge ---
df = ba.merge(vni[['time','Close','Pe','pe_rank','vni_ret']], on='time', how='left')
df = df.merge(state, on='time', how='left')
df['state'] = df['state'].ffill()
df['ba_ret'] = df['BA_v11'].pct_change().fillna(0.0)

# --- Identify CRISIS-exit trigger dates ---
df['state_prev'] = df['state'].shift(1)
df['just_exited_crisis'] = (df['state_prev']==1) & (df['state']!=1)

# CRISIS duration ending at exit
crisis_durs = []
cur_dur = 0
for st in df['state'].values:
    if st == 1:
        cur_dur += 1
        crisis_durs.append(cur_dur)
    else:
        crisis_durs.append(cur_dur)
        cur_dur = 0
df['crisis_dur_ending'] = crisis_durs
# Snap duration at the moment of exit (one bar after state goes from 1 -> not 1)
df['prior_crisis_len'] = df['crisis_dur_ending'].shift(1).fillna(0)

# --- Backtest function ---
def run_overlay(df, pe_th, min_crisis, exit_window, margin_pct, hold_days,
                borrow_annual=0.10):
    """Returns NAV series and stats."""
    n = len(df)
    nav = df['BA_v11'].copy().values.astype(float)  # baseline NAV
    overlay_active = np.zeros(n, dtype=bool)
    overlay_left = 0  # days remaining
    fired_dates = []
    daily_borrow = borrow_annual / 250.0

    state_arr = df['state'].fillna(3).values
    pe_rank = df['pe_rank'].values
    vni_ret = df['vni_ret'].values
    just_exit = df['just_exited_crisis'].values
    prior_len = df['prior_crisis_len'].values

    # Track days since CRISIS exit
    days_since_exit = 9999
    last_exit_prior_len = 0

    boosted_nav = nav.copy()
    for i in range(1, n):
        # Apply baseline return increment
        boosted_nav[i] = boosted_nav[i-1] * (1 + df['ba_ret'].iloc[i])

        # Update days_since_exit tracker
        if just_exit[i]:
            days_since_exit = 0
            last_exit_prior_len = prior_len[i]
        else:
            days_since_exit += 1

        # Check for new trigger: within exit window, sufficient prior CRISIS, low PE
        if (overlay_left == 0
            and days_since_exit <= exit_window
            and last_exit_prior_len >= min_crisis
            and not np.isnan(pe_rank[i])
            and pe_rank[i] <= pe_th
            and state_arr[i] in (2, 3)):  # NEUTRAL or BEAR (state 2,3)
            overlay_left = hold_days
            fired_dates.append((df['time'].iloc[i], pe_rank[i], last_exit_prior_len))

        if overlay_left > 0:
            # Boost: extra leg on VNI return minus borrow cost
            extra = margin_pct * (vni_ret[i] - daily_borrow)
            boosted_nav[i] = boosted_nav[i-1] * (1 + df['ba_ret'].iloc[i] + extra)
            overlay_active[i] = True
            overlay_left -= 1
            # Force exit if state regresses to CRISIS
            if state_arr[i] == 1:
                overlay_left = 0

    return boosted_nav, overlay_active, fired_dates

def stats(nav, dates):
    rets = pd.Series(nav).pct_change().dropna()
    n_years = (dates.iloc[-1] - dates.iloc[0]).days / 365.25
    cagr = (nav[-1] / nav[0]) ** (1.0/n_years) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(250) if rets.std() > 0 else 0
    cummax = pd.Series(nav).cummax()
    dd = (pd.Series(nav) / cummax - 1).min()
    calmar = cagr / abs(dd) if dd != 0 else 0
    return dict(cagr=cagr*100, sharpe=sharpe, dd=dd*100, calmar=calmar)

# --- Baseline stats ---
base = stats(df['BA_v11'].values, df['time'])
print(f"Baseline BA v11: CAGR={base['cagr']:.2f}% Sh={base['sharpe']:.2f} DD={base['dd']:.2f}% Calmar={base['calmar']:.2f}")
print()

# --- Grid sensitivity ---
print(f"{'PE_th':>6} {'min_cr':>6} {'win':>4} {'margin':>6} {'hold':>4} {'n_fire':>6} "
      f"{'CAGR':>7} {'dCAGR':>6} {'Sh':>5} {'DD':>7} {'Calmar':>6}")
print("-"*84)

results = []
for pe_th, min_crisis, exit_window, margin_pct, hold_days in product(
        [0.05, 0.10, 0.15, 0.20],
        [30, 50],
        [10, 15, 20],
        [0.10, 0.20, 0.30],
        [60, 90, 120],
    ):
    nav, active, fires = run_overlay(df, pe_th, min_crisis, exit_window, margin_pct, hold_days)
    s = stats(nav, df['time'])
    results.append({
        'pe_th': pe_th, 'min_crisis': min_crisis, 'exit_window': exit_window,
        'margin': margin_pct, 'hold': hold_days, 'n_fire': len(fires),
        **s, 'dCAGR': s['cagr'] - base['cagr'],
    })
    if margin_pct == 0.20 and hold_days == 90 and exit_window == 15:
        print(f"{pe_th:6.2f} {min_crisis:6d} {exit_window:4d} {margin_pct:6.2f} {hold_days:4d} "
              f"{len(fires):6d} {s['cagr']:7.2f} {s['cagr']-base['cagr']:+6.2f} "
              f"{s['sharpe']:5.2f} {s['dd']:7.2f} {s['calmar']:6.2f}")

results = pd.DataFrame(results)
results.to_csv('data/capitulation_boost_grid.csv', index=False)
print()
print("=== TOP 10 by CAGR ===")
print(results.nlargest(10, 'cagr')[['pe_th','min_crisis','exit_window','margin','hold','n_fire','cagr','dCAGR','sharpe','dd','calmar']].to_string(index=False))
print()
print("=== TOP 10 by Sharpe ===")
print(results.nlargest(10, 'sharpe')[['pe_th','min_crisis','exit_window','margin','hold','n_fire','cagr','dCAGR','sharpe','dd','calmar']].to_string(index=False))
print()
print("=== TOP 10 by Calmar ===")
print(results.nlargest(10, 'calmar')[['pe_th','min_crisis','exit_window','margin','hold','n_fire','cagr','dCAGR','sharpe','dd','calmar']].to_string(index=False))

# --- Detail print of fires for a representative config ---
nav, active, fires = run_overlay(df, pe_th=0.10, min_crisis=30, exit_window=15,
                                  margin_pct=0.20, hold_days=90)
print()
print("=== Fires for config: PE<=10%, mincrisis=30, window=15, margin=20%, hold=90 ===")
for d, pr, plen in fires:
    print(f"  {d.date()}  PE_rank={pr:.3f}  prior_CRISIS={int(plen)} phiên")
