"""ROBUSTNESS — thien lech song sot (survivorship) cua ro CAPIT lich su.

Van de: `ticker_prune` la danh sach thanh vien duoc DUNG LAI cho toan bo lich su (CLAUDE.md
changelog 2026-07-29 da xac nhan chinh xac loi nay o breadth: "mot ten duoc nap hom nay duoc dem
o MOI ngay lich su"). Ro CAPIT lich su dung trong analyze.py vi vay CO thien lech song sot
huong LEN. Doi chung: dung `tav2_mike.universe_pit` (thanh vien theo TUNG NGAY) lam pool thay
`ticker_prune`, GIU NGUYEN moi tieu chi con lai cua capit_basket().

Cung file nay va lai state/PE/dd cho MOI su kien (ke ca su kien chua du 60 phien).
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from google.cloud import bigquery

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/'
HOLD, TC, BORROW = 60, 0.00075, 0.125
RNG = np.random.default_rng(20260803)
c = bigquery.Client(project='lithe-record-440915-m9')
pd.set_option('display.width', 250)

ev = pd.read_csv(EXP + 'events.csv', parse_dates=['time'])
bk = pd.read_csv(EXP + 'basket.csv', parse_dates=['event'])
vni = pd.read_csv(EXP + 'vni.csv', parse_dates=['time'])
st = pd.read_csv(EXP + 'state.csv', parse_dates=['time'])

# ------------------------------------------------------------------ ro theo universe_pit
rows = []
for _, e in ev.iterrows():
    d = e.time.date()
    df = c.query(f"""SELECT t.ticker, SAFE_DIVIDE(t.PB-t.PB_MA5Y,t.PB_SD5Y) pbz
