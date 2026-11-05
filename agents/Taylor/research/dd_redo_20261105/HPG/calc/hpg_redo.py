"""DD REDO HPG 05/11/2026 (job Taylor_20261105_014125). Chay: $DNA_PYEXE -I hpg_redo.py > hpg_redo_out.txt
Khung hien hanh: r = 13,5% (Ke noi dia) gan lai huy dong 12T hieu dung (deposit_rate_vn), beta=1 (ban cu: Ke 11,83% = rf 6,75% + beta do 0,915 x ERP 5,55%).
Tam = ky vong RI thuan (ban cu: 2/3 RI + 1/3 EV/EBITDA 5x -> nay chi doi chieu). CK thanh khoan: _common_014125/common.py.
Du an dang/sap dau tu (XDCB 16.113, cam ket ~19.472, DQ2 con lai): RI dung BV0 theo gia so + capex tuong lai khong tru => NPV 0 ngam dinh (luat 03/11).
DAU VAO BCTC goc [HN-Q3] + duong LN kich ban: chep tu dd_HPG_20261031/calc/hpg_valuation_v2.py (v3, da qua skeptic CONFIRMED + GAPS/GAPS2)."""
import os, sys, json, csv
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014125'))
import common as C
import numpy as np

TK = 'HPG'
SH = 8442.96452; BV0 = 148795.5       # trieu cp luu hanh; VCSH me 30/09/2026 [HN-Q3]
PAYOUT, G = 0.20, 0.05
TAXF = 0.80 / 0.88                     # thue terminal 20% (het uu dai) vs ETR hien hanh ~12% [ban cu GAPS §2/§7]
SC = {  # LNST me Q4/26, 2027, 2028, 2029 (ty, uoc luong); g terminal; w  — giu nguyen ban v3 31/10
 'XAU':   dict(w=0.25, e=[5500, 16000, 15000, 16000], g=0.03),
 'TRUNG_LAP': dict(w=0.50, e=[7000, 26000, 26000, 27000], g=0.05),
 'TOT':   dict(w=0.25, e=[8000, 31000, 33000, 35000], g=0.05),
}
TLSH = 9915.0                          # co phan TLSH (duoi trai, KHONG vao base) [ban cu §6]
ND, PT_DH, MI, INV_LK = 59607.6, 3828.9, 772.9, 12664.1   # no rong, phai tra NB DH, CDKKS, lien ket [HN-Q3]

L = C.liquidity(TK, free_float=1 - 0.3546, ff_src='(uoc luong) 1 - nhom ong Tran Dinh Long ~35,46% [dd_HPG_20261031 REPORT §6]; NN 21,8%, room con 27,2% [WEB 24hmoney 30/10]')
PX, PXD = L['last_price'], L['last_date']
A = C.anchor_info(); R = A['r']
ROLL = (np.datetime64(PXD) - np.datetime64('2026-09-30')).astype(int) / 365   # gia tri tinh tai 30/09 -> day toi ngay gia


NPV0_TERMINAL = True   # luat 03/11: von tang them khong bi gia dinh pha gia tri => ROE_T < r thi RI terminal KHONG tang (g_RI = 0)


def ri(e, ke, g, mult=1.0, dg=0.0, bv0=BV0, npv0=None):
    npv0 = NPV0_TERMINAL if npv0 is None else npv0
    bv = bv0; pv = 0.0; t = 0.0; e = [x * mult for x in e]
    for i, ni in enumerate(e):
        dt = 0.25 if i == 0 else 1.0; t += dt
        pv += (ni - ke * dt * bv) / (1 + ke) ** t; bv += ni * (1 - PAYOUT)
    gg = g + dg; roeT = e[-1] * (1 + gg) * TAXF / bv
    g_ri = 0.0 if (npv0 and roeT < ke) else gg
    tv = (roeT - ke) * bv / (ke - g_ri) / (1 + ke) ** t
    return (bv0 + pv + tv) / SH * 1e3 * (1 + ke) ** ROLL, roeT, tv / (bv0 + pv + tv)


def W(ke, ws=None, **kw):
    ws = ws or [s['w'] for s in SC.values()]
    return sum(w * ri(s['e'], ke, s['g'], **kw)[0] for w, s in zip(ws, SC.values()))


bvps = BV0 / SH * 1e3
out = dict(ticker=TK, price=PX, price_date=PXD, r=R, anchor=A, bvps=bvps, pb=PX / bvps, roll_years=ROLL)
print(f"== HPG redo | gia {PX:,.0f} ({PXD}) | BVPS 30/09 {bvps:,.0f} | P/B {PX/bvps:.2f}x | r {R:.2%} (neo 13,5% @ {A['r_anchor']['rate']:.2%} {A['r_anchor']['source']})")
sv = {}
for n, s in SC.items():
    v, roeT, tvs = ri(s['e'], R, s['g']); sv[n] = v
    print(f"  {n} w={s['w']}: LN {s['e']} g {s['g']:.0%} -> RI {v:,.0f} d/cp (P/B {v/bvps:.2f}x; ROE terminal sau thue 20% {roeT:.1%}; TV {tvs:.0%})")
