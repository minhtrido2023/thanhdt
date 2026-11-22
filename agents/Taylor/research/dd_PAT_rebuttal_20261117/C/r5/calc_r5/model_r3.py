"""PAT r3 — chạy SAU khoá lock_r3.txt (md5 assumptions_objective_r3.md = f312ad6c...).
Tham số nguyên văn assumptions_objective_r3.md. Khung: chuỗi tường minh 2027..2045 + Gordon 2046+.
"""
import math, json, itertools, sys

SH = 25.0
NET_CASH0 = 1.246 + 558.069 - 67.218 - 76.690
LOCKED70 = 70 - 70 * 0.060 * 0.80 / 0.135
KTPL9T = 0.06 * 215.713
NET_CASH = NET_CASH0 - LOCKED70 - KTPL9T
REV = 1366.520 * 4 / 3
DV = 0.2508; REST = 0.0582
F5 = 1 + 0.30 * 0.035 + 0.25 * 0.06 - 0.10 * 0.02
K = 1.37 / 1.13 * 3857 / 100e6
STEP = 1 - 0.85 / 0.90
U27 = 0.5520 + K * (2108 - 2040); R27 = 0.4864 + K * (2108 - 1541)
O3 = 0.5520 + K * (1825 - 2040); O2 = 0.4864 + K * (1825 - 1541); O1 = 0.4660 + K * (1825 - 1491)
LAMBDA = -math.log(0.70) / 6.5
LAST = 2045
TAX = {y: (0.05 if y <= 2030 else 0.10 if y <= 2032 else 0.20) for y in range(2028, LAST + 1)}

def year_window(y):
    if y == 2027: return (1.5, 13.5)
    a = 13.5 + 12 * (y - 2028); return (a, a + 12)

def levels(y):
    return (U27, R27, R27) if y == 2027 else (O3, O2, O1)

def leaf_nvl(D, a_yes, tau_a, tau_b, u, dm=0.05):
    """NVL_y theo năm cho 1 lá (trung bình thời gian)."""
    out = {}
    for y in range(2027, LAST + 1):
        a, b = year_window(y); unres, res, o1 = levels(y)
        n = int(round((b - a) / dm)); s = 0.0
        for i in range(n):
            m = a + (i + 0.5) * dm
            if m < 7.5: s += unres; continue
            A_ok = a_yes and m >= tau_a
            B_ok = m >= max(tau_b, 7.5)
            if (A_ok if D == 'A' else B_ok):
                s += o1 if (A_ok and B_ok and y >= 2028 and u == 1) else res
            else:
                s += unres
        out[y] = s / n
    return out

def ebit(nvl, f, p, s_exp, elec, vol=1.0):
    rev = REV * f * p * vol
    sga = 0.0385 * s_exp * rev + 6.3 + 5 + 17
    return rev - REV * vol * (nvl + DV * elec) - REV * REST - sga

def value(nvl_by_year, f, p, s_exp, elec, r=0.135, g=0.02, lr_mult=1.0, oneoff=0.0, cash=None,
          transfer=0.0, vol27=1.0, detail=False):
    ff = f * (1 - 0.65 * transfer)
    e27 = ebit(nvl_by_year[2027], ff, p, s_exp, elec, vol27) if vol27 == 1.0 else \
        0.5 * ebit(nvl_by_year[2027], ff, p, s_exp, elec, 1.0) + 0.5 * ebit(nvl_by_year[2027], ff, p, s_exp, elec, vol27)  # vol27 = hệ số sản lượng H2/2027
    pv = 53.844 * 0.95 * 0.94 / (1 + r) ** 0.13 + e27 * 0.95 * 0.94 / (1 + r) ** 0.63
    el = None
    for y in range(2028, LAST + 1):
        el = ebit(nvl_by_year[y], ff, p, s_exp, elec) * lr_mult * (1 + g) ** (y - 2028)
        pv += el * (1 - TAX[y]) * 0.94 / (1 + r) ** (1.63 + y - 2028)
    tv = el * (1 + g) * 0.8 * 0.94 / (r - g) / (1 + r) ** (1.63 + LAST - 2028)
    nc = NET_CASH if cash is None else cash
    eq = pv + tv + nc + oneoff
    if detail:
        e28 = ebit(nvl_by_year[2028], ff, p, s_exp, elec); e45 = ebit(nvl_by_year[LAST], ff, p, s_exp, elec)
        return dict(per_share=eq / SH * 1000, equity=eq, pv_flows=pv, pv_tv=tv, net_cash=nc, ebit27=e27,
                    ebit28=e28, ebit45=e45, tv_share=tv / eq,
                    gpm28=1 - REV * (nvl_by_year[2028] + DV * elec + REST) / (REV * ff * p),
                    gpm45=1 - REV * (nvl_by_year[LAST] + DV * elec + REST) / (REV * ff * p))
    return eq / SH * 1000

# ---------- O-node states ----------
def b_buckets(lam=LAMBDA, cut_month=None, q_perm=0.0):
    """Trả [(p, tau_rep)]; tau=inf = không giải. cut_month: B chỉ giải trước mốc (r2-style)."""
    edges = [0.0, 7.5, 13.5] + [13.5 + 12 * k for k in range(1, LAST - 2027 + 1)]
    F = lambda t: (1 - q_perm) * (1 - math.exp(-lam * t))
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        if cut_month is not None and a >= cut_month: break
        bb = b if cut_month is None else min(b, cut_month)
        p = F(bb) - F(a)
        if p <= 0: continue
        # E[tau | a<tau<=bb] cho mũ cắt cụt
        ea, eb = math.exp(-lam * a), math.exp(-lam * bb)
        mean = (a * ea - bb * eb) / (ea - eb) + 1 / lam
        out.append((p, mean))
    out.append((1 - sum(p for p, _ in out), float('inf')))
    return out

