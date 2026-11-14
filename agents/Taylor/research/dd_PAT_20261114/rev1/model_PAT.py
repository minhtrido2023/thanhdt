"""DD PAT valuation — inputs locked in ../assumptions_PAT.md. Units: tỷ đồng; per share đ."""
import csv, os
SH = 25.0            # triệu cp -> tỷ / (SH) * 1000 = đ/cp
NETCASH = 1.25 + 558.07 - 67.22 - 76.69   # C3
NWC = 53.0
def tax(year):  # B4; period t=1 ~ 2027
    return 0.05 if year <= 2030 else (0.10 if year <= 2032 else 0.20)
def dcf(ebt_path, r=0.135, g=0.02, finite_end=None, fin_income=0.0):
    pv = 0.0; last = None
    for t in range(1, 60):
        y = 2026 + t
        ebt = ebt_path(y)
        ni = ebt * (1 - tax(y))
        fcfe = ni  # capex = D&A, dNWC = 0
        if finite_end and y > finite_end:
            pv += NWC / (1 + r) ** (t - 1); return pv
        if y >= 2033 and not finite_end:
            # Gordon from 2033 on (tax steady 20%)
            tv = fcfe * (1 + 0) / (r - g)
            pv += tv / (1 + r) ** (t - 1) / (1 + r) * (1 + r)  # tv at t-1 discounted to 0 includes year t flow
            return pv
        pv += fcfe / (1 + r) ** t
    return pv
def base(y):  return 245.0 * (1.02 ** max(0, y - 2030))
def good(y):  return 330.0 * (1.02 ** max(0, y - 2030))
def bad(y):   return 150.0 if y <= 2028 else 200.0
def per_share(v): return v / SH * 1000
def run(r=0.135):
    out = {}
    out['base'] = dcf(base, r) + NETCASH
    out['good'] = dcf(good, r) + NETCASH
    out['bad_gc'] = dcf(bad, r) + NETCASH
    out['bad_finite'] = dcf(bad, r, finite_end=2034) + NETCASH
    out['bad'] = 0.5 * out['bad_gc'] + 0.5 * out['bad_finite']
    out['weighted'] = 0.30 * out['bad'] + 0.50 * out['base'] + 0.20 * out['good']
    return out
if __name__ == '__main__':
    rows = []
    res = run()
    for k, v in res.items():
        rows.append(['scenario', k, round(v, 1), round(per_share(v))])
    # V_ngan / V_dai / C4 / D2
    r, g = 0.135, 0.02
    ni_norm = 287.7; roe = ni_norm / 708.45
    reinv = min(max(g / roe, 0), 0.8)
    v_ngan = ni_norm * (1 - reinv) * (1 + g) / (r - g)
    rows.append(['two_base', 'V_ngan', round(v_ngan, 1), round(per_share(v_ngan))])
    rows.append(['two_base', 'V_dai(=DCF base)', round(res['base'], 1), round(per_share(res['base']))])
    import math
    rows.append(['two_base', 'D=|ln(Vn/Vd)|', round(abs(math.log(v_ngan / res['base'])), 3), ''])
    cfo3 = (463.96 + 370.75 + 284.60) / 3; capex3 = (0.83 + 8.06 + 0.36) / 3; da = 45.0; rev = 1842.0
    c4 = cfo3 - min(capex3, da)
    v_c4 = c4 * (1 - reinv) * (1 + g) / (r - g)
    d2 = cfo3 - 0.05 * rev  # sector capex/revenue 5% (ước lượng)
    v_d2 = d2 * (1 - reinv) * (1 + g) / (r - g)
    rows.append(['two_base', 'V_C4 (theo doi)', round(v_c4, 1), round(per_share(v_c4))])
    rows.append(['two_base', 'V_D2 (theo doi, capex/DT nganh 5% uoc luong)', round(v_d2, 1), round(per_share(v_d2))])
    # r sensitivity (deposit +/-50/100bp, beta 1 and 0.5)
    for beta in (1.0, 0.5):
        for bp in (-100, -50, 50, 100):
            rr = 0.135 + beta * bp / 10000
            w = run(rr)['weighted']
            rows.append(['r_sens', f'beta{beta}_{bp:+d}bp_r{rr:.4f}', round(w, 1), round(per_share(w))])
    # liquidity discount
    w = res['weighted']
    for d in (0.0, 0.05, 0.10, 0.20):
        rows.append(['liq', f'disc{int(d*100)}%', round(w * (1 - d), 1), round(per_share(w * (1 - d)))])
    # moat sensitivity: NONE = fade EBT to 70% of base by 2033 (info only)
    none = dcf(lambda y: 245.0 * (1 - 0.3 * min(1, max(0, y - 2026) / 7)), 0.135) + NETCASH
    rows.append(['moat_sens', 'NONE (fade -30% to 2033, info only)', round(none, 1), round(per_share(none))])
    # operating sensitivities on base EBT (annual, tỷ)
    rows.append(['ebt_sens', 'P4 price +/-10% (~ +/-176 rev, ~full pass to EBT)', 176, ''])
    rows.append(['ebt_sens', 'electricity +/-5% (~500/yr est)', 25, ''])
    rows.append(['ebt_sens', 'export tax 10->15% on ~650 (run-rate 9T26) / ~1738 (2025 mix)', '32 / 87', ''])
    rows.append(['ebt_sens', 'volume -20% (contribution ~445/yr est)', 89, ''])
    rows.append(['meta', 'NETCASH_true', round(NETCASH, 1), round(per_share(NETCASH))])
    rows.append(['meta', 'cfo3_avg', round(cfo3, 1), ''])
    p = os.path.join(os.path.dirname(__file__), 'valuation_PAT.csv')
    with open(p, 'w', newline='') as f:
        csv.writer(f).writerows([['block', 'item', 'value_bn', 'per_share_vnd']] + rows)
    for r_ in rows: print(r_)
