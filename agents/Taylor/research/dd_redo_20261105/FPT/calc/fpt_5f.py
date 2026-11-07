"""ADDENDUM 5F FPT 07/11/2026 (job Taylor_20261107_120553). Chay: $DNA_PYEXE -I fpt_5f.py > fpt_5f_out.txt
Tai dung NGUYEN mo hinh fpt_r2.py (exec phan truoc finalize, KHONG ghi file nao cua r2); chi doi cach tinh conv o TERMINAL/giai doan tuong minh
theo moat: RONIC ngam dinh = g/(1-conv).
 WIDE  = mo hinh hien hanh (RONIC terminal ngam dinh CO_SO 16%, TOT 26,7% > Ke; XAU 5% < Ke).
 NARROW= RONIC terminal <= Ke: conv_T = min(conv, 1 - gT/Ke) (khong thuong moat o terminal; giu 5 nam tuong minh = fade N=5; XAU giu nguyen vi < Ke la phat co du lieu).
 NARROW_SYM = RONIC terminal = Ke moi kich ban (ke ca XAU nang len) - ban doi chieu.
 NONE  = RONIC <= Ke ca 5 nam tuong minh lan terminal (tang truong khong tao gia tri; KHONG fade ROIC von hien huu => can tren cua NONE)."""
import os, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'fpt_r2.py')).read().split('RES = R2C.finalize')[0]
ns = dict(__file__=os.path.join(HERE, 'fpt_r2.py'), __name__='fpt_r2_model'); exec(src, ns)
R2C, R, PX, SH, SC, axes, core_op = ns['R2C'], ns['R'], ns['PX'], ns['SH'], ns['SC'], ns['axes'], ns['core_op']
d = R2C.liq2('FPT')['d_ref']
orig_dcf = ns['dcf']

def make_dcf(mode):
    def dcf(base, g1, conv, gT, ke, n=5):
        ce = conv if mode in ('WIDE', 'NARROW', 'NARROW_SYM') else min(conv, max(1 - g1 / ke, 0.0))
        cT = {'WIDE': conv, 'NARROW': min(conv, 1 - gT / ke), 'NARROW_SYM': 1 - gT / ke, 'NONE': min(conv, 1 - gT / ke)}[mode]
        pv, e = 0.0, base
        for t in range(1, n + 1):
            e *= 1 + g1; pv += e * ce / (1 + ke) ** t
        tv = e * (1 + gT) * cT / (ke - gT); pvtv = tv / (1 + ke) ** n
        return pv + pvtv, pvtv / (pv + pvtv)
    return dcf

out = {}
for mode in ('WIDE', 'NARROW', 'NARROW_SYM', 'NONE'):
    ns['dcf'] = make_dcf(mode)
    res = R2C.outcomes(axes, lambda **kw: ns['fv2'](R, **kw))
    s = R2C.stats(res, PX, d); s['label'] = R2C.label(PX, s)
    s['central'] = ns['fv2'](R, scen='CO_SO', dconv=0.0, dg=0.0, frt_d=0.0, oth=0) * (1 - d)
    s['scen_central'] = {n: ns['fv2'](R, scen=n, dconv=0.0, dg=0.0, frt_d=0.0, oth=0) * (1 - d) for n in SC}
    out[mode] = s
    print(f"{mode:10s} tam {s['center']:,.0f} P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} | trung tam {s['central']:,.0f} | "
          + ' '.join(f"{n} {v:,.0f}" for n, v in s['scen_central'].items()) + f" | %duoi gia {s['pct_below_px']:.1%} | {s['label']}")
ns['dcf'] = orig_dcf
print("RONIC terminal ngam dinh (conv, g_T, Ke %.2f%%):" % (R * 100), {n: round(SC[n][2] / (1 - SC[n][1]), 4) for n in SC},
      "| conv_T tai RONIC=Ke:", {n: round(1 - SC[n][2] / R, 4) for n in SC})
print(f"Gia {PX:,.0f}; CK thanh khoan 5 ty {d:.4%}")
json.dump(dict(r=R, px=PX, d_liq=d, modes=out), open(os.path.join(HERE, 'fpt_5f_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
