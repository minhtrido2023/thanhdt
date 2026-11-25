"""SAS rev3 (đợt 4, job Taylor_20261125_063648). PREREG_rev3.md + calc/assumptions_rev3.json khoá TRƯỚC khi chạy (LOCK_rev3_md5.txt).
Chạy model_sas_r3.py đã khôi phục (git archive 14ad1c925^ agents/Taylor/research/dd_redo_20261105/SAS -> /tmp/ddrestore_w4sas) NGUYÊN VĂN,
chỉ bỏ assert md5 của data/deposit_rate_vn_events.csv (đã append sự kiện sau 08/11; assert r = 13,5% của model vẫn giữ) — như probe w3.
Base rev3 = r3 + B1 (D4: TV = E2028/r) + B2 (lãi tiền gửi Q4/26). E17 theo PREREG_rev3 §B.
Dùng: python3 model_sas_rev3.py <thư mục calc_r3 đã khôi phục>  (ghi model_sas_rev3_out.json cạnh file này)"""
import contextlib, hashlib, io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.dirname(HERE)
for ln in open(os.path.join(DIR, 'LOCK_rev3_md5.txt')):
    h, p = ln.split(None, 1); p = p.strip()
    assert hashlib.md5(open(os.path.join(DIR, p), 'rb').read()).hexdigest() == h, f"LOCK lệch: {p}"
A3 = json.load(open(os.path.join(HERE, 'assumptions_rev3.json')))
cdir = os.path.abspath(sys.argv[1]); mp = os.path.join(cdir, 'model_sas_r3.py')
assert hashlib.md5(open(mp, 'rb').read()).hexdigest() == 'e11b414e618abfa523fb60018d89edb5'
assert hashlib.md5(open(os.path.join(cdir, 'assumptions_r3.json'), 'rb').read()).hexdigest() == A3['inherits']['md5']
src = open(mp).read()
old = "    assert hashlib.md5(open(fp, 'rb').read()).hexdigest() == h, f\"LOCK lech: {p}\""
assert src.count(old) == 1
src = src.replace(old, "    if p.endswith('deposit_rate_vn_events.csv'): continue\n" + old)
g = {'__file__': mp, '__name__': 'm'}
cwd = os.getcwd(); os.chdir('/tmp')
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, mp, 'exec'), g)
os.chdir(cwd)
run, N0, LD, PX, BASE_R3, R, EPSR, DT, SH = g['run'], g['N0_r3'], g['LD'], g['PX'], g['BASE'], g['R'], g['EPSR'], g['DT'], g['SH']
assert round(g['H']['center_post']) == 31658 and abs(R - 0.135) < 1e-12

G0 = ((0.0,), (1.0,))  # B1: TV = E2028 / r
Q4I = A3['B2_q4_interest']['v'] * 0.8 * EPSR / (1 + R) ** DT  # B2
BASE = dict(BASE_R3, x=BASE_R3['x'] + Q4I, gs=G0)

def c(n0=N0, **kw):
    k = dict(BASE); dx = kw.pop('dx', 0.0); k.update(kw); k['x'] = k['x'] + dx
    s, _, _ = run('x', n0, LD, PX, **k); return s

H = c(); C0 = H['center_post']
pct = lambda s: s['center_post'] / C0 - 1
out = dict(ticker='SAS', rev=3, r=R, ld=LD, q4_interest_bn=Q4I, headline=H,
           control_r3=g['H']['center_post'], d4_only=c(x=BASE_R3['x'])['center_post'])

# độ nhạy r (E15, dải Ke, ±bp)
out['r_sens'] = {k: c(rshift=v)['center_post'] for k, v in
                 {'Ke12.3_E15': 0.123 - R, 'Ke13.4': 0.134 - R, '-100bp': -0.01, '-50bp': -0.005, '+50bp': 0.005, '+100bp': 0.01}.items()}
out['r_sens_p'] = {k: {kk: c(rshift=v)[kk] for kk in ('p10_post', 'p50_post', 'p90_post')} for k, v in {'Ke12.3_E15': 0.123 - R}.items()}
out['law_r3_ronic_inf'] = c(gs=(g['GS'], g['WG']))['center_post']

