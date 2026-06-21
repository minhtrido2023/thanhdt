"""
exbull_value_tilt.py
Variant D: State-conditional value/momentum tilt — max VALUE khi EX-BULL
Mở rộng từ backtest_core_arch.py (A/B/C đã có), thêm D.

Logic:
  CRISIS   → 30% value / 70% momentum  (crisis value traps, momentum rebound)
  BEAR     → 40% value / 60% momentum
  NEUTRAL  → 50% value / 50% momentum  (= B balanced)
  BULL     → 60% value / 40% momentum  (Fitness Matrix: value works in bull)
  EX-BULL  → 80% value / 20% momentum  (peak momentum crowding, value safe)
"""
import sys, os
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import subprocess, numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from io import StringIO
import warnings; warnings.filterwarnings('ignore')

WORKDIR  = r"/home/trido/thanhdt/WorkingClaude"
PROJECT  = "lithe-record-440915-m9"
BQ_PATH  = r"bq"
CACHE    = WORKDIR + r"\data\core_arch_backtest.csv"
os.chdir(WORKDIR)

STATE_NAMES  = {1:'CRISIS', 2:'BEAR', 3:'NEUTRAL', 4:'BULL', 5:'EX-BULL'}
STATE_COLORS = {1:'#d62728', 2:'#ff7f0e', 3:'#7fafcf', 4:'#2ca02c', 5:'#9467bd'}

# value weight per DT5G state (parameter sweep will vary this)
BASE_WVAL = {1: 0.30, 2: 0.40, 3: 0.50, 4: 0.60, 5: 0.80}

# ── helpers ─────────────────────────────────────────────────
def bq(sql):
    cmd = f'"{BQ_PATH}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --quiet --max_rows=100000'
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True, encoding='utf-8', shell=True)
    if r.returncode != 0:
        print(f"  BQ ERROR: {r.stderr[:200]}"); return pd.DataFrame()
    return pd.read_csv(StringIO(r.stdout))

def ann(ret):
    ret = ret.dropna(); n = len(ret)
    if n < 3: return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan, Calmar=np.nan)
    mu = ret.mean()*12; sd = ret.std(ddof=1)*np.sqrt(12)
    cagr = (1+ret).prod()**(12/n)-1
    nav = (1+ret).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd>0 else 0, MaxDD=dd*100,
                Calmar=cagr/abs(dd) if dd<0 else np.nan)

def fmt(m):
    if m['CAGR'] != m['CAGR']: return "  n/a"
    return (f"CAGR {m['CAGR']:5.1f}%  Sharpe {m['Sharpe']:.2f}  "
            f"MaxDD {m['MaxDD']:5.1f}%  Calmar {m['Calmar']:.2f}")

def sub(r, lo, hi):
    return r[(r.index >= pd.Period(lo)) & (r.index <= pd.Period(hi))]

# ════════════════════════════════════════════════════════════
# 1. LOAD EXISTING CORE BACKTEST
# ════════════════════════════════════════════════════════════
print("Loading cached core-arch backtest...")
cache = pd.read_csv(CACHE, index_col=0)
cache.index = pd.PeriodIndex(cache.index, freq="M")

A = cache["A"]         # momentum-core (V5 DT5G-gated)
B = cache["B"]         # balanced 50/50 static
C = cache["C"]         # adaptive IC-tilt
V = cache["value"]     # value book

print(f"  Monthly returns: {cache.index.min()} -> {cache.index.max()} ({len(cache)} months)")
print(f"  EX-BULL months identifiable from DT5G query...\n")

# ════════════════════════════════════════════════════════════
# 2. LOAD DT5G STATE → monthly mode
# ════════════════════════════════════════════════════════════
print("Loading DT5G states...")
raw = bq("""
    SELECT s.time, s.state
    FROM tav2_bq.vnindex_5state_dt5g_live AS s
    ORDER BY s.time
""")
raw['time'] = pd.to_datetime(raw['time'])
raw = raw.set_index('time')['state'].astype(int)
# Monthly mode (which state dominated each month)
monthly_state = raw.resample('ME').apply(lambda x: x.mode()[0] if len(x) > 0 else np.nan)
monthly_state.index = monthly_state.index.to_period('M')
monthly_state = monthly_state.astype(int)

# Align to cache index
idx = cache.index
monthly_state = monthly_state.reindex(idx)
# Fill missing with NEUTRAL (3)
monthly_state = monthly_state.fillna(3).astype(int)

print(f"  Monthly state distribution:")
for s in [1,2,3,4,5]:
    n = (monthly_state==s).sum()
    print(f"    {STATE_NAMES[s]:8s}: {n} months")

