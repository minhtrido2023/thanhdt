"""TCH VONG 3 — SAU KHOA: kiem md5 moi dong cua LOCK_md5.txt roi moi doc gia 06/11 (px_tch_r3_20261106.csv, BQ tav2_bq.ticker).
-> ../SUMMARY.json (r2 da backup ../SUMMARY_r2.json) + compare_r3_out.txt. Chay: /home/trido/thanhdt/wc_venv/bin/python -I tch_r3_compare.py"""
import csv, hashlib, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); ROOT = os.path.dirname(BASE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, '_shared'))
import numpy as np                     # noqa: E402
from wpct import wpct, weight_below    # noqa: E402
for line in open(os.path.join(HERE, 'LOCK_md5.txt')):
    p = line.split()
    if not p or p[0] in ('#', '##', 'POST'):
        continue
    h, f = (p[1], os.path.join(ROOT, p[2])) if p[0] == 'LOCK' else (p[0], os.path.join(HERE, p[1]))
    assert hashlib.md5(open(f, 'rb').read()).hexdigest() == h, f'doi sau khoa: {f}'
import tch_r3 as M                     # noqa: E402  (chay lai, ghi trung byte)
O = json.load(open(os.path.join(HERE, 'tch_r3_out.json')))
ASOF = '2026-11-06'; Q_REF = 5e9; SLEEVE = (10e6, 20e6, 40e6); CALIB = (0.001, 0.10)


def liq():
    rows = sorted((r for r in csv.DictReader(open(os.path.join(HERE, 'px_tch_r3_20261106.csv'))) if r['ticker'] == 'TCH'), key=lambda r: r['time'])
    assert rows[-1]['time'] == ASOF
    out = dict(px=float(rows[-1]['Price']), pxd=rows[-1]['time'], px_5d_ago=float(rows[-6]['Price']), px_5d_ago_date=rows[-6]['time'])
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        out[f'w{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), n_zero_vol=int((v[1:] == 0).sum()), adv_med=adv, sigma_d=sig,
                            sizes={f'{q/1e6:.0f}tr': dict(q_over_adv=q / adv, disc=sig * math.sqrt(q / adv), in_calib=bool(CALIB[0] <= q / adv <= CALIB[1]),
                                                          days_at_15pct=q / (0.15 * adv)) for q in (Q_REF,) + SLEEVE})
    out['d_ref'] = out['w250']['sizes']['5000tr']['disc']
    return out


def summ(vals, wts, px, d, cparam=None):
    f = 1 - d; q = wpct(vals, wts, (0.10, 0.25, 0.50, 0.75, 0.90)); post = [v * f for v in vals]; c = sum(a * b for a, b in zip(vals, wts)) / sum(wts)
    s = dict(n_outcomes=len(vals), center_pre=round(c), center_post=round(c * f),
             p10_out=round(q[0.10] * f), p25_out=round(q[0.25] * f), p50_out=round(q[0.50] * f), p75_out=round(q[0.75] * f), p90_out=round(q[0.90] * f),
             min_out=round(min(post)), max_out=round(max(post)), pct_weight_below_price=round(weight_below(post, wts, px), 4),
             label=('DƯỚI vùng' if px < q[0.10] * f else ('TRÊN vùng' if px > q[0.90] * f else 'TRONG vùng')))
    if cparam is not None:
        s['center_param_post'] = round(cparam * f)
    return s


def bisect(fn, lo, hi, target, it=80):
    flo = fn(lo) - target
    for _ in range(it):
        mid = (lo + hi) / 2; fm = fn(mid) - target
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return (lo + hi) / 2


