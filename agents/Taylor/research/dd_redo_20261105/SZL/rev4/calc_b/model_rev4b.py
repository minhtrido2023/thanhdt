"""SZL REV4 (23/11/2026, job Taylor_20261123_003503 / resume Taylor_20261123_050009) — xu ly skeptic DD_GENERAL r1 (INCONCLUSIVE).
Ke thua model r3c (restored/calc_r3c/model_r3c.py chep tu git fc5bd02d9 -> ../../calc_r3c/model_r3c.py). Thay doi (assumptions_rev4b.json):
 (1) BDS dau tu moi 166,9 -> truc {0; 166,9-DC; 166,9} (0,25/0,5/0,25), DC = phan LN da nam trong N0 (uoc luong 78,7)
 (2) ky quy DH 147 -> truc {menh gia; PV@lai huy dong; PV@r} (0,25/0,5/0,25)
 (3) N0 -> truc muc {N0_9M; N0_cycle GPM TB 2017-24} (0,5/0,5) x he so -12..+12%
 (4) CP tai chinh loai 100% (r3c 0,8) doi xung DT tai chinh
Doc file tu ../restored (khoi phuc tu git). Chay: $DNA_PYEXE -I model_rev4.py > model_rev4_out.txt (2 lan, cmp)."""
import csv, itertools, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
RS = os.path.join(HERE, '..', 'restored')
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', '..', '_shared')))
import numpy as np                     # noqa: E402
from wpct import wpct, weight_below    # noqa: E402
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
from deposit_rate_vn import effective_deposit_rate   # noqa: E402

A4 = json.load(open(os.path.join(HERE, 'assumptions_rev4b.json')))
A3 = json.load(open(os.path.join(RS, 'calc_r3', 'assumptions_r3.json')))
ASOF = '2026-11-06'
# ---- so BCTC Q3/2026 (giong r3c) ----
SH = 48.198884
CASH = 171.220813690; DIV_PAY = 70.360021125
LOAN_ST, LOAN_LT = 110.030903581, 196.337026604
CIP = 407.037010429
DEP_ST = 10.147281118 + 0.230000000; DEP_LT = A4['deposit_lt']['face_ty']
LAND_RENT_ACCR = A4['land_rent_44_3']['value_ty']
LAND_RENT_YR = A4['land_rent_annual']['value_9m_ty']   # rev4-postfix: phat sinh H1 = 9T = 13,74 => ghi nhan 1 lan/nam, KHONG x4/3
INV_BOOK = {"SZC": 221.8, "SZB": 63.0, "An Binh": 24.5, "Binh Thuan": 80.0, "Dich vu": 8.75}
OWN = {"SZC": 0.1008, "SZB": 0.084}
NP_9M = 132.589359502; FIN_REV_9M, FIN_EXP_9M = 37.740263110, 4.326469728
NQ76_YR = 5.845686000   # TM17: phan bo LN giu lai NQ 76/2020 (157,834 -> 151,988 trong 9T), ghi 1 lan/nam, phi tien mat
CORE_9M = NP_9M - FIN_REV_9M + FIN_EXP_9M * 0.80   # rev4b: tro lai x0,8 (DT TC = co tuc mien thue; lai vay co la chan thue)
N0_9M_RAW = CORE_9M * 4 / 3
N0_9M = N0_9M_RAW - NQ76_YR * 4 / 3 * 0.8   # rev4b: bo LN phi tien mat NQ76 (gia dinh chiu thue 20%)
N0_R3C = (NP_9M - FIN_REV_9M + FIN_EXP_9M * 0.80) * 4 / 3
# ---- N0 chuan hoa bien chu ky (BQ) ----
G = list(csv.DictReader(open(os.path.join(HERE, 'szl_gpm_hist_20261123.csv'))))
cyc = [float(r['GPM_P0']) for r in G if '2017Q1' <= r['quarter'] <= '2024Q4']
GPM_CYC = sum(cyc) / len(cyc)
q9 = [r for r in G if r['quarter'] in ('2026Q1', '2026Q2', '2026Q3')]
REV_9M = sum(float(r['Revenue_P0']) for r in q9) / 1e9
GPM_9M = sum(float(r['Revenue_P0']) * float(r['GPM_P0']) for r in q9) / 1e9 / REV_9M
N0_CYC = N0_9M - REV_9M * (GPM_9M - GPM_CYC) * 0.8 * 4 / 3
N0_LEVELS = ((N0_9M, 0.5), (N0_CYC, 0.5))
# ---- BDS DT moi ----
BDS_COST = A4['bds_dt_new']['cost_ty']
DC = 101.7 * 6 / 9 + 65.2 * 1.5 / 9
BDS_AX = ((0.0, 0.25), (BDS_COST - DC, 0.5), (BDS_COST, 0.25))
NET_DEBT = LOAN_ST + LOAN_LT - CASH + DIV_PAY
YRS_LEFT = 27
K = A3['ktpl_rate']['num_ty'] / A3['ktpl_rate']['den_ty']
KFUND = A3['ktpl_fund_balance_ty']['value']
d1 = effective_deposit_rate(ASOF); d0 = effective_deposit_rate('2026-11-03')
R = 0.135 + 1.0 * (d1['rate'] - d0['rate'])
RDEP = d1['rate']
ROWS = sorted(csv.DictReader(open(os.path.join(RS, 'calc_r3', 'px_szl_r3_20261106.csv'))), key=lambda r: (r['ticker'], r['time']))
osh = {r['ticker']: float(r['OShares']) for r in csv.DictReader(open(os.path.join(RS, 'calc', 'bq_oshares_szc_szb.csv')))}
px06 = {r['ticker']: float(r['Close']) for r in ROWS if r['time'] == ASOF}
SNZ = {r['ticker']: float(r['PB']) for r in csv.DictReader(open(os.path.join(RS, 'calc_r3', 'snz_holdco_20261106.csv')))}
UNLISTED = sum(v for k, v in INV_BOOK.items() if k not in OWN)
MKT = {k: OWN[k] * osh[k] * px06[k] / 1e9 for k in sorted(OWN)}
MKT_T = sum(MKT.values())
GAIN = sum(max(MKT[k] - INV_BOOK[k], 0) for k in OWN)
TAX = GAIN * 0.20


