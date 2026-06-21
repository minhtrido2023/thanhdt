"""
book_rebal_policy.py — When to rebalance CAPITAL across the 3 independent books?
=================================================================================
This is the THIRD rebalance cadence (distinct from the two already settled):
  1. within-book holdings rotation  -> monthly (Book C: day-10)   [SETTLED]
  2. per-book exposure via DT5G      -> on state change            [SETTLED]
  3. cross-book capital weight reset -> THIS SCRIPT                [QUESTION]

Target weights: BAL 35% / LAG 35% / VALUE 30%  (17.5 / 17.5 / 15 of 50B).
Each book's GATED monthly return is taken as-is (DT5G already applied inside each).
We test how/when to reset the 35/35/30 split as the books drift apart.

Policies tested:
  - never        : let weights drift (winners compound their share)
  - monthly / quarterly / semiannual / annual : calendar resets
  - band_5 / band_10 : reset only when a book drifts > X pp from target

TC = 0.30% charged on the turnover (|w_after - w_before|) at each reset.
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
TARGET = np.array([0.35, 0.35, 0.30])   # BAL, LAG, VALUE
NAMES  = ['BAL', 'LAG', 'VALUE']

# ── Load the three GATED monthly return streams ──────────────────────
def monthly_ret_from_nav(path):
    df = pd.read_csv(path, parse_dates=['time']).set_index('time')['nav']
    m = df.resample('ME').last().pct_change()
    m.index = m.index.to_period('M')
    return m

bal = monthly_ret_from_nav('data/pt_v22_bal_v21.csv')
lag = monthly_ret_from_nav('data/pt_v22_lag_v21.csv')

vc = pd.read_csv('data/book_c_backtest.csv')
vc['time'] = pd.PeriodIndex(vc['time'], freq='M')
val = vc.set_index('time')['ret_gated_eq']

R = pd.concat([bal.rename('BAL'), lag.rename('LAG'), val.rename('VALUE')], axis=1).dropna()
print("="*68)
print("CROSS-BOOK REBALANCE POLICY TEST")
print("="*68)
print(f"\n  Common period: {R.index.min()} -> {R.index.max()}  ({len(R)} months)")

# ── Correlation structure (WHY rebalancing may pay) ──────────────────
print("\n  Pairwise monthly-return correlation:")
corr = R.corr()
print(corr.round(2).to_string())
print(f"\n  -> BAL/LAG (both momentum) corr = {corr.loc['BAL','LAG']:.2f}")
print(f"  -> VALUE vs momentum avg corr  = {((corr.loc['VALUE','BAL']+corr.loc['VALUE','LAG'])/2):.2f}")
print("  Rebalancing bonus comes mainly from the VALUE-vs-momentum axis.")

# ── Standalone book stats ────────────────────────────────────────────
def metrics(r):
    r = r.dropna(); n = len(r)
    if n < 6: return dict(CAGR=np.nan, Vol=np.nan, Sharpe=np.nan, MaxDD=np.nan, Calmar=np.nan)
    mu = r.mean()*12; sd = r.std(ddof=1)*np.sqrt(12)
    cagr = (1+r).prod()**(12/n)-1
    nav = (1+r).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Vol=sd*100, Sharpe=mu/sd if sd>0 else 0,
                MaxDD=dd*100, Calmar=cagr/abs(dd) if dd<0 else np.nan)

print("\n  Standalone book metrics (gated):")
print(f"  {'Book':8s}  {'CAGR':>6s}  {'Vol':>6s}  {'Sharpe':>7s}  {'MaxDD':>7s}")
for nm in NAMES:
    m = metrics(R[nm])
    print(f"  {nm:8s}  {m['CAGR']:5.1f}%  {m['Vol']:5.1f}%  {m['Sharpe']:7.2f}  {m['MaxDD']:6.1f}%")

# ── Simulate a rebalance policy ──────────────────────────────────────
def simulate(R, policy, target=TARGET, tc=TC):
    """Returns (monthly_portfolio_return_series, total_turnover, n_rebals)."""
    months = R.index
    w = target.copy()                      # current weights (start at target)
    port_ret = []
    total_turn = 0.0
    n_rebal = 0
    months_since = 0
    for i, m in enumerate(months):
        r = R.loc[m].values                # this month's book returns
        # portfolio return BEFORE any reset = w . r
        pr = float(np.dot(w, r))
        # let weights drift with realized returns
        w_drift = w * (1 + r)
        w_drift = w_drift / w_drift.sum()
        months_since += 1
        # decide whether to rebalance at month END
        do = False
        if policy == 'never':
            do = False
        elif policy == 'monthly':
            do = True
        elif policy == 'quarterly':
            do = (months_since >= 3)
        elif policy == 'semiannual':
            do = (months_since >= 6)
        elif policy == 'annual':
            do = (months_since >= 12)
        elif policy.startswith('band_'):
            band = int(policy.split('_')[1]) / 100.0
            do = np.any(np.abs(w_drift - target) > band)
        if do:
            turn = np.abs(target - w_drift).sum() / 2   # one-way turnover
            cost = turn * tc
            pr -= cost                       # charge TC in the month of reset
            total_turn += turn
            n_rebal += 1
            w = target.copy()
            months_since = 0
        else:
            w = w_drift
        port_ret.append(pr)
    return pd.Series(port_ret, index=months), total_turn, n_rebal

POLICIES = ['never', 'monthly', 'quarterly', 'semiannual', 'annual', 'band_5', 'band_10']
PLABEL = {'never':'Never (drift)', 'monthly':'Monthly', 'quarterly':'Quarterly',
          'semiannual':'Semi-annual', 'annual':'Annual',
          'band_5':'Band ±5pp', 'band_10':'Band ±10pp'}

results = {}
print("\n" + "="*68)
print("REBALANCE POLICY COMPARISON (TC 0.30% on turnover)")
print("="*68)
print(f"\n  {'Policy':16s}  {'CAGR':>6s}  {'Vol':>6s}  {'Sharpe':>7s}  {'MaxDD':>7s}  "
      f"{'Calmar':>7s}  {'#reb':>5s}  {'turn/yr':>8s}")
print("  " + "-"*78)
yrs = len(R)/12
for p in POLICIES:
    pr, turn, nreb = simulate(R, p)
    m = metrics(pr)
    results[p] = dict(ret=pr, turn=turn, nreb=nreb, **m)
    print(f"  {PLABEL[p]:16s}  {m['CAGR']:5.1f}%  {m['Vol']:5.1f}%  {m['Sharpe']:7.2f}  "
          f"{m['MaxDD']:6.1f}%  {m['Calmar']:6.2f}  {nreb:5d}  {turn/yrs*100:7.1f}%")

# ── Rebalancing bonus vs drift ───────────────────────────────────────
base = results['never']
print("\n  Delta vs Never (drift):")
for p in POLICIES:
    if p == 'never': continue
    d_cagr = results[p]['CAGR'] - base['CAGR']
    d_shar = results[p]['Sharpe'] - base['Sharpe']
    d_dd   = results[p]['MaxDD'] - base['MaxDD']
    print(f"    {PLABEL[p]:16s}  CAGR {d_cagr:+.2f}pp  Sharpe {d_shar:+.3f}  MaxDD {d_dd:+.1f}pp")

# ── IS / OOS split robustness ────────────────────────────────────────
print("\n  IS (2016-2019) / OOS (2020-2026) Sharpe:")
def sub(s, lo, hi): return s[(s.index>=pd.Period(lo))&(s.index<=pd.Period(hi))]
print(f"  {'Policy':16s}  {'IS Sh':>6s}  {'OOS Sh':>7s}  {'IS Cal':>7s}  {'OOS Cal':>8s}")
for p in POLICIES:
    ri = sub(results[p]['ret'], '2016-01', '2019-12')
    ro = sub(results[p]['ret'], '2020-01', '2026-12')
    mi, mo = metrics(ri), metrics(ro)
    print(f"  {PLABEL[p]:16s}  {mi['Sharpe']:6.2f}  {mo['Sharpe']:7.2f}  "
          f"{mi['Calmar']:7.2f}  {mo['Calmar']:8.2f}")

# ── Weight-drift magnitude under 'never' ─────────────────────────────
print("\n  How far do weights drift WITHOUT rebalancing?")
w = TARGET.copy(); maxdev = np.zeros(3); wpath = []
for m in R.index:
    r = R.loc[m].values
    w = w*(1+r); w = w/w.sum()
    wpath.append(w.copy())
    maxdev = np.maximum(maxdev, np.abs(w - TARGET))
wpath = np.array(wpath)
for i, nm in enumerate(NAMES):
    print(f"    {nm:8s}: end weight {w[i]*100:4.1f}% (target {TARGET[i]*100:.0f}%), "
          f"max drift {maxdev[i]*100:+.1f}pp")

# ── FIGURE ───────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 11))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('Cross-Book Rebalance Policy — BAL 35 / LAG 35 / VALUE 30\n'
             'When to reset the capital split (gated monthly returns, 2016-2026, TC 0.30%)',
             fontsize=12, fontweight='bold', color='white', y=0.99)
dark='#161b22'; sp='#30363d'
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.34)
def sty(ax, t=""):
    ax.set_facecolor(dark); [s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e', labelsize=8)
    if t: ax.set_title(t, color='#e6edf3', fontsize=10, fontweight='bold', pad=7)

# R1C0: Sharpe by policy
ax1 = fig.add_subplot(gs[0,0]); sty(ax1, 'Sharpe by Rebalance Policy')
shs = [results[p]['Sharpe'] for p in POLICIES]
bi = int(np.argmax(shs))
cols = ['#3fb950' if i==bi else '#58a6ff' for i in range(len(shs))]
ax1.bar(range(len(POLICIES)), shs, color=cols, alpha=0.85)
for i,v in enumerate(shs): ax1.text(i, v+0.005, f'{v:.2f}', ha='center', color='white', fontsize=8)
ax1.set_xticks(range(len(POLICIES)))
ax1.set_xticklabels([PLABEL[p] for p in POLICIES], rotation=35, ha='right', fontsize=7)
ax1.set_ylim(min(shs)*0.95, max(shs)*1.03)

# R1C1: MaxDD by policy
ax2 = fig.add_subplot(gs[0,1]); sty(ax2, 'MaxDD by Rebalance Policy')
dds = [results[p]['MaxDD'] for p in POLICIES]
bi2 = int(np.argmax(dds))  # least negative
cols2 = ['#3fb950' if i==bi2 else '#e8c547' for i in range(len(dds))]
ax2.bar(range(len(POLICIES)), dds, color=cols2, alpha=0.85)
for i,v in enumerate(dds): ax2.text(i, v-0.5, f'{v:.0f}', ha='center', color='white', fontsize=8)
ax2.set_xticks(range(len(POLICIES)))
ax2.set_xticklabels([PLABEL[p] for p in POLICIES], rotation=35, ha='right', fontsize=7)

# R1C2: NAV curves
ax3 = fig.add_subplot(gs[0,2]); sty(ax3, 'Cumulative NAV: key policies')
for p, col in [('never','#d62728'),('annual','#e8c547'),
               ('quarterly','#58a6ff'),('band_10','#3fb950')]:
    nav = (1+results[p]['ret']).cumprod()
    ax3.semilogy(nav.index.to_timestamp(), nav.values, color=col, lw=1.6,
                 label=f"{PLABEL[p]} (Sh {results[p]['Sharpe']:.2f})")
ax3.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')

# R2C0: correlation heatmap
ax4 = fig.add_subplot(gs[1,0]); sty(ax4, 'Book Return Correlation')
im = ax4.imshow(corr.values, cmap='RdYlGn_r', vmin=-1, vmax=1)
ax4.set_xticks(range(3)); ax4.set_xticklabels(NAMES, color='#8b949e')
ax4.set_yticks(range(3)); ax4.set_yticklabels(NAMES, color='#8b949e')
for i in range(3):
    for j in range(3):
        ax4.text(j,i,f'{corr.values[i,j]:.2f}', ha='center', va='center',
                 color='black', fontsize=11, fontweight='bold')
plt.colorbar(im, ax=ax4, shrink=0.7)

# R2C1: weight drift path under never
ax5 = fig.add_subplot(gs[1,1]); sty(ax5, 'Weight Drift WITHOUT Rebalancing')
ts = R.index.to_timestamp()
for i, (nm, col) in enumerate(zip(NAMES, ['#58a6ff','#9467bd','#e8c547'])):
    ax5.plot(ts, wpath[:,i]*100, color=col, lw=1.5, label=nm)
    ax5.axhline(TARGET[i]*100, color=col, lw=0.8, ls='--', alpha=0.5)
ax5.set_ylabel('weight %', color='#8b949e')
ax5.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')

# R2C2: delta CAGR/Sharpe vs never
ax6 = fig.add_subplot(gs[1,2]); sty(ax6, 'Bonus vs Never (drift)')
pol2 = [p for p in POLICIES if p!='never']
dc = [results[p]['CAGR']-base['CAGR'] for p in pol2]
ds = [(results[p]['Sharpe']-base['Sharpe'])*10 for p in pol2]  # scaled x10 for visibility
x = np.arange(len(pol2)); w_=0.38
ax6.bar(x-w_/2, dc, w_, color='#58a6ff', alpha=0.85, label='ΔCAGR pp')
ax6.bar(x+w_/2, ds, w_, color='#3fb950', alpha=0.85, label='ΔSharpe ×10')
ax6.axhline(0, color='white', lw=0.8, alpha=0.5)
ax6.set_xticks(x); ax6.set_xticklabels([PLABEL[p] for p in pol2], rotation=35, ha='right', fontsize=7)
ax6.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')

out = WORKDIR + r"\book_rebal_policy.png"
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: book_rebal_policy.png")
plt.close()
print("DONE")
