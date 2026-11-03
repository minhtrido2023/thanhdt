"""DD NNC r3 (03/11/2026 ~20:10 ICT) — DUNG LAI theo nguyen tac user 03/11 17:06 (du an moi base = so sach/NPV 0; lech chi khi co co so
doc lap; AP DOI XUNG khoan cong lan khoan tru). MU GIA: khong doc gia/von hoa/P-E NNC hay MVC trong file nay.
Chay: /home/trido/thanhdt/wc_venv/bin/python -B model_r3.py
He thong: tai dung mo hinh MVC r6 (../../../dd_MVC_20261103/r6/calc: valuation_base.py, model_r5.py, model_r6.py — KHONG SUA, md5 ghi o LOCK).
V_NNC = N_ex + c*V_MVC ; V_MVC = D_MVC + s*V_NNC (c=0,103 NNC->MVC ; s=0,4407 MVC->NNC ; holding 0) — D1: KHONG dung gia thi truong MVC/NNC.

KIEM KE (bang day du: ../INVENTORY_r3.md). Thay doi so voi khoi NNC trong MVC r6 (V_NNC 83.887):
 (a) San luong NNC co_so 2028+ 1,10/1,20 -> 1,40 (= muc 2026, 1,42 tr m3 thanh pham = tran GP [BCTN25 tr.6]; 2025 '100% cong suat' [BCTN25 tr.20]).
     Cat san luong 2028-30 khong co nguon do lon (FPTS base 0,8 tu 2028 khong neu ly do; huong co co so: cung moi cum) -> do nhay.
 (b) Doi xung bang can doi: da tru du phong phuc hoi moi truong 4,50 va du phong truy thu 22,37 => CONG ky quy PHMT 4,57 [Q3 V9]
     + tai san thue hoan lai 4,31 ghi tren 2 khoan truy thu [Q3 V19a/tr.2].
 (c) CIP Tam Lap 1 khu II 83,5 o SO SACH moi kich ban (r6 da lam) + chi phi tre GP ky vong theo Bobby F6 P(tre 0/1/2 nam)=0,30/0,40/0,30
     (doi xung voi mo moi MVC r6).
 Giu nguyen r6: gia co_so truot 360/340/320 (2028-30) roi 320 (moc = hoi GPM ve gan TB chu ky), tot 420/400/420 (Bobby F2 P(>+7%)=0,30),
 xau/rat_xau = kich ban co xac suat (FPTS 0,8x250 / mat bang 2023-24), W 25/50/20/5, PW g2031 50/real 50 (phang = STRESS), r 13%,
 K chi phi 0,97 [KT25 7.2], LN cho thue Nui Nho 11,13 [KT25 7.1-7.2], NHC so sach, Q4/26 60 (uoc luong; Q3/26 thuc 69,3), thue 20%.
NGUONG (DANG KY TRUOC KHI CHAY; khong sua sau khi thay so). Luoi 729 bo: r 11/13/15 x K NNC 0,87/0,97/1,07 x W {15/60/20/5, 25/50/20/5,
 35/50/10/5} x PW g2031:real {70:30,50:50,30:70} x stress bien cum ve TB chu ky {0, 0,5, 1} x han GP Tan Lap (MVC) {2035, W, 2045}:
  RE <= P10 ; RE CO DIEU KIEN P10-P25 ; HOP LY P25-P75 ; NGHIENG DAT P75-P90 ; DAT >= P90.
  'Bien an toan' chi dung kem dieu kien (muc bien cum toi thieu de tam >= gia) — tinh o compare_r3.py SAU khoa.
"""
import sys, os, itertools, json, csv
import numpy as np
sys.dont_write_bytecode = True
R6 = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../dd_MVC_20261103/r6/calc'))
sys.path.insert(0, R6)
import model_r6 as S          # noqa: E402  (patch R.nprice/tanlap/solve khi import)
M, R = S.M, S.R
SCN, PATHS, W0, PW0 = S.SCN, S.PATHS, S.W0, S.PW0
N_SH = M.N_SH
KYQUY, DTA = 4.57, 4.31
BVPS_NNC = 29915.0   # VCSH 30/09/2026 / 21,92 tr cp (REPORT §7)
DELAY_P = {0: .30, 1: .40, 2: .30}
BASE3 = dict(nnc_vol=(1.40, 1.40), bs_sym=True, cip_delay=True, K=0.97, rent=True, extra=0.0)

