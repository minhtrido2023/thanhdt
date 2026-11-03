"""DD MVC r7 (03/11/2026 ~21:00 ICT) — CHUAN HOA CHU KY MO HIEN HUU (Tan Lap + NNC cung cum Dong Phu), CUNG logic NNC r4.
MU GIA: khong doc gia/von hoa/P-E MVC hay NNC trong file nay. Chay: /home/trido/thanhdt/wc_venv/bin/python -B model_r7.py
He thong: tai dung NNC r4 (../../../dd_NNC_20261030/r4/calc/model_r4.py, da khoa LOCK_md5_r4.txt 20:24:58) -> model_r3 -> MVC r6
(valuation_base/model_r5/model_r6) — KHONG SUA, md5 ghi o LOCK_md5_r7.txt. V_NNC giai vong cheo DONG THOI trong tung trang thai
(V_NNC = N_ex + c V_MVC ; V_MVC = D_MVC + s V_NNC ; c 0,103 ; s 0,4407 ; holding 0) => V_NNC ky vong = 67.596 = tam NNC r4.

THAY DOI r7 so voi r6 (r6 = tam o stress 0 = bien dinh vinh vien cho Tan Lap + NNC; SKEPTIC_R3 'He qua MVC'):
 (1) TAM = tron 3 trang thai theo Bobby §4: STRUCTURAL 0,20 (bien dinh, Tan Lap 1,30 / NNC 1,40) ; ADMIN_GATED 0,45 (hoi bien mot nua,
     SL nam thuong) ; CYCLICAL 0,35 (hoi bien tron ve TB chu ky, SL nam thuong). Ap tu 2028 cho Tan Lap + NNC (cung cum, gia MVC = REL x gia NNC).
 (2) SL nam thuong Tan Lap co_so 1,10 (2028-30) / 1,20 (2031+) = cung muc NNC (cong suat ~1,4 ca hai; co so: NNC 2024 1,05 tr m3 = 74% tran).
 (3) Tran gia chu ky = tran NNC r4 (bien da thanh pham 34,3% tren chi phi NNC o SL nhanh -> 249,7k tien 2026; Tan Lap ban REL x tran).
 GIU nguyen tac du an MOI = so sach (r6): mo moi 438,4 so sach moi kich ban (+ tre GP Bobby F6), dat o so sach 30, cum CN 500 & mua NNC 51%
 NPV 0, CIP Tam Lap NNC so sach; doi xung: upside mo moi (+) va NPV gia xau (-) chi la do nhay co nhan.
 (4) Gordon P/B voi ROE CHUAN HOA theo trang thai (STRUCTURAL = ROE Q3/26 trailing 20,7% ; CYCLICAL = TB 2017-25 ; ADMIN = trung diem).
 (5) Lo trinh no rong base tinh lai voi CFO 2028 KY VONG qua 3 trang thai; nguong canh bao = lo trinh + 150 ty.
NGUONG (DANG KY TRUOC KHI CHAY; khong sua sau khi thay so). Luoi 13.122 bo: r 11/13/15 x chi phi Tan Lap 0,85/1/1,15 x REL 0,88/0,91/0,95 x
 W {15/60/20/5, 25/50/20/5, 35/50/10/5} x PW g2031:real {70:30,50:50,30:70} x trong so trang thai {20/45/35, 40/35/25, 15/35/50}
 x SL nam thuong {1,05; 1,10/1,20; 1,20/1,30} x co so tran {SL nhanh, SL 1,40} x han GP Tan Lap {2035, W, 2045}:
  RE <= P10 ; RE CO DIEU KIEN P10-P25 ; HOP LY P25-P75 ; NGHIENG DAT P75-P90 ; DAT >= P90.
  'Bien an toan' chi dung kem dieu kien (gia da hoa von) — tinh o compare_r7.py SAU khoa.
"""
import sys, os, itertools, json, csv
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
N4D = os.path.abspath(os.path.join(HERE, '../../../dd_NNC_20261030/r4/calc'))
sys.path.insert(0, N4D)
import model_r4 as N4      # noqa: E402
N3, S, M, R = N4.N3, N4.S, N4.M, N4.R
SCN, PATHS, W0, PW0 = S.SCN, S.PATHS, S.W0, S.PW0
CW = N4.CW_BOBBY; STRESS = N4.STRESS; V_REV = N4.V_REV


