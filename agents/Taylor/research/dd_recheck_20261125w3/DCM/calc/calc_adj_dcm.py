"""DCM recheck đợt 3 (25/11/2026, job Taylor_20261125_032448): CONTROL + E15 + E17 trên model_r9 KHÔNG SỬA (monkeypatch trong bộ nhớ).
Chạy: cd agents/Taylor/research/dd_DCM_20261104 && /home/trido/thanhdt/wc_venv/bin/python -I ../dd_recheck_20261125w3/DCM/calc/calc_adj_dcm.py
MÙ GIÁ: dùng d_liq đã khoá trong compare_px_r9_out.json (0,585%), không đọc giá.
Số đầu vào E17 (bậc A, TM25 BCTC HN KT 2025 png_r7/kt25_p37.png — trích trong REPORT_rev9 §1a T1): sử dụng quỹ KH&CN 2024 39,50 / 2025 75,82,
chuyển TSCĐ 11,80 / 13,51, trích 44,78 / 187,99; 9T/26 sử dụng ≈47,5 (REPORT_rev9 §9) trên trích 249,63.
"""
import sys, os, json, hashlib
sys.path.insert(0, 'calc'); sys.path.insert(0, '../dd_redo_20261105/_shared')
for f, h in (('calc/model_r9.py', '615c950a29e376f3e615fcfd07bafeb9'), ('assumptions_r9.json', 'a12917ea454b449b000bf660af2f929c'),
             ('../dd_adjcenter_20261124/PREREG_adj.md', 'ef5157cb3f762d58623ed550ebc214c7'), ('../dd_adjcenter_20261124/PREREG_adj_v2.md', '835dfc1e07f9c67ac7f6c3028b529d13')):
    assert hashlib.md5(open(f, 'rb').read()).hexdigest() == h, f
import numpy as np, model as m, model_r6 as r6, model_r7 as r7, model_r9 as r9
D = json.load(open('calc/compare_px_r9_out.json'))['d_liq_used']
def C():
    v, w = r9.grid9(); return float(np.average(v * (1 - D), weights=w))
BASE = C(); print(f"CONTROL tâm sau CK {BASE:,.1f} (rev9 27.393)"); assert round(BASE) == 27393
RS0 = list(r6.RS)
def with_rs(shift, fn):
    r6.RS = [x + shift for x in RS0]
    try: return fn()
    finally: r6.RS = list(RS0)
e15 = with_rs(0.123 - 0.135, C); print(f"E15 trục r dịch về tâm 12,3% (±100bp giữ): {e15:,.0f} ({e15/BASE-1:+.2%})")
r6.RS = [0.123]; e15pt = C(); r6.RS = list(RS0); print(f"   r cố định 12,3% (bỏ trục): {e15pt:,.0f} ({e15pt/BASE-1:+.2%})")
r6.RS = [0.135]; b135 = C(); r6.RS = list(RS0); print(f"   r cố định 13,5% (bỏ trục, đối chiếu): {b135:,.0f}")
for dd in (-1, -.5, .5, 1):
    x = with_rs(dd / 100, C); print(f"   lãi huy động {dd*100:+.0f}bp (β1, dịch trục): {x:,.0f} ({x/BASE-1:+.2%})")

# ---- D1: phần trích quỹ KH&CN bị chi BẮT BUỘC cho KH&CN không thành TSCĐ (chi phí, không tạo doanh thu đo được) ⇒ giá trị 0 (D3), phần còn lại giữ v
f24 = (39.50 - 11.80) / 44.78; f25 = (75.82 - 13.51) / 187.99; f_pool = ((39.50 - 11.80) + (75.82 - 13.51)) / (44.78 + 187.99); f26 = 47.5 / 249.63
_v0 = r9.v_khcn
def with_f(f, fn):
    r9.v_khcn = lambda t, L, r: (1 - f) * _v0(t, L, r)
    try: return fn()
    finally: r9.v_khcn = _v0
# ---- D2: hồi quy (trước khấu hao, trước trích) đoán cao 2024–25 ⇒ dịch tung độ gốc mỗi cửa sổ bằng phần dư TB
def resid(k):
    a, b = r7.FITS_BD[k]; da = r9.da9()
    return {y: m.np_[y] + da[y] * (1 - r9.TH) + r9.a_hist(y) * (1 - r9.TH) - (a + b * m.proxy[y]) for y in (2024, 2025)}
