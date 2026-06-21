"""
book_c_rebal_timing.py — Optimal monthly rebalance day for Book C (Value)
==========================================================================
Q: BCTC ra ngay 20-30 cua thang dau quy. Rebalance ngay nao trong thang
   de Book C dung du lieu TUOI nhat va hieu qua nhat?

Test: same signal (PB+PE rank, quality gate V4), 7 anchor days:
  day 1 / 5 / 10 / 15 / 20 / 25 / EOM (last trading day)
Metric: profit_1M (T+20) per rebalance event + data staleness (days since
        latest Release_Date at rebalance).
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
    if r.returncode != 0: print("ERR:", r.stderr[:300])
    return df

def ann(ret):
    ret = ret.dropna(); n = len(ret)
    if n < 6: return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan)
    mu=ret.mean()*12; sd=ret.std(ddof=1)*np.sqrt(12)
    cagr=(1+ret).prod()**(12/n)-1
    nav=(1+ret).cumprod(); dd=(nav/nav.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=mu/sd if sd>0 else 0, MaxDD=dd*100)

# ════════════════════════════════════════════════════════════
# PART 1: When do financial reports actually land?
# ════════════════════════════════════════════════════════════
print("="*65)
print("PART 1: Release_Date distribution (ticker_financial, 2016+)")
print("="*65)

rel = bq("""
SELECT
  EXTRACT(MONTH FROM f.Release_Date) AS rel_month,
  EXTRACT(DAY   FROM f.Release_Date) AS rel_day,
  COUNT(*) AS n
FROM tav2_bq.ticker_financial AS f
WHERE f.Release_Date IS NOT NULL AND f.time >= '2016-01-01'
GROUP BY 1, 2 ORDER BY 1, 2
""", "release date histogram")

# Month-of-quarter position: month 1/2/3 of quarter
rel['moq'] = ((rel['rel_month'] - 1) % 3) + 1
moq_dist = rel.groupby('moq')['n'].sum()
total_n = moq_dist.sum()
print(f"\n  Releases by month-of-quarter:")
for moq, n in moq_dist.items():
    print(f"    Month {moq} of quarter: {n:,} ({n/total_n*100:.0f}%)")

# Within month-1 of quarter, day distribution
m1 = rel[rel['moq']==1].groupby('rel_day')['n'].sum()
m1_cum = m1.cumsum() / m1.sum() * 100
print(f"\n  Within month 1 of quarter, cumulative % released by day:")
for d in [10, 15, 18, 20, 22, 25, 28, 31]:
    pct = m1_cum[m1_cum.index <= d].iloc[-1] if len(m1_cum[m1_cum.index <= d]) else 0
    print(f"    by day {d:2d}: {pct:5.1f}%")

# ════════════════════════════════════════════════════════════
# PART 2: Backtest 7 rebalance anchors
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 2: Backtest — same signal, 7 rebalance day anchors (2016+)")
print("="*65)

MAIN = """
WITH
anchors AS (SELECT a FROM UNNEST([1,5,10,15,20,25]) AS a),
days AS (
  SELECT DISTINCT t.time FROM tav2_bq.ticker_prune AS t
  WHERE t.time >= '2016-01-01' AND t.time <= '2026-03-31'
),
rebal AS (
  SELECT DATE_TRUNC(d.time, MONTH) AS m, a.a AS anchor, MIN(d.time) AS rd
  FROM days d CROSS JOIN anchors a
  WHERE EXTRACT(DAY FROM d.time) >= a.a
  GROUP BY 1, 2
  UNION ALL
  SELECT DATE_TRUNC(d.time, MONTH) AS m, 99 AS anchor, MAX(d.time) AS rd
  FROM days d GROUP BY 1
),
rebal_dates AS (SELECT DISTINCT rd FROM rebal),
universe AS (
  SELECT t.time, t.ticker, t.PB, t.PE, t.profit_1M, t.Trading_Value_1M_P50
  FROM tav2_bq.ticker_prune AS t
  INNER JOIN rebal_dates rdd ON t.time = rdd.rd
  WHERE t.PB > 0 AND t.PE > 0 AND t.PE < 100
    AND t.ROIC5Y >= 0.08 AND t.FSCORE >= 5
    AND t.Trading_Value_1M_P50 >= 10e9
    AND t.profit_1M IS NOT NULL
),
ranked AS (
  SELECT *,
    PERCENT_RANK() OVER (PARTITION BY time ORDER BY PB ASC) AS pbr,
    PERCENT_RANK() OVER (PARTITION BY time ORDER BY PE ASC) AS per
  FROM universe
),
scored AS (
  SELECT *,
    PERCENT_RANK() OVER (PARTITION BY time ORDER BY pbr+per ASC) AS vrank
  FROM ranked
),
picks AS (SELECT * FROM scored WHERE vrank <= 0.20),
-- staleness: latest financial release on/before rebalance date
rel AS (
  SELECT p.time, p.ticker, MAX(f.Release_Date) AS last_rel
  FROM (SELECT DISTINCT time, ticker FROM picks) p
  JOIN tav2_bq.ticker_financial f
    ON f.ticker = p.ticker AND f.Release_Date <= p.time
  GROUP BY 1, 2
)
SELECT
  r.anchor,
  r.rd                                  AS rebal_date,
  COUNT(*)                              AS n_picks,
  AVG(p.profit_1M)                      AS ret_pct,
  AVG(DATE_DIFF(p.time, rl.last_rel, DAY)) AS stale_days,
  STRING_AGG(p.ticker ORDER BY p.pbr+p.per LIMIT 6) AS tickers
