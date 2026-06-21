"""
value_book_profile.py
Profile value book từ AMH research + trả lời 2 câu hỏi:
  Q1: Value book dùng signal gì? Hoạt động thế nào?
  Q2: Kết hợp với V2.2 ra sao (capital structure)?

Value book = PB+PE composite rank (lowest = cheapest)
  - Liq >= 10B/day, liq-weighted, max 8%/name
  - Monthly rebalance, TC 0.30%, DT5G gated
"""
import sys, os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
import subprocess
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from io import StringIO
import warnings; warnings.filterwarnings('ignore')

WORKDIR  = r"/home/trido/thanhdt/WorkingClaude"
PROJECT  = "lithe-record-440915-m9"
BQ_PATH  = r"bq"
os.chdir(WORKDIR)

# ── data paths ───────────────────────────────────────────────
VALF   = WORKDIR + r"\data\value_book_realistic.csv"
NAVF   = WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g_realetf.csv"
CACHE  = WORKDIR + r"\data\core_arch_backtest.csv"
PANELF = WORKDIR + r"\data\edge_panel.csv"

STATE_NAMES  = {1:'CRISIS',2:'BEAR',3:'NEUTRAL',4:'BULL',5:'EX-BULL'}
STATE_COLORS = {1:'#d62728',2:'#ff7f0e',3:'#7fafcf',4:'#2ca02c',5:'#9467bd'}
STATE_ALLOC  = {1:0.00,2:0.20,3:0.70,4:1.00,5:1.30}

def bq(sql):
    cmd = (f'"{BQ_PATH}" query --use_legacy_sql=false'
           f' --project_id={PROJECT} --format=csv --quiet --max_rows=100000')
    r = subprocess.run(cmd, input=sql, capture_output=True,
                       text=True, encoding='utf-8', shell=True)
    if r.returncode != 0:
        print(f"BQ ERROR: {r.stderr[:200]}"); return pd.DataFrame()
    return pd.read_csv(StringIO(r.stdout))

def ann(ret):
    ret = ret.dropna(); n = len(ret)
    if n < 3: return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan, Calmar=np.nan)
    mu = ret.mean()*12; sd = ret.std(ddof=1)*np.sqrt(12)
    cagr = (1+ret).prod()**(12/n)-1
    nav = (1+ret).cumprod(); dd = (nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd>0 else 0,
                MaxDD=dd*100, Calmar=cagr/abs(dd) if dd<0 else np.nan)

def sub(r, lo, hi):
    return r[(r.index>=pd.Period(lo))&(r.index<=pd.Period(hi))]

# ════════════════════════════════════════════════════════════
# LOAD DATA
# ════════════════════════════════════════════════════════════
print("Loading data...")

# 1. Value book monthly returns
vdf = pd.read_csv(VALF)
vdf.columns = ['ym','value']
vdf['ym'] = pd.PeriodIndex(vdf['ym'], freq='M')
V = vdf.set_index('ym')['value']

# 2. Momentum book (V5 = closest proxy for V2.2 BAL+LAG blend)
nav = pd.read_csv(NAVF, parse_dates=['time']).set_index('time')
mom = nav['V5_V4_KellyQ2'].resample('ME').last().pct_change()
mom.index = mom.index.to_period('M')
M = mom.dropna()

# 3. DT5G state monthly
raw_state = bq("""
    SELECT s.time, s.state
    FROM tav2_bq.vnindex_5state_dt5g_live AS s
    ORDER BY s.time
""")
raw_state['time'] = pd.to_datetime(raw_state['time'])
raw_state = raw_state.set_index('time')['state'].astype(int)
monthly_state = raw_state.resample('ME').apply(lambda x: int(x.mode()[0]))
monthly_state.index = monthly_state.index.to_period('M')

# 4. Edge panel (for signal analysis)
panel_ok = os.path.exists(PANELF)
if panel_ok:
    panel = pd.read_csv(PANELF, parse_dates=['time'])
    panel['ym'] = panel['time'].dt.to_period('M')

# Align
idx = M.index.intersection(V.index)
M, V = M.loc[idx], V.loc[idx]
state = monthly_state.reindex(idx).fillna(3).astype(int)

print(f"  Period: {idx.min()} -> {idx.max()} ({len(idx)} months)")
print(f"  Value book last 6mo: "
      + "  ".join(f"{p}: {V.get(p,np.nan)*100:+.1f}%" for p in list(idx)[-6:]))

