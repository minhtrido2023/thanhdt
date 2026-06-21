#!/usr/bin/env python3
"""
euphoria_short_analysis.py
Phân tích: SHORT VN30F 20% khi EX-BULL (đối xứng với capitulation buy)

3 phần:
  1. EX-BULL Event Study — fwd10/20/40/60 VNINDEX returns distribution
  2. Breadth Overbought — % stocks above MA200 during EX-BULL vs other states
  3. Symmetric Overlay Backtest — SHORT VN30F 20% khi EX-BULL
"""

import subprocess
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from io import StringIO
import os, sys, warnings
warnings.filterwarnings('ignore')

WORKDIR  = r"/home/trido/thanhdt/WorkingClaude"
PROJECT  = "lithe-record-440915-m9"
os.chdir(WORKDIR)

STATE_NAMES  = {1: 'CRISIS', 2: 'BEAR', 3: 'NEUTRAL', 4: 'BULL', 5: 'EX-BULL'}
STATE_ALLOC  = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_COLORS = {1: '#d62728', 2: '#ff7f0e', 3: '#7fafcf', 4: '#2ca02c', 5: '#9467bd'}

BQ_PATH = r"bq"

def bq(sql, label=""):
    if label: print(f"  > {label}...", end=" ", flush=True)
    cmd = f'"{BQ_PATH}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --quiet --max_rows=100000'
    r = subprocess.run(
        cmd, input=sql, capture_output=True, text=True, encoding='utf-8', shell=True
    )
    if r.returncode != 0:
        print(f"\n  ERROR: {r.stderr[:300]}")
        return pd.DataFrame()
    df = pd.read_csv(StringIO(r.stdout))
    if label: print(f"OK ({len(df):,} rows)")
    return df

print("\n" + "="*65)
print("EUPHORIA SHORT ANALYSIS — 3 PARTS")
print("="*65)

# ════════════════════════════════════════════════════════════════
# LOAD DATA
# ════════════════════════════════════════════════════════════════

# 1. DT5G states
dt5g_raw = bq("""
    SELECT s.time, s.state
    FROM tav2_bq.vnindex_5state_dt5g_live AS s
    ORDER BY s.time
""", "DT5G states")
dt5g_raw['time'] = pd.to_datetime(dt5g_raw['time'])
dt5g = dt5g_raw.set_index('time')['state'].astype(int)

# 2. VNINDEX from CSV
vni = pd.read_csv(os.path.join(WORKDIR, "data/VNINDEX.csv"))
vni['time'] = pd.to_datetime(vni['time'])
vni = vni.set_index('time').sort_index()
vni_close = vni['Close'].astype(float)
vni_ret = vni_close.pct_change()

# 3. VN30F front month close
vn30f_raw = bq("""
    SELECT v.time, v.f1m_close
    FROM tav2_bq.vn30f_daily AS v
    WHERE v.time >= '2017-01-01'
    ORDER BY v.time
""", "VN30F f1m_close")
vn30f_raw['time'] = pd.to_datetime(vn30f_raw['time'])
vn30f = vn30f_raw.set_index('time')['f1m_close'].astype(float)
vn30f_ret = vn30f.pct_change()
print(f"    VN30F: {vn30f.index[0].date()} → {vn30f.index[-1].date()}")

# 4. Breadth from ticker_prune
breadth_raw = bq("""
    SELECT t.time,
        COUNTIF(t.Close > t.MA200) / COUNT(*) AS breadth_ma200,
        COUNT(*)                               AS n_stocks
    FROM tav2_bq.ticker_prune AS t
    WHERE t.time >= '2014-01-01'
      AND t.MA200 IS NOT NULL
    GROUP BY t.time
    ORDER BY t.time
""", "breadth_ma200 (ticker_prune)")
breadth_raw['time'] = pd.to_datetime(breadth_raw['time'])
breadth = breadth_raw.set_index('time')