_nnc_ex6 = R.nnc_ex


def nnc_ex(k, path, P):
    oldK, oldR = M.K, M.RENT
    M.K = P.get('K', 0.97)
    if not P.get('rent', True): M.RENT = 0.0
    try:
        v = _nnc_ex6(k, path, P)
    finally:
        M.K, M.RENT = oldK, oldR
    if P.get('bs_sym'): v += KYQUY + DTA
    if P.get('cip_delay'): v -= sum(p * M.n_cip * (1 - (1 + P['r']) ** -d) for d, p in DELAY_P.items())
    return v + P.get('extra', 0.0)


R.nnc_ex = nnc_ex


def EV3(over=None, detail=False):
    P = {**BASE3, **(over or {})}
    ev_m, res = S.EV(P, detail=True)
    Wd, PWd = P.get('W', W0), P.get('PW', PW0)
    vn = sum(Wd[k] * PWd[p] * res[(k, p)]['V_NNC_ps'] for k in SCN for p in PWd)
    return (vn, ev_m, res) if detail else vn


def ex_only(k, path, P):
    """gia tri NNC TU THAN (khong gom co phan MVC) — d/cp"""
    return nnc_ex(k, path, {**R.BASE, **S.BASE6, **BASE3, **P}) * 1e9 / N_SH


