"""SUMMARY.json vong 3 MVC tu mvc_redo_r3_out.json + grid_mvc_redo_r3.csv (chay SAU mvc_redo_r3.py; khong tinh lai dinh gia, chi tong hop
+ 1 do nhay 'chat-3c' tren luoi da khoa, cung quy uoc 5F/moat_sens_5f.py: bo STRUCTURAL & ADMIN-perm05, giu ADMIN 0,45 / CYC 0,35)."""
import json, os, csv, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_shared')))
from wpct import wpct, weight_below  # noqa: E402
o = json.load(open(os.path.join(HERE, 'mvc_redo_r3_out.json'))); A = json.load(open(os.path.join(HERE, 'assumptions_r3.json'), encoding='utf-8'))
r2 = json.load(open(os.path.join(HERE, '..', 'SUMMARY_r2.json')))
P, Q, T, px = o['post'], o['pre'], o['tornado'], o['price']; f5 = 1 - o['ck']['5ty']['adv250']
# do nhay chat-3c tren luoi r3 (truc headline)
V, W, B, AD = [], [], [], []
for r in csv.DictReader(open(os.path.join(HERE, 'grid_mvc_redo_r3.csv'))):
    if r['tl_m'] not in ('0.3', 'nnc', '0.38'): continue
    V.append(float(r['V'])); W.append(float(r['wraw'])); B.append(r['branch']); AD.append(r['admin'])
