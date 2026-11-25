"""VLB recheck đợt 3 (25/11/2026, job Taylor_20261125_032448): CONTROL + E15 + E17 trên mô hình rev4 KHÔNG SỬA.
Chạy: python3 -I calc_adj_vlb.py  (thuần python, tất định). MÙ GIÁ (giá chỉ qua px_vlb.csv cho CK thanh khoản của rev4).
Số đầu vào E17 (bậc A, đọc ảnh trang BCTC):
  LCTT KT25 [src/BCTC_KiemToan_2025.pdf tr.14 PDF]: khấu hao 2025 10,615596665 / 2024 17,090897830; tiền chi TSCĐ 2025 12,038804540 / 2024 3,623146679;
     tăng giảm chi phí trả trước 2025 −70,923060623 / 2024 +15,597944722.
  LCTT 9T/26 [src/BCTC_Q3_2026.pdf tr.6 PDF]: khấu hao 7,997178643; tiền chi TSCĐ 1,129718370; tăng giảm chi phí chờ phân bổ +2,889216194.
  KQKD Q3/26 [src/BCTC_Q3_2026.pdf tr.5 PDF]: LN thuần HĐKD quý 143,763841308, DTTC quý 17,813844274; 9T 355,953341814 / 25,191570102.
  Q3 BS phải trả người lao động 54,215 (= thành phần wc_liab của rev4 [Q3 p2-3]).
"""
import hashlib, importlib.util, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.normpath(os.path.join(HERE, '../../../dd_VLB_20261122/model'))
P = os.path.join(MD, 'dcf_vlb_r4.py')
assert hashlib.md5(open(P, 'rb').read()).hexdigest() == '05cc094364d09b4c90b3ffbf7ecac207', 'model md5 lệch'
PRE = os.path.normpath(os.path.join(HERE, '../../../dd_adjcenter_20261124'))
for f, m in (('PREREG_adj.md', 'ef5157cb3f762d58623ed550ebc214c7'), ('PREREG_adj_v2.md', '835dfc1e07f9c67ac7f6c3028b529d13')):
    assert hashlib.md5(open(os.path.join(PRE, f), 'rb').read()).hexdigest() == m, f
spec = importlib.util.spec_from_file_location('m4', P); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)

d5 = M.d_liq(5); DIV = M.DIV_2026_INTERIM
post = lambda v: v * (1 - d5) - DIV   # sau CK 5 tỷ, ex-div = cơ sở sổ
base_pre = M.center(); BASE = post(base_pre)
print(f"CONTROL tâm trước CK {base_pre:,.0f} | sổ (sau CK, ex-div) {BASE:,.0f} (rev4: 49.123 / 45.161); d5={d5:.4%}")
e15 = post(M.center(r=0.123)); print(f"E15 Tâm @ Ke 12,3%: {e15:,.0f} ({e15/BASE-1:+.2%})")
for dr in (-0.01, -0.005, 0.005, 0.01):
    v = post(M.center(r=M.R + dr)); print(f"  r {dr*1e4:+.0f}bp: {v:,.0f} ({v/BASE-1:+.2%})")

# ---------- hạng mục: mỗi hàm trả dict scenario->(path override / extra) ----------
G = M.G
def path_mid(mid_level, start=M.CORE_TTM):
    mid = lambda t: mid_level * (1 + G) ** (t + 0.75)
    prem = start - mid(1)
    return lambda t: mid(t) + prem * max(0.0, 1 - (t - 1) / 2)

def flow_pv(F, r, L):   # dòng tiền hằng năm F (tỷ) theo tỷ trọng mỏ còn hoạt động
    return sum(F * M.share_active(t, L) / (1 + r) ** t for t in range(1, 46))

WC_NLD = 54.215
def run(mid_level=None, xau_flat=None, start=None, nld_now=False, wc_shrink=0.0, F=0.0):
    tot = 0.0
    for k, s in M.SCEN.items():
        pth = None
        if k == 'co_so' and (mid_level is not None or start is not None):
            pth = path_mid(mid_level if mid_level is not None else M.CORE_FY25, start if start is not None else M.CORE_TTM)
        if k == 'xau' and xau_flat is not None:
            pth = (lambda c: (lambda t: c))(xau_flat)
        x = M.value(s, path=pth); v = x['op'] + x['off'] + x['dep'] + x['nc']
        L = x['L']
        if nld_now or wc_shrink:
            old = M.wc_pv(M.R, L)
            settle = M.WC_SETTLE - (WC_NLD if nld_now else 0.0)
            new_close = settle * (1 - wc_shrink)
            pv_close = sum(new_close * m['share'] / (1 + M.R) ** L[kk] for kk, m in M.MINES.items())
            pv_early = settle * wc_shrink / (1 + M.R) ** 2.5
            v = v + old - pv_close - pv_early - (WC_NLD if nld_now else 0.0)
        if F:
            v += flow_pv(F, M.R, L)
        tot += s['w'] * v / M.SH * 1000
    return post(tot)

