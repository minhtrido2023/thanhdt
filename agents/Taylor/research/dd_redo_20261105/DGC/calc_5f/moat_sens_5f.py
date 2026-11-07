"""DGC — do nhay moat buoc 3c (job Taylor_20261107_123131; r3 job Taylor_20261107_124453).
r3: (a) GPM nganh = GPM_P0 dong Q4 dung THANG (GPM_P0 la TTM — dinh chinh Mike 07/11 19:50), ttm_out.json moi;
 (b) them CAP MOT CHIEU: e_term = min(e_rieng, e_nganh) moi nhanh (khong NANG nhanh dung — fade doi xung thuong cho kich ban mat hao);
 (c) tuy chon 2027-28 tai dau tu theo Ke (ronic_near=Ke) thay RONIC 20%. KHONG ghi calc/; import model_r2 (khong chay __main__).
Kenh moat trong mo hinh hien hanh: (1) RONIC=20% > Ke trong terminal (reinv = 1-g/RONIC); (2) bien terminal = bien rieng DGC
 (GPM kich ban 15/17,5/19% + nhanh mo lai khai truong +1.000 ty LN gop/nam = loi the quang tu chu).
Chat-3c (NARROW/khong ben): RONIC=Ke VA GPM terminal = TB chu ky nganh (GPM TTM co trong so DT 2017-25, ttm_out.json), DOI XUNG:
 ap cho MOI nhanh (nhanh dung bien thap hon nganh duoc NANG len, nhanh mo lai bi HA xuong); 2027-28 tuong minh giu nguyen.
 EBIT_term = (GPM_ind*Rev28_scn - opex_scn)*m ; opex_scn = gp-ebit (r12 out_A_forecast.csv) = 520 moi kich ban.
Chay: $DNA_PYEXE -B moat_sens_5f.py > moat_sens_5f_out.txt"""
import os, sys, json, itertools, statistics as st
H = os.path.dirname(os.path.abspath(__file__)); CALC = os.path.abspath(os.path.join(H, '../calc'))
sys.path.insert(0, CALC); sys.path.insert(0, os.path.abspath(os.path.join(H, '../../_common_014127'))); sys.path.insert(0, os.path.abspath(os.path.join(H, '../../_shared')))
import model_r2 as R, model as M1, common_r2 as R2
from wpct import wpct, weight_below
S = json.load(open(os.path.join(H, '..', 'SUMMARY.json'))); PX = S['price']; D = S['liquidity']['d_ref']
D_SL = {k: S['liquidity']['w250']['sizes'][k]['disc'] for k in ('10tr', '20tr', '40tr')}
REV = {'xau': 8217.0, 'coso': 9403.0, 'tot': 10834.0}; OPEX = {'xau': 1233.0 - 713.0, 'coso': 1646.0 - 1126.0, 'tot': 2058.0 - 1538.0}   # r12 out_A_forecast.csv 2028
T = json.load(open(os.path.join(H, 'ttm_out.json'))); YRS = [str(y) for y in range(2017, 2026)]
def ind(peers, agg): return st.mean(agg([T[p][y]['gpm'] for p in peers if y in T[p] and T[p][y]['gpm'] is not None]) for y in YRS)
CORE = ('CSV', 'DDV', 'LAS', 'HVT')
PEERS = {'median_CSV_DDV_LAS_HVT': (CORE, st.median), 'mean_CSV_DDV_LAS_HVT': (CORE, st.mean),
         'median_+VAF': (CORE + ('VAF',), st.median), 'median_+BFC_SFG': (CORE + ('BFC', 'SFG'), st.median),
         'median_+DPM_DCM': (CORE + ('DPM', 'DCM'), st.median), 'CSV_only': (('CSV',), st.mean)}
IND = {k: ind(*v) for k, v in PEERS.items()}
DGC_GPM = st.mean(T['DGC'][y]['gpm'] for y in YRS)

def core(s, o, m, r, ronic=M1.RONIC, gpm_term=None, half=False, cap=False, ronic_near=M1.RONIC):
    c = R.SCN[s]; u = M1.ORE[o]; t = M1.T_NEAR; reinv = 1 - M1.G / ronic; rn = 1 - M1.G / ronic_near
    v = R.Q4_EX * m * (1 - t) / (1 + r) ** 0.125
    v += c['e27'] * m * (1 - t) * rn / (1 + r) ** 0.75          # 2027-28 tuong minh: mac dinh giu nguyen (reinv cu RONIC 20%); ronic_near=Ke -> theo Ke
    v += (c['e28'] * m + u['up28']) * (1 - t) * rn / (1 + r) ** 1.75
    e_own = c['e28'] * m + u['up']
    if gpm_term is None: e_t = e_own
    else:
        e_ind = (gpm_term * REV[s] - OPEX[s]) * m
        e_t = min(e_own, e_ind) if cap else ((e_own + e_ind) / 2 if half else e_ind)
    v += e_t * (1 + M1.G) * (1 - M1.T_TERM) * reinv / (r - M1.G) / (1 + r) ** 2.25    # quy uoc nam: giu nguyen model_r2 (Q4 0,125; 2027 0,75; 2028 1,75; TV 2,25 tu 30/09/26)
    return v

