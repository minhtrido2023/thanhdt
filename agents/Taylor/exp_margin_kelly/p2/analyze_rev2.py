"""VIEC 2 (phan 2) — hai cau hoi con thieu sau analyze_rev.py:

  D. Tuong quan HANG (Spearman) giua muc do "da hoi" tai T va ket cuc — 1 phep thu duy nhat,
     khong cat nguong (tranh dò nguong). Kem permutation test.
  E. DELAYED-ENTRY co lam GIAM MAE (drawdown trong ky giu) khong? — day moi la cau hoi dung
     cho bai toan DON BAY, vi rang buoc troi la RUIN (margin call), khong phai ky vong.
     Neu doi xac nhan cat duoc MAE xau nhat thi TRAN GROSS an toan tang len.
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from scipy import stats

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/'
P2 = EXP + 'p2/'
HOLD, TC, BORROW = 60, 0.00075, 0.125
RNG = np.random.default_rng(20260803)
pd.set_option('display.width', 240)

C = pd.read_csv(EXP + 'compare_pit.csv', parse_dates=['event'])
R = pd.read_csv(P2 + 'rev_signals.csv', parse_dates=['event'])
D = C.merge(R.drop(columns=['n_pit']), on='event', how='left')
vni = pd.read_csv(EXP + 'vni.csv', parse_dates=['time']).sort_values('time')
px = pd.read_parquet(P2 + 'px_pit.parquet')

cal = np.sort(vni.time.unique())
W = px.pivot_table(index='time', columns='ticker', values='Close').reindex(cal).ffill()
V = vni.set_index('time').reindex(cal)
V['lo21'] = V.Close.rolling(21, min_periods=10).min()
V['reb1m'] = 100 * (V.Close / V.lo21 - 1)
_m = V.Close.ewm(span=12, adjust=False).mean() - V.Close.ewm(span=26, adjust=False).mean()
V['macddiff'] = _m - _m.ewm(span=9, adjust=False).mean()
V['ma20'] = V.Close.rolling(20).mean()

B = D[(D.event >= '2014-01-01') & D.x_pit.notna()].reset_index(drop=True)


def path(d, nms, entry_i=None):
    i0 = int(np.searchsorted(cal, np.datetime64(d)))
    ie = (i0 + 1) if entry_i is None else int(entry_i)
    ix = ie + HOLD
    if len(nms) < 3 or ix >= len(cal):
        return None
    sub = W.iloc[ie:ix + 1][nms]
    p0 = sub.iloc[0]; ok = p0.notna() & sub.iloc[-1].notna()
    if ok.sum() < 3:
        return None
    nav = (sub.loc[:, ok] / p0[ok]).mean(axis=1)
    days = (cal[ix] - cal[ie]) / np.timedelta64(1, 'D')
    return dict(x=float(nav.iloc[-1] - 1) - (BORROW * days / 365.0 + 2 * TC),
                mae=float(nav.min() - 1))


print('=' * 120)
print('D — TUONG QUAN HANG: "da hoi bao nhieu tai ngay T" vs KET CUC (1 phep thu, khong cat nguong)')
print('=' * 120)
for col, lbl in [('b_reb1m', 'ro: % da hoi tu day 1M tai T'),
                 ('b_reb1w', 'ro: % da hoi tu day 1W tai T'),
                 ('b_macd_pos', 'ro: % ten MACDdiff>0 tai T'),
                 ('b_rsi_up1w', 'ro: RSI da hoi tu day 1W tai T'),
                 ('b_xfast', 'ro: CMB_XFast TB tai T (thap=moi dao chieu)'),
                 ('dd52', 'thi truong: dd52 tai T (do SAU, doi chieu)')]:
    m = B[col].notna()
    rho, p = stats.spearmanr(B[col][m], B.x_pit[m])
    # permutation (N nho -> khong tin p tiem can)
    obs = rho
    perm = np.array([stats.spearmanr(B[col][m], RNG.permutation(B.x_pit[m].values))[0] for _ in range(20000)])
    pp = (np.abs(perm) >= abs(obs)).mean()
    print(f'  {lbl:<48} N={m.sum():2d} rho={rho:+.3f}  p_asym={p:.3f}  p_perm={pp:.3f}'
          f'   {"<-- da hoi CANG NHIEU thi ket cuc CANG KEM" if rho < -0.3 else ""}')

print('\n' + '=' * 120)
print('E — DOI XAC NHAN CO CAT DUOC MAE (rang buoc RUIN) KHONG?')
print('=' * 120)


def confirm_idx(d, rule, thr, wmax=30):
    i0 = int(np.searchsorted(cal, np.datetime64(d)))
    for j in range(i0 + 1, min(i0 + 1 + wmax, len(cal))):
        if rule == 'reb1m' and V.reb1m.iloc[j] >= thr: return j + 1
        if rule == 'macd' and V.macddiff.iloc[j] > 0: return j + 1
        if rule == 'ma20' and V.Close.iloc[j] > V.ma20.iloc[j]: return j + 1
    return None


def maint_ok(mae, gross, maint):
    a = gross * (1 + mae); e = a - (gross - 1)
    return e / a >= maint if a > 0 else False


rows = []
for lbl, rule, thr in [('T+1 ngay lap tuc (nen)', None, None),
                       ('doi reb1m>=3%', 'reb1m', 3.0),
                       ('doi reb1m>=5%', 'reb1m', 5.0),
                       ('doi reb1m>=8%', 'reb1m', 8.0),
                       ('doi MACDdiff>0', 'macd', 0),
                       ('doi Close>MA20', 'ma20', 0)]:
    xs, ms = [], []
    for _, e in B.iterrows():
        nms = [t for t in str(e.nm_pit).split(',') if t]
        j = None if rule is None else confirm_idx(e.event, rule, thr)
        if rule is not None and j is None:
            continue
        r = path(e.event, nms, entry_i=j)
        if r:
            xs.append(r['x']); ms.append(r['mae'])
    xs, ms = np.array(xs), np.array(ms)
    b = np.array([RNG.choice(xs, len(xs), True).mean() for _ in range(20000)])
    # tran gross an toan: gross lon nhat con song sot MAE xau nhat o maintenance 35%
    gmax = max([g for g in np.arange(1.0, 3.01, 0.05) if maint_ok(ms.min(), g, 0.35)] or [1.0])
    rows.append(dict(leg=lbl, N=len(xs), TB=100 * xs.mean(), p=2 * min((b <= 0).mean(), (b >= 0).mean()),
                     duong=100 * (xs > 0).mean(), MAE_xau=100 * ms.min(), MAE_TB=100 * ms.mean(),
                     MAE_p10=100 * np.percentile(ms, 10), gross_max_m35=gmax))
E = pd.DataFrame(rows)
print(E.round(2).to_string(index=False))
print('\n  gross_max_m35 = don bay gop LON NHAT con song sot cu MAE XAU NHAT cua chinh chan do,')
print('  o maintenance margin 35% (cong thuc y het bao cao p1 §4.2).')
print('DONE')
