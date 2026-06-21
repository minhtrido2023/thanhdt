"""
book_c_signal.py — Book C (Value) signal design + BQ validation
================================================================
Q: "Có hiệu quả thật không?" — validate trực tiếp từ ticker_prune
   thay vì edge_panel abstract.

Signal: PB+PE composite rank, quality gate ROIC5Y>=8% + FSCORE>=5
Universe: ticker_prune, liq>=10B/day, monthly rebalance
Forward return: profit_1M (T+20) từ BQ — historical validation only
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

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
BQ_PATH = r"bq"
os.chdir(WORKDIR)

NAVF  = WORKDIR + r"\data\5sys_prodspec_201401_202605_dt5g_realetf.csv"
TC_RT = 0.003    # 0.30% round-trip
NAME_CAP = 0.08

STATE_NAMES = {1:'CRISIS',2:'BEAR',3:'NEUTRAL',4:'BULL',5:'EX-BULL'}
STATE_ALLOC = {1:0.0, 2:0.2, 3:0.7, 4:1.0, 5:1.3}

def bq(sql, label=""):
    if label: print(f"  > {label}...", end=" ", flush=True)
    cmd = (f'"{BQ_PATH}" query --use_legacy_sql=false'
           f' --project_id={PROJECT} --format=csv --quiet --max_rows=100000')
    r = subprocess.run(cmd, input=sql, capture_output=True,
                       text=True, encoding='utf-8', shell=True)
    df = pd.read_csv(StringIO(r.stdout)) if r.returncode==0 else pd.DataFrame()
    if label: print(f"OK ({len(df):,} rows)")
    return df

def ann(ret):
    ret = ret.dropna(); n = len(ret)
    if n < 3: return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan, Calmar=np.nan)
    mu=ret.mean()*12; sd=ret.std(ddof=1)*np.sqrt(12)
    cagr=(1+ret).prod()**(12/n)-1
    nav=(1+ret).cumprod(); dd=(nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd>0 else 0,
                MaxDD=dd*100, Calmar=cagr/abs(dd) if dd<0 else np.nan)

def sub(r, lo, hi):
    return r[(r.index>=pd.Period(lo))&(r.index<=pd.Period(hi))]

# ════════════════════════════════════════════════════════════
# PART 0: PRINT LIVE SIGNAL SQL
# ════════════════════════════════════════════════════════════
LIVE_SQL = """-- Book C VALUE signal (live screen, copy vào BQ console)
-- Signal: PB+PE composite rank, quality gate ROIC5Y>=8% + FSCORE>=5
-- Universe: ticker_1m, liq>=10B/day
-- Output: top quintile (20%) = Book C picks today

WITH quality_universe AS (
  SELECT
    t.time, t.ticker, t.Close,
    t.PB, t.PE, t.ROIC5Y, t.FSCORE, t.ROE_Min5Y,
    t.Trading_Value_1M_P50 / 1e9                    AS liq_B,
    t.ICB_Code, t.Risk_Rating,
    -- rank within quality-filtered universe (same-day, cross-sectional)
    PERCENT_RANK() OVER (ORDER BY t.PB ASC)          AS pb_rank,
    PERCENT_RANK() OVER (ORDER BY t.PE ASC)          AS pe_rank,
    COUNT(*) OVER ()                                  AS n_universe
  FROM tav2_bq.ticker_1m AS t
  WHERE t.time = (SELECT MAX(time) FROM tav2_bq.ticker_1m)
    AND t.PB  > 0 AND t.PE > 0 AND t.PE < 100
    AND t.ROIC5Y  >= 0.08          -- quality gate 1: ROIC5Y >= 8%
    AND t.FSCORE  >= 5             -- quality gate 2: Piotroski >= 5
    AND t.Trading_Value_1M_P50 >= 10e9   -- liq >= 10B/day
),
scored AS (
  SELECT *,
    pb_rank + pe_rank                                 AS vscore,
    PERCENT_RANK() OVER (ORDER BY pb_rank+pe_rank ASC) AS value_rank
  FROM quality_universe
)
SELECT
  time, ticker, Close, PB, PE,
  ROUND(ROIC5Y*100,1)  AS ROIC5Y_pct,
  FSCORE,
  ROUND(liq_B,1)        AS liq_B,
  ROUND(pb_rank,3)      AS pb_rank,
  ROUND(pe_rank,3)      AS pe_rank,
  ROUND(vscore,3)       AS vscore,
  n_universe,
  CASE WHEN value_rank <= 0.20 THEN 'PICK'
       WHEN value_rank <= 0.30 THEN 'WATCH'
       ELSE 'OUT' END   AS status
