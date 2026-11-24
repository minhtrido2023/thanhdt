"""dd_recheck dot 2 (24/11) MBB (job Taylor_20261124_131354): E15 + dai Ke + do nhay r, CUNG mo hinh r3, chi doi r.
Nguon mo hinh: dd_redo_20261105/MBB/calc_r3/mbb_r3.py (bi TRIM 19/11 commit 14ad1c925) — khoi phuc:
  git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105 agents/Taylor/research/dd_MBB_20261031 | tar -x -C /tmp/ddrestore_MBB
Chay: /home/trido/thanhdt/wc_venv/bin/python -I calc_recheck.py /tmp/ddrestore_MBB/agents/Taylor/research/dd_redo_20261105
CONTROL: stdout mbb_r3.py trung run2.txt r3 tru cac dong 'LOCK' (data/deposit_rate_vn_events.csv da them su kien sau 08/11;
  lai 12T hieu dung tai 03/11, 06/11, 24/11 deu 7,40% cctg_12m(2026-11-02) => r khong doi).
Mu gia: khong doc gia moi; PX 19.250 (06/11) ke thua r3 chi cho %duoi gia."""
import sys, os, io, json, hashlib, runpy, contextlib
ROOT = os.path.abspath(sys.argv[1]); HERE = os.path.join(ROOT, 'MBB', 'calc_r3')
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {'MBB/calc_r3/mbb_r3.py': 'f5ad8f9ed0b3761de289f918e17ba679', 'MBB/calc_r3/px_mbb_r3_20261106.csv': '606e2f65e2648e3fd6ae4e1cf29c8c0a',
        '_common_014125/r2common.py': 'b664ec37b7728c5ccaa06b0a77d7d76c', '_common_014125/bq_px_liq_20261104.csv': '442f39a3d556f43f75fa5f3f5519c2e9',
        '_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6', 'MBB/calc/mbb_r2.py': 'e918d858b4355d3a116a82ec20baeab2',
        'MBB/calc_r3/summary_r3_extra.json': '3b6c133994a1e9fa09752f1a75f77f65', 'MBB/calc_r3/run2.txt': '1c79f8d0e30ea005501c9a4b1ccba5a3'}
for k, v in LOCK.items(): assert md5(os.path.join(ROOT, k)) == v, k
ref = [l for l in open(os.path.join(HERE, 'run2.txt')).read().splitlines() if not l.startswith('LOCK')]
buf = io.StringIO()
with contextlib.redirect_stdout(buf): g = runpy.run_path(os.path.join(HERE, 'mbb_r3.py'), run_name='__main__')
got = [l for l in buf.getvalue().splitlines() if not l.startswith('LOCK')]
assert got == ref, 'CONTROL lech run2.txt (ngoai dong LOCK)'
ctrl_md5 = hashlib.md5('\n'.join(got).encode()).hexdigest()
run, FH, AXH, PX, D, R, make_fn, DAYS = (g[k] for k in ('run', 'FH', 'AXH', 'PX', 'D', 'R', 'make_fn', 'DAYS'))
assert abs(R - 0.135) < 1e-12
base = run(FH, AXH, PX, D); assert (round(base['center']), round(base['p10']), round(base['p90'])) == (21069, 14729, 27577)
rows = []
for lab, r in [('12,3% E15/dau duoi Ke', 0.123), ('12,5% (-100bp)', R - 0.01), ('13,0% (-50bp)', R - 0.005), ('13,4% dau tren Ke', 0.134),
               ('13,5% BASE', R), ('14,0% (+50bp)', R + 0.005), ('14,5% (+100bp)', R + 0.01)]:
    s = run(FH, AXH, PX, D, r=r)
    rows.append(dict(label=lab, r=round(r, 4), center=round(s['center']), p10=round(s['p10']), p90=round(s['p90']),
                     d_center=round(s['center'] - base['center']), d_pct=round(s['center'] / base['center'] - 1, 4), pct_below_px=round(s['pct_below_px'], 4)))
# ban F (ROE_T -2pp) va G (+2pp) o r 12,3% de doc kem
alt = {k: run(make_fn(DAYS, 'npv0', x), AXH, PX, D, r=0.123) for k, x in (('F_ROE_T_-2pp', -0.02), ('G_ROE_T_+2pp', 0.02))}
res = dict(control_nonlock_md5=ctrl_md5, r_base=R, ck=D, rows=rows, alt_at_123={k: dict(center=round(s['center']), p10=round(s['p10']), p90=round(s['p90'])) for k, s in alt.items()})
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_recheck_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
