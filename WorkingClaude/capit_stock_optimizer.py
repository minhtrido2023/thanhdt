"""
capit_stock_optimizer.py — Optimize capitulation stock selection
================================================================
Q: "Ngoài PB, feature nào predict bounce mạnh nhất trong CRISIS?"

Method:
  1. Lấy tất cả CRISIS dates từ DT5G (state=1)
  2. Join ticker_prune để lấy features + profit_3M (T+60 = hold 60d)
  3. IC (Spearman rank corr) cho từng feature vs profit_3M
  4. Quintile analysis → ai bounce mạnh nhất?
  5. Composite score optimizer: base (PB_z) vs combinations
  6. Deep-dive: phân biệt "bounce mạnh" vs "stay-down trap"
"""
import sys, os
try: sys.stdout.reconfigure(encoding='utf-8')
except: pass
import subprocess
import numpy as np
import pandas as pd
try:
    from scipy import stats as sp_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
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
    if r.returncode != 0: print(f"  ERROR: {r.stderr[:200]}")
    return df

# ════════════════════════════════════════════════════════════
# PART 1: Pull CRISIS-period features + outcomes from BQ
# ════════════════════════════════════════════════════════════
print("="*65)
print("CAPITULATION STOCK OPTIMIZER — Feature Analysis")
print("="*65)

PULL_SQL = """
WITH
-- All CRISIS dates (DT5G state=1)
crisis_dates AS (
  SELECT s.time
  FROM tav2_bq.vnindex_5state_dt5g_live AS s
  WHERE s.state = 1
),
-- Breadth on each CRISIS date (% of prune universe above MA200)
breadth_daily AS (
  SELECT
    t.time,
    SAFE_DIVIDE(COUNTIF(t.Close > t.MA200), COUNT(*)) AS breadth_pct
  FROM tav2_bq.ticker_prune AS t
  INNER JOIN crisis_dates c ON t.time = c.time
  WHERE t.MA200 IS NOT NULL AND t.Trading_Value_1M_P50 >= 5e9
  GROUP BY t.time
),
-- Stock features on CRISIS dates (liquid, non-null outcome)
feat AS (
  SELECT
    t.time,
    t.ticker,
    t.ICB_Code,
    -- Forward return outcome (T+60 = capitulation hold period)
    t.profit_3M                                                  AS fwd60d,
    -- Valuation
    SAFE_DIVIDE(t.PB - t.PB_MA5Y, t.PB_SD5Y)                   AS pb_z,
    t.PB,
    t.PE,
    -- Technical: oversoldness
    t.D_RSI,
    t.D_CMF,
    t.C_L1M,   -- 0=at recent 1M low, 1=at 1M high (lower=more oversold)
    t.C_L1W,
    t.PC_6M,   -- 6M return (negative=big dip)
    t.D_CMB,
    t.D_CMB_XFast,   -- periods since crossed fast line; 0=just crossed=fresh signal
    -- Quality
    t.ROIC5Y,
    t.FSCORE,
    t.ROE_Min5Y,
    t.CF_OA_P0,
    -- Risk/beta proxy
    t.Risk_Rating,   -- composite Beta+Dev bins
    -- Historical pattern
    t.Pattern_Median_Profit_3Y,
    t.Pattern_Winrate_3Y,
    t.Pattern_Deal_Count_3Y,
    -- Distance from extremes
    t.ID_LO_3Y,    -- sessions since 3Y low (0=at 3Y low)
    t.ID_HI_3Y,    -- sessions since 3Y high
    -- Money flow
    t.D_MFI,
    -- Liquidity
    t.Trading_Value_1M_P50 / 1e9                                AS liq_B,
    b.breadth_pct
  FROM tav2_bq.ticker_prune AS t
  INNER JOIN crisis_dates c ON t.time = c.time
  LEFT JOIN breadth_daily b ON t.time = b.time
  WHERE t.profit_3M IS NOT NULL
    AND t.Trading_Value_1M_P50 >= 10e9
    AND t.PB  > 0  AND t.PB  < 20
    AND t.PE  > 0  AND t.PE  < 100
    AND t.PB_MA5Y IS NOT NULL AND t.PB_SD5Y > 0
    AND t.D_RSI IS NOT NULL
    AND t.C_L1M IS NOT NULL
)
SELECT * FROM feat
ORDER BY time, ticker
"""