L = liq(); px = L['px']; d = L['d_ref']; f = 1 - d
S0 = summ(O['outcomes_vals'], O['outcomes_wts'], px, d, O['center_param_pre'])
sizes = {k: summ(O['outcomes_vals'], O['outcomes_wts'], px, L['w250']['sizes'][k]['disc']) for k in ('10tr', '20tr', '40tr')}
par = {k: dict(desc=v['desc'], **summ(v['vals'], v['wts'], px, d)) for k, v in O['parallel'].items()}
R2S = json.load(open(os.path.join(BASE, 'SUMMARY_r2.json')))
v2, w2 = M.grid_r2(); r2_post = [v * (1 - R2S['liq_discount_ref']) for v in v2]
r2_below_new_px = weight_below(r2_post, w2, px)
mean = M.mean
g3 = lambda **kw: mean(*M.grid_r3(**kw)[:2])
implied = dict(
    hold_uniform_for_center_eq_px=bisect(lambda h: g3(hold_ax=((h, 1.0),)) * f, 0.0, 0.6, px),
    gov_for_center_eq_px=bisect(lambda g: g3(gov=g) * f, 0.0, 0.5, px),
    g_both_for_center_eq_px=bisect(lambda g: mean([M.nav(M.m_of(g + a), M.s_of(g + b), 0.0, M.R0 + c) for (a, _), (b, _), (c, _) in __import__('itertools').product(M.GAX, M.GAX, M.RAX)],
                                                  [x * y * z for (_, x), (_, y), (_, z) in __import__('itertools').product(M.GAX, M.GAX, M.RAX)]) * f, 0.12, 0.519, px),
    g_old_only_for_center_eq_px=bisect(lambda g: mean([M.nav(M.m_of(M.G_OBS + a), M.s_of(g + b), 0.0, M.R0 + c) for (a, _), (b, _), (c, _) in __import__('itertools').product(M.GAX, M.GAX, M.RAX)],
                                                      [x * y * z for (_, x), (_, y), (_, z) in __import__('itertools').product(M.GAX, M.GAX, M.RAX)]) * f, 0.06, 0.519, px),
    pb_at_price=px / O['bvps'])
implied['s_old_for_center_eq_px'] = M.s_of(implied['g_old_only_for_center_eq_px'])
implied['note'] = (f"Giá {px:.0f} ⇔ CK holding đều {implied['hold_uniform_for_center_eq_px']:.1%} (phần qua công ty con), HOẶC CK quản trị {implied['gov_for_center_eq_px']:.1%}, "
                   f"HOẶC biên gộp BĐS chung {implied['g_both_for_center_eq_px']:.1%} cho cả backlog lẫn đất cũ (quan sát 51,9%), HOẶC chỉ đất cũ g {implied['g_old_only_for_center_eq_px']:.1%} "
                   f"(s {implied['s_old_for_center_eq_px']:.1%}); P/B giá {implied['pb_at_price']:.2f}x.")
A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))['assumptions']
bridge = [dict(step='r2 công bố (giá 04/11 12.750, CK 5 tỷ ADV đến 04/11)', center_post=round(R2S['center_post_liq']), delta=0, reason='điểm xuất phát; control tái lập center_pre 13.857,2 trùng file')]
prev = bridge[0]['center_post']
c = round(O['bridge_pre'][0]['center_pre'] * f)
bridge.append(dict(step='đổi CK theo ADV đến 06/11 (giá 13.500)', center_post=c, delta=c - prev, reason=f"đính chính 4; CK 5 tỷ {R2S['liq_discount_ref']:.4%} → {d:.4%}")); prev = c
reasons = ['đính chính 1: CK holding [UL] → base 0% (song song); tái lập skeptic 14.931',
           'đính chính 2: thặng dư đất cũ s=s(g) cùng biên gộp quan sát 51,9% ±5pp (r2 s 40% ⇔ g 40% mâu thuẫn m 33,5% ⇔ g 51,9%)',
           'đính chính 2/3: backlog m=m(g) cùng trục g đối xứng ±5pp (≈ giá bán ±10%)']
for b, rsn in zip(O['bridge_pre'][1:], reasons):
    c = round(b['center_pre'] * f); bridge.append(dict(step=b['step'], center_post=c, delta=c - prev, reason=rsn)); prev = c
assert bridge[-1]['center_post'] == S0['center_post']
alts = [dict(name='HEADLINE r3 (holding 0, g 51,9% ±5pp nhất quán)', center_post=S0['center_post'], p10_out=S0['p10_out'], p90_out=S0['p90_out'], label=S0['label'], pct_below=S0['pct_weight_below_price'])]
for k in ('hold_0_10_20_30', 'hold_r1_10_20_30', 'hold_27', 'gov_5', 'gov_10', 'gov_15', 'both_g40', 'r2_s_40_keep', 'skeptic_s_40_55_70', 'skeptic_s_55_70_85', 'skeptic_bl_g40', 'sgtl_loss_100',
          'new_land_m10', 'new_land_p10', 'share_khac_050', 'share_khac_100'):
    v = par[k]; alts.append(dict(name=k, desc=v['desc'], center_post=v['center_post'], p10_out=v['p10_out'], p90_out=v['p90_out'], label=v['label'], pct_below=v['pct_weight_below_price']))