V, W, B, AD = np.array(V), np.array(W), np.array(B), np.array(AD)
k3 = np.where(B == 'STRUCTURAL', 0.0, np.where((B == 'ADMIN_GATED') & (AD == 'perm05'), 0.0, 1.0))
sc = np.where(B == 'ADMIN_GATED', 0.45 / (W[B == 'ADMIN_GATED'] * k3[B == 'ADMIN_GATED']).sum(), np.where(B == 'CYCLICAL', 0.35 / W[B == 'CYCLICAL'].sum(), 0.0))
w3 = W * k3 * sc; w3 = w3 / w3.sum(); p3 = wpct(V * f5, w3)
chat3c = dict(center=float((V * w3).sum() * f5), p10=p3[0.1], p50=p3[0.5], p90=p3[0.9], below=weight_below(V * f5, w3, px))
R = lambda x: int(round(x))
def pack(s): return dict(center=R(s['mean']), p10=R(s['p10']), p50=R(s['p50']), p90=R(s['p90']), below=round(s['below'], 4))
sz = o['post_by_size']; alt = o['alternatives_post']; ib = o['implied_by_price']
s = dict(ticker='MVC', round=3, job='Taylor_20261108_180136', asof_price_date=o['price_date'], price=px, r=o['r'], dep=o['dep'], dep_src=o['dep_src'],
  center_pre_liq=R(Q['mean']), center_post_liq=R(P['mean']), p10_post=R(P['p10']), p50_post=R(P['p50']), p90_post=R(P['p90']),
  p10_pre=R(Q['p10']), p50_pre=R(Q['p50']), p90_pre=R(Q['p90']), p10_out=R(P['p10']), p50_out=R(P['p50']), p90_out=R(P['p90']), min_out=R(P['min']),
  pct_weight_below_price=P['below'], n_outcomes=o['n_outcomes'], n_cells=6561, n_cells_note='6.561 o (3 nhanh x 3^7) x 3 muc thue x 8 ket cuc = 157.464',
  center_param_nodelay=R(o['center_param_nodelay']), center_param_withdelay=R(o['center_param_withdelay']),
  label=o['label'], label_by_size=o['label_by_size'],
  label_note='TRONG vung o moi co (5 ty, 1 ty, 40 tr, 10 tr). Khong doi so r2.',
  rule4_by_size={k: dict(center=R(v['center']), thr_085=R(v['thr']), pass_=v['pass_']) for k, v in o['rule4_by_size'].items()},
  rule4_note=('Luat 4 DAT o moi co (r2: KHONG dat o 5 ty). Mong o 5 ty: 0,85 x 16.241 = 13.805 vs 13.500 (+2,3%). Phu thuoc truc bien TL: '
              f"ban r2 mot chieu {{25/30/~NNC}} tam {alt['tl_r2_onesided_25_30_nnc']['mean']:,.0f} -> 0,85x = {0.85*alt['tl_r2_onesided_25_30_nnc']['mean']:,.0f} < 13.500 (TRUOT 0,7%)."),
  ck_ref_size=dict(size_vnd=5e9, Y=1.0, **o['ck']['5ty'], note='5 ty = quy uoc fleet; Q/ADV250 11,5x (ADV60 26,5x) = NGOAI SUY ngoai vung hieu chinh luat can bac hai'),
  ck_by_size=o['ck'], post_by_size={k: pack(v) for k, v in sz.items()},
  ck_real_sleeve={k: o['ck'][k] for k in ('10tr', '40tr')},
  tranche=dict(sleeve_cap='2-4% NAV SpaceX (~0,94 ty) = ~19-38 tr', per_session_cap_20pct_adv60=0.2 * o['liq']['adv_60'],
               note='r2 ghi tranche <=1 ty: SAI (vuot tran sleeve); sua: <= min(4% NAV, 20% ADV60 ~ 37,8 tr/phien), toi da 1 phien/lenh'),
  px_vs_center_post=o['px_vs_center_post'], px_vs_p10_post=o['px_vs_p10_post'], px_vs_p90_post=o['px_vs_p90_post'],
  center_vs_p50_note=(f"tam = ky vong luoi {Q['mean']:,.0f} truoc CK / {P['mean']:,.0f} sau CK 5 ty; tham so trung tam (khong tre) {o['center_param_nodelay']:,.0f} truoc CK; "
     f"P50 ket cuc {P['p50']:,.0f} sau CK. P90 do nhanh STRUCTURAL (0,20, Bobby) quyet dinh (trung vi nhanh sau CK {o['branch_post']['STRUCTURAL']['p50']:,.0f}); "
     f"w_STRUCT 0,10 -> P90 {o['sens_w_structural_post']['0.10']['p90']:,.0f}, 0,30 -> {o['sens_w_structural_post']['0.30']['p90']:,.0f}; P10 gan nhu bat bien (~9,9k)."),
  assumptions=A['assumptions'],
  axes_included=['trang thai 0,20/0,45/0,35 (Bobby)', 'chi phi TL ca 0,85/1/1,15', 'REL 0,88/0,91/0,95', 'SL nam thuong 3 muc', 'han GP TL 2035/W/2045', 'anh xa ADMIN 3',
     'bien chu ky TL {30%/~NNC/38%} deu [UL] (DOI XUNG, moi r3)', 'tran chu ky {SL 1,05/theo nhanh/SL 1,40} (moi r3)', 'thue Nui Nho {2043/2030/khong} (moi r3)',
     'ket cuc trong o: W0 x PW0', 'D1 tran tang theo lam phat (co che, khong phai truc)'],
  axes_excluded=[dict(axis='r', reason='13,5% theo luat 21; do nhay rieng'),
     dict(axis='tre GP mo moi (Bobby F6)', reason=f"nhan dinh -> khoi base; do nhay {T['tre GP ky vong (Bobby F6) mo moi + CIP NNC']['d']:+,.0f}"),
     dict(axis='mo moi hai phia', reason=f"lech NPV0 khong co IRR du lieu; do nhay {T['mo moi hai phia (upside + NPV gia xau; lech NPV0)']['d']:+,.0f}"),
     dict(axis='chiet khau holding/quan tri', reason=f"[UL] -> base 0%; 6% {T['chiet khau holding 6% (phan NNC)']['d']:+,.0f}, 15% {T['chiet khau holding 15% (phan NNC)']['d']:+,.0f} (truoc CK, tham so trung tam)"),
     dict(axis='bien TL 25%', reason='muc r2 chi mo chieu giam; ban r2 {25/30/~NNC} bao song song')],
  base_adjustments=[
     dict(item='D1 tran chu ky tang theo lam phat (Tan Lap + NNC nhin xuyen)', effect_dong_per_share=R(o['bridge_post']['2 + D1 tran tang theo lam phat'] - o['bridge_post']['1 r2 o CK 06/11']), basis='sua loi dem hai lan (co che), bien TL ~NNC 25,7% -> 34,0%', source='assumptions_r3.json D1; TOP5D MVC#1'),
     dict(item='ICD Hoa Lu = tai san thuan tru tien 38,728 ty (thay von gop 44,797)', effect_dong_per_share=R(o['bridge_post']['6 + ICD tai san thuan tru tien (= r3)'] - o['bridge_post']['5 + truc bien TL doi xung {30/~NNC/38}']), basis='hop nhat - rieng 30/09/26, khop tong TS va VCSH; tien ICD 2,923 da trong NETFIN', source='BCTC HN + rieng Q3/26'),
     dict(item='Hai mo moi da chi 438,4 ty; dat 30 ty; cum CN; mua NNC 51%', effect_dong_per_share=0, basis='so sach / NPV0', source='BCTC HN Q3/26; DHDCD 2026'),
     dict(item='Co phan NNC 44,07% giai dong thoi', effect_dong_per_share=None, basis=f"V_NNC ngam {o['V_NNC_implied_pre']:,.0f} vs NNC r3 {o['V_NNC_r3_pre']:,.0f} truoc CK ({o['V_NNC_implied_pre']/o['V_NNC_r3_pre']-1:+.1%}) => nhat quan", source='nnc_model_r6 + patch D1/D2/thue nhu NNC r3')],
  headline_vs_alternatives=dict(
     headline=dict(desc='D1 + tran 3 muc + thue 3 muc + bien TL doi xung {30/~NNC/38} + ICD tai san thuan', **pack(P)),
     tl_r2_onesided_25_30_nnc=pack(alt['tl_r2_onesided_25_30_nnc']), tl_no_axis_nnc_only=pack(alt['tl_no_axis_nnc_only']),
     rent_2043_only=pack(alt['rent_2043_only']), cap_r2_branch_140=pack(alt['cap_r2_branch_140']), icd_r2_44797=pack(alt['icd_r2_44797']),
     strict_3c_sensitivity=dict(center=R(chat3c['center']), p10=R(chat3c['p10']), p50=R(chat3c['p50']), p90=R(chat3c['p90']), below=round(chat3c['below'], 4),
        note='do nhay rui ro (quy uoc user 08/11: KHONG ap 3c chat vao headline)'),
     skeptic_point=dict(center=15821, note='skeptic = r2 + D1 + tran 1,05 + thue (chua doi xung bien TL, chua sua ICD) = buoc 4 bridge, tai lap trung (15.821)')),
  implied_by_price=dict(
     cyclical_only_post=R(ib['cyclical_only_post']), note_cyc='CA nhanh CYCLICAL 100% sau CK 5 ty 14.284 > gia 13.500 (r2: 12.855 < gia) => gia khong con giai thich duoc chi bang CYC',
     w_structural_needed=ib['w_structural_needed'], note_ws='am (-0,22): khong ty trong STRUCTURAL >=0 nao cho tam = gia',
     vnnc_at_market_47200_post=R(ib['vnnc_market_shift_post']), generic_disc_after_vnnc_market=ib['generic_disc_needed_after_vnnc_market'],
     note_vnnc='NNC theo gia thi truong 47.200 (-1.496 sau CK) roi them chiet khau holding/quan tri chung ~8,4% => ra gia',
     roe_sustainable_implied=ib['roe_sustainable_implied'], roe_implied_center=ib['roe_implied_center'], note_roe='Gordon (ROE-3%)/(r-3%) x BVPS 15.460; ROE ben ngu y 13,0% (ROE TB Q4 2017-25 7,4% (ROE_MVC model_r6.py), Q3/26 TTM 20,7%)'),
  bridge_r2_to_r3={k: R(v) for k, v in o['bridge_post'].items()},
  corrections=[
     dict(n=1, verdict='DUNG - ap base', measured=R(o['bridge_post']['2 + D1 tran tang theo lam phat'] - o['bridge_post']['1 r2 o CK 06/11']), skeptic=556, note='bien TL ~NNC 25,7% -> 34,0% (NNC 34,3%) khop skeptic; patch runtime, khong sua file pin'),
     dict(n=2, verdict='DUNG - ap base', measured=R(o['bridge_post']['3 + muc tran SL 1,05'] - o['bridge_post']['2 + D1 tran tang theo lam phat']), skeptic=158),
     dict(n=3, verdict='DUNG - ap base', measured=R(o['bridge_post']['4 + truc thue {2043/2030/khong}'] - o['bridge_post']['3 + muc tran SL 1,05']), skeptic=-161, note=f"V_NNC ngam {o['V_NNC_implied_pre']:,.0f} vs NNC r3 {o['V_NNC_r3_pre']:,.0f} truoc CK (-0,3%)"),
     dict(n=4, verdict='DUNG mot phan - chon doi xung {30/~NNC/38} lam headline (khong bo truc)', measured=R(o['bridge_post']['5 + truc bien TL doi xung {30/~NNC/38}'] - o['bridge_post']['4 + truc thue {2043/2030/khong}']), skeptic='bo truc 16.281 / doi xung 16.299',
          note=f"ban bo truc tam {alt['tl_no_axis_nnc_only']['mean']:,.0f}; chon doi xung vi bien da rieng CHUA KIEM ca 2 chieu (STANDARD_r2 #2: giu bat dinh, khong gia vo biet)"),
     dict(n=5, verdict='SAI do lon - dem doi chi phan TIEN ICD 2,923 ty, khong phai ca 44,797', measured=R(o['bridge_post']['6 + ICD tai san thuan tru tien (= r3)'] - o['bridge_post']['5 + truc bien TL doi xung {30/~NNC/38}']), skeptic=-429,
          note='hop nhat - rieng 30/09/26: ICD tai san thuan 41,651 = tien 2,923 + GTGT 2,695 + TSCD 20,830 + tra truoc DH 16,073 + tra truoc NH 0,041 - no 0,911; CIP 37,69 -> TSCD/tra truoc DH (chuyen loai, khong xoa so); TSCD/tra truoc khong nam trong NETFIN va khong nam trong DCF Tan Lap => giu theo so sach (NPV0)'),
     dict(n=6, verdict='DUNG - sua', note='luat 4 ghi theo co; tranche sua ve tran sleeve + 20% ADV60'),
     dict(n=7, verdict='DUNG - sua', note='274,416 / 20,000 / -60,000 (co tuc phai tra V.19) / -6,524 doc lai BCTC HN Q3 KHOP; LOCK_r2 ghi chu sua 2 duong dan (md5 khop); §2.5 KHONG du dieu kien')],
  gordon=dict(roe_implied_center=ib['roe_implied_center'], roe_implied_price=ib['roe_sustainable_implied'], note='mot bien the (MVC no rong, khong tach lai tien gui)'),
  dep_sens_param={k: dict(r=v['r'], pct=v['pct']) for k, v in o['dep_sens_param'].items()},
  grid_desc=(f"Luoi MUC KET CUC n={o['n_outcomes']}: trang thai x ca 3 x REL 3 x SL 3 x han GP TL 3 x ADMIN 3 x bien TL {{30/~NNC/38}} x tran {{1,05/nhanh/1,40}} x thue {{2043/2030/khong}} x W0 x PW0; "
     "trong so o = trang thai x deu; r 13,5%; base khong tre GP; D1 tran tang theo lam phat. Phan vi _shared/wpct.py. Sau CK = x(1 - CK 5 ty)."),
  zone_old=r2['zone_old'], r2=dict(center_post=r2['center_post_liq'], p10=r2['p10_out'], p50=r2['p50_out'], p90=r2['p90_out'], label=r2['label'], price=r2['price']),
  center_change_pct_vs_r2=P['mean'] / r2['center_post_liq'] - 1,
  change_reason='tam 15.276 -> 16.241 (+6,3%): D1 +556, tran 1,05 +158, thue -161, bien TL doi xung +478, ICD -58, CK 06/11 -8.',
  warnings=r2['warnings'] + ["Phap ly sau 05/11/2026: CHUA quet lai trong vong 3 (chi WARNING)",
     "Rui ro buoc thoai theo Luat DN D195 khi MVC len 51% NNC (NNC dang so huu 10,3% MVC) - can legal-vn",
     "Bien da rieng Tan Lap CHUA KIEM (khong co bao cao bo phan) - truc doi xung {30/~NNC/38}; GPM hop nhat MVC 2017-25 16,1% < peer (gop mang phu)"],
  open_issues=r2['open_issues'] + ['Nguon 117,395/461,848/1.546 BQ khop; 274,416/20,0/60,0/6,524 doc tu txt BCTC HN Q3 (pdftotext), chua soat PDF goc bang mat'],
  fear_buy_2_5='KHONG du dieu kien sleeve fear-buy §2.5 (khong co su kien so hai; DK2 no rong -> 1,4-1,5 nghin ty chua dong)',
  measured_by='calc_r3/mvc_redo_r3.py (2 lan trung byte, run1.md5=run2.md5) + calc_r3/summary_r3.py; LOCK calc_r3/LOCK_r3_md5.txt')
json.dump(s, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1, default=float)
print(json.dumps({k: s[k] for k in ('center_post_liq', 'p10_out', 'p50_out', 'p90_out', 'pct_weight_below_price', 'label', 'center_change_pct_vs_r2')}, default=float))
print('chat3c', {k: round(v) if k != 'below' else round(v, 3) for k, v in chat3c.items()})
