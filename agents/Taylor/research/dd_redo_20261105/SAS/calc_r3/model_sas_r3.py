"""SAS — DD redo VONG 3 (08/11/2026, job Taylor_20261108_153740). Ap TOP5B_CORRECTIONS_20261108.md §SAS (sau khi KIEM tung diem).
Gia dinh khoa: assumptions_r3.json (md5 trong LOCK_r3_md5.txt, chot TRUOC khi chay; script assert md5 khop truoc khi tinh).
Chay: /home/trido/thanhdt/wc_venv/bin/python -I -B model_sas_r3.py > model_sas_r3_out.txt  (ghi model_sas_r3_out.json)

Bridge r2 -> r3 (moi buoc doi MOT thu, tam sau CK 5 ty):
  S0 r2 tai lap (gia 04/11)                           — doi chung, phai = 31.066
  S1 gia + ADV toi 06/11 (BQ)                          — r giu 13,5% (lai huy dong hieu dung 06/11 = 7,40%)
  S2 N0: co tuc mien thue (dinh chinh 1)               — N0 = (LNTT - TC rong) x 0,8 x 4/3
  S3 VLD nhat quan (dinh chinh 2)                      — chi tru quy KTPL + co tuc phai tra; phai tra NLD/thue = VLD van hanh
  S4 XDCB 118,0 + BDS dau tu 32,2 theo so (dinh chinh 3, luat 20)
  S5 trich KTPL tren LN 9T chua trich (dinh chinh 6 — WARNING cua skeptic; dua vao base vi cung co so eps_ratio)
  S6 khop ngay dinh gia 06/11: + LN van hanh Q4/26, chiet khau 55 ngay  (MOI, phat hien khi kiem — r2 bo trong Q4/26)
"""
import hashlib, itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '_common_020021'))
import r2lib as R2  # noqa: E402
L = R2.L

# ---- 0. LOCK: md5 moi file upstream phai khop LOCK_r3_md5.txt (chot truoc khi so gia)
LOCK = os.path.join(HERE, 'LOCK_r3_md5.txt')
for ln in open(LOCK):
    h, p = ln.split(None, 1); p = p.strip()
    fp = p if p.startswith('/') else os.path.join(ROOT, p)
    assert hashlib.md5(open(fp, 'rb').read()).hexdigest() == h, f"LOCK lech: {p}"
A = json.load(open(os.path.join(HERE, 'assumptions_r3.json')))
v = lambda k: A[k]['v']
SH = v('shares_mn'); EPSR = v('eps_ratio'); T = v('cit_rate')
G = A['grid']
DS, WD = tuple(G['delta']), tuple(G['w_delta'])
GS, WG = tuple(G['g']), tuple(G['w_g'])

# ---- 1. thanh khoan: S0 = csv cu (04/11), tu S1 = csv moi 06/11
ASOF_NEW = '2026-11-06'
Q_old = R2.liq2('SAS')
import csv  # noqa: E402
_rows = [r for r in csv.DictReader(open(os.path.join(HERE, 'px_sas_r3_20261106.csv')))]
L.px_series = lambda tk, asof=ASOF_NEW: [r for r in _rows if r['ticker'] == tk and r['time'] <= asof]
_liq0 = L.liq
L.liq = lambda tk, Q_bn=(1, 5, 10), asof=ASOF_NEW, n=250, free_float_shares=None: _liq0(tk, Q_bn, ASOF_NEW, n, free_float_shares)
Q = R2.liq2('SAS'); PX = Q['price']; LD = Q['disc_ref']
assert Q['price_date'] == ASOF_NEW, Q['price_date']
dep, dep_src = L.current_dep(ASOF_NEW); R = L.r_of(dep)
assert abs(R - v('r')) < 1e-12, R

# ---- 2. cac khoi so (ty VND)
FIN_NET = v('fin_rev_9m') - v('fin_exp_9m')
N0_r2 = (v('np_9m') - FIN_NET * 0.80) * 4 / 3
N0_r3 = (v('pbt_9m') - FIN_NET) * (1 - T) * 4 / 3
fin_at_press = v('div_income_9m_press') + (FIN_NET - v('div_income_9m_press')) * (1 - T)
N0_press = (v('np_9m') - fin_at_press) * 4 / 3
exempt_implied = v('pbt_9m') - v('cur_tax_9m') / T
CASHHTM = v('cash') + v('htm_st')
X_r2 = CASHHTM - v('emp_payable') - v('ktpl_fund') - v('tax_payable')
X_r3 = CASHHTM - v('ktpl_fund') - v('div_payable')
X_fullnwc = CASHHTM + v('nwc_noncash')
CIPBDS = v('cip') + v('inv_property')
KTPL9 = (1 - EPSR) * v('np_9m')
DT = 55 / 365


