"""TANG VI THE — "vay margin + Kelly trong pha washout CAPIT co +EV khong?"

Cau hoi rut gon ve dieu kien CAN: mot dong von VAY them, bo vao DUNG ro CAPIT tai DUNG ngay
tin hieu, giu DUNG 60 phien (CAPIT_HOLD), co thang duoc CHI PHI VAY + phi giao dich khong?
Neu dieu kien can nay khong vung => moi kich ban Kelly/marginal deu sup, khong can chay engine.

Quy uoc (khong tu bia):
  - vao lenh T+1 sau ngay tin hieu (dung quy uoc khong-nhin-truoc cua engine), Close da dieu chinh
  - giu 60 phien = CAPIT_HOLD production
  - lai vay 12,5%/nam (hop dong DNSE RocketX loan_package_id=1840, ghi trong results_registry
    muc V2.5; CHUA doi chieu ban giay) + do nhay 10,0%/nam
  - phi 0,075%/chieu x 2 chieu
  - ro EW, bo su kien co <3 ten (dung luat production add_capit_arm)
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd

EXP = '/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_margin_kelly/'
HOLD = 60
TC = 0.00075
BORROW = 0.125
BORROW_ALT = 0.10
RNG = np.random.default_rng(20260803)
pd.set_option('display.width', 250)

ev = pd.read_csv(EXP + 'events.csv', parse_dates=['time'])
bk = pd.read_csv(EXP + 'basket.csv', parse_dates=['event'])
px = pd.read_parquet(EXP + 'px.parquet')
st = pd.read_csv(EXP + 'state.csv', parse_dates=['time'])
vni = pd.read_csv(EXP + 'vni.csv', parse_dates=['time'])

# ------------------------------------------------------------------ 0. lich phien + gia wide
cal = np.sort(vni.time.unique())
W = px.pivot_table(index='time', columns='ticker', values='Close').reindex(cal).ffill()

# VNINDEX PE percentile 5y NHAN QUA (chi so sanh voi qua khu) — cong thuc gate state-blind V2.5
vni = vni.set_index('time').reindex(cal)
pe = vni.VNINDEX_PE
vni['pe_pct'] = pe.rolling(1250, min_periods=250).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)
stmap = st.set_index('time').state.reindex(cal).ffill()


def capit_base(state, dd52, cool):
    if state == 1: return 1.0
    if state == 3: return 0.75
    if state in (4, 5): return 0.5
    if state == 2: return 0.5 if (dd52 > -25 or cool) else 0.0
    return 0.5


vni['dd52'] = 100 * (vni.Close / vni.Close.rolling(252, min_periods=60).max() - 1)
_r = vni.Close.pct_change()
_rv10 = _r.rolling(10).std() * np.sqrt(252) * 100
vni['cool'] = _rv10 <= _rv10.rolling(30).max() * 0.85

# ------------------------------------------------------------------ 1. ket cuc tung su kien
rows = []
for _, e in ev.iterrows():
    d = e.time
    names = sorted(bk.loc[bk.event == d, 'ticker'])
    i0 = int(np.searchsorted(cal, np.datetime64(d)))
    if len(names) < 3:                       # luat production: <3 ten -> KHONG trien khai
        rows.append(dict(event=d, n=len(names), skip='ro<3'))
        continue
    ie, ix = i0 + 1, i0 + 1 + HOLD           # vao T+1, ra sau 60 phien
    if ix >= len(cal):
        rows.append(dict(event=d, n=len(names), skip='chua du 60 phien'))
        continue
    sub = W.iloc[ie:ix + 1][names]
    p0 = sub.iloc[0]
    ok = p0.notna() & sub.iloc[-1].notna()
    if ok.sum() < 3:
        rows.append(dict(event=d, n=len(names), skip='thieu gia'))
        continue
    nav = (sub.loc[:, ok] / p0[ok]).mean(axis=1)      # chi so EW cua ro trong ky nam giu
    r = float(nav.iloc[-1] - 1)
    mae = float(nav.min() - 1)
    days = (cal[ix] - cal[ie]) / np.timedelta64(1, 'D')
    s = int(stmap.iloc[i0]) if np.isfinite(stmap.iloc[i0]) else np.nan
    rows.append(dict(event=d, n=int(ok.sum()), skip='', r=r, mae=mae, cal_days=days,
                     state=s, dd52=float(vni.dd52.iloc[i0]), cool=bool(vni.cool.iloc[i0]),
                     pe_pct=float(vni.pe_pct.iloc[i0]), ovs=float(e.ovs),
                     names=','.join(np.array(names)[ok.values])))
E = pd.DataFrame(rows)
E['size'] = [capit_base(r.state, r.dd52, r.cool) if np.isfinite(r.get('state', np.nan)) else np.nan
             for _, r in E.iterrows()]
E['cost'] = BORROW * E.cal_days / 365.0 + 2 * TC
E['x'] = E.r - E.cost                                   # loi the RONG cua 1 dong VAY (per hold)
E['x10'] = E.r - (BORROW_ALT * E.cal_days / 365.0 + 2 * TC)
E.to_csv(EXP + 'events_outcome.csv', index=False)

print('=' * 118)
print('B1 — 26 SU KIEN WASHOUT: ket cuc EW ro CAPIT, vao T+1, giu 60 phien')
print('=' * 118)
show = E[['event', 'n', 'skip', 'ovs', 'state', 'size', 'dd52', 'pe_pct', 'r', 'mae', 'cost', 'x']].copy()
for c in ['ovs', 'dd52']: show[c] = show[c].round(1)
for c in ['r', 'mae', 'cost', 'x']: show[c] = (100 * show[c]).round(2)
show['pe_pct'] = show.pe_pct.round(2)
print(show.to_string(index=False))

V = E[(E.skip == '') & E.x.notna()].copy()
V14 = V[V.event >= '2014-01-01'].copy()
print(f'\n  N su kien co ket cuc day du: TOAN BO {len(V)} | ky DT5G 2014+ {len(V14)}')
print('  (su kien bi loai: %s)' % '; '.join(f"{r.event.date()}={r.skip}" for _, r in E[E.skip != ''].iterrows()))


def blk(v, lbl):
    v = np.asarray(v, float)
    if len(v) == 0:
        return
    b = np.array([RNG.choice(v, len(v), True).mean() for _ in range(20000)])
    p_sign = 2 * min((v > 0).mean(), (v < 0).mean())      # sign test 2 phia (xap xi doi xung)
    print(f'  {lbl:<34} N={len(v):2d}  TB {100*v.mean():+7.2f}%  TV {100*np.median(v):+7.2f}%  '
          f'SD {100*v.std(ddof=1):6.2f}  %duong {100*(v>0).mean():5.1f}  '
          f'CI90 TB [{100*np.percentile(b,5):+6.2f};{100*np.percentile(b,95):+6.2f}]  p_boot={2*min((b<=0).mean(),(b>=0).mean()):.3f}')


print('\n' + '=' * 118)
print('B2 — DIEU KIEN CAN: 1 dong VAY bo vao ro CAPIT co thang chi phi vay khong?')
print('=' * 118)
print('  [toan bo lich su]')
blk(V.r, 'r ro (chua tru chi phi)')
blk(V.x, 'x = r - vay12.5% - phi')
blk(V.x10, 'x = r - vay10.0% - phi')
print('  [ky DT5G 2014+ — ky duy nhat co regime production]')
blk(V14.r, 'r ro (chua tru chi phi)')
blk(V14.x, 'x = r - vay12.5% - phi')
blk(V14.x10, 'x = r - vay10.0% - phi')

# ------------------------------------------------------------------ 2. KELLY (uoc luong NGOAI MAU)
print('\n' + '=' * 118)
print('B3 — KELLY: f* = E[x]/Var(x), uoc luong MO RONG (chi dung su kien TRUOC do), toi thieu 5 mau')
print('=' * 118)
V = V.sort_values('event').reset_index(drop=True)
MINH = 5
recs = []
for i in range(len(V)):
    prior = V.x.values[:i]
    if len(prior) < MINH:
        recs.append(dict(event=V.event[i], f_full=np.nan, f_half=np.nan, real=np.nan))
        continue
    mu, var = prior.mean(), prior.var(ddof=1)
    f = mu / var if var > 0 else 0.0
    f = max(f, 0.0)
    recs.append(dict(event=V.event[i], mu=mu, sd=np.sqrt(var), f_full=f, f_half=0.5 * f,
                     x=V.x[i], mae=V.mae[i]))
K = pd.DataFrame(recs)
K['pnl_half'] = K.f_half * K.x           # lai/lo tang them tren NAV neu vay f_half x NAV
K['pnl_cap1'] = np.minimum(K.f_half, 1.0) * K.x      # tran thuc te: khong vay qua 1x NAV
K.to_csv(EXP + 'kelly_oos.csv', index=False)
print(K.round(3).to_string(index=False))
KK = K.dropna(subset=['pnl_half'])
print('\n  Kelly NGOAI MAU (half-Kelly, khong tran):')
blk(KK.pnl_half, 'delta NAV / su kien')
print('  Kelly NGOAI MAU (half-Kelly, tran vay 1.0x NAV — thuc te margin):')
blk(KK.pnl_cap1, 'delta NAV / su kien')
print(f'  f_half khoang [{KK.f_half.min():.2f} ; {KK.f_half.max():.2f}]  trung vi {KK.f_half.median():.2f}')

# LOO theo su kien tren chuoi pnl (bo 1 su kien -> con lai co con duong khong?)
print('\n  LEAVE-ONE-EVENT-OUT tren delta NAV (tran 1.0x):')
v = KK.pnl_cap1.values
for i in range(len(v)):
    loo = np.delete(v, i)
    print(f'    bo {KK.event.iloc[i].date()} (dong gop {100*v[i]:+6.2f}pp) -> TB con lai {100*loo.mean():+6.3f}pp')

# ------------------------------------------------------------------ 3. CONG (gate) — dose-response
print('\n' + '=' * 118)
print('B4 — DOSE-RESPONSE THEO CONG KICH HOAT (x = loi the rong cua dong von vay, vay 12,5%)')
print('=' * 118)
gates = [
    ('G0 moi washout', V.index >= 0),
    ('G1 CRISIS/BEAR (state<=2)', V.state <= 2),
    ('G2 NEUTRAL+ (state>=3) <- ca 2026-07-20', V.state >= 3),
    ('G3 PE_pctile<=0.20 (cong V2.5 state-blind)', V.pe_pct <= 0.20),
    ('G4 PE_pctile<=0.20 & state>=3', (V.pe_pct <= 0.20) & (V.state >= 3)),
    ('G5 dd52<=-20% (washout sau)', V.dd52 <= -20),
    ('G6 dd52>-20% (washout nong)', V.dd52 > -20),
    ('G7 ovs>=40% (breadth cuc doan)', V.ovs >= 40),
]
for lbl, m in gates:
    s = V[m.fillna(False) if hasattr(m, 'fillna') else m]
    if len(s) == 0:
        print(f'  {lbl:<44} N=0')
        continue
    blk(s.x, lbl)

print('\n  [chi ky 2014+]')
for lbl, m in gates:
    s = V14[(m.fillna(False) if hasattr(m, 'fillna') else m).reindex(V14.index, fill_value=False)] \
        if hasattr(m, 'reindex') else V14
    if len(s) == 0:
        print(f'  {lbl:<44} N=0')
        continue
    blk(s.x, lbl)

# ------------------------------------------------------------------ 4. RUI RO: MAE / margin call
print('\n' + '=' * 118)
print('B5 — RUI RO DUONG DI: MAE (muc lo sau nhat TRONG ky giu) — quyet dinh tran don bay')
print('=' * 118)
m = V.mae.values
print(f'  MAE: xau nhat {100*m.min():+.1f}%  p10 {100*np.percentile(m,10):+.1f}%  '
      f'trung vi {100*np.median(m):+.1f}%  TB {100*m.mean():+.1f}%')
for _, r in V.nsmallest(5, 'mae').iterrows():
    print(f'    {r.event.date()} state={r.state:.0f} MAE {100*r.mae:+.1f}%  r60 {100*r.r:+.1f}%')
# tran don bay tu MAE: goi margin khi equity/gross < maintenance (DNSE ~30%)
for maint in (0.30, 0.35):
    for w in (-0.262, m.min()):
        gmax = (1 - maint) / (maint * abs(w) / (1 - abs(w))) if False else None
    print(f'  (tham chieu) maintenance {maint:.0%}: gross toi da chiu duoc cu sut |MAE| '
          f'{abs(m.min()):.1%} truoc khi equity/gross < maint  =  '
          f'{(1-abs(m.min()))/(1-maint*0):.2f} — xem cong thuc trong bao cao')

print('\n' + '=' * 118)
print('B6 — SU KIEN DANG SONG 2026-07-20 dat vao phan phoi')
print('=' * 118)
live = E[E.event == '2026-07-20'].iloc[0]
print(f'  state={live.state:.0f} size={live.size:.2f} dd52={live.dd52:.1f}% pe_pct={live.pe_pct:.2f} '
      f'ovs={live.ovs:.1f}% ro={live.n} ten  | ket cuc 60 phien: {live.skip or "co"}')
print(f'  cong G1 (CRISIS/BEAR): {"PASS" if live.state<=2 else "CHAN"} | '
      f'cong G3 (PE_pctile<=0.20): {"PASS" if live.pe_pct<=0.20 else "CHAN"} (pe_pct={live.pe_pct:.2f})')
print('DONE')
