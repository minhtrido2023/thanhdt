"""DD MVC r3 (03/11/2026) — MU GIA. Khong doc gia/von hoa/P-E MVC hay NNC. Tham so lay tu valuation_base.py (ban dong bang cua
calc/valuation.py r1/r2, md5 d3fb9637...) + sua doi r3. Chay: /home/trido/thanhdt/wc_venv/bin/python -B model_r3.py

SUA DOI r3 so voi r2:
 (P) Duong gia: 3 duong thay cap phang/thuc 50:50 —
     flat  = gia danh nghia phang mai mai (STRESS, chi kiem chiu dung);
     g2031 = vach kich ban (2028-30) KHONG chuyen lam phat toi 2030, +3%/nam tu 2031;
     real  = muc kich ban (tien 2026) giu gia tri thuc tu 2026.
     Trong so duong gia PW = flat 10 / g2031 50 / real 40 — co so: price_path_out.txt (xem REPORT r3 §2).
 (I) Hang muc rieng MVC (dat du an, han BOT, han GP Tan Lap, he so lien ket MCC/NHC, ICD, gach/xang) KHONG con xep chong theo
     kich ban NNC: moi hang muc lay muc theo W DOC LAP (r2 gan muc 'tot' cua moi hang muc vao cung kich ban 'tot').
 (M1) Do nhay he so gia MVC/NNC (REL) hieu chinh lai COST_A va COST_B de giu bien 2026 da quan sat.
 (M2) Tre mo moi 1 nam lui CA vach gia/san luong va moc lam phat g2031.
 (M3) Tornado 2 chieu day du.
NGUONG (DANG KY TRUOC KHI CHAY, khong sua sau khi thay so):
  RE RO  : gia <= P10 luoi tham so cua gia tri ky vong (ngay ca bo tham so bi quan 10% van cho gia tri > gia)
  HOP LY : P25 .. P75 luoi tham so
  DAT    : gia >= P90 luoi tham so
  (P10-P25 = nghieng re; P75-P90 = nghieng dat). Dai kich ban (P10-P90 theo trong so) bao cao rieng = rui ro, khong dung lam nguong.
"""
import sys, itertools, json, csv
import numpy as np
sys.dont_write_bytecode = True
import valuation_base as M

SCN = ['tot', 'co_so', 'xau', 'rat_xau']
W0 = {'tot': .25, 'co_so': .50, 'xau': .20, 'rat_xau': .05}
PATHS = ['flat', 'g2031', 'real']
PW0 = {'flat': .10, 'g2031': .50, 'real': .40}
LAND_SUNK = 431.857          # dat mo moi da chi (CIP), nam trong NETFIN qua vay/tien da tra
BASE = dict(REL=0.87, COST_A=130.0, COST_B=135.0, CAPEX_LEFT=1500 - 438.4, SALV=0.30 * 431.857, r=0.13, hold=0.15,
            shift=0, delay_add=0, delay_k=None, floor_all=False, W=W0, PW=PW0, corr=False)
IDIO = ['LAND', 'BOT_YRS', 'END_A', 'ASSOC_K', 'ICD_K', 'D_EBIT']
GP26 = 0.87 * 380 - 130      # bien thuc te Tan Lap 2026 (k/m3) — neo hieu chinh M1


def g(y, path, sh=0):
    if path == 'flat': return 1.0
    if path == 'real': return 1.03 ** (y - 2026)
    return 1.03 ** max(0, y - 2030 - sh)          # g2031


def nprice(k, y, sh):
    a = M.NNC_SCN[k]
    return a[2] if y <= 2027 + sh else (a[3] if y < 2031 + sh else a[5])


def cf_A(k, path, endA, P):
    out = []
    for y in range(2027, endA + 1):
        v = M.VOL_A[k][0] if y <= 2027 + P['shift'] else M.VOL_A[k][1]
        f = 1.03 ** (y - 2026)
        ebit = v * (P['REL'] * nprice(k, y, P['shift']) * g(y, path, P['shift']) - P['COST_A'] * f) - M.SGA_A * f
        out.append((y, max(ebit, 0) * (1 - M.TAX)))
    return out


