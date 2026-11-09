"""Ghi FPT/SUMMARY.json r3 tu model_r3_out.json + assumptions_r3.json (backup SUMMARY.json r2 -> SUMMARY_r2.json, byte-identical)."""
import json, os, shutil, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); FD = os.path.join(HERE, '..')
SP = os.path.join(FD, 'SUMMARY.json'); BK = os.path.join(FD, 'SUMMARY_r2.json')
if not os.path.exists(BK): shutil.copyfile(SP, BK)
assert hashlib.md5(open(BK, 'rb').read()).hexdigest() == '1d14cc2f2d167c0080f913de7a6dd1ca'
O = json.load(open(os.path.join(HERE, 'model_r3_out.json'))); A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
S = json.load(open(BK)); m, pre, PX = O['main'], O['pre'], O['price']
r1 = lambda x: int(round(x))
lab = lambda s: 'DƯỚI vùng' if PX < s['p10'] else ('TRÊN vùng' if PX > s['p90'] else 'TRONG vùng')
alts = O['alts']; L = O['liq']
S.update(round='r3', job='Taylor_20261108_180128', asof_price_date=O['pxd'], price=PX, price_date=O['pxd'], price_source='BQ tav2_bq.ticker Price (calc_r3/px_fpt_r3_20261106.csv)', r=O['r'],
  r_anchor=dict(r=0.135, rate=O['dep']['d0']['rate'], source=O['dep']['d0']['rate_source'], dep_asof=O['dep']['d1']['rate'], dep_asof_source=O['dep']['d1']['rate_source'], rule='r = 13,5% + 1,0 x (dep_12T - 7,40%)'),
  center_pre_liq=r1(pre['center']), center_post_liq=r1(m['center']), p10_post=r1(m['p10']), p25_post=r1(m['p25']), p50_post=r1(m['p50']), p75_post=r1(m['p75']), p90_post=r1(m['p90']),
  p10_pre=r1(pre['p10']), p50_pre=r1(pre['p50']), p90_pre=r1(pre['p90']), p10_out=r1(m['p10']), p50_out=r1(m['p50']), p90_out=r1(m['p90']),
  pct_weight_below_price=m['pct_below_px'], n_outcomes=m['n'], grid_n=m['n'], min_outcome=r1(m['min']), central_param_value_post=r1(O['central']), liq_disc_5ty=L['d_ref'],
  px_vs_center_post=PX / m['center'] - 1, px_vs_p10_post=PX / m['p10'] - 1, px_vs_p90_post=PX / m['p90'] - 1, label=lab(m), drivers=O['drivers'],
  label_by_size={'5ty': dict(center=r1(m['center']), p10=r1(m['p10']), p90=r1(m['p90']), label=lab(m), ck=L['d_ref']),
                 'sleeve_40tr': dict(center=r1(O['sleeve40']['center']), p10=r1(O['sleeve40']['p10']), p90=r1(O['sleeve40']['p90']), label=lab(O['sleeve40']), ck=L['d_40tr'])},
  rule4={'5ty': dict(threshold=r1(0.85 * m['center']), pass_=PX <= 0.85 * m['center']), 'sleeve_40tr': dict(threshold=r1(0.85 * O['sleeve40']['center']), pass_=PX <= 0.85 * O['sleeve40']['center'])},
  ck_ref_size=dict(size='5 ty', adv250=L['adv250']['adv_med'], adv60=L['adv60']['adv_med'], ck_adv250=L['d_ref'], ck_adv60=L['d_ref_adv60'], part_adv250=L['adv250']['part']['5000000000']),
  ck_real_sleeve={'10tr': L['d_10tr'], '40tr': L['d_40tr'], 'note': 'Q/ADV250 < 0,1% => duoi vung hieu chinh luat can bac hai; CK that ~ nua spread, chua do'},
  zone_old_r2=dict(center=S['center_post_liq'], p10=S['p10_post'], p90=S['p90_post'], label=S['label'], price=S['price']),
  center_change_vs_old=r1(m['center']) - S['center_post_liq'],
  grid_desc='540 ket cuc = scen(3; 0,275/0,45/0,275) x dconv(5) x dg(3) x FRT(3) x lien ket khac(4); RONIC terminal = Ke; tru CDKKS; FTEL CK 0%; FOX/FRT thi gia 06/11; wpct mid-block',
  axes_included=['kich ban XAU/CO_SO/TOT 0,275/0,45/0,275 [UL doi xung]', 'dich conv 5 nam -0,20..+0,20 (deu, san 0,10)', 'dich g -1/0/+1pp (sau RONIC=Ke chi con tac dung qua (1+g)/Ke)',
                 'FRT quanh thi gia 06/11 +20/0/-20% (0,25/0,5/0,25) [UL]', 'lien ket khac + TPB/FTS lech so -1.300/0/+1.100/+2.600 d/cp (0,2/0,3/0,3/0,2) [UL; SKEPTIC_20261101 T6a/T6b]'],
  axes_excluded=[dict(axis='r (Ke)', reason='luat neo lai huy dong; song song co_truc_r_pm1pp'),
                 dict(axis='CK FTEL 30/15/0%', reason='do lon [UL]; luat user CK holding/quan tri ra do nhay, base 0%; gia FOX da la gia co phan thieu so; song song A'),
                 dict(axis='chan RONIC 5 nam (25,5%/17,7%/Ke)', reason='RONIC 5 nam co mot phan du lieu (2025 ~48%); do nhay E/F/G'),
                 dict(axis='lai LK Q4/25 740', reason='600 la uoc luong chua kiem; do nhay H'),
                 dict(axis='tien khach ung truoc 2.370 ty', reason='float theo mua; do nhay I')],
  base_adjustments=[dict(item='loi ich CDKKS', effect_dong_per_share=r1(-1165.791218519 / 1885.727648 * 1e3), basis='ma 429 BCD HN 30/09/2026 (tien rong cong 100%)', source='dd_FPT_20261101/calc/notes_q3_bctc.md:85'),
                    dict(item='FOX 45,66% thi gia 06/11', effect_dong_per_share=0, basis='thi gia, CK 0% base', source='BQ px_fpt_r3_20261106.csv'),
                    dict(item='FRT 46,54% thi gia 06/11', effect_dong_per_share=0, basis='thi gia', source='BQ px_fpt_r3_20261106.csv'),
                    dict(item='XDCB khuon vien GD 760 ty', effect_dong_per_share=0, basis='gia so = NPV0', source='Q3HN p37'),
                    dict(item='Lien ket khac 1.500 ty', effect_dong_per_share=0, basis='theo so (uoc luong, BCTC khong tach); lech so o truc oth', source='uoc luong')],
  assumptions=A['assumptions'],
  headline_vs_alternatives=dict(headline=dict(center=r1(m['center']), p10=r1(m['p10']), p50=r1(m['p50']), p90=r1(m['p90']), pct_below=m['pct_below_px'], label=lab(m)),
    **{k: dict(center=r1(s['center']), p10=r1(s['p10']), p50=r1(s['p50']), p90=r1(s['p90']), pct_below=s['pct_below_px'], label=lab(s)) for k, s in alts.items()}),
  implied_by_price=dict(r=O['implied']['r'], dep12_implied=O['implied']['dep12_implied'], ronic_phase_cap=O['implied']['ronic_phase_cap'], r_if_keep_ftel_discount=O['implied']['r_altA'],
    w_xau='0,693 neu CO_SO:TOT giu ti le 0,45:0,275 (implied_wx_check.txt); voi CO_SO co dinh 0,45 thi w XAU 0,55 (TOT 0) van cho tam 53.031 > gia'),
  bridge_r2_to_r3=O['bridge'], sens_r=O['sens_r'], gordon_crosscheck={k: r1(v) for k, v in O['gordon'].items()},
  center_vs_p50_note=f"tam = ky vong luoi {m['center']:,.0f}; P50 {m['p50']:,.0f}; gia tri tai tham so trung tam {O['central']:,.0f}. P10 do rieng nhanh XAU quyet dinh, P90 do rieng TOT.",
  r2_at_new_price_pct_below=O['r2_at_newpx_pct_below'],
  open_issues=['lai LK Q4/25 600 ty chua kiem (GAPS G10)', 'tam nhay voi chan RONIC 5 nam: ROIC5Y 17,7% => 52.311; Ke => 50.652 (~gia)', 'vay ngoai te 30/09 trung 30/06 (G15)', 'BC quan tri 6T/2026 chua doc (G7)', 'ETR 11,1% -> 15,2% chua ro (G11)', 'phap ly sau 01/11 chua quet'],
  change_reason='r3: D1 trong so doi xung, D2 RONIC_T=Ke, D3 tru CDKKS, D4 gia 06/11, D7 CK FTEL ra do nhay (base 0%); D5/D6 do nhay',
  lock_md5='calc_r3/LOCK_r3_prerun.txt (truoc chay) + calc_r3/LOCK_r3_post_md5.txt', fear_buy_eligible_2_5=False,
  fear_buy_note='KHONG du dieu kien §2.5 (truot DK1 khong co trang thai so hai/scandal, DK4)')
json.dump(S, open(SP, 'w'), ensure_ascii=False, indent=1, default=float)
print('SUMMARY.json r3:', S['center_post_liq'], S['p10_out'], S['p90_out'], S['label'], S['rule4'])
