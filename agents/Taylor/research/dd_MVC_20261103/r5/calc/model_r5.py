"""DD MVC r5 (03/11/2026 ~17:30 ICT) — NGUYEN TAC MOI (user 03/11 17:06): dung vai doanh nghiep; du an dau tu moi o GIA TRI SO SACH
(NPV=0) trong BASE; moi khoan giam tru trong base phai co CO SO DU LIEU DOC LAP, khong co => chuyen thanh do nhay/kich ban co nhan.
MU GIA: khong doc gia/von hoa/P-E MVC hay NNC. Chay: /home/trido/thanhdt/wc_venv/bin/python -B model_r5.py
Tai dung valuation_base.py (= r3, md5 ghi o LOCK). Don vi ty dong; d/cp = ty x 10.

THAY DOI r5 so voi r3/r4 (bang kiem ke day du: inventory_r5.md):
 (1) Mo moi 1.500 ty: BASE = so sach: da chi 438,4 (CIP dat 431,86 + tien cap quyen 6,56) la TAI SAN theo gia von; phan con chi ~1.062
     doi ung gia tri tuong duong (NPV=0). r3: Bops+Bcap (va dat da chi coi la mat) => bo.
     (+) kich ban 'tot' (W 25%, neo Bobby F2 P(gia Q2/27 >+7%)=0,30): cong NPV toan du an >0 tinh tu du lieu (gia k-tot, chi phi Tan Lap
         hieu chinh, cong suat 1,0+0,5 tr m3 nguyen khoi x1,42, ramp 0,5/0,8/0,93 = ty le dung cong suat Tan Lap 1,3/1,4, tru luong 18,75).
     (-) rui ro CU THE: tre GP/van hanh (Bobby: tre 2-4 nam dau gia->san xuat; F6 P(co GP truoc 06/2027)=0,30) => P(tre 0/1/2 nam)=0,30/0,40/0,30,
         chi phi tre = gia tri so sach x (1-(1+r)^-d). Gia xau KHONG ap len mo moi o base (quyen dung chi phan con lai) — do nhay rieng.
 (2) Cum cong nghiep <=500 ty, mua NNC len 51%: NPV=0 (khong vao base, khong vao luoi).
 (3) Holding 15% -> 0 (khong co du lieu doc lap); do nhay 15/30%.
 (4) REL 0,87 -> 0,91: co so Bobby (sector read 30/10): gia 1x2 tai mo Binh Phuoc cu 230-240k/tan ~ 334-360k/m3 (Tan Lap o Dong Phu,
     Binh Phuoc cu) / gia NNC 380 => 0,88-0,95, giua 0,91. COST_A hieu chinh giu bien 2026 da quan sat (200,6k/m3).
 (5) Duong gia: vach co_so 380->300 (2028-30, nhan FPTS 'cung moi') -> TRUOT 360/340/320 (2028/29/30), 320 tu 2031 — moc 320 giu nguyen
     (= hoi ve gia thuc TB 2012-25 cua NNC theo GPM: g2031 cho 0,75x, real 0,84x). Vach 300 = do nhay downside co nhan.
     PW trung tam g2031 50 / real 50; phang danh nghia = STRESS (khong vao tam, khong vao luoi).
 (6) San luong Tan Lap co_so 1,30 -> 1,20 tu 2028 (r3) -> giu 1,30 (muc 2026 da hieu chinh; khong co du lieu suy giam).
 (7) MCC/NHC/ICD: he so 0,8/0,6 x so sach -> GIA TRI GHI SO BCTC HN 30/09 (MCC 22,59; NHC 32,47; ICD von gop 44,80) moi kich ban.
 (8) NNC (vong cheo): CIP Tam Lap 1 khu II 83,5 tinh o MOI kich ban (r3: chi tot/co_so) — cung loi 'du an moi bi gach' ben NNC.
 Giu nguyen (co nhan uoc luong, khong phai giam tru moi): r 13% (khung user), han GP Tan Lap W, BOT, gach/xang, dat o, Q4, thue 20%, W 25/50/20/5.
NGUONG (DANG KY TRUOC KHI CHAY; khong sua sau khi thay so). Luoi 729 bo: r 11/13/15 x chi phi Tan Lap 0,85/1/1,15 x REL 0,88/0,91/0,95 x
 W {15/60/20/5, 25/50/20/5, 35/50/10/5} x PW g2031:real {70:30, 50:50, 30:70} x capex mo moi (chi anh huong upside) 0,7/1/1,3:
  RE CO BIEN AN TOAN <= P10 ; RE CO DIEU KIEN P10-P25 ; HOP LY P25-P75 ; NGHIENG DAT P75-P90 ; DAT >= P90.
"""
import sys, itertools, json, csv
import numpy as np
sys.dont_write_bytecode = True
import valuation_base as M

