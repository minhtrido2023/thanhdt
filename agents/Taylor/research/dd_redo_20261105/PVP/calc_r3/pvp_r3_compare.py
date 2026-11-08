"""PVP VONG 3 — SAU KHOA: kiem md5 moi dong LOCK cua LOCK_md5.txt (outputs + upstream) roi moi doc gia 06/11 (px_pvp_r3_20261106.csv, BQ tav2_bq.ticker).
-> ../SUMMARY.json (backup ../SUMMARY_r2.json da tao truoc khoa) + compare_r3_out.txt. Chay: $DNA_PYEXE -I pvp_r3_compare.py"""
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
import pvp_r3 as M                     # noqa: E402
O = json.load(open(os.path.join(HERE, 'pvp_r3_out.json')))
ASOF = '2026-11-06'; Q_REF = 5e9; SLEEVE = (10e6, 20e6, 40e6); CALIB = (0.001, 0.20)


def liq():
    rows = sorted((r for r in csv.DictReader(open(os.path.join(HERE, 'px_pvp_r3_20261106.csv'))) if r['ticker'] == 'PVP'), key=lambda r: r['time'])
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
par = {}
for k, P in O['parallel'].items():
    s = summ(P['vals'], P['wts'], P['center_pre'], P['center_pre'], px, d); s.pop('center_param_post'); s.pop('center_pre'); par[k] = dict(desc=P['desc'], **s)
R2S = json.load(open(os.path.join(BASE, 'SUMMARY_r2.json')))
r2o = json.load(open(os.path.join(BASE, 'calc', 'model_r2_out.json')))
r2_newpx = summ(r2o['outcomes_vals'], r2o['outcomes_wts'], r2o['center_pre'], r2o['center_param_pre'], px, R2S['liq_disc_5ty'])
# cau noi r2 -> r3 (sau CK)
bridge = [dict(step='r2_SUMMARY (CK ADV den 04/11)', center_post=R2S['center_post'], delta=None, why='ban r2 da cong bo')]
prev = R2S['center_post']
why = {'r2_control': 'cau hinh r2 tai lap center_pre trung (22.822,73) — chi doi CK sang ADV 250 phien den 06/11',
       'd1_trong_so_doi_xung': 'dinh chinh 1: trong so cuoc 0,40/0,45/0,15 -> 0,275/0,45/0,275 (muc 400 da duoi 561 nam hoa; lech xuong la nhan dinh)',
       'd2_cat_npv_+30_nhanh_tot': 'dinh chinh 2: cat +30% NPV tau moi o nhanh tot (khong IRR kiem duoc); giu -30% o xau (IRR 7,67% < 11%)',
       'd3_fso_chiet_khau_Ke': 'dinh chinh 3: FSO chiet khau 10% -> r=13,5% (spread khong nguon; phu luc gia han chua ky)',
       'd4_vld_khac_+37': 'dinh chinh 4: + VLD khac 37,0 ty (CDKT Q3 tr.1-2, da kiem)',
       'r_06_11': 'r 06/11 = 13,5% (dep 12T hieu dung 06/11 = 03/11 = 7,40%) — khong doi'}
for b in O['bridge_pre']:
    c = round(b['center_pre'] * f); bridge.append(dict(step=b['step'], center_post=c, delta=c - prev, why=why[b['step']])); prev = c
assert prev == S0['center_post']
# gia ngu y
k_eb = bisect(lambda k: M.center(dict(M.R3, ebitda_k=k)) * f, 0.0, 2.0, px)
x_npv = bisect(lambda x: M.center(dict(M.R3, npv={s: x for s in M.SCNS})) * f, -1.5, 0.5, px)
flat_e = bisect(lambda e: M.center(dict(M.R3, ebitda={s: e for s in M.SCNS})) * f, 0.0, 800.0, px)
implied = dict(ebitda_scale_k=round(k_eb, 4), ebitda_levels_at_k={s: round(M.A['ebitda'][s] * k_eb, 1) for s in M.SCNS},
               ebitda_flat_all_scn=round(flat_e, 1), ebitda_flat_vs_561_run_rate=round(flat_e / (M1VT := 421.084 * 4 / 3), 3),
               ship_npv_uncond=round(x_npv, 4),
               note=f'Gia {px:.0f} = tam r3 khi: (a) EBITDA doi tau phang moi kich ban ~{flat_e:.0f} ty/nam (= {flat_e / M1VT:.0%} muc 561 nam hoa 9T/26), hoac (b) muc 300/400/550 x {k_eb:.3f}, hoac (c) NPV tau moi vo dieu kien {x_npv:+.0%} (giu con lai r3)')
