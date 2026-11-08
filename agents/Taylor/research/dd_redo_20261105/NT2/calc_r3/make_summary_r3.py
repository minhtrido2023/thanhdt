"""SUMMARY.json vong 3 NT2 — doc model_r3_out.json + assumptions_r3.json + SUMMARY_r2.json (backup). Khong go tay so."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__)); TOP = os.path.dirname(HERE)
M = json.load(open(os.path.join(HERE, 'model_r3_out.json')))
A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
old = json.load(open(os.path.join(TOP, 'SUMMARY_r2.json')))
S, Q, PX = M['grid'], M['liq'], M['price']
r2c = old['center_post_liq']
c = S['center_post']
f = lambda x: f"{x:,.0f}".replace(',', '.')
pct = lambda x: f"{x*100:.1f}".replace('.', ',') + '%'
grid_desc = (f"4 truc, n={S['n']} ket cuc tat dinh (1 o = 1 ket cuc): LNST chuan hoa/nam {{450;625;800;975;1150}} ty (0,1/0,2/0,4/0,2/0,1) [UL; co so du lieu: "
             f"bien LNST 2015-25 x DT 7.137 = 728-742, 9T/26 829] x thoi han dong tien {{5;8;10;12;15}} nam (0,1/0,2/0,4/0,2/0,1) [UL; giam: khi can ~2030, PPA goc 2011-2020; "
             f"tang: GSA ~2035, PL13 2026-2039] x r {{R-1;R;R+1}}% (1/4-1/2-1/4), R={M['r']*100:.1f}% x FCF-LNST {{-150;0;+150}} ty/nam (1/4-1/2-1/4) [UL, doi xung]. "
             f"Net cash {f(M['net_cash'])} co dinh; NWC 837,2 chuan hoa theo DT 7.137/10.404 => {f(M['nwc_norm'])} thu hoi cuoi thoi han + {f(M['nwc_release'])} giai phong t=1. "
             f"Gia tri sau thoi han = 0. LNST van hanh = LNST - {M['fin_net_at']:.0f} thu nhap TC rong sau thue. Phan vi = _shared/wpct.py tren {S['n']} o; tam = ky vong trong so luoi; "
             f"CK thanh khoan 5 ty (ADV250) ap dong loat.")
ip = M['implied_by_price']
assumptions = [
    dict(item=f"r = {M['r']*100:.2f}%", basis=f"13,5% + 1,0 x (lai huy dong 12T hieu dung {M['dep']*100:.2f}% - 7,40%)", source=f"deposit_rate_vn.effective_deposit_rate('2026-11-06') = {M['dep_src']}"),
    dict(item=f"Gia tham chieu {f(PX)} (dong cua {M['price_date']})", basis="tav2_bq.ticker Price", source="calc_r3/px_nt2_r3.sql -> px_nt2_r3_20261106.csv"),
    dict(item="So BCTC 30/09/2026 (net cash, NWC, co tuc phai tra, thu nhap TC)", basis="giu nguyen r2", source="src/Q3_2026_hopnhat_va_giaitrinh.pdf; calc/model_r2.py"),
    dict(item="LNST chuan hoa tam 800 (5 muc 450-1150)", basis=A['np_basis'], source="calc_r3/fin_nt2_r3.csv"),
    dict(item="Thoi han 5/8/10/12/15 (.1/.2/.4/.2/.1)", basis=A['yrs_basis'], source="dd_blind_NT2_20261026/CYCLE_BLOCK.md muc C-D"),
    dict(item="NWC chuan hoa 574,3 + giai phong 262,9 t=1", basis=A['nwc_basis'] + ' ' + A['nwc_norm_rule'], source="calc_r3/ar_nt2_r3.csv; BCTC tr.2-3"),
    dict(item="Truc FCF-LNST +-150 (.25/.5/.25), base 0", basis=A['fcf_basis'], source="calc_r3/fin_nt2_r3.csv (CF_Invest_P0); CYCLE_BLOCK.md (khau hao H1/26)"),
    dict(item="Gia tri sau thoi han = 0", basis="dong tien co thoi han (PPA/GSA); khong thuong moat (NONE, ADDENDUM_5F)", source="ADDENDUM_5F.md §1"),
    dict(item="CK thanh khoan co 5 ty ADV250 (luat can bac hai, Y=1)", basis="quy uoc fleet; 5 ty = 28% ADV250, NGOAI vung hieu chinh", source="_common/liq.py"),
]
corrections = [
    dict(n=1, verdict="DUNG - AP", note=f"Luoi 5/8/10/12/15: tai lap tam 23.475 (skeptic 23.475), P10 18.088 (skeptic 18.088) o buoc 2 bridge. Nut 4 nam trong so 0,2: tam {f(M['parallel']['A_nut_4_nam_tr0.2 (skeptic)']['center_post'])} tren luoi r3 day du (skeptic 22.780 tren luoi r2 khong NWC chuan hoa) - bao song song, khong headline vi chieu tang PL13 2026-2039 cung co nguon. WARNING 2 nguon mau thuan han PPA ghi o warnings."),
    dict(n=2, verdict="DUNG VE HUONG, SUA THOI DIEM", note=f"Co so them: AR/DT TTM on dinh 37-49% (2022Q1-2026Q3, BQ AR_P0) => NWC ty le DT. Giai phong 262,9 o t=1 (khong phai t=0 nhu skeptic): +{f(M['bridge'][3]['delta'])} (skeptic +646 kem gop #1 => 24.111; r3 24.003, lech -108 do chiet khau 1 nam)."),
    dict(n=3, verdict="DUNG - AP", note=f"Gia 22.200 (06/11, BQ). Tren luoi r2: % duoi gia {pct(M['bridge'][1]['pct_below_px'])} (skeptic 32,5%), gia/tam -6,0%."),
    dict(n=4, verdict="DUNG MOT PHAN", note="Capex BQ 2,5 (9T/26)/1,2-10,6 ty/nam 2015-26 xac nhan. Nhung du lieu nghieng LEN: khau hao 115-153 > capex => FCF > LNST neu dai tu on dinh; chieu xuong (dai tu tien mat > phan bo, thay the cuoi vong doi) khong co lich su tra truoc 2015-25 trong BQ (CHUA KIEM). Dua truc doi xung +-150 vao luoi (tam khong doi, P10/P90 gian); bien the D (+110 base) chi la do nhay."),
    dict(n=5, verdict="DUNG - AP (chi them dong co so)", note="Tai lap: bien LNST TB/trung vi 2015-25 10,39%/10,20% x 7.137 = 742/728; 9T/26 906/7.803 = 11,6% => 829. 800 giu. Bien the E (735) va F (829) bao song song."),
    dict(n=6, verdict="DUNG - AP", note="Them WARNING: so Q3/26 tu lap chua soat xet; tien le soat xet H1/26 giam LNST ~94 ty (chi phi bao tri dinh ky ghi thieu) — BQ NP_P0 9T/26 = 1.002 vs BCTC 906 (chenh 96 = phan soat xet chua cap nhat BQ)."),
]
pos = {k: v for k, v in M['center_by_size'].items()}
SM = dict(old)
SM.update(dict(
    round='r3', job='Taylor_20261108_153742', asof_price_date=M['price_date'], price_date=M['price_date'], price=PX, r=M['r'], dep_now=M['dep'],
    center_pre_liq=S['center_pre'], center_post_liq=c, p10_post=S['p10_post'], p50_post=S['p50_post'], p90_post=S['p90_post'],
    p10_pre=S['p10_pre'], p50_pre=S['p50_pre'], p90_pre=S['p90_pre'], p10_out=S['p10_post'], p50_out=S['p50_post'], p90_out=S['p90_post'],
    pct_weight_below_price=S['pct_w_below_px'], n_outcomes=S['n'], min_outcome_post=S['min_post'], grid_n=S['n'], grid_desc=grid_desc,
    central_param_value_post=M['center_param_pre'] * (1 - Q['disc_ref']),
    liq_discount_ref=Q['disc_ref'], adv_med_bn_vnd=Q['adv250']['adv_bn'], adv60_med_bn_vnd=Q['adv60']['adv_bn'],
    ck_ref_size=dict(q_bn=5, adv250=Q['adv250']['sizes']['5'], adv60=Q['adv60']['sizes']['5'], center_post=c),
    ck_real_sleeve={k: dict(adv250=Q['adv250']['sizes'][k], adv60=Q['adv60']['sizes'][k], center_post=pos[k]) for k in ('0.01', '0.02', '0.04')},
    label=M['label'], label_note=f"Nhan theo gia tri sau CK o co 5 ty (ADV250, CK {pct(Q['disc_ref'])}); co sleeve 10-40 tr tam {f(pos['0.04'])}-{f(pos['0.01'])} — nhan khong doi. Vung P10-P90 (khong doi dinh nghia so r2).",
    px_vs_center=PX / c - 1, px_vs_p10=PX / S['p10_post'] - 1, px_vs_p90=PX / S['p90_post'] - 1,
    center_change_vs_r2=c / r2c - 1, center_change_vs_r1=c / (r2c / (1 + old['center_change_vs_r1'])) - 1,
    center_change_vs_old=c / old['zone_old']['center'] - 1,
    center_change_vs_old_basis=f"r3 tam {f(c)} so tam cu DD 26/10 25.400 (cum-div; co tuc 1.000 d GDKHQ 29/10) = " + ("+" if c > 25400 else "") + pct(c / 25400 - 1),
    zone_r2=dict(center=round(r2c), p10=round(old['p10_post']), p50=round(old['p50_post']), p90=round(old['p90_post']), label=old['label'], price=old['price'], date=old['asof_price_date']),
    axes_included=["LNST chuan hoa 450-1150 (2 chieu quanh 800)", "thoi han 5/8/10/12/15 (2 chieu quanh 10, MOI r3)", "r +-100bp", "FCF-LNST +-150 ty/nam (2 chieu quanh 0, MOI r3)"],
    axes_excluded=[dict(axis="NT5 dung tien NT2", reason="luat du an moi 03/11: NPV 0 => ban co truc = ban khong truc; chi WARNING quan tri"),
                   dict(axis="rui ro doi tac tien gui SHB", reason="khong co du lieu thuyet minh tien gui theo NH; chi WARNING"),
                   dict(axis="nut 4 nam (khi can 2030, khong PL13)", reason="chieu tang PL13 2026-2039 cung co nguon; giu luoi doi xung 5-15; bao song song A"),
                   dict(axis="gia tri sau thoi han > 0 / WIDE moat", reason="moat NONE (ADDENDUM_5F); WIDE chi do nhay")],
    base_adjustments=[dict(item="co tuc phai tra 297,1 tru khoi net cash", effect_dong_per_share=-297.125837477 / 287.876029 * 1000, basis="BCTC ma 313; gia 06/11 da ex-div", source="BCTC tr.3 + BQ Price"),
                      dict(item="NWC chuan hoa 574,3 thu hoi cuoi thoi han + 262,9 giai phong t=1 (r3 thay 837,2 cuoi han)", effect_dong_per_share=M['bridge'][3]['delta'],
                           basis="AR/DT TTM 37-49% 2022-26 => NWC ty le DT; dong LN chuan hoa theo DT 7.137", source="BCTC tr.2-3; calc_r3/ar_nt2_r3.csv"),
                      dict(item="gia tri sau thoi han = 0", effect_dong_per_share=None, basis="dong tien co thoi han; truc thoi han 5-15", source="CYCLE_BLOCK.md muc D")],
    center_vs_p50_note=f"tam (ky vong luoi) {f(c)} vs P50 ket cuc {f(S['p50_post'])} vs gia tri tai tham so trung tam (800/10 nam/r 13,5%/FCF=LNST) {f(M['center_param_pre']*(1-Q['disc_ref']))}: lech <1%, luoi doi xung; min ket cuc {f(S['min_post'])} (450 ty x 5 nam x r 14,5% x FCF -150). Khong nhanh trong so nho nao quyet dinh P10/P90.",
    change_reason=f"r3 vs r2: tam {f(r2c)} -> {f(c)} (+{pct(c / r2c - 1)}): truc thoi han 5-15 (-142), NWC chuan hoa (+{M['bridge'][3]['delta']}), truc FCF +-150 (0 o tam, gian P10/P90); gia 22.200 (06/11). Xem bridge_r2_to_r3.",
    change_vs_r1='r1->r2: ' + old.get('change_vs_r1', '') + ' | r2->r3: xem bridge_r2_to_r3',
    bridge_r2_to_r3=M['bridge'], control_r2_reproduced=dict(center_post=M['control_r2']['center_post'], p10=M['control_r2']['p10_post'], p90=M['control_r2']['p90_post'], match_r2=abs(M['control_r2']['center_post'] - r2c) < 0.5),
    headline_vs_alternatives=M['headline_vs_alternatives'],
    implied_by_price=dict(np_const_10y_nwc_norm=ip['np_const_10y_nwcnorm'], np_const_10y_nwc_full=ip['np_const_10y_nwcfull'], yrs_at_np800=ip['yrs_at_800_nwcnorm'],
                          r_at_center_params=ip['r_at_center_params'], net_cash_per_share=ip['net_cash_per_share'], net_cash_pct_price=ip['net_cash_pct_px'],
                          note="gia sau CK 5 ty = gia tri; LNST co dinh 10 nam can thiet / so nam can o LNST 800 / r ngu y o tham so trung tam"),
    assumptions=assumptions, corrections_check=corrections, parallel=M['parallel'], crosscheck=M['crosscheck'], sens_dep=M['sens_dep'],
    fear_buy_eligible_2_5=False,
    warnings=old['warnings'] + [
        "Han PPA: 2 nguon mau thuan (2036 substack vs PPA goc 2011-2020 bao cao MBS 2016, trang thai sau 2020 CHUA XAC MINH); khi mo hien huu can ~2030 [WEB-2] — truc thoi han 5-15 phu ca hai chieu",
        "So Q3/2026 tu lap CHUA soat xet; tien le soat xet H1/2026 giam LNST ~94 ty do chi phi bao tri dinh ky ghi thieu (BQ NP_P0 9T/26 1.002 vs BCTC 906)",
        "FCF chieu xuong (dai tu tien mat > phan bo; chi phi tra truoc 262,9 ma 271) CHUA KIEM lich su 2015-25 — chi co truc +-150 [UL]"],
    open_issues=old['open_issues'] + ["Lich su chi phi tra truoc dai tu 2015-25 (BCTC nam) de thay truc FCF +-150 [UL] bang so do"],
    sources=dict(model='calc_r3/model_r3.py -> calc_r3/model_r3_out.json/txt', assumptions='calc_r3/assumptions_r3.json', lock='calc_r3/LOCK_md5.txt (chot truoc khi chay)',
                 runs='calc_r3/run1.md5 = run2.md5', summary='calc_r3/make_summary_r3.py', liq='_common/liq.py + calc_r3/px_nt2_r3_20261106.csv', pct='_shared/wpct.py',
                 report='REPORT_r3.md', backup='SUMMARY_r2.json'),
))
json.dump(SM, open(os.path.join(TOP, 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print(f"SUMMARY r3: tam {c:,.0f} P10/50/90 {S['p10_post']:,.0f}/{S['p50_post']:,.0f}/{S['p90_post']:,.0f} {M['label']} vs r2 {c/r2c-1:+.2%} vs cu {c/25400-1:+.2%} vs r1 {SM['center_change_vs_r1']:+.2%}")