RES = {k: resid(k) for k in r7.HEAD_REGS}; print('phần dư 2024/2025:', {k: {y: round(v, 1) for y, v in d.items()} for k, d in RES.items()})
_rf = r9.refit
def with_shift(mode, fn):
    def rf():
        _rf()
        for k in list(r7.FITS_BD):
            if k in RES:
                rr = RES[k]; dlt = {'mean': (rr[2024] + rr[2025]) / 2, '2025': rr[2025], '2024': rr[2024]}[mode]
                a, b = r7.FITS_BD[k]; r7.FITS_BD[k] = (a + dlt, b)
    r9.refit = rf; rf()
    try: return fn()
    finally: r9.refit = _rf; _rf()
items = {
 'D1_khcn_forced_spend': (0.5, 0.25, 0.75, {z: with_f(f, C) for z, f in (('pt', f_pool), ('lo', f24), ('hi', f26))}),
 'D2_regression_overpredict': (0.35, 0.15, 0.55, {z: with_shift(md, C) for z, md in (('pt', 'mean'), ('lo', '2025'), ('hi', '2024'))}),
}
print(f"f: 2024 {f24:.3f} 2025 {f25:.3f} pool {f_pool:.3f} 9T26 {f26:.3f}")
S = Slo = Shi = 0.0; out = {}
for k, (p, pl, ph, v) in items.items():
    mm = {z: v[z] / BASE - 1 for z in v}
    c = [pp * x for pp in (pl, ph) for x in mm.values()]
    S += p * mm['pt']; Slo += min(c); Shi += max(c)
    out[k] = dict(m_pt=round(mm['pt'] * 100, 3), m_lo=round(min(mm['lo'], mm['hi']) * 100, 3), m_hi=round(max(mm['lo'], mm['hi']) * 100, 3), p=p, p_low=pl, p_high=ph, contrib=round(p * mm['pt'] * 100, 3))
    print(f"{k}: m {mm['pt']:+.2%} [lo {mm['lo']:+.2%}; hi {mm['hi']:+.2%}] p {p} -> {p*mm['pt']:+.2%}")
adj = BASE * (1 + S)
combo = with_shift('mean', lambda: None)  # placeholder to keep order deterministic
# tổ hợp: D1 ở f_pool×p (kỳ vọng tuyến tính trong f) + D2 tung độ gốc × p
def combo_fn():
    return with_f(0.5 * f_pool, lambda: C())
def with_shift_scaled(scale, fn):
    def rf():
        _rf()
        for k in list(r7.FITS_BD):
            if k in RES:
                rr = RES[k]; a, b = r7.FITS_BD[k]; r7.FITS_BD[k] = (a + scale * (rr[2024] + rr[2025]) / 2, b)
    r9.refit = rf; rf()
    try: return fn()
    finally: r9.refit = _rf; _rf()
combo = with_shift_scaled(0.35, combo_fn)
print(f"SUM linear {S:+.3%} -> adj {adj:,.0f}; range {BASE*(1+Slo):,.0f} – {BASE*(1+Shi):,.0f}; TO HOP {combo:,.0f} ({combo/BASE-1:+.3%})")
# độ nhạy C (đối chiếu): khí 2035+ trục, rev7 reading, đất, phong toả, 4 cửa sổ, thuế XK — sau CK
def G(**kw):
    v, w = r9.grid9(**kw); return float(np.average(v * (1 - D), weights=w))
sens = dict(late_axis=G(late_axis=True), w4=G(regs=tuple(r6.CODE_REG)), policy055=G(p_policy=0.55),
            rev7_100pct=r9.with_p(lambda: float(np.average(r9.r8.grid8(khcn=1.0)[0] * (1 - D), weights=r9.r8.grid8(khcn=1.0)[1])), on=False))
for k, v in sens.items(): print(f"  sens {k}: {v:,.0f} ({v/BASE-1:+.2%})")
json.dump(dict(base=round(BASE), e15=round(e15), e15_fixed=round(e15pt), items=out, sum_linear_pct=round(S * 100, 3), adj=round(adj), lo=round(BASE * (1 + Slo)),
               hi=round(BASE * (1 + Shi)), combo=round(combo), f=dict(f24=f24, f25=f25, pool=f_pool, f26=f26),
               resid={k: {str(y): v for y, v in d.items()} for k, d in RES.items()}, sens={k: round(v) for k, v in sens.items()}),
          open('../dd_recheck_20261125w3/DCM/calc/calc_adj_out.json', 'w'), ensure_ascii=False, indent=1)
