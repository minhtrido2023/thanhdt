# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
"""
analyze_ticker_pattern.py
=========================
Mục tiêu: Tìm các ticker "structural underperformer" — tức là được hit bởi buy filter
nhưng profit vẫn tệ, KHÔNG phải vì filter sai mà vì bản chất ticker đó.

Bước 1: Tính per-ticker Pattern stats từ profile_hit.csv
         (thay thế cho Pattern_Median_Profit_3Y, Pattern_Winrate_3Y vì chưa có trong BQ)
Bước 2: Phân tích per-ticker vs per-filter — ticker nào luôn tệ bất kể filter nào?
Bước 3: Query BQ lấy fundamental của các ticker này (PE, PB, ROIC, FSCORE, ICB...)
Bước 4: Tìm threshold phân loại Good/Neutral/Bad ticker
Bước 5: Đề xuất pre-screening gate
"""

import subprocess, sys, os
import pandas as pd
import numpy as np
import json

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"
PROJECT = "lithe-record-440915-m9"
WIN = sys.platform == "win32"

# ─────────────────────────────────────────────
# BƯỚC 1: Load profile_hit.csv và tính Pattern stats
# ─────────────────────────────────────────────
print("=" * 70)
print("BƯỚC 1: Load profile_hit.csv và tính per-ticker stats")
print("=" * 70)

df = pd.read_csv(os.path.join(WORKDIR, "profile_hit.csv"), index_col=0, low_memory=False)
print(f"Total rows: {len(df):,} | Tickers: {df['ticker'].nunique()} | Filters: {df['filter'].nunique()}")
print(f"Filters: {sorted(df['filter'].unique())}")

# Chỉ dùng các rows có kết quả thực tế (không phải hold vô hạn)
df_real = df[df['Sell_profit'].notna()].copy()
print(f"\nRows có Sell_profit: {len(df_real):,}")

# Định nghĩa win = profit > 0 (sau phí ~0.5% thực tế)
df_real['is_win'] = df_real['Sell_profit'] > 0
df_real['is_good'] = df_real['Sell_profit'] > 5   # profit > 5% mới đáng
df_real['is_loss'] = df_real['Sell_profit'] < -5  # cutloss nặng

# ─────────────────────────────────────────────
# BƯỚC 2: Tổng hợp per-ticker across ALL filters
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("BƯỚC 2: Per-ticker aggregate stats (tất cả filters)")
print("=" * 70)

ticker_stats = df_real.groupby('ticker').agg(
    deal_count=('Sell_profit', 'count'),
    median_profit=('Sell_profit', 'median'),
    mean_profit=('Sell_profit', 'mean'),
    winrate=('is_win', 'mean'),
    good_rate=('is_good', 'mean'),
    loss_rate=('is_loss', 'mean'),
    profit_std=('Sell_profit', 'std'),
    min_profit=('Sell_profit', 'min'),
    max_profit=('Sell_profit', 'max'),
    filter_count=('filter', 'nunique'),
    filters_hit=('filter', lambda x: '|'.join(sorted(x.unique())))
).reset_index()

ticker_stats['sharpe_proxy'] = ticker_stats['mean_profit'] / (ticker_stats['profit_std'] + 1e-6)

print(f"\nTicker stats computed: {len(ticker_stats)} tickers")
print(f"\nPhân phối median_profit:")
print(ticker_stats['median_profit'].describe())
print(f"\nPhân phối winrate:")
print(ticker_stats['winrate'].describe())

# ─────────────────────────────────────────────
# BƯỚC 3: Phân loại Good / Neutral / Bad ticker
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("BƯỚC 3: Phân loại ticker theo Pattern performance")
print("=" * 70)

# Chỉ tin cậy khi có đủ deals
MIN_DEALS = 3

ts_valid = ticker_stats[ticker_stats['deal_count'] >= MIN_DEALS].copy()
print(f"Tickers có >= {MIN_DEALS} deals: {len(ts_valid)}")