alts.append(dict(name='r ±100bp (tâm sau CK)', center_post={k: round(v * f) for k, v in O['r_sens_pre'].items()}))
S = dict(ticker='TCH', round=3, job='Taylor_20261108_180134', asof_price_date=L['pxd'], price=px, r=O['r'],
         r_anchor=dict(r=0.135, dep_asof_06_11=O['dep'], rule='r = 13,5% + 1,0 x (dep12T hieu dung - 7,40%)'))
S.update(S0)
S.update(center_pre_liq=S0['center_pre'], center_post_liq=S0['center_post'], p10_post=S0['p10_out'], p25_post=S0['p25_out'], p50_post=S0['p50_out'],
         p75_post=S0['p75_out'], p90_post=S0['p90_out'], liq_disc_5ty=d, liq_discount_ref=d, grid_n=S0['n_outcomes'], min_outcome=S0['min_out'],
         px_vs_center_post=px / S0['center_post'] - 1, px_vs_p10_post=px / S0['p10_out'] - 1, px_vs_p90_post=px / S0['p90_out'] - 1)
q = wpct(O['outcomes_vals'], O['outcomes_wts']); S.update(p10_pre=round(q[0.10]), p50_pre=round(q[0.50]), p90_pre=round(q[0.90]))
S['grid_desc'] = ('kết cục = biên gộp BĐS backlog g_bl × biên gộp đất cũ chưa bán g_old (mỗi trục 51,9% ±5pp, w 1/4-1/2-1/4, ĐỘC LẬP; m=0,8(g−0,1) trên DT trước VAT, s=0,8(g−0,1)/(1−g) trên giá vốn) '
                  '× r 13,5% ±100bp (1/4-1/2-1/4); n=27 tất định. Cố định: VCSH mẹ 12.159,1 (12.119 đ/cp = 74% tâm trước CK) — KHÔNG có trục chất lượng tài sản; CK holding 0; quỹ đất mới NPV0. '
                  'Tham số trung tâm = g 51,9% cả hai, r 13,5%.')
S['label_note'] = (f"Nhãn theo cỡ 5 tỷ/ADV250 (CK {d:.2%}, Q/ADV {L['w250']['sizes']['5000tr']['q_over_adv']:.1%}); sleeve 10–40 tr nhãn "
                   f"{', '.join(k + ' ' + v['label'] for k, v in sizes.items())}. Định nghĩa vùng P10–P90 không đổi. Vùng HẸP do cấu trúc (sổ sách hằng số) — KHÔNG phải thước đo bất định đầy đủ.")
S['ck_ref_size'] = dict(q_vnd=Q_REF, adv='250 phien', disc=d, in_calib=L['w250']['sizes']['5000tr']['in_calib'], disc_adv60=L['w60']['sizes']['5000tr']['disc'],
                        q_over_adv250=L['w250']['sizes']['5000tr']['q_over_adv'], q_over_adv60=L['w60']['sizes']['5000tr']['q_over_adv'])
S['ck_real_sleeve'] = {k: dict(disc_adv250=L['w250']['sizes'][k]['disc'], disc_adv60=L['w60']['sizes'][k]['disc'], q_over_adv250=L['w250']['sizes'][k]['q_over_adv'],
                               in_calib=L['w250']['sizes'][k]['in_calib'], **sizes[k]) for k in sizes}
S['ck_real_sleeve_note'] = 'cỡ sleeve 10–40 tr: Q/ADV <0,1% NGOÀI vùng hiệu chỉnh luật căn bậc hai ⇒ CK là cận trên, ≈0'
S['liquidity'] = L
S['parallel'] = par
S['headline_vs_alternatives'] = alts
S['bridge_r2_to_r3'] = bridge
S['implied_by_price'] = implied
S['assumptions'] = A
S['control_r2_reproduced'] = dict(center_pre=O['control_r2_center_pre'], file=O['r2_center_pre_file'], hold0=O['control_hold0_center_pre'], hold0_file=O['r2_hold0_center_pre_file'],
                                  ok=abs(O['control_r2_center_pre'] - O['r2_center_pre_file']) < 0.5)