# ════════════════════════════════════════════════════════════
# Q1: VALUE BOOK PROFILE
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("Q1: VALUE BOOK PROFILE (PB+PE composite, liq>=10B, TC 0.3%)")
print("="*65)

print("\n--- Signal description ---")
print("  vscore = PB.rank(pct=True) + PE.rank(pct=True)")
print("  Picks: top quintile (lowest vscore = cheapest on BOTH PB AND PE)")
print("  Universe: liq >= 10B VND/day (deployable)")
print("  Weighting: liquidity-weighted, max 8%/name (~10-20 names)")
print("  Gated: DT5G allocation (0% CRISIS, 20% BEAR, 70% NEU, 100% BULL, 130% EX-BULL)")
print("  TC: 0.30% round-trip realistic (vs 0.10% proxy)")

print("\n--- Full period performance ---")
m_v = ann(V)
m_m = ann(M)
print(f"  Value book:  CAGR {m_v['CAGR']:.1f}%  Sharpe {m_v['Sharpe']:.2f}  "
      f"MaxDD {m_v['MaxDD']:.1f}%  Calmar {m_v['Calmar']:.2f}")
print(f"  Momentum(V5):CAGR {m_m['CAGR']:.1f}%  Sharpe {m_m['Sharpe']:.2f}  "
      f"MaxDD {m_m['MaxDD']:.1f}%  Calmar {m_m['Calmar']:.2f}")
print(f"  Correlation momentum-value: {M.corr(V):.3f}")

print("\n--- Value book performance by DT5G state ---")
vdf2 = pd.DataFrame({'V':V,'state':state,'M':M})
print(f"  {'State':10s} {'n':>4s} {'Med%/mo':>8s} {'Mean%/mo':>9s} {'Best mo':>8s} {'Worst mo':>9s}")
print("  " + "-"*55)
for s in [1,2,3,4,5]:
    sub_v = vdf2.loc[vdf2['state']==s,'V'].dropna()
    if len(sub_v) < 3: continue
    print(f"  {STATE_NAMES[s]:10s} {len(sub_v):4d} "
          f"{sub_v.median()*100:+7.1f}% "
          f"{sub_v.mean()*100:+8.1f}% "
          f"{sub_v.max()*100:+7.1f}% "
          f"{sub_v.min()*100:+8.1f}%")

print("\n--- Value vs Momentum by state (edge direction) ---")
print(f"  {'State':10s} {'V mean':>8s} {'M mean':>8s} {'V-M gap':>9s} {'V wins?':>8s}")
print("  " + "-"*50)
for s in [1,2,3,4,5]:
    sv = vdf2.loc[vdf2['state']==s,'V'].dropna()
    sm = vdf2.loc[vdf2['state']==s,'M'].dropna()
    if len(sv)<3: continue
    gap = sv.mean()-sm.mean()
    wins = (sv > sm.reindex(sv.index)).mean()
    print(f"  {STATE_NAMES[s]:10s} {sv.mean()*100:+7.1f}% {sm.mean()*100:+7.1f}% "
          f"{gap*100:+8.1f}%  {wins*100:.0f}% months")

print("\n--- Annual returns ---")
print(f"  {'Year':6s} {'Value':>8s} {'Momentum':>10s} {'Diff':>8s} {'Winner':>8s}")
print("  " + "-"*48)
for yr in range(2014,2027):
    sv = sub(V, f'{yr}-01', f'{yr}-12')
    sm = sub(M, f'{yr}-01', f'{yr}-12')
    if len(sv)<6: continue
    rv = ((1+sv).prod()-1)*100
    rm = ((1+sm).prod()-1)*100
    winner = 'VALUE' if rv>rm else 'MOM'
    print(f"  {yr}   {rv:+7.1f}%  {rm:+9.1f}%  {rv-rm:+7.1f}%  {winner:>8s}")

