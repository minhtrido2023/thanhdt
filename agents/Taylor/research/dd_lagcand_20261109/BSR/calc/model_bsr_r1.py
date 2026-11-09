"""DD BSR (job Taylor_20261109_073600). Mo hinh mu gia thi truong (gia chi dung de dan nhan + thanh khoan).
Gia tri = loi lam chuan hoa / Ke (RONIC=Ke, buoc thue 10%->20% sau 2039) + LN vuot nen 2026Q4-2028 (PV)
        + tien rong + CIP (NPV0) - quy KHCN + giai phong von luu dong vuot (truc).
Doc moi gia dinh tu assumptions.json (khoa md5 o LOCK_md5.txt). Chay: python3 -I model_bsr.py"""
import os, sys, json, csv, math, hashlib, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
import numpy as np
from deposit_rate_vn import effective_deposit_rate

A = json.load(open(os.path.join(HERE, 'assumptions.json')))
A_MD5 = hashlib.md5(open(os.path.join(HERE, 'assumptions.json'), 'rb').read()).hexdigest()
SH = A['shares_m']; B = A['bs_bn']

# --- kiem lai LN lich su tu CSV BQ (khong tin so chep tay)
rows = list(csv.DictReader(open(os.path.join(HERE, 'bq_bsr_fin.csv'))))
yr = {}
for r in rows:
    if r['NP_P0']:
        yr.setdefault(r['quarter'][:4], []).append(float(r['NP_P0']) / 1e9)
np_hist = {y: sum(v) for y, v in yr.items() if len(v) == 4}
for y, v in A['np_hist_bn'].items():
    if y.startswith('_'): continue
    assert abs(np_hist[y] - v) < 2.0, (y, np_hist[y], v)
avg2325 = np.mean([np_hist[y] for y in ('2023', '2024', '2025')]); avg1925 = np.mean([np_hist[str(y)] for y in range(2019, 2026)])
core2325 = avg2325 - A['interest_ann_aftertax_bn']['2023_25']

# --- r gan lai huy dong
d0 = effective_deposit_rate(A['anchor_date']); d1 = effective_deposit_rate(A['price_date'])
R = A['r_anchor'] + 1.0 * (d1['rate'] - d0['rate'])

