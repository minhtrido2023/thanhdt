"""DD NNC r6 (03/11/2026 ~22:40 ICT) — doi chi phi von theo luat 21 (user 03/11 22:27). MU GIA: khong doc gia/von hoa/P-E NNC hay MVC trong file nay
(khong dung gia thi truong lam dau vao cua mo hinh). Chay: /home/trido/thanhdt/wc_venv/bin/python -B nnc_model_r6.py
He thong: tai dung nnc_model_r5.py -> model_r4 -> model_r3 -> MVC r6 KHONG SUA (md5 o LOCK_md5_r6.txt). Moi gia dinh phan doan r5 GIU NGUYEN (user duyet).

THAY DOI r6 so voi r5 (CHI chi phi von + thanh khoan):
 (1) r = 13,5% tai diem neo lai huy dong 12T hieu dung 7,40% (cctg_12m 02/11/2026; deposit_rate_vn.macro_killswitch_a_status() doc 03/11/2026).
     r(dep) = 13,5% + beta x (dep - 7,40%), beta = 1 (gia dinh pass-through du; do nhay beta 0,5). Tiem r vao MOI lan goi N3.EV3 (r5 mac dinh 13%).
 (2) Gordon/ROE chuan hoa dung CUNG r (r - g = 10,5%); PV dong thue Nui Nho + tra truoc CNBP chiet khau o r.
 (3) Truc r cua luoi doi tam: {11,5%; 13,5%; 15,5%} (= tam +-2pp nhu r5).
 (4) Chan doi chung: tam o r 13% PHAI tai lap r5 61.666 (sai < 1 d/cp).
RUI RO THANH KHOAN (DANG KY TRUOC; tinh SAU khoa o liquidity_r6.py vi can khoi luong/gia tri giao dich — khong dung lam dau vao mo hinh):
  chiet khau d(Q) = Y x sigma_ngay x sqrt(Q / ADV_trung_vi)  (luat can bac hai tac dong gia; Y = 1,0 tam, do nhay Y 0,5/1,5),
  sigma_ngay = do lech chuan log-return ngay 250 phien, ADV = trung vi Volume x Price 250 phien (tav2_bq.ticker); kiem cheo Amihud
  (trung vi |r|/gia tri GD) x gia tri ban moi phien o ty le tham gia 15%; so phien thoat lenh o 10%/20% ADV. Quy mo 1/5/10 ty d.
  NHAN re/dat = gia so voi thang P10..P90 nhan (1 - d(5 ty)), Y=1,0. Quy mo tham chieu 5 ty d; bao them nhan o 1 va 10 ty neu khac.
NGUONG mo hinh (dang ky truoc): RE <= P10 ; RE CO DIEU KIEN P10-P25 ; HOP LY P25-P75 ; NGHIENG DAT P75-P90 ; DAT >= P90 (luoi 4.374 bo).
"""
import sys, os, itertools, json, csv
import numpy as np
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
N5D = os.path.abspath(os.path.join(HERE, '../../r5/calc'))
sys.path.insert(0, N5D)
_cwd = os.getcwd(); os.chdir(N5D)
import nnc_model_r5 as N5   # noqa: E402
os.chdir(_cwd)
N4, N3, S, M, R = N5.N4, N5.N3, N5.S, N5.M, N5.R
CW_BOBBY, V_REV, ADMIN = N5.CW_BOBBY, N5.V_REV, N5.ADMIN
R_ANCHOR, DEP_ANCHOR, DEP_SRC = 0.135, 0.074, 'cctg_12m 02/11/2026 (deposit_rate_vn, doc 03/11/2026)'
G = 0.03


def r_of(dep, beta=1.0): return R_ANCHOR + beta * (dep - DEP_ANCHOR)


_EV3 = N3.EV3


def EV3r(over=None, detail=False):
    return _EV3({'r': R_ANCHOR, **(over or {})}, detail=detail)


N3.EV3 = EV3r          # N5.branch / MVC r8 tra N3.EV3 luc goi => r mac dinh 13,5%
EV5, branch = N5.EV5, N5.branch
Ws, PWs, CWs, VRs, AMs = N5.Ws, N5.PWs, N5.CWs, N5.VRs, N5.AMs
R_AXIS = (R_ANCHOR - 0.02, R_ANCHOR, R_ANCHOR + 0.02)


def _cell(a):
    r, kk, wi, pi, ci, vi, cb, am = a
    vnn, vmm, _ = EV5({'r': r, 'K': kk, 'W': Ws[wi], 'PW': PWs[pi]}, cw=CWs[ci], v_rev=VRs[vi], cap_basis=cb, admin=am, detail=True)
    return dict(r=r, K=kk, W=wi, PW=pi, CW=ci, VR=vi, cap=cb, admin=am, ev=vnn, ev_mvc=vmm)


