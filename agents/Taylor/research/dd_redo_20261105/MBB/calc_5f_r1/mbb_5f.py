"""5F/3c addendum MBB (job Taylor_20261107_130206). Chay: $DNA_PYEXE -I mbb_5f.py > mbb_5f_out.txt
KHONG ghi SUMMARY.json/grid r2. Mo hinh RI + luoi 180 o chep nguyen calc/mbb_r2.py (kich ban, droe, dg, MBV);
chi them bien the terminal theo luat 3c:
  CUR    = hien hanh (ROE_T kich ban giu vinh vien, RI terminal tang g_T neu ROE_T>=Ke)  [= WIDE ngam]
  R      = chi RONIC=Ke (RI terminal khong tang, doi xung moi o)
  M      = chi ROE -> TB chu ky nganh (fade N nam), giu g_T
  NARROW = RONIC=Ke + ROE fade -> TB chu ky nganh trong N=5 nam (headline 3c)
  NONE   = RONIC=Ke + ROE fade -> Ke trong N=2 nam
droe ap ca vao dich nganh (doi xung). Quy uoc nam: nhu mo hinh (nam 1 = 2027 chiet khau 1 ky tu 31/12/2026)."""
import os, sys, csv, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014125'))
import common as C
import r2common as R2C

TK = 'MBB'
BV = 164141.608 - 7124.845; SH = 10068.749885; NI9 = 23784.072; LT9 = 30518.358
L = C.liquidity(TK, free_float=0.60, ff_src='(uoc luong) nhu mbb_r2.py')
PX, PXD = L['last_price'], L['last_date']
A = C.anchor_info(); R = A['r']
DAYS = (np.datetime64('2026-12-31') - np.datetime64(PXD)).astype(int)
SC = {'XAU': (0.35, 16000, 7500, [0.13, 0.14, 0.15], 0.14, 0.06),
      'CO_SO': (0.45, 17500, 5500, [0.185, 0.18, 0.17], 0.16, 0.07),
      'TOT': (0.20, 18700, 4200, [0.22, 0.21, 0.20], 0.18, 0.08)}
TAX, NCI, PAYOUT = 0.20, 0.025, 0.30
base = {}
for n, (w, pp4, dp4, path, roeT, gT) in SC.items():
    ni26 = (LT9 + pp4 - dp4) * (1 - TAX) * (1 - NCI)
    base[n] = dict(bv26=BV + (ni26 - NI9), path=path, roeT=roeT, gT=gT)

# ---- TB chu ky nganh: ROE10Y peer (BQ ticker_financial quy moi nhat), bo MBB ----
peer = {r['ticker']: r for r in csv.DictReader(open(os.path.join(HERE, 'peer_roe_bq_20261107.csv')))}
LARGE = ['VCB', 'BID', 'CTG', 'TCB', 'VPB', 'ACB', 'HDB', 'LPB', 'STB', 'SHB', 'VIB']   # nhom quy mo lon (uoc luong theo tong tai san, can kiem chung)
def agg(tks, col='ROE10Y'):
    v = np.array([float(peer[t][col]) for t in tks]); return float(np.median(v)), float(v.mean())
ALL = [t for t in peer if t != 'MBB']; ALLX = [t for t in ALL if t != 'NVB']
IND = {'all_ex_NVB_med': agg(ALLX)[0], 'all_ex_NVB_mean': agg(ALLX)[1], 'all_mean': agg(ALL)[1],
       'large_med': agg(LARGE)[0], 'large_mean': agg(LARGE)[1]}


def ri(path, roeT, gT, ke, bv0, mode, tgt=None, N=5):
    bv = bv0; pv = 0.0; yrs = list(path)
    if mode in ('M', 'NARROW', 'NONE'):
        end = ke if mode == 'NONE' else tgt
        yrs += [roeT + (end - roeT) * k / N for k in range(1, N + 1)]; roe_term = end
    else:
        roe_term = roeT
    for i, r in enumerate(yrs, 1):
        pv += (r - ke) * bv / (1 + ke) ** i; bv += r * bv * (1 - PAYOUT)
    if mode in ('R', 'NARROW', 'NONE'): g_ri = 0.0
    else: g_ri = 0.0 if roe_term < ke else gT          # luat 03/11 cua mo hinh hien hanh
    tv = (roe_term - ke) * bv / (ke - g_ri) / (1 + ke) ** len(yrs)
    return (bv0 + pv + tv) / SH * 1e3 / (1 + ke) ** (DAYS / 365)


