"""TCH recheck 24/11: chạy lại tch_r3b.py (KHÔNG sửa file gốc; exec bản sao md5 bc9a874f trong mirror/) ở các mức r
và CK holding trên phần công ty con. Đầu vào r3/r3b bị TRIM khỏi git ở 14ad1c925 ⇒ khôi phục từ fc5bd02d9 vào mirror/,
assert md5 khớp LOCK_md5.txt r3b. CONTROL: r=R0 (neo), hold=0 tái lập tâm trước CK 15.964 / sau CK 15.864, P10 14.563, P90 17.325.
Chỉ 3 thay thế văn bản lúc exec: (1) R0 override, (2) bỏ assert control r3 khi override, (3) nhân (1-HOLD) phần 'sub' (như tch_r3.py:41)."""
import hashlib, json, os, sys, io, contextlib
H = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(H, 'mirror')
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
LOCK = {'TCH/calc_r3b/tch_r3b.py': 'bc9a874fdcb2523d7f9585de92fb4770', 'TCH/calc_r3b/assumptions_r3b.json': '6a1f0e0dde520b5e95c3eff38dd45713',
        'TCH/calc_r3/assumptions_r3.json': 'a83ad010bdffb06bbfde1f5474c143fe', 'TCH/calc_r3/tch_r3_out.json': 'f4c0c2d3685156af2845bebdb56ce33f',
        '_shared/wpct.py': '4597bc083f0d64d8873141b12fbfb3a6', 'TCH/SUMMARY_r3b.json': 'b878186108a380860291ab50cc2328a3'}
for f, h in LOCK.items():
    assert md5(os.path.join(M, f)) == h, f
sys.path.insert(0, os.path.join(M, '_shared')); from wpct import wpct  # noqa
S3B = json.load(open(os.path.join(M, 'TCH/SUMMARY_r3b.json'))); d = S3B['liq_disc_5ty']; f5 = 1 - d
SRCF = os.path.join(M, 'TCH/calc_r3b/tch_r3b.py'); src = open(SRCF).read()
A = "DEP = effective_deposit_rate(ASOF); R0 = R_ANCHOR + 1.0 * (DEP['rate'] - DEP_ANCHOR)"
B = "assert abs(c_r3 - R3O['center_pre']) < 0.05, (c_r3, R3O['center_pre'])"
C = 'return (part["me"] + part["sub"]) / SH * 1000'
for s in (A, B, C):
    assert src.count(s) == 1, s
src = src.replace(A, A + "\nR0 = R_OVR if R_OVR is not None else R0").replace(B, "assert R_OVR is not None or HOLD or abs(c_r3 - R3O['center_pre']) < 0.05").replace(C, 'return (part["me"] + part["sub"] * (1 - HOLD)) / SH * 1000')
scratch = os.path.join(H, '_scratch', 'TCH', 'calc_r3b'); os.makedirs(scratch, exist_ok=True)
for sub in ('calc_r3',):
    dst = os.path.join(H, '_scratch', 'TCH', sub); os.makedirs(dst, exist_ok=True)
    for fn in os.listdir(os.path.join(M, 'TCH', sub)):
        open(os.path.join(dst, fn), 'wb').write(open(os.path.join(M, 'TCH', sub, fn), 'rb').read())
open(os.path.join(scratch, 'assumptions_r3b.json'), 'wb').write(open(os.path.join(M, 'TCH/calc_r3b/assumptions_r3b.json'), 'rb').read())
code = compile(src, SRCF, 'exec')
def run(r=None, hold=0.0):
    g = {'__file__': os.path.join(scratch, 'tch_r3b.py'), '__name__': 'm', 'R_OVR': r, 'HOLD': hold}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(code, g)
    V, W = g['V'], g['W']; c = g['c_b']; q = wpct(V, W, (0.10, 0.50, 0.90))
    return dict(r=round(g['R0'], 4), hold=hold, center_pre=round(c), center_post=round(c * f5), p10_post=round(q[0.10] * f5), p50_post=round(q[0.50] * f5), p90_post=round(q[0.90] * f5),
                g_audit_427_center_post=round(g['par']['g_audit_427']['center_pre'] * f5))
base = run()
assert (base['center_pre'], base['center_post'], base['p10_post'], base['p90_post']) == (15964, 15864, 14563, 17325), base
out = {'base': base}
for r in (0.123, 0.125, 0.130, 0.134, 0.140, 0.145):
    x = run(r); x['d_center_post'] = x['center_post'] - base['center_post']; x['d_pct'] = round((x['center_post'] / base['center_post'] - 1) * 100, 2); out[f'r{r:.3f}'] = x
for h in (0.20, 0.27):
    x = run(None, h); x['d_pct'] = round((x['center_post'] / base['center_post'] - 1) * 100, 2); out[f'hold{h:.2f}'] = x
x = run(0.123, 0.20); x['d_pct'] = round((x['center_post'] / base['center_post'] - 1) * 100, 2); out['r0.123_hold0.20'] = x
import shutil; shutil.rmtree(os.path.join(H, '_scratch'))
json.dump(out, open(os.path.join(H, 'calc_recheck_out.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
