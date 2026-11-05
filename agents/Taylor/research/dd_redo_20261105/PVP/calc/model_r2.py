"""PVP — VONG 2 (STANDARD_r2.md), job Taylor_20261105_020016. Import model.py vong 1 (hang so BCTC/FSO/annuity) — khong sua.
Doi so vong 1:
 (1) Gia tri tau ky vong (77,8 tr USD = ky vong theo xac suat mua) bi NEN o vong 1 => TACH thanh ket cuc: mua ca hai 116 / chi #2 56,5 / khong mua 0 (0,50/0,35/0,15 [UL], DD 29/10 §4).
 (2) NPV tau doi xung theo chu ky cuoc: xau -30% / co so 0 / tot +30% (vong 1: -30% chi o xau, khong co chieu len). Chieu xuong co co so du lieu
     (IRR du an 7,67% < IRRmin 11% [AGM p44]; Bobby BDTI -41..-61%); bien do +-30% [UL]. Song song: ban vong 1 (khong chieu len).
 (3) 177 ty FSO nam 1 chua hoa giai thanh TRUC RIENG (thanh tien / khong, 0,5/0,5 [UL]) — vong 1 gan cung kich ban xau.
 (4) Truc lai huy dong; phan vi muc ket cuc wpct."""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import model as M1
import common_r2 as R2
C = R2.C
VCB = 26.040                     # d/USD nghin (DD 29/10)
BUY = {'ca_hai': dict(w=0.50, usd=116.0), 'chi_2': dict(w=0.35, usd=56.5), 'khong': dict(w=0.15, usd=0.0)}   # [UL] DD 29/10 §4
SHIP_NPV = {'xau': -0.30, 'coso': 0.0, 'tot': 0.30}            # theo kich ban cuoc; bien do [UL]
SHIP_NPV_R1 = {'xau': -0.30, 'coso': 0.0, 'tot': 0.0}          # ban vong 1 (song song)
FSO_X = {'thanh_tien': dict(w=0.5, ok=True), 'khong': dict(w=0.5, ok=False)}                                   # [UL]


def value_ps(s, n, r, b, fx, npv_map=SHIP_NPV):
    c = M1.SCN[s]
    v = (M1.CASH + M1.HTM - M1.DEBT_ST - M1.DEBT_LT - M1.DIV_PAY + M1.fso_pv(M1.r_fso(r), FSO_X[fx]['ok'])
         + M1.annuity(c['ebitda'] * (1 - M1.TAX * 0.75), n, r) - M1.DRYDOCK - M1.annuity(M1.QLDN_9T * 4 / 3 * (1 - M1.TAX), M1.CORP_YEARS, r)
         + npv_map[s] * BUY[b]['usd'] * VCB)
    return v * 1e9 / M1.SH


def grid(npv_map=SHIP_NPV):
    vals, wts = [], []
    for (s, sc), n, (r, rw, _), (b, bc), (f, fc) in itertools.product(M1.SCN.items(), M1.LIVES, R2.r_points(), BUY.items(), FSO_X.items()):
        vals.append(value_ps(s, n, r, b, f, npv_map)); wts.append(sc['w'] / len(M1.LIVES) * rw * bc['w'] * fc['w'])
    return vals, wts


def mean(v, w):
    return sum(a * b for a, b in zip(v, w)) / sum(w)


def sub(vals, wts, keyidx, key):
    keys = list(itertools.product(M1.SCN, M1.LIVES, R2.R_AXIS, BUY, FSO_X))
    v = [x for x, k in zip(vals, keys) if k[keyidx] == key]; w = [x for x, k in zip(wts, keys) if k[keyidx] == key]
    return round(mean(v, w))


