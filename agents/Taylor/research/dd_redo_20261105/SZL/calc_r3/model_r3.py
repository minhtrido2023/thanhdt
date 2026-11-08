"""SZL VONG 3 (08/11/2026, job Taylor_20261108_164337). Ap/kiem dinh chinh TOP5C_CORRECTIONS_20261108.md muc SZL.
Gia dinh khoa: assumptions_r3.json (md5 vao LOCK_md5.txt TRUOC khi so gia). Hang so BCTC chep tu ../calc/model_r2.py (khong import: file do ghi output khi chay).
Control: tai lap r2 32.391 bang _common_020021/r2lib (gia + thanh khoan 04/11). Gia + thanh khoan r3: px_szl_r3_20261106.csv (BQ tav2_bq.ticker).
Chay: cd calc_r3 && $DNA_PYEXE -I model_r3.py > model_r3_out.txt  (2 lan, cmp trung byte)."""
import csv, hashlib, itertools, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '_common_020021')); sys.path.insert(0, os.path.join(ROOT, '_shared'))
import numpy as np                     # noqa: E402
import r2lib as R2                     # noqa: E402
from wpct import wpct, weight_below    # noqa: E402
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from deposit_rate_vn import effective_deposit_rate   # noqa: E402

A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
ASOF = A['asof_price']
# ---- so BCTC (giong het ../calc/model_r2.py; src/Q3_2026_hopnhat.pdf) ----
SH = 48.198884
CASH = 171.220813690; DIV_PAY = 70.360021125
LOAN_ST, LOAN_LT = 110.030903581, 196.337026604
CIP = 407.037010429; EQ = 784.151356245
DEP_ST = 10.147281118 + 0.230000000; DEP_LT = 146.987107831
DEPOSITS = DEP_ST + DEP_LT
LAND_RENT_ACCR = 44.265169191
INV_BOOK = {"SZC": 221.8, "SZB": 63.0, "An Binh": 24.5, "Binh Thuan": 80.0, "Dich vu": 8.75}
OWN = {"SZC": 0.1008, "SZB": 0.084}
NP_9M = 132.589359502; FIN_REV_9M, FIN_EXP_9M = 37.740263110, 4.326469728
CORE_9M = NP_9M - FIN_REV_9M + FIN_EXP_9M * 0.80
N0 = CORE_9M * 4 / 3
NET_DEBT = LOAN_ST + LOAN_LT - CASH + DIV_PAY
OTHER_LIAB = DEPOSITS + LAND_RENT_ACCR
YRS_LEFT = 27
# ---- r3 ----
K = A['ktpl_rate']['num_ty'] / A['ktpl_rate']['den_ty']
KFUND = A['ktpl_fund_balance_ty']['value']
d0 = effective_deposit_rate('2026-11-03'); d1 = effective_deposit_rate(ASOF)
R = 0.135 + 1.0 * (d1['rate'] - d0['rate'])
PXF = os.path.join(HERE, 'px_szl_r3_20261106.csv')
ROWS = sorted(csv.DictReader(open(PXF)), key=lambda r: (r['ticker'], r['time']))
osh = {r['ticker']: float(r['OShares']) for r in csv.DictReader(open(os.path.join(ROOT, 'SZL', 'calc', 'bq_oshares_szc_szb.csv')))}
px04 = {r['ticker']: float(r['Close']) for r in csv.DictReader(open(os.path.join(ROOT, 'SZL', 'calc', 'bq_szc_szb_20261104.csv')))}
px06 = {}
for r in ROWS:
    if r['time'] == ASOF:
        px06[r['ticker']] = float(r['Close'])


def inv_of(px):
    mkt = {k: OWN[k] * osh[k] * px[k] / 1e9 for k in sorted(OWN)}
    tax = sum(max(mkt[k] - INV_BOOK[k], 0) for k in OWN) * 0.20
    return mkt, tax


UNLISTED = sum(v for k, v in INV_BOOK.items() if k not in OWN)


