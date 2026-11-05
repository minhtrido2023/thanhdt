"""Chung cho DD redo VONG 2 (job Taylor_20261105_020021: NT2 SAS SZL TCH). Ap STANDARD_r2.md.
- Phan vi o MUC KET CUC: moi o luoi = 1 ket cuc tat dinh (khong co kich ban con ben trong o) => phan vi tren chinh cac o,
  trong so = tich trong so cac truc; dung _shared/wpct.py (mid-block CDF). Tam = ky vong co trong so CUA LUOI (khong phai 3 kich ban rieng).
- Thanh khoan: _common/liq.py (luat can bac hai Y*sigma*sqrt(Q/ADV), Y=1), ADV trung vi Price*Volume 250 VA 60 phien;
  co tham chieu 5 ty (quy uoc fleet) + co sleeve that 10/20/40 trieu. Vung hieu chinh quy uoc Q/ADV <= 10% [UL — quy uoc job nay].
- LOCK: md5 moi file upstream script thuc thi/doc."""
import os, sys, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, '_shared')); sys.path.insert(0, os.path.join(ROOT, '_common'))
from wpct import wpct, weight_below  # noqa: E402
import liq as L  # noqa: E402

REF_BN = 5
SLEEVE_BN = (0.01, 0.02, 0.04)
CALIB_MAX = 0.10
UPSTREAM_COMMON = [os.path.join(HERE, 'r2lib.py'), os.path.join(ROOT, '_shared', 'wpct.py'), os.path.join(ROOT, '_common', 'liq.py'),
                   os.path.join(ROOT, '_common', 'bq_px_4ma_20261104.csv'), '/home/trido/thanhdt/WorkingClaude/deposit_rate_vn.py',
                   '/home/trido/thanhdt/WorkingClaude/data/deposit_rate_vn_events.csv']


def liq2(tk):
    out = {}
    for n in (250, 60):
        q = L.liq(tk, Q_bn=SLEEVE_BN + (1, REF_BN, 10), n=n)
        sizes = {}
        for k, v in q['pos'].items():
            qbn = float(k); ratio = qbn * 1e9 / q['adv_med_vnd']
            sizes[k] = dict(q_bn=qbn, disc=v['disc_Y1'], disc_Y05=v['disc_Y05'], disc_Y15=v['disc_Y15'], q_over_adv=ratio,
                            in_calib=bool(ratio <= CALIB_MAX), days_at10=v['days_at10'], days_at20=v['days_at20'])
        out[f'adv{n}'] = dict(window=q['window'], n=q['n'], adv_bn=q['adv_med_vnd'] / 1e9, adv_shares=q['adv_med_shares'], sigma_d=q['sigma_d'],
                              zero_vol_days=q['zero_vol_days'], sizes=sizes)
        out.setdefault('price', q['price']); out.setdefault('price_date', q['price_date'])
    out['ref_key'] = str(REF_BN)
    out['disc_ref'] = out['adv250']['sizes'][str(REF_BN)]['disc']
    out['disc_sleeve_max'] = out['adv250']['sizes'][str(SLEEVE_BN[-1])]['disc']
    return out


def stats(vals, ws, px, disc):
    """vals = gia tri truoc CK (1 ket cuc/o); tra ve muc ket cuc truoc + sau CK."""
    tot = float(sum(ws)); post = [v * (1 - disc) for v in vals]
    c_pre = sum(v * w for v, w in zip(vals, ws)) / tot
    q_pre = wpct(vals, ws); q_post = wpct(post, ws)
    return dict(n=len(vals), center_pre=c_pre, center_post=c_pre * (1 - disc),
                p10_pre=q_pre[0.10], p50_pre=q_pre[0.50], p90_pre=q_pre[0.90],
                p10_post=q_post[0.10], p50_post=q_post[0.50], p90_post=q_post[0.90],
                pct_w_below_px=weight_below(post, ws, px), min_post=min(post), max_post=max(post), disc=disc)


def label(px, s):
    return 'DUOI vung (<P10)' if px < s['p10_post'] else ('TREN vung (>P90)' if px > s['p90_post'] else 'TRONG vung')


def fmt(s, px):
    return (f"n={s['n']} | tam truoc {s['center_pre']:,.0f} sau {s['center_post']:,.0f} | P10/P50/P90 sau {s['p10_post']:,.0f}/{s['p50_post']:,.0f}/{s['p90_post']:,.0f}"
            f" | min sau {s['min_post']:,.0f} | % trong so duoi gia {s['pct_w_below_px']:.1%} | gia/tam {px/s['center_post']-1:+.1%} => {label(px, s)}")


