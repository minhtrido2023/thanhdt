"""Bắc cầu r3→r4, một-lần-một, độ nhạy (danh sách khoá assumptions_objective_r4.md §4)."""
import math, json
import model_r4 as M

R3 = json.load(open('model_out_r3.json'))['center']
def C(**kw): return M.run(**kw)['center']
out = {}

# ---- bước 0 + cầu cộng dồn
s0 = C(freight=M.FREIGHT_R3, PPd=M.PP_R3, inv=0.0)
s1 = C(PPd=M.PP_R3, inv=0.0)
s2 = C(inv=0.0)
s3 = C()
print(f"buoc 0 khung r4 + tham so r3 {s0:,.1f} vs r3 {R3:,.1f} lech {100*(s0/R3-1):+.5f}%")
br = [('r3', R3, None), ('(1) cước 3,85% → 4,686%', s1, s1 - s0), ('(2) nút P một quy tắc ε', s2, s2 - s1),
      ('(3) tồn kho dư 44,44 giải phóng theo nút O', s3, s3 - s2)]
for k, v, d in br: print(f"{k:50s} {v:>10,.0f} {'' if d is None else f'{d:+,.0f}'}")
print(f"tổng r3→r4 {s3 - R3:+,.0f} ({100*(s3/R3-1):+.2f}%)")
out['bridge'] = br; out['step0'] = s0
oat = {'gỡ cước (về 3,85%)': C(freight=M.FREIGHT_R3), 'gỡ P (về r3)': C(PPd=M.PP_R3), 'gỡ tồn kho': C(inv=0.0)}
for k, v in oat.items(): print(f"OAT {k:25s} {v:,.0f} (đóng góp {s3 - v:+,.0f})")
out['oat'] = oat

# ---- độ nhạy
R = M.run(); base = M.base_path(R); out['base'] = base
S = {}
S['grid'] = {r: {g: round(M.base_path(R, r=r, g=g, inv_pv=R['Einv'] * 1)) for g in (0, .01, .02, .03)} for r in (.125, .13, .135, .14, .145)}
for m in (.8, .9, 1.1, 1.2): S[f'EBIT_LR_x{m}'] = M.base_path(R, lr_mult=m)
for p in (0.90, 0.95, 1.05, 1.10): S[f'price_x{p}'] = M.value(R['En'], R['Ef'], R['EP'] * p, R['Esx'], R['elec'], R['freight'], inv_pv=R['Einv'])
for s in (0.135, 0.35, 0.75, 0.785, 1.0): S[f's_eff_{s}'] = M.value(R['En'], 1 - s * M.STEP, R['EP'], 0.35, R['elec'], R['freight'], inv_pv=R['Einv'])
S['DLC_below_netback_-5pct'] = M.base_path(R, transfer=0.05)
S['TX10_certain'] = M.value(R['En'], 1.0, R['EP'], 0.35, R['elec'], R['freight'], inv_pv=R['Einv'])
S['TX_0.90 (cay)'] = C(PX15=0.90)
S['freight_3.85 (cay)'] = C(freight=M.FREIGHT_R3); S['freight_4.03 (cay)'] = C(freight=0.040304)
S['P_mid_1.0_r3 (cay)'] = C(PPd=M.PP_R3)
S['P_rule_31500 (cay)'] = C(PPd={0.9366: 0.32, 0.9950: 0.58, 1.0618: 0.10})
S['P_lognorm_skeptic_0.990 (cay)'] = C(PPd={0.937: 0.32, 0.990: 0.58, 1.063: 0.10})
S['P_amp_10pct (cay)'] = C(PPd={0.90: 0.32, 0.9961: 0.58, 1.10: 0.10})
lq25 = -math.log(1 - 0.30 / 0.75) / 6.5; lq40 = -math.log(1 - 0.30 / 0.60) / 6.5
S['O_qB_0.25_refitF7 (cay)'] = C(q_perm=0.25, lam=lq25)
S['O_qB_0.40_refitF7 (cay)'] = C(q_perm=0.40, lam=lq40)
S['O_qB_0.25_lam_unchanged_r3style (cay)'] = C(q_perm=0.25)
S['O_r2_cut_2028 (cay)'] = C(cut_month=13.5)
S['O_cell_opt75 (cay)'] = C(cell='opt75'); S['O_cell_O2 (cay)'] = C(cell='O2')
S['D_A_0.7 (cay)'] = C(pD=0.7)
for pa in (0.30, 0.35, 0.70): S[f'P(A)={pa} (cay)'] = C(pA=pa)
S['A_late_tau25.5 (cay)'] = C(tau_a=25.5)
U27, R27, O3, O2, O1 = M.levels_for()
def fixed(l28, l27):
    n = {y: ((0.5 * U27 + 0.5 * l27) if y == 2027 else l28, 1.0, (0.5 * U27 + 0.5 * l27) if y == 2027 else l28) for y in range(2027, M.LAST + 1)}
    return M.value(n, R['Ef'], R['EP'], R['Esx'], R['elec'], R['freight'], inv_pv=R['Einv'])
