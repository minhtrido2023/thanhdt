import csv
from datetime import date

rows = list(csv.DictReader(open('breadth_daily_5episodes.csv')))
for r in rows:
    r['dt'] = date.fromisoformat(r['dt'])
    r['pct_oversold'] = float(r['pct_oversold'])
    r['n_universe'] = int(r['n_universe'])
rows.sort(key=lambda r: r['dt'])

def slice_range(d0, d1):
    return [r for r in rows if d0 <= r['dt'] <= d1]

episodes = {
    'EP-2014-09': dict(peak=date(2014,9,3), trough=date(2014,12,17), baseline=(date(2014,7,1), date(2014,8,29))),
    'EP-2015-07': dict(peak=date(2015,7,14), trough=date(2015,8,24), baseline=(date(2015,5,1), date(2015,7,10))),
    'EP-2023-09': dict(peak=date(2023,9,6), trough=date(2023,10,31), baseline=(date(2023,7,1), date(2023,9,1))),
    'EP-2025-03': dict(peak=date(2025,3,17), trough=date(2025,4,9), baseline=(date(2025,1,1), date(2025,3,10))),
    'EP-2026-01': dict(peak=date(2026,1,13), trough=date(2026,3,23), baseline=(date(2025,11,1), date(2026,1,8))),
}

print(f"{'episode':12s} {'baseline%':>10s} {'peak_breadth%':>14s} {'peak_dt':>12s} {'vs_price_trough':>18s} {'heal_days':>10s} {'heal_dt':>12s}")
for name, ep in episodes.items():
    bl_rows = slice_range(*ep['baseline'])
    baseline = sum(r['pct_oversold'] for r in bl_rows)/len(bl_rows) if bl_rows else float('nan')
    # window for episode peak search: from episode start-5d to trough+10d
    win = slice_range(ep['peak'], ep['trough'])
    if not win:
        print(name, "NO DATA IN WINDOW"); continue
    peak_row = max(win, key=lambda r: r['pct_oversold'])
    lag_days = (peak_row['dt'] - ep['trough']).days
    # healing: after peak_row date, find first date where pct_oversold <= baseline
    after = [r for r in rows if r['dt'] > peak_row['dt']]
    heal_row = None
    for r in after:
        if r['pct_oversold'] <= baseline:
            heal_row = r
            break
    if heal_row:
        heal_sessions = sum(1 for r in rows if peak_row['dt'] < r['dt'] <= heal_row['dt'])
        heal_dt = heal_row['dt'].isoformat()
    else:
        heal_sessions = None
        heal_dt = 'NOT HEALED in data range'
    vs_trough = f"{lag_days:+d}d(price trough)"
    print(f"{name:12s} {baseline:9.2f}% {peak_row['pct_oversold']:13.2f}% {peak_row['dt'].isoformat():>12s} {vs_trough:>18s} {str(heal_sessions):>10s} {heal_dt:>12s}")
