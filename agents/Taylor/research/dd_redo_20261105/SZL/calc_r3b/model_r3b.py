"""SZL VONG 3b (09/11/2026, job Taylor_20261108_175123). Ap A (RONIC=Ke o base) + B (KTPL tru ca tren gia tri co phan SZC/SZB) — user duyet.
Moi so BCTC/gia/thanh khoan GIONG r3 (chep tu ../calc_r3/model_r3.py, khong import: file do ghi LOCK khi chay). Gia dinh khoa: assumptions_r3b.json.
LOCK: LOCK_r3b_prerun.txt duoc ghi TRUOC khi chay (bin rieng, co timestamp) — model nay KHONG ghi LOCK.
Control: tai lap headline r3 29.257 (ronic_ke=False, kinv=0). Chay: cd calc_r3b && $DNA_PYEXE -I model_r3b.py > model_r3b_out.txt (2 lan, cmp trung byte)."""
import csv, itertools, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
R3 = os.path.join(ROOT, 'SZL', 'calc_r3')
sys.path.insert(0, os.path.join(ROOT, '_shared'))
import numpy as np                     # noqa: E402
from wpct import wpct, weight_below    # noqa: E402
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from deposit_rate_vn import effective_deposit_rate   # noqa: E402

A = json.load(open(os.path.join(HERE, 'assumptions_r3b.json')))
A3 = json.load(open(os.path.join(R3, 'assumptions_r3.json')))
ASOF = A['asof_price']
# ---- so BCTC (giong het r3/r2; src/Q3_2026_hopnhat.pdf) ----
SH = 48.198884
CASH = 171.220813690; DIV_PAY = 70.360021125
LOAN_ST, LOAN_LT = 110.030903581, 196.337026604
CIP = 407.037010429; EQ = 784.151356245
DEP_ST = 10.147281118 + 0.230000000; DEP_LT = 146.987107831
LAND_RENT_ACCR = 44.265169191
INV_BOOK = {"SZC": 221.8, "SZB": 63.0, "An Binh": 24.5, "Binh Thuan": 80.0, "Dich vu": 8.75}
OWN = {"SZC": 0.1008, "SZB": 0.084}
NP_9M = 132.589359502; FIN_REV_9M, FIN_EXP_9M = 37.740263110, 4.326469728
CORE_9M = NP_9M - FIN_REV_9M + FIN_EXP_9M * 0.80
N0 = CORE_9M * 4 / 3
NET_DEBT = LOAN_ST + LOAN_LT - CASH + DIV_PAY
YRS_LEFT = 27
K = A3['ktpl_rate']['num_ty'] / A3['ktpl_rate']['den_ty']
KFUND = A3['ktpl_fund_balance_ty']['value']
d1 = effective_deposit_rate(ASOF); d0 = effective_deposit_rate('2026-11-03')
R = 0.135 + 1.0 * (d1['rate'] - d0['rate'])
PXF = os.path.join(R3, 'px_szl_r3_20261106.csv')
ROWS = sorted(csv.DictReader(open(PXF)), key=lambda r: (r['ticker'], r['time']))
osh = {r['ticker']: float(r['OShares']) for r in csv.DictReader(open(os.path.join(ROOT, 'SZL', 'calc', 'bq_oshares_szc_szb.csv')))}
px06 = {r['ticker']: float(r['Close']) for r in ROWS if r['time'] == ASOF}
SNZ = {r['ticker']: float(r['PB']) for r in csv.DictReader(open(os.path.join(R3, 'snz_holdco_20261106.csv')))}
UNLISTED = sum(v for k, v in INV_BOOK.items() if k not in OWN)
MKT = {k: OWN[k] * osh[k] * px06[k] / 1e9 for k in sorted(OWN)}
TAX = sum(max(MKT[k] - INV_BOOK[k], 0) for k in OWN) * 0.20


def liquidity(tk='SZL'):
    rows = [r for r in ROWS if r['ticker'] == tk]
    assert rows[-1]['time'] == ASOF, rows[-1]['time']
    out = dict(price=float(rows[-1]['Price']), price_date=rows[-1]['time'])
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val_ = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val_))
        sz = {}
        for q in (0.04, 5):
            part = q * 1e9 / adv
            sz[str(q)] = dict(q_bn=q, q_over_adv=part, disc=sig * math.sqrt(part), in_calib=bool(part <= 0.10))
        out[f'adv{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', adv_bn=adv / 1e9, sigma_d=sig, sizes=sz)
    return out