assert abs(run() - BASE) < 0.5
# I3: chênh dòng tiền vs LNST = khấu hao − tiền chi TSCĐ + tăng giảm chi phí trả trước (đền bù đất qua CFO)
g24 = 17.090897830 - 3.623146679 + 15.597944722
g25 = 10.615596665 - 12.038804540 - 70.923060623
g26 = 7.997178643 - 1.129718370 + 2.889216194
F_pt = (g24 + g25 + g26) / 2.75; F_lo = (g25 + g26) / 1.75; F_hi = g26 / 0.75
q3core = (143.763841308 - 17.813844274) * 4 * 0.8
t9core = (355.953341814 - 25.191570102) / 0.75 * 0.8
print(f"I3 gap 2024 {g24:.2f} 2025 {g25:.2f} 9T26 {g26:.2f} => F diem {F_pt:.2f} [{F_lo:.2f}; {F_hi:.2f}] ty/nam")
print(f"I4 Q3/26 core x4 = {q3core:.1f}; 9T26 core nam hoa = {t9core:.1f}; TTM rev4 = {M.CORE_TTM:.1f}")
MIDAVG = (M.CORE_FY24 + M.CORE_FY25) / 2
items = {
  'I1_mid_cycle': dict(pt=dict(mid_level=MIDAVG, xau_flat=M.CORE_FY24), lo=dict(mid_level=M.CORE_FY24, xau_flat=M.CORE_FY24), hi=dict(mid_level=MIDAVG)),
  'I2_wc_nld':    dict(pt=dict(nld_now=True), lo=dict(nld_now=True, wc_shrink=0.26), hi=dict(nld_now=True)),
  'I3_cash_gap':  dict(pt=dict(F=F_pt), lo=dict(F=F_lo), hi=dict(F=F_hi)),
  'I4_year1_q3':  dict(pt=dict(start=q3core), lo=dict(start=t9core), hi=dict(start=q3core)),
}
P_ = {'I1_mid_cycle': (0.35, 0.15, 0.55), 'I2_wc_nld': (0.5, 0.25, 0.75), 'I3_cash_gap': (0.35, 0.15, 0.55), 'I4_year1_q3': (0.35, 0.15, 0.55)}
out = {}; S = 0.0; Slo = 0.0; Shi = 0.0
for k, d in items.items():
    m = {z: run(**d[z]) / BASE - 1 for z in ('pt', 'lo', 'hi')}
    p, pl, ph = P_[k]
    cands = [pp * mm for pp in (pl, ph) for mm in (m['lo'], m['hi'], m['pt'])]
    S += p * m['pt']; Slo += min(cands); Shi += max(cands)
    out[k] = dict(m_pt=round(m['pt'] * 100, 3), m_lo=round(m['lo'] * 100, 3), m_hi=round(m['hi'] * 100, 3), p=p, p_low=pl, p_high=ph, contrib=round(p * m['pt'] * 100, 3))
    print(f"{k}: m {m['pt']:+.2%} [{m['lo']:+.2%}; {m['hi']:+.2%}] p {p} -> {p*m['pt']:+.2%}")
adj = BASE * (1 + S)
print(f"SUM linear {S:+.3%} -> adj {adj:,.0f}; range {BASE*(1+Slo):,.0f} – {BASE*(1+Shi):,.0f}")
# tổ hợp (kiểm tra cộng tuyến tính; bắt buộc nếu |Σ|>5%): áp tất cả ở m điểm với trọng p qua nội suy tham số
combo = run(mid_level=M.CORE_FY25 + 0.35 * (MIDAVG - M.CORE_FY25), xau_flat=250 + 0.35 * (M.CORE_FY24 - 250),
            start=M.CORE_TTM + 0.35 * (q3core - M.CORE_TTM), nld_now=False, F=0.35 * F_pt) - 0.5 * WC_NLD / M.SH * 1000 * (1 - d5)
print(f"TO HOP (tham so noi suy theo p; I2 tru 0,5 x NLD ngay, xap xi): {combo:,.0f} ({combo/BASE-1:+.3%})")
json.dump(dict(base=round(BASE), e15=round(e15), items=out, sum_linear_pct=round(S * 100, 3), adj=round(adj), lo=round(BASE * (1 + Slo)), hi=round(BASE * (1 + Shi)),
               combo=round(combo), F=[F_pt, F_lo, F_hi], q3core=q3core, t9core=t9core), open(os.path.join(HERE, 'calc_adj_out.json'), 'w'), ensure_ascii=False, indent=1)
