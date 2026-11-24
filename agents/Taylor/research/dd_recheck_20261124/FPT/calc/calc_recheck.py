"""dd_recheck 24/11 FPT (job Taylor_20261124_095517): E15 + dai Ke + do nhay r, CUNG mo hinh r3, chi doi r.
Nguon mo hinh: dd_redo_20261105/FPT/calc_r3/model_r3.py (bi TRIM 19/11 commit 14ad1c925) — khoi phuc:
  git -C <mike> archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 | tar -x -C /tmp/ddrestore_B
Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc_recheck.py /tmp/ddrestore_B/agents/Taylor/research/dd_redo_20261105
Mu gia: khong doc gia moi; PX 50.800 (06/11) chi do model_r3 dung cho %duoi gia (ke thua)."""
import sys, os, io, json, hashlib, runpy, contextlib
ROOT = os.path.abspath(sys.argv[1]); HERE = os.path.join(ROOT, 'FPT', 'calc_r3')
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {'FPT/calc_r3/assumptions_r3.json': 'a873ef0eb43c9d1354f2b376e916064f', 'FPT/calc_r3/model_r3.py': 'c15138774b3da3a33625201fcf08f082',
        'FPT/calc_r3/px_fpt_r3_20261106.csv': '1ef90b777cee2199dcc0defe4f48aabd', 'FPT/calc/fpt_r2.py': 'e6d0ac32e6f6374afcf2c9cd2e8bba21',
        'FPT/calc/assoc_px_20261104.csv': '33772a6e33add436e5732eb65929eb1f', '_common_014125/r2common.py': 'b664ec37b7728c5ccaa06b0a77d7d76c',
        '_common_014125/common.py': '89e390381402790204264c5c2ae1254a', '_common_014125/bq_px_liq_20261104.csv': '442f39a3d556f43f75fa5f3f5519c2e9',
        '_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6'}
for k, v in LOCK.items(): assert md5(os.path.join(ROOT, k)) == v, k
buf = io.StringIO()
with contextlib.redirect_stdout(buf): g = runpy.run_path(os.path.join(HERE, 'model_r3.py'), run_name='__main__')
out = buf.getvalue()
ctrl_md5 = hashlib.md5(out.encode()).hexdigest()
assert ctrl_md5 == '51b85a478e8b72288fe2d2f3665f55dc', ('CONTROL lech run1.txt', ctrl_md5)
assert md5(os.path.join(HERE, 'model_r3_out.json')) == '17ddd898d55fefa464eac0b97037615e'
run, BASE, PX, D, R = g['run'], g['BASE_CFG'], g['PX'], g['D'], g['R']
base, _ = run(BASE, PX, D); assert round(base['center']) == 57312 and round(base['p10']) == 45270 and round(base['p90']) == 68466
pre, _ = run(BASE, PX, 0.0)
rows = []
for lab, r in [('12,3% E15/dau duoi Ke', 0.123), ('12,5% (-100bp)', R - 0.01), ('13,0% (-50bp)', R - 0.005), ('13,4% dau tren Ke', 0.134),
               ('13,5% BASE', R), ('14,0% (+50bp)', R + 0.005), ('14,5% (+100bp)', R + 0.01)]:
    s, _ = run(BASE, PX, D, r=r)
    rows.append(dict(label=lab, r=round(r, 4), center=round(s['center']), p10=round(s['p10']), p90=round(s['p90']),
                     d_center=round(s['center'] - base['center']), d_pct=round(s['center'] / base['center'] - 1, 4), pct_below_px=round(s['pct_below_px'], 4)))
# D4: ban G (RONIC 5 nam chan Ke) o r 12,3% de doc kem
gG, _ = run(dict(BASE, cap=0.123), PX, D, r=0.123)
res = dict(control_stdout_md5=ctrl_md5, r_base=R, center_pre_ck=round(pre['center']), ck=D, rows=rows,
           altG_at_123=dict(center=round(gG['center']), p10=round(gG['p10']), p90=round(gG['p90'])))
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_recheck_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
