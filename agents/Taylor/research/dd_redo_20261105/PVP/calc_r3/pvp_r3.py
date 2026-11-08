"""PVP — DD REDO VONG 3 (job Taylor_20261108_164335). Ap dinh chinh fundamental-skeptic 08/11 (TOP5C_CORRECTIONS_20261108.md muc PVP).
Mo hinh = SOTP dong tien r1/r2: tien rong sau co tuc + VLD khac (MOI) + FSO hop dong + nien kim doi tau theo tuoi doi - du phong sua chua - chi phi cong ty + NPV tau moi.
KHONG doc gia. Gia dinh khoa o assumptions_r3.json; hang so BCTC import tu ../calc/model.py (khong sua).
Buoc 1 (CONTROL): cau hinh r2 tai lap center_pre ../calc/model_r2_out.json. Buoc 2: cau noi tung buoc r2->r3. Buoc 3: luoi r3. Buoc 4: bien the song song.
Chay: python3 -I pvp_r3.py (2 lan, so md5) ; LOCK ; roi pvp_r3_compare.py (doc gia)."""
import csv, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WC = '/home/trido/thanhdt/WorkingClaude'
sys.path.insert(0, os.path.join(HERE, '..', 'calc')); sys.path.insert(0, os.path.join(HERE, '..', '..', '_common_014127')); sys.path.insert(0, WC)
import model as M1                                   # noqa: E402  (vong 1: hang so BCTC + fso_pv + annuity)
from deposit_rate_vn import effective_deposit_rate   # noqa: E402

A = {a['key']: a['value'] for a in json.load(open(os.path.join(HERE, 'assumptions_r3.json')))['assumptions']}
ASOF = '2026-11-06'; ANCHOR_DATE = '2026-11-03'; R_ANCHOR = 0.135
D0 = effective_deposit_rate(ANCHOR_DATE)['rate']; D1 = effective_deposit_rate(ASOF)['rate']
R0 = R_ANCHOR + 1.0 * (D1 - D0)
SCNS = ('xau', 'coso', 'tot'); BUYS = ('ca_hai', 'chi_2', 'khong'); FSOX = ('thanh_tien', 'khong')
BUY = {k: dict(w=v[0], usd=v[1]) for k, v in A['ship_buy'].items()}
R3 = dict(w=A['scn_w'], ebitda=A['ebitda'], npv=A['ship_npv'], fso_mode='r', fso_spread=None, nwc=A['nwc_other'], r_axis=[tuple(x) for x in A['r_axis']],
          fso_w=A['fso_excess'], drop_fso_gt5=False, ebitda_k=1.0, scrap_usd=0.0)
R2CFG = dict(R3, w={'xau': 0.40, 'coso': 0.45, 'tot': 0.15}, npv={'xau': -0.30, 'coso': 0.0, 'tot': 0.30}, fso_mode='dep_spread', fso_spread=M1.SPREAD_FSO, nwc=0.0)
assert A['ebitda'] == {s: M1.SCN[s]['ebitda'] for s in SCNS} and A['lives'] == list(M1.LIVES) and A['vcb'] == 26.04 and A['corp_years'] == M1.CORP_YEARS


def fso_rate(r, cfg):
    if cfg['fso_mode'] == 'r':
        return r
    if cfg['fso_mode'] == 'fixed':
        return cfg['fso_spread'] + (r - R0)          # muc co dinh, dich cung truc r
    return r - R_ANCHOR + D0 + cfg['fso_spread']      # cach r1/r2: lai huy dong neo + spread


def fso_pv(rr, excess, drop_gt5):
    if not drop_gt5:
        return M1.fso_pv(rr, excess)
    keep = M1.FSO_GT5; M1.FSO_GT5 = 0.0
    try:
        return M1.fso_pv(rr, excess)
    finally:
        M1.FSO_GT5 = keep