def fn_factory(mode, tgt=None, N=5):
    def fn(r, scen, droe, dg, mbv):
        b = base[scen]
        return ri([x + droe for x in b['path']], b['roeT'] + droe, b['gT'] + dg, r, b['bv26'] - mbv, mode,
                  None if tgt is None else tgt + droe, N)
    return fn

DROE = (-0.03, -0.015, 0.0, 0.015, 0.03); DG = (-0.01, 0.0, 0.01)
MBV_AX = ((-3500, 0.15), (0, 0.50), (3500, 0.25), (15688, 0.10))
axes = [('scen', [(n, SC[n][0]) for n in SC]), ('droe', [(x, 0.2) for x in DROE]), ('dg', [(x, 1 / 3) for x in DG]), ('mbv', list(MBV_AX))]
LQ = R2C.liq2(TK); d5 = LQ['d_ref']; d40 = LQ['d_sleeve']['40tr']; d10 = LQ['d_sleeve']['10tr']

def run(mode, tgt=None, N=5):
    f = fn_factory(mode, tgt, N); res = R2C.outcomes(axes, lambda **kw: f(R, **kw))
    s = R2C.stats(res, PX, d5); s40 = R2C.stats(res, PX, d40)
    return dict(main=s, label=R2C.label(PX, s), s40=dict(p10=s40['p10'], p90=s40['p90'], center=s40['center']), label40=R2C.label(PX, s40),
                central=f(R, 'CO_SO', 0.0, 0.0, 0) * (1 - d5))

print(f"== MBB 5F/3c | gia {PX:,.0f} ({PXD}) | r {R:.2%} | CK 5 ty {d5:.4%} | 40tr {d40:.5%}")
print("TB chu ky nganh ROE10Y (bo MBB): " + ' | '.join(f"{k} {v:.2%}" for k, v in IND.items()))
print(f"MBB: ROE5Y {float(peer['MBB']['ROE5Y']):.2%} ROE10Y {float(peer['MBB']['ROE10Y']):.2%} ROE_Min5Y {float(peer['MBB']['ROE_Min5Y']):.2%} ROE_Min10Y {float(peer['MBB']['ROE_Min10Y']):.2%} ROIC5Y(BQ) {peer['MBB']['ROIC5Y']}")
V = {}
V['CUR'] = run('CUR'); V['R'] = run('R')
for k in ('all_ex_NVB_med', 'all_ex_NVB_mean', 'large_med', 'large_mean'):
    V[f'M_{k}'] = run('M', IND[k]); V[f'NARROW_{k}'] = run('NARROW', IND[k])
V['NARROW_N10_all_ex_NVB_med'] = run('NARROW', IND['all_ex_NVB_med'], 10)
V['NONE'] = run('NONE', N=2)
for k, v in V.items():
    m = v['main']
    print(f"{k:28s} tam {m['center']:7,.0f} P10 {m['p10']:7,.0f} P50 {m['p50']:7,.0f} P90 {m['p90']:7,.0f} %duoi {m['pct_below_px']:5.1%} | {v['label']} | 40tr P10/P90 {v['s40']['p10']:,.0f}/{v['s40']['p90']:,.0f} {v['label40']} | trung tam {v['central']:,.0f}")
json.dump(dict(price=PX, price_date=PXD, r=R, ind=IND, variants={k: dict(center=v['main']['center'], p10=v['main']['p10'], p50=v['main']['p50'], p90=v['main']['p90'],
          pct_below=v['main']['pct_below_px'], label=v['label'], s40=v['s40'], label40=v['label40'], central=v['central']) for k, v in V.items()}),
          open(os.path.join(HERE, 'mbb_5f_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
LOCK = R2C.md5s([os.path.abspath(__file__), os.path.join(HERE, 'peer_roe_bq_20261107.csv'), os.path.join(HERE, '..', 'calc', 'mbb_r2.py')])
for k, v in LOCK.items(): print(f"LOCK {v} {k}")