def liquidity(tk='SZL'):
    rows = [r for r in ROWS if r['ticker'] == tk]
    assert rows[-1]['time'] == ASOF, rows[-1]['time']
    out = dict(price=float(rows[-1]['Price']), price_date=rows[-1]['time'])
    d = rows[-251:]
    c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
    val_ = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val_))
    out['adv250'] = dict(adv_bn=adv / 1e9, sigma_d=sig, sizes={str(q): dict(q_over_adv=q * 1e9 / adv, disc=sig * math.sqrt(q * 1e9 / adv)) for q in (0.04, 5)})
    return out


LQ = liquidity(); PX = LQ['price']
D_REF = LQ['adv250']['sizes']['5']['disc']; D_40 = LQ['adv250']['sizes']['0.04']['disc']
BASE = dict(k=K, kfund=KFUND, hold=0.0, dcf=0.0, kinv=1.0, add_extra=0.0)


def stake(c):
    k = c['kinv'] * c['k']
    return MKT_T - TAX - k * (GAIN - TAX)


def dep_val(mode, r):
    if mode == 'face':
        return DEP_LT
    rr = RDEP if mode == 'pv_dep' else r
    return DEP_LT / (1 + rr) ** YRS_LEFT


def val(n0, g, r, nc, T, bds, dep, cfg=None):
    c = dict(BASE); c.update(cfg or {})
    cf = n0 * (1 - nc - c['k']) + c['dcf']
    core = cf / r if T is None else cf * (1 - (1 + r) ** -T) / r     # RONIC = Ke (giu r3b/r3c)
    listed = stake(c) * (1 - c['hold'])
    liab = DEP_ST + dep_val(dep, r) + LAND_RENT_ACCR + c['kfund']
    return (core + listed + UNLISTED + CIP + bds + c['add_extra'] - liab - NET_DEBT) / SH * 1000