def grid(**kw):
    vals, wts = [], []
    for (s, sc), (o, oc), (p, pc), (n, nc), m, (r, rw, _) in itertools.product(R.SCN.items(), M1.ORE.items(), R.PROV.items(), R.NS.items(), M1.MULTS, R2.r_points()):
        other = (M1.CASH_DEP - M1.DEBT) - M1.PROV - M1.FUND_KTPL + M1.NS_CIP + R.NS[n]['adj']
        eq = (core(s, o, m, r, **kw) - R.prov_pv(p, r)) * (1 - M1.S_NP) + other * (1 - M1.S_EQ)
        vals.append(eq * 1e9 / M1.SH); wts.append(sc['w'] * oc['w'] * pc['w'] * nc['w'] / len(M1.MULTS) * rw)
    return vals, wts

def summ(v, w, d=D):
    f = 1 - d; q = wpct(v, w, (0.10, 0.50, 0.90)); c = sum(a * b for a, b in zip(v, w)) / sum(w) * f
    p10, p90 = q[0.10] * f, q[0.90] * f
    return dict(center=round(c), p10=round(p10), p50=round(q[0.50] * f), p90=round(p90), below=round(weight_below([x * f for x in v], w, PX), 3),
                label='DƯỚI vùng' if PX < p10 else ('TRÊN vùng' if PX > p90 else 'TRONG vùng'))

KE = R2.C.r_now()
out = dict(ke=KE, px=PX, d_ref=D, dgc_gpm_ttm_mean_2017_25=DGC_GPM, ind_gpm=IND, gpm_model_term={s: (R.SCN[s]['e28'] + OPEX[s]) / REV[s] for s in REV},
           gpm_model_term_molai={s: (R.SCN[s]['e28'] + OPEX[s] + 1000) / REV[s] for s in REV})
V = {}
V['current'] = grid(); b = summ(*V['current']); assert b['center'] == 44767 and b['p10'] == 32518 and b['p90'] == 57101, b   # chan doi chung = pin SUMMARY r2
V['ronic_ke_only'] = grid(ronic=KE)
V['margin_only_median'] = grid(gpm_term=IND['median_CSV_DDV_LAS_HVT'])
V['strict3c_half'] = grid(ronic=KE, gpm_term=IND['median_CSV_DDV_LAS_HVT'], half=True)
for k, g in IND.items(): V[f'strict3c_{k}'] = grid(ronic=KE, gpm_term=g)
V['wide_ul_ronic25'] = grid(ronic=0.25)
T2 = json.load(open(os.path.join(H, '_r2', 'ttm_out.json'))); IND_R2_MED = st.mean(st.median([T2[p][y]['gpm'] for p in CORE if y in T2[p] and T2[p][y]['gpm'] is not None]) for y in YRS)
out['ind_gpm_r2_method_median'] = IND_R2_MED   # tai lap so Mike (19,47%, phuong phap r2 SAI) — chi doi chung
V['cap_r2median'] = grid(ronic=KE, gpm_term=IND_R2_MED, cap=True)
V['strict3c_r2median'] = grid(ronic=KE, gpm_term=IND_R2_MED)
for k, g in IND.items(): V[f'cap_{k}'] = grid(ronic=KE, gpm_term=g, cap=True)
V['cap_median_ke2728'] = grid(ronic=KE, gpm_term=IND['median_CSV_DDV_LAS_HVT'], cap=True, ronic_near=KE)
V['strict3c_median_ke2728'] = grid(ronic=KE, gpm_term=IND['median_CSV_DDV_LAS_HVT'], ronic_near=KE)
yrs_above = sum(1 for y in YRS if T['DGC'][y]['gpm'] > st.median([T[p][y]['gpm'] for p in CORE if T[p][y]['gpm'] is not None]))
out['dgc_years_above_core_median_2017_25'] = yrs_above
out['variants'] = {k: summ(*v) for k, v in V.items()}
out['strict3c_sleeve'] = {sz: summ(*V['strict3c_median_CSV_DDV_LAS_HVT'], d=dd) for sz, dd in D_SL.items()}
out['cap_ke2728_sleeve'] = {sz: summ(*V['cap_median_ke2728'], d=dd) for sz, dd in D_SL.items()}
out['current_sleeve'] = {sz: summ(*V['current'], d=dd) for sz, dd in D_SL.items()}
print(json.dumps(out, indent=1, ensure_ascii=False))
json.dump(out, open(os.path.join(H, 'moat_sens_5f_out.json'), 'w'), indent=1, ensure_ascii=False)
