"""Ghep summary_r3_core.json + implied_r3_out.json + metadata -> ../SUMMARY.json (backup SUMMARY_r2.json da tao trong compare_r3.py). Tat dinh."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
S = json.load(open(os.path.join(HERE, 'summary_r3_core.json'))); I = json.load(open(os.path.join(HERE, 'implied_r3_out.json')))
M = json.load(open(os.path.join(HERE, 'model_r3_out.json'))); R2 = json.load(open(os.path.join(BASE, 'SUMMARY_r2.json')))
f = 1 - S['liq_disc_5ty']
S['assumptions'] = [
 dict(item='Nen bien gop 2027/28 = R2 19,5/20,7% (gia von Q3/26 x4 bo du phong, co dinh)', basis='GPM Q3/26 thuc te khi dung quang mua ngoai: 20,5% gom du phong / 24,6% bo du phong; 9T 20,7%/23,6%; trung vi 4 peer 19,47% (3c: moat khong ben => bien ve TB nganh)', source='MIKE_EXTRACT_BCTC_Q3_2026.md dong 8-9; ADDENDUM_5F_r2.md dong 16; r9_calc.py dong 7'),
 dict(item='Trong so kich ban xau/co so/tot 0,25/0,5/0,25 [UL]', basis='bien do quanh co so gan doi xung (-369/+405 ty EBIT 2027 tren R2); 0,3/0,2 cu tu nhan chu quan', source='dgc_valuation_20261029_r12/REPORT dong 5; TOP5C muc DGC #2'),
 dict(item='RONIC = Ke (13,5%)', basis='moat_durable=false (khai truong dung, ROIC5Y<Ke 2018-20)', source='ADDENDUM_5F_r2.md §2'),
 dict(item='Khai truong 25 DUNG o base (w mo lai = 0)', basis='hien trang quan sat duoc: Q3/26 chay 100% quang mua ngoai; khong co van ban/tin mo lai (WebSearch 08/11/2026); mo lai = khoi phuc co che hao, hao khong ben => khong cong', source='REPORT.md dong 30; TOP5C #4; quet 08/11'),
 dict(item='Du phong moi truong 100 ty/quy: mot lan/huu han 4 quy/vinh vien, 1/3 moi nhanh [UL]', basis='da trich 100 ty Q2 + 100 ty Q3/26 (BCTC); lap hay khong chua phan dinh', source='BCTC HN Q3/2026 p06, LCTT'),
 dict(item='La chan thue du phong = 0 [UL]', basis='than trong: tru thue khi chi that chua xac minh chung tu; do nhay 20% +570', source='TOP5C #6'),
 dict(item='Nghi Son XDCB 1.408,8 so sach, truc -500/0/+500 (0,25/0,5/0,25 [UL])', basis='luat du an moi NPV0; bien do = chenh von 2.900 vs 2.400', source='BCTC note 11 p30; TBTCVN 17/09/2025'),
 dict(item='r = 13,5% + 1,0x(7,40% - 7,40%) = 13,5%; truc +-50bp (0,25/0,5/0,25 [UL])', basis='CCTG 12T Big4 online 6,8% -> hieu dung 7,40% (2026-11-02, khong doi 06/11)', source='deposit_rate_vn.py + data/deposit_rate_vn_events.csv'),
 dict(item='g 3%, thue dai han 15% [UL], he so EBIT 0,8..1,2 deu', basis='giu tu r1/r2', source='model.py'),
 dict(item='Phap ly khong vao base', basis='luat user 02/11: vu an chi WARNING; bao song song truc haircut tien rong', source='model_r2.py LEGAL')]
S['implied_by_price'] = dict(I, reading=('Gia 33.000 ~ P10 ket cuc. De TAM = 33.000 can EBIT loi chi ~%.2fx co so mai mai (tren nen R2, khai truong dung), hoac kich ban xau chac chan + du phong vinh vien chac chan (%d). '
                                          'Rieng du phong vinh vien chac chan: %d; rieng kich ban xau chac chan: %d.') % (I['ebit_mult_for_center_eq_price'], I['center_if_xau_and_permanent'], I['center_if_prov_permanent_certain'], I['center_if_xau_certain']))
br = []
for b in M['bridge_pre']:
    br.append(dict(step=b['step'], center_pre=round(b['center_pre']), center_post_ck_r3=round(b['center_pre'] * f), delta_pre=None if b['delta'] is None else round(b['delta'])))
br.append(dict(step='CK 5 ty ADV250 06/11 (0,725%) va gia moi', center_post_ck_r3=S['center_post'], note='r2 CK 0,712%% @04/11 -> 44.767; r2 tai lap o CK moi = %d' % round(M['bridge_pre'][0]['center_pre'] * f)))
S['bridge_r2_to_r3'] = br
S['skeptic_check'] = {
 'c1_dem_doi': dict(verdict='DUNG ve ban chat, so khac', skeptic=1612, r3_single_post=S['single_correction_post']['c1'], why='r3 bo chong lan cho MOI quy du phong tu 2027 (gap r4-R2 281/305 ty/nam), khong chi nhanh vinh vien; trong headline van de bi trit tieu bang cach dung nen R2 (khong chua du phong)'),
 'c2_trong_so': dict(verdict='DUNG, trung so', skeptic=653, r3_single_post=S['single_correction_post']['c2']),
 'c3_ronic': dict(verdict='DUNG, so lon hon', skeptic=-1760, r3_single_post=S['single_correction_post']['c3'], why='r3 ap reinv=1-g/Ke cho ca 2027-28 tuong minh lan terminal (nhu cau truc model_r2)'),
 'c4_khai_truong': dict(verdict='DUNG; r3 di xa hon: base w=0', r3_single_post_w0=S['single_correction_post']['c4_w0'], note='w>=0,10 => nhan DUOI vung; nhan phu thuoc gan hoan toan vao truc nay'),
 'c5_nen_bien': dict(verdict='DUNG; R2 co dong co so => len BASE', skeptic=3041, r3_single_post=S['single_correction_post']['c5_R2'], why='so r3 gom ca viec het chong lan du phong (c1) vi R2 bo du phong'),
 'c6_shield': dict(verdict='DUNG la do nhay; giu 0 o base', skeptic=378, r3_single_post_20pct=S['single_correction_post']['c6_shield20']),
 'c7_chu_day': dict(verdict='DUNG', fix='EBIT 2027 co so R2 1.289 < EBIT 9T nam hoa 1.405 (gom du phong) / 1.672 (bo du phong) => 9T KHONG phai day trong mo hinh; mo hinh gia dinh bien ve TB nganh, thap hon 9T'),
 'c8_HTM': dict(verdict='chua kiem PDF goc', note='ban trich cong khop noi bo: 2.991,4+3.241,0+2.017,5+401,3+786,6=9.437,8 + du thu 93,2 = 9.531,0'),
 'c9_vi_the': dict(verdict='ghi WARNING', note='ZaloPay 10.000 cp gia von 39.775 ~ 35% NAV theo skeptic (chua doi soat broker trong phien nay) >> tran sleeve 2-4%; §2.5 NON (tru #2 DN tu nhan truot)')}
S['axes_included'] = ['kich ban EBIT 2027-28 (R2)', 'du phong moi truong lap (xuong)', 'Nghi Son (hai chieu)', 'he so EBIT loi (hai chieu)', 'lai huy dong (hai chieu)']
S['axes_excluded'] = [dict(axis='mo lai khai truong 25 (len)', reason='khong co co so du lieu + moat khong ben; bao song song w 0,10/0,25/0,50'),
                      dict(axis='phap ly (haircut tien rong)', reason='luat user 02/11 WARNING; song song legal_axis')]
S['base_adjustments'] = R2['base_adjustments']
S['center_vs_p50_note'] = f"tam {S['center_post']} vs P50 ket cuc {S['p50_out']} vs tham so trung tam {S['center_param_post']} (tham so trung tam = du phong huu han 4 quy; tam thap hon vi nhanh vinh vien -7.696 d/cp w 1/3). P10 do nhanh xau x du phong vinh vien quyet dinh."
S['label_fragility'] = 'Gia 33.000 chi tren P10 32.931 +0,2%: TRONG vung mong manh. DUOI vung neu mo lai khai truong w>=0,10, la chan thue 20%, hoac RONIC 20%.'
S['warnings'] = R2['warnings'] + ['Quet WebSearch 08/11/2026: chua thay tin truy to/xu phat phap nhan DGC moi sau 05/11; vu Lilama (cao trang VKS Lao Cai) lien quan cong ty con DGC Lao Cai mua quang — da biet', 'Tap trung vi the ZaloPay 10.000 cp (~35% NAV theo skeptic) >> tran sleeve 2-4% NAV — KHONG du dieu kien §2.5 (NON)']
S['fear_buy_25'] = 'NON: P/B me ~0,96 dat, tru #2 (NN chi phoi) truot — DN tu nhan'
S['open_issues'] = R2['open_issues'] + ['HTM 9.531 chua doi chieu PDF goc', 'Vi the ZaloPay chua doi soat broker trong phien nay']
S['lock'] = 'calc/LOCK_r3_md5.txt (19 file)'
json.dump(S, open(os.path.join(BASE, 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1)
print({k: S[k] for k in ('center_post', 'p10_out', 'p50_out', 'p90_out', 'label', 'pct_weight_below_price')})