S['r_sens_post'] = {k: round(v * f) for k, v in O['r_sens_pre'].items()}
S['gordon_roe_xcheck'] = O['gordon_roe_xcheck']
S['gordon_note'] = ('Kiểm chéo P/B–ROE (g 3%) cho 3.400–5.300 đ/cp — RẤT dưới NAV: ROE TTM 6,5% (LN mẹ TTM BQ 796) là giai đoạn TRƯỚC bàn giao chính NC-II, '
                    'không đại diện năng lực sinh lời; NAV hàng tồn kho là phương pháp chính. Lệch lớn này là cờ: nếu TCH tái đầu tư tiền bán hàng vào quỹ đất ROE thấp (<Ke), '
                    'giá trị cổ đông thấp hơn NAV — chính là cơ chế mà CK holding/quản trị song song đo; không đưa vào base (không có dữ liệu RONIC).')
S['axes_included'] = ['biên gộp backlog (2 chiều, ±5pp)', 'biên gộp đất cũ chưa bán (2 chiều, ±5pp ≈ giá bán ±10%)', 'r ±100bp']
S['axes_excluded'] = [
    dict(axis='CK holding {0;10;20;30}', reason='đính chính 1: độ lớn [UL], thực chất CK quản trị đổi tên (đếm đôi) ⇒ song song hold_0_10_20_30 / hold_r1_10_20_30 / hold_27'),
    dict(axis='CK quản trị 5/10/15%', reason='luật pháp lý/quản trị = WARNING; song song gov_*'),
    dict(axis='biên ngành 40% cho backlog/đất cũ', reason='không có dữ liệu (quan sát 51,0–51,9%); song song both_g40 / skeptic_bl_g40'),
    dict(axis='chất lượng tài sản sổ sách (tiền gửi SGTL 678,3; dự phòng)', reason='không có dữ liệu suy giảm; stress sgtl_loss_100 song song; WARNING'),
    dict(axis='quỹ đất mới 150 Tô Hiệu + I.14', reason='luật dự án mới NPV0; song song ±10%'),
    dict(axis='sở hữu H1+khác 0,80', reason='[UL], ảnh hưởng <80 đ/cp; song song 0,5/1,0')]
S['base_adjustments'] = [
    dict(item='CK holding: r2 kỳ vọng 15% → base 0%', effect_dong_per_share=round((O['bridge_pre'][1]['center_pre'] - O['bridge_pre'][0]['center_pre']) * f), basis='độ lớn [UL] ⇒ không đủ cơ sở trong base', source='TOP5D TCH#1'),
    dict(item='thặng dư đất cũ theo biên quan sát (s 69,7% ⇔ g 51,9%) thay s 40%', effect_dong_per_share=round((O['bridge_pre'][2]['center_pre'] - O['bridge_pre'][1]['center_pre']) * f),
         basis='TM25 6T FY26 biên bán BĐS 51,9% (6T FY25 51,0%); đệm chi phí hoàn thành chưa định lượng ⇒ không vào base; s áp trên chi phí ĐÃ phát sinh (thận trọng sẵn)', source='notes_read.md TM25; TOP5D TCH#2'),
    dict(item='backlog m theo cùng trục g đối xứng', effect_dong_per_share=round((O['bridge_pre'][3]['center_pre'] - O['bridge_pre'][2]['center_pre']) * f), basis='r2 {30;33,5;36} lệch xuống nhẹ', source='TOP5D TCH#2/3'),
    dict(item='quỹ đất mới 3.006,3 = giá sổ (NPV0)', effect_dong_per_share=0, basis='TM17', source='notes_read.md')]
S['center_vs_p50_note'] = (f"tâm (kỳ vọng lưới, sau CK 5 tỷ) {S0['center_post']} vs P50 kết cục {S0['p50_out']} vs giá trị tại tham số trung tâm {S0['center_param_post']}. "
                           "Lưới đối xứng ⇒ ba số sát nhau (s(g) lồi ⇒ tâm > giá trị tham số trung tâm một chút); P10/P90 do g thấp/cao cả hai trục, không nhánh trọng số nhỏ.")