# do nhay don vi phe lieu/len da
unit_scrap = round(par['scrap_plus_1musd']['center_post'] - S0['center_post'])
headline_alt = [dict(variant='HEADLINE r3', center_post=S0['center_post'], p10_out=S0['p10_out'], p90_out=S0['p90_out'], label=S0['label'], pct_below=S0['pct_weight_below_price'])]
headline_alt += [dict(variant=k, desc=v['desc'], center_post=v['center_post'], p10_out=v['p10_out'], p50_out=v['p50_out'], p90_out=v['p90_out'], label=v['label'], pct_below=v['pct_weight_below_price']) for k, v in par.items()]
liqd = dict(ck_ref_size=dict(q_vnd=Q_REF, adv='250 phien', disc=d, in_calib=L['w250']['sizes']['5000tr']['in_calib'], disc_adv60=L['w60']['sizes']['5000tr']['disc']),
            ck_real_sleeve={k: dict(disc_adv250=L['w250']['sizes'][k]['disc'], disc_adv60=L['w60']['sizes'][k]['disc'], q_over_adv250=L['w250']['sizes'][k]['q_over_adv'],
                                    in_calib=L['w250']['sizes'][k]['in_calib']) for k in ('10tr', '20tr', '40tr')})
sleeve40 = summ(O['outcomes_vals'], O['outcomes_wts'], O['center_pre'], O['center_param_pre'], px, liqd['ck_real_sleeve']['40tr']['disc_adv250'])
ASM = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))['assumptions']
S = dict(R2S)
for k in [k for k in S if k.startswith('r1') or k in ('delta_center_vs_r1_pct', 'p10_pre', 'p50_pre', 'p90_pre', 'center_pre_liq', 'center_post_liq', 'scenarios_pre', 'r_sens_pre', 'r_sens_post')]:
    S.pop(k)
