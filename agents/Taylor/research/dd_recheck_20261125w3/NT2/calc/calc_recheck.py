"""dd_recheck w3 25/11 NT2 (job Taylor_20261125_032446): E15 + dai Ke + do nhay r, CUNG mo hinh r3, chi doi r.
Nguon: dd_redo_20261105/NT2/calc_r3/model_r3.py (TRIM 19/11 commit 14ad1c925) — khoi phuc:
  git -C <mike> archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105/{NT2,_common_020021,_common,_shared,...} | tar -x -C /tmp/ddrestore_NT2
Chay: /home/trido/thanhdt/wc_venv/bin/python calc_recheck.py /tmp/ddrestore_NT2/agents/Taylor/research/dd_redo_20261105
Mu gia: khong doc gia moi; PX 22.200 (06/11) chi do model_r3 dung cho % duoi gia (ke thua)."""
import sys, os, io, json, hashlib, runpy, contextlib
ROOT = os.path.abspath(sys.argv[1]); HERE = os.path.join(ROOT, 'NT2', 'calc_r3')
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {}
for ln in open(os.path.join(HERE, 'LOCK_md5.txt')):
    if ln.startswith('#') or not ln.strip(): continue
    h, p = ln.split()[:2]
    if not p.startswith('/') and 'make_summary' not in p and 'REPORT_r3' not in p and 'SUMMARY.json' not in p and '5F' not in p: LOCK[p] = h
for k, v in LOCK.items(): assert md5(os.path.join(ROOT, k)) == v, k
buf = io.StringIO()
cwd = os.getcwd(); os.chdir(HERE)
with contextlib.redirect_stdout(buf): g = runpy.run_path(os.path.join(HERE, 'model_r3.py'), run_name='__main__')
os.chdir(cwd)
out = buf.getvalue(); ctrl_md5 = hashlib.md5(out.encode()).hexdigest()
assert ctrl_md5 == open(os.path.join(HERE, 'run1.md5')).read().split()[0], ('CONTROL lech model_r3_out.txt r3', ctrl_md5)
run, Q, A, R, S = g['run'], g['Q'], g['A'], g['R'], g['S']
assert round(S['center_post']) == 24003 and round(S['p10_post']) == 18301 and round(S['p90_post']) == 29619
def at(r):
    s, _, _ = run(Q, r=([r + o for o in A['r_offsets']], A['r_weights'])); return s
rows = []
for lab, r in [('12,3% E15/dau duoi Ke', 0.123), ('12,5% (-100bp)', R - 0.01), ('13,0% (-50bp)', R - 0.005), ('13,4% dau tren Ke', 0.134),
               ('13,5% BASE', R), ('14,0% (+50bp)', R + 0.005), ('14,5% (+100bp)', R + 0.01)]:
    s = at(r)
    rows.append(dict(label=lab, r=round(r, 4), center=round(s['center_post']), p10=round(s['p10_post']), p90=round(s['p90_post']),
                     d_center=round(s['center_post'] - S['center_post']), d_pct=round(s['center_post'] / S['center_post'] - 1, 4), pct_below_px=round(s['pct_w_below_px'], 4)))
# deposit rate hom nay (buoc 0: delta so neo 03/11)
sys.path.insert(0, '/home/trido/thanhdt/WorkingClaude'); import deposit_rate_vn as dr
dep_now = dr.effective_deposit_rate('2026-11-25')
res = dict(control_stdout_md5=ctrl_md5, r_base=R, center_pre=round(S['center_pre']), rows=rows,
           dep_now=dict(rate=dep_now['rate'], src=dep_now['rate_source']))
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_recheck_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True, default=str)