def lock(here, files):
    rows = []
    for f in sorted(set(UPSTREAM_COMMON + files)):
        rows.append(f"{hashlib.md5(open(f, 'rb').read()).hexdigest()}  {os.path.relpath(f, ROOT) if f.startswith(ROOT) else f}")
    open(os.path.join(here, 'LOCK_r2_md5.txt'), 'w').write('\n'.join(rows) + '\n')
    return rows


def dump(here, obj):
    json.dump(obj, open(os.path.join(here, 'model_r2_out.json'), 'w'), indent=1, default=float, ensure_ascii=False, sort_keys=True)


def liq_lines(Q):
    out = []
    for w in ('adv250', 'adv60'):
        a = Q[w]
        out.append(f"{w}: ADV trung vi {a['adv_bn']:.2f} ty/phien ({a['window']}, {a['zero_vol_days']} phien KL=0), sigma {a['sigma_d']:.2%}")
        for k, v in a['sizes'].items():
            out.append(f"   Q={v['q_bn']*1000:>7,.0f} tr: CK Y0,5/1/1,5 = {v['disc_Y05']:.2%}/{v['disc']:.2%}/{v['disc_Y15']:.2%}; Q/ADV {v['q_over_adv']:.1%}"
                       f" {'trong' if v['in_calib'] else 'NGOAI'} vung hieu chinh (<=10%); {v['days_at20']:.1f}-{v['days_at10']:.1f} phien @20-10%")
    return out


def summary(here, tk, M, meta, old_summary_path):
    """SUMMARY.json vong 2: giu truong cu (p10_post... = ban muc ket cuc moi) + truong moi diem 11."""
    old = json.load(open(old_summary_path))
    s = M['grid']; Q = M['liq']
    S = dict(old)
    S.update(dict(round='r2', job='Taylor_20261105_020021', asof_price_date=M['price_date'], price=M['price'], r=M['r'],
                  center_pre_liq=s['center_pre'], center_post_liq=s['center_post'],
                  p10_post=s['p10_post'], p50_post=s['p50_post'], p90_post=s['p90_post'],
                  p10_pre=s['p10_pre'], p50_pre=s['p50_pre'], p90_pre=s['p90_pre'],
                  p10_out=s['p10_post'], p50_out=s['p50_post'], p90_out=s['p90_post'],
                  pct_weight_below_price=s['pct_w_below_px'], n_outcomes=s['n'], min_outcome_post=s['min_post'],
                  liq_discount_ref=Q['disc_ref'], liq_ref_position_bn_vnd=REF_BN, adv_med_bn_vnd=Q['adv250']['adv_bn'], adv60_med_bn_vnd=Q['adv60']['adv_bn'],
                  ck_ref_size=dict(q_bn=REF_BN, adv250=Q['adv250']['sizes'][str(REF_BN)], adv60=Q['adv60']['sizes'][str(REF_BN)]),
                  ck_real_sleeve={k: dict(adv250=Q['adv250']['sizes'][k], adv60=Q['adv60']['sizes'][k]) for k in map(str, SLEEVE_BN)},
                  grid_n=s['n'], grid_desc=meta['grid_desc'], label=M['label'], label_note=meta.get('label_note', ''),
                  px_vs_center=M['price'] / s['center_post'] - 1, px_vs_p10=M['price'] / s['p10_post'] - 1, px_vs_p90=M['price'] / s['p90_post'] - 1,
                  center_change_vs_r1=s['center_post'] / old['center_post_liq'] - 1,
                  center_change_vs_old=(s['center_post'] / old['zone_old']['center'] - 1) if old.get('zone_old', {}).get('center') else None,
                  axes_included=meta['axes_included'], axes_excluded=meta['axes_excluded'], base_adjustments=meta['base_adjustments'],
                  center_vs_p50_note=meta['center_vs_p50_note'], change_reason=meta['change_reason'], change_vs_r1=meta['change_vs_r1'],
                  warnings=meta['warnings'], open_issues=meta['open_issues'], parallel=M.get('parallel', {}), crosscheck=M.get('crosscheck', {}),
                  sources=dict(model='calc/model_r2.py -> calc/model_r2_out.json/txt', lock='calc/LOCK_r2_md5.txt',
                               liq='_common/liq.py + _common/bq_px_4ma_20261104.csv (via _common_020021/r2lib.py)', pct='_shared/wpct.py')))
    json.dump(S, open(os.path.join(here, '..', 'SUMMARY.json'), 'w'), indent=1, ensure_ascii=False, default=float)
    return S
