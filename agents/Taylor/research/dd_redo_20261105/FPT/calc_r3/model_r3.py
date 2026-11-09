"""DD REDO VONG 3 FPT (job Taylor_20261108_180128) — ap dinh chinh fundamental-skeptic (TOP5D_CORRECTIONS_20261108.md muc FPT).
Mo hinh = FPT/calc/fpt_r2.py (hang so BCTC chep nguyen van dong 13-24, khong import vi fpt_r2.py ghi SUMMARY khi chay).
Cong tac cau hinh: W (r2|sym), RONIC terminal (r2|ke), NCI (tru 1.165,8 ty), FTEL CK (scen|0), gia FOX/FRT (0411|0611), chan RONIC 5 nam, lai LK Q4/25.
Gia 06/11 = BQ (px_fpt_r3.sql -> px_fpt_r3_20261106.csv). Chay: python3 -I model_r3.py (2 lan, so md5)."""
import os, sys, json, csv, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '_common_014125')); sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude')
import numpy as np
import r2common as R2C
from deposit_rate_vn import effective_deposit_rate

TK = 'FPT'; ASOF = '2026-11-06'; ANCHOR_DATE = '2026-11-03'; R_ANCHOR = 0.135
SH = 1885.727648
cash, htm, htm_l, st_debt, lt_debt = 7377.3, 21449.7, 2.5, 14316.5, 2280.0
NC = cash + htm + htm_l - st_debt - lt_debt
pat9, assoc9 = 7776.4, 2220.3
Q4_25_PAT = 2509.5
NET_INT9 = 1283 - 612
OTHER_ASSOC_BOOK = 1500.0
INV_OTHER = 494.4 + 451.1
CIP_EDU = 415 + 247 + 61 + 37
FTEL_PCT, FRT_PCT = 0.4566, 0.4654
NCI = 1165.791218519                 # ma 429 [notes_q3_bctc.md:85]
ADV_CUST = 2370.0                    # tien khach ung truoc (do nhay, so r2)

px_rows = list(csv.DictReader(open(os.path.join(HERE, 'px_fpt_r3_20261106.csv'))))
def assoc_val(date):
    a = {r['ticker']: r for r in px_rows if r['time'] == date}
    return (float(a['FOX']['Price']) * float(a['FOX']['OShares']) / 1e9 * FTEL_PCT, float(a['FRT']['Price']) * float(a['FRT']['OShares']) / 1e9 * FRT_PCT)
ASSOC = {'0411': assoc_val('2026-11-04'), '0611': assoc_val('2026-11-06')}
r2csv = {r['ticker']: r for r in csv.DictReader(open(os.path.join(ROOT, 'FPT', 'calc', 'assoc_px_20261104.csv'))) if r['time'] == '2026-11-04'}
assert abs(ASSOC['0411'][0] - float(r2csv['FOX']['Price']) * float(r2csv['FOX']['OShares']) / 1e9 * FTEL_PCT) < 1e-6

SC = {'XAU': (0.03, 0.40, 0.030, 0.30), 'CO_SO': (0.09, 0.75, 0.040, 0.15), 'TOT': (0.14, 0.85, 0.040, 0.00)}
W = {'r2': {'XAU': 0.35, 'CO_SO': 0.45, 'TOT': 0.20}, 'sym': {'XAU': 0.275, 'CO_SO': 0.45, 'TOT': 0.275}}
FRT_AX = ((0.20, 0.25), (0.0, 0.50), (-0.20, 0.25))
OTH_AX = ((-1300, 0.20), (0, 0.30), (1100, 0.30), (2600, 0.20))
DCV = (-0.20, -0.10, 0.0, 0.10, 0.20); DG = (-0.01, 0.0, 0.01)
d0 = effective_deposit_rate(ANCHOR_DATE); d1 = effective_deposit_rate(ASOF)
R = R_ANCHOR + 1.0 * (d1['rate'] - d0['rate'])
BASE_CFG = dict(w='sym', ronic='ke', nci=True, ftel='zero', px='0611', cap=None, q4a=600.0, adv=False)


def core_op(q4a):
    return (pat9 - assoc9) + (Q4_25_PAT - q4a) - NET_INT9 * 4 / 3 * 0.85