# ── Merge ────────────────────────────────────────────────────
df = pd.DataFrame({
    'state':   dt5g,
    'vni_ret': vni_ret,
}).dropna()
df['state']  = df['state'].astype(int)
df['alloc']  = df['state'].map(STATE_ALLOC)
df = df.join(breadth[['breadth_ma200']], how='left')
df = df.join(vn30f_ret.rename('vn30f_ret'), how='left')
df = df.sort_index()

# Forward returns (on VNI close aligned to merged index)
vni_aligned = vni_close.reindex(df.index)
for h in [5, 10, 20, 40, 60]:
    df[f'fwd{h}'] = vni_aligned.pct_change(h).shift(-h)

print(f"\n  Merged: {len(df):,} sessions | "
      f"{df.index[0].date()} → {df.index[-1].date()}")
print(f"  State counts: " +
      " | ".join(f"{STATE_NAMES[s]}={int((df.state==s).sum())}" for s in [1,2,3,4,5]))

# ════════════════════════════════════════════════════════════════
# PART 1: EX-BULL EVENT STUDY
# ════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 1: EX-BULL EVENT STUDY (forward returns by state)")
print("="*65)

horizons = [5, 10, 20, 40, 60]
print(f"\n{'State':10s} {'H':>5s} {'n':>5s} {'Med%':>7s} {'Win%':>7s} {'P10%':>7s} {'P90%':>7s}")
print("-"*55)
for s in [1, 2, 3, 4, 5]:
    for h in horizons:
        sub = df.loc[df['state'] == s, f'fwd{h}'].dropna()
        if len(sub) < 3: continue
        print(f"{STATE_NAMES[s]:10s} {h:5d} {len(sub):5d} "
              f"{sub.median()*100:+6.1f}% "
              f"{(sub>0).mean()*100:6.0f}% "
              f"{sub.quantile(0.1)*100:+6.1f}% "
              f"{sub.quantile(0.9)*100:+6.1f}%")

# EX-BULL episodes
print("\n  EX-BULL episodes:")
exbull_dates = df.index[df['state'] == 5]
gaps = (exbull_dates[1:] - exbull_dates[:-1]).days > 5
starts = list(exbull_dates[[True] + list(gaps)])
ends   = list(exbull_dates[list(gaps) + [True]])
for s_ep, e_ep in zip(starts, ends):
    n = (df.loc[s_ep:e_ep, 'state'] == 5).sum()
    vni_before = vni_close.loc[:s_ep].iloc[-1]
    vni_after  = vni_close.loc[e_ep:].iloc[0] if e_ep < vni_close.index[-1] else np.nan
    vni_peak   = vni_close.loc[s_ep:].iloc[:60].max() if len(vni_close.loc[s_ep:]) >= 60 else np.nan
    print(f"    {s_ep.date()} → {e_ep.date()} ({n} sessions) | "
          f"VNI={vni_before:.0f} | after60d={vni_close.loc[s_ep:].iloc[:60].iloc[-1]:.0f} "
          f"(peak={vni_peak:.0f})")

# ════════════════════════════════════════════════════════════════
# PART 2: BREADTH OVERBOUGHT ANALYSIS
# ════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 2: BREADTH OVERBOUGHT ANALYSIS")
print("="*65)

print(f"\n{'State':10s} {'n':>5s} {'Med%':>7s} {'Mean%':>7s} {'P25%':>7s} {'P75%':>7s} {'P90%':>7s}")
print("-"*55)
for s in [1, 2, 3, 4, 5]:
    sub = df.loc[df['state'] == s, 'breadth_ma200'].dropna()
    if len(sub) < 5: continue
    print(f"{STATE_NAMES[s]:10s} {len(sub):5d} "
          f"{sub.median()*100:6.0f}% "
          f"{sub.mean()*100:6.0f}% "
          f"{sub.quantile(0.25)*100:6.0f}% "
          f"{sub.quantile(0.75)*100:6.0f}% "
          f"{sub.quantile(0.90)*100:6.0f}%")

