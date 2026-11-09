"""TCH — DD REDO VONG 3 (job Taylor_20261108_180134). Ap dinh chinh fundamental-skeptic (TOP5D_CORRECTIONS_20261108.md muc TCH).
Mo hinh = NAV me r2 (VCSH me + thang du backlog NMTT + thang du dat cu chua ban; quy dat moi NPV0) — KHONG doc gia.
So BCTC giu nguyen r1/r2 (dd_TCH_20261031/calc/notes_read.md). Gia dinh khoa o assumptions_r3.json.
Buoc 1 CONTROL: tai lap center_pre r2 13.857 (model_r2_out.json) + hold_0 skeptic. Buoc 2 luoi r3. Buoc 3 song song.
Chay: /home/trido/thanhdt/wc_venv/bin/python -I tch_r3.py (2 lan, so md5); roi LOCK; roi tch_r3_compare.py (doc gia)."""
import csv, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
WC = '/home/trido/thanhdt/WorkingClaude'; sys.path.insert(0, WC)
from deposit_rate_vn import effective_deposit_rate   # noqa: E402

A = {a['key']: a for a in json.load(open(os.path.join(HERE, 'assumptions_r3.json')))['assumptions']}
ASOF = '2026-11-06'; R_ANCHOR, DEP_ANCHOR = 0.135, 0.074
DEP = effective_deposit_rate(ASOF); R0 = R_ANCHOR + 1.0 * (DEP['rate'] - DEP_ANCHOR)
# ---- so lieu BCTC (copy nguyen model_r2.py; nguon notes_read.md) ----
SH = 1003.312808; VAT = 1.08
EQ_ME = 15279.65 - 3120.54; EQ_DIRECT = 10530.2 - 4571.6; EQ_SUBS = EQ_ME - EQ_DIRECT
PROJ = {"NC-II": (3099.20, 0.6802, 1.0, "crv"), "Green River": (1837.75, 1.0, 1.5, "me"), "H2": (617.83, 1.0, 2.0, "me"), "H1+khac": (38.15 + 6.88, None, 1.0, "khac")}
HTK = {"me": 759.57 + 2557.50 + 555.53 + 1677.51 + 1.71, "crv": 7390.37 + 1328.75}; HTK["khac"] = 14630.92 - HTK["me"] - HTK["crv"]
NEW = {"me": 1677.51, "crv": 1328.75}; SGTL = 678.3; INT_6M = 173.51; CASH_ME = 2960.0
NP_TTM_BQ = (537.726548424 + 125.4169214 + 80.548446343 + 52.42516578)      # BQ ticker_financial 2026Q3 NP_P0..P3 (fin_tch_r3.csv)
NP_NORM_R2 = 725 * SH / 1000
G_OBS = A['g_obs']['value']; GAX = list(zip(A['g_axis']['value'], A['g_axis']['w'])); RAX = list(zip(A['r_axis']['value'], A['r_axis']['w']))
m_of = lambda g: 0.8 * (g - 0.10)
s_of = lambda g: 0.8 * (g - 0.10) / (1 - g)


def nav(m, s_old, hold=0.0, r=R0, gov=0.0, s_new=0.0, loss=0.0, sh_khac=A['share_khac']['value'], m_cost_gm=None):
    """m: bien rong backlog tren DT truoc VAT. m_cost_gm: neu khac None, gia von backlog tinh theo GM nay (r2: GM 0,519 co dinh)."""
    pv = lambda y: 1 / (1 + r) ** y
    gm_cost = G_OBS if m_cost_gm is None else m_cost_gm
    share = {"crv": 0.6802, "me": 1.0, "khac": sh_khac}
    cost_bl = {"me": 0.0, "crv": 0.0, "khac": 0.0}
    bl = {"me": 0.0, "sub": 0.0}
    for k, (n, _, y, g) in PROJ.items():
        cost_bl[g] += n / VAT * (1 - gm_cost)
        bl["me" if g == "me" else "sub"] += n / VAT * m * share[g] * pv(y)
    rest = {k: HTK[k] - cost_bl[k] - NEW.get(k, 0.0) for k in HTK}
    sur_me = (rest["me"] * s_old + NEW["me"] * s_new) * pv(4)
    sur_sub = ((rest["crv"] * s_old + NEW["crv"] * s_new) * share["crv"] + rest["khac"] * s_old * share["khac"]) * pv(4)
    direct = EQ_DIRECT + bl["me"] + sur_me - loss; subs = EQ_SUBS + bl["sub"] + sur_sub
    return (direct + subs * (1 - hold)) * (1 - gov) / SH * 1000


def grid_r3(hold_ax=((0.0, 1.0),), **kw):
    v, w, k = [], [], []
    for (dgb, wb), (dgo, wo), (dr, wr), (h, wh) in itertools.product(GAX, GAX, RAX, hold_ax):
        gb, go = G_OBS + dgb, G_OBS + dgo
        v.append(nav(m_of(gb), s_of(go), h, R0 + dr, **kw)); w.append(wb * wo * wr * wh); k.append(f'gbl{gb:.3f}|gold{go:.3f}|dr{dr:+.3f}|h{h:.2f}')
    return v, w, k