def o_states(pA=0.5, tau_a=10.5, lam=LAMBDA, cut_month=None, q_perm=0.0):
    st = []
    for D in ('A', 'B'):
        for a_yes, pa in ((True, pA), (False, 1 - pA)):
            for pb, tb in b_buckets(lam, cut_month, q_perm):
                for u in (0, 1):
                    w = 0.5 * pa * pb * 0.5
                    if w > 0: st.append((w, D, a_yes, tb, u))
    return st

_cache = {}
def nvl_for(D, a_yes, tau_a, tb, u):
    key = (D, a_yes, tau_a, tb, u)
    if key not in _cache: _cache[key] = leaf_nvl(D, a_yes, tau_a, tb, u)
    return _cache[key]

def expected_nvl(states, tau_a=10.5):
    E = {y: 0.0 for y in range(2027, LAST + 1)}
    for w, D, a_yes, tb, u in states:
        n = nvl_for(D, a_yes, tau_a, tb, u)
        for y in E: E[y] += w * n[y]
    return E

PP = {0.937: 0.32, 1.0: 0.58, 1.063: 0.10}
PT = {'Ta': (1.0, 0.35, 0.65), 'Tb': (0.35, 0.35, 0.25), 'Tc': (0.135, 0.135, 0.10)}

def run(PX15=0.97, cut=0.985, pA=0.5, tau_a=10.5, cut_month=None, q_perm=0.0, PPd=None, collect=True):
    PPd = PPd or PP
    elec = cut * F5
    states = o_states(pA, tau_a, LAMBDA, cut_month, q_perm)
    leaves = []
    # O-states aggregated to unique NVL paths for speed
    for (w, D, a_yes, tb, u) in states:
        n = nvl_for(D, a_yes, tau_a, tb, u)
        for (p, pp), (t, (s, sx, pt)), (x, px) in itertools.product(PPd.items(), PT.items(), ((15, PX15), (10, 1 - PX15))):
            if px <= 0: continue
            f = 1 - s * STEP if x == 15 else 1.0
            leaves.append((w * pp * pt * px, value(n, f, p, sx, elec), D, a_yes, tb, u, p, t, x))
    tot = sum(l[0] for l in leaves); center = sum(l[0] * l[1] for l in leaves)
    En = expected_nvl(states, tau_a)
    EP = sum(k * v for k, v in PPd.items())
    Ef = PX15 * sum(pt * (1 - s * STEP) for s, sx, pt in PT.values()) + (1 - PX15)
    Esx = sum(pt * sx for s, sx, pt in PT.values())
    return dict(leaves=leaves, tot=tot, center=center, En=En, EP=EP, Ef=Ef, Esx=Esx, elec=elec)

def wq(leaves, q):
    acc = 0
    for l in sorted(leaves, key=lambda z: z[1]):
        acc += l[0]
        if acc >= q: return l[1]

if __name__ == '__main__':
    R = run()
    L = R['leaves']
    base = value(R['En'], R['Ef'], R['EP'], R['Esx'], R['elec'], detail=True)
    q = {k: wq(L, v) for k, v in (('P10', .10), ('P25', .25), ('P50', .50), ('P75', .75), ('P90', .90))}
    print(f"NET_CASH {NET_CASH:.3f} ELEC {R['elec']:.5f} LAMBDA {LAMBDA:.6f} leaves {len(L)} sum_p {R['tot']:.10f}")
    print("E[NVL] by year:", {y: round(v, 4) for y, v in R['En'].items() if y in (2027, 2028, 2029, 2030, 2033, 2045)})
    print(f"TAM {R['center']:,.0f}  quantiles " + "  ".join(f"{k} {v:,.0f}" for k, v in q.items()))
    print("CO SO (inputs ky vong):", {k: round(v, 4) for k, v in base.items()})
    # marginals
    for name, idx, keys in (('D', 2, ('A', 'B')), ('Ayes', 3, (True, False)), ('P', 6, PP), ('T', 7, PT), ('TX', 8, (15, 10))):
        out = {}
        for k in keys:
            sel = [l for l in L if l[idx] == k]; w = sum(l[0] for l in sel)
            if w: out[str(k)] = (round(w, 4), round(sum(l[0] * l[1] for l in sel) / w))
        print('node', name, out)
    # B-timing marginal (coarse)
    bt = {}
    for l in L:
        k = 'by_mid27' if l[4] <= 7.5 else 'H2_27' if l[4] <= 13.5 else '2028' if l[4] <= 25.5 else '2029-30' if l[4] <= 49.5 else '2031+'
        bt.setdefault(k, [0, 0]); bt[k][0] += l[0]; bt[k][1] += l[0] * l[1]
    print('B timing', {k: (round(v[0], 4), round(v[1] / v[0])) for k, v in bt.items()})
    json.dump(dict(center=R['center'], quantiles=q, base=base, En=R['En'], EP=R['EP'], Ef=R['Ef'], Esx=R['Esx'], elec=R['elec'],
                   net_cash=NET_CASH, n_leaves=len(L)), open('model_out_r3.json', 'w'), indent=1, default=float)
