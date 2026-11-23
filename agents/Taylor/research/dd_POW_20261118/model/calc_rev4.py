"""POW DD rev4 (23/11/2026) = rev3 + hồi tố sau thuế tách khỏi khối ROE/r, ghi ~1,0x (skeptic r2).
rev3 docstring: POW DD rev3 (23/11/2026) — nền rev2 + capex tuân thủ QCVN 19:2024 VA1 (D3: dòng tiền ra trong base)
+ độ nhạy các hạng mục skeptic DD_GENERAL r1. Mù giá: không đọc giá thị trường."""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(H, 'assumptions_POW_20261118_rev2.json')))
B = json.load(open(os.path.join(H, 'model_rev3_inputs.json')))
B.update(json.load(open(os.path.join(H, 'model_rev4_inputs.json'))))
S = A['shares_m']; E = A['equity_parent_q3']; EN = A['e_nt34_book_estimate']; NEW = A['e_new_projects_book']
r0 = A['r_ke']; w = A['weights']; L = A['liquidity_discount']; sc = A['scenario_roe_legacy']
RETRO = B['retro_equity']['pbt_bn'] * (1 - B['retro_equity']['tax'])
EL = E - EN - NEW - RETRO
Q = B['qcvn19_va1']; X = B['sensitivity_inputs']
dps = lambda bn: bn / S * 1000  # tỷ -> đ/cp


def legacy(roe, r=r0, el=EL):
    return el * roe / r


def qcvn_p0(r=r0, capex=Q['capex_bn'], opex=Q['opex_bn_per_year'], t=Q['tax_rate'], opex_end=None):
    """PV (tỷ, tại 30/09/2026) gánh nặng sau thuế nếu KHÔNG được bù giá. Năm y giữa năm => t = y - 2026.25."""
    pv = 0.0
    for y, f in Q['capex_schedule'].items():
        pv += capex * f / (1 + r) ** (int(y) + 0.5 - 2026.75)
    y0 = Q['opex_start_year']; dep = capex / Q['dep_years']
    last = opex_end if opex_end else y0 + 400
    for y in range(y0, last + 1):
        d = 1 / (1 + r) ** (y + 0.5 - 2026.75)
        pv += opex * (1 - t) * d
        if y < y0 + Q['dep_years']:
            pv -= dep * t * d
    return pv


def qcvn_exp(p0, wts=Q['passthrough_weights']):
    return p0 * (wts['P0'] + 0.5 * wts['P50'])


def center(r=r0, roe_shift=0.0, el=EL, en=EN, new=NEW, burden=None):
    b = qcvn_exp(qcvn_p0(r=r)) if burden is None else burden
    vals = {k: dps(legacy(v + roe_shift, r, el) + en + new + RETRO - b) for k, v in sc.items()}
    return sum(w[k] * vals[k] for k in w), vals


p0 = qcvn_p0(); be = qcvn_exp(p0)
print(f'RETRO_after_tax={RETRO:.1f} (1.0x)'); print(f'E_legacy={EL:.1f} BVPS_parent={dps(E):.0f}')
print(f'QCVN19 VA1: P0 PV burden={p0:.0f} ty ({dps(p0):.0f} d/cp); expected (0.40 P0 + 0.36 x 0.5)={be:.0f} ty ({dps(be):.0f} d/cp)')
c2, v2 = center(burden=0.0)
c3r, _ = center(el=EL + RETRO, burden=None); c3r -= RETRO / S * 1000
print(f'rev3 reproduce (retro in legacy): pre-liq {c3r:.0f} post {c3r*(1-L):.0f}')
c3, v3 = center()
print(f'khong QCVN (=P100), retro tach: pre-liq {c2:.0f} post {c2*(1-L):.0f}')
print(f'REV4 scen pre-liq {dict((k, round(v)) for k, v in v3.items())}')
print(f'REV4 center pre-liq={c3:.0f} post-liq={c3*(1-L):.0f} zone_post=[{v3["bad"]*(1-L):.0f};{v3["good"]*(1-L):.0f}] '
      f'P/B_center={c3*(1-L)/dps(E):.2f} 0.85xcenter={0.85*c3*(1-L):.0f} delta_vs_P100={c3/c2-1:+.1%}')