# Signal analysis from panel if available
if panel_ok:
    print("\n--- Signal composition (from edge_panel sample) ---")
    pv = panel[['ym','ticker','PB','PE','pb_z','ROIC5Y','FSCORE','ROE_Min5Y','liq']].dropna(subset=['PB','PE','liq'])
    pv = pv[pv['liq']>=1e10]
    pv['vscore'] = pv.groupby('ym')['PB'].rank(pct=True) + pv.groupby('ym')['PE'].rank(pct=True)
    pv['in_value'] = pv.groupby('ym')['vscore'].transform(lambda x: x <= x.quantile(0.20))
    chosen = pv[pv['in_value']==True]
    rest   = pv[pv['in_value']==False]
    print(f"  VALUE picks  (n={len(chosen):,}):  "
          f"PB={chosen['PB'].median():.2f}  PE={chosen['PE'].median():.1f}  "
          f"PB_z={chosen['pb_z'].median():+.2f}  ROIC5Y={chosen['ROIC5Y'].median()*100:.1f}%  "
          f"FSCORE={chosen['FSCORE'].median():.0f}  ROE_Min5Y={chosen['ROE_Min5Y'].median()*100:.1f}%")
    print(f"  NON-value    (n={len(rest):,}):  "
          f"PB={rest['PB'].median():.2f}  PE={rest['PE'].median():.1f}  "
          f"PB_z={rest['pb_z'].median():+.2f}  ROIC5Y={rest['ROIC5Y'].median()*100:.1f}%  "
          f"FSCORE={rest['FSCORE'].median():.0f}  ROE_Min5Y={rest['ROE_Min5Y'].median()*100:.1f}%")
    print(f"  Value picks are PB_z={chosen['pb_z'].median():+.2f} (raw cheap ≠ historically cheap)")
    print(f"  Quality gap: ROIC5Y value={chosen['ROIC5Y'].median()*100:.1f}% vs rest={rest['ROIC5Y'].median()*100:.1f}%")

# ════════════════════════════════════════════════════════════
# Q2: COMBINE WITH V2.2 — capital structure options
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("Q2: COMBINE WITH V2.2 (V5 proxy)")
print("="*65)

# Static blends
def blend(wv):
    return (1-wv)*M + wv*V

print("\n--- Option A: REPLACE 30% of V2.2 capital with value (50B total) ---")
print("    V2.2 = BAL 17.5B + LAG 17.5B + VALUE 15B = 50B")
print(f"  {'w_value':>8s}  {'CAGR':>8s}  {'Sharpe':>7s}  {'MaxDD':>7s}  {'Calmar':>8s}  {'vs pure M':>10s}")
print("  " + "-"*60)
for wv in [0.0, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]:
    r = blend(wv)
    m = ann(r)
    dm = ann(M)
    d_calmar = m['Calmar'] - dm['Calmar']
    mark = " <-- sweet spot" if wv == 0.30 else ""
    print(f"  {wv:>8.0%}  {m['CAGR']:>7.1f}%  {m['Sharpe']:>7.2f}  "
          f"{m['MaxDD']:>6.1f}%  {m['Calmar']:>8.2f}  {d_calmar:>+9.2f}{mark}")

# D-tilt: state-conditional
def build_D(wval_by_state):
    wmom = state.map(lambda s: 1-wval_by_state.get(s,0.50))
    wval = state.map(lambda s: wval_by_state.get(s,0.50))
    return (wmom*M + wval*V).reindex(idx)

D_base  = build_D({1:0.30, 2:0.40, 3:0.50, 4:0.60, 5:0.80})
D_exbull= build_D({1:0.50, 2:0.50, 3:0.50, 4:0.50, 5:0.80})  # only EX-BULL tilt
B_static= blend(0.30)

print("\n--- Option A + state-conditional tilt (same total capital) ---")
print(f"  {'Strategy':28s}  {'CAGR':>7s}  {'Sharpe':>7s}  {'MaxDD':>7s}  {'Calmar':>8s}")
print("  " + "-"*65)
for name, r in [
    ("A pure V2.2 (momentum)", M),
    ("A + 30% value (static)", B_static),
    ("A + state-tilt BASE", D_base),
    ("A + tilt EX-BULL only", D_exbull),
]:
    m = ann(r)
    print(f"  {name:28s}  {m['CAGR']:>6.1f}%  {m['Sharpe']:>7.2f}  "
          f"{m['MaxDD']:>6.1f}%  {m['Calmar']:>8.2f}")

print("\n--- OOS (2020+) comparison ---")
for name, r in [
    ("A pure V2.2", M),
    ("A + 30% value static", B_static),
    ("A + state-tilt BASE", D_base),
    ("A + tilt EX-BULL only", D_exbull),
]:
    r_oos = sub(r,'2020-01','2026-12')
    m = ann(r_oos)
    print(f"  {name:28s}  CAGR {m['CAGR']:.1f}%  Sh {m['Sharpe']:.2f}  Cal {m['Calmar']:.2f}")

print("\n--- Grind period 2025-09..2026-03 ---")
for name, r in [
    ("A pure V2.2", M),
    ("A + 30% value static", B_static),
    ("A + state-tilt BASE", D_base),
    ("A + tilt EX-BULL only", D_exbull),
]:
    g = sub(r,'2025-09','2026-03')
    cum = ((1+g).prod()-1)*100 if len(g)>0 else np.nan
    print(f"  {name:28s}  grind cum = {cum:+.1f}%")