print("\n  EX-BULL sessions by breadth threshold:")
exbull_df = df[df['state'] == 5].copy()
n_valid = exbull_df['breadth_ma200'].notna().sum()
for thresh in [0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
    n_above = (exbull_df['breadth_ma200'] >= thresh).sum()
    pct = n_above / n_valid * 100 if n_valid > 0 else 0
    # fwd60 when breadth >= thresh vs not
    sub_hi = df.loc[(df['state']==5) & (df['breadth_ma200'] >= thresh), 'fwd60'].dropna()
    sub_lo = df.loc[(df['state']==5) & (df['breadth_ma200'] < thresh), 'fwd60'].dropna()
    hi_med = f"{sub_hi.median()*100:+.1f}%" if len(sub_hi) > 0 else "n/a"
    lo_med = f"{sub_lo.median()*100:+.1f}%" if len(sub_lo) > 0 else "n/a"
    print(f"    ≥{thresh*100:.0f}%: {n_above}/{n_valid} ({pct:.0f}%) | "
          f"fwd60 above={hi_med}, below={lo_med}")

# ════════════════════════════════════════════════════════════════
# PART 3: SYMMETRIC OVERLAY BACKTEST
# ════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 3: SYMMETRIC OVERLAY BACKTEST")
print("="*65)

TC = 0.001  # 0.1% per trade

df_bt = df[['state', 'alloc', 'vni_ret', 'vn30f_ret']].copy()
df_bt['alloc_t1'] = df_bt['alloc'].shift(1).fillna(0)  # T+1 execution

# Short overlay: 20% VN30F short when EX-BULL (alloc=1.3)
SHORT_SIZE = 0.20
for label, short_frac in [('short15', 0.15), ('short20', 0.20), ('short30', 0.30)]:
    df_bt[f'short_{label}'] = np.where(df_bt['alloc_t1'] >= 1.3, -short_frac, 0.0)

# TC on allocation changes
df_bt['tc_base'] = df_bt['alloc_t1'].diff().abs().fillna(0) * TC

# NAV: base
df_bt['pnl_base'] = df_bt['alloc_t1'] * df_bt['vni_ret'] - df_bt['tc_base']
nav_base = (1 + df_bt['pnl_base'].fillna(0)).cumprod()

# NAV: +SHORT overlays (only from 2017 when VN30F data exists)
results = {}
for label, short_frac in [('15%', 0.15), ('20%', 0.20), ('30%', 0.30)]:
    short_col = f'short_short{label.replace("%","")}'
    # Use VN30F return; fallback to VNI if missing
    vn30f_use = df_bt['vn30f_ret'].fillna(df_bt['vni_ret'])
    df_bt[f'short_{label}'] = np.where(df_bt['alloc_t1'] >= 1.3, -short_frac, 0.0)
    tc_short = df_bt[f'short_{label}'].diff().abs().fillna(0) * TC
    pnl = (df_bt['alloc_t1'] * df_bt['vni_ret']
           + df_bt[f'short_{label}'] * vn30f_use
           - df_bt['tc_base'] - tc_short)
    results[label] = (1 + pnl.fillna(0)).cumprod()

def metrics(nav, label=""):
    ret = nav.pct_change().dropna()
    n_years = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = nav.iloc[-1] ** (1 / n_years) - 1
    vol  = ret.std() * np.sqrt(252)
    sharpe = ret.mean() * 252 / (ret.std() * np.sqrt(252)) if ret.std() > 0 else 0
    roll_max = nav.cummax()
    dd = nav / roll_max - 1
    max_dd = dd.min()
    calmar = cagr / abs(max_dd) if max_dd != 0 else 0
    return {'label': label, 'CAGR': cagr, 'Vol': vol,
            'Sharpe': sharpe, 'MaxDD': max_dd, 'Calmar': calmar}

m_base = metrics(nav_base, 'Baseline')
print(f"\n  {'Strategy':18s} {'CAGR':>8s} {'Sharpe':>8s} {'MaxDD':>8s} {'Calmar':>8s}  ΔCAGR  ΔSharpe  ΔMaxDD")
print(f"  {'-'*78}")

def pf(m):
    return (f"  {m['label']:18s} {m['CAGR']:8.2%} {m['Sharpe']:8.2f} "
            f"{m['MaxDD']:8.2%} {m['Calmar']:8.2f}")
print(pf(m_base))
for label, nav_ov in results.items():
    m = metrics(nav_ov, f'+SHORT {label} VN30F')
    dcagr  = m['CAGR']   - m_base['CAGR']
    dsh    = m['Sharpe'] - m_base['Sharpe']
    ddd    = m['MaxDD']  - m_base['MaxDD']
    print(f"{pf(m)}  {dcagr:+.2%}  {dsh:+.2f}  {ddd:+.2%}")

# P&L from the short leg alone during EX-BULL
vn30f_use = df_bt['vn30f_ret'].fillna(df_bt['vni_ret'])
exbull_mask = df_bt['alloc_t1'] >= 1.3
short_pnl = -SHORT_SIZE * vn30f_use[exbull_mask]
print(f"\n  SHORT 20% VN30F leg (EX-BULL only):")
print(f"    Active sessions: {exbull_mask.sum()}")
print(f"    Cumulative P&L from short: {short_pnl.sum()*100:+.2f}%")
print(f"    Annualised drag/benefit: {short_pnl.mean()*252*100:+.2f}%/yr equivalent")
print(f"    Win rate of short leg: {(short_pnl > 0).mean()*100:.0f}%")

# VN30F correlation with VNINDEX during EX-BULL
corr = df.loc[exbull_mask, ['vni_ret','vn30f_ret']].corr().iloc[0,1]
print(f"    VNI vs VN30F correlation (EX-BULL): {corr:.3f}")

# What happened AFTER the two EX-BULL episodes
print("\n  Post-EX-BULL outcomes:")
for s_ep, e_ep in zip(starts, ends):
    after = vni_close.loc[e_ep:]
    if len(after) < 2: continue
    for h in [20, 60, 120]:
        if len(after) > h:
            ret_h = after.iloc[h] / after.iloc[0] - 1
            print(f"    After {e_ep.date()} (end of episode): "
                  f"+{h}d = {ret_h:+.1%}")

# ════════════════════════════════════════════════════════════════
# FIGURES
# ════════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("GENERATING FIGURES")
print("="*65)

fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('Euphoria SHORT Overlay — VN30F Short 20% @ EX-BULL\n'
             'Symmetric với Capitulation Buy (đối xứng CRISIS ↔ EX-BULL)',
             fontsize=13, fontweight='bold', color='white', y=0.98)

gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.50, wspace=0.38)

