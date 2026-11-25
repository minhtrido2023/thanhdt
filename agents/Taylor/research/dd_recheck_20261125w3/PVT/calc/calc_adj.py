"""E17 PVT — tam ky vong dieu chinh, chay QUA mo hinh r3 + D4 (cung value_ps cua calc_recheck.py; ADJ_PREREG_PVT.md khoa truoc).
Chay: /home/trido/thanhdt/wc_venv/bin/python calc_adj.py /tmp/ddrestore_PVT/agents/Taylor/research
P1: he so (1-k) nhan vao moi dong LN me (Q4/26, np27, terminal roe*EQ) — ap tren LN da tru P2.
P2: np27 + d27, Q4/26 + dq4 (ty, phan me). MU GIA: gia 20.550 chi dung cho % duoi gia ke thua, khong dung khi dung."""
import sys, os, io, json, hashlib, runpy, contextlib, itertools
RS = os.path.abspath(sys.argv[1]); BASE = os.path.join(RS, 'dd_redo_20261105', 'PVT'); HERE = os.path.join(BASE, 'calc_r3')
OUT = os.path.dirname(os.path.abspath(__file__)); md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(OUT, '..', 'ADJ_PREREG_PVT.md')) == '9d8b4c5385260ad40c863a206eba5c67'
assert md5(os.path.join(HERE, 'assumptions_r3.json')) == '5f07cb59fc4cfb43b5ff875fba642803'
cwd = os.getcwd(); os.chdir(HERE)
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(os.path.join(HERE, 'pvt_r3.py'), run_name='__main__')
os.chdir(cwd)
assert md5(os.path.join(HERE, 'pvt_r3_out.txt')) == '23f5090fa729bfbc2a40d60d3f58e43c', 'CONTROL lech'
d = json.load(open(os.path.join(OUT, 'calc_recheck_out.json')))['ck']
G, Q3_NP, EQ, SH, BUY_AMT, NCI, R0, R3 = g['G'], g['Q3_NP'], g['EQ'], g['SH'], g['BUY_AMT'], g['NCI'], g['R0'], g['R3']
def value_ps(s, m, r, b, cfg, k=0.0, d27=0.0, dq4=0.0):
    roe = cfg['roe_mid'] * cfg['mid'][s] * m
    reinv = 1 - G / max(roe, 1e-9); reinv_T = 1 - G / r; f = 1 - k
    v = (Q3_NP + dq4) * f / (1 + r) ** 0.125 + (cfg['np27'][s] + d27) * f * reinv / (1 + r) ** 0.75
    v += roe * EQ * f * (1 + G) * reinv_T / (r - G) / (1 + r) ** 1.25
    v += cfg['npv'][s] * BUY_AMT[b] * (1 - NCI) + cfg['adj']
    return v * 1e9 / SH
def center(k=0.0, x2=0.0):  # x2 = p*m cua P2 tinh theo np27 (ty); Q4 = x2/4
    V, W = [], []
    for s, m, (dr, rw), b in itertools.product(('xau', 'coso', 'tot'), g['MULTS'], R3['r_axis'], ('mua_phan_con_lai', 'khong')):
        V.append(value_ps(s, m, R0 + dr, b, R3, k, x2, x2 / 4)); W.append(R3['w'][s] / len(g['MULTS']) * rw * R3['buy'][b])
    return sum(a * b for a, b in zip(V, W)) / sum(W) * (1 - d)
C0 = center(); assert round(C0) == 18956, C0
IT = {'P1_trich_KTPL_tu_LN_me': ('k', 0.0747, 0.0747, 0.145, .50, .25, .75, 'B'),
      'P2_hoan_nhap_du_phong_sua_chua_lon_TT99': ('x2', -73.2, -36.6, -73.2, .50, .25, .75, 'B')}
def run(sel): return center(**{IT[k][0]: v for k, v in sel.items()})
items = {}
for k, (kind, m, lo, hi, p, plo, phi, bac) in IT.items():
    ext = [run({k: pp * mm}) / C0 - 1 for pp in (plo, phi) for mm in (lo, hi)]
    items[k] = dict(bac=bac, input=m, input_range=[lo, hi], m_pct=round(run({k: m}) / C0 - 1, 5), p=p, p_range=[plo, phi],
                    pm_pct=round(run({k: p * m}) / C0 - 1, 5), pm_min=round(min(ext), 5), pm_max=round(max(ext), 5))
adj = run({k: IT[k][4] * IT[k][1] for k in IT})
def pick(fn):  # chon cuc tri (p,m) theo tac dong len tam cho tung hang muc, chay to hop qua mo hinh
    return {k: fn([pp * mm for pp in (v[5], v[6]) for mm in (v[2], v[3])], key=lambda x, k=k: run({k: x})) for k, v in IT.items()}
low, high = run(pick(min)), run(pick(max))
lin = sum(v['pm_pct'] for v in items.values())
# bang dieu kien doi so
trig = {'P1_len_A_k7.47_p0.90': center(k=.9 * .0747, x2=.5 * -73.2) / adj - 1,
        'P1_len_A_k14.5_p0.90': center(k=.9 * .145, x2=.5 * -73.2) / adj - 1,
        'P1_dong_k0': center(x2=.5 * -73.2) / adj - 1,
        'P2_len_A_p0.90_m73.2': center(k=.5 * .0747, x2=.9 * -73.2) / adj - 1,
        'P2_dong_chi_dry_dock_bang_hoan_nhap': center(k=.5 * .0747) / adj - 1}
res = dict(center_base=round(C0), center_adj=round(adj), adj_pct=round(adj / C0 - 1, 5), range_low=round(low), range_high=round(high),
           sum_pm_linear_pct=round(lin, 5), items=items, triggers={k: round(v, 5) for k, v in trig.items()}, ck=d)
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(OUT, 'calc_adj_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