df = bq(PULL_SQL, "CRISIS features + profit_3M from ticker_prune")
if df.empty:
    print("  ERROR: empty result"); import sys; sys.exit(1)

df['time'] = pd.to_datetime(df['time'])
print(f"\n  Date range: {df['time'].min().date()} -> {df['time'].max().date()}")
print(f"  CRISIS sessions: {df['time'].nunique()}  |  Stock-days: {len(df):,}")
print(f"  Unique tickers: {df['ticker'].nunique()}")
print(f"  Breadth range: {df['breadth_pct'].min():.2f} -> {df['breadth_pct'].max():.2f}")

# fwd60d is in % — convert
df['fwd60d'] = df['fwd60d'] / 100.0

# Quality gate filter (same as capitulation playbook v2)
df_q = df[
    (df['ROIC5Y'] >= 0.08) & (df['FSCORE'] >= 5) &
    (df['ROE_Min5Y'] >= 0.08)
].copy()
print(f"\n  After quality gate (ROIC5Y>=8%, FSCORE>=5, ROE_Min5Y>=8%): {len(df_q):,} obs / {df_q['ticker'].nunique()} tickers")

# Washout subset (breadth <= 30% = genuine panic)
df_wash = df_q[df_q['breadth_pct'] <= 0.30].copy()
print(f"  After washout (breadth<=30%): {len(df_wash):,} obs")

# ════════════════════════════════════════════════════════════
# PART 2: IC analysis — which feature best predicts bounce?
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 2: INFORMATION COEFFICIENT (Spearman rank corr vs fwd60d)")
print("="*65)

FEATURES = {
    # Oversoldness (expect: negative = lower = more bounce)
    'pb_z':       ('Valuation',    'PB vs 5Y history (z-score)', -1),
    'PB':         ('Valuation',    'Price-to-Book raw', -1),
    'D_RSI':      ('Technical',    'RSI daily (0-1)', -1),
    'C_L1M':      ('Technical',    'Close/Lowest 1M (0=at low)', -1),
    'C_L1W':      ('Technical',    'Close/Lowest 1W (0=at low)', -1),
    'PC_6M':      ('Technical',    '6M price change (neg=dip)', -1),
    # Quality (expect: positive)
    'ROIC5Y':     ('Quality',      'ROIC 5Y', +1),
    'FSCORE':     ('Quality',      'Piotroski F-score', +1),
    'ROE_Min5Y':  ('Quality',      'ROE floor 5Y', +1),
    'CF_OA_P0':   ('Quality',      'Operating CF/Assets', +1),
    # Pattern history (expect: positive)
    'Pattern_Median_Profit_3Y': ('Pattern', 'Historical median bounce', +1),
    'Pattern_Winrate_3Y':       ('Pattern', 'Historical win rate', +1),
    # Risk/beta (expect: positive bounce, negative in drawdown)
    'Risk_Rating':('Risk',         'Beta+Dev composite', +1),
    # Money flow
    'D_CMF':      ('MFI',          'CMF (money flow)', +1),
    'D_MFI':      ('MFI',          'MFI index', +1),
    # CMB signal
    'D_CMB':      ('CMB',          'CMB composite', -1),
    'D_CMB_XFast':('CMB',          'CMB crossed fast (0=fresh)', -1),
    # Distance from extremes
    'ID_LO_3Y':   ('Extreme',      'Sessions since 3Y low (0=fresh low)', -1),
}

results = []
for feat, (cat, desc, expected_sign) in FEATURES.items():
    for name, data in [('all_crisis', df_q), ('washout', df_wash)]:
        sub = data[[feat, 'fwd60d']].dropna()
        if len(sub) < 30: continue
        if HAS_SCIPY:
            rho, pval = sp_stats.spearmanr(sub[feat], sub['fwd60d'])
        else:
            rho = sub[[feat,'fwd60d']].dropna().corr(method='spearman').iloc[0,1]
            n_sp = len(sub)
            t_s = rho*np.sqrt((n_sp-2)/(1-rho**2+1e-9)) if abs(rho)<1 else 0
            # approximate p-value via normal for large n
            pval = 2*(1 - 0.5*(1+np.sign(t_s)*min(abs(t_s)/np.sqrt(n_sp),0.999)))
        n = len(sub)
        t_stat = rho * np.sqrt((n-2)/(1-rho**2)) if abs(rho) < 1 else np.nan
        # Directional IC (flip if expected negative)
        ic_dir = rho * expected_sign
        results.append(dict(feature=feat, category=cat, desc=desc,
                            subset=name, IC=rho, IC_dir=ic_dir,
                            pval=pval, t_stat=t_stat, n=n,
                            expected_sign=expected_sign))