dark_bg = '#161b22'
ax_spine = '#30363d'

def style(ax, title=""):
    ax.set_facecolor(dark_bg)
    for s in ax.spines.values(): s.set_color(ax_spine)
    ax.tick_params(colors='#8b949e')
    ax.xaxis.label.set_color('#8b949e')
    ax.yaxis.label.set_color('#8b949e')
    if title: ax.set_title(title, color='#e6edf3', fontsize=10, fontweight='bold', pad=8)

# ── R1 C0-1: Fwd returns box by state ─────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
style(ax1, 'Forward 60D VNINDEX Returns by DT5G State')
data_box = []
labels_box = []
for s in [1, 2, 3, 4, 5]:
    sub = df.loc[df['state']==s, 'fwd60'].dropna() * 100
    if len(sub) > 3:
        data_box.append(sub.values)
        labels_box.append(f"{STATE_NAMES[s]}\n(n={len(sub)})")
bp = ax1.boxplot(data_box, labels=labels_box, patch_artist=True,
                 medianprops=dict(color='white', linewidth=2.5),
                 whiskerprops=dict(color='#8b949e'),
                 capprops=dict(color='#8b949e'),
                 flierprops=dict(marker='.', color='#8b949e', ms=3))
for patch, s in zip(bp['boxes'], [1,2,3,4,5]):
    patch.set_facecolor(STATE_COLORS[s])
    patch.set_alpha(0.75)
