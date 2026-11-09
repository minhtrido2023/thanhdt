"""summary_r3b_core.json + gia ngu y + metadata -> ../SUMMARY.json (backup ../SUMMARY_r3.json). Tat dinh. Chay sau compare_r3b.py."""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_shared')))
import model_r3b as B
from wpct import wpct
S = json.load(open(os.path.join(HERE, 'summary_r3b_core.json'))); M = json.load(open(os.path.join(HERE, 'model_r3b_out.json')))
R3 = json.load(open(os.path.join(BASE, 'SUMMARY_r3.json')))
f = 1 - S['liq_disc_5ty'] if 'liq_disc_5ty' in S else 1 - S['ck_ref_size']['disc_adv250']; px = S['price']; r0 = B.C.r_now(); cfg = B.CFG3B
ws = dict(zip(('xau', 'coso', 'tot'), cfg['w_scn'])); wo = {'dung': 1 - cfg['w_ore'], 'molai': cfg['w_ore']}
def ev(mult=1.0, prov=None, s_only=None, o_only=None):
    tot = 0
    for s, o, p, n in itertools.product(ws, wo, B.MR2.PROV, B.MR2.NS):
        a = (1.0 if p == prov else 0.0) if prov else B.MR2.PROV[p]['w']
        b = (1.0 if s == s_only else 0.0) if s_only else ws[s]
        c = (1.0 if o == o_only else 0.0) if o_only else wo[o]
        tot += a * b * c * B.MR2.NS[n]['w'] * B.value_ps(s, o, p, n, mult, r0, cfg)
    return tot * f
lo, hi = 0.0, 1.0
for _ in range(60):
    mid = (lo + hi) / 2; lo, hi = (mid, hi) if ev(mid) < px else (lo, mid)
I = dict(price=px, ebit_mult_for_center_eq_price=round(lo, 4), center_if_ore_closed_certain=round(ev(o_only='dung')), center_if_prov_permanent_certain=round(ev(prov='vinh_vien')),
         center_if_xau_certain=round(ev(s_only='xau')), center_if_xau_and_permanent=round(ev(prov='vinh_vien', s_only='xau')),
         center_if_xau_permanent_closed=round(ev(prov='vinh_vien', s_only='xau', o_only='dung')))
I['reading'] = ('Gia 33.000 thap hon P10 ket cuc 33.272 (-0,8%%). De TAM = gia can EBIT loi ~%.2fx co so mai mai, hoac xau chac chan + du phong vinh vien chac chan + khai truong dong chac chan (%d). '
                'Rieng khai truong dong chac chan: %d; rieng du phong vinh vien chac chan: %d; rieng xau chac chan: %d.') % (
    I['ebit_mult_for_center_eq_price'], I['center_if_xau_permanent_closed'], I['center_if_ore_closed_certain'], I['center_if_prov_permanent_certain'], I['center_if_xau_certain'])
S['implied_by_price'] = I
# nhan o co sleeve that (CK ADV250 va ADV60)
sl = {}
q = wpct(M['outcomes_vals'], M['outcomes_wts'], (0.10, 0.50, 0.90))
for k, v in S['ck_real_sleeve'].items():
    for a in ('adv250', 'adv60'):
        g = 1 - v[f'disc_{a}']; p10, p90 = q[0.10] * g, q[0.90] * g
        sl[f'{k}_{a}'] = dict(center=round(M['center_pre'] * g), p10=round(p10), p50=round(q[0.50] * g), p90=round(p90), label='DƯỚI vùng' if px < p10 else ('TRÊN vùng' if px > p90 else 'TRONG vùng'))
S['sleeve_size_labels'] = sl
S['assumptions'] = [x for x in R3['assumptions'] if not x['item'].startswith('Khai truong 25')] + [
 dict(item='Mo lai khai truong 25: w=0,5 (cach B, user duyet 08/11)', basis='giu xac suat cua r2/r3-goc (model.py:37); khong co van ban/tin mo lai (quet 08/11) nhung cung khong co quyet dinh dong vinh vien — xac suat 0,5 [UL] la ngoai sinh, user chot', source='dispatch Taylor_20261108_175121; TOP5C muc DGC #4'),
 dict(item='Nhanh mo lai: +500 ty lai gop 2028 GIU; bien tang VINH VIEN (terminal 1.000 ty/nam) = 0', basis='lai gop 2028 = loi ich co hoc cua quang tu khai (giam gia von quang mua ngoai) trong tam nhin du bao — khong phai thuong moat; bien vinh vien = hao chi phi ben, ma moat_durable=false => khong cong (quy uoc user 08/11: moat chi cong khi ben)', source='model.py:37 (up28=500, up=1000); ADDENDUM_5F_r2.md §2')]
