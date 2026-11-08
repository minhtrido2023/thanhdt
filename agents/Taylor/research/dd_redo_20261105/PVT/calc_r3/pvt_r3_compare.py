"""PVT VONG 3 — SAU KHOA: kiem md5 moi dong LOCK cua LOCK_md5.txt (outputs + upstream) roi moi doc gia 06/11 (px_pvt_r3_20261106.csv, BQ tav2_bq.ticker).
-> ../SUMMARY.json (backup ../SUMMARY_r2.json 1 lan) + compare_r3_out.txt. Chay: $DNA_PYEXE -I pvt_r3_compare.py"""
import csv, hashlib, json, math, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); ROOT = os.path.dirname(BASE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, '_shared'))
import numpy as np                     # noqa: E402
from wpct import wpct, weight_below    # noqa: E402
sec = None
for line in open(os.path.join(HERE, 'LOCK_md5.txt')):
    p = line.split()
    if not p or p[0] in ('#', 'POST'):          # POST = md5 ghi SAU khi doc gia (khong phai dau vao)
        continue
    if p[0] == '##':
        sec = line; continue
    h, f = (p[1], os.path.join(ROOT, p[2])) if p[0] == 'LOCK' else (p[0], os.path.join(HERE, p[1]))
    assert hashlib.md5(open(f, 'rb').read()).hexdigest() == h, f'doi sau khoa: {f}'
import pvt_r3 as M                     # noqa: E402
O = json.load(open(os.path.join(HERE, 'pvt_r3_out.json')))
ASOF = '2026-11-06'; Q_REF = 5e9; SLEEVE = (10e6, 20e6, 40e6); CALIB = (0.001, 0.20)


def liq():
    rows = sorted((r for r in csv.DictReader(open(os.path.join(HERE, 'px_pvt_r3_20261106.csv'))) if r['ticker'] == 'PVT'), key=lambda r: r['time'])
    assert rows[-1]['time'] == ASOF
    out = dict(px=float(rows[-1]['Price']), pxd=rows[-1]['time'])
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        out[f'w{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), adv_med=adv, sigma_d=sig,
                            sizes={f'{q/1e6:.0f}tr': dict(q_over_adv=q / adv, disc=sig * math.sqrt(q / adv), in_calib=bool(CALIB[0] <= q / adv <= CALIB[1]),
                                                          days_at_15pct=q / (0.15 * adv)) for q in (Q_REF,) + SLEEVE})
    out['d_ref'] = out['w250']['sizes']['5000tr']['disc']
    return out


def summ(vals, wts, cpre, cparam, px, d):
    f = 1 - d; q = wpct(vals, wts, (0.10, 0.25, 0.50, 0.75, 0.90)); post = [v * f for v in vals]
    return dict(n_outcomes=len(vals), center_pre=round(cpre), center_post=round(cpre * f), center_param_post=round(cparam * f),
                p10_out=round(q[0.10] * f), p25_out=round(q[0.25] * f), p50_out=round(q[0.50] * f), p75_out=round(q[0.75] * f), p90_out=round(q[0.90] * f),
                min_out=round(min(post)), max_out=round(max(post)), pct_weight_below_price=round(weight_below(post, wts, px), 4),
                label=('DƯỚI vùng' if px < q[0.10] * f else ('TRÊN vùng' if px > q[0.90] * f else 'TRONG vùng')))


def bisect(fn, lo, hi, target, it=80):
    for _ in range(it):
        mid = (lo + hi) / 2
        if (fn(mid) - target) * (fn(lo) - target) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2


L = liq(); px = L['px']; d = L['d_ref']; f = 1 - d
S0 = summ(O['outcomes_vals'], O['outcomes_wts'], O['center_pre'], O['center_param_pre'], px, d)
par = {k: dict(desc=P['desc'], **summ(P['vals'], P['wts'], P['center_pre'], P['center_pre'], px, d)) for k, P in O['parallel'].items()}
for v in par.values():
    v.pop('center_param_post'); v.pop('center_pre')
# r2 tai gia moi (dinh chinh 5): ket cuc r2, CK r2 (ADV den 04/11)
SUMP = os.path.join(BASE, 'SUMMARY.json'); BK = os.path.join(BASE, 'SUMMARY_r2.json')
if not os.path.exists(BK):
    shutil.copy(SUMP, BK)