def dcf(base, g1, conv, gT, ke, ronic, n=5):
    pv, e = 0.0, base
    for t in range(1, n + 1):
        e *= 1 + g1; pv += e * conv / (1 + ke) ** t
    convT = conv if ronic == 'r2' else 1 - gT / ke
    tv = e * (1 + gT) * convT / (ke - gT)
    return pv + tv / (1 + ke) ** n


def make_fn(cfg):
    fox, frt = ASSOC[cfg['px']]
    co = core_op(cfg['q4a'])
    def fn(r, scen, dconv, dg, frt_d, oth):
        g1, cv, gT, fd = SC[scen]
        c = cv + dconv
        if cfg['cap'] is not None: c = min(c, 1 - g1 / cfg['cap'])
        v = dcf(co, g1, max(c, 0.10), gT + dg, r, cfg['ronic'])
        fdisc = fd if cfg['ftel'] == 'scen' else 0.0
        tot = v + fox * (1 - fdisc) + frt * (1 + frt_d) + OTHER_ASSOC_BOOK + INV_OTHER + CIP_EDU + NC - (NCI if cfg['nci'] else 0) - (ADV_CUST if cfg['adv'] else 0)
        return tot / SH * 1e3 + oth
    return fn


def axes(cfg, wov=None):
    ww = wov or W[cfg['w']]
    return [('scen', [(n, ww[n]) for n in SC]), ('dconv', [(x, 1 / 5) for x in DCV]), ('dg', [(x, 1 / 3) for x in DG]),
            ('frt_d', list(FRT_AX)), ('oth', list(OTH_AX))]


def liq(pxdate):
    rows = sorted((r for r in px_rows if r['ticker'] == TK and r['time'] <= pxdate), key=lambda r: r['time'])
    out = {}
    for n in (250, 60):
        d = rows[-n - 1:]
        c = np.array([float(r['Close']) for r in d]); p = np.array([float(r['Price']) for r in d]); v = np.array([float(r['Volume']) for r in d])
        val = (p * v)[1:]; sig = float(np.std(np.diff(np.log(c)), ddof=1)); adv = float(np.median(val))
        out[f'adv{n}'] = dict(window=f'{d[1]["time"]}..{d[-1]["time"]}', n=len(val), adv_med=adv, sigma_d=sig,
                              disc={f'{q:.0f}': sig * math.sqrt(q / adv) for q in (5e9, 40e6, 10e6)}, part={f'{q:.0f}': q / adv for q in (5e9, 40e6, 10e6)})
    out['d_ref'] = out['adv250']['disc']['5000000000']; out['d_ref_adv60'] = out['adv60']['disc']['5000000000']
    out['d_40tr'] = out['adv250']['disc']['40000000']; out['d_10tr'] = out['adv250']['disc']['10000000']
    out['px'] = float(rows[-1]['Price']); out['pxd'] = rows[-1]['time']
    return out


def run(cfg, px, d, r=R, wov=None):
    f = make_fn(cfg); res = R2C.outcomes(axes(cfg, wov), lambda **kw: f(r, **kw))
    return R2C.stats(res, px, d), res


r2cfg = dict(w='r2', ronic='r2', nci=False, ftel='scen', px='0411', cap=None, q4a=600.0, adv=False)
L2 = R2C.liq2(TK)
ctrl, _ = run(r2cfg, 53900.0, L2['d_ref'])
L = liq(ASOF); PX, PXD, D = L['px'], L['pxd'], L['d_ref']
print(f"== FPT VONG 3 | gia {PX:,.0f} ({PXD}, BQ) | r {R:.2%} (dep12T {d1['rate']:.2%} {d1['rate_source']}; neo {d0['rate']:.2%})")
print(f"FOX 06/11 {ASSOC['0611'][0]:,.0f} ty (04/11 {ASSOC['0411'][0]:,.0f}) | FRT 06/11 {ASSOC['0611'][1]:,.0f} ty (04/11 {ASSOC['0411'][1]:,.0f})")
print(f"CK 5 ty: r2 {L2['d_ref']:.4%} | r3 {D:.4%} (ADV250 {L['adv250']['adv_med']/1e9:,.1f} ty; ADV60 {L['adv60']['adv_med']/1e9:,.1f} ty, CK ADV60 {L['d_ref_adv60']:.4%}) | 40tr {L['d_40tr']:.4%} 10tr {L['d_10tr']:.4%}")
print("CONTROL r2 tai lap (04/11):", R2C.fmt(ctrl))

