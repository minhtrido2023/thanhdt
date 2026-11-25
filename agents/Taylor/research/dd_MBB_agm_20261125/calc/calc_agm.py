"""MBB — đóng hạng mục KTPL (E17 #1) bằng số BCTC gốc. MÙ GIÁ (19.250 chỉ là tham số kỹ thuật của R2C.stats, như calc_adj.py).
Chạy: /home/trido/thanhdt/wc_venv/bin/python -I calc_agm.py /tmp/ddrestore_MBB/agents/Taylor/research/dd_redo_20261105 <worktree>
Nguồn số (đơn vị triệu đồng; ảnh trích ở ../src/img, md5 PDF ở ../src/pdf_md5.txt):
  HNQ3 = BCTC hợp nhất Q3/2026, TM 22.1 (tr.in 36, ảnh hn_p44.png); LCTT (ảnh q3hn_lctt.png)
  RQ3  = BCTC riêng Q3/2026, TM 21 (tr.in 32, cm_p40_n21.png), TM 22.1 (tr.in 33, cm_p41_n22.png)
  HN25 = BCTC hợp nhất KIỂM TOÁN 2025, TM 26.1 (tr.in 65-66, h25_p65.png / h25_p66.png)
  R25  = BCTC riêng KIỂM TOÁN 2025, TM 25.1 (tr.in 51, k25_p51.png / k25_p51b.png)
"""
import sys, os, io, json, runpy, contextlib, hashlib
ROOT = os.path.abspath(sys.argv[1]); WT = os.path.abspath(sys.argv[2]); HERE = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(ROOT, 'MBB/calc_r3/mbb_r3.py')) == 'f5ad8f9ed0b3761de289f918e17ba679'

# ---------- 1. Số gốc ----------
VDL_2025 = 80_549_999                      # HNQ3 22.1 dư đầu vốn điều lệ
# HNQ3 22.1 (hợp nhất, 9T/2026): LNCPP sử dụng; trích lập các quỹ thuộc VCSH (cột Trích lập/Tăng)
HN_LNCPP_USED = 28_462_814
HN_FUNDS_IN_EQ = {'du_tru_bs_VDL': 2_757_753, 'du_phong_TC': 2_463_901, 'quy_khac': 685_043}
VDL_INC = 20_137_500                       # VĐL +20.137.500 = CP thưởng 15% + quyền mua 10:1 (805,5 tr CP × 10.000)
SHARES_0, SHARES_1 = 8_054_999_909, 10_068_749_885   # HNQ3 22.3
STOCK_DIV = round(SHARES_0 * 0.15) * 1e4 / 1e6     # 15% CP ⇒ triệu đồng (mệnh giá 10.000)
RIGHTS = round(SHARES_0 / 10) * 1e4 / 1e6          # quyền mua 10:1 — tiền mặt cổ đông góp, KHÔNG từ LNCPP
CASH_DIV = VDL_2025 * 0.10                 # cổ tức tiền 10% (NQ ĐHĐCĐ 18/04/2026 — nguồn báo chí + MB news; khớp LCTT bên dưới)
LCTT_DIV_PAID = 8_557_134                  # HNQ3 LCTT: cổ tức trả cho cổ đông (gồm cổ tức trả cổ đông không kiểm soát)
HN_NCI_USED = 555_369                      # HNQ3 22.1 NCI cột Sử dụng/Giảm (trần cho phần cổ tức NCI)
LN_HN_2025_MB = 26_778_939                 # HN25 26.1 LN thuần 2025 thuộc MB
LN_HN_2024_MB = 22_633_757                 # HN25 26.1 (bảng 2024) LN thuần 2024 thuộc MB
KTPL_HN_2025 = 1_866_219                   # HN25 26.1 dòng "Trích quỹ khen thưởng và phúc lợi" năm 2025 (phần MB)
# riêng lẻ
R_LNCPP_USED = 28_338_847                  # RQ3 22.1
R_FUNDS_IN_EQ = {'du_phong_TC': 2_459_690, 'du_tru_bs_VDL': 2_732_989, 'quy_khac': 685_048}
R_KTPL_LIAB = (1_906_685, 3_335_476)       # RQ3 TM21 "Quỹ KTPL và Quỹ thưởng người lãnh đạo quản trị điều hành" 31/12/25 → 30/09/26
LN_R_2025, LN_R_2024 = 27_329_888, 22_195_364   # R25 25.1
KTPL_R_2025, KTPL_R_2024 = 1_775_629, 1_586_443 # R25 25.1 dòng trực tiếp (năm 2025 / năm 2024)