S['O_fixed_unresolved_forever'] = fixed(O3, U27); S['O_fixed_O2_from_H2_27'] = fixed(O2, R27); S['O_fixed_O1_from_2028'] = fixed(O1, R27)
S['T_0.80/0.15/0.05 (cay)'] = C(PTd={'Ta': (1.0, 0.35, 0.80), 'Tb': (0.35, 0.35, 0.15), 'Tc': (0.135, 0.135, 0.05)})
S['T_0.55/0.35/0.10 (cay)'] = C(PTd={'Ta': (1.0, 0.35, 0.55), 'Tb': (0.35, 0.35, 0.35), 'Tc': (0.135, 0.135, 0.10)})
S['elec_cut_0.98 (cay)'] = C(cut=0.98)
S['elec_0.985_noF5'] = M.value(R['En'], R['Ef'], R['EP'], R['Esx'], 0.985, R['freight'], inv_pv=R['Einv'])
S['elec_phi_0.91 (cay)'] = C(phi=0.91); S['elec_phi_0.6 (cay)'] = C(phi=0.6)
S['coke_LR_2100 (cay)'] = C(coke_lr=2100.0); S['coke_LR_2108 (cay)'] = C(coke_lr=2108.0)
S['vol_state_onesided_0.927/1.0 (cay)'] = C(vol=(0.927, 1.0))
S['vol_state_twosided_0.927/1.037 (cay)'] = C(vol=(0.927, 1.037))
S['vol_H2_27_-15pct'] = M.base_path(R, vol27=0.85); S['vol_H2_27_-30pct'] = M.base_path(R, vol27=0.70)
S['no_inventory (cay)'] = C(inv=0.0)
S['oneoff_-50'] = M.base_path(R, oneoff=-50); S['pledge_loss_-42.6'] = M.base_path(R, oneoff=-42.6)
S['deposit70_at_face'] = M.base_path(R, oneoff=M.LOCKED70)
# xếp chồng bi quan có bằng chứng theo skeptic (để đo khoảng cách tới 57.500)
S['STACK_pess: qB0.25F7+P(A)0.35+T.80/.15/.05+vol onesided (cay)'] = C(q_perm=0.25, lam=lq25, pA=0.35,
    PTd={'Ta': (1.0, 0.35, 0.80), 'Tb': (0.35, 0.35, 0.15), 'Tc': (0.135, 0.135, 0.05)}, vol=(0.927, 1.0))
S['STACK_opt: cell opt75 + phi0.6 + vol twosided (cay)'] = C(cell='opt75', phi=0.6, vol=(0.927, 1.037))
for k, v in S.items():
    if k != 'grid': print(f"{k:62s} {v:>9,.0f}  ({v - s3:+,.0f} vs tâm)")
print('grid r x g:'); [print(r, S['grid'][r]) for r in S['grid']]
out['sens'] = S; out['center'] = s3
json.dump(out, open('bridge_sens_r4_out.json', 'w'), indent=1, default=float, ensure_ascii=False)
