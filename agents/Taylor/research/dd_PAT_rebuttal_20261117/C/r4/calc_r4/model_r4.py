"""PAT r4 — chạy SAU khoá lock_r4.txt (md5 assumptions_objective_r4.md = 2521604d...).
Sửa từ model_r3.py (bản sao trong thư mục này, không đổi). Thay đổi base r4 so với r3:
  (1) hệ số cước 0,0385 -> 0,046858 (9T/26, p29/p31)
  (2) nút P theo quy tắc ánh xạ một độ co giãn (assumptions §3.2) -> {0,9384; 0,9961; 1,0670}
  (3) tồn kho dư 44,44 tỷ giải phóng tại thời điểm cung bình thường hoá đầu tiên (§3.4)
Nút O giữ khung r3 (π_B = 1, λ F7, A nhị phân, ánh xạ D/U) — §3.1. Các tuỳ chọn khác chỉ phục vụ độ nhạy.
"""
import math, json, itertools

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
LAMBDA = -math.log(0.70) / 6.5
LAST = 2045
TAX = {y: (0.05 if y <= 2030 else 0.10 if y <= 2032 else 0.20) for y in range(2028, LAST + 1)}
FREIGHT_R4 = 22.843840946 / 487.507728152      # 0,046858
FREIGHT_R3 = 0.0385
INV_EXCESS = 120.190 - (84.700 + 67.712 + 74.843) / 3   # 44,438
PP_R4 = {0.9384: 0.32, 0.9961: 0.58, 1.0670: 0.10}
PP_R3 = {0.937: 0.32, 1.0: 0.58, 1.063: 0.10}
PT_R3 = {'Ta': (1.0, 0.35, 0.65), 'Tb': (0.35, 0.35, 0.25), 'Tc': (0.135, 0.135, 0.10)}

def levels_for(coke_lr=1825.0):
    U27 = 0.5520 + K * (2108 - 2040); R27 = 0.4864 + K * (2108 - 1541)
    O3 = 0.5520 + K * (coke_lr - 2040); O2 = 0.4864 + K * (coke_lr - 1541); O1 = 0.4660 + K * (coke_lr - 1491)
    return U27, R27, O3, O2, O1

def year_window(y):
    if y == 2027: return (1.5, 13.5)
    a = 13.5 + 12 * (y - 2028); return (a, a + 12)

def leaf_path(D, a_yes, tau_a, tau_b, u, cell='D', coke_lr=1825.0, vol=(1.0, 1.0), dm=0.05):
    """Trả {y: (nvl_avg, v_avg, vnvl_avg)}.
    cell: 'D' (r3/r4 base: ô (A tắt,B bật) theo D), 'opt75' (D=A ∧ A-không ∧ B bật -> trung điểm O2/O3), 'O2' (ô -> O2 hẳn).
    vol = (v_thiếu, v_bình_thường): thiếu khi chưa nguồn nào hiệu lực (m<7,5 luôn thiếu)."""
    U27, R27, O3, O2, O1 = levels_for(coke_lr)
    out = {}
    for y in range(2027, LAST + 1):
        a, b = year_window(y)
        unres, res, o1 = (U27, R27, R27) if y == 2027 else (O3, O2, O1)
        n = int(round((b - a) / dm)); s = sv = svn = 0.0
        for i in range(n):
            m = a + (i + 0.5) * dm
            if m < 7.5:
                lv = unres; v = vol[0]
            else:
                A_ok = a_yes and m >= tau_a
                B_ok = m >= max(tau_b, 7.5)
                v = vol[1] if (A_ok or B_ok) else vol[0]
                if A_ok and B_ok:
                    lv = o1 if (y >= 2028 and u == 1) else res
                elif (A_ok if D == 'A' else B_ok):
                    lv = res
                elif B_ok and not A_ok and D == 'A' and cell != 'D':   # ô (A tắt, B bật) nhánh D=A
                    lv = res if cell == 'O2' else 0.5 * (res + unres)
                else:
                    lv = unres
            s += lv; sv += v; svn += v * lv
        out[y] = (s / n, sv / n, svn / n)
    return out

def t_release(a_yes, tau_a, tau_b):
    tb = max(tau_b, 7.5)
    t = min(tb, max(tau_a, 7.5)) if a_yes else tb
    return t

