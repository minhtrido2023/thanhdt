"""DGC — VONG 3 (TOP5C_CORRECTIONS_20261108.md muc DGC), job Taylor_20261108_164329. KHONG doc gia (gia + CK o compare_r3.py sau LOCK_r3).
Chay: $DNA_PYEXE -I model_r3.py -> model_r3_out.json ; md5 -> LOCK_r3_md5.txt ; roi compare_r3.py.
Dung lai hang so BCTC (model.py) + truc du phong/Nghi Son (model_r2.py) — import, khong sua.
Doi so r2 (kiem tung dinh chinh, xem REPORT_r3.md §1):
 c1 dem doi du phong tren nen r4 -> base dung nen R2 (gia von Q3x4 BO du phong) => khong con chong lan; ban r4 + bo chong lan bao song song.
 c2 trong so kich ban 0,3/0,5/0,2 -> 0,25/0,5/0,25 (bien do -337/+367 gan doi xung; 0,3/0,2 tu nhan 'chu quan', r12 REPORT dong 5).
 c3 RONIC 20% -> Ke (moat_durable=false, ADDENDUM_5F_r2.md §2).
 c4 mo lai khai truong: base w=0 (hien trang quan sat duoc; mo lai = phuc hoi co che hao, hao khong ben => khong cong); w 0,1/0,25/0,5 bao song song.
 c5 nen bien r4 (16,5/17,5%, khong co dong co so) -> R2 19,5/20,7% (co so: GPM Q3/26 thuc te 20,5% gom du phong/24,6% bo du phong khi dung quang mua ngoai,
    BCTC HN Q3/2026 p dong 8-9; trung vi 4 peer 19,47% ADDENDUM_5F_r2.md dong 16).
 c6 la chan thue du phong: base 0 [UL], do nhay 20%/15%."""
import csv, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import model as M1
import model_r2 as MR2
import common_r2 as R2
C = R2.C
FC = os.path.abspath(os.path.join(HERE, '../../../dgc_valuation_20261029_r12/out_A_forecast.csv'))
F = {(r['scn'], int(r['year'])): r for r in csv.DictReader(open(FC)) if r['rev_core']}
KEY = {'xau': 'nghich', 'coso': 'coso', 'tot': 'thuan'}
OPEX = {k: float(F[(KEY[k], 2027)]['gp']) - float(F[(KEY[k], 2027)]['ebit_core']) for k in KEY}
COGS_R2 = (2469.45 - 506.35) * 4 - 400.0          # gia von Q3/26 x4 bo 100 ty/quy du phong (= r9_calc.py dong 7, R2)
REV_CS = [float(F[('coso', y)]['rev_core']) for y in (2027, 2028)]
GM_CS = [float(F[('coso', y)]['gm_eff']) for y in (2027, 2028)]
SH_R2 = [(1 - COGS_R2 / REV_CS[i]) - GM_CS[i] for i in (0, 1)]        # dich bien dong deu moi kich ban (nhu r9_calc.py)
GAP_R4 = [REV_CS[i] * (1 - GM_CS[i]) - COGS_R2 for i in (0, 1)]       # gia von nen r4 cao hon R2 (ty/nam) = 'du phong ngam'


def ebit(s, y, basis):
    r = F[(KEY[s], y)]; i = y - 2027
    if basis == 'r4':
        return float(r['ebit_core'])
    return (float(r['gm_eff']) + SH_R2[i]) * float(r['rev_core']) - OPEX[s]


CFG0 = dict(basis='R2', w_scn=(0.25, 0.5, 0.25), ronic='ke', w_ore=0.0, shield=0.0, r4_overlap_fix=False)


def core(s, o, m, r, cfg):
    u = M1.ORE[o]; ron = r if cfg['ronic'] == 'ke' else cfg['ronic']; reinv = 1 - M1.G / ron; t = M1.T_NEAR
    e27, e28 = ebit(s, 2027, cfg['basis']), ebit(s, 2028, cfg['basis'])
    v = MR2.Q4_EX * m * (1 - t) / (1 + r) ** 0.125
    v += e27 * m * (1 - t) * reinv / (1 + r) ** 0.75
    v += (e28 * m + u['up28']) * (1 - t) * reinv / (1 + r) ** 1.75
    v += (e28 * m + u['up']) * (1 + M1.G) * (1 - M1.T_TERM) * reinv / (r - M1.G) / (1 + r) ** 2.25
    return v


