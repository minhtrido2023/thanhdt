"""TCH — DD REDO VONG 3b (job Taylor_20261109_003030; vong cuoi, circuit-breaker). KHONG doc gia.
Sua bat doi xung r3 (tch_r3.py:33 chi chiet khau thang du dat cu): gia von + thang du cung pv(y), y theo moc hoan thanh du an (BCTN25),
chi phi hoan thanh tuong lai k*C chi tai y/2 va sinh bien s nhu chi phi da phat sinh; k DO tu TMDT BCTN25 - HTK - GV da ket chuyen.
So BCTC/hang so chep nguyen tch_r3.py (control: tai lap center_pre r3 16.346,8 tu calc_r3/tch_r3_out.json).
Chay: /home/trido/thanhdt/wc_venv/bin/python -I tch_r3b.py (2 lan, so md5); roi LOCK; roi tch_r3b_compare.py (doc gia)."""
import csv, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
WC = '/home/trido/thanhdt/WorkingClaude'; sys.path.insert(0, WC)
from deposit_rate_vn import effective_deposit_rate   # noqa: E402

A3 = {a['key']: a for a in json.load(open(os.path.join(BASE, 'calc_r3', 'assumptions_r3.json')))['assumptions']}
AB = {a['key']: a for a in json.load(open(os.path.join(HERE, 'assumptions_r3b.json')))['assumptions']}
R3O = json.load(open(os.path.join(BASE, 'calc_r3', 'tch_r3_out.json')))
ASOF = '2026-11-06'; R_ANCHOR, DEP_ANCHOR = 0.135, 0.074
DEP = effective_deposit_rate(ASOF); R0 = R_ANCHOR + 1.0 * (DEP['rate'] - DEP_ANCHOR)
# ---- so lieu BCTC (chep nguyen tch_r3.py; nguon notes_read.md) ----
SH = 1003.312808; VAT = 1.08
EQ_ME = 15279.65 - 3120.54; EQ_DIRECT = 10530.2 - 4571.6; EQ_SUBS = EQ_ME - EQ_DIRECT
G_OBS = A3['g_obs']['value']; GAX = list(zip(A3['g_axis']['value'], A3['g_axis']['w'])); RAX = list(zip(A3['r_axis']['value'], A3['r_axis']['w']))
SH_KHAC = A3['share_khac']['value']
HTK_ME = 759.57 + 2557.50 + 555.53 + 1677.51 + 1.71; HTK_CRV = 7390.37 + 1328.75; HTK_KHAC = 14630.92 - HTK_ME - HTK_CRV
# backlog (NMTT) theo du an: (NMTT, so huu, nam backlog, nhom)
BL = {"NC-II": (3099.20, 0.6802, 1.0, "sub"), "Green River": (1837.75, 1.0, 1.5, "me"), "H2": (617.83, 1.0, 2.0, "me"), "H1+khac": (38.15 + 6.88, SH_KHAC, 1.0, "sub")}
# dat cu chua ban theo du an: (HTK du an 30/09/26, NMTT tru ra, so huu, nhom)
OLD = {"Green River": (759.57 + 2557.50, 1837.75, 1.0, "me"), "H2": (555.53, 617.83, 1.0, "me"), "me_khac": (1.71, 0.0, 1.0, "me"),
       "NC-II": (7390.37, 3099.20, 0.6802, "sub"), "khac": (HTK_KHAC, 38.15 + 6.88, SH_KHAC, "sub")}
Y = AB['y_by_project']['value']; YP = {"Green River": Y["Green River"], "H2": Y["H2"], "NC-II": Y["NC-II"], "me_khac": 1.0, "khac": Y["khac (H1 TP da xong, Gold Tower, N01)"]}
TMDT = AB['TMDT']['value']; EXB = AB['expensed_bounds']['value']
KDAX = list(zip(AB['k_axis']['value'], AB['k_axis']['w']))
m_of = lambda g: 0.8 * (g - 0.10)
s_of = lambda g: 0.8 * (g - 0.10) / (1 - g)