if __name__ == '__main__':
    out = {}
    gpm = [float(x) for x in '0.35 0.21 0.36 0.35 0.37 0.43 0.34 0.30 0.37 0.40 0.21 0.28 0.32 0.49'.split()]
    print(f'P_CYC (gia chu ky, tien 2026) {S.P_CYC:.0f}k/m3 = 380 x (1-0,533)/(1-{np.mean(gpm):.3f}); GPM TB NNC 2012-25 {np.mean(gpm):.3f}')
    vn, vm, res = EV3(detail=True); out['tam'] = vn; out['mvc_simul'] = vm
    base = sum(PW0[p] * res[('co_so', p)]['V_NNC_ps'] for p in PATHS); out['base_co_so'] = base
    print(f'=== TAM NNC r3 (W 25/50/20/5 x PW g2031 50/real 50; r13; K 0,97; SL co_so 1,40; doi xung BCDKT; CIP so sach - tre GP): {vn:,.0f} d/cp | BASE co_so {base:,.0f}')
    cells = {}
    for p in PATHS:
        print(f'  {p:5s}: ' + ' '.join(f'{k} {res[(k, p)]["V_NNC_ps"]:7,.0f}' for k in SCN))
        for k in SCN: cells[f'{k}|{p}'] = res[(k, p)]['V_NNC_ps']
    out['cells'] = cells
    sc3 = {'tich_cuc': sum(PW0[p] * cells[f'tot|{p}'] for p in PATHS), 'co_so': base,
           'tieu_cuc': sum(PW0[p] * (0.20 * cells[f'xau|{p}'] + 0.05 * cells[f'rat_xau|{p}']) / 0.25 for p in PATHS)}
    out['sc3'] = sc3; print('  3 kich ban NDT (25/50/25): ' + ' | '.join(f'{a} {b:,.0f}' for a, b in sc3.items()))

    # ---- cau noi co_so (ty) — tung manh
    P = {**R.BASE, **S.BASE6, **BASE3}
    br = {}
    for p in PATHS:
        a = M.NNC_SCN['co_so']; cf = []
        oldK = M.K; M.K = 0.97
        for y in range(2027, 2044):
            v = 1.40; f = 1.03 ** (y - 2026)
            ebit = v * (R.nprice('co_so', y, P) * R.g(y, p) - M.VAR * M.K * f) - M.FIX * M.K * f - M.SGA * f + M.RENT * f
            cf.append((y, max(ebit, 0) * (1 - M.TAX)))
        M.K = oldK
        dcf = M.pv(cf, P['r'])
        dly = sum(pp * M.n_cip * (1 - 1.13 ** -d) for d, pp in DELAY_P.items())
        c = res[('co_so', p)]
        br[p] = dict(DCF_Mui_Tau_2027_43_gom_cho_thue=dcf, Q4_2026=M.n_q4, tien_rong_sau_nghia_vu=M.n_cash, ky_quy_PHMT=KYQUY, thue_hoan_lai=DTA,
                     NHC_so_sach=M.n_nhc_book, CIP_TamLap_so_sach=M.n_cip, tre_GP_ky_vong=-dly, co_phan_MVC_10_3pct=M.c_MVC * c['VM'],
                     TONG=c['N_ex'] + M.c_MVC * c['VM'], TONG_dcp=c['V_NNC_ps'])
        print(f'[{p}] ' + ' | '.join(f'{a} {v:,.1f}' for a, v in br[p].items()))
    out['bridge'] = br

    # ---- Gordon P/B kiem cheo (NNC: mo huu han 2043 + tien lon => Gordon chi la doi chieu tho)
    roe = [.4729, .4005, .4764, .4769, .4880, .4139, .4474, .3802, .3770, .1300, .1193, .1006, .1547, .3011]
    gor = {}
    print('\n=== Kiem Gordon P/B=(ROE-g)/(r-g), r13 g3, BVPS 29.915 ===')
    for lab, x in [('ROE 12%', .12), ('ROE TB 2021-25 (mot mo) %.1f%%' % (100 * np.mean(roe[9:])), float(np.mean(roe[9:]))), ('ROE 20%', .20),
                   ('ROE TB 2012-25 %.1f%% (gom thoi 2 mo)' % (100 * np.mean(roe)), float(np.mean(roe))), ('ROE Q3/26 TTM 35,9% (tham chieu)', .3592)]:
        pb = (x - .03) / .10; gor[lab] = dict(pb=pb, ps=pb * BVPS_NNC); print(f'  {lab:40s} P/B {pb:4.2f}x -> {pb*BVPS_NNC:8,.0f}')
    out['gordon'] = gor; out['roe_implied_by_tam'] = .03 + vn / BVPS_NNC * .10
    print(f'  ROE ben ham y cua TAM {vn:,.0f} (P/B {vn/BVPS_NNC:.2f}x): {out["roe_implied_by_tam"]:.1%}')

    # ---- luoi 729
    Ws = [{'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05}, W0, {'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05}]
    PWs = [{'g2031': .7, 'real': .3}, PW0, {'g2031': .3, 'real': .7}]
    grid = []
    for r, kk, wi, pi, st, en in itertools.product((0.11, 0.13, 0.15), (0.87, 0.97, 1.07), range(3), range(3), (0.0, 0.5, 1.0), (2035, 'W', 2045)):
        grid.append(dict(r=r, K=kk, W=wi, PW=pi, stress=st, endA=en, ev=EV3({'r': r, 'K': kk, 'W': Ws[wi], 'PW': PWs[pi], 'stress': st, 'endA': en})))
    ge = np.array([x['ev'] for x in grid]); gp = {q: float(np.percentile(ge, q)) for q in (5, 10, 25, 50, 75, 90, 95)}
    gp['min'] = float(ge.min()); gp['max'] = float(ge.max())
    print(f'\n=== Luoi {len(ge)} bo: ' + ' '.join(f'P{q} {v:,.0f}' for q, v in gp.items()))
    for st in (0.0, 0.5, 1.0):
        sub = np.array([x['ev'] for x in grid if x['stress'] == st]); print(f'   stress {st}: P10 {np.percentile(sub,10):,.0f} P50 {np.median(sub):,.0f} P90 {np.percentile(sub,90):,.0f}')
    out['grid_pct'] = gp; out['grid_n'] = len(ge)
    with open('grid_r3.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    print('NGUONG (dang ky truoc): RE <= {:,.0f} | RE CO DIEU KIEN {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | NGHIENG DAT {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))

    # ---- kiem ke: hieu ung tung khoan (dua lai khoan cu / do nhay co nhan)
    print('\n=== Kiem ke & do nhay (so voi tam r3) ===')
    tor = {}
    def T(lab, **kw):
        x = EV3(kw); tor[lab] = x - vn; print(f'  {lab:78s} {x:8,.0f} ({x - vn:+7,.0f})')
    T('[cu] SL co_so 1,10 (2028-30) / 1,20 (2031+) (khoi NNC trong MVC r6)', nnc_vol=(1.10, 1.20))
    T('SL co_so 1,20 ca ky 2028+', nnc_vol=(1.20, 1.20))
    T('[cu] bo doi xung BCDKT (khong cong ky quy 4,57 + thue hoan lai 4,31)', bs_sym=False)
    T('bo chi phi tre GP Tam Lap 1 khu II (CIP so sach tron)', cip_delay=False)
    T('[cu] CIP Tam Lap chi o tot/co_so (xau/rat_xau = 0)', cip_all=False)
    T('[cu] vach gia co_so 300 (2028-30) thay truot 360/340/320', glide=False)
    T('stress bien cum 0,5 tu 2028', stress=0.5); T('stress bien cum 1,0 (GPM ve TB 2012-25) tu 2028', stress=1.0)
    T('STRESS duong gia danh nghia phang 100%', PW={'flat': 1.0})
    T('[cu] PW them phang 10% (10/50/40)', PW={'flat': .1, 'g2031': .5, 'real': .4})
    T('K chi phi 0,87', K=0.87); T('K chi phi 1,07', K=1.07)
    T('r 11%', r=0.11); T('r 15%', r=0.15)
    T('W 15/60/20/5', W={'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05}); T('W 35/50/10/5', W={'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05})
    T('[cu] W 20/45/25/10', W={'tot': .20, 'co_so': .45, 'xau': .25, 'rat_xau': .10})
    T('bo LN cho thue Nui Nho', rent=False)
    T('holding MVC->NNC 15% (MVC phia cau)', hold=0.15)
    T('MVC: han GP Tan Lap 2035', endA=2035); T('MVC: han GP Tan Lap 2045', endA=2045)
    T('MVC: mo moi hai phia co trong so (phia MVC)', up=True, mine_xau=True)
    T('(+) may nghien 350t/h CIP 24,5 o gia von (neu la mo rong, khong thay the)', extra=24.5)
    T('(+) tra truoc dai han CNBP 59,2: PV khau tru phi tien mat 12,8/nam x 4,6 nam (CHUA XAC MINH ban chat)', extra=sum(12.8 / 1.13 ** (i + 0.5) for i in range(4)) + 0.6 * 12.8 / 1.13 ** 4.5)
    # stress bien tren CHI PHI MO HINH: gia de GPM da (mo hinh) ve ~36% (= TB toan cong ty 34,2% + ~2pp hang hoa/dich vu) ; P_CYC r6 dung ty le GPM toan cong ty
    c_unit = M.VAR * 0.97 + M.FIX * 0.97 / 1.40; p36 = c_unit / (1 - 0.36); s36 = (320 - p36) / (320 - S.P_CYC)
    out['stress_model_cost'] = dict(cost_unit=c_unit, p=p36, s=s36)
    _pc = S.P_CYC; S.P_CYC = p36   # tran gia = p36 moi kich ban tu 2028 (stress 1,0 voi tran moi; khong ngoai suy s>1)
    T(f'STRESS bien da ve GPM 36% tren chi phi mo hinh (tran gia {p36:.0f}k tu 2028 moi kich ban, cum; NGOAI luoi)', stress=1.0)
    S.P_CYC = _pc
    out['tornado'] = tor
    print('  Tam Lap 1 khu II upside: KHONG dinh luong (chua co GP, tru luong, cong suat, capex cong bo; AWM thu cap) -> 0 o tam, chi neu dinh tinh')

    # ---- V_NNC cho MVC
    ref = {'NNC-DD cong bo (77.656)': 77656, 'V_NNC nhat quan MVC r6 (83.887)': 83887}
    out['vnnc_for_mvc'] = {lab: dict(v_old=v, v_new=vn, d_nnc=vn - v, d_mvc_slope=(vn - v) / 10000 * 966) for lab, v in ref.items()}
    print('\n=== V_NNC cho MVC (do doc 966 d/cp MVC moi 10.000 d/cp NNC, MVC r6) ===')
    for lab, d in out['vnnc_for_mvc'].items():
        print(f'  so {lab}: V_NNC moi {vn:,.0f} ({d["d_nnc"]:+,.0f}) -> MVC {d["d_mvc_slope"]:+,.0f} d/cp')
    print(f'  (doi chieu: MVC giai dong thoi trong he r3 = {vm:,.0f} d/cp; KHONG phai so MVC moi — Mike dung lai MVC)')
    with open('model_r3_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
