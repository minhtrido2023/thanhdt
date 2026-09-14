import os, subprocess, sys
src = open('oshares_live.py', encoding='utf-8').read()
M = {
 'M1_fparts_gt1_off': ('    if len(fparts) > 1:\n', '    if False:\n'),
 'M1b_fparts_ge1':    ('    if len(fparts) > 1:\n', '    if len(fparts) >= 1:\n'),
 'M2_skip_empty':     ('    skip = {id(e) for e in not_absorbed}\n', '    skip = set()\n'),
 'M3_back_unsz_off':  ('    if fp and any(s is None for s in bsz):\n', '    if False:\n'),
 'M4_skipunsz_off':   ('    if any(s is None for s in fsz):\n        rep["verdict"], rep["absorbed"] = "SKIPPED_UNSIZABLE", []', '    if False:\n        rep["verdict"], rep["absorbed"] = "SKIPPED_UNSIZABLE", []'),
 'M5_cap_99':         ('    if len(pool) > 14:\n        return _amb', '    if len(pool) > 99:\n        return _amb'),
 'M5b_cap_13':        ('    if len(pool) > 14:\n        return _amb', '    if len(pool) > 13:\n        return _amb'),
 'M6_noprior_off':    ('        if not prior_ais:\n            return _amb', '        if False:\n            return _amb'),
 'M7_drop_off':       ('            if absorbed:\n                drop = ', '            if False:\n                drop = '),
}
procs = {}
for name, (a, b) in M.items():
    assert src.count(a) == 1, name
    d = f'/tmp/osfx/mut/{name}'; os.makedirs(d, exist_ok=True)
    open(f'{d}/oshares_live.py', 'w', encoding='utf-8').write(src.replace(a, b))
    env = dict(os.environ, PYTHONPATH=os.getcwd()); env.pop('TZ', None)
    procs[name] = subprocess.Popen([sys.executable, f'{d}/oshares_live.py', '--selfcheck'],
                                   stdout=open(f'{d}/out.txt', 'w'), stderr=subprocess.STDOUT, env=env)
for name, p in procs.items():
    rc = p.wait()
    out = open(f'/tmp/osfx/mut/{name}/out.txt', encoding='utf-8').read()
    fails = [l.split('  ')[2][:6] for l in out.splitlines() if l.startswith('  FAIL')]
    tb = 'Traceback' in out
    last = [l for l in out.splitlines() if l.startswith(('FAILED', 'OK', 'ModuleNotFound'))]
    print(f'{name}: rc={rc} crash={tb} fails={fails} {last[-1][:120] if last else ""}')
    if tb: print('   ', [l for l in out.splitlines() if 'Error' in l][-1:])
