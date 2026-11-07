"""SZL 3c kiem nhanh: ROIC/ROE nhieu cua so + GPM TTM trong so doanh thu, SZL vs peer KCN noi dia. Nguon: 5F/bq_fin_peers_20261107.csv (BQ ticker_financial 07/11/2026).
GPM_P0 = gia tri MOT QUY => GP_q = GPM_P0*Rev_P0; GPM TTM = sum GP 4Q / sum Rev 4Q; GPM nam = sum 4 quy cua nam."""
import csv, os, statistics as st, json
H = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in csv.DictReader(open(os.path.join(H, 'bq_fin_peers_20261107.csv')))]
PEERS = ["SZC","SZB","IDC","NTC","LHG","D2D","TIP","KBC","BCM","SIP","ITA"]
f = lambda x: float(x) if x not in ('', 'NULL', None) else None
by = {}
for r in rows: by.setdefault(r['ticker'], {})[r['quarter']] = r
def yr_gpm(tk, y):
    q = [by[tk].get(f"{y}Q{i}") for i in range(1,5)]
    if any(x is None or f(x['gpm']) is None or f(x['rev']) in (None,0) for x in q): return None
    return sum(f(x['gpm'])*f(x['rev']) for x in q)/sum(f(x['rev']) for x in q)
def ttm(tk, qs=("2025Q4","2026Q1","2026Q2","2026Q3")):
    q = [by[tk].get(x) for x in qs]
    if any(x is None or f(x['gpm']) is None or f(x['rev']) in (None,0) for x in q): return None
    return sum(f(x['gpm'])*f(x['rev']) for x in q)/sum(f(x['rev']) for x in q)
out = {}
print("SZL theo nam (Q4 snapshot) — ROIC_Min5Y/ROIC5Y/ROIC3Y/ROIC10Y/ROIC_Min10Y/ROE_Trailing/ROE_Min5Y/ROIC_Trailing/_v1 ; GPM nam (trong so DT) ; NP nam (ty)")
for y in range(2015, 2027):
    k = f"{y}Q4" if y < 2026 else "2026Q3"; r = by['SZL'].get(k)
    if not r: continue
    np_y = sum(f(by['SZL'][f"{y}Q{i}"]['np']) for i in range(1,5) if f"{y}Q{i}" in by['SZL'])/1e9
    g = yr_gpm('SZL', y)
    print(f" {k}: " + " ".join(f"{c}={f(r[c]):.3f}" if f(r[c]) is not None else f"{c}=NA" for c in ['ROIC_Min5Y','ROIC5Y','ROIC3Y','ROIC10Y','ROIC_Min10Y','ROE_Trailing','ROE_Min5Y','ROIC_Trailing','ROIC_Trailing_v1']) + f" | GPM {g if g is None else round(g,3)} | NP {np_y:.1f}{' (9T)' if y==2026 else ''}")
print("\nGPM: TTM (Q4/25-Q3/26, trong so DT) ; TB GPM nam 2017-2025 (TB cac nam) ; ROIC_Min5Y/ROIC5Y/ROE_Trailing @2026Q3 (hoac quy moi nhat)")
tab = {}
for tk in ["SZL"] + PEERS:
    if tk not in by: continue
    ys = [yr_gpm(tk, y) for y in range(2017, 2026)]; ys = [v for v in ys if v is not None]
    lq = max(by[tk]); r = by[tk][lq]
    tab[tk] = dict(ttm=ttm(tk), cyc=st.mean(ys) if ys else None, n_yrs=len(ys), lastq=lq, rmin5=f(r['ROIC_Min5Y']), r5=f(r['ROIC5Y']), roe=f(r['ROE_Trailing']))
    t = tab[tk]
    print(f" {tk}: TTM {t['ttm'] if t['ttm'] is None else round(t['ttm'],3)} | cyc17-25 {t['cyc'] if t['cyc'] is None else round(t['cyc'],3)} (n={t['n_yrs']}) | {lq} ROIC_Min5Y {t['rmin5']} ROIC5Y {t['r5']} ROE_T {t['roe']}")
pc = [tab[k]['cyc'] for k in PEERS if k in tab and tab[k]['cyc'] is not None]
pt = [tab[k]['ttm'] for k in PEERS if k in tab and tab[k]['ttm'] is not None]
pr = [tab[k]['rmin5'] for k in PEERS if k in tab and tab[k]['rmin5'] is not None]
S = dict(peer_cyc_median=st.median(pc), peer_cyc_mean=st.mean(pc), n_cyc=len(pc), peer_ttm_median=st.median(pt), peer_ttm_mean=st.mean(pt), n_ttm=len(pt),
         peer_rmin5_median=st.median(pr), szl=tab['SZL'])
print("\nPEER (KCN noi dia, %s): GPM chu ky TB nam 2017-25 trung vi %.3f / TB %.3f (n=%d); TTM trung vi %.3f / TB %.3f (n=%d); ROIC_Min5Y trung vi %.3f" % (",".join(PEERS), S['peer_cyc_median'], S['peer_cyc_mean'], S['n_cyc'], S['peer_ttm_median'], S['peer_ttm_mean'], S['n_ttm'], S['peer_rmin5_median']))
json.dump(dict(table=tab, summary=S), open(os.path.join(H, 'szl_5f_stats_out.json'), 'w'), indent=1, default=float, sort_keys=True)