center_pre = W(R); out['scen'] = sv; out['center_pre'] = center_pre
print(f"  KY VONG truoc CK: {center_pre:,.0f}")
for lab, ws in (('w_len_015_050_035', (0.15, 0.50, 0.35)), ('w_xuong_035_050_015', (0.35, 0.50, 0.15))):
    out[lab] = W(R, ws); print(f"  do nhay trong so {lab}: {out[lab]:,.0f}")
out['tlsh_tail_50pct'] = -0.5 * TLSH / SH * 1e3
print(f"  Duoi trai TLSH (khong vao base): mat 50% khoan {TLSH:,.0f} = {out['tlsh_tail_50pct']:,.0f} d/cp")

sens = {}
for beta in (0.5, 1.0):
    for bp in (-100, -50, 50, 100):
        ke = C.r_now(beta=beta, shift=bp / 1e4); v = W(ke)
        sens[f'b{beta}_{bp:+d}bp'] = dict(r=ke, v=v, dv=v - center_pre, pct=v / center_pre - 1)
out['sens_r'] = sens
print("Do nhay r theo lai huy dong:")
for k, s in sens.items(): print(f"  {k}: r {s['r']:.2%} -> {s['v']:,.0f} ({s['dv']:+,.0f}; {s['pct']:+.1%})")

