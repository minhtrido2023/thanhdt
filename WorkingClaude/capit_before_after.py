"""
capit_before_after.py — Before/After comparison: old vs new capitulation stock criteria
- Old (base): quality(ROE_Min5Y>=12%,ROIC5Y>=10%,FSCORE>=6) + pb_z < -1 ("golden")
- New: quality gate ONLY as risk filter + composite score:
        40% pb_z + 35% RSI_oversold + 25% 3Y-low proximity
  Plus sector exclusion (ICB 86xx/87xx) + relax RSI threshold 0.30->0.35

Uses ticker_prune profit_3M (T+60) across all CRISIS washout events 2014-2026.
"""
import sys, os
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass
import subprocess, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from io import StringIO
import warnings; warnings.filterwarnings('ignore')

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
BQ_PATH = r"bq"
os.chdir(WORKDIR)

def bq(sql, label=""):
    if label: print(f"  > {label}...", end=" ", flush=True)
    cmd = (f'"{BQ_PATH}" query --use_legacy_sql=false'
           f' --project_id={PROJECT} --format=csv --quiet --max_rows=500000')
    r = subprocess.run(cmd, input=sql, capture_output=True,
                       text=True, encoding='utf-8', shell=True)
    df = pd.read_csv(StringIO(r.stdout)) if r.returncode==0 and r.stdout.strip() else pd.DataFrame()
    if label: print(f"OK ({len(df):,} rows)")
    return df

# ── Pull all CRISIS-event data from ticker_prune ─────────────────────
# Using WASHOUT events: % above MA200 <= 30% (playbook v2)
PULL = """
WITH
crisis_dates AS (
  SELECT s.time FROM tav2_bq.vnindex_5state_dt5g_live s WHERE s.state = 1
),
breadth AS (
  SELECT t.time,
    SAFE_DIVIDE(COUNTIF(t.Close > t.MA200), COUNT(*)) AS above_ma200_pct,
    SAFE_DIVIDE(COUNTIF(t.D_RSI < 0.30),  COUNT(*)) AS panic_breadth
  FROM tav2_bq.ticker_prune t
  INNER JOIN crisis_dates c ON t.time = c.time
  WHERE t.MA200 IS NOT NULL AND t.Trading_Value_1M_P50 >= 5e9
  GROUP BY t.time
),
-- Identify distinct washout ENTRY DATES (first day breadth dips <=30%)
washout_entries AS (
  SELECT b.time,
    LAG(b.above_ma200_pct) OVER (ORDER BY b.time) AS prev_breadth
  FROM breadth b
  WHERE b.above_ma200_pct <= 0.30
),
-- For multi-day washouts, only use first day of each episode to avoid overlap
entries_dedupe AS (
  SELECT time FROM washout_entries
  WHERE prev_breadth IS NULL OR prev_breadth > 0.30   -- first day of episode
),
-- Also keep any CRISIS day with high panic (legacy threshold) not already in washout
-- to include the full CRISIS+panic range from playbook
all_entries AS (
  SELECT DISTINCT b.time, b.above_ma200_pct, b.panic_breadth
  FROM breadth b
  WHERE b.above_ma200_pct <= 0.35   -- slightly wider gate for full analysis
    AND b.time IN (SELECT time FROM crisis_dates)
),
-- Sample: first trading day of each month within CRISIS+washout to reduce overlap
monthly_entry AS (
  SELECT DATE_TRUNC(e.time, MONTH) AS month, MIN(e.time) AS entry_date
  FROM all_entries e
  GROUP BY 1
),
features AS (
  SELECT
    t.time,
    t.ticker,
    t.ICB_Code,
    -- Outcome: T+60
    t.profit_3M / 100.0                                          AS fwd60d,
    -- Valuation
    SAFE_DIVIDE(t.PB - t.PB_MA5Y, t.PB_SD5Y)                   AS pb_z,
    t.PB,
    t.PE,
    -- Technical
    t.D_RSI,
    t.C_L1M,
    t.PC_6M,
    -- 3Y low proximity
    t.ID_LO_3Y,
    -- Quality
    t.ROE_Min5Y,
    t.ROIC5Y,
    t.FSCORE,
    -- Breadth context
    b.above_ma200_pct,
    b.panic_breadth,
    t.Trading_Value_1M_P50 / 1e9 AS liq_B
  FROM tav2_bq.ticker_prune t
  INNER JOIN monthly_entry m ON t.time = m.entry_date
  INNER JOIN breadth b ON t.time = b.time
  WHERE t.profit_3M IS NOT NULL
    AND t.Trading_Value_1M_P50 >= 10e9
    AND t.PB  > 0  AND t.PB < 20
    AND t.PE  > 0  AND t.PE < 100
    AND t.PB_MA5Y IS NOT NULL AND t.PB_SD5Y > 0
    AND t.D_RSI IS NOT NULL AND t.C_L1M IS NOT NULL
    AND t.ICB_Code IS NOT NULL
)
SELECT * FROM features ORDER BY time, ticker
"""

