"""dd_recheck w3 25/11 PVT (job Taylor_20261125_032446): D4 (terminal RONIC = Ke) + E15 + dai Ke + do nhay r, CUNG mo hinh r3.
Nguon: dd_redo_20261105/PVT/calc_r3/pvt_r3.py (TRIM 19/11, 14ad1c925) — khoi phuc vao /tmp/ddrestore_PVT (git archive 14ad1c925^ ...PVT _common_014127 _shared dd_PVT_20261029 ...).
Chay: /home/trido/thanhdt/wc_venv/bin/python calc_recheck.py /tmp/ddrestore_PVT/agents/Taylor/research
Mu gia: khong doc gia moi; CK 5 ty lay tu SUMMARY.json r3 (d_ref), gia 20.550 (06/11) chi cho % duoi gia (ke thua)."""
import sys, os, io, json, hashlib, runpy, contextlib
RS = os.path.abspath(sys.argv[1]); BASE = os.path.join(RS, 'dd_redo_20261105', 'PVT'); HERE = os.path.join(BASE, 'calc_r3')
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
ROOT = os.path.dirname(BASE)
for ln in open(os.path.join(HERE, 'LOCK_md5.txt')):
    p = ln.split()
    if p and p[0] == 'LOCK' and not p[2].startswith('../../../../../data/deposit'):  # events csv append-only sau 06/11 (khong doi gia tri asof)
        f = '/home/trido/thanhdt/WorkingClaude/' + p[2][15:] if p[2].startswith('../../../../../') else os.path.join(ROOT, p[2])
        assert md5(f) == p[1], p[2]
cwd = os.getcwd(); os.chdir(HERE)
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(os.path.join(HERE, 'pvt_r3.py'), run_name='__main__')
os.chdir(cwd)
assert md5(os.path.join(HERE, 'pvt_r3_out.txt')) == '23f5090fa729bfbc2a40d60d3f58e43c', 'CONTROL lech'
assert md5(os.path.join(HERE, 'grid_pvt_r3.csv')) == '58d046161075a2c806cb8419aed04b82'
sys.path.insert(0, os.path.join(ROOT, '_shared')); from wpct import wpct, weight_below
SUMM = json.load(open(os.path.join(BASE, 'SUMMARY.json')))
d = SUMM['liq_disc_5ty']
G, Q3_NP, EQ, SH, BUY_AMT, NCI, R0, R3 = g['G'], g['Q3_NP'], g['EQ'], g['SH'], g['BUY_AMT'], g['NCI'], g['R0'], g['R3']
import itertools
def value_ps(s, m, r, b, cfg, ronic_ke):
    roe = cfg['roe_mid'] * cfg['mid'][s] * m
    reinv = 1 - G / max(roe, 1e-9)
    reinv_T = (1 - G / r) if ronic_ke else reinv
    v = Q3_NP / (1 + r) ** 0.125 + cfg['np27'][s] * reinv / (1 + r) ** 0.75
    v += roe * EQ * (1 + G) * reinv_T / (r - G) / (1 + r) ** 1.25
    v += cfg['npv'][s] * BUY_AMT[b] * (1 - NCI) + cfg['adj']
    return v * 1e9 / SH
def grid(cfg, rb, ronic_ke):
    V, W = [], []
    for s, m, (dr, rw), b in itertools.product(('xau', 'coso', 'tot'), g['MULTS'], cfg['r_axis'], ('mua_phan_con_lai', 'khong')):
        V.append(value_ps(s, m, rb + dr, b, cfg, ronic_ke)); W.append(cfg['w'][s] / len(g['MULTS']) * rw * cfg['buy'][b])
    return V, W
def summ(rb, ronic_ke, dd, px=20550.0):
    V, W = grid(R3, rb, ronic_ke); c = sum(a * b for a, b in zip(V, W)) / sum(W); q = wpct(V, W, (0.10, 0.50, 0.90)); f = 1 - dd
    return dict(center_pre=c, center=c * f, p10=q[0.10] * f, p50=q[0.50] * f, p90=q[0.90] * f, below=weight_below([v * f for v in V], W, px))
# CK: suy tu tam r3 (18.968 truoc -> 18.841 sau) neu SUMMARY khong co truong
b0 = summ(R0, False, 0.0)
if d is None: d = 1 - 18841 / b0['center_pre']
s_old = summ(R0, False, d)
assert round(s_old['center']) == 18841 and round(s_old['p10']) == 13903 and round(s_old['p90']) == 24207, s_old
s_new = summ(R0, True, d)
rows = []
for lab, r in [('12,3% E15/dau duoi Ke', 0.123), ('12,5% (-100bp)', R0 - 0.01), ('13,0% (-50bp)', R0 - 0.005), ('13,4% dau tren Ke', 0.134),
               ('13,5% BASE', R0), ('14,0% (+50bp)', R0 + 0.005), ('14,5% (+100bp)', R0 + 0.01)]:
    s = summ(r, True, d)
    rows.append(dict(label=lab, r=round(r, 4), center=round(s['center']), p10=round(s['p10']), p90=round(s['p90']),
                     d_center=round(s['center'] - s_new['center']), d_pct=round(s['center'] / s_new['center'] - 1, 4), pct_below_px=round(s['below'], 4)))
old_rows = {lab: round(summ(r, False, d)['center']) for lab, r in [('-100', R0 - .01), ('-50', R0 - .005), ('+50', R0 + .005), ('+100', R0 + .01)]}
res = dict(r_base=R0, ck=d, old_base=dict((k, round(v, 4) if k == 'below' else round(v)) for k, v in s_old.items()),
           d4_base=dict((k, round(v, 4) if k == 'below' else round(v)) for k, v in s_new.items()),
           d4_delta_pct=round(s_new['center'] / s_old['center'] - 1, 5), rows_d4=rows, old_r_sens_check=old_rows)
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_recheck_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
