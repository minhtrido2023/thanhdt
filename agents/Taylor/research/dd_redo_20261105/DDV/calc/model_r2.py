"""DDV — VONG 2 (STANDARD_r2.md), job Taylor_20261105_020016. Import model.py vong 1 (hang so BCTC, SCN, MULTS, NPM_CYCLE) — khong sua.
Chay: $DNA_PYEXE -I model_r2.py ; lock_r2.sh DDV ... ; compare_r2.py DDV.
Doi so vong 1: (1) them Q4/2026 (vong 1 bo sot) thanh truc quanh LN loi Q3 THAT; (2) truc Liven 217 ty (co xac suat, khong vao base);
(3) truc lai huy dong; (4) phan vi muc ket cuc wpct; (5) song song: tien rong BCTC (khong chuan hoa VLD) va LN giua chu ky GOM lai tien gui."""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import model as M1
import common_r2 as R2
C = R2.C
Q3_CORE = 47.65 - 21.51 - 30.52           # LN gop - BH - QLDN Q3/2026 (BCTC) = -4,38 ty (truoc thue; lo => khong tinh la chan)
Q4 = {'xau': dict(w=0.25, np=-60.0), 'nhu_q3': dict(w=0.50, np=Q3_CORE), 'tot': dict(w=0.25, np=40.0)}   # [UL] bien do +-; tam = Q3 that
LIVEN = {'thu_du': dict(w=0.90, loss=0.0), 'mat': dict(w=0.10, loss=217.0)}                              # [UL] xac suat mat; LGD 100% [UL]


def value_ps(s, m, r, q4, lv, nc=None, incl_int=False):
    c = M1.SCN[s]; nc = M1.NC_NORM if nc is None else nc; g, ro = M1.G, M1.RONIC
    f27 = c['np27'] * ((1 - g / ro) if c['np27'] > 0 else 1.0)
    mid = M1.NPM_CYCLE * M1.REV_NORM - (0.0 if incl_int else M1.INT_AT_NORM)
    e_term = mid * c['mid'] * m * (1 + g) * (1 - g / ro)
    v = nc - LIVEN[lv]['loss'] + Q4[q4]['np'] / (1 + r) ** 0.125 + f27 / (1 + r) ** 0.75 + e_term / (r - g) / (1 + r) ** 1.25
    return v * 1e9 / M1.SH


def grid(**kw):
    vals, wts = [], []
    for (s, sc), m, (r, rw, _), (q, qc), (l, lc) in itertools.product(M1.SCN.items(), M1.MULTS, R2.r_points(), Q4.items(), LIVEN.items()):
        vals.append(value_ps(s, m, r, q, l, **kw)); wts.append(sc['w'] / len(M1.MULTS) * rw * qc['w'] * lc['w'])
    return vals, wts


def mean(v, w):
    return sum(a * b for a, b in zip(v, w)) / sum(w)