def ebit(path_y, f, p, s_exp, elec, freight, vol27=1.0, y=None):
    nvl, v, vn = path_y
    rev = REV * f * p * v
    sga = freight * s_exp * rev + 6.3 + 5 + 17
    return rev - REV * (vn + DV * elec * v) - REV * REST - sga

def value(path, f, p, s_exp, elec, freight=FREIGHT_R4, r=0.135, g=0.02, lr_mult=1.0, oneoff=0.0, cash=None,
          transfer=0.0, vol27=1.0, inv_pv=0.0, detail=False):
    ff = f * (1 - 0.65 * transfer)
    e27 = ebit(path[2027], ff, p, s_exp, elec, freight)
    if vol27 != 1.0:   # giữ cách r3: hệ số sản lượng H2/2027
        n, v, vn = path[2027]
        e27 = 0.5 * e27 + 0.5 * ebit((n, v * vol27, vn * vol27), ff, p, s_exp, elec, freight)
    pv = 53.844 * 0.95 * 0.94 / (1 + r) ** 0.13 + e27 * 0.95 * 0.94 / (1 + r) ** 0.63
    el = None
    for y in range(2028, LAST + 1):
        el = ebit(path[y], ff, p, s_exp, elec, freight) * lr_mult * (1 + g) ** (y - 2028)
        pv += el * (1 - TAX[y]) * 0.94 / (1 + r) ** (1.63 + y - 2028)
    tv = el * (1 + g) * 0.8 * 0.94 / (r - g) / (1 + r) ** (1.63 + LAST - 2028)
    nc = NET_CASH if cash is None else cash
    eq = pv + tv + nc + oneoff + inv_pv
    if detail:
        return dict(per_share=eq / SH * 1000, equity=eq, pv_flows=pv, pv_tv=tv, net_cash=nc, inv_pv=inv_pv, ebit27=e27,
                    ebit28=ebit(path[2028], ff, p, s_exp, elec, freight), ebit45=ebit(path[LAST], ff, p, s_exp, elec, freight),
                    tv_share=tv / eq,
                    ebitm28=ebit(path[2028], ff, p, s_exp, elec, freight) / (REV * ff * p),
                    ebitm45=ebit(path[LAST], ff, p, s_exp, elec, freight) / (REV * ff * p))
    return eq / SH * 1000

def b_buckets(lam=LAMBDA, cut_month=None, q_perm=0.0):
    edges = [0.0, 7.5, 13.5] + [13.5 + 12 * k for k in range(1, LAST - 2027 + 1)]
    F = lambda t: (1 - q_perm) * (1 - math.exp(-lam * t))
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        if cut_month is not None and a >= cut_month: break
        bb = b if cut_month is None else min(b, cut_month)
        p = F(bb) - F(a)
        if p <= 0: continue
        ea, eb = math.exp(-lam * a), math.exp(-lam * bb)
        mean = (a * ea - bb * eb) / (ea - eb) + 1 / lam
        out.append((p, mean))
    out.append((1 - sum(p for p, _ in out), float('inf')))
    return out

def o_states(pA=0.5, lam=LAMBDA, cut_month=None, q_perm=0.0, pD=0.5):
    st = []
    for D, pd in (('A', pD), ('B', 1 - pD)):
        for a_yes, pa in ((True, pA), (False, 1 - pA)):
            for pb, tb in b_buckets(lam, cut_month, q_perm):
                for u in (0, 1):
                    w = pd * pa * pb * 0.5
                    if w > 0: st.append((w, D, a_yes, tb, u))
    return st

_cache = {}
def path_for(D, a_yes, tau_a, tb, u, cell, coke_lr, vol):
    key = (D, a_yes, tau_a, tb, u, cell, coke_lr, vol)
    if key not in _cache: _cache[key] = leaf_path(D, a_yes, tau_a, tb, u, cell, coke_lr, vol)
    return _cache[key]

