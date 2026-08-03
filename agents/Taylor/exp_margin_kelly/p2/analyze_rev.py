"""VIEC 2 — co tin hieu "DAY DA HINH THANH VA DANG DI LEN" nao cai thien cong kich hoat khong?

Ba lop test (khai bao TRUOC khi chay, de dem N_trials trung thuc):
  A. Tin hieu dao chieu MUC RO tai ngay T lam GATE rieng (thay dd52)      — dose-response
  B. XAC NHAN bang cach DOI VAO LENH (delayed entry) — dung nghia "da tao day va di len"
  C. TO HOP dd52 (do sau) ∧ tin hieu dao chieu

x = (loi nhuan ro CAPIT sau 60 phien ke tu ngay VAO LENH) - lai vay 12,5%/nam - 2x0,075% phi
  = loi the RONG cua MOT DONG VON VAY (giong het dinh nghia bao cao p1, de so sanh truc tiep).

Su kien / ro: KHONG dinh nghia lai — dung compare_pit.csv (nm_pit, ro universe_pit).
Causal: moi gia tri gate lay tai ngay T (hoac ngay xac nhan, <= ngay vao lenh). Khong nhin truoc.
"""
import warnings; warnings.filterwarnings('ignore')
import os
import numpy as np
import pandas as pd
from google.cloud import bigquery

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/'
P2 = EXP + 'p2/'
HOLD, TC, BORROW = 60, 0.00075, 0.125
RNG = np.random.default_rng(20260803)
pd.set_option('display.width', 240)

C = pd.read_csv(EXP + 'compare_pit.csv', parse_dates=['event'])
R = pd.read_csv(P2 + 'rev_signals.csv', parse_dates=['event'])
D = C.merge(R.drop(columns=['n_pit']), on='event', how='left')
vni = pd.read_csv(EXP + 'vni.csv', parse_dates=['time']).sort_values('time')

# ---------------------------------------------------------------- gia (cache)
names = sorted({t for s in C.nm_pit.dropna() for t in str(s).split(',') if t})
PXP = P2 + 'px_pit.parquet'
if os.path.exists(PXP):
    px = pd.read_parquet(PXP)
else:
    c = bigquery.Client(project='lithe-record-440915-m9')
    inl = ','.join(f"'{t}'" for t in names)
    px = c.query(f"""SELECT t.time, t.ticker, t.Close FROM tav2_bq.ticker t
WHERE t.ticker IN ({inl}) AND t.time >= DATE '2008-01-01'""").to_dataframe()
    px['time'] = pd.to_datetime(px['time'])
    px.to_parquet(PXP, index=False)

cal = np.sort(vni.time.unique())
W = px.pivot_table(index='time', columns='ticker', values='Close').reindex(cal).ffill()
V = vni.set_index('time').reindex(cal)
V['lo21'] = V.Close.rolling(21, min_periods=10).min()
V['reb1m'] = 100 * (V.Close / V.lo21 - 1)
_m = V.Close.ewm(span=12, adjust=False).mean() - V.Close.ewm(span=26, adjust=False).mean()
V['macddiff'] = _m - _m.ewm(span=9, adjust=False).mean()
V['ma20'] = V.Close.rolling(20).mean()


def outcome(d, nms, entry_i=None):
    """x tai ngay vao lenh. entry_i = index lich vao lenh (None => T+1)."""
    i0 = int(np.searchsorted(cal, np.datetime64(d)))
    ie = (i0 + 1) if entry_i is None else int(entry_i)
    ix = ie + HOLD
    if len(nms) < 3 or ix >= len(cal):
        return np.nan
    sub = W.iloc[ie:ix + 1][nms]
    p0 = sub.iloc[0]; ok = p0.notna() & sub.iloc[-1].notna()
    if ok.sum() < 3:
        return np.nan
    nav = (sub.loc[:, ok] / p0[ok]).mean(axis=1)
    days = (cal[ix] - cal[ie]) / np.timedelta64(1, 'D')
    return float(nav.iloc[-1] - 1) - (BORROW * days / 365.0 + 2 * TC)


def blk(vv, lbl, ret=False):
    vv = np.asarray([x for x in vv if np.isfinite(x)], float)
    if len(vv) < 2:
        print(f'  {lbl:<44} N={len(vv):2d} ' + (f'x={100*vv[0]:+.1f}%' if len(vv) else '(rong)'))
        return (len(vv), np.nan, np.nan)
    b = np.array([RNG.choice(vv, len(vv), True).mean() for _ in range(20000)])
    p = 2 * min((b <= 0).mean(), (b >= 0).mean())
    print(f'  {lbl:<44} N={len(vv):2d} TB {100*vv.mean():+7.2f}% TV {100*np.median(vv):+7.2f}% '
          f'%duong {100*(vv>0).mean():5.1f} CI90 [{100*np.percentile(b,5):+6.2f};{100*np.percentile(b,95):+6.2f}] p={p:.3f}')
    return (len(vv), vv.mean(), p)