FROM tav2_bq.ticker t
JOIN tav2_mike.universe_pit u ON u.ticker=t.ticker AND u.time=t.time AND u.in_universe
WHERE t.time = DATE '{d}' AND t.ROE_Min5Y>=0.12 AND t.ROIC5Y>=0.10 AND t.FSCORE>=6
  AND COALESCE(t.Price,t.Close)*t.Volume/1e9 >= 2""").to_dataframe()
    if df.empty:
        continue
    g = df[df.pbz < -1]; cc = df[df.pbz < 0]
    pick = g if len(g) >= 3 else (cc if len(cc) >= 3 else df)
    pick = pick.nsmallest(15, 'pbz') if len(pick) > 15 else pick
    for _, r in pick.iterrows():
        rows.append({'event': e.time, 'ticker': r.ticker, 'pbz': r.pbz})
bp = pd.DataFrame(rows)
bp.to_csv(EXP + 'basket_pit.csv', index=False)

# ------------------------------------------------------------------ gia cho MOI ten (2 ro)
names = sorted(set(bp.ticker) | set(bk.ticker))
inl = ','.join(f"'{t}'" for t in names)
px = c.query(f"""SELECT t.time, t.ticker, t.Close FROM tav2_bq.ticker t
WHERE t.ticker IN ({inl}) AND t.time >= DATE '2008-01-01'""").to_dataframe()
px['time'] = pd.to_datetime(px['time'])

cal = np.sort(vni.time.unique())
W = px.pivot_table(index='time', columns='ticker', values='Close').reindex(cal).ffill()
vni = vni.set_index('time').reindex(cal)
vni['pe_pct'] = vni.VNINDEX_PE.rolling(1250, min_periods=250).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)
vni['dd52'] = 100 * (vni.Close / vni.Close.rolling(252, min_periods=60).max() - 1)
stmap = st.set_index('time').state.reindex(cal).ffill()


def outcome(d, names):
    i0 = int(np.searchsorted(cal, np.datetime64(d)))
    out = dict(state=stmap.iloc[i0], pe_pct=vni.pe_pct.iloc[i0], dd52=vni.dd52.iloc[i0], n=len(names))
    if len(names) < 3:
        out['skip'] = 'ro<3'; return out
    ie, ix = i0 + 1, i0 + 1 + HOLD
    if ix >= len(cal):
        out['skip'] = 'chua du 60 phien'; return out
    sub = W.iloc[ie:ix + 1][names]
    p0 = sub.iloc[0]; ok = p0.notna() & sub.iloc[-1].notna()
    if ok.sum() < 3:
        out['skip'] = 'thieu gia'; return out
    nav = (sub.loc[:, ok] / p0[ok]).mean(axis=1)
    days = (cal[ix] - cal[ie]) / np.timedelta64(1, 'D')
    out.update(skip='', n=int(ok.sum()), r=float(nav.iloc[-1] - 1), mae=float(nav.min() - 1),
               x=float(nav.iloc[-1] - 1) - (BORROW * days / 365.0 + 2 * TC))
    return out


rows = []
for _, e in ev.iterrows():
    d = e.time
    a = outcome(d, sorted(bk.loc[bk.event == d, 'ticker']))
    b = outcome(d, sorted(bp.loc[bp.event == d, 'ticker']))
    rows.append(dict(event=d, ovs=e.ovs, state=a['state'], pe_pct=a['pe_pct'], dd52=a['dd52'],
                     n_prune=a['n'], r_prune=a.get('r', np.nan), x_prune=a.get('x', np.nan),
                     n_pit=b['n'], r_pit=b.get('r', np.nan), x_pit=b.get('x', np.nan),
                     skip=a.get('skip', ''),
                     nm_prune=','.join(sorted(bk.loc[bk.event == d, 'ticker'])),
                     nm_pit=','.join(sorted(bp.loc[bp.event == d, 'ticker']))))
C = pd.DataFrame(rows)
C.to_csv(EXP + 'compare_pit.csv', index=False)

print('=' * 130)
print('A — RO ticker_prune (production) vs RO universe_pit (point-in-time) — kiem thien lech song sot')
print('=' * 130)
s = C[['event', 'ovs', 'state', 'pe_pct', 'dd52', 'n_prune', 'r_prune', 'n_pit', 'r_pit', 'skip']].copy()
for cl in ['r_prune', 'r_pit']: s[cl] = (100 * s[cl]).round(2)
for cl in ['ovs', 'dd52']: s[cl] = s[cl].round(1)
s['pe_pct'] = s.pe_pct.round(2)
print(s.to_string(index=False))

both = C[(C.skip == '') & C.x_prune.notna() & C.x_pit.notna()]
b14 = both[both.event >= '2014-01-01']


def blk(v, lbl):
    v = np.asarray(v, float)
    b = np.array([RNG.choice(v, len(v), True).mean() for _ in range(20000)])
    print(f'  {lbl:<40} N={len(v):2d} TB {100*v.mean():+7.2f}% TV {100*np.median(v):+7.2f}% '
          f'%duong {100*(v>0).mean():5.1f}  CI90 [{100*np.percentile(b,5):+6.2f};{100*np.percentile(b,95):+6.2f}] '
          f'p_boot={2*min((b<=0).mean(),(b>=0).mean()):.3f}')


print('\n  x = loi the RONG cua 1 dong VAY (r - vay 12,5% - phi) — 2 nguon pool:')
blk(both.x_prune, 'ticker_prune (co thien lech song sot)')
blk(both.x_pit, 'universe_pit (point-in-time)')
blk(both.x_pit - both.x_prune, 'HIEU pit - prune (thien lech)')
print('  [2014+]')
blk(b14.x_prune, 'ticker_prune 2014+')
blk(b14.x_pit, 'universe_pit 2014+')
blk(b14.x_pit - b14.x_prune, 'HIEU pit - prune 2014+')

print('\n  Ro khac nhau o may su kien: %d/%d' % ((C.nm_prune != C.nm_pit).sum(), len(C)))
print('\n  Chi tiet su kien LIVE 2026-07-20:')
lv = C[C.event == '2026-07-20'].iloc[0]
print(f'    state={lv.state:.0f} dd52={lv.dd52:.1f}% pe_pct={lv.pe_pct:.2f} ovs={lv.ovs:.1f}%')
print(f'    ro prune ({lv.n_prune}): {lv.nm_prune}')
print(f'    ro pit   ({lv.n_pit}): {lv.nm_pit}')

print('\n  Cong V2.5 state-blind (PE_pctile<=0.20) tai TUNG su kien 2014+:')
for _, r in C[C.event >= '2014-01-01'].iterrows():
    print(f'    {r.event.date()} state={r.state:.0f} pe_pct={r.pe_pct:.2f} '
          f'-> {"PASS" if r.pe_pct <= 0.20 else "CHAN"}   x_pit={100*r.x_pit:+.1f}%' if np.isfinite(r.x_pit)
          else f'    {r.event.date()} state={r.state:.0f} pe_pct={r.pe_pct:.2f} '
               f'-> {"PASS" if r.pe_pct <= 0.20 else "CHAN"}   x_pit=(chua du)')
print('DONE')
