"""
v22c_compare.py — Does adding Book C help V2.2? (historical, 2016 -> now)
=========================================================================
The earlier v22_reverify_2014.py was MOMENTUM-ONLY (BAL+LAG+capit). It did NOT
include Book C. This script adds the 3rd book and compares apples-to-apples over
the common period (Book C history starts 2016-01).

  V2.2 momentum (2-book)  = BAL_cap + LAG_cap        (the live champion)
  V2.2 + C   (3-book)     = 35% BAL + 35% LAG + 30% VALUE, Band +-10pp rebal

All legs are GATED (DT5G already inside). Monthly frequency (Book C is monthly).
"""
import sys, os
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings; warnings.filterwarnings('ignore')

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
TC = 0.003

def monthly_ret(path):
    nav = pd.read_csv(f'data/{path}.csv', parse_dates=['time']).set_index('time')['nav']
    m = nav.resample('ME').last().pct_change()
    m.index = m.index.to_period('M'); return m

# momentum legs WITH capit (the champion uses +capit)
bal = monthly_ret('pt_v22_bal_v21_cap')
lag = monthly_ret('pt_v22_lag_v21_cap')

# Book C (gated value), monthly
vc = pd.read_csv('data/book_c_backtest.csv')
vc['time'] = pd.PeriodIndex(vc['time'], freq='M')
val = vc.set_index('time')['ret_gated_eq']

R = pd.concat([bal.rename('BAL'), lag.rename('LAG'), val.rename('VALUE')], axis=1).dropna()
print("="*72)
print(f"V2.2  vs  V2.2+C   (common period {R.index.min()} -> {R.index.max()}, {len(R)} months)")
print("="*72)

def metrics(r):
    r = r.dropna(); n = len(r)
    mu = r.mean()*12; sd = r.std(ddof=1)*np.sqrt(12)
    cagr = (1+r).prod()**(12/n)-1
    nav = (1+r).cumprod(); dd = (nav/nav.cummax()-1).min()
    dn = r[r<0].std()*np.sqrt(12)
    return dict(CAGR=cagr*100, Vol=sd*100, Sharpe=mu/sd if sd>0 else 0,
                Sortino=mu/dn if dn>0 else 0, MaxDD=dd*100,
                Calmar=cagr/abs(dd) if dd<0 else np.nan)

# --- V2.2 momentum (2-book): sum/drift = the live champion method ---
# combined NAV = bal_nav + lag_nav (each starts equal); use monthly returns of the sum
bal_nav = (1+bal).cumprod(); lag_nav = (1+lag).cumprod()
v22_nav = (bal_nav + lag_nav)             # 50/50 start, drift
v22_mom = v22_nav.pct_change().reindex(R.index)

# --- Band +-10pp combiner ---
def band_combine(R3, target, band=0.10, tc=TC):
    w = np.array(target, float); out = []
    for i, m in enumerate(R3.index):
        r = R3.loc[m].values
        pr = float(np.dot(w, r))
        wd = w*(1+r); wd = wd/wd.sum()
        if i > 0 and np.any(np.abs(wd-target) > band):
            pr -= np.abs(target-wd).sum()/2*tc; w = np.array(target, float)
        else:
            w = wd
        out.append(pr)
    return pd.Series(out, index=R3.index)

# 2-book Band (for method-matched comparison)
v22_band = band_combine(R[['BAL','LAG']], [0.5,0.5])
# 3-book = +Book C
v22c = band_combine(R[['BAL','LAG','VALUE']], [0.35,0.35,0.30])

rows = [
    ('V2.2 momentum (sum/drift)', v22_mom),
    ('V2.2 momentum (50/50 Band)', v22_band),
    ('V2.2 + C  (35/35/30 Band)',  v22c),
    ('  -- Book C standalone',      R['VALUE']),
]
print(f"\n  {'Strategy':30s}  {'CAGR':>6s}  {'Vol':>6s}  {'Sharpe':>7s}  "
      f"{'Sortino':>7s}  {'MaxDD':>7s}  {'Calmar':>7s}")