df = bq(PULL, "CRISIS washout events (monthly, first entry day)")
df['time'] = pd.to_datetime(df['time'])
# ICB first 2 digits for sector exclusion
df['icb2'] = df['ICB_Code'].fillna(0).astype(int) // 10

print(f"\n  Events: {df['time'].nunique()} months | {len(df):,} stock-days | "
      f"{df['ticker'].nunique()} tickers")
print(f"  Date range: {df['time'].min().date()} -> {df['time'].max().date()}")

# ── Normalize helpers ────────────────────────────────────────────────
def norm_series(s, invert=False):
    mn, mx = s.min(), s.max()
    if mx == mn: return pd.Series(0.5, index=s.index)
    v = (s - mn) / (mx - mn)
    return 1-v if invert else v

# ── Per-event scoring function ───────────────────────────────────────
N_PICK = 5   # picks per event

def pick_event(g, method):
    """Given group g (one date), apply scoring method, return top N_PICK tickers."""
    g = g.copy()
    # Sector exclusion (BDS 86xx/87xx -> icb2 in [86,87])
    if 'exclude_sector' in method:
        g = g[~g['icb2'].isin([86, 87, 33])]
    if len(g) < 2: return pd.Series(dtype=float)

    if method['name'] == 'old':
        # OLD: quality (strict) + golden (pb_z < -1)
        # If no golden, relax to cheapest by pb_z
        g['qual_old'] = (g['ROE_Min5Y'] >= 0.12) & (g['ROIC5Y'] >= 0.10) & (g['FSCORE'] >= 6)
        cands = g[g['qual_old'] & (g['pb_z'] < -1)]
        if len(cands) == 0:
            cands = g[g['qual_old']].nsmallest(N_PICK, 'pb_z')
        if len(cands) == 0:
            cands = g.nsmallest(N_PICK, 'pb_z')
        picks = cands.nsmallest(N_PICK, 'pb_z')

    elif method['name'] == 'new':
        # NEW: quality gate (relaxed) + composite score
        g['qual_new'] = (g['ROIC5Y'] >= 0.08) & (g['FSCORE'] >= 5) & (g['ROE_Min5Y'] >= 0.08)
        cands = g[g['qual_new']]
        if len(cands) < 3: cands = g  # fallback if too few quality stocks
        # Composite score: 40% pb_z + 35% RSI + 25% 3Y-low proximity
        c = cands.copy()
        c['s_pbz']  = norm_series(c['pb_z'], invert=True)
        c['s_rsi']  = norm_series(c['D_RSI'], invert=True)
        c['s_lo3y'] = norm_series(c['ID_LO_3Y'], invert=True)
        c['score']  = (0.40*c['s_pbz'] + 0.35*c['s_rsi'] + 0.25*c['s_lo3y'])
        picks = c.nlargest(N_PICK, 'score')

    elif method['name'] == 'pbz_only':
        g['qual_new'] = (g['ROIC5Y'] >= 0.08) & (g['FSCORE'] >= 5) & (g['ROE_Min5Y'] >= 0.08)
        cands = g[g['qual_new']]
        if len(cands) < 3: cands = g
        picks = cands.nsmallest(N_PICK, 'pb_z')

    elif method['name'] == 'rsi_only':
        g['qual_new'] = (g['ROIC5Y'] >= 0.08) & (g['FSCORE'] >= 5) & (g['ROE_Min5Y'] >= 0.08)
        cands = g[g['qual_new']]
        if len(cands) < 3: cands = g
        picks = cands.nsmallest(N_PICK, 'D_RSI')

    else:
        picks = g.nsmallest(N_PICK, 'pb_z')

    return picks['fwd60d']

# ── Run all methods across all events ────────────────────────────────
METHODS = [
    {'name': 'old',      'label': 'OLD: strict quality + pb_z<-1 (golden)'},
    {'name': 'pbz_only', 'label': 'BASE: relaxed quality + pb_z only', 'exclude_sector': True},
    {'name': 'rsi_only', 'label': 'RSI only: relaxed quality + D_RSI', 'exclude_sector': True},
    {'name': 'new',      'label': 'NEW: 40%pbz+35%RSI+25%3Ylow + sector excl', 'exclude_sector': True},
]

