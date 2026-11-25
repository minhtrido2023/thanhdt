"""dd_recheck w3 25/11 HPG (job Taylor_20261125_032443): E15 + dai Ke + do nhay r, CUNG mo hinh r3 (hpg_r3.py), chi doi r.
Nguon: dd_redo_20261105/HPG/calc_r3/hpg_r3.py (TRIM 19/11 commit 14ad1c925) — khoi phuc:
  git -C <mike> archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 | tar -x -C /tmp/ddrestore_w3a/mike
Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc_recheck.py /tmp/ddrestore_w3a/mike/agents/Taylor/research/dd_redo_20261105
(hpg_r3.py tu ghi lai out/SUMMARY trong thu muc khoi phuc /tmp — khong dung repo.) Mu gia: PX 21.200 (06/11) ke thua."""
import sys, os, io, json, hashlib, runpy, contextlib
ROOT = os.path.abspath(sys.argv[1]); HERE = os.path.join(ROOT, 'HPG', 'calc_r3')
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {'HPG/calc_r3/hpg_r3.py': '8fbf24506eb5d6da4e15ad049f4f3643', 'HPG/calc_r3/px_hpg_r3_20261106.csv': '03f82a271cf409843a6b063e8a564c2d',
        '_common_014125/r2common.py': 'b664ec37b7728c5ccaa06b0a77d7d76c', '_common_014125/bq_px_liq_20261104.csv': '442f39a3d556f43f75fa5f3f5519c2e9',
        '_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6', 'HPG/calc/hpg_r2.py': 'c6c7233a6589db20724d02e6f810879b',
        'HPG/calc_r3/summary_r3_extra.json': '5d78410454e689b3120691352d9e48cf'}
for k, v in LOCK.items(): assert md5(os.path.join(ROOT, k)) == v, k
buf = io.StringIO(); cwd = os.getcwd(); os.chdir(HERE)
with contextlib.redirect_stdout(buf): g = runpy.run_path(os.path.join(HERE, 'hpg_r3.py'), run_name='__main__')
os.chdir(cwd)
# CONTROL: stdout tru dong 'LOCK ...' (md5 tu in: duong dan tuong doi + file su kien lai suat repo ngoai da them dong 09/11, 16/11) phai trung hpg_r3_out.txt r3 cung phep loc
def nolock(t): return ''.join(l for l in t.splitlines(True) if not l.startswith('LOCK '))
ref = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ref_hpg_r3_out.txt')).read()
assert hashlib.md5(ref.encode()).hexdigest() == '72b260132c7e0d7996b12a9e11200d8f', 'ref r3 out lech LOCK'
ctrl_md5 = hashlib.md5(nolock(buf.getvalue()).encode()).hexdigest()
assert nolock(buf.getvalue()) == nolock(ref), 'CONTROL lech hpg_r3_out.txt (ngoai dong LOCK)'
assert md5(os.path.join(HERE, 'grid_hpg_r3.csv')) == 'b1c8c9ee83152330b4742df12b872f09'
run, FH, AXH, PX, D, R = g['run'], g['FH'], g['AXH'], g['PX'], g['D'], g['R']
base = run(FH, AXH, PX, D); assert (round(base['center']), round(base['p10']), round(base['p90'])) == (21338, 13316, 28993), base
pre = run(FH, AXH, PX, 0.0)
rows = []
for lab, r in [('12,3% E15/dau duoi Ke', 0.123), ('12,5% (-100bp)', R - 0.01), ('13,0% (-50bp)', R - 0.005), ('13,4% dau tren Ke', 0.134),
               ('13,5% BASE', R), ('14,0% (+50bp)', R + 0.005), ('14,5% (+100bp)', R + 0.01)]:
    s = run(FH, AXH, PX, D, r=r)
    rows.append(dict(label=lab, r=round(r, 4), center=round(s['center']), p10=round(s['p10']), p90=round(s['p90']),
                     d_center=round(s['center'] - base['center']), d_pct=round(s['center'] / base['center'] - 1, 4), pct_below_px=round(s['pct_below_px'], 4)))
res = dict(control_stdout_md5=ctrl_md5, r_base=R, center_pre_ck=round(pre['center']), ck=D, headline=dict(center=round(base['center']), p10=round(base['p10']), p90=round(base['p90'])), rows=rows)
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_recheck_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
