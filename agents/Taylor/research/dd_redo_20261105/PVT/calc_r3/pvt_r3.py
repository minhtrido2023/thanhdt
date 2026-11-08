"""PVT — DD REDO VONG 3 (job Taylor_20261108_153736). Ap dinh chinh fundamental-skeptic 08/11 (TOP5B_CORRECTIONS_20261108.md muc PVT).
Mo hinh = FCFE co dong me r1/r2 (Q4/2026 + LN me 2027 + terminal ROE giua chu ky x VCSH me, g 3%) + truc mua tau (r2). KHONG doc gia.
Gia dinh khoa o assumptions_r3.json. Dau vao du lieu: ../calc/model.py (ROE_MID, Q3_NP, SH tu bq_hist_out.csv) — import, khong sua.
Buoc 1 (CONTROL): cau hinh r2 tai lap center_pre model_r2_out.json. Buoc 2: luoi r3. Buoc 3: do nhay song song.
Chay: python3 -I pvt_r3.py  (2 lan, so md5 output) ; sau do lock_r3.sh ; roi pvt_r3_compare.py (doc gia)."""
import csv, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WC = '/home/trido/thanhdt/WorkingClaude'
sys.path.insert(0, os.path.join(HERE, '..', 'calc')); sys.path.insert(0, WC)
import model as M1                                   # noqa: E402  (vong 1, chi lay du lieu)
from deposit_rate_vn import effective_deposit_rate   # noqa: E402

A = {a['key']: a['value'] for a in json.load(open(os.path.join(HERE, 'assumptions_r3.json')))['assumptions']}
ASOF = '2026-11-06'; ANCHOR_DATE = '2026-11-03'; R_ANCHOR = 0.135
D0 = effective_deposit_rate(ANCHOR_DATE)['rate']; D1 = effective_deposit_rate(ASOF)['rate']
R0 = R_ANCHOR + 1.0 * (D1 - D0)
SH, EQ, Q3_NP, ROE_MID = M1.SH, A['eq_parent'], M1.Q3_NP, M1.ROE_MID
assert abs(EQ - M1.EQ_PARENT) < 1e-9
G = A['g']; MULTS = tuple(A['mults']); NCI = A['nci']
BUY_AMT = {'mua_phan_con_lai': 3445.0 - 979.6, 'khong': 0.0}
NI = A['net_interest_9t']
NET_INT_PARENT_YR = (NI['lai_tien_gui_cho_vay'] - NI['chi_phi_lai_vay']) * 4 / 3 * (1 - 0.20) * (1 - NCI)   # am = chi phi rong
DEP_PARENT_YR = NI['lai_tien_gui_cho_vay'] * 4 / 3 * (1 - 0.20) * (1 - NCI)                                 # cach r2 (mot chieu)

R3 = dict(w=A['scn_w'], mid=A['scn_mid'], np27=A['np27'], npv=A['ship_npv'], buy=A['ship_buy'], roe_mid=ROE_MID, r_axis=A['r_axis'], adj=0.0)
R2CFG = dict(R3, w={'xau': 0.35, 'coso': 0.45, 'tot': 0.20}, mid={'xau': 0.85, 'coso': 1.0, 'tot': 1.1},
             np27={'xau': 1000.0, 'coso': 1250.0, 'tot': 1500.0})


def value_ps(s, m, r, b, cfg):
    roe = cfg['roe_mid'] * cfg['mid'][s] * m
    reinv = 1 - G / max(roe, 1e-9)
    v = Q3_NP / (1 + r) ** 0.125 + cfg['np27'][s] * reinv / (1 + r) ** 0.75
    v += roe * EQ * (1 + G) * reinv / (r - G) / (1 + r) ** 1.25
    v += cfg['npv'][s] * BUY_AMT[b] * (1 - NCI) + cfg['adj']
    return v * 1e9 / SH


def grid(cfg, r_base=None):
    rb = R0 if r_base is None else r_base; vals, wts, keys = [], [], []
    for s, m, (dr, rw), b in itertools.product(('xau', 'coso', 'tot'), MULTS, cfg['r_axis'], ('mua_phan_con_lai', 'khong')):
        vals.append(value_ps(s, m, rb + dr, b, cfg)); wts.append(cfg['w'][s] / len(MULTS) * rw * cfg['buy'][b])
        keys.append(f'{s}|m{m}|dr{dr:+.3f}|{b}')
    return vals, wts, keys


def mean(v, w):
    return sum(a * b for a, b in zip(v, w)) / sum(w)


def center(cfg, r_base=None):
    v, w, _ = grid(cfg, r_base); return mean(v, w)


