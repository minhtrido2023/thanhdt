"""TCH VONG 3b — SAU KHOA: kiem md5 moi dong LOCK_md5.txt roi moi doc gia 06/11 (calc_r3/px_tch_r3_20261106.csv, BQ tav2_bq.ticker).
-> ../SUMMARY.json (r3 backup ../SUMMARY_r3.json, ghi 1 lan) + compare_r3b_out.txt. Chay: /home/trido/thanhdt/wc_venv/bin/python -I tch_r3b_compare.py"""
import csv, hashlib, json, math, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); ROOT = os.path.dirname(BASE)
sys.path.insert(0, os.path.join(ROOT, '_shared'))
import numpy as np                     # noqa: E402
from wpct import wpct, weight_below    # noqa: E402
S3_PATH = os.path.join(BASE, 'SUMMARY_r3.json')
for line in open(os.path.join(HERE, 'LOCK_md5.txt')):
    p = line.split()
    if not p or p[0] in ('#', '##', 'POST'):
        continue
    h, f = (p[1], os.path.join(ROOT, p[2])) if p[0] == 'LOCK' else (p[0], os.path.join(HERE, p[1]))
    if p[0] == 'LOCK' and p[2] == 'TCH/SUMMARY.json' and os.path.exists(S3_PATH):
        f = S3_PATH                    # lan chay thu 2: SUMMARY.json da la r3b, ban r3 nam o SUMMARY_r3.json
    assert hashlib.md5(open(f, 'rb').read()).hexdigest() == h, f'doi sau khoa: {f}'
if not os.path.exists(S3_PATH):
    shutil.copy2(os.path.join(BASE, 'SUMMARY.json'), S3_PATH)
S3 = json.load(open(S3_PATH))
O = json.load(open(os.path.join(HERE, 'tch_r3b_out.json')))
ASOF = '2026-11-06'; Q_REF = 5e9; SLEEVE = (10e6, 20e6, 40e6); CALIB = (0.001, 0.10)


def liq():   # chep nguyen tch_r3_compare.py:liq()
    rows = sorted((r for r in csv.DictReader(open(os.path.join(BASE, 'calc_r3', 'px_tch_r3_20261106.csv'))) if r['ticker'] == 'TCH'), key=lambda r: r['time'])
    assert rows[-1]['time'] == ASOF
    out = dict(px=float(rows[-1]['Price']), pxd=rows[-1]['time'])
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        out[f'w{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', adv_med=adv, sigma_d=sig,
                            sizes={f'{q/1e6:.0f}tr': dict(q_over_adv=q / adv, disc=sig * math.sqrt(q / adv), in_calib=bool(CALIB[0] <= q / adv <= CALIB[1])) for q in (Q_REF,) + SLEEVE})
    out['d_ref'] = out['w250']['sizes']['5000tr']['disc']
    return out


def summ(vals, wts, px, d):
    f = 1 - d; q = wpct(vals, wts, (0.10, 0.25, 0.50, 0.75, 0.90)); post = [v * f for v in vals]; c = sum(a * b for a, b in zip(vals, wts)) / sum(wts)
    return dict(n_outcomes=len(vals), center_pre=round(c), center_post=round(c * f), p10_out=round(q[0.10] * f), p25_out=round(q[0.25] * f), p50_out=round(q[0.50] * f),
                p75_out=round(q[0.75] * f), p90_out=round(q[0.90] * f), min_out=round(min(post)), max_out=round(max(post)),
                pct_weight_below_price=round(weight_below(post, wts, px), 4),
                label=('DƯỚI vùng' if px < q[0.10] * f else ('TRÊN vùng' if px > q[0.90] * f else 'TRONG vùng')))


L = liq(); px = L['px']; d = L['d_ref']; f = 1 - d
assert abs(d - S3['liq_disc_5ty']) < 1e-12
S0 = summ(O['outcomes_vals'], O['outcomes_wts'], px, d)
sizes = {k: summ(O['outcomes_vals'], O['outcomes_wts'], px, L['w250']['sizes'][k]['disc']) for k in ('10tr', '20tr', '40tr')}
par = {k: dict(desc=v['desc'], **summ(v['vals'], v['wts'], px, d)) for k, v in O['parallel'].items()}
par_40 = {k: summ(v['vals'], v['wts'], px, L['w250']['sizes']['40tr']['disc']) for k, v in O['parallel'].items()}
assert par['r3_old']['center_post'] == S3['center_post'] and par['r3_old']['p10_out'] == S3['p10_out'] and par['r3_old']['p90_out'] == S3['p90_out']
bridge, prev = [], None
for b in O['bridge_pre']:
    c = round(b['center_pre'] * f); bridge.append(dict(step=b['step'], center_post=c, delta=0 if prev is None else c - prev)); prev = c