def prov_pv(p, r, cfg):
    """Dong tien du phong theo quy (t=0,125+0,25i). r4_overlap_fix: tu 2027 chi tru phan VUOT gia von ngam cua nen r4 (GAP_R4/4 moi quy, san 0)."""
    n = MR2.PROV[p]['n']; q = MR2.PROV_Q * (1 - cfg['shield'])
    if n == 0:
        return 0.0
    def qamt(i):
        if not cfg['r4_overlap_fix'] or i == 0:
            return q
        g = GAP_R4[0] if i <= 4 else GAP_R4[1]
        return max(0.0, MR2.PROV_Q - g / 4) * (1 - cfg['shield'])
    if n is not None:
        return sum(qamt(i) / (1 + r) ** (0.125 + 0.25 * i) for i in range(n))
    v = sum(qamt(i) / (1 + r) ** (0.125 + 0.25 * i) for i in range(9))          # Q4/26 .. Q4/28
    rq = (1 + r) ** 0.25 - 1
    return v + qamt(9) / rq / (1 + r) ** (0.125 + 0.25 * 8)                     # vinh vien tu Q1/29


def value_ps(s, o, p, ns, m, r, cfg, legal_h=0.0):
    other = (M1.CASH_DEP - M1.DEBT) * (1 - legal_h) - M1.PROV - M1.FUND_KTPL + M1.NS_CIP + MR2.NS[ns]['adj']
    eq = (core(s, o, m, r, cfg) - prov_pv(p, r, cfg)) * (1 - M1.S_NP) + other * (1 - M1.S_EQ)
    return eq * 1e9 / M1.SH


def grid(cfg, legal=False):
    ws = dict(zip(('xau', 'coso', 'tot'), cfg['w_scn']))
    ore = {'dung': 1 - cfg['w_ore'], 'molai': cfg['w_ore']}
    lg = MR2.LEGAL if legal else {'none': dict(w=1.0, h=0.0)}
    vals, wts = [], []
    for s, (o, wo), (p, pc), (n, nc), m, (r, rw, _), (l, lc) in itertools.product(ws, ore.items(), MR2.PROV.items(), MR2.NS.items(), M1.MULTS, R2.r_points(), lg.items()):
        if wo == 0:
            continue
        vals.append(value_ps(s, o, p, n, m, r, cfg, lc['h'])); wts.append(ws[s] * wo * pc['w'] * nc['w'] / len(M1.MULTS) * rw * lc['w'])
    return vals, wts


def mean(v, w):
    return sum(a * b for a, b in zip(v, w)) / sum(w)


def cfgx(**kw):
    c = dict(CFG0); c.update(kw); return c


R2CFG = dict(basis='r4', w_scn=(0.3, 0.5, 0.2), ronic=0.20, w_ore=0.5, shield=0.0, r4_overlap_fix=False)

VARIANTS = {   # bao song song (headline_vs_alternatives)
    'ore_w0.10': ('mo lai khai truong w=0,10', cfgx(w_ore=0.10)),
    'ore_w0.25': ('mo lai khai truong w=0,25', cfgx(w_ore=0.25)),
    'ore_w0.50': ('mo lai khai truong w=0,50 (= r2)', cfgx(w_ore=0.50)),
    'r4_fix': ('nen bien r4 16,5/17,5% (khong co dong co so) + bo chong lan du phong (dinh chinh 1 nguyen ban)', cfgx(basis='r4', r4_overlap_fix=True)),
    'r4_nofix': ('nen bien r4 + du phong chong lan nhu r2 (doi chieu)', cfgx(basis='r4')),
    'shield20': ('la chan thue du phong 20% (TT48: tru khi chi that) [UL]', cfgx(shield=0.20)),
    'ronic20': ('RONIC 20% (thuong moat — trai luat 3c, chi doi chieu)', cfgx(ronic=0.20)),
    'w_scn_r2': ('trong so kich ban 0,3/0,5/0,2 cua r2', cfgx(w_scn=(0.3, 0.5, 0.2))),
}

