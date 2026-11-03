"""DD NNC r4 (03/11/2026 ~20:40 ICT) — CHUAN HOA CHU KY MO HIEN HUU theo SKEPTIC_R3_20261103.md + Bobby sector read 30/10 §4.
MU GIA: khong doc gia/von hoa/P-E NNC hay MVC trong file nay. Chay: /home/trido/thanhdt/wc_venv/bin/python -B model_r4.py
He thong: tai dung model_r3.py (NNC r3) + MVC r6 (valuation_base/model_r5/model_r6) KHONG SUA — md5 ghi o LOCK_md5_r4.txt.
Giai cheo dong thoi V_NNC = N_ex + c V_MVC ; V_MVC = D_MVC + s V_NNC (c 0,103 ; s 0,4407 ; holding 0) => cung luc ra V_MVC nhat quan.

NGUYEN TAC (user 03/11): du an MOI = so sach/NPV 0 (CIP Tam Lap 1 khu II, mo moi MVC, dat, cum CN, mua NNC 51%: GIU); moi giam tru base can
co so doc lap, AP DOI XUNG; CHU KY cua MO HIEN HUU (bien, san luong Mui Tau / Tan Lap) KHONG phai du an moi => chuan hoa theo co so doc lap.

THAY DOI r4 so voi r3 (r3 = tam o stress 0 + SL 1,40 = bien dinh vinh vien):
 (1) TAM = tron 3 TRANG THAI theo phan loai cua Bobby (§4, xac suat chu quan cua nguoi doc nganh, KHONG chinh theo gia):
       STRUCTURAL 0,20 -> bien dinh ben (stress 0, SL co_so NNC 1,40, Tan Lap 1,30)            [= tam r3]
       ADMIN_GATED 0,45 -> nghen hanh chinh go trong 6-18 thang: hoi bien MOT NUA (stress 0,5) tu 2028, SL hoi ve nam thuong
       CYCLICAL   0,35 -> hoi bien TRON ve TB chu ky (stress 1,0) tu 2028, SL hoi ve nam thuong
 (2) SL nam thuong (nhanh hoi bien): NNC co_so 1,10 (2028-30) / 1,20 (2031+). Co so quan sat: 2024 = 1,05 tr m3 o gia ~245k/m3, GV thanh pham
     kiem toan 178,29 ty / DT 257,44 [KT25 7.2; SL FPTS] = 74% tran GP 1,42 => nam thuong ~1,05-1,20. Tan Lap (cung cum, cung cong suat 1,4):
     cat CUNG muc 1,10/1,20 (doi xung cum; truoc day 1,30). SL 1,40 chi o nhanh bien dinh.
 (3) TRAN GIA CHU KY (stress 1,0): gia da (tien 2026) tai do BIEN GOP DA THANH PHAM tren chi phi mo hinh (= GV kiem toan da hieu chinh K 0,97)
     bang TB chu ky, tinh O CHINH SAN LUONG cua nhanh hoi bien (chi phi co dinh/m3 phu thuoc SL):
       GPM_da_chu_ky = TB GPM toan cong ty NNC 2012-25 (BQ, 34,2%) + chenh da-thanh-pham vs toan cong ty (TB 2 nam kiem toan 2024/2025).
     r3 ghi nhan 'GPM ve TB 2012-25' cho tran 270k la SAI NHAN (270k ~ bien 42,5% tren chi phi mo hinh) — sua o day.
     Doi chieu bat buoc in ra: tran 'co so 1,40' (skeptic 242,5k) va kiem tra nam 2024 (gia, SL, bien thuc).
 (4) Gordon P/B kiem cheo voi ROE CHUAN HOA (ROE tung trang thai, tron theo trong so Bobby) — khong dung ROE dinh.
 (5) Upside doi xung CO CO SO (do nhay, khong vao tam): doi thu het GP — Tam Lap 2 (~2033), Tam Lap 3 (~2035) [FPTS 07/01/2026 tr.~9:
     Mui Tau con 17 nam, hon TL3 8 nam, TL2 10 nam] => tu 2034 stress giam mot nua o nhanh hoi bien.
NGUONG (DANG KY TRUOC KHI CHAY; khong sua sau khi thay so). Luoi 1.458 bo: r 11/13/15 x K NNC 0,87/0,97/1,07 x W {15/60/20/5, 25/50/20/5,
 35/50/10/5} x PW g2031:real {70:30,50:50,30:70} x trong so phan loai {Bobby 20/45/35, nghieng STRUCTURAL 40/35/25 (dieu kien doi nhan cua
 Bobby: STRUCTURAL >=0,40), nghieng CYCLICAL 15/35/50 (CYCLICAL >=0,50)} x SL nam thuong {1,05 ca ky (quan sat 2024), 1,10/1,20, 1,20/1,30}
 x co so tran {SL cua nhanh (tam), SL 1,40 (skeptic)}:
  RE <= P10 ; RE CO DIEU KIEN P10-P25 ; HOP LY P25-P75 ; NGHIENG DAT P75-P90 ; DAT >= P90.
  'Bien an toan' chi dung kem dieu kien (gia da hoa von: tran chu ky tai do tam = gia) — tinh o compare_r4.py SAU khoa.
"""
import sys, os, itertools, json, csv
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../r3/calc')))
_cwd = os.getcwd(); os.chdir(os.path.join(HERE, '../../r3/calc'))
import model_r3 as N3      # noqa: E402  (patch R.nnc_ex: doi xung BCDKT + tre GP CIP)
os.chdir(_cwd)
S, M, R = N3.S, N3.M, N3.R
SCN, PATHS, W0, PW0 = S.SCN, S.PATHS, S.W0, S.PW0
BV_NNC = N3.BVPS_NNC * M.N_SH / 1e9          # VCSH 30/09/2026 (ty)

