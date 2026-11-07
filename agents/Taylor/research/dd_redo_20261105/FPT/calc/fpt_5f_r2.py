"""ADDENDUM 5F FPT r2 (07/11/2026, job Taylor_20261107_122439). Chay: $DNA_PYEXE -I fpt_5f_r2.py > fpt_5f_r2_out.txt
Exec nguyen mo hinh fpt_r2.py (khong ghi file r2). Bien the = (terminal: WIDE/NARROW(cat 1 chieu)/SYM(RONIC_T=Ke doi xung)) x (cap RONIC giai doan explicit: None/25,5%/17,7%)."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'fpt_r2.py')).read().split('RES = R2C.finalize')[0]
ns = dict(__file__=os.path.join(HERE, 'fpt_r2.py'), __name__='fpt_r2_model'); exec(src, ns)
R2C, R, PX, SH, SC, axes = ns['R2C'], ns['R'], ns['PX'], ns['SH'], ns['SC'], ns['axes']
d = R2C.liq2('FPT')['d_ref']; orig = ns['dcf']

def make(term, cap):
    def dcf(base, g1, conv, gT, ke, n=5):
        ce = conv if cap is None else min(conv, max(1 - g1 / cap, 0.0))
        cT = {'WIDE': conv, 'ONEWAY': min(conv, 1 - gT / ke), 'SYM': 1 - gT / ke}[term]
        if cap is not None and term != 'WIDE': cT = min(cT, 1 - gT / max(cap, ke)) if term == 'ONEWAY' else cT
        pv, e = 0.0, base
        for t in range(1, n + 1):
            e *= 1 + g1; pv += e * ce / (1 + ke) ** t
        return pv + e * (1 + gT) * cT / (ke - gT) / (1 + ke) ** n, 0
    return dcf
out = {}
for term in ('WIDE', 'ONEWAY', 'SYM'):
    for cap in (None, 0.255, 0.177):
        ns['dcf'] = make(term, cap)
        s = R2C.stats(R2C.outcomes(axes, lambda **kw: ns['fv2'](R, **kw)), PX, d); s['label'] = R2C.label(PX, s)
        s['central'] = ns['fv2'](R, scen='CO_SO', dconv=0.0, dg=0.0, frt_d=0.0, oth=0) * (1 - d)
        k = f"{term}|cap={cap}"; out[k] = s
        print(f"{k:18s} tam {s['center']:,.0f} P10 {s['p10']:,.0f} P50 {s['p50']:,.0f} P90 {s['p90']:,.0f} | tt {s['central']:,.0f} | %duoi {s['pct_below_px']:.1%} | {s['label']}")
ns['dcf'] = orig
print("RONIC explicit ngam dinh g1/(1-conv):", {n: round(SC[n][0] / (1 - SC[n][1]), 3) for n in SC})
print(f"Gia {PX:,.0f}; CK {d:.4%}")
json.dump(out, open(os.path.join(HERE, 'fpt_5f_r2_out.json'), 'w'), ensure_ascii=False, indent=1, default=float)
