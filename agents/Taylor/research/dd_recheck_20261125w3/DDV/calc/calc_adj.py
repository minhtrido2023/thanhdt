"""E17 DDV (job Taylor_20261125_032443): do m tung hang muc + to hop TRONG mo hinh r3 (khong cong tay).
PREREG: ../PREREG_adj_DDV.md (md5 assert) + dd_adjcenter_20261124/PREREG_adj(_v2).md. Mu gia.
Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc_adj.py /tmp/ddrestore_w3a/mike/agents/Taylor/research/dd_redo_20261105 <mike_root>"""
import sys, os, io, json, hashlib, runpy, contextlib, itertools
ROOT = os.path.abspath(sys.argv[1]); MIKE = os.path.abspath(sys.argv[2]); HERE = os.path.join(ROOT, 'DDV', 'calc_r3')
ME = os.path.dirname(os.path.abspath(__file__))
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(ME, '..', 'PREREG_adj_DDV.md')) == '215e58ec1f7ef6d399e2bd353d427dc6'
PR = {'PREREG_adj': 'ef5157cb3f762d58623ed550ebc214c7', 'PREREG_adj_v2': '835dfc1e07f9c67ac7f6c3028b529d13'}
for k, v in PR.items(): assert md5(os.path.join(MIKE, 'agents/Taylor/research/dd_adjcenter_20261124', k + '.md')) == v, k
assert md5(os.path.join(HERE, 'assumptions_r3.json')) == '0e62e59d6175ef01d6329a44737d7520'
assert md5(os.path.join(HERE, 'model_r3.py')) == '0432190ecbb23aa0783f47bd0e3190c0'
buf = io.StringIO(); cwd = os.getcwd(); os.chdir(HERE)
with contextlib.redirect_stdout(buf): g = runpy.run_path(os.path.join(HERE, 'model_r3.py'), run_name='__main__')
os.chdir(cwd); assert hashlib.md5(buf.getvalue().encode()).hexdigest() == 'eeee072ded0755b471a9143fc61ad130', 'CONTROL'
grid, summ, R3, with_ = g['grid'], g['summ'], g['R3CFG'], g['with_']
GL = grid.__globals__; M1 = GL['M1']; G = GL['G']; orig = GL['value_ps']
def value_kt(s, m, r, q4np, int_ded, cfg, liven_loss=0.0):
    k = cfg.get('kt', 0.0)
    c = M1.SCN[s]; ro = r if cfg['ronic'] == 'ke' else float(cfg['ronic']) / 100
    np27 = c['np27'] * ((1 - k) if c['np27'] > 0 else 1.0)
    f27 = np27 * ((1 - G / ro) if np27 > 0 else 1.0)
    mid = M1.NPM_CYCLE * cfg['rev'] * (1 - k) - int_ded + cfg.get('addint', 0.0)
    e_term = mid * (c['mid'] if cfg['midcoef'] else 1.0) * m * (1 + G) * (1 - G / ro)
    v = cfg['nc'] - liven_loss + q4np / (1 + r) ** 0.125 + f27 / (1 + r) ** 0.75 + e_term / (r - G) / (1 + r) ** 1.25
    return v * 1e9 / M1.SH
GL['value_ps'] = value_kt
H = summ(*grid(R3)); assert (H['center_post'], H['p10'], H['p90']) == (15911, 13315, 18573), H  # kt=0 tai lap headline
GL['value_ps'] = orig; assert summ(*grid(R3))['center_post'] == 15911; GL['value_ps'] = value_kt
C0 = H['center_post']
def cen(cfg): s = summ(*grid(cfg)); return s
def pct(x): return round(x / C0 - 1, 5)
KT_PT, KT_LO = 64.25 / 630.83, 56.39 / 630.83
NC = R3['nc']; KTPL_STOCK = 80.22
def cfg_of(kt=0.0, stock=False, ded=None):
    c = with_(R3, kt=kt)
    if stock: c = with_(c, nc=NC - KTPL_STOCK)
    if ded is not None: c = with_(c, intax={'x': (ded, 1.0)})
    return c
items = {}
items['1_ktpl_flow'] = dict(m=pct(cen(cfg_of(kt=KT_PT))['center_post']), m_rng=sorted([pct(cen(cfg_of(kt=KT_LO))['center_post']), pct(cen(cfg_of(kt=KT_PT))['center_post'])]), p=0.9, pl=0.75, ph=1.0, tier='A')
items['2_ktpl_stock'] = dict(m=pct(cen(cfg_of(stock=True))['center_post']), p=0.9, pl=0.75, ph=1.0, tier='A'); items['2_ktpl_stock']['m_rng'] = [items['2_ktpl_stock']['m']] * 2
items['3_int_ded'] = dict(m=pct(cen(cfg_of(ded=8.5))['center_post']), m_rng=sorted([pct(cen(cfg_of(ded=26.0))['center_post']), pct(cen(cfg_of(ded=-9.0))['center_post'])]), p=0.5, pl=0.25, ph=0.75, tier='B')
lin = sum(v['p'] * v['m'] for v in items.values())
# to hop trong mo hinh: ky vong theo p = tron trong so tren cac nhanh bat/tat (doc lap); p dung lam trong so nhanh
def mix(ps, kts=(KT_PT,), ded_on=8.5, ded_off=None):
    tot = 0.0
    for b1, b2, b3 in itertools.product((1, 0), repeat=3):
        w = (ps[0] if b1 else 1 - ps[0]) * (ps[1] if b2 else 1 - ps[1]) * (ps[2] if b3 else 1 - ps[2])
        if w == 0: continue
        c = cfg_of(kt=kts[0] if b1 else 0.0, stock=bool(b2), ded=ded_on if b3 else None)
        tot += w * cen(c)['center_pre']
    return tot * (1 - GL['D_REF'])
adj = mix([items[k]['p'] for k in sorted(items)])
# cuc tri (p, m): thap = moi muc chon dau cho tich nho nhat; cao = lon nhat
def ext(lo=True):
    ps, kt, ded = [], KT_PT if lo else KT_LO, (26.0 if lo else -9.0)
    for k in sorted(items):
        v = items[k]; mm = v['m_rng'][0] if lo else v['m_rng'][1]
        ps.append(v['ph'] if (mm < 0) == lo else v['pl'])
    return mix(ps, kts=(kt,), ded_on=ded)
lowv, highv = ext(True), ext(False)
sens = {'gypsum_per_100ty': round(-100e9 / M1.SH * (1 - GL['D_REF'])), 'ke_12_3': 16854}
res = dict(center_base=C0, center_adj=round(adj), adj_pct=round(adj / C0 - 1, 5), range_low=round(lowv), range_high=round(highv), sum_pm_linear=round(lin, 5),
           items=items, kt_point=KT_PT, kt_low=KT_LO, sens=sens, d_ref=GL['D_REF'])
print(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True))
json.dump(res, open(os.path.join(ME, 'calc_adj_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