ax1.axhline(0, color='white', lw=0.8, ls='--', alpha=0.5)
ax1.set_ylabel('Return (%)', color='#8b949e')
ax1.set_ylim(-65, 100)
# Annotate medians
for i, s in enumerate([1,2,3,4,5]):
    sub = df.loc[df['state']==s, 'fwd60'].dropna() * 100
    if len(sub) > 3:
        ax1.text(i+1, sub.median()+3, f"{sub.median():+.0f}%",
                 ha='center', color='white', fontsize=9, fontweight='bold')

# ── R1 C2: Multi-horizon EX-BULL vs others ───────────────────
ax2 = fig.add_subplot(gs[0, 2])
style(ax2, 'Median Fwd Returns\nby Horizon & State')
for s in [3, 4, 5]:
    meds = [df.loc[df['state']==s, f'fwd{h}'].median()*100 for h in horizons]
    ax2.plot(horizons, meds, marker='o', label=STATE_NAMES[s],
             color=STATE_COLORS[s], linewidth=2.5, ms=6)
ax2.axhline(0, color='white', lw=0.8, ls='--', alpha=0.5)
ax2.set_xlabel('Horizon (days)')
ax2.set_ylabel('Median Return (%)')
ax2.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')
ax2.set_xticks(horizons)

# ── R2 C0-1: Breadth timeline ────────────────────────────────
ax3 = fig.add_subplot(gs[1, :2])
style(ax3, '% Stocks Above MA200 (ticker_prune) — Colored by DT5G State')
b_aligned = breadth['breadth_ma200'].reindex(df.index) * 100
ax3.plot(df.index, b_aligned, color='#30363d', lw=0.6, alpha=0.8)

for s in [1, 2, 3, 4, 5]:
    mask = df['state'] == s
    ax3.scatter(df.index[mask], b_aligned[mask], s=4,
                color=STATE_COLORS[s], alpha=0.7, zorder=3, label=STATE_NAMES[s])

ax3.axhline(75, color='#9467bd', lw=1.2, ls='--', alpha=0.8, label='75% (overbought)')
ax3.axhline(30, color='#d62728', lw=1.2, ls='--', alpha=0.8, label='30% (washout)')
ax3.set_ylabel('Breadth (%)')
ax3.legend(fontsize=8, facecolor='#1c2128', labelcolor='white', ncol=4)

# Shade EX-BULL
for s_ep, e_ep in zip(starts, ends):
    ax3.axvspan(s_ep, e_ep, alpha=0.2, color='#9467bd')

# ── R2 C2: Breadth distribution by state ────────────────────
ax4 = fig.add_subplot(gs[1, 2])
style(ax4, 'Breadth Distribution\nby DT5G State')
data_b = []
labels_b = []
for s in [1, 2, 3, 4, 5]:
    sub = df.loc[df['state']==s, 'breadth_ma200'].dropna() * 100
    if len(sub) > 5:
        data_b.append(sub.values)
        labels_b.append(STATE_NAMES[s])
bp2 = ax4.boxplot(data_b, labels=labels_b, patch_artist=True,
                  medianprops=dict(color='white', linewidth=2),
                  whiskerprops=dict(color='#8b949e'),
                  capprops=dict(color='#8b949e'))
for patch, s in zip(bp2['boxes'], [1,2,3,4,5]):
    patch.set_facecolor(STATE_COLORS[s])
    patch.set_alpha(0.75)
ax4.axhline(75, color='#9467bd', lw=1, ls='--', alpha=0.7)
ax4.set_ylabel('% Above MA200')

# ── R3 C0-1: NAV comparison ──────────────────────────────────
ax5 = fig.add_subplot(gs[2, :2])
style(ax5, 'NAV: Baseline DT5G vs SHORT VN30F 20% @ EX-BULL')

ax5.semilogy(nav_base.index, nav_base.values,
             label=f'DT5G Baseline ({m_base["CAGR"]:.1%}/Sh{m_base["Sharpe"]:.2f})',
             color='#58a6ff', lw=1.8)