ic = pd.DataFrame(results)
ic_all = ic[ic['subset']=='all_crisis'].sort_values('IC_dir', ascending=False)
ic_wash = ic[ic['subset']=='washout'].sort_values('IC_dir', ascending=False)

print(f"\n  {'Feature':26s}  {'Cat':9s}  {'IC(all)':>8s}  {'IC(wash)':>8s}  {'t-stat':>7s}  Sig")
print("  " + "-"*75)
ic_m = ic_all.set_index('feature').join(
    ic_wash.set_index('feature')[['IC_dir','pval']].rename(columns={'IC_dir':'IC_dir_w','pval':'pval_w'}))
for _, row in ic_m.sort_values('IC_dir', ascending=False).iterrows():
    sig = "**" if row['pval']<0.01 else ("*" if row['pval']<0.05 else "")
    ic_w_str = f"{row['IC_dir_w']:+.3f}" if not np.isnan(row.get('IC_dir_w',np.nan)) else "  n/a "
    print(f"  {row.name:26s}  {row['category']:9s}  {row['IC_dir']:+.3f}    {ic_w_str}"
          f"    {row['t_stat']:+6.2f}  {sig}")

# ════════════════════════════════════════════════════════════
# PART 3: Quintile analysis — bounce by factor bucket
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 3: QUINTILE ANALYSIS — bounce by factor (washout subset)")
print("="*65)

# Key features to investigate in detail
KEY_FEATS = ['pb_z', 'D_RSI', 'C_L1M', 'PC_6M', 'Risk_Rating',
             'Pattern_Median_Profit_3Y', 'ROIC5Y', 'D_CMF']

quintile_data = {}  # feat -> dict(q -> stats)

for feat in KEY_FEATS:
    sub = df_wash[[feat, 'fwd60d', 'ticker']].dropna()
    if len(sub) < 50: sub = df_q[[feat, 'fwd60d', 'ticker']].dropna()
    if len(sub) < 20: continue
    try:
        sub['q'] = pd.qcut(sub[feat], q=5, labels=[1,2,3,4,5], duplicates='drop')
    except ValueError:
        sub['q'] = pd.qcut(sub[feat].rank(method='first'), q=5, labels=[1,2,3,4,5])
    stats = sub.groupby('q', observed=True)['fwd60d'].agg([
        ('med', 'median'),
        ('mean', 'mean'),
        ('win', lambda x: (x>0).mean()),
        ('p10', lambda x: np.percentile(x, 10)),
        ('n', 'count')
    ]).reset_index()
    quintile_data[feat] = stats

    print(f"\n  {feat} (lower Q1 = lower value)")
    print(f"  {'Q':3s}  {'Median':>8s}  {'Win%':>6s}  {'P10':>8s}  {'n':>5s}")
    for _, row in stats.iterrows():
        expected = FEATURES[feat][2]
        best = "<<" if (expected<0 and row['q']==1) or (expected>0 and row['q']==5) else ""
        print(f"  Q{int(row['q'])}   {row['med']*100:+7.1f}%   {row['win']*100:4.0f}%  "
              f"{row['p10']*100:+7.1f}%  {int(row['n']):5d}  {best}")

# ════════════════════════════════════════════════════════════
# PART 4: COMPOSITE SCORE — compare combinations
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 4: COMPOSITE SCORE — base vs optimized combinations")
print("="*65)