# E17 — hạng mục #1..#3 (PREREG_rev3 §B)
o = A3['op_9m']
op = {y: (o[y]['pbt'] - (o[y]['fin_rev'] - o[y]['fin_exp'])) * 0.8 for y in ('9M2025', '9M2026')}
mg = {y: op[y] / o[y]['rev'] for y in ('9M2025', '9M2026')}
mN0_full = mg['9M2025'] / mg['9M2026'] - 1
LR = A3['lt_recv_project']['v']; VAT = A3['vat_credit']['v']
items = {
  '1_N0_dinh_bien': dict(p=0.35, p_rng=(0.15, 0.55), full=lambda f: dict(n0=N0 * (1 + mN0_full * f)), m_rng=(0.5, 1.0), m_pt=1.0),
  '2_phai_thu_DH_du_an': dict(p=0.50, p_rng=(0.25, 0.75), full=lambda f: dict(dx=-LR * f), m_rng=(0.47, 1.0), m_pt=0.86),
  '3_thue_GTGT_khau_tru': dict(p=0.35, p_rng=(0.15, 0.55), full=lambda f: dict(dx=VAT * f), m_rng=(0.5, 1.0), m_pt=1.0),
}
for k, it in items.items():
    it['m'] = pct(c(**it['full'](it['m_pt'])))
    it['m_lo_hi'] = [pct(c(**it['full'](f))) for f in it['m_rng']]
sig = sum(it['p'] * it['m'] for it in items.values())

def combo(sel):  # sel: {k: (p, f)}; chạy MÔ HÌNH với tổ hợp
    n0 = N0; dx = 0.0
    for k, (p, f) in sel.items():
        kw = items[k]['full'](f)
        if 'n0' in kw: n0 = N0 * (1 + (kw['n0'] / N0 - 1) * p)
        dx += kw.get('dx', 0.0) * p
    return c(n0=n0, dx=dx)
adj = combo({k: (it['p'], it['m_pt']) for k, it in items.items()})
def extreme(lo):
    sel = {}
    for k, it in items.items():
        cands = [(p, f) for p in it['p_rng'] for f in it['m_rng']]
        vals = [(pct(combo({k: pf})), pf) for pf in cands]
        sel[k] = (min if lo else max)(vals)[1]
    return combo(sel), sel
lo, sel_lo = extreme(True); hi, sel_hi = extreme(False)
out['E17'] = dict(margin_op=mg, op_bn=op, mN0_full=mN0_full, sigma_linear=sig, center_linear=C0 * (1 + sig),
                  center_adj=adj['center_post'], range_low=lo['center_post'], range_high=hi['center_post'], sel_lo=sel_lo, sel_hi=sel_hi,
                  items={k: dict(p=it['p'], p_rng=it['p_rng'], m=it['m'], m_lo_hi=it['m_lo_hi'], m_pt=it['m_pt']) for k, it in items.items()})
# độ nhạy C (không vào tâm)
out['C_sens'] = {f'4_co_tuc_von_hoa_{D}': pct(c(ltinv=lambda r, D=D: D * EPSR / r)) for D in (12.8, 71.0, 100.0)}
out['C_sens']['6_HTK_-10pct'] = pct(c(dx=-0.1 * 204.335973162))
out['C_sens']['A6_bo_toan_bo_phai_thu_DH'] = pct(c(recv=False))

print(f"SAS rev3 | r {R:.2%} | CK 5 tỷ {LD:.2%} | lãi Q4 cộng {Q4I:.2f} tỷ ({Q4I/SH*1000*(1-LD):.0f} đ/cp sau CK)")
print(f"CONTROL r3 {out['control_r3']:,.0f} | chỉ D4 {out['d4_only']:,.0f} | HEADLINE rev3 tâm {C0:,.0f} (trước CK {H['center_pre']:,.0f}) "
      f"P10/P50/P90 {H['p10_post']:,.0f}/{H['p50_post']:,.0f}/{H['p90_post']:,.0f} | Δ vs r3 {C0/out['control_r3']-1:+.2%}")
for k, v in out['r_sens'].items(): print(f"  r {k:12s} {v:,.0f} ({v/C0-1:+.2%})")
print(f"  [LUẬT] r3 RONIC ngầm ∞ (g 2-4%) trên base rev3: {out['law_r3_ronic_inf']:,.0f} ({out['law_r3_ronic_inf']/C0-1:+.2%})")
print(f"E17: biên vh 9T/25 {mg['9M2025']:.2%} vs 9T/26 {mg['9M2026']:.2%} ⇒ m_N0 đủ {mN0_full:+.2%}")
for k, it in out['E17']['items'].items():
    print(f"  #{k}: p {it['p']} {it['p_rng']} m {it['m']:+.2%} (dải m {it['m_lo_hi'][0]:+.2%}..{it['m_lo_hi'][1]:+.2%}) p×m {it['p']*it['m']:+.2%}")
e = out['E17']
print(f"  Σp×m {e['sigma_linear']:+.2%} ⇒ tuyến tính {e['center_linear']:,.0f}; MÔ HÌNH tổ hợp {e['center_adj']:,.0f} ({e['center_adj']/C0-1:+.2%}); dải {e['range_low']:,.0f}–{e['range_high']:,.0f}")
for k, v in out['C_sens'].items(): print(f"  [C] {k}: {v:+.2%} ({C0*(1+v):,.0f})")
json.dump(out, open(os.path.join(HERE, 'model_sas_rev3_out.json'), 'w'), indent=1, default=float, ensure_ascii=False, sort_keys=True)