assert bridge[0]['center_post'] == S3['center_post'] and bridge[-1]['center_post'] == S0['center_post']
S = dict(ticker='TCH', round='3b', job='Taylor_20261109_003030', final_round=True, asof_price_date=L['pxd'], price=px, r=O['r'])
S.update(S0)
S.update(center_post_liq=S0['center_post'], center_pre_liq=S0['center_pre'], p10_post=S0['p10_out'], p50_post=S0['p50_out'], p90_post=S0['p90_out'],
         liq_disc_5ty=d, liq_discount_ref=d, grid_n=S0['n_outcomes'], px_vs_center_post=px / S0['center_post'] - 1,
         px_vs_p10_post=px / S0['p10_out'] - 1, px_vs_p90_post=px / S0['p90_out'] - 1)
S['label_5ty'] = S0['label']; S['label_sleeve'] = {k: v['label'] for k, v in sizes.items()}
S['ck_real_sleeve'] = {k: dict(disc_adv250=L['w250']['sizes'][k]['disc'], **sizes[k]) for k in sizes}
S['grid_desc'] = ('kết cục = g backlog × g đất cũ (mỗi trục 51,9% ±5pp, 1/4-1/2-1/4, ĐỘC LẬP) × r 13,5% ±100bp × chi phí hoàn thành còn lại F ±25% (k×0,75/1/1,25); n=81. '
                  'Đất cũ chưa bán: giá vốn + thặng dư CÙNG pv(y), y = mốc hoàn thành dự án BCTN25 (GR 2,15; H2 1,15; NC-II 4,07; SP đã xong 1,0 năm), '
                  'chi phí tương lai k·C chi tại y/2 và sinh biên s như chi phí đã phát sinh; k đo = (TMĐT − HTK − GV đã kết chuyển)/(HTK + GV đã kết chuyển). CK holding 0; quỹ đất mới NPV0.')
S['k_measured'] = dict(by_project=O['k_center'], range_by_project=O['k_range'], weighted_me_share=O['k_weighted_me_share'], C_unsold_me_share=O['C_unsold_me_share'],
                       source='TMĐT BCTN25 tr.30-33 (bctn25.txt:1372,1393,1419) − HTK 30/09/26 (notes_read TM9) − GV BĐS đã kết chuyển (cận 0..FY25 275,27 / 6T FY26 940,37)',
                       caveat='TMĐT là dự toán pháp lý (có thể gồm dự phòng), không phải số kiểm toán; GV kết chuyển lũy kế theo dự án không công bố ⇒ dùng cận; H2 k 2,96 bất thường (xong thô nhưng HTK 25% TMĐT) ⇒ song song k_H2_cap1')
S['y_by_project'] = O['y_by_project']
S['skeptic_check'] = dict(consistent_y4_k0_post=par['cons_y4_k0']['center_post'], skeptic_claim=13435,
                          slope_per_k_post=round(O['skeptic_slope_per_k_pre'] * f), skeptic_slope_claim=1742,
                          note='tâm nhất quán y=4,k=0 tái lập skeptic; độ dốc theo k (y=4, chi phí y=2) lệch skeptic ~+2% — cách gán k cho nhóm SP đã hoàn thành chưa đối chiếu chi tiết')
S['bridge_r3_to_r3b'] = bridge
S['parallel'] = par
S['parallel_40tr'] = {k: dict(center_post=v['center_post'], p10_out=v['p10_out'], p90_out=v['p90_out'], label=v['label']) for k, v in par_40.items()}
S['r3_old_parallel'] = dict(center_post=par['r3_old']['center_post'], p10_out=par['r3_old']['p10_out'], p90_out=par['r3_old']['p90_out'], label=par['r3_old']['label'],
                            corr_g=dict(p10_out=par['r3_old_corr_g']['p10_out'], p90_out=par['r3_old_corr_g']['p90_out'], label=par['r3_old_corr_g']['label']),
                            note='r3 (chỉ thặng dư đất cũ chiết khấu pv(4), giá vốn giữ giá sổ) — làm song song theo yêu cầu, KHÔNG còn là headline')