def run(PX15=0.97, cut=0.985, phi=1.0, pA=0.5, tau_a=10.5, lam=LAMBDA, cut_month=None, q_perm=0.0, pD=0.5,
        PPd=None, PTd=None, freight=FREIGHT_R4, inv=INV_EXCESS, cell='D', coke_lr=1825.0, vol=(1.0, 1.0),
        r=0.135, g=0.02, vol27=1.0):
    PPd = PPd or PP_R4; PTd = PTd or PT_R3
    elec = 1 + phi * (cut * F5 - 1)
    states = o_states(pA, lam, cut_month, q_perm, pD)
    leaves = []
    En = {y: [0.0, 0.0, 0.0] for y in range(2027, LAST + 1)}; Einv = 0.0
    for (w, D, a_yes, tb, u) in states:
        path = path_for(D, a_yes, tau_a, tb, u, cell, coke_lr, vol)
        trel = t_release(a_yes, tau_a, tb)
        ipv = 0.0 if math.isinf(trel) else inv * (1 + r) ** (-trel / 12)
        Einv += w * ipv
        for y in En:
            for k in range(3): En[y][k] += w * path[y][k]
        for (p, pp), (t, (s, sx, pt)), (x, px) in itertools.product(PPd.items(), PTd.items(), ((15, PX15), (10, 1 - PX15))):
            if px <= 0: continue
            f = 1 - s * STEP if x == 15 else 1.0
            leaves.append((w * pp * pt * px, value(path, f, p, sx, elec, freight, r, g, inv_pv=ipv, vol27=vol27),
                           D, a_yes, tb, u, p, t, x))
    tot = sum(l[0] for l in leaves); center = sum(l[0] * l[1] for l in leaves)
    En = {y: tuple(v) for y, v in En.items()}
    EP = sum(k * v for k, v in PPd.items())
    Ef = PX15 * sum(pt * (1 - s * STEP) for s, sx, pt in PTd.values()) + (1 - PX15)
    Esx = sum(pt * sx for s, sx, pt in PTd.values())
    return dict(leaves=leaves, tot=tot, center=center, En=En, EP=EP, Ef=Ef, Esx=Esx, elec=elec, Einv=Einv,
                freight=freight, r=r, g=g)

def wq(leaves, q):
    acc = 0
    for l in sorted(leaves, key=lambda z: z[1]):
        acc += l[0]
        if acc >= q: return l[1]

def base_path(R, **kw):
    kw.setdefault('freight', R['freight']); kw.setdefault('inv_pv', R['Einv'])
    return value(R['En'], R['Ef'], R['EP'], R['Esx'], R['elec'], **kw)

if __name__ == '__main__':
    R = run(); L = R['leaves']
    base = value(R['En'], R['Ef'], R['EP'], R['Esx'], R['elec'], R['freight'], inv_pv=R['Einv'], detail=True)
    q = {k: wq(L, v) for k, v in (('P10', .10), ('P25', .25), ('P50', .50), ('P75', .75), ('P90', .90))}
    print(f"NET_CASH {NET_CASH:.3f} ELEC {R['elec']:.5f} FREIGHT {R['freight']:.6f} INV {INV_EXCESS:.3f} E[PV inv] {R['Einv']:.3f} leaves {len(L)} sum_p {R['tot']:.10f}")
    print("E[NVL] by year:", {y: round(v[0], 4) for y, v in R['En'].items() if y in (2027, 2028, 2029, 2030, 2033, 2045)})
    print(f"TAM {R['center']:,.1f}  quantiles " + "  ".join(f"{k} {v:,.0f}" for k, v in q.items()))
    print("CO SO:", {k: round(v, 4) for k, v in base.items()})
    for name, idx, keys in (('D', 2, ('A', 'B')), ('Ayes', 3, (True, False)), ('P', 6, PP_R4), ('T', 7, PT_R3), ('TX', 8, (15, 10))):
        out = {}
        for k in keys:
            sel = [l for l in L if l[idx] == k]; w = sum(l[0] for l in sel)
            if w: out[str(k)] = (round(w, 4), round(sum(l[0] * l[1] for l in sel) / w))
        print('node', name, out)
    bt = {}
    for l in L:
        k = 'by_mid27' if l[4] <= 7.5 else 'H2_27' if l[4] <= 13.5 else '2028' if l[4] <= 25.5 else '2029-30' if l[4] <= 49.5 else '2031+'
        bt.setdefault(k, [0, 0]); bt[k][0] += l[0]; bt[k][1] += l[0] * l[1]
    print('B timing', {k: (round(v[0], 4), round(v[1] / v[0])) for k, v in bt.items()})
    json.dump(dict(center=R['center'], quantiles=q, base=base, En={y: v[0] for y, v in R['En'].items()}, EP=R['EP'],
                   Ef=R['Ef'], Esx=R['Esx'], elec=R['elec'], Einv=R['Einv'], freight=R['freight'], net_cash=NET_CASH,
                   n_leaves=len(L)), open('model_out_r4.json', 'w'), indent=1, default=float)