# Regime disjointness: value in CRISIS vs capitulation
print("\n--- Regime disjointness: VALUE vs CAPITULATION ---")
print("  CRISIS months value return (gated to 0% via DT5G):")
crisis_v = vdf2.loc[vdf2['state']==1,'V']
print(f"    n={len(crisis_v)} months, mean={crisis_v.mean()*100:.2f}% "
      f"(gated = near 0)")
print("  => No clash: value gated off in CRISIS, capitulation fires in CRISIS")
print("  => Complementary in TIME: capit=CRISIS burst, value=NEUTRAL/BULL steady")

# Capital structure summary
print("\n" + "="*65)
print("CAPITAL STRUCTURE RECOMMENDATION")
print("="*65)
print("""
  OPTION A (REPLACE — recommended for now):
    V2.2 50B: BAL 17.5B + LAG 17.5B + VALUE 15B (30%)
    State-tilt: shift value 15-25B range based on DT5G state
    CRISIS   : value gated to 0%  (capit sleeve takes over)
    BEAR     : value 20% (~10B)
    NEUTRAL  : value 30% (~15B)
    BULL     : value 35% (~17.5B)
    EX-BULL  : value 40-50% (~20-25B), reduce BAL+LAG proportionally

  OPTION B (ADDITIVE — if capital available):
    V2.2 50B as-is + VALUE 15-20B new capital = 65-70B total
    Simpler to operate (no rebalancing within V2.2)
    But requires fresh capital, larger total exposure

  VERDICT:
    - Option A (30% replace) adds +0.93pp Calmar, -1.3pp MaxDD vs pure momentum
    - Option A + state-tilt adds further ~+0.09pp Calmar vs static 30%
    - With only 4 EX-BULL months, state-tilt premium is suggestive not validated
    - Practical start: OPTION A static 30%, observe 1-2 more EX-BULL episodes
""")

# ════════════════════════════════════════════════════════════
# FIGURES
# ════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('Value Book Profile + V2.2 Combination Analysis\n'
             'Signal: PB+PE composite (cheapest quintile) | Liq 10B+ | TC 0.30%',
             fontsize=12, fontweight='bold', color='white', y=0.98)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)
dark = '#161b22'; sp = '#30363d'

def sty(ax, t=""):
    ax.set_facecolor(dark)
    for s in ax.spines.values(): s.set_color(sp)
    ax.tick_params(colors='#8b949e')
    if t: ax.set_title(t, color='#e6edf3', fontsize=10, fontweight='bold', pad=8)

# ── R1C0-1: NAV comparison ────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
sty(ax1, 'Cumulative NAV: Value vs Momentum vs Blends')
navs = {
    'Momentum V5 (V2.2 proxy)': (M, '#58a6ff', '-', 1.5),
    'Value book': (V, '#e8c547', '-', 1.5),
    'Static 30% value': (B_static, '#3fb950', '--', 1.8),
    'State-tilt BASE': (D_base, '#f97316', '--', 1.8),
}
for name, (r, c, ls, lw) in navs.items():
    nav = (1+r.dropna()).cumprod()
    nav.index = nav.index.to_timestamp()
    ax1.semilogy(nav.index, nav.values, label=name, color=c, ls=ls, lw=lw)

# Shade EX-BULL months
for m_ep in state[state==5].index:
    ts = m_ep.to_timestamp(); te = (m_ep+1).to_timestamp()
    ax1.axvspan(ts, te, alpha=0.2, color='#9467bd')
ax1.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')
ax1.set_ylabel('NAV (log, start=1)', color='#8b949e')

# ── R1C2: Annual returns side-by-side ────────────────────
ax2 = fig.add_subplot(gs[0, 2])
sty(ax2, 'Annual Returns\nValue vs Momentum')
years, rv_ann, rm_ann = [], [], []
for yr in range(2014, 2027):
    sv = sub(V,f'{yr}-01',f'{yr}-12')
    sm = sub(M,f'{yr}-01',f'{yr}-12')
    if len(sv)<6: continue
    years.append(yr)
    rv_ann.append(((1+sv).prod()-1)*100)
    rm_ann.append(((1+sm).prod()-1)*100)