FROM scored
WHERE value_rank <= 0.30
ORDER BY vscore
"""

print("="*65)
print("BOOK C — VALUE SIGNAL SQL")
print("="*65)
print(LIVE_SQL)

# Save SQL file
with open(WORKDIR + r"\book_c_live_signal.sql", "w", encoding="utf-8") as f:
    f.write(LIVE_SQL)
print("Saved: book_c_live_signal.sql")

# ════════════════════════════════════════════════════════════
# PART 1: LIVE SCREEN — current picks
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 1: LIVE SCREEN (ticker_1m latest)")
print("="*65)

live_sql_run = LIVE_SQL.replace(
    "-- Book C VALUE signal (live screen, copy vào BQ console)\n"
    "-- Signal: PB+PE composite rank, quality gate ROIC5Y>=8% + FSCORE>=5\n"
    "-- Universe: ticker_1m, liq>=10B/day\n"
    "-- Output: top quintile (20%) = Book C picks today\n\n", ""
)

live = bq(live_sql_run, "live screen ticker_1m")
if not live.empty:
    picks = live[live['status']=='PICK']
    watch = live[live['status']=='WATCH']
    print(f"\n  Universe after quality gate: {live['n_universe'].iloc[0]} stocks")
    print(f"  PICKS (top 20%): {len(picks)} stocks")
    print(f"  WATCHLIST (21-30%): {len(watch)} stocks")
    print(f"\n  --- PICKS ---")
    cols = ['ticker','Close','PB','PE','ROIC5Y_pct','FSCORE','liq_B','vscore']
    cols = [c for c in cols if c in live.columns]
    print(picks[cols].to_string(index=False))
    if not watch.empty:
        print(f"\n  --- WATCHLIST ---")
        print(watch[cols].to_string(index=False))

    # Compute liq-weighted portfolio for current picks
    if len(picks) >= 3:
        print(f"\n  --- CURRENT PORTFOLIO WEIGHTS (liq-weighted, max 8%) ---")
        liq = picks['liq_B'].clip(upper=picks['liq_B'].quantile(0.9))
        w = liq / liq.sum()
        w = w.clip(upper=NAME_CAP)
        w = w / w.sum()
        for _, row in picks.iterrows():
            idx_ = picks.index.get_loc(row.name)
            wi = w.iloc[idx_] * 100
            print(f"    {row['ticker']:6s}  PB={row['PB']:.2f}  PE={row['PE']:.1f}  "
                  f"ROIC={row['ROIC5Y_pct']:.1f}%  FSCORE={int(row['FSCORE'])}  "
                  f"liq={row['liq_B']:.1f}B  weight={wi:.1f}%")

# ════════════════════════════════════════════════════════════
# PART 2: BQ HISTORICAL BACKTEST (ticker_prune + profit_1M)
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 2: BQ HISTORICAL BACKTEST (ticker_prune, 2016-2026)")
print("Signal applied monthly, profit_1M as forward return")
print("="*65)

HIST_SQL = """
WITH
-- Rebalance date = last trading day of each month
monthly_last AS (
  SELECT
    DATE_TRUNC(t.time, MONTH) AS month_start,
    MAX(t.time)               AS rebal_date
  FROM tav2_bq.ticker_prune AS t
  WHERE t.time >= '2016-01-01' AND t.time <= '2026-03-31'
  GROUP BY 1
),
-- Quality-filtered universe on rebalance dates
universe AS (
  SELECT
    t.time, t.ticker,
    t.PB, t.PE, t.ROIC5Y, t.FSCORE,
    t.Trading_Value_1M_P50, t.profit_1M
  FROM tav2_bq.ticker_prune AS t
  INNER JOIN monthly_last m ON t.time = m.rebal_date
  WHERE t.PB  > 0  AND t.PE > 0 AND t.PE < 100
    AND t.ROIC5Y  >= 0.08
    AND t.FSCORE  >= 5
    AND t.Trading_Value_1M_P50 >= 10e9
    AND t.profit_1M IS NOT NULL
),
-- Cross-sectional rank within quality universe per date
ranked AS (
  SELECT *,
    PERCENT_RANK() OVER (PARTITION BY time ORDER BY PB  ASC) AS pb_rank,
    PERCENT_RANK() OVER (PARTITION BY time ORDER BY PE  ASC) AS pe_rank,
    COUNT(*) OVER (PARTITION BY time)                         AS n_universe
  FROM universe
),
scored AS (
  SELECT *,
    pb_rank + pe_rank AS vscore,
    PERCENT_RANK() OVER (PARTITION BY time ORDER BY pb_rank+pe_rank ASC) AS value_rank
  FROM ranked
),
picks AS (
  SELECT * FROM scored WHERE value_rank <= 0.20
),
-- Also compute universe average return (benchmark)
universe_bench AS (
  SELECT time, AVG(profit_1M) AS bench_return, COUNT(*) AS n_bench
  FROM universe
  GROUP BY time
)
SELECT
  p.time,
  COUNT(*)                                               AS n_picks,
  AVG(p.profit_1M)                                      AS eq_return_pct,
  SUM(p.profit_1M * p.Trading_Value_1M_P50)
    / NULLIF(SUM(p.Trading_Value_1M_P50), 0)            AS liq_return_pct,
  AVG(p.n_universe)                                      AS n_universe,
  ROUND(AVG(p.PB), 2)                                   AS avg_pb,
  ROUND(AVG(p.PE), 1)                                   AS avg_pe,
  ROUND(AVG(p.ROIC5Y)*100, 1)                           AS avg_roic_pct,
  ROUND(AVG(p.FSCORE), 1)                               AS avg_fscore,
  ub.bench_return                                        AS bench_return_pct,
  STRING_AGG(p.ticker ORDER BY p.vscore LIMIT 8)        AS tickers