S['g_audit'] = dict(FY25=dict(rev=480.49, cogs=275.27, gpm=1 - 275.27 / 480.49, gpm_incl_impairment_19_11=1 - (275.27 + 19.11) / 480.49),
                    FY24=dict(rev=3899.17, cogs=2235.88, gpm=1 - 2235.88 / 3899.17),
                    src='BCTC HN FY25 kiểm toán AASC, TM24/TM25 (pdf tr.42, đọc ảnh: calc_r3b/evidence_FY25_audited_pdfp42_TM24_TM25.png)',
                    note='base giữ g 51,9% (6T FY26 CHƯA soát xét; 6T FY25 51,0% có soát xét) vì quỹ đất còn lại chủ yếu NC-II (bắt đầu bàn giao Q2 FY26); FY24/FY25 chủ yếu H1/GR — song song g_audit_427')
S['assumptions_r3b'] = json.load(open(os.path.join(HERE, 'assumptions_r3b.json')))['assumptions']
S['warnings'] = S3['warnings']
S['open_issues'] = [x for x in S3['open_issues'] if 'Biên gộp FY24/FY25' not in x] + [
    'GV BĐS đã kết chuyển lũy kế theo dự án (để chốt k) — không công bố; k dùng cận', 'TMĐT vs dự toán nội bộ dùng trích trước giá vốn (TM 2.25) — chưa đối chiếu',
    'biên gộp theo dự án (GR vs NC-II) — không công bố; FY24/FY25 kiểm toán 42,7% vs 6T FY26 51,9%']
S['closed_issues'] = S3.get('closed_issues', []) + ['Biên gộp mảng BĐS FY24/FY25 kiểm toán: 42,7% / 42,7% (OCR/đọc ảnh pdf tr.42) — ĐÓNG']
S['floor_fail'] = 'FLOOR_FAIL golden floor: CF_OA_3Y = −771,7 tỷ (BQ ticker_financial 2026Q3, calc_r3/fin_tch_r3.csv) — không đủ điều kiện sleeve fear-buy; giữ nguyên'
S['text_sync_note'] = ('SUMMARY_5F.json:45,49,181 (centre 13768/TRONG) và ADDENDUM_5F.md:76 ("r2 giữ nguyên… TRONG") là số r2, đã LẠC HẬU qua r3 (16.244 DƯỚI) và r3b (file này). '
                       'Không sửa (2 file có hash trong calc_r3/LOCK_md5.txt POST) — nguồn hiện hành là SUMMARY.json r3b + REPORT_r3b.md; ghi chú đồng bộ ở SYNC_NOTE_r3b.md.')
S['r3'] = dict(center_post=S3['center_post'], p10_out=S3['p10_out'], p90_out=S3['p90_out'], label=S3['label'], pct_below=S3['pct_weight_below_price'])
S['center_change_vs_r3'] = dict(delta=S0['center_post'] - S3['center_post'], pct=S0['center_post'] / S3['center_post'] - 1)
S['lock_md5'] = 'TCH/calc_r3b/LOCK_md5.txt'
S['sources'] = dict(model='calc_r3b/tch_r3b.py -> tch_r3b_out.json/txt, grid_tch_r3b.csv', compare='calc_r3b/tch_r3b_compare.py -> compare_r3b_out.txt',
                    price='calc_r3/px_tch_r3_20261106.csv (BQ tav2_bq.ticker)', bctc='dd_TCH_20261031/calc/notes_read.md; src/gaps/bctn25.txt; src/FY25_audited_hopnhat.pdf tr.42')
json.dump(S, open(os.path.join(BASE, 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'compare_r3b_out.txt'), 'w') as fo:
    for k in ('price', 'asof_price_date', 'n_outcomes', 'center_pre', 'center_post', 'p10_out', 'p50_out', 'p90_out', 'min_out', 'max_out', 'pct_weight_below_price', 'px_vs_center_post', 'label', 'liq_disc_5ty'):
        print(f'{k}: {S[k]}', file=fo)
    for k, v in sizes.items():
        print(f"sleeve {k}: center {v['center_post']} P10 {v['p10_out']} P90 {v['p90_out']} below {v['pct_weight_below_price']} {v['label']}", file=fo)
    for b in bridge:
        print(f"bridge {b['step']}: {b['center_post']} ({b['delta']:+d})", file=fo)
    print('skeptic_check', json.dumps(S['skeptic_check'], ensure_ascii=False), file=fo)
    for k, v in par.items():
        v4 = par_40[k]
        print(f"par {k}: 5ty center {v['center_post']} P10 {v['p10_out']} P90 {v['p90_out']} below {v['pct_weight_below_price']} {v['label']} | 40tr {v4['center_post']} P10 {v4['p10_out']} P90 {v4['p90_out']} {v4['label']} — {v['desc']}", file=fo)
print(open(os.path.join(HERE, 'compare_r3b_out.txt')).read())