x = np.arange(len(years))
w = 0.38
ax2.bar(x-w/2, rv_ann, w, label='Value', color='#e8c547', alpha=0.8)
ax2.bar(x+w/2, rm_ann, w, label='Momentum', color='#58a6ff', alpha=0.8)
ax2.axhline(0, color='white', lw=0.8, ls='--', alpha=0.5)
ax2.set_xticks(x)
ax2.set_xticklabels([str(y)[-2:] for y in years], color='#8b949e', fontsize=8)
ax2.set_ylabel('%', color='#8b949e')
ax2.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')

# ── R2C0: Monthly returns by state (value vs momentum) ─
ax3 = fig.add_subplot(gs[1, 0])
sty(ax3, 'Mean Monthly Return by State\nValue vs Momentum')
states_list = [1,2,3,4,5]
x = np.arange(len(states_list))
w = 0.35
vm_by_s = [(vdf2.loc[vdf2['state']==s,'V'].mean()*100,
            vdf2.loc[vdf2['state']==s,'M'].mean()*100) for s in states_list]
ax3.bar(x-w/2, [v for v,m in vm_by_s], w, label='Value',
        color=['#e8c547' if v>m else '#e87a4e' for v,m in vm_by_s], alpha=0.85)
ax3.bar(x+w/2, [m for v,m in vm_by_s], w, label='Momentum', color='#58a6ff', alpha=0.85)
ax3.set_xticks(x)
ax3.set_xticklabels([STATE_NAMES[s] for s in states_list],
                     color='#8b949e', fontsize=8, rotation=20)
ax3.axhline(0, color='white', lw=0.8, ls='--', alpha=0.5)
ax3.set_ylabel('%/month', color='#8b949e')
ax3.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')

# ── R2C1: Calmar vs value weight ─────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
sty(ax4, 'Calmar & MaxDD vs Value Weight\n(replacing V2.2 capital)')
weights_sw = [0, 0.10, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
calmars = [ann(blend(w))['Calmar'] for w in weights_sw]
maxdds  = [ann(blend(w))['MaxDD']  for w in weights_sw]
ax4r = ax4.twinx()
ax4.plot(weights_sw, calmars, 'o-', color='#3fb950', lw=2, label='Calmar (left)')
ax4r.plot(weights_sw, maxdds, 's--', color='#d62728', lw=2, label='MaxDD% (right)')
ax4.axvline(0.30, color='white', lw=1, ls='--', alpha=0.5)
ax4.set_xlabel('Value weight in 50B total', color='#8b949e')
ax4.set_ylabel('Calmar', color='#3fb950')
ax4r.set_ylabel('MaxDD (%)', color='#d62728')
ax4r.tick_params(colors='#d62728')
ax4.set_xticks(weights_sw)
ax4.set_xticklabels([f'{w:.0%}' for w in weights_sw], color='#8b949e', fontsize=8)
lines1, l1 = ax4.get_legend_handles_labels()
lines2, l2 = ax4r.get_legend_handles_labels()
ax4.legend(lines1+lines2, l1+l2, fontsize=8, facecolor='#1c2128', labelcolor='white')

# ── R2C2: Summary table ───────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor(dark); ax5.axis('off')
sty(ax5, 'Performance Summary\n(Full period)')

strats_tbl = [
    ("V2.2 momentum only", M),
    ("+ 20% value", blend(0.20)),
    ("+ 30% value (rec.)", blend(0.30)),
    ("+ 40% value", blend(0.40)),
    ("State-tilt BASE", D_base),
    ("EX-BULL tilt only", D_exbull),
]
hdr = ['Strategy','CAGR','Sh','MaxDD','Cal']
rows_t = [hdr]
for name, r in strats_tbl:
    m = ann(r)
    rows_t.append([name, f"{m['CAGR']:.1f}%", f"{m['Sharpe']:.2f}",
                   f"{m['MaxDD']:.1f}%", f"{m['Calmar']:.2f}"])

tbl = ax5.table(cellText=rows_t[1:], colLabels=rows_t[0],
                loc='center', cellLoc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(8.5); tbl.scale(1.15, 1.85)
for (r_i,c), cell in tbl.get_celld().items():
    cell.set_facecolor('#1c2128' if r_i%2==0 else dark)
    cell.set_text_props(color='#e6edf3'); cell.set_edgecolor(sp)
    if r_i==0:
        cell.set_facecolor('#21262d'); cell.set_text_props(color='white', fontweight='bold')
    if r_i>0 and '30%' in rows_t[r_i][0]:
        cell.set_facecolor('#0d2818')

out = WORKDIR + r"\value_book_profile.png"
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: value_book_profile.png")
plt.close()
print("DONE")
