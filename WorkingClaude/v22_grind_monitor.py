"""
v22_grind_monitor.py — Is V2.2+capit declining since 2025? + grind-window lens
==============================================================================
Uses the REAL momentum leg NAVs (BAL_cap + LAG_cap, daily to latest) to map the
current drawdown/grind precisely, and checks whether it is STYLE-DIVERGENCE
(book bleeds while VNINDEX is flat/up) vs a real market drawdown. Overlays
Book C (monthly, to its data cutoff) to show what the value sleeve would have
added in the grind.
"""
import sys, os, subprocess
from io import StringIO
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings; warnings.filterwarnings('ignore')

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
BQ_PATH = r"bq"
PROJECT = "lithe-record-440915-m9"

def bq(sql):
    cmd = (f'"{BQ_PATH}" query --use_legacy_sql=false --project_id={PROJECT}'
           f' --format=csv --quiet --max_rows=500000')
    r = subprocess.run(cmd, input=sql, capture_output=True, text=True, encoding="utf-8", shell=True)
    return pd.read_csv(StringIO(r.stdout)) if r.returncode == 0 and r.stdout.strip() else pd.DataFrame()

def load(f):
    return pd.read_csv(f'data/{f}.csv', parse_dates=['time']).set_index('time')['nav']

bal = load('pt_v22_bal_v21_cap')
lag = load('pt_v22_lag_v21_cap')
idx = bal.index.intersection(lag.index)
mom = (bal.reindex(idx) + lag.reindex(idx))        # V2.2 momentum (sum/drift), daily