r2o = json.load(open(os.path.join(BASE, 'calc', 'model_r2_out.json'))); R2S = json.load(open(BK))
r2_post = [v * (1 - R2S['liq_disc_5ty']) for v in r2o['outcomes_vals']]
r2_below_new_px = weight_below(r2_post, r2o['outcomes_wts'], px)
# gia ngu y
roe_impl = bisect(lambda x: M.center(dict(M.R3, roe_mid=x)) * f, 0.05, 0.30, px)
r_impl = bisect(lambda x: M.center(M.R3, r_base=x) * f, 0.09, 0.20, px)
roe_impl_point = bisect(lambda x: M.value_ps('coso', 1.0, M.R0, 'khong', dict(M.R3, roe_mid=x)) * f, 0.05, 0.30, px)
hist = sorted(M.M1.ROE_HIST.items())
roe_1825 = float(np.median([v for k, v in hist if int(k) >= 2018]))
implied = dict(roe_mid_for_center_eq_px=roe_impl, roe_mid_point_coso_eq_px=roe_impl_point, roe_mid_base=M.ROE_MID, roe_median_2018_25=roe_1825,
               roe_hist_q4=dict(hist), r_for_center_eq_px=r_impl, dep12t_implied=0.074 + (r_impl - 0.135),
               note=f'Gia {px:.0f} = ROE giua chu ky {roe_impl:.2%} vinh vien tren luoi r3 (base {M.ROE_MID:.2%} trung vi 2015-25; trung vi 2018-25 {roe_1825:.2%}) '
                    f'hoac r {r_impl:.2%} (lai huy dong 12T ngu y {0.074 + r_impl - 0.135:.2%} vs 7,40%).')
R2 = R2S; assert R2['round'] == 2
A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))['assumptions']
bridge = []
prev = R2['center_post']
bridge.append(dict(step='r2 cong bo (gia 04/11 21.000, CK ADV den 04/11)', center_post=R2['center_post'], delta=0, reason='diem xuat phat; tai lap center_pre 17.794 trung (control)'))
bridge.append(dict(step='doi gia tham chieu 21.000 (04/11) -> 20.550 (06/11) + CK theo ADV den 06/11', center_post=round(O['bridge_pre'][0]['center_pre'] * f),
                   delta=round(O['bridge_pre'][0]['center_pre'] * f) - prev, reason=f'dinh chinh 5; % trong so r2 duoi gia moi = {r2_below_new_px:.1%} (skeptic 72,2%); CK 5 ty {R2["liq_disc_5ty"]:.4%} -> {d:.4%}'))
prev = bridge[-1]['center_post']
reasons = ['dinh chinh 1a: trong so 0,35/0,45/0,20 la nhan dinh Bobby, khong co du lieu -> doi xung; lech xuong sang do nhay',
           'dinh chinh 1b: he so ROE theo kich ban 0,85 dem chu ky 2 lan voi trung vi 2015-25 -> 0,9/1/1,1; NPV tau ky vong ve 0',
           'dinh chinh 2 (ap mot phan): np27 co so = Q3 x4 = 1.500 (du lieu) thay 1.250; skeptic 1.450 -> do nhay (lech -50 khong co co so)']
for b, rsn in zip(O['bridge_pre'][1:], reasons):
    cpost = round(b['center_pre'] * f); bridge.append(dict(step=b['step'], center_post=cpost, delta=cpost - prev, reason=rsn)); prev = cpost
assert bridge[-1]['center_post'] == S0['center_post']
alts = [dict(name='HEADLINE r3', center_post=S0['center_post'], p10_out=S0['p10_out'], p90_out=S0['p90_out'], label=S0['label'], pct_below=S0['pct_weight_below_price'])]
for k in ('np27_skeptic_1450', 'np27_r2_1250_sym', 'bobby_asym', 'w_asym_only', 'mid_asym_only', 'ship_npv0', 'roe_ex_net_interest', 'plan_anchor'):
    v = par[k]; alts.append(dict(name=k, desc=v['desc'], center_post=v['center_post'], p10_out=v['p10_out'], p90_out=v['p90_out'], label=v['label'], pct_below=v['pct_weight_below_price']))
alts.append(dict(name=f'r +-100bp', center_post={k: round(v * f) for k, v in O['r_sens_pre'].items()}))
S = dict(ticker='PVT', round=3, job='Taylor_20261108_153736', asof_price_date=L['pxd'], price=px, r=O['r'],
         r_anchor=dict(r=0.135, dep_anchor_03_11=O['dep_anchor'], dep_asof_06_11=O['dep_asof'], rule='r = 13,5% + 1,0 x (dep12T hieu dung - 7,40%)'))
