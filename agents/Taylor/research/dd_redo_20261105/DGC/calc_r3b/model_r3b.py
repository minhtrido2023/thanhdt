"""DGC — VONG 3b (job Taylor_20261108_175121). User duyet cach B cua fundamental-skeptic cho dinh chinh #4:
GIU xac suat mo lai khai truong 25 w=0,5 (nhu r2/r3-goc model.py:37), CHI bo bien tang VINH VIEN (terminal 'up'=1.000 ty/nam) cua nhanh mo lai;
GIU phan tang lai gop 2028 ('up28'=500 ty) — khong phai thuong moat. Moi dinh chinh #1,#2,#3,#5,#6,#7 cua r3 GIU NGUYEN (import model_r3, khong sua).
KHONG doc gia. Chay: $DNA_PYEXE -I model_r3b.py -> model_r3b_out.json ; md5 -> LOCK_r3b_md5.txt ; roi compare_r3b.py."""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../calc'))); sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../_common_014127')))
import model_r3 as M3
M1, MR2, R2, C = M3.M1, M3.MR2, M3.R2, M3.C


def ore_tab(term_keep):
    """term_keep=1 -> nhu r2/r3 (up=1.000 vinh vien); 0 -> cach B (up=0, giu up28)."""
    o = {k: dict(v) for k, v in M1.ORE.items()}
    o['molai']['up'] = o['molai']['up'] * term_keep
    return o


def core(s, o, m, r, cfg):
    u = ore_tab(cfg['ore_term'])[o]; ron = r if cfg['ronic'] == 'ke' else cfg['ronic']; reinv = 1 - M1.G / ron; t = M1.T_NEAR
    e27, e28 = M3.ebit(s, 2027, cfg['basis']), M3.ebit(s, 2028, cfg['basis'])
    v = MR2.Q4_EX * m * (1 - t) / (1 + r) ** 0.125
    v += e27 * m * (1 - t) * reinv / (1 + r) ** 0.75
    v += (e28 * m + u['up28']) * (1 - t) * reinv / (1 + r) ** 1.75
    v += (e28 * m + u['up']) * (1 + M1.G) * (1 - M1.T_TERM) * reinv / (r - M1.G) / (1 + r) ** 2.25
    return v


def value_ps(s, o, p, ns, m, r, cfg, legal_h=0.0):
    other = (M1.CASH_DEP - M1.DEBT) * (1 - legal_h) - M1.PROV - M1.FUND_KTPL + M1.NS_CIP + MR2.NS[ns]['adj']
    eq = (core(s, o, m, r, cfg) - M3.prov_pv(p, r, cfg)) * (1 - M1.S_NP) + other * (1 - M1.S_EQ)
    return eq * 1e9 / M1.SH


def grid(cfg, legal=False, r_shift=None):
    ws = dict(zip(('xau', 'coso', 'tot'), cfg['w_scn']))
    ore = {'dung': 1 - cfg['w_ore'], 'molai': cfg['w_ore']}
    lg = MR2.LEGAL if legal else {'none': dict(w=1.0, h=0.0)}
    rp = R2.r_points() if r_shift is None else [(C.r_now(shift=r_shift), 1.0, None)]
    vals, wts = [], []
    for s, (o, wo), (p, pc), (n, nc), m, (r, rw, _), (l, lc) in itertools.product(ws, ore.items(), MR2.PROV.items(), MR2.NS.items(), M1.MULTS, rp, lg.items()):
        if wo == 0:
            continue
        vals.append(value_ps(s, o, p, n, m, r, cfg, lc['h'])); wts.append(ws[s] * wo * pc['w'] * nc['w'] / len(M1.MULTS) * rw * lc['w'])
    return vals, wts


mean = M3.mean
CFG3 = dict(M3.CFG0, ore_term=1.0)                    # r3 headline (w=0)
CFG3B = dict(M3.CFG0, w_ore=0.5, ore_term=0.0)        # r3b headline (cach B)
def cx(**kw):
    c = dict(CFG3B); c.update(kw); return c

