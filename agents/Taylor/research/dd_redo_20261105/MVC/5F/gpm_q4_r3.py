"""5F r3 MVC (job Taylor_20261107_124458). Dinh chinh GPM (Mike 07/11 19:50): BQ GPM_P0 = TTM 4 quy truot => dong Q4 = GPM CA NAM (dung thang),
KHONG lay TB/trong so tu chuoi GPM_P0. Dau vao bq_q_r3.csv (bq query 07/11/2026, tav2_bq.ticker_financial). Cua so CHUNG 2017-2025 cho moi ma.
Them: chuoi ROIC (ROIC_Trailing_v1 = bao cao, ROIC_Trailing = tu tinh) o Q4. Chay: $DNA_PYEXE -B gpm_q4_r3.py"""
import csv, json, os, statistics as stt
HERE = os.path.dirname(os.path.abspath(__file__))
R = [r for r in csv.DictReader(open(os.path.join(HERE, 'bq_q_r3.csv')))]
f = lambda x: float(x) if x not in ('', None) else None
TK = ['MVC', 'NNC', 'KSB', 'DHA', 'VLB']; PEER = ['KSB', 'DHA', 'VLB']; Y0, Y1 = 2017, 2025
q4 = {t: {int(r['quarter'][:4]): f(r['GPM_P0']) for r in R if r['ticker'] == t and r['quarter'].endswith('Q4') and f(r['GPM_P0']) is not None} for t in TK}
now = {t: next((f(r['GPM_P0']) for r in R if r['ticker'] == t and r['quarter'] == '2026Q3'), None) for t in TK}
win = {t: {y: q4[t][y] for y in range(Y0, Y1 + 1) if y in q4[t]} for t in TK}
mean = {t: stt.mean(win[t].values()) for t in TK}; nyr = {t: len(win[t]) for t in TK}
pm = [mean[t] for t in PEER]; pm4 = [mean[t] for t in PEER + ['NNC']]
out = dict(basis='GPM_P0 tai Q4 (=GPM nam, TTM) cua so chung 2017-2025', q4=q4, win_mean=mean, n_years=nyr, ttm_2026Q3=now,
           peer3_mean=stt.mean(pm), peer3_median=stt.median(pm), peer3_ex_KSB_mean=stt.mean([mean['DHA'], mean['VLB']]),
           peer4_incl_NNC_mean=stt.mean(pm4), peer4_incl_NNC_median=stt.median(pm4),
           ttm_peer3_mean=stt.mean([now[t] for t in PEER]), ttm_peer3_median=stt.median([now[t] for t in PEER]))
m = [r for r in R if r['ticker'] == 'MVC']
out['mvc_roic'] = {r['quarter']: dict(v1=f(r['ROIC_Trailing_v1']), self=f(r['ROIC_Trailing']), roe=f(r['ROE_Trailing'])) for r in m if r['quarter'].endswith('Q4') or r['quarter'] == '2026Q3'}
qs = [r for r in m if r['quarter'] >= '2022Q4']
out['v1_gt_ke_quarters_from_2022Q4'] = [sum(f(r['ROIC_Trailing_v1']) > 0.135 for r in qs), len(qs)]
out['v1_q4_mean_2021_25'] = stt.mean(f(r['ROIC_Trailing_v1']) for r in m if r['quarter'] in [f'{y}Q4' for y in range(2021, 2026)])
out['self_q4_mean_2021_25'] = stt.mean(f(r['ROIC_Trailing']) for r in m if r['quarter'] in [f'{y}Q4' for y in range(2021, 2026)])
out['ROIC5Y_latest'] = f(m[-1]['ROIC5Y']); out['ROIC_Min5Y_latest'] = f(m[-1]['ROIC_Min5Y'])
for t in TK: print(t, 'n', nyr[t], f'TB {mean[t]:.1%}', 'TTM26Q3', f'{now[t]:.1%}', {y: round(v * 100, 1) for y, v in win[t].items()})
print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items() if k.startswith(('peer', 'ttm_peer', 'v1', 'self', 'ROIC'))})
json.dump(out, open(os.path.join(HERE, 'gpm_q4_r3_out.json'), 'w'), indent=1, sort_keys=True)
