"""DD NNC r5 (03/11/2026 ~21:00 ICT) — sua theo SKEPTIC_R4_20261103.md. MU GIA: khong doc gia/von hoa/P-E NNC hay MVC trong file nay
(khong dung gia thi truong lam dau vao cua mo hinh). Chay: /home/trido/thanhdt/wc_venv/bin/python -B nnc_model_r5.py
He thong: tai dung model_r4.py (NNC r4) -> model_r3.py + MVC r6 KHONG SUA (md5 o LOCK_md5_r5.txt). Giai cheo dong thoi V_NNC/V_MVC nhu r4.

THAY DOI r5 so voi r4:
 (1) ADMIN_GATED: Bobby §4 (sector_read_da_xay_dung_nam_bo_20261030.md:181,185) = nghen hanh chinh TAM THOI go duoc 6-18 thang; co che san gia
     cao BEN (dau gia, mo xa) da nam o STRUCTURAL => giu nua premium o ADMIN la dem trung kenh. Anh xa CO SO moi: hoi bien TRON co tre 1 nam
     = stress 0,5 nam 2028 roi 1,0 tu 2029 ('ramp'). Truc anh xa ADMIN vao luoi: {0,5 vinh vien (=r4), 0,5@2028->1,0 (tam), 1,0 tu 2028}.
 (2) Tran chu ky 249,7k GIU (SL nhanh); bao do nhay tran 242,5k va 236,1k (SL 1,40) — 'hai cach neo hop le', khong phai 'tru hai lan'.
 (3) Gordon: ROE chuan hoa nhat quan anh xa moi (ADMIN = CYC o nam dien hinh 2031+), hien CA HAI chieu: ban khoa (khong LN tai chinh) va
     ban bo sung (+LN tai chinh 9T/26 nam hoa sau thue).
 (4) Bien o tran: tinh ca duong thuc (giu gia tri thuc) va duong g2031 (gia danh nghia phang toi 2030, chi phi +3%/nam) — nam 2030.
 (5) Cho thue Nui Nho: thoi han thue toi 2043 CHUA XAC MINH (BCTC scan, khong doc duoc trong phien; BCTN 2025 khong neu) => do nhay
     'thue toi 2030' ; tra truoc dai han CNBP 59,2 ty: ban chat CHUA XAC MINH => giu do nhay (khong vao tam).
NGUONG (DANG KY TRUOC KHI CHAY; khong sua sau khi thay so). Luoi 4.374 bo = luoi r4 1.458 x truc anh xa ADMIN 3 muc:
  RE <= P10 ; RE CO DIEU KIEN P10-P25 ; HOP LY P25-P75 ; NGHIENG DAT P75-P90 ; DAT >= P90.
"""
import sys, os, itertools, json, csv
import numpy as np
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../r4/calc')))
_cwd = os.getcwd(); os.chdir(os.path.join(HERE, '../../r4/calc'))
import model_r4 as N4   # noqa: E402
os.chdir(_cwd)
N3, S, M, R = N4.N3, N4.S, N4.M, N4.R
SCN, PATHS, W0, PW0 = N4.SCN, N4.PATHS, N4.W0, N4.PW0
CW_BOBBY = N4.CW_BOBBY; V_REV = N4.V_REV
ADMIN = {'perm05': (0.5, False), 'ramp': (1.0, True), 'full': (1.0, False)}   # (stress dai han, tre 1 nam: 0,5 o 2028)
ADMIN_BASE = 'ramp'

_np4 = S.nprice


def nprice(k, y, P):
    if P.get('ramp') and y == 2028:
        P = {**P, 'stress': P.get('stress', 0.0) * 0.5}
    return _np4(k, y, P)


S.nprice = nprice; R.nprice = nprice