def grid_r2(hs=((0.0, 0.10, 0.20, 0.30), (0.25,) * 4), ss=((0.25, 0.40, 0.55), (0.25, 0.5, 0.25)), ms=(0.30, 0.335, 0.36)):
    v, w = [], []
    W3 = (0.25, 0.5, 0.25)
    for (m, wm), (s, ws), (h, wh), (rr, wr) in itertools.product(zip(ms, W3), zip(*ss), zip(*hs), zip((R0 - 0.01, R0, R0 + 0.01), W3)):
        v.append(nav(m, s, h, rr)); w.append(wm * ws * wh * wr)
    return v, w


mean = lambda v, w: sum(a * b for a, b in zip(v, w)) / sum(w)
r2o = json.load(open(os.path.join(BASE, 'calc', 'model_r2_out.json')))
c_r2 = mean(*grid_r2())
c_h0 = mean(*grid_r2(hs=((0.0,), (1.0,))))
# cau r2 -> r3 (truoc CK, gia-doc-lap)
gs = [(G_OBS + d, wt) for d, wt in GAX]
c_s_cons = mean(*grid_r2(hs=((0.0,), (1.0,)), ss=(tuple(s_of(g) for g, _ in gs), tuple(wt for _, wt in gs))))
V, W, K = grid_r3()
c_r3 = mean(V, W)
bridge_pre = [dict(step='r2 tai lap (control)', center_pre=c_r2),
              dict(step='dinh chinh 1: CK holding -> base 0% (truc sang song song)', center_pre=c_h0),
              dict(step='dinh chinh 2a: thang du dat cu nhat quan voi g quan sat (s=s(g), g 51,9% +-5pp)', center_pre=c_s_cons),
              dict(step='dinh chinh 2b/3: backlog m=m(g) cung truc g doi xung +-5pp (r2 0,30/0,335/0,36 lech)', center_pre=c_r3)]
cp = nav(m_of(G_OBS), s_of(G_OBS))
par = {}
def P(name, desc, v, w):
    par[name] = dict(desc=desc, vals=v, wts=w, center_pre=mean(v, w))
H4 = tuple(zip((0.0, 0.10, 0.20, 0.30), (0.25,) * 4)); H3 = tuple(zip((0.10, 0.20, 0.30), (1 / 3,) * 3))
P('hold_0_10_20_30', 'r3 + truc CK holding {0;10;20;30} deu (r2)', *grid_r3(hold_ax=H4)[:2])
P('hold_r1_10_20_30', 'r3 + CK holding {10;20;30} deu (r1, ky vong 20%)', *grid_r3(hold_ax=H3)[:2])
P('hold_27', 'r3 + CK holding 27% co dinh (tham chieu HHS)', *grid_r3(hold_ax=((0.27, 1.0),))[:2])
for gv in (0.05, 0.10, 0.15):
    P(f'gov_{int(gv*100)}', f'r3 + CK quan tri {gv:.0%}', *grid_r3(gov=gv)[:2])
P('sgtl_loss_100', 'stress mat 100% tien gui SGTL 678,3 (can duoi cuc doan)', *grid_r3(loss=SGTL)[:2])
P('new_land_m10', 'quy dat moi -10%', *grid_r3(s_new=-0.10)[:2]); P('new_land_p10', 'quy dat moi +10%', *grid_r3(s_new=0.10)[:2])
P('share_khac_050', 'so huu H1+khac 0,50', *grid_r3(sh_khac=0.50)[:2]); P('share_khac_100', 'so huu H1+khac 1,00', *grid_r3(sh_khac=1.00)[:2])
# ca hai ve g nganh 40% (chieu xuong cua 'nhat quan') ; skeptic {40;55;70} va {55;70;85}; backlog 40%
vv, ww = [], []
for (dgb, wb), (dgo, wo), (dr, wr) in itertools.product(GAX, GAX, RAX):
    vv.append(nav(m_of(0.40 + dgb), s_of(0.40 + dgo), 0.0, R0 + dr)); ww.append(wb * wo * wr)