NS_M = (0.88, 0.94, 1.0, 1.06, 1.12); WN = (0.1, 0.2, 0.4, 0.2, 0.1)
GS = (0.02, 0.03, 0.04); WG = (0.25, 0.5, 0.25)
NCS = (0.20, 0.10, 0.0); WNC = (0.25, 0.5, 0.25)
DEP_AX = (('face', 0.5), ('pv_dep', 0.5))   # rev4b: trong so trung lap


def grid(cfg=None, tw=(0.75, 0.25), n0lv=N0_LEVELS, bds_ax=BDS_AX, dep_ax=DEP_AX, r0=R):
    v, w = [], []
    rs = (r0 - 0.01, r0, r0 + 0.01)
    for (n0, wl), (m, wn), (g, wg), (rr, wr), (nc, wc), (T, wt), (b, wb), (dp, wd) in itertools.product(
            n0lv, zip(NS_M, WN), zip(GS, WG), zip(rs, (0.25, 0.5, 0.25)), zip(NCS, WNC), zip((YRS_LEFT, None), tw), bds_ax, dep_ax):
        if wt == 0 or wl == 0 or wb == 0 or wd == 0:
            continue
        v.append(val(n0 * m, g, rr, nc, T, b, dp, cfg)); w.append(wl * wn * wg * wr * wc * wt * wb * wd)
    return v, w


def stats(v, w, disc, px=PX):
    tot = sum(w); post = [x * (1 - disc) for x in v]; q = wpct(post, w); qp = wpct(v, w)
    c = sum(a * b for a, b in zip(v, w)) / tot
    return dict(n=len(v), center_pre=c, center_post=c * (1 - disc), p10_pre=qp[0.1], p50_pre=qp[0.5], p90_pre=qp[0.9],
                p10_post=q[0.1], p50_post=q[0.5], p90_post=q[0.9], pct_w_below_px=weight_below(post, w, px), disc=disc)


def lab(px, s):
    return 'DUOI' if px < s['p10_post'] else ('TREN' if px > s['p90_post'] else 'TRONG')


def run(cfg=None, **kw):
    v, w = grid(cfg, **kw); return stats(v, w, D_REF), stats(v, w, D_40)


def fmt(s):
    return f"tam {s['center_post']:,.0f} | P10/P50/P90 {s['p10_post']:,.0f}/{s['p50_post']:,.0f}/{s['p90_post']:,.0f} | duoi gia {s['pct_w_below_px']:.1%} => {lab(PX, s)}"


OUT = dict(ticker='SZL', round='rev4b', asof_price=ASOF, price=PX, r=R, r_dep=RDEP, k_ktpl=K, n0_9m=N0_9M, n0_r3c=N0_R3C, n0_cycle=N0_CYC,
           gpm_cycle=GPM_CYC, gpm_9m=GPM_9M, rev_9m=REV_9M, bds_cost=BDS_COST, bds_dc=DC, dep_lt_face=DEP_LT,
           dep_lt_pv_dep=dep_val('pv_dep', R), dep_lt_pv_r=dep_val('pv_r', R), land_rent_yr=LAND_RENT_YR, d_ref=D_REF, d_40=D_40, liq=LQ)