if __name__ == '__main__':
    out = dict(r=R_ANCHOR, dep_anchor=DEP_ANCHOR, dep_src=DEP_SRC, beta=1.0)
    vn, vm, b = EV5(detail=True); out['tam'] = vn; out['mvc_simul'] = vm
    out['branches'] = {n: dict(w=CW_BOBBY[n], V_NNC=b[n][0], V_MVC=b[n][1]) for n in b}
    print(f'=== 1. TAM NNC r6 (r 13,5% @ huy dong 7,40%; con lai = r5): {vn:,.0f} d/cp | MVC dong thoi {vm:,.0f}')
    for n in b: print(f'  {n:11s} w {CW_BOBBY[n]:.2f}: NNC {b[n][0]:8,.0f} | MVC {b[n][1]:7,.0f}')
    c13 = EV5({'r': 0.13}); out['control_r13'] = c13
    print(f'  CHAN DOI CHUNG r 13%: {c13:,.0f} (r5 pin 61.666; lech {c13-61666:+.1f})')
    out['admin_axis'] = {}
    for am in AMs:
        x, y, _ = EV5(admin=am, detail=True); out['admin_axis'][am] = dict(V_NNC=x, V_MVC=y)
    out['branch_path'] = {f'{n}|{p}': dict(zip(('V_NNC', 'V_MVC'), branch(n, {'PW': {p: 1.0}}))) for n in CW_BOBBY for p in N5.PATHS}

    print('\n=== 2. Phan ung theo r (tam, nhanh) ===')
    rt = {}
    for r in (0.12, 0.125, 0.13, 0.135, 0.14, 0.145, 0.15):
        x, y, bb = EV5({'r': r}, detail=True)
        rt[f'{r:.3f}'] = dict(V_NNC=x, V_MVC=y, d_vs_135=x - vn, pct_vs_135=x / vn - 1, **{n: bb[n][0] for n in bb})
        print(f'  r {r:.1%}: {x:8,.0f} ({x-vn:+7,.0f}; {x/vn-1:+.1%}) | MVC {y:7,.0f} | ' + ' '.join(f'{n[:4]} {bb[n][0]:,.0f}' for n in bb))
    out['r_table'] = rt
    print('\n=== 3. Do nhay lai huy dong (r = 13,5% + beta x d_dep) ===')
    dep = {}
    for beta in (1.0, 0.5):
        for bp in (-100, -50, 50, 100):
            r = r_of(DEP_ANCHOR + bp / 1e4, beta); x, y, _ = EV5({'r': r}, detail=True)
            dep[f'b{beta}_{bp:+d}'] = dict(beta=beta, bp=bp, dep=DEP_ANCHOR + bp / 1e4, r=r, V_NNC=x, V_MVC=y, d=x - vn, pct=x / vn - 1)
            print(f'  beta {beta}: huy dong {(DEP_ANCHOR+bp/1e4):.2%} ({bp:+d}bp) -> r {r:.2%}: {x:8,.0f} ({x-vn:+7,.0f}; {x/vn-1:+.1%}) | MVC {y:,.0f}')
    out['dep_sens'] = dep

    ev_ = N4.eff_vol(V_REV); cu = N4.unit_cost(ev_); cap = N4.cap_for(ev_)
    out['margin'] = dict(cap=cap, cost=cu, real=1 - cu / cap, g2031_2030=1 - cu * 1.03 ** 4 / cap, cap140=N4.cap_for(1.40))

    print(f'\n=== 4. Gordon P/B = (ROE-g)/(r-g), r {R_ANCHOR:.1%} g 3% (CUNG r) ===')
    fin = 15.60 / 0.75 * (1 - M.TAX); gor = {}
    for n in CW_BOBBY:
        npt, p, v = N4.nopat_norm('CYCLICAL' if n == 'ADMIN_GATED' else n)
        gor[n] = dict(nopat=npt, p=p, v=v, roe_lock=npt / N4.BV_NNC, roe_fin=(npt + fin) / N4.BV_NNC)
    for key in ('roe_lock', 'roe_fin'):
        rw = sum(CW_BOBBY[n] * gor[n][key] for n in CW_BOBBY); pb = (rw - G) / (R_ANCHOR - G)
        gor['tron_' + key] = dict(roe=rw, pb=pb, ps=pb * N3.BVPS_NNC, ps_r13=(rw - G) / 0.10 * N3.BVPS_NNC)
        print(f'  {key}: ROE {rw:.1%} -> P/B {pb:.2f}x -> {pb*N3.BVPS_NNC:,.0f} (o r13: {(rw-G)/0.10*N3.BVPS_NNC:,.0f})')
    for n in CW_BOBBY: gor[n]['ps_fin'] = (gor[n]['roe_fin'] - G) / (R_ANCHOR - G) * N3.BVPS_NNC
    out['gordon'] = gor; out['roe_implied_tam'] = G + vn / N3.BVPS_NNC * (R_ANCHOR - G)
    print(f'  ROE ham y cua tam {vn:,.0f} (P/B {vn/N3.BVPS_NNC:.2f}x): {out["roe_implied_tam"]:.1%}')

    print('\n=== 5. Luoi 4.374 bo (truc r 11,5/13,5/15,5) ===')
    args = list(itertools.product(R_AXIS, (0.87, 0.97, 1.07), range(3), range(3), range(3), range(3), ('branch', '1.40'), AMs))
    with Pool(6) as pool: grid = pool.map(_cell, args, chunksize=40)
    ge = np.array([x['ev'] for x in grid]); gp = {q: float(np.percentile(ge, q)) for q in (5, 10, 25, 50, 75, 90, 95)}
    gp['min'] = float(ge.min()); gp['max'] = float(ge.max())
    print(f'  N={len(ge)}: ' + ' '.join(f'P{q} {v:,.0f}' for q, v in gp.items()))
    out['grid_pct'] = gp; out['grid_n'] = len(ge)
    out['grid_sub_r'] = {f'{r:.3f}': dict(p10=float(np.percentile([x['ev'] for x in grid if x['r'] == r], 10)),
                                          p50=float(np.median([x['ev'] for x in grid if x['r'] == r])),
                                          p90=float(np.percentile([x['ev'] for x in grid if x['r'] == r], 90))) for r in R_AXIS}
    with open('grid_r6.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    print('NGUONG (truoc CK thanh khoan): RE <= {:,.0f} | RE CO DK {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | NGHIENG DAT {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))

    print('\n=== 6. Do nhay (so voi tam r6) ===')
    tor = {}
    def T(lab, over=None, **kw):
        x = EV5(over, **kw); tor[lab] = x - vn; print(f'  {lab:80s} {x:8,.0f} ({x - vn:+7,.0f})')
    T('tran chu ky 242,5k (neo skeptic)', cap_abs=242.5); T('tran chu ky SL 1,40 = %.1fk' % N4.cap_for(1.40), cap_basis='1.40')
    T('anh xa ADMIN 0,5 vinh vien', admin='perm05'); T('anh xa ADMIN 1,0 tu 2028 (khong tre)', admin='full')
    T('trong so nghieng STRUCTURAL 40/35/25', cw=CWs[1]); T('trong so nghieng CYCLICAL 15/35/50', cw=CWs[2])
    T('chi CYCLICAL', cw={'CYCLICAL': 1.0}); T('chi STRUCTURAL', cw={'STRUCTURAL': 1.0})
    T('SL nam thuong 1,05 ca ky', v_rev=(1.05, 1.05)); T('SL nam thuong 1,20/1,30', v_rev=(1.20, 1.30))
    T('(+) upside doi thu het GP: tu 2034 stress giam mot nua', {'up2034': True})
    T('K chi phi 0,87', {'K': 0.87}); T('K chi phi 1,07', {'K': 1.07}); T('r 11,5%', {'r': 0.115}); T('r 15,5%', {'r': 0.155})
    T('PW g2031 70/real 30', {'PW': PWs[0]}); T('PW g2031 30/real 70', {'PW': PWs[2]})
    T('STRESS duong gia danh nghia phang 100%', {'PW': {'flat': 1.0}})
    T('bo LN cho thue Nui Nho (thoi han CHUA XAC MINH)', {'rent': False})
    q = 1 + R_ANCHOR
    pvf = {y: 1.03 ** (y - 2026) / q ** (y - 2026) for y in range(2027, 2044)}
    fr = sum(v for y, v in pvf.items() if y >= 2031) / sum(pvf.values())
    tor['cho thue Nui Nho chi toi 2030 (xap xi ty le PV)'] = fr * tor['bo LN cho thue Nui Nho (thoi han CHUA XAC MINH)']
    print(f'  cho thue Nui Nho chi toi 2030 (~{fr:.0%} PV): {tor["cho thue Nui Nho chi toi 2030 (xap xi ty le PV)"]:+,.0f}')
    pp = sum(12.8 / q ** (i + 0.5) for i in range(4)) + 0.6 * 12.8 / q ** 4.5
    T('(+) tra truoc dai han CNBP 59,2 la tien thue da tra (CHUA XAC MINH)', {'extra': pp})
    T('bo doi xung BCDKT', {'bs_sym': False}); T('holding MVC->NNC 15%', {'hold': 0.15})
    out['tornado'] = tor
    out['bridge'] = dict(r5_r13=c13, r6_r135=vn)
    print(f'\n  Cau noi: r5 (r13) {c13:,.0f} -> r6 (r13,5) {vn:,.0f} ({vn-c13:+,.0f}; {vn/c13-1:+.1%})')
    print(f'=== 7. V_NNC cho MVC r9: {vn:,.0f} d/cp (MVC dong thoi {vm:,.0f}) ===')
    with open('nnc_model_r6_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