def k_meas(p, which='mid'):
    if p not in TMDT:
        return 0.0
    htk = OLD[p][0]; lo, hi = EXB[p]; e = {'lo_exp': lo, 'hi_exp': hi, 'mid': (lo + hi) / 2}[which]
    return (TMDT[p] - htk - e) / (htk + e)


KC = {p: k_meas(p) for p in OLD}
K_RANGE = {p: (k_meas(p, 'hi_exp'), k_meas(p, 'lo_exp')) for p in TMDT}


def nav(gb, go, r=R0, mode='b', kd=0.0, kfix=None, yfix=None, exact=False, kc=None):
    """mode 'r3': chi thang du chiet khau pv(4) (tai lap r3). mode 'b': nhat quan gia von+thang du pv(y), chi phi tuong lai k*C tai y/2.
    kd: delta tren F (k_p*(1+kd)); kfix: k dong nhat moi du an dat cu (thay k do); yfix: y dong nhat (chi phi tuong lai tai yfix/2);
    exact: backlog chi chiem cost_bl/(1+k) trong HTK (C lon hon); kc: dict k thay KC."""
    pv = lambda y: 1 / (1 + r) ** y
    m, s = m_of(gb), s_of(go)
    kc = KC if kc is None else kc
    part = {"me": EQ_DIRECT, "sub": EQ_SUBS}
    for p, (n, sh, y, grp) in BL.items():
        part[grp] += n / VAT * m * sh * pv(y)
    for p, (htk, n, sh, grp) in OLD.items():
        cbl = n / VAT * (1 - G_OBS)
        if mode == 'r3':
            part[grp] += (htk - cbl) * s * sh * pv(4.0)
            continue
        k = (kc[p] * (1 + kd)) if kfix is None else kfix
        C = htk - (cbl / (1 + k) if exact else cbl)
        y = YP[p] if yfix is None else yfix
        part[grp] += sh * (C * (1 + k) * (1 + s) * pv(y) - k * C * pv(y / 2) - C)
    return (part["me"] + part["sub"]) / SH * 1000


mean = lambda v, w: sum(a * b for a, b in zip(v, w)) / sum(w)


def grid(corr=False, kax=None, **kw):
    """truc g backlog x g dat cu (doc lap; corr=True: cung mot rut) x r x truc k. kax: list (kd, w) hoac ('kfix', [(k, w)])."""
    kax = KDAX if kax is None else kax
    v, w, key = [], [], []
    gpairs = [((a, wa), (a, 1.0)) for a, wa in GAX] if corr else list(itertools.product(GAX, GAX))
    for ((db, wb), (do, wo)), (dr, wr), (kk, wk) in itertools.product(gpairs, RAX, kax):
        kwx = dict(kw); kwx.setdefault('kfix', None)
        if isinstance(kk, tuple):
            kwx['kfix'] = kk[1]; kd = 0.0
        else:
            kd = kk
        v.append(nav(G_OBS + db, G_OBS + do, R0 + dr, kd=kd, **kwx)); w.append(wb * wo * wr * wk)
        key.append(f'gbl{G_OBS + db:.3f}|gold{G_OBS + do:.3f}|dr{dr:+.3f}|k{kk if not isinstance(kk, tuple) else "fix" + str(kk[1])}')
    return v, w, key


K0 = [(0.0, 1.0)]
def kfix_ax(vals, wts):
    return [(('f', k), wt) for k, wt in zip(vals, wts)]