if __name__ == '__main__':
    r0 = C.r_now(); vals, wts = grid()
    cp = value_ps('coso', 6, r0, 'ca_hai', 'thanh_tien')
    v1, w1 = grid(SHIP_NPV_R1)
    par = dict(r1_ship_downside_only=dict(desc='NPV tau chi chieu xuong (xau -30%, co so/tot 0) nhu vong 1 — tach ket cuc mua', vals=v1, wts=w1, center_pre=mean(v1, w1)))
    sens = {}
    for bp in (-100, -50, 50, 100):
        rr = C.r_now(shift=bp / 1e4); acc = 0.0
        for (s, sc), n, (b, bc), (f, fc) in itertools.product(M1.SCN.items(), M1.LIVES, BUY.items(), FSO_X.items()):
            acc += value_ps(s, n, rr, b, f) * sc['w'] / 5 * bc['w'] * fc['w']
        sens[f'beta1.0_{bp:+d}bp'] = round(acc)
    branch = {f'scn_{s}': sub(vals, wts, 0, s) for s in M1.SCN}
    branch.update({f'buy_{b}': sub(vals, wts, 3, b) for b in BUY})
    sc = {f'{s}|{b}': round(value_ps(s, 6, r0, b, 'thanh_tien')) for s in M1.SCN for b in BUY}
    floor = (M1.CASH + M1.HTM - M1.DEBT_ST - M1.DEBT_LT - M1.DIV_PAY + M1.fso_pv(M1.r_fso(r0)) - M1.DRYDOCK) * 1e9 / M1.SH
    out = dict(ticker='PVP', r=r0, r_fso=M1.r_fso(r0), center_pre=mean(vals, wts), center_param_pre=cp, outcomes_vals=vals, outcomes_wts=wts,
               grid_desc=('ket cuc = kich ban cuoc (xau/co so/tot 0,40/0,45/0,15 [UL, Bobby]; EBITDA doi tau 300/400/550 [UL]; NPV tau moi -30%/0/+30% theo kich ban, bien do [UL]) '
                          'x tuoi doi con lai doi tau 4..8 nam (deu) x lai huy dong -50/0/+50bp (0,25/0,5/0,25 [UL]; FSO chiet khau dich cung) '
                          'x ket cuc mua tau ca hai 116 / chi #2 56,5 / khong 0 tr USD (0,50/0,35/0,15 [UL]) x 177 ty FSO nam 1 thanh tien/khong (0,5/0,5 [UL]); n=270; '
                          'tham so trung tam = co so, 6 nam, Δr=0, mua ca hai, FSO thanh tien'),
               axes_included=['chu ky cuoc (hai chieu) + NPV tau moi doi xung theo chu ky', 'tuoi doi doi tau (hai chieu)', 'lai huy dong (hai chieu)', 'ket cuc mua tau (tach ky vong)', '177 ty FSO nam 1 (xuong; vong 1 gan voi xau)'],
               axes_excluded=[dict(axis='phat hanh co phieu tai tro tau (pha loang)', reason='chua co van kien DHDCD bat thuong; khong co du lieu gia/so luong — WARNING + moc doi nhan dinh'),
                              dict(axis='NPV tau chi chieu xuong (ban vong 1)', reason='bao SONG SONG parallel.r1_ship_downside_only')],
               base_adjustments=[dict(item='phai tra co tuc 109,5 ty', effect_dong_per_share=round(-M1.DIV_PAY * 1e9 / M1.SH), basis='nghia vu da ghi so (tra 20/10)', source='[Q3 p4], NQ 17'),
                                 dict(item='du phong sua chua dinh ky 232,9', effect_dong_per_share=round(-M1.DRYDOCK * 1e9 / M1.SH), basis='nghia vu da ghi so', source='[Q3]'),
                                 dict(item='chi phi cong ty 10 nam', effect_dong_per_share=round(-M1.annuity(M1.QLDN_9T * 4 / 3 * (1 - M1.TAX), M1.CORP_YEARS, r0) * 1e9 / M1.SH),
                                      basis='QLDN 9T that nam hoa; 10 nam [UL]', source='[Q3 p6]'),
                                 dict(item='tau moi NPV 0 tai tham so trung tam', effect_dong_per_share=0, basis='luat 03/11', source='[AGM p21]')],
               parallel=par, r_sens_pre=dict(sens, base=round(mean(vals, wts))), scenarios_pre=sc, branch_center_pre=branch,
               aux=dict(floor_pre_capex_ps=floor, ship_value_if_both_ty=116.0 * VCB),
               gordon_roe_xcheck=dict(note='Khong ap dung: SOTP dong tien (tien rong + FSO hop dong + nien kim doi tau), khong dung Gordon/ROE; lai tien gui 9T 57,4 = 16,5% LNTT (DD 29/10) — nam trong tien rong cong rieng, khong tinh doi'),
               center_vs_p50_note_model=('Phan phoi 2 dinh theo kich ban cuoc (tam nhanh xau ' + str(branch['scn_xau']) + ' / co so ' + str(branch['scn_coso']) + ' / tot ' + str(branch['scn_tot']) +
                                         ' truoc CK): P10 do nhanh xau (w 0,40) + mua ca hai quyet dinh; P90 do nhanh tot (w 0,15) + mua ca hai — nhanh trong so nho.'),
               free_float=M1.__dict__.get('FF', 1 - (0.6492 + 0.0666)), free_float_src='1 - PVTrans 64,92% - Le Ngoc Anh 6,66% [H1 p28]',
               new_data_obs=['NQ 22/NQ-TBD-HDQT 02/10 + NQ 23/NQ-TBD-HDQT 23/10: gia han DHDCD bat thuong toi <=30/11/2026, ly do hoan thien van kien (DD 29/10 [CB]) — da phan anh: xac suat mua giu 0,50/0,35/0,15',
                             'WebSearch 05/11/2026 09:00 ICT: bai baophapluat 12/09/2026 (DKCC 28/09, du kien hop 23/10) — van kien chua cong bo; khong thay ket qua bieu quyet / hop dong mua tau'],
               warnings=['Mua tau 116 tr USD (~1,55x von hoa) da duyet DHDCD 23/06; DHDCD bat thuong gia han 2 lan (<=30/11/2026), van kien chua cong bo',
                         'IRR du an Aframax #2 7,67% < IRRmin 11% cong ty tu dat [AGM p44]; NPV von CSH duong chi nho don bay vay 70%',
                         'Ben lien quan 63,3% DT 6T (PVTrans, BSR, LPG VN); GD lien quan "theo thuc te phat sinh" khong tran (NQ 16/HDQT 18/08/2026)',
                         'Doi GD (23/06) va PGD (12/08); free float ~28%',
                         'Chua thay khoi to/dieu tra (DD 29/10 + WebSearch 05/11); kiem toan ban nien chap nhan toan phan'],
               open_issues=['177 ty cam ket FSO nam 1 chua hoa giai', 'Co cau TC/chuyen/pool, dao han HD tau', 'Tuoi tau chi tu bao chi', 'Van kien DHDCD bat thuong (gia, cau truc von, phat hanh?)', 'Room ngoai'],
               fear_buy_25='Khong phai case fear-buy: khong co khung hoang; PB/sàn tai san truoc capex ~14,9k < gia nhung luan diem la chu ky dinh cuoc (Bobby) => KHONG du dieu kien §2.5 (#1 "day chua toi": dang o dinh chu ky)',
               change_reason='Vong 2: tach ket cuc mua tau, NPV tau doi xung theo cuoc, truc FSO 177 rieng, truc r, phan vi muc ket cuc')
    json.dump(out, open(os.path.join(HERE, 'model_r2_out.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(dict(center_pre=round(out['center_pre']), cp=round(cp), n=len(vals), branch=branch, sc=sc, par=round(par['r1_ship_downside_only']['center_pre']), floor=round(floor)), ensure_ascii=False))
