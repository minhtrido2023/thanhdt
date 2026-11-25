"""dd_recheck w3 25/11 DDV (job Taylor_20261125_032443): E15 + dai Ke + do nhay r, CUNG mo hinh r3, chi doi r.
Nguon: dd_redo_20261105/DDV/calc_r3/model_r3.py (TRIM 19/11 commit 14ad1c925) — khoi phuc:
  git -C <mike> archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 | tar -x -C /tmp/ddrestore_w3a/mike
Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc_recheck.py /tmp/ddrestore_w3a/mike/agents/Taylor/research/dd_redo_20261105
Mu gia: khong doc gia moi; PX 15.200 (06/11) chi do model_r3 dung cho %duoi gia (ke thua)."""
import sys, os, io, json, hashlib, runpy, contextlib
ROOT = os.path.abspath(sys.argv[1]); HERE = os.path.join(ROOT, 'DDV', 'calc_r3')
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {'DDV/calc_r3/assumptions_r3.json': '0e62e59d6175ef01d6329a44737d7520', 'DDV/calc_r3/model_r3.py': '0432190ecbb23aa0783f47bd0e3190c0',
        'DDV/calc/model.py': '3a69ce4b7259927e765cf26e3e97ccdf', 'DDV/calc/model_r2.py': 'c6de17ba62919418803ebb51a338c95a',
        'DDV/calc/bq_hist_out.csv': '6b504e226be3c465c7efe6fdc71be3f5', 'DDV/calc_r3/px_ddv_r3_20261106.csv': 'aec440d99cc8e41a1df601b7b574987a',
        '_common_014127/common.py': '24943cb1a1d35d91bee6ca1fab9d7202', '_common_014127/common_r2.py': '95da3038b3710b57e66747acfcd95722',
        '_common_014127/bq_px_liq_20261104.csv': 'c64ac0755af0994244487184b1eabf3e', '_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6'}
for k, v in LOCK.items(): assert md5(os.path.join(ROOT, k)) == v, k
buf = io.StringIO()
cwd = os.getcwd(); os.chdir(HERE)
with contextlib.redirect_stdout(buf): g = runpy.run_path(os.path.join(HERE, 'model_r3.py'), run_name='__main__')
os.chdir(cwd)
out = buf.getvalue(); ctrl_md5 = hashlib.md5(out.encode()).hexdigest()
assert ctrl_md5 == 'eeee072ded0755b471a9143fc61ad130', ('CONTROL lech run1.txt', ctrl_md5)
assert md5(os.path.join(HERE, 'model_r3_out.json')) == 'd452a7dee93eac03f1cdf08c7f6714be', 'model_r3_out.json lech LOCK phan 2'
grid, summ, R3CFG, RPTS, R0, A = g['grid'], g['summ'], g['R3CFG'], g['RPTS'], g['R0'], g['A']
H = summ(*grid(R3CFG)); assert (H['center_post'], H['p10'], H['p90']) == (15911, 13315, 18573), H
def at(r):  # chi doi tam truc r, giu truc +-bp va trong so
    return summ(*grid(R3CFG, rpts=[(r + bp / 1e4, w) for bp, w in zip(A['r_axis_bp'], A['r_axis_w'])]))
rows = []
for lab, r in [('12,3% E15/dau duoi Ke', 0.123), ('12,5% (-100bp)', R0 - 0.01), ('13,0% (-50bp)', R0 - 0.005), ('13,4% dau tren Ke', 0.134),
               ('13,5% BASE', R0), ('14,0% (+50bp)', R0 + 0.005), ('14,5% (+100bp)', R0 + 0.01)]:
    s = at(r)
    rows.append(dict(label=lab, r=round(r, 4), center=s['center_post'], p10=s['p10'], p90=s['p90'], label_zone=s['label'],
                     d_center=s['center_post'] - H['center_post'], d_pct=round(s['center_post'] / H['center_post'] - 1, 4), below=s['below']))
res = dict(control_stdout_md5=ctrl_md5, r_base=R0, r_axis_bp=A['r_axis_bp'], r_axis_w=A['r_axis_w'], headline=H, rows=rows)
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_recheck_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
