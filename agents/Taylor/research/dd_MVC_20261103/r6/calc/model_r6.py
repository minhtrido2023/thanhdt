"""DD MVC r6 (03/11/2026 ~17:45 ICT) — SUA DOI XUNG sau SKEPTIC4: nguyen tac user (du an moi base = so sach/NPV 0; lech chi khi co
co so doc lap) ap CA KHOAN CONG LAN KHOAN TRU. MU GIA: khong doc gia/von hoa/P-E MVC hay NNC. Gia chi o compare_r6.py SAU khi khoa md5.
Chay: /home/trido/thanhdt/wc_venv/bin/python -B model_r6.py   (tai dung model_r5.py + valuation_base.py KHONG SUA, md5 o LOCK)

THAY DOI r6 so voi r5:
 (1) Dat du an nha o: r5 ky vong 150 ty (400/100/0/0) -> SO SACH 30 ty moi kich ban (SKEPTIC4 #1: ~23,5-30 ty, 2 lo da xac dinh;
     chua doi chieu thuyet minh tung lo = uoc luong). Gia tri phat trien = OPTION NGOAI TAM, neu rieng (+1.200 d/cp neu ky vong r5).
 (2) Mo moi = SO SACH 438,4 o MOI kich ban (up=False). Upside IRR kich ban tot (+) va NPV gia xau/rat xau (-) CA HAI ra do nhay co nhan;
     them phuong an "hai phia co trong so" lam doi chieu. Rui ro tre GP (Bobby F6, P 0,30/0,40/0,30) GIU — co co so quan sat.
 (3) Bo lap luan chi phi von hon hop 5,98%; NPV mo moi bao o r 11/13/15%.
 (4) Kiem Gordon P/B voi ROE chuan hoa 9/12/13,5% (18,5% hien tai chi tham chieu) + 2 TRUC MOI trong luoi:
     stress bien da cum ve trung binh chu ky (0 / 0,5 / 1) va han GP Tan Lap (2035 moi kb / W theo kb / 2045 moi kb — doi xung).
     Trung binh chu ky: GPM NNC (mo da thuan, cung cum) Q4 2012-2025 TB 34,2% vs 53,3% Q3/26 TTM (BQ ticker_financial, chi GPM/ROE).
     Gia chu ky (tien 2026, chi phi giu nguyen) = 380 x (1-0,533)/(1-0,342). Ap tu 2028 cho Tan Lap + NNC (cung cum).
 (5) San luong cum: NNC co_so 1,10 (2028-30) GIU = NNC-DD da cong bo (co so: FPTS base 0,8 tr m3 tu 2028 cho rieng NNC — chua ro ly do,
     NNC-DD ghi CHUA RA); Tan Lap 1,30. Do nhay: NNC 1,20 / 1,30 ca ky; Tan Lap 1,10 2028-30 (cat doi xung cum).
 (6) No rong: lo trinh capex base (uoc luong) thay nguong 600 ty tuyet doi.
 (7) Phu thuoc V_NNC: tam dung V_NNC nhat quan (vong cheo); do nhay V_NNC co dinh 77.656 (NNC-DD cong bo) + do doc d/cp MVC moi 10.000 d NNC.
NGUONG (DANG KY TRUOC KHI CHAY; khong sua sau khi thay so). Luoi 2.187 bo: r 11/13/15 x chi phi Tan Lap 0,85/1/1,15 x REL 0,88/0,91/0,95 x
 W {15/60/20/5, 25/50/20/5, 35/50/10/5} x PW g2031:real {70:30,50:50,30:70} x stress bien {0, 0,5, 1} x han GP Tan Lap {2035, W, 2045}:
  RE (duoi P10) <= P10 ; RE CO DIEU KIEN P10-P25 ; HOP LY P25-P75 ; NGHIENG DAT P75-P90 ; DAT >= P90.
  "Bien an toan" CHI dung kem dieu kien (muc bien da cum toi thieu de tam >= gia) — tinh o compare_r6.py sau khoa.
"""
import sys, itertools, json, csv
import numpy as np
sys.dont_write_bytecode = True
import valuation_base as M
import model_r5 as R

