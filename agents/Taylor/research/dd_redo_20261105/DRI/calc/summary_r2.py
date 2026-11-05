"""SUMMARY.json vong 2 DRI tu dri_redo_r2_out.json."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
o = json.load(open(os.path.join(HERE, 'dri_redo_r2_out.json'))); r1 = json.load(open(os.path.join(HERE, '..', 'SUMMARY_r1.json')))
P, Q, S = o['post'], o['pre'], o['sens_mean_post']; br = o['bridge_point_TB_L27']
s = dict(ticker='DRI', round=2, job='Taylor_20261105_020023', asof_price_date=o['price_date'], price=o['price'], r=o['r'], r_anchor=r1['r_anchor'],
  center_pre_liq=round(Q['mean']), center_post_liq=round(P['mean']), p10_post=round(P['p10']), p50_post=round(P['p50']), p90_post=round(P['p90']),
  p10_pre=round(Q['p10']), p90_pre=round(Q['p90']), p10_out=round(P['p10']), p50_out=round(P['p50']), p90_out=round(P['p90']), min_out=round(P['min']),
  pct_weight_below_price=o['pct_weight_below_price'], n_outcomes=o['n_outcomes'], n_cells=o['n_cells'], liq_disc_5bn=o['ck_ref']['adv250'],
  ck_ref_size=dict(size_vnd=5e9, Y=1.0, disc_adv250=o['ck_ref']['adv250'], disc_adv60=o['ck_ref']['adv60'], q_over_adv250=o['ck_ref']['q_over_adv250'],
     note='5 ty = quy uoc fleet (~65x vi the that 75 tr da dong); Q/ADV250 0,6x trong vung hieu chinh'),
  ck_real_sleeve=o['ck_real_sleeve'], px_vs_center_post=o['px_vs_center_post'], px_vs_p10_post=o['px_vs_p10_post'], px_vs_p90_post=o['px_vs_p90_post'],
  label=o['label'], label_note='TRONG vung nhu vong 1. Vung so voi so muc gia cu doi chu yeu do DINH NGHIA (P25-P75 luoi base -> P10-P90 muc ket cuc). Luat 4 (gia <= 0,85 x tam): KHONG dat.',
  center_vs_p50_note=(f"tam = ky vong luoi {Q['mean']:,.0f} truoc CK; gia tri tai tham so trung tam (mid TB, L27, 0,8 NPV0 + 0,2 kinh te) {o['center_param_pre']:,.0f}; "
     f"P50 ket cuc {Q['p50']:,.0f}. Duoi P10 do nhanh KINH TE (0,20) quyet dinh mot phan (min {P['min']:,.0f} sau CK)."),
  axes_included=['doc NQ15: NPV0 0,80 / KINH TE (tai canh kinh te engine m7) 0,20 [trong so nhan dinh UL]', 'mid RSS3 thuc 2014-01..2026-09 P25/TB/P75 (.25/.5/.25)',
     'doi cao L 22/27/32 (.25/.5/.25) [gia dinh, khong co dinh muc nguon]', 'ket cuc trong o: duong gia PEAK/MID wp 0,6/0,4 [UL]'],
  axes_excluded=[dict(axis='r', reason='co dinh 13,5%; do nhay +-50/100bp rieng'),
     dict(axis='ban cu giu vuon toi L27 (bo qua NQ15)', reason=f"NQ HDQT 15 Dieu 4 la du lieu quan sat; bao song song tam {o['parallel_keepL27']['mean']:,.0f} sau CK"),
     dict(axis='wp PEAK', reason=f"khai [UL]; nhay wp 0 -> {o['sens_wp']['0.0']['mean']:,.0f}, 0,5 -> {o['sens_wp']['0.5']['mean']:,.0f}, 1 -> {o['sens_wp']['1.0']['mean']:,.0f}"),
     dict(axis='FCF = 90% LN loi', reason=f"[UL]; 80% {S['FCF/LN loi 80% (base 90% [UL])']:,.0f} / 100% {S['FCF/LN loi 100% (base 90% [UL])']:,.0f}"),
     dict(axis='haircut khoan vay Dakruco / tien Lao', reason='khong co co so du lieu -> WARNING + do nhay')],
  base_adjustments=[dict(item='Khoan vay Dakruco 40 ty', effect_dong_per_share=0, basis='so sach day du (dang tra dung han 80->40 ty H1, lai ~9%, TSDB 6 tr cp DRI)', source='BCTC HN Q3/2026; vong 1 cat 50% (-268 sau CK) -> do nhay'),
     dict(item='Tien tai Lao ~197 ty', effect_dong_per_share=0, basis='so sach; vong 1 giu lai 15% la DOAN -> do nhay (-395)', source='BCTC HN Q3/2026'),
     dict(item='Thue chuyen LN Lao wht 10% + quy du phong TC Lao TAU + KTPL', effect_dong_per_share=None, basis='giu nhu engine r4: TAU/KTPL tu BCTC; wht 10% = gia dinh engine, CHUA dan nguon luat thue Lao', source='r3/model.py dong 26-28'),
     dict(item='Gia go thanh ly', effect_dong_per_share=round(-S['wood_ha cu 20,87 tr/ha'] + P['mean']), basis=f"gia khoi diem NQ15 36 tr LAK/ha = {o['wood_nq15_tr_per_ha']:.2f} tr VND/ha thay uoc 20,87 tu ~54 ha; ap cho MOI ha thanh ly", source='NQ HDQT 15 Dieu 4 (04/11/2026)'),
     dict(item='XDCB do dang 72,71 ty', effect_dong_per_share=993, basis='so sach (NPV0)', source='BCTC HN Q3 ma 252')],
  grid_desc=(f"Luoi MUC KET CUC n={o['n_outcomes']} ({o['n_cells']} o x 2 duong gia). Doc NQ15 (NPV0 0,80 / KINH TE 0,20) x mid 3 x L 3; ket cuc PEAK 0,6/MID 0,4. "
     "r 13,5%. Base: khoan vay Dakruco, tien Lao theo so sach; thanh ly 1.975,23 ha 2027-30 gia khoi diem NQ15; tai canh NPV0. Phan vi _shared/wpct.py. Sau CK = x(1 - CK 5 ty)."),
  zone_old=r1['zone_old'], r1=dict(center_post=r1['center_post_liq'], p10=r1['p10_post'], p50=r1['p50_post'], p90=r1['p90_post'], label=r1['label']),
  center_change_pct=P['mean'] / r1['zone_old']['center'] - 1,
  change_reason=(f"Tam sau CK 14.329 -> {P['mean']:,.0f}. Cau noi diem (TB, L27, truoc CK): base cu 15.860 -> bo haircut Dakruco {br['+bo haircut Dakruco']:,.0f} -> bo giu 15% tien Lao {br['+bo giu 15% tien Lao']:,.0f} "
     f"-> gia go NQ15 {br['+wood_ha = gia khoi diem NQ15']:,.0f} -> doc NQ15 thanh ly 1.975 ha 2027-30 {br['+doc NQ15-NPV0 (lich thanh ly 1.975 ha 2027-30)']:,.0f}. "
     "Hai sua base (+) bi NQ15 (-) bu tru; phan vi o muc ket cuc."),
  warnings=["Vu an Dakruco (co dong ~45%, ma DRG): 2 cuu TGD bi khoi to, 5 bi can bi truy to 02/2025 -> rui ro di cu sang DRI qua ben lien quan",
     "DHDCD 22/10/2026 nang nguong giao dich ben lien quan can DHDCD duyet tu 10% -> 30% tong tai san, CUNG NGAY To trinh 40 (Dakruwood) - doi chieu LDN D167 k2, ND155 D293 k4b (can legal-vn)",
     "NQ HDQT 15: nghien cuu mua Dakruwood tu Dakruco (HDQT xet 12/2026) - giao dich ben lien quan",
     "Dau gia 1.975,23 ha mot lo, gia co dinh 4 nam, khong cam ben lien quan mua -> theo doi DANH TINH ben trung (Dakruco/Dakruwood = ben lien quan)",
     "Cho Dakruco vay con 40 ty (TSDB 6 tr cp DRI) - dang tra dung han; mat trang = -536 sau CK",
     "Tien gui Quy TDND Cao su DL 70 ty + gop 3 ty (soat xet chua xac dinh gia tri thu hoi khoan gop)",
     "~197 ty tai Lao khong thuyet minh nguyen te/lai suat/ky han; van ban to nhuong chua cong khai; mot phan dat thuoc quy hoach rung bao ton",
     "Lien he framework §3 HARD ABANDON #4 (giao dich ben lien quan chuyen gia tri ra co dong lon)",
     "Tra cuu 'khoi to/xu phat DRI 2026': WebSearch 05/11/2026 khong thay vu moi lien quan DRI; tim thay bai Bao Thanh tra ve khoi to lanh dao Dakruco (cu)",
     "Ngoai redo (Mike xu ly): broker openQuantity DRI = 0 o ca 2 account"],
  open_issues=["Hop dong to nhuong 01616/KD/DDT4 chua xac minh", "Doi cao L 22/27/32 la gia dinh", "Trong so nhanh KINH TE 0,20 vs luat 20 (NPV0) - nhan dinh",
     "wht 10% thue chuyen LN Lao chua dan nguon", "Gia trung dau gia thuc (>= khoi diem) va danh tinh ben mua", "SXKD T10 (~10/11)", "HOSE Q4/2026"],
  fear_buy_2_5='Ho so crisis-DD DRI dang mo (ngay 4 GIU); muc gia nay KHONG thoa luat 4 (gia <= 0,85 x tam) -> khong du dieu kien vao them theo §2.5 o gia 04/11')
json.dump(s, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps({k: s[k] for k in ('center_post_liq', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label', 'center_change_pct')}, default=float))
