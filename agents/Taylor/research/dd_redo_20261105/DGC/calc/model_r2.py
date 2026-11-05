"""DGC — VONG 2 (STANDARD_r2.md), job Taylor_20261105_020016. Dung lai hang so BCTC + EBIT kich ban cua model.py vong 1 (import, khong sua).
Chay: $DNA_PYEXE -I model_r2.py -> model_r2_out.json ; roi lock_r2.sh ; roi ../../_common_014127/compare_r2.py DGC.
Doi so vong 1 (theo phan bien NNC/DRI/MVC + ERRATA r10/r11 cua DGC):
 - Du phong moi truong thanh TRUC RIENG doi xung {mot lan / huu han 4 quy / lap vinh vien 100 ty/quy} (vong 1: chi Q4 trong kich ban xau => lech mot chieu vs truc mo lai khai truong).
 - Nghi Son thanh TRUC RIENG doi xung {-500 / 0 / +500 ty} quanh so sach (vong 1: -500 chi o kich ban xau).
 - Truc lai huy dong {-50/0/+50bp}. Phan vi o muc ket cuc (wpct).
 - Song song: (a) CO truc phap ly (haircut tien rong 3/9/29%, w r12 0,2/0,5/0,3), (b) khai truong dung vinh vien (w mo lai 0)."""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import model as M1          # vong 1: hang so BCTC, SCN e27/e28, ORE, MULTS, S_NP, S_EQ, T_NEAR, G, RONIC, T_TERM
import common_r2 as R2
C = R2.C

SCN = {k: dict(w=v['w'], e27=v['e27'], e28=v['e28']) for k, v in M1.SCN.items()}       # 0,3/0,5/0,2 [UL]
Q4_EX = (M1.EBIT_9T + M1.PROV) / 3            # EBIT loi quy truoc du phong (du phong tach thanh truc rieng)
PROV = {'mot_lan': dict(w=1 / 3, n=0), 'huu_han_4q': dict(w=1 / 3, n=4), 'vinh_vien': dict(w=1 / 3, n=None)}   # [UL] deu: 'chua phan dinh' (r12 §11)
PROV_Q = 100.0                                # ty/quy, = muc trich Q2, Q3/2026 (BCTC)
PROV_SHIELD = 0.0                             # [UL] than trong: TT48 khong cho tru khi trich; tru khi chi that — chua xac minh
NS = {'vuot_500': dict(w=0.25, adj=-500.0), 'so_sach': dict(w=0.50, adj=0.0), 'duoi_500': dict(w=0.25, adj=500.0)}   # [UL] w; bien do 500 = chenh 2.900 vs 2.400 (TBTCVN 17/09/2025)
LEGAL = {'thuan': dict(w=0.2, h=0.03), 'coso': dict(w=0.5, h=0.09), 'nghich': dict(w=0.3, h=0.29)}   # CHI ban song song (r12 HC_LEGAL, w r12)


def core(s, o, m, r):
    c = SCN[s]; u = M1.ORE[o]; reinv = 1 - M1.G / M1.RONIC; t = M1.T_NEAR
    v = Q4_EX * m * (1 - t) / (1 + r) ** 0.125
    v += c['e27'] * m * (1 - t) * reinv / (1 + r) ** 0.75
    v += (c['e28'] * m + u['up28']) * (1 - t) * reinv / (1 + r) ** 1.75
    v += (c['e28'] * m + u['up']) * (1 + M1.G) * (1 - M1.T_TERM) * reinv / (r - M1.G) / (1 + r) ** 2.25
    return v


def prov_pv(p, r):
    n = PROV[p]['n']; q = PROV_Q * (1 - PROV_SHIELD); rq = (1 + r) ** 0.25 - 1
    if n == 0:
        return 0.0
    if n is None:                                   # vinh vien tu Q4/2026 (t=0,125)
        return q / rq * (1 + r) ** (0.25 - 0.125)
    return sum(q / (1 + r) ** (0.125 + 0.25 * i) for i in range(n))


def value_ps(s, o, p, ns, m, r, legal_h=0.0):
    other = (M1.CASH_DEP - M1.DEBT) * (1 - legal_h) - M1.PROV - M1.FUND_KTPL + M1.NS_CIP + NS[ns]['adj']
    eq = (core(s, o, m, r) - prov_pv(p, r)) * (1 - M1.S_NP) + other * (1 - M1.S_EQ)
    return eq * 1e9 / M1.SH


def grid(ore=None, legal=False):
    vals, wts = [], []
    ores = M1.ORE if ore is None else {ore: dict(M1.ORE[ore], w=1.0)}
    lg = LEGAL if legal else {'none': dict(w=1.0, h=0.0)}
    for (s, sc), (o, oc), (p, pc), (n, nc), m, (r, rw, _), (l, lc) in itertools.product(
            SCN.items(), ores.items(), PROV.items(), NS.items(), M1.MULTS, R2.r_points(), lg.items()):
        vals.append(value_ps(s, o, p, n, m, r, lc['h'])); wts.append(sc['w'] * oc['w'] * pc['w'] * nc['w'] / len(M1.MULTS) * rw * lc['w'])
    return vals, wts