def val(delta, n0, r, g, x, recv=True, cip=0.0, ktpl9=0.0, timing=False, ltinv=None):
    e27 = n0 * (1 + delta / 2); e28 = n0 * (1 + delta)
    pv = (e27 / (1 + r) + e28 / (r - g) / (1 + r)) * EPSR
    if timing:
        pv = (pv + n0 / 4 * EPSR) / (1 + r) ** DT
    li = v('lt_inv') if ltinv is None else ltinv(r)
    return (x + li + (v('lt_recv') if recv else 0.0) + cip - ktpl9 + pv) / SH * 1000


def grid(n0, gs=(GS, WG), dshift=0.0, rshift=0.0, **kw):
    vals, ws = [], []
    for (d, wd), (m, wn), (rs, wr), (g, wg) in itertools.product(zip(DS, WD), zip(G['n0_mult'], G['w_n0']), zip(G['r_shift'], G['w_r']), zip(*gs)):
        vals.append(val(d + dshift, n0 * m, R + rs + rshift, g, **kw)); ws.append(wd * wn * wr * wg)
    return vals, ws


def run(name, n0, ld, px, **kw):
    vals, ws = grid(n0, **kw); s = R2.stats(vals, ws, px, ld); s['label'] = R2.label(px, s); s['name'] = name
    return s, vals, ws


BASE = dict(x=X_r3, cip=CIPBDS, ktpl9=KTPL9, timing=True)
steps = [("S0_r2_tai_lap_gia_0411", N0_r2, Q_old['disc_ref'], Q_old['price'], dict(x=X_r2)),
         ("S1_gia_ADV_0611", N0_r2, LD, PX, dict(x=X_r2)),
         ("S2_N0_co_tuc_mien_thue", N0_r3, LD, PX, dict(x=X_r2)),
         ("S3_VLD_nhat_quan", N0_r3, LD, PX, dict(x=X_r3)),
         ("S4_XDCB_BDSDT_theo_so", N0_r3, LD, PX, dict(x=X_r3, cip=CIPBDS)),
         ("S5_trich_KTPL_LN_9T", N0_r3, LD, PX, dict(x=X_r3, cip=CIPBDS, ktpl9=KTPL9)),
         ("S6_khop_ngay_dinh_gia", N0_r3, LD, PX, BASE)]
bridge = {}
for nm, n0, ld, px, kw in steps:
    s, _, _ = run(nm, n0, ld, px, **kw); bridge[nm] = s
assert round(bridge['S0_r2_tai_lap_gia_0411']['center_post']) == 31066, bridge['S0_r2_tai_lap_gia_0411']['center_post']
H, hv, hw = run('HEADLINE', N0_r3, LD, PX, **BASE)
cp = val(-0.25, N0_r3, R, 0.03, **BASE)

print(f"SAS r3 | gia {PX:,.0f} ({Q['price_date']}) | r {R:.2%} (dep {dep:.2%} {dep_src}) | CK 5 ty {LD:.2%}")
print(f"N0: r2 {N0_r2:.1f} -> r3 {N0_r3:.1f} (LNTT {v('pbt_9m'):.2f} - TC rong {FIN_NET:.2f}) x 0,8 x 4/3; bien the co tuc bao chi 135,8: {N0_press:.1f}; "
      f"kiem: mien thue suy tu thue hien hanh = {exempt_implied:.1f} (vs co tuc 135,8)")
print(f"Tien rong: r2 {X_r2:.1f} -> r3 {X_r3:.1f} (chi tru KTPL {v('ktpl_fund'):.1f} + co tuc phai tra {v('div_payable'):.2f}); gop du VLD rong {X_fullnwc:.1f}")
print(f"XDCB+BDSDT {CIPBDS:.1f} ({CIPBDS/SH*1000:,.0f} d/cp); trich KTPL LN 9T {KTPL9:.1f} ({-KTPL9/SH*1000:,.0f} d/cp); khop ngay: +Q4/26 {N0_r3/4*EPSR:.1f} ty, chiet khau {DT*365:.0f} ngay")
print("BRIDGE (tam sau CK 5 ty):")
prev = None
for k, s in bridge.items():
    print(f"  {k:<28} tam {s['center_post']:>7,.0f}" + ("" if prev is None else f" ({s['center_post']-prev:+,.0f})") + f" | P10/P50/P90 {s['p10_post']:,.0f}/{s['p50_post']:,.0f}/{s['p90_post']:,.0f} | duoi gia {s['pct_w_below_px']:.1%} | {s['label']}")
    prev = s['center_post']
print("HEADLINE (CK 5 ty): " + R2.fmt(H, PX))
print(f"Gia tri tai tham so trung tam (Delta -25%, N0 {N0_r3:.1f}, r {R:.1%}, g 3%): {cp:,.0f} truoc / {cp*(1-LD):,.0f} sau CK")