# tap chuan: 2014+, co ket cuc (x_pit khong NaN)
B = D[(D.event >= '2014-01-01') & D.x_pit.notna()].reset_index(drop=True)
ALL = D[D.event >= '2014-01-01'].reset_index(drop=True)   # ke ca 2026-07-20 (chua du 60 phien)
print('=' * 128)
print(f'TAP CHUAN: {len(B)} su kien 2014+ co ket cuc 60 phien (giong het bao cao p1). '
      f'TB nen (G0) = {100*B.x_pit.mean():+.2f}%')
print('=' * 128)

print('\n### QUAN SAT CO CAU (tra loi truc tiep cau hoi user) ###')
print('  "Da tao day va di len chua" tai NGAY FIRE — do o MUC THI TRUONG (VNINDEX):')
z = D[['event', 'm_dsince_lo21', 'm_reb1m', 'm_up3', 'm_up5', 'm_macddiff', 'dd52']].copy()
print(f'  So su kien co VNINDEX DUNG tai day 21 phien ngay hom fire (dsince_lo21=0): '
      f'{(D.m_dsince_lo21 == 0).sum()}/{len(D)}')
print(f'  So su kien co reb1m (da hoi tu day 1M) > 1%: {(D.m_reb1m > 1).sum()}/{len(D)}')
print(f'  So su kien co MACDdiff VNINDEX > 0: {(D.m_macddiff > 0).sum()}/{len(D)}')
print(f'  So su kien co momentum 3 phien duong: {(D.m_up3 > 0).sum()}/{len(D)}')
print('  => Cong washout theo THIET KE fire dung luc thi truong DANG tao day, KHONG phai sau do.')

# ---------------------------------------------------------------- A. gate muc RO tai T
print('\n' + '=' * 128)
print('A — TIN HIEU DAO CHIEU MUC RO TAI NGAY T, DUNG LAM GATE RIENG (dose-response)')
print('=' * 128)
A_SPECS = [
    ('b_reb1m', 'ro da hoi tu day 1M >= %', [0.5, 1.0, 2.0, 3.0]),
    ('b_reb1w', 'ro da hoi tu day 1W >= %', [0.5, 1.0, 2.0]),
    ('b_rsi_up1w', 'RSI ro da hoi tu day 1W >= (diem x100)', [2, 5, 10]),
    ('b_macd_pos', '% ten trong ro co MACDdiff > 0 >=', [20, 40, 60]),
    ('b_xfast', 'CMB_XFast TB <= (moi cat = moi dao chieu)', [3, 5, 8]),
]
ntrials_A = 0
for col, lbl, thrs in A_SPECS:
    print(f'\n  -- {lbl}  ({col})')
    for t in thrs:
        m = (B[col] >= t) if col != 'b_xfast' else (B[col] <= t)
        blk(B.x_pit[m], f'{col} {"<=" if col == "b_xfast" else ">="} {t}')
        ntrials_A += 1
    m = (B[col] < t) if col != 'b_xfast' else (B[col] > t)
    blk(B.x_pit[m], f'   (phan bu tai nguong cuoi)')

# ---------------------------------------------------------------- B. delayed entry (xac nhan)
print('\n' + '=' * 128)
print('B — XAC NHAN BANG CACH DOI: vao lenh o ngay DAU TIEN sau T thoa dieu kien dao chieu')
print('    (trong cua so toi da WMAX phien; khong thoa => BO su kien). Hold 60 phien tu ngay vao.')
print('=' * 128)


def confirm_idx(d, rule, thr, wmax):
    i0 = int(np.searchsorted(cal, np.datetime64(d)))
    for j in range(i0 + 1, min(i0 + 1 + wmax, len(cal))):
        if rule == 'reb1m' and V.reb1m.iloc[j] >= thr: return j + 1
        if rule == 'macd' and V.macddiff.iloc[j] > 0: return j + 1
        if rule == 'ma20' and V.Close.iloc[j] > V.ma20.iloc[j]: return j + 1
        if rule == 'up3' and (V.Close.iloc[j] / V.Close.iloc[j - 3] - 1) * 100 >= thr: return j + 1
    return None


