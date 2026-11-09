import json, hashlib, os
H = os.path.dirname(os.path.abspath(__file__)); o = json.load(open(os.path.join(H, 'model_out.txt'))); A = json.load(open(os.path.join(H, 'assumptions.json')))
md5 = hashlib.md5(open(os.path.join(H, 'assumptions.json'), 'rb').read()).hexdigest()
px = o['price']; p = o['post_5ty']; q = o['pre']; s40 = o['post_40tr']
def lab(c, lo, hi): return 'DƯỚI vùng' if px < lo else ('TRÊN vùng' if px > hi else 'TRONG vùng')
S = dict(ticker='GAS', asof_price_date=o['price_date'], price=px, r=o['r'],
  r_anchor=dict(r=0.135, rate=0.074, source='cctg_12m(2026-11-02)', rule='r = 13,5% + 1,0 x (dep_12T - 7,40%)'),
  center_pre_liq=round(q['center']), center_post_liq=round(p['center']), p10_post=round(p['p10']), p25_post=round(p['p25']), p50_post=round(p['p50']), p75_post=round(p['p75']), p90_post=round(p['p90']),
  p10_pre=round(q['p10']), p50_pre=round(q['p50']), p90_pre=round(q['p90']),
  kind='expected_weighted', center_kind='expected_weighted',
  liq_disc_5ty=o['liq250']['ck']['5000000000'], liq_disc_40tr=o['liq250']['ck']['40000000'],
  px_vs_center_post=px / p['center'] - 1, px_vs_p10_post=px / p['p10'] - 1, px_vs_p90_post=px / p['p90'] - 1,
  label=lab(p['center'], p['p10'], p['p90']), pct_weight_below_price=o['pct_weight_below_price'],
  grid_n=p['n'], grid_desc='243 = kich ban(3; 0,275/0,45/0,275) x he so Brent(3) x du phong DH 343(3) x Brent dai han +-5(3) x muc ben phan du LN 2026(3); RONIC=Ke; tien rong theo so; XDCB NPV0',
  label_by_size={'5ty': dict(center=round(p['center']), p10=round(p['p10']), p90=round(p['p90']), label=lab(0, p['p10'], p['p90']), ck=o['liq250']['ck']['5000000000']),
                 'sleeve_40tr': dict(center=round(s40['center']), p10=round(s40['p10']), p90=round(s40['p90']), label=lab(0, s40['p10'], s40['p90']), ck=o['liq250']['ck']['40000000'])},
  sens_r={k: round(v) for k, v in o['sens_r'].items()}, implied_by_price=dict(r=o['implied_r'], note='r=8% van cho tam 63.446 < gia (calc/sens_r_wide.txt)'),
  scen_central={k: round(v) for k, v in o['scen_central'].items()},
  net_cash_per_share=round(o['net_cash_per_sh']),
  moat=dict(tier='NARROW', type='REGULATORY/INFRA (doc quyen tu nhien trung nguon ong + xu ly khi)', durable=False, params_added='khong', sens_wide_no_decline=round(o['sens_moat_wide_no_decline']), sens_none_decline_plus3pp=round(o['sens_moat_none_decline_plus3pp']), moat_tags_csv='chua co dong GAS -> de xuat trong REPORT'),
  lag_surprise=dict(np_q3_26=4576.5, np_q3_25=2549.1, yoy=4576.5 / 2549.1 - 1, np_9t_26=13381.2, np_9t_25=10053.3, yoy_9t=13381.2 / 10053.3 - 1, np_q2_26=5860.1, qoq=4576.5 / 5860.1 - 1, driver='Brent Q3 90,7 vs 68,0 (+33%); khong phai khoan mot lan', durable='CHU KY (theo Brent) - khong ben'),
  auto_flags=dict(CEIL2_20260810='THAT nhung chieu TANG (tran 07/08 +6,9% & 10/08 +6,97% sau KQ Q2); TTL 30 ngay het 09/09; khong la rui ro', DCF_auto_RICH_67081='CUNG CHIEU, doc lap thap hon (tam 46.488)', PE_12_1='dung (TTM 14.742 ty / 2,413 ty cp = 6.110 d; 74.100/6.110 = 12,1) nhung LN TTM o Brent 82, cao hon trung binh chu ky'),
  warnings=['KHONG CON DU DIEU KIEN CONG TY DAI CHUNG: PVN 95,76%, co dong nho 4,24% < 10% (CBTT 31/12/2025); han 1 nam -> neu khong khac phuc phai nop ho so huy tu cach dai chung (rui ro huy niem yet/thoai von PVN cung cap lon) [WARNING, khong vao tam]',
            'Thay Chu tich HDQT (23/07/2026) va TGD (21/07/2026) - PVN dieu dong; DHDCD bat thuong 14/09/2026 mien nhiem 3 TV HDQT',
            'Cuoc van chuyen duong ong nhieu nam chay gia tam tinh (sector read Bobby) - rui ro truy thu/hoan tra hoi to (do nhay -1.500 ty = -618 d/cp)',
            'Bao tieu: tien khi cam ket theo bao tieu 1.775,5 ty tra truoc (giam tu 2.122,6) - dang thu hoi',
            'Soat xet 6T/2026 Deloitte: chap nhan toan phan'],
  open_issues=['thuyet minh du phong phai tra DH 3.300 ty chua doc (gia dinh ARO)', 'co cau san luong theo mo/khach hang chua co (BCTC quy khong tach)', 'cong thuc gia ban khi/tran-san chua kiem tu nguon goc', 'phuong an tang von/thoai von PVN de dat 10% free float chua co chi tiet', 'ty trong Q3 cua hoan nhap DP 9T/26 492 ty'],
  assumptions_md5=md5, assumptions_file='calc/assumptions.json', lock_md5='calc/LOCK_prerun.txt + calc/LOCK_post_md5.txt',
  fear_buy_eligible_2_5=False, job='Taylor_20261109_073604', round='r1')
json.dump(S, open(os.path.join(H, '..', 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False); print(json.dumps({k: S[k] for k in ('center_post_liq', 'p10_post', 'p90_post', 'label', 'px_vs_p90_post', 'assumptions_md5')}, ensure_ascii=False))