# EX-BULL months
exbull_months = monthly_state[monthly_state==5].index
print(f"\n  EX-BULL months: {list(exbull_months)}")
print(f"  Value return in EX-BULL months: {V.reindex(exbull_months).mean()*100:+.2f}%/month avg")
print(f"  Momentum return in EX-BULL months: {A.reindex(exbull_months).mean()*100:+.2f}%/month avg")

# ════════════════════════════════════════════════════════════
# 3. BUILD VARIANT D: state-conditional tilt
# ════════════════════════════════════════════════════════════

def build_D(wval_by_state):
    """Build blended series given a dict {state: value_weight}."""
    wmom = monthly_state.map(lambda s: 1 - wval_by_state.get(s, 0.50))
    wval = monthly_state.map(lambda s: wval_by_state.get(s, 0.50))
    return (wmom * A + wval * V).reindex(idx)

D = build_D(BASE_WVAL)
# name label
D_LABEL = "D EX-BULL→80% value (state-tilt)"

# Also build some sensitivity variants
D_MILD  = build_D({1: 0.40, 2: 0.45, 3: 0.50, 4: 0.55, 5: 0.65})
D_MAX   = build_D({1: 0.20, 2: 0.35, 3: 0.50, 4: 0.70, 5: 0.90})
D_FLAT  = build_D({1: 0.50, 2: 0.50, 3: 0.50, 4: 0.50, 5: 0.80})  # only EX-BULL tilt

all_strats = {
    "A momentum-core": A,
    "B balanced 50/50": B,
    "C adaptive IC-tilt": C,
    "D state-tilt BASE": D,
    "D state-tilt MILD": D_MILD,
    "D flat+EX-BULL": D_FLAT,
    "  value-only ref": V,
}

# ════════════════════════════════════════════════════════════
# 4. RESULTS
# ════════════════════════════════════════════════════════════
GRIND = ("2025-09", "2026-05")

print("\n" + "="*70)
print("FULL PERIOD")
print("="*70)
print(f"{'Strategy':>24}  CAGR   Sharpe  MaxDD   Calmar")
print("-"*60)
for name, r in all_strats.items():
    m = ann(r.dropna())
    print(f"{name:>24}  {fmt(m)}")

print("\n" + "="*70)
print("IS (2014-2019) / OOS (2020-2026)")
print("="*70)
for name, r in all_strats.items():
    mi = ann(sub(r,'2014-01','2019-12'))
    mo = ann(sub(r,'2020-01','2026-12'))
    print(f"{name:>24}  IS  {fmt(mi)}")
    print(f"{name:>24}  OOS {fmt(mo)}")

print("\n" + "="*70)
print(f"MOMENTUM GRIND {GRIND[0]}..{GRIND[1]}")
print("="*70)
for name, r in all_strats.items():
    g = sub(r, *GRIND); cum = ((1+g).prod()-1)*100 if len(g)>0 else np.nan
    print(f"{name:>24}  cumulative {cum:+5.1f}%  (worst mo {g.min()*100:+.1f}%)")

print("\n" + "="*70)
print("BULL YEARS")
print("="*70)
for yr, label in [("2021","2021 VN mega-bull"),("2023","2023 recovery"),("2025","2025 VIC-led")]:
    line = f"  {label}: "
    for name, r in all_strats.items():
        g = sub(r, f"{yr}-01", f"{yr}-12")
        if len(g) > 0:
            line += f"{name.split()[0]}={((1+g).prod()-1)*100:+5.1f}%  "
    print(line)

print("\n" + "="*70)
print("EX-BULL MONTHS DEEP DIVE")
print("="*70)
print(f"  {'Strategy':>24}  EX-BULL avg/mo  EX-BULL cum  vs B delta")
B_eb = B.reindex(exbull_months).mean()*100 if len(exbull_months) > 0 else 0
for name, r in all_strats.items():
    eb = r.reindex(exbull_months)
    if len(eb) == 0: continue
    avg = eb.mean()*100
    cum = ((1+eb).prod()-1)*100
    delta = cum - ((1+B.reindex(exbull_months)).prod()-1)*100
    print(f"  {name:>24}  {avg:+.2f}%/mo    {cum:+6.2f}%    {delta:+.2f}pp vs B")

