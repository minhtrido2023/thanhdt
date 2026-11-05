"""PVP — DD redo 05/11/2026 (job Taylor_20261105_014127). Mo hinh DUNG LAI theo khung skill hien hanh (SOTP dong tien).
Chay: $DNA_PYEXE -I model.py -> model_out.json/.txt ; md5 -> LOCK_md5.txt ; ../../_common_014127/compare.py PVP.
Nguon so BCTC: ../../../dd_PVP_20261029/ (src/bctc_q3_2026.pdf [Q3], bctc_banien_2026_kiemtoan.pdf [H1], agm2026_nq_bienban.pdf [AGM]); so chep tai calc.py cu (kem trang).
PVP lap BCTC rieng (khong co cty con/lien ket) [Q3 p8]. Don vi ty dong; moc 30/09/2026."""
import json, os, sys, itertools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../_common_014127')))
import common as C
SH = 103_702_452                                  # [Q3 p13]
CASH, HTM, DEBT_ST, DEBT_LT = 718.2, 1015.9, 134.9, 473.5   # [Q3 p3-5]
DIV_PAY = 109.5                                   # phai tra co tuc 30/9 (co tuc 2025 103,70 thanh toan 20/10 + ton cu) [Q3 p4, NQ 17]
DRYDOCK = 232.9                                   # du phong sua chua dinh ky (ngan han) [Q3]
QLDN_9T = 38.896                                  # [Q3 p6]
# FSO Dai Hung Queen: lich cam ket cho thue khong huy ngang (rieng FSO, gia moi den 31/12/2036) [H1 p34]
FSO_Y1, FSO_Y2_5, FSO_GT5 = 415.807, 542.908, 204.953
FSO_Q3 = 59.657                                   # DT FSO Q3 (da thu trong nam 1) [Q3 p13-14]
FSO_NBV, FSO_KH_9T = 1873.654 - 1484.578, 111.108 # nguyen gia - KH luy ke; KH 9T [Q3 p10]
FSO_RUN = FSO_Q3 * 4
FSO_Y1_EXCESS = FSO_Y1 - FSO_RUN                  # phan nam 1 vuot run-rate, KHONG hoa giai duoc (giai thich: chenh gia hoi to? chua kiem)
VT_EBITDA_9T = 292.9 + 54.468 + 73.716            # LN gop van tai 9T + KH Era + Pride [Q3 p10, p13-14]
SHIP_EXP_TY = 77.8 * 26.040                        # gia tri tau ky vong theo xac suat mua (DD cu §4: 0,50/0,35/0,15; 116/56,5/0 tr USD; VCB 26.040)
# --- Gia dinh (uoc luong) ---
SPREAD_FSO = 0.026     # (uoc luong) r_hop_dong = lai huy dong 12T hieu dung + 2,6pp rui ro doi tac PVTrans (VIS A) => 10,0% tai 04/11 (dong bang muc 10% DD cu)
CORP_YEARS = 10        # (uoc luong) chi phi cong ty tru trong 10 nam
TAX = 0.20
SCN = {'xau': dict(w=0.40, ebitda=300.0, ship_npv=-0.30, fso_excess=False),
       'coso': dict(w=0.45, ebitda=400.0, ship_npv=0.0, fso_excess=True),
       'tot': dict(w=0.15, ebitda=550.0, ship_npv=0.0, fso_excess=True)}
# EBITDA doi tau dau hien huu/nam (uoc luong; 9T/26 nam hoa = dinh). Trong so 0,40/0,45/0,15 tu doc mu Bobby (K3 0,15; CYCLICAL 0,55, P(BDTI<=3.500 30/09/27)=0,58).
# ship_npv: CO SO = NPV 0 (luat 03/11). XAU = -30% gia tri tau ky vong — CO SO DU LIEU: bao cao kha thi cua chinh PVP IRR du an 7,67% < nguong IRRmin 11% [AGM p43-44]
#   + du bao BDTI giam 41-61% toi 2027 (Bobby F1/F2, khoa truoc). fso_excess=False o XAU: 177 ty nam 1 khong thanh tien (khong hoa giai duoc trong BCTC).
LIVES = (4, 5, 6, 7, 8)   # tuoi doi con lai doi tau hien huu (nam; Apollo ~21 tuoi, Era/Pride con 4,7-5 nam KH) — bien luoi (uoc luong)


def r_fso(r):
    return r - C.R_ANCHOR + (C.dep(C.ANCHOR_DATE)[0] + SPREAD_FSO)   # dich chuyen cung lai huy dong


def fso_pv(rr, excess=True):
    flows = [(0.375, FSO_Y1 - FSO_Q3 - (0 if excess else FSO_Y1_EXCESS))]
    flows += [(0.75 + y + 0.5, FSO_Y2_5 / 4) for y in range(4)]
    flows += [(4.75 + y + 0.5, FSO_GT5 / 5.5 * (0.5 if y == 5 else 1.0)) for y in range(6)]
    dl, kh, v = FSO_NBV, FSO_KH_9T * 4 / 3, 0.0
    for t, rev in flows:
        d = min(dl, kh * (0.75 if t < 0.75 else 1.0)); dl -= d
        v += (rev * (1 - TAX) + d * TAX) / (1 + rr) ** t
    return v


