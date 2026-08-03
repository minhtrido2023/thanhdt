"""VIEC 2 (phan 3) — kiem tra ky phat hien "doi xac nhan cat duoc MAE":
la do TIMING (vao sau nen tranh duoc phan roi con lai) hay do BO BOT SU KIEN (selection)?

Cach kiem: so sanh TREN CUNG TAP su kien (chi nhung su kien co xac nhan trong 30 phien) —
neu MAE van cai thien manh thi la TIMING that; neu bien mat thi la selection.
Kem bang chi tiet tung su kien.
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/'
P2 = EXP + 'p2/'
HOLD, TC, BORROW = 60, 0.00075, 0.125
RNG = np.random.default_rng(20260803)
pd.set_option('display.width', 250)

C = pd.read_csv(EXP + 'compare_pit.csv', parse_dates=['event'])
vni = pd.read_csv(EXP + 'vni.csv', parse_dates=['time']).sort_values('time')
px = pd.read_parquet(P2 + 'px_pit.parquet')
cal = np.sort(vni.time.unique())
W = px.pivot_table(index='time', columns='ticker', values='Close').reindex(cal).ffill()
V = vni.set_index('time').reindex(cal)
V['lo21'] = V.Close.rolling(21, min_periods=10).min()
V['reb1m'] = 100 * (V.Close / V.lo21 - 1)
V['ma20'] = V.Close.rolling(20).mean()
B = C[(C.event >= '2014-01-01') & C.x_pit.notna()].reset_index(drop=True)


def path(d, nms, entry_i=None):
    i0 = int(np.searchsorted(cal, np.datetime64(d)))
    ie = (i0 + 1) if entry_i is None else int(entry_i)
    ix = ie + HOLD
    if len(nms) < 3 or ix >= len(cal): return None
    sub = W.iloc[ie:ix + 1][nms]
    p0 = sub.iloc[0]; ok = p0.notna() & sub.iloc[-1].notna()
    if ok.sum() < 3: return None
    nav = (sub.loc[:, ok] / p0[ok]).mean(axis=1)
    days = (cal[ix] - cal[ie]) / np.timedelta64(1, 'D')
    return (float(nav.iloc[-1] - 1) - (BORROW * days / 365.0 + 2 * TC), float(nav.min() - 1), ie - i0 - 1)


def confirm_idx(d, rule, thr, wmax=30):
    i0 = int(np.searchsorted(cal, np.datetime64(d)))
    for j in range(i0 + 1, min(i0 + 1 + wmax, len(cal))):
        if rule == 'reb1m' and V.reb1m.iloc[j] >= thr: return j + 1
        if rule == 'ma20' and V.Close.iloc[j] > V.ma20.iloc[j]: return j + 1
    return None


for rule, thr, lbl in [('reb1m', 8.0, 'VNINDEX hoi >=8% tu day 1M'), ('ma20', 0, 'VNINDEX > MA20')]:
    rows = []
    for _, e in B.iterrows():
        nms = [t for t in str(e.nm_pit).split(',') if t]
        a = path(e.event, nms)
        j = confirm_idx(e.event, rule, thr)
        b = path(e.event, nms, entry_i=j) if j is not None else None
        rows.append(dict(event=e.event.date(), dd52=round(e.dd52, 1),
                         x_T1=100 * a[0], mae_T1=100 * a[1],
                         tre=(b[2] if b else np.nan),
                         x_wait=(100 * b[0] if b else np.nan), mae_wait=(100 * b[1] if b else np.nan)))
    T = pd.DataFrame(rows)
    both = T[T.x_wait.notna()]
    print('=' * 128)
    print(f'XAC NHAN = {lbl}   (cua so 30 phien)')
    print('=' * 128)
    print(T.round(2).to_string(index=False))
    print(f'\n  TREN CUNG TAP {len(both)} su kien co xac nhan (loai bo hieu ung selection):')
    print(f'    T+1 ngay      : TB x {both.x_T1.mean():+6.2f}%  MAE xau nhat {both.mae_T1.min():+6.2f}%  '
          f'MAE TB {both.mae_T1.mean():+6.2f}%  MAE p10 {np.percentile(both.mae_T1,10):+6.2f}%')
    print(f'    doi xac nhan  : TB x {both.x_wait.mean():+6.2f}%  MAE xau nhat {both.mae_wait.min():+6.2f}%  '
          f'MAE TB {both.mae_wait.mean():+6.2f}%  MAE p10 {np.percentile(both.mae_wait,10):+6.2f}%')
    d = (both.x_wait - both.x_T1).values
    bb = np.array([RNG.choice(d, len(d), True).mean() for _ in range(20000)])
    print(f'    HIEU (doi - T+1) tren cung su kien: TB {d.mean():+6.2f}pp  '
          f'CI90 [{np.percentile(bb,5):+.2f};{np.percentile(bb,95):+.2f}]  '
          f'p={2*min((bb<=0).mean(),(bb>=0).mean()):.3f}  ({(d>0).sum()}/{len(d)} su kien tot len)')
    dm = (both.mae_wait - both.mae_T1).values
    bm = np.array([RNG.choice(dm, len(dm), True).mean() for _ in range(20000)])
    print(f'    HIEU MAE (doi - T+1): TB {dm.mean():+6.2f}pp (duong = MAE nong hon = TOT)  '
          f'CI90 [{np.percentile(bm,5):+.2f};{np.percentile(bm,95):+.2f}]  '
          f'p={2*min((bm<=0).mean(),(bm>=0).mean()):.3f}  ({(dm>0).sum()}/{len(dm)} nong hon)')
    print()
print('DONE')
