"""(B) ROE thi truong tu SO LIEU CO BAN — gom ca doanh nghiep LO (NP am),
(C) ROE ro top-100 mcap (universe kich thuoc CO DINH -> so sanh xuyen thoi dai duoc),
(D) phan phoi cat ngang per-ticker hien tai.
"""
import pandas as pd, numpy as np
from scipy import stats

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_roe/'
OLD = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'
pd.set_option('display.width', 220)

# ---------------- (B) fundamental, includes loss-makers ----------------
f = pd.read_csv(EXP + 'fin_quarterly.csv', parse_dates=['time', 'Release_Date'])
f['np_ttm'] = f[['NP_P0', 'NP_P1', 'NP_P2', 'NP_P3']].sum(axis=1, min_count=4)
f['equity'] = f.BVPS * f.OShares
f = f[(f.equity > 0) & f.np_ttm.notna()].copy()
f['roe_i'] = f.np_ttm / f.equity
# PIT: dung Release_Date (ngay cong bo) chu khong phai ngay ket thuc quy
f['pit'] = f.Release_Date.fillna(f.time)
f = f[f.pit >= '2008-01-01'].sort_values('pit')

# tai moi ngay-cong-bo, lay ban ghi MOI NHAT cua tung ma (as-of) -> tong hop theo quy lich
f['yq'] = f.pit.dt.to_period('Q')
last = f.sort_values('pit').groupby(['ticker', 'yq']).tail(1)
# state as-of moi quy: forward-fill ban ghi gan nhat cua tung ma
piv_np = last.pivot_table(index='yq', columns='ticker', values='np_ttm', aggfunc='last').sort_index().ffill()
piv_eq = last.pivot_table(index='yq', columns='ticker', values='equity', aggfunc='last').sort_index().ffill()
piv_roe = last.pivot_table(index='yq', columns='ticker', values='roe_i', aggfunc='last').sort_index().ffill()
mask = piv_np.notna() & piv_eq.notna()
agg = pd.DataFrame({
    'n': mask.sum(axis=1),
    'np_sum': piv_np.where(mask).sum(axis=1),
    'eq_sum': piv_eq.where(mask).sum(axis=1),
})
agg['roe_fund'] = agg.np_sum / agg.eq_sum
agg['roe_med_ew'] = piv_roe.where(mask).median(axis=1)
agg['pct_loss'] = (piv_np.where(mask) < 0).sum(axis=1) / mask.sum(axis=1)
agg = agg[agg.n >= 50]
print('=== (B) ROE THI TRUONG TU SO LIEU CO BAN (GOM ca ma LO), theo quy ===')
print(agg.tail(16).assign(roe_fund=lambda x: (100 * x.roe_fund).round(2),
                          roe_med_ew=lambda x: (100 * x.roe_med_ew).round(2),
                          pct_loss=lambda x: (100 * x.pct_loss).round(1))[
    ['n', 'roe_fund', 'roe_med_ew', 'pct_loss']].to_string())
curB = agg.iloc[-1]
sB = agg.roe_fund
print('\nHIEN TAI (quy %s): ROE_fund = %.2f%%  | n=%d | %% ma lo = %.1f%%' % (agg.index[-1], 100 * curB.roe_fund, curB.n, 100 * curB.pct_loss))
for lab, sub in [('2008+', sB), ('10Y', sB[sB.index >= pd.Period('2016Q3', 'Q')]),
                 ('5Y', sB[sB.index >= pd.Period('2021Q3', 'Q')]), ('3Y', sB[sB.index >= pd.Period('2023Q3', 'Q')])]:
    print('  pctile %-6s N=%3d  %.1f   (mean %.2f%% median %.2f%% sd %.2f%%)' % (
        lab, len(sub), 100 * (sub < curB.roe_fund).mean(), 100 * sub.mean(), 100 * sub.median(), 100 * sub.std()))
agg.to_csv(EXP + 'roe_fund_quarterly.csv')

# ---------------- (C) top-100 mcap constant-size universe ----------------
o = pd.read_csv(OLD + 'agg_pepb.csv', parse_dates=['time'])
o['roe_t100'] = o.earn_t100 / o.book_t100
o['pe_t100'] = o.mcap_pe_t100 / o.earn_t100
o['pb_t100'] = o.mcap_pb_t100 / o.book_t100
o = o[o.time >= '2008-01-01']
curC = o.iloc[-1]
print('\n=== (C) ROE ro TOP-100 MCAP (universe kich thuoc co dinh) ===')
print('hien tai %s: ROE_t100 = %.2f%%  (PE_t100=%.2f PB_t100=%.3f)' % (curC.time.date(), 100 * curC.roe_t100, curC.pe_t100, curC.pb_t100))
end = curC.time
rows = []
for lab, m in [('full_2008+', o.time >= '2008-01-01'), ('last_10Y', o.time >= end - pd.DateOffset(years=10)),
               ('last_5Y', o.time >= end - pd.DateOffset(years=5)), ('last_3Y', o.time >= end - pd.DateOffset(years=3))]:
    s = o[m].roe_t100.dropna()
    q = s.quantile([.05, .25, .5, .75, .95])
    rows.append(dict(window=lab, N=len(s), cur=round(100 * curC.roe_t100, 2), pctile=round(100 * (s < curC.roe_t100).mean(), 1),
                     mean=round(100 * s.mean(), 2), median=round(100 * s.median(), 2), std=round(100 * s.std(), 2),
                     skew=round(stats.skew(s), 3), kurt=round(stats.kurtosis(s), 3),
                     p05=round(100 * q.iloc[0], 2), p25=round(100 * q.iloc[1], 2), p50=round(100 * q.iloc[2], 2),
                     p75=round(100 * q.iloc[3], 2), p95=round(100 * q.iloc[4], 2)))
