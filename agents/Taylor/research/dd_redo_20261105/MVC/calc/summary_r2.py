"""SUMMARY.json vong 2 MVC tu mvc_redo_r2_out.json."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
o = json.load(open(os.path.join(HERE, 'mvc_redo_r2_out.json'))); r1 = json.load(open(os.path.join(HERE, '..', 'SUMMARY_r1.json')))
g9 = json.load(open(os.path.join(HERE, '../../../dd_MVC_20261103/r9/calc/model_r9_out.json')))
P, Q, T = o['post'], o['pre'], o['tornado']
s = dict(ticker='MVC', round=2, job='Taylor_20261105_020023', asof_price_date=o['price_date'], price=o['price'], r=o['r'], r_anchor=r1['r_anchor'],
  center_pre_liq=round(Q['mean']), center_post_liq=round(P['mean']), p10_post=round(P['p10']), p50_post=round(P['p50']), p90_post=round(P['p90']),
  p10_pre=round(Q['p10']), p90_pre=round(Q['p90']), p10_out=round(P['p10']), p50_out=round(P['p50']), p90_out=round(P['p90']), min_out=round(P['min']),
  pct_weight_below_price=o['pct_weight_below_price'], n_outcomes=o['n_outcomes'], n_cells=o['n_cells'], liq_disc_5bn=o['ck_ref']['adv250'],
  ck_ref_size=dict(size_vnd=5e9, Y=1.0, disc_adv250=o['ck_ref']['adv250'], disc_adv60=o['ck_ref']['adv60'], q_over_adv250=o['ck_ref']['q_over_adv250'],
     disc_1bn=o['ck_ref']['disc_1bn'], disc_1bn_adv60=o['ck_ref']['disc_1bn_adv60'],
     note='5 ty = quy uoc fleet nhung Q/ADV250 11,3x (ADV60 26x) = NGOAI SUY ngoai vung hieu chinh luat can bac hai; ban 1 ty (Q/ADV 2,3x) bao song song',
     post_1bn=dict(center=round(o['post_1bn']['mean']), p10=round(o['post_1bn']['p10']), p50=round(o['post_1bn']['p50']), p90=round(o['post_1bn']['p90']), below=o['post_1bn']['below'], label=o['label_1bn'])),
  ck_real_sleeve=o['ck_real_sleeve'], px_vs_center_post=o['px_vs_center_post'], px_vs_p10_post=o['px_vs_p10_post'], px_vs_p90_post=o['px_vs_p90_post'],
  label=o['label'], label_note='TRONG vung o ca 5 ty va 1 ty. So voi so cu (P25-P75, nhan RE CO DIEU KIEN) nhan doi do DINH NGHIA vung. Luat 4: KHONG dat.',
  center_vs_p50_note=(f"tam = ky vong luoi {Q['mean']:,.0f} truoc CK; gia tri tai tham so trung tam (khong tre) {o['center_param_nodelay']:,.0f}; P50 ket cuc {Q['p50']:,.0f}. "
     f"P90 {Q['p90']:,.0f} do nhanh STRUCTURAL (trong so 0,20) quyet dinh (trung vi nhanh sau CK {o['branch_post']['STRUCTURAL']['p50']:,.0f}); "
     f"w_STRUCT 0,15 -> P90 sau CK {o['sens_w_structural_post']['0.15']['p90']:,.0f}, 0,10 -> {o['sens_w_structural_post']['0.10']['p90']:,.0f}. "
     "So o: moi nhanh 1.458 o x 8 ket cuc (STRUCTURAL bat bien theo VR/ADMIN/tran/bien TL nhung van dem du de trong so dung)."),
  axes_included=['trang thai bien 0,20/0,45/0,35 (Bobby)', 'chi phi Tan Lap ca 0,85/1,0/1,15', 'REL gia TL/NNC 0,88/0,91/0,95', 'SL nam thuong 3 muc',
     'han GP Tan Lap 2035/W/2045', 'anh xa ADMIN 3', 'bien chu ky Tan Lap 25%/30%/~NNC deu [UL] (DUA LAI)', 'tran chu ky branch/SL 1,40 (MOI, nhu NNC r2)',
     'ket cuc trong o: 4 kich ban W0 x 2 duong gia PW0'],
  axes_excluded=[dict(axis='r', reason='co dinh 13,5%; do nhay rieng'),
     dict(axis='tre GP mo moi (Bobby F6)', reason=f"nhan dinh, trai ke hoach DHDCD 'khai thac 2028' -> khoi base (luat 3); do nhay {T['chi tre mo moi MVC']['d']:+,.0f}"),
     dict(axis='mo moi hai phia (upside + NPV gia xau)', reason=f"lech NPV0 cua du an moi (luat 20) khong co IRR du lieu; do nhay {T['mo moi hai phia (upside + NPV gia xau; lech NPV0)']['d']:+,.0f}")],
  base_adjustments=[dict(item='Hai mo moi da chi 438,4 ty', effect_dong_per_share=0, basis='so sach, NPV0 that (vong 2 KHONG tru tre GP; vong 1 tru -527)', source='BCTC HN Q3/2026 XDCB/tra truoc'),
     dict(item='Dat 30 ty; cum CN; mua NNC len 51%', effect_dong_per_share=0, basis='so sach / NPV0', source='DHDCD 2026; SKEPTIC4/R7'),
     dict(item='Co phan NNC 44,07% giai dong thoi', effect_dong_per_share=None, basis='V_NNC tu mo hinh NNC r6 (khong tre GP, cung truc), khong dung gia thi truong', source='nnc_model_r6')],
  gordon=dict(roe_blend=g9['gordon']['tron']['roe'], ps=round(g9['gordon']['tron']['ps']), roe_implied_center_r9=g9['roe_implied_tam'],
     note='mot bien the: MVC no rong, khong co LN lai tien gui dang ke de tach (so r9, co tre GP)'),
  grid_desc=(f"Luoi MUC KET CUC n={o['n_outcomes']} ({o['n_cells']} o x 8). Truc: trang thai x ca 3 x REL 3 x SL 3 x han GP TL 3 x ADMIN 3 x bien TL 3 x tran 2; "
     "trong so o = xac suat trang thai x deu; ket cuc W0 x PW0; r 13,5%; base khong tre GP. Phan vi _shared/wpct.py. Sau CK = x(1 - CK 5 ty)."),
  zone_old=r1['zone_old'], r1=dict(center_post=r1['center_post_liq'], p10=r1['p10_post'], p50=r1['p50_post'], p90=r1['p90_post'], label=r1['label']),
  center_change_pct=P['mean'] / r1['zone_old']['center'] - 1,
  change_reason=(f"Tam sau CK 15.082 -> {P['mean']:,.0f}: bo tre GP (+{-T['co tre GP ky vong (Bobby F6) mo moi + CIP NNC']['d']:,.0f} tai tham so) bu boi truc bien Tan Lap (-) va tran (-); "
     f"vong 1 'tam' la gia tri tham so, vong 2 la ky vong luoi. P10 11.941 -> {P['p10']:,.0f} chu yeu do MUC KET CUC; {o['pct_weight_below_price']:.1%} ket cuc duoi gia (vong 1: 40,3% o)."),
  warnings=["So huu cheo MVC 44,07% NNC <-> NNC 10,3% MVC; Chu tich HDQT MVC = Chu tich Thanh Le va NNC; truong BKS MVC = TGD Thanh Le",
     "Uy quyen DHDCD MVC 2026 mua NNC len 51% (gia/doi tac chua cong bo; ~1,52 tr cp, uoc ~72 ty theo SKEPTIC_20261103) - giao dich ben lien quan",
     "Neu MVC >=51% NNC: Luat DN D195 co the buoc NNC thoai 10,3% MVC (~142 ty ~ 325-760 phien ADV MVC) -> ap luc cung - CAN legal-vn xac minh",
     "DHDCD 2026 duyet cum cong nghiep toi 500 ty (ngoai 1.500 ty mo moi): no rong ~1,4-1,5 nghin ty truoc doanh thu mo, D/E ~0,9-1,0 (SKEPTIC_20261103 #1, CHUA DONG)",
     "Du no BIDV 452 ty > han muc 350 ty hop dong da cong bo; tam ung 60,6 ty chua thuyet minh doi tuong",
     "Thanh khoan rat thap: ADV250 0,44 ty, ADV60 0,19 ty; thoat 5 ty 113/57 phien",
     "Tra cuu 'xu phat/khoi to MVC 2026': WebSearch 05/11/2026 khong thay; Simplize ghi MVC so huu NNC 43,55% (lech 44,07%, chua doi soat)"],
  open_issues=["Bien chu ky mang da Tan Lap (khong co bao cao bo phan) - nay la truc", "Han GP Tan Lap, BOT", "Free float uoc 30,2%", "Xac suat trang thai la nhan dinh Bobby",
     "HD tin dung BIDV moi + co cau 1.500 ty", "Ty le so huu NNC 44,07% vs 43,55%"],
  fear_buy_2_5='KHONG du dieu kien sleeve fear-buy §2.5 (khong co su kien so hai; luat 4 khong dat)')
json.dump(s, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps({k: s[k] for k in ('center_post_liq', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label', 'center_change_pct')}, default=float))
