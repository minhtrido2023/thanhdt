import pandas as pd
import numpy as np

df = pd.read_csv('/home/trido/thanhdt/WorkingClaude/data/VNINDEX.csv', usecols=['time','Close'])
df['time'] = pd.to_datetime(df['time'])
df = df.sort_values('time').reset_index(drop=True)

def idx_of(date_str):
    d = pd.Timestamp(date_str)
    # find first trading day >= date_str
    sub = df[df['time'] >= d]
    if sub.empty:
        raise ValueError(f"no data on/after {date_str}")
    return sub.index[0]

def analyze_entry(label, date_str, fwd_days=(30,60,120,252), dd_window=60):
    i0 = idx_of(date_str)
    actual_date = df.loc[i0,'time'].date()
    p0 = df.loc[i0,'Close']
    window = df.loc[i0:i0+dd_window]
    dd = (window['Close']/p0 - 1)
    worst_idx = dd.idxmin()
    max_dd = dd.min()
    worst_date = df.loc[worst_idx,'time'].date()
    sessions_to_worst = worst_idx - i0
    out = {
        'label': label, 'requested_date': date_str, 'actual_trading_date': str(actual_date),
        'p0': round(p0,2), 'max_drawdown_60d': round(max_dd*100,2),
        'worst_date': str(worst_date), 'sessions_to_worst': int(sessions_to_worst),
    }
    for fd in fwd_days:
        j = i0+fd
        if j < len(df):
            ret = df.loc[j,'Close']/p0 - 1
            out[f'ret_D{fd}'] = round(ret*100,2)
            out[f'date_D{fd}'] = str(df.loc[j,'time'].date())
        else:
            out[f'ret_D{fd}'] = None
    return out

print("=== PART A2: washout/arm entries, max drawdown 60 sessions forward ===")
episodes_A = [
    ('2020-03 washout arm (E7)', '2020-03-11'),
    ('2022-11 counterfactual arm', '2022-11-15'),
    ('2018-05 washout arm (E4, counter-example)', '2018-05-28'),
]
resA = [analyze_entry(l,d) for l,d in episodes_A]
for r in resA:
    print(r)

print()
print("=== MARGIN SURVIVAL (f=1.3, maintenance=0.40, liquidation=0.30) ===")
f = 1.3
maint = 0.40
liq = 0.30
def equity_ratio(d, f):
    # equity_ratio = [f*(1+d) - (f-1)] / [f*(1+d)]
    return (f*(1+d) - (f-1)) / (f*(1+d))

def dd_for_ratio(target_ratio, f):
    # solve f(1+d) - (f-1) = target*f*(1+d)
    # (1+d)*(f - target*f) = f-1
    # (1+d) = (f-1) / (f*(1-target))
    onepd = (f-1) / (f*(1-target_ratio))
    return onepd - 1

d_maint_f13 = dd_for_ratio(maint, 1.3)
d_liq_f13 = dd_for_ratio(liq, 1.3)
print(f"f=1.3: drawdown to breach maintenance(40%) = {d_maint_f13*100:.2f}% | to breach liquidation(30%) = {d_liq_f13*100:.2f}%")

d_maint_f20 = dd_for_ratio(maint, 2.0)
d_liq_f20 = dd_for_ratio(liq, 2.0)
print(f"f=2.0 (single-name policy reference, initial 50%): maintenance breach = {d_maint_f20*100:.2f}% | liquidation breach = {d_liq_f20*100:.2f}%")

print()
for r in resA:
    er = equity_ratio(r['max_drawdown_60d']/100, f)
    margin_call = er < maint
    liq_call = er < liq
    print(f"{r['label']}: max_dd={r['max_drawdown_60d']}% -> equity_ratio(f=1.3)={er*100:.1f}% | maintenance_breach={margin_call} | liquidation_breach={liq_call}")

print()
print("=== PART B1/B2: DT5G recovery-exit transitions + forward return/drawdown ===")
dt5g = pd.read_csv('/home/trido/thanhdt/WorkingClaude/data/vnindex_5state_dt5g_live.csv')
dt5g['time'] = pd.to_datetime(dt5g['time'])
STATE_MAP = {1:'CRISIS',2:'BEAR',3:'NEUTRAL',4:'BULL',5:'EX-BULL'}
dt5g['label'] = dt5g['state'].map(STATE_MAP)
dt5g = dt5g.sort_values('time').reset_index(drop=True)
dt5g['prev_label'] = dt5g['label'].shift(1)
transitions = dt5g[dt5g['label'] != dt5g['prev_label']].dropna(subset=['prev_label'])
print("Min date in DT5G table:", dt5g['time'].min().date())
print()
print("All CRISIS-> / BEAR->NEUTRAL transitions:")
for _,row in transitions.iterrows():
    if row['prev_label'] in ('CRISIS','BEAR') and row['label'] in ('BEAR','NEUTRAL'):
        print(f"  {row['prev_label']} -> {row['label']} on {row['time'].date()}")

recovery_entries = [
    ('2020 COVID: CRISIS->NEUTRAL', '2020-05-27'),
    ('2022-23 SCB: CRISIS->BEAR', '2022-12-14'),
    ('2022-23 SCB: BEAR->NEUTRAL (fuller confirm)', '2023-04-12'),
]
resB = [analyze_entry(l,d) for l,d in recovery_entries]
print()
for r in resB:
    print(r)