def variants():
    sk1450 = dict(R3, np27={'xau': 1200.0, 'coso': 1450.0, 'tot': 1700.0})
    plan_parent = (6750.0 - 1581.8 * 4 / 3) / 4 * (1 - NCI); roe_plan = plan_parent / EQ
    plan = dict(R3, roe_mid=roe_plan, np27={k: plan_parent * v / A['np27']['coso'] for k, v in A['np27'].items()})
    exnet = dict(R3, roe_mid=ROE_MID - NET_INT_PARENT_YR / EQ, adj=-A['net_debt'] * (1 - NCI))
    return {
        'bobby_asym': (dict(R3, w=R2CFG['w'], mid=R2CFG['mid']), 'trong so 0,35/0,45/0,20 + he so ROE 0,85/1/1,1 (nhan dinh Bobby, r2) tren np27 r3'),
        'w_asym_only': (dict(R3, w=R2CFG['w']), 'chi trong so lech xuong 0,35/0,45/0,20'),
        'mid_asym_only': (dict(R3, mid=R2CFG['mid']), 'chi he so ROE lech xuong 0,85/1/1,1'),
        'np27_skeptic_1450': (sk1450, 'np27 1.200/1.450/1.700 (de xuat skeptic)'),
        'np27_r2_1250_sym': (dict(R3, np27=R2CFG['np27']), 'np27 r2 1.000/1.250/1.500 voi trong so/he so doi xung (skeptic 18.506)'),
        'w_sym_only_r2np': (dict(R2CFG, w=R3['w']), 'skeptic kiem: chi doi xung trong so, con lai r2 (18.212)'),
        'mid_sym_only_r2np': (dict(R2CFG, mid=R3['mid']), 'skeptic kiem: chi doi xung he so, con lai r2 (18.050)'),
        'ship_npv0': (dict(R3, npv={'xau': 0.0, 'coso': 0.0, 'tot': 0.0}), 'NPV tau moi = 0 moi kich ban'),
        'plan_anchor': (plan, f'neo ke hoach 5 nam NQ HDQT: LN me/nam {plan_parent:.0f} ty, ROE {roe_plan:.2%}'),
        'roe_ex_net_interest': (exnet, f'ROE bo lai RONG (lai gui 251,0 - lai vay 345,6 /9T => {NET_INT_PARENT_YR:.0f} ty/nam phan me, ROE {ROE_MID - NET_INT_PARENT_YR / EQ:.2%}) va tru no rong phan me 619,3x(1-NCI)'),
    }


if __name__ == '__main__':
    r2o = json.load(open(os.path.join(HERE, '..', 'calc', 'model_r2_out.json')))
    ctrl = center(R2CFG, r_base=0.135)
    assert abs(ctrl - r2o['center_pre']) < 0.5, (ctrl, r2o['center_pre'])
    vals, wts, keys = grid(R3)
    cp = value_ps('coso', 1.0, R0, 'khong', R3)
    par = {}
    for k, (cfg, desc) in variants().items():
        v, w, _ = grid(cfg); par[k] = dict(desc=desc, vals=v, wts=w, center_pre=mean(v, w))
    bridge_cfgs = [('r2 (tai lap)', R2CFG), ('+ trong so doi xung 0,275/0,45/0,275', dict(R2CFG, w=R3['w'])),
                   ('+ he so ROE doi xung 0,9/1/1,1', dict(R2CFG, w=R3['w'], mid=R3['mid'])),
                   ('+ np27 co so 1.500 (Q3x4) +-250 = r3', R3)]
    bridge = [dict(step=n, center_pre=center(c)) for n, c in bridge_cfgs]
    sens_r = {f'{bp:+d}bp': center(R3, r_base=R0 + bp / 1e4) for bp in (-100, -50, 50, 100)}
    sc = {f'{s}|{b}': value_ps(s, 1.0, R0, b, R3) for s in ('xau', 'coso', 'tot') for b in BUY_AMT}
    bvps = EQ * 1e9 / SH
    gx = dict(roe_mid_incl=ROE_MID, roe_mid_ex_net_interest=ROE_MID - NET_INT_PARENT_YR / EQ, net_interest_parent_yr=NET_INT_PARENT_YR,
              dep_only_parent_yr_r2=DEP_PARENT_YR, roe_ex_deposit_only_r2=ROE_MID - DEP_PARENT_YR / EQ,
              gordon_ps_incl=bvps * (ROE_MID - G) / (R0 - G), bvps=bvps,
              note='lai rong am (chi phi lai vay > lai gui) => bo lai tien gui mot chieu (r2) keo ROE xuong sai chieu; bo lai RONG nang ROE nhung phai tru no rong')
    out = dict(ticker='PVT', round=3, r=R0, dep_anchor=D0, dep_asof=D1, control_r2_center_pre=ctrl, r2_center_pre_file=r2o['center_pre'],
               center_pre=mean(vals, wts), center_param_pre=cp, outcomes_vals=vals, outcomes_wts=wts, outcomes_keys=keys,
               parallel=par, bridge_pre=bridge, r_sens_pre=sens_r, scenarios_pre=sc, gordon_roe_xcheck=gx,
               ship_npv_expected_pre=sum(R3['w'][s] * R3['npv'][s] for s in R3['w']) * 0.5 * BUY_AMT['mua_phan_con_lai'] * (1 - NCI) * 1e9 / SH)
    json.dump(out, open(os.path.join(HERE, 'pvt_r3_out.json'), 'w'), indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, 'grid_pvt_r3.csv'), 'w', newline='') as f:
        wr = csv.writer(f); wr.writerow(['key', 'value_pre', 'weight'])
        for k, v, w in zip(keys, vals, wts):
            wr.writerow([k, f'{v:.4f}', f'{w:.8f}'])
    with open(os.path.join(HERE, 'pvt_r3_out.txt'), 'w') as f:
        print(f'r={R0:.4f} dep03/11={D0:.4f} dep06/11={D1:.4f} control_r2={ctrl:.2f} (file {r2o["center_pre"]:.2f})', file=f)
        print(f'center_pre={out["center_pre"]:.0f} center_param_pre={cp:.0f} n={len(vals)} ship_npv_expected_pre={out["ship_npv_expected_pre"]:.2f}', file=f)
        for b in bridge:
            print(f'bridge {b["step"]}: {b["center_pre"]:.0f}', file=f)
        for k, p in par.items():
            print(f'parallel {k}: {p["center_pre"]:.0f} | {p["desc"]}', file=f)
        print('r_sens_pre', json.dumps({k: round(v) for k, v in sens_r.items()}), file=f)
        print('scenarios_pre', json.dumps({k: round(v) for k, v in sc.items()}), file=f)
        print('gordon', json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in gx.items()}, ensure_ascii=False), file=f)
    print(open(os.path.join(HERE, 'pvt_r3_out.txt')).read())
