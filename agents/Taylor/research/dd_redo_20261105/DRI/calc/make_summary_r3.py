"""SUMMARY.json vong 3 DRI tu dri_redo_r3_out.json + ../calc_5f/moat_sens_5f_r3_out.json (backup r2: ../SUMMARY_r2.json). Chay: python3 make_summary_r3.py"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
o = json.load(open(os.path.join(H, 'dri_redo_r3_out.json'))); r2 = json.load(open(os.path.join(H, '..', 'SUMMARY_r2.json')))
m5 = json.load(open(os.path.join(H, '..', 'calc_5f', 'moat_sens_5f_r3_out.json')))
A = json.load(open(os.path.join(H, 'assumptions_r3.json'), encoding='utf-8'))
P, Q, S, alt, imp = o['post'], o['pre'], o['sens_mean_post'], o['alternatives'], o['implied_by_price']
px = o['price']; R = lambda x: round(x)
def V(lab, s, note): return dict(variant=lab, center=R(s['mean']), p10=R(s['p10']), p50=R(s['p50']), p90=R(s['p90']), pct_weight_below_price=round(s['below'], 4), n=s['n'], note=note)
br = o['bridge_r2_to_r3']
WHY = ['ban r2 (gia 13.500 @04/11)', 'cua so thanh khoan 25/11/2025..06/11/2026: CK 5 ty 1,997% -> 2,00%; r khong doi 13,5%',
       'dinh chinh 1 skeptic (CHAP NHAN): trong so 0,20 la nhan dinh [UL], luat 20 + STANDARD_r2 dieu 3 => tai canh NPV0; nhanh KINH TE sang do nhay',
       'dinh chinh 2 (CHAP NHAN huong, SUA cach mo hinh): BCTN25 tr.44 khoi thanh ly vi khong dam bao mat do => q<1; q CHI cho khoi, tong dien tich giu A0 (ban skeptic q toan vuon vi pham tong dien tich 8.592 ha)',
       'dinh chinh 3 (CHAP NHAN MOT PHAN): nguon luat 10% CO (Wendy Luat 67/NA + DTA 1996 Dieu 10) => SUMMARY r2 "chua dan nguon" sai; nhung co so chiu thue = 1-KTPL-TAU => 8,16%, trong dai quan sat 7,0-8,3%',
       'dinh chinh 4 (CHAP NHAN): wp 0,6 = Bobby CYCLICAL_PEAK (nhan dinh) => 0,5 trung tinh; 0,6 sang do nhay']
s = dict(ticker='DRI', round=3, job='Taylor_20261108_153743', asof_price_date=o['price_date'], price=px, price_date=o['price_date'], r=o['r'],
  r_anchor=dict(rate=o['dep'], date=o['dep_src'], asof=A['asof_price'], rule='r = 13,5% + 1,0 x (lai huy dong 12T hieu dung - 7,40%) = 13,50%'),
  center_pre_liq=R(Q['mean']), center_post_liq=R(P['mean']), p10_post=R(P['p10']), p50_post=R(P['p50']), p90_post=R(P['p90']),
  p10_pre=R(Q['p10']), p90_pre=R(Q['p90']), p10_out=R(P['p10']), p50_out=R(P['p50']), p90_out=R(P['p90']), min_out=R(P['min']), max_out=R(P['max']),
  pct_weight_below_price=round(P['below'], 4), n_outcomes=o['n_outcomes'], n_cells=o['n_cells'], liq_disc_5bn=o['ck_ref']['adv250'],
  ck_ref_size=dict(size_vnd=5e9, Y=1.0, disc_adv250=o['ck_ref']['adv250'], disc_adv60=o['ck_ref']['adv60'], q_over_adv250=o['ck_ref']['q_over_adv250'],
     adv250_ty=o['liq']['adv_med'] / 1e9, adv60_ty=o['liq']['adv_60'] / 1e9, window=o['liq']['window'],
     note='HEADLINE o co tham chieu 5 ty (quy uoc fleet); Q/ADV250 0,60x trong vung hieu chinh luat can bac hai'),
  ck_real_sleeve=o['ck_real_sleeve'],
  real_sleeve_headline={k: dict(center=R(v['mean']), p10=R(v['p10']), p50=R(v['p50']), p90=R(v['p90']), pct_weight_below_price=round(v['below'], 4)) for k, v in o['post_real_sleeve'].items()},
  px_vs_center_post=o['px_vs_center_post'], px_vs_p10_post=o['px_vs_p10_post'], px_vs_p90_post=o['px_vs_p90_post'],
  label=o['label'],
  label_note=(f"TRONG vung nhu r2 nhung sat CANH DUOI: gia {px:,.0f} chi cao hon P10 {P['p10']:,.0f} {o['px_vs_p10_post']:+.1%}; "
     f"{P['below']:.1%} trong so ket cuc duoi gia. O co sleeve that 10-40 tr (CK 0,09-0,18%) P10 {o['post_real_sleeve']['10tr']['p10']:,.0f}/{o['post_real_sleeve']['40tr']['p10']:,.0f} > gia => DUOI vung (sat ranh gioi); nhan chinh theo co 5 ty. Luat 4 (gia <= 0,85 x tam = {o['rule4_threshold']:,.0f}): KHONG dat (cach {px/o['rule4_threshold']-1:+.1%})."),
  center_vs_p50_note=(f"tam = ky vong luoi {Q['mean']:,.0f} truoc CK / {P['mean']:,.0f} sau CK; P50 ket cuc {P['p50']:,.0f} sau CK; gia tri tai tham so trung tam "
     f"(mid TB, L27, q 0,85, wp 0,5) {o['center_param_pre']:,.0f} truoc CK (cao hon tam vi L22 va mid P25 keo xuong manh hon L32/P75 keo len). "
     f"Vung duoi P10 gom khoi mid P25 x duong PEAK (L22/L27, moi muc q) - khong con nhanh trong so nho nao (nhu KINH TE 0,20 r2) chi phoi duoi."),
  axes_included=['mid RSS3 thuc 2014-01..2026-09 P25/TB/P75 (.25/.5/.25)', 'doi cao L 22/27/32 (.25/.5/.25) [gia dinh, khong co dinh muc nguon]',
     'mat do q khoi thanh ly 1.975,23 ha 0,7/0,85/1 (.25/.5/.25) [UL do lon; huong = BCTN25 tr.44]', 'ket cuc trong o: duong gia PEAK/MID wp 0,5/0,5'],
  axes_excluded=[dict(axis='r', reason='co dinh 13,5% theo luat 21; do nhay +-50/100bp rieng'),
     dict(axis='nhanh NQ15-KINH TE (tai canh pha gia tri)', reason=f"nhan dinh khong du lieu (luat 20) -> do nhay: w 0,1/0,2/0,3 -> {alt['nhanh KINH TE 0.1 (q=1 o nhanh KINH TE)']['mean']:,.0f}/{alt['nhanh KINH TE 0.2 (q=1 o nhanh KINH TE)']['mean']:,.0f}/{alt['nhanh KINH TE 0.3 (q=1 o nhanh KINH TE)']['mean']:,.0f}; 1,0 -> {alt['chi nhanh KINH TE 1,0 (tai canh pha gia tri 100%)']['mean']:,.0f}"),
     dict(axis='ban cu giu vuon toi L27 (bo qua NQ15)', reason=f"NQ HDQT 15 Dieu 4 la du lieu; song song {alt['ban cu giu vuon L27 (bo qua NQ15) 0,8 + bi buoc 0,2']['mean']:,.0f}"),
     dict(axis='wht', reason=f"co dinh 8,16% co co so; 10% -> {S['wht 10% phang (r2)']:,.0f}, 7,04% -> {S['wht 7.04% (quan sat 2025)']:,.0f}"),
     dict(axis='FCF = 90% LN loi', reason=f"[UL]; 80% {S['FCF/LN loi 80% (base 90% [UL])']:,.0f} / 100% {S['FCF/LN loi 100% (base 90% [UL])']:,.0f} (doi xung +-936)"),
     dict(axis='haircut khoan vay Dakruco / tien Lao', reason='khong co co so du lieu -> WARNING + do nhay'),
     dict(axis='ty gia LAK cho tien dau gia', reason=f"co dinh 1,1404 (BCTC Q3); +-10% -> +-{S['gia go LAK +10%']-P['mean']:,.0f}")],
  base_adjustments=[dict(item='Khoan vay Dakruco 40 ty', effect_dong_per_share=0, basis='so sach day du (80->40 ty H1, lai ~9%, TSDB 6 tr cp DRI); WARNING tien le gia han', source='BCTC HN Q3/2026'),
     dict(item='Tien tai Lao ~197 ty', effect_dong_per_share=0, basis='so sach', source='BCTC HN Q3/2026'),
     dict(item='Thue chuyen LN Lao (wht)', effect_dong_per_share=R(P['mean'] - S['wht 10% phang (r2)']), basis=A['wht_basis'], source='dri_val_supply_adj_r2_20261027/REPORT.md:106; r3/model.py WHT_OBS; BCTC3 hn_29'),
     dict(item='Gia go thanh ly NQ15', effect_dong_per_share=R(P['mean'] - S['gia go cu 20,87 tr/ha']), basis='gia khoi diem 36 tr LAK/ha x 1,1404 = 41,05 tr VND/ha; ap moi ha thanh ly', source='NQ HDQT 15 Dieu 4 (04/11/2026); ty gia BCTC HN Q3/2026 hn_01'),
     dict(item='Mat do q khoi thanh ly', effect_dong_per_share=R(P['mean'] - alt['q=1 (khong truc mat do, nhu r2)']['mean']), basis=A['q_basis'], source='BCTN 2025 tr.44 (trich dri_val_supply_adj_r4_20261027/REPORT.md:194)'),
     dict(item='XDCB do dang 72,71 ty', effect_dong_per_share=993, basis='so sach (NPV0)', source='BCTC HN Q3 ma 252')],
  assumptions=[dict(item='r', value=o['r'], basis=f"deposit_rate_vn.effective_deposit_rate({A['asof_price']}) = {o['dep']:.2%} ({o['dep_src']}) => 13,50%"),
     dict(item='gia tham chieu', value=px, basis='dong cua 06/11/2026 tav2_bq.ticker (Close=Price=13.100; calc/r3data/px_dri_20261106.csv, sql px_dri_r3.sql)'),
     dict(item='doc NQ15', value='NPV0 1,0', basis=A['branch_basis']),
     dict(item='mat do q khoi', value=A['q_block'], basis=A['q_basis']),
     dict(item='wht', value=o['wht']['base'], basis=A['wht_basis']),
     dict(item='wp PEAK', value=A['wp_peak'], basis=A['wp_basis']),
     dict(item='mid RSS3', value=o['mids'], basis='RSS3 thuc USD2025/kg 2014-01..2026-09 (snapshot 03/11), P25/TB/P75 .25/.5/.25 (skeptic R4 doi xung)'),
     dict(item='doi cao L', value=[22, 27, 32], basis='gia dinh, khong co dinh muc nguon; .25/.5/.25'),
     dict(item='FCF/LN loi', value=0.9, basis='[UL] engine r3; do nhay doi xung 80/100%'),
     dict(item='LAK/VND', value=o['lak_vnd'], basis=A['lak_basis']),
     dict(item='CK', value=o['ck_ref']['adv250'], basis='luat can bac hai Y=1,0, 5 ty, ADV250 trung vi Price x Volume, sigma log-return Close 250 phien'),
     dict(item='LOCK', value='calc/LOCK_r3_md5.txt', basis='assumptions_r3.json + script + upstream md5 chot TRUOC lan chay dau (so gia)')],
  headline_vs_alternatives=[V('HEADLINE r3 (NPV0, q khoi .7/.85/1, wht 8,16%, wp 0,5)', P, 'mo hinh co so sau dinh chinh'),
     V('skeptic: q toan vuon cu (dien tich A0/q)', alt['skeptic: q toan vuon cu (dien tich A0/q)'], 'cach mo hinh cua skeptic; vi pham tong dien tich 8.592 ha'),
     V('q=1 (khong truc mat do)', alt['q=1 (khong truc mat do, nhu r2)'], 'nhu r2 ve mat do'),
     V('q khoi 0,5', alt['q khoi 0,5 co dinh'], 'duoi trong so de nghi'),
     V('nhanh KINH TE 0,2 (nhu r2)', alt['nhanh KINH TE 0.2 (q=1 o nhanh KINH TE)'], 'trong so r2 [UL]'),
     V('chi nhanh KINH TE 1,0', alt['chi nhanh KINH TE 1,0 (tai canh pha gia tri 100%)'], 'tai canh pha gia tri 100%'),
     V('ban cu giu vuon L27 0,8 + bi buoc 0,2', alt['ban cu giu vuon L27 (bo qua NQ15) 0,8 + bi buoc 0,2'], 'bo qua NQ15'),
     V('moat NONE_half (bien ve 1/2 gap nganh)', m5['NONE_half'], 'do nhay rui ro, KHONG headline (quy uoc 08/11)'),
     V('moat NONE (bien ve trung vi nganh 11,70pp)', m5['NONE'], 'do nhay rui ro, KHONG headline (quy uoc 08/11)')],
  implied_by_price=dict(price=px, FCF_over_core_NI=imp['FCF/LN loi'], deposit_rate_12m=imp['lai huy dong 12T'],
     r_implied=0.135 + imp['lai huy dong 12T'] - 0.074, econ_branch_weight=imp['trong so nhanh KINH TE'], q_block=imp['q khoi co dinh'], wp_peak=imp['wp PEAK'],
     note=(f"Gia 13.100 ngu y (mot tham so, cac truc khac = headline): FCF/LN loi {imp['FCF/LN loi']:.0%} (base 90%), hoac lai huy dong 12T {imp['lai huy dong 12T']:.1%} (r {0.135 + imp['lai huy dong 12T'] - 0.074:.1%}). "
       f"KHONG dat duoc bang rieng trong so nhanh KINH TE (100% -> {alt['chi nhanh KINH TE 1,0 (tai canh pha gia tri 100%)']['mean']:,.0f}), q khoi (q=1 -> {alt['q=1 (khong truc mat do, nhu r2)']['mean']:,.0f}) hay wp (1,0 -> {S['wp PEAK 1.0']:,.0f}). "
       f"Bien ve trung vi nganh (moat NONE) cho {m5['NONE']['mean']:,.0f} < gia => gia hop voi gia thiet loi the gia thanh DRI mat ~3/4.")),
  bridge_r2_to_r3=[dict(step=b['step'], center_post=R(b['center_post']), delta=R(b['delta']), why=w) for b, w in zip(br, WHY)],
  corrections_check=[dict(n=1, verdict='CHAP NHAN', effect=R(br[2]['delta'])), dict(n=2, verdict='CHAP NHAN huong; sua cach mo hinh (q chi cho khoi)', effect=R(br[3]['delta']), skeptic_repro=dict(o['skeptic_repro_eng_q'], note='skeptic 14.902/15.519/16.348 @q .85/.7/.5; tai lap 14.855/15.502/16.617 - KHONG trung (lech -47/-17/+269), spec luoi cua skeptic khong ro')),
     dict(n=3, verdict='CHAP NHAN MOT PHAN (nguon luat co; co so chiu thue sai)', effect=R(br[4]['delta'])), dict(n=4, verdict='CHAP NHAN', effect=R(br[5]['delta'])),
     dict(n=5, verdict='CHAP NHAN: gia 06/11 13.100; price_date dien; FX LAK dan nguon BCTC Q3 hn_01 (0,8769 LAK/VND)'), dict(n=6, verdict='CHAP NHAN: them WARNING'), dict(n=7, verdict='CHAP NHAN: ghi ro thien lech xac nhan')],
  grid_desc=(f"Luoi MUC KET CUC n={o['n_outcomes']} ({o['n_cells']} o x 2 duong gia): doc NQ15-NPV0 x mid 3 x L 3 x q khoi 3; ket cuc PEAK 0,5/MID 0,5. "
     "r 13,5%. Base: khoan vay Dakruco, tien Lao theo so sach; thanh ly 1.975,23 ha 2027-30 gia khoi diem NQ15; tai canh NPV0; wht 10%x(1-KTPL-TAU). Phan vi _shared/wpct.py. Sau CK = x(1 - CK 5 ty 2,00%)."),
  zone_old=r2['zone_old'], r1=r2['r1'],
  r2=dict(center_post=r2['center_post_liq'], p10=r2['p10_post'], p50=r2['p50_post'], p90=r2['p90_post'], label=r2['label'], price=r2['price'], pct_below=r2['pct_weight_below_price']),
  center_change_vs_r2=P['mean'] / r2['center_post_liq'] - 1, center_change_pct=P['mean'] / r2['zone_old']['center'] - 1,
  center_change_note='center_change_pct = so voi tam so muc gia cu (14.360, dd_price_zones rev 2); center_change_vs_r2 = so voi tam r2 14.092',
  change_reason=(f"Tam sau CK r2 14.092 -> r3 {P['mean']:,.0f} ({P['mean']-r2['center_post_liq']:+,.0f}): bo nhanh KINH TE {br[2]['delta']:+,.0f}; mat do q khoi {br[3]['delta']:+,.0f}; "
     f"wht co so chiu thue {br[4]['delta']:+,.0f}; wp 0,5 {br[5]['delta']:+,.0f}; CK du lieu 06/11 {br[1]['delta']:+,.0f}. Gia tham chieu 13.500 -> 13.100."),
  warnings=[w for w in r2['warnings'] if 'dang tra dung han' not in w] + ["Cho Dakruco vay con 40 ty (TSDB 6 tr cp DRI) - base theo so sach; da tung GIA HAN (xem duoi), khong viet 'tra dung han'",
     "Tien le: DRI da GIA HAN khoan vay 40 ty cho cong ty me Dakruco (Thoi bao Tai chinh, thoibaotaichinhvietnam.vn ...-158125.html; trich data/intraday_watch/crisis_dd/DRI_2026-11-02/notes/daily_day4_taylor.md:42) - mau thuan cach viet 'dang tra dung han' cua r2; mat trang -536, haircut 50% -268 (do nhay)",
     "Giay nhuong dat 2016 (01616/KD/DDT4) CHUA xac minh (SKEPTIC_R4_20261103 muc 4)",
     "Thien lech xac nhan: DRI da BAN HET 02/11. r2 chi ap thong tin moi (NQ15) theo chieu giam va bo qua bang chung mat do co san; r3 khong neo vao quyet dinh ban - dinh gia doc lap, ket qua tam > gia ban",
     "LAK yeu ~6% trong 9T/2026 (0,8252 -> 0,8769 LAK/VND); gia khoi diem dau gia co dinh bang LAK 4 nam -> rui ro ty gia (+-10% = +-164 d/cp)"],
  open_issues=["Hop dong to nhuong 01616/KD/DDT4 chua xac minh", "Doi cao L 22/27/32 la gia dinh", "Do lon mat do khoi thanh ly (q) chua co so do - chi co huong (BCTN25 tr.44)",
     "Nguon luat Lao 67/NA la nguon thu cap (Wendy); co so chiu thue wht that (LN chuyen ve) chua tach duoc tu BCTC",
     "So skeptic q (14.902/15.519/16.348) chua tai lap dung - tai lap 14.855/15.502/16.617", "Gia trung dau gia thuc (>= khoi diem) va danh tinh ben mua", "SXKD T10 (~10/11)", "HOSE Q4/2026"],
  fear_buy_2_5=(f"Ho so crisis-DD DRI: da ban het 02/11. O gia 06/11 13.100: luat 4 can gia <= {o['rule4_threshold']:,.0f} -> KHONG dat (cach {px/o['rule4_threshold']-1:+.1%}) => KHONG du dieu kien §2.5. "
     "Ghi chu: nguong nay sat gia, nhung moat NONE (bien ve nganh) cho tam < gia => khong co bien an toan neu loi the gia thanh khong ben."),
  files=dict(calc='calc/dri_redo_r3.py', out='calc/dri_redo_r3_out.txt', json='calc/dri_redo_r3_out.json', grid='calc/grid_dri_redo_r3.csv', assumptions='calc/assumptions_r3.json',
     lock='calc/LOCK_r3_md5.txt', moat='calc_5f/moat_sens_5f_r3_out.txt', report='REPORT_r3.md'))
json.dump(s, open(os.path.join(H, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps({k: s[k] for k in ('center_post_liq', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label', 'center_change_vs_r2', 'center_change_pct')}, default=float))