P('both_g40', 'ca backlog va dat cu o g 40% (+-5pp) — chieu xuong, khong co du lieu', vv, ww)
P('skeptic_s_40_55_70', 'skeptic: hold 0, m r2, s {40;55;70}', *grid_r2(hs=((0.0,), (1.0,)), ss=((0.40, 0.55, 0.70), (0.25, 0.5, 0.25))))
P('skeptic_s_55_70_85', 'skeptic: hold 0, m r2, s {55;70;85}', *grid_r2(hs=((0.0,), (1.0,)), ss=((0.55, 0.70, 0.85), (0.25, 0.5, 0.25))))
P('skeptic_bl_g40', 'skeptic: hold 0, s r2, backlog m=m(40%)', *grid_r2(hs=((0.0,), (1.0,)), ms=(m_of(0.40),) * 3))
P('r2_s_40_keep', 'r3 nhung giu s r2 {25;40;55} (khong nhat quan)', *grid_r2(hs=((0.0,), (1.0,)), ss=((0.25, 0.40, 0.55), (0.25, 0.5, 0.25)), ms=tuple(m_of(g) for g, _ in gs)))
r_sens = {f'{d:+.0%}': mean(*grid_r3()[:2]) if d == 0 else mean([nav(m_of(G_OBS + a), s_of(G_OBS + b), 0.0, R0 + d + c) for (a, _), (b, _), (c, _) in itertools.product(GAX, GAX, RAX)],
                                                                   [x * y * z for (_, x), (_, y), (_, z) in itertools.product(GAX, GAX, RAX)]) for d in (-0.01, 0.0, 0.01)}
bvps = EQ_ME / SH * 1000; int_at = INT_6M * 2 * 0.80
gx = {}
for lab, npv in (('TTM_BQ_796', NP_TTM_BQ), ('norm_r2_727_UL', NP_NORM_R2)):
    roe_a = npv / EQ_ME; roe_b = (npv - int_at) / (EQ_ME - CASH_ME)
    gx[lab] = dict(np=npv, roe_co_lai=roe_a, A_co_lai=bvps * (roe_a - 0.03) / (R0 - 0.03),
                   roe_khong_lai=roe_b, B_khong_lai_cong_tien=((EQ_ME - CASH_ME) * (roe_b - 0.03) / (R0 - 0.03) + CASH_ME) / SH * 1000)
O = dict(ticker='TCH', round=3, asof=ASOF, r=R0, dep=DEP, sh=SH, eq_me=EQ_ME, bvps=bvps, n_outcomes=len(V), center_pre=c_r3, center_param_pre=cp,
         g_obs=G_OBS, s_center=s_of(G_OBS), m_center=m_of(G_OBS), control_r2_center_pre=c_r2, r2_center_pre_file=r2o['grid']['center_pre'],
         control_hold0_center_pre=c_h0, r2_hold0_center_pre_file=r2o['parallel']['hold_0 (khong CK holding)']['center_pre'],
         bridge_pre=bridge_pre, outcomes_vals=V, outcomes_wts=W, outcomes_keys=K, parallel=par, r_sens_pre=r_sens, gordon_roe_xcheck=gx,
         book_share_of_center=bvps / c_r3)
assert abs(c_r2 - r2o['grid']['center_pre']) < 0.5, (c_r2, r2o['grid']['center_pre'])
json.dump(O, open(os.path.join(HERE, 'tch_r3_out.json'), 'w'), indent=1, sort_keys=True, default=float)
with open(os.path.join(HERE, 'grid_tch_r3.csv'), 'w', newline='') as f:
    cw = csv.writer(f); cw.writerow(['key', 'value_pre', 'weight'])
    for k, v, w in zip(K, V, W):
        cw.writerow([k, f'{v:.4f}', f'{w:.6f}'])
with open(os.path.join(HERE, 'tch_r3_out.txt'), 'w') as f:
    print(f"r {R0:.4%} (dep {DEP['rate']:.2%} {DEP['rate_source']}); VCSH me {EQ_ME:,.1f} = {bvps:,.0f} d/cp ({bvps/c_r3:.1%} tam)", file=f)
    print(f"CONTROL r2 center_pre {c_r2:,.1f} (file {r2o['grid']['center_pre']:,.1f}); hold0 {c_h0:,.1f} (file {O['r2_hold0_center_pre_file']:,.1f})", file=f)
    for b in bridge_pre:
        print(f"bridge {b['step']}: {b['center_pre']:,.1f}", file=f)
    print(f"R3 n={len(V)} center_pre {c_r3:,.1f}; tham so trung tam (g 51,9% ca hai, s {s_of(G_OBS):.3f}, m {m_of(G_OBS):.4f}) {cp:,.1f}; min {min(V):,.1f} max {max(V):,.1f}", file=f)
    for k, v in par.items():
        print(f"song song {k}: center_pre {v['center_pre']:,.1f} (n={len(v['vals'])}) — {v['desc']}", file=f)
    print('r_sens_pre ' + json.dumps({k: round(v, 1) for k, v in r_sens.items()}), file=f)
    for k, v in gx.items():
        print(f"gordon {k}: LN {v['np']:.1f} ROE co lai {v['roe_co_lai']:.2%} => {v['A_co_lai']:,.0f}; khong lai {v['roe_khong_lai']:.2%} + tien => {v['B_khong_lai_cong_tien']:,.0f}", file=f)
print(open(os.path.join(HERE, 'tch_r3_out.txt')).read())
