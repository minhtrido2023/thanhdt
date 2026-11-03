"""DD DRI r5 (job Taylor_20261103_160959, 03/11/2026). MU GIA. Dang ky truoc: ../PREREG_r5.md (commit cee65d404).
Engine: exec NGUYEN VAN ../../../dri_val_supply_adj_r4_20261027/model.py (va r3 ben trong), voi `open` CHUYEN HUONG
2 file song cua WorkingClaude/data (rubber_monthly.csv, macro_usdvnd.csv) sang snapshot data/ (nam trong LOCK).
Chay: python3 -B dri_model_r5.py (tu thu muc nay).
Sua so voi r4 (SKEPTIC_R4_20261103.md):
 1. mid = TB thuc RSS3 2014-01..2026-09 (bo 2013 = duoi sieu chu ky); luoi mid DOI XUNG {P25, TB, P75} cung cua so
    (bo 'TB 2006-26'). Do nhay cua so: 10 nam truot, nam tron 2014-25, 2013-26 (r4), day-day 2016-23.
 2. L_tap {22,27,32} = GIA DINH (khong co dinh muc nguon); bao them L24.
 3. Dien giai NPV0 tai canh: bao song song 'C-thanh ly' (thanh ly khoi 2029-36 la quyet dinh tai san hien huu,
    khong trong lai) + XDCB — KHONG vao base.
 4. Kich ban tai canh bi buoc = T1 cu + XDCB 72,71 ty (r4 thieu XDCB). p = 20% nhan dinh; do nhay p 0/10/20/30%.
 5. Snapshot du lieu song vao LOCK.
"""
import os, io, csv, json, builtins, contextlib, itertools, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
WC = '/home/trido/thanhdt/WorkingClaude/data'
REDIR = {f'{WC}/rubber_monthly.csv': os.path.join(HERE, 'data/rubber_monthly_snapshot_20261103.csv'),
         f'{WC}/macro_usdvnd.csv': os.path.join(HERE, 'data/macro_usdvnd_snapshot_20261103.csv')}
SEEN = []
def _open(p, *a, **k):
    p2 = REDIR.get(os.path.abspath(str(p)), p)
    assert not str(p2).startswith(WC), f'doc file song {p2}'
    SEEN.append(os.path.abspath(str(p2))); return builtins.open(p2, *a, **k)
ENG = os.path.abspath(os.path.join(HERE, '../../../dri_val_supply_adj_r4_20261027/model.py'))
ns = {'__file__': ENG, '__name__': 'eng', 'open': _open}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(builtins.open(ENG, encoding='utf-8').read(), ENG, 'exec'), ns)
assert all(not s.startswith(WC) for s in SEEN) and any('rubber_monthly_snapshot' in s for s in SEEN), SEEN
fvph, CEN, SH, build3, D_V = ns['fvph'], ns['CEN'], ns['SH'], ns['build3'], ns['D_V']
R_ANCHOR, DEP_ANCHOR, PI = 0.135, 0.0740, ns['PI']
def r_of(dep, beta=1.0): return R_ANCHOR + beta*(dep - DEP_ANCHOR)
CIP = 72.712702447; CIPPS = CIP*1e9/SH                  # XDCB do dang 30/09/2026, ty [BCTC3 CDKT 252]
out = {'files_read': sorted({os.path.relpath(s, HERE) for s in SEEN})}
def base(mid, L=27, r=R_ANCHOR):
    CEN['r'] = r; return fvph(mid, 2029, L, R_on=False, new_on=False) + CIPPS
def liqread(mid, L=27, r=R_ANCHOR):                    # dien giai khac: thanh ly khoi 2029-36, khong trong lai
    CEN['r'] = r; return fvph(mid, 2029, L, new_on=False) + CIPPS
def forced(mid, L=27, r=R_ANCHOR):                     # T1 cu (thanh ly + trong lai, capex 172,6 tr/ha) + XDCB
    CEN['r'] = r; return fvph(mid, 2029, L) + CIPPS