LQ = liquidity(); PX = LQ['price']
D_REF = LQ['adv250']['sizes']['5']['disc']; D_40 = LQ['adv250']['sizes']['0.04']['disc']
BASE = dict(k=K, kfund=KFUND, hold=0.0, hold_unl=0.0, dcf=0.0, ronic_ke=True, kinv=1.0, kunl=0.0, k_on_cf=False, dep_pv=False, add_asset=0.0)
R3CFG = dict(ronic_ke=False, kinv=0.0)


def val(n0=N0, g=0.03, r=R, nc=0.10, T=None, cfg=None):
    c = dict(BASE); c.update(cfg or {})
    k_core = c['k'] * (1 - nc) if c['k_on_cf'] else c['k']          # k_on_cf = quy uoc skeptic (chi de doi chieu 28.052)
    cf = n0 * (1 - nc - k_core) + c['dcf']
    if c['ronic_ke']:
        core = cf / r if T is None else cf * (1 - (1 + r) ** -T) / r
    else:
        core = cf / (r - g) if T is None else cf * (1 - ((1 + g) / (1 + r)) ** T) / (r - g)
    listed = (sum(MKT.values()) - TAX) * (1 - c['hold']) * (1 - c['kinv'] * c['k'])
    unl = UNLISTED * (1 - c['hold_unl']) * (1 - c['kunl'] * c['k'])
    dep_lt = DEP_LT / (1 + r) ** YRS_LEFT if c['dep_pv'] else DEP_LT
    liab = DEP_ST + dep_lt + LAND_RENT_ACCR + c['kfund']
    return (core + listed + unl + CIP + c['add_asset'] - liab - NET_DEBT) / SH * 1000


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


def run(cfg=None, **kw):
    v, w = grid(cfg, **kw); return stats(v, w, D_REF), stats(v, w, D_40)


def fmt(s):
    return (f"tam {s['center_post']:,.0f} | P10/P50/P90 {s['p10_post']:,.0f}/{s['p50_post']:,.0f}/{s['p90_post']:,.0f} | duoi gia {s['pct_w_below_px']:.1%} => {lab(PX, s)}")


OUT = dict(ticker='SZL', round='r3b', job='Taylor_20261108_175123', asof_price=ASOF, price=PX, r=R, dep_asof=d1, k_ktpl=K, n0=N0, liq=LQ, d_ref=D_REF, d_40=D_40,
           stake=dict(mkt_ty=MKT, tax_ty=TAX, net_ty=sum(MKT.values()) - TAX, unlisted_book_ty=UNLISTED))
print(f"r = {R:.2%}; gia SZL {PX:,.0f} ({LQ['price_date']}); N0 {N0:.2f}; k {K:.3%}; CK 5 ty {D_REF:.2%} (Q/ADV250 {LQ['adv250']['sizes']['5']['q_over_adv']:.1%}), 40 tr {D_40:.2%} (Q/ADV250 {LQ['adv250']['sizes']['0.04']['q_over_adv']:.1%})")
print(f"Co phan SZC/SZB thi gia 06/11 {sum(MKT.values()):.1f} ty, thue lai von {TAX:.1f}, rong {sum(MKT.values())-TAX:.1f} ty ({(sum(MKT.values())-TAX)/SH*1000:,.0f} d/cp); KTPL tren phan nay {K*(sum(MKT.values())-TAX):.1f} ty ({K*(sum(MKT.values())-TAX)/SH*1000:,.0f} d/cp truoc CK)")

# ---- 0. Control = headline r3 ----
c5, c40 = run(R3CFG)
print(f"CONTROL r3 tai lap: 5 ty {fmt(c5)} | 40 tr P10 {c40['p10_post']:,.0f} (r3 ghi 29.257 / 26.209/28.963/32.706; 40 tr 30.401 P10 27.234)")
OUT['control_r3'] = dict(ref5=c5, sleeve40=c40)

