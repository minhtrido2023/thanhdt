"""PVT — 5F buoc 3c (job Taylor_20261107_131640). CHEP cong thuc model_r2.value_ps (import M1/R2, khong sua), chi doi:
(a) RONIC terminal: 'roe' (hien hanh: tai dau tu sinh loi = ROE) | 'ke' (RONIC = Ke, doi xung moi nhanh) | 'wide' (RONIC = ROE giu vinh vien)
(b) neo ROE giua chu ky: PVT trung vi 2015-25 (hien hanh) | TB chu ky NGANH = trung vi/TB peer tau dau-khi noi dia (ROE_Trailing Q4 2015-25, BQ peer_5f_bq.csv).
Luoi 90 ket cuc, trong so, truc r, truc mua tau, CK thanh khoan: giu nguyen r2. Chay: $DNA_PYEXE -I pvt_5f.py > pvt_5f_out.txt"""
import csv, json, os, statistics as st, sys, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../calc')); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import model as M1, model_r2 as MR2, common_r2 as R2
C = R2.C
PX = 21000.0
rows = list(csv.DictReader(open(os.path.join(HERE, 'peer_5f_bq.csv'))))
def med_roe(tk):
    v = [float(r['roe_t']) for r in rows if r['ticker'] == tk and r['quarter'].endswith('Q4') and '2015' <= r['quarter'][:4] <= '2025' and r['roe_t']]
    assert len(v) >= 10, (tk, len(v)); return st.median(v)
PEERS = ['GSP', 'PJT', 'PVP', 'VIP']          # tau dau/khi/san pham noi dia; VTO thieu ROE_Trailing; VOS (hang roi), HAH (container) loai: khac phan khuc
pr = {t: med_roe(t) for t in PEERS}; assert abs(med_roe('PVT') - M1.ROE_MID) < 5e-4
ANCH = dict(own=M1.ROE_MID, peer_med=st.median(pr.values()), peer_mean=st.mean(pr.values()),
            peer_med_exPVP=st.median([pr[t] for t in PEERS if t != 'PVP']), peer_mean_exPVP=st.mean([pr[t] for t in PEERS if t != 'PVP']),
            ttm_q3_26=0.1577, ke=None)

def value_ps(s, m, r, b, base, ronic):
    c = M1.SCN[s]; g = M1.G; roe = (r if base is None else base) * c['mid'] * m
    k = {'roe': roe, 'ke': r, 'wide': roe}[ronic]
    reinv = 1 - g / max(k, 1e-9)
    v = M1.Q3_NP / (1 + r) ** 0.125 + c['np27'] * reinv / (1 + r) ** 0.75
    v += roe * M1.EQ_PARENT * (1 + g) * reinv / (r - g) / (1 + r) ** 1.25
    v += MR2.SHIP_NPV[s] * MR2.BUY[b]['amt'] * (1 - MR2.NCI)
    return v * 1e9 / M1.SH

def grid(base, ronic):
    V, W = [], []
    for (s, sc), m, (r, rw, _), (b, bc) in itertools.product(M1.SCN.items(), M1.MULTS, R2.r_points(), MR2.BUY.items()):
        V.append(value_ps(s, m, r, b, base, ronic)); W.append(sc['w'] / len(M1.MULTS) * rw * bc['w'])
    return V, W

liq = R2.liquidity_r2('PVT'); d5 = liq['d_ref']; d40 = liq['w250']['sizes']['40tr']['disc']; d10 = liq['w250']['sizes']['10tr']['disc']
VARS = dict(CUR=('own', 'roe'), SYM=('own', 'ke'), REVm=('peer_med', 'ke'), REVa=('peer_mean', 'ke'),
            REVm_exPVP=('peer_med_exPVP', 'ke'), REVa_exPVP=('peer_mean_exPVP', 'ke'), REV_only_m_RONICroe=('peer_med', 'roe'),
            ROE_eq_Ke=('ke', 'ke'), WIDE=('ttm_q3_26', 'wide'))
out = dict(r=C.r_now(), peers_roe_med_2015_25={k: round(v, 4) for k, v in pr.items()}, anchors={k: (round(v, 4) if v else 'r') for k, v in ANCH.items()},
           liq=dict(d5ty=d5, d10tr=d10, d40tr=d40), price=PX, variants={})
for k, (a, ro) in VARS.items():
    V, W = grid(ANCH[a], ro); cen = sum(x * y for x, y in zip(V, W)) / sum(W)
    s5 = R2.summarize_r2(V, W, cen, value_ps('coso', 1.0, C.r_now(), 'khong', ANCH[a], ro), PX, d5)
    s40 = R2.summarize_r2(V, W, cen, cen, PX, d40)
    out['variants'][k] = dict(anchor=a, ronic=ro, **{x: s5[x] for x in ('center_post', 'center_param_post', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label')},
                              label_40tr=s40['label'], p90_40tr=s40['p90_out'], center_40tr=s40['center_post'])
print(json.dumps(out, ensure_ascii=False, indent=1))
