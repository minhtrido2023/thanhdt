"""PVT — VONG 2 (STANDARD_r2.md), job Taylor_20261105_020016. Import model.py vong 1 (SCN, MULTS, ROE_MID, EQ_PARENT, Q3_NP) — khong sua.
Doi so vong 1: (1) truc lai huy dong; (2) truc mua tau phan capex 2026 con lai (mua/khong) x NPV doi xung theo kich ban cuoc (-30/0/+30% [UL]) — vong 1 chi ghi 'NPV 0'
(Bobby muc 7: dồn mua truoc 31/12/2026 o dinh gia tau cu); (3) phan vi muc ket cuc wpct; (4) song song: neo ke hoach 5 nam (NQ HDQT 2026-2030, du lieu quan sat duoc)
va ROE bo lai tien gui (dieu 10)."""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import model as M1
import common_r2 as R2
C = R2.C
NCI = 0.196                                  # CDKKS 19,6% LNST HN 9T (DD 29/10 §2)
CAPEX_PLAN_2026 = 3445.0                     # DHDCD 2026: toi da 5 tau moi (mekongasean, DHDCD thuong nien 2026)
SHIP_BOUGHT_9T = 979.6                       # nguyen gia phuong tien van tai tang 9T [TM12]
CAPEX_LEFT = CAPEX_PLAN_2026 - SHIP_BOUGHT_9T
BUY = {'mua_phan_con_lai': dict(w=0.5, amt=CAPEX_LEFT), 'khong': dict(w=0.5, amt=0.0)}   # [UL]
SHIP_NPV = {'xau': -0.30, 'coso': 0.0, 'tot': 0.30}                                        # [UL] bien do; chieu xuong: Bobby muc 7
# Ke hoach 5 nam (NQ HDQT, mekongasean 26/05/2026): LNST HN 2026-30 6.500-7.000; 2026 uoc = 9T 1.581,8 x 4/3 [UL]
PLAN_TOTAL = 6750.0; NP26_EST = 1581.8 * 4 / 3
PLAN_PARENT_YR = (PLAN_TOTAL - NP26_EST) / 4 * (1 - NCI)
INT_AT = 251.0 * 4 / 3 * (1 - 0.20) * (1 - NCI)  # lai tien gui 9T 251 nam hoa, sau thue 20%, phan me — muc HIEN TAI (lich su chua co)


def value_ps(s, m, r, b, roe_mid=None, np27=None, npv_map=SHIP_NPV):
    c = M1.SCN[s]; roe = (M1.ROE_MID if roe_mid is None else roe_mid) * c['mid'] * m; g = M1.G
    reinv = 1 - g / max(roe, 1e-9)
    v = M1.Q3_NP / (1 + r) ** 0.125 + (c['np27'] if np27 is None else np27 * c['np27'] / M1.SCN['coso']['np27']) * reinv / (1 + r) ** 0.75
    v += roe * M1.EQ_PARENT * (1 + g) * reinv / (r - g) / (1 + r) ** 1.25
    v += npv_map[s] * BUY[b]['amt'] * (1 - NCI)
    return v * 1e9 / M1.SH


def grid(**kw):
    vals, wts = [], []
    for (s, sc), m, (r, rw, _), (b, bc) in itertools.product(M1.SCN.items(), M1.MULTS, R2.r_points(), BUY.items()):
        vals.append(value_ps(s, m, r, b, **kw)); wts.append(sc['w'] / len(M1.MULTS) * rw * bc['w'])
    return vals, wts


def mean(v, w):
    return sum(a * b for a, b in zip(v, w)) / sum(w)


