"""VIEC 2 — FETCH tin hieu DAO CHIEU ("day da hinh thanh, dang di len") tai NGAY TIN HIEU T.

Cau hoi user (John): gate `dd52<=-20%` chi do DO SAU (da sut bao nhieu tu dinh), KHONG do
XAC NHAN DAO CHIEU (da tao day va bat dau di len chua). Kiem tra xem co tin hieu dao chieu
nao lam cong kich hoat tot hon khong.

KHONG dinh nghia lai su kien: dung DUNG 26 su kien washout trong events.csv (17 su kien 2014+
co ket cuc 60 phien) va DUNG ro `universe_pit` trong basket_pit.csv (= cot nm_pit cua compare_pit.csv).

KHONG NHIN TRUOC: moi gia tri lay tai ngay T (ngay tin hieu, biet duoc luc dong cua T);
vao lenh T+1. Khong dung bat ky gia tri nao sau T.

Output: p2/rev_signals.csv (1 dong / su kien).
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from google.cloud import bigquery

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/'
P2 = EXP + 'p2/'
c = bigquery.Client(project='lithe-record-440915-m9')

C = pd.read_csv(EXP + 'compare_pit.csv', parse_dates=['event'])
vni = pd.read_csv(EXP + 'vni.csv', parse_dates=['time']).sort_values('time').reset_index(drop=True)

# ---------------------------------------------------------------- A. muc THI TRUONG (VNINDEX)
# Tu tinh tu chuoi Close cua VNINDEX (khong dung cot mirror nao) -> minh bach, causal.
v = vni.set_index('time')
v['lo21'] = v.Close.rolling(21, min_periods=10).min()      # day 1 thang (bao gom hom nay)
v['lo63'] = v.Close.rolling(63, min_periods=30).min()      # day 3 thang
v['reb1m'] = 100 * (v.Close / v.lo21 - 1)                  # % da hoi tu day 1M  (>=0)
v['reb3m'] = 100 * (v.Close / v.lo63 - 1)
v['dsince_lo21'] = v.Close.rolling(21, min_periods=10).apply(lambda x: len(x) - 1 - int(np.argmin(x)), raw=True)
v['ma20'] = v.Close.rolling(20).mean()
v['above_ma20'] = 100 * (v.Close / v.ma20 - 1)
v['up3'] = 100 * (v.Close / v.Close.shift(3) - 1)          # momentum 3 phien gan nhat
v['up5'] = 100 * (v.Close / v.Close.shift(5) - 1)
# RSI(14) + MACDdiff cua VNINDEX — TU TINH tu Close (cot mirror VNINDEX_RSI/VNINDEX_MACDdiff
# KHONG ton tai trong tav2_bq.ticker du CLAUDE.md co liet ke; da kiem schema 2026-08-03).
_d = v.Close.diff()
_g = _d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
_l = (-_d.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
v['rsi'] = 100 - 100 / (1 + _g / _l)
v['rsi_up1m'] = v.rsi - v.rsi.rolling(21, min_periods=10).min()   # RSI da hoi bao nhieu tu day 1M
_macd = v.Close.ewm(span=12, adjust=False).mean() - v.Close.ewm(span=26, adjust=False).mean()
v['macddiff'] = _macd - _macd.ewm(span=9, adjust=False).mean()

# ---------------------------------------------------------------- B. muc RO (mean tren ro pit tai T)
COLS = ['C_L1W', 'C_L1M', 'D_RSI', 'D_RSI_Min1W', 'D_RSI_Min3M', 'D_MACDdiff',
        'D_CMB_XFast', 'D_CMB_Peak_T1', 'D_CMB']
rows = []
for _, e in C.iterrows():
    d = e.event.date()
    names = [t for t in str(e.nm_pit).split(',') if t]
    r = dict(event=e.event, n_pit=len(names))
    if names:
        inl = ','.join(f"'{t}'" for t in names)
        df = c.query(f"""SELECT t.ticker, {', '.join('t.'+x for x in COLS)}
FROM tav2_bq.ticker t WHERE t.time = DATE '{d}' AND t.ticker IN ({inl})""").to_dataframe()
        if len(df):
            r['n_row'] = len(df)
            r['b_reb1m'] = 100 * (df.C_L1M.mean() - 1)          # % ro da hoi tu day 1M
            r['b_reb1w'] = 100 * (df.C_L1W.mean() - 1)
            r['b_reb1m_med'] = 100 * (df.C_L1M.median() - 1)
            r['b_rsi'] = df.D_RSI.mean()
            r['b_rsi_up1w'] = 100 * (df.D_RSI - df.D_RSI_Min1W).mean()   # RSI da hoi bao nhieu tu day 1W
            r['b_rsi_up3m'] = 100 * (df.D_RSI - df.D_RSI_Min3M).mean()
            r['b_macd'] = df.D_MACDdiff.mean()
            r['b_macd_pos'] = 100 * (df.D_MACDdiff > 0).mean()   # % ten co MACDdiff duong
            r['b_xfast'] = df.D_CMB_XFast.mean()
            r['b_xfast_med'] = df.D_CMB_XFast.median()
            r['b_cmbpk_neg'] = 100 * (df.D_CMB_Peak_T1 < 0).mean()
            r['b_cmb'] = df.D_CMB.mean()
    # muc thi truong tai T
    if e.event in v.index:
        row = v.loc[e.event]
    else:
        row = v.reindex([e.event], method='ffill').iloc[0]
    for k in ['reb1m', 'reb3m', 'dsince_lo21', 'above_ma20', 'up3', 'up5', 'rsi', 'rsi_up1m', 'macddiff']:
        r['m_' + k] = float(row[k])
    rows.append(r)
    print(f"  {d} n={r['n_pit']} reb1m_ro={r.get('b_reb1m', np.nan):.2f}% reb1m_vni={r['m_reb1m']:.2f}% "
          f"dsince_lo={r['m_dsince_lo21']:.0f}")

R = pd.DataFrame(rows)
R.to_csv(P2 + 'rev_signals.csv', index=False)
print(f'\nDONE -> rev_signals.csv  ({len(R)} su kien)')
