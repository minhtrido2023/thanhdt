"""MVC recheck dot 2 (job Taylor_20261124_131351): E15 + dai Ke + do nhay r tren LUOI (157.464 ket cuc), CUNG mo hinh r3, CHI doi r;
+ do nhay chiet khau holding 20% (dai CK holding user chot 24/11: 0..+20%) tai tham so trung tam. KHONG sua file mo hinh.
Khoi phuc vao <root>/agents/Taylor/research: git archive 14ad1c925^ dd_redo_20261105/{MVC,NNC,common.py,_shared}; ef7472f56^ dd_NNC_20261030; bffae9c42^ dd_MVC_20261103.
Doi r: thay common.r_of => R = RR (mvc_redo_r3.py:33 gan N6.R_ANCHOR = R). Moi r 1 tien trinh con (module sach). 2 assert tai lap r2 (dong 97-98) chi dung o r goc => tat khi RR>0.
Chay: wc_venv python -I calc_recheck.py <root>/agents/Taylor/research"""
import sys, os, json, hashlib, subprocess
ROOT = os.path.abspath(sys.argv[1]); CALC = os.path.join(ROOT, 'dd_redo_20261105', 'MVC', 'calc_r3'); PY = sys.executable
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
for line in open(os.path.join(CALC, 'LOCK_r3_md5.txt')):
    if line.startswith('#') or not line.strip(): continue
    h, p = line.split(); p = p.replace('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research', ROOT)
    if p.endswith('deposit_rate_vn_events.csv'): continue   # file su kien them dong sau 06/11; lai hieu dung 06/11 doc lai van 7,40% (kiem o duoi)
    assert md5(p) == h, p
CHILD = r'''
import sys, os, json, __main__
CALC, RR = sys.argv[1], float(sys.argv[2])
sys.path.insert(0, os.path.abspath(os.path.join(CALC, '../..')))
import common as C
if RR > 0:
    C.r_of = lambda dep, beta=1.0: RR
os.chdir(CALC); f = os.path.join(CALC, 'mvc_redo_r3.py'); src = open(f, encoding='utf-8').read()
A2 = ["for cb in ('branch', '1.40'):\n        a = V8.branch(n, dict(NODELAY), cap_basis=cb)['vm']; b_ = branch(n, NODELAY, cap_basis=cb)['vm']; assert abs(a - b_) < 1e-6, (n, cb, a, b_)",
      "c0_r2 = EVc(); assert abs(c0_r2 - r2['center_param_nodelay']) < 1e-6, (c0_r2, r2['center_param_nodelay'])"]
for a in A2:
    assert src.count(a) == 1
    if RR > 0:
        src = src.replace(a, 'pass' if a.startswith('for') else 'c0_r2 = EVc()')
__main__.__file__ = f
exec(compile(src, f, 'exec'), __main__.__dict__)
g = __main__.__dict__
c0 = g['out']['center_param_nodelay']; x = g['EVc']({'hold': 0.20})
print('EXTRA ' + json.dumps(dict(dep=g['dep'], R=g['R'], c0=c0, hold20=x, hold20_d=x - c0)))
'''
def run(rr):
    p = subprocess.run([PY, '-B', '-c', CHILD, CALC, str(rr)], capture_output=True, text=True); assert p.returncode == 0, p.stderr[-3000:]
    o = json.load(open(os.path.join(CALC, 'mvc_redo_r3_out.json')))
    ex = json.loads([l for l in p.stdout.splitlines() if l.startswith('EXTRA ')][0][6:])
    return p.stdout, o, ex
def pick(o):
    s = o['post']; return dict(center=round(s['mean']), p10=round(s['p10']), p50=round(s['p50']), p90=round(s['p90']), center_pre=round(o['pre']['mean']))
so, o, ex = run(0)
body = so.split('EXTRA ')[0]
assert hashlib.md5(body.encode()).hexdigest() == '3b13f0612421e09b3e7dd9e60130cf4e', 'stdout CONTROL lech'
assert md5(os.path.join(CALC, 'mvc_redo_r3_out.json')) == 'c70f8350e52b945755373d1dd784d839'
base = pick(o); assert (base['center'], base['p10'], base['p90']) == (16241, 9940, 23471), base
assert abs(ex['dep'] - 0.074) < 1e-12 and abs(ex['R'] - 0.135) < 1e-12
res = {'0.135': dict(**base, d_vnd=0, d_pct=0.0)}; hold = dict(r135=ex)
for rr in (0.123, 0.125, 0.130, 0.134, 0.140, 0.145):
    _, oo, e2 = run(rr); s = pick(oo); s['d_vnd'] = s['center'] - base['center']; s['d_pct'] = round(100 * s['d_vnd'] / base['center'], 2); res[f'{rr:.3f}'] = s
    if rr == 0.123: hold['r123'] = e2
so2, _, _ = run(0)   # tra file output ve trang thai r3
assert md5(os.path.join(CALC, 'mvc_redo_r3_out.json')) == 'c70f8350e52b945755373d1dd784d839'
f5 = 1 - o['ck']['5ty']['adv250']
out = dict(ticker='MVC', ck_5ty=o['ck']['5ty']['adv250'], r_sens_grid=dict(sorted(res.items())),
           hold20_param=dict(c0_pre=round(ex['c0']), V_pre=round(ex['hold20']), d_pre=round(ex['hold20_d']), d_pct=round(100 * ex['hold20_d'] / ex['c0'], 2),
                              d_post_approx=round(ex['hold20_d'] * f5), note='tai tham so trung tam (nhu tornado r3 6%/15%), phan NNC'),
           tornado_r3={k: round(v['d']) for k, v in o['tornado'].items()}, V_NNC_implied_pre=round(o['V_NNC_implied_pre']), branch_post={k: round(v['mean']) for k, v in o['branch_post'].items()})
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calc_recheck_out.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