B_SPECS = [('reb1m', 3.0), ('reb1m', 5.0), ('reb1m', 8.0), ('macd', 0), ('ma20', 0), ('up3', 3.0)]
WMAX = 30
ntrials_B = 0
base_n, base_m, _ = None, None, None
print('\n  Chan nen (vao T+1, khong doi):')
base = blk(B.x_pit, 'T+1 ngay lap tuc (nen)')
for rule, thr in B_SPECS:
    xs, lag = [], []
    for _, e in B.iterrows():
        j = confirm_idx(e.event, rule, thr, WMAX)
        if j is None:
            continue
        nms = [t for t in str(e.nm_pit).split(',') if t]
        x = outcome(e.event, nms, entry_i=j)
        if np.isfinite(x):
            xs.append(x)
            lag.append(j - int(np.searchsorted(cal, np.datetime64(e.event))) - 1)
    blk(xs, f'doi den khi {rule}>={thr} (tre TB {np.mean(lag) if lag else 0:.1f} phien)')
    ntrials_B += 1

# ---------------------------------------------------------------- C. to hop dd52 x dao chieu
print('\n' + '=' * 128)
print('C — TO HOP: do SAU (dd52<=-20%, truc S4) ∧ tin hieu dao chieu muc RO')
print('=' * 128)
deep = (B.dd52 <= -20)
blk(B.x_pit[deep], 'S4 goc: dd52 <= -20% (chan doi chieu)')
blk(B.x_pit[~deep], '   phan bu: dd52 > -20%')
ntrials_C = 0
for col, op, t in [('b_reb1m', '>=', 1.0), ('b_reb1m', '>=', 2.0), ('b_macd_pos', '>=', 40),
                   ('b_rsi_up1w', '>=', 5), ('b_xfast', '<=', 5)]:
    m = (B[col] >= t) if op == '>=' else (B[col] <= t)
    blk(B.x_pit[deep & m], f'dd52<=-20% ∧ {col} {op} {t}')
    ntrials_C += 1

# ---------------------------------------------------------------- LOO cho ung vien tot nhat
print('\n' + '=' * 128)
print('LOO (bo tung su kien) cho cac cell dang chu y')
print('=' * 128)


def loo(mask, lbl):
    vv = B.x_pit[mask].dropna().values
    if len(vv) < 3:
        print(f'  {lbl:<44} N={len(vv)} — qua mong de LOO'); return
    outs = [np.delete(vv, i).mean() for i in range(len(vv))]
    print(f'  {lbl:<44} N={len(vv):2d} TB {100*vv.mean():+6.2f}%  LOO min {100*min(outs):+6.2f}% '
          f'max {100*max(outs):+6.2f}%  {"TAT CA DUONG" if min(outs) > 0 else "CO CHAN AM"}')


loo(np.ones(len(B), bool), 'G0 moi washout')
loo(deep, 'dd52 <= -20%')
for col, op, t in [('b_reb1m', '>=', 1.0), ('b_reb1m', '>=', 2.0), ('b_macd_pos', '>=', 40)]:
    m = (B[col] >= t) if op == '>=' else (B[col] <= t)
    loo(m, f'{col} {op} {t}')
    loo(deep & m, f'dd52<=-20% ∧ {col} {op} {t}')

# ---------------------------------------------------------------- 2026-07-20 co qua cong khong
print('\n' + '=' * 128)
print('CONG CO MO CHO 2026-07-20 KHONG? (su kien LIVE user hoi)')
print('=' * 128)
lv = D[D.event == '2026-07-20'].iloc[0]
print(f'  dd52={lv.dd52:.1f}%  state={lv.state:.0f}  pe_pct={lv.pe_pct:.2f}')
print(f'  MUC RO: reb1m={lv.b_reb1m:.2f}% reb1w={lv.b_reb1w:.2f}% rsi_up1w={lv.b_rsi_up1w:.1f} '
      f'macd_pos={lv.b_macd_pos:.0f}% xfast={lv.b_xfast:.1f}')
print(f'  MUC VNI: dsince_lo21={lv.m_dsince_lo21:.0f} reb1m={lv.m_reb1m:.2f}% up3={lv.m_up3:+.2f}% '
      f'macddiff={lv.m_macddiff:+.2f}')
for col, op, t in [('dd52', '<=', -20), ('b_reb1m', '>=', 1.0), ('b_reb1m', '>=', 2.0),
                   ('b_macd_pos', '>=', 40), ('b_rsi_up1w', '>=', 5), ('b_xfast', '<=', 5)]:
    val = lv[col]
    ok = (val >= t) if op == '>=' else (val <= t)
    print(f'    {col} {op} {t}: {val:.2f} -> {"PASS" if ok else "CHAN"}')

print(f'\nN_TRIALS trong VIEC 2 = A:{ntrials_A} + B:{ntrials_B} + C:{ntrials_C} = '
      f'{ntrials_A + ntrials_B + ntrials_C} (chua ke 17 cua p1)')
print('DONE')