SCN = ['tot', 'co_so', 'xau', 'rat_xau']
W0 = {'tot': .25, 'co_so': .50, 'xau': .20, 'rat_xau': .05}
PATHS = ['g2031', 'real']
PW0 = {'g2031': .5, 'real': .5}
BOOK_MINE = 431.857 + 6.56          # CIP dat + tien cap quyen da chi
GP26 = 200.6                        # bien Tan Lap 2026 (k/m3) quan sat = 0,87*380-130 (r3)
MCC_BV, NHC_BV, ICD_BV = 22.588, 32.473, 44.797   # BCTC HN Q3/26 V.12; ICD von gop
DELAY_P = {0: .30, 1: .40, 2: .30}
BASE = dict(REL=0.91, ca=1.0, r=0.13, hold=0.0, capex=1.0, W=W0, PW=PW0, glide=True, volA_cut=False, mine_xau=False,
            assoc_k=1.0, delay=True, cip_all=True, up=True, costB_add=0.0, mine_r3=False)
DELAY_D = {'tot': 0, 'co_so': 0, 'xau': 1, 'rat_xau': 2}


def g(y, path):
    if path == 'flat': return 1.0
    if path == 'real': return 1.03 ** (y - 2026)
    return 1.03 ** max(0, y - 2030)


def nprice(k, y, P):
    a = M.NNC_SCN[k]
    if y <= 2027: return a[2]
    if k == 'co_so' and P['glide']:
        return {2028: 360, 2029: 340, 2030: 320}.get(y, 320)
    return a[3] if y < 2031 else a[5]


def costA(P): return (P['REL'] * 380 - GP26) * P['ca']


def tanlap(k, path, endA, P):
    vol = {'tot': (1.40, 1.40), 'co_so': (1.30, 1.20 if P['volA_cut'] else 1.30), 'xau': (1.30, 1.05), 'rat_xau': (0.90, 0.90)}[k]
    out = []
    for y in range(2027, endA + 1):
        v = vol[0] if y == 2027 else vol[1]; f = 1.03 ** (y - 2026)
        ebit = v * (P['REL'] * nprice(k, y, P) * g(y, path) - costA(P) * f) - M.SGA_A * f
        out.append((y, max(ebit, 0) * (1 - M.TAX)))
    return M.pv(out, P['r'])


def mine_cf(k, path, P, d=0):
    """dong tien toan du an (gom 438,4 da chi tai 2026) — dung cho IRR/NPV"""
    capl = (1500 - BOOK_MINE) * P['capex']
    cf = [(2026, -BOOK_MINE), (2027 + d, -0.6 * capl), (2028 + d, -0.4 * capl)]
    tl, mh = 14.806, 3.945; ramp = (0.5, 0.8, 0.93)
    for y in range(2028 + d, 2060):
        u = ramp[min(y - 2028 - d, 2)]
        q1 = min(1.0 * u, tl); q2 = min(0.5 * u, mh); tl -= q1; mh -= q2
        v = (q1 + q2) * 1.42
        if v <= 1e-6: break
        f = 1.03 ** (y - 2026); px = P['REL'] * nprice(k, y, P) * g(y, path)
        ebit = v * (px - (costA(P) + P['costB_add']) * f) - M.SGA_B * f
        cf.append((y, (ebit * (1 - M.TAX) if ebit > 0 else ebit) - 0.03 * v * px))
    return cf


def npv_total(k, path, P, r=None):
    r = P['r'] if r is None else r
    return sum(c / (1 + r) ** (y - 2026) for y, c in mine_cf(k, path, P))   # ve dau 2027 ~ moc 2026 cuoi nam


def irr(cf):
    lo, hi = -0.5, 1.0
    f = lambda r: sum(c / (1 + r) ** (y - 2026) for y, c in cf)
    if f(lo) * f(hi) > 0: return float('nan')
    for _ in range(200):
        m = (lo + hi) / 2
        if f(lo) * f(m) <= 0: hi = m
        else: lo = m
    return m