def branch(name, over=None, v_rev=V_REV, cap_basis='branch', admin=ADMIN_BASE, cap_abs=None):
    o = dict(over or {})
    if name == 'STRUCTURAL':
        o.update(stress=0.0, nnc_vol=(1.40, 1.40), ramp=False); cap = S.P_CYC
    else:
        st, rp = ADMIN[admin] if name == 'ADMIN_GATED' else (1.0, False)
        o.update(stress=st, ramp=rp, nnc_vol=v_rev)
        if 'tl_vol' not in o: o['tl_vol'] = v_rev
        cap = cap_abs or N4.cap_for(N4.eff_vol(v_rev) if cap_basis == 'branch' else 1.40)
    old = S.P_CYC; S.P_CYC = cap
    try:
        vn, vm, _ = N3.EV3(o, detail=True)
    finally:
        S.P_CYC = old
    return vn, vm


def EV5(over=None, cw=CW_BOBBY, v_rev=V_REV, cap_basis='branch', admin=ADMIN_BASE, cap_abs=None, detail=False):
    b = {n: branch(n, over, v_rev, cap_basis, admin, cap_abs) for n in cw}
    vn = sum(cw[n] * b[n][0] for n in cw); vm = sum(cw[n] * b[n][1] for n in cw)
    return (vn, vm, b) if detail else vn


Ws = [{'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05}, W0, {'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05}]
PWs = [{'g2031': .7, 'real': .3}, PW0, {'g2031': .3, 'real': .7}]
CWs = [CW_BOBBY, {'STRUCTURAL': .40, 'ADMIN_GATED': .35, 'CYCLICAL': .25}, {'STRUCTURAL': .15, 'ADMIN_GATED': .35, 'CYCLICAL': .50}]
VRs = [(1.05, 1.05), V_REV, (1.20, 1.30)]
AMs = ['perm05', 'ramp', 'full']


def _cell(a):
    r, kk, wi, pi, ci, vi, cb, am = a
    vnn, vmm, _ = EV5({'r': r, 'K': kk, 'W': Ws[wi], 'PW': PWs[pi]}, cw=CWs[ci], v_rev=VRs[vi], cap_basis=cb, admin=am, detail=True)
    return dict(r=r, K=kk, W=wi, PW=pi, CW=ci, VR=vi, cap=cb, admin=am, ev=vnn, ev_mvc=vmm)