print("  " + "-"*82)
M = {}
for nm, r in rows:
    m = metrics(r); M[nm] = m
    print(f"  {nm:30s}  {m['CAGR']:5.1f}%  {m['Vol']:5.1f}%  {m['Sharpe']:7.2f}  "
          f"{m['Sortino']:7.2f}  {m['MaxDD']:6.1f}%  {m['Calmar']:6.2f}")

# --- effect of adding C (method-matched: Band 2-book vs Band 3-book) ---
a, b = M['V2.2 momentum (50/50 Band)'], M['V2.2 + C  (35/35/30 Band)']
print(f"\n  EFFECT OF ADDING BOOK C (Band-vs-Band, apples-to-apples):")
print(f"    CAGR   {a['CAGR']:.1f}% -> {b['CAGR']:.1f}%   ({b['CAGR']-a['CAGR']:+.2f}pp)")
print(f"    Sharpe {a['Sharpe']:.2f}  -> {b['Sharpe']:.2f}    ({b['Sharpe']-a['Sharpe']:+.3f})")
print(f"    MaxDD  {a['MaxDD']:.1f}% -> {b['MaxDD']:.1f}%   ({b['MaxDD']-a['MaxDD']:+.1f}pp)")
print(f"    Calmar {a['Calmar']:.2f}  -> {b['Calmar']:.2f}    ({b['Calmar']-a['Calmar']:+.2f})")

# --- IS/OOS ---
def sub(s, lo, hi): return s[(s.index>=pd.Period(lo))&(s.index<=pd.Period(hi))]
print(f"\n  IS (2016-2019) / OOS (2020-now):")
for nm, r in [('V2.2 mom (Band)', v22_band), ('V2.2 + C (Band)', v22c)]:
    mi = metrics(sub(r,'2016-01','2019-12')); mo = metrics(sub(r,'2020-01','2026-12'))
    print(f"    {nm:18s}  IS {mi['CAGR']:5.1f}%/Sh{mi['Sharpe']:.2f}  "
          f"OOS {mo['CAGR']:5.1f}%/Sh{mo['Sharpe']:.2f}/DD{mo['MaxDD']:.0f}")

# --- annual + spotlight grind ---
print(f"\n  Annual returns:")
print(f"  {'Year':6s}  {'V2.2 mom':>9s}  {'V2.2+C':>8s}  {'diff':>7s}")
print("  " + "-"*40)
for y in range(2016, 2027):
    rm = sub(v22_band, f'{y}-01', f'{y}-12'); rc = sub(v22c, f'{y}-01', f'{y}-12')
    if len(rm) < 3: continue
    cm = ((1+rm).prod()-1)*100; cc = ((1+rc).prod()-1)*100
    mk = '  <- grind' if y == 2026 else ''
    print(f"  {y}   {cm:+8.1f}%  {cc:+7.1f}%  {cc-cm:+6.1f}%{mk}")

# 2026 YTD detail (the momentum weakness)
g_m = sub(v22_band, '2025-09', '2026-03'); g_c = sub(v22c, '2025-09', '2026-03')
print(f"\n  Grind 2025-09..2026-03:  V2.2 mom {((1+g_m).prod()-1)*100:+.1f}%  "
      f"vs  V2.2+C {((1+g_c).prod()-1)*100:+.1f}%")

# --- FIGURE ---
fig = plt.figure(figsize=(18, 9)); fig.patch.set_facecolor('#0d1117')
fig.suptitle('Does Book C help V2.2? — Historical 2016->now (gated, +capit momentum)\n'
             'V2.2 momentum (BAL+LAG)  vs  V2.2+C (35/35/30 Band +-10pp)',
             fontsize=12, color='white', fontweight='bold', y=0.99)