T = pd.DataFrame(rows); print(T.to_string(index=False)); T.to_csv(EXP + 'roe_t100_desc.csv', index=False)
o[['time', 'roe_t100', 'pe_t100', 'pb_t100']].to_csv(EXP + 'roe_t100_daily.csv', index=False)

# ---------------- (D) cross-section hom nay ----------------
cs = last[last.yq == last.yq.max()] if False else None
# lay ban ghi tai chinh moi nhat cua tung ma tinh den hom nay
lastrec = f.sort_values('pit').groupby('ticker').tail(1)
lastrec = lastrec[lastrec.pit >= (f.pit.max() - pd.Timedelta(days=400))]
x = lastrec.roe_i
print('\n=== (D) PHAN PHOI CAT NGANG per-ticker, ban ghi tai chinh moi nhat (N=%d) ===' % len(x))
q = x.quantile([.05, .1, .25, .5, .75, .9, .95])
print('mean=%.2f%% median=%.2f%% sd=%.2f%% skew=%.2f kurt=%.2f  min=%.1f%% max=%.1f%%' % (
    100 * x.mean(), 100 * x.median(), 100 * x.std(), stats.skew(x), stats.kurtosis(x), 100 * x.min(), 100 * x.max()))
print('p05=%.2f p10=%.2f p25=%.2f p50=%.2f p75=%.2f p90=%.2f p95=%.2f (%%)' % tuple(100 * q))
print('%% ma LO (ROE<0) = %.1f%%   %% ROE>20%% = %.1f%%' % (100 * (x < 0).mean(), 100 * (x > .20).mean()))
xw = x.clip(-1, 1)
print('winsor +-100%%: mean=%.2f%% sd=%.2f%% skew=%.2f' % (100 * xw.mean(), 100 * xw.std(), stats.skew(xw)))

edges = np.arange(-20, 42, 2)
cnt, _ = np.histogram(100 * x, bins=np.concatenate([[-1e9], edges, [1e9]]))
labs = ['< -20'] + ['%d..%d' % (edges[i], edges[i + 1]) for i in range(len(edges) - 1)] + ['>= 40']
H = pd.DataFrame({'bucket_ROE_pct': labs, 'count': cnt})
H['pct'] = (100 * H['count'] / H['count'].sum()).round(1)
H['bar'] = H.pct.apply(lambda v: '#' * int(round(v)))
print('\n=== (D) HISTOGRAM cat ngang ROE per-ticker, hien tai (buoc 2pp) ===')
print(H.to_string(index=False))
H.to_csv(EXP + 'hist_roe_crosssection_now.csv', index=False)

# cat ngang gop 3 nam gan nhat de so hinh dang
p3 = f[f.pit >= f.pit.max() - pd.DateOffset(years=3)].roe_i
cnt3, _ = np.histogram(100 * p3, bins=np.concatenate([[-1e9], edges, [1e9]]))
H3 = pd.DataFrame({'bucket_ROE_pct': labs, 'count': cnt3})
H3['pct'] = (100 * H3['count'] / H3['count'].sum()).round(1)
H3['bar'] = H3.pct.apply(lambda v: '#' * int(round(v)))
print('\n=== (D2) HISTOGRAM cat ngang GOP 3 nam gan nhat (N=%d quan sat ma-quy) ===' % len(p3))
print(H3.to_string(index=False))
print('mean=%.2f%% median=%.2f%% sd=%.2f%% skew=%.2f  %%lo=%.1f%%' % (
    100 * p3.mean(), 100 * p3.median(), 100 * p3.std(), stats.skew(p3.clip(-1, 1)), 100 * (p3 < 0).mean()))
H3.to_csv(EXP + 'hist_roe_crosssection_3y.csv', index=False)
lastrec[['ticker', 'quarter', 'pit', 'np_ttm', 'equity', 'roe_i', 'ROE_Trailing']].to_csv(EXP + 'crosssection_now.csv', index=False)

# cross-check vs cot bao cao ROE_Trailing
cc = lastrec.dropna(subset=['ROE_Trailing'])
print('\nKIEM CHUNG roe_i (tu NP_TTM/equity) vs cot ROE_Trailing: N=%d corr=%.4f  median|diff|=%.4f' % (
    len(cc), cc.roe_i.corr(cc.ROE_Trailing), (cc.roe_i - cc.ROE_Trailing).abs().median()))
