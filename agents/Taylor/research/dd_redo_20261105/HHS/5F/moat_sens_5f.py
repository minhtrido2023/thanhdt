"""HHS addendum 3c (job Taylor_20261107_130213): do nhay moat tren mo hinh KHOA calc/hhs_r2.py.
Hang so + fv2 chep NGUYEN VAN tu calc/hhs_r2.py (khong import vi hhs_r2.py ghi de SUMMARY.json). Assert tai lap tam 10.387.
Chay: $DNA_PYEXE -I 5F/moat_sens_5f.py > 5F/moat_sens_5f_out.txt"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014125'))
import r2common as R2C
SH = 431.985968; HHS = 0.5115
EQ_ME, NCI = 9152.94, 7726.98
CRV_FV = NCI / (1 - HHS); STEP_AT = 2020.76 / 0.20 * 0.8; CRV_COST = CRV_FV - STEP_AT
OTHER = EQ_ME - HHS * CRV_FV - (694.84 - 310.74)
NMTT, VAT = 3099.20, 1.08; REST_CRV = 7338.8; NEW_I14 = 1329.0
SC = {'TIEU_CUC': dict(p=0.30, m=0.30, s=0.15, np=25, pe=5, hd=0.35),
      'CO_SO':    dict(p=0.50, m=0.335, s=0.40, np=35, pe=6, hd=0.25),
      'TICH_CUC': dict(p=0.20, m=0.36, s=0.55, np=50, pe=8, hd=0.15)}
BDS_SURP = (2459.74 - 1438.45) * 0.8; KQ = 28.4
HD_AX = ((0.0, 0.10), (0.15, 0.15), (0.25, 0.30), (0.35, 0.30), (0.45, 0.15))
GOV_AX = ((0.0, 0.55), (0.05, 0.20), (0.10, 0.15), (0.15, 0.10))
BDS_AX = ((0.0, 1 / 3), (0.5, 1 / 3), (1.0, 1 / 3))
I14_AX = ((-0.15, 0.25), (0.0, 0.50), (0.40, 0.25))
KQ_AX = ((0.0, 0.70), (1.0, 0.30))
DS = (-0.15, -0.075, 0.0, 0.075, 0.15)
J = json.load(open(os.path.join(HERE, '..', 'calc', 'hhs_r2_out.json')))
R = 0.135; PX = 9550.0; D = J['liq']['d_ref']; DSL = J['liq']['d_sleeve']
pv = lambda y, ke: 1 / (1 + ke) ** y
g_of_s = lambda s: (s + 0.08) / (s + 0.8)          # dd_HHS_20261101/calc/valuation_v2.py:44
s_of_g = lambda g: (0.8 * g - 0.08) / (1 - g)
ES = sum(v['p'] * v['s'] for v in SC.values())       # 0,355

def make(s_shift=0.0, m_mult=1.0):
    def crv(m, s, ke, s_new=0.0):
        return CRV_COST + NMTT / VAT * m * m_mult * pv(1, ke) + (REST_CRV - NEW_I14) * s * pv(4, ke) + NEW_I14 * s_new * pv(4, ke)
    def fv2(scen, ds, hd, gov, bds, i14, kq):
        s = SC[scen]; c = crv(s['m'], max(s['s'] + s_shift + ds, 0.0), R, i14)
        core = HHS * c * (1 - hd) + OTHER + s['np'] * s['pe'] + bds * BDS_SURP * HHS * (1 - hd) - kq * KQ
        return core * (1 - gov) / SH * 1e3
    return fv2

def run(name, s_shift=0.0, i14=I14_AX, m_mult=1.0):
    axes = [('scen', [(k, s['p']) for k, s in SC.items()]), ('ds', [(x, 1 / 5) for x in DS]), ('hd', list(HD_AX)), ('gov', list(GOV_AX)),
            ('bds', list(BDS_AX)), ('i14', list(i14)), ('kq', list(KQ_AX))]
    res = R2C.outcomes(axes, make(s_shift, m_mult))
    st = R2C.stats(res, PX, D); st['label'] = R2C.label(PX, st)
    for k, d in DSL.items():
        s2 = R2C.stats(res, PX, d); st['label_' + k] = R2C.label(PX, s2); st['p10_' + k] = s2['p10']; st['p90_' + k] = s2['p90']
    st['E_s'] = ES + s_shift; st['E_gpm_proxy'] = g_of_s(ES + s_shift); st['E_i14'] = sum(a * b for a, b in i14)
    print(f"{name:34s} E[s] {st['E_s']:.1%} (GPM~{st['E_gpm_proxy']:.1%}) E[I14] {st['E_i14']:+.2%} | {R2C.fmt(st)} | {st['label']} | 10tr {st['label_10tr']} 40tr {st['label_40tr']} (P10/P90 40tr {st['p10_40tr']:,.0f}/{st['p90_40tr']:,.0f})")
    return st

OUT = {}
OUT['CURRENT'] = run('CURRENT (REPORT_r2)')
assert abs(OUT['CURRENT']['center'] - J['main']['center']) < 0.5 and abs(OUT['CURRENT']['p10'] - J['main']['p10']) < 0.5, 'khong tai lap REPORT_r2'
PEER_MEAN, PEER_MED, TCH_G, OWN_G = 0.377, 0.379, 0.299, 0.522     # 5F/peer_stats_out.txt ; REPORT.md C7 (52,2%)
sh = lambda g: s_of_g(g) - ES
SYM15 = ((-0.15, 0.25), (0.0, 0.50), (0.15, 0.25)); SYM40 = ((-0.40, 0.25), (0.0, 0.50), (0.40, 0.25))
OUT['STRICT3C_I14sym15'] = run('STRICT-3C I.14 +-15 doi xung', 0.0, SYM15)
OUT['STRICT3C_I14sym40'] = run('STRICT-3C I.14 +-40 doi xung', 0.0, SYM40)
OUT['STRICT3C_peer_mean'] = run('STRICT-3C + GPM=TB peer 37,7%', sh(PEER_MEAN), SYM15)
OUT['STRICT3C_peer_median'] = run('STRICT-3C + GPM=trung vi peer 37,9%', sh(PEER_MED), SYM15)
OUT['NONE_TCH'] = run('NONE-san: GPM=TB TCH 29,9%', sh(TCH_G), SYM15)
OUT['NARROW'] = run('NARROW: GPM giua 45,0%', sh((PEER_MEAN + OWN_G) / 2), I14_AX)
OUT['WIDE'] = run('WIDE: GPM=NC-II 52,2%, I.14 +40%', sh(OWN_G), ((0.40, 1.0),))
OUT['STRESS_backlog_peer'] = run('stress backlog m x 37,7/52,2', 0.0, I14_AX, PEER_MEAN / OWN_G)
json.dump(OUT, open(os.path.join(HERE, 'moat_sens_5f_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
