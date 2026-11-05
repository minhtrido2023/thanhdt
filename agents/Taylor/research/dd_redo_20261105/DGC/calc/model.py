"""DGC — DD redo 05/11/2026 (job Taylor_20261105_014127). Mo hinh DUNG LAI theo khung skill due-diligence hien hanh.
Chay: $DNA_PYEXE -I model.py -> model_out.json / model_out.txt ; roi md5 -> LOCK_md5.txt TRUOC khi chay ../../_common_014127/compare.py DGC (doc gia/ADV).
Don vi: ty dong; dau ra d/cp. Moc gia tri 30/09/2026 (BCTC HN Q3/2026 goc, ../../../dgc_valuation_20261029_r12/MIKE_EXTRACT_BCTC_Q3_2026.md).
Gia tri me = loi x (1 - s_np) + (tien rong - nghia vu + Nghi Son so sach) x (1 - s_eq)."""
import json, os, sys, itertools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../_common_014127')))
import common as C

# --- BCTC HN Q3/2026 (do, nguon: MIKE_EXTRACT_BCTC_Q3_2026.md) ---
CASH_DEP = 9761.2            # tien 230,2 + HTM 9.531,0 (p05, note 4 p24)
DEBT = 1391.0                # vay ngan han (p06); khong co vay dai han
PROV = 200.0                 # du phong phai tra ngan han (p06) — nghia vu da ghi so, tru o moi kich ban
FUND_KTPL = 592.8            # quy khen thuong phuc loi (ma 323, p06)
NS_CIP = 1408.8              # XDCB Nghi Son (note 11 p30) — base NPV=0 => tai san theo gia von
EQ_TOT, EQ_NCI = 13474.6, 400.7          # VCSH, loi ich CDKKS (p06)
NP_9T, NP_NCI_9T = 1369.39, 102.29       # LNST HN 9T, phan CDKKS (r07)
LNTT_9T, TAX_9T = 1577.30, 205.55 + 2.36 # thue hien hanh + hoan lai (r07, dinh chinh 29/10)
GP_9T, SELL_9T, GA_9T = 1451.19, 242.77, 154.66
SH = 379_779_286                          # co phieu (p36)
S_NP = NP_NCI_9T / NP_9T                  # ty trong LN cua CDKKS (do 9T)
S_EQ = EQ_NCI / EQ_TOT                    # ty trong VCSH cua CDKKS (do 30/09)
T_NEAR = TAX_9T / LNTT_9T                 # thue hieu dung 9T (do)
EBIT_9T = GP_9T - SELL_9T - GA_9T         # EBIT loi 9T (da gom chi phi du phong 200 trong gia von)

# --- Gia dinh (uoc luong) ---
T_TERM = 0.15        # (uoc luong) thue dai han: uu dai du an het dan, giua 13,2% do 9T va 20% pho thong
G = 0.03             # (uoc luong) tang truong dai han danh nghia, <= GDP danh nghia
RONIC = 0.20         # (uoc luong) loi nhuan tren von moi; > r (do 30/09: NOPAT/von hoat dong ~40%, dung muc than trong)
# EBIT loi 2027/2028 theo kich ban: lay tu du bao dong co so r12 (../../../dgc_valuation_20261029_r12/out_A_forecast.csv, cot ebit_core;
# nen bien gop 14,5-19% nam 2027-28 do nguon quang/luu huynh), KHONG gom lai tien gui (tien rong cong rieng) va KHONG gom Nghi Son.
SCN = {'xau': dict(w=0.30, e27=671.0, e28=713.0, q4=(EBIT_9T) / 3, ns_adj=-500.0),
       'coso': dict(w=0.50, e27=1008.0, e28=1126.0, q4=(EBIT_9T + PROV) / 3, ns_adj=0.0),
       'tot': dict(w=0.20, e27=1375.0, e28=1538.0, q4=(EBIT_9T + PROV) / 3, ns_adj=0.0)}
# trong so 0,3/0,5/0,2 (uoc luong, giu thu tu r12: nghich 0,3 / co so 0,5 / thuan 0,2).
# q4: xau = du phong 100 ty/quy lap lai (EBIT 9T da tru 200); co so/tot = EBIT 9T truoc du phong (du phong 200 la nghia vu da ghi, tru o tien rong).
# ns_adj xau: von 2.900 vs 2.400 (Thoi bao Tai chinh VN 17/09/2025) => vuot du toan 500 ty — co so du lieu cu the; KHONG dua vao co so.
ORE = {'dung': dict(w=0.5, up28=0.0, up=0.0), 'molai': dict(w=0.5, up28=500.0, up=1000.0)}
# nguon quang: khai truong dung (hien trang) vs mo lai giua 2028 (+1.000 ty LN gop/nam, r12 CFG_B 'uplift khai truong 25/19B'); 0,5/0,5 (uoc luong, khong co co so phan dinh).
MULTS = (0.8, 0.9, 1.0, 1.1, 1.2)   # he so EBIT loi (uoc luong, +-20% ~ +-2pp bien gop tren DT ~9.300)


def core_value(s, o, m=1.0, r=None):
    r = C.r_now() if r is None else r; c = SCN[s]; u = ORE[o]
    reinv = 1 - G / RONIC
    q4 = c['q4'] * m * (1 - T_NEAR)                              # Q4/2026, t=0,125 nam
    f27 = (c['e27'] * m + u['up28'] * 0) * (1 - T_NEAR) * reinv    # 2027, giua nam t=0,75
    f28 = (c['e28'] * m + u['up28']) * (1 - T_NEAR) * reinv        # 2028, t=1,75
    e_term = (c['e28'] * m + u['up']) * (1 + G) * (1 - T_TERM) * reinv
    tv = e_term / (r - G)                                         # cuoi 2028, t=2,25
    return q4 / (1 + r) ** 0.125 + f27 / (1 + r) ** 0.75 + f28 / (1 + r) ** 1.75 + tv / (1 + r) ** 2.25