def eval_score(data, score_col, n_top=5, label=""):
    """For each date, pick top n_top by score_col, compute EW return."""
    rets = []
    for dt, g in data.groupby('time'):
        g_valid = g.dropna(subset=[score_col, 'fwd60d'])
        if len(g_valid) < 3: continue
        top = g_valid.nsmallest(n_top, score_col) if score_col.endswith('_neg') \
              else g_valid.nlargest(n_top, score_col)
        rets.append({'time': dt, 'ret': top['fwd60d'].mean(),
                     'n': len(top), 'tickers': ','.join(top['ticker'].tolist()[:5])})
    if not rets: return pd.DataFrame()
    r = pd.DataFrame(rets).set_index('time')
    ann_ret = r['ret'].mean() * 12
    median_r = r['ret'].median()
    win = (r['ret'] > 0).mean()
    # per-event stats
    ev_med = r['ret'].median()
    ev_p10 = r['ret'].quantile(0.10)
    ev_p90 = r['ret'].quantile(0.90)
    if label:
        print(f"  {label:40s}  med/event {ev_med*100:+5.1f}%  "
              f"win {win*100:3.0f}%  P10 {ev_p10*100:+5.1f}%  "
              f"P90 {ev_p90*100:+5.1f}%  n={len(r)}")
    return r

# Build composite scores
sub = df_wash.copy()  # washout only for live-equivalent

# Normalize features to 0-1 scale, invert where needed (lower=better)
def norm(s, invert=False):
    mn, mx = s.min(), s.max()
    if mx == mn: return pd.Series(0.5, index=s.index)
    v = (s - mn) / (mx - mn)
    return 1-v if invert else v

sub['s_pbz']    = norm(sub['pb_z'], invert=True)    # lower pb_z = more undervalued
sub['s_rsi']    = norm(sub['D_RSI'], invert=True)   # lower RSI = more oversold
sub['s_c1m']    = norm(sub['C_L1M'], invert=True)   # at recent low = more upside
sub['s_pc6m']   = norm(sub['PC_6M'], invert=True)   # big recent dip = bounce potential
sub['s_cmf']    = norm(sub['D_CMF'])                # positive CMF = accumulation
sub['s_risk']   = norm(sub['Risk_Rating'])          # high beta = big bounce
sub['s_patt']   = norm(sub['Pattern_Median_Profit_3Y'])  # good historical bounce
sub['s_roic']   = norm(sub['ROIC5Y'])               # quality
sub['s_mfi']    = norm(sub['D_MFI'])                # MFI
sub['s_lo3y']   = norm(sub['ID_LO_3Y'], invert=True)  # at 3Y low = fresh capitulation

# Base: pb_z only (current approach)
# Note: lower pb_z = more undervalued, so score = -pb_z (higher = better)
sub['score_base']   = sub['s_pbz']
# Add tech: pb_z + RSI + C_L1M
sub['score_tech']   = (sub['s_pbz'] * 0.4 + sub['s_rsi'] * 0.3 + sub['s_c1m'] * 0.3)
# Add pattern: pb_z + pattern history
sub['score_patt']   = (sub['s_pbz'] * 0.5 + sub['s_patt'] * 0.5)
# Add beta: pb_z + risk rating (high beta bounces harder in CRISIS)
sub['score_beta']   = (sub['s_pbz'] * 0.5 + sub['s_risk'] * 0.3 + sub['s_roic'] * 0.2)
# Full combo: pb_z + tech + pattern + beta
sub['score_full']   = (sub['s_pbz'] * 0.30 + sub['s_rsi'] * 0.15 + sub['s_c1m'] * 0.15 +
                       sub['s_patt'] * 0.20 + sub['s_risk'] * 0.10 + sub['s_cmf'] * 0.10)
# CMF-focus: quality + CMF + pb_z
sub['score_cmf']    = (sub['s_pbz'] * 0.40 + sub['s_cmf'] * 0.40 + sub['s_roic'] * 0.20)
# NEW: 3Y low proximity (stocks at 3Y lows bounce hardest?)
sub['score_lo3y']   = (sub['s_pbz'] * 0.35 + sub['s_lo3y'] * 0.40 + sub['s_roic'] * 0.25)

print("\n  Pick top 5 by each score | metric = per-CRISIS-event")
for score_col, label in [
    ('score_base',  'PB_z only (base)'),
    ('score_tech',  'PB_z + RSI + C_L1M'),
    ('score_patt',  'PB_z + Pattern_3Y'),
    ('score_beta',  'PB_z + Risk_Rating'),
    ('score_cmf',   'PB_z + CMF + ROIC'),
    ('score_lo3y',  'PB_z + 3Y-low + ROIC'),
    ('score_full',  'Full combo (6 signals)'),
]:
    eval_score(sub, score_col, n_top=5, label=label)

