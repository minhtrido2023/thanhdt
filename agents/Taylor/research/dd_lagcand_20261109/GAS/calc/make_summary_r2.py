import json, hashlib, os
H = os.path.dirname(os.path.abspath(__file__)); o = json.load(open(os.path.join(H, 'model_out_r2.txt'))); S = json.load(open(os.path.join(H, '..', 'SUMMARY_r1.json')))
md5 = hashlib.md5(open(os.path.join(H, 'assumptions_r2.json'), 'rb').read()).hexdigest()
px = o['price']; p = o['post_5ty']; q = o['pre']; s40 = o['post_40tr']
def lab(lo, hi): return 'DƯỚI vùng' if px < lo else ('TRÊN vùng' if px > hi else 'TRONG vùng')
ck5 = o['liq250']['ck']['5000000000']; ck40 = o['liq250']['ck']['40000000']
S.update(center_pre_liq=round(q['center']), center_post_liq=round(p['center']), p10_post=round(p['p10']), p25_post=round(p['p25']), p50_post=round(p['p50']), p75_post=round(p['p75']), p90_post=round(p['p90']),
  p10_pre=round(q['p10']), p50_pre=round(q['p50']), p90_pre=round(q['p90']), liq_disc_5ty=ck5, liq_disc_40tr=ck40,
  px_vs_center_post=px / p['center'] - 1, px_vs_p10_post=px / p['p10'] - 1, px_vs_p90_post=px / p['p90'] - 1, label=lab(p['p10'], p['p90']),
  pct_weight_below_price=o['pct_weight_below_price'],
  rule4_zone_5ty={'cheap_below': round(p['p10'], -2), 'fair_to': round(p['p90'], -2), 'expensive_above': round(p['p90'], -2)},
  label_by_size={'5ty': dict(center=round(p['center']), p10=round(p['p10']), p90=round(p['p90']), label=lab(p['p10'], p['p90']), ck=ck5),
                 'sleeve_40tr': dict(center=round(s40['center']), p10=round(s40['p10']), p90=round(s40['p90']), label=lab(s40['p10'], s40['p90']), ck=ck40)},
  sens_r={k: round(v) for k, v in o['sens_r'].items()},
  implied_by_price=dict(r=o['implied_r'], perp_growth_at_r13_5=o['implied_perp_growth_uniform'], note='r=8%% cho tam %d < gia; label tuong doi theo khung, khong phai bang chung hung phan' % round(o['r8_center'])),
  scen_central={k: round(v) for k, v in o['scen_central'].items()}, net_cash_per_share=round(o['net_cash_per_sh']), net_cash_per_share_incl_extras=round(o['net_cash_per_sh_incl_extras']),
  grid_desc='243 = kich ban(3; 0,275/0,45/0,275; decline 2,8/1,4/0%) x he so Brent(3) x du phong DH 343(3) x Brent dai han +-5(3) x muc ben phan du LN 2026(3); RONIC=Ke; tien rong theo so + XDCB 5.916,4 gia so (NPV0) + bao tieu 1.775,5 - quy KT-PL 875,6; Q4=0,231 nam',
  pe=dict(ttm=round(o['pe']['pe_at_price'], 1), center=round(o['pe']['pe_at_center'], 1), hist=o['pe_hist']),
  steps_cumulative={k: {a: round(b) for a, b in v.items()} for k, v in o['steps_cumulative'].items()},
  steps_individual_vs_r1={k: {a: round(b) for a, b in v.items()} for k, v in o['steps_individual_vs_r1'].items()},
  sens_offgrid_dong_per_share={k: round(v) for k, v in o['sens_offgrid_dong_per_share'].items()},
  sens_no_decline=round(o['sens_no_decline']), sens_decline_plus3pp=round(o['sens_moat_none_decline_plus3pp']))
S['moat']['sens_wide_no_decline'] = S['moat'].pop('sens_wide_no_decline') and round(o['sens_no_decline']); S['moat']['sens_none_decline_plus3pp'] = round(o['sens_moat_none_decline_plus3pp']); S['moat']['note_r2'] = 'khong suy giam != WIDE (WIDE con doi RONIC>Ke); bien gop % giam la pha loang co hoc, khong dung lam bang chung'
S['auto_flags']['DCF_auto_RICH_67081'] = 'CUNG CHIEU, doc lap thap hon (tam %d)' % round(p['center'])
S['auto_flags']['PE_12_1'] = 'dung (TTM 14.742 ty / 2,413 ty cp = 6.110 d; 74.100/6.110 = 12,1; lich su 2016Q1-2026Q3 11,7-26,5x trung vi 15,6x => sat day 10 nam) nhung LN TTM o Brent 82, cao hon trung binh chu ky'
S['warnings'] = [w for w in S['warnings'] if not w.startswith('Bao tieu')] + ['Bao tieu: tien khi tra truoc 1.775,5 ty (giam tu 2.122,6) - tinh la tai san thu hoi trong tam r2 (+731 d/cp) [UL: chua tru thue]', 'Nhan TREN vung la TUONG DOI THEO KHUNG (r danh nghia 13,5%, RONIC=Ke, suy giam 1,4%), khong phai bang chung thi truong hung phan; P/E 12,1x sat day 10 nam']
S['open_issues'] = ['thuyet minh du phong phai tra DH 343 (3.300 ty): CHUA KIEM - khong co trong TM16-23 BCTC HN Q3; do nhay tru 100% theo so = -679 d/cp, giu truc 0/50/100',
  'ly do mien nhiem Chu tich/TGD 07/2026 va ke hoach free-float truoc 31/12/2026: CHUA KIEM (legal-vn)', 'co tuc: 2.500 d/cp = 6.032,4 ty (BQ + bao cao bien dong VCSH) nhung khoan phai tra 5.491,7 ty: lech 540,7 ty CHUA GIAI THICH',
  'co cau san luong theo mo/khach hang chua co', 'cong thuc gia ban khi/tran-san chua kiem tu nguon goc', 'ty trong Q3 cua hoan nhap DP 9T/26 492 ty', 'E2 co so chi 10 diem nam (Brent 2016 chi 49 ngay du lieu); phan du RES co the chua lai ton kho LPG Q2-Q3/26 (thien lech len)']
S.update(assumptions_md5=md5, assumptions_file='calc/assumptions_r2.json', lock_md5='calc/LOCK_prerun_r2.txt + calc/LOCK_post_md5_r2.txt', job='Taylor_20261109_083126', round='r2', prev_round_file='SUMMARY_r1.json')
json.dump(S, open(os.path.join(H, '..', 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: S[k] for k in ('center_post_liq', 'p10_post', 'p90_post', 'label', 'px_vs_p90_post', 'assumptions_md5', 'rule4_zone_5ty')}, ensure_ascii=False))