def branch(name, over=None, v_rev=V_REV, cap_basis='branch'):
    o = dict(over or {})
    if name == 'STRUCTURAL':
        o.update(stress=0.0, nnc_vol=(1.40, 1.40)); cap = S.P_CYC
    else:
        o.update(stress=STRESS[name], nnc_vol=v_rev)
        if 'tl_vol' not in o: o['tl_vol'] = v_rev
        cap = N4.cap_for(N4.eff_vol(v_rev) if cap_basis == 'branch' else 1.40)
    old = S.P_CYC; S.P_CYC = cap
    try:
        vn, vm, res = N3.EV3(o, detail=True)
    finally:
        S.P_CYC = old
    return dict(vn=vn, vm=vm, res=res, cap=cap)


def EV7(over=None, cw=CW, v_rev=V_REV, cap_basis='branch', detail=False):
    b = {n: branch(n, over, v_rev, cap_basis) for n in cw}
    vm = sum(cw[n] * b[n]['vm'] for n in cw); vn = sum(cw[n] * b[n]['vn'] for n in cw)
    return (vm, vn, b) if detail else vm


if __name__ == '__main__':
    out = {}
    vm, vn, b = EV7(detail=True); out['tam'] = vm; out['V_NNC'] = vn
    out['branches'] = {n: dict(w=CW[n], V_MVC=b[n]['vm'], V_NNC=b[n]['vn'], cap=b[n]['cap']) for n in b}
    print(f'=== 1. TAM MVC r7 (Bobby 20/45/35; W 25/50/20/5 x PW g2031 50/real 50; r13; holding 0; du an moi so sach): {vm:,.0f} d/cp | V_NNC dong thoi {vn:,.0f}')
    print(f'  tran chu ky {N4.cap_for(N4.eff_vol(V_REV)):.1f}k/m3 NNC -> Tan Lap REL 0,91 x = {0.91*N4.cap_for(N4.eff_vol(V_REV)):.1f}k; chi phi Tan Lap {R.costA(R.BASE):.1f}k '
          f'-> bien Tan Lap o tran {1-R.costA(R.BASE)/(0.91*N4.cap_for(N4.eff_vol(V_REV))):.1%} (dinh 2026 {1-R.costA(R.BASE)/(0.91*380):.1%})')
    for n in b:
        r = b[n]['res']
        print(f'  {n:11s} w {CW[n]:.2f}: MVC {b[n]["vm"]:7,.0f} | NNC {b[n]["vn"]:8,.0f} | ' + ' '.join(f'{k} {np.mean([r[(k, p)]["ps"] for p in PATHS]):7,.0f}' for k in SCN))
    # tung nhanh x duong gia (W ky vong)
    bp = {}
    for n in CW:
        for p in PATHS:
            x = branch(n, {'PW': {p: 1.0}}); bp[f'{n}|{p}'] = dict(V_MVC=x['vm'], V_NNC=x['vn'])
    out['branch_path'] = bp
    # cau noi ky vong (ty): trong so W x PW x CW tren cac o
    keys = ['A', 'B', 'BOT', 'gach_xang', 'dat_o', 'LK_nho_ICD', 'Q4', 'NETFIN', 'Dm', 'stake', 'VM']
    br = {kk: sum(CW[n] * W0[k] * PW0[p] * b[n]['res'][(k, p)][kk] for n in CW for k in SCN for p in PATHS) for kk in keys}
    out['bridge_ty'] = br
    print('\n=== 2. CAU NOI KY VONG (ty; d/cp = x10) ===\n  ' + ' | '.join(f'{kk} {v:,.1f}' for kk, v in br.items()))

    print('\n=== 3. Gordon P/B = (ROE-g)/(r-g), r13 g3, BVPS 15.460, ROE CHUAN HOA theo trang thai ===')
    roe_avg = float(np.mean(list(S.ROE_MVC.values())))
    st = {'STRUCTURAL': S.ROE_NOW, 'ADMIN_GATED': (S.ROE_NOW + roe_avg) / 2, 'CYCLICAL': roe_avg}
    gor = {n: dict(roe=x, pb=(x - .03) / .10, ps=(x - .03) / .10 * S.BVPS) for n, x in st.items()}
    rw = sum(CW[n] * st[n] for n in CW); gor['tron'] = dict(roe=rw, pb=(rw - .03) / .10, ps=(rw - .03) / .10 * S.BVPS)
    for n, d in gor.items(): print(f'  {n:11s}: ROE {d["roe"]:5.1%} -> P/B {d["pb"]:4.2f}x -> {d["ps"]:7,.0f}')
    out['gordon'] = gor; out['roe_implied'] = .03 + vm / S.BVPS * .10
    print(f'  ROE ben ham y cua TAM {vm:,.0f} (P/B {vm/S.BVPS:.2f}x): {out["roe_implied"]:.1%}')

    # ---- 4. luoi
    Ws = [{'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05}, W0, {'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05}]
    PWs = [{'g2031': .7, 'real': .3}, PW0, {'g2031': .3, 'real': .7}]
    CWs = [CW, {'STRUCTURAL': .40, 'ADMIN_GATED': .35, 'CYCLICAL': .25}, {'STRUCTURAL': .15, 'ADMIN_GATED': .35, 'CYCLICAL': .50}]
    VRs = [(1.05, 1.05), V_REV, (1.20, 1.30)]
    grid = []
    for r, ca, rel, wi, pi, ci, vi, cb, en in itertools.product((0.11, 0.13, 0.15), (0.85, 1.0, 1.15), (0.88, 0.91, 0.95), range(3), range(3), range(3),
                                                                  range(3), ('branch', '1.40'), (2035, 'W', 2045)):
        m_, n_, _ = EV7({'r': r, 'ca': ca, 'REL': rel, 'W': Ws[wi], 'PW': PWs[pi], 'endA': en}, cw=CWs[ci], v_rev=VRs[vi], cap_basis=cb, detail=True)
        grid.append(dict(r=r, ca=ca, rel=rel, W=wi, PW=pi, CW=ci, VR=vi, cap=cb, endA=en, ev=m_, ev_nnc=n_))
    ge = np.array([x['ev'] for x in grid]); gp = {q: float(np.percentile(ge, q)) for q in (5, 10, 25, 50, 75, 90, 95)}
    gp['min'] = float(ge.min()); gp['max'] = float(ge.max())
    print(f'\n=== 4. Luoi {len(ge)} bo: ' + ' '.join(f'P{q} {v:,.0f}' for q, v in gp.items()))
    for key, labs in [('CW', ['Bobby', 'nghieng STRUCT', 'nghieng CYC']), ('VR', ['SL 1,05', 'SL 1,10/1,20', 'SL 1,20/1,30']), ('cap', None), ('endA', None)]:
        for v in sorted(set(x[key] for x in grid), key=str):
            sub = np.array([x['ev'] for x in grid if x[key] == v])
            print(f'   {key}={labs[v] if labs else v}: P10 {np.percentile(sub,10):,.0f} P50 {np.median(sub):,.0f} P90 {np.percentile(sub,90):,.0f}')
    out['grid_pct'] = gp; out['grid_n'] = len(ge)
    with open('grid_r7.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    print('NGUONG (dang ky truoc): RE <= {:,.0f} | RE CO DIEU KIEN {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | NGHIENG DAT {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))

    # ---- 5. do nhay
    print('\n=== 5. Do nhay (so voi tam r7) ===')
    tor = {}
    def T(lab, over=None, **kw):
        x = EV7(over, **kw); tor[lab] = x - vm; print(f'  {lab:84s} {x:8,.0f} ({x - vm:+7,.0f})')
    T('tran chu ky co so SL 1,40 (236,1k)', cap_basis='1.40')
    T('trong so nghieng STRUCTURAL 40/35/25', cw=CWs[1]); T('trong so nghieng CYCLICAL 15/35/50', cw=CWs[2])
    T('chi CYCLICAL (100% hoi bien tron)', cw={'CYCLICAL': 1.0}); T('chi STRUCTURAL (= tam r6 + V_NNC r3)', cw={'STRUCTURAL': 1.0})
    T('SL nam thuong 1,05 ca ky', v_rev=(1.05, 1.05)); T('SL nam thuong 1,20/1,30', v_rev=(1.20, 1.30))
    T('Tan Lap KHONG cat SL o nhanh hoi bien (giu 1,30; chi NNC cat)', {'tl_vol': None})
    T('(+) upside doi thu het GP: tu 2034 stress giam mot nua', {'up2034': True})
    T('han GP Tan Lap 2035 moi muc', {'endA': 2035}); T('han GP Tan Lap 2045 moi muc', {'endA': 2045})
    T('chi phi Tan Lap +15%', {'ca': 1.15}); T('chi phi Tan Lap -15%', {'ca': 0.85})
    T('REL 0,88', {'REL': 0.88}); T('REL 0,95', {'REL': 0.95})
    T('r 11%', {'r': 0.11}); T('r 15%', {'r': 0.15})
    T('PW g2031 70/real 30', {'PW': PWs[0]}); T('PW g2031 30/real 70', {'PW': PWs[2]})
    T('STRESS duong gia danh nghia phang 100%', {'PW': {'flat': 1.0}})
    T('mo moi: + upside kich ban tot (IRR 17-21%)', {'up': True}); T('mo moi: + NPV gia xau/rat xau', {'mine_xau': True})
    T('mo moi: hai phia co trong so', {'up': True, 'mine_xau': True}); T('mo moi: bo rui ro tre GP', {'delay': False})
    T('holding 15%', {'hold': 0.15}); T('holding 30%', {'hold': 0.30})
    T('V_NNC co dinh 67.596 (= tam NNC r4, khong giai theo nhanh)', {'VN_fix': 67596})
    T('V_NNC co dinh 77.656 (NNC-DD 31/10 cong bo)', {'VN_fix': 77656})
    x1 = EV7({'VN_fix': 60000}); x2 = EV7({'VN_fix': 70000}); slope = x2 - x1
    print(f'  do doc: MVC {slope:+,.0f} d/cp moi +10.000 d/cp V_NNC (V_NNC co dinh)'); out['vnnc_slope_per10k'] = slope
    out['tornado'] = tor

    # ---- 6. lo trinh no rong (uoc luong) voi CFO 2028 ky vong qua trang thai
    capl = 1500 - R.BOOK_MINE; DIVP = 100.0; DIVR = 10.6
    def op(y, vol, px):
        f = 1.03 ** (y - 2026)
        return (vol * (0.91 * px - R.costA(R.BASE) * f) - M.SGA_A * f) * (1 - M.TAX) + M.BOT_GP * (1 - M.TAX) + M.D_EBIT['co_so'] * (1 - M.TAX)
    op27 = op(2027, 1.30, 380)
    cap = N4.cap_for(N4.eff_vol(V_REV))
    op28 = {n: op(2028, 1.30 if n == 'STRUCTURAL' else V_REV[0], (1 - STRESS[n]) * 360 + STRESS[n] * min(360, cap)) for n in CW}
    op28e = sum(CW[n] * op28[n] for n in CW)
    nd26 = -M.NETFIN - M.Q4_DIRECT
    nd27 = nd26 + 0.6 * capl - op27 - DIVR + DIVP
    nd28 = nd27 + 0.4 * capl - op28e - DIVR + DIVP
    nd28c = nd27 + 0.4 * capl - op28['CYCLICAL'] - DIVR + DIVP
    out['net_debt_path'] = dict(end2026=nd26, end2027=nd27, end2028=nd28, end2028_cyc=nd28c, op27=op27, op28=op28, op28_exp=op28e, alert_over_path=150)
    print(f'\n=== 6. Lo trinh no rong base (uoc luong; chua tinh khau hao/von luu dong; mo moi chua co dong tien 2028): cuoi 2026 {nd26:,.0f} | 2027 {nd27:,.0f} '
          f'| 2028 {nd28:,.0f} ty (CYCLICAL {nd28c:,.0f}); CFO 2027 {op27:,.0f}, 2028 ky vong {op28e:,.0f} (' + ', '.join(f'{n} {v:,.0f}' for n, v in op28.items()) + ')')
    print(f'  Nguong canh bao: no rong vuot lo trinh > 150 ty (2027 > {nd27+150:,.0f}; 2028 > {nd28+150:,.0f})')
    with open('model_r7_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
