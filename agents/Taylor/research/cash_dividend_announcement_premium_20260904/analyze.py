import pandas as pd, numpy as np
from scipy import stats

DEPOSIT_RATE = 0.068
IS_END = pd.Timestamp('2019-12-31')

df = pd.read_csv('raw_events.csv', parse_dates=['ex_date','t28','t15','t14','t1'])
n0 = len(df)
df = df.dropna(subset=['c28','c15','c14','c1','v28','v15','v14','v1'])
n1 = len(df)
df = df[(df[['c28','c15','c14','c1']] > 0).all(axis=1)]
print(f"dropped {n0-n1} rows for missing boundary price/index; dropped {n1-len(df)} more for zero/negative price (data error); N={len(df)}")

df['pre_ex_ret'] = df['c1']/df['c14'] - 1
df['baseline_ret'] = df['c15']/df['c28'] - 1
df['vnindex_pre_ex_ret'] = df['v1']/df['v14'] - 1
df['abnormal_return'] = df['pre_ex_ret'] - df['baseline_ret'] - df['vnindex_pre_ex_ret']

cash = df[df['grp']=='CASH'].copy()
stock = df[df['grp']=='STOCK_DIV'].copy()

cash['yield_ratio'] = (cash['div_vnd']/cash['c14']) / DEPOSIT_RATE
def bucket(y):
    if y > 1.0: return 'H'
    if y >= 0.5: return 'M'
    return 'L'
cash['bucket'] = cash['yield_ratio'].apply(bucket)

print("\n=== Sanity: yield_ratio distribution (CASH) ===")
print(cash['yield_ratio'].describe())
print(cash['bucket'].value_counts())

# outlier guard: yield_ratio should realistically be <10 (1000% dividend yield would be data error)
print("\nyield_ratio > 10:", (cash['yield_ratio']>10).sum(), "  yield_ratio <=0:", (cash['yield_ratio']<=0).sum())

def report_group(name, sub):
    n = len(sub)
    med = sub['abnormal_return'].median()
    if n >= 5:
        w = stats.wilcoxon(sub['abnormal_return'])
        wp = w.pvalue
    else:
        wp = np.nan
    print(f"{name}: N={n}, median_AR={med:.4%}, wilcoxon_p={wp}")
    return n, med, wp

print("\n=== FULL SAMPLE ===")
report_group("CASH (all)", cash)
report_group("STOCK_DIV (all)", stock)

print("\n=== H1: median ABNORMAL_RETURN of CASH > 0 (Wilcoxon vs 0) ===")
n_full, med_full, p_full = report_group("CASH full", cash)

print("\n=== H2: Spearman(yield_ratio, ABNORMAL_RETURN) ===")
rho, p2 = stats.spearmanr(cash['yield_ratio'], cash['abnormal_return'])
print(f"Spearman rho={rho:.4f}, p={p2:.4g}, N={len(cash)}")
# robustness: drop extreme yield_ratio outliers
cash_trim = cash[cash['yield_ratio']<=10]
rho_t, p2_t = stats.spearmanr(cash_trim['yield_ratio'], cash_trim['abnormal_return'])
print(f"[trimmed yield_ratio<=10] rho={rho_t:.4f}, p={p2_t:.4g}, N={len(cash_trim)}")

print("\n=== H3: median AR(H) > median AR(L), Mann-Whitney ===")
H = cash[cash['bucket']=='H']
L = cash[cash['bucket']=='L']
M = cash[cash['bucket']=='M']
for g,name in [(H,'H'),(M,'M'),(L,'L')]:
    print(f"  {name}: N={len(g)}, median_AR={g['abnormal_return'].median():.4%}")
if len(H)>=5 and len(L)>=5:
    u = stats.mannwhitneyu(H['abnormal_return'], L['abnormal_return'], alternative='greater')
    print(f"Mann-Whitney H>L: U={u.statistic}, p={u.pvalue:.4g}")

print("\n=== H_neg: STOCK_DIV control ===")
report_group("STOCK_DIV", stock)

print("\n=== CASH vs STOCK_DIV direct comparison (can we distinguish the cash effect?) ===")
u_cs = stats.mannwhitneyu(cash['abnormal_return'], stock['abnormal_return'], alternative='greater')
print(f"MWU CASH>STOCK_DIV: p={u_cs.pvalue:.4g}")
print(f"CASH median={cash['abnormal_return'].median():.4%}  STOCK_DIV median={stock['abnormal_return'].median():.4%}")
print(f"CASH mean={cash['abnormal_return'].mean():.4%}  STOCK_DIV mean={stock['abnormal_return'].mean():.4%}")

print("\n=== IS (<=2019) / OOS (>=2020) split ===")
for label, cond in [('IS', df['ex_date']<=IS_END), ('OOS', df['ex_date']>IS_END)]:
    sub_cash = cash[cash['ex_date'].isin(df[cond]['ex_date'])] if False else cash[ (cash['ex_date']<=IS_END) if label=='IS' else (cash['ex_date']>IS_END) ]
    n = len(sub_cash)
    med = sub_cash['abnormal_return'].median() if n else np.nan
    print(f"{label} CASH: N={n}, median_AR={med if n==0 else f'{med:.4%}'}")
    if n>=5:
        rho_s, p_s = stats.spearmanr(sub_cash['yield_ratio'], sub_cash['abnormal_return'])
        print(f"   Spearman rho={rho_s:.4f} p={p_s:.4g}")
    H_s = sub_cash[sub_cash['bucket']=='H']
    L_s = sub_cash[sub_cash['bucket']=='L']
    print(f"   H N={len(H_s)}, L N={len(L_s)}")
    if len(H_s)>=5 and len(L_s)>=5:
        u_s = stats.mannwhitneyu(H_s['abnormal_return'], L_s['abnormal_return'], alternative='greater')
        print(f"   MWU H>L p={u_s.pvalue:.4g}")

cash.to_csv('cash_events_analyzed.csv', index=False)
stock.to_csv('stock_div_events_analyzed.csv', index=False)
print("\nSaved cash_events_analyzed.csv, stock_div_events_analyzed.csv")