def cf_B_parts(k, path, P):
    """tra (PV van hanh, PV capex con lai) — capex giu 2027/2028 (than trong, nhu r2)"""
    r = P['r']; d = M.DELAY[k] + (P['delay_add'] if (P['delay_k'] is None or k in P['delay_k']) else 0)
    capex = [(2027, -0.6 * P['CAPEX_LEFT']), (2028, -0.4 * P['CAPEX_LEFT'])]
    ops = []; tl, mh = 14.806, 3.945
    for y in range(2028 + d, 2050):
        u = M.UTIL[k][min(y - 2028 - d, 2)]
        q1 = min(1.0 * u, tl); q2 = min(0.5 * u, mh); tl -= q1; mh -= q2
        v = (q1 + q2) * 1.42
        if v <= 1e-6: break
        f = 1.03 ** (y - 2026); px = P['REL'] * nprice(k, y, P['shift']) * g(y, path, P['shift'])
        ebit = v * (px - P['COST_B'] * f) - M.SGA_B * f
        ops.append((y, max(ebit, 0) * (1 - M.TAX) - 0.03 * v * px))
    return M.pv(ops, r), M.pv(capex, r)


def nnc_ex(k, path, P):
    a = M.NNC_SCN[k]; out = []; sh = P['shift']
    for y in range(2027, 2044):
        v = a[0] if y <= 2027 + sh else (a[1] if y < 2031 + sh else a[4])
        f = 1.03 ** (y - 2026)
        ebit = v * (nprice(k, y, sh) * g(y, path, sh) - M.VAR * M.K * f) - M.FIX * M.K * f - M.SGA * f + M.RENT * f
        out.append((y, max(ebit, 0) * (1 - M.TAX)))
    return M.pv(out, P['r']) + M.n_q4 + M.n_cash + M.n_nhc_book + (M.n_cip if k in ('tot', 'co_so') else 0)


def comps(k, path, P):
    r = P['r']
    Bops, Bcap = cf_B_parts(k, path, P); B = Bops + Bcap
    if P['floor_all'] or k in ('xau', 'rat_xau'):
        B = max(B, P['SALV'])
    A = {e: M.pv(cf_A(k, path, M.END_A[e], P), r) for e in SCN}
    return dict(A=A, B=B, Bops=Bops, Bcap=Bcap, N_ex=nnc_ex(k, path, P))


def idio_val(item, e):
    if item == 'LAND': return M.LAND[e]
    if item == 'BOT_YRS': return M.pv([(2027 + i, M.BOT_GP * (1 - M.TAX)) for i in range(M.BOT_YRS[e])], 0.13)
    if item == 'ASSOC_K': return M.ASSOC_K[e] * (M.MCC_BOOK + M.NHC_BOOK)
    if item == 'ICD_K': return M.ICD_K[e] * M.ICD_BOOK
    if item == 'D_EBIT': return M.pv([(y, M.D_EBIT[e] * (1 - M.TAX) if M.D_EBIT[e] > 0 else M.D_EBIT[e]) for y in range(2027, 2037)], 0.13)


def vm_of(Dm, N_ex, P):
    h = P['hold']; s = M.s_NNC; c = M.c_MVC
    VM = (Dm + (1 - h) * s * N_ex) / (1 - (1 - h) * s * c)
    return VM


def ps(VM): return VM * 1e9 / M.SH_M


def idio_r(P):
    """idio_val phu thuoc r cho BOT/D_EBIT — tinh lai theo r"""
    r = P['r']
    def f(item, e):
        if item == 'BOT_YRS': return M.pv([(2027 + i, M.BOT_GP * (1 - M.TAX)) for i in range(M.BOT_YRS[e])], r)
        if item == 'D_EBIT': return M.pv([(y, M.D_EBIT[e] * (1 - M.TAX) if M.D_EBIT[e] > 0 else M.D_EBIT[e]) for y in range(2027, 2037)], r)
        return idio_val(item, e)
    return f


def Dm_of(cp, k, labels, fI):
    """labels: dict item->muc kich ban; END_A dung cho A"""
    oth = sum(fI(it, labels[it]) for it in IDIO if it != 'END_A')
    return cp['A'][labels['END_A']] + cp['B'] + M.Q4_DIRECT + M.NETFIN + oth


