"""DD MVC r8 (03/11/2026 ~21:15 ICT) — sua theo SKEPTIC_R7_20261103.md. Khong dung gia thi truong (MVC/NNC: gia, von hoa, P/E) lam dau vao.
Chay: /home/trido/thanhdt/wc_venv/bin/python -B model_r8.py. He thong: NNC r5 (../../../dd_NNC_20261030/r5/calc/nnc_model_r5.py, khoa LOCK_md5_r5
20:49:47) -> model_r4 -> model_r3 -> MVC r6 — KHONG SUA (md5 o LOCK_md5_r8.txt). V_NNC giai dong thoi trong tung trang thai (c 0,103; s 0,4407; holding 0).

THAY DOI r8 so voi r7:
 (1) Anh xa ADMIN nhat quan NNC r5 cho CA Tan Lap: stress 0,5 nam 2028 roi 1,0 tu 2029 (truc {0,5 vinh vien; tre 1 nam; 1,0 tu 2028} vao luoi).
 (2) Dinh phi gia von Tan Lap cung ty le NNC: costTL(v) = costA x unit_cost_NNC(v)/unit_cost_NNC(1,30) (VAR 110/FIX 70 cua NNC; 1,30 = SL hieu chinh
     costA — GIA DINH). Ap DOI XUNG moi kich ban (SL 1,40 re hon, 1,05/0,90 dat hon).
 (3) Bien chu ky Tan Lap: KHONG co du lieu bien/SL mang da rieng cua MVC (thuyet minh gop 'gia von hang da ban' da+gach+xang; BCTN 2025, BCTC
     Q2/Q3/6T 2026 khong tach bo phan) => CHUA KIEM. Truc {25%, 30%, ~NNC} ; ~NNC = gia chu ky Tan Lap = REL x tran NNC (gia cum), bien tu chi phi
     rieng Tan Lap (co dinh phi). TAM dung ~NNC (neo GIA cum + chi phi rieng: co co so); 25/30% = truc luoi + do nhay.
 (4) Lo trinh no rong: CFO = NOPAT - lai vay sau thue (lai suat GIA DINH 7%/nam tren no rong binh quan; lai suat hieu dung vay NH 9T/2026 do
     tu BCTC ~4,5% la can duoi); nguong canh bao chinh lai.
 (5) Gordon nhat quan anh xa (ADMIN = CYC o nam dien hinh) + phan ra DCF-CYC vs Gordon-CYC.
GIU nguyen tac du an MOI (r6/r7): mo moi 389,7 ky vong (so sach 438,4 - tre GP), dat 30 so sach, cum CN & mua NNC 51% NPV 0.
NGUONG (DANG KY TRUOC KHI CHAY; khong sua sau khi thay so). Luoi = luoi r7 (13.122) x anh xa ADMIN {0,5 vv; tre 1 nam; 1,0} x bien chu ky Tan Lap
 {25%, 30%, ~NNC} = 118.098 bo: RE <= P10 ; RE CO DIEU KIEN P10-P25 ; HOP LY P25-P75 ; NGHIENG DAT P75-P90 ; DAT >= P90.
"""
import sys, os, itertools, json, csv
import numpy as np
from multiprocessing import Pool
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
N5D = os.path.abspath(os.path.join(HERE, '../../../dd_NNC_20261030/r5/calc'))
sys.path.insert(0, N5D)
_cwd = os.getcwd(); os.chdir(N5D)
import nnc_model_r5 as N5   # noqa: E402
os.chdir(_cwd)
N4, N3, S, M, R = N5.N4, N5.N3, N5.S, N5.M, N5.R
SCN, PATHS, W0, PW0 = S.SCN, S.PATHS, S.W0, S.PW0
CW = N5.CW_BOBBY; V_REV = N5.V_REV; ADMIN = N5.ADMIN
V_CAL = 1.30


def fixfac(v): return N4.unit_cost(v) / N4.unit_cost(V_CAL)