# ---- CONTROL ----
c_r3 = mean(*grid(kax=K0, mode='r3')[:2])
assert abs(c_r3 - R3O['center_pre']) < 0.05, (c_r3, R3O['center_pre'])
# ---- CAU r3 -> r3b (truoc CK, doc lap gia) ----
c_cons_y4 = mean(*grid(kax=kfix_ax([0.0], [1.0]), yfix=4.0)[:2])                 # skeptic: nhat quan, y=4, k=0
c_cons_yp = mean(*grid(kax=kfix_ax([0.0], [1.0]))[:2])                           # y theo moc hoan thanh, k=0
c_k_meas = mean(*grid(kax=[(0.0, 1.0)])[:2])                                     # + k do (tam), khong truc
V, W, KEY = grid()                                                               # HEADLINE: + truc k +-25% F
c_b = mean(V, W)
bridge_pre = [dict(step='r3 tai lap (control, tch_r3.py)', center_pre=c_r3),
              dict(step='nhat quan gia von+thang du, y=4 dong nhat, k=0 (dang skeptic)', center_pre=c_cons_y4),
              dict(step='y theo moc hoan thanh du an BCTN25 (GR 2,15; H2 1,15; NC-II 4,07; khac 1,0), k=0', center_pre=c_cons_yp),
              dict(step='+ k do tu TMDT (tam trung diem can GV da ket chuyen)', center_pre=c_k_meas),
              dict(step='+ truc F +-25% (k x 0,75/1/1,25) = HEADLINE r3b', center_pre=c_b)]
# skeptic check: +X d/cp moi 1,0 k (y=4, chi phi tai 2)
sk_slope = mean(*grid(kax=kfix_ax([1.0], [1.0]), yfix=4.0)[:2]) - c_cons_y4
par = {}
def P(name, desc, v, w):
    par[name] = dict(desc=desc, vals=v, wts=w, center_pre=mean(v, w))
P('r3_old', 'r3 cu (chi thang du chiet khau pv(4)) — song song theo yeu cau', *grid(kax=K0, mode='r3')[:2])
P('r3_old_corr_g', 'r3 cu, hai truc g TUONG QUAN HOAN TOAN', *grid(corr=True, kax=K0, mode='r3')[:2])
P('cons_y4_k0', 'nhat quan, y=4, k=0 (skeptic ~13.435 sau CK)', *grid(kax=kfix_ax([0.0], [1.0]), yfix=4.0)[:2])
P('cons_yp_k0', 'nhat quan, y du an, k=0 (khong tinh chi phi tuong lai)', *grid(kax=kfix_ax([0.0], [1.0]))[:2])
P('headline_corr_g', 'HEADLINE r3b nhung hai truc g TUONG QUAN HOAN TOAN', *grid(corr=True)[:2])
P('k_sym_0_02_04_06', 'nhat quan y du an + truc k doi xung {0;0,2;0,4;0,6} deu (fallback khi chua do)', *grid(kax=kfix_ax(AB['k_sym_fallback_parallel']['value'], AB['k_sym_fallback_parallel']['w']))[:2])
P('k_sym_y4', 'nhat quan y=4 + truc k {0;0,2;0,4;0,6}', *grid(kax=kfix_ax(AB['k_sym_fallback_parallel']['value'], AB['k_sym_fallback_parallel']['w']), yfix=4.0)[:2])
P('k_meas_y4', 'k do + truc F, nhung y=4 dong nhat (quy uoc skeptic/r2)', *grid(yfix=4.0)[:2])
P('k_lo', 'k can duoi (GV da ket chuyen o can tren) + truc F', *grid(kc={p: (K_RANGE[p][0] if p in K_RANGE else 0.0) for p in OLD})[:2])
P('k_hi', 'k can tren (chua ket chuyen GV nao) + truc F', *grid(kc={p: (K_RANGE[p][1] if p in K_RANGE else 0.0) for p in OLD})[:2])
P('k_H2_cap1', 'k H2 chan 1,0 (H2 "xong tho" ma HTK chi 25% TMDT — nghi TMDT H2 gom dat/hang muc da ghi o H1) + truc F', *grid(kc={**KC, 'H2': 1.0})[:2])
P('exact_C', 'dang chinh xac: backlog chi chiem cost_bl/(1+k) trong HTK (C chua ban lon hon)', *grid(exact=True)[:2])
def grid_g(g0, kd_ax, **kw):
    vv, ww = [], []
    for (a, wa), (b, wb), (c, wc), (d, wd) in itertools.product(GAX, GAX, RAX, kd_ax):
        vv.append(nav(g0 + a, g0 + b, R0 + c, kd=d, **kw)); ww.append(wa * wb * wc * wd)
    return vv, ww