# VNINDEX over same window
vni = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX'
AND t.time BETWEEN DATE '{idx.min().date()}' AND DATE '{idx.max().date()}' ORDER BY t.time""")
vni["time"] = pd.to_datetime(vni["time"]); vni = vni.set_index("time")["Close"].reindex(idx, method="ffill")

print("=" * 74)
print("V2.2 (momentum + capit) — DRAWDOWN / GRIND MAP")
print(f"data: {idx.min().date()} -> {idx.max().date()}")
print("=" * 74)

# ---- current drawdown / grind window ---------------------------------------
peak_val = mom.cummax()
cur_dd = (mom.iloc[-1] / peak_val.iloc[-1] - 1) * 100
peak_date = mom.idxmax()
since_peak = mom[mom.index >= peak_date]
grind_days = (idx.max() - peak_date).days
print(f"\n  All-time-high: {mom.max()/1e9:.2f}B on {peak_date.date()}")
print(f"  Current NAV:   {mom.iloc[-1]/1e9:.2f}B  ({idx.max().date()})")
print(f"  Current drawdown from peak: {cur_dd:+.1f}%   |   underwater {grind_days} days")

# ---- monthly returns 2024-12 -> now ----------------------------------------
def monthly(nav):
    m = nav.resample('ME').last().pct_change()
    m.index = m.index.to_period('M'); return m
mom_m = monthly(mom); vni_m = monthly(vni)
bal_m = monthly(bal.reindex(idx)); lag_m = monthly(lag.reindex(idx))

print(f"\n  Monthly returns (2025-01 -> now):")
print(f"  {'Month':9s}  {'BAL':>7s}  {'LAG':>7s}  {'V2.2mom':>8s}  {'VNINDEX':>8s}  {'spread':>7s}")
print("  " + "-"*56)
for m in mom_m.index:
    if m < pd.Period('2025-01'): continue
    sp = (mom_m[m] - vni_m.get(m, np.nan)) * 100
    print(f"  {str(m):9s}  {bal_m.get(m,np.nan)*100:+6.1f}%  {lag_m.get(m,np.nan)*100:+6.1f}%  "
          f"{mom_m[m]*100:+7.1f}%  {vni_m.get(m,np.nan)*100:+7.1f}%  {sp:+6.1f}%")

# ---- grind window stats: peak -> now ---------------------------------------
g_mom = (mom.iloc[-1] / mom.loc[peak_date] - 1) * 100
g_vni = (vni.iloc[-1] / vni.loc[peak_date] - 1) * 100
print(f"\n  GRIND (peak {peak_date.date()} -> now, {grind_days}d):")
print(f"    V2.2 momentum : {g_mom:+.1f}%")
print(f"    VNINDEX       : {g_vni:+.1f}%")
diag = ("STYLE-DIVERGENCE (book bleeds while index holds/up — value sleeve helps)"
        if g_vni > g_mom + 3 else
        "MARKET drawdown (index also down — beta, not style)")
print(f"    -> {diag}")

# trailing windows
def trail(nav, days):
    if len(nav) < days + 1: return np.nan
    return (nav.iloc[-1] / nav.iloc[-1-days] - 1) * 100
print(f"\n  Trailing returns (V2.2 momentum):")
for lbl, d in [('1M (~21d)', 21), ('3M (~63d)', 63), ('6M (~126d)', 126), ('12M (~252d)', 252)]:
    print(f"    {lbl:12s}: {trail(mom, d):+6.1f}%")

# ---- 2025 calendar vs grind decomposition ----------------------------------
def yr_ret(nav, y):
    s = nav[nav.index.year == y]
    return (s.iloc[-1]/s.iloc[0]-1)*100 if len(s) > 1 else np.nan
print(f"\n  Calendar decomposition (the question 'declining since 2025?'):")
print(f"    2025 full year : V2.2 mom {yr_ret(mom,2025):+.1f}%  |  VNI {yr_ret(vni,2025):+.1f}%")
print(f"    2026 YTD       : V2.2 mom {yr_ret(mom,2026):+.1f}%  |  VNI {yr_ret(vni,2026):+.1f}%")
# H1 vs H2 2025
h1 = mom[(mom.index>='2025-01-01')&(mom.index<'2025-07-01')]
h2 = mom[(mom.index>='2025-07-01')&(mom.index<'2026-01-01')]
print(f"    2025 H1        : {(h1.iloc[-1]/h1.iloc[0]-1)*100:+.1f}%")
print(f"    2025 H2        : {(h2.iloc[-1]/h2.iloc[0]-1)*100:+.1f}%  (grind onset)")

# ---- Book C overlay in the grind (where data available) --------------------
print(f"\n  Book C in the grind window (data to its cutoff):")
try:
    vc = pd.read_csv('data/book_c_backtest.csv')
    vc['time'] = pd.PeriodIndex(vc['time'], freq='M')
    val_m = vc.set_index('time')['ret_gated_eq']
    # common grind months from peak month onward
    peak_m = pd.Period(peak_date, 'M')
    gm = [m for m in mom_m.index if m >= peak_m and m in val_m.index]
    if gm:
        mom_g = (1 + mom_m.reindex(gm)).prod() - 1
        val_g = (1 + val_m.reindex(gm)).prod() - 1
        # 35/35/30 blend over those months (simple, no band — short window)
        rb = bal_m.reindex(gm); rl = lag_m.reindex(gm); rv = val_m.reindex(gm)
        blend_g = (1 + 0.35*rb + 0.35*rl + 0.30*rv).prod() - 1
        print(f"    window {gm[0]}..{gm[-1]} ({len(gm)} mo, Book C data ends "
              f"{val_m.index.max()}):")
        print(f"    V2.2 momentum : {mom_g*100:+.1f}%")
        print(f"    Book C alone  : {val_g*100:+.1f}%")
        print(f"    V2.2 + C 35/35/30: {blend_g*100:+.1f}%   (delta {(blend_g-mom_g)*100:+.1f}pp)")
    else:
        print("    (no overlapping months — Book C data ends before grind)")
except Exception as ex:
    print(f"    (Book C overlay unavailable: {ex})")

# ============================================================================
# FIGURE
# ============================================================================
fig = plt.figure(figsize=(18, 9)); fig.patch.set_facecolor('#0d1117')
fig.suptitle('V2.2 (momentum + capit) — Grind Monitor\n'
             f'Current drawdown {cur_dd:+.1f}% from {peak_date.date()} peak ({grind_days}d underwater)',
             fontsize=12, color='white', fontweight='bold', y=0.99)
dark='#161b22'; sp='#30363d'
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.34)
def sty(ax, t=""):
    ax.set_facecolor(dark); [s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e', labelsize=8)
    if t: ax.set_title(t, color='#e6edf3', fontsize=10, fontweight='bold', pad=6)

# R1 span2: NAV 2024+ with peak + grind shading
ax1 = fig.add_subplot(gs[0, :2]); sty(ax1, 'V2.2 momentum NAV vs VNINDEX (rebased) — 2024+')
m24 = mom[mom.index >= '2024-01-01']; v24 = vni[vni.index >= '2024-01-01']
ax1.plot(m24.index, m24.values/m24.iloc[0], color='#58a6ff', lw=1.8, label='V2.2 momentum')
ax1.plot(v24.index, v24.values/v24.iloc[0], color='#d62728', lw=1.3, label='VNINDEX')
if peak_date >= pd.Timestamp('2024-01-01'):
    ax1.axvspan(peak_date, idx.max(), color='#e8c547', alpha=0.12, label='grind window')
    ax1.axvline(peak_date, color='#e8c547', lw=1, ls='--')
ax1.legend(fontsize=9, facecolor='#1c2128', labelcolor='white'); ax1.set_ylabel('rebased', color='#8b949e')

# R1C2: drawdown
ax2 = fig.add_subplot(gs[0, 2]); sty(ax2, 'V2.2 momentum drawdown')
dd = (mom/mom.cummax()-1)*100; dd24 = dd[dd.index >= '2024-01-01']
ax2.fill_between(dd24.index, dd24.values, 0, color='#58a6ff', alpha=0.45)
ax2.axhline(cur_dd, color='#d62728', lw=1, ls='--', label=f'now {cur_dd:+.1f}%')
ax2.legend(fontsize=8, facecolor='#1c2128', labelcolor='white'); ax2.set_ylabel('DD %', color='#8b949e')

# R2C0: monthly bars 2025+
ax3 = fig.add_subplot(gs[1, 0]); sty(ax3, 'Monthly: V2.2 mom vs VNINDEX (2025+)')
ms = [m for m in mom_m.index if m >= pd.Period('2025-01')]
x = np.arange(len(ms)); w = 0.4
ax3.bar(x-w/2, [mom_m[m]*100 for m in ms], w, color='#58a6ff', alpha=0.85, label='V2.2 mom')
ax3.bar(x+w/2, [vni_m.get(m,np.nan)*100 for m in ms], w, color='#d62728', alpha=0.7, label='VNI')
ax3.axhline(0, color='white', lw=0.8, alpha=0.5)
ax3.set_xticks(x); ax3.set_xticklabels([str(m)[2:] for m in ms], rotation=45, ha='right', color='#8b949e', fontsize=7)
ax3.legend(fontsize=8, facecolor='#1c2128', labelcolor='white'); ax3.set_ylabel('%', color='#8b949e')

# R2C1: trailing returns
ax4 = fig.add_subplot(gs[1, 1]); sty(ax4, 'Trailing returns — V2.2 momentum')
tw = [('1M',21),('3M',63),('6M',126),('12M',252)]
tv = [trail(mom,d) for _,d in tw]
cols = ['#3fb950' if v>0 else '#d62728' for v in tv]
ax4.bar([l for l,_ in tw], tv, color=cols, alpha=0.85)
for i,v in enumerate(tv): ax4.text(i, v+(0.5 if v>=0 else -1.5), f'{v:+.1f}', ha='center', color='white', fontsize=8)
ax4.axhline(0, color='white', lw=0.8, alpha=0.5); ax4.set_ylabel('%', color='#8b949e')

# R2C2: calendar decomposition text
ax5 = fig.add_subplot(gs[1, 2]); ax5.set_facecolor(dark); ax5.axis('off'); sty(ax5, 'Declining since 2025?')
txt = [
    f"2025 H1:   {(h1.iloc[-1]/h1.iloc[0]-1)*100:+.1f}%   (strong)",
    f"2025 H2:   {(h2.iloc[-1]/h2.iloc[0]-1)*100:+.1f}%   (grind onset)",
    f"2026 YTD:  {yr_ret(mom,2026):+.1f}%",
    "",
    f"Peak: {peak_date.date()}",
    f"Now DD: {cur_dd:+.1f}% ({grind_days}d)",
    "",
    f"Grind: V2.2 {g_mom:+.1f}% vs VNI {g_vni:+.1f}%",
    f"-> {'STYLE-DIVERGENCE' if g_vni > g_mom+3 else 'market beta'}",
]
ax5.text(0.05, 0.95, "\n".join(txt), transform=ax5.transAxes, va='top', ha='left',
         color='#e6edf3', fontsize=10, family='monospace')

fig.savefig(WORKDIR+r"\v22_grind_monitor.png", dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: v22_grind_monitor.png")
plt.close(); print("DONE")