VARIANTS = {
 'ore_w0': ('mo lai khai truong w=0 (= headline r3)', cx(w_ore=0.0)),
 'ore_w0.10': ('mo lai w=0,10, bien vinh vien 0', cx(w_ore=0.10)),
 'ore_w0.25': ('mo lai w=0,25, bien vinh vien 0', cx(w_ore=0.25)),
 'ore_w0.75': ('mo lai w=0,75, bien vinh vien 0', cx(w_ore=0.75)),
 'ore_w1.0': ('mo lai chac chan (w=1), bien vinh vien 0', cx(w_ore=1.0)),
 'ore_w0.5_term': ('mo lai w=0,5 CO bien vinh vien 1.000 ty (= r3 dong w=0,50; thuong moat — doi chieu)', cx(ore_term=1.0)),
 'ore_w0.1_term': ('mo lai w=0,10 CO bien vinh vien (= r3 dong w=0,10, doi chieu)', cx(w_ore=0.10, ore_term=1.0)),
 'ore_w0.25_term': ('mo lai w=0,25 CO bien vinh vien (= r3 dong w=0,25, doi chieu)', cx(w_ore=0.25, ore_term=1.0)),
 'r4_fix': ('nen bien r4 + bo chong lan du phong', cx(basis='r4', r4_overlap_fix=True)),
 'r4_nofix': ('nen bien r4 + du phong chong lan nhu r2 (doi chieu)', cx(basis='r4')),
 'shield20': ('la chan thue du phong 20% [UL]', cx(shield=0.20)),
 'ronic20': ('RONIC 20% (thuong moat — doi chieu)', cx(ronic=0.20)),
 'w_scn_r2': ('trong so kich ban 0,3/0,5/0,2 cua r2', cx(w_scn=(0.3, 0.5, 0.2))),
}

if __name__ == '__main__':
    r0 = C.r_now()
    # control: tai lap headline r3 bang code r3b (phai = model_r3_out.json center_pre)
    r3j = json.load(open(os.path.join(HERE, '../calc/model_r3_out.json')))
    v3, w3 = grid(CFG3); assert abs(mean(v3, w3) - r3j['center_pre']) < 1e-6
    for k in ('ore_w0.10', 'ore_w0.25', 'ore_w0.50'):          # dong song song r3 tai lap
        c = dict(CFG3, w_ore=float(k.split('_w')[1]))
        v, w = grid(c); assert abs(mean(v, w) - r3j['parallel'][k]['center_pre']) < 1e-6, k
    vals, wts = grid(CFG3B)
    cp = value_ps('coso', 'dung', 'huu_han_4q', 'so_sach', 1.0, r0, CFG3B)
    cp_molai = value_ps('coso', 'molai', 'huu_han_4q', 'so_sach', 1.0, r0, CFG3B)
    steps = [('r3 headline (w=0)', CFG3), ('w 0 -> 0,5 voi bien vinh vien 1.000 (= r3 dong w=0,50)', dict(CFG3, w_ore=0.5)),
             ('bo bien vinh vien nhanh mo lai (cach B) = r3b', CFG3B)]
    bridge, prev = [], None
    for nm, c in steps:
        v, w = grid(c); x = mean(v, w); bridge.append(dict(step=nm, center_pre=x, delta=None if prev is None else x - prev)); prev = x
    par = {}
    for k, (d, c) in VARIANTS.items():
        v, w = grid(c); par[k] = dict(desc=d, vals=v, wts=w, center_pre=mean(v, w))
    v, w = grid(CFG3B, legal=True); par['legal_axis'] = dict(desc='CO truc phap ly haircut tien rong 3/9/29% (w 0,2/0,5/0,3) — ngoai base', vals=v, wts=w, center_pre=mean(v, w))
    rs = {f'{bp:+d}bp': mean(*grid(CFG3B, r_shift=bp / 1e4)) for bp in (-100, -50, 50, 100)}
    ore_uplift_ps = dict(up28_pv_ps=(value_ps('coso', 'molai', 'huu_han_4q', 'so_sach', 1.0, r0, CFG3B) - value_ps('coso', 'dung', 'huu_han_4q', 'so_sach', 1.0, r0, CFG3B)),
                         term_pv_ps_removed=(value_ps('coso', 'molai', 'huu_han_4q', 'so_sach', 1.0, r0, dict(CFG3B, ore_term=1.0)) - cp_molai))
    out = dict(ticker='DGC', round='3b', job='Taylor_20261108_175121', r=r0, cfg=CFG3B, ore_table=ore_tab(0.0), center_pre=mean(vals, wts), center_param_pre=cp,
               center_param_molai_pre=cp_molai, outcomes_vals=vals, outcomes_wts=wts, control_r3_center_pre=mean(v3, w3), bridge_pre=bridge, parallel=par,
               r_sens_pre=rs, ore_uplift_ps_pre=ore_uplift_ps,
               grid_desc='nhu r3 (n=405 moi nhanh khai truong) x khai truong dung/mo lai 0,5/0,5; nhanh mo lai: +500 ty lai gop 2028, terminal +0 (cach B); n=810')
    json.dump(out, open(os.path.join(HERE, 'model_r3b_out.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(dict(center_pre=round(out['center_pre']), cp=round(cp), cp_molai=round(cp_molai), n=len(vals), control=round(mean(v3, w3)),
                          bridge=[(b['step'], round(b['center_pre'])) for b in bridge], par={k: round(x['center_pre']) for k, x in par.items()},
                          rs={k: round(x) for k, x in rs.items()}, uplift={k: round(x) for k, x in ore_uplift_ps.items()}), ensure_ascii=False))
