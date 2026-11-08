"""DDV r3 — dung SUMMARY.json tu model_r3_out.json + assumptions_r3.json (moi truong dan xuat lay tu so r3, khong go tay).
Chay: cd calc_r3 && $DNA_PYEXE -I make_summary_r3.py  (SUMMARY r2 da backup ../SUMMARY_r2.json)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
O = json.load(open(os.path.join(HERE, 'model_r3_out.json')))
A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
S2 = json.load(open(os.path.join(HERE, '..', 'SUMMARY_r2.json')))
H, C, PX = O['headline'], O['control_r2'], O['price']
alt = O['alternatives']
f = lambda x: f'{x:,.0f}'.replace(',', '.')


def row(k):
    a = alt[k]; return dict(desc=a['desc'], center_post=a['center_post'], p10_out=a['p10'], p50_out=a['p50'], p90_out=a['p90'],
                            pct_weight_below_price=a['below'], label=a['label'], delta_vs_headline=a['delta_vs_headline'])


grid_desc = ('ket cuc = duong S/DAP 2027 (xau/co so/tot 0,45/0,40/0,15; LN 2027 -185/+107/+373) x he so LN giua chu ky 0,8..1,2 (deu) '
             'x lai huy dong -50/0/+50bp (0,25/0,5/0,25) x LN loi Q4/2026 -54,4/-4,4(=Q3 that)/+45,6 ty (0,25/0,5/0,25) '
             'x khoan tru lai gui khoi LN giua chu ky 70,9/35,4/0 ty (0,25/0,5/0,25); RONIC = Ke tung o; tien rong = so BCTC 1.108; '
             f'DT chuan hoa 5.652 (FY2025); n={H["n"]}; tham so trung tam = co so, m=1, dr=0, Q4 nhu Q3, tru lai 35,4')
center_vs_p50 = (f'tam (ky vong trong so luoi, sau CK 5 ty) {f(H["center_post"])} vs P50 ket cuc {f(H["p50"])} vs gia tri tai tham so trung tam '
                 f'{f(O["center_param_post"])}. Tam < tham so trung tam vi nhanh xau duong 2027 (w 0,45) nang hon nhanh tot (0,15); '
                 'khong nhanh trong so nho nao quyet dinh rieng P10/P90 (truc doi xung, Liven da ra khoi luoi).')
bridge = O['bridge']
reasons = {
 '1': 'gia 06/11 = 15.200 (khong doi), CK 5 ty 1,447% -> 1,473% (ADV 250 phien 12,50 ty)',
 '2': 'skeptic #1 DUNG: VLD rong day du 30/09 581,8 > 01/01 463,9 => khong co tien thoi phong; r2 chi lay chan PT NB/PT KH so moc 30/06 (dinh). Chon so BCTC (khong chuan hoa), khong phai moc 01/01 mot chan (-355) skeptic dung cho diem 14.388',
 '3': 'skeptic #2 DUNG: he so 0,8/1/1,1 theo trong so Bobby = nhan dinh, bien chu ky da gom nam lo 2016',
 '4': 'skeptic #3 DUNG: moat NONE => RONIC = Ke (tien le HPG #3); -731 (skeptic -675 tinh truoc buoc 3)',
 '5': 'skeptic #4 DUNG: khong co van ban no qua han => Liven theo so, xac suat mat sang do nhay',
 '6': 'skeptic #7 DUNG: truc Q4 doi xung +-50 (skeptic +19 tai lap +18)',
 '7': 'skeptic #6: 5.500 khong co co so -> FY2025 BQ 5.652 (du lieu); hai chieu bao do nhay',
 '8': 'skeptic #5 kiem MOT PHAN: khoan tru phai la thu nhap TC lich su trong bien, khong phai lai hien tai; can tren 70,9 (lai hien tai tren tien thuc), can duoi 0 (bao thu: 2015-20 no vay 260-1.050 ty). +886 nam trong uoc skeptic +0,5-1,0k. So chinh xac CHUA KIEM (thieu thu nhap TC kiem toan 2015-22)'}
for b in bridge:
    b['reason'] = reasons.get(b['step'][0], 'control r2 tai lap trung (13.109 / 10.115 / 16.270)')
corrections = [
 dict(n=1, verdict='DUNG (chon ban skeptic "bo chuan hoa", khong chon moc 01/01 mot chan)', effect=bridge[2]['delta'], evidence='BCTC Q3 en_p1.txt dong 107-175: PT KH 219,4/23,8, tra truoc 130,1/82,8, HTK 836,6/693,9, PT NB 569,4/321,2, KH tra truoc 34,9/15,4 (30/09 / 01/01) => VLD 581,8 / 463,9 (tai lap so skeptic)'),
 dict(n=2, verdict='DUNG', effect=bridge[3]['delta'], evidence='BQ bq_hist_out.csv: 2016 LN -470,3 ty nam trong NPM chu ky 4,05%'),
 dict(n=3, verdict='DUNG', effect=bridge[4]['delta'], evidence='ADDENDUM_5F moat NONE; quy uoc user 08/11'),
 dict(n=4, verdict='DUNG', effect=bridge[5]['delta'], evidence='khong co van ban no qua han trong BCTC Q3'),
 dict(n=5, verdict='KIEM MOT PHAN — huong dung, so chinh xac CHUA KIEM', effect=bridge[8]['delta'], evidence='BQ StDebt_P0 2015-20 260-1.050 ty (bq_cash_hist_out.csv); VND 02/06/2025: DT tai chinh thuan 2023 43 / 2024 50 ty; lai Q3/2026 22,15 ty (BCTC). Thieu thu nhap TC kiem toan 2015-22 => truc 3 diem, do nhay can 70,9 (-1.558) / 0 (+1.558)'),
 dict(n=6, verdict='DUNG (them dong co so)', effect=bridge[7]['delta'], evidence='BQ: FY2025 5.652,0; TB 2021-25 3.709,7 (do nhay -3.459, TREN); LTM 6.406,2 (+1.343)'),
 dict(n=7, verdict='DUNG', effect=bridge[6]['delta'], evidence='VCSH BCTC 2.208,2 (ma 400) thay 2.214; trong so 2027 doi xung 1/3 tai lap +425 (bao song song, khong vao base vi E[LN 2027] co neo LN loi Q3 that)'),
 dict(n=8, verdict='DUNG', effect=0, evidence='gia 06/11 BQ 15.200 (px_ddv_r3_20261106.csv); van CHUA tra truc tiep UBCKNN/HNX (WARNING)')]
out = dict(
 ticker='DDV', round=3, job='Taylor_20261108_153738', asof_price_date=O['asof_price'], price=PX, r=O['r'],
 r_anchor=dict(rule=A['r_rule'], dep_asof=O['dep_asof'], dep_anchor=O['dep_anchor']),
 n_outcomes=H['n'], grid_n=H['n'], grid_desc=grid_desc,
 center_pre=H['center_pre'], center_post=H['center_post'], center_pre_liq=H['center_pre'], center_post_liq=H['center_post'],
 center_param_post=round(O['center_param_post']), center_param_pre=round(O['center_param_pre']),
 p10_out=H['p10'], p25_out=H['p25'], p50_out=H['p50'], p75_out=H['p75'], p90_out=H['p90'],
 p10_post=H['p10'], p25_post=H['p25'], p50_post=H['p50'], p75_post=H['p75'], p90_post=H['p90'],
 min_out=H['min'], max_out=H['max'], pct_weight_below_price=H['below'], label=H['label'],
 px_vs_center_post=PX / H['center_post'] - 1, px_vs_p10_post=PX / H['p10'] - 1, px_vs_p90_post=PX / H['p90'] - 1,
 liq_disc_5ty=O['d_ref'], ck_ref_size=dict(q_vnd=5e9, adv='250 phien', disc=O['d_ref'], in_calib=False, q_over_adv=O['liquidity']['w250']['sizes']['5000tr']['q_over_adv'],
                                           disc_adv60=O['liquidity']['w60']['sizes']['5000tr']['disc']),
 ck_real_sleeve={k: dict(disc_adv250=O['liquidity']['w250']['sizes'][k]['disc'], disc_adv60=O['liquidity']['w60']['sizes'][k]['disc'],
                         q_over_adv250=O['liquidity']['w250']['sizes'][k]['q_over_adv'], in_calib=O['liquidity']['w250']['sizes'][k]['in_calib']) for k in ('10tr', '20tr', '40tr')},
 headline_sleeve_40tr=dict(center_post=O['headline_sleeve40']['center_post'], p10_out=O['headline_sleeve40']['p10'], p90_out=O['headline_sleeve40']['p90'],
                           label=O['headline_sleeve40']['label'], disc=O['d_40tr']),
 liquidity=O['liquidity'],
 center_change_vs_old=H['center_post'] - S2['center_post'], center_change_vs_old_pct=H['center_post'] / S2['center_post'] - 1,
 center_change_vs_old_basis=f'r3 {f(H["center_post"])} vs r2 {f(S2["center_post"])} (SUMMARY_r2.json, gia 04/11); cung gia 15.200',
 r2=dict(center_post=S2['center_post'], p10_out=S2['p10_out'], p50_out=S2['p50_out'], p90_out=S2['p90_out'], pct_weight_below_price=S2['pct_weight_below_price'], label=S2['label']),
 r1=S2.get('r1'), zone_old=S2.get('zone_old'),
 control_r2_reproduced=dict(C, fn_equiv_max_abs_diff=O['control_fn_max_abs_diff']),
 bridge_r2_to_r3=bridge, corrections_check=corrections,
 assumptions=[
  dict(item='r = 13,50%', basis=A['r_rule'] + f"; dep 06/11 = {O['dep_asof']['rate']:.4f} ({O['dep_asof']['rate_source']})", source='deposit_rate_vn.effective_deposit_rate'),
  dict(item='Gia tham chieu 15.200 (dong cua 06/11/2026)', basis='tav2_bq.ticker Price', source='calc_r3/px_ddv_r3.sql -> px_ddv_r3_20261106.csv'),
  dict(item='Tien rong 1.108,0 ty theo so', basis=A['nc_base_basis'], source='BCTC rieng Q3/2026 (dd_DDV_20261026/src/en_p1.txt)'),
  dict(item='Duong LN 2027 -185/+107/+373, trong so 0,45/0,40/0,15', basis=A['scn_np27_weights_basis'], source='dd_DDV_reweight_20261028/REPORT.md §2-3; BCTC Q3'),
  dict(item='Khong he so giua chu ky theo kich ban; truc 0,8..1,2 deu', basis=A['mid_coef_basis'], source='bq_hist_out.csv'),
  dict(item='Bien LN chu ky 4,052% (gop 2015-25)', basis='Sum NP / Sum DT 44 quy', source='BQ ticker_financial (calc/bq_hist_out.csv)'),
  dict(item='DT chuan hoa 5.652 ty', basis=A['rev_norm_basis'], source='calc/bq_hist_out.csv'),
  dict(item='Tru lai gui khoi LN giua chu ky: 70,9/35,4/0 (0,25/0,5/0,25)', basis=A['int_ded_basis'], source='BCTC Q3; bq_cash_hist_out.csv; dd_DDV_20261026/src/vnd.txt dong 971-975'),
  dict(item='RONIC = Ke', basis=A['ronic_basis'], source='ADDENDUM_5F.md'),
  dict(item='g = 3%', basis='[UL] giu tu r1/r2', source='calc/model.py'),
  dict(item='Q4/2026 -54,4/-4,4/+45,6 ty', basis=A['q4_basis'], source='BCTC Q3/2026'),
  dict(item='Liven 217 ty theo so', basis=A['liven_basis'], source='BCTC Q3/2026'),
  dict(item='Lai huy dong -50/0/+50bp (0,25/0,5/0,25)', basis='[UL] truc doi xung', source='common_r2.R_AXIS'),
  dict(item='CK = sigma x sqrt(Q/ADV), co 5 ty ngoai vung hieu chinh (Q/ADV 40%)', basis='luat can bac hai, Y=1 [UL]', source='px_ddv_r3_20261106.csv')],
 axes_included=['duong S/DAP 2027 (hai chieu)', 'LN giua chu ky 0,8..1,2 (hai chieu)', 'lai huy dong (hai chieu)', 'LN loi Q4/2026 +-50 quanh Q3 that (hai chieu)',
                'khoan tru lai gui lich su 70,9/35,4/0 (hai chieu quanh trung diem)'],
 axes_excluded=[dict(axis='Liven 217 mat', reason='khong co van ban no qua han => do nhay alternatives.liven_p10 (-146)'),
                dict(axis='DT chuan hoa', reason='truc MULTS 0,8..1,2 da phu +-20% muc LN; them truc DT la dem doi => do nhay hai chieu rev_avg2125 / rev_ltm'),
                dict(axis='von luu dong', reason='base = so sach; 3 bien the bao song song (nc_*)'),
                dict(axis='bai thach cao / dinh chi Dinh Vu', reason='khong co du lieu bien do/xac suat; WARNING + HARD ABANDON'),
                dict(axis='gia chuyen giao apatit (Vinachem)', reason='khong co du lieu gia chuyen giao; WARNING')],
 base_adjustments=[dict(item='khong co khoan lech khoi so sach trong base (tien rong, Liven theo so)', effect_dong_per_share=0, basis='luat 03/11 + TOP5B #1, #4', source='BCTC Q3/2026'),
                   dict(item='tru lai gui (trung diem 35,4 ty/nam) khoi LN giua chu ky — khong phai lech so sach ma tranh tinh doi tien rong', effect_dong_per_share=None, basis=A['int_ded_basis'], source='BCTC Q3; BQ; VND')],
 headline_vs_alternatives=dict(headline=dict(center_post=H['center_post'], p10_out=H['p10'], p50_out=H['p50'], p90_out=H['p90'], pct_weight_below_price=H['below'], label=H['label']),
                               **{k: row(k) for k in alt}),
 implied_by_price=dict(O['implied'], note=('gia 15.200 = tam sau CK neu LN giua chu ky (truoc tru lai) = {:.1f} ty thay {:.1f} (x{:.3f}, tuong duong DT chuan hoa {:.0f} o bien 4,05%) '
                                            'hoac r = {:.2%} (lai huy dong 12T {:.2%})').format(O['implied']['implied_npm_x_rev_ty'], A['rev_norm_ty'] * O['npm_cycle'], O['implied']['scale_on_rev'],
                                                                                                O['implied']['implied_rev_at_npm_cycle'], O['implied']['r_implied'], O['implied']['r_implied_dep12'])),
 r_sens_post=dict(O['r_sens_post'], base=H['center_post']),
 gordon_roe_xcheck=dict(O['gordon_xcheck'], cash_capitalized_variant=row('xcheck_cash_capitalized'),
                        note='ROE gom lai gui tren VCSH BCTC 2.208,2 = 10,4% < r; ROE loi tren VCSH tru tien rong = 17,6%. Neu tien bi giu lai chi sinh lai gui (khong theo menh gia) tam 11.555 TREN — kiem cheo, khong vao base (quy uoc tien theo so moi ma)'),
 center_vs_p50_note=center_vs_p50,
 change_reason=('Vong 3 (TOP5B 08/11): tien rong theo so (bo chuan hoa VLD mot chan), bo he so giua chu ky Bobby, RONIC=Ke, Liven ra khoi base, Q4 doi xung, '
                'DT chuan hoa = FY2025, khoan tru lai gui thanh truc 70,9/35,4/0; tam {} -> {} ({:+.1%}), nhan TRONG giu').format(f(S2['center_post']), f(H['center_post']), H['center_post'] / S2['center_post'] - 1),
 warnings=S2['warnings'] + ['Tien rong 1.108 ty bi giu trong cong ty co dong lon Vinachem 64%: neu khong phan phoi, kiem cheo von hoa lai gui cho tam 11.555 (TREN) — rui ro "tien bi nhot"'],
 open_issues=['Thu nhap tai chinh kiem toan 2015-22 (de chot khoan tru lai gui; hien la truc 70,9/35,4/0)', 'Duong S 2027 / do doc bien 2,44 (2 diem hieu chuan)',
              'DT chuan hoa: TB 2021-25 cho TREN vung (12.452)', 'NH3 khong co chuoi BQ', 'Room ngoai', 'BCTC Q4/2026', 'Chua tra truc tiep UBCKNN/HNX'],
 new_data_obs=S2.get('new_data_obs', []) + ['08/11/2026: khong tra moi tin phap ly (job chi kiem dinh chinh); gia 06/11 BQ 15.200'],
 fear_buy_25=S2.get('fear_buy_25'), free_float=S2.get('free_float'), free_float_src=S2.get('free_float_src'),
 lock_md5='calc_r3/LOCK_md5.txt (phan 1 dau vao+gia dinh chot truoc khi chay; 1b them bien the kiem cheo; 2 dau ra)',
 measured_by='calc_r3/model_r3.py -> model_r3_out.json (2 lan cmp trung byte) -> make_summary_r3.py')
json.dump(out, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, sort_keys=False)
print('ok', out['center_post'], out['p10_out'], out['p90_out'], out['label'], round(out['center_change_vs_old']))