# --- thanh khoan
px = [r for r in csv.DictReader(open(os.path.join(HERE, 'px_bsr.csv'))) if r['time'] <= A['price_date']]
PX = float(px[-1]['Price']); PXD = px[-1]['time']
def liq():
    out = {}
    for n in (250, 60):
        d = px[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        out[f'adv{n}'] = dict(window=f"{d[1]['time']}..{d[-1]['time']}", n=len(val), adv_med=adv, sigma_d=sig,
                              disc={f'{q:.0f}': sig * math.sqrt(q / adv) for q in A['liq']['sizes_vnd']},
                              part={f'{q:.0f}': q / adv for q in A['liq']['sizes_vnd']})
    return out
L = liq()
CK = {'5ty': L['adv250']['disc']['5000000000'], '40tr': L['adv250']['disc']['40000000'], '10tr': L['adv250']['disc']['10000000']}

# --- cau phan
NC = B['cash_110'] + B['htm_123'] - B['st_debt_321'] - B['lt_debt']
FIXED = NC + B['cip_252'] + B['lt_invest_260'] - B['khcn_fund_344']
wc_now = sum(A['wc_bn']['now'].values()); wc_start = sum(A['wc_bn']['start'].values()); WC_EX = wc_now - wc_start
TS = A['tax_step']
def ops_value(nopat, ke):
    v13 = (1 + ke) ** -TS['years_left']
    after = (1 - TS['rate_after']) / (1 - TS['rate_now'])
    return nopat / ke - nopat * (1 - after) * v13 / ke          # RONIC = Ke => g khong tao gia tri
WF = A['windfall_np_bn']
def windfall(sc, ke, mult):
    # Q4/26 nhan ~0,25 nam; 2027 giua nam ~0,64 nam; 2028 ~1,64 nam
    return mult * (WF['Q4_2026'][sc] / (1 + ke) ** 0.25 + WF['Y2027'][sc] / (1 + ke) ** 0.64 + WF['Y2028'][sc] / (1 + ke) ** 1.64)
SCN = ('XAU', 'CO_SO', 'TOT')
def value(sc, ke, nshift, wcrel, wmult):
    n = A['core_nopat_bn'][sc] * (1 + nshift)
    eq = ops_value(n, ke) + windfall(sc, ke, wmult) + FIXED + wcrel * WC_EX
    return eq / SH * 1000.0   # d/cp

def grid(w, ke, ck=0.0):
    out = []
    for sc, (ns, wn), (wr, ww), (wm, wwm) in itertools.product(SCN, A['nopat_shift_axis'], A['wc_release_axis'], WF['multiplier_axis']):
        out.append((value(sc, ke, ns, wr, wm) * (1 - ck), w[sc] * wn * ww * wwm, sc))
    return out
def stats(g):
    v = np.array([x[0] for x in g]); p = np.array([x[1] for x in g]); o = np.argsort(v); v, p = v[o], p[o]; c = np.cumsum(p) / p.sum()
    q = lambda t: float(v[np.searchsorted(c, t)])
    return dict(center=float((v * p).sum() / p.sum()), p10=q(0.10), p25=q(0.25), p50=q(0.50), p75=q(0.75), p90=q(0.90),
                pct_below_px=float(p[v < PX].sum() / p.sum()), min=float(v.min()), max=float(v.max()), n=len(v))
def label(s):
    return 'DƯỚI vùng' if PX < s['p10'] else ('TRÊN vùng' if PX > s['p90'] else 'TRONG vùng')
r0 = lambda x: int(round(x))

W = A['weights']
pre = stats(grid(W['bobby'], R)); post = stats(grid(W['bobby'], R, CK['5ty'])); s40 = stats(grid(W['bobby'], R, CK['40tr']))
sym = stats(grid(W['sym'], R, CK['5ty']))
by_sc = {sc: value(sc, R, 0, A['wc_release_axis'][1][0], 1.0) for sc in SCN}
sens_r = {k: stats(grid(W['bobby'], R + dr, CK['5ty']))['center'] for k, dr in (('+100bp', .01), ('+50bp', .005), ('-50bp', -.005), ('-100bp', -.01))}
# do nhay moat (thong tin): neu moat WIDE gia dinh RONIC 20% voi g 4% -> he so (1-g/RONIC)/(Ke-g) thay 1/Ke
def moat_alt(ronic, g=0.04):
    f = (1 - g / ronic) / (R - g) * R
    return stats([(x[0] - 0, x[1], x[2]) for x in grid(W['bobby'], R, CK['5ty'])])['center'] + \
        sum(W['bobby'][sc] * A['core_nopat_bn'][sc] * (f - 1) / R for sc in SCN) / SH * 1000 * (1 - CK['5ty'])
moat_sens = {'NONE/NARROW (RONIC=Ke, headline)': post['center'], 'WIDE gia dinh RONIC 20%, g 4%': moat_alt(0.20)}
# gia ngu y
def solve(f, lo, hi):
    for _ in range(80):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) > 0 else (lo, m)
    return (lo + hi) / 2
ke_imp = solve(lambda k: stats(grid(W['bobby'], k, CK['5ty']))['center'] - PX, 0.03, 0.30)
n_imp = solve(lambda n: PX - (ops_value(n, R) + sum(W['bobby'][sc] * windfall(sc, R, 1.0) for sc in SCN) + FIXED + 0.27 * WC_EX) / SH * 1000 * (1 - CK['5ty']), 0, 80000)
grm_1usd = A['grm_sens']['bbl_m'] * A['grm_sens']['usdvnd'] / 1000 * (1 - A['grm_sens']['tax'])   # ty/nam / 1 USD/thung
comp = dict(net_cash_ps=NC / SH * 1000, fixed_ps=FIXED / SH * 1000, wc_ex_bn=WC_EX, wc_now=wc_now, wc_start=wc_start,
            ops_ps={sc: ops_value(A['core_nopat_bn'][sc], R) / SH * 1000 for sc in SCN},
            windfall_ps={sc: windfall(sc, R, 1.0) / SH * 1000 for sc in SCN}, by_scen_mid=by_sc)
