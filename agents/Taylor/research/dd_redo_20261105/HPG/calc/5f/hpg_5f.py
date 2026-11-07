"""5F addendum HPG (job Taylor_20261107_130203). Chay: $DNA_PYEXE -I hpg_5f.py > hpg_5f_out.txt
Mo hinh RI + luoi 675 ket cuc CHEP NGUYEN hpg_r2.py (SC, ri(), TLSH_AX, SLOPE, MULT, DG, quy uoc nam 1 = 0,25 nam Q4/26, ROLL).
Chi thay QUY TAC TERMINAL (mode):
  CUR  = mo hinh hien hanh: g_RI = 0 neu ROE_T < r, nguoc lai g_RI = g (=> nhanh ROE_T>r ngam RONIC>Ke)
  SYM  = chat-3c: g_RI = 0 moi nhanh (RONIC = Ke DOI XUNG), ROE_T giu theo kich ban
  CAPm/CAPa = SYM + ROE_T = min(ROE_T, TB chu ky nganh) (trung vi / trung binh peer ROE10Y)
  REVm/REVa = SYM + ROE_T = TB chu ky nganh moi nhanh (hoi quy hai chieu)
  WIDE = ROE_T = max(ROE_T, ROE5Y HPG x thue 20%), g_RI = g (RONIC > Ke)
  NONE = SYM + spread (ROE_T - r) fade tuyen tinh ve 0 trong N=5 nam sau 2029 (hai chieu)
Peer ROE10Y (BQ ticker_financial Q4/2025, ROE10Y): HSG .162 NKG .151 VGS .124 SMC .112 GDA .159 TLH .059 TVN .044 -> trung vi .124, trung binh .1159
HPG ROE5Y .169 (Q4/2025) x TAXF."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '_common_014125'))
import common as C, r2common as R2C
import numpy as np

SH = 8442.96452; BV0 = 148795.5; PAYOUT = 0.20; TAXF = 0.80 / 0.88
SC = {'XAU': dict(w=0.25, e=[5500, 16000, 15000, 16000], g=0.03),
      'TRUNG_LAP': dict(w=0.50, e=[7000, 26000, 26000, 27000], g=0.05),
      'TOT': dict(w=0.25, e=[8000, 31000, 33000, 35000], g=0.05)}
TLSH = 9915.0
TLSH_AX = ((-0.25, 0.10), (0.0, 0.50), (0.25, 0.20), (0.50, 0.12), (1.00, 0.08))
SLOPE = (-0.05, 0.0, 0.05); MULT = (0.80, 0.90, 1.00, 1.10, 1.20); DG = (-0.01, 0.0, 0.01)
PEER = dict(HSG=.162, NKG=.151, VGS=.124, SMC=.112, GDA=.159, TLH=.059, TVN=.044)
IND_MED = float(np.median(list(PEER.values()))); IND_MEAN = float(np.mean(list(PEER.values())))
HPG_ROE5Y = 0.169 * TAXF; NFADE = 5
L = R2C.liq2('HPG'); PX, PXD = 21700.0, '2026-11-04'
A = C.anchor_info(); R = A['r']
ROLL = (np.datetime64(PXD) - np.datetime64('2026-09-30')).astype(int) / 365


def ri(e, ke, g, mult=1.0, dg=0.0, mode='CUR'):
    bv = BV0; pv = 0.0; t = 0.0; e = [x * mult for x in e]
    for i, ni in enumerate(e):
        dt = 0.25 if i == 0 else 1.0; t += dt
        pv += (ni - ke * dt * bv) / (1 + ke) ** t; bv += ni * (1 - PAYOUT)
    gg = g + dg; roeT = e[-1] * (1 + gg) * TAXF / bv
    if mode == 'CUR':
        g_ri = 0.0 if roeT < ke else gg; tv = (roeT - ke) * bv / (ke - g_ri) / (1 + ke) ** t
    elif mode == 'WIDE':
        roeT = max(roeT, HPG_ROE5Y); tv = (roeT - ke) * bv / (ke - gg) / (1 + ke) ** t
    elif mode == 'NONE':
        tv = sum((roeT - ke) * bv * max(0.0, 1 - (k - 1) / NFADE) / (1 + ke) ** (t + k) for k in range(1, NFADE + 1))
    else:
        if mode == 'CAPm': roeT = min(roeT, IND_MED)
        if mode == 'CAPa': roeT = min(roeT, IND_MEAN)
        if mode == 'REVm': roeT = IND_MED
        if mode == 'REVa': roeT = IND_MEAN
        tv = (roeT - ke) * bv / ke / (1 + ke) ** t
    return (BV0 + pv + tv) / SH * 1e3 * (1 + ke) ** ROLL, roeT


def fv(r, scen, mult, dg, slope, tlsh, mode):
    s = SC[scen]; e = list(s['e']); e[2] *= 1 + slope; e[3] *= (1 + slope) ** 2
    return ri(e, r, s['g'], mult=mult, dg=dg, mode=mode)[0] - tlsh * TLSH / SH * 1e3


axes = [('scen', [(n, s['w']) for n, s in SC.items()]), ('mult', [(x, 1 / 5) for x in MULT]), ('dg', [(x, 1 / 3) for x in DG]),
        ('slope', [(x, 1 / 3) for x in SLOPE]), ('tlsh', list(TLSH_AX))]
print(f"r {R:.2%} | d_ref 5ty {L['d_ref']:.4%} | sleeve {L['d_sleeve']} | peer ROE10Y trung vi {IND_MED:.3f} TB {IND_MEAN:.4f} | HPG ROE5Y x thue {HPG_ROE5Y:.4f}")
for n, s in SC.items():
    print(f"  {n}: ROE_T (CUR) {ri(s['e'], R, s['g'])[1]:.2%}")
OUT = {}
for mode in ('CUR', 'SYM', 'CAPm', 'CAPa', 'REVm', 'REVa', 'WIDE', 'NONE'):
    res = R2C.outcomes(axes, lambda **kw: fv(R, mode=mode, **kw))
    o = {}
    for lab, d in (('5ty', L['d_ref']), ('10tr', L['d_sleeve']['10tr']), ('40tr', L['d_sleeve']['40tr'])):
        st = R2C.stats(res, PX, d); st['label'] = R2C.label(PX, st); o[lab] = st
    OUT[mode] = o; m = o['5ty']
    print(f"{mode:5s} tam {m['center']:,.0f} P10 {m['p10']:,.0f} P50 {m['p50']:,.0f} P90 {m['p90']:,.0f} | %duoi gia {m['pct_below_px']:.1%} | nhan 5ty {m['label']} / 10tr {o['10tr']['label']} (P90 {o['10tr']['p90']:,.0f}) / 40tr {o['40tr']['label']}")
LOCK = R2C.md5s([os.path.abspath(__file__), os.path.join(HERE, '..', 'hpg_r2.py'), os.path.join(R2C.HERE, 'common.py'), os.path.join(R2C.HERE, 'r2common.py'),
                 os.path.join(R2C.HERE, 'bq_px_liq_20261104.csv')])
for k, v in LOCK.items(): print(f"LOCK {v} {k}")
json.dump(dict(r=R, peer=PEER, ind_med=IND_MED, ind_mean=IND_MEAN, hpg_roe5y_taxadj=HPG_ROE5Y, nfade=NFADE, res=OUT, lock=LOCK),
          open(os.path.join(HERE, 'hpg_5f_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