def mine_val(k, path, P):
    if P['mine_r3']:   # cach r3/r4: gia tri = PV van hanh - PV capex con lai (dat da chi coi la mat); san ban dat 30% o xau/rat_xau
        fwd = npv_total(k, path, P) + BOOK_MINE
        return max(fwd, 0.30 * 431.857) if k in ('xau', 'rat_xau') else fwd
    v = BOOK_MINE
    if P['up'] and k == 'tot':
        v += max(npv_total(k, path, P), 0)
    if P['mine_xau'] and k in ('xau', 'rat_xau'):
        v += npv_total(k, path, P)
    if P['delay']:
        v -= sum(p * BOOK_MINE * (1 - (1 + P['r']) ** -d) for d, p in DELAY_P.items())
    return v


def nnc_ex(k, path, P):
    a = M.NNC_SCN[k]; out = []
    for y in range(2027, 2044):
        v = a[0] if y <= 2027 else (a[1] if y < 2031 else a[4])
        f = 1.03 ** (y - 2026)
        ebit = v * (nprice(k, y, P) * g(y, path) - M.VAR * M.K * f) - M.FIX * M.K * f - M.SGA * f + M.RENT * f
        out.append((y, max(ebit, 0) * (1 - M.TAX)))
    cip = M.n_cip if (P['cip_all'] or k in ('tot', 'co_so')) else 0
    return M.pv(out, P['r']) + M.n_q4 + M.n_cash + M.n_nhc_book + cip


def other_exp(P):
    """ky vong hang muc rieng (doc lap voi k, nhu r3): han GP Tan Lap xu ly rieng; BOT, gach/xang, dat o"""
    W = P['W']; r = P['r']
    bot = sum(W[e] * M.pv([(2027 + i, M.BOT_GP * (1 - M.TAX)) for i in range(M.BOT_YRS[e])], r) for e in SCN)
    de = sum(W[e] * M.pv([(y, M.D_EBIT[e] * (1 - M.TAX) if M.D_EBIT[e] > 0 else M.D_EBIT[e]) for y in range(2027, 2037)], r) for e in SCN)
    land = sum(W[e] * M.LAND[e] for e in SCN)
    assoc = P['assoc_k'] * (MCC_BV + NHC_BV) + ICD_BV
    return dict(BOT=bot, gach_xang=de, dat_o=land, LK_nho_ICD=assoc)


def solve(Dm, N_ex, P):
    h = P['hold']; s = M.s_NNC; c = M.c_MVC
    VM = (Dm + (1 - h) * s * N_ex) / (1 - (1 - h) * s * c)
    return VM


def cell(k, path, P):
    W = P['W']
    A = sum(W[e] * tanlap(k, path, M.END_A[e], P) for e in SCN)
    o = other_exp(P); B = mine_val(k, path, P); N = nnc_ex(k, path, P)
    Dm = A + B + sum(o.values()) + M.Q4_DIRECT + M.NETFIN
    VM = solve(Dm, N, P)
    stake = (1 - P['hold']) * M.s_NNC * (N + M.c_MVC * VM)
    return dict(A=A, B=B, **o, Q4=M.Q4_DIRECT, NETFIN=M.NETFIN, Dm=Dm, stake=stake, VM=VM, ps=VM * 10, N_ex=N,
                V_NNC_ps=(N + M.c_MVC * VM) * 1e9 / M.N_SH)


def EV(over=None, detail=False):
    P = {**BASE, **(over or {})}
    res = {(k, p): cell(k, p, P) for k in SCN for p in P['PW']}
    ev = sum(P['W'][k] * P['PW'][p] * res[(k, p)]['ps'] for k in SCN for p in P['PW'])
    return (ev, res) if detail else ev