if __name__ == '__main__':
    out = {}
    vn, vm, b = EV5(detail=True); out['tam'] = vn; out['mvc_simul'] = vm
    out['branches'] = {n: dict(w=CW_BOBBY[n], V_NNC=b[n][0], V_MVC=b[n][1]) for n in b}
    out['sc3'] = {'tich_cuc': b['STRUCTURAL'][0], 'co_so': b['ADMIN_GATED'][0], 'tieu_cuc': b['CYCLICAL'][0]}
    print(f'=== 1. TAM NNC r5 (Bobby 20/45/35; ADMIN 0,5@2028->1,0; W 25/50/20/5 x PW 50/50; r13; K 0,97): {vn:,.0f} d/cp | MVC dong thoi {vm:,.0f}')
    for n in b: print(f'  {n:11s} w {CW_BOBBY[n]:.2f}: NNC {b[n][0]:8,.0f} | MVC {b[n][1]:7,.0f}')
    out['admin_axis'] = {}
    for am in AMs:
        x, y, _ = EV5(admin=am, detail=True); out['admin_axis'][am] = dict(V_NNC=x, V_MVC=y)
        print(f'  anh xa ADMIN {am:6s}: tam {x:8,.0f} ({x-vn:+7,.0f}) | MVC {y:7,.0f}')
    out['branch_path'] = {}
    for n in CW_BOBBY:
        for p in PATHS:
            x, y = branch(n, {'PW': {p: 1.0}}); out['branch_path'][f'{n}|{p}'] = dict(V_NNC=x, V_MVC=y)

    print('\n=== 2. Bien o tran chu ky (tien 2026) ===')
    ev_ = N4.eff_vol(V_REV); cu = N4.unit_cost(ev_); cap = N4.cap_for(ev_)
    m_real = 1 - cu / cap; m_g31 = 1 - cu * 1.03 ** 4 / cap
    print(f'  tran {cap:.1f}k, chi phi {cu:.1f}k @SL {ev_:.3f}: bien duong thuc {m_real:.1%} (giu gia tri thuc) ; duong g2031 nam 2030 {m_g31:.1%}')
    out['margin'] = dict(cap=cap, cost=cu, real=m_real, g2031_2030=m_g31, cap140=N4.cap_for(1.40))

    print('\n=== 3. Gordon P/B = (ROE-g)/(r-g), r13 g3; ROE chuan hoa nhat quan anh xa (ADMIN = CYC o nam dien hinh 2031+) ===')
    fin = 15.60 / 0.75 * (1 - M.TAX)   # DT tai chinh 9T/26 15,60 ty [Q3 VI.3] nam hoa, sau thue
    gor = {}
    for n in CW_BOBBY:
        npt, p, v = N4.nopat_norm('CYCLICAL' if n == 'ADMIN_GATED' else n)
        gor[n] = dict(nopat=npt, p=p, v=v, roe_lock=npt / N4.BV_NNC, roe_fin=(npt + fin) / N4.BV_NNC)
    for key in ('roe_lock', 'roe_fin'):
        rw = sum(CW_BOBBY[n] * gor[n][key] for n in CW_BOBBY); pb = (rw - .03) / .10
        gor['tron_' + key] = dict(roe=rw, pb=pb, ps=pb * N3.BVPS_NNC)
        print(f'  {"ban khoa (khong LN tai chinh)" if key=="roe_lock" else "ban bo sung (+LN tai chinh)":32s}: ROE tron {rw:.1%} -> P/B {pb:.2f}x -> {pb*N3.BVPS_NNC:,.0f} d/cp')
    for am in ('perm05',):
        pass
    out['gordon'] = gor; out['gordon_fin_after_tax'] = fin
    print(f'  ROE ben ham y cua TAM {vn:,.0f} (P/B {vn/N3.BVPS_NNC:.2f}x): {.03 + vn/N3.BVPS_NNC*.10:.1%}')

    print('\n=== 4. Luoi 4.374 bo (r4 x truc anh xa ADMIN) ===')
    args = list(itertools.product((0.11, 0.13, 0.15), (0.87, 0.97, 1.07), range(3), range(3), range(3), range(3), ('branch', '1.40'), AMs))
    with Pool(6) as pool: grid = pool.map(_cell, args, chunksize=40)
    ge = np.array([x['ev'] for x in grid]); gp = {q: float(np.percentile(ge, q)) for q in (5, 10, 25, 50, 75, 90, 95)}
    gp['min'] = float(ge.min()); gp['max'] = float(ge.max())
    print(f'  N={len(ge)}: ' + ' '.join(f'P{q} {v:,.0f}' for q, v in gp.items()))
    sub = {}
    for key, labs in [('admin', None), ('CW', ['Bobby', 'nghieng STRUCT', 'nghieng CYC']), ('VR', ['SL 1,05', 'SL 1,10/1,20', 'SL 1,20/1,30']), ('cap', None)]:
        for v in sorted(set(x[key] for x in grid), key=str):
            s_ = np.array([x['ev'] for x in grid if x[key] == v]); lab = labs[v] if labs else v
            sub[f'{key}={lab}'] = dict(p10=float(np.percentile(s_, 10)), p50=float(np.median(s_)), p90=float(np.percentile(s_, 90)))
            print(f'   {key}={lab}: P10 {np.percentile(s_,10):,.0f} P50 {np.median(s_):,.0f} P90 {np.percentile(s_,90):,.0f}')
    out['grid_pct'] = gp; out['grid_n'] = len(ge); out['grid_sub'] = sub
    with open('grid_r5.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    print('NGUONG (dang ky truoc): RE <= {:,.0f} | RE CO DIEU KIEN {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | NGHIENG DAT {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))

    print('\n=== 5. Do nhay (so voi tam r5) ===')
    tor = {}
    def T(lab, over=None, **kw):
        x = EV5(over, **kw); tor[lab] = x - vn; print(f'  {lab:84s} {x:8,.0f} ({x - vn:+7,.0f})')
    T('tran chu ky 242,5k (neo skeptic)', cap_abs=242.5); T('tran chu ky SL 1,40 = %.1fk' % N4.cap_for(1.40), cap_basis='1.40')
    T('anh xa ADMIN 0,5 vinh vien (= r4)', admin='perm05'); T('anh xa ADMIN 1,0 tu 2028 (khong tre)', admin='full')
    T('trong so nghieng STRUCTURAL 40/35/25', cw=CWs[1]); T('trong so nghieng CYCLICAL 15/35/50', cw=CWs[2])
    T('chi CYCLICAL', cw={'CYCLICAL': 1.0}); T('chi STRUCTURAL (= tam r3)', cw={'STRUCTURAL': 1.0})
    T('SL nam thuong 1,05 ca ky', v_rev=(1.05, 1.05)); T('SL nam thuong 1,20/1,30', v_rev=(1.20, 1.30))
    T('(+) upside doi thu het GP: tu 2034 stress giam mot nua', {'up2034': True})
    T('K chi phi 0,87', {'K': 0.87}); T('K chi phi 1,07', {'K': 1.07}); T('r 11%', {'r': 0.11}); T('r 15%', {'r': 0.15})
    T('PW g2031 70/real 30', {'PW': PWs[0]}); T('PW g2031 30/real 70', {'PW': PWs[2]})
    T('STRESS duong gia danh nghia phang 100%', {'PW': {'flat': 1.0}})
    T('bo LN cho thue Nui Nho (thoi han CHUA XAC MINH)', {'rent': False})
    # thue toi 2030: ty le PV 2031-2043 trong PV 2027-2043 cua dong LN thue (tang 3%/nam, chiet khau 13%)
    pvf = {y: 1.03 ** (y - 2026) / 1.13 ** (y - 2026) for y in range(2027, 2044)}
    fr = sum(v for y, v in pvf.items() if y >= 2031) / sum(pvf.values())
    tor['cho thue Nui Nho chi toi 2030 (xap xi ty le PV)'] = fr * tor['bo LN cho thue Nui Nho (thoi han CHUA XAC MINH)']
    print(f'  {"cho thue Nui Nho chi toi 2030 (xap xi = %.0f%% PV dong thue)" % (fr*100):84s} {vn+tor["cho thue Nui Nho chi toi 2030 (xap xi ty le PV)"]:8,.0f} ({tor["cho thue Nui Nho chi toi 2030 (xap xi ty le PV)"]:+7,.0f})')
    pp = sum(12.8 / 1.13 ** (i + 0.5) for i in range(4)) + 0.6 * 12.8 / 1.13 ** 4.5
    T('(+) tra truoc dai han CNBP 59,2 la tien thue da tra (ban chat CHUA XAC MINH)', {'extra': pp})
    T('bo doi xung BCDKT', {'bs_sym': False}); T('holding MVC->NNC 15%', {'hold': 0.15})
    out['tornado'] = tor
    out['bridge'] = dict(r4=EV5(admin='perm05'), r5=vn)
    print(f'\n  Cau noi: tam r4 (ADMIN 0,5 vinh vien) {out["bridge"]["r4"]:,.0f} -> r5 {vn:,.0f}')
    print(f'\n=== 6. V_NNC cho MVC r8: {vn:,.0f} d/cp (MVC dong thoi {vm:,.0f}) ===')
    with open('nnc_model_r5_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