S['center_change_vs_old'] = dict(vs_r2=S0['center_post'] - round(R2S['center_post_liq']), vs_r2_pct=S0['center_post'] / R2S['center_post_liq'] - 1,
                                 vs_zone_old=S0['center_post'] / R2S['zone_old']['center'] - 1)
S['change_reason'] = ('Vòng 3: CK holding [UL] ra khỏi base (song song); thặng dư đất cũ nhất quán với biên gộp BĐS quan sát 51,9% (r2 dùng 40% cho đất cũ nhưng 51,9% cho backlog); '
                      'trục g ±5pp hai chiều cho cả backlog/đất cũ; giá 06/11 13.500 (+5,9% từ 04/11); kiểm chéo ROE bằng LN mẹ TTM BQ 796.')
S['r2'] = dict(center_post=round(R2S['center_post_liq']), p10_out=round(R2S['p10_out']), p50_out=round(R2S['p50_out']), p90_out=round(R2S['p90_out']), label=R2S['label'], price=R2S['price'],
               pct_below_at_r2_price=R2S['pct_weight_below_price'], pct_below_at_13500=round(r2_below_new_px, 4), px_vs_center_at_13500=px / R2S['center_post_liq'] - 1)
S['zone_r2'] = dict(low=round(R2S['p10_out']), center=round(R2S['center_post_liq']), high=round(R2S['p90_out']))
S['zone_old'] = R2S.get('zone_old')
S['fear_buy_eligible_2_5'] = False
S['fear_buy_25'] = 'KHÔNG đủ điều kiện sleeve fear-buy §2.5: không có khủng hoảng/sự kiện sợ hãi; FLOOR_FAIL (CF_OA_3Y âm) — đây là lý do bỏ lệnh MUA TCH 03/11.'
S['warnings'] = R2S['warnings'] + [
    f"FLOOR_FAIL golden floor: BQ ticker_financial 2026Q3 CF_OA_3Y = −771,7 tỷ (fin_tch_r3.csv) do chi mua quỹ đất (150 Tô Hiệu 1.677,5 + I.14 1.328,8) — lý do bỏ lệnh MUA TCH 03/11; 8L rating gate LAG/production không áp cho sleeve DD nhưng là cờ đỏ dòng tiền.",
    "Danh tính 'NH TMCP Sài Gòn Tài Lộc' (tiền gửi 678,3 tỷ, 21% tiền+HTM) MÂU THUẪN giữa nguồn: notes_read.md:21 'đọc ảnh; có thể SCB/SGB' vs investor_report:131 'Sacombank đổi tên' (không nguồn) ⇒ CHƯA xác minh; stress mất 100% = sgtl_loss_100.",
    "Dự phòng 282,4 tỷ khoản đầu tư vào công ty con ở BCTC RIÊNG (theo skeptic 08/11; chưa tự đọc lại trong phiên này) — loại trừ ở hợp nhất, nhưng là tín hiệu kết quả công ty con dưới giá vốn đầu tư.",
    f"Giá tăng +{px / L['px_5d_ago'] - 1:.1%} trong 5 phiên ({L['px_5d_ago_date']} {L['px_5d_ago']:.0f} → {L['pxd']} {px:.0f}) — câu r2 'sát P10' lỗi thời."]