MULT = (0.80, 0.90, 1.00, 1.10, 1.20); DG = (-0.01, 0.0, 0.01)
cells = [(n, m, dg, ri(s['e'], R, s['g'], mult=m, dg=dg)[0], s['w'] / (len(MULT) * len(DG))) for n, s in SC.items() for m in MULT for dg in DG]
with open(os.path.join(HERE, 'grid_hpg.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['scen', 'ln_mult', 'dg', 'value_pre', 'weight']); w.writerows(cells)
grid_desc = ("Luoi co trong so n=45: kich ban XAU/TRUNG LAP/TOT (w 0,25/0,50/0,25) x he so duong LNST 2026Q4-2029 (~LN/tan) 0,8/0,9/1,0/1,1/1,2 "
             "x dich g terminal -1/0/+1 pp (deu); r co dinh 13,50%; RI, BV0 = VCSH me 30/09, ROE terminal suy ra nhat quan voi thue 20%; terminal: ROE_T < r => RI khong tang (von moi NPV 0). "
             "Ban SAU = nhan (1 - CK thanh khoan 5 ty, Y=1,0).")
S = C.summarize(TK, PXD, PX, center_pre, [c[3] for c in cells], [c[4] for c in cells], L, grid_desc)
print(f"Luoi n={S['grid_n']}: truoc CK P10 {S['p10_pre']:,} P50 {S['p50_pre']:,} P90 {S['p90_pre']:,}")
print(f"Thanh khoan: ADV trung vi 250 phien {L['adv_med']/1e9:,.1f} ty | sigma {L['sigma_d']:.2%} | CK @5 ty {L['d_label']:.3%} (1 ty {L['pos']['1']['disc']['Y1.0']:.3%}; 10 ty {L['pos']['10']['disc']['Y1.0']:.3%}) | phien thoat 5 ty @10/20% {L['pos']['5']['days']['p10']:.2f}/{L['pos']['5']['days']['p20']:.2f} | Amihud {L['amihud_med_per_bn']:.2e}")
print(f"SAU CK: tam {S['center_post_liq']:,} | P10 {S['p10_post']:,} P25 {S['p25_post']:,} P50 {S['p50_post']:,} P75 {S['p75_post']:,} P90 {S['p90_post']:,}")
print(f"Gia {PX:,.0f}: vs tam {S['px_vs_center_post']:+.1%} | vs P10 {S['px_vs_p10_post']:+.1%} | vs P90 {S['px_vs_p90_post']:+.1%} | NHAN {S['label']}")

# nguong: r de tam = gia ; ROE terminal ngam dinh o gia (trung lap)
lo, hi = 0.08, 0.20
for _ in range(60):
    m = (lo + hi) / 2
    if W(m) * (1 - L['d_label']) > PX: lo = m
    else: hi = m
out['r_implied_center_eq_px'] = m
print(f"r ma tam sau CK = gia: {m:.2%}")
# doi chieu EV/EBITDA (khong vao tam)
EB = {k: round(s['e'][1] / 0.88 + 7100 + 12300, -2) for k, s in SC.items()}
ev5 = sum(SC[k]['w'] * (5 * e - ND - PT_DH - MI + INV_LK) / SH * 1e3 for k, e in EB.items())
mcap = PX * SH / 1e3; ev = mcap + ND + PT_DH + MI - INV_LK
out['xcheck'] = dict(ev5=ev5, ev_ebitda_ttm=ev / 44235.3)
print(f"Doi chieu: EV/EBITDA 5x (2027 theo kich ban) {ev5:,.0f} d/cp; EV/EBITDA loi TTM hien tai {ev/44235.3:.2f}x")

es = [e for e in json.load(open(C.WC + '/mike/kb/dd_price_zones.json'))['entries'] if e.get('ticker') == TK]; e = es[-1]
ew = [x for x in es if x.get('center_kind') == 'expected_weighted']
zo = dict(low=e['zone_low'], center=e['center'], high=e['zone_high'], dd_date=e['dd_date'], center_kind=e.get('center_kind'),
          expected_weighted_old=ew[-1]['center'] if ew else None)
# cau noi: Ke cu 11,83% (khong roll) -> roll -> r 13,5%
ROLL_SAVE = ROLL
ke_old = 0.0675 + 0.915 * 0.0555
ROLL = 0.0; b0 = W(ke_old, npv0=False); ROLL = ROLL_SAVE; b1 = W(ke_old, npv0=False); b2 = W(R, npv0=False); b3 = W(ke_old)
out['center_pre_old_terminal_rule'] = b2
print(f"Cau noi: RI trong so cu {zo['expected_weighted_old']:,} (Ke {ke_old:.2%}, tai 30/09) | tai lap {b0:,.0f} -> day toi {PXD} {b1:,.0f} -> r 13,5% (terminal cu, g tren RI am) {b2:,.0f} ({b2-b1:+,.0f}) -> terminal NPV0 {center_pre:,.0f} ({center_pre-b2:+,.0f}) -> sau CK {S['center_post_liq']:,}")
print(f"  [doi chieu] terminal NPV0 o Ke cu {ke_old:.2%}: {b3:,.0f} (chi XAU doi vi ROE_T 7,9% < Ke cu)")
print(f"  vs tam cu (blend) {zo['center']:,}: {S['center_post_liq']/zo['center']-1:+.1%} ; vs RI cu {zo['expected_weighted_old']:,}: {S['center_post_liq']/zo['expected_weighted_old']-1:+.1%}")
out.update(summary_core=S, liq=L, zone_old=zo, bridge=dict(ri_old_repro=b0, rolled=b1, r135=center_pre, ke_old=ke_old))
json.dump(out, open(os.path.join(HERE, 'hpg_redo_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)

summ = dict(ticker=TK, asof_price_date=PXD, price=PX, r=R, r_anchor=dict(rate=A['r_anchor']['rate'], date=A['r_anchor']['date'], source=A['r_anchor']['source'],
            asof_rate=A['dep_asof']['rate'], rule='r = 13,5% + beta x (dep - dep_neo), beta = 1 (gia dinh)'),
            center_pre_liq=S['center_pre_liq'], center_post_liq=S['center_post_liq'], p10_post=S['p10_post'], p50_post=S['p50_post'], p90_post=S['p90_post'],
            p25_post=S['p25_post'], p75_post=S['p75_post'], p10_pre=S['p10_pre'], p50_pre=S['p50_pre'], p90_pre=S['p90_pre'], liq_disc_5ty=S['liq_disc_5ty'],
            px_vs_center_post=S['px_vs_center_post'], px_vs_p10_post=S['px_vs_p10_post'], px_vs_p90_post=S['px_vs_p90_post'],
            grid_desc=grid_desc, grid_n=S['grid_n'], label=S['label'], zone_old=zo, center_change_vs_old=S['center_post_liq'] / zo['center'] - 1,
            sens_r={k: dict(r=v['r'], value=round(v['v']), dv=round(v['dv']), pct=v['pct']) for k, v in sens.items()},
            r_implied_center_eq_px=m,
            change_reason=(f"LECH >10%: nguyen nhan chinh la r: Ke cu {ke_old:.2%} (rf chuan hoa 6,75% + beta do 0,915 x ERP 5,55%) -> r 13,5% theo luat 03/11 "
                           f"({b2-b1:+,.0f} d/cp neu giu terminal cu); terminal NPV0 (ROE_T < r => RI khong tang) {center_pre-b2:+,.0f}; bo chan EV/EBITDA 5x khoi tam (tam cu blend {zo['center']:,} vs RI cu {zo['expected_weighted_old']:,}); "
                           f"day gia tri 30/09 -> {PXD} {b1-b0:+,.0f}. Duong LN/kich ban giu nguyen v3 31/10 (khong co BCTC moi)."),
            warnings=["Quan tri/ben lien quan (WARNING nang): he Dai Quang Minh-TLSH 3 lop phoi nhiem (co phan TLSH 9.915, 26,55% BDS HP, lien danh BT); lai thoai von BDS 4.929 ty ben mua khong cong bo",
                      "Uu dai thue: thoi han khong cong bo; DQ2 chua co ket luan du an moi/mo rong (thue terminal 20% da dua vao)",
                      "Tien gui cam co 8.294 ty; AD HRC Trung Quoc dang ra soat (QD 1902)",
                      "Khong tim thay khoi to/xu phat 2025-26 (khong tim thay != sach)"],
            open_issues=["Luat r 13,5% dong nhat moi ma; beta do HPG 0,84-0,93 (ban cu) khong dung - neu ap beta vao r thi gia tri cao hon",
                         "EBITDA slide lech 361 ty chua giai thich", "Free float ~64,5% la uoc luong (chi tru nhom TDL)", "Chua quet tin moi 31/10-04/11/2026"])
json.dump(summ, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print('SUMMARY.json written')