# ---------- 0. SELFCHECK ----------
CEN['r'] = 0.12
assert [round(fvph(m, 2029, 27)) for m in (1.97, 2.18)] == [9078, 11116]
assert [round(fvph(m, 2029, 27, R_on=False, new_on=False)) for m in (1.97, 2.18)] == [13096, 15172]
cpi = {r['observation_date'][:7]: float(r['CPIAUCSL']) for r in csv.DictReader(builtins.open(os.path.join(HERE, 'data/fred_cpiaucsl_20261103.csv'))) if r['CPIAUCSL']}
cpi['2025-10'] = (cpi['2025-09'] + cpi['2025-11'])/2
rss = [(m, float(p)) for m, p in csv.reader(builtins.open(os.path.join(HERE, 'data/rubber_monthly_snapshot_20261103.csv'))) if m != 'month']
c25 = st.mean([cpi[f'2025-{i:02d}'] for i in range(1, 13)])
real = {m: p*c25/cpi[m] for m, p in rss if m in cpi}
def win(a, b): return [v for m, v in real.items() if a <= m <= b]
m13 = st.mean(win('2013-01', '2026-09'))
assert round(base(m13)) == 16950, base(m13)
print(f"0) SELFCHECK PASS: engine cu 9.078/11.116 & 13.096/15.172 @r12; r4 tam 16.950 @mid {m13:.3f} (snapshot, khong file song)")

# ---------- 1. Mid ----------
w = win('2014-01', '2026-09')
def pct(xs, q):
    xs = sorted(xs); i = q*(len(xs)-1); lo = int(i); return xs[lo] + (xs[min(lo+1, len(xs)-1)] - xs[lo])*(i-lo)
MID = {'P25': pct(w, .25), 'TB': st.mean(w), 'P75': pct(w, .75)}
WINS = {'2014-01..2026-09 (CHON)': ('2014-01', '2026-09'), '10 nam truot 2016-10..2026-09': ('2016-10', '2026-09'),
        'nam tron 2014-2025': ('2014-01', '2025-12'), 'r4: 2013-01..2026-09': ('2013-01', '2026-09'), 'day-day 2016-2023': ('2016-01', '2023-12')}
print(f"\n1) MID RSS3 thuc USD2025/kg, cua so 2014-01..2026-09 (n={len(w)}): P25 {MID['P25']:.3f} | TB {MID['TB']:.3f} | P75 {MID['P75']:.3f}"
      f" | dx TB-P25 {MID['TB']-MID['P25']:.3f} P75-TB {MID['P75']-MID['TB']:.3f}")
print(f"   Q3/26 danh nghia {ns['rssq3']:.3f}; phan vi trong chuoi thuc cua so: {sum(v <= ns['rssq3'] for v in w)/len(w):.0%}; cao hon TB {ns['rssq3']/MID['TB']-1:+.1%}")
wsens = {}
for k, (a, b) in WINS.items():
    mm = st.mean(win(a, b)); wsens[k] = dict(mid=mm, v=base(mm)); print(f"   do nhay cua so [{k}]: mid {mm:.3f} -> tam {base(mm):,.0f}")
out.update(mids=MID, window_sens=wsens, rssq3=ns['rssq3'])

# ---------- 2. Tam + dien giai ----------
C = base(MID['TB']); CL = liqread(MID['TB']); F = forced(MID['TB'])
print(f"\n2) TAM base (mid {MID['TB']:.3f}, L27, r13,5%): {C:,.0f} d/cp (XDCB gia von {CIPPS:,.0f})")
print(f"   DIEN GIAI KHAC 'C-thanh ly' (thanh ly 2029-36 la quyet dinh tai san hien huu, khong trong lai, + XDCB): {CL:,.0f} ({CL-C:+,.0f}) — KHONG vao base")
print(f"   KICH BAN tai canh bi buoc (T1 cu + XDCB): {F:,.0f} ({F-C:+,.0f})")
CEN['r'] = R_ANCHOR
print(f"   cau noi r4->r5: mid 2,341->{MID['TB']:.3f}: {C-16950:+,.0f}")
print(f"   mot truc L (tam): " + " | ".join(f"L{L} {base(MID['TB'], L):,.0f}" for L in (22, 24, 27, 32)))