# ---------- 2. Kiểm cơ học ----------
assert abs(STOCK_DIV + RIGHTS - VDL_INC) < 1, (STOCK_DIV, RIGHTS)          # VĐL tăng = CP thưởng + quyền mua
assert abs((SHARES_1 - SHARES_0) - (round(SHARES_0 * 0.15) + round(SHARES_0 / 10))) <= 10  # lệch lẻ cổ phiếu do làm tròn
nci_div = LCTT_DIV_PAID - CASH_DIV
assert 0 < nci_div <= HN_NCI_USED, nci_div                                  # 8.557.134 − 8.055.000 ≤ NCI sử dụng
assert R_FUNDS_IN_EQ['du_tru_bs_VDL'] / LN_R_2025 - 0.10 < 1e-4                  # 10% LN riêng 2025
assert abs(R_FUNDS_IN_EQ['du_phong_TC'] / (LN_R_2025 - R_FUNDS_IN_EQ['du_tru_bs_VDL']) - 0.10) < 1e-4  # 10% phần còn lại
hn_res = HN_LNCPP_USED - STOCK_DIV - CASH_DIV - sum(HN_FUNDS_IN_EQ.values())
r_res = R_LNCPP_USED - STOCK_DIV - CASH_DIV - sum(R_FUNDS_IN_EQ.values())
assert r_res >= R_KTPL_LIAB[1] - R_KTPL_LIAB[0], (r_res,)                   # trích ≥ tăng thuần số dư quỹ (đã chi một phần)
k = dict(
  HN_2026=hn_res / LN_HN_2025_MB, HN_2025=KTPL_HN_2025 / LN_HN_2024_MB,
  R_2026=r_res / LN_R_2025, R_2025=KTPL_R_2025 / LN_R_2024)
facts = dict(stock_div=STOCK_DIV, rights=RIGHTS, cash_div=CASH_DIV, nci_div_in_lctt=nci_div,
             hn_residual_2026=round(hn_res), r_residual_2026=round(r_res), ktpl_r_2024=KTPL_R_2024,
             r_ktpl_liab_net_inc=R_KTPL_LIAB[1] - R_KTPL_LIAB[0], k_pct={a: round(b * 100, 3) for a, b in k.items()})

# ---------- 3. Chạy lại RI r3 (cùng hàm của calc_adj.py) ----------
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(os.path.join(ROOT, 'MBB/calc_r3/mbb_r3.py'), run_name='__main__')
R2C, base, AXH, SH, PAYOUT, R, D, DAYS, TAX, NCI, BV = (g[x] for x in ('R2C', 'base', 'AXH', 'SH', 'PAYOUT', 'R', 'D', 'DAYS', 'TAX', 'NCI', 'BV'))
def ri(path, roeT, ke, bv0, k=0.0, prem=True):
    bv = bv0; pv = 0.0
    for i, r in enumerate(path, 1):
        pv += (r * (1 - k) - ke) * bv / (1 + ke) ** i; bv += r * bv * (1 - k - PAYOUT)
    rt = roeT * (1 - k) if prem else ke
    tv = (rt - ke) * bv / ke / (1 + ke) ** len(path)
    return (bv0 + pv + tv) / SH * 1e3 / (1 + ke) ** (DAYS / 365)
def center(k=0.0, dpath=(0, 0, 0), prem=True, r=R):
    def fn(scen, droe, mbv):
        b = base[scen]
        return ri([x + droe + dp for x, dp in zip(b['path'], dpath)], b['roeT'] + droe, r, b['bv26'] - mbv, k, prem)
    return R2C.stats(R2C.outcomes(AXH, fn), 19250.0, D)['center']