print(f"r {R:.2%}; lai huy dong 12T {RDEP:.2%}; gia {PX:,.0f} ({LQ['price_date']}); k {K:.3%}; CK 5 ty {D_REF:.2%} / 40 tr {D_40:.2%}")
print(f"N0_9M_RAW {N0_9M_RAW:.2f} (= r3c {N0_R3C:.2f}) - NQ76 => N0_9M {N0_9M:.2f}; GPM 9M {GPM_9M:.2%} vs TB 2017-24 {GPM_CYC:.2%} (n={len(cyc)}); DT 9M {REV_9M:.1f} => N0_cycle {N0_CYC:.2f}")
print(f"BDS DT moi {BDS_COST:.1f}, DC {DC:.1f} => truc 0/{BDS_COST-DC:.1f}/{BDS_COST:.1f}; ky quy DH menh gia {DEP_LT:.1f} / PV@{RDEP:.2%} {dep_val('pv_dep', R):.1f} / PV@r {dep_val('pv_r', R):.1f}")

# ---- 0. Control: tai lap r3c 25.165 (truc moi ve dung lua chon r3c) ----
R3C_KW = dict(n0lv=((N0_R3C, 1.0),), bds_ax=((0.0, 1.0),), dep_ax=(('face', 1.0),))
c5, c40 = run(**R3C_KW)
print(f"CONTROL r3c: 5 ty {fmt(c5)} | 40 tr {fmt(c40)}  (r3c ghi 25.165 / 22.936/25.008/27.710; 40 tr 26.148)")
OUT['control_r3c'] = dict(ref5=c5, sleeve40=c40)

# ---- 1. Cau noi r3c -> rev4 (them tung buoc) ----
steps = [("r3c (control)", R3C_KW),
         ("+ truc BDS DT moi", dict(n0lv=((N0_R3C, 1.0),), dep_ax=(('face', 1.0),))),
         ("+ truc ky quy DH 0,5 menh gia/0,5 PV@lai huy dong", dict(n0lv=((N0_R3C, 1.0),))),
         ("+ bo LN phi tien mat NQ76", dict(n0lv=((N0_9M, 1.0),))),
         ("+ truc N0 chuan hoa bien (= rev4b base)", {})]
bridge, prev = [], None
for nm, kw in steps:
    s, s40 = run(**kw)
    bridge.append(dict(step=nm, center=s['center_post'], delta=None if prev is None else s['center_post'] - prev, p10=s['p10_post'], p50=s['p50_post'], p90=s['p90_post'],
                       label_5bn=lab(PX, s), center_40=s40['center_post'], p10_40=s40['p10_post'], p90_40=s40['p90_post'], pct_below_40=s40['pct_w_below_px'], label_40=lab(PX, s40)))
    print(f"CAU NOI {nm}: 5 ty {fmt(s)}" + ("" if prev is None else f" ({s['center_post']-prev:+,.0f})") + f" | 40 tr {fmt(s40)}")
    prev = s['center_post']
OUT['bridge'] = bridge

# ---- 2. Headline ----
S, S40 = run()
OUT.update(grid_ref5=S, grid_sleeve40=S40, label=lab(PX, S), label_sleeve40=lab(PX, S40))
print(f"HEADLINE rev4b (5 ty):  n={S['n']} {fmt(S)} | gia/tam {(PX/S['center_post']-1)*100:+.1f}%")
print(f"HEADLINE rev4b (40 tr): n={S40['n']} {fmt(S40)} | gia/tam {(PX/S40['center_post']-1)*100:+.1f}%")

