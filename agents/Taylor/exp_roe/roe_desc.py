"""ROE toan thi truong — thong ke mo ta + histogram.
Hai dinh nghia ROE thi truong duoc dung song song:
  (A) ROE_agg_ratio = Sum(earn)/Sum(book), earn=mcap/PE, book=BVPS*OShares
      -> chi gom ma co PE>0 (loai doanh nghiep lo). Bang dung PB_agg/PE_agg (dong nhat thuc dai so).
  (B) ROE_agg_fund  = Sum(NP_TTM)/Sum(equity) tu ticker_financial, GOM ca ma lo (NP am).
      -> khong bi bias song sot cua bo loc PE>0.
"""
import pandas as pd, numpy as np
from scipy import stats

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_roe/'
pd.set_option('display.width', 220)

# ---------- (A) daily ratio-derived ----------
d = pd.read_csv(EXP + 'roe_market_daily.csv', parse_dates=['time'])
d['roe_agg'] = d.earn_sum / d.book_sum          # book-weighted aggregate
d['pe_agg'] = d.mcap_sum / d.earn_sum
d['pb_agg'] = d.mcap_sum / d.book_sum
d['roe_median'] = d.roe_p50                      # equal-weighted median per-ticker
cur = d.iloc[-1]

print('=== (A) HIEN TAI %s ===' % cur.time.date())
print('n ma (PE>0 & PB>0)          = %d' % cur.n)
print('ROE gop (Sum earn/Sum book) = %.4f%%' % (100 * cur.roe_agg))
print('  kiem chung PB_agg/PE_agg  = %.4f%%   (PE_agg=%.3f PB_agg=%.4f)' % (100 * cur.pb_agg / cur.pe_agg, cur.pe_agg, cur.pb_agg))
print('ROE trung binh gian don     = %.4f%% (raw)  %.4f%% (winsor +-100%%)' % (100 * cur.roe_mean_raw, 100 * cur.roe_mean_w))
print('ROE trung vi per-ticker     = %.4f%%' % (100 * cur.roe_p50))
print('ngu phan vi per-ticker: p05=%.2f%% p25=%.2f%% p50=%.2f%% p75=%.2f%% p95=%.2f%%' % tuple(
    100 * cur[c] for c in ['roe_p05', 'roe_p25', 'roe_p50', 'roe_p75', 'roe_p95']))

# identity check across full history
ident = (d.roe_agg - d.pb_agg / d.pe_agg).abs().max()
print('\nKIEM CHUNG DONG NHAT THUC  max|ROE_agg - PB_agg/PE_agg| = %.3e  (=0 => ROE la ham dai so cua PE,PB)' % ident)

end = cur.time
WIN = {'full_2008+': d.time >= '2008-01-01',
       'last_10Y': d.time >= end - pd.DateOffset(years=10),
       'last_5Y':  d.time >= end - pd.DateOffset(years=5),
       'last_3Y':  d.time >= end - pd.DateOffset(years=3)}


def desc(s, v, label):
    s = s.dropna()
    q = s.quantile([.05, .25, .5, .75, .95])
    return dict(series=label, N=len(s), cur=round(100 * v, 3), pctile=round(100 * (s < v).mean(), 1),
                mean=round(100 * s.mean(), 2), median=round(100 * s.median(), 2), std=round(100 * s.std(), 2),
                skew=round(stats.skew(s), 3), kurt=round(stats.kurtosis(s), 3),
                p05=round(100 * q.iloc[0], 2), p25=round(100 * q.iloc[1], 2), p50=round(100 * q.iloc[2], 2),
                p75=round(100 * q.iloc[3], 2), p95=round(100 * q.iloc[4], 2),
                min=round(100 * s.min(), 2), max=round(100 * s.max(), 2))


rows = []
for w, m in WIN.items():
    sub = d[m]
    for col, lab in [('roe_agg', 'ROE_gop(book-w)'), ('roe_median', 'ROE_trungvi(EW)'), ('roe_mean_w', 'ROE_TB(EW,winsor)')]:
        r = desc(sub[col], cur[col], lab); r['window'] = w; rows.append(r)
S = pd.DataFrame(rows)[['window', 'series', 'N', 'cur', 'pctile', 'mean', 'median', 'std', 'skew', 'kurt',
                        'p05', 'p25', 'p50', 'p75', 'p95', 'min', 'max']]
print('\n=== (A) THONG KE MO TA CHUOI THOI GIAN ROE THI TRUONG (don vi %) ===')
print(S.to_string(index=False))
S.to_csv(EXP + 'roe_ts_desc.csv', index=False)


def hist(s, lo, hi, step, label):
    s = s.dropna() * 100
    edges = np.arange(lo, hi + step, step)
    cnt, _ = np.histogram(s, bins=np.concatenate([[-1e9], edges, [1e9]]))
    labs = ['<%g' % lo] + ['%g..%g' % (edges[i], edges[i + 1]) for i in range(len(edges) - 1)] + ['>=%g' % hi]
    out = pd.DataFrame({'bucket': labs, 'count': cnt})
    out['pct'] = (100 * out['count'] / out['count'].sum()).round(1)
    out['bar'] = out.pct.apply(lambda x: '#' * int(round(x / 1.0)))
    return out


print('\n=== (A) HISTOGRAM chuoi ROE_gop theo phien — 2008+ (buoc 0.5pp) ===')
h1 = hist(d[d.time >= '2008-01-01'].roe_agg, 8, 20, .5, '2008+')
print(h1.to_string(index=False))
print('\n=== (A) HISTOGRAM chuoi ROE_gop theo phien — 3 nam gan nhat (buoc 0.5pp) ===')
h2 = hist(d[d.time >= end - pd.DateOffset(years=3)].roe_agg, 8, 20, .5, '3Y')
print(h2.to_string(index=False))
h1.to_csv(EXP + 'hist_roe_agg_2008.csv', index=False); h2.to_csv(EXP + 'hist_roe_agg_3y.csv', index=False)

# yearly means for context
yr = d.groupby(d.time.dt.year).agg(n=('n', 'mean'), roe_agg=('roe_agg', 'mean'), roe_med=('roe_median', 'mean'),
                                   pe=('pe_agg', 'mean'), pb=('pb_agg', 'mean'))
yr[['roe_agg', 'roe_med']] *= 100
print('\n=== (A) TRUNG BINH THEO NAM ===')
print(yr.round(2).to_string())
yr.to_csv(EXP + 'roe_by_year.csv')

d.to_csv(EXP + 'roe_daily_enriched.csv', index=False)