def annuity(cf, n, r):
    return cf * (1 - (1 + r) ** -n) / r


def parts(s, n=6, r=None):
    r = C.r_now() if r is None else r; c = SCN[s]
    return dict(net_cash_after_div=CASH + HTM - DEBT_ST - DEBT_LT - DIV_PAY,
                fso=fso_pv(r_fso(r), c['fso_excess']),
                tankers=annuity(c['ebitda'] * (1 - TAX * 0.75), n, r),      # sau thue, la chan KH ~25% EBITDA (uoc luong)
                drydock=-DRYDOCK,
                corp=-annuity(QLDN_9T * 4 / 3 * (1 - TAX), CORP_YEARS, r),
                ships_new=c['ship_npv'] * SHIP_EXP_TY)


def value_ps(s, n=6, r=None):
    return sum(parts(s, n, r).values()) * 1e9 / SH


def expected(r=None):
    return sum(SCN[s]['w'] * value_ps(s, 6, r) for s in SCN)


if __name__ == '__main__':
    r0 = C.r_now(); vals, wts = [], []
    for s, n in itertools.product(SCN, LIVES):
        vals.append(value_ps(s, n)); wts.append(SCN[s]['w'] / len(LIVES))
    sens = {f'beta{b}_{bp:+d}bp': round(expected(C.r_now(beta=b, shift=bp / 1e4))) for b in (0.5, 1.0) for bp in (-100, -50, 50, 100)}
    sens['base'] = round(expected())
    sc = {s: round(value_ps(s)) for s in SCN}
    pp = {s: {k: round(v, 1) for k, v in parts(s).items()} for s in SCN}
    out = dict(ticker='PVP', r=r0, r_fso=r_fso(r0), center_pre=expected(), grid_vals=vals, grid_wts=wts,
               grid_desc='3 kich ban cuoc (xau/co so/tot, w 0,40/0,45/0,15; EBITDA doi tau 300/400/550) x tuoi doi con lai doi tau hien huu 5 diem 4-8 nam (deu); n=15; trong so o = w_kb/5',
               r_sens_pre=sens, scenarios_pre=sc, parts_by_scn=pp,
               aux=dict(vt_ebitda_9t=VT_EBITDA_9T, vt_ebitda_9t_annual=VT_EBITDA_9T * 4 / 3, fso_y1_excess=FSO_Y1_EXCESS, ship_exp_ty=SHIP_EXP_TY,
                        floor_pre_capex_ps=(CASH + HTM - DEBT_ST - DEBT_LT - DIV_PAY + fso_pv(r_fso(r0)) - DRYDOCK) * 1e9 / SH),
               free_float=1 - (0.6492 + 0.0666), free_float_src='1 - PVTrans 64,92% - Le Ngoc Anh 6,66% [H1 p28]',
               change_reason='Mua tau: co so NPV=0 (cu: -10% o co so, -30% xau; nay -30% chi o xau co co so du lieu); doi tau hien huu = DCF nien kim r 13,5% theo tuoi doi (cu: EV/EBITDA 3-4x); FSO chiet khau gan lai huy dong (10,0%); co tam ky vong (cu: dai PB trung vi - SOTP khong tam); co chiet khau thanh khoan',
               warnings=['Mua tau 116 tr USD (1,55x von hoa) da duyet DHDCD, chua ky; DHDCD bat thuong gia han 2 lan (<=30/11/2026), van kien chua cong bo',
                         'Ben lien quan 63,3% DT 6T (PVTrans, BSR); GD lien quan "theo thuc te phat sinh" khong tran (NQ 16/HDQT)',
                         'Doi GD/PGD 06-09/2026', 'Free float ~28%'],
               open_issues=['177 ty cam ket FSO nam 1 vuot run-rate chua hoa giai', 'Ty trong TC/chuyen/pool va dao han hop dong tau khong co trong BCTC', 'Tuoi tau chi tu bao chi', 'Room ngoai chua kiem', 'EBITDA doi tau theo kich ban la uoc luong'])
    json.dump(out, open('model_out.json', 'w'), indent=1, ensure_ascii=False)
    with open('model_out.txt', 'w') as f:
        print(f"r={r0:.4f} r_fso={r_fso(r0):.4f} center_pre={out['center_pre']:.0f}", file=f)
        for k in ('scenarios_pre', 'r_sens_pre', 'parts_by_scn', 'aux'):
            print(k, json.dumps(out[k]), file=f)
        print('grid wq pre:', json.dumps({k: round(v) for k, v in C.wq(vals, wts).items()}), file=f)
    print(open('model_out.txt').read())
