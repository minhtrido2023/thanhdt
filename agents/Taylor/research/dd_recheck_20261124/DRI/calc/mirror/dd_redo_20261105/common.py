"""Tien ich dung chung cho DD redo 05/11/2026 (NNC, DRI, MVC). Chay bang $DNA_PYEXE (/home/trido/thanhdt/wc_venv/bin/python).
- r(dep): luat 21 (user 03/11 22:27): r = 13,5% + beta x (dep_hieu_dung - 7,40%), beta = 1 (gia dinh), dep doc tu deposit_rate_vn.
- Chiet khau thanh khoan: phuong phap DANG KY TRUOC o nnc_model_r6.py / dri r5 (luat can bac hai): d(Q) = Y x sigma_ngay x sqrt(Q/ADV_trung_vi),
  Y = 1,0 (do nhay 0,5/1,5), Q tham chieu 5 ty d; ADV = trung vi Price x Volume 250 phien (tav2_bq.ticker), sigma tu log-return Close.
- Phan vi CO TRONG SO (weighted, noi suy tren CDF giua-khoi).
"""
import csv, math, sys
import numpy as np

WC = '/home/trido/thanhdt/WorkingClaude'
R_ANCHOR, DEP_ANCHOR = 0.135, 0.074          # diem neo luat 21: 13,5% @ 7,40% (cctg_12m 02/11/2026)
ASOF = '2026-11-04'
LIQ_CSV = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/dd_redo_20261105/bq_liq_nnc_mvc_dri_20261104.csv'


def dep_now(asof=ASOF):
    sys.path.insert(0, WC)
    import deposit_rate_vn as D
    s = D.macro_killswitch_a_status(asof=asof)
    return float(s['rate']), s['rate_source']


def r_of(dep, beta=1.0):
    return R_ANCHOR + beta * (dep - DEP_ANCHOR)


def wpct(vals, w, qs=(10, 25, 50, 75, 90)):
    v = np.asarray(vals, float); w = np.asarray(w, float); o = np.argsort(v); v, w = v[o], w[o]
    c = (np.cumsum(w) - 0.5 * w) / w.sum()
    return {q: float(np.interp(q / 100, c, v)) for q in qs}


def liquidity(tk, ff, asof=ASOF, n=250, qs=(1e9, 5e9, 10e9), ys=(0.5, 1.0, 1.5)):
    rows = [r for r in csv.DictReader(open(LIQ_CSV)) if r['ticker'] == tk and r['time'] <= asof][-n - 1:]
    c = np.array([float(r['Close']) for r in rows]); p = np.array([float(r['Price']) for r in rows]); v = np.array([float(r['Volume']) for r in rows])
    val = (p * v)[1:]; lr = np.diff(np.log(c)); sig = float(np.std(lr, ddof=1)); adv = float(np.median(val))
    m = val > 0; ami = float(np.median(np.abs(lr[m]) / (val[m] / 1e9)))
    o = dict(window=f'{rows[1]["time"]}..{rows[-1]["time"]}', n=len(val), adv_med=adv, adv_mean=float(val.mean()), sigma_d=sig,
             zero_vol_share=float(np.mean(v[1:] == 0)), amihud_med_per_bn=ami, free_float=ff, price=float(p[-1]), price_date=rows[-1]['time'],
             adv_60=float(np.median(val[-60:])), pos={})
    for q in qs:
        o['pos'][f'{q/1e9:.0f}'] = dict(disc={f'Y{y}': y * sig * math.sqrt(q / adv) for y in ys},
                                       days={f'p{int(pp*100)}': q / (pp * adv) for pp in (0.10, 0.15, 0.20)},
                                       amihud_day15=ami * 0.15 * adv / 1e9)
    o['d_ref'] = o['pos']['5']['disc']['Y1.0']
    o['d_ref_adv60'] = 1.0 * sig * math.sqrt(5e9 / o['adv_60'])
    return o


def label(px, p10, p90):
    return 'DƯỚI vùng (<P10)' if px < p10 else ('TRÊN vùng (>P90)' if px > p90 else 'TRONG vùng')


def zone_old(tk):
    """Ban ghi CUOI CUNG cua ma trong kb/dd_price_zones.json (chi DOC, khong sua)."""
    import json as _j
    es = [e for e in _j.load(open(WC + '/mike/kb/dd_price_zones.json'))['entries'] if e.get('ticker') == tk]
    e = es[-1]
    return dict(low=e['zone_low'], center=e['center'], high=e['zone_high'], dd_date=e['dd_date'], rev=e.get('rev'),
                zone_def='P25-P75 sau CK thanh khoan (ban cu)', source_file=e.get('source_file'))


def write_summary(out, path, grid_desc, change_reason, warnings, open_issues):
    import json as _j
    P, Q = out['grid_pct_post'], out['grid_pct_pre']
    zo = zone_old(out['ticker'])
    s = dict(ticker=out['ticker'], asof_price_date=out['price_date'], price=out['price'], r=out['r'],
             r_anchor=dict(rate=out['dep'], date=out['dep_src'], rule='r = 13,5% + 1,0 x (dep - 7,40%)'),
             center_pre_liq=round(out['center_pre']), center_post_liq=round(out['center_post']),
             p10_post=round(P[10]), p50_post=round(P[50]), p90_post=round(P[90]), p10_pre=round(Q[10]), p90_pre=round(Q[90]),
             liq_disc_5bn=out['liq']['d_ref'], px_vs_center_post=out['px_vs_center_post'], px_vs_p10_post=out['px_vs_p10_post'],
             px_vs_p90_post=out['px_vs_p90_post'], grid_desc=grid_desc, label=out['label'], zone_old=zo,
             center_change_pct=out['center_post'] / zo['center'] - 1, change_reason=change_reason, warnings=warnings, open_issues=open_issues)
    _j.dump(s, open(path, 'w'), ensure_ascii=False, indent=1, default=float)
    return s