if __name__ == '__main__':
    r0 = C.r_now()
    vals, wts = grid(CFG0)
    cp = value_ps('coso', 'dung', 'huu_han_4q', 'so_sach', 1.0, r0, CFG0)
    # tai lap r2 bang code r3 (phai = model_r2_out.json center_pre)
    v2, w2 = grid(R2CFG); r2_json = json.load(open(os.path.join(HERE, 'model_r2_out.json')))
    repro = dict(r3_code=mean(v2, w2), r2_json=r2_json['center_pre'])
    assert abs(repro['r3_code'] - repro['r2_json']) < 1e-6, repro
    # cau noi r2 -> r3 (truoc CK), tung buoc cong don
    steps = [('r2 (tai lap)', R2CFG),
             ('c1 bo chong lan du phong tren nen r4', dict(R2CFG, r4_overlap_fix=True)),
             ('c2 trong so 0,25/0,5/0,25', dict(R2CFG, r4_overlap_fix=True, w_scn=(0.25, 0.5, 0.25))),
             ('c3 RONIC = Ke', dict(R2CFG, r4_overlap_fix=True, w_scn=(0.25, 0.5, 0.25), ronic='ke')),
             ('c5 nen bien R2 (thay r4+fix; R2 khong chong lan)', dict(R2CFG, basis='R2', w_scn=(0.25, 0.5, 0.25), ronic='ke')),
             ('c4 mo lai khai truong w 0,5 -> 0', CFG0)]
    bridge, prev = [], None
    for nm, c in steps:
        v, w = grid(c); x = mean(v, w)
        bridge.append(dict(step=nm, center_pre=x, delta=None if prev is None else x - prev)); prev = x
    # skeptic don le (moi dinh chinh rieng tren r2) de doi chieu so cua skeptic
    single = {}
    for nm, kw in (('c1', dict(r4_overlap_fix=True)), ('c2', dict(w_scn=(0.25, 0.5, 0.25))), ('c3', dict(ronic='ke')), ('c5_R2', dict(basis='R2')),
                   ('c6_shield20', dict(shield=0.20)), ('c4_w0', dict(w_ore=0.0)), ('c4_w0.1', dict(w_ore=0.1))):
        v, w = grid(dict(R2CFG, **kw)); single[nm] = mean(v, w) - repro['r2_json']
    par = {}
    for k, (d, c) in VARIANTS.items():
        v, w = grid(c); par[k] = dict(desc=d, vals=v, wts=w, center_pre=mean(v, w))
    for k, d in (('legal_axis', 'CO truc phap ly: haircut tien rong 3/9/29% (w 0,2/0,5/0,3) — ngoai base (vu an chi WARNING)'),):
        v, w = grid(CFG0, legal=True); par[k] = dict(desc=d, vals=v, wts=w, center_pre=mean(v, w))
    prov_ps = {p: round(-prov_pv(p, r0, CFG0) * (1 - M1.S_NP) * 1e9 / M1.SH) for p in MR2.PROV}
    ebit_tab = {s: {y: round(ebit(s, y, b)) for y in (2027, 2028) for b in ('R2',)} for s in KEY}
    ebit_9t_ann = dict(incl_prov=M1.EBIT_9T * 4 / 3, ex_prov=(M1.EBIT_9T + M1.PROV) * 4 / 3)
    rs = {}
    for bp in (-100, -50, 50, 100):
        rr = C.r_now(shift=bp / 1e4)
        ws = dict(zip(('xau', 'coso', 'tot'), CFG0['w_scn']))
        it = list(itertools.product(ws, MR2.PROV, MR2.NS, M1.MULTS))
        rs[f'beta1.0_{bp:+d}bp'] = sum(value_ps(s, 'dung', p, n, m, rr, CFG0) * ws[s] * MR2.PROV[p]['w'] * MR2.NS[n]['w'] / 5 for s, p, n, m in it)
    rs['base'] = mean(vals, wts)
    # Gordon/ROE kiem cheo (giu tu r2)
    out = dict(ticker='DGC', round=3, job='Taylor_20261108_164329', r=r0, cfg=CFG0, center_pre=mean(vals, wts), center_param_pre=cp,
               outcomes_vals=vals, outcomes_wts=wts, reproduce_r2=repro, bridge_pre=bridge, single_correction_pre=single,
               parallel=par, prov_axis_ps=prov_ps, ebit_R2=ebit_tab, opex=OPEX, sh_R2=SH_R2, gap_r4=GAP_R4, ebit_9t_annualized=ebit_9t_ann,
               r_sens_pre=rs, gordon_roe_xcheck=r2_json['gordon_roe_xcheck'],
               grid_desc=('ket cuc = kich ban EBIT (xau/co so/tot 0,25/0,5/0,25) tren nen bien R2 x khai truong DUNG (w mo lai 0 o base) x du phong moi truong '
                          '(mot lan/huu han 4 quy/vinh vien 100 ty/quy, 1/3 [UL], la chan thue 0 [UL]) x Nghi Son -500/0/+500 (0,25/0,5/0,25 [UL]) x he so EBIT 0,8..1,2 (deu) '
                          'x lai huy dong -50/0/+50bp (0,25/0,5/0,25 [UL]); RONIC=Ke; n=405; tham so trung tam = co so, huu han 4 quy, NS so sach, m=1, Δr=0'))
    json.dump(out, open(os.path.join(HERE, 'model_r3_out.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(dict(center_pre=round(out['center_pre']), center_param_pre=round(cp), n=len(vals), repro=repro,
                          bridge=[(b['step'], round(b['center_pre']), None if b['delta'] is None else round(b['delta'])) for b in bridge],
                          single={k: round(v) for k, v in single.items()}, par={k: round(v['center_pre']) for k, v in par.items()},
                          prov_ps=prov_ps, ebit_R2=ebit_tab, gap_r4=[round(g) for g in GAP_R4], ebit9t=ebit_9t_ann), ensure_ascii=False))