# Phân loại theo cả 2 chiều: median_profit + winrate
def classify_ticker(row):
    if row['median_profit'] > 5 and row['winrate'] > 0.50:
        return 'GOOD'
    elif row['median_profit'] < -2 or (row['winrate'] < 0.35 and row['deal_count'] >= 5):
        return 'BAD'
    else:
        return 'NEUTRAL'

ts_valid['tier'] = ts_valid.apply(classify_ticker, axis=1)

tier_counts = ts_valid['tier'].value_counts()
print(f"\nTier distribution:")
for t, c in tier_counts.items():
    pct = c / len(ts_valid) * 100
    print(f"  {t}: {c} tickers ({pct:.1f}%)")

# ─────────────────────────────────────────────
# BƯỚC 4: Per-filter breakdown — ticker nào tệ nhất ở từng filter?
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("BƯỚC 4: Per-ticker × Per-filter performance matrix")
print("=" * 70)

filter_ticker = df_real.groupby(['filter', 'ticker']).agg(
    deals=('Sell_profit', 'count'),
    median_profit=('Sell_profit', 'median'),
    winrate=('is_win', 'mean')
).reset_index()

# Merge tier
filter_ticker = filter_ticker.merge(ts_valid[['ticker', 'tier', 'deal_count']], on='ticker', how='left')

print("\nTop 15 BAD tickers (median_profit thấp nhất, >= 3 deals):")
bad_filter = filter_ticker[filter_ticker['deals'] >= 3].sort_values('median_profit')
print(bad_filter[['filter', 'ticker', 'deals', 'median_profit', 'winrate', 'tier']].head(15).to_string(index=False))

# ─────────────────────────────────────────────
# BƯỚC 5: Tickers consistently bad across MULTIPLE filters
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("BƯỚC 5: Consistent underperformers (tệ qua nhiều filters khác nhau)")
print("=" * 70)

# Tính số filter mà ticker có median_profit < 0
ticker_neg_filters = filter_ticker[filter_ticker['deals'] >= 2].groupby('ticker').apply(
    lambda x: (x['median_profit'] < 0).sum()
).reset_index()
ticker_neg_filters.columns = ['ticker', 'neg_filter_count']

ticker_total_filters = filter_ticker[filter_ticker['deals'] >= 2].groupby('ticker').size().reset_index(name='total_filter_count')

ticker_consistency = ticker_neg_filters.merge(ticker_total_filters, on='ticker')
ticker_consistency['neg_ratio'] = ticker_consistency['neg_filter_count'] / ticker_consistency['total_filter_count']
ticker_consistency = ticker_consistency.merge(ts_valid[['ticker', 'deal_count', 'median_profit', 'winrate', 'tier']], on='ticker', how='left')

# Bad across multiple filters
consistent_bad = ticker_consistency[
    (ticker_consistency['neg_filter_count'] >= 2) &
    (ticker_consistency['median_profit'] < 0)
].sort_values(['neg_filter_count', 'median_profit'])

print(f"Tickers tệ qua >= 2 filters: {len(consistent_bad)}")
print(consistent_bad[['ticker', 'total_filter_count', 'neg_filter_count', 'neg_ratio',
                        'deal_count', 'median_profit', 'winrate', 'tier']].head(20).to_string(index=False))

# ─────────────────────────────────────────────
# BƯỚC 6: Query BQ fundamentals cho bad vs good tickers
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("BƯỚC 6: Query BQ fundamentals để phân biệt Good vs Bad tickers")
print("=" * 70)

bad_tickers = ts_valid[ts_valid['tier'] == 'BAD']['ticker'].tolist()
good_tickers = ts_valid[ts_valid['tier'] == 'GOOD']['ticker'].tolist()
print(f"Bad tickers: {len(bad_tickers)} | Good tickers: {len(good_tickers)}")
print(f"Sample bad: {bad_tickers[:10]}")
print(f"Sample good: {good_tickers[:10]}")