# Monthly breakdown in EX-BULL months
print(f"\n  Month-by-month in EX-BULL:")
print(f"  {'Month':>8}  {'State':>8}  {'A mom':>7}  {'value':>7}  {'B 50/50':>8}  {'D tilt':>7}")
for m_ep in exbull_months:
    s = monthly_state.get(m_ep, 3)
    a_r = A.get(m_ep, np.nan)*100
    v_r = V.get(m_ep, np.nan)*100
    b_r = B.get(m_ep, np.nan)*100
    d_r = D.get(m_ep, np.nan)*100
    print(f"  {str(m_ep):>8}  {STATE_NAMES[s]:>8}  {a_r:+6.1f}%  {v_r:+6.1f}%  {b_r:+7.1f}%  {d_r:+6.1f}%")

# ════════════════════════════════════════════════════════════
# 5. PARAMETER SWEEP: best EX-BULL value weight
# ════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PARAMETER SWEEP: EX-BULL value weight (others fixed 50%)")
print("="*70)
print(f"  {'EX-BULL wval':>14}  {'Full CAGR':>10}  {'Sharpe':>8}  {'MaxDD':>8}  {'Calmar':>8}  {'Grind':>8}  {'vs B sharpe':>12}")
m_B = ann(B)
for w in [0.30, 0.40, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
    r = build_D({1: 0.50, 2: 0.50, 3: 0.50, 4: 0.50, 5: w})
    m = ann(r.dropna())
    g = sub(r, *GRIND); grind_cum = ((1+g).prod()-1)*100 if len(g)>0 else np.nan
    delta_sh = m['Sharpe'] - m_B['Sharpe']
    mark = " <--" if w == 0.80 else ""
    print(f"  {w:>14.0%}  {m['CAGR']:>9.1f}%  {m['Sharpe']:>8.2f}  "
          f"{m['MaxDD']:>7.1f}%  {m['Calmar']:>8.2f}  {grind_cum:>7.1f}%  {delta_sh:>+11.2f}{mark}")

# ════════════════════════════════════════════════════════════
# 6. FIGURES
# ════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('EX-BULL Value Tilt — Variant D: State-Conditional Momentum/Value Blend',
             fontsize=13, fontweight='bold', color='white', y=0.98)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)
dark_bg = '#161b22'; ax_sp = '#30363d'

def style(ax, title=""):
    ax.set_facecolor(dark_bg)
    for s in ax.spines.values(): s.set_color(ax_sp)
    ax.tick_params(colors='#8b949e')
    if title: ax.set_title(title, color='#e6edf3', fontsize=10, fontweight='bold', pad=8)

# ── NAV comparison ───────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
style(ax1, 'Cumulative NAV: A (momentum) vs B (50/50) vs D (EX-BULL tilt)')
nav_colors = {'A momentum-core': '#58a6ff', 'B balanced 50/50': '#3fb950',
              'D state-tilt BASE': '#f97316', '  value-only ref': '#8b949e'}
for name, r in all_strats.items():
    if name not in nav_colors: continue
    nav = (1+r.dropna()).cumprod()
    nav.index = nav.index.to_timestamp()
    ax1.semilogy(nav.index, nav.values,
                 label=name.strip(), color=nav_colors[name],
                 lw=2.2 if 'D' in name else 1.5,
                 ls='--' if 'D' in name else '-')

# Shade EX-BULL months
for m_ep in exbull_months:
    ts = m_ep.to_timestamp()
    te = (m_ep + 1).to_timestamp()
    ax1.axvspan(ts, te, alpha=0.25, color='#9467bd', label='_')

import matplotlib.patches as mpatches
patch_eb = mpatches.Patch(color='#9467bd', alpha=0.3, label='EX-BULL month')
handles, lbls = ax1.get_legend_handles_labels()
ax1.legend(handles + [patch_eb], lbls + ['EX-BULL month'],
           fontsize=9, facecolor='#1c2128', labelcolor='white')
ax1.set_ylabel('NAV (log, start=1)', color='#8b949e')

# ── EX-BULL month returns heatmap ─────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
style(ax2, 'EX-BULL Month Returns\nA vs Value vs D')
if len(exbull_months) > 0:
    eb_data = pd.DataFrame({
        'Momentum(A)': A.reindex(exbull_months)*100,
        'Value': V.reindex(exbull_months)*100,
        'D-tilt': D.reindex(exbull_months)*100,
    })
    x = np.arange(len(exbull_months))
    w = 0.25
    colors_bar = ['#58a6ff', '#e8c547', '#f97316']
    for i, (col, c) in enumerate(zip(eb_data.columns, colors_bar)):
        bars = ax2.bar(x + i*w, eb_data[col].values, w, label=col, color=c, alpha=0.8)
    ax2.set_xticks(x + w)
    ax2.set_xticklabels([str(m)[-7:] for m in exbull_months], rotation=45, ha='right',
                         color='#8b949e', fontsize=8)
    ax2.axhline(0, color='white', lw=0.8, ls='--', alpha=0.5)
    ax2.set_ylabel('Monthly Return (%)', color='#8b949e')
    ax2.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')