G_AUD = AB['g_audit_parallel']['value']
P('g_audit_427', 'g ca hai truc 42,7% +-5pp (BCTC kiem toan FY24/FY25 mang BDS) + k do + truc F', *grid_g(G_AUD, KDAX))
P('g_audit_427_k0', 'g 42,7% +-5pp + nhat quan y du an, k=0 (can duoi ket hop)', *grid_g(G_AUD, K0, kfix=0.0))
cp = nav(G_OBS, G_OBS)
O = dict(ticker='TCH', round='3b', asof=ASOF, r=R0, dep=DEP, sh=SH, eq_me=EQ_ME, bvps=EQ_ME / SH * 1000, n_outcomes=len(V), center_pre=c_b, center_param_pre=cp,
         control_r3_center_pre=c_r3, r3_center_pre_file=R3O['center_pre'], k_center=KC, k_range=K_RANGE, y_by_project=YP,
         C_unsold_by_project={p: htk - n / VAT * (1 - G_OBS) for p, (htk, n, sh, grp) in OLD.items()},
         C_unsold_me_share=sum(sh * (htk - n / VAT * (1 - G_OBS)) for p, (htk, n, sh, grp) in OLD.items()),
         k_weighted_me_share=sum(KC[p] * OLD[p][2] * (OLD[p][0] - OLD[p][1] / VAT * (1 - G_OBS)) for p in OLD) / sum(sh * (htk - n / VAT * (1 - G_OBS)) for p, (htk, n, sh, grp) in OLD.items()),
         skeptic_slope_per_k_pre=sk_slope, bridge_pre=bridge_pre, outcomes_vals=V, outcomes_wts=W, outcomes_keys=KEY, parallel=par)
json.dump(O, open(os.path.join(HERE, 'tch_r3b_out.json'), 'w'), indent=1, sort_keys=True, default=float)
with open(os.path.join(HERE, 'grid_tch_r3b.csv'), 'w', newline='') as f:
    cw = csv.writer(f); cw.writerow(['key', 'value_pre', 'weight'])
    for k, v, w in zip(KEY, V, W):
        cw.writerow([k, f'{v:.4f}', f'{w:.6f}'])
with open(os.path.join(HERE, 'tch_r3b_out.txt'), 'w') as f:
    print(f"r {R0:.4%}; CONTROL r3 center_pre {c_r3:,.2f} (file {R3O['center_pre']:,.2f})", file=f)
    print(f"C chua ban phan me {O['C_unsold_me_share']:,.1f}; k tam theo du an {json.dumps({p: round(v, 4) for p, v in KC.items()})}; k range {json.dumps({p: [round(a, 4), round(b, 4)] for p, (a, b) in K_RANGE.items()})}; k binh quan (trong so C me) {O['k_weighted_me_share']:.4f}", file=f)
    print(f"skeptic doc: +{sk_slope:,.1f} d/cp (truoc CK) moi 1,0 k (y=4, chi phi y=2)", file=f)
    for b in bridge_pre:
        print(f"bridge {b['step']}: {b['center_pre']:,.1f}", file=f)
    print(f"R3b n={len(V)} center_pre {c_b:,.1f}; tham so trung tam {cp:,.1f}; min {min(V):,.1f} max {max(V):,.1f}", file=f)
    for k, v in par.items():
        print(f"song song {k}: center_pre {v['center_pre']:,.1f} (n={len(v['vals'])}) — {v['desc']}", file=f)
print(open(os.path.join(HERE, 'tch_r3b_out.txt')).read())
