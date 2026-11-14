"""DD PAT valuation rev2 — inputs locked in ../assumptions_PAT.md (mục rev2). Units: tỷ đồng; per share đ.
rev1 giữ ở ../rev1/. Chạy: python3 model_PAT.py"""
import csv, os, math
SH = 25.0
NETCASH = 1.25 + 558.07 - 67.22 - 76.69          # C3 (quỹ KTPL đã trừ số dư)
NWC = 53.0
FUND = 0.055                                     # rev2 #1: trích quỹ KTPL 5,1–6,0% LNST (20,71/343,21; 13,49/264,94)
# rev2 #2: EBT cơ sở = run-rate Q3/26, trừ riêng bước thuế XK 10->15% trên XK Q3
Q3_LNTT, Q3_DTTC, Q3_CPTC = 63.747, 11.371, 1.467
Q3_DT, Q3_DLC = 440.032, 376.29
EBT_Q3_RUN = 4 * (Q3_LNTT - (Q3_DTTC - Q3_CPTC))          # hoạt động, đã chịu thuế XK 10%
XK_Q3_ANN = 4 * (Q3_DT - Q3_DLC)                           # cận trên XK (DT − bán DLC)
XK_STEP = 0.05 * XK_Q3_ANN                                 # 10%->15% chỉ trên XK này
BASE0 = EBT_Q3_RUN - XK_STEP
EBT_OLD = 245.0
def tax(y): return 0.05 if y <= 2030 else (0.10 if y <= 2032 else 0.20)
def dcf(ebt_path, r=0.135, g=0.02, finite_end=None, fund=FUND):
    pv = 0.0
    for t in range(1, 60):
        y = 2026 + t
        fcfe = ebt_path(y) * (1 - tax(y)) * (1 - fund)
        if finite_end and y > finite_end:
            return pv + NWC / (1 + r) ** (t - 1)
        if y >= 2033 and not finite_end:
            return pv + fcfe / (r - g) / (1 + r) ** (t - 1)
        pv += fcfe / (1 + r) ** t
    return pv
def mk_base(b0): return lambda y: b0 * (1.02 ** max(0, y - 2030))
good = lambda y: 330.0 * (1.02 ** max(0, y - 2030))
bad = lambda y: 150.0 if y <= 2028 else 200.0
ps = lambda v: v / SH * 1000
W = (0.30, 0.50, 0.20)
def run(r=0.135, b0=None, fund=FUND, w=W):
    b0 = BASE0 if b0 is None else b0
    o = {}
    o['base'] = dcf(mk_base(b0), r, fund=fund) + NETCASH
    o['good'] = dcf(good, r, fund=fund) + NETCASH
    o['bad_gc'] = dcf(bad, r, fund=fund) + NETCASH
    o['bad_finite'] = dcf(bad, r, finite_end=2034, fund=fund) + NETCASH
    o['bad'] = 0.5 * o['bad_gc'] + 0.5 * o['bad_finite']
    o['weighted'] = w[0] * o['bad'] + w[1] * o['base'] + w[2] * o['good']
    return o