event_results = {}  # method_name -> list of (time, mean_ret, n_picks, tickers)

for method in METHODS:
    rows = []
    for dt, g in df.groupby('time'):
        picks_ret = pick_event(g, method)
        if len(picks_ret) == 0: continue
        rows.append({
            'time': dt,
            'ret': picks_ret.mean(),
            'n': len(picks_ret),
            'median': picks_ret.median(),
            'p10': picks_ret.quantile(0.10),
        })
    event_results[method['name']] = pd.DataFrame(rows).set_index('time')

# ── Print comparison table ────────────────────────────────────────────
print("\n" + "="*70)
print("BEFORE vs AFTER — Event-level comparison (each CRISIS washout month)")
print("="*70)

def stats(r):
    if r.empty: return {}
    return {
        'n_ev': len(r),
        'med':  r['median'].median()*100,
        'mean': r['ret'].mean()*100,
        'win':  (r['ret']>0).mean()*100,
        'p10':  r['p10'].median()*100,
    }

print(f"\n  {'Strategy':45s}  {'n_ev':>5}  {'Med/ev':>7}  {'Mean/ev':>7}  {'Win%':>6}  {'P10':>7}")
print("  " + "-"*80)
for method in METHODS:
    s = stats(event_results[method['name']])
    if not s: continue
    marker = ""
    if method['name'] == 'old': marker = "  <- current"
    elif method['name'] == 'new': marker = "  <- PROPOSED"
    print(f"  {method['label']:45s}  {s['n_ev']:5d}  "
          f"{s['med']:+6.1f}%  {s['mean']:+6.1f}%  {s['win']:5.0f}%  {s['p10']:+6.1f}%{marker}")

# ── Per-event delta: new - old ─────────────────────────────────────────
old_r = event_results['old']
new_r = event_results['new']
common = old_r.index.intersection(new_r.index)
diff = new_r.loc[common, 'ret'] - old_r.loc[common, 'ret']
print(f"\n  Delta NEW - OLD ({len(common)} matched events):")
print(f"    Mean delta: {diff.mean()*100:+.2f}%/event")
print(f"    Positive events: {(diff>0).sum()}/{len(diff)} ({(diff>0).mean()*100:.0f}%)")
print(f"    Events where NEW > OLD by >2%: {(diff>0.02).sum()}")
print(f"    Events where OLD > NEW by >2%: {(diff<-0.02).sum()}")

# ── Annual breakdown ──────────────────────────────────────────────────
print("\n  Annual breakdown:")
print(f"  {'Year':6s}  {'OLD':>8s}  {'BASE':>8s}  {'RSI':>8s}  {'NEW':>8s}  {'Delta':>8s}  n_events")
print("  " + "-"*65)
all_years = sorted(set(df['time'].dt.year.unique()))
for yr in all_years:
    row_parts = [f"  {yr}"]
    for mn in ['old', 'pbz_only', 'rsi_only', 'new']:
        r = event_results[mn]
        yr_r = r[r.index.year == yr]['ret']
        if len(yr_r) == 0:
            row_parts.append("     n/a")
        else:
            row_parts.append(f"  {yr_r.mean()*100:+6.1f}%")
    # delta
    old_yr = event_results['old'][event_results['old'].index.year==yr]['ret']
    new_yr = event_results['new'][event_results['new'].index.year==yr]['ret']
    idx_c = old_yr.index.intersection(new_yr.index)
    if len(idx_c):
        d = (new_yr.loc[idx_c].mean() - old_yr.loc[idx_c].mean())*100
        row_parts.append(f"  {d:+6.1f}%")
    else:
        row_parts.append("     n/a")
    n_ev = len(event_results['old'][event_results['old'].index.year==yr])
    row_parts.append(f"  n={n_ev}")
    print("".join(row_parts))

# ── Qualitative overlap analysis ──────────────────────────────────────
print("\n" + "="*70)
print("STOCK OVERLAP: how many picks are SHARED old vs new?")
print("="*70)