S.update(dict(round=3, job='Taylor_20261108_164335', asof_price_date=L['pxd'], price=px, **S0,
              p10_post=S0['p10_out'], p25_post=S0['p25_out'], p50_post=S0['p50_out'], p75_post=S0['p75_out'], p90_post=S0['p90_out'],
              px_vs_center_post=px / S0['center_post'] - 1, liq_disc_5ty=d, grid_n=S0['n_outcomes'], **liqd, liquidity=L,
              sleeve_40tr_view=dict(p10_out=sleeve40['p10_out'], p90_out=sleeve40['p90_out'], center_post=sleeve40['center_post'], label=sleeve40['label']),
              r=O['r'], center_param_pre=round(O['center_param_pre']),
              grid_desc=('ket cuc = kich ban cuoc (xau/co so/tot 0,275/0,45/0,275 [UL doi xung]; EBITDA doi tau 300/400/550; NPV tau moi -30%/0/0 [dau: du lieu IRR; do lon UL]) '
                         'x tuoi doi con lai 4..8 nam (deu) x lai huy dong -50/0/+50bp (0,25/0,5/0,25; FSO chiet khau = r) '
                         'x mua tau ca hai 116 / chi #2 56,5 / khong 0 trUSD (0,50/0,35/0,15 [UL]) x 177 ty FSO nam 1 thanh tien/khong (0,5/0,5 [UL]); n=270; '
                         'tham so trung tam = co so, 6 nam, dr=0, mua ca hai, FSO thanh tien'),
              assumptions=ASM, headline_vs_alternatives=headline_alt, implied_by_price=implied, bridge_r2_to_r3=bridge,
              r2_at_new_price=dict(center_post=r2_newpx['center_post'], p10_out=r2_newpx['p10_out'], p90_out=r2_newpx['p90_out'], label=r2_newpx['label'], pct_below=r2_newpx['pct_weight_below_price']),
              parallel=par, branch_center_pre=O['branch_center_pre'], parts_center_param=O['parts_center_param'],
              axes_included=['chu ky cuoc (hai chieu, trong so doi xung)', 'tuoi doi doi tau (hai chieu)', 'lai huy dong (hai chieu; FSO cung truc)', 'ket cuc mua tau (tach ky vong)',
                             'NPV tau moi -30% nhanh xau (chieu xuong co du lieu)', '177 ty FSO nam 1 (0,5/0,5)'],
              axes_excluded=[dict(axis='NPV tau moi +30% nhanh tot', reason='khong IRR/du lieu kiem duoc (dinh chinh 2) — bao song song ship_pm30_sym'),
                             dict(axis='phat hanh co phieu tai tro tau (pha loang)', reason='van kien DHDCD bat thuong chua cong bo; khong co gia/so luong — WARNING + moc'),
                             dict(axis='phu luc gia han FSO 2036 chua ky', reason='hai ben da thong nhat (BB 03/06/2025), cong ty da ghi cam ket theo gia/thoi han moi; rui ro khong ky -> do nhay fso_no_gt5y + WARNING'),
                             dict(axis='phe lieu doi tau cu vs chi phi len da sau TT99', reason=f'khong co du lieu LDT/chi phi; do nhay don vi {unit_scrap:+d} d/cp moi 1 trUSD (hai chieu)')],
              base_adjustments=R2S['base_adjustments'] + [dict(item='VLD khac (TS NH ngoai tien/HTM 583,9 - no NH ngoai vay/co tuc/du phong 546,9)', effect_dong_per_share=round(37.007e9 / M.M1.SH),
                                                                basis='so du CDKT 30/09/2026', source='BCTC Q3/2026 tr.1-2 (ma 100-160, 310-323)'),
                                                           dict(item='NPV tau moi ky vong (-30% x w_xau 0,275)', effect_dong_per_share=round(-0.3 * 0.275 * 77.8 * 26.04e9 / M.M1.SH),
                                                                basis='IRR Aframax #2 7,67% < IRRmin 11%; do lon 30% [UL]', source='[AGM p44]')],
              center_vs_p50_note=(f"tam (ky vong luoi, sau CK) {S0['center_post']} vs P50 ket cuc {S0['p50_out']} vs gia tri tai tham so trung tam {S0['center_param_post']}. "
                                  f"Tam nhanh truoc CK: xau {O['branch_center_pre']['scn_xau']} / co so {O['branch_center_pre']['scn_coso']} / tot {O['branch_center_pre']['scn_tot']}; "
                                  'P10 do nhanh xau (w 0,275) + mua ca hai (NPV -30%) quyet dinh — mot nhanh UL.'),
              change_reason='Vong 3: ap dinh chinh skeptic 1-4 (trong so doi xung, cat +30% NPV tau, FSO chiet khau Ke, + VLD 37 ty); 5-7 = do nhay/WARNING; CK theo ADV 06/11',
              warnings=R2S['warnings'] + ['Phu luc gia han hop dong FSO Dai Hung Queen den 31/12/2036 CHUA KY (hop dong cu het 17/05/2026; BB 03/06/2025 da thong nhat gia+thoi han moi); doi tac la cong ty me PVTrans, tung dieu chinh gia cuoc [H1 tr.31]'],
              open_issues=R2S['open_issues'] + ['Phe lieu doi tau cu (hien 0) vs chi phi len da sau TT99 chua trong EBITDA'],
              fear_buy_25=R2S['fear_buy_25']))
json.dump(S, open(os.path.join(BASE, 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False)
with open(os.path.join(HERE, 'compare_r3_out.txt'), 'w') as fo:
    print(f"px {px:.0f} ({L['pxd']}) d_ref5ty={d:.4f} adv250={L['w250']['adv_med']/1e9:.3f} ty adv60={L['w60']['adv_med']/1e9:.3f} ty", file=fo)
    print('HEADLINE', json.dumps(S0, ensure_ascii=False), file=fo)
    print('sleeve40', json.dumps(S['sleeve_40tr_view'], ensure_ascii=False), file=fo)
    print('r2@newpx', json.dumps(S['r2_at_new_price'], ensure_ascii=False), file=fo)
    for b in bridge:
        print('bridge', json.dumps(b, ensure_ascii=False), file=fo)
    for k, v in par.items():
        print(f"par {k}: c={v['center_post']} p10={v['p10_out']} p50={v['p50_out']} p90={v['p90_out']} below={v['pct_weight_below_price']} {v['label']}", file=fo)
    print('implied', json.dumps(implied, ensure_ascii=False), file=fo)
    print('unit_scrap_per_1musd', unit_scrap, file=fo)
print(open(os.path.join(HERE, 'compare_r3_out.txt')).read())
