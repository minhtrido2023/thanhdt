"""GPM/EBITM TTM (BQ ticker_financial) — r3 07/11 theo dinh chinh Mike 19:50: GPM_P0/EBITM_P0 DA LA TTM (4 quy truot);
Revenue_P0/NP_P0 la QUY. Nam = dong Q4 cua GPM_P0/EBITM_P0, dung THANG (khong TB4Q, khong tinh lai TTM tu chuoi GPM_Pi).
2026 = dong 2026Q3 (TTM Q4/25-Q3/26). rev_ttm = sum Revenue_P0..P3 (quy). Chay: $DNA_PYEXE -B ttm.py > ttm_out.txt"""
import csv, json
R = {}
for r in csv.DictReader(open('ttm_bq.csv')):
    R.setdefault(r['ticker'], {})[r['quarter']] = r
f = lambda x: float(x) if x not in ('', None) else None
out = {}
for t, d in R.items():
    for q in sorted(d):
        if not (q.endswith('Q4') or q == '2026Q3'): continue
        r = d[q]; v = [f(r[f'Revenue_P{i}']) for i in range(4)]
        out.setdefault(t, {})[q[:4]] = dict(gpm=f(r['GPM_P0']), ebitm=f(r['EBITM_P0']), rev_ttm=sum(v) / 1e9 if None not in v else None,
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
