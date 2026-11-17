"""Bắc cầu r2→r3, độ nhạy (danh sách khoá §4), kiểm khung (bước 0')."""
import math, json, io, contextlib
import model_r3 as M

R2_CENTER = json.load(open('model_out_r2_rerun.json'))['center']

def center(**kw):
    return M.run(**kw)['center']

def base_path(R, **kw):
    return M.value(R['En'], R['Ef'], R['EP'], R['Esx'], R['elec'], **kw)

out = {}
# ---- bước 0': khung r3 với tham số r2 (O tĩnh: A,B giải từ H2/2027 với P(B)=0,55, phần còn lại vĩnh viễn; TX .90; điện .98)
lam_r2 = -math.log(0.45) / 7.5
def r2_like(PX15, cut, static_r2=True):
    if static_r2:
        M.LAMBDA_SAVE = M.LAMBDA
        st = M.o_states(0.5, 7.5, lam_r2, 7.5, 0.0)
        # chạy thủ công với states r2-style
        R = _run_states(st, PX15, cut, tau_a=7.5)
        return R
def _run_states(states, PX15, cut, tau_a, PPd=None):
    PPd = PPd or M.PP
    elec = cut * M.F5; L = []
    for (w, D, a_yes, tb, u) in states:
        n = M.nvl_for(D, a_yes, tau_a, tb, u)
        for p, pp in PPd.items():
            for t, (s, sx, pt) in M.PT.items():
                for x, px in ((15, PX15), (10, 1 - PX15)):
                    if px <= 0: continue
                    f = 1 - s * M.STEP if x == 15 else 1.0
                    L.append((w * pp * pt * px, M.value(n, f, p, sx, elec)))
    return sum(a * b for a, b in L), L

c0, _ = r2_like(0.90, 0.98)
out['step0_r2_rerun'] = R2_CENTER
out["step0p_r3frame_r2params"] = c0
print(f"buoc 0  r2 chay lai {R2_CENTER:,.1f} | buoc 0' khung r3 + tham so r2 {c0:,.1f}  lech {100*(c0/R2_CENTER-1):+.4f}%")

# ---- bắc cầu cộng dồn
s1, _ = r2_like(0.97, 0.98)
s2, _ = r2_like(0.97, 0.985)
c3a = center(PX15=0.97, cut=0.985, cut_month=13.5)       # timing + λ chính xác + A nhị phân H2/27; B cắt 01/2028 rồi vĩnh viễn
c3b = center()                                           # r3 đầy đủ
steps = [('r2 (chạy lại)', R2_CENTER), ('(1) TX 0,90→0,97', s1), ('(2) điện cắt 0,98→0,985', s2),
         ('(3a) O thời gian: λ chính xác, H2/2027 theo xác suất tích luỹ, A nhị phân; B vẫn cắt 01/2028', c3a),
         ('(3b) B hazard tiếp sau 2028 (= r3)', c3b)]
prev = None; br = []
for k, v in steps:
    d = None if prev is None else v - prev
    br.append((k, v, d)); prev = v
    print(f"{k:95s} {v:>10,.0f} {'' if d is None else f'{d:+,.0f}'}")
out['bridge'] = br
# một-lần-một trên r3
oat = {
 'gỡ TX (về 0,90)': center(PX15=0.90),
 'gỡ điện (về 0,98)': center(cut=0.98),
 'gỡ O-nhất quán (B cắt 01/2028 vĩnh viễn)': center(cut_month=13.5),
}
for k, v in oat.items(): print(f"OAT {k:45s} {v:,.0f}  (đóng góp của thay đổi = {c3b - v:+,.0f})")
out['oat'] = oat

# ---- độ nhạy trên đường cơ sở r3 (inputs kỳ vọng) trừ khi ghi "cây"
R = M.run(); base = base_path(R); out['base'] = base
S = {}
S['grid'] = {r: {g: round(base_path(R, r=r, g=g)) for g in (0, .01, .02, .03)} for r in (.125, .13, .135, .14, .145)}
def lr_mult(m):
    # chỉ nhân EBIT 2028+ (giống r2)
    return base_path(R, lr_mult=m)
for m in (.8, .9, 1.1, 1.2): S[f'EBIT_LR_x{m}'] = lr_mult(m)
for s in (0.135, 0.35, 0.75, 0.785, 1.0): S[f's_eff_{s}'] = M.value(R['En'], 1 - s * M.STEP, R['EP'], 0.35, R['elec'])
S['TX10_certain'] = M.value(R['En'], 1.0, R['EP'], 0.35, R['elec'])
S['TX_back_0.90 (cay)'] = center(PX15=0.90)
for p in (0.90, 0.95, 1.05, 1.10): S[f'price_x{p}'] = M.value(R['En'], R['Ef'], R['EP'] * p, R['Esx'], R['elec'])
S['P_amp_10pct (cay)'] = center(PPd={0.90: 0.32, 1.0: 0.58, 1.10: 0.10})
S['P_mid_0.977 (cay)'] = center(PPd={0.937: 0.32, 0.977: 0.58, 1.063: 0.10})
S['O_B_cut_2028_permanent (cay)'] = c3a
S['O_qB_perm_0.25 (cay)'] = center(q_perm=0.25)
S['P(A)=0.3 (cay)'] = center(pA=0.3); S['P(A)=0.7 (cay)'] = center(pA=0.7)
S['A_late_tau25.5 (cay)'] = center(tau_a=25.5)
# trạng thái O cố định
def fixed(level28, level27):
    n = {y: (level27 if y == 2027 else level28) for y in range(2027, M.LAST + 1)}
    n[2027] = 0.5 * M.U27 + 0.5 * level27
    return M.value(n, R['Ef'], R['EP'], R['Esx'], R['elec'])
S['O_fixed_unresolved_forever'] = fixed(M.O3, M.U27)
S['O_fixed_O2_from_H2_27'] = fixed(M.O2, M.R27)
S['O_fixed_O1_from_2028'] = fixed(M.O1, M.R27)
S['elec_cut_0.98 (cay)'] = center(cut=0.98)
S['elec_0.985_noF5'] = M.value(R['En'], R['Ef'], R['EP'], R['Esx'], 0.985)
S['vol_H2_27_-15pct'] = base_path(R, vol27=0.85); S['vol_H2_27_-30pct'] = base_path(R, vol27=0.70)
S['DLC_below_netback_-5pct'] = base_path(R, transfer=0.05)
S['oneoff_-50'] = base_path(R, oneoff=-50); S['pledge_loss_-42.6'] = base_path(R, oneoff=-42.6)
S['deposit70_at_face'] = base_path(R, oneoff=M.LOCKED70)
for k, v in S.items():
    if k != 'grid': print(f"{k:38s} {v:,.0f}  ({v-base:+,.0f})")
print('grid r x g:'); [print(r, S['grid'][r]) for r in S['grid']]
out['sens'] = S
json.dump(out, open('bridge_sens_out.json', 'w'), indent=1, default=float, ensure_ascii=False)