# ────────────────────────────────────────────────────────────
# Also test UNIVERSE (no quality gate) vs with gate
# ────────────────────────────────────────────────────────────
print(f"\n  --- Effect of quality gate (pb_z score, washout) ---")
sub_all_wash = df[df['breadth_pct'] <= 0.30].copy()
sub_all_wash['score_base'] = -sub_all_wash['pb_z']  # lower pb_z = better

# Recompute for quality-gated subset
sub_no_quality = df_wash.copy()  # already quality gated

# Also test: no quality gate
sub_all_wash2 = df[df['breadth_pct'] <= 0.30].copy()
sub_all_wash2['s_pbz'] = norm(sub_all_wash2['pb_z'], invert=True)
sub_all_wash2['score_base'] = sub_all_wash2['s_pbz']

eval_score(sub_all_wash2, 'score_base', n_top=5, label='No quality gate (pb_z only)')
eval_score(sub, 'score_base', n_top=5, label='Quality gate + pb_z (current)')

# ════════════════════════════════════════════════════════════
# PART 5: Deep-dive — what separates GREAT vs TRAP bounces
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 5: ANATOMY — GREAT bounce vs TRAP (washout, top-5)")
print("="*65)

sub_valid = sub.dropna(subset=['score_base', 'fwd60d'])
sub_valid['ret_decile'] = pd.qcut(sub_valid['fwd60d'], q=5, labels=['Q1-worst','Q2','Q3','Q4','Q5-best'])

print("\n  Average features for best (Q5) vs worst (Q1) bouncers:")
print(f"\n  {'Feature':30s}  {'Q1-worst':>10s}  {'Q5-best':>10s}  {'Diff':>8s}  Direction")
feat_cols = ['pb_z','D_RSI','C_L1M','PC_6M','ROIC5Y','FSCORE',
             'Risk_Rating','D_CMF','D_MFI','Pattern_Median_Profit_3Y',
             'ID_LO_3Y','CF_OA_P0']
for fc in feat_cols:
    if fc not in sub_valid.columns: continue
    q1 = sub_valid[sub_valid['ret_decile']=='Q1-worst'][fc].median()
    q5 = sub_valid[sub_valid['ret_decile']=='Q5-best'][fc].median()
    diff = q5 - q1
    sign = '+' if diff > 0 else '-'
    print(f"  {fc:30s}  {q1:+10.3f}  {q5:+10.3f}  {diff:+8.3f}  {sign}")

# Which tickers appear most as top performers?
print(f"\n  --- Most frequent tickers in Q5-best bounces ---")
top_tkrs = sub_valid[sub_valid['ret_decile']=='Q5-best']['ticker'].value_counts().head(15)
print("  ", top_tkrs.to_dict())

# ════════════════════════════════════════════════════════════
# PART 6: Sector analysis
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 6: SECTOR BOUNCE — which sectors bounce most in CRISIS?")
print("="*65)

sub_sec = df_q[['ICB_Code', 'fwd60d']].dropna()
# Map ICB to sector
SECTOR_MAP = {
    'CT': 'Consumer', 'NH': 'Finance',
    'BH': 'Realestate', 'CK': 'Securities'
}
# ICB_Code is numeric — group by range or use raw
sub_sec['icb_i'] = sub_sec['ICB_Code'].astype(str).str[:2]
icb_stats = sub_sec.groupby('icb_i')['fwd60d'].agg([
    ('med', 'median'), ('win', lambda x: (x>0).mean()),
    ('n', 'count'), ('p10', lambda x: x.quantile(0.1))
]).reset_index()
icb_stats = icb_stats[icb_stats['n'] >= 30].sort_values('med', ascending=False)
print(f"\n  {'ICB_2d':8s}  {'Median':>8s}  {'Win%':>6s}  {'P10':>8s}  {'n':>5s}")
for _, row in icb_stats.iterrows():
    print(f"  {str(row['icb_i']):8s}  {row['med']*100:+7.1f}%  "
          f"{row['win']*100:4.0f}%  {row['p10']*100:+7.1f}%  {int(row['n']):5d}")

# ════════════════════════════════════════════════════════════
# PART 7: RECOMMENDATION — optimal composite criteria
# ════════════════════════════════════════════════════════════
print("\n" + "="*65)
print("PART 7: RECOMMENDATION — optimal stock selection")
print("="*65)

