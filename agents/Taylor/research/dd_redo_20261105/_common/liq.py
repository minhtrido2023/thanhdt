"""Chung cho job Taylor_20261105_014133: thanh khoan + r + luoi.
Nguon: bq_px_4ma_20261104.csv (tav2_bq.ticker, Close/Price/Volume, keo 05/11/2026 08:4x ICT).
Chiet khau thanh khoan = Y * sigma_ngay * sqrt(Q/ADV) (luat can bac hai, cung cong thuc DRI r4/r5), Y=1 tam (0,5/1,5 do nhay),
Q tham chieu = 5 ty (quy uoc fleet); ADV = trung vi Price*Volume 250 phien toi asof.
r = 13,5% + beta*(dep - 7,40%); neo dep 7,40% = effective_deposit_rate('2026-11-03') = CCTG 12M (02/11/2026), Big-4 6,8%."""
import os, csv, math, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R_ANCHOR, DEP_ANCHOR, DEP_ANCHOR_DATE = 0.135, 0.0740, '2026-11-03 (CCTG 12M 02/11/2026; Big-4 12M 6,8%)'
ASOF = '2026-11-04'

def r_of(dep, beta=1.0):
    return R_ANCHOR + beta * (dep - DEP_ANCHOR)

def current_dep(asof=ASOF):
    import sys
    sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
    import deposit_rate_vn as d
    x = d.effective_deposit_rate(asof)
    return x['rate'], x['rate_source']

def px_series(tk, asof=ASOF):
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, 'bq_px_4ma_20261104.csv'))) if r['ticker'] == tk and r['time'] <= asof]
    return rows

def liq(tk, Q_bn=(1, 5, 10), asof=ASOF, n=250, free_float_shares=None):
    rows = px_series(tk, asof)[-(n + 1):]
    c = np.array([float(r['Close']) for r in rows]); p = np.array([float(r['Price']) for r in rows]); v = np.array([float(r['Volume']) for r in rows])
    val = (p * v)[1:]
    sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val)); advv = float(np.median(v[1:]))
    zero = int((v[1:] == 0).sum())
    out = dict(ticker=tk, window=f"{rows[1]['time']}..{rows[-1]['time']}", n=len(val), adv_med_vnd=adv, adv_med_shares=advv,
               sigma_d=sig, zero_vol_days=zero, price=float(p[-1]), price_date=rows[-1]['time'], pos={})
    for q in Q_bn:
        Q = q * 1e9
        out['pos'][str(q)] = dict(disc_Y05=0.5 * sig * math.sqrt(Q / adv), disc_Y1=sig * math.sqrt(Q / adv), disc_Y15=1.5 * sig * math.sqrt(Q / adv),
                                  days_at10=Q / (0.10 * adv), days_at15=Q / (0.15 * adv), days_at20=Q / (0.20 * adv))
    if free_float_shares:
        out['ff_turnover_days'] = free_float_shares / advv  # so phien de khop het free float o ADV
    out['disc_ref'] = out['pos']['5']['disc_Y1']
    return out

def wq(vals, w, qs=(0.1, 0.5, 0.9)):
    """phan vi co trong so (CDF buoc, ban trung diem)"""
    vals = np.asarray(vals, float); w = np.asarray(w, float)
    o = np.argsort(vals); vals, w = vals[o], w[o] / w.sum()
    cw = np.cumsum(w) - 0.5 * w
    return {f'P{int(q*100)}': float(np.interp(q, cw, vals)) for q in qs}

def label(px, p10, p90):
    return 'DUOI vung (<P10)' if px < p10 else ('TREN vung (>P90)' if px > p90 else 'TRONG vung')