def mean(v, w):
    return sum(a * b for a, b in zip(v, w)) / sum(w)


if __name__ == '__main__':
    r0 = C.r_now()
    vals, wts = grid()
    cp = value_ps('coso', 'dung', 'huu_han_4q', 'so_sach', 1.0, r0)
    par = {}
    for k, kw, desc in (('legal_axis', dict(legal=True), 'CO truc phap ly: haircut tien rong 3/9/29% (w 0,2/0,5/0,3, r12) — loai khoi base theo luat user 02/11 (vu an chi WARNING)'),
                        ('ore_closed', dict(ore='dung'), 'khai truong dung vinh vien (w mo lai = 0)'),
                        ('ore_closed_legal', dict(ore='dung', legal=True), 'khai truong dung + CO truc phap ly (canh xau cua ca hai truc lien quan vu an)')):
        v, w = grid(**kw); par[k] = dict(desc=desc, vals=v, wts=w, center_pre=mean(v, w))
    # Phan vi do 1 nhanh nho quyet dinh?
    branch = {}
    for o in M1.ORE:
        v, w = grid(ore=o); branch[f'ore_{o}'] = round(mean(v, w))
    sens = {}
    for bp in (-100, -50, 50, 100):
        rr = C.r_now(shift=bp / 1e4)
        sens[f'beta1.0_{bp:+d}bp'] = round(sum(a * b for a, b in zip([value_ps(s, o, p, n, m, rr) for s, o, p, n, m in itertools.product(SCN, M1.ORE, PROV, NS, M1.MULTS)],
                                                                     [SCN[s]['w'] * M1.ORE[o]['w'] * PROV[p]['w'] * NS[n]['w'] / 5 for s, o, p, n, m in itertools.product(SCN, M1.ORE, PROV, NS, M1.MULTS)])))
    sc = {f'{s}|{o}|{p}': round(value_ps(s, o, p, 'so_sach', 1.0, r0)) for s in SCN for o in M1.ORE for p in PROV}
    prov_ps = {p: round(-prov_pv(p, r0) * (1 - M1.S_NP) * 1e9 / M1.SH) for p in PROV}
    # Gordon/ROE (dieu 10): 9T me 1.267,1 nam hoa; VCSH me 13.073,9; DT tai chinh 9T 576,1 (lai tien gui)
    np_ann, eq_me, fin_ann = 1267.1 * 4 / 3, 13073.9, 576.1 * 4 / 3 * (1 - M1.T_NEAR) * (1 - M1.S_NP)
    nc_me = (M1.CASH_DEP - M1.DEBT) * (1 - M1.S_EQ)
    roe_a = np_ann / eq_me; roe_b = (np_ann - fin_ann) / (eq_me - nc_me)
    g, rr = M1.G, r0
    gx = dict(roe_incl_interest=roe_a, gordon_incl_ps=eq_me * (roe_a - g) / (rr - g) * 1e9 / M1.SH,
              roe_ex_interest_on_op_equity=roe_b, gordon_ex_ps=(nc_me + (eq_me - nc_me) * (roe_b - g) / (rr - g)) * 1e9 / M1.SH,
              note='LN 9T/2026 nam hoa (day chu ky, khai truong dung, du phong 200) => kiem cheo muc san, khong phai uoc tinh')
    out = dict(ticker='DGC', r=r0, center_pre=mean(vals, wts), center_param_pre=cp, outcomes_vals=vals, outcomes_wts=wts,
               grid_desc=('ket cuc = kich ban EBIT (xau/co so/tot 0,3/0,5/0,2 [UL]) x khai truong (dung/mo lai 2028, 0,5/0,5 [UL]) x du phong moi truong '
                          '(mot lan/huu han 4 quy/lap vinh vien 100 ty/quy, 1/3 moi nhanh [UL], la chan thue 0 [UL]) x Nghi Son quanh so sach (-500/0/+500 ty, 0,25/0,5/0,25 [UL]) '
                          'x he so EBIT loi 0,8..1,2 (deu) x lai huy dong 12T -50/0/+50bp (0,25/0,5/0,25 [UL]); n=810; tham so trung tam = co so, khai truong dung, huu han 4 quy, NS so sach, m=1, Δr=0'),
               axes_included=['kich ban EBIT 2027-28', 'khai truong 25/19B (len)', 'du phong moi truong lap (xuong)', 'Nghi Son von 2.400 vs 2.900 (hai chieu)', 'he so EBIT loi (hai chieu)', 'lai huy dong (hai chieu)'],
               axes_excluded=[dict(axis='phap ly (phat/dinh chi/haircut tien rong)', reason='luat user 02/11: vu an chi WARNING, khong bake vao base; bao SONG SONG ban CO truc (parallel.legal_axis, ore_closed_legal)'),
                              dict(axis='NPV doc lap Nghi Son -3.245/+2.524/+6.781 d/cp (r11)', reason='dau vao [UL] (gia san pham, WC 15%) — ERRATA r11: chi la do nhay, khong uoc tinh')],
               base_adjustments=[dict(item='du phong phai tra 200 ty', effect_dong_per_share=round(-M1.PROV * (1 - M1.S_EQ) * 1e9 / M1.SH), basis='nghia vu da ghi so', source='BCTC HN Q3/2026 p06'),
                                 dict(item='quy khen thuong phuc loi 592,8', effect_dong_per_share=round(-M1.FUND_KTPL * (1 - M1.S_EQ) * 1e9 / M1.SH), basis='nghia vu da ghi so (ma 323)', source='BCTC HN Q3/2026 p06'),
                                 dict(item='Nghi Son XDCB 1.408,8 theo gia von (NPV 0)', effect_dong_per_share=round(M1.NS_CIP * (1 - M1.S_EQ) * 1e9 / M1.SH), basis='so sach; khong tru khoan nao o tham so trung tam', source='BCTC HN Q3/2026 note 11 p30')],
               prov_axis_ps=prov_ps, ore_branch_center_pre=branch,
               parallel=par, r_sens_pre=dict(sens, base=round(mean(vals, wts))), scenarios_pre=sc, gordon_roe_xcheck=gx,
               center_vs_p50_note_model=('Phan phoi tron cua 2 nhanh khai truong (tam dung ' + str(branch['ore_dung']) + ' / mo lai ' + str(branch['ore_molai']) +
                                         ' truoc CK, moi nhanh w 0,5): P90 do nhanh mo lai quyet dinh, P10 do nhanh dung + lap vinh vien.'),
               free_float=M1.__dict__.get('FF', 1 - (0.1838 + 0.0664 + 0.0597)), free_float_src='1 - co dong lon 30/09 (1 nguon bao chi)',
               new_data_obs=['Quet WebSearch 05/11/2026 09:00 ICT: khong thay tin khoi to/xu phat moi thang 10-11/2026 (ket qua moi nhat ~08/2026); quet tin 01-29/10 (legal_and_news_scan_20261029.md): khong co su kien moi',
                             'NQ HDQT 34 (15/10/2026) Nghi Son: them H3PO4/PCl3/PCl5, chay thu Q4/2026, thuong mai Q1/2027, NQ KHONG ghi von — giu truc -500/0/+500'],
               warnings=['Vu an moi truong/khai thac/ke toan: CT HDQT cu Dao Huu Huyen (18,38%) bi tam giam 17/03/2026; khoi to them TGD Luu Bach Dat, TV HDQT Nguyen Quoc Trung, PTGD Phung Trong Tu, GD mo KT25 Trinh Quoc Khanh (07/2026). Phap nhan: chua thay quyet dinh khoi to phap nhan (quet 29/10 + WebSearch 05/11). Dieu 76 BLHS cho phep truy cuu phap nhan voi toi 227/235',
                         'Y kien NGOAI TRU BCTC kiem toan 2025: 950,9 ty ton kho chua du bang chung + noi dung vu an (VietnamFinance 06/10/2026) — chua dong',
                         'HOSE han che giao dich (chi phien chieu) tu 26/05/2026 do cham nop BCTC kiem toan; canh bao tu 30/06; cat margin Q4/2026 — chua thay go',
                         'Du phong moi truong 200 ty (2 quy): mot lan hay lap CHUA phan dinh; TKV chi BVMT ~1.000+ ty/nam (tien le chi thuong xuyen co ton tai — ERRATA r11)',
                         'Du phong moi truong KHONG duoc tru thue khi trich (TT48/2019) — chi phi thue hieu dung co the cao hon',
                         'PAT (con): CT HDQT mien nhiem sau khoi to (28/07); TSB doi lanh dao 05-06/10',
                         'Tap trung vi the ZaloPay 10.000 cp'],
               open_issues=['Von Nghi Son 2.400/2.900 chua co van ban goc', 'Trong so mo lai khai truong va trong so du phong lap la [UL]', 'EBIT 2027-28 nen r12 chua cap nhat luu huynh/P4 sau 28/10', 'LCTT lech 48,23 ty', 'Room ngoai'],
               fear_buy_25='Thuoc nhom (a) scandal + (b)/(d); §2 tieu chi #2 (NN chi phoi >50%) KHONG dat (tu nhan) => KHONG du dieu kien sleeve fear-buy theo §2; ho so §6 cu (AMBIGUOUS) — khong danh gia lai o day',
               change_reason='Vong 2: tach du phong lap + Nghi Son thanh truc doi xung, them truc lai huy dong, phan vi muc ket cuc; bao song song truc phap ly')
    json.dump(out, open(os.path.join(HERE, 'model_r2_out.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: (round(v) if isinstance(v, float) else v) for k, v in dict(r=r0, center_pre=out['center_pre'], center_param_pre=cp, n=len(vals),
                      branch=branch, prov_ps=prov_ps, par={k: round(v['center_pre']) for k, v in par.items()}, gx=gx).items()}, ensure_ascii=False, default=str))