# ---- 3. bien the song song (CK 5 ty)
alts = {}
def alt(nm, n0=N0_r3, **kw):
    k2 = dict(BASE); k2.update(kw); s, _, _ = run(nm, n0, LD, PX, **k2); alts[nm] = s
alt("A1_skeptic_diem_S2_S4_khong_S5_S6", x=X_r3, cip=CIPBDS, ktpl9=0.0, timing=False)
alt("A2_gop_du_VLD_rong", x=X_fullnwc)
alt("A3_khong_trich_KTPL_9T", ktpl9=0.0)
alt("A4_khong_khop_ngay", timing=False)
alt("A5_N0_co_tuc_bao_chi_135_8", n0=N0_press)
alt("A6_bo_phai_thu_DH", recv=False)
alt("A7_bo_truc_g", gs=((0.03,), (1.0,)))
for D in (71.0, 100.0, 140.0):
    alt(f"A8_von_hoa_co_tuc_dau_tu_{D:.0f}ty_nam", ltinv=lambda r, D=D: D * EPSR / r)
for k, s in alts.items():
    print(f"SONG SONG {k}: " + R2.fmt(s, PX))

# ---- 4. gia ngu y (tam sau CK 5 ty = gia)
def solve(f, lo, hi):
    flo = f(lo)
    for _ in range(80):
        mid = (lo + hi) / 2; fm = f(mid)
        if (fm > 0) == (flo > 0): lo, flo = mid, fm
        else: hi = mid
    return (lo + hi) / 2
c_of = lambda **kw: run('x', N0_r3, LD, PX, **{**BASE, **kw})[0]['center_post'] - PX
imp = dict(delta_center=-0.25 + solve(lambda s: c_of(dshift=s), -0.3, 0.3),
           r=R + solve(lambda s: c_of(rshift=s), -0.04, 0.03),
           div_capitalized_bn_per_year=solve(lambda D: c_of(ltinv=lambda r: D * EPSR / r), 0.0, 400.0),
           n0_bn=N0_r3 * (1 + solve(lambda m: run('x', N0_r3 * (1 + m), LD, PX, **BASE)[0]['center_post'] - PX, -0.3, 0.5)))
print(f"GIA NGU Y (tam sau CK 5 ty = {PX:,.0f}): tam Delta Long Thanh {imp['delta_center']:+.1%} (base -25%); hoac r {imp['r']:.2%}; "
      f"hoac co tuc dau tu von hoa {imp['div_capitalized_bn_per_year']:.0f} ty/nam (thay so sach 253,8); hoac N0 {imp['n0_bn']:.0f} ty")

# ---- 5. do nhay lai huy dong + thanh khoan theo co
sens = {}
for b in (0.5, 1.0):
    for d in (-0.01, -0.005, 0.005, 0.01):
        s = run('x', N0_r3, LD, PX, rshift=L.r_of(dep + d, b) - R, **BASE)[0]
        sens[f"b{b}_d{int(d*1e4)}bp"] = dict(center_post=s['center_post'], d_pct=s['center_post'] / H['center_post'] - 1)
print("Do nhay lai huy dong (tam sau CK 5 ty): " + "; ".join(f"{k} {x['center_post']:,.0f} ({x['d_pct']:+.1%})" for k, x in sens.items()))
for ln in R2.liq_lines(Q):
    print(ln)
by_size = {}
for k, z in Q['adv250']['sizes'].items():
    s = R2.stats(hv, hw, PX, z['disc']); s['label'] = R2.label(PX, s); by_size[k] = s
    print(f"Co {float(k)*1000:>7,.0f} tr (CK {z['disc']:.2%}, Q/ADV250 {z['q_over_adv']:.1%}): tam {s['center_post']:,.0f} | P10/P90 {s['p10_post']:,.0f}/{s['p90_post']:,.0f} | gia/tam {PX/s['center_post']-1:+.1%} | duoi gia {s['pct_w_below_px']:.1%} | {s['label']}")

OUT = dict(ticker='SAS', round=3, price=PX, price_date=Q['price_date'], r=R, dep=dep, dep_src=dep_src, liq=Q, liq_old=Q_old,
           headline=H, center_param_pre=cp, center_param_post=cp * (1 - LD), bridge=bridge, alternatives=alts, implied=imp, sens_dep=sens, by_size=by_size,
           blocks=dict(N0_r2=N0_r2, N0_r3=N0_r3, N0_press=N0_press, exempt_implied=exempt_implied, fin_net_9m=FIN_NET, X_r2=X_r2, X_r3=X_r3,
                       X_fullnwc=X_fullnwc, cip_bds=CIPBDS, ktpl9=KTPL9, q4_ops=N0_r3 / 4 * EPSR, dt_days=DT * 365))
json.dump(OUT, open(os.path.join(HERE, 'model_sas_r3_out.json'), 'w'), indent=1, default=float, ensure_ascii=False, sort_keys=True)
