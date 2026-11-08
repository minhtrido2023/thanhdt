"""SUMMARY.json NNC r3 tu nnc_redo_r3_out.json + SUMMARY_r2.json (giu warnings/open_issues). Chay: $DNA_PYEXE -B make_summary_r3.py"""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
o = json.load(open(os.path.join(H, 'nnc_redo_r3_out.json'))); s2 = json.load(open(os.path.join(P, 'SUMMARY_r2.json')))
A = json.load(open(os.path.join(H, 'assumptions_r3.json'), encoding='utf-8'))
po, pr, alt, T = o['post'], o['pre'], o['post_alternatives'], o['tornado']
rd = lambda x: int(round(x))  # noqa: E731
f = 1 - o['ck_ref']['adv250']
sh = {k: rd(v['d'] * f) for k, v in T.items()}
S = dict(s2)
S.update(
    round=3, job='Taylor_20261108_164333', asof_price_date=o['price_date'], price=o['price'], r=o['r'],
    r_anchor=dict(rate=o['dep'], date=o['dep_src'], rule='r = 13,5% + 1,0 x (dep_12T_hieu_dung - 7,40%)'),
    center_pre_liq=rd(o['center_pre']), center_post_liq=rd(o['center_post']),
    p10_post=rd(po['p10']), p50_post=rd(po['p50']), p90_post=rd(po['p90']), p10_pre=rd(pr['p10']), p90_pre=rd(pr['p90']),
    p10_out=rd(po['p10']), p50_out=rd(po['p50']), p90_out=rd(po['p90']), min_out=rd(po['min']),
    pct_weight_below_price=round(o['pct_weight_below_price'], 4), n_outcomes=o['n_outcomes'], n_cells=o['n_cells'],
    liq_disc_5bn=round(o['ck_ref']['adv250'], 5), ck_ref_size=o['ck_ref'], ck_real_sleeve=o['ck_real_sleeve'],
    px_vs_center_post=round(o['px_vs_center_post'], 4), px_vs_p10_post=round(o['px_vs_p10_post'], 4), px_vs_p90_post=round(o['px_vs_p90_post'], 4),
    label=o['label'],
    label_note=f"TRONG vung (P10-P90 muc ket cuc) nhu r2; dinh chinh keo tam LEN. Luat 4 (gia <= 0,85 x tam): {'DAT' if o['rule4_px_below_center_15pct'] else 'KHONG'}. Gia o canh duoi phan bo: {o['pct_weight_below_price']:.1%} trong so ket cuc duoi gia.",
    center_vs_p50_note=f"tam (ky vong luoi) {rd(o['center_post'])} vs P50 {rd(po['p50'])} vs gia tri tai tham so trung tam {rd(o['center_param_nodelay_post'])} (sau CK). Lech phai: P90 do nhanh STRUCTURAL (0,20) quyet dinh (P50 nhanh {rd(o['branch_pre']['STRUCTURAL']['p50']*f)}).",
    axes_included=['trang thai bien STRUCTURAL/ADMIN/CYCLICAL 0,20/0,45/0,35 (Bobby)', 'K chi phi 0,87/0,97/1,07', 'SL nam thuong 3 muc', 'anh xa ADMIN perm05/ramp/full',
                   'tran chu ky {SL 1,05 260,6k / theo SL nhanh / SL 1,40 236,1k} deu (r3: them 1,05)', 'thue Nui Nho {2043/2030/khong} deu [UL]', 'trong o: 4 kich ban W0 x 2 duong gia PW0',
                   'tran chu ky tang theo lam phat 3%/nam danh nghia tren moi duong gia (r3)'],
    axes_excluded=s2['axes_excluded'] + [
        dict(axis='co gian doi xung quanh tran (bo min, skeptic d.4)', reason=f"chi do nhay: tam sau CK {rd(alt['D4_sym_elastic']['mean'])}, P10 {rd(alt['D4_sym_elastic']['p10'])} (skeptic ghi 64.022 / P10 28,2k - KHONG tai lap; bo min thi chi nang duoc gia => P10 khong the giam)"),
        dict(axis='day kich ban xau khong chong len nhanh stress (skeptic d.5)', reason=f"do nhay: tam sau CK {rd(alt['D5_xau_nostack']['mean'])} ({rd(alt['D5_xau_nostack']['mean']-o['center_post']):+d}); base giu vi kich ban xau co dong co so du lieu (FPTS duong co so 0,8 tr m3 tu 2028, gia 237,6k/209,8k - FPTS tr.1, tr.17; SKEPTIC_20261031 E3)"),
        dict(axis='nguoi mua tra truoc 5,03 ty', reason=f"VLD van hanh, mo hinh khong tinh VLD ca hai phia; mot chieu {sh['(-) tru nguoi mua tra truoc 5,03 ty mot chieu']:+d}, doi xung voi phai thu BQ 24,44 {sh['(+) VLD doi xung: phai thu BQ AR_P0 24,44 - tra truoc 5,03']:+d} (sau CK)")],
    base_adjustments=s2['base_adjustments'] + [
        dict(item='Tran chu ky tang theo lam phat (D1)', effect_dong_per_share=rd(o['bridge_post']['D1_infl_cap'] - o['bridge_post']['r2_rebuild']), basis='sua loi mo hinh: tran tien 2026 nhan g2031 => bien kep 26% < TB chu ky 34,3% tu 2030 (dem hai lan voi duong g2031)', source='model_r6.py:43-47 x model_r5.py:49,124; SKEPTIC_R4_20261103.md:3; TOP5C d.1'),
        dict(item='Truc tran them muc SL 1,05 (D2)', effect_dong_per_share=rd(o['bridge_post']['D2_cap_axis_3'] - o['bridge_post']['D1_infl_cap']), basis='luat doi xung STANDARD_r2 §2; SL 2024 = 1,05 tr m3; DT TP kiem toan 257,44/1,05 = 245,2k x1,03^2 = 260,1k ~ tran 260,6k', source='REPORT.md:78-79 (KT25 7.1, FPTS); TOP5C d.2')],
    assumptions=[dict(key=k, value=A.get(k), basis=A['notes'].get(k.replace('cust_adv_bn', 'cust_adv').replace('ar_bq_bn', 'cust_adv').replace('cap_axis', 'D2_cap_axis'), '')) for k in ('cap_axis', 'cust_adv_bn', 'ar_bq_bn')] + [
        dict(key='infl_cap', value=True, basis=A['notes']['D1_infl_cap']), dict(key='rent_axis', value='2043/2030/khong deu', basis=A['notes']['rent_axis']),
        dict(key='r', value=o['r'], basis=A['notes']['r']), dict(key='bs_items', value='n_cash engine', basis=A['notes']['bs_items_verified']),
        dict(key='trong so trang thai bien', value='0,20/0,45/0,35', basis='Bobby (nhan dinh, khong phai tan suat) - [UL]'),
        dict(key='W0 kich ban', value='25/50/20/5', basis='r3 engine; xau = FPTS duong co so'), dict(key='PW0 duong gia', value='g2031 50 / thuc 50', basis='r3 engine [UL]'),
        dict(key='CK thanh khoan', value=f"Y=1,0 x sigma x sqrt(5 ty / ADV250) = {o['ck_ref']['adv250']:.2%}", basis='luat can bac hai dang ky truoc (common.py); BQ 06/11')],
    headline_vs_alternatives=dict(headline=dict(center=rd(o['center_post']), p10=rd(po['p10']), p50=rd(po['p50']), p90=rd(po['p90'])),
                                  **{k: dict(center=rd(v['mean']), p10=rd(v['p10']), p50=rd(v['p50']), p90=rd(v['p90'])) for k, v in alt.items()},
                                  w_structural={k: dict(center=rd(v['mean'] * f), p10=rd(v['p10'] * f), p90=rd(v['p90'] * f)) for k, v in o['sens_w_structural_pre'].items()},
                                  tornado_post={k: v for k, v in sh.items()}),
    implied_by_price=dict(price=o['price'], price_pre_ck=rd(o['implied_by_price']['px_pre_ck']), roe_gordon=round(o['implied_by_price']['roe_gordon'], 4),
                          roe_normalised_range=[round(s2['gordon']['roe_lock'], 4), round(s2['gordon']['roe_fin'], 4)],
                          cyclical_100pct_post=rd(o['implied_by_price']['cyc100_post']), cyclical_100pct_vs_price=round(o['implied_by_price']['cyc100_vs_px'], 4),
                          note='Gia ham y ROE ben ~20,2% (Gordon) > ROE chuan hoa 14,7-17,2%; ngay ca 100% CYCLICAL van cao hon gia ~12%. Gia chi khop khi kich ban xau/rat xau (FPTS duong co so) la chu dao.'),
    bridge_r2_to_r3=[dict(step='r2 pin (gia 04/11, CK 3,63%)', center_post=s2['center_post_liq']),
                     dict(step='r2 dung lai, CK 06/11 3,65%', center_post=rd(o['bridge_post']['r2_rebuild']), reason='chi doi cua so thanh khoan; luoi tai lap trung r2 truoc CK 59.760'),
                     dict(step='D1 tran tang theo lam phat', center_post=rd(o['bridge_post']['D1_infl_cap']), reason='bo dem hai lan bien tren duong g2031 (skeptic +2.525: KHOP)'),
                     dict(step='D2 them muc tran SL 1,05', center_post=rd(o['bridge_post']['D2_cap_axis_3']), reason='truc tran doi xung (skeptic +1.167: KHOP; co so gia skeptic "260k" = DT kiem toan/SL, khong phai gia mo FPTS 202,6k)'),
                     dict(step='d.3-d.6 chi do nhay/ghi chu', center_post=rd(o['center_post']), reason='thue chi 2043, co gian doi xung, xau khong chong, tra truoc nguoi mua: khong vao base')],
    gordon=dict(s2['gordon'], roe_implied_center=o['gordon']['roe_implied_center_pre'], roe_implied_by_price=o['gordon']['roe_implied_by_price']),
    r2=dict(center_post=s2['center_post_liq'], p10=s2['p10_post'], p50=s2['p50_post'], p90=s2['p90_post'], price=s2['price'], below=s2['pct_weight_below_price'],
            below_at_new_price=round(o['r2_at_new_price']['below'], 4)),
    center_change_pct=round(o['center_post'] / s2['center_post_liq'] - 1, 4),
    change_reason='D1 tran chu ky tang theo lam phat (+2.525) + D2 truc tran doi xung them SL 1,05 (+1.167); CK 06/11 (-8)',
    lock='calc/LOCK_r3_md5.txt', measured_by='dd_redo_20261105/NNC/calc/nnc_redo_r3_out.json (2 lan chay trung byte)')
S['open_issues'] = s2['open_issues'] + ['Ban co gian doi xung cua skeptic (64.022 / P10 28,2k) khong tai lap duoc - can skeptic neu cong thuc',
                                        'BCTC Q3 PDF: 322,44 HTM / 22,37 / 16,78 / nguoi mua tra truoc 5,03 chua kiem lai trong phien r3 (BQ khop tien 25,47 + vay 74,89)']
S.pop('r1', None)
json.dump(S, open(os.path.join(P, 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=False)
print('ok', S['center_post_liq'], S['p10_out'], S['p90_out'], S['label'], S['pct_weight_below_price'])