def tanlap8(k, path, endA, P):
    vol = {'tot': (1.40, 1.40), 'co_so': (1.30, 1.30), 'xau': (1.30, 1.05), 'rat_xau': (0.90, 0.90)}[k]
    tlv = P.get('tl_vol'); fx = P.get('tl_fix', 'all'); tlm = P.get('tl_m', 'nnc')
    cap_tl = None
    if tlm != 'nnc' and P.get('stress', 0) > 0:
        ev = N4.eff_vol(tlv) if tlv else 1.30
        cap_tl = R.costA(P) * fixfac(ev) / (1 - tlm) / P['REL']      # gia NNC-tuong-duong de bien Tan Lap = tlm (tien 2026)
    out = []
    for y in range(2027, endA + 1):
        if k == 'co_so' and tlv:
            v = 1.30 if y == 2027 else (tlv[0] if y <= 2030 else tlv[1])
        else:
            v = vol[0] if y == 2027 else vol[1]
            if k == 'co_so' and not tlv and P.get('tl_cut') and 2028 <= y <= 2030: v = 1.10
        ff = fixfac(v) if (fx == 'all' or (fx == 'stress' and P.get('stress', 0) > 0 and y >= 2028)) else 1.0
        f = 1.03 ** (y - 2026)
        if cap_tl is not None:
            old = S.P_CYC; S.P_CYC = cap_tl
            try: px = S.nprice(k, y, P)
            finally: S.P_CYC = old
        else:
            px = S.nprice(k, y, P)
        ebit = v * (P['REL'] * px * R.g(y, path) - R.costA(P) * ff * f) - M.SGA_A * f
        out.append((y, max(ebit, 0) * (1 - M.TAX)))
    return M.pv(out, P['r'])


R.tanlap = tanlap8; S.tanlap = tanlap8


def branch(name, over=None, v_rev=V_REV, cap_basis='branch', admin='ramp'):
    o = dict(over or {})
    if name == 'STRUCTURAL':
        o.update(stress=0.0, ramp=False, nnc_vol=(1.40, 1.40)); cap = S.P_CYC
    else:
        st, rp = ADMIN[admin] if name == 'ADMIN_GATED' else (1.0, False)
        o.update(stress=st, ramp=rp, nnc_vol=v_rev)
        if 'tl_vol' not in o: o['tl_vol'] = v_rev
        cap = N4.cap_for(N4.eff_vol(v_rev) if cap_basis == 'branch' else 1.40)
    old = S.P_CYC; S.P_CYC = cap
    try:
        vn, vm, res = N3.EV3(o, detail=True)
    finally:
        S.P_CYC = old
    return dict(vn=vn, vm=vm, res=res, cap=cap)


def EV8(over=None, cw=CW, v_rev=V_REV, cap_basis='branch', admin='ramp', detail=False):
    b = {n: branch(n, over, v_rev, cap_basis, admin) for n in cw}
    vm = sum(cw[n] * b[n]['vm'] for n in cw); vn = sum(cw[n] * b[n]['vn'] for n in cw)
    return (vm, vn, b) if detail else vm


Ws = [{'tot': .15, 'co_so': .60, 'xau': .20, 'rat_xau': .05}, W0, {'tot': .35, 'co_so': .50, 'xau': .10, 'rat_xau': .05}]
PWs = [{'g2031': .7, 'real': .3}, PW0, {'g2031': .3, 'real': .7}]
CWs = [CW, {'STRUCTURAL': .40, 'ADMIN_GATED': .35, 'CYCLICAL': .25}, {'STRUCTURAL': .15, 'ADMIN_GATED': .35, 'CYCLICAL': .50}]
VRs = [(1.05, 1.05), V_REV, (1.20, 1.30)]
AMs = ['perm05', 'ramp', 'full']; TLMs = [0.25, 0.30, 'nnc']


