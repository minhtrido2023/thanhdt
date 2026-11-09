"""Ghi ../SUMMARY.json tu model_out.json + assumptions.json (schema theo FPT/SUMMARY.json, rut gon phan khong ap dung)."""
import os, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
O = json.load(open(os.path.join(HERE, 'model_out.json'))); A = json.load(open(os.path.join(HERE, 'assumptions.json')))
r1 = lambda x: int(round(x)); P = O['post']; PX = O['price']
md5 = hashlib.md5(open(os.path.join(HERE, 'assumptions.json'), 'rb').read()).hexdigest()
assert md5 == O['assumptions_md5']
S = dict(
 ticker='BSR', asof_price_date=O['pxd'], price=PX, price_source='BQ tav2_bq.ticker Price (calc/px_bsr.csv)',
 r=O['r'], r_anchor=dict(r=0.135, rate=O['dep']['d0']['rate'], source=O['dep']['d0'].get('rate_source'), dep_asof=O['dep']['d1']['rate'],
     dep_asof_source=O['dep']['d1'].get('rate_source'), rule='r = 13,5%% + 1,0 x (dep_12T - %.2f%%)' % (100 * O['dep']['d0']['rate'])),
 kind='expected_weighted', center_pre_liq=r1(O['pre']['center']), center_post_liq=r1(P['center']),
 p10_post=r1(P['p10']), p25_post=r1(P['p25']), p50_post=r1(P['p50']), p75_post=r1(P['p75']), p90_post=r1(P['p90']),
 p10_pre=r1(O['pre']['p10']), p50_pre=r1(O['pre']['p50']), p90_pre=r1(O['pre']['p90']),
 liq_disc_5ty=O['ck']['5ty'], px_vs_center_post=PX / P['center'] - 1, px_vs_p10_post=PX / P['p10'] - 1, px_vs_p90_post=PX / P['p90'] - 1,
 label=O['label'], pct_weight_below_price=P['pct_below_px'], n_outcomes=P['n'], min_outcome=r1(P['min']), max_outcome=r1(P['max']),
 grid_desc='rev2: 81 ket cuc = kich ban(3; Bobby 0,30/0,50/0,20) x loi lam chuan hoa +-20% (3) x giai phong WC vuot 0/0,27/0,54 (3) x he so LN vuot nen 0,5/1/1,5 (3); RONIC=Ke; thue 10%->20% sau 2039; mo rong NPV0',
 scen_mid={k: r1(v) for k, v in O['comp']['by_scen_mid'].items()},
 components_d_per_share=dict(net_cash=r1(O['comp']['net_cash_ps']), fixed_incl_cip_minus_khcn=r1(O['comp']['fixed_ps']),
     ops=dict((k, r1(v)) for k, v in O['comp']['ops_ps'].items()), windfall=dict((k, r1(v)) for k, v in O['comp']['windfall_ps'].items()),
     wc_excess_bn=r1(O['comp']['wc_ex_bn'])),
 sens_r={k: r1(v) for k, v in O['sens_r'].items()}, sens_moat={k: r1(v) for k, v in O['moat_sens'].items()},
 parallel_versions=dict(sym_0275_045_0275={k: (r1(v) if isinstance(v, float) and k != 'pct_below_px' else v) for k, v in O['sym'].items()}),
 label_by_size={'5ty': dict(center=r1(P['center']), p10=r1(P['p10']), p90=r1(P['p90']), label=O['label'], ck=O['ck']['5ty']),
                'sleeve_40tr': dict(center=r1(O['sleeve40']['center']), p10=r1(O['sleeve40']['p10']), p90=r1(O['sleeve40']['p90']), label=O['label_40tr'], ck=O['ck']['40tr'])},
 rule4={'5ty': dict(threshold=r1(0.85 * P['center']), pass_=PX <= 0.85 * P['center'])},
 ck_ref_size=dict(size='5 ty', adv250=O['liq']['adv250']['adv_med'], adv60=O['liq']['adv60']['adv_med'], sigma_d=O['liq']['adv250']['sigma_d'],
                  ck_adv250=O['ck']['5ty'], part_adv250=O['liq']['adv250']['part']['5000000000']),
 implied_by_price=dict(ke=O['implied']['ke'], core_nopat_bn=r1(O['implied']['core_nopat_bn']), core_nopat_x_2023_25=O['implied']['core_nopat_x_hist'],
                       grm_usd_bbl_above_coso=O['implied']['grm_usd_above_base']),
 pe=dict(pe_ttm=O['pe']['pe_ttm'], pb=O['pe']['pb'], ttm_np_bn=r1(O['pe']['ttm_np_bn'])),
 moat=dict(tier='NARROW', type='ADMIN/LOCATION', durable=False, params='khong thuong (RONIC=Ke)', moat_tags_csv='chua co dong BSR -> de xuat trong REPORT muc 6'),
 assumptions_md5=md5, assumptions_file='calc/assumptions.json',
 auto_flags=dict(dcf_rich_21359='THAT (huong dung, muc con nhe: tam DD 17.496)', pe_4_75='NHIEU — PE tren LN dinh chu ky ~7,2-7,9x loi lam chuan hoa (TTM 27.754 / 3.863-3.493)',
                 lag_hi='THAT ve so (Q3 +888% YoY) nhung KHONG BEN (crack ngoai sinh + ton kho); gia sau cong bo -8,7%'),
 warnings=['PVN so huu 92,12% (free float ~7,9%); quyet toan co phan hoa 2018 CHUA duoc phe duyet (Deloitte nhan manh, soat xet 6T/2026)',
           'KH 2026 dieu chinh 06/11 LNST HN 18.579 ty < 9T thuc 24.902 ty (doc thang = Q4 lo -6.323 ty); doc la KH hanh chinh, chua xac minh',
           'Thue NK MFN xang dau 0% den 31/12/2026 (ND 72, NQ 43) - quyet dinh 2027 nam o Chinh phu',
           'Uu dai thue TNDN 10% den het 2039 (QD 952/QD-TTg)',
           'Du an mo rong 39.004,5 ty (vay 23.402,7) - NPV0 base; rui ro tre tien do 2028->2029'],
 open_issues=['BQ Q1+Q2+Q3/2026 = 24.693 ty vs BCTC 9T 24.899 ty (lech 206 ty, co the dieu chinh hoi to sau soat xet)',
              'Vay ngan han 13.525 ty: dong tien/muc dich chua doc thuyet minh 14',
              'Tra truoc nguoi ban 3.009 ty (dau nam 372) va chi capex 3.155 ty vs TSCD+CIP tang ~0,7 nghin ty - chua giai thich',
              'GRM tach crack/ton kho theo quy: BCTC khong cong bo; tach bang chung cap nganh (Bobby 3.2) + du phong ton kho 678 ty',
              'TTDB xang 0% tu 01/11/2026 mau thuan nguon (Bobby muc 2)'],
 fear_buy_eligible_2_5=False, job='Taylor_20261109_083122', job_r1='Taylor_20261109_073600', round='r2',
)