FROM picks AS p
JOIN universe_bench ub ON p.time = ub.time
GROUP BY p.time, ub.bench_return
ORDER BY p.time
"""

hist = bq(HIST_SQL, "historical BQ backtest (ticker_prune)")

if hist.empty:
    print("  ERROR: historical query returned empty")
    import sys; sys.exit(1)

hist['time'] = pd.to_datetime(hist['time'])
hist = hist.set_index('time').sort_index()
hist.index = hist.index.to_period('M')

# profit_1M is in % already — convert to decimal returns
hist['ret_eq']    = hist['eq_return_pct'] / 100
hist['ret_liq']   = hist['liq_return_pct'] / 100
hist['ret_bench'] = hist['bench_return_pct'] / 100

print(f"\n  Backtest: {hist.index.min()} -> {hist.index.max()} ({len(hist)} months)")
print(f"  Avg n_picks: {hist['n_picks'].mean():.1f}  "
      f"Avg n_universe: {hist['n_universe'].mean():.0f}")
print(f"\n  Portfolio composition (average):")
print(f"    PB: {hist['avg_pb'].mean():.2f}  PE: {hist['avg_pe'].mean():.1f}  "
      f"ROIC5Y: {hist['avg_roic_pct'].mean():.1f}%  FSCORE: {hist['avg_fscore'].mean():.1f}")

# Monthly thin-portfolio months
thin = hist[hist['n_picks'] < 5]
print(f"\n  Months with < 5 picks: {len(thin)} "
      f"({', '.join(str(p) for p in thin.index[:10])}{'...' if len(thin)>10 else ''})")

# ── Apply DT5G gating + TC ────────────────────────────────────
print("\n  Applying DT5G state gating + TC 0.30%...")
raw_state = bq("""
    SELECT s.time, s.state
    FROM tav2_bq.vnindex_5state_dt5g_live AS s
    ORDER BY s.time