if __name__ == '__main__':
    r0 = C.r_now(); vals, wts = grid()
    cp = value_ps('coso', 1.0, r0, 'khong')
    par = {}
    roe_plan = PLAN_PARENT_YR / M1.EQ_PARENT
    roe_ex = M1.ROE_MID - INT_AT / M1.EQ_PARENT
    for k, kw, desc in (('plan_anchor', dict(roe_mid=roe_plan, np27=PLAN_PARENT_YR), f'neo ke hoach 5 nam NQ HDQT: LN me/nam 2027-30 = {PLAN_PARENT_YR:.0f} ty, ROE giua chu ky {roe_plan:.2%}'),
                        ('roe_ex_interest', dict(roe_mid=roe_ex), f'ROE giua chu ky BO lai tien gui hien tai ({INT_AT:.0f} ty/nam phan me): {roe_ex:.2%}'),
                        ('ship_npv0', dict(npv_map={'xau': 0.0, 'coso': 0.0, 'tot': 0.0}), 'NPV tau moi = 0 o moi kich ban (nhu vong 1)')):
        v, w = grid(**kw); par[k] = dict(desc=desc, vals=v, wts=w, center_pre=mean(v, w))
    sens = {}
    for bp in (-100, -50, 50, 100):
        rr = C.r_now(shift=bp / 1e4); acc = 0.0
        for (s, sc), m, (b, bc) in itertools.product(M1.SCN.items(), M1.MULTS, BUY.items()):
            acc += value_ps(s, m, rr, b) * sc['w'] / 5 * bc['w']
        sens[f'beta1.0_{bp:+d}bp'] = round(acc)
    sc = {f'{s}|{b}': round(value_ps(s, 1.0, r0, b)) for s in M1.SCN for b in BUY}
    bvps = M1.EQ_PARENT * 1e9 / M1.SH
    gx = dict(roe_mid_incl_interest=M1.ROE_MID, roe_mid_ex_interest=roe_ex, gordon_pb_incl=(M1.ROE_MID - M1.G) / (r0 - M1.G), gordon_pb_ex=(roe_ex - M1.G) / (r0 - M1.G),
              gordon_ps_incl=bvps * (M1.ROE_MID - M1.G) / (r0 - M1.G), gordon_ps_ex=bvps * (roe_ex - M1.G) / (r0 - M1.G), bvps=bvps,
              note='PVT no rong (619) => lai tien gui va lai vay cung nam trong LN co dong; ban bo lai tien gui chi la kiem cheo, khong phai base')
    out = dict(ticker='PVT', r=r0, center_pre=mean(vals, wts), center_param_pre=cp, outcomes_vals=vals, outcomes_wts=wts,
               grid_desc=('ket cuc = kich ban LN me 2027 1.000/1.250/1.500 (0,35/0,45/0,20 [UL]; he so ROE theo kich ban 0,85/1,0/1,1 [UL]) x he so ROE giua chu ky 0,8..1,2 (deu; nen ROE_Trailing trung vi 2015-25 BQ) '
                          'x lai huy dong -50/0/+50bp (0,25/0,5/0,25 [UL]) x mua tau phan capex 2026 con lai 2.465 ty / khong (0,5/0,5 [UL]) voi NPV -30/0/+30% theo kich ban [UL]; n=90; '
                          'tham so trung tam = co so, m=1, Δr=0, khong mua'),
               axes_included=['LN 2027 / chu ky cuoc (hai chieu)', 'ROE giua chu ky (hai chieu)', 'lai huy dong (hai chieu)', 'mua tau o dinh (NPV doi xung theo cuoc)'],
               axes_excluded=[dict(axis='TT99 (ngung trich truoc sua chua lon) thien lech LN 2026', reason='do lon chua xac dinh tu text BCTC; nen ROE lich su 2015-25 khong bi anh huong, LN 2027 kich ban [UL] — WARNING'),
                              dict(axis='ke hoach 5 nam NQ HDQT (LN thap hon)', reason='muc tieu ban dieu hanh thuong than trong (2026: KH 1.200 HN vs 9T thuc 1.581,8); khong thay ROE lich su 11 nam — bao SONG SONG parallel.plan_anchor'),
                              dict(axis='phat hanh co phieu tai tro doi tau', reason='NQ 5 nam neu "phat hanh co phieu" la mot nguon von, chua co dot cu the — WARNING')],
               base_adjustments=[dict(item='khong tru no rong 619,3 (da nam trong LN sau lai vay va VCSH)', effect_dong_per_share=0, basis='dinh gia FCFE co dong me', source='BCDKT Q3/2026'),
                                 dict(item='tau moi NPV 0 tai tham so trung tam', effect_dong_per_share=0, basis='luat 03/11', source='DHDCD 2026')],
               parallel=par, r_sens_pre=dict(sens, base=round(mean(vals, wts))), scenarios_pre=sc, gordon_roe_xcheck=gx,
               center_vs_p50_note_model='Lech nho; NPV tau +-30% chi o nhanh xau/tot va nua ket cuc mua — khong co nhanh trong so nho quyet dinh rieng P10/P90.',
               free_float=0.49, free_float_src='1 - PVN 51% [TM22b]',
               new_data_obs=[f'NQ HDQT ke hoach 2026-2030 (mekongasean 26/05/2026; so/ngay NQ chua xac dinh): LNST HN 6.500-7.000 ty 5 nam, me 3.100-3.400 (cong ty me rieng), co tuc 5-10%/nam, nguon von gom phat hanh co phieu => dua vao SONG SONG plan_anchor (LN me/nam 2027-30 {PLAN_PARENT_YR:.0f} ty)',
                             'DHDCD 2026: capex toi da 5 tau moi 3.445 ty; 9T moi tang nguyen gia phuong tien 979,6 => con lai 2.465 ty — dua vao truc mua tau',
                             'WebSearch 05/11/2026 09:00 ICT: khong thay NQ mua tau cu the thang 10-11/2026, khong thay khoi to/xu phat'],
               warnings=['Thay TGD 2 lan trong 4 thang (Tran Ngoc Nguyen mien nhiem 01/07; Nguyen Thanh Binh tu 03/08/2026), ly do khong cong bo',
                         'Phai thu don vi PVN 1.144,7 ty (+130%); ben PVN 22,4% DT 9T (Q3 31,7%) — ben lien quan / von luu dong',
                         'TT99/2025 + TT43/2026: ngung trich truoc sua chua lon tu 01/01/2026 => bien 2026 thien lech tang, do lon chua xac dinh; "dieu chinh khac" LCTT 9T/25 155,7 ty chua giai thich',
                         'Y kien kiem toan 2025 / soat xet H1/2026: CHUA CO TRONG TAY (DD 29/10) — co ngoai tru/nhan manh hay khong: chua kiem',
                         'Phai thu cu lien quan Huynh Thi Huyen Nhu 73,1 ty da du phong 100%', 'Chu tich dang ky ban 200.000 cp roi khong ban (03-04/2026)',
                         'Capex/KH 0,52 => FCF hien tai cao hon muc ben; doi tau VN gia (~17,7 nam, Bobby)'],
               open_issues=['Y kien kiem toan 2025 / soat xet H1', 'Dinh luong TT99', 'TC/spot + dao han HD', 'So/ngay NQ ke hoach 5 nam', 'Room ngoai'],
               fear_buy_25='Khong phai case fear-buy: khong khung hoang, LN dang o dinh; PB 1,10 > trung vi lich su 0,91 => KHONG du dieu kien §2.5 (#4 san tai san, "day chua toi")',
               change_reason='Vong 2: truc r, truc mua tau o dinh (NPV doi xung), phan vi muc ket cuc; song song neo ke hoach 5 nam va ROE bo lai tien gui')
    json.dump(out, open(os.path.join(HERE, 'model_r2_out.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(dict(center_pre=round(out['center_pre']), cp=round(cp), n=len(vals), sc=sc, par={k: round(v['center_pre']) for k, v in par.items()},
                          plan_parent_yr=round(PLAN_PARENT_YR), roe_plan=round(roe_plan, 4), roe_ex=round(roe_ex, 4), roe_mid=round(M1.ROE_MID, 4),
                          gx={k: (round(v, 3) if isinstance(v, float) else v) for k, v in gx.items()}), ensure_ascii=False))