# ---- 3. Do nhay (1 truc) ----
var = {"N0 chi 9T (bien hien tai)": ({}, dict(n0lv=((N0_9M, 1.0),))),
       "N0 chi bien chu ky": ({}, dict(n0lv=((N0_CYC, 1.0),))),
       "BDS DT moi = 0 (da het trong N0)": ({}, dict(bds_ax=((0.0, 1.0),))),
       "BDS DT moi = gia von du": ({}, dict(bds_ax=((BDS_COST, 1.0),))),
       "ky quy DH menh gia": ({}, dict(dep_ax=(('face', 1.0),))),
       "ky quy DH PV@lai huy dong": ({}, dict(dep_ax=(('pv_dep', 1.0),))),
       "ky quy DH 0,25/0,5/0,25 kem PV@r (rev4)": ({}, dict(dep_ax=(('face', 0.25), ('pv_dep', 0.5), ('pv_r', 0.25)))),
       "thue dat hang nam +25% (sau thue)": (dict(dcf=-LAND_RENT_YR * 0.25 * 0.8), {}),
       "thue dat hang nam +50% (sau thue)": (dict(dcf=-LAND_RENT_YR * 0.50 * 0.8), {}),
       "thue dat hang nam x2 (sau thue)": (dict(dcf=-LAND_RENT_YR * 1.0 * 0.8), {}),
       "thue dat ghi 1 lan/nam => bo x4/3 (+13,74/3 truoc thue)": ({}, dict(n0lv=((N0_9M + LAND_RENT_YR / 3 * 0.8, 0.5), (N0_CYC + LAND_RENT_YR / 3 * 0.8, 0.5)))),
       "NQ76 khong chiu thue": ({}, dict(n0lv=((N0_9M - NQ76_YR * 4 / 3 * 0.2, 0.5), (N0_CYC - NQ76_YR * 4 / 3 * 0.2, 0.5)))),
       "Long Phuoc vuot von 20% phan con lai (-102,6)": (dict(add_extra=-0.2 * 513), {}),
       "holdco 10% (SZC/SZB)": (dict(hold=0.10), {}), "holdco 25% (SZC/SZB)": (dict(hold=0.25), {}),
       "KTPL 8%": (dict(k=0.08), {}), "KTPL 5%": (dict(k=0.05), {}),
       "capex duy tri 0,5x KH (+45/nam)": (dict(dcf=45.0), {}), "capex duy tri 1,5x KH (-45/nam)": (dict(dcf=-45.0), {}),
       "chi 27 nam": ({}, dict(tw=(1.0, 0.0))), "chi vinh vien": ({}, dict(tw=(0.0, 1.0)))}
par = {}
for nm, (cfg, kw) in var.items():
    s, s40 = run(cfg, **kw)
    par[nm] = dict(ref5=s, sleeve40=s40, delta_center=s['center_post'] - S['center_post'])
    print(f"DO NHAY {nm}: 5 ty tam {s['center_post']:,.0f} ({s['center_post']-S['center_post']:+,.0f}) {lab(PX, s)} | 40 tr {fmt(s40)}")
OUT['parallel'] = par


def solve(f, lo, hi, tgt=PX):
    for _ in range(60):
        mid = (lo + hi) / 2
        if (f(mid) - tgt) * (f(lo) - tgt) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


thr = dict(dcf_p90_40=solve(lambda x: run(dict(dcf=x))[1]['p90_post'], -150, 200), dcf_p10_40=solve(lambda x: run(dict(dcf=x))[1]['p10_post'], -150, 300),
           hold_p90_40=solve(lambda x: run(dict(hold=x))[1]['p90_post'], -0.5, 0.95), k_p90_40=solve(lambda x: run(dict(k=x))[1]['p90_post'], -0.5, 0.95),
           r_center=solve(lambda x: run(r0=x)[0]['center_post'], 0.06, 0.25))
OUT['thresholds'] = thr
print(f"NGUONG 40 tr: TREN neu dong tien them < {thr['dcf_p90_40']:+.1f} ty/nam, DUOI neu > {thr['dcf_p10_40']:+.1f}; holdco TREN > {thr['hold_p90_40']:.1%}; KTPL TREN > {thr['k_p90_40']:.1%}; r de tam 5 ty = gia: {thr['r_center']:.2%}")
sens = {f"{int(dd*1e4)}bp": run(r0=R + dd)[0]['center_post'] / S['center_post'] - 1 for dd in (-0.01, 0.01)}
OUT['sens_dep_b1'] = sens
print("Do nhay lai huy dong (beta 1, r): " + "; ".join(f"{k} {v:+.1%}" for k, v in sens.items()))
json.dump(OUT, open(os.path.join(HERE, 'model_rev4b_out.json'), 'w'), indent=1, ensure_ascii=False, default=float, sort_keys=True)