def EV(P=None, by_path=False, by_k=False):
    """gia tri ky vong (d/cp). Doc lap (corr=False): E[Dm] tuyen tinh -> lay ky vong tung hang muc."""
    P = {**BASE, **(P or {})}; W = P['W']; PW = P['PW']; fI = idio_r(P)
    res = {}
    for k in SCN:
        for path in PATHS:
            cp = comps(k, path, P)
            if P['corr']:
                Dm = Dm_of(cp, k, {it: k for it in IDIO}, fI)
            else:
                EA = sum(W[e] * cp['A'][e] for e in SCN)
                Eo = sum(W[e] * fI(it, e) for it in IDIO if it != 'END_A' for e in SCN)
                Dm = EA + cp['B'] + M.Q4_DIRECT + M.NETFIN + Eo
            VM = vm_of(Dm, cp['N_ex'], P)
            res[(k, path)] = dict(VM=VM, ps=ps(VM), N_ex=cp['N_ex'], Dm=Dm)
    ev = sum(W[k] * PW[p] * res[(k, p)]['ps'] for k in SCN for p in PATHS)
    if by_path:
        return ev, {p: sum(W[k] * res[(k, p)]['ps'] for k in SCN) for p in PATHS}, res
    return ev


def scen_dist(P=None):
    """phan phoi theo trong so kich ban (k x duong gia x 6 hang muc rieng doc lap) -> (gia tri d/cp, trong so)"""
    P = {**BASE, **(P or {})}; W = P['W']; PW = P['PW']; fI = idio_r(P)
    vals = []; wts = []
    for k in SCN:
        for path in PATHS:
            cp = comps(k, path, P)
            for combo in itertools.product(SCN, repeat=len(IDIO)):
                lab = dict(zip(IDIO, combo))
                wt = W[k] * PW[path] * np.prod([W[e] for e in combo])
                vals.append(ps(vm_of(Dm_of(cp, k, lab, fI), cp['N_ex'], P))); wts.append(wt)
    return np.array(vals), np.array(wts)


def wpct(v, w, q):
    o = np.argsort(v); v = v[o]; cw = np.cumsum(w[o]) / w.sum()
    return np.interp(q, cw, v)