# ---- (3) bien chu ky: du lieu
GPM_CO = float(np.mean(S.GPM_NNC))                                   # BQ ticker_financial Q4 TTM 2012-2025
AUD = {2024: dict(dt=257.44, gv=178.287, gpm_co=0.316, sl=1.05), 2025: dict(dt=360.39, gv=178.589, gpm_co=0.494, sl=1.20)}  # KT25 7.1/7.2, tr.9 ; SL FPTS
GAP = float(np.mean([1 - a['gv'] / a['dt'] - a['gpm_co'] for a in AUD.values()]))
GPM_STONE = GPM_CO + GAP
PEERS = {}
for row in csv.reader(open(os.path.join(HERE, '../../r3/calc/sector_gpm_roe.csv'))):
    if row and row[0] in ('NNC', 'KSB', 'DHA', 'VLB') and row[-1] == 'gpm':
        PEERS[row[0]] = float(np.mean([float(x) for x in row[1:15] if x]))
K0 = 0.97


def unit_cost(vol, K=K0): return M.VAR * K + M.FIX * K / vol


def eff_vol(v):  # SL TB nam 2028-2043 (Mui Tau het GP 2043)
    return (3 * v[0] + 13 * v[1]) / 16


def cap_for(vol):  return unit_cost(vol) / (1 - GPM_STONE)


V_REV = (1.10, 1.20)
CW_BOBBY = {'STRUCTURAL': .20, 'ADMIN_GATED': .45, 'CYCLICAL': .35}
STRESS = {'STRUCTURAL': 0.0, 'ADMIN_GATED': 0.5, 'CYCLICAL': 1.0}

# ---- Tan Lap: SL co_so theo nhanh (tl_vol = (2028-30, 2031+)); con lai giong S.tanlap
_tl6 = S.tanlap


def tanlap(k, path, endA, P):
    if not P.get('tl_vol'): return _tl6(k, path, endA, P)
    vol = {'tot': (1.40, 1.40), 'co_so': (1.30, None), 'xau': (1.30, 1.05), 'rat_xau': (0.90, 0.90)}[k]
    out = []
    for y in range(2027, endA + 1):
        if k == 'co_so':
            v = 1.30 if y == 2027 else (P['tl_vol'][0] if y <= 2030 else P['tl_vol'][1])
        else:
            v = vol[0] if y == 2027 else vol[1]
        f = 1.03 ** (y - 2026)
        ebit = v * (P['REL'] * S.nprice(k, y, P) * R.g(y, path) - R.costA(P) * f) - M.SGA_A * f
        out.append((y, max(ebit, 0) * (1 - M.TAX)))
    return M.pv(out, P['r'])


R.tanlap = tanlap
# upside doi thu het GP: tu 2034 stress giam mot nua (chi khi P['up2034'])
_np6 = S.nprice


def nprice(k, y, P):
    if P.get('up2034') and y >= 2034:
        return _np6(k, y, {**P, 'stress': P.get('stress', 0.0) * 0.5})
    return _np6(k, y, P)


S.nprice = nprice; R.nprice = nprice


