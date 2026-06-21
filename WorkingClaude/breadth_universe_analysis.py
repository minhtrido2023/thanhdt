"""
Quantify impact of breadth universe mismatch on 5-state decisions.

Universes:
  1. Production: ticker_prune (~500, mixed HSX/HNX/UPCOM)
  2. Strict HSX: tickers VNINDEX represents
  3. All tickers (~1272): what my research scripts used by mistake

Tests:
  - Correlation of daily breadth across universes
  - Sub-period stability
  - State machine sensitivity: would r_score change materially?
"""
import pandas as pd
import numpy as np
import subprocess, io

def bq(sql):
    return pd.read_csv(io.StringIO(subprocess.run(
        ['bq','query','--use_legacy_sql=false','--project_id=lithe-record-440915-m9',
         '--format=csv','--max_rows=10000','-q', sql],
        capture_output=True, text=True, shell=True).stdout))

print("Pulling 3 breadth versions...")

# v1: production breadth from ticker_prune (current 5-state input)
br_prune = pd.read_csv('breadth_data.csv', parse_dates=['time'])
br_prune.columns = ['time','br_prune']
print(f"  v1 ticker_prune: n={len(br_prune)}")

# v2: HSX-only breadth (we approximate via VN30 + extended HSX)
# Best approximation: ticker_prune MINUS known HNX/UPCOM tickers
hnx_upcom = ("('ACB','CEO','DBC','HUT','IDC','LAS','MBS','NTP','NVB','PHP','PLC','PSI',"
             "'PVI','PVS','SHB','SHS','TIG','TJC','TNG','TVC','VC3','VCS','VGC','VGS',"
             "'VND','VNR','ACV','BCM','BSR','FRT','GVR','LTG','MCH','MML','MPC','MSR',"
             "'OIL','SBS','VEA','VEF','VGI','VTP')")
sql_hsx = ('SELECT t.time, ROUND(SUM(CASE WHEN t.Close > t.MA50 THEN 1 ELSE 0 END)/COUNT(*), 4) AS br_hsx '
           'FROM tav2_bq.ticker AS t '
           'WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) '
           f'AND t.ticker NOT IN {hnx_upcom} '
           "AND t.time >= '2014-01-01' "
           'AND t.MA50 IS NOT NULL AND t.Close IS NOT NULL '
           'GROUP BY t.time ORDER BY t.time')
br_hsx = bq(sql_hsx)
br_hsx['time'] = pd.to_datetime(br_hsx['time'])
print(f"  v2 ticker_prune\\HNX/UPCOM (HSX-proxy): n={len(br_hsx)}")

# v3: ALL tickers (what my research used incorrectly)
sql_all = ('SELECT t.time, ROUND(SUM(CASE WHEN t.Close > t.MA50 THEN 1 ELSE 0 END)/COUNT(*), 4) AS br_all '
           'FROM tav2_bq.ticker AS t '
           "WHERE t.ticker != 'VNINDEX' AND t.time >= '2014-01-01' "
           'AND t.MA50 IS NOT NULL AND t.Close IS NOT NULL '
           'GROUP BY t.time ORDER BY t.time')
br_all = bq(sql_all)
br_all['time'] = pd.to_datetime(br_all['time'])
print(f"  v3 all tickers (research mistake): n={len(br_all)}")

# Merge
df = br_prune.merge(br_hsx, on='time', how='inner').merge(br_all, on='time', how='inner')
print(f"\nJoined {len(df)} sessions, {df['time'].min().date()} -> {df['time'].max().date()}")

# Correlations
print("\n=== Pearson correlations ===")
print(df[['br_prune','br_hsx','br_all']].corr().round(4))

# Daily diff statistics
df['diff_prune_hsx'] = df['br_prune'] - df['br_hsx']
df['diff_prune_all'] = df['br_prune'] - df['br_all']
df['diff_hsx_all']   = df['br_hsx']   - df['br_all']
print("\n=== Daily breadth difference (pp) ===")
print(f"  prune - hsx:  mean={df['diff_prune_hsx'].mean()*100:+.2f}pp  std={df['diff_prune_hsx'].std()*100:.2f}pp  max abs={df['diff_prune_hsx'].abs().max()*100:.2f}pp")
print(f"  prune - all:  mean={df['diff_prune_all'].mean()*100:+.2f}pp  std={df['diff_prune_all'].std()*100:.2f}pp  max abs={df['diff_prune_all'].abs().max()*100:.2f}pp")
print(f"  hsx - all:    mean={df['diff_hsx_all'].mean()*100:+.2f}pp  std={df['diff_hsx_all'].std()*100:.2f}pp  max abs={df['diff_hsx_all'].abs().max()*100:.2f}pp")

# Worst divergence days
print("\n=== Days with largest |prune - hsx| divergence ===")
top = df.reindex(df['diff_prune_hsx'].abs().sort_values(ascending=False).head(10).index)
print(top[['time','br_prune','br_hsx','diff_prune_hsx']].round(3).to_string(index=False))

# Sub-period stats
df['year'] = df['time'].dt.year
print("\n=== Mean diff by year (pp) ===")
yearly = df.groupby('year').agg(
    mean_pp=('diff_prune_hsx', lambda s: s.mean()*100),
    std_pp=('diff_prune_hsx', lambda s: s.std()*100),
    n=('diff_prune_hsx','count')
).round(2)
print(yearly)

# Impact on f_Breadth factor in r_score
# In production, breadth has 12% weight in r_score. So 1pp change in breadth
# rank approximately moves r_score by 0.12 * (change in rank).
# Rank shift estimation:
df['rank_prune'] = df['br_prune'].rolling(252, min_periods=60).rank(pct=True)
df['rank_hsx']   = df['br_hsx'].rolling(252, min_periods=60).rank(pct=True)
df['rank_diff']  = df['rank_prune'] - df['rank_hsx']
print(f"\n=== Expanding rank difference (252d rolling rank) ===")
print(f"  mean |rank diff|: {df['rank_diff'].abs().mean():.4f}")
print(f"  std rank diff:    {df['rank_diff'].std():.4f}")
print(f"  max |rank diff|:  {df['rank_diff'].abs().max():.4f}")
print(f"  Expected r_score shift (12% weight): ~{df['rank_diff'].abs().mean()*0.12:.4f}")

# How often would the rank flip materially (>10pp)?
big_flip = (df['rank_diff'].abs() > 0.10).sum()
print(f"  Sessions with |rank diff| > 10pp: {big_flip} ({100*big_flip/len(df):.1f}%)")

# Save for further use
df.to_csv('breadth_universe_comparison.csv', index=False)
print("\nSaved: breadth_universe_comparison.csv")
