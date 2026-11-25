"""dd_recheck w3 25/11 SZL (job Taylor_20261125_053004): E15 + dai Ke + do nhay r +-50/100bp, CUNG mo hinh rev5 (khong sua).
Chay: /home/trido/thanhdt/wc_venv/bin/python calc_recheck.py <worktree>/agents/Taylor/research/dd_redo_20261105/SZL/rev5/calc
Mu gia: khong doc gia moi; gia 27.700 (06/11) chi dung trong model rev5 cho CK + nhan (ke thua)."""
import sys, os, io, json, hashlib, contextlib, importlib.util
HERE = os.path.abspath(sys.argv[1]); OUT = os.path.dirname(os.path.abspath(__file__))
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
for ln in open(os.path.join(HERE, 'LOCK_rev5_prerun.txt')):
    if ln.startswith('#') or not ln.strip(): continue
    h, p = ln.split(None, 1); p = p.strip(); f = p if p.startswith('/') else os.path.join(HERE, p)
    assert md5(f) == h, p
spec = importlib.util.spec_from_file_location('model_rev5', os.path.join(HERE, 'model_rev5.py')); M = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()) as b: spec.loader.exec_module(M)
assert hashlib.md5(b.getvalue().encode()).hexdigest() == md5(os.path.join(HERE, 'model_rev5_out.txt')), 'CONTROL lech'
s5, s40 = M.run()
assert round(s5['center_post']) == 26183 and round(s5['p10_post']) == 22740 and round(s5['p90_post']) == 29700, s5
rows = []
for lab, r in [('12,3% E15/dau duoi Ke', .123), ('12,5% (-100bp)', M.R - .01), ('13,0% (-50bp)', M.R - .005), ('13,4% dau tren Ke', .134),
               ('13,5% BASE', M.R), ('14,0% (+50bp)', M.R + .005), ('14,5% (+100bp)', M.R + .01)]:
    a, c = M.run(r0=r)
    rows.append(dict(label=lab, r=round(r, 4), center=round(a['center_post']), p10=round(a['p10_post']), p90=round(a['p90_post']),
                     d_pct=round(a['center_post'] / s5['center_post'] - 1, 4), center_40=round(c['center_post']),
                     pct_below_px=round(a['pct_w_below_px'], 4), lab5=M.lab(M.PX, a), lab40=M.lab(M.PX, c)))
res = dict(r_base=M.R, base=dict(center=round(s5['center_post']), p10=round(s5['p10_post']), p90=round(s5['p90_post']), center_40=round(s40['center_post'])), rows=rows)
print(json.dumps(res, ensure_ascii=False, indent=1))
json.dump(res, open(os.path.join(OUT, 'calc_recheck_out.json'), 'w'), ensure_ascii=False, indent=1, sort_keys=True)