dark='#161b22'; sp='#30363d'
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.40, wspace=0.34)
def sty(ax, t=""):
    ax.set_facecolor(dark); [s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e', labelsize=8)
    if t: ax.set_title(t, color='#e6edf3', fontsize=10, fontweight='bold', pad=6)

ax1 = fig.add_subplot(gs[0, :2]); sty(ax1, 'Cumulative NAV')
for r, lbl, col in [(v22_band,'V2.2 momentum','#58a6ff'),
                    (v22c,'V2.2 + C','#3fb950'),
                    (R['VALUE'],'Book C alone','#e8c547')]:
    nav=(1+r.dropna()).cumprod(); ax1.semilogy(nav.index.to_timestamp(), nav.values,
        color=col, lw=1.9 if 'C' in lbl and 'alone' not in lbl else 1.3, label=lbl)
ax1.legend(fontsize=9, facecolor='#1c2128', labelcolor='white'); ax1.set_ylabel('NAV (log)', color='#8b949e')

ax2 = fig.add_subplot(gs[0, 2]); sty(ax2, 'Drawdown')
for r, lbl, col in [(v22_band,'V2.2 mom','#58a6ff'),(v22c,'V2.2+C','#3fb950')]:
    nav=(1+r.dropna()).cumprod(); dd=(nav/nav.cummax()-1)*100
    ax2.fill_between(dd.index.to_timestamp(), dd.values, 0, color=col, alpha=0.45, label=lbl)
ax2.legend(fontsize=8, facecolor='#1c2128', labelcolor='white'); ax2.set_ylabel('DD %', color='#8b949e')

ax3 = fig.add_subplot(gs[1, 0]); sty(ax3, 'Risk-Adjusted (Sharpe / Calmar)')
labs=['V2.2 mom','V2.2+C']; shs=[a['Sharpe'],b['Sharpe']]; cals=[a['Calmar'],b['Calmar']]
x=np.arange(2); w=0.35
ax3.bar(x-w/2, shs, w, color='#58a6ff', alpha=0.85, label='Sharpe')
ax3.bar(x+w/2, cals, w, color='#3fb950', alpha=0.85, label='Calmar')
for i,v in enumerate(shs): ax3.text(i-w/2, v+0.01, f'{v:.2f}', ha='center', color='white', fontsize=8)
for i,v in enumerate(cals): ax3.text(i+w/2, v+0.01, f'{v:.2f}', ha='center', color='white', fontsize=8)
ax3.set_xticks(x); ax3.set_xticklabels(labs, color='#8b949e'); ax3.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')

ax4 = fig.add_subplot(gs[1, 1]); sty(ax4, 'Annual: V2.2+C minus V2.2 momentum')
yrs=[]; diffs=[]
for y in range(2016,2027):
    rm=sub(v22_band,f'{y}-01',f'{y}-12'); rc=sub(v22c,f'{y}-01',f'{y}-12')
    if len(rm)<3: continue
    yrs.append(y); diffs.append(((1+rc).prod()-1)*100-((1+rm).prod()-1)*100)
cols=['#3fb950' if d>0 else '#d62728' for d in diffs]
ax4.bar(range(len(yrs)), diffs, color=cols, alpha=0.85)
ax4.axhline(0, color='white', lw=0.8, alpha=0.5)
ax4.set_xticks(range(len(yrs))); ax4.set_xticklabels([str(y)[-2:] for y in yrs], color='#8b949e', fontsize=8)
ax4.set_ylabel('diff pp', color='#8b949e')

ax5 = fig.add_subplot(gs[1, 2]); ax5.set_facecolor(dark); ax5.axis('off'); sty(ax5, 'Summary')
tr=[['','CAGR','Sharpe','MaxDD','Cal']]
for nm,key in [('V2.2 mom','V2.2 momentum (50/50 Band)'),('V2.2+C','V2.2 + C  (35/35/30 Band)')]:
    m=M[key]; tr.append([nm,f"{m['CAGR']:.1f}%",f"{m['Sharpe']:.2f}",f"{m['MaxDD']:.1f}%",f"{m['Calmar']:.2f}"])
t=ax5.table(cellText=tr[1:],colLabels=tr[0],loc='center',cellLoc='center')
t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1.1,2.6)
for (ri,ci),c in t.get_celld().items():
    c.set_facecolor('#1c2128' if ri%2==0 else dark); c.set_text_props(color='#e6edf3'); c.set_edgecolor(sp)
    if ri==0: c.set_facecolor('#21262d'); c.set_text_props(color='white', fontweight='bold')
    if ri==2: c.set_facecolor('#0d2e14')

fig.savefig(WORKDIR+r"\v22c_compare.png", dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: v22c_compare.png")
plt.close(); print("DONE")