if __name__ == '__main__':
    out = {}
    ev, res = EV(detail=True); out['tam'] = ev
    base_ps = sum(PW0[p] * res[('co_so', p)]['ps'] for p in PATHS); out['base_co_so'] = base_ps
    print(f'=== TAM r5 (W 25/50/20/5 x PW g2031 50/real 50; r13; holding 0; mo moi so sach): {ev:,.0f} d/cp | BASE (co_so) {base_ps:,.0f}')
    for p in PATHS:
        print(f'  {p:5s}: ' + ' '.join(f'{k} {res[(k, p)]["ps"]:7,.0f}' for k in SCN))
    out['cells'] = {f'{k}|{p}': res[(k, p)]['ps'] for k in SCN for p in PATHS}
    st = {}
    for p in ('flat',):
        e2, r2 = EV({'PW': {'flat': 1.0}}, detail=True); st['flat_100'] = e2; st['flat_co_so'] = r2[('co_so', 'flat')]['ps']
    print(f'  STRESS phang danh nghia 100%: KV {st["flat_100"]:,.0f} | co_so {st["flat_co_so"]:,.0f}'); out['stress'] = st

    print('\n=== 1. CAU NOI co_so (ty; d/cp = x10) ===')
    br = {}
    for p in PATHS:
        c = res[('co_so', p)]
        b = dict(TanLap=c['A'], mo_moi_so_sach_sau_tre=c['B'], BOT=c['BOT'], gach_xang=c['gach_xang'], dat_o=c['dat_o'], LK_nho_ICD=c['LK_nho_ICD'],
                 Q4=c['Q4'], no_rong=c['NETFIN'], TRUC_TIEP=c['Dm'], phan_NNC=c['stake'], TONG=c['VM'], TONG_dcp=c['ps'], V_NNC_dcp=c['V_NNC_ps'])
        br[p] = b; print(f'[{p}] ' + ' | '.join(f'{a} {v:,.1f}' for a, v in b.items()))
    out['bridge'] = br
    print(f'  Kiem so: VCSH HN 30/09 1.546,0 (BVPS 15.460); NNC ghi so (VCSH) 470,0; CIP 436,7; LK 525,1')

    print('\n=== 2. Mo moi: NPV toan du an (gom 438,4 da chi) & IRR — tu du lieu ===')
    mine = {}
    for k in SCN:
        for p in ('flat', 'g2031', 'real'):
            cf = mine_cf(k, p, BASE); i = irr(cf)
            n = {r: npv_total(k, p, BASE, r) for r in (0.11, 0.13, 0.15)}
            mine[f'{k}|{p}'] = dict(irr=i, **{f'npv{int(r*100)}': v for r, v in n.items()})
            print(f'  {k:7s} {p:5s}: IRR {i:6.1%} | NPV r11 {n[0.11]:7.0f} r13 {n[0.13]:7.0f} r15 {n[0.15]:7.0f}')
    out['mine'] = mine
    # don vi: gia ban/m3, chi phi
    print(f'  REL {BASE["REL"]} -> gia MVC 2026 {BASE["REL"]*380:.0f}k/m3, chi phi tien mat {costA(BASE):.1f}k/m3, SGA mo moi {M.SGA_B} ty/nam')
    print(f'  capex/tru luong thanh pham: {1500/((14.806+3.945)*1.42):.1f}k/m3')
    dly = sum(p * BOOK_MINE * (1 - 1.13 ** -d) for d, p in DELAY_P.items()); print(f'  chi phi tre ky vong (r13): {dly:.1f} ty = {dly*10:,.0f} d/cp truc tiep')

    # ---------- 3. luoi
    grid = []
    Ws = [{'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05}, W0, {'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05}]
    PWs = [{'g2031': .7, 'real': .3}, PW0, {'g2031': .3, 'real': .7}]
    for r, ca, rel, wi, pi, cx in itertools.product((0.11, 0.13, 0.15), (0.85, 1.0, 1.15), (0.88, 0.91, 0.95), range(3), range(3), (0.7, 1.0, 1.3)):
        grid.append(dict(r=r, ca=ca, rel=rel, W=wi, PW=pi, capex=cx, ev=EV({'r': r, 'ca': ca, 'REL': rel, 'W': Ws[wi], 'PW': PWs[pi], 'capex': cx})))
    ge = np.array([x['ev'] for x in grid]); gp = {q: float(np.percentile(ge, q)) for q in (5, 10, 25, 50, 75, 90)}
    print(f'\n=== 3. Luoi {len(ge)} bo: ' + ' '.join(f'P{q} {v:,.0f}' for q, v in gp.items()))
    out['grid_pct'] = gp
    with open('grid_r5.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    print('NGUONG (dang ky truoc): RE CO BIEN AN TOAN <= {:,.0f} | RE CO DIEU KIEN {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | nghieng dat {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))

    # ---------- 4. kiem ke: hieu ung tung khoan (dua lai tung khoan r3/r4 vao r5) + do nhay
    print('\n=== 4. Hieu ung tung khoan giam tru r3/r4 (dua lai vao r5, so voi tam r5) ===')
    tor = {}
    def T(lab, **kw):
        x = EV(kw); tor[lab] = x - ev; print(f'  {lab:70s} {x:8,.0f} ({x - ev:+7,.0f})')
    T('holding 15%', hold=0.15); T('holding 30%', hold=0.30)
    T('REL 0,87 (r3)', REL=0.87); T('REL 0,95', REL=0.95); T('REL 0,88', REL=0.88)
    T('vach co_so 300 (2028-30, nhan FPTS cung moi) thay truot', glide=False)
    T('san luong Tan Lap co_so 1,20 tu 2028 (r3)', volA_cut=True)
    T('LK nho x0,8 so sach (r3 co_so)', assoc_k=0.8)
    T('NNC: CIP Tam Lap chi o tot/co_so (r3)', cip_all=False)
    T('mo moi: bo upside kich ban tot', up=False)
    T('mo moi: bo rui ro tre', delay=False)
    T('mo moi: ap NPV gia xau/rat xau (doi xung, khong quyen dung)', mine_xau=True)
    T('capex mo moi +30% (chi qua upside)', capex=1.3)
    T('chi phi mo moi +30k/m3 (chi qua upside)', costB_add=30.0)
    T('chi phi Tan Lap +15%', ca=1.15); T('chi phi Tan Lap -15%', ca=0.85)
    T('r 11%', r=0.11); T('r 15%', r=0.15)
    T('W 15/60/20/5', W={'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05})
    T('W 35/50/10/5', W={'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05})
    T('PW g2031 70/real 30', PW={'g2031': .7, 'real': .3}); T('PW g2031 30/real 70', PW={'g2031': .3, 'real': .7})
    T('PW them phang 10% (r3)', PW={'flat': .1, 'g2031': .5, 'real': .4})
    old = dict(M.LAND); M.LAND.update({k: 0 for k in SCN}); T('dat du an nha o = 0'); M.LAND.update(old)
    old = dict(M.END_A); M.END_A.update({k: 2035 for k in SCN}); T('han GP Tan Lap 2035 moi muc'); M.END_A.update(old)
    old = dict(M.END_A); M.END_A.update({k: 2045 for k in SCN}); T('han GP Tan Lap 2045 moi muc'); M.END_A.update(old)
    # cum CN / NNC 51%: NPV 0 => 0; do nhay: cum CN thu hoi 70% (r4) = -150 ty truc tiep
    x = EV(); M.Q4_DIRECT -= 150; T('cum CN 500 ty thu hoi 70% (r4, KHONG co co so)'); M.Q4_DIRECT += 150
    # tat ca giam tru r3/r4 cung luc (tai lap gan r4)
    T('TAT CA giam tru r3/r4 (holding15, REL0,87, vach, SL1,20, LK0,8, CIP, mo moi kieu r3 khong lam), PW +phang', hold=0.15, REL=0.87, glide=False,
      volA_cut=True, assoc_k=0.8, cip_all=False, PW={'flat': .1, 'g2031': .5, 'real': .4})
    T('mo moi cach r3/r4 (NPV moi kich ban, dat da chi la mat, san 30% o xau)', mine_r3=True)
    T('TAT CA + mo moi cach r3/r4', hold=0.15, REL=0.87, glide=False, volA_cut=True, assoc_k=0.8, cip_all=False,
      PW={'flat': .1, 'g2031': .5, 'real': .4}, mine_r3=True)
    out['tornado'] = tor

    # ---------- 5. NNC nhat quan + hieu ung NNC
    print('\n=== 5. NNC nhat quan V_N = N_ex + c V_M (d/cp NNC) ===')
    nn = sum(W0[k] * PW0[p] * res[(k, p)]['V_NNC_ps'] for k in SCN for p in PATHS)
    print(f'  tam NNC (r5 inputs): {nn:,.0f}'); out['NNC_tam'] = nn
    e_cip, r_cip = EV({'cip_all': False}, detail=True)
    nn_cip = sum(W0[k] * PW0[p] * r_cip[(k, p)]['V_NNC_ps'] for k in SCN for p in PATHS)
    print(f'  chi sua CIP Tam Lap moi kich ban: NNC {nn - nn_cip:+,.0f} d/cp NNC ; MVC {ev - e_cip:+,.0f} d/cp')
    out['NNC_cip_effect'] = dict(nnc=nn - nn_cip, mvc=ev - e_cip)
    # hieu ung CIP tren khung r3 (NNC-DD dang cong bo): W x 0,25 xau+rat_xau x 83,5
    d_nnc_r3 = (W0['xau'] + W0['rat_xau']) * M.n_cip * 1e9 / M.N_SH
    print(f'  tren khung NNC-DD (khong vong cheo): +{d_nnc_r3:,.0f} d/cp NNC')
    out['NNC_cip_effect_r3frame'] = d_nnc_r3
    with open('model_r5_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