post = lambda c: c * (1 - L)
C = post(c3)
print('\n-- QCVN19 variants (post-liq center) --')
for lab, b in [('P0 100% (khong bu)', p0), ('P100 (bu du)', 0.0), ('P50', 0.5 * p0),
               ('P0 0.5/P50 0.3/P100 0.2', qcvn_exp(p0, {'P0': .5, 'P50': .3, 'P100': .2})),
               ('capex/opex x0.5 (VA1 da co mot phan)', qcvn_exp(qcvn_p0(capex=Q['capex_bn'] * .5, opex=Q['opex_bn_per_year'] * .5))),
               ('capex/opex x1.5', qcvn_exp(qcvn_p0(capex=Q['capex_bn'] * 1.5, opex=Q['opex_bn_per_year'] * 1.5))),
               ('opex dung 2045 (doi VA1 30 nam)', qcvn_exp(qcvn_p0(opex_end=2045))),
               ('thue 10.9%', qcvn_exp(qcvn_p0(t=0.109)))]:
    c, _ = center(burden=b); print(f'{lab}: burden {b:.0f} ty => {post(c):.0f} ({post(c)/C-1:+.1%})')
print('\n-- V1 r (neo lai huy dong, beta 1) + D4 dai Ke --')
for d in (-100, -50, 50, 100):
    for beta in (1.0, 0.5):
        rr = r0 + d / 1e4 * beta; c, _ = center(r=rr); print(f'dep {d:+d}bp beta{beta}: r={rr:.4f} => {post(c):.0f} ({post(c)/C-1:+.1%})')
for rr in (0.123, 0.134, 0.11):
    c, _ = center(r=rr); print(f'r={rr}: {post(c):.0f} ({post(c)/C-1:+.1%})')
print('\n-- NT3&4 (base NPV=0 so sach; chi do nhay) --')
for h in X['nt34_book_haircut_test']:
    c, _ = center(en=EN * (1 - h)); print(f'NT34 book -{h:.0%}: {post(c):.0f} ({post(c)/C-1:+.1%})')
print('\n-- Legacy finite life (von thu hoi tai dau tu NPV=0; chi do nhay) --')
def legacy_finite(roe, s, T, r=r0, el=EL):
    v = el; dep = el * s
    for t in range(1, T + 1):
        e_prev = el - dep * (t - 1) / T
        v += (roe - r) * e_prev / (1 + r) ** t
    rest = el * (1 - s)
    v += (roe - r) * rest / r / (1 + r) ** T
    return v
for s in X['legacy_finite_life']['depreciating_share_test']:
    for T in X['legacy_finite_life']['T_years_test']:
        vals = {k: dps(legacy_finite(v, s, T) + EN + NEW + RETRO - be) for k, v in sc.items()}
        c = sum(w[k] * vals[k] for k in w); print(f'share {s} T {T}: {post(c):.0f} ({post(c)/C-1:+.1%})')
print('\n-- Khac --')
for f in X['retro_uncollected_frac']:
    loss = RETRO * f; print(f'hoi to khong thu duoc {f:.0%}: -{dps(loss)*(1-L):.0f} d/cp ({-dps(loss)*(1-L)/C:+.1%})')
print(f'CPH: them 1 khoan nhu tien le 728,2: -{dps(X["cph_settlement_precedent_bn"])*(1-L):.0f} d/cp ({-dps(X["cph_settlement_precedent_bn"])*(1-L)/C:+.1%})')
for pct in X['welfare_pct_npat_test']:
    vals = {k: dps(legacy(v, el=EL) * (1 - pct) + EN + NEW + RETRO - be) for k, v in sc.items()}
    c = sum(w[k] * vals[k] for k in w); print(f'quy KTPL {pct:.0%} LNST di san: {post(c):.0f} ({post(c)/C-1:+.1%})')
for k in X['gas_qcvn_capex_bn_per_mw_test']:
    b = k * X['gas_plants_mw'] / (1 + r0) ** 3.75 * (Q['passthrough_weights']['P0'] + 0.5 * Q['passthrough_weights']['P50'])
    print(f'QCVN19 khi CM1&2+NT1 {k} ty/MW (minh hoa, kỳ vọng sau bu): -{dps(b)*(1-L):.0f} d/cp ({-dps(b)*(1-L)/C:+.1%})')
for d in (-0.02, 0.02):
    c, _ = center(roe_shift=d); print(f'ROE all {d:+.2f}: {post(c):.0f}')
print(f'VA1 CLTG con ~490 (ngoai base): +{dps(490*(1-0.109))*(1-L):.0f} d/cp')