# Query BQ latest fundamentals
all_query_tickers = bad_tickers + good_tickers
ticker_list_sql = ", ".join([f'"{t}"' for t in all_query_tickers])

bq_sql = f"""
SELECT
  t.ticker,
  t.ICB_Code,
  t.PE,
  t.PB,
  t.ROIC_Trailing,
  t.ROE_Min3Y,
  t.ROE5Y,
  t.FSCORE,
  t.Debt_Eq_P0,
  t.NPM_P0,
  t.NP_P0,
  t.NP_P4,
  t.Risk_Rating,
  t.Volume_3M_P50,
  t.Price,
  t.CF_OA_5Y,
  t.OShares
FROM tav2_bq.ticker AS t
WHERE t.time = (
  SELECT MAX(t2.time) FROM tav2_bq.ticker AS t2 WHERE t2.ticker = t.ticker
)
AND t.ticker IN ({ticker_list_sql})
"""

bq_cmd = [BQ, "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
           "--format=csv", "--max_rows=500", bq_sql]

print("  Querying BQ...")
result = subprocess.run(bq_cmd, capture_output=True, text=True)

bq_path = os.path.join(WORKDIR, "ticker_fundamentals.csv")
if result.returncode == 0 and result.stdout.strip():
    lines = result.stdout.strip().split('\n')
    with open(bq_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    fund = pd.read_csv(bq_path)
    print(f"  BQ returned {len(fund)} rows")
else:
    print("  BQ error:", result.stderr[:200])
    fund = pd.DataFrame()

# ─────────────────────────────────────────────
# BƯỚC 7: Phân tích fundamental differences
# ─────────────────────────────────────────────
if len(fund) > 0:
    print("\n" + "=" * 70)
    print("BƯỚC 7: Fundamental comparison Good vs Bad tickers")
    print("=" * 70)

    fund = fund.merge(ts_valid[['ticker', 'tier', 'median_profit', 'winrate', 'deal_count']], on='ticker', how='left')
    fund_valid = fund[fund['tier'].isin(['GOOD', 'BAD'])].copy()

    num_cols = ['PE', 'PB', 'ROIC_Trailing', 'ROE_Min3Y', 'ROE5Y', 'FSCORE',
                'Debt_Eq_P0', 'NPM_P0', 'Risk_Rating']

    print(f"\n{'Column':<20} {'BAD median':>12} {'GOOD median':>12} {'Diff':>10} {'Signal'}")
    print("-" * 65)

    for col in num_cols:
        if col not in fund_valid.columns:
            continue
        bad_med = fund_valid[fund_valid['tier'] == 'BAD'][col].median()
        good_med = fund_valid[fund_valid['tier'] == 'GOOD'][col].median()
        if pd.isna(bad_med) or pd.isna(good_med):
            continue
        diff = good_med - bad_med
        # Signal direction (which is better)
        if col in ['ROIC_Trailing', 'ROE_Min3Y', 'ROE5Y', 'FSCORE', 'NPM_P0']:
            signal = "GOOD > BAD ✓" if diff > 0 else "GOOD < BAD ✗"
        elif col in ['PE', 'PB', 'Debt_Eq_P0', 'Risk_Rating']:
            signal = "GOOD < BAD ✓" if diff < 0 else "GOOD > BAD ✗"
        else:
            signal = ""
        print(f"  {col:<18} {bad_med:>12.2f} {good_med:>12.2f} {diff:>+10.2f}  {signal}")

    # ICB_Code distribution
    print("\n--- ICB_Code distribution ---")
    print("BAD tickers:")
    bad_icb = fund_valid[fund_valid['tier'] == 'BAD']['ICB_Code'].value_counts()
    print(bad_icb.to_string())
    print("\nGOOD tickers:")
    good_icb = fund_valid[fund_valid['tier'] == 'GOOD']['ICB_Code'].value_counts()
    print(good_icb.to_string())

    fund_valid.to_csv(os.path.join(WORKDIR, "ticker_tier_fundamentals.csv"), index=False)
    print(f"\nSaved: ticker_tier_fundamentals.csv")

# ─────────────────────────────────────────────
# BƯỚC 8: Per-filter analysis — filter nào bị "nhiễm" bad tickers nhiều nhất?
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("BƯỚC 8: Per-filter — bad ticker contamination rate")
print("=" * 70)

df_real_tier = df_real.merge(ts_valid[['ticker', 'tier']], on='ticker', how='left')

filter_contamination = df_real_tier.groupby('filter').apply(lambda g: pd.Series({
    'total_deals': len(g),
    'bad_ticker_deals': (g['tier'] == 'BAD').sum(),
    'good_ticker_deals': (g['tier'] == 'GOOD').sum(),
    'bad_pct': (g['tier'] == 'BAD').mean() * 100,
    'median_profit_all': g['Sell_profit'].median(),
    'median_profit_good_only': g[g['tier'] == 'GOOD']['Sell_profit'].median() if (g['tier'] == 'GOOD').any() else np.nan,
    'median_profit_bad_only': g[g['tier'] == 'BAD']['Sell_profit'].median() if (g['tier'] == 'BAD').any() else np.nan,
})).reset_index()

filter_contamination = filter_contamination.sort_values('bad_pct', ascending=False)
print(filter_contamination[[
    'filter', 'total_deals', 'bad_ticker_deals', 'bad_pct',
    'median_profit_all', 'median_profit_good_only', 'median_profit_bad_only'
]].to_string(index=False))

# ─────────────────────────────────────────────
# BƯỚC 9: Đề xuất pre-screening thresholds
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("BƯỚC 9: Đề xuất pre-screening gate dựa trên Pattern stats")
print("=" * 70)

# Tìm optimal threshold cho Pattern_Winrate
print("\nTối ưu threshold winrate (trên tập deals >= 3):")
results = []
for wr_thresh in [0.30, 0.35, 0.40, 0.45, 0.50]:
    for mp_thresh in [-5, -2, 0, 2, 5]:
        passed = ts_valid[
            (ts_valid['winrate'] >= wr_thresh) &
            (ts_valid['median_profit'] >= mp_thresh)
        ]
        blocked = ts_valid[~ts_valid.index.isin(passed.index)]

        # Đánh giá: bao nhiêu BAD ticker bị chặn đúng?
        if len(blocked) == 0 or len(passed) == 0:
            continue
        true_pos = (blocked['tier'] == 'BAD').sum()    # BAD bị chặn đúng
        false_pos = (blocked['tier'] == 'GOOD').sum()  # GOOD bị chặn sai
        passed_bad = (passed['tier'] == 'BAD').sum()   # BAD lọt qua
        passed_good = (passed['tier'] == 'GOOD').sum()

        # Precision: trong những bị chặn, bao nhiêu thực sự BAD?
        precision = true_pos / len(blocked) if len(blocked) > 0 else 0
        recall = true_pos / ts_valid[ts_valid['tier'] == 'BAD'].shape[0]
        f1 = 2 * precision * recall / (precision + recall + 1e-9)

        results.append({
            'wr_thresh': wr_thresh,
            'mp_thresh': mp_thresh,
            'tickers_blocked': len(blocked),
            'true_positive': true_pos,
            'false_positive': false_pos,
            'precision': precision,
            'recall': recall,
            'f1': f1
        })

results_df = pd.DataFrame(results).sort_values('f1', ascending=False)
print(results_df.head(10).to_string(index=False))

best = results_df.iloc[0]
print(f"\n>>> Best gate: Pattern_Winrate >= {best.wr_thresh:.2f} AND Pattern_Median_Profit >= {best.mp_thresh:.0f}%")
print(f"    F1={best.f1:.3f} | Precision={best.precision:.1%} | Recall={best.recall:.1%}")
print(f"    Chặn {best.tickers_blocked:.0f} tickers — trong đó {best.true_positive:.0f} BAD, {best.false_positive:.0f} GOOD bị block nhầm")

# ─────────────────────────────────────────────
# BƯỚC 10: Output cuối — danh sách BAD tickers cần avoid
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("BƯỚC 10: Danh sách BAD tickers (cần tránh)")
print("=" * 70)

bad_list = ts_valid[ts_valid['tier'] == 'BAD'].sort_values('median_profit')
print(bad_list[['ticker', 'deal_count', 'filter_count', 'filters_hit',
                'median_profit', 'winrate', 'loss_rate']].to_string(index=False))

# Và GOOD tickers để tham khảo
print("\n" + "=" * 70)
print("GOOD tickers (ưu tiên cao):")
print("=" * 70)
good_list = ts_valid[ts_valid['tier'] == 'GOOD'].sort_values('median_profit', ascending=False)
print(good_list[['ticker', 'deal_count', 'filter_count', 'filters_hit',
                 'median_profit', 'winrate', 'good_rate']].head(30).to_string(index=False))

# Save full results
ts_valid.to_csv(os.path.join(WORKDIR, "ticker_pattern_stats.csv"), index=False)
print(f"\nSaved: ticker_pattern_stats.csv ({len(ts_valid)} tickers)")

# ─────────────────────────────────────────────
# BƯỚC 11: Validation — nếu áp gate, profit cải thiện bao nhiêu?
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("BƯỚC 11: Validate impact nếu dùng pre-screening gate")
print("=" * 70)

wr_gate = float(best.wr_thresh)
mp_gate = float(best.mp_thresh)

# Tickers pass gate
pass_gate = set(ts_valid[
    (ts_valid['winrate'] >= wr_gate) & (ts_valid['median_profit'] >= mp_gate)
]['ticker'].tolist())

df_pass = df_real[df_real['ticker'].isin(pass_gate)]
df_block = df_real[~df_real['ticker'].isin(pass_gate)]

print(f"\nGate: Pattern_Winrate >= {wr_gate} AND Pattern_Median_Profit >= {mp_gate}%")
print(f"  Tickers pass: {len(pass_gate)} | Deals: {len(df_pass):,}")
print(f"  Tickers blocked: {df['ticker'].nunique() - len(pass_gate)} | Deals: {len(df_block):,}")

print(f"\n  Without gate - median profit: {df_real['Sell_profit'].median():.2f}%  winrate: {df_real['is_win'].mean():.1%}")
print(f"  With gate    - median profit: {df_pass['Sell_profit'].median():.2f}%  winrate: {df_pass['is_win'].mean():.1%}")
print(f"  Improvement: {df_pass['Sell_profit'].median() - df_real['Sell_profit'].median():+.2f}pp profit | {df_pass['is_win'].mean() - df_real['is_win'].mean():+.1%} winrate")

# Per-filter improvement
print(f"\nPer-filter improvement with gate:")
print(f"{'Filter':<20} {'Before':>10} {'After':>10} {'Delta':>8} {'Deals Before':>14} {'Deals After':>12}")
print("-" * 80)
for filt in sorted(df_real['filter'].unique()):
    before = df_real[df_real['filter'] == filt]['Sell_profit'].median()
    after = df_pass[df_pass['filter'] == filt]['Sell_profit'].median() if len(df_pass[df_pass['filter'] == filt]) > 0 else np.nan
    n_before = (df_real['filter'] == filt).sum()
    n_after = (df_pass['filter'] == filt).sum()
    delta = (after - before) if not pd.isna(after) else np.nan
    flag = " ✓" if delta and delta > 0 else (" ✗" if delta and delta < -1 else "")
    print(f"  {filt:<18} {before:>10.2f} {after:>10.2f} {delta:>+8.2f}{flag}  {n_before:>10,} → {n_after:>10,}")

print("\nDone!")