# Compare: base vs best combo by event-level metrics
print("\n  Event-by-event backtest of top scores (washout periods):")
score_results = {}
for score_col, label in [
    ('score_base',  'A. PB_z only'),
    ('score_tech',  'B. PB_z+RSI+C_L1M'),
    ('score_patt',  'C. PB_z+Pattern'),
    ('score_lo3y',  'D. PB_z+3Y-low+ROIC'),
    ('score_full',  'E. Full combo'),
]:
    r = eval_score(sub, score_col, n_top=5)
    if r.empty: continue
    score_results[label] = r

print(f"\n  Delta vs base (PB_z only):")
base = score_results.get('A. PB_z only', pd.DataFrame())
if not base.empty:
    for label, r in score_results.items():
        if label == 'A. PB_z only': continue
        idx = base.index.intersection(r.index)
        diff_med = (r.loc[idx,'ret'].median() - base.loc[idx,'ret'].median())*100
        diff_win = (r.loc[idx,'ret']>0).mean() - (base.loc[idx,'ret']>0).mean()
        print(f"  {label}: med {diff_med:+.1f}pp  win {diff_win*100:+.1f}pp")

# ════════════════════════════════════════════════════════════
# FIGURES
# ════════════════════════════════════════════════════════════
n_feats = len([f for f in KEY_FEATS if f in quintile_data])
fig = plt.figure(figsize=(22, 16))
fig.patch.set_facecolor('#0d1117')
fig.suptitle('Capitulation Stock Optimizer — Feature Analysis\n'
             'CRISIS periods (DT5G state=1) | Quality gate | profit_3M = T+60',
             fontsize=12, fontweight='bold', color='white', y=0.99)
dark = '#161b22'; sp = '#30363d'

gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.50, wspace=0.38)

def sty(ax, t=""):
    ax.set_facecolor(dark); [s.set_color(sp) for s in ax.spines.values()]
    ax.tick_params(colors='#8b949e', labelsize=8)
    if t: ax.set_title(t, color='#e6edf3', fontsize=9, fontweight='bold', pad=6)

# ── R1: IC bar chart ──────────────────────────────────────
ax_ic = fig.add_subplot(gs[0, :])
sty(ax_ic, 'Information Coefficient (Spearman rho, directional) — All Crisis vs Washout')
feats_ord = ic_all.sort_values('IC_dir', ascending=False)
cats = feats_ord['category'].tolist()
cats_uniq = list(dict.fromkeys(cats))
cat_colors = {'Valuation':'#e8c547','Technical':'#58a6ff','Quality':'#3fb950',
              'Pattern':'#f97316','Risk':'#da7a0d','MFI':'#9467bd',
              'CMB':'#8c564b','Extreme':'#17becf'}
x = np.arange(len(feats_ord))
bars1 = ax_ic.bar(x - 0.2, feats_ord['IC_dir'].values, 0.38,
                  color=[cat_colors.get(c,'#aaa') for c in cats],
                  alpha=0.8, label='All Crisis')
# washout IC
ic_w_vals = ic_wash.set_index('feature').reindex(feats_ord['feature'])['IC_dir'].values
mask_w = ~np.isnan(ic_w_vals)
ax_ic.bar(x[mask_w] + 0.2, ic_w_vals[mask_w], 0.38,
          color=[cat_colors.get(cats[i],'#aaa') for i in range(len(cats)) if mask_w[i]],
          alpha=0.4, label='Washout only', hatch='///')
ax_ic.axhline(0, color='white', lw=0.8, alpha=0.4)
ax_ic.set_xticks(x)
ax_ic.set_xticklabels([f.replace('Pattern_','P_').replace('Median_Profit_3Y','Med3Y')
                        .replace('Winrate_3Y','Win3Y').replace('_Rating','_R')
                       for f in feats_ord['feature'].values],
                      rotation=30, ha='right', color='#8b949e', fontsize=8)
ax_ic.set_ylabel('Directional IC', color='#8b949e', fontsize=9)
ax_ic.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')
# Category legend
import matplotlib.patches as mpatches
cat_patches = [mpatches.Patch(color=c, label=k) for k,c in cat_colors.items()]
ax_ic.legend(handles=cat_patches, fontsize=8, facecolor='#1c2128',
             labelcolor='white', loc='lower right', ncol=4)