BVPS = BV / SH * 1e3
def combo(pk, mk, pr, pp, mppl):
    v = center(k=mk * pk, dpath=tuple(x * pr for x in (0.015, 0.01, 0.01)))
    return v * (1 - pp) + (v * SH + 200 * mppl * (1 - D)) / (SH + 200) * pp
c0 = center(); assert round(c0) == 21069, c0                                  # CONTROL 1: tâm base sổ
ctl = combo(.5, .0445, .35, .5, BVPS); assert round(ctl) == 20587, ctl         # CONTROL 2: tâm adj đợt 2
def pct(x): return round((x / c0 - 1) * 100, 3)
KP, KLO = k['HN_2026'], k['HN_2025']        # điểm = tỷ lệ năm gần nhất (hợp nhất, phần MB); thấp = năm trước
cases = {n: dict(center=round(center(k=v)), d_pct=pct(center(k=v))) for n, v in
         (('KT_2026_actual', KP), ('KT_2025_actual', KLO), ('KT_R_2026', k['R_2026']))}
# E17 mới: #1 bậc A p 0,90 [0,75;1,00]; #2, #3 giữ nguyên đợt 2
cc = combo(.90, KP, .35, .5, BVPS)
cands = [combo(pk, mk, pr, pp, mp) for pk in (.75, 1.0) for mk in (KLO, KP) for pr in (.15, .55) for pp in (.25, .75) for mp in (BVPS, 1.3 * BVPS)]
lin = .90 * cases['KT_2026_actual']['d_pct'] + .35 * 2.749 + .5 * -0.509
out = dict(facts=facts, control=dict(center_base=round(c0), center_adj_w2=round(ctl)), cases=cases,
           e17_new=dict(center_adj=round(cc), d_pct_vs_base=pct(cc), d_pct_vs_adj_w2=round((cc / ctl - 1) * 100, 3),
                        low=round(min(cands)), high=round(max(cands)), sum_lin_pct=round(lin, 3)))
# ---------- 4. rev6: KTPL vào TÂM BASE (dữ kiện A, 3 năm liền 8,0–9,0%) + E17 mới trên base rev6 ----------
def stats_k(kk):
    def fn(scen, droe, mbv):
        b = base[scen]
        return ri([x + droe for x in b['path']], b['roeT'] + droe, R, b['bv26'] - mbv, kk, True)
    return R2C.stats(R2C.outcomes(AXH, fn), 19250.0, D)
s0, s6 = stats_k(0.0), stats_k(KP)
assert (round(s0['p10']), round(s0['center']), round(s0['p90'])) == (14729, 21069, 27577), s0   # CONTROL vùng sổ rev5
c6 = s6['center']
def combo6(pr, pp, mppl, kk=KP):
    v = center(k=kk, dpath=tuple(x * pr for x in (0.015, 0.01, 0.01)))
    return v * (1 - pp) + (v * SH + 200 * mppl * (1 - D)) / (SH + 200) * pp
a6 = combo6(.35, .5, BVPS)
c6s = [combo6(pr, pp, mp, kk) for pr in (.15, .55) for pp in (.25, .75) for mp in (BVPS, 1.3 * BVPS) for kk in (KLO, KP)]
m2 = round((center(k=KP, dpath=(0.015, 0.01, 0.01)) / c6 - 1) * 100, 3)
m3 = round(((c6 * SH + 200 * BVPS * (1 - D)) / (SH + 200) / c6 - 1) * 100, 3)
out['rev6'] = dict(k_point_pct=round(KP * 100, 3), center=round(c6), zone_low=round(s6['p10']), zone_high=round(s6['p90']),
                   pct_below_19250=round(s6['pct_below_px'], 4), n=s6['n'], d_pct_vs_rev5=pct(c6),
                   k_low_center=round(center(k=KLO)), rule085=round(0.85 * c6),
                   adj=dict(center_adj=round(a6), d_pct_vs_rev6=round((a6 / c6 - 1) * 100, 3), low=round(min(c6s)), high=round(max(c6s)),
                            m_roepath_pct=m2, m_ppl_book_pct=m3))
print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open(os.path.join(HERE, 'calc_agm_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