shared_counts, old_unique, new_unique = [], [], []
for dt, g in df.groupby('time'):
    old_p = pick_event(g, {'name':'old'})
    new_m = {'name':'new','exclude_sector':True}
    g_exc = g[~g['icb2'].isin([86,87,33])].copy()
    if len(g_exc) >= 2:
        g_exc['qual_new'] = (g_exc['ROIC5Y']>=0.08)&(g_exc['FSCORE']>=5)&(g_exc['ROE_Min5Y']>=0.08)
        cands = g_exc[g_exc['qual_new']]
        if len(cands)<3: cands = g_exc
        c = cands.copy()
        c['s_pbz']  = norm_series(c['pb_z'],   invert=True)
        c['s_rsi']  = norm_series(c['D_RSI'],   invert=True)
        c['s_lo3y'] = norm_series(c['ID_LO_3Y'],invert=True)
        c['score']  = 0.40*c['s_pbz']+0.35*c['s_rsi']+0.25*c['s_lo3y']
        new_p_tkr = set(c.nlargest(N_PICK,'score')['ticker'])
    else:
        new_p_tkr = set()
    old_p_tkr = set(old_p.index) if hasattr(old_p,'index') and not old_p.empty else set()
    if len(old_p_tkr)==0 and len(new_p_tkr)==0: continue
    shared_counts.append(len(old_p_tkr & new_p_tkr))
    old_unique.append(len(old_p_tkr - new_p_tkr))
    new_unique.append(len(new_p_tkr - old_p_tkr))

if shared_counts:
    print(f"  Avg shared picks per event: {np.mean(shared_counts):.1f}/{N_PICK}")
    print(f"  Avg OLD-unique (dropped by new): {np.mean(old_unique):.1f}")
    print(f"  Avg NEW-unique (added by new): {np.mean(new_unique):.1f}")
    print(f"  -> NEW replaces {np.mean(new_unique):.1f}/{N_PICK} picks on average")

# ── NEW: what RSI threshold for "oversold"? ───────────────────────────
print("\n" + "="*70)
print("RSI THRESHOLD CALIBRATION (within quality-gated CRISIS washout universe)")
print("="*70)
df_q = df[(df['ROIC5Y']>=0.08)&(df['FSCORE']>=5)&(df['ROE_Min5Y']>=0.08)]
for thr in [0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60]:
    sub = df_q[df_q['D_RSI'] <= thr]
    if len(sub) < 20: continue
    med = sub['fwd60d'].median()*100
    win = (sub['fwd60d']>0).mean()*100
    n   = len(sub)
    print(f"  D_RSI <= {thr:.2f}: n={n:4d}  med {med:+5.1f}%  win {win:4.0f}%")

# ── FIGURE ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 12))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('Capitulation Stock Selection: Before vs After Optimization\n'
             'CRISIS washout events (monthly), profit_3M = T+60, quality gate applied',
             fontsize=12, fontweight='bold', color='white', y=0.99)
dark = '#161b22'; sp = '#30363d'
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)