S['headline_vs_alternatives_note'] = 'Dong *_term = cong bien vinh vien (thuong moat) — chi doi chieu voi r3, khong phai ung vien headline.'
S['bridge_r3_to_r3b'] = [dict(step=b['step'], center_pre=round(b['center_pre']), center_post=round(b['center_pre'] * f), delta_pre=None if b['delta'] is None else round(b['delta'])) for b in M['bridge_pre']]
S['r3_line_corrections'] = dict(ore_w0_10=dict(r3_report=42768, r3b=S['headline_vs_alternatives']['ore_w0.10']['center_post'], why='r3 dong w=0,10 gom bien vinh vien 1.000 ty; cach B bo => 41.587 (khop skeptic)'),
                               ore_w0_25=dict(r3_report=44637, r3b=S['headline_vs_alternatives']['ore_w0.25']['center_post']),
                               ore_w0_50=dict(r3_report=47753, r3b=S['center_post']))
S['skeptic_check_r3b'] = dict(skeptic_center=41849, skeptic_p10=33272, taylor_center=S['center_post'], taylor_p10=S['p10_out'], verdict='TRUNG SO (tai lap doc lap bang calc_r3b/model_r3b.py)')
S['skeptic_check_r3'] = R3['skeptic_check']
S['skeptic_check_r3']['c4_khai_truong'] = dict(verdict='THAY bang cach B (user duyet 08/11): w=0,5, bien vinh vien nhanh mo lai = 0', r3b_center_post=S['center_post'])
S['text_fixes_vs_r3'] = [
 'REPORT_r3.md:72 vi the: 10.000 x 33.000 = 330,0 tr = 35,3% NAV theo GIA THI TRUONG (NAV 934,55 tr ngay 06/11, nav_history_ZaloPay.csv); 42,6% neu tinh theo gia von 39.775 (397,75 tr). Doi soat broker dnse_raw_2026-11-08 (tradeQuantity 10000, costPrice 39775).',
 "REPORT_r3.md:72 'tru #2' la tieu chi §2 (khong phai §2.5).",
 "REPORT_r3.md:17 vien sai 'luat 3c' cho nen bien R2 — co so that la so BCTC Q3/26 (bien gop 20,5% gom du phong / 24,6% bo du phong), Q3 chay hoan toan quang mua ngoai, R2 19,5% ~ trung vi 4 peer 19,47%."]
S['axes_included'] = R3['axes_included'] + ['mo lai khai truong 25 (len, chi phan 2028; w 0,5)']
S['axes_excluded'] = [dict(axis='bien tang vinh vien cua nhanh mo lai', reason='moat khong ben (cach B); bao doi chieu ore_w*_term'), dict(axis='phap ly (haircut tien rong)', reason='luat user 02/11 WARNING; song song legal_axis')]
for k in ('base_adjustments', 'warnings', 'open_issues', 'fear_buy_25'):
    S[k] = R3[k]
S['warnings'] = [w for w in S['warnings'] if not w.startswith('Tap trung vi the ZaloPay')] + ['Tap trung vi the ZaloPay 10.000 cp = 35,3% NAV gia thi truong (42,6% gia von) >> tran sleeve 2-4% NAV — xem exit_discipline; KHONG du dieu kien §2.5 (NON)']
S['open_issues'] = [x for x in S['open_issues'] if not x.startswith('Vi the ZaloPay chua doi soat')]
S['fear_buy_25'] = 'NON: §2.5 — P/B me ~0,96 dat; tru #2 cua §2 (nha nuoc chi phoi) truot — DN tu nhan => NON dung'
S['label_fragility'] = ('Gia 33.000 duoi P10 33.272 chi 0,8%%: DUOI vung mong. Lat ve TRONG neu: w mo lai = 0 (r3), nen bien r4, trong so kich ban r2 0,3/0,5/0,2, hoac co truc phap ly. Giu DUOI o co sleeve that.')
S['center_vs_p50_note'] = f"tam {S['center_post']} vs P50 {S['p50_out']} vs tham so trung tam (khai truong dung) {S['center_param_post']}; nhanh mo lai chi them +659 d/cp truoc CK (lai gop 2028), bo 11.883 d/cp bien vinh vien."
S['lock'] = 'calc_r3b/LOCK_r3b_md5.txt (ghi 2026-11-09T00:54:10+0700 truoc compare)'
S['reproduce'] = '$DNA_PYEXE -I calc_r3b/model_r3b.py -> LOCK -> compare_r3b.py -> make_summary_r3b.py; control assert r3 41.825 truoc CK (model_r3_out.json) + 3 dong mo lai r3'
json.dump(S, open(os.path.join(BASE, 'SUMMARY.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(dict(I=I, sl=sl), ensure_ascii=False))