# ---------- 3. Luoi 27 o ----------
WM = {'P25': .25, 'TB': .5, 'P75': .25}; WL = {22: .25, 27: .5, 32: .25}; WR = {0.115: .25, 0.135: .5, 0.155: .25}
def grid(fn):
    cs = []
    for (mk, wm), (L, wl), (r, wr) in itertools.product(WM.items(), WL.items(), WR.items()):
        cs.append(dict(mid=mk, L=L, r=r, w=wm*wl*wr, v=fn(MID[mk], L, r)))
    return cs
def wq(cs, q):
    acc = 0
    for c in sorted(cs, key=lambda c: c['v']):
        acc += c['w']
        if acc >= q - 1e-12: return c['v']
def scale(cs): return {f'P{int(q*100)}': wq(cs, q) for q in (.10, .25, .50, .75, .90)}
G = grid(base); GF = grid(forced); GL = grid(liqread)
SCALE, SF, SL = scale(G), scale(GF), scale(GL)
mean = lambda cs: sum(c['v']*c['w'] for c in cs)
for nm, s, cs in (('BASE', SCALE, G), ('tai canh bi buoc', SF, GF), ('C-thanh ly (dien giai khac)', SL, GL)):
    print(f"\n3) THANG {nm}: " + " / ".join(f"{k} {v:,.0f}" for k, v in s.items()) + f" | TB co trong so {mean(cs):,.0f} | min {min(c['v'] for c in cs):,.0f} max {max(c['v'] for c in cs):,.0f}")
print("   mot truc quanh tam [mid]: " + " | ".join(f"{k} {base(MID[k]):,.0f}" for k in WM) + "  [r]: " + " | ".join(f"{r:.1%} {base(MID['TB'], 27, r):,.0f}" for r in WR))
with builtins.open(os.path.join(HERE, 'grid_r5.csv'), 'w', newline='') as f:
    wr_ = csv.DictWriter(f, fieldnames=['mid', 'L', 'r', 'w', 'v', 'v_forced', 'v_liqread']); wr_.writeheader()
    for a, b, c in zip(G, GF, GL): wr_.writerow({**a, 'v': round(a['v']), 'v_forced': round(b['v']), 'v_liqread': round(c['v'])})

# ---------- 4. Ky vong (p nhan dinh) ----------
P_FORCED = 0.20
EXP = {p: (1-p)*mean(G) + p*mean(GF) for p in (0.0, 0.1, 0.2, 0.3)}
print("\n4) KY VONG = (1-p) x TB luoi base + p x TB luoi bi buoc (p = NHAN DINH, khong co co so dinh luong): "
      + " | ".join(f"p{int(p*100)}% {v:,.0f}" for p, v in EXP.items()))
CEN['r'] = R_ANCHOR
_V, _w = build3(2029, 27, R_on=False, new_on=False)
tr = ns['fv4']('TROUGH', MID['TB'], CEN, V=_V, farea=True, addD=D_V, wood=ns['wood3'](_w)) + CIPPS
print(f"   stress RSS3 2027=2028=1,60 roi ve mid: {tr:,.0f}")

# ---------- 5. Lai huy dong ----------
sens = {}
for beta in (1.0, 0.5):
    sens[beta] = {bp: base(MID['TB'], 27, r_of(DEP_ANCHOR + bp/1e4, beta)) for bp in (-100, -50, 0, 50, 100)}
    print(f"5) beta {beta}: " + " | ".join(f"{bp:+d}bp {v:,.0f} ({v/C-1:+.1%})" for bp, v in sens[beta].items()))
out.update(center=C, center_liqread=CL, forced=F, scale=SCALE, scale_forced=SF, scale_liqread=SL, mean_base=mean(G), mean_forced=mean(GF),
           expected={str(p): v for p, v in EXP.items()}, p_forced=P_FORCED, trough_stress=tr, L_axis={L: base(MID['TB'], L) for L in (22, 24, 27, 32)},
           dep_sens={str(b): {str(k): v for k, v in r.items()} for b, r in sens.items()}, cip_bn=CIP, r_anchor=R_ANCHOR, dep_anchor=DEP_ANCHOR)
json.dump(out, builtins.open(os.path.join(HERE, 'dri_model_r5_out.json'), 'w'), indent=1, default=float)
print("\nOUT -> dri_model_r5_out.json, grid_r5.csv")