# ── Sweep chart ───────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, :2])
style(ax3, 'Parameter Sweep: EX-BULL Value Weight (others = 50%)')
weights = [0.30, 0.40, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]
cagrs, sharpes, caldmar, grinds = [], [], [], []
for w in weights:
    r = build_D({1: 0.50, 2: 0.50, 3: 0.50, 4: 0.50, 5: w})
    m = ann(r.dropna())
    g = sub(r, *GRIND)
    cagrs.append(m['CAGR']); sharpes.append(m['Sharpe'])
    caldmar.append(m['Calmar'])
    grinds.append(((1+g).prod()-1)*100 if len(g)>0 else np.nan)

ax3_r = ax3.twinx()
ax3.plot(weights, sharpes, 'o-', color='#58a6ff', lw=2, label='Sharpe (left)')
ax3.plot(weights, caldmar, 's--', color='#3fb950', lw=2, label='Calmar (left)')
ax3_r.plot(weights, grinds, '^:', color='#f97316', lw=2, label='Grind cum% (right)')
ax3.axvline(0.80, color='white', lw=1, ls='--', alpha=0.5, label='Base (80%)')
ax3.axhline(m_B['Sharpe'], color='#58a6ff', lw=1, ls=':', alpha=0.5)
ax3.set_xlabel('EX-BULL value weight', color='#8b949e')
ax3.set_ylabel('Sharpe / Calmar', color='#8b949e')
ax3_r.set_ylabel('Grind period cum%', color='#f97316')
ax3_r.tick_params(colors='#f97316')
lines1, lbl1 = ax3.get_legend_handles_labels()
lines2, lbl2 = ax3_r.get_legend_handles_labels()
ax3.legend(lines1+lines2, lbl1+lbl2, fontsize=9, facecolor='#1c2128', labelcolor='white')
ax3.set_xticks(weights)
ax3.set_xticklabels([f'{w:.0%}' for w in weights], color='#8b949e')

# ── Summary table ─────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 2])
ax4.set_facecolor(dark_bg); ax4.axis('off')
style(ax4, 'Performance Summary')

plot_strats = ["A momentum-core", "B balanced 50/50", "C adaptive IC-tilt", "D state-tilt BASE"]
rows = [['Strategy', 'CAGR', 'Sharpe', 'MaxDD', 'Calmar']]
for name in plot_strats:
    r = all_strats[name]
    m = ann(r.dropna())
    rows.append([name.split()[0]+' '+name.split()[1] if len(name.split())>1 else name,
                 f"{m['CAGR']:.1f}%", f"{m['Sharpe']:.2f}",
                 f"{m['MaxDD']:.1f}%", f"{m['Calmar']:.2f}"])

tbl = ax4.table(cellText=rows[1:], colLabels=rows[0], loc='center', cellLoc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1.2, 2.0)
for (r_i, c), cell in tbl.get_celld().items():
    cell.set_facecolor('#1c2128' if r_i%2==0 else dark_bg)
    cell.set_text_props(color='#e6edf3')
    cell.set_edgecolor(ax_sp)
    if r_i == 0:
        cell.set_facecolor('#21262d'); cell.set_text_props(color='white', fontweight='bold')
    if r_i > 0 and c == 0 and 'D' in rows[r_i][0]:
        cell.set_facecolor('#2d1b0e')  # highlight D

outfile = WORKDIR + r"\exbull_value_tilt.png"
fig.savefig(outfile, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: exbull_value_tilt.png")
plt.close()

# Save results CSV
rows_csv = []
for name, r in all_strats.items():
    m_full = ann(r.dropna())
    m_oos  = ann(sub(r, '2020-01', '2026-12'))
    g = sub(r, *GRIND)
    rows_csv.append({
        'strategy': name.strip(),
        'cagr_full': m_full['CAGR'], 'sharpe_full': m_full['Sharpe'],
        'maxdd_full': m_full['MaxDD'], 'calmar_full': m_full['Calmar'],
        'cagr_oos':  m_oos['CAGR'],  'sharpe_oos':  m_oos['Sharpe'],
        'grind_cum':  ((1+g).prod()-1)*100 if len(g)>0 else np.nan,
    })
pd.DataFrame(rows_csv).to_csv(WORKDIR + r"\data\exbull_tilt_results.csv", index=False)
print("Saved: data/exbull_tilt_results.csv")
print("\nDONE")