S['open_issues'] = [x for x in R2S['open_issues'] if 'OShares' not in x] + ['Biên gộp FY24/FY25 cả năm theo mảng BĐS (BCTC kiểm toán FY25 là PDF scan — chưa OCR trong phiên này)']
S['closed_issues'] = [f"OShares: BQ 2026Q3 = 1.003,31 tr cp (fin_tch_r3.csv) = SH model; 912,1 tr là quý trước cp thưởng 10% — ĐÓNG"]
S['corrections_check'] = [
    dict(item=1, verdict='ĐÚNG — áp', evidence=f"hold_0 tái lập {round(O['control_hold0_center_pre'] * (1 - R2S['liq_discount_ref']))} tại CK r2 (skeptic 14.931); song song hold_0_10_20_30 {par['hold_0_10_20_30']['center_post']}, r1 {par['hold_r1_10_20_30']['center_post']}"),
    dict(item=2, verdict='ĐÚNG — áp (dạng trục g thống nhất, không chép lưới s của skeptic)', evidence=f"quy đổi s(1−g)=0,8(g−0,1): g 51,9% ⇒ s 69,7%; skeptic s{{55;70;85}} {par['skeptic_s_55_70_85']['center_post']} (≈16.210), s{{40;55;70}} {par['skeptic_s_40_55_70']['center_post']} (≈15.571), backlog 40% {par['skeptic_bl_g40']['center_post']} (≈14.593) — tái lập; headline dùng g ±5pp hai trục ⇒ {S0['center_post']}. Biên FY24/FY25 cả năm theo mảng: CHƯA đọc được (PDF scan) — neo bằng 6T FY26 51,9% / 6T FY25 51,0%"),
    dict(item=3, verdict='ĐÚNG — áp một phần', evidence='thêm trục giá bán hai chiều dưới dạng g ±5pp ≈ giá ±10% (độ lớn [UL], không có dữ liệu giá bán); KHÔNG thêm trục chất lượng tài sản vì không có dữ liệu — ghi rõ vùng hẹp do cấu trúc'),
    dict(item=4, verdict='ĐÚNG — áp', evidence=f"giá 13.500 (BQ 06/11); giá/tâm r2 {px / R2S['center_post_liq'] - 1:+.1%}; % trọng số r2 dưới 13.500 = {r2_below_new_px:.1%}"),
    dict(item=5, verdict='ĐÚNG — áp', evidence=f"share_khac 0,5/1,0 ⇒ {par['share_khac_050']['center_post']}/{par['share_khac_100']['center_post']}; ROE TTM BQ 796 ⇒ {O['gordon_roe_xcheck']['TTM_BQ_796']['roe_co_lai']:.2%}"),
    dict(item=6, verdict='ĐÚNG — áp', evidence='WARNING FLOOR_FAIL (CF_OA_3Y −771,7 BQ), danh tính SGTL mâu thuẫn, dự phòng 282,4 riêng; OShares đóng')]
S['lock_md5'] = 'TCH/calc_r3/LOCK_md5.txt'
S['sources'] = dict(model='calc_r3/tch_r3.py -> tch_r3_out.json/txt, grid_tch_r3.csv', compare='calc_r3/tch_r3_compare.py -> compare_r3_out.txt', price='calc_r3/px_tch_r3_20261106.csv (BQ tav2_bq.ticker)',
                    fin='calc_r3/fin_tch_r3.csv (BQ tav2_bq.ticker_financial)', bctc='dd_TCH_20261031/calc/notes_read.md')
json.dump(S, open(os.path.join(BASE, 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'compare_r3_out.txt'), 'w') as fo:
    for k in ('price', 'asof_price_date', 'r', 'n_outcomes', 'center_pre', 'center_post', 'center_param_post', 'p10_out', 'p25_out', 'p50_out', 'p75_out', 'p90_out',
              'min_out', 'max_out', 'pct_weight_below_price', 'px_vs_center_post', 'label', 'liq_disc_5ty'):
        print(f'{k}: {S[k]}', file=fo)
    print('r2:', json.dumps(S['r2'], ensure_ascii=False), file=fo)
    for k, v in sizes.items():
        print(f"sleeve {k}: {json.dumps(v, ensure_ascii=False)}", file=fo)
    for b in bridge:
        print(f"bridge {b['step']}: {b['center_post']} ({b['delta']:+d})", file=fo)
    for a in alts:
        print('alt', json.dumps(a, ensure_ascii=False), file=fo)
    print('implied', json.dumps(implied, ensure_ascii=False), file=fo)
    for n in ('w250', 'w60'):
        w = L[n]
        print(f"{n} {w['window']} ADV {w['adv_med']/1e9:.2f} ty sigma {w['sigma_d']:.4f} zero_vol {w['n_zero_vol']} | " +
              ' | '.join(f"{k}: CK {v['disc']:.3%} Q/ADV {v['q_over_adv']:.4%} calib={v['in_calib']}" for k, v in w['sizes'].items()), file=fo)
print(open(os.path.join(HERE, 'compare_r3_out.txt')).read())