SCN = R.SCN; PATHS = R.PATHS; W0 = R.W0; PW0 = R.PW0
# --- GPM NNC (Q4 TTM) 2012-2025 + Q3/26 (bq ticker_financial, 03/11 17:40) ; MVC ROE trailing Q4 2017-2025 + Q3/26
GPM_NNC = [.349, .212, .361, .349, .367, .428, .341, .300, .370, .402, .214, .279, .316, .494]
GPM_NOW = 0.533
ROE_MVC = {2017: .097, 2018: .133, 2019: .089, 2020: .065, 2021: -.036, 2022: .049, 2023: .061, 2024: .071, 2025: .136}
ROE_NOW = 0.207   # Q3/26 trailing BQ; REPORT r5 dung 18,5% (Q2/26 0,183)
GPM_CYC = float(np.mean(GPM_NNC))
P_CYC = 380 * (1 - GPM_NOW) / (1 - GPM_CYC)
LAND_BOOK = 30.0
BVPS = 15460.0     # VCSH HN 30/09/26 1.546,0 ty / 100 tr cp
_np5 = R.nprice


def nprice(k, y, P):
    p = _np5(k, y, P); s = P.get('stress', 0.0)
    if y >= 2028 and s > 0:
        p = (1 - s) * p + s * min(p, P_CYC)
    return p


def tanlap(k, path, endA, P):
    vol = {'tot': (1.40, 1.40), 'co_so': (1.30, 1.30), 'xau': (1.30, 1.05), 'rat_xau': (0.90, 0.90)}[k]
    out = []
    for y in range(2027, endA + 1):
        v = vol[0] if y == 2027 else vol[1]
        if k == 'co_so' and P.get('tl_cut') and 2028 <= y <= 2030: v = 1.10
        f = 1.03 ** (y - 2026)
        ebit = v * (P['REL'] * nprice(k, y, P) * R.g(y, path) - R.costA(P) * f) - M.SGA_A * f
        out.append((y, max(ebit, 0) * (1 - M.TAX)))
    return M.pv(out, P['r'])


def solve(Dm, N_ex, P):
    if P.get('VN_fix'):
        return Dm + (1 - P['hold']) * M.s_NNC * P['VN_fix'] * M.N_SH / 1e9
    return R._solve5(Dm, N_ex, P)


R._solve5 = R.solve
R.nprice = nprice; R.tanlap = tanlap; R.solve = solve

BASE6 = dict(up=False, delay=True, mine_xau=False, hold=0.0, stress=0.0, endA='W', nnc_vol=None, tl_cut=False, VN_fix=None)
LAND_R6 = {k: LAND_BOOK for k in SCN}
LAND_R5 = {'tot': 400, 'co_so': 100, 'xau': 0, 'rat_xau': 0}


def EV(over=None, detail=False, land=None):
    P = {**BASE6, **(over or {})}
    oldL, oldE, oldN = dict(M.LAND), dict(M.END_A), dict(M.NNC_SCN)
    M.LAND.update(land or LAND_R6)
    if P['endA'] != 'W': M.END_A.update({k: P['endA'] for k in SCN})
    if P['nnc_vol']:
        a = list(M.NNC_SCN['co_so']); a[1], a[4] = P['nnc_vol']; M.NNC_SCN['co_so'] = tuple(a)
    try:
        return R.EV(P, detail=detail)
    finally:
        M.LAND.clear(); M.LAND.update(oldL); M.END_A.clear(); M.END_A.update(oldE); M.NNC_SCN.clear(); M.NNC_SCN.update(oldN)


