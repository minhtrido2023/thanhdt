"""SAU KHOA r4 — so phu cho bao cao NDT, tinh tu mo hinh DA KHOA (model_r4.py khong sua): tung nhanh x duong gia, cau noi tam, nhanh CYCLICAL voi tran SL 1,40."""
import sys, json
sys.dont_write_bytecode = True
import model_r4 as N
S, M = N.S, N.M
out = {'branch_path': {}, 'bridge_dcp': {}}
for n in N.CW_BOBBY:
    for p in N.PATHS:
        vn, vm = N.branch(n, {'PW': {p: 1.0}})
        out['branch_path'][f'{n}|{p}'] = dict(V_NNC=vn, V_MVC=vm)
vn, vm, b = N.EV4(detail=True)
ps = lambda ty: ty * 1e9 / M.N_SH
dly = sum(pp * M.n_cip * (1 - 1.13 ** -d) for d, pp in N.N3.DELAY_P.items())
const = dict(Q4_2026=ps(M.n_q4), tien_rong=ps(M.n_cash), ky_quy_thue_hoan_lai=ps(N.N3.KYQUY + N.N3.DTA), NHC_so_sach=ps(M.n_nhc_book),
             CIP_TamLap=ps(M.n_cip), tre_GP=-ps(dly))
mvc = ps(M.c_MVC * vm / 10)        # V_MVC d/cp -> ty = /10
out['bridge_dcp'] = dict(mo_Mui_Tau_gom_thue=vn - sum(const.values()) - mvc, **const, co_phan_MVC=mvc, TONG=vn)
out['cyc_cap140'] = N.branch('CYCLICAL', cap_basis='1.40')[0]
out['cyc_flat'] = N.branch('CYCLICAL', {'PW': {'flat': 1.0}})[0]
for kk, v in out.items(): print(kk, v)
json.dump(out, open('extras_r4_out.json', 'w'), indent=1)
# Gordon bo sung (SAU KHOA, khong doi tam/thang): ROE chuan hoa cong LN tai chinh sau thue (DT tai chinh 9T/26 15,60 ty [Q3 VI.3] nam hoa)
fin = 15.60 / 0.75 * (1 - M.TAX); gor = {}
for n, d in json.load(open('model_r4_out.json'))['gordon']['by_state'].items():
    roe = (d['nopat'] + fin) / N.BV_NNC; gor[n] = dict(roe=roe, ps=(roe - .03) / .10 * N.N3.BVPS_NNC)
rw = sum(N.CW_BOBBY[n] * gor[n]['roe'] for n in gor)
gor['tron'] = dict(roe=rw, ps=(rw - .03) / .10 * N.N3.BVPS_NNC); gor['fin_income_after_tax'] = fin
print('gordon_fin', gor)
out['gordon_fin'] = gor
json.dump(out, open('extras_r4_out.json', 'w'), indent=1)