m20 = metrics(results['20%'], '+SHORT 20%')
ax5.semilogy(results['20%'].index, results['20%'].values,
             label=f'+ SHORT 20% VN30F ({m20["CAGR"]:.1%}/Sh{m20["Sharpe"]:.2f})',
             color='#f97316', lw=1.8, ls='--')

# EX-BULL shading
for s_ep, e_ep in zip(starts, ends):
    ax5.axvspan(s_ep, e_ep, alpha=0.25, color='#9467bd', label='_')

# Annotate EX-BULL periods
for s_ep, e_ep in zip(starts, ends):
    mid = s_ep + (e_ep - s_ep) / 2
    ax5.text(mid, nav_base.loc[:s_ep].iloc[-1]*1.05,
             f"EX-BULL\n{s_ep.year}",
             ha='center', color='#c084fc', fontsize=8.5, fontweight='bold')

ax5.set_ylabel('NAV (log scale)', color='#8b949e')
patch_ex = mpatches.Patch(color='#9467bd', alpha=0.3, label='EX-BULL period')
handles, lbls = ax5.get_legend_handles_labels()
ax5.legend(handles + [patch_ex], lbls + ['EX-BULL period'],
           fontsize=9, facecolor='#1c2128', labelcolor='white')

# ── R3 C2: Metrics table ─────────────────────────────────────
ax6 = fig.add_subplot(gs[2, 2])
ax6.set_facecolor(dark_bg)
ax6.axis('off')
style(ax6, 'Performance Summary')

rows = [
    ['Strategy', 'CAGR', 'Sharpe', 'MaxDD', 'Calmar'],
    ['Baseline',
     f"{m_base['CAGR']:.1%}", f"{m_base['Sharpe']:.2f}",
     f"{m_base['MaxDD']:.1%}", f"{m_base['Calmar']:.2f}"],
]
for label, nav_ov in results.items():
    m = metrics(nav_ov, f'+SHORT {label}')
    rows.append([
        f'+SHORT {label}',
        f"{m['CAGR']:.1%} ({m['CAGR']-m_base['CAGR']:+.2%})",
        f"{m['Sharpe']:.2f} ({m['Sharpe']-m_base['Sharpe']:+.2f})",
        f"{m['MaxDD']:.1%} ({m['MaxDD']-m_base['MaxDD']:+.2%})",
        f"{m['Calmar']:.2f} ({m['Calmar']-m_base['Calmar']:+.2f})",
    ])

tbl = ax6.table(cellText=rows[1:], colLabels=rows[0],
                loc='center', cellLoc='center')
tbl.auto_set_font_size(False)
tbl.set_fontsize(8.5)
tbl.scale(1.1, 2.0)
for (r, c), cell in tbl.get_celld().items():
    cell.set_facecolor('#1c2128' if r % 2 == 0 else dark_bg)
    cell.set_text_props(color='#e6edf3')
    cell.set_edgecolor(ax_spine)
    if r == 0:
        cell.set_facecolor('#21262d')
        cell.set_text_props(color='white', fontweight='bold')

outfile = os.path.join(WORKDIR, "euphoria_short_analysis.png")
fig.savefig(outfile, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"  Saved: euphoria_short_analysis.png")
plt.close()

# ── Save CSV ─────────────────────────────────────────────────
rows_csv = []
for h in horizons:
    for s in [1,2,3,4,5]:
        sub = df.loc[df['state']==s, f'fwd{h}'].dropna()
        if len(sub) < 3: continue
        rows_csv.append({
            'state': s, 'state_name': STATE_NAMES[s], 'horizon': h,
            'n': len(sub), 'median': sub.median(), 'mean': sub.mean(),
            'win_rate': (sub>0).mean(),
            'p10': sub.quantile(0.1), 'p90': sub.quantile(0.9)
        })
pd.DataFrame(rows_csv).to_csv(
    os.path.join(WORKDIR, "data/euphoria_exbull_event_study.csv"), index=False)
print("  Saved: euphoria_exbull_event_study.csv")

print("\n" + "="*65)
print("DONE")
print("="*65)