S.update(S0)
S.update(center_pre_liq=S0['center_pre'], center_post_liq=S0['center_post'], p10_post=S0['p10_out'], p25_post=S0['p25_out'], p50_post=S0['p50_out'],
         p75_post=S0['p75_out'], p90_post=S0['p90_out'], p10_pre=None, liq_disc_5ty=d, grid_n=S0['n_outcomes'], min_outcome=S0['min_out'],
         px_vs_center_post=px / S0['center_post'] - 1, px_vs_p10_post=px / S0['p10_out'] - 1, px_vs_p90_post=px / S0['p90_out'] - 1)
q = wpct(O['outcomes_vals'], O['outcomes_wts']); S.update(p10_pre=round(q[0.10]), p50_pre=round(q[0.50]), p90_pre=round(q[0.90]))
S['grid_desc'] = ('ket cuc = kich ban LN me 2027 1.250/1.500/1.750 (w 0,275/0,45/0,275 doi xung; he so ROE theo kich ban 0,9/1,0/1,1) x he so ROE giua chu ky 0,8..1,2 (deu; nen trung vi ROE_Trailing Q4 2015-25 BQ 13,15%) '
                  'x lai huy dong -50/0/+50bp (0,25/0,5/0,25) x mua tau phan capex 2026 con lai 2.465 ty / khong (0,5/0,5) voi NPV -30/0/+30% theo kich ban (ky vong 0); n=90; '
                  'tham so trung tam = co so, m=1, dr=0, khong mua')
S['ck_ref_size'] = dict(q_vnd=Q_REF, adv='250 phien', disc=d, in_calib=L['w250']['sizes']['5000tr']['in_calib'], disc_adv60=L['w60']['sizes']['5000tr']['disc'],
                        q_over_adv250=L['w250']['sizes']['5000tr']['q_over_adv'])
S['ck_real_sleeve'] = {k: dict(disc_adv250=L['w250']['sizes'][k]['disc'], disc_adv60=L['w60']['sizes'][k]['disc'], q_over_adv250=L['w250']['sizes'][k]['q_over_adv'],
                               in_calib=L['w250']['sizes'][k]['in_calib'], center_post=round(O['center_pre'] * (1 - L['w250']['sizes'][k]['disc'])))
                       for k in ('10tr', '20tr', '40tr')}
S['ck_real_sleeve_note'] = 'cỡ sleeve 10–40 tr: Q/ADV ~0,01–0,04% NGOÀI vùng hiệu chỉnh luật căn bậc hai (0,1–20%) ⇒ CK ≈ 0 (chỉ là cận trên), giá trị ≈ tâm trước CK'
S['liquidity'] = L
S['parallel'] = par
S['headline_vs_alternatives'] = alts
S['bridge_r2_to_r3'] = bridge
S['implied_by_price'] = implied
S['assumptions'] = A
S['control_r2_reproduced'] = dict(center_pre=O['control_r2_center_pre'], file=O['r2_center_pre_file'], ok=abs(O['control_r2_center_pre'] - O['r2_center_pre_file']) < 0.5)
S['r_sens_pre'] = {k: round(v) for k, v in O['r_sens_pre'].items()}; S['r_sens_post'] = {k: round(v * f) for k, v in O['r_sens_pre'].items()}
S['scenarios_pre'] = {k: round(v) for k, v in O['scenarios_pre'].items()}
S['gordon_roe_xcheck'] = O['gordon_roe_xcheck']
S['axes_included'] = ['LN 2027 / chu ky cuoc (hai chieu, doi xung quanh Q3x4)', 'ROE giua chu ky (hai chieu)', 'lai huy dong (hai chieu)', 'mua tau o dinh (NPV doi xung, ky vong 0)']
S['axes_excluded'] = [
    dict(axis='nhan dinh Bobby lech xuong (trong so 0,35/0,45/0,20, he so ROE 0,85)', reason='chi la nhan dinh, khong co du lieu; trung vi 2015-25 da gom day 2015-17 — bao song song bobby_asym'),
    dict(axis='TT99 (ngung trich truoc sua chua lon) thien lech LN 2026 → np27', reason='do lon chua xac dinh tu text BCTC (can BCTC nam 2026); cận dưới thấy được: hoàn nhập dự phòng 85,4 tỷ/9T phi tiền mặt; xem do nhay np27_skeptic_1450 / np27_r2_1250_sym (−65/−335 đ) — WARNING'),
    dict(axis='ke hoach 5 nam NQ HDQT (LN thap hon)', reason='muc tieu ban dieu hanh than trong (KH 2026 LNST HN 1.200 vs 9T thuc 1.581,8); khong thay ROE lich su 11 nam — song song plan_anchor'),
    dict(axis='PVT Logistics (PDV) chao ban ~56,9 tr cp @10.000 cho co dong hien huu (~569,5 ty, Q4/2026–Q2/2027)', reason='quyen mua theo ty le; neu PVT mua du = khong pha loang, chi la phan bo von (NPV0); neu khong mua = pha loang NCI o cong ty con nho — chua co du lieu PVT dang ky; WARNING')]