def parts(s, n, r, b, fx, cfg):
    e = cfg['ebitda'][s] * cfg['ebitda_k']
    return dict(net_cash_after_div=M1.CASH + M1.HTM - M1.DEBT_ST - M1.DEBT_LT - M1.DIV_PAY,
                nwc_other=cfg['nwc'],
                fso=fso_pv(fso_rate(r, cfg), fx == 'thanh_tien', cfg['drop_fso_gt5']),
                tankers=M1.annuity(e * (1 - M1.TAX * A['tax_shield_frac']), n, r),
                drydock=-M1.DRYDOCK,
                corp=-M1.annuity(M1.QLDN_9T * 4 / 3 * (1 - M1.TAX), M1.CORP_YEARS, r),
                ships_new=cfg['npv'][s] * BUY[b]['usd'] * A['vcb'],
                scrap=cfg['scrap_usd'] * A['vcb'] / (1 + r) ** n)


def value_ps(s, n, r, b, fx, cfg):
    return sum(parts(s, n, r, b, fx, cfg).values()) * 1e9 / M1.SH


def grid(cfg, r_base=None):
    rb = R0 if r_base is None else r_base; vals, wts, keys = [], [], []
    for s, n, (dr, rw), b, fx in itertools.product(SCNS, M1.LIVES, cfg['r_axis'], BUYS, FSOX):
        vals.append(value_ps(s, n, rb + dr, b, fx, cfg))
        wts.append(cfg['w'][s] / len(M1.LIVES) * rw * BUY[b]['w'] * cfg['fso_w'][fx]); keys.append(f'{s}|n{n}|dr{dr:+.3f}|{b}|fso_{fx}')
    return vals, wts, keys


def mean(v, w):
    return sum(a * b for a, b in zip(v, w)) / sum(w)


def center(cfg, r_base=None):
    v, w, _ = grid(cfg, r_base); return mean(v, w)


def variants():
    return {
        'bobby_asym': (dict(R3, w=R2CFG['w']), 'trong so cuoc lech xuong 0,40/0,45/0,15 (nhan dinh Bobby, r2), con lai r3'),
        'ship_pm30_sym': (dict(R3, npv=R2CFG['npv']), 'NPV tau moi +-30% doi xung theo cuoc (r2), trong so doi xung (skeptic: 24.060 truoc VLD/FSO-r)'),
        'ship_npv0': (dict(R3, npv={s: 0.0 for s in SCNS}), 'NPV tau moi = 0 moi kich ban (luat 03/11 thuan)'),
        'ship_m30_uncond': (dict(R3, npv={s: -0.30 for s in SCNS}), 'NPV tau moi -30% VO DIEU KIEN (nhat quan khung chiet khau du an o Ke 13,5% voi IRR 7,67%: nien kim 20 nam -32%)'),
        'fso_r10': (dict(R3, fso_mode='dep_spread', fso_spread=M1.SPREAD_FSO), 'FSO chiet khau = lai huy dong + 2,6pp (10%, r1/r2) — khong nguon'),
        'fso_excess_always': (dict(R3, fso_w={'thanh_tien': 1.0, 'khong': 0.0}), '177 ty FSO nam 1 luon thanh tien (o luoi, KHONG phai tam)'),
        'fso_excess_never': (dict(R3, fso_w={'thanh_tien': 0.0, 'khong': 1.0}), '177 ty FSO nam 1 khong bao gio thanh tien'),
        'fso_no_gt5y': (dict(R3, drop_fso_gt5=True), 'phu luc gia han FSO den 2036 chua ky: bo dong tien "sau nam 5" (204,95 ty) [H1 tr.31]'),
        'nwc_excluded': (dict(R3, nwc=0.0), 'bo VLD khac +37,0 (cach r2)'),
        'fivef_A_ebitda_x0904': (dict(R3, ebitda_k=0.904), '5F proxy chu ky: EBITDA x 0,904 (ADDENDUM_5F; proxy = EBITDA TONG cong ty, dau sai lech chua do)'),
        'scrap_plus_1musd': (dict(R3, scrap_usd=1.0), 'don vi do nhay: +1 trUSD phe lieu (hoac -1 trUSD chi phi len da TT99 neu doi dau) thu cuoi doi tau hien huu'),
    }


