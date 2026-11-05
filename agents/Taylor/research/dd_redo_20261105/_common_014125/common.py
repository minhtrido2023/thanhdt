"""Module chung job Taylor_20261105_014125 (MBB FPT HPG HHS) — ban sao NGUYEN VAN phuong phap cua _common_014127 (cung dinh nghia lien ma). Chay: $DNA_PYEXE -I common.py
1) r (Ke noi dia) = 13,5% @ diem neo lai huy dong 12T hieu dung 03/11/2026, r_moi = 13,5% + beta*(dep_moi - dep_neo), beta=1 (gia dinh; do nhay 0,5).
   dep doc tu deposit_rate_vn.effective_deposit_rate (effective = max(Big-4 12M, CCTG 12M)), KHONG hardcode.
2) Chiet khau thanh khoan (CUNG phuong phap NNC r6 / MVC r9 / SCL r3, dang ky truoc): d(Q) = Y*sigma_ngay*sqrt(Q/ADV_trung_vi),
   Y=1,0 (0,5/1,5), sigma = do lech chuan log-return 250 phien (Close dieu chinh), ADV = trung vi Price*Volume 250 phien (tav2_bq.ticker, KHONG ticker_prune).
   Quy mo tham chieu NHAN = 5 ty d (1 va 10 ty la do nhay); so phien thoat o ty le tham gia 10/15/20% ADV; kiem cheo Amihud.
3) P10/P50/P90 = phan vi CO TRONG SO cua luoi (kich ban x bien trong yeu); trong so o = w_kich_ban x 1/n_diem_bien (deu)."""
import csv, json, math, os, sys
import numpy as np
WC = '/home/trido/thanhdt/WorkingClaude'
sys.path.insert(0, WC)
HERE = os.path.dirname(os.path.abspath(__file__))
R_ANCHOR = 0.135
ANCHOR_DATE = '2026-11-03'
ASOF = '2026-11-04'
QS = (1e9, 5e9, 10e9); YS = (0.5, 1.0, 1.5); N = 250; Q_LABEL = 5e9


def dep(asof):
    from deposit_rate_vn import effective_deposit_rate
    d = effective_deposit_rate(asof)
    return d['rate'], d['rate_source']


def r_now(beta=1.0, shift=0.0):
    d0, _ = dep(ANCHOR_DATE); d1, _ = dep(ASOF)
    return R_ANCHOR + beta * (d1 + shift - d0)


def anchor_info():
    d0, s0 = dep(ANCHOR_DATE); d1, s1 = dep(ASOF)
    return dict(r=r_now(), r_anchor=dict(r=R_ANCHOR, rate=d0, source=s0, date=ANCHOR_DATE), dep_asof=dict(rate=d1, source=s1, date=ASOF))


def liquidity(tk, free_float, ff_src):
    rows = [r for r in csv.DictReader(open(os.path.join(HERE, 'bq_px_liq_20261104.csv'))) if r['ticker'] == tk]
    rows.sort(key=lambda r: r['time']); d = rows[-N - 1:]
    c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
    val = (p * v)[1:]; lr = np.diff(np.log(c)); sig = float(np.std(lr, ddof=1)); adv = float(np.median(val))
    m = val > 0; ill = float(np.median(np.abs(lr[m]) / (val[m] / 1e9)))
    o = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), adv_med=adv, sigma_d=sig, amihud_med_per_bn=ill,
             zero_vol_share=float(np.mean(v[1:] == 0)), free_float=free_float, free_float_src=ff_src,
             last_price=float(p[-1]), last_date=d[-1]['time'], pos={})
    for q in QS:
        o['pos'][f'{q/1e9:.0f}'] = dict(disc={f'Y{y}': y * sig * math.sqrt(q / adv) for y in YS},
                                        days={f'p{int(pp*100)}': q / (pp * adv) for pp in (0.10, 0.15, 0.20)},
                                        amihud_day15=ill * 0.15 * adv / 1e9)
    o['d_label'] = o['pos'][f'{Q_LABEL/1e9:.0f}']['disc']['Y1.0']
    return o


def wq(vals, wts, qs=(10, 25, 50, 75, 90)):
    v = np.asarray(vals, float); w = np.asarray(wts, float); i = np.argsort(v); v, w = v[i], w[i]
    cw = (np.cumsum(w) - 0.5 * w) / w.sum()
    return {q: float(np.interp(q / 100, cw, v)) for q in qs}


def label(px, p10, p90):
    return 'DƯỚI vùng' if px < p10 else ('TRÊN vùng' if px > p90 else 'TRONG vùng')


def summarize(tk, px_date, px, center_pre, grid_vals, grid_wts, liq, grid_desc):
    f = 1 - liq['d_label']; qpre = wq(grid_vals, grid_wts)
    qpost = {k: v * f for k, v in qpre.items()}; cpost = center_pre * f
    return dict(ticker=tk, asof_price_date=px_date, price=px, center_pre_liq=round(center_pre), center_post_liq=round(cpost),
                p10_pre=round(qpre[10]), p50_pre=round(qpre[50]), p90_pre=round(qpre[90]),
                p10_post=round(qpost[10]), p25_post=round(qpost[25]), p50_post=round(qpost[50]), p75_post=round(qpost[75]), p90_post=round(qpost[90]),
                liq_disc_5ty=liq['d_label'], grid_desc=grid_desc, grid_n=len(grid_vals),
                px_vs_center_post=px / cpost - 1, px_vs_p10_post=px / qpost[10] - 1, px_vs_p90_post=px / qpost[90] - 1,
                label=label(px, qpost[10], qpost[90]))


if __name__ == '__main__':
    print(json.dumps(anchor_info(), ensure_ascii=False, indent=1))
