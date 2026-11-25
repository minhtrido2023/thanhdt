"""SAS Bước 0 probe (dd_recheck w3, job Taylor_20261125_053002). Đo, KHÔNG phải tâm mới.
Chạy model_sas_r3.py đã khôi phục (git archive 14ad1c925^ -> /tmp/ddrestore_w3a/mike) NGUYÊN VĂN, chỉ bỏ assert md5 của
data/deposit_rate_vn_events.csv (file đã append sự kiện sau 08/11; assert r = 13,5% của model vẫn giữ).
D4 (user 22/11 19:07): terminal RONIC = Ke ⇒ TV = E/r (g không tạo giá trị) ⇒ lưới với g = 0.
Dùng: python3 step0_probe_sas.py <thư mục calc_r3 đã khôi phục>"""
import contextlib, io, os, sys
cdir = os.path.abspath(sys.argv[1]); mp = os.path.join(cdir, 'model_sas_r3.py')
src = open(mp).read()
old = "    assert hashlib.md5(open(fp, 'rb').read()).hexdigest() == h, f\"LOCK lech: {p}\""
assert src.count(old) == 1
src = src.replace(old, "    if p.endswith('deposit_rate_vn_events.csv'): continue\n" + old)
g = {'__file__': mp, '__name__': 'm'}
os.chdir('/tmp')
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, mp, 'exec'), g)
run, N0, LD, PX, BASE, R = g['run'], g['N0_r3'], g['LD'], g['PX'], g['BASE'], g['R']
H = g['H']; assert round(H['center_post']) == 31658, H['center_post']
G0 = ((0.0,), (1.0,))
def c(**kw):
    s, _, _ = run('x', N0, LD, PX, **BASE, **kw); return s
rows = [('r3 headline (sổ rev2)', c()), ('D4: RONIC = Ke (g=0)', c(gs=G0)),
        ('r3 @ Ke 12,3% (E15)', c(rshift=0.123 - R)), ('D4 @ Ke 12,3% (E15)', c(gs=G0, rshift=0.123 - R)),
        ('D4 @ Ke 13,4%', c(gs=G0, rshift=0.134 - R))]
for bp in (-100, -50, 50, 100):
    rows.append((f'D4 r {bp:+d}bp', c(gs=G0, rshift=bp / 1e4)))
base = rows[0][1]['center_post']; d4 = rows[1][1]['center_post']
print(f"r = {R:.4f} (assert model: r_of(current_dep 06/11) = 13,5%)")
for nm, s in rows:
    print(f"{nm:28s} tâm trước/sau CK {s['center_pre']:8,.0f} / {s['center_post']:8,.0f}  P10/P50/P90 sau CK "
          f"{s['p10_post']:,.0f}/{s['p50_post']:,.0f}/{s['p90_post']:,.0f}  Δ vs r3 {s['center_post']/base-1:+.2%}  Δ vs D4 {s['center_post']/d4-1:+.2%}")