if __name__ == '__main__':
    r2o = json.load(open(os.path.join(HERE, '..', 'calc', 'model_r2_out.json')))
    ctrl = center(R2CFG, r_base=0.135)
    assert abs(ctrl - r2o['center_pre']) < 0.5, (ctrl, r2o['center_pre'])
    steps = [('r2_control', R2CFG, 0.135),
             ('d1_trong_so_doi_xung', dict(R2CFG, w=R3['w']), 0.135),
             ('d2_cat_npv_+30_nhanh_tot', dict(R2CFG, w=R3['w'], npv=R3['npv']), 0.135),
             ('d3_fso_chiet_khau_Ke', dict(R2CFG, w=R3['w'], npv=R3['npv'], fso_mode='r'), 0.135),
             ('d4_vld_khac_+37', dict(R3), 0.135),
             ('r_06_11', dict(R3), R0)]
    bridge, prev = [], None
    for k, cfg, rb in steps:
        c = center(cfg, rb); bridge.append(dict(step=k, center_pre=round(c, 1), delta_pre=None if prev is None else round(c - prev, 1))); prev = c
    vals, wts, keys = grid(R3)
    cp = value_ps('coso', 6, R0, 'ca_hai', 'thanh_tien', R3)
    par = {}
    for k, (cfg, desc) in variants().items():
        v, w, _ = grid(cfg); par[k] = dict(desc=desc, vals=v, wts=w, center_pre=mean(v, w))
    branch = {f'scn_{s}': round(mean([v for v, kk in zip(vals, keys) if kk.startswith(s + '|')], [x for x, kk in zip(wts, keys) if kk.startswith(s + '|')])) for s in SCNS}
    pp = {k: round(v, 2) for k, v in parts('coso', 6, R0, 'ca_hai', 'thanh_tien', R3).items()}
    out = dict(ticker='PVP', round=3, r=R0, dep_anchor=D0, dep_asof=D1, center_pre=mean(vals, wts), center_param_pre=cp, outcomes_vals=vals, outcomes_wts=wts, outcome_keys=keys,
               control=dict(r2_center_pre_file=r2o['center_pre'], r2_center_pre_recomputed=ctrl), bridge_pre=bridge, branch_center_pre=branch, parts_center_param=pp,
               parallel=par)
    json.dump(out, open(os.path.join(HERE, 'pvp_r3_out.json'), 'w'), indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, 'grid_pvp_r3.csv'), 'w', newline='') as f:
        wr = csv.writer(f); wr.writerow(['key', 'value_pre', 'weight'])
        for k, v, w in zip(keys, vals, wts):
            wr.writerow([k, f'{v:.4f}', f'{w:.8f}'])
    with open(os.path.join(HERE, 'pvp_r3_out.txt'), 'w') as f:
        print(f'r={R0:.4f} dep03/11={D0:.4f} dep06/11={D1:.4f} n={len(vals)} sum_w={sum(wts):.6f}', file=f)
        print(f'control r2 center_pre {ctrl:.2f} (file {r2o["center_pre"]:.2f})', file=f)
        for b in bridge:
            print('bridge', json.dumps(b, ensure_ascii=False), file=f)
        print(f'center_pre={out["center_pre"]:.1f} center_param_pre={cp:.1f}', file=f)
        print('branch', json.dumps(branch), file=f); print('parts_center_param', json.dumps(pp), file=f)
        for k, p in par.items():
            print(f'parallel {k}: center_pre={p["center_pre"]:.1f}', file=f)
    print(open(os.path.join(HERE, 'pvp_r3_out.txt')).read())