def liquidity(tk='SZL'):
    rows = [r for r in ROWS if r['ticker'] == tk]
    assert rows[-1]['time'] == ASOF, rows[-1]['time']
    out = dict(price=float(rows[-1]['Price']), price_date=rows[-1]['time'])
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        sz = {}
        for q in (0.01, 0.02, 0.04, 1, 5, 10):
            part = q * 1e9 / adv
            sz[str(q)] = dict(q_bn=q, q_over_adv=part, disc=sig * math.sqrt(part), in_calib=bool(part <= 0.10), days_at20=q * 1e9 / (0.2 * adv), days_at10=q * 1e9 / (0.1 * adv))
        out[f'adv{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), adv_bn=adv / 1e9, sigma_d=sig, zero_vol_days=int((v[1:] == 0).sum()), sizes=sz)
    return out


LQ = liquidity(); PX = LQ['price']
D_REF = LQ['adv250']['sizes']['5']['disc']; D_40 = LQ['adv250']['sizes']['0.04']['disc']


def val(n0=N0, g=0.03, r=R, nc=0.10, T=None, cfg=None):
    c = dict(BASE); c.update(cfg or {})
    cf = n0 * (1 - nc - c['k']) + c['dcf']
    if c['ronic_ke']:
        core = cf / r if T is None else cf * (1 - (1 + r) ** -T) / r
    else:
        core = cf / (r - g) if T is None else cf * (1 - ((1 + g) / (1 + r)) ** T) / (r - g)
    mkt, tax = inv_of(c['px'])
    inv = (sum(mkt.values()) - tax) * (1 - c['hold']) + UNLISTED
    dep_lt = DEP_LT / (1 + r) ** YRS_LEFT if c['dep_pv'] else DEP_LT
    liab = DEP_ST + dep_lt + LAND_RENT_ACCR + c['kfund']
    return (core + inv + CIP + c['add_asset'] - liab - NET_DEBT) / SH * 1000


BASE = dict(k=K, kfund=KFUND, px=px06, hold=0.0, dcf=0.0, ronic_ke=False, dep_pv=False, add_asset=0.0)
R2CFG = dict(k=0.0, kfund=0.0, px=px04)
NS_M = (0.88, 0.94, 1.0, 1.06, 1.12); WN = (0.1, 0.2, 0.4, 0.2, 0.1)
GS = (0.02, 0.03, 0.04); WG = (0.25, 0.5, 0.25)
NCS = (0.20, 0.10, 0.0); WNC = (0.25, 0.5, 0.25)


def grid(cfg=None, tw=(0.75, 0.25), n0=N0, r0=R):
    v, w = [], []
    rs = (r0 - 0.01, r0, r0 + 0.01)
    for (m, wn), (g, wg), (rr, wr), (nc, wc), (T, wt) in itertools.product(zip(NS_M, WN), zip(GS, WG), zip(rs, (0.25, 0.5, 0.25)), zip(NCS, WNC), zip((YRS_LEFT, None), tw)):
        if wt == 0:
            continue
        v.append(val(n0 * m, g, rr, nc, T, cfg)); w.append(wn * wg * wr * wc * wt)
    return v, w


def stats(v, w, disc, px=PX):
    tot = sum(w); post = [x * (1 - disc) for x in v]; q = wpct(post, w); qp = wpct(v, w)
    c = sum(a * b for a, b in zip(v, w)) / tot
    return dict(n=len(v), center_pre=c, center_post=c * (1 - disc), p10_pre=qp[0.1], p50_pre=qp[0.5], p90_pre=qp[0.9],
                p10_post=q[0.1], p50_post=q[0.5], p90_post=q[0.9], pct_w_below_px=weight_below(post, w, px), min_post=min(post), max_post=max(post), disc=disc)


def lab(px, s):
    return 'DUOI' if px < s['p10_post'] else ('TREN' if px > s['p90_post'] else 'TRONG')


def fmt(s, px=PX):
    return (f"n={s['n']} tam {s['center_post']:,.0f} | P10/P50/P90 {s['p10_post']:,.0f}/{s['p50_post']:,.0f}/{s['p90_post']:,.0f} | min {s['min_post']:,.0f}"
            f" | duoi gia {s['pct_w_below_px']:.1%} | gia/tam {px/s['center_post']-1:+.1%} => {lab(px, s)}")


OUT = dict(ticker='SZL', job='Taylor_20261108_164337', asof_price=ASOF, price=PX, r=R, dep_asof=d1, dep_anchor=d0, k_ktpl=K, n0=N0,
           px_szc_szb_0611=px06, px_szc_szb_0411=px04, liq=LQ, d_ref=D_REF, d_40=D_40)
print(f"r = {R:.2%} (dep {d1['rate']:.2%} [{d1['rate_source']}]); gia SZL {PX:,.0f} ({LQ['price_date']}); SZC/SZB 06/11 {px06['SZC']:,.0f}/{px06['SZB']:,.0f} (04/11 {px04['SZC']:,.0f}/{px04['SZB']:,.0f})")
print(f"N0 {N0:.2f}; KTPL k {K:.2%} (15,778/140,687); quy KTPL so du {KFUND:.2f} ({KFUND/SH*1000:,.0f} d/cp); CK 5 ty {D_REF:.2%}, 40 tr {D_40:.2%}")

# ---- 0. Control r2 (gia/thanh khoan 04/11 qua r2lib) ----
Q2 = R2.liq2('SZL')
v, w = grid(R2CFG, r0=0.135)
ctrl = R2.stats(v, w, Q2['price'], Q2['disc_ref'])
print(f"CONTROL r2 tai lap: tam sau {ctrl['center_post']:,.0f} P10/50/90 {ctrl['p10_post']:,.0f}/{ctrl['p50_post']:,.0f}/{ctrl['p90_post']:,.0f} (r2 ghi 32.391 / 28.966/32.162/36.075)")
OUT['control_r2'] = ctrl

# ---- 1. Cau noi r2 -> r3 (tung buoc, tam sau CK 5 ty) ----
steps = [("r2 (control)", R2CFG, Q2['disc_ref']),
         ("+ gia SZC/SZB 06/11", dict(k=0.0, kfund=0.0), Q2['disc_ref']),
         ("+ CK thanh khoan cua so den 06/11", dict(k=0.0, kfund=0.0), D_REF),
         ("+ tru so du quy KTPL 23,96 (ma 323)", dict(k=0.0), D_REF),
         ("+ trich KTPL 11,2% LN loi hang nam (TM18)", {}, D_REF)]
bridge = []; prev = None
for name, cfg, d in steps:
    v, w = grid(cfg); s = stats(v, w, d)
    bridge.append(dict(step=name, center_post=s['center_post'], delta=None if prev is None else s['center_post'] - prev, p10=s['p10_post'], p90=s['p90_post']))
    print(f"CAU NOI {name}: tam {s['center_post']:,.0f}" + ("" if prev is None else f" ({s['center_post']-prev:+,.0f})")); prev = s['center_post']
OUT['bridge_r2_to_r3'] = bridge

# ---- 2. Headline r3 ----
v, w = grid(); S = stats(v, w, D_REF); S40 = stats(v, w, D_40)
OUT['grid'] = S; OUT['grid_sleeve40'] = S40; OUT['label'] = lab(PX, S); OUT['label_sleeve40'] = lab(PX, S40)
print("HEADLINE r3 (5 ty): " + fmt(S)); print("HEADLINE r3 (sleeve 40 tr): " + fmt(S40))
cp27, cpinf = val(T=YRS_LEFT), val()
OUT['center_param_pre'] = dict(T27=cp27, perp=cpinf, mix=0.75 * cp27 + 0.25 * cpinf)
print(f"Gia tri tai tham so trung tam (truoc CK): 27 nam {cp27:,.0f} / vinh vien {cpinf:,.0f}; tron 3/4-1/4 {0.75*cp27+0.25*cpinf:,.0f}")

# ---- 3. Bien the song song / do nhay (cung luoi, 5 ty va 40 tr) ----
var = {"KTPL 0% (= r2 + gia/CK moi + so du quy)": (dict(k=0.0), {}),
       "KTPL 5%": (dict(k=0.05), {}), "KTPL 8%": (dict(k=0.08), {}),
       "thoi han 1/2-1/2 (#2)": ({}, dict(tw=(0.5, 0.5))),
       "chi 27 nam": ({}, dict(tw=(1.0, 0.0))), "chi vinh vien": ({}, dict(tw=(0.0, 1.0))),
       "holdco 10%": (dict(hold=0.10), {}), "holdco 25% (#3)": (dict(hold=0.25), {}),
       "KTPL 5% + holdco 25%": (dict(k=0.05, hold=0.25), {}),
       "capex duy tri 0,5x KH (+45/nam, #4 len)": (dict(dcf=A['sens_capex']['da_ty_per_year'] * 0.5), {}),
       "capex duy tri 1,5x KH (-45/nam, #4 xuong)": (dict(dcf=-A['sens_capex']['da_ty_per_year'] * 0.5), {}),
       "RONIC=Ke (g khong tao gia tri; quy tac chung TOP5C)": (dict(ronic_ke=True), {}),
       "+ BDS dau tu moi 166,9 theo gia von (#5 len)": (dict(add_asset=A['sens_up']['bds_dt_add_ty']), {}),
       "N0 = Q3x4 138,5 (#5 len)": ({}, dict(n0=A['sens_up']['n0_q3x4_ty'])),
       "N0 = 2025 nam hoa 115,3 (#6 xuong)": ({}, dict(n0=115.3)),
       "ky quy DH theo PV den 2053 (#5 len)": (dict(dep_pv=True), {}),
       "SZC/SZB gia 04/11": (dict(px=px04), {})}
par = {}
for name, (cfg, kw) in var.items():
    v, w = grid(cfg, **kw); s = stats(v, w, D_REF); s40 = stats(v, w, D_40)
    par[name] = dict(ref5=s, sleeve40=s40, delta_center=s['center_post'] - S['center_post'])
    print(f"SONG SONG {name}: {fmt(s)} | 40tr P10 {s40['p10_post']:,.0f} => {lab(PX, s40)}")
OUT['parallel'] = par

# ---- 4. Gia ngu y (tam sau CK 5 ty = gia) ----
def solve(f, lo, hi):
    for _ in range(80):
        mid = (lo + hi) / 2
        if (f(mid) - PX) * (f(lo) - PX) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def ctr(cfg=None, **kw):
    v, w = grid(cfg, **kw); return stats(v, w, D_REF)['center_post']


imp = dict(n0_ty=solve(lambda x: ctr(n0=x), 60, 200), k_ktpl=solve(lambda x: ctr(dict(k=x)), 0.0, 0.6),
           holdco=solve(lambda x: ctr(dict(hold=x)), 0.0, 1.0), r=solve(lambda x: ctr(r0=x), 0.10, 0.25))
imp['n0_ktpl0_ty'] = solve(lambda x: ctr(dict(k=0.0), n0=x), 60, 200)
OUT['implied_by_price'] = imp
print(f"GIA NGU Y {PX:,.0f}: N0 {imp['n0_ty']:.1f} ty (base KTPL 11,2%) / {imp['n0_ktpl0_ty']:.1f} (truoc KTPL); hoac KTPL {imp['k_ktpl']:.1%}; hoac holdco {imp['holdco']:.1%}; hoac r {imp['r']:.2%}")

# ---- 5. Cross-check ----
fin_ann = (FIN_REV_9M - FIN_EXP_9M * 0.8) * 4 / 3
OUT['crosscheck'] = dict(gordon_LNST_gom_TC=((N0 + fin_ann) * (0.9 - K) / (R - 0.03) + CIP - OTHER_LIAB - KFUND - NET_DEBT) / SH * 1000,
                         gordon_loi_cong_co_phan=val(), roe_co_TC=(N0 + fin_ann) / EQ,
                         roe_loi=N0 / (EQ - sum(INV_BOOK.values()) - CIP + NET_DEBT + OTHER_LIAB + KFUND))
print("Cross-check (g 3%, nc 10%, KTPL 11,2%, vinh vien): A LNST gom TC {gordon_LNST_gom_TC:,.0f}; B loi + co phan {gordon_loi_cong_co_phan:,.0f}; ROE co TC {roe_co_TC:.1%}; ROE loi {roe_loi:.1%}".format(**OUT['crosscheck']))
sens = {}
for dd in (-0.01, -0.005, 0.005, 0.01):
    sens[f"{int(dd*1e4)}bp"] = ctr(r0=R + dd) / S['center_post'] - 1
OUT['sens_dep_b1'] = sens
print("Do nhay lai huy dong (beta 1, tam): " + "; ".join(f"{k} {v:+.1%}" for k, v in sens.items()))
for wnd in ('adv250', 'adv60'):
    a = LQ[wnd]
    print(f"{wnd}: ADV {a['adv_bn']:.2f} ty ({a['window']}, KL=0 {a['zero_vol_days']} phien), sigma {a['sigma_d']:.2%}; " +
          "; ".join(f"{float(k)*1000:,.0f}tr CK {x['disc']:.2%} Q/ADV {x['q_over_adv']:.1%}{'' if x['in_calib'] else ' NGOAI'}" for k, x in a['sizes'].items()))

json.dump(OUT, open(os.path.join(HERE, 'model_r3_out.json'), 'w'), indent=1, ensure_ascii=False, default=float, sort_keys=True)
files = [os.path.abspath(__file__), os.path.join(HERE, 'assumptions_r3.json'), PXF, os.path.join(HERE, 'snz_holdco_20261106.csv'), os.path.join(HERE, 'szl_cf_hist.csv'),
         os.path.join(ROOT, 'SZL', 'calc', 'bq_oshares_szc_szb.csv'), os.path.join(ROOT, 'SZL', 'calc', 'bq_szc_szb_20261104.csv'), os.path.join(ROOT, 'SZL', 'calc', 'model_r2.py'),
         os.path.join(ROOT, 'SZL', 'src', 'Q3_2026_hopnhat.pdf'), os.path.join(ROOT, 'SZL', 'SUMMARY_r2.json')] + R2.UPSTREAM_COMMON
rows = [f"{hashlib.md5(open(f, 'rb').read()).hexdigest()}  {os.path.relpath(f, ROOT) if f.startswith(ROOT) else f}" for f in sorted(set(files))]
open(os.path.join(HERE, 'LOCK_md5.txt'), 'w').write('\n'.join(rows) + '\n')
for r_ in rows:
    print("LOCK " + r_)