def branch(name, over=None, v_rev=V_REV, cap_basis='branch'):
    """tra (V_NNC, V_MVC) cua 1 trang thai"""
    o = dict(over or {})
    if name == 'STRUCTURAL':
        o.update(stress=0.0, nnc_vol=(1.40, 1.40))
        cap = S.P_CYC
    else:
        o.update(stress=STRESS[name], nnc_vol=v_rev)
        if 'tl_vol' not in o: o['tl_vol'] = v_rev
        cap = cap_for(eff_vol(v_rev) if cap_basis == 'branch' else 1.40)
    old = S.P_CYC; S.P_CYC = cap
    try:
        vn, vm, _ = N3.EV3(o, detail=True)
    finally:
        S.P_CYC = old
    return vn, vm


def EV4(over=None, cw=CW_BOBBY, v_rev=V_REV, cap_basis='branch', detail=False):
    b = {n: branch(n, over, v_rev, cap_basis) for n in cw}
    vn = sum(cw[n] * b[n][0] for n in cw); vm = sum(cw[n] * b[n][1] for n in cw)
    return (vn, vm, b) if detail else vn


def nopat_norm(name, v_rev=V_REV):
    """LNST chuan hoa (tien 2026, nam dien hinh 2031+, kich ban co_so) cua NNC tu than (khong gom LK MVC/NHC, khong lai tien)"""
    if name == 'STRUCTURAL':
        p, v = 320.0, 1.40   # co_so 2031+ (moc 320) — dinh ben
    else:
        s = STRESS[name]; cap = cap_for(eff_vol(v_rev)); p = (1 - s) * 320 + s * min(320, cap); v = v_rev[1]
    ebit = v * (p - M.VAR * K0) - M.FIX * K0 - M.SGA + M.RENT
    return ebit * (1 - M.TAX), p, v


