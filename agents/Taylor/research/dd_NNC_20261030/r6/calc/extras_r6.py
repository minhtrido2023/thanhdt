"""SAU KHOA r6 — so phu cho bao cao NDT, tinh tu mo hinh DA KHOA (nnc_model_r6.py khong sua): cau noi tam, nhanh CYCLICAL tran SL 1,40, Gordon theo trang thai (r 13,5%)."""
import sys, json
sys.dont_write_bytecode = True
import nnc_model_r6 as N
S, M, N4, R0 = N.S, N.M, N.N4, N.R_ANCHOR
o = json.load(open('nnc_model_r6_out.json'))
out = {'branch_path': o['branch_path']}
vn, vm, b = N.EV5(detail=True)
ps = lambda ty: ty * 1e9 / M.N_SH
dly = sum(pp * M.n_cip * (1 - (1 + R0) ** -d) for d, pp in N.N3.DELAY_P.items())
const = dict(Q4_2026=ps(M.n_q4), tien_rong=ps(M.n_cash), ky_quy_thue_hoan_lai=ps(N.N3.KYQUY + N.N3.DTA), NHC_so_sach=ps(M.n_nhc_book),
             CIP_TamLap=ps(M.n_cip), tre_GP=-ps(dly))
mvc = ps(M.c_MVC * vm / 10)
out['bridge_dcp'] = dict(mo_Mui_Tau_gom_thue=vn - sum(const.values()) - mvc, **const, co_phan_MVC=mvc, TONG=vn)
out['cyc_cap140'] = N.branch('CYCLICAL', cap_basis='1.40')[0]
out['gordon_fin'] = {n: dict(roe=d['roe_fin'], ps=d['ps_fin']) for n, d in o['gordon'].items() if n in N.CW_BOBBY}
out['gordon_fin']['tron'] = dict(roe=o['gordon']['tron_roe_fin']['roe'], ps=o['gordon']['tron_roe_fin']['ps'])
out['gordon_lock_tron'] = o['gordon']['tron_roe_lock']
for kk, v in out.items():
    if kk != 'branch_path': print(kk, v)
json.dump(out, open('extras_r6_out.json', 'w'), indent=1)
