"""Module chung VONG 2 (STANDARD_r2.md) — job Taylor_20261105_020016 (DGC DDV PVP PVT). Mo rong common.py vong 1, KHONG sua common.py.
- Phan vi o MUC KET CUC: moi mo hinh tra ve danh sach (gia tri, trong so) tung ket cuc; P10/P50/P90 = _shared/wpct.py (mid-block CDF).
- Truc lai huy dong (doi xung): Δ dep 12T {-50, 0, +50}bp, w 0,25/0,5/0,25 [UL], beta 1 -> r = 13,5% + Δ.
- Thanh khoan: CK = Y*sigma*sqrt(Q/ADV), Y=1; ADV = trung vi Price*Volume 250 VA 60 phien; co tham chieu 5 ty (nhan) + co sleeve that 10/20/40 trieu.
  Vung hieu chinh luat can bac hai (uoc luong, theo tai lieu thuc nghiem pho bien): Q/ADV ~ 0,1%..20%; ngoai vung -> ghi ro."""
import hashlib, math, os, sys, csv
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), '_shared'))
import common as C          # noqa: E402  (r neo, dep)
from wpct import wpct, weight_below   # noqa: E402

R_AXIS = ((-0.005, 0.25), (0.0, 0.50), (0.005, 0.25))   # [UL] trong so truc lai huy dong
Q_REF = 5e9
Q_SLEEVE = (10e6, 20e6, 40e6)
CALIB = (0.001, 0.20)


def r_points():
    return [(C.r_now(shift=s), w, s) for s, w in R_AXIS]


def liquidity_r2(tk):
    rows = sorted([r for r in csv.DictReader(open(os.path.join(HERE, 'bq_px_liq_20261104.csv'))) if r['ticker'] == tk], key=lambda r: r['time'])
    assert rows[-1]['time'] == C.ASOF, rows[-1]['time']
    out = dict(last_price=float(rows[-1]['Price']), last_date=rows[-1]['time'])
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        sz = {}
        for q in (Q_REF,) + Q_SLEEVE:
            part = q / adv
            sz[f'{q/1e6:.0f}tr'] = dict(q_over_adv=part, disc=sig * math.sqrt(part),
                                       in_calib=bool(CALIB[0] <= part <= CALIB[1]), days_at_15pct=q / (0.15 * adv))
        out[f'w{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', adv_med=adv, sigma_d=sig, sizes=sz)
    out['d_ref'] = out['w250']['sizes'][f'{Q_REF/1e6:.0f}tr']['disc']   # nhan theo ADV 250, co 5 ty
    return out


def summarize_r2(vals, wts, center_pre, center_param_pre, px, d_ref):
    """vals/wts = KET CUC (khong phai ky vong o). Tra phan vi truoc/sau CK, % trong so duoi gia (sau CK)."""
    f = 1 - d_ref
    q = wpct(vals, wts, (0.10, 0.25, 0.50, 0.75, 0.90))
    post = [v * f for v in vals]
    return dict(n_outcomes=len(vals), center_pre=round(center_pre), center_post=round(center_pre * f),
                center_param_pre=round(center_param_pre), center_param_post=round(center_param_pre * f),
                p10_pre=round(q[0.10]), p50_pre=round(q[0.50]), p90_pre=round(q[0.90]),
                p10_out=round(q[0.10] * f), p25_out=round(q[0.25] * f), p50_out=round(q[0.50] * f), p75_out=round(q[0.75] * f), p90_out=round(q[0.90] * f),
                min_out=round(min(post)), max_out=round(max(post)),
                pct_weight_below_price=weight_below(post, wts, px),
                label=('DƯỚI vùng' if px < q[0.10] * f else ('TRÊN vùng' if px > q[0.90] * f else 'TRONG vùng')))


def md5s(paths):
    return {os.path.relpath(p, '/home/trido/thanhdt/WorkingClaude'): hashlib.md5(open(p, 'rb').read()).hexdigest() for p in paths}


UPSTREAM_COMMON = [os.path.join(HERE, 'common.py'), os.path.join(HERE, 'common_r2.py'), os.path.join(HERE, 'bq_px_liq_20261104.csv'),
                   os.path.join(os.path.dirname(HERE), '_shared', 'wpct.py'),
                   os.path.join(C.WC, 'deposit_rate_vn.py'), os.path.join(C.WC, 'data', 'deposit_rate_vn_events.csv')]