def sty(ax, t=""):
    ax.set_facecolor(dark); [s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e', labelsize=9)
    if t: ax.set_title(t, color='#e6edf3', fontsize=10, fontweight='bold', pad=7)

# ── R1C0: Event-by-event return scatter ───────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
sty(ax1, 'Event Returns: OLD vs NEW\n(each dot = 1 CRISIS washout month)')
old_vals = old_r.loc[common, 'ret']*100
new_vals = new_r.loc[common, 'ret']*100
colors_s = ['#3fb950' if n>o else '#d62728'
            for n,o in zip(new_vals, old_vals)]
ax1.scatter(old_vals, new_vals, c=colors_s, alpha=0.7, s=40)
lim = max(abs(old_vals).max(), abs(new_vals).max())*1.1
ax1.plot([-lim,lim],[-lim,lim],'--', color='white', lw=0.8, alpha=0.4)
ax1.axhline(0, color='#8b949e', lw=0.8, alpha=0.5)
ax1.axvline(0, color='#8b949e', lw=0.8, alpha=0.5)
ax1.set_xlabel('OLD return %', color='#8b949e')
ax1.set_ylabel('NEW return %', color='#8b949e')
ax1.set_xlim(-lim, lim); ax1.set_ylim(-lim, lim)

# ── R1C1: Distribution comparison ─────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
sty(ax2, 'Return Distribution per Event')
for mn, col, lbl in [('old','#d62728','OLD (strict)'),
                      ('new','#3fb950','NEW (composite)')]:
    r = event_results[mn]['ret']*100
    ax2.hist(r, bins=20, alpha=0.6, color=col, label=lbl)
    ax2.axvline(r.median(), color=col, lw=2, ls='--',
                label=f'{lbl} med={r.median():.1f}%')
ax2.set_xlabel('Return %/event', color='#8b949e')
ax2.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')

# ── R1C2: Annual bar chart ─────────────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
sty(ax3, 'Annual Average Return per Event')
years = [y for y in all_years
         if len(event_results['old'][event_results['old'].index.year==y])>0]
x = np.arange(len(years)); w = 0.35
old_ann = [event_results['old'][event_results['old'].index.year==y]['ret'].mean()*100
           for y in years]
new_ann = [event_results['new'][event_results['new'].index.year==y]['ret'].mean()*100
           for y in years]
ax3.bar(x-w/2, old_ann, w, label='OLD', color='#d62728', alpha=0.7)
ax3.bar(x+w/2, new_ann, w, label='NEW', color='#3fb950', alpha=0.7)
ax3.axhline(0, color='white', lw=0.8, alpha=0.5)
ax3.set_xticks(x)
ax3.set_xticklabels([str(y)[-2:] for y in years], color='#8b949e')
ax3.set_ylabel('%', color='#8b949e')
ax3.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')

# ── R2C0: RSI threshold calibration ───────────────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
sty(ax4, 'RSI Threshold: n stocks vs bounce quality')
thresholds = [0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60]
meds_t, wins_t, ns_t = [], [], []
for thr in thresholds:
    sub = df_q[df_q['D_RSI'] <= thr]
    meds_t.append(sub['fwd60d'].median()*100 if len(sub)>10 else np.nan)
    wins_t.append((sub['fwd60d']>0).mean()*100 if len(sub)>10 else np.nan)
    ns_t.append(len(sub))
ax4.bar(range(len(thresholds)), meds_t, color=['#3fb950' if m and m>5 else '#e8c547'
                                                for m in meds_t], alpha=0.8)
ax4.axhline(0, color='white', lw=0.8, alpha=0.5)
ax4.set_xticks(range(len(thresholds)))
ax4.set_xticklabels([f'<={t:.2f}' for t in thresholds],
                    rotation=25, ha='right', color='#8b949e', fontsize=8)
ax4.set_ylabel('Median bounce %', color='#8b949e')
ax4r = ax4.twinx()
ax4r.plot(range(len(thresholds)), ns_t, 'o--', color='#58a6ff', lw=1.5)
ax4r.set_ylabel('n obs', color='#58a6ff', fontsize=8)
ax4r.tick_params(colors='#58a6ff')

# ── R2C1: Summary stats table ──────────────────────────────────────────
ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor(dark); ax5.axis('off')
sty(ax5, 'Strategy Comparison Summary')
rows_t = [['Strategy', 'Med/ev', 'Win%', 'P10', 'n']]
for method in METHODS:
    s = stats(event_results[method['name']])
    if not s: continue
    rows_t.append([method['label'][:30],
                   f"{s['med']:+.1f}%", f"{s['win']:.0f}%",
                   f"{s['p10']:+.1f}%", str(s['n_ev'])])
tbl = ax5.table(cellText=rows_t[1:], colLabels=rows_t[0],
                loc='center', cellLoc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(8); tbl.scale(1.1, 2.2)
for (ri, ci), cell in tbl.get_celld().items():
    cell.set_facecolor('#1c2128' if ri%2==0 else dark)
    cell.set_text_props(color='#e6edf3'); cell.set_edgecolor(sp)
    if ri == 0:
        cell.set_facecolor('#21262d')
        cell.set_text_props(color='white', fontweight='bold')
    if ri > 0 and 'NEW' in rows_t[ri][0]:
        cell.set_facecolor('#0d2e14')

# ── R2C2: Feature importance bar ──────────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
sty(ax6, 'Feature Importance (Directional IC)\nin CRISIS Washout Events')
feats_ic = [
    ('pb_z',  '#e8c547', 0.398),
    ('D_RSI', '#58a6ff', 0.382),
    ('PC_6M', '#3fb950', 0.218),
    ('D_CMB', '#f97316', 0.203),
    ('ID_LO_3Y','#9467bd', 0.200),
    ('C_L1M', '#17becf', 0.174),
    ('PB raw','#aaaaaa', 0.223),
    ('Pattern','#d62728',-0.298),
]
names_ic = [f[0] for f in feats_ic]
vals_ic  = [f[2] for f in feats_ic]
cols_ic  = [f[1] for f in feats_ic]
y_pos = range(len(names_ic))
ax6.barh(y_pos, vals_ic, color=cols_ic, alpha=0.85)
ax6.axvline(0, color='white', lw=0.8, alpha=0.5)
ax6.set_yticks(y_pos)
ax6.set_yticklabels(names_ic, color='#8b949e', fontsize=9)
ax6.set_xlabel('Directional IC (washout)', color='#8b949e')
ax6.text(0.25, 6.8, 'NEW criteria', color='#3fb950', fontsize=9,
         bbox=dict(boxstyle='round', fc='#0d2e14', ec='#3fb950', alpha=0.8))

out = WORKDIR + r"\capit_before_after.png"
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: capit_before_after.png")
plt.close()
print("DONE")