# ── R2: Quintile charts for top features ─────────────────
top4 = ['pb_z','D_RSI','C_L1M','Pattern_Median_Profit_3Y']
for i, feat in enumerate(top4):
    ax = fig.add_subplot(gs[1, i])
    sty(ax, f'{feat}\n(Q1=lowest value)')
    if feat not in quintile_data: continue
    stats = quintile_data[feat]
    qs = stats['q'].astype(int).tolist()
    meds = (stats['med']*100).tolist()
    wins = (stats['win']*100).tolist()
    colors_q = ['#d62728' if m<0 else '#3fb950' for m in meds]
    bars = ax.bar(qs, meds, color=colors_q, alpha=0.8, width=0.65, zorder=3)
    ax.axhline(0, color='white', lw=0.8, alpha=0.5)
    for q, m, w in zip(qs, meds, wins):
        ax.text(q, max(m, 0)+0.5, f'{w:.0f}%', ha='center',
                va='bottom', fontsize=7, color='white')
    ax.set_xlabel('Quintile', color='#8b949e', fontsize=8)
    ax.set_ylabel('Median fwd60d %', color='#8b949e', fontsize=8)
    ax.set_xticks(qs)
    ax.grid(axis='y', color=sp, alpha=0.4, lw=0.6)

# ── R3: Score comparison + Q1 vs Q5 anatomy ──────────────
ax_score = fig.add_subplot(gs[2, :2])
sty(ax_score, 'Composite Score Comparison (washout, top-5 per event)')
score_lbls = list(score_results.keys())
medians  = [r['ret'].median()*100 for r in score_results.values()]
win_rates= [(r['ret']>0).mean()*100 for r in score_results.values()]
p10s     = [r['ret'].quantile(0.1)*100 for r in score_results.values()]
xp = np.arange(len(score_lbls)); w = 0.28
ax_score.bar(xp-w, medians, w, color='#e8c547', label='Median', alpha=0.85)
ax_score.bar(xp,   p10s,   w, color='#d62728', label='P10 (downside)', alpha=0.85)
ax_score.bar(xp+w, win_rates, w, color='#3fb950', label='Win %', alpha=0.85)
ax_score.axhline(0, color='white', lw=0.8, alpha=0.5)
ax_score.set_xticks(xp)
ax_score.set_xticklabels([l[:20] for l in score_lbls], rotation=25, ha='right',
                          color='#8b949e', fontsize=8)
ax_score.set_ylabel('%', color='#8b949e', fontsize=9)
ax_score.legend(fontsize=9, facecolor='#1c2128', labelcolor='white')

# ── R3: Anatomy Q1 vs Q5 ─────────────────────────────────
ax_ana = fig.add_subplot(gs[2, 2:])
sty(ax_ana, 'Best vs Worst Bouncers — Median Feature Value')
feat_diff = {}
sub_v = sub.dropna(subset=['score_base', 'fwd60d'])
sub_v = sub_v.copy()
sub_v['rdec'] = pd.qcut(sub_v['fwd60d'], q=5, labels=[1,2,3,4,5])
disp_feats = ['pb_z','D_RSI','C_L1M','ROIC5Y','Risk_Rating','D_CMF',
              'Pattern_Median_Profit_3Y','ID_LO_3Y']
q1m = sub_v[sub_v['rdec']==1][disp_feats].median()
q5m = sub_v[sub_v['rdec']==5][disp_feats].median()
diff_norm = ((q5m - q1m) / (q1m.abs() + 0.001)).clip(-3, 3)
colors_d = ['#3fb950' if v>0 else '#d62728' for v in diff_norm]
yp = np.arange(len(disp_feats))
ax_ana.barh(yp, diff_norm.values, color=colors_d, alpha=0.85)
ax_ana.axvline(0, color='white', lw=0.8, alpha=0.5)
ax_ana.set_yticks(yp)
ax_ana.set_yticklabels([f.replace('Pattern_Median_Profit_3Y','Pattern').replace('Risk_Rating','RiskRating')
                         .replace('ID_LO_3Y','3Y_low_dist') for f in disp_feats],
                        color='#8b949e', fontsize=8)
ax_ana.set_xlabel('Normalized diff (Q5-best vs Q1-worst)', color='#8b949e', fontsize=9)

out = WORKDIR + r"\capit_stock_optimizer.png"
fig.savefig(out, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved: capit_stock_optimizer.png")
plt.close()

print("\nDONE")