S['base_adjustments'] = [dict(item='khong tru no rong 619,3 (da nam trong LN sau lai vay va VCSH)', effect_dong_per_share=0, basis='dinh gia FCFE co dong me', source='BCDKT Q3/2026'),
                         dict(item='tau moi: NPV ky vong 0 (doi xung)', effect_dong_per_share=round(O['ship_npv_expected_pre']), basis='luat 03/11 NPV0; r2 co -86 d/cp do trong so lech', source='DHDCD 2026; TM12')]
S['center_vs_p50_note'] = (f"tâm (kỳ vọng trọng số lưới, sau CK 5 tỷ) {S0['center_post']} vs P50 kết cục {S0['p50_out']} vs giá trị tại tham số trung tâm {S0['center_param_post']}. "
                           "Lưới đối xứng ⇒ ba số sát nhau; không nhánh trọng số nhỏ nào quyết định riêng P10/P90 (P10 do xấu×m thấp×r+50bp, P90 do tốt×m cao×r−50bp).")
S['center_change_vs_old'] = dict(vs_r2=S0['center_post'] - R2['center_post'], vs_r2_pct=S0['center_post'] / R2['center_post'] - 1)
S['center_change_vs_old_basis'] = 'r2 center_post 17.675 (SUMMARY_r2.json) -> r3; cầu chi tiết bridge_r2_to_r3'
S['change_reason'] = ('Vòng 3: đối xứng trọng số kịch bản (0,275/0,45/0,275) và hệ số ROE (0,9/1/1,1) — lệch xuống của Bobby sang độ nhạy; LN mẹ 2027 cơ sở = Q3×4 1.500 (±250); '
                      'kiểm chéo ROE theo lãi RÒNG thay lãi gửi một chiều; giá 06/11 20.550; warning PDV chào bán; provenance VCSH mẹ/lãi gửi kiểm từ text BCTC')
S['r2'] = dict(center_post=R2['center_post'], p10_out=R2['p10_out'], p50_out=R2['p50_out'], p90_out=R2['p90_out'], label=R2['label'], price=R2['price'],
               pct_below_at_r2_price=R2['pct_weight_below_price'], pct_below_at_20550=round(r2_below_new_px, 4))
S['zone_r2'] = dict(low=R2['p10_out'], center=R2['center_post'], high=R2['p90_out'])
S['zone_old'] = R2.get('zone_old')
for k in ('free_float', 'free_float_src', 'fear_buy_25', 'new_data_obs'):
    S[k] = R2.get(k)
S['fear_buy_eligible_2_5'] = False
S['fear_buy_25'] = ('KHÔNG đủ điều kiện §2.5: không khủng hoảng, LN ở đỉnh chu kỳ ("đáy chưa tới"), drawdown từ đỉnh 52 tuần < ngưỡng T1 35%. '
                     'Đính chính câu r2 "P/B 1,10 > trung vị 0,91": skeptic 29/10 §14.1 — cùng gốc (VCSH gồm NCI) P/B ≈ 0,86, giữa p25 0,82 và trung vị 0,91 ⇒ lý do P/B bị bỏ, kết luận NON không đổi.')
S['warnings'] = R2['warnings'] + [
    'PVT Logistics (PDV, công ty con) chào bán ~56,9 tr cp @10.000 cho cổ đông hiện hữu (~569,5 tỷ) đầu tư tàu tối đa 29 tr USD, Q4/2026–Q2/2027 (doanhnhan.baophapluat.vn, tra 08/11/2026); rủi ro mua tàu ở đỉnh + pha loãng NCI nếu PVT không mua đủ — r2 viết "chưa có đợt cụ thể" là SAI cho cấp công ty con; HOSE từng nhắc nhở PDV chậm công bố thương vụ mua tàu PVT Opal',
    'Ý kiến kiểm toán BCTC 2025 / soát xét H1/2026: CHƯA KIỂM ĐƯỢC (WebSearch 08/11/2026 không ra văn bản ý kiến; text BCTC Q3 không có). Không định lượng được; nếu có ngoại trừ liên quan dry-dock/TT99 ⇒ np27 lệch như độ nhạy np27_r2_1250_sym (−335 đ/cp)']
