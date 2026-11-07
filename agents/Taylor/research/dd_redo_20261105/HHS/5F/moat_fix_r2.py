"""HHS addendum 3c VONG SUA (job Taylor_20261107_131625, sau skeptic).
Loi r1: crv() de gia goc HTK cu (REST_CRV-NEW_I14 = 6.009,8 ty) KHONG chiet khau (chi thang du s nhan pv(4)) => von nam ~4 nam van huong Ke
+ cong bien TB peer = kenh RONIC>Ke ngam. Ban sua: tru gia goc*(1-pv(y)) [y=4 hoac 2,5], tuy chon tru phan khach tra truoc NMTT khoi von bi giam.
Tai dung hang so/truc tu 5F/moat_sens_5f.py (chep nguyen van calc/hhs_r2.py, da assert tai lap REPORT_r2).
Chay: $DNA_PYEXE -I 5F/moat_fix_r2.py > 5F/moat_fix_r2_out.txt"""
import os, sys, io, json, contextlib, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('m5', os.path.join(HERE, 'moat_sens_5f.py')); m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(m)   # chay lai = assert tai lap tam 10.387
R2C = m.R2C; SYM15 = ((-0.15, 0.25), (0.0, 0.50), (0.15, 0.25)); OLD = m.REST_CRV - m.NEW_I14

def run(name, cost_y=None, prepay=0.0, s_shift=0.0, i14=SYM15, gov=m.GOV_AX, cost_base=OLD):
    off = 0.0 if cost_y is None else (cost_base - prepay) * (1 - m.pv(cost_y, m.R))
    def fv2(scen, ds, hd, gov, bds, i14, kq):
        s = m.SC[scen]
        c = (m.CRV_COST + m.NMTT / m.VAT * s['m'] * m.pv(1, m.R) + OLD * max(s['s'] + s_shift + ds, 0.0) * m.pv(4, m.R)
             + m.NEW_I14 * i14 * m.pv(4, m.R) - off)
        core = m.HHS * c * (1 - hd) + m.OTHER + s['np'] * s['pe'] + bds * m.BDS_SURP * m.HHS * (1 - hd) - kq * m.KQ
        return core * (1 - gov) / m.SH * 1e3
    axes = [('scen', [(k, s['p']) for k, s in m.SC.items()]), ('ds', [(x, 1 / 5) for x in m.DS]), ('hd', list(m.HD_AX)), ('gov', list(gov)),
            ('bds', list(m.BDS_AX)), ('i14', list(i14)), ('kq', list(m.KQ_AX))]
    res = R2C.outcomes(axes, fv2); st = R2C.stats(res, m.PX, m.D); st['label'] = R2C.label(m.PX, st); st['cost_offset_bn'] = off
    for k, d in m.DSL.items():
        s2 = R2C.stats(res, m.PX, d); st['label_' + k] = R2C.label(m.PX, s2)
    st['E_gov'] = sum(a * b for a, b in gov)
    print(f"{name:44s} off {off:7.1f} | {R2C.fmt(st)} | {st['label']} | 10tr {st['label_10tr']} 40tr {st['label_40tr']}")
    return st

sh = lambda g: m.s_of_g(g) - m.ES
O = {}
O['R1_STRICT_nodisc'] = run('r1 chat-3c (gia goc KHONG chiet khau)')
O['FIX_A_pv4'] = run('A: gia goc pv(4)', 4)
O['FIX_B_pv2.5'] = run('B: gia goc pv(2,5)', 2.5)
O['FIX_C_pv2.5_prepay'] = run('C: gia goc pv(2,5) tru KH tra truoc 3.099', 2.5, m.NMTT)
O['FIX_A_pv4_incl_I14cost'] = run('A+: pv(4) ca gia goc I.14 (7.338,8)', 4, 0.0, cost_base=m.REST_CRV)
for k, y, pp in (('A', 4, 0.0), ('B', 2.5, 0.0), ('C', 2.5, m.NMTT)):
    O[f'{k}_govzero'] = run(f'{k} + GOV=0 (do dong gop truc quan tri)', y, pp, gov=((0.0, 1.0),))
    O[f'{k}_NONE_TCH'] = run(f'{k} + NONE-san GPM=TB TCH 29,9%', y, pp, sh(m.TCH_G))
    O[f'{k}_NARROW'] = run(f'{k} + NARROW GPM 45,0%, I.14 hien hanh', y, pp, sh((m.PEER_MEAN + m.OWN_G) / 2), m.I14_AX)
    O[f'{k}_WIDE'] = run(f'{k} + WIDE GPM 52,2%, I.14 +40%', y, pp, sh(m.OWN_G), ((0.40, 1.0),))
json.dump(O, open(os.path.join(HERE, 'moat_fix_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
