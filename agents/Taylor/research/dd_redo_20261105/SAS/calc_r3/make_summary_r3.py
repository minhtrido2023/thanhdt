"""Ghi SAS/SUMMARY.json vong 3 tu model_sas_r3_out.json + assumptions_r3.json + SUMMARY_r2.json (tat dinh).
Chay sau model_sas_r3.py: /home/trido/thanhdt/wc_venv/bin/python -I -B make_summary_r3.py > make_summary_r3_out.txt"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SAS = os.path.dirname(HERE)
M = json.load(open(os.path.join(HERE, 'model_sas_r3_out.json')))
A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
OLD = json.load(open(os.path.join(SAS, 'SUMMARY_r2.json')))
R = lambda x: int(round(x))
H = M['headline']; px = M['price']; Q = M['liq']; B = M['blocks']; SH = A['shares_mn']['v']; EPSR = A['eps_ratio']['v']; r = M['r']


def d(s):
    return dict(center=R(s['center_post']), p10=R(s['p10_post']), p50=R(s['p50_post']), p90=R(s['p90_post']),
                pct_below=round(s['pct_w_below_px'], 4), px_vs_center=round(px / s['center_post'] - 1, 4), label=s['label'])


reasons = {
    "S0_r2_tai_lap_gia_0411": "doi chung: tai lap r2 dung 31.066 (gia 34.700 ngay 04/11)",
    "S1_gia_ADV_0611": "gia + ADV toi 06/11 tu BQ (34.200; ADV250 0,59->0,61 ty; CK 5 ty 6,01%->5,93%); r giu 13,5% (lai huy dong hieu dung 06/11 = 7,40%)",
    "S2_N0_co_tuc_mien_thue": "dinh chinh 1 DUNG: r2 danh thue 20% len ca 188,3 thu nhap TC rong trong khi co tuc mien thue (kiem: LNTT 638,03 - thue hien hanh 98,13/20% => mien thue 147,4). N0 = (LNTT - TC rong) x 0,8 x 4/3 = 479,7 (r2 518,4)",
    "S3_VLD_nhat_quan": "dinh chinh 2 DUNG: r2 tru phai tra NLD 141,2 + thue 50,2 nhung bo qua TSNH van hanh (VLD ngoai tien +130,3). Coi VLD van hanh nam trong N0 => chi tru quy KTPL 99,7 + co tuc phai tra 2,06 (khoan khong thuoc co dong/ da cong bo)",
    "S4_XDCB_BDSDT_theo_so": "dinh chinh 3 DUNG (luat 20): XDCB 118,0 (ma 252) + BDS dau tu 32,2 (ma 240, hao mon luy ke khong doi 9T => nam giu cho tang gia, khong trong N0) theo so",
    "S5_trich_KTPL_LN_9T": "WARNING 6 cua skeptic dua vao base: LN 9T/2026 chua trich quy (VCSH 1.878 khong doi); trich (1-0,883) x 539,5 = 63,1 ty — cung co so eps_ratio da ap cho LN tuong lai",
    "S6_khop_ngay_dinh_gia": "MOI (phat hien khi kiem): r2 lay CDKT 30/09 nhung chiet khau tu 31/12/2026 => bo trong LN van hanh Q4/2026. + N0/4 x 0,883 = 105,9 ty, chiet khau moi dong tien tuong lai 55 ngay ve 06/11",
}
bridge, prev = [], None
for k, s in M['bridge'].items():
    bridge.append(dict(step=k, **{x: y for x, y in d(s).items() if x in ('center', 'p10', 'p50', 'p90', 'pct_below', 'label')},
                       delta_center=None if prev is None else R(s['center_post'] - prev), reason=reasons[k]))
    prev = s['center_post']

alts = {k: d(s) for k, s in M['alternatives'].items()}
alt_note = {
    "A1_skeptic_diem_S2_S4_khong_S5_S6": "tai lap diem skeptic (dinh chinh 1-3, khong trich KTPL 9T, khong khop ngay) — skeptic 31.731 (gia 04/11 CK cu, khong tru co tuc phai tra)",
    "A2_gop_du_VLD_rong": "chieu LEN: cong VLD ngoai tien rong 130,3 (coi TSNH > no NH la tien thua) — khong vao base vi VLD can de van hanh",
    "A3_khong_trich_KTPL_9T": "bo S5",
    "A4_khong_khop_ngay": "bo S6",
    "A5_N0_co_tuc_bao_chi_135_8": "N0 tinh qua co tuc bao chi 135,8 thay vi LNTT - TC rong (N0 482,2)",
    "A6_bo_phai_thu_DH": "chieu XUONG: bo phai thu DH 242 (song song r2)",
    "A7_bo_truc_g": "g = 3% co dinh",
    "A8_von_hoa_co_tuc_dau_tu_71ty_nam": "chieu LEN (dinh chinh 4, KHONG vao base): thay so sach dau tu 253,8 bang D x 0,883 / r (g 0)",
    "A8_von_hoa_co_tuc_dau_tu_100ty_nam": "nhu tren, D 100",
    "A8_von_hoa_co_tuc_dau_tu_140ty_nam": "nhu tren, D 140 (skeptic 140 => 37.253 khong nhan 0,883 va tren nen khac; o day 36.340)",
}
for k in alts:
    alts[k]['note'] = alt_note[k]

hd = d(H)
# cross-check Gordon (STANDARD dieu 10), Delta -25% vinh vien, g 3%, khong nam chuyen tiep, khong khop ngay
fin_ann_at = (B['fin_net_9m'] - (B['fin_net_9m'] - B['exempt_implied']) * 0.20) * 4 / 3
assets = B['X_r3'] + A['lt_inv']['v'] + A['lt_recv']['v'] + B['cip_bds'] - B['ktpl9']
cc = dict(A_co_thu_nhap_TC_khong_cong_tien_va_dau_tu=R(((B['N0_r3'] * 0.75 + fin_ann_at) * EPSR / (r - 0.03) + A['lt_recv']['v'] + B['cip_bds'] - B['ktpl9'] - A['ktpl_fund']['v'] - A['div_payable']['v']) / SH * 1000),
          B_khong_thu_nhap_TC_cong_tien_va_tai_san=R((B['N0_r3'] * 0.75 * EPSR / (r - 0.03) + assets) / SH * 1000),
          fin_income_after_tax_annual_bn=round(fin_ann_at, 1), note="truoc CK; A von hoa ca lai tien gui + co tuc vinh vien g 3% (khong dung); B = cach base")

S = dict(OLD)
for k in ('parallel', 'crosscheck', 'change_vs_r1', 'center_change_vs_r1', 'dep_now', 'r_anchor', 'sources'):
    S.pop(k, None)
S.update(dict(
    ticker='SAS', round='r3', job='Taylor_20261108_153740', asof_price_date=M['price_date'], price=px,
    price_basis='dong cua 06/11/2026 tav2_bq.ticker (07/11 thu Bay) — calc_r3/px_sas_r3_20261106.csv',
    r=r, r_anchor=dict(formula='r = 13,5% + 1,0 x (lai huy dong 12T hieu dung - 7,40%)', dep_06_11=M['dep'], dep_source=M['dep_src']),
    center_pre_liq=R(H['center_pre']), center_post_liq=R(H['center_post']),
    p10_post=R(H['p10_post']), p50_post=R(H['p50_post']), p90_post=R(H['p90_post']),
    p10_pre=R(H['p10_pre']), p50_pre=R(H['p50_pre']), p90_pre=R(H['p90_pre']),
    p10_out=R(H['p10_post']), p50_out=R(H['p50_post']), p90_out=R(H['p90_post']),
    min_outcome_post=R(H['min_post']), max_outcome_post=R(H['max_post']), pct_weight_below_price=round(H['pct_w_below_px'], 4), n_outcomes=H['n'], grid_n=H['n'],
    center_param_post=R(M['center_param_post']),
    label=H['label'], label_changed_vs_r2=False,
    label_note=("Headline o co tham chieu 5 ty (CK %.2f%%, Q/ADV250 %.0f%% — NGOAI xa vung hieu chinh, CK chi la quy uoc). Co sleeve that 40 tr (CK %.2f%%): tam %s, P10/P90 %s/%s, gia/tam %+.1f%%, %s — dong rieng ck_real_sleeve_line. Dinh nghia vung P10-P90 khong doi so r2."
                % (Q['disc_ref'] * 100, Q['adv250']['sizes']['5']['q_over_adv'] * 100, Q['adv250']['sizes']['0.04']['disc'] * 100,
                   f"{R(M['by_size']['0.04']['center_post']):,}", f"{R(M['by_size']['0.04']['p10_post']):,}", f"{R(M['by_size']['0.04']['p90_post']):,}",
                   (px / M['by_size']['0.04']['center_post'] - 1) * 100, M['by_size']['0.04']['label'])),
    liq_discount_ref=Q['disc_ref'], liq_ref_position_bn_vnd=5, adv_med_bn_vnd=Q['adv250']['adv_bn'], adv60_med_bn_vnd=Q['adv60']['adv_bn'],
    ck_ref_size=dict(q_bn=5, adv250=Q['adv250']['sizes']['5'], adv60=Q['adv60']['sizes']['5']),
    ck_real_sleeve={k: dict(adv250=Q['adv250']['sizes'][k], adv60=Q['adv60']['sizes'][k], center_post=R(M['by_size'][k]['center_post']),
                            p10_post=R(M['by_size'][k]['p10_post']), p90_post=R(M['by_size'][k]['p90_post']), label=M['by_size'][k]['label'])
                    for k in ('0.01', '0.02', '0.04')},
    px_vs_center=round(px / H['center_post'] - 1, 4), px_vs_p10=round(px / H['p10_post'] - 1, 4), px_vs_p90=round(px / H['p90_post'] - 1, 4),
    center_change_vs_r2=round(H['center_post'] / OLD['center_post_liq'] - 1, 4),
    center_change_vs_old=round(H['center_post'] / OLD['zone_old']['center'] - 1, 4),
    grid_desc=("4 truc, n=135 ket cuc tat dinh (luoi r2 giu nguyen): Delta Long Thanh len LN van hanh tu 2028 {-55;-40;-25;-10;+5}% (0,1/0,2/0,4/0,2/0,1) [UL], 2027 = nua tac dong "
               "x N0 {-10%;0;+10%} quanh 479,7 (r3; r2 518,4) x r {12,5;13,5;14,5}% x g {2;3;4}% (truc phu 1/4-1/2-1/4). Tai san co dinh: tien+DTNH 945,2 - quy KTPL 99,7 - co tuc phai tra 2,1 "
               "+ dau tu DH 253,8 + phai thu DH 242,0 + XDCB 118,0 + BDS DT 32,2 - trich KTPL LN 9T 63,1 (so sach). + LN van hanh Q4/26 105,9; dong tien tuong lai chiet khau 55 ngay ve 06/11. "
               "LN x 0,883. Phan vi = _shared/wpct.py tren 135 o; tam = ky vong luoi. Headline CK 5 ty ADV250."),
    center_vs_p50_note=f"tam (ky vong luoi) {R(H['center_post']):,} > P50 {R(H['p50_post']):,} > gia tri tai tham so trung tam {R(M['center_param_post']):,} (Delta -25, N0 479,7, r 13,5, g 3; sau CK 5 ty): lech phai nhe do Gordon loi theo g/r. Khong nhanh trong so nho nao quyet dinh P10/P90.",
    assumptions=[dict(key=k, value=x.get('v'), basis=x['basis'], source=x['source']) for k, x in A.items() if not k.startswith('_')],
    headline_vs_alternatives=dict(headline=dict(hd, desc='S6: dinh chinh 1-3 + trich KTPL 9T + khop ngay; CK 5 ty'), alternatives=alts,
                                  headline_choice_reason="Headline = mo hinh co so sau dinh chinh co co so du lieu BCTC; moi bien the khac (VLD rong, von hoa co tuc, bo phai thu DH) chi la do nhay song song."),
    implied_by_price=dict(price=px, delta_longthanh_center=round(M['implied']['delta_center'], 4), r=round(M['implied']['r'], 4),
                          div_capitalized_bn_per_year=round(M['implied']['div_capitalized_bn_per_year'], 1), n0_bn=round(M['implied']['n0_bn'], 1),
                          note="moi bien doi rieng le de tam sau CK 5 ty = gia; skeptic: Delta ~-16%, r ~12,4%, ~71 ty/nam (khong nhan 0,883, nen khac)"),
    bridge_r2_to_r3=bridge,
    corrections_check=[
        dict(item=1, verdict="DUNG — ap", evidence="KQKD tr.5 (img/p11): LNTT 638,035; thue hien hanh 98,128 => mien thue 147,4; N0 479,7 (bien the co tuc 135,8: 482,2) — khop 479-482 cua skeptic", effect=bridge[2]['delta_center']),
        dict(item=2, verdict="DUNG — ap ban 'chi tru KTPL' (+ co tuc phai tra 2,06); ban gop du VLD rong la song song chieu len", evidence="CDKT tr.1/tr.3: 130 165,8 / 140 204,3 / 162 240,6 / 310 495,8; VLD ngoai tien +130,3", effect=bridge[3]['delta_center']),
        dict(item=3, verdict="DUNG — ap", evidence="CDKT tr.2 (img/p08): ma 252 118,04; ma 240 32,24 (hao mon luy ke 5,009 khong doi => nam giu cho tang gia)", effect=bridge[4]['delta_center']),
        dict(item=4, verdict="DUNG huong — chi do nhay (khong base)", evidence="bien the A8; o 140 ty/nam tam 36.340 (skeptic 37.253 khong nhan 0,883). Ben tra co tuc + muc deu dan CHUA KIEM (thuyet minh V.2c/V.27 khong co trong anh trich)", effect=None),
        dict(item=5, verdict="DUNG", evidence="BQ 06/11 dong cua 34.200; r2 o gia moi: tam 31.094, gia/tam +10,0%, 73,3% duoi gia (S1)", effect=bridge[1]['delta_center']),
        dict(item=6, verdict="DUNG — 3 warning ghi; KTPL 9T dua vao base (S5, -63,1 ty)", evidence="VCSH 1.878 khong doi, LNST chua phan phoi 539,3", effect=bridge[5]['delta_center']),
        dict(item=7, verdict="GHI NHAN", evidence="Delta Long Thanh + 57% DT quoc te van [UL] hai chieu; Gordon khong tru tai dau tu giu quy uoc 08/11 (ban chat-3c 22.002 cua ADDENDUM_5F tinh tren mo hinh r2, chi la do nhay rui ro, khong tinh lai)", effect=None)],
    axes_included=["Delta Long Thanh 2 chieu quanh -25%", "N0 +-10% (quanh 479,7)", "r +-100bp", "g 2/3/4%"],
    axes_excluded=OLD['axes_excluded'] + [dict(axis="von hoa co tuc dau tu (chieu len)", reason="chua biet ben tra/muc deu dan (thuyet minh V.2c/V.27 chua doc) => do nhay A8"),
                                          dict(axis="VLD ngoai tien rong +130,3 (chieu len)", reason="VLD can cho van hanh, da trong N0 => do nhay A2")],
    base_adjustments=[
        dict(item="Delta Long Thanh tam -25% tu 2028 (2027 -12,5%)", effect_dong_per_share=None, basis="lo trinh Cuc HK 28/3/2027-25/3/2028; ~57% DT Q3 gan khach quoc te; DO LON = nhan dinh [UL], da la truc xac suat 2 chieu", source="dd_SAS_20261026 §2-3"),
        dict(item="N0 loai thu nhap TC rong, thue 20% chi tren LN van hanh", effect_dong_per_share=None, basis="KQKD ma 50/22/23/51", source="img/p11 tr.5"),
        dict(item="tru quy KTPL 99,7 + co tuc phai tra 2,06 khoi tien", effect_dong_per_share=R(-(A['ktpl_fund']['v'] + A['div_payable']['v']) / SH * 1000), basis="BCTC ma 323/313", source="img/p09 tr.3"),
        dict(item="phai thu DH khac 242,0 theo so", effect_dong_per_share=R(A['lt_recv']['v'] / SH * 1000), basis="BCTC ma 215; khong co du lieu suy giam", source="img/p08 tr.2"),
        dict(item="XDCB 118,0 + BDS dau tu 32,2 theo so (MOI r3)", effect_dong_per_share=R(B['cip_bds'] / SH * 1000), basis="BCTC ma 252/240; luat 20", source="img/p08 tr.2"),
        dict(item="trich KTPL tren LN 9T/2026 (MOI r3)", effect_dong_per_share=R(-B['ktpl9'] / SH * 1000), basis="(1-0,883) x LNST 9T 539,5", source="img/p11 + eps_ratio"),
        dict(item="LN van hanh Q4/2026 + chiet khau 55 ngay (MOI r3)", effect_dong_per_share=None, basis="CDKT 30/09 vs goc chiet khau 31/12/2026", source="mo hinh"),
        dict(item="LN x 0,883", effect_dong_per_share=None, basis="EPS 2025 4.602 / (LNST 695,6 / 133,45 tr CP)", source="DHDCD 2026 (vietnambiz 25/06/2026) + BQ")],
    crosscheck_gordon=cc,
    sens_dep={k: dict(center_post=R(x['center_post']), d_pct=round(x['d_pct'], 4)) for k, x in M['sens_dep'].items()},
    change_reason=(f"r3 vs r2 {H['center_post']/OLD['center_post_liq']-1:+.1%}: gia 06/11 (+{bridge[1]['delta_center']}), N0 co tuc mien thue ({bridge[2]['delta_center']:+,}), VLD nhat quan ({bridge[3]['delta_center']:+,}), "
                   f"XDCB+BDSDT ({bridge[4]['delta_center']:+,}), trich KTPL 9T ({bridge[5]['delta_center']:+,}), khop ngay Q4/26 ({bridge[6]['delta_center']:+,}). So vung cu 26/10 (32.600): {H['center_post']/OLD['zone_old']['center']-1:+.1%}."),
    change_vs_r2="xem bridge_r2_to_r3",
    warnings=OLD['warnings'] + [
        "20 lo dat >7,2 trieu m2 (Bo Tai chinh 2019) — theo skeptic 08/11, CHUA KIEM ban goc",
        "Phai thu IPP Group Pte 194 ty (ben lien quan) — da thu (DD 26/10 [BC-BCTC]); van la kenh giao dich ben lien quan",
        "Ben tra co tuc dau tu (135,8-147 ty/9T) CHUA xac dinh — dau tu DH 253,8 gom LDLK 161,4 + gop von khac 107,2 - du phong 14,8 (img/p08)",
        "Ky giua nien do khong trich quy KTPL tren LN 9T — r3 da tru 63,1 ty trong base (S5)"],
    open_issues=["Thuyet minh V.2c/V.27: ben tra co tuc + muc deu dan (quyet dinh bien the A8)", "Thuyet minh V.5b phai thu DH 242", "Khoan bu DFS Q4/2025",
                 "Ket qua thau Long Thanh + lo trinh chinh thuc", "HTK 204,3 chua trich lap", "Thieu sector read dich vu hang khong", "BQ EPS = 0 moi quy SAS",
                 "20 lo dat 7,2 trieu m2 (BTC 2019) chua kiem"],
    fearbuy_sleeve_eligible=False,
    sources=dict(model='calc_r3/model_sas_r3.py -> calc_r3/model_sas_r3_out.txt/json', summary='calc_r3/make_summary_r3.py', assumptions='calc_r3/assumptions_r3.json',
                 lock='calc_r3/LOCK_r3_md5.txt (+ LOCK_r3_summary_md5.txt)', price='calc_r3/px_sas_r3.sql -> px_sas_r3_20261106.csv', pct='_shared/wpct.py', r2_backup='SUMMARY_r2.json'),
))
S['ck_real_sleeve_line'] = (f"Co sleeve 40 tr: CK {Q['adv250']['sizes']['0.04']['disc']:.2%} (Q/ADV250 {Q['adv250']['sizes']['0.04']['q_over_adv']:.1%}, trong vung) => tam {R(M['by_size']['0.04']['center_post']):,}, "
                            f"P10/P90 {R(M['by_size']['0.04']['p10_post']):,}/{R(M['by_size']['0.04']['p90_post']):,}, gia/tam {px/M['by_size']['0.04']['center_post']-1:+.1%}, {M['by_size']['0.04']['label']}")
json.dump(S, open(os.path.join(SAS, 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print(f"SUMMARY r3: tam {S['center_post_liq']:,} | P10/50/90 {S['p10_out']:,}/{S['p50_out']:,}/{S['p90_out']:,} | {S['label']} | gia {px:,.0f} gia/tam {S['px_vs_center']:+.1%} | duoi gia {S['pct_weight_below_price']:.1%} | vs r2 {S['center_change_vs_r2']:+.1%} | vs cu {S['center_change_vs_old']:+.1%}")
print(S['ck_real_sleeve_line'])
print("crosscheck", cc)
print(S['change_reason'])