if __name__ == '__main__':
    out = {}
    ev, bypath, res = EV(by_path=True)
    out['tam'] = ev; out['by_path'] = bypath
    print(f'=== TAM r3 (W 25/50/20/5, PW flat10/g2031 50/real40, r13, holding15, hang muc rieng doc lap): {ev:,.0f} d/cp')
    for p in PATHS:
        print(f'  duong {p:5s}: KV {bypath[p]:7,.0f} | ' + ' '.join(f'{k} {res[(k,p)]["ps"]:7,.0f}' for k in SCN))
    out['scn_ps'] = {f'{k}|{p}': res[(k, p)]['ps'] for k in SCN for p in PATHS}

    # ---------- 1. CAU NOI co_so theo duong gia
    print('\n=== 1. CAU NOI kich ban co_so (ty dong; d/cp = x10), hang muc rieng o muc co_so ===')
    P = dict(BASE); fI = idio_r(P); bridge = {}
    for path in PATHS:
        cp = comps('co_so', path, P); lab = {it: 'co_so' for it in IDIO}
        Dm = Dm_of(cp, 'co_so', lab, fI); VM = vm_of(Dm, cp['N_ex'], P)
        h = P['hold']; stake_pre = M.s_NNC * (cp['N_ex'] + M.c_MVC * VM); stake = (1 - h) * stake_pre
        A = cp['A']['co_so']; prog = cp['Bops'] + cp['Bcap'] - LAND_SUNK
        others = sum(fI(it, 'co_so') for it in IDIO if it != 'END_A') + M.Q4_DIRECT
        netfin_ex = M.NETFIN + LAND_SUNK
        b = dict(TanLap=A, mo_moi_PV_van_hanh=cp['Bops'], mo_moi_PV_capex_con=cp['Bcap'], mo_moi_dat_da_chi=-LAND_SUNK,
                 CHUONG_TRINH_MO_MOI=prog, BOT_gach_ICD_LK_dat_Q4=others, no_rong_KHONG_gom_dat_mo=netfin_ex,
                 TRUC_TIEP=Dm, phan_NNC_truoc_holding=stake_pre, holding=-(stake_pre - stake), phan_NNC=stake, TONG=VM,
                 TONG_dcp=ps(VM), NNC_ex_MVC=cp['N_ex'], V_NNC_dcp=(cp['N_ex'] + M.c_MVC * VM) * 1e9 / M.N_SH)
        bridge[path] = b
        print(f'[{path}] ' + ' | '.join(f'{a} {v:,.1f}' for a, v in b.items()))
    out['bridge_co_so'] = bridge
    print('Moc "gia tri phan gop NNC": so sach khoan dau tu NNC tren BCTC HN 30/09 (xem REPORT r2 §SOTP) va gia tri phan NNC theo mo hinh (cot phan_NNC).')
    # khi nao TONG < phan NNC (ca 12 o)
    print('\nTONG vs phan NNC (sau holding) — 12 o, hang muc rieng theo k:')
    neg = []
    for k in SCN:
        for path in PATHS:
            cp = comps(k, path, P); lab = {it: k for it in IDIO}; Dm = Dm_of(cp, k, lab, fI); VM = vm_of(Dm, cp['N_ex'], P)
            stake = (1 - P['hold']) * M.s_NNC * (cp['N_ex'] + M.c_MVC * VM)
            prog = cp['B'] - LAND_SUNK   # B da ap san dung du an o xau/rat_xau
            print(f'  {k:7s} {path:5s}: TONG {VM:7.1f} | phan NNC {stake:6.1f} | TRUC TIEP {Dm:7.1f} | chuong trinh mo moi {prog:7.1f} | TONG<NNC? {VM < stake} | TRUC TIEP<NNC? {Dm < stake}')
            if Dm < stake: neg.append(f'{k}|{path}')
    out['direct_lt_stake'] = neg

    # ---------- 2. Phan phoi kich ban + luoi tham so
    v, w = scen_dist()
    sd = {q: wpct(v, w, q / 100) for q in (10, 25, 50, 75, 90)}
    print(f'\n=== 2a. Phan phoi THEO TRONG SO KICH BAN ({len(v)} o, k x duong gia x 6 hang muc doc lap): ' + ' '.join(f'P{q} {x:,.0f}' for q, x in sd.items()) + f' | KV {np.average(v, weights=w):,.0f}')
    vc, wc = [], []
    for k in SCN:
        for p in PATHS:
            vc.append(EV({'corr': True, 'W': {**{e: 0 for e in SCN}, k: 1}, 'PW': {**{q: 0 for q in PATHS}, p: 1}})); wc.append(W0[k] * PW0[p])
    vc, wc = np.array(vc), np.array(wc)
    sdc = {q: wpct(vc, wc, q / 100) for q in (10, 25, 50, 75, 90)}
    print('    (xep chong kieu r2, 12 o): ' + ' '.join(f'P{q} {x:,.0f}' for q, x in sdc.items()) + f' | KV {np.average(vc, weights=wc):,.0f}')
    out['scen_pct'] = sd; out['scen_pct_stacked'] = sdc
    grid = []
    for r, h, cx, ca, rel in itertools.product((0.11, 0.13, 0.15), (0.0, 0.15, 0.30), (0.7, 1.0, 1.3), (0.85, 1.0, 1.15), (0.80, 0.87, 0.95)):
        cost_a = (rel * 380 - GP26) * ca
        grid.append(dict(r=r, hold=h, capex=cx, costA=ca, rel=rel,
                         ev=EV({'r': r, 'hold': h, 'CAPEX_LEFT': BASE['CAPEX_LEFT'] * cx, 'REL': rel, 'COST_A': cost_a, 'COST_B': cost_a + 5})))
    ge = np.array([x['ev'] for x in grid])
    gp = {q: float(np.percentile(ge, q)) for q in (10, 25, 50, 75, 90)}
    print(f'=== 2b. Luoi tham so ({len(ge)} bo: r 11/13/15 x holding 0/15/30 x capex +-30% x chi phi Tan Lap +-15% x REL 0,80/0,87/0,95 hieu chinh): '
          + ' '.join(f'P{q} {x:,.0f}' for q, x in gp.items()))
    out['grid_pct'] = gp
    with open('grid_r3.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    zones = dict(RE_RO_duoi=gp[10], NGHIENG_RE=(gp[10], gp[25]), HOP_LY=(gp[25], gp[75]), NGHIENG_DAT=(gp[75], gp[90]), DAT_tren=gp[90])
    print('NGUONG (dang ky truoc): RE RO <= {:,.0f} | nghieng re {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | nghieng dat {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))
    out['zones'] = zones

    # ---------- 3. Tornado 2 chieu + cac sua doi
    print('\n=== 3. Do nhay (so voi tam) ===')
    tor = {}
    def T(lab, **kw):
        x = EV(kw); tor[lab] = x - ev; print(f'  {lab:58s} {x:8,.0f} ({x - ev:+7,.0f})')
    for rel in (0.80, 0.95, 1.00):
        T(f'M1 REL {rel} (COST_A/COST_B hieu chinh giu bien 2026)', REL=rel, COST_A=rel * 380 - GP26, COST_B=rel * 380 - GP26 + 5)
    T('M2 mo moi co_so tre 1 nam, vach gia KHONG lui', delay_add=1)
    T('M2 tre 1 nam + vach gia/san luong/moc lam phat lui 1 nam', delay_add=1, shift=1)
    T('M2 (dinh nghia skeptic) CHI co_so tre 1 nam, vach KHONG lui', delay_add=1, delay_k=('co_so',))
    T('M2 (dinh nghia skeptic) CHI co_so tre 1 nam + vach lui 1 nam', delay_add=1, delay_k=('co_so',), shift=1)
    T('capex mo moi con lai -30%', CAPEX_LEFT=BASE['CAPEX_LEFT'] * 0.7)
    T('capex mo moi con lai +30%', CAPEX_LEFT=BASE['CAPEX_LEFT'] * 1.3)
    T('chi phi mo moi 105k', COST_B=105)
    T('chi phi mo moi 165k', COST_B=165)
    T('chi phi Tan Lap -15% (110k)', COST_A=110.5)
    T('chi phi Tan Lap +15% (150k)', COST_A=149.5)
    T('holding 0%', hold=0.0)
    T('holding 30%', hold=0.30)
    T('san dung du an ap MOI kich ban', floor_all=True)
    T('r 11%', r=0.11)
    T('r 15%', r=0.15)
    T('W 15/60/20/5', W={'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05})
    T('W 35/50/10/5 (doi xung)', W={'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05})
    T('PW flat 25/g2031 50/real 25', PW={'flat': .25, 'g2031': .50, 'real': .25})
    T('PW flat 5/g2031 35/real 60', PW={'flat': .05, 'g2031': .35, 'real': .60})
    T('PW flat 50/real 50 (cach r2)', PW={'flat': .5, 'g2031': 0, 'real': .5})
    T('xep chong hang muc rieng theo k (cach r2)', corr=True)
    sv = {a: dict(getattr(M, a)) for a in IDIO}
    for a in IDIO: getattr(M, a)['tot'] = getattr(M, a)['co_so']
    T('bo muc "tot" cua MOI hang muc rieng (= co_so)')
    for a in IDIO: getattr(M, a).update(sv[a])
    old = dict(M.LAND); M.LAND.update({k: 0 for k in SCN}); T('dat du an nha o = 0'); M.LAND.update(old)
    old = dict(M.END_A); M.END_A.update({k: 2035 for k in SCN}); T('han GP Tan Lap 2035 moi muc'); M.END_A.update(old)
    old = dict(M.END_A); M.END_A.update({k: 2045 for k in SCN}); T('han GP Tan Lap 2045 moi muc'); M.END_A.update(old)
    out['tornado'] = tor

    # ---------- 4. Cac buoc r2 -> r3 (hieu ung tung sua doi)
    print('\n=== 4. Tu r2 sang r3 (tung buoc) ===')
    steps = []
    x0 = EV({'corr': True, 'PW': {'flat': .5, 'g2031': 0, 'real': .5}}); steps.append(('r2 tai lap (xep chong, phang/thuc 50:50)', x0))
    x1 = EV({'corr': True}); steps.append(('+ duong gia 10/50/40', x1))
    x2 = EV(); steps.append(('+ hang muc rieng doc lap (= tam r3)', x2))
    for a, b in steps: print(f'  {a:50s} {b:8,.0f}')
    out['steps'] = steps

    # ---------- 5. NNC nhat quan (he phuong trinh; khong dung gia thi truong)
    print('\n=== 5. NNC nhat quan V_N = N_ex + c*V_M (d/cp NNC) ===')
    nn = {}
    for p in PATHS:
        nn[p] = sum(W0[k] * (res[(k, p)]['N_ex'] + M.c_MVC * res[(k, p)]['VM']) * 1e9 / M.N_SH for k in SCN)
        print(f'  {p:5s}: KV {nn[p]:,.0f} | ' + ' '.join(f'{k} {(res[(k, p)]["N_ex"] + M.c_MVC * res[(k, p)]["VM"]) * 1e9 / M.N_SH:,.0f}' for k in SCN))
    nn['tam_PW'] = sum(PW0[p] * nn[p] for p in PATHS); print(f'  tam NNC theo PW 10/50/40: {nn["tam_PW"]:,.0f}')
    out['NNC'] = nn
    with open('model_r3_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