if __name__ == '__main__':
    out = {}
    print('=== 0. Kiem quy doi bien / gia von (du lieu) ===')
    print(f'GPM toan cong ty NNC TB 2012-25 (BQ) {GPM_CO:.3f}; peers TB 2012-25: ' + ', '.join(f'{k} {v:.3f}' for k, v in PEERS.items()))
    for y, a in AUD.items():
        g = 1 - a['gv'] / a['dt']; uc = a['gv'] / a['sl']; px = a['dt'] / a['sl']
        mod = (a['sl'] * M.VAR + M.FIX) * K0 / 1.03 ** (2026 - y) / a['sl']
        print(f'  {y}: GPM da thanh pham kiem toan {g:.1%} vs toan cong ty {a["gpm_co"]:.1%} (chenh {g-a["gpm_co"]:+.1%}); SL {a["sl"]} -> gia {px:.1f}k, '
              f'GV {uc:.1f}k/m3 ; chi phi mo hinh cung nam {mod:.1f}k/m3')
    print(f'  => GPM da chu ky = {GPM_CO:.3f} + chenh TB {GAP:+.4f} = {GPM_STONE:.3f}')
    for lab, v in [('SL 1,40 (co so skeptic)', 1.40), ('SL TB nhanh hoi bien 1,10/1,20 = %.3f' % eff_vol(V_REV), eff_vol(V_REV)),
                   ('SL 1,05 (nam 2024)', 1.05), ('SL TB 1,20/1,30 = %.3f' % eff_vol((1.20, 1.30)), eff_vol((1.20, 1.30)))]:
        print(f'  tran chu ky @ {lab:38s}: chi phi {unit_cost(v):6.1f}k -> tran {cap_for(v):6.1f}k/m3 (tien 2026); bien tai 242,5k = {1-unit_cost(v)/242.5:.1%}')
    p24_26 = AUD[2024]['dt'] / AUD[2024]['sl'] * 1.03 ** 2
    print(f'  kiem 2024 (tien 2026): gia {p24_26:.1f}k o SL 1,05 -> bien mo hinh {1-unit_cost(1.05)/p24_26:.1%} ; tran tam @1,05 = {cap_for(1.05):.1f}k')
    print(f'  r3 P_CYC {S.P_CYC:.1f}k = bien {1-unit_cost(1.40)/S.P_CYC:.1%} tren chi phi mo hinh @1,40 (nhan r3 "GPM ve TB" SAI)')
    out['cycle'] = dict(gpm_co=GPM_CO, gap=GAP, gpm_stone=GPM_STONE, peers=PEERS, cap_branch=cap_for(eff_vol(V_REV)), cap_140=cap_for(1.40),
                        cost_branch=unit_cost(eff_vol(V_REV)), cost_140=unit_cost(1.40), eff_vol=eff_vol(V_REV), p2024_in2026=p24_26)

    vn, vm, b = EV4(detail=True); out['tam'] = vn; out['mvc_simul'] = vm
    out['branches'] = {n: dict(w=CW_BOBBY[n], V_NNC=b[n][0], V_MVC=b[n][1]) for n in b}
    print(f'\n=== 1. TAM NNC r4 (Bobby 20/45/35; W 25/50/20/5 x PW 50/50; r13; K 0,97): {vn:,.0f} d/cp | MVC giai dong thoi {vm:,.0f}')
    for n in b: print(f'  {n:11s} w {CW_BOBBY[n]:.2f}: NNC {b[n][0]:8,.0f} | MVC {b[n][1]:7,.0f}')
    # 3 kich ban NDT: tich cuc = STRUCTURAL ; co so = ADMIN_GATED ; tieu cuc = CYCLICAL (moi nhanh da ky vong theo W/PW)
    out['sc3'] = {'tich_cuc': b['STRUCTURAL'][0], 'co_so': b['ADMIN_GATED'][0], 'tieu_cuc': b['CYCLICAL'][0]}
    # o (co_so, PW) cua tung nhanh
    cells = {}
    for n in CW_BOBBY:
        o = {'stress': STRESS[n]}
        if n != 'STRUCTURAL': o.update(nnc_vol=V_REV, tl_vol=V_REV)
        else: o.update(nnc_vol=(1.40, 1.40))
        old = S.P_CYC; S.P_CYC = S.P_CYC if n == 'STRUCTURAL' else cap_for(eff_vol(V_REV))
        _, _, res = N3.EV3(o, detail=True); S.P_CYC = old
        cells[n] = {f'{k}|{p}': res[(k, p)]['V_NNC_ps'] for k in SCN for p in PATHS}
        print(f'  {n:11s} ' + ' '.join(f'{k} {np.mean([res[(k, p)]["V_NNC_ps"] for p in PATHS]):7,.0f}' for k in SCN))
    out['cells'] = cells

    print('\n=== 2. Gordon P/B = (ROE-g)/(r-g), r13 g3, ROE CHUAN HOA (NNC tu than, nam dien hinh co_so, tien 2026) ===')
    gor = {}; roe_w = 0
    for n in CW_BOBBY:
        npt, p, v = nopat_norm(n); roe = npt / BV_NNC; roe_w += CW_BOBBY[n] * roe
        gor[n] = dict(nopat=npt, p=p, v=v, roe=roe, pb=(roe - .03) / .10, ps=(roe - .03) / .10 * N3.BVPS_NNC)
        print(f'  {n:11s}: gia {p:5.1f}k SL {v:.2f} -> LNST {npt:5.1f} ty, ROE {roe:5.1%} -> P/B {(roe-.03)/.10:4.2f}x {gor[n]["ps"]:8,.0f}')
    pbw = (roe_w - .03) / .10
    print(f'  ROE chuan hoa tron Bobby {roe_w:.1%} -> P/B {pbw:.2f}x -> {pbw*N3.BVPS_NNC:,.0f} d/cp (Gordon vinh vien; mo huu han 2043 + tien lon => doi chieu tho)')
    print(f'  ROE ben ham y cua TAM {vn:,.0f} (P/B {vn/N3.BVPS_NNC:.2f}x): {.03 + vn/N3.BVPS_NNC*.10:.1%}')
    out['gordon'] = dict(by_state=gor, roe_norm=roe_w, pb_norm=pbw, ps_norm=pbw * N3.BVPS_NNC, roe_implied=.03 + vn / N3.BVPS_NNC * .10)

    # ---- 3. luoi 1.458
    Ws = [{'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05}, W0, {'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05}]
    PWs = [{'g2031': .7, 'real': .3}, PW0, {'g2031': .3, 'real': .7}]
    CWs = [CW_BOBBY, {'STRUCTURAL': .40, 'ADMIN_GATED': .35, 'CYCLICAL': .25}, {'STRUCTURAL': .15, 'ADMIN_GATED': .35, 'CYCLICAL': .50}]
    VRs = [(1.05, 1.05), V_REV, (1.20, 1.30)]
    grid = []
    for r, kk, wi, pi, ci, vi, cb in itertools.product((0.11, 0.13, 0.15), (0.87, 0.97, 1.07), range(3), range(3), range(3), range(3), ('branch', '1.40')):
        vnn, vmm, _ = EV4({'r': r, 'K': kk, 'W': Ws[wi], 'PW': PWs[pi]}, cw=CWs[ci], v_rev=VRs[vi], cap_basis=cb, detail=True)
        grid.append(dict(r=r, K=kk, W=wi, PW=pi, CW=ci, VR=vi, cap=cb, ev=vnn, ev_mvc=vmm))
    ge = np.array([x['ev'] for x in grid]); gp = {q: float(np.percentile(ge, q)) for q in (5, 10, 25, 50, 75, 90, 95)}
    gp['min'] = float(ge.min()); gp['max'] = float(ge.max())
    print(f'\n=== 3. Luoi {len(ge)} bo: ' + ' '.join(f'P{q} {v:,.0f}' for q, v in gp.items()))
    for key, labs in [('CW', ['Bobby', 'nghieng STRUCT', 'nghieng CYC']), ('VR', ['SL 1,05', 'SL 1,10/1,20', 'SL 1,20/1,30']), ('cap', None)]:
        vals = sorted(set(x[key] for x in grid), key=str)
        for i, v in enumerate(vals):
            sub = np.array([x['ev'] for x in grid if x[key] == v])
            print(f'   {key}={labs[v] if labs else v}: P10 {np.percentile(sub,10):,.0f} P50 {np.median(sub):,.0f} P90 {np.percentile(sub,90):,.0f}')
    out['grid_pct'] = gp; out['grid_n'] = len(ge)
    with open('grid_r4.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    print('NGUONG (dang ky truoc): RE <= {:,.0f} | RE CO DIEU KIEN {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | NGHIENG DAT {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))

    # ---- 4. do nhay
    print('\n=== 4. Do nhay (so voi tam r4) ===')
    tor = {}
    def T(lab, over=None, **kw):
        x = EV4(over, **kw); tor[lab] = x - vn; print(f'  {lab:84s} {x:8,.0f} ({x - vn:+7,.0f})')
    T('tran chu ky co so SL 1,40 (skeptic 242,5k ~ %.1fk)' % cap_for(1.40), cap_basis='1.40')
    T('trong so phan loai nghieng STRUCTURAL 40/35/25', cw=CWs[1]); T('trong so nghieng CYCLICAL 15/35/50', cw=CWs[2])
    T('chi CYCLICAL (100% hoi bien tron)', cw={'CYCLICAL': 1.0}); T('chi STRUCTURAL (= tam r3)', cw={'STRUCTURAL': 1.0})
    T('SL nam thuong 1,05 ca ky (quan sat 2024)', v_rev=(1.05, 1.05)); T('SL nam thuong 1,20/1,30', v_rev=(1.20, 1.30))
    T('(+) upside doi thu het GP: tu 2034 stress giam mot nua (TL2 ~2033, TL3 ~2035)', {'up2034': True})
    T('Tan Lap KHONG cat SL o nhanh hoi bien (giu 1,30)', {'tl_vol': None})
    T('K chi phi 0,87', {'K': 0.87}); T('K chi phi 1,07', {'K': 1.07})
    T('r 11%', {'r': 0.11}); T('r 15%', {'r': 0.15})
    T('PW g2031 70/real 30', {'PW': PWs[0]}); T('PW g2031 30/real 70', {'PW': PWs[2]})
    T('STRESS duong gia danh nghia phang 100%', {'PW': {'flat': 1.0}})
    T('bo LN cho thue Nui Nho', {'rent': False})
    T('bo doi xung BCDKT (ky quy + thue hoan lai)', {'bs_sym': False})
    T('holding MVC->NNC 15%', {'hold': 0.15})
    out['tornado'] = tor
    # cau noi tam r3 -> r4
    r3 = EV4(cw={'STRUCTURAL': 1.0}); a = EV4(cw={'STRUCTURAL': .2, 'ADMIN_GATED': .45, 'CYCLICAL': .35}, cap_basis='1.40')
    out['bridge_r3'] = dict(r3=r3, r4_cap140=a, r4=vn)
    print(f'\n  Cau noi: tam r3 {r3:,.0f} -> r4 voi tran SL 1,40 {a:,.0f} -> r4 tran theo SL nhanh {vn:,.0f}')
    # V_NNC cho MVC
    print(f'\n=== 5. V_NNC nhat quan cho MVC r7: {vn:,.0f} d/cp NNC (MVC giai dong thoi cung he {vm:,.0f} d/cp) ===')
    with open('model_r4_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
