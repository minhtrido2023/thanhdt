"""Ghi SUMMARY.json vong 2 NNC tu nnc_redo_r2_out.json (moi so lay tu out; chu thich o day)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '../..'))
import common as C
o = json.load(open(os.path.join(HERE, 'nnc_redo_r2_out.json'))); r1 = json.load(open(os.path.join(HERE, '..', 'SUMMARY_r1.json')))
P, Q = o['post'], o['pre']; T = o['tornado']
s = dict(ticker='NNC', round=2, job='Taylor_20261105_020023', asof_price_date=o['price_date'], price=o['price'], r=o['r'],
  r_anchor=r1['r_anchor'], center_pre_liq=round(Q['mean']), center_post_liq=round(P['mean']),
  p10_post=round(P['p10']), p50_post=round(P['p50']), p90_post=round(P['p90']), p10_pre=round(Q['p10']), p90_pre=round(Q['p90']),
  p10_out=round(P['p10']), p50_out=round(P['p50']), p90_out=round(P['p90']), min_out=round(P['min']),
  pct_weight_below_price=o['pct_weight_below_price'], n_outcomes=o['n_outcomes'], n_cells=o['n_cells'],
  liq_disc_5bn=o['ck_ref']['adv250'], ck_ref_size=dict(size_vnd=5e9, Y=1.0, disc_adv250=o['ck_ref']['adv250'], disc_adv60=o['ck_ref']['adv60'],
     q_over_adv250=o['ck_ref']['q_over_adv250'], note='5 ty = quy uoc fleet; Q/ADV250 2,4x nam trong vung hieu chinh luat can bac hai'),
  ck_real_sleeve=o['ck_real_sleeve'],
  px_vs_center_post=o['px_vs_center_post'], px_vs_p10_post=o['px_vs_p10_post'], px_vs_p90_post=o['px_vs_p90_post'],
  label=o['label'], label_note='Nhan TRONG vung giu nhu vong 1; vung rong hon do chuyen sang MUC KET CUC (khong doi co ban). Luat 4 (gia <= 0,85 x tam): DAT.',
  center_vs_p50_note=(f"tam = ky vong trong so luoi {Q['mean']:,.0f} (truoc CK) ; gia tri tai tham so trung tam (khong tre) {o['center_param_nodelay']:,.0f} ; "
     f"P50 ket cuc {Q['p50']:,.0f}. Phan phoi lech phai: P90 {Q['p90']:,.0f} nam trong nhanh STRUCTURAL (trong so 0,20; trung vi nhanh {o['branch_pre']['STRUCTURAL']['p50']:,.0f}); "
     f"nhay w_STRUCT 0,15 -> P90 {o['sens_w_structural_pre']['0.15']['p90']:,.0f}, 0,10 -> {o['sens_w_structural_pre']['0.10']['p90']:,.0f}."),
  axes_included=['trang thai bien STRUCTURAL/ADMIN_GATED/CYCLICAL 0,20/0,45/0,35 (Bobby)', 'K chi phi 0,87/0,97/1,07', 'san luong nam thuong 3 muc',
     'anh xa ADMIN perm05/ramp/full', 'tran chu ky branch/SL 1,40 (DUA LAI vong 2)', 'thue Nui Nho toi 2043/2030/khong (deu, [UL]) (MOI vong 2)',
     'ket cuc ben trong o: 4 kich ban W0 25/50/20/5 x 2 duong gia PW0 50/50'],
  axes_excluded=[dict(axis='r (lai huy dong)', reason='co dinh r(04/11)=13,5%; bao do nhay +-50/100bp rieng'),
     dict(axis='(+) tra truoc CNBP 59,2 ty la tien thue da tra', reason=f"ban chat chua xac minh; do nhay {T['(+) tra truoc CNBP 59,2 la tien thue da tra (CHUA XAC MINH)']['d']:+,.0f}"),
     dict(axis='(+) doi thu het GP tu 2034', reason=f"chua co du lieu GP doi thu; do nhay {T['(+) doi thu het GP tu 2034']['d']:+,.0f}; doi xung voi STRESS duong gia phang {T['STRESS duong gia danh nghia phang']['d']:+,.0f} cung loai"),
     dict(axis='tre GP ky vong (Bobby F6)', reason=f"chi la nhan dinh -> ra khoi base (luat 3); do nhay {T['co tre GP ky vong (Bobby F6) CA CIP Tam Lap + mo MVC']['d']:+,.0f}")],
  base_adjustments=[dict(item='CIP Tam Lap 1 khu II 83,5 ty', effect_dong_per_share=0, basis='so sach (NPV 0 that, KHONG tru chi phi tre)', source='BCTC rieng Q3/2026 XDCB do dang'),
     dict(item='Doi xung BCDKT: ky quy PHMT 4,57 + DTA 4,31', effect_dong_per_share=424, basis='so sach (so do: tornado r6 nnc_model_r6_out.json)', source='Q3 V9, V19a tr.2'),
     dict(item='Thu nhap cho thue Nui Nho', effect_dong_per_share=round(-T['bo thue Nui Nho']['d']), basis='KHONG con trong base: truc 3 muc (2043/2030/khong); thoi han chua xac minh, nhieu kha nang ben lien quan NHC', source='KT25 7.1-7.2; KT25 9.1 cam ket: Khong co')],
  gordon=dict(roe_lock_ps=round(o['gordon']['roe_lock']['ps']), roe_lock=o['gordon']['roe_lock']['roe'], roe_fin_ps=round(o['gordon']['roe_fin']['ps']), roe_fin=o['gordon']['roe_fin']['roe'], roe_implied_center=o['gordon']['roe_implied_center_pre']),
  grid_desc=(f"Luoi MUC KET CUC n={o['n_outcomes']} ({o['n_cells']} o x 8 ket cuc). Truc: trang thai bien 0,20/0,45/0,35 x K 3 x SL 3 x ADMIN 3 x tran 2 x thue Nui Nho 3; "
     "trong so o = xac suat trang thai x deu; ket cuc = W0[kich ban] x PW0[duong]. r 13,5%. Base KHONG tru tre GP. Phan vi _shared/wpct.py. Sau CK = x(1 - CK 5 ty Y1 ADV250)."),
  zone_old=r1['zone_old'], r1=dict(center_post=r1['center_post_liq'], p10=r1['p10_post'], p50=r1['p50_post'], p90=r1['p90_post'], label=r1['label']),
  center_change_pct=P['mean'] / r1['zone_old']['center'] - 1,
  change_reason=("Vong 2: (a) phan vi o MUC KET CUC (vong 1 la phan vi cua ky vong tung o -> nen phan tan; P10 44,9k->30,2k); (b) dua truc tran SL 1,40 va truc thue Nui Nho vao luoi (-); "
     "(c) bo tre GP khoi base (+705 truoc CK). Tam sau CK 58.497 -> " + f"{P['mean']:,.0f}" + ". Nhan khong doi (TRONG vung) nhung 'sat can duoi' la ao anh: " + f"{o['pct_weight_below_price']:.1%} trong so duoi gia."),
  warnings=["So huu cheo MVC 44,07% NNC (Simplize ghi 43,55% - lech nguon, chua doi soat) <-> NNC 10,3% MVC; uy quyen DHDCD MVC 2026 mua NNC len 51% (gia/doi tac chua biet, giao dich ben lien quan); neu MVC >=51% Luat DN D195 co the buoc NNC thoai 10,3% MVC -> CAN legal-vn xac minh",
     "Truy thu TAI NGUYEN cham mo loi Mui Tau: du phong tien cap quyen 0,84 ty (Q3 V19a) sau CQKTKS 1,735 ty (KT25 7.8) - co E12 SKEPTIC_20261031 CHUA DONG",
     "Tong truy thu Nui Nho ~42 ty (du phong 15,58 + 5,95 + da nop 20,43 nam 2026) ~ 1.900 d/cp - KHONG nho",
     "Ben lien quan NHC (giam doc NNC = Chu tich NHC): 61% phai thu; DT dich vu 2025 18,92 ty ~ DT tu NHC 18,41 ty -> thu nhap cho thue Nui Nho nhieu kha nang la tu ben lien quan",
     "Dinh huong dua tien giu lai vao BDS; co tuc tien 2025 ~15% LNST",
     "Bien o dinh 15 nam (GPM Q3/26 57,9%) - rui ro chu ky chiem uu the",
     "Tra cuu 'xu phat/khoi to NNC 2026': WebSearch 05/11/2026 khong thay; nguon cong bo: financialreports.eu (CBTT NNC), BCTC Q3/2026. Co CBTT 17/04/2026 trung dau gia quyen khai thac khoang san (UBND TP.HCM) - CHUA doi chieu voi Tam Lap 1 khu II"],
  open_issues=["Thoi han + ban chat hop dong cho thue Nui Nho (nay la truc luoi)", "Tra truoc dai han CNBP 59,2 ty (+2,1k neu la tien thue)",
     "CBTT 17/04/2026 trung dau gia quyen khai thac: mo nao, gia, han -> co the dong cot 'Tam Lap 1 khu II chua GP'", "Xac suat 3 trang thai bien la nhan dinh Bobby",
     "Ty le MVC so huu NNC 44,07% vs 43,55%", "Mo hinh MVC nhung trong NNC la MVC r6 (khac MVC r9 dung o DD MVC)"],
  fear_buy_2_5='KHONG du dieu kien sleeve fear-buy §2.5 (khong co su kien so hai/khung hoang; day la DD dinh gia thuong)')
json.dump(s, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps({k: s[k] for k in ('center_post_liq', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label', 'center_change_pct')}, default=float))