def value_ps(s, o, m=1.0, r=None):
    core = core_value(s, o, m, r)
    other = CASH_DEP - DEBT - PROV - FUND_KTPL + NS_CIP + SCN[s]['ns_adj']
    eq = core * (1 - S_NP) + other * (1 - S_EQ)
    return eq * 1e9 / SH


def expected(r=None):
    return sum(SCN[s]['w'] * ORE[o]['w'] * value_ps(s, o, 1.0, r) for s in SCN for o in ORE)


if __name__ == '__main__':
    r0 = C.r_now()
    vals, wts = [], []
    for s, o, m in itertools.product(SCN, ORE, MULTS):
        vals.append(value_ps(s, o, m)); wts.append(SCN[s]['w'] * ORE[o]['w'] / len(MULTS))
    sens = {}
    for b in (0.5, 1.0):
        for bp in (-100, -50, 50, 100):
            sens[f'beta{b}_{bp:+d}bp'] = round(expected(C.r_now(beta=b, shift=bp / 1e4)))
    sens['base'] = round(expected())
    sc = {f'{s}|{o}': round(value_ps(s, o)) for s in SCN for o in ORE}
    parts = dict(net_cash=CASH_DEP - DEBT, prov=PROV, fund_ktpl=FUND_KTPL, ns_book=NS_CIP, s_np=S_NP, s_eq=S_EQ, t_near=T_NEAR, ebit_9t=EBIT_9T,
                 core_coso_dung=core_value('coso', 'dung'), other_ps_coso=(CASH_DEP - DEBT - PROV - FUND_KTPL + NS_CIP) * (1 - S_EQ) * 1e9 / SH,
                 tv_share_coso_dung=None)
    rr = r0; c = SCN['coso']; reinv = 1 - G / RONIC
    tvpv = (c['e28']) * (1 + G) * (1 - T_TERM) * reinv / (rr - G) / (1 + rr) ** 2.25
    parts['tv_share_coso_dung'] = tvpv / core_value('coso', 'dung')
    gk = {}
    for g in (0.02, 0.03, 0.04):
        G_old = G; globals()['G'] = g
        gk[f'g{g:.0%}'] = {f'r{rv:.1%}': round(expected(rv)) for rv in (r0 - 0.01, r0, r0 + 0.01)}
        globals()['G'] = G_old
    ore_w = {}
    for wm in (0.0, 0.2, 0.5, 0.8):
        ore_w[f'w_molai{wm}'] = round(sum(SCN[s]['w'] * ((1 - wm) * value_ps(s, 'dung') + wm * value_ps(s, 'molai')) for s in SCN))
    out = dict(ticker='DGC', ore_weight_sens_pre=ore_w, r=r0, center_pre=expected(), grid_vals=vals, grid_wts=wts,
               grid_desc='3 kich ban (xau/co so/tot, w 0,3/0,5/0,2) x nguon quang 2 trang thai (dung/mo lai 2028, w 0,5/0,5) x he so EBIT loi 5 diem 0,8-1,2 (deu); n=30; trong so o = w_kb x w_quang / 5',
               r_sens_pre=sens, scenarios_pre=sc, parts=parts, g_x_r=gk,
               free_float=1 - (0.1838 + 0.0664 + 0.0597), free_float_src='1 - co dong lon 30/09 (Dao Huu Huyen 18,38%, Ngo Thi Ngoc Lan 6,64%, Dao Huu Kha 5,97%; 1 nguon bao chi, dgc_valuation_20261029_r12/REPORT)',
               change_reason='Ke 13,5% neo lai huy dong (cu 13%/12,5-13,5%); bo haircut phap ly tien rong 3-29% khoi co so (phap ly = WARNING); Nghi Son co so = so sach NPV=0 (cu: rong -447 d/cp); DCF loi Gordon (g 3%, RONIC 20%) thay P/E 6-8 tren LN loi; co trong so cho trang thai nguon quang (cu: A7/B7 khong chon); co chiet khau thanh khoan',
               warnings=['Phap ly: vu an moi truong/khai thac, Chu tich HDQT cu Dao Huu Huyen (18,38%) la 1 trong 14 bi can; khai truong dung — WARNING, khong loai, khong dinh luong trong co so',
                         'HOSE han che giao dich (chi phien chieu) — thanh khoan thap hon lich su',
                         'Du phong phai tra 200 ty: mot lan hay lap lai CHUA phan dinh (kich ban xau = lap lai 100 ty/quy)',
                         'Tap trung vi the ZaloPay (10.000 cp) — xem ho so cu'],
               open_issues=['Von Nghi Son 2.400 hay 2.900 ty chua co van ban goc', 'Ty trong nguon quang mo lai 0,5 la uoc luong', 'EBIT 2027-28 lay tu nen r12 (bien gop 14,5-19%), chua cap nhat gia luu huynh/P4 moi', 'LCTT 9T lech 48,23 ty trong ban goc'])
    json.dump(out, open('model_out.json', 'w'), indent=1, ensure_ascii=False)
    with open('model_out.txt', 'w') as f:
        print(f"r={r0:.4f} center_pre={out['center_pre']:.0f}", file=f)
        print('scenarios:', json.dumps(sc), file=f); print('r_sens:', json.dumps(sens), file=f); print('g x r:', json.dumps(gk), file=f)
        print('parts:', json.dumps(parts), file=f); print('ore_w:', json.dumps(ore_w), file=f)
        print('grid wq pre:', json.dumps({k: round(v) for k, v in C.wq(vals, wts).items()}), file=f)
    print(open('model_out.txt').read())