steps = [('1 gia FPT/FOX/FRT + thanh khoan 06/11', dict(r2cfg, px='0611')),
         ('2 D1 trong so doi xung 0,275/0,45/0,275', dict(r2cfg, px='0611', w='sym')),
         ('3 D2 RONIC terminal = Ke ca 3 kich ban', dict(r2cfg, px='0611', w='sym', ronic='ke')),
         ('4 D3 tru loi ich CDKKS 1.165,8 ty', dict(r2cfg, px='0611', w='sym', ronic='ke', nci=True)),
         ('5 D7 CK FTEL [UL] -> base 0%', dict(BASE_CFG))]
bridge = [dict(step='0 r2 tai lap (gia 04/11)', center=round(ctrl['center']), delta=0, p10=round(ctrl['p10']), p90=round(ctrl['p90']), pct_below_px=round(ctrl['pct_below_px'], 4))]
prev = ctrl['center']
for nm, cfg in steps:
    s, _ = run(cfg, PX, D)
    bridge.append(dict(step=nm, center=round(s['center']), delta=round(s['center'] - prev), p10=round(s['p10']), p90=round(s['p90']), pct_below_px=round(s['pct_below_px'], 4))); prev = s['center']
    print(f"BRIDGE {nm}: tam {s['center']:,.0f} ({bridge[-1]['delta']:+,}) P10 {s['p10']:,.0f} P90 {s['p90']:,.0f} %duoi {s['pct_below_px']:.1%}")
r2_newpx, _ = run(r2cfg, PX, L2['d_ref']); print(f"r2 o gia 06/11 (chi doi so sanh gia): %duoi gia {r2_newpx['pct_below_px']:.1%}")

main, res = run(BASE_CFG, PX, D); pre, _ = run(BASE_CFG, PX, 0.0)
s40, _ = run(BASE_CFG, PX, L['d_40tr'])
R2C.write_grid(os.path.join(HERE, 'grid_fpt_r3.csv'), res)
FH = make_fn(BASE_CFG)
central = FH(R, scen='CO_SO', dconv=0, dg=0, frt_d=0, oth=0) * (1 - D)
print("HEADLINE r3 (sau CK 5 ty):", R2C.fmt(main)); print("Truoc CK:", R2C.fmt(pre)); print("Sleeve 40tr:", R2C.fmt(s40))
print(f"Gia tri tai tham so trung tam sau CK 5 ty: {central:,.0f}")
for sc in SC: print(f"  {sc}: r3 {FH(R, scen=sc, dconv=0, dg=0, frt_d=0, oth=0):,.0f} | r2-style {make_fn(dict(r2cfg, px='0611'))(R, scen=sc, dconv=0, dg=0, frt_d=0, oth=0):,.0f} (truoc CK)")
v = np.array([x[1] for x in res]) * (1 - D); w = np.array([x[2] for x in res])
def near(q):
    m = np.abs(v - q) <= 0.05 * abs(q); tw = w[m].sum(); out = {}
    for (kw, _, ww), mm in zip(res, m):
        if mm: out[kw['scen']] = out.get(kw['scen'], 0) + ww / tw
    return {k: round(float(x), 3) for k, x in sorted(out.items())}
drivers = dict(p10_scen_mix_pm5pct=near(main['p10']), p90_scen_mix_pm5pct=near(main['p90'])); print("Nhom kich ban quanh P10/P90:", drivers)

alts = {
 'A_giu_CK_FTEL_30/15/0': dict(BASE_CFG, ftel='scen'),
 'B_trong_so_r2_0,35/0,45/0,20': dict(BASE_CFG, w='r2'),
 'C_RONIC_terminal_r2_(>Ke)': dict(BASE_CFG, ronic='r2'),
 'D_khong_tru_CDKKS': dict(BASE_CFG, nci=False),
 'E_RONIC_5nam_chan_25,5%_(ROE_TTM)': dict(BASE_CFG, cap=0.255),
 'F_RONIC_5nam_chan_17,7%_(ROIC5Y)': dict(BASE_CFG, cap=0.177),
 'G_RONIC_5nam_chan_Ke': dict(BASE_CFG, cap=R),
 'H_lai_LK_Q4/25_740': dict(BASE_CFG, q4a=740.0),
 'I_tru_tien_khach_ung_truoc_2.370': dict(BASE_CFG, adv=True),
 'J_FOX/FRT_gia_04/11': dict(BASE_CFG, px='0411'),
 'K_ban_skeptic_(giu_CK_FTEL,_E1-E4)': dict(BASE_CFG, ftel='scen'),
}
alt_out = {}
for k, cfg in alts.items():
    if k.startswith('K_'): continue
    s, _ = run(cfg, PX, D); alt_out[k] = s; print(f"SONG SONG {k}:", R2C.fmt(s))