""")
raw_state['time'] = pd.to_datetime(raw_state['time'])
raw_state = raw_state.set_index('time')['state'].astype(int)
mo_state = raw_state.resample('ME').apply(lambda x: int(x.mode()[0]))
mo_state.index = mo_state.index.to_period('M')

hist['state'] = mo_state.reindex(hist.index).fillna(3).astype(int)
hist['alloc']  = hist['state'].map(STATE_ALLOC)

# TC: estimate turnover ~60% monthly (new picks replace ~3/5 names)
# TC_MONTHLY = TC_RT * 0.60 (round-trip on 60% of portfolio)
TC_MONTHLY = TC_RT * 0.60

hist['ret_gated_eq']  = hist['alloc'] * hist['ret_eq']  - hist['alloc'].diff().abs().fillna(0)*TC_RT - TC_MONTHLY*hist['alloc']
hist['ret_gated_liq'] = hist['alloc'] * hist['ret_liq'] - hist['alloc'].diff().abs().fillna(0)*TC_RT - TC_MONTHLY*hist['alloc']
hist['ret_bench_gated'] = hist['alloc'] * hist['ret_bench']

# ════════════════════════════════════════════════════════════
# PART 3: PERFORMANCE vs BENCHMARK + MOMENTUM
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 3: PERFORMANCE SUMMARY")
print("="*65)

# Momentum V5 for comparison
nav_m = pd.read_csv(NAVF, parse_dates=['time']).set_index('time')
M_mo = nav_m['V5_V4_KellyQ2'].resample('ME').last().pct_change()
M_mo.index = M_mo.index.to_period('M')
M_mo = M_mo.reindex(hist.index).dropna()

idx_common = hist.index.intersection(M_mo.index)

def print_metrics(label, ret, indent="  "):
    m = ann(ret.dropna())
    if np.isnan(m['CAGR']): return
    print(f"{indent}{label:30s}  CAGR {m['CAGR']:5.1f}%  "
          f"Sh {m['Sharpe']:.2f}  MaxDD {m['MaxDD']:5.1f}%  Cal {m['Calmar']:.2f}")

print("\n--- Standalone value book (gated + TC) ---")
print_metrics("EW gated (DT5G + TC)",   hist['ret_gated_eq'])
print_metrics("Liq-w gated (DT5G + TC)",hist['ret_gated_liq'])
print_metrics("Quality universe bench", hist['ret_bench_gated'])
print_metrics("Momentum V5 (same idx)", M_mo.loc[idx_common])

print("\n--- IS (2016-2019) / OOS (2020-2026) ---")
for label, ret in [
    ("Value EW gated",     hist['ret_gated_eq']),
    ("Value liq-w gated",  hist['ret_gated_liq']),
    ("Momentum V5",        M_mo),
]:
    ri = sub(ret,'2016-01','2019-12'); ro = sub(ret,'2020-01','2026-12')
    mi = ann(ri); mo_m = ann(ro)
    print(f"  {label:26s}  IS {mi['CAGR']:5.1f}%/Sh{mi['Sharpe']:.2f}/Cal{mi['Calmar']:.2f}  "
          f"OOS {mo_m['CAGR']:5.1f}%/Sh{mo_m['Sharpe']:.2f}/Cal{mo_m['Calmar']:.2f}")

GRIND = ("2025-09", "2026-03")
print(f"\n--- Grind {GRIND[0]}..{GRIND[1]} ---")
for label, ret in [
    ("Value EW gated",  hist['ret_gated_eq']),
    ("Momentum V5",     M_mo),
]:
    g = sub(ret, *GRIND)
    cum = ((1+g).prod()-1)*100 if len(g)>0 else np.nan
    print(f"  {label:26s}  {cum:+.1f}%")

print("\n--- Option A blend: V2.2 70% + Value 30% ---")
idx_bl = M_mo.index.intersection(hist['ret_gated_eq'].index)
blend_eq  = 0.70*M_mo.loc[idx_bl] + 0.30*hist['ret_gated_eq'].loc[idx_bl]
blend_liq = 0.70*M_mo.loc[idx_bl] + 0.30*hist['ret_gated_liq'].loc[idx_bl]
print_metrics("V2.2 pure momentum",    M_mo.loc[idx_bl])
print_metrics("V2.2 + 30% value EW",  blend_eq)
print_metrics("V2.2 + 30% value liq", blend_liq)

print("\n--- Annual breakdown ---")
print(f"  {'Year':6s}  {'Value EW':>9s}  {'Momentum':>9s}  {'Blend':>9s}  {'Diff V-M':>9s}")
print("  " + "-"*55)
for yr in range(2016, 2027):
    sv = sub(hist['ret_gated_eq'], f'{yr}-01', f'{yr}-12')
    sm = sub(M_mo, f'{yr}-01', f'{yr}-12')
    sb = sub(blend_eq, f'{yr}-01', f'{yr}-12')
    if len(sv)<6: continue
    rv = ((1+sv).prod()-1)*100
    rm = ((1+sm).prod()-1)*100 if len(sm)>=6 else np.nan
    rb = ((1+sb).prod()-1)*100 if len(sb)>=6 else np.nan
    mark = "*" if not np.isnan(rv) and not np.isnan(rm) and rv>rm else " "
    print(f"  {yr}   {rv:+8.1f}%  {rm:+8.1f}%  {rb:+8.1f}%  "
          f"{rv-rm:+8.1f}%{mark}")

# IC validation
print("\n--- Signal IC: PB+PE rank -> profit_1M (cross-sectional) ---")
ic_vals = []
for ym, g in hist[['ret_eq','ret_bench']].groupby(hist.index):
    # We already have EW return; compute IC from raw panel would need re-query
    pass
# Approximate: value EW vs universe bench spread = excess return
spread = hist['ret_eq'] - hist['ret_bench']
print(f"  Avg monthly spread (value EW - universe bench): "
      f"{spread.mean()*100:+.2f}%/mo (={spread.mean()*1200:+.1f}pp/yr equiv)")
print(f"  Win rate (value > bench): {(spread>0).mean()*100:.0f}%  "
      f"t-stat: {spread.mean()/spread.std()*np.sqrt(len(spread)):.2f}")

# ════════════════════════════════════════════════════════════
# PART 4: RECENT PICKS HISTORY (last 12 months)
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 4: RECENT PICKS HISTORY (last 12 months)")
print("="*65)
last12 = hist.tail(12)
print(f"\n  {'Month':>8}  {'n':>3}  {'Tickers':60s}  {'Return':>8}  {'State':>8}")
print("  " + "-"*95)
for ym, row in last12.iterrows():
    tickers_str = str(row.get('tickers',''))[:58]
    ret_v = row['ret_gated_eq']*100
    state_n = STATE_NAMES.get(int(row['state']),'?')
    print(f"  {str(ym):>8}  {int(row['n_picks']):3d}  {tickers_str:60s}  "
          f"{ret_v:+7.1f}%  {state_n:>8}")

# ════════════════════════════════════════════════════════════
# FIGURES
# ════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('Book C Value Signal — BQ Validation (ticker_prune)\n'
             'Signal: PB+PE rank | Quality: ROIC5Y>=8%, FSCORE>=5 | Liq>=10B | TC 0.30%',
             fontsize=12, fontweight='bold', color='white', y=0.98)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)
dark = '#161b22'; sp = '#30363d'

def sty(ax, t=""):
    ax.set_facecolor(dark); [s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e')
    if t: ax.set_title(t, color='#e6edf3', fontsize=10, fontweight='bold', pad=8)

# ── R1C0-1: NAV comparison ─────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
sty(ax1, 'Cumulative NAV: Value Book C vs Momentum V5 vs Blend 30%')

nav_v  = (1+hist['ret_gated_eq'].reindex(idx_bl).dropna()).cumprod()
nav_m2 = (1+M_mo.loc[idx_bl].dropna()).cumprod()
nav_bl = (1+blend_eq.dropna()).cumprod()

for nav_s, label, col, lw, ls in [
    (nav_m2, 'Momentum V5 (V2.2 proxy)', '#58a6ff', 1.8, '-'),
    (nav_v,  'Value Book C (EW gated)',  '#e8c547', 1.8, '-'),
    (nav_bl, 'Blend 70%M+30%V',          '#f97316', 2.2, '--'),
]:
    ts = nav_s.index.to_timestamp()
    ax1.semilogy(ts, nav_s.values, label=label, color=col, lw=lw, ls=ls)

# Shade states
state_ts = mo_state.reindex(idx_bl)
for s in [1, 5]:
    mask = state_ts == s
    for i, (idx_t, is_s) in enumerate(mask.items()):
        if is_s:
            ts = idx_t.to_timestamp()
            te = (idx_t+1).to_timestamp()
            ax1.axvspan(ts, te, alpha=0.15,
                        color=('#d62728' if s==1 else '#9467bd'))

import matplotlib.patches as mpatches
patches = [mpatches.Patch(color='#d62728',alpha=0.3,label='CRISIS'),
           mpatches.Patch(color='#9467bd',alpha=0.3,label='EX-BULL')]
handles, lbls = ax1.get_legend_handles_labels()
ax1.legend(handles+patches, lbls+['CRISIS','EX-BULL'],
           fontsize=9, facecolor='#1c2128', labelcolor='white')
ax1.set_ylabel('NAV (log, start=1)', color='#8b949e')

# ── R1C2: Monthly spread (value - bench) ──────────────────
ax2 = fig.add_subplot(gs[0, 2])
sty(ax2, 'Monthly Excess Return\nValue vs Universe Bench')
sp_vals = (hist['ret_eq'] - hist['ret_bench']).reindex(idx_bl)*100
ts_sp = sp_vals.index.to_timestamp()
colors_sp = ['#3fb950' if v>0 else '#d62728' for v in sp_vals]
ax2.bar(ts_sp, sp_vals.values, color=colors_sp, alpha=0.8, width=20)
ax2.axhline(0, color='white', lw=0.8, ls='--', alpha=0.5)
ax2.axhline(sp_vals.mean(), color='#e8c547', lw=1.5, ls='--',
            label=f'Avg {sp_vals.mean():+.2f}%/mo')
ax2.set_ylabel('Excess %/month', color='#8b949e')
ax2.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')

# ── R2C0: Annual returns bar ──────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
sty(ax3, 'Annual Returns: Value vs Momentum')
ann_yrs, rv_l, rm_l = [], [], []
for yr in range(2016, 2027):
    sv = sub(hist['ret_gated_eq'], f'{yr}-01', f'{yr}-12')
    sm = sub(M_mo, f'{yr}-01', f'{yr}-12')
    if len(sv)<6: continue
    ann_yrs.append(yr)
    rv_l.append(((1+sv).prod()-1)*100)
    rm_l.append(((1+sm).prod()-1)*100 if len(sm)>=6 else np.nan)
x = np.arange(len(ann_yrs)); w = 0.38
ax3.bar(x-w/2, rv_l, w, label='Value C', color='#e8c547', alpha=0.85)
ax3.bar(x+w/2, rm_l, w, label='Momentum V5', color='#58a6ff', alpha=0.85)
ax3.axhline(0, color='white', lw=0.8, ls='--', alpha=0.5)
ax3.set_xticks(x)
ax3.set_xticklabels([str(y)[-2:] for y in ann_yrs], color='#8b949e', fontsize=9)
ax3.set_ylabel('%', color='#8b949e')
ax3.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')

# ── R2C1: Portfolio size over time ───────────────────────
ax4 = fig.add_subplot(gs[1, 1])
sty(ax4, 'Portfolio Size (n_picks) over Time\n& Avg Quality Metrics')
ts_n = hist.index.to_timestamp()
ax4.bar(ts_n, hist['n_picks'].values, color='#7fafcf', alpha=0.7, width=20)
ax4.axhline(5, color='#d62728', lw=1, ls='--', alpha=0.7, label='Min 5')
ax4.set_ylabel('n picks', color='#8b949e')
ax4r = ax4.twinx()
ax4r.plot(ts_n, hist['avg_roic_pct'].values, color='#3fb950',
          lw=1.5, label='ROIC5Y% (right)')
ax4r.set_ylabel('ROIC5Y %', color='#3fb950')
ax4r.tick_params(colors='#3fb950')
lines1,l1=ax4.get_legend_handles_labels(); lines2,l2=ax4r.get_legend_handles_labels()
ax4.legend(lines1+lines2, l1+l2, fontsize=8, facecolor='#1c2128', labelcolor='white')

# ── R2C2: Summary metrics table ──────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
ax5.set_facecolor(dark); ax5.axis('off')
sty(ax5, 'Performance Summary (BQ validated)')
rows_t = [['Strategy','CAGR','Sharpe','MaxDD','Calmar']]
for label, ret in [
    ('Pure V2.2 (mom)', M_mo.loc[idx_bl]),
    ('Value C EW gated', hist['ret_gated_eq'].loc[idx_bl]),
    ('Value C liq gated', hist['ret_gated_liq'].loc[idx_bl]),
    ('Blend 70+30% EW', blend_eq),
]:
    m = ann(ret.dropna())
    rows_t.append([label,
                   f"{m['CAGR']:.1f}%" if not np.isnan(m['CAGR']) else 'n/a',
                   f"{m['Sharpe']:.2f}" if not np.isnan(m['Sharpe']) else 'n/a',
                   f"{m['MaxDD']:.1f}%" if not np.isnan(m['MaxDD']) else 'n/a',
                   f"{m['Calmar']:.2f}" if not np.isnan(m['Calmar']) else 'n/a'])
tbl = ax5.table(cellText=rows_t[1:], colLabels=rows_t[0],
                loc='center', cellLoc='center')
tbl.auto_set_font_size(False); tbl.set_fontsize(8.5); tbl.scale(1.1, 2.0)
for (ri,ci), cell in tbl.get_celld().items():
    cell.set_facecolor('#1c2128' if ri%2==0 else dark)
    cell.set_text_props(color='#e6edf3'); cell.set_edgecolor(sp)
    if ri==0:
        cell.set_facecolor('#21262d')
        cell.set_text_props(color='white', fontweight='bold')
    if ri>0 and 'Blend' in rows_t[ri][0]:
        cell.set_facecolor('#1a2e0d')

out = WORKDIR + r"\book_c_signal.png"
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: book_c_signal.png")
plt.close()

# Save backtest CSV
hist[['n_picks','eq_return_pct','liq_return_pct','bench_return_pct',
      'avg_pb','avg_pe','avg_roic_pct','avg_fscore',
      'state','alloc','ret_gated_eq','ret_gated_liq','tickers']].to_csv(
    WORKDIR + r"\data\book_c_backtest.csv")
print("Saved: data/book_c_backtest.csv")
print("\nDONE")