if __name__ == '__main__':
    rows = []; A = rows.append
    res = run()
    A(['meta', 'EBT_Q3_runrate_annual', round(EBT_Q3_RUN, 1), ''])
    A(['meta', 'XK_Q3_annual (DT - ban DLC, can tren)', round(XK_Q3_ANN, 1), ''])
    A(['meta', 'XK_tax_step_5pp', round(XK_STEP, 1), ''])
    A(['meta', 'EBT_base_rev2', round(BASE0, 1), ''])
    for k, v in res.items(): A(['scenario', k, round(v, 1), round(ps(v))])
    cen = res['weighted'] * 0.9
    A(['scenario', 'centre_after_liq10', round(cen, 1), round(ps(cen))])
    A(['zone', 'cheap<=0.85*centre', '', round(0.85 * ps(cen))])
    A(['zone', 'expensive>=1.15*centre', '', round(1.15 * ps(cen))])
    # độ nhạy so rev1 / EBT 245
    old = run(b0=EBT_OLD); A(['sens_245', 'weighted_FCFE_fund_EBT245', round(old['weighted'], 1), round(ps(old['weighted']))])
    A(['sens_245', 'centre_after_liq10_EBT245', round(old['weighted'] * .9, 1), round(ps(old['weighted'] * .9))])
    nf = run(b0=EBT_OLD, fund=0.0); A(['sens_245', 'rev1_replica_no_fund_EBT245', round(nf['weighted'], 1), round(ps(nf['weighted']))])
    nf2 = run(fund=0.0); A(['sens_fund', 'rev2_base_without_fund_haircut', round(nf2['weighted'], 1), round(ps(nf2['weighted']))])
    # V_ngan / V_dai
    r, g = 0.135, 0.02
    ni_norm = 287.7; roe = ni_norm / 708.45; reinv = min(max(g / roe, 0), 0.8)
    v_ngan = ni_norm * (1 - FUND) * (1 - reinv) * (1 + g) / (r - g)
    A(['two_base', 'V_ngan (x(1-5.5%))', round(v_ngan, 1), round(ps(v_ngan))])
    A(['two_base', 'V_dai(=DCF base)', round(res['base'], 1), round(ps(res['base']))])
    A(['two_base', 'D=|ln(Vn/Vd)|', round(abs(math.log(v_ngan / res['base'])), 3), ''])
    cfo3 = (463.96 + 370.75 + 284.60) / 3; capex3 = (0.83 + 8.06 + 0.36) / 3; da = 45.0; rev = 1842.0
    v_c4 = (cfo3 - min(capex3, da)) * (1 - reinv) * (1 + g) / (r - g)
    v_d2 = (cfo3 - 0.05 * rev) * (1 - reinv) * (1 + g) / (r - g)
    A(['two_base', 'V_C4 (theo doi, khong doi)', round(v_c4, 1), round(ps(v_c4))])
    A(['two_base', 'V_D2 (theo doi, 5% uoc luong)', round(v_d2, 1), round(ps(v_d2))])
    # r sens
    for beta in (1.0, 0.5):
        for bp in (-100, -50, 50, 100):
            rr = 0.135 + beta * bp / 10000; w_ = run(rr)['weighted']
            A(['r_sens', f'beta{beta}_{bp:+d}bp_r{rr:.4f}', round(w_, 1), round(ps(w_))])
    for d in (0.0, 0.05, 0.10, 0.20):
        w_ = res['weighted'] * (1 - d); A(['liq', f'disc{int(d*100)}%', round(w_, 1), round(ps(w_))])
    # moat NONE: fade 30% on base0
    none = dcf(lambda y: BASE0 * (1 - 0.3 * min(1, max(0, y - 2026) / 7))) + NETCASH
    wn = 0.3 * res['bad'] + 0.5 * none + 0.2 * res['good']
    A(['moat_sens', 'NONE fade -30% to 2033 (weighted, pre-liq)', round(wn, 1), round(ps(wn))])
    A(['moat_sens', 'NONE after liq10', round(wn * .9, 1), round(ps(wn * .9))])
    # 1 tỷ EBT/năm
    b1 = dcf(lambda y: mk_base(BASE0)(y) + 1.0) + NETCASH - res['base']
    A(['per_bn_EBT', 'base scenario, +1bn EBT/yr forever (d/cp)', round(b1, 3), round(ps(b1), 1)])
    A(['per_bn_EBT', 'centre effect if shift only base (x0.5 weight x0.9 liq)', '', round(ps(b1) * 0.5 * 0.9, 1)])
    A(['per_bn_EBT', 'centre effect if shift all scenarios (x0.9)', '', round(ps(b1) * 0.9, 1)])
    # mốc M2: hoãn thuế XK => +XK_STEP; M3: base xuống 160
    d2 = (dcf(mk_base(BASE0 + XK_STEP)) - dcf(mk_base(BASE0))); A(['M2', 'thue XK hoan: +step EBT, tam (x0.5x0.9) d/cp', round(d2, 1), round(ps(d2) * .45)])
    for b in (160, 150):
        w_ = run(b0=b)['weighted'] * .9; A(['M3', f'base EBT {b}: tam', round(w_, 1), round(ps(w_))])
    for b in (330,):
        w_ = run(b0=b)['weighted'] * .9; A(['M6', f'base EBT {b}: tam', round(w_, 1), round(ps(w_))])
    # M1 branches
    for name, w in (('M1_bad_0.50/0.35/0.15', (.5, .35, .15)), ('M1_mid_0.30/0.50/0.20', W), ('M1_good_0.20/0.45/0.35', (.2, .45, .35))):
        w_ = run(w=w)['weighted']; A(['M1', name + ' pre-liq', round(w_, 1), round(ps(w_))]); A(['M1', name + ' centre', round(w_ * .9, 1), round(ps(w_ * .9))])
    # net cash trừ 42,6 tỷ cầm cố Vietinbank
    nc = 42.6; w_ = (res['weighted'] - nc) * .9; A(['sens_pledge', 'net cash -42.6bn (centre)', round(w_, 1), round(ps(w_))])
    # operating sens
    A(['ebt_sens', 'P4 price +/-10% (~176 rev)', 176, f'{176/BASE0:.0%} EBT co so'])
    A(['ebt_sens', 'electricity +/-5% (~500/yr est)', 25, ''])
    A(['ebt_sens', 'XK tax step (Q3 mix / 9T26 ~650 / 2025 ~1738)', f'{XK_STEP:.1f} / 32 / 87', ''])
    A(['ebt_sens', 'volume -20% (~445 contribution est)', 89, ''])
    A(['meta', 'NETCASH_true', round(NETCASH, 1), round(ps(NETCASH))])
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'valuation_PAT.csv')
    with open(p, 'w', newline='') as f: csv.writer(f).writerows([['block', 'item', 'value_bn', 'per_share_vnd']] + rows)
    for x in rows: print(x)