f_ = make_fn(BASE_CFG); rax = [(R - 0.01, 0.25), (R, 0.50), (R + 0.01, 0.25)]
s_r = R2C.stats(R2C.outcomes(axes(BASE_CFG) + [('r', rax)], lambda r, **kw: f_(r, **kw)), PX, D); alt_out['co_truc_r_pm1pp'] = s_r
print("SONG SONG co_truc_r_pm1pp:", R2C.fmt(s_r))
sens_r = {f'{dr*1e4:+.0f}bp': round(run(BASE_CFG, PX, D, r=R + dr)[0]['center']) for dr in (-0.01, -0.005, 0.005, 0.01)}; print("Do nhay r (tam):", sens_r)


def solve(f, lo, hi):
    up = f(hi) > f(lo)
    for _ in range(60):
        m = (lo + hi) / 2
        if (f(m) > PX) != up: lo = m
        else: hi = m
    return m
r_imp = solve(lambda rr: run(BASE_CFG, PX, D, r=rr)[0]['center'], 0.10, 0.30)
wx_imp = solve(lambda x: run(BASE_CFG, PX, D, wov={'XAU': x, 'CO_SO': 0.45, 'TOT': 0.55 - x})[0]['center'], 0.0, 0.55)
cap_imp = solve(lambda c: run(dict(BASE_CFG, cap=c), PX, D)[0]['center'], 0.05, 0.60)
r_imp_A = solve(lambda rr: run(dict(BASE_CFG, ftel='scen'), PX, D, r=rr)[0]['center'], 0.10, 0.30)
print(f"GIA NGU Y (headline): Ke {r_imp:.2%} (dep12T ngu y {r_imp - 0.135 + 0.074:.2%}) | w XAU {wx_imp:.3f} (CO_SO 0,45, TOT phan con lai) | RONIC 5 nam chan {cap_imp:.1%} | ban A (giu CK FTEL): Ke {r_imp_A:.2%}")
implied = dict(r=r_imp, dep12_implied=r_imp - 0.135 + 0.074, w_xau=wx_imp, ronic_phase_cap=cap_imp, r_altA=r_imp_A)

nonop = ASSOC['0611'][0] + ASSOC['0611'][1] + OTHER_ASSOC_BOOK + INV_OTHER + CIP_EDU - NCI
ni_int = NET_INT9 * 4 / 3 * 0.85; co = core_op(600.0); gord = {}
for g in (0.04, 0.05):
    cvT = 1 - g / R
    gord[f'A_khong_lai_tg_RONICKe_g{g}'] = (co * (1 + g) / R + nonop + NC) / SH * 1e3
    gord[f'B_co_lai_tg_RONICKe_g{g}'] = ((co + ni_int) * (1 + g) / R + nonop) / SH * 1e3
print("Gordon RONIC=Ke (truoc CK): " + ' | '.join(f"{k} {x:,.0f}" for k, x in gord.items()))
json.dump(dict(price=PX, pxd=PXD, r=R, dep=dict(d0=d0, d1=d1), liq=L, ctrl=ctrl, bridge=bridge, main=main, pre=pre, sleeve40=s40, central=central,
               drivers=drivers, alts=alt_out, sens_r=sens_r, implied=implied, gordon=gord, r2_at_newpx_pct_below=r2_newpx['pct_below_px'],
               assoc={k: dict(fox=v_[0], frt=v_[1]) for k, v_ in ASSOC.items()}),
          open(os.path.join(HERE, 'model_r3_out.json'), 'w'), ensure_ascii=False, indent=1, default=float, sort_keys=True)
print('model_r3_out.json written')
