import json, os, hashlib
H = os.path.dirname(os.path.abspath(__file__)); M = json.load(open(os.path.join(H, 'model_out.json')))
amd5 = hashlib.md5(open(os.path.join(H, 'assumptions.json'), 'rb').read()).hexdigest()
p = M['post']['5ty']; px = M['price']
S = dict(ticker='CSV', asof_price_date=M['price_date'], price=px, r=M['r'],
 r_anchor=dict(r=0.135, rate=0.074, source='cctg_12m(2026-11-02)', rule='r = 13,5% + 1,0 x (dep_12T - 7,40%)'),
 kind='expected_weighted', center_pre_liq=M['pre']['center'], center_post_liq=p['center'],
 p10_post=p['p10'], p25_post=p['p25'], p50_post=p['p50'], p75_post=p['p75'], p90_post=p['p90'],
 p10_pre=M['pre']['p10'], p50_pre=M['pre']['p50'], p90_pre=M['pre']['p90'],
 liq_disc_5ty=M['liq']['ck']['5ty'], px_vs_center_post=px / p['center'] - 1, px_vs_p10_post=px / p['p10'] - 1, px_vs_p90_post=px / p['p90'] - 1,
 label=M['label']['5ty'], label_by_size={k: dict(center=v['center'], p10=v['p10'], p90=v['p90'], label=M['label'][k], ck=M['liq']['ck'][k]) for k, v in M['post'].items()},
 rule4=M['rule4'], pct_weight_below_price=M['pct_weight_below_price'], grid_n=p['n'],
 grid_desc='27 ket cuc (r2) = kich ban LN me chuan hoa XAU/CO_SO/TOT 179,7/235,0/294,5 ty (0,25/0,5/0,25) x dE +-10% x NPV Nhon Trach -20/0/+20% (0,2/0,6/0,2); gian doan CHUYEN KHOI BASE (E2) thanh do nhay; RONIC=Ke; + tien rong 525,6 ty + phan da chi Nhon Trach 346,484 ty gia von (E1) - CDKKS 50,0',
 scen_pre=M['scen_pre'], central_param_value_pre=M['central_param'], sens_r=M['sens_r'], sens=M['sens'],
 implied_by_price=dict(r=M['r_implied'], dep12_implied=M['dep12_implied'], E_parent_perpetual_ty=M['E_parent_implied_ty']),
 lag_surprise=dict(q3_26_np_parent=M['q3_26'], q3_25=M['q3_25'], yoy_q3=M['q3_26']/M['q3_25']-1, q2_yoy=M['q2_26']/M['q2_25']-1, nine_m_yoy=M['nine_m26']/M['nine_m25']-1,
   driver='gia H2SO4 +249% (Q2) / +289% (Q3) + phot pho vang; hang hoa thuong mai 9T GP 73,4 vs 15,4 ty', durable=False, one_off_est_ty='60-85 (uoc luong)'),
 ck_ref_size=dict(size='5 ty', adv250=M['liq']['adv250'], adv60=M['liq']['adv60'], sigma_d=M['liq']['sigma_d'], q_over_adv250=M['liq']['exit']['5ty']['q_over_adv'], note='ngoai vung hieu chinh (Q/ADV 54%)'),
 sizing=dict(max_one_shot_vnd=1e9, exit=M['liq']['exit'], note='<=1 ty/lan (~11% ADV250, ~17% ADV60); free float <=35% (Nha nuoc 65,0%)'),
 moat=dict(tier='NARROW', type='COST/SCALE', source='data/moat_tags.csv asof 2026-06-05 (tai dung)', durable=False, roe_min5y=0.1366, roic_min5y=0.1426,
   risk1_proposed='di doi bat buoc BH1 -> Nhon Trach 1.840 ty ~ von CSH + cong suat xut noi dia ~x2 2027-30; lai 2026 la cu soc axit/phot pho tam thoi'),
 auto_flags=dict(IDIOCRASH_20260727='NHIEU (VNINDEX -1,0%, khong CBTT, hoi +3,75% phien sau)', DCF_CHEAP_29479='NHIEU ve ket luan (thu nhap dinh chu ky)', ROE5Y_18_3='that nhung gom dinh 2022; ROE_Min5Y 13,66% ~ Ke', ADV3T_6ty='that'),
 warnings=['Cuong che thao do BH1 QD 2408/QD-UBND 07/07/2026; dung NM Tan Binh 2 tu 15/08/2026 (QD 1122/QD-HDQT) - gian doan chuyen tiep KHONG vao base (r2), chi do nhay', 'Du an Nhon Trach ~1.840 ty (632 tu co + ~1.208 vay 10 nam), chua co ngay van hanh dong bo', 'Nha nuoc (Vinachem) 65,0%; free float <=35%', 'Khong chia co tuc tien 2025 (LN trich het vao quy DTPT)', 'UBND TP.HCM thu hoi dat tu nguyen tra lai (CBTT 19/10/2026) - chua doc noi dung'],
 open_issues=['G2 tra truoc nguoi ban 242,4 ty (~200 ty nghi Nhon Trach, CHUA xac nhan -> chi do nhay +1.779 d/cp)', 'G3 hang hoa thuong mai 350 ty la gi', 'G4 lich dung day chuyen BH1 / chay Nhon Trach', 'G5 boi thuong BH1 + dat HCM', 'G6 H2SO4 tu dot luu huynh hay thuong mai', 'E5 co tuc 21,17 ty tra 9T/26 co phai tra CDKKS: chua kiem'],
 fear_buy_eligible_2_5=False, assumptions_file='calc/assumptions.json', assumptions_md5=amd5,
 source_file='src/q3_2026_HN.pdf', lock_md5='calc/LOCK_prerun.txt (truoc chay) + calc/LOCK_post_md5.txt',
 sector_read='kb/data_registry/market-state/sector_read_hoa_chat_xut_clo_20261109.md', round='r2', job='Taylor_20261109_073602', job_r2='Taylor_20261109_083124',
 sens_e=M['sens_e'], spent_book_ty=M['spent_book_ty'], prior_round='SUMMARY_r1.json / REPORT_r1.md (r1: tam 17.273 P10 12.739 P90 21.885 TREN vung)',
 errata=dict(source='ERRATA_r1_skeptic.md', applied=['E1','E2','E3','E4(theo errata, Taylor chua tu kiem ban scan)','E5','E6'],
  E4_note='G1 dong theo errata skeptic: FAC 041/2025 (23/02/2026) va FAC 044/2026 (27/07/2026) chap nhan toan phan. Taylor KHONG tu kiem duoc (PDF scan, khong co cong cu render trong phien).'))
json.dump(S, open(os.path.join(H, '..', 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print(amd5, S['label'], S['center_post_liq'], S['p10_post'], S['p90_post'])