FROM rebal r
JOIN picks p ON p.time = r.rd
LEFT JOIN rel rl ON rl.time = p.time AND rl.ticker = p.ticker
GROUP BY 1, 2
ORDER BY 1, 2
"""

df = bq(MAIN, "anchor backtest panel")
if df.empty: print("ERROR"); sys.exit(1)

df['rebal_date'] = pd.to_datetime(df['rebal_date'])
df['ret'] = df['ret_pct'] / 100.0
df['month'] = df['rebal_date'].dt.month
df['moq'] = ((df['month'] - 1) % 3) + 1   # month-of-quarter of the rebal month

ANCHOR_LBL = {1:'day 1', 5:'day 5', 10:'day 10', 15:'day 15',
              20:'day 20', 25:'day 25', 99:'EOM'}

print(f"\n  {'Anchor':>8s}  {'n_mo':>5s}  {'CAGR':>7s}  {'Sharpe':>7s}  {'MaxDD':>7s}  "
      f"{'med/mo':>7s}  {'win%':>5s}  {'stale_d':>8s}")
print("  " + "-"*70)
anchor_stats = {}
for a in [1, 5, 10, 15, 20, 25, 99]:
    sub = df[df['anchor']==a].set_index('rebal_date').sort_index()
    m = ann(sub['ret'])
    med = sub['ret'].median()*100
    win = (sub['ret']>0).mean()*100
    stale = sub['stale_days'].mean()
    anchor_stats[a] = dict(sub=sub, **m, med=med, win=win, stale=stale)
    print(f"  {ANCHOR_LBL[a]:>8s}  {len(sub):5d}  {m['CAGR']:6.1f}%  {m['Sharpe']:7.2f}  "
          f"{m['MaxDD']:6.1f}%  {med:+6.2f}%  {win:4.0f}%  {stale:7.0f}d")

# Paired comparison vs EOM
print(f"\n  Paired delta vs EOM (same months):")
eom = anchor_stats[99]['sub']['ret']
for a in [1, 5, 10, 15, 20, 25]:
    s = anchor_stats[a]['sub']['ret']
    # align by month
    s_m  = s.copy();  s_m.index  = s_m.index.to_period('M')
    e_m  = eom.copy(); e_m.index = e_m.index.to_period('M')
    idx = s_m.index.intersection(e_m.index)
    d = s_m.loc[idx] - e_m.loc[idx]
    t = d.mean()/d.std()*np.sqrt(len(d)) if d.std()>0 else 0
    print(f"    {ANCHOR_LBL[a]:>7s} - EOM: {d.mean()*100:+.2f}%/mo  t={t:+.2f}  "
          f"win {((d>0).mean()*100):.0f}%")

# ════════════════════════════════════════════════════════════
# PART 3: Earnings-month effect — does freshness matter most in months 1,4,7,10?
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 3: By month-of-quarter (1 = earnings month: Jan/Apr/Jul/Oct)")
print("="*65)
print(f"\n  {'Anchor':>8s}  {'MoQ1 ret':>9s}  {'MoQ1 stale':>10s}  {'MoQ2 ret':>9s}  "
      f"{'MoQ3 ret':>9s}")
print("  " + "-"*55)
for a in [1, 5, 10, 15, 20, 25, 99]:
    sub = df[df['anchor']==a]
    parts = []
    stale1 = sub[sub['moq']==1]['stale_days'].mean()
    for moq in [1,2,3]:
        r = sub[sub['moq']==moq]['ret']
        parts.append(f"{r.mean()*100:+8.2f}%")
    print(f"  {ANCHOR_LBL[a]:>8s}  {parts[0]}  {stale1:9.0f}d  {parts[1]}  {parts[2]}")

# ════════════════════════════════════════════════════════════
# PART 4: Turnover check — does rebalancing right after earnings rotate more?
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 4: Pick turnover by anchor (avg % new names vs prior month)")
print("="*65)
for a in [1, 5, 99]:
    sub = df[df['anchor']==a].sort_values('rebal_date')
    prev = None; tos = []
    for _, row in sub.iterrows():
        cur = set(str(row['tickers']).split(','))
        if prev is not None and len(cur):
            tos.append(len(cur - prev)/len(cur))
        prev = cur
    print(f"  {ANCHOR_LBL[a]:>7s}: avg turnover {np.mean(tos)*100:.0f}%/mo")

# ════════════════════════════════════════════════════════════
# FIGURE
# ════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 11))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('Book C Rebalance Timing — Which Day of Month?\n'
             'Same signal (PB+PE rank, V4 gate), 7 anchor days, 2016-2026, profit_1M',
             fontsize=12, fontweight='bold', color='white', y=0.99)
dark='#161b22'; sp='#30363d'
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.36)
def sty(ax, t=""):
    ax.set_facecolor(dark); [s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e', labelsize=8)
    if t: ax.set_title(t, color='#e6edf3', fontsize=10, fontweight='bold', pad=7)

anchors_plot = [1, 5, 10, 15, 20, 25, 99]
lbls = [ANCHOR_LBL[a] for a in anchors_plot]

# R1C0: CAGR by anchor
ax1 = fig.add_subplot(gs[0, 0])
sty(ax1, 'CAGR by Rebalance Anchor')
cagrs = [anchor_stats[a]['CAGR'] for a in anchors_plot]
best_i = int(np.nanargmax(cagrs))
cols = ['#3fb950' if i==best_i else '#58a6ff' for i in range(len(cagrs))]
ax1.bar(lbls, cagrs, color=cols, alpha=0.85)
for i, v in enumerate(cagrs):
    ax1.text(i, v+0.2, f'{v:.1f}', ha='center', color='white', fontsize=9)
ax1.set_ylabel('CAGR %', color='#8b949e')
plt.setp(ax1.get_xticklabels(), rotation=30, ha='right')

# R1C1: Sharpe by anchor
ax2 = fig.add_subplot(gs[0, 1])
sty(ax2, 'Sharpe by Rebalance Anchor')
shs = [anchor_stats[a]['Sharpe'] for a in anchors_plot]
best_i2 = int(np.nanargmax(shs))
cols2 = ['#3fb950' if i==best_i2 else '#e8c547' for i in range(len(shs))]
ax2.bar(lbls, shs, color=cols2, alpha=0.85)
for i, v in enumerate(shs):
    ax2.text(i, v+0.01, f'{v:.2f}', ha='center', color='white', fontsize=9)
plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')

# R1C2: Data staleness by anchor
ax3 = fig.add_subplot(gs[0, 2])
sty(ax3, 'Avg Data Staleness at Rebalance\n(days since latest BCTC release)')
stales = [anchor_stats[a]['stale'] for a in anchors_plot]
ax3.bar(lbls, stales, color='#f97316', alpha=0.85)
for i, v in enumerate(stales):
    ax3.text(i, v+0.5, f'{v:.0f}d', ha='center', color='white', fontsize=9)
ax3.set_ylabel('days', color='#8b949e')
plt.setp(ax3.get_xticklabels(), rotation=30, ha='right')

# R2C0: Release day-of-month histogram (month 1 of quarter)
ax4 = fig.add_subplot(gs[1, 0])
sty(ax4, 'BCTC Release Day Distribution\n(month 1 of quarter)')
ax4.bar(m1.index, m1.values, color='#9467bd', alpha=0.85)
ax4.set_xlabel('day of month', color='#8b949e')
ax4.set_ylabel('n releases', color='#8b949e')

# R2C1: NAV comparison best vs EOM
ax5 = fig.add_subplot(gs[1, 1])
sty(ax5, 'Cumulative NAV: Best Anchor vs EOM')
for a, col, lw in [(99, '#58a6ff', 1.6),
                   (anchors_plot[best_i], '#3fb950', 2.0)]:
    s = anchor_stats[a]['sub']['ret'].dropna()
    nav = (1+s).cumprod()
    ax5.semilogy(nav.index, nav.values, color=col, lw=lw,
                 label=f"{ANCHOR_LBL[a]} (CAGR {anchor_stats[a]['CAGR']:.1f}%)")
ax5.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')

# R2C2: MoQ heatmap
ax6 = fig.add_subplot(gs[1, 2])
sty(ax6, 'Avg Monthly Return by Anchor x Month-of-Quarter')
mat = np.zeros((len(anchors_plot), 3))
for i, a in enumerate(anchors_plot):
    for j, moq in enumerate([1,2,3]):
        r = df[(df['anchor']==a)&(df['moq']==moq)]['ret']
        mat[i,j] = r.mean()*100
im = ax6.imshow(mat, aspect='auto', cmap='RdYlGn',
                vmin=-abs(mat).max(), vmax=abs(mat).max())
ax6.set_xticks(range(3)); ax6.set_xticklabels(['MoQ1\n(earnings)','MoQ2','MoQ3'], color='#8b949e', fontsize=8)
ax6.set_yticks(range(len(anchors_plot))); ax6.set_yticklabels(lbls, color='#8b949e', fontsize=8)
for i in range(len(anchors_plot)):
    for j in range(3):
        ax6.text(j, i, f'{mat[i,j]:+.1f}', ha='center', va='center',
                 color='black' if abs(mat[i,j])>abs(mat).max()*0.4 else 'white', fontsize=8)
plt.colorbar(im, ax=ax6, shrink=0.8)

out = WORKDIR + r"\book_c_rebal_timing.png"
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: book_c_rebal_timing.png")
plt.close()
print("DONE")
