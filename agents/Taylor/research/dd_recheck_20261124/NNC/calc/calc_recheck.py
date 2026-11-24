"""dd_recheck 24/11 NNC (job Taylor_20261124_095517): E15 + dai Ke + do nhay r, CUNG mo hinh r3, CHI doi r.
Mo hinh: dd_redo_20261105/NNC/calc/nnc_redo_r3.py (+ engine dd_NNC_20261030 r3..r6, dd_MVC_20261103 r6), bi TRIM khoi git 19/11.
Khoi phuc vao <root>=/tmp/ddrestore_B/agents/Taylor/research:
  git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 ; ef7472f56^ .../dd_NNC_20261030 ; bffae9c42^ .../dd_MVC_20261103
Doi r: thay common.r_of (dd_redo_20261105/common.py) => R cua r3 = r_moi; r3 tu gan N6.R_ANCHOR = R (wrapper N3.EV3 doc luc goi).
Moi r chay 1 tien trinh con rieng (trang thai module sach). Chay: wc_venv python -I calc_recheck.py <root>"""
import sys, os, json, hashlib, subprocess
ROOT = os.path.abspath(sys.argv[1]); CALC = os.path.join(ROOT, 'dd_redo_20261105', 'NNC', 'calc'); PY = sys.executable
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {'dd_redo_20261105/NNC/calc/assumptions_r3.json': 'c36da69593e28d05ad92acca530a2cb4', 'dd_redo_20261105/NNC/calc/nnc_redo_r3.py': '9b8969ec8ea8c2ba93728deb0caee45d',
 'dd_redo_20261105/NNC/calc/nnc_redo_r2_out.json': 'c1522cb0b75385543cd4a2d2c4a16470', 'dd_NNC_20261030/r6/calc/nnc_model_r6.py': '6688f1e61c8568f63fae889312462442',
 'dd_NNC_20261030/r6/calc/nnc_model_r6_out.json': '5f3c34d1269245483a87ceb9c7c72989', 'dd_NNC_20261030/r5/calc/nnc_model_r5.py': '14f3fb87c2d0b4c340382a371b26be29',
 'dd_NNC_20261030/r4/calc/model_r4.py': '812ca351e968913e2e4787bbcff9f552', 'dd_NNC_20261030/r3/calc/model_r3.py': 'c992769f86794f5d6f39b0df7e13bd91',
 'dd_MVC_20261103/r6/calc/model_r6.py': 'bd93107a93a7f958eea03e1a5f01eed0', 'dd_MVC_20261103/r6/calc/model_r5.py': '9fd64a26a7daca9b0244c3f62ce7dd91',
 'dd_MVC_20261103/r6/calc/valuation_base.py': 'd3fb9637389ca6d9c7472e28f4846506', 'dd_redo_20261105/common.py': 'e430be2363c19983d8d83120a3743e98',
 'dd_redo_20261105/_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6', 'dd_redo_20261105/NNC/calc/r3data/px_nnc_20261106.csv': '0bbe7eb7c315a48410d1265e39d8ea87'}
for k, v in LOCK.items(): assert md5(os.path.join(ROOT, k)) == v, k
CHILD = r'''
import sys, os
CALC, RR = sys.argv[1], float(sys.argv[2])
sys.path.insert(0, os.path.abspath(os.path.join(CALC, '../..')))
import common as C
if RR > 0:
    C.r_of = lambda dep, beta=1.0: RR
os.chdir(CALC); f = os.path.join(CALC, 'nnc_redo_r3.py'); src = open(f, encoding='utf-8').read()
A2 = ["assert abs(c0_r2 - r2['center_param_nodelay']) < 1e-6, (c0_r2, r2['center_param_nodelay'])",
      "assert abs(br['r2_rebuild']['mean'] - r2['pre']['mean']) < 1e-6, (br['r2_rebuild']['mean'], r2['pre']['mean'])"]
for a in A2:
    assert src.count(a) == 1
    if RR > 0:  # 2 kiem tai lap r2 chi dung o r 13,5% (da chay o CONTROL)
        src = src.replace(a, 'pass')
exec(compile(src, f, 'exec'), {'__name__': '__main__', '__file__': f})
'''
def run(rr):
    p = subprocess.run([PY, '-I', '-B', '-c', CHILD, CALC, str(rr)], capture_output=True, text=True); assert p.returncode == 0, p.stderr[-2000:]
    o = json.load(open(os.path.join(CALC, 'nnc_redo_r3_out.json'))); return p.stdout, o
# CONTROL: r goc (0 = khong doi) => trung byte r3
so, o = run(0)
assert hashlib.md5(so.encode()).hexdigest() == '857c7adb3a319e2a819cbfa4de08caa4', ('stdout CONTROL lech', hashlib.md5(so.encode()).hexdigest())
assert md5(os.path.join(CALC, 'nnc_redo_r3_out.json')) == '02a4e6ca744e2390367103f7296e12be'
base = o['post']; assert round(base['mean']) == 61273 and round(base['p10']) == 30375 and round(base['p90']) == 95341 and abs(o['r'] - 0.135) < 1e-12
rows = []
for lab, rr in [('12,3% E15/dau duoi Ke', 0.123), ('12,5% (-100bp)', 0.125), ('13,0% (-50bp)', 0.130), ('13,4% dau tren Ke', 0.134),
                ('13,5% BASE', 0.135), ('14,0% (+50bp)', 0.140), ('14,5% (+100bp)', 0.145)]:
    _, x = run(rr); s = x['post']; assert abs(x['r'] - rr) < 1e-12
    rows.append(dict(label=lab, r=rr, center=round(s['mean']), p10=round(s['p10']), p90=round(s['p90']), d_center=round(s['mean'] - base['mean']),
                     d_pct=round(s['mean'] / base['mean'] - 1, 4), pct_below_px=round(x['pct_weight_below_price'], 4), center_pre=round(x['pre']['mean'])))
_ = run(0)  # tra lai output r3 goc trong thu muc khoi phuc
assert md5(os.path.join(CALC, 'nnc_redo_r3_out.json')) == '02a4e6ca744e2390367103f7296e12be'
res = dict(control_stdout_md5='857c7adb3a319e2a819cbfa4de08caa4', r_base=0.135, ck_ref=o['ck_ref'], center_pre=round(o['pre']['mean']), rows=rows)
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_recheck_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