pe = dict(ttm_np_bn=np_hist.get('2026', 0) or sum(float(r['NP_P0']) / 1e9 for r in rows[-4:]), mcap_bn=PX * SH / 1000)
pe['pe_ttm'] = pe['mcap_bn'] / pe['ttm_np_bn']; pe['pb'] = PX / (83524.554 / SH * 1000)
out = dict(price=PX, pxd=PXD, r=R, dep=dict(d0=d0, d1=d1), assumptions_md5=A_MD5, liq=L, ck=CK, pre=pre, post=post, sleeve40=s40, sym=sym,
           sens_r=sens_r, moat_sens=moat_sens, implied=dict(ke=ke_imp, dep12_implied=ke_imp - A['r_anchor'] + d0['rate'], core_nopat_bn=n_imp,
           core_nopat_x_hist=n_imp / core2325, grm_usd_above_base=(n_imp - A['core_nopat_bn']['CO_SO']) / grm_1usd),
           hist=dict(np_hist=np_hist, avg2325=avg2325, avg1925=avg1925, core2325=core2325), grm_1usd_bn=grm_1usd, comp=comp, pe=pe,
           label=label(post), label_40tr=label(s40), label_pre=label(pre), label_sym=label(sym))
json.dump(out, open(os.path.join(HERE, 'model_out.json'), 'w'), indent=1, ensure_ascii=False, default=float)
f = lambda s: f"tam {r0(s['center']):,} P10 {r0(s['p10']):,} P50 {r0(s['p50']):,} P90 {r0(s['p90']):,} | <gia {s['pct_below_px']:.0%}"
print(f"BSR | gia {PX:,.0f} ({PXD}) | r {R:.2%} (dep {d1['rate']:.2%} {d1.get('rate_source')}; neo {d0['rate']:.2%}) | md5 {A_MD5}")
print(f"LN lich su: TB23-25 {avg2325:,.0f} | TB19-25 {avg1925:,.0f} | loi lam 23-25 {core2325:,.0f} ty | PE TTM {pe['pe_ttm']:.2f} PB {pe['pb']:.2f}")
print(f"tien rong {NC:,.0f} ty ({comp['net_cash_ps']:,.0f} d/cp) | FIXED {comp['fixed_ps']:,.0f} d/cp | WC vuot {WC_EX:,.0f} ty (now {wc_now:,.0f} start {wc_start:,.0f})")
print('ops d/cp', {k: r0(v) for k, v in comp['ops_ps'].items()}, '| windfall d/cp', {k: r0(v) for k, v in comp['windfall_ps'].items()}, '| kich ban giua', {k: r0(v) for k, v in by_sc.items()})
print(f"ADV250 {L['adv250']['adv_med']/1e9:,.1f} ty ADV60 {L['adv60']['adv_med']/1e9:,.1f} ty sigma {L['adv250']['sigma_d']:.4f} | CK 5ty {CK['5ty']:.3%} 40tr {CK['40tr']:.4%}")
print('PRE  ', f(pre), label(pre)); print('POST ', f(post), label(post)); print('40tr ', f(s40), label(s40)); print('SYM  ', f(sym), label(sym))
print('sens r', {k: r0(v) for k, v in sens_r.items()}); print('moat', {k: r0(v) for k, v in moat_sens.items()})
print(f"NGU Y: Ke {ke_imp:.2%} | loi lam chuan hoa {n_imp:,.0f} ty = {n_imp/core2325:.1f}x 23-25 = +{out['implied']['grm_usd_above_base']:.1f} USD/thung GRM tren CO_SO ({grm_1usd:,.0f} ty/USD)")
