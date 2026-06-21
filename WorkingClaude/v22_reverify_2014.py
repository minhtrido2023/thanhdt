"""
v22_reverify_2014.py — Independent re-verification of V2.2 (2014 -> now)
========================================================================
Rebuilds V2.2 from the actual paper-trade leg NAVs (no trust in cached numbers):
  V2.2 base   = BAL(25B) + LAG(25B)  independent sleeves
  V2.2 +capit = BAL_cap   + LAG_cap
Reports full-period + IS/OOS + annual vs VNINDEX, and checks against the
claimed champion numbers (base 24.08%, +capit 25.77% / DD-20.1 / Sh1.65).

Also tests the cross-book combination method:
  - sum (drift, no cross-rebal)   <- what the champion used
  - 50/50 daily rebalance
  - Band +-10pp (this session's recommendation)
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

def load_nav(f):
    d = pd.read_csv(f'data/{f}.csv', parse_dates=['time']).set_index('time')['nav']
    return d

bal   = load_nav('pt_v22_bal_v21')
lag   = load_nav('pt_v22_lag_v21')
balc  = load_nav('pt_v22_bal_v21_cap')
lagc  = load_nav('pt_v22_lag_v21_cap')

# VNINDEX benchmark (normalized) from the 5sys aligned file
vni = pd.read_csv('data/5sys_prodspec_201401_202605_dt5g_realetf.csv',
                  parse_dates=['time']).set_index('time')['VNI']

idx = bal.index.intersection(lag.index).intersection(vni.index)
bal, lag, balc, lagc, vni = [s.reindex(idx) for s in [bal, lag, balc, lagc, vni]]

# ── Combined NAVs ────────────────────────────────────────────────────
v22_sum   = bal + lag                       # independent sleeves (drift)
v22c_sum  = balc + lagc
# daily returns of each leg for rebalanced variants
rb, rl = bal.pct_change().fillna(0), lag.pct_change().fillna(0)
v22_5050 = (1 + 0.5*rb + 0.5*rl).cumprod() * (bal.iloc[0]+lag.iloc[0])

# Band +-10pp on the two momentum legs (50/50 target)
def band_combine(rb, rl, target=0.5, band=0.10, tc=0.003):
    w = target; navs = [1.0]; cur = 1.0
    for i in range(1, len(rb)):
        pr = w*rb.iloc[i] + (1-w)*rl.iloc[i]
        # drift
        wb = w*(1+rb.iloc[i]); wl = (1-w)*(1+rl.iloc[i])
        w_new = wb/(wb+wl)
        if abs(w_new - target) > band:
            pr -= abs(target - w_new) * tc
            w = target
        else:
            w = w_new
        cur *= (1+pr); navs.append(cur)
    return pd.Series(navs, index=rb.index) * (bal.iloc[0]+lag.iloc[0])

v22_band = band_combine(rb, rl)

YEARS = (idx[-1] - idx[0]).days / 365.25
print("="*70)
print(f"V2.2 RE-VERIFICATION  ({idx[0].date()} -> {idx[-1].date()}, {YEARS:.2f} yrs)")
print("="*70)

# Trading days per year for annualization (VN ~250)
def metrics(nav):
    r = nav.pct_change().dropna()
    n = len(r)
    tdy = n / YEARS
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/YEARS) - 1
    sd = r.std()*np.sqrt(tdy)
    mu = r.mean()*tdy
    dd = (nav/nav.cummax() - 1).min()
    sortino_dn = r[r<0].std()*np.sqrt(tdy)
    return dict(CAGR=cagr*100, Vol=sd*100, Sharpe=mu/sd if sd>0 else 0,
                Sortino=mu/sortino_dn if sortino_dn>0 else 0,
                MaxDD=dd*100, Calmar=cagr/abs(dd) if dd<0 else np.nan,
                final=nav.iloc[-1]/1e9)

print(f"\n  {'Strategy':28s}  {'Final':>8s}  {'CAGR':>6s}  {'Sharpe':>7s}  "
      f"{'Sortino':>7s}  {'MaxDD':>7s}  {'Calmar':>7s}")
print("  " + "-"*82)
rows = [
    ('BAL leg only (25B)',      bal),
    ('LAG leg only (25B)',      lag),
    ('V2.2 base = BAL+LAG sum', v22_sum),
    ('V2.2 base 50/50 rebal',   v22_5050),
    ('V2.2 base Band +-10pp',   v22_band),
    ('V2.2 +capit = sum',       v22c_sum),
    ('VNINDEX (B&H)',           vni),
]
M = {}
for name, nav in rows:
    m = metrics(nav); M[name] = m
    print(f"  {name:28s}  {m['final']:7.1f}B  {m['CAGR']:5.1f}%  {m['Sharpe']:7.2f}  "
          f"{m['Sortino']:7.2f}  {m['MaxDD']:6.1f}%  {m['Calmar']:6.2f}")

# ── Verification vs claimed numbers ──────────────────────────────────
print("\n  --- Check vs claimed champion numbers (from memory) ---")
claim = {'V2.2 base = BAL+LAG sum': (24.08, None, None),
         'V2.2 +capit = sum': (25.77, -20.1, 1.65)}
for k, (c_cagr, c_dd, c_sh) in claim.items():
    m = M[k]
    note = f"CAGR {m['CAGR']:.2f}% vs claimed {c_cagr}%  (diff {m['CAGR']-c_cagr:+.2f}pp)"
    if c_dd:  note += f" | MaxDD {m['MaxDD']:.1f} vs {c_dd}"
    if c_sh:  note += f" | Sharpe {m['Sharpe']:.2f} vs {c_sh}"
    ok = "OK" if abs(m['CAGR']-c_cagr) < 0.5 else "CHECK"
    print(f"  [{ok}] {k}: {note}")

# ── IS / OOS ─────────────────────────────────────────────────────────
print("\n  --- IS (2014-2019) / OOS (2020-now) ---")
def slice_nav(nav, lo, hi):
    s = nav[(nav.index>=lo)&(nav.index<=hi)]
    return s / s.iloc[0]
for name, nav in [('V2.2 base (sum)', v22_sum), ('V2.2 +capit (sum)', v22c_sum),
                  ('VNINDEX', vni)]:
    for lbl, lo, hi in [('IS', '2014-01-01','2019-12-31'), ('OOS','2020-01-01','2026-12-31')]:
        s = slice_nav(nav, lo, hi)
        yrs = (s.index[-1]-s.index[0]).days/365.25
        cagr = (s.iloc[-1])**(1/yrs)-1
        r = s.pct_change().dropna(); tdy=len(r)/yrs
        sh = r.mean()*tdy/(r.std()*np.sqrt(tdy))
        dd = (s/s.cummax()-1).min()
        print(f"    {name:20s} {lbl}: CAGR {cagr*100:5.1f}%  Sh {sh:.2f}  MaxDD {dd*100:5.1f}%")

# ── Annual breakdown ─────────────────────────────────────────────────
print("\n  --- Annual returns (%) ---")
print(f"  {'Year':6s}  {'BAL':>7s}  {'LAG':>7s}  {'V2.2base':>9s}  {'V2.2+cap':>9s}  {'VNINDEX':>8s}")
print("  " + "-"*58)
def yr_ret(nav, y):
    s = nav[nav.index.year==y]
    if len(s)<2: return np.nan
    return (s.iloc[-1]/s.iloc[0]-1)*100
for y in range(2014, 2027):
    parts = [yr_ret(x, y) for x in [bal, lag, v22_sum, v22c_sum, vni]]
    if np.isnan(parts[2]): continue
    mark = '*' if not np.isnan(parts[3]) and not np.isnan(parts[4]) and parts[3]>parts[4] else ' '
    print(f"  {y}   {parts[0]:+6.1f}%  {parts[1]:+6.1f}%  {parts[2]:+8.1f}%  "
          f"{parts[3]:+8.1f}%{mark}  {parts[4]:+7.1f}%")

# win rate vs VNI
wins = sum(1 for y in range(2014,2027)
           if not np.isnan(yr_ret(v22c_sum,y)) and not np.isnan(yr_ret(vni,y))
           and yr_ret(v22c_sum,y) > yr_ret(vni,y))
tot = sum(1 for y in range(2014,2027) if not np.isnan(yr_ret(v22c_sum,y)))
print(f"\n  V2.2+capit beats VNINDEX in {wins}/{tot} years")

# ── FIGURE ───────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 11))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('V2.2 Re-Verification from Paper-Trade Legs (2014 -> 2026-06)\n'
             'BAL + LAG independent sleeves | capit overlay | vs VNINDEX',
             fontsize=12, fontweight='bold', color='white', y=0.99)
dark='#161b22'; sp='#30363d'
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.40, wspace=0.34)
def sty(ax, t=""):
    ax.set_facecolor(dark); [s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e', labelsize=8)
    if t: ax.set_title(t, color='#e6edf3', fontsize=10, fontweight='bold', pad=7)

# R1 (span 2): NAV log
ax1 = fig.add_subplot(gs[0, :2]); sty(ax1, 'Cumulative NAV (log scale)')
for nav, lbl, col, lw in [
    (v22c_sum, f"V2.2+capit ({M['V2.2 +capit = sum']['CAGR']:.1f}%)", '#3fb950', 2.2),
    (v22_sum,  f"V2.2 base ({M['V2.2 base = BAL+LAG sum']['CAGR']:.1f}%)", '#58a6ff', 1.8),
    (lag,      f"LAG leg ({M['LAG leg only (25B)']['CAGR']:.1f}%)", '#9467bd', 1.0),
    (bal,      f"BAL leg ({M['BAL leg only (25B)']['CAGR']:.1f}%)", '#e8c547', 1.0),
    (vni*((bal.iloc[0]+lag.iloc[0])/vni.iloc[0]), f"VNINDEX ({M['VNINDEX (B&H)']['CAGR']:.1f}%)", '#d62728', 1.4),
]:
    ax1.semilogy(nav.index, nav.values/1e9, color=col, lw=lw, label=lbl)
ax1.legend(fontsize=9, facecolor='#1c2128', labelcolor='white', loc='upper left')
ax1.set_ylabel('NAV (B VND, log)', color='#8b949e')

# R1C2: drawdown
ax2 = fig.add_subplot(gs[0, 2]); sty(ax2, 'Drawdown')
for nav, lbl, col in [(v22c_sum,'V2.2+capit','#3fb950'),
                      (vni,'VNINDEX','#d62728')]:
    dd = (nav/nav.cummax()-1)*100
    ax2.fill_between(dd.index, dd.values, 0, color=col, alpha=0.4, label=lbl)
ax2.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')
ax2.set_ylabel('DD %', color='#8b949e')

# R2C0: annual bars
ax3 = fig.add_subplot(gs[1, 0]); sty(ax3, 'Annual Return: V2.2+capit vs VNINDEX')
yrs_l = [y for y in range(2014,2027) if not np.isnan(yr_ret(v22c_sum,y))]
v_l = [yr_ret(v22c_sum,y) for y in yrs_l]; n_l=[yr_ret(vni,y) for y in yrs_l]
x = np.arange(len(yrs_l)); w=0.4
ax3.bar(x-w/2, v_l, w, color='#3fb950', alpha=0.85, label='V2.2+capit')
ax3.bar(x+w/2, n_l, w, color='#d62728', alpha=0.7, label='VNINDEX')
ax3.axhline(0, color='white', lw=0.8, alpha=0.5)
ax3.set_xticks(x); ax3.set_xticklabels([str(y)[-2:] for y in yrs_l], color='#8b949e', fontsize=8)
ax3.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')

# R2C1: combination method comparison
ax4 = fig.add_subplot(gs[1, 1]); sty(ax4, 'Cross-Leg Combination Method (base)')
combos = [('sum/drift', v22_sum), ('50/50 rebal', v22_5050), ('Band +-10pp', v22_band)]
cb_cagr = [metrics(n)['CAGR'] for _,n in combos]
cb_sh   = [metrics(n)['Sharpe'] for _,n in combos]
x=np.arange(len(combos)); w=0.38
ax4b = ax4.twinx()
ax4.bar(x-w/2, cb_cagr, w, color='#58a6ff', alpha=0.85, label='CAGR%')
ax4b.bar(x+w/2, cb_sh, w, color='#3fb950', alpha=0.85, label='Sharpe')
ax4.set_xticks(x); ax4.set_xticklabels([c for c,_ in combos], color='#8b949e', fontsize=8)
ax4.set_ylabel('CAGR %', color='#58a6ff'); ax4b.set_ylabel('Sharpe', color='#3fb950')
ax4b.tick_params(colors='#3fb950')
for i,v in enumerate(cb_cagr): ax4.text(i-w/2, v+0.2, f'{v:.1f}', ha='center', color='white', fontsize=7)
for i,v in enumerate(cb_sh): ax4b.text(i+w/2, v+0.01, f'{v:.2f}', ha='center', color='white', fontsize=7)

# R2C2: metrics table
ax5 = fig.add_subplot(gs[1, 2]); ax5.set_facecolor(dark); ax5.axis('off')
sty(ax5, 'Full-Period Metrics (2014 -> now)')
tbl_rows = [['Strategy','CAGR','Sharpe','MaxDD','Cal']]
for name in ['V2.2 base = BAL+LAG sum','V2.2 +capit = sum','VNINDEX (B&H)']:
    m=M[name]
    tbl_rows.append([name.replace(' = BAL+LAG sum','').replace(' = sum','').replace(' (B&H)',''),
                     f"{m['CAGR']:.1f}%", f"{m['Sharpe']:.2f}",
                     f"{m['MaxDD']:.1f}%", f"{m['Calmar']:.2f}"])
t = ax5.table(cellText=tbl_rows[1:], colLabels=tbl_rows[0], loc='center', cellLoc='center')
t.auto_set_font_size(False); t.set_fontsize(9); t.scale(1.1, 2.4)
for (ri,ci),cell in t.get_celld().items():
    cell.set_facecolor('#1c2128' if ri%2==0 else dark)
    cell.set_text_props(color='#e6edf3'); cell.set_edgecolor(sp)
    if ri==0: cell.set_facecolor('#21262d'); cell.set_text_props(color='white', fontweight='bold')
    if ri==2: cell.set_facecolor('#0d2e14')

out = WORKDIR + r"\v22_reverify_2014.png"
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: v22_reverify_2014.png")
plt.close()
print("DONE")