# ---- 1. Cau noi r3 -> A -> A+B ----
bridge, prev = [], None
for name, cfg in (("r3 (control)", R3CFG), ("+ A: RONIC = Ke", dict(kinv=0.0)), ("+ B: KTPL 11,2% tren co phan SZC/SZB (100%)", {})):
    s, s40 = run(cfg)
    bridge.append(dict(step=name, center_post=s['center_post'], delta=None if prev is None else s['center_post'] - prev, p10=s['p10_post'], p90=s['p90_post'],
                       label_5bn=lab(PX, s), center_40=s40['center_post'], p10_40=s40['p10_post'], p90_40=s40['p90_post'], label_40=lab(PX, s40)))
    print(f"CAU NOI {name}: tam {s['center_post']:,.0f}" + ("" if prev is None else f" ({s['center_post']-prev:+,.0f})") +
          f" P10/P90 {s['p10_post']:,.0f}/{s['p90_post']:,.0f} {lab(PX, s)} | 40tr tam {s40['center_post']:,.0f} P10/P90 {s40['p10_post']:,.0f}/{s40['p90_post']:,.0f} {lab(PX, s40)}")
    prev = s['center_post']
OUT['bridge_r3_to_r3b'] = bridge

# ---- 2. Headline r3b ----
S, S40 = run()
OUT.update(grid_ref5=S, grid_sleeve40=S40, label=lab(PX, S), label_sleeve40=lab(PX, S40))
print("HEADLINE r3b (5 ty):  n=%d %s | gia/tam %+.1f%% | gia/P90 %+.1f%%" % (S['n'], fmt(S), (PX / S['center_post'] - 1) * 100, (PX / S['p90_post'] - 1) * 100))
print("HEADLINE r3b (40 tr): n=%d %s | gia/tam %+.1f%% | gia/P90 %+.1f%%" % (S40['n'], fmt(S40), (PX / S40['center_post'] - 1) * 100, (PX / S40['p90_post'] - 1) * 100))
OUT['center_param_pre'] = dict(T27=val(T=YRS_LEFT), perp=val())

# ---- 3. Do nhay (moi bien the doi 1 truc so voi r3b) ----
hold_snz = 1 - SNZ['SNZ'] / SNZ['SZC']
var = {"chi A (B tat)": (dict(kinv=0.0), {}),
       "chi B (A tat, RONIC ngam vo han)": (dict(ronic_ke=False), {}),
       "B o 50%": (dict(kinv=0.5), {}),
       "KTPL 5% (LN loi + co phan)": (dict(k=0.05), {}), "KTPL 8% (LN loi + co phan)": (dict(k=0.08), {}),
       "N0 = Q3x4 138,5": ({}, dict(n0=A3['sens_up']['n0_q3x4_ty'])),
       "chi nhanh vinh vien": ({}, dict(tw=(0.0, 1.0))), "chi 27 nam": ({}, dict(tw=(1.0, 0.0))), "thoi han 1/2-1/2": ({}, dict(tw=(0.5, 0.5))),
       "B ca co phan chua niem yet": (dict(kunl=1.0), {}),
       "holdco 10% (SZC/SZB)": (dict(hold=0.10), {}), "holdco 25% (SZC/SZB)": (dict(hold=0.25), {}),
       f"holdco ngu y P/B SNZ/SZC {hold_snz:.0%} (can tren tho)": (dict(hold=hold_snz), {}),
       "N0 = 2025 nam hoa 115,3": ({}, dict(n0=115.3)),
       "capex duy tri 0,5x KH (+45/nam)": (dict(dcf=A3['sens_capex']['da_ty_per_year'] * 0.5), {}),
       "capex duy tri 1,5x KH (-45/nam)": (dict(dcf=-A3['sens_capex']['da_ty_per_year'] * 0.5), {}),
       "+ BDS dau tu moi 166,9 theo gia von": (dict(add_asset=A3['sens_up']['bds_dt_add_ty']), {}),
       "ky quy DH theo PV den 2053": (dict(dep_pv=True), {})}
