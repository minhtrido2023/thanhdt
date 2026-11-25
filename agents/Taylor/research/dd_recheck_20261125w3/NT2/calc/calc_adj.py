"""E17 NT2 — tam ky vong dieu chinh, chay QUA mo hinh r3 (ADJ_PREREG_NT2.md khoa truoc).
Chay: /home/trido/thanhdt/wc_venv/bin/python calc_adj.py /tmp/ddrestore_NT2/agents/Taylor/research/dd_redo_20261105"""
import sys, os, io, json, hashlib, runpy, contextlib, itertools
ROOT = os.path.abspath(sys.argv[1]); HERE = os.path.join(ROOT, 'NT2', 'calc_r3'); OUT = os.path.dirname(os.path.abspath(__file__))
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
assert md5(os.path.join(OUT, '..', 'ADJ_PREREG_NT2.md')) == '9cf0946d4f00d8a66c1a36400555e097'
assert md5(os.path.join(HERE, 'assumptions_r3.json')) == '675413d6a93559f6c55b0dd2cfd009ea'
cwd = os.getcwd(); os.chdir(HERE)
with contextlib.redirect_stdout(io.StringIO()) as b: g = runpy.run_path(os.path.join(HERE, 'model_r3.py'), run_name='__main__')
os.chdir(cwd)
assert hashlib.md5(b.getvalue().encode()).hexdigest() == 'f2c6788a0c53c0cdf7b7acddb941b4ae'
run, Q, SH, LD = g['run'], g['Q'], g['SH'], g['LD']
C0 = g['S']['center_post']; assert round(C0) == 24003
def center(np_shift=0.0, fcf_shift=0.0, t0_bn=0.0):
    s, _, _ = run(Q, np_shift=np_shift, fcf_shift=fcf_shift)
    return s['center_post'] + t0_bn / SH * 1000 * (1 - LD)
# item: (kind, m_center, m_lo, m_hi, p, p_lo, p_hi, bac)
IT = {'N1_bien_LNST_het_khau_hao': ('np', 121.0, 29.0, 214.0, .50, .25, .75, 'B'),
      'N2_FCF_tru_LNST_het_khau_hao': ('fcf', 66.0, -136.0, 252.0, .35, .15, .55, 'B'),
      'N3_no_ngan_han_ngoai_netcash': ('t0', -91.88, -91.88, -91.88, .90, .75, 1.00, 'A'),
      'N4_trich_KTPL_hang_nam': ('np', -20.0, -40.0, -20.0, .50, .25, .75, 'C+')}
def shifts(sel):  # sel: name -> effective input (p*m)
    a = dict(np_shift=0.0, fcf_shift=0.0, t0_bn=0.0)
    for k, x in sel.items(): a[{'np': 'np_shift', 'fcf': 'fcf_shift', 't0': 't0_bn'}[IT[k][0]]] += x
    return a
items = {}
for k, (kind, m, lo, hi, p, plo, phi, bac) in IT.items():
    full = center(**shifts({k: m}))
    m_pct = full / C0 - 1
    ext = [center(**shifts({k: pp * mm})) / C0 - 1 for pp in (plo, phi) for mm in (lo, hi)]
    items[k] = dict(bac=bac, input=m, input_range=[lo, hi], m_pct=round(m_pct, 5), p=p, p_range=[plo, phi],
                    pm_pct=round(center(**shifts({k: p * m})) / C0 - 1, 5), pm_min=round(min(ext), 5), pm_max=round(max(ext), 5))
adj = center(**shifts({k: IT[k][4] * IT[k][1] for k in IT}))
# dai: moi hang muc chon cuc tri (p,m) cho tich nho nhat / lon nhat, chay to hop qua mo hinh
def pick(fn):
    sel = {}
    for k, (kind, m, lo, hi, p, plo, phi, bac) in IT.items():
        cands = [pp * mm for pp in (plo, phi) for mm in (lo, hi)]
        sel[k] = fn(cands)
    return sel
low, high = center(**shifts(pick(min))), center(**shifts(pick(max)))
lin = sum(v['pm_pct'] for v in items.values())
res = dict(center_base=round(C0), center_adj=round(adj), adj_pct=round(adj / C0 - 1, 5), range_low=round(low), range_high=round(high),
           sum_pm_linear_pct=round(lin, 5), items=items)
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(OUT, 'calc_adj_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
