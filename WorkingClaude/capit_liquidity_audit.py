"""
capit_liquidity_audit.py — Capacity audit for capitulation stock selection
===========================================================================
Q: "Đủ mã để deploy hết vốn không?"

Analyzes per CRISIS washout event:
  - How many quality+golden candidates available?
  - Total tradable capacity (ADV-constrained)?
  - Fill rate at various capital levels (5B / 10B / 15B / 20B / 30B)?
  - What criteria tier opens enough capacity?
  - Position sizing rule: max 30% daily ADV per stock per day → 3-day fill = 90% ADV
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

# Position sizing: max deployable per stock = ADV_FRAC × daily_liq over RAMP_DAYS
ADV_FRAC  = 0.30   # 30% of daily ADV per day
RAMP_DAYS = 3      # 3-day ramp
MAX_FILL_PER_STOCK = ADV_FRAC * RAMP_DAYS   # = 0.9× daily ADV
NAME_CAP_FRAC = 0.25   # max 25% of total deployment per single name

SECTOR_EXCL = {86, 87, 33}   # BDS, securities, mining

CAPITAL_LEVELS = [5, 10, 15, 20, 30, 50]   # billion VND

def bq(sql, label=""):
    if label: print(f"  > {label}...", end=" ", flush=True)
    cmd = (f'"{BQ_PATH}" query --use_legacy_sql=false'
           f' --project_id={PROJECT} --format=csv --quiet --max_rows=500000')
    r = subprocess.run(cmd, input=sql, capture_output=True,
                       text=True, encoding='utf-8', shell=True)
    df = pd.read_csv(StringIO(r.stdout)) if r.returncode==0 and r.stdout.strip() else pd.DataFrame()
    if label: print(f"OK ({len(df):,} rows)")
    return df

# ── Pull all CRISIS+washout events with full candidate info ───────────
SQL = """
WITH
crisis_dates AS (
  SELECT s.time FROM tav2_bq.vnindex_5state_dt5g_live s WHERE s.state = 1
),
breadth AS (
  SELECT t.time,
    SAFE_DIVIDE(COUNTIF(t.Close > t.MA200), COUNT(*)) AS above_ma200_pct,
    SAFE_DIVIDE(COUNTIF(t.D_RSI < 0.30),   COUNT(*)) AS panic_pct
  FROM tav2_bq.ticker_prune t INNER JOIN crisis_dates c ON t.time = c.time
  WHERE t.MA200 IS NOT NULL AND t.Trading_Value_1M_P50 >= 2e9
  GROUP BY t.time
),
-- Only STRONG washout days: above_MA200 <= 30%
washout_days AS (
  SELECT b.time, b.above_ma200_pct, b.panic_pct
  FROM breadth b WHERE b.above_ma200_pct <= 0.30
),
-- Monthly first entry
monthly_first AS (
  SELECT DATE_TRUNC(w.time, MONTH) AS month, MIN(w.time) AS entry_date
  FROM washout_days w GROUP BY 1
),
-- All stocks on those entry dates with features + outcome
candidates AS (
  SELECT
    t.time,
    t.ticker,
    t.ICB_Code,
    t.Close,
    t.D_RSI,
    SAFE_DIVIDE(t.PB - t.PB_MA5Y, t.PB_SD5Y)  AS pb_z,
    t.PB,
    t.ROE_Min5Y,
    t.ROIC5Y,
    t.FSCORE,
    t.ID_LO_3Y,
    t.Trading_Value_1M_P50 / 1e9               AS liq_B,
    t.profit_3M / 100.0                         AS fwd60d,
    w.above_ma200_pct,
    w.panic_pct
  FROM tav2_bq.ticker_prune t
  INNER JOIN monthly_first m ON t.time = m.entry_date
  INNER JOIN washout_days  w ON t.time = w.time
  WHERE t.Trading_Value_1M_P50 >= 1e9   -- minimal liq filter (1B/day baseline)
    AND t.PB > 0 AND t.PB_MA5Y IS NOT NULL AND t.PB_SD5Y > 0
    AND t.D_RSI IS NOT NULL
)
SELECT * FROM candidates ORDER BY time, liq_B DESC
"""

df = bq(SQL, "CRISIS washout events + candidate pool")
if df.empty: print("ERROR: empty"); import sys; sys.exit(1)
df['time'] = pd.to_datetime(df['time'])
df['icb2'] = df['ICB_Code'].fillna(0).astype(float).astype(int) // 10
df['sector_ok'] = ~df['icb2'].isin(SECTOR_EXCL)

print(f"\n  Events: {df['time'].nunique()} washout months | "
      f"{df['ticker'].nunique()} unique tickers | {len(df):,} obs")
print(f"  Date range: {df['time'].min().date()} -> {df['time'].max().date()}")

# ── Tier assignment (mirrors crisis_capitulation_signal.py) ──────────
df['quality_strict'] = (df['ROE_Min5Y']>=0.12) & (df['ROIC5Y']>=0.10) & (df['FSCORE']>=6)
df['quality_base']   = (df['ROE_Min5Y']>=0.08) & (df['ROIC5Y']>=0.08) & (df['FSCORE']>=5)
df['golden']         = df['pb_z'] < -1.0
df['rsi_os']         = df['D_RSI'] < 0.35

def assign_tier(r):
    if not r.sector_ok:                                    return 9
    if r.quality_strict and r.golden and r.rsi_os:         return 0
    if r.quality_strict and r.golden:                      return 1
    if r.quality_base   and r.pb_z < 0 and r.rsi_os:      return 2
    if r.golden:                                           return 3
    if r.quality_base   and r.pb_z < 0:                   return 4   # quality cheap (no golden, no RSI)
    if r.quality_base:                                     return 5   # quality only
    return 9

df['tier'] = df.apply(assign_tier, axis=1)

# ── Per-event capacity analysis ────────────────────────────────────────
def compute_fill(group, tier_max, capital_B):
    """
    Given candidates in tiers <= tier_max, compute how much capital (B VND)
    can be deployed given ADV constraints and name concentration cap.
    Returns (deployed_B, n_stocks, fill_pct).
    """
    cands = group[group['tier'] <= tier_max].copy()
    if cands.empty: return 0.0, 0, 0.0
    # Sort: tier ASC, then pb_z ASC, then D_RSI ASC
    cands = cands.sort_values(['tier', 'pb_z', 'D_RSI'])
    # Capacity per stock: min(ADV * MAX_FILL_PER_STOCK, NAME_CAP_FRAC * capital)
    cands['capacity'] = np.minimum(
        cands['liq_B'] * MAX_FILL_PER_STOCK,
        capital_B * NAME_CAP_FRAC
    )
    # Greedy fill until capital exhausted
    remaining = capital_B
    deployed = 0.0
    n_stocks = 0
    for _, row in cands.iterrows():
        if remaining <= 0: break
        alloc = min(row['capacity'], remaining)
        deployed  += alloc
        remaining -= alloc
        n_stocks  += 1
    fill_pct = deployed / capital_B * 100
    return deployed, n_stocks, fill_pct

# ── Analysis 1: Fill rate per event per tier expansion ────────────────
print("\n" + "="*65)
print("ANALYSIS 1: Fill rate by tier expansion (% capital deployed)")
print(f"Position sizing: max {ADV_FRAC*100:.0f}% ADV/day x {RAMP_DAYS}d ramp = "
      f"{MAX_FILL_PER_STOCK*100:.0f}% ADV total | name cap {NAME_CAP_FRAC*100:.0f}%")
print("="*65)

TIER_SCENARIOS = [
    (1,  'Tier 0+1: strict quality+golden'),
    (2,  'Tier 0-2: + quality+cheap+RSI'),
    (3,  'Tier 0-3: + golden_any'),
    (4,  'Tier 0-4: + quality+cheap'),
    (5,  'Tier 0-5: + quality_base'),
]

print(f"\n  {'Scenario':40s}  {'5B':>7s}  {'10B':>7s}  {'15B':>7s}  {'20B':>7s}  {'30B':>7s}  "
      f"{'avg_n':>6s}  {'avail_ev':>8s}")
print("  " + "-"*95)

fill_results = {}
for tier_max, label in TIER_SCENARIOS:
    fills_by_cap = {c: [] for c in CAPITAL_LEVELS}
    n_stocks_by_event = []
    events_with_any = 0
    for dt, grp in df.groupby('time'):
        cands_t = grp[grp['tier'] <= tier_max]
        if len(cands_t) > 0: events_with_any += 1
        ns = []
        for cap in CAPITAL_LEVELS:
            _, n, fp = compute_fill(grp, tier_max, cap)
            fills_by_cap[cap].append(fp)
            ns.append(n)
        n_stocks_by_event.append(np.mean(ns))
    avg_n = np.mean(n_stocks_by_event)
    n_events = df['time'].nunique()
    row = f"  {label:40s}"
    for cap in CAPITAL_LEVELS:
        if cap in [5, 10, 15, 20, 30]:
            row += f"  {np.mean(fills_by_cap[cap]):5.0f}%"
    row += f"  {avg_n:5.1f}n  {events_with_any:3d}/{n_events}"
    print(row)
    fill_results[label] = fills_by_cap

# ── Analysis 2: Per-event breakdown for Tier 0+1 (current criteria) ──
print("\n" + "="*65)
print("ANALYSIS 2: Per-event detail — Tier 0+1 (strict quality+golden)")
print("="*65)
print(f"\n  {'Date':>10s}  {'n_t01':>6s}  {'cap_5B':>7s}  {'cap_10B':>8s}  "
      f"{'cap_15B':>8s}  {'cap_20B':>8s}  {'total_ADV':>10s}  Tickers (T0+T1)")
print("  " + "-"*90)

events_thin = []   # events where even 5B can't be deployed
for dt, grp in df.groupby('time'):
    t01 = grp[grp['tier'] <= 1]
    n_t01 = len(t01)
    fills = {}
    for cap in [5, 10, 15, 20]:
        _, _, fp = compute_fill(grp, 1, cap)
        fills[cap] = fp
    total_adv = t01['liq_B'].sum() * MAX_FILL_PER_STOCK if n_t01 > 0 else 0
    tickers = ','.join(t01.sort_values('pb_z')['ticker'].head(6).tolist())
    flag = " <THIN" if fills[5] < 80 else ""
    print(f"  {str(dt.date()):>10s}  {n_t01:6d}  {fills[5]:6.0f}%  {fills[10]:7.0f}%  "
          f"{fills[15]:7.0f}%  {fills[20]:7.0f}%  {total_adv:9.1f}B  {tickers}{flag}")
    if fills[10] < 80:
        events_thin.append(dt)

print(f"\n  Events where 10B deployment < 80% filled: {len(events_thin)}/{df['time'].nunique()}")

# ── Analysis 3: What tier expansion helps thin events? ────────────────
if events_thin:
    print("\n" + "="*65)
    print("ANALYSIS 3: Thin events — can Tier 2/3 fix the gap? (10B capital)")
    print("="*65)
    print(f"\n  {'Date':>10s}  {'T0+1':>6s}  {'T0+2':>6s}  {'T0+3':>6s}  "
          f"{'T0+4':>6s}  n_added  Delta_fwd60d")
    print("  " + "-"*65)
    for dt in events_thin:
        grp = df[df['time']==dt]
        fills_t = {}
        for tm in [1, 2, 3, 4]:
            _, n, fp = compute_fill(grp, tm, 10)
            fills_t[tm] = (fp, n)
        # Forward return for T0+1 vs T0+2/T0+3 picks at 10B
        t01_ret = grp[grp['tier']<=1].sort_values('pb_z')['fwd60d'].head(5).mean()
        t02_ret = grp[grp['tier']<=2].sort_values(['tier','pb_z','D_RSI'])['fwd60d'].head(5).mean()
        n_add = fills_t[2][1] - fills_t[1][1]
        delta = (t02_ret - t01_ret)*100 if not np.isnan(t01_ret) and not np.isnan(t02_ret) else np.nan
        print(f"  {str(dt.date()):>10s}  {fills_t[1][0]:5.0f}%  {fills_t[2][0]:5.0f}%  "
              f"{fills_t[3][0]:5.0f}%  {fills_t[4][0]:5.0f}%  {n_add:+4d}n  "
              f"delta {delta:+5.1f}pp")

# ── Analysis 4: Liquidity distribution of quality+golden candidates ───
print("\n" + "="*65)
print("ANALYSIS 4: Liquidity distribution of Tier 0+1 candidates")
print("="*65)

t01_all = df[df['tier'] <= 1].copy()
print(f"\n  Tier 0+1 total obs: {len(t01_all)}")
print(f"  liq_B distribution:")
for pct in [10, 25, 50, 75, 90]:
    v = t01_all['liq_B'].quantile(pct/100)
    print(f"    P{pct}: {v:.1f}B/day")
print(f"\n  Most frequent Tier 0+1 tickers across all events:")
top_t01 = t01_all['ticker'].value_counts().head(20)
for tkr, cnt in top_t01.items():
    liq_med = t01_all[t01_all['ticker']==tkr]['liq_B'].median()
    ret_med = t01_all[t01_all['ticker']==tkr]['fwd60d'].median()*100 if 'fwd60d' in t01_all.columns else np.nan
    print(f"    {tkr:6s}  appears {cnt:2d}×  liq {liq_med:5.1f}B/day  "
          f"fwd60d_med {ret_med:+5.1f}%")

# ── Analysis 5: Recommended position sizing rule ──────────────────────
print("\n" + "="*65)
print("ANALYSIS 5: Recommended deployment approach")
print("="*65)

# What is the avg total capacity at each tier level for 10B deployment?
print("\n  Avg fill% at 10B deployment (across all events):")
for tier_max, label in TIER_SCENARIOS:
    fp_list = [compute_fill(grp, tier_max, 10)[2] for _, grp in df.groupby('time')]
    print(f"  {label:45s}  avg {np.mean(fp_list):5.0f}%  "
          f"min {np.min(fp_list):5.0f}%  "
          f"<80%: {sum(f<80 for f in fp_list)}/{len(fp_list)} events")

# ── Analysis 6: ADV-based liq floor calibration ───────────────────────
print("\n" + "="*65)
print("ANALYSIS 6: Liq floor sensitivity — candidates vs quality at each liq threshold")
print("="*65)
print(f"\n  {'Liq floor':>10s}  {'n_cands_avg':>12s}  {'n_T01_avg':>10s}  "
      f"{'fwd60d_med':>11s}  {'win%':>6s}")
print("  " + "-"*55)
for liq_floor in [1, 2, 3, 5, 7, 10, 15]:
    sub = df[df['liq_B'] >= liq_floor]
    n_avg = sub.groupby('time').size().mean()
    t01_s = sub[sub['tier']<=1]
    n_t01 = t01_s.groupby('time').size().mean() if not t01_s.empty else 0
    med_ret = t01_s['fwd60d'].median()*100 if not t01_s.empty else np.nan
    win = (t01_s['fwd60d']>0).mean()*100 if not t01_s.empty else np.nan
    print(f"  {liq_floor:>8.0f}B  {n_avg:11.1f}  {n_t01:9.1f}  "
          f"{med_ret:+10.1f}%  {win:5.0f}%")

# ── FIGURE ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 12))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('Capitulation Liquidity Audit — Deployment Capacity Analysis\n'
             'Position sizing: max 30% ADV/day × 3-day ramp = 90% ADV per stock',
             fontsize=12, fontweight='bold', color='white', y=0.99)
dark = '#161b22'; sp = '#30363d'
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.42, wspace=0.35)

def sty(ax, t=""):
    ax.set_facecolor(dark); [s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e', labelsize=8)
    if t: ax.set_title(t, color='#e6edf3', fontsize=9, fontweight='bold', pad=6)

# ── R1C0-1: Fill rate heat-map by tier × capital ──────────────────────
ax1 = fig.add_subplot(gs[0, :2])
sty(ax1, 'Fill Rate (%) by Tier Expansion × Capital Level\n(darker green = fully deployed)')
caps_show = [5, 10, 15, 20, 30]
tiers_show = [l for _, l in TIER_SCENARIOS]
matrix = np.array([[np.mean(fill_results[l][c]) for c in caps_show] for l in tiers_show])
im = ax1.imshow(matrix, aspect='auto', cmap='RdYlGn', vmin=0, vmax=100)
ax1.set_xticks(range(len(caps_show)))
ax1.set_xticklabels([f'{c}B' for c in caps_show], color='#8b949e')
ax1.set_yticks(range(len(tiers_show)))
ax1.set_yticklabels([l[:35] for l in tiers_show], color='#8b949e', fontsize=8)
for i in range(len(tiers_show)):
    for j in range(len(caps_show)):
        ax1.text(j, i, f'{matrix[i,j]:.0f}%', ha='center', va='center',
                 color='black' if matrix[i,j]>60 else 'white', fontsize=9, fontweight='bold')
plt.colorbar(im, ax=ax1, shrink=0.8)

# ── R1C2: Liq distribution of Tier 0+1 ───────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
sty(ax2, 'Tier 0+1 Liquidity Distribution\n(quality+golden candidates)')
liq_vals = t01_all['liq_B'].clip(0, 100)
ax2.hist(liq_vals, bins=20, color='#e8c547', alpha=0.85)
for pct, col in [(25,'#d62728'),(50,'#3fb950'),(75,'#58a6ff')]:
    v = liq_vals.quantile(pct/100)
    ax2.axvline(v, color=col, lw=1.5, ls='--', label=f'P{pct}={v:.0f}B')
ax2.set_xlabel('liq B/day', color='#8b949e')
ax2.set_ylabel('n candidates', color='#8b949e')
ax2.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')

# ── R2C0: Fill rate across events at 10B / Tier 0+1 ──────────────────
ax3 = fig.add_subplot(gs[1, 0])
sty(ax3, 'Fill Rate per Event (10B, Tier 0+1)\nvs Tier 0-2 expansion')
event_dates = sorted(df['time'].unique())
fills_01  = [compute_fill(df[df['time']==dt], 1, 10)[2] for dt in event_dates]
fills_02  = [compute_fill(df[df['time']==dt], 2, 10)[2] for dt in event_dates]
x_ev = range(len(event_dates))
ax3.bar(x_ev, fills_01, color='#58a6ff', alpha=0.8, label='Tier 0+1', width=0.6)
ax3.bar(x_ev, [max(0, f2-f1) for f1,f2 in zip(fills_01, fills_02)],
        bottom=fills_01, color='#3fb950', alpha=0.7, label='Tier 2 addition', width=0.6)
ax3.axhline(80, color='#e8c547', lw=1.5, ls='--', label='80% threshold')
ax3.set_ylim(0, 110)
ax3.set_xticks(x_ev)
ax3.set_xticklabels([str(d.year)[-2:]+'/'+str(d.month).zfill(2)
                     for d in pd.DatetimeIndex(event_dates)],
                    rotation=45, ha='right', color='#8b949e', fontsize=7)
ax3.set_ylabel('Fill %', color='#8b949e')
ax3.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')

# ── R2C1: n candidates per tier per event ────────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
sty(ax4, 'Avg n Candidates per Event by Tier\n(cumulative)')
tier_labels_s = ['T0+1\nstrict+golden', 'T0+2\n+quality+RSI', 'T0+3\n+golden_any',
                 'T0+4\n+quality', 'T0+5\n+quality_base']
avg_ns = []
for tm in [1, 2, 3, 4, 5]:
    avg_n = df[df['tier'] <= tm].groupby('time').size().mean()
    avg_ns.append(avg_n)
colors_n = ['#58a6ff','#3fb950','#e8c547','#f97316','#aaaaaa']
ax4.bar(range(len(avg_ns)), avg_ns, color=colors_n, alpha=0.85)
for i, v in enumerate(avg_ns):
    ax4.text(i, v+0.2, f'{v:.1f}', ha='center', color='white', fontsize=9)
ax4.set_xticks(range(len(tier_labels_s)))
ax4.set_xticklabels(tier_labels_s, color='#8b949e', fontsize=7)
ax4.set_ylabel('Avg n stocks/event', color='#8b949e')
ax4.axhline(5, color='white', lw=1, ls='--', alpha=0.5, label='5-stock target')
ax4.legend(fontsize=8, facecolor='#1c2128', labelcolor='white')

# ── R2C2: Top recurring stocks with returns ───────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor(dark); ax5.axis('off')
sty(ax5, 'Tier 0+1 Recurring Stocks\n(appears most across events)')
top10 = t01_all['ticker'].value_counts().head(10)
rows_t = [['Ticker', 'Count', 'Liq B/d', 'Med fwd60d']]
for tkr, cnt in top10.items():
    liq_m = t01_all[t01_all['ticker']==tkr]['liq_B'].median()
    ret_m = t01_all[t01_all['ticker']==tkr]['fwd60d'].median()*100
    rows_t.append([tkr, str(int(cnt)), f'{liq_m:.1f}', f'{ret_m:+.1f}%'])
tbl = ax5.table(cellText=rows_t[1:], colLabels=rows_t[0], loc='center', cellLoc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1.1, 2.1)
for (ri, ci), cell in tbl.get_celld().items():
    cell.set_facecolor('#1c2128' if ri%2==0 else dark)
    cell.set_text_props(color='#e6edf3'); cell.set_edgecolor(sp)
    if ri == 0:
        cell.set_facecolor('#21262d')
        cell.set_text_props(color='white', fontweight='bold')

out = WORKDIR + r"\capit_liquidity_audit.png"
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: capit_liquidity_audit.png")
plt.close()

# ── Final recommendation print ────────────────────────────────────────
print("\n" + "="*65)
print("RECOMMENDATION")
print("="*65)
t1_fills_10 = [compute_fill(df[df['time']==dt], 1, 10)[2] for dt in event_dates]
t2_fills_10 = [compute_fill(df[df['time']==dt], 2, 10)[2] for dt in event_dates]
print(f"\n  10B deployment via Tier 0+1 only:")
print(f"    avg fill {np.mean(t1_fills_10):.0f}%  |  events >80%: {sum(f>80 for f in t1_fills_10)}/{len(t1_fills_10)}")
print(f"  10B deployment via Tier 0-2 (add quality+cheap+RSI when T01 depleted):")
print(f"    avg fill {np.mean(t2_fills_10):.0f}%  |  events >80%: {sum(f>80 for f in t2_fills_10)}/{len(t2_fills_10)}")
print()
print("DONE")