if __name__ == '__main__':
    r0 = C.r_now(); vals, wts = grid()
    cp = value_ps('coso', 1.0, r0, 'nhu_q3', 'thu_du')
    par = {}
    for k, kw, desc in (('nc_bctc', dict(nc=M1.NC_BCTC), 'tien rong BCTC 1.108 (KHONG chuan hoa von luu dong)'),
                        ('mid_incl_interest', dict(incl_int=True), 'LN giua chu ky GOM lai tien gui (dieu 10; tinh doi voi tien rong — chi kiem cheo)')):
        v, w = grid(**kw); par[k] = dict(desc=desc, vals=v, wts=w, center_pre=mean(v, w))
    sens = {}
    for bp in (-100, -50, 50, 100):
        rr = C.r_now(shift=bp / 1e4); acc = 0.0
        for (s, sc), m, (q, qc), (l, lc) in itertools.product(M1.SCN.items(), M1.MULTS, Q4.items(), LIVEN.items()):
            acc += value_ps(s, m, rr, q, l) * sc['w'] / 5 * qc['w'] * lc['w']
        sens[f'beta1.0_{bp:+d}bp'] = round(acc)
    sc = {s: round(value_ps(s, 1.0, r0, 'nhu_q3', 'thu_du')) for s in M1.SCN}
    branch = {s: round(mean(*grid_s)) for s, grid_s in ((s, ([v for v, (ss, *_) in zip(vals, itertools.product(M1.SCN, M1.MULTS, R2.r_points(), Q4, LIVEN)) if ss == s],
                                                              [w for w, (ss, *_) in zip(wts, itertools.product(M1.SCN, M1.MULTS, R2.r_points(), Q4, LIVEN)) if ss == s])) for s in M1.SCN)}
    eq_book = 217.0 / 0.098                    # VCSH suy tu 'Liven 217 = 9,8% VCSH' (BCTC Q3) — xap xi
    gx = dict(mid_np_excl_interest=M1.mid_np(), mid_np_incl_interest=M1.NPM_CYCLE * M1.REV_NORM, npm_cycle=M1.NPM_CYCLE,
              roe_cycle_excl=M1.mid_np() / (eq_book - M1.NC_NORM), roe_cycle_incl=M1.NPM_CYCLE * M1.REV_NORM / eq_book, eq_book_approx=eq_book,
              note='VCSH xap xi tu ty le Liven/VCSH 9,8%; ROE excl tinh tren VCSH tru tien rong chuan hoa')
    out = dict(ticker='DDV', r=r0, center_pre=mean(vals, wts), center_param_pre=cp, outcomes_vals=vals, outcomes_wts=wts,
               grid_desc=('ket cuc = kich ban duong S/DAP 2027 (xau/co so/tot 0,45/0,40/0,15 [UL, doc mu Bobby]; LN 2027 -185/+107/+373; he so giua chu ky 0,8/1,0/1,1 [UL]) '
                          'x he so LN giua chu ky 0,8..1,2 (deu) x lai huy dong -50/0/+50bp (0,25/0,5/0,25 [UL]) x LN loi Q4/2026 sau thue -60/-4,4(=Q3 that)/+40 ty (0,25/0,5/0,25 [UL]) '
                          'x phai thu Liven 217 ty thu du/mat 100% (0,9/0,1 [UL]); n=270; tham so trung tam = co so, m=1, Δr=0, Q4 nhu Q3, Liven thu du'),
               axes_included=['duong S/DAP 2027 (hai chieu)', 'LN giua chu ky (hai chieu)', 'lai huy dong (hai chieu)', 'LN loi Q4/2026 (hai chieu, quanh Q3 that; gom rui ro trich lap ton kho NVL 617)', 'Liven 217 (xuong — rui ro tin dung, khong co chieu len)'],
               axes_excluded=[dict(axis='giai doan bai thach cao / dinh chi Dinh Vu', reason='khong co du lieu bien do/xac suat; WARNING + HARD ABANDON #6'),
                              dict(axis='gia chuyen giao apatit (Vinachem)', reason='khong co du lieu gia chuyen giao; WARNING'),
                              dict(axis='von luu dong khong dao (tien rong BCTC)', reason='base chuan hoa VLD co co so BCTC; bao SONG SONG parallel.nc_bctc')],
               base_adjustments=[dict(item='chuan hoa von luu dong: tien rong 1.108 -> 869,1 (tru phai tra tang 449 - phai thu tang 210,1 trong Q3)',
                                      effect_dong_per_share=round(-(M1.NC_BCTC - M1.NC_NORM) * 1e9 / M1.SH),
                                      basis='DCF loi gia dinh VLD binh thuong; phan tai tro VLD bat thuong trong Q3 la tien phai tra (khong cua co dong)', source='BCTC Q3/2026 rieng (en_p1.txt), DD 26/10 §4'),
                                 dict(item='tru lai tien gui sau thue khoi LN giua chu ky (55,6 ty/nam)', effect_dong_per_share=None,
                                      basis='tranh tinh doi voi tien rong cong rieng', source='BCTC Q3 lai tien gui 22,15')],
               parallel=par, r_sens_pre=dict(sens, base=round(mean(vals, wts))), scenarios_pre=sc, branch_center_pre=branch, gordon_roe_xcheck=gx,
               center_vs_p50_note_model='Nhanh xau w 0,45 [UL] keo tam xuong; khong co nhanh trong so nho nao quyet dinh rieng P10/P90 (Liven mat w 0,1 chi day duoi P10 ~-1.485 d/cp).',
               free_float=M1.__dict__.get('FF', 0.36), free_float_src='1 - Vinachem 64,0% (BCTC Q3/2026)',
               new_data_obs=['WebSearch 05/11/2026 09:00 ICT: khong thay NQ HDQT/DHDCD moi hay tin xu phat/khoi to DDV (ket qua tra ve nham DVP — khong lien quan). DD 26/10: chua tra truc tiep UBCKNN/HNX'],
               warnings=['Vinachem 64%: gia chuyen giao apatit (Apatit Viet Nam, cung tap doan) — ben lien quan; thoai von chua thuc hien',
                         'Phai thu Liven Nutrients PTE 217 ty (9,8% VCSH) mot khach; khach tung tra truoc — chua thu tai 30/09',
                         'Phai tra 326,3 ty mot nha cung cap moi (Tuong Nguyen) — tap trung doi tac',
                         'Bai thach cao / moi truong Dinh Vu — nut that cong suat; nha may tung trong nhom 12 du an thua lo nganh Cong Thuong (lich su)',
                         '20/04/2026: 2 lanh dao tu nhiem cho Vinachem phan cong',
                         'Ton kho NVL 617,3 ty mua gia S cao, chua trich lap giam gia', 'UPCOM, free float 36%'],
               open_issues=['Duong S 2027 / do doc bien 2,44 (2 diem hieu chuan)', 'NH3 khong co chuoi BQ', 'VCSH dung xap xi trong kiem cheo ROE', 'Room ngoai', 'BCTC Q4/2026'],
               fear_buy_25='§2.5: NON (DD 26/10, giu 28/10 "NON nghieng xau di"): #3 leader chi phi YEU, #4 PB 1,17 > 1, "day chua toi" dinh => KHONG du dieu kien sleeve fear-buy',
               change_reason='Vong 2: them Q4/2026 (vong 1 bo sot), truc Liven co xac suat, truc r, phan vi muc ket cuc; bao song song tien rong BCTC + LN gom lai tien gui')
    json.dump(out, open(os.path.join(HERE, 'model_r2_out.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(dict(center_pre=round(out['center_pre']), cp=round(cp), n=len(vals), branch=branch, sc=sc, par={k: round(v['center_pre']) for k, v in par.items()},
                          gx={k: (round(v, 4) if isinstance(v, float) else v) for k, v in gx.items()}), ensure_ascii=False))