if __name__ == '__main__':
    out = {}
    print(f'GPM NNC chu ky TB {GPM_CYC:.3f} vs nay {GPM_NOW}; gia chu ky (tien 2026) {P_CYC:.0f}k/m3 NNC = {P_CYC/380:.3f}x 380; '
          f'MVC {0.91*P_CYC:.0f}k, bien don vi Tan Lap {0.91*P_CYC-R.costA(R.BASE):.0f}k vs dinh {0.91*380-R.costA(R.BASE):.0f}k '
          f'= {(0.91*P_CYC-R.costA(R.BASE))/(0.91*380-R.costA(R.BASE)):.0%} bien dinh')
    out['cycle'] = dict(gpm_cyc=GPM_CYC, gpm_now=GPM_NOW, p_cyc=P_CYC,
                        unit_margin_frac=(0.91 * P_CYC - R.costA(R.BASE)) / (0.91 * 380 - R.costA(R.BASE)))
    ev, res = EV(detail=True); out['tam'] = ev
    base_ps = sum(PW0[p] * res[('co_so', p)]['ps'] for p in PATHS); out['base_co_so'] = base_ps
    print(f'=== TAM r6 (W 25/50/20/5 x PW g2031 50/real 50; r13; holding 0; mo moi so sach MOI kb; dat o so sach 30): {ev:,.0f} d/cp | BASE co_so {base_ps:,.0f}')
    for p in PATHS:
        print(f'  {p:5s}: ' + ' '.join(f'{k} {res[(k, p)]["ps"]:7,.0f}' for k in SCN))
    out['cells'] = {f'{k}|{p}': res[(k, p)]['ps'] for k in SCN for p in PATHS}
    e2, r2 = EV({'PW': {'flat': 1.0}}, detail=True)
    out['stress_flat'] = dict(kv=e2, co_so=r2[('co_so', 'flat')]['ps'])
    out['stress_margin1'] = EV({'stress': 1.0}); out['stress_margin05'] = EV({'stress': 0.5})
    print(f'  STRESS phang danh nghia 100%: KV {e2:,.0f} | co_so {r2[("co_so","flat")]["ps"]:,.0f}')
    print(f'  STRESS bien cum ve TB chu ky tu 2028: 0,5 -> {out["stress_margin05"]:,.0f} ; 1,0 -> {out["stress_margin1"]:,.0f}')
    two = EV({'up': True, 'mine_xau': True}); out['two_sided'] = two
    print(f'  DOI CHIEU mo moi hai phia co trong so (upside tot + NPV xau/rat xau): {two:,.0f} ({two-ev:+,.0f})')

    print('\n=== 1. CAU NOI co_so (ty; d/cp = x10) ===')
    br = {}
    for p in PATHS:
        c = res[('co_so', p)]
        b = dict(TanLap=c['A'], mo_moi_so_sach_sau_tre=c['B'], BOT=c['BOT'], gach_xang=c['gach_xang'], dat_o_so_sach=c['dat_o'],
                 LK_nho_ICD=c['LK_nho_ICD'], Q4=c['Q4'], no_rong=c['NETFIN'], TRUC_TIEP=c['Dm'], phan_NNC=c['stake'], TONG=c['VM'],
                 TONG_dcp=c['ps'], V_NNC_dcp=c['V_NNC_ps'])
        br[p] = b; print(f'[{p}] ' + ' | '.join(f'{a} {v:,.1f}' for a, v in b.items()))
    out['bridge'] = br
    nn = sum(W0[k] * PW0[p] * res[(k, p)]['V_NNC_ps'] for k in SCN for p in PATHS); out['NNC_tam'] = nn
    print(f'  V_NNC nhat quan (ky vong): {nn:,.0f} d/cp NNC')

    print('\n=== 2. Mo moi: NPV toan du an (gom 438,4 da chi) & IRR (khong vao tam) ===')
    mine = {}
    for k in SCN:
        for p in ('flat', 'g2031', 'real'):
            cf = R.mine_cf(k, p, R.BASE); i = R.irr(cf)
            n = {r: R.npv_total(k, p, R.BASE, r) for r in (0.11, 0.13, 0.15)}
            mine[f'{k}|{p}'] = dict(irr=i, **{f'npv{int(r*100)}': v for r, v in n.items()})
            print(f'  {k:7s} {p:5s}: IRR {i:6.1%} | NPV r11 {n[0.11]:7.0f} r13 {n[0.13]:7.0f} r15 {n[0.15]:7.0f}')
    out['mine'] = mine

    print('\n=== 3. Kiem Gordon P/B = (ROE-g)/(r-g), r13 g3, BVPS 15.460 ===')
    roe10 = float(np.mean(list(ROE_MVC.values()))); gor = {}
    for lab, roe in [('ROE 9%', .09), ('ROE 12%', .12), ('ROE 13,5%', .135), (f'ROE TB 2017-25 {roe10:.1%}', roe10), ('ROE hien tai 18,5% (tham chieu)', .185)]:
        pb = (roe - .03) / .10; gor[lab] = dict(pb=pb, ps=pb * BVPS); print(f'  {lab:32s} P/B {pb:4.2f}x -> {pb*BVPS:7,.0f}')
    roe_imp = .03 + ev / BVPS * .10; out['gordon'] = gor; out['roe_implied_by_tam'] = roe_imp; out['roe_mvc_avg_2017_25'] = roe10
    print(f'  ROE ben ham y cua TAM {ev:,.0f} (P/B {ev/BVPS:.2f}x): {roe_imp:.1%}')

    # ---------- 4. luoi 2.187
    grid = []
    Ws = [{'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05}, W0, {'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05}]
    PWs = [{'g2031': .7, 'real': .3}, PW0, {'g2031': .3, 'real': .7}]
    for r, ca, rel, wi, pi, st, en in itertools.product((0.11, 0.13, 0.15), (0.85, 1.0, 1.15), (0.88, 0.91, 0.95), range(3), range(3),
                                                         (0.0, 0.5, 1.0), (2035, 'W', 2045)):
        grid.append(dict(r=r, ca=ca, rel=rel, W=wi, PW=pi, stress=st, endA=en,
                         ev=EV({'r': r, 'ca': ca, 'REL': rel, 'W': Ws[wi], 'PW': PWs[pi], 'stress': st, 'endA': en})))
    ge = np.array([x['ev'] for x in grid]); gp = {q: float(np.percentile(ge, q)) for q in (5, 10, 25, 50, 75, 90)}
    gp['min'] = float(ge.min()); gp['max'] = float(ge.max())
    print(f'\n=== 4. Luoi {len(ge)} bo: ' + ' '.join(f'P{q} {v:,.0f}' for q, v in gp.items()))
    for st in (0.0, 0.5, 1.0):
        sub = np.array([x['ev'] for x in grid if x['stress'] == st]); print(f'   stress {st}: P10 {np.percentile(sub,10):,.0f} P50 {np.median(sub):,.0f} P90 {np.percentile(sub,90):,.0f}')
    out['grid_pct'] = gp; out['grid_n'] = len(ge)
    with open('grid_r6.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    print('NGUONG (dang ky truoc): RE <= {:,.0f} | RE CO DIEU KIEN {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | NGHIENG DAT {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))

    print('\n=== 5. Do nhay / kich ban co nhan (so voi tam r6) ===')
    tor = {}
    def T(lab, land=None, **kw):
        x = EV(kw, land=land); tor[lab] = x - ev; print(f'  {lab:72s} {x:8,.0f} ({x - ev:+7,.0f})')
    T('OPTION dat o theo ky vong r5 (400/100/0/0, khong co IRR/chu truong)', land=LAND_R5)
    T('dat o so sach 23,5', land={k: 23.5 for k in SCN})
    T('mo moi: + upside kich ban tot (IRR 17-21%)', up=True)
    T('mo moi: + NPV gia xau/rat xau (khong quyen dung)', mine_xau=True)
    T('mo moi: hai phia co trong so', up=True, mine_xau=True)
    T('mo moi: bo rui ro tre GP', delay=False)
    T('holding 15% (NNC co tuc ve tien 15%, quy DTPT 87->353)', hold=0.15); T('holding 30%', hold=0.30)
    T('vach gia co_so 300 (2028-30) thay truot', glide=False)
    T('stress bien cum 0,5 tu 2028', stress=0.5); T('stress bien cum 1,0 (TB chu ky) tu 2028', stress=1.0)
    T('han GP Tan Lap 2035 moi muc', endA=2035); T('han GP Tan Lap 2045 moi muc', endA=2045)
    T('NNC SL co_so 1,20 (2028-30)', nnc_vol=(1.20, 1.20)); T('NNC SL co_so 1,30 ca ky (2028+)', nnc_vol=(1.30, 1.30))
    T('Tan Lap SL co_so 1,10 (2028-30) — cat doi xung cum', tl_cut=True)
    T('chi phi Tan Lap +15%', ca=1.15); T('chi phi Tan Lap -15%', ca=0.85)
    T('r 11%', r=0.11); T('r 15%', r=0.15)
    T('PW g2031 70/real 30', PW={'g2031': .7, 'real': .3}); T('PW g2031 30/real 70', PW={'g2031': .3, 'real': .7})
    T('V_NNC co dinh 77.656 (NNC-DD cong bo)', VN_fix=77656)
    x1 = EV({'VN_fix': 70000}); x2 = EV({'VN_fix': 80000}); slope = (x2 - x1) / 10000 * 10000
    print(f'  do doc: MVC {slope:+,.0f} d/cp moi +10.000 d/cp V_NNC (V_NNC co dinh)'); out['vnnc_slope_per10k'] = slope
    out['tornado'] = tor

    # ---------- 6. lo trinh no rong base (uoc luong)
    capl = 1500 - R.BOOK_MINE
    c27 = res[('co_so', 'g2031')]
    P = {**R.BASE, **BASE6}
    op27 = (1.30 * (0.91 * 380 - R.costA(R.BASE) * 1.03) - M.SGA_A * 1.03) * (1 - M.TAX) + M.BOT_GP * (1 - M.TAX) + M.D_EBIT['co_so'] * (1 - M.TAX)
    op28 = (1.30 * (0.91 * 360 - R.costA(R.BASE) * 1.03 ** 2) - M.SGA_A * 1.03 ** 2) * (1 - M.TAX) + M.BOT_GP * (1 - M.TAX) + M.D_EBIT['co_so'] * (1 - M.TAX)
    DIVP = 100.0; DIVR = 10.6   # co tuc tra (uoc luong, = SKEPTIC4) ; co tuc NNC/LK ve tien (SKEPTIC4 #6)
    nd26 = -M.NETFIN - M.Q4_DIRECT + 0.0
    nd27 = nd26 + 0.6 * capl - op27 - DIVR + DIVP
    nd28 = nd27 + 0.4 * capl - op28 - DIVR + DIVP
    out['net_debt_path'] = dict(end2026=nd26, end2027=nd27, end2028=nd28, op27=op27, op28=op28, alert_over_path=150)
    print(f'\n=== 6. Lo trinh no rong base (uoc luong, chua tinh khau hao/von luu dong; mo moi chua co dong tien 2028): '
          f'cuoi 2026 {nd26:,.0f} | 2027 {nd27:,.0f} | 2028 {nd28:,.0f} ty ; CFO hoat dong uoc 2027 {op27:,.0f}, 2028 {op28:,.0f}')
    print(f'  Nguong canh bao: no rong vuot lo trinh base > 150 ty (2027 > {nd27+150:,.0f}; 2028 > {nd28+150:,.0f})')
    with open('model_r6_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