def _cell(a):
    r, ca, rel, wi, pi, ci, vi, cb, en, am, tm = a
    m_, n_, _ = EV8({'r': r, 'ca': ca, 'REL': rel, 'W': Ws[wi], 'PW': PWs[pi], 'endA': en, 'tl_m': tm}, cw=CWs[ci], v_rev=VRs[vi], cap_basis=cb, admin=am, detail=True)
    return dict(r=r, ca=ca, rel=rel, W=wi, PW=pi, CW=ci, VR=vi, cap=cb, endA=en, admin=am, tl_m=tm, ev=m_, ev_nnc=n_)


INT = 0.07


def debt_path(tlm='nnc', rate=INT):
    """no rong (ty): NOPAT (gom BOT, gach/xang co_so) - lai vay sau thue (rate x no rong binh quan) + capex mo moi + co tuc rong."""
    capl = 1500 - R.BOOK_MINE; DIVP = 100.0; DIVR = 10.6
    cap = N4.cap_for(N4.eff_vol(V_REV)); ff = fixfac(V_REV[0])
    def nopat(y, vol, n):
        f = 1.03 ** (y - 2026); c = R.costA(R.BASE) * (fixfac(vol) if y >= 2028 else 1.0)
        if y == 2027: px = 380.0
        else:
            s = 0.0 if n == 'STRUCTURAL' else (0.5 if n == 'ADMIN_GATED' else 1.0)   # 2028: ADMIN tre 1 nam = 0,5
            capx = cap if tlm == 'nnc' else R.costA(R.BASE) * ff / (1 - tlm) / 0.91
            px = (1 - s) * 360 + s * min(360, capx)
        return (vol * (0.91 * px - c * f) - M.SGA_A * f) * (1 - M.TAX) + M.BOT_GP * (1 - M.TAX) + M.D_EBIT['co_so'] * (1 - M.TAX)
    def step(nd0, op, capex):
        nd1 = nd0
        for _ in range(30):
            it = rate * (nd0 + nd1) / 2; nd1 = nd0 + capex - (op - it * (1 - M.TAX)) - DIVR + DIVP
        return nd1, it
    nd26 = -M.NETFIN - M.Q4_DIRECT
    op27 = nopat(2027, 1.30, 'STRUCTURAL'); nd27, i27 = step(nd26, op27, 0.6 * capl)
    out = dict(end2026=nd26, op27=op27, end2027=nd27, int2027=i27)
    for n in CW:
        op28 = nopat(2028, 1.30 if n == 'STRUCTURAL' else V_REV[0], n); nd28, i28 = step(nd27, op28, 0.4 * capl)
        out[n] = dict(op28=op28, int2028=i28, end2028=nd28)
    out['end2028_exp'] = sum(CW[n] * out[n]['end2028'] for n in CW); out['op28_exp'] = sum(CW[n] * out[n]['op28'] for n in CW)
    out['int_cum_2027_28_exp'] = i27 + sum(CW[n] * out[n]['int2028'] for n in CW)
    return out