par = {}
for name, (cfg, kw) in var.items():
    s, s40 = run(cfg, **kw)
    par[name] = dict(ref5=s, sleeve40=s40, delta_center=s['center_post'] - S['center_post'])
    print(f"DO NHAY {name}: {fmt(s)} ({s['center_post']-S['center_post']:+,.0f}) | 40tr P10/P90 {s40['p10_post']:,.0f}/{s40['p90_post']:,.0f} => {lab(PX, s40)}")
OUT['parallel'] = par; OUT['hold_snz_implied'] = hold_snz

# ---- 4. Doi chieu skeptic: 28.052 (KTPL + holdco 25%) vs r3 28.507 ----
recon = {"r3: KTPL 5% + holdco 25% (SZC/SZB)": dict(R3CFG, k=0.05, hold=0.25),
         "+ holdco 25% ca co phan chua niem yet": dict(R3CFG, k=0.05, hold=0.25, hold_unl=0.25),
         "+ KTPL tren N0x(1-nc) (quy uoc skeptic)": dict(R3CFG, k=0.05, hold=0.25, k_on_cf=True),
         "ca hai (holdco chua niem yet + KTPL tren N0x(1-nc))": dict(R3CFG, k=0.05, hold=0.25, hold_unl=0.25, k_on_cf=True),
         "KTPL 11,2% + holdco 25% (r3)": dict(R3CFG, hold=0.25),
         "KTPL 11,2% tren N0x(1-nc) + holdco 25% ca chua niem yet": dict(R3CFG, hold=0.25, hold_unl=0.25, k_on_cf=True),
         "skeptic diem 29.510 (KTPL 11,2% tren N0x(1-nc), khong holdco)": dict(R3CFG, k_on_cf=True)}
OUT['skeptic_recon'] = {}
for name, cfg in recon.items():
    s, _ = run(cfg); OUT['skeptic_recon'][name] = s['center_post']
    print(f"DOI CHIEU {name}: tam {s['center_post']:,.0f} (vs 28.052: {s['center_post']-28052:+,.0f})")

# ---- 5. Gia ngu y (tam sau CK 5 ty = gia; va P90 = gia) ----
def solve(f, lo, hi, tgt=PX):
    for _ in range(80):
        mid = (lo + hi) / 2
        if (f(mid) - tgt) * (f(lo) - tgt) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


ctr = lambda cfg=None, **kw: run(cfg, **kw)[0]['center_post']   # noqa: E731
imp = dict(n0_ty=solve(lambda x: ctr(n0=x), 60, 250), k_ktpl=solve(lambda x: ctr(dict(k=x)), -0.5, 0.6),
           r=solve(lambda x: ctr(r0=x), 0.08, 0.25), dcf_ty=solve(lambda x: ctr(dict(dcf=x)), -100, 200))
imp['n0_ktpl0_ty'] = solve(lambda x: ctr(dict(k=0.0), n0=x), 60, 250)
imp['n0_for_p90_5bn_eq_px'] = solve(lambda x: run(n0=x)[0]['p90_post'], 60, 250)
imp['n0_for_p90_40_eq_px'] = solve(lambda x: run(n0=x)[1]['p90_post'], 60, 250)
OUT['implied_by_price'] = imp
print(f"GIA NGU Y {PX:,.0f} (tam 5 ty): N0 {imp['n0_ty']:.1f} ty (KTPL 11,2%) / {imp['n0_ktpl0_ty']:.1f} (KTPL 0%); hoac KTPL {imp['k_ktpl']:.1%}; hoac r {imp['r']:.2%}; hoac dong tien them {imp['dcf_ty']:+.1f} ty/nam")
print(f"P90 = gia khi N0 = {imp['n0_for_p90_5bn_eq_px']:.1f} ty (5 ty) / {imp['n0_for_p90_40_eq_px']:.1f} ty (40 tr)")
sens = {f"{int(dd*1e4)}bp": ctr(r0=R + dd) / S['center_post'] - 1 for dd in (-0.01, 0.01)}
OUT['sens_dep_b1'] = sens
print("Do nhay lai huy dong (beta 1, tam): " + "; ".join(f"{k} {v:+.1%}" for k, v in sens.items()))
json.dump(OUT, open(os.path.join(HERE, 'model_r3b_out.json'), 'w'), indent=1, ensure_ascii=False, default=float, sort_keys=True)