ES = json.load(open(os.path.join(HERE, 'errata_steps.json')))
S['errata_r2'] = dict(steps=ES, headline_choice='E1-B (boc ty gia rong; lai quy nam 1.292) lam headline vi tham trong; E1-A (giu ty gia) la ban song song',
    variant_A_giu_ty_gia=[x for x in ES if x['name'].startswith('rev2 bien the A')][0],
    mbv_loss_B=[x for x in ES if x['name'] == 'rev2 B + MBV mat trang'][0], mbv_loss_per_share_est=-round(A['mbv_blocked']['htm_bn'] / A['shares_m'] * 1000 * (1 - O['ck']['5ty'])),
    rule4_zone_range='~14.400-15.400 (skeptic) ; headline B nguong 85 pct tam = %d ; ban A %d' % (r1(0.85 * P['center']), r1(0.85 * [x for x in ES if x['name'].startswith('rev2 bien the A')][0]['center'])),
    inside_zone_threshold_p90='%d (headline B) ; %d (ban A)' % (r1(P['p90']), [x for x in ES if x['name'].startswith('rev2 bien the A')][0]['p90']),
    unchecked=['PDF goc BCTC HN Q3/2026 KHONG doi chieu lai trong phien r2 (khong co cong cu doc PDF): E1-E4 dung so theo ERRATA skeptic', 'lai/chi phi vay 2023-24 chua lay duoc', 'hop dong ung truoc 2.601 ty (China Chengda/Beijing Petrochemical Eng.): can xac nhan', 'nhanh LN loi 2019-25 (~1,55 lai) chua kiem', 'tin phap ly sau 03/11 chua quet duoc (khong co cong cu tim kiem tin trong phien nay)'])
S['warnings'] += ['Tien gui HTM 2.735,6 ty (trong 56.893) o MBV (ex-OceanBank) "dang tam dung giao dich" (TM5 tr.20): base giu nguyen; neu mat trang tam -> %d (do nhay, ~%d d/cp)' % (round(S['errata_r2']['mbv_loss_B']['center']), S['errata_r2']['mbv_loss_per_share_est'])]
S['open_issues'] = [x for x in S['open_issues'] if not x.startswith('BQ Q1+Q2+Q3') and not x.startswith('Vay ngan han') ] + [
 'E5: BQ Q1+Q2+Q3/2026 24.693 vs BCTC 9T 24.899 (lech 206 ty): chi anh huong PE TTM, khong vao gia tri',
 'E5 dong: vay ngan han 13.525 ty la han muc quay vong BIDV/VCB/VietinBank (TM14) — binh thuong; da tru menh gia',
 'E5 dong: PP LN gop ~-4 ty (DT 3.840 - GV 3.844)',
 'E6 lech 2 chieu CHUA dinh luong: VAT khau tru 6.509 gan truc giai phong (xuong/len); cua so 2023-25 chua TA5 trong 1/3 vs chu ky ~4 nam (lech xuong nhe); nha may gan khau hao het 36,8/46,7 nghin ty nen capex duy tri = khau hao co the cao (lech len)',
 'E2: ung truoc 2.601,2 ty cho 2 nha thau ky su Trung Quoc ghi 100% gia so — can xac nhan hop dong',
 'LN loi 2019-25 (lai ~1,55) va lai/CP vay 2023-24 chua kiem']
json.dump(S, open(os.path.join(HERE, '..', 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print('SUMMARY', S['center_post_liq'], S['p10_post'], S['p90_post'], S['label'], S['rule4'], md5)