if __name__ == '__main__':
    out = {}
    vm, vn, b = EV8(detail=True); out['tam'] = vm; out['V_NNC'] = vn
    out['branches'] = {n: dict(w=CW[n], V_MVC=b[n]['vm'], V_NNC=b[n]['vn']) for n in b}
    cap = N4.cap_for(N4.eff_vol(V_REV)); ctl = R.costA(R.BASE) * fixfac(N4.eff_vol(V_REV))
    print(f'=== 1. TAM MVC r8 (Bobby 20/45/35; ADMIN tre 1 nam; dinh phi Tan Lap; bien chu ky Tan Lap ~NNC; W 25/50/20/5 x PW 50/50; r13): {vm:,.0f} d/cp | V_NNC {vn:,.0f}')
    print(f'  Tan Lap o tran: gia 0,91 x {cap:.1f} = {0.91*cap:.1f}k; chi phi @SL {N4.eff_vol(V_REV):.3f} = {ctl:.1f}k (costA {R.costA(R.BASE):.1f} x {fixfac(N4.eff_vol(V_REV)):.3f}) '
          f'-> bien {1-ctl/(0.91*cap):.1%} (NNC {1-N4.unit_cost(N4.eff_vol(V_REV))/cap:.1%})')
    for n in b:
        r = b[n]['res']
        print(f'  {n:11s} w {CW[n]:.2f}: MVC {b[n]["vm"]:7,.0f} | NNC {b[n]["vn"]:8,.0f} | ' + ' '.join(f'{k} {np.mean([r[(k, p)]["ps"] for p in PATHS]):7,.0f}' for k in SCN))
    out['tl_cap'] = dict(price=0.91 * cap, cost=ctl, margin=1 - ctl / (0.91 * cap))
    # cau noi tam r7 -> r8
    o = {}
    o['r7_lap_lai (ADMIN 0,5 vv, khong dinh phi)'] = EV8({'tl_fix': 'none'}, admin='perm05')
    o['+ ADMIN tre 1 nam (V_NNC r5)'] = EV8({'tl_fix': 'none'})
    o['+ dinh phi Tan Lap chi o ADMIN/CYC (cach skeptic)'] = EV8({'tl_fix': 'stress'})
    o['+ dinh phi Tan Lap doi xung moi kich ban (tam r8)'] = vm
    out['bridge'] = o
    print('  Cau noi: ' + ' -> '.join(f'{k} {v:,.0f}' for k, v in o.items()))
    out['tl_margin_axis'] = {}
    for tm in TLMs:
        x, y, bb = EV8({'tl_m': tm}, detail=True)
        out['tl_margin_axis'][str(tm)] = dict(V_MVC=x, V_NNC=y, CYC=bb['CYCLICAL']['vm'], ADMIN=bb['ADMIN_GATED']['vm'])
        print(f'  bien chu ky Tan Lap {str(tm):4s}: tam {x:7,.0f} ({x-vm:+6,.0f}) | ADMIN {bb["ADMIN_GATED"]["vm"]:7,.0f} | CYC {bb["CYCLICAL"]["vm"]:7,.0f}')
    out['admin_axis'] = {am: EV8(admin=am) for am in AMs}
    print('  anh xa ADMIN: ' + ' | '.join(f'{k} {v:,.0f}' for k, v in out['admin_axis'].items()))
    bp = {}
    for n in CW:
        for p in PATHS:
            x = branch(n, {'PW': {p: 1.0}}); bp[f'{n}|{p}'] = dict(V_MVC=x['vm'], V_NNC=x['vn'])
    out['branch_path'] = bp
    keys = ['A', 'B', 'BOT', 'gach_xang', 'dat_o', 'LK_nho_ICD', 'Q4', 'NETFIN', 'Dm', 'stake', 'VM']
    br = {kk: sum(CW[n] * W0[k] * PW0[p] * b[n]['res'][(k, p)][kk] for n in CW for k in SCN for p in PATHS) for kk in keys}
    brc = {kk: sum(W0[k] * PW0[p] * b['CYCLICAL']['res'][(k, p)][kk] for k in SCN for p in PATHS) for kk in keys}
    out['bridge_ty'] = br; out['bridge_cyc_ty'] = brc
    print('\n=== 2. CAU NOI KY VONG (ty; d/cp = x10) ===\n  ' + ' | '.join(f'{kk} {v:,.1f}' for kk, v in br.items()))
    print('  nhanh CYCLICAL: ' + ' | '.join(f'{kk} {v:,.1f}' for kk, v in brc.items()))

    print('\n=== 3. Gordon nhat quan anh xa (ADMIN = CYC o nam dien hinh) + phan ra DCF-CYC vs Gordon-CYC ===')
    roe_avg = float(np.mean(list(S.ROE_MVC.values())))
    st = {'STRUCTURAL': S.ROE_NOW, 'ADMIN_GATED': roe_avg, 'CYCLICAL': roe_avg}
    gor = {n: dict(roe=x, ps=(x - .03) / .10 * S.BVPS) for n, x in st.items()}
    rw = sum(CW[n] * st[n] for n in CW); gor['tron'] = dict(roe=rw, ps=(rw - .03) / .10 * S.BVPS)
    for n, d in gor.items(): print(f'  {n:11s}: ROE {d["roe"]:5.1%} -> {d["ps"]:7,.0f}')
    cyc = b['CYCLICAL']['vm']; book_like = brc['B'] + brc['dat_o'] + brc['LK_nho_ICD'] + brc['Q4'] + brc['NETFIN']
    ops = brc['A'] + brc['BOT'] + brc['gach_xang']
    dec = dict(DCF_CYC=cyc, stake_NNC_ps=brc['stake'] * 10, book_like_ps=book_like * 10, ops_TanLap_BOT_gach_ps=ops * 10,
               gordon_cyc=gor['CYCLICAL']['ps'], roe_implied_dcf_cyc=.03 + cyc / S.BVPS * .10)
    # ROE "khong gom NNC": gia tri ops + so sach vs von chu tru gia tri so sach co phan NNC (uoc luong: von chu tru phan NNC theo so sach ~ BVPS)
    out['gordon'] = gor; out['dcf_vs_gordon_cyc'] = dec
    print(f'  DCF-CYC {cyc:,.0f} = 44,07% NNC {brc["stake"]*10:,.0f} + so sach/NPV0 (mo moi, dat, LK, Q4, tai chinh rong) {book_like*10:,.0f} + van hanh '
          f'(Tan Lap+BOT+gach) {ops*10:,.0f} d/cp ; Gordon-CYC (ROE TB 2017-25 {roe_avg:.1%}) {gor["CYCLICAL"]["ps"]:,.0f} ; ROE ham y DCF-CYC {dec["roe_implied_dcf_cyc"]:.1%}')
    print(f'  ROE ben ham y cua TAM {vm:,.0f}: {.03 + vm / S.BVPS * .10:.1%}')

    print('\n=== 4. Lo trinh no rong (uoc luong; lai suat GIA DINH 7%; NOPAT - lai sau thue; chua tinh KH/von luu dong) ===')
    dp = {f'{tm}|{rt}': debt_path(tm, rt) for tm in ('nnc', 0.25) for rt in (0.07, 0.045)}
    out['debt'] = dp; d0 = dp['nnc|0.07']
    print(f'  cuoi 2026 {d0["end2026"]:,.0f} | 2027 {d0["end2027"]:,.0f} (lai {d0["int2027"]:.0f}) | 2028 ky vong {d0["end2028_exp"]:,.0f} (' +
          ', '.join(f'{n} {d0[n]["end2028"]:,.0f}: NOPAT {d0[n]["op28"]:.0f} vs lai {d0[n]["int2028"]:.0f}' for n in CW) + ')')
    for kk, d in dp.items(): print(f'  [{kk}] 2028 ky vong {d["end2028_exp"]:,.0f} ; CYC {d["CYCLICAL"]["end2028"]:,.0f} ; lai 2027+2028 {d["int_cum_2027_28_exp"]:.0f}')
    print(f'  Nguong canh bao: no rong 2027 > {d0["end2027"]+150:,.0f} ; 2028 > {d0["end2028_exp"]+150:,.0f} ; HOAC lai vay 4 quy > 50% LN gop da 4 quy')

    print('\n=== 5. Luoi 118.098 bo ===')
    args = list(itertools.product((0.11, 0.13, 0.15), (0.85, 1.0, 1.15), (0.88, 0.91, 0.95), range(3), range(3), range(3), range(3), ('branch', '1.40'),
                                  (2035, 'W', 2045), AMs, TLMs))
    with Pool(8) as pool: grid = pool.map(_cell, args, chunksize=200)
    ge = np.array([x['ev'] for x in grid]); gp = {q: float(np.percentile(ge, q)) for q in (5, 10, 25, 50, 75, 90, 95)}
    gp['min'] = float(ge.min()); gp['max'] = float(ge.max())
    print(f'  N={len(ge)}: ' + ' '.join(f'P{q} {v:,.0f}' for q, v in gp.items()))
    sub = {}
    for key in ('admin', 'tl_m', 'CW', 'endA', 'cap'):
        for v in sorted(set(x[key] for x in grid), key=str):
            s_ = np.array([x['ev'] for x in grid if x[key] == v])
            sub[f'{key}={v}'] = dict(p10=float(np.percentile(s_, 10)), p50=float(np.median(s_)), p90=float(np.percentile(s_, 90)))
            print(f'   {key}={v}: P10 {np.percentile(s_,10):,.0f} P50 {np.median(s_):,.0f} P90 {np.percentile(s_,90):,.0f}')
    out['grid_pct'] = gp; out['grid_n'] = len(ge); out['grid_sub'] = sub
    with open('grid_r8.csv', 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(grid[0])); wr.writeheader(); wr.writerows(grid)
    print('NGUONG (dang ky truoc): RE <= {:,.0f} | RE CO DIEU KIEN {:,.0f}-{:,.0f} | HOP LY {:,.0f}-{:,.0f} | NGHIENG DAT {:,.0f}-{:,.0f} | DAT >= {:,.0f}'.format(
        gp[10], gp[10], gp[25], gp[25], gp[75], gp[75], gp[90], gp[90]))

    print('\n=== 6. Do nhay (so voi tam r8) ===')
    tor = {}
    def T(lab, over=None, **kw):
        x = EV8(over, **kw); tor[lab] = x - vm; print(f'  {lab:84s} {x:8,.0f} ({x - vm:+7,.0f})')
    T('bien chu ky Tan Lap 25% (CHUA KIEM)', {'tl_m': 0.25}); T('bien chu ky Tan Lap 30% (CHUA KIEM)', {'tl_m': 0.30})
    T('anh xa ADMIN 0,5 vinh vien', admin='perm05'); T('anh xa ADMIN 1,0 tu 2028', admin='full')
    T('tran chu ky SL 1,40 (236,1k)', cap_basis='1.40')
    T('trong so nghieng STRUCTURAL 40/35/25', cw=CWs[1]); T('trong so nghieng CYCLICAL 15/35/50', cw=CWs[2])
    T('chi CYCLICAL', cw={'CYCLICAL': 1.0}); T('chi STRUCTURAL', cw={'STRUCTURAL': 1.0})
    T('SL nam thuong 1,05', v_rev=(1.05, 1.05)); T('SL nam thuong 1,20/1,30', v_rev=(1.20, 1.30))
    T('(+) upside doi thu het GP tu 2034', {'up2034': True})
    T('han GP Tan Lap 2035', {'endA': 2035}); T('han GP Tan Lap 2045', {'endA': 2045})
    T('chi phi Tan Lap +15%', {'ca': 1.15}); T('chi phi Tan Lap -15%', {'ca': 0.85}); T('REL 0,88', {'REL': 0.88}); T('REL 0,95', {'REL': 0.95})
    T('r 11%', {'r': 0.11}); T('r 15%', {'r': 0.15}); T('PW g2031 70/real 30', {'PW': PWs[0]}); T('PW g2031 30/real 70', {'PW': PWs[2]})
    T('STRESS duong gia danh nghia phang 100%', {'PW': {'flat': 1.0}})
    T('mo moi: hai phia co trong so (upside + NPV gia xau)', {'up': True, 'mine_xau': True}); T('mo moi: bo rui ro tre GP', {'delay': False})
    T('holding 15%', {'hold': 0.15}); T('holding 30%', {'hold': 0.30})
    x1 = EV8({'VN_fix': 50000}); x2 = EV8({'VN_fix': 60000}); out['vnnc_slope_per10k'] = x2 - x1
    print(f'  do doc: MVC {x2-x1:+,.0f} d/cp moi +10.000 d/cp V_NNC')
    out['tornado'] = tor
    with open('model_r8_out.json', 'w') as fh: json.dump(out, fh, ensure_ascii=False, indent=1, default=float)
