"""E17 HPG (job Taylor_20261125_032443): do m tung hang muc + to hop TRONG mo hinh hpg_r3.py (khong cong tay).
PREREG: ../PREREG_adj_HPG.md (md5 assert) + dd_adjcenter_20261124/PREREG_adj(_v2).md. Mu gia.
Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc_adj.py /tmp/ddrestore_w3a/mike/agents/Taylor/research/dd_redo_20261105 <mike_root>"""
import sys, os, io, json, hashlib, runpy, contextlib, itertools
ROOT = os.path.abspath(sys.argv[1]); MIKE = os.path.abspath(sys.argv[2]); HERE = os.path.join(ROOT, 'HPG', 'calc_r3')
ME = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(ME, '..', 'PREREG_adj_HPG.md')) == '1544c2276d1eaa2dd45a9219a1b2f4e3'
for k, v in {'PREREG_adj': 'ef5157cb3f762d58623ed550ebc214c7', 'PREREG_adj_v2': '835dfc1e07f9c67ac7f6c3028b529d13'}.items():
    assert md5(os.path.join(MIKE, 'agents/Taylor/research/dd_adjcenter_20261124', k + '.md')) == v, k
assert md5(os.path.join(HERE, 'hpg_r3.py')) == '8fbf24506eb5d6da4e15ad049f4f3643'
buf = io.StringIO(); cwd = os.getcwd(); os.chdir(HERE)
with contextlib.redirect_stdout(buf): g = runpy.run_path(os.path.join(HERE, 'hpg_r3.py'), run_name='__main__')
os.chdir(cwd)
def nolock(t): return ''.join(l for l in t.splitlines(True) if not l.startswith('LOCK '))
assert nolock(buf.getvalue()) == nolock(open(os.path.join(ME, 'ref_hpg_r3_out.txt')).read()), 'CONTROL'
run, make_fn, axes, PX, D, R, ROLL = g['run'], g['make_fn'], g['axes'], g['PX'], g['D'], g['R'], g['ROLL']
GL = make_fn.__globals__; BASE = dict(COMMIT=GL['COMMIT'], TAXF=GL['TAXF'], DEP_AT=GL['DEP_AT'])
AX = axes(((0.0, 1.0),))
def center(kt=0.0, commit_cut=0.0, etr=None, J=False, dep_at=None):
    GL['COMMIT'] = BASE['COMMIT'] - commit_cut
    GL['TAXF'] = BASE['TAXF'] if etr is None else 0.80 / (1 - etr)
    GL['DEP_AT'] = BASE['DEP_AT'] if dep_at is None else dep_at
    ret = dict(XAU='capex', TRUNG_LAP='capex', TOT='dep') if J else 'capex'
    f0 = make_fn(ROLL, ret, 2035, 'npv0')
    f = lambda r, scen, mult, dg, slope, tlsh: f0(r, scen, mult * (1 - kt), dg, slope, tlsh)
    s = run(f, AX, PX, D)
    GL.update(BASE)
    return s['center']
C0 = center(); assert round(C0) == 21338, C0
def pct(x): return x / C0 - 1
K_PT, K_LO = 401.5 / 15453.2, 221.5 / 15453.2
CQ3 = 14607.2 - 8312.9
ETR_PT, ETR_MID = 1451.3 / 22160.5, (1451.3 / 22160.5 + 0.12) / 2
assert abs(0.80 / 0.88 - BASE['TAXF']) < 1e-12
Jc = center(J=True); assert round(Jc) == 20673, Jc
items = {
 '1_ktpl_flow': dict(tier='A', p=0.9, pl=0.75, ph=1.0, kw=dict(kt=K_PT), kw_lo=dict(kt=K_LO), m=pct(center(kt=K_PT)), m_alt=pct(center(kt=K_LO))),
 '2_commit_q3': dict(tier='B', p=0.5, pl=0.25, ph=0.75, kw=dict(commit_cut=CQ3), kw_lo=dict(commit_cut=CQ3 / 2), m=pct(center(commit_cut=CQ3)), m_alt=pct(center(commit_cut=CQ3 / 2))),
 '3_etr_steel': dict(tier='B', p=0.5, pl=0.25, ph=0.75, kw=dict(etr=ETR_PT), kw_lo=dict(etr=ETR_MID), m=pct(center(etr=ETR_PT)), m_alt=pct(center(etr=ETR_MID))),
}
# J: khoang m [1/2 J; J] — 1/2 J xap xi bang trung binh tam headline va J (TOT tron 50/50 'capex'/'dep' khong co trong mo hinh => tuyen tinh)
items['4_tot_double'] = dict(tier='B', p=0.5, pl=0.25, ph=0.75, m=pct(Jc), m_alt=pct(Jc) / 2)
for v in items.values(): v['m_rng'] = sorted([v['m'], v['m_alt']])
lin = sum(v['p'] * v['m'] for v in items.values())
def combo(ps, use_lo=None):
    """trung binh tam theo nhanh bat/tat doc lap; 4_tot_double bat = J. use_lo: tap hang muc dung m_alt (dau nhe)."""
    use_lo = use_lo or set(); tot = 0.0
    keys = sorted(items)
    for bits in itertools.product((1, 0), repeat=len(keys)):
        w = 1.0; kw = {}; J = False; half_J = False
        for b, k, p in zip(bits, keys, ps):
            w *= p if b else 1 - p
            if not b: continue
            if k == '4_tot_double':
                if k in use_lo: half_J = True
                else: J = True
            else: kw.update(items[k]['kw_lo'] if k in use_lo else items[k]['kw'])
        if w == 0: continue
        if half_J: c = 0.5 * center(J=False, **kw) + 0.5 * center(J=True, **kw)
        else: c = center(J=J, **kw)
        tot += w * c
    return tot
keys = sorted(items)
adj = combo([items[k]['p'] for k in keys])
# cuc tri: moi muc xuong => thap: p cao + m lon; cao: p thap + m nhe
lowv = combo([items[k]['ph'] for k in keys])
highv = combo([items[k]['pl'] for k in keys], use_lo=set(keys))
sens = dict(I_capex_zero=20456, B_tax2030=20648, C_etr_perm=22119, E_tlsh_r2=21144, D_gri_r2=22530,
            ktpl_cap5=round(center(kt=0.05)), ke_12_3=23625, excess_retained_at_Ke=round(center(dep_at=R)))
res = dict(center_base=round(C0), center_adj=round(adj), adj_pct=round(adj / C0 - 1, 5), range_low=round(lowv), range_high=round(highv),
           sum_pm_linear=round(lin, 5), items={k: {kk: (round(vv, 5) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk not in ('kw', 'kw_lo')} for k, v in items.items()},
           k_pt=K_PT, k_lo=K_LO, commit_q3=CQ3, etr_pt=ETR_PT, etr_mid=ETR_MID, sens=sens)
print(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True))
json.dump(res, open(os.path.join(ME, 'calc_adj_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