S['open_issues'] = ['Ý kiến kiểm toán 2025 / soát xét H1 (chưa kiểm, xem warning)', 'Định lượng TT99', 'TC/spot + đáo hạn HĐ', 'PVT có đăng ký mua quyền PDV không', 'Room ngoại']
S['corrections_check'] = [
    dict(item=1, verdict='ĐÚNG — áp', evidence=f"tái lập skeptic: chỉ đối xứng trọng số {par['w_sym_only_r2np']['center_post']} (18.212), chỉ hệ số {par['mid_sym_only_r2np']['center_post']} (18.050), cả hai {par['np27_r2_1250_sym']['center_post']} (18.506); NPV tàu kỳ vọng {O['ship_npv_expected_pre']:.2f} đ"),
    dict(item=2, verdict='ĐÚNG hướng — áp một phần', evidence=f"skeptic 1.450 → {par['np27_skeptic_1450']['center_post']} (18.774 trùng); chọn 1.500 = Q3×4 (dữ liệu, đúng lý do r1 'biên như Q3'); −50 của skeptic không có cơ sở → độ nhạy (−{S0['center_post'] - par['np27_skeptic_1450']['center_post']} đ)"),
    dict(item=3, verdict='ĐÚNG — áp', evidence=f"lãi gửi 251,0 < lãi vay 345,6 /9T ⇒ lãi ròng phần mẹ {O['gordon_roe_xcheck']['net_interest_parent_yr']:.0f} tỷ/năm; ROE bỏ lãi ròng {O['gordon_roe_xcheck']['roe_mid_ex_net_interest']:.2%} (r2 một chiều 10,97%); bản sửa (trừ nợ ròng) {par['roe_ex_net_interest']['center_post']} — chỉ kiểm chéo, bỏ bản r2 khỏi §0"),
    dict(item=4, verdict='ĐÚNG — áp', evidence='warning PDV chào bán thêm; ý kiến kiểm toán 2025 đóng thành "chưa kiểm" có ghi rõ'),
    dict(item=5, verdict='ĐÚNG — áp', evidence=f"BQ 06/11 Price {px:.0f}; % trọng số r2 dưới 20.550 = {r2_below_new_px:.1%}"),
    dict(item=6, verdict='ĐÚNG — đã kiểm (text, không phải PDF)', evidence='VCSH 12.862.928.406.161 − CĐKKS 3.007.359.354.829 = 9.855,569 tỷ (text dòng 933/1005); lãi tiền gửi, cho vay 9T 250.953.803.131 (dòng 4249); lãi vay 345.641.490.397 (dòng 1171). PDF gốc không mở được (pymupdf không chạy vì không có file PDF local)')]
S['lock_md5'] = 'PVT/calc_r3/LOCK_md5.txt'
json.dump(S, open(SUMP, 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'compare_r3_out.txt'), 'w') as fo:
    for k in ('price', 'asof_price_date', 'r', 'n_outcomes', 'center_pre', 'center_post', 'center_param_post', 'p10_out', 'p25_out', 'p50_out', 'p75_out', 'p90_out',
              'min_out', 'max_out', 'pct_weight_below_price', 'px_vs_center_post', 'label', 'liq_disc_5ty'):
        print(f'{k}: {S[k]}', file=fo)
    print('r2:', json.dumps(S['r2'], ensure_ascii=False), file=fo)
    for b in bridge:
        print(f"bridge {b['step']}: {b['center_post']} ({b['delta']:+d})", file=fo)
    for a in alts:
        print('alt', json.dumps(a, ensure_ascii=False), file=fo)
    print('implied', json.dumps({k: v for k, v in implied.items() if k != 'roe_hist_q4'}, ensure_ascii=False), file=fo)
    for n in ('w250', 'w60'):
        w = L[n]
        print(f"{n} {w['window']} ADV {w['adv_med']/1e9:.2f} ty sigma {w['sigma_d']:.4f} | " +
              ' | '.join(f"{k}: CK {v['disc']:.3%} Q/ADV {v['q_over_adv']:.4%} calib={v['in_calib']}" for k, v in w['sizes'].items()), file=fo)
print(open(os.path.join(HERE, 'compare_r3_out.txt')).read())
