"""GPM/EBITM TTM co trong so doanh thu (BQ ticker_financial: GPM_Pi, EBITM_P0, Revenue_Pi la gia tri TUNG QUY).
GPM TTM(dong q) = sum_i GPM_Pi*Rev_Pi / sum_i Rev_Pi (i=0..3). EBITM TTM(dong q) = sum 4 dong lien tiep EBITM_P0*Rev_P0 / sum Rev_P0.
Nam = dong Q4 (2026 = dong 2026Q3, TTM Q4/25-Q3/26). Chay: $DNA_PYEXE -B ttm.py > ttm_out.txt"""
import csv, statistics as st, json
R = {}
for r in csv.DictReader(open('ttm_bq.csv')):
    R.setdefault(r['ticker'], {})[r['quarter']] = r
f = lambda x: float(x) if x not in ('', None) else None
out = {}
for t, d in R.items():
    qs = sorted(d)
    for k, q in enumerate(qs):
        if not (q.endswith('Q4') or q == '2026Q3'): continue
        r = d[q]; g = [f(r[f'GPM_P{i}']) for i in range(4)]; v = [f(r[f'Revenue_P{i}']) for i in range(4)]
        gpm = sum(a * b for a, b in zip(g, v)) / sum(v) if None not in g + v and sum(v) > 0 else None
        last4 = [d[x] for x in qs[max(0, k - 3):k + 1]]
        ok = len(last4) == 4 and all(f(x['EBITM_P0']) is not None and f(x['Revenue_P0']) for x in last4)
        ebm = sum(f(x['EBITM_P0']) * f(x['Revenue_P0']) for x in last4) / sum(f(x['Revenue_P0']) for x in last4) if ok else None
        out.setdefault(t, {})[q[:4]] = dict(gpm=gpm, ebitm=ebm, rev_ttm=sum(v) / 1e9 if None not in v else None,
            **{c: f(r[c]) for c in ('ROIC_Min5Y', 'ROIC5Y', 'ROIC10Y', 'ROIC_Min10Y', 'ROE_Min5Y', 'ROE5Y', 'ROE_Trailing')})
yrs = [str(y) for y in range(2014, 2027)]
P = lambda x: '  -  ' if x is None else f'{x*100:5.1f}'
for c in ('gpm', 'ebitm', 'ROE_Trailing'):
    print(f'== {c} (%)  ' + ' '.join(y[2:] + '   ' for y in yrs))
    for t in sorted(out): print(f'{t:4s} ' + ' '.join(P(out[t].get(y, {}).get(c)) for y in yrs))
print('== DGC multi-window ROIC/ROE (dong Q4 / 2026Q3)')
for y in yrs:
    x = out['DGC'].get(y)
    if x: print(y, {k: (round(x[k] * 100, 1) if x[k] is not None else None) for k in ('ROIC_Min5Y', 'ROIC5Y', 'ROIC10Y', 'ROIC_Min10Y', 'ROE_Min5Y', 'ROE5Y', 'ROE_Trailing')}, 'rev', round(x['rev_ttm'] or 0))
json.dump(out, open('ttm_out.json', 'w'), indent=0)
